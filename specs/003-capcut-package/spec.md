# Feature Specification: CapCut package for each episode

**Feature Branch**: `003-capcut-package`

**Created**: 2026-11-28

**Status**: Approved by Marco on 2026-11-28 (answers: Q1 B with at most 30% reused clips per video, Q2 B, Q3 A)

**Input**: User description: "Spec 003: the package Marco needs to edit each episode by hand in
CapCut (phase 1). It covers the news image, the script and subtitles, which cats are on screen and
their expressions, the staging mode, and anything else needed to go from an approved script to a
published video. CapCut voices with one fixed voice per cat, 9:16, soft 3D cartoon, Fotor for
images (API in phase 2), a dedicated image per news story with three rotating staging modes, assets
outside git, Markdown tracking, budget under 50 USD a month. Everything must run in the cloud: Marco
works from his phone with his computer off."

Covers requirement RF-13 of `docs/analisi-requisiti.md` (CapCut package, YouTube title, description
and hashtags). Input: a script approved in spec 002. Out of scope: episode and asset records with
the published video link and the asset library catalogue (RF-10, spec 004); any automation of
Fotor, CapCut or YouTube (phase 2, B-001 to B-007).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Scene-by-scene editing guide (Priority: P1)

As soon as Marco approves a script, he receives the CapCut package: one block per scene, in order,
that tells him everything he needs to build that piece of the timeline without thinking: start time
and duration, the shot, which cats are on screen, what each one is doing (who talks, who reacts and
with which face or gesture), which library image or clip to use, the line(s) spoken with the cat's
fixed CapCut voice, and the caption text. He works through it top to bottom, on his phone, copying
one line at a time.

**Why this priority**: It is the package's reason to exist: it turns an approved script into a
video Marco can assemble in CapCut in a short session.

**Independent Test**: Approve a script; check that the package has one block per scene in the
script's order, that every spoken line appears exactly once with its cat and voice, that every cat
listed as reacting in the script appears on screen with its direction, and that the start times add
up to the script's estimated duration.

**Acceptance Scenarios**:

1. **Given** Marco approves a daily script, **When** the package step runs, **Then** a package
   is created with one block per scene containing: scene number, start time and duration, shot,
   cats on screen, the action or expression of each cat on screen, the asset to use, the lines with
   the speaker's CapCut voice, and the caption text.
2. **Given** a cat has no lines in the script, **When** the package is built, **Then** that cat
   still appears in at least one block with its reaction (face or gesture), as the script requires.
3. **Given** a line contains numbers, abbreviations, foreign names or a year such as "'94",
   **When** the package is built, **Then** the voice text spells them as they must be read
   ("novantaquattro") while the caption text keeps the written form, and the two are shown apart.
4. **Given** the script is not approved, **When** the package step runs, **Then** nothing is
   built and Marco is told the script must be approved first.

---

### User Story 2 - The news image, ready for Fotor (Priority: P1)

The package contains the prompt for the episode's dedicated news image, ready to paste into Fotor,
built for the staging mode chosen in the script (A: the tavern's CRT TV, B: 2–3 s full-screen
cut-in with a slow zoom, C: a cat holding a newspaper or photo), with the scene and second where it
appears, the line that comments it, how to place it in CapCut for that mode, and the file name to
save it under.

**Why this priority**: Every episode MUST have its own news image (constitution, principle I); it is
the one asset Marco must create each time.

**Independent Test**: Build packages for three scripts with modes A, B and C; check that each prompt
follows the template of its mode, includes the show's style block, describes the subject without
real people's faces, logos or brand names, and that mode C names the cat holding it, who is the cat
speaking in that scene.

**Acceptance Scenarios**:

1. **Given** an approved script with news image mode A, **When** the package is built, **Then** the
   prompt is for an image readable on a small screen, and the placement says to put it on the TV
   screen of the tavern wide shot in the given scene.
2. **Given** mode C held by Vinile, **When** the package is built, **Then** the prompt describes
   Vinile with his fixed look holding the newspaper or photo, with the expression of that scene, and
   says which reference image to use in Fotor so he looks the same as always.
3. **Given** the story is about a real person, **When** the prompt is written, **Then** the person
   appears only as a faceless silhouette or through objects and symbols, never as a recognisable
   face, and no logo or brand is named.
