from podcat.scripts.models import Line, Scene
from podcat.scripts.timing import apply_timing, count_words, spoken_words

CFG = {"words_per_second": {"flanella": 2.0, "fuzz": 3.0, "vinile": 2.5, "feedback": 2.0},
       "pause_s": 0.5, "fixed_shot_s": {"news-cutin": 2.5, "sting-gnocchi": 3.0}, "silent_default_s": 1.5}


def test_count_words_italian():
    assert count_words("L'aria è fresca, no?") == 4
    assert count_words("Nel '94... boh!") == 3
    assert count_words("") == 0


def test_spoken_words_skips_formula():
    lines = [Line(n=1, cat="flanella", text="Giovedì buone notizie! Oggi si ride.")]
    assert spoken_words(lines, skip_text="Giovedì buone notizie!") == 3
    assert spoken_words(lines) == 6


def test_durations_and_sting_excluded():
    lines = [Line(n=1, cat="flanella", text="uno due tre quattro"), Line(n=2, cat="fuzz", text="uno due tre")]
    scenes = [Scene(n=1, shot="sting-gnocchi", lines=[]), Scene(n=2, shot="wide", lines=[1, 2]),
              Scene(n=3, shot="news-cutin", lines=[]), Scene(n=4, shot="react-vinile", lines=[])]
    out, total = apply_timing(lines, scenes, CFG)
    assert [s.duration_s for s in out] == [3.0, 4.0, 2.5, 1.5]
    assert total == 8.0
