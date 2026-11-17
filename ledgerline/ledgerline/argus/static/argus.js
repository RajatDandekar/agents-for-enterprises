/* Argus · Lecture 6 · Observability and Evals. Vanilla JS, no build step. One section per tab. */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const E = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fmt = n => (n == null ? "–" : Number(n).toLocaleString("en-GB"));
const usd = v => v == null ? "–" : (v < 0.01 ? "$" + Number(v).toFixed(4) : "$" + Number(v).toFixed(3));
const ms = v => v == null ? "–" : (v < 1000 ? Math.round(v) + " ms" : (v / 1000).toFixed(2) + " s");
const KEYNAME = "argus-key";
let KEY = null, ME = null, CAT = null, TAB = "traces", PROMPT = "good", EVPROMPT = "good", GUARDS = [], SCN = "change_mind", PERSONA = "impatient", CVPROMPT = "good";
const TOOLNAME = {langfuse: "Langfuse", langsmith: "LangSmith", sentry: "Sentry"};
const linkBtns = (links) => Object.entries(links || {}).map(([k, u]) => `<a class="btn xs" href="${E(u)}" target="_blank" rel="noopener">Open in ${TOOLNAME[k] || k} ↗</a>`).join("");
try { KEY = localStorage.getItem(KEYNAME); } catch (e) { KEY = null; }

