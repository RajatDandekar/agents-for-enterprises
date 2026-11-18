/* Live figures for Lecture 6 · Observability and Evals (v2, 16 Nov; the guard figures stay for the parked Lecture 7 deck). Loaded after figdata.js (window.L6, written by
   gen_figdata.py from experiments/logs), before plates.js. A figure: FIGS.name = (el) => ({ step(k) }), k = the number of
   .step elements shown on its slide. Every number about our system comes from window.L6; a missing value shows a labelled
   slot ("from the run"), never a typed number. Facts about other tools are on the slides, sourced in NOTES.md. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const L = () => window.L6 || {};
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => (n == null ? '–' : Number(n).toLocaleString('en-GB'));
const get = (path) => { let v = L(); for (const k of String(path).split('.')) v = v == null ? v : v[k]; return v; };
const at = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('l6-hide', +x.dataset.k > k));
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">From the run</span><div>${esc(what)}</div><div class="todo-s">Fills in from <code>experiments/logs</code> after <code>python3 gen_figdata.py</code>.</div></div>`; return { step() {} }; };
const ms = (v) => (v == null ? '–' : v < 1000 ? Math.round(v) + ' ms' : (v / 1000).toFixed(1) + ' s');
const usd = (v) => (v == null ? '–' : '$' + Number(v).toFixed(v < 0.1 ? 4 : 2));
const pct = (v) => (v == null ? '–' : Math.round(v * 100) + '%');
let uid = 0;
const svgOpen = (w, h) => { const id = `l6a${++uid}`; return [id, `<svg class="l6-svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><defs><marker id="${id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>`]; };
const R = (x, y, w, h, cls = '', rx = 16) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" class="bx ${cls}"/>`;
const T = (x, y, s, cls = 't2', anchor = '') => `<text x="${x}" y="${y}" class="${cls}"${anchor ? ` text-anchor="${anchor}"` : ''}>${s}</text>`;
const TL = (x, y, lines, cls = 't2', lh = 22, anchor = '') => lines.map((s, i) => T(x, y + i * lh, s, cls, anchor)).join('');
const A = (d, id, cls = '') => `<path d="${d}" class="arr ${cls}" marker-end="url(#${id})"/>`;
const G = (k, inner) => `<g data-k="${k}">${inner}</g>`;

/* ------------------------------------------------------------------ text from the data: <span data-l6="m.x.y" data-f="n|usd|pct|s|ms"> */
FIGS._fill = () => {
  document.querySelectorAll('[data-l6]').forEach((s) => {
    let v = get(s.dataset.l6);
    if (v == null || v === '') { s.innerHTML = '<span class="todo-in">from the run</span>'; return; }
    const f = s.dataset.f;
    if (f === 'link') { s.innerHTML = `<a href="${esc(v)}" target="_blank" rel="noopener">${esc(s.dataset.text || 'open')}</a>`; return; }   // a link with our own words
    if (f === 'url') { s.innerHTML = `<a href="${esc(v)}" target="_blank" rel="noopener">${esc(String(v).replace(/^https?:\/\//, ''))}</a>`; return; }
    if (f === 'pf') { s.innerHTML = v ? '<span class="x3-ok">pass</span>' : '<span class="x3-no">fail</span>'; return; }
    s.textContent = f === 'n' ? fmt(v) : f === 'usd' ? usd(v) : f === 'usd2' ? '$' + Number(v).toFixed(2) : f === 'pct' ? pct(v) : f === 's' ? Number(v).toFixed(1) + ' s' : f === 'ms' ? ms(v) : f === 'k' ? Number(v).toFixed(2) : String(v);
  });
};

/* ------------------------------------------------------------------ a screenshot (optionally cropped: x,y,w,h in image px) */
FIGS.shot = (el) => {
  const src = el.dataset.src || '', label = el.dataset.label || '', media = get('media') || [];
  const slot = () => { el.innerHTML = el.dataset.pending
    ? `<div class="slot pend"><span class="slot-k">Screenshot pending · ${esc(el.dataset.pending)}</span><div class="slot-l">${esc(label)}</div><div class="slot-f">Shown live in class. The capture lands as <code>${esc(src)}</code> and fills this plate.</div></div>`
    : `<div class="slot"><span class="slot-k">Screenshot · our run</span><div>${esc(label)}</div><div class="slot-f">lands as <code>${esc(src)}</code></div></div>`; };
  if (!media.includes(src)) { slot(); return { step() {} }; }
  const crop = (el.dataset.crop || '').split(',').map(Number);
  if (crop.length !== 4 || crop.some(isNaN)) { el.innerHTML = `<img class="shot-i" src="${esc(src)}" alt="${esc(label)}">`; el.querySelector('img').onerror = slot; return { step() {} }; }
  const [x, y, w, h] = crop;
  el.innerHTML = `<div class="shot-c"><div class="shot-cw" role="img" aria-label="${esc(label)}"></div></div>`;
  const box = el.querySelector('.shot-cw'), img = new Image();
  const lay = () => { const W = el.clientWidth, H = el.clientHeight; if (!W || !H || !img.naturalWidth) return; const s = Math.min(W / w, H / h);
    Object.assign(box.style, { width: `${w * s}px`, height: `${h * s}px`, backgroundImage: `url("${src}")`, backgroundSize: `${img.naturalWidth * s}px auto`, backgroundPosition: `${-x * s}px ${-y * s}px` }); };
  img.onload = lay; img.onerror = slot; img.src = src;
  return { step() { lay(); } };
};

