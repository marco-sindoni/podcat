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

---

# Amendment A1 (2026-11-27): comedy-first selection

Spec changes: FR-004, FR-005, FR-007, FR-008 amended; FR-019 to FR-023 and SC-008 new. Evidence: a
one-off trial on the cached 2026-11-27 run (28 verified groups, 0.005 USD) re-rated every group
with the A1 rules and gave 4 usable candidates against 1–2 in the original list.

## R12. Ordering and floors

- **Decision**: keep ratings in the editorial call and keep ordering deterministic in
  `shortlist.select`: drop stories with comic < 3, clarity < 3 or importance < 2 (FR-020), then sort
  by `comic + clarity` desc, `comic` desc, `importance` desc, id. Category cap stays 2; new cap of one
  `politics`-flagged story (FR-021). The old "fill with the best remaining" step is removed: below 3
  passing stories the list stays short with a warning (FR-023).
- **Rationale**: the trial showed the model's comic ratings were already right (the Salvini fridge
  hack had comic 5) but the importance-first sort pushed them out. Deterministic ordering stays
  testable without paid calls.
- **Alternatives**: let the model rank the list directly (not testable, less stable day to day);
  weighted formula with importance (importance is mostly press coverage, which favours hard news).

## R13. Clarity rating

- **Decision**: new `clarity` 1–5 with `clarity_reason`, rated in the same editorial call. Anchors in
  the prompt: 5 = anyone gets it in a few seconds with no background; 1 = needs names, acronyms,
  procedures or earlier events. The editorial prompt becomes "editor-in-chief and author" of a
  30-second reel for the general Italian public, with two eyes: comic (anchors from the trial, 5 =
  the story is already funny on its own) and satirical (R19).
- **Rationale**: one call, a few hundred extra output tokens (trial: ~8k output for 28 stories).
- **Alternatives**: separate clarity call (double cost, no gain).

## R14. Harm exclusion (FR-005 extension)

- **Decision**: two nets. Triage gets a new excluded value `harm` (illness, injury, physical harm or
  violence suffered by real people, famous people included). The editorial call returns
  `sensitive: bool` as a second net on the fuller text; sensitive stories are discarded with reason
  "tema delicato". Both prompts say explicitly that a career choice such as a retirement is not
  sensitive even when health is one of its reasons (the trial wrongly flagged Márquez).
- **Rationale**: triage sees only headlines and snippets and misses some cases (Ornella Muti passed
  triage on 2026-11-27); the editorial pass catches them. A health *flag* (advice risk) stays
  separate from the *exclusion* (harm to a person).
- **Alternatives**: editorial only (triage would waste verification and rating tokens on them).

## R15. One source for light categories (FR-004 exception)

