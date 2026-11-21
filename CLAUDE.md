# Movies: video studio run by Claude

This folder makes videos with Claude Code skills. Each video is code (HTML/React/Three.js) rendered to MP4, with a local voice and code-made sound.
Read `research/CLAUDE.md` for the facts behind every rule here: what each skill does, install, licences, TTS choice, money plan.

## Layout

| Path | What it holds |
|---|---|
| `CLAUDE.md` | This file: the router, the pipeline, the rules. The skill registry lives only here. |
| `research/` | Research notes. One card per skill in `research/skills/`, plus `tts.md`, `licenses.md`, `monetization.md`. |
| `projects/<YYYY-MM-DD>-<slug>/` | One folder per video. Make it with `bin/new-project.sh <slug>`. |
| `templates/project/` | The skeleton every project starts from. Edit it to change all future projects. |
| `assets/` | Shared, reusable media: `brand/`, `music/`, `sfx/`, `fonts/`, `footage/`, `images/`. Every file is logged in `assets/LEDGER.md`. |
| `business/` | Paid work: `leads.md`, `clients/<name>/`. |
| `channel/` | Own IG + YouTube channel: `profile.md` (niche, viewer, peers), `swipe.md` (outliers), `ideas.md` (scored backlog). Made by `/film-idea-score` on first run. |
| `studio/` | Film Studio desktop app (Tauri: Rust `src-tauri/`, TypeScript `src/`). Runs any agent CLI on the pipeline; reads progress from project files; gates via `.studio/gate.json`, handoff via `.studio/handoff.md` (see film-studio "Gates and handoff"). |
| `bin/` | `studio.sh` (open the app, release build), `new-project.sh`, `vo.sh` (voiceover + word timings), `setup-skills.sh` (install skills), `clean.sh` (stage 9: delete rebuildable bulk). |
| `.agents/skills/` | Real home of project skills (film-*, remotion-*). `.claude/skills/` and `.hermes/skills/` hold relative symlinks to it, so any agent tool finds them. `AGENTS.md` links to this file. Add a new project skill here, then symlink it into both. |

## Skill registry (router)

Pick the skill by the job. This mapping is our design choice, not something the repos state.
Install state checked 2026-11-20 (all 7 present). Run `bin/setup-skills.sh <name>` to install one.

| Job | Skill (invoke) | Engine | Card | Commercial use | Installed |
|---|---|---|---|---|---|
| **A whole film (default): story + voice + scenes from several skills + music + captions** | **film-studio (`/film-studio`)** | orchestrator, ffmpeg assembly | `.claude/skills/film-studio/` | Ours | Yes, project |
| A whole film with no narration, cut to music | film-studio-nospeech (`/film-studio-nospeech`) | same | `.claude/skills/film-studio-nospeech/` | Ours | Yes, project |
| Intro, chapter bridges and outro for films with topic sections (add-on, stages 1, 2, 5) | film-framing (`/film-framing`) | plan.json roles + `framing_check.py` | `.claude/skills/film-framing/` | Ours | Yes, project (2026-11-21) |
| Score a channel video idea out of 100 before making it (IG Reels + YT Shorts) | film-idea-score (`/film-idea-score`) | rubric + `score.py` | `.claude/skills/film-idea-score/`, `research/viral-roadmap.md` | Ours | Yes, project (2026-11-21) |
| Captions on any video (the only skill that adds captions) | film-captions (`/film-captions`) | ASS + libass | `.claude/skills/film-captions/` | Ours; Montserrat OFL | Yes, project |
| General edits, any single scene with no better fit, render/preview | HyperFrames (`/hyperframes`) | HyperFrames | `research/skills/hyperframes.md` | Yes (Apache-2.0) | Yes, global |
| Real-UI product promo from a website or app, Ink Press template | Shotcraft (`video-shotcraft`) | HyperFrames (fork) or Remotion (upstream) | `research/skills/shotcraft.md` | Yes (Apache-2.0); 5 SFX excluded | Yes, global (2026-11-20) |
| Idea-led launch film, brand sting, kinetic type, "fix this mid video" | Motionmaxxing (`/motionmaxxing`) | HTML + GSAP runtime | `research/skills/motionmaxxing.md` | Yes (Apache-2.0, GSAP own terms) | Yes, global (2026-11-20) |
| Narrated film in a named look (99 styles: watercolor, news, chalkboard...) | Lemo-Opuscar (`/lemo-opuscar:lemo-opuscar`) | canvas/WebGL frame render | `research/skills/lemo-opuscar.md` | Films yes; style docs CC BY-NC | Yes, user plugin (library downloads on first use) |
| 3D hero scene, STEM/3D explainer, explorable world | 3DViz Pro Max (`/3dviz-pro-max`) | Three.js (+ Blender) | `research/skills/3dviz-pro-max.md` | Yes (MIT) | Yes, global symlink |
| Sound: pick/make SFX, check sync and loudness, critique the mix | Earshot (`earshot` CLI / MCP) | Python, CPU | `research/skills/earshot.md` | Yes (MIT) | Yes, CLI + MCP (skill files not installed) |
| React video only when the user or client asks for Remotion | Remotion (`/remotion-create`) | Remotion | `research/skills/remotion.md` | Yes for individual or <=3 employees | Yes, project skills in `Movies/.claude/skills` |

