# 3DViz Pro Max

| Field | Value |
|---|---|
| Repo | <https://github.com/viettranx/3dviz-pro-max> (site <https://3dviz.dev>) |
| Checked | 2026-11-20, commit `d077e0e68915`, ★1,441, last push 2026-09-11 |
| Licence | MIT. Commercial: yes |
| Invoke | `/3dviz-pro-max` (folder install) or `/3dviz-pro-max:3dviz-pro-max` (plugin) |
| Engine | Three.js 0.180 (Vite scaffold); optional Blender 4.2+ for baked T3 hero models |
| Needs | Node, Python 3. Optional: Playwright + Chromium for `capture.py`, Blender 4.2 LTS+ |
| Install | `git clone https://github.com/viettranx/3dviz-pro-max ~/.local/share/skill-src/3dviz-pro-max && ln -s ~/.local/share/skill-src/3dviz-pro-max/skills/3dviz-pro-max ~/.claude/skills/3dviz-pro-max`. Copy the whole folder, never `SKILL.md` alone (README "Install") |
| Scope | Global user skill |

## What it does

"Turn an idea into a 3D scene worth exploring" (README). Ten-step workflow from intent to honest report.
Ships (as of 2026-09-10, `catalog-summary.json`): 223 recipes, 440 knowledge records, 22 kit blueprints, 37 style profiles, 24 directions, 37 runnable example studies.
Directions include environments, characters, products and assemblies, architecture, anatomy, molecules, math (linear algebra, calculus, topology), algorithms, robotics, astronomy.

## Use it for

- 3D hero moments inside a promo (product exploded view, logo in 3D world).
- STEM / education explainers: math, physics, anatomy, algorithms. Good YouTube niche because each video is unique.

## Do not use it for

- A whole narrated film alone. It builds interactive scenes, not a timeline. Record the scene into HyperFrames, or capture frames and cut them in.

## Voice hook

None. It makes no audio. Add VO and sound in the HyperFrames composition.

## Limits and risks

- GTX 1650 4 GB: fine for Three.js; heavy post or big scenes may be slow. Blender bakes on CPU are slow.
- Plugin marketplace install route is "untested" (README).
- Its showcase village footage predates the skill (README caption): do not judge quality from it.

## Our take

Niche but valuable: 3D sells at a premium on freelance sites, and STEM content avoids the "template" YouTube problem.
