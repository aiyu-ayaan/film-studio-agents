# Production note: Letting Go (2026-11-20)

| Field | Value |
|---|---|
| Skills | film-studio orchestrator; s1 Lemo-Opuscar (own canvas page, ink-wash palette); s2 HyperFrames; s3 Motionmaxxing; s4 3DViz Pro Max direction + HyperFrames/Three.js 0.181.2; s5 Shotcraft-style 2.5D notes page in HyperFrames (no Shotcraft demo copied); s6 Remotion 4.0.545 |
| Format | 1440x2560, 30 fps, 9:16, 1694 frames (56.47 s) |
| Voice | Kokoro-82M, voice am_michael, via bin/vo.sh / narrate.py. Realistic synthetic voice: disclose on YouTube |
| Captions | film-captions karaoke, accent #F2A33A (`renders/final.captioned.mp4`) |
| Files | `renders/final.mp4` (clean master), `renders/final.captioned.mp4`, `final.srt` |

## Third-party assets

| File | Source | Licence | Credit needed |
|---|---|---|---|
| Salamander Grand Piano V3 (in music bed) | Alexander Holm | CC BY 3.0 | Yes: `Piano: "Salamander Grand Piano V3" by Alexander Holm, licensed under CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/)` |
| VS Chamber Orchestra: Community Edition (strings in bed) | Versilian Studios | CC0 | No |
| Music score and SFX | Original, made with Lemo sampler and Earshot code-made bank | MIT / own | No |
| Cormorant Garamond, Montserrat, Liberation Serif | system / embedded-captions fonts | SIL OFL | No |
| GSAP 3.x, three.js (MIT), HyperFrames (Apache-2.0), Remotion (free <=3 staff) | npm | own terms | No |

Lemo style docs are CC BY-NC; only film output is used.

## Quality gate

| Check | Result |
|---|---|
| `earshot critique` | launch-grade, 0 critical, 0 major (22/23 metrics) |
| Loudness / true peak | -14.1 LUFS / -1.4 dBTP |
| Frames | 1694 = planned |
| Dead frames / page chrome | s3 lint G5 pass, G2 pass; others checked by eye on contact sheet |
| Captions | karaoke, inside frame, sit under on-screen content |

## What I would still improve

- Figures and hands are stylised shapes (s1, s2, s4, s6); s2 lower third is flat dark.
- Cormorant italic missing; titles in s5 use Liberation Serif italic.
- Music not listened to by Claude: user ear check needed.
- assemble.py hung on a never-ending audio filter; fixed with `-t` on the premix command.
