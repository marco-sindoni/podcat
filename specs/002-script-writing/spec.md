# Feature Specification: Script writing for the four cats

**Feature Branch**: `002-script-writing`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Script writing for Podcat (spec 002): from the story Marco picked (daily) or the weekly picks, write an Italian comedy script for the four cats (Flanella host, sarcastic, opens and has the last word; Fuzz hothead escalating to the absurd; Feedback slow philosopher with the final punchline; Vinile grumpy 90s nostalgic, culture/entertainment expert), as a seasoned comedy writer, then a second "head writer" review pass; daily reel ~30 s (70-90 words), weekly episode ~2 min (280-320 words, Saturday list, Sunday publication), "Giovedì buone notizie" warm tone on Thursdays; split into scenes (who speaks, shot, news image staging mode rotating A/B/C never repeated between consecutive videos); deliver as commentable document Marco approves via comments, revisions until approval; recorded in tracking/ as Markdown. CapCut package (spec 003) out of scope. Low cost first."

Covers requirements RF-03, RF-04 and RF-05 of `docs/analisi-requisiti.md`. Input comes from spec 001
(the story Marco picked in a daily or weekly shortlist). Out of scope: the CapCut package with
visual prompts and the Fotor prompt for the news image, YouTube title, description and hashtags
(RF-13, spec 003); episode and asset tracking beyond the script record (RF-10, spec 004).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Daily reel script from the picked story (Priority: P1)

As soon as Marco picks the day's story, he receives a ready-to-read Italian script for a 30-second
reel: the four cats' lines in order, each tagged with the speaker, 70–90 spoken words in total.
Flanella opens and closes, Fuzz escalates the story to the absurd, Feedback lands the unexpected
punchline, Vinile brings the nineties comparison (and leads when the story is culture,
entertainment or music). The script has been written by a "comedy writer" pass and then reworked
by a "head writer" pass that sharpens jokes, cuts flat lines and checks length, voice and rules.

**Why this priority**: The script is the editorial core of every episode and the step that turns a
news item into Podcat content. With only this story Marco can already record the reel in CapCut.

**Independent Test**: With a picked story in `tracking/news/`, ask for the script; check that a
script file appears under `tracking/scripts/` with 70–90 spoken words, Flanella's line first and
last, a Feedback punchline just before Flanella's closing line, every line attributed to one of
the four cats, and the head writer's notes listing what was changed.

**Acceptance Scenarios**:

1. **Given** Marco has picked a story in today's daily shortlist, **When** the script step runs,
   **Then** a script is created with 70–90 spoken words, lines only from the four cats, Flanella
   first and last, and Feedback's punchline as the second-to-last line.
2. **Given** the picked story has a sensitivity flag (politics, health, legal, finance), **When**
   the script is written, **Then** no cat gives advice or takes a party's side, and the satire
   targets facts and the powerful only.
3. **Given** a script for that story already exists, **When** the step runs again, **Then**
   nothing is regenerated or paid for and the existing script is shown, unless Marco explicitly
   asks for a new draft.
4. **Given** the comedy writer's draft is outside 70–90 words or breaks a character rule, **When**
   the head writer pass runs, **Then** the final draft respects the limits, and the notes say what
   was fixed.

---

### User Story 2 - Review by comments until approval (Priority: P1)

Marco receives each script as a commentable document in Italian. He comments on single lines
("più cattiva", "questa non fa ridere", "togli il riferimento a X") or on the whole script. Each
round of comments produces a new version that changes only what was commented, keeps the rest
untouched, and answers each comment briefly. When Marco writes "approvato" (or equivalent), the
script is locked and marked approved; only an approved script can go to production.

**Why this priority**: The constitution's approval gate (principle II) is non-negotiable: no
script reaches CapCut without Marco's approval.

**Independent Test**: Publish a script, add two comments on two different lines, run the revision;
check that version 2 changes those two lines only, that each comment gets a short answer, and that
after "approvato" the script record shows `approved` with the date and version.

**Acceptance Scenarios**:

1. **Given** a script document with comments on specific lines, **When** the revision runs,
   **Then** a new version replaces only the commented lines (and lines that must change to keep
   the joke coherent, listed explicitly), the word count stays within limits, and the document
   shows the new version.
2. **Given** Marco asks to rewrite everything ("rifalla da capo", "cambia angolo"), **When** the
   revision runs, **Then** a fresh draft with a different comic angle is written through both
   passes.
3. **Given** Marco approves, **When** the approval is recorded, **Then** the script status becomes
   `approved`, the story moves to `used`, and further comments do not change the approved text
   unless Marco reopens it.
