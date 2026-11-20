#!/usr/bin/env python3
"""Stage 3 (speech mode): voice every script line, join them, time the scenes to the voice.

Reads  <project>/plan.json  (master, lines[], scenes[]).
Writes audio/vo/lines/<id>.wav, audio/vo/vo.wav (48 kHz mono), audio/vo/vo.words.json,
       audio/vo/vo.srt, and updates plan.json: lines[].start_s/end_s/asr_ok, scenes[].start_s/end_s/start_f/frames.

Usage: narrate.py <project_dir> [--only l3,l7]   (--only re-voices those lines, reuses the rest)
Stdlib only; needs ffmpeg, ffprobe, npx (hyperframes) and ../../../../bin/vo.sh.
"""
import argparse, difflib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # Movies/
VO = ROOT / "bin" / "vo.sh"
SR = 48000


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"failed: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]))


def norm_words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def synth_line(m, line, raw, out):
    env = dict(os.environ, VO_NO_WORDS="1")
    cmd = [str(VO), m["voice_engine"], line["text"], str(raw)]
    if m.get("voice"):
        cmd.append(m["voice"])
    run(cmd, env=env)
    # 48 kHz mono, trim leading/trailing silence so gaps are ours, not the engine's.
    trim = "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", trim, "-ac", "1", "-ar", str(SR), str(out)])


def transcribe(wav):
    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ)
        env.setdefault("HYPERFRAMES_CACHE_DIR", str(Path.home() / ".local/share/hyperframes-cache"))
        r = subprocess.run(["npx", "-y", "hyperframes", "transcribe", str(wav), "--dir", d, "--json"],
                           capture_output=True, text=True, env=env)
        t = Path(d) / "transcript.json"
        if r.returncode or not t.exists():
            sys.exit(f"transcription failed (install: npx hyperframes models install parakeet)\n{r.stdout[-500:]}{r.stderr[-500:]}")
        return json.loads(t.read_text())


