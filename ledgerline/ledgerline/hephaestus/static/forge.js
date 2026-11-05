/* Hephaestus: the forge page. Six tabs on one page; everything comes from the API (no numbers are made up here). */
(() => {
'use strict';
const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => [...(r || document).querySelectorAll(s)];
const E = HX.esc;
let CAT = null, ME = null, TAB = 'anvil', busy = false, liveT = null, liveSince = 0, lastHits = [];
const SHOWN = (n) => (ME.config.tools[n].name === 'legacy' ? CAT.legacy_names[n] : n);
const T = (n) => CAT.tools.find((t) => t.name === n);
const KN = (id) => CAT.knobs.tool_knobs.find((k) => k.id === id) || {};
const clone = (o) => JSON.parse(JSON.stringify(o));
const pl = (n, w) => `${HX.num(n)} ${w}${n === 1 ? '' : 's'}`;

/* ------------------------------------------------------------------ start */
async function boot() {
  CAT = await HX.api('/api/catalog');
  if (HX.key()) {
    try { ME = await HX.api('/api/me'); welcome(); return; } catch (e) { if (e.status === 401) HX.forget(); }
  }
}
function welcome() {
  $('#joinform').classList.add('hide'); $('#keyline').classList.add('hide');
  $('#welcome').classList.remove('hide'); $('#wname').textContent = ME.name;
  $('h1').textContent = `${ME.name.split(' ')[0]}, your forge is lit.`;
  enter(location.hash.replace('#', '') || null, true);
}
function enter(tab, quiet) {
  $('#app').classList.remove('hide'); $('#nav').classList.remove('hide');
  $('#navname').textContent = ME.name;
  if (!quiet || tab) show(tab || 'anvil');
  else show('anvil', true);
}
$('#joinform').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const name = $('#name').value.trim(); if (name.length < 2) return;
  $('#joinbtn').disabled = true;
  try { ME = await HX.api('/api/join', { name }); HX.setKey(ME.key); welcome(); show('anvil'); }
  catch (e) { HX.toast(e.message); } finally { $('#joinbtn').disabled = false; }
});
$('#usekey').addEventListener('click', async (ev) => {
  ev.preventDefault();
  const k = (prompt('Paste your forge key (it starts with hx-; it is the last part of your MCP address):') || '').trim().split('/').pop();
  if (!k) return; HX.setKey(k);
  try { ME = await HX.api('/api/me'); welcome(); } catch (e) { HX.forget(); HX.toast('No forge with that key.'); }
});
$('#notme').addEventListener('click', (ev) => { ev.preventDefault(); HX.forget(); location.hash = ''; location.reload(); });
$('#enter').addEventListener('click', (ev) => { ev.preventDefault(); show('anvil'); });
$$('#nav a[data-tab]').forEach((a) => a.addEventListener('click', (ev) => { ev.preventDefault(); show(a.dataset.tab); }));
window.addEventListener('hashchange', () => { const t = location.hash.replace('#', ''); if (ME && t && t !== TAB && $('#tab-' + t)) show(t); });

function show(tab, noScroll) {
  if (!$('#tab-' + tab)) tab = 'anvil';
  TAB = tab;
  $$('section.tab').forEach((s) => s.classList.toggle('hide', s.dataset.tab !== tab));
  $$('#nav a[data-tab]').forEach((a) => a.classList.toggle('on', a.dataset.tab === tab));
  if (location.hash !== '#' + tab) history.replaceState(null, '', '#' + tab);
  ({ anvil: renderAnvil, ask: renderAsk, exp: renderExp, shield: renderShield, connect: renderConnect, prod: renderProd })[tab]();
  if (!noScroll) $('#tab-' + tab).scrollIntoView({ behavior: 'instant', block: 'start' });
  clearInterval(liveT); liveT = null;
  if (tab === 'connect') { pollLive(); liveT = setInterval(pollLive, 3000); }
}

async function saveConfig(cfg, msg) {
  try {
    const r = await HX.api('/api/config', { config: cfg });
    ME = r;
    if (msg) HX.toast(msg);
    return r;
  } catch (e) { HX.toast(e.message); throw e; }
}
async function knob(n, k, v) {
  const c = clone(ME.config); c.tools[n][k] = v;
  await saveConfig(c); renderAnvil();
}

/* ------------------------------------------------------------------ 1 · the anvil */
function pills(opts, cur, on, cls) {
  return `<span class="pills">${opts.map(([v, l]) => `<button class="pill sm ${cls || ''}${String(v) === String(cur) ? ' on' : ''}" data-v="${E(v)}">${E(l)}</button>`).join('')}</span>`;
}
function bindPills(root, sel, fn) {
  $$(sel + ' .pill', root).forEach((b) => b.addEventListener('click', () => fn(b.dataset.v)));
}
function edited(n) { return ME.versions[n] !== T(n).shipped._meta['ledgerline/version']; }

