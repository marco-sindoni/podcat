"""Settings loaded from the environment and `.env`, plus shared paths and time helpers."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

ROME = ZoneInfo("Europe/Rome")


def find_repo_root(start: Path | None = None) -> Path:
    """Return the closest parent directory holding `pyproject.toml` and `config/`."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "config").is_dir():
            return candidate
    raise FileNotFoundError("Podcat repository root not found (run from inside the repository).")


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    assets_dir: Path
    anthropic_api_key: str | None

    @property
    def config_dir(self) -> Path:
        return self.repo_root / "config"

    @property
    def tracking_dir(self) -> Path:
        return self.repo_root / "tracking"

    @property
    def cache_dir(self) -> Path:
        return self.assets_dir / "cache"


def load_settings(repo_root: Path | None = None) -> Settings:
    root = repo_root or find_repo_root()
    load_dotenv(root / ".env", override=False)
    assets = os.environ.get("PODCAT_ASSETS_DIR") or str(Path(tempfile.gettempdir()) / "podcat-assets")
    return Settings(
        repo_root=root,
        assets_dir=Path(assets).expanduser(),
        anthropic_api_key=os.environ.get("PODCAT_ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or None,
    )


def now_rome() -> datetime:
    return datetime.now(ROME)


def today_rome() -> date:
    return now_rome().date()
