# Herk Edit Kit

| Field | Value |
|---|---|
| Repo | <https://github.com/nateherkai/herk-edit-kit> |
| Upstream / forks | Formerly "HyperFrames Student Kit". Bundles HyperFrames skills from heygen-com/hyperframes (Apache-2.0) |
| Checked | 2026-11-21, commit `10511e5af86f`, ★3,026, last push 2026-10-14 |
| Licence | MIT (`LICENSE`) + "Herk Edit Kit Use Permission" for the pipeline skills, style library and templates: "use them to produce personal or commercial videos" (`licenses/PIPELINE-USE-PERMISSION.txt`). Commercial: yes. AIS brand assets excluded (see Limits) |
| Invoke | Not symlinked as slash commands. Read `$HERK/.claude/skills/<name>/SKILL.md` and run its scripts by absolute path (`HERK=~/.local/share/skill-src/herk-edit-kit`) |
| Engine | HyperFrames + GSAP (cards, templates); Node scripts + ffmpeg (cuts) |
| Needs | Node 22+, ffmpeg, Chrome. No API key for the parts we use |
| Install | `bin/setup-skills.sh herk-edit-kit` (clone to `$HERK`, `npm ci --onnxruntime-node-install-cuda=skip`, `npm test`). Plain `npm ci` fails here: onnxruntime-node tries a CUDA 12 download that 404s |
| Scope | External clone; no skill symlinks (see "Why not symlinked") |

## What it does

Nate Herk's kit for editing your own footage with an agent (README): transcript-driven cuts, storytelling, short-form reels, motion-graphics cards.
15 skills (`.claude/skills/`). 406 draft motion-graphics cards in two styles (`style-library/registry.json`: `vox-explainer` 106, `kallaway` 300), each a standalone HyperFrames composition with named text slots and `tokens.css`.
Two whole-scene templates (`style-templates/`: dark graph paper, left glass popout). Editing playbook (`docs/EDITING-PLAYBOOK.md`), motion vocabulary (`MOTION_PHILOSOPHY.md`).

Skills we use and what for:

| Skill | Use | Tested here |
|---|---|---|
| `style-library` (cards) | Scene source for film-studio: recipe key `card` | Yes, 2026-11-21 (see adapters.md) |
| `cut-silences` | Remove dead air from the user's own recording, from a word-level transcript | Yes, 2026-11-21, on our Parakeet `vo.words.json` (EDL written) |
| `cut-mistakes` | Find stutters, repeats, retakes; review-gated | CLI runs; not run on real footage |
| `edit-video` | Whole long-form edit of the user's talking-head recording | No |
| `short-form-edit` | User's recording to 9:16 reel/Short (hook, payoff, B-roll, SFX) | No |
| `video-storytelling` | One persistent world the camera moves through (stage 2 direction for long films) | Reference only |
| `motion-showreel` | 10-30 s brand reel cut to a 120-130 BPM grid (no-speech) | No |
| `hyperframes-video-beats` | Lower thirds and callouts over a talking head | No |

Not used: `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `gsap` (older copies of the global HyperFrames skills), `make-a-video` (overlaps film-studio), `website-to-hyperframes` (Shotcraft does real UI), `short-form-video` (superseded by `short-form-edit`, per README).

## Why not symlinked

Its SKILL.md files call scripts by repo-relative path (`node scripts/transcribe-elevenlabs.mjs`, `style-library/registry.json`) and keep projects in `video-projects/`. Symlinked into this repo those paths break.
Four of its skills share names with our newer global HyperFrames skills and would shadow them. So we run its scripts by absolute path and keep our projects in `projects/`.

## Use it for

- Editing footage the user recorded: silence and mistake cuts, long-form edit, reels.
- Editorial explainer cards (section, stat, quote, list, lower third) in a film-studio scene.
- Story direction for long films: persistent world, camera grammar, spotlight rule (`video-storytelling`).

## Do not use it for

- Captions: `short-form-edit` and `edit-video` add captions. Ours come only from `/film-captions`.
- Voice: its `npx hyperframes tts` path is excluded. Use `bin/vo.sh`.
- Transcription: `scripts/transcribe-elevenlabs.mjs` uploads audio to ElevenLabs. Use `npx hyperframes transcribe` (local Parakeet), then wrap: `jq '{words: .}' x.words.json > x.json`. Its scripts accept `{ words: [{ text, start, end }] }`.
- Generated media: `motion-showreel/scripts/kie.mjs` (Kie.ai) is paid. Ask the user first.

## Voice hook

No built-in voice in the cut skills: they edit the user's own recorded voice. `make-a-video` and `website-to-hyperframes` offer `npx hyperframes tts` (Kokoro via HyperFrames); we do not use those skills. For narration use `bin/vo.sh`.

## Output

Cut scripts: `<stem>.silence-edl.json`, `<stem>.silence-transcript.json` (re-timed words), `<stem>.silence-decisions.md`, an ffmpeg filter script; `--apply` renders the cut video. Cards: HTML you copy into `scenes/<id>/`, rendered with HyperFrames.

## Limits and risks

- AIS (AI Automation Society) logo, brand guideline, brand tokens and several example projects are "not licensed for reuse" (`LICENSE`). Never use them.
- Card names, handles, statistics and source labels are placeholders (`THIRD_PARTY_NOTICES.md`). Replace every slot.
- "Vox", "Kallaway", "Infinite" are aesthetic reference names, not endorsements. Never name them in a video or a client deliverable.
- Cards load GSAP and Google Fonts from CDNs. HyperFrames renders them fine online; localise fonts for offline renders.
- Cards alone are too still for our gate: the stock card measured 86% frozen in `scene_check.py`. See adapters.md for the fix.

## Our take

Opinion: the cards are the main win for film-studio. They give 406 ready editorial layouts with tokens, so explainer beats stop being hand-drawn. The cut skills add a job we had no tool for: editing footage the user films.
