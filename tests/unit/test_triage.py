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
