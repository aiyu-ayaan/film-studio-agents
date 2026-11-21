//! Run an AI agent CLI headless in the repo and stream its output to the UI.

use serde_json::Value;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use tauri::{AppHandle, Emitter, State};

#[derive(Default)]
pub struct Runner {
    child: Arc<Mutex<Option<Child>>>,
}

#[derive(serde::Serialize)]
pub struct AgentInfo {
    id: &'static str,
    label: &'static str,
    bin: Option<String>,
    /// what each permission level means for this agent, in plain words
    levels: [&'static str; 3],
}

const AGENTS: [(&str, &str, &str, [&str; 3]); 3] = [
    ("claude", "Claude Code", "claude", [
        "Plans only: reads files, changes nothing (--permission-mode plan).",
        "Edits and commands, a safety check blocks risky ones (--permission-mode auto).",
        "Runs any command and edits any file without asking (--dangerously-skip-permissions).",
    ]),
    ("codex", "Codex", "codex", [
        "Read-only sandbox: cannot write files (sandbox_mode=read-only).",
        "Writes only inside the repo, no network for commands (sandbox_mode=workspace-write).",
        "No sandbox, no approvals: any command, any file (--dangerously-bypass-approvals-and-sandbox).",
    ]),
    ("agy", "Antigravity", "agy", [
        "Plans only: changes nothing (--mode plan).",
        "Accepts file edits; other tool requests are denied (--mode accept-edits).",
        "Approves every tool request without asking (--dangerously-skip-permissions).",
    ]),
];

/// GUI launches often lack the user's shell PATH, so look in the usual bin dirs too.
fn find_bin(name: &str) -> Option<PathBuf> {
    let home = std::env::var_os("HOME").map(PathBuf::from).unwrap_or_default();
    std::env::var_os("PATH")
        .map(|p| std::env::split_paths(&p).collect::<Vec<_>>())
        .unwrap_or_default()
        .into_iter()
        .chain([home.join(".local/bin"), home.join(".cargo/bin"), "/usr/local/bin".into()])
        .map(|d| d.join(name))
        .find(|p| p.is_file())
}

#[tauri::command]
pub fn list_agents() -> Vec<AgentInfo> {
    AGENTS
        .iter()
        .map(|(id, label, bin, levels)| AgentInfo {
            id,
            label,
            bin: find_bin(bin).map(|p| p.display().to_string()),
            levels: *levels,
        })
        .collect()
}

/// Model choices per agent. Claude takes aliases; Antigravity lists its own; Codex is free text.
#[tauri::command]
pub fn list_models(agent: String) -> Vec<(String, String)> {
    match agent.as_str() {
        "claude" => [("fable", "Fable (latest)"), ("opus", "Opus (latest)"), ("sonnet", "Sonnet (latest)"), ("haiku", "Haiku (latest)")]
            .iter().map(|(a, b)| (a.to_string(), b.to_string())).collect(),
        "agy" => find_bin("agy")
            .and_then(|b| Command::new(b).arg("models").stdin(Stdio::null()).output().ok())
            .map(|o| String::from_utf8_lossy(&o.stdout).lines()
                .filter_map(|l| l.split_once('\t')).map(|(a, b)| (a.to_string(), b.to_string())).collect())
            .unwrap_or_default(),
        _ => vec![],
    }
}

/// Argument list for one turn. `level`: 0 read only, 1 guarded, 2 full access.
/// `lean`: drop context the film pipeline never uses (MCP servers other than earshot).
fn build_args(agent: &str, prompt: &str, session: Option<&str>, level: u8, lean: bool, model: &str, effort: &str) -> Vec<String> {
    let mut a: Vec<String> = Vec::new();
    let mut push = |s: &str| a.push(s.to_string());
    // model / effort: empty = the CLI's own default
    match agent {
        "claude" | "agy" => {
            if !model.is_empty() { push("--model"); push(model) }
            if !effort.is_empty() { push("--effort"); push(effort) }
        }
        _ => {}
    }
    match agent {
        "claude" => {
            for s in ["-p", "--output-format", "stream-json", "--verbose"] { push(s) }
            match level {
                2 => push("--dangerously-skip-permissions"),
                1 => { push("--permission-mode"); push("auto") }
                _ => { push("--permission-mode"); push("plan") }
            }
            if lean {
                // ~10 MCP servers (Gmail, Drive, rea...) cost thousands of tokens per turn
                for s in ["--strict-mcp-config", "--mcp-config", EARSHOT_ONLY, "--exclude-dynamic-system-prompt-sections"] { push(s) }
            }
            if let Some(id) = session { push("--resume"); push(id) }
            push(prompt);
        }
        "codex" => {
            push("exec");
            if let Some(id) = session { push("resume"); push(id) }
            for s in ["--json", "--skip-git-repo-check"] { push(s) }
            if !model.is_empty() { push("-m"); push(model) }
            if !effort.is_empty() { push("-c"); push(&format!("model_reasoning_effort=\"{effort}\"")) }
            match level {
                2 => push("--dangerously-bypass-approvals-and-sandbox"),
                1 => { push("-c"); push("sandbox_mode=\"workspace-write\"") }
                _ => { push("-c"); push("sandbox_mode=\"read-only\"") }
            }
            if lean {
                for s in ["-c", "mcp_servers.chrome-devtools.enabled=false", "-c", "mcp_servers.codegraph.enabled=false"] { push(s) }
            }
            push(prompt);
        }
        "agy" => {
            for s in ["-p", "--output-format", "stream-json"] { push(s) }
            match level {
                2 => push("--dangerously-skip-permissions"),
                1 => { push("--mode"); push("accept-edits") }
                _ => { push("--mode"); push("plan") }
            }
            if let Some(id) = session { push("--conversation"); push(id) }
            push(prompt);
        }
        _ => {}
    }
    a
}

const EARSHOT_ONLY: &str = r#"{"mcpServers":{"earshot":{"command":"earshot","args":["mcp"]}}}"#;

/// Model ids are passed as argv, never through a shell; still refuse odd characters.
fn clean_opt(v: &Option<String>) -> &str {
    match v.as_deref().map(str::trim) {
        Some(s) if s.chars().all(|c| c.is_ascii_alphanumeric() || "-._:/[]".contains(c)) => s,
        _ => "",
    }
}

#[derive(serde::Serialize, Clone, Default, PartialEq, Debug)]
struct Usage {
    input: u64,
    cached: u64,
    output: u64,
    cost: Option<f64>,
}

/// Token use from each agent's end-of-turn line.
fn usage_of(v: &Value) -> Option<Usage> {
    let n = |x: &Value| x.as_u64().unwrap_or(0);
    if v["type"] == "result" {
        let u = &v["usage"];
        return Some(Usage {
            input: n(&u["input_tokens"]) + n(&u["cache_creation_input_tokens"]),
            cached: n(&u["cache_read_input_tokens"]),
            output: n(&u["output_tokens"]),
            cost: v["total_cost_usd"].as_f64(),
        });
    }
    if v["type"] == "turn.completed" {
        let u = &v["usage"];
        let cached = n(&u["cached_input_tokens"]);
        return Some(Usage { input: n(&u["input_tokens"]).saturating_sub(cached), cached, output: n(&u["output_tokens"]), cost: None });
    }
    if v["event"] == "result" {
        let u = &v["result"]["usage"];
        return Some(Usage { input: n(&u["input_tokens"]), cached: n(&u["cache_read_tokens"]), output: n(&u["output_tokens"]), cost: None });
    }
    None
}

#[derive(serde::Serialize, Clone)]
struct Line {
    kind: &'static str, // text | delta | tool | info | error | raw
    text: String,
}

/// Session id from the first lines of each agent's JSON stream.
fn session_of(v: &Value) -> Option<String> {
    v["session_id"].as_str()
        .or(v["thread_id"].as_str())
        .or(v["conversation_id"].as_str())
        .map(str::to_owned)
}

/// Turn one stream line into something a person can read. None = skip (noise).
fn readable(line: &str) -> Option<Line> {
    let l = |kind, text: &str| Some(Line { kind, text: text.trim_end().to_string() });
    let Ok(v) = serde_json::from_str::<Value>(line) else {
        return if line.trim().is_empty() { None } else { l("raw", line) };
    };
    // Claude Code
    match v["type"].as_str() {
        Some("assistant") => {
            let parts: Vec<String> = v["message"]["content"].as_array()?.iter().filter_map(|c| {
                match c["type"].as_str()? {
                    "text" => c["text"].as_str().map(str::to_owned),
                    "tool_use" => Some(format!("▸ {} {}", c["name"].as_str()?, short(&c["input"]))),
                    _ => None,
                }
            }).collect();
            let tool = v["message"]["content"][0]["type"] == "tool_use";
            return if parts.is_empty() { None } else { l(if tool { "tool" } else { "text" }, &parts.join("\n")) };
        }
        Some("result") => return l("info", &format!("Turn finished: {}", v["subtype"].as_str().unwrap_or("done"))),
        Some("item.completed") | Some("item.started") => {
            // Codex
            let it = &v["item"];
            return match it["type"].as_str()? {
                "agent_message" | "reasoning" if v["type"] == "item.completed" => l("text", it["text"].as_str()?),
                "command_execution" if v["type"] == "item.started" => l("tool", &format!("▸ {}", it["command"].as_str()?)),
                "file_change" if v["type"] == "item.completed" => l("tool", &format!("▸ edit {}", short(&it["changes"]))),
                "error" => l("error", it["message"].as_str()?),
                _ => None,
            };
        }
        Some("error") => return l("error", v["message"].as_str()?),
        Some("turn.completed") => return l("info", "Turn finished"),
        _ => {}
    }
    // Antigravity
    match v["event"].as_str() {
        Some("step_update") => {
            let s = &v["step_update"];
            if let Some(d) = s["text_delta"].as_str() {
                return l_delta(d);
            }
            if s["state"] == "DONE" && s["step_type"] != "user_input" {
                return l("tool", &format!("▸ {}", s["step_type"].as_str()?));
            }
            None
        }
        Some("result") => l("info", &format!("Turn finished: {}", v["result"]["status"].as_str().unwrap_or("done"))),
        _ => None,
    }
}

fn l_delta(d: &str) -> Option<Line> {
    Some(Line { kind: "delta", text: d.to_string() })
}

fn short(v: &Value) -> String {
    let s = match v {
        Value::Object(m) => m.get("command").or(m.get("file_path")).or(m.get("description"))
            .and_then(Value::as_str).map(str::to_owned).unwrap_or_else(|| v.to_string()),
        _ => v.to_string(),
    };
    let s = s.replace('\n', " ");
    if s.chars().count() > 160 { format!("{}…", s.chars().take(160).collect::<String>()) } else { s }
}

#[tauri::command]
pub fn start_agent(
    app: AppHandle,
    runner: State<Runner>,
    agent: String,
    prompt: String,
    session: Option<String>,
    level: u8,
    lean: bool,
    model: Option<String>,
    effort: Option<String>,
    custom_cmd: Option<String>,
) -> Result<String, String> {
    let mut slot = runner.child.lock().unwrap();
    if let Some(c) = slot.as_mut() {
        if c.try_wait().map_err(|e| e.to_string())?.is_none() {
            return Err("An agent is already running. Stop it first.".into());
        }
    }
    let root = crate::root();
    let home = std::env::var_os("HOME").map(PathBuf::from).unwrap_or_default();
    let path = std::env::join_paths(
        [home.join(".local/bin"), home.join(".cargo/bin")].into_iter()
            .chain(std::env::var_os("PATH").map(|p| std::env::split_paths(&p).collect::<Vec<_>>()).unwrap_or_default()),
    ).map_err(|e| e.to_string())?;

    let (mut cmd, shown) = if agent == "custom" {
        let tpl = custom_cmd.filter(|s| !s.trim().is_empty()).ok_or("Enter a command for the custom agent.")?;
        let mut c = Command::new("bash");
        c.arg("-c").arg(&tpl).env("PROMPT", &prompt);
        (c, format!("bash -c '{tpl}'  (prompt in $PROMPT)"))
    } else {
        let bin_name = AGENTS.iter().find(|a| a.0 == agent).ok_or("Unknown agent.")?.2;
        let bin = find_bin(bin_name).ok_or(format!("`{bin_name}` was not found on PATH or in ~/.local/bin."))?;
        let args = build_args(&agent, &prompt, session.as_deref(), level.min(2), lean,
            clean_opt(&model), clean_opt(&effort));
        let mut c = Command::new(&bin);
        c.args(&args);
        let shown_args: Vec<String> = args[..args.len() - 1].to_vec(); // hide the long prompt
        (c, format!("{} {} \"<prompt>\"", bin.display(), shown_args.join(" ")))
    };
    #[cfg(unix)]
    std::os::unix::process::CommandExt::process_group(&mut cmd, 0); // so Stop kills the whole tree
    let mut child = cmd
        .current_dir(&root)
        .env("PATH", path)
        .env("HYPERFRAMES_CACHE_DIR", home.join(".local/share/hyperframes-cache"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Could not start the agent: {e}"))?;

    let _ = app.emit("agent-line", Line { kind: "info", text: format!("$ {shown}") });
    let out = child.stdout.take().unwrap();
    let err = child.stderr.take().unwrap();
    *slot = Some(child);

    let a2 = app.clone();
    std::thread::spawn(move || {
        for line in BufReader::new(err).lines().map_while(Result::ok) {
            if !line.trim().is_empty() {
                let _ = a2.emit("agent-line", Line { kind: "raw", text: line });
            }
        }
    });
    let child_ref = runner.child.clone();
    std::thread::spawn(move || {
        let mut sent_session = false;
        for line in BufReader::new(out).lines().map_while(Result::ok) {
            if !sent_session {
                if let Some(id) = serde_json::from_str::<Value>(&line).ok().as_ref().and_then(session_of) {
                    let _ = app.emit("agent-session", id);
                    sent_session = true;
                }
            }
            if let Some(u) = serde_json::from_str::<Value>(&line).ok().as_ref().and_then(usage_of) {
                let _ = app.emit("agent-usage", u);
            }
            if let Some(l) = readable(&line) {
                let _ = app.emit("agent-line", l);
            }
        }
        let code = child_ref.lock().unwrap().as_mut().and_then(|c| c.wait().ok()).and_then(|s| s.code());
        let _ = app.emit("agent-exit", code);
    });
    Ok(shown)
}

#[tauri::command]
pub fn stop_agent(runner: State<Runner>) -> Result<(), String> {
    if let Some(c) = runner.child.lock().unwrap().as_mut() {
        #[cfg(unix)]
        let _ = Command::new("kill").args(["-TERM", "--", &format!("-{}", c.id())]).status();
        let _ = c.kill();
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn full_access_only_at_level_2() {
        for agent in ["claude", "codex", "agy"] {
            for level in 0..=2u8 {
                let a = build_args(agent, "hi", None, level, true, "", "").join(" ");
                assert_eq!(a.contains("dangerously"), level == 2, "{agent} {level}: {a}");
                assert!(a.ends_with("hi"));
            }
        }
        let r = build_args("codex", "hi", Some("abc"), 1, false, "gpt-x", "high").join(" ");
        assert!(r.starts_with("exec resume abc --json"));
        assert!(r.contains("-m gpt-x -c model_reasoning_effort=\"high\""));
        assert!(build_args("claude", "hi", None, 1, false, "opus", "low").join(" ").starts_with("--model opus --effort low -p"));
    }

    #[test]
    fn parses_each_stream() {
        let c = r#"{"type":"assistant","message":{"content":[{"type":"text","text":"ok"}]}}"#;
        assert_eq!(readable(c).unwrap().text, "ok");
        let x = r#"{"type":"item.completed","item":{"type":"agent_message","text":"hey"}}"#;
        assert_eq!(readable(x).unwrap().text, "hey");
        let g = r#"{"event":"step_update","step_update":{"state":"ACTIVE","step_type":"agent_response","text_delta":"yo"}}"#;
        assert_eq!(readable(g).unwrap().kind, "delta");
        assert_eq!(session_of(&serde_json::from_str(r#"{"event":"init","conversation_id":"z"}"#).unwrap()), Some("z".into()));
        assert_eq!(readable("plain text").unwrap().kind, "raw");
        let r: Value = serde_json::from_str(r#"{"type":"result","total_cost_usd":0.5,"usage":{"input_tokens":2,"cache_creation_input_tokens":8,"cache_read_input_tokens":100,"output_tokens":4}}"#).unwrap();
        assert_eq!(usage_of(&r), Some(Usage { input: 10, cached: 100, output: 4, cost: Some(0.5) }));
        let r: Value = serde_json::from_str(r#"{"type":"turn.completed","usage":{"input_tokens":50,"cached_input_tokens":20,"output_tokens":5}}"#).unwrap();
        assert_eq!(usage_of(&r).unwrap().input, 30);
    }
}
