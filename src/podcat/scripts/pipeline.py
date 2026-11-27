"""Write orchestration: picked story → writers' room → head writer → checks → one fix → save (spec 002)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

from podcat.news.store import NewsStore
from podcat.scripts import checks, headwriter, room, rotation
from podcat.scripts.bible import Bible, load_bible
from podcat.scripts.models import HeadWriterResult, Version
from podcat.scripts.prompts import Brief
from podcat.scripts.render import render_index, render_version
from podcat.scripts.store import ScriptError, ScriptStore, now_iso
from podcat.scripts.timing import apply_timing, spoken_words
from podcat.settings import Settings
from podcat.tracking.costs import Ledger, load_prices

# factory(ledger, day, step) -> TextModel; step is room | head-writer | fix | revision
ModelFactory = Callable[[Ledger, date, str], object]


@dataclass
class WriteResult:
    script_id: str
    path: Path
    created: bool
    problems: list[str] = field(default_factory=list)
    cost_usd: float = 0.0


@dataclass
class Context:
    settings: Settings
    bible: Bible
    news: NewsStore
    scripts: ScriptStore
    ledger: Ledger


def context(settings: Settings) -> Context:
    return Context(
        settings=settings,
        bible=load_bible(settings.repo_root),
        news=NewsStore(settings.tracking_dir, settings.cache_dir),
        scripts=ScriptStore(settings.tracking_dir),
        ledger=Ledger(settings.tracking_dir, load_prices(settings.config_dir)),
    )


def picked_story(ctx: Context, day: date, kind: str) -> tuple[dict, dict]:
    shortlist = ctx.news.read_shortlist(day, kind)
    if shortlist is None:
        raise ScriptError(f"Nessuna lista {kind} per il {day.isoformat()}.")
    if not shortlist.get("picked"):
        raise ScriptError("Nella lista non è ancora stata scelta una notizia.")
    return shortlist, ctx.news.read_story(shortlist["picked"])


def recent_lines(ctx: Context, exclude: str | None, current: dict) -> tuple[list[dict], list[str]]:
    """First/last lines and whole texts of the last scripts (research R8)."""
    window = int(ctx.bible.config.get("repeat_window", 7))
    briefs, texts = [], []
    for meta in ctx.scripts.recent(before=current, limit=window, exclude=exclude):
        v = ctx.scripts.read_version(meta["id"])
        briefs.append({"first": v.lines[0].text, "last": v.lines[-1].text})
        texts.append(" ".join(l.text for l in v.lines))
    return briefs, texts


def check_context(ctx: Context, kind: str, thursday: bool, story: dict, allowed: list[str],
                  recent: list[dict], texts: list[str]) -> checks.CheckContext:
    return checks.CheckContext(
        kind=kind,
        thursday=thursday,
        category=story.get("category", ""),
        allowed_modes=allowed,
        shots=set(ctx.bible.shots),
        config=ctx.bible.config,
        recent_first_lines=[r["first"] for r in recent],
        recent_last_lines=[r["last"] for r in recent],
        recent_texts=texts,
    )


def build_version(number: int, result: HeadWriterResult, ctx: Context, thursday: bool, **extra) -> Version:
    cfg = ctx.bible.config
    formula = cfg["thursday_formula"] if thursday else None
    scenes, total = apply_timing(result.lines, result.scenes, cfg, skip_text=formula)
    return Version(
        version=number,
        lines=result.lines,
        scenes=scenes,
        news_image=result.news_image,
        endings=result.endings,
        words=spoken_words(result.lines, skip_text=formula),
        duration_s=total,
        head_writer_notes=result.notes,
        chosen_angle=result.chosen_angle,
        **extra,
    )


def run_checks(v: Version, cctx: checks.CheckContext) -> list[str]:
    return checks.check(v.lines, v.scenes, v.news_image, v.endings, v.duration_s, cctx)


def reel_lines_for(ctx: Context, story_id: str) -> list[str]:
    meta = ctx.scripts.find(story_id, "daily")
    if not meta:
        return []
    return [l.text for l in ctx.scripts.read_version(meta["id"]).lines]


def write(settings: Settings, day: date, kind: str, factory: ModelFactory, new_draft: bool = False) -> WriteResult:
    ctx = context(settings)
    shortlist, story = picked_story(ctx, day, kind)
    existing = ctx.scripts.find(story["id"], kind)
    if existing and not new_draft:
        return WriteResult(existing["id"], ctx.scripts.index_path(existing["id"]), False, existing.get("problems") or [])
    if existing and existing["status"] == "approved":
        raise ScriptError("Il copione è approvato: riaprilo prima di riscriverlo.")
    if kind == "daily" and not existing and story.get("status") != "chosen":
        raise ScriptError(f"La notizia {story['id']} non è nello stato «chosen».")

    thursday = bool(shortlist.get("good_news_thursday")) and kind == "daily"
    tone = (existing or {}).get("tone") or story.get("tone") or "comico"
    current = {"date": day.isoformat(), "versions": [{"created_at": now_iso()}]}
    exclude = existing["id"] if existing else None
    previous = rotation.previous_script(ctx.scripts, current, exclude=exclude)
    allowed = rotation.allowed_modes(previous)
    recent, texts = recent_lines(ctx, exclude, current)
    brief = Brief(kind=kind, story=story, thursday=thursday, tone=tone, allowed_modes=allowed, recent=recent,
                  reel_lines=reel_lines_for(ctx, story["id"]) if kind == "weekly" else [])
    cctx = check_context(ctx, kind, thursday, story, allowed, recent, texts)

    spent_before = ctx.ledger.total(day)
    drafts = room.write_drafts(factory(ctx.ledger, day, "room"), ctx.bible, brief)
    head = factory(ctx.ledger, day, "head-writer")
    result = headwriter.rewrite(head, ctx.bible, brief, drafts)
    number = int(existing["current_version"]) + 1 if existing else 1
    version = build_version(number, result, ctx, thursday)
    problems = run_checks(version, cctx)
    if problems:
        result = headwriter.fix(factory(ctx.ledger, day, "fix"), ctx.bible, brief, result, problems)
        version = build_version(number, result, ctx, thursday)
        problems = run_checks(version, cctx)
    cost = round(ctx.ledger.total(day) - spent_before, 6)

    meta = existing or {
        "id": ctx.scripts.new_id(day, kind, story["id"]),
        "story_id": story["id"],
        "kind": kind,
        "date": day.isoformat(),
        "good_news_thursday": thursday,
        "doc_url": None,
        "approved_at": None,
        "approved_version": None,
        "versions": [],
    }
    meta.update(
        tone=tone,
        status=meta.get("status") if existing and meta.get("status") == "review" and not problems else "draft",
        problems=problems,
        news_image_mode=version.news_image.mode,
        previous_script=previous["id"] if previous else None,
    )
    body = render_version(meta, story, version, ctx.bible.shots)
    meta = ctx.scripts.add_version(meta, version, body, "new-draft" if existing else "write", cost, "")
    ctx.scripts.set(meta["id"], summary=render_index(meta, story))
    ctx.news.set_story(story["id"], script=meta["id"])
    return WriteResult(meta["id"], ctx.scripts.index_path(meta["id"]), True, problems, cost)


def show(settings: Settings, day: date, kind: str, version: int | None = None) -> str:
    ctx = context(settings)
    _, story = picked_story(ctx, day, kind)
    meta = ctx.scripts.find(story["id"], kind)
    if not meta:
        raise ScriptError("Per questa notizia non c'è ancora un copione.")
    v = ctx.scripts.read_version(meta["id"], version)
    return render_version(meta, story, v, ctx.bible.shots)


def listing(settings: Settings, last: int = 10) -> list[dict]:
    store = ScriptStore(settings.tracking_dir)
    items = sorted(store.all(), key=lambda m: (str(m.get("date")), m.get("id")), reverse=True)
    return items[:last]
