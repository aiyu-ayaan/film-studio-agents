import "@fontsource-variable/archivo/standard.css";
import "./styles.css";
import { invoke, convertFileSrc } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

type Stage = { id: string; label: string; done: boolean };
type Status = {
  title: string; stages: Stage[]; current: number; progress: number;
  scenes_done: number; scenes_total: number; final_video: string | null;
};
type Project = { name: string; path: string; status: Status };
type Agent = { id: string; label: string; bin: string | null; levels: [string, string, string] };
type Line = { kind: "text" | "delta" | "tool" | "info" | "error" | "raw"; text: string };

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const store = {
  get: (k: string, d = "") => { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
  set: (k: string, v: string) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};

let agents: Agent[] = [];
let projects: Project[] = [];
let current: Project | null = null;
let running = false;
let runLevel = 1;
let lastVideo = "";
let lastBlock: HTMLElement | null = null;

const FRAMING_SKILL = ".agents/skills/film-framing/SKILL.md";

// ---------- agent + permission controls ----------
const agentSel = $<HTMLSelectElement>("agent");
const levelInputs = [...document.querySelectorAll<HTMLInputElement>('input[name="level"]')];
const level = () => Number(levelInputs.find((i) => i.checked)?.value ?? 1);

function renderLevelHelp() {
  const a = agents.find((x) => x.id === agentSel.value);
  $("level-help").textContent = a
    ? a.levels[level()]
    : "Custom command: the level is whatever your command allows. Check its flags.";
  $("full-banner").hidden = !(level() === 2 && agentSel.value !== "custom");
}

function setLevel(v: number) {
  levelInputs.forEach((i) => (i.checked = Number(i.value) === v));
  store.set("level", String(v));
  renderLevelHelp();
}

levelInputs.forEach((i) =>
  i.addEventListener("change", () => {
    if (Number(i.value) !== 2) return setLevel(Number(i.value));
    const a = agents.find((x) => x.id === agentSel.value);
    $("full-text").textContent =
      `Full access lets ${a?.label ?? "the agent"} run any command and edit or delete any file in this folder, with no question first. ${a?.levels[2] ?? ""}`;
    const dlg = $<HTMLDialogElement>("full-dialog");
    dlg.returnValue = "";
    dlg.showModal();
    dlg.addEventListener("close", () => setLevel(dlg.returnValue === "yes" ? 2 : 1), { once: true });
  }),
);

agentSel.addEventListener("change", () => {
  store.set("agent", agentSel.value);
  $("custom-wrap").hidden = agentSel.value !== "custom";
  renderLevelHelp();
});
$<HTMLInputElement>("custom-cmd").addEventListener("change", (e) =>
  store.set("custom", (e.target as HTMLInputElement).value));
$<HTMLInputElement>("lean").addEventListener("change", (e) =>
  store.set("lean", (e.target as HTMLInputElement).checked ? "1" : "0"));

// ---------- prompt ----------
function filmPrompt(rel: string, brief: string, speech: boolean, framing: boolean) {
  const skill = speech ? "film-studio" : "film-studio-nospeech";
  return [
    "Make a film with the Film Studio pipeline in this repo.",
    `Read CLAUDE.md, then follow .agents/skills/${skill}/SKILL.md stage by stage.`,
    `Project folder, already created: ${rel}. Work only inside it.`,
    framing ? `Also apply ${FRAMING_SKILL}: plan an intro and a bridge between every topic section.` : "",
    `Brief: ${brief}`,
    leanRules(),
    "At a user gate (G1 script + storyboard approval, voice choice), stop and ask in one short message. My answer comes in the next turn.",
  ].filter(Boolean).join("\n");
}

function leanRules() {
  if (!$<HTMLInputElement>("lean").checked) return "";
  return "Token budget: read only the files the current stage names, never a whole skill folder or a large reference end to end. Trust script exit codes instead of re-reading outputs. Keep messages short.";
}

// ---------- run ----------
async function run(prompt: string, resume: boolean) {
  if (!current) return;
  const key = `session:${current.path}:${agentSel.value}`;
  const session = resume ? store.get(key) || null : null;
  runLevel = level();
  try {
    await invoke("start_agent", {
      agent: agentSel.value, prompt, session, level: runLevel,
      lean: $<HTMLInputElement>("lean").checked,
      customCmd: $<HTMLInputElement>("custom-cmd").value || null,
    });
    setRunning(true);
  } catch (e) {
    addLine({ kind: "error", text: String(e) });
  }
}

function setRunning(on: boolean) {
  running = on;
  $("stop").hidden = !on;
  $<HTMLButtonElement>("send").disabled = on;
  $<HTMLButtonElement>("new-film").disabled = on;
  agentSel.disabled = on;
  levelInputs.forEach((i) => (i.disabled = on));
  const a = agents.find((x) => x.id === agentSel.value)?.label ?? "Custom agent";
  const rs = $("run-state");
  rs.textContent = on ? `${a} working${runLevel === 2 ? ", full access" : ""}` : "Idle";
  rs.dataset.state = on ? (runLevel === 2 ? "full" : "on") : "off";
}

function addLine(l: Line) {
  const log = $("log");
  const stick = log.scrollHeight - log.scrollTop - log.clientHeight < 40;
  if (l.kind === "delta" && lastBlock?.dataset.kind === "delta") {
    lastBlock.textContent += l.text;
  } else {
    const p = document.createElement("p");
    p.className = `ln ${l.kind}`;
    p.dataset.kind = l.kind;
    p.textContent = l.text;
    log.append(p);
    lastBlock = p;
    while (log.childElementCount > 2000) log.firstElementChild?.remove();
  }
  if (stick) log.scrollTop = log.scrollHeight;
}

listen<Line>("agent-line", (e) => addLine(e.payload));
listen<string>("agent-session", (e) => {
  if (current) store.set(`session:${current.path}:${agentSel.value}`, e.payload);
});
listen<number | null>("agent-exit", (e) => {
  setRunning(false);
  addLine({ kind: "info", text: e.payload === 0 ? "Agent finished. Reply below to continue." : `Agent stopped (exit ${e.payload ?? "signal"}).` });
  refresh();
});

$("stop").addEventListener("click", () => invoke("stop_agent"));

$("reply-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const ta = $<HTMLTextAreaElement>("reply");
  const text = ta.value.trim();
  if (!text || running || !current) return;
  addLine({ kind: "info", text: `You: ${text}` });
  ta.value = "";
  const hasSession = !!store.get(`session:${current.path}:${agentSel.value}`);
  const rel = `projects/${current.name}`;
  // a fresh agent (switched tool or no session yet) needs the context restated
  run(hasSession ? text : `Continue the film in ${rel} from its current stage, following its plan.json and .agents/skills/film-studio/SKILL.md.\n${leanRules()}\nUser: ${text}`, hasSession);
});
$<HTMLTextAreaElement>("reply").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) $<HTMLFormElement>("reply-form").requestSubmit();
});

