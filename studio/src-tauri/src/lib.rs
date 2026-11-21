mod agent;
mod status;

use std::path::PathBuf;
use std::process::Command;
use tauri::Manager;

/// Repo root: `FILM_STUDIO_ROOT`, else two levels above this crate (studio/src-tauri).
/// shortcut: compile-time path, set FILM_STUDIO_ROOT when the app is moved out of the repo.
pub fn root() -> PathBuf {
    std::env::var_os("FILM_STUDIO_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../.."))
        .canonicalize()
        .unwrap_or_else(|_| PathBuf::from("."))
}

#[derive(serde::Serialize)]
struct ProjectSummary {
    name: String,
    path: String,
    status: status::Status,
}

#[tauri::command]
fn studio_root() -> String {
    root().display().to_string()
}

/// True when a repo-relative file exists (used to show optional skills).
#[tauri::command]
fn has_file(rel: String) -> bool {
    !rel.contains("..") && root().join(rel).is_file()
}

#[tauri::command]
fn list_projects() -> Vec<ProjectSummary> {
    let root = root();
    let mut out: Vec<ProjectSummary> = std::fs::read_dir(root.join("projects"))
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| e.path().is_dir())
        .map(|e| ProjectSummary {
            name: e.file_name().to_string_lossy().into_owned(),
            path: e.path().display().to_string(),
            status: status::project_status(&root, &e.path()),
        })
        .collect();
    out.sort_by(|a, b| b.name.cmp(&a.name)); // newest date prefix first
    out
}

#[tauri::command]
fn project_status(dir: String) -> status::Status {
    status::project_status(&root(), std::path::Path::new(&dir))
}

#[tauri::command]
fn new_project(slug: String) -> Result<String, String> {
    let ok = !slug.is_empty()
        && slug.len() <= 60
        && slug.chars().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-');
    if !ok {
        return Err("Use lowercase letters, digits and dashes only, up to 60 characters.".into());
    }
    let out = Command::new("bash")
        .arg(root().join("bin/new-project.sh"))
        .arg(&slug)
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(String::from_utf8_lossy(&out.stderr).trim().to_string());
    }
    Ok(String::from_utf8_lossy(&out.stdout).trim().to_string())
}

/// Open a file or folder inside the repo with the desktop's default app.
#[tauri::command]
fn open_path(path: String) -> Result<(), String> {
    let p = PathBuf::from(&path).canonicalize().map_err(|e| e.to_string())?;
    if !p.starts_with(root()) {
        return Err("Only files inside the studio folder can be opened.".into());
    }
    Command::new("xdg-open").arg(p).spawn().map(|_| ()).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(agent::Runner::default())
        .setup(|app| {
            // let the webview play renders/final.mp4 from any project
            app.asset_protocol_scope().allow_directory(root().join("projects"), true)?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            studio_root,
            has_file,
            list_projects,
            project_status,
            new_project,
            open_path,
            agent::list_agents,
            agent::list_models,
            agent::start_agent,
            agent::stop_agent,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
