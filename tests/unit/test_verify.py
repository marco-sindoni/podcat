from podcat.news.models import FeedItem, Source, TriageGroup
from podcat.news.verify import verify_group

SOURCES = {
    s.id: s
    for s in [
        Source(id="ansa", name="ANSA", category="current-affairs", group="ansa"),
        Source(id="corriere", name="Corriere", category="current-affairs", group="rcs"),
        Source(id="gazzetta", name="Gazzetta", category="sport", group="rcs"),
        Source(id="repubblica", name="Repubblica", category="current-affairs", group="gedi"),
        Source(id="lastampa", name="La Stampa", category="current-affairs", group="gedi"),
        Source(id="fanpage", name="Fanpage", category="current-affairs", group="ciaopeople"),
        Source(id="ilpost", name="Il Post", category="current-affairs", group="ilpost", role="confirmation-only"),
        Source(id="ilfatto", name="Il Fatto", category="current-affairs", group="sef", role="confirmation-only"),
        Source(id="lercio", name="Lercio", category="satire", group="lercio"),
        Source(id="vita", name="Vita", category="good-news", group="vita"),
        Source(id="positive", name="Positive News", category="good-news", group="positivenews"),
    ]
}


def item(source: str, n: int = 0, agency: str | None = None) -> FeedItem:
    return FeedItem(item_id=f"{source}-{n}", source_id=source, title="t", url=f"https://x/{source}/{n}", agency=agency)


def check(*items, thursday=False, **group):
    by_id = {i.item_id: i for i in items}
    g = TriageGroup(item_ids=list(by_id), category=group.pop("category", "current-affairs"), **group)
    return verify_group(g, by_id, SOURCES, thursday=thursday)


def test_two_different_groups_verified():
    v = check(item("corriere"), item("fanpage"))
    assert v.verified and v.effective_groups == ["ciaopeople", "rcs"]


def test_same_group_not_enough():
    v = check(item("corriere"), item("gazzetta"))
    assert not v.verified


def test_same_agency_counts_once():
    v = check(item("repubblica", agency="ansa"), item("fanpage", agency="ansa"))
    assert not v.verified
    assert v.effective_groups == ["ansa"]


def test_agency_plus_independent_outlet():
    v = check(item("repubblica", agency="ansa"), item("corriere"))
    assert v.verified


def test_satire_never_counts():
    assert not check(item("corriere"), item("lercio")).verified
    assert check(item("lercio"), item("lercio", 1)).reason == "solo fonti satiriche"


def test_confirmation_only_sources_cannot_start():
    v = check(item("ilpost"), item("ilfatto"))
    assert not v.verified and "conferma" in v.reason
    assert check(item("ilpost"), item("corriere")).verified


def test_excluded_topic():
    v = check(item("corriere"), item("fanpage"), excluded="crime", excluded_reason="cronaca nera")
    assert not v.verified and "crime" in v.reason


def test_thursday_needs_positive_and_one_reliable_source():
    assert not check(item("vita"), item("corriere"), thursday=True, positive=False).verified
    assert check(item("vita"), thursday=True, positive=True, category="good-news").verified
    assert check(item("corriere"), thursday=True, positive=True).verified
    assert not check(item("ilpost"), thursday=True, positive=True).verified  # confirmation-only
    assert not check(item("lercio"), thursday=True, positive=True).verified  # satire never counts
    assert not check(item("vita"), positive=True, category="good-news").verified  # other days: two groups


def test_agency_own_item_and_its_wire_count_once():
    assert not check(item("ansa"), item("repubblica", agency="ansa")).verified


# Amendment A1: one starting source is enough for light categories (FR-004, quickstart scenario 8)

LIGHT = dict(SOURCES)
LIGHT["comingsoon"] = Source(id="comingsoon", name="Comingsoon", category="entertainment", group="comingsoon")
LIGHT["upi"] = Source(id="upi", name="UPI Odd News", category="oddities", group="upi")


def check_light(*items, **group):
    by_id = {i.item_id: i for i in items}
    g = TriageGroup(item_ids=list(by_id), category=group.pop("category"), **group)
    return verify_group(g, by_id, LIGHT)


def test_single_source_ok_for_light_categories():
    for category in ("entertainment", "music", "lifestyle", "oddities"):
        assert check_light(item("comingsoon"), category=category).verified


def test_single_source_not_enough_for_other_categories():
    for category in ("current-affairs", "sport", "culture"):
        v = check_light(item("corriere"), category=category)
        assert not v.verified and "una sola fonte" in v.reason


def test_light_category_still_needs_a_starting_non_satire_source():
    assert not check_light(item("ilpost"), category="oddities").verified
    assert not check_light(item("lercio"), category="oddities").verified


def test_light_category_exclusions_still_apply():
    v = check_light(item("upi"), category="oddities", excluded="harm", excluded_reason="ferito")
    assert not v.verified and "harm" in v.reason
