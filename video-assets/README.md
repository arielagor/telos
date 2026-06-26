# Telos walkthrough video — production pipeline

The ~8.5-minute walkthrough was produced by the same goal-autonomous pipeline that built Telos:
an AI-written script, a HeyGen **Avatar V** synthetic presenter (AI voice, no human voiceover),
AGOR-look cutaways, and an ffmpeg composite. The final MP4 is hosted as a **GitHub Release asset**
(too large for the repo) and on YouTube; this folder holds the reproducible pipeline.

- `script.md` — the beat-structured script (spoken narration + visual plan).
- `beats.json` — per-beat narration fed to HeyGen.
- `render_heygen.py` — renders each beat with HeyGen Avatar V v3 (`HEYGEN_API_KEY`), resumable.
- `make_slides.py` — generates the 16 AGOR-look cutaway slides (PIL).
- `build_telos_video.py` — composites: per-beat avatar (blur-filled, no pillarbars) + cutaway with
  avatar PiP + burned captions, then concat, disclosure lower-third, progress bar, title/outro.
- `youtube-meta.md` — the upload title/description/visibility.
- `cutaways/` — the rendered slides.

Transparency: the presenter is a synthetic avatar with an AI voice; the script was generated from
the submitted repo; no human voiceover was recorded. A persistent on-screen lower-third says so.

Reproduce: `python render_heygen.py && python make_slides.py && python build_telos_video.py`.
