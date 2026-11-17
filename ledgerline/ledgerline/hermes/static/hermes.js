/* Hermes · Lecture 5 · The Habits. Vanilla JS, no build step. One file, one section per tab. */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const E = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fmt = n => (n == null ? "–" : Number(n).toLocaleString("en-GB"));
const usd = v => v == null ? "–" : (v < 0.01 ? "US$" + Number(v).toFixed(4) : "US$" + Number(v).toFixed(3));
const secs = v => v == null ? "–" : (v < 10 ? Number(v).toFixed(1) : Math.round(v)) + " s";
const KEYNAME = "hermes-key";
let KEY = null, ME = null, CAT = null, TAB = "memory";
try { KEY = localStorage.getItem(KEYNAME); } catch (e) { KEY = null; }

/* ------------------------------------------------------------------ api, jobs, toast */
async function api(path, body, method) {
  const opt = {method: method || (body !== undefined ? "POST" : "GET"), headers: {"Content-Type": "application/json"}};
  if (KEY) opt.headers["X-Hermes-Key"] = KEY;
  if (body !== undefined) opt.body = JSON.stringify(body);
  const r = await fetch(path, opt);
  let j = null;
  try { j = await r.json(); } catch (e) { j = null; }
  if (!r.ok) throw new Error((j && j.detail) || ("The server said " + r.status));
  return j;
}
async function poll(jid, onEvents, every = 600) {
  let since = 0;
  for (;;) {
    const j = await api(`/api/job/${jid}?since=${since}`);
    const evs = j.progress.events || [];
    since += evs.length;
    if (onEvents && (evs.length || j.state !== "running")) onEvents(evs, j);
    if (j.state !== "running") {
      if (j.state === "failed") throw new Error(j.error || "It failed.");
      return j;
    }
    await sleep(every);
  }
}
let toastT;
function toast(msg, ms = 3200) {
  const t = $("#toast"); t.textContent = msg; t.classList.add("on");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("on"), ms);
}
function busy(btn, on, label) {
  if (!btn) return;
  if (on) { btn.dataset.l = btn.innerHTML; btn.disabled = true; btn.innerHTML = `<span class="spin"></span>${label || ""}`; }
  else { btn.disabled = false; if (btn.dataset.l) btn.innerHTML = btn.dataset.l; }
}
function drawer(title, html) {
  $("#dtitle").textContent = title; $("#dbody").innerHTML = html;
  $("#drawer").classList.add("on"); $("#scrim").classList.add("on");
}
function closeDrawer() { $("#drawer").classList.remove("on"); $("#scrim").classList.remove("on"); }
$("#dclose").onclick = closeDrawer; $("#scrim").onclick = closeDrawer;
document.addEventListener("keydown", e => { if (e.key === "Escape") closeDrawer(); });

/* ------------------------------------------------------------------ icons */
const I = {
  trigger: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
  schedule: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  form: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
  event: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 12h4l3-8 4 16 3-8h2"/></svg>',
  tool: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 0 0 5 5L22 14l-8 8-2.3-2.3a4 4 0 0 0-5-5L4 12l8-8z"/></svg>',
  condition: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3 21 12 12 21 3 12z"/></svg>',
  approval: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
  llm: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3l2.2 5.8L20 11l-5.8 2.2L12 19l-2.2-5.8L4 11l5.8-2.2z"/></svg>',
  message: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 5h16v11H8l-4 4z"/></svg>',
  set: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 8h14M5 16h14"/></svg>',
  foreach: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="7" width="13" height="13" rx="2"/><path d="M8 4h11a2 2 0 0 1 2 2v11"/></svg>',
  check: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#12805a" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
  cross: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#c03a2b" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
  clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  box: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 7 12 3l9 4-9 4-9-4zM3 7v10l9 4 9-4V7M12 11v10"/></svg>',
  receipt: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 2h12v20l-3-2-3 2-3-2-3 2zM9 7h6M9 11h6M9 15h4"/></svg>',
  badge: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="9" r="6"/><path d="M8.5 14 7 22l5-3 5 3-1.5-8"/></svg>',
  chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/></svg>',
  scale: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0zM8 21h8"/></svg>',
  inbox: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 13h5l1 3h6l1-3h5M5 5h14l2 8v6H3v-6z"/></svg>',
  mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
  slack: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 3v18M15 3v18M3 9h18M3 15h18"/></svg>',
  db: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/></svg>',
  moon: '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M21 13A9 9 0 1 1 11 3a7 7 0 0 0 10 10z"/></svg>',
  plus: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  spark: '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.4 6.6L21 11l-6.6 2.4L12 20l-2.4-6.6L3 11l6.6-2.4z"/></svg>',
};
const ICON_OF = {chase: "clock", reorder: "box", invoices: "receipt", onboard: "badge", spend: "chart"};
function nodeIcon(n) {
  if (n.type === "trigger") return I[{schedule: "schedule", form: "form", event: "event"}[(n.config || {}).kind] || "trigger"];
  return I[n.type] || I.tool;
}
const PEOPLE_SHORT = {ECLARKE: "Emma", DOKAFOR: "Daniel", LMORENO: "Luis", ATANAKA: "Aiko", LHUGHES: "Laura"};

/* ------------------------------------------------------------------ guides (what to try, what to notice, next) */
const GUIDES = {
  memory: ["Run Emma's week with <b>Notes + search</b>, then with <b>No memory</b>. Turn <b>provenance</b> off and run Notes + search again. Shrink the window to 2,000.",
           "Which questions each design gets right; tokens per turn; the <b>poisoned</b> answer about Nordic Cell; the background writer missing Tuesday's correction on Tuesday afternoon; the window, part by part.",
           "Pick the design you trust and press <b>Use the selected design in Ask Northbridge</b>. Then 2 · Workflows."],
  workflows: ["Pick <b>Process this week's invoices</b> and build it. Run it on the 40 invoices. Set the tolerance to 0 and run again. Then type a task of your own.",
              "The model only writes JSON; code checks each step against the tool's own tool.json. The <b>parameters</b> are what may change per run. The batch tally, the time and the cost.",
              "<b>Save as my routine</b>: it becomes a tool in Ask Northbridge, and a scheduled one runs on the clock. Then 3 · Background agents."],
  agents: ["Turn on the <b>three-way match</b> and the <b>late-order chaser</b>, then press <b>+1 week</b>. Open a run. Try <b>Stop all</b>.",
           "Wednesday 02:00: Ledgerline is down; the run retries at 02:15 and 02:30 without spending a token. Drafts are never sent. What each run changed and left for a person.",
           "4 · Triggers: start the work when something arrives, not on a timer."],
  triggers: ["Drop an <b>invoice e-mail</b>, then <b>the same e-mail twice</b>, then <b>the resent invoice</b>. Aiko's Slack message. Turn on the memory listener; drop the <b>poisoned e-mail</b> with provenance on, then off.",
             "Poll against push timing. Two kinds of duplicate, stopped in two different places. The poisoned note quarantined (on) or filed like Emma's own words (off).",
             "5 · Ask Northbridge: say <b>Morning</b>."],
  ask: ["Say <b>Morning</b>. Then <b>Run my Monday chase</b>, <b>What came in?</b>, <b>Order the usual</b>.",
        "It knows Emma before she speaks (memory), tells her what ran overnight (background agents) and what arrived (triggers), and runs her routine on a word (workflows). The window, part by part.",
        "Lecture 6 · Trust: what may it do on its own, and who checks?"],
};
function renderGuides() {
  for (const [k, [a, b, c]] of Object.entries(GUIDES)) {
    $(`#guide-${k}`).innerHTML = `<div class="try"><h4><i></i>What to try</h4><p>${a}</p></div>
      <div class="notice"><h4><i></i>What to notice</h4><p>${b}</p></div><div class="next"><h4><i></i>Next</h4><p>${c}</p></div>`;
  }
}

/* ------------------------------------------------------------------ join, tabs, clock, approvals */
async function boot() {
  CAT = await api("/api/catalog");
  if (KEY) {
    try { ME = await api("/api/me"); $("#wname").textContent = ME.name; $("#welcome").classList.remove("hide"); $("#joinform").classList.add("hide"); $("#keyline").classList.add("hide"); }
    catch (e) { KEY = null; try { localStorage.removeItem(KEYNAME); } catch (x) {} }
  }
  const q = new URLSearchParams(location.search);
  if (q.get("key") && !ME) { KEY = q.get("key"); try { ME = await api("/api/me"); saveKey(); enter(); return; } catch (e) { KEY = null; } }
  if (ME && q.get("go")) enter();
}
function saveKey() { try { localStorage.setItem(KEYNAME, KEY); } catch (e) {} }
$("#joinform").onsubmit = async e => {
  e.preventDefault();
  busy($("#joinbtn"), true, "Opening");
  try { ME = await api("/api/join", {name: $("#name").value}); KEY = ME.key; saveKey(); enter(); }
  catch (err) { toast(err.message); } finally { busy($("#joinbtn"), false); }
};
$("#enter").onclick = () => enter();
$("#notme").onclick = e => { e.preventDefault(); try { localStorage.removeItem(KEYNAME); } catch (x) {} KEY = null; ME = null; location.reload(); };
$("#usekey").onclick = e => { e.preventDefault(); const k = prompt("Paste your Hermes key (hm-…)"); if (k) { KEY = k.trim(); saveKey(); location.reload(); } };
function enter() {
  $("#join").classList.add("hide"); $("#lab").classList.remove("hide");
  $("#avatar").textContent = (ME.name || "?").trim()[0].toUpperCase(); $("#avatar").title = ME.name + " · your key: " + KEY;
  renderGuides(); setClock(ME.clock); initMemory(); initFlows(); initAgents(); initTriggers(); initAsk();
  go((location.hash || "#memory").slice(1)); refreshInbox(); setInterval(refreshInbox, 20000);
}
function go(t) {
  if (!["memory", "workflows", "agents", "triggers", "ask"].includes(t)) t = "memory";
  TAB = t;
  $$(".tabs a").forEach(a => a.classList.toggle("on", a.dataset.tab === t));
  $$(".tab").forEach(s => s.classList.toggle("on", s.id === "tab-" + t));
  if (t === "agents") loadAgents(); if (t === "triggers") loadTriggers(); if (t === "ask") loadAsk(); if (t === "workflows") renderShelf();
  window.scrollTo({top: 0});
}
window.addEventListener("hashchange", () => go(location.hash.slice(1)));
function setClock(c) { if (c) { $("#clockt").textContent = c.label; if (ME) ME.clock = c; } }
async function playClock(action, btns) {
  btns.forEach(b => busy(b, true, action === "week" ? "Playing the week" : "Playing"));
  try {
    const j0 = await api("/api/clock", {action});
    let n = 0;
    const j = await poll(j0.id, (evs, j) => {
      n += evs.length;
      if (j.progress.of) $("#clockt").textContent = `Running ${n} of ${j.progress.of}…`;
      evs.forEach(r => AG.onRun && AG.onRun(r));
    }, 700);
    setClock(j.result.clock);
    toast(j.result.runs ? `${j.result.runs} run(s) on the way · ${usd(j.result.usd)}` : "Nothing was due. Turn an agent on in 3 · Background agents.");
    if (TAB === "agents") loadAgents(); if (TAB === "ask") loadAsk(); refreshInbox();
  } catch (e) { toast(e.message); setClock(ME.clock); }
  finally { btns.forEach(b => busy(b, false)); }
}
$("#ctomorrow").onclick = () => playClock("tomorrow", [$("#ctomorrow"), $("#btomorrow")]);
$("#cweek").onclick = () => playClock("week", [$("#cweek"), $("#bweek")]);
async function refreshInbox() {
  try { const r = await api("/api/inbox"); const n = r.waiting.length; $("#inboxn").textContent = n; $("#inboxn").classList.toggle("hide", !n); return r; } catch (e) { return null; }
}
$("#inboxbtn").onclick = async () => {
  const r = await refreshInbox();
  const rows = (r && r.waiting) || [];
  drawer("Approvals", `<p class="muted small" style="margin-bottom:12px">Sign as the approver, with their own Ledgerline permissions. Daniel Okafor approves above Emma's £250,000 limit; Laura Hughes covers for him.</p>` +
    (rows.length ? rows.map(w => `<div class="inbox-item"><div style="flex:1"><b class="mono">${E(w.doc_no)}</b> <span class="muted">${E(w.item_code || "")} × ${fmt(w.quantity)}</span><br>
      <span class="small muted">£${fmt(w.value)} · raised by ${E(w.requested_by)} · for ${E(w.approver_name)}</span></div>
      <button class="btn sm" data-sign="${E(w.doc_no)}" data-as="${w.approver}" data-d="reject">Reject</button>
      <button class="btn sm primary" data-sign="${E(w.doc_no)}" data-as="${w.approver}" data-d="approve">Approve as ${E(PEOPLE_SHORT[w.approver])}</button></div>`).join("")
      : `<div class="empty">Nothing waits for a signature.</div>`));
  $$("[data-sign]", $("#dbody")).forEach(b => b.onclick = async () => {
    busy(b, true);
    try { const o = await api("/api/inbox/sign", {doc_no: b.dataset.sign, decision: b.dataset.d, as: b.dataset.as});
      toast(o.result.ok ? `${b.dataset.sign}: ${o.result.status || "signed"}` : o.result.error); $("#inboxbtn").click();
      if (FL.run && FL.run.status === "waiting") FL.showResult();
    } catch (e) { toast(e.message); busy(b, false); }
  });
};

