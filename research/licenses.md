# Licences: can I sell what this makes?

Checked 2026-11-20. Not legal advice. Re-check before a large contract.

## Action items before the first paid job

1. Voice is Kokoro (Apache-2.0) or Pocket TTS only, so no TTS registration is needed. (KittenTTS 2, now excluded, would need Stellon Labs registration.)
2. **Credit Kyutai** in the video description if you use Pocket TTS (weights CC BY 4.0).
3. **Do not use** these 5 Shotcraft SFX: `sfx/text/keyboard.mp3`, `sfx/ui/pop.mp3`, `sfx/riser/riser-cine.mp3`, `sfx/light/sparkle.mp3`, `sfx/transition/whoosh-big.mp3` (source unknown).
4. Keep a per-project asset list in `NOTE.md`. Clients may ask for it.

## Table

| Tool | Code / tool licence | Can you sell videos made with it? | Traps |
|---|---|---|---|
| HyperFrames | Apache-2.0 | Yes | HeyGen-hosted features cost money |
| Remotion | Remotion License | Yes, as an individual or company with up to 3 employees | No selling of a modified Remotion; Company License above 3 employees; licence changes in v5.0 |
| Shotcraft fork / upstream | Apache-2.0 | Yes | 5 SFX of unknown source (above). Mixkit files: Mixkit free licence |
| video-talkcraft | PolyForm Noncommercial 1.0.0 | No without the author's permission | Do not install |
| Motionmaxxing | Apache-2.0 | Yes | Bundled GSAP 3.12.5: GreenSock Standard "No Charge" licence (fine for client videos; check its terms if you sell a product built on GSAP). Do not reuse its brand demo films |
| 3DViz Pro Max | MIT | Yes | Check licences of any downloaded 3D models or HDRIs |
| Earshot | MIT | Yes; SFX bank is code-made | `llm` uploads audio to Gemini |
| Lemo-Opuscar | Code MIT; docs and STYLE.md CC BY-NC 4.0; demo films CC BY 4.0 | Yes: "Films you make with the library are yours, commercial films included, and need no credit" | Do not resell style prompts. No Clawd, no Claude UI, no third-party marks. Sample libraries and data keep their own terms (`core/audio/INSTRUMENTS.md`). Demo narrations excluded |
| Kokoro-82M | Apache-2.0 | Yes | None known |
| KittenTTS 2 (excluded) | Code Apache-2.0; model Stellon Labs Community License | Yes after registering; limit USD 1M revenue | Not used |
| Pocket TTS | Code MIT; weights CC BY 4.0 | Yes with attribution | Clone only voices you have consent for |

## Platform rules that touch money

- YouTube: realistic synthetic media must be disclosed. Mass-produced or template content is not monetizable. See `monetization.md`.
- Client work: get written permission for every logo, screenshot and trademark of the client. Never use another company's brand in a portfolio piece without labelling it as a concept/spec piece.

## Sources

Each repo's `LICENSE` / `NOTICE` / `REUSE.toml` at the commit in its card; <https://huggingface.co/KittenML/kitten-tts-2/blob/main/LICENSE.md>; <https://huggingface.co/api/models/kyutai/pocket-tts>; `video-talkcraft` LICENSE via GitHub API.
