# Feature Specification: Daily news gathering and verification

**Feature Branch**: `001-news-gathering`

**Created**: 2026-11-25

**Status**: Approved by Marco on 2026-11-26; amendment A1 (selection strategy) drafted 2026-11-27, pending review

**Input**: User description: "Daily news gathering and verification for Podcat: fetch the approved RSS feeds in docs/news-sources.md, filter out excluded topics, cross-check each story on at least two sources from different groups, and propose 3-5 candidate stories per day (positive story on Thursdays) for Marco to pick, recorded in tracking/ as Markdown with YAML front matter."

**Amendment A1 (2026-11-27)**: after the first real shortlists Marco found the candidates weak for
a comedy reel (hard politics that the general public does not follow, violence, a sick celebrity).
A trial on the 2026-11-27 stories showed why: ordering by importance pushed out the stories the
model itself rated funniest, only the 20 most covered stories were rated, and single-source light
stories never reached verification. A1 changes the selection strategy: FR-004, FR-005, FR-007 and
FR-008 are amended; FR-019 to FR-023 and SC-008 are new.

Covers requirements RF-01 and RF-02 of `docs/analisi-requisiti.md` and backlog item B-010
("Giovedì buone notizie"). Script writing (RF-03 onwards) is a separate feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Daily shortlist of verified stories (Priority: P1)

Every day Marco runs one command and gets a short list of 3–5 candidate stories for the daily reel.
Each candidate is confirmed by at least two approved sources from different publishing groups,
lists every confirming source with its link, carries a short neutral summary in Italian, a category,
an importance rating and a "comic potential" rating, each with a one-line reason. Marco receives the
shortlist as a commentable document. Stories on excluded topics never appear.

**Why this priority**: Without verified stories there is nothing to write about. This is the first
step of every episode and the smallest useful slice: even before scripts are automated, Marco can
use the shortlist to write or brief a reel.

**Independent Test**: Run the command on a normal weekday with the approved feeds reachable; check
that a dated shortlist file appears under `tracking/news/` with 3–5 candidates, each with ≥2
confirming sources from different groups, and that every link opens the cited article.

**Acceptance Scenarios**:

1. **Given** the approved feeds are reachable, **When** Marco runs the daily gathering, **Then** a
   shortlist for today is created with 3–5 candidates, each confirmed by at least two sources from
   different publishing groups (one source for light categories, see FR-004), ordered by comic
   potential plus clarity, each also showing its importance.
2. **Given** two outlets republish the same agency wire, **When** confirmations are counted,
   **Then** they count as one source.
3. **Given** a current-affairs, sport or culture story only appears in one approved source, or any
   story only appears in satire sources, **When** the shortlist is built, **Then** that story is not
   a candidate. *(A1)* **Given** an entertainment, music, lifestyle or oddities story appears in one
   approved starting source, **Then** it can be a candidate.
4. **Given** a story is crime news, a tragedy, clickbait, sponsored content, a rumour or based only
   on social media posts, **When** the shortlist is built, **Then** it is discarded and the reason
   is recorded in the run log.
5. *(A1)* **Given** a story about the illness or injury of a famous person, or about clashes with
   injured people, **When** the shortlist is built, **Then** it is discarded with its reason.
6. *(A1)* **Given** a story rated comic potential 2 or clarity 2, however widely covered, **When**
   the shortlist is built, **Then** it is not a candidate and the run log says why.
7. *(A1)* **Given** three eligible stories flagged politics, **When** the shortlist is built,
   **Then** only the best-ranked one is a candidate.
8. *(A1)* **Given** a widely covered but unfunny story and a less covered story rated comic 4 and
   clarity 5, **When** the shortlist is ordered, **Then** the second one comes first.
5. **Given** today's shortlist already exists, **When** Marco runs the command again, **Then**
   nothing is fetched or paid for again and the existing shortlist is shown, unless Marco
   explicitly asks for a refresh.

---

### User Story 2 - Marco picks the story (Priority: P1)

