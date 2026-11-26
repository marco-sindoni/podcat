from datetime import datetime, timedelta

from podcat.news.fetch import in_window
from podcat.news.models import FeedItem
from podcat.news.prefilter import is_clickbait, prefilter
from podcat.settings import ROME

NOW = datetime(2026, 11, 27, 7, 0, tzinfo=ROME)


def item(n, title="Titolo", url=None, source="corriere", hours_ago=1):
    return FeedItem(
        item_id=f"i{n}", source_id=source, title=title, url=url or f"https://x.it/{n}",
        published_at=NOW - timedelta(hours=hours_ago),
    )


def test_duplicate_urls_and_titles_removed():
    items = [item(1, url="https://x.it/a"), item(2, url="https://X.it/a/"), item(3, title="Titolo")]
    kept, discarded = prefilter(items)
    assert [i.item_id for i in kept] == ["i1"]
    assert discarded == []


def test_clickbait_discarded_with_reason():
    kept, discarded = prefilter([item(1, title="Non crederai a cosa è successo"), item(2, title="Sciopero dei treni")])
    assert [i.item_id for i in kept] == ["i2"]
    assert discarded[0]["reason"] == "clickbait"


def test_clickbait_words():
    assert is_clickbait("SHOCK in diretta")
    assert not is_clickbait("Sinner vince le Finals")


def test_window_24_hours():
    items = [item(1, hours_ago=1), item(2, hours_ago=23), item(3, hours_ago=25)]
    undated = FeedItem(item_id="u", source_id="corriere", title="t", url="https://x.it/u")
    assert [i.item_id for i in in_window(items + [undated], NOW)] == ["i1", "i2"]
