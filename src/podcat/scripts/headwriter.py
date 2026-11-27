"""Call 2: the head writer picks, rewrites, adds two endings and notes; plus the one-shot fix (R2, R3)."""

from __future__ import annotations

from podcat.llm.base import TextModel
from podcat.scripts.bible import Bible
from podcat.scripts.models import FixResult, HeadWriterResult, RoomResult
from podcat.scripts.timing import count_words
from podcat.scripts.prompts import Brief, dump, fix_user, head_user, system_prompt

MAX_TOKENS = {"daily": 16_000, "weekly": 20_000}


def rewrite(model: TextModel, bible: Bible, brief: Brief, room: RoomResult) -> HeadWriterResult:
    drafts = dump([d.model_dump(mode="json") for d in room.drafts])
    result, _ = model.parse(system_prompt(bible, "head"), head_user(bible, brief, drafts), HeadWriterResult,
                            MAX_TOKENS[brief.kind])
    return result


def word_report(bible: Bible, brief: Brief, current: HeadWriterResult) -> str:
    """Exact word counts per line, so the model knows how much to cut or add (models miscount)."""
    limits = bible.config["words"][brief.kind]
    counts = [(l.n, count_words(l.text)) for l in current.lines]
    total = sum(c for _, c in counts)
    target = (limits["min"] + limits["max"]) // 2
    lines = ", ".join(f"battuta {n}: {c}" for n, c in counts)
    delta = total - target
    action = f"taglia circa {delta} parole" if delta > 0 else f"aggiungi circa {-delta} parole"
    return (f"\nParole contate dal programma: {lines}; totale {total}. Obiettivo {target} "
            f"(tra {limits['min']} e {limits['max']}): {action}.")


def fix(model: TextModel, bible: Bible, brief: Brief, current: HeadWriterResult, problems: list[str]) -> FixResult:
    user = fix_user(bible, brief, dump(current.model_dump(mode="json")), problems, word_report(bible, brief, current))
    result, _ = model.parse(system_prompt(bible, "head"), user, FixResult, MAX_TOKENS[brief.kind])
    return result
