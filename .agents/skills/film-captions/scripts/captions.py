#!/usr/bin/env python3
"""Add styled captions to any video. Captions only: picture and sound are not changed.

Word timings come from --words (transcript JSON [{text,start,end}], e.g. audio/vo/vo.words.json)
or, if absent, from transcribing the video (Parakeet via `npx hyperframes transcribe`).
Builds an ASS file at the video's own resolution and burns it with libass.

Styles:
  clean    2-line white subtitle with soft outline, bottom. Default for explainers.
  karaoke  1-2 lines, the spoken word lights up in the accent colour and pops. Social/story.
  box      white text on a translucent dark box. Busy backgrounds, documentaries.
  punch    1-3 words at a time, big, centred, uppercase, pop-in. Shorts/Reels hooks.

Placement (--position auto, default) is content aware: for each caption it samples the frames under it,
measures detail (edges: on-screen text, figures) and brightness in the bottom and top caption bands,
puts the caption in the quieter band, and gives it a dark box when both bands are busy or bright.

Usage:
  captions.py IN.mp4 OUT.mp4 [--words vo.words.json] [--style karaoke] [--accent FFD400]
              [--font Montserrat] [--position auto|bottom|middle|top] [--srt] [--ass-only]
Writes only OUT.mp4 (plus OUT.srt with --srt; OUT.ass with --ass-only, no video).
OUT may equal IN: the clean input is kept in IN's folder under .clean/ and reused on every rerun,
so captions are never burned twice. A video this script already captioned is refused as input.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(map(str, cmd))[:300]}\n{r.stderr[-1500:]}")
    return r.stdout


def probe(video):
    w, h = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                "-of", "csv=p=0:s=x", str(video)]).strip().split("x")
    return int(w), int(h)


TAG = "film-captions"
BUSY, BOX_EDGE, BRIGHT = 0.02, 0.012, 0.6  # edge density / brightness, 0..1. Calibrated 2026-11-20: flat ground 0.002, thin lines 0.013, on-screen titles 0.02-0.06


def tagged(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format_tags=comment", "-of", "csv=p=0",
                          str(video)], capture_output=True, text=True).stdout
    return TAG in out


def sample(video, sw=192, fps=4):
    """Small grayscale frames at `fps`, for placement. Returns (frames, sw, sh)."""
    w, h = probe(video)
    sh = round(h * sw / w / 2) * 2
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={fps},scale={sw}:{sh},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    n = sw * sh
    return [raw[i:i + n] for i in range(0, len(raw) - n + 1, n)], sw, sh


def band_stats(frame, sw, y0, y1):
    """Edge density (0..1) and mean brightness (0..1) of rows y0..y1."""
    edges = lum = cnt = 0
    for y in range(max(0, y0), min(y1, len(frame) // sw - 1)):
        r, r2 = y * sw, (y + 1) * sw
        for x in range(sw - 1):
            p = frame[r + x]
            edges += abs(frame[r + x + 1] - p) + abs(frame[r2 + x] - p)
            lum += p; cnt += 1
    return (edges / cnt / 255, lum / cnt / 255) if cnt else (0, 0)


def place(events, video, w, h, size, margin_v, fps=4):
    """Per event: (alignment, boxed). Bottom unless it is clearly busier than the top; box when busy or bright."""
    frames, sw, sh = sample(video, fps=fps)
    k = sh / h
    band = round(size * 2.6 * k)
    bot = (round((h - margin_v) * k) - band, round((h - margin_v) * k))
    top = (round(margin_v * k), round(margin_v * k) + band)
    out, prev = [], 2
    for ev in events:
        idx = range(int(ev[0]["start"] * fps), int(ev[-1]["end"] * fps) + 1)
        fs = [frames[i] for i in idx if i < len(frames)][:8] or frames[-1:]
        b = [band_stats(f, sw, *bot) for f in fs]
        t = [band_stats(f, sw, *top) for f in fs]
        be, bl = max(x[0] for x in b), max(x[1] for x in b)
        te, tl = max(x[0] for x in t), max(x[1] for x in t)
        # Move up only for a clear win; stay where we were when it is close (no jumping).
        if be > BUSY and be > 1.8 * te:
            align = 8
        elif te > BUSY and te > 1.8 * be:
            align = 2
        else:
            align = prev
        e, l = (te, tl) if align == 8 else (be, bl)
        out.append((align, e > BOX_EDGE or l > BRIGHT))
        prev = align
    return out


def transcribe(video):
    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ)
        env.setdefault("HYPERFRAMES_CACHE_DIR", str(Path.home() / ".local/share/hyperframes-cache"))
        r = subprocess.run(["npx", "-y", "hyperframes", "transcribe", str(video), "--dir", d, "--json"],
                           capture_output=True, text=True, env=env)
        t = Path(d) / "transcript.json"
        if r.returncode or not t.exists():
            sys.exit("transcription failed: pass --words, or run `npx hyperframes models install parakeet`")
        return json.loads(t.read_text())


def group(words, style, width, size):
    """Split words into caption events. Breaks on sentence ends, long pauses, and length."""
    if style == "punch":
        max_words, max_chars = 3, 18
    else:
        # ~0.55 em average glyph width; leave 12% side margins.
        max_chars = int(width * 0.76 / (size * 0.55)) * (2 if style in ("clean", "box") else 1)
        max_words = 14 if style in ("clean", "box") else 7
    def words_to_sentence_end(i):
        for k in range(i + 1, len(words)):
            if words[k]["text"][-1:] in ".?!":
                return k - i
        return len(words) - i - 1

    def words_to_clause_end(i):
        for k in range(i + 1, len(words)):
            if words[k]["text"][-1:] in ".?!,;:":
                return k - i
        return len(words) - i - 1

    events, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        text = " ".join(x["text"] for x in cur)
        nxt = words[i + 1] if i + 1 < len(words) else None
        pause = nxt is not None and nxt["start"] - w["end"] > 0.3
        max_s = {"clean": 3.5, "box": 3.5, "karaoke": 2.4, "punch": 1.1}[style]
        full = len(cur) >= max_words or len(text) >= max_chars or w["end"] - cur[0]["start"] >= max_s
        # Don't leave 1-2 words of a sentence alone in the next caption (punch keeps its tight limit).
        if full and style != "punch" and min(words_to_sentence_end(i), words_to_clause_end(i)) <= 2 and len(cur) < max_words + 3:
            full = False
        if full and style == "punch" and words_to_sentence_end(i) == 1:
            full = False
        # Past half the limit, a comma is a good place to break.
        comma = w["text"][-1:] in ",;:" and (style == "punch" or len(text) > max_chars * 0.4)
        if nxt is None or w["text"][-1:] in ".?!" or pause or full or comma:
            events.append(cur); cur = []
    return events


def t_ass(s):
    cs = max(0, round(s * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def t_srt(s):
    ms = max(0, round(s * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def bgr(hex_rgb, alpha=0):
    h = hex_rgb.lstrip("#")
    return f"&H{alpha:02X}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def esc(t):
    return t.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def wrap2(ws):
    """Two balanced lines for long events."""
    text = " ".join(ws)
    if len(text) < 38 or len(ws) < 4:
        return [ws]
    best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(" ".join(ws[k:]))))
    return [ws[:best], ws[best:]]


def build_ass(words, w, h, style, accent, font, position, video=None):
    portrait = h > w
    base = min(w, h)
    size = {"clean": 0.056, "box": 0.05, "karaoke": 0.062, "punch": 0.11}[style] * base
    size = round(size * (1.12 if portrait else 1))
    margin_v = round(h * (0.22 if portrait else 0.085))          # vertical feeds hide the bottom ~20% under UI
    auto = position == "auto"
    if style == "punch" and position in ("bottom", "auto"):
        position = "middle"
    align = {"bottom": 2, "middle": 5, "top": 8, "auto": 2}[position]
    outline, shadow, border = round(size * 0.07, 1), round(size * 0.04, 1), 1
    primary, secondary, back = bgr("FFFFFF"), bgr("FFFFFF"), bgr("000000", 0x70)
    if style == "karaoke":
        primary = bgr(accent)                                     # \k: word turns primary when spoken
    if style == "box":
        border, outline, shadow, back = 3, round(size * 0.28), 0, bgr("000000", 0x50)
    bold = -1
    fam = font if style != "punch" else f"{font} Black"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{fam},{size},{primary},{secondary},{bgr('000000', 0x20) if border == 1 else back},{bgr('000000', 0x90)},{bold},0,0,0,100,100,{round(size * 0.02, 1)},0,{border},{outline},{shadow},{align},{round(w * 0.1)},{round(w * 0.1)},{margin_v},1
Style: CapBox,{fam},{size},{primary},{secondary},{bgr('000000', 0x20) if border == 1 else back},{bgr('000000', 0x50)},{bold},0,0,0,100,100,{round(size * 0.02, 1)},0,3,{round(size * 0.28)},0,{align},{round(w * 0.1)},{round(w * 0.1)},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines, srt = [], []
    fade_in_next = True
    events = group(words, style, w, size)
    spots = place(events, video, w, h, size, margin_v) if auto and video else [(align, False)] * len(events)
    for n, ev in enumerate(events):
        start = ev[0]["start"]
        nxt = events[n + 1][0]["start"] if n + 1 < len(events) else ev[-1]["end"] + 0.6
        joined = nxt - ev[-1]["end"] < 0.35            # next caption follows at once: no gap, no fade-out
        end = nxt if joined else ev[-1]["end"] + 0.35
        fade_out = 0 if joined else 80
        fade_in, fade_in_next = (60 if fade_in_next else 0), not joined
        texts = [x["text"] for x in ev]
        if style == "punch":
            texts = [t.upper().rstrip(",;:") for t in texts]
        if style == "karaoke":
            parts, prev = [], start
            for i, x in enumerate(ev):
                lead = max(0, round((x["start"] - prev) * 100))
                dur = max(1, round((x["end"] - x["start"]) * 100))
                parts.append((f"{{\\k{lead}}}" if lead else "") + f"{{\\k{dur}}}{esc(texts[i])}")
                prev = x["end"]
            body = " ".join(parts)
            body = f"{{\\fad({fade_in},{fade_out})\\fscx94\\fscy94\\t(0,110,\\fscx100\\fscy100)}}" + body
        else:
            rows = wrap2(texts) if style in ("clean", "box") else [texts]
            body = "\\N".join(esc(" ".join(r)) for r in rows)
            anim = f"{{\\fad({fade_in},{fade_out})}}" if style != "punch" else f"{{\\fad({fade_in},{fade_out})\\fscx80\\fscy80\\t(0,120,\\fscx100\\fscy100)}}"
            body = anim + body
        an, boxed = spots[n]
        if an != align:
            body = f"{{\\an{an}}}" + body
        lines.append(f"Dialogue: 0,{t_ass(start)},{t_ass(end)},{'CapBox' if boxed and style != 'box' else 'Cap'},,0,0,0,,{body}")
        srt.append(f"{n + 1}\n{t_srt(start)} --> {t_srt(end)}\n{' '.join(x['text'] for x in ev)}\n")
    return head + "\n".join(lines) + "\n", "\n".join(srt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--words")
    ap.add_argument("--style", default="clean", choices=["clean", "karaoke", "box", "punch"])
    ap.add_argument("--accent", default="FFD400")
    ap.add_argument("--font", default="Montserrat")
    ap.add_argument("--position", default="auto", choices=["auto", "bottom", "middle", "top"])
    ap.add_argument("--srt", action="store_true", help="also write OUT.srt (sidecar for YouTube)")
    ap.add_argument("--crf", default="16")
    ap.add_argument("--ass-only", action="store_true")
    a = ap.parse_args()
    inp, out = Path(a.inp).resolve(), Path(a.out).resolve()
    clean = inp.parent / ".clean" / inp.name
    if tagged(inp):
        if not clean.exists():
            sys.exit(f"{inp} already has burned captions; caption the clean video instead")
        inp = clean                                       # rerun: burn from the clean copy, never on top
    elif inp == out:
        clean.parent.mkdir(exist_ok=True)
        shutil.copy2(inp, clean)
        inp = clean
    words = json.loads(Path(a.words).read_text()) if a.words else transcribe(inp)
    words = [x for x in words if x.get("text", "").strip()]
    if not words:
        sys.exit("no words to caption")
    w, h = probe(inp)
    ass, srt = build_ass(words, w, h, a.style, a.accent, a.font, a.position, inp)
    out.parent.mkdir(parents=True, exist_ok=True)
    if a.srt:
        out.with_suffix(".srt").write_text(srt)
    if a.ass_only:
        out.with_suffix(".ass").write_text(ass); print(out.with_suffix(".ass")); return
    tmpd = tempfile.mkdtemp()
    ass_p = Path(tmpd) / "cap.ass"
    ass_p.write_text(ass)
    tmp_out = Path(tmpd) / out.name
    path = str(ass_p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(inp), "-vf", f"ass='{path}'", "-c:v", "libx264", "-crf", a.crf,
         "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", "-metadata", f"comment={TAG}:{a.style}",
         "-movflags", "+faststart", str(tmp_out)])
    shutil.move(str(tmp_out), out)
    shutil.rmtree(tmpd, ignore_errors=True)
    print(f"wrote {out} ({a.style}, {w}x{h})" + (f", {out.with_suffix('.srt').name}" if a.srt else ""))


if __name__ == "__main__":
    main()
