# Scene packet (shared by every scene builder)

Film: "film-studio launch", a 9:16 launch video for a Claude Code video studio that combines several video skills into one narrated film.
Project: `/media/aiyu/550E85595197DBEC/Personal/Movies/projects/2026-11-20-studio-launch`

## Your job

Build ONE scene and render it to `scenes/<id>/clip.mp4` (inside the project). Work only inside `scenes/<id>/`.
Picture only: no voice, no TTS, no music, no captions. Audio in your clip is thrown away; do not spend time on sound.
The narration line for your scene is given so the picture can match its meaning and rhythm. Do not write the narration words on screen word-for-word: on-screen text carries a different, shorter fragment.

## Format (hard requirements)

- 1440 x 2560 px, 30 fps, H.264 MP4, yuv420p.
- Length: at least the frame count given for your scene. Add 6 extra frames (0.2 s) at the end; the editor trims.
- The scene starts already moving (no fade-in from black) and is still moving at its last frame (hard cut follows).

## Style bible (from style.md; obey exactly)

| Token | Value |
|---|---|
| Ground | Ink `#0B0F1A`, lifted to `#141A2B` in a soft radial light pool; never a flat swatch: radial light + ~3% film grain |
| Text | Paper `#F4EFE6` |
| Accent | Amber `#FFB547` (hero words, highlights) |
| Secondary | Cyan `#5EE6FF` (UI, data, waveforms), sparingly |
| Display font | `Montserrat` (installed system-wide), weights 800-900, letter-spacing -0.03em |
| Mono font | `FiraCode Nerd Font` (installed system-wide) for terminal, code, numbers |
| Type scale | Hero 220-300 px; headline 140 px; body 72 px; UI text at least 104 px |
| Safe zones | Nothing important in the top 200 px. NO on-screen text below y = 1990 (captions go there). Side margins 96 px |

## Quality bar

- Motion: median move ~10 frames; landings ease out (power3.out / expo.out), exits ease in; overshoot rare; things arrive from larger than life or from the frame edge, never scale up from 0; move by transform, not opacity fades.
- Something moves on almost every frame: no run of more than 3 identical frames.
- One hero per frame. No page chrome: no corner labels, no counters like "02/05", no timecodes, no progress bars, no small kicker text above a headline.
- Depth and texture: light pool, grain, subtle shadows. The scene must look designed, premium, not like a slide.
- Text readable on a phone.
- No third-party logos. Skill names (HyperFrames, Shotcraft, Motionmaxxing, Lemo, Remotion, Earshot, Three.js) may appear as plain text in our fonts. No Claude/Anthropic logo, UI or mascot.

## Environment

- Always run first: `export HYPERFRAMES_CACHE_DIR=$HOME/.local/share/hyperframes-cache`
- Machine: Linux, 8 cores, Node 26, ffmpeg 7.0.2, Chrome at `/usr/bin/google-chrome`, Python 3.14 default (`uv` has 3.11/3.12).
- Do not install system software. npm/pip installs only inside `scenes/<id>/`.
- RENDER LOCK: other scene builders run at the same time. Wrap your FINAL full render (and any full-length draft render) in
  `flock /media/aiyu/550E85595197DBEC/Personal/Movies/projects/2026-11-20-studio-launch/scenes/.render.lock <render command>`
  so only one render runs at once. Single stills/snapshots do not need the lock.
- Do not invoke the `film-studio` skill. Do not ask the user questions: you are autonomous; make the design calls yourself from this packet.
- Adapter notes for each skill: `/media/aiyu/550E85595197DBEC/Personal/Movies/.claude/skills/film-studio/references/adapters.md`.

## Verify before you finish

1. `ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=width,height,r_frame_rate,nb_read_packets -of csv=p=0 scenes/<id>/clip.mp4` must show 1440,2560,30/1 and at least the required frames.
2. Extract stills at 10%, 50%, 90% (`ffmpeg -ss <t> -i clip.mp4 -frames:v 1 -vf scale=360:-1 still_N.png`) and look at them with the Read tool. Fix anything that breaks the style bible or quality bar, re-render once.

## Report back (short)

clip path, frame count, what is on screen, which skill files you actually used, anything that did not work.
