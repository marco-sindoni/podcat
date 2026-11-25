# T-001 — Prompt test session on Fotor and CapCut

- **Owner:** Marco (manual, phase 1)
- **Backlog:** B-012
- **Prompts:** [`bible/prompts.md`](../../bible/prompts.md)
- **Estimated time:** 3–4 hours, can be split over several sessions (one block per step)
- **Cost:** 0 USD extra (Fotor Pro and CapCut already available); note any credits used
- **Done when:** every row in the results table has a verdict, the approved images are saved in the
  assets folder, and the working prompt versions are written back into `bible/prompts.md`.

## Rules for the session

1. Test the prompts **in order**: later steps use earlier approved images as reference.
2. For each prompt make **up to 4 attempts**. Change one thing at a time and note what you changed.
3. Save every kept image or clip in `/home/marco/Projects/podcat-assets/` (paths below), named
   `<ID>_v<attempt>.<ext>`, e.g. `P-CH-01_v3.png`. Don't put them in git.
4. Verdict per prompt: **OK** (approved as reference), **TWEAK** (usable after a prompt change,
   write the change), **KO** (does not work, describe why).
5. Approval checks for every image: soft 3D cartoon style; matches the character sheet; no text,
   logos or real people; consistent with the other approved images.

## Steps

### Step 1 — Characters (Fotor) → `reference/characters/<cat>/`

- [ ] P-CH-01 Flanella model sheet
- [ ] P-CH-02 Fuzz model sheet
- [ ] P-CH-03 Feedback model sheet
- [ ] P-CH-04 Vinile model sheet
- [ ] Check the four side by side: same style, same proportions, clearly different silhouettes
- [ ] P-CH-05 expression sheet × 4 cats (using each approved model sheet as reference image)

### Step 2 — Tavern (Fotor) → `reference/tavern/`

- [ ] P-TV-01 empty tavern
- [ ] P-TV-02 tavern with the four cats (reference: tavern + 4 model sheets)
- [ ] P-TV-03…06 one medium shot per cat in their armchair
- [ ] P-TV-07 CRT TV close-up

### Step 3 — "Giovedì buone notizie" logo (Fotor) → `intro/gnocchi/`

- [ ] P-GN-01 steaming gnocchi, vertical
- [ ] P-GN-02 variant with the cat paw and fork
- [ ] P-GN-03 square thumbnail

### Step 4 — News image modes (Fotor) → `tests/news/`

Use a real story of the day as `<subject>`.

- [ ] P-NW-A CRT TV mode
- [ ] P-NW-B full-screen cut-in mode
- [ ] P-NW-C newspaper held by a cat mode

### Step 5 — Clips (CapCut, image to video) → `library/<cat>/` and `library/tavern/`

- [ ] P-CL-01…04 on one cat first (Flanella); if OK, repeat on the other three
- [ ] P-CL-05 tavern wide push-in
- [ ] P-CL-06 gnocchi sting, then add the title text layer
- [ ] P-CL-07 CRT TV flicker
- [ ] Check: cats stay on-model across the 5 s (no face or fur changes)

### Step 6 — Voices (CapCut text to speech)

- [ ] Listen to the Italian voices with each cat's test line
- [ ] Pick one voice per cat; four clearly different voices
- [ ] Write the voice name into `capcut_voice` in each character sheet (or tell Claude)

### Step 7 — Dry run (CapCut)

- [ ] Build a 30 s test reel: tavern wide → 4 lines (one per cat) → news image (one mode) → close
- [ ] Turn on CapCut auto captions; check they are readable above the Shorts interface
- [ ] Export 9:16 and watch it on a phone

## Results

Fill in as you go (or send the notes to Claude, who updates this table and `bible/prompts.md`).

| Prompt | Attempts | Verdict | Kept file | Prompt changes / notes |
| --- | --- | --- | --- | --- |
| P-CH-01 | | | | |
| P-CH-02 | | | | |
| P-CH-03 | | | | |
| P-CH-04 | | | | |
| P-CH-05 | | | | |
| P-TV-01 | | | | |
| P-TV-02 | | | | |
| P-TV-03…06 | | | | |
| P-TV-07 | | | | |
| P-GN-01 | | | | |
| P-GN-02 | | | | |
| P-GN-03 | | | | |
| P-NW-A | | | | |
| P-NW-B | | | | |
| P-NW-C | | | | |
| P-CL-01…04 | | | | |
| P-CL-05 | | | | |
| P-CL-06 | | | | |
| P-CL-07 | | | | |
| Voices | | | | |
| Dry run | | | | |

## After the session

- Approved images become the reference assets (constitution, IV): record each one in
  `tracking/assets/` (path, SHA-256, prompt, source "Fotor").
- Update `bible/prompts.md` with the working versions and mark it tested.
- Record any rule learned (e.g. a style keyword that is required) in `docs/decisions.md`.
