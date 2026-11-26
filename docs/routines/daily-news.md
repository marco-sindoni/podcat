# Routine: daily news shortlist

Followed by Claude every morning at 07:00 Europe/Rome (scheduled task) and whenever Marco asks for
"notizie di oggi" in the project chat. Spec: `specs/001-news-gathering/` (FR-017, FR-018).

## Requirements of the cloud environment

- Network access to the feed hosts (currently "unrestricted").
- `ANTHROPIC_API_KEY` as an environment variable, entered by Marco in the environment settings.
- `uv` (preinstalled in Claude Code cloud containers; otherwise `curl -LsSf https://astral.sh/uv/install.sh | sh`).
- No setup script is needed: step 1 runs `uv sync`, which is fast and idempotent.

## Steps

1. Update and install, from the repository root:
   `git checkout main && git pull --rebase origin main && uv sync`
2. Run the daily shortlist: `uv run podcat news gather`.
   - Exit 0: shortlist ready. Exit 3: no verified story (the file still exists, with a warning).
   - Exit 2: monthly budget cap reached. Stop, tell Marco, publish nothing.
   - Any other failure: tell Marco what failed (command and message), do not retry more than once.
3. On Saturday also run `uv run podcat news weekly`.
4. Commit and push only tracking files:
   `git add tracking/ && git commit -m "News shortlist <YYYY-MM-DD>" && git push origin main`
   (on a rejected push: `git pull --rebase origin main`, then push again). Never commit the cache
   (it lives in `$PODCAT_ASSETS_DIR`, outside the repository).
5. Publish each new shortlist as a commentable Claude Doc in the project, in Italian:
   - title: `Podcat – Notizie di <giorno> <data>` (weekly: `Podcat – Notizie della settimana <data>`);
   - content: the shortlist body (`uv run podcat news show`, add `--kind weekly` for the weekly one),
     then a closing line: "Scegli la notizia con un commento, per esempio: la 2.";
   - store the link: `uv run podcat news link-doc <url>` (add `--kind weekly`), then commit and push
     as in step 4.
6. Tell Marco in the project thread, in one or two short Italian sentences, with the document link:
   how many candidates, any warning (few stories, feeds down, Thursday or Saturday list).
7. When Marco picks (a document comment or a chat message such as "la 2"):
   `uv run podcat news pick <N>` (add `--date` / `--kind` if it is not today's daily list), commit
   and push, answer in the comment thread or chat with the chosen title. "Nessuna" means
   `uv run podcat news reject` followed by `uv run podcat news gather --refresh` and steps 4–6 again.

## Notes

- Re-running any step is safe: an existing shortlist is reused at no cost.
- Thursday lists are "Giovedì buone notizie"; mention it in the message.
- On Marco's machine the same commands work; run `git pull` there to see the files.
