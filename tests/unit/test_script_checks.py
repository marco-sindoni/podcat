import copy

import pytest
import yaml

from podcat.scripts.checks import CheckContext, check
from podcat.scripts.models import HeadWriterResult
from podcat.scripts.timing import apply_timing
from scriptfixtures import REPO, head_result

CFG = yaml.safe_load((REPO / "config" / "scripts.yaml").read_text(encoding="utf-8"))
SHOTS = {"wide", "two-fuzz-flanella", "two-flanella-vinile", "two-vinile-feedback", "news-cutin", "news-tv",
         "sting-gnocchi", *(f"{p}-{c}" for p in ("close", "react", "news-held") for c in ("flanella", "fuzz", "vinile", "feedback"))}


def ctx(**kw):
    base = dict(kind="daily", thursday=False, category="oddities", allowed_modes=["A", "B"], shots=SHOTS, config=CFG)
    base.update(kw)
    return CheckContext(**base)


def run(data=None, **kw):
    r = HeadWriterResult.model_validate(data or head_result())
    formula = CFG["thursday_formula"] if kw.get("thursday") else None
    scenes, total = apply_timing(r.lines, r.scenes, CFG, skip_text=formula)
    return check(r.lines, scenes, r.news_image, r.endings, total, ctx(**kw))


def test_valid_fixture_passes():
    assert run() == []


def test_structure():
    d = head_result()
    d["lines"][0]["cat"] = "fuzz"
    d["lines"][-2]["cat"] = "vinile"
    problems = run(d)
    assert any("prima battuta" in p for p in problems)
    assert any("penultima" in p for p in problems)


def test_word_limits():
    d = head_result()
    d["lines"][2]["text"] = "Boh."
    d["lines"][1]["text"] = "Boh."
    assert any(p.startswith("Parole:") for p in run(d))


def test_silent_cat_needs_reaction():
    d = head_result()
    d["lines"][2]["cat"] = "fuzz"  # Vinile no longer speaks
    d["scenes"][3]["shot"] = "close-fuzz"
    assert any("Vinile non parla" in p for p in run(d))
    d["scenes"][0]["reactions"].append({"cat": "vinile", "direction": "alza gli occhi al cielo"})
    assert not any("Vinile non parla" in p for p in run(d))


def test_vinile_must_speak_on_culture():
    d = head_result()
    d["lines"][2]["cat"] = "fuzz"
    d["scenes"][3]["shot"] = "close-fuzz"
    d["scenes"][0]["reactions"].append({"cat": "vinile", "direction": "sbuffa"})
    assert any("Vinile deve parlare" in p for p in run(d, category="music"))


def test_mode_rotation_and_shot():
    assert any("uguale al video precedente" in p for p in run(allowed_modes=["A", "C"]))
    d = head_result()
    d["scenes"][2]["shot"] = "wide"
    assert any("news-cutin" in p for p in run(d))


def test_mode_c_holder_speaks():
    d = head_result()
    d["news_image"] = {"mode": "C", "scene": 4, "comment_line": 3, "held_by": "fuzz", "subject": "x"}
    d["scenes"][3]["shot"] = "news-held-fuzz"
    d["scenes"][2]["shot"] = "wide"
    assert any("deve parlare in quella scena" in p for p in run(d, allowed_modes=["C"]))


def test_scenes_cover_lines_in_order_and_shots_known():
    d = head_result()
    d["scenes"][4]["lines"] = [5]
    d["scenes"][1]["shot"] = "two-fuzz-feedback"
    problems = run(d)
    assert any("una sola scena" in p for p in problems)
    assert any("sconosciuta" in p for p in problems)


def test_close_up_only_its_cat():
    d = head_result()
    d["scenes"][3]["shot"] = "close-fuzz"
    assert any("parla un altro gatto" in p for p in run(d))


def test_thursday_formula_and_sting():
    problems = run(thursday=True)
    assert any("stacchetto degli gnocchi" in p for p in problems)
    assert any("formula" in p for p in problems)
    d = head_result()
    d["lines"][0]["text"] = CFG["thursday_formula"] + " " + d["lines"][0]["text"]
    d["scenes"] = [{"n": 1, "shot": "sting-gnocchi", "lines": [], "reactions": []}] + [
        {**s, "n": s["n"] + 1} for s in d["scenes"]]
    d["news_image"]["scene"] = 4
    assert run(d, thursday=True) == []


def test_endings_required():
    d = head_result(endings=[head_result()["endings"][0]])
    assert any("2 finali" in p for p in run(d))


def test_repetition():
    first = head_result()["lines"][0]["text"]
    assert any("prima battuta è uguale" in p for p in run(recent_first_lines=[first]))
    with_tic = ["Ricapitoliamo, gente.", "Ricapitoliamo: niente."]
    d = head_result()
    d["lines"][3]["text"] = "Ricapitoliamo: sullo schermo è comparsa la foto di un vicepremier."
    assert any("Ricapitoliamo" in p for p in run(d, recent_texts=with_tic))
    assert not any("Ricapitoliamo" in p for p in run(d, recent_texts=with_tic[:1]))
    assert not any("Ricapitoliamo" in p for p in run(recent_texts=with_tic))


def test_weekly_needs_two_lines_each():
    problems = run(kind="weekly")
    assert any("almeno due battute" in p for p in problems)
