# Research: Script writing for the four cats

## R1. Models and cost

- **Decision**: writers' room on `claude-haiku-5-5`; head writer, fix and revisions on
  `claude-sonnet-5-5`. Both configurable in `config/pricing.yaml` (`script_models`).
- **Rationale**: the head writer decides what reaches Marco, so it gets the stronger model; drafts
  are raw material and cost almost nothing on Haiku. Estimates with current prices (Haiku 0.10/0.50,
  Sonnet 2/10 USD per million tokens):

  | Step | Input tokens | Output tokens | USD |
  | --- | --- | --- | --- |
  | Writers' room, 2 drafts (Haiku) | ~6,000 | ~2,000 | 0.002 |
  | Head writer + 2 endings + notes (Sonnet) | ~9,000 | ~2,500 | 0.043 |
  | Reel total | | | ~0.045 |
  | Revision round (Sonnet) | ~7,000 | ~1,200 | ~0.026 |
  | Weekly script total | ~2× reel | ~2.5× reel | ~0.11 |

  Month: 30 reels (1.35) + 4 weekly (0.44) + ~40 revisions (1.05) ≈ 2.9 USD, under SC-005.
- **Alternatives**: Sonnet for both passes (~0.07 per reel, above SC-005); Opus 5.5 as head
  writer (~0.08 per reel, about 4.5 USD/month, best comedy quality); Haiku for everything (~0.005,
  weakest jokes). Marco chose Sonnet on 2026-11-27 and asked that the model stay a parameter that is
  easy to change: one line per step in `config/pricing.yaml`, read on every run.

## R2. Writers' room: two angles, then the head writer

