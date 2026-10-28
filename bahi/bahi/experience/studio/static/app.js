/* Workflow Studio: the canvas UI. Vanilla JS + inline SVG, no build step.
   Talks to /api/studio/* (see SPEC.md §3). State lives in S; the workflow JSON is S.wf (SPEC.md §1). */
(() => {
"use strict";

// ------------------------------------------------------------------------------------------------ helpers
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const inr = v => typeof v === "number" ? "₹" + v.toLocaleString("en-IN", {maximumFractionDigits: 2}) : (v ?? "–");
const num = v => typeof v === "number" ? v.toLocaleString("en-IN") : (v ?? "–");
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "class") el.className = v;
    else if (k === "html") el.innerHTML = v;
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat()) {
    if (c == null || c === false) continue;
    if (typeof c === "string" && c.startsWith("<svg")) el.insertAdjacentHTML("beforeend", c);  // an icon from svg()
    else el.append(c.nodeType ? c : document.createTextNode(c));
  }
  return el;
}
async function api(method, path, body) {
  const r = await fetch(path, {method, credentials: "same-origin", headers: {"Content-Type": "application/json"},
                               body: body === undefined ? undefined : JSON.stringify(body)});
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.detail || r.statusText);
  return j;
}
function toast(text, err) {
  const t = h("div", {class: "toast" + (err ? " err" : "")}, text);
  $("#toasts").append(t);
  setTimeout(() => t.remove(), err ? 6000 : 3200);
}

// ------------------------------------------------------------------------------------------------ icons
const P = {
  play: '<path d="M7 4.5v15l12-7.5z" fill="currentColor"/>',
  form: '<rect x="5" y="3.5" width="14" height="17" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.9"/><path d="M8.5 8.5h7M8.5 12h7M8.5 15.5h4" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>',
  bolt: '<path d="M13.5 2.5L5 13.5h6l-1 8 8.5-11h-6z" fill="currentColor"/>',
  clock: '<circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.9"/><path d="M12 7v5.2l3.4 2" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>',
  chat: '<path d="M4.5 6.5a3 3 0 013-3h9a3 3 0 013 3v6.5a3 3 0 01-3 3H10l-4.5 4v-4h0a3 3 0 01-1-2.2z" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"/>',
  search: '<circle cx="10.5" cy="10.5" r="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15 15l5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
  doc: '<path d="M6.5 3.5h7l4 4v13h-11z" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"/><path d="M9.5 12.5h5M9.5 16h5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>',
  cart: '<path d="M3.5 4.5h2.4l2 10.5h9.6l2-7.5H7" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9.5" cy="19" r="1.6" fill="currentColor"/><circle cx="16.5" cy="19" r="1.6" fill="currentColor"/>',
  send: '<path d="M4 12l16-8-6 16-2.5-6.5z" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"/>',
  seal: '<path d="M12 3l2.2 1.6 2.7-.2.9 2.6 2.3 1.5-.8 2.6.8 2.6-2.3 1.5-.9 2.6-2.7-.2L12 21l-2.2-1.6-2.7.2-.9-2.6-2.3-1.5.8-2.6-.8-2.6 2.3-1.5.9-2.6 2.7.2z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M8.8 12.2l2.2 2.2 4.2-4.4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>',
  box: '<path d="M12 3l8 4.2v9.6L12 21l-8-4.2V7.2z M4 7.2l8 4.3 8-4.3M12 11.5V21" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  book: '<path d="M5 4.5h5.5a2 2 0 012 2V20a2 2 0 00-2-2H5zM19 4.5h-5.5a2 2 0 00-1 .3M19 4.5V18h-5.5a2 2 0 00-1 .3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  branch: '<circle cx="6" cy="6" r="2.3" fill="none" stroke="currentColor" stroke-width="1.9"/><circle cx="18" cy="7" r="2.3" fill="none" stroke="currentColor" stroke-width="1.9"/><circle cx="18" cy="17" r="2.3" fill="none" stroke="currentColor" stroke-width="1.9"/><path d="M8.3 6.3c4 .2 4.5.4 7.4.7M8 7.5c2.5 3 3.5 8.2 7.7 9.3" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>',
  sliders: '<path d="M5 7h14M5 12h14M5 17h14" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/><circle cx="9" cy="7" r="2.2" fill="#fff" stroke="currentColor" stroke-width="1.9"/><circle cx="15" cy="12" r="2.2" fill="#fff" stroke="currentColor" stroke-width="1.9"/><circle cx="8" cy="17" r="2.2" fill="#fff" stroke="currentColor" stroke-width="1.9"/>',
  spark: '<path d="M12 3l1.9 5.6L19.5 10l-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.4z" fill="currentColor"/><path d="M18.5 15.5l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z" fill="currentColor"/>',
  agent: '<circle cx="12" cy="12" r="3" fill="currentColor"/><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-dasharray="3.4 2.6"/><circle cx="12" cy="4" r="1.8" fill="currentColor"/><circle cx="19" cy="15.5" r="1.8" fill="currentColor"/><circle cx="5" cy="15.5" r="1.8" fill="currentColor"/>',
  inbox: '<path d="M4 13.5l2.2-8h11.6l2.2 8V19H4z M4 13.5h4.5l1 2h5l1-2H20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
  check: '<path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>',
  x: '<path d="M7 7l10 10M17 7L7 17" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>',
  warn: '<path d="M12 6v7" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"/><circle cx="12" cy="17.5" r="1.7" fill="currentColor"/>',
  hour: '<path d="M8 4h8M8 20h8M9 4c0 5 6 5 6 8s-6 3-6 8M15 4c0 5-6 5-6 8s6 3 6 8" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>',
  dots: '<circle cx="6" cy="12" r="2" fill="currentColor"/><circle cx="12" cy="12" r="2" fill="currentColor"/><circle cx="18" cy="12" r="2" fill="currentColor"/>',
};
const svg = (name, size) => `<svg viewBox="0 0 24 24"${size ? ` width="${size}" height="${size}"` : ""}>${P[name] || P.dots}</svg>`;
const CAT = {"Look up": "lookup", "Purchasing": "purchasing", "Approvals": "approvals", "Stores": "stores",
             "Knowledge": "knowledge", "Messaging": "messaging"};
const TOOL_ICON = {find_item: "search", check_stock: "box", find_supplier: "search", check_budget: "doc", search_policy: "book",
  create_purchase_request: "doc", list_my_approvals: "inbox", approve_purchase_request: "seal", create_purchase_order: "cart",
  approve_purchase_order: "seal", release_purchase_order: "send", order_status: "doc", receive_goods: "box",
  register_supplier: "doc", send_message: "chat"};
const KIND_ICON = {manual: "play", form: "form", event: "bolt", schedule: "clock", chat: "chat"};
const KIND_LABEL = {manual: "Manual start", form: "Form", event: "Stock below reorder", schedule: "Schedule", chat: "Chat message"};
const TYPE_ICON = {condition: "branch", approval: "seal", set: "sliders", llm: "spark", agent: "agent", message: "send"};
const SHORT = {check_stock: "stock", create_purchase_request: "pr", create_purchase_order: "po", release_purchase_order: "release",
  receive_goods: "grn", approve_purchase_request: "approve_pr", approve_purchase_order: "approve_po", find_item: "item",
  find_supplier: "supplier", check_budget: "budget", search_policy: "policy", list_my_approvals: "inbox",
  order_status: "status", register_supplier: "new_supplier", send_message: "msg",
  trigger: "start", condition: "check", approval: "approval", set: "values", llm: "llm", agent: "agent", message: "message"};
const MODELS = ["gemini:gemini-3.8-flash", "gemini:gemini-3.1-flash-lite", "gemini:gemini-3.1-pro-preview"];
const NODE_W = 200;

// ------------------------------------------------------------------------------------------------ state
const S = {tools: {}, toolList: [], types: [], people: {}, me: null, wfs: [], wf: null, sel: null, selEdge: null,
           run: null, view: {x: 60, y: 40, k: 1}, tab: "config", running: false, saveTimer: null, chat: [], els: {}};
const node = id => S.wf && S.wf.nodes.find(n => n.id === id);
const first = uid => (S.people[uid]?.name || uid || "").split(" ")[0];
const trigger = () => S.wf?.nodes.find(n => n.type === "trigger");

function cat(n) {
  if (n.type === "trigger") return "trigger";
  if (n.type === "tool") return CAT[S.tools[n.config.tool]?.category] || "logic";
  if (n.type === "llm" || n.type === "agent") return "ai";
  if (n.type === "message") return "messaging";
  if (n.type === "approval") return "approvals";
  return "logic";
}
function iconName(n) {
  if (n.type === "trigger") return KIND_ICON[n.config.kind || "manual"];
  if (n.type === "tool") return TOOL_ICON[n.config.tool] || "doc";
  return TYPE_ICON[n.type] || "dots";
}
function subtitle(n) {
  const c = n.config || {};
  switch (n.type) {
    case "trigger": return KIND_LABEL[c.kind || "manual"] + (c.kind === "event" ? ` · ${(c.item_codes || []).length} items` : "");
    case "tool": return `${c.tool} · as ${first(c.as || "KJOSHI")}`;
    case "condition": return c.if ? `if ${c.if.replace(/[{}]/g, "").trim()}` : "if …";
    case "approval": return `${first(c.approver || "RMEHTA")} signs ${c.doc_no ? c.doc_no.replace(/[{}]/g, "").replace("nodes.", "") : "…"}`;
    case "llm": return (c.output === "json" ? `JSON · ${(c.fields || []).join(", ")}` : "text") ;
    case "agent": return `${(c.tools || []).length} tools · as ${first(c.as || "KJOSHI")}`;
    case "message": return `to ${c.to || "…"} · as ${first(c.as || "KJOSHI")}`;
    case "set": return Object.keys(c.values || {}).join(", ") || "values";
  }
  return n.type;
}
function outPorts(n) {
  const ports = n.type === "condition" ? ["true", "false"] : n.type === "approval" ? ["out", "rejected"] : ["out"];
  if (["tool", "llm", "agent", "message", "approval"].includes(n.type)) ports.push("error");
  return ports;
}
const PORT_LABEL = {true: "yes", false: "no", rejected: "rejected", error: "on error"};