Routing rules:
- Any request for a finished video goes to `/film-studio` (or `-nospeech`). It calls the skills below per scene.
- Captions only through `/film-captions`. Other skills' caption features stay off.
- The global `hyperframes` skill calls itself the mandatory entry point. In this folder, use the table above first. Use HyperFrames when no row fits better.
- Earshot runs on every film before delivery (see "Quality gate").
- Do not add `video-talkcraft`: its licence (PolyForm Noncommercial) forbids paid use.

## Add a new skill

1. Copy `research/skills/_TEMPLATE.md` to `research/skills/<name>.md` and fill every field. Pin the commit.
2. Add one row to the registry table above.
3. Add an install case to `bin/setup-skills.sh`.
4. Add a licence row to `research/licenses.md`.
5. If the skill makes its own voice, note in its card ("Voice hook") how to switch that off and feed it our `bin/vo.sh` wav. Its voice is never used.
6. Add an adapter section to `.claude/skills/film-studio/references/adapters.md` (silent clip at master size/fps/length), test one scene, mark it tested.

## Pipeline for every video

Run `/film-studio` (narrated, default) or `/film-studio-nospeech`. Stages, all in `.claude/skills/film-studio/SKILL.md`:
0 setup > 1 story + script > 2 storyboard + style bible (user approves) > 3 voice + timing (`narrate.py`) or beat timing (`timing.py`) > 4 scenes, one silent clip per scene from the chosen skill > 5 music + SFX > 6 assemble (`assemble.py`) > 6b captions (`/film-captions`) > 7 review > 8 deliver (`NOTE.md` credits) > 9 cleanup (`bin/clean.sh`).
Self-test of the scripts: `.claude/skills/film-studio/scripts/selftest.sh` (about 35 s).

## Voice policy

**Only two voices are allowed: Kokoro-82M and Pocket TTS, always made with `bin/vo.sh` (or `narrate.py`, which calls it).**
Built-in voices of every skill and library are excluded, even when a skill picks one by default:
HyperFrames `/media-use` and faceless-explainer `audio.mjs` (HeyGen, ElevenLabs, Gemini voices), Motionmaxxing `voice.py` (ElevenLabs, macOS `say`), Lemo-Opuscar `core/tts` (its own Kokoro and edge-tts), Remotion `@remotion/elevenlabs`, KittenTTS, VoiceStudio, and any cloud TTS.
When a skill reaches its voice step, skip it and give it our wav from `audio/vo/`.

| Engine | Use | Speed on this PC | Command |
|---|---|---|---|
| Kokoro-82M (Apache-2.0) | Clean narration; voices af_heart, af_nova, am_michael, bm_george ... | 5 s line in ~9 s incl. word timings | `bin/vo.sh kokoro script.txt out.wav [voice]` |
| Pocket TTS (Kyutai; weights CC BY 4.0) | Most human option: clone the user's own voice from a 5-20 s clean wav | 5 s line in ~10 s incl. word timings | `bin/vo.sh pocket script.txt out.wav [my_voice.wav]` |

- Which of the two is the default: PENDING the user's ear test of `research/tts-audition/*.wav` (2026-11-20). Until set in `plan.master.voice_engine`, ask once.
- `narrate.py` and `vo.sh` refuse any other engine.
- Follow "Make any TTS sound human" in `research/tts.md` for every script. One line per take.
- `bin/vo.sh` needs `.venv/` here (kokoro-onnx, pocket-tts, CPU torch) and Parakeet (installed 2026-11-20) for word timings.
- Pocket TTS: credit Kyutai in the video description. Clone only the user's own voice or a client's with written consent.

## Quality gate (before delivery)

- `earshot critique renders/final.mp4`: fix every "major" item. `earshot sheet renders/final.mp4 -o renders/sheet.png` to see sync against picture.
- Loudness: -14 LUFS for YouTube/social, true peak <= -1 dBTP (`earshot measure`).
- Look at a contact sheet of frames. No dead frames, no corner labels or counters (motionmaxxing gates G0-G5 apply to any film).
- Captions present for social cuts. Text readable at phone size.

## Rules for agents working here

- Machine: 8 cores, 31 GB RAM, GTX 1650 4 GB, ffmpeg 7.0.2 static, Chrome at `/usr/bin/google-chrome`, Node 26. Default `python3` is 3.14: use `uv` with Python 3.11 or 3.12 for kokoro-onnx, earshot and lemo-opuscar.
- Every `npx hyperframes` command needs `export HYPERFRAMES_CACHE_DIR=$HOME/.local/share/hyperframes-cache` (or fix `~/.cache` with `chmod go-w ~/.cache`).
- Render with `--workers 1` or `2` if HyperFrames runs out of memory.
- Never put a third-party logo, character or trademark in a paid video without the client's rights. Never use Clawd (Anthropic's mascot) from lemo-opuscar.
- Log every asset you add to `assets/` in `assets/LEDGER.md` with source URL and licence. No source, no use in paid work.
- YouTube work: vary style per video, add original research or a human angle, disclose realistic synthetic media. See `research/monetization.md`.
- Keep `research/` facts dated. When a fact changes, update the card and the date.
