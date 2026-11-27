# Quickstart: CapCut package

Prerequisites: specs 001 and 002 working, an approved script. Offline tests: `uv run pytest`.

1. **First real package** (fridge script, approved v4, mode A):
   `uv run podcat package build --date 2026-11-27` → `tracking/packages/2026-11-27-daily-…md` and
   `…/v1.md`; check 10 blocks in order, all 10 lines once, Vinile and Feedback on screen with their
   reactions, mode A on scene 3, every asset "da creare", reuse 0%, voice text for line 5
   ("novantaquattro"), three titles ≤ 70 characters, both sources in the description, cost under
   0.03 USD in `podcat costs show`.
2. **Idempotency**: same command again → same package, no new ledger entry.
3. **Document**: `podcat package show`, publish as Claude Doc, `podcat package link-doc <url>`.
4. **Revision**: comments on `image` and `title-2` → v2 changes only those parts, answers present;
   a comment on a line's text → no change and the fixed answer.
5. **Reuse cap**: in tests, a library with approved clips for every shot → reused share ≤ 30%,
   key moments new, least recently used chosen.
6. **Outdated**: `podcat script reopen` → package `outdated`; approve again → `package build`
   makes v2 from the new script version.
7. **Not approved**: `package build` on a script in `review` → exit 1, nothing written.
8. **Thursday and weekly**: first block is the gnocchi sting with the title styling; weekly has all
   four cats speaking and about 2 minutes.
9. **Mode C**: the holding cat is the speaker, the prompt has his look and the reference image.