/* ------------------------------------------------------------------ a measured table: data-path, data-cols="key:Label:fmt|..." */
FIGS.mtab = (el) => {
  let rows = get(el.dataset.path);
  if (Array.isArray(rows) && el.dataset.ids) { const ids = el.dataset.ids.split(','); rows = rows.filter((r) => ids.includes(r.id)); }
  if (!Array.isArray(rows) || !rows.length) return need(el, el.dataset.what || 'Measured table');
  const cols = el.dataset.cols.split('|').map((c) => c.split(':'));
  const f = (v, t) => (v == null ? '–' : t === 'k' ? Number(v).toFixed(2) : t === 'n' ? fmt(v) : t === 'usd' ? usd(v) : t === 'pct' ? pct(v) : t === 'b' ? (v ? '<span class="ok">yes</span>' : '<span class="no">no</span>') : t === 'bx' ? (v ? '<span class="no">got through</span>' : '<span class="ok">held</span>') : t === 'list' ? esc((v || []).join(', ') || '–') : esc(v));
  const lim = +(el.dataset.limit || 99);
  el.innerHTML = `<div class="l6-tw">${el.dataset.mk ? `<span class="l6-mk">${esc(el.dataset.mk)}</span>` : ''}<table class="l6t ${el.dataset.sm ? 'sm' : ''} ${el.dataset.xs ? 'xs' : ''}"><tr>${cols.map(([, l, t]) => `<th class="${t && !['x', 'list'].includes(t) ? 'n' : ''}">${esc(l)}</th>`).join('')}</tr>
    ${rows.slice(0, lim).map((r) => `<tr>${cols.map(([k, , t]) => `<td class="${t && !['x', 'list'].includes(t) ? 'n' : ''}">${f(k.split('.').reduce((o, kk) => (o == null ? o : o[kk]), r), t)}</td>`).join('')}</tr>`).join('')}</table></div>`;
  return { step() {} };
};

/* ------------------------------------------------------------------ horizontal bars: data-bars='[["label","path","cls","max"]...]' fmt: data-f */
FIGS.bars = (el) => {
  const spec = JSON.parse(el.dataset.bars), f = el.dataset.f || 'pct';
  const vals = spec.map(([, p]) => (typeof p === 'number' ? p : get(p)));
  if (vals.some((v) => v == null)) return need(el, el.dataset.what || 'Measured bars');
  const max = +(el.dataset.max || Math.max(...vals, 1e-9));
  const ofs = spec.map(([, , , , o]) => (o == null ? null : typeof o === 'number' ? o : get(o)));   // optional: “3 of 20”, drawn as 3/20
  el.innerHTML = `<div class="l6-bars" style="--lw:${el.dataset.lw || 330}px">${spec.map(([lab, , cls, sub], i) => `<div class="l6-bar" data-i="${i}"><span class="lb">${lab}${sub ? `<br><small style="color:var(--ink-3);font-size:14px">${sub}</small>` : ''}</span><span class="tr"><i class="${cls || ''}" style="width:0%"></i></span><span class="v">${ofs[i] ? `${vals[i]} of ${ofs[i]}` : f === 'pct' ? pct(vals[i]) : f === 'n' ? fmt(vals[i]) : f === 'usd' ? usd(vals[i]) : f === 'frac' ? vals[i] : vals[i]}</span></div>`).join('')}</div>`;
  const steps = (el.dataset.steps || '').split(',').map(Number);   // bar i appears at step steps[i] (default 0)
  return { step(k) { el.querySelectorAll('.l6-bar').forEach((b, i) => { const s = steps[i] || 0; b.classList.toggle('hide', s > k); b.querySelector('i').style.width = (s > k ? 0 : Math.max(0.5, 100 * vals[i] / (ofs[i] || max))) + '%'; }); } };
};

/* ------------------------------------------------------------------ the real trace: data-path (rows from gen_figdata slim_tree) */
const ICON = { invoke_agent: '◆', chat: '✦', execute_tool: '⚒', guardrail: '⛨', span: '·' };
FIGS.trace = (el) => {
  const rows = get(el.dataset.path || 'm.incident.trace');
  if (!Array.isArray(rows) || !rows.length) return need(el, 'The span tree of our incident trace');
  const total = Math.max(1, ...rows.map((r) => r.end));
  const mode = el.dataset.mode || 'plain';
  el.innerHTML = `<div class="l6-trace" style="--nw:${el.dataset.nw || 470}px"><div class="hd"><span>span</span><span>time, 0 to ${ms(total)}</span><span style="text-align:right">tokens · cost</span></div>${rows.map((r, i) => {
    const tg = r.confirm === true ? `<span class="tg bad">confirm=true</span>` : r.preview ? `<span class="tg warn">preview</span>` : r.refused ? `<span class="tg bad">refused</span>` : r.decision ? `<span class="tg ${/refused|blocked|flagged|quarantined/.test(r.decision) ? 'bad' : 'ok'}">${esc(r.decision)}</span>` : '';
    return `<div class="r k-${r.kind}" data-i="${i}"><span class="nm" style="padding-left:${r.depth * 18}px"><i>${ICON[r.kind] || '·'}</i>${esc(r.name)}${tg}</span><span class="bar"><b style="left:${100 * r.start / total}%;width:${Math.max(0.5, 100 * (r.end - r.start) / total)}%"></b></span><span class="t">${r.tin ? fmt(r.tin) + ' · ' + usd(r.usd) : ms(r.end - r.start)}</span></div>`; }).join('')}</div>`;
  const rs = [...el.querySelectorAll('.r')];
  return { step(k) {
    if (mode !== 'find') return;
    // find mode: 0 all; 1 tools only; 2 the preview; 3 the commit
    rs.forEach((r, i) => { const x = rows[i]; r.classList.remove('dim', 'hot', 'prev');
      if (k >= 1 && x.kind !== 'execute_tool' && x.kind !== 'invoke_agent') r.classList.add('dim');
      if (k >= 2 && x.name.endsWith('create_purchase_request') && x.confirm !== true) r.classList.add('prev');
      if (k >= 2 && !x.name.endsWith('create_purchase_request') && x.kind === 'execute_tool') r.classList.add('dim');
      if (k >= 3 && x.confirm === true) r.classList.add('hot'); });
  } };
};

