# OpenMontage

| Field | Value |
|---|---|
| Repo | <https://github.com/OpenMontageInc/OpenMontage> (README clone URL: `calesthio/OpenMontage`) |
| Checked | 2026-11-21, commit `2e003e65fa99`, ★82,047, last push 2026-11-16 |
| Licence | AGPL-3.0 (`LICENSE`). Commercial: yes for videos made with it (output is not the program). Do not copy its code into this repo, do not import its modules from repo scripts, do not offer it as a network service. We run it as a separate process (`bin/om.sh`) |
| Invoke | `bin/om.sh <tool> '<json inputs>'`; `bin/om.sh list` shows the tools usable now |
| Engine | Python tool registry (`tools/`), ffmpeg; optional Remotion/HyperFrames composers (not used) |
| Needs | Python 3.12 venv inside the clone (`uv`), ffmpeg. Optional API keys per tool (Pexels, Pixabay, fal, ...) |
| Install | `bin/setup-skills.sh openmontage` (clone, `uv venv --python 3.12 .venv`, `uv pip install -r requirements.txt`). We skip `make setup`: it installs Piper TTS (excluded voice) and the Remotion composer (unused) |
| Scope | External clone at `~/.local/share/skill-src/OpenMontage`, own venv (never this repo's `.venv`) |

## What it does

"Agentic video production system": 12 pipelines (`pipeline_defs/`), about 200 tools in `tools/` with a registry that reports status per machine (`registry.support_envelope()`), and Layer-2 skills in `skills/`.
Most generation tools are paid APIs. What runs here with no key (checked 2026-11-21, `bin/om.sh list`: 35 tools):

| Tool | What | Tested here |
|---|---|---|
| `direct_clip_search` | Stock footage search + download with licence and source URL per clip. Key-free sources: `nasa`, `wikimedia`, `archive_org`, `openverse`, `loc` (`coverr` needs a key in practice: 401) | Yes: 2 NASA clips for "earth from space" |
| `color_grade` | Grade profiles (`cinematic_warm/cool`, `moody_dark`, `bright_clean`, `vintage_film`, `high_contrast`, `neutral`) or a `.cube` LUT, with intensity | Yes |
| `auto_reframe` | Crop 16:9 footage to 9:16 / 1:1 (face-aware if a face track is given) | Yes |
| `scene_detect` | Shot boundaries of a long clip (pick usable ranges) | Yes |
| `video_trimmer`, `video_stitch`, `silence_cutter`, `audio_energy`, `audio_probe`, `frame_sampler`, `video_analyzer`, `visual_qa`, `composition_validator` | Footage prep and checks | Listed available, not run |
| `threejs_world`, `threejs_asset_catalog` | Procedural 3D world fly-through workspaces for HyperFrames/Three.js | Listed available, not run |
| `character_*`, `svg_rig_builder`, `pose_library_builder`, `action_timeline_compiler` | 2D SVG character rigs and animation | Listed available, not run |
| `screen_recorder` | Record the screen with ffmpeg | Not run |

Paid or unavailable here: every video/image generator, music generators, `upscale` and `face_restore` (need torch/GPU), `bg_remove` (needs `rembg`), `transcriber` (needs faster-whisper; use Parakeet).

## Use it for

- Real footage in a scene: documentary, science, history, travel. Search, download, grade, conform (adapters.md "OpenMontage").
- Reframing footage for vertical cuts.
- Picking usable ranges in long archive clips.

## Do not use it for

- Voice: every `*_tts`, `tts_selector`, `piper_tts`, `heygen_voice_convert`, avatar and lip-sync tool. `bin/om.sh` refuses names containing `tts`, `voice`, `avatar`, `lip_sync`, `talking_head`.
- Captions: `subtitle_gen`, `remotion_caption_burn`. Ours come only from `/film-captions`.
- Assembly: `video_compose`, `hyperframes_compose`, its pipelines. Our `assemble.py` does the cut and mix.
- Music: `pixabay_music` scrapes Pixabay (experimental; Content ID claims are common on YouTube). `freesound_music` mixes CC0, CC-BY and CC-BY-NC sounds. Neither goes in paid work without a per-file licence check.
- `video_downloader` (yt-dlp): never download other people's videos for a film.

## Voice hook

`tts_selector` routes to many cloud voices and Piper. All excluded. Narration comes from `bin/vo.sh`; OpenMontage only touches picture.

## Output

Whatever path the JSON gives (`output_dir`, `output_path`). `direct_clip_search` writes `<output_dir>/clips/*.mp4` + thumbnails and returns per clip `source`, `license`, `source_url`.

## Limits and risks

- AGPL-3.0: keep it a separate program. A script in this repo that imported its modules and was shared would have to be AGPL too.
- Stock licences differ per source and per item: NASA "public domain with caveats" (no NASA logo or endorsement), Wikimedia/Openverse per file (CC BY needs credit, CC BY-SA share-alike, NC never), Library of Congress "verify per item". Write each clip's licence and URL in `NOTE.md`.
- `direct_clip_search` returns `duration: 0.0` for NASA clips: probe with ffprobe.
- Pipelines and many tools are experimental (per-tool `stability` field).

## Our take

Opinion: worth it for one thing we lacked, real footage with provenance. Its colour grade and reframe are handy ffmpeg wrappers. The rest overlaps our pipeline or needs paid keys.