/* ================================================================== 1 · MEMORY */
const PART = {system: ["System and rules", "#58606e"], profile: ["Profile (always loaded)", "#6b4bd6"], memory: ["Memory files", "#3550c4"],
  briefing: ["While you were away", "#12805a"], retrieved: ["Retrieved notes", "#0d8a8a"], history: ["Conversation history", "#b9770e"],
  message: ["This message", "#0b57d0"], working: ["Tool calls", "#bf3d86"], tools: ["Tool definitions", "#b4b7bd"]};
const PART_ORDER = ["system", "profile", "memory", "briefing", "history", "retrieved", "working", "message", "tools"];
const VERDICT = {right: ["good", "right"], stale: ["warn", "stale"], poisoned: ["bad", "poisoned"], missing: ["slate", "missing"], wrong: ["bad", "wrong"]};
const MM = {design: "openclaw", knobs: null, res: {}, live: null, sel: null, day: -1, file: null, running: false};
function initMemory() {
  MM.knobs = {...CAT.designs.find(d => d.id === MM.design).knobs};
  renderDesigns(); renderKnobs(); renderStrip(); renderMemTable();
  $("#runweek").onclick = runWeek; $("#compare").onclick = compareAll;
  $("#usemem").onclick = async () => {
    try { const v = await api("/api/memory/use", {design: MM.design}); ME.memory = v.memory; toast(`Ask Northbridge now uses ${v.memory.title} (your week).`); }
    catch (e) { toast(e.message); }
  };
  $("#showwin").onclick = showWindow;
}
function dmeta(id) { return CAT.designs.find(d => d.id === id); }
function renderDesigns() {
  $("#designs").innerHTML = CAT.designs.map(d => {
    const r = MM.res[d.id];
    return `<button class="design ${d.id === MM.design ? "on" : ""}" data-d="${d.id}"><div class="t">${E(d.title)}<span class="k">${E(d.kicker)}</span>
      ${r ? `<span class="sc pill ${r.score.right >= 8 ? "good" : r.score.right >= 5 ? "accent" : "slate"}">${r.score.right}/${r.score.of}</span>` : ""}</div><p>${E(d.line)}</p></button>`;
  }).join("");
  $$(".design").forEach(b => b.onclick = () => {
    if (MM.running) return;
    MM.design = b.dataset.d; MM.knobs = {...dmeta(MM.design).knobs};
    renderDesigns(); renderKnobs();
    if (MM.res[MM.design]) showResult(MM.res[MM.design]); else { MM.live = null; MM.sel = null; renderStrip(); $("#convo").innerHTML = `<div class="empty">Press <b>Run Emma's week</b>.</div>`; $("#probes").innerHTML = ""; $("#files").innerHTML = ""; $("#ctxpanel").innerHTML = `<div class="empty">Run the week first.</div>`; $("#dayseg").innerHTML = ""; }
  });
}
function renderKnobs() {
  const d = dmeta(MM.design), fixed = d.fixed || [], k = MM.knobs;
  const seg = (name, vals, labels) => `<div class="seg" data-k="${name}">${vals.map((v, i) => `<button class="${k[name] === v ? "on" : ""}" data-v="${v}" ${fixed.includes(name) || (name === "writer" && ["none", "full"].includes(MM.design)) ? "disabled" : ""}>${labels[i]}</button>`).join("")}</div>`;
  const sw = (name) => `<button class="switch ${k[name] ? "on" : ""}" data-sw="${name}" ${fixed.includes(name) ? "disabled" : ""}></button>`;
  const alwaysWhat = {none: "nothing to load", full: "every earlier conversation", profile: "USER.md", openclaw: "AGENTS, USER, MEMORY + 2 days of notes", instinct: "the one-pager"}[MM.design];
  const searchWhat = {openclaw: "memory_search: hybrid", instinct: "grep_memory: keywords"}[MM.design] || "search_chats: past chats";
  $("#knobs").innerHTML = `
    <div class="knob"><div class="n">Window budget<small>tokens the harness may fill</small></div>${seg("window", CAT.windows, CAT.windows.map(w => (w / 1000) + "k"))}</div>
    <div class="knob"><div class="n">Always loaded<small>${alwaysWhat}</small></div>${sw("always")}</div>
    <div class="knob"><div class="n">Search<small>${searchWhat}</small></div>${sw("search")}</div>
    <div class="knob"><div class="n">Who writes</div>${seg("writer", CAT.writers, ["nobody", "agent", "night", "both"])}</div>
    <div class="knob"><div class="n">Provenance<small>e-mail text marked untrusted</small></div>${sw("provenance")}</div>`;
  $$("#knobs .seg").forEach(s => $$("button", s).forEach(b => b.onclick = () => { const v = b.dataset.v; MM.knobs[s.dataset.k] = isNaN(+v) ? v : +v; renderKnobs(); }));
  $$("#knobs [data-sw]").forEach(b => b.onclick = () => { MM.knobs[b.dataset.sw] = !MM.knobs[b.dataset.sw]; renderKnobs(); });
  const ch = Object.keys(d.knobs).filter(x => d.knobs[x] !== MM.knobs[x]);
  $("#knobstate").textContent = ch.length ? `${ch.length} changed` : "as designed";
  $("#knobstate").className = "pill " + (ch.length ? "warn" : "");
}
function timeline() {
  const W = CAT.week, days = {};
  const dkey = iso => iso.slice(0, 10);
  W.sessions.forEach(s => (days[dkey(s.at)] = days[dkey(s.at)] || []).push({kind: "session", id: s.id, at: s.at, title: s.title, s}));
  W.probes.filter(p => p.at < W.sessions[W.sessions.length - 1].at).forEach(p => (days[dkey(p.at)] = days[dkey(p.at)] || []).push({kind: "probe", id: p.id, at: p.at, title: "Question: " + p.title, p}));
  Object.keys(days).forEach(d => days[d].push({kind: "night", id: "n" + d, at: d + "T23:00:00", title: "Night"}));
  const later = W.probes.filter(p => p.at >= W.sessions[W.sessions.length - 1].at);
  return {days, later};
}
function renderStrip() {
  const {days, later} = timeline(), r = MM.live || MM.res[MM.design];
  const seen = new Set(), probesDone = {};
  if (r) { (r.turns || []).forEach(t => seen.add(t.session)); (r.probes || []).forEach(p => probesDone[p.probe] = p.verdict); (r.nights || []).forEach(n => seen.add("n" + n.at.slice(0, 10))); }
  const nightLabel = d => ({openclaw: "Dreaming", instinct: "Ingestion", profile: "Profile rewrite"})[MM.design] || "Night";
  const chips = items => items.sort((a, b) => a.at.localeCompare(b.at)).map(x => {
    const tm = x.kind === "night" ? "23:00" : x.at.slice(11, 16);
    const sel = MM.sel && MM.sel.id === x.id ? "on" : "";
    const done = x.kind === "probe" ? probesDone[x.id] : seen.has(x.id);
    const v = x.kind === "probe" && probesDone[x.id] ? `<span class="v pill ${VERDICT[probesDone[x.id]][0]}" style="height:18px;padding:0 6px;font-size:10.5px">${VERDICT[probesDone[x.id]][1]}</span>` : "";
    const nightOn = x.kind === "night" && r && (r.nights || []).some(n => "n" + n.at.slice(0, 10) === x.id);
    return `<div class="chip ${x.kind === "night" ? "night" : ""} ${sel} ${r && !done && !nightOn ? "pending" : ""} ${MM.running && MM.next === x.id ? "live" : ""}" data-sel="${x.kind}:${x.id}">
      <span class="tm">${x.kind === "night" ? I.moon + " " : ""}${tm}</span>${E(x.kind === "night" ? nightLabel() : shortTitle(x.title))}${v}</div>`;
  }).join("");
  const names = Object.keys(days).sort();
  $("#weekstrip").innerHTML = names.map(d => { const dt = new Date(d + "T12:00:00"); return `<div class="day"><h5>${dt.toLocaleDateString("en-GB", {weekday: "short", day: "numeric", month: "short"})}</h5>${chips(days[d])}</div>`; }).join("")
    + `<div class="day probes"><h5>Mon 2 Nov <span class="muted">09:00</span></h5>${later.map(p => {
      const v = probesDone[p.id]; return `<div class="chip pr ${MM.sel && MM.sel.id === p.id ? "on" : ""} ${r && !v ? "pending" : ""}" data-sel="probe:${p.id}"><span>${E(p.title)}</span>${v ? `<span class="pill ${VERDICT[v][0]}" style="height:18px;padding:0 6px;font-size:10.5px">${VERDICT[v][1]}</span>` : ""}</div>`;
    }).join("")}</div>`;
  $$("#weekstrip [data-sel]").forEach(c => c.onclick = () => { const [k, id] = c.dataset.sel.split(":"); MM.sel = {kind: k, id}; renderStrip(); renderSel(); });
}
function shortTitle(t) { return String(t).replace(/^(Monday|Tuesday|Wednesday|Thursday|Friday)( morning| afternoon)?: /, "").replace(/^Question: /, "Question: "); }
function curRes() { return MM.live || MM.res[MM.design]; }
function renderSel() {
  const r = curRes(); if (!r || !MM.sel) return;
  if (MM.sel.kind === "session") {
    const turns = r.turns.filter(t => t.session === MM.sel.id);
    if (!turns.length) { $("#convo").innerHTML = `<div class="empty">Not reached yet.</div>`; return; }
    $("#convo").innerHTML = `<div class="small muted">${E(turns[0].title || "")} · ${new Date(turns[0].at).toLocaleString("en-GB", {weekday: "long", hour: "2-digit", minute: "2-digit"})}</div>` + turns.map((t, i) => turnHTML(t, r.turns.indexOf(t))).join("");
    $$("#convo [data-turn]").forEach(b => b.onclick = () => showCtx("turn", +b.dataset.turn));
    showCtx("turn", r.turns.indexOf(turns[turns.length - 1]));
  } else if (MM.sel.kind === "probe") {
    const i = r.probes.findIndex(p => p.probe === MM.sel.id); const p = r.probes[i];
    if (!p) { $("#convo").innerHTML = `<div class="empty">Not asked yet.</div>`; return; }
    $("#convo").innerHTML = `<div class="small muted">A fresh conversation · ${new Date(p.at).toLocaleString("en-GB", {weekday: "long", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"})} · read only</div>` + turnHTML(p, i, true)
      + `<div class="row"><span class="pill ${VERDICT[p.verdict][0]}">${VERDICT[p.verdict][1]}</span><span class="small muted">${E(p.why)}</span></div>`;
    $$("#convo [data-turn]").forEach(b => b.onclick = () => showCtx("probe", i));
    showCtx("probe", i);
  } else {
    const n = (r.nights || []).find(x => "n" + x.at.slice(0, 10) === MM.sel.id);
    $("#convo").innerHTML = n ? `<div class="bub bot" style="max-width:100%"><b>${E(n.kind)}</b> · ${E(n.label)}<br>${E(n.diary || (n.commit && n.commit.message) || n.note || "")}
      ${n.skipped_untrusted ? `<br><span class="pill bad" style="margin-top:6px">${n.skipped_untrusted} untrusted note(s) not promoted</span>` : ""}
      ${n.commit ? `<br><span class="small muted">changed: ${E((n.commit.files || []).join(", "))}</span>` : ""}
      <br><span class="small muted">${fmt(n.tokens_in)} tokens in · ${usd(n.usd)}</span></div>`
      : `<div class="empty">Nobody writes at night in this design (who writes: ${E((r.knobs || MM.knobs).writer)}).</div>`;
    const idx = (r.days || []).findIndex(d => d.at && d.at.slice(0, 10) === MM.sel.id.slice(1));
    if (idx >= 0) { MM.day = idx; renderFiles(); }
  }
}
function turnHTML(t, idx, probe) {
  const att = t.attachment ? `<div class="att">${E((t.attachment.kind === "email" ? "E-mail from " : "Pasted: ") + t.attachment.from + "\n" + t.attachment.subject + "\n\n" + t.attachment.body)}</div>` : "";
  const tools = (t.tool_calls || []).map(c => {
    const w = (t.writes || []).find(x => c.name === "memory_append" || c.name === "update_profile");
    const cls = ["memory_append", "update_profile"].includes(c.name) ? (c.ok === false ? "u" : "w") : "r";
    const untrusted = (t.writes || []).some(x => x.prov === "untrusted") && cls === "w";
    return `<span class="tchip ${untrusted ? "u" : cls}" title="${E(JSON.stringify(c.args))}">${E(c.name)}${c.args && (c.args.query || c.args.text) ? ` <span style="font-family:var(--font);font-weight:400">${E(String(c.args.query || c.args.text).slice(0, 60))}</span>` : ""}${untrusted ? " · untrusted" : ""}</span>`;
  }).join("");
  const extra = [t.flushed ? `<span class="tchip w">memory flush before compaction: ${(t.flushed.saved || []).length} saved</span>` : "",
    t.compacted ? `<span class="tchip">compacted: ${t.compacted.dropped} messages → a summary</span>` : "",
    t.trimmed ? `<span class="tchip">${t.trimmed} oldest message(s) cut to fit the window</span>` : ""].join("");
  return `<div class="bub emma" data-turn="${idx}" style="cursor:pointer">${E(probe ? t.q : t.text)}${att}</div>
    ${tools || extra ? `<div class="toolline">${extra}${tools}</div>` : ""}
    <div class="bub bot" data-turn="${idx}" style="cursor:pointer">${E(t.reply)}<div class="tiny muted" style="margin-top:6px">${fmt(t.tokens_in)} tokens in · ${t.calls.length} call${t.calls.length > 1 ? "s" : ""} · ${secs(t.seconds)}</div></div>`;
}
function ctxBar(parts, budget) {
  const total = Object.values(parts).reduce((a, b) => a + b, 0) || 1;
  const keys = PART_ORDER.filter(k => parts[k]);
  return `<div class="ctx">${keys.map(k => `<i style="width:${(parts[k] / Math.max(total, budget || 0)) * 100}%;background:${PART[k][1]}" title="${PART[k][0]}: ${fmt(parts[k])}"></i>`).join("")}</div>
    <div class="legend">${keys.map(k => `<span><i style="background:${PART[k][1]}"></i>${PART[k][0]}</span><b>${fmt(parts[k])}</b>`).join("")}
    <span style="border-top:1px solid var(--line);padding-top:6px;font-weight:500;color:var(--ink)">Total read by the model</span><b style="border-top:1px solid var(--line);padding-top:6px">${fmt(total)}</b></div>`;
}
function showCtx(kind, i, call) {
  const r = curRes(); const rows = kind === "turn" ? r.turns : r.probes; const t = rows[i]; if (!t) return;
  const c = t.calls[call == null ? t.calls.length - 1 : call];
  MM.ctx = {kind, i, call: call == null ? t.calls.length - 1 : call};
  const budget = (r.knobs || MM.knobs).window;
  $("#ctxpanel").innerHTML = `<div class="row" style="margin-bottom:10px"><b class="small">${E(kind === "probe" ? t.title : (t.text || "").slice(0, 54) + "…")}</b><span class="sp"></span>
      ${t.calls.length > 1 ? `<div class="seg">${t.calls.map((x, k) => `<button class="${k === MM.ctx.call ? "on" : ""}" data-c="${k}">call ${k + 1}</button>`).join("")}</div>` : ""}</div>
    ${ctxBar(c.parts, budget)}
    <div class="budget"><span>Window budget ${fmt(budget)} (harness estimate)</span><span>${fmt(c.tokens_in)} counted by the model</span></div>
    <p class="small muted" style="margin-top:10px">Parts are estimated from their text and scaled to the model's own count. ${c.parts.retrieved ? "Teal: what search brought back this turn." : ""}</p>`;
  $$("#ctxpanel [data-c]").forEach(b => b.onclick = () => showCtx(kind, i, +b.dataset.c));
}
async function showWindow() {
  if (!MM.ctx || MM.live) { toast("Pick a turn first (after the run finishes)."); return; }
  try {
    const w = await api(`/api/memory/window?design=${MM.design}&kind=${MM.ctx.kind}&i=${MM.ctx.i}&call=${MM.ctx.call}`);
    const msgs = w.window.messages.map(m => `<div class="wtext"><span class="tag pill ${m.role === "user" ? "accent" : m.role === "tool" ? "violet" : "slate"}">${m.role}</span>${E(m.content || JSON.stringify(m.tool_calls || ""))}</div>`).join("");
    drawer(`The exact window · ${fmt(w.tokens_in)} tokens`, `<p class="small muted" style="margin-bottom:10px">Everything the model read for this call, in order. Tools offered: ${E(w.window.tools.join(", ") || "none")}.</p>
      <div class="wtext"><span class="tag pill slate">system</span>${E(w.window.system)}</div>${msgs}`);
  } catch (e) { toast(e.message); }
}
function renderProbes(r) {
  const ps = (r.probes || []).slice().sort((a, b) => a.at.localeCompare(b.at));
  $("#probescore").innerHTML = r.score ? `<span class="pill ${r.score.right >= 8 ? "good" : "accent"}">${r.score.right} of ${r.score.of} right</span> ${r.score.stale ? `<span class="pill warn">${r.score.stale} stale</span>` : ""} ${r.score.poisoned ? `<span class="pill bad">${r.score.poisoned} poisoned</span>` : ""}` : "";
  $("#probes").innerHTML = ps.length ? ps.map((p, k) => `<div class="probe"><div class="q">${E(p.title)}<small>${p.probe === "p10" ? "Tue 27 Oct 15:00" : "Mon 2 Nov 09:00"}</small></div>
    <div class="a"><span class="muted">${E(p.q)}</span><br>${E(p.reply)}</div><div class="verdict"><span class="pill ${VERDICT[p.verdict][0]}">${VERDICT[p.verdict][1]}</span></div></div>`).join("") : `<div class="empty">The questions come after the week.</div>`;
}
function renderFiles() {
  const r = curRes(); if (!r || !r.days || !r.days.length) { $("#files").innerHTML = `<div class="empty" style="grid-column:1/-1">No files yet.</div>`; return; }
  if (MM.day < 0 || MM.day >= r.days.length) MM.day = r.days.length - 1;
  $("#dayseg").innerHTML = r.days.map((d, i) => `<button class="${i === MM.day ? "on" : ""}" data-i="${i}">${E(d.label.replace("After the week", "After").replace(/ \d+ \w+$/, ""))}</button>`).join("");
  $$("#dayseg button").forEach(b => b.onclick = () => { MM.day = +b.dataset.i; renderFiles(); });
  const day = r.days[MM.day], files = Object.keys(day.files).sort();
  if (!files.length) { $("#files").innerHTML = `<div class="empty" style="grid-column:1/-1">${MM.design === "full" ? "Full history keeps no files: it pastes the transcripts back." : "This design keeps no memory files."}</div>`; return; }
  if (!MM.file || !files.includes(MM.file)) MM.file = files.find(f => day.diff[f]) || files[0];
  const diff = day.diff[MM.file] || {added: [], removed: []};
  const added = new Set(diff.added);
  const body = (day.files[MM.file] || "").split("\n").map(l => added.has(l) && l.trim() ? `<span class="add">${E(l)}</span>` : E(l)).join("\n")
    + (diff.removed.length ? "\n" + diff.removed.filter(l => l.trim()).map(l => `<span class="rem">${E(l)}</span>`).join("") : "");
  $("#files").innerHTML = `<div class="tree">${files.map(f => `<button class="${f === MM.file ? "on" : ""}" data-f="${E(f)}">${E(f)}${day.diff[f] ? '<span class="ch">●</span>' : ""}</button>`).join("")}</div><pre>${body}</pre>`;
  $$("#files [data-f]").forEach(b => b.onclick = () => { MM.file = b.dataset.f; renderFiles(); });
}
function showResult(r) {
  MM.live = null; MM.res[r.design] = r; MM.day = r.days.length - 1;
  renderDesigns(); renderStrip(); renderProbes(r); renderFiles();
  if (!MM.sel) MM.sel = {kind: "probe", id: "p1"};
  renderSel();
  $("#weekstatus").innerHTML = `<span class="pill line">${r.model_calls} model calls · ${fmt(r.tokens_per_turn)} tokens per turn · ${usd(r.usd)} · ${secs(r.seconds)}</span>`;
}
async function runWeek() {
  if (MM.running) return;
  MM.running = true; busy($("#runweek"), true, "Running the week"); $("#compare").disabled = true;
  MM.live = {design: MM.design, knobs: {...MM.knobs}, turns: [], probes: [], nights: [], days: []};
  MM.sel = null; renderStrip(); $("#probes").innerHTML = `<div class="empty">The questions come after the week.</div>`; $("#probescore").innerHTML = "";
  $("#convo").innerHTML = `<div class="empty">Monday morning…</div>`;
  try {
    const j0 = await api("/api/memory/run", {design: MM.design, knobs: MM.knobs});
    const j = await poll(j0.id, evs => {
      for (const ev of evs) {
        if (ev.kind === "turn") { MM.live.turns.push(ev.rec); MM.sel = {kind: "session", id: ev.rec.session}; }
        if (ev.kind === "probe") { MM.live.probes.push(ev.rec); if (ev.rec.probe !== "p10") MM.sel = {kind: "probe", id: ev.rec.probe}; renderProbes(MM.live); }
        if (ev.kind === "night") MM.live.nights.push(ev.rec);
      }
      if (evs.length) { renderStrip(); renderSel(); $("#weekstatus").innerHTML = `<span class="pill accent"><span class="spin" style="width:10px;height:10px"></span>${MM.live.turns.length} of 13 turns · ${MM.live.probes.length} of 10 questions</span>`; }
    }, 700);
    showResult(j.result);
    ME.mem_rows = (await api("/api/me")).mem_rows; renderMemTable();
    toast(`${dmeta(MM.design).title}: ${j.result.score.right} of 10 right · ${usd(j.result.usd)}`);
  } catch (e) { toast(e.message); }
  finally { MM.running = false; busy($("#runweek"), false); $("#compare").disabled = false; }
}
async function compareAll() {
  if (MM.running) return;
  MM.running = true; busy($("#compare"), true, "Five weeks at once"); $("#runweek").disabled = true;
  const count = {};
  try {
    const j0 = await api("/api/memory/compare", {window: MM.knobs.window});
    await poll(j0.id, evs => {
      evs.forEach(ev => count[ev.design] = (count[ev.design] || 0) + (ev.kind === "night" ? 0 : 1));
      $("#weekstatus").innerHTML = CAT.designs.map(d => `<span class="pill ${count[d.id] >= 23 ? "good" : "line"}" style="margin-left:4px">${E(d.title)} ${count[d.id] || 0}/23</span>`).join("");
    }, 900);
    for (const d of CAT.designs) { try { MM.res[d.id] = await api(`/api/memory/result/${d.id}`); } catch (e) {} }
    ME.mem_rows = (await api("/api/me")).mem_rows; renderMemTable(); renderDesigns();
    if (MM.res[MM.design]) showResult(MM.res[MM.design]);
    toast("Five designs, the same week: compare them below.");
  } catch (e) { toast(e.message); }
  finally { MM.running = false; busy($("#compare"), false); $("#runweek").disabled = false; }
}
function renderMemTable() {
  const rows = (ME.mem_rows || []).slice().reverse();
  if (!rows.length) { $("#memtable").innerHTML = `<div class="empty">No runs yet.</div>`; return; }
  const maxTok = Math.max(...rows.map(r => r.tokens_per_turn || 0), 1);
  $("#memtable").innerHTML = `<table class="t"><thead><tr><th>Design</th><th>Right</th><th class="r">Stale</th><th class="r">Poisoned</th><th>Tokens per turn</th><th class="r">Cost</th><th class="r">Time</th></tr></thead><tbody>
    ${rows.map(r => `<tr data-d="${r.design}" style="cursor:pointer"><td><b style="font-weight:500">${E(r.title)}</b> <span class="muted small">${E(r.kicker)}</span>${r.changed && r.changed.length ? `<br><span class="small muted">${E(r.changed.join(", "))}</span>` : ""}</td>
      <td><div class="row"><div class="mbar" style="width:80px"><i style="width:${r.score.right * 10}%;background:${r.score.right >= 8 ? "var(--good)" : "var(--accent)"}"></i></div><span class="num">${r.score.right}/${r.score.of}</span></div></td>
      <td class="r">${r.score.stale || ""}</td><td class="r" style="color:var(--bad)">${r.score.poisoned || ""}</td>
      <td><div class="row"><div class="mbar" style="width:90px"><i style="width:${(r.tokens_per_turn / maxTok) * 100}%;background:var(--amber)"></i></div><span class="num">${fmt(r.tokens_per_turn)}</span></div></td>
      <td class="r">${usd(r.usd)}</td><td class="r">${secs(r.seconds)}</td></tr>`).join("")}</tbody></table>`;
  $$("#memtable tr[data-d]").forEach(tr => tr.onclick = async () => {
    MM.design = tr.dataset.d; renderDesigns();
    try { if (!MM.res[MM.design]) MM.res[MM.design] = await api(`/api/memory/result/${MM.design}`); MM.knobs = {...MM.res[MM.design].knobs}; renderKnobs(); showResult(MM.res[MM.design]); }
    catch (e) { toast("That run is no longer in memory on the server: run it again."); }
  });
}

