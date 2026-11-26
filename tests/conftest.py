from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A throwaway repository root with the real config and an empty tracking dir."""
    root = tmp_path / "repo"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project]\nname='podcat-test'\n")
    shutil.copytree(REPO / "config", root / "config")
    (root / "tracking").mkdir()
    assets = tmp_path / "assets"
    assets.mkdir()
    monkeypatch.setenv("PODCAT_ASSETS_DIR", str(assets))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.chdir(root)
    return root
