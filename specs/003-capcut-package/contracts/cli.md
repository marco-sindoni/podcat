# CLI contract: `podcat package`

Same conventions as `podcat script` (`specs/002-script-writing/contracts/cli.md`): settings from
`.env`, run from the repository root, short Italian output. Exit codes: 0 ok, 1 user error (e.g.
script not approved), 2 budget cap, 4 package checks failed after the automatic fix (package saved
with its problems, not delivered).

`--date D` and `--kind daily|weekly` select the script (default: today's daily), as for scripts.

| Command | Does | Paid | Idempotent |
| --- | --- | --- | --- |
| `podcat package build [--date D] [--kind K]` | Build the package from the approved script version: layout, clip plan, creative call, checks, fix if needed; save v1 (or a new version if the script was re-approved) | yes | reuses a `ready` package for the same script version |
| `podcat package show [--date D] [--kind K] [--version N]` | Print the Italian document text | no | yes |
| `podcat package link-doc URL [...]` | Store the document link | no | yes |
| `podcat package revise --comments FILE [...]` | Apply comments to the allowed parts as a new version | yes | the same comments file on the same version is applied once |
| `podcat package list [--last N]` | Recent packages: status, mode, reuse share, new clips, cost | no | yes |

`podcat script reopen` now also sets the package `outdated` and prints it.

Comments file (YAML), written by Claude from the doc comments:

```yaml
- part: image          # image, image-alt, title-1..3, description, hashtags, clip-N, voice-N, effects
  quote: "an industrial cold room"
  text: "metti un frigo più grande"
- text: "nel complesso va bene"   # whole-package comment
```
