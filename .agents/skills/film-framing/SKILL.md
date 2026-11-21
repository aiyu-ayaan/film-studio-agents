---
name: film-framing
description: Give a film a frame - an intro (cold open, title, roadmap), a bridge at every topic change (close the last section, ask the question the next one answers, chapter card), and an outro that pays off the intro. Fixes films that start cold and jump between topics (why > what > where > now) with no transition. Add-on to film-studio and film-studio-nospeech, used at stages 1, 2 and 5. Use when the user asks for an intro, chapters, sections, smoother topic changes, or "framing".
---

# film-framing

An add-on to `/film-studio` (and `-nospeech`). It changes what the script and storyboard contain. It never changes the scripts' timing math or the assembler: intro, bridges and outro are ordinary lines and scenes.

Apply it when the user asks for it (the Studio app's "Intro and chapter bridges" box, or words like intro, chapters, sections, smoother transitions). For a film with 3+ topic sections or over 3 minutes, offer it once at gate G1 if it was not asked for.

## Why films felt abrupt

A long film made of sections (for example History of C: why, what, where, now) cut from the last fact of one section straight to the first fact of the next. Nothing said "this part is done, here is the next question", and nothing on screen marked the change. Viewers lose the thread at every cut. There was also no opening: the film began on its first fact.

The fix has three parts. **Intro** sets the question and the map. **Bridges** close one chapter and open the next. **Outro** answers the intro.

## Stage 1: script

Plan chapters first: 2-6 chapters, each one question the film answers ("Why was C made?"). Write `chapters[]` into plan.json (format below). Then write lines with these beats.

**Intro** (3-8% of the film; 4-6 s for films under 90 s, 15-25 s for a 10-minute film):
1. Cold open: the most surprising fact or image from a later chapter, as a question or a contradiction. "Your phone, your car and the Mars rover all run on a language from 1972."
2. The film's question: "So how did a fifty-year-old language end up running everything?"
3. Roadmap: name the chapters in plain words, in order, in one sentence. "We'll see why it was born, what it really is, where it runs, and where it's heading." Short films (under 2 minutes) skip the roadmap.

**Bridge** at every chapter change: two lines that straddle the boundary.
- Exit line (last line of the chapter): one-sentence takeaway. "So C was born to make Unix portable." Set `pause_after_s` 0.6-0.9 so the chapter card has air.
- Entry line (first line of the next chapter): turn the takeaway into the next question. Pick one pattern and vary it across bridges:
  - Callback + question: "Portable, sure. But what actually *is* C?"
  - Consequence: "And that speed came with a price."
  - Contrast: "That was 1978. Today the picture looks very different."
  - Zoom: "To see why, we need to look inside a single line of C."
- Never open a chapter with a new fact and no entry line.

**Outro**: one line that answers the intro question, an optional one-line recap of the chapters (callback to the roadmap), then the call to action.

Follow "Make any TTS sound human" in `research/tts.md` for every bridge line too: contractions, short sentences, a pause where a person would breathe.

## Stage 2: storyboard

Scene roles. Add `"role"` and `"chapter"` to each scene. narrate.py, scene_check.py and assemble.py ignore these keys; `framing_check.py` reads them.

| Role | What is on screen | Length | Owns lines |
|---|---|---|---|
| `intro` | Cold open: the film's strongest visual, taken from a later chapter. Then the title: film title lands on a music hit. Then the roadmap: the chapter titles appear as a row of marks (the **chapter motif**). | 1-3 scenes | Cold open, question, roadmap |
| `card` | Chapter card: the motif with this chapter's mark lit, chapter number and title. One design for all cards. | 2.5-4 s | The entry line (the question) |
| (none) | Normal content scenes of the chapter. | as film-studio | Chapter body, exit line |
| `outro` | Payoff visual, the motif with every mark lit, end card. | 1-2 scenes | Payoff, recap, CTA |

Rules:
- **One card template.** Build the chapter card once as a HyperFrames composition with variables (number, title, lit mark). Render one clip per chapter from it. Each card scene's `recipe` names the same `blueprint` and `registry` blocks. Search: `node ~/.claude/skills/hyperframes/scripts/plugin-cli.mjs catalog --query "chapter title card" --json`.
- **The motif is the thread.** The roadmap marks in the intro, the lit mark on each card and the full row in the outro are the same shapes, colours and positions. Take them from `style.md` (accent colour, display font). Write the motif into `style.md` under "Chapter motif".
- **Cards show titles, not the spoken sentence.** The card shows "02 What C is"; the narration asks the question. Captions carry the spoken words (film-studio rule: on-screen text never repeats the narration).
- **Transitions into and out of a card.** The film-studio rule stays: hard cuts on motion, no fade to black. A chapter change may use one designed transition: a whip pan, a match cut (an object from the last content shot becomes the card's mark), or a push through the card. Use a registry transition block, the same one at every chapter change: `catalog --query "whip pan transition" --json`.
- **The motif appears only in intro, cards and outro.** It is never an overlay on content scenes. A chapter bar in a corner is page chrome, and the quality bar forbids it.
- The cold-open visual must come from a later chapter's best moment, so build or reuse that scene first.

## Stage 5: sound at the seams

Same sounds at every chapter change, so the ear learns the pattern. Earshot bank ids, checked 2026-11-21:
- Into a card: `riser/snatch` or `reverse_swell/short`, peak on the cut. `earshot sfx render reverse_swell/short -o audio/sfx/into_card.wav --dur 0.7`
- Card title lands: `cut_hit/air` or `cut_hit/sub`, low gain (-10 dB).
- Title in the intro: `impact/swell` on the title hit.
- Music: change phrase at the chapter boundary if the bed has sections (cut on a bar line, `beats_of` in film-studio scripts), or duck the bed about 4 dB under the card and swell back on the first content scene.
Put each one in `plan.sfx[]` at the card scene's `start_s`.

## plan.json additions

```json
"chapters": [
  {"id": "c1", "title": "Why C was born", "question": "Why was C made?", "scene_ids": ["s3", "s4", "s5"]},
  {"id": "c2", "title": "What C is", "question": "What actually is C?", "scene_ids": ["c2card", "s6", "s7"]}
],
"scenes": [
  {"id": "s1", "role": "intro", "line_ids": ["l1", "l2"], "...": "..."},
  {"id": "c2card", "role": "card", "chapter": "c2", "line_ids": ["l9"], "...": "..."}
]
```
The first chapter may start right after the intro without a card when the roadmap already named it. Every later chapter starts with its card.

## Gate

Before G1: `python3 .agents/skills/film-framing/scripts/framing_check.py <project>`. Exit 0, or fix what it prints. It checks: the film opens with an intro scene and closes with an outro scene, there are 2+ chapters, every scene belongs to exactly one chapter or is intro/outro, chapters are in film order, every chapter after the first opens with a card, each card owns its entry line (speech films), and the exit line before each card has `pause_after_s` of at least 0.5. The wording of entry lines is not checked: read them aloud.
Self-test: `framing_check.py --selftest`.