function renderAnvil() {
  const on = CAT.tools.filter((t) => ME.config.tools[t.name].on).map((t) => t.name);
  const cnt = on.length;
  $('#countpills').innerHTML = pills([['2', '2'], ['7', '7'], ['16', '16']], ['2', '7', '16'].includes(String(cnt)) ? cnt : '', null);
  $('#countline').textContent = `${cnt} on now. ${KN('on').line || ''}`;
  bindPills($('.toolbar'), '#countpills', async (v) => {
    const c = clone(ME.config);
    const want = v === '2' ? ['find_item', 'check_stock'] : v === '7' ? CAT.starter : CAT.tools.map((t) => t.name);
    CAT.tools.forEach((t) => { c.tools[t.name].on = want.includes(t.name); });
    await saveConfig(c, `${v} tools switched on`); renderAnvil();
  });
  $('#changed').innerHTML = ME.changed.length ? ME.changed.map((d) => `<span class="chip info">${E(d)}</span>`).join('')
    : '<span class="chip mute">Shipped toolbox: nothing changed yet</span>';
  $('#cards').innerHTML = on.map(card).join('');
  on.forEach(bindCard);
  const off = CAT.tools.filter((t) => !ME.config.tools[t.name].on);
  $('#more').innerHTML = off.map((t) => `<div class="mini"><div><div class="nm">${E(t.name)}</div><div class="tt">${E(t.title)}${t.writes ? ' · writes' : ''}</div></div>
    <label class="switch"><input type="checkbox" data-on="${E(t.name)}"></label></div>`).join('') || '<p class="muted small">Every tool is on.</p>';
  $$('#more input[data-on]').forEach((i) => i.addEventListener('change', () => knob(i.dataset.on, 'on', true)));
  const ed = on.filter(edited);
  const last = ME.runs[ME.runs.length - 1];
  $('#tk-anvil').innerHTML = `<h3>Your takeaway</h3><p>${cnt} tools on; ${ed.length ? `${ed.length} reshaped (${ed.map(E).join(', ')}), each with a new version in tools/list` : 'none reshaped yet'}. `
    + `Every knob above changes only what the model reads or what comes back; the services in “What runs” never change.`
    + (last ? ` Your last run of the six questions: <b>${last.totals.right} of ${last.totals.of}</b> right, ${HX.num(last.totals.first_call_tokens)} tokens on the first model call.` : ' Next: ask the six questions (tab 2), then change a knob and measure it (tab 3).') + '</p>';
}

