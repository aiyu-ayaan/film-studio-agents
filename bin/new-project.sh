#!/usr/bin/env bash
# Start a video project from templates/project.
# Usage: bin/new-project.sh <slug>   ->   projects/YYYY-MM-DD-<slug>/
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
slug=${1:?usage: bin/new-project.sh <slug>}
dest="$root/projects/$(date +%F)-$slug"
[ -e "$dest" ] && { echo "exists: $dest" >&2; exit 1; }
cp -r "$root/templates/project" "$dest"
find "$dest" -name .gitkeep -delete
echo "$dest"