4. **Given** Marco changes his mind about the story before approving, **When** he picks another
   candidate, **Then** the old script is marked `discarded`, its story goes back to `candidate`,
   and a new script is written for the new pick.

---

### User Story 3 - Scenes and news image placement (Priority: P2)

Every script is split into scenes: for each scene, who speaks, a shot taken from a fixed list
(e.g. wide shot of the four armchairs, close-up of one cat, two-shot, news image), an estimated
duration, and the point where the episode's news image appears, with its staging mode (A: tavern
TV, B: full-screen cut-in with an off-screen line, C: a cat holding a newspaper or photo) and the
line that comments it. The mode is chosen automatically so that it never repeats the mode of the
previous video (daily and weekly counted together).

**Why this priority**: Marco needs scene directions to assemble the video, and the constitution
requires the news image and the mode rotation; the lines alone are still usable without it.

**Independent Test**: Write two scripts in a row; check that each has a scene list whose durations
add up to the target length (±5 s for the reel, ±15 s for the weekly), exactly one news image
placement with a mode, and that the two scripts use different modes.

**Acceptance Scenarios**:

1. **Given** the previous approved script used mode A, **When** a new script is written, **Then**
   its news image uses mode B or C, and the choice is recorded in the script file.
2. **Given** mode C is chosen, **When** the scenes are written, **Then** the cat holding the
   newspaper or photo is the one who speaks about it in that scene.
3. **Given** Marco comments asking for a different mode, **When** the revision runs, **Then** the
   mode changes only if it still differs from the previous video's mode; otherwise the document
   explains why.

---

### User Story 4 - "Giovedì buone notizie" (Priority: P2)

On Thursdays the reel opens with the "Giovedì buone notizie" slot: Flanella introduces it with a
short fixed formula over the gnocchi sting, and the tone is warm. The cats stay witty, but jokes
are about themselves and the situation, never aimed at the people in the story; Fuzz's outrage
turns into enthusiasm or into outrage at something trivial and harmless.

**Why this priority**: A recurring slot already in the constitution, but the daily flow works
without it.

**Independent Test**: Write the script for a Thursday story; check that it opens with the slot
formula, marks the sting scene, and that the head writer notes confirm no joke targets the people
in the story.

**Acceptance Scenarios**:

1. **Given** the picked story comes from a Thursday shortlist, **When** the script is written,
   **Then** it starts with Flanella's slot formula, the first scene is the gnocchi sting, and the
   word count (excluding the sting) stays within 70–90 words.
2. **Given** a draft line mocks a person in the positive story, **When** the head writer pass
   runs, **Then** that line is rewritten and the change is listed in the notes.

---

### User Story 5 - Comic or pungente register (Priority: P1)

Since spec 001 amendment A1 every story carries a tone: `comico` (about four stories in five, plus
good news on Thursdays) or `pungente` (about one in five: a sharper or more serious story). A
comico story gets a joke-driven script. A pungente story gets satire, a pointed remark and a
moment that makes people think: fewer gags, the laugh comes from the irony of the facts, and the
close leaves a thought rather than a gag. The four cats and the fixed structure stay the same.

**Why this priority**: Every pick from now on has a tone, and a pungente story written as a string
of gags (or a comic one written as a sermon) would be the wrong episode.

**Independent Test**: Write one script for a `comico` story and one for a `pungente` story; check
that each records its tone, that the pungente one has Feedback's line as a reflection that still
lands with irony and Flanella's close as a pointed remark, and that the head writer notes confirm
the register.

**Acceptance Scenarios**:

1. **Given** the picked story has tone `pungente`, **When** the script is written, **Then** the
   satire targets facts and the powerful, Fuzz's escalation is aimed at the absurdity of the facts
   (never at victims), Feedback's final line is a reflection with an ironic twist, and Flanella
   closes with a pointed remark.
2. **Given** the picked story has tone `comico`, **When** the script is written, **Then** it is
   joke-driven, with an absurd escalation and a surprising punchline.
3. **Given** Marco comments "più leggera" or "più pungente", **When** the revision runs, **Then**
   the register changes accordingly and the script records the new tone.

---

### User Story 6 - Weekly episode script (Priority: P3)

On Saturday, after Marco picks from the weekly shortlist, he receives a script for the Sunday
episode of about 2 minutes (280–320 words) in which all four cats have room: a cold open, the story
told and argued through, at least one escalation by Fuzz and one nostalgic detour by Vinile,
Feedback's punchline and Flanella's sign-off. It follows the same two passes, scenes and approval
flow as the reel.

**Why this priority**: One episode a week; it reuses everything built for the reel.