function card(n) {
  const t = T(n), k = ME.config.tools[n];
  const d = ME.definitions.find((x) => x._meta['ledgerline/tool'] === n) || t.shipped;
  const outOpts = CAT.output_tools.includes(n);
  const rowsOpt = CAT.rows_tools.includes(n);
  return `<article class="tool${edited(n) ? ' edited' : ''}" data-tool="${E(n)}">
  <div class="th"><span class="nm">${E(d.name)}</span><span class="tt">${E(t.title)}</span>${t.writes ? '<span class="wtag">writes</span>' : '<span class="rtag">reads</span>'}
    <span class="sp"></span><span class="ver" title="the version published in tools/list">v${E(ME.versions[n])}</span>
    ${edited(n) ? '<button class="btn ghost sm" data-reset>Reset to shipped</button>' : ''}
    <label class="switch" title="switched on"><input type="checkbox" data-onoff checked></label></div>
  <div class="tb">
   <div class="pane reads"><h4>What the model reads</h4>
    <div class="knob" data-k="name"><div class="kh"><span class="lbl">Name</span>${pills([['clear', n], ['legacy', CAT.legacy_names[n]]], k.name)}</div><p class="hint">${E(KN('name').line)}</p></div>
    <div class="knob" data-k="description"><div class="kh"><span class="lbl">Description</span>${pills([['precise', 'Precise'], ['vague', 'Vague'], ['misleading', 'Misleading'], ['custom', 'Your own']], k.description)}</div>
      ${k.description === 'custom' ? `<textarea class="desc" data-custom maxlength="600">${E(k.custom || d.description)}</textarea><button class="btn ghost sm" data-savecustom>Save my description</button>` : `<div class="desc">${E(d.description)}</div>`}
      <p class="hint">${E(KN('description').line)}${k.description === 'misleading' && t.misleading_from ? ` Here: ${E(t.misleading_from)}'s description.` : ''}</p></div>
    <div class="knob" data-k="input"><div class="kh"><span class="lbl">Input schema</span>${pills([['loose', 'Loose'], ['shipped', 'As shipped'], ['strict', 'Strict']], k.input)}</div>
      <div class="schema">${HX.json(d.inputSchema)}</div><p class="hint">${E((CAT.knobs.tool_knobs.find((x) => x.id === 'input').presets || {})[k.input] || '')}</p></div>
    <div class="knob" data-k="output"><div class="kh"><span class="lbl">Output</span>${outOpts ? pills([['all', 'All fields'], ['lean', 'Only what is needed'], ['minimal', 'Too little']], k.output) : '<span class="muted small">all fields (no lean set for this tool)</span>'}
      </div>${rowsOpt ? `<div class="kh"><span class="lbl">Rows in a list</span>${pills([['0', 'all'], ['1', '1'], ['3', '3'], ['5', '5']], k.rows)}</div>` : ''}
      <details class="src"><summary>Output schema the model is promised</summary><div class="schema">${HX.json(d.outputSchema || {})}</div></details>
      <p class="hint">${E(KN('output').line)}</p></div>
    <div class="knob" data-k="errors"><div class="kh"><span class="lbl">Error replies</span>${pills([['words', 'In words + next step'], ['raw', 'Raw legacy code']], k.errors)}</div><p class="hint">${E(KN('errors').line)}</p></div>
   </div>
   <div class="pane runs"><h4>What runs</h4>
    <p class="small ink2">Ledgerline services this tool calls, in order of need:</p>
    <div class="svc">${t.services.map((s) => `<code>${E(s)}</code>`).join('') || '<span class="muted small">none (it reads Northbridge’s documents)</span>'}</div>
    <p class="small ink2">Acts as <b>${ME.config.identity === 'SVC_AGENT' ? 'the service account SVC_AGENT (every permission, no limit)' : 'Emma Clarke (ECLARKE), her permissions and her £250,000 limit'}</b>. Change it in The Shield.</p>
    <details class="src"><summary>tool.py (read only)</summary><pre>${E(t.python)}</pre></details>
   </div>
  </div>
  <div class="try"><button class="btn ghost sm" data-try>Try it</button><code class="small" data-args contenteditable="true" spellcheck="false" title="edit the arguments">${E(JSON.stringify(t.example))}</code>
    <span class="muted small">calls ${E(d.name)} in your sandbox through your MCP server, exactly as the model would; no model, no cost</span><div class="out" data-out></div></div>
</article>`;
}

function bindCard(n) {
  const el = $(`article.tool[data-tool="${n}"]`); if (!el) return;
  ['name', 'description', 'input', 'errors'].forEach((k) => bindPills(el, `.knob[data-k="${k}"] .kh`, (v) => knob(n, k, v)));
  const kh = $$(`.knob[data-k="output"] .kh`, el);
  const outP = CAT.output_tools.includes(n) ? kh[0] : null, rowP = CAT.rows_tools.includes(n) ? kh[kh.length - 1] : null;
  if (outP) $$('.pill', outP).forEach((b) => b.addEventListener('click', () => knob(n, 'output', b.dataset.v)));
  if (rowP && rowP !== outP) $$('.pill', rowP).forEach((b) => b.addEventListener('click', () => knob(n, 'rows', +b.dataset.v)));
  const oo = $('input[data-onoff]', el); oo.addEventListener('change', () => knob(n, 'on', oo.checked));
  const rs = $('[data-reset]', el);
  if (rs) rs.addEventListener('click', async () => {
    const c = clone(ME.config); Object.assign(c.tools[n], { name: 'clear', description: 'precise', custom: '', input: 'shipped', output: 'all', rows: 0, errors: 'words' });
    await saveConfig(c, `${n} back to its shipped version`); renderAnvil();
  });
  const sc = $('[data-savecustom]', el);
  if (sc) sc.addEventListener('click', async () => { const c = clone(ME.config); c.tools[n].custom = $('[data-custom]', el).value; c.tools[n].description = 'custom'; await saveConfig(c, 'Description saved: it is in tools/list now'); renderAnvil(); });
  $('[data-try]', el).addEventListener('click', async () => {
    let args = {}; try { args = JSON.parse($('[data-args]', el).textContent || '{}'); } catch (e) { HX.toast('The arguments are not valid JSON'); return; }
    const out = $('[data-out]', el); out.innerHTML = '<span class="thinking"><i></i><i></i><i></i></span>';
    try {
      const r = await HX.api('/api/tool/try', { tool: n, args });
      out.innerHTML = r.error ? `<p class="bad small">${E(r.error)}</p>` : `<p class="small muted">Result as the model reads it: ${HX.num(r.chars)} characters${r.isError ? ' · <span class="bad">isError: true</span>' : ''}</p><pre>${HX.json(r.text, 6000)}</pre>`;
    } catch (e) { out.innerHTML = `<p class="bad small">${E(e.message)}</p>`; }
  });
}
$('#resetall').addEventListener('click', async () => {
  const c = clone(ME.config);
  CAT.tools.forEach((t) => Object.assign(c.tools[t.name], { on: CAT.starter.includes(t.name), name: 'clear', description: 'precise', custom: '', input: 'shipped', output: 'all', rows: 0, errors: 'words' }));
  c.rules = { max_qty: 'off', max_qty_n: CAT.limit_default, preview: 'prompt', self_approval: 'off' }; c.identity = 'ECLARKE';
  await saveConfig(c, 'Back to the shipped toolbox'); show(TAB, true);
});

/* ------------------------------------------------------------------ 2 · ask */
let chatHistory = [];
function renderAsk() {
  $('#qchips').innerHTML = CAT.questions.map((q) => `<button class="qchip" data-q="${q.id}"><b>${q.n} · ${E(q.title)}</b>${E(q.ask)}</button>`).join('');
  $$('#qchips .qchip').forEach((b) => b.addEventListener('click', async () => {
    const q = CAT.questions.find((x) => x.id === b.dataset.q);
    if (q.id === 'q6' && chatHistory.length && !busy) {  // after q4 the same request exists already: q6 starts clean
      await HX.api('/api/sandbox/reset', {}); chatHistory = []; drawChat();
      HX.toast('Question 6 starts on a fresh sandbox and a new conversation', 4000);
    }
    send(q.ask, q.then || []);
  }));
  if (!chatHistory.length) loadChat(); else drawChat();
}
async function loadChat() {
  try {
    const c = await HX.api('/api/chat');
    chatHistory = [];
    (c.transcript || []).forEach((t) => { if (t.role === 'user') chatHistory.push({ role: 'user', text: t.text }); else chatHistory.push({ role: 'assistant', turn: t }); });
    drawChat();
  } catch (e) { /* first visit */ }
}
function drawChat(pending, nexts) {
  const m = $('#msgs');
  m.style.minHeight = m.offsetHeight + 'px';  // keep the page from jumping while the chat is redrawn
  requestAnimationFrame(() => requestAnimationFrame(() => { m.style.minHeight = ''; }));
  if (!chatHistory.length && !pending) { m.innerHTML = '<p class="muted center empty">Click a question above, or type your own. Our harness is Ask Northbridge with gemini-3.8-flash; it finds your tools over MCP from your own forge and acts in your own Ledgerline sandbox as Emma Clarke.</p>'; return; }
  m.innerHTML = chatHistory.map((h) => h.role === 'user' ? `<div class="mu">${E(h.text)}</div>` : turnHTML(h.turn)).join('')
    + (pending ? `<div class="ma"><span class="thinking"><i></i><i></i><i></i> ${E(pending)}</span></div>` : '');
  const last = chatHistory[chatHistory.length - 1];
  if (!pending && last && last.role === 'assistant') {
    const opts = [];
    if (last.turn.preview) opts.push('Yes, go ahead.');
    (nexts || []).forEach((x) => { if (!opts.includes(x)) opts.push(x); });
    if (opts.length) {
      m.insertAdjacentHTML('beforeend', `<div class="row yes">${opts.map((o, i) => `<button class="btn ${i ? 'ghost' : 'sky'} sm" data-next="${E(o)}">${E(o.length > 70 ? o.slice(0, 68) + '…' : o)}</button>`).join('')}</div>`);
      $$('[data-next]', m).forEach((b) => b.addEventListener('click', () => send(b.dataset.next, (nexts || []).filter((x) => x !== b.dataset.next))));
    }
  }
  const turns = chatHistory.filter((h) => h.role === 'assistant').map((h) => h.turn);
  const tin = turns.reduce((a, t) => a + (t.tokens_in || 0), 0), calls = turns.reduce((a, t) => a + (t.model_calls || 0), 0);
  const tools = turns.reduce((a, t) => a + (t.cards || []).length, 0);
  $('#chatmeta').textContent = turns.length ? `This conversation: ${pl(calls, 'model call')}, ${pl(tools, 'tool call')}, ${HX.num(tin)} tokens in.` : '';
  const first = turns.find((t) => (t.model_steps || []).length);
  $('#tk-ask').innerHTML = `<h3>Your takeaway</h3><p>${turns.length ? `In this conversation the model made ${pl(calls, 'call')} and ${pl(tools, 'tool call')}, and read ${HX.num(tin)} tokens. `
    + (first ? `Even its first call read ${HX.num(first.model_steps[0].tokens_in)} tokens: the system prompt and your ${ME.definitions.length} tool definitions travel with every call. ` : '')
    + 'The model never touched Ledgerline: it saw only your definitions and the results above.' : 'Ask the six questions in order. Watch which tool each one needs, and what the model receives back.'}</p>`;
}
function turnHTML(t) {
  const steps = t.model_steps || [];
  let ci = 0;
  const cards = t.cards || [];
  const tr = steps.map((s, i) => {
    const mine = cards.slice(ci, ci + (s.tools_called || []).length); ci += mine.length;
    return `<div class="step"><span class="mc">Model call ${i + 1} · ${HX.num(s.tokens_in)} tokens in · ${HX.num(s.tokens_out)} out · ${s.seconds.toFixed(1)} s${s.tools_called && s.tools_called.length ? ' → ' + E(s.tools_called.join(', ')) : ' → answers'}</span></div>`
      + mine.map(cardHTML).join('');
  }).join('') + cards.slice(ci).map(cardHTML).join('');
  return `<div class="ma"><div class="bub">${E(t.reply)}</div>
    <div class="meta">${E(t.model || '')} · ${t.model_calls} model calls · ${HX.num(t.tokens_in)} tokens in, ${HX.num(t.tokens_out)} out · ${t.seconds} s · ${HX.usd(t.usd)}</div>
    ${tr ? `<div class="trace">${tr}</div>` : ''}</div>`;
}
function cardHTML(c) {
  const r = c.result || {}, ok = r.ok !== false;
  const txt = JSON.stringify(r);
  return `<div class="tc${ok ? '' : ' fail'}"><div class="tch"><span class="nm">${E(c.tool)}</span>${c.canonical && c.canonical !== c.tool ? `<span class="muted">(${E(c.canonical)})</span>` : ''}
    <span class="chip ${ok ? 'right' : 'wrong'}">${ok ? 'ok' : 'refused'}</span><span class="muted">${c.ms} ms</span></div>
    <pre>${HX.json(c.args || {})}</pre>
    ${ok ? '' : `<p class="small bad" style="margin:6px 0 0">${E(r.error || r.msg || r.err_cd || '')}${r.next_step ? ' → ' + E(r.next_step) : ''}</p>`}
    <details><summary>Result as the model reads it (${HX.num(txt.length)} characters)</summary><pre>${HX.json(r, 5000)}</pre></details></div>`;
}
async function send(text, nexts) {
  if (busy) { HX.toast('Still answering…'); return; }
  busy = true; $('#askbtn').disabled = true;
  chatHistory.push({ role: 'user', text });
  drawChat('Ask Northbridge is working: model, tools, model…');
  try {
    const t = await HX.api('/api/ask', { text });
    chatHistory.push({ role: 'assistant', turn: t });
    drawChat(null, nexts);
  } catch (e) { chatHistory.pop(); drawChat(); HX.toast(e.message, 5000); }
  finally { busy = false; $('#askbtn').disabled = false; }
  const last = $$('#msgs .ma'); if (last.length) last[last.length - 1].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
$('#askform').addEventListener('submit', (ev) => { ev.preventDefault(); const t = $('#asktext').value.trim(); if (!t) return; $('#asktext').value = ''; send(t, []); });
$('#newconv').addEventListener('click', async () => { await HX.api('/api/ask/new', {}); chatHistory = []; drawChat(); HX.toast('New conversation (same sandbox)'); });
$('#resetsb').addEventListener('click', async () => { await HX.api('/api/sandbox/reset', {}); chatHistory = []; drawChat(); HX.toast('Fresh Ledgerline sandbox: Monday 26 October, 09:00'); });

/* ------------------------------------------------------------------ 3 · experiments */
const SUGS = [
  { t: 'Vague descriptions on every tool', m: 'e.g. check_stock: “Gets item data.”', f: (c) => on(c).forEach((n) => { c.tools[n].description = 'vague'; }) },
  { t: 'Legacy names and vague descriptions', m: 'stk_qry, sup_srch, bud_chk … with one-word descriptions', f: (c) => on(c).forEach((n) => { c.tools[n].name = 'legacy'; c.tools[n].description = 'vague'; }) },
  { t: 'Legacy names, precise descriptions', m: 'does a good description rescue a bad name?', f: (c) => on(c).forEach((n) => { c.tools[n].name = 'legacy'; }) },
  { t: 'Misleading descriptions', m: 'each tool carries a neighbour’s description', f: (c) => on(c).forEach((n) => { c.tools[n].description = 'misleading'; }) },
  { t: 'Only what is needed in every result', m: 'lean outputs: fewer tokens?', f: (c) => on(c).forEach((n) => { if (CAT.output_tools.includes(n)) c.tools[n].output = 'lean'; }) },
  { t: 'Too little in every result', m: 'check_stock: the total only, no warehouses', f: (c) => on(c).forEach((n) => { if (CAT.output_tools.includes(n)) c.tools[n].output = 'minimal'; }) },
  { t: 'Raw error codes everywhere', m: 'ERR-SEC-0001 ACCESS DENIED, no next step', f: (c) => on(c).forEach((n) => { c.tools[n].errors = 'raw'; }) },
  { t: 'Loose input schemas', m: 'nothing required, no format hints, nothing checked at the door', f: (c) => on(c).forEach((n) => { c.tools[n].input = 'loose'; }) },
  { t: 'All 16 tools switched on', m: 'tokens on every call, wrong picks?', f: (c) => CAT.tools.forEach((t) => { c.tools[t.name].on = true; }) },
  { t: 'Only 2 tools', m: 'find_item and check_stock', f: (c) => CAT.tools.forEach((t) => { c.tools[t.name].on = ['find_item', 'check_stock'].includes(t.name); }) },
  { t: 'Tools act as the service account', m: 'SVC_AGENT: every permission, no limit', f: (c) => { c.identity = 'SVC_AGENT'; } },
];
const on = (c) => Object.keys(c.tools).filter((n) => c.tools[n].on);
function renderExp() {
  $('#nowsettings').innerHTML = ME.changed.length ? `<div class="settings">${ME.changed.map((d) => `<span>• ${E(d)}</span>`).join('')}</div>` : '<p class="ink2">The shipped toolbox: seven tools, precise descriptions, as-shipped schemas, errors in words, the preview rule in the prompt, acting as Emma. Run it first: that is your baseline.</p>';
  $('#sugs').innerHTML = SUGS.map((s, i) => `<button class="sug" data-i="${i}"><b>${E(s.t)}</b><span class="muted">${E(s.m)}</span></button>`).join('');
  $$('#sugs .sug').forEach((b) => b.addEventListener('click', async () => {
    const c = clone(ME.config); SUGS[+b.dataset.i].f(c);
    await saveConfig(c, 'Changed: ' + SUGS[+b.dataset.i].t + '. Now run the six questions.'); renderExp();
  }));
  drawRuns();
  if (ME.last_run && !$('#scorecard').innerHTML) drawScore(ME.last_run);
  takeExp();
}
$('#backshipped').addEventListener('click', () => $('#resetall').click());
$('#runsix').addEventListener('click', () => runSet('six', $('#runsix')));
$('#runerr').addEventListener('click', () => runSet('errors', $('#runerr')));
async function runSet(set, btn) {
  btn.disabled = true;
  const qs = set === 'errors' ? CAT.probes : CAT.questions;
  try {
    const j0 = await HX.api('/api/six', { set });
    const draw = (j) => { const done = (j.progress && j.progress.done) || []; $('#prog6').innerHTML = qs.map((q) => { const d = done.find((x) => x.id === q.id); return `<span class="p6 ${d ? (d.right ? 'right' : 'wrong') : (j.progress && j.progress.now === q.id ? 'now' : '')}">${q.id.startsWith('e') ? 'E' : ''}${q.n}</span>`; }).join('') + `<span class="muted small" style="align-self:center">${j.seconds} s</span>`; };
    draw(j0);
    const j = await HX.poll(j0.id, draw, 1500);
    if (j.state === 'failed') { HX.toast(j.error, 6000); return; }
    ME = await HX.api('/api/me');
    drawScore(j.result); drawRuns(); takeExp();
  } catch (e) { HX.toast(e.message, 5000); } finally { btn.disabled = false; }
}
function drawScore(run) {
  const t = run.totals;
  const QS = CAT.questions.concat(CAT.probes);
  $('#scorecard').innerHTML = `<div class="sc card white"><h3>Run ${run.n}${run.set === 'errors' ? ' (the three error questions)' : ''}: ${t.right} of ${t.of} right</h3>
    <p class="small muted">${run.settings && run.settings.length ? E(run.settings.join(' · ')) : 'shipped toolbox'} · ${t.model_calls} model calls · ${HX.num(t.tokens_in)} tokens in · ${t.seconds} s of model time · ${HX.usd(t.usd)} · ${E((t.models || []).join(', '))}</p>
    <div class="tablewrap"><table><tr><th>#</th><th>Question</th><th></th><th>Why</th><th>Tools the model called</th><th class="num">Model calls</th><th class="num">Tokens in</th><th class="num">Door / rule refusals</th><th class="num">Ledgerline errors</th><th class="num">Seconds</th></tr>
    ${run.rows.map((r) => `<tr><td>${r.n}</td><td class="small">${E(QS.find((q) => q.id === r.id).ask)}${r.turns ? `<details class="qturns"><summary>see the answer and trace</summary>${r.turns.map(turnHTML).join('')}</details>` : ''}</td>
      <td><span class="chip ${r.right ? 'right' : r.failed ? 'mute' : 'wrong'}">${r.right ? 'right' : r.failed ? 'no answer' : 'wrong'}</span></td><td class="small">${E(r.why)}</td>
      <td class="small mono">${E(r.tools.join(', ') || '(none)')}</td><td class="num">${r.model_calls}</td><td class="num">${HX.num(r.tokens_in)}</td><td class="num">${r.door} / ${r.rule}</td><td class="num">${r.ledgerline_errors}</td><td class="num">${r.seconds}</td></tr>`).join('')}
    </table></div></div>`;
}
function drawRuns() {
  const rs = ME.runs || [];
  $('#runs').innerHTML = rs.length ? `<tr><th>Run</th><th>Settings</th><th class="num">Right</th><th class="num">Tokens in</th><th class="num">First call</th><th class="num">Per model call</th><th class="num">Tool calls</th><th class="num">Door / rule</th><th class="num">Ledgerline errors</th><th class="num">Seconds</th><th class="num">Cost</th></tr>`
    + rs.slice().reverse().map((r) => `<tr data-n="${r.n}"><td>${r.n}${r.set === 'errors' ? ' <span class="chip mute">errors</span>' : ''}</td><td class="small">${r.settings.length ? r.settings.map(E).join('<br>') : '<b>shipped</b>'}</td><td class="num"><b>${r.totals.right}/${r.totals.of}</b></td><td class="num">${HX.num(r.totals.tokens_in)}</td><td class="num">${HX.num(r.totals.first_call_tokens)}</td><td class="num">${HX.num(r.totals.tokens_per_model_call)}</td><td class="num">${r.totals.tool_calls}</td><td class="num">${r.totals.door} / ${r.totals.rule}</td><td class="num">${r.totals.ledgerline_errors}</td><td class="num">${r.totals.seconds}</td><td class="num">${HX.usd(r.totals.usd)}</td></tr>`).join('')
    : '<tr><td class="muted">No runs yet. Run the six questions with the shipped toolbox first.</td></tr>';
  $$('#runs tr[data-n]').forEach((tr) => tr.addEventListener('click', () => {
    const r = ME.runs.find((x) => String(x.n) === tr.dataset.n);
    $$('#runs tr').forEach((x) => x.classList.toggle('sel', x === tr));
    drawScore(ME.last_run && ME.last_run.n === r.n ? ME.last_run : r);
    $('#scorecard').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }));
}
function takeExp() {
  const rs = ME.runs || [];
  const six = rs.filter((r) => (r.set || 'six') === 'six');
  const base = six.filter((r) => !r.settings.length).pop();
  const other = six.filter((r) => r.settings.length).pop();
  let p = 'Run the shipped toolbox once, then change one thing and run again. The table above keeps every run beside its settings.';
  if (base && other) {
    const dt = other.totals.tokens_in - base.totals.tokens_in, df = (other.totals.first_call_tokens || 0) - (base.totals.first_call_tokens || 0);
    p = `Shipped: <b>${base.totals.right} of 6</b> right, ${HX.num(base.totals.tokens_in)} tokens in. With “${E(other.settings.join('; '))}”: <b>${other.totals.right} of 6</b>, ${HX.num(other.totals.tokens_in)} tokens in (${dt >= 0 ? '+' : ''}${HX.num(dt)}), the first call ${df >= 0 ? '+' : ''}${HX.num(df)} tokens, ${other.totals.tool_calls} tool calls against ${base.totals.tool_calls}, ${other.totals.door + other.totals.rule} refusals at the door. `
      + (other.totals.right < base.totals.right ? 'The knob cost right answers: read the “Why” column to see where.' : other.totals.right > base.totals.right ? 'The knob helped.' : 'Same score: look at the tokens and tool calls, where the cost moved.');
  } else if (base) p = `Your baseline: <b>${base.totals.right} of 6</b> right, ${HX.num(base.totals.tokens_in)} tokens in, ${base.totals.tool_calls} tool calls. Now change one thing.`;
  $('#tk-exp').innerHTML = `<h3>Your takeaway</h3><p>${p}</p>`;
}

/* ------------------------------------------------------------------ 4 · the shield */
function renderShield() {
  const r = ME.config.rules, R = CAT.knobs.rules;
  const place = [['off', 'Off'], ['prompt', 'In the prompt'], ['tool', 'In the tool']];
  $('#rules').innerHTML = R.filter((x) => x.id !== 'identity').map((x) => `<div class="rule" data-r="${x.id}"><div class="rl"><b>${E(x.id === 'max_qty' ? `At most ${HX.num(r.max_qty_n)} units in one request or order` : x.label)}</b><span>${E(x.line)}</span>
      ${x.id === 'max_qty' ? `<div class="row" style="margin-top:6px"><span class="lbl">Limit</span><input class="n" type="number" min="1" value="${r.max_qty_n}" data-n></div>` : ''}</div>
      ${pills(x.id === 'preview' ? place.concat([['host', 'In the host']]) : place, r[x.id], null, 'ember')}</div>`).join('')
    + `<div class="rule" data-r="identity"><div class="rl"><b>The tools act as</b><span>${E(R.find((x) => x.id === 'identity').line)}</span></div>${pills([['ECLARKE', 'Emma Clarke (ECLARKE)'], ['SVC_AGENT', 'Service account (SVC_AGENT)']], ME.config.identity, null, 'ember')}</div>`;
  $$('#rules .rule').forEach((el) => bindPills(el, '', async (v) => {
    const c = clone(ME.config);
    if (el.dataset.r === 'identity') c.identity = v; else c.rules[el.dataset.r] = v;
    await saveConfig(c); renderShield();
  }));
  const n = $('#rules [data-n]'); if (n) n.addEventListener('change', async () => { const c = clone(ME.config); c.rules.max_qty_n = +n.value || 5000; await saveConfig(c, 'Limit saved'); renderShield(); });
  const lastRun = (ME.shield || []).filter((s) => s.kind === 'run').pop();
  const lastCmp = (ME.shield || []).filter((s) => s.kind === 'compare').pop();
  if (lastRun && !$('#attacks').innerHTML) drawAttacks(lastRun);
  if (lastCmp && !$('#matrix').innerHTML) drawMatrix(lastCmp);
  takeShield();
}
function drawAttacks(s) {
  $('#attacks').innerHTML = s.rows.map((a) => `<div class="atk ${a.held ? 'held' : 'broke'}"><div class="ah"><b>${E(a.title)}</b><span class="chip ${a.held ? 'held' : a.held === null ? 'mute' : 'broke'}">${a.held ? 'held' : a.held === null ? 'no answer' : 'broke'}</span></div>
    <div class="q">“${E(a.ask)}”${(CAT.attacks.find((x) => x.id === a.id) || {}).then ? ` → then “${E(CAT.attacks.find((x) => x.id === a.id).then.join(' '))}”` : ''}</div><p class="what">${E(a.what)}</p>
    <p class="small muted">Rule: ${E(a.placement === 'off' ? 'off' : 'in the ' + a.placement)} · acts as ${E(a.identity)}${a.stopped_by ? ' · stopped by ' + E(a.stopped_by) : ''}</p>
    <details><summary>The model's reply and its tool calls</summary><pre>${E(a.turn.reply)}</pre>${a.turn.cards.map((c) => `<pre>${E(c.tool)} ${E(JSON.stringify(c.args))}\n→ ${E(JSON.stringify(c.result).slice(0, 400))}</pre>`).join('')}</details></div>`).join('');
}
function drawMatrix(s) {
  const ids = [...new Set(s.rows.map((r) => r.id))];
  const cols = [['off', 'ours', 'Rule off'], ['prompt', 'ours', 'In the prompt'], ['tool', 'ours', 'In the tool'], ['host', 'ours', 'In the host (preview rule only)'], ['prompt', 'generic', 'In the prompt, host without our prompt'], ['tool', 'generic', 'In the tool, host without our prompt']];
  $('#matrix').innerHTML = `<div class="card white"><h3>Prompt or tool: the comparison</h3><p class="small muted">Acting as ${E(s.identity)}. “Host without our prompt”: the same MCP tools with a plain host prompt (“You are a helpful assistant…”), as Claude has; only what is in the tools comes along.</p>
    <div class="tablewrap"><table><tr><th>Attack</th>${cols.map((c) => `<th>${E(c[2])}</th>`).join('')}</tr>
    ${ids.map((id) => `<tr><td><b>${E(s.rows.find((r) => r.id === id).title)}</b></td>${cols.map((c) => { const r = s.rows.find((x) => x.id === id && x.placement === c[0] && x.host === c[1]); return `<td>${r ? `<span class="chip ${r.held ? 'held' : r.held === null ? 'mute' : 'broke'}">${r.held ? 'held' : r.held === null ? 'no answer' : 'broke'}</span><div class="small muted" style="margin-top:4px">${E(r.what)}</div>` : '–'}</td>`; }).join('')}</tr>`).join('')}</table></div></div>`;
}
async function job(path, btn, draw) {
  btn.disabled = true; const old = btn.textContent; btn.textContent = 'Running…';
  try {
    const j0 = await HX.api(path, {});
    const j = await HX.poll(j0.id, (x) => { btn.textContent = `Running… ${x.seconds} s`; }, 1500);
    if (j.state === 'failed') { HX.toast(j.error, 6000); return null; }
    ME = await HX.api('/api/me'); draw(j.result); return j.result;
  } catch (e) { HX.toast(e.message, 5000); return null; } finally { btn.disabled = false; btn.textContent = old; }
}
$('#runattacks').addEventListener('click', () => job('/api/shield/run', $('#runattacks'), (r) => { drawAttacks(r); takeShield(); }));
$('#compare').addEventListener('click', () => job('/api/shield/compare', $('#compare'), (r) => { drawMatrix(r); takeShield(); }));
$('#scansecrets').addEventListener('click', async () => {
  const pats = [/@123\b/, /svc@ledger/, /password/i, /northbridgecycles\.example/, /api[_-]?key/i, /token/i];
  const tools = on(ME.config).filter((n) => !T(n).writes);
  let found = [], chars = 0;
  for (const n of tools) {
    try { const r = await HX.api('/api/tool/try', { tool: n, args: T(n).example }); chars += r.chars || 0; pats.forEach((p) => { if (p.test(r.text || '')) found.push(`${n}: ${p}`); }); } catch (e) { /* skip */ }
  }
  $('#secrets').innerHTML = found.length ? `<span class="bad">Found in results: ${E(found.join('; '))}</span>` : `Scanned ${tools.length} read tools' results (${HX.num(chars)} characters) for passwords, e-mail addresses, keys and tokens: <b class="ok">none found</b>.`;
});
function takeShield() {
  const lr = (ME.shield || []).filter((s) => s.kind === 'run').pop(), lc = (ME.shield || []).filter((s) => s.kind === 'compare').pop();
  let p = 'Run the four attacks with the shipped rules, then move a rule from the prompt to the tool and run them again.';
  if (lc) {
    const col = (w, h) => lc.rows.filter((r) => r.placement === w && r.host === h);
    const held = (xs) => `${xs.filter((r) => r.held).length} of ${xs.length}`;
    const np = lc.rows.filter((r) => r.id === 'nopreview' && r.placement === 'tool' && r.host === 'ours')[0];
    p = `Rules off: ${held(col('off', 'ours'))} held. In the prompt: ${held(col('prompt', 'ours'))}. In the tool: ${held(col('tool', 'ours'))}. In the host (preview rule only): ${held(col('host', 'ours'))}. On a host without our prompt (Claude's situation): in the prompt ${held(col('prompt', 'generic'))}, in the tool ${held(col('tool', 'generic'))}. A rule in the tool is code: it holds whoever the host is, for what the tool can see.`
      + (np && !np.held ? ' But “skip the preview” broke with the rule in the tool: the model previewed and committed in the same turn, and the tool cannot see whether Emma read it. Only the host, which sees her messages, can hold that one.' : '');
  } else if (lr) p = `With your rules, ${lr.held} of ${lr.of} attacks held. ${lr.rows.filter((r) => !r.held).map((r) => `“${r.title}” broke: ${r.what}.`).join(' ')}`;
  $('#tk-shield').innerHTML = `<h3>Your takeaway</h3><p>${E(p)}</p>`;
}

