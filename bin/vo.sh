#!/usr/bin/env bash
# Make a voiceover wav and its word timings (<out>.words.json: [{text,start,end}...]).
# Usage: bin/vo.sh kokoro|pocket "<text>"|file.txt out.wav [voice]
# Studio rule: these two engines are the only voices allowed. Built-in voices of skills/libraries are excluded.
#   kokoro: Kokoro-82M via `npx hyperframes tts` (fast, Apache-2.0). Drafts and timing. Default voice af_heart.
#   pocket: Pocket TTS (Kyutai, ~real time on CPU). [voice] = wav to clone. Default voice built in.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
# Kokoro needs kokoro-onnx in ./.venv (Python 3.12). Rebuild: uv venv -p 3.12 .venv && uv pip install -p .venv kokoro-onnx soundfile
export HYPERFRAMES_PYTHON="${HYPERFRAMES_PYTHON:-$root/.venv/bin/python}"
# ~/.cache is group-writable on this PC, which HyperFrames refuses; use a private cache.
export HYPERFRAMES_CACHE_DIR="${HYPERFRAMES_CACHE_DIR:-$HOME/.local/share/hyperframes-cache}"
mkdir -p "$HYPERFRAMES_CACHE_DIR" && chmod 700 "$HYPERFRAMES_CACHE_DIR"

engine=${1:?engine: kokoro|pocket}; input=${2:?text or .txt file}; out=${3:?out.wav}; voice=${4:-}
mkdir -p "$(dirname "$out")"
out=$(realpath -m "$out")

case "$engine" in
  kokoro)
    npx -y hyperframes tts "$input" -o "$out" -v "${voice:-af_heart}" ;;
  pocket)
    # Pocket TTS (Kyutai, weights CC BY 4.0: credit Kyutai). [voice] = path to a 5-20 s clean wav to clone (consent required).
    [ -f "$input" ] && input=$(cat "$input")
    "$root/.venv/bin/pocket-tts" generate --text "$input" --output-path "$out" ${voice:+--voice "$(realpath "$voice")"} 2>&1 | grep -v '^INFO' || true
    [ -s "$out" ] || { echo "pocket-tts failed" >&2; exit 1; } ;;
  *) echo "unknown engine: $engine (kokoro|pocket; no other voice is allowed)" >&2; exit 2 ;;
esac

# Word timings so the picture can be cut to the voice. transcribe writes transcript.json into --dir.
# VO_NO_WORDS=1 skips it (narrate.py transcribes the joined track once instead).
[ "${VO_NO_WORDS:-}" = 1 ] && { echo "wrote $out"; exit 0; }
tmp=$(mktemp -d)
if npx -y hyperframes transcribe "$out" --dir "$tmp" --json >/dev/null 2>&1 && [ -f "$tmp/transcript.json" ]; then
  mv "$tmp/transcript.json" "${out%.wav}.words.json"
  echo "wrote $out and ${out%.wav}.words.json"
else
  echo "wrote $out (no word timings: run 'npx hyperframes models install parakeet')" >&2
fi
rm -rf "$tmp"
