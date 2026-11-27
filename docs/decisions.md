# Decision log

Newest first. Rules that follow from a decision are also written into the constitution.

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-11-28 | Phase 1 subtitles: CapCut auto-captions generated from the voice track, corrected against the package's subtitle section (fixed style in `bible/subtitles.md`, color per cat, caption chunks of at most 2 × 32 characters, words to check); no SRT until phase 2 | Always in time with the voices; synthetic voices are clean, so only names and numbers need checking (Marco) |
| 2026-11-28 | Spec 003 (CapCut package) approved: reused clips (library or earlier episodes) cover at most 30% of each video, the rest is new clips made for the episode; sound = tavern ambience, one or two effects and a fixed short theme tune for opening and closing, licensed for YouTube; publishing kit for YouTube only | Reuse saves credits but makes episodes look alike, and the inauthentic content policy punishes repetition (Marco) |
| 2026-11-28 | Daily reel becomes ~45 s (110–135 words, target 45 s ± 5); head writer and revisions move to Opus 5.5 at medium effort (`config/pricing.yaml`), with a stricter craft prompt (one comic premise, each line answers the previous, callback ending). Constitution v1.5.0 | Trial on the fridge story: Opus at 45 s gave the most connected script; about 7.5 USD a month for scripts, well under the cap (Marco) |
| 2026-11-28 | Script speaking rates start at about 3 words/s (Flanella 3.0, Fuzz 3.4, Vinile 2.9, Feedback 2.5); weekly target 110 s ± 15; thinking effort per script step in `config/pricing.yaml` (`script_effort`) | 70-90 words must fit 30 s and 280-320 words then give 95-125 s; with default thinking the models spent the whole output budget thinking |
| 2026-11-27 | Spec 002 plan: writers' room on Haiku 5.5, head writer and revisions on Sonnet 5.5, set in `config/pricing.yaml` (`script_models`) so they change without code; Thursday formula "Giovedì buone notizie! Buoni gli gnocchi, buone le notizie." | About 3 USD a month for scripts; easy to move to Opus later (Marco) |
| 2026-11-27 | Thursday logo and sting: the words "Giovedì" and "gnocchi" in red or another standout color, so the title reads "giovedì gnocchi" at a glance | With the steaming plate it recalls the saying "giovedì gnocchi" (Marco) |
| 2026-11-27 | Spec 002 (script writing) approved: two passes (writer, head writer); comico or pungente register from the story's tone; final version plus 2 alternative endings; all four cats speak when possible, otherwise silent cats get reaction shots with faces or gestures; weekly episode covers one story in depth | Marco's answers to the spec questions |
| 2026-11-26 | Only sources with a working RSS feed are used; no manual sources. Blocked or feedless sources replaced (Euronews Italiano, Open, Sportface, Doppiozero, Ciak, Soundsblog, SentireAscoltare, Rockon, NME, Dove Viaggi, The Optimist Daily, YES! Magazine); satire extended with The Hard Times, The Beaverton, The Shovel, Le Gorafi, Reductress. 84 sources, 10 per category (14 current affairs) | Keep it simple: everything read automatically from the cloud (Marco) |
| 2026-11-26 | Daily work runs in Claude Code cloud sessions (repo cloned from GitHub, results pushed); the daily news run starts automatically at 07:00 Europe/Rome; Marco reviews from the Claude phone app. Constitution v1.3.0 | Works with Marco's computer off; brings B-008 forward to phase 1 |
| 2026-11-27 | Politics cap per tone (one comic political story plus the pungente one); triage split in chunks by source category with a merge call | First A1 run lost the Salvini fridge story to the cap and found fewer groups with 959 items |
| 2026-11-27 | Spec 001 amendment A1: candidates ordered by comic potential plus clarity, with floors (comic and clarity at least 3, importance at least 2); one "pungente" slot per daily list (satirical potential, clarity and importance at least 3) for satire and reflection, about 20% of the offer; tone recorded per story; at most one politics story per list | First real lists were mostly hard politics, violence and a sick celebrity; Marco wants mostly comic stories plus some sharper, thought-provoking ones |
| 2026-11-27 | One approved starting source is enough for light categories (entertainment, music, lifestyle, oddities) unless the story touches politics, justice, health or money; harm to real people excluded; new "curiosità e stranezze" category with 10 sources (constitution v1.4.0) | Light, odd stories rarely appear in two outlets; the risk of a wrong light story is low |
| 2026-11-26 | Spec 001 (news gathering) approved: weekly shortlist on Saturday for Sunday publication; shortlists delivered as commentable documents; candidates ordered by importance with comic potential shown | Marco's answers to the spec questions |
| 2026-11-26 | "Giovedì buone notizie": search the last 7 days and accept one approved, non-satire starting source per positive story (FR-009 updated) | First real run found only 1 positive story confirmed by two groups; the slot is weekly, so a 7-day window fits |
| 2026-11-26 | Thursday also excludes positive outcomes of mourning, deaths, violence or crimes against people, and ranks candidates by importance plus comic potential | Second real run proposed a story born from a femicide; the reel needs a story the cats can joke about |
| 2026-11-25 | News sources approved: 10 per category (current affairs, sport, culture, entertainment, music, lifestyle, good news, satire as inspiration only); two-source rule; no crime news or tragedies; non-partisan politics | Verified, high-traffic sources; satire never as fact source |
| 2026-11-25 | Prompt library in `bible/prompts/` and manual test plan `docs/visual-test-plan.md` before any production | Lock the look and voices once, then reuse |
| 2026-11-25 | "Giovedì buone notizie" logo: a steaming plate of gnocchi al sugo, used as a short reusable opening sting every Thursday | "Buoni gli gnocchi, buone le notizie" (Marco) |
| 2026-11-25 | "Giovedì buone notizie": every Thursday the daily reel is a positive story from around the world; dedicated "good news" source category | Recognisable weekly ritual (like "giovedì gnocchi"); varies the tone |
| 2026-11-25 | Character sheets get verbal tics, voice profiles and seating (left to right: Fuzz, Flanella, Vinile, Feedback) | Marco approved; Fuzz and Vinile at opposite ends because they argue |
| 2026-11-25 | The four cats: Flanella (F, host), Fuzz (M, hothead), Feedback (M, slow philosopher), Vinile (M, grumpy nostalgic) | Three males and one female, grunge-inspired names, no real people or brands |
| 2026-11-25 | Phase 1 voices: four fixed CapCut voices, one per cat, recorded in the bible; ElevenLabs (Starter, 6 USD/month, commercial licence) in phase 2 | No account yet; free tier lacks commercial licence |
| 2026-11-25 | Code runs in `/home/marco/Projects/podcat`; assets in `/home/marco/Projects/podcat-assets` | Marco's machine; assets outside git |
| 2026-11-25 | Future work tracked in `BACKLOG.md`, promoted to Spec Kit specs when picked | Markdown, versioned with the code, no extra tools |
| 2026-11-25 | Monthly budget cap 50 USD across all services | Cost before quality |
| 2026-11-25 | All videos vertical 9:16, daily and weekly | Shorts-first channel |
| 2026-11-25 | Generic lip-sync at start; real lip-sync in backlog | Audio-driven models cost more |
| 2026-11-25 | Visual style: soft 3D cartoon | More consistent across generations; exempt from realistic-AI labelling |
| 2026-11-25 | Channel language: Italian only | Marco's choice |
| 2026-11-25 | Each episode has a dedicated news image, staged in one of three rotating modes, never the same mode twice in a row | Variety and authenticity against the "template" risk |
| 2026-11-25 | Phase 1: videos built by hand in CapCut from approved scripts; automation in phase 2 | CapCut has no public API and its terms forbid automation |
| 2026-11-25 | Scripts reviewed by Marco as commentable documents | Editorial control is the core of the format |
| 2026-11-25 | Tracking in Markdown + YAML, no database; assets outside git | Keep it simple |
| 2026-11-25 | Spec-driven framework: GitHub Spec Kit with Claude Code integration | Only major framework with a constitution; greenfield fit |
| 2026-11-25 | Stack: Python 3.12+, uv, Typer, Pydantic, pytest; Claude API for scripts | Best ecosystem for AI, audio and video |

Background analysis: Claude Doc "Podcat – Analisi e bozza requisiti", snapshot in [`analisi-requisiti.md`](analisi-requisiti.md).
