# Podcat Constitution

Podcat — *"Chiacchiere tra quattro gatti"* — is an Italian-language YouTube show in which four
grunge cats, sitting in four soft brown leather armchairs in a warmly lit tavern, comment on the
news (current affairs, sports, culture, entertainment) with irony, sarcasm and wit. This repository
holds the software that prepares each episode. This constitution is the single source of truth for
project-wide settings and decisions; every spec, plan and task MUST comply with it.

## Core Principles

### I. Editorial Value First

- Every episode MUST have original jokes, its own angle on the story and a small narrative arc.
  No copy-paste episodes: the format repeats, the substance never does.
- Every episode MUST include at least one image created specifically for its news story. That
  image MUST be staged in one of three modes — (a) the tavern's old CRT TV above the fireplace,
  (b) a 2–3 s full-screen cut-in with an off-screen cat line, (c) a cat holding a newspaper or
  photo — and two consecutively published videos (daily and weekly counted together) MUST NOT use
  the same mode. The episode record stores the mode used.
- Scripts are written as by a seasoned comedy and show writer, then reviewed by a second
  "head writer" pass.
- Rationale: YouTube's inauthentic content policy (July 2025, clarified July 2026) demonetizes
  channels with generic, repetitive or template-based content. Editorial substance is the
  channel's protection and its reason to exist.

### II. Human Approval Gates (NON-NEGOTIABLE)

- No script moves to production until Marco has reviewed and approved it. Scripts are delivered as
  commentable documents; comments are applied until approval.
- No video is published without Marco's approval of the final cut.

### III. Content Safety and Platform Compliance

- Comment on facts; never copy text, images or video from news outlets. Every story records its
  source URL.
- Never generate realistic images or voices of real people. No logos or trademarks in generated
  images.
- The cats MUST NOT present themselves as experts giving health, legal or financial advice.
- Satire targets facts and the powerful, never vulnerable groups. No distressing or shock content
  made to chase views.
- The YouTube "AI use" disclosure is always set to Yes on upload.
- Only official, terms-compliant APIs. No automation of personal consumer accounts (e.g. no
  unofficial CapCut or Dreamina wrappers).

### IV. Consistency of Characters, Set and Voices

- Characters, tavern, visual style and voices are defined in the production bible (`bible/`) and
  change only through an approved amendment.
- Visual style: soft 3D cartoon, animated-film look.
- Every generated image or clip starts from the approved reference images. Each cat has a fixed
  voice: in phase 1 a named CapCut voice recorded in the bible, in phase 2 a fixed ElevenLabs
  voice ID and parameters.
- Character personalities evolve only through each character's evolution log.
- Lip-sync is generic (non-synchronized mouth movement) until a backlog item says otherwise.

### V. Cost Before Quality

- Monthly spend cap: **50 USD across all services**. The pipeline MUST track the cost of every
  episode and refuse to run paid steps once the cap is reached.
- Pick the cheapest model that is acceptable; reuse library assets before generating new ones.
- Every external provider (text, voice, image, video) sits behind a replaceable interface.

### VI. Simplicity

- Start with the smallest thing that works; no infrastructure before it is needed.
- No database: tracking lives in Markdown files with YAML front matter.
- Every pipeline step is a repeatable, idempotent CLI command: re-running it never regenerates
  (or re-pays for) what already exists.

## Project Settings

| Setting | Value |
| --- | --- |
| Channel language | Italian only (voices, subtitles, titles, descriptions, on-screen text) |
| Code language | English for all code, identifiers, comments, commit messages and technical docs |
| Chat language | Conversations with Marco are always in Italian |
| Outputs | Daily reel ~30 s (70–90 words); weekly episode ~2 min (280–320 words) |
| News sources | Approved list and verification rules in `docs/news-sources.md`: two sources from different groups per story; no crime news or tragedies; politics only as satire of the powerful, never partisan |
| Recurring slot | "Giovedì buone notizie": every Thursday the daily reel covers one positive story from anywhere in the world (human progress, hope, kindness). Cats stay witty but warm; no sarcasm aimed at the people in the story |
| Aspect ratio | Always vertical 9:16 |
| Subtitles | Always present (phase 1: CapCut auto-captions; phase 2: burned in by FFmpeg, one color per cat, plus SRT) |
| Phase 1 production | Software gathers news and writes scripts; Marco reviews; Marco builds the video by hand in CapCut from a "CapCut package" (lines per cat, scene directions, visual prompts, Fotor prompt for the news image) and makes the news image by hand in Fotor |
| Phase 2 production | Automated voices, clips, FFmpeg editing, YouTube upload (see `BACKLOG.md`) |
| Monthly budget | 50 USD cap, all services |
| Tracking | Markdown + YAML front matter under `tracking/` |
| Assets | Binary assets live OUTSIDE git, under the directory in `PODCAT_ASSETS_DIR` (`/home/marco/Projects/podcat-assets` on Marco's machine; a temporary folder in cloud sessions, used only for caches) |
| Secrets | API keys in `.env`, never committed |
| Backlog | `BACKLOG.md` at the repository root |
| Decision log | `docs/decisions.md` |

## Technology Stack

- Python 3.12+, managed with `uv`; CLI built with Typer; data models with Pydantic; tests with
  pytest.
- Scripts: Claude via the Anthropic API.
- News: RSS feeds.
- Reference and news images: Fotor (phase 1 manual; Fotor OpenAPI later).
- Phase 2: ElevenLabs for voices, an official video-generation API behind an adapter, FFmpeg for
  editing and subtitles.
- Runs in Claude Code cloud sessions that clone the GitHub repository, so the daily work needs no
  local computer; results are committed and pushed. The daily news run starts automatically at
  07:00 Europe/Rome. The same commands also run on Marco's Linux machine
  (`/home/marco/Projects/podcat`).

## Development Workflow

- Every feature follows Spec Kit: `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` →
  `/speckit-implement`.
- Every project-level choice is recorded in `docs/decisions.md` (date, decision, rationale) and,
  when it is a rule, in this constitution.
- Future work goes into `BACKLOG.md` (ID, title, phase, status, spec link) and becomes a spec when
  picked.

## Governance

- This constitution supersedes every other practice in the repository. Specs and plans MUST check
  compliance with it.
- Amendments require Marco's approval, an entry in `docs/decisions.md`, and a version bump:
  MAJOR for removed or redefined principles, MINOR for new principles or settings, PATCH for
  wording.

**Version**: 1.3.0 | **Ratified**: 2026-11-25 | **Last Amended**: 2026-11-26