// ------------------------------------------------------------------------------------------------ boot
async function boot() {
  const [nodes, me, wfs] = await Promise.all([api("GET", "/api/studio/nodes"), api("GET", "/api/studio/me"),
                                              api("GET", "/api/studio/workflows")]);
  S.types = nodes.types; S.toolList = nodes.tools; S.people = nodes.people; S.me = me; S.wfs = wfs;
  for (const t of nodes.tools) S.tools[t.name] = t;
  $("#who").textContent = me.name ? `Signed in: ${me.name}` : "";
  buildPalette();
  bindCanvas();
  bindTop();
  const m = location.pathname.match(/\/studio\/w\/([^/]+)/);
  let want = m ? decodeURIComponent(m[1]) : null;
  try { want = want || localStorage.getItem("studio.wf"); } catch (e) {}
  if (want && wfs.some(w => w.id === want)) await loadWorkflow(want);
  else if (wfs.length) await loadWorkflow(wfs[0].id);
  else { render(); openTemplates(true); }
}

async function loadWorkflow(id) {
  const wf = await api("GET", `/api/studio/workflows/${encodeURIComponent(id)}`);
  S.wf = wf; S.sel = null; S.selEdge = null; S.run = null; S.chat = [];
  showProblems(wf.problems || []);
  delete S.wf.problems;
  $("#wfName").value = wf.name || "Untitled workflow";
  history.replaceState(null, "", `/studio/w/${encodeURIComponent(id)}`);
  try { localStorage.setItem("studio.wf", id); } catch (e) {}
  closeInspector();
  render();
  requestAnimationFrame(() => { if (wf.nodes.length > 1) fit(); else { S.view = {x: 20, y: 40, k: 1}; applyView(); } });
  setSaved("Saved");
  updateRunButton();
  const last = (await api("GET", `/api/studio/runs?workflow_id=${encodeURIComponent(id)}`))[0];
  if (last && last.status === "waiting") { S.run = await api("GET", `/api/studio/runs/${last.id}`); paint(); openInspector("run"); }
}

// ------------------------------------------------------------------------------------------------ palette
function paletteEntries() {
  const groups = {};
  const add = (g, e) => (groups[g] = groups[g] || []).push(e);
  for (const t of S.types) add(t.group, {key: t.type + (t.kind ? ":" + t.kind : ""), spec: {type: t.type, kind: t.kind},
    title: t.title, desc: t.description, icon: t.type === "trigger" ? KIND_ICON[t.kind] : TYPE_ICON[t.type],
    cls: t.type === "trigger" ? "trigger" : (t.group === "AI" ? "ai" : t.group === "Messaging" ? "messaging" : t.type === "approval" ? "approvals" : "logic")});
  for (const t of S.toolList) add("Tools · " + t.category, {key: "tool:" + t.name, spec: {type: "tool", tool: t.name},
    title: t.title, desc: t.name, icon: TOOL_ICON[t.name], cls: CAT[t.category] || "logic", writes: t.writes});
  return groups;
}
function buildPalette() {
  const q = ($("#paletteSearch").value || "").toLowerCase();
  const box = $("#paletteGroups");
  box.innerHTML = "";
  for (const [g, items] of Object.entries(paletteEntries())) {
    const hit = items.filter(e => !q || (e.title + " " + e.desc + " " + g).toLowerCase().includes(q));
    if (!hit.length) continue;
    box.append(h("div", {class: "pgroup"}, h("h4", {}, g),
      ...hit.map(e => h("div", {class: "pitem", "data-key": e.key, title: e.desc,
                                onmousedown: ev => paletteDown(ev, e)},
        h("span", {class: "ico c-" + e.cls, html: svg(e.icon)}),
        h("span", {class: "pt"}, h("b", {}, e.title), h("small", {}, e.writes ? e.desc + " · writes" : e.desc))))));
  }
}
function paletteDown(ev, entry) {
  if (ev.button !== 0) return;
  ev.preventDefault();
  const ghost = $("#ghost"), x0 = ev.clientX, y0 = ev.clientY;
  let moved = false;
  ghost.innerHTML = `<span class="ico c-${entry.cls}">${svg(entry.icon)}</span>${esc(entry.title)}`;
  const move = e => {
    if (!moved && Math.hypot(e.clientX - x0, e.clientY - y0) < 5) return;
    moved = true; ghost.hidden = false;
    ghost.style.left = e.clientX + "px"; ghost.style.top = e.clientY + "px";
  };
  const up = e => {
    document.removeEventListener("mousemove", move); document.removeEventListener("mouseup", up);
    ghost.hidden = true;
    if (!S.wf) return toast("Pick a template or start a blank workflow first.");
    const r = $("#canvas").getBoundingClientRect();
    if (moved) {
      if (e.clientX < r.left || e.clientY < r.top) return;
      const w = toWorld(e.clientX, e.clientY);
      addNode(entry.spec, w.x - 30, w.y - 24, false);
    } else {
      const prev = S.sel && node(S.sel);
      if (prev) addNode(entry.spec, prev.x + 230, prev.y, true);
      else { const w = toWorld(r.left + r.width * .42, r.top + r.height * .42); addNode(entry.spec, w.x, w.y, false); }
    }
  };
  document.addEventListener("mousemove", move); document.addEventListener("mouseup", up);
}

function defaultConfig(spec) {
  switch (spec.type) {
    case "trigger": return {kind: spec.kind || "manual", ...(spec.kind === "event" ? {event: "stock_below_reorder", item_codes: ["GSK-SIL-05L"], as: "KJOSHI"} : {}),
      ...(spec.kind === "form" ? {fields: [{name: "po_no", label: "Purchase order", type: "text", default: ""}]} : {}),
      ...(spec.kind === "schedule" ? {every: "day", at: "09:00"} : {})};
    case "tool": {
      const t = S.tools[spec.tool];
      return {tool: spec.tool, as: spec.tool === "receive_goods" ? "NDESAI" : spec.tool.startsWith("approve_") ? "RMEHTA" : "KJOSHI",
              args: {}, ...("confirm" in (t.input_schema.properties || {}) ? {confirm: false} : {})};
    }
    case "condition": return {if: ""};
    case "approval": return {doc_no: "", approver: "RMEHTA"};
    case "set": return {values: {}};
    case "llm": return {prompt: "", output: "text", model: MODELS[0]};
    case "agent": return {instructions: "You are a purchasing assistant at Rasoi Steel Works.", tools: ["find_item", "check_stock"],
                          as: "KJOSHI", may_commit: false, model: MODELS[0], input: "{{ trigger.message }}", max_steps: 10};
    case "message": return {to: "@rohit", text: "", as: "KJOSHI"};
  }
  return {};
}
function uniqueId(base) {
  let id = base, i = 2;
  while (node(id)) id = `${base}_${i++}`;
  return id;
}
function addNode(spec, x, y, connectFromSel) {
  if (spec.type === "trigger" && trigger()) {
    const t = trigger();
    t.config = {...defaultConfig(spec)}; t.title = KIND_LABEL[spec.kind];
    toast("A workflow has one trigger: it is now a " + KIND_LABEL[spec.kind].toLowerCase() + " trigger.");
    render(); select(t.id); markDirty(); return t;
  }
  const n = {id: uniqueId(SHORT[spec.tool || spec.type] || spec.type), type: spec.type,
             title: spec.type === "tool" ? S.tools[spec.tool].title : spec.type === "trigger" ? KIND_LABEL[spec.kind] :
               (S.types.find(t => t.type === spec.type)?.title || spec.type),
             x: Math.round(x / 10) * 10, y: Math.round(y / 10) * 10, config: defaultConfig(spec)};
  const from = connectFromSel && S.sel && node(S.sel);
  S.wf.nodes.push(n);
  if (from && n.type !== "trigger") S.wf.edges.push({from: from.id, to: n.id, ...(from.type === "condition" ? {port: "true"} : {})});
  render(); select(n.id); markDirty();
  return n;
}

