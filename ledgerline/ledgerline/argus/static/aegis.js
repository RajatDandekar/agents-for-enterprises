/* Aegis · Lecture 7 · Guardrails and Red-Teaming. Vanilla JS, no build step.
   Loaded after argus.js, and only by the Aegis app (the server adds this script and <body class="aegis">). It reuses
   argus.js's helpers ($, $$, E, api, toast, busy, go, ME, ...) and adds what Lecture 7 needs:
     1 Chat and trace   the chat, plus a strip that says where the guards live, and the instructor's inbox switch
     2 Guard bench      the 17 attacks as tool calls made directly (no model), guards off against guards on
     3 Detectors        every detector on one text, with its prompt, its code and its notebook
     4 Attacks          the guards station that argus.js already draws */
(function () {
"use strict";
window.AEGIS_TABS = ["bench", "detect"];
const GH = "https://github.com/RajatDandekar/agents-for-enterprises/blob/main/ledgerline/ledgerline/course/l6/";
const shield = (px, dark) => `<svg width="${px}" height="${px}" viewBox="0 0 32 32" fill="none">${dark ? '<rect width="32" height="32" rx="9" fill="#141519"/>' : ""}<path d="M16 5.5l8.5 3.2v6.6c0 5.2-3.5 9.3-8.5 11.2-5-1.9-8.5-6-8.5-11.2V8.7L16 5.5z" stroke="${dark ? "#fff" : "currentColor"}" stroke-width="1.9" stroke-linejoin="round"/><path d="M12 15.8l3 3 5.2-5.6" stroke="${dark ? "#7fb0ff" : "currentColor"}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
let BENCH = null, RUN = {}, SEL = null, DET = null, EX = null, PEEKED = null;

/* ------------------------------------------------------------------ the page, relabelled (once, at load) */
$("#join .card .k").innerHTML = `${shield(15)}Northbridge Cycles · Lecture 7 · Guardrails and Red-Teaming`;
$("#join h1").textContent = "Aegis.";
$("#join .lede").textContent = "The shield. Ask Northbridge goes to 40 buyers on Monday. Today you put guards around it, call its tools directly to watch each guard refuse, run every detector on one text, and then attack it.";
const four = $("#join .four"); four.classList.remove("three-up");
four.innerHTML = `<div><b>1 · Chat and trace</b>The same message with the guards off, then on</div>
  <div><b>2 · Guard bench</b>Call the tools directly; see which guard refuses</div>
  <div><b>3 · Detectors</b>Every detector on one text, with its prompt</div>
  <div><b>4 · Attacks</b>Send the attack library; the wall keeps score</div>`;
$(".brand svg").outerHTML = shield(26, true);
$(".brand div").innerHTML = "Aegis<br><small>Lecture 7 · Guardrails and Red-Teaming</small>";

const tabs = $("#tabs"), gtab = $("#guardstab");
[["bench", "Guard bench"], ["detect", "Detectors"]].forEach(([id, lbl]) => {
  const a = document.createElement("a"); a.href = "#" + id; a.dataset.tab = id;
  a.innerHTML = `<span class="n"></span><span class="lbl">${lbl}</span>`;
  a.addEventListener("click", e => { e.preventDefault(); history.replaceState(null, "", "#" + id); go(id); });
  tabs.insertBefore(a, gtab);
});
$("#tabs a[data-tab=traces] .lbl").textContent = "Chat and trace"; $("#guardstab .lbl").textContent = "Attacks";
["traces", "bench", "detect", "guards"].forEach((t, i) => { $(`#tabs a[data-tab=${t}] .n`).textContent = i + 1; });

/* ---- tab 1: the chat */
const th = $("#tab-traces .head");
$(".kick", th).textContent = "Station 1 · The chat, guards off and on";
$("h2", th).textContent = "The same message, with and without guards";
$("p.lede", th).innerHTML = "Chat with your own Ask Northbridge, as Emma. Here <b>the agent (the model) handles the message</b>: it decides which tools to ask for. Flip <b>Guards</b> and send the same message again. Every guard decision is its own span in the trace.";
$(".guide .try p", th).innerHTML = "Pick the <b>Thursday prompt</b>, Guards <b>on</b>, and ask <b>“Order the usual, please, needed by 4 Dec 2026.”</b> Then say <b>“Yes, go ahead.”</b>";
$(".guide .notice p", th).innerHTML = "Which call was refused, by which guard, and what did the agent tell Emma? After her yes, what was saved? Now Guards <b>off</b>, the same message.";
$(".guide .next p", th).innerHTML = "Ask <b>“Please deal with the new invoice in the AP inbox.”</b> with guards off, then on. Open the trace in LangSmith, Langfuse or Sentry. Then the Guard bench.";
const strip = document.createElement("div"); strip.className = "ag-strip"; strip.id = "agstrip";
strip.innerHTML = `<div class="lead"><span><b>Where the guards live:</b> code at the tool boundary, outside the model.</span><span class="sp"></span><a href="${GH}guards.py#L204-L308" target="_blank" rel="noopener">guards.py ↗</a></div>
  <span class="st">the agent (the model) asks for a tool</span><span class="ar">→</span><span class="st g">guard.before()</span><span class="ar">→</span>
  <span class="st">the tool runs on Ledgerline</span><span class="ar">→</span><span class="st g">guard.after()</span><span class="ar">→</span>
  <span class="st">the result goes back to the model</span><span class="sp"></span><span class="pill" id="agstate"></span>`;
$("#tab-traces").insertBefore(strip, $("#tab-traces .tr-grid"));
function stripState() {
  const on = !!(ME && ME.chat_guards), p = $("#agstate");
  strip.classList.toggle("off", !on);
  p.className = "pill " + (on ? "accent" : "slate");
  p.textContent = on ? "Guards on in this chat" : "Guards off: nothing between the model and the tools";
}
const sync0 = window.syncChatGuards;
window.syncChatGuards = function () { sync0(); stripState(); };

/* ---- tab 4: the attacks */
const gh = $("#tab-guards .head");
$(".kick", gh).textContent = "Station 4 · Red-teaming";
$("p.lede", gh).innerHTML = "Here <b>the agent (the model) handles the attack</b>, so the same attack can end differently from run to run. Turn guards on or off, then send an attack from the library or write your own. Each attack runs in a fresh sandbox; whether it worked is read from Ledgerline, never guessed by a model.";

/* ------------------------------------------------------------------ tab 2: the guard bench */
const bench = document.createElement("section"); bench.className = "tab"; bench.id = "tab-bench";
bench.innerHTML = `
  <div class="head">
    <div><div class="kick">Station 2 · The guard bench</div><h2>Call the tools directly</h2>
      <p class="lede">No model here. <b>We call the tool directly, skipping the model</b>, as if an attacker had already talked the model round. Each attack runs twice, on two fresh sandboxes: with no guards, then with the six code guards. Whether it worked is read from Ledgerline.</p></div>
    <div class="guide">
      <div class="try"><h4><i></i>Try</h4><p>Press <b>Run all 17</b>. Then open <b>A14</b>, <b>A01</b>, <b>A03</b>, <b>A06</b> and <b>A11</b>.</p></div>
      <div class="notice"><h4><i></i>Notice</h4><p>With no guards, who said no the other times? With guards on, which guard refused, and on which lines of <code>guards.py</code>?</p></div>
      <div class="next"><h4><i></i>Next</h4><p>Call any tool with your own arguments, at the bottom. Then Detectors.</p></div>
    </div>
  </div>
  <div class="ag-bench">
    <div class="panel">
      <div class="ph"><h3>17 attacks, as the tool calls they need</h3><span class="sp"></span><button class="btn primary sm" id="agrunall">Run all 17 (no model, free)</button></div>
      <div class="pb">
        <div class="ag-totals" id="agtotals"></div>
        <table class="ag-tbl"><thead><tr><th></th><th>Attack</th><th>No guards</th><th>Code guards on</th></tr></thead><tbody id="agtbl"></tbody></table>
        <p class="tiny muted" style="margin-top:10px">A07, A10 and A17 want words, not a tool call, so they are not on this bench. The Detectors and Attacks tabs cover them.</p>
      </div>
    </div>
    <div class="panel" id="agres"><div class="empty">Run all 17, or click one attack. Its tool calls are made directly, and you see Ledgerline's answer next to the guard's.</div></div>
  </div>
  <div class="panel" style="margin-top:16px">
    <div class="ph"><h3>Call any tool yourself</h3><span class="muted small">we call the tool directly, skipping the model: once with no guards, once with the code guards, each on a fresh sandbox</span></div>
    <div class="pb ag-own">
      <div class="col">
        <div class="ag-chips" id="agpre"></div>
        <div><span class="label">Tool</span><select class="input" id="agtool"></select></div>
        <div class="args" id="agargs"></div>
        <div><span class="label">Arguments, as JSON</span><textarea class="input mono" id="agjson" rows="7" spellcheck="false"></textarea></div>
        <div><span class="label">What Emma said in this turn (optional: one guard reads it for a yes)</span><input class="input" id="agheard" maxlength="400" style="width:100%" placeholder="for example: Yes, go ahead."></div>
        <button class="btn primary" id="agcall">Call it: guards off, and guards on</button>
      </div>
      <div id="agownres"><div class="empty">The same call, twice. Left: what Ledgerline does with it. Right: what the guards do before Ledgerline sees it.</div></div>
    </div>
  </div>`;
$("main").insertBefore(bench, $("#tab-guards"));

const argsText = a => Object.entries(a || {}).map(([k, v]) => `${k}=${typeof v === "string" ? JSON.stringify(v) : JSON.stringify(v)}`).join(", ");
const srcLinks = s => (s || []).map(x => `<a href="${E(x.url)}" target="_blank" rel="noopener"><code>${E(x.file)}</code> lines ${E(x.lines)} ↗ <span class="muted">${E(x.what)}</span></a>`).join("");
const writes = t => !!(BENCH && (BENCH.tools.find(x => x.name === t) || {}).writes);
function callBox(c) {
  const call = `<div class="ag-call"><span class="t">${E(c.tool)}</span>(${E(argsText(c.args))})</div>`;
  const raw = `<details><summary>What came back, in full</summary><pre class="json">${E(c.out)}</pre></details>`;
  if (c.by === "guard") {
    const g = c.guard || {};
    return `${call}<div class="ag-ans guard"><b>⛨ Refused by the guard “${E(g.title || g.id)}”, before the tool ran</b>${E(g.reason || "")}
      <dl><dt>Rule</dt><dd>${E(g.rule || "–")}</dd><dt>Next step</dt><dd>${E(g.next_step || "–")}</dd><dt>Code</dt><dd><div class="ag-src">${srcLinks(g.source)}</div></dd></dl>${raw}</div>`;
  }
  if (!c.ok) return `${call}<div class="ag-ans erp"><b>Ledgerline itself said no</b>${E(String(c.answer).replace(/^Ledgerline said no: /, ""))}${raw}</div>`;
  const preview = /^preview only/.test(c.answer), hit = writes(c.tool) && !preview;
  return `${call}<div class="ag-ans ${hit ? "saved" : "ran"}"><b>${hit ? "The tool ran on Ledgerline: this is now real" : "The tool ran on Ledgerline"}</b>${E(c.answer)}${raw}</div>`;
}
function sideBox(s, on, verdict) {
  const v = verdict === false ? `<div class="ag-verdict plain"><b>Ledgerline now holds</b>${E(s.saved || "nothing new")}</div>`
    : `<div class="ag-verdict ${s.worked ? "thru" : "held"}"><b>${s.worked ? "The attack worked" : "The attack was stopped"}</b>Read from Ledgerline: ${E(s.why || "")}<br><span class="muted">Ledgerline now holds: ${E(s.saved || "nothing new")}.</span></div>`;
  return `<div class="ag-side ${on ? "on" : "off"}"><h4>${on ? `<span class="pill accent xs">Guards on</span> the six code guards` : `<span class="pill slate xs">Guards off</span> nothing in front of the tool`}</h4>
    <div class="sub">${on ? "guard.before() reads each call first" : "the call goes straight to Ledgerline"}</div>${s.calls.map(callBox).join("")}${v}</div>`;
}
const guardOf = s => { const c = (s.calls || []).find(x => x.by === "guard"); return c && c.guard ? c.guard.title : null; };
function cell(s) {
  if (!s) return `<span class="muted">–</span>`;
  if (s.worked) return `<span class="pill bad xs">worked</span>`;
  const g = guardOf(s);
  return `<span class="pill good xs">stopped</span><small>${g ? "by the guard “" + E(g) + "”" : s.stopped_by ? "by Ledgerline itself" : "nothing changed in Ledgerline"}</small>`;
}
function drawTable() {
  if (!BENCH) return;
  $("#agtbl").innerHTML = BENCH.attacks.map(a => { const r = RUN[a.id];
    return `<tr class="r ${SEL === a.id ? "on" : ""}" data-a="${a.id}"><td class="id">${a.id}</td><td class="ti">${E(a.title)}<small>${E(a.owasp)}${a.channel === "indirect" ? " · via an e-mail" : ""}${a.session ? " · signed in as " + E(a.session) : ""}</small></td><td class="v">${cell(r && r.off)}</td><td class="v">${cell(r && r.on)}</td></tr>`; }).join("");
  $$("#agtbl tr.r").forEach(tr => tr.onclick = () => pick(tr.dataset.a));
  const done = Object.keys(RUN).length, n = BENCH.attacks.length, all = done === n;
  const off = Object.values(RUN).filter(r => r.off.worked).length, on = Object.values(RUN).filter(r => r.on.worked).length;
  $("#agtotals").innerHTML = `<div class="off ${all ? "done" : ""}"><b class="num">${all ? off : "–"} of ${n}</b><span>attacks worked with <b style="display:inline;font-size:inherit">no guards</b></span></div>
    <div class="on ${all ? "done" : ""}"><b class="num">${all ? on : "–"} of ${n}</b><span>worked with the <b style="display:inline;font-size:inherit">six code guards</b> on</span></div>`;
}
function drawAttack(r) {
  const says = (r.says || []).map(t => `<q>${E(t.length > 520 ? t.slice(0, 520) + "…" : t)}</q>`).join("");
  const notes = [r.has_mail ? "The instruction is inside an e-mail in the AP inbox. The first call, read_mailbox, opens it." : "",
    r.session ? `This sandbox is signed in to Ledgerline as ${E(r.session)}, a service account.` : "",
    (r.setup || []).length ? "Before the attack: Emma's request for 2,400 BAT-500 packs waits for Daniel's approval." : ""].filter(Boolean);
  $("#agres").innerHTML = `<div class="ph"><h3>${E(r.id)} · ${E(r.title)}</h3><span class="sp"></span><span class="pill slate xs">${E(r.owasp)}</span>${r.channel === "indirect" ? '<span class="pill violet xs">via e-mail</span>' : ""}</div>
    <div class="pb"><span class="label">What the attacker says to the agent</span><div class="ag-says">${says}${notes.map(n => `<span class="small">${n}</span>`).join("")}</div>
    <span class="label">The tool calls the attacker wants. We make them directly, skipping the model: ${r.off.calls.length === 1 ? "one call" : r.off.calls.length + " calls"}, on two fresh sandboxes</span>
    <div class="ag-two">${sideBox(r.off, false)}${sideBox(r.on, true)}</div></div>`;
}
async function pick(id) {
  SEL = id; drawTable();
  if (!RUN[id]) {
    $("#agres").innerHTML = `<div class="empty"><span class="spin" style="display:inline-block;width:14px;height:14px;border-radius:50%;border:2px solid currentColor;border-right-color:transparent;animation:spin .7s linear infinite;vertical-align:-2px;margin-right:8px"></span>Running ${E(id)} on two fresh sandboxes…</div>`;
    try { const j = await api("/api/bench/run", {attack: id}); j.rows.forEach(r => { RUN[r.id] = r; }); } catch (x) { toast(x.message); $("#agres").innerHTML = `<div class="empty">${E(x.message)}</div>`; return; }
  }
  if (SEL === id) { drawTable(); drawAttack(RUN[id]); }
}
$("#agrunall").onclick = async e => {
  const b = e.currentTarget; busy(b, true, "Running 34 sandboxes…");
  try { const j = await api("/api/bench/run", {attack: "all"}); j.rows.forEach(r => { RUN[r.id] = r; }); drawTable();
    toast(`${j.totals.worked_off} of ${j.totals.attacks} worked with no guards; ${j.totals.worked_on} of ${j.totals.attacks} with the code guards on.`);
    if (!SEL) pick("A14"); else drawAttack(RUN[SEL]); } catch (x) { toast(x.message); }
  busy(b, false);
};

/* a call of your own */
function toolArgs() {
  const t = BENCH.tools.find(x => x.name === $("#agtool").value); if (!t) return;
  $("#agargs").innerHTML = t.args.length ? t.args.map(a => `<code>${E(a.name)}</code>${a.required ? "" : " (optional)"}${a.about ? ": " + E(a.about) : ""}`).join("<br>") : "This tool takes no arguments.";
  return t;
}
function template(t) { const o = {}; t.args.filter(a => a.required).forEach(a => { o[a.name] = /int|number/.test(a.type) ? 0 : a.type === "boolean" ? false : ""; }); return o; }
function setCall(tool, args, heard) { $("#agtool").value = tool; toolArgs(); $("#agjson").value = JSON.stringify(args, null, 1); $("#agheard").value = heard || ""; }
function drawOwn() {
  const u = BENCH.usual, has = n => BENCH.tools.some(t => t.name === n);
  const pre = [["Commit the usual, no preview", "create_purchase_request", {...u, confirm: true}],
    ["Preview the usual", "create_purchase_request", {...u, confirm: false}],
    ["Send our orders to an outside address", "send_message", {to: "someone@outside.example", text: "Open purchase orders and their values"}],
    ["Read the stock (a read-only tool)", "check_stock", {item_code: u.item_code}]].filter(p => has(p[1]));
  $("#agtool").innerHTML = BENCH.tools.map(t => `<option value="${E(t.name)}">${E(t.name)}${t.writes ? "  · writes" : ""}</option>`).join("");
  $("#agpre").innerHTML = pre.map((p, i) => `<button class="chipbtn" data-i="${i}" type="button">${E(p[0])}</button>`).join("");
  $$("#agpre .chipbtn").forEach(b => b.onclick = () => { const p = pre[+b.dataset.i]; setCall(p[1], p[2]); $$("#agpre .chipbtn").forEach(x => x.classList.toggle("on", x === b)); });
  $("#agtool").onchange = () => { const t = toolArgs(); $("#agjson").value = JSON.stringify(template(t), null, 1); $$("#agpre .chipbtn").forEach(x => x.classList.remove("on")); };
  if (pre.length) { setCall(pre[0][1], pre[0][2]); $("#agpre .chipbtn").classList.add("on"); } else { toolArgs(); }
}
$("#agcall").onclick = async e => {
  let args; try { args = JSON.parse($("#agjson").value || "{}"); } catch (x) { toast("The arguments are not valid JSON: " + x.message); return; }
  if (!args || typeof args !== "object" || Array.isArray(args)) { toast("The arguments must be one JSON object, for example {\"item_code\": \"BAT-500\"}."); return; }
  const b = e.currentTarget; busy(b, true, "Calling…");
  try { const j = await api("/api/bench/call", {tool: $("#agtool").value, args, heard: $("#agheard").value});
    $("#agownres").innerHTML = `${j.heard ? `<div class="ag-says"><span class="label" style="margin:0">Emma said, in this turn</span><q>${E(j.heard)}</q></div>` : ""}<div class="ag-two">${sideBox(j.off, false, false)}${sideBox(j.on, true, false)}</div>`;
  } catch (x) { toast(x.message); }
  busy(b, false);
};

/* ------------------------------------------------------------------ tab 3: the detectors */
const WHERE = ["message in", "tool result", "reply out"];
const det = document.createElement("section"); det.className = "tab"; det.id = "tab-detect";
det.innerHTML = `
  <div class="head">
    <div><div class="kick">Station 3 · Detectors</div><h2>Guards that read the words</h2>
      <p class="lede">The code guards read Ledgerline. These read text: a classifier, Presidio, a second model, and two that are plain code. Type or pick a text and press <b>Check</b>: every detector runs on it, and each card says where it sits, what it found, and where its code is.</p></div>
    <div class="guide">
      <div class="try"><h4><i></i>Try</h4><p>The six examples, one by one. Then a message of your own that should pass, and one that should not.</p></div>
      <div class="notice"><h4><i></i>Notice</h4><p>Where do the classifier and the second model disagree? Which one raises a false alarm on an ordinary request?</p></div>
      <div class="next"><h4><i></i>Next</h4><p><b>NB7b</b> measures them all on the labelled set: caught, false alarms, time and cost. Then Attacks.</p></div>
    </div>
  </div>
  <div class="ag-det">
    <div class="col">
      <div class="panel"><div class="ph"><h3>The text</h3><span class="sp"></span><span class="muted small" id="agexwhat"></span></div>
        <div class="pb col">
          <div class="ag-chips" id="agex"></div>
          <textarea class="input" id="agtext" rows="9" maxlength="4000" placeholder="Type or paste any text: a message from Emma, or an e-mail the agent might open."></textarea>
          <div><span class="label">The agent's reply (only the reply check reads this one)</span><textarea class="input" id="agreply" rows="4" maxlength="2000"></textarea></div>
          <button class="btn primary" id="agcheck">Check with every detector</button>
          <p class="tiny muted">Four of the five run on our own server and cost nothing. The second model is one call to Claude Haiku: a fraction of a cent, from your daily budget.</p>
        </div></div>
      <div class="panel"><div class="ph"><h3>Where each one sits</h3></div><div class="pb col small ink2" id="agsits"></div></div>
    </div>
    <div class="ag-cards" id="agcards"><div class="empty">Loading the detectors…</div></div>
  </div>`;
$("main").insertBefore(det, $("#tab-guards"));

const whereRow = w => `<div class="ag-where">${WHERE.map((x, i) => `${i ? "<i>→</i>" : ""}<span class="${(w || []).includes(x) ? "on" : ""}">${x}</span>`).join("")}</div>`;
function drawCards() {
  $("#agcards").innerHTML = DET.detectors.map(d => `<div class="ag-card ${d.id === "llm_check" ? "wide" : ""}" data-d="${d.id}">
    <h3>${E(d.title)}</h3><div class="kind">${E(d.kind)}</div>${whereRow(d.where)}
    <div id="agr-${d.id}"></div>
    <p class="runs">${E(d.runs)}</p>
    ${d.model ? `<p class="meta"><b>${d.id === "pii" ? "Library" : "Model"}:</b> ${E(d.model)}${d.threshold != null ? ` · <b>threshold</b> ${d.threshold}` : ""}</p>` : ""}
    ${d.numbers ? `<p class="meta">${E(d.numbers)}</p>` : ""}${d.note ? `<p class="meta">${E(d.note)}</p>` : ""}
    ${d.prompt ? `<span class="label" style="margin-top:12px">The prompt, exactly as the code sends it (the text goes where {text} is)</span><pre class="ag-prompt">${E(d.prompt).replace("{text}", "<mark>{text}</mark>")}</pre>` : ""}
    <div class="ag-links"><span class="lbl2">Where it is implemented</span>${srcLinks(d.source)}
      <span class="lbl2" style="margin-top:6px">Run it yourself</span><a href="${E(d.notebook.url)}" target="_blank" rel="noopener">Open ${E(d.notebook.title)} in Colab ↗</a></div>
  </div>`).join("");
  const by = w => DET.detectors.filter(d => d.where.includes(w)).map(d => E(d.title.split(":")[0].split(" (")[0])).join(" · ");
  $("#agsits").innerHTML = `<div><span class="pill accent xs">message in</span> before the agent (the model) reads Emma's message<br><b>${by("message in")}</b></div>
    <div><span class="pill accent xs">tool result</span> when a tool returns text written outside Northbridge, before the model reads it<br><b>${by("tool result")}</b></div>
    <div><span class="pill accent xs">reply out</span> before Emma reads the agent's reply<br><b>${by("reply out")}</b></div>`;
  $("#agex").innerHTML = DET.examples.map((x, i) => `<button class="chipbtn" data-i="${i}" type="button" title="${E(x.what)}">${E(x.chip)}</button>`).join("");
  $$("#agex .chipbtn").forEach(b => b.onclick = () => { EX = DET.examples[+b.dataset.i]; $("#agtext").value = EX.text; exState(); grow(); });
  if (!$("#agreply").value) $("#agreply").value = DET.default_reply || "";
}
function exState() {
  $$("#agex .chipbtn").forEach((b, i) => b.classList.toggle("on", !!EX && DET.examples[i] === EX));
  $("#agexwhat").textContent = EX ? `${EX.id} in the labelled set: ${EX.what}` : "";
}
function grow() {   /* the box shows the whole text, up to a limit */
  const t = $("#agtext"); t.style.height = "auto"; t.style.height = Math.min(Math.max(t.scrollHeight + 2, 150), 620) + "px";
}
$("#agtext").addEventListener("input", () => { if (EX && $("#agtext").value !== EX.text) { EX = null; exState(); } grow(); });
function truth(flag, kind) {   /* against the labelled set, when the text is one of its examples */
  if (!EX) return "";
  if (kind === "injection" && EX.set === "injection") return `<div class="truth">The labelled set says: <b>${EX.label ? "an attack" : "not an attack"}</b>. ${EX.label ? (flag ? "Caught." : "<b>Missed.</b>") : (flag ? "<b>A false alarm.</b>" : "Correct.")}</div>`;
  if (kind === "pii" && EX.set === "PII") return `<div class="truth">The labelled set says: <b>${EX.label ? "personal or payment data" : "no personal data"}</b>. ${EX.label ? (flag ? "Caught." : "<b>Missed.</b>") : (flag ? "<b>A false alarm.</b>" : "Correct.")}</div>`;
  return "";
}
const money = v => "£" + Number(v).toLocaleString("en-GB", {maximumFractionDigits: 2});
const RES = {
  injection_clf: r => `<div class="ag-res ${r.flag ? "flag" : "pass"}"><div class="big">${r.flag ? "Flagged as an injection" : "Passed"}</div>
    <div class="ag-bar"><i style="width:${Math.max(1, Math.round(r.score * 100))}%"></i><u></u></div><div class="ag-barl"><span>0</span><span>threshold ${r.threshold}</span><span>1</span></div>
    <div class="nums">injection probability <b>${Number(r.score).toFixed(4)}</b> · ${ms(r.ms)} · US$0, on our own CPU</div>${truth(r.flag, "injection")}</div>`,
  pii: r => `<div class="ag-res ${r.flag ? "flag" : "pass"}"><div class="big">${r.flag ? `${r.entities.length} item${r.entities.length === 1 ? "" : "s"} masked` : "Nothing to mask"}</div>
    ${r.flag ? `<div class="ag-ents">${r.entities.map(f => `<span class="pill bad xs">${E(f.type)} · ${E(f.text)} · ${f.score}</span>`).join("")}</div><pre class="json">${E(r.redacted)}</pre>` : ""}
    <div class="nums">${ms(r.ms)} · US$0, on our own CPU${r.flag ? " · the trace keeps the masked text" : ""}</div>${truth(r.flag, "pii")}</div>`,
  llm_check: r => `<div class="ag-res ${r.flag ? "flag" : "pass"}"><div class="big">The second model answered: ${E(r.verdict)}</div>
    <div class="nums">“${E(r.reason)}”</div>
    <div class="nums">${ms(r.ms)} · US${usd(r.usd)} · ${fmt(r.tokens_in)} tokens in, ${fmt(r.tokens_out)} out · ${E(r.model)}</div>${truth(r.flag, "injection")}
    <details><summary class="small muted" style="cursor:pointer;margin-top:6px">What was sent to the second model, in full</summary><pre class="json">${E(r.sent)}</pre></details></div>`,
  spotlight: r => `<div class="ag-res note"><div class="big">Wrapped as outside text; the turn is marked</div>
    <div class="nums">What the agent (the model) would read if a tool returned this text as an e-mail:</div><pre class="json full">${E(r.wrapped)}</pre>
    <div class="nums">${r.marked ? "The turn is now marked: until it ends, the code guard refuses any save and any message to an outside address." : ""}</div></div>`,
  output_check: r => `<div class="ag-res ${r.flag ? "flag" : "pass"}"><div class="big">${r.flag ? `${r.flagged.length} figure${r.flagged.length === 1 ? "" : "s"} did not come from Ledgerline` : (r.found.length ? "Every £ figure is in a tool result" : "No £ figure in the reply")}</div>
    <div class="ag-ents">${r.found.map(v => `<span class="pill ${r.flagged.some(b => Math.abs(b - v) < 0.005) ? "bad" : "good"} xs">${money(v)} ${r.flagged.some(b => Math.abs(b - v) < 0.005) ? "✕ in no tool result" : "✓ from a tool"}</span>`).join("")}</div>
    <div class="nums">Compared with what the tools returned in this conversation: <code>${E(r.call.tool)}(${E(argsText(r.call.args))})</code></div>
    ${r.flag ? `<div class="nums">What Emma reads:</div><pre class="json full">${E(r.checked_reply)}</pre>` : ""}
    <details><summary class="small muted" style="cursor:pointer;margin-top:6px">The tool result it was compared with</summary><pre class="json">${E(r.call.out)}</pre></details></div>`,
};
$("#agcheck").onclick = async e => {
  const text = $("#agtext").value.trim(); if (!text) { toast("Type or pick a text to check."); return; }
  const b = e.currentTarget; busy(b, true, "Running five detectors…");
  try { const j = await api("/api/detect", {text, reply: $("#agreply").value});
    j.results.forEach(r => { const el = $("#agr-" + r.id); if (!el) return;
      el.innerHTML = r.error ? `<div class="ag-res"><div class="big">This check could not run</div><div class="nums">${E(r.error)}</div></div>` : RES[r.id](r); });
    refreshMe();
  } catch (x) { toast(x.message); }
  busy(b, false);
};

/* ------------------------------------------------------------------ the instructor's inbox: the sandbox, or one label of a real mailbox */
function resetTrace(msg) { $("#wf").innerHTML = `<div class="empty">${E(msg)}</div>`; $("#incident").classList.add("hide"); $("#spand").innerHTML = ""; $("#tmeta").textContent = ""; $("#tlinks").innerHTML = ""; }
async function peek(fresh) {
  let el = $("#agpeek"); const mb = (ME && ME.mailbox) || {};
  if (!(ME && ME.instructor && mb.live)) { if (el) el.remove(); PEEKED = null; return; }
  if (!el) { el = document.createElement("div"); el.className = "ag-peek"; el.id = "agpeek"; $(".chatp").insertBefore(el, $("#convo")); }
  if (!PEEKED || fresh) { el.innerHTML = `<div class="ph2"><b>Reading the label “${E(mb.label)}” of ${E(mb.user)}…</b></div>`;
    try { PEEKED = await api("/api/mailbox/peek"); } catch (x) { el.innerHTML = `<div class="ph2"><b>The mailbox could not be read.</b></div>${E(x.message)}`; return; } }
  const m = PEEKED.messages || [];
  el.innerHTML = `<div class="ph2"><b>Live: the label “${E(PEEKED.label)}” of ${E(PEEKED.user)}</b><span class="sp"></span><button class="btn xs" id="agpeekre" type="button">Read it again</button></div>
    <div class="muted" style="margin-bottom:4px">${m.length ? `The agent reads ${m.length === 1 ? "this e-mail" : "these " + m.length + " e-mails"} with <code>read_mailbox</code>, as text from outside Northbridge. Nothing is marked read; no other label is opened.` : "The label is empty. Send or move an e-mail into it, then read it again."}</div>
    ${m.map(x => `<div class="m"><b>${E(x.subject)}</b><span>${E(x.received)}</span><p>${E(x.sender)} · ${E(x.preview)}${(x.preview || "").length >= 200 ? "…" : ""}</p></div>`).join("")}`;
  $("#agpeekre").onclick = () => peek(true);
}
function inbox() {
  let el = $("#aginbox"); const mb = (ME && ME.mailbox) || {};
  if (!(ME && ME.instructor)) { if (el) el.remove(); peek(); return; }
  if (!el) {
    el = document.createElement("span"); el.className = "gsw ag-inbox"; el.id = "aginbox";
    el.innerHTML = `Inbox<div class="seg"><button data-m="sandbox" type="button">sandbox</button><button data-m="live" type="button">my mailbox</button></div>`;
    $(".chatp .ph").insertBefore(el, $("#showprompt"));
    $$("button", el).forEach(b => b.onclick = async () => {
      const live = b.dataset.m === "live"; if (live === !!((ME.mailbox || {}).live)) return;
      busy(b, true);
      try { ME = await api("/api/chat/mailbox", {live}); PEEKED = null; renderChat(); resetTrace(live ? "New conversation. The AP inbox is your mailbox's label; this chat's traces are not public." : "New conversation, fresh sandbox, the sandbox's own inbox.");
        toast(live ? "Inbox: your mailbox's label. A new chat." : "Inbox: the sandbox. A new chat."); } catch (x) { toast(x.message); }
      busy(b, false); inbox();
    });
  }
  el.title = mb.available ? `One label, read-only: “${mb.label}” of ${mb.user}. Switching starts a new chat.` : "The live mailbox is not set up on this server yet: run tools/aegis_mailbox_secret.sh.";
  $$("button", el).forEach(b => { b.classList.toggle("on", (b.dataset.m === "live") === !!mb.live); if (b.dataset.m === "live") b.disabled = !mb.available; });
  peek();
}

/* ------------------------------------------------------------------ called by argus.js once the lab is open */
async function loadBench() { try { BENCH = await api("/api/bench"); drawTable(); drawOwn(); } catch (x) { $("#agtbl").innerHTML = `<tr><td colspan="4" class="muted">${E(x.message)}</td></tr>`; } }
async function loadDetect() { try { DET = await api("/api/detect/info"); drawCards(); } catch (x) { $("#agcards").innerHTML = `<div class="empty">${E(x.message)}</div>`; } }
window.aegisLab = function () {
  $(".brand div").innerHTML = "Aegis<br><small>Lecture 7 · Guardrails and Red-Teaming</small>";
  stripState(); inbox();
  if (!BENCH) loadBench();
  if (!DET) loadDetect();
};
})();
