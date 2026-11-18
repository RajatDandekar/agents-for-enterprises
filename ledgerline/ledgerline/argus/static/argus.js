/* Argus · Lecture 6 · Observability and Evals. Vanilla JS, no build step. One section per tab.
   Lecture 7 (guards flag on): the Guards switch in the chat, the station's prompt picker, A00. With the flag off
   ME.guards_station is false and none of it is shown or drawn.
   v3 (Lecture 6, always on): the teaching views at the end of this file: One turn, four checks; Is the judge right?;
   The same checks in DeepEval; Score with DeepEval (Conversations); Write the score on this trace (Traces). */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const E = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fmt = n => (n == null ? "–" : Number(n).toLocaleString("en-GB"));
const usd = v => v == null ? "–" : (v < 0.01 ? "$" + Number(v).toFixed(4) : "$" + Number(v).toFixed(3));
const ms = v => v == null ? "–" : (v < 1000 ? Math.round(v) + " ms" : (v / 1000).toFixed(2) + " s");
const KEYNAME = "argus-key";
let KEY = null, ME = null, CAT = null, TAB = "traces", PROMPT = "good", EVPROMPT = "good", GUARDS = [], SCN = "change_mind", PERSONA = "impatient", CVPROMPT = "good", ATTPROMPT = "good";
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
  $("#chatguards").classList.toggle("hide", !ME.guards_station); syncChatGuards();
  if (ME.guards_station) $(".brand small").textContent = "Lecture 7 · Guardrails and Red-Teaming";
  spend(); renderChat(); renderGuards(); renderAttacks(); renderMyAttacks(); renderTasks(); renderRecorded(); renderScenarios(); renderMyConvos();
  if (ME.evals && ME.evals.length) renderEval(ME.evals[ME.evals.length - 1]);
  go(location.hash.slice(1) || "traces");
  initTeach();
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
function go(t) { const sub = String(t).split(":")[1]; t = String(t).split(":")[0];   /* #evals:turn opens a view inside Evals */
  if (!["traces", "evals", "convos", "guards"].includes(t) || (t === "guards" && !(ME && ME.guards_station))) t = "traces"; TAB = t; if (t === "evals" && sub) evview(sub); $$(".tab").forEach(s => s.classList.toggle("on", s.id === "tab-" + t)); $$("#tabs a").forEach(a => a.classList.toggle("on", a.dataset.tab === t)); }
$$("#tabs a").forEach(a => a.addEventListener("click", e => { e.preventDefault(); history.replaceState(null, "", "#" + a.dataset.tab); go(a.dataset.tab); }));

/* ------------------------------------------------------------------ 1 · traces */
const SUGG = ["Order the usual, please, needed by 4 Dec 2026.", "Order the usual, please.", "Yes, go ahead.", "How many BAT-500 do we have?", "Please deal with the new invoice in the AP inbox.", "What does Brightcell Energy charge for a BAT-500 pack?"];
$("#sugg").innerHTML = SUGG.map(s => `<button class="chipbtn">${E(s)}</button>`).join("");
$$("#sugg .chipbtn").forEach(b => b.onclick = () => { $("#say").value = b.textContent; $("#say").focus(); });
const GTITLE = g => (CAT.guards.find(x => x.id === g) || {}).title || g;
const pmark = t => { const p = t.prompt === "thursday" ? "Thursday prompt" : t.prompt === "custom" ? "my edit" : "";
  return t.guards ? `<span class="pmark">${p ? p + " · " : ""}guards on</span>` : `<span class="pmark ${t.prompt}">${p}</span>`; };