// ------------------------------------------------------------------------------------------------ canvas rendering
function nodeHTML(n) {
  const c = n.config || {}, t = n.type === "tool" ? S.tools[c.tool] : null;
  const badges = [];
  if (t && "confirm" in (t.input_schema.properties || {})) badges.push(c.confirm ? '<span class="badge commit">Commit</span>' : '<span class="badge preview">Preview only</span>');
  else if (t && t.writes) badges.push('<span class="badge commit">Writes</span>');
  if (n.type === "agent") badges.push(c.may_commit ? '<span class="badge commit">May commit</span>' : '<span class="badge preview">Previews only</span>');
  if (n.type === "approval") badges.push('<span class="badge">Pauses the run</span>');
  if (n.type === "llm") badges.push(`<span class="badge">${esc((c.model || MODELS[0]).split(":").pop())}</span>`);
  const outs = outPorts(n);
  const used = new Set(S.wf.edges.filter(e => e.from === n.id).map(e => e.port || "out"));
  let ports = "";
  const tops = n.type === "condition" ? [50, 76] : [21, 51];  // a condition's yes/no sit below its title
  outs.filter(p => p !== "error").forEach((p, i) => {
    ports += `<div class="port out p-${p}" data-port="${p}" style="top:${tops[i]}px" title="${PORT_LABEL[p] || "next"}"></div>`;
    if (PORT_LABEL[p]) ports += `<div class="plabel" style="top:${tops[i] - 1}px">${PORT_LABEL[p]}</div>`;
  });
  if (outs.includes("error")) {
    ports += `<div class="port out p-error${used.has("error") ? " used" : ""}" data-port="error" style="bottom:14px;top:auto" title="on error: where the run goes if this node fails"></div>`;
    if (used.has("error")) ports += `<div class="plabel err" style="bottom:-6px">on error</div>`;
  }
  return `<div class="port in" data-port="in"></div>
    <div class="nhead"><span class="ico c-${cat(n)}">${svg(iconName(n))}</span>
      <span class="nt"><b>${esc(n.title || n.id)}</b><small>${esc(subtitle(n))}</small></span></div>
    ${badges.length ? `<div class="nbadges">${badges.join("")}</div>` : ""}
    <div class="nres" title="Show this node's output"></div>
    <button class="pill small violet waitbtn" data-act="approve">${svg("seal", 14)} Open approval</button>
    <span class="nstate"></span>${ports}`;
}
function renderNode(n) {
  let el = S.els[n.id];
  const fresh = !el;
  if (fresh) { el = h("div", {"data-id": n.id}); S.els[n.id] = el; $("#nodes").append(el); }
  el.className = `node t-${n.type}` + (S.sel === n.id ? " sel" : "");
  el.style.left = n.x + "px"; el.style.top = n.y + "px";
  const two = outPorts(n).filter(p => p !== "error").length > 1;
  el.style.minHeight = two ? "100px" : "";
  el.innerHTML = nodeHTML(n);
  paintNode(n.id);
}
function render() {
  $("#nodes").innerHTML = ""; S.els = {};
  if (S.wf) S.wf.nodes.forEach(renderNode);
  renderEdges(); applyView();
  $("#empty").hidden = !!(S.wf && S.wf.nodes.length);
}
function portXY(nid, port) {
  const n = node(nid), el = S.els[nid];
  if (!n || !el) return null;
  if (port === "in") { const p = el.querySelector(".port.in"); return {x: n.x - 1, y: n.y + p.offsetTop + p.offsetHeight / 2}; }
  const p = el.querySelector(`.port.out[data-port="${port}"]`) || el.querySelector(".port.out");
  return {x: n.x + el.offsetWidth + 1, y: n.y + p.offsetTop + p.offsetHeight / 2};
}
function curve(a, b) {
  const dx = Math.max(50, Math.abs(b.x - a.x) * .5);
  return `M${a.x},${a.y} C${a.x + dx},${a.y} ${b.x - dx},${b.y} ${b.x},${b.y}`;
}
function renderEdges() {
  const g = $("#edgeLayer");
  if (!S.wf) { g.innerHTML = ""; return; }
  const taken = new Set((S.run?.edges_taken || []).map(e => e.join("|")));
  const runningId = Object.entries(S.run?.nodes || {}).find(([, r]) => r.status === "running")?.[0];
  let out = "";
  S.wf.edges.forEach((e, i) => {
    const a = portXY(e.from, e.port || "out"), b = portXY(e.to, "in");
    if (!a || !b) return;
    const d = curve(a, b), port = e.port || "out";
    let cls = "edge" + (port === "error" ? " err" : "");
    if (S.run && S.run.nodes[e.from]) {
      const key = [e.from, e.to, port].join("|");
      if (taken.has(key)) cls += e.to === runningId ? " flow" : " taken";
      else if (["done", "warning", "error", "skipped"].includes(S.run.nodes[e.from].status)) cls += " dim";
    }
    if (S.selEdge === i) cls += " sel";
    out += `<path class="${cls}" d="${d}" marker-end="url(#arrow)"/><path class="edge-hit" data-edge="${i}" d="${d}"/>`;
    if (S.selEdge === i) {
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      out += `<g class="edel" data-del="${i}" transform="translate(${mx},${my})"><circle r="11"/><path d="M-4,-4L4,4M4,-4L-4,4"/></g>`;
    }
  });
  g.innerHTML = out;
}
function applyView() {
  const {x, y, k} = S.view;
  $("#world").style.transform = `translate(${x}px,${y}px) scale(${k})`;
  const c = $("#canvas");
  c.style.backgroundSize = `${22 * k}px ${22 * k}px,100% 100%,100% 100%`;
  c.style.backgroundPosition = `${x}px ${y}px,0 0,0 0`;
  $("#zoomPct").textContent = Math.round(k * 100) + "%";
}
function toWorld(cx, cy) {
  const r = $("#canvas").getBoundingClientRect();
  return {x: (cx - r.left - S.view.x) / S.view.k, y: (cy - r.top - S.view.y) / S.view.k};
}
function zoomAt(cx, cy, factor) {
  const r = $("#canvas").getBoundingClientRect();
  const k = Math.min(1.8, Math.max(.3, S.view.k * factor));
  const px = cx - r.left, py = cy - r.top;
  S.view.x = px - (px - S.view.x) * (k / S.view.k);
  S.view.y = py - (py - S.view.y) * (k / S.view.k);
  S.view.k = k; applyView();
}
function fit() {
  if (!S.wf || !S.wf.nodes.length) return;
  const r = $("#canvas").getBoundingClientRect();
  const right = $("#inspector").hidden ? 0 : 392 + 28;
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (const n of S.wf.nodes) {
    const el = S.els[n.id];
    x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y);
    x1 = Math.max(x1, n.x + (el?.offsetWidth || NODE_W)); y1 = Math.max(y1, n.y + (el?.offsetHeight || 90));
  }
  const W = r.width - right - 120, H = r.height - 170;
  // fit everything; but never shrink below 60% to dodge the panel: then show the start and let the panel cover the end
  const k = Math.min(1.15, Math.max(.6, Math.min(W / (x1 - x0), H / (y1 - y0))));
  const fits = (x1 - x0) * k <= W;
  S.view = {k, x: fits ? 60 + (W - (x1 - x0) * k) / 2 - x0 * k : 40 - x0 * k, y: 80 + (H - (y1 - y0) * k) / 2 - y0 * k};
  applyView();
}

// ------------------------------------------------------------------------------------------------ canvas interaction
function bindCanvas() {
  const canvas = $("#canvas"), nodesEl = $("#nodes");
  canvas.addEventListener("wheel", e => {
    e.preventDefault();
    if (e.ctrlKey || e.metaKey) zoomAt(e.clientX, e.clientY, Math.exp(-e.deltaY * 0.01));
    else { S.view.x -= e.deltaX; S.view.y -= e.deltaY; applyView(); }
  }, {passive: false});
  canvas.addEventListener("mousedown", e => {
    if (e.button !== 0) return;
    const del = e.target.closest(".edel");
    if (del) { S.wf.edges.splice(+del.dataset.del, 1); S.selEdge = null; render(); markDirty(); return; }
    const hit = e.target.closest(".edge-hit");
    if (hit) { S.selEdge = +hit.dataset.edge; S.sel = null; closeInspector(); render(); return; }
    if (e.target.closest(".node") || e.target.closest(".zoom") || e.target.closest(".runbar") || e.target.closest(".empty")) return;
    // pan the background
    const x0 = e.clientX, y0 = e.clientY, v0 = {...S.view};
    let moved = false;
    canvas.classList.add("panning");
    const move = ev => { moved = true; S.view.x = v0.x + ev.clientX - x0; S.view.y = v0.y + ev.clientY - y0; applyView(); };
    const up = () => {
      canvas.classList.remove("panning");
      document.removeEventListener("mousemove", move); document.removeEventListener("mouseup", up);
      if (!moved) { S.sel = null; S.selEdge = null; render(); if (S.run) openInspector("run"); else closeInspector(); }
    };
    document.addEventListener("mousemove", move); document.addEventListener("mouseup", up);
  });
  nodesEl.addEventListener("mousedown", e => {
    if (e.button !== 0) return;
    const el = e.target.closest(".node");
    if (!el) return;
    const id = el.dataset.id;
    const port = e.target.closest(".port.out");
    if (port) { e.stopPropagation(); e.preventDefault(); return startConnect(id, port.dataset.port, e); }
    if (e.target.closest("[data-act=approve]")) { e.stopPropagation(); return; }
    e.preventDefault();
    const n = node(id), x0 = e.clientX, y0 = e.clientY, nx = n.x, ny = n.y;
    let moved = false;
    const move = ev => {
      const dx = (ev.clientX - x0) / S.view.k, dy = (ev.clientY - y0) / S.view.k;
      if (!moved && Math.hypot(dx, dy) < 3) return;
      moved = true;
      n.x = Math.round((nx + dx) / 10) * 10; n.y = Math.round((ny + dy) / 10) * 10;
      el.style.left = n.x + "px"; el.style.top = n.y + "px"; renderEdges();
    };
    const up = ev => {
      document.removeEventListener("mousemove", move); document.removeEventListener("mouseup", up);
      if (moved) markDirty();
      else select(id, ev.target.closest(".nres") ? "output" : null);
    };
    document.addEventListener("mousemove", move); document.addEventListener("mouseup", up);
  });
  nodesEl.addEventListener("click", e => { if (e.target.closest("[data-act=approve]")) openApproval(); });
  $("#zoomIn").onclick = () => { const r = canvas.getBoundingClientRect(); zoomAt(r.left + r.width / 2, r.top + r.height / 2, 1.2); };
  $("#zoomOut").onclick = () => { const r = canvas.getBoundingClientRect(); zoomAt(r.left + r.width / 2, r.top + r.height / 2, 1 / 1.2); };
  $("#zoomFit").onclick = fit;
  $("#emptyTemplates").onclick = () => openTemplates(false);
  window.addEventListener("resize", () => renderEdges());
  document.addEventListener("keydown", e => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || "");
    if ((e.metaKey || e.ctrlKey) && e.key === "s") { e.preventDefault(); save(); return; }
    if (e.key === "Escape") { hidePicker(); closeSheet(); return; }
    if (typing || !S.wf) return;
    if (e.key === "Delete" || e.key === "Backspace") {
      if (S.selEdge != null) { S.wf.edges.splice(S.selEdge, 1); S.selEdge = null; render(); markDirty(); }
      else if (S.sel) deleteNode(S.sel);
    }
  });
}
function startConnect(from, port, e) {
  const temp = $("#tempEdge"), a = portXY(from, port);
  let hot = null;
  const move = ev => {
    const w = toWorld(ev.clientX, ev.clientY);
    temp.setAttribute("d", curve(a, w));
    const t = document.elementFromPoint(ev.clientX, ev.clientY);
    const p = t && (t.closest(".port.in") || (t.closest(".node") && t.closest(".node").querySelector(".port.in")));
    if (hot && hot !== p) hot.classList.remove("hot");
    hot = p && p.closest(".node").dataset.id !== from ? p : null;
    if (hot) hot.classList.add("hot");
  };
  const up = () => {
    document.removeEventListener("mousemove", move); document.removeEventListener("mouseup", up);
    temp.setAttribute("d", "");
    if (!hot) return;
    hot.classList.remove("hot");
    const to = hot.closest(".node").dataset.id;
    if (node(to).type === "trigger") return toast("Nothing can lead into the trigger.");
    if (S.wf.edges.some(x => x.from === from && x.to === to && (x.port || "out") === port)) return;
    S.wf.edges.push({from, to, ...(port !== "out" ? {port} : {})});
    render(); markDirty();
  };
  move(e);
  document.addEventListener("mousemove", move); document.addEventListener("mouseup", up);
}
function select(id, tab) {
  S.sel = id; S.selEdge = null;
  for (const [nid, el] of Object.entries(S.els)) el.classList.toggle("sel", nid === id);
  renderEdges();
  openInspector(tab || (S.tab === "output" && S.run?.nodes[id]?.output ? "output" : "config"));
}
function deleteNode(id) {
  const n = node(id);
  S.wf.nodes = S.wf.nodes.filter(x => x.id !== id);
  S.wf.edges = S.wf.edges.filter(e => e.from !== id && e.to !== id);
  S.sel = null; closeInspector(); render(); markDirty();
  toast(`Removed “${n.title || id}”.`);
}

