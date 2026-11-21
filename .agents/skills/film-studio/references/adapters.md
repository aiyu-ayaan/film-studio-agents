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
| `card` | Herk card scenes | Search command in "Herk Edit Kit cards" below; one card id, e.g. `vox-explainer.t1.section.circle` |
| `footage` | OpenMontage footage scenes | Project-relative path of the downloaded clip, e.g. `assets/footage/nasa-iss-earth.mp4` (search: "OpenMontage" adapter below). Must exist: the gate checks it |
| `words` | every speech scene (auto) | The line's word times from `audio/vo/vo.words.json`, minus the scene's `start_s`. Reveals land on the spoken word |

Pick the base engine by film type, not by habit:
- Story, history, myth, spiritual: a Lemo painted style (`ink-wash`, `watercolor`, `impasto`, `ukiyoe`, `shadow-puppet`, `woodcut`, `gilded-illumination`) for most scenes. Motionmaxxing only for the hook and the end card.
- Science, STEM: 3D (HyperFrames Three.js + a 3DViz `record`) for the hero, Lemo `chalkboard`/`blueprint`/`colored-pencil` for diagrams.
- Product, launch, brand: Motionmaxxing + Shotcraft, HyperFrames blueprints for UI beats.
- Documentary, science, history, travel with real places or events: OpenMontage `footage` scenes (graded to style.md) between styled scenes. Real footage beats a drawn stand-in.
- Editorial explainer (news take, deep dive, listicle): Herk `card` scenes for section, stat, quote and list beats.
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

## Herk Edit Kit cards [tested 2026-11-21]

- Find a card (`HERK=~/.local/share/skill-src/herk-edit-kit`): `jq -r '.styles[].cards[] | [.id, .purpose, (.slots | map(if type == "object" then .name else . end) | join(","))] | @tsv' $HERK/style-library/registry.json | grep -i "<purpose>"` (purposes: thesis, stat, section, quote, overview, label, list, equation, definition, lower-third). No preview images ship: after copying a card, look at it with `npx hyperframes snapshot --at 2` in the scene folder.
- Use for editorial beats: section marker, big stat, quote, thesis, list, lower third. 406 cards, 2 styles (`vox-explainer` paper/ink, `kallaway`). One style per film; match style.md to its `DESIGN.md` + `tokens.css`, or edit `tokens.css` to style.md.
- Build: `mkdir -p scenes/<id> && cp $HERK/style-library/<NN-style>/tokens.css scenes/<id>/`, then copy `$HERK/style-library/<the card's registry "file">` (e.g. `01-vox-explainer/cards/tier1/t1-section-circle.html`; `jq -r '.styles[].cards[] | select(.id == "<id>") | .file' $HERK/style-library/registry.json`) to `scenes/<id>/index.html` and change `href="../../tokens.css"` to `href="tokens.css"`. Fill every `data-slot` (placeholders like "SOURCE · INTERNAL RESEARCH 2026" must go; image slots get a real image, e.g. a still of a `footage` clip).
- Required motion fix: a stock card fails `scene_check.py` (tested: 86% frozen; its 6% push is too slow). What passed (34%, no crop): stage push 1.00 > 1.12 with rotation -0.8 > 0.8 deg on `transformOrigin` at the headline, plus parallax drift on two elements (`x: 140, y: -40` and `y: -70, rotate: -1.5`, 5.2 s, `sine.inOut`) and one accent event mid-scene. An 18% push also passes but crops the headline at the end.
- Set the timeline length to the scene: card `duration.min/max` is 5-8 s; for other lengths change the `duration` of the stage tween to `frames / fps`.
- Render: `export HYPERFRAMES_CACHE_DIR=$HOME/.local/share/hyperframes-cache; cd scenes/<id> && npx hyperframes render --fps <fps> --quality delivery --output clip.mp4`. Cards are 1920x1080; for 9:16 masters, re-lay out the card at 1080x1920 (padding is not a delivery).
- Never: AIS brand assets, the names "Vox"/"Kallaway" on screen, placeholder stats.

## OpenMontage footage [tested 2026-11-21]

- Use for real places, space, nature, history (public archives). Runs as a separate process: `bin/om.sh <tool> '<json>'` (absolute paths in the JSON). `bin/om.sh list` = tools usable now.
- Search + download (key-free sources: `nasa`, `wikimedia`, `archive_org`, `openverse`, `loc`):
  `bin/om.sh direct_clip_search '{"output_dir":"<abs project>/build/footage","queries":[{"query":"earth from space"}],"sources":["nasa","wikimedia","archive_org"],"clips_per_query":3,"filters":{"max_duration":120}}'`
  Look at the thumbnails, pick one, copy it to `assets/footage/<name>.mp4`, and write its `source_url` + `license` in `NOTE.md`. Never an NC licence. `duration` reads 0.0 for NASA: use ffprobe.
- Long clip: `bin/om.sh scene_detect '{"input_path":"<abs clip>"}'` gives shot ranges; pick a range with motion.
- Grade to style.md: `bin/om.sh color_grade '{"input_path":"<abs clip>","output_path":"<abs>/scenes/<id>/graded.mp4","profile":"cinematic_cool","intensity":0.7}'` (profiles: `cinematic_warm`, `cinematic_cool`, `moody_dark`, `bright_clean`, `vintage_film`, `high_contrast`, `neutral`; or `lut_path`).
- Conform with a camera move (tested 1280x720 source to 1920x1080, 0% frozen):
  `ffmpeg -ss <in> -t <s> -i scenes/<id>/graded.mp4 -an -vf "scale=w='trunc(<W>*(1+0.08*t/<s>)/2)*2':h=-2:eval=frame,crop=<W>:<H>,fps=<fps>,format=yuv420p" -c:v libx264 -crf 16 -preset veryfast scenes/<id>/clip.mp4`
  The source must be at least the master aspect; for 9:16 first `bin/om.sh auto_reframe '{"input_path":"...","output_path":"...","target_aspect":"9:16"}'`.
- Titles or labels over footage: build a HyperFrames scene with the conformed clip as a `<video>` layer instead.
- Never its TTS, avatar, captions, `video_compose`/`hyperframes_compose` or `video_downloader`.

## Remotion [untested; only when asked]

- Render muted at the master size: `npx remotion render <CompositionId> scenes/<id>/clip.mp4 --muted` with the composition's width/height/fps/durationInFrames set to master values.
- Licence: free for an individual or up to 3 employees.

## Adding a new skill as an adapter

1. Add a section here: when to use, where it builds, exact render command for a silent clip at master w/h/fps and a given length, what audio it produces and how to drop or export it.
2. Run one scene through it, then assemble.py. Change "[untested]" to "[tested <date>]".
3. Follow the rest of "Add a new skill" in the root `CLAUDE.md`.
