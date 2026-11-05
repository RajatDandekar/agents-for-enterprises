/* Live figures for Lecture 3 · The Memory (v4, Northbridge), part 1: the opener, the dump, the questions, the metrics
   and RAG. Loaded BEFORE plates.js. Every number, passage and line of code comes from window.L3 (figdata.js, written by
   gen_figdata.py from experiments/logs, the dump's golden set and the wiki). Nothing is typed in here by hand.
   Each FIGS.<name>(el) returns { step(k) }, k = the number of .step elements shown on the slide. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const L = () => window.L3 || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const pct = (v, d = 1) => (v == null ? '–' : (100 * v).toFixed(d) + '%');
const stop = (e) => e.stopPropagation();
const get = (path) => { let v = L(); for (const k of path.split('.')) v = v == null ? v : v[k]; return v; };
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k));
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(L3 data)</span><div>${what}</div><div class="todo-s">Fills in from figdata.js (gen_figdata.py).</div></div>`; return { step() {} }; };
const ms = (s) => (s < 1 ? Math.round(s * 1000) + ' ms' : s.toFixed(1) + ' s');
const ktok = (n) => (n >= 1e6 ? (n / 1e6).toFixed(2) + 'M' : n >= 1e3 ? Math.round(n / 1e3) + 'k' : String(n));
const CLS = { structured: '#138a60', 'semi-structured': '#7a5af5', unstructured: '#0b57d0' };
const CLSBG = { structured: '#e3f5ec', 'semi-structured': '#ece6fb', unstructured: '#dbe9ff' };
window.L3u = { esc, fmt, pct, get, reveal, need, ms, ktok, stop, CLS, CLSBG };

/* a small highlighter for Python, JSON and YAML lines (comments, strings, keywords, numbers) */
const KW = /^(def|return|for|in|if|else|elif|try|except|import|from|raise|not|and|or|None|True|False|is|lambda|with|as|class|continue|while|true|false|null|self)$/;
function hl(line) {
  const re = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d[\d_.]*\b)|([A-Za-z_]\w*)/g;
  let out = '', last = 0, m;
  while ((m = re.exec(line))) {
    out += esc(line.slice(last, m.index));
    if (m[1]) out += `<span class="cmt">${esc(m[1])}</span>`;
    else if (m[2]) out += `<span class="st">${esc(m[2])}</span>`;
    else if (m[3]) out += `<span class="nu">${esc(m[3])}</span>`;
    else out += KW.test(m[4]) ? `<span class="kw">${m[4]}</span>` : esc(m[4]);
    last = re.lastIndex;
  }
  return out + esc(line.slice(last));
}
window.L3hl = hl;
const ranges = (spec) => { const s = new Set(); (spec || '').split(',').filter(Boolean).forEach((r) => { const [a, b] = r.split('-').map(Number); for (let i = a; i <= (b || a); i++) s.add(i); }); return s; };

/* ======================= generic: real source as a notebook-style card, highlighted per click =======================
   data-src="code.bm25" data-title="…" data-hl="3-5;8" (one range list per click; click 0 = data-hl0) data-rows=N */
FIGS.code = (el) => {
  let src = get(el.dataset.src); if (src == null) return need(el, `The file ${esc(el.dataset.src)}.`);
  if (typeof src !== 'string') src = JSON.stringify(src, null, 2);
  const all = src.replace(/\n$/, '').split('\n');
  const from = +(el.dataset.from || 1), to = +(el.dataset.to || all.length);
  const lines = all.slice(from - 1, to);
  const steps = (el.dataset.hl || '').split(';');
  el.classList.add('nbcell');
  const fit = Math.max(4, Math.floor(((el.clientHeight || 600) - 64) / 21.75));   // rows that fit the box
  const rows = Math.min(+(el.dataset.rows || 999), fit);
  const cols = Math.max(30, Math.floor(((el.clientWidth || 1000) - 92) / 8.75));   // characters that fit a line
  const clip = (t) => (t.length > cols ? t.slice(0, cols - 1) + '…' : t);
  const draw = (k) => {
    const on = ranges(k === 0 ? el.dataset.hl0 || '' : steps[Math.min(k, steps.length) - 1]);
    let start = 0;
    if (lines.length > rows) {
      const hits = [...on].map((n) => n - from).filter((i) => i >= 0 && i < lines.length);
      const mid = hits.length ? Math.round((Math.min(...hits) + Math.max(...hits)) / 2) : 0;
      start = hits.length ? Math.max(0, Math.min(lines.length - rows, mid - Math.floor(rows / 2))) : 0;
    }
    const vis = lines.slice(start, start + rows);
    el.innerHTML = `<span class="hd">${esc(el.dataset.title || '')}${lines.length > rows ? ` · lines ${from + start}–${from + start + vis.length - 1} of ${all.length}` : ''}</span>` +
      vis.map((t, i) => { const n = from + start + i; return `<span class="ln${on.has(n) ? ' hl' : ''}"><i class="lno">${n}</i>${hl(clip(t)) || ' '}</span>`; }).join('');
  };
  return { step(k) { draw(k); } };
};

