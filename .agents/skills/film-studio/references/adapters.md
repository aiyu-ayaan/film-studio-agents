# Scene adapters: how each skill makes one clip

Contract for every adapter (and any skill added later):
- Output `scenes/<id>/clip.mp4`, master width/height/fps, at least `frames` frames long (`frames / fps` seconds).
- Picture only. Any audio in the clip is dropped by assemble.py. Sound the scene needs goes in `scenes/<id>/sfx.wav` (aligned to the scene's t=0) and `scenes[].sfx_stem`.
- Use `style.md` (palette, fonts). Keep on-screen text out of the bottom 20%: film-captions puts captions there.
- Never paint the narration or a subtitle line as on-screen text: captions already show it. On-screen text = titles, labels, numbers, kinetic-type hits.
- Start already moving, end mid-move: the assembler hard-cuts.
- Too long is fine (cut). Too short is held on its last frame: avoid it.

## Recipe: pick the skill's own parts before building (stage 2, director does it once)

Why: the first four films hand-drew flat SVG scenes and held them still (buddha s2-s7: 77-100% frozen frames). The installed skills hold hundreds of ready blueprints, blocks, shot cards, styles and 3D records. Each scene must name the parts it uses in `scenes[].recipe`. `scene_check.py --recipes-only` refuses a scene without them.

Run the searches yourself, pick, and write the result into plan.json. Subagents then read only the files the recipe names, never a whole skill folder (saves tokens: Motionmaxxing `references/` alone is over 200 KB).
`S=~/.claude/skills`. All commands checked on 2026-11-20.

| Recipe key | For | How to find it |
|---|---|---|
| `blueprint` | HyperFrames scenes | Read `$S/hyperframes-animation/blueprints-index.md` (22 time-coded shot shapes); pick one id. File: `blueprints/<id>.md` |
| `registry` | HyperFrames scenes (list, 1-4 items) | `node $S/hyperframes/scripts/plugin-cli.mjs catalog --query "<what the beat does, English>" --json` (448 blocks: backgrounds, grain, light, transitions, kinetic type, charts, 3D). Install in the scene: `... add <name> --json` |
| `camera` | every scene | A named move: push-in, orbit, parallax dolly, crash zoom, pan between stations. Patterns: `$S/hyperframes-keyframes/references/keyframe-patterns.md`; Shotcraft `demos/camera/<name>/` |
| `precedent` | Motionmaxxing scenes | `python3 $S/motionmaxxing/scripts/precedent.py query --beat hook\|turn\|proof\|cta --content type\|logo\|number\|3d\|ui --text "<the idea>"`; write the row ids (e.g. `PM913`) |
| `shot_card` | Shotcraft scenes | `$S/video-shotcraft/demos/README.md`, then one folder `demos/<category>/<name>/` |
| `style` | Lemo scenes (one per film) | `~/lemo-opuscar/styles/README.md` (101 styles); folder name, e.g. `watercolor`, `ink-wash`, `impasto`, `chalkboard` |
| `record` | 3D scenes | `cd $S/3dviz-pro-max && python3 scripts/search.py "<subject + look>" --limit 5`; then `python3 scripts/resolve.py <id>` for the chosen ids |
| `words` | every speech scene (auto) | The line's word times from `audio/vo/vo.words.json`, minus the scene's `start_s`. Reveals land on the spoken word |

Pick the base engine by film type, not by habit:
- Story, history, myth, spiritual: a Lemo painted style (`ink-wash`, `watercolor`, `impasto`, `ukiyoe`, `shadow-puppet`, `woodcut`, `gilded-illumination`) for most scenes. Motionmaxxing only for the hook and the end card.
- Science, STEM: 3D (HyperFrames Three.js + a 3DViz `record`) for the hero, Lemo `chalkboard`/`blueprint`/`colored-pencil` for diagrams.
- Product, launch, brand: Motionmaxxing + Shotcraft, HyperFrames blueprints for UI beats.
- Never make a hand-drawn flat SVG figure (stick person, clip-art tree) the hero of a frame. Use a style, a 3D model, a registry block or real imagery.

Every scene, every engine: a camera move runs the whole scene; a new visual event at least every 2 s, timed to `words`; no static title + subtitle header.

Status: tested = ran end to end here on 2026-11-20. Untested = documented from the skill's own files, the skill was not installed yet.

## HyperFrames (default; also 3D and anything without a better fit) [tested 2026-11-20]

- Skills: `/hyperframes-core` (composition contract), `/hyperframes-animation` (motion; `adapters/three.md` for Three.js), `/hyperframes-registry` (ready blocks), `/hyperframes-keyframes` (camera moves).
- Do not use the orchestrator skills `faceless-explainer` / `general-video` for one scene: they run their own audio and HeyGen preflight.
- Always first: `export HYPERFRAMES_CACHE_DIR=$HOME/.local/share/hyperframes-cache` (this PC's `~/.cache` is group-writable and HyperFrames refuses it).
- Build in `scenes/<id>/` (`npx hyperframes init scenes/<id> --non-interactive --example=blank`; note: init may also update the global HyperFrames skills). Root composition `data-width`/`data-height` = master; duration = `frames / fps`.
- Render: `cd scenes/<id> && npx hyperframes render --fps <fps> --quality delivery --output clip.mp4` (`--quality draft` for drafts). Tested: a 2.4 s 1920x1080 GSAP scene rendered in 7 s (first run adds ~1 min setup).
- Check: `npx hyperframes check`, `npx hyperframes snapshot --at <s>`.

## 3D scenes: 3DViz Pro Max + HyperFrames [untested]

- 3DViz has no video recorder (`scripts/capture.py` writes PNG stills only). Our design choice: build the scene as a HyperFrames composition with the Three.js adapter, using 3DViz for direction (recipes, kits, style profiles: `python3 scripts/search.py`, `resolve.py <record-id>`).
- The scene must be seek-safe: state is a function of time, no free-running animation loop.
- Fallback for a still hero: 3DViz capture PNG + slow camera move in HyperFrames.

## Shotcraft (video-shotcraft, HyperFrames fork) [untested]

- Use for scenes that show real product UI (web/desktop captures, 2.5D page camera).
- Copy the needed shot card's demo (`demos/<category>/<name>/`) or the Ink Press template into `scenes/<id>/`; set duration = `frames / fps`.
- Render: `npx hyperframes render --fps <fps> --output clip.mp4`. Ink Press ships a pinned BGM + SFX pass: it is dropped by the assembler. To keep its SFX, export them as `sfx.wav`.
- Never use the 5 untraceable SFX (`research/skills/shotcraft.md`).

## Motionmaxxing [untested]

- Use for the hook, idea beats, brand stings, kinetic type, the end card.
- Build `scenes/<id>/film/index.html` with its runtime (follow its SKILL.md steps 2-7; skip its voice and sound steps: this skill owns sound).
- Render: `node ~/.claude/skills/motionmaxxing/scripts/render.mjs scenes/<id>/film/index.html scenes/<id>/clip.mp4 --fps <fps> --width <w> --height <h> --duration <s>` with no `--audio`. Optional `--shutter 180` for motion blur on hero moves.
- Gates: `node ~/.claude/skills/motionmaxxing/scripts/lint.mjs scenes/<id>/film/index.html` (G5 page chrome). Dead frames: `scene_check.py` (`look.py` fails here: this ffmpeg build has no `drawtext`).

## Lemo-Opuscar [untested]

- Use for a painted, documentary, chalkboard, news or other named look. Pick ONE style per film (style.md maps to it).
- Build the scene page per its `TECHNIQUE.md` §2 (`window.DUR`, `window.render(t)`, `window.READY`) and the style's `STYLE.md`.
- Render picture only: `cd $LIB && node core/render/video.mjs <scene_dir> --fps <fps> --size <w>x<h> --out <scene_dir>/clip.mp4`. Skip its `mix.py` and `mux.sh`.
- Its voice (Kokoro) and score tools are not used per scene; its sampler is used for the film's music (`audio.md`).

## Remotion [untested; only when asked]

- Render muted at the master size: `npx remotion render <CompositionId> scenes/<id>/clip.mp4 --muted` with the composition's width/height/fps/durationInFrames set to master values.
- Licence: free for an individual or up to 3 employees.

## Adding a new skill as an adapter

1. Add a section here: when to use, where it builds, exact render command for a silent clip at master w/h/fps and a given length, what audio it produces and how to drop or export it.
2. Run one scene through it, then assemble.py. Change "[untested]" to "[tested <date>]".
3. Follow the rest of "Add a new skill" in the root `CLAUDE.md`.