- **Decision**: light categories = `entertainment`, `music`, `lifestyle`, `oddities`. Triage step 2
  becomes: return groups with two or more outlets, plus single-article groups whose category is a
  light one. `verify_group` accepts one counted group for light categories when at least one member
  is a `starting` source (same check as Thursday). After the editorial call, a single-source story
  flagged `politics`, `legal`, `health` or `finance` is discarded ("una sola fonte per un tema
  delicato"). The rumour exclusion still applies, so single-source gossip is still dropped.
- **Rationale**: the trial found zero single-source groups because triage drops them before
  verification; the exception must start at triage.
- **Cost**: more groups out of triage (estimate +30–50% triage output, ~+0.005 USD per day) and more
  stories to rate. Daily run estimate ~0.03 USD, within SC-005 (0.10 USD).
- **Alternatives**: a separate single-source pass per light category (more calls, more code).

## R16. Rating every verified story (FR-022)

- **Decision**: `MAX_GROUPS` goes from 20 to 60 as a budget guard only; the existing order (most
  confirmed first) decides what is left out above 60, and the run log records "N notizie non valutate
  per limite di budget". Single-source light groups are rated too.
- **Rationale**: 2026-11-27 had 28 verified groups; the Antonelli jet-ski story was one of the 8 never
  rated. 60 stories ≈ 25k input + 18k output tokens ≈ 0.012 USD.

## R17. Oddities sources (FR-019)

- **Decision**: new source category `oddities` (Italian label "curiosità"). Proposed sources, feeds
  checked on 2026-11-27 (items in the feed at check time), to be approved by Marco before they enter
  `docs/news-sources.md` and `config/sources.yaml`:

  | Source | Feed | Items | Group | Role | Note |
  | --- | --- | --- | --- | --- | --- |
  | Leggo | `https://www.leggo.it/rss/home.xml` | 20 | caltagirone | starting | popular daily, many offbeat stories (had the Salvini fridge hack) |
  | GreenMe | `https://www.greenme.it/feed/` | 30 | greenme | starting | everyday curiosities (replaces Focus.it, already a culture source) |
  | Geopop | `https://www.geopop.it/feed/` | 10 | geopop | starting | explainers and odd facts |
  | Corriere – Animali | `https://www.corriere.it/rss/animali.xml` | 49 | rcs | starting | animal stories |
  | Il Post – Animali | `https://www.ilpost.it/tag/animali/feed/` | 10 | ilpost | confirmation-only | same rule as Il Post |
  | La Nazione | `https://www.lanazione.it/rss` | 100 | qn | starting | local oddities from central Italy |
  | UPI Odd News | `https://rss.upi.com/news/odd_news.rss` | 25 | upi | starting | wire service, world oddities |
  | Sky News – Strange | `https://feeds.skynews.com/feeds/rss/strange.xml` | 3 | sky | starting | few but well chosen |
  | Metro – Weird | `https://www.metro.co.uk/news/weird/feed/` | 20 | dmg | starting | tabloid: clickbait filter applies |
  | Mirror – Weird News | `https://www.mirror.co.uk/news/weird-news/?service=rss` | 25 | reach | starting | tabloid: clickbait filter applies |

  Rejected at check: ANSA, Il Messaggero, Tgcom24 and Il Fatto curiosity feeds (404 or empty),
  Today.it, Notizie.it and Virgilio (block automated readers), Oddity Central and The Independent
  (empty feeds).
- **Rationale**: Italian first (6 of 10), plus world oddities that the cats can retell. Tabloids are
  acceptable because one source is enough only for light stories and the clickbait and rumour
  exclusions still apply.

## R18. Thursday and weekly under A1

- **Decision**: Thursday keeps FR-009 (positive only, 7 days, one source) and adds the clarity floor,
  the harm exclusion and the politics cap; its order becomes comic + clarity (the old importance +
  comic order is dropped). The weekly prompt receives clarity next to comic and importance and is
  asked to order by comic + clarity; stories created before A1 have no clarity and are shown as
  "n/d", ranked as clarity 3.
- **Rationale**: one ordering rule everywhere; the weekly pool is already made of A1 candidates
  after the first week.

## R19. Two tones: comico and pungente (FR-024, A1 revision)

- **Decision**: the editorial call adds `satirical_potential` 1–5 and `satirical_reason`. Anchors:
  5 = a clear, pointed observation on power, contradiction, hypocrisy or society that stays with the
  viewer; 1 = nothing to say beyond the fact; never at the expense of victims. `shortlist.select`
  first fills the pungente slot: best story by `satirical + clarity`, then importance, among those
  with satirical ≥ 3, clarity ≥ 3, importance ≥ 3, not sensitive. It then fills up to four comic
  slots with the comic rules (R12), skipping the story already used. A story whose comic potential is higher
  than its satirical potential stays comic, so the pungente slot never takes the funniest story. The politics cap (one) and the
  category cap (two) apply to the whole list. Each story file records `tone: comico | pungente`.
  Thursday skips the pungente slot. The weekly prompt is asked for one pungente story among its
  picks and receives the tone and satirical rating of each story.
- **Rationale**: a fixed slot gives about 20% of the offer every day (one in five) with a simple,
  testable rule; Marco's picks decide the final share. The same call rates both tones, so no extra
  cost beyond a few output tokens per story.
- **Alternatives**: a monthly quota that tracks Marco's picks (more state, and it would push stories
  on days when none is good); letting the model choose the tone (not testable).