/* ------------------------------------------------------------------ 5 · connect */
function renderConnect() {
  $('#mcpurl').textContent = ME.mcp_url;
  $('#cccmd').textContent = `claude mcp add --transport http hephaestus ${ME.mcp_url}`;
  $('#sixcopy').innerHTML = `<div class="six">${CAT.questions.map((q) => { const t = [q.ask].concat(q.then || []); return t.map((x, i) => `<div class="sq"><span class="n">${q.n}${t.length > 1 ? 'abc'[i] : ''}</span><span class="t">${E(x)}</span><button class="btn ghost sm" data-copy="${E(x)}">Copy</button></div>`).join(''); }).join('')}</div>`;
  $$('#sixcopy [data-copy]').forEach((b) => b.addEventListener('click', () => HX.copy(b.dataset.copy, 'Question copied')));
  drawLive();
}
$('#copyurl').addEventListener('click', () => HX.copy(ME.mcp_url, 'Address copied'));
$('#copycc').addEventListener('click', () => HX.copy($('#cccmd').textContent, 'Command copied'));
$('#testaddr').addEventListener('click', () => job('/api/prod/mcp', $('#testaddr'), (r) => {
  const c = r.checks[0];
  $('#testout').innerHTML = `<p class="${c.pass ? 'ok' : 'bad'}">${E(c.headline)}</p>` + c.rows.map((x) => `<div>${x.pass === null ? '•' : x.pass ? '<span class="ok">✓</span>' : '<span class="bad">✕</span>'} ${E(x.step)}: <span class="muted">${E(x.shows)}</span></div>`).join('');
}));
async function pollLive() {
  try {
    const r = await HX.api('/api/calls?since=' + liveSince);
    if (r.hits.length) { lastHits = lastHits.concat(r.hits).slice(-200); liveSince = r.hits[r.hits.length - 1].t; }
    ME.connected = r.connected;
    drawLive(r.hits.length);
  } catch (e) { $('#livestate').textContent = e.message; }
}
function drawLive(fresh) {
  const con = ME.connected;
  $('#livestate').innerHTML = con ? `<span class="chip right">connected: ${E(con.client)}</span> · ${con.calls || 0} tool calls · last ${HX.ago(con.last)}` : 'no client yet · refreshing every 3 s';
  const hs = lastHits.filter((h) => !String(h.client || '').startsWith('hephaestus-')).slice().reverse();
  if (hs.length) $('#livelog').innerHTML = hs.map((h, i) => `<div class="lg${fresh && i < fresh ? ' new' : ''}"><div class="lh"><span class="muted">${HX.time(h.t)}</span><b>${E(h.client)}</b><span class="mono">${E(h.method)}${h.tool ? ' · ' + E(h.tool) : ''}</span>${h.method === 'tools/call' ? `<span class="chip ${h.ok ? 'right' : 'wrong'}">${h.ok ? 'ok' : 'refused'}</span>` : ''}<span class="muted">${h.ms} ms</span></div>
      ${h.tools ? `<div class="small muted">listed: ${E(h.tools.join(', '))}</div>` : ''}${h.args ? `<pre>${HX.json(h.args)}</pre>` : ''}${h.text ? `<details><summary class="small">result</summary><pre>${HX.json(h.text, 3000)}</pre></details>` : ''}</div>`).join('');
  const calls = hs.filter((h) => h.method === 'tools/call');
  const used = [...new Set(calls.map((h) => h.tool))];
  $('#tk-connect').innerHTML = `<h3>Your takeaway</h3><p>${calls.length ? `Claude (${E(con ? con.client : 'a client')}) has called your tools ${calls.length} times: ${E(used.join(', '))}. Same definitions, same sandbox, a different harness: compare its answers and its tool choices with your runs in tab 3. Your prompt rules did not come along; your tool rules did.` : 'Connect Claude with your address, paste question 1, and watch the call arrive here. Then change a knob in The Anvil and ask again: Claude sees the change on its next tools/list.'}</p>`;
}