/* ======================= generic horizontal bars: data-src → {label: value} or [[label, value], …] =======================
   data-max (default: the largest), data-f ("pct" | "n" | "s" | "tok"), data-hi="label1,label2" (blue), data-steps="1" (one bar per click) */
FIGS.bars = (el) => {
  let d = get(el.dataset.src); if (d == null) return need(el, esc(el.dataset.src));
  let rows = Array.isArray(d) ? d : Object.entries(d);
  if (el.dataset.order) { const o = el.dataset.order.split(','); rows = o.map((k) => rows.find((r) => String(r[0]) === k)).filter(Boolean); }
  const rename = Object.fromEntries((el.dataset.names || '').split('|').filter(Boolean).map((p) => p.split('=')));
  const f = el.dataset.f || 'pct';
  const max = +(el.dataset.max || Math.max(...rows.map((r) => +r[1] || 0)));
  const hi = new Set((el.dataset.hi || '').split(',').filter(Boolean));
  const show = (v) => (v == null ? '–' : f === 'pct' ? pct(v) : f === 'n' ? fmt(v) : f === 's' ? ms(v) : f === 'tok' ? ktok(v) : f === 'r' ? (+v).toFixed(3) : String(v));
  const step = el.dataset.steps === '1';
  el.innerHTML = `<div class="hbars">${rows.map(([k, v], i) => `<div class="hz-r${hi.has(String(k)) ? ' hi' : ''}" ${step ? `data-k="${i}"` : ''}>
    <span class="hz-l">${esc(rename[k] || k)}</span><span class="hz-t"><i style="width:${Math.max(0.6, 100 * (+v || 0) / max)}%"></i></span><span class="hz-v">${show(v)}</span></div>`).join('')}</div>`;
  return { step(k) { if (step) reveal(el, k); } };
};

/* ======================= films (L2/L4 pattern: films/<name>.mp4 + .webm + .jpg; never autoplay) ======================= */
FIGS.film = (el) => {
  const n = el.dataset.name, base = 'films/' + n;
  const todo = () => { el.innerHTML = `<div class="todo-card f3"><span class="todo-k">TODO(film)</span><div>The narrated film <b>${esc(n)}</b> plays here: ${esc(el.dataset.what || '')}</div><div class="todo-s">Lands as films/${esc(n)}.mp4, .webm and .jpg (films/FILMS.md).</div></div>`; };
  el.innerHTML = `<video class="film" controls preload="metadata" playsinline poster="${base}.jpg"><source src="${base}.webm" type="video/webm"><source src="${base}.mp4" type="video/mp4"></video>
    <div class="ctl film-ctl"><button>Present (full screen)</button></div>`;
  const v = el.querySelector('video'), srcs = [...v.querySelectorAll('source')];
  let failed = 0;
  srcs.forEach((sc) => sc.addEventListener('error', () => { if (++failed === srcs.length) todo(); }));
  ['click', 'keydown', 'touchstart', 'touchend'].forEach((ev) => v.addEventListener(ev, stop));
  el.querySelector('.film-ctl button').onclick = (e) => { stop(e); (v.requestFullscreen || v.webkitRequestFullscreen || (() => {})).call(v); v.play(); };
  return { step() {} };
};

/* ======================= a live page in a frame (the RAG Lab, the Wiki Explorer) ======================= */
FIGS.frame = (el) => {
  const url = el.dataset.url, label = el.dataset.label || url;
  el.innerHTML = `<iframe src="${esc(url)}" title="${esc(label)}" loading="lazy" style="position:absolute;inset:0 0 58px 0;width:100%;height:calc(100% - 58px);border:0;border-radius:18px;background:#fff;box-shadow:var(--shadow)"></iframe>
    <div class="ctl" style="position:absolute;left:0;bottom:0;margin:0"><a class="live" href="${esc(url)}" target="_blank" rel="noopener">Open in a new tab <code>${esc(label)}</code></a></div>`;
  el.querySelector('a').addEventListener('click', stop);
  return { step() {} };
};