/* ------------------------------------------------------------------ one span as a record (the commit span) */
FIGS.spanrec = (el) => {
  const s = get(el.dataset.path || 'm.incident.commit_span');
  if (!s) return need(el, 'The commit span from our trace');
  const a = s.attributes || {};
  const args = a['gen_ai.tool.call.arguments'] || {};
  const rows = [['name', s.name, 0], ['trace_id', s.trace_id.slice(0, 16) + '…', 1], ['span_id', s.span_id, 1], ['parent_id', s.parent_id + '  (invoke_agent)', 1],
    ['start', s.start.replace('T', ' ').slice(0, 23), 2], ['end', s.end.replace('T', ' ').slice(0, 23), 2],
    ['gen_ai.operation.name', a['gen_ai.operation.name'], 3], ['gen_ai.tool.name', a['gen_ai.tool.name'], 3], ['gen_ai.tool.call.id', String(a['gen_ai.tool.call.id'] || '').slice(0, 26), 3],
    ['…call.arguments', JSON.stringify(args), 4, true], ['…call.result', `request_no ${a['ledgerline.receipt.request_no'] || '–'}, status ${a['ledgerline.receipt.status'] || '–'}`, 4, true], ['status', s.status || 'UNSET', 2]];
  el.innerHTML = `<div class="l6-span">${rows.map(([k, v, g, hl]) => `<div class="sr${hl ? ' hl' : ''}" data-g="${g}"><span class="key">${esc(k)}</span><span class="val">${esc(v)}</span></div>`).join('')}</div>`;
  return { step(k) { el.querySelectorAll('.sr').forEach((r) => r.classList.toggle('dim', +r.dataset.g > k)); } };
};

/* ------------------------------------------------------------------ the suite grid */
FIGS.grid = (el) => {
  const g = get('m.suite.grid');
  if (!g) return need(el, 'The suite, task by task');
  const head = ['good · run 1', 'good · run 2', 'good · run 3', 'Thursday · run 1'];
  el.innerHTML = `<div class="l6-grid" style="grid-template-columns:330px repeat(4,1fr)"><span></span>${head.map((h) => `<span class="hd">${h}</span>`).join('')}
    ${g.map((r) => `<span class="lb">${r.task} · ${esc(r.title)}</span>${r.cells.map((c, i) => `<span class="c ${c || 'e'}" title="${esc(r.why[i] || '')}">${c === 'p' ? '✓' : c === 'f' ? '✕' : '–'}</span>`).join('')}`).join('')}</div>`;
  return { step() {} };
};

/* ------------------------------------------------------------------ a confusion matrix for one judge: data-judge=naive|specific|grounded */
FIGS.cm = (el) => {
  const s = get(`m.calib.summary.${el.dataset.judge}`);
  if (!s) return need(el, 'Judge against labels');
  const c = s.confusion;
  el.innerHTML = `<div class="l6-cm"><span></span><span class="h">the judge passed it</span><span class="h">the judge failed it</span>
    <span class="h">a person: right (${s.real})</span><div class="c ok"><b>${c.label_pass_judge_pass}</b><span>agree</span></div><div class="c no"><b>${c.label_pass_judge_fail}</b><span>false alarm${c.label_pass_judge_fail === 1 ? '' : 's'}</span></div>
    <span class="h">a person: wrong (${s.planted})</span><div class="c no"><b>${c.label_fail_judge_pass}</b><span>missed</span></div><div class="c ok"><b>${c.label_fail_judge_fail}</b><span>caught</span></div></div>
    <p class="x3-pl">Caught <b>${c.label_fail_judge_fail} of ${s.planted}</b> wrong replies.<br><b>${c.label_pass_judge_fail} false alarm${c.label_pass_judge_fail === 1 ? '' : 's'}</b> in ${s.real} right ones.</p>`;
  return { step() {} };
};

/* ------------------------------------------------------------------ the chat Emma saw */
FIGS.chat = (el) => {
  // the run the class then sees traced in Argus, LangSmith, Langfuse and Sentry (m.demo.incident); the first recorded incident if it is missing
  const dm = get('m.demo.incident'), b = dm && dm.reply ? dm : get('m.incident.bad'), msg = (dm && dm.reply && dm.text) || get('m.incident.msg_dated');
  if (!b) return need(el, 'The chat from our run');
  const rep = String(b.reply || '').replace(/\*\*/g, '');
  el.innerHTML = `<div class="l6-chat"><div class="bu me"><span class="who">Emma · Fri 20 Nov, 09:10</span>${esc(msg)}</div><div class="bu bot"><span class="who">Ask Northbridge</span>${esc(rep)}</div></div>`;
  return { step() {} };
};