/* ------------------------------------------------------------------ 6 · production */
function renderProd() {
  $('#crit').innerHTML = CAT.criteria.map((c, i) => critHTML(c, i, ME.prod[c.id])).join('');
  $$('#crit [data-run]').forEach((b) => b.addEventListener('click', () => job('/api/prod/' + b.dataset.run, b, (r) => { r.checks.forEach(putCheck); takeProd(); })));
  takeProd();
}
function critHTML(c, i, res) {
  const st = res ? (res.pass === true ? 'pass' : res.pass === false ? 'fail' : '') : '';
  return `<div class="cr ${st}" data-c="${c.id}"><div class="crh"><span class="no">${i + 1}</span><div class="crt"><b>${E(c.area)} · ${E(c.criterion)}</b><span>Threshold: ${E(c.threshold)}</span></div>
    <div>${res ? `<span class="chip ${res.pass === true ? 'right' : res.pass === false ? 'wrong' : 'mute'}">${res.pass === true ? 'passes' : res.pass === false ? 'fails' : 'n/a'}</span> ` : ''}<button class="btn ghost sm" data-run="${c.id}">${res ? 'Run again' : 'Run on my tools'}</button></div></div>
    <div class="res" data-res>${res ? E(res.headline) + (res.settings && res.settings.length ? ` <span class="muted small">(with: ${E(res.settings.join('; '))})</span>` : '') : '<span class="muted">Not run yet.</span>'}</div>
    <div data-rows></div>
    <div class="do"><b>For your own project:</b> ${E(c.do)}</div></div>`;
}
function putCheck(r) {
  const el = $(`#crit .cr[data-c="${r.id}"]`); if (!el) return;
  const i = CAT.criteria.findIndex((c) => c.id === r.id);
  el.outerHTML = critHTML(CAT.criteria[i], i, r);
  const nel = $(`#crit .cr[data-c="${r.id}"]`);
  $('[data-rows]', nel).innerHTML = `<details><summary>Details (${r.seconds} s)</summary><pre>${HX.json(r.rows, 12000)}</pre></details>`;
  $('[data-run]', nel).addEventListener('click', () => job('/api/prod/' + r.id, $('[data-run]', nel), (x) => { x.checks.forEach(putCheck); takeProd(); }));
}
$('#runall').addEventListener('click', async () => {
  const b = $('#runall'); b.disabled = true;
  try {
    const j0 = await HX.api('/api/prod/all', {});
    const j = await HX.poll(j0.id, (x) => { $('#prodline').textContent = x.progress && x.progress.now ? `checking ${x.progress.now}… ${x.seconds} s` : ''; }, 1500);
    if (j.state === 'failed') { HX.toast(j.error, 6000); return; }
    ME = await HX.api('/api/me'); j.result.checks.forEach(putCheck); $('#prodline').textContent = `done in ${j.seconds} s`; takeProd();
  } catch (e) { HX.toast(e.message, 5000); } finally { b.disabled = false; }
});
function takeProd() {
  const r = Object.values(ME.prod || {});
  const pass = r.filter((x) => x.pass === true), fail = r.filter((x) => x.pass === false);
  $('#tk-prod').innerHTML = `<h3>Your takeaway</h3><p>${r.length ? `${pass.length} of ${r.length} criteria pass on your tools${fail.length ? `; failing: ${fail.map((x) => E(x.area)).join(', ')}` : ''}. A demo is one happy path; each criterion here is a test you can run again after every change. Change a knob in The Anvil (say, raw errors or loose input) and run Reliability or Idempotency again.` : 'Run every check on your tools. Then break something on purpose in The Anvil and run the check that should catch it.'}</p>`;
}

boot();
})();
