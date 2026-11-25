# Visual test session: Fotor and CapCut

Goal: try every prompt in `bible/prompts/` once, pick what works, and save the approved images as
the show's reference assets. Phase 1, manual. Estimated time: 3–4 hours, can be split in sessions.

Before starting: `git pull`, open `bible/prompts/`, create
`/home/marco/Projects/podcat-assets/reference/` and `/home/marco/Projects/podcat-assets/tests/`.

## Rules for every attempt

- Use the prompt exactly as written (fill the `<...>` placeholders, append the style block).
- Generate 2–4 variants; keep at most the best one.
- Save files as `tests/<step>-<name>-v<n>.png` (or `.mp4`).
- Write one line per attempt in `tracking/assets/test-log.md`: date, step, tool, model, prompt
  file, result (ok / so-so / no), note. If you prefer, just paste notes in chat and Claude writes
  the log.

## Steps

### 1. Style check (Fotor, ~20 min)
- [ ] 1.1 Generate Flanella's single portrait (`characters.md`, portrait template) with 2–3
      different Fotor models; note which model gives the best soft 3D cartoon look.
- [ ] 1.2 Pick the model and use it for everything else (record it in the log).

Done when: one model chosen.

### 2. Character model sheets (Fotor, ~45 min)
- [ ] 2.1 Fuzz model sheet
- [ ] 2.2 Flanella model sheet
- [ ] 2.3 Vinile model sheet
- [ ] 2.4 Feedback model sheet

Done when: four sheets approved, each cat recognisable and different from the others, clothes as
in the bible. Move them to `reference/characters/`.

### 3. Expressions (Fotor with smart reference, ~45 min)
- [ ] 3.1 For each cat: talking, laughing, rolling eyes, listening (16 images)
- [ ] 3.2 Extras: Fuzz outraged, Feedback dozing, Flanella sipping, all cats moved

Done when: the cat is clearly the same as in its model sheet in every image.

### 4. The tavern (Fotor, ~30 min)
- [ ] 4.1 Empty wide shot
- [ ] 4.2 Wide shot with the four cats (references from step 2), seating Fuzz, Flanella, Vinile,
      Feedback
- [ ] 4.3 CRT TV close-up

Done when: one approved wide shot with all four cats; this becomes the show's key image.

### 5. Recurring and news images (Fotor, ~30 min)
- [ ] 5.1 Gnocchi sting, base prompt plus one variant
- [ ] 5.2 News mode A, B, C with the three test subjects in `news-image-modes.md`

### 6. Clips (CapCut AI video, ~45 min)
- [ ] 6.1 Wide establishing clip from the approved wide shot
- [ ] 6.2 For one cat only (Flanella): talking, listening, laughing, eye roll
- [ ] 6.3 If 6.2 is good, repeat for the other three cats
- [ ] 6.4 Note credits used per clip (to estimate the monthly cost)

Done when: the cat keeps the same look during the whole clip, no deformed paws or extra tails.

### 7. Voices and captions (CapCut, ~20 min)
- [ ] 7.1 Try CapCut Italian voices on this test line for each cat and pick one per cat:
      "Allora, gattini, oggi la notizia è di quelle che fanno discutere."
      Guide: Flanella warm, low and dry; Fuzz fast, cracking when angry; Vinile raspy and
      theatrical; Feedback deep and slow.
- [ ] 7.2 Write the chosen voice names in each sheet in `bible/characters/` (field `capcut_voice`).
- [ ] 7.3 Auto captions on a 15 s test: check Italian accuracy and that the cat names are right.

### 8. Mini pilot (CapCut, ~30 min)
- [ ] 8.1 Edit a 20–30 s 9:16 test with: wide clip, two talking clips, one news image (mode A),
      captions. No need for a real story.

Done when: you would not be embarrassed to publish it.

## After the session

Tell Claude the results (or point to the log). Claude will: mark prompts `tested` / `approved`,
create the asset records in `tracking/assets/`, update the bible, and adjust the prompts that
failed.