**Independent Test**: With a picked weekly story, ask for the weekly script; check 280–320 words,
all four cats with at least two lines each, scene durations summing to about 2 minutes, and a
staging mode different from the last daily reel's.

**Acceptance Scenarios**:

1. **Given** Marco picked a story in the Saturday weekly shortlist, **When** the script step runs,
   **Then** a weekly script with 280–320 words is created and delivered as a commentable document
   on Saturday, so it can be approved and published on Sunday.
2. **Given** the weekly story was already used in a daily reel, **When** the weekly script is
   written, **Then** it takes a new angle or a new development and does not reuse the reel's jokes.

---

### Edge Cases

- The picked story has too little substance for jokes: the script is still written, and the head
  writer notes say it is weak and suggest picking another candidate.
- The draft repeats an opening, catchphrase or joke structure used in one of the last 7 scripts:
  the head writer replaces it (verbal tics such as "Ai miei tempi…" appear sparingly, not in every
  script).
- A line names a real person: allowed only for public figures in the story, as satire of facts or
  of the powerful; never private individuals, never vulnerable groups.
- The monthly budget cap would be exceeded by a paid step: the step stops before running, tells
  Marco, and no partial script is saved.
- Marco comments on an old version after a newer one exists: the comment is applied to the latest
  version if the line still exists; otherwise the answer says the line has already changed.
- A revision would push the word count out of limits: the revision trims or extends other lines
  and lists them.
- No previous video exists (first script ever): any mode can be chosen.
- Marco never approves a daily script by the end of the day: the script stays in `review`; nothing
  is published and the next day starts normally.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST write a script only for a story whose status is `chosen` in a daily
  or weekly shortlist, and MUST read the story record (title, summary, category, sources,
  sensitivity flags, tone, Thursday flag) as its only news input.
- **FR-002**: The system MUST write each script in Italian, in two passes: a comedy writer draft,
  then a head writer pass that rewrites weak lines, enforces length and character rules, and
  produces short notes (in Italian) on what it changed and why.
- **FR-003**: Each line MUST belong to exactly one of the four cats, and the writing MUST follow
  each cat's sheet in `bible/characters/` (role, personality, verbal tics, evolution log). Fixed
  structure: Flanella has the first and the last line; Feedback has the punchline immediately
  before Flanella's last line; Fuzz escalates at least once; Vinile has at least one nineties
  comparison and leads on culture, entertainment and music stories.
- **FR-004**: A daily reel script MUST contain 70–90 spoken words (about 30 s); a weekly script MUST
  contain 280–320 spoken words (about 2 min) with at least two lines per cat. Stage directions and
  the Thursday sting are not counted.
- **FR-005**: Each script MUST be split into scenes, each with: number, speaker(s), shot from a
  fixed list, estimated duration in seconds, and the lines spoken in it. Durations MUST add up to
  the target length within ±5 s (reel) or ±15 s (weekly).
- **FR-006**: Each script MUST place the news image exactly once, with its staging mode (A, B or C
  per `bible/prompts/news-image-modes.md`), the scene where it appears and the line that comments
  it; the mode MUST differ from that of the most recent approved script (daily and weekly
  together), and the chosen mode MUST be recorded in the script file.
- **FR-007**: Scripts MUST comply with the constitution's content rules: comment on facts without
  copying source text; satire targets facts and the powerful, never vulnerable groups; no cat gives
  health, legal or financial advice; politics never partisan; on Thursdays no joke targets the
  people in the story.
- **FR-008**: The system MUST avoid repetition: the head writer pass MUST compare the draft with
  the last 7 scripts and replace repeated openings, closing lines, catchphrases used in a row and
  recycled jokes.
- **FR-009**: On Thursdays the script MUST start with Flanella's "Giovedì buone notizie" formula
  over the gnocchi sting scene and use the warm tone defined in the constitution.
- **FR-010**: The system MUST deliver every script version to Marco as a commentable document in
  Italian, containing the lines by cat, the scenes, the news image placement, the word count and
  estimated duration, and the head writer's notes; the link MUST be stored in the script file,
  which stays the source of truth.
- **FR-011**: The system MUST apply Marco's comments as a new version that changes only the
  commented lines plus any lines that must change for coherence (listed), keeps all rules
  (FR-003 to FR-009), answers each comment briefly, and keeps previous versions readable.
- **FR-012**: The system MUST record Marco's approval (date and version) in the script file, set
  the script to `approved`, set the story to `used`, and refuse to change an approved script
  unless Marco explicitly reopens it.