// ------------------------------------------------------------------------------------------------ run painting
function paintNode(id) {
  const el = S.els[id];
  if (!el) return;
  const rec = S.run?.nodes?.[id];
  el.classList.remove("s-running", "s-done", "s-warning", "s-error", "s-waiting", "s-skipped", "s-pending", "has-res", "run-on");
  if (!rec) return;
  el.classList.add("s-" + rec.status, "run-on");
  const text = rec.status === "waiting" ? rec.summary : (rec.summary || rec.error || "");
  const res = el.querySelector(".nres");
  if (text && rec.status !== "pending" && rec.status !== "skipped") { res.textContent = text; el.classList.add("has-res"); }
  const st = el.querySelector(".nstate");
  st.innerHTML = svg({done: "check", error: "x", warning: "warn", waiting: "hour", running: "dots"}[rec.status] || "dots");
}
function paint() {
  if (!S.wf) return;
  for (const n of S.wf.nodes) paintNode(n.id);
  renderEdges(); paintRunbar(); updateRunButton();
  if (!$("#inspector").hidden && (S.tab === "run" || S.tab === "output")) renderInspector();
}
function paintRunbar() {
  const bar = $("#runbar"), r = S.run;
  if (!r) { bar.hidden = true; return; }
  bar.hidden = false;
  bar.className = "runbar " + r.status;
  const done = Object.values(r.nodes).filter(x => ["done", "warning"].includes(x.status)).length;
  const label = {running: "Running", done: "Finished", failed: "Stopped", waiting: "Waiting for " + (r.waiting_for?.approver_name || "approval")}[r.status];
  bar.innerHTML = `<span class="dot"></span><span>${esc(label)} · ${done} of ${Object.keys(r.nodes).length} nodes</span>`;
  if (r.status === "waiting") bar.append(h("button", {class: "pill small violet", onclick: openApproval, id: "barApprove"}, "Open approval"));
  bar.append(h("button", {class: "pill small", onclick: () => openInspector("run")}, "Run log"));
  if (r.status !== "running") bar.append(h("button", {class: "pill small ghost", title: "Clear the run from the canvas",
    onclick: () => { S.run = null; paint(); if (S.tab === "run") closeInspector(); }}, "Clear"));
}
function predictNext(run) {
  // the same rule as the engine (SPEC §2): every input settled, at least one taken; leftmost first
  const fin = new Set(["done", "warning", "error", "skipped"]);
  const taken = new Set(run.edges_taken.map(e => e.join("|")));
  const order = [...run.workflow.nodes].sort((a, b) => (a.x - b.x) || (a.y - b.y));
  for (const n of order) {
    if (run.nodes[n.id].status !== "pending" || n.type === "trigger") continue;
    const inc = run.workflow.edges.filter(e => e.to === n.id);
    if (inc.length && inc.every(e => fin.has(run.nodes[e.from].status)) &&
        inc.some(e => taken.has([e.from, e.to, e.port || "out"].join("|")))) return n.id;
  }
  return null;
}

// ------------------------------------------------------------------------------------------------ running
function updateRunButton() {
  const b = $("#btnRun"), t = trigger(), kind = t?.config?.kind || "manual";
  b.disabled = S.running || !S.wf;
  $("span", b).textContent = S.running ? "Running…" : kind === "chat" ? "Open chat" : kind === "event" ? "Check now" :
    S.run?.status === "waiting" ? "Run again" : "Run";
}
async function runWorkflow() {
  if (S.running || !S.wf) return;
  const t = trigger();
  if (!t) return toast("Add a trigger first (left, under Triggers).", true);
  if (t.config.kind === "chat") return openInspector("chat");
  const problems = await save();
  if (problems && problems.length) return toast(problems[0], true);
  let data = {};
  if (t.config.kind === "form") { data = await formSheet(t); if (!data) return; }
  S.running = true; updateRunButton();
  try {
    S.run = await api("POST", `/api/studio/workflows/${encodeURIComponent(S.wf.id)}/run`, {trigger: data, mode: "step"});
    for (const n of S.wf.nodes) if (!S.run.nodes[n.id]) S.run.nodes[n.id] = {status: "pending"};
    paint(); openInspector("run");
    await sleep(450);
    await autoStep();
  } catch (e) { toast(e.message, true); }
  S.running = false; updateRunButton();
}
async function autoStep() {
  S.running = true; updateRunButton();
  try {
    while (S.run && S.run.status === "running") {
      const next = predictNext(S.run);
      if (next) { S.run.nodes[next].status = "running"; paint(); }
      const t0 = Date.now();
      const run = await api("POST", `/api/studio/runs/${S.run.id}/step`);
      await sleep(Math.max(0, 520 - (Date.now() - t0)));
      S.run = run; paint();
      await sleep(160);
    }
  } catch (e) { toast(e.message, true); }
  S.running = false; updateRunButton();
  if (!S.run) return;
  if (S.run.status === "done") toast("Run finished: every node done.");
  else if (S.run.status === "failed") toast("Run stopped: " + (S.run.error || "a node failed"), true);
  else if (S.run.status === "waiting") toast(`Waiting for ${S.run.waiting_for.approver_name} to approve ${S.run.waiting_for.doc_no}.`);
}

// ------------------------------------------------------------------------------------------------ saving
function setSaved(t) { $("#saveState").textContent = t; }
function markDirty() {
  setSaved("Unsaved");
  clearTimeout(S.saveTimer);
  S.saveTimer = setTimeout(save, 900);
}
async function save() {
  if (!S.wf) return [];
  clearTimeout(S.saveTimer);
  setSaved("Saving…");
  try {
    const r = await api("PUT", `/api/studio/workflows/${encodeURIComponent(S.wf.id)}`, S.wf);
    showProblems(r.problems || []);
    setSaved("Saved");
    const w = S.wfs.find(x => x.id === S.wf.id);
    if (w) w.name = S.wf.name;
    return r.problems || [];
  } catch (e) { setSaved("Not saved"); toast(e.message, true); return [e.message]; }
}
function showProblems(list) {
  const p = $("#problems");
  p.hidden = !list.length;
  p.textContent = list.length === 1 ? "1 problem" : `${list.length} problems`;
  p.title = list.join("\n");
}

// ------------------------------------------------------------------------------------------------ top bar
function bindTop() {
  $("#btnRun").onclick = runWorkflow;
  $("#btnSave").onclick = async () => { await save(); toast("Saved."); };
  $("#btnTemplates").onclick = () => openTemplates(false);
  $("#btnRuns").onclick = () => openInspector("run");
  $("#paletteSearch").oninput = buildPalette;
  const name = $("#wfName");
  name.addEventListener("mousedown", e => e.stopPropagation());
  name.addEventListener("click", e => e.stopPropagation());
  name.addEventListener("input", () => { if (S.wf) { S.wf.name = name.value; markDirty(); } });
  name.addEventListener("keydown", e => { if (e.key === "Enter") name.blur(); });
  $("#wfMenuBtn").onclick = e => { e.stopPropagation(); toggleWfMenu(); };
  document.addEventListener("click", e => {
    if (!e.target.closest("#wfMenu")) $("#wfMenu").classList.remove("open");
    if (!e.target.closest("#picker") && !e.target.closest(".ref")) hidePicker();
  });
}
async function toggleWfMenu() {
  const m = $("#wfMenu");
  if (m.classList.contains("open")) return m.classList.remove("open");
  S.wfs = await api("GET", "/api/studio/workflows");
  m.innerHTML = "";
  for (const w of S.wfs) m.append(h("div", {class: "mi" + (S.wf?.id === w.id ? " cur" : ""), onclick: () => { m.classList.remove("open"); loadWorkflow(w.id); }},
    h("span", {class: "ico c-trigger", html: svg("branch")}), h("span", {}, w.name, h("small", {}, `${w.nodes} nodes`))));
  m.append(h("hr"), h("div", {class: "mi", onclick: () => { m.classList.remove("open"); newBlank(); }}, "New blank workflow"),
           h("div", {class: "mi", onclick: () => { m.classList.remove("open"); openTemplates(false); }}, "New from a template…"));
  if (S.wf) m.append(h("div", {class: "mi", style: "color:var(--red)", onclick: async () => {
    m.classList.remove("open");
    if (!confirm(`Delete “${S.wf.name}”?`)) return;
    await api("DELETE", `/api/studio/workflows/${encodeURIComponent(S.wf.id)}`);
    S.wfs = await api("GET", "/api/studio/workflows");
    if (S.wfs.length) loadWorkflow(S.wfs[0].id); else { S.wf = null; render(); openTemplates(true); }
  }}, "Delete this workflow"));
  m.classList.add("open");
}
async function newBlank() {
  const wf = await api("POST", "/api/studio/workflows", {name: "Untitled workflow", description: "",
    nodes: [{id: "start", type: "trigger", title: "Manual start", x: 40, y: 220, config: {kind: "manual"}}], edges: []});
  await loadWorkflow(wf.id);
  select("start");
}

