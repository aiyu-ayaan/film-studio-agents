# HyperFrames (HeyGen)

| Field | Value |
|---|---|
| Repo | <https://github.com/heygen-com/hyperframes> |
| Checked | 2026-11-20, commit `a755e3f58588`, ★87,206, last push 2026-11-20. CLI on this PC: v0.9.72 |
| Licence | Apache-2.0. Commercial: yes |
| Invoke | `/hyperframes` (entry point, routes to sub-skills). CLI: `npx hyperframes <cmd>` |
| Engine | Plain HTML + `data-*` timing attributes, seeked frame by frame in headless Chrome, encoded with FFmpeg |
| Needs | Node.js 22+, FFmpeg (README "Requirements") |
| Install | Already installed globally (`~/.claude/skills/hyperframes*`). Refresh: `npx hyperframes skills update` |
| Scope | Global user skills |

## What it does

Open-source AI video editor: "Describe any video and get a real project you can change down to the frame" (repo description).
Compositions are HTML files. The same input renders the same video (README line 252).
Core skill set: `/hyperframes`, `/hyperframes-cli`, `/hyperframes-registry`, `/media-use`, `/reverse-any-video`, `/style-sampling`. On demand: `/figma`, `/slideshow`, `/remotion-to-hyperframes` (README line 90).
Installed here also: `faceless-explainer`, `product-launch-video`, `pr-to-video`, `motion-graphics`, `music-to-video`, `embedded-captions`, `talking-head-recut`, `general-video`, `hyperframes-animation`, `-audio`, `-keyframes`, `-creative`, `-core`, `-studio`.
Registry: about 400 hosted blocks and components (CRT, glitch, charts, terminal windows, maps, confetti) per the `hyperframes-registry` skill description.

## Useful CLI (v0.9.72)

| Command | Use |
|---|---|
| `npx hyperframes init` | New project |
| `npx hyperframes preview` / `render --output out/x.mp4` | Preview / render |
| `npx hyperframes snapshot --at 5` | Still frame for checking |
| `npx hyperframes tts "text" -o vo.wav -v af_heart` | Kokoro-82M local voice. Voices: af_heart, af_nova, af_sky, am_adam, am_michael, bf_emma, bf_isabella, bm_george (+ non-English) |
| `npx hyperframes transcribe vo.wav --json` | Word-level timestamps (Parakeet or whisper.cpp). `--to srt` for captions |
| `npx hyperframes remove-background` | Cutouts |
| `npx hyperframes lambda` / `cloudrun` | Cloud rendering |

## Use it for

- Any video with no better row in the registry. Captions on footage, talking-head recuts, slideshows, music videos, PR/changelog videos, faceless explainers.
- The render engine under Shotcraft (fork) and as an option for Motionmaxxing.

## Voice hook

Its built-in voices (`/media-use` HeyGen/ElevenLabs/Gemini, faceless-explainer `audio.mjs`) are excluded. `npx hyperframes tts` is used only through `bin/vo.sh kokoro`. Pass our VO wav as a user file; HyperFrames places audio as a clip.

## Limits and risks

- Some features bill HeyGen (HeyGen voice, `--engine heygen` transcription, avatars). Stay on local options to keep cost zero.
- Low-core or low-RAM renders: use `--concurrency=1` (Shotcraft README "Headless / CI notes").

## Our take

The best base for paid work: Apache licence, HTML is easy for Claude to write, deterministic renders, big registry. Default engine for this studio.
