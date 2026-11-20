# Earshot

| Field | Value |
|---|---|
| Repo | <https://github.com/Leonxlnx/earshot> |
| Checked | 2026-11-20, commit `4ac3d2ac2b15`, ★5,280, last push 2026-11-19. Version 0.4 |
| Licence | MIT. Commercial: yes. Models: CLAP `laion/larger_clap_general`, AST `MIT/ast-finetuned-audioset-10-10-0.4593` |
| Invoke | CLI `earshot <cmd>`, MCP server `earshot mcp`, skills `earshot` and `real-sound` |
| Engine | Python, CPU only, torch + transformers |
| Needs | uv, ffmpeg/ffprobe, Python 3.10+, ~1.1 GB models |
| Install | `uv tool install --python 3.12 "earshot[mcp] @ git+https://github.com/Leonxlnx/earshot"` then `earshot doctor --fetch`. MCP: `claude mcp add earshot --scope user -e EARSHOT_THREADS=3 -- earshot mcp` |
| Scope | User-level CLI + MCP |

## What it does

"Ears for coding agents" (README). Claude cannot hear; earshot turns sound into numbers and words.

| Command | Use here |
|---|---|
| `describe`, `match`, `rank` | Pick the right SFX or music from candidates |
| `find FILE QUERY` | Best moment in a long recording |
| `timeline`, `sheet` | Listening transcript, sync of sound to picture cuts, annotated PNG |
| `critique FILE` | Scorecard against 7 pro launch films, with timestamped fixes |
| `measure FILE` | LUFS, true peak, LRA, tempo, key (no models) |
| `sfx render ID` | 252 code-made SFX, aimed at a frame (`--dur`, `--apex`, `--pitch`) |
| `kit init/render/check` | A whole film's SFX; `launch` preset places them against music and cuts |
| `forge`, `fit` | Make or re-create a sound in code |

## Use it for

- QA gate on every film (critique + measure).
- Royalty-free SFX made in code: no licence questions.

## Voice hook

Not a voice tool. Use `measure` and `critique` on the final mix.

## Limits and risks

- Each CLI call loads models (~20-40 s). For many calls, use the MCP server or `from earshot import api`.
- Linux `uv` may pull CUDA torch (large). Force CPU wheels: add `--index https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match` to the install (our suggestion, not in README).
- `earshot llm` uploads audio to Gemini; only with the user's key and consent.
- Forge reference recordings are not shipped (licensed); without refs it runs in "designed mode".
- Alpha (pyproject "Development Status :: 3 - Alpha").

## Our take

Required. It is the only check that the sound is right, and the SFX bank removes one licensing risk.