- **Decision**: call 1 asks for two complete drafts with different comic angles (e.g. "take the fact
  literally" vs "Fuzz's conspiracy"), each already respecting the structure. Call 2 receives both,
  picks or merges, rewrites and explains the choice in its notes.
- **Rationale**: in a writers' room the head writer chooses between pitches; two cheap Haiku drafts
  cost less than one Sonnet draft and give the head writer more material.
- **Alternatives**: one draft (less choice); three drafts (more input tokens for the head writer).

## R3. Checks in code, one automatic fix

- **Decision**: `checks.py` verifies, without a model: lines only from the four cats; Flanella first
  and last; Feedback second-to-last; Fuzz and Vinile present when they have lines; word count
  (110–135 reel, 280–320 weekly, at least two lines per cat weekly); every silent cat has at least one
  reaction in the scenes (FR-018); exactly one news image with a valid mode different from the
  previous script; Thursday opens with the slot formula and the sting scene; durations within
  tolerance; endings respect the same structure. On failure, one "fix" call to the head writer model
  with the list of problems; if it still fails, the script is saved as `draft` with the problems and
  the command exits with code 4, so Claude tells Marco instead of delivering a broken script.
- **Rationale**: SC-002 asks for 100% compliance; counting words and checking order is exact in code
  and free; models miscount words.
- **Alternatives**: trust the head writer (miscounts); unlimited retries (unbounded cost).

## R4. Timing

- **Decision**: duration of a line = words / speaking rate of the cat + 0.3 s pause; rates in
  `config/scripts.yaml` (start: Flanella 3.0, Fuzz 3.4, Vinile 2.9, Feedback 2.5 words/s, so that
  110–135 words fit about 45 s as the constitution says). Scene
  duration = sum of its lines, or the fixed duration of a silent shot (B cut-in 2.5 s, Thursday sting
  3 s). Durations are computed by code, never by the model. Tolerance: ±5 s reel (target 45 s, sting
  excluded), ±15 s weekly (target 110 s: 280–320 words at about 3 words/s is 95–125 s, still "about
  2 minutes"; the constitution's 120 s and 280–320 words do not fit the same speaking rate).
- **Rationale**: deterministic and calibratable after B-012 recordings by editing the config.

## R5. Storage: index plus one file per version

- **Decision**: `tracking/scripts/<script-id>.md` holds status, story, mode, tone, current version,
  document link, approval and the list of versions; `tracking/scripts/<script-id>/v<N>.md` holds one
  version: structured lines, scenes, news image, endings, notes, answers in the front matter, and the
  Italian rendering in the body. Versions are never rewritten after a newer one exists.
- **Rationale**: previous versions stay readable (FR-011); each file stays small; YAML keeps the
  structure exact for revisions; the body is what Claude pastes into the doc.
- **Manual edits (FR-013)**: Marco may edit a line's `text` in the latest version file, or edit a
  line inline in the Claude Doc; in the second case Claude runs `podcat script edit-line N "..."`
  (free). Revisions start from the latest file content, so manual edits are kept, and the revision
  prompt marks them as "do not touch".

## R6. Document and comments

- **Decision**: same mechanism as spec 001. `podcat script show` prints the Italian document text;
  Claude publishes it as a Claude Doc (title `Podcat – Copione <giorno> <data>`, weekly `Podcat –
  Copione della domenica <data>`) and stores the link with `podcat script link-doc`. Each new version
  replaces the doc content and keeps the link. Comments are read by Claude from the doc and passed
  to `podcat script revise --comments <file>` as YAML (`line` number when the comment is anchored on
  a numbered line, `quote`, `text`). Keywords recognised by Claude, not by the CLI: "approvato" →
  `approve`; "finale N" → `ending N`; "rifalla da capo" / "cambia angolo" → `write --new-draft`;
  "più leggera" / "più pungente" → `revise` with a tone change.
- **Rationale**: no new infrastructure; the CLI stays testable offline; Claude already reads doc
  comments in the news routine.

## R7. News image mode rotation

- **Decision**: the previous video is the most recent non-discarded script (daily or weekly) with an
  earlier `date`, or the same date but created earlier; the new mode is chosen by the head writer
  among the two allowed modes (whichever fits the story better), and checked by code. Mode C names
  the cat holding the newspaper or photo, who must speak in that scene. When spec 004 adds episode
  records with the published mode, `rotation.py` switches to them.
- **Rationale**: there are no published-episode records yet; scripts are the best proxy.

## R8. Anti-repetition

- **Decision**: the head writer receives the first line, the last two lines and the catchphrases of
  the last 7 non-discarded scripts, and must avoid repeating them; `checks.py` flags an exact repeat
  of a first or last line and a verbal tic ("Ai miei tempi", "Questo è uno scandalo", "Allora,
  gattini", "Ricapitoliamo", "No, no, no, fermi tutti") used in each of the previous 2 scripts.
- **Rationale**: cheap (a few hundred tokens) and matches the inauthentic-content concern.

## R9. Tone and Thursday registers

- **Decision**: the prompts carry three register blocks: `comico` (joke-driven, absurd escalation,
  surprise punchline), `pungente` (satire on facts and the powerful, Fuzz outraged at the absurdity
  of the facts, Feedback's reflection with an ironic twist, Flanella's pointed close), Thursday
  (warm, jokes on themselves and the situation, never on the people in the story). The slot formula
  is fixed in `config/scripts.yaml`: "Giovedì buone notizie! Buoni gli gnocchi, buone le notizie."
  (approved by Marco on 2026-11-27, editable in the config).
- **Sensitivity flags**: `politics` adds "satira sui fatti e sui potenti, mai di parte"; `health`,
  `legal`, `finance` add "nessun consiglio". Real people: only public figures of the story, never
  realistic descriptions beyond their public role.

## R10. Silent cats and reactions

- **Decision**: each scene lists `reactions` (cat + short Italian direction of the face or gesture,
  e.g. "Fuzz trattiene a stento la rabbia"). A cat without lines must have at least one reaction in
  a shot where it is visible (wide shot, two-shot or reaction close-up). The writers' room decides
  who speaks; the default is all four, and the head writer explains in the notes when a cat stays
  silent.

## R11. Shot list

- **Decision**: new `bible/shots.md` with ids used in scenes: `wide` (four armchairs), `close-<cat>`,
  `two-fuzz-flanella`, `two-vinile-feedback`, `two-flanella-vinile`, `react-<cat>` (silent close-up),
  `news-tv` (mode A, wide with the CRT TV), `news-cutin` (mode B, full screen, off-screen line),
  `news-held-<cat>` (mode C), `sting-gnocchi` (Thursday). Adjacent seats only for two-shots,
  matching the armchair order Fuzz, Flanella, Vinile, Feedback.
- **Rationale**: a fixed, small list keeps scenes consistent with the reusable clip library (B-005).

## R12. Weekly script

- **Decision**: same pipeline with `kind: weekly`: 280–320 words, all four cats with at least two
  lines, cold open, two escalations allowed, one Vinile detour. If the story was used in a reel, the
  head writer receives that reel's lines and must take a new angle.

## R13. Thinking per step (found in the first real run, 2026-11-28)

- **Decision**: `script_effort` in `config/pricing.yaml`: writers' room `off` (Haiku `disabled`),
  head writer and revision `low` (adaptive thinking at low effort). `off` on Sonnet 5.5 maps to
  `between_tools`, since `disabled` is rejected there. `max_tokens` raised to 16,000 (daily).
- **Rationale**: with the model default, Haiku 5.5 used all 6,000 output tokens thinking and returned
  truncated JSON. Thinking tokens are billed as output.
