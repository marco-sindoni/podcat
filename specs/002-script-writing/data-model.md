# Data Model: Script writing for the four cats

Markdown files with YAML front matter (constitution VI). Field names in English; script content,
notes and answers in Italian. Times in Europe/Rome.

## Script index (`tracking/scripts/<script-id>.md`)

`script-id` = `<date>-<kind>-<story slug>`, e.g. `2026-11-27-daily-hacker-fanno-impazzire-i-frigoriferi`.

| Field | Type | Rules |
| --- | --- | --- |
| `id` | string | as above |
| `story_id` | story id | story with `status: chosen` when written |
| `kind` | enum | `daily`, `weekly` |
| `date` | date | date of the shortlist the story was picked from |
| `good_news_thursday` | bool | copied from the shortlist |
| `tone` | enum | `comico`, `pungente`; from the story, changeable by revision |
| `status` | enum | `draft`, `review`, `approved`, `discarded` |
| `problems` | list of string | check failures when `draft` after a failed fix (R3) |
| `news_image_mode` | enum | `A`, `B`, `C` |
| `previous_script` | script id or null | used for the rotation |
| `current_version` | int | ≥1 |
| `versions` | list | each: `version`, `created_at`, `cause` (`write`, `new-draft`, `revise`, `ending`, `edit-line`), `words`, `duration_s`, `cost_usd`, `path` |
| `doc_url` | URL or null | commentable document |
| `approved_at` | datetime or null | |
| `approved_version` | int or null | |
| `cost_usd` | number | sum of the versions |

Body: generated summary in Italian (story, status, link to current version) between the generated
markers; Marco's notes below are kept.

Status transitions:

```text
(write) ─▶ draft ─link-doc─▶ review ──approve──▶ approved ──reopen──▶ review
             │                 │  ▲
             │                 └──┘ revise / ending / edit-line / new-draft (new version)
             └── checks failed: stays draft with problems
draft or review ──news pick of another story / discard──▶ discarded
```

Story effects: `write` sets `story.script = <script-id>`; `approve` sets `story.status = used` and
`story.episode = <script-id>`; `discard` clears `story.script` and sets the story back to
`candidate`.

## Script version (`tracking/scripts/<script-id>/v<N>.md`)

| Field | Type | Rules |
| --- | --- | --- |
| `version` | int | |
| `lines` | list | each: `n` (1-based), `cat` (`flanella`, `fuzz`, `vinile`, `feedback`), `text`, `manual` (bool, edited by Marco) |
| `scenes` | list | each: `n`, `shot` (id from `bible/shots.md`), `lines` (line numbers), `reactions` (list of `cat` + `direction`), `duration_s` (computed) |
| `news_image` | object | `mode`, `scene`, `comment_line` (line number), `held_by` (cat, mode C only), `subject` (one Italian sentence for spec 003's Fotor prompt) |
| `endings` | list of 2 | alternative endings: each `feedback` and `flanella` text |
| `words` | int | spoken words, sting excluded (computed) |
| `duration_s` | number | computed (R4) |
| `head_writer_notes` | list of string | Italian, what changed and why, who stays silent and why |
| `answers` | list | each: `comment` (quote), `answer` (Italian, one sentence), `changed_lines` |
| `coherence_changes` | list of line numbers | lines changed without a comment, to keep a joke coherent |

Body: the Italian rendering (see `contracts/tracking-files.md`), regenerated from the front matter.

## Configuration (`config/scripts.yaml`)

`words` (daily 70–90, weekly 280–320), `target_s` (30, 120), `tolerance_s` (5, 15),
`words_per_second` per cat, `pause_s` (0.3), fixed shot durations (`news-cutin` 2.5, `sting-gnocchi`
3), `thursday_formula`, `repeat_window` (7), `tics` (list per cat for R8).

`config/pricing.yaml` gains `script_models: {room: claude-haiku-5-5, head_writer: claude-sonnet-5-5,
revision: claude-sonnet-5-5}`.

## Cost ledger

Reused from spec 001; entries use `feature: script` and `step`: `room`, `head-writer`, `fix`,
`revision`.

## Model outputs (Pydantic)

- **RoomResult**: `drafts` (2): each `angle` (one sentence), `lines`, `scenes`, `news_image`.
- **HeadWriterResult**: `chosen_angle`, `lines`, `scenes` (no durations), `news_image`, `endings`
  (2), `notes`.
- **RevisionResult**: `changes` (line `n` + new `text`, or a new line inserted after `n`),
  `coherence_changes`, `answers`, `tone` (optional new tone), `notes`.
- **FixResult**: same shape as HeadWriterResult.
