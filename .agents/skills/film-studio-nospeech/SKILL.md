---
name: film-studio-nospeech
description: Produce one finished film with no narration by combining several video skills scene by scene, cut to the beat of a music track, with on-screen text carrying the story, plus SFX and a loudness-checked mix. Use for music-led promos, launch teasers, brand reels and silent social clips in the Movies studio. For a narrated film use film-studio (the default).
argument-hint: "[topic, brief or path to BRIEF.md]"
---

# film-studio-nospeech

Read and follow `/media/aiyu/550E85595197DBEC/Personal/Movies/.claude/skills/film-studio/SKILL.md` and its `references/`. Everything there applies, with these differences only:

| Stage | Change |
|---|---|
| Setup | `plan.master.speech: false`, `voice_engine: ""`, `captions: "none"`. Skip stage 6b (no voice, so no captions). |
| 1. Story | No narration lines (`lines` absent). Write the story as on-screen text beats: 2-6 words each, one idea per beat, read time about 0.3 s per word + 0.5 s. The text IS the story, so it must make sense alone. |
| 2. Storyboard | Each scene gets `seconds` (wanted length) and the text it shows. Kinetic type (Motionmaxxing) and HyperFrames text effects fit best. |
| 3. Timing | Music first: choose the track (licence ladder in `references/audio.md`) and save it to `audio/music/bed.wav`. Then `python3 .claude/skills/film-studio/scripts/timing.py <project>`: cuts snap to beats (`master.cut_on: "bar"` for slower cuts). No voice step. |
| 4. Scenes | Same adapters, same `recipe` and `scene_check.py` gates. Land key text hits on beats: `audio/music/beats.json` has the beat times (use them where speech films use `words`). |
| 5. Sound | Music is the lead: `music.gain_db` about -1. SFX sit on cuts and text hits. |
| 6. Assemble | Same `assemble.py`; it skips voice and ducking when `speech` is false. |
| 8. Deliver | No `.srt`. Text must be readable at phone size without sound. |