- **FR-013**: The system MUST store each script as a Markdown file with YAML front matter under
  `tracking/scripts/`, readable and editable by hand; if Marco edits a line by hand, the next
  revision keeps his edit.
- **FR-014**: Each step MUST be idempotent: re-running it for a story that already has a script
  MUST reuse it and MUST NOT repeat paid steps unless a new draft is explicitly requested.
- **FR-015**: The system MUST record the cost of every paid step in the shared monthly cost ledger
  and refuse to start a paid step once the 50 USD monthly cap would be exceeded.
- **FR-016**: When Marco picks a story from the phone (as in spec 001), the daily script MUST be
  written and its document delivered without Marco's computer, in the same cloud flow.
- **FR-020**: The system MUST read the story's tone (`comico` or `pungente`, from spec 001 A1) and
  write the script in the matching register: joke-driven for `comico` (and Thursday good news);
  satire, pointed remarks and a closing thought with an ironic twist for `pungente`. The tone MUST
  be recorded in the script file and shown in the document; Marco can change it with a comment.
- **FR-017**: [NEEDS CLARIFICATION: Should the document also offer alternative punchlines? Option
  A: one final version only (cheapest, simplest); option B: the final version plus 2 alternative
  endings (Feedback's punchline + Flanella's close) that Marco can pick with a comment such as
  "finale 2".]
- **FR-018**: [NEEDS CLARIFICATION: Must every cat speak in every 30-second reel? Option A: yes,
  all four always (consistent cast, but shorter lines); option B: at least Flanella, Feedback and
  one of Fuzz or Vinile, chosen by the story (more room for the joke).]
- **FR-019**: [NEEDS CLARIFICATION: What does the weekly episode cover? Option A: the one story
  picked from the weekly shortlist, in depth; option B: the picked story plus a quick round-up of 2
  more stories from the week (about 20 s each).]

### Key Entities

- **Script**: one script for one story and output type (daily or weekly). Story id, kind, date,
  Thursday flag, tone (`comico` or `pungente`), status (`draft`, `review`, `approved`, `discarded`), current version, versions,
  staging mode of the news image, word count, estimated duration, document link, approval date and
  version, cost.
- **Script version**: the full text of one version: lines (speaker, text), scenes (number,
  speakers, shot, duration, lines), news image placement (scene, mode, commenting line), head
  writer notes, answers to Marco's comments, word count.
- **Comment**: Marco's note on a line or on the whole script, the version it refers to, and the
  answer given in the next version.
- **Story** (from spec 001): read as input; its status moves to `used` on approval or back to
  `candidate` when its script is discarded.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The daily script document is ready within 10 minutes of Marco's pick, without any
  action from him.
- **SC-002**: 100% of delivered scripts respect the word limits, the fixed structure (Flanella
  first and last, Feedback's punchline before the close) and the mode rotation, checked
  automatically before delivery.
- **SC-003**: Over the first 4 weeks, Marco approves at least 4 daily scripts out of 5 within two
  rounds of comments.
- **SC-004**: Over the first 4 weeks, 0 approved scripts contain advice, partisan politics or jokes
  against vulnerable groups or against the people in a Thursday story, as checked by Marco.
- **SC-005**: A daily script (both passes) costs under 0.05 USD and each revision round under
  0.03 USD; scripts stay under 5 USD per month in total.
- **SC-006**: Re-running the script step for a story that already has a script costs nothing and
  changes nothing.
- **SC-007**: Each weekly script is delivered on Saturday the same day as Marco's pick, so it can
  be approved and published on Sunday.

## Assumptions

- The script writer reads the character sheets and the bible; updating the characters' evolution
  logs after an episode is left to spec 004 (tracking), or done by hand.
- The fixed shot list is part of the bible and is proposed during planning (e.g. wide shot of the
  four armchairs, single close-up per cat, two-shot Fuzz/Vinile, news image).
- Speaking rate for the duration estimate: about 2.6 words per second for Italian CapCut voices,
  with Feedback slower; calibrated after the first recordings (B-012).
- The commentable document is created from the project chat with Claude, the same way as the news
  shortlists (spec 001); comments are read from that document and written back to the script file.
- The model used for each pass is the cheapest one whose quality Marco accepts; the plan proposes
  it and estimates the cost.
- The script document does not include visual prompts, the Fotor prompt for the news image, or
  the YouTube title and description: those belong to the CapCut package (spec 003).
- The first real input is the story picked on 2026-11-27, "Hacker fanno impazzire i frigoriferi in
  Slovenia" (tone `comico`); it is the first end-to-end test of this feature.
- File names, field names and logs are in English; all script content and notes are in Italian.
