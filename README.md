# Medical AI Videos

Turns medical board MCQs into single-narrator English teaching videos —
one male voice, no on-screen characters, mechanism-first explanations in
plain language, and custom clinical diagrams. Free to run: rendering
happens on GitHub Actions instead of a paid API.

## How a video gets made

1. **Write the script** — a `questions/<id>.script.json` file with the
   question, its options, the correct answer, and a scene-by-scene
   narration written in plain teaching English (mechanism → why each
   wrong choice is wrong → why the correct one is right → a clinical
   pearl → take-home).
2. **Build the scenes** — `node engine/build.mjs questions/<id>.script.json engine/out`
   turns that script into one HTML file per scene, using the diagrams in
   `engine/visuals.mjs` (dark clinical style: navy canvas, cyan accents,
   amber for warnings/traps).
3. **Render each scene to an image** — screenshot every
   `engine/out/<id>.sceneN-*.html` at 1920×1080 and save it as the
   matching `.png` next to it. (Ask Claude to do this and commit the
   results, or run it yourself with Playwright.)
4. **Push** — pushing changes under `questions/` or `engine/` triggers
   the render workflow automatically (or run it manually from the
   Actions tab: **Render Narrated Videos → Run workflow**).
5. **Get the video** — the workflow downloads a real neural voice model
   (Piper's `en_US-ryan-high`, a deep male voice — see
   https://github.com/rhasspy/piper/blob/master/VOICES.md for other
   options), narrates every scene, stitches each scene's image + audio
   into a clip, concatenates all clips, and uploads the finished MP4 as
   the `narrated-videos` artifact. Takes a few minutes, costs nothing on
   GitHub's free Actions minutes (unlimited for public repos).

## Why it's split this way

The image rendering (`engine/out/*.png`) is done ahead of time and
committed, rather than running a browser inside the Actions job — that
keeps the workflow itself simple and fast: all it has to do is add real
narration and stitch video, which is the one part that genuinely needs
GitHub's unrestricted internet access (the voice model lives on Hugging
Face).

## Arabic track (current direction)

A second, parallel track matches the visual style of a reference video the
user provided: warm amber background, pink/cyan "sticker" cards with black
borders and offset color shadows, bold Anton headlines, Cairo for Arabic
body text, a gold banner + trophy for the correct answer, and a black pill
caption bar. Narration is Arabic with medical terminology spoken in
English mid-sentence, per the project's language rule.

- `questions/<id>.ar.script.json` — same idea as the English scripts, plus
  `question_ar`, `card_text` (on-screen Arabic explanation per card scene),
  and `verdicts` (per-choice right/wrong + why, shown as a list with ✓/✕
  badges).
- `engine/style-ar.mjs` / `engine/visuals-ar.mjs` — the Arabic design
  system and illustrations (gradient-shaded custom SVGs; real
  photographic/3D organ renders aren't reachable from this sandbox, so
  these are original artwork built to fit the same visual language).
- `engine/build_ar.mjs questions/<id>.ar.script.json engine/out-ar` builds
  the scene HTML; screenshot the same way as the English track.
- `engine/generate_video_ar.py` auto-detects Arabic vs. English runs
  within each narration line and synthesizes each with the matching Piper
  voice (`ar_JO-kareem-medium` for Arabic, `en_US-ryan-high` for the
  English medical terms), with a slower length-scale and small pauses
  between runs/scenes per user feedback on pacing.
- `.github/workflows/render-ar.yml` — same pattern as the English
  workflow, downloads both voices and renders every `*.ar.script.json`.

## Status

- English track: `surgery-1-0001` (obstructive jaundice / Factor VIII)
  and `surgery-6mo2013-01` (real Q1, GI recovery order) — both rendered
  successfully via GitHub Actions.
- Arabic track: same two questions rebuilt in the new visual system —
  script, diagrams, and scene images done, rendering via `render-ar.yml`.
- Everything else in the 1031-question bank is not started yet.

## Honesty notes

- The voice is real neural TTS, clearly better than robotic offline
  voices, but not indistinguishable from a professional human narrator.
- Diagrams are original hand-built SVGs, not stock photos or fetched
  images — image/photo CDNs aren't reachable from the sandbox this runs
  in, so anatomy is illustrated rather than photographed.