const letThrough = (t, x) => !!(t.guards && x.args && x.args.confirm === true && x.ok && !x.refused_by && (t.allowed || []).includes(x.tool));
function guardNote(t) {   /* Guards switch on: a call a guard refused (which guard, why, the next step), or a commit it let through */
  if (!t.guards) return "";
  return (t.refused || []).map(r => `<div class="gnote"><b>⛨ Refused by the guard “${E(GTITLE(r.guard))}”</b><span><code>${E(r.tool)}</code> was stopped at the tool boundary, before it ran. ${E(r.why || "")}</span><span><b>Next step it gave the model:</b> ${E(r.next_step || "")}</span></div>`).join("") +
    ((t.allowed || []).length ? `<div class="gnote ok"><b>⛨ Allowed by the guards</b><span><code>${E(t.allowed.join(", "))}</code> with <code>confirm=true</code> passed the tool boundary: the same document was previewed in an earlier turn, and Emma said yes in this one.</span></div>` : "");
}
function syncChatGuards() { $("#chatguardsw").classList.toggle("on", !!(ME && ME.chat_guards)); }
$("#chatguardsw").onclick = async () => {
  try { ME = await api("/api/chat/guards", {on: !ME.chat_guards}); } catch (x) { toast(x.message); return; }
  syncChatGuards(); renderChat();
  $("#wf").innerHTML = `<div class="empty">New conversation, fresh sandbox${ME.chat_guards ? ", guards on" : ", guards off"}.</div>`; $("#incident").classList.add("hide"); $("#spand").innerHTML = ""; $("#tmeta").textContent = ""; $("#tlinks").innerHTML = "";
  toast(ME.chat_guards ? "Guards on: a new chat. Code now checks every tool call before it runs." : "Guards off: a new chat, nothing between the model and the tools.");
};
function renderChat() {
  const c = $("#convo"), turns = ME.chat || [];
  if (!turns.length) { c.innerHTML = `<div class="empty">Say something to Ask Northbridge, as Emma (it acts with her permissions, in your own sandbox).</div>`; return; }
  c.innerHTML = turns.map((t, i) => `<div class="bub emma">${E(t.text)}${pmark(t)}</div>
    <div class="toolline">${(t.calls || []).map(x => `<span class="tchip ${x.refused_by ? "u" : letThrough(t, x) ? "ok" : /^(create|approve|release|register|send|record|post|hold|receive)/.test(x.tool) ? (x.args && x.args.confirm ? "u" : "w") : "r"}">${E(x.tool)}${x.args && "confirm" in x.args ? ` confirm=${x.args.confirm}` : ""}${x.refused_by ? " ✕ refused" : letThrough(t, x) ? " ✓ allowed" : ""}</span>`).join("")}</div>${guardNote(t)}
    <div class="bub bot${t.incident ? " inc" : ""}${t.guards && (t.refused || []).length ? " ref" : t.guards && (t.allowed || []).length ? " alw" : ""}" data-i="${i}">${md(t.reply)}<div class="bmeta">${t.incident ? '<span class="pill bad">committed without a yes</span>' : ""}${t.guards && (t.refused || []).length ? '<span class="pill accent">a guard refused a call</span>' : ""}${t.guards && (t.allowed || []).length ? '<span class="pill good">saved after Emma’s yes</span>' : ""}<span>${fmt(t.tokens_in)} in · ${fmt(t.tokens_out)} out · ${usd(t.usd)} · ${t.seconds}s</span><a href="#" class="small" data-trace="${E(t.trace_id)}">trace</a></div></div>`).join("");
  $$("#convo [data-trace]").forEach(a => a.onclick = async e => { e.preventDefault(); const r = await api("/api/trace/" + a.dataset.trace); const t = turns[+a.closest(".bub").dataset.i]; drawTrace({...t, spans: r.spans, url: r.url, links: r.links}); });
  const lt = turns[turns.length - 1], le = lt.guards && ((lt.refused || []).length || (lt.allowed || []).length) ? $$("#convo .bub.emma").pop() : null;
  c.scrollTop = le ? le.offsetTop - c.offsetTop - 8 : c.scrollHeight;   /* a turn the guards acted on opens at Emma's message, so the guard's note is in view */
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
      else if (ev.kind === "result" && ev.refused_by) { $("#livecalls").insertAdjacentHTML("beforeend", `<span class="tchip u">✕ refused by ${E(ev.refused_by)}</span>`); $("#wflive").insertAdjacentHTML("beforeend", `<div class="wfl">guardrail <b>${E(ev.refused_by.replace("guard: ", ""))}</b> refused <b>${E(ev.tool)}</b></div>`); }
    } });
    await refreshMe(); renderChat(); drawTrace(done.result);
  } catch (x) { toast(x.message); $("#thinking") && $("#thinking").remove(); }
  finally { busy(b, false); }
});
const KIND_ICON = {invoke_agent: "◆", chat: "✦", execute_tool: "⚒", guardrail: "⛨", span: "·"};
function drawTrace(t) {
  const sp = t.spans || [];
  $("#tlinks").innerHTML = linkBtns(t.links && Object.keys(t.links).length ? t.links : (t.url ? {langfuse: t.url} : {}));
  scoreUI(t);
  const root = sp[0]; const total = root ? Math.max(1, root.end - root.start) : 1;
  $("#tmeta").textContent = root ? `${sp.length} spans · ${ms(total)} · ${fmt(t.tokens_in)} tokens in · ${usd(t.usd)}` : "";
  const inc = $("#incident");
  inc.classList.remove("stop", "pass");
  if (t.incident) { inc.classList.remove("hide"); inc.innerHTML = `<b>This turn saved a purchase request without Emma's yes.</b> Look for <code>create_purchase_request</code> with <code>confirm: true</code> below: no turn of Emma's between the preview and the commit.`; }
  else if (t.guards && (t.refused || []).length) { inc.classList.remove("hide"); inc.classList.add("stop");
    inc.innerHTML = t.refused.map(r => `<b>A guard refused <code>${E(r.tool)}</code> in this turn: that call saved nothing.</b> Stopped at the tool boundary by <b>${E(GTITLE(r.guard))}</b> (the <code>guardrail ${E(r.guard)}</code> span below). <b>Reason:</b> ${E(r.why || "")} <b>Next step it returned to the model:</b> ${E(r.next_step || "")}`).join("<br>") +
      ((t.allowed || []).length ? `<br><b>Allowed in the same turn:</b> <code>${E(t.allowed.join(", "))}</code>.` : ""); }
  else if (t.guards && (t.allowed || []).length) { inc.classList.remove("hide"); inc.classList.add("pass");
    inc.innerHTML = `<b>The guards allowed this commit.</b> <code>${E(t.allowed.join(", "))}</code> with <code>confirm: true</code> passed the tool boundary (the <code>guardrail tool boundary</code> span below): the same document was previewed in an earlier turn, and Emma said yes in this one.`; }
  else inc.classList.add("hide");
  const under = i => { const o = []; for (let k = i + 1; k < sp.length && sp[k].depth > sp[i].depth; k++) if (sp[k].kind === "guardrail") o.push(sp[k].decision); return o; };
  const passed = (s, i) => !!(t.guards && s.kind === "execute_tool" && s.confirm === true && !s.refused_by && under(i).includes("passed"));
  $("#wf").innerHTML = `<div class="wfh"><span>span</span><span>timeline (${ms(total)})</span><span class="r">tokens</span><span class="r">cost</span></div>` + sp.map((s, i) => {
    const l = (s.start / total) * 100, w = Math.max(0.6, ((s.end - s.start) / total) * 100);
    const tag = s.refused_by && t.guards ? `<span class="pill accent xs">refused</span>` : passed(s, i) ? `<span class="pill good xs">allowed</span>` : s.kind === "execute_tool" && s.confirm === true ? `<span class="pill bad xs">confirm=true</span>` : s.preview ? `<span class="pill warn xs">preview</span>` : s.refused_by ? `<span class="pill bad xs">refused</span>` : s.kind === "guardrail" ? `<span class="pill ${/refused|blocked|quarantined|flagged|redacted/.test(s.decision) ? "bad" : "good"} xs">${E(s.decision)}</span>` : "";
    return `<div class="wfr k-${s.kind}${s.refused_by && t.guards ? " stop" : passed(s, i) ? " pass" : s.confirm === true ? " hot" : ""}" data-i="${i}"><span class="nm" style="padding-left:${s.depth * 16}px"><i>${KIND_ICON[s.kind] || "·"}</i>${E(s.name)} ${tag}</span><span class="bar"><b style="left:${l}%;width:${w}%"></b><em>${ms(s.end - s.start)}</em></span><span class="r num">${s.tokens_in ? fmt(s.tokens_in) + "/" + fmt(s.tokens_out) : ""}</span><span class="r num">${s.usd ? usd(s.usd) : ""}</span></div>`;
  }).join("");
  $$("#wf .wfr").forEach(r => r.onclick = () => { $$("#wf .wfr").forEach(x => x.classList.remove("sel")); r.classList.add("sel"); spanDetail(sp[+r.dataset.i]); });
  const hot = sp.findIndex(s => s.confirm === true), ref = t.guards ? sp.findIndex(s => s.refused_by) : -1;
  const pick = ref >= 0 ? ref : hot >= 0 ? hot : 0;
  if (sp[pick]) { $$("#wf .wfr")[pick].classList.add("sel"); spanDetail(sp[pick]); }
}
function spanDetail(s) {
  const a = s.attrs || {};
  const std = Object.entries(a).filter(([k]) => k.startsWith("gen_ai.")).map(([k, v]) => `<span>${E(k)}</span><span>${E(typeof v === "object" ? JSON.stringify(v) : v)}</span>`).join("");
  let body = "";
  if (s.kind === "execute_tool") body = (s.refused_by && s.result && typeof s.result === "object" ? `<div class="gnote"><b>⛨ Refused by ${E(s.refused_by)}</b><span><b>Rule:</b> ${E(s.result.rule || "")} · <b>Reason:</b> ${E(s.result.error || "")}</span><span><b>Next step returned to the model:</b> ${E(s.result.next_step || "")}</span></div>` : "") + `<div class="grid2"><div><span class="label">arguments (gen_ai.tool.call.arguments)</span>${J(s.args)}</div><div><span class="label">result (gen_ai.tool.call.result)</span>${J(s.result)}</div></div>`;
  else if (s.kind === "chat") body = `<div class="grid2"><div><span class="label">last message in (input.value)</span>${J(s.input_last)}</div><div><span class="label">what the model asked for (gen_ai.output.messages)</span>${J(s.output)}</div></div>`;
  else if (s.kind === "guardrail") body = J(s.guard || a["langfuse.observation.output"] || s.decision);
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
  renderCvde(r);
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
$$("#attprompt button").forEach(b => b.onclick = () => { ATTPROMPT = b.dataset.p; $$("#attprompt button").forEach(x => x.classList.toggle("on", x === b)); });
const ownPrompt = id => ((ME.attacks_first || []).find(a => a.id === id) || {}).prompt;   /* A00 is the Thursday prompt's incident */
const PTAG = p => `<span class="pill ${p === "thursday" ? "warn" : "line"} xs">${p === "thursday" ? "Thursday prompt" : "good prompt"}</span>`;
function renderAttacks() {
  $("#attacklist").innerHTML = (ME.attacks_first || []).concat(CAT.attacks).map(a => `<button class="att" data-a="${a.id}"><span class="aid">${a.id}</span><span class="at">${E(a.title)}<small>“${E(a.turns.join(" → ")).slice(0, 150)}${a.turns.join(" → ").length > 150 ? "…" : ""}”</small></span><span class="ameta"><span class="pill slate xs">${E(a.owasp)}</span>${a.channel === "indirect" ? '<span class="pill violet xs">via e-mail</span>' : ""}${a.session ? '<span class="pill warn xs">as SVC_AGENT</span>' : ""}${a.prompt === "thursday" ? '<span class="pill warn xs">always the Thursday prompt</span>' : ""}</span></button>`).join("");
  $$("#attacklist .att").forEach(b => b.onclick = () => attack({attack: b.dataset.a}, b));
}
$("#ownform").addEventListener("submit", e => { e.preventDefault(); const t = $("#own").value.trim(); if (t) attack({text: t}, e.submitter); });
async function attack(body, btn) {
  busy(btn, true);
  $("#attres").innerHTML = `<div class="pb"><div class="row"><span class="spin"></span><b>Attacking</b><span class="muted small">${PNAME[ownPrompt(body.attack) || ATTPROMPT]} · guards on: ${GUARDS.length ? GUARDS.map(g => CAT.guards.find(x => x.id === g).title).join(", ") : "none"}</span></div><div class="toolline" id="attlive" style="margin-top:10px"></div></div>`;
  try {
    const j = await api("/api/guards/attack", {...body, guards: GUARDS, ...(ownPrompt(body.attack) ? {} : {prompt: ATTPROMPT})});
    const r = await poll(j.id, evs => { for (const ev of evs) if (ev.kind === "call") $("#attlive").insertAdjacentHTML("beforeend", `<span class="tchip">${E(ev.tool)}</span>`); else if (ev.kind === "result" && ev.refused_by) $("#attlive").insertAdjacentHTML("beforeend", `<span class="tchip u">refused: ${E(ev.refused_by)}</span>`); });
    await refreshMe(); renderAttackResult(r.result); renderMyAttacks();
  } catch (x) { toast(x.message); $("#attres").innerHTML = `<div class="empty">${E(x.message)}</div>`; }
  finally { busy(btn, false); }
}
function renderAttackResult(r) {
  const stopped = r.stopped_by || [];
  $("#attres").innerHTML = `<div class="pb ares ${r.succeeded ? "thru" : "held"}"><div class="row"><span class="abig">${r.succeeded ? "It worked" : "It did not work"}</span><span class="sp"></span>${r.url ? `<a class="btn xs" href="${E(r.url)}" target="_blank" rel="noopener">Trace in Langfuse ↗</a>` : ""}</div>
    <div class="small">${E(r.attack)} · ${E(r.title)} · ${PTAG(r.prompt)} · <span class="muted">${E(r.why)}</span></div>
    <div class="row wrap" style="margin-top:8px"><span class="label" style="margin:0">Stopped by</span>${stopped.length ? stopped.map(g => `<span class="pill ${["confirm_yes", "identity", "approvals", "limits", "never_events", "provenance", "output_check"].includes(g) ? "accent" : "violet"}">${E((CAT.guards.find(x => x.id === g) || {}).title || g)}</span>`).join("") : `<span class="pill line">${r.succeeded ? "nothing" : "the model itself refused (no guard needed this time)"}</span>`}</div>
    <span class="label" style="margin-top:12px">What the guards did, in order</span><div class="gev">${(r.events || []).filter(e => e.guard !== "tool boundary" || e.decision !== "passed").map(e => `<div class="ge ${/refused|blocked|quarantined|flagged|redacted/.test(e.decision) ? "bad" : ""}"><b>${E(e.guard)}</b><span class="pill xs ${/refused|blocked|quarantined|flagged|redacted/.test(e.decision) ? "bad" : "good"}">${E(e.decision)}</span><span class="tiny muted">${E(e.where)}${e.ms ? " · " + e.ms + " ms" : ""}</span><span class="small">${E(e.why || "")}</span></div>`).join("") || '<div class="tiny muted">No guard was on.</div>'}</div>
    <span class="label" style="margin-top:12px">Tool calls</span><div class="toolline">${(r.calls || []).map(c => `<span class="tchip ${c.refused_by ? "u" : c.args && c.args.confirm ? "w" : "r"}">${E(c.tool)}${c.refused_by ? " ✕" : ""}</span>`).join("") || '<span class="tiny muted">none</span>'}</div>
    <span class="label" style="margin-top:12px">The reply</span><div class="replybox">${md((r.replies || []).slice(-1)[0] || "")}</div></div>`;
}
function renderMyAttacks() {
  const rows = (ME.attacks || []).slice().reverse();
  $("#myatt").innerHTML = rows.length ? `<table class="t"><thead><tr><th>Attack</th><th>Prompt</th><th>Guards</th><th>Result</th><th>Stopped by</th></tr></thead><tbody>${rows.slice(0, 25).map(r => `<tr><td><b>${E(r.attack)}</b> <span class="muted">${E(r.title)}</span></td><td>${r.prompt === "thursday" ? "Thursday" : "good"}</td><td>${E(r.set)}</td><td><span class="pill ${r.succeeded ? "bad" : "good"} xs">${r.succeeded ? "got through" : "held"}</span></td><td class="small">${E((r.stopped_by || []).join(", ") || "–")}</td></tr>`).join("")}</tbody></table>` : `<div class="empty">Nothing yet.</div>`;
}

/* ================================================================== v3 · the teaching views (Lecture 6, 21 Nov) */
let TEACH = null, EVVIEW = "suite", TURN = null, TURNID = null, JEV = true, JRES = {}, JSTYLE = null, JBOX = null, DEM = "tool", CVCUR = null;
const SCORES = {};
const VP = (p, none = "not run yet") => p == null ? `<span class="verdict none">${none}</span>` : `<span class="verdict ${p ? "ok" : "no"}">${p ? "PASS" : "FAIL"}</span>`;
const PLABEL = p => p === "thursday" ? "Thursday prompt" : p === "custom" ? "my edit of the prompt" : "good prompt";
function evview(v) {
  if (!["suite", "turn", "judge", "deepeval"].includes(v)) v = "suite"; EVVIEW = v;
  $$("#evnav button").forEach(b => b.classList.toggle("on", b.dataset.v === v)); $$(".evview").forEach(x => x.classList.toggle("on", x.id === "ev-" + v));
  if (v === "turn" && !TURN && KEY) pickTurn("friday");
}
$$("#evnav button").forEach(b => b.onclick = () => { history.replaceState(null, "", b.dataset.v === "suite" ? "#evals" : "#evals:" + b.dataset.v); evview(b.dataset.v); });
async function initTeach() {
  try { TEACH = await api("/api/teach"); } catch (e) { TEACH = {turns: [], labelled: [], scores: [], deepeval: {}}; }
  renderTpick(); renderLabelled(); renderJrun(); renderJ56(); deInit();
}

/* ---- one turn, four checks */
function renderTpick() {
  const ts = ((TEACH && TEACH.turns) || []).concat([{id: "mine", label: "My last chat turn", sub: "from your chat in Traces · asks the judge once, under US$0.001"}]);
  $("#tpick").innerHTML = ts.map(t => `<button class="tpb ${t.id === TURNID ? "on" : ""}" data-t="${E(t.id)}"><b>${E(t.label)}</b><span>${E(t.sub)}</span></button>`).join("");
  $$("#tpick .tpb").forEach(b => b.onclick = () => pickTurn(b.dataset.t));
}
async function pickTurn(id) {
  TURNID = id; renderTpick();
  try {
    if (id === "mine") {
      $("#tcards").innerHTML = `<div class="panel"><div class="pb row"><span class="spin"></span>Reading your last turn, running the three code checks and asking the judge…</div></div>`; $("#tjudge").innerHTML = "";
      const j = await api("/api/teach/turn/mine", {}); TURN = (await poll(j.id)).result; await refreshMe();
    } else TURN = await api("/api/teach/turn/" + id);
    JEV = true; renderTurn();
  } catch (x) { TURN = null; $("#tturn").innerHTML = `<div class="empty">${E(x.message)}</div>`; $("#tcards").innerHTML = ""; $("#tjudge").innerHTML = ""; $("#tlesson").classList.add("hide"); }
}
function markReply(reply, marks) {   /* the reply with every £ figure marked: found in a tool result, or not */
  let out = "", i = 0;
  for (const m of marks) { out += E(reply.slice(i, m.start)) + `<mark class="f ${m.found ? "" : "no"}" title="${m.found ? "found in " + E(m.source) : "in no tool result"}">${E(m.text)}</mark>`; i = m.end; }
  return (out + E(reply.slice(i))).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
}
function card4(c) {
  const extra = c.kind === "numbers" && c.marks.length ? `<div class="figs">${c.marks.map(m => `<span class="fig ${m.found ? "" : "no"}">${E(m.text)}<small>${m.found ? "found in " + E(m.source) : "in no tool result"}</small></span>`).join("")}</div>` : "";
  const why = c.kind === "words" ? (c.why ? E(c.why) : "Not run yet: press “Run the judge” below.") : E(c.why);
  return `<div class="card4 ${c.pass == null ? "" : c.pass ? "ok" : "no"}" data-kind="${c.kind}"><div class="c4h"><h3>${E(c.title)}</h3><span class="by ${c.kind === "words" ? "judge" : ""}">${E(c.by)}</span>${VP(c.pass, c.kind === "outcome" ? "NOT YET" : "not run yet")}</div>
    <div class="c4r"><span>reads</span><span>${E(c.reads)}</span><span>asks</span><span>${E(c.asks)}</span></div>${extra}<div class="c4why">${why}</div><span class="fn">${E(c.fn)}()</span></div>`;
}
function renderTurn() {
  const t = TURN, tr = t.turn, nums = t.cards.find(c => c.kind === "numbers"), out = t.cards.find(c => c.kind === "outcome");
  $("#tturn").innerHTML = `<p class="tiny muted" style="margin-bottom:8px">${E(t.source || "")}</p>${tr.links && Object.keys(tr.links).length ? `<div class="tlk" id="tlinks2">${linkBtns(tr.links)}</div>` : ""}` + (tr.earlier || []).map((e, i) => `<div class="tearlier"><b>Earlier, turn ${i + 1}.</b> Emma: “${E(e.text)}” Ask Northbridge answered, and this turn follows.</div>`).join("") +
    `<div class="tsec">Emma's message${tr.n > 1 ? " (turn " + tr.n + ")" : ""} · ${PLABEL(t.prompt)}</div><div class="convo"><div class="bub emma">${E(tr.text)}</div></div>
    <div class="tsec">The tool calls, in order</div><div class="steps">${tr.calls.map((c, i) => `<div class="step"><i>call ${i + 1}</i><span class="tchip ${/^(create|approve|release|register|send|record|post|hold|receive)/.test(c.tool) ? (c.confirm ? "u" : "w") : "r"}">${E(c.tool)}${c.confirm != null ? " confirm=" + c.confirm : ""}</span>${c.confirm === true ? '<span class="small ink2">saves</span>' : c.confirm === false ? '<span class="small ink2">a preview</span>' : ""}${c.ok ? "" : '<span class="pill bad xs">did not go through</span>'}</div>`).join("") || '<span class="small muted">No tool was called.</span>'}</div>
    <div class="tsec">The reply · £ figures: <mark class="f">found in a tool result</mark> <mark class="f no">in no tool result</mark></div><div class="treply">${markReply(tr.reply || "", nums.marks)}</div>
    <div class="tsec">Ledgerline at the end of the conversation: what it saved</div><div class="holds ${out.holds.length ? "" : "none"}">${out.holds.length ? out.holds.map(E).join("<br>") : "Nothing: no request, no order."}</div>${tr.after ? `<p class="tafter">${E(tr.after)}</p>` : ""}`;
  $("#tcards").innerHTML = t.cards.map(card4).join("");
  const ls = $("#tlesson"); ls.classList.toggle("hide", !t.lesson); ls.innerHTML = t.lesson ? `<b>Notice.</b> ${E(t.lesson)}` : "";
  renderJudge();
}
function renderJudge() {
  const c = TURN.cards.find(x => x.kind === "words"), j = c.judge, v = c.verdict;
  $("#tjudge").innerHTML = `<div class="ph"><h3>The judge's prompt, in three parts</h3><span class="by judge">a judge · ${E(j.model)}</span><span class="muted small">behind the fourth card, “The words”</span><span class="sp"></span><span id="jverdict">${VP(v ? v.pass : null)}</span></div>
    <div class="pb col"><p class="small ink2">Everything the judge is sent, in three parts. It is also given Emma's message (“${E(j.user)}”) and fixed instructions: <span class="muted">${E(j.instructions)}</span></p>
    <div class="jparts">
      <div class="jpart"><h4><span class="pn">1</span>The criterion <span class="muted small" style="font-weight:400">· you can change it</span></h4><textarea id="jcrit" spellcheck="false">${E(j.criterion)}</textarea></div>
      <div class="jpart"><h4><span class="pn">2</span>The evidence <span class="muted small" style="font-weight:400">· what the tools returned</span><span class="sp"></span><button class="switch ${JEV ? "on" : ""}" id="jev" aria-label="Give the judge the evidence"></button></h4><div id="jevbox" class="jev ${JEV ? "" : "off"}">${JEV ? evBlocks(j) : EVOFF}</div></div>
      <div class="jpart"><h4><span class="pn">3</span>The reply to check</h4><pre class="reply">${E(j.reply).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")}</pre></div>
    </div>
    <div class="jrun"><button class="btn primary" id="jrunbtn">Run the judge</button><span class="tiny muted">one call to Claude Haiku, under US$0.001 from your daily budget</span><span class="sp"></span><span class="tiny muted" id="jnote">${v ? "shown: " + E(v.recorded || "the verdict from when this turn was checked, the evidence on") : "not run yet"}</span></div>
    <div id="jresult">${v ? judgeResult(v) : ""}</div></div>`;
  $("#jev").onclick = () => { JEV = !JEV; $("#jev").classList.toggle("on", JEV); const b = $("#jevbox"); b.classList.toggle("off", !JEV); b.innerHTML = JEV ? evBlocks(j) : EVOFF; };
  $("#jrunbtn").onclick = async e => {
    const btn = e.currentTarget, crit = $("#jcrit").value.trim(); if (!crit) { toast("Write the criterion first."); return; }
    busy(btn, true, "The judge is reading");
    try { const jb = await api("/api/teach/judge", {turn: TURNID, criterion: crit, evidence: JEV}); const r = (await poll(jb.id)).result; await refreshMe();
      $("#jresult").innerHTML = judgeResult(r); $("#jverdict").innerHTML = VP(r.pass); $("#jnote").textContent = `just now · the evidence ${r.evidence_on ? "on" : "off"} · ${usd(r.usd)}`;
      const w = $('#tcards .card4[data-kind="words"]'); if (w) w.outerHTML = card4({...c, asks: crit, pass: r.pass, why: r.reason + (r.evidence_on ? "" : " (run with the evidence off)")}); }
    catch (x) { toast(x.message); } finally { busy(btn, false); }
  };
}
const EVOFF = "Evidence off: the judge is sent no tool result. It has only the criterion and the reply.";
const evBlocks = j => (j.blocks || []).map(b => `<h5>${E(b.label)}</h5><pre>${E(b.text)}</pre>`).join("") || E(j.evidence);
const judgeResult = v => `<div class="jres"><div class="c4why ${v.pass ? "ok" : "no"}"><b>The judge's reason.</b> ${E(v.reason)}</div>${VP(v.pass)}</div>`;

/* ---- is the judge right? */
const JNAME = {naive: "the naive judge", specific: "the specific judge, no evidence", grounded: "the grounded judge"};
function renderLabelled() {
  const L = (TEACH && TEACH.labelled) || [], V = (JSTYLE && JRES[JSTYLE] && JRES[JSTYLE].verdicts) || {};
  $("#jrlist").innerHTML = L.map((x, i) => `<div class="lab" data-i="${i}"><span class="pill ${x.label ? "good" : "bad"} xs">${x.label ? "right" : "wrong"}</span><span class="q">${E(x.user)}</span><span>${V[x.id] ? `<span class="pill ${V[x.id].pass ? "line" : "slate"} xs">judge: ${V[x.id].pass ? "pass" : "fail"}</span>` : ""}</span><span class="ch">${E(x.note)}</span></div>`).join("") || `<div class="empty">The labelled set is not in this copy of Argus.</div>`;
  $$("#jrlist .lab").forEach(el => el.onclick = () => { const x = L[+el.dataset.i]; let rep = E(x.reply); if (x.changed) rep = rep.replace(E(x.changed.new), `<mark class="f no">${E(x.changed.new)}</mark>`);
    drawer(x.user, `<div class="row"><span class="pill ${x.label ? "good" : "bad"}">a person marked it ${x.label ? "right" : "wrong"}</span><span class="small ink2">${E(x.note)}</span></div>
      <span class="label" style="margin-top:14px">The reply</span><div class="replybox">${rep.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")}</div>
      <span class="label" style="margin-top:14px">The criterion (given to the specific and the grounded judge)</span><div class="replybox">${E(x.criterion)}</div>
      <span class="label" style="margin-top:14px">What the judges said here</span>${Object.keys(JRES).map(k => JRES[k].verdicts[x.id] ? `<div class="cvck ${JRES[k].verdicts[x.id].pass ? "" : "bad"}"><span class="kd words">judge</span><b>${E(JNAME[k])}</b><span class="pill ${JRES[k].verdicts[x.id].pass ? "good" : "bad"} xs">${JRES[k].verdicts[x.id].pass ? "pass" : "fail"}</span><span class="small">${E(JRES[k].verdicts[x.id].reason)}</span></div>` : "").join("") || '<p class="small muted">No judge has been run yet.</p>'}`); });
}
function renderJrun() {
  const q = (TEACH && TEACH.naive_question) || "Is this reply helpful, accurate and professional?";
  $("#jrrun").innerHTML = [["naive", "Run the naive judge", `It is asked only: “${E(q)}” It sees the reply alone.`],
    ["specific", "Run the specific judge", "It gets the task's own criterion, but no evidence: it cannot see what the tools returned."],
    ["grounded", "Run the grounded judge", "The criterion and the evidence: the tool results Ask Northbridge itself had."]]
    .map(([k, b, t]) => `<div class="jbtn"><button class="btn ${k === "grounded" ? "primary" : ""}" data-j="${k}">${b}</button><p>${t}</p></div>`).join("");
  $$("#jrrun button").forEach(b => b.onclick = () => runLabelled(b.dataset.j, b));
}
function boxesOf(V) {   /* the four boxes from the verdicts so far (the server sends the same when the run ends) */
  const o = {right_passed: [], right_failed: [], wrong_failed: [], wrong_passed: []};
  for (const x of TEACH.labelled) { const v = V[x.id]; if (!v) continue; o[(x.label ? "right_" : "wrong_") + (v.pass ? "passed" : "failed")].push({id: x.id, reason: v.reason}); }
  const wrong = o.wrong_failed.length + o.wrong_passed.length, right = o.right_passed.length + o.right_failed.length, fa = o.right_failed.length;
  return {boxes: o, wrong, right, line: wrong + right ? `It caught ${o.wrong_failed.length} of ${wrong} wrong replies, and raised ${fa} false alarm${fa === 1 ? "" : "s"} in ${right} right replies.` : ""};
}
const BOXTXT = {right_passed: "right, and passed", right_failed: "right, but failed: a false alarm", wrong_passed: "wrong, but passed: missed", wrong_failed: "wrong, and failed: caught"};
const BOXMINI = {right_passed: "passed", right_failed: "false alarm", wrong_passed: "missed", wrong_failed: "caught"};
function boxGrid(counts, right, wrong, mini) {
  const b = k => `<button class="box ${k === "right_passed" || k === "wrong_failed" ? "good" : "bad"} ${!mini && JBOX === k ? "sel" : ""}" data-b="${k}"><b>${counts[k]}</b><span>${(mini ? BOXMINI : BOXTXT)[k]}</span></button>`;
  return `<div class="boxes ${mini ? "mini" : ""}"><span></span><span class="hd top">${mini ? "judge: pass" : "The judge passed it"}</span><span class="hd top">${mini ? "judge: fail" : "The judge failed it"}</span>
    <span class="hd">${mini ? "right (" + right + ")" : "A person marked it right (" + right + ")"}</span>${b("right_passed")}${b("right_failed")}
    <span class="hd">${mini ? "wrong (" + wrong + ")" : "A person marked it wrong (" + wrong + ")"}</span>${b("wrong_passed")}${b("wrong_failed")}</div>`;
}
function renderBoxes(running) {
  const R = JRES[JSTYLE]; if (!R) return; const B = boxesOf(R.verdicts), n = Object.keys(R.verdicts).length, L = TEACH.labelled;
  const counts = Object.fromEntries(Object.entries(B.boxes).map(([k, v]) => [k, v.length]));
  $("#jrboxes").innerHTML = `<div class="ph"><h3>${E(JNAME[JSTYLE][0].toUpperCase() + JNAME[JSTYLE].slice(1))} against the person</h3><span class="sp"></span><span class="muted small">${running ? '<span class="spin"></span> ' : ""}${n} of ${L.length} verdicts${R.usd != null ? " · " + usd(R.usd) : ""}</span></div>
    <div class="pb">${boxGrid(counts, L.filter(x => x.label).length, L.filter(x => !x.label).length)}<p class="boxline">${running ? "" : "<b>" + E(B.line) + "</b> Click a box to read the judge's reasons."}</p><div class="inbox" id="inbox"></div></div>`;
  $$("#jrboxes .box").forEach(el => el.onclick = () => { JBOX = el.dataset.b; renderBoxes(running); });
  if (JBOX) $("#inbox").innerHTML = (B.boxes[JBOX] || []).map(it => { const x = L.find(y => y.id === it.id); return `<div class="it"><span class="pill ${x.label ? "good" : "bad"} xs">${x.label ? "right" : "wrong"}</span><b>${E(x.user)}</b><span></span><span><span class="muted">${E(x.note)}.</span> The judge: ${E(it.reason)}</span></div>`; }).join("") || `<p class="small muted">No reply landed in this box.</p>`;
  renderLabelled();
}
async function runLabelled(style, btn) {
  JSTYLE = style; JBOX = null; JRES[style] = {verdicts: {}}; busy(btn, true, "Judging 12 replies"); renderBoxes(true);
  try {
    const j = await api("/api/teach/labelled", {judge: style});
    const r = await poll(j.id, evs => { for (const ev of evs) if (ev.kind === "verdict") JRES[style].verdicts[ev.id] = {pass: ev.pass, reason: ev.reason}; renderBoxes(true); }, 600);
    JRES[style] = {verdicts: r.result.verdicts, usd: r.result.usd}; await refreshMe(); renderBoxes(false);
  } catch (x) { toast(x.message); $("#jrboxes").innerHTML = `<div class="empty">${E(x.message)}</div>`; }
  finally { busy(btn, false); }
}
function renderJ56() {
  const R = TEACH && TEACH.recorded56; if (!R) { $("#jr56").innerHTML = `<div class="empty">Not recorded in this copy.</div>`; return; }
  $("#jr56").innerHTML = `<div class="j56">${["naive", "specific", "grounded"].map(k => `<div><h4>${E(JNAME[k][0].toUpperCase() + JNAME[k].slice(1))}</h4>${boxGrid(R.judges[k].counts, R.judges[k].right, R.judges[k].wrong, true)}<p>${E(R.judges[k].line)}</p></div>`).join("")}</div>
    <p class="tiny muted" style="margin-top:10px">The same model each time (Claude Haiku); only what it is asked and what it is shown changes. Recorded ${E(R.at)}: ${E(R.source)}.</p>`;
}

/* ---- the same checks in DeepEval (the shape of NB6b's section 5: three things you set) */
let DECASE = null;
const toolsText = xs => (xs || []).map(t => t.name + (t.input_parameters && Object.keys(t.input_parameters).length ? "(" + Object.entries(t.input_parameters).map(([k, v]) => k + "=" + v).join(", ") + ")" : "")).join(", ");
function toolsOf(text) {   /* "create_purchase_request(confirm=false), check_budget" -> [{name, input_parameters}] */
  return (String(text || "").match(/[\w.]+(\([^)]*\))?/g) || []).map(x => { const m = x.match(/^([\w.]+)(?:\(([^)]*)\))?$/), ip = {};
    (m[2] || "").split(",").map(y => y.trim()).filter(Boolean).forEach(kv => { const [k, v] = kv.split("=").map(z => z.trim()); if (k && v !== undefined) ip[k] = /^true$/i.test(v) ? true : /^false$/i.test(v) ? false : isNaN(Number(v)) ? v : Number(v); });
    return {name: m[1], input_parameters: ip}; });
}
const pyTools = xs => xs.map(t => `ToolCall(name=${JSON.stringify(t.name)}${Object.keys(t.input_parameters).length ? ", input_parameters={" + Object.entries(t.input_parameters).map(([k, v]) => JSON.stringify(k) + ": " + (v === true ? "True" : v === false ? "False" : JSON.stringify(v))).join(", ") + "}" : ""})`).join(", ");
function deInit() {
  $("#deturn").innerHTML = ((TEACH && TEACH.turns) || []).map(t => `<option value="${E(t.id)}">filled in from: ${E(t.label)}</option>`).join("") + `<option value="mine">filled in from: my last chat turn</option>`;
  $("#deturn").value = (TEACH.turns || []).some(t => t.id === "good1") ? "good1" : "mine";
  $("#deturn").onchange = () => deFill($("#deturn").value);
  $$("#demetric button").forEach(b => b.onclick = () => deMetric(b.dataset.m));
  ["dein", "deout", "decalled", "deexp", "dethr"].forEach(id => $("#" + id).addEventListener("input", deCode));
  deFill($("#deturn").value);
}
async function deFill(id) {
  try { DECASE = await api("/api/teach/case/" + id); $("#dein").value = DECASE.input; $("#deout").value = DECASE.actual_output; $("#decalled").value = toolsText(DECASE.tools_called); $("#deexp").value = toolsText(DECASE.expected_tools); }
  catch (x) { toast(x.message); DECASE = DECASE || {context: [], geval: {name: "My criterion", criterion: ""}}; }
  $("#deres").innerHTML = `<div class="empty">The score, pass or fail, and DeepEval's reason appear here.</div>`;
  deMetric(DEM, true);
}
function deMetric(m, fresh) {
  DEM = m; $$("#demetric button").forEach(b => b.classList.toggle("on", b.dataset.m === m));
  const g = (DECASE && DECASE.geval) || {name: "My criterion", criterion: ""}, n = ((DECASE && DECASE.context) || []).length;
  const keep = fresh ? {} : {name: $("#dename") && $("#dename").value, crit: $("#decrit") && $("#decrit").value};
  $("#dembody").innerHTML = m === "tool" ? `<p class="ink2" style="font-size:14.5px;line-height:1.5"><b>ToolCorrectnessMetric</b> compares the tools that were called with the tools you expect. It is plain comparison: no model is asked. Two switches are yours:</p>
       <div class="knob"><div class="n" style="font-size:14px">Compare the arguments too<small>here: <code>confirm</code>. Off: only the tools' names are compared.</small></div><button class="switch on" id="deargs" aria-label="Compare the arguments too"></button></div>
       <div class="knob"><div class="n" style="font-size:14px">Exact match<small>the calls must be exactly the expected ones, nothing extra. Off: “at least these”.</small></div><button class="switch on" id="deexact" aria-label="Exact match"></button></div>`
    : `<p class="ink2" style="font-size:14.5px;line-height:1.5"><b>GEval</b> is a judge that DeepEval builds from one sentence of yours. It reads Emma's message and the reply, and answers with a score from 0 to 1 and a reason.</p>
       <label class="label" for="dename">name · what you call this check</label><input class="input" id="dename" value="${E(keep.name || g.name)}">
       <label class="label" for="decrit">criteria · one sentence about what a good reply says</label><textarea class="input" id="decrit" rows="4">${E(keep.crit || g.criterion)}</textarea>
       <div class="row small ink2"><span>model</span><span class="pill line">claude-haiku-5-5</span></div>
       <div class="knob"><div class="n" style="font-size:14px">Also give it the turn's tool results<small>DeepEval calls this the <code>context</code> (${n} result${n === 1 ? "" : "s"} in this turn). Off, as in NB6b: it reads only the words.</small></div><button class="switch" id="dectx" aria-label="Give GEval the tool results as context"></button></div>`;
  $("#dethr").value = m === "tool" ? "1" : "0.5";
  $("#dethrline").textContent = m === "tool" ? "Pass when the score reaches 1. For tool calls there is no “nearly right”." : "Pass when the score reaches 0.5. A judge's score is a matter of degree; you draw the line.";
  $("#decost").textContent = m === "tool" ? "No model call, so it costs nothing. The library takes a few seconds to start." : "A few calls to Claude Haiku: under US$0.001 from your daily budget, about 10 seconds.";
  $$("#dembody .switch").forEach(sw => sw.onclick = e => { e.currentTarget.classList.toggle("on"); deCode(); });
  if (m === "geval") { $("#dename").addEventListener("input", deCode); $("#decrit").addEventListener("input", deCode); }
  deCode();
}
const swOn = id => !!($("#" + id) && $("#" + id).classList.contains("on"));
function deCode() {   /* the same thing as Python: NB6b's cells, from the form's values */
  const S = JSON.stringify, thr = Number($("#dethr").value || 0), g = DEM === "geval", ctx = g && swOn("dectx");
  const py3 = t => '"""' + String(t).replace(/\\/g, "\\\\").replace(/"""/g, '\\"\\"\\"') + '"""';
  $("#decode").textContent = `from deepeval.metrics import ${g ? "GEval" : "ToolCorrectnessMetric"}
from deepeval.models import AnthropicModel
from deepeval.test_case import LLMTestCase, ToolCall, ${g ? "SingleTurnParams" : "ToolCallParams"}

claude = AnthropicModel(model="claude-haiku-5-5")

reply = ${py3($("#deout").value)}

# 1 · the test case
case = LLMTestCase(
    input=${S($("#dein").value)},        # what Emma typed
    actual_output=reply,                 # what the assistant answered
    # what it did:
    tools_called=[${pyTools(toolsOf($("#decalled").value))}],
    # YOU SET THIS: what it should have done
    expected_tools=[${pyTools(toolsOf($("#deexp").value))}],${ctx ? "\n    # the tool results of this turn, a list of strings\n    context=context," : ""}
)

# 2 · the metric, with 3 · the threshold
${g ? `metric = GEval(
    name=${S($("#dename").value)},                 # YOU SET THIS: a name
    # YOU SET THIS: one sentence
    criteria=${S($("#decrit").value)},
    model=claude, threshold=${thr}, async_mode=False,
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT${ctx ? ", SingleTurnParams.CONTEXT" : ""}],
)`
  : `metric = ToolCorrectnessMetric(
    model=claude, threshold=${thr},${swOn("deargs") ? "\n    evaluation_params=[ToolCallParams.INPUT_PARAMETERS],     # YOU SET THIS: compare the arguments too" : ""}
    should_exact_match=${swOn("deexact") ? "True,                                 # YOU SET THIS: nothing extra allowed" : "False,                                # the library's default: at least the expected calls"}
)`}

metric.measure(case)                     # this one line is "the eval"
print(metric.score, metric.is_successful(), metric.reason)`;
}
$("#decopy").onclick = () => navigator.clipboard.writeText($("#decode").textContent).then(() => toast("Copied."));
$("#derun").onclick = async e => {
  const btn = e.currentTarget; busy(btn, true, "DeepEval is running");
  $("#deres").innerHTML = `<div class="pb row"><span class="spin"></span><b>Running the real library</b><span class="muted small">${DEM === "tool" ? "comparing the two lists" : "its judge is reading the reply"}</span></div>`;
  try {
    const body = {turn: $("#deturn").value, metric: DEM, threshold: Number($("#dethr").value),
      case: {input: $("#dein").value, actual_output: $("#deout").value, tools_called: toolsOf($("#decalled").value), expected_tools: toolsOf($("#deexp").value)},
      ...(DEM === "geval" ? {name: $("#dename").value, criterion: $("#decrit").value, context: swOn("dectx")} : {args: swOn("deargs"), exact: swOn("deexact")})};
    const j = await api("/api/deepeval/run", body); const r = (await poll(j.id, null, 900)).result; await refreshMe(); renderDe(r);
  } catch (x) { toast(x.message); $("#deres").innerHTML = `<div class="empty">${E(x.message)}</div>`; }
  finally { busy(btn, false); }
};
const deFail = r => `<div class="pb"><div class="c4why no"><b>DeepEval did not give a result.</b> ${E(r.error || "It stopped without an answer.")}</div><p class="tiny muted" style="margin-top:8px">The rest of Argus is not affected. Press Run again; a small judge model sometimes breaks the answer format DeepEval asks for.</p></div>`;
function renderDe(r) {
  const m = (r.results || [])[0];
  if (!r.ok || !m || m.error) { $("#deres").innerHTML = deFail(m && m.error ? {error: `Its judge broke the answer format ${m.attempts} times (${m.error}).`} : r); return; }
  const tool = r.metric === "tool", c = r.case || {};
  $("#deres").innerHTML = `<div class="pb vd ${m.passed ? "ok" : "no"}"><span class="label">${E(m.name)}</span><div class="score"><b>${Number(m.score).toFixed(2)}</b>${VP(m.passed)}<span class="small ink2">${m.passed ? "the score reaches" : "the score is under"} the threshold of ${m.threshold}</span></div>
    ${tool ? `<div class="c4r wide" style="margin-top:12px"><span>called</span><span class="mono">${E(toolsText(c.tools_called) || "nothing")}</span><span>expected</span><span class="mono">${E(toolsText(c.expected_tools))}</span></div>` : ""}
    <span class="label" style="margin-top:12px">DeepEval's reason</span><div class="dereason">${E(m.reason)}</div>
    ${tool ? `<p class="tiny muted" style="margin-top:8px">The reason lists tool names only. ${r.args ? "The arguments were compared too: when the names are the same, look at <code>confirm</code> in the two lines above." : "Only the names were compared."} “Tool Selection” is a further check that is not switched on: it needs the list of every tool the assistant could have chosen from.</p>` : ""}
    <p class="tiny muted" style="margin-top:8px">DeepEval ${E(r.deepeval || "")} · ${r.seconds} s · ${usd(r.usd)}${m.attempts > 1 ? " · it took " + m.attempts + " tries: the judge broke DeepEval's answer format first" : ""}${!tool ? " · it read Emma's message and the reply" + (r.context_items ? " and " + r.context_items + " tool result" + (r.context_items === 1 ? "" : "s") : "") : ""}</p></div>`;
}

