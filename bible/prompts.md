# Prompt library (phase 1: Fotor images, CapCut clips)

Status: **draft, not yet tested.** Every prompt is tested in the session described in
[`docs/tasks/T-001-prompt-test.md`](../docs/tasks/T-001-prompt-test.md); the version that works is
written back here with a version number, and the approved image becomes the reference asset.

Prompts are in English (image and video models follow English best). Any on-screen text in Italian
is added as a text layer in CapCut, not generated in the image: models misspell lettering.

## Shared style block

Append to every Fotor prompt:

> soft 3D cartoon, animated feature film look, rounded shapes, expressive eyes, warm amber
> lighting, cozy, high detail, no text, no logos, no watermark

Negative prompt (where Fotor accepts one):

> realistic photo, human, text, letters, logo, watermark, brand, extra limbs, extra tails,
> deformed paws, dark horror mood

## 1. Character model sheets (Fotor, 16:9)

One sheet per cat: front, three-quarter and side view on a plain background, then 4–6 expressions.
Source: the "Look" section of each sheet in [`characters/`](characters/README.md).

| ID | Cat | Prompt |
| --- | --- | --- |
| P-CH-01 | Flanella | Character turnaround sheet of one anthropomorphic female cat: red tabby fur, green eyes, oversized red-and-black plaid flannel shirt, studded collar, confident calm expression; front view, three-quarter view, side view, full body, standing, plain light grey background, consistent design across views |
| P-CH-02 | Fuzz | Character turnaround sheet of one anthropomorphic male cat: black fur, messy spiky electrified fur, yellow eyes, ripped jeans, faded black t-shirt with no print, restless energetic pose; front view, three-quarter view, side view, full body, standing, plain light grey background, consistent design across views |
| P-CH-03 | Feedback | Character turnaround sheet of one anthropomorphic male cat: big and chubby, grey fur, sleepy half-closed amber eyes, loose knitted beanie, relaxed slouching pose; front view, three-quarter view, side view, full body, standing, plain light grey background, consistent design across views |
| P-CH-04 | Vinile | Character turnaround sheet of one anthropomorphic old male cat: white fur with dark patches, grey whiskers, round glasses, worn cardigan over a plaid shirt, holding a vinyl record, grumpy but kind expression; front view, three-quarter view, side view, full body, standing, plain light grey background, consistent design across views |
| P-CH-05 | each cat | Expression sheet of the same cat as the reference image: six head-and-shoulders portraits in a grid — talking, laughing, outraged, sarcastic smirk, bored, surprised; plain light grey background (use the approved P-CH-0x image as reference) |

## 2. Tavern (Fotor, 9:16)

| ID | Shot | Prompt |
| --- | --- | --- |
| P-TV-01 | Wide shot, empty | Interior of a small cozy tavern at night, four soft brown leather armchairs in a gentle arc facing the viewer, wooden floor, brick walls, stone fireplace with an old CRT television above it, warm lamps, shelves with vinyl records and old guitar amplifiers, grunge 90s vibe, vertical composition |
| P-TV-02 | Wide shot, with cats | Same tavern as the reference image, the four cats from the reference images sitting in the armchairs, left to right: Fuzz, Flanella, Vinile, Feedback, chatting, vertical composition |
| P-TV-03…06 | One per armchair | Medium shot of <cat> sitting in a soft brown leather armchair in the tavern from the reference image, talking to someone off-screen, vertical composition (one per cat, from the approved model sheet) |
| P-TV-07 | CRT TV close-up | Close-up of the old CRT television above the tavern fireplace, screen glowing, empty screen area to be filled later, warm light, vertical composition |

## 3. "Giovedì buone notizie" logo (Fotor, 9:16 and 1:1) — B-011

| ID | Prompt |
| --- | --- |
| P-GN-01 | A steaming plate of potato gnocchi with rich red tomato sauce and a basil leaf, on a rustic wooden table in a cozy tavern, the steam rising and curling into the shape of a small heart, warm golden light, appetizing, top area left empty for a title, vertical composition |
| P-GN-02 | Same plate as the reference image, a cartoon cat paw entering the frame holding a fork, about to take a gnocco, playful, vertical composition |
| P-GN-03 | Square version of P-GN-01 for thumbnails |

Title "Giovedì buone notizie" is added in CapCut: warm retro lettering, cream with a tomato-red
outline.

## 4. News image, three staging modes (Fotor, per episode)

Templates the software fills for each story (`<subject>` = a neutral visual description of the
news, never a real person's face, no logos).

| ID | Mode | Template |
| --- | --- | --- |
| P-NW-A | (a) CRT TV | Illustration of <subject>, simple bold composition readable at small size, as if shown on an old television, 4:3 |
| P-NW-B | (b) Full-screen cut-in | Illustration of <subject>, dynamic composition, centered subject, vertical composition |
| P-NW-C | (c) Newspaper or photo held by a cat | A newspaper front page illustration showing <subject>, no readable text, slightly crumpled, held by a cartoon cat paw, vertical composition |

## 5. CapCut clips (image to video, from approved Fotor images)

Each clip ~5 s, 9:16, silent (voices are added separately). Same prompts for every cat; the start
image is the cat's approved P-TV-03…06 frame.

| ID | Clip | Motion prompt |
| --- | --- | --- |
| P-CL-01 | Talking | The cat talks animatedly, mouth moving, small paw gestures, slight head movements, camera static |
| P-CL-02 | Laughing | The cat bursts out laughing, shoulders shaking, eyes closed, camera static |
| P-CL-03 | Listening | The cat listens, nods slowly, ears twitch, blinks, camera static |
| P-CL-04 | Scoffing | The cat rolls its eyes and scoffs, crossing its arms, camera static |
| P-CL-05 | Tavern wide | Slow gentle push-in on the tavern with the four cats, fire flickering, camera slowly moving forward |
| P-CL-06 | Gnocchi sting | Steam rises from the plate of gnocchi and forms a heart, slow push-in, 2–3 s |
| P-CL-07 | CRT TV | The old television flickers on, slight screen glow, static camera |

## 6. CapCut voices (text to speech)

One fixed CapCut Italian voice per cat, chosen in T-001 and written into each character sheet
(`capcut_voice`). Test line for every candidate voice:

- Flanella: "Allora, gattini… ricapitoliamo."
- Fuzz: "No, no, no, fermi tutti! Questo è uno scandalo!"
- Feedback: "Mmh. E quindi?"
- Vinile: "Ai miei tempi… nel '94 questa cosa non sarebbe mai successa."
