"""Write orchestration: picked story → writers' room → head writer → checks → one fix → save (spec 002)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

from podcat.news.store import NewsStore
from podcat.scripts import checks, headwriter, room, rotation
from podcat.scripts.bible import Bible, load_bible
from podcat.scripts.models import HeadWriterResult, Version
from podcat.scripts.prompts import Brief
from podcat.scripts.render import render_index, render_version
from podcat.scripts.store import ScriptError, ScriptStore, now_iso
from podcat.scripts.timing import apply_timing, spoken_words
from podcat.settings import Settings
from podcat.tracking.costs import Ledger, load_prices

# factory(ledger, day, step) -> TextModel; step is room | head-writer | fix | revision
ModelFactory = Callable[[Ledger, date, str], object]


@dataclass
class WriteResult:
    script_id: str
    path: Path
    created: bool
    problems: list[str] = field(default_factory=list)
    cost_usd: float = 0.0


@dataclass
class Context:
    settings: Settings
    bible: Bible
    news: NewsStore
    scripts: ScriptStore
    ledger: Ledger


def context(settings: Settings) -> Context:
    return Context(
        settings=settings,
        bible=load_bible(settings.repo_root),
        news=NewsStore(settings.tracking_dir, settings.cache_dir),
        scripts=ScriptStore(settings.tracking_dir),
        ledger=Ledger(settings.tracking_dir, load_prices(settings.config_dir)),
    )


def picked_story(ctx: Context, day: date, kind: str) -> tuple[dict, dict]:
    shortlist = ctx.news.read_shortlist(day, kind)
    if shortlist is None:
        raise ScriptError(f"Nessuna lista {kind} per il {day.isoformat()}.")
    if not shortlist.get("picked"):
        raise ScriptError("Nella lista non è ancora stata scelta una notizia.")
    return shortlist, ctx.news.read_story(shortlist["picked"])


def recent_lines(ctx: Context, exclude: str | None, current: dict) -> tuple[list[dict], list[str]]:
    """First/last lines and whole texts of the last scripts (research R8)."""
    window = int(ctx.bible.config.get("repeat_window", 7))
    briefs, texts = [], []
    for meta in ctx.scripts.recent(before=current, limit=window, exclude=exclude):
        v = ctx.scripts.read_version(meta["id"])
        briefs.append({"first": v.lines[0].text, "last": v.lines[-1].text})
        texts.append(" ".join(l.text for l in v.lines))
    return briefs, texts


def check_context(ctx: Context, kind: str, thursday: bool, story: dict, allowed: list[str],
                  recent: list[dict], texts: list[str]) -> checks.CheckContext:
    return checks.CheckContext(
        kind=kind,
        thursday=thursday,
        category=story.get("category", ""),
        allowed_modes=allowed,
        shots=set(ctx.bible.shots),
        config=ctx.bible.config,
        recent_first_lines=[r["first"] for r in recent],
        recent_last_lines=[r["last"] for r in recent],
        recent_texts=texts,
    )


def build_version(number: int, result: HeadWriterResult, ctx: Context, thursday: bool, **extra) -> Version:
    cfg = ctx.bible.config
    formula = cfg["thursday_formula"] if thursday else None
    scenes, total = apply_timing(result.lines, result.scenes, cfg, skip_text=formula)
    return Version(
        version=number,
        lines=result.lines,
        scenes=scenes,
        news_image=result.news_image,
        endings=result.endings,
        words=spoken_words(result.lines, skip_text=formula),
        duration_s=total,
        head_writer_notes=result.notes,
        chosen_angle=result.chosen_angle,
        **extra,
    )


def run_checks(v: Version, cctx: checks.CheckContext) -> list[str]:
    return checks.check(v.lines, v.scenes, v.news_image, v.endings, v.duration_s, cctx)


def reel_lines_for(ctx: Context, story_id: str) -> list[str]:
    meta = ctx.scripts.find(story_id, "daily")
    if not meta:
        return []
    return [l.text for l in ctx.scripts.read_version(meta["id"]).lines]


def write(settings: Settings, day: date, kind: str, factory: ModelFactory, new_draft: bool = False) -> WriteResult:
    ctx = context(settings)
    shortlist, story = picked_story(ctx, day, kind)
    existing = ctx.scripts.find(story["id"], kind)
    if existing and not new_draft:
        return WriteResult(existing["id"], ctx.scripts.index_path(existing["id"]), False, existing.get("problems") or [])
    if existing and existing["status"] == "approved":
        raise ScriptError("Il copione è approvato: riaprilo prima di riscriverlo.")
    if kind == "daily" and not existing and story.get("status") != "chosen":
        raise ScriptError(f"La notizia {story['id']} non è nello stato «chosen».")

    thursday = bool(shortlist.get("good_news_thursday")) and kind == "daily"
    tone = (existing or {}).get("tone") or story.get("tone") or "comico"
    current = {"date": day.isoformat(), "versions": [{"created_at": now_iso()}]}
    exclude = existing["id"] if existing else None
    previous = rotation.previous_script(ctx.scripts, current, exclude=exclude)
    allowed = rotation.allowed_modes(previous)
    recent, texts = recent_lines(ctx, exclude, current)
    brief = Brief(kind=kind, story=story, thursday=thursday, tone=tone, allowed_modes=allowed, recent=recent,
                  reel_lines=reel_lines_for(ctx, story["id"]) if kind == "weekly" else [])
    cctx = check_context(ctx, kind, thursday, story, allowed, recent, texts)

    spent_before = ctx.ledger.total(day)
    drafts = room.write_drafts(factory(ctx.ledger, day, "room"), ctx.bible, brief)
    head = factory(ctx.ledger, day, "head-writer")
    result = headwriter.rewrite(head, ctx.bible, brief, drafts)
    number = int(existing["current_version"]) + 1 if existing else 1
    version = build_version(number, result, ctx, thursday)
    problems = run_checks(version, cctx)
    if problems:
        result = headwriter.fix(factory(ctx.ledger, day, "fix"), ctx.bible, brief, result, problems)
        version = build_version(number, result, ctx, thursday)
        problems = run_checks(version, cctx)
    cost = round(ctx.ledger.total(day) - spent_before, 6)

    meta = existing or {
        "id": ctx.scripts.new_id(day, kind, story["id"]),
        "story_id": story["id"],
        "kind": kind,
        "date": day.isoformat(),
        "good_news_thursday": thursday,
        "doc_url": None,
        "approved_at": None,
        "approved_version": None,
        "versions": [],
    }
    meta.update(
        tone=tone,
        status=meta.get("status") if existing and meta.get("status") == "review" and not problems else "draft",
        problems=problems,
        news_image_mode=version.news_image.mode,
        previous_script=previous["id"] if previous else None,
    )
    body = render_version(meta, story, version, ctx.bible.shots)
    meta = ctx.scripts.add_version(meta, version, body, "new-draft" if existing else "write", cost, "")
    ctx.scripts.set(meta["id"], summary=render_index(meta, story))
    ctx.news.set_story(story["id"], script=meta["id"])
    return WriteResult(meta["id"], ctx.scripts.index_path(meta["id"]), True, problems, cost)


def show(settings: Settings, day: date, kind: str, version: int | None = None) -> str:
    ctx = context(settings)
    _, story = picked_story(ctx, day, kind)
    meta = ctx.scripts.find(story["id"], kind)
    if not meta:
        raise ScriptError("Per questa notizia non c'è ancora un copione.")
    v = ctx.scripts.read_version(meta["id"], version)
    return render_version(meta, story, v, ctx.bible.shots)


def listing(settings: Settings, last: int = 10) -> list[dict]:
    store = ScriptStore(settings.tracking_dir)
    items = sorted(store.all(), key=lambda m: (str(m.get("date")), m.get("id")), reverse=True)
    return items[:last]


# review (User Story 2) --------------------------------------------------------


@dataclass
class Loaded:
    ctx: Context
    shortlist: dict
    story: dict
    meta: dict
    version: Version


def load(settings: Settings, day: date, kind: str) -> Loaded:
    ctx = context(settings)
    shortlist, story = picked_story(ctx, day, kind)
    meta = ctx.scripts.find(story["id"], kind)
    if not meta:
        raise ScriptError("Per questa notizia non c'è ancora un copione.")
    return Loaded(ctx, shortlist, story, meta, ctx.scripts.read_version(meta["id"]))


def _editable(l: Loaded) -> None:
    if l.meta["status"] == "approved":
        raise ScriptError("Il copione è approvato: per cambiarlo scrivi prima «riapri».")


def _brief_and_checks(l: Loaded, tone: str | None = None) -> tuple[Brief, checks.CheckContext, bool]:
    ctx, meta, story = l.ctx, l.meta, l.story
    thursday = bool(meta.get("good_news_thursday"))
    previous = rotation.previous_script(ctx.scripts, meta, exclude=meta["id"])
    allowed = rotation.allowed_modes(previous)
    recent, texts = recent_lines(ctx, meta["id"], meta)
    brief = Brief(kind=meta["kind"], story=story, thursday=thursday, tone=tone or meta.get("tone") or "comico",
                  allowed_modes=allowed, recent=recent,
                  reel_lines=reel_lines_for(ctx, story["id"]) if meta["kind"] == "weekly" else [])
    return brief, check_context(ctx, meta["kind"], thursday, story, allowed, recent, texts), thursday


def _save(l: Loaded, result: HeadWriterResult, cause: str, cost: float, problems_from: checks.CheckContext,
          thursday: bool, **extra) -> WriteResult:
    ctx, meta = l.ctx, dict(l.meta)
    number = int(meta["current_version"]) + 1
    version = build_version(number, result, ctx, thursday, **extra)
    problems = run_checks(version, problems_from)
    meta.update(status="review" if meta.get("doc_url") else "draft", problems=problems,
                news_image_mode=version.news_image.mode)
    body = render_version(meta, l.story, version, ctx.bible.shots)
    meta = ctx.scripts.add_version(meta, version, body, cause, cost, "")
    ctx.scripts.set(meta["id"], summary=render_index(meta, l.story))
    return WriteResult(meta["id"], ctx.scripts.index_path(meta["id"]), True, problems, cost)


def revise(settings: Settings, day: date, kind: str, comments_text: str, factory: ModelFactory,
           tone: str | None = None) -> WriteResult:
    from podcat.scripts import revise as rv

    l = load(settings, day, kind)
    _editable(l)
    comments = rv.load_comments(comments_text)
    digest = rv.comments_digest(comments, int(l.meta["current_version"]))
    applied = l.meta.get("applied_comments") or []
    if digest in applied or rv.comments_digest(comments, int(l.meta["current_version"]) - 1) in applied:
        return WriteResult(l.meta["id"], l.ctx.scripts.index_path(l.meta["id"]), False, l.meta.get("problems") or [])
    brief, cctx, thursday = _brief_and_checks(l, tone)
    ledger, spent = l.ctx.ledger, l.ctx.ledger.total(day)
    rev = rv.ask_revision(factory(ledger, day, "revision"), l.ctx.bible, brief, l.version, comments)
    result, warnings = rv.apply_revision(l.version, rev)
    new_tone = tone or rev.tone or l.meta.get("tone")
    if new_tone != brief.tone:
        brief.tone = new_tone
    probe = build_version(0, result, l.ctx, thursday)
    problems = run_checks(probe, cctx)
    if problems:
        result = headwriter.fix(factory(ledger, day, "fix"), l.ctx.bible, brief, result, problems)
        # Marco's manual lines win over the fix
        manual = {x.n: x for x in l.version.lines if x.manual}
        result.lines = [manual[x.n] if x.n in manual and manual[x.n].cat == x.cat else x for x in result.lines]
    cost = round(ledger.total(day) - spent, 6)
    l.meta = {**l.meta, "tone": new_tone, "applied_comments": applied + [digest]}
    return _save(l, result, "revise", cost, cctx, thursday, answers=rv.answers_for(rev, warnings),
                 coherence_changes=rev.coherence_changes)


def ending(settings: Settings, day: date, kind: str, number: int) -> WriteResult:
    from podcat.scripts import revise as rv

    l = load(settings, day, kind)
    _editable(l)
    _, cctx, thursday = _brief_and_checks(l)
    return _save(l, rv.swap_ending(l.version, number), "ending", 0.0, cctx, thursday)


def edit_line(settings: Settings, day: date, kind: str, n: int, text: str) -> WriteResult:
    from podcat.scripts import revise as rv

    l = load(settings, day, kind)
    _editable(l)
    current = next((x for x in l.version.lines if x.n == n), None)
    if current is not None and current.text.strip() == text.strip() and current.manual:
        return WriteResult(l.meta["id"], l.ctx.scripts.index_path(l.meta["id"]), False, l.meta.get("problems") or [])
    _, cctx, thursday = _brief_and_checks(l)
    return _save(l, rv.edit_line(l.version, n, text), "edit-line", 0.0, cctx, thursday)


def link_doc(settings: Settings, day: date, kind: str, url: str) -> dict:
    if not url.startswith("https://"):
        raise ScriptError("Il link del documento deve iniziare con https://")
    l = load(settings, day, kind)
    status = l.meta["status"] if l.meta["status"] == "approved" else "review"
    meta = {**l.meta, "doc_url": url, "status": status}
    return l.ctx.scripts.set(meta["id"], summary=render_index(meta, l.story), doc_url=url, status=status)


def approve(settings: Settings, day: date, kind: str) -> dict:
    l = load(settings, day, kind)
    if l.meta["status"] == "approved":
        return l.meta
    if l.meta.get("problems"):
        raise ScriptError("Il copione non passa i controlli: correggilo prima di approvarlo.")
    fields = {"status": "approved", "approved_at": now_iso(), "approved_version": int(l.meta["current_version"])}
    meta = {**l.meta, **fields}
    meta = l.ctx.scripts.set(meta["id"], summary=render_index(meta, l.story), **fields)
    if kind == "daily":
        l.ctx.news.set_story(l.story["id"], status="used", episode=meta["id"], script=meta["id"])
    else:
        l.ctx.news.set_story(l.story["id"], weekly_episode=meta["id"])
    return meta


def reopen(settings: Settings, day: date, kind: str) -> dict:
    l = load(settings, day, kind)
    if l.meta["status"] != "approved":
        return l.meta
    meta = {**l.meta, "status": "review"}
    meta = l.ctx.scripts.set(meta["id"], summary=render_index(meta, l.story), status="review")
    if kind == "daily":
        l.ctx.news.set_story(l.story["id"], status="chosen", episode=None)
    return meta


def discard_script(ctx: Context, meta: dict, story: dict) -> dict:
    if meta["status"] == "approved":
        raise ScriptError("Il copione è approvato: non si può scartare.")
    meta = {**meta, "status": "discarded"}
    meta = ctx.scripts.set(meta["id"], summary=render_index(meta, story), status="discarded")
    if meta["kind"] == "daily":
        ctx.news.set_story(story["id"], script=None, status="candidate")
    return meta


def discard(settings: Settings, day: date, kind: str) -> dict:
    l = load(settings, day, kind)
    return discard_script(l.ctx, l.meta, l.story)