/* ======================= Ask Northbridge, knowledge stage: a recorded turn (tool call, then the reply) ======================= */
FIGS.chatk = (el) => {
  const T = get('knowledge.turns'); if (!T) return need(el, 'knowledge_stage.json turns.');
  const pick = (el.dataset.turns || '0').split(',').map(Number);
  let cur = pick[0];
  const draw = (k) => {
    const t = T[cur];
    const calls = t.calls.map((c) => `<div class="kq-call"><span class="kq-t">search_docs</span><code>${esc(JSON.stringify(c.args))}</code>
      <div class="kq-res">${c.n} passages${c.withheld ? ' · <b class="b">withheld notice</b>' : ''}: ${c.top.map((x) => `<span>${esc(x.cite)}</span>`).join('')}</div></div>`).join('');
    el.innerHTML = `${pick.length > 1 ? `<div class="ctl kq-tabs">${pick.map((i) => `<button class="${i === cur ? 'on' : ''}" data-i="${i}">${esc(T[i].question.slice(0, 34))}…</button>`).join('')}</div>` : ''}
      <div class="kq"><div class="kq-u"><span class="kq-who">${esc(t.user)} · Emma Clarke</span>${esc(t.question)}</div>
      <div class="kq-calls" data-k="1">${calls}</div>
      <div class="kq-a" data-k="2">${esc(t.reply).replace(/\n/g, '<br>')}</div>
      <div class="kq-m" data-k="2">${t.model_calls} model calls · ${fmt(t.tokens_in)} tokens in · ${t.seconds.toFixed(1)} s · ${esc(get('knowledge.model'))} · recorded in-process on 3 Nov 2026 (experiments/logs/knowledge_stage.json)</div></div>`;
    el.querySelectorAll('.kq-tabs button').forEach((b) => b.addEventListener('click', (e) => { stop(e); cur = +b.dataset.i; draw(9); }));
    reveal(el, k);
  };
  return { step(k) { draw(k); } };
};

