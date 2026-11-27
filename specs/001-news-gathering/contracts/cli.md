# CLI contract: `podcat`

All commands read settings from `.env` (`PODCAT_ASSETS_DIR`, `ANTHROPIC_API_KEY`) and work from the
repository root. Exit code 0 on success, 1 on user error, 2 on budget cap reached, 3 on no data.
Output is short Italian text for Marco; logs and file contents stay in English field names.

| Command | Does | Paid | Idempotent |
| --- | --- | --- | --- |
| `podcat sources check [--write]` | Fetch every configured feed, try autodiscovery for broken ones, print a status table; with `--write` update `config/sources.yaml` (`feeds`, `manual`, `last_check`) | no | yes |
| `podcat news gather [--date D] [--refresh]` | Daily run for date D (default today): fetch, triage, verify, editorial, write stories, shortlist, run log, cost | yes | reuses existing shortlist unless `--refresh` |
| `podcat news show [--date D] [--kind daily\|weekly]` | Print the shortlist | no | yes |
| `podcat news pick N [--date D] [--kind K]` | Mark candidate N (1-based) as chosen; clears an earlier pick | no | yes |
| `podcat news unpick [--date D] [--kind K]` | Clear the pick if no script exists | no | yes |
| `podcat news reject [--date D] [--kind K]` | Mark all candidates rejected; next `gather --refresh` excludes them | no | yes |
| `podcat news weekly [--date D] [--refresh]` | Weekly run (meant for Saturday) from the week's stories | yes | as `gather` |
| `podcat news link-doc URL [--date D] [--kind K]` | Store the commentable document link in the shortlist | no | yes |
| `podcat costs show [--month M]` | Print month total, cap and remaining | no | yes |

`gather` and `weekly` print the shortlist path at the end, so the project chat can publish it.

## Amendment A1 (2026-11-27)

No new commands or exit codes. `podcat news show` adds the "Comprensibilità" column and line (data
model A1). `podcat news gather` may print a shortlist with 1–2 candidates and a warning (FR-023).

## Spec 002 (2026-11-28)

`podcat news pick N` on another candidate discards a `draft` or `review` script of the previously
picked story (daily and weekly lists); an approved script still blocks the change. Script commands:
`specs/002-script-writing/contracts/cli.md`.
