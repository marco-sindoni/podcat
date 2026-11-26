"""Choosing 3–5 candidates, and Marco's pick, unpick, reject and document link (FR-008, FR-010)."""

from __future__ import annotations

from datetime import date

from podcat.news.store import NewsStore

MIN_CANDIDATES = 3
MAX_CANDIDATES = 5
MAX_PER_CATEGORY = 2


class ShortlistError(ValueError):
    """A user error on a shortlist command (wrong number, missing list, script already written)."""


def select(stories: list[dict], limit: int = MAX_CANDIDATES) -> list[dict]:
    """Order by importance (then comic potential) and keep categories balanced."""
    ordered = sorted(stories, key=lambda s: (-s["importance"], -s["comic_potential"], s["id"]))
    chosen, per_category = [], {}
    for s in ordered:
        if per_category.get(s["category"], 0) >= MAX_PER_CATEGORY:
            continue
        chosen.append(s)
        per_category[s["category"]] = per_category.get(s["category"], 0) + 1
        if len(chosen) == limit:
            break
    if len(chosen) < limit:  # not enough variety: fill with the best remaining
        for s in ordered:
            if s not in chosen:
                chosen.append(s)
                if len(chosen) == limit:
                    break
    return sorted(chosen, key=lambda s: (-s["importance"], -s["comic_potential"], s["id"]))


def warning_for(count: int, thursday: bool = False) -> str | None:
    if thursday:
        if count == 0:
            return "nessuna buona notizia trovata negli ultimi 7 giorni."
        if count < MIN_CANDIDATES:
            return f"solo {count} buone notizie trovate negli ultimi 7 giorni."
        return None
    if count == 0:
        return "nessuna notizia verificata su due fonti indipendenti."
    if count < MIN_CANDIDATES:
        return f"solo {count} notizie verificate su due fonti indipendenti."
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
            store.set_story(old, status="candidate")
        store.set_story(new, status="chosen")
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


def _ensure_no_script(store: NewsStore, story_id: str) -> None:
    story = store.read_story(story_id)
    if story.get("status") == "used" or story.get("episode"):
        raise ShortlistError("Il copione di questa notizia esiste già: la scelta non si può più cambiare.")
