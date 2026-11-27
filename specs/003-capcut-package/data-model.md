# Data model: CapCut package

All files are Markdown with YAML front matter under `tracking/` (constitution VI). Field names in
English, values shown to Marco in Italian.

## Package (index) – `tracking/packages/<script-id>.md`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | str | equals the script id |
| `script_id`, `story_id` | str | inputs |
| `kind` | `daily` \| `weekly` | from the script |
| `date` | date | script date |
| `script_version` | int | approved version the package was built from |
| `status` | `ready` \| `outdated` | `outdated` after the script is reopened |
| `current_version` | int | |
| `versions` | list | `version`, `created_at`, `cause` (`build`, `revise`, `fix`), `cost_usd`, `path` |
| `problems` | list[str] | failed checks after the fix (empty when delivered) |
| `reuse_share` | float | reused clip seconds / counted seconds, 0–0.30 |
| `new_clips` | int | number of new clips to make |
| `doc_url` | str \| null | Claude Doc link |
| `cost_usd` | float | sum of versions |

Transitions: (none) → `ready` on build; `ready` → `outdated` on script reopen; a build on a newly
approved script version adds a version and sets `ready` again.

## Package version – `tracking/packages/<script-id>/v<N>.md`

| Field | Type | Notes |
| --- | --- | --- |
| `version` | int | |
| `header` | object | title, date, kind, tone, thursday, duration_s, mode |
| `assets` | list[AssetNeed] | |
| `news_image` | NewsImagePlan | |
| `blocks` | list[SceneBlock] | one per script scene, in order |
| `clips` | list[ClipUnit] | |
| `voices` | list[VoiceLine] | every line in order |
| `subtitles` | SubtitlePlan | style, colors, chunks, words to check |
| `sound` | SoundPlan | |
| `publishing` | PublishingKit | |
| `people` | list[str] | real people named in the story (for the prompt check) |
| `answers` | list | answers to comments, as in spec 002 |

**SceneBlock**: `scene`, `start_s`, `duration_s`, `shot`, `shot_label`, `on_screen` (list of
CatOnScreen), `cutaways` (list of `react-X` with direction), `clip_unit`, `lines` (line numbers),
`captions` (line, text, color), `off_screen_voice` (bool, modes B and sting).

**CatOnScreen**: `cat`, `state` (`parla` \| `ascolta` \| script direction), `expression` (key from
the bible list).

**ClipUnit**: `n`, `scenes`, `duration_s`, `shot`, `cat`, `expression`, `source` (`reused` \|
`new` \| `still` \| `branding`), `asset_id` (reused), `prompt` and `start_image` (new),
`file_name`, `key_moment` (bool).

**AssetNeed**: `kind` (`reference`, `clip`, `news-image`, `sting`, `theme`, `ambience`), `label`,
`status` (`ready` with `file`, `to-create` with `tool`, `prompt`, `reference`).

**NewsImagePlan**: `mode`, `scene`, `start_s`, `comment_line`, `held_by`, `expression`,
`prompt`, `alt_prompt`, `negative`, `placement` (Italian CapCut steps for the mode),
`reference_image` (mode C), `file_name`.

**VoiceLine**: `n`, `cat`, `voice` (CapCut voice or null), `voice_profile`, `text`,
`voice_text` (null when equal to text).

**SubtitlePlan**: `style` (from `bible/subtitles.md`), `colors` (cat → hex), `chunks` (line,
cat, text, color; at most 2 lines × `max_chars`), `check_words` (word, why: `cat-name`, `person`,
`place`, `foreign`, `voice-differs`, line).

**SoundPlan**: `theme` (name or "da scegliere"), `ambience`, `effects` (list of `effect`, `scene`,
`moment`).

**PublishingKit**: `platform` (`youtube-shorts` \| `youtube`), `titles` (3), `description`,
`sources` (outlet, url), `hashtags`, `ai_disclosure`.

## Asset record – `tracking/assets/<asset-id>.md` (minimal; spec 004 extends it)

| Field | Type | Notes |
| --- | --- | --- |
| `id` | str | e.g. `clip-fuzz-outraged-1` |
| `kind` | `reference` \| `clip` \| `sting` \| `theme` \| `ambience` | |
| `cat` | cat id \| null | |
| `expression` | key \| null | bible expression list |
| `shot` | shot id \| null | |
| `file` | str | path relative to `PODCAT_ASSETS_DIR` |
| `status` | `draft` \| `approved` | only `approved` is used |

Last use of a clip = the newest package version whose `clips` names its `asset_id`.

## Inputs (read only)

- Script index and approved version (spec 002 data model).
- Story record (spec 001): title, summary, sources, tone, flags.
- Bible: character sheets (`capcut_voice`, `voice_profile`, `subtitle_color`, look), `shots.md`,
  `prompts/` (style block, negative hints, mode templates, clip template), `sound.md`, `subtitles.md`.
