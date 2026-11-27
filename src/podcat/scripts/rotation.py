"""News image mode rotation: never the mode of the previous video (research R7)."""

from __future__ import annotations

from podcat.scripts.store import ScriptStore

MODES = ["A", "B", "C"]


def previous_script(store: ScriptStore, current: dict, exclude: str | None = None) -> dict | None:
    items = store.recent(before=current, limit=1, exclude=exclude)
    return items[0] if items else None


def allowed_modes(previous: dict | None) -> list[str]:
    last = previous.get("news_image_mode") if previous else None
    return [m for m in MODES if m != last]
