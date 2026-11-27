"""Command line entry point: `podcat` (contracts/cli.md)."""

from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path
from typing import Optional

import typer
import yaml

from podcat.settings import Settings, load_settings, today_rome
from podcat.tracking import frontmatter
from podcat.tracking.costs import BudgetExceeded, Ledger, load_prices

EXIT_USER_ERROR = 1
EXIT_BUDGET = 2
EXIT_NO_DATA = 3
EXIT_SCRIPT_CHECKS = 4

app = typer.Typer(help="Podcat: preparazione delle puntate.", no_args_is_help=True)
sources_app = typer.Typer(help="Fonti delle notizie.", no_args_is_help=True)
news_app = typer.Typer(help="Raccolta e scelta delle notizie.", no_args_is_help=True)
costs_app = typer.Typer(help="Costi e tetto mensile.", no_args_is_help=True)
script_app = typer.Typer(help="Copioni dei quattro gatti.", no_args_is_help=True)
app.add_typer(sources_app, name="sources")
app.add_typer(news_app, name="news")
app.add_typer(costs_app, name="costs")
app.add_typer(script_app, name="script")

DateOpt = typer.Option(None, "--date", help="Data AAAA-MM-GG (predefinita: oggi, ora italiana).")
KindOpt = typer.Option("daily", "--kind", help="daily oppure weekly.")


def _fail(message: str, code: int = EXIT_USER_ERROR) -> None:
    typer.echo(message, err=True)
    raise typer.Exit(code)


def _day(value: Optional[str]) -> date:
    if not value:
        return today_rome()
    try:
        return date.fromisoformat(value)
    except ValueError:
        _fail(f"Data non valida: {value!r}. Usa il formato AAAA-MM-GG.")


def _kind(value: str) -> str:
    if value not in ("daily", "weekly"):
        _fail("--kind deve essere daily oppure weekly.")
    return value


def news_model_factory(settings: Settings):
    from podcat.llm.anthropic_model import AnthropicModel

    pricing = yaml.safe_load((settings.config_dir / "pricing.yaml").read_text(encoding="utf-8"))
    model_id = pricing["news_model"]

    def factory(ledger: Ledger, day: date):
        return AnthropicModel(model_id, ledger, day, "news", api_key=settings.anthropic_api_key)

    return factory


# sources ----------------------------------------------------------------------


@sources_app.command("check")
def sources_check(write: bool = typer.Option(False, "--write", help="Aggiorna config/sources.yaml.")) -> None:
    """Controlla i feed di tutte le fonti e cerca quelli mancanti."""
    from podcat.news.sources import apply_check, check_sources, load_sources, save_sources

    settings = load_settings()
    sources = load_sources(settings.config_dir)
    results = asyncio.run(check_sources(sources))
    labels = {"ok": "ok", "discovered": "trovato", "manual": "solo a mano"}
    for r in results:
        feed = r.working[0] if r.working else "-"
        typer.echo(f"{labels[r.status]:<12} {r.source.id:<22} {feed}")
    counts = {k: sum(1 for r in results if r.status == k) for k in labels}
    typer.echo(f"\nFunzionanti {counts['ok']}, trovati {counts['discovered']}, solo a mano {counts['manual']}.")
    if write:
        save_sources(settings.config_dir, apply_check(results, today_rome().isoformat()))
        typer.echo("config/sources.yaml aggiornato.")


# news -------------------------------------------------------------------------


def _store(settings: Settings):
    from podcat.news.store import NewsStore

    return NewsStore(settings.tracking_dir, settings.cache_dir)


def _print_shortlist(path) -> None:
    from pathlib import Path

    doc = frontmatter.read(Path(path))
    typer.echo(doc.body.replace(frontmatter.GENERATED_START, "").replace(frontmatter.GENERATED_END, "").strip())


@news_app.command("gather")
def news_gather(
    date_: Optional[str] = DateOpt,
    refresh: bool = typer.Option(False, "--refresh", help="Rifà la lista (ripaga i passi a pagamento)."),
) -> None:
    """Giro del giorno: raccoglie, verifica e propone 3-5 notizie."""
    from podcat.news.pipeline import gather
    from podcat.news.shortlist import ShortlistError

    settings = load_settings()
    day = _day(date_)
    try:
        result = gather(settings, day, news_model_factory(settings), refresh=refresh)
    except BudgetExceeded as exc:
        _fail(str(exc), EXIT_BUDGET)
    except ShortlistError as exc:
        _fail(str(exc))
    _print_shortlist(result.path)
    status = "Lista creata" if result.created else "Lista già pronta, nessun costo"
    typer.echo(f"\n{status}: {result.path}")
    if not result.meta.get("candidates"):
        raise typer.Exit(EXIT_NO_DATA)