/* ======================= Emma's question needs 11 sources, in these folders ======================= */
FIGS.goldmap = (el) => {
  const g = get('questions.emma.gold'); if (!g) return need(el, 'Q-EMMA gold sources.');
  const by = {};
  g.forEach((x) => { const f = x.file.split('/')[0]; (by[f] = by[f] || []).push(x); });
  el.innerHTML = `<div class="gm">${Object.entries(by).map(([f, xs], i) => `<div class="gm-f" data-k="${Math.min(i, 3)}"><div class="gm-h">${esc(f)}/</div>
    ${xs.map((x) => `<div class="gm-x${x.absent ? ' ab' : ''}"><b>${esc(x.file.split('/').pop())}</b>${x.absent ? '<span>what is NOT in it: Brightcell</span>' : x.section ? `<span>§ ${esc(x.section)}${x.page ? `, p.${esc(x.page)}` : ''}</span>` : ''}</div>`).join('')}</div>`).join('')}</div>
    <p class="ftiny">${g.filter((x) => !x.absent).length} gold passages (and one file that must NOT contain Brightcell) in ${Object.keys(by).length} folders: the golden set's own list for Q-EMMA (northbridge-docs/eval/questions.jsonl).</p>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= the repository's folders, with what the audit counted ======================= */
FIGS.tree = (el) => {
  const fo = get('readme.folders'), bf = get('audit.by_folder'); if (!fo || !bf) return need(el, 'README folders + audit.');
  el.innerHTML = `<table class="t tree3"><tr><th>Folder</th><th>What Henrik says it holds</th><th class="n" data-k="1">Files</th><th class="n" data-k="1">PDF pages</th><th class="n" data-k="1">Rows</th><th class="n" data-k="2">Tokens</th></tr>
    ${fo.filter(([f]) => bf[f.replace('/', '')]).map(([f, w]) => { const b = bf[f.replace('/', '')]; return `<tr><td><code>${esc(f)}</code></td><td>${esc(w.length > 92 ? w.slice(0, 90) + '…' : w)}</td>
      <td class="n" data-k="1">${fmt(b.files)}</td><td class="n" data-k="1">${b.pages ? fmt(b.pages) : ''}</td><td class="n" data-k="1">${b.rows ? fmt(b.rows) : ''}</td><td class="n" data-k="2">${ktok(b.tokens_o200k)}</td></tr>`; }).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= the Dump Explorer: a treemap of folders by tokens (or files); click a folder ======================= */
function squarify(items, x, y, w, h) {   // items: [{v, …}] sorted desc; returns [{…, x, y, w, h}]
  const out = [], total = items.reduce((s, i) => s + i.v, 0);
  let rest = items.slice(), X = x, Y = y, W = w, H = h, sum = total;
  while (rest.length) {
    const horiz = W >= H, side = horiz ? H : W;
    let row = [], best = Infinity;
    for (let i = 0; i < rest.length; i++) {
      const r = rest.slice(0, i + 1), s = r.reduce((a, b) => a + b.v, 0), len = (s / sum) * (horiz ? W : H);
      const worst = Math.max(...r.map((it) => { const o = (it.v / s) * side; return Math.max(len / o, o / len); }));
      if (worst > best) break;
      best = worst; row = r;
    }
    const s = row.reduce((a, b) => a + b.v, 0), len = (s / sum) * (horiz ? W : H);
    let off = 0;
    row.forEach((it) => { const o = (it.v / s) * side; out.push(horiz ? { ...it, x: X, y: Y + off, w: len, h: o } : { ...it, x: X + off, y: Y, w: o, h: len }); off += o; });
    if (horiz) { X += len; W -= len; } else { Y += len; H -= len; }
    sum -= s; rest = rest.slice(row.length);
  }
  return out;
}
FIGS.treemap = (el) => {
  const F = get('audit.files'); if (!F) return need(el, 'audit per_file.');
  let by = 'tok', open = null;
  const W = el.clientWidth || 1400, H = (el.clientHeight || 560) - 64;
  const draw = () => {
    const val = (f) => (by === 'tok' ? Math.max(f[4], 1) : 1);
    let items;
    if (!open) {
      const g = {};
      F.forEach((f) => { const k = f[1]; g[k] = g[k] || { k, v: 0, n: 0, cls: {} }; g[k].v += val(f); g[k].n++; g[k].cls[f[3]] = (g[k].cls[f[3]] || 0) + val(f); });
      items = Object.values(g).sort((a, b) => b.v - a.v);
    } else {
      items = F.filter((f) => f[1] === open).map((f) => ({ k: f[0].split('/').slice(1).join('/'), v: val(f), f })).sort((a, b) => b.v - a.v);
    }
    const rects = squarify(items, 0, 0, W, H);
    const cell = (r) => {
      const cls = open ? r.f[3] : Object.entries(r.cls).sort((a, b) => b[1] - a[1])[0][0];
      const lab = open ? `${esc(r.k)}<small>${r.f[2]} · ${ktok(r.f[4])} tokens${r.f[5] ? ` · ${r.f[5]} pp.` : ''}${r.f[6] ? ` · ${fmt(r.f[6])} rows` : ''}</small>`
        : `${esc(r.k)}/<small>${fmt(r.n)} files · ${ktok(F.filter((f) => f[1] === r.k).reduce((s, f) => s + f[4], 0))} tokens</small>`;
      return `<div class="tm-c" data-k="${esc(r.k)}" style="left:${r.x}px;top:${r.y}px;width:${Math.max(r.w - 3, 0)}px;height:${Math.max(r.h - 3, 0)}px;background:${CLSBG[cls]};box-shadow:inset 0 0 0 2px ${CLS[cls]}33">${r.w > 150 && r.h > 52 ? `<span>${lab}</span>` : r.w > 70 && r.h > 26 ? `<span class="sm">${esc(open ? r.k.split('/').pop() : r.k)}</span>` : ''}</div>`;
    };
    el.innerHTML = `<div class="ctl tm-ctl"><button class="${by === 'tok' ? 'on' : ''}" data-b="tok">Size by tokens</button><button class="${by === 'n' ? 'on' : ''}" data-b="n">Size by files</button>
      ${open ? `<button data-up="1">◀ All folders</button><span class="tm-open"><code>${esc(open)}/</code> · click a file for its numbers</span>` : '<span class="tm-open">Click a folder to open it</span>'}
      <span class="tm-leg">${Object.keys(CLS).map((c) => `<i style="background:${CLSBG[c]};box-shadow:inset 0 0 0 2px ${CLS[c]}55"></i>${c}`).join('')}</span></div>
      <div class="tm" style="height:${H}px">${rects.map(cell).join('')}</div>`;
    el.querySelectorAll('[data-b]').forEach((b) => b.addEventListener('click', (e) => { stop(e); by = b.dataset.b; draw(); }));
    el.querySelectorAll('[data-up]').forEach((b) => b.addEventListener('click', (e) => { stop(e); open = null; draw(); }));
    if (!open) el.querySelectorAll('.tm-c').forEach((c) => c.addEventListener('click', (e) => { stop(e); open = c.dataset.k; draw(); }));
  };
  draw();
  return { step() {} };
};

/* ======================= structured / semi-structured / unstructured: files against tokens ======================= */
FIGS.classes = (el) => {
  const c = get('audit.by_class'); if (!c) return need(el, 'audit by_class.');
  const order = ['unstructured', 'semi-structured', 'structured'];
  const tf = order.reduce((s, k) => s + c[k].files, 0), tt = order.reduce((s, k) => s + c[k].tokens_o200k, 0);
  const bar = (key, tot, f) => `<div class="cl-bar">${order.map((k) => `<i style="flex:${c[k][key]};background:${CLSBG[k]};box-shadow:inset 0 0 0 2px ${CLS[k]}55"><b>${f(c[k][key])}</b>${Math.round(100 * c[k][key] / tot)}%</i>`).join('')}</div>`;
  el.innerHTML = `<div class="cl"><div class="cl-row"><span class="cl-l">Files</span>${bar('files', tf, fmt)}</div>
    <div class="cl-row" data-k="1"><span class="cl-l">Tokens</span>${bar('tokens_o200k', tt, ktok)}</div>
    <div class="cl-keys">${order.map((k) => `<div class="card" data-k="2"><span class="tag" style="color:${CLS[k]}">${k}</span><b>${Object.entries(c[k].types).map(([t, n]) => `${n} ${t}`).join(' · ')}</b></div>`).join('')}</div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= what the audit flagged: the messiness Henrik warned about ======================= */
FIGS.messy = (el) => {
  const m = get('audit.messiness'), fl = get('audit.flags'); if (!m) return need(el, 'audit messiness.');
  const kinds = {}; m.forEach((x) => { kinds[x.kind] = kinds[x.kind] || x; });
  const pick = Object.values(kinds).slice(0, 8);
  el.innerHTML = `<div class="ms">${pick.map((x, i) => `<div class="ms-r" data-k="${Math.min(Math.floor(i / 3), 2)}"><span class="chip f">${esc(x.kind.replace(/_/g, ' '))}</span><span>${esc(x.what)}</span></div>`).join('')}</div>
    <p class="ftiny">${m.length} planted problems in eval/messiness.json, each traced through the parser · the parser's own flags: ${fl.superseded.n} superseded, ${fl.future.n} not yet in force, ${fl.confidential.n} confidential (audit.json).</p>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= the same file through the two parsers ======================= */
FIGS.parsers = (el) => {
  const P = get('extract.parsers'); if (!P) return need(el, 'deck_extract.json parsers.');
  const keys = (el.dataset.keys || 'email,supplier_master,scan,qrc').split(',');
  const names = { email: 'An e-mail', supplier_master: 'A spreadsheet row', scan: 'A scan', qrc: 'A quick-reference PDF', policy: 'A policy PDF' };
  let cur = keys[0];
  const unit = (p, which) => {
    const us = p[which].units;
    const u = cur === 'supplier_master' ? us.find((x) => /VC-EIN-0042|Voltway/.test(x.text)) || us[us.length - 1] : us[0];
    const txt = u ? u.text.split('\n').slice(0, 14).map((l) => (l.length > 64 ? l.slice(0, 63) + '…' : l)).join('\n') : '';
    return u ? `<pre class="px">${esc(txt) || '<i>(nothing: an image-only page has no text layer)</i>'}</pre><div class="px-m">${esc(JSON.stringify(u.loc))} · ${u.tokens} tokens</div>` : '<pre class="px"><i>(no unit)</i></pre>';
  };
  const draw = () => {
    const p = P[cur];
    el.innerHTML = `<div class="ctl">${keys.map((k) => `<button class="${k === cur ? 'on' : ''}" data-p="${k}">${names[k]}</button>`).join('')}</div>
      <div class="px-f"><code>${esc(p.file)}</code></div>
      <div class="px2"><div><div class="px-h b">plain · ${p.plain.n_units} units · ${fmt(p.plain.tokens)} tokens</div>${unit(p, 'plain')}</div>
      <div><div class="px-h a">structured · ${p.structured.n_units} units · ${fmt(p.structured.tokens)} tokens</div>${unit(p, 'structured')}</div></div>`;
    el.querySelectorAll('[data-p]').forEach((b) => b.addEventListener('click', (e) => { stop(e); cur = b.dataset.p; draw(); }));
  };
  draw();
  return { step() {} };
};

/* ======================= genesis / analytical / documentation ======================= */
FIGS.taxonomy = (el) => {
  const Q = get('questions'); if (!Q) return need(el, 'questions.jsonl.');
  // The documentation examples are spread over its ten types; the other two categories have their own lists.
  const ex = (cat) => Q.examples[cat] || ['single_lookup', 'procedure', 'rule', 'exact_code'].map((t) => Q.examples[t][0]);
  const col = (cat, name, tag, what, cls, k) => `<div class="card tx ${cls}" data-k="${k}"><span class="tag ${cls === 'af' ? 'af' : 'nt'}">${tag}</span><h3>${name} · ${fmt(Q.categories[cat])}</h3><p class="tx-w">${what}</p>
    <ul>${ex(cat).slice(0, 3).map((x) => `<li>“${esc(x.q)}”</li>`).join('')}</ul></div>`;
  el.innerHTML = `<div class="three tx3">${col('genesis', 'Genesis', 'Create or change something', '<b>Genesis</b> (making): the answer is an action in Ledgerline, such as raising an order. It needs write tools and an approval. Lecture 4 onward.', '', 0)}
    ${col('analytical', 'Analytical', 'Count, sum, compare', '<b>Analytical</b>: the answer is computed from the transaction data, by a query. Tools and SQL, later.', '', 1)}
    ${col('documentation', 'Documentation', 'How, what, which rule', '<b>Documentation</b>: the answer is written down somewhere in the dump, so we must find it. <b>Today.</b>', 'af', 2)}</div>`;
  return { step(k) { reveal(el, k); } };
};

FIGS.doctypes = (el) => {
  const Q = get('questions'); if (!Q) return need(el, 'questions.jsonl.');
  const order = ['single_lookup', 'procedure', 'rule', 'service_field', 'table_lookup', 'multi_hop', 'version_conflict', 'exact_code', 'not_in_docs', 'permission'];
  const max = Math.max(...order.map((t) => Q.types[t]));
  el.innerHTML = `<div class="dt">${order.map((t, i) => `<div class="dt-r" data-k="${i < 5 ? 0 : 1}"><span class="dt-t">${t.replace(/_/g, ' ')}</span><span class="dt-b"><i style="width:${100 * Q.types[t] / max}%"></i><b>${Q.types[t]}</b></span><span class="dt-e">“${esc(Q.examples[t][t === 'multi_hop' ? 1 : 0].q)}”</span></div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= paste everything: 4.69M tokens against the context windows ======================= */
FIGS.windows = (el) => {
  const P = get('paste'); if (!P) return need(el, 'paste_all.json.');
  const rows = [['The whole dump', P.total, 'dump'], ['without 06_transactions', P.subsets['without 06_transactions'], 'sub']]
    .concat(P.windows.map(([m, n]) => [m.split('/')[1], n, 'win']));
  const max = P.total;
  el.innerHTML = `<div class="pw3">${rows.map(([l, v, kind], i) => `<div class="pw-r ${kind}" data-k="${kind === 'dump' ? 0 : kind === 'sub' ? 2 : 1}"><span class="pw-l">${esc(l)}</span><span class="pw-b"><i style="width:${100 * v / max}%"></i></span><span class="pw-v">${ktok(v)}</span></div>`).join('')}</div>
    <p class="ftiny">Tokens: tiktoken o200k on the structured parser's text. Windows: OpenRouter's listed context_length on 3 Nov 2026 (paste_all.json). Fits any model: ${P.fits_any ? 'yes' : 'no'}.</p>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= chunking: one real document cut three ways ======================= */
FIGS.chunks = (el) => {
  const C = get('extract.chunks.' + (el.dataset.doc || 'policy')); if (!C) return need(el, 'deck_extract.json chunks.');
  const order = ['fixed', 'recursive', 'structure'];
  const name = { fixed: 'Fixed: every 200 tokens', recursive: 'Recursive: paragraphs, then lines', structure: 'Structure-aware: by heading' };
  let cur = 'fixed';
  const draw = () => {
    const c = C[cur];
    el.innerHTML = `<div class="ctl">${order.map((m) => `<button class="${m === cur ? 'on' : ''}" data-m="${m}">${name[m]} · ${C[m].n} chunks</button>`).join('')}</div>
      <div class="ck">${c.chunks.slice(1, 5).map((x, i) => `<div class="ck-c"><div class="ck-h"><b>#${i + 2}</b> ${esc(x.cite)} · ${x.tokens} tokens</div><div class="ck-hd">${esc(x.header.split('\n').pop())}</div><pre>${esc(x.body.length > 360 ? x.body.slice(0, 359) + '…' : x.body)}</pre></div>`).join('')}</div>`;
    el.querySelectorAll('[data-m]').forEach((b) => b.addEventListener('click', (e) => { stop(e); cur = b.dataset.m; draw(); }));
  };
  draw();
  return { step(k) { const want = order[Math.min(k, 2)]; if (want !== cur) { cur = want; draw(); } } };
};

/* ======================= the grid: 2,112 configurations, recall@5 against p95 search time ======================= */
FIGS.scatter = (el) => {
  const G = get('grid'); if (!G) return need(el, 'rag_grid.json.');
  const W = el.clientWidth || 1400, H = el.clientHeight || 560, m = { l: 80, r: 300, t: 20, b: 60 };
  const xs = (v) => m.l + (Math.log10(Math.max(v, 1e-4)) + 4) / (Math.log10(30) + 4) * (W - m.l - m.r);
  const ys = (v) => H - m.b - (v - 0.2) / 0.75 * (H - m.t - m.b);
  const col = { dense: '#7a5af5', bm25: '#138a60', hybrid: '#0b57d0' };
  const layers = [
    { k: 0, f: () => true, lab: 'all 2,112 rows' },
    { k: 1, f: (p) => p[2] === 'dense' && !p[3] && !p[4], lab: 'dense (embeddings) only' },
    { k: 2, f: (p) => p[2] === 'bm25' && !p[3] && !p[4], lab: 'BM25 only' },
    { k: 3, f: (p) => p[2] === 'hybrid' && !p[3] && !p[4], lab: 'hybrid (RRF)' },
    { k: 4, f: (p) => p[3] && !p[4], lab: '+ the reranker' },
    { k: 5, f: (p) => p[4], lab: '+ query rewriting' },
  ];
  const best = get('best.config');
  const isBest = (p) => p[6] === best.parser && p[7] === best.chunker && p[8] === best.size && p[9] === best.overlap && p[2] === best.retrieval && !!p[3] === best.rerank && !p[4] && p[5] === '-';
  const ticks = [1e-3, 1e-2, 0.1, 1, 10].map((t) => `<line x1="${xs(t)}" x2="${xs(t)}" y1="${m.t}" y2="${H - m.b}" class="gl"/><text x="${xs(t)}" y="${H - m.b + 24}" class="ax" text-anchor="middle">${ms(t)}</text>`).join('') +
    [0.3, 0.5, 0.7, 0.9].map((t) => `<line x1="${m.l}" x2="${W - m.r}" y1="${ys(t)}" y2="${ys(t)}" class="gl"/><text x="${m.l - 10}" y="${ys(t) + 5}" class="ax" text-anchor="end">${t.toFixed(1)}</text>`).join('');
  const draw = (k) => {
    const L = layers.filter((x) => x.k <= k && x.k > 0).pop();
    const dots = G.points.map((p) => {
      const on = !L || L.f(p);
      return `<circle cx="${xs(p[1]).toFixed(1)}" cy="${ys(p[0]).toFixed(1)}" r="${on && L ? 3.6 : 2.6}" fill="${on && L ? col[p[2]] : '#9aa3b2'}" fill-opacity="${on && L ? 0.75 : 0.22}"/>`;
    }).join('');
    const b = G.points.find(isBest);
    el.innerHTML = `<svg width="${W}" height="${H}">${ticks}
      <line x1="${xs(G.budget_p95_s)}" x2="${xs(G.budget_p95_s)}" y1="${m.t}" y2="${H - m.b}" class="budget"/><text x="${xs(G.budget_p95_s) + 6}" y="${m.t + 16}" class="ax b">200 ms budget</text>
      <line x1="${m.l}" x2="${W - m.r}" y1="${ys(0.9)}" y2="${ys(0.9)}" class="budget" style="stroke:var(--gold)"/><text x="${W - m.r - 4}" y="${ys(0.9) - 8}" class="ax" text-anchor="end" style="fill:var(--gold)">target 0.90</text>
      ${dots}
      ${k >= 6 && b ? `<circle cx="${xs(b[1])}" cy="${ys(b[0])}" r="11" fill="none" stroke="#c4511f" stroke-width="3"/><text x="${xs(b[1]) + 16}" y="${ys(b[0]) - 12}" class="ax b">chosen: ${(b[0]).toFixed(3)} at ${ms(b[1])}</text>` : ''}
      <text x="${(m.l + W - m.r) / 2}" y="${H - 12}" class="ax" text-anchor="middle">search time, p95 per question (log scale)</text>
      <text x="22" y="${(m.t + H - m.b) / 2}" class="ax" transform="rotate(-90 22 ${(m.t + H - m.b) / 2})" text-anchor="middle">recall@5</text></svg>
      <div class="sc-leg">${layers.slice(1).map((x) => `<div class="${x.k <= k ? 'on' : ''}"><i style="background:${x.k <= 3 ? col[['', 'dense', 'bm25', 'hybrid'][x.k]] : '#5f6672'}"></i>${x.lab}</div>`).join('')}
      <p>${fmt(G.n_rows)} configurations: 2 parsers × 3 chunkers × 4 sizes × 2 overlaps × 5 embedding models × dense/BM25/hybrid × reranker × rewriting, each searched for all 224 questions on ${esc(G.machine.split(',')[0])}.</p></div>`;
  };
  return { step(k) { draw(k); } };
};

/* ======================= exact codes: who finds ERR-PO-0412? ======================= */
FIGS.codes = (el) => {
  const F = get('fail'); if (!F) return need(el, 'rag_failures.json.');
  const order = ['dense', 'bm25', 'hybrid', 'hybrid+rerank'];
  el.innerHTML = `<div class="cd2"><div><h4>Recall@5 on the ${F.exact_code.dense.n} exact-code questions</h4>
    ${order.map((k) => `<div class="hz-r${k === 'bm25' ? ' hi' : ''}"><span class="hz-l">${k}</span><span class="hz-t"><i style="width:${100 * F.exact_code[k]['recall@5']}%"></i></span><span class="hz-v">${F.exact_code[k]['recall@5'].toFixed(2)}</span></div>`).join('')}
    <p class="ftiny">Dense: bge-small. With the best embedding model (nomic) dense reaches ${F.exact_code_by_model_dense.nomic.toFixed(2)}.</p></div>
    <div data-k="1"><h4>“What does ERR-PO-0412 mean and how do I fix it?” · the top 3</h4>
    ${['dense', 'bm25'].map((k) => `<div class="cd-m"><span class="tag ${k === 'bm25' ? 'af' : 'bf'}">${k} · first gold at rank ${F.q0412[k].rank_of_first_gold ?? 'none'}</span><ol>${F.q0412[k].top3.map((c) => `<li>${esc(c)}</li>`).join('')}</ol></div>`).join('')}</div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= Chroma's HNSW against the exact answer ======================= */
FIGS.hnsw = (el) => {
  const h = get('hnsw'); if (!h) return need(el, 'hnsw_check.json.');
  const rows = [['default', 'default (ef_search 10)'], ['ef_search200', 'ef_search 200'], ['ef_search1000', 'ef_search 1,000'], ['ef_search4000', 'ef_search 4,000']];
  el.innerHTML = `<div class="hbars">${rows.map(([k, l], i) => `<div class="hz-r${k === 'ef_search4000' ? ' hi' : ''}" data-k="${i ? 1 : 0}"><span class="hz-l">${l}</span><span class="hz-t"><i style="width:${100 * h[k]['overlap@10']}%"></i></span><span class="hz-v">${pct(h[k]['overlap@10'])} · ${h[k].ms_per_q} ms</span></div>`).join('')}</div>
    <p class="ftiny">${esc(h.what)}</p>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= answers for the 9 configurations we answered with ======================= */
FIGS.answers9 = (el) => {
  const c = get('best.candidates'); if (!c) return need(el, 'rag_best candidates.');
  const rows = c.slice().sort((a, b) => a.answer_correct - b.answer_correct);
  el.innerHTML = `<div class="hbars a9">${rows.map((x, i) => `<div class="hz-r${x.label === 'top config at k=10' ? ' hi' : ''}${x.under_budget ? '' : ' over'}" data-k="${i < 3 ? 0 : i < 6 ? 1 : 2}"><span class="hz-l">${esc(x.label)}</span><span class="hz-t"><i style="width:${100 * x.answer_correct}%"></i></span><span class="hz-v">${pct(x.answer_correct)} · ${ms(x.retrieval_p95_s)}</span></div>`).join('')}</div>
    <p class="ftiny">Answer correct (judge) on all 224 questions, and the search's p95. Same answer model and prompt for every row (rag_best.json → candidates).</p>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= what RAG retrieved for Emma, against what the question needed ======================= */
FIGS.ragitems = (el) => {
  const R = get('extract.race_items.' + (el.dataset.q || 'Q-EMMA')); if (!R) return need(el, 'race items.');
  const n = +(el.dataset.n || 6);
  el.innerHTML = `<div class="ri">${R.slice(0, n).map((x, i) => `<div class="ri-c" data-k="${i < 3 ? 0 : 1}"><span class="ri-n">${x.rank}</span><div><b>${esc(x.cite)}</b><p>${esc(x.body.replace(/\s+/g, ' ').slice(0, 170))}…</p></div></div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* Text spans filled from the data: <span data-l3="best.answers.answer_correct" data-f="pct"></span>. */
FIGS._fill = () => {
  document.querySelectorAll('[data-l3]').forEach((s) => {
    const v = get(s.dataset.l3);
    if (v == null) { s.innerHTML = '<span class="todo-in">TODO(L3 data)</span>'; return; }
    const f = s.dataset.f;
    s.textContent = f === 'n' ? fmt(v) : f === 'pct' ? pct(v) : f === 'pct0' ? pct(v, 0) : f === 's' ? ms(v) : f === 'tok' ? ktok(v) : f === 'r2' ? (+v).toFixed(2) : f === 'r3' ? (+v).toFixed(3) : f === 'usd' ? '$' + (+v).toFixed(4) : f === 'usd2' ? '$' + (+v).toFixed(2) : Array.isArray(v) ? v.join(', ') : String(v);
  });
};
})();
