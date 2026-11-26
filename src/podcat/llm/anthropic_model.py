"""Claude through the official Anthropic SDK, with the budget check around every call."""

from __future__ import annotations

from datetime import date

import anthropic

from podcat.llm.base import ModelRefused, T, Usage
from podcat.tracking.costs import Ledger


class AnthropicModel:
    def __init__(
        self,
        model: str,
        ledger: Ledger,
        day: date,
        feature: str,
        api_key: str | None = None,
        client: anthropic.Anthropic | None = None,
    ):
        self.name = model
        self.ledger = ledger
        self.day = day
        self.feature = feature
        self.step = "call"
        self._client = client
        self._api_key = api_key

    @property
    def client(self) -> anthropic.Anthropic:
        if self._client is None:
            # With no key given, the SDK uses its own credential lookup (ANTHROPIC_API_KEY, profiles).
            self._client = anthropic.Anthropic(api_key=self._api_key) if self._api_key else anthropic.Anthropic()
        return self._client

    def for_step(self, step: str) -> "AnthropicModel":
        self.step = step
        return self

    def parse(self, system: str, user: str, schema: type[T], max_tokens: int) -> tuple[T, Usage]:
        # Refuse before paying if the worst case would exceed the monthly cap.
        self.ledger.check(self.day, self.ledger.worst_case(self.name, system + user, max_tokens))
        response = self.client.messages.parse(
            model=self.name,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=schema,
        )
        usage = Usage(response.usage.input_tokens, response.usage.output_tokens)
        self.ledger.record(self.day, self.feature, self.step, self.name, usage.input_tokens, usage.output_tokens)
        if response.stop_reason == "refusal":
            raise ModelRefused(f"{self.name} declined the {self.step} request")
        if response.stop_reason == "max_tokens":
            raise RuntimeError(f"{self.name} hit max_tokens={max_tokens} during {self.step}")
        parsed = response.parsed_output
        if parsed is None:
            raise RuntimeError(f"{self.name} returned no parsable output during {self.step}")
        return parsed, usage
