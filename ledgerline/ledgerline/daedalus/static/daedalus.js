/* Daedalus: the Lecture 5 workshop. Tabs: The Loop, Your agent, Your workflow, The race; Daniel's inbox on every tab. */
(() => {
'use strict';
const $ = (s) => document.querySelector(s);
const esc = DX.esc, num = DX.num;
let CAT = null, ME = null, WRUN = null;
const ORDER = 'Order 2,000 BAT-500 packs from Voltway for the spring launch run.';

/* ------------------------------------------------------------------ join */
async function boot() {
  CAT = await DX.api('/api/catalog');
  if (DX.key()) {
    try { ME = await DX.api('/api/me'); $('#wname').textContent = ME.name; $('#joinform').classList.add('hide'); $('#keyline').classList.add('hide'); $('#welcome').classList.remove('hide'); }
    catch (e) { DX.forget(); }
  }
  if (location.hash && ME) enter();
}
$('#joinform').onsubmit = async (e) => {
  e.preventDefault(); $('#joinbtn').disabled = true;
  try { ME = await DX.api('/api/join', { name: $('#name').value }); DX.setKey(ME.key); enter(); }
  catch (err) { DX.toast(err.message); } finally { $('#joinbtn').disabled = false; }
};
$('#usekey').onclick = (e) => { e.preventDefault(); const k = prompt('Paste your workshop key (dx-…)'); if (k) { DX.setKey(k.trim()); location.reload(); } };
$('#notme').onclick = (e) => { e.preventDefault(); DX.forget(); location.hash = ''; location.reload(); };
$('#enter').onclick = (e) => { e.preventDefault(); enter(); };

function enter() {
  $('#top').classList.add('hide'); $('#app').classList.remove('hide'); $('#nav').classList.remove('hide');
  $('#navname').textContent = ME.name;
  drawAll(); tab((location.hash || '#loop').slice(1)); inboxCount();
}
function tab(t) {
  if (!['loop', 'agent', 'workflow', 'race'].includes(t)) t = 'loop';
  document.querySelectorAll('section.tab').forEach((s) => s.classList.toggle('hide', s.dataset.tab !== t));
  document.querySelectorAll('.nav a[data-tab]').forEach((a) => a.classList.toggle('on', a.dataset.tab === t));
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', () => ME && tab(location.hash.slice(1)));
function drawAll() { drawSay(); drawTrace(); drawKnobs(); drawSix(); drawBlocks(); drawWfRuns(); drawRaces(); spend(); }
function spend() { $('#spend').textContent = ME ? `· your model spend today ${DX.usd(ME.spend_usd)} of ${DX.usd(ME.student_cap_usd)}` : ''; }
async function refresh() { ME = await DX.api('/api/me'); spend(); }

/* ------------------------------------------------------------------ 1 · the loop */
function drawSay() {
  if (!$('#saytext').value) $('#saytext').value = ORDER;
  const chips = [['Emma’s order', ORDER], ['Yes, go ahead.', 'Yes, go ahead.'], ['Next morning', CAT.morning]].concat(CAT.jobs.map((j) => [j.title, j.text]));
  $('#saychips').innerHTML = chips.map(([l, t], i) => `<button class="pill sm" data-i="${i}" title="${esc(t)}">${esc(l)}</button>`).join('');
  $('#saychips').querySelectorAll('button').forEach((b) => { b.onclick = () => { $('#saytext').value = chips[+b.dataset.i][1]; }; });
}
function loopButtons() {
  const L = ME.loop, busy = !L.done;
  $('#stepbtn').disabled = !busy; $('#runbtn').disabled = !busy; $('#saybtn').disabled = busy;
  const c = ME.config;
  $('#harnessline').innerHTML = `Your harness: at most <b>${c.max_steps}</b> steps a message · budget <b>${c.budget ? num(c.budget) + ' tokens' : 'none'}</b> · <b>${c.tools.length}</b> tools · prompt <b>${esc(c.prompt)}</b> · pause <b>${c.pause ? 'on' : 'off'}</b> · recovery <b>${c.recovery ? 'on' : 'off'}</b>. <a href="#agent">Change it</a>` +
    (L.waiting ? ` · <span class="chip wait">paused: ${esc(L.waiting.doc)} waits for ${esc(L.waiting.approver)}</span>` : '');
}
function callCard(c) {
  const r = c.result || {};
  const tag = c.blocked ? `<span class="chip wait">refused by the harness: ${esc(c.blocked)}</span>` : c.ok ? '<span class="chip right">ok</span>' : '<span class="chip wrong">ok: false</span>';
  const head = r.request_no || r.po_no ? `${esc(r.request_no || '')} ${esc(r.po_no || '')} · ${esc(r.status || '')}` : r.error ? esc(r.error) : '';
  return `<details class="call"><summary><code class="tn">${esc(c.name)}</code><span class="args">${esc(JSON.stringify(c.args))}</span>${tag}<span class="muted small">${esc(head)}</span></summary><pre class="json">${DX.json(r, 2400)}</pre></details>`;
}
function stepCard(s) {
  if (s.kind === 'harness') return `<div class="step h"><span class="sn">harness</span><div class="sb"><b>${esc(s.note || '')}</b>${s.result ? `<details class="call"><summary><code class="tn">${esc(s.tool || '')}</code> <span class="args">${esc(JSON.stringify(s.args || {}))}</span></summary><pre class="json">${DX.json(s.result, 1600)}</pre></details>` : ''}</div></div>`;
  const words = (s.text || '').trim();
  return `<div class="step m${s.end ? ' end' : ''}"><span class="sn">step ${s.n}</span><div class="sb">
    <div class="think"><span class="lbl">the model</span>${words ? `<p>${esc(words).replace(/\n/g, '<br>')}</p>` : '<p class="muted">(no words: it went straight to the tools)</p>'}</div>
    ${s.calls.length ? `<div class="calls"><span class="lbl">it asked for ${s.calls.length} tool call${s.calls.length > 1 ? 's' : ''} · our code ran ${s.calls.length > 1 ? 'them' : 'it'}</span>${s.calls.map(callCard).join('')}</div>` : ''}
    <div class="meta"><span>${num(s.tokens_in)} tokens in</span><span>${num(s.tokens_out)} out</span><span>${s.seconds} s</span><span>${esc((s.model || '').replace('gemini:', ''))}</span>${(s.harness || []).map((h) => `<span class="chip ${/paused|refused|stopped|last/.test(h) ? 'wait' : 'info'}">${esc(h)}</span>`).join('')}${s.end ? `<span class="chip end">loop ends: ${esc(s.end)}</span>` : ''}</div>
  </div></div>`;
}
const ENDS = { answered: 'it answered in words', paused: 'paused: waiting for an approver', max_steps: 'the step limit', budget: 'the token budget', failures: 'three failures in a row', 'still waiting': 'still waiting (no model call)' };
function drawTrace() {
  loopButtons();
  const turns = ME.loop.turns;
  if (!turns.length) { $('#trace').innerHTML = '<p class="muted center">Send Emma’s message, then press <b>Next step</b> to run the loop one turn at a time.</p>'; $('#tk-loop').classList.add('hide'); return; }
  $('#trace').innerHTML = turns.map((t, i) => `<div class="turn"><div class="msg u"><span class="who-e">Emma</span>${esc(t.text)}</div>
    ${t.steps.map(stepCard).join('')}
    ${t.end ? `<div class="msg ag"><span class="who-a">Ask Northbridge</span>${esc(t.reply).replace(/\n/g, '<br>')}<div class="meta"><span class="chip end">${esc(ENDS[t.end] || t.end)}</span><span>${t.model_calls} model call${t.model_calls === 1 ? '' : 's'}</span><span>${t.tool_calls} tool calls</span><span>${num(t.tokens_in)} tokens in</span><span>${DX.usd(t.usd)}</span></div></div>` : `<div class="msg pend">…the loop is running. Press <b>Next step</b>.</div>`}</div>`).join('');
  const all = turns.filter((t) => t.end);
  if (all.length) {
    const mc = all.reduce((a, t) => a + t.model_calls, 0), tc = all.reduce((a, t) => a + t.tool_calls, 0), ti = all.reduce((a, t) => a + t.tokens_in, 0);
    $('#tk-loop').innerHTML = `<h3>Your takeaway</h3><p>${all.length} message${all.length > 1 ? 's' : ''} from Emma; the loop made <b>${mc}</b> model calls and <b>${tc}</b> tool calls, and read <b>${num(ti)}</b> tokens. Every step re-sends the whole conversation, so each one reads more than the last. Each loop ended for one reason: ${[...new Set(all.map((t) => ENDS[t.end] || t.end))].map(esc).join('; ')}.</p>`;
    $('#tk-loop').classList.remove('hide');
  }
}
async function act(btn, fn) { btn.disabled = true; btn.classList.add('busy'); try { await fn(); } catch (e) { DX.toast(e.message, 5000); } finally { btn.classList.remove('busy'); await refresh(); drawTrace(); inboxCount(); } }
$('#saybtn').onclick = () => act($('#saybtn'), async () => { await DX.api('/api/loop/say', { text: $('#saytext').value }); $('#nightbox').classList.add('hide'); });
$('#stepbtn').onclick = () => act($('#stepbtn'), () => DX.api('/api/loop/step', {}));
$('#runbtn').onclick = () => act($('#runbtn'), () => DX.api('/api/loop/run', {}));
$('#newbtn').onclick = () => act($('#newbtn'), () => DX.api('/api/loop/new', {}));
$('#resetbtn').onclick = () => act($('#resetbtn'), async () => { await DX.api('/api/sandbox/reset', {}); DX.toast('A fresh Ledgerline: nothing saved yet.'); });
$('#nightbtn').onclick = () => act($('#nightbtn'), async () => {
  const n = await DX.api('/api/loop/night', {});
  $('#nightbox').innerHTML = `<div class="card white"><span class="lbl">Overnight · state across days</span><p>The agent was saved as <b>${num(n.bytes)} bytes of JSON</b> (${n.messages} messages${n.waiting ? `, waiting for ${esc(n.waiting.approver)} on ${esc(n.waiting.doc)}` : ''}), thrown away, and a new one was built from that JSON. Nothing else survived the night. Send the next morning’s message.</p><pre class="json small">${DX.json(n.preview + '…', 1400)}</pre></div>`;
  $('#nightbox').classList.remove('hide'); $('#saytext').value = CAT.morning;
});

/* ------------------------------------------------------------------ 2 · your agent (the harness) */
const KN = [
  { id: 'max_steps', label: 'Max steps', line: 'Model calls allowed per message. The last one must be words.', presets: [[2, '2'], [4, '4'], [12, '12 · shipped'], [25, '25']] },
  { id: 'budget', label: 'Token budget', line: 'Input tokens allowed per message, re-read on every step.', presets: [[6000, '6,000'], [60000, '60,000 · shipped'], [0, 'none']] },
  { id: 'tools', label: 'Tools', line: 'What the model may call. Every definition is sent on every step.', presets: [['two', '2'], ['shipped', '11 · shipped'], ['all', 'all 16']] },
  { id: 'prompt', label: 'System prompt', line: 'Who it works for and the rules of the job.', presets: [['full', 'Ask Northbridge’s · shipped'], ['bare', 'one line'], ['custom', 'your own']] },
  { id: 'pause', label: 'Approval pause', line: 'A request waiting for Daniel pauses the job; next time, read Ledgerline first.', presets: [[true, 'on · shipped'], [false, 'off']] },
  { id: 'recovery', label: 'Error recovery', line: 'Never repeat a failed call; refuse the same call a third time; stop after 3 failures.', presets: [[true, 'on · shipped'], [false, 'off']] },
];
function toolsKey(c) { const s = c.tools.slice().sort().join(); if (s === CAT.two.slice().sort().join()) return 'two'; if (s === CAT.shipped.tools.slice().sort().join()) return 'shipped'; if (s === CAT.all.slice().sort().join()) return 'all'; return 'own'; }
function drawKnobs() {
  const c = ME.config;
  $('#knobs').innerHTML = KN.map((k) => {
    const cur = k.id === 'tools' ? toolsKey(c) : c[k.id];
    const pills = k.presets.map(([v, l]) => `<button class="pill sm${cur === v ? ' on' : ''}" data-k="${k.id}" data-v='${JSON.stringify(v)}'>${esc(l)}</button>`).join('');
    let more = '';
    if (k.id === 'tools') more = `<details class="tl"><summary>one by one (${c.tools.length} on)</summary><div class="tgrid">${CAT.tools.map((t) => `<label class="tchk"><input type="checkbox" data-tool="${t.name}"${c.tools.includes(t.name) ? ' checked' : ''}><code>${t.name}</code>${t.writes ? '<span class="wtag">writes</span>' : ''}</label>`).join('')}</div></details>`;
    if (k.id === 'prompt') more = `<details class="tl"${c.prompt === 'custom' ? ' open' : ''}><summary>read or edit the prompt</summary><textarea id="customp" rows="9">${esc(c.prompt === 'custom' ? c.custom_prompt : CAT.prompts[c.prompt === 'bare' ? 'bare' : 'full'])}</textarea><button class="btn sm" id="savep">Use my prompt</button></details>`;
    return `<div class="knob card white"><div class="kh"><span class="lbl">${k.label}</span><span class="pills">${pills}</span></div><p class="hint">${k.line}</p>${more}</div>`;
  }).join('');
  $('#knobs').querySelectorAll('button[data-k]').forEach((b) => { b.onclick = () => { const v = JSON.parse(b.dataset.v); const c2 = JSON.parse(JSON.stringify(ME.config));
    if (b.dataset.k === 'tools') c2.tools = v === 'two' ? CAT.two : v === 'all' ? CAT.all : CAT.shipped.tools; else c2[b.dataset.k] = v;
    if (b.dataset.k === 'prompt' && v === 'custom' && !c2.custom_prompt) c2.custom_prompt = CAT.prompts.full;
    setConfig(c2); }; });
  $('#knobs').querySelectorAll('input[data-tool]').forEach((i) => { i.onchange = () => { const c2 = JSON.parse(JSON.stringify(ME.config)); c2.tools = [...$('#knobs').querySelectorAll('input[data-tool]:checked')].map((x) => x.dataset.tool); setConfig(c2); }; });
  const sp = $('#savep'); if (sp) sp.onclick = () => { const c2 = JSON.parse(JSON.stringify(ME.config)); c2.prompt = 'custom'; c2.custom_prompt = $('#customp').value; setConfig(c2); };
  $('#sixline').textContent = ME.changed.length ? 'Changed: ' + ME.changed.join(' · ') : 'Shipped settings.';
}
async function setConfig(c) { try { ME = await DX.api('/api/agent/config', { config: c }); drawKnobs(); loopButtons(); DX.toast(ME.changed.length ? 'Changed: ' + ME.changed.join(' · ') : 'Back to shipped'); } catch (e) { DX.toast(e.message); } }
$('#shipbtn').onclick = () => setConfig(CAT.shipped);
function prog(el, p, label) {
  const want = CAT.jobs.map((j) => j.id);
  const rows = Object.entries(p || {}).map(([who, done]) => `<div class="pr"><span class="lbl">${esc(who)}</span>${want.map((id) => { const d = (done || []).filter((x) => x.id === id); return `<span class="pc ${d.length ? (d.every((x) => x.right) ? 'ok' : 'no') : ''}" title="${id}">${esc(id)}${d.length > 1 ? ' ×' + d.length : ''}</span>`; }).join('')}</div>`).join('');
  el.innerHTML = rows || `<p class="muted small">${label}</p>`;
}
function rowsTable(rows, who) {
  const byId = Object.fromEntries(CAT.jobs.map((j) => [j.id, j]));
  return `<div class="tablewrap"><table><tr><th>Job</th><th>Result</th><th>Why (read from Ledgerline)</th>${who === 'agent' ? '<th class="num">Emma’s messages</th>' : ''}<th class="num">Model calls</th><th class="num">Tool calls</th><th class="num">Tokens in</th><th class="num">Seconds</th><th class="num">Cost</th></tr>
  ${rows.map((r) => `<tr><td><b>${esc(byId[r.id] ? byId[r.id].title : r.id)}</b></td><td>${r.failed ? '<span class="chip mute">no answer</span>' : r.right ? '<span class="chip right">right</span>' : '<span class="chip wrong">wrong</span>'}</td><td class="small">${esc(r.why)}${r.stopped_at ? ` <span class="muted">· stopped at “${esc(r.stopped_at)}”</span>` : ''}${r.ends ? ` <span class="muted">· ${esc(r.ends.join(', '))}</span>` : ''}</td>${who === 'agent' ? `<td class="num">${r.emma_turns}</td>` : ''}<td class="num">${r.model_calls}</td><td class="num">${r.tool_calls}</td><td class="num">${num(r.tokens_in)}</td><td class="num">${r.seconds}</td><td class="num">${DX.usd(r.usd)}</td></tr>`).join('')}</table></div>`;
}
function drawSix() {
  const last = ME.six[ME.six.length - 1];
  $('#sixout').innerHTML = last ? `<div class="score"><span class="big">${last.totals.right}<small> / ${last.totals.of}</small></span><span>right · ${last.totals.model_calls} model calls · ${num(last.totals.tokens_in)} tokens · ${DX.usd(last.totals.usd)} · settings: ${esc(last.settings.join(', ') || 'shipped')}</span></div>${rowsTable(last.rows, 'agent')}` : '';
  $('#sixruns').innerHTML = ME.six.length ? `<tr><th>Run</th><th>Settings</th><th class="num">Right</th><th class="num">Model calls</th><th class="num">Tool calls</th><th class="num">Tokens in</th><th class="num">Cost</th></tr>` +
    ME.six.slice().reverse().map((r) => `<tr><td>#${r.n}</td><td>${esc(r.settings.join(' · ') || 'shipped')}</td><td class="num"><b>${r.totals.right}</b> / ${r.totals.of}</td><td class="num">${r.totals.model_calls}</td><td class="num">${r.totals.tool_calls}</td><td class="num">${num(r.totals.tokens_in)}</td><td class="num">${DX.usd(r.totals.usd)}</td></tr>`).join('') : '<tr><td class="muted">No runs yet.</td></tr>';
}
$('#sixbtn').onclick = async () => {
  const b = $('#sixbtn'); b.disabled = true;
  try { const j0 = await DX.api('/api/six', {}); const j = await DX.poll(j0.id, (x) => prog($('#sixprog'), x.progress, 'Starting six fresh sandboxes…'));
    if (j.state === 'failed') DX.toast(j.error, 6000); await refresh(); drawSix(); }
  catch (e) { DX.toast(e.message); } finally { b.disabled = false; }
};

/* ------------------------------------------------------------------ 3 · your workflow */
function drawBlocks() {
  const B = CAT.blocks, list = ME.blocks;
  $('#wfchanged').textContent = ME.blocks_changed.length ? 'Changed: ' + ME.blocks_changed.join(' · ') : 'The shipped workflow';
  $('#blocks').innerHTML = list.map((b, i) => { const d = B[b.block];
    let opt = '';
    if (b.block === 'cert') opt = `<select data-o="on_fail" data-i="${i}"><option value="stop"${b.on_fail === 'stop' ? ' selected' : ''}>if not certified: stop</option><option value="switch"${b.on_fail === 'switch' ? ' selected' : ''}>if not certified: use the preferred supplier</option></select>`;
    if (b.block === 'stock') opt = `<select data-o="stop_days" data-i="${i}">${[0, 7, 14, 30].map((d2) => `<option value="${d2}"${b.stop_days === d2 ? ' selected' : ''}>${d2 ? `stop if cover ≥ ${d2} days` : 'never stop here'}</option>`).join('')}</select>`;
    if (['request', 'order', 'release'].includes(b.block)) opt = `<select data-o="retries" data-i="${i}">${[0, 1, 2].map((r) => `<option value="${r}"${b.retries === r ? ' selected' : ''}>${r} ${r === 1 ? 'retry' : 'retries'} on a lost reply</option>`).join('')}</select>`;
    return `<li class="blk k-${d.kind}"><span class="bn">${i + 1}</span><div class="bb"><b>${esc(d.title)}</b><span class="kt">${esc(d.kind)}</span><p class="hint">${esc(d.line)}</p><p class="nd small">needs <code>${d.needs.join('</code> <code>') || '—'}</code> · gives <code>${d.gives.join('</code> <code>') || '—'}</code></p>${opt}</div>
      <div class="bc"><button class="btn ghost sm" data-m="-1" data-i="${i}" ${i ? '' : 'disabled'} aria-label="Move up">↑</button><button class="btn ghost sm" data-m="1" data-i="${i}" ${i < list.length - 1 ? '' : 'disabled'} aria-label="Move down">↓</button><button class="btn ghost sm" data-x="${i}" aria-label="Remove">✕</button></div></li>`; }).join('');
  const missing = Object.keys(B).filter((k) => !list.some((b) => b.block === k));
  $('#palette').innerHTML = missing.length ? `<span class="lbl">Add a block</span> ${missing.map((k) => `<button class="pill sm" data-add="${k}">+ ${esc(B[k].title)}</button>`).join('')}` : '';
  $('#blocks').querySelectorAll('[data-m]').forEach((x) => { x.onclick = () => { const l = JSON.parse(JSON.stringify(list)), i = +x.dataset.i, j = i + +x.dataset.m; [l[i], l[j]] = [l[j], l[i]]; setBlocks(l); }; });
  $('#blocks').querySelectorAll('[data-x]').forEach((x) => { x.onclick = () => { const l = JSON.parse(JSON.stringify(list)); l.splice(+x.dataset.x, 1); setBlocks(l); }; });
  $('#blocks').querySelectorAll('select[data-o]').forEach((s) => { s.onchange = () => { const l = JSON.parse(JSON.stringify(list)); const v = s.value; l[+s.dataset.i][s.dataset.o] = isNaN(+v) ? v : +v; setBlocks(l); }; });
  $('#palette').querySelectorAll('[data-add]').forEach((x) => { x.onclick = () => { const l = JSON.parse(JSON.stringify(list)); const at = CAT.shipped_blocks.findIndex((b) => b.block === x.dataset.add); const pos = l.filter((b) => CAT.shipped_blocks.findIndex((s) => s.block === b.block) < at).length; l.splice(pos, 0, { block: x.dataset.add }); setBlocks(l); }; });
  $('#wfjob').innerHTML = CAT.jobs.map((j) => `<option value="${j.id}">${esc(j.title)}: ${esc(j.text.slice(0, 70))}…</option>`).join('') + '<option value="own">Your own words…</option>';
}
async function setBlocks(l) { try { ME = await DX.api('/api/workflow', { blocks: l }); drawBlocks(); } catch (e) { DX.toast(e.message); } }
$('#wfship').onclick = () => setBlocks(CAT.shipped_blocks);
$('#wfjob').onchange = () => $('#wftext').classList.toggle('hide', $('#wfjob').value !== 'own');
const ST = { done: 'done', stopped: 'stopped here', waiting: 'waiting', error: 'broken' };
function drawRun(run) {
  WRUN = run;
  if (!run) { $('#wfrunview').innerHTML = ''; return; }
  $('#wfnext').classList.toggle('hide', run.status !== 'running');
  $('#wfresume').classList.toggle('hide', run.status !== 'waiting');
  const next = run.status === 'running' ? run.blocks[run.at] : null;
  $('#wfrunview').innerHTML = `<div class="card white wfrun"><div class="rh"><span class="lbl">Run ${esc(run.id)}</span><span class="chip ${run.status === 'done' ? 'right' : run.status === 'waiting' ? 'wait' : run.status === 'running' ? 'info' : 'wrong'}">${esc(run.status)}</span><span class="muted small">${run.model_calls} model call · ${run.tool_calls} tool calls · ${num(run.tokens_in)} tokens · ${DX.usd(run.usd)}</span></div>
    <p class="small"><b>Emma:</b> ${esc(run.text)}</p>
    <ol class="rsteps">${run.steps.map((s) => `<li class="rs s-${s.status}"><span class="bn">${s.n}</span><div><b>${esc(s.title)}</b> <span class="chip ${s.status === 'done' ? 'right' : s.status === 'waiting' ? 'wait' : 'wrong'}">${esc(ST[s.status] || s.status)}</span> <span class="small">${esc(s.note || '')}</span>
      ${s.got ? `<pre class="json small">${DX.json(s.got)}</pre>` : ''}${s.calls.map((c) => `<details class="call"><summary><code class="tn">${esc(c.name)}</code><span class="args">${esc(JSON.stringify(c.args))}</span>${c.ok ? '<span class="chip right">ok</span>' : '<span class="chip wrong">ok: false</span>'}${c.attempt > 1 ? `<span class="chip wait">attempt ${c.attempt}</span>` : ''}</summary><pre class="json">${DX.json(c.result, 2000)}</pre></details>`).join('')}</div></li>`).join('')}
    ${next ? `<li class="rs s-next"><span class="bn">${run.at + 1}</span><div><b>${esc(CAT.blocks[next.block].title)}</b> <span class="muted small">next</span></div></li>` : ''}</ol>
    ${run.status === 'waiting' ? `<div class="saved"><span class="lbl">A waiting run is a document</span><p>This run is saved as <b>${num(run.saved_bytes)} bytes of JSON</b>. Nothing is running while it waits. Open <a href="#" class="openinbox">Daniel's inbox</a>, sign it as Daniel, then press <b>Resume</b>: the approval step reads Ledgerline again.</p></div>` : ''}
    ${run.reply && run.status !== 'running' ? `<div class="msg ag"><span class="who-a">The workflow</span>${esc(run.reply)}</div>` : ''}</div>`;
  $('#wfrunview').querySelectorAll('.openinbox').forEach((a) => { a.onclick = (e) => { e.preventDefault(); openInbox(); }; });
}
function drawWfRuns() { drawRun(WRUN && ME.wruns.find((r) => r.id === WRUN.id) || ME.wruns[0] || null); }
async function wf(btn, path, body) { btn.disabled = true; try { const r = await DX.api(path, body); drawRun(r); } catch (e) { DX.toast(e.message, 5000); } finally { btn.disabled = false; await refresh(); inboxCount(); } }
const wfBody = (step) => ({ job: $('#wfjob').value === 'own' ? '' : $('#wfjob').value, text: $('#wftext').value, flaky: $('#wfflaky').checked, step });
$('#wfrun').onclick = () => wf($('#wfrun'), '/api/workflow/run', wfBody(false));
$('#wfstep').onclick = () => wf($('#wfstep'), '/api/workflow/run', wfBody(true));
$('#wfnext').onclick = () => wf($('#wfnext'), '/api/workflow/step', { run: WRUN.id });
$('#wfresume').onclick = () => wf($('#wfresume'), '/api/workflow/resume', { run: WRUN.id });

/* ------------------------------------------------------------------ 4 · the race */
function drawRaces() {
  const r = ME.last_race;
  if (r) {
    const T = r.totals, byId = Object.fromEntries(CAT.jobs.map((j) => [j.id, j]));
    const cell = (x) => !x ? '<td>–</td>' : `<td><span class="chip ${x.failed ? 'mute' : x.right ? 'right' : 'wrong'}">${x.failed ? 'no answer' : x.right ? 'right' : 'wrong'}</span><div class="small muted">${x.model_calls} model · ${x.tool_calls} tools · ${num(x.tokens_in)} tok · ${x.seconds} s</div><div class="small">${esc(x.why.split(' · ')[0])}</div></td>`;
    const ag = (id) => r.agent.filter((x) => x.id === id);
    $('#raceout').innerHTML = `<div class="duel"><div class="side wf"><span class="lbl">Your workflow</span><span class="big">${T.workflow.right}<small> / ${T.workflow.of}</small></span><span class="small">${T.workflow.model_calls} model calls · ${num(T.workflow.tokens_in)} tokens · ${DX.usd(T.workflow.usd)} · ${T.workflow.seconds} s</span></div><div class="vs">vs</div><div class="side ag"><span class="lbl">Your agent${r.repeats > 1 ? ' (×' + r.repeats + ')' : ''}</span><span class="big">${T.agent.right}<small> / ${T.agent.of}</small></span><span class="small">${T.agent.model_calls} model calls · ${num(T.agent.tokens_in)} tokens · ${DX.usd(T.agent.usd)} · ${T.agent.seconds} s</span></div></div>
      <div class="tablewrap"><table class="racet"><tr><th>Job</th><th>Workflow</th>${Array.from({ length: r.repeats }, (_, k) => `<th>Agent${r.repeats > 1 ? ' run ' + (k + 1) : ''}</th>`).join('')}${r.repeats > 1 ? '<th>Same path?</th>' : ''}</tr>
      ${CAT.jobs.map((j) => `<tr><td><b>${esc(j.title)}</b><div class="small muted">${esc(j.right)}</div></td>${cell(r.workflow.find((x) => x.id === j.id))}${ag(j.id).sort((a, b) => a.repeat - b.repeat).map(cell).join('')}${r.repeats > 1 ? `<td>${r.same_path[j.id] ? '<span class="chip right">same</span>' : '<span class="chip wait">varied</span>'}</td>` : ''}</tr>`).join('')}</table></div>
      <p class="hint">Settings: agent ${esc(r.settings.join(', ') || 'shipped')}; workflow ${esc(r.blocks.join(', ') || 'shipped')}.</p>`;
  }
  $('#races').innerHTML = ME.races.length ? `<tr><th>Race</th><th>Agent settings</th><th>Workflow</th><th class="num">Workflow right</th><th class="num">Agent right</th><th class="num">Workflow tokens</th><th class="num">Agent tokens</th></tr>` +
    ME.races.slice().reverse().map((x) => `<tr><td>#${x.n}</td><td>${esc(x.settings.join(' · ') || 'shipped')}</td><td>${esc(x.blocks.join(' · ') || 'shipped')}</td><td class="num"><b>${x.totals.workflow.right}</b> / ${x.totals.workflow.of}</td><td class="num"><b>${x.totals.agent.right}</b> / ${x.totals.agent.of}</td><td class="num">${num(x.totals.workflow.tokens_in)}</td><td class="num">${num(x.totals.agent.tokens_in)}</td></tr>`).join('') : '<tr><td class="muted">No races yet.</td></tr>';
}
$('#racebtn').onclick = async () => {
  const b = $('#racebtn'); b.disabled = true;
  try { const j0 = await DX.api('/api/race', { repeats: $('#race3').checked ? 3 : 1 }); const j = await DX.poll(j0.id, (x) => prog($('#raceprog'), x.progress, 'Twelve fresh sandboxes are starting…'), 1500);
    if (j.state === 'failed') DX.toast(j.error, 6000); await refresh(); drawRaces(); }
  catch (e) { DX.toast(e.message); } finally { b.disabled = false; }
};

/* ------------------------------------------------------------------ Daniel's inbox */
async function inboxCount() { try { const d = await DX.api('/api/inbox'); const n = d.waiting.length; $('#inboxn').textContent = n; $('#inboxn').classList.toggle('hide', !n); return d; } catch (e) { return null; } }
function docsTable(docs) {
  const rows = docs.requests.map((p) => `<tr><td><code>${esc(p.pr_no)}</code></td><td>${num(p.qty)} ${esc(p.itm_cd)}</td><td>${esc(p.cc_cd)}</td><td>${esc(p.status)}</td><td>${esc(p.approved_by || '')}</td></tr>`)
    .concat(docs.orders.map((o) => `<tr><td><code>${esc(o.po_no)}</code></td><td>${num(o.qty)} ${esc(o.itm_cd)} · ${esc(o.sup_cd)}</td><td>${esc(o.cc_cd)}</td><td>${esc(o.status)}</td><td>${esc(o.approved_by || '')}</td></tr>`));
  return rows.length ? `<div class="tablewrap"><table><tr><th>Document</th><th>What</th><th>Cost centre</th><th>Status</th><th>Approved by</th></tr>${rows.join('')}</table></div>` : '<p class="muted small">Nothing saved in your sandbox yet.</p>';
}
async function openInbox() {
  $('#drawer').classList.remove('hide');
  const d = await inboxCount(); if (!d) return;
  $('#drbody').innerHTML = d.waiting.length ? d.waiting.map((w) => `<div class="card white wait1"><div><code>${esc(w.doc_no)}</code> · ${num(w.quantity)} ${esc(w.item_code)} · £${num(Math.round(w.value))}<div class="small muted">raised by ${esc(w.requested_by)} on ${esc(String(w.requested_on).slice(0, 10))}</div></div><div class="row"><button class="btn sky sm" data-sign="${esc(w.doc_no)}">Approve as Daniel</button><button class="btn ghost sm" data-rej="${esc(w.doc_no)}">Reject</button></div></div>`).join('') : '<p class="muted">Nothing waits for Daniel in your sandbox.</p>';
  $('#drdocs').innerHTML = docsTable(d.docs);
  $('#drbody').querySelectorAll('[data-sign],[data-rej]').forEach((b) => { b.onclick = async () => {
    const doc = b.dataset.sign || b.dataset.rej; b.disabled = true;
    try { const r = await DX.api('/api/inbox/sign', { doc_no: doc, decision: b.dataset.rej ? 'reject' : 'approve' }); DX.toast(r.result.ok ? `${doc}: ${r.result.status} (signed as Daniel)` : r.result.error, 5000); } catch (e) { DX.toast(e.message); }
    openInbox(); }; });
}
$('#inboxbtn').onclick = openInbox;
$('#drclose').onclick = () => $('#drawer').classList.add('hide');

boot();
})();
