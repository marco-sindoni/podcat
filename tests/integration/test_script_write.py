import pytest
from typer.testing import CliRunner

from podcat import cli
from podcat.news.store import NewsStore
from podcat.scripts.pipeline import show, write
from podcat.scripts.store import ScriptError, ScriptStore
from podcat.tracking.costs import BudgetExceeded
from scriptfixtures import FRIDAY, FRIDGE, LIBRARY, STRIKE, THURSDAY, factory_for, fake, head_result, pick_story, setup_repo


@pytest.fixture
def settings(repo):
    s = setup_repo(repo)
    pick_story(s, FRIDGE)
    return s


def test_write_creates_checked_script(settings):
    model = fake()
    result = write(settings, FRIDAY, "daily", factory_for(model))
    assert result.created and result.problems == []
    assert [c[0] for c in model.calls] == ["RoomResult", "HeadWriterResult"]
    store = ScriptStore(settings.tracking_dir)
    meta = store.read(result.script_id)
    assert meta["status"] == "draft" and meta["news_image_mode"] == "B" and meta["tone"] == "comico"
    v = store.read_version(result.script_id)
    assert 70 <= v.words <= 90 and all(s.duration_s for s in v.scenes)
    news = NewsStore(settings.tracking_dir, settings.cache_dir)
    assert news.read_story(FRIDGE["id"])["script"] == result.script_id
    text = show(settings, FRIDAY, "daily")
    assert "**Flanella**" in text and "Finale 2" in text and "stacco a tutto schermo" in text


def test_rerun_is_free_and_unchanged(settings):
    model = fake()
    first = write(settings, FRIDAY, "daily", factory_for(model))
    before = first.path.read_text()
    again = write(settings, FRIDAY, "daily", factory_for(model))
    assert not again.created and len(model.calls) == 2 and first.path.read_text() == before


def test_failed_check_gets_one_fix(settings):
    bad = head_result()
    bad["lines"][0]["cat"] = "fuzz"
    model = fake(head=bad, fix=head_result())
    result = write(settings, FRIDAY, "daily", factory_for(model))
    assert result.problems == []
    assert [c[0] for c in model.calls] == ["RoomResult", "HeadWriterResult", "FixResult"]
    assert "prima battuta deve essere di Flanella" in model.calls[2][1]


def test_failed_fix_saves_draft_with_problems_and_exit_4(settings, monkeypatch):
    bad = head_result()
    bad["lines"][0]["cat"] = "fuzz"
    model = fake(head=bad, fix=bad)
    monkeypatch.setattr(cli, "script_model_factory", lambda s: factory_for(model))
    out = CliRunner().invoke(cli.app, ["script", "write", "--date", "2026-11-27"])
    assert out.exit_code == 4
    meta = ScriptStore(settings.tracking_dir).all()[0]
    assert meta["status"] == "draft" and meta["problems"]


def test_budget_cap_writes_nothing(settings):
    def broke(ledger, day, step):
        raise BudgetExceeded("tetto")
    with pytest.raises(BudgetExceeded):
        write(settings, FRIDAY, "daily", broke)
    assert ScriptStore(settings.tracking_dir).all() == []


def test_no_pick_is_a_user_error(repo):
    s = setup_repo(repo)
    with pytest.raises(ScriptError):
        write(s, FRIDAY, "daily", factory_for(fake()))


def test_rotation_avoids_previous_mode(settings):
    write(settings, FRIDAY, "daily", factory_for(fake()))
    pick_story(settings, {**STRIKE, "id": "2026-11-28-sciopero", "status": "chosen"}, day=FRIDAY.replace(day=28))
    model = fake()
    result = write(settings, FRIDAY.replace(day=28), "daily", factory_for(model))
    assert "modo B" not in model.calls[0][1].split("Immagine della notizia: usa")[1].split("\n")[0]
    assert any("uguale al video precedente" in p for p in model.calls[2][1].splitlines()) or result.problems


def test_pungente_and_politics_in_prompt(repo):
    s = setup_repo(repo)
    pick_story(s, {**STRIKE, "status": "chosen"})
    model = fake()
    write(s, FRIDAY, "daily", factory_for(model))
    prompt = model.calls[0][1]
    assert "Registro: PUNGENTE" in prompt and "mai di parte" in prompt


def test_thursday_prompt(repo):
    s = setup_repo(repo)
    pick_story(s, LIBRARY, day=THURSDAY, thursday=True)
    model = fake()
    write(s, THURSDAY, "daily", factory_for(model))
    assert "Giovedì buone notizie" in model.calls[0][1] and "sting-gnocchi" in model.calls[0][1]
