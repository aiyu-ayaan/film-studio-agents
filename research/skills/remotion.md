# Remotion

| Field | Value |
|---|---|
| Repo | <https://github.com/remotion-dev/remotion> (skills: `packages/skills`, published as `remotion-dev/skills`) |
| Checked | 2026-11-20, commit `9f49257faa79`, ★74,467, last push 2026-11-20 |
| Licence | Remotion License (custom, `LICENSE.md`). Free incl. commercial for: individuals, for-profit orgs with up to 3 employees, non-profits. Company License needed above that |
| Invoke | `/remotion-create`, `/remotion-render`, `/remotion-captions`, ... |
| Engine | React components rendered in headless Chrome + FFmpeg |
| Needs | Node.js, a Remotion project (`npx create-video@latest --skills`) |
| Install | In a Remotion project: `npx remotion skills add`. Otherwise: `npx skills add remotion-dev/skills` |
| Scope | Project-local or global, depending on the skills CLI choice |

## What it does

"Make videos programmatically with React." Agent skills in `packages/skills/skills/`: remotion-best-practices, -captions, -create, -docs, -interactivity, -license, -maps, -markup, -multimedia, -render, -saas, -studio, -upgrade.
Ecosystem packages: captions, openai-whisper, install-whisper-cpp, lottie, three, skia, rive, gsap, light-leaks, motion-blur, noise, sfx, elevenlabs, google-fonts, lambda, cloudrun, player.

## Use it for

- A client who asks for Remotion or for a React codebase they will own.
- Video apps or batch rendering of many personalized videos (`/remotion-saas`, Lambda).
- Running upstream Shotcraft (`Vincentwei1021/video-shotcraft` is Remotion-based).

## Do not use it for

- Default production here. HyperFrames covers the same ground under Apache-2.0. `/remotion-to-hyperframes` ports a Remotion project.

## Voice hook

Only `bin/vo.sh` voices (Kokoro, Pocket). Any built-in voice is excluded.

Audio is a React `<Audio>` element. Pass our VO wav from `bin/vo.sh`.

## Limits and risks

- `LICENSE.md` "Disallowed use cases": you may not copy or modify Remotion code "for the purpose of selling, renting, licensing, relicensing, or sublicensing your own derivate of Remotion". Selling videos is fine. Selling a Remotion-based template pack or editor needs care.
- If you grow past 3 employees, you need a Company License (<https://www.remotion.dev/docs/license/pricing>).
- `LICENSE.md` says the licence "will slightly change" in Remotion 5.0 (PR #3750). Re-check on upgrade.
- The monorepo is ~900 MB. Do not clone it to work; use the skills package.

## Our take

Strong, mature, huge docs. Fine for solo freelance work. Keep it second to HyperFrames because of the licence ceiling and because the other skills here target HyperFrames or plain HTML.
