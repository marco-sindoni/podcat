# Routine: script writing and review

Followed by Claude in the project chat or thread right after Marco picks a story (daily: step 7 of
[daily-news.md](daily-news.md); weekly: Saturday pick), and whenever Marco comments on a script
document. Spec: `specs/002-script-writing/` (contracts/cli.md).

## Requirements

Same cloud environment as the news routine (`PODCAT_ANTHROPIC_API_KEY`, network, `uv`). Models and
thinking effort per step are in `config/pricing.yaml` (`script_models`, `script_effort`).

## After a pick

1. `git pull --rebase origin main && uv sync`
2. `uv run podcat script write` (weekly: `--kind weekly`; another day: `--date`).
   - Exit 0: script ready. Exit 2: budget cap reached, tell Marco, stop.
   - Exit 4: the script failed the checks after one automatic fix. Tell Marco the problems in one
     sentence and offer `script write --new-draft`; do not publish it.
3. Publish `uv run podcat script show` as a Claude Doc, in Italian, title
   `Podcat – Copione <giorno> <data>` (weekly: `Podcat – Copione della domenica <data>`).
4. `uv run podcat script link-doc <url>` (status becomes `review`).
5. Commit and push `tracking/`: `git add tracking/ && git commit -m "Script <date>" && git push`.
6. Tell Marco in one or two Italian sentences, with the link: words, duration, image mode, cost.

## When Marco comments

Read the new comments on the document and act on keywords first:

| Marco writes | Command | Cost |
| --- | --- | --- |
| «approvato» | `podcat script approve` | free |
| «finale 1» / «finale 2» | `podcat script ending N` | free |
| an edit made inline in the document | `podcat script edit-line N "<new text>"` (one per edited line) | free |
| «rifalla da capo», «cambia angolo» | `podcat script write --new-draft` | paid |
| «più leggera» / «più pungente» | `podcat script revise --comments f.yaml --tone comico\|pungente` | paid |
| «riapri» (approved script) | `podcat script reopen` | free |
| «scartala» | `podcat script discard` | free |
| any other comment | `podcat script revise --comments f.yaml` | paid |

The comments file is YAML in the scratchpad, one entry per comment: `line` (the numbered line the
comment is anchored on, if any), `quote` (the anchored words), `text` (Marco's words). Put all the
open comments of one round in one file.

After each new version: replace the document content with `podcat script show` (same link), answer
each comment thread with one short sentence (the version's answers), commit and push `tracking/`.

## Notes

- Re-running a step is safe: an existing script, or a comments file already applied, costs nothing.
- Changing the pick in the news list discards a script still in review; an approved one blocks it.
- An approved script is the input of spec 003 (CapCut package).
