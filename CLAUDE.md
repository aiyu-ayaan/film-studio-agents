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
| `assets/` | Shared, reusable media (not tied to one channel): `brand/<client>/`, `music/`, `sfx/`, `fonts/`, `footage/`, `images/`. Every file is logged in `assets/LEDGER.md`. |
| `todo/` | Planned videos, one file each, in order (`todo/README.md`). Pick the next video here. |
| `business/` | Paid work: `leads.md`, `clients/<name>/`. |
| `channel/<name>/` | One folder per own channel. `channel/renderstand/` = the Renderstand page (Instagram, Facebook, YouTube @renderstand.studio): `profile.md` (links, niche, viewer, peers), `format.md` (45 s reel rules), `ideas.md` (scored backlog), `swipe.md` (outliers, when made), brand (`DESIGN.md`, `tokens.css`, `pixels.js`, logos, banner), `posts/`, `outro/` (the cached outro). Local only, not in git. |
| `studio/` | Film Studio desktop app (Tauri: Rust `src-tauri/`, TypeScript `src/`). Runs any agent CLI on the pipeline; reads progress from project files; gates via `.studio/gate.json`, handoff via `.studio/handoff.md` (see film-studio "Gates and handoff"). |
| `bin/` | `studio.sh` (open the app, release build), `new-project.sh`, `vo.sh` (voiceover + word timings), `setup-skills.sh` (install skills), `om.sh` (run one OpenMontage tool), `clean.sh` (stage 9: delete rebuildable bulk). |
| `.agents/skills/` | Real home of all project skills (film-*, design skills, remotion-*). `.claude/skills/` and `.hermes/skills/` hold relative symlinks to it, so any agent tool finds them. `AGENTS.md` links to this file. Add a new project skill here, then symlink it into both. |

## Context map: check these before any work

Nothing here lives only in a chat. Before planning, scripting or making a video, read what applies:

| Working on | Read first |
|---|---|
| Anything for the Renderstand page | `channel/renderstand/profile.md` (links, niche), then `format.md` and `DESIGN.md` in the same folder |
| "What next?", a new idea, a script | `todo/README.md` (the ordered plan) and the todo file it points to |
| A film in progress | `projects/<date>-<slug>/.studio/handoff.md`, then its `plan.json` |
| Paid work | `business/` |
| Which skill does what | the registry below; `README.md` "Skills" |

Write back to the same places: new ideas go to `todo/` (one file each, listed in `todo/README.md`), scores and posted results to `channel/<name>/ideas.md`, channel facts (handles, niche, viewer, peers) to `channel/<name>/profile.md`, stage progress to the project's `.studio/handoff.md`. A new channel gets its own `channel/<name>/` with the same files.

## Skill registry (router)

Pick the skill by the job. This mapping is our design choice, not something the repos state.
Install state checked 2026-11-21 (all present). Herk and OpenMontage live in `~/.local/share/skill-src/` (not symlinked: see their cards). Run `bin/setup-skills.sh <name>` to install one.

