#!/usr/bin/env bash
# Stage 9 cleanup: delete rebuildable bulk from finished projects so the repo stays small.
# Keeps sources (plan.json, *.md, scene code, style), audio/ (narration is slow to remake)
# and the delivered renders/final.mp4 + final.srt + qa.json + contact.png.
# Deletes: build/, renders/.clean/, other renders/*.mp4, scene clips, frames, caches,
# node_modules, vendored runtimes. Then packs git objects.
# Usage: bin/clean.sh [-n] [project_dir ...]   (no dirs = every project; -n = dry run)
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
dry=0; [ "${1:-}" = "-n" ] && { dry=1; shift; }
[ $# -eq 0 ] && set -- "$root"/projects/*/
before=$(du -sb "$root" --exclude=.venv | cut -f1)
for p in "$@"; do
  p=${p%/}
  [ -f "$p/plan.json" ] || [ -f "$p/BRIEF.md" ] || { echo "skip (not a project): $p" >&2; continue; }
  find "$p" \( \
      -path "$p/build" -o -path "$p/renders/.clean" \
      -o -name node_modules -o -name .cache -o -name .hyperframes -o -name .remotion \
      -o -path "*/scenes/*/frames" -o -path "*/scenes/*/out" -o -path "*/scenes/*/film/stills" \
      -o -path "*/scenes/*/film/runtime" \
    \) -prune -print \
    -o -type f \( -path "*/scenes/*.mp4" -o -path "*/scenes/*.mov" \
      -o \( -path "$p/renders/*.mp4" ! -name final.mp4 \) \) -print |
  while read -r f; do
    echo "rm $(du -sh "$f" | cut -f1)	${f#$root/}"
    [ $dry = 1 ] || rm -rf "$f"
  done
done
[ $dry = 1 ] && exit 0
git -C "$root" gc --quiet --prune=now 2>/dev/null || true
after=$(du -sb "$root" --exclude=.venv | cut -f1)
echo "freed $(( (before - after) / 1048576 )) MB (excluding .venv)"
