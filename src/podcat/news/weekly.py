"""Saturday shortlist for the Sunday episode, built from the week's daily runs (research R8, FR-015)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Callable

from pydantic import BaseModel

from podcat.llm.base import TextModel
from podcat.news.models import WeeklyResult
from podcat.news.pipeline import GatherResult
from podcat.news.shortlist import MAX_CANDIDATES, warning_for
from podcat.news.store import NewsStore
from podcat.settings import Settings, now_rome
from podcat.tracking.costs import Ledger, load_prices

MAX_TOKENS = 6_000

SYSTEM = """Sei caporedattore e autore di "Podcat – Chiacchiere tra quattro gatti". La domenica esce una puntata
di circa due minuti che riprende le notizie migliori della settimana. Ricevi le notizie verificate dei giorni
scorsi, con i voti già dati (comicità, satira, comprensibilità, importanza), il tono (comico o pungente) e
l'indicazione se sono già state usate in un reel.

Scegli da 3 a 5 notizie per la puntata. Preferisci le notizie con comicità e comprensibilità alte; includi
una notizia dal tono pungente (satira, osservazione pungente, riflessione) se la settimana ne ha una.
Puoi riprendere notizie già usate in un reel se meritano un approfondimento, ma cerca un buon equilibrio
tra notizie nuove e riprese e tra categorie diverse. Per ognuna dai weekly_importance da 1 a 5 (quanto vale
per la puntata, in quest'ordine di preferenza) e un motivo breve in italiano. Usa solo gli story_id ricevuti."""


def _score(value) -> str:
    return "n/d" if value is None else str(value)  # stories created before spec 001 A1


def week_start(day: date) -> date:
    """The Sunday that opens the week ending on `day` (Sunday to Saturday)."""
    return day - timedelta(days=(day.weekday() + 1) % 7)


def render(stories: list[dict]) -> str:
    lines = []
    for s in stories:
        used = "già usata in un reel" if s.get("status") == "used" else "nuova"
        lines.append(
            f"- {s['id']} | {s['category']} | tono {s.get('tone') or 'comico'} | importanza {s['importance']} | "
            f"comicità {s['comic_potential']} | satira {_score(s.get('satirical_potential'))} | "
            f"comprensibilità {_score(s.get('clarity'))} | {used}\n  {s['title']}: {s['summary']}"
        )
    return "\n".join(lines)


def weekly(
    settings: Settings,
    day: date,
    model_factory: Callable[[Ledger, date], TextModel],
    refresh: bool = False,
) -> GatherResult:
    store = NewsStore(settings.tracking_dir, settings.cache_dir)
    kind = "weekly"
    existing = store.read_shortlist(day, kind)
    if existing and not refresh:
        return GatherResult(str(store.shortlist_path(day, kind)), existing, created=False)
    if refresh:
        store.cache_clear(day, kind)

    start = week_start(day)
    days = [start + timedelta(days=n) for n in range((day - start).days + 1)]
    gaps = [d.isoformat() for d in days if store.read_shortlist(d, "daily") is None]
    stories = [s for s in store.stories_between(start, day) if s.get("status") in ("candidate", "chosen", "used")]
    by_id = {s["id"]: s for s in stories}

    cost = 0.0
    picks: list[str] = []
    if stories:
        cached = store.cache_read(day, kind, "weekly-rank")
        if cached is None:
            ledger = Ledger(settings.tracking_dir, load_prices(settings.config_dir))
            model = model_factory(ledger, day)
            if hasattr(model, "for_step"):
                model = model.for_step("weekly-rank")
            result, usage = model.parse(SYSTEM, "Notizie della settimana:\n" + render(stories), WeeklyResult, MAX_TOKENS)
            cost = round(ledger.price(model.name).cost(usage.input_tokens, usage.output_tokens), 6)
            cached = result.model_dump(mode="json")
            store.cache_write(day, kind, "weekly-rank", cached)
        result = WeeklyResult.model_validate(cached)
        ordered = sorted(
            (p for p in result.picks if p.story_id in by_id), key=lambda p: -p.weekly_importance
        )
        picks = list(dict.fromkeys(p.story_id for p in ordered))[:MAX_CANDIDATES]

    run_log = store.write_run_log(
        day,
        kind,
        {
            "date": day.isoformat(),
            "kind": kind,
            "started_at": now_rome().isoformat(timespec="seconds"),
            "week_start": start.isoformat(),
            "stories_in_week": len(stories),
            "gaps": gaps,
            "cost_usd": cost,
        },
        [],
    )
    meta = {
        "date": day.isoformat(),
        "kind": kind,
        "good_news_thursday": False,
        "status": "proposed",
        "candidates": picks,
        "backups": [],
        "picked": None,
        "warning": warning_for(len(picks)),
        "gaps": gaps,
        "doc_url": None,
        "run_log": str(run_log.relative_to(settings.repo_root)),
        "cost_usd": cost,
    }
    path = store.write_shortlist(meta)
    return GatherResult(str(path), meta, created=True)
