#!/usr/bin/env bash
# Self-test for narrate.py / timing.py / assemble.py with fake scene clips.
# Usage: selftest.sh [work_dir]   (default: a temp dir). Needs ffmpeg, npx hyperframes, Movies/.venv (Kokoro).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=${1:-$(mktemp -d)}
rm -rf "$W/speech" "$W/silent"; mkdir -p "$W/speech/scenes" "$W/speech/audio/music"

# Three scene clips that disagree on size, fps and length, one solid colour each so cuts are measurable.
mk() { ffmpeg -y -v error -f lavfi -i "color=c=$2:s=$3:r=$4:d=$5" -f lavfi -i "sine=f=1000:d=$5" -shortest "$1"; }
mk "$W/speech/scenes/a.mp4" red   1280x720  24 2   # too short: must be held
mk "$W/speech/scenes/b.mp4" lime  1920x1080 30 9   # too long: must be cut
mk "$W/speech/scenes/c.mp4" blue  1080x1920 25 6   # wrong aspect: must be padded
# Music bed: two-tone pad, 6 s, looped by the assembler.
ffmpeg -y -v error -f lavfi -i "sine=f=220:d=6" -f lavfi -i "sine=f=330:d=6" -filter_complex amix=inputs=2 "$W/speech/audio/music/bed.wav"

cat > "$W/speech/plan.json" <<'JSON'
{
  "title": "selftest",
  "master": {"width": 1920, "height": 1080, "fps": 30, "speech": true, "voice_engine": "kokoro", "voice": "af_heart",
             "captions": "karaoke", "lufs": -14, "true_peak": -1.5},
  "lines": [
    {"id": "l1", "text": "So, here's a quick test."},
    {"id": "l2", "text": "The second scene starts right on this line."},
    {"id": "l3", "text": "And the last one closes it out."}
  ],
  "scenes": [
    {"id": "s1", "skill": "test", "line_ids": ["l1"], "clip": "scenes/a.mp4"},
    {"id": "s2", "skill": "test", "line_ids": ["l2"], "clip": "scenes/b.mp4"},
    {"id": "s3", "skill": "test", "line_ids": ["l3"], "clip": "scenes/c.mp4"}
  ],
  "music": {"path": "audio/music/bed.wav", "licence": "test tone", "credit": ""},
  "sfx": []
}
JSON

python3 "$HERE/../../film-captions/scripts/captions.py" --selftest
python3 "$HERE/narrate.py" "$W/speech"
python3 "$HERE/assemble.py" "$W/speech"
python3 "$HERE/../../film-captions/scripts/captions.py" "$W/speech/renders/final.mp4" "$W/speech/renders/final.captioned.mp4" \
  --words "$W/speech/audio/vo/vo.words.json" --style karaoke

# Colour at frame n of the final film (rgb of a 1x1 downscale).
rgb() { ffmpeg -v error -i "$1" -vf "select=eq(n\,$2),scale=1:1" -frames:v 1 -f rawvideo -pix_fmt rgb24 - | od -An -tu1 | tr -s ' '; }
python3 - "$W/speech" <<'PY'
import json, subprocess, sys
from pathlib import Path
p = Path(sys.argv[1]); plan = json.loads((p / "plan.json").read_text()); film = p / "renders/final.mp4"
def rgb(n):
    out = subprocess.run(["ffmpeg","-v","error","-i",str(film),"-vf",f"select=eq(n\\,{n}),scale=1:1","-frames:v","1",
                          "-f","rawvideo","-pix_fmt","rgb24","-"], capture_output=True).stdout
    return tuple(out[:3])
dom = lambda c: max(range(3), key=lambda i: c[i])   # 0 red, 1 green, 2 blue
for i, sc in enumerate(plan["scenes"][1:], 1):
    f = sc["start_f"]
    before, at = dom(rgb(f - 1)), dom(rgb(f))
    assert before == i - 1 and at == i, f"cut {sc['id']} not at frame {f}: before {before}, at {at}"
    # Cut sits just before its line starts (cut_lead_s), never after it.
    line = next(l for l in plan["lines"] if l["id"] == sc["line_ids"][0])
    assert 0 <= line["start_s"] - f / plan["master"]["fps"] <= 0.2, "cut not just before its line"
qa = json.loads((p / "renders/qa.json").read_text())
assert qa["frames_ok"] and qa["lufs_ok"] and qa["peak_ok"], qa
words = json.loads((p / "audio/vo/vo.words.json").read_text())
srt = (p / "renders/final.srt").read_text().split("\n")
assert srt[1].startswith("00:00:00,") and abs(int(srt[1][6:8]) + int(srt[1][9:12]) / 1000 - words[0]["start"]) < 0.01, "srt start != first word"
assert all(l["asr_ok"] for l in plan["lines"]), "ASR mismatch"
print("SPEECH OK", qa)
PY

# No-speech mode: same clips, music-led, cuts snapped to beats.
mkdir -p "$W/silent/audio/music"; cp -r "$W/speech/scenes" "$W/silent/"
# 120 bpm click track, 20 s.
ffmpeg -y -v error -f lavfi -i "sine=f=880:d=0.05,apad=pad_dur=0.45" -af "aloop=loop=39:size=24000" "$W/silent/audio/music/bed.wav"
python3 - "$W" <<'PY'
import json, sys
from pathlib import Path
w = Path(sys.argv[1]); plan = json.loads((w / "speech/plan.json").read_text())
plan["master"].update(speech=False, voice_engine="", captions="none")
plan.pop("lines")
for sc, s in zip(plan["scenes"], (3.1, 4.2, 5)):
    for k in ("start_s", "end_s", "start_f", "frames", "line_ids"): sc.pop(k, None)
    sc["seconds"] = s
(w / "silent/plan.json").write_text(json.dumps(plan, indent=2))
PY
python3 "$HERE/timing.py" "$W/silent"
python3 "$HERE/assemble.py" "$W/silent"
# Captions in place: one output file, clean copy kept in .clean/, a rerun never burns twice.
CAP="$HERE/../../film-captions/scripts/captions.py"; R="$W/speech/renders"
for i in 1 2; do python3 "$CAP" "$R/final.mp4" "$R/final.mp4" --words "$W/speech/audio/vo/vo.words.json" --style clean >/dev/null; done
ffprobe -v error -show_entries format_tags=comment -of csv=p=0 "$R/final.mp4" | grep -q film-captions || { echo "caption tag missing"; exit 1; }
[ -f "$R/.clean/final.mp4" ] && ! ffprobe -v error -show_entries format_tags=comment -of csv=p=0 "$R/.clean/final.mp4" | grep -q film-captions || { echo ".clean copy wrong"; exit 1; }
! python3 "$CAP" "$R/final.mp4" "$R/x.mp4" --words "$W/speech/audio/vo/vo.words.json" 2>/dev/null || [ -f "$R/.clean/final.mp4" ] || { echo "double burn not refused"; exit 1; }
echo "CAPTIONS OK"

echo "ALL OK  ($W)"
