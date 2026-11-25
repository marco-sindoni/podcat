# Decision log

Newest first. Rules that follow from a decision are also written into the constitution.

| Date | Decision | Rationale |
| --- | --- | --- |
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
