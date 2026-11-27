"""Tracking files for stories, shortlists and run logs, plus the JSON cache outside git."""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from podcat.news.models import CATEGORY_IT
from podcat.tracking import frontmatter

WEEKDAYS_IT = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MONTHS_IT = [
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]


def italian_date(day: date) -> str:
    return f"{WEEKDAYS_IT[day.weekday()]} {day.day} {MONTHS_IT[day.month - 1]} {day.year}"


def slugify(text: str, max_len: int = 50) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:max_len].rstrip("-") or "notizia"


class NewsStore:
    def __init__(self, tracking_dir: Path, cache_dir: Path):
        self.root = tracking_dir / "news"
        self.stories_dir = self.root / "stories"
        self.shortlists_dir = self.root / "shortlists"
        self.runs_dir = self.root / "runs"
        self.cache_root = cache_dir / "news"

    # cache ------------------------------------------------------------------

    def cache_dir(self, day: date, kind: str) -> Path:
        return self.cache_root / f"{day.isoformat()}-{kind}"

    def cache_read(self, day: date, kind: str, name: str) -> Any | None:
        path = self.cache_dir(day, kind) / f"{name}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def cache_write(self, day: date, kind: str, name: str, data: Any) -> None:
        path = self.cache_dir(day, kind) / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8")

    def cache_clear(self, day: date, kind: str) -> None:
        directory = self.cache_dir(day, kind)
        if directory.exists():
            for f in directory.glob("*.json"):
                f.unlink()

    # stories ----------------------------------------------------------------

    def story_path(self, story_id: str) -> Path:
        return self.stories_dir / f"{story_id}.md"

    def new_story_id(self, day: date, title: str) -> str:
        base = f"{day.isoformat()}-{slugify(title)}"
        candidate, n = base, 2
        while self.story_path(candidate).exists():
            candidate, n = f"{base}-{n}", n + 1
        return candidate

    def write_story(self, meta: dict) -> None:
        body = [f"# {meta['title']}", "", meta["summary"], "", "## Fonti", ""]
        for s in meta["sources"]:
            body.append(f"- [{s['outlet']}]({s['url']})")
        body += [
            "",
            f"Importanza {meta['importance']}/5: {meta['importance_reason']}",
            "",
            f"Potenziale comico {meta['comic_potential']}/5: {meta['comic_reason']}",
        ]
        frontmatter.update(self.story_path(meta["id"]), meta, generated_body="\n".join(body))

    def read_story(self, story_id: str) -> dict:
        return frontmatter.read(self.story_path(story_id)).meta

    def set_story(self, story_id: str, **fields: Any) -> None:
        path = self.story_path(story_id)
        doc = frontmatter.read(path)
        doc.meta.update(fields)
        frontmatter.write(path, doc)

    def all_stories(self) -> list[dict]:
        if not self.stories_dir.exists():
            return []
        return [frontmatter.read(p).meta for p in sorted(self.stories_dir.glob("*.md"))]

    def stories_between(self, start: date, end: date) -> list[dict]:
        out = []
        for s in self.all_stories():
            seen = _as_date(s.get("first_seen"))
            if seen and start <= seen <= end:
                out.append(s)
        return out

    def recent_covered(self, day: date, days: int = 30) -> list[dict]:
        """Stories chosen or used recently: the editorial pass avoids repeating them."""
        stories = self.stories_between(day - timedelta(days=days), day)
        return [{"id": s["id"], "title": s["title"]} for s in stories if s.get("status") in ("chosen", "used")]

    def rejected_urls(self, day: date, days: int = 7) -> set[str]:
        urls = set()
        for s in self.stories_between(day - timedelta(days=days), day):
            if s.get("status") == "rejected":
                urls.update(src["url"] for src in s.get("sources", []))
        return urls

    # shortlists -------------------------------------------------------------

    def shortlist_path(self, day: date, kind: str) -> Path:
        return self.shortlists_dir / f"{day.isoformat()}-{kind}.md"

    def read_shortlist(self, day: date, kind: str) -> dict | None:
        path = self.shortlist_path(day, kind)
        return frontmatter.read(path).meta if path.exists() else None

    def write_shortlist(self, meta: dict) -> Path:
        day = _as_date(meta["date"])
        path = self.shortlist_path(day, meta["kind"])
        frontmatter.update(path, meta, generated_body=self.render_shortlist(meta))
        return path

    def render_shortlist(self, meta: dict) -> str:
        day = _as_date(meta["date"])
        if meta["kind"] == "weekly":
            heading = f"# Notizie per la puntata settimanale – {italian_date(day)}"
        elif meta.get("good_news_thursday"):
            heading = f"# Giovedì buone notizie – {italian_date(day)}"
        else:
            heading = f"# Notizie candidate – {italian_date(day)}"
        lines = [heading, ""]
        if meta.get("warning"):
            lines += [f"> Attenzione: {meta['warning']}", ""]
        if meta.get("note"):
            lines += [f"> Nota: {meta['note']}", ""]
        lines += self._story_table(meta.get("candidates", []), meta.get("picked"), weekly=meta["kind"] == "weekly")
        if meta.get("backups"):
            lines += ["", "## Riserve dei giorni precedenti", ""]
            lines += self._story_table(meta["backups"], None, weekly=False)
        if meta.get("gaps"):
            lines += ["", "Giorni senza giro giornaliero: " + ", ".join(str(g) for g in meta["gaps"]) + "."]
        lines += ["", "## Dettagli", ""]
        for n, sid in enumerate(meta.get("candidates", []), start=1):
            s = self.read_story(sid)
            lines += [f"### {n}. {s['title']}", "", s["summary"], ""]
            lines.append(f"- Importanza {s['importance']}/5: {s['importance_reason']}")
            lines.append(f"- Potenziale comico {s['comic_potential']}/5: {s['comic_reason']}")
            if s.get("satirical_potential") is not None:
                lines.append(f"- Potenziale satirico {s['satirical_potential']}/5: {s.get('satirical_reason', '')}")
            if s.get("clarity") is not None:
                lines.append(f"- Comprensibilità {s['clarity']}/5: {s.get('clarity_reason', '')}")
            if s.get("tone") == "pungente":
                lines.append("- Tono: pungente (satira, osservazioni pungenti, riflessione)")
            if s.get("flags"):
                lines.append("- Attenzione: " + ", ".join(s["flags"]))
            if s.get("follow_up_of"):
                lines.append(f"- Seguito di: {s['follow_up_of']}")
            lines.append("- Fonti: " + ", ".join(f"[{x['outlet']}]({x['url']})" for x in s["sources"]))
            lines.append("")
        return "\n".join(lines).rstrip()

    def _story_table(self, ids: list[str], picked: str | None, weekly: bool) -> list[str]:
        head = "| # | Notizia | Tono | Categoria | Comicità | Satira | Comprensibilità | Importanza | Fonti |"
        if weekly:
            head += " Reel |"
        lines = [head, "|" + " --- |" * (head.count("|") - 1)]
        for n, sid in enumerate(ids, start=1):
            s = self.read_story(sid)
            mark = " ✅" if sid == picked else ""
            outlets = ", ".join(dict.fromkeys(x["outlet"] for x in s["sources"]))
            row = (
                f"| {n} | {s['title']}{mark} | {s.get('tone') or 'n/d'} | "
                f"{CATEGORY_IT.get(s['category'], s['category'])} | {s['comic_potential']} | "
                f"{_score(s.get('satirical_potential'))} | {_score(s.get('clarity'))} | {s['importance']} | {outlets} |"
            )
            if weekly:
                row += " " + ("già usata" if s.get("status") == "used" else "nuova") + " |"
            lines.append(row)
        return lines

    # run logs ---------------------------------------------------------------

    def write_run_log(self, day: date, kind: str, meta: dict, discarded: list[dict]) -> Path:
        path = self.runs_dir / f"{day.isoformat()}-{kind}.md"
        lines = [f"# Registro del giro – {italian_date(day)} ({kind})", ""]
        if meta.get("feeds_failed"):
            lines += ["## Feed non raggiungibili", ""]
            lines += [f"- {f['source']}: {f['error']} ({f['url']})" for f in meta["feeds_failed"]]
            lines.append("")
        lines += ["## Notizie scartate", "", "| Notizia | Motivo |", "| --- | --- |"]
        for d in discarded:
            lines.append(f"| {d['title'].replace('|', '/')} | {d['reason'].replace('|', '/')} |")
        meta = dict(meta, discarded=len(discarded))
        frontmatter.write(path, frontmatter.Document(meta=meta, body="\n".join(lines) + "\n"))
        return path


def _score(value: Any) -> str:
    return "n/d" if value is None else str(value)


def _as_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])