// ---------- views ----------
function show(view: "new" | "film" | "empty") {
  $("new-view").hidden = view !== "new";
  $("film-view").hidden = view !== "film";
  $("empty-view").hidden = view !== "empty";
}

$("new-film").addEventListener("click", () => {
  current = null;
  renderList();
  show("new");
  $("slug").focus();
});
$("new-cancel").addEventListener("click", () => show(current ? "film" : "empty"));

$("new-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const slug = $<HTMLInputElement>("slug").value.trim();
  const brief = $<HTMLTextAreaElement>("brief").value.trim();
  $("new-error").textContent = "";
  try {
    const path = await invoke<string>("new_project", { slug });
    await refresh();
    open(path);
    $("log").replaceChildren();
    const rel = `projects/${path.split("/").pop()}`;
    await run(filmPrompt(rel, brief, $<HTMLInputElement>("speech").checked, $<HTMLInputElement>("framing").checked), false);
    $<HTMLFormElement>("new-form").reset();
  } catch (err) {
    $("new-error").textContent = String(err);
  }
});

function open(path: string) {
  current = projects.find((p) => p.path === path) ?? null;
  if (!current) return;
  if (!running) $("log").replaceChildren();
  lastVideo = "";
  renderList();
  renderFilm();
  show("film");
}

