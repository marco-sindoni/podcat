---
description: "Task list for spec 002: script writing for the four cats"
---

# Tasks: Script writing for the four cats

**Input**: Design documents from `specs/002-script-writing/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included, as in spec 001: offline pytest with the fake `TextModel` and recorded model
outputs, no paid calls. The checks (structure, words, reactions, rotation) are tested first.

**Organization**: grouped by user story (US1–US6 from spec.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: US1–US6 from spec.md

---

## Phase 1: Setup

**Purpose**: configuration, bible additions and package skeleton

- [ ] T001 Create package skeleton `src/podcat/scripts/__init__.py` and empty modules listed in plan.md; add `tests/scriptfixtures.py` with a picked story (comico, the 2026-11-27 fridge story), a pungente story, a Thursday story and a weekly pick
- [ ] T002 [P] Add `script_models` (`room: claude-haiku-5-5`, `head_writer: claude-sonnet-5-5`, `revision: claude-sonnet-5-5`) to `config/pricing.yaml`; the model of each step is read from there on every run, so changing one line switches model (data-model.md Configuration; Marco, 2026-11-27)
- [ ] T003 [P] Create `config/scripts.yaml` with word limits, targets, tolerances, speaking rates, pause, fixed shot durations, Thursday formula, repeat window and tics per cat (data-model.md Configuration, research R4, R8, R9)
- [ ] T004 [P] Create `bible/shots.md` with the fixed shot ids of research R11 (Italian description per shot) and link it from `bible/characters/README.md`

---

## Phase 2: Foundational (blocking)

**Purpose**: models, storage, timing and checks used by every story

- [ ] T005 Define Pydantic models in `src/podcat/scripts/models.py`: `Line`, `Reaction`, `Scene`, `NewsImage`, `Ending`, `RoomResult`, `HeadWriterResult`, `FixResult`, `RevisionResult` (data-model.md Script version.lines, .scenes, .news_image, .endings; Model outputs); cat ids restricted to `flanella`, `fuzz`, `vinile`, `feedback`; mode to `A`, `B`, `C`
- [ ] T006 [P] Implement `src/podcat/scripts/bible.py`: load the four character sheets (role, personality, tics, evolution log), the shot ids from `bible/shots.md` and `config/scripts.yaml`
- [ ] T007 [P] Implement `src/podcat/scripts/timing.py`: word count (sting excluded) and line, scene and total durations from speaking rates (research R4; data-model.md Script version.words, .duration_s, Script version.scenes.duration_s)
- [ ] T008 Implement `src/podcat/scripts/store.py`: script id, index and version files, `versions` list, status transitions and story effects (`story.script`, `status`, `episode`) (data-model.md Script index.id, .status, .versions, .current_version, .cost_usd; contracts/tracking-files.md)
- [ ] T009 [P] Write `tests/unit/test_script_timing.py` and `tests/unit/test_script_store.py` (word count, durations, transitions draft → review → approved → review, discarded, unknown keys and notes kept)
- [ ] T010 Write `tests/unit/test_script_checks.py` first (failing), covering every check of research R3, then implement `src/podcat/scripts/checks.py` returning a list of Italian problem strings

**Checkpoint**: storage, timing and checks work offline.

---

## Phase 3: User Story 1 - Daily reel script from the picked story (P1) 🎯 MVP

**Goal**: the picked story becomes a checked reel script (two passes) saved in `tracking/scripts/`.

**Independent Test**: quickstart steps 1–2 with recorded outputs; with the real API on the fridge story.

- [ ] T011 [US1] Write the Italian system prompts in `src/podcat/scripts/prompts.py`: writers' room (two drafts, two angles, cast rules, all four speak by default, reactions for silent cats), head writer (choose or merge, rewrite, 2 alternative endings, notes, content rules of FR-007, flags of research R9), fix (list of problems); the story summary is the only news input
- [ ] T012 [P] [US1] Implement `src/podcat/scripts/room.py` (call 1, step `room`, model from `script_models.room`)
- [ ] T013 [P] [US1] Implement `src/podcat/scripts/headwriter.py` (call 2, step `head-writer`; fix call, step `fix`, at most once) with the last 7 scripts' openings and closings (research R8)
- [ ] T014 [US1] Implement `src/podcat/scripts/rotation.py` (previous non-discarded script, allowed modes; research R7; data-model.md Script index.news_image_mode, .previous_script)
- [ ] T015 [US1] Implement `src/podcat/scripts/pipeline.py` `write()`: find the picked story, idempotency, room → head writer → timing → checks → one fix → save v1 (`draft`), or save with `problems` and exit 4 (data-model.md Script index.problems); budget check reused from the ledger
- [ ] T016 [US1] Implement `src/podcat/scripts/render.py` with the Italian document text of contracts/tracking-files.md (numbered lines, scenes table with reactions, image, endings, notes, closing instructions)
- [ ] T017 [US1] Add the `script` command group to `src/podcat/cli.py`: `write`, `show`, `list` (contracts/cli.md, exit codes 0/1/2/4)
- [ ] T018 [US1] Write `tests/integration/test_script_write.py`: write with recorded outputs, idempotent rerun with no ledger entry, failed checks → fix call → success, failed fix → exit 4, budget cap → exit 2 with no files

**Checkpoint**: MVP. Run once with the real API on the fridge story and check cost < 0.05 USD.

---

## Phase 4: User Story 2 - Review by comments until approval (P1)

**Goal**: comments produce new versions; endings swap; approval locks.

**Independent Test**: quickstart steps 3–6, 8.

- [ ] T019 [US2] Implement `src/podcat/scripts/revise.py`: apply `RevisionResult` (only commented lines plus listed coherence changes), keep `manual` lines, refuse comments files already applied, `ending N` swap, `edit-line` (data-model.md Script version.answers, .coherence_changes, .lines.manual)
- [ ] T020 [US2] Add the revision prompt to `src/podcat/scripts/prompts.py` and the call (step `revision`, model from `script_models.revision`); rerun checks after the revision
- [ ] T021 [US2] Add `link-doc`, `revise`, `ending`, `edit-line`, `approve`, `reopen`, `discard` to `src/podcat/cli.py` and `pipeline.py` (data-model.md Script index.doc_url, .approved_at, .approved_version; approved scripts refuse changes until `reopen`)
- [ ] T022 [US2] Change `src/podcat/news/shortlist.py` pick: a `draft` or `review` script of the old story is discarded and the story set back to `candidate`; an approved one still blocks (plan.md "Changes to spec 001"); extend `tests/unit/test_pick.py`
- [ ] T023 [US2] Write `tests/integration/test_script_review.py`: two anchored comments change only those lines, rewrite with `--new-draft`, ending swap at no cost, manual edit kept, approve → story `used`, revise refused until reopen
- [ ] T024 [US2] Write the routine `docs/routines/script-review.md` (after a pick run `script write`, publish the Claude Doc, store the link, read comments into the YAML file, keywords "approvato", "finale N", "rifalla da capo", "più leggera/pungente", commit and push tracking files) and link it from `docs/routines/daily-news.md` step 7

**Checkpoint**: Marco can review a full script from his phone.

---

## Phase 5: User Story 5 - Comic or pungente register (P1)

**Goal**: the script follows the story's tone.

**Independent Test**: quickstart step 10.

- [ ] T025 [US5] Add the `comico` and `pungente` register blocks to the writers' room, head writer and revision prompts in `src/podcat/scripts/prompts.py`; record `tone` and allow `--tone` on `revise` (data-model.md Script index.tone)
- [ ] T026 [US5] Test in `tests/integration/test_script_write.py`: the prompt sent for a pungente story contains the pungente block; `revise --tone comico` updates the index

---

## Phase 6: User Story 3 - Scenes and news image placement (P2)

**Goal**: scenes, reactions and the news image respect the shot list and rotation.

**Independent Test**: quickstart step 7.

- [ ] T027 [US3] Extend `checks.py` and its tests for shot ids from `bible/shots.md`, mode C held by the speaking cat, adjacent seats in two-shots, tolerance of scene durations (data-model.md Script version.news_image.held_by, .subject)
- [ ] T028 [US3] Handle a comment asking for a different mode in `revise.py`: allowed only if it still differs from the previous script, otherwise the answer explains why; test in `tests/integration/test_script_review.py`

---

## Phase 7: User Story 4 - "Giovedì buone notizie" (P2)

**Goal**: Thursday scripts open with the formula over the gnocchi sting, in a warm tone.

**Independent Test**: quickstart step 9.

- [ ] T029 [US4] Add the Thursday block to the prompts and the `sting-gnocchi` first scene plus the formula check to `checks.py` (data-model.md Script index.good_news_thursday); tests with the Thursday fixture

---

## Phase 8: User Story 6 - Weekly episode script (P3)

**Goal**: the Saturday pick becomes a 2-minute script with all four cats.

**Independent Test**: quickstart step 11.

- [ ] T030 [US6] Support `--kind weekly` in `pipeline.py` and the prompts (280–320 words, at least two lines per cat, cold open, the reel's lines passed when the story was used in a reel; research R12); tests in `tests/integration/test_script_write.py`
- [ ] T031 [US6] Add the Saturday step to `docs/routines/script-review.md` (weekly pick → weekly script the same day)

---

## Phase 9: Polish

- [ ] T032 [P] Update `specs/001-news-gathering/contracts/cli.md` (pick change) and `specs/001-news-gathering/data-model.md` (story `script` field)
- [ ] T033 [P] Update `BACKLOG.md` (B-014 done when quickstart passes) and `docs/decisions.md` if implementation changes a choice
- [ ] T034 Run the whole quickstart with the real API on the 2026-11-27 fridge story; record words, duration, cost and Marco's verdict in `specs/002-script-writing/quickstart.md`

---

## Dependencies

- Phase 1 → Phase 2 → US1 (MVP) → US2 → US5, US3, US4 (any order) → US6 → Polish.
- US2 needs US1 (a script to review). US5, US3 and US4 touch prompts and checks written in US1.
- T022 changes spec 001 code; run the spec 001 tests after it.

## Parallel examples

- Phase 1: T002, T003, T004 together.
- Phase 2: T006, T007 together, then T008; T009 after T007 and T008.
- US1: T012 and T013 together after T011.

## Implementation strategy

1. Phases 1–3, then a first real script on the fridge story: Marco reads it before anything else is
   built (MVP check of tone and jokes).
2. Phase 4, so the real review loop works from the phone.
3. Phases 5–8, then the polish and the full quickstart.
