"""Choosing 3–5 candidates, and Marco's pick, unpick, reject and document link (FR-008, FR-010)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from podcat.news.store import NewsStore

MIN_CANDIDATES = 3
MAX_CANDIDATES = 5
MAX_PER_CATEGORY = 2


class ShortlistError(ValueError):
    """A user error on a shortlist command (wrong number, missing list, script already written)."""


# Floors (spec 001 A1, FR-020 and FR-024).
COMIC_FLOOR = 3
CLARITY_FLOOR = 3
IMPORTANCE_FLOOR = 2
PUNGENTE_FLOOR = 3  # satirical potential, clarity and importance of the pungente candidate
MAX_POLITICS = 1  # per tone: one comic and one pungente political story at most (Marco, 2026-11-27)


@dataclass
class Selection:
    chosen: list[dict]  # in shortlist order; each dict gets a "tone" key
    discarded: list[dict] = field(default_factory=list)  # {"title", "reason"}
    no_pungente: bool = False  # weekday without a qualifying pungente story


def _clarity(story: dict) -> int:
    return story.get("clarity") or 3  # stories created before A1 have no clarity


def _satire(story: dict) -> int:
    return story.get("satirical_potential") or 1


def rank_key(story: dict, thursday: bool = False) -> tuple:
    """Comic candidates: comic potential plus clarity, then comic potential, then importance
    (research R12). Thursday uses the same order (R18)."""
    comic, clarity = story["comic_potential"], _clarity(story)
    return (-(comic + clarity), -comic, -story["importance"], story["id"])


def pungente_key(story: dict) -> tuple:
    """The pungente candidate: satirical potential plus clarity, then importance (R19)."""
    satire, clarity = _satire(story), _clarity(story)
    return (-(satire + clarity), -story["importance"], -satire, story["id"])


def _floor_reason(story: dict) -> str | None:
    if story["importance"] < IMPORTANCE_FLOOR:
        return "poco rilevante"
    if _clarity(story) < CLARITY_FLOOR:
        return "poco comprensibile"
    if story["comic_potential"] < COMIC_FLOOR:
        return "comicità sotto 3"
    return None


def _pungente_ok(story: dict) -> bool:
    # A story funnier than it is sharp stays comic (R19).
    return (
        _satire(story) >= PUNGENTE_FLOOR
        and _clarity(story) >= PUNGENTE_FLOOR
        and story["importance"] >= PUNGENTE_FLOOR
        and _satire(story) >= story["comic_potential"]
    )


def _politics(story: dict) -> bool:
    return "politics" in story.get("flags", [])


def choose(stories: list[dict], limit: int = MAX_CANDIDATES, thursday: bool = False) -> Selection:
    """Fill one pungente slot (not on Thursday), then the comic slots (FR-008, FR-020–FR-024)."""
    discarded: list[dict] = []
    pool = []
    for s in stories:
        if s.get("sensitive"):
            discarded.append({"title": s["title"], "reason": "tema delicato"})
        else:
            pool.append(s)

    pungente = None
    if not thursday:
        eligible = sorted((s for s in pool if _pungente_ok(s)), key=pungente_key)
        pungente = eligible[0] if eligible else None

    per_category: dict[str, int] = {}
    politics = 0
    comic: list[dict] = []
    if pungente:
        per_category[pungente["category"]] = 1
    slots = limit - (1 if pungente else 0)

    eligible = []
    for s in pool:
        if s is pungente:
            continue
        reason = _floor_reason(s)
        if reason:
            discarded.append({"title": s["title"], "reason": reason})
        else:
            eligible.append(s)
    eligible.sort(key=lambda s: rank_key(s, thursday))

    def take(respect_categories: bool) -> None:
        nonlocal politics
        for s in eligible:
            if len(comic) == slots:
                return
            if s in comic:
                continue
            if _politics(s) and politics >= MAX_POLITICS:
                continue
            if respect_categories and per_category.get(s["category"], 0) >= MAX_PER_CATEGORY:
                continue
            comic.append(s)
            politics += int(_politics(s))
            per_category[s["category"]] = per_category.get(s["category"], 0) + 1

    take(respect_categories=True)
    take(respect_categories=False)  # not enough variety: allow a third story of a category
    for s in eligible:
        if s not in comic and _politics(s) and politics >= MAX_POLITICS:
            discarded.append({"title": s["title"], "reason": "già una notizia politica"})

    chosen = [dict(s, tone="comico") for s in sorted(comic, key=lambda s: rank_key(s, thursday))]
    if pungente:
        chosen.append(dict(pungente, tone="pungente"))
    return Selection(chosen=chosen, discarded=discarded, no_pungente=not thursday and pungente is None)


def select(stories: list[dict], limit: int = MAX_CANDIDATES, thursday: bool = False) -> list[dict]:
    return choose(stories, limit, thursday).chosen


def warning_for(count: int, thursday: bool = False) -> str | None:
    if thursday:
        if count == 0:
            return "nessuna buona notizia adatta negli ultimi 7 giorni."
        if count < MIN_CANDIDATES:
            return f"solo {count} buone notizie adatte negli ultimi 7 giorni."
        return None
    if count == 0:
        return "nessuna notizia verificata e adatta al reel."
    if count < MIN_CANDIDATES:
        return f"solo {count} notizie verificate e adatte al reel."
    return None


def _require(store: NewsStore, day: date, kind: str) -> dict:
    meta = store.read_shortlist(day, kind)
    if meta is None:
        raise ShortlistError(f"Nessuna lista {kind} per il {day.isoformat()}.")
    return meta


def pick(store: NewsStore, day: date, kind: str, number: int) -> str:
    meta = _require(store, day, kind)
    candidates = meta.get("candidates", [])
    if not 1 <= number <= len(candidates):
        raise ShortlistError(f"Numero non valido: scegli tra 1 e {len(candidates)}.")
    new = candidates[number - 1]
    old = meta.get("picked")
    if kind == "daily":  # the weekly list reuses stories: their daily status stays as it is
        if old and old != new:
            _ensure_no_script(store, old)
            _discard_open_script(store, old, kind)
            store.set_story(old, status="candidate")
        store.set_story(new, status="chosen")
    elif old and old != new:
        _discard_open_script(store, old, kind)
    meta.update(picked=new, status="picked")
    store.write_shortlist(meta)
    return new


def unpick(store: NewsStore, day: date, kind: str) -> None:
    meta = _require(store, day, kind)
    old = meta.get("picked")
    if not old:
        raise ShortlistError("Nessuna notizia scelta da annullare.")
    if kind == "daily":
        _ensure_no_script(store, old)
        store.set_story(old, status="candidate")
    meta.update(picked=None, status="proposed")
    store.write_shortlist(meta)


def reject(store: NewsStore, day: date, kind: str) -> list[str]:
    meta = _require(store, day, kind)
    if kind == "weekly":
        meta.update(picked=None, status="rejected")
        store.write_shortlist(meta)
        return meta.get("candidates", [])
    for sid in meta.get("candidates", []):
        story = store.read_story(sid)
        if story.get("status") in ("used",) or story.get("episode"):
            raise ShortlistError(f"La notizia {sid} è già usata in una puntata: non si può scartare.")
    for sid in meta.get("candidates", []):
        store.set_story(sid, status="rejected")
    meta.update(picked=None, status="rejected")
    store.write_shortlist(meta)
    return meta.get("candidates", [])


def link_doc(store: NewsStore, day: date, kind: str, url: str) -> None:
    if not url.startswith("https://"):
        raise ShortlistError("Il link del documento deve iniziare con https://")
    meta = _require(store, day, kind)
    meta["doc_url"] = url
    store.write_shortlist(meta)


def _discard_open_script(store: NewsStore, story_id: str, kind: str) -> None:
    """A script still in draft or review for the old pick is discarded (spec 002, US2 scenario 4)."""
    from podcat.scripts.store import ScriptStore

    scripts = ScriptStore(store.root.parent)
    meta = scripts.find(story_id, kind)
    if meta is None:
        return
    if meta["status"] == "approved":
        raise ShortlistError("Il copione di questa notizia è approvato: la scelta non si può più cambiare.")
    scripts.set(meta["id"], status="discarded")
    store.set_story(story_id, script=None)


def _ensure_no_script(store: NewsStore, story_id: str) -> None:
    story = store.read_story(story_id)
    if story.get("status") == "used" or story.get("episode"):
        raise ShortlistError("Il copione di questa notizia esiste già: la scelta non si può più cambiare.")