async function api(path, body) {
  const opt = {method: body !== undefined ? "POST" : "GET", headers: {"Content-Type": "application/json"}};
  if (KEY) opt.headers["X-Argus-Key"] = KEY;
  if (body !== undefined) opt.body = JSON.stringify(body);
  const r = await fetch(path, opt);
  let j = null; try { j = await r.json(); } catch (e) { j = null; }
  if (!r.ok) throw new Error((j && j.detail) || ("The server said " + r.status));
  return j;
}
async function poll(jid, onEvents, every = 700) {
  let since = 0;
  for (;;) {
    const j = await api(`/api/job/${jid}?since=${since}`);
    const evs = j.progress.events || []; since += evs.length;
    if (onEvents && evs.length) onEvents(evs, j);
    if (j.state !== "running") { if (j.state === "failed") throw new Error(j.error || "It failed."); return j; }
    await sleep(every);
  }
}
let toastT;
function toast(msg, t = 3600) { const el = $("#toast"); el.textContent = msg; el.classList.add("on"); clearTimeout(toastT); toastT = setTimeout(() => el.classList.remove("on"), t); }
function busy(btn, on, label) { if (!btn) return; if (on) { btn.dataset.l = btn.innerHTML; btn.disabled = true; btn.innerHTML = `<span class="spin"></span>${label || ""}`; } else { btn.disabled = false; if (btn.dataset.l) btn.innerHTML = btn.dataset.l; } }
function drawer(title, html) { $("#dtitle").textContent = title; $("#dbody").innerHTML = html; $("#drawer").classList.add("on"); $("#scrim").classList.add("on"); }
function closeDrawer() { $("#drawer").classList.remove("on"); $("#scrim").classList.remove("on"); }
$("#dclose").onclick = closeDrawer; $("#scrim").onclick = closeDrawer;
document.addEventListener("keydown", e => { if (e.key === "Escape") closeDrawer(); });
const J = o => `<pre class="json">${E(typeof o === "string" ? o : JSON.stringify(o, null, 1))}</pre>`;
const md = s => E(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");

/* ------------------------------------------------------------------ join */
function showLab() {
  $("#join").classList.add("hide"); $("#lab").classList.remove("hide");
  $("#avatar").textContent = (ME.name || "?").slice(0, 1).toUpperCase();
  PROMPT = ME.prompt || "good"; GUARDS = ME.guards || CAT.presets.code;
  $$("#promptseg button").forEach(b => b.classList.toggle("on", b.dataset.p === PROMPT));
  $("#guardstab").classList.toggle("hide", !ME.guards_station);
  spend(); renderChat(); renderGuards(); renderAttacks(); renderMyAttacks(); renderTasks(); renderRecorded(); renderScenarios(); renderMyConvos();
  if (ME.evals && ME.evals.length) renderEval(ME.evals[ME.evals.length - 1]);
  go(location.hash.slice(1) || "traces");
}
function spend() { $("#spend").textContent = `US$${(ME.spend_usd || 0).toFixed(2)} of ${(ME.student_cap_usd || 0).toFixed(2)}`; }
async function refreshMe() { try { ME = await api("/api/me"); spend(); } catch (e) { /* ignore */ } }
async function boot() {
  CAT = await api("/api/catalog");
  if (KEY) { try { ME = await api("/api/me"); $("#wname").textContent = ME.name; $("#welcome").classList.remove("hide"); $("#joinform").classList.add("hide"); $("#keyline").classList.add("hide"); } catch (e) { KEY = null; } }
}
$("#joinform").addEventListener("submit", async e => {
  e.preventDefault(); const b = $("#joinbtn"); busy(b, true, "Opening");
  try { ME = await api("/api/join", {name: $("#name").value}); KEY = ME.key; try { localStorage.setItem(KEYNAME, KEY); } catch (x) { /* private mode */ } showLab(); }
  catch (x) { toast(x.message); } finally { busy(b, false); }
});
$("#enter").onclick = () => showLab();
$("#notme").onclick = e => { e.preventDefault(); try { localStorage.removeItem(KEYNAME); } catch (x) { /**/ } KEY = null; location.reload(); };
$("#usekey").onclick = async e => { e.preventDefault(); const k = prompt("Paste your key (ar-…)"); if (!k) return; KEY = k.trim(); try { ME = await api("/api/me"); localStorage.setItem(KEYNAME, KEY); showLab(); } catch (x) { toast("That key is not known here."); KEY = null; } };
$("#keybtn").onclick = () => drawer("Your key for the class notebooks", `<p class="small">The notebooks call Claude through Argus's gateway, with your Argus key as the API key. It spends from the same daily budget as the stations.</p>
  <span class="label" style="margin-top:12px">Paste this into the notebook's first cell</span><pre class="json" id="keybox">ARGUS_URL = "${E(location.origin)}"\nARGUS_KEY = "${E(KEY)}"</pre>
  <div class="row" style="margin-top:10px"><button class="btn primary" id="copykey">Copy</button><span class="tiny muted">Keep it to yourself: anyone with it spends your budget.</span></div>`);
document.addEventListener("click", e => { if (e.target && e.target.id === "copykey") { navigator.clipboard.writeText($("#keybox").textContent).then(() => toast("Copied.")); } });
function go(t) { if (!["traces", "evals", "convos", "guards"].includes(t) || (t === "guards" && !(ME && ME.guards_station))) t = "traces"; TAB = t; $$(".tab").forEach(s => s.classList.toggle("on", s.id === "tab-" + t)); $$("#tabs a").forEach(a => a.classList.toggle("on", a.dataset.tab === t)); }
$$("#tabs a").forEach(a => a.addEventListener("click", e => { e.preventDefault(); history.replaceState(null, "", "#" + a.dataset.tab); go(a.dataset.tab); }));

/* ------------------------------------------------------------------ 1 · traces */
const SUGG = ["Order the usual, please, needed by 4 Dec 2026.", "Order the usual, please.", "Yes, go ahead.", "How many BAT-500 do we have?", "Please deal with the new invoice in the AP inbox.", "What does Brightcell Energy charge for a BAT-500 pack?"];
$("#sugg").innerHTML = SUGG.map(s => `<button class="chipbtn">${E(s)}</button>`).join("");
$$("#sugg .chipbtn").forEach(b => b.onclick = () => { $("#say").value = b.textContent; $("#say").focus(); });
function renderChat() {
  const c = $("#convo"), turns = ME.chat || [];
  if (!turns.length) { c.innerHTML = `<div class="empty">Say something to Ask Northbridge, as Emma (it acts with her permissions, in your own sandbox).</div>`; return; }
  c.innerHTML = turns.map((t, i) => `<div class="bub emma">${E(t.text)}<span class="pmark ${t.prompt}">${t.prompt === "thursday" ? "Thursday prompt" : t.prompt === "custom" ? "my edit" : ""}</span></div>
    <div class="toolline">${(t.calls || []).map(x => `<span class="tchip ${/^(create|approve|release|register|send|record|post|hold|receive)/.test(x.tool) ? (x.args && x.args.confirm ? "u" : "w") : "r"}">${E(x.tool)}${x.args && "confirm" in x.args ? ` confirm=${x.args.confirm}` : ""}</span>`).join("")}</div>
    <div class="bub bot${t.incident ? " inc" : ""}" data-i="${i}">${md(t.reply)}<div class="bmeta">${t.incident ? '<span class="pill bad">committed without a yes</span>' : ""}<span>${fmt(t.tokens_in)} in · ${fmt(t.tokens_out)} out · ${usd(t.usd)} · ${t.seconds}s</span><a href="#" class="small" data-trace="${E(t.trace_id)}">trace</a></div></div>`).join("");
  $$("#convo [data-trace]").forEach(a => a.onclick = async e => { e.preventDefault(); const r = await api("/api/trace/" + a.dataset.trace); const t = turns[+a.closest(".bub").dataset.i]; drawTrace({...t, spans: r.spans, url: r.url, links: r.links}); });
  c.scrollTop = c.scrollHeight;
}
$$("#promptseg button").forEach(b => b.onclick = async () => {
  let custom;
  if (b.dataset.p === "custom") { custom = await editPrompt(); if (custom == null) return; }
  ME = await api("/api/chat/prompt", {prompt: b.dataset.p, ...(custom != null ? {custom} : {})}); PROMPT = ME.prompt;
  $$("#promptseg button").forEach(x => x.classList.toggle("on", x.dataset.p === PROMPT));
  toast(PROMPT === "thursday" ? "Thursday prompt on: the next message starts a new conversation with it." : "Prompt changed: the next message starts a new conversation.");
});
function promptDiff(a, b) {
  const A = a.split("\n"), B = b.split("\n");
  return B.map(l => A.includes(l) ? `<div class="dl">${E(l)}</div>` : `<div class="dl add">+ ${E(l)}</div>`).join("") + A.filter(l => !B.includes(l)).map(l => `<div class="dl del">− ${E(l)}</div>`).join("");
}
$("#showprompt").onclick = () => {
  const cur = PROMPT === "custom" ? (ME.custom || CAT.prompts.good) : CAT.prompts[PROMPT];
  drawer(PROMPT === "thursday" ? "The Thursday prompt (changes against the good prompt)" : "The system prompt", `<p class="small muted" style="margin-bottom:10px">${PROMPT === "good" ? "Lecture 5's Ask Northbridge prompt, unchanged." : "Green lines are new; red lines were removed."} Below it, the agent also reads Emma's memory files and the briefing.</p><div class="diff">${promptDiff(CAT.prompts.good, cur)}</div>`);
};
function editPrompt() {
  return new Promise(res => {
    drawer("My edit of the system prompt", `<p class="small muted">Change anything. Your edit is used for your chat and, in Evals, as “My edit”. <code>{now}</code> becomes the date.</p><textarea class="input mono" id="ped" rows="26" style="margin-top:10px;font-size:12px">${E(ME.custom || CAT.prompts.good)}</textarea><div class="row" style="margin-top:10px"><button class="btn primary" id="pedok">Use my edit</button><button class="btn ghost" id="pedcancel">Cancel</button></div>`);
    $("#pedok").onclick = () => { const v = $("#ped").value; closeDrawer(); res(v); };
    $("#pedcancel").onclick = () => { closeDrawer(); res(null); };
  });
}
$("#newchat").onclick = async () => { ME = await api("/api/chat/new", {}); renderChat(); $("#wf").innerHTML = `<div class="empty">New conversation, fresh sandbox.</div>`; $("#incident").classList.add("hide"); };
$("#sayform").addEventListener("submit", async e => {
  e.preventDefault(); const text = $("#say").value.trim(); if (!text) return;
  const b = $("#saybtn"); busy(b, true); $("#say").value = "";
  const c = $("#convo"); if (!(ME.chat || []).length) c.innerHTML = "";
  c.insertAdjacentHTML("beforeend", `<div class="bub emma">${E(text)}</div><div class="toolline live" id="livecalls"></div><div class="bub bot thinking" id="thinking"><span class="spin"></span> working…</div>`);
  c.scrollTop = c.scrollHeight;
  $("#wf").innerHTML = `<div class="wf-live" id="wflive"><div class="row muted small"><span class="spin"></span>the trace fills in as it works</div></div>`;
  try {
    const j = await api("/api/chat/say", {text});
    const done = await poll(j.id, evs => { for (const ev of evs) {
      if (ev.kind === "call") { $("#livecalls").insertAdjacentHTML("beforeend", `<span class="tchip">${E(ev.tool)}${ev.args && "confirm" in ev.args ? " confirm=" + ev.args.confirm : ""}</span>`); $("#wflive").insertAdjacentHTML("beforeend", `<div class="wfl">execute_tool <b>${E(ev.tool)}</b> <code>${E(JSON.stringify(ev.args)).slice(0, 140)}</code></div>`); }
    } });
    await refreshMe(); renderChat(); drawTrace(done.result);
  } catch (x) { toast(x.message); $("#thinking") && $("#thinking").remove(); }
  finally { busy(b, false); }
});
const KIND_ICON = {invoke_agent: "◆", chat: "✦", execute_tool: "⚒", guardrail: "⛨", span: "·"};
function drawTrace(t) {
  const sp = t.spans || [];
  $("#tlinks").innerHTML = linkBtns(t.links && Object.keys(t.links).length ? t.links : (t.url ? {langfuse: t.url} : {}));
  const root = sp[0]; const total = root ? Math.max(1, root.end - root.start) : 1;
  $("#tmeta").textContent = root ? `${sp.length} spans · ${ms(total)} · ${fmt(t.tokens_in)} tokens in · ${usd(t.usd)}` : "";
  const inc = $("#incident");
  if (t.incident) { inc.classList.remove("hide"); inc.innerHTML = `<b>This turn saved a purchase request without Emma's yes.</b> Look for <code>create_purchase_request</code> with <code>confirm: true</code> below: no turn of Emma's between the preview and the commit.`; }
  else inc.classList.add("hide");
  $("#wf").innerHTML = `<div class="wfh"><span>span</span><span>timeline (${ms(total)})</span><span class="r">tokens</span><span class="r">cost</span></div>` + sp.map((s, i) => {
    const l = (s.start / total) * 100, w = Math.max(0.6, ((s.end - s.start) / total) * 100);
    const tag = s.kind === "execute_tool" && s.confirm === true ? `<span class="pill bad xs">confirm=true</span>` : s.preview ? `<span class="pill warn xs">preview</span>` : s.refused_by ? `<span class="pill bad xs">refused</span>` : s.kind === "guardrail" ? `<span class="pill ${/refused|blocked|quarantined|flagged|redacted/.test(s.decision) ? "bad" : "good"} xs">${E(s.decision)}</span>` : "";
    return `<div class="wfr k-${s.kind}${s.confirm === true ? " hot" : ""}" data-i="${i}"><span class="nm" style="padding-left:${s.depth * 16}px"><i>${KIND_ICON[s.kind] || "·"}</i>${E(s.name)} ${tag}</span><span class="bar"><b style="left:${l}%;width:${w}%"></b><em>${ms(s.end - s.start)}</em></span><span class="r num">${s.tokens_in ? fmt(s.tokens_in) + "/" + fmt(s.tokens_out) : ""}</span><span class="r num">${s.usd ? usd(s.usd) : ""}</span></div>`;
  }).join("");
  $$("#wf .wfr").forEach(r => r.onclick = () => { $$("#wf .wfr").forEach(x => x.classList.remove("sel")); r.classList.add("sel"); spanDetail(sp[+r.dataset.i]); });
  const hot = sp.findIndex(s => s.confirm === true);
  const pick = hot >= 0 ? hot : 0;
  if (sp[pick]) { $$("#wf .wfr")[pick].classList.add("sel"); spanDetail(sp[pick]); }
}
function spanDetail(s) {
  const a = s.attrs || {};
  const std = Object.entries(a).filter(([k]) => k.startsWith("gen_ai.")).map(([k, v]) => `<span>${E(k)}</span><span>${E(typeof v === "object" ? JSON.stringify(v) : v)}</span>`).join("");
  let body = "";
  if (s.kind === "execute_tool") body = `<div class="grid2"><div><span class="label">arguments (gen_ai.tool.call.arguments)</span>${J(s.args)}</div><div><span class="label">result (gen_ai.tool.call.result)</span>${J(s.result)}</div></div>`;
  else if (s.kind === "chat") body = `<div class="grid2"><div><span class="label">last message in (input.value)</span>${J(s.input_last)}</div><div><span class="label">what the model asked for (gen_ai.output.messages)</span>${J(s.output)}</div></div>`;
  else if (s.kind === "guardrail") body = J(a["langfuse.observation.output"] || s.decision);
  else if (s.kind === "invoke_agent") body = `<div class="grid2"><div><span class="label">input: Emma's message</span>${J(s.input_last)}</div><div><span class="label">output: the reply</span>${J(((s.output || [])[0] || {}).parts ? s.output[0].parts.map(p => p.content).join("") : "")}</div></div>`;
  $("#spand").innerHTML = `<div class="sdh"><b>${E(s.name)}</b><span class="muted small">${ms(s.end - s.start)} · status ${E(s.status)}</span></div><div class="kv small">${std}</div>${body}`;
}

/* ------------------------------------------------------------------ 2 · evals */
function renderTasks() {
  $("#tasklist").innerHTML = `<span class="label" style="margin-top:8px">The quick suite</span>` + CAT.quick.map(id => { const t = CAT.tasks.find(x => x.id === id); return `<div class="task"><b>${t.id}</b> ${E(t.title)}<div class="tiny muted">“${E(t.turns.join(" → "))}”</div><div class="kinds">${t.kinds.map(k => `<span class="kd ${k}">${k}</span>`).join("")}</div></div>`; }).join("");
}
$$("#evprompt button").forEach(b => b.onclick = () => { EVPROMPT = b.dataset.p; $$("#evprompt button").forEach(x => x.classList.toggle("on", x === b)); });
async function runEval(mode, btn) {
  if (EVPROMPT === "custom" && !(ME.custom || "").trim()) { toast("Write your edit first: Traces tab, My edit."); return; }
  busy(btn, true, mode === "quick" ? "Running 6 tasks" : "Running 3 times");
  const n = mode === "quick" ? CAT.quick.length : 3; let done = 0;
  $("#verdict").innerHTML = `<div class="pb"><div class="row"><span class="spin"></span><b>Running</b><span class="muted small" id="evprog">0 of ${n}</span></div><div class="prog"><i id="evbar" style="width:0%"></i></div><div class="tiny muted" id="evlog"></div></div>`;
  try {
    const j = await api("/api/evals/run", {mode, prompt: EVPROMPT});
    const r = await poll(j.id, evs => { for (const ev of evs) if (ev.kind === "done") { done++; $("#evprog").textContent = `${done} of ${n}`; $("#evbar").style.width = (100 * done / n) + "%"; $("#evlog").insertAdjacentHTML("beforeend", `<span class="pill ${ev.pass ? "good" : "bad"} xs">${ev.task}${mode === "passk" ? "·" + (ev.rep + 1) : ""}</span> `); } }, 1200);
    await refreshMe(); renderEval(r.result);
  } catch (x) { toast(x.message); $("#verdict").innerHTML = `<div class="empty">${E(x.message)}</div>`; }
  finally { busy(btn, false); }
}
$("#runquick").onclick = e => runEval("quick", e.currentTarget);
$("#runpassk").onclick = e => runEval("passk", e.currentTarget);
const PNAME = {good: "the good prompt", thursday: "the Thursday prompt", custom: "your edit"};
function renderEval(run) {
  if (!run) return;
  const pk = run.pass_k;
  $("#verdict").innerHTML = `<div class="pb vd ${run.ship ? "ok" : "no"}"><div class="vbig">${run.ship ? "Would ship" : "Would not ship"}</div>
    <div class="vsub">${run.mode === "quick" ? "Quick suite" : "pass^3 on “Order the usual”"} on ${PNAME[run.prompt] || run.prompt}: <b>${run.passed} of ${run.of}</b> runs passed every check${pk ? ` · pass^3 = <b>${pk.pass_hat_k === 1 ? "yes" : "no"}</b> (${run.passed}/3 runs passed)` : ""} · ${usd(run.usd)}</div>
    <div class="tiny muted">The gate: every outcome and trajectory check must pass (they are code: they read Ledgerline and the tool calls). The judge's verdict on the words is shown, not gated.</div></div>`;
  $("#evrows").innerHTML = `<table class="t evt"><thead><tr><th>Task</th><th>Outcome</th><th>Trajectory</th><th>Numbers</th><th>Judge (words)</th><th class="r">Cost</th><th></th></tr></thead><tbody>${run.rows.map((r, i) => {
    const cell = k => { const cs = r.checks.filter(c => c.kind === k); if (!cs.length) return `<td class="muted">–</td>`; const ok = cs.every(c => c.pass); return `<td><span class="pill ${ok ? "good" : "bad"} xs" title="${E(cs.map(c => c.why).join(" · "))}">${ok ? "pass" : "fail"}</span></td>`; };
    return `<tr data-i="${i}" class="clk"><td><b>${r.task}</b>${run.mode === "passk" ? " · run " + (r.rep + 1) : ""} <span class="muted">${E(r.title)}</span>${r.error ? ` <span class="pill bad xs">error</span>` : ""}</td>${cell("outcome")}${cell("trajectory")}${cell("numbers")}${cell("words")}<td class="r">${usd(r.usd)}</td><td>${r.url ? `<a href="${E(r.url)}" target="_blank" rel="noopener" class="small">trace ↗</a>` : ""}</td></tr>`; }).join("")}</tbody></table>`;
  $$("#evrows tr.clk").forEach(tr => tr.onclick = e => { if (e.target.closest("a")) return; const r = run.rows[+tr.dataset.i];
    drawer(`${r.task} · ${r.title}`, `<span class="label">Every check</span><table class="t">${r.checks.map(c => `<tr><td><span class="kd ${c.kind}">${c.kind}</span></td><td><span class="pill ${c.pass ? "good" : "bad"} xs">${c.pass ? "pass" : "fail"}</span></td><td style="white-space:normal">${E(c.why)}</td></tr>`).join("")}</table>
      <span class="label" style="margin-top:14px">The reply</span><div class="replybox">${md(r.reply || "")}</div><span class="label" style="margin-top:14px">Tool calls</span>${J(r.calls.map(c => `${c.tool} ${JSON.stringify(c.args)}${c.refused_by ? "  ← refused by " + c.refused_by : ""}`).join("\n"))}`); });
}
function renderRecorded() {
  const R = CAT.recorded || {}; const el = $("#recorded");
  if (!R.suite) { el.innerHTML = `<div class="empty">Not recorded yet.</div>`; return; }
  el.innerHTML = `<table class="t"><thead><tr><th>Prompt</th><th class="r">Runs</th><th class="r">Passed every check</th><th class="r">pass^k</th><th class="r">Commits without a yes</th></tr></thead><tbody>${R.suite.map(s => `<tr><td>${E(s.label)}</td><td class="r">${s.runs}</td><td class="r">${s.passed}</td><td class="r">${s.pass_hat_k ?? "–"}</td><td class="r">${s.unseen_commits ?? "–"}</td></tr>`).join("")}</tbody></table><p class="tiny muted" style="margin-top:8px">${E(R.note || "")}</p>`;
}

/* ------------------------------------------------------------------ 3 · conversations */
function renderScenarios() {
  $("#scnlist").innerHTML = CAT.scenarios.map(x => `<button class="scn ${x.id === SCN ? "on" : ""}" data-s="${x.id}"><b>${E(x.title)}</b><span>${E(x.goal)}</span><small>expected: ${E(x.expect)}</small></button>`).join("");
  $$("#scnlist .scn").forEach(b => b.onclick = () => { SCN = b.dataset.s; renderScenarios(); });
  $("#personas").innerHTML = Object.keys(CAT.personas).map(k => `<button data-p="${k}" class="${k === PERSONA ? "on" : ""}">${k}</button>`).join("");
  $$("#personas button").forEach(b => b.onclick = () => { PERSONA = b.dataset.p; renderScenarios(); });
  $("#personaline").textContent = CAT.personas[PERSONA];
}
$$("#cvprompt button").forEach(b => b.onclick = () => { CVPROMPT = b.dataset.p; $$("#cvprompt button").forEach(x => x.classList.toggle("on", x === b)); });
const turnHTML = (who, text, calls) => who === "emma" ? `<div class="bub emma"><span class="simtag">simulated Emma</span>${E(text)}</div>` :
  `<div class="toolline">${(calls || []).map(c => `<span class="tchip ${/^(create|approve|release|register|send|record|post|hold|receive)/.test(c.tool || c) ? ((c.args && c.args.confirm) ? "u" : "w") : "r"}">${E(c.tool || c)}${c.args && "confirm" in c.args ? " confirm=" + c.args.confirm : ""}${c.refused_by ? " ✕" : ""}</span>`).join("")}</div><div class="bub bot">${md(text)}</div>`;
$("#runconvo").onclick = async e => {
  const btn = e.currentTarget;
  if (CVPROMPT === "custom" && !(ME.custom || "").trim()) { toast("Write your edit first: Traces tab, My edit."); return; }
  busy(btn, true, "Emma is typing");
  const box = $("#cvconvo"); box.innerHTML = ""; $("#cvmeta").textContent = ""; $("#cvlinks").innerHTML = "";
  $("#cvverdict").innerHTML = `<div class="pb"><div class="row"><span class="spin"></span><b>The conversation is running</b></div><p class="tiny muted" style="margin-top:8px">It is scored when Emma says DONE, or after the turn budget.</p></div>`;
  try {
    const j = await api("/api/convo/run", {scenario: SCN, persona: PERSONA, prompt: CVPROMPT});
    const r = await poll(j.id, evs => { for (const ev of evs) {
      if (ev.kind === "emma") { box.insertAdjacentHTML("beforeend", turnHTML("emma", ev.text) + `<div class="toolline live" data-live="1"></div>`); }
      else if (ev.kind === "call") { const l = $$("#cvconvo [data-live]").pop(); if (l) l.insertAdjacentHTML("beforeend", `<span class="tchip">${E(ev.tool)}${ev.args && "confirm" in ev.args ? " confirm=" + ev.args.confirm : ""}</span>`); }
      else if (ev.kind === "agent") { box.insertAdjacentHTML("beforeend", `<div class="bub bot">${md(ev.text)}</div>`); }
      box.scrollTop = box.scrollHeight; } }, 900);
    await refreshMe(); renderConvo(r.result); renderMyConvos();
  } catch (x) { toast(x.message); $("#cvverdict").innerHTML = `<div class="empty">${E(x.message)}</div>`; }
  finally { busy(btn, false); }
};
function renderConvo(r) {
  if (!r) return;
  $("#cvconvo").innerHTML = r.turns.map(t => turnHTML("emma", t.emma) + turnHTML("agent", t.reply, t.calls)).join("") + (r.emma_done ? `<div class="bub emma"><span class="simtag">simulated Emma</span>DONE</div>` : "");
  $("#cvmeta").textContent = `${r.turns.length} turns · ${usd(r.usd)} · ${r.seconds}s`;
  $("#cvlinks").innerHTML = linkBtns(r.links);
  const KN = {outcome: "outcome", trajectory: "trajectory", turns: "turns", words: "words"};
  $("#cvverdict").innerHTML = `<div class="pb vd ${r.pass ? "ok" : "no"}"><div class="vbig">${r.pass ? "The conversation passed" : r.gate ? "Passed the code checks, not the judge" : "The conversation failed"}</div>
    <div class="vsub">${E(r.title)} · ${E(r.persona)} Emma · ${PNAME[r.prompt] || r.prompt}</div>
    <div class="tiny muted" style="margin-bottom:10px">Expected at the end: ${E(r.expect)}</div>
    ${r.error ? `<div class="pill bad">${E(r.error)}</div>` : r.checks.map(c => `<div class="cvck ${c.pass ? "" : "bad"}"><span class="kd ${KN[c.kind] === "turns" ? "numbers" : c.kind}">${c.kind === "words" ? "judge" : "code"}</span><b>${E(c.name)}</b><span class="pill ${c.pass ? "good" : "bad"} xs">${c.pass ? "pass" : "fail"}</span><span class="small">${E(c.why)}</span></div>`).join("")}</div>`;
}
function renderMyConvos() {
  const rows = (ME.convos || []).slice().reverse();
  $("#mycv").innerHTML = rows.length ? `<table class="t"><thead><tr><th>Goal</th><th>Emma</th><th>Prompt</th><th>Turns</th><th>Result</th></tr></thead><tbody>${rows.map((r, i) => `<tr class="clk" data-i="${i}"><td><b>${E(r.title)}</b></td><td>${E(r.persona)}</td><td>${E(r.prompt)}</td><td>${r.turns.length}</td><td><span class="pill ${r.pass ? "good" : "bad"} xs">${r.pass ? "passed" : "failed"}</span></td></tr>`).join("")}</tbody></table>` : `<div class="empty">Nothing yet.</div>`;
  $$("#mycv tr.clk").forEach(tr => tr.onclick = () => renderConvo(rows[+tr.dataset.i]));
  if (rows.length && !$("#cvconvo .bub")) renderConvo(rows[0]);
}

/* ------------------------------------------------------------------ 4 · guards (next lecture; behind a flag) */
function renderGuards() {
  const grp = k => CAT.guards.filter(g => g.kind === k);
  const row = g => `<div class="knob"><div class="n">${E(g.title)} <span class="where">${E(g.where)}</span><small>${E(g.line)}</small></div><button class="switch ${GUARDS.includes(g.id) ? "on" : ""}" data-g="${g.id}" aria-label="${E(g.title)}"></button></div>`;
  $("#guardlist").innerHTML = `<span class="label">Code (deterministic)</span>${grp("code").map(row).join("")}<span class="label" style="margin-top:12px">Models (detectors)</span>${grp("model").map(row).join("")}`;
  $$("#guardlist .switch").forEach(b => b.onclick = () => { const g = b.dataset.g; GUARDS = GUARDS.includes(g) ? GUARDS.filter(x => x !== g) : [...GUARDS, g]; b.classList.toggle("on"); syncPreset(); });
  syncPreset();
}
function syncPreset() { const s = [...GUARDS].sort().join(); const name = Object.entries(CAT.presets).find(([, v]) => [...v].sort().join() === s); $$("#presets button").forEach(b => b.classList.toggle("on", name && b.dataset.s === name[0])); }
$$("#presets button").forEach(b => b.onclick = () => { GUARDS = [...CAT.presets[b.dataset.s]]; renderGuards(); });
function renderAttacks() {
  $("#attacklist").innerHTML = CAT.attacks.map(a => `<button class="att" data-a="${a.id}"><span class="aid">${a.id}</span><span class="at">${E(a.title)}<small>“${E(a.turns.join(" → ")).slice(0, 150)}${a.turns.join(" → ").length > 150 ? "…" : ""}”</small></span><span class="ameta"><span class="pill slate xs">${E(a.owasp)}</span>${a.channel === "indirect" ? '<span class="pill violet xs">via e-mail</span>' : ""}${a.session ? '<span class="pill warn xs">as SVC_AGENT</span>' : ""}</span></button>`).join("");
  $$("#attacklist .att").forEach(b => b.onclick = () => attack({attack: b.dataset.a}, b));
}
$("#ownform").addEventListener("submit", e => { e.preventDefault(); const t = $("#own").value.trim(); if (t) attack({text: t}, e.submitter); });
async function attack(body, btn) {
  busy(btn, true);
  $("#attres").innerHTML = `<div class="pb"><div class="row"><span class="spin"></span><b>Attacking</b><span class="muted small">guards on: ${GUARDS.length ? GUARDS.map(g => CAT.guards.find(x => x.id === g).title).join(", ") : "none"}</span></div><div class="toolline" id="attlive" style="margin-top:10px"></div></div>`;
  try {
    const j = await api("/api/guards/attack", {...body, guards: GUARDS});
    const r = await poll(j.id, evs => { for (const ev of evs) if (ev.kind === "call") $("#attlive").insertAdjacentHTML("beforeend", `<span class="tchip">${E(ev.tool)}</span>`); else if (ev.kind === "result" && ev.refused_by) $("#attlive").insertAdjacentHTML("beforeend", `<span class="tchip u">refused: ${E(ev.refused_by)}</span>`); });
    await refreshMe(); renderAttackResult(r.result); renderMyAttacks();
  } catch (x) { toast(x.message); $("#attres").innerHTML = `<div class="empty">${E(x.message)}</div>`; }
  finally { busy(btn, false); }
}
function renderAttackResult(r) {
  const stopped = r.stopped_by || [];
  $("#attres").innerHTML = `<div class="pb ares ${r.succeeded ? "thru" : "held"}"><div class="row"><span class="abig">${r.succeeded ? "It worked" : "It did not work"}</span><span class="sp"></span>${r.url ? `<a class="btn xs" href="${E(r.url)}" target="_blank" rel="noopener">Trace in Langfuse ↗</a>` : ""}</div>
    <div class="small">${E(r.attack)} · ${E(r.title)} · <span class="muted">${E(r.why)}</span></div>
    <div class="row wrap" style="margin-top:8px"><span class="label" style="margin:0">Stopped by</span>${stopped.length ? stopped.map(g => `<span class="pill ${["confirm_yes", "identity", "approvals", "limits", "never_events", "provenance", "output_check"].includes(g) ? "accent" : "violet"}">${E((CAT.guards.find(x => x.id === g) || {}).title || g)}</span>`).join("") : `<span class="pill line">${r.succeeded ? "nothing" : "the model itself refused (no guard needed this time)"}</span>`}</div>
    <span class="label" style="margin-top:12px">What the guards did, in order</span><div class="gev">${(r.events || []).filter(e => e.guard !== "tool boundary" || e.decision !== "passed").map(e => `<div class="ge ${/refused|blocked|quarantined|flagged|redacted/.test(e.decision) ? "bad" : ""}"><b>${E(e.guard)}</b><span class="pill xs ${/refused|blocked|quarantined|flagged|redacted/.test(e.decision) ? "bad" : "good"}">${E(e.decision)}</span><span class="tiny muted">${E(e.where)}${e.ms ? " · " + e.ms + " ms" : ""}</span><span class="small">${E(e.why || "")}</span></div>`).join("") || '<div class="tiny muted">No guard was on.</div>'}</div>
    <span class="label" style="margin-top:12px">Tool calls</span><div class="toolline">${(r.calls || []).map(c => `<span class="tchip ${c.refused_by ? "u" : c.args && c.args.confirm ? "w" : "r"}">${E(c.tool)}${c.refused_by ? " ✕" : ""}</span>`).join("") || '<span class="tiny muted">none</span>'}</div>
    <span class="label" style="margin-top:12px">The reply</span><div class="replybox">${md((r.replies || []).slice(-1)[0] || "")}</div></div>`;
}
function renderMyAttacks() {
  const rows = (ME.attacks || []).slice().reverse();
  $("#myatt").innerHTML = rows.length ? `<table class="t"><thead><tr><th>Attack</th><th>Guards</th><th>Result</th><th>Stopped by</th></tr></thead><tbody>${rows.slice(0, 25).map(r => `<tr><td><b>${E(r.attack)}</b> <span class="muted">${E(r.title)}</span></td><td>${E(r.set)}</td><td><span class="pill ${r.succeeded ? "bad" : "good"} xs">${r.succeeded ? "got through" : "held"}</span></td><td class="small">${E((r.stopped_by || []).join(", ") || "–")}</td></tr>`).join("")}</tbody></table>` : `<div class="empty">Nothing yet.</div>`;
}

boot().catch(e => toast("Could not reach Argus: " + e.message));
