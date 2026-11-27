# Implementation Plan: Script writing for the four cats

**Branch**: `002-script-writing` | **Date**: 2026-11-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-script-writing/spec.md` (approved 2026-11-27)

## Summary

A new `podcat script` command group turns the story Marco picked into an Italian script for the
four cats. A cheap "writers' room" call (Haiku) writes two drafts with different comic angles; a
"head writer" call (Sonnet) picks the stronger one, rewrites it, adds two alternative endings and
notes. Deterministic code then checks structure, word count, timing, reactions of silent cats and
the news image mode rotation, and asks the head writer for one fix if a check fails. The script is
saved under `tracking/scripts/` as an index file plus one file per version. Claude publishes each
version as a commentable Claude Doc from the project chat; Marco's comments go back to
`podcat script revise`, which changes only the commented lines. "finale N" swaps an ending at no
cost; "approvato" locks the script and marks the story as used. The routine runs in the cloud right
after Marco's pick, like the news routine.

## Technical Context

**Language/Version**: Python 3.12+ (same project as spec 001)

**Primary Dependencies**: existing ones only (Typer, Pydantic, PyYAML, python-dotenv, anthropic)

**Storage**: Markdown + YAML front matter: `tracking/scripts/<script-id>.md` (index) and
`tracking/scripts/<script-id>/v<N>.md` (versions); config in `config/scripts.yaml`; shot list in
`bible/shots.md`

**Testing**: pytest; recorded model outputs through the existing fake `TextModel`; no paid calls

**Target Platform**: Claude Code cloud sessions (as spec 001) and Marco's Linux machine

**Project Type**: single-project CLI (extends `podcat`)

**Performance Goals**: script ready within 10 minutes of the pick (SC-001); the two calls take
about 1 minute

**Constraints**: daily script under 0.05 USD, revision under 0.03 USD, under 5 USD/month
(SC-005); 50 USD cap shared with news; idempotent steps; Italian content, English code

**Scale/Scope**: one reel script a day, one weekly script, 1–3 revision rounds each; one user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Editorial value | Two passes (writers' room + head writer), anti-repetition against the last 7 scripts, one news image per script with mode rotation recorded | pass |
| II. Human approval | Script stays `review` until Marco writes "approvato"; only `approved` scripts are usable by spec 003 | pass |
| III. Content safety | Story summary is the only news input (no source text); prompt rules + head writer check on advice, partisan politics, vulnerable groups, Thursday targets; story flags passed to the prompts | pass |
| IV. Consistency | Characters read from `bible/characters/`; fixed shot list added to the bible (`bible/shots.md`, approved with this plan) | pass |
| V. Cost | Haiku for drafts, Sonnet only for the head writer and revisions, ending swap and approval free, per-call ledger and cap check reused, models configurable | pass |
| VI. Simplicity | No new dependencies; Markdown tracking; every command idempotent; checks are plain code | pass |
| Settings | Italian channel text, English code, `tracking/`, 9:16 not affected, `.env` secrets | pass |

Post-design re-check: pass, no violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/002-script-writing/
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
config/
├── pricing.yaml         # + script_models (writer, head_writer, revision)
└── scripts.yaml         # word limits, speaking rates per cat, tolerances, shot ids
bible/
└── shots.md             # fixed shot list (new, approved with this plan)
src/podcat/
├── cli.py               # + `script` command group
├── news/shortlist.py    # pick: discard a non-approved script of the old story
└── scripts/
    ├── models.py        # Pydantic: Line, Scene, NewsImage, Ending, Draft, results
    ├── bible.py         # load character sheets, shot list, slot formula
    ├── prompts.py       # Italian system prompts: writers' room, head writer, revision, fix
    ├── room.py          # call 1: two drafts (Haiku)
    ├── headwriter.py    # call 2: final draft, 2 alternative endings, notes (Sonnet)
    ├── checks.py        # structure, word count, reactions, mode, Thursday, advice keywords
    ├── timing.py        # durations from words and speaking rates
    ├── rotation.py      # pick the news image mode from the previous script
    ├── revise.py        # apply comments, ending swap, manual line edits
    ├── store.py         # index + version files, status transitions
    ├── render.py        # Italian document text for the Claude Doc
    └── pipeline.py      # write / revise / approve orchestration
docs/routines/
└── script-review.md     # cloud routine: after pick, publish, comments, approval
tests/
├── unit/                # checks, timing, rotation, revise, store
└── integration/         # write → revise → ending → approve with fakes
```

**Structure Decision**: a new `scripts` package beside `news`, reusing `tracking/`, `llm/` and
`settings.py` from spec 001.

## Changes to spec 001 made by this plan

- `podcat news pick` on a different candidate now discards a script still in `draft` or `review`
  for the old story (spec 002, User Story 2 scenario 4); an approved script still blocks it.
- Stories get a `script` field (script id) while a script exists; `status: used` and `episode` are
  set on approval, as spec 001's data model expected.
