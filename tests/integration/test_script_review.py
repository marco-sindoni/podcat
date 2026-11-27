import pytest

from fakes import FakeModel
from podcat.news.shortlist import ShortlistError, pick
from podcat.news.store import NewsStore
from podcat.scripts import pipeline
from podcat.scripts.store import ScriptError, ScriptStore
from scriptfixtures import FRIDAY, FRIDGE, STRIKE, factory_for, fake, head_result, pick_story, setup_repo

D = "daily"


@pytest.fixture
def env(repo):
    s = setup_repo(repo)
    pick_story(s, FRIDGE, extra=[STRIKE])
    pipeline.write(s, FRIDAY, D, factory_for(fake()))
    pipeline.link_doc(s, FRIDAY, D, "https://claude.ai/artifact/abc")
    return s


def revision_model(changes, answers=None, **extra):
    data = {"changes": changes, "answers": answers or [{"comment": "c", "answer": "fatto"}], **extra}
    return FakeModel({"RevisionResult": data, "FixResult": head_result()})


def current(s):
    store = ScriptStore(s.tracking_dir)
    meta = store.all()[0]
    return meta, store.read_version(meta["id"])


COMMENTS = "- line: 2\n  text: più cattiva\n- line: 5\n  text: questa non fa ridere\n"


def test_revision_changes_only_commented_lines(env):
    model = revision_model([
        {"n": 2, "cat": "fuzz", "text": "No, no, no, fermi tutti! Oggi il frigo, domani il tostapane, poi ci rubano la lavatrice!"},
        {"n": 5, "cat": "fuzz", "text": "Un salame con il ponte sullo Stretto già incorporato!"},
    ])
    before = current(env)[1]
    result = pipeline.revise(env, FRIDAY, D, COMMENTS, factory_for(model))
    assert result.created and result.problems == []
    meta, after = current(env)
    assert meta["current_version"] == 2 and meta["status"] == "review"
    changed = [a.n for a, b in zip(after.lines, before.lines) if a.text != b.text]
    assert changed == [2, 5]
    assert after.answers[0].answer == "fatto"
    # same comments again: nothing happens, nothing is paid
    again = pipeline.revise(env, FRIDAY, D, COMMENTS, factory_for(model))
    assert not again.created and len(model.calls) == 1


def test_manual_edit_is_kept(env):
    pipeline.edit_line(env, FRIDAY, D, 3, "Nel novantaquattro il frigo faceva il freddo e basta, senza opinioni politiche.")
    model = revision_model([{"n": 3, "cat": "vinile", "text": "altro testo"}])
    pipeline.revise(env, FRIDAY, D, "- text: nel complesso ok\n", factory_for(model))
    _, v = current(env)
    assert v.lines[2].manual and "senza opinioni politiche" in v.lines[2].text
    assert any("è tua" in a.answer for a in v.answers)


def test_ending_swap_is_free_and_reversible(env):
    _, before = current(env)
    pipeline.ending(env, FRIDAY, D, 2)
    meta, v = current(env)
    assert v.lines[-2].text == before.endings[1].feedback and v.lines[-1].text == before.endings[1].flanella
    assert v.endings[1].feedback == before.lines[-2].text
    assert meta["versions"][-1]["cause"] == "ending" and meta["versions"][-1]["cost_usd"] == 0
    with pytest.raises(ScriptError):
        pipeline.ending(env, FRIDAY, D, 3)


def test_new_draft(env):
    model = fake()
    pipeline.write(env, FRIDAY, D, factory_for(model), new_draft=True)
    meta, v = current(env)
    assert meta["current_version"] == 2 and meta["versions"][-1]["cause"] == "new-draft"


def test_approve_locks_and_reopen(env):
    meta = pipeline.approve(env, FRIDAY, D)
    assert meta["status"] == "approved" and meta["approved_version"] == 1
    news = NewsStore(env.tracking_dir, env.cache_dir)
    story = news.read_story(FRIDGE["id"])
    assert story["status"] == "used" and story["episode"] == meta["id"]
    with pytest.raises(ScriptError):
        pipeline.revise(env, FRIDAY, D, COMMENTS, factory_for(revision_model([])))
    with pytest.raises(ShortlistError):
        pick(news, FRIDAY, D, 2)
    pipeline.reopen(env, FRIDAY, D)
    assert current(env)[0]["status"] == "review"
    assert news.read_story(FRIDGE["id"])["status"] == "chosen"


def test_pick_change_discards_open_script(env):
    news = NewsStore(env.tracking_dir, env.cache_dir)
    pick(news, FRIDAY, D, 2)
    meta = ScriptStore(env.tracking_dir).all()[0]
    assert meta["status"] == "discarded"
    old = news.read_story(FRIDGE["id"])
    assert old["status"] == "candidate" and old.get("script") is None
    assert news.read_story(STRIKE["id"])["status"] == "chosen"


def test_approve_refused_with_problems(env):
    pipeline.edit_line(env, FRIDAY, D, 2, "Boh.")
    result = pipeline.edit_line(env, FRIDAY, D, 3, "Mah.")  # far below 70 words
    assert result.problems and current(env)[0]["problems"]
    with pytest.raises(ScriptError):
        pipeline.approve(env, FRIDAY, D)


def test_tone_change_on_revise(env):
    model = revision_model([{"n": 6, "cat": "feedback", "text": "Mmh. Se il frigo si scalda, almeno uno in Italia ha la febbre."}])
    pipeline.revise(env, FRIDAY, D, "- text: più pungente\n", factory_for(model), tone="pungente")
    assert current(env)[0]["tone"] == "pungente"
    assert "Registro: PUNGENTE" in model.calls[0][1]


def test_mode_change_to_previous_mode_goes_through_fix(repo):
    s = setup_repo(repo)
    pick_story(s, FRIDGE)
    pipeline.write(s, FRIDAY, D, factory_for(fake()))  # mode B
    pipeline.approve(s, FRIDAY, D)
    nxt = FRIDAY.replace(day=28)
    pick_story(s, {**STRIKE, "id": "2026-11-28-sciopero", "status": "chosen"}, day=nxt)
    tv = head_result(news_image={"mode": "A", "scene": 3, "comment_line": 4, "held_by": None, "subject": "x"})
    tv["scenes"][2]["shot"] = "news-tv"
    tv["scenes"][2]["lines"] = []
    pipeline.write(s, nxt, D, factory_for(fake(head=tv)))
    bad = {"mode": "B", "scene": 3, "comment_line": 4, "held_by": None, "subject": "x"}
    scenes = [dict(x) for x in tv["scenes"]]
    scenes[2] = {**scenes[2], "shot": "news-cutin"}
    model = FakeModel({"RevisionResult": {"changes": [], "answers": [{"comment": "modo B", "answer": "ok"}],
                                          "news_image": bad, "scenes": scenes},
                       "FixResult": tv})
    pipeline.revise(s, nxt, D, "- text: metti l'immagine a tutto schermo\n", factory_for(model))
    assert [c[0] for c in model.calls] == ["RevisionResult", "FixResult"]
    assert "uguale al video precedente" in model.calls[1][1]
    meta = ScriptStore(s.tracking_dir).find("2026-11-28-sciopero", D)
    assert meta["news_image_mode"] == "A"
