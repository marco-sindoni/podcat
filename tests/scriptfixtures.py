"""Shared helpers for script tests: a repo with the bible, picked stories and recorded model outputs."""

from __future__ import annotations

import copy
import shutil
from datetime import date
from pathlib import Path

from fakes import FakeModel
from podcat.news.store import NewsStore
from podcat.settings import Settings, load_settings

REPO = Path(__file__).resolve().parents[1]
FRIDAY = date(2026, 11, 27)
THURSDAY = date(2026, 11, 26)

FRIDGE = {
    "id": "2026-11-27-hacker-fanno-impazzire-i-frigoriferi-in-slovenia",
    "title": "Hacker fanno impazzire i frigoriferi in Slovenia",
    "summary": "Un attacco informatico ha surriscaldato le celle frigorifere di un'azienda alimentare a "
               "Tolmino, vicino a Udine. Sul sistema è comparsa la foto del vicepremier italiano Salvini.",
    "category": "oddities",
    "tone": "comico",
    "flags": [],
    "positive": False,
    "status": "chosen",
    "first_seen": "2026-11-27T23:16+01:00",
    "sources": [],
}
STRIKE = {**FRIDGE, "id": "2026-11-27-sciopero-dei-treni", "title": "Sciopero dei treni di 24 ore",
          "summary": "Treni fermi per 24 ore in tutta Italia.", "category": "current-affairs",
          "tone": "pungente", "flags": ["politics"], "status": "candidate"}
LIBRARY = {**FRIDGE, "id": "2026-11-26-volontari-riaprono-una-biblioteca", "title": "Volontari riaprono una biblioteca",
           "summary": "In un paese di montagna dei volontari hanno riaperto la biblioteca chiusa da anni.",
           "category": "good-news", "tone": "comico", "positive": True}

# A reel that passes every check: 7 lines, all four cats, mode B in scene 3.
LINES = [
    (1, "flanella", "Allora, in Slovenia degli hacker hanno fatto impazzire i frigoriferi di un salumificio."),
    (2, "fuzz", "No, no, no, fermi tutti! Prima i frigoriferi, poi i tostapane, poi ci attaccano la lavatrice!"),
    (3, "vinile", "Nel novantaquattro il frigo faceva solo una cosa: il freddo. E la faceva benissimo."),
    (4, "flanella", "E sullo schermo è comparsa la foto di un vicepremier."),
    (5, "fuzz", "Un salame con il ponte sullo Stretto incorporato!"),
    (6, "feedback", "Mmh. Se il frigo si scalda, almeno uno in Italia ha la febbre."),
    (7, "flanella", "Ricordatevi di spegnere il salame prima di uscire."),
]


def head_result(**changes) -> dict:
    data = {
        "chosen_angle": "Il frigo come elettrodomestico ribelle",
        "lines": [{"n": n, "cat": c, "text": t} for n, c, t in LINES],
        "scenes": [
            {"n": 1, "shot": "wide", "lines": [1], "reactions": [{"cat": "feedback", "direction": "sbadiglia"}]},
            {"n": 2, "shot": "two-fuzz-flanella", "lines": [2], "reactions": []},
            {"n": 3, "shot": "news-cutin", "lines": [], "reactions": []},
            {"n": 4, "shot": "close-vinile", "lines": [3], "reactions": []},
            {"n": 5, "shot": "wide", "lines": [4, 5], "reactions": []},
            {"n": 6, "shot": "close-feedback", "lines": [6], "reactions": []},
            {"n": 7, "shot": "close-flanella", "lines": [7], "reactions": []},
        ],
        "news_image": {"mode": "B", "scene": 3, "comment_line": 4, "held_by": None,
                       "subject": "celle frigorifere che fumano come una sauna, salami sudati"},
        "endings": [
            {"feedback": "Mmh. Il prosciutto ora è cotto.", "flanella": "Buon appetito, Slovenia."},
            {"feedback": "E quindi? Anche il frigo vuole fare carriera.", "flanella": "Chiudete lo sportello."},
        ],
        "notes": ["Ho tagliato una battuta di Vinile troppo lunga."],
    }
    data.update(changes)
    return data


def room_result() -> dict:
    h = head_result()
    draft = {"angle": "alla lettera", "lines": h["lines"], "scenes": h["scenes"], "news_image": h["news_image"]}
    return {"drafts": [draft, {**copy.deepcopy(draft), "angle": "complotto di Fuzz"}]}


def fake(head: dict | None = None, fix: dict | None = None) -> FakeModel:
    head = head or head_result()
    return FakeModel({"RoomResult": room_result(), "HeadWriterResult": head, "FixResult": fix or head})


def factory_for(model: FakeModel):
    return lambda ledger, day, step: model.for_step(step)


def setup_repo(repo: Path) -> Settings:
    shutil.copytree(REPO / "bible", repo / "bible")
    shutil.copy(REPO / "config" / "scripts.yaml", repo / "config" / "scripts.yaml")
    return load_settings(repo)


def pick_story(settings: Settings, story: dict, day: date = FRIDAY, kind: str = "daily",
               thursday: bool = False, extra: list[dict] | None = None) -> NewsStore:
    store = NewsStore(settings.tracking_dir, settings.cache_dir)
    for s in [story, *(extra or [])]:
        store.write_story(_story_meta(s))
    store.write_shortlist({
        "date": day.isoformat(), "kind": kind, "good_news_thursday": thursday, "status": "picked",
        "candidates": [story["id"], *[s["id"] for s in extra or []]], "backups": [], "picked": story["id"],
        "warning": None, "doc_url": None, "run_log": "", "cost_usd": 0.0,
    })
    return store


def _story_meta(s: dict) -> dict:
    return {"importance": 3, "importance_reason": "-", "comic_potential": 4, "comic_reason": "-",
            "effective_groups": 2, "follow_up_of": None, "episode": None, **s}
