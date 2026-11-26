# Implementation Plan: Daily news gathering and verification

**Branch**: `001-news-gathering` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-news-gathering/spec.md` (approved 2026-11-26)

## Summary

A `podcat` command line tool that, once a day, reads the approved RSS feeds, groups items about the
same event with one cheap language-model call, verifies each story with a deterministic
two-groups rule (agency wires counted once, satire never), writes an Italian summary with
importance and comic potential ratings in a second cheap call, and saves a 3–5 story shortlist
plus story records, a run log and a cost ledger as Markdown in `tracking/`. Thursdays use only
positive stories from the last 7 days, one reliable source each; Saturdays build the weekly shortlist from the week's stories. Claude publishes
each shortlist as a commentable document from the project chat; Marco picks the story there.
Every morning at 07:00 a scheduled cloud session runs the gather, pushes the results to GitHub and
publishes the document, so Marco's computer can stay off.

## Technical Context

**Language/Version**: Python 3.12+ (Marco's machine: 3.14)

**Primary Dependencies**: Typer (CLI), Pydantic (models, validation), httpx (HTTP), feedparser
(RSS/Atom), PyYAML (front matter, config), python-dotenv (settings), anthropic (official SDK)

**Storage**: Markdown + YAML front matter under `tracking/`; config in `config/`; intermediate JSON
cache in `$PODCAT_ASSETS_DIR/cache/news/` (outside git)

**Testing**: pytest; offline fixtures for feeds and recorded model outputs; no paid calls in tests

**Target Platform**: Claude Code cloud sessions (Linux container, repo cloned from GitHub), started
by a daily 07:00 Europe/Rome schedule or from the project chat; also Marco's Linux machine

**Project Type**: single-project CLI

**Performance Goals**: full daily run in under 5 minutes (SC-001), dominated by ~80 feed fetches
done concurrently

**Constraints**: ≤0.10 USD per daily run (estimate ~0.01 USD), 50 USD monthly cap across services,
idempotent steps, no article text stored, Italian editorial text, English code

**Scale/Scope**: ~80 sources, ~300–600 items per day, 3–5 candidates per day, one user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Editorial value | Comic potential rating and own-words summaries feed original scripts; follow-ups detected so stories are not repeated | pass |
| II. Human approval | Marco picks the story; nothing moves on without his pick | pass |
| III. Content safety | Two-group verification, source URLs on every story, excluded topics, only headlines/links/own summaries stored, sensitivity flags for health/legal/finance, neutral politics | pass |
| IV. Consistency | Not affected (no characters or assets in this feature) | n/a |
| V. Cost | Cheapest model (Haiku 5.5), per-call ledger, refusal before exceeding the cap, provider behind a `TextModel` interface | pass |
| VI. Simplicity | One package, Markdown tracking, no database, idempotent CLI steps, cache outside git | pass |
| Settings | Italian channel text, English code, `tracking/`, `PODCAT_ASSETS_DIR`, `.env` secrets, news-sources rules | pass |

Post-design re-check: pass, no violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-news-gathering/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── tracking-files.md
└── tasks.md             # next step (/speckit-tasks)
```

### Source Code (repository root)

```text
pyproject.toml           # uv project, entry point `podcat`
config/
├── sources.yaml         # approved sources, groups, roles, feeds
├── agencies.yaml        # agency credit patterns
└── pricing.yaml         # model prices for the cost ledger
src/podcat/
├── cli.py               # Typer app: sources, news, costs
├── settings.py          # .env loading, paths
├── tracking/
│   ├── frontmatter.py   # read/write Markdown + YAML
│   └── costs.py         # ledger, cap check
├── llm/
│   ├── base.py          # TextModel interface
│   └── anthropic_model.py
└── news/
    ├── sources.py       # load and check sources, autodiscovery
    ├── fetch.py         # concurrent feed fetch, window filter
    ├── prefilter.py     # duplicates, clickbait word list
    ├── triage.py        # model call 1: grouping, topics, positivity
    ├── verify.py        # two-groups rule, agencies, roles, Thursday rule
    ├── editorial.py     # model call 2: summary, ratings, flags, follow-ups
    ├── shortlist.py     # build, pick, reject, link-doc
    ├── weekly.py        # Saturday shortlist
    └── store.py         # stories, shortlists, run logs, cache
tests/
├── fixtures/            # saved feeds, recorded model outputs
├── unit/
└── integration/         # end-to-end gather with fixtures, no network
```

**Structure Decision**: single project with `src/` layout. Shared parts (`tracking/`, `llm/`,
`settings.py`) are built here once and reused by the script feature (spec 002).

## Spec updates made during planning

- FR-002: the weekly run uses the week's daily runs plus the last 24 hours, because RSS feeds keep
  only one or two days of items (research R8).

- FR-018 and SC-007: automatic daily start at 07:00 in the cloud (Marco, 2026-11-26; backlog B-008
  brought forward). Constitution amended to v1.3.0 (runs in the cloud).

## Complexity Tracking

No constitution violations.