// ------------------------------------------------------------------------------------------------ sheets
function openSheet(content, narrow) {
  const sh = $("#sheet");
  sh.className = "sheet" + (narrow ? " narrow" : "");
  sh.innerHTML = ""; sh.append(...[content].flat());
  $("#scrim").hidden = false;
  $("#scrim").onclick = e => { if (e.target.id === "scrim") closeSheet(); };
}
function closeSheet() { $("#scrim").hidden = true; if (S._sheetResolve) { S._sheetResolve(null); S._sheetResolve = null; } }

async function openTemplates(welcome) {
  const list = await api("GET", "/api/studio/templates");
  const kinds = {manual: "Manual", form: "Form", event: "Event", chat: "Chat", schedule: "Schedule"};
  const card = (t, i) => h("div", {class: "tcard" + (i === 0 ? " hero" : ""), "data-template": t.id, onclick: () => useTemplate(t.id)},
    h("span", {class: "tkind"}, `${kinds[t.trigger] || t.trigger} trigger · ${t.nodes} nodes`),
    h("h3", {}, t.name), h("p", {}, t.description),
    h("div", {class: "tsteps"}, ...t.steps.map((s, j) => h("b", {class: "tstep"}, j ? h("i", {}, "→") : null, h("span", {}, s)))));
  openSheet([
    h("h2", {}, welcome ? "Welcome to the Workflow Studio" : "Templates"),
    h("p", {class: "lede"}, "Stitch Rasoi's tools into workflows, and build agents of your own. Every template runs on your own Rasoi, as Kavita, Rohit or Neha, with their own permissions."),
    h("div", {class: "tgrid"}, ...list.map(card),
      h("div", {class: "tcard", onclick: () => { closeSheet(); newBlank(); }},
        h("span", {class: "tkind"}, "Blank"), h("h3", {}, "Start from scratch"),
        h("p", {}, "A manual trigger on an empty canvas. Drag tools in from the left and join them."))),
  ]);
}
async function useTemplate(tid) {
  try {
    const wf = await api("POST", `/api/studio/templates/${tid}/use`);
    closeSheet();
    await loadWorkflow(wf.id);
    toast(`“${wf.name}” is ready. Press Run.`);
  } catch (e) { toast(e.message, true); }
}

function formSheet(t) {
  return new Promise(resolve => {
    S._sheetResolve = resolve;
    const inputs = {};
    const fields = t.config.fields || [];
    openSheet([
      h("div", {class: "inbox-who"}, h("span", {class: "ico c-trigger", html: svg("form")}), "Form trigger"),
      h("h2", {}, t.title || "Form"),
      h("p", {class: "lede"}, "Fill it in; the run starts with these values as the trigger's output."),
      ...fields.map(f => h("div", {class: "field"}, h("label", {}, f.label || f.name, h("span", {class: "hint"}, `trigger.${f.name}`)),
        h("div", {class: "inp"}, inputs[f.name] = h("input", {value: f.default ?? "", type: f.type === "date" ? "date" : "text",
          inputmode: f.type === "number" ? "numeric" : null, "data-field": f.name})))),
      h("div", {class: "row"}, h("button", {class: "pill", onclick: () => closeSheet()}, "Cancel"),
        h("button", {class: "pill primary", id: "formStart", onclick: () => {
          const data = {};
          for (const f of fields) data[f.name] = inputs[f.name].value;
          S._sheetResolve = null; $("#scrim").hidden = true; resolve(data);
        }}, svg("play", 13), " Start the run")),
    ], true);
  });
}

async function openApproval() {
  const w = S.run?.waiting_for;
  if (!w) return;
  let doc = {};
  try { doc = await api("GET", `/api/studio/document?doc_no=${encodeURIComponent(w.doc_no)}&user=${w.approver}`); }
  catch (e) { return toast(e.message, true); }
  const p = S.people[w.approver] || {name: w.approver_name, role: ""};
  const initials = p.name.split(" ").map(x => x[0]).join("");
  const decide = async decision => {
    $$("#sheet button").forEach(b => b.disabled = true);
    try {
      S.run = await api("POST", `/api/studio/runs/${S.run.id}/approve`, {decision});
      closeSheet(); paint();
      toast(decision === "approve" ? `${p.name.split(" ")[0]} approved ${w.doc_no}.` : `${w.doc_no} rejected.`);
      await sleep(400);
      await autoStep();
    } catch (e) { toast(e.message, true); $$("#sheet button").forEach(b => b.disabled = false); }
  };
  const isPR = w.doc_no.toUpperCase().startsWith("PR");
  openSheet([
    h("div", {class: "inbox-who"}, h("span", {class: "avatar"}, initials), `${p.name}'s approvals inbox · ${p.role}`),
    h("h2", {}, isPR ? "A purchase request waits for you" : "A purchase order waits for you"),
    h("p", {class: "lede"}, `The workflow “${S.run.workflow_name}” is paused at “${node(w.node)?.title || w.node}”. It carries on when you sign.`),
    h("div", {class: "doc"},
      h("div", {class: "dh"}, h("b", {}, w.doc_no), h("span", {class: "stat waiting"}, doc.status || "WAITING FOR APPROVAL")),
      h("dl", {},
        h("dt", {}, "Item"), h("dd", {}, doc.item_code || "–"),
        h("dt", {}, "Quantity"), h("dd", {}, num(doc.quantity)),
        h("dt", {}, isPR ? "Estimated value" : "Gross value"), h("dd", {}, inr(doc.estimated_value ?? doc.gross_value)),
        h("dt", {}, "Cost centre"), h("dd", {}, doc.cost_centre || "–"),
        h("dt", {}, "Need by"), h("dd", {}, doc.need_by || "–"),
        h("dt", {}, "Raised by"), h("dd", {}, S.people[doc.created_by || "KJOSHI"]?.name || doc.created_by || "Kavita Joshi"))),
    h("div", {class: "row"},
      h("button", {class: "pill", onclick: () => closeSheet()}, "Later"),
      isPR ? h("button", {class: "pill danger", onclick: () => decide("reject")}, "Reject") : null,
      h("button", {class: "pill violet", id: "approveBtn", onclick: () => decide("approve")}, svg("seal", 15), ` Approve as ${p.name.split(" ")[0]}`)),
  ], true);
}

// ------------------------------------------------------------------------------------------------ inspector
function openInspector(tab) {
  S.tab = tab || "config";
  const wasHidden = $("#inspector").hidden;
  $("#inspector").hidden = false;
  $("#canvas").classList.add("with-insp");
  renderInspector();
  if (wasHidden && S.wf) {
    // keep the selected node in view when the panel slides over the canvas
    const n = S.sel && node(S.sel), r = $("#canvas").getBoundingClientRect();
    if (n) { const sx = n.x * S.view.k + S.view.x; if (sx + NODE_W * S.view.k > r.width - 420) { S.view.x -= sx + NODE_W * S.view.k - (r.width - 440); applyView(); } }
  }
}
function closeInspector() { $("#inspector").hidden = true; $("#canvas").classList.remove("with-insp"); }
function renderInspector() {
  const tabs = $("#itabs"), body = $("#ibody");
  const n = S.sel && node(S.sel);
  const isChat = trigger()?.config?.kind === "chat";
  const avail = [];
  if (n) avail.push(["config", "Configure"]);
  if (n && S.run?.nodes?.[n.id]?.output) avail.push(["output", "Output"]);
  avail.push(["run", "Run"]);
  if (isChat) avail.push(["chat", "Chat"]);
  if (!avail.some(a => a[0] === S.tab)) S.tab = avail[0][0];
  tabs.innerHTML = "";
  for (const [k, label] of avail) tabs.append(h("button", {class: "itab" + (S.tab === k ? " on" : ""), "data-tab": k,
    onclick: () => { S.tab = k; renderInspector(); }}, label));
  tabs.append(h("button", {class: "x", title: "Close", onclick: () => { closeInspector(); }}, "×"));
  body.innerHTML = ""; body.style.display = ""; body.style.flexDirection = "";
  S.ivToken = (S.ivToken || 0) + 1;
  if (S.tab === "config" && n) configView(n, body);
  else if (S.tab === "output" && n) outputView(n, body);
  else if (S.tab === "chat") chatView(body);
  else runView(body);
}

