"""Command line entry point: `podcat` (contracts/cli.md)."""

from __future__ import annotations

from datetime import date
from typing import Optional

import typer

from podcat.settings import load_settings, today_rome
from podcat.tracking.costs import Ledger, load_prices

EXIT_USER_ERROR = 1
EXIT_BUDGET = 2
EXIT_NO_DATA = 3

app = typer.Typer(help="Podcat: preparazione delle puntate.", no_args_is_help=True)
sources_app = typer.Typer(help="Fonti delle notizie.", no_args_is_help=True)
news_app = typer.Typer(help="Raccolta e scelta delle notizie.", no_args_is_help=True)
costs_app = typer.Typer(help="Costi e tetto mensile.", no_args_is_help=True)
app.add_typer(sources_app, name="sources")
app.add_typer(news_app, name="news")
app.add_typer(costs_app, name="costs")


def _parse_month(month: Optional[str]) -> date:
    if not month:
        return today_rome()
    try:
        year, mon = month.split("-")
        return date(int(year), int(mon), 1)
    except ValueError:
        typer.echo(f"Mese non valido: {month!r}. Usa il formato AAAA-MM.", err=True)
        raise typer.Exit(EXIT_USER_ERROR)


@costs_app.command("show")
def costs_show(month: Optional[str] = typer.Option(None, help="Mese, formato AAAA-MM.")) -> None:
    """Mostra quanto si è speso nel mese e quanto resta."""
    settings = load_settings()
    ledger = Ledger(settings.tracking_dir, load_prices(settings.config_dir))
    day = _parse_month(month)
    total, cap = ledger.total(day), ledger.cap(day)
    typer.echo(f"{day:%Y-%m}: spesi {total:.4f} USD su {cap:.2f} USD, restano {cap - total:.4f} USD.")


if __name__ == "__main__":  # pragma: no cover
    app()
