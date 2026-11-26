from datetime import date

import pytest

from newsfixtures import FRIDAY_7AM, fake_model, mock_client
from podcat.news.pipeline import gather
from podcat.news.shortlist import ShortlistError, link_doc, pick, reject, unpick
from podcat.news.store import NewsStore
from podcat.settings import load_settings

FRIDAY = date(2026, 11, 27)


@pytest.fixture
def setup(repo):
    settings = load_settings(repo)
    model = fake_model()

    def run(refresh=False):
        return gather(settings, FRIDAY, lambda l, d: model, refresh=refresh, now=FRIDAY_7AM,
                      http_client=mock_client(settings.config_dir))

    meta = run().meta
    return NewsStore(settings.tracking_dir, settings.cache_dir), meta, run


def test_pick_and_change(setup):
    store, meta, _ = setup
    first = pick(store, FRIDAY, "daily", 2)
    assert store.read_story(first)["status"] == "chosen"
    second = pick(store, FRIDAY, "daily", 1)
    assert store.read_story(first)["status"] == "candidate"
    assert store.read_story(second)["status"] == "chosen"
    sl = store.read_shortlist(FRIDAY, "daily")
    assert sl["picked"] == second and sl["status"] == "picked"
    assert "✅" in store.shortlist_path(FRIDAY, "daily").read_text()


def test_pick_out_of_range(setup):
    store, meta, _ = setup
    with pytest.raises(ShortlistError):
        pick(store, FRIDAY, "daily", 9)


def test_unpick_blocked_when_script_exists(setup):
    store, meta, _ = setup
    sid = pick(store, FRIDAY, "daily", 1)
    store.set_story(sid, status="used", episode="2026-11-27-reel")
    with pytest.raises(ShortlistError):
        unpick(store, FRIDAY, "daily")
    with pytest.raises(ShortlistError):
        pick(store, FRIDAY, "daily", 2)


def test_unpick(setup):
    store, meta, _ = setup
    sid = pick(store, FRIDAY, "daily", 1)
    unpick(store, FRIDAY, "daily")
    assert store.read_story(sid)["status"] == "candidate"
    assert store.read_shortlist(FRIDAY, "daily")["picked"] is None


def test_reject_then_refresh_excludes_rejected(setup):
    store, meta, run = setup
    rejected = reject(store, FRIDAY, "daily")
    assert all(store.read_story(s)["status"] == "rejected" for s in rejected)
    new = run(refresh=True).meta
    assert not set(new["candidates"]) & set(rejected)
    assert new["candidates"] == []  # every fixture story was rejected
    assert "nessuna notizia" in new["warning"]


def test_refresh_refused_after_pick(setup):
    store, meta, run = setup
    pick(store, FRIDAY, "daily", 1)
    with pytest.raises(ShortlistError):
        run(refresh=True)


def test_link_doc(setup):
    store, meta, _ = setup
    link_doc(store, FRIDAY, "daily", "https://claude.ai/artifact/abc")
    assert store.read_shortlist(FRIDAY, "daily")["doc_url"] == "https://claude.ai/artifact/abc"
    with pytest.raises(ShortlistError):
        link_doc(store, FRIDAY, "daily", "ftp://x")
