# Movies

A video studio run by AI coding agents (Claude Code and any tool that reads `AGENTS.md`). Each film is code (HTML, React, Three.js) rendered to MP4, with a local voice and code-made sound.

Ask for a film; the `film-studio` skill writes the story, voices it, builds each scene with the best-fitting video skill, mixes the sound, adds captions and checks the result.

## Demo

The studio launch film, made by the studio itself (47 s, vertical, narrated):

<img src="docs/launch.gif" alt="Studio launch film" width="270">

[Full video with sound: `docs/launch.mp4`](docs/launch.mp4) (the GIF is silent; this is a 720p copy, the full-quality master stays local at `projects/2026-11-20-studio-launch/renders/final.mp4`).

## Quick start

```bash
bin/new-project.sh my-film        # makes projects/<date>-my-film/ from templates/project/
# then, in your agent: /film-studio  "a 60 s explainer about ..."
```

Narrated film: `/film-studio`. Music-led film with no speech: `/film-studio-nospeech`. Captions on any video: `/film-captions`.

## How a film is made

`story + script` > `storyboard + recipe per scene` (you approve) > `voice + timing` > `scenes` > `music + SFX` > `assemble` > `captions` > `review` > `deliver`.

Every scene carries a `recipe` in `plan.json`: the blueprint, registry blocks, camera move, shot card, Lemo style or 3D record it uses. `scene_check.py` refuses a scene with a missing or invented recipe, a wrong size, or more than 40% frozen frames.

## Layout

| Path | What it holds |
|---|---|
| `AGENTS.md` / `CLAUDE.md` | Rules, skill router, pipeline. `AGENTS.md` is a symlink to `CLAUDE.md`. |
| `.agents/skills/` | Project skills (film-*, remotion-*). `.claude/skills/` and `.hermes/skills/` link here. |
| `research/` | Dated notes: one card per skill, TTS, licences, money plan. |
| `projects/<date>-<slug>/` | One folder per film: `plan.json`, script, storyboard, scene sources. |
| `templates/project/` | Skeleton for new projects. |
| `assets/` | Shared media, each file logged in `assets/LEDGER.md` with source and licence. |
| `business/` | Paid work: leads and clients. |
| `bin/` | `new-project.sh`, `vo.sh` (voice + word timings), `setup-skills.sh`. |

## Not in git

Rebuildable or heavy files are ignored (see `.gitignore`): `.venv/`, `node_modules/`, all audio and video (`renders/`, `build/`, `audio/`, scene `clip.mp4`), and copies the skills vendor into each scene. Regenerate a film from its `plan.json`, `script.md` and scene sources.

## Setup

- Machine used: 8 cores, 31 GB RAM, GTX 1650, ffmpeg 7, Chrome, Node, Python 3.11/3.12 via `uv`.
- Python env: `.venv/` with kokoro-onnx, pocket-tts and CPU torch (see `research/tts.md`).
- Install the video skills: `bin/setup-skills.sh all` (HyperFrames, Shotcraft, Motionmaxxing, 3DViz, Earshot, Lemo-Opuscar, Remotion). They install into `~/.claude/`, not this repo.
- Every `npx hyperframes` command needs `export HYPERFRAMES_CACHE_DIR=$HOME/.local/share/hyperframes-cache`.
- Self-test of the film scripts (about 35 s): `.agents/skills/film-studio/scripts/selftest.sh`.

## Voice and licences

Only two voices are allowed: Kokoro-82M (Apache-2.0) and Pocket TTS (Kyutai, CC BY 4.0, credit Kyutai). Both run locally through `bin/vo.sh`. Skill and licence details: `research/licenses.md`. No third-party logo or character in paid work without rights.
