"""Call 1: the writers' room writes two drafts with different angles (research R2)."""

from __future__ import annotations

from podcat.llm.base import TextModel
from podcat.scripts.bible import Bible
from podcat.scripts.models import RoomResult
from podcat.scripts.prompts import Brief, room_user, system_prompt

MAX_TOKENS = {"daily": 6_000, "weekly": 12_000}


def write_drafts(model: TextModel, bible: Bible, brief: Brief) -> RoomResult:
    result, _ = model.parse(system_prompt(bible, "room"), room_user(bible, brief), RoomResult, MAX_TOKENS[brief.kind])
    return result
