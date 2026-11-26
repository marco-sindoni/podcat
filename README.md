# Podcat — Chiacchiere tra quattro gatti

Software that prepares episodes of Podcat, an Italian YouTube show where four grunge cats comment
on the news from their tavern armchairs.

- Rules and settings: [`.specify/memory/constitution.md`](.specify/memory/constitution.md)
- Decisions: [`docs/decisions.md`](docs/decisions.md)
- Backlog: [`BACKLOG.md`](BACKLOG.md)
- Production bible: [`bible/`](bible/) (characters and prompt library)
- Visual test plan: [`docs/visual-test-plan.md`](docs/visual-test-plan.md)
- Episode, asset and news tracking: [`tracking/`](tracking/)

Binary assets are stored outside this repository, in the directory set by `PODCAT_ASSETS_DIR`
(see `.env.example`).

## Install

```bash
uv sync
cp .env.example .env   # on a local machine; in the cloud use environment variables
uv run pytest          # offline, no paid calls
```

## Commands

| Command | Does |
| --- | --- |
| `podcat sources check [--write]` | Check every source feed, autodiscover missing ones, update `config/sources.yaml` |
| `podcat news gather [--date D] [--refresh]` | Daily shortlist of 3–5 verified stories (Thursday: good news only) |
| `podcat news weekly [--date D] [--refresh]` | Saturday shortlist for the Sunday episode |
| `podcat news show / pick N / unpick / reject / link-doc URL` | Read the list, pick a story, undo, reject all, attach the review document |
| `podcat costs show [--month YYYY-MM]` | Month spend against the 50 USD cap |

Run them with `uv run podcat …`. Details: [`specs/001-news-gathering/contracts/cli.md`](specs/001-news-gathering/contracts/cli.md).

## Daily routine

Every morning (scheduled at 06:33 Europe/Rome, so the document is ready by 07:00) a scheduled Claude Code session follows
[`docs/routines/daily-news.md`](docs/routines/daily-news.md): it gathers the news, pushes
`tracking/` to GitHub and publishes the shortlist as a commentable document for Marco.