Marco reads the shortlist in the commentable document and marks one candidate as the story for the day's reel. The choice is
recorded in the shortlist file and becomes the input for the script-writing feature. Marco can
change his pick until a script has been written from it.

**Why this priority**: The constitution puts Marco in charge of editorial choices; the next feature
needs a single, explicit chosen story.

**Independent Test**: Mark a candidate as chosen (by a comment on the document, by command or by
editing the file); check that
the shortlist shows exactly one chosen story and that a story record for it exists in
`tracking/news/`.

**Acceptance Scenarios**:

1. **Given** a shortlist exists, **When** Marco picks candidate N, **Then** that candidate is
   marked as chosen, any previous pick for that day is cleared, and a story record is saved with
   all its sources.
2. **Given** none of the candidates convinces him, **When** Marco rejects the shortlist, **Then** he
   can ask for a new shortlist that excludes the rejected stories.

---

### User Story 3 - "Giovedì buone notizie" (Priority: P2)

On Thursdays the shortlist contains only positive stories from anywhere in the world (human
progress, hope, kindness) taken from the `good-news` category and still confirmed by a major
outlet or agency.

**Why this priority**: A fixed weekly slot already approved in the constitution, but the rest of the
pipeline works without it.

**Independent Test**: Run the gathering with Thursday as the date; check that every candidate is
from the `good-news` category, has a confirmation from a non-good-news approved source, and is
labelled as "Giovedì buone notizie".

**Acceptance Scenarios**:

1. **Given** today is Thursday, **When** the gathering runs, **Then** all candidates are positive
   stories from the last 7 days, each reported by at least one approved starting source.
2. **Given** today is Thursday and fewer than 3 verified positive stories are found, **When** the
   shortlist is built, **Then** Marco is shown what was found with a clear warning, and the
   positive stories of the previous 7 days that were not used are offered as backups.

---

### User Story 4 - Stories for the weekly episode (Priority: P3)

Every Saturday Marco gets a shortlist for the weekly episode, built from the week's
verified candidates and chosen stories, so the weekly episode can recap or expand the week's best
material. The weekly episode is published on Sunday.

**Why this priority**: The weekly episode depends on a week of daily data; it can come after the
daily flow works.

**Independent Test**: With at least five daily shortlists in `tracking/news/`, run the weekly
gathering and check that it proposes stories only from that week, with sources, and flags those
already used in a daily reel.

**Acceptance Scenarios**:

1. **Given** a week of daily shortlists, **When** Marco runs the weekly gathering, **Then** he gets
   3–5 candidate stories from that week, each marked "already used in reel" or "new".

---

### Edge Cases

- A feed is unreachable, slow or malformed: the run continues with the other feeds and the run log
  lists the failing feeds; if a whole category is down, the shortlist says so.
- Fewer than 3 verified stories found: the shortlist shows what was found (possibly zero) with a
  warning; it never pads the list with unverified stories.
- A story was already covered in a previous episode: it is excluded, unless there is a substantial
  new development, in which case it is marked "follow-up".
- The same story appears with different headlines in different outlets: it is grouped as one story.
- The monthly budget cap is reached and the run needs a paid step: the run stops before that step
  and tells Marco, without partial charges.
- Politics: a political story is kept only if it is a public fact suitable for satire of the
  powerful; the summary stays neutral and the rating reason never takes a party's side.
- Health, legal or financial stories: allowed as news, but the record flags them so the script
  feature keeps the cats from giving advice.
- A source in the approved list has no working RSS feed: it is recorded as "manual only" and
  ignored by the automatic run.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST read the approved sources, their categories and publishing groups
  from a single configuration derived from `docs/news-sources.md`; adding or removing a source MUST
  NOT require code changes.
- **FR-002**: The system MUST fetch recent items from every approved source with a working feed,
  covering at least the last 24 hours. The weekly run uses the stories verified by the daily runs of
  the past 7 days plus the last 24 hours, because feeds keep only one or two days of items.