// generic form controls ------------------------------------------------------------------------
function changed(n, rerenderPanel) {
  renderNode(n); renderEdges(); markDirty();
  if (rerenderPanel) renderInspector();
}
function textField(label, value, onInput, o = {}) {
  const tag = o.multiline ? "textarea" : "input";
  const inp = h(tag, {value: o.multiline ? null : (value ?? ""), placeholder: o.placeholder || "", rows: o.rows || null,
                      "data-field": o.key || label, inputmode: o.numeric ? "decimal" : null});
  if (o.multiline) inp.value = value ?? "";
  const mark = () => inp.classList.toggle("tpl", String(inp.value).includes("{{"));
  mark();
  inp.addEventListener("input", () => { mark(); onInput(inp.value); });
  const wrap = h("div", {class: "inp"}, inp);
  if (o.picker) wrap.append(h("button", {class: "ref", title: "Use an earlier node's output", type: "button",
    onclick: e => { e.stopPropagation(); openPicker(wrap, inp); }}, "{ }"));
  return h("div", {class: "field"}, h("label", {}, label, o.required ? h("span", {class: "req"}, "*") : null,
    o.hint ? h("span", {class: "hint"}, o.hint) : null), wrap);
}
function seg(options, value, onPick) {
  const box = h("div", {class: "seg"});
  for (const [v, label, small] of options) box.append(h("button", {class: v === value ? "on" : "", type: "button", "data-value": v,
    onclick: () => { $$("button", box).forEach(b => b.classList.toggle("on", b.dataset.value === v)); onPick(v); }},
    label, small ? h("small", {}, small) : null));
  return box;
}
function toggle(title, desc, value, onSet, key) {
  const el = h("div", {class: "toggle" + (value ? " on" : ""), "data-toggle": key || title},
    h("span", {class: "sw"}), h("span", {}, h("b", {}, title), h("small", {}, desc)));
  el.onclick = () => { const on = !el.classList.contains("on"); el.classList.toggle("on", on); onSet(on); };
  return el;
}
const peopleSeg = (value, onPick, only) => seg(Object.entries(S.people).filter(([k]) => !only || only.includes(k))
  .map(([k, p]) => [k, p.name.split(" ")[0], p.role]), value, onPick);
const parseVal = (v, type) => {
  if (typeof v !== "string") return v;
  if (v.includes("{{")) return v;
  if ((type === "integer" || type === "number") && /^-?\d+(\.\d+)?$/.test(v.replace(/,/g, "").trim())) return Number(v.replace(/,/g, ""));
  return v;
};

function configView(n, body) {
  const c = n.config;
  body.append(h("div", {class: "ihead"}, h("span", {class: "ico c-" + cat(n), html: svg(iconName(n))}),
    h("div", {style: "flex:1;min-width:0"},
      h("input", {value: n.title || "", "data-field": "title", oninput: e => { n.title = e.target.value; changed(n); }}),
      h("small", {}, `${n.type === "tool" ? "Tool" : n.type[0].toUpperCase() + n.type.slice(1)} node · id `, h("code", {}, n.id)))));
  const T = {trigger: triggerConfig, tool: toolConfig, condition: conditionConfig, approval: approvalConfig, llm: llmConfig,
             agent: agentConfig, message: messageConfig, set: setConfig}[n.type];
  T(n, c, body);
  body.append(h("div", {class: "ifoot"},
    h("button", {class: "pill small danger", onclick: () => deleteNode(n.id)}, "Delete node"),
    h("span", {class: "grow", style: "flex:1"}),
    S.run?.nodes?.[n.id]?.output ? h("button", {class: "pill small", onclick: () => { S.tab = "output"; renderInspector(); }}, "Last output") : null));
}
function toolConfig(n, c, body) {
  const t = S.tools[c.tool];
  body.append(h("p", {class: "idesc"}, t.description));
  body.append(h("div", {class: "sec"}, "Run as"), peopleSeg(c.as || "KJOSHI", v => { c.as = v; changed(n); }));
  body.append(h("p", {class: "note"}, "The tool runs with this person's own Bahi permissions, nothing more."));
  const props = t.input_schema.properties || {}, req = t.input_schema.required || [];
  const fields = Object.entries(props).filter(([k]) => k !== "confirm");
  if (fields.length) body.append(h("div", {class: "sec"}, "Inputs"));
  c.args = c.args || {};
  for (const [k, p] of fields) {
    const cur = c.args[k];
    if (p.enum) {
      body.append(h("div", {class: "field"}, h("label", {}, k, req.includes(k) ? h("span", {class: "req"}, "*") : null, h("span", {class: "hint"}, p.description || "")),
        seg(p.enum.map(v => [v, v]), cur, v => { c.args[k] = v; changed(n); })));
    } else if (p.type === "boolean") {
      body.append(toggle(k, p.description || "", !!cur, v => { c.args[k] = v; changed(n); }));
    } else {
      body.append(textField(k, cur == null ? "" : String(cur), v => {
        if (v === "") delete c.args[k]; else c.args[k] = parseVal(v, p.type);
        changed(n);
      }, {picker: true, required: req.includes(k), hint: p.description, numeric: p.type === "integer" || p.type === "number", key: k,
          placeholder: t.example && t.example[k] != null ? `e.g. ${t.example[k]}` : ""}));
    }
  }
  if ("confirm" in props) {
    body.append(h("div", {class: "sec"}, "Commit"));
    body.append(toggle("Commit to Bahi (confirm = true)", c.confirm ? "Saves the document in Bahi and returns a receipt." :
      "Off: preview only. Bahi checks it and shows value and approver; nothing is saved.", !!c.confirm,
      v => { c.confirm = v; changed(n, true); }, "confirm"));
  }
  if (t.writes) body.append(toggle("Stop on a warning", "If Bahi warns (e.g. a closed cost centre saves a silent DRAFT), stop the run so a person looks.",
    c.stop_on_warning !== false, v => { c.stop_on_warning = v; changed(n); }, "stop_on_warning"));
}
function triggerConfig(n, c, body) {
  body.append(h("div", {class: "sec"}, "Starts when"));
  body.append(seg(Object.entries(KIND_LABEL).map(([k, l]) => [k, l.split(" ")[0] === "Stock" ? "Event" : l.split(" ")[0]]), c.kind || "manual", v => {
    const keep = n.title; n.config = defaultConfig({type: "trigger", kind: v});
    if (!keep || Object.values(KIND_LABEL).includes(keep)) n.title = KIND_LABEL[v];
    changed(n, true); updateRunButton();
  }));
  const k = c.kind || "manual";
  if (k === "manual") {
    body.append(h("p", {class: "note"}, "Runs when you press Run. Optional start data, as JSON, is the trigger's output (trigger.<field>)."));
    const ta = textField("Start data (JSON)", JSON.stringify(c.data || {}, null, 2), v => {
      try { c.data = JSON.parse(v || "{}"); ta.querySelector(".inp").style.borderColor = ""; changed(n); }
      catch (e) { ta.querySelector(".inp").style.borderColor = "var(--red)"; }
    }, {multiline: true, rows: 6, key: "data"});
    body.append(ta);
  } else if (k === "form") {
    body.append(h("p", {class: "note"}, "Run opens this form; what is typed becomes trigger.<name>."));
    c.fields = c.fields || [];
    c.fields.forEach((f, i) => body.append(h("div", {class: "kv", style: "grid-template-columns:96px 1fr 84px 26px"},
      h("div", {class: "inp"}, h("input", {value: f.name, placeholder: "name", oninput: e => { f.name = e.target.value.replace(/\W/g, "_"); changed(n); }})),
      h("div", {class: "inp"}, h("input", {value: f.default ?? "", placeholder: f.label || "default", title: f.label,
        oninput: e => { f.default = f.type === "number" ? parseVal(e.target.value, "number") : e.target.value; changed(n); }})),
      h("div", {class: "inp"}, h("select", {onchange: e => { f.type = e.target.value; changed(n); }},
        ...["text", "number", "date"].map(t => h("option", {value: t, selected: f.type === t}, t)))),
      h("button", {class: "iconbtn", onclick: () => { c.fields.splice(i, 1); changed(n, true); }}, "×"))));
    body.append(h("button", {class: "addrow", onclick: () => { c.fields.push({name: "field" + (c.fields.length + 1), label: "", type: "text", default: ""}); changed(n, true); }}, "+ Add a field"));
  } else if (k === "event") {
    body.append(h("p", {class: "note"}, "Watches stock with check_stock. Fires for the first watched item below its reorder level; the trigger's output has item_code, free, on_order, reorder_level and cover_days."));
    body.append(textField("Items to watch", (c.item_codes || []).join(", "), v => {
      c.item_codes = v.split(/[,\s]+/).map(s => s.trim()).filter(Boolean); changed(n);
    }, {hint: "item codes, comma separated", key: "item_codes"}));
    body.append(h("div", {class: "sec"}, "Look as"), peopleSeg(c.as || "KJOSHI", v => { c.as = v; changed(n); }));
  } else if (k === "schedule") {
    body.append(h("div", {class: "sec"}, "Every"), seg([["hour", "Hour"], ["day", "Day"], ["week", "Week"]], c.every || "day", v => { c.every = v; changed(n); }));
    body.append(textField("At", c.at || "09:00", v => { c.at = v; changed(n); }, {key: "at"}));
    body.append(h("p", {class: "note"}, "Rasoi's sandbox clock stands at Monday 26 Oct 2026, so the scheduler fires when you press Run, or when the class scheduler ticks."));
  } else {
    body.append(h("p", {class: "idesc"}, "Each message in the Chat tab starts a run; the trigger's output is trigger.message (and the conversation so far). Join it to an Agent node."));
  }
}
function conditionConfig(n, c, body) {
  body.append(h("p", {class: "idesc"}, "Branch the run: it leaves by yes when the test is true, by no when it is false. The other side is skipped."));
  body.append(textField("If", c.if || "", v => { c.if = v; changed(n); }, {picker: true, key: "if", placeholder: "{{ nodes.stock.below_reorder }}",
    hint: "a test, e.g. {{ nodes.pr.estimated_value > 250000 }}"}));
}
function approvalConfig(n, c, body) {
  body.append(h("p", {class: "idesc"}, "Pauses the run until the approver signs in their inbox. The run is saved while it waits; nothing holds it in memory. If Bahi already approved the document (within the raiser's limit), it passes at once."));
  body.append(textField("Document", c.doc_no || "", v => { c.doc_no = v; changed(n); }, {picker: true, required: true, key: "doc_no",
    placeholder: "{{nodes.pr.request_no}}", hint: "a PR/ or PO/ number"}));
  body.append(h("div", {class: "sec"}, "Approver"), peopleSeg(c.approver || "RMEHTA", v => { c.approver = v; changed(n); }));
  body.append(h("p", {class: "note"}, "Bahi routes the request to the raiser's manager; the run shows who it really waits for."));
}
function llmConfig(n, c, body) {
  body.append(h("p", {class: "idesc"}, "One call to a language model: a prompt in, text or a JSON object out. Use {{ }} to put earlier outputs into the prompt."));
  body.append(textField("Prompt", c.prompt || "", v => { c.prompt = v; changed(n); }, {multiline: true, rows: 9, picker: true, key: "prompt"}));
  body.append(h("div", {class: "sec"}, "Output"), seg([["text", "Text"], ["json", "JSON object"]], c.output || "text", v => { c.output = v; changed(n, true); }));
  if (c.output === "json") body.append(textField("Fields", (c.fields || []).join(", "), v => {
    c.fields = v.split(/[,\s]+/).filter(Boolean); changed(n); }, {hint: "the keys you want back", key: "fields"}));
  body.append(modelField(n, c));
}
function modelField(n, c) {
  return h("div", {class: "field"}, h("label", {}, "Model"), h("div", {class: "inp"},
    h("select", {"data-field": "model", onchange: e => { c.model = e.target.value; changed(n); }},
      ...MODELS.map(m => h("option", {value: m, selected: (c.model || MODELS[0]) === m}, m.split(":").pop())))));
}
function agentConfig(n, c, body) {
  body.append(h("p", {class: "idesc"}, "Your own agent: a model in a loop with the tools you tick. It decides which tool to call next, reads the result, and stops when it can answer."));
  body.append(textField("Instructions", c.instructions || "", v => { c.instructions = v; changed(n); }, {multiline: true, rows: 6, key: "instructions"}));
  body.append(textField("Input", c.input || "{{ trigger.message }}", v => { c.input = v; changed(n); }, {picker: true, key: "input", hint: "what it is asked"}));
  body.append(h("div", {class: "sec"}, "Acts as"), peopleSeg(c.as || "KJOSHI", v => { c.as = v; changed(n); }));
  body.append(h("div", {class: "sec"}, `Tools it may use (${(c.tools || []).length})`));
  const box = h("div", {class: "checks"});
  for (const t of S.toolList) box.append(h("label", {class: "check"},
    h("input", {type: "checkbox", checked: (c.tools || []).includes(t.name), "data-tool": t.name, onchange: e => {
      c.tools = (c.tools || []).filter(x => x !== t.name);
      if (e.target.checked) c.tools.push(t.name);
      changed(n);
    }}), h("span", {}, t.title), h("small", {}, t.writes ? "writes" : t.category)));
  body.append(box);
  body.append(h("div", {class: "sec"}, "Safety"));
  body.append(toggle("May commit writes", c.may_commit ? "It previews first and commits only after you say yes." :
    "Off: every write is forced to a preview (confirm=false), whatever the model asks.", !!c.may_commit,
    v => { c.may_commit = v; changed(n, true); }, "may_commit"));
  body.append(modelField(n, c));
  body.append(textField("Max tool calls", String(c.max_steps || 10), v => { c.max_steps = parseInt(v) || 10; changed(n); }, {numeric: true, key: "max_steps"}));
}
function messageConfig(n, c, body) {
  body.append(textField("To", c.to || "", v => { c.to = v; changed(n); }, {picker: true, key: "to", hint: "@handle or email"}));
  body.lastChild.append(h("div", {class: "chips"}, ...["@rohit", "@kavita", "@suresh", "@anand"].map(x =>
    h("button", {class: "chip", onclick: () => { c.to = x; changed(n, true); }}, x))));
  body.append(textField("Message", c.text || "", v => { c.text = v; changed(n); }, {multiline: true, rows: 5, picker: true, key: "text"}));
  body.append(h("div", {class: "sec"}, "Send as"), peopleSeg(c.as || "KJOSHI", v => { c.as = v; changed(n); }));
  body.append(h("p", {class: "note"}, "Goes through Bahi's notification queue as this person. Stores (Neha) may not send messages."));
}
function setConfig(n, c, body) {
  body.append(h("p", {class: "idesc"}, "Compute named values from earlier outputs. Later nodes read them as nodes." + n.id + ".<name>."));
  c.values = c.values || {};
  Object.entries(c.values).forEach(([k, v]) => {
    let key = k;
    const row = h("div", {class: "kv"},
      h("div", {class: "inp"}, h("input", {value: k, onchange: e => {
        const nv = {}; for (const [a, b] of Object.entries(c.values)) nv[a === key ? e.target.value : a] = b;
        c.values = nv; key = e.target.value; changed(n);
      }})), null,
      h("button", {class: "iconbtn", onclick: () => { delete c.values[key]; changed(n, true); }}, "×"));
    const f = textField("", typeof v === "string" ? v : JSON.stringify(v), val => { c.values[key] = parseVal(val, "number"); changed(n); }, {picker: true, key: "value:" + k});
    f.style.margin = "0"; f.querySelector("label").remove();
    row.children[1] ? row.insertBefore(f, row.children[1]) : row.append(f);
    body.append(row);
  });
  body.append(h("button", {class: "addrow", onclick: () => { let i = 1; while (("value" + i) in c.values) i++; c.values["value" + i] = ""; changed(n, true); }}, "+ Add a value"));
}

