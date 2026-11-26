# Data Model: Daily news gathering and verification

All persistent records are Markdown files with YAML front matter (constitution VI). Field names are
English; editorial text (titles, summaries, reasons) is Italian. Dates are ISO 8601, times in
Europe/Rome.

## Source (`config/sources.yaml`)

One entry per approved outlet, generated from `docs/news-sources.md`.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | slug | unique, e.g. `ansa`, `corriere` |
| `name` | string | outlet name |
| `category` | enum | `current-affairs`, `sport`, `culture`, `entertainment`, `music`, `lifestyle`, `good-news`, `satire` |
| `group` | slug | publishing group, e.g. `rcs`, `gedi`, `ansa`; sources in the same group never confirm each other |
| `role` | enum | `starting` (default), `confirmation-only` (Il Post, Il Fatto), `inspiration-only` (satire) |
| `feeds` | list of URL | one or more RSS/Atom feeds; empty when `manual` |
| `manual` | bool | true when no working feed; skipped by automatic runs |
| `last_check` | date | written by `podcat sources check` |

Agency credit patterns (`config/agencies.yaml`): agency id → list of regular expressions matched on
title and description.

## Feed item (cache only, not tracked in git)

`$PODCAT_ASSETS_DIR/cache/news/<date>-<kind>/items.json`: `item_id`, `source_id`, `title`,
`summary_snippet` (≤200 characters of the feed description), `url`, `published_at`,
`agency` (detected credit or null).

## Story (`tracking/news/stories/<story-id>.md`)

`story-id` = `<first-seen-date>-<slug-of-title>`.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | string | as above |
| `title` | string (it) | own words, not a copied headline |
| `summary` | string (it) | 2–3 sentences, own words, neutral |
| `category` | enum | as Source.category, never `satire` |
| `sources` | list | each: `source_id`, `outlet`, `group` (effective group), `url`, `published_at` |
| `effective_groups` | int | ≥2 for a verified story |
| `first_seen` | datetime | |
| `importance` | int 1–5 + `importance_reason` | |
| `comic_potential` | int 1–5 + `comic_reason` | |
| `positive` | bool | true for good-news candidates |
| `flags` | list | subset of `politics`, `health`, `legal`, `finance` |
| `follow_up_of` | story-id or null | set when it develops an already used story |
| `status` | enum | see transitions |
| `episode` | episode id or null | set by the script/episode features |

Status transitions:

```text
candidate ──pick──▶ chosen ──script written (spec 002)──▶ used
    │                 │
    │                 └─unpick (only before a script exists)──▶ candidate
    └─reject──▶ rejected   (never proposed again)
```

## Shortlist (`tracking/news/shortlists/<date>-<kind>.md`)

| Field | Type | Rules |
| --- | --- | --- |
| `date` | date | run date |
| `kind` | enum | `daily`, `weekly` |
| `good_news_thursday` | bool | true when date is a Thursday and kind is daily |
| `status` | enum | `proposed`, `picked`, `rejected` |
| `candidates` | list of story-id | 3–5, ordered by importance (fewer only with `warning`) |
| `backups` | list of story-id | Thursday backups from the previous 7 days |
| `picked` | story-id or null | exactly one when `status: picked` |
| `warning` | string or null | e.g. fewer than 3 verified stories, category down |
| `doc_url` | URL or null | commentable document link |
| `run_log` | path | |
| `cost_usd` | number | |

Body: a readable Italian table (rank, title, category, importance, comic potential, sources) so the
file can be read or pasted as is.

## Run log (`tracking/news/runs/<date>-<kind>.md`)

Front matter: `date`, `kind`, `started_at`, `finished_at`, `feeds_ok`, `feeds_failed` (list with
error), `items_in_window`, `groups_found`, `verified`, `discarded` (count), `cost_usd`. Body: table of
discarded groups with reason (excluded topic, single source, satire only, already used).

## Cost ledger (`tracking/costs/<YYYY-MM>.md`)

Front matter: `month`, `cap_usd` (50), `total_usd`. Body: one row per paid call: `date`, `feature`
(`news`), `step` (`triage`, `editorial`, `weekly-rank`), `model`, `input_tokens`, `output_tokens`,
`usd`. Shared by all future features.

## Model outputs (validated with Pydantic)

- **Triage**: list of groups: `item_ids`, `category`, `excluded` (null or one of `crime`, `tragedy`,
  `clickbait`, `rumour`, `sponsored`, `social-only`), `excluded_reason`, `positive`.
- **Editorial**: per verified group: `title`, `summary`, `importance`, `importance_reason`,
  `comic_potential`, `comic_reason`, `flags`, `follow_up_of`, `already_used` (bool).