/* ---- Conversations: score with DeepEval */
const CV_CRIT = "The assistant showed Emma a preview and saved a request only after she agreed to that preview.";
function cvdeRows(d, r) {
  if (!d.ok) return deFail(d).replace('<div class="pb">', "<div>");
  const ours = ((r && r.checks) || []).map(c => `<span class="pill ${c.pass ? "good" : "bad"} xs">${c.kind === "words" ? "judge" : "code"} · ${E(c.name)}: ${c.pass ? "pass" : "fail"}</span>`).join("");
  return `<div class="dems">${(d.results || []).map(m => m.error ? `<div class="dem"><b>${E(m.name)}</b><span class="pill slate xs">no result</span><span></span><p>Its judge broke the answer format DeepEval asks for ${m.attempts} times. Run it again.</p></div>`
    : `<div class="dem"><b>${E(m.name)}</b><span class="sc">${Number(m.score).toFixed(2)}</span><span class="pill ${m.passed ? "good" : "bad"}">${m.passed ? "pass" : "fail"}</span><p>${E(m.reason)}</p></div>`).join("")}</div>
    <div class="ours"><b>Our five checks on the same conversation:</b>${ours}</div>
    <p class="small ink2" style="margin-top:8px"><b>What each side read.</b> DeepEval's three judges read the words of the conversation. Of our five checks, three are code that read Ledgerline and the tool calls, and two are our own judge.</p>
    <p class="tiny muted">DeepEval ${E(d.deepeval || "")} · threshold ${d.threshold} · ${d.seconds} s · ${usd(d.usd)}</p>`;
}
function renderCvde(r) {
  CVCUR = r; const el = $("#cvde");
  const show = !!(r && !r.error && (r.turns || []).length); el.classList.toggle("hide", !show); $(".cv-grid").classList.toggle("hasde", show);
  if (!show) return;
  el.innerHTML = `<div class="ph"><h3>Score with DeepEval</h3><span class="muted small">the same conversation, scored by the real library · its judges are Claude Haiku</span></div>
    <div class="pb col"><div class="cvde-set">
      <p class="small ink2"><b>1 · The test case.</b> DeepEval's <code>ConversationalTestCase</code>: the ${2 * r.turns.length} messages in order, the scenario (“${E(r.goal)}”) and the expected outcome (“${E(r.expect)}”).</p>
      <div class="col" style="gap:6px"><p class="small ink2"><b>2 · The metrics.</b> Knowledge retention (did it forget something Emma said?), conversation completeness (did Emma get what she wanted?), and one criterion of your own:</p>
        <textarea class="input" id="cvcrit" rows="3" aria-label="Your criterion">${E((r.deepeval && r.deepeval.criterion) || CV_CRIT)}</textarea></div>
      <div class="col" style="gap:8px"><p class="small ink2"><b>3 · The threshold.</b> 0.5 for each: a score at or above it passes.</p>
        <button class="btn primary" id="cvderun">Score with DeepEval</button><span class="tiny muted">under US$0.01 from your daily budget · 20 to 40 seconds</span></div></div>
    <div id="cvderes">${r.deepeval ? cvdeRows(r.deepeval, r) : '<div class="empty">Three scores from 0 to 1, pass or fail, and a reason each appear here.</div>'}</div></div>`;
  $("#cvderun").onclick = async e => {
    const btn = e.currentTarget; busy(btn, true, "DeepEval's judges are reading");
    try { const j = await api("/api/convo/deepeval", {at: r.at, criterion: $("#cvcrit").value, name: "Asked before saving"}); const d = (await poll(j.id, null, 1200)).result;
      r.deepeval = d; await refreshMe(); $("#cvderes").innerHTML = cvdeRows(d, r); renderMyConvos(); }
    catch (x) { toast(x.message); } finally { busy(btn, false); }
  };
}

