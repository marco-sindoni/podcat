"""Call 2: the head writer picks, rewrites, adds two endings and notes; plus the one-shot fix (R2, R3)."""

from __future__ import annotations

from podcat.llm.base import TextModel
from podcat.scripts.bible import Bible
from podcat.scripts.models import FixResult, HeadWriterResult, RoomResult
from podcat.scripts.prompts import Brief, dump, fix_user, head_user, system_prompt

MAX_TOKENS = {"daily": 6_000, "weekly": 12_000}


def rewrite(model: TextModel, bible: Bible, brief: Brief, room: RoomResult) -> HeadWriterResult:
    drafts = dump([d.model_dump(mode="json") for d in room.drafts])
    result, _ = model.parse(system_prompt(bible, "head"), head_user(bible, brief, drafts), HeadWriterResult,
                            MAX_TOKENS[brief.kind])
    return result


def fix(model: TextModel, bible: Bible, brief: Brief, current: HeadWriterResult, problems: list[str]) -> FixResult:
    result, _ = model.parse(system_prompt(bible, "head"), fix_user(bible, brief, dump(current.model_dump(mode="json")), problems),
                            FixResult, MAX_TOKENS[brief.kind])
    return result
