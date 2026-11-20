# research/: facts behind the studio

Researched 2026-11-20. Sources: each repo cloned at the commit named in its card, plus the web pages listed in each file.
The skill registry (job to skill) lives only in `../CLAUDE.md`. This folder holds the evidence.

## Files

| File | What it answers |
|---|---|
| `skills/_TEMPLATE.md` | Blank card. Copy it to add a skill. |
| `skills/hyperframes.md` | HeyGen HyperFrames: the base engine, already installed. |
| `skills/remotion.md` | Remotion: React video, licence limits. |
| `skills/shotcraft.md` | video-shotcraft / hyper-videocraft: product promos from shot recipe cards. |
| `skills/motionmaxxing.md` | Motionmaxxing: measured motion design, gates G0-G5. |
| `skills/3dviz-pro-max.md` | 3DViz Pro Max: Three.js 3D scenes. |
| `skills/earshot.md` | Earshot: listen, critique, and make SFX in code. |
| `skills/lemo-opuscar.md` | Lemo-Opuscar: 99 film styles in code. |
| `tts.md` | Voice decision (Kokoro + Pocket only), benchmarks, rules for a human-sounding voice. |
| `tts-audition/` | Same line rendered per engine, to judge by ear. |
| `licenses.md` | One table: can I sell what this makes? Action items. |
| `monetization.md` | How to earn with this stack. Offers, prices, platform rules. |
| `orchestration.md` | How film-studio combines the skills into one film; what is tested. |

## Summary in 8 lines

1. HyperFrames (Apache-2.0, ★87k) is the base. Shotcraft (fork) and Motionmaxxing render through it or plain HTML.
2. Best money skills: Shotcraft and Motionmaxxing for SaaS launch/promo films. Lemo-Opuscar for styled narrated explainers. 3DViz for 3D hero shots.
3. Earshot is the only skill that lets Claude "hear". Use it as the audio QA gate on every film.
4. Remotion is free for you as an individual or a company of up to 3 employees. You cannot sell a modified Remotion.
5. Voice: only Kokoro-82M (Apache-2.0) and Pocket TTS (clones your voice, credit Kyutai), via `bin/vo.sh`. Built-in voices of all skills/libraries are excluded (user decision 2026-11-20). Default of the two pending the ear test in `tts-audition/`.
6. KittenTTS 2 and VoiceStudio were researched (`tts.md`) but are excluded.
7. `windyinwind/hyper-videocraft` is a 1-commit HyperFrames port of `Vincentwei1021/video-shotcraft` (★21.7k, Remotion). Its sibling `video-talkcraft` is noncommercial: avoid.
8. YouTube (July 2026) demonetizes generic, repetitive, template content. Client work is the safer first income.

## How to refresh

- Repo facts: `gh api repos/<owner>/<repo> --jq '.stargazers_count, .pushed_at, .license.spdx_id'`, then read the changelog since the pinned commit.
- Shallow-clone to a temp folder to read. Never run scripts from that clone. Install with each card's official command.
- Update the card's "Checked" date and commit. If the licence changed, update `licenses.md` and the registry row in `../CLAUDE.md`.
- TTS moves fast. Re-check `tts.md` every 2-3 months.

## Card rules

- Every claim names its source: a repo file path or a URL.
- Separate what the repo says from our judgment. Mark judgment "Our take".
- Numbers are copied exactly. If sources disagree, write both.
