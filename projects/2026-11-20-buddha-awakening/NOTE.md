# Production Note: The Prince Who Chose Truth

## Format & Deliverables
- **Clean master**: `renders/final.mp4` (`1440x2560`, 2K 9:16, `30 fps`, `2228 frames`, `74.283 s`)
- **Captioned social cut**: `renders/final.captioned.mp4` (karaoke captions, accent `#D4A34A`)
- **Subtitles**: `renders/final.srt`, `renders/final.captioned.srt`, `renders/final.captioned.ass`
- **Contact sheet**: `renders/contact.png`

## Skills & Engines Used
- Orchestrator: `film-studio` + `film-captions`
- Scenes `s1`, `s8`: `motionmaxxing` (passed `lint.mjs` GATE G5)
- Scenes `s2`–`s7`: `hyperframes` (passed `hyperframes check`, 0 errors)
- Voiceover: **Kokoro-82M** (`bm_george`, Apache-2.0) via `bin/vo.sh` + `narrate.py` (Parakeet word timings)

## Third-Party Assets & Licences
- **Music bed** (`audio/music/bed.wav`): Original ambient singing-bowl & harmonic drone synthesized locally via `build/make_music.py` (CC0).
- **SFX** (`audio/sfx/swish.wav`, `audio/sfx/bell.wav`): Generated via `earshot sfx render` (`swish/soft`, `fit/bell/small_bell`, MIT).
- **Fonts**: Bundled `Georgia`, `DejaVu Sans`, `Inter` (OFL), `EB Garamond` (OFL).

## QA Results (`qa.json` & `earshot critique`)
- `frames`: `2228` / `2228` (`frames_ok: true`)
- `lufs`: `-14.0 LUFS` (`lufs_ok: true`)
- `true_peak`: `-1.5 dBTP` (`peak_ok: true`)
- `earshot critique`: **launch-grade — 23 of 23 scored metrics in range (weighted 100%), 0 critical, 0 major issues** (music presence `93%`, realness `0.88`, stereo width `-7.9 dB`).
- Visual review (`renders/contact.png`): All 8 scenes match `style.md` palette (`#0F0D0B` / `#D4A34A` / `#F2E8D5`), captions stay in bottom safe zone, no dead frames or page chrome.

## Platform Note
- If uploading to YouTube/social, disclose synthetic narration voice (`Kokoro-82M`).
