# Research: CapCut package

Decisions taken while planning spec 003. Format: decision, rationale, alternatives.

## R1 – One paid call, the rest plain code

- **Decision**: scene blocks, timings, cats on screen, captions, asset list, clip plan, sound plan
  and checklist are built by code. One model call writes only what needs language: news image
  prompts (main and alternative), new clip prompts, expression mapping, voice text, effects choice,
  titles, description, hashtags. If checks fail, one fix call with the problems, as in spec 002.
- **Rationale**: the package must mirror the approved script exactly; code cannot drift from it.
  Cost stays near zero (constitution V).
- **Alternatives**: a full package written by the model (risk of changed lines or missing scenes);
  no model at all (prompts and titles would be templates, repetitive: principle I).

## R2 – Model: Haiku 5.5, configurable

- **Decision**: `package_model: claude-haiku-5-5`, `package_effort: "off"` in `config/pricing.yaml`.
  Estimate: about 7k input and 3k output tokens → about 0.002 USD per package; Sonnet 5.5 would be
  about 0.045 USD, Opus 5.5 about 0.09 USD.
- **Rationale**: the creative parts are short and constrained; titles are the only part where
  quality shows, and the model is one line to change.
- **Alternatives**: Sonnet for everything (still cheap, over the SC-006 target); a second call only
  for titles on a stronger model (more moving parts). Marco went ahead with Haiku (2026-11-28); switch to Sonnet if the titles are flat.

## R3 – Cats on screen from the shot and the seating

- **Decision**: a fixed map in `config/package.yaml`: `wide` and `news-tv` → all four (seating
  Fuzz, Flanella, Vinile, Feedback); `close-X` and `react-X` → X; `two-X-Y` → X and Y;
  `news-held-X` → X; `news-cutin` and `sting-gnocchi` → none (the voice is off screen). The speaker
  is `parla`; a cat with a reaction in the script gets that direction; any other cat on screen is
  `ascolta`. A reaction for a cat not in the shot becomes a 1–1.5 s cutaway `react-X` inside the
  same block, so no reaction is lost.
- **Rationale**: the shot list already defines who is in frame; no model needed.
- **Alternatives**: ask the model (could contradict the shot).

## R4 – Expressions mapped to the bible's list

- **Decision**: the model maps each state to one key of the bible's list (`talking`, `listening`,
  `laughing`, `rolling eyes`, `outraged`, `surprised`, `moved`, `dozing`, `sipping`), keeping the
  script's Italian direction beside it. A key outside the list fails the check.
- **Rationale**: reference images and library clips are indexed by these keys (spec US3 scenario 3).

## R5 – Clip plan and the 30% reuse cap

- **Decision**: consecutive scenes with the same shot form one clip unit. Fixed branding (gnocchi
  sting, theme tune) and the mode B cut-in (a still image with a slow zoom, no clip) are excluded
  from the computation. For the other units, a library clip can be reused only if it is `approved`,
  matches the shot, cat and expression, and adding it keeps reused seconds ≤ 30% of the counted
  duration. Candidates go in this order: units whose state is `listening` or a reaction first
  (generic moments), then the rest; among matching clips the least recently used wins, where usage
  is read from existing package files. Key moments (Fuzz's escalation, Feedback's punchline, the
  news image scene) are never reused. Every other unit gets a new clip: the CapCut image-to-video
  prompt (template in `bible/prompts/clips.md`), the start image (an approved reference image of
  that cat and expression, or the tavern wide shot, or for mode C the news image itself) and a
  suggested file name.
- **Rationale**: Marco's answer to Q1; least recently used avoids the same clip in two videos in a
  row.
- **Estimate**: a 45 s reel has about 10 scenes, 7–8 units after merging, so about 6–8 new clips of
  4–5 s; a weekly about 20–25. CapCut credits per clip are measured in the visual test session
  (B-012, step 6.4). Marco's CapCut plan is not known yet: measure credits per clip in B-012 step 6.4; if about 200
  new clips a month do not fit, the fallback to propose is a still image made for the episode with
  a slow zoom counted as new.

## R6 – Voice text

- **Decision**: the model returns a `voice_text` only for lines that need it (digits, years such as
  "'94", abbreviations, foreign names); a check fails if any voice text still contains a digit.
  Captions keep the written line. Voices from `capcut_voice` in each character sheet, or
  "voce da scegliere" with the `voice_profile`.

