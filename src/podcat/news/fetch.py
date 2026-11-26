"""Concurrent feed fetching, time window and agency detection (research R2, R4)."""

from __future__ import annotations

import asyncio
import calendar
import hashlib
import html
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import httpx
import yaml

from podcat.news.models import FeedItem, Source
from podcat.news.sources import TIMEOUT_S, USER_AGENT

SNIPPET_CHARS = 200
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def load_agencies(config_dir: Path) -> dict[str, list[re.Pattern]]:
    data = yaml.safe_load((config_dir / "agencies.yaml").read_text(encoding="utf-8"))
    return {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in data["agencies"].items()}


def detect_agency(text: str, agencies: dict[str, list[re.Pattern]]) -> str | None:
    for agency, patterns in agencies.items():
        if any(p.search(text) for p in patterns):
            return agency
    return None


def clean(text: str) -> str:
    return SPACE_RE.sub(" ", html.unescape(TAG_RE.sub(" ", text or ""))).strip()


def item_id(source_id: str, url: str) -> str:
    return f"{source_id}-{hashlib.sha1(url.encode('utf-8')).hexdigest()[:8]}"


def _published(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return datetime.fromtimestamp(calendar.timegm(value), tz=timezone.utc)
    return None


def parse_feed(content: bytes, source: Source, agencies: dict[str, list[re.Pattern]]) -> list[FeedItem]:
    parsed = feedparser.parse(content)
    items = []
    for entry in parsed.entries:
        url = entry.get("link")
        title = clean(entry.get("title", ""))
        if not url or not title:
            continue
        snippet = clean(entry.get("summary", ""))[:SNIPPET_CHARS]
        items.append(
            FeedItem(
                item_id=item_id(source.id, url),
                source_id=source.id,
                title=title,
                summary_snippet=snippet,
                url=url,
                published_at=_published(entry),
                agency=detect_agency(f"{title} {snippet}", agencies),
            )
        )
    return items


@dataclass
class FetchReport:
    items: list[FeedItem] = field(default_factory=list)
    feeds_ok: list[str] = field(default_factory=list)
    feeds_failed: list[dict] = field(default_factory=list)


async def _fetch(client: httpx.AsyncClient, url: str) -> tuple[bytes | None, str | None]:
    try:
        response = await client.get(url)
    except httpx.HTTPError as exc:
        return None, type(exc).__name__
    if response.status_code != 200:
        return None, f"HTTP {response.status_code}"
    return response.content, None


async def fetch_all(
    sources: list[Source],
    agencies: dict[str, list[re.Pattern]],
    client: httpx.AsyncClient | None = None,
) -> FetchReport:
    own = client is None
    client = client or httpx.AsyncClient(
        timeout=TIMEOUT_S, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    )
    jobs = [(s, url) for s in sources if not s.manual for url in s.feeds]
    report = FetchReport()
    try:
        results = await asyncio.gather(*(_fetch(client, url) for _, url in jobs))
    finally:
        if own:
            await client.aclose()
    for (source, url), (content, error) in zip(jobs, results):
        if content is None:
            report.feeds_failed.append({"source": source.id, "url": url, "error": error})
            continue
        items = parse_feed(content, source, agencies)
        if not items and feedparser.parse(content).bozo:
            report.feeds_failed.append({"source": source.id, "url": url, "error": "feed non leggibile"})
            continue
        report.feeds_ok.append(url)
        report.items.extend(items)
    return report


def in_window(items: list[FeedItem], end: datetime, hours: int = 24) -> list[FeedItem]:
    start = end - timedelta(hours=hours)
    kept = []
    for item in items:
        if item.published_at is None:
            continue  # undated items cannot be placed in the window
        if start <= item.published_at <= end + timedelta(minutes=5):
            kept.append(item)
    return kept
