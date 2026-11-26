from datetime import date

from fakes import FakeModel
from podcat.news.shortlist import pick
from podcat.news.store import NewsStore
from podcat.news.weekly import week_start, weekly
from podcat.settings import load_settings

SATURDAY = date(2026, 11, 28)


def story(store, sid, day, status="candidate", importance=3):
    store.write_story({
        "id": sid, "title": f"Titolo {sid}", "summary": "Riassunto.", "category": "current-affairs",
        "sources": [{"outlet": "ANSA", "url": f"https://x/{sid}"}], "effective_groups": 2,
        "first_seen": f"{day}T07:00+01:00", "importance": importance, "importance_reason": "r",
        "comic_potential": 3, "comic_reason": "r", "positive": False, "flags": [],
        "follow_up_of": None, "status": status, "episode": None,
    })


def model_picking(ids):
    def answer(user):
        return {"picks": [{"story_id": i, "weekly_importance": 5 - n, "reason": "ok"} for n, i in enumerate(ids)]}
    return FakeModel({"WeeklyResult": answer})


def setup(repo):
    settings = load_settings(repo)
    store = NewsStore(settings.tracking_dir, settings.cache_dir)
    story(store, "a", "2026-11-22", status="used")
    story(store, "b", "2026-11-24")
    story(store, "c", "2026-11-26", status="chosen")
    story(store, "old", "2026-11-20")  # previous week
    story(store, "rej", "2026-11-25", status="rejected")
    for d in ("2026-11-23", "2026-11-24"):
        store.write_shortlist({"date": d, "kind": "daily", "candidates": [], "status": "proposed"})
    return settings, store


def test_week_start_is_sunday():
    assert week_start(SATURDAY) == date(2026, 11, 22)
    assert week_start(date(2026, 11, 22)) == date(2026, 11, 22)


def test_weekly_uses_only_this_week_and_marks_used(repo):
    settings, store = setup(repo)
    model = model_picking(["c", "a", "b", "old", "rej"])
    result = weekly(settings, SATURDAY, lambda l, d: model)
    meta = result.meta
    assert meta["candidates"] == ["c", "a", "b"]
    assert "old" not in model.calls[0][1] and "rej" not in model.calls[0][1]
    assert "2026-11-22" in meta["gaps"] and "2026-11-23" not in meta["gaps"]
    body = store.shortlist_path(SATURDAY, "weekly").read_text()
    assert "già usata" in body and "nuova" in body and "Giorni senza giro" in body
    table = [l for l in body.splitlines() if l.startswith("|")]
    assert table[0].endswith("| Fonti | Reel |")
    assert len({l.count("|") for l in table}) == 1  # header, separator and rows have the same columns


def test_weekly_idempotent(repo):
    settings, store = setup(repo)
    model = model_picking(["b", "c", "a"])
    first = weekly(settings, SATURDAY, lambda l, d: model)
    second = weekly(settings, SATURDAY, lambda l, d: model)
    assert not second.created and second.meta == first.meta and len(model.calls) == 1


def test_weekly_pick_keeps_story_status(repo):
    settings, store = setup(repo)
    weekly(settings, SATURDAY, lambda l, d: model_picking(["a", "b", "c"]))
    pick(store, SATURDAY, "weekly", 1)
    assert store.read_story("a")["status"] == "used"
    assert store.read_shortlist(SATURDAY, "weekly")["picked"] == "a"


def test_weekly_without_stories_costs_nothing(repo):
    settings = load_settings(repo)
    model = model_picking([])
    meta = weekly(settings, SATURDAY, lambda l, d: model).meta
    assert meta["candidates"] == [] and model.calls == [] and "nessuna" in meta["warning"]