## R7 – Sound plan

- **Decision**: new `bible/sound.md` with the theme tune, the tavern ambience and a short list of
  allowed sound effects (e.g. record scratch, rimshot, cash register, boing, crowd gasp), each with
  source and licence once chosen; all `TBD` until B-012. The model picks one or two effects with
  their scene; the theme sits under the first and the last block, the ambience under everything.
- **Rationale**: Marco's answer to Q2; licensed sources only (YouTube Audio Library or CapCut items
  marked for commercial use).

## R8 – Publishing kit

- **Decision**: three titles ≤ 70 characters; description ≤ 5 lines plus one "Fonti:" line per
  source (outlet and URL from the story record); 3–6 hashtags including the fixed `#Podcat`
  (`config/package.yaml`); fixed line "Contenuto creato con l'AI: etichetta «uso dell'AI» su Sì";
  daily = YouTube Shorts, weekly = regular video. Thursday: slot name in titles and description.
- **Alternatives**: other platforms (excluded by Marco, Q3).

## R9 – Checks

- **Decision**: every line appears once in the blocks and in the voice sheet; every scene once and
  in order; news image mode, scene and line equal to the script's; prompts end with the style block
  and include the negative hints; no real person's name in any English prompt (the model lists the
  real people in the story, and the check also uses capitalised names from the story title and
  summary that are not places in the script); reuse ≤ 30%; title, description and hashtag limits;
  every source outlet in the description; no digit in voice text; expression keys valid.
- **Rationale**: SC-002, SC-005, SC-007 checked before delivery.

## R10 – Storage and status

- **Decision**: `tracking/packages/<script-id>.md` index (`status: ready | outdated`, versions, doc
  link, cost) and one file per version. The package id equals the script id. `podcat script reopen`
  sets the package to `outdated`; building again after a new approval creates a new version from the
  new script version.
- **Alternatives**: inside `tracking/scripts/` (mixes two lifecycles).

## R11 – Asset records (minimal, owned later by spec 004)

- **Decision**: `tracking/assets/<asset-id>.md` with `kind` (`reference`, `clip`, `sting`,
  `theme`), `cat`, `expression`, `shot`, `file` (path relative to `PODCAT_ASSETS_DIR`), `status`
  (`draft`, `approved`). Only `approved` records are used. Today the folder is empty, so every asset
  is "da creare".

## R12 – Revisions by comment

- **Decision**: `podcat package revise --comments f.yaml`, same comments file shape as scripts with
  `part` instead of `line` (e.g. `image`, `image-alt`, `title-2`, `description`, `hashtags`,
  `clip-3`, `voice-5`, `effects`). The model returns changes only for those parts; code merges them
  and re-runs the checks. A comment on a line's text gets a fixed answer: "Le battute si cambiano
  dal copione: scrivi «riapri» sul copione". Cost about 0.001 USD on Haiku.

## R13 – Document

- **Decision**: Claude publishes `podcat package show` as a Claude Doc titled
  `Podcat – Pacchetto CapCut <giorno> <data>`; prompts in code blocks (one tap to copy on the
  phone), each spoken line in its own paragraph, short tables only for the asset list and the plan.

## R14 – Subtitles (added after Marco's question, 2026-11-28)

- **Decision**: CapCut auto-captions generated from the finished voice track (always in time; the
  synthetic voices are clean, so recognition is reliable), corrected against the package's subtitle
  section. The style lives in a new `bible/subtitles.md` (font, size, outline, position in the
  Shorts safe area, max 2 lines × 32 characters), tried in B-012 step 7.3. Code splits each line
  into chunks at punctuation, then at word boundaries, within the limits, one speaker per chunk.
  The words-to-check list is built by code (cat names; capitalised words in the lines; lines whose
  voice text differs) plus the model's list of people, places and foreign words.
- **Alternatives**: typing each line as a text clip and using it for text-to-speech, keeping the
  text as caption (exact text, manual timing); an SRT with estimated timings imported in CapCut
  (timings drift from the real voices; import is mainly a desktop feature). Kept as options for
  Marco; SRT export stays in phase 2 (B-004).
