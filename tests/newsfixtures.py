"""Shared helpers for news tests: mocked HTTP for fixture feeds and a scripted fake model."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import httpx

from fakes import FakeModel
from podcat.news.sources import load_sources
from podcat.settings import ROME

FEEDS = Path(__file__).parent / "fixtures" / "feeds"
FRIDAY_7AM = datetime(2026, 11, 27, 7, 0, tzinfo=ROME)
THURSDAY_EVENING = datetime(2026, 11, 26, 21, 0, tzinfo=ROME)

# keyword -> (story key, category, excluded, positive)
STORIES = {
    "treni": ("A", "current-affairs", None, False),
    "vinil": ("B", "music", None, False),
    "rapina": ("C", "current-affairs", "crime", False),
    "sinner": ("F", "sport", None, False),
    "bibliotec": ("H", "good-news", None, True),
    "caravaggio": ("I", "culture", None, False),
    "bosco": ("J", "good-news", None, True),
}
# key -> (title, importance, comic, clarity, satirical, sensitive)
EDITORIAL = {
    "A": ("Sciopero dei treni di 24 ore", 5, 2, 4, 4, False),  # the pungente candidate
    "B": ("Il vinile supera il cd", 3, 4, 5, 1, False),  # music: one ANSA wire is enough (A1)
    "F": ("Sinner vince le Finals", 4, 3, 5, 1, False),
    "H": ("Volontari riaprono una biblioteca", 3, 3, 4, 1, False),
    "I": ("Caravaggio in mostra a Roma", 3, 3, 4, 1, True),  # flagged sensitive by the fake model
    "J": ("Una scuola pianta un bosco", 2, 3, 4, 1, False),
}

FLAGS: dict[str, list[str]] = {}  # key -> flags returned by the fake editorial (tests may patch it)


def mock_client(config_dir: Path) -> httpx.AsyncClient:
    by_url = {}
    for source in load_sources(config_dir):
        path = FEEDS / f"{source.id}.xml"
        for url in source.feeds:
            by_url[url] = path

    def handler(request: httpx.Request) -> httpx.Response:
        path = by_url.get(str(request.url))
        if path and path.exists():
            return httpx.Response(200, content=path.read_bytes())
        return httpx.Response(404)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def triage_answer(user: str) -> dict:
    groups: dict[str, dict] = {}
    for line in user.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        item_id, _, title = parts[0], parts[1], parts[2].lower()
        for keyword, (key, category, excluded, positive) in STORIES.items():
            if keyword in title:
                g = groups.setdefault(
                    key,
                    {"item_ids": [], "category": category, "excluded": excluded,
                     "excluded_reason": "cronaca nera" if excluded else None, "positive": positive},
                )
                g["item_ids"].append(item_id)
    return {"groups": list(groups.values())}


def editorial_answer(user: str) -> dict:
    stories = []
    for match in re.finditer(r"\[(\d+)\][^\[]*", user):
        block = match.group(0).lower()
        for keyword, (key, *_rest) in STORIES.items():
            if keyword in block and key in EDITORIAL:
                title, importance, comic, clarity, satire, sensitive = EDITORIAL[key]
                stories.append({
                    "group_index": int(match.group(1)), "title": title,
                    "summary": f"{title}: riassunto neutro di prova.", "importance": importance,
                    "importance_reason": "molto ripresa", "comic_potential": comic,
                    "comic_reason": "si presta a battute", "clarity": clarity,
                    "clarity_reason": "si capisce subito", "satirical_potential": satire,
                    "satirical_reason": "spunto pungente", "sensitive": sensitive, "flags": FLAGS.get(key, []), "follow_up_of": None,
                    "already_covered": False,
                })
                break
    return {"stories": stories}


def fake_model() -> FakeModel:
    return FakeModel({"TriageResult": triage_answer, "EditorialResult": editorial_answer})