def srt_time(s):
    ms = round(s * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def write_srt(words, path, max_words=7, max_s=2.8):
    cues, cur = [], []
    for w in words:
        cur.append(w)
        end_punct = w["text"][-1:] in ".?!,;:"
        if len(cur) >= max_words or cur[-1]["end"] - cur[0]["start"] >= max_s or end_punct:
            cues.append(cur); cur = []
    if cur:
        cues.append(cur)
    out = [f"{i}\n{srt_time(c[0]['start'])} --> {srt_time(c[-1]['end'])}\n{' '.join(w['text'] for w in c)}\n"
           for i, c in enumerate(cues, 1)]
    Path(path).write_text("\n".join(out))


def time_scenes(plan, total_s):
    """Scene i starts at the start of its first line (scene 0 at 0); ends where the next starts."""
    m, fps = plan["master"], plan["master"]["fps"]
    starts = {l["id"]: l["start_s"] for l in plan["lines"]}
    scenes = plan["scenes"]
    for i, sc in enumerate(scenes):
        sc["start_s"] = 0.0 if i == 0 else round(starts[sc["line_ids"][0]] - m.get("cut_lead_s", 0.1), 3)
    for i, sc in enumerate(scenes):
        sc["end_s"] = scenes[i + 1]["start_s"] if i + 1 < len(scenes) else total_s
        # Frame-exact from absolute times, never by summing rounded durations.
        sc["start_f"] = round(sc["start_s"] * fps)
        end_f = round(sc["end_s"] * fps)
        sc["frames"] = end_f - sc["start_f"]
        if sc["frames"] <= 0:
            sys.exit(f"scene {sc['id']} has no frames: check its line_ids order")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--only", default="", help="comma list of line ids to re-voice")
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    plan_p = proj / "plan.json"
    plan = json.loads(plan_p.read_text())
    m = plan["master"]
    if not m.get("speech", True):
        sys.exit("plan.master.speech is false: use timing.py (no-speech mode)")
    if not m.get("voice_engine"):
        sys.exit("plan.master.voice_engine is empty: ask the user which voice (see research/tts.md), then set it")
    if m["voice_engine"] not in ("kokoro", "pocket"):
        sys.exit(f"voice_engine {m['voice_engine']!r} not allowed: studio voices are kokoro or pocket only")
    only = set(filter(None, a.only.split(",")))
    vo_dir = proj / "audio" / "vo"
    (vo_dir / "lines").mkdir(parents=True, exist_ok=True)

    # 1. One take per line.
    for line in plan["lines"]:
        out = vo_dir / "lines" / f"{line['id']}.wav"
        if out.exists() and line["id"] not in only:   # reuse takes; --only forces a new take
            continue
        print(f"voicing {line['id']}: {line['text'][:60]}")
        synth_line(m, line, vo_dir / "lines" / f"{line['id']}.raw.wav", out)

    # 2. Join with gaps; record absolute line times.
    lead, gap = m.get("lead_in_s", 0.4), m.get("gap_s", 0.35)
    t, parts = lead, []
    silence = lambda s: f"anullsrc=r={SR}:cl=mono,atrim=duration={s:.3f}"
    inputs, filters = [], []
    filters.append(f"{silence(lead)}[s0]"); parts.append("[s0]")
    for i, line in enumerate(plan["lines"]):
        wav = vo_dir / "lines" / f"{line['id']}.wav"
        d = duration(wav)
        line["start_s"], line["end_s"] = round(t, 3), round(t + d, 3)
        g = line.get("pause_after_s", gap)
        inputs += ["-i", str(wav)]
        parts.append(f"[{len(inputs)//2 - 1}:a]")
        filters.append(f"{silence(g)}[g{i}]"); parts.append(f"[g{i}]")
        t += d + g
    total = round(plan["lines"][-1]["end_s"] + m.get("tail_s", 1.2), 3)
    tail = total - t
    if tail > 0:
        filters.append(f"{silence(tail)}[tail]"); parts.append("[tail]")
    fc = ";".join(filters + ["".join(parts) + f"concat=n={len(parts)}:v=0:a=1[out]"])
    vo = vo_dir / "vo.wav"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[out]", "-ar", str(SR), "-ac", "1", str(vo)])

    # 3. Word timings of the joined track + script check per line.
    words = transcribe(vo)
    (vo_dir / "vo.words.json").write_text(json.dumps(words, indent=1))
    write_srt(words, vo_dir / "vo.srt")
    bad = []
    for line in plan["lines"]:
        heard = [w["text"] for w in words if line["start_s"] - 0.15 <= w["start"] < line["end_s"] + 0.15]
        ratio = difflib.SequenceMatcher(None, norm_words(line["text"]), norm_words(" ".join(heard))).ratio()
        line["asr_ratio"] = round(ratio, 3)
        line["asr_ok"] = ratio >= line.get("asr_min_ratio", m.get("asr_min_ratio", 0.85))   # per-line override for brand names
        if not line["asr_ok"]:
            bad.append(f"{line['id']} ({ratio:.2f}): said '{' '.join(heard)}'")

    # 4. Scene timing locks here.
    time_scenes(plan, total)
    plan["master"]["duration_s"] = total
    plan["master"]["total_frames"] = round(total * m["fps"])
    plan_p.write_text(json.dumps(plan, indent=2))
    print(f"vo.wav {total:.2f}s, {len(words)} words, {len(plan['scenes'])} scenes timed")
    for sc in plan["scenes"]:
        print(f"  {sc['id']:>6} {sc['skill']:<14} {sc['start_s']:7.2f}s  {sc['frames']:5d} frames")
    if bad:
        print("ASR MISMATCH (rewrite or re-voice with --only):\n  " + "\n  ".join(bad))
        sys.exit(3)


if __name__ == "__main__":
    main()
