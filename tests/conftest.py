from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A throwaway repository root with the real config and an empty tracking dir."""
    root = tmp_path / "repo"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project]\nname='podcat-test'\n")
    shutil.copytree(REPO / "config", root / "config")
    # Tests use fixture feeds for every source, whatever the last real feed check said.
    sources_file = root / "config" / "sources.yaml"
    data = yaml.safe_load(sources_file.read_text(encoding="utf-8"))
    for source in data["sources"]:
        source["manual"] = False
    sources_file.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    (root / "tracking").mkdir()
    assets = tmp_path / "assets"
    assets.mkdir()
    monkeypatch.setenv("PODCAT_ASSETS_DIR", str(assets))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("PODCAT_ANTHROPIC_API_KEY", raising=False)
    monkeypatch.chdir(root)
    return root
