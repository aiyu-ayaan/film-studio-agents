import "@fontsource-variable/archivo/standard.css";
import "./styles.css";
import { invoke, convertFileSrc } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

type Check = { label: string; ok: boolean };
type Stage = { id: string; label: string; about: string; done: boolean; checks: Check[] };
type Scene = { id: string; skill: string | null; brief: string | null; frames: number | null; seconds: number | null; clip: string | null; text: string };
type Status = {
  title: string; stages: Stage[]; current: number; progress: number;
  scenes_done: number; scenes_total: number; final_video: string | null;
  master: { width?: number; height?: number; fps?: number; duration_s?: number; voice_engine?: string; voice?: string; captions?: string; speech: boolean };
  scenes: Scene[]; lines: { id: string; text: string }[];
};
type Project = { name: string; path: string; status: Status };
type Agent = { id: string; label: string; bin: string | null; levels: [string, string, string] };
type Line = { kind: "text" | "delta" | "tool" | "info" | "error" | "raw"; text: string };
type Usage = { input: number; cached: number; output: number; cost: number | null };

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const el = <K extends keyof HTMLElementTagNameMap>(tag: K, cls = "", text = "") => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  return e;
};
const store = {
  get: (k: string, d = "") => { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
  set: (k: string, v: string) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};

let agents: Agent[] = [];
let projects: Project[] = [];
let current: Project | null = null;
let running = false;
let runLevel = 1;
let runStart = 0;
let picked: number | null = null; // stage the user clicked; null = follow the current stage
let playing = ""; // path of the clip in the player
let lastBlock: HTMLElement | null = null;

const FRAMING_SKILL = ".agents/skills/film-framing/SKILL.md";

function toast(msg: string) {
  const t = $("toast");
  t.textContent = msg;
  t.dataset.on = "1";
  clearTimeout((toast as any).h);
  (toast as any).h = setTimeout(() => (t.dataset.on = ""), 3000);
}

// ---------- agent, model, permission controls ----------
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

async function onAgentChange() {
  const id = agentSel.value;
  store.set("agent", id);
  $("custom-wrap").hidden = id !== "custom";
  $("model-wrap").hidden = id === "custom";
  $<HTMLSelectElement>("effort").value = store.get(`effort:${id}`);
  // codex has no "max" effort
  $<HTMLSelectElement>("effort").querySelector<HTMLOptionElement>('option[value="max"]')!.hidden = id === "codex";
  renderLevelHelp();
  const pick = $<HTMLSelectElement>("model-pick");
  pick.replaceChildren(new Option("Default", ""));
  if (id === "custom") return;
  const models = await invoke<[string, string][]>("list_models", { agent: id }).catch(() => []);
  if (agentSel.value !== id) return;
  pick.replaceChildren(new Option("Default", ""), ...models.map(([v, l]) => new Option(l, v)), new Option("Other…", OTHER));
  const saved = store.get(`model:${id}`);
  const known = !saved || models.some(([v]) => v === saved);
  pick.value = known ? saved : OTHER;
  $<HTMLInputElement>("model").value = known ? "" : saved;
  $("model-other-wrap").hidden = known;
}

const OTHER = "__other";
const modelValue = () => {
  const v = $<HTMLSelectElement>("model-pick").value;
  return (v === OTHER ? $<HTMLInputElement>("model").value : v).trim();
};
$<HTMLSelectElement>("model-pick").addEventListener("change", (e) => {
  const other = (e.target as HTMLSelectElement).value === OTHER;
  $("model-other-wrap").hidden = !other;
  if (other) $("model").focus();
  store.set(`model:${agentSel.value}`, modelValue());
});
agentSel.addEventListener("change", onAgentChange);
$<HTMLInputElement>("model").addEventListener("change", () => store.set(`model:${agentSel.value}`, modelValue()));
$<HTMLSelectElement>("effort").addEventListener("change", (e) => store.set(`effort:${agentSel.value}`, (e.target as HTMLSelectElement).value));
$<HTMLInputElement>("custom-cmd").addEventListener("change", (e) => store.set("custom", (e.target as HTMLInputElement).value));
$<HTMLInputElement>("lean").addEventListener("change", (e) => store.set("lean", (e.target as HTMLInputElement).checked ? "1" : "0"));

// ---------- prompt ----------
function filmPrompt(rel: string, brief: string, o: { speech: boolean; framing: boolean; format: string; length: string }) {
  const skill = o.speech ? "film-studio" : "film-studio-nospeech";
  return [
    "Make a film with the Film Studio pipeline in this repo.",
    `Read CLAUDE.md, then follow .agents/skills/${skill}/SKILL.md stage by stage.`,
    `Project folder, already created: ${rel}. Work only inside it.`,
    `Master format: ${o.format}. Target length: ${o.length}.`,
    o.framing ? `Also apply ${FRAMING_SKILL}: plan an intro and a bridge between every topic section.` : "",
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
  const id = agentSel.value;
  const session = resume ? store.get(`session:${current.path}:${id}`) || null : null;
  runLevel = level();
  try {
    await invoke("start_agent", {
      agent: id, prompt, session, level: runLevel,
      lean: $<HTMLInputElement>("lean").checked,
      model: modelValue() || null,
      effort: $<HTMLSelectElement>("effort").value || null,
      customCmd: $<HTMLInputElement>("custom-cmd").value || null,
    });
    runStart = Date.now();
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
  $("quick").querySelectorAll("button").forEach((b) => ((b as HTMLButtonElement).disabled = on));
  agentSel.disabled = on;
  levelInputs.forEach((i) => (i.disabled = on));
  renderRunState();
  renderList();
}

function renderRunState() {
  const a = agents.find((x) => x.id === agentSel.value)?.label ?? "Custom agent";
  const rs = $("run-state");
  if (running) {
    const s = Math.floor((Date.now() - runStart) / 1000);
    const t = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
    const model = modelValue();
    rs.textContent = `${a}${model ? ` (${model})` : ""} working · ${t}${runLevel === 2 ? " · full access" : ""}`;
    rs.dataset.state = runLevel === 2 ? "full" : "on";
  } else {
    rs.textContent = `Idle · ${a}`;
    rs.dataset.state = "off";
  }
}
setInterval(() => running && renderRunState(), 1000);

function addLine(l: Line) {
  const log = $("log");
  log.querySelector(".empty-log")?.remove();
  const stick = log.scrollHeight - log.scrollTop - log.clientHeight < 40;
  if (l.kind === "delta" && lastBlock?.dataset.kind === "delta") {
    lastBlock.textContent += l.text;
  } else {
    const p = el("p", `ln ${l.kind}`, l.text);
    p.dataset.kind = l.kind;
    log.append(p);
    lastBlock = p;
    while (log.childElementCount > 2000) log.firstElementChild?.remove();
  }
  if (stick) log.scrollTop = log.scrollHeight;
}

// log filters
document.querySelectorAll<HTMLButtonElement>("[data-filter]").forEach((b) =>
  b.addEventListener("click", () => {
    document.querySelectorAll("[data-filter]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    $("log").dataset.filter = b.dataset.filter!;
  }),
);
$("copy-log").addEventListener("click", async () => {
  await navigator.clipboard.writeText([...$("log").querySelectorAll(".ln")].map((p) => p.textContent).join("\n"));
  toast("Log copied");
});

// token usage, kept per film
function usageKey() { return current ? `usage:${current.path}` : ""; }
function renderUsage() {
  const u: Usage = JSON.parse(store.get(usageKey(), '{"input":0,"cached":0,"output":0,"cost":null}'));
  const k = (n: number) => (n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : String(n));
  $("usage").textContent = u.input + u.output + u.cached
    ? `${k(u.input)} in · ${k(u.cached)} cached · ${k(u.output)} out${u.cost != null ? ` · $${u.cost.toFixed(2)}` : ""}`
    : "";
}
listen<Usage>("agent-usage", (e) => {
  if (!current) return;
  const u: Usage = JSON.parse(store.get(usageKey(), '{"input":0,"cached":0,"output":0,"cost":null}'));
  u.input += e.payload.input; u.cached += e.payload.cached; u.output += e.payload.output;
  if (e.payload.cost != null) u.cost = (u.cost ?? 0) + e.payload.cost;
  store.set(usageKey(), JSON.stringify(u));
  renderUsage();
});

listen<Line>("agent-line", (e) => addLine(e.payload));
listen<string>("agent-session", (e) => {
  if (current) store.set(`session:${current.path}:${agentSel.value}`, e.payload);
});
listen<number | null>("agent-exit", (e) => {
  setRunning(false);
  addLine({ kind: "info", text: e.payload === 0 ? "Agent finished. Reply below to continue." : `Agent stopped (exit ${e.payload ?? "signal"}).` });
  toast(e.payload === 0 ? "Agent finished" : "Agent stopped");
  refresh();
});

$("stop").addEventListener("click", () => invoke("stop_agent"));

function send(text: string) {
  if (!text || running || !current) return;
  addLine({ kind: "info", text: `You: ${text}` });
  const hasSession = !!store.get(`session:${current.path}:${agentSel.value}`);
  const rel = `projects/${current.name}`;
  // a fresh agent (switched tool or no session yet) needs the context restated
  run(hasSession ? text : `Continue the film in ${rel} from its current stage, following its plan.json and .agents/skills/film-studio/SKILL.md.\n${leanRules()}\nUser: ${text}`, hasSession);
}
$("reply-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const ta = $<HTMLTextAreaElement>("reply");
  send(ta.value.trim());
  ta.value = "";
});
$<HTMLTextAreaElement>("reply").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) $<HTMLFormElement>("reply-form").requestSubmit();
});
document.querySelectorAll<HTMLButtonElement>("[data-say]").forEach((b) => b.addEventListener("click", () => send(b.dataset.say!)));

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
    await run(filmPrompt(rel, brief, {
      speech: $<HTMLInputElement>("speech").checked,
      framing: $<HTMLInputElement>("framing").checked,
      format: $<HTMLSelectElement>("format").value,
      length: $<HTMLSelectElement>("length").value,
    }), false);
    $<HTMLFormElement>("new-form").reset();
  } catch (err) {
    $("new-error").textContent = String(err);
  }
});