/* ---- Traces: write the score on this trace */
function scoreUI(t) {
  const el = $("#scoreline"), on = t && t.trace_id && TEACH && (TEACH.scores || []).length;
  if (on) $("#tlinks").insertAdjacentHTML("afterbegin", `<button class="btn xs primary" id="scorebtn" title="Runs the code check “saved without a yes?” on this turn and writes the verdict onto the trace">Write the score on this trace</button>`);
  const s = on ? SCORES[t.trace_id] : null;
  if (!s) { el.classList.add("hide"); } else { el.classList.remove("hide");
    el.innerHTML = `<b>${Object.values(s.wrote).some(w => w.ok) ? "Written on this trace." : "Not written."}</b> ${E(s.line)}<span class="rule">The code check, no model: ${E(s.check.rule)} On this turn: ${E(s.check.why)}. Open the trace with the buttons above: the score is on it.</span>`; }
  if (on) $("#scorebtn").onclick = async e => {
    const btn = e.currentTarget; busy(btn, true, "Writing");
    try { const j = await api("/api/trace/score", {trace_id: t.trace_id}); SCORES[t.trace_id] = (await poll(j.id)).result; }
    catch (x) { toast(x.message); } finally { busy(btn, false); scoreUI2(t); }
  };
}
function scoreUI2(t) { const b = $("#scorebtn"); if (b) b.remove(); scoreUI(t); }

boot().catch(e => toast("Could not reach Argus: " + e.message));
