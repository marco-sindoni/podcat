from datetime import date

import pytest

from newsfixtures import FRIDAY_7AM, fake_model, mock_client
from podcat.news.pipeline import gather
from podcat.news.store import NewsStore
from podcat.settings import load_settings
from podcat.tracking.costs import Ledger, load_prices

FRIDAY = date(2026, 11, 27)


def run(repo, model, refresh=False, day=FRIDAY, now=FRIDAY_7AM):
    settings = load_settings(repo)
    return gather(
        settings, day, lambda ledger, d: model, refresh=refresh, now=now,
        http_client=mock_client(settings.config_dir),
    )


def titles(repo, ids):
    store = NewsStore(repo / "tracking", load_settings(repo).cache_dir)
    return [store.read_story(i)["title"] for i in ids]


def test_daily_gather_end_to_end(repo):
    model = fake_model()
    result = run(repo, model)
    meta = result.meta
    assert result.created
    # A (trains), F (Sinner), I (Caravaggio), H (library) are verified; B is one ANSA wire, C is crime.
    assert titles(repo, meta["candidates"]) == [
        "Sciopero dei treni di 24 ore",
        "Sinner vince le Finals",
        "Volontari riaprono una biblioteca",  # same importance as Caravaggio, higher comic potential
        "Caravaggio in mostra a Roma",
    ]
    assert len(meta["candidates"]) == 4
    assert meta["warning"] is None and meta["good_news_thursday"] is False

    store = NewsStore(repo / "tracking", load_settings(repo).cache_dir)
    trains = store.read_story(meta["candidates"][0])
    assert trains["effective_groups"] == 3
    assert {s["outlet"] for s in trains["sources"]} == {"ANSA", "Corriere della Sera", "Sky TG24"}
    assert all(s["url"].startswith("https://example.org/") for s in trains["sources"])

    log = (repo / meta["run_log"]).read_text()
    assert "clickbait" in log and "crime" in log and "agenzia" in log
    assert "Vecchia notizia" not in str(model.calls)  # outside the 24 h window
    assert "Lercio" not in model.calls[0][1]  # satire never goes to triage

    body = (repo / "tracking/news/shortlists/2026-11-27-daily.md").read_text()
    assert "# Notizie candidate – venerdì 27 novembre 2026" in body
    assert "| 1 | Sciopero dei treni di 24 ore |" in body


def test_second_run_is_free_and_unchanged(repo):
    model = fake_model()
    first = run(repo, model)
    calls = len(model.calls)
    second = run(repo, model)
    assert not second.created
    assert second.meta == first.meta
    assert len(model.calls) == calls


def test_cost_recorded_through_ledger(repo):
    # The fake model does not write the ledger; the shortlist still reports the run cost.
    result = run(repo, fake_model())
    assert result.meta["cost_usd"] > 0
    assert Ledger(repo / "tracking", load_prices(repo / "config")).total(FRIDAY) == 0


def test_cached_steps_reused_after_crash(repo):
    model = fake_model()
    run(repo, model)
    (repo / "tracking/news/shortlists/2026-11-27-daily.md").unlink()
    for f in (repo / "tracking/news/stories").glob("*.md"):
        f.unlink()
    calls = len(model.calls)
    result = run(repo, model)
    assert result.created and len(model.calls) == calls  # triage and editorial came from the cache
