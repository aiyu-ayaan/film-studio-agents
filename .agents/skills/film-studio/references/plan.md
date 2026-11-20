# plan.json: the single source of truth

One per project, at `<project>/plan.json`. Every stage reads and writes it. Paths are relative to the project folder.

```json
{
  "title": "Why bees dance",
  "master": {
    "width": 1920, "height": 1080, "fps": 30,
    "speech": true,
    "voice_engine": "kokoro",          // kokoro | pocket only. Empty = ask the user
    "voice": "af_heart",               // engine voice id, or a wav path to clone (pocket)
    "lead_in_s": 0.4,                  // silence before the first line
    "gap_s": 0.35,                     // default pause between lines
    "tail_s": 1.2,                     // after the last line
    "cut_lead_s": 0.1,                 // cut this long before a scene's first line
    "asr_min_ratio": 0.85,             // per-line script match needed
    "captions": "clean",              // film-captions style: clean | karaoke | box | punch | none
    "lufs": -14, "true_peak": -1.5, "crf": 12,
    "cut_on": "beat"                   // no-speech: beat | bar
  },
  "lines": [
    {"id": "l1", "text": "So... ever watched a bee dance?", "pause_after_s": 0.5}
  ],
  "scenes": [
    {"id": "s1", "skill": "motionmaxxing", "line_ids": ["l1"],
     "brief": "Kinetic type hook: the word DANCE swings like a waggle run",
     "recipe": {"precedent": ["PM913"], "camera": "slow push-in, 3 deg orbit",
                "blueprint": "kinetic-type-beats", "registry": ["grain-overlay"],
                "shot_card": null, "style": null, "record": null},   // keys per skill: references/adapters.md "Recipe"
     "clip": "scenes/s1/clip.mp4",
     "sfx_stem": null,                 // optional wav aligned to the scene's t=0
     "seconds": 4                      // no-speech only: wanted length before beat snapping
    }
  ],
  "music": {"path": "audio/music/bed.wav", "licence": "CC0 (VSCO 2 CE) + CC BY 3.0 (Salamander)",
            "credit": "Piano: \"Salamander Grand Piano V3\" by Alexander Holm, CC BY 3.0", "gain_db": -8},
  "sfx": [{"path": "audio/sfx/whoosh.wav", "t": 4.1, "gain_db": -6}]
}
```
(Comments above are for reading; real JSON has none.)

## Written by the scripts

| Field | Written by | Meaning |
|---|---|---|
| `lines[].start_s/end_s` | narrate.py | Line position in `audio/vo/vo.wav` |
| `lines[].asr_ratio/asr_ok` | narrate.py | Script vs what the transcriber heard. Set `lines[].asr_min_ratio` (e.g. 0.78) only when the miss is a brand-name spelling |
| `scenes[].start_s/end_s/start_f/frames` | narrate.py or timing.py | Frame-exact cut points. Do not edit by hand |
| `master.duration_s/total_frames` | narrate.py or timing.py | Film length |

## Files a project ends with

```
plan.json  BRIEF.md  script.md  style.md  STORYBOARD.md  NOTE.md
audio/vo/lines/<id>.wav  audio/vo/vo.wav  vo.words.json  vo.srt
audio/music/bed.wav (+ beats.json in no-speech)   audio/sfx/*.wav
scenes/<id>/...  scenes/<id>/clip.mp4
build/assemble/  (intermediates)
renders/final.mp4 (the film: captioned in place when master.captions != none)  .clean/final.mp4 (clean master)  final.srt  qa.json  contact.png
```
