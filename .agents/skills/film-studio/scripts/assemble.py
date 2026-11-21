#!/usr/bin/env python3
"""Stage 6: join every scene clip into one film and give it its whole sound.

Reads plan.json. Each scenes[].clip is a video from any skill; its audio is ignored.
Picture: each clip conformed to master w/h/fps (scale+pad, setsar, yuv420p), then cut or
held (last frame cloned) to exactly scenes[].frames, then concatenated.
Sound: voice (speech mode) + music bed ducked under the voice + SFX (plan.sfx[] and
scenes[].sfx_stem offset by scene start), then two-pass loudnorm to master.lufs / master.true_peak.
Captions: not burned. vo.srt is copied next to the film; the film-captions skill burns styled captions.

Writes renders/final.mp4, renders/final.srt, renders/qa.json. Exit 1 if a QA check fails.
Usage: assemble.py <project_dir> [--out renders/final.mp4]
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

SR = 48000


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(map(str, cmd))[:400]}\n{r.stderr[-2000:]}")
    return r


def loudness(path):
    """Integrated LUFS and true peak via ffmpeg ebur128."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", tail).group(1))
    return i, tp


def picture(plan, proj, tmp):
    m = plan["master"]
    w, h, fps = m["width"], m["height"], m["fps"]
    inputs, chains, labels = [], [], []
    for i, sc in enumerate(plan["scenes"]):
        clip = proj / sc["clip"]
        if not clip.exists():
            sys.exit(f"scene {sc['id']}: clip missing: {clip}")
        n = sc["frames"]
        inputs += ["-i", str(clip)]
        chains.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps={fps},format=yuv420p,tpad=stop_mode=clone:stop={n},"
            f"trim=end_frame={n},setpts=PTS-STARTPTS[v{i}]")
        labels.append(f"[v{i}]")
    fc = ";".join(chains + ["".join(labels) + f"concat=n={len(labels)}:v=1:a=0[v]"])
    out = tmp / "picture.mp4"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[v]", "-an",
         "-c:v", "libx264", "-crf", str(m.get("crf", 12)), "-preset", "medium", "-r", str(fps), str(out)])
    return out


def sound(plan, proj, tmp):
    m = plan["master"]
    total = m["total_frames"] / m["fps"]
    speech = m.get("speech", True)
    inputs, fc, mix = [], [], []

    def add(path, extra=()):
        inputs.extend([*extra, "-i", str(path)])
        return sum(1 for x in inputs if x == "-i") - 1

    vo_idx = None
    if speech:
        vo_idx = add(proj / "audio" / "vo" / "vo.wav")
        fc.append(f"[{vo_idx}:a]aresample={SR},aformat=channel_layouts=stereo,apad,atrim=0:{total:.6f},asplit=2[vo][key]")
    music = plan.get("music") or {}
    if music.get("path"):
        mi = add(proj / music["path"], ("-stream_loop", "-1"))
        fade = min(2.0, total / 4)
        gain = music.get("gain_db", -8 if speech else -1)
        fc.append(f"[{mi}:a]aresample={SR},aformat=channel_layouts=stereo,atrim=0:{total:.6f},"
                  f"volume={gain}dB,afade=t=out:st={total - fade:.3f}:d={fade:.3f}[bed]")
        if speech:  # music ducks under the voice
            fc.append("[bed][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350:makeup=1[duck]")
            mix.append("[duck]")
        else:
            mix.append("[bed]")
    elif speech:
        fc.append("[key]anullsink")
    if speech:
        mix.append("[vo]")
    sfx = list(plan.get("sfx", []))
    for sc in plan["scenes"]:
        if sc.get("sfx_stem"):
            sfx.append({"path": sc["sfx_stem"], "t": sc["start_s"], "gain_db": 0})
    for k, s in enumerate(sfx):
        si = add(proj / s["path"])
        ms = max(0, round(s["t"] * 1000))
        fc.append(f"[{si}:a]aresample={SR},aformat=channel_layouts=stereo,volume={s.get('gain_db', -4)}dB,"
                  f"adelay={ms}|{ms}[x{k}]")
        mix.append(f"[x{k}]")
    if not mix:
        return None
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,apad,atrim=0:{total:.6f}[pre]")
    pre = tmp / "pre.wav"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[pre]", "-t", f"{total:.6f}",
         "-ar", str(SR), "-c:a", "pcm_s24le", str(pre)])
    # Two-pass loudness normalisation.
    I, TP = m.get("lufs", -14), m.get("true_peak", -1.5)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(pre), "-af",
                        f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    meas = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    mixed = tmp / "mix.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(pre), "-af",
         f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
         f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true,"
         f"aresample={SR}", "-ar", str(SR), str(mixed)])
    return mixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out", default="renders/final.mp4")
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    plan = json.loads((proj / "plan.json").read_text())
    m = plan["master"]
    for sc in plan["scenes"]:
        if "frames" not in sc:
            sys.exit("scenes are not timed: run narrate.py (speech) or timing.py (no speech) first")
    out = proj / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = proj / "build" / "assemble"
    tmp.mkdir(parents=True, exist_ok=True)

    pic = picture(plan, proj, tmp)
    mix = sound(plan, proj, tmp)
    # Captions are not burned here: the film-captions skill is the only thing that adds them.
    srt = proj / "audio" / "vo" / "vo.srt"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(pic)]
    if mix:
        cmd += ["-i", str(mix)]
    cmd += ["-c:v", "copy"]
    if mix:
        cmd += ["-c:a", "aac", "-b:a", "256k"]
    cmd += ["-frames:v", str(m["total_frames"])]   # exact frame count; never -shortest (it drops frames)
    cmd += ["-movflags", "+faststart", str(out)]
    run(cmd)
    if srt.exists() and m.get("speech", True):
        shutil.copy(srt, out.with_suffix(".srt"))

    # QA
    frames = int(run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                      "stream=nb_read_packets", "-of", "csv=p=0", str(out)]).stdout.strip())
    qa = {"frames": frames, "frames_planned": m["total_frames"], "frames_ok": abs(frames - m["total_frames"]) <= 1}
    if mix:
        i, tp = loudness(out)
        qa.update(lufs=i, true_peak=tp, lufs_ok=abs(i - m.get("lufs", -14)) <= 1.0, peak_ok=tp <= -1.0)
    (out.parent / "qa.json").write_text(json.dumps(qa, indent=2))
    print(json.dumps(qa))
    if not all(v for k, v in qa.items() if k.endswith("_ok")):
        sys.exit(1)


if __name__ == "__main__":
    main()