function open(path: string) {
  current = projects.find((p) => p.path === path) ?? null;
  if (!current) return;
  if (!running) {
    $("log").replaceChildren(el("p", "empty-log", "Nothing yet in this session. Send a message to continue this film."));
  }
  picked = null;
  playing = "";
  renderList();
  renderFilm();
  renderUsage();
  show("film");
}

$<HTMLInputElement>("filter").addEventListener("input", renderList);

function renderList() {
  const q = $<HTMLInputElement>("filter").value.trim().toLowerCase();
  const ul = $("projects");
  const shown = projects.filter((p) => !q || `${p.name} ${p.status.title}`.toLowerCase().includes(q));
  ul.replaceChildren(
    ...shown.map((p) => {
      const li = el("li");
      const b = el("button", "proj");
      b.type = "button";
      if (current?.path === p.path) b.setAttribute("aria-current", "true");
      b.disabled = running && current?.path !== p.path;
      const pct = Math.round(p.status.progress * 100);
      const stage = p.status.stages[p.status.current]?.label ?? "Done";
      const mini = el("span", "mini");
      mini.setAttribute("aria-hidden", "true");
      const fill = el("i");
      fill.style.width = `${pct}%`;
      mini.append(fill);
      b.append(el("span", "proj-name", p.status.title || p.name), el("span", "proj-pct", `${pct}%`), mini, el("span", "proj-stage", stage));
      b.setAttribute("aria-label", `${p.status.title || p.name}, ${pct}% done, ${stage}`);
      b.addEventListener("click", () => open(p.path));
      li.append(b);
      return li;
    }),
  );
  if (!shown.length) ul.append(el("li", "help", projects.length ? "No film matches." : "No films yet."));
}

