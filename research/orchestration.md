# Orchestration: many skills, one film

Researched 2026-11-20. Basis for `.claude/skills/film-studio`, `film-studio-nospeech`, `film-captions`.

## The gap the orchestrator fills

| Skill | Picture | Music | Narration (spoken story) | Captions |
|---|---|---|---|---|
| HyperFrames (single scene) | Yes | via `/media-use` | `npx hyperframes tts` (Kokoro), not a story | `embedded-captions` (talking head only) |
| HyperFrames `faceless-explainer` | Yes | HeyGen catalog, else Lyria/MusicGen | Yes (HeyGen, else Kokoro) | Yes |
| Shotcraft | Yes | 5 bundled BGM | No | Its own caption components |
| Motionmaxxing | Yes | ElevenLabs only | ElevenLabs only (key needed) | Speech uncaptioned by design |
| Lemo-Opuscar | Yes | Sampler score | Kokoro / edge-tts | `.srt` |
| 3DViz | Interactive scene, stills only | No | No | No |
| Herk Edit Kit (2026-11-21) | 406 HyperFrames cards; edits the user's own footage | Its own picks | `npx hyperframes tts`; ElevenLabs transcription | `short-form-edit` adds its own |
| OpenMontage (2026-11-21) | Stock footage, grade, reframe (+ paid generators) | Pixabay scrape, Freesound, paid generators | `tts_selector` (cloud TTS, Piper) | `subtitle_gen`, `remotion_caption_burn` |

No skill combines other skills, and most add no spoken story. Built-in voices in this table are excluded by user decision (2026-11-20): only Kokoro and Pocket via `bin/vo.sh`. So film-studio owns script, voice, timing, music, mix and captions; each video skill only makes silent picture for some scenes.

## Design decisions (ours) and why

| Decision | Why | Evidence |
|---|---|---|
| Voice first, scene lengths from the voice | Picture cut to the voice reads as edited; voice stretched to picture reads as TTS | Motionmaxxing `references/sound-sync.md` "Script, VO, word timings, then picture on those frames" |
| Every skill outputs a silent clip; one ffmpeg assembler | Skills use different runtimes (HyperFrames, Motionmaxxing `render.mjs`, Lemo `video.mjs`, Remotion); all can render a silent MP4 at a set size, fps and length | `render.mjs --fps --width --height --duration`; Lemo `video.mjs --fps --size`; `npx hyperframes render --fps`; Remotion `--muted` |
| Frame-exact cuts from absolute times | Summing rounded clip lengths drifts | Self-test: cuts land on the planned frame |
| 3D via HyperFrames Three.js adapter + 3DViz recipes | 3DViz `capture.py` writes PNG stills, not video | 3DViz `skills/3dviz-pro-max/scripts/`, README "Frames, not assurances"; `hyperframes-animation` `adapters/three.md` |
| Music not from `/media-use` offline fallback | Its fallback is MusicGen-small | HF `facebook/musicgen-small` licence `cc-by-nc-4.0`; `media-use/audio/references/bgm.md` |
| Music ladder: user track > Lemo sampler > HeyGen catalog > Mixkit | Licence clarity | Lemo `core/audio/INSTRUMENTS.md` §4: VSCO 2 CE, VCSL, FreePats, Karoryfer CC0; Salamander piano CC BY 3.0; MuldjordKit CC BY 4.0 |
| Captions as their own skill, not `embedded-captions` | `embedded-captions` is for "single-subject talking-head video" and says "split multi-shot footage before applying it" | `~/.claude/skills/embedded-captions/SKILL.md` description |
| Captions via ASS/libass | Deterministic, fast, word-level karaoke (`\k`), pop/fade transforms, any font | ffmpeg 7.0.2 static has `ass` and `subtitles` filters |
| Mix: sidechain ducking + two-pass loudnorm | Voice clear over music; platform loudness | ffmpeg `sidechaincompress`, `loudnorm`; self-test -14.0 LUFS / -1.5 dBTP |
| No-speech cuts snap to beats | Music-led films cut on the grid | `npx hyperframes beats` (v0.9.72); Motionmaxxing "one beat unit g, every cut on a multiple of g" |
| Two skills: `film-studio` + `film-studio-nospeech` (lowercase) | Skill names: the open Agent Skills spec wants lowercase; uppercase untested in Claude Code | Claude Code skills docs (code.claude.com/docs/en/skills) |
| No-speech skill points to the main SKILL.md by absolute path | Relative cross-skill references are not documented | same docs |
| Scene work in foreground parallel subagents, renders 2 at a time | Background subagents lose most built-in tools; each render runs Chrome | code.claude.com/docs/en/sub-agents |

## Claude Code facts used (from docs, 2026-11-20)

- Frontmatter: `name`, `description` (+`when_to_use`, 1,536 chars combined in the listing), `argument-hint`, `arguments`, `allowed-tools`, `model`, `effort`, `disable-model-invocation`, `user-invocable`, `context: fork`, `agent`, `paths`, `hooks`.
- `$ARGUMENTS`, `$0`... for arguments. `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}` in commands.
- Personal skills beat project skills of the same name: no `film-*` names exist in `~/.claude/skills`.
- Keep SKILL.md under 500 lines; details in referenced files.
- Subagents: up to 20 concurrent by default; can use the Skill tool; start without the parent's context, so packets must stand alone.

## Tested vs untested (2026-11-20)

| Part | Status |
|---|---|
| narrate.py, timing.py, assemble.py, captions.py | Tested by `selftest.sh` with fake clips of mixed size/fps/length, a Kokoro voice, generated music |
| HyperFrames scene render | Tested: real 2.4 s GSAP scene rendered (`--quality delivery`), assembled, captioned; frame count exact |
| Shotcraft, Motionmaxxing, Lemo, 3DViz, Remotion adapters | Untested: those skills are not installed |
| Herk card + OpenMontage footage adapters | Tested 2026-11-21: one card scene and one NASA footage scene passed `scene_check.py` (34% / 0% frozen) and `assemble.py` (330/330 frames) |
| Pocket TTS through narrate.py | `vo.sh pocket` tested alone; not inside narrate.py |