- **FR-003**: The system MUST group items from different sources that report the same story.
- **FR-004**: The system MUST count a story as verified only when at least two approved sources
  from different publishing groups report it; republications of the same agency wire count once;
  `satire` sources never count; Il Post and Il Fatto Quotidiano count only as confirmations.
  *(A1)* Exception: stories in the light categories (entertainment, music, lifestyle, oddities,
  see FR-019) are verified by one approved, non-satire starting source, as on Thursdays. Current
  affairs, sport, culture and every story flagged politics, legal, health or finance keep the
  two-groups rule. The exception applies from the first grouping step, so single-source light
  stories are not dropped before verification.
- **FR-005**: The system MUST discard crime news, tragedies, clickbait, rumours, sponsored content
  and stories based only on social media posts, and record each discarded story with its reason.
  *(A1)* It MUST also discard stories centred on the illness, injury, physical harm or violence
  suffered by real people, famous people included (for example fan clashes with injured people, a
  celebrity with pneumonia, an injured athlete). A career choice such as a retirement is not a
  sensitive story even when health is one of its reasons.
- **FR-006**: The system MUST exclude stories already covered in a published or in-production
  episode, except for clearly marked follow-ups.
- **FR-007**: For each candidate the system MUST record: title, neutral Italian summary (2–3
  sentences, written in its own words, never copied from the source), category, all confirming
  sources with outlet name, publishing group and URL, publication time, importance rating (1–5)
  with a one-line reason (how widely and prominently it is covered, how much it matters to an
  Italian audience), comic potential rating (1–5) with a one-line reason, and sensitivity flags (politics, health, legal, finance).
  *(A1)* It MUST also record a clarity rating (1–5) with a one-line reason: 5 means anyone
  understands the story in a few seconds without background; 1 means it needs names, acronyms,
  procedures or earlier events to make sense.
- **FR-008** *(amended by A1)*: The system MUST produce 3–5 candidates per daily run, ordered by
  comic potential plus clarity (equal weight), then by comic potential, then by importance. All
  three ratings are shown for each candidate. Categories stay balanced: at most two candidates from
  the same category when other categories have eligible stories.
- **FR-019** *(A1)*: The system MUST support a new category "curiosità e stranezze" (oddities:
  bizarre facts, absurd records, animals, gaffes, everyday habits everyone recognises), with its own
  approved sources added to `docs/news-sources.md` and the source configuration. It counts as a
  light category for FR-004.
- **FR-020** *(A1)*: A story MUST NOT become a candidate when its comic potential is below 3, its
  clarity is below 3 or its importance is below 2. Discarded stories are recorded in the run log
  with the reason ("comicità sotto 3", "poco comprensibile", "poco rilevante").
- **FR-021** *(A1)*: A shortlist MUST contain at most one story flagged politics.
- **FR-022** *(A1)*: The rating step MUST consider every verified story of the run, not only the
  most covered ones. A cap is allowed only to protect the budget and MUST be recorded in the run log
  with the number of stories left out.
- **FR-023** *(A1)*: When fewer than 3 stories pass FR-020, the shortlist keeps the ones that pass
  (even only 1 or 2) and shows a warning; it MUST NOT fill the list with stories below the floors.
  With none, it behaves as a run with no verified story.
- **FR-009**: On Thursdays the system MUST build the shortlist only from positive stories
  ("Giovedì buone notizie") published in the last 7 days. One approved, non-satire starting
  source is enough for such a story; the two-groups rule of FR-004 does not apply on Thursdays.
  Positive outcomes of mourning, deaths, violence or crimes against people are excluded, and
  Thursday candidates are ordered by importance plus comic potential (equal weight).
- **FR-010**: Marco MUST be able to pick exactly one candidate per day and change the pick until a
  script exists for it; he MUST be able to reject the shortlist and request a new one that excludes
  rejected stories.
- **FR-011**: The system MUST store shortlists and story records as Markdown files with YAML front
  matter under `tracking/news/`, readable and editable by hand.
- **FR-012**: Each run MUST be idempotent: re-running for the same date MUST reuse what exists and
  MUST NOT repeat paid steps unless a refresh is explicitly requested.
- **FR-013**: The system MUST record the cost of each run in the tracking files, add it to the
  monthly total, and refuse to start a paid step once the 50 USD monthly cap would be exceeded.
