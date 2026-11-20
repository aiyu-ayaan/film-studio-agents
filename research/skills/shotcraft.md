# Shotcraft (video-shotcraft / hyper-videocraft)

| Field | Value |
|---|---|
| Repo (given) | <https://github.com/windyinwind/hyper-videocraft>: ★4, one commit `5dd77fb42911` "feat: migrate Remotion -> HyperFrames (Apache 2.0)", 2026-09-02 |
| Upstream | <https://github.com/Vincentwei1021/video-shotcraft>: ★21,734, last push 2026-11-19, commit `075b548c2405`. Its `SKILL.md` names Remotion (12 mentions), not HyperFrames |
| Checked | 2026-11-20 |
| Licence | Both Apache-2.0. Commercial: yes, except bundled audio (see Limits) |
| Invoke | Say "use video-shotcraft to ..." (skill name `video-shotcraft`) |
| Engine | Fork: HyperFrames (`template/hyperframes.json`, `npx hyperframes preview/render`). Upstream: Remotion |
| Needs | Node 22, Chrome, ffmpeg |
| Install | Fork: `git clone https://github.com/windyinwind/hyper-videocraft ~/.claude/skills/video-shotcraft`. Upstream: `npx skills add Vincentwei1021/video-shotcraft` |
| Scope | Global user skill |

## What it does

Turns Claude into a product-video studio: "157 shot recipe cards, 214 styles, 214 motion previews, a production-ready template" (README).
Captures real pages of your product, builds 2.5D camera moves, beat-synced cuts and a pinned SFX pass.
Ships the **Ink Press** template: 36.2 s, 1920x1080, 30 fps, 10 shots (README). Gallery: <https://vincentwei1021.github.io/video-shotcraft/>.
Three modes (`SKILL.md`): use the template, autonomous free creation (`references/pipeline.md`), co-creation with checkpoints (`references/guided-free-creation.md`).
Also: 5 BGM tracks, 149 SFX in 16 categories, JianYing (CapCut CN) project export.

## Use it for

- SaaS / app / website promo and launch videos from real UI. The fastest path to a sellable result is Ink Press with the client's screenshots.
- Picking single named shots for any film (shot cards are general motion vocabulary).

## Do not use it for

- Narrated explainers. Its sibling `video-talkcraft` is PolyForm Noncommercial: commercial use of the toolkit "requires prior authorization from the author" (its LICENSE). Use Lemo-Opuscar or HyperFrames instead.

## Voice hook

Only `bin/vo.sh` voices (Kokoro, Pocket). Any built-in voice is excluded.

Built for music + SFX led promos. For voice, generate with `bin/vo.sh` and add as an audio clip in the HyperFrames composition.

## Limits and risks

- Bundled audio is NOT all clear. `assets/audio/ATTRIBUTION.md` line 13 says "剩余 6 个仍无法反查，商用前须逐个确认" (6 files untraceable, confirm each before commercial use), but its table marks only 5: `sfx/text/keyboard.mp3`, `sfx/ui/pop.mp3`, `sfx/riser/riser-cine.mp3`, `sfx/light/sparkle.mp3`, `sfx/transition/whoosh-big.mp3`. Exclude these 5 from paid work and treat any base SFX without a URL as the same. Files with a Mixkit URL are under the Mixkit free licence. Safer: use Earshot's code-made SFX bank.
- The fork is one unreviewed commit. If a render breaks, compare with upstream.
- Headless Linux: use `--concurrency=1`, a chrome-headless-shell binary, `--browser-executable=` if the CDN is blocked (README "Headless / CI notes").
- `SKILL.md` and references are mostly Chinese. Claude reads them fine.

## Our take

The highest-value skill for client money: product promos are what SaaS founders buy. Start with the fork (HyperFrames, matches this studio). Keep upstream as fallback.