@news_app.command("weekly")
def news_weekly(
    date_: Optional[str] = DateOpt,
    refresh: bool = typer.Option(False, "--refresh", help="Rifà la lista (ripaga il passo a pagamento)."),
) -> None:
    """Lista del sabato per la puntata settimanale."""
    from podcat.news.shortlist import ShortlistError
    from podcat.news.weekly import weekly

    settings = load_settings()
    day = _day(date_)
    try:
        result = weekly(settings, day, news_model_factory(settings), refresh=refresh)
    except BudgetExceeded as exc:
        _fail(str(exc), EXIT_BUDGET)
    except ShortlistError as exc:
        _fail(str(exc))
    _print_shortlist(result.path)
    status = "Lista creata" if result.created else "Lista già pronta, nessun costo"
    typer.echo(f"\n{status}: {result.path}")
    if not result.meta.get("candidates"):
        raise typer.Exit(EXIT_NO_DATA)


@news_app.command("show")
def news_show(date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Mostra la lista."""
    settings = load_settings()
    store = _store(settings)
    path = store.shortlist_path(_day(date_), _kind(kind))
    if not path.exists():
        _fail("Nessuna lista per questa data.", EXIT_NO_DATA)
    _print_shortlist(path)


@news_app.command("pick")
def news_pick(number: int, date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Sceglie la notizia numero N."""
    from podcat.news.shortlist import ShortlistError, pick

    settings = load_settings()
    store = _store(settings)
    try:
        sid = pick(store, _day(date_), _kind(kind), number)
    except ShortlistError as exc:
        _fail(str(exc))
    typer.echo(f"Scelta la notizia {number}: {store.read_story(sid)['title']}")


@news_app.command("unpick")
def news_unpick(date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Annulla la scelta, se il copione non esiste ancora."""
    from podcat.news.shortlist import ShortlistError, unpick

    settings = load_settings()
    try:
        unpick(_store(settings), _day(date_), _kind(kind))
    except ShortlistError as exc:
        _fail(str(exc))
    typer.echo("Scelta annullata.")


@news_app.command("reject")
def news_reject(date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Scarta tutte le candidate; il prossimo giro con --refresh le esclude."""
    from podcat.news.shortlist import ShortlistError, reject

    settings = load_settings()
    try:
        ids = reject(_store(settings), _day(date_), _kind(kind))
    except ShortlistError as exc:
        _fail(str(exc))
    typer.echo(f"Scartate {len(ids)} notizie. Per una nuova lista: podcat news gather --refresh")


@news_app.command("link-doc")
def news_link_doc(url: str, date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Collega il documento da commentare alla lista."""
    from podcat.news.shortlist import ShortlistError, link_doc

    settings = load_settings()
    try:
        link_doc(_store(settings), _day(date_), _kind(kind), url)
    except ShortlistError as exc:
        _fail(str(exc))
    typer.echo("Documento collegato.")


# costs ------------------------------------------------------------------------


def _parse_month(month: Optional[str]) -> date:
    if not month:
        return today_rome()
    try:
        year, mon = month.split("-")
        return date(int(year), int(mon), 1)
    except ValueError:
        _fail(f"Mese non valido: {month!r}. Usa il formato AAAA-MM.")


@costs_app.command("show")
def costs_show(month: Optional[str] = typer.Option(None, help="Mese, formato AAAA-MM.")) -> None:
    """Mostra quanto si è speso nel mese e quanto resta."""
    settings = load_settings()
    ledger = Ledger(settings.tracking_dir, load_prices(settings.config_dir))
    day = _parse_month(month)
    total, cap = ledger.total(day), ledger.cap(day)
    typer.echo(f"{day:%Y-%m}: spesi {total:.4f} USD su {cap:.2f} USD, restano {cap - total:.4f} USD.")


# script (spec 002) -----------------------------------------------------------

SCRIPT_STEP_KEY = {"room": "room", "head-writer": "head_writer", "fix": "head_writer", "revision": "revision"}


def script_model_factory(settings: Settings):
    """Model per step from `script_models` in config/pricing.yaml (one line to change a model)."""
    from podcat.llm.anthropic_model import AnthropicModel

    pricing = yaml.safe_load((settings.config_dir / "pricing.yaml").read_text(encoding="utf-8"))
    models = pricing["script_models"]
    efforts = pricing.get("script_effort", {})

    def factory(ledger: Ledger, day: date, step: str):
        key = SCRIPT_STEP_KEY[step]
        return AnthropicModel(models[key], ledger, day, "script", api_key=settings.anthropic_api_key,
                              effort=efforts.get(key)).for_step(step)

    return factory


def _script_errors(func):
    from functools import wraps

    from podcat.scripts.store import ScriptError

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ScriptError as exc:
            _fail(str(exc))
        except BudgetExceeded as exc:
            _fail(str(exc), EXIT_BUDGET)

    return wrapper


@script_app.command("write")
@_script_errors
def script_write(
    date_: Optional[str] = DateOpt,
    kind: str = KindOpt,
    new_draft: bool = typer.Option(False, "--new-draft", help="Riscrive il copione da capo, come nuova versione."),
) -> None:
    """Scrive il copione della notizia scelta (stanza degli autori + capo autore)."""
    from podcat.scripts.pipeline import write

    settings = load_settings()
    result = write(settings, _day(date_), _kind(kind), script_model_factory(settings), new_draft=new_draft)
    if not result.created:
        typer.echo("Il copione esiste già: nessuna nuova spesa.")
    else:
        typer.echo(f"Copione scritto, costo {result.cost_usd:.4f} USD.")
    typer.echo(str(result.path))
    if result.problems:
        typer.echo("Il copione non passa i controlli:", err=True)
        for p in result.problems:
            typer.echo(f"- {p}", err=True)
        raise typer.Exit(EXIT_SCRIPT_CHECKS)


@script_app.command("show")
@_script_errors
def script_show(
    date_: Optional[str] = DateOpt,
    kind: str = KindOpt,
    version: Optional[int] = typer.Option(None, "--version", help="Versione da mostrare (predefinita: l'ultima)."),
) -> None:
    """Mostra il testo del documento del copione."""
    from podcat.scripts.pipeline import show

    typer.echo(show(load_settings(), _day(date_), _kind(kind), version))


@script_app.command("list")
def script_list(last: int = typer.Option(10, "--last", help="Quanti copioni mostrare.")) -> None:
    """Elenca gli ultimi copioni."""
    from podcat.scripts.pipeline import listing

    items = listing(load_settings(), last)
    if not items:
        typer.echo("Nessun copione.")
        return
    for m in items:
        typer.echo(
            f"{m['date']} {m['kind']:<6} {m['status']:<9} modo {m.get('news_image_mode')} "
            f"{m.get('tone', ''):<8} v{m.get('current_version')} {float(m.get('cost_usd') or 0):.4f} USD  {m['id']}"
        )


def _script_out(result, done: str) -> None:
    if not result.created:
        typer.echo("Niente da fare: nessuna modifica e nessuna spesa.")
    else:
        typer.echo(f"{done} Costo {result.cost_usd:.4f} USD.")
    typer.echo(str(result.path))
    if result.problems:
        typer.echo("Il copione non passa i controlli:", err=True)
        for p in result.problems:
            typer.echo(f"- {p}", err=True)
        raise typer.Exit(EXIT_SCRIPT_CHECKS)


@script_app.command("link-doc")
@_script_errors
def script_link_doc(url: str, date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Salva il link del documento commentabile (il copione passa in revisione)."""
    from podcat.scripts.pipeline import link_doc

    meta = link_doc(load_settings(), _day(date_), _kind(kind), url)
    typer.echo(f"Link salvato, stato: {meta['status']}.")


@script_app.command("revise")
@_script_errors
def script_revise(
    comments: Path = typer.Option(..., "--comments", help="File YAML con i commenti di Marco."),
    tone: Optional[str] = typer.Option(None, "--tone", help="comico oppure pungente."),
    date_: Optional[str] = DateOpt,
    kind: str = KindOpt,
) -> None:
    """Applica i commenti di Marco come nuova versione."""
    from podcat.scripts.pipeline import revise

    if tone not in (None, "comico", "pungente"):
        _fail("--tone deve essere comico oppure pungente.")
    settings = load_settings()
    result = revise(settings, _day(date_), _kind(kind), comments.read_text(encoding="utf-8"),
                    script_model_factory(settings), tone=tone)
    _script_out(result, "Nuova versione scritta.")


@script_app.command("ending")
@_script_errors
def script_ending(number: int, date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Mette il finale alternativo N (1 o 2), senza costi."""
    from podcat.scripts.pipeline import ending

    _script_out(ending(load_settings(), _day(date_), _kind(kind), number), f"Finale {number} messo.")


@script_app.command("edit-line")
@_script_errors
def script_edit_line(number: int, text: str, date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Registra una correzione a mano di Marco sulla battuta N."""
    from podcat.scripts.pipeline import edit_line

    _script_out(edit_line(load_settings(), _day(date_), _kind(kind), number, text), f"Battuta {number} aggiornata.")


@script_app.command("approve")
@_script_errors
def script_approve(date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Approva il copione: la versione attuale viene bloccata."""
    from podcat.scripts.pipeline import approve

    meta = approve(load_settings(), _day(date_), _kind(kind))
    typer.echo(f"Copione approvato (versione {meta['approved_version']}).")


@script_app.command("reopen")
@_script_errors
def script_reopen(date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Riapre un copione approvato."""
    from podcat.scripts.pipeline import reopen

    meta = reopen(load_settings(), _day(date_), _kind(kind))
    typer.echo(f"Stato: {meta['status']}.")


@script_app.command("discard")
@_script_errors
def script_discard(date_: Optional[str] = DateOpt, kind: str = KindOpt) -> None:
    """Scarta il copione; la notizia torna tra le candidate."""
    from podcat.scripts.pipeline import discard

    discard(load_settings(), _day(date_), _kind(kind))
    typer.echo("Copione scartato.")


if __name__ == "__main__":  # pragma: no cover
    app()