/* ================================================================== 2 · WORKFLOWS */
const FL = {draft: null, wf: null, values: {}, run: null, runId: null, sel: null, side: "params", scale: 1, tx: 0, ty: 0, fresh: false};
function initFlows() {
  $("#starters").innerHTML = CAT.starters.map(s => `<button class="starter" data-s="${s.id}"><span class="ico">${I[ICON_OF[s.id]] ? I[ICON_OF[s.id]].replace("<svg", '<svg width="13" height="13"') : ""}</span>${E(s.title)}</button>`).join("");
  $$(".starter").forEach(b => b.onclick = () => { const s = CAT.starters.find(x => x.id === b.dataset.s); $("#ask").value = s.prompt; FL.starter = s.id; $("#ask").focus(); autoGrow($("#ask")); $("#build").animate([{transform: "scale(1)"}, {transform: "scale(1.06)"}, {transform: "scale(1)"}], {duration: 380}); });
  $("#ask").addEventListener("input", e => { autoGrow(e.target); FL.starter = null; });
  $("#ask").addEventListener("keydown", e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) build(); });
  $("#build").onclick = build;
  $$("#sidetabs button").forEach(b => b.onclick = () => { FL.side = b.dataset.s; renderSide(); });
  initPanZoom();
}
function autoGrow(t) { t.style.height = "auto"; t.style.height = Math.min(220, t.scrollHeight) + "px"; }
function buildingOverlay(step, extra) {
  const S = ["Reading your words", "Choosing tools from the toolbox", "Checking every step against tool.json", "Finding the parameters", "Laying out the canvas"];
  $("#hello").classList.remove("hide");
  $("#hello").innerHTML = `<div class="building">${S.map((s, i) => `<div class="s ${i < step ? "ok" : i === step ? "on" : ""}"><i></i>${s}</div>`).join("")}${extra ? `<div class="small" style="color:var(--warn);margin-top:4px">${extra}</div>` : ""}</div>`;
}
async function build() {
  const ask = $("#ask").value.trim();
  if (ask.length < 12) { toast("Describe the task in a sentence or two."); return; }
  busy($("#build"), true, "Building"); FL.run = null; FL.runId = null; $("#runresult").innerHTML = ""; clearCanvas();
  let step = 0, extra = "";
  buildingOverlay(0);
  const tick = setInterval(() => { if (step < 2) { step++; buildingOverlay(step, extra); } }, 2600);
  try {
    const j0 = await api("/api/flow/draft", {prompt: ask});
    const j = await poll(j0.id, evs => evs.forEach(r => {
      if (!r.ok) { extra = `Round ${r.round}: ${r.problems.length} problem(s) found by the checks. Sent back to the model to fix…`; step = 2; }
      else step = 3;
      buildingOverlay(step, extra);
    }), 600);
    clearInterval(tick);
    const d = j.result; FL.draft = d;
    buildingOverlay(4, extra); await sleep(350);
    if (!d.ok) {
      $("#hello").innerHTML = `<div class="building" style="max-width:520px"><b>The draft did not pass the checks</b>${(d.problems || []).slice(0, 6).map(p => `<div class="check">${I.cross}${E(p)}</div>`).join("")}
        <div class="row" style="margin-top:8px"><button class="btn sm" id="retry">Try again</button>${FL.starter ? `<button class="btn sm" id="canned">Load the hand-built one</button>` : ""}</div></div>`;
      $("#retry").onclick = build; if ($("#canned")) $("#canned").onclick = () => loadCanned(FL.starter);
      FL.wf = d.workflow; FL.side = "checks"; renderSide(); return;
    }
    loadWorkflow(d.workflow, true);
    FL.side = "params"; renderSide();
    toast(`Drafted in ${secs(d.seconds)} · ${d.rounds.length} model call${d.rounds.length > 1 ? "s" : ""} · ${d.params.length} parameters · ${usd(d.usd)}`);
  } catch (e) { clearInterval(tick); toast(e.message); $("#hello").innerHTML = `<div><h3>Could not build it</h3><p>${E(e.message)}</p></div>`; }
  finally { busy($("#build"), false); }
}
async function loadCanned(id) {
  const r = await api(`/api/flow/canned/${id}`);
  FL.draft = {ok: true, workflow: r.workflow, problems: r.problems, checks: r.checks, rounds: [], params: r.workflow.params, canned: true};
  loadWorkflow(r.workflow, true); FL.side = "params"; renderSide();
}
function relayout(wf) {
  /* columns by depth (longest path from the trigger), each as wide as its widest node; rows keep the server's lanes */
  const by = Object.fromEntries(wf.nodes.map(n => [n.id, n])), depth = {};
  const trig = wf.nodes.find(n => n.type === "trigger"); if (!trig) return wf;
  depth[trig.id] = 0;
  for (let k = 0; k < wf.nodes.length; k++) wf.edges.forEach(e => { if (depth[e.from] != null && by[e.to] && (depth[e.to] == null || depth[e.to] < depth[e.from] + 1)) depth[e.to] = depth[e.from] + 1; });
  const w = {}; wf.nodes.forEach(n => { const c = depth[n.id] ?? 0; w[c] = Math.max(w[c] || 0, nodeSize(n)[0]); });
  const xs = {}; let x = 60; Object.keys(w).map(Number).sort((a, b) => a - b).forEach(c => { xs[c] = x; x += w[c] + 56; });
  const ys = [...new Set(wf.nodes.map(n => Math.round(n.y)))].sort((a, b) => a - b);
  wf.nodes.forEach(n => { n.x = xs[depth[n.id] ?? 0]; n.y = 120 + ys.indexOf(Math.round(n.y)) * 176; });
  return wf;
}
function loadWorkflow(wf, fresh) {
  relayout(wf);
  FL.wf = wf; FL.values = {}; (wf.params || []).forEach(p => FL.values[p.name] = p.default);
  FL.run = null; FL.runId = null; FL.sel = null; FL.fresh = !!fresh; $("#runresult").innerHTML = "";
  renderCanvas(); fitCanvas();
}
function clearCanvas() { $$("#world .node").forEach(n => n.remove()); $("#edges").innerHTML = ""; $("#cstrip").innerHTML = ""; }
function nodeSub(n) {
  const c = n.config || {};
  if (n.type === "trigger") return c.kind === "schedule" ? scheduleText(c) : c.kind === "event" ? "when: " + (c.event || "event") : c.kind === "form" ? `a form · ${(c.fields || []).length} fields` : "by hand";
  if (n.type === "tool") return `${c.tool} · ${PEOPLE_SHORT[c.as || "ECLARKE"] || c.as}${c.confirm ? " · saves" : ""}`;
  if (n.type === "condition") return String(c.if || "").replace(/\{\{|\}\}/g, "").trim();
  if (n.type === "approval") return `waits for ${PEOPLE_SHORT[c.approver] || "Daniel"}`;
  if (n.type === "llm") return `model · ${c.output || "text"}`;
  if (n.type === "message") return `to ${String(c.to || "").replace(/\{\{|\}\}/g, "")}`;
  if (n.type === "set") return Object.keys(c.values || {}).join(", ");
  if (n.type === "foreach") return `for each of ${String(c.items || "").replace(/\{\{|\}\}|nodes\./g, "").trim()}`;
  return "";
}
function scheduleText(c) { const at = c.at || "09:00"; return c.every === "week" ? `every ${c.day || "Mon"} ${at}` : c.every === "weekday" ? `weekdays ${at}` : c.every === "month" ? `day ${c.day_of_month || 1} of each month ${at}` : `every day ${at}`; }
const NW = 236, NH = 76;
function nodeSize(n) { return n.type === "foreach" ? [320, 132] : [NW, NH]; }
function renderCanvas() {
  const wf = FL.wf; if (!wf) return;
  $("#hello").classList.add("hide");
  clearCanvas();
  const world = $("#world");
  const order = wf.nodes.slice().sort((a, b) => (a.x - b.x) || (a.y - b.y));
  const rank = Object.fromEntries(order.map((n, i) => [n.id, i]));
  for (const n of wf.nodes) {
    const [w] = nodeSize(n);
    const el = document.createElement("div");
    el.className = "node" + (n.type === "foreach" ? " batch" : "");
    el.id = "n-" + n.id; el.style.left = n.x + "px"; el.style.top = n.y + "px"; el.style.width = w + "px";
    const inner = n.type === "foreach" ? `<div class="inner">${((n.config || {}).steps || []).map(s => `<span title="${E(s.type)}">${E(s.title || s.id)}</span>`).join("")}</div><div class="cells" id="cells-${n.id}"></div>` : "";
    el.innerHTML = `<div class="ic ${n.type}">${nodeIcon(n)}</div><div class="tx"><div class="ti">${E(n.title || n.id)}</div><div class="su">${E(nodeSub(n))}</div><div class="out" id="out-${n.id}"></div>${inner}<span class="meta" id="meta-${n.id}"></span></div>
      <span class="st" id="st-${n.id}"></span>`;
    el.onclick = e => { e.stopPropagation(); FL.sel = n.id; $$(".node").forEach(x => x.classList.toggle("sel", x === el)); FL.side = "node"; renderSide(); };
    world.appendChild(el);
    if (FL.fresh) setTimeout(() => el.classList.add("in"), 120 + rank[n.id] * 150); else el.classList.add("in");
  }
  drawEdges(FL.fresh ? rank : null);
  FL.fresh = false;
  const ps = (wf.params || []).map(p => `<span class="pill line" style="height:26px"><span class="muted">${E(p.label || p.name)}</span> <b style="font-weight:500">${E(fmtParam(FL.values[p.name]))}</b></span>`).join("");
  const d = FL.draft;
  $("#cstrip").innerHTML = `<span class="pill" style="height:26px;background:#fff;border:1px solid var(--line)"><b style="font-weight:500">${E(wf.name)}</b></span>
    ${d && !d.canned && d.rounds ? `<span class="pill good" style="height:26px">${I.check} ${wf.nodes.length} steps checked${d.rounds.length > 1 ? ` · ${d.rounds.length - 1} repair round` : ""}</span>` : d && d.canned ? `<span class="pill slate" style="height:26px">hand-built</span>` : ""}
    <span class="sp"></span>${ps}`;
}
function fmtParam(v) { return v === true ? "yes" : v === false ? "no" : v == null ? "–" : String(v); }
function edgePath(a, b) {
  const [aw, ah] = nodeSize(a), [, bh] = nodeSize(b);
  const x1 = a.x + aw, y1 = a.y + ah / 2, x2 = b.x, y2 = b.y + bh / 2;
  const dx = Math.max(40, (x2 - x1) / 2);
  return {d: `M${x1},${y1} C${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`, mx: (x1 + x2) / 2, my: (y1 + y2) / 2};
}
function drawEdges(rank) {
  const wf = FL.wf, by = Object.fromEntries(wf.nodes.map(n => [n.id, n]));
  let html = "";
  wf.edges.forEach((e, i) => {
    const a = by[e.from], b = by[e.to]; if (!a || !b) return;
    const p = edgePath(a, b);
    const delay = rank ? (180 + rank[e.to] * 150) : 0;
    html += `<path class="edge ${rank ? "draw" : ""}" id="e-${i}" d="${p.d}" style="${rank ? `animation-delay:${delay}ms;` : ""}"/>`;
    if (e.port && e.port !== "out") html += `<g style="opacity:${rank ? 0 : 1};transition:opacity .3s ${delay + 300}ms" class="lbl"><rect class="eportbg" x="${p.mx - 20}" y="${p.my - 10}" width="40" height="20" rx="10"/><text class="eport" x="${p.mx}" y="${p.my + 4}" text-anchor="middle">${e.port === "true" ? "yes" : e.port === "false" ? "no" : e.port}</text></g>`;
  });
  $("#edges").innerHTML = html;
  $$("#edges path").forEach(p => { const L = p.getTotalLength ? p.getTotalLength() : 400; p.style.setProperty("--len", L); });
  if (rank) setTimeout(() => $$("#edges g.lbl").forEach(g => g.style.opacity = 1), 50);
}
function initPanZoom() {
  const c = $("#canvas"); let drag = null;
  c.addEventListener("mousedown", e => { if (e.target.closest(".node,.zoom,.cstrip,.building")) return; drag = {x: e.clientX, y: e.clientY, tx: FL.tx, ty: FL.ty}; c.classList.add("drag"); });
  window.addEventListener("mousemove", e => { if (!drag) return; FL.tx = drag.tx + e.clientX - drag.x; FL.ty = drag.ty + e.clientY - drag.y; applyT(); });
  window.addEventListener("mouseup", () => { drag = null; c.classList.remove("drag"); });
  c.addEventListener("wheel", e => { if (!FL.wf) return; e.preventDefault(); c.classList.add("nozoomanim"); const r = c.getBoundingClientRect(); zoomAt(e.deltaY < 0 ? 1.08 : 1 / 1.08, e.clientX - r.left, e.clientY - r.top); clearTimeout(c._z); c._z = setTimeout(() => c.classList.remove("nozoomanim"), 120); }, {passive: false});
  $("#zin").onclick = () => zoomAt(1.2); $("#zout").onclick = () => zoomAt(1 / 1.2); $("#zfit").onclick = fitCanvas;
  c.addEventListener("click", e => { if (!e.target.closest(".node")) { FL.sel = null; $$(".node").forEach(x => x.classList.remove("sel")); } });
}
function zoomAt(f, cx, cy) {
  const c = $("#canvas"); cx = cx ?? c.clientWidth / 2; cy = cy ?? c.clientHeight / 2;
  const s = Math.max(.35, Math.min(1.6, FL.scale * f)); const k = s / FL.scale;
  FL.tx = cx - (cx - FL.tx) * k; FL.ty = cy - (cy - FL.ty) * k; FL.scale = s; applyT();
}
function applyT() { $("#world").style.transform = `translate(${FL.tx}px,${FL.ty}px) scale(${FL.scale})`; }
function fitCanvas() {
  if (!FL.wf) return;
  const c = $("#canvas"), ns = FL.wf.nodes;
  const minx = Math.min(...ns.map(n => n.x)), miny = Math.min(...ns.map(n => n.y));
  const maxx = Math.max(...ns.map(n => n.x + nodeSize(n)[0])), maxy = Math.max(...ns.map(n => n.y + nodeSize(n)[1]));
  const W = c.clientWidth - 60, H = c.clientHeight - 90;
  FL.scale = Math.min(1.35, W / (maxx - minx), H / (maxy - miny));
  FL.tx = 30 + (W - (maxx - minx) * FL.scale) / 2 - minx * FL.scale;
  FL.ty = 62 + (H - (maxy - miny) * FL.scale) / 2 - miny * FL.scale;
  applyT();
}
function paramInput(p) {
  const v = FL.values[p.name], id = "p-" + p.name;
  let inp;
  if (p.type === "choice") inp = `<select class="input" id="${id}">${(p.options || []).map(o => `<option ${o == v ? "selected" : ""}>${E(o)}</option>`).join("")}</select>`;
  else if (p.type === "boolean") inp = `<div><button class="switch ${v ? "on" : ""}" id="${id}" type="button"></button></div>`;
  else if (p.type === "person") inp = `<select class="input" id="${id}">${Object.entries(CAT.people).map(([k, x]) => `<option value="${k}" ${k === v ? "selected" : ""}>${E(x.name)} (${k})</option>`).join("")}</select>`;
  else inp = `<input class="input" id="${id}" type="${p.type === "number" ? "number" : p.type === "date" ? "date" : "text"}" value="${E(v ?? "")}" step="any">`;
  return `<div class="field"><label for="${id}">${E(p.label || p.name)} <span class="pname">${E(p.name)}</span></label>${inp}${p.help ? `<small>${E(p.help)}</small>` : ""}</div>`;
}
function readParams() {
  (FL.wf.params || []).forEach(p => {
    const el = $("#p-" + p.name); if (!el) return;
    FL.values[p.name] = p.type === "boolean" ? el.classList.contains("on") : p.type === "number" ? (el.value === "" ? null : Number(el.value)) : el.value;
  });
}
function renderSide() {
  $$("#sidetabs button").forEach(b => b.classList.toggle("on", b.dataset.s === FL.side));
  const sb = $("#sidebody"), wf = FL.wf;
  if (!wf) { sb.innerHTML = `<div class="empty">Build a workflow first.</div>`; return; }
  if (FL.side === "params") {
    const trig = wf.nodes.find(n => n.type === "trigger"), form = trig && trig.config.kind === "form" ? trig.config.fields || [] : [];
    sb.innerHTML = `<p class="small muted" style="margin-bottom:14px">${E(wf.description || "")}</p>
      ${(wf.params || []).length ? `<div class="label">Parameters (what may change per run)</div>${wf.params.map(paramInput).join("")}` : `<div class="empty">This workflow has no parameters.</div>`}
      ${form.length ? `<div class="label" style="margin-top:6px">The form (what the trigger asks for)</div>${form.map(f => `<div class="field"><label>${E(f.label || f.name)}</label><input class="input" id="f-${f.name}" value="${E(f.default ?? "")}" type="${f.type === "date" ? "date" : f.type === "number" ? "number" : "text"}"></div>`).join("")}` : ""}
      <div class="row" style="margin-top:6px"><button class="btn primary" id="runwf" style="flex:1">${FL.run ? "Run again with these values" : "Run with these values"}</button></div>
      <div style="border-top:1px solid var(--line);margin:16px -18px 0;padding:14px 18px 0">
        <div class="label">Save as my routine</div><div class="row"><input class="input" id="rname" value="${E(wf.name)}"><button class="btn" id="savewf">Save</button></div>
        <label class="row small muted" style="margin-top:8px;cursor:pointer"><button class="switch on" id="rsched" type="button"></button>run it on its schedule (the clock)</label></div>`;
    $$("#sidebody .switch").forEach(b => b.onclick = () => b.classList.toggle("on"));
    $("#runwf").onclick = runFlow; $("#savewf").onclick = saveFlow;
  } else if (FL.side === "checks") {
    const d = FL.draft || {};
    sb.innerHTML = `${(d.rounds || []).length ? `<div class="label">Model calls</div>${d.rounds.map(r => `<div class="check">${r.ok ? I.check : I.cross}<div>Round ${r.round}: ${r.ok ? "passed every check" : `${r.problems.length} problem(s): ${E(r.problems.slice(0, 3).join(" · "))}`}<br><span class="tiny muted">${fmt(r.tokens_in)} in · ${fmt(r.tokens_out)} out · ${secs(r.seconds)} · ${usd(r.usd)}</span></div></div>`).join("")}` : d.canned ? `<p class="small muted">The hand-built version of this starter (no model call).</p>` : ""}
      ${(d.problems || []).length ? `<div class="label" style="margin-top:12px">Still wrong</div>${d.problems.map(p => `<div class="check">${I.cross}${E(p)}</div>`).join("")}` : ""}
      <div class="label" style="margin-top:12px">Checked against the toolbox</div>${(d.checks || []).map(c => `<div class="check">${I.check}<div><b class="mono" style="font-weight:500">${E(c.node)}</b> ${E(c.text)}</div></div>`).join("") || `<div class="small muted">No tool steps.</div>`}
      <div class="check">${I.check}<div>every {{ }} reference names a node, a step or a parameter that exists</div></div>
      <div class="check">${I.check}<div>one trigger; the graph flows one way; every node can be reached</div></div>
      ${FL.starter ? `<button class="btn sm" id="canned2" style="margin-top:10px">Compare with the hand-built one</button>` : ""}`;
    if ($("#canned2")) $("#canned2").onclick = () => loadCanned(FL.starter);
  } else if (FL.side === "node") {
    const n = wf.nodes.find(x => x.id === FL.sel);
    if (!n) { sb.innerHTML = `<div class="empty">Click a step on the canvas.</div>`; return; }
    const r = FL.run && FL.run.nodes[n.id];
    let items = "";
    if (r && r.progress) {
      items = `<div class="label" style="margin-top:12px">Items (${r.progress.done} of ${r.progress.of})</div>` + r.progress.items.filter(Boolean).map(x => `<div class="evrow" data-item="${x.i}" style="grid-template-columns:28px 1fr auto"><span class="muted mono">${x.i + 1}</span><span>${E(x.label)}${x.error ? `<br><span class="tiny" style="color:var(--bad)">${E(x.error)}</span>` : ""}</span><span class="pill ${outcomeCls(x.outcome)}">${E(x.outcome || x.status)}</span></div>`).join("");
    }
    sb.innerHTML = `<div class="row" style="margin-bottom:10px"><div class="ic ${n.type}" style="width:30px;height:30px;border-radius:9px;display:grid;place-items:center">${nodeIcon(n)}</div><b style="font-weight:500">${E(n.title)}</b><span class="sp"></span>${r ? `<span class="pill ${statusCls(r.status)}">${r.status}</span>` : ""}</div>
      ${r ? `<div class="kv" style="margin-bottom:12px"><span>Time</span><span>${secs(r.seconds)}</span>${r.meta && r.meta.tokens_in ? `<span>Tokens</span><span>${fmt(r.meta.tokens_in)} in · ${fmt(r.meta.tokens_out)} out</span><span>Cost</span><span>${usd(r.meta.usd)}</span>` : ""}<span>Result</span><span>${E(r.summary || "")}</span></div>` : ""}
      <div class="label">Configuration</div><div class="json">${E(JSON.stringify(n.config, null, 2))}</div>
      ${r && r.inputs ? `<div class="label" style="margin-top:12px">Inputs, filled</div><div class="json">${E(JSON.stringify(r.inputs, null, 2))}</div>` : ""}
      ${r && r.output && !r.progress ? `<div class="label" style="margin-top:12px">Output</div><div class="json">${E(JSON.stringify(r.output, null, 2))}</div>` : ""}${items}`;
    $$("#sidebody [data-item]").forEach(row => row.onclick = async () => {
      try { const it = await api(`/api/flow/runs/${FL.runId}/item?node=${n.id}&i=${row.dataset.item}`); drawer(`Item ${+row.dataset.item + 1}: ${it.row.label}`, `<div class="json" style="max-height:none">${E(JSON.stringify(it.item, null, 2))}</div>`); }
      catch (e) { toast(e.message); }
    });
  } else {
    const log = (FL.run && FL.run.log) || [];
    sb.innerHTML = log.length ? `<div class="timeline">${log.map(l => `<div class="ev ${l.event === "done" ? "good" : l.event === "error" || l.event === "failed" ? "bad" : l.event === "waiting" || l.event === "warning" ? "warn" : ""}"><div class="small"><span class="mono muted">${E(l.t)} · +${secs(l.wall)}</span> ${l.node ? `<b class="mono" style="font-weight:500">${E(l.node)}</b>` : ""}</div><div class="small ink2">${E(l.text)}</div></div>`).join("")}</div>` : `<div class="empty">Run it to see the log.</div>`;
  }
}
const statusCls = s => ({done: "good", running: "accent", waiting: "warn", warning: "warn", error: "bad", failed: "bad", skipped: "slate"})[s] || "";
const outcomeCls = o => !o ? "" : /posted|e-mailed|drafted|requested|checked|done|short/.test(o) ? "good" : /held|still/.test(o) ? "warn" : /duplicate/.test(o) ? "violet" : "bad";
const cellCls = o => !o ? "" : /posted|e-mailed|drafted|requested|checked|done|short/.test(o) ? "posted" : /held|still/.test(o) ? "held" : /duplicate/.test(o) ? "dup" : "err";
async function runFlow() {
  readParams();
  const form = {};
  const trig = FL.wf.nodes.find(n => n.type === "trigger");
  if (trig && trig.config.kind === "form") (trig.config.fields || []).forEach(f => { const el = $("#f-" + f.name); if (el) form[f.name] = el.value; });
  busy($("#runwf"), true, "Running");
  try {
    const r = await api("/api/flow/run", {workflow: FL.wf, params: FL.values, trigger: form});
    FL.runId = r.run_id; FL.run = null; $("#runresult").innerHTML = "";
    $$(".node").forEach(n => n.classList.remove("done", "error", "warning", "waiting", "skipped", "running"));
    $$(".cells").forEach(c => c.innerHTML = "");
    renderCanvas();
    await followRun(r.job);
  } catch (e) { toast(e.message); }
  finally { busy($("#runwf"), false); renderSide(); }
}
async function followRun(job) {
  let done = false;
  const jp = poll(job, null, 800).then(() => { done = true; }).catch(e => { done = true; toast(e.message); });
  while (!done) {
    try { FL.run = await api(`/api/flow/runs/${FL.runId}`); paintRun(); } catch (e) {}
    await sleep(450);
  }
  await jp;
  FL.run = await api(`/api/flow/runs/${FL.runId}`); paintRun(); FL.showResult();
}
function paintRun() {
  const run = FL.run; if (!run) return;
  const taken = new Set(run.edges_taken.map(([a, b, p]) => `${a}>${b}>${p}`));
  for (const [nid, r] of Object.entries(run.nodes)) {
    const el = $("#n-" + nid); if (!el) continue;
    el.classList.remove("done", "error", "warning", "waiting", "skipped", "running"); if (r.status !== "pending") el.classList.add(r.status);
    $("#st-" + nid).innerHTML = r.status === "pending" ? "" : `<span class="pill ${statusCls(r.status)}" style="height:20px;font-size:11px">${r.status === "running" ? '<span class="spin" style="width:9px;height:9px"></span>' : ""}${r.status}</span>`;
    $("#out-" + nid).textContent = r.summary || "";
    $("#meta-" + nid).textContent = r.seconds != null ? secs(r.seconds) + (r.meta && r.meta.usd ? " · " + usd(r.meta.usd) : "") : "";
    if (r.progress) {
      const cells = $("#cells-" + nid);
      if (cells && cells.children.length !== r.progress.of) cells.innerHTML = Array.from({length: r.progress.of}, () => "<i></i>").join("");
      if (cells) r.progress.items.forEach((x, i) => { const c = cells.children[i]; if (!c) return; const cls = x ? (x.status === "running" ? "run" : cellCls(x.outcome)) : ""; if (c.dataset.c !== cls) { c.className = cls + (cls && cls !== "run" ? " pop" : ""); c.dataset.c = cls; c.title = x ? `${x.label}: ${x.outcome || x.status}` : ""; setTimeout(() => c.classList.remove("pop"), 300); } });
      $("#out-" + nid).textContent = `${r.progress.done} of ${r.progress.of} · ` + Object.entries(r.progress.tally).map(([k, v]) => `${v} ${k}`).join(" · ");
    }
  }
  FL.wf.edges.forEach((e, i) => {
    const p = $("#e-" + i); if (!p) return;
    const k = `${e.from}>${e.to}>${e.port || "out"}`, src = run.nodes[e.from], dst = run.nodes[e.to];
    p.classList.remove("draw"); p.style.strokeDashoffset = "";
    p.classList.toggle("taken", taken.has(k) && dst && dst.status !== "running");
    p.classList.toggle("flow", taken.has(k) && dst && dst.status === "running");
    p.classList.toggle("skip", !!(dst && dst.status === "skipped"));
  });
  if (FL.side === "log" || (FL.side === "node" && FL.sel)) renderSide();
}
FL.showResult = function () {
  const run = FL.run; if (!run) return;
  const each = Object.values(run.nodes).find(r => r.progress);
  const tally = each ? each.progress.tally : null;
  const waiting = run.status === "waiting";
  const keys = tally ? Object.keys(tally) : [];
  $("#runresult").innerHTML = `<div class="result"><div class="col" style="gap:2px"><span class="small muted">${E(run.workflow_name)} · ${Object.entries(run.params || {}).map(([k, v]) => `${k}=${fmtParam(v)}`).join(", ")}</span>
    <span class="big">${waiting ? "Waiting for " + E(run.waiting_for.approver_name) : run.status === "done" ? "Done" : "Stopped"}${run.wall_seconds ? ` in ${secs(run.wall_seconds)}` : ""}</span>${run.error ? `<span class="small" style="color:var(--bad)">${E(run.error)}</span>` : ""}</div>
    ${tally ? `<div class="tally">${keys.map(k => `<div><b>${tally[k]}</b><span><i class="dot" style="background:${{posted: "#3aa57c", held: "#e3a43a", dup: "#a98be8", err: "#df6a5c"}[cellCls(k)] || "#999"}"></i>${E(k)}</span></div>`).join("")}</div>` : ""}
    <span class="sp"></span><div class="col" style="gap:2px;text-align:right"><span class="small muted">model</span><b style="font-weight:500">${fmt(run.cost.tokens_in)} tokens · ${usd(run.cost.usd)}</b></div>
    ${waiting ? `<button class="btn" id="openappr">Open approvals</button><button class="btn primary" id="resume">Resume</button>` : ""}</div>`;
  if (waiting) { $("#openappr").onclick = () => $("#inboxbtn").click(); $("#resume").onclick = async () => { busy($("#resume"), true, "Resuming"); try { const r = await api("/api/flow/resume", {run_id: FL.runId}); await followRun(r.job); } catch (e) { toast(e.message); busy($("#resume"), false); } }; }
  refreshInbox();
};
async function saveFlow() {
  readParams();
  try {
    const r = await api("/api/flow/save", {workflow: FL.wf, name: $("#rname").value, params: FL.values, scheduled: $("#rsched").classList.contains("on"), source: FL.draft && FL.draft.canned ? "hand-built" : "drafted"});
    ME.routines = r.routines; renderShelf(); toast("Saved. It is a tool in Ask Northbridge now" + ($("#rsched").classList.contains("on") ? ", and it runs on its schedule." : "."));
  } catch (e) { toast(e.message); }
}
async function renderShelf() {
  try { const r = await api("/api/flow/routines"); ME.routines = r.routines; FL.full = r.full; } catch (e) { return; }
  const rs = ME.routines || [];
  $("#shelf").innerHTML = rs.length ? rs.map((r, i) => `<div class="routine"><div class="row"><h4>${E(r.name)}</h4><span class="sp"></span>${r.schedule ? `<span class="pill ${r.scheduled ? "accent" : "line"}">${E(r.schedule)}</span>` : `<span class="pill line">${E(r.trigger)}</span>`}</div>
    <p class="small muted">${E(r.description || "")}</p><div class="ps">${(r.params || []).map(p => `<span class="pill line">${E(p.name)} = ${E(fmtParam(p.default))}</span>`).join("")}</div>
    <div class="row"><button class="btn sm" data-open="${i}">Open</button><label class="row small muted" style="gap:6px"><button class="switch ${r.scheduled ? "on" : ""}" data-sched="${E(r.id)}"></button>on the clock</label><span class="sp"></span><button class="btn xs ghost" data-del="${E(r.id)}">Delete</button></div>
    ${r.last ? `<span class="tiny muted">Last run: ${E(r.last.status)} · ${usd(r.last.usd)}</span>` : ""}</div>`).join("") : `<div class="empty">Nothing saved yet. Build one above and press Save.</div>`;
  $$("[data-open]").forEach(b => b.onclick = () => { FL.draft = {ok: true, workflow: FL.full[+b.dataset.open], rounds: [], checks: [], problems: [], canned: false}; loadWorkflow(JSON.parse(JSON.stringify(FL.full[+b.dataset.open])), true); FL.side = "params"; renderSide(); window.scrollTo({top: 200, behavior: "smooth"}); });
  $$("[data-sched]").forEach(b => b.onclick = async () => { try { await api("/api/flow/routine", {id: b.dataset.sched, scheduled: !b.classList.contains("on")}); renderShelf(); } catch (e) { toast(e.message); } });
  $$("[data-del]").forEach(b => b.onclick = async () => { try { await api("/api/flow/routine", {id: b.dataset.del, delete: true}); renderShelf(); } catch (e) { toast(e.message); } });
}