function fmtTime(s?: number) {
  if (!s) return "";
  return `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, "0")}`;
}

function renderFilm() {
  if (!current) return;
  const s = current.status;
  $("film-title").textContent = s.title || current.name;
  $("film-meta").textContent = current.name;

  // facts
  const m = s.master;
  const facts: [string, string][] = [
    ["Length", fmtTime(m.duration_s) || "not timed yet"],
    ["Format", m.width ? `${m.width}×${m.height} · ${m.fps} fps` : "not set"],
    ["Scenes", s.scenes_total ? `${s.scenes_done}/${s.scenes_total} rendered` : "none yet"],
    ["Voice", m.speech ? (m.voice_engine ? `${m.voice_engine}${m.voice ? ` · ${String(m.voice).split("/").pop()}` : ""}` : "not chosen") : "no speech"],
    ["Captions", m.captions || "not set"],
  ];
  $("facts").replaceChildren(...facts.flatMap(([k, v]) => {
    const d = el("div");
    d.append(el("dt", "", k), el("dd", "", v));
    return [d];
  }));

  // leader strip: each frame is a button that shows its checks
  const sel = picked ?? Math.min(s.current, s.stages.length - 1);
  $("leader").replaceChildren(
    ...s.stages.map((st, i) => {
      const li = el("li");
      const b = el("button", "frame");
      b.type = "button";
      b.dataset.state = st.done ? "done" : i === s.current ? "now" : "todo";
      if (i === s.current) li.setAttribute("aria-current", "step");
      b.setAttribute("aria-pressed", String(i === sel));
      b.append(el("span", "n", st.id), el("span", "l", st.label));
      b.setAttribute("aria-label", `Stage ${st.id}, ${st.label}: ${st.done ? "done" : i === s.current ? "in progress" : "not started"}`);
      b.addEventListener("click", () => { picked = picked === i ? null : i; renderFilm(); });
      li.append(b);
      return li;
    }),
  );

  const pct = Math.round(s.progress * 100);
  $("bar-fill").style.transform = `scaleX(${s.progress})`;
  $("bar").setAttribute("aria-valuenow", String(pct));

  // stage detail
  const st = s.stages[sel];
  const det = $("stage-detail");
  det.replaceChildren();
  const head = el("div", "sd-head");
  const where = s.current >= s.stages.length ? "All stages done" : `Stage ${s.current + 1} of ${s.stages.length}`;
  head.append(el("strong", "", `${st.label}`), el("span", "sd-state", st.done ? "Done" : sel === s.current ? "In progress" : "Not started"), el("span", "sd-pct", `${where} · ${pct}%`));
  det.append(head, el("p", "sd-about", st.about));
  const ul = el("ul", "checks");
  st.checks.forEach((c) => {
    const li = el("li", c.ok ? "ok" : "miss");
    li.append(el("span", "mark", c.ok ? "✓" : "·"), el("span", "", c.label), el("span", "sr", c.ok ? " (done)" : " (missing)"));
    ul.append(li);
  });
  det.append(ul);
  if (st.id === "4" && s.scenes_total) {
    const sb = el("div", "scene-bar");
    s.scenes.forEach((sc) => {
      const i = el("i");
      i.dataset.ok = sc.clip ? "1" : "";
      i.title = `${sc.id}: ${sc.clip ? "rendered" : "not rendered"}`;
      sb.append(i);
    });
    det.append(sb);
  }

  renderScenes(s);
  renderScript(s);
  if (!playing || (playing !== s.final_video && !s.scenes.some((x) => x.clip === playing))) {
    play(s.final_video, "Final film");
  }
  $<HTMLButtonElement>("open-video").disabled = !playing;
}

