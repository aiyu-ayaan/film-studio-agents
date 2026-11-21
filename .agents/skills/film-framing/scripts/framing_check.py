#!/usr/bin/env python3
"""Gate for film-framing: the film has an intro, chapters with cards, and an outro.

Usage: framing_check.py <project>      exit 0 = pass, 1 = problems printed
       framing_check.py --selftest
Reads only plan.json. Standard library only.
"""
import json, sys
from pathlib import Path


def check(plan):
    bad = []
    scenes = plan.get("scenes") or []
    chapters = plan.get("chapters") or []
    speech = (plan.get("master") or {}).get("speech", True) is not False
    lines = {l.get("id"): l for l in plan.get("lines") or []}
    order = [s.get("id") for s in scenes]
    if not scenes:
        return ["no scenes in plan.json"]
    if scenes[0].get("role") != "intro":
        bad.append(f"first scene {order[0]} is not role=intro")
    if scenes[-1].get("role") != "outro":
        bad.append(f"last scene {order[-1]} is not role=outro")
    if len(chapters) < 2:
        bad.append(f"{len(chapters)} chapters; framing needs 2 or more")

    owner = {}
    for c in chapters:
        for sid in c.get("scene_ids") or []:
            if sid in owner:
                bad.append(f"scene {sid} is in chapters {owner[sid]} and {c.get('id')}")
            owner[sid] = c.get("id")
            if sid not in order:
                bad.append(f"chapter {c.get('id')} names unknown scene {sid}")
    for s in scenes:
        if s.get("role") in ("intro", "outro"):
            if s.get("id") in owner:
                bad.append(f"{s['role']} scene {s['id']} must not be inside a chapter")
        elif s.get("id") not in owner:
            bad.append(f"scene {s.get('id')} belongs to no chapter")

    # chapters in film order, each a contiguous run
    pos = [[order.index(x) for x in c.get("scene_ids") or [] if x in order] for c in chapters]
    for c, p in zip(chapters, pos):
        if p and p != list(range(p[0], p[0] + len(p))):
            bad.append(f"chapter {c.get('id')} scenes are not consecutive in the film")
    starts = [p[0] for p in pos if p]
    if starts != sorted(starts):
        bad.append("chapters are not in film order")

    for i, (c, p) in enumerate(zip(chapters, pos)):
        if i == 0 or not p:
            continue
        card = scenes[p[0]]
        if card.get("role") != "card":
            bad.append(f"chapter {c.get('id')} opens with {card.get('id')}, not a role=card scene")
            continue
        if card.get("chapter") not in (None, c.get("id")):
            bad.append(f"card {card.get('id')} says chapter {card.get('chapter')}, but sits in {c.get('id')}")
        if speech:
            if not card.get("line_ids"):
                bad.append(f"card {card.get('id')} owns no line: give it the chapter's entry line")
            prev = scenes[p[0] - 1].get("line_ids") or []
            exit_line = lines.get(prev[-1]) if prev else None
            if exit_line is not None and exit_line.get("pause_after_s", 0) < 0.5:
                bad.append(f"exit line {exit_line.get('id')} before card {card.get('id')} needs pause_after_s >= 0.5")
    return bad


def selftest():
    good = {
        "master": {"speech": True},
        "lines": [{"id": f"l{i}", "text": "x", "pause_after_s": 0.7} for i in range(1, 7)],
        "chapters": [{"id": "c1", "scene_ids": ["s2"]}, {"id": "c2", "scene_ids": ["k2", "s3"]}],
        "scenes": [
            {"id": "s1", "role": "intro", "line_ids": ["l1"]},
            {"id": "s2", "line_ids": ["l2"]},
            {"id": "k2", "role": "card", "chapter": "c2", "line_ids": ["l3"]},
            {"id": "s3", "line_ids": ["l4"]},
            {"id": "s9", "role": "outro", "line_ids": ["l5"]},
        ],
    }
    assert check(good) == [], check(good)
    bad = json.loads(json.dumps(good))
    bad["scenes"][2]["role"] = None
    bad["lines"][1]["pause_after_s"] = 0.2
    del bad["scenes"][-1]["role"]
    msgs = check(bad)
    assert any("not a role=card" in m for m in msgs), msgs
    assert any("not role=outro" in m for m in msgs), msgs
    bad2 = json.loads(json.dumps(good))
    bad2["lines"][1]["pause_after_s"] = 0.2
    assert any("pause_after_s" in m for m in check(bad2)), check(bad2)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        sys.exit(0)
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    plan = json.loads((Path(sys.argv[1]) / "plan.json").read_text())
    problems = check(plan)
    for p in problems:
        print(f"FAIL {p}")
    print("OK   framing" if not problems else f"{len(problems)} framing problem(s)")
    sys.exit(1 if problems else 0)
