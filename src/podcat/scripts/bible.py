"""Read the production bible (character sheets, shot list) and config/scripts.yaml."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from podcat.scripts.models import CATS
from podcat.tracking import frontmatter


@dataclass(frozen=True)
class Bible:
    characters: dict[str, str]  # cat id -> sheet text (front matter dropped)
    shots: dict[str, str]  # shot id -> Italian label
    config: dict

    def shot_list_text(self) -> str:
        return "\n".join(f"- {sid}: {label}" for sid, label in self.shots.items())


def load_bible(repo_root: Path) -> Bible:
    chars = {}
    for cat in CATS:
        doc = frontmatter.read(repo_root / "bible" / "characters" / f"{cat}.md")
        voice = doc.meta.get("voice_profile", "")
        chars[cat] = (doc.body.strip() + (f"\n\nVoce: {voice}" if voice else "")).strip()
    shots = {}
    for line in (repo_root / "bible" / "shots.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*`([a-z0-9-]+)`\s*\|\s*([^|]+)\|", line)
        if m:
            shots[m.group(1)] = m.group(2).strip()
    config = yaml.safe_load((repo_root / "config" / "scripts.yaml").read_text(encoding="utf-8"))
    return Bible(characters=chars, shots=shots, config=config)
