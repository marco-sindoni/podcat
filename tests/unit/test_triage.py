"""Spec 001 A1: triage keeps single-article groups in light categories and excludes harm (R14, R15)."""

from fakes import FakeModel
from podcat.news import triage
from podcat.news.models import FeedItem, Source

SOURCES = {
    "ansa": Source(id="ansa", name="ANSA", category="current-affairs", group="ansa"),
    "upi": Source(id="upi", name="UPI", category="oddities", group="upi"),
}
ITEMS = [FeedItem(item_id=f"i{n}", source_id=src, title=f"t{n}", url=f"https://x/{n}")
         for n, src in enumerate(["ansa", "upi", "ansa"])]


def test_weekday_keeps_single_item_groups_only_in_light_categories():
    answer = {"groups": [
        {"item_ids": ["i0"], "category": "current-affairs"},
        {"item_ids": ["i1"], "category": "oddities"},
        {"item_ids": ["i2"], "category": "music"},
        {"item_ids": ["i0", "i2"], "category": "sport"},
    ]}
    result, _ = triage.triage(FakeModel({"TriageResult": answer}), ITEMS, SOURCES)
    assert [g.category for g in result.groups] == ["oddities", "music", "sport"]


def test_prompt_knows_oddities_and_harm_but_allows_retirements():
    assert "oddities" in triage.SYSTEM and "harm:" in triage.SYSTEM
    assert "ritiro NON è harm" in triage.SYSTEM


def test_long_daily_lists_are_chunked_by_category_and_merged(monkeypatch):
    monkeypatch.setattr(triage, "DAILY_CHUNK", 2)
    sources = dict(SOURCES, leggo=Source(id="leggo", name="Leggo", category="oddities", group="caltagirone"))
    items = [FeedItem(item_id="a1", source_id="ansa", title="Frigoriferi hackerati", url="https://x/a1"),
             FeedItem(item_id="a2", source_id="ansa", title="Frigoriferi hackerati bis", url="https://x/a2"),
             FeedItem(item_id="l1", source_id="leggo", title="Hacker e salumi", url="https://x/l1"),
             FeedItem(item_id="u1", source_id="upi", title="Cane record", url="https://x/u1")]

    def answer(user):
        if "a1" in user:
            return {"groups": [{"item_ids": ["a1", "a2"], "category": "current-affairs"}]}
        return {"groups": [{"item_ids": ["l1"], "category": "oddities"}, {"item_ids": ["u1"], "category": "oddities"}]}

    model = FakeModel({"TriageResult": answer, "MergeResult": {"merges": [[0, 1]]}})
    result, _ = triage.triage(model, items, sources)
    assert [c[0] for c in model.calls] == ["TriageResult", "TriageResult", "MergeResult"]
    assert [g.item_ids for g in result.groups] == [["a1", "a2", "l1"], ["u1"]]


def test_short_daily_lists_need_one_call():
    model = FakeModel({"TriageResult": {"groups": []}})
    triage.triage(model, ITEMS, SOURCES)
    assert [c[0] for c in model.calls] == ["TriageResult"]
