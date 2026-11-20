# TTS: KittenTTS and lighter real-sounding voices

## Decision (user, 2026-11-20)

Only **Kokoro-82M** and **Pocket TTS** are used, through `bin/vo.sh`. Every built-in voice of any skill or library is excluded (see "Voice policy" in `../CLAUDE.md`).
Everything below about KittenTTS 2, VoiceStudio, Chatterbox and others is kept as research only: not in use.

Checked 2026-11-20. Machine: 8-core CPU, 31 GB RAM, GTX 1650 4 GB.

## Recommendation

User requirement (2026-11-20): the voice must sound as human as possible, never electronic or "AI agent".
So speed is second. Quality of a final voice decides.

| Role | Engine | Why |
|---|---|---|
| ~~Final voice~~ (excluded) | KittenTTS 2 (removed) | 1.7B model, the largest local model that runs on this CPU. Copies how real people talk; emotion tags (`[joyful]`, `<laugh>`, `<sigh>`, `(((stress)))`), 50 English voices. Slow: ~2 min per 10 s, so run in background. Needs Stellon Labs registration for commercial use |
| **Most human of all: your own voice** | **Pocket TTS** clone | A clone of a real person's 10-20 s clean recording sounds like that person. Only your own voice or a client's with written consent. Pocket weights CC BY 4.0 (credit Kyutai) |
| Clean narration, drafts and timing | **Kokoro-82M** | Apache-2.0, top UTMOS (4.46) in a CPU benchmark, faster than real time. Clean but narrator-like, so not the final voice when "human" matters most. Use it to time the picture, then swap in the KittenTTS take |
| ~~Workbench~~ (excluded) | VoiceStudio app (below) | Auditions dozens of engines in one GUI. Do not use its default engine for paid work |

Update later on 2026-11-20: KittenTTS was removed from disk. Final engine is pending the user's ear test of these clips (same line, made on this PC):
`kokoro.wav` (af_heart), `kokoro-af_nova.wav`, `kokoro-am_michael.wav`, `pocket.wav` (Pocket default voice). Pocket TTS and Kokoro are installed in `../.venv`.
A clone of the user's own voice with Pocket TTS is expected to sound the most human (our take).

Our take, not measured: the model with the most acting range (KittenTTS 2, or Pocket with a real-voice clone) beats a small clean model for "sounds like a person". A UTMOS score measures clarity, not humanness, so Kokoro's higher score does not settle it. Claude cannot hear: the user's ear decides.
Judge by ear: `research/tts-audition/kokoro.wav` exists. `kitten.wav` could not be made on 2026-11-20 because the KittenTTS folder was gone; after reinstalling, run `bin/vo.sh kitten "Hey, so... this is Kitten. It's local, and honestly? It sounds pretty human." research/tts-audition/kitten.wav`.

Reinstall KittenTTS (from its old `config.md`):
`uv venv -p 3.12 .venv && uv pip install -p .venv kitten_tts_cpp soundfile`, plus its `tts.py` wrapper (the `kitten_tts_cpp` API: `KittenTTS("KittenML/kitten-tts-2", decoder="student_w4", threads=8).generate_to_file(text, out, voice=..., preset="expressive")`). First run downloads ~1 GB to `~/.cache/kitten-tts`.

## Make any TTS sound human (rules for every script)

1. Write speech, not text: contractions, short sentences, "so,", "I mean,", "honestly?". One idea per sentence.
2. Punctuation is timing: comma short pause, "..." long pause, "?" lifts pitch.
3. Generate one line per take, not the whole script at once. Keep the best seed per line (`--seed`).
4. Use emotion tags sparingly: one per 2-3 lines. Too many sounds acted.
5. Vary pace: hook faster, proof slower. Leave 0.2-0.4 s gaps between lines in the edit.
6. Post: light compression, high-pass at 80 Hz, a little room tone under the voice so silence is not digital zero. Music 8-10 dB under the voice.
7. Check every line with a transcription (`vo.words.json`): a misread word sounds robotic at once.

## Heavier, more human engines (need a bigger GPU)

