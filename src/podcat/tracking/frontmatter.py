"""Read and write Markdown files with a YAML front matter block.

Writers keep keys they do not know and any hand-written text in the body,
so Marco can add notes to tracking files (contracts/tracking-files.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DELIMITER = "---"
GENERATED_START = "<!-- podcat:generated:start -->"
GENERATED_END = "<!-- podcat:generated:end -->"


class FrontMatterError(ValueError):
    """Raised when a tracking file cannot be parsed."""


@dataclass
class Document:
    meta: dict[str, Any] = field(default_factory=dict)
    body: str = ""


def parse(text: str, source: str = "<text>") -> Document:
    if not text.startswith(DELIMITER + "\n"):
        return Document(meta={}, body=text)
    end = text.find("\n" + DELIMITER, len(DELIMITER))
    if end == -1:
        raise FrontMatterError(f"{source}: front matter is not closed with '---'")
    raw = text[len(DELIMITER) + 1 : end]
    rest = text[end + len(DELIMITER) + 1 :]
    if rest.startswith("\n"):  # end of the closing delimiter line
        rest = rest[1:]
    if rest.startswith("\n"):  # the blank line `dumps` writes after the front matter
        rest = rest[1:]
    try:
        meta = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise FrontMatterError(f"{source}: invalid YAML front matter: {exc}") from exc
    if not isinstance(meta, dict):
        raise FrontMatterError(f"{source}: front matter must be a mapping")
    return Document(meta=meta, body=rest)


def dumps(doc: Document) -> str:
    meta = yaml.safe_dump(doc.meta, sort_keys=False, allow_unicode=True, default_flow_style=False).strip()
    body = doc.body if doc.body.endswith("\n") or not doc.body else doc.body + "\n"
    return f"{DELIMITER}\n{meta}\n{DELIMITER}\n\n{body}"


def read(path: Path) -> Document:
    return parse(path.read_text(encoding="utf-8"), source=str(path))


def write(path: Path, doc: Document) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(doc), encoding="utf-8")


def update(path: Path, meta: dict[str, Any], generated_body: str | None = None) -> Document:
    """Merge `meta` into the file's front matter and replace only the generated body section.

    Unknown keys already in the file are kept. Text outside the generated markers is kept.
    """
    doc = read(path) if path.exists() else Document()
    merged = dict(doc.meta)
    merged.update(meta)
    body = doc.body
    if generated_body is not None:
        body = replace_generated(body, generated_body)
    new = Document(meta=merged, body=body)
    write(path, new)
    return new


def replace_generated(body: str, generated: str) -> str:
    block = f"{GENERATED_START}\n{generated.rstrip()}\n{GENERATED_END}"
    start = body.find(GENERATED_START)
    end = body.find(GENERATED_END)
    if start != -1 and end != -1 and end > start:
        return body[:start] + block + body[end + len(GENERATED_END) :]
    if body.strip():
        return block + "\n\n" + body.lstrip("\n")
    return block + "\n"
