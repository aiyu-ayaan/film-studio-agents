#!/usr/bin/env python3
"""Score video ideas for an Instagram Reels + YouTube Shorts channel.

The agent rates each criterion 0-10 with one line of evidence; this script does the
math the same way every time: weighted total out of 100, verdict, weakest criterion,
dealbreakers. Input is one idea object or a list of them (ranked on output).

  python3 score.py ideas.json            # table + detail
  python3 score.py ideas.json --json     # machine-readable
  python3 score.py --selftest
"""
import json
import sys

# weight, question the agent must answer. Weights sum to 100.
# Sources: research/viral-roadmap.md section 2 (platform signals) and section 3 (studio rules).
CRITERIA = {
    "proof":  (15, "Did a similar idea beat its own account's median by 3x+ (swipe file)? 0 = no evidence"),
    "hook":   (15, "Can a stranger be hooked in the first 3 s with a concrete line and on-screen text?"),
    "share":  (15, "Is there one specific person a viewer would DM it to? (sends per reach)"),
    "legible": (10, "Is the topic clear in 1 s, sound off, to someone who never heard of you?"),
    "payoff": (10, "Is there a turn or payoff that holds 70%+ to the end, and a loop back to the hook?"),
    "angle":  (10, "Own research, data or human angle? Not a template or rehash (YouTube demonetizes those)"),
    "fit":    (10, "Does it fit the channel promise in channel/renderstand/profile.md, so viewers follow?"),
    "make":   (10, "Can this studio make it in code in about a day? No real faces, footage or trademarks needed"),
    "legs":   (5,  "Does it have a part 2 / series, stay searchable, and work on both IG and YT?"),
}
assert sum(w for w, _ in CRITERIA.values()) == 100

# A score this low on these criteria kills the idea whatever the total says.
HARD_FLOORS = {
    "angle": "No own angle: template content gets demonetized and cut from cold reach.",
    "make": "The studio cannot make it (needs footage, faces or rights we do not have).",
}
MAKE, FIX = 75, 60


def score(idea):
    s = idea.get("scores", {})
    missing = [k for k in CRITERIA if k not in s]
    if missing:
        raise ValueError(f"{idea.get('idea', '?')}: missing scores for {', '.join(missing)}")
    for k, v in s.items():
        if k not in CRITERIA:
            raise ValueError(f"unknown criterion '{k}' (allowed: {', '.join(CRITERIA)})")
        if not isinstance(v, (int, float)) or not 0 <= v <= 10:
            raise ValueError(f"{k} must be a number 0-10, got {v!r}")
    total = round(sum(CRITERIA[k][0] * s[k] / 10 for k in CRITERIA), 1)
    deal = list(idea.get("dealbreakers", []))
    deal += [msg for k, msg in HARD_FLOORS.items() if s[k] <= 2]
    # weakest = biggest points lost, so fixing it gains the most
    weakest = max(CRITERIA, key=lambda k: CRITERIA[k][0] * (10 - s[k]))
    verdict = "KILL" if deal else "MAKE" if total >= MAKE else "FIX" if total >= FIX else "PARK"
    return {"idea": idea.get("idea", "?"), "total": total, "verdict": verdict,
            "weakest": weakest, "points_lost": round(CRITERIA[weakest][0] * (10 - s[weakest]) / 10, 1),
            "dealbreakers": deal, "scores": s, "notes": idea.get("notes", {})}


def report(results):
    out = ["IDEA RANKING", "=" * 78]
    for r in results:
        out.append(f"{r['total']:5.1f}  {r['verdict']:<4}  {r['idea'][:62]}")
    for r in results:
        out += ["", "-" * 78, f"{r['idea']}", f"  TOTAL {r['total']}/100  ->  {r['verdict']}"]
        for k, (w, _) in CRITERIA.items():
            note = r["notes"].get(k, "")
            out.append(f"  {k:<8} {r['scores'][k]:>4}/10  x{w:<3} {note[:52]}")
        out.append(f"  weakest: {r['weakest']} (costs {r['points_lost']} points). Fix this first.")
        for d in r["dealbreakers"]:
            out.append(f"  DEALBREAKER: {d}")
    out += ["", f"MAKE >= {MAKE}  ·  FIX {FIX}-{MAKE - 1} (rewrite the weakest, rescore)  ·  "
            f"PARK < {FIX}  ·  KILL = dealbreaker"]
    return "\n".join(out)


def selftest():
    good = {"idea": "g", "scores": {k: 9 for k in CRITERIA}}
    assert score(good)["total"] == 90 and score(good)["verdict"] == "MAKE"
    mid = {"idea": "m", "scores": {**{k: 7 for k in CRITERIA}, "proof": 4}}
    r = score(mid)
    assert r["verdict"] == "FIX" and r["weakest"] == "proof", r
    bad = {"idea": "b", "scores": {**{k: 9 for k in CRITERIA}, "angle": 2}}
    assert score(bad)["verdict"] == "KILL"
    assert score({"idea": "d", "scores": good["scores"], "dealbreakers": ["x"]})["verdict"] == "KILL"
    assert score({"idea": "p", "scores": {k: 5 for k in CRITERIA}})["verdict"] == "PARK"
    for broken in ({"scores": {"hook": 5}}, {"scores": {**good["scores"], "hook": 11}}):
        try:
            score(broken)
        except ValueError:
            continue
        raise AssertionError("bad input accepted")
    print("selftest ok")


def main(argv):
    if "--selftest" in argv:
        return selftest()
    paths = [a for a in argv if not a.startswith("--")]
    if len(paths) != 1:
        sys.exit(__doc__)
    data = json.load(open(paths[0]))
    ideas = data if isinstance(data, list) else [data]
    results = sorted((score(i) for i in ideas), key=lambda r: (r["verdict"] != "KILL", r["total"]), reverse=True)
    print(json.dumps(results, indent=2) if "--json" in argv else report(results))


if __name__ == "__main__":
    main(sys.argv[1:])
