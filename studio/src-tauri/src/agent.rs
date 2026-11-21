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
        "Plans only: changes nothing; may read files anywhere (--mode plan, read_file(*) allowed).",
        "Edits files and runs shell commands without asking; browser and other tools stay denied (--mode accept-edits, command(*) and read_file(*) allowed). Headless Antigravity cannot ask, so this is close to full access.",
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
            // -c works on both `exec` and `exec resume` (resume has no -m)
            if !model.is_empty() { push("-c"); push(&format!("model=\"{model}\"")) }
            if !effort.is_empty() { push("-c"); push(&format!("model_reasoning_effort=\"{effort}\"")) }
            match level {
                2 => push("--dangerously-bypass-approvals-and-sandbox"),
                1 => { push("-c"); push("sandbox_mode=\"workspace-write\"") }
                _ => { push("-c"); push("sandbox_mode=\"read-only\"") }
            }
            if lean {
                // only servers defined in ~/.codex/config.toml can be switched off this way;
                // naming an undefined one (chrome-devtools comes from a plugin) breaks config loading
                for s in ["-c", "mcp_servers.codegraph.enabled=false"] { push(s) }
            }
            push(prompt);
        }
        "agy" => {
            // agy's -p takes the prompt as its value, so it goes last, right before the prompt
            for s in ["--output-format", "stream-json"] { push(s) }
            match level {
                2 => push("--dangerously-skip-permissions"),
                // headless agy auto-denies every shell command; the pipeline cannot run without them
                1 => { push("--mode"); push("accept-edits"); push("--settings"); push(r#"{"permissions":{"allow":["command(*)","read_file(*)"]}}"#) }
                // skills live outside the repo (~/.claude/skills, ~/lemo-opuscar); headless agy denies reading them
                _ => { push("--mode"); push("plan"); push("--settings"); push(r#"{"permissions":{"allow":["read_file(*)"]}}"#) }
            }
            if let Some(id) = session { push("--conversation"); push(id) }
            push("-p");
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
            if s["state"] == "ACTIVE" && s["step_type"] == "tool" {
                let p = &s["tool_info"]["parameters"];
                let what = p["CommandLine"].as_str().map(str::to_owned).unwrap_or_else(|| short(p));
                return l("tool", &format!("▸ {} {}", s["tool_name"].as_str().unwrap_or("tool"), what));
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
    project: Option<String>,
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

    // per-film record so any agent (or a later app session) can pick up where this run stopped
    let studio = project.as_deref().map(crate::project_dir).transpose()?.map(|d| d.join(".studio"));
    if let Some(s) = &studio {
        std::fs::create_dir_all(s).map_err(|e| e.to_string())?;
    }
    let started = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0);
    let mut record = serde_json::json!({
        "agent": agent, "model": clean_opt(&model), "level": level.min(2), "started": started, "exit": null,
    });
    if let Some(s) = &studio {
        let _ = std::fs::write(s.join("last-run.json"), record.to_string());
    }
    let log = studio.as_ref().and_then(|s| std::fs::OpenOptions::new().create(true).append(true).open(s.join("run.log")).ok());
    let log = Arc::new(Mutex::new(log));
    let note = |l: &Line| {
        if let Some(f) = log.lock().unwrap().as_mut() {
            use std::io::Write;
            let _ = writeln!(f, "{}", l.text);
        }
    };
    let head = Line { kind: "info", text: format!("--- run {started}: {agent} {}\n$ {shown}", ["read only", "guarded", "full access"][level.min(2) as usize]) };
    note(&head);
    let _ = app.emit("agent-line", head);
    let out = child.stdout.take().unwrap();
    let err = child.stderr.take().unwrap();
    *slot = Some(child);

    let a2 = app.clone();
    let log_err = log.clone();
    std::thread::spawn(move || {
        for line in BufReader::new(err).lines().map_while(Result::ok) {
            if !line.trim().is_empty() {
                // failure reasons often come on stderr; keep them for whoever takes over
                if let Some(f) = log_err.lock().unwrap().as_mut() {
                    use std::io::Write;
                    let _ = writeln!(f, "{line}");
                }
                let _ = a2.emit("agent-line", Line { kind: "raw", text: line });
            }
        }
    });
    let child_ref = runner.child.clone();
    let log2 = log.clone();
    let note = move |l: &Line| {
        if let Some(f) = log2.lock().unwrap().as_mut() {
            use std::io::Write;
            let _ = if l.kind == "delta" { write!(f, "{}", l.text) } else { writeln!(f, "{}", l.text) };
        }
    };
    std::thread::spawn(move || {
        let mut sent_session = false;
        for line in BufReader::new(out).lines().map_while(Result::ok) {
            if !sent_session {
                if let Some(id) = serde_json::from_str::<Value>(&line).ok().as_ref().and_then(session_of) {
                    let _ = app.emit("agent-session", id.clone());
                    sent_session = true;
                    record["session"] = Value::String(id);
                }
            }
            if let Some(u) = serde_json::from_str::<Value>(&line).ok().as_ref().and_then(usage_of) {
                let _ = app.emit("agent-usage", u);
            }
            if let Some(l) = readable(&line) {
                note(&l);
                let _ = app.emit("agent-line", l);
            }
        }
        let code = child_ref.lock().unwrap().as_mut().and_then(|c| c.wait().ok()).and_then(|s| s.code());
        note(&Line { kind: "info", text: format!("--- exit {}", code.map_or("signal".into(), |c| c.to_string())) });
        if let Some(s) = &studio {
            record["exit"] = code.map_or(Value::String("signal".into()), Value::from);
            let _ = std::fs::write(s.join("last-run.json"), record.to_string());
        }
        let _ = app.emit("agent-exit", code);
    });
    Ok(shown)
}

#[tauri::command]
pub fn stop_agent(runner: State<Runner>) -> Result<(), String> {
    runner.kill();
    Ok(())
}

impl Runner {
    /// Kill the agent and everything it started (its own process group).
    pub fn kill(&self) {
        if let Some(c) = self.child.lock().unwrap().as_mut() {
            if c.try_wait().ok().flatten().is_none() {
                // agents (agy) start long commands in their own session, outside our process group:
                // signal every descendant first, while they are still findable under the agent's pid
                #[cfg(target_os = "linux")]
                {
                    let pids: Vec<String> = descendants(c.id()).iter().map(u32::to_string).collect();
                    if !pids.is_empty() {
                        let _ = Command::new("kill").arg("-TERM").args(&pids).status();
                    }
                }
                #[cfg(unix)]
                let _ = Command::new("kill").args(["-TERM", "--", &format!("-{}", c.id())]).status();
                let _ = c.kill();
            }
        }
    }
}

/// All live descendants of `root`, from the parent pids in /proc/<pid>/stat.
#[cfg(target_os = "linux")]
fn descendants(root: u32) -> Vec<u32> {
    let mut kids: std::collections::HashMap<u32, Vec<u32>> = Default::default();
    for e in std::fs::read_dir("/proc").into_iter().flatten().flatten() {
        let Some(pid) = e.file_name().to_str().and_then(|n| n.parse::<u32>().ok()) else { continue };
        let Ok(stat) = std::fs::read_to_string(e.path().join("stat")) else { continue };
        // "pid (comm) state ppid ...": comm may hold spaces or ')', so read after the last ')'
        let ppid = stat.rsplit_once(')').and_then(|(_, r)| r.split_whitespace().nth(1)?.parse().ok());
        if let Some(pp) = ppid { kids.entry(pp).or_default().push(pid) }
    }
    let (mut out, mut todo) = (vec![], vec![root]);
    while let Some(p) = todo.pop() {
        for &k in kids.get(&p).map(Vec::as_slice).unwrap_or(&[]) {
            out.push(k);
            todo.push(k);
        }
    }
    out
}

#[cfg(test)]
mod tests {
    #[cfg(target_os = "linux")]
    #[test]
    fn finds_children_in_their_own_session() {
        let mut c = std::process::Command::new("sh").args(["-c", "setsid sleep 30 & wait"]).spawn().unwrap();
        std::thread::sleep(std::time::Duration::from_millis(300));
        let d = super::descendants(c.id());
        let found = d.iter().any(|p| std::fs::read_to_string(format!("/proc/{p}/comm")).is_ok_and(|n| n.trim() == "sleep"));
        let _ = std::process::Command::new("kill").args(d.iter().map(u32::to_string)).status();
        let _ = c.kill();
        let _ = c.wait();
        assert!(found, "{d:?}");
    }

    use super::*;

    #[test]
    fn full_access_only_at_level_2() {
        for agent in ["claude", "codex", "agy"] {
            for level in 0..=2u8 {
                let a = build_args(agent, "hi", None, level, true, "", "").join(" ");
                assert_eq!(a.contains("dangerously"), level == 2, "{agent} {level}: {a}");
                assert!(a.ends_with("hi"));
                if agent == "agy" { assert!(a.ends_with("-p hi"), "{a}") }
            }
        }
        let r = build_args("codex", "hi", Some("abc"), 1, false, "gpt-x", "high").join(" ");
        assert!(r.starts_with("exec resume abc --json"));
        assert!(r.contains("-c model=\"gpt-x\" -c model_reasoning_effort=\"high\""));
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
        let t = r#"{"event":"step_update","step_update":{"state":"ACTIVE","step_type":"tool","tool_name":"run_command","tool_info":{"parameters":{"CommandLine":"ls"}}}}"#;
        assert_eq!(readable(t).unwrap().text, "▸ run_command ls");
        assert_eq!(session_of(&serde_json::from_str(r#"{"event":"init","conversation_id":"z"}"#).unwrap()), Some("z".into()));
        assert_eq!(readable("plain text").unwrap().kind, "raw");
        let r: Value = serde_json::from_str(r#"{"type":"result","total_cost_usd":0.5,"usage":{"input_tokens":2,"cache_creation_input_tokens":8,"cache_read_input_tokens":100,"output_tokens":4}}"#).unwrap();
        assert_eq!(usage_of(&r), Some(Usage { input: 10, cached: 100, output: 4, cost: Some(0.5) }));
        let r: Value = serde_json::from_str(r#"{"type":"turn.completed","usage":{"input_tokens":50,"cached_input_tokens":20,"output_tokens":5}}"#).unwrap();
        assert_eq!(usage_of(&r).unwrap().input, 30);
    }
}