/* ------------------------------------------------------------------ the prompt diff (good → Thursday), only the changed bullets and context */
FIGS.diff = (el) => {
  const p = get('m.prompts');
  if (!p) return need(el, 'The prompt diff');
  const A0 = p.good.split('\n'), B0 = p.thursday.split('\n');
  const from = A0.findIndex((l) => l.startsWith('- What you know')), to = A0.findIndex((l) => l.startsWith('- Her saved routines'));
  const a = A0.slice(from, to), bfrom = B0.findIndex((l) => l.startsWith('- What you know')), bto = B0.findIndex((l) => l.startsWith('- Her saved routines'));
  const b = B0.slice(bfrom, bto);
  el.innerHTML = `<div class="l6-diff"><div class="dl ctx">How you work  ·  …</div>${a.map((l) => `<div class="dl ${b.includes(l) ? 'ctx' : 'del'}" data-k="0">${esc(l)}</div>`).join('')}${b.filter((l) => !a.includes(l)).map((l) => `<div class="dl add" data-k="1">${esc(l)}</div>`).join('')}<div class="dl ctx">- Her saved routines are tools … (unchanged)</div></div>`;
  return { step(k) { at(el, k); } };
};

/* ================================================================== diagrams */
/* logs, metrics, traces: three views of the same Friday */
FIGS.signals = (el) => {
  const [id, o] = svgOpen(1400, 470);
  el.innerHTML = o + G(0, R(0, 0, 440, 470, '', 22) + T(28, 46, 'LOGS · lines of text', 't3') + TL(28, 90, ['09:10:04 INFO  chat request user=ECLARKE', '09:10:07 INFO  tool find_item ok', '09:10:13 INFO  tool create_purchase_request ok', '09:10:16 INFO  tool create_purchase_request ok', '09:10:19 INFO  reply sent (612 chars)'], 'tm', 30) + TL(28, 300, ['Every event, as text. Which line belongs', 'to which turn? What were the arguments?', 'You grep, and you guess.'], 't2', 26))
    + G(1, R(480, 0, 440, 470, 'a', 22) + T(508, 46, 'METRICS · numbers over time', 't3') + TL(508, 96, (() => { const d = get('m.online.dashboard.good') || {}, c = get('m.online.cost_per_conversation_usd') || {}; return [`turns (good prompt)    ${fmt(d.turns)}`, `latency p50            ${d.latency_p50_s ?? '–'} s`, `latency p95            ${d.latency_p95_s ?? '–'} s`, `cost per conversation  $${c.mean ?? '–'}`]; })(), 'tm', 34) + TL(508, 300, ['Cheap to keep, good for alerts.', 'They say THAT something changed,', 'never WHICH turn, or WHY.'], 't2', 26))
    + G(2, R(960, 0, 440, 470, 'g', 22) + T(988, 46, 'TRACES · the steps of one turn', 't3') + TL(988, 96, ['invoke_agent Ask Northbridge', '  chat claude-sonnet-5-5', '  execute_tool find_item', '  execute_tool create_purchase_request', '  execute_tool create_purchase_request', '  chat claude-sonnet-5-5'], 'tm', 30) + TL(988, 320, ['Each step with its parent, timings,', 'arguments and result. This is what', 'answers Henrik\'s first question.'], 't2', 26)) + '</svg>';
  const note = document.createElement('div'); note.className = 'shot-cap'; note.style.cssText = 'left:0;top:478px'; note.textContent = 'Logs: an illustration of the format. Metrics: our own, from the Langfuse traces of our runs (online_evals.json). Traces: our incident turn.'; el.appendChild(note);
  return { step(k) { at(el, k); } };
};

/* OpenTelemetry: instrument once, send anywhere */
FIGS.otel = (el) => {
  const [id, o] = svgOpen(1400, 520);
  const box = (x, y, w, h, cls, t, s) => R(x, y, w, h, cls) + T(x + 20, y + 36, t, 't1') + TL(x + 20, y + 64, s, 't2', 22);
  el.innerHTML = o + G(0, box(0, 40, 330, 190, 'a', 'Your code', ['Ask Northbridge\'s loop, wrapped:', 'agent turn, model call, tool call', 'each opens and closes a span']) + box(0, 290, 330, 150, '', 'OpenTelemetry SDK', ['TracerProvider, spans, context:', 'the parent is found for you']))
    + G(1, A('M330,365 L420,365', id) + box(420, 290, 300, 150, '', 'Span processor', ['Simple (now) or Batch', '(every 1.5 s, in the background)']) + A('M720,365 L800,365', id) + box(800, 290, 280, 150, 'y', 'Exporter · OTLP', ['the open wire format:', 'protobuf over HTTP']))
    + G(2, A('M1080,330 L1150,120', id) + A('M1080,365 L1150,280', id) + A('M1080,400 L1150,440', id) + box(1150, 60, 250, 110, 'g', 'LangSmith', ['traces and evals']) + box(1150, 225, 250, 110, 'g', 'Langfuse', ['traces and evals']) + box(1150, 390, 250, 110, 'g', 'Sentry', ['errors, speed, cost']))
    + G(3, T(420, 80, 'Instrument once, send anywhere.', 't1') + TL(420, 112, ['The names on the spans follow the GenAI semantic', 'conventions, so every tool understands them.', 'One line of code adds or removes a tool.'], 't2', 24)) + '</svg>';
  return { step(k) { at(el, k); } };
};

