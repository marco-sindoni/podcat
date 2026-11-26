# Quickstart: Daily news gathering and verification

Validation guide for spec 001. Commands run on Marco's machine in `/home/marco/Projects/podcat`.

## Prerequisites

- `uv` installed, Python 3.12+ (3.14 present).
- `.env` with `PODCAT_ASSETS_DIR` and `ANTHROPIC_API_KEY`.
- `config/sources.yaml` checked at least once (`podcat sources check --write`).

## Setup

```bash
uv sync
uv run pytest            # offline, no paid calls
uv run podcat sources check
```

Expected: tests pass; the check prints one row per source with `ok`, `found by autodiscovery` or
`manual`.

## Scenario 1: daily shortlist (US1, SC-001, SC-002)

```bash
uv run podcat news gather
```

Expected within 5 minutes: path of `tracking/news/shortlists/<today>-daily.md` with 3–5 candidates
ordered by importance, each with comic potential and ≥2 sources from different groups; run log in
`tracking/news/runs/`; cost row in `tracking/costs/<month>.md`. Open two source links per candidate
and check they report the same event.

## Scenario 2: idempotency (FR-012, SC-006)

Run `uv run podcat news gather` again. Expected: the same shortlist is printed, no new cost row.

## Scenario 3: pick and reject (US2)

```bash
uv run podcat news pick 2
uv run podcat news show
uv run podcat news reject && uv run podcat news gather --refresh
```

Expected: candidate 2 is `chosen`; after reject and refresh the new shortlist excludes the rejected
stories.

## Scenario 4: Thursday (US3)

```bash
uv run podcat news gather --date <a Thursday>
```

Expected: only positive stories, each with a confirmation outside `good-news` sources; a warning and
backups if fewer than 3.

## Scenario 5: weekly (US4)

On a Saturday after some daily runs: `uv run podcat news weekly`. Expected: 3–5 stories from the
week, each marked used or new, and the list of days without a daily run.

## Scenario 6: budget cap (FR-013)

Set `cap_usd` in the current ledger below `total_usd` and run `gather --refresh`. Expected: exit
code 2, a clear message, no new cost row. Restore the cap afterwards.

## Daily routine (phase 1)

1. Marco asks in the project chat for today's news (or Claude does it when asked).
2. Claude runs `podcat news gather` on Marco's machine and publishes the shortlist as a commentable
   document; `podcat news link-doc` stores the link.
3. Marco comments the pick; Claude runs `podcat news pick N`. The chosen story feeds spec 002.
