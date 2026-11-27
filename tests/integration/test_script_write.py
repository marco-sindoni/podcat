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
    assert 110 <= v.words <= 135 and all(s.duration_s for s in v.scenes)
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


def weekly_result():
    lines = [
        (1, "flanella", "Allora, gattini, la notizia della settimana: hacker sloveni hanno fatto impazzire i frigoriferi di un salumificio."),
        (2, "fuzz", "No, no, no, fermi tutti! Lo sapevo: prima i frigoriferi, poi i tostapane, poi ci rubano anche la lavatrice!"),
        (3, "vinile", "Ai miei tempi il frigorifero faceva una cosa sola: il freddo. E la faceva benissimo, senza internet."),
        (4, "feedback", "Mmh. E se il frigo avesse solo voluto un po' di caldo, come tutti noi d'inverno?"),
        (5, "flanella", "E sullo schermo, invece della temperatura, è comparsa la foto di un vicepremier sorridente."),
        (6, "fuzz", "Questo è uno scandalo! Un salame con il ponte sullo Stretto incorporato! Le mortadelle protestano in piazza!"),
        (7, "vinile", "Nel novantaquattro gli hacker al massimo ti cambiavano la suoneria del cercapersone. Che tempi, che classe."),
        (8, "flanella", "Vinile, il cercapersone lo avevi solo tu, e nessuno ti chiamava mai."),
        (9, "fuzz", "Io da stasera dormo con il frigo staccato e il formaggio sotto il cuscino, per sicurezza nazionale."),
        (10, "vinile", "Il formaggio sotto il cuscino è una vecchia tradizione di famiglia, ragazzo. Funziona anche contro i vampiri."),
        (11, "flanella", "Ricapitoliamo: frigoriferi caldi, salumi sudati, un vicepremier in cella frigorifera e Fuzz con il formaggio a letto."),
        (12, "fuzz", "E quando i salami chiederanno il voto, non dite che non vi avevo avvertiti!"),
        (13, "feedback", "Mmh. Forse il vero virus è che vogliamo tutto connesso, anche il prosciutto. Il prosciutto non ha mai chiesto il wifi."),
        (14, "flanella", "Spegnete il frigo prima di uscire, e magari anche il telefono. Ci vediamo domenica prossima, gattini."),
    ]
    h = head_result()
    pad = " E questo, credetemi, non è affatto normale."
    h["lines"] = [{"n": n, "cat": c, "text": t + (pad if 2 <= n <= 12 else "")} for n, c, t in lines]
    h["scenes"] = [{"n": i, "shot": "wide", "lines": [i], "reactions": []} for i in range(1, 15)]
    h["scenes"].insert(4, {"n": 0, "shot": "news-cutin", "lines": [], "reactions": []})
    for i, sc in enumerate(h["scenes"], 1):
        sc["n"] = i
    h["news_image"] = {"mode": "B", "scene": 5, "comment_line": 5, "held_by": None, "subject": "frigoriferi fumanti"}
    return h


def test_weekly_script(repo):
    s = setup_repo(repo)
    pick_story(s, {**FRIDGE, "status": "used"}, day=FRIDAY.replace(day=28), kind="weekly")
    model = fake(head=weekly_result())
    result = write(s, FRIDAY.replace(day=28), "weekly", factory_for(model))
    assert "Puntata settimanale" in model.calls[0][1]
    v = ScriptStore(s.tracking_dir).read_version(result.script_id)
    assert result.problems == [], result.problems
    assert 280 <= v.words <= 320
