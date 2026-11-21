#!/usr/bin/env python3
"""Gate for stage 2 and 4: every scene has a recipe, and every clip is the right size, long enough and alive.

Usage: scene_check.py <project> [--only s2,s3] [--recipes-only] [--max-frozen 0.4]
Exit 0 = all pass, 1 = a scene failed (reasons printed).

Frozen time: ffmpeg freezedetect (n=0.003, d=0.5) on a 160 px blurred copy, so animated grain does not
count as motion (unblurred, a grain layer made a still SVG read 0% frozen). The last scene may hold
up to 1.4 s at its end (end-card hold). Calibrated 2026-11-20 on all 30 past clips: live scenes
0-26% frozen, flat held scenes 49-100%; limit 40%.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

S = Path.home() / ".claude/skills"
HERK = Path.home() / ".local/share/skill-src/herk-edit-kit"


def herk_cards():
    reg = HERK / "style-library/registry.json"
    if not reg.exists():
        return set()
    return {c["id"] for st in json.loads(reg.read_text())["styles"] for c in st["cards"]}


EXISTS = {  # recipe ids that must name a real file, so ids cannot be invented. (value, project) -> bool
    "blueprint": lambda v, p: (S / "hyperframes-animation/blueprints" / f"{v}.md").exists(),
    "style": lambda v, p: (Path.home() / "lemo-opuscar/styles" / v / "STYLE.md").exists(),
    "shot_card": lambda v, p: any((S / "video-shotcraft/demos").glob(f"*/{v}")),
    "card": lambda v, p: v in herk_cards(),
    "footage": lambda v, p: (p / v).is_file(),  # a downloaded clip inside the project; licence goes in NOTE.md
}

NEED = {  # recipe keys a scene must name, by skill family
    "hyperframes": ["blueprint", "registry", "camera"],
    "shotcraft": ["shot_card", "camera"],
    "motionmaxxing": ["precedent", "camera"],
    "lemo-opuscar": ["style"],
    "3dviz": ["record", "camera"],
    "remotion": ["camera"],
    "herk": ["card", "camera"],
    "openmontage": ["footage", "camera"],
}


def family(skill):
    s = (skill or "").lower()
    for k in NEED:
        if k.split("-")[0] in s:
            return k
    return "hyperframes"


def probe(clip):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                          "-show_entries", "stream=width,height,r_frame_rate,nb_read_packets",
                          "-of", "json", str(clip)], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return s["width"], s["height"], float(n) / float(d), int(s["nb_read_packets"])


def frozen_fraction(clip, frames, fps, end_hold=0.0):
    dur = frames / fps
    log = subprocess.run(["ffmpeg", "-hide_banner", "-t", f"{dur:.3f}", "-i", str(clip), "-vf",
                          "scale=160:-2,gblur=sigma=2,freezedetect=n=0.003:d=0.5", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", log)]
    ends += [dur] * (len(starts) - len(ends))  # a freeze still open at the end runs to the end
    spans = list(zip(starts, ends))
    if spans and end_hold and spans[-1][1] >= dur - 0.05:  # forgive the end-card hold
        s, e = spans[-1]
        spans[-1] = (s, max(s, e - end_hold))
    return sum(e - s for s, e in spans) / dur


def check(proj, sc, m, recipes_only, max_frozen, last=False):
    bad = []
    fam = family(sc.get("skill"))
    rec = sc.get("recipe") or {}
    miss = [k for k in NEED[fam] if not rec.get(k)]
    if miss:
        bad.append(f"recipe missing {miss} for {fam}")
    for k, ok in EXISTS.items():
        if rec.get(k) and not ok(rec[k], proj):
            bad.append(f"recipe {k}={rec[k]!r} not found in the installed skill")
    if recipes_only:
        return bad
    clip = proj / sc.get("clip", f"scenes/{sc['id']}/clip.mp4")
    if not clip.exists():
        return bad + [f"no clip {clip}"]
    w, h, fps, n = probe(clip)
    if (w, h) != (m["width"], m["height"]):
        bad.append(f"size {w}x{h} != {m['width']}x{m['height']}")
    if abs(fps - m["fps"]) > 0.01:
        bad.append(f"fps {fps:g} != {m['fps']}")
    frames = sc.get("frames") or n
    if n < frames:
        bad.append(f"{n} frames < {frames} needed")
    fr = frozen_fraction(clip, min(n, frames), m["fps"], 1.4 if last else 0.0)
    if fr > max_frozen:
        bad.append(f"frozen {fr:.0%} of the scene (max {max_frozen:.0%}): add continuous motion or a camera move")
    else:
        print(f"  {sc['id']}: frozen {fr:.0%}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--only")
    ap.add_argument("--recipes-only", action="store_true")
    ap.add_argument("--max-frozen", type=float, default=0.4)
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    plan = json.loads((proj / "plan.json").read_text())
    only = set(a.only.split(",")) if a.only else None
    fails = 0
    for sc in plan["scenes"]:
        if only and sc["id"] not in only:
            continue
        bad = check(proj, sc, plan["master"], a.recipes_only, a.max_frozen, sc is plan["scenes"][-1])
        print(f"{'FAIL' if bad else 'OK  '} {sc['id']} {sc.get('skill')}" + ("".join(f"\n    - {b}" for b in bad)))
        fails += bool(bad)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
