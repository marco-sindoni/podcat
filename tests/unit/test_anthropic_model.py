from datetime import date
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from podcat.llm.anthropic_model import AnthropicModel
from podcat.llm.base import ModelRefused
from podcat.tracking.costs import BudgetExceeded, Ledger, load_prices

DAY = date(2026, 11, 27)


class Answer(BaseModel):
    ok: bool


class FakeMessages:
    def __init__(self, stop_reason="end_turn"):
        self.stop_reason = stop_reason
        self.calls = 0

    def parse(self, **kwargs):
        self.calls += 1
        assert kwargs["output_format"] is Answer
        return SimpleNamespace(
            stop_reason=self.stop_reason,
            usage=SimpleNamespace(input_tokens=1000, output_tokens=100),
            parsed_output=Answer(ok=True),
        )


def make(repo, stop_reason="end_turn"):
    ledger = Ledger(repo / "tracking", load_prices(repo / "config"))
    messages = FakeMessages(stop_reason)
    client = SimpleNamespace(messages=messages)
    model = AnthropicModel("claude-haiku-5-5", ledger, DAY, "news", client=client)
    return model, ledger, messages


def test_parse_records_cost(repo):
    model, ledger, _ = make(repo)
    answer, usage = model.for_step("triage").parse("sys", "user", Answer, 500)
    assert answer.ok and usage.input_tokens == 1000
    assert ledger.total(DAY) == pytest.approx(0.00015)


def test_refuses_before_calling_when_over_cap(repo):
    model, ledger, messages = make(repo)
    ledger.record(DAY, "news", "x", "claude-haiku-5-5", 0, 0)
    from podcat.tracking import frontmatter

    doc = frontmatter.read(ledger.path(DAY))
    doc.meta["cap_usd"] = 0.0
    frontmatter.write(ledger.path(DAY), doc)
    with pytest.raises(BudgetExceeded):
        model.parse("sys", "user", Answer, 500)
    assert messages.calls == 0


def test_refusal_is_recorded_and_raised(repo):
    model, ledger, _ = make(repo, stop_reason="refusal")
    with pytest.raises(ModelRefused):
        model.parse("sys", "user", Answer, 500)
    assert ledger.total(DAY) > 0
