"""Monthly cost ledger with the budget cap (constitution V).

The ledger lives in `tracking/costs/<YYYY-MM>.md`. Its front matter holds the cap, the
running total and one entry per paid call; the body shows the same entries as a table.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from podcat.tracking import frontmatter

DEFAULT_CAP_USD = 50.0
CHARS_PER_TOKEN = 3.0  # conservative estimate for Italian text


class BudgetExceeded(RuntimeError):
    """Raised before a paid call that would push the month over its cap."""


@dataclass(frozen=True)
class Price:
    input_per_mtok: float
    output_per_mtok: float

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.input_per_mtok + output_tokens * self.output_per_mtok) / 1_000_000


def load_prices(config_dir: Path) -> dict[str, Price]:
    data = yaml.safe_load((config_dir / "pricing.yaml").read_text(encoding="utf-8"))
    return {model: Price(p["input"], p["output"]) for model, p in data["models"].items()}


def estimate_input_tokens(text: str) -> int:
    return int(len(text) / CHARS_PER_TOKEN) + 1


class Ledger:
    def __init__(self, tracking_dir: Path, prices: dict[str, Price]):
        self.dir = tracking_dir / "costs"
        self.prices = prices

    def path(self, day: date) -> Path:
        return self.dir / f"{day:%Y-%m}.md"

    def _load(self, day: date) -> dict:
        path = self.path(day)
        if path.exists():
            meta = frontmatter.read(path).meta
        else:
            meta = {}
        meta.setdefault("month", f"{day:%Y-%m}")
        meta.setdefault("cap_usd", DEFAULT_CAP_USD)
        meta.setdefault("total_usd", 0.0)
        meta.setdefault("entries", [])
        return meta

    def total(self, day: date) -> float:
        return float(self._load(day)["total_usd"])

    def cap(self, day: date) -> float:
        return float(self._load(day)["cap_usd"])

    def price(self, model: str) -> Price:
        if model not in self.prices:
            raise KeyError(f"No price for model {model!r} in config/pricing.yaml")
        return self.prices[model]

    def worst_case(self, model: str, prompt_text: str, max_tokens: int) -> float:
        return self.price(model).cost(estimate_input_tokens(prompt_text), max_tokens)

    def check(self, day: date, estimate_usd: float) -> None:
        meta = self._load(day)
        total, cap = float(meta["total_usd"]), float(meta["cap_usd"])
        if total + estimate_usd > cap:
            raise BudgetExceeded(
                f"Tetto mensile raggiunto: spesi {total:.2f} USD su {cap:.2f}, "
                f"questo passo costerebbe fino a {estimate_usd:.4f} USD."
            )

    def record(
        self,
        day: date,
        feature: str,
        step: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        usd = round(self.price(model).cost(input_tokens, output_tokens), 6)
        meta = self._load(day)
        meta["entries"].append(
            {
                "date": day.isoformat(),
                "feature": feature,
                "step": step,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "usd": usd,
            }
        )
        meta["total_usd"] = round(float(meta["total_usd"]) + usd, 6)
        frontmatter.update(self.path(day), meta, generated_body=self._table(meta))
        return usd

    @staticmethod
    def _table(meta: dict) -> str:
        lines = [
            f"# Costi {meta['month']}",
            "",
            f"Totale: {float(meta['total_usd']):.4f} USD su un tetto di {float(meta['cap_usd']):.2f} USD.",
            "",
            "| Data | Funzione | Passo | Modello | Token in | Token out | USD |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for e in meta["entries"]:
            lines.append(
                f"| {e['date']} | {e['feature']} | {e['step']} | {e['model']} | "
                f"{e['input_tokens']} | {e['output_tokens']} | {e['usd']:.6f} |"
            )
        return "\n".join(lines)
