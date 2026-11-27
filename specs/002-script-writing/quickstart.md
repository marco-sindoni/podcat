# Quickstart: Script writing

Prerequisites: spec 001 working (`uv sync`, `ANTHROPIC_API_KEY`), a shortlist with a picked story.
Offline tests: `uv run pytest`.

1. **First real script** (story picked on 2026-11-27, comico):
   `uv run podcat script write --date 2026-11-27` → `tracking/scripts/2026-11-27-daily-…md` and
   `…/v1.md`; check 110–135 words, Flanella first and last, Feedback second-to-last, one news image
   with a mode, reactions for any silent cat, cost under 0.05 USD in `podcat costs show`.
2. **Idempotency**: run the same command again → same script shown, no new ledger entry.
3. **Document**: `uv run podcat script show --date 2026-11-27`, publish as Claude Doc, then
   `podcat script link-doc <url> --date 2026-11-27` → status `review`.
4. **Revision**: comments file with two anchored comments → `podcat script revise --comments f.yaml`
   → v2 changes only those lines (plus listed coherence changes), answers present, cost under
   0.03 USD.
5. **Ending**: `podcat script ending 2` → v3 with ending 2 in place, no cost.
6. **Approval**: `podcat script approve` → status `approved`, story `used`, `episode` set; a further
   `revise` is refused until `reopen`.
7. **Rotation**: write the next day's script → its mode differs from the previous one.
8. **Pick change**: on a script in `review`, `podcat news pick <other N>` → old script `discarded`,
   old story `candidate`.
9. **Thursday**: on a Thursday shortlist, the script opens with the slot formula and the
   `sting-gnocchi` scene.
10. **Pungente**: on a pungente story, notes confirm the register; Flanella closes with a pointed
    remark.
11. **Weekly**: Saturday pick → `podcat script write --kind weekly` → 280–320 words, all four cats
    with at least two lines.

## Real run, 2026-11-27 (fridge story)

- v1 (Sonnet head writer, 30 s): 99 words, failed the word check; v2 after fix: 89 words, 31 s.
  Marco: "moderatamente divertente, battute slegate".
- Trials after the craft prompt: Sonnet 30 s (85 words, 0.057 USD), Opus 30 s (86 words,
  0.116 USD), Opus 45 s (126 words, 43 s, 0.146 USD). Marco chose Opus at 45 s.
- v3 = Opus 45 s trial; v4 = ending 1 swapped in (`podcat script ending 1`, no cost):
  121 words, 41 s. Approved by Marco on 2026-11-28 with no line comments.
- Steps run for real: 1–3, 5, 6. Step 4 (revision) was not needed on this script; it is covered by
  the integration tests and will run live on the first script Marco comments.
