---
name: film-outro
description: The channel's 2 s outro ("Follow Renderstand, daily reels.") - built ONCE and cached, then appended to the end of any reel. Use when the user says "add the outro", "add extro", "end card", "follow card", or when plan.json master.outro is true. Never rebuild it unless the user asks for a new outro.
argument-hint: "[film.mp4]"
---

# film-outro

One outro for the whole channel. It is made once and reused, so adding it to a reel costs one command and almost no tokens.
Script: `.agents/skills/film-outro/scripts/outro.py` (paths from the repo root).

## Steps (when the user asks to add the outro)

1. `python3 .agents/skills/film-outro/scripts/outro.py status`
   - Prints `cached: ...` (exit 0): go to step 2. Do not read or rebuild anything.
   - Prints `no outro yet` (exit 1): run `outro.py make` once (about 20 s). It voices the line with Kokoro, renders the brand composition, mixes the render blip and writes `assets/brand/renderstand/outro/outro.mp4`.
2. `python3 .agents/skills/film-outro/scripts/outro.py append <project>/renders/final.mp4`
   - In place: the film without the outro is kept in `renders/.pre-outro/`. A film that already has the outro is refused.
   - Run it last, after `film-captions` (the outro's words are already on screen, in sync with its voice, so it gets no captions).
   - After re-captioning or re-assembling a film, run `append` again: those steps write a new `final.mp4` without the outro.

## What the outro is

- 1080x1920, 30 fps, about 2 s, -14 LUFS, true peak under -1.5 dBTP. Look: `assets/brand/renderstand/DESIGN.md` (ink, cream, signal orange; squares fly in from the edges and become the R mark, the two orange steps land with the render blip).
- Voice: Kokoro `am_michael` at speed 1.25 (Kokoro's own speed setting, prosody kept) through `bin/vo.sh` (`VO_SPEED`). Line: "Follow Renderstand, daily reels." Each word appears on screen as it is spoken, in signal orange.
- Files in `assets/brand/renderstand/outro/`: `outro.mp4` (the deliverable), `outro.json` (config, length, loudness, word times), `src/` (composition), `vo.wav`.
- A new outro only when the user asks: `outro.py make --force [--text "..."] [--voice ID] [--speed 1.25] [--seconds 2]`. The new config is saved in `outro.json`.

## Rules

- Never rebuild a cached outro on your own. `make` without `--force` is a no-op when it exists.
- Only appends to a film of the same size and fps (reels: 1080x1920 at 30). Other sizes are refused.
- The outro ends the video, so a reel with it no longer loops back to frame 0. Ask before adding it to a series reel whose ending is a sting into the next episode.
- Self-test: `python3 .agents/skills/film-outro/scripts/outro.py --selftest`.