function play(path: string | null, label: string) {
  const box = $("player");
  if (!path) {
    if (playing) box.replaceChildren(el("p", "empty", "The film appears here after it is assembled."));
    playing = "";
    $("playing").textContent = "";
    return;
  }
  if (path === playing) return;
  playing = path;
  const v = el("video");
  v.controls = true;
  v.preload = "metadata";
  v.src = `${convertFileSrc(path)}?t=${Date.now()}`;
  box.replaceChildren(v);
  $("playing").textContent = `Playing: ${label}`;
}

function renderScenes(s: Status) {
  $("scene-count").textContent = s.scenes_total ? String(s.scenes_total) : "";
  const ol = $("scenes");
  if (!s.scenes.length) {
    ol.replaceChildren(el("li", "help", "Scenes appear after the storyboard stage."));
    return;
  }
  ol.replaceChildren(...s.scenes.map((sc) => {
    const li = el("li", "scene");
    const top = el("div", "sc-top");
    top.append(el("strong", "", sc.id), el("span", "badge", sc.skill ?? "skill not set"), el("span", "sc-len", sc.seconds ? `${sc.seconds.toFixed(1)} s` : ""), el("span", sc.clip ? "sc-ok" : "sc-miss", sc.clip ? "Rendered" : "Not rendered"));
    li.append(top);
    if (sc.brief) li.append(el("p", "sc-brief", sc.brief));
    if (sc.text) li.append(el("p", "sc-text", `“${sc.text}”`));
    if (sc.clip) {
      const b = el("button", "link", "Play clip");
      b.type = "button";
      b.addEventListener("click", () => { play(sc.clip, `scene ${sc.id}`); selectTab("film"); });
      li.append(b);
    }
    return li;
  }));
}

