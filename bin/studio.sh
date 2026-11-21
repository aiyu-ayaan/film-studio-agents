#!/usr/bin/env bash
# Launch the Film Studio desktop app (studio/) as a production build.
# Builds the release binary on first run and again whenever app sources change; then runs it.
# Usage: bin/studio.sh [--rebuild]
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
app="$root/studio"
bin="$app/src-tauri/target/release/studio"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

stale() {
  [ ! -x "$bin" ] && return 0
  [ "${1:-}" = "--rebuild" ] && return 0
  # any source newer than the binary
  [ -n "$(find "$app/index.html" "$app/src" "$app/src-tauri/src" "$app/src-tauri/tauri.conf.json" \
      "$app/src-tauri/Cargo.toml" "$app/src-tauri/capabilities" "$app/package.json" \
      -newer "$bin" -print -quit)" ]
}

if stale "${1:-}"; then
  echo "Building Film Studio (release). First build takes a few minutes." >&2
  cd "$app"
  [ -d node_modules ] || pnpm install --frozen-lockfile
  # --no-bundle: just the binary; .deb/.AppImage packaging is not needed to run it here
  pnpm tauri build --no-bundle
fi

FILM_STUDIO_ROOT="$root" exec "$bin"