4. **Given** the package exists, **When** Marco reads it, **Then** he also sees a second, different
   prompt for the same subject to try if the first result is poor.

---

### User Story 3 - Assets to reuse or to create (Priority: P2)

Before the scene blocks, the package lists every visual asset the episode needs (tavern wide shot,
close-ups, reaction images or clips per cat and expression, the TV close-up, the gnocchi sting on
Thursdays, the news image), marking for each one whether it already exists in the approved library
(with its file name) or still has to be made, in which case it gives the ready-to-paste prompt
(Fotor for images, CapCut image-to-video for clips) from the bible's prompt library.

**Why this priority**: Reference images are always reused (consistency), but clips are mostly new
each episode so videos do not look alike (at most 30% of the duration from reused clips, FR-018);
the library is still empty today, so the first packages must tell him what to create.

**Independent Test**: Build a package with an empty asset library; check that every asset is marked
"da creare" with its prompt. Mark some library assets as approved; build again; check that those
are marked "già pronto" with their file name and no prompt.

**Acceptance Scenarios**:

1. **Given** no approved reference asset exists yet, **When** the package is built, **Then** every
   needed asset is listed as "da creare", with its prompt and the reference image to start from.
2. **Given** the library has an approved "Fuzz outraged" clip and reused clips still cover less
   than 30% of the video, **When** a scene needs Fuzz outraged, **Then** the package may point to
   that clip and gives no prompt for it; once the 30% is reached, it gives a new clip prompt instead.
3. **Given** a scene needs an expression or action not in the bible's expression list, **When** the
   package is built, **Then** it maps it to the closest existing expression and shows the script's
   original direction next to it, so Marco can decide.

---

### User Story 4 - Publishing kit (Priority: P2)

The package ends with what Marco needs to publish: three title options in Italian (short, with the
hook), a description that summarises the story in the cats' tone and credits the news sources with
their links, a few hashtags, the reminder to set the YouTube "AI use" disclosure to Yes, and a short
final checklist (9:16, captions on, news image present, no logos, voices as in the bible).

**Why this priority**: Required by RF-13 and by the constitution (AI disclosure, sources); it saves
time at upload, but the video can be edited without it.

**Independent Test**: Build a package; check three Italian titles within the platform length limit,
a description that names every source with its link, the AI disclosure line, and the checklist.

**Acceptance Scenarios**:

1. **Given** an approved script, **When** the package is built, **Then** it has three titles of at
   most 70 characters each, a description of at most 5 lines plus the source links, and 3 to 6
   hashtags including the channel's fixed one.
2. **Given** a Thursday script, **When** the package is built, **Then** the titles and description
   carry the "Giovedì buone notizie" slot name.
3. **Given** the story has a sensitivity flag, **When** the publishing text is written, **Then** it
   follows the same content rules as the script (no partisan politics, no advice).

---

### User Story 5 - Changes by comment (Priority: P2)

Marco receives the package as a commentable document, like the scripts. He can comment on the news
image prompt ("più semplice", "metti un frigo più grande"), on a title, on the description or on a
scene's asset choice; each round produces a new package version that changes only what was
commented. The script lines cannot be changed from the package: to change a line he reopens the
script (spec 002), and the package is rebuilt when the script is approved again.

**Why this priority**: The first Fotor results will need tuning, but the package is usable as built.

**Independent Test**: Comment on the image prompt and on title 2; run the revision; check that only
those two parts changed and that each comment gets a short answer.

**Acceptance Scenarios**:

1. **Given** comments on the image prompt and a title, **When** the revision runs, **Then** a new
   version changes only those parts and answers each comment.
2. **Given** a comment asks to change a script line, **When** the revision runs, **Then** nothing
   changes and the answer explains how to reopen the script.
3. **Given** Marco reopens and re-approves the script, **When** the package step runs, **Then** the
   old package is marked outdated and a new one is built from the new script.

---

### User Story 6 - Subtitles that are always right (Priority: P1)

Subtitles are always on (constitution). In phase 1 Marco generates CapCut's auto-captions from the
finished voice track, so they are always in time with the voices. The package gives him a subtitle
section with: the fixed caption style (font, size, outline, position inside the Shorts safe area,
at most two lines per caption), the color of each cat, the reference text of every line split into
caption chunks as they should appear, and a short list of the words to check, because recognition
gets them wrong: the cats' names, people, places, foreign words, and every line whose voice text
differs from the written text ("novantaquattro" must read "'94").

