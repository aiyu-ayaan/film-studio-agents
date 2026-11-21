#!/usr/bin/env bash
# Install the studio's skills with each project's official command.
# Usage: bin/setup-skills.sh <name>... | all | list
# Add a skill: add a case below, a card in research/skills/, a row in ../CLAUDE.md.
# Changes ~/.claude (skills, plugins, MCP) and downloads code. Read research/skills/<name>.md first.
set -euo pipefail
SRC=~/.local/share/skill-src   # stable home for clones that get symlinked
NAMES="hyperframes shotcraft motionmaxxing 3dviz-pro-max earshot lemo-opuscar remotion herk-edit-kit openmontage"

install() {
  case "$1" in
    hyperframes)   npx -y hyperframes skills update ;;
    shotcraft)     [ -e ~/.claude/skills/video-shotcraft ] || git clone --depth 1 https://github.com/windyinwind/hyper-videocraft ~/.claude/skills/video-shotcraft ;;
    motionmaxxing) [ -e ~/.claude/skills/motionmaxxing ] || git clone --depth 1 https://github.com/Tejashmakwana/motionmaxxing ~/.claude/skills/motionmaxxing
                   bash ~/.claude/skills/motionmaxxing/install.sh ;;
    3dviz-pro-max) mkdir -p "$SRC"
                   [ -e "$SRC/3dviz-pro-max" ] || git clone --depth 1 https://github.com/viettranx/3dviz-pro-max "$SRC/3dviz-pro-max"
                   [ -e ~/.claude/skills/3dviz-pro-max ] || ln -s "$SRC/3dviz-pro-max/skills/3dviz-pro-max" ~/.claude/skills/3dviz-pro-max ;;
    earshot)       uv tool install --python 3.12 --index https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match \
                     "earshot[mcp] @ git+https://github.com/Leonxlnx/earshot"
                   earshot doctor --fetch
                   claude mcp add earshot --scope user -e EARSHOT_THREADS=3 -- earshot mcp ;;
    lemo-opuscar)  claude plugin marketplace add lemomo-ai/lemo-opuscar
                   claude plugin install lemo-opuscar@lemolab ;;
    remotion)      npx -y skills add remotion-dev/skills ;;
    # Not symlinked: its skills use repo-relative paths and 4 would shadow the global HyperFrames skills.
    # CUDA skip: onnxruntime-node's CUDA 12 download 404s on this PC (2026-11-21).
    herk-edit-kit) [ -e "$SRC/herk-edit-kit" ] || git clone https://github.com/nateherkai/herk-edit-kit "$SRC/herk-edit-kit"
                   (cd "$SRC/herk-edit-kit" && npm ci --onnxruntime-node-install-cuda=skip && npm test) ;;
    # AGPL-3.0: runs only as a separate process (bin/om.sh). No `make setup`: it installs Piper TTS (excluded voice).
    openmontage)   [ -e "$SRC/OpenMontage" ] || git clone --depth 1 https://github.com/OpenMontageInc/OpenMontage "$SRC/OpenMontage"
                   (cd "$SRC/OpenMontage" && { [ -x .venv/bin/python ] || uv venv -q --python 3.12 .venv; } && uv pip install -q --python .venv/bin/python -r requirements.txt) ;;
    *) echo "unknown skill: $1 (known: $NAMES)" >&2; return 2 ;;
  esac
}

[ $# -gt 0 ] || { echo "usage: $0 <name>... | all | list" >&2; exit 2; }
[ "$1" = list ] && { echo "$NAMES"; exit 0; }
[ "$1" = all ] && set -- $NAMES
for n in "$@"; do echo "== $n"; install "$n"; done