These are reported as more expressive but need more than this GTX 1650 4 GB / CPU can run fast: Chatterbox (MIT; 7.5 GB RAM and 48 s to first audio on CPU in Picovoice's test), Orpheus 3B (Apache-2.0 card, Llama base), Qwen3-TTS 1.7B (Apache-2.0), CosyVoice 3 0.5B (Apache-2.0). Try them in VoiceStudio or on a rented GPU before paying for hardware.

## Your KittenTTS setup

- Path: `/media/aiyu/550E85595197DBEC/development/KittenTTS`, entry `tts.py`, runtime `kitten_tts_cpp`, model `KittenML/kitten-tts-2` (1.7B) with `student_w4` decoder.
- Command: `.venv/bin/python tts.py -f script.txt --voice Claire --preset expressive -o out.wav`. Defaults and voice guide in its `config.md`.
- Speed: ~2 min compute per ~10 s audio (its `CLAUDE.md`). Run in the background.
- Model licence: Stellon Labs Community License (<https://huggingface.co/KittenML/kitten-tts-2/blob/main/LICENSE.md>). Section 3: commercial use allowed, but "you must register with Stellon Labs by contacting us"; above USD 1,000,000 annual revenue you need another licence. Section 4.c(iii): you own the outputs. Code is Apache-2.0.
- Lighter Kitten: KittenTTS Nano (15-80M, Apache-2.0). Picovoice measured first audio at 10,483 ms on a Ryzen 7 5700X; slower than Kokoro in that test.

## Benchmarks (copied numbers)

HeyNeo CPU benchmark, 2026-07-06, Intel Xeon 8272CL, 4 cores, no GPU. RTF < 1 means faster than real time.

| Model | Params | Mean RTF | UTMOS | Cloning | Licence |
|---|---|---|---|---|---|
| Kokoro-82M (PyTorch) | 82M | 0.665 | 4.46 | No | Apache-2.0 |
| Kokoro-82M (ONNX) | 82M | 0.641 | 4.44 | No | Apache-2.0 |
| Supertonic 3 (5 steps) | ~99M | 0.240 | 4.32 | No | OpenRAIL-M |
| Pocket TTS | ~100M | 0.714 | 4.10 | Yes, ~5 s | see below |
| Inflect-Nano-v1 | 4.63M | 0.145 | 3.48 (author: "buzzy and robotic") | ? | Apache-2.0 |

Picovoice on-device benchmark (published 2026-07-14, updated 2026-08-18), Ryzen 7 5700X: first-audio latency Pocket 1,713 ms, Piper 1,720 ms, Supertonic 2 2,612 ms, Kokoro 3,658 ms, KittenTTS Nano 10,483 ms, Chatterbox Turbo 48,281 ms (7.5 GB peak RAM).

## Others considered

| Model | Verdict | Reason |
|---|---|---|
| Chatterbox (Resemble) | Skip on this PC | MIT and expressive, but Turbo 7.5 GB RAM and 48 s to first audio on CPU; adds a PerTh watermark |
| Piper | Skip | Fast but robotic; engine now GPL-3.0 (`piper1-gpl`), per-voice licences |
| NeuTTS Air | Maybe later | Apache-2.0, cloning from 3 s, 0.7B: heavier |
| Qwen3-TTS 0.6B | Maybe later (GPU) | Apache-2.0, cloning, voice design by text. GPU-oriented |
| F5-TTS, XTTS-v2, ChatTTS, Spark-TTS, OmniVoice | No | Non-commercial weights |
| Fish Audio S2, IndexTTS-2.5 | No | Research or permission-needed licences |

## VoiceStudio (debpalash/VoiceStudio)

| Field | Value |
|---|---|
| Repo | <https://github.com/debpalash/voicestudio>, ★114,887, last push 2026-11-20 (checked 2026-11-20) |
| What | Desktop app: "fully-local ElevenLabs alternative": voice cloning, voice design, video dubbing, dictation, transcription, audiobooks, 646 languages. Local API, MCP server, batch queue, watch folders |
| Licence | App AGPL-3.0 (free incl. commercial use under its terms). Pro: closed build with a "Commercial License for your client work" (README "Pro and Cloud") |
| Linux | x64: AUR, Snap, DEB, AppImage, Nix. NVIDIA CUDA, CPU, Vulkan for GGUF engines |
| Default engine | "VoiceStudio (default, powered by k2-fsa/OmniVoice)". OmniVoice weights are CC-BY-NC (Yaps licence table): **not for paid work** |
| Other engines (`docs/feature-catalog.md`) | KittenTTS, pockettts, supertonic3, CosyVoice 3 (+GGUF), IndexTTS 2.5, VoxCPM2, MOSS-TTS, gpt-sovits, sherpa-onnx, dots.tts, ... Each keeps its own model licence |

Our take: worth installing as a listening workbench and for dubbing. For paid work, pick an engine inside it whose weights allow commercial use (KittenTTS 2 after registering, Pocket TTS with credit, CosyVoice 3 Apache-2.0) and record the engine in the project `NOTE.md`. IndexTTS 2.5 needs bilibili's permission for commercial use. Its MCP server could let Claude drive it; not tested here.

## Pocket TTS licence note

Sources disagree: HeyNeo says MIT, Picovoice says MIT and Apache-2.0, Yaps says CC BY 4.0.
Checked 2026-11-20: the Hugging Face model `kyutai/pocket-tts` has `license: cc-by-4.0` (gated: auto). GitHub `kyutai-labs/pocket-tts` code is MIT.
So: commercial use allowed with attribution to Kyutai for the weights. Install: `uv pip install pocket-tts` in a Python 3.11/3.12 venv.

## Sources

- <https://heyneo.com/blog/kokoro-supertonic-inflect-nano-pocket-tts-cpu-benchmark>
- <https://picovoice.ai/blog/on-device-tts/>
- <https://www.yaps.ai/blog/best-local-tts-models> (licences checked 2026-10-10)
- <https://huggingface.co/api/models/kyutai/pocket-tts>
- KittenTTS `upstream/README.md` "License", and its HF LICENSE.md
