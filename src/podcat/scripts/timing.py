"""Word counts and durations, computed by code, never by the model (research R4)."""

from __future__ import annotations

import re

from podcat.scripts.models import Line, Scene

WORD = re.compile(r"[0-9A-Za-zÀ-ÿ]+(?:['’][0-9A-Za-zÀ-ÿ]+)*")


def count_words(text: str) -> int:
    return len(WORD.findall(text))


def spoken_words(lines: list[Line], skip_text: str | None = None) -> int:
    """Spoken words; `skip_text` (the Thursday formula) is not counted when a line starts with it."""
    total = 0
    for line in lines:
        text = line.text
        if skip_text and _norm(text).startswith(_norm(skip_text)):
            text = text.strip()[len(skip_text.strip()):]
        total += count_words(text)
    return total


def line_seconds(line: Line, config: dict) -> float:
    rate = float(config["words_per_second"][line.cat])
    return count_words(line.text) / rate + float(config["pause_s"])


def scene_seconds(scene: Scene, lines_by_n: dict[int, Line], config: dict) -> float:
    spoken = [lines_by_n[n] for n in scene.lines if n in lines_by_n]
    if spoken:
        return round(sum(line_seconds(l, config) for l in spoken), 1)
    return float(config["fixed_shot_s"].get(scene.shot, config["silent_default_s"]))


def apply_timing(
    lines: list[Line], scenes: list[Scene], config: dict, skip_text: str | None = None
) -> tuple[list[Scene], float]:
    """Fill each scene's duration; return the scenes and the total, sting and Thursday formula excluded."""
    by_n = {l.n: l for l in lines}
    out, total = [], 0.0
    if skip_text and lines and _norm(lines[0].text).startswith(_norm(skip_text)):
        rate = float(config["words_per_second"][lines[0].cat])
        total -= count_words(skip_text) / rate
    for scene in scenes:
        seconds = scene_seconds(scene, by_n, config)
        out.append(scene.model_copy(update={"duration_s": seconds}))
        if scene.shot != "sting-gnocchi":
            total += seconds
    return out, round(total, 1)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())