// output picker ------------------------------------------------------------------------------
function upstream(id) {
  const seen = new Set(), queue = [id], out = [];
  while (queue.length) {
    const cur = queue.shift();
    for (const e of S.wf.edges) if (e.to === cur && !seen.has(e.from)) { seen.add(e.from); out.push(e.from); queue.push(e.from); }
  }
  return out.map(node).filter(Boolean).sort((a, b) => a.x - b.x);
}
function knownFields(n) {
  const rec = S.run?.nodes?.[n.id];
  if (rec && rec.output && typeof rec.output === "object") {
    const f = [];
    for (const [k, v] of Object.entries(rec.output)) {
      if (Array.isArray(v) && v.length && typeof v[0] === "object") for (const kk of Object.keys(v[0]).slice(0, 6)) f.push([`${k}[0].${kk}`, v[0][kk]]);
      else if (v && typeof v === "object" && !Array.isArray(v)) for (const kk of Object.keys(v).slice(0, 8)) f.push([`${k}.${kk}`, v[kk]]);
      else f.push([k, v]);
    }
    return f;
  }
  const c = n.config || {};
  switch (n.type) {
    case "tool": return Object.entries(S.tools[c.tool]?.output_schema?.properties || {}).filter(([k]) => k !== "ok").map(([k, p]) => [k, p.description || p.type]);
    case "trigger": return c.kind === "form" ? (c.fields || []).map(f => [f.name, f.label || f.type]) :
      c.kind === "event" ? ["item_code", "free", "on_order", "reorder_level", "cover_days"].map(k => [k, ""]) :
      c.kind === "chat" ? [["message", "the user's message"]] : c.kind === "schedule" ? [["fired_at", ""]] :
      Object.keys(c.data || {}).map(k => [k, c.data[k]]);
    case "approval": return [["doc_no", ""], ["status", ""], ["approved_by", ""], ["waited", ""]];
    case "condition": return [["branch", "true or false"], ["value", ""]];
    case "llm": return c.output === "json" ? (c.fields || []).map(f => [f, ""]) : [["text", "the reply"]];
    case "agent": return [["reply", "the answer"], ["steps", "tool calls made"]];
    case "message": return [["to", ""], ["text", ""], ["queued", ""]];
    case "set": return Object.keys(c.values || {}).map(k => [k, c.values[k]]);
  }
  return [];
}
function openPicker(anchor, input) {
  const pk = $("#picker");
  pk.innerHTML = "";
  const ups = upstream(S.sel);
  if (!ups.length) pk.append(h("div", {class: "none"}, "Join this node to earlier nodes first; their outputs appear here."));
  for (const u of ups) {
    const base = u.type === "trigger" ? "trigger" : `nodes.${u.id}`;
    pk.append(h("h5", {}, h("span", {class: "ico c-" + cat(u), style: "width:18px;height:18px;border-radius:6px", html: svg(iconName(u), 11)}), u.title || u.id,
      S.run?.nodes?.[u.id]?.output ? " · last run" : ""));
    const f = knownFields(u);
    if (!f.length) pk.append(h("div", {class: "none"}, "No fields yet."));
    for (const [k, v] of f) pk.append(h("div", {class: "pk", "data-path": `${base}.${k}`, onclick: () => {
      const tok = `{{${base}.${k}}}`;
      const s = input.selectionStart ?? input.value.length, e = input.selectionEnd ?? s;
      input.value = input.value.slice(0, s) + tok + input.value.slice(e);
      input.dispatchEvent(new Event("input"));
      input.focus(); hidePicker();
    }}, h("b", {style: "font-weight:500"}, `${base === "trigger" ? "trigger" : u.id}.${k}`), h("span", {}, v == null ? "" : typeof v === "object" ? JSON.stringify(v) : String(v))));
  }
  pk.append(h("h5", {}, "Run"), h("div", {class: "pk", "data-path": "today", onclick: () => {
    input.value += "{{today}}"; input.dispatchEvent(new Event("input")); hidePicker(); }}, h("b", {style: "font-weight:500"}, "today"), h("span", {}, "the Rasoi sandbox date")));
  const r = anchor.getBoundingClientRect();
  pk.hidden = false;
  pk.style.left = Math.max(12, r.right - 340) + "px";
  pk.style.top = Math.min(window.innerHeight - 390, r.bottom + 6) + "px";
}
function hidePicker() { $("#picker").hidden = true; }

