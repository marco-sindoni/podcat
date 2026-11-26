"""Provider-neutral interface for text models (constitution V: replaceable providers)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int


class ModelRefused(RuntimeError):
    """The model declined the request."""


class TextModel(Protocol):
    """A model that answers with JSON validated against a Pydantic schema."""

    name: str

    def parse(self, system: str, user: str, schema: type[T], max_tokens: int) -> tuple[T, Usage]:
        ...
