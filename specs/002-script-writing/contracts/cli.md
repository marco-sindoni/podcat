# CLI contract: `podcat script`

Same conventions as spec 001 (`specs/001-news-gathering/contracts/cli.md`): settings from `.env`,
run from the repository root, short Italian output. Exit codes: 0 ok, 1 user error, 2 budget cap,
4 script checks failed after the automatic fix (script saved as `draft` with its problems).

`--date D` and `--kind daily|weekly` select the shortlist (default: today's daily). The script is
the one for the story picked in that shortlist.

| Command | Does | Paid | Idempotent |
| --- | --- | --- | --- |
| `podcat script write [--date D] [--kind K] [--new-draft]` | Write the script for the picked story: writers' room, head writer, checks, fix if needed; save v1 (or a new version with `--new-draft`) | yes | reuses an existing script unless `--new-draft` |
| `podcat script show [--date D] [--kind K] [--version N]` | Print the Italian document text of the current (or given) version | no | yes |
| `podcat script link-doc URL [...]` | Store the document link; `draft` → `review` | no | yes |
| `podcat script revise --comments FILE [--tone comico\|pungente] [...]` | Apply Marco's comments as a new version | yes | the same comments file on the same version is applied once |
| `podcat script ending N [...]` | Swap in alternative ending N (1 or 2) as a new version | no | yes |
| `podcat script edit-line N TEXT [...]` | Record Marco's inline edit of line N as a new version, marked manual | no | yes |
| `podcat script approve [...]` | Lock the current version; story → `used` | no | yes |
| `podcat script reopen [...]` | Approved → review | no | yes |
| `podcat script discard [...]` | Mark the script discarded; story back to `candidate` | no | yes |
| `podcat script list [--last N]` | Recent scripts with status, mode, tone, words, cost | no | yes |

Comments file (YAML), written by Claude from the doc comments:

```yaml
- line: 3            # optional: numbered line the comment is anchored on
  quote: "Questo è uno scandalo!"
  text: "più cattiva"
- text: "nel complesso troppo lunga"   # whole-script comment
```

Change to spec 001: `podcat news pick N` on another candidate discards a `draft` or `review`
script of the previously picked story and prints it; an `approved` script still blocks the change.