// output, run and chat views ------------------------------------------------------------------
function jsonHTML(v) {
  const s = esc(JSON.stringify(v, null, 2) ?? "null");
  return s.replace(/(&quot;(?:[^&]|&(?!quot;))*?&quot;)(\s*:)?|\b(true|false)\b|\bnull\b|-?\b\d+(?:\.\d+)?\b/g, (m, str, colon, bool) => {
    if (str) return colon ? `<span class="j-k">${str}</span>${colon}` : `<span class="j-s">${str}</span>`;
    if (bool) return `<span class="j-b">${m}</span>`;
    if (m === "null") return `<span class="j-z">null</span>`;
    return `<span class="j-n">${m}</span>`;
  });
}
function outputView(n, body) {
  const rec = S.run.nodes[n.id];
  body.append(h("div", {class: "ihead"}, h("span", {class: "ico c-" + cat(n), html: svg(iconName(n))}),
    h("div", {}, h("b", {style: "font-size:17px;font-weight:540"}, n.title || n.id), h("small", {}, `nodes.${n.id}`))));
  body.append(h("div", {}, h("span", {class: "stat " + rec.status}, rec.status), rec.seconds != null ? h("span", {class: "meta"}, `  ${rec.seconds}s`) : null));
  if (rec.summary) body.append(h("div", {class: "summary"}, rec.summary));
  if (rec.status === "waiting") body.append(h("button", {class: "pill violet", style: "margin:6px 0", onclick: openApproval}, svg("seal", 15), " Open approval"));
  if (rec.meta) body.append(h("div", {class: "meta"}, [rec.meta.model, rec.meta.tokens_in != null ? `${rec.meta.tokens_in} in / ${rec.meta.tokens_out} out tokens` : "",
    rec.meta.replayed ? "replayed from the cassette" : "", rec.meta.cost_inr ? `₹${rec.meta.cost_inr}` : ""].filter(Boolean).join(" · ")));
  if (n.type === "agent" && rec.output?.tool_calls?.length) {
    body.append(h("div", {class: "sec"}, "Tool calls"));
    body.append(h("ul", {class: "timeline"}, ...rec.output.tool_calls.map(c => h("li", {}, h("span", {class: "d " + (c.ok ? "done" : "error")}),
      h("span", {}, h("b", {}, c.tool), h("small", {}, c.summary))))));
  }
  if (rec.inputs) { body.append(h("div", {class: "sec"}, "Input (templates filled)")); body.append(h("pre", {class: "json", html: jsonHTML(rec.inputs)})); }
  body.append(h("div", {class: "sec"}, "Output"));
  body.append(h("pre", {class: "json", "data-output": n.id, html: jsonHTML(rec.output)}));
}
async function runView(body) {
  const r = S.run;
  if (r) {
    body.append(h("div", {class: "ihead"}, h("span", {class: "ico c-trigger", html: svg("play")}),
      h("div", {}, h("b", {style: "font-size:17px;font-weight:540"}, `Run ${r.id.replace("run-", "#")}`),
        h("small", {}, `${r.workflow_name} · started ${r.started.slice(11, 19)}`))));
    body.append(h("div", {}, h("span", {class: "stat " + r.status, id: "runStatus"}, r.status)));
    if (r.status === "waiting" && r.waiting_for) {
      const w = r.waiting_for;
      body.append(h("div", {class: "waitcard"}, h("b", {}, `Waiting for ${w.approver_name}`),
        h("p", {}, `${w.doc_no} is in ${w.approver_name.split(" ")[0]}'s approvals inbox. The run is saved; it carries on from “${node(w.node)?.title || w.node}” once it is signed.`),
        h("div", {style: "display:flex;gap:8px"}, h("button", {class: "pill small violet", onclick: openApproval}, "Open approval"),
          h("button", {class: "pill small", title: "Re-read the status from Bahi (if it was signed in the experience inbox)", onclick: async () => {
            S.run = await api("POST", `/api/studio/runs/${r.id}/resume`); paint();
            if (S.run.status === "running") autoStep(); else toast("Still waiting: nobody has signed yet.");
          }}, "Check again"))));
    }
    if (r.status === "failed" && r.error) body.append(h("div", {class: "summary", style: "background:var(--red-soft);color:#8c1d18"}, r.error));
    body.append(h("div", {class: "sec"}, "Run log"));
    const titles = Object.fromEntries(r.workflow.nodes.map(n => [n.id, n.title || n.id]));
    body.append(h("ul", {class: "timeline"}, ...r.log.map(e => h("li", {onclick: () => { if (e.node && node(e.node)) select(e.node, "output"); }},
      h("span", {class: "d " + e.event}), h("span", {}, h("b", {}, e.node ? titles[e.node] : (e.event === "started" ? "Started" : e.event === "done" ? "Finished" : "Stopped")),
        h("small", {}, e.text))))));
  } else {
    body.append(h("p", {class: "idesc"}, "No run on the canvas. Press Run; each node lights up as it runs, and its output appears here."));
  }
  if (!S.wf) return;
  const token = S.ivToken;
  const list = await api("GET", `/api/studio/runs?workflow_id=${encodeURIComponent(S.wf.id)}`);
  if (!list.length || S.tab !== "run" || token !== S.ivToken) return;
  body.append(h("div", {class: "sec"}, "Earlier runs"));
  body.append(h("div", {class: "runlist"}, ...list.slice(0, 12).map(x => h("div", {class: "ri", onclick: async () => {
    S.run = await api("GET", `/api/studio/runs/${x.id}`); paint(); renderInspector(); }},
    h("span", {}, `${x.id.replace("run-", "#")} · ${x.started.slice(11, 19)}`), h("span", {class: "stat " + x.status}, x.status)))));
}
async function chatView(body) {
  const agent = S.wf.nodes.find(n => n.type === "agent");
  body.append(h("div", {class: "ihead"}, h("span", {class: "ico c-ai", html: svg("agent")}),
    h("div", {}, h("b", {style: "font-size:17px;font-weight:540"}, agent?.title || "Chat"),
      h("small", {}, agent ? `${(agent.config.tools || []).length} tools · acts as ${first(agent.config.as)}` : "Add an Agent node"))));
  const chat = h("div", {class: "chat"}), msgs = h("div", {class: "msgs", id: "chatMsgs"});
  const ta = h("textarea", {placeholder: "Message your agent…", id: "chatInput"});
  const sendBtn = h("button", {class: "pill primary", id: "chatSend"}, "Send");
  chat.append(msgs, h("div", {class: "chatin"}, ta, sendBtn));
  body.append(chat);
  body.style.display = "flex"; body.style.flexDirection = "column";
  chat.style.flex = "1";
  const draw = () => {
    msgs.innerHTML = "";
    if (!S.chat.length) msgs.append(h("div", {class: "suggest"}, h("div", {class: "note"}, "Try:"),
      ...["How many days of cover do we have for the 5 litre silicone gasket?", "Is cost centre PRD-05 open?",
          "Can we buy gaskets from a supplier without a food-grade certificate?"].map(q => h("button", {onclick: () => { ta.value = q; send(); }}, q))));
    for (const m of S.chat) {
      const el = h("div", {class: "msg " + m.role}, m.content);
      if (m.calls?.length) el.append(h("div", {class: "calls"}, ...m.calls.map(c => h("span", {class: "call" + (c.ok ? "" : " bad"), title: c.summary},
        c.tool + (c.args?.confirm ? " · commit" : "")))));
      msgs.append(el);
    }
    msgs.scrollTop = msgs.scrollHeight;
  };
  const send = async () => {
    const text = ta.value.trim();
    if (!text || S.running) return;
    ta.value = ""; S.chat.push({role: "user", content: text});
    draw(); msgs.append(h("div", {class: "msg assistant typing"}, "Thinking…"));
    S.running = true; updateRunButton();
    if (agent) { S.run = {status: "running", nodes: Object.fromEntries(S.wf.nodes.map(n => [n.id, {status: n.type === "trigger" ? "done" : n.id === agent.id ? "running" : "pending"}])), edges_taken: [], workflow: S.wf, log: []}; paint(); }
    try {
      const r = await api("POST", `/api/studio/workflows/${encodeURIComponent(S.wf.id)}/chat`, {message: text});
      S.run = r.run;
      const calls = agent && r.run.nodes[agent.id]?.output?.tool_calls || [];
      S.chat.push({role: "assistant", content: r.reply, calls});
    } catch (e) { S.chat.push({role: "assistant", content: "Error: " + e.message}); S.run = null; }
    S.running = false; updateRunButton();
    for (const n of S.wf.nodes) paintNode(n.id);
    renderEdges(); paintRunbar();
    draw();
  };
  sendBtn.onclick = send;
  ta.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
  if (!S.chat.length) {
    const hist = (await api("GET", `/api/studio/workflows/${encodeURIComponent(S.wf.id)}/chat`)).history || [];
    S.chat = hist.map(m => ({...m}));
  }
  draw();
  body.append(h("div", {style: "padding-top:8px"}, h("button", {class: "pill small ghost", onclick: async () => {
    await api("DELETE", `/api/studio/workflows/${encodeURIComponent(S.wf.id)}/chat`); S.chat = []; draw(); }}, "New conversation")));
  ta.focus();
}

window.__studio = S;  // for tests and the curious
boot().catch(e => toast(e.message, true));
})();
