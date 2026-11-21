# Film Studio app

Desktop control room for the film pipeline in this repo. Tauri 2: Rust backend in `src-tauri/`, vanilla TypeScript UI in `src/`.

Run it: `bin/studio.sh` from the repo root (release build, rebuilt when sources change).
Develop: `pnpm install && pnpm tauri dev`. Tests: `cd src-tauri && cargo test`.

| File | Does |
|---|---|
| `src-tauri/src/agent.rs` | Builds each agent's command line (permission level, model, effort, lean flags), runs it in the repo, streams readable lines, token usage and the session id to the UI, writes `.studio/run.log` and `.studio/last-run.json`. |
| `src-tauri/src/status.rs` | Reads a project folder and returns the 11 stages with their checks, scenes, script lines, gate, handoff note and last run. |
| `src-tauri/src/lib.rs` | Tauri commands: list/create films, read files inside a film, clear a gate, open a file. Repo root = `FILM_STUDIO_ROOT` or two levels up from `src-tauri`. |
| `src/main.ts`, `index.html`, `src/styles.css` | The UI. |

Permission levels map to these flags:

| Level | Claude Code | Codex | Antigravity |
|---|---|---|---|
| Read only | `--permission-mode plan` | `sandbox_mode="read-only"` | `--mode plan` |
| Guarded | `--permission-mode auto` (safety check on commands) | `sandbox_mode="workspace-write"` | `--mode accept-edits` + `command(*)` allowed: headless agy cannot ask, so without it every shell command is denied |
| Full access | `--dangerously-skip-permissions` | `--dangerously-bypass-approvals-and-sandbox` | `--dangerously-skip-permissions` |
