"""Deterministic checks run on every script version before delivery (research R3, R8, R10)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from podcat.scripts.models import CAT_NAMES, CATS, Ending, Line, NewsImage, Scene
from podcat.scripts.timing import spoken_words

NEWS_SHOT = {"A": "news-tv", "B": "news-cutin"}
NEIGHBOURS = {frozenset(p) for p in zip(CATS, CATS[1:])}


@dataclass
class CheckContext:
    kind: str  # daily | weekly
    thursday: bool
    category: str
    allowed_modes: list[str]
    shots: set[str]
    config: dict
    recent_first_lines: list[str] = field(default_factory=list)
    recent_last_lines: list[str] = field(default_factory=list)
    recent_texts: list[str] = field(default_factory=list)  # whole text of the previous scripts, newest first


def check(
    lines: list[Line],
    scenes: list[Scene],
    news_image: NewsImage,
    endings: list[Ending],
    duration_s: float,
    ctx: CheckContext,
) -> list[str]:
    """Return problems in Italian; an empty list means the script can be delivered."""
    p: list[str] = []
    cfg = ctx.config
    if not lines:
        return ["Il copione non ha battute."]
    if [l.n for l in lines] != list(range(1, len(lines) + 1)):
        p.append("Le battute devono essere numerate da 1 in ordine, senza buchi.")
    by_n = {l.n: l for l in lines}

    # Fixed structure (FR-003)
    if lines[0].cat != "flanella":
        p.append("La prima battuta deve essere di Flanella.")
    if lines[-1].cat != "flanella":
        p.append("L'ultima battuta deve essere di Flanella.")
    if len(lines) < 2 or lines[-2].cat != "feedback":
        p.append("La penultima battuta deve essere la battuta finale di Feedback.")

    speakers = {l.cat for l in lines}
    if "fuzz" not in speakers and "vinile" not in speakers:
        p.append("Oltre a Flanella e Feedback deve parlare almeno uno tra Fuzz e Vinile.")
    if ctx.category in cfg.get("vinile_categories", []) and "vinile" not in speakers:
        p.append("Su cultura, spettacolo e musica Vinile deve parlare.")

    # Length (FR-004)
    formula = cfg["thursday_formula"] if ctx.thursday else None
    words = spoken_words(lines, skip_text=formula)
    limits = cfg["words"][ctx.kind]
    if not limits["min"] <= words <= limits["max"]:
        p.append(f"Parole: {words}, devono essere tra {limits['min']} e {limits['max']}.")
    if ctx.kind == "weekly":
        for cat in CATS:
            if sum(1 for l in lines if l.cat == cat) < 2:
                p.append(f"Nella puntata settimanale {CAT_NAMES[cat]} deve avere almeno due battute.")

    # Scenes (FR-005, R11)
    used: list[int] = []
    for s in scenes:
        if s.shot not in ctx.shots:
            p.append(f"Scena {s.n}: inquadratura sconosciuta «{s.shot}».")
        used += s.lines
        if s.shot.startswith("two-"):
            pair = s.shot[4:].split("-")
            if frozenset(pair) not in NEIGHBOURS:
                p.append(f"Scena {s.n}: «{s.shot}» non è una coppia di poltrone vicine.")
        if s.shot.startswith("close-") and s.lines:
            cat = s.shot[6:]
            if any(by_n[n].cat != cat for n in s.lines if n in by_n):
                p.append(f"Scena {s.n}: nel primo piano di {CAT_NAMES.get(cat, cat)} parla un altro gatto.")
    if sorted(used) != [l.n for l in lines] or used != sorted(used):
        p.append("Ogni battuta deve stare in una sola scena, nell'ordine del copione.")
    if [s.n for s in scenes] != list(range(1, len(scenes) + 1)):
        p.append("Le scene devono essere numerate da 1 in ordine.")

    # Silent cats react (FR-018)
    reacting = {r.cat for s in scenes for r in s.reactions}
    for cat in CATS:
        if cat not in speakers and cat not in reacting:
            p.append(f"{CAT_NAMES[cat]} non parla: deve avere almeno una reazione in una scena.")

    # Duration (FR-005)
    target, tol = cfg["target_s"][ctx.kind], cfg["tolerance_s"][ctx.kind]
    if abs(duration_s - target) > tol:
        p.append(f"Durata stimata {duration_s:.0f} s, deve essere {target} s ± {tol}.")

    # News image (FR-006)
    p += _check_image(news_image, scenes, by_n, ctx)

    # Thursday (FR-009)
    if ctx.thursday:
        if not scenes or scenes[0].shot != "sting-gnocchi" or scenes[0].lines:
            p.append("Il giovedì la prima scena è lo stacchetto degli gnocchi, senza battute.")
        if not _norm(lines[0].text).startswith(_norm(cfg["thursday_formula"])):
            p.append(f"Il giovedì Flanella apre con la formula: «{cfg['thursday_formula']}».")

    # Endings (FR-017)
    if len(endings) != 2 or any(not e.feedback.strip() or not e.flanella.strip() for e in endings):
        p.append("Servono esattamente 2 finali alternativi, ognuno con Feedback e Flanella.")

    # Repetition (FR-008, R8)
    if _norm(lines[0].text) in {_norm(t) for t in ctx.recent_first_lines}:
        p.append("La prima battuta è uguale a quella di un copione recente.")
    if _norm(lines[-1].text) in {_norm(t) for t in ctx.recent_last_lines}:
        p.append("L'ultima battuta è uguale a quella di un copione recente.")
    text = " ".join(l.text for l in lines)
    for cat, tics in cfg.get("tics", {}).items():
        for tic in tics:
            if _has(text, tic) and len(ctx.recent_texts) >= 2 and all(_has(t, tic) for t in ctx.recent_texts[:2]):
                p.append(f"Il tormentone «{tic}» è già nei due copioni precedenti: cambialo.")
    return p


def _check_image(img: NewsImage, scenes: list[Scene], by_n: dict[int, Line], ctx: CheckContext) -> list[str]:
    p = []
    if img.mode not in ctx.allowed_modes:
        p.append(f"Immagine della notizia: il modo {img.mode} è uguale al video precedente; usa {' o '.join(ctx.allowed_modes)}.")
    scene = next((s for s in scenes if s.n == img.scene), None)
    if scene is None:
        return p + [f"Immagine della notizia: la scena {img.scene} non esiste."]
    expected = NEWS_SHOT.get(img.mode) or (f"news-held-{img.held_by}" if img.held_by else None)
    if img.mode == "C" and not img.held_by:
        p.append("Modo C: manca il gatto che tiene il giornale o la foto.")
    elif scene.shot != expected:
        p.append(f"Immagine della notizia: la scena {img.scene} deve usare l'inquadratura «{expected}».")
    if img.mode == "C" and img.held_by and not any(by_n.get(n) and by_n[n].cat == img.held_by for n in scene.lines):
        p.append("Modo C: il gatto che tiene il giornale deve parlare in quella scena.")
    if img.comment_line not in by_n:
        p.append("Immagine della notizia: la battuta che la commenta non esiste.")
    news_scenes = [s for s in scenes if s.shot.startswith("news-")]
    if len(news_scenes) != 1:
        p.append("L'immagine della notizia deve comparire in una sola scena.")
    if not img.subject.strip():
        p.append("Immagine della notizia: manca la frase sul soggetto.")
    return p


def _norm(text: str) -> str:
    return re.sub(r"[^\w]+", " ", text.lower()).strip()


def _has(text: str, tic: str) -> bool:
    return _norm(tic) in _norm(text)
