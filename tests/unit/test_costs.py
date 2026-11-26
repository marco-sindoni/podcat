from datetime import date
from pathlib import Path

import pytest

from podcat.tracking import frontmatter
from podcat.tracking.costs import BudgetExceeded, Ledger, load_prices

DAY = date(2026, 11, 27)


@pytest.fixture
def ledger(repo: Path) -> Ledger:
    return Ledger(repo / "tracking", load_prices(repo / "config"))


def test_empty_month(ledger: Ledger):
    assert ledger.total(DAY) == 0.0
    assert ledger.cap(DAY) == 50.0


def test_record_adds_entry_and_total(ledger: Ledger):
    usd = ledger.record(DAY, "news", "triage", "claude-haiku-5-5", 40_000, 6_000)
    assert usd == pytest.approx(0.007)
    assert ledger.total(DAY) == pytest.approx(0.007)
    doc = frontmatter.read(ledger.path(DAY))
    assert doc.meta["entries"][0]["step"] == "triage"
    assert "| 2026-11-27 | news | triage |" in doc.body


def test_check_refuses_over_cap(ledger: Ledger):
    ledger.record(DAY, "news", "triage", "claude-haiku-5-5", 40_000, 6_000)
    path = ledger.path(DAY)
    doc = frontmatter.read(path)
    doc.meta["cap_usd"] = 0.0071
    frontmatter.write(path, doc)
    with pytest.raises(BudgetExceeded):
        ledger.check(DAY, 0.001)
    ledger.check(DAY, 0.0)  # nothing more to pay is fine


def test_worst_case_counts_max_tokens(ledger: Ledger):
    estimate = ledger.worst_case("claude-haiku-5-5", "x" * 3000, 1000)
    assert estimate == pytest.approx((1001 * 0.10 + 1000 * 0.50) / 1_000_000)


def test_new_month_has_its_own_file(ledger: Ledger):
    ledger.record(DAY, "news", "triage", "claude-haiku-5-5", 1000, 100)
    december = date(2026, 12, 1)
    assert ledger.total(december) == 0.0
    assert ledger.path(december).name == "2026-12.md"


def test_unknown_model(ledger: Ledger):
    with pytest.raises(KeyError):
        ledger.worst_case("unknown-model", "x", 10)
