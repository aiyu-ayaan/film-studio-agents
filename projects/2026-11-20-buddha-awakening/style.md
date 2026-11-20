# Style Bible: The Prince Who Chose Truth

## Palette
- **Ground (Obsidian Night)**: `#0F0D0B` (with subtle radial warm vignette `#1F1812` and 3% film grain)
- **Secondary Ground (Temple Stone)**: `#1B1612`
- **Primary Ink (Warm Parchment)**: `#F2E8D5`
- **Muted Ink (Sandstone)**: `#B8A88E`
- **Accent (Burnished Gold)**: `#D4A34A`
- **Highlight / Tension (Lotus Crimson)**: `#B84335`

## Typography
- **Display / Titles**: `Cinzel` or `Georgia` serif (bundled fallback: `Georgia, "Times New Roman", serif`), bold, tight tracking `-0.02em`, uppercase for single-word hooks, sentence case for teachings.
- **Body / Sub-labels**: `Inter` / `DejaVu Sans` (clean sans-serif), minimum 58px at 1440x2560 (~2.3%–4% of frame height) so every word is crisp on phones.

## Surface & Lighting
- Never flat swatches: every background uses layered radial glows, drifting golden dust motes, and subtle SVG noise grain.
- Warm candle/dawn light rays in gold (`#D4A34A`) against deep charcoal (`#0F0D0B`).

## Motion & Framing
- **Canvas**: 1440x2560 (9:16 2K vertical), 30 fps.
- **Safe zones**: Keep all key visuals and on-screen text inside the top 75% and middle 80% width. **Bottom 22% (`y > 1996px`) is reserved for `film-captions`** — no scene text there.
- **Motion**: Median move ~10 frames; landings ease-out (`power3.out`), exits ease-in (`power2.in`). Continuous slow camera drift or particle motion so no frame is ever dead. Hard cuts on motion between scenes.

## Captions
- Style: `karaoke` with accent `#D4A34A` (burnished gold), placed in bottom 20% safe zone.
