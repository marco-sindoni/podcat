# Prompt library

Prompts for the reference images (Fotor) and clips (CapCut AI video) of Podcat. Prompts are in
English because image and video models follow English best. Every prompt shares the **style block**
below so all assets look like the same show.

Status per prompt: `draft` (never tried) → `tested` (tried, see results) → `approved` (output saved
as a reference asset in `$PODCAT_ASSETS_DIR/reference/` and recorded in `tracking/assets/`).

## Style block (append to every prompt)

```
soft 3D cartoon style like a modern animated feature film, rounded shapes, expressive faces,
warm golden tavern lighting, cozy atmosphere, vertical 9:16 composition, no text, no logos
```

## Negative hints (use where the tool has a negative prompt field)

```
photorealistic, real people, human faces, text, watermark, logo, brand names, extra limbs,
extra tails, distorted paws, horror, dark mood
```

| File | What it covers |
| --- | --- |
| [characters.md](characters.md) | Model sheets and expressions for the four cats |
| [set.md](set.md) | The tavern: wide shot, each armchair, the CRT TV |
| [recurring.md](recurring.md) | Recurring assets: Giovedì buone notizie gnocchi sting |
| [news-image-modes.md](news-image-modes.md) | Templates for the per-episode news image, one per staging mode |
| [clips.md](clips.md) | CapCut image-to-video prompts for the reusable clip library |