| Job | Skill (invoke) | Engine | Card | Commercial use | Installed |
|---|---|---|---|---|---|
| **A whole film (default): story + voice + scenes from several skills + music + captions** | **film-studio (`/film-studio`)** | orchestrator, ffmpeg assembly | `.claude/skills/film-studio/` | Ours | Yes, project |
| A whole film with no narration, cut to music | film-studio-nospeech (`/film-studio-nospeech`) | same | `.claude/skills/film-studio-nospeech/` | Ours | Yes, project |
| Intro, chapter bridges and outro for films with topic sections (add-on, stages 1, 2, 5) | film-framing (`/film-framing`) | plan.json roles + `framing_check.py` | `.claude/skills/film-framing/` | Ours | Yes, project (2026-11-21) |
| Score a channel video idea out of 100 before making it (IG Reels + YT Shorts) | film-idea-score (`/film-idea-score`) | rubric + `score.py` | `.claude/skills/film-idea-score/`, `research/viral-roadmap.md` | Ours | Yes, project (2026-11-21) |
| Channel outro (about 2.9 s, "More tomorrow. Follow Renderstand."): built once, appended to any reel | film-outro (`/film-outro`) | `outro.py` (cached in `channel/renderstand/outro/`) | `.claude/skills/film-outro/` | Ours | Yes, project (2026-11-21) |
| Captions on any video (the only skill that adds captions) | film-captions (`/film-captions`) | ASS + libass | `.claude/skills/film-captions/` | Ours; Montserrat OFL | Yes, project |
| General edits, any single scene with no better fit, render/preview | HyperFrames (`/hyperframes`) | HyperFrames | `research/skills/hyperframes.md` | Yes (Apache-2.0) | Yes, global |
| Real-UI product promo from a website or app, Ink Press template | Shotcraft (`video-shotcraft`) | HyperFrames (fork) or Remotion (upstream) | `research/skills/shotcraft.md` | Yes (Apache-2.0); 5 SFX excluded | Yes, global (2026-11-20) |
| Idea-led launch film, brand sting, kinetic type, "fix this mid video" | Motionmaxxing (`/motionmaxxing`) | HTML + GSAP runtime | `research/skills/motionmaxxing.md` | Yes (Apache-2.0, GSAP own terms) | Yes, global (2026-11-20) |
| Narrated film in a named look (99 styles: watercolor, news, chalkboard...) | Lemo-Opuscar (`/lemo-opuscar:lemo-opuscar`) | canvas/WebGL frame render | `research/skills/lemo-opuscar.md` | Films yes; style docs CC BY-NC | Yes, user plugin (library downloads on first use) |
| 3D hero scene, STEM/3D explainer, explorable world | 3DViz Pro Max (`/3dviz-pro-max`) | Three.js (+ Blender) | `research/skills/3dviz-pro-max.md` | Yes (MIT) | Yes, global symlink |
| Sound: pick/make SFX, check sync and loudness, critique the mix | Earshot (`earshot` CLI / MCP) | Python, CPU | `research/skills/earshot.md` | Yes (MIT) | Yes, CLI + MCP (skill files not installed) |
| Edit the user's own recording: cut silences and mistakes, long-form edit, 9:16 reel from their footage | Herk Edit Kit (`cut-silences`, `cut-mistakes`, `edit-video`, `short-form-edit`; run by absolute path) | Node + ffmpeg, HyperFrames | `research/skills/herk-edit-kit.md` | Yes (MIT + use permission); AIS brand excluded | Yes, `~/.local/share/skill-src/herk-edit-kit` (2026-11-21) |
| Editorial explainer card scene (section, stat, quote, list, lower third): 406 cards | Herk Edit Kit `style-library` (recipe key `card`) | HyperFrames + GSAP | `research/skills/herk-edit-kit.md` | Yes | Yes, same clone |
| Real stock footage scene (NASA, Wikimedia, Archive.org, Openverse, LoC), colour grade, reframe to 9:16, shot detection | OpenMontage tools via `bin/om.sh` (recipe key `footage`) | Python + ffmpeg, separate process | `research/skills/openmontage.md` | Videos yes; code AGPL-3.0: only `bin/om.sh` (AGPL) imports it | Yes, `~/.local/share/skill-src/OpenMontage` (2026-11-21) |
| React video only when the user or client asks for Remotion | Remotion (`/remotion-create`) | Remotion | `research/skills/remotion.md` | Yes for individual or <=3 employees | Yes, project skills in `Movies/.claude/skills` |

Routing rules:
- Any request for a finished video goes to `/film-studio` (or `-nospeech`). It calls the skills below per scene.
- Captions only through `/film-captions`. Other skills' caption features stay off.
- Outro only through `/film-outro`: `outro.py status`, then `append`. Never rebuild the cached outro unless the user asks.
- The global `hyperframes` skill calls itself the mandatory entry point. In this folder, use the table above first. Use HyperFrames when no row fits better.
- Earshot runs on every film before delivery (see "Quality gate").
- Footage the user recorded (not a film we write and voice) goes to Herk Edit Kit; finish with `/film-captions` and the quality gate. A film-studio film can still use a Herk card scene or an OpenMontage footage scene.
- OpenMontage runs only through `bin/om.sh` (AGPL-3.0; that file is the only one that imports it: never copy or import its code elsewhere). Never use its TTS, avatar, caption, assembly or `video_downloader` tools.
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
HyperFrames `/media-use` and faceless-explainer `audio.mjs` (HeyGen, ElevenLabs, Gemini voices), Motionmaxxing `voice.py` (ElevenLabs, macOS `say`), Lemo-Opuscar `core/tts` (its own Kokoro and edge-tts), Remotion `@remotion/elevenlabs`, Herk Edit Kit `npx hyperframes tts` and `transcribe-elevenlabs.mjs` (uploads audio), OpenMontage `tts_selector`, every `*_tts` tool and Piper, KittenTTS, VoiceStudio, and any cloud TTS.
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