- **FR-014**: The system MUST keep a run log for each run: feeds read, feeds failed, stories found,
  stories discarded with reasons, cost.
- **FR-017**: The system MUST deliver each shortlist (daily and weekly) to Marco as a commentable
  document, with a link to it in the shortlist file; the Markdown file in `tracking/news/` stays the
  source of truth, and Marco's pick made in the document is written back to it.
- **FR-018**: The daily run MUST be able to start automatically every day at 07:00 Europe/Rome
  without Marco's computer, save its results to the shared repository, and deliver the shortlist
  document so Marco can pick from his phone. The weekly run starts the same way on Saturday.
- **FR-015**: The system MUST provide a weekly run, every Saturday, that proposes 3–5 stories from the week's
  verified candidates, marking which were already used in a daily reel.
- **FR-016**: The system MUST NOT store full article text, images or video from sources; only
  headlines, links, timestamps and its own summaries.

### Key Entities

- **Source**: an approved outlet. Name, category, publishing group, feed address (or "manual
  only"), role (starting source, confirmation only, inspiration only).
- **Story**: one news event confirmed by several sources. Title, summary, category, confirming
  sources, first seen time, sensitivity flags, importance, comic potential, clarity (A1), status (candidate, chosen,
  rejected, used, follow-up), episode that used it.
- **Shortlist**: the list of candidates for one date and output type (daily or weekly), with the
  Thursday flag, Marco's pick, the link to its commentable document and the link to the run log.
- **Run log**: what happened in one run: feeds read and failed, discarded stories with reasons,
  cost.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a normal weekday, a full daily run gives Marco a shortlist in under 5 minutes,
  with a single command.
- **SC-002**: 100% of candidates have at least two confirming sources from different publishing
  groups, with working links (Thursdays and light categories: at least one approved starting
  source, see FR-004 and FR-009).
- **SC-003**: Over the first 4 weeks, 0 candidates fall in an excluded topic, as checked by Marco.
- **SC-004**: On at least 4 days out of 5, Marco finds at least one candidate good enough to pick
  without asking for a new shortlist.
- **SC-005**: The average cost of a daily run stays under 0.10 USD (about 3 USD per month, well
  within the 50 USD cap).
- **SC-007**: On at least 6 days out of 7, the shortlist document is ready by 07:30 without anyone
  starting it.
- **SC-008** *(A1)*: Over the first 2 weeks after A1, at least 4 days out of 5 have at least one
  candidate Marco rates "easy to use" for a reel, and no candidate is about illness, injury or
  violence of real people.
- **SC-006**: Re-running the command for a date that already has a shortlist costs nothing and
  changes nothing.

## Assumptions

- The daily run starts automatically at 07:00 Italian time (Marco, 2026-11-26) and looks at the
  previous 24 hours; Marco can also start it by asking in the project chat.
- Choosing which items describe the same story, the topic filter, the summary and the comic
  potential rating may use a low-cost language model; that cost counts towards the budget.
- Feed addresses for the approved sources are found and checked during planning; sources without a
  feed are "manual only" and do not block the feature.
- The weekly run is done on Saturday, so the weekly episode can be published on Sunday (Marco,
  2026-11-26).
- The commentable document is created from the project chat with Claude, the same way scripts will
  be reviewed; the plan decides the exact mechanism.
- *(A1)* The weekly run (FR-015) uses the same floors, exclusions and ordering as the daily run,
  so the weekly episode also gets stories that are funny and easy to follow.
- *(A1)* Thursday ("Giovedì buone notizie") keeps its own rules in FR-009, plus the clarity floor
  of FR-020 and the exclusions of FR-005. Its order becomes comic potential plus clarity, as in
  FR-008.
- *(A1)* The oddities sources (about 10, Italian first) are proposed during planning and approved
  by Marco before they enter the configuration, like the other categories.
- *(A1)* The extra rating work stays within SC-005: the 2026-11-27 trial cost about 0.005 USD.
- Summaries are in Italian (channel content); file names, field names and logs are in English.
