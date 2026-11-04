// arkAgent web UI — talks only to the local server on 127.0.0.1.
const $ = (id) => document.getElementById(id);
let currentPlanId = null;
let listeningPoll = null;

function setCharacter(state, label) {
  const c = $("character");
  c.className = "character " + state;
  if (label) $("charLabel").textContent = label;
  const pill = $("pill");
  pill.className = "pill " + state;
  pill.textContent = "● " + state.charAt(0).toUpperCase() + state.slice(1);
}
function log(text) {
  const el = $("log");
  el.textContent += text + "\n";
  el.scrollTop = el.scrollHeight;
}
function hidePanels() {
  $("taskPlan").classList.add("hidden");
  $("suggestionBar").classList.add("hidden");
}
async function post(path, data) {
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data || {}) });
  return res.json();
}
function handleResponse(data) {
  if (data.type === "task_plan") {
    currentPlanId = data.plan_id;
    $("taskTitle").textContent = data.title;
    $("taskSteps").innerHTML = "";
    data.steps.forEach((s) => { const li = document.createElement("li"); li.textContent = s; $("taskSteps").appendChild(li); });
    $("taskPlan").classList.remove("hidden");
    setCharacter("working", data.message);
    log(data.message);
    return;
  }
  if (data.type === "ask") {
    $("suggestionText").textContent = data.message;
    $("suggestionBar").classList.remove("hidden");
    setCharacter("speaking", data.message);
    log(data.message);
    return;
  }
  const messages = data.messages || (data.message ? [data.message] : []);
  messages.forEach((m) => log(m));
  setCharacter(data.state || "idle", messages[messages.length - 1] || "");
}
async function sendCommand(text) {
  if (!text.trim()) return;
  hidePanels();
  log("> " + text);
  setCharacter("working", "Working on it...");
  try {
    const data = await post("/api/command", { text });
    handleResponse(data);
  } catch (e) {
    log("Could not reach the local server. Is run_web.bat still running?");
    setCharacter("error", "Server not reachable.");
  }
}
$("runBtn").onclick = () => { const t = $("commandInput").value; $("commandInput").value = ""; sendCommand(t); };
$("commandInput").addEventListener("keydown", (e) => { if (e.key === "Enter") $("runBtn").click(); });
document.querySelectorAll("[data-cmd]").forEach((b) => { b.onclick = () => sendCommand(b.dataset.cmd); });
$("confirmTaskBtn").onclick = async () => {
  if (!currentPlanId) return;
  setCharacter("working", "Running task...");
  const data = await post("/api/execute_task", { plan_id: currentPlanId });
  currentPlanId = null;
  $("taskPlan").classList.add("hidden");
  handleResponse(data);
};
$("cancelTaskBtn").onclick = () => { currentPlanId = null; $("taskPlan").classList.add("hidden"); log("Task cancelled."); setCharacter("idle", "Ready."); };
$("suggestionYes").onclick = () => sendCommand("yes");
$("suggestionNo").onclick = () => sendCommand("no");
$("saveSettingsBtn").onclick = async () => {
  const data = await post("/api/settings", { vosk_model_path: $("modelPath").value, default_browser: $("defaultBrowser").value });
  $("settingsMsg").textContent = data.message || "Saved.";
};
$("stopDictationBtn").onclick = async () => {
  const data = await post("/api/stop_dictation", {});
  $("dictationBanner").classList.add("hidden");
  log(data.message);
};
$("searchBtn").onclick = async () => {
  const q = $("searchInput").value;
  const res = await fetch("/api/commands?q=" + encodeURIComponent(q));
  const data = await res.json();
  log("Commands matching '" + q + "': " + (data.commands.join(", ") || "none"));
};
$("listenBtn").onclick = async () => {
  setCharacter("listening", "Listening...");
  log("Listening... (one utterance, up to 30 seconds)");
  await post("/api/listen", {});
  if (listeningPoll) clearInterval(listeningPoll);
  listeningPoll = setInterval(async () => {
    const res = await fetch("/api/listen_result");
    const data = await res.json();
    if (!data.result) return;
    clearInterval(listeningPoll);
    const r = data.result;
    if (r.text) { $("lastHeard").textContent = r.text; log("Heard: " + r.text); }
    if (r.mode === "dictation") {
      $("dictationBanner").classList.remove("hidden");
      log("Dictation: " + r.dictation_text);
      setCharacter("speaking", "Dictation on.");
    } else if (r.mode === "command" && r.text) {
      sendCommand(r.text);
    } else {
      log(r.message || "I did not hear anything.");
      setCharacter("error", r.message || "");
    }
  }, 600);
};
$("stopBtn").onclick = () => { setCharacter("idle", "Ready."); log("Stopped."); };
(async () => {
  try {
    const res = await fetch("/api/status");
    const s = await res.json();
    if (s.vosk_model_path) $("modelPath").value = s.vosk_model_path;
    if (s.default_browser) $("defaultBrowser").value = s.default_browser;
    if (s.mode === "dictation") $("dictationBanner").classList.remove("hidden");
    log("Welcome to arkAgent v2. Type a task, or press Listen.\nExamples: open chrome and search for cats • create a word document and type hello");
  } catch (e) { log("Could not reach the local server."); }
})();
