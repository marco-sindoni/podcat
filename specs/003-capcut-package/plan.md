# Implementation Plan: CapCut package for each episode

**Branch**: `003-capcut-package` (work pushed on `claude/project-thread-p5j6ca`) | **Date**: 2026-11-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-capcut-package/spec.md` (approved 2026-11-28)

**Plan status**: approved by Marco on 2026-11-28 ("aggiorna il piano e i task"): D1 Haiku 5.5 as default model; D2 CapCut credits measured in the visual test session (B-012) before the first real package; subtitles = CapCut auto-captions plus correction (research R14)

## Summary

A new `podcat package` command group turns an approved script into the CapCut package. Most of the
package is assembled by plain code from the approved script version, the story, the bible and the
asset records: scene blocks with start times, cats on screen per shot, reactions, the subtitle section
(style, colors, caption chunks, words to check; research R14), the asset list, the clip plan with the 30% reuse cap, the sound plan, the final
checklist. One cheap model call (Haiku 5.5, configurable) writes the creative parts: the two Fotor
prompts for the news image, the CapCut image-to-video prompt for each new clip, the expression of
each cat on screen mapped to the bible's list, the spoken form of numbers and names for the voices,
the sound effects to use, three titles, the description and hashtags. Deterministic checks then
verify coverage (every line and scene once), the image mode, the reuse cap, title and hashtag
limits, sources in the description and no real people's names in English prompts; one automatic
fix call runs if a check fails. The package is saved under `tracking/packages/` as an index plus one
file per version, published by Claude as a commentable Claude Doc, and revised from comments like
scripts. It is built right after "approvato", in the same cloud routine.

## Technical Context

**Language/Version**: Python 3.12+ (same project)

**Primary Dependencies**: existing only (Typer, Pydantic, PyYAML, python-dotenv, anthropic)

**Storage**: Markdown + YAML front matter: `tracking/packages/<script-id>.md` (index) and
`tracking/packages/<script-id>/v<N>.md` (versions); asset records `tracking/assets/<asset-id>.md`
(minimal schema defined here, owned later by spec 004); sound plan in `bible/sound.md` (new);
settings in `config/package.yaml` (new); model in `config/pricing.yaml` (`package_model`)

**Testing**: pytest; recorded model outputs through the existing fake `TextModel`; no paid calls

**Target Platform**: Claude Code cloud sessions and Marco's Linux machine

**Project Type**: single-project CLI (extends `podcat`)

**Performance Goals**: package ready within 10 minutes of approval (SC-001); one call of about 30 s

**Constraints**: under 0.03 USD per package, 0.02 USD per comment round, 2 USD/month (SC-006);
reused clips at most 30% of duration (FR-018); 50 USD cap shared; idempotent; Italian content,
English code and prompts

**Scale/Scope**: one reel package a day, one weekly package, 0–2 revision rounds; one user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | How the plan complies | Status |
| --- | --- | --- |
| I. Editorial value | A dedicated news image per episode in the script's mode; mostly new clips per episode (reuse capped at 30%); least recently used clips chosen when reusing | pass |
| II. Human approval | Built only from `approved` scripts; never rewrites lines; checklist ends with Marco's approval of the final cut | pass |
| III. Content safety | Prompts forbid real faces, logos, brands (style block + negative hints + check on people's names); sources credited in the description; "AI use" reminder; theme, ambience and effects only from sources licensed for YouTube | pass |
| IV. Consistency | Looks, voices, subtitle colors from the bible; every new clip starts from an approved reference image; theme and ambience fixed once in `bible/sound.md` | pass |
| V. Cost | Most of the package is plain code; one Haiku call (~0.003 USD); ledger and cap check reused; model configurable | pass |
| VI. Simplicity | No new dependencies; Markdown tracking; idempotent commands; reuse computed from existing package files, no extra usage log | pass |
| Settings | 9:16 in the checklist; CapCut auto-captions in phase 1 (no SRT); YouTube only; assets outside git (only suggested file names in the package) | pass |

Post-design re-check: pass, no violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/003-capcut-package/
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
├── pricing.yaml         # + package_model, package_effort
└── package.yaml         # reuse cap, shot → cats map, expression list, title/hashtag limits, fixed hashtag
bible/
├── sound.md             # new: theme tune, ambience, sound effect list (TBD until B-012)
├── subtitles.md         # new: caption style (font, size, outline, safe-area position, 2 × 32 chars)
└── prompts/             # read: style block, negative hints, mode templates, clip template
src/podcat/
├── cli.py               # + `package` command group
├── scripts/pipeline.py  # reopen → package outdated
└── package/
    ├── models.py        # Pydantic: SceneBlock, CatOnScreen, AssetNeed, ClipPlan, NewsImagePlan, VoiceLine, PublishingKit, model outputs
    ├── assets.py        # read tracking/assets/, match reference images and library clips
    ├── layout.py        # scene blocks: start times, cats on screen from shot + seating, reactions, captions
    ├── clips.py         # merge same-shot runs, pick reused clips (LRU, ≤30%), list new clips
    ├── sound.py         # ambience, theme under first/last scene, effects
    ├── subtitles.py     # caption chunks, colors, words to check
    ├── prompts.py       # system and user prompts for the creative call and the revision
    ├── creative.py      # the one paid call (+ fix)
    ├── checks.py        # coverage, mode, reuse cap, limits, sources, names in prompts
    ├── revise.py        # comments → changes to allowed parts only
    ├── store.py         # index + version files, status ready/outdated
    ├── render.py        # Italian document text (phone-friendly, prompts in code blocks)
    └── pipeline.py      # build / show / revise / link-doc / list
docs/routines/
└── script-review.md     # + after approval: build and publish the package
tests/
├── unit/                # layout, clips, checks, assets, render
└── integration/         # approve → build → revise → reopen (outdated) with fakes
```

**Structure Decision**: a new `package` package beside `news` and `scripts`, reusing `tracking/`,
`llm/`, `settings.py` and the script store.

## Changes to spec 002 made by this plan

- `podcat script reopen` marks the script's package `outdated` (FR-013).
- The script routine gains a step after "approvato": build and publish the package.
