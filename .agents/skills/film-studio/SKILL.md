---
name: film-studio
description: Produce one finished, narrated film by combining several video skills (HyperFrames, Shotcraft, Motionmaxxing, Lemo-Opuscar, 3DViz, Herk Edit Kit cards, OpenMontage stock footage, Remotion) scene by scene, with a written narration script, local human-sounding voiceover, music bed, SFX, captions and a loudness-checked mix. Default is storytelling with speech. Use for "make a video/film/explainer/promo/story about X" in the Movies studio. For music-only films use film-studio-nospeech.
argument-hint: "[topic, brief or path to BRIEF.md]"
---

# film-studio: many skills, one film, with voice

You are the director. Each video skill builds some scenes. You own the story, the voice, the timing, the sound and the final cut.
The video skills make picture only (some add music); none of them writes and voices a story. That is this skill's job.

Paths below are relative to the repo root (the folder holding `CLAUDE.md`). Scripts: `.claude/skills/film-studio/scripts/`.
Read before starting: `references/plan.md` (plan.json, the single source of truth). Read the others at their stage.

## Modes

| Mode | Invoke | Story carried by | Timing from |
|---|---|---|---|
| Speech (default) | `/film-studio` | narration + picture | the voice (`narrate.py`) |
| No speech | `/film-studio-nospeech` | on-screen text + picture + music | the music's beats (`timing.py`) |

## Stages and gates

Pass each gate before the next stage. Two user gates only: G1 (story + storyboard) and the voice choice in stage 3 if not yet made.

### 0. Setup
- `bin/new-project.sh <slug>`; work inside that folder. Fill `BRIEF.md` from the user's ask: goal, audience, platform, length, aspect, deadline, price.
- Master format: 1920x1080 at 30 fps unless the platform needs 1080x1920 (Shorts/Reels/TikTok) or 1080x1080.
- Check which skills are installed (`ls ~/.claude/skills ~/.local/share/skill-src`, `claude plugin list`). Only plan scenes for installed skills. HyperFrames is always available.
- Gate: `BRIEF.md` filled, master format decided.

### 1. Story and script (speech)
- Shape: hook (first 3 s) > problem or question > turn > proof or journey > payoff > call to action. For pure storytelling: setup > rising tension > turn > resolution.
- Write every narration line as speech. Follow "Make any TTS sound human" in `research/tts.md`: contractions, short sentences, fillers where a person pauses, punctuation for timing, numbers spelled out.
- Pace: about 2.5 words per second. 60 s film = about 140 words. One line = one beat = 1-3 sentences.
- Put lines in `plan.json` `lines[]` and a readable copy in `script.md`.
- Own-channel Reels/Shorts: follow `channel/format.md` (word budget, pauses, 3-6 s scenes, safe zones, caption sync).
- Framing (intro, chapter bridges, outro): when the user asks for it, apply `.agents/skills/film-framing/SKILL.md` at stages 1, 2 and 5 and pass its `framing_check.py` before G1. For a film with 3+ topic sections or over 3 minutes, offer it once at G1.
- Gate G1 (with stage 2): show the user the script and the storyboard together. Wait for approval.

### 2. Storyboard and style bible
- Split the lines into scenes (`scenes[]`, each owns 1+ consecutive `line_ids`). Usually 4-8 s per scene.
- Pick the skill per scene with the router in the root `CLAUDE.md` and `references/adapters.md`. Use a different skill only where its technique is clearly better (real UI: Shotcraft; idea or kinetic type: Motionmaxxing; painted or documentary look: Lemo; 3D: HyperFrames + Three.js with 3DViz recipes; real places and events: OpenMontage footage; editorial section, stat, quote or list beats: Herk cards).
- Write `style.md`: one palette (hex), two fonts, type scale, grain, safe zones (keep on-screen text out of the bottom 20% when captions are on), caption style + accent. Every scene uses it. One look per film; skills vary technique, not identity.
- Fill `scenes[].recipe` for every scene: follow "Recipe" in `references/adapters.md` (base engine by film type, blueprint, registry blocks, camera move, precedent, shot card, Lemo style, 3DViz record). Run the searches; do not invent ids.
- Write `STORYBOARD.md`: per scene, what is on screen, the line it carries, skill, recipe, transition (default: hard cut on motion).
- Gate: `python3 .claude/skills/film-studio/scripts/scene_check.py <project> --recipes-only` exits 0; style.md exists; user approved (G1).

