from datetime import date

from typer.testing import CliRunner

import podcat.cli as cli
import podcat.news.pipeline as pipeline
from newsfixtures import FRIDAY_7AM, fake_model, mock_client
from podcat.llm.anthropic_model import AnthropicModel
from podcat.tracking import frontmatter


class FakeAnthropicClient:
    """Stands in for the SDK client; returns the scripted fake answers."""

    def __init__(self):
        self.fake = fake_model()
        self.messages = self

    def parse(self, model, max_tokens, system, messages, output_format):
        from types import SimpleNamespace

        parsed, usage = self.fake.parse(system, messages[0]["content"], output_format, max_tokens)
        return SimpleNamespace(
            stop_reason="end_turn", parsed_output=parsed,
            usage=SimpleNamespace(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
        )


def patch(monkeypatch, repo):
    client = FakeAnthropicClient()

    def factory(settings):
        return lambda ledger, day: AnthropicModel("claude-haiku-5-5", ledger, day, "news", client=client)

    monkeypatch.setattr(cli, "news_model_factory", factory)
    original = pipeline.gather

    def gather(settings, day, model_factory, refresh=False, now=None, http_client=None):
        return original(settings, day, model_factory, refresh=refresh, now=FRIDAY_7AM,
                        http_client=mock_client(settings.config_dir))

    monkeypatch.setattr(pipeline, "gather", gather)


def test_gather_pick_and_costs(repo, monkeypatch):
    patch(monkeypatch, repo)
    runner = CliRunner()
    result = runner.invoke(cli.app, ["news", "gather", "--date", "2026-11-27"])
    assert result.exit_code == 0, result.output
    assert "Lista creata" in result.output and "Sciopero dei treni" in result.output
    again = runner.invoke(cli.app, ["news", "gather", "--date", "2026-11-27"])
    assert "Lista già pronta, nessun costo" in again.output
    ledger = frontmatter.read(repo / "tracking/costs/2026-11.md").meta
    assert len(ledger["entries"]) == 2  # triage + editorial, only once
    picked = runner.invoke(cli.app, ["news", "pick", "2", "--date", "2026-11-27"])
    assert picked.exit_code == 0 and "Sinner" in picked.output
    shown = runner.invoke(cli.app, ["news", "show", "--date", "2026-11-27"])
    assert "✅" in shown.output


def test_budget_cap_stops_with_exit_code_2(repo, monkeypatch):
    patch(monkeypatch, repo)
    path = repo / "tracking/costs/2026-11.md"
    frontmatter.write(path, frontmatter.Document(meta={"month": "2026-11", "cap_usd": 0.0, "total_usd": 0.0, "entries": []}))
    result = CliRunner().invoke(cli.app, ["news", "gather", "--date", "2026-11-27"])
    assert result.exit_code == 2
    assert frontmatter.read(path).meta["entries"] == []
    assert not (repo / "tracking/news/shortlists/2026-11-27-daily.md").exists()


def test_show_missing_list(repo):
    result = CliRunner().invoke(cli.app, ["news", "show", "--date", "2026-01-01"])
    assert result.exit_code == 3
