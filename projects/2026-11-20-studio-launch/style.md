# Style bible: film-studio launch

One look for every scene. Skills vary technique, never identity.

| Token | Value |
|---|---|
| Frame | 1440x2560, 30 fps, 9:16 |
| Ground | Ink `#0B0F1A`, lifted to `#141A2B` in the light pool; never flat: radial light + 3% film grain |
| Ink (text) | Paper `#F4EFE6` |
| Accent | Amber `#FFB547` (hero words, highlights, caption karaoke) |
| Secondary | Cyan `#5EE6FF` (UI, data, waveforms), used sparingly |
| Display font | Montserrat Black / ExtraBold, tight tracking -0.03em |
| Mono font | FiraCode Nerd Font (terminal, code, numbers) |
| Type scale | Hero 220-300 px; headline 140 px; body 72 px; UI min 104 px (4% of height) |
| Safe zones | Top 8% free (platform UI). Bottom 22% reserved for captions: no on-screen text below y=1990. Side margins 96 px |
| Motion | Median move 10 frames; land ease-out (`power3.out`), leave ease-in; arrive from oversize or edge, never from zero; hard cuts on motion |
| Lemo scene | Ink-wash look, tinted to ink/paper/amber so it reads as the same film |
| Captions | film-captions `karaoke`, accent `FFB547`, Montserrat |
| Never | Corner labels, counters, timecodes, progress bars, third-party logos, Claude UI or mascot |
