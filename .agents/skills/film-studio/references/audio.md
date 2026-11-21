# Audio: voice, music, SFX, mix

## Voice (speech mode)

- Engines: Kokoro or Pocket TTS only (`bin/vo.sh`); every skill's built-in voice is excluded. Humanising rules: `research/tts.md`. narrate.py calls `bin/vo.sh <engine>` once per line.
- Per line: trimmed of engine silence, resampled to 48 kHz mono. Gaps are ours (`gap_s`, `pause_after_s`), so pacing is controllable.
- Pause after a question or a big claim: `pause_after_s` 0.6-0.9. Before the call to action: 0.5.
- The joined track is transcribed once (Parakeet via `npx hyperframes transcribe`) for word timings, captions and the script check.

## Music: licence ladder (paid work)

Take the first that fits:

| # | Source | Licence | Notes |
|---|---|---|---|
| 1 | Track the user or client supplies or licenses | Theirs | Log in `assets/LEDGER.md` / NOTE.md |
| 2 | Lemo-Opuscar sampler score (`core/audio/sampler.py`) | Samples CC0, except Salamander piano (CC BY 3.0) and MuldjordKit drums (CC BY 4.0) | Original score made in code. `S.credits([...])` prints the credit lines. Needs Lemo installed |
| 3 | HeyGen music catalog (`/media-use`, after `heygen auth login`) | HeyGen terms: read them before paid use | Free-usage path, needs sign-in |
| 4 | Mixkit tracks bundled with Shotcraft (`cat-walk`, `house-vibez`, ...) | Mixkit free licence: verify on mixkit.co before paid use | `bgm-tech-house.mp3` source unknown: never |

Never: MusicGen-small (`facebook/musicgen-small`, CC-BY-NC 4.0), the offline fallback of `/media-use` and faceless-explainer's `audio.mjs`. So do not let those scripts make the music.
Not for paid work: OpenMontage `pixabay_music` (scrapes Pixabay; Content ID claims on YouTube) and `freesound_music` (mixes CC-BY-NC with CC0/CC-BY). Its music generators are paid APIs: ask first.
Later (needs a bigger GPU): ACE-Step v1 3.5B (Apache-2.0).
Today (2026-11-20) Lemo is not installed: music means #1 until it is.

Music fit:
- Speech: bed at `music.gain_db` -8 dB; the assembler ducks it further under the voice (sidechain). Start the hit of the music near the hook.
- No speech: music near full level (-1 dB); cuts snap to beats (`timing.py`).
- Length: the assembler loops the file and fades the last 2 s. Prefer a track at least as long as the film.

## SFX

- Sources, in order: Earshot bank (`earshot sfx render <id> -o x.wav --dur ...`, code-made, MIT), Earshot `kit` with the `launch` preset, Mixkit-sourced Shotcraft SFX with a URL in its ATTRIBUTION.md.
- Place: whoosh peak just after a cut, taps slightly before the action (Earshot `kit` measures this). 3-5 sound kinds reused, not a new sound per event.
- In plan.json: `sfx[]` with absolute film time `t`, or per scene `sfx_stem`.

## Mix (assemble.py)

voice (stereo) + music (gain, sidechain-ducked by the voice) + SFX (adelay) > amix > two-pass loudnorm to `lufs` (-14) / `true_peak` (-1.5) > AAC 256k.
QA in `renders/qa.json`: integrated LUFS within 1 LU of target, true peak <= -1.0 dBTP, frame count equals plan.
