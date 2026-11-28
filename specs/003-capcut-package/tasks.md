---
description: "Task list for spec 003: CapCut package for each episode"
---

# Tasks: CapCut package for each episode

**Input**: Design documents from `specs/003-capcut-package/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included, as in specs 001 and 002: offline pytest with the fake `TextModel` and recorded
model outputs, no paid calls. Layout, clip plan, subtitles and checks are tested first.

**Organization**: grouped by user story (US1–US7 from spec.md), in priority order: US1, US2, US6
(P1), US3, US4, US5 (P2), US7 (P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: US1–US7 from spec.md

---

## Phase 1: Setup

**Purpose**: configuration, bible additions and package skeleton

- [ ] T001 Create `src/podcat/package/__init__.py` and the empty modules listed in plan.md; add `tests/packagefixtures.py` with the approved fridge script (v4, mode A, 10 scenes), a mode B script, a mode C script held by Vinile, a Thursday script with the sting and a weekly script, plus asset records (none, and a full library of approved clips)
- [ ] T002 [P] Add `package_model: claude-haiku-5-5` and `package_effort: "off"` to `config/pricing.yaml` (research R2; Marco, 2026-11-28)
- [ ] T003 [P] Create `config/package.yaml`: reuse cap 0.30, shot → cats on screen map (research R3), expression keys (research R4), key-moment rules, cutaway length 1.2 s, title max 70, description max 5 lines, hashtags 3–6, fixed hashtag `#Podcat`, caption limits 2 lines × 32 characters
- [ ] T004 [P] Create `bible/sound.md` (theme tune, tavern ambience, allowed effects: record scratch, rimshot, cash register, boing, crowd gasp; source and licence `TBD`) and `bible/subtitles.md` (style proposal of spec Assumptions: bold rounded sans-serif, cat color with dark outline, lower-middle position above the Shorts buttons, 2 × 32); link both from `bible/prompts/README.md`
- [ ] T005 [P] Add to `docs/visual-test-plan.md`: step 6.4 also counts credits for about 200 clips a month (research R5); step 7.3 tries the caption style of `bible/subtitles.md`; new step 7.4 picks the theme tune and the ambience and writes them in `bible/sound.md`

---

## Phase 2: Foundational (blocking)

**Purpose**: models, storage, inputs and the creative call used by every story

- [ ] T006 Define Pydantic models in `src/podcat/package/models.py` for data-model.md Package version and its parts: `SceneBlock`, `CatOnScreen`, `ClipUnit`, `AssetNeed`, `NewsImagePlan`, `VoiceLine`, `SubtitlePlan`, `SoundPlan`, `PublishingKit`; and the model outputs `CreativeResult` and `RevisionResult` (research R1, R12); constrained values per data-model.md (CatOnScreen.expression, ClipUnit.source, AssetNeed.kind, AssetNeed.status, PublishingKit.platform, SubtitlePlan.check_words why)
- [ ] T007 [P] Implement `src/podcat/package/assets.py`: read `tracking/assets/*.md` (data-model.md Asset record.kind, .status, .cat, .expression, .shot, .file), keep only `approved`, find a reference image by cat and expression and a clip by shot, cat and expression; last use of a clip from existing package versions
- [ ] T008 [P] Implement `src/podcat/package/store.py`: index and version files under `tracking/packages/`, id = script id (data-model.md Package.id, .status, .script_version, .versions, .current_version, .problems, .reuse_share, .new_clips, .doc_url, .cost_usd; contracts/tracking-files.md); transitions build → `ready`, reopen → `outdated`, rebuild on a new approved script version
- [ ] T009 [P] Write `tests/unit/test_package_store.py` and `tests/unit/test_package_assets.py` (paths, versions, transitions, unknown keys and notes kept; approved-only matching, last use)
- [ ] T010 Implement `src/podcat/package/prompts.py` and `src/podcat/package/creative.py`: one call (step `package`, model from `package_model`) that receives the approved script version, story summary and sources, looks from `bible/prompts/characters.md`, mode template, clip template, style block, negative hints, sound effect list and the clip units to write; returns news image prompts, clip prompts, expressions, voice texts, effects, titles, description, hashtags, people and places; one `fix` call with the problems; ledger and cap check reused from `podcat.tracking.costs`

**Checkpoint**: inputs, storage and the paid call work offline with recorded outputs.

---

## Phase 3: User Story 1 - Scene-by-scene editing guide (P1) 🎯 MVP

**Goal**: an approved script becomes the package's scene blocks and voice sheet, checked and saved.

**Independent Test**: quickstart steps 1, 2 and 7 on the fridge script with recorded outputs.