/* where a guard sits */
FIGS.guardpath = (el) => {
  const [id, o] = svgOpen(1400, 480);
  const st = (x, t, s, cls = '') => R(x, 150, 210, 120, cls) + T(x + 105, 198, t, 't1', 'middle') + TL(x + 105, 226, s, 't2', 22, 'middle');
  const gd = (x, k, t, s) => G(k, R(x, 330, 230, 140, 'b', 14) + T(x + 115, 362, t, 't3', 'middle') + TL(x + 115, 392, s, 't2', 22, 'middle') + A(`M${x + 115},330 L${x + 115},285`, id, 'b'));
  el.innerHTML = o + G(0, st(0, 'Emma', ['types a message']) + A('M210,210 L290,210', id) + st(290, 'the model', ['reads the window,', 'asks for a tool']) + A('M500,210 L580,210', id) + st(580, 'the tool', ['acts in Ledgerline'], 'a') + A('M790,210 L870,210', id) + st(870, 'tool result', ['back to the model'], 'y') + A('M1080,210 L1160,210', id) + st(1160, 'the reply', ['what Emma reads']))
    + G(1, T(700, 60, 'Four places to stand. Words are checked at 1 and 4; actions at 2 and 3.', 't1', 'middle'))
    + gd(10, 1, '1 · INPUT', ['injection classifier,', 'PII masking']) + gd(470, 2, '2 · BEFORE THE TOOL', ['identity, approvals,', 'confirm needs a yes, limits']) + gd(870, 3, '3 · AFTER THE RESULT', ['provenance: outside', 'text is data']) + gd(1160, 4, '4 · OUTPUT', ['numbers from Ledgerline,', 'PII in the reply']) + '</svg>';
  return { step(k) { at(el, k); } };
};

/* an eval, anatomy */
FIGS.evalparts = (el) => {
  const [id, o] = svgOpen(1400, 430);
  const c = (x, k, cls, h, lines) => G(k, R(x, 40, 320, 300, cls) + T(x + 24, 84, h, 't1') + TL(x + 24, 120, lines, 't2', 25));
  el.innerHTML = o + c(0, 0, '', '1 · Input', ['a known sandbox (Ledgerline at', 'Fri 20 Nov 09:10) and the turns:', '', '“Order the usual, please,', 'needed by 4 Dec 2026.”', '“Yes, go ahead.”'])
    + c(360, 1, 'a', '2 · Criteria', ['what “right” means here:', '• one request, 2,400 BAT-500,', '  PRD-03, waiting for Daniel', '• confirm=true only after the yes', '• the reply says it waits, not “done”'])
    + c(720, 2, 'y', '3 · Scorer', ['who checks each criterion:', '• code reads Ledgerline', '• code reads the tool calls', '• a judge model reads the words', '• a person, for the labels'])
    + c(1080, 3, 'g', '4 · Threshold', ['when it passes:', '• every code check, every run', '• judge: pass on its criterion', '• pass^3: all three runs pass', '→ the change may ship'])
    + G(1, A('M320,190 L360,190', id)) + G(2, A('M680,190 L720,190', id)) + G(3, A('M1040,190 L1080,190', id))
    + G(4, T(700, 395, 'Run it on every change, in the same sandbox, with the same inputs: then a difference is the change.', 't1', 'middle')) + '</svg>';
  return { step(k) { at(el, k); } };
};

/* the CI gate */
FIGS.gate = (el) => {
  const [id, o] = svgOpen(1400, 380);
  const b = (x, k, cls, t, s) => G(k, R(x, 60, 240, 170, cls) + T(x + 120, 104, t, 't1', 'middle') + TL(x + 120, 136, s, 't2', 23, 'middle'));
  el.innerHTML = o + b(0, 0, '', 'A change', ['someone edits the', 'system prompt', '(a pull request)']) + G(1, A('M240,145 L300,145', id)) + b(300, 1, 'y', 'CI starts', ['GitHub Actions:', 'install, then run', 'the gate']) + G(2, A('M540,145 L600,145', id))
    + b(600, 2, 'a', 'The gate', ['pytest runs our code', 'checks on the incident', 'tasks, twice each']) + G(3, A('M840,120 L920,80', id, 'a') + A('M840,170 L920,220', id, 'b'))
    + G(3, R(920, 20, 300, 110, 'g') + T(1070, 64, 'all green → merge allowed', 't1', 'middle') + T(1070, 94, 'exit code 0', 'tm', 'middle'))
    + G(3, R(920, 170, 300, 110, 'b') + T(1070, 214, 'a red test → merge blocked', 't1', 'middle') + T(1070, 244, 'exit code 1 (required check)', 'tm', 'middle'))
    + G(4, T(700, 340, 'The judge runs nightly on the whole suite; the gate runs on every change, in minutes, for about a dollar.', 't1', 'middle')) + '</svg>';
  return { step(k) { at(el, k); } };
};

/* error analysis: traces → notes → categories → tasks */
FIGS.errflow = (el) => {
  const [id, o] = svgOpen(1400, 300);
  const b = (x, k, cls, t, s) => G(k, R(x, 40, 300, 200, cls) + T(x + 24, 84, t, 't1') + TL(x + 24, 118, s, 't2', 24));
  el.innerHTML = o + b(0, 0, '', '1 · Read traces', ['every failing run, all its', 'spans: the reply, the calls,', 'the arguments, the results']) + G(1, A('M300,140 L360,140', id))
    + b(360, 1, 'y', '2 · Write a note', ['open coding: one plain line', 'per failure, in your words:', '“asked for the date”']) + G(2, A('M660,140 L720,140', id))
    + b(720, 2, 'a', '3 · Group the notes', ['axial coding: a few named', 'categories, with counts;', 'agent, eval, tool or infra?']) + G(3, A('M1020,140 L1080,140', id))
    + b(1080, 3, 'g', '4 · Fix, then add', ['fix the cause; turn each', 'category into a task in', 'the suite (a golden set)']) + '</svg>';
  return { step(k) { at(el, k); } };
};