**Why this priority**: Most viewers watch Shorts without sound; wrong or unreadable captions make
the video unwatchable, and a misspelled name looks careless.

**Independent Test**: Build the package for the fridge script; check that the subtitle section has
the style, the four colors, every line split into chunks of at most two lines within the character
limit, and a words-to-check list that contains Flanella, Fuzz, Tolmino, Salvini and line 5 ('94).

**Acceptance Scenarios**:

1. **Given** any approved script, **When** the package is built, **Then** the subtitle section
   lists every line in order, with speaker color and chunks within the limits in
   `config/package.yaml`.
2. **Given** a line whose voice text differs from the written text, **When** the package is built,
   **Then** that line is in the words-to-check list with the text the caption must show.
3. **Given** a line names a cat, a person or a place, **When** the package is built, **Then** that
   name is in the words-to-check list with its exact spelling.
4. **Given** the caption style is changed in the bible, **When** the next package is built,
   **Then** it shows the new style.

---

### User Story 7 - Weekly episode and Thursday slot (Priority: P3)

The same package works for the Sunday weekly episode (about 2 minutes, all four cats) and for the
Thursday "Giovedì buone notizie" reel, which opens with the gnocchi sting: the package gives the
sting asset, its 2–3 s duration, and the on-screen title "Giovedì buone notizie" with the words
"Giovedì" and "gnocchi" in red, as the bible requires.

**Why this priority**: One weekly episode and one Thursday reel per week; they reuse everything
above.

**Independent Test**: Build a package for a weekly script and one for a Thursday script; check
durations (about 2 min, about 45 s plus sting), that all four cats speak in the weekly, and that the
Thursday package starts with the sting block and its title styling.

**Acceptance Scenarios**:

1. **Given** an approved weekly script, **When** the package is built on Saturday, **Then** it is
   ready the same day so Marco can edit and publish on Sunday.
2. **Given** an approved Thursday script, **When** the package is built, **Then** the first block
   is the gnocchi sting with its asset, duration and title styling.

---

### Edge Cases

- A cat's CapCut voice is still "TBD" in the bible: the package is built, shows "voce da scegliere"
  for that cat, and repeats the voice guide from the bible (e.g. "calda, bassa e secca").
- The script's scene durations differ from the real voice lengths: start times are marked as
  estimates; the order and content of the blocks are what matter.
- Mode B needs an off-screen line: the block says the voice plays over the full-screen image and
  which cat speaks off screen.
- The story's source links are missing or broken: the description lists the outlet names and the
  package flags the missing link.
- A paid step would exceed the 50 USD monthly cap: the step stops before running, tells Marco, and
  no partial package is saved.
- The package is asked for again with nothing changed: the existing package is shown, nothing is
  paid for again.
- Two consecutive scenes use the same shot: the package says Marco can keep a single clip running
  over both.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST build a package only from a script with status `approved` (spec 002),
  reading the approved version, the story record, the bible (character sheets with looks, voices,
  subtitle colors; shot list; prompt library) and the asset library records as its only inputs.
- **FR-002**: The package MUST contain, in this order: a header (story, date, kind, tone, Thursday
  flag, estimated duration, news image mode, version), the asset list (FR-006), the news image
  (FR-004), the scene blocks (FR-003), the voice sheet (FR-005), the subtitle section (FR-007), the publishing kit (FR-008) and the
  final checklist (FR-009).
- **FR-003**: Each scene of the script MUST become one block with: scene number; estimated start
  time and duration; shot (name from the shot list); the cats on screen, derived from the shot and
  the seating (left to right Fuzz, Flanella, Vinile, Feedback); for each cat on screen, its state
  (talking, or the script's reaction direction, or a neutral "ascolta"); the asset to use for that
  shot and state; the lines spoken, each with cat, CapCut voice and voice text; the caption text.
- **FR-004**: The news image section MUST give: the mode and its CapCut placement instructions; the
  scene, estimated second and commenting line; a main Fotor prompt in English following the mode's
  template in `bible/prompts/news-image-modes.md` plus the style block and negative hints; one
  alternative prompt; for mode C the holding cat's fixed look, expression and reference image; the
  suggested file name. No prompt may describe a real person's face, a logo or a brand.
- **FR-005**: The voice sheet MUST list every line in order with the cat, the cat's fixed CapCut
  voice from the bible (or "voce da scegliere" with the voice guide when not yet set), and the voice
  text, in which numbers, years, abbreviations and foreign names are written as they must be spoken;
  lines whose voice text differs from the caption MUST be marked.
- **FR-006**: The asset list MUST name every visual asset the episode needs and mark each as
  "già pronto" (approved in the library, with file name) or "da creare" (with the ready-to-paste
  prompt from `bible/prompts/`, the tool, and the reference image to start from). Expressions not in
  the bible's list MUST be mapped to the closest listed one, showing the original direction.
- **FR-007**: The package MUST contain a subtitle section (User Story 6): the caption style from
  the bible (font, size, outline, position inside the YouTube Shorts safe area, at most two lines
  and a maximum number of characters per line); each cat's subtitle color; every line in order in
  its written form, split into caption chunks within those limits, one speaker per chunk; and a
  words-to-check list with the exact spelling of the cats' names, people, places and foreign words
  in the lines and of every line whose voice text differs from the written text. In phase 1
  captions are CapCut auto-captions generated from the finished voice track and corrected against
  this section; no subtitle file is produced (phase 2, B-004).
- **FR-008**: The publishing kit MUST contain, in Italian: three title options of at most 70
  characters; a description of at most 5 lines in the cats' tone that credits every source outlet
  with its link; 3–6 hashtags including a fixed channel hashtag; the reminder to set the "AI use"
  disclosure to Yes. On Thursdays titles and description carry the slot name. The same content rules
  as scripts apply (constitution, principle III).
- **FR-009**: The final checklist MUST include at least: 9:16 format, captions on and corrected,
  news image present in its mode, no logos or real faces, each cat with its fixed voice, AI
  disclosure set, and Marco's own approval of the final cut before publishing.
- **FR-010**: On Thursdays the first block MUST be the gnocchi sting (2–3 s) with its asset and the
  on-screen title "Giovedì buone notizie" with "Giovedì" and "gnocchi" in red or another standout
  color.
- **FR-011**: The system MUST deliver every package version to Marco as a commentable document in
  Italian, readable and copyable on a phone, and store the link in the package file, which stays the
  source of truth.
- **FR-012**: The system MUST apply comments as a new version that changes only the commented parts
  (image prompts, titles, description, hashtags, asset choices, voice text), answers each comment
  briefly, and keeps previous versions readable. Comments on script lines MUST NOT change the
  package; the answer explains how to reopen the script.
- **FR-013**: When the script is reopened, the package MUST be marked `outdated`; a new approval
  builds a new package.
- **FR-014**: The system MUST store each package as a Markdown file with YAML front matter under
  `tracking/`, next to its script, readable and editable by hand; no binary asset is stored in git.
- **FR-015**: Each step MUST be idempotent: re-running it for a script that already has a current
  package MUST reuse it and MUST NOT repeat paid steps.
- **FR-016**: The system MUST record the cost of every paid step in the shared monthly ledger and
  refuse to start one once the 50 USD cap would be exceeded.
- **FR-017**: The package MUST be built and delivered right after the approval, in the same cloud
  flow as spec 002, without Marco's computer.
- **FR-018**: Clips reused from earlier episodes or from the library MUST cover at most 30% of the
  video's estimated duration; every other scene MUST get a new clip made for this episode, with a
  ready-to-paste CapCut image-to-video prompt in English that starts from an approved reference
  image (or from the episode's news image) and describes the scene's action and expressions. One
  new clip MAY cover consecutive scenes with the same shot. The package MUST show the reused share
  (percent of duration) and the number and total seconds of new clips, and the automatic check MUST
  fail a package over 30%. Reused clips MUST be the least recently used ones that fit.
- **FR-019**: The package MUST give the sound plan: tavern ambience under the whole video, one or
  two sound effects tied to a scene (e.g. on Fuzz's escalation or the punchline), and the fixed
  theme tune at the opening and the closing, laid under the first and last scene so the video does
  not get longer. All music and effects come from sources licensed for YouTube monetisation; the
  theme tune, the ambience and their sources are recorded once in the bible.
- **FR-020**: The publishing kit is for YouTube only: Shorts for the daily reel, a regular video
  for the Sunday episode.

### Key Entities

- **Package**: one per approved script. Script id and approved version, kind, date, status
  (`ready`, `outdated`), current version, versions, document link, cost.
- **Package version**: header, asset list, news image (mode, scene, second, commenting line,
  prompts, file name, placement), scene blocks, voice sheet, captions, publishing kit, checklist,
  answers to comments.
- **Scene block**: scene number, start, duration, shot, cats on screen with state, asset per cat or
  shot, lines with voice text and caption.
- **Asset need**: asset kind (reference image, clip, news image, sting), cat and expression or set
  piece, status (`ready` with file name, `to-create` with prompt and reference).
- **Script** (spec 002) and **Story** (spec 001): read as input.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The package document is ready within 10 minutes of Marco's approval, with no action
  from him and with his computer off.
- **SC-002**: 100% of packages contain every spoken line of the approved script exactly once, every
  scene, and a news image in the script's mode, checked automatically before delivery.
- **SC-003**: Using only the package (no need to reopen the script), Marco edits a daily reel in
  CapCut in at most 45 minutes once the library is populated.
- **SC-004**: Over the first 4 weeks, at least 3 news images in 4 are usable at the first or second
  prompt tried.
- **SC-005**: 0 packages contain prompts with real people's faces, logos or brand names.
- **SC-006**: A package costs under 0.03 USD and each comment round under 0.02 USD; packages stay
  under 2 USD a month.
- **SC-007**: In 100% of packages reused clips cover at most 30% of the duration.
- **SC-008**: Over the first 4 weeks, 0 published videos have a misspelled cat, person or place name
  or a caption that does not match the line, as checked by Marco.

## Decisions (Marco, 2026-11-28)

- **Q1 – Clips**: each episode gets mostly new clips. Clips taken from earlier episodes or from the
  reusable library may cover at most 30% of the video's duration; the rest is new clips made for
  this episode (FR-018).
- **Q2 – Sound**: tavern ambience under the whole video, one or two suggested sound effects, and a
  fixed short theme tune for opening and closing, chosen once and recorded in the bible (FR-019).
- **Subtitles** (Marco, 2026-11-28, after the first review): a dedicated story (User Story 6) and
  FR-007 rewritten: CapCut auto-captions from the voice track, with style, colors, caption chunks
  and words to check given by the package. [Method pending Marco's confirmation.]
- **Q3 – Platforms**: YouTube only (Shorts for the daily reel, the Sunday episode) (FR-020).

## Assumptions

- The package's order and content come from the approved script; the package never rewrites lines,
  scenes or the staging mode (they were approved in spec 002).
- Asset library records live under `tracking/assets/` and are filled during the visual test session
  (B-012); until then every asset is "da creare". Moving files into `$PODCAT_ASSETS_DIR` and
  recording the published video belong to spec 004.
- Prompts for Fotor and CapCut stay in English (the bible's rule); everything else in the package
  is Italian.
- Marco can work in CapCut on his phone or on the computer; the package does not depend on either.
- The caption style is defined once in the bible (`bible/subtitles.md`) and tried in the visual
  test session (B-012, step 7.3); starting proposal: bold rounded sans-serif, each cat's color with a
  dark outline, centred in the lower-middle part of the frame above YouTube's buttons, at most 2
  lines of 32 characters.
- Estimated times use the script's per-cat speaking rates; real voice lengths are calibrated after
  the first recordings.
- Most of the package is assembled without paid calls; a cheap model writes the news image prompts,
  the voice text fixes and the publishing kit.
- New clips use CapCut AI video credits from Marco's CapCut plan, not paid per call by the
  software; the visual test session (B-012, step 6.4) measures credits per clip, and the plan checks
  that about 7 new clips per reel and 25 per weekly episode fit the plan and the 50 USD cap.
- The theme tune is chosen once by Marco (B-012) from YouTube's Audio Library or another source
  licensed for monetisation; until then the package says "sigla da scegliere".
- The first real input is the approved fridge script of 2026-11-27 (mode A, version 4).
