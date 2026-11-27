import asyncio

import httpx

from podcat.news.models import Source
from podcat.news.sources import apply_check, check_sources, discover_feeds, load_sources, save_sources

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>
<item><title>Notizia</title><link>https://x.it/1</link></item></channel></rss>"""
HOME = b"""<html><head><link rel="alternate" type="application/rss+xml" href="/feed/"></head></html>"""


def client():
    def handler(request):
        url = str(request.url)
        if url == "https://ok.it/rss":
            return httpx.Response(200, content=RSS)
        if url == "https://disc.it/":
            return httpx.Response(200, content=HOME)
        if url == "https://disc.it/feed/":
            return httpx.Response(200, content=RSS)
        return httpx.Response(404)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_check_ok_discovered_manual():
    sources = [
        Source(id="ok", name="Ok", category="sport", group="a", feeds=["https://ok.it/rss"]),
        Source(id="disc", name="Disc", category="sport", group="b", home="https://disc.it/", feeds=["https://disc.it/old"]),
        Source(id="none", name="None", category="sport", group="c", home="https://none.it/"),
    ]
    results = asyncio.run(check_sources(sources, client()))
    assert [r.status for r in results] == ["ok", "discovered", "manual"]
    updated = apply_check(results, "2026-11-26")
    assert updated[1].feeds == ["https://disc.it/feed/"]
    assert updated[2].manual and updated[2].last_check == "2026-11-26"


def test_discover_feeds_relative_links():
    assert discover_feeds(HOME.decode(), "https://disc.it/") == ["https://disc.it/feed/"]


def test_real_config_loads_and_roundtrips(repo):
    sources = load_sources(repo / "config")
    assert len(sources) == 94
    assert {s.category for s in sources} >= {"current-affairs", "good-news", "oddities", "satire"}
    save_sources(repo / "config", sources)
    assert [s.model_dump() for s in load_sources(repo / "config")] == [s.model_dump() for s in sources]