/* ================================================================== 3 · BACKGROUND AGENTS */
const AG = {data: null, open: {}, week0: null, live: []};
function initAgents() {
  $("#btomorrow").onclick = () => playClock("tomorrow", [$("#ctomorrow"), $("#btomorrow")]);
  $("#bweek").onclick = () => { AG.week0 = ME.clock.iso; AG.live = []; playClock("week", [$("#cweek"), $("#bweek")]); };
  $("#stopall").onclick = async () => { const on = !$("#stopall").classList.contains("on"); await api("/api/agents/config", {stop_all: on}); loadAgents(); toast(on ? "Stop all: no background agent runs." : "Agents may run again."); };
  AG.onRun = r => { AG.live.push(r); if (TAB === "agents") { renderGrid(); renderLog(); } };
}
async function loadAgents() {
  try { AG.data = await api("/api/agents"); } catch (e) { return; }
  setClock(AG.data.clock);
  $("#stopall").classList.toggle("on", AG.data.stop_all);
  renderAgentCards(); renderGrid(); renderLog(); renderLeft();
}
function renderAgentCards() {
  const d = AG.data;
  $("#agentlist").innerHTML = CAT.agents.map(a => {
    const c = d.config[a.id] || {}; const on = c.on;
    const sched = c.schedule || a.schedule;
    const params = Object.entries(c.params || {}).map(([k, v]) => `<div class="row"><span style="width:120px" class="muted">${E(k.replace(/_/g, " "))}</span><input class="input" data-p="${k}" value="${E(v)}"></div>`).join("");
    return `<div class="agent ${on ? "on" : ""} ${AG.open[a.id] ? "open" : ""}" data-a="${a.id}"><div class="h"><div class="ic">${I[a.icon] ? I[a.icon].replace("<svg", '<svg width="16" height="16"') : ""}</div>
      <div style="flex:1"><h4>${E(a.title)}</h4><div class="tiny muted">as ${E(a.as_name)} · ${E(scheduleText(sched))}</div></div><button class="switch ${on ? "on" : ""}" data-on></button></div>
      <p>${E(a.what)}</p><div class="row"><button class="btn xs" data-cfg>${AG.open[a.id] ? "Hide settings" : "Settings"}</button><button class="btn xs" data-now>Run now</button><span class="sp"></span><span class="tiny muted">${a.tools.length} tools</span></div>
      <div class="cfg"><div class="row"><span style="width:120px" class="muted">runs</span><select class="input" data-every>${["day", "weekday", "week"].map(x => `<option ${sched.every === x ? "selected" : ""}>${x}</option>`).join("")}</select>
        <select class="input" data-day ${sched.every !== "week" ? "disabled" : ""}>${["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map(x => `<option ${sched.day === x ? "selected" : ""}>${x}</option>`).join("")}</select><input class="input" data-at value="${E(sched.at)}" style="width:80px"></div>
        ${params}<div class="row"><span style="width:120px" class="muted">max steps</span><input class="input" data-l="max_steps" value="${c.limits.max_steps}"></div>
        <div class="row"><span style="width:120px" class="muted">token budget</span><input class="input" data-l="max_tokens" value="${c.limits.max_tokens}"></div>
        <div class="row"><span style="width:120px" class="muted">may commit</span><button class="switch ${c.limits.may_commit ? "on" : ""}" data-commit></button><span class="tiny muted">${a.id === "reorder" ? "off: requests stay previews" : "off: every write is a preview"}</span></div>
        <div class="row"><span class="tiny muted" style="flex:1">tools: ${E(a.tools.join(", "))}</span><button class="btn xs primary" data-save>Save</button></div></div></div>`;
  }).join("");
  $$(".agent").forEach(card => {
    const id = card.dataset.a;
    $("[data-on]", card).onclick = async () => { await api("/api/agents/config", {id, on: !$("[data-on]", card).classList.contains("on")}); loadAgents(); };
    $("[data-cfg]", card).onclick = () => { AG.open[id] = !AG.open[id]; renderAgentCards(); };
    $("[data-commit]", card).onclick = e => e.target.classList.toggle("on");
    $("[data-every]", card).onchange = e => { $("[data-day]", card).disabled = e.target.value !== "week"; };
    $("[data-save]", card).onclick = async () => {
      const params = {}; $$("[data-p]", card).forEach(i => params[i.dataset.p] = i.value);
      await api("/api/agents/config", {id, schedule: {every: $("[data-every]", card).value, day: $("[data-day]", card).value, at: $("[data-at]", card).value}, params,
        limits: {max_steps: $("[data-l=max_steps]", card).value, max_tokens: $("[data-l=max_tokens]", card).value, may_commit: $("[data-commit]", card).classList.contains("on")}});
      toast("Saved."); loadAgents();
    };
    $("[data-now]", card).onclick = async e => {
      const b = e.target; busy(b, true);
      try { const j0 = await api("/api/agents/run_now", {id}); const j = await poll(j0.id, null, 700); toast(`${j.result.title}: ${j.result.status} · ${usd(j.result.usd)}`); loadAgents(); showRun(j.result); }
      catch (err) { toast(err.message); } finally { busy(b, false); }
    };
  });
}
function weekDays() {
  /* 8 days: the week being played (from AG.week0), or the 7 days up to the clock if runs happened, else from the clock */
  const clock = new Date(((AG.data && AG.data.clock.iso) || CAT.start).slice(0, 10) + "T00:00:00Z");
  let start = AG.week0 ? new Date(AG.week0.slice(0, 10) + "T00:00:00Z") : clock;
  if (!AG.week0 && AG.data && AG.data.log.length) start = new Date(clock.getTime() - 7 * 864e5);
  return Array.from({length: 8}, (_, i) => new Date(start.getTime() + i * 864e5));
}
function renderGrid() {
  if (!AG.data) return;
  const days = weekDays(), d0 = days[0].toISOString().slice(0, 10), d6 = days[days.length - 1].toISOString().slice(0, 10);
  const log = AG.data.log.concat(AG.live.filter(r => !AG.data.log.some(x => x.key === r.key)));
  const rows = CAT.agents.map(a => ({id: a.id, title: a.title, icon: a.icon})).concat((ME.routines || []).filter(r => r.scheduled && r.schedule).map(r => ({id: r.id, title: r.name, icon: "receipt", routine: true})));
  const today = (AG.data.clock.iso || "").slice(0, 10);
  let html = `<div class="weekgrid" style="--days:${days.length}"><div class="hd">Agent</div>${days.map(d => { const k = d.toISOString().slice(0, 10); return `<div class="hd ${k === today ? "today" : ""}">${d.toLocaleDateString("en-GB", {weekday: "short", day: "numeric", month: "short", timeZone: "UTC"})}</div>`; }).join("")}`;
  for (const r of rows) {
    html += `<div class="an">${E(r.title)}</div>`;
    for (const d of days) {
      const k = d.toISOString().slice(0, 10);
      const done = log.filter(x => x.agent === r.id && (x.scheduled || "").slice(0, 10) === k);
      const plan = (AG.data.next || []).filter(x => x.id === r.id && x.at.slice(0, 10) === k && !done.some(y => y.scheduled === x.at));
      html += `<div class="cell">${done.map(x => `<span class="rdot ${x.status}" data-key="${E(x.key)}" title="${E(x.summary || "")}">${(x.ran_at || x.scheduled || "").slice(11, 16)}${x.status === "retried" ? " ↻" : x.status === "failed" ? " ✕" : ""}</span>`).join("")}${plan.map(x => `<span class="rdot plan">${x.at.slice(11, 16)}</span>`).join("")}</div>`;
    }
  }
  $("#weekgrid").innerHTML = html + "</div>";
  $$("#weekgrid [data-key]").forEach(s => s.onclick = () => { const r = log.find(x => x.key === s.dataset.key); if (r) showRun(r); });
  const n = log.filter(x => (x.scheduled || "").slice(0, 10) >= d0 && (x.scheduled || "").slice(0, 10) <= d6).length;
  $("#bgmeta").textContent = `${days[0].toLocaleDateString("en-GB", {day: "numeric", month: "short", timeZone: "UTC"})} to ${days[days.length - 1].toLocaleDateString("en-GB", {day: "numeric", month: "short", timeZone: "UTC"})} · ${n} run(s)`;
}
function renderLog() {
  if (!AG.data) return;
  const log = AG.data.log.concat(AG.live.filter(r => !AG.data.log.some(x => x.key === r.key))).slice().reverse();
  const tot = log.reduce((a, r) => a + (r.usd || 0), 0);
  $("#bgtotal").textContent = log.length ? `${log.length} runs · ${usd(tot)}` : "";
  $("#runlog").innerHTML = log.length ? log.slice(0, 40).map((r, i) => `<div class="evrow" data-i="${i}" style="grid-template-columns:110px 1fr auto"><span class="mono small muted">${E((r.ran_at || r.scheduled || "").slice(5, 16).replace("T", " "))}</span>
    <span><b style="font-weight:500">${E(r.title || r.agent)}</b> <span class="ink2">${E(String(r.summary || "").slice(0, 160))}</span></span><span class="pill ${r.status === "ok" ? "good" : r.status === "retried" ? "warn" : r.status === "failed" ? "bad" : "slate"}">${E(r.status)}</span></div>`).join("") : `<div class="empty">No runs yet. Turn an agent on and press +1 week.</div>`;
  $$("#runlog [data-i]").forEach(row => row.onclick = () => showRun(log[+row.dataset.i]));
}
function renderLeft() {
  const L = AG.data.left || [];
  $("#leftpanel").innerHTML = L.length ? `<div class="left">${L.map(x => `<div><div class="row"><b class="small" style="font-weight:500">${E(x.text)}</b></div>${(x.items || []).slice(0, 6).map(i => `<div class="item">${E(i)}</div>`).join("")}</div>`).join("")}</div>` : `<div class="empty">Nothing waits for a person.</div>`;
  const nx = AG.data.next || [];
  $("#nextpanel").innerHTML = nx.length ? nx.slice(0, 10).map(x => `<div class="row small" style="padding:5px 0"><span class="mono muted" style="width:96px">${E(x.label)}</span><span>${E((CAT.agents.find(a => a.id === x.id) || {}).title || x.id)}</span></div>`).join("") : `<div class="empty">Nothing on. Turn an agent on.</div>`;
}
function showRun(r) {
  const at = r.attempts || [];
  drawer(`${r.title || r.agent} · ${(r.scheduled || "").slice(0, 16).replace("T", " ")}`, `
    <div class="row wrap" style="margin-bottom:14px"><span class="pill ${r.status === "ok" ? "good" : r.status === "retried" ? "warn" : "bad"}">${E(r.status)}</span><span class="pill line">as ${E(r.as || "")}</span><span class="pill line">${fmt(r.tokens_in)} tokens in</span><span class="pill line">${usd(r.usd)}</span><span class="pill line">${secs(r.seconds)}</span>${r.stopped ? `<span class="pill warn">${E(r.stopped)}</span>` : ""}</div>
    ${at.length ? `<div class="label">Before the first model call: is Ledgerline up?</div><div class="timeline" style="margin-bottom:14px">${at.map(a => `<div class="ev ${a.ok ? "good" : "bad"}"><div class="small"><b class="mono" style="font-weight:500">${E(a.at.slice(11, 16))}</b> ${E(a.why)}${a.ok ? "" : " · no tokens spent, retry in 15 minutes"}</div></div>`).join("")}</div>` : ""}
    <div class="label">What it did</div>${(r.tool_calls || []).length ? (r.tool_calls || []).map(c => `<div class="check">${c.ok ? I.check : I.cross}<div><b class="mono" style="font-weight:500">${E(c.tool)}</b> <span class="ink2">${E(c.summary || "")}</span></div></div>`).join("") : `<div class="small muted">No tool calls.</div>`}
    <div class="label" style="margin-top:14px">What it changed (read from Ledgerline, before and after)</div>${(r.changed || []).length ? r.changed.map(c => `<div class="check"><span class="pill slate" style="height:20px">${E(c.kind)}</span><span class="ink2">${E(c.text)}</span></div>`).join("") : `<div class="small muted">Nothing in Ledgerline changed.</div>`}
    <div class="label" style="margin-top:14px">What it left for a person</div>${(r.left || []).length ? r.left.map(x => `<div class="small"><b style="font-weight:500">${E(x.text)}</b><div class="muted tiny">${E((x.items || []).slice(0, 5).join(" · "))}</div></div>`).join("") : `<div class="small muted">Nothing.</div>`}
    <div class="label" style="margin-top:14px">Its own summary (given to its next run)</div><p class="ink2">${E(r.summary || "")}</p>`);
}

