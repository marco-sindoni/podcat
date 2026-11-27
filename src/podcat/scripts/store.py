"""Script index and version files under tracking/scripts/ (data-model.md, contracts/tracking-files.md)."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from podcat.news.store import slugify
from podcat.scripts.models import Version
from podcat.settings import now_rome
from podcat.tracking import frontmatter

ACTIVE = ("draft", "review", "approved")


class ScriptError(ValueError):
    """A user error on a script command."""


class ScriptStore:
    def __init__(self, tracking_dir: Path):
        self.dir = tracking_dir / "scripts"

    # paths ------------------------------------------------------------------

    def index_path(self, script_id: str) -> Path:
        return self.dir / f"{script_id}.md"

    def version_path(self, script_id: str, version: int) -> Path:
        return self.dir / script_id / f"v{version}.md"

    def new_id(self, day: date, kind: str, story_id: str) -> str:
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", story_id)
        base = f"{day.isoformat()}-{kind}-{slugify(slug, 40)}"
        candidate, n = base, 2
        while self.index_path(candidate).exists():
            candidate, n = f"{base}-{n}", n + 1
        return candidate

    # index ------------------------------------------------------------------

    def read(self, script_id: str) -> dict:
        path = self.index_path(script_id)
        if not path.exists():
            raise ScriptError(f"Copione {script_id} non trovato.")
        return frontmatter.read(path).meta

    def write(self, meta: dict, summary: str) -> Path:
        path = self.index_path(meta["id"])
        frontmatter.update(path, meta, generated_body=summary)
        return path

    def all(self) -> list[dict]:
        if not self.dir.exists():
            return []
        return [frontmatter.read(p).meta for p in sorted(self.dir.glob("*.md"))]

    def find(self, story_id: str, kind: str) -> dict | None:
        """The active (not discarded) script for a story and kind."""
        for meta in self.all():
            if meta.get("story_id") == story_id and meta.get("kind") == kind and meta.get("status") in ACTIVE:
                return meta
        return None

    def recent(self, before: dict | None = None, limit: int = 7, exclude: str | None = None) -> list[dict]:
        """Non-discarded scripts, newest first, created before `before` (a sort key) if given."""
        items = [m for m in self.all() if m.get("status") in ACTIVE and m.get("id") != exclude]
        items.sort(key=sort_key, reverse=True)
        if before is not None:
            items = [m for m in items if sort_key(m) < sort_key(before)]
        return items[:limit]

    # versions ---------------------------------------------------------------

    def read_version(self, script_id: str, version: int | None = None) -> Version:
        if version is None:
            version = int(self.read(script_id)["current_version"])
        path = self.version_path(script_id, version)
        if not path.exists():
            raise ScriptError(f"Versione {version} del copione {script_id} non trovata.")
        return Version.model_validate(frontmatter.read(path).meta)

    def write_version(self, script_id: str, version: Version, body: str) -> Path:
        path = self.version_path(script_id, version.version)
        doc = frontmatter.Document(meta=version.model_dump(mode="json"), body=body)
        frontmatter.write(path, doc)
        return path

    def add_version(
        self, meta: dict, version: Version, body: str, cause: str, cost_usd: float, summary: str
    ) -> dict:
        path = self.write_version(meta["id"], version, body)
        meta = dict(meta)
        meta["current_version"] = version.version
        meta.setdefault("versions", [])
        meta["versions"] = [v for v in meta["versions"] if v["version"] != version.version] + [
            {
                "version": version.version,
                "created_at": now_rome().isoformat(timespec="minutes"),
                "cause": cause,
                "words": version.words,
                "duration_s": version.duration_s,
                "cost_usd": round(cost_usd, 6),
                "path": str(path.relative_to(self.dir.parent.parent)),
            }
        ]
        meta["cost_usd"] = round(sum(float(v["cost_usd"]) for v in meta["versions"]), 6)
        self.write(meta, summary)
        return meta

    def set(self, script_id: str, summary: str | None = None, **fields: Any) -> dict:
        meta = self.read(script_id)
        meta.update(fields)
        frontmatter.update(self.index_path(script_id), meta, generated_body=summary)
        return meta


def sort_key(meta: dict) -> tuple[str, str]:
    created = ""
    versions = meta.get("versions") or []
    if versions:
        created = str(versions[0].get("created_at", ""))
    return (str(meta.get("date", "")), created)


def now_iso() -> str:
    return now_rome().isoformat(timespec="minutes")


def as_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])
