#!/usr/bin/env python3
"""Stage 3 (no-speech mode): time the scenes to the music's beat grid.

Reads plan.json: master.fps, music.path, scenes[].seconds (wanted length).
Runs `npx hyperframes beats <music>` and snaps every cut to the nearest beat
(to a bar line if master.cut_on = "bar"). Writes scenes[].start_s/end_s/start_f/frames,
master.duration_s/total_frames, and audio/music/beats.json.

Usage: timing.py <project_dir>
"""
import json, os, subprocess, sys
from pathlib import Path


def beats_of(music):
    env = dict(os.environ)
    env.setdefault("HYPERFRAMES_CACHE_DIR", str(Path.home() / ".local/share/hyperframes-cache"))
    r = subprocess.run(["npx", "-y", "hyperframes", "beats", str(music), "--json"], capture_output=True, text=True, env=env)
    if r.returncode:
        sys.exit(f"beats failed: {r.stderr[-800:]}")
    return json.loads(r.stdout)


def beat_times(data):
    # Accept the shapes the CLI may print: {"beats":[t...]} or {"beats":[{"time":t}...]} or nested result.
    for key in ("beats", "beatTimes", "beat_times"):
        for d in (data, data.get("result", {}) if isinstance(data, dict) else {}):
            v = d.get(key) if isinstance(d, dict) else None
            if v:
                return [b if isinstance(b, (int, float)) else b.get("time", b.get("t")) for b in v]
    sys.exit(f"no beat list in beats output; keys: {list(data)[:10]}")


def main():
    proj = Path(sys.argv[1]).resolve()
    plan_p = proj / "plan.json"
    plan = json.loads(plan_p.read_text())
    m, fps = plan["master"], plan["master"]["fps"]
    music = proj / plan["music"]["path"]
    data = beats_of(music)
    (proj / "audio" / "music").mkdir(parents=True, exist_ok=True)
    (proj / "audio" / "music" / "beats.json").write_text(json.dumps(data, indent=1))
    grid = sorted(beat_times(data))
    if m.get("cut_on") == "bar":
        grid = grid[::4]
    snap = lambda t: min(grid, key=lambda b: abs(b - t)) if grid else t

    t, cuts = 0.0, [0.0]
    for sc in plan["scenes"][:-1]:
        t += sc.get("seconds", 4)
        cuts.append(max(snap(t), cuts[-1] + 1 / fps))
        t = cuts[-1]
    end = snap(t + plan["scenes"][-1].get("seconds", 4))
    total = round(max(end, cuts[-1] + 1), 3)
    for i, sc in enumerate(plan["scenes"]):
        sc["start_s"] = round(cuts[i], 3)
        sc["end_s"] = round(cuts[i + 1], 3) if i + 1 < len(cuts) else total
        sc["start_f"] = round(sc["start_s"] * fps)
        sc["frames"] = round(sc["end_s"] * fps) - sc["start_f"]
    m["duration_s"], m["total_frames"] = total, round(total * fps)
    plan_p.write_text(json.dumps(plan, indent=2))
    print(f"{len(grid)} grid points, {total:.2f}s")
    for sc in plan["scenes"]:
        print(f"  {sc['id']:>6} {sc['skill']:<14} {sc['start_s']:7.2f}s  {sc['frames']:5d} frames")


if __name__ == "__main__":
    main()
