"""The daily run: fetch → prefilter → triage → verify → editorial → shortlist (FR-001…FR-014)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Callable

import httpx

from podcat.llm.base import TextModel, Usage
from podcat.news import editorial as editorial_step
from podcat.news import triage as triage_step
from podcat.news.fetch import FetchReport, fetch_all, in_window, load_agencies
from podcat.news.models import EditorialResult, FeedItem, TriageResult
from podcat.news.prefilter import normalize_url, prefilter
from podcat.news.shortlist import ShortlistError, select, warning_for
from podcat.news.sources import load_sources
from podcat.news.store import NewsStore
from podcat.news.verify import effective_group, verify_all
from podcat.settings import ROME, Settings, now_rome
from podcat.tracking.costs import Ledger, load_prices

THURSDAY = 3
THURSDAY_WINDOW_HOURS = 7 * 24  # "Giovedì buone notizie" looks at the whole week (FR-009)


@dataclass
class GatherResult:
    path: str
    meta: dict
    created: bool


def window_end(day: date, now: datetime) -> datetime:
    if now.astimezone(ROME).date() == day:
        return now
    return datetime.combine(day, time(23, 59), tzinfo=ROME)


def gather(
    settings: Settings,
    day: date,
    model_factory: Callable[[Ledger, date], TextModel],
    refresh: bool = False,
    now: datetime | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> GatherResult:
    store = NewsStore(settings.tracking_dir, settings.cache_dir)
    kind = "daily"
    existing = store.read_shortlist(day, kind)
    if existing and not refresh:
        return GatherResult(str(store.shortlist_path(day, kind)), existing, created=False)
    if existing and refresh:
        if existing.get("picked"):
            raise ShortlistError("C'è già una notizia scelta: annulla la scelta prima di rifare la lista.")
        for sid in existing.get("candidates", []):
            if store.read_story(sid).get("status") == "candidate":
                store.story_path(sid).unlink()
        store.cache_clear(day, kind)

    now = now or now_rome()
    started = now_rome()
    thursday = day.weekday() == THURSDAY
    ledger = Ledger(settings.tracking_dir, load_prices(settings.config_dir))
    model = model_factory(ledger, day)
    sources = {s.id: s for s in load_sources(settings.config_dir)}
    usages: list[Usage] = []

    # 1. fetch (cached)
    cached = store.cache_read(day, kind, "fetch")
    if cached is None:
        report = asyncio.run(fetch_all(list(sources.values()), load_agencies(settings.config_dir), http_client))
        cached = {
            "items": [i.model_dump(mode="json") for i in report.items],
            "feeds_ok": report.feeds_ok,
            "feeds_failed": report.feeds_failed,
        }
        store.cache_write(day, kind, "fetch", cached)
    report = FetchReport(
        items=[FeedItem.model_validate(i) for i in cached["items"]],
        feeds_ok=cached["feeds_ok"],
        feeds_failed=cached["feeds_failed"],
    )

    # 2. window and free filters
    hours = THURSDAY_WINDOW_HOURS if thursday else 24
    items = [i for i in in_window(report.items, window_end(day, now), hours) if i.source_id in sources]
    rejected = {normalize_url(u) for u in store.rejected_urls(day)}
    items = [i for i in items if normalize_url(i.url) not in rejected]
    items, discarded = prefilter(items)
    by_id = {i.item_id: i for i in items}

    # 3. triage (cached)
    triage_cached = store.cache_read(day, kind, "triage")
    if triage_cached is None:
        triage, usage = triage_step.triage(model, items, sources, thursday)
        usages.append(usage)
        store.cache_write(day, kind, "triage", triage.model_dump(mode="json"))
    else:
        triage = TriageResult.model_validate(triage_cached)

    # 4. verify (free, deterministic)
    verdicts = verify_all(triage.groups, by_id, sources, thursday=thursday)
    for v in verdicts:
        if not v.verified:
            discarded.append({"title": v.items[0].title if v.items else "?", "reason": v.reason or ""})
    verified = editorial_step.rank_for_editorial([v for v in verdicts if v.verified])

    # 5. editorial (cached)
    editorial_cached = store.cache_read(day, kind, "editorial")
    if editorial_cached is None:
        edit, usage = editorial_step.editorial(model, verified, sources, store.recent_covered(day), thursday)
        usages.append(usage)
        store.cache_write(day, kind, "editorial", edit.model_dump(mode="json"))
    else:
        edit = EditorialResult.model_validate(editorial_cached)

    # 6. stories and shortlist
    proposals = []
    for s in edit.stories:
        v = verified[s.group_index]
        if s.already_covered and not s.follow_up_of:
            discarded.append({"title": s.title, "reason": "notizia già trattata"})
            continue
        proposals.append((s, v))
    drafts = [
        {
            "title": s.title,
            "category": v.group.category,
            "importance": s.importance,
            "comic_potential": s.comic_potential,
            "id": f"{i:03d}",
            "_pair": (s, v),
        }
        for i, (s, v) in enumerate(proposals)
    ]
    chosen = select(drafts)
    candidate_ids = []
    first_seen = now.astimezone(ROME).isoformat(timespec="minutes")
    for d in chosen:
        s, v = d["_pair"]
        sid = store.new_story_id(day, s.title)
        store.write_story(
            {
                "id": sid,
                "title": s.title,
                "summary": s.summary,
                "category": v.group.category,
                "sources": [
                    {
                        "source_id": item.source_id,
                        "outlet": sources[item.source_id].name,
                        "group": effective_group(item, sources[item.source_id]),
                        "url": item.url,
                        "published_at": item.published_at.isoformat() if item.published_at else None,
                    }
                    for item in v.items
                ],
                "effective_groups": len(v.effective_groups),
                "first_seen": first_seen,
                "importance": s.importance,
                "importance_reason": s.importance_reason,
                "comic_potential": s.comic_potential,
                "comic_reason": s.comic_reason,
                "positive": v.group.positive,
                "flags": list(s.flags),
                "follow_up_of": s.follow_up_of,
                "status": "candidate",
                "episode": None,
            }
        )
        candidate_ids.append(sid)

    backups = []
    if thursday and len(candidate_ids) < 3:
        week = store.stories_between(day - timedelta(days=7), day - timedelta(days=1))
        backups = [s["id"] for s in week if s.get("positive") and s.get("status") == "candidate"][:3]

    prices = ledger.price(model.name) if usages else None
    cost = round(sum(prices.cost(u.input_tokens, u.output_tokens) for u in usages), 6) if prices else 0.0
    run_meta = {
        "date": day.isoformat(),
        "kind": kind,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": now_rome().isoformat(timespec="seconds"),
        "feeds_ok": len(report.feeds_ok),
        "feeds_failed": report.feeds_failed,
        "items_in_window": len(by_id),
        "groups_found": len(triage.groups),
        "verified": len(verified),
        "cost_usd": cost,
    }
    run_log = store.write_run_log(day, kind, run_meta, discarded)
    warning = warning_for(len(candidate_ids), thursday)
    if report.feeds_ok == [] and report.feeds_failed:
        warning = "nessun feed raggiungibile: controlla la rete."
    meta = {
        "date": day.isoformat(),
        "kind": kind,
        "good_news_thursday": thursday,
        "status": "proposed",
        "candidates": candidate_ids,
        "backups": backups,
        "picked": None,
        "warning": warning,
        "doc_url": None,
        "run_log": str(run_log.relative_to(settings.repo_root)),
        "cost_usd": cost,
    }
    path = store.write_shortlist(meta)
    return GatherResult(str(path), meta, created=True)