/* ================================================================== 4 · TRIGGERS */
const TR = {data: null, cur: null};
function initTriggers() {
  $("#prov").onclick = async () => { await api("/api/triggers/config", {provenance: !$("#prov").classList.contains("on")}); loadTriggers(); };
}
async function loadTriggers() {
  try { TR.data = await api("/api/triggers"); } catch (e) { return; }
  setClock(TR.data.clock);
  $("#prov").classList.toggle("on", TR.data.provenance);
  $("#sources").innerHTML = Object.entries(CAT.sources).map(([k, s]) => `<div class="source"><div class="sh"><div class="ic" style="background:${{mail: "var(--accent-soft)", slack: "var(--violet-soft)", ledgerline: "var(--good-soft)"}[k]};color:${{mail: "var(--accent)", slack: "var(--violet)", ledgerline: "var(--good)"}[k]}">${I[s.icon].replace("<svg", '<svg width="16" height="16"')}</div>
    <div><h4>${E(s.title)}</h4><div class="tiny muted">${s.mode === "poll" ? `polled every ${s.every} minutes` : "pushed at once (webhook)"}</div></div></div>
    ${CAT.buttons.filter(b => b.source === k).map(b => `<button class="drop" data-drop="${b.id}"><div><b>${E(b.title)}</b><small>${E(b.hint)}</small></div><span class="plus">${I.plus}</span></button>`).join("")}</div>`).join("");
  $$("[data-drop]").forEach(b => b.onclick = () => drop(b.dataset.drop, b));
  $("#listeners").innerHTML = CAT.listeners.map(l => `<div class="listener"><span class="pill ${{mail: "accent", slack: "violet", ledgerline: "good"}[l.source]}">${E(CAT.sources[l.source].title)}</span>
    <div><div class="t">${E(l.title)}</div><small>when: ${E(l.match)} · then: ${E(l.action)}</small></div><button class="switch ${TR.data.listeners[l.id] ? "on" : ""}" data-l="${l.id}"></button></div>`).join("");
  $$("#listeners [data-l]").forEach(b => b.onclick = async () => { await api("/api/triggers/config", {id: b.dataset.l, on: !b.classList.contains("on")}); loadTriggers(); });
  renderEvents();
  if (!TR.cur && TR.data.events.length) TR.cur = TR.data.events[TR.data.events.length - 1];
  if (TR.cur) renderChain(TR.data.events.find(e => e.id === TR.cur.id) || TR.cur);
  else renderChain(null);
  const notes = TR.data.notes || [];
  $("#evnotes").innerHTML = notes.length ? notes.slice().reverse().map(n => `<div class="row" style="padding:6px 0;align-items:flex-start"><span class="pill ${n.prov === "untrusted" ? "bad" : "warn"}">${n.prov === "untrusted" ? "quarantined" : "filed"}</span><span class="small ink2">${E(n.text)}<br><span class="tiny muted">from ${E(n.source)}</span></span></div>`).join("") : `<div class="empty">Turn on "Any supplier e-mail → memory", then drop an e-mail.</div>`;
}
function renderEvents() {
  const evs = (TR.data.events || []).slice().reverse();
  $("#evlog").innerHTML = evs.length ? evs.map(e => `<div class="evrow" data-ev="${e.id}"><span class="mono small muted">${E(e.at.slice(11, 16))}</span><span class="small">${E(e.title)}</span><span class="pill ${e.status === "ran" ? "good" : e.status === "duplicate" ? "violet" : e.status === "running" ? "accent" : "slate"}">${E(e.status)}</span></div>`).join("") : `<div class="empty">Nothing yet.</div>`;
  $$("#evlog [data-ev]").forEach(r => r.onclick = () => { TR.cur = TR.data.events.find(e => e.id === r.dataset.ev); renderChain(TR.cur); });
}
function renderChain(ev) {
  const S = [["event", "Event"], ["listener", "Listener"], ["action", "Action"], ["result", "Result"]];
  if (!ev) { $("#chain").innerHTML = S.map(([k, t]) => `<div class="stage"><h5>${t}</h5><p class="muted">–</p></div>`).join(""); $("#chainextra").innerHTML = ""; return; }
  $("#chaintitle").textContent = ev.title + " · " + ev.at.slice(11, 16) + (ev.picked_at && ev.picked_at !== ev.at ? ` · picked up ${ev.picked_at.slice(11, 16)}` : "");
  const last = k => [...(ev.chain || [])].reverse().find(c => c.stage === k);
  $("#chain").innerHTML = S.map(([k, t]) => { const c = last(k); return `<div class="stage ${c ? "lit " + c.status : ""}"><h5>${t}${c && c.status === "running" ? ' <span class="spin" style="width:10px;height:10px;color:var(--accent)"></span>' : ""}</h5><p>${c ? E(c.text) : '<span class="muted">…</span>'}</p>${c && c.usd ? `<p class="tiny muted" style="margin-top:6px">${usd(c.usd)}</p>` : ""}</div>`; }).join("");
  let extra = "";
  if (ev.thread && ev.thread.length) extra += `<div class="thread"><div class="tiny muted" style="margin-bottom:4px">#purchasing · thread</div><div class="m"><b>Aiko</b> ${E(ev.message.text)}</div>${ev.thread.map(m => `<div class="m"><b>${E(m.user)}</b> ${E(m.text)}</div>`).join("")}${ev.pending ? `<button class="btn sm primary" id="confirmpr" style="margin-top:8px">Confirm as Emma</button>` : ""}</div>`;
  if (ev.message && ev.message.body) extra += `<details style="margin-top:10px"><summary class="small muted" style="cursor:pointer">The e-mail as it arrived</summary><div class="json" style="margin-top:6px">${E("From: " + ev.message.sender + "\nSubject: " + ev.message.subject + "\n\n" + ev.message.body)}</div></details>`;
  extra += `<div class="row" style="margin-top:10px"><button class="btn xs" id="replay">Replay this event</button><span class="tiny muted">a replay runs the action again: the tools are idempotent, so nothing is done twice</span></div>`;
  $("#chainextra").innerHTML = extra;
  if ($("#confirmpr")) $("#confirmpr").onclick = async () => { try { const r = await api("/api/triggers/confirm", {id: ev.id}); toast(r.result.ok ? `${r.result.request_no}: ${r.result.status}` : r.result.error); TR.cur = r.event; loadTriggers(); refreshInbox(); } catch (e) { toast(e.message); } };
  $("#replay").onclick = async () => { try { const r = await api("/api/triggers/replay", {id: ev.id}); await followEvent(r); } catch (e) { toast(e.message); } };
}
async function drop(kind, btn) {
  busy(btn, true);
  try { const r = await api("/api/triggers/drop", {kind}); await followEvent(r); } catch (e) { toast(e.message); } finally { busy(btn, false); }
}
async function followEvent(r) {
  TR.cur = {...r.event, chain: []}; renderChain(TR.cur);
  setClock(ME.clock);
  const j = await poll(r.job, evs => { evs.forEach(x => TR.cur.chain.push(x)); renderChain(TR.cur); }, 500);
  TR.cur = j.result; await loadTriggers(); renderChain(TR.cur); refreshInbox();
}

