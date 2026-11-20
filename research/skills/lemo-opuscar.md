# Lemo-Opuscar

| Field | Value |
|---|---|
| Repo | <https://github.com/lemomo-ai/lemo-opuscar> (gallery <https://lemomo-ai.github.io/lemo-opuscar/>) |
| Checked | 2026-11-20, commit `f9e204293930`, ★18,884, last push 2026-11-20 |
| Licence | Mixed (`LICENSE`, `REUSE.toml`): code MIT; all Markdown incl. each `STYLE.md` CC BY-NC 4.0; demo films CC BY 4.0. "Films you make with the library are yours, commercial films included, and need no credit" |
| Invoke | `/lemo-opuscar:lemo-opuscar`, or "Make a film in the <style> style about ..." |
| Engine | Canvas / WebGL pages rendered frame by frame, ffmpeg |
| Needs | Node 20+, ffmpeg 7+ (this PC: 7.0.2 OK), Python 3.11+ (kokoro-onnx needs 3.11-3.13; this PC's default 3.14 is too new) |
| Install | `claude plugin marketplace add lemomo-ai/lemo-opuscar && claude plugin install lemo-opuscar@lemolab`. First use downloads the library to `~/lemo-opuscar` |
| Scope | User plugin; films go in the folder you start from |

## What it does

"99 film styles for your coding agent. Pick one, bring your story, and the agent makes the film, entirely in code" (README). No video model, no stock footage.
15 categories: edit & documentary, painting, sketch & board, traditional crafts, print, graphic & type, line diagrams, cartoons, ... Folder names in `styles/` include chalkboard, whiteboard, watercolor, news-package, map-explainer, dataviz, blueprint, ukiyoe, pixel-rpg, neon-tubes, teardown, lidar-survey.
Guides: `DIRECTOR.md` (story, sound, rhythm, camera), `TECHNIQUE.md` (render, voice, music, mix), `styles/<style>/STYLE.md`.
Original music from free sample libraries (`core/audio/sampler.py`: VSCO 2 CE, VCSL, FreePats, Karoryfer, Salamander; licences in `core/audio/INSTRUMENTS.md`).
"Make a style your own": brand colours, logo, characters, kept in `~/lemo-my-styles/<name>/`.
A film takes the agent "about 30-60 minutes"; README says set effort to high.

## Use it for

- Narrated explainers and documentaries with a strong look. Each video can use a different style: helps against YouTube's "template" rule.
- A client's branded house style (make a style your own).

## Voice hook

`TECHNIQUE.md` section 4: "TTS is only the default. If the user brings a recording or names a voice, use that." Default English TTS is Kokoro (`core/tts/tts.py`); Chinese uses edge-tts (online). It checks every line with faster-whisper (`asr_check.py`).
Its built-in TTS (`core/tts`: its own Kokoro, edge-tts) is excluded. Give it our `bin/vo.sh` wav per line as "the user's recording".

## Limits and risks

- STYLE.md and all docs are CC BY-NC: use them to make films, never resell or republish the style prompts.
- Never use Clawd (Anthropic's mascot) or the Mascot Screencast style's Claude UI in paid work (`LICENSE`: no licence given).
- Six demo narrations (Edge TTS, Doubao TTS) are excluded from any licence. Do not reuse demo films' audio.
- Manga Panels, Text Flash Cuts, Comic History Cartoon need an image generator you bring.
- Third-party material in a film (samples under CC BY, maps, footage) keeps its own terms: credit it.

## Our take

Best tool for varied, original-looking narrated content at scale. The built-in sampler score is a real money saver.
