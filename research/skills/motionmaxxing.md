# Motionmaxxing

| Field | Value |
|---|---|
| Repo | <https://github.com/Tejashmakwana/motionmaxxing> |
| Checked | 2026-11-20, commit `8c8ec0f2a6f6`, ★1,702, last push 2026-10-06. Status: "early release" |
| Licence | Apache-2.0 for original work. Bundled GSAP 3.12.5 is under GreenSock's "No Charge" Standard License (`NOTICE`). Commercial: yes |
| Invoke | `/motionmaxxing` |
| Engine | Plain HTML + its `Motion` runtime (seek-safe GSAP), rendered by `scripts/render.mjs`; works in HyperFrames too |
| Needs | Node 22+, Python 3.9+, ffmpeg, Google Chrome. Optional: `ELEVENLABS_API_KEY`, Codex CLI image generation |
| Install | `git clone https://github.com/Tejashmakwana/motionmaxxing ~/.claude/skills/motionmaxxing && bash ~/.claude/skills/motionmaxxing/install.sh` (install.sh only checks requirements, installs nothing system-wide) |
| Scope | Global user skill |

## What it does

"Turns AI slop videos into films that look made by a motion designer" (README). Launch films, promos, brand stings, kinetic type.
Built from measurement: 53 pro moments, about 4,300 moves, 12 measured eases, about 150 designer rules (README "The science of the mog").
Key numbers: median move 10 frames; landings ease out, exits ease in; overshoot under 9%; arrive from oversize, nothing grows from zero; pros cut on motion.
Gates: G0 render exists, G1 proof readable, G2 no >3 flat frames, G3 end hold <= 1.4 s, G4 one hero per frame, G5 no page chrome (`look.py`, `lint.mjs`).
10-step protocol: brand capture (`brand.mjs`, `fetch_logo.mjs`) to idea to storyboard to build to gates to sound to deliver.

## Use it for

- Launch films and brand stings where an idea matters more than showing every UI screen.
- "Rate and repair" any mid video (from any skill): run its gates.

## Output

`film/final.mp4`, `film/index.html` (editable source), `film/STORYBOARD.md`, `film/NOTE.md` with gate numbers.

## Voice hook

Its built-in voice (`voice.py`: ElevenLabs, macOS `say`) is excluded. For reference: default voice is ElevenLabs (`voice.py`). Without a key it falls back (`references/sound-sync.md` section 9). It states: "WHEN the user supplies their own music or voice DO use it, measure its BPM or word times".
So: make VO with `bin/vo.sh` (gives `vo.words.json` via `npx hyperframes transcribe`), then mix with `python3 scripts/mix.py --vo film/audio/vo/line01.wav@<t> ...` (`SKILL.md` line 120).
Its macOS `say` fallback does not apply on Linux.

## Limits and risks

- Early release (`docs/KNOWN-LIMITS.md`).
- Without ElevenLabs it makes no music. Get music elsewhere: Lemo-Opuscar sampler, Earshot SFX bank, or licensed tracks logged in `assets/LEDGER.md`.
- The README before/after demos use real brands (Cluely, Spotify, Wispr Flow) "only to show the difference". Do not reuse those films.

## Our take

Best taste layer in the stack. Its gates and rules raise any film's quality; use them as a checklist even when another skill builds the film.
