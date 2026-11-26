"""Approved sources: loading, validation and the feed check (research R1)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import feedparser
import httpx
import yaml

from podcat.news.models import Source

USER_AGENT = "podcat-news/0.1 (+https://github.com/marco-sindoni/podcat)"
TIMEOUT_S = 10.0

HEADER = """# Approved news sources (generated from docs/news-sources.md, approved 2026-11-25).
# Fields: see specs/001-news-gathering/data-model.md (Source).
# `group` = publishing group: sources in the same group never confirm each other.
# `podcat sources check --write` verifies `feeds`, tries autodiscovery from `home`
# and sets `manual: true` when nothing works.
"""


def sources_path(config_dir: Path) -> Path:
    return config_dir / "sources.yaml"


def load_sources(config_dir: Path) -> list[Source]:
    data = yaml.safe_load(sources_path(config_dir).read_text(encoding="utf-8")) or {}
    sources = [Source.model_validate(raw) for raw in data.get("sources", [])]
    ids = [s.id for s in sources]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"Duplicate source ids in config/sources.yaml: {sorted(dupes)}")
    return sources


def save_sources(config_dir: Path, sources: list[Source]) -> None:
    lines = [HEADER, "sources:"]
    for s in sources:
        data = s.model_dump(exclude_none=True)
        if data.get("role") == "starting":
            data.pop("role")
        if not data.get("manual"):
            data.pop("manual", None)
        lines.append("  - " + yaml.safe_dump(data, default_flow_style=True, allow_unicode=True, width=10_000, sort_keys=False).strip())
    sources_path(config_dir).write_text("\n".join(lines) + "\n", encoding="utf-8")


class _FeedLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag != "link":
            return
        a = dict(attrs)
        if (a.get("rel") or "").lower() == "alternate" and (a.get("type") or "").lower() in (
            "application/rss+xml",
            "application/atom+xml",
        ) and a.get("href"):
            self.links.append(a["href"])


def discover_feeds(html: str, base_url: str) -> list[str]:
    parser = _FeedLinkParser()
    parser.feed(html)
    return [urljoin(base_url, href) for href in parser.links]


def is_feed(content: bytes) -> bool:
    parsed = feedparser.parse(content)
    return bool(parsed.entries) and not (parsed.bozo and not parsed.entries)


@dataclass
class CheckResult:
    source: Source
    status: str  # ok | discovered | manual
    working: list[str]
    note: str = ""


async def _get(client: httpx.AsyncClient, url: str) -> bytes | None:
    try:
        response = await client.get(url)
        if response.status_code == 200:
            return response.content
    except httpx.HTTPError:
        return None
    return None


async def _check_one(client: httpx.AsyncClient, source: Source) -> CheckResult:
    working = []
    for url in source.feeds:
        content = await _get(client, url)
        if content and is_feed(content):
            working.append(url)
    if working:
        return CheckResult(source, "ok", working)
    if source.home:
        page = await _get(client, source.home)
        if page:
            for url in discover_feeds(page.decode("utf-8", errors="replace"), source.home)[:3]:
                content = await _get(client, url)
                if content and is_feed(content):
                    return CheckResult(source, "discovered", [url])
    return CheckResult(source, "manual", [], note="nessun feed funzionante")


async def check_sources(sources: list[Source], client: httpx.AsyncClient | None = None) -> list[CheckResult]:
    own = client is None
    client = client or httpx.AsyncClient(
        timeout=TIMEOUT_S, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    )
    try:
        return await asyncio.gather(*(_check_one(client, s) for s in sources))
    finally:
        if own:
            await client.aclose()


def apply_check(results: list[CheckResult], today: str) -> list[Source]:
    updated = []
    for r in results:
        s = r.source.model_copy()
        s.feeds = r.working or s.feeds
        s.manual = r.status == "manual"
        s.last_check = today
        updated.append(s)
    return updated
