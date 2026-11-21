---
name: film-idea-score
description: Score a video idea (or a list of ideas) out of 100 before making it, for an Instagram Reels + YouTube Shorts channel. Rates nine criteria from the 2026 platform signals (proof from outliers, 3-second hook, shareability, legibility, payoff/loop, own angle, channel fit, makeable by this studio, series legs), then gives MAKE / FIX / PARK / KILL and the one thing to fix. Use when the user says "score my idea", "rate this idea", "is this worth making", "which idea should I make", "rank these ideas", or before stage 1 of /film-studio for a channel video.
---

# film-idea-score

Scores ideas, not hooks or finished videos. Run it before `/film-studio` stage 1.
Background and sources: `research/viral-roadmap.md` (sections 2 and 3).

The score is a structured judgment, not a prediction. A high score means the idea avoids the known ways short videos fail. It never promises views.

## Step 1: load the channel profile

Read `channel/profile.md`. If it does not exist, ask these three questions in one message, then write the file:

1. Niche and promise in one line ("How machines work, explained in 30 seconds of 3D").
2. Who it is for (one specific viewer).
3. Three to five accounts or channels near your size that you admire.

The `fit` criterion is judged against this file. Update it when the user changes direction.

## Step 2: get evidence for `proof`

Look for a swipe file in `channel/swipe.md` (made by `/ig-viral` or `/yt-viral` if installed, or by hand).
If an idea matches a pattern there that beat its account's median by 3x or more, `proof` can be 7 to 10.
With no evidence, `proof` is at most 3. Do not invent view numbers. Say which row you matched, or say there is none.

## Step 3: rate each criterion 0 to 10

Write one line of evidence per criterion. Be harsh: a 7 means clearly good, not "fine".

| Key | Weight | Question |
|---|---|---|
| `proof` | 15 | Did a similar idea beat its own account's median by 3x+? |
| `hook` | 15 | Can a stranger be hooked in 3 s by a concrete line plus on-screen text? Write the best hook you can; rate that. |
| `share` | 15 | Name the one person a viewer would DM it to. No name, low score. |
| `legible` | 10 | Is the topic clear in 1 s with sound off, to a stranger? |
| `payoff` | 10 | Is there a turn or reveal that holds to the end, and a loop back to the hook? |
| `angle` | 10 | Own research, data or human angle? A rehash of a common video scores 2 or less. |
| `fit` | 10 | Does it fit the promise in `channel/profile.md`? |
| `make` | 10 | Can this studio make it in code in about a day (HyperFrames, 3DViz, Lemo-Opuscar, Motionmaxxing, our TTS)? Needing real faces, real footage or someone else's trademark scores 2 or less. |
| `legs` | 5 | Part 2 or series potential, searchable, works on both IG and YT vertical? |

Add a dealbreaker for anything that should stop the idea outright: a third-party logo or character without rights, a claim you cannot back up, a payoff the video cannot deliver, a copy of someone else's video. `angle` or `make` at 2 or less is a dealbreaker automatically.

## Step 4: run the scorer

Write the ratings to a JSON file in the scratchpad (one object, or a list to rank several):

```json
{
  "idea": "Why jet engines suck, squeeze, bang, blow, in 30 s of 3D",
  "scores": {"proof": 6, "hook": 8, "share": 6, "legible": 9, "payoff": 7,
             "angle": 5, "fit": 9, "make": 9, "legs": 8},
  "notes": {"proof": "swipe row 4: engine cutaway did 5.2x", "share": "the friend who flies a lot"},
  "dealbreakers": []
}
```

```bash
python3 .agents/skills/film-idea-score/scripts/score.py ideas.json
python3 .agents/skills/film-idea-score/scripts/score.py --selftest
```

Verdicts: **MAKE** at 75 or more. **FIX** at 60 to 74: rewrite the idea to lift the weakest criterion, then rescore (at most two rounds). **PARK** under 60. **KILL** if any dealbreaker.

## Step 5: report

Show the script's ranking as is. Then, for each idea, give:
- the verdict and total,
- the weakest criterion and a concrete rewrite that fixes it (a new angle, a sharper hook line, a named share target),
- for MAKE: the best hook line, ready for `/film-studio`.

Append every scored idea to `channel/ideas.md` as one line: date, total, verdict, idea. That file is the backlog. After a video is posted, add its real result to the same line so future `proof` ratings can use it.
