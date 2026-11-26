from datetime import date, datetime, timedelta

from newsfixtures import THURSDAY_EVENING, fake_model, mock_client
from podcat.news.pipeline import gather
from podcat.news.store import NewsStore
from podcat.settings import ROME, load_settings

THURSDAY = date(2026, 11, 26)


def run(repo, day=THURSDAY, now=THURSDAY_EVENING):
    settings = load_settings(repo)
    return gather(settings, day, lambda l, d: fake_model(), now=now, http_client=mock_client(settings.config_dir))


def test_thursday_only_positive_confirmed_stories(repo):
    meta = run(repo).meta
    store = NewsStore(repo / "tracking", load_settings(repo).cache_dir)
    assert meta["good_news_thursday"] is True
    stories = [store.read_story(s) for s in meta["candidates"]]
    assert [s["title"] for s in stories] == ["Volontari riaprono una biblioteca"]
    assert all(s["positive"] for s in stories)
    assert any(src["outlet"] == "Corriere della Sera" for src in stories[0]["sources"])  # outside good-news
    assert meta["warning"] == "solo 1 notizie verificate su due fonti indipendenti."
    body = store.shortlist_path(THURSDAY, "daily").read_text()
    assert "# Giovedì buone notizie – giovedì 26 novembre 2026" in body


def test_thursday_backups_from_previous_days(repo):
    settings = load_settings(repo)
    store = NewsStore(settings.tracking_dir, settings.cache_dir)
    store.write_story({
        "id": "2026-11-23-orto-solidale", "title": "Un orto solidale", "summary": "Riassunto.",
        "category": "good-news", "sources": [{"outlet": "Vita.it", "url": "https://x/1"}],
        "effective_groups": 2, "first_seen": "2026-11-23T07:00+01:00", "importance": 3,
        "importance_reason": "r", "comic_potential": 2, "comic_reason": "r", "positive": True,
        "flags": [], "follow_up_of": None, "status": "candidate", "episode": None,
    })
    meta = run(repo).meta
    assert meta["backups"] == ["2026-11-23-orto-solidale"]
    assert "Riserve dei giorni precedenti" in store.shortlist_path(THURSDAY, "daily").read_text()


def test_editorial_gets_warm_tone_on_thursday(repo):
    settings = load_settings(repo)
    model = fake_model()
    calls = []
    original = model.parse

    def spy(system, user, schema, max_tokens):
        calls.append(system)
        return original(system, user, schema, max_tokens)

    model.parse = spy
    gather(settings, THURSDAY, lambda l, d: model, now=THURSDAY_EVENING, http_client=mock_client(settings.config_dir))
    assert "Giovedì buone notizie" in calls[-1]
