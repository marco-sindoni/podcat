"""New versions from Marco's comments, ending swaps and manual edits (FR-011, FR-013, FR-017; research R5, R6)."""

from __future__ import annotations

import hashlib
from datetime import date

import yaml

from podcat.llm.base import TextModel
from podcat.scripts.bible import Bible
from podcat.scripts.models import Answer, Ending, HeadWriterResult, Line, RevisionResult, Version
from podcat.scripts.prompts import Brief, dump, revision_user, system_prompt
from podcat.scripts.store import ScriptError

MAX_TOKENS = {"daily": 16_000, "weekly": 20_000}


def comments_digest(comments: list[dict], version: int) -> str:
    raw = yaml.safe_dump({"v": version, "c": comments}, allow_unicode=True, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_comments(text: str) -> list[dict]:
    data = yaml.safe_load(text) or []
    if not isinstance(data, list) or not all(isinstance(c, dict) and str(c.get("text", "")).strip() for c in data):
        raise ScriptError("Il file dei commenti deve essere una lista di voci con almeno «text».")
    return [{k: c[k] for k in ("line", "quote", "text") if k in c} for c in data]


def ask_revision(model: TextModel, bible: Bible, brief: Brief, current: Version, comments: list[dict]) -> RevisionResult:
    current_yaml = dump({"lines": [l.model_dump() for l in current.lines],
                         "scenes": [s.model_dump(exclude={"duration_s"}) for s in current.scenes],
                         "news_image": current.news_image.model_dump(),
                         "endings": [e.model_dump() for e in current.endings]})
    result, _ = model.parse(system_prompt(bible, "revision"),
                            revision_user(bible, brief, current_yaml, dump(comments)), RevisionResult,
                            MAX_TOKENS[brief.kind])
    return result


def apply_revision(current: Version, rev: RevisionResult) -> tuple[HeadWriterResult, list[str]]:
    """Apply only the listed changes; manual lines are never touched. Returns the result and warnings."""
    lines = [l.model_copy() for l in current.lines]
    warnings = []
    inserts: dict[int, list[Line]] = {}
    for ch in rev.changes:
        if ch.insert_after:
            inserts.setdefault(ch.n, []).append(Line(n=0, cat=ch.cat, text=ch.text))
            continue
        idx = next((i for i, l in enumerate(lines) if l.n == ch.n), None)
        if idx is None:
            warnings.append(f"La battuta {ch.n} non esiste: modifica ignorata.")
        elif lines[idx].manual:
            warnings.append(f"La battuta {ch.n} è tua: non l'ho toccata.")
        else:
            lines[idx] = Line(n=ch.n, cat=ch.cat, text=ch.text)
    scenes = rev.scenes or current.scenes
    if inserts:
        lines, scenes = _with_inserts(lines, scenes, inserts)
    result = HeadWriterResult(
        chosen_angle=current.chosen_angle or "",
        lines=lines,
        scenes=[s.model_copy(update={"duration_s": None}) for s in scenes],
        news_image=rev.news_image or current.news_image,
        endings=rev.endings or current.endings,
        notes=rev.notes,
    )
    return result, warnings


def _with_inserts(lines, scenes, inserts):
    """Renumber lines after insertions and move scene references accordingly."""
    new_lines, mapping = [], {}
    for l in lines:
        mapping[l.n] = len(new_lines) + 1
        new_lines.append(l.model_copy(update={"n": len(new_lines) + 1}))
        for extra in inserts.get(l.n, []):
            new_lines.append(extra.model_copy(update={"n": len(new_lines) + 1}))
    new_scenes = []
    for s in scenes:
        refs = []
        for n in s.lines:
            refs.append(mapping.get(n, n))
            first = mapping.get(n, n)
            refs += [first + k + 1 for k in range(len(inserts.get(n, [])))]
        new_scenes.append(s.model_copy(update={"lines": refs}))
    return new_lines, new_scenes


def swap_ending(current: Version, number: int) -> HeadWriterResult:
    if not 1 <= number <= len(current.endings):
        raise ScriptError(f"Finale non valido: scegli tra 1 e {len(current.endings)}.")
    lines = [l.model_copy() for l in current.lines]
    if len(lines) < 2 or lines[-1].cat != "flanella" or lines[-2].cat != "feedback":
        raise ScriptError("Il copione non chiude con Feedback e Flanella: non posso cambiare il finale.")
    chosen = current.endings[number - 1]
    old = Ending(feedback=lines[-2].text, flanella=lines[-1].text)
    lines[-2] = lines[-2].model_copy(update={"text": chosen.feedback, "manual": False})
    lines[-1] = lines[-1].model_copy(update={"text": chosen.flanella, "manual": False})
    endings = list(current.endings)
    endings[number - 1] = old  # the replaced ending stays available
    return HeadWriterResult(chosen_angle=current.chosen_angle or "", lines=lines,
                            scenes=[s.model_copy() for s in current.scenes], news_image=current.news_image,
                            endings=endings, notes=[f"Messo il finale {number}; il finale precedente è ora il finale {number}."])


def edit_line(current: Version, n: int, text: str) -> HeadWriterResult:
    lines = [l.model_copy() for l in current.lines]
    idx = next((i for i, l in enumerate(lines) if l.n == n), None)
    if idx is None:
        raise ScriptError(f"La battuta {n} non esiste.")
    if not text.strip():
        raise ScriptError("Il testo della battuta è vuoto.")
    lines[idx] = lines[idx].model_copy(update={"text": text.strip(), "manual": True})
    return HeadWriterResult(chosen_angle=current.chosen_angle or "", lines=lines,
                            scenes=[s.model_copy() for s in current.scenes], news_image=current.news_image,
                            endings=current.endings, notes=[f"Battuta {n} corretta a mano da Marco."])


def answers_for(rev: RevisionResult, warnings: list[str]) -> list[Answer]:
    return list(rev.answers) + [Answer(comment="(controllo)", answer=w) for w in warnings]
