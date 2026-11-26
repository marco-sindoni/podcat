"""Test doubles: a TextModel that replays recorded outputs and never calls the network."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from podcat.llm.base import T, Usage


class FakeModel:
    def __init__(self, responses: dict[str, dict | Callable[[str], dict]], name: str = "claude-haiku-5-5"):
        # responses: schema class name -> JSON-like dict, or a function of the user prompt
        self.name = name
        self.responses = responses
        self.calls: list[tuple[str, str]] = []
        self.step = "call"

    @classmethod
    def from_dir(cls, directory: Path) -> "FakeModel":
        return cls({p.stem: json.loads(p.read_text(encoding="utf-8")) for p in directory.glob("*.json")})

    def for_step(self, step: str) -> "FakeModel":
        self.step = step
        return self

    def parse(self, system: str, user: str, schema: type[T], max_tokens: int) -> tuple[T, Usage]:
        self.calls.append((schema.__name__, user))
        data = self.responses[schema.__name__]
        if callable(data):
            data = data(user)
        return schema.model_validate(data), Usage(input_tokens=len(user) // 3, output_tokens=200)
