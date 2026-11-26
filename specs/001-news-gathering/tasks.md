---
description: "Task list for spec 001: daily news gathering and verification"
---

# Tasks: Daily news gathering and verification

**Input**: Design documents from `specs/001-news-gathering/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included. The plan requires an offline pytest suite (fixtures for feeds and recorded
model outputs) so tests cost nothing; the verification rule and the cost cap are tested first.

**Organization**: Tasks are grouped by user story so each story can be built and checked on its
own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: US1–US4 from spec.md

---

## Phase 1: Setup

**Purpose**: Python project, configuration and test scaffolding

- [X] T001 Create `pyproject.toml` (uv project `podcat`, Python >=3.12, `src/` layout, script `podcat = "podcat.cli:app"`, dependencies typer, pydantic, httpx, feedparser, pyyaml, python-dotenv, anthropic; dev dependency pytest) and run `uv lock`
- [X] T002 Create package skeleton per plan.md: `src/podcat/__init__.py`, `src/podcat/{tracking,llm,news}/__init__.py`, `tests/{unit,integration,fixtures}/`, `tests/conftest.py` with a temporary repo root and assets dir fixture
- [X] T003 [P] Create `config/sources.yaml` from `docs/news-sources.md` with every source: `id`, `name`, `category`, `group`, `role`, `feeds` (best-known URL or empty), `manual` (see data-model.md Source)
- [X] T004 [P] Create `config/agencies.yaml` with credit patterns for ANSA, AGI, Adnkronos, Reuters, AP, AFP, LaPresse, Dire (data-model.md Source / agency patterns)
- [X] T005 [P] Create `config/pricing.yaml` with `claude-haiku-5-5` input 0.10 and output 0.50 USD per million tokens, and the default news model id
- [X] T006 [P] Add `.gitignore` entries for `.venv/`, `__pycache__/`, `.pytest_cache/`; update `.env.example` comments for cloud use

---

## Phase 2: Foundational (blocking)

**Purpose**: shared pieces used by every story and reused by spec 002

- [X] T007 Implement settings in `src/podcat/settings.py`: load `.env` if present, read `PODCAT_ASSETS_DIR` (default a temp dir) and `ANTHROPIC_API_KEY`, repo root detection, Europe/Rome timezone helper
- [X] T008 [P] Implement front matter read/write in `src/podcat/tracking/frontmatter.py` (preserve unknown keys and hand-written body, per contracts/tracking-files.md) with tests in `tests/unit/test_frontmatter.py`
- [X] T009 [P] Write cost ledger tests in `tests/unit/test_costs.py`: estimate, refuse when total + estimate > cap, record actual usage, new month file
- [X] T010 Implement cost ledger in `src/podcat/tracking/costs.py` (data-model.md Cost ledger: `month`, `cap_usd`, `total_usd`, rows) with `BudgetExceeded` error
- [X] T011 [P] Define `TextModel` interface in `src/podcat/llm/base.py`: `parse(system, user, schema, max_tokens) -> (parsed, usage)`; plus a `FakeModel` in `tests/fakes.py` that returns recorded outputs from `tests/fixtures/`
- [X] T012 Implement `src/podcat/llm/anthropic_model.py` with the official SDK (`messages.parse` with Pydantic schema), cost check through `tracking/costs.py` before every call and recording after it
- [X] T013 Create the Typer app in `src/podcat/cli.py` with groups `sources`, `news`, `costs`, Italian messages and exit codes from contracts/cli.md; implement `podcat costs show`

**Checkpoint**: `uv run pytest` passes; `uv run podcat costs show` prints an empty month.

---

## Phase 3: User Story 1 – Daily shortlist of verified stories (P1) 🎯 MVP

**Goal**: one command produces 3–5 verified candidates with sources, summary, importance and comic potential.

**Independent test**: quickstart.md Scenarios 1 and 2, and the integration test below with fixtures.

### Tests for US1

- [X] T014 [P] [US1] Save fixture feeds in `tests/fixtures/feeds/` (at least 6 outlets from 4 groups, an agency wire republished by two outlets, a satire item, a crime item, a clickbait headline, an item outside the 24 h window)
- [X] T015 [P] [US1] Write verification rule tests in `tests/unit/test_verify.py`: two groups needed, same agency counts once, satire never counts, confirmation-only sources cannot be the only starting source (data-model.md Source.role, Story.effective_groups)
- [X] T016 [P] [US1] Write prefilter tests in `tests/unit/test_prefilter.py`: duplicate URLs, clickbait word list, time window in Europe/Rome
- [X] T017 [P] [US1] Write end-to-end test in `tests/integration/test_gather.py`: gather with fixture feeds and `FakeModel` creates shortlist, stories, run log and one cost row; a second run changes nothing and adds no cost row

### Implementation for US1

- [X] T018 [US1] Implement source loading in `src/podcat/news/sources.py` (validate `config/sources.yaml` against data-model.md Source fields)
- [X] T019 [US1] Implement `podcat sources check [--write]` in `src/podcat/news/sources.py` and `cli.py`: fetch each feed, autodiscover from the home page when broken, set `manual`, `last_check` (research R1)
- [X] T020 [US1] Implement concurrent fetch in `src/podcat/news/fetch.py` (httpx + feedparser, 10 s timeout per feed, failures collected, window filter, agency detection from `config/agencies.yaml`); items cached as data-model.md Feed item
- [X] T021 [P] [US1] Implement `src/podcat/news/prefilter.py` (duplicates, clickbait list)
- [X] T022 [US1] Implement triage call in `src/podcat/news/triage.py`: Pydantic schema data-model.md Model outputs / Triage, Italian prompt with the excluded topics from docs/news-sources.md, output cached
- [X] T023 [US1] Implement verification in `src/podcat/news/verify.py` (research R4) making T015 pass
- [X] T024 [US1] Implement editorial call in `src/podcat/news/editorial.py`: schema data-model.md Model outputs / Editorial (Story.title, Story.summary, Story.importance, Story.comic_potential, Story.flags, Story.follow_up_of), recent used stories passed in for follow-up and duplicate detection, neutral politics instruction
- [X] T025 [US1] Implement storage in `src/podcat/news/store.py`: write Story, Shortlist and Run log files (data-model.md Story, Shortlist, Run log) with the Italian table body; read existing ones
- [X] T026 [US1] Implement selection in `src/podcat/news/shortlist.py`: 3–5 candidates ordered by importance with category balance (FR-008), warning when fewer than 3 (Shortlist.warning)
- [X] T027 [US1] Implement `podcat news gather [--date] [--refresh]` and `podcat news show` in `src/podcat/cli.py`, idempotent per FR-012, printing the shortlist path at the end
- [X] T028 [US1] On Marco's machine or in the cloud with network: run `podcat sources check --write`, fix or mark `manual` the failing sources, commit `config/sources.yaml`
- [ ] T029 [US1] First real run: `podcat news gather`; Marco checks the shortlist against SC-002 and SC-003

**Checkpoint**: MVP. The daily shortlist works end to end.

---

## Phase 4: User Story 2 – Marco picks the story (P1)

**Goal**: pick, change or reject from the document; the choice is written to the files.

**Independent test**: quickstart.md Scenario 3.

- [X] T030 [P] [US2] Write tests in `tests/unit/test_pick.py`: pick N, change pick, unpick blocked when a script exists, reject then refresh excludes rejected stories (data-model.md Story.status transitions, Shortlist.picked)
- [X] T031 [US2] Implement pick, unpick, reject and link-doc in `src/podcat/news/shortlist.py`
- [X] T032 [US2] Add `podcat news pick|unpick|reject|link-doc` to `src/podcat/cli.py`
- [X] T033 [US2] Write the publishing routine in `docs/routines/daily-news.md`: steps for Claude to run gather, publish the shortlist as a commentable document, run link-doc, then pick on Marco's comment

---

## Phase 5: Automatic daily run at 07:00 (FR-018, SC-007)

**Goal**: the shortlist document is ready every morning without Marco's computer.

**Independent test**: a manual firing of the scheduled run produces the document and pushes `tracking/` to GitHub.

- [X] T034 [US1] Install with `uv sync` at the start of the routine (no setup script needed: uv is preinstalled) and document required settings (network access, `ANTHROPIC_API_KEY`) in `docs/routines/daily-news.md`
- [X] T035 [US1] Add commit-and-push of `tracking/` after a run (commit message "News shortlist <date>") in the routine; no push of cache files
- [X] T036 [US1] Create the scheduled trigger: every day 07:00 Europe/Rome, prompt = the routine in `docs/routines/daily-news.md`; on Saturday also the weekly run once US4 exists
- [ ] T037 [US1] Fire the trigger once by hand and check the result against SC-007

---

## Phase 6: User Story 3 – "Giovedì buone notizie" (P2)

**Goal**: Thursdays propose only positive, confirmed stories.

**Independent test**: quickstart.md Scenario 4 with a fixture Thursday.

- [X] T038 [P] [US3] Write tests in `tests/unit/test_thursday.py`: only `positive` groups, a confirmation outside `good-news` required, backups from the previous 7 days when fewer than 3 (data-model.md Story.positive, Shortlist.good_news_thursday, Shortlist.backups)
- [X] T039 [US3] Implement the Thursday rule in `src/podcat/news/verify.py` and `src/podcat/news/shortlist.py`, and the warm-tone instruction in `src/podcat/news/editorial.py`

---

## Phase 7: User Story 4 – Stories for the weekly episode (P3)

**Goal**: on Saturday, 3–5 stories from the week for the Sunday episode.

**Independent test**: quickstart.md Scenario 5 with a week of fixture shortlists.

- [X] T040 [P] [US4] Write tests in `tests/unit/test_weekly.py`: stories only from Sunday–Saturday, "already used" marks, gaps listed, idempotent
- [X] T041 [US4] Implement `src/podcat/news/weekly.py` (research R8) with one ranking call (`weekly-rank` cost step)
- [X] T042 [US4] Add `podcat news weekly` to `src/podcat/cli.py` and the Saturday step to `docs/routines/daily-news.md`

---

## Phase 8: Polish

- [X] T043 [P] Update `README.md` with install, commands and the daily routine
- [ ] T044 [P] Mark FR coverage in `specs/001-news-gathering/checklists/requirements.md` notes; update `BACKLOG.md` (B-010, B-008 done when verified)
- [ ] T045 Run all quickstart.md scenarios, including the budget cap (Scenario 6), and record the results in `tracking/news/runs/`

---

## Dependencies

- Phase 1 → Phase 2 → US1 (Phase 3). Everything else needs US1.
- US2 needs US1. The automatic run (Phase 5) needs US1 and US2 (the document and the pick).
- US3 and US4 need US1 only and can be built in either order; Phase 5 adds the Saturday step after US4.
- T028–T029 and T036–T037 need network access to the feeds (cloud environment settings or Marco's machine).

## Parallel opportunities

- Phase 1: T003, T004, T005, T006 together.
- Phase 2: T008, T009, T011 together.
- US1 tests T014–T017 together; T021 alongside T020.
- After US1: US3 and US4 in parallel.

## Implementation strategy

1. MVP = Phases 1–3: a working `podcat news gather` checked by Marco on real feeds.
2. Then US2 and the 07:00 automatic run, so the daily routine is complete.
3. Then Thursday (US3) and the weekly list (US4) before the first Thursday and Saturday in production.
4. After each phase: tests green, commit and push, short report to Marco.
