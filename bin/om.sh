#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Run one OpenMontage tool by name with JSON inputs; prints the result as JSON. Exit 1 if the tool failed.
# Usage: bin/om.sh <tool> '<json inputs>'   |   bin/om.sh list   (tools usable now on this PC)
# OpenMontage is AGPL-3.0. This file imports its registry, so this file alone is AGPL-3.0-or-later.
# OpenMontage runs from its own clone and venv. Never copy its code into this repo; nothing else here imports it.
# Paths in the JSON must be absolute (the tool runs with cwd = the OpenMontage clone).
set -euo pipefail
OM=${OPENMONTAGE_DIR:-$HOME/.local/share/skill-src/OpenMontage}
[ -x "$OM/.venv/bin/python" ] || { echo "OpenMontage not installed: bin/setup-skills.sh openmontage" >&2; exit 2; }
[ $# -ge 1 ] || { echo "usage: $0 <tool> '<json>' | list" >&2; exit 2; }
# The voice policy forbids every OpenMontage TTS / voice tool (CLAUDE.md "Voice policy").
case "$1" in *tts*|*voice*|lip_sync|talking_head|*avatar*) echo "refused: $1 makes a voice; use bin/vo.sh" >&2; exit 2 ;; esac
cd "$OM"
exec .venv/bin/python - "$@" <<'PY'
import json, sys
from tools.tool_registry import registry
registry.discover()
name = sys.argv[1]
if name == "list":
    for k, v in sorted(registry.support_envelope().items()):
        if v["status"] == "available":
            print(f"{k:28} {v['capability']:22} {v['runtime']}")
    sys.exit(0)
tool = registry.get(name)
if tool is None:
    sys.exit(f"unknown tool: {name} (bin/om.sh list)")
r = tool.execute(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
print(json.dumps({"success": r.success, "error": r.error, "data": r.data, "artifacts": r.artifacts}, indent=1, default=str))
sys.exit(0 if r.success else 1)
PY