function renderScript(s: Status) {
  $("line-count").textContent = s.lines.length ? String(s.lines.length) : "";
  const ol = $("script");
  if (!s.lines.length) {
    ol.replaceChildren(el("li", "help", s.master.speech ? "The narration appears after the script stage." : "No-speech film: there is no narration."));
    return;
  }
  const words = s.lines.reduce((n, l) => n + (l.text ?? "").split(/\s+/).filter(Boolean).length, 0);
  ol.replaceChildren(
    el("li", "help", `${s.lines.length} lines · ${words} words · about ${fmtTime(words / 2.5)} spoken`),
    ...s.lines.map((l) => {
      const li = el("li", "line");
      li.append(el("span", "line-id", l.id), el("span", "", l.text));
      return li;
    }),
  );
}

// tabs (arrow keys move between them)
const tabs = ["film", "scenes", "script"];
function selectTab(name: string) {
  tabs.forEach((t) => {
    const on = t === name;
    const b = $(`tab-${t}`);
    b.setAttribute("aria-selected", String(on));
    b.tabIndex = on ? 0 : -1;
    $(`panel-${t}`).hidden = !on;
  });
}
tabs.forEach((t, i) => {
  const b = $(`tab-${t}`);
  b.addEventListener("click", () => selectTab(t));
  b.addEventListener("keydown", (e) => {
    const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
    if (!d) return;
    const n = tabs[(i + d + tabs.length) % tabs.length];
    selectTab(n);
    $(`tab-${n}`).focus();
  });
});

$("open-video").addEventListener("click", () => playing && invoke("open_path", { path: playing }));
$("open-folder").addEventListener("click", () => current && invoke("open_path", { path: current.path }).catch((e) => toast(String(e))));

async function refresh() {
  projects = await invoke<Project[]>("list_projects");
  if (current) {
    const prev = current.status.current;
    current = projects.find((p) => p.path === current!.path) ?? current;
    if (current.status.current > prev && prev < current.status.stages.length) toast(`${current.status.stages[prev].label} done`);
  }
  renderList();
  renderFilm();
}

// No browser context menu (Inspect, Reload) outside text fields; fields keep copy/paste.
document.addEventListener("contextmenu", (e) => {
  const t = e.target as HTMLElement;
  if (!t.closest("input, textarea, .log")) e.preventDefault();
});

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
  agentSel.value = store.get("agent", agents.find((a) => a.bin)?.id ?? "custom");
  $<HTMLInputElement>("custom-cmd").value = store.get("custom");
  $<HTMLInputElement>("lean").checked = store.get("lean", "1") === "1";
  // full access never survives a restart: the user re-confirms it each session
  setLevel(Math.min(Number(store.get("level", "1")), 1));
  await onAgentChange();
  setRunning(false);

  const hasFraming = await invoke<boolean>("has_file", { rel: FRAMING_SKILL }).catch(() => false);
  $("framing-wrap").hidden = !hasFraming;

  await refresh();
  show("empty");
  setInterval(() => { if (current || running) refresh(); }, 2000);
})();
