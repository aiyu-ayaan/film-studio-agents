# Production Note: Newton's Three Laws of Motion (Class 10)

## Format & Deliverables
- **Clean master**: `renders/final.mp4` (`1440x2560`, 2K 9:16, `30 fps`, `2875 frames`, `95.833 s`)
- **Captioned social cut**: `renders/final.captioned.mp4` (`clean` style captions, accent `#38BDF8`)
- **Subtitles**: `renders/final.srt`, `renders/final.captioned.srt`, `renders/final.captioned.ass`
- **Contact sheet**: `renders/contact.png`

## Skills & Engines Used
- Orchestrator: `film-studio` + `film-captions`
- Scenes `s1`, `s6`: `motionmaxxing` (passed `lint.mjs` `GATE G5: PASS`)
- Scenes `s2`–`s5`: `hyperframes` (passed `hyperframes check` with `0` errors)
- Voiceover: **Kokoro-82M** (`am_michael`, Apache-2.0) via `bin/vo.sh` + `narrate.py` (Parakeet word timings)

## Third-Party Assets & Licences
- **Music bed** (`audio/music/bed.wav`): Original ambient science pad & marimba pulse synthesized locally via `build/make_music.py` (CC0).
- **SFX** (`audio/sfx/drop.wav`, `swish.wav`, `pop.wav`, `chime.wav`): Generated via `earshot sfx render` (`cut_hit/punch`, `swish/soft`, `ui_pop/soft`, `fit/bell/small_bell`, MIT).
- **Fonts**: Bundled `DejaVu Sans`, `Georgia`, `Inter` (OFL), `EB Garamond` (OFL), `Montserrat` (OFL via `film-captions`).

## QA Results (`qa.json` & `earshot critique`)
- `frames`: `2875` / `2875` (`frames_ok: true`)
- `lufs`: `-14.0 LUFS` (`lufs_ok: true`)
- `true_peak`: `-1.3 dBTP` (`peak_ok: true`)
- `earshot critique`: **launch-grade — 22 of 23 scored metrics in range (weighted 97%), 0 critical, 0 major issues** (1 minor: low sub 20–60 Hz share `-31.0 dB`; music presence `95%`, onset sync `100%`, realness `p_real 0.90`).
- Visual review (`renders/contact.png` & `renders/check/cap1.png`–`cap3.png`): All 6 scenes follow `style.md` (`#0B101B` slate blueprint grid, `#38BDF8`/`#F59E0B`/`#34D399`/`#FB7185` vector color coding); proper FBDs (`mg`, `F_N`, `F_app`, `f`, `F_AB`, `F_BA`), step-by-step Class-10 derivations (`ΣF = 0`, `p = mv` → `F = ma`, `F_AB = -F_BA`), and captions stay cleanly in the bottom 22% safe zone without overlapping diagrams.

## Platform Note
- If uploading to YouTube/social, disclose synthetic narration voice (`Kokoro-82M`).