- [ ] T011 [US1] Write `tests/unit/test_package_layout.py` first (failing): start times add up, cats on screen per shot, speaker `parla`, script reactions kept, other cats `ascolta`, a reaction outside the shot becomes a cutaway, modes B and sting are off-screen voice; then implement `src/podcat/package/layout.py` (data-model.md SceneBlock.start_s, .on_screen, .cutaways, .off_screen_voice; CatOnScreen.state)
- [ ] T012 [P] [US1] Implement the voice sheet in `src/podcat/package/layout.py`: every line in order with `capcut_voice` or "voce da scegliere" plus `voice_profile` from the character sheets, voice text from the creative call (data-model.md VoiceLine.voice, .voice_text)
- [ ] T013 [US1] Write `tests/unit/test_package_checks.py` first (failing) for coverage (every line once in blocks and voices, every scene once and in order), digits left in voice text and expression keys; then implement those checks in `src/podcat/package/checks.py` returning Italian problem strings
- [ ] T014 [US1] Implement `src/podcat/package/pipeline.py` `build()`: refuse a script not `approved` (exit 1), idempotency on the same script version, layout → creative call → checks → one fix → save v1 `ready`, or save with `problems` and exit 4
- [ ] T015 [US1] Implement `src/podcat/package/render.py`: header, scene blocks and voice sheet in the Italian, phone-friendly form of contracts/tracking-files.md (one paragraph per spoken line, prompts in code blocks)
- [ ] T016 [US1] Add `podcat package build`, `show`, `link-doc`, `list` to `src/podcat/cli.py` (contracts/cli.md, exit codes 0/1/2/4)
- [ ] T017 [US1] Write `tests/integration/test_package_build.py`: fridge script → package v1, rerun costs nothing, unapproved script refused

**Checkpoint**: MVP. Marco can follow the scene blocks in CapCut.

---

## Phase 4: User Story 2 - The news image, ready for Fotor (P1)

**Goal**: the news image section with main and alternative prompts, placement and file name.

**Independent Test**: packages for modes A, B and C (fixtures) pass the image checks.

- [ ] T018 [US2] Build the news image plan in `src/podcat/package/pipeline.py` from the script's `news_image` and the creative output (data-model.md NewsImagePlan.mode, .scene, .start_s, .comment_line, .held_by, .reference_image, .file_name); Italian CapCut placement steps per mode in `config/package.yaml`
- [ ] T019 [US2] Add the image checks to `src/podcat/package/checks.py` with tests first in `tests/unit/test_package_checks.py`: mode, scene and line equal to the script; mode C held by the speaker of that scene; style block and negative hints in both prompts; no real person's name in any English prompt (research R9)
- [ ] T020 [US2] Render the news image section in `src/podcat/package/render.py` (both prompts in code blocks, placement, file name, reference image for mode C)

---

## Phase 5: User Story 6 - Subtitles that are always right (P1)

**Goal**: the subtitle section of FR-007 (Marco, 2026-11-28).

**Independent Test**: on the fridge script, chunks within 2 × 32, the four colors, and Flanella, Fuzz, Tolmino, Salvini and line 5 in the words to check.

- [ ] T021 [US6] Write `tests/unit/test_package_subtitles.py` first (failing), then implement `src/podcat/package/subtitles.py`: style from `bible/subtitles.md`, colors from `subtitle_color` in the character sheets, chunks split at punctuation then at word boundaries within the limits, one speaker per chunk (data-model.md SubtitlePlan.style, .colors, .chunks)
- [ ] T022 [US6] Build the words-to-check list in `src/podcat/package/subtitles.py`: cat names in the lines, capitalised words, lines whose voice text differs, plus people, places and foreign words from the creative call (data-model.md SubtitlePlan.check_words)
- [ ] T023 [US6] Render the subtitle section in `src/podcat/package/render.py`, with the step "genera i sottotitoli automatici dalla traccia delle voci, poi correggi con questa lista"

---

## Phase 6: User Story 3 - Assets to reuse or to create (P2)

**Goal**: asset list and clip plan with the 30% reuse cap.

**Independent Test**: quickstart step 5 (empty library → 0% reuse and everything "da creare"; full library → reuse ≤ 30%, key moments new, least recently used first).

- [ ] T024 [US3] Write `tests/unit/test_package_clips.py` first (failing), then implement `src/podcat/package/clips.py` per research R5: merge same-shot runs, exclude branding and the mode B still, reuse only approved matching clips within 30%, generic moments first, key moments never, least recently used first; new units get prompt, start image and file name from the creative call (data-model.md ClipUnit.source, .asset_id, .prompt, .start_image, .file_name, .key_moment; Package.reuse_share, .new_clips)
- [ ] T025 [US3] Build the asset list in `src/podcat/package/pipeline.py` (data-model.md AssetNeed.kind, .status): reference images and set pieces from `bible/prompts/` as "da creare" with prompt, tool and reference, or "già pronto" with file
- [ ] T026 [US3] Add the reuse-cap check (fail over 30%) to `src/podcat/package/checks.py` and render the asset table and clip plan in `src/podcat/package/render.py` (reuse share, number and seconds of new clips)
- [ ] T027 [P] [US3] Implement `src/podcat/package/sound.py` (FR-019, research R7): ambience under everything, theme under the first and last block, effects from the creative call with their scene; "sigla da scegliere" while `bible/sound.md` says `TBD`; render the sound section (data-model.md SoundPlan.theme, .ambience, .effects)