### 3. Voice and timing (locks scene lengths)
- Voice is Kokoro or Pocket TTS only, through narrate.py. Never use a skill's or library's built-in voice (HeyGen, ElevenLabs, Lemo's TTS, Motionmaxxing `voice.py`, OpenMontage TTS, Herk `hyperframes tts`, ...).
- `plan.master.voice_engine` (`kokoro` or `pocket`): if empty, ask the user once which they chose after the ear test (`research/tts-audition/`). Never default silently.
- Run `python3 .claude/skills/film-studio/scripts/narrate.py <project>`. It voices each line, joins them with gaps, transcribes the result, checks every line against the script, and writes frame-exact scene lengths into plan.json.
- Exit 3 = a line was misread. Rewrite that line's text (spelling, punctuation) and rerun with `--only <id>`. Kokoro gives the same take for the same text, so change the text or the voice, not just retry.
- After any script change, rerun narrate.py. Scene frame counts from before are invalid.
- Gate: narrate.py exit 0; every scene has `frames`.

### 4. Scenes (picture)
- For each scene, follow its adapter in `references/adapters.md`. Every clip: master width/height/fps, at least `frames` long, saved to `scenes/<id>/clip.mp4`. Audio in clips is ignored.
- Parallel work: send one standalone packet per scene to a subagent (foreground, in one message, so they keep Bash). Packet = scene brief, its narration text with `words` times (scene-relative), `style.md` content, w/h/fps, exact `frames`, output path, the adapter section, the `recipe`, "picture only", and the line `export HYPERFRAMES_CACHE_DIR=$HOME/.local/share/hyperframes-cache` (subagents do not inherit your shell).
- Token budget: the packet lists the exact files to read (the recipe's blueprint file, registry items, shot-card folder, one Lemo `STYLE.md`, `hyperframes-core/SKILL.md` for HyperFrames). The subagent reads only those, never a whole skill folder or a 40 KB+ reference end to end. Group scenes that share an engine into one subagent (one Lemo agent for all Lemo scenes) so each skill is read once per film.
- Render at most 2 scenes at a time: each render runs Chrome on this 8-core PC.
- Speed: render fixes and look checks at draft (`--quality draft`, no `--shutter`/`--grain`); render each scene at delivery once, after its stills pass. Re-render only scenes whose source changed.
- Check each clip: `python3 .claude/skills/film-studio/scripts/scene_check.py <project> --only <id>` (size, fps, length, recipe, frozen time <= 40%). Then 3 stills (start, middle, end) by eye against style.md. A failed scene goes back to its subagent with the printed reason.
- Gate: `scene_check.py <project>` exits 0 for all scenes.

### 5. Music and SFX
- Follow `references/audio.md`: the music ladder (licence first), SFX on cuts, optional per-scene SFX stems.
- Gate: `plan.music` has path + licence + credit, or the user agreed to no music.

### 6. Assemble
- `python3 .claude/skills/film-studio/scripts/assemble.py <project>`: conforms clips, cuts to exact frames, mixes voice + ducked music + SFX, normalises to -14 LUFS / -1.5 dBTP, writes the clean master `renders/final.mp4`, `final.srt`, `qa.json`. It never burns captions.
- Gate: exit 0 (frames, loudness and peak checks pass).

### 6b. Captions (speech mode)
- Invoke the `film-captions` skill. It is the only step that adds captions: `python3 .claude/skills/film-captions/scripts/captions.py renders/final.mp4 renders/final.mp4 --words audio/vo/vo.words.json --style <master.captions> --accent <style.md accent>` (add `--srt` for YouTube). In place: `renders/final.mp4` becomes the one captioned film; the clean master moves to `renders/.clean/`. After re-assembling, run it again: assemble writes a new clean `final.mp4`.
- `master.captions`: `clean` (YouTube, client), `karaoke` (story, social), `box`, `punch` (Shorts hook), or `none`. Placement is content aware by default (`--position auto`).
- Captions are the only words that repeat the narration. Scenes never paint subtitle lines or the spoken sentence; on-screen text is titles, labels, numbers and kinetic-type hits only. Otherwise the film shows the words twice.
- Gate: 3 caption frames checked (inside frame, not over on-screen text, words right).

### 7. Review
- Contact sheet: `ffmpeg -i renders/final.mp4 -vf "fps=1,scale=480:-1,tile=6x5" -frames:v 1 renders/contact.png`; look at it. Fix: dead frames, page chrome (corner labels, counters), unreadable text, a scene that breaks style.md.
- Required: `earshot critique renders/final.mp4` (fix "major" items) and Motionmaxxing `lint.mjs` on every HTML scene's `index.html` (page chrome). Dead frames are already gated by `scene_check.py`.
- Gate: the user has seen the film. Iterate: change a scene > re-render that clip > rerun assemble.py (narration is reused).

### 8. Deliver
- Fill `NOTE.md`: skills + commits, voice engine, every third-party asset with licence (each OpenMontage clip: source URL + licence; CC BY credit lines), music credit (Lemo `credits()` lines, Kyutai for Pocket TTS), qa.json numbers.
- Other aspects: re-render scenes at the new size (padding is a fallback, not a delivery).
- YouTube: disclose realistic synthetic voice; vary style per video (`research/monetization.md`).

### 9. Cleanup (always, after the user accepts the film)
- `bin/clean.sh <project>` (`-n` first to see the list). Deletes rebuildable bulk: `build/`, `renders/.clean/`, draft renders, scene clips/frames/caches, `node_modules`, vendored runtimes; then `git gc`. Keeps sources, `audio/` and `renders/final.mp4` + `.srt` + `qa.json`.
- Re-editing later: re-render the scene clips first (`scene_check.py` lists the missing ones), then rerun assemble.py.

## Gates and handoff (any agent, needed by the Studio app)

The Studio app (`studio/`) runs this skill headless with Claude Code, Codex, Antigravity or another agent, and lets the user switch agent mid-film. Two files in `<project>/.studio/` make that work. Write them whatever tool you are.
- `handoff.md`: overwrite after every stage gate passes and before you stop for any reason. At most 30 lines: stage reached, what is done (files), decisions made (voice engine and voice, captions style, approvals given), next step, open problems. Another agent starts from this note, so write facts, not plans you have not checked.
- `gate.json`: at a user gate (G1, voice choice, review sign-off, or any question only the user can answer), write `{"gate": "G1", "question": "<one sentence>", "files": ["script.md", "STORYBOARD.md"], "options": ["Approve", "<other choice>"]}` (`files` relative to the project, `options` optional), update `handoff.md`, then end your turn without waiting. The user's answer arrives as the next message. When you have it, delete `gate.json` (the app also deletes it).
- Taking over from another agent: read `handoff.md` and the end of `.studio/run.log`, check the files on disk, then continue from the first stage whose gate does not pass. Never redo a stage that passes.

## Quality bar (best possible picture)

Apply on every scene, whatever the skill. Taken from Motionmaxxing's measured findings and Shotcraft/HyperFrames practice.
- Never hand-build what a skill already ships: the recipe names the blueprint, registry blocks, shot card, style or 3D record. Hand-drawn flat SVG figures as a hero are the main reason past films looked cheap.
- Camera always moving (push, orbit, parallax, pan between stations); a new visual event at least every 2 s, landing on the spoken word.
- Motion: median move about 10 frames; landings ease out, exits ease in; overshoot rare and late; things arrive from larger or from the edge, never grow from zero; move by transform, not opacity fades.
- No dead frames: something moves on almost every frame; no run of more than 3 still frames.
- Cut on motion with hard cuts; no fade-to-black between scenes; end hold 0.6-1.4 s.
- One hero per frame. No page chrome (corner labels, counters, timecodes, progress bars, kicker over a headline).
- A ground is a surface: light, depth, grain or texture, not a flat swatch. Hero moment gets the most work (3D, real UI capture, dense composition).
- Text: at least 4% of frame height for UI/proof text; readable at phone size.
- Render quality: HyperFrames `--quality delivery`; Motionmaxxing `--shutter 180` on fast hero moves and `--grain 0.03` on gradients/3D. The film is encoded 3 times (scene, assemble, captions), so the assembled master uses `crf` 12 and captions `--crf 16`.
- Review twice: stills of every scene before assembling, contact sheet after. Fix the worst thing first, then re-check.

## Rules
- Never use MusicGen-small or any CC-BY-NC model or asset in paid work (`references/audio.md`).
- Voices: Kokoro or Pocket TTS via `bin/vo.sh` only. Never clone a voice without the person's consent. Never put a third-party brand in a film without rights.
- Scripts are the only place timing math happens. Do not hand-edit `start_f` / `frames`.
- If a skill in the plan is not installed, swap the scene to HyperFrames and tell the user.
