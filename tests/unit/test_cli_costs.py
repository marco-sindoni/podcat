from typer.testing import CliRunner

from podcat.cli import app


def test_costs_show_empty_month(repo):
    result = CliRunner().invoke(app, ["costs", "show", "--month", "2026-11"])
    assert result.exit_code == 0
    assert "spesi 0.0000 USD su 50.00 USD" in result.output


def test_costs_show_bad_month(repo):
    result = CliRunner().invoke(app, ["costs", "show", "--month", "novembre"])
    assert result.exit_code == 1
