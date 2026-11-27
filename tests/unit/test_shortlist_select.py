"""Spec 001 amendment A1: floors, comedy-first order, politics cap, pungente slot (quickstart 7, 7b)."""

from podcat.news.shortlist import choose, warning_for


def s(id, comic=4, clarity=4, importance=3, satire=1, category="current-affairs", flags=(), sensitive=False):
    return {"id": id, "title": id, "comic_potential": comic, "clarity": clarity, "importance": importance,
            "satirical_potential": satire, "category": category, "flags": list(flags), "sensitive": sensitive}


def ids(result):
    return [x["id"] for x in result.chosen]


def test_floors_discard_with_reasons():
    stories = [s("ok"), s("unfunny", comic=2), s("unclear", clarity=2), s("minor", importance=1),
               s("harm", sensitive=True)]
    result = choose(stories)
    assert ids(result) == ["ok"]
    assert {d["title"]: d["reason"] for d in result.discarded} == {
        "unfunny": "comicità sotto 3", "unclear": "poco comprensibile", "minor": "poco rilevante",
        "harm": "tema delicato",
    }


def test_order_comic_plus_clarity_beats_importance():
    stories = [s("big-news", comic=3, clarity=3, importance=5, category="sport"),
               s("jet-ski", comic=4, clarity=5, importance=2, category="sport")]
    assert ids(choose(stories)) == ["jet-ski", "big-news"]


def test_tie_breaks_comic_then_importance():
    stories = [s("a", comic=3, clarity=5, category="music"), s("b", comic=4, clarity=4, category="sport"),
               s("c", comic=4, clarity=4, importance=4, category="culture")]
    assert ids(choose(stories)) == ["c", "b", "a"]


def test_at_most_one_politics_story():
    stories = [s("p1", comic=5, flags=["politics"]), s("p2", comic=4, flags=["politics"], category="sport"),
               s("other", comic=3, category="music")]
    result = choose(stories)
    assert ids(result) == ["p1", "other"]
    assert {"title": "p2", "reason": "già una notizia politica"} in result.discarded


def test_category_cap_two_then_fill_when_no_variety():
    stories = [s(f"sport{n}", comic=5 - n, category="sport") for n in range(4)] + [s("music", comic=2, clarity=5, category="music")]
    # cap 2 per category while other categories have eligible stories; music is below the floor
    assert ids(choose(stories, limit=2)) == ["sport0", "sport1"]
    mixed = [s(f"sport{n}", comic=5 - n, category="sport") for n in range(3)] + [s("music", comic=3, category="music")]
    # the third sport story only fills a free slot after every other category is in
    assert ids(choose(mixed, limit=3)) == ["sport0", "sport1", "music"]
    assert ids(choose(mixed)) == ["sport0", "sport1", "music", "sport2"]
    only_sport = [s(f"sport{n}", comic=5 - n, category="sport") for n in range(3)]
    assert ids(choose(only_sport)) == ["sport0", "sport1", "sport2"]


def test_no_padding_below_floors():
    result = choose([s("good"), s("bad1", comic=1), s("bad2", clarity=1)])
    assert ids(result) == ["good"]
    assert warning_for(len(result.chosen)) == "solo 1 notizie verificate e adatte al reel."


def test_pungente_slot_filled_last_and_marked():
    comic = [s(f"c{n}", comic=5, clarity=5 - n % 2, category=cat)
             for n, cat in enumerate(["sport", "music", "lifestyle", "culture", "oddities"])]
    sharp = s("sharp", comic=2, clarity=4, importance=4, satire=4)
    result = choose(comic + [sharp])
    assert len(result.chosen) == 5
    assert result.chosen[-1]["id"] == "sharp" and result.chosen[-1]["tone"] == "pungente"
    assert all(x["tone"] == "comico" for x in result.chosen[:-1])
    assert not result.no_pungente


def test_pungente_needs_its_floors():
    weak = [s("low-importance", comic=2, satire=5, importance=2), s("unclear", comic=2, satire=5, clarity=2)]
    result = choose([s("c")] + weak)
    assert ids(result) == ["c"] and result.no_pungente


def test_funnier_than_sharp_stays_comic():
    result = choose([s("funny", comic=5, satire=4, importance=4)])
    assert result.chosen[0]["tone"] == "comico" and result.no_pungente


def test_pungente_counts_for_politics_cap():
    sharp = s("sharp", comic=2, satire=5, importance=4, flags=["politics"])
    result = choose([sharp, s("p-comic", comic=5, flags=["politics"]), s("c", category="music")])
    assert ids(result) == ["c", "sharp"]


def test_no_pungente_on_thursday():
    sharp = s("sharp", comic=2, satire=5, importance=4, category="good-news")
    result = choose([sharp, s("c", category="good-news")], thursday=True)
    assert ids(result) == ["c"] and not result.no_pungente
