# Style Bible: Newton's Three Laws of Motion

## Palette
- **Ground (Deep Physics Slate)**: `#0B101B` (radial spotlight `#162036`, subtle 24px engineering grid at 4% opacity, 3% grain)
- **Diagram Card / Panel**: `#131B2E` with `2px solid rgba(148, 163, 184, 0.22)` border
- **Primary Ink (Chalk White)**: `#F4F7FB`
- **Muted Ink (Slate Grey)**: `#94A3B8`
- **Motion / Velocity Accent (Electric Cyan)**: `#38BDF8`
- **Applied / Net Force Accent (Amber Gold)**: `#F59E0B`
- **Normal / Balance Accent (Emerald)**: `#34D399`
- **Gravity / Reaction Accent (Coral Red)**: `#FB7185`

## Typography
- **Display / Titles**: `Space Grotesk` or `Inter` / `DejaVu Sans`, bold, tight tracking `-0.02em`, crisp uppercase headers for law titles.
- **Equations & Variables**: `JetBrains Mono` or `Georgia` italic for physics symbols (`F`, `m`, `a`, `v`, `u`, `p`), minimum 54px at 1440x2560 so every subscript and fraction reads cleanly on a phone.
- **FBD Vector Labels**: Minimum 46px bold with dark pill backdrop so arrows never collide with text.

## Surface & Diagram Rules
- Every scene uses a subtle blueprint coordinate grid and soft radial glow—never a flat solid fill.
- **Proper Free Body Diagrams (FBDs)**: Always isolate the body as a clean box/dot with arrows originating from the center of mass (or contact surface where clearly indicated), arrow length proportional to magnitude, and clear arrowheads + symbol labels (`mg`, `F_N`, `F_app`, `f`, `F_AB`, `F_BA`).
- **Derivations**: Show each algebraic step cleanly top-to-bottom inside a dedicated equation card, highlighting the substituted term in cyan/amber before simplifying.

## Motion & Framing
- **Canvas**: 1440x2560 (9:16 2K vertical), 30 fps.
- **Safe zones**: Keep all diagrams, equations, and labels inside the top 74% (`y: 140px – 1890px`) and middle 86% width (`x: 100px – 1340px`). **Bottom 22% (`y > 1996px`) is reserved exclusively for `film-captions`**.
- **Motion**: Median move ~10 frames; landings ease-out (`power3.out`), exits ease-in (`power2.in`); continuous subtle grid/particle/vector shimmer so no frame is dead. Hard cuts on motion between scenes.

## Captions
- Style: `clean` (crisp readable subtitles for study/explainer) with accent `#38BDF8` in the bottom 20% safe zone.
