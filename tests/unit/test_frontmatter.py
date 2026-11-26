from pathlib import Path

import pytest

from podcat.tracking import frontmatter as fm


def test_roundtrip(tmp_path: Path):
    path = tmp_path / "a.md"
    fm.write(path, fm.Document(meta={"date": "2026-11-27", "candidates": ["a", "b"]}, body="# Titolo\n"))
    doc = fm.read(path)
    assert doc.meta == {"date": "2026-11-27", "candidates": ["a", "b"]}
    assert doc.body == "# Titolo\n"


def test_update_keeps_unknown_keys_and_hand_notes(tmp_path: Path):
    path = tmp_path / "a.md"
    fm.update(path, {"status": "proposed"}, generated_body="| tabella |")
    text = path.read_text()
    text = text.replace("status: proposed", "status: proposed\nnote_marco: bella")
    text += "\nNota a mano di Marco.\n"
    path.write_text(text)
    fm.update(path, {"status": "picked"}, generated_body="| tabella nuova |")
    doc = fm.read(path)
    assert doc.meta["status"] == "picked"
    assert doc.meta["note_marco"] == "bella"
    assert "Nota a mano di Marco." in doc.body
    assert "| tabella nuova |" in doc.body
    assert "| tabella |\n" not in doc.body


def test_no_front_matter():
    doc = fm.parse("solo testo")
    assert doc.meta == {} and doc.body == "solo testo"


def test_invalid_yaml_reports_file():
    with pytest.raises(fm.FrontMatterError, match="x.md"):
        fm.parse("---\n: : :\n---\n", source="x.md")


def test_unclosed_front_matter():
    with pytest.raises(fm.FrontMatterError):
        fm.parse("---\na: 1\n")
