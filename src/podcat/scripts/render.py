"""Italian document text of a script version (contracts/tracking-files.md)."""

from __future__ import annotations

from podcat.news.store import italian_date
from podcat.scripts.models import CAT_NAMES, MODE_IT, Version
from podcat.scripts.store import as_date


def shot_label(shots: dict[str, str], shot: str) -> str:
    return shots.get(shot, shot)


def render_version(index: dict, story: dict, v: Version, shots: dict[str, str]) -> str:
    day = as_date(index["date"])
    kind = "puntata della domenica" if index["kind"] == "weekly" else "reel"
    title = "Giovedì buone notizie" if index.get("good_news_thursday") else "Copione"
    out = [
        f"# {title} – {italian_date(day)} · {kind}",
        "",
        f"**Notizia**: {story.get('title')} · tono {index.get('tone')} · versione {v.version}",
        "",
        f"**Parole**: {v.words} · **Durata stimata**: {v.duration_s:.0f} s · "
        f"**Immagine**: {MODE_IT[v.news_image.mode]}, scena {v.news_image.scene}",
        "",
        "## Battute",
        "",
    ]
    for line in v.lines:
        mark = " *(tua)*" if line.manual else ""
        out.append(f"{line.n}. **{CAT_NAMES[line.cat]}**: {line.text}{mark}")
    out += ["", "## Scene", "", "| # | Inquadratura | Battute | Reazioni | Durata |", "| --- | --- | --- | --- | --- |"]
    for s in v.scenes:
        lines = ", ".join(str(n) for n in s.lines) or "–"
        reactions = "; ".join(f"{CAT_NAMES[r.cat]} {r.direction}" for r in s.reactions) or "–"
        out.append(f"| {s.n} | {shot_label(shots, s.shot)} | {lines} | {reactions} | {s.duration_s or 0:.0f} s |")
    img = v.news_image
    held = f", in mano a {CAT_NAMES[img.held_by]}" if img.held_by else ""
    out += [
        "",
        "## Immagine della notizia",
        "",
        f"{MODE_IT[img.mode]}{held}, scena {img.scene}, commentata dalla battuta {img.comment_line}. "
        f"Soggetto: {img.subject}",
        "",
        "## Finali alternativi",
        "",
    ]
    for i, e in enumerate(v.endings, 1):
        out.append(f"**Finale {i}** – Feedback: {e.feedback} / Flanella: {e.flanella}")
        out.append("")
    if v.answers:
        out += ["## Risposte ai tuoi commenti", ""]
        out += [f"- «{a.comment}»: {a.answer}" for a in v.answers]
        out.append("")
    if v.head_writer_notes:
        out += ["## Note del capo autore", ""]
        out += [f"- {n}" for n in v.head_writer_notes]
        out.append("")
    out.append("Commenta le battute. Scrivi «finale 1» o «finale 2» per cambiare il finale, «approvato» per approvare.")
    return "\n".join(out)


def render_index(index: dict, story: dict) -> str:
    lines = [
        f"# Copione: {story.get('title')}",
        "",
        f"Stato: {index['status']} · versione attuale {index['current_version']} · costo {index.get('cost_usd', 0):.4f} USD",
        "",
        f"Testo: [{index['id']}/v{index['current_version']}.md]({index['id']}/v{index['current_version']}.md)",
    ]
    if index.get("doc_url"):
        lines += ["", f"Documento: {index['doc_url']}"]
    if index.get("problems"):
        lines += ["", "Problemi da risolvere:"] + [f"- {p}" for p in index["problems"]]
    return "\n".join(lines)
