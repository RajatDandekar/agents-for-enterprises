/* Live figures for Lecture 4 · The Hands (v4, Northbridge), part 1: opener and sections 1–5.
   Loaded BEFORE plates.js. Every number and every line of code comes from window.L4 (figdata.js, written by
   gen_figdata.py from experiments/logs and the tool folders). Nothing is typed in here by hand.
   Each FIGS.<name>(el) returns { step(k, instant) }, k = the number of .step elements shown on the slide. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const L = () => window.L4 || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const stop = (e) => e.stopPropagation();
const get = (path) => { let v = L(); for (const k of path.split('.')) v = v == null ? v : v[k]; return v; };
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k));
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(L4 data)</span><div>${what}</div><div class="todo-s">Fills in from figdata.js (gen_figdata.py).</div></div>`; return { step() {} }; };
const pj = (o, n = 2) => JSON.stringify(o, null, n);
const cj = (o) => JSON.stringify(o);
const short = (s, n) => { s = typeof s === 'string' ? s : cj(s); return s.length > n ? s.slice(0, n - 1) + '…' : s; };
const args = (a) => Object.entries(a || {}).map(([k, v]) => `${k}: ${typeof v === 'string' ? v : cj(v)}`).join(', ');

/* A small highlighter for Python and JSON source lines (comments, strings, keywords, numbers). */
const KW = /\b(def|return|for|in|if|else|elif|try|except|import|from|raise|not|and|or|None|True|False|is|lambda|with|as|class|continue|while|true|false|null)\b/;
function hl(line) {
  const re = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d[\d_.]*\b)|([A-Za-z_]\w*)/g;
  let out = '', last = 0, m;
  while ((m = re.exec(line))) {
    out += esc(line.slice(last, m.index));
    if (m[1]) out += `<span class="cmt">${esc(m[1])}</span>`;
    else if (m[2]) out += `<span class="st">${esc(m[2])}</span>`;
    else if (m[3]) out += `<span class="nu">${esc(m[3])}</span>`;
    else out += KW.test(m[4]) && m[4].match(KW)[0] === m[4] ? `<span class="kw">${m[4]}</span>` : esc(m[4]);
    last = re.lastIndex;
  }
  return out + esc(line.slice(last));
}
const ranges = (spec) => { const s = new Set(); (spec || '').split(',').filter(Boolean).forEach((r) => { const [a, b] = r.split('-').map(Number); for (let i = a; i <= (b || a); i++) s.add(i); }); return s; };
window.L4hl = hl;

/* ======================= generic: a real source file as a notebook-style card, highlighted per click =======================
   data-src="anatomy.tool_py"  data-title="…"  data-hl="8;10;12-14"  (one range list per click; click 0 = data-hl0)
   data-from / data-to: show only these lines (1-based) of the file. data-rows: at most this many lines at once; the
   window follows the highlight, so a long file never overflows its box. */
FIGS.code = (el) => {
  let src = get(el.dataset.src); if (src == null) return need(el, `The file ${esc(el.dataset.src)}.`);
  if (typeof src !== 'string') src = pj(src);
  const all = src.replace(/\n$/, '').split('\n');
  const from = +(el.dataset.from || 1), to = +(el.dataset.to || all.length);
  const lines = all.slice(from - 1, to);
  const steps = (el.dataset.hl || '').split(';');
  const rows = +(el.dataset.rows || 999);
  el.classList.add('nbcell');
  const draw = (k) => {
    const on = ranges(k === 0 ? el.dataset.hl0 || '' : steps[Math.min(k, steps.length) - 1]);
    let start = 0;
    if (lines.length > rows) {
      const hits = [...on].map((n) => n - from).filter((i) => i >= 0 && i < lines.length);
      const mid = hits.length ? Math.round((Math.min(...hits) + Math.max(...hits)) / 2) : 0;
      start = Math.max(0, Math.min(lines.length - rows, mid - Math.floor(rows / 2)));
      if (!hits.length) start = 0;
    }
    const vis = lines.slice(start, start + rows);
    el.innerHTML = `<span class="hd">${esc(el.dataset.title || '')}${lines.length > rows ? ` · lines ${from + start}–${from + start + vis.length - 1} of ${all.length}` : ''}</span>` +
      vis.map((t, i) => { const n = from + start + i; return `<span class="ln${on.has(n) ? ' hl' : ''}"><i class="lno">${n}</i>${hl(t.replace(/(\S)\s{4,}#/, '$1   #')) || ' '}</span>`; }).join('');
  };
  return { step(k) { draw(k); } };
};

