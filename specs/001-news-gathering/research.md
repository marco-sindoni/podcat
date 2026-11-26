# Research: Daily news gathering and verification

Phase 0 of the plan. Each item: decision, rationale, alternatives considered.

## R1. Feed addresses for the approved sources

- **Decision**: Keep a machine-readable source list in `config/sources.yaml` (name, category, publishing
  group, role, feed URL or `manual`). Feed URLs are filled and verified on Marco's machine by a
  `podcat sources check` command that (a) fetches each configured feed, (b) if missing or broken,
  tries feed autodiscovery from the outlet's home page (`<link rel="alternate"
  type="application/rss+xml">`), and (c) writes a status report. Sources without a working feed
  become `manual` and are skipped by the automatic run.
- **Rationale**: The planning environment has no outbound access to news sites, so feeds cannot be
  checked here; Marco's machine can. Making the check a repeatable command also catches feeds that
  break later. Matches the note in `docs/news-sources.md` ("RSS availability is checked when the
  news-gathering feature is planned").
- **Alternatives**: Hard-code URLs from memory (unverified, would silently rot); scrape home pages
  (fragile, and closer to copying content).

## R2. Fetching and parsing feeds

- **Decision**: `httpx` for HTTP (timeouts, redirects, a clear User-Agent naming the project but no
  personal data), `feedparser` to parse RSS and Atom. Fetch concurrently with a per-feed timeout of
  10 s; a failing feed is logged and skipped. Keep only items published in the window (default
  24 h, Europe/Rome).
- **Rationale**: Both libraries are standard and well maintained; feedparser copes with malformed
  feeds common on Italian news sites.
- **Alternatives**: `requests` (no async, no advantage); custom XML parsing (fragile).

## R3. Grouping items into stories, topic filter

- **Decision**: One language-model call ("triage") per run. Input: every item in the window as a
  compact line (id, outlet, title, first 200 characters of the feed description). Output (structured
  JSON validated by Pydantic): groups of item ids that report the same event, each with a category,
  an excluded-topic verdict (crime, tragedy, clickbait, rumour, sponsored, social-only) with a reason,
  and a "positive story" flag. Before the call, deterministic pre-filters drop duplicates (same URL),
  items outside the window and headlines matching a clickbait word list.
- **Rationale**: Italian headlines about the same event vary a lot; string similarity misses many
  matches and creates false ones. One call over ~300–600 short lines is cheap (see R5) and keeps
  the code simple.
- **Alternatives**: TF-IDF/embedding clustering (extra dependency or paid embeddings, weaker on
  short Italian headlines); one call per item (more calls, same cost, slower).

## R4. Verification rule and agency wires

- **Decision**: Verification is deterministic code, not the model. A group is verified when its items
  come from at least two distinct *effective groups*. Effective group = the source's publishing
  group from `config/sources.yaml`, except when the item credits an agency (patterns such as
  "(ANSA)", "Adnkronos", "(AGI)", "Reuters", "AP") — then it is the agency. `satire` sources never
  count; Il Post and Il Fatto Quotidiano count only as confirmations (they cannot be the only
  starting source). On Thursdays the window is 7 days, triage runs in chunks of 600 items and returns only positive
  groups, and one approved starting source is enough (decided 2026-11-26 after the first real run).
- **Rationale**: The rule is the editorial core of the feature and must be predictable and testable
  without network or model calls.
- **Alternatives**: Ask the model to judge verification (not reproducible, harder to test).

## R5. Language model and cost

- **Decision**: Claude Haiku 5.5 (`claude-haiku-5-5`, 0.10 USD per million input tokens, 0.50 USD
  per million output tokens) for both calls of the feature: triage (R3) and the editorial pass
  (Italian summary, importance 1–5, comic potential 1–5, sensitivity flags, follow-up detection
  against recently used stories). Structured output through the SDK's `messages.parse` with Pydantic
  models. The model id lives in configuration so it can be changed without code changes.
- **Rationale**: Constitution V ("cheapest model that is acceptable"). Estimated daily cost: triage
  ~40k input + ~6k output tokens ≈ 0.007 USD; editorial pass on ≤15 verified stories ~8k input +
  ~4k output ≈ 0.003 USD. Total ≈ 0.01 USD per day, ~0.30 USD per month, well under SC-005
  (0.10 USD per day). Script writing (spec 002) can use a stronger model separately.
- **Alternatives**: Sonnet 5.5 (20× the price, not needed for classification and short summaries);
  Message Batches (50% cheaper but asynchronous, adds waiting for a cost that is already tiny).
- **Prompt caching**: not useful here; the instruction prefix is short and each day's input differs.

## R6. Cost tracking and the monthly cap

- **Decision**: A monthly ledger `tracking/costs/YYYY-MM.md` (front matter: month, cap_usd,
  total_usd; body: one table row per paid call with date, feature, step, model, tokens, USD).
  Before each paid call the code estimates the worst-case cost (input tokens estimated from
  characters, plus `max_tokens` at output price) and refuses the call if `total + estimate > cap`.
  After the call it records the real cost from the response usage. Prices live in
  `config/pricing.yaml`.
- **Rationale**: Constitution V and VI: a Markdown ledger, no database; refusing before the call means
  no partial charges.
- **Alternatives**: Read the Anthropic usage API (needs an admin key, not per episode).

## R7. Idempotency and caching of intermediate results

- **Decision**: Each step writes its result once and reuses it: fetched items and model outputs go to
  `$PODCAT_ASSETS_DIR/cache/news/<date>-<kind>/` as JSON (headlines, links and model outputs only,
  no article text); the shortlist goes to `tracking/news/`. Re-running for a date with a shortlist
  shows it and does nothing else. `--refresh` re-runs from the fetch step and replaces the shortlist
  (rejected stories stay excluded).
- **Rationale**: Constitution VI (never re-pay for what exists). Intermediate JSON is bulky and not
  editorial, so it stays out of git with the other assets.
- **Alternatives**: Store everything in git (noisy history); no cache (re-pays on every re-run).

## R8. Weekly run

- **Decision**: The Saturday run builds the weekly shortlist from the stories already verified by the
  daily runs of the week (Sunday to Saturday); the Saturday daily run, done first, covers the last
  24 hours. It
  re-ranks them with one editorial call and marks "already used in reel". Days without a daily run
  are listed as gaps.
- **Rationale**: RSS feeds usually keep only the last 1–2 days of items, so a 7-day fetch is not
  reliable; the daily runs are the week's memory. Spec FR-002 is updated to say so.
- **Alternatives**: Fetch 7 days (most feeds cannot serve it).

## R9. Delivering the shortlist as a commentable document

- **Decision**: The CLI writes the shortlist as Markdown in `tracking/news/shortlists/` (source of
  truth) and prints its path. The commentable document is a Claude Doc created by Claude in the
  project chat: the daily routine is "Claude runs `podcat news gather` on Marco's machine, publishes
  the shortlist as a Claude Doc, stores the link with `podcat news link-doc`". When Marco picks a
  story in a comment, Claude runs `podcat news pick`. The CLI never calls the Docs service itself.
- **Rationale**: There is no public API for Claude Docs; the project chat already has the connector,
  and this matches how scripts will be reviewed. It keeps the CLI simple and testable.
- **Alternatives**: Google Docs API (new account, OAuth, out of scope); Markdown only (Marco asked for
  a document).

## R10. Project layout and tooling

- **Decision**: One Python package `podcat` under `src/`, managed with `uv`, entry point `podcat`
  (Typer). Settings from `.env` via `python-dotenv` and a Pydantic settings model. Tracking files
  read and written with PyYAML front matter by a small helper (no extra frontmatter library). Tests
  with pytest; network and model calls replaced by fixtures (saved RSS files and recorded model
  outputs), so the test suite costs nothing and runs offline.
- **Rationale**: Constitution technology stack; smallest set of dependencies.
- **Alternatives**: `python-frontmatter` (tiny gain, one more dependency); `pydantic-settings`
  (fine, but `python-dotenv` + Pydantic is enough).

## R11. Running without Marco's computer

- **Decision**: The default place to run is a Claude Code cloud session. A scheduled task resumes the
  project session every day at 07:00 Europe/Rome (Saturday also runs `news weekly`). The session pulls the
  repository, installs dependencies with `uv sync` (no setup script needed), runs
  `podcat news gather`, commits and pushes `tracking/` to `main`, and publishes the shortlist as a
  commentable document. The cloud environment needs outbound access to the feed hosts and
  `ANTHROPIC_API_KEY` as an environment variable (entered by Marco). `PODCAT_ASSETS_DIR` points to a
  temporary folder there; losing the cache only means a refresh would re-pay a few cents, while the
  shortlist in git still makes re-runs free.
- **Rationale**: Marco wants to work from his phone with the computer off (2026-11-26). Phase 1
  produces only text files, which all live in git.
- **Alternatives**: GitHub Actions cron (no project chat or document publishing); a home server (new
  infrastructure, against constitution VI).