function renderList() {
  const ul = $("projects");
  ul.replaceChildren(
    ...projects.map((p) => {
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.type = "button";
      b.className = "proj";
      if (current?.path === p.path) b.setAttribute("aria-current", "true");
      b.disabled = running && current?.path !== p.path;
      const pct = Math.round(p.status.progress * 100);
      b.innerHTML = `<span class="proj-name"></span><span class="mini" aria-hidden="true"><i style="width:${pct}%"></i></span><span class="proj-pct">${pct}%</span>`;
      b.querySelector(".proj-name")!.textContent = p.status.title || p.name;
      b.setAttribute("aria-label", `${p.status.title || p.name}, ${pct}% done`);
      b.addEventListener("click", () => open(p.path));
      li.append(b);
      return li;
    }),
  );
  if (!projects.length) {
    const li = document.createElement("li");
    li.className = "help";
    li.textContent = "No films yet.";
    ul.append(li);
  }
}

function renderFilm() {
  if (!current) return;
  const s = current.status;
  $("film-title").textContent = s.title || current.name;
  $("film-meta").textContent = current.name;

  const leader = $("leader");
  leader.replaceChildren(
    ...s.stages.map((st, i) => {
      const li = document.createElement("li");
      li.className = "frame";
      li.dataset.state = st.done ? "done" : i === s.current ? "now" : "todo";
      if (i === s.current) li.setAttribute("aria-current", "step");
      li.innerHTML = `<span class="n"></span><span class="l"></span>`;
      li.querySelector(".n")!.textContent = st.id;
      li.querySelector(".l")!.textContent = st.label;
      li.title = `${st.label}: ${st.done ? "done" : i === s.current ? "in progress" : "not started"}`;
      return li;
    }),
  );

  const pct = Math.round(s.progress * 100);
  $("bar-fill").style.transform = `scaleX(${s.progress})`;
  $("bar").setAttribute("aria-valuenow", String(pct));
  const total = s.stages.length;
  const now = s.stages[s.current];
  $("stage-line").textContent = now
    ? `Stage ${s.current + 1} of ${total}: ${now.label}${now.id === "4" && s.scenes_total ? `, ${s.scenes_done} of ${s.scenes_total} scenes rendered` : ""} · ${pct}%`
    : "All stages done.";

  const vid = s.final_video ?? "";
  $<HTMLButtonElement>("open-video").disabled = !vid;
  if (vid !== lastVideo) {
    lastVideo = vid;
    const box = $("player");
    if (vid) {
      const v = document.createElement("video");
      v.controls = true;
      v.preload = "metadata";
      v.src = `${convertFileSrc(vid)}?t=${Date.now()}`;
      box.replaceChildren(v);
    } else {
      box.innerHTML = `<p class="empty">The film appears here after it is assembled.</p>`;
    }
  }
}

$("open-video").addEventListener("click", () => current?.status.final_video && invoke("open_path", { path: current.status.final_video }));
$("open-folder").addEventListener("click", () => current && invoke("open_path", { path: current.path }).catch((e) => addLine({ kind: "error", text: String(e) })));

async function refresh() {
  projects = await invoke<Project[]>("list_projects");
  if (current) current = projects.find((p) => p.path === current!.path) ?? current;
  renderList();
  renderFilm();
}

// ---------- boot ----------
(async () => {
  agents = await invoke<Agent[]>("list_agents");
  agentSel.replaceChildren(
    ...agents.map((a) => new Option(a.bin ? a.label : `${a.label} (not installed)`, a.id)),
    new Option("Custom command", "custom"),
  );
  [...agentSel.options].forEach((o) => {
    const a = agents.find((x) => x.id === o.value);
    if (a && !a.bin) o.disabled = true;
  });
  const saved = store.get("agent", agents.find((a) => a.bin)?.id ?? "custom");
  agentSel.value = saved;
  $("custom-wrap").hidden = agentSel.value !== "custom";
  $<HTMLInputElement>("custom-cmd").value = store.get("custom");
  $<HTMLInputElement>("lean").checked = store.get("lean", "1") === "1";
  // full access never survives a restart: the user re-confirms it each session
  setLevel(Math.min(Number(store.get("level", "1")), 1));
  setRunning(false);

  const hasFraming = await invoke<boolean>("has_file", { rel: FRAMING_SKILL }).catch(() => false);
  $("framing-wrap").hidden = !hasFraming;

  await refresh();
  show("empty");
  setInterval(() => { if (current || running) refresh(); }, 2000);
})();