/* ======================= opener: Emma's question, with hands (the recorded single run of our harness) ======================= */
FIGS.chattool = (el) => {
  const R = get('ours.single'); if (!R) return need(el, 'The recorded single run.');
  const t = R.turns[0], c = t.cards[0], res = JSON.parse(c.result.replace(/…$/, '') || '{}');
  const wh = (res.warehouses || []).map((w) => `${esc(w.name)} <b>${fmt(w.on_hand)}</b>`).join(' · ');
  el.innerHTML = `<div class="cr" style="bottom:0">
    <div class="cr-top"><span class="cr-av">AN</span><div><b>Ask Northbridge</b><span>as Emma Clarke · purchase executive · with tools</span></div></div>
    <div class="cr-body" style="justify-content:flex-start;gap:12px;padding-top:18px">
      <div class="msg u" data-k="1">${esc(t.user)}</div>
      <div class="toolcard" data-k="2"><span class="tc-k">Tool call</span><code>${esc(c.tool)}</code> <span class="tc-a">${esc(args(c.args))}</span>
        <div class="tc-r">${wh}<span class="tc-ms">${c.ms} ms · ran in Emma’s own Ledgerline session</span></div></div>
      <div class="msg ag" data-k="3">${esc(t.reply).replace(/\n+/g, '<br>')}</div>
    </div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 1 · the two model calls of the single run ======================= */
FIGS.rt = (el) => {
  const R = get('ours.single'), A = get('anatomy'); if (!R || !A) return need(el, 'The single run.');
  const [s0, s1] = R.steps, B = R.blocks, tc = s0.tool_calls[0];
  el.innerHTML = `<div class="rt">
   <div class="rt-c" data-k="0"><span class="rt-h">Model call 1 · reads ${fmt(s0.prompt_tokens)} tokens</span>
     <div class="rt-in">${B.slice(0, 3).map((b) => `<span class="kb ${b.kind}">${esc(b.label.replace(' (only what the tool returned)', ''))} <b>${fmt(b.tokens)}</b></span>`).join('')}</div>
     <span class="rt-o">writes, as text (content: ${s0.text === null ? 'null' : '…'}):</span><pre class="rt-j">${esc(pj({ name: tc.name, arguments: tc.arguments }))}</pre></div>
   <div class="rt-c mid" data-k="1"><span class="rt-h">Our code</span>
     <p>Checks it against tool.json: <code>${esc(cj(A.door.arguments_clean))}</code> is clean.</p>
     <p>Runs <code>check_stock</code> in Emma’s session: ${A.legacy_calls.length} Ledgerline calls (${A.legacy_calls.map((c) => c.service).join(', ')}).</p>
     <p>Hands back ${fmt(A.sizes.tool_result_bytes)} bytes of JSON.</p></div>
   <div class="rt-c" data-k="2"><span class="rt-h">Model call 2 · reads ${fmt(s1.prompt_tokens)} tokens</span>
     <div class="rt-in"><span class="kb sum">all of call 1 <b>${fmt(s0.prompt_tokens)}</b></span>${B.slice(3).map((b) => `<span class="kb ${b.kind}">${b.kind === 'call' ? 'its tool call' : 'the tool result'} <b>${fmt(b.tokens)}</b></span>`).join('')}</div>
     <span class="rt-o">writes the answer (${fmt(R.final.tokens)} tokens):</span><p class="rt-a">${esc(R.final.text)}</p></div>
  </div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 2 · JSON Schema, built up field by field on check_stock's input ======================= */
FIGS.schemabuild = (el) => {
  const A = get('anatomy'); if (!A) return need(el, 'check_stock’s tool.json.');
  const S = JSON.parse(A.tool_json).input_schema, p = S.properties.item_code;
  const stages = [
    ['{ }', 'A schema is itself JSON. An empty one accepts anything.'],
    [pj({ type: S.type }), '<b>type</b>: the arguments must be one JSON object.'],
    [pj({ type: S.type, properties: { item_code: { type: p.type } } }), '<b>properties</b>: the object may have <code>item_code</code>, and it must be a <b>string</b>.'],
    [pj({ type: S.type, properties: { item_code: { type: p.type, description: p.description } } }), '<b>description</b>: what the model reads to fill it in. It is a prompt.'],
    [pj(S), '<b>required</b>: without <code>item_code</code> the call is refused. This is check_stock’s real input schema.'],
  ];
  const ok = A.door.arguments_in, bad = A.error_wrong_type;
  el.innerHTML = `<div class="sb2"><pre class="sb-j"></pre><div class="sb-side"><div class="sb-note"></div>
    <div class="sb-test" data-k="5"><span class="rt-h">At the door, two real requests</span>
      <div class="sb-t okk"><code>${esc(cj(ok))}</code><span>clean: runs</span></div>
      <div class="sb-t no"><code>${esc(cj(bad.model_request.arguments))}</code><span>${esc(bad.tool_result.error)}<br><small>next_step: ${esc(bad.tool_result.next_step)} · Ledgerline calls: ${bad.ledgerline_calls}</small></span></div></div></div></div>`;
  return { step(k) {
    const st = stages[Math.min(k, 4)];
    el.querySelector('.sb-j').innerHTML = esc(st[0]).replace(/&quot;|"/g, '"');
    el.querySelector('.sb-note').innerHTML = `<span class="sb-n">${Math.min(k, 4) + 1} / 5</span>${st[1]}`;
    reveal(el, k);
  } };
};

/* ======================= 2 · the JSON Schema words, each on a real tool of ours ======================= */
FIGS.vocab = (el) => {
  const T = get('toolbox'); if (!T) return need(el, 'The tool folders.');
  const by = Object.fromEntries(T.map((t) => [t.name, t]));
  const B = get('build.schema')['tool.json'];
  const pr = by.create_purchase_request, sc = by.supplier_certificates;
  const rows = [
    ['type', 'string, integer, number, boolean, object, array, null', `check_stock · item_code: <code>${esc(cj(by.check_stock.input_schema.properties.item_code.type))}</code>; create_purchase_request · quantity: <code>${esc(pr.input_schema.properties.quantity.type)}</code>`],
    ['required', 'the fields that must be there', `supplier_certificates: <code>${esc(cj(sc.required))}</code>; the other four are optional`],
    ['enum', 'one of a fixed list', `supplier_certificates output · un38_3: <code>${esc(cj(B.output_schema.properties.un38_3.enum))}</code>`],
    ['format', 'a string with a shape (date, e-mail …)', `create_purchase_request · need_by: our tool.json says <code>${esc(cj(pr.argument_formats))}</code>, checked at the door`],
    ['description', 'words for the reader, the model', `find_item · query: “${esc(by.find_item.input_schema.properties.query.description)}”`],
    ['examples', 'a valid call, for the reader', `check_stock: <code>${esc(cj(by.check_stock.example))}</code>`],
  ];
  el.innerHTML = `<table class="t vt"><tr><th>Word</th><th>Says</th><th>In our toolbox</th></tr>${rows.map((r, i) => `<tr data-k="${i}"><td><code>${r[0]}</code></td><td>${r[1]}</td><td>${r[2]}</td></tr>`).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 2 · the output schema next to a real result ======================= */
FIGS.outschema = (el) => {
  const A = get('anatomy'); if (!A) return need(el, 'check_stock’s output.');
  const O = JSON.parse(A.tool_json).output_schema.properties, R = A.tool_result;
  const keys = Object.keys(R);
  el.innerHTML = `<table class="t os"><tr><th>Field in the real result</th><th>Value</th><th>In the output schema</th></tr>${keys.map((k) => {
    const s = O[k], v = R[k];
    return `<tr class="${s ? '' : 'extra'}"><td><code>${k}</code></td><td class="mono">${esc(short(v, 46))}</td><td>${s ? `<span class="os-y" data-k="1">${esc(s.type)}${s.description ? ` · ${esc(s.description)}` : ''}</span>` : '<span class="os-n" data-k="2">not listed</span>'}</td></tr>`;
  }).join('')}</table>`;
  return { step(k) { reveal(el, k); el.querySelectorAll('tr.extra').forEach((r) => r.classList.toggle('lit2', k >= 2)); } };
};

/* ======================= 2 · refused at the door (real refusals, 0 Ledgerline calls) ======================= */
FIGS.refusals = (el) => {
  const C = get('build.errors.cases'), W = get('anatomy.error_wrong_type'); if (!C || !W) return need(el, 'The error cases.');
  const door = C.filter((c) => c.ledgerline_calls === 0);
  const rows = [{ tool: 'check_stock', arguments: W.model_request.arguments, result: W.tool_result, n: W.ledgerline_calls },
    ...door.slice(0, 3).map((c) => ({ tool: 'supplier_certificates', arguments: c.arguments, result: c.result, n: c.ledgerline_calls }))];
  el.innerHTML = `<div class="rf">${rows.map((r, i) => `<div class="rf-r" data-k="${Math.min(i, 3)}"><code class="rf-a">${esc(r.tool)} ${esc(cj(r.arguments))}</code><span class="rf-e">${esc(r.result.error)}</span><span class="rf-n">${esc(r.result.next_step)}</span><span class="rf-c">${r.n} Ledgerline calls</span></div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 3 · the toolbox: 16 folders ======================= */
FIGS.toolgrid = (el) => {
  const T = get('toolbox'); if (!T) return need(el, 'The tool folders.');
  el.innerHTML = `<div class="tg">${T.map((t) => `<div class="tg-c${t.writes ? ' w' : ''}${t.name === 'check_stock' ? ' on' : ''}${t.name === 'supplier_certificates' ? ' nw' : ''}">
    <b>${esc(t.name)}</b><span>${esc(t.category)} · v${esc(t.version)} · ${t.services.length} service${t.services.length === 1 ? '' : 's'}</span></div>`).join('')}</div>
    <div class="tg-l"><span><i class="r"></i>reads (${T.filter((t) => !t.writes).length})</span><span><i class="w"></i>writes, preview first (${T.filter((t) => t.writes).length})</span><span><i class="n"></i>built today</span></div>`;
  return { step() {} };
};

/* ======================= 3 · the services inside check_stock ======================= */
FIGS.services = (el) => {
  const S = get('anatomy.services'); if (!S) return need(el, 'The services.');
  el.innerHTML = `<div class="sv">${S.map((s, i) => `<div class="sv-c" data-k="${i}"><div class="sv-h"><code>${esc(s.name)}</code><span>${esc(s.legacy_title)}</span></div>
    <div class="sv-m">${esc(s.kind)}${s.screen ? ` · screen ${esc(s.screen)}` : ''} · fields: ${s.fields.length ? s.fields.map((f) => `<code>${esc(f.name)}</code>${f.required ? '*' : ''}`).join(' ') : 'none'}</div>
    <pre class="sv-s">${s.source.trim().split('\n').map(hl).join('\n')}</pre></div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 3 · each line of tool.py, linked to the service it calls ======================= */
FIGS.linemap = (el) => {
  const A = get('anatomy'); if (!A) return need(el, 'check_stock’s anatomy.');
  const lines = A.tool_py.replace(/\n$/, '').split('\n').slice(4);   // from the import line down
  const base = 5;
  const at = (svc) => base + lines.findIndex((l) => l.includes(`"${svc}"`));
  const calls = A.legacy_calls.map((c) => ({ ...c, line: at(c.service) }));
  el.innerHTML = `<div class="lm"><div class="nbcell lm-code">${lines.map((t, i) => `<span class="ln" data-n="${base + i}"><i class="lno">${base + i}</i>${hl(t) || ' '}</span>`).join('')}</div>
    <svg class="lm-svg"></svg><div class="lm-side"></div></div>`;
  const side = el.querySelector('.lm-side'), svg = el.querySelector('.lm-svg'), code = el.querySelector('.lm-code');
  const res = A.tool_result;
  return { step(k) {
    code.querySelectorAll('.ln').forEach((x) => x.classList.remove('hl'));
    svg.innerHTML = '';
    if (k === 0) { side.innerHTML = `<div class="lm-0">Three lines of <code>tool.py</code> call Ledgerline. Click to follow each call, in the order it ran for <code>BAT-500</code>.</div>`; return; }
    if (k > calls.length) {
      side.innerHTML = `<div class="lm-card done"><span class="rt-h">What tool.py hands back · ${fmt(A.sizes.tool_result_bytes)} bytes</span><pre>${esc(pj(res)).slice(0, 820)}</pre></div>`;
      code.querySelectorAll('.ln').forEach((x) => x.classList.toggle('hl', /return \{"ok"|"warehouses"|"cover_days"|"below_reorder"/.test(x.textContent)));
      return;
    }
    const c = calls[k - 1], ln = code.querySelector(`.ln[data-n="${c.line}"]`);
    ln.classList.add('hl');
    side.innerHTML = `<div class="lm-card"><span class="rt-h">Ledgerline call ${c.seq} of ${calls.length} · line ${c.line}</span>
      <div class="lm-svc"><code>${esc(c.service)}</code> ${esc((A.services.find((s) => s.name === c.service) || {}).legacy_title || '')}</div>
      <div class="lm-k">request</div><pre>${esc(cj(c.request))}</pre>
      <div class="lm-k">reply, in the legacy envelope</div><pre>${esc(pj({ rc: c.reply.rc, err_cd: c.reply.err_cd, msg: c.reply.msg, data: c.reply.data })).slice(0, 640)}</pre></div>`;
    const y = ln.offsetTop + ln.offsetHeight / 2 + code.offsetTop, x0 = code.offsetLeft + code.offsetWidth, x1 = side.offsetLeft;
    const card = side.firstElementChild, y1 = side.offsetTop + card.offsetTop + 22;
    svg.setAttribute('width', el.clientWidth); svg.setAttribute('height', el.clientHeight);
    svg.innerHTML = `<path d="M${x0} ${y} C ${x0 + 40} ${y}, ${x1 - 40} ${y1}, ${x1} ${y1}" fill="none" stroke="#c4511f" stroke-width="2.5"/><circle cx="${x0}" cy="${y}" r="5" fill="#c4511f"/>`;
  } };
};

/* ======================= 3 · four legacy envelopes become one clean result ======================= */
FIGS.envelope = (el) => {
  const A = get('anatomy'); if (!A) return need(el, 'check_stock’s anatomy.');
  const R = A.tool_result, C = A.legacy_calls;
  const st = C.filter((c) => c.service === 'stk_query').map((c) => c.reply.data);
  const map = [
    ['itm_cd', 'item_code', R.item_code], ['descr', 'description', R.description], ['uom_cd', 'unit', R.unit],
    ['on_hand − allocated', 'free (per warehouse)', R.warehouses.map((w) => fmt(w.free)).join(' + ')],
    ['(no such field)', 'free_total', fmt(R.free_total)],
    [`cover_days: ${st.map((d) => d.cover_days).join(' and ')} (per warehouse)`, 'cover_days (all warehouses)', `${fmt(R.free_total)} ÷ ${fmt(st[0].avg_daily_issue)} a day = ${R.cover_days}`],
    ['rc, err_cd, msg', '(dropped: ok is enough)', 'ok: true'],
  ];
  el.innerHTML = `<div class="ev"><div class="ev-l" data-k="0"><span class="rt-h">${C.length} legacy replies · ${fmt(A.sizes.legacy_replies_bytes)} bytes</span>${C.map((c) => `<pre>${esc(c.service)} → ${esc(short({ rc: c.reply.rc, err_cd: c.reply.err_cd, msg: c.reply.msg, data: c.reply.data }, 150))}</pre>`).join('')}</div>
    <div class="ev-m" data-k="1"><table class="t"><tr><th>Ledgerline says</th><th>The tool says</th><th>For BAT-500</th></tr>${map.map((m) => `<tr><td><code>${esc(m[0])}</code></td><td><code>${esc(m[1])}</code></td><td>${esc(m[2])}</td></tr>`).join('')}</table></div>
    <div class="ev-r" data-k="2"><span class="rt-h">One clean result · ${fmt(A.sizes.tool_result_bytes)} bytes</span><pre>${esc(pj(R, 1))}</pre></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 3 · the error path: a wrong code ======================= */
FIGS.errpath = (el) => {
  const E = get('anatomy.error_path'), M = get('mcp.lines'); if (!E) return need(el, 'The error path.');
  const lc = E.legacy_calls[0];
  const isErr = (M || []).find((l) => l.dir === '<' && l.msg.result && l.msg.result.isError && l.msg.result.structuredContent);
  el.innerHTML = `<div class="ep">
    <div class="ep-c" data-k="0"><span class="rt-h">1 · The model asks</span><pre>${esc(cj(E.model_request))}</pre></div>
    <div class="ep-c leg" data-k="1"><span class="rt-h">2 · Ledgerline answers ${esc(lc.service)}</span><pre>${esc(pj(lc.reply))}</pre></div>
    <div class="ep-c" data-k="2"><span class="rt-h">3 · The tool returns the error contract</span><pre>${esc(pj(E.tool_result))}</pre></div>
    <div class="ep-c" data-k="3"><span class="rt-h">4 · Over MCP it is flagged</span><pre>${isErr ? esc(`"isError": ${isErr.msg.result.isError}`) : ''}</pre><p class="small">${esc(E.how)}</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 4 · the job, and the overlap with find_supplier ======================= */
FIGS.bjob = (el) => {
  const J = get('build.job'); if (!J) return need(el, 'The new tool’s job.');
  const o = J.overlap_with_existing;
  el.innerHTML = `<div class="bj"><div class="bj-q" data-k="0"><span class="rt-h">The questions · ${esc(J.who_asks)}</span>${J.questions.map((q) => `<div class="msg u">${esc(q)}</div>`).join('')}</div>
    <div class="bj-o" data-k="1"><span class="rt-h">What ${esc(o.tool)} already gives: ${esc(o.gives)}</span>${o.example.map((x) => `<pre>${esc(cj({ supplier_code: x.supplier_code, name: x.name, cell_safety_certificate: x.cell_safety_certificate }))}</pre>`).join('')}</div>
    <div class="bj-m" data-k="2"><span class="rt-h">What is missing</span><ul>${o.missing.map((m) => `<li>${esc(m)}</li>`).join('')}</ul><p><b>Verdict:</b> ${esc(o.verdict)}. Read-only: ${J.read_only ? 'yes' : 'no'}.</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 4 · finding the services ======================= */
FIGS.bservices = (el) => {
  const S = get('build.services'); if (!S) return need(el, 'The service search.');
  const chosen = Object.fromEntries(S.chosen.map((c) => [c.name, c]));
  el.innerHTML = `<div class="bsv">${S.candidates.map((c) => `<div class="bsv-c${chosen[c.name] ? ' ch' : ''}${S.not_chosen[c.name] ? ' nc' : ''}">
      <div class="bsv-h"><code>${esc(c.name)}</code><span class="bsv-k ${c.kind}">${esc(c.kind)}</span></div><div class="bsv-t">${esc(c.legacy_title)}</div>
      <div class="bsv-f">${c.fields.map(esc).join(' · ')}</div>
      ${chosen[c.name] ? `<div class="bsv-w" data-k="1">use it: ${esc(chosen[c.name].why)}</div>` : ''}${S.not_chosen[c.name] ? `<div class="bsv-x" data-k="2">not now: ${esc(S.not_chosen[c.name])}</div>` : ''}</div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); el.querySelectorAll('.bsv-c').forEach((c) => c.classList.toggle('dim', k >= 1 && !c.classList.contains('ch') && !(k >= 2 && c.classList.contains('nc')))); } };
};

/* ======================= 4 · the schema of the new tool (input, then output) ======================= */
FIGS.bschema = (el) => {
  const S = get('build.schema'); if (!S) return need(el, 'The new tool.json.');
  const j = S['tool.json'], I = j.input_schema, O = j.output_schema;
  const row = (k, v, req) => `<div class="bs-r"><code>${esc(k)}</code><span class="bs-t">${esc(Array.isArray(v.type) ? v.type.join(' | ') : v.type)}${v.enum ? ` · ${esc(v.enum.join(' / '))}` : ''}</span>${req ? '<span class="bs-q">required</span>' : '<span></span>'}<span class="bs-d">${esc(v.description || '')}</span></div>`;
  el.innerHTML = `<div class="bs2"><div class="bs-col" data-k="0"><span class="rt-h">input_schema: what the model must send</span>${Object.entries(I.properties).map(([k, v]) => row(k, v, I.required.includes(k))).join('')}
      <div class="bs-dec" data-k="1">${S.decisions.slice(0, 3).map((d) => `<p>${esc(d)}</p>`).join('')}</div></div>
    <div class="bs-col" data-k="2"><span class="rt-h">output_schema: what it gets back</span>${Object.entries(O.properties).map(([k, v]) => row(k, v, (O.required || []).includes(k))).join('')}
      <div class="bs-dec" data-k="3"><p><b>annotations</b> <code>${esc(cj(j.annotations))}</code></p><p><b>policy</b> ${esc(j.policy.on_busy_or_lost_reply)}; reply timeout ${j.policy.ledgerline_reply_timeout_s} s.</p></div></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 4 · the error contract, case by case ======================= */
FIGS.berrors = (el) => {
  const E = get('build.errors'); if (!E) return need(el, 'The error cases.');
  el.innerHTML = `<table class="t be"><colgroup><col style="width:230px"><col style="width:300px"><col style="width:110px"><col></colgroup><tr><th>Case</th><th>Arguments</th><th class="n">Ledgerline calls</th><th>What the model gets</th></tr>${E.cases.map((c, i) => `<tr data-k="${i < 2 ? 0 : i < 7 ? 1 : 2}"><td>${esc(c.case)}</td><td><code>${esc(short(c.arguments, 54))}</code></td><td class="n">${c.ledgerline_calls}</td><td>${c.result.ok ? `<span class="ok">ok</span> ${esc(short(c.result.next_step || '', 120))}` : `<span class="no">ok=false</span> ${esc(c.result.error)} <small>→ ${esc(c.result.next_step)}</small>`}</td></tr>`).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 4 · the tests ======================= */
FIGS.btests = (el) => {
  const T = get('build.tests'); if (!T) return need(el, 'The tests.');
  el.innerHTML = `<div class="bt2"><div class="bt-n"><b>${T.assertions}</b><span>assertions for supplier_certificates</span></div>
    <div class="bt-n ${T.passed ? 'g' : ''}"><b>${T.passed ? 'pass' : 'fail'}</b><span>and the whole file: ${T.whole_file_passed ? 'pass' : 'fail'}</span></div>
    <div class="bt-m"><span class="rt-h">Markers printed by <code>${esc(T.file)}</code></span>${T.markers.map((m) => `<span class="chip p">${esc(m)}</span>`).join(' ')}</div></div>`;
  return { step() {} };
};

/* ======================= 4 · two real answers: Voltway and Nordic ======================= */
FIGS.bresults = (el) => {
  const B = get('build'); if (!B) return need(el, 'The results.');
  const v = B.mcp_call.structuredContent, n = B.errors.cases.find((c) => c.arguments.supplier_code === 'NC-GDA-0063').result;
  const card = (r, cls) => `<div class="br-c ${cls}"><div class="br-h"><b>${esc(r.supplier_name)}</b><code>${esc(r.supplier_code)}</code></div>
    ${r.certificates.map((c) => `<div class="br-x"><code>${esc(c.cert_type)}</code> ${esc(c.doc_ref)} · valid to ${esc(c.valid_to)} · <b class="${c.valid ? 'g' : 'b'}">${c.days_left} days</b></div>`).join('')}
    <div class="br-v">un38_3: <b>${esc(r.un38_3)}</b> · ${esc(r.item.item_code)} needs UN 38.3: ${r.item.needs_un38_3} · supplier qualifies: <b class="${r.item.supplier_qualifies ? 'g' : 'b'}">${r.item.supplier_qualifies}</b></div>
    ${r.next_step ? `<div class="br-n">next_step: ${esc(r.next_step)}</div>` : ''}</div>`;
  el.innerHTML = `<div class="br">${card(v, 'af')}${card(n, 'bf')}</div><p class="cap" style="position:static;margin-top:12px">As of Ledgerline’s own date, ${esc(v.as_of)}. Voltway’s came back over MCP (structuredContent); Nordic’s from the toolbox test run.</p>`;
  return { step() {} };
};

/* ======================= 5 · JSON-RPC from first principles, on the real initialize ======================= */
FIGS.rpc = (el) => {
  const M = get('mcp.lines'); if (!M) return need(el, 'The raw wire.');
  const req = M[0].msg, res = M[1].msg, note = M[2].msg;
  const lab = (o, notes) => '{\n' + Object.entries(o).map(([k, v]) => `  <span class="rk${notes[k] ? ' on' : ''}" data-k="${notes[k] || 0}">"${k}": ${esc(cj(v)).slice(0, 150)}</span>`).join(',\n') + '\n}';
  el.innerHTML = `<div class="rpc"><div class="rpc-c"><span class="rt-h">→ request, from the client (${M[0].t} s)</span><pre>${lab(req, { jsonrpc: 1, id: 2, method: 3, params: 4 })}</pre></div>
    <div class="rpc-c" data-k="5"><span class="rt-h">← response, the same id (${M[1].t} s)</span><pre>${lab(res, {})}</pre></div>
    <div class="rpc-c" data-k="6"><span class="rt-h">→ notification: no id, so no reply</span><pre>${esc(cj(note))}</pre></div></div>`;
  return { step(k) { reveal(el, k); el.querySelectorAll('.rk').forEach((x) => x.classList.toggle('lit', +x.dataset.k === k)); } };
};

/* ======================= 5–6 · the raw wire of one session, step by step ======================= */
FIGS.wire = (el) => {
  const M = get('mcp.lines'); if (!M) return need(el, 'The raw wire.');
  const groups = [[0, 1], [2, 3, 4], [5, 6], [7, 8], [9, 10], [11, 12]];
  const what = (m) => m.method ? m.method + (m.params && m.params.name ? ` · ${m.params.name} ${cj(m.params.arguments)}` : '') :
    m.result && m.result.tools ? `result · ${m.result.tools.length} tool: ${m.result.tools.map((t) => t.name).join(', ')}` :
    m.result && m.result.content ? `result · isError ${!!m.result.isError}` : m.result && m.result.protocolVersion ? `result · protocolVersion ${m.result.protocolVersion}` : 'result';
  el.innerHTML = `<div class="wr"><div class="wr-l">${M.map((l, i) => `<div class="wr-r ${l.dir === '>' ? 'out' : 'in'}" data-i="${i}"><span class="wr-t">${l.t.toFixed(4)} s</span><span class="wr-d">${l.dir === '>' ? '→' : '←'}</span><span class="wr-w">${esc(short(what(l.msg), 92))}</span></div>`).join('')}</div>
    <pre class="wr-j"></pre></div>`;
  const rows = el.querySelectorAll('.wr-r'), box = el.querySelector('.wr-j');
  return { step(k) {
    const g = groups[Math.max(0, Math.min(k, groups.length) - 1)], showUpTo = k === 0 ? -1 : g[g.length - 1];
    rows.forEach((r) => { const i = +r.dataset.i; r.classList.toggle('fade-hide', i > showUpTo); r.classList.toggle('cur', k > 0 && g.includes(i)); });
    box.innerHTML = k === 0 ? 'Click to send the first message.' : g.map((i) => `<span class="wr-h">${M[i].dir === '>' ? '→ client sends' : '← server sends'}</span>\n${esc(short(pj(M[i].msg), 900))}`).join('\n\n');
  } };
};

/* ======================= 5 · the MCP tool definition and the result, on check_stock ======================= */
FIGS.mcpdef = (el) => {
  const D = get('mcp.diff_check_stock.after'), M = get('mcp.lines'); if (!D || !M) return need(el, 'check_stock over MCP.');
  const ok = M.find((l) => l.dir === '<' && l.msg.id === 2).msg.result, bad = M.find((l) => l.dir === '<' && l.msg.id === 3).msg.result;
  const def = { name: D.name, title: D.title, description: D.description, inputSchema: D.inputSchema, outputSchema: { type: 'object', properties: `{${Object.keys(D.outputSchema.properties).join(', ')}}` }, annotations: D.annotations, _meta: `{${Object.keys(D._meta).filter((k) => k.startsWith('ledgerline')).join(', ')}}` };
  const okS = { content: [{ type: 'text', text: short(ok.content[0].text, 70) }], structuredContent: '{ the same dict }', isError: !!ok.isError };
  const badS = { content: [{ type: 'text', text: short(bad.content[0].text, 70) }], structuredContent: '{ the same dict }', isError: bad.isError };
  el.innerHTML = `<div class="md"><div class="md-c" data-k="0"><span class="rt-h">The definition: one entry of tools/list</span><pre>${esc(pj(def))}</pre></div>
    <div class="md-c" data-k="1"><span class="rt-h">The result of tools/call (BAT-500)</span><pre>${esc(pj(okS))}</pre><span class="rt-h">… and of BAT-5000</span><pre>${esc(pj(badS))}</pre></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 5 · tool.json against the MCP spec, field by field, before and after ======================= */
FIGS.align = (el) => {
  const A = get('mcp.alignment'); if (!A) return need(el, 'The alignment.');
  const tf = A.tool_fields.filter((f) => !f.field.startsWith('annotations.') || /destructive|idempotent|openWorld/.test(f.field));
  const cell = (n, of) => `<span class="al-n${n === of ? ' full' : n === 0 ? ' zero' : ''}">${n} / ${of}</span>`;
  el.innerHTML = `<div class="al"><table class="t"><tr><th>MCP Tool field</th><th>From tool.json</th><th class="n">Before (15 tools)</th><th class="n">After (16)</th></tr>
    ${tf.map((f) => `<tr><td><code>${esc(f.field)}</code>${f.field.startsWith('annotations.') ? '' : ` <small>${esc(f.meaning)}</small>`}</td><td>${f.from_tool_json ? `<code>${esc(f.from_tool_json)}</code>` : (f.field.startsWith('annotations.') ? '<code>annotations</code>' : '<small>not sent (optional)</small>')}</td><td class="n" data-k="1">${cell(f.before_tools_with_it, 15)}</td><td class="n" data-k="2">${cell(f.after_tools_with_it, f.tools)}</td></tr>`).join('')}</table>
    <div><table class="t"><tr><th>CallToolResult field</th><th class="n">Before: ok · error</th><th class="n">After: ok · error</th></tr>
    ${A.result_fields.map((f) => `<tr><td><code>${esc(f.field)}</code><br><small>${esc(f.meaning)}</small></td><td class="n" data-k="1">${f.before_ok_result} · ${f.before_error_result}</td><td class="n" data-k="2">${f.after_ok_result} · ${f.after_error_result}</td></tr>`).join('')}</table>
    <p class="al-p" data-k="2">${esc(A.backwards_compatible)}</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};
/* ======================= 3 · Henrik's documentation: the 04_service_definitions folder of the Lecture 3 dump ======================= */
FIGS.docsglimpse = (el) => {
  const D = get('docs'); if (!D) return need(el, 'The northbridge-docs dump.');
  const F = D.folders, max = Math.max(...Object.values(F).map((f) => f.files));
  const order = ['purchase', 'inventory', 'sales', 'accounts_payable', 'production', 'admin', '_legacy_6x'];
  el.innerHTML = `<div class="dg"><div class="dg-tree"><span class="rt-h">${esc(D.root)}/</span>
      ${order.filter((k) => F[k]).map((k) => `<div class="dg-r${k === 'purchase' ? ' on' : ''}${k.startsWith('_') ? ' old' : ''}"><code>${esc(k)}/</code><span class="dg-b"><i style="width:${(F[k].files / max) * 100}%"></i></span><b>${F[k].files}</b><small>${F[k].yaml ? F[k].yaml + ' yaml' : ''}${F[k].yaml && F[k].xml ? ' · ' : ''}${F[k].xml ? F[k].xml + ' xml' : ''}</small></div>`).join('')}
      <div class="dg-r idx"><code>service_index.csv</code><span></span><b>${fmt(D.definitions)}</b><small>one row per service</small></div>
      <div class="dg-r idx"><code>README.md</code><span></span><b></b><small>the {rc, err_cd, msg, data} envelope</small></div></div>
    <div class="dg-pur" data-k="1"><span class="rt-h">purchase/ · the ${D.purchase.length} purchasing services</span><div class="dg-chips">${D.purchase.map((r) => `<span class="dg-c ${r.kind}${['itm_get', 'whs_list', 'stk_query', 'sup_get', 'sup_cert_get'].includes(r.service) ? ' use' : ''}">${esc(r.service)}</span>`).join('')}</div>
      <p class="small">Outlined: the five that check_stock and supplier_certificates use. Orange: writes.</p></div>
    <div class="dg-old" data-k="2"><span class="rt-h">The old ones, still there</span><pre>${esc(D.gateway_xml_sample.split('\n').slice(0, 4).join('\n'))}</pre>
      <p class="small">${F.accounts_payable.xml + F.sales.xml} WSDL-style XML files for the SOAP gateway (EDI, bank payments, carriers), still served.</p>
      <pre>${esc(D.legacy_sample.split('\n').slice(0, 3).join('\n'))}</pre><p class="small">_legacy_6x/: ${F._legacy_6x.files} Ledgerline 6 definitions, gone from the server since 2015.</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};
})();
