# Production note

| Field | Value |
|---|---|
| Skill + commit | `film-studio` (project) + Motionmaxxing, HyperFrames, Shotcraft, Lemo-Opuscar (`f9e204293930`), 3DViz Pro Max + Three.js, Remotion (`4.0.545`), Earshot, `film-captions` |
| Engine | Multi-skill per scene -> ffmpeg assembly (`1440x2560`, 30 fps, CRF 12 master / CRF 16 captioned) |
| Voice engine + voice + seed | Pocket TTS (`bin/vo.sh pocket`), local CPU |
| Render command | `python3 .claude/skills/film-studio/scripts/assemble.py projects/2026-11-20-studio-launch` + `captions.py --style karaoke --accent FFB547 --crf 16` |

## Third-party assets

Every file not made in this project. No source, no use in paid work.

| File | Source URL | Licence | Credit needed |
|---|---|---|---|
| `audio/vo/vo.wav` (Pocket TTS) | https://github.com/kyutai-labs/pocket-tts | CC BY 4.0 (weights) | Voice synthesis: Kyutai Pocket TTS (CC BY 4.0) |
| `audio/music/bed.wav` (Lemo sampler) | https://github.com/sgossner/VSCO-2-CE | CC0 1.0 | Samples (CC0): VS Chamber Orchestra: Community Edition (Versilian Studios) |
| `audio/sfx/*.wav` (Earshot bank) | Local procedural (`earshot sfx render`) | MIT | None |
| `Montserrat`, `FiraCode Nerd Font` | System OFL fonts | SIL OFL 1.1 | None |

## Quality gate

| Check | Result |
|---|---|
| `earshot critique` verdict | **launch-grade** (21/23 metrics in range, 95% weighted, 0 critical, 0 major, `p_real=0.91`) |
| Integrated loudness (LUFS) / true peak (dBTP) | `-14.0 LUFS` / `-1.4 dBTP` |
| Dead frames / page chrome (G2, G5) | Contact sheet `renders/contact.png` checked; zero dead frames, zero unintended chrome |
| Captions checked | Checked 3 stills (`karaoke`, `#FFB547`); inside bottom 22% safe zone, zero overlap |

## What I would still improve

- Add subtle stereo width / sub-drop layer to address the 2 minor `earshot critique` notes (side vs mid `-22.2 dB`, sub 20-60 Hz `-23.5 dB`).
