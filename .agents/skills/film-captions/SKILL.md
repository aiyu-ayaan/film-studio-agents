---
name: film-captions
description: Add styled, word-timed captions to any video, and do nothing else (picture and sound are untouched). Four styles - clean, karaoke (spoken word lights up), box, punch (1-3 big words for Shorts/Reels). Uses existing word timings or transcribes locally. Use for "add captions/subtitles to this video", and as the caption stage of film-studio. Not for talking-head embed effects (use embedded-captions).
argument-hint: "[video path] [style]"
---

# film-captions

The only skill in this studio that puts captions on a video. Script: `.claude/skills/film-captions/scripts/captions.py` (paths from `/media/aiyu/550E85595197DBEC/Personal/Movies`).

## Steps

1. Input video. Word timings: from film-studio use `<project>/audio/vo/vo.words.json`. Otherwise omit `--words` and the script transcribes with Parakeet (local).
2. Pick the style for the platform (ask only if the user cares):

| Style | Use for | Look |
|---|---|---|
| `clean` (default) | YouTube explainers, docs, client promos | 1-2 lines, white Montserrat Bold, soft outline, bottom |
| `karaoke` | Story videos, social | One line, the spoken word turns accent colour, slight pop-in |
| `box` | Busy or bright backgrounds | White text on a translucent dark box |
| `punch` | Shorts/Reels/TikTok hooks | 1-3 words, Montserrat Black, uppercase, centred, pop-in |

3. Run:
```bash
python3 .claude/skills/film-captions/scripts/captions.py IN.mp4 OUT.mp4 --words vo.words.json --style karaoke --accent FFD400
```
Options: `--font` (any installed family; default Montserrat, OFL licence), `--position auto|bottom|middle|top` (default `auto`), `--accent` hex (use the brand colour from `style.md`), `--srt` (also write `OUT.srt` for YouTube), `--ass-only` (write `OUT.ass` only, no video).
Writes one file: `OUT.mp4`. Use the same path for IN and OUT to caption in place: the clean input is kept in `.clean/` next to it, and every rerun burns from that clean copy. A video the script already captioned (tag `film-captions` in its metadata) is never captioned again.

4. Check 3 frames (`ffmpeg -ss <t> -i OUT.mp4 -frames:v 1 x.png`) at caption changes:
   - text inside the frame, not over on-screen text or a face. `auto` handles most of this: per caption it measures detail and brightness in the bottom and top bands, moves to the quieter one, and adds a dark box when the picture is busy or bright. Force `--position` only if auto is wrong;
   - vertical video: captions sit above the bottom ~22% (platform UI); the script does this by aspect;
   - words match the voice. A misheard word: fix it in the words JSON (`text` field) and rerun.

## Rules built into the script

- Breaks at sentence ends, pauses over 0.3 s and commas once half a line is used; no 1-2 word orphans.
- Max on screen: clean/box 3.5 s, karaoke 2.4 s, punch 1.1 s. Back-to-back captions switch with no gap and no fade (no flicker).
- Size scales with the short side of the frame; vertical gets 12% larger text.

## Deliver

One burned file. For YouTube, run with `--srt` and upload `OUT.srt` too (searchable, viewers can turn it off). The clean master stays in `.clean/` for re-captioning; it is not a deliverable.