/* ================================================================== v2 figures */
/* a span as a card of plain rows: data-path -> {title, rows:[[key, value, step, highlight]]} */
FIGS.kv = (el) => {
  const d = get(el.dataset.path);
  if (!d || !d.rows) return need(el, el.dataset.what || 'One span from our trace');
  el.innerHTML = `<div class="l6-span l6-kv"><div class="kvt">${esc(d.title)}</div>${d.rows.map(([k, v, g, hl]) => `<div class="sr${hl ? ' hl' : ''}" data-g="${g}"><span class="key">${esc(k)}</span><span class="val">${esc(v)}</span></div>`).join('')}</div>`;
  return { step(k) { el.querySelectorAll('.sr').forEach((r) => r.classList.toggle('dim', +r.dataset.g > k)); } };
};

/* a conversation: data-path -> [{who: emma|script|bot, text, tools?, n_tools?}]; data-from/data-to pick turns; data-who names the user */
FIGS.convo = (el) => {
  let t = get(el.dataset.path);
  if (!Array.isArray(t) || !t.length) return need(el, el.dataset.what || 'The conversation from our run');
  t = t.slice(+(el.dataset.from || 0), +(el.dataset.to || 99));
  const who = { emma: el.dataset.who || 'Emma', script: 'Emma (the script)', bot: 'Ask Northbridge' };
  el.innerHTML = `<div class="l6-chat ${el.dataset.sm ? 'sm' : ''}">${t.map((x, i) => `<div class="bu ${x.who === 'bot' ? 'bot' : 'me'}" data-k="${Math.floor(i / 2) * (el.dataset.stepped ? 1 : 0)}"><span class="who">${esc(who[x.who] || x.who)}${x.who === 'bot' && x.n_tools != null ? ` · ${x.n_tools} tool call${x.n_tools === 1 ? '' : 's'}` : ''}</span>${esc(x.text)}${(x.tools || []).map((c) => `<span class="tc ${/save/.test(c) ? 'sv' : ''}">${esc(c)}</span>`).join('')}</div>`).join('')}</div>`;
  return { step(k) { if (el.dataset.stepped) at(el, k); } };
};

/* the same message, run many times: one tile per run (m.incident.nodate_runs) */
FIGS.runs = (el) => {
  const r = get(el.dataset.path || 'm.incident.nodate_runs');
  if (!Array.isArray(r) || !r.length) return need(el, 'The same message, run many times');
  const first = +(el.dataset.first || 5);
  el.innerHTML = `<div class="l6-runs">${r.map((x, i) => `<div class="rn ${x.saved ? 'bad' : 'ok'}" data-k="${i < first ? 0 : 1}"><b>run ${x.i}</b><span>${x.saved ? 'saved it,<br>no yes' : 'asked for<br>the date'}</span><i>${x.tools} tool calls</i></div>`).join('')}</div>`;
  return { step(k) { at(el, k); } };
};

/* simulated conversations: goals down, prompt x persona across (m.convos.grid) */
FIGS.cvgrid = (el) => {
  const g = get('m.convos.grid'), pe = get('m.convos.personas') || [];
  if (!g) return need(el, 'The simulated conversations, goal by goal');
  const head = ['good', 'good', 'Thursday', 'Thursday'].map((p, i) => `${p} · ${pe[i % pe.length] || ''}`);
  el.innerHTML = `<div class="l6-grid cv" style="grid-template-columns:400px repeat(4,1fr)"><span></span>${head.map((h) => `<span class="hd">${esc(h)}</span>`).join('')}
    ${g.map((r) => `<span class="lb">${esc(r.title)}</span>${r.cells.map((c, i) => `<span class="c ${c || 'e'}" data-k="${i < 2 ? 0 : 1}" title="${esc(r.why[i] || '')}">${c === 'p' ? '✓ pass' : c === 'f' ? '✕ fail' : '–'}</span>`).join('')}`).join('')}</div>`;
  return { step(k) { at(el, k); } };
};