/* ================================================================== 5 · ASK NORTHBRIDGE */
const AK = {data: null, sending: false};
const QUICK = ["Morning", "Run my Monday chase", "What came in?", "Order the usual", "Anything waiting for Daniel?"];
function initAsk() {
  $("#quick").innerHTML = QUICK.map(q => `<button>${E(q)}</button>`).join("");
  $$("#quick button").forEach(b => b.onclick = () => say(b.textContent));
  $("#send").onclick = () => say($("#say").value);
  $("#say").addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); say($("#say").value); } });
  $("#say").addEventListener("input", e => autoGrow(e.target));
  $("#newchat").onclick = async () => { AK.data = await api("/api/chat/new", {}); $("#stream").innerHTML = ""; renderAsk(); toast("A new conversation: the briefing now starts from this moment."); };
}
async function loadAsk() {
  try { AK.data = await api("/api/chat"); } catch (e) { return; }
  setClock(AK.data.clock); renderAsk();
  $("#stream").innerHTML = AK.data.turns.length ? "" : `<div class="hello" id="chathello"><h3>Morning, Emma.</h3><p>It already knows what your memory holds, what ran overnight and what arrived. Try one of the prompts below.</p></div>`;
  AK.data.turns.forEach(t => { addMsg("me", t.text); addBot(t); });
}
function md(s) {
  const lines = E(s).split("\n"); let out = "", inList = false;
  for (const l of lines) {
    const m = l.match(/^\s*[-*•]\s+(.*)/);
    if (m) { if (!inList) { out += '<ul style="margin:4px 0 4px 18px;padding:0">'; inList = true; } out += `<li>${m[1]}</li>`; continue; }
    if (inList) { out += "</ul>"; inList = false; }
    out += l + "\n";
  }
  if (inList) out += "</ul>";
  return out.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\n(<ul)/g, "$1").replace(/<\/ul>\n/g, "</ul>").trim();
}
function addMsg(who, text) {
  $("#chathello") && $("#chathello").remove();
  const d = document.createElement("div"); d.className = "msg " + who; d.innerHTML = `<div class="b">${E(text)}</div>`;
  $("#stream").appendChild(d); $("#stream").scrollTop = 1e9; return d;
}
function addBot(t) {
  const d = document.createElement("div"); d.className = "msg bot";
  d.innerHTML = `<div class="who"><span class="lg">${I.spark}</span>Ask Northbridge</div><div class="steps">${(t.calls || []).map(c => `<span class="tchip ${c.ok ? "r" : "u"}" title="${E(c.summary)}">${E(c.tool)}</span>`).join("")}</div><div class="b">${md(t.reply)}</div>
    <div class="tiny muted">${fmt(t.tokens_in)} tokens in · ${(t.calls || []).length} tool call(s) · ${secs(t.seconds)} · ${usd(t.usd)}</div>`;
  $("#stream").appendChild(d); $("#stream").scrollTop = 1e9;
  if (t.window) renderWindow(t.window);
}
async function say(text) {
  text = (text || "").trim(); if (!text || AK.sending) return;
  AK.sending = true; $("#say").value = ""; autoGrow($("#say")); $("#send").disabled = true;
  addMsg("me", text);
  const d = document.createElement("div"); d.className = "msg bot";
  d.innerHTML = `<div class="who"><span class="lg">${I.spark}</span>Ask Northbridge</div><div class="steps"></div><div class="typing"><i></i><i></i><i></i></div>`;
  $("#stream").appendChild(d); $("#stream").scrollTop = 1e9;
  try {
    const j0 = await api("/api/chat/say", {text});
    const j = await poll(j0.id, evs => evs.forEach(ev => {
      const st = $(".steps", d);
      if (ev.kind === "call") st.insertAdjacentHTML("beforeend", `<span class="tchip" data-t="${E(ev.tool)}"><span class="spin" style="width:9px;height:9px"></span>${E(ev.tool)}</span>`);
      if (ev.kind === "result") { const c = [...$$(`[data-t="${CSS.escape(ev.tool)}"]`, st)].find(x => x.querySelector(".spin")); if (c) { c.className = "tchip " + (ev.ok ? "r" : "u"); c.innerHTML = E(ev.tool) + ` <span style="font-family:var(--font);font-weight:400">${E((ev.summary || "").slice(0, 70))}</span>`; } }
      $("#stream").scrollTop = 1e9;
    }), 500);
    d.remove(); addBot(j.result); AK.data = await api("/api/chat"); renderAsk(); refreshInbox();
  } catch (e) { d.remove(); toast(e.message); }
  finally { AK.sending = false; $("#send").disabled = false; }
}
function renderAsk() {
  const s = AK.data.since, m = AK.data.memory;
  const runs = s.runs || [];
  $("#railL").innerHTML = `
    <div class="panel"><div class="ph"><h3>While you were away</h3></div><div class="pb"><div class="tiny muted" style="margin-bottom:6px">since ${E(s.since_label)}</div><div class="away">
      ${runs.length ? runs.slice(-8).reverse().map(r => `<div class="a"><span class="ic">${(I[(CAT.agents.find(a => a.id === r.agent) || {}).icon] || I.receipt).replace("<svg", '<svg width="13" height="13"')}</span><div><b>${E(r.title || r.agent)}</b> · <span class="mono tiny">${E((r.ran_at || r.scheduled || "").slice(5, 16).replace("T", " "))}</span><br>${E(String(r.summary || "").slice(0, 150))}</div></div>`).join("") : `<div class="small muted">No background runs. Turn agents on in 3 and press +1 week.</div>`}</div></div></div>
    <div class="panel"><div class="ph"><h3>What came in</h3></div><div class="pb"><div class="away">${(s.events || []).length ? s.events.slice(-6).reverse().map(e => `<div class="a"><span class="ic">${I[CAT.sources[e.source].icon].replace("<svg", '<svg width="13" height="13"')}</span><div><b>${E(e.title)}</b><br>${E(e.result || e.status || "")}</div></div>`).join("") : `<div class="small muted">Nothing. Drop events in 4 · Triggers.</div>`}</div></div></div>
    <div class="panel"><div class="ph"><h3>Waiting</h3></div><div class="pb">
      ${(s.waiting || []).length ? s.waiting.map(w => `<div class="row small" style="padding:4px 0"><span class="mono">${E(w.doc_no)}</span><span class="muted">£${fmt(w.value)}</span><span class="sp"></span><span class="pill warn">${E(PEOPLE_SHORT[w.approver])}</span></div>`).join("") : `<div class="small muted">No approvals waiting.</div>`}
      ${(s.drafts || []).length ? `<div class="small" style="margin-top:8px"><b style="font-weight:500">${s.drafts.length} draft(s)</b> to read and send</div>` : ""}
      ${(s.held || []).length ? `<div class="small"><b style="font-weight:500">${s.held.length} invoice(s)</b> held</div>` : ""}</div></div>`;
  $("#railR").innerHTML = `<div class="panel"><div class="ph"><h3>This turn's context window</h3></div><div class="pb" id="askwin"><div class="small muted">Send a message to see what the model read, part by part.</div></div></div>
    <div class="panel"><div class="ph"><h3>Memory in use</h3><span class="sp"></span><a class="small" href="#memory">change</a></div><div class="pb"><b style="font-weight:500">${E(m.title)}</b> <span class="muted small">${E(m.kicker)}</span>
      <div class="tiny muted" style="margin:4px 0 8px">${m.source === "yours" ? "from your week" + (m.score ? ` · ${m.score.right}/10 right` : "") : m.source === "class" ? "the class's recorded week (run your own in 1)" : "empty"}</div>
      ${(m.files || []).map(f => `<span class="pill line mono" style="margin:0 4px 4px 0;font-size:11px">${E(f)}</span>`).join("")}${m.event_notes ? `<div class="tiny muted" style="margin-top:6px">+ ${m.event_notes} note(s) filed from e-mails</div>` : ""}</div></div>
    <div class="panel"><div class="ph"><h3>Routines as tools</h3></div><div class="pb">${(AK.data.routines || []).map(r => `<div style="padding:5px 0"><b class="small" style="font-weight:500">${E(r.name)}</b>${r.source === "class" ? ' <span class="pill slate" style="height:18px;font-size:10.5px">class</span>' : ""}<div class="tiny muted">${(r.params || []).map(p => `${E(p.name)}=${E(fmtParam(p.default))}`).join(" · ")}</div></div>`).join("")}</div></div>`;
  const last = AK.data.turns[AK.data.turns.length - 1];
  if (last && last.window) renderWindow(last.window);
}
function renderWindow(w) { const el = $("#askwin"); if (el) el.innerHTML = ctxBar(w.parts) + `<div class="budget"><span>estimated per part</span><span>${fmt(w.tokens_in)} counted by the model</span></div>`; }

boot().catch(e => toast(e.message));
