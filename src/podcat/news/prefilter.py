"""Free filters applied before any paid step: duplicates and clickbait headlines."""

from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

from podcat.news.models import FeedItem

CLICKBAIT = [
    r"non crederai",
    r"\bshock\b",
    r"\bchoc\b",
    r"incredibile ma vero",
    r"ecco cosa (è successo|succede)",
    r"(guarda|guardate) (il video|cosa)",
    r"lascia (tutti )?senza parole",
    r"da non credere",
    r"\bsconvolgente\b",
    r"\bclamoroso\b.*\?$",
    r"you won'?t believe",
]
CLICKBAIT_RE = [re.compile(p, re.IGNORECASE) for p in CLICKBAIT]


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def is_clickbait(title: str) -> bool:
    return any(p.search(title) for p in CLICKBAIT_RE)


def prefilter(items: list[FeedItem]) -> tuple[list[FeedItem], list[dict]]:
    """Return kept items and the list of discarded ones with their reason."""
    seen_urls: set[str] = set()
    seen_titles: set[tuple[str, str]] = set()
    kept, discarded = [], []
    for item in items:
        url = normalize_url(item.url)
        key = (item.source_id, item.title.lower())
        if url in seen_urls or key in seen_titles:
            continue  # exact duplicate, not worth logging
        seen_urls.add(url)
        seen_titles.add(key)
        if is_clickbait(item.title):
            discarded.append({"title": item.title, "source": item.source_id, "reason": "clickbait"})
            continue
        kept.append(item)
    return kept, discarded