---

## Phase 7: User Story 4 - Publishing kit (P2)

**Goal**: titles, description with sources, hashtags, AI reminder and final checklist.

**Independent Test**: fridge package has three titles ≤ 70 characters, both sources with links, `#Podcat`, the AI line and the checklist.

- [ ] T028 [US4] Build the publishing kit in `src/podcat/package/pipeline.py` (data-model.md PublishingKit.platform, .titles, .sources, .hashtags, .ai_disclosure): sources from the story record, fixed AI line, Shorts for daily and regular video for weekly
- [ ] T029 [US4] Add the kit checks to `src/podcat/package/checks.py` with tests first: title length, description lines, every source outlet present, 3–6 hashtags with `#Podcat`
- [ ] T030 [US4] Render the publishing kit and the final checklist of FR-009 in `src/podcat/package/render.py`

---

## Phase 8: User Story 5 - Changes by comment (P2)

**Goal**: comment rounds change only the allowed parts; reopening the script outdates the package.

**Independent Test**: quickstart steps 4 and 6.

- [ ] T031 [US5] Implement `src/podcat/package/revise.py` and `pipeline.revise()`: comments file with `part` (contracts/cli.md), one call (step `package-revision`) returning changes only for the named parts, merge, checks, new version, answers; fixed answer for comments on a line's text; the same file on the same version applied once
- [ ] T032 [US5] Add `podcat package revise` to `src/podcat/cli.py`; in `src/podcat/scripts/pipeline.py` `reopen()` mark the package `outdated` and print it (data-model.md Package.status)
- [ ] T033 [US5] Write `tests/integration/test_package_revise.py`: image and title comments → only those parts change; line comment → no change and the fixed answer; reopen → `outdated`; re-approve → `build` makes v2

---

## Phase 9: User Story 7 - Weekly episode and Thursday slot (P3)

**Goal**: weekly packages and the Thursday sting block.

**Independent Test**: quickstart step 8 with the fixtures.

- [ ] T034 [US7] Thursday: first block is the gnocchi sting with its asset, 2–3 s and the title "Giovedì buone notizie" with "Giovedì" and "gnocchi" in red (FR-010), in `src/podcat/package/layout.py` and `render.py`; slot name in titles and description
- [ ] T035 [US7] Weekly: `--kind weekly` end to end (about 2 minutes, all four cats, about 20–25 clip units), test in `tests/integration/test_package_build.py`

---

## Phase 10: Polish

- [ ] T036 Update `docs/routines/script-review.md`: after «approvato» run `podcat package build`, publish `podcat package show` as a Claude Doc titled `Podcat – Pacchetto CapCut <giorno> <data>`, `link-doc`, commit and push `tracking/`; comment keywords for packages; exit 4 handling
- [ ] T037 [P] Update `BACKLOG.md` (B-015 done when merged), `docs/decisions.md` if anything changes during implementation, and `README.md` commands
- [ ] T038 Run the full offline suite (`uv run pytest`), then quickstart step 1 for real on the fridge script (cost under 0.03 USD), publish the first real package document and record the run in `quickstart.md`
- [ ] T039 Open the pull request to `main` with the spec 003 work

---

## Dependencies

- Setup (T001–T005) → Foundational (T006–T010) → US1 (T011–T017).
- US2, US6, US3, US4 depend on US1's pipeline and render (T014, T015) and can then run in any order;
  US5 needs US2–US4 parts to revise; US7 needs US1 and US3.
- Polish after all stories; T038 needs the API key (cloud environment has `PODCAT_ANTHROPIC_API_KEY`).

## Parallel examples

- Setup: T002, T003, T004, T005 together.
- Foundational: T007, T008, T009 together, then T010.
- After US1: US6 (T021–T023) beside US3's sound task T027.

## Implementation strategy

1. MVP = Phases 1–3: Marco gets the scene guide and voice sheet for the fridge script.
2. Add US2 and US6 (image and subtitles, both P1), then US3 and US4, then US5, then US7.
3. One commit per phase, a short report to Marco after each phase, as for spec 002; the real run
   (T038) uses Haiku and is compared with Sonnet only if the titles are flat.