/* a notebook, rendered: the executed copy in an iframe (scrolls), or a plate until the run exists */
FIGS.nbframe = (el) => {
  const src = el.dataset.src, runs = get('m.nb_runs') || {}, key = src.replace(/^nb\//, '').replace(/\.html$/, '');
  const have = (get('m.nb_html') || []).includes(src);
  if (!have) { el.innerHTML = `<div class="slot pend"><span class="slot-k">Rendered copy pending · ${esc(el.dataset.pending || 'live run')}</span><div class="slot-l">${esc(el.dataset.label || key)}</div><div class="slot-f">The executed notebook lands as <code>${esc(src)}</code> and fills this plate. In class: open it in Colab.</div></div>`; return { step() {} }; }
  el.innerHTML = `<iframe class="nbf" src="${esc(src)}" title="${esc(el.dataset.label || key)}"></iframe>`;
  const fr = el.querySelector('iframe');
  fr.addEventListener('load', () => { try { const d = fr.contentDocument; const st = d.createElement('style');   // larger type, and no pip chatter, in the embedded copy
    st.textContent = 'body{zoom:1.3;padding:8px 14px!important} .jp-OutputArea-output pre{white-space:pre-wrap!important} .jp-InputPrompt,.jp-OutputPrompt{display:none!important}'; d.head.appendChild(st); } catch (e) { /* another origin: leave it as it is */ } });
  return { step() {} };
};

/* ================================================================== v3 (17 Nov review): one running example for the scorers
   Friday's turn and the good two-turn chat (m.ex, from traces_v2.json and the suite logs), the four boxes, the loop. */
const cap1 = (s) => (s ? String(s).charAt(0).toUpperCase() + String(s).slice(1) : s);

/* the turn as a ledger: Emma's message, the tool calls in order, the reply. data-turns="friday" | "good1,good2" */
FIGS.exturn = (el) => {
  const ex = get('m.ex');
  if (!ex || !ex.friday) return need(el, 'The running example: Friday’s turn and the good chat');
  const names = (el.dataset.turns || 'friday').split(','), good = names[0] !== 'friday', rep = el.dataset.reply !== 'none';
  const label = { friday: 'Friday’s turn · Thursday prompt', good1: 'The good chat · turn 1', good2: 'The good chat · turn 2' };
  let n = 0;
  const held = el.dataset.held, row = get('m.ex.outcome.friday.row') || [];
  el.innerHTML = `<div class="x3-turn${good ? ' good' : ''}">${names.map((nm) => { const t = ex[nm]; if (!t) return '';
    return `<span class="hd">${label[nm]}</span><div class="msg">${esc(t.typed)}</div>${t.rows.map((r) => `<div class="cl ${r.cls}"><i>${++n}</i><code>${esc(r.name)}</code><span>${esc(r.arg)}</span>${r.tag ? `<em class="${r.cls}">${esc(r.tag)}</em>` : '<u></u>'}</div>`).join('')}${rep ? `<div class="rp"><small>The reply ${nm === 'good1' ? 'ends' : 'begins'}</small>${esc(nm === 'good1' ? t.last : t.first)}</div>` : ''}`; }).join('')}${held && row.length ? `<div class="held"><small>Ledgerline now holds</small>${esc(row[0][1])} · ${esc(row[1][1])} · ${esc(row[4][1])}</div>` : ''}</div>`;
  return { step() {} };
};

/* what Ledgerline holds: data-path -> [[label, value]...] */
FIGS.x3row = (el) => {
  const rows = get(el.dataset.path);
  if (!Array.isArray(rows)) return need(el, 'What Ledgerline holds after the turn');
  el.innerHTML = `<div class="x3-row"><span class="x3-k">${esc(el.dataset.title || 'Ledgerline · purchase requests · after the turn')}</span><dl>${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}</dl></div>`;
  return { step() {} };
};

/* one verdict: data-path -> {pass, why|reason}; data-who names the turn */
FIGS.verdict = (el) => {
  const v = get(el.dataset.path);
  if (!v || v.pass == null) return need(el, 'The verdict of this check');
  el.innerHTML = `<div class="x3-vd${el.dataset.row ? ' row' : ''} ${v.pass ? 'p' : 'f'}"><span class="x3-k">${esc(el.dataset.who || '')}</span><b>${v.pass ? 'pass' : 'fail'}</b><p>${el.dataset.noq ? '' : '“'}${esc(cap1(v.why || v.reason))}${el.dataset.noq ? '.' : '”'}</p></div>`;
  return { step() {} };
};

/* numbers: the figures the tools returned, as chips; the reply with each £ figure marked found or not found */
const x3marks = (segs) => segs.map((s) => (s.amt ? `<span class="x3-amt ${s.found ? 'y' : 'n'}">${esc(s.t)}</span>` : esc(s.t))).join('');
FIGS.numcheck = (el) => {
  const d = get('m.ex.numbers');
  if (!d || !d.chips) return need(el, 'Every £ figure of Friday’s reply against the tool results');
  // the first line of the reply, then every line that holds a £ figure; a line left out is shown as "…"
  const keep = d.lines.map((ln, i) => i === 0 || ln.some((s) => s.amt));
  const rows = []; d.lines.forEach((ln, i) => { if (keep[i]) rows.push(`<p>${x3marks(ln)}</p>`); else if (rows[rows.length - 1] !== '<p class="gap">…</p>') rows.push('<p class="gap">…</p>'); });
  el.innerHTML = `<div class="x3-num"><span class="x3-k">What the tools returned in this turn</span><div class="chips">${d.chips.map((c) => `<div class="x3-chip"><b>${esc(c.value)}</b><span>${esc(c.key)}<br>${esc(c.tool)}</span></div>`).join('')}</div>
    <div class="rep"><span class="x3-k">What the agent told Emma · each £ figure looked up above</span>${rows.join('')}</div></div>`;
  return { step() {} };
};
FIGS.numce = (el) => {
  const c = get('m.ex.numbers.counter');
  if (!c) return need(el, 'A reply with a £ figure no tool returned');
  const ls = c.lines || [c.line];
  el.innerHTML = `<div class="x3-ce"><span class="x3-k">Another reply, from ${esc(c.from || 'our suite')} · Emma asked: “${esc(c.question)}”</span>
    <p>${x3marks(ls[0])}${c.more ? ` <span class="more">… ${c.more} more orders, every value found …</span>` : ''}</p>${ls.slice(1).map((l) => `<p>${x3marks(l)}</p>`).join('')}
    <p class="v"><span class="x3-no">fail</span> · the check’s words: “${esc(c.why)}”</p></div>`;
  return { step() {} };
};

/* is the judge right: six labelled replies, then the four boxes fill. k: 0 labels, 1 the judge's verdicts, 2 the boxes, 3 the sentence */
FIGS.fourbox = (el) => {
  const rows = get('m.calib.tiny'), n = get('m.calib.tiny_n');
  if (!Array.isArray(rows) || !n) return need(el, 'Six labelled replies and the judge’s verdict on each');
  const box = (k, t, s, cls) => `<div class="b ${cls}"><span class="t">${t}</span><b data-k="2">${n[k]}</b><span class="ids" data-k="2">${rows.filter((r) => r.box === k).map((r) => `<i>${r.n}</i>`).join('')}</span><span class="s">${s}</span></div>`;
  const wrong = n.wf + n.wp, right = n.rp + n.rf;
  el.innerHTML = `<div class="x3-fb"><div class="l"><table><tr><th></th><th>Emma asked</th><th>A person says</th><th data-k="1">The judge says</th></tr>
    ${rows.map((r) => `<tr><td><i>${r.n}</i></td><td>${esc(r.q)}<small>${esc(r.change)}</small></td><td><span class="${r.label ? 'x3-ok' : 'x3-no'}">${r.label ? 'right' : 'wrong'}</span></td><td data-k="1"><span class="${r.judge ? 'x3-ok' : 'x3-no'}">${r.judge ? 'pass' : 'fail'}</span></td></tr>`).join('')}</table></div>
    <div class="r"><div class="g"><span></span><span class="h">the judge passed it</span><span class="h">the judge failed it</span>
      <span class="h v">a person: right</span>${box('rp', 'right, and passed', 'agree', 'ok')}${box('rf', 'right, but failed', 'a false alarm', 'no')}
      <span class="h v">a person: wrong</span>${box('wp', 'wrong, but passed', 'missed', 'no')}${box('wf', 'wrong, and failed', 'caught', 'ok')}</div>
      <p class="say" data-k="3">This judge caught <b>${n.wf} of ${wrong}</b> wrong replies, and raised <b>${n.rf} false alarm${n.rf === 1 ? '' : 's'}</b> in ${right} right ones.</p></div></div>`;
  return { step(k) { at(el, k); } };
};

/* observability and evals as one loop. k = the number of boxes shown beyond the first */
FIGS.loopflow = (el) => {
  const W = 1400, H = 520, w = 256, h = 190, gap = (W - 5 * w) / 4, X = (i) => i * (w + gap), Y0 = 0, Y1 = 316;
  const [id, o] = svgOpen(W, H);
  const node = (k, n, x, y, cls, title, sub, tools) => G(k, R(x, y, w, h, cls, 20) + `<circle cx="${x + 26}" cy="${y + 28}" r="15" class="x3-nb"/>` + T(x + 26, y + 34, n, 'x3-nn', 'middle')
    + TL(x + 52, y + 35, title, 't1', 27) + (sub ? T(x + 20, y + 35 + title.length * 27 + 4, sub, 't2') : '') + TL(x + 20, y + h - 16 - (tools.length - 1) * 22, tools, 'x3-tl', 22));
  const right = (k, i, y, cls = '') => G(k, A(`M${X(i) + w + 4},${y + h / 2} L${X(i + 1) - 6},${y + h / 2}`, id, cls));
  const left = (k, i, y, cls = '') => G(k, A(`M${X(i) - 4},${y + h / 2} L${X(i - 1) + w + 6},${y + h / 2}`, id, cls));
  el.innerHTML = o
    + node(0, 1, X(0), Y0, '', ['The agent', 'runs'], '', ['Ask Northbridge'])
    + right(1, 0, Y0) + node(1, 2, X(1), Y0, 'a', ['Every turn', 'is a trace'], '', ['OpenTelemetry sends it to', 'LangSmith, Langfuse,', 'Sentry'])
    + right(2, 1, Y0, 'a') + node(2, 3, X(2), Y0, 'a', ['People read', 'the traces'], 'error analysis', ['LangSmith · Langfuse'])
    + right(3, 2, Y0) + node(3, 4, X(3), Y0, 'g', ['What they find', 'becomes scores'], 'code · a judge · a person', ['our code · DeepEval · Ragas'])
    + right(4, 3, Y0, 'g') + node(4, 5, X(4), Y0, 'g', ['The failures', 'become test cases'], '', ['a dataset: our 20 tasks'])
    + G(5, A(`M${X(4) + w / 2},${Y0 + h + 4} L${X(4) + w / 2},${Y1 - 6}`, id, 'g')) + node(5, 6, X(4), Y1, 'g', ['The suite runs', 'on every change'], 'the gate blocks a bad one', ['pytest · DeepEval', 'the CI gate'])
    + left(6, 4, Y1, 'g') + node(6, 7, X(3), Y1, 'y', ['Ship'], 'the change reaches real users', [''])
    + left(7, 3, Y1) + node(7, 8, X(2), Y1, 'a', ['The same scorers', 'on live traces'], 'online evals', ['scores: LangSmith,', 'Langfuse · alerts: Sentry'])
    + left(8, 2, Y1, 'a') + node(8, 9, X(1), Y1, 'a', ['The flagged ones', 'go back to be read'], '', ['review queues'])
    + G(8, A(`M${X(1) + w / 2},${Y1 - 4} L${X(1) + w / 2},${(Y0 + h + Y1) / 2} L${X(2) + 60},${(Y0 + h + Y1) / 2} L${X(2) + 60},${Y0 + h + 6}`, id, 'a'))
    + G(8, T(X(1) + w / 2 + 14, (Y0 + h + Y1) / 2 - 10, 'and round again', 't3'))
    + `<g>${R(X(0), Y1 + 10, w, h - 20, 'c', 20)}${T(X(0) + 20, Y1 + 44, 'Blue: observability', 'x3-lg a')}${T(X(0) + 20, Y1 + 74, 'what happened', 't2')}${T(X(0) + 20, Y1 + 112, 'Green: evals', 'x3-lg g')}${T(X(0) + 20, Y1 + 142, 'was it right', 't2')}</g>`
    + '</svg>';
  return { step(k) { at(el, k); } };
};

FIGS.blank = (el) => ({ step() {} });
})();
