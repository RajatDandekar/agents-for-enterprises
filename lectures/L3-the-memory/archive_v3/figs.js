/* Live figures for Lecture 3 · The Memory. Loaded BEFORE plates.js, after figdata.js (window.L3D).
   Every number drawn here comes from window.L3D, which experiments/figdata.py copies from experiments/logs/*.json. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const D = window.L3D || {};
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmtN = (n) => Number(n).toLocaleString('en-IN');
const rup = (x, d = 2) => '₹' + Number(x).toLocaleString('en-IN', { minimumFractionDigits: d, maximumFractionDigits: d });
const md = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
const hiCite = (s) => md(s).replace(/((?:POL|MAN|AMD|HR)-[A-Z0-9-]+ §\d+(?:\.\d+)?)/g, '<span class="cite">$1</span>');
const ctlRow = (el, html) => { const c = document.createElement('div'); c.className = 'ctl'; c.innerHTML = html; el.appendChild(c); return c; };
const DOCCOL = { 'POL-PUR-001': '#0b57d0', 'POL-SUP-003': '#3c90ff', 'POL-APR-002': '#7aa7e6', 'MAN-PUR-72': '#9aa3b2',
  'MAN-DD-72': '#c2c8d2', 'AMD-SUP-2026-02': '#138a60', 'AMD-PUR-2026-03': '#5cbf96', 'HR-CONF-007': '#c4511f' };
const C62 = 'POL-PUR-001 §6.2';
const on = (nodes, k) => nodes.forEach((n, i) => { n.style.opacity = i < k ? 1 : 0.12; });

/* ---------- cold open: Kavita asks; three real replies from the bare brain (logs/story.json → brain) ---------- */
FIGS.coldchat = (el) => {
  const tiers = [['gemini-3.5-flash-lite', 'small'], ['gemini-3.8-flash', 'default'], ['gemini-3.1-pro-preview', 'large']];
  el.innerHTML = `<div class="thread" style="height:400px">
    <div class="who" style="align-self:flex-end">Kavita Joshi · purchase executive</div>
    <div class="msg u" style="font-size:24px">${esc(D.brain ? 'Can I buy the gaskets from Shakti Seals? They quote ₹10.40' : '')}</div>
    <div id="cc-r" style="display:flex;flex-direction:column;gap:6px"><div class="who">Ask Rasoi · brain stage · <span id="cc-m"></span></div><div class="msg ag" style="font-size:22px" id="cc-a"></div></div>
    <div class="mini" id="cc-t" style="margin-top:auto"></div></div>`;
  const ctl = ctlRow(el, tiers.map(([m, t]) => `<button data-m="${m}">${t}: ${m}</button>`).join(''));
  const r = el.querySelector('#cc-r');
  const set = (m) => { const b = D.brain[m]; el.querySelector('#cc-a').textContent = b.answer; el.querySelector('#cc-m').textContent = m;
    el.querySelector('#cc-t').textContent = `${b.tokens_in} tokens in, ${b.tokens_out} out. No documents, no tools.`;
    ctl.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x.dataset.m === m)); };
  ctl.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => set(b.dataset.m)));
  return { step(k) { r.style.opacity = k >= 1 ? 1 : 0; ctl.style.opacity = k >= 2 ? 1 : 0.2; set(k >= 2 ? 'gemini-3.5-flash-lite' : 'gemini-3.5-flash-lite'); } };
};

/* ---------- the dates: Rasoi's documents are private and newer (bahi/docs front-matter) ---------- */
FIGS.timeline = (el) => {
  const P = window.Plates, W = 820, H = 430;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const d0 = new Date('2025-01-01'), d1 = new Date('2027-01-15'), sx = (d) => 30 + (new Date(d) - d0) / (d1 - d0) * (W - 60);
  P.svgEl('line', { x1: 30, x2: W - 30, y1: 220, y2: 220, style: 'stroke:var(--ink-3);stroke-width:2' }, svg);
  const ev = [['2025-01-15', 'Bahi user manual v7.2.3', 'var(--ink-2)', -1, 0],
    ['2026-04-01', 'Purchase Policy v4.1 (§6.2)', 'var(--after)', 1, 1],
    ['2026-09-01', 'Certificate rule amended', 'var(--gold)', -1, 2],
    ['2026-10-26', "Today, Bahi's clock", 'var(--before)', 1, 3],
    ['2026-12-01', 'Direct-order limit amended', 'var(--gold)', -1, 4]];
  const g = ev.map(([d, lab, c, s]) => {
    const x = sx(d), grp = P.svgEl('g', { style: 'transition:opacity .4s' }, svg);
    P.svgEl('line', { x1: x, x2: x, y1: 220, y2: 220 + s * 60, style: `stroke:${c};stroke-width:2` }, grp);
    P.svgEl('circle', { cx: x, cy: 220, r: 8, style: `fill:${c}` }, grp);
    P.txt(grp, x, 220 + s * 74 + (s > 0 ? 8 : 0), lab, `font:500 18px var(--font);fill:${c}`, x > W - 160 ? 'end' : x < 120 ? 'start' : 'middle');
    P.txt(grp, x, 220 + s * 74 + (s > 0 ? 30 : -22), d, 'font:15px var(--mono);fill:var(--ink-3)', x > W - 160 ? 'end' : x < 120 ? 'start' : 'middle');
    return grp;
  });
  const band = P.svgEl('g', { style: 'transition:opacity .4s' }, svg);
  P.svgEl('rect', { x: 30, y: 36, width: W - 60, height: 58, rx: 14, style: 'fill:var(--before-soft)' }, band);
  P.txt(band, W / 2, 62, 'None of these was ever on the public web.', 'font:500 20px var(--font);fill:var(--before)', 'middle');
  P.txt(band, W / 2, 84, 'A model trained on public text has never read a line of them.', 'font:17px var(--font);fill:var(--ink-2)', 'middle');
  return { step(k) { g.forEach((x, i) => { x.style.opacity = i <= k + 1 ? 1 : 0.1; }); band.style.opacity = k >= 3 ? 1 : 0; } };
};

/* ---------- the context window is the memory: §6.2 off / on (logs/story.json → brain, with62) ---------- */
FIGS.ctxwin = (el) => {
  el.innerHTML = `<div style="display:flex;gap:6px;height:64px;margin-bottom:14px" id="cw-strip"></div>
    <div class="card" style="min-height:200px;font-size:21px" id="cw-ans"></div><div class="mini" id="cw-n" style="margin-top:10px"></div>`;
  const ctl = ctlRow(el, `<button data-v="0">§6.2 not in the prompt</button><button data-v="1">§6.2 in the prompt</button>`);
  const strip = el.querySelector('#cw-strip'), ans = el.querySelector('#cw-ans'), n = el.querySelector('#cw-n');
  const seg = (t, w, c) => `<div style="flex:${w};background:${c};border-radius:12px;display:flex;align-items:center;justify-content:center;font:500 16px var(--font);color:var(--ink-2)">${t}</div>`;
  const set = (v) => {
    strip.innerHTML = seg('system prompt', 2, 'var(--card)') + (v ? seg('[POL-PUR-001 §6.2] Parts that come into contact with food …', 5, 'var(--after-soft)') : '') + seg('Kavita’s question', 2, 'var(--card-2)');
    const a = v ? D.with62 : D.brain['gemini-3.8-flash'];
    ans.innerHTML = `<div class="who">${v ? 'the same model, with one clause in its context window' : 'gemini-3.8-flash, brain stage'}</div>${hiCite(a.answer)}`;
    n.textContent = `${a.tokens_in} tokens in. ${v ? 'Now it names the food-grade rule and cites §6.2. Its opening line says the rest (does Shakti hold a certificate?) lives in Bahi: true, that is a fact, not a rule.' : 'It invents an “Approved Vendor List” and a standard. Rasoi has neither.'}`;
    ctl.querySelectorAll('button').forEach((b) => b.classList.toggle('on', +b.dataset.v === v));
  };
  ctl.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => set(+b.dataset.v)));
  return { step(k) { set(k >= 2 ? 1 : 0); } };
};

/* ---------- the corpus, token by token (logs/retrieval_eval.json → corpus) ---------- */
FIGS.corpus = (el) => {
  const rows = [...D.corpus].sort((a, b) => b.tokens - a.tokens), mx = rows[0].tokens;
  el.innerHTML = `<div class="cmp" style="gap:12px">${rows.map((d) => `<div class="row" style="grid-template-columns:300px 1fr"><div class="lab" style="font-size:18px">${esc(d.title.replace('Bahi ERP 7.2 ', 'Bahi ').replace(', Purchasing and Inventory Enquiry', '').replace(' (Confidential)', ''))}<div class="tiny" style="font-family:var(--mono)">${d.doc_id} · ${d.audience}</div></div>
    <div class="br"><div class="bar ${d.kavita_may_read ? 'a' : 'b'}" data-w="${Math.max(3, 100 * d.tokens / mx)}" style="width:0">${fmtN(d.tokens)}</div></div></div>`).join('')}</div>
    <p class="mini" style="margin-top:14px" id="co-n"></p>`;
  const bars = [...el.querySelectorAll('.bar')];
  el.querySelector('#co-n').innerHTML = `Kavita may read 7 of the 8 (${fmtN(D.full_ctx.words)} words). Pasted whole with headers: <b>${fmtN(D.full_ctx.tokens)} tokens</b>. The HR page (ember) is not for her.`;
  return { step(k) { bars.forEach((b, i) => { b.style.width = (k >= 0 ? b.dataset.w : 0) + '%'; }); } };
};

/* ---------- what pasting costs: questions per day (assumption) × measured ₹ per question (logs/answers_eval.json) ---------- */
FIGS.costcalc = (el) => {
  const E = D.eval || {};
  const per = (s) => E[s] ? E[s].cost_inr_40 / 40 : null;
  const sys = [['full', 'Paste Kavita’s documents', 'b'], ['company', 'Paste the whole company’s', 'b'], ['wiki', 'LLM wiki', 'a'], ['rag', 'RAG (search_policy)', 'a']].filter(([s]) => per(s) !== null);
  el.innerHTML = `<div class="cmp" id="cc-bars">${sys.map(([s, l, c]) => `<div class="row"><div class="lab">${l}</div><div class="br"><div class="bar ${c}" data-s="${s}" style="width:0"></div></div></div>`).join('')}</div>
    <p class="mini" id="cc-n" style="margin-top:14px"></p>`;
  const ctl = ctlRow(el, `<label>Questions a day (your assumption)</label><input type="range" min="50" max="5000" step="50" value="500"><output></output>`);
  const inp = ctl.querySelector('input'), out = ctl.querySelector('output'), bars = [...el.querySelectorAll('.bar')];
  const draw = () => {
    const q = +inp.value, mx = Math.max(...sys.map(([s]) => per(s))) * q * 30;
    out.textContent = fmtN(q) + ' a day';
    bars.forEach((b) => { const v = per(b.dataset.s) * q * 30; b.style.width = Math.max(14, 100 * v / mx) + '%'; b.textContent = rup(v, 0) + ' a month'; });
    el.querySelector('#cc-n').innerHTML = `Measured ₹ per question (40 questions, gemini-3.8-flash at the course’s list price): ${sys.map(([s, l]) => `${l.split(' (')[0]} ${rup(per(s), 3)}`).join(' · ')}. The month is your slider × 30.`;
  };
  inp.addEventListener('input', draw);
  return { step() { draw(); } };
};

/* ---------- scale: Kavita's documents vs the whole company's, pasted (logs/answers_eval.json) ---------- */
FIGS.scale = (el) => {
  const E = D.eval; if (!E) { el.textContent = 'not yet measured'; return { step() {} }; }
  const rows = [['tokens in, per question', (s) => E[s].all.tokens_in_mean, (v) => fmtN(v)], ['seconds, per answer', (s) => E[s].all.seconds_mean, (v) => v.toFixed(1)],
    ['₹ for 40 questions', (s) => E[s].cost_inr_40, (v) => rup(v)], ['correct of 40', (s) => E[s].all.correct, (v) => v]];
  el.innerHTML = `<table class="t" style="font-size:22px"><thead><tr><th></th><th>Kavita’s 7 documents</th><th>Whole company: ${D.company_ctx.docs} documents</th><th>RAG</th></tr></thead><tbody>
    ${rows.map(([l, f, g], i) => `<tr data-i="${i}"><td>${l}</td><td class="n">${g(f('full'))}</td><td class="n" style="color:var(--before)">${g(f('company'))}</td><td class="n" style="color:var(--after)">${g(f('rag'))}</td></tr>`).join('')}</tbody></table>`;
  const tr = [...el.querySelectorAll('tr[data-i]')];
  return { step(k) { on(tr, k + 1); } };
};

/* ---------- chunking slider on the real Purchase Policy (logs/retrieval_eval.json → chunking) ---------- */
FIGS.chunker = (el) => {
  const W = D.chunking.words, S = D.chunking.starts;
  const secOf = []; let si = -1;
  for (let i = 0; i < W.length; i++) { while (si + 1 < S.length && S[si + 1][0] <= i) si++; secOf.push(si >= 0 ? S[si][1] : ''); }
  const newline = new Set(S.map((s) => s[0]));
  const from = S.find((x) => x[1] === '§5')[0], to = S.find((x) => x[1] === '§6.4')[0];
  el.innerHTML = `<div class="card" style="height:500px;font:17px/1.6 var(--font);padding:14px 16px" id="ck-txt"></div>
    <div class="mini" id="ck-read" style="margin-top:10px;min-height:60px"></div>`;
  const ctl = ctlRow(el, `<button data-m="fixed" class="on">Fixed windows</button><button data-m="section">By clause</button><label style="margin-left:10px">Window</label><input type="range" min="40" max="200" step="10" value="120"><output></output>`);
  const box = el.querySelector('#ck-txt'), read = el.querySelector('#ck-read'), inp = ctl.querySelector('input'), out = ctl.querySelector('output');
  const tints = ['#e6f1ff', '#edfaf5', '#f2f1ff', '#fff1e8'];
  let mode = 'fixed';
  const draw = () => {
    const size = +inp.value, step = size - 20;
    const idx = mode === 'fixed' ? W.map((_, i) => Math.floor(i / step)) : secOf.map((s) => S.findIndex((x) => x[1] === s));
    let h = '';
    for (let i = Math.max(0, from); i < Math.min(W.length, to); i++) {
      const br = newline.has(i) ? '<br>' : '';
      const cut = i > 0 && idx[i] !== idx[i - 1] ? 'border-left:3px solid var(--ink);padding-left:3px;' : '';
      if (/^#+$/.test(W[i])) continue;
      h += `${br}<span style="background:${tints[((idx[i] % 4) + 4) % 4]};${secOf[i] === '§6.2' ? 'box-shadow:inset 0 -3px 0 var(--gold);' : ''}${cut}">${esc(W[i].replace(/\*\*/g, ''))} </span>`;
    }
    box.innerHTML = h;
    const f62 = secOf.indexOf('§6.2'), l62 = secOf.lastIndexOf('§6.2');
    const mem = new Set(secOf.filter((_, i) => idx[i] === idx[f62]));
    out.textContent = mode === 'fixed' ? `${size} words` : 'clauses';
    read.innerHTML = mode === 'fixed'
      ? `Windows of ${size} words, sliding by ${step}. The window holding the start of §6.2 also holds ${[...mem].filter((s) => s !== '§6.2').join(', ') || 'nothing else'}, ${idx[f62] === idx[l62] ? 'and all of §6.2' : '<span class="b">and cuts §6.2 in two</span>'}. It has no id to cite.`
      : `One chunk per clause. §6.2 is one chunk of ${D.chunking.c62_words} words, whole, with the id <span class="a">POL-PUR-001 §6.2</span>.`;
    inp.disabled = mode !== 'fixed';
    ctl.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x.dataset.m === mode));
  };
  ctl.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => { mode = b.dataset.m; draw(); }));
  inp.addEventListener('input', draw);
  return { step(k) { mode = k >= 2 ? 'section' : 'fixed'; draw(); } };
};

/* ---------- one chunk, zoomed in (the chunker's real output for §6.2) ---------- */
FIGS.chunkzoom = (el) => {
  const f = [['id = citation', 'POL-PUR-001 §6.2'], ['heading path', 'Purchase Policy › 6. Supplier qualification'], ['version, effective', 'v4.1, 2026-04-01'],
    ['audience', 'all purchase staff → clearance “purchase”'], ['status', 'in force (as of 2026-10-26)']];
  el.innerHTML = `<div class="json" style="white-space:pre-wrap;font-size:16px;background:var(--after-soft)">${esc(D.chunking.c62_render.replace(/\*\*/g, ''))}</div>
    <p class="mini" style="margin:10px 0 12px">Exactly what goes into the context window: <code>Chunk.render()</code>.</p>
    <div class="kv" style="display:grid;grid-template-columns:200px 1fr;gap:8px 14px;font-size:20px">${f.map(([k, v], i) => `<b data-i="${i}" style="font:600 15px/1.6 var(--font);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)">${k}</b><span data-i="${i}" class="mono" style="font-size:18px">${esc(v)}</span>`).join('')}</div>`;
  const cells = [...el.querySelectorAll('[data-i]')];
  return { step(k) { cells.forEach((c) => { const i = +c.dataset.i; c.style.opacity = i < k ? 1 : 0.15; c.style.color = i === k - 1 ? 'var(--after)' : ''; }); } };
};

/* ---------- section vs fixed chunks, measured (logs/retrieval_eval.json → fixed_vs_section, summary) ---------- */
FIGS.fixsec = (el) => {
  const F = D.fixed_vs_section, n = F.n, S = D.summary;
  const m = [['bm25', 'BM25'], ['vector', 'Embeddings'], ['hybrid', 'Hybrid']];
  el.innerHTML = `<div class="cmp" style="gap:24px">${m.map(([k, l]) => `<div class="row"><div class="lab">${l}</div><div class="br">
    <div class="bar a" data-w="${100 * Math.round(S[k]['recall@5'] * n) / n}" style="width:0">by clause: ${Math.round(S[k]['recall@5'] * n)} of ${n}</div>
    <div class="bar b" data-w="${100 * F.fixed_top5[k].whole_clause / n}" style="width:0">120-word windows: ${F.fixed_top5[k].whole_clause} of ${n}</div></div></div>`).join('')}</div>
    <p class="mini" style="margin-top:16px">Questions whose right clause is found, whole, in the top 5. By clause: ${F.n_section_chunks} chunks; windows: ${F.n_fixed_chunks}. A window that holds only the start of the clause does not count (it would: ${m.map(([k, l]) => `${l} ${F.fixed_top5[k].clause_start}`).join(', ')}).</p>`;
  const bars = [...el.querySelectorAll('.bar')];
  return { step(k) { bars.forEach((b) => { b.style.width = b.dataset.w + '%'; }); } };
};

/* ---------- the question as BM25 sees it (logs/retrieval_eval.json → s1.tokens) ---------- */
FIGS.tokens = (el) => {
  const q = 'Can we buy the 5-litre gaskets from a supplier that doesn\'t have a food-grade certificate? Their price is much better.';
  const kept = new Set(D.s1.tokens);
  const words = q.split(' ');
  el.innerHTML = `<div class="card" style="font-size:26px;line-height:1.9" id="tk-q">${words.map((w) => `<span class="w" style="padding:2px 6px;border-radius:8px;margin-right:4px;transition:all .4s">${esc(w)}</span>`).join('')}</div>
    <div style="margin-top:18px;display:flex;flex-wrap:wrap;gap:8px" id="tk-t">${D.s1.tokens.map((t) => `<span style="font:500 20px var(--mono);padding:6px 12px;border-radius:999px;background:var(--after-soft);color:var(--after)">${esc(t)}</span>`).join('')}</div>
    <p class="mini" style="margin-top:14px">Lower case; small words (can, we, the, from, a, that, have, is) dropped; plurals cut (gaskets → gasket); a code with a hyphen kept whole <i>and</i> split (food-grade → food-grade, food, grade).</p>`;
  const ws = [...el.querySelectorAll('.w')], tt = el.querySelector('#tk-t');
  return { step(k) { ws.forEach((w) => { const t = w.textContent.toLowerCase().replace(/[^a-z0-9-]/g, '').replace(/s$/, ''); const keep = [...kept].some((x) => x === t || x === t + 's' || t.startsWith(x) && x.length > 3); w.style.background = k >= 1 ? (keep ? 'var(--after-soft)' : 'transparent') : 'transparent'; w.style.color = k >= 1 && !keep ? 'var(--ink-3)' : ''; w.style.textDecoration = k >= 1 && !keep ? 'line-through' : ''; }); tt.style.opacity = k >= 2 ? 1 : 0; } };
};

/* ---------- term frequency with diminishing returns, and length (BM25's tf part) ---------- */
FIGS.tfsat = (el) => {
  const P = window.Plates, W = 800, H = 450, x0 = 70, y0 = 380, xs = 64, ys = 135;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  P.svgEl('line', { x1: x0, y1: y0, x2: W - 20, y2: y0, style: 'stroke:var(--ink-3)' }, svg);
  P.svgEl('line', { x1: x0, y1: y0, x2: x0, y2: 20, style: 'stroke:var(--ink-3)' }, svg);
  for (let t = 0; t <= 10; t += 2) P.txt(svg, x0 + t * xs, y0 + 24, t, 'font:15px var(--mono);fill:var(--ink-3)', 'middle');
  P.txt(svg, W / 2, H - 20, 'times the word appears in the chunk (tf)', 'font:16px var(--font);fill:var(--ink-2)', 'middle');
  for (let v = 0; v <= 2.5; v += 0.5) P.txt(svg, x0 - 10, y0 - v * ys + 5, v.toFixed(1), 'font:15px var(--mono);fill:var(--ink-3)', 'end');
  P.txt(svg, x0 + 12, 22, 'weight of the word (before idf)', 'font:16px var(--font);fill:var(--ink-2)');
  const lin = P.svgEl('path', { style: 'fill:none;stroke:var(--before);stroke-width:2;stroke-dasharray:6 5' }, svg);
  const cur = P.svgEl('path', { style: 'fill:none;stroke:var(--after);stroke-width:3.5' }, svg);
  const lab = P.txt(svg, W - 30, 120, '', 'font:500 17px var(--font);fill:var(--after)', 'end');
  P.txt(svg, x0 + 3.1 * xs, 40, 'just counting', 'font:16px var(--font);fill:var(--before)');
  const ctl = ctlRow(el, `<label>k₁</label><input type="range" min="0.2" max="3" step="0.1" value="1.2" style="width:190px"><output style="min-width:40px"></output><label style="margin-left:14px">chunk length ÷ average</label><input type="range" min="0.25" max="3" step="0.05" value="${(D.s1.c62.dl / D.s1.avgdl).toFixed(2)}" style="width:190px"><output style="min-width:50px"></output>`);
  const [ik, il] = ctl.querySelectorAll('input'), [ok, ol] = ctl.querySelectorAll('output');
  const draw = () => {
    const k1 = +ik.value, L = +il.value, b = 0.75, f = (t) => t * (k1 + 1) / (t + k1 * (1 - b + b * L));
    let d = '', dl = '';
    for (let t = 0; t <= 10; t += 0.1) { d += (t ? 'L' : 'M') + (x0 + t * xs) + ',' + (y0 - f(t) * ys); }
    for (let t = 0; t <= 2.6; t += 0.1) dl += (t ? 'L' : 'M') + (x0 + t * xs) + ',' + (y0 - t * ys);
    cur.setAttribute('d', d); lin.setAttribute('d', dl);
    lab.textContent = `1 → ${f(1).toFixed(2)}, 2 → ${f(2).toFixed(2)}, 10 → ${f(10).toFixed(2)} (ceiling ${(k1 + 1).toFixed(1)})`;
    ok.textContent = k1.toFixed(1); ol.textContent = L.toFixed(2) + '×';
  };
  ik.addEventListener('input', draw); il.addEventListener('input', draw);
  return { step(k) { draw(); lin.style.opacity = k >= 1 ? 1 : 0.15; } };
};

/* ---------- idf: rare words count more (logs/retrieval_eval.json → s1.df, s1.idf) ---------- */
FIGS.idf = (el) => {
  const Z = D.s1, terms = Object.keys(Z.df).filter((t) => Z.df[t] > 0).sort((a, b) => Z.idf[b] - Z.idf[a]), mx = Math.max(...terms.map((t) => Z.idf[t]));
  el.innerHTML = `<table class="t" style="font-size:20px"><thead><tr><th>word</th><th>chunks containing it (of ${Z.N})</th><th>idf</th><th style="width:300px"></th></tr></thead><tbody>
    ${terms.map((t) => `<tr><td class="n" style="font-size:19px">${esc(t)}</td><td class="n">${Z.df[t]}</td><td class="n">${Z.idf[t].toFixed(2)}</td><td><div class="bar" style="height:18px;border-radius:7px;background:linear-gradient(90deg,#1b5fb5,#5a9cf5);width:${300 * Z.idf[t] / mx}px"></div></td></tr>`).join('')}</tbody></table>
    <p class="mini" style="margin-top:10px">Words that appear in no chunk at all (${Object.keys(Z.df).filter((t) => !Z.df[t]).join(', ') || 'none'}) add nothing.</p>`;
  const tr = [...el.querySelectorAll('tbody tr')];
  return { step(k) { tr.forEach((r, i) => { r.style.opacity = k >= 1 || i < 3 ? 1 : 0.15; }); } };
};

/* ---------- BM25 for §6.2, term by term (logs/retrieval_eval.json → s1.c62) ---------- */
FIGS.bm25work = (el) => {
  const Z = D.s1, c = Z.c62, terms = Object.keys(c.terms), tot = terms.reduce((a, t) => a + c.terms[t], 0);
  const norm = (1 - 0.75 + 0.75 * c.dl / Z.avgdl);
  el.innerHTML = `<div class="json" style="font-size:17px;margin-bottom:12px">§6.2: |d| = ${c.dl} words, avgdl = ${Z.avgdl} → length factor 1 − b + b·|d|/avgdl = ${norm.toFixed(3)}</div>
    <table class="t" style="font-size:20px"><thead><tr><th>word</th><th>tf</th><th>idf</th><th>idf · tf·2.2 / (tf + 1.2·${norm.toFixed(3)})</th></tr></thead><tbody>
    ${terms.map((t) => `<tr><td class="n">${esc(t)}</td><td class="n">${c.tf[t]}</td><td class="n">${Z.idf[t].toFixed(3)}</td><td class="n">${c.terms[t].toFixed(3)}</td></tr>`).join('')}
    <tr class="tot"><td><b>BM25(question, §6.2)</b></td><td></td><td></td><td class="n" style="color:var(--after);font-weight:600">${tot.toFixed(3)}</td></tr></tbody></table>`;
  const tr = [...el.querySelectorAll('tbody tr')];
  return { step(k) { tr.forEach((r, i) => { r.style.opacity = i === tr.length - 1 ? (k >= 2 ? 1 : 0.1) : (k >= 1 ? 1 : 0.15); }); } };
};

/* ---------- BM25 over the corpus, split by word (logs/retrieval_eval.json → s1.bm25) ---------- */
FIGS.bm25 = (el) => {
  const rows = D.s1.bm25, mx = rows[0].score, cols = {};
  const pal = ['#0b57d0', '#3c90ff', '#7aa7e6', '#138a60', '#5cbf96', '#c4511f', '#eb6834', '#9aa3b2', '#45474d'];
  D.s1.tokens.forEach((t) => { if (!(t in cols)) cols[t] = pal[Object.keys(cols).length % pal.length]; });
  el.innerHTML = rows.map((r, i) => `<div class="brow" style="display:grid;grid-template-columns:190px 1fr 70px;gap:10px;align-items:center;margin-bottom:9px;transition:opacity .4s">
    <div class="mono" style="font-size:16px;${r.id === C62 ? 'color:var(--after);font-weight:600' : ''}">${i + 1}. ${r.id}</div>
    <div style="display:flex;height:30px">${Object.entries(r.terms).map(([t, v]) => `<div title="${t}" style="width:${520 * v / mx}px;background:${cols[t]};color:#fff;font:500 13px/30px var(--font);overflow:hidden;white-space:nowrap;padding-left:4px;border-right:2px solid #fff">${esc(t)}</div>`).join('')}</div>
    <div class="mono" style="font-size:16px">${r.score.toFixed(2)}</div></div>`).join('') + `<p class="mini">Each bar is one chunk's real BM25 score, split by the words that earned it.</p>`;
  const br = [...el.querySelectorAll('.brow')];
  return { step(k) { br.forEach((b, i) => { b.style.opacity = k >= 1 || i < 4 ? 1 : 0.2; b.style.outline = k >= 2 && rows[i].id === 'POL-SUP-003 §4.2' ? '2px solid var(--before)' : ''; }); } };
};

/* ---------- embeddings: every chunk's 384 numbers squeezed to 2 (logs/retrieval_eval.json → pca) ---------- */
FIGS.embed = (el) => {
  const P = window.Plates, W = 820, H = 560, pad = 36;
  const pts = D.pca.points, qs = D.pca.queries;
  const xs = pts.map((p) => p[2]).concat(Object.values(qs).map((q) => q.x)), ys = pts.map((p) => p[3]).concat(Object.values(qs).map((q) => q.y));
  const [x1, x2, y1, y2] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const sx = (x) => pad + (x - x1) / (x2 - x1) * (W - 2 * pad), sy = (y) => H - pad - (y - y1) / (y2 - y1) * (H - 2 * pad - 40);
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  Object.keys(DOCCOL).forEach((d, i) => { P.svgEl('circle', { cx: 12 + (i % 4) * 200, cy: 12 + Math.floor(i / 4) * 22, r: 5, style: `fill:${DOCCOL[d]}` }, svg); P.txt(svg, 22 + (i % 4) * 200, 17 + Math.floor(i / 4) * 22, d, 'font:14px var(--mono);fill:var(--ink-2)'); });
  const lines = P.svgEl('g', {}, svg);
  const tip = P.txt(svg, W - 10, H - 6, '', 'font:15px var(--mono);fill:var(--ink)', 'end');
  const dots = pts.map((p) => { const c = P.svgEl('circle', { cx: sx(p[2]), cy: sy(p[3]), r: p[0] === C62 ? 8 : 4.5, style: `fill:${DOCCOL[p[1]]};opacity:.8;cursor:pointer;transition:opacity .4s` }, svg);
    c.addEventListener('mouseenter', () => { tip.textContent = `${p[0]} · cosine to Kavita's question ${p[4].toFixed(3)}`; }); return c; });
  const p62 = pts.find((p) => p[0] === C62);
  P.txt(svg, sx(p62[2]) + 12, sy(p62[3]) + 5, '§6.2', 'font:600 17px var(--mono);fill:var(--after)');
  const star = P.svgEl('path', { d: 'M0,-14 L4,-4 L14,-4 L6,3 L9,13 L0,7 L-9,13 L-6,3 L-14,-4 L-4,-4 Z', style: 'fill:var(--ink)' }, svg);
  const lab = P.txt(svg, 0, 0, '', 'font:500 17px var(--font);fill:var(--ink)');
  const names = { shakti: 'Kavita: Shakti Seals', P13: 'P13: CGST or IGST?', M01: 'M01: ERR-PO-0412', T01: 'T01: gaskets in stock' };
  const ctl = ctlRow(el, Object.keys(names).map((k) => `<button data-q="${k}">${names[k]}</button>`).join(''));
  const top = [...pts].sort((a, b) => b[4] - a[4]).slice(0, 5);
  const set = (key) => { const q = qs[key]; star.setAttribute('transform', `translate(${sx(q.x)},${sy(q.y)})`); lab.setAttribute('x', sx(q.x) + 16); lab.setAttribute('y', sy(q.y) - 12); lab.textContent = names[key];
    lines.innerHTML = ''; if (key === 'shakti') top.forEach((p) => P.svgEl('line', { x1: sx(q.x), y1: sy(q.y), x2: sx(p[2]), y2: sy(p[3]), style: 'stroke:var(--after);stroke-width:1.5;stroke-dasharray:4 3' }, lines));
    ctl.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.q === key)); };
  ctl.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => set(b.dataset.q)));
  tip.textContent = `2 of 384 directions keep ${(100 * (D.pca.explained[0] + D.pca.explained[1])).toFixed(0)}% of the spread. Hover a dot.`;
  return { step(k) { dots.forEach((c) => { c.style.opacity = k >= 1 ? 0.8 : 0.25; }); set('shakti'); } };
};

/* ---------- cosine in two dimensions (a toy you can turn) ---------- */
FIGS.cos2d = (el) => {
  const P = window.Plates, W = 560, H = 440, cx = 120, cy = 360, R = 260;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  P.svgEl('line', { x1: cx - 20, y1: cy, x2: W - 10, y2: cy, style: 'stroke:var(--rule)' }, svg);
  P.svgEl('line', { x1: cx, y1: cy + 20, x2: cx, y2: 10, style: 'stroke:var(--rule)' }, svg);
  const a = P.svgEl('line', { x1: cx, y1: cy, style: 'stroke:var(--ink);stroke-width:4' }, svg);
  const b = P.svgEl('line', { x1: cx, y1: cy, style: 'stroke:var(--after);stroke-width:4' }, svg);
  const arc = P.svgEl('path', { style: 'fill:none;stroke:var(--gold);stroke-width:2' }, svg);
  const la = P.txt(svg, 0, 0, 'question', 'font:500 18px var(--font);fill:var(--ink)'), lb = P.txt(svg, 0, 0, 'clause', 'font:500 18px var(--font);fill:var(--after)');
  const out = document.createElement('div'); out.className = 'json'; out.style.cssText = 'font-size:17px;margin-top:8px'; el.appendChild(out);
  const ctl = ctlRow(el, `<label>angle between them</label><input type="range" min="0" max="180" value="40"><output></output>`);
  const inp = ctl.querySelector('input'), o = ctl.querySelector('output');
  const qa = 15 * Math.PI / 180;
  const draw = () => {
    const th = +inp.value * Math.PI / 180, ba = qa + th, len2 = 0.8;
    const A = [Math.cos(qa), Math.sin(qa)], B = [len2 * Math.cos(ba), len2 * Math.sin(ba)];
    a.setAttribute('x2', cx + R * A[0]); a.setAttribute('y2', cy - R * A[1]); b.setAttribute('x2', cx + R * B[0]); b.setAttribute('y2', cy - R * B[1]);
    la.setAttribute('x', cx + R * A[0] - 40); la.setAttribute('y', cy - R * A[1] + 26); lb.setAttribute('x', cx + R * B[0] + (B[0] < 0 ? -64 : 6)); lb.setAttribute('y', cy - R * B[1] - 8);
    const r = 70; arc.setAttribute('d', `M${cx + r * Math.cos(qa)},${cy - r * Math.sin(qa)} A${r},${r} 0 0 0 ${cx + r * Math.cos(ba)},${cy - r * Math.sin(ba)}`);
    const dot = A[0] * B[0] + A[1] * B[1], na = 1, nb = len2;
    out.textContent = `a = (${A[0].toFixed(2)}, ${A[1].toFixed(2)})   b = (${B[0].toFixed(2)}, ${B[1].toFixed(2)})\na·b = ${dot.toFixed(3)}   |a| = ${na.toFixed(2)}   |b| = ${nb.toFixed(2)}\ncos = a·b / (|a|·|b|) = ${(dot / (na * nb)).toFixed(3)}`;
    o.textContent = `${inp.value}°`;
  };
  inp.addEventListener('input', draw);
  return { step() { draw(); } };
};

/* ---------- the real cosine: 384 products, added up (logs/retrieval_eval.json → shakti.qvec, shakti.c62vec) ---------- */
FIGS.cosreal = (el) => {
  const P = window.Plates, q = D.s1.qvec, c = D.s1.c62vec, n = q.length, W = 820, H = 380;
  const prod = q.map((x, i) => x * c[i]), cum = []; prod.reduce((s, x, i) => (cum[i] = s + x), 0);
  el.innerHTML = `<div class="json" id="cr-v" style="font-size:15.5px;margin-bottom:10px"></div>`;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const mxp = Math.max(...prod.map(Math.abs)), sx = (i) => 50 + i / n * (W - 70), mid = 140;
  prod.forEach((p, i) => P.svgEl('rect', { x: sx(i), y: p > 0 ? mid - 110 * p / mxp : mid, width: Math.max(1, (W - 70) / n - 0.3), height: Math.max(0.5, 110 * Math.abs(p) / mxp), style: `fill:${p > 0 ? 'var(--after)' : 'var(--before)'};opacity:.75` }, svg));
  P.txt(svg, 4, mid + 5, 'qᵢ·dᵢ', 'font:15px var(--mono);fill:var(--ink-3)');
  const base = 360, top = 270, sy = (v) => base - v / cum[n - 1] * (base - top);
  P.svgEl('line', { x1: 50, x2: W - 20, y1: base, y2: base, style: 'stroke:var(--rule)' }, svg);
  P.txt(svg, 4, top + 5, 'sum', 'font:15px var(--mono);fill:var(--ink-3)');
  const path = P.svgEl('path', { style: 'fill:none;stroke:var(--gold);stroke-width:3' }, svg);
  const cur = P.svgEl('line', { y1: 20, y2: base, style: 'stroke:var(--ink);stroke-width:1.5;stroke-dasharray:4 3' }, svg);
  const ctl = ctlRow(el, `<label>dimensions added</label><input type="range" min="1" max="${n}" value="${n}"><output></output>`);
  const inp = ctl.querySelector('input'), o = ctl.querySelector('output'), v = el.querySelector('#cr-v');
  const draw = () => {
    const m = +inp.value; let d = '';
    for (let i = 0; i < m; i++) d += (i ? 'L' : 'M') + sx(i) + ',' + sy(cum[i]);
    path.setAttribute('d', d); cur.setAttribute('x1', sx(m - 1)); cur.setAttribute('x2', sx(m - 1));
    o.textContent = `${m} of ${n}: sum = ${cum[m - 1].toFixed(4)}`;
    v.textContent = `q = embed(question) = [${q.slice(0, 5).map((x) => x.toFixed(4)).join(', ')}, …]  |q| = ${D.s1.qnorm}\nd = embed(§6.2)     = [${c.slice(0, 5).map((x) => x.toFixed(4)).join(', ')}, …]  |d| = ${D.s1.c62norm}\ncos(q, d) = Σ qᵢ·dᵢ / (|q|·|d|) = ${(cum[n - 1] / (D.s1.qnorm * D.s1.c62norm)).toFixed(4)}`;
  };
  inp.addEventListener('input', draw);
  return { step(k) { if (k === 0) inp.value = 8; else if (k >= 1 && +inp.value < n) inp.value = n; draw(); } };
};

/* ---------- where each method goes blind (logs/retrieval_eval.json → ranks P01, M01) ---------- */
FIGS.blind = (el) => {
  const rows = [['P01 · scenario 1: “a supplier that doesn’t have a food-grade certificate”', 'POL-PUR-001 §6.2', D.ranks.P01], ['M01 · “What does error ERR-PO-0412 mean?”', 'MAN-PUR-72 §17.2', D.ranks.M01]];
  const modes = [['bm25', 'BM25'], ['vector', 'Embeddings']];
  el.innerHTML = `<table class="t" style="font-size:22px"><thead><tr><th>Question</th><th>Right clause</th>${modes.map((m) => `<th class="s">${m[1]}</th>`).join('')}</tr></thead><tbody>
    ${rows.map(([q, g, r], i) => `<tr data-r="${i}"><td>${q}</td><td class="n">${g}</td>${modes.map(([m]) => { const v = r[m]; const c = v === 1 ? 'p' : v && v <= 3 ? 'h' : 'f'; return `<td class="s"><span class="chip ${c}" style="font-size:18px;min-width:66px">${v ? 'rank ' + v : 'not in top 10'}</span></td>`; }).join('')}</tr>`).join('')}</tbody></table>`;
  const tr = [...el.querySelectorAll('tr[data-r]')];
  return { step(k) { tr.forEach((t, i) => { t.style.opacity = i <= k ? 1 : 0.12; }); } };
};

/* ---------- reciprocal rank fusion, worked (logs/retrieval_eval.json → s1.hybrid) ---------- */
FIGS.rrf = (el) => {
  const H = D.s1.hybrid.slice(0, 6);
  el.innerHTML = `<table class="t" style="font-size:20px"><thead><tr><th>chunk</th><th>BM25 rank</th><th>vector rank</th><th>1/(k+r₁) + 1/(k+r₂)</th><th>fused rank</th></tr></thead><tbody id="rf-b"></tbody></table>`;
  const ctl = ctlRow(el, `<label>k</label><input type="range" min="1" max="120" value="60"><output></output>`);
  const inp = ctl.querySelector('input'), o = ctl.querySelector('output'), tb = el.querySelector('#rf-b');
  const draw = () => {
    const k = +inp.value, sc = H.map((h) => ({ id: h.id, b: h.bm25_rank, v: h.vec_rank, s: (h.bm25_rank && h.bm25_rank <= 20 ? 1 / (k + h.bm25_rank) : 0) + (h.vec_rank && h.vec_rank <= 20 ? 1 / (k + h.vec_rank) : 0) }));
    const order = [...sc].sort((a, b) => b.s - a.s).map((x) => x.id);
    tb.innerHTML = sc.map((x) => `<tr style="${x.id === C62 ? 'background:var(--after-soft)' : ''}"><td class="n">${x.id}</td><td class="n">${x.b ?? '–'}</td><td class="n">${x.v ?? '–'}</td><td class="n">1/${k + x.b} + 1/${x.v <= 20 ? k + x.v : '∞'} = ${x.s.toFixed(5)}</td><td class="n"><b>${order.indexOf(x.id) + 1}</b></td></tr>`).join('');
    o.textContent = k === 60 ? '60 (the usual choice)' : String(k);
  };
  inp.addEventListener('input', draw);
  return { step() { draw(); } };
};

/* ---------- four rankings for one question (logs/retrieval_eval.json → s1) ---------- */
FIGS.rankings = (el) => {
  const Z = D.s1, M = { bm25: ['BM25 score', Z.bm25.map((r) => [r.id, r.score])], vector: ['cosine', Z.vector.map((r) => [r.id, r.cos])],
    hybrid: ['RRF score', Z.hybrid.map((r) => [r.id, r.rrf])], rerank: ['reranker score', Z.rerank.map((r) => [r.id, r.rerank])] };
  const names = { bm25: 'BM25', vector: 'Embeddings', hybrid: 'Hybrid (RRF)', rerank: 'Hybrid + rerank' };
  el.innerHTML = `<div class="ctl" style="margin:0 0 12px">${Object.keys(M).map((m) => `<button data-m="${m}">${names[m]}</button>`).join('')}</div><div id="rk"></div><p class="mini" id="rk-n" style="margin-top:8px"></p>`;
  const box = el.querySelector('#rk'), note = el.querySelector('#rk-n');
  const set = (m) => {
    const [unit, rows] = M[m], vals = rows.map((r) => r[1]), mx = Math.max(...vals), mn = Math.min(0, ...vals);
    box.innerHTML = `<table class="t" style="font-size:19px"><thead><tr><th>#</th><th>chunk</th><th>${unit}</th><th style="width:280px"></th></tr></thead><tbody>${rows.map(([id, v], i) =>
      `<tr style="${id === C62 ? 'background:var(--after-soft)' : ''}"><td class="n">${i + 1}</td><td class="n" style="${id === C62 ? 'color:var(--after);font-weight:600' : ''}">${id}</td><td class="n">${Math.abs(v) < 0.1 ? v.toFixed(5) : v.toFixed(m === 'vector' ? 4 : 3)}</td><td><div style="height:15px;border-radius:6px;width:${Math.max(2, 270 * (v - mn) / (mx - mn))}px;background:${v < 0 ? 'var(--before)' : 'var(--after)'};opacity:.75"></div></td></tr>`).join('')}</tbody></table>`;
    const r = rows.findIndex((x) => x[0] === C62) + 1;
    note.textContent = `§6.2 is rank ${r} under ${names[m]}.` + (m === 'rerank' ? ' Reranker scores: 0 is even odds; below 0, probably not relevant.' : '');
    el.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.m === m));
  };
  el.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => set(b.dataset.m)));
  return { step(k) { set(['bm25', 'vector', 'hybrid', 'rerank'][Math.min(k, 3)]); } };
};

/* ---------- recall@k, measured (logs/retrieval_eval.json → summary) ---------- */
FIGS.recall = (el) => {
  const S = D.summary, n = S.bm25.n, m = [['bm25', 'BM25'], ['vector', 'Embeddings'], ['hybrid', 'Hybrid (RRF)'], ['hybrid+rerank', 'Hybrid + rerank']];
  el.innerHTML = `<div class="cmp" style="gap:22px">${m.map(([k, l]) => `<div class="row"><div class="lab">${l}</div><div class="br">
    <div class="bar a" data-w="${100 * S[k]['recall@1']}" style="width:0">first: ${Math.round(S[k]['recall@1'] * n)} of ${n}</div>
    <div class="bar a" data-w="${100 * S[k]['recall@5']}" style="width:0;opacity:.6">top 5: ${Math.round(S[k]['recall@5'] * n)} of ${n}</div></div></div>`).join('')}</div>
    <p class="mini" style="margin-top:14px">recall@k = share of questions whose right clause is in the top k. MRR: ${m.map(([k, l]) => `${l} ${S[k].mrr.toFixed(2)}`).join(' · ')}.</p>`;
  const bars = [...el.querySelectorAll('.bar')];
  return { step(k) { bars.forEach((b, i) => { b.style.width = (i % 2 === 0 || k >= 1 ? b.dataset.w : 0) + '%'; }); } };
};

/* ---------- Kavita's words vs the rule's words (logs/retrieval_eval.json → shakti) ---------- */
FIGS.gap = (el) => {
  const Z = D.shakti, ruleWords = ['food', 'food-grade', 'certificate', 'supplier', 'gasket', 'grade', 'valid'];
  el.innerHTML = `<div class="ba" style="position:relative;left:0;right:0;top:0;gap:14px"><div class="card"><span class="tag nt">Kavita’s words, as BM25 sees them</span><div style="display:flex;flex-wrap:wrap;gap:7px;margin-top:6px">${Z.tokens.map((t) => `<span style="font:500 19px var(--mono);padding:5px 10px;border-radius:999px;background:${ruleWords.includes(t) ? 'var(--gold-soft)' : '#fff'};color:${ruleWords.includes(t) ? 'var(--gold)' : 'var(--ink-2)'}">${esc(t)}</span>`).join('')}</div></div>
    <div class="card af"><span class="tag af">The words of §6.2</span><div style="font-size:18px">parts that come into contact with <b>food</b> (<b>gaskets</b>, lids, body blanks …) may be bought only from a <b>supplier</b> holding a valid <b>food-grade certificate</b> on file in Bahi</div></div></div>
    <table class="t step-tab" style="font-size:19px;margin-top:16px"><thead><tr><th>after hybrid + rerank</th><th>reranker score</th><th>kept? (cut at 0)</th></tr></thead><tbody>${Z.rerank.slice(0, 5).map((r) => `<tr style="${r.id === C62 ? 'background:var(--after-soft)' : ''}"><td class="n">${r.id}</td><td class="n">${r.rerank.toFixed(2)}</td><td>${r.rerank >= 0 ? 'yes' : '<span class="b">no</span>'}</td></tr>`).join('')}</tbody></table>`;
  const t = el.querySelector('.step-tab');
  return { step(k) { t.style.opacity = k >= 2 ? 1 : 0.1; } };
};

/* ---------- a recorded trace of Ask Rasoi's searches (logs/story.json → knowledge; logs/finding62.json → agent) ---------- */
const traceFig = (key) => (el) => {
  const K = D[key]; if (!K) { el.textContent = 'not yet measured'; return { step() {} }; }
  const T = K.trace;
  const big = T.length > 5;
  el.innerHTML = `<div id="tr-list" style="display:flex;flex-direction:column;gap:${big ? 4 : 8}px"></div><div class="card" id="tr-ans" style="margin-top:10px;font-size:${big ? 15 : 17}px;line-height:1.38;padding:14px 18px"></div>`;
  const list = el.querySelector('#tr-list'), ans = el.querySelector('#tr-ans');
  const ctl = ctlRow(el, `<label>step</label><input type="range" min="0" max="${T.length + 1}" value="${T.length + 1}"><output></output>`);
  const inp = ctl.querySelector('input'), o = ctl.querySelector('output');
  const draw = () => {
    const s = +inp.value;
    list.innerHTML = T.map((t, i) => `<div style="display:grid;grid-template-columns:36px 1fr;gap:8px;opacity:${i < s ? 1 : 0.1};transition:opacity .3s"><span class="chip ${t.found.some((f) => f[0] === C62) ? 'p' : 'h'}" style="min-width:30px">${i + 1}</span><div style="font-size:${big ? 14.5 : 17}px;line-height:1.3"><span class="mono" style="font-size:${big ? 14 : 16}px">search_policy(“${esc(t.q)}”)</span><br><span style="color:var(--ink-3)">→ ${t.found.length ? t.found.filter((f, j) => j < (big ? 3 : 4) || f[0] === C62).map((f) => `<span style="${f[0] === C62 ? 'color:var(--after);font-weight:600' : ''}">${f[0]} (${f[1]})</span>`).join(', ') : 'nothing above the cut: “not in the documents”'}</span></div></div>`).join('');
    ans.style.opacity = s > T.length ? 1 : 0.1;
    ans.innerHTML = `<div class="who">Ask Rasoi's reply · ${K.llm.calls} model calls, ${fmtN(K.llm.tokens_in)} tokens in, ${rup(K.llm.cost_inr, 2)}</div>${hiCite(K.answer.replace(/\n\s*\n/g, '\n'))}`;
    o.textContent = s > T.length ? 'reply' : s === 0 ? 'question' : `search ${s}`;
  };
  inp.addEventListener('input', draw);
  return { step(k, instant) { draw(); } };
};
FIGS.trace0 = traceFig('k0');
FIGS.trace1 = traceFig('k1');

/* ---------- writing the search query (logs/story.json → rewrite_v0; logs/finding62.json → rewrite) ---------- */
FIGS.rewrite = (el) => {
  const R = D.rewrite; if (!R) { el.textContent = 'not yet measured'; return { step() {} }; }
  const pq = R.per_query || {};
  el.innerHTML = `<div class="card bf" data-s="0" style="font-size:18px"><span class="tag bf">One query, no context</span><div class="mono" style="font-size:16px">${esc(D.rewrite_v0)}</div><div style="color:var(--ink-2);font-size:16px;margin-top:4px">→ nothing above the cut</div></div>
    <div class="card bf" data-s="1" style="font-size:18px;margin-top:10px"><span class="tag bf">One long query, with the context line</span><div class="mono" style="font-size:16px">${esc(D.rewrite_one.query)}</div><div style="color:var(--ink-2);font-size:16px;margin-top:4px">→ §6.2 ranked first, but scored ${D.rewrite_one.top62.toFixed(2)}: below the cut at 0, so dropped</div></div>
    <div class="card af" data-s="2" style="font-size:18px;margin-top:10px"><span class="tag af">One short query per rule, with the context line</span>${R.queries.map((q) => `<div style="margin-top:4px"><span class="mono" style="font-size:16px">${esc(q)}</span><span style="color:var(--ink-3);font-size:15px"> → ${(pq[q] || []).map((f) => `<span style="${f[0] === C62 ? 'color:var(--after);font-weight:600' : ''}">${f[0]}</span>`).join(', ') || 'nothing'}</span></div>`).join('')}</div>`;
  const cards = [...el.querySelectorAll('[data-s]')];
  return { step(k) { cards.forEach((c) => { c.style.opacity = +c.dataset.s <= k ? 1 : 0.1; }); } };
};

/* ---------- RAG end to end on Kavita's question (logs/finding62.json → rewrite) ---------- */
FIGS.ragstep = (el) => {
  const R = D.rewrite; if (!R) { el.textContent = 'not yet measured'; return { step() {} }; }
  const stages = [
    ['1 · Question', `<div class="msg u" style="font-size:20px;max-width:100%">Can I buy the gaskets from Shakti Seals? They quote ₹10.40</div>`],
    ['2 · Search queries', R.queries.map((q) => `<div class="mono" style="font-size:16px">${esc(q)}</div>`).join('') + `<div class="mini">written by the model, ${rup(R.rw_cost, 3)}</div>`],
    ['3 · Top clauses', R.clauses.map((c) => `<div style="font-size:16px"><span class="cite">${c.cite}</span> <span class="mono" style="font-size:14px;color:var(--ink-3)">score ${c.score}</span> ${esc(c.text.replace(/\*\*/g, '').slice(0, 110))}…</div>`).join('')],
    ['4 · The prompt', `<div class="json" style="white-space:pre-wrap;font-size:12.5px;line-height:1.32;padding:10px 14px;background:#fff">${esc(R.prompt.replace(/\*\*/g, ''))}</div><div class="mini" style="margin-top:6px">${fmtN(R.prompt_tokens)} tokens for this message, ${fmtN(R.tokens_in)} with the answer instructions (the whole corpus: ${fmtN(D.full_shakti.tokens_in)})</div>`],
    ['5 · The answer', `<div class="msg ag" style="font-size:19px;max-width:100%">${hiCite(R.answer)}</div><div class="mini">${R.tokens_out} tokens out, ${R.seconds.toFixed(1)} s, ${rup(R.cost_inr, 3)}</div>`],
    ['6 · Check the citations', `<div class="json" style="font-size:16px">cites      ${esc(JSON.stringify(R.check.cites))}\ninvented   ${esc(JSON.stringify(R.check.invented))}\nungrounded ${esc(JSON.stringify(R.check.ungrounded))}</div>`]];
  el.innerHTML = `<div style="display:flex;gap:6px;margin-bottom:12px" id="rs-tabs">${stages.map((s, i) => `<button data-i="${i}" style="flex:1;font:500 14px var(--font);padding:9px 4px;border-radius:999px;border:1px solid var(--pill-line);background:var(--glass);cursor:pointer">${s[0]}</button>`).join('')}</div><div class="card" id="rs-body" style="min-height:420px;font-size:18px;padding:16px 20px"></div>`;
  const tabs = [...el.querySelectorAll('#rs-tabs button')], body = el.querySelector('#rs-body');
  const set = (i) => { body.innerHTML = stages[i][1]; tabs.forEach((t, j) => { t.style.background = j === i ? 'var(--ink)' : j < i ? 'var(--after-soft)' : 'var(--glass)'; t.style.color = j === i ? '#fff' : 'var(--ink)'; }); };
  tabs.forEach((t) => t.addEventListener('click', (e) => { e.stopPropagation(); set(+t.dataset.i); }));
  el.classList.add('ctl-host');
  return { step(k) { set(Math.min(k, stages.length - 1)); } };
};

/* ---------- the citation checker on a real answer and a hand-edited copy (logs/story.json → checker) ---------- */
FIGS.checker = (el) => {
  const R = D.rewrite, real = R ? R.check : D.checker.real;
  const ed = R ? null : D.checker.edited_to_6_9;
  const edited = R ? { cites: real.cites.map((c) => c === C62 ? 'POL-PUR-001 §6.9' : c), invented: real.cites.includes(C62) ? ['POL-PUR-001 §6.9'] : [], ungrounded: [] } : ed;
  const box = (t, c, cls) => `<div class="card ${cls}" style="font-size:18px"><span class="tag ${cls}">${t}</span><div class="json" style="font-size:15.5px;background:#fff">cites      ${esc(JSON.stringify(c.cites))}\ninvented   ${esc(JSON.stringify(c.invented))}\nungrounded ${esc(JSON.stringify(c.ungrounded))}</div></div>`;
  el.innerHTML = box('The real answer from our run', real, 'af') + `<div style="height:12px"></div>` + box('The same answer, §6.2 changed to §6.9 by hand', edited, 'bf');
  const cs = [...el.querySelectorAll('.card')];
  return { step(k) { cs.forEach((c, i) => { c.style.opacity = i <= k ? 1 : 0.1; }); } };
};

/* ---------- can a score say "not in the documents"? (logs/retrieval_eval.json → tau) ---------- */
FIGS.tau = (el) => {
  const P = window.Plates, W = 820, H = 300, T = D.tau.per_question.filter((r) => r.top !== null);
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const lo = -3, hi = 10, sx = (v) => 40 + (v - lo) / (hi - lo) * (W - 80);
  P.svgEl('line', { x1: 40, x2: W - 40, y1: 230, y2: 230, style: 'stroke:var(--ink-3)' }, svg);
  for (let v = lo; v <= hi; v += 1) P.txt(svg, sx(v), 254, v, 'font:14px var(--mono);fill:var(--ink-3)', 'middle');
  P.svgEl('line', { x1: sx(0), x2: sx(0), y1: 30, y2: 236, style: 'stroke:var(--gold);stroke-width:2;stroke-dasharray:5 4' }, svg);
  P.txt(svg, sx(0) + 6, 34, 'cut at 0 (even odds)', 'font:15px var(--font);fill:var(--gold)');
  P.txt(svg, W / 2, 284, "best reranker score for each of the 40 questions", 'font:16px var(--font);fill:var(--ink-2)', 'middle');
  const g1 = P.svgEl('g', {}, svg), g2 = P.svgEl('g', {}, svg);
  T.forEach((r, i) => { const ans = !['perm', 'trap'].includes(r.kind); P.svgEl('circle', { cx: sx(r.top), cy: ans ? 110 + (i % 5) * 9 : 190 + (i % 3) * 9, r: 6, style: `fill:${ans ? 'var(--after)' : 'var(--before)'};opacity:.8` }, ans ? g1 : g2); });
  P.txt(g1, 40, 92, 'answerable (33)', 'font:500 16px var(--font);fill:var(--after)');
  P.txt(g2, 40, 180, 'not in any document (7)', 'font:500 16px var(--font);fill:var(--before)');
  return { step(k) { g2.style.opacity = k >= 1 ? 1 : 0.1; } };
};

/* ---------- the wiki as linked pages (bahi/wiki/manifest.json, pages/*.md; logs/v2_wiki_compile.json) ---------- */
FIGS.wikigraph = (el) => {
  const P = window.Plates, W = 900, H = 600, pg = D.wiki.pages, slugs = Object.keys(pg);
  const open = slugs.filter((s) => pg[s].audience !== 'hr only'), hr = slugs.filter((s) => pg[s].audience === 'hr only');
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const pos = {}, cx = 330, cy = 300, R = 250;
  open.forEach((s, i) => { const a = -Math.PI / 2 + i * 2 * Math.PI / open.length; pos[s] = [cx + R * Math.cos(a), cy + R * Math.sin(a)]; });
  hr.forEach((s, i) => { pos[s] = [W - 90, 60 + i * 60]; });
  const edges = P.svgEl('g', {}, svg), E = [];
  slugs.forEach((s) => pg[s].links.forEach((t) => { if (pos[t]) E.push([s, t, P.svgEl('line', { x1: pos[s][0], y1: pos[s][1], x2: pos[t][0], y2: pos[t][1], style: 'stroke:var(--rule);stroke-width:1.5' }, edges)]); }));
  const info = document.createElement('div'); info.className = 'card'; info.style.cssText = 'position:absolute;left:620px;top:380px;width:280px;font-size:17px'; el.appendChild(info);
  const nodes = slugs.map((s) => { const [x, y] = pos[s], r = 9 + Math.sqrt(D.wiki.page_tokens[s] || 400) / 3.4;
    const c = P.svgEl('circle', { cx: x, cy: y, r, style: `fill:${pg[s].audience === 'hr only' ? 'var(--before-soft)' : 'var(--after-soft)'};stroke:${pg[s].audience === 'hr only' ? 'var(--before)' : 'var(--after)'};stroke-width:2;cursor:pointer` }, svg);
    P.txt(svg, x, y + r + 15, s.split('-').slice(0, 2).join('-'), 'font:14px var(--mono);fill:var(--ink-2);pointer-events:none', 'middle');
    c.addEventListener('click', (e) => { e.stopPropagation(); sel(s); }); return { s, c }; });
  const sel = (s) => { const p = pg[s]; E.forEach(([a, b, l]) => { const o = a === s || b === s; l.style.stroke = o ? 'var(--after)' : 'var(--rule)'; l.style.strokeWidth = o ? 3 : 1.5; });
    nodes.forEach((n) => { n.c.style.strokeWidth = n.s === s ? 4 : 2; });
    info.innerHTML = `<b>${esc(p.title)}</b><div class="mono" style="font-size:14px;color:var(--ink-3)">[[${s}]] · ${esc(p.audience)}</div><div>${p.n_sources} source clauses · ${fmtN(D.wiki.page_tokens[s] || 0)} tokens · ${p.links.length} links</div>`; };
  return { step(k) { sel(k >= 1 ? hr[0] : 'food-grade-compliance'); } };
};

/* ---------- the wiki on Kavita's question (logs/finding62.json → wiki) ---------- */
FIGS.wikishakti = (el) => {
  const W = D.wiki_shakti; if (!W) { el.textContent = 'not yet measured'; return { step() {} }; }
  el.innerHTML = `<div class="card" data-s="0" style="font-size:18px"><span class="tag nt">Step 1 · read the index (${fmtN(D.wiki.index_tokens)} tokens), pick pages</span><div>${W.pages.map((p) => `<span class="mono" style="font-size:17px;margin-right:12px;${p === 'food-grade-compliance' ? 'color:var(--after);font-weight:600' : ''}">[[${p}]]</span>`).join('')}</div></div>
    <div class="card af" data-s="1" style="font-size:18px;margin-top:12px"><span class="tag af">Step 2 · answer from those pages · ${fmtN(W.tokens_in)} tokens in over two calls</span><div>${hiCite(W.answer)}</div></div>`;
  const c = [...el.querySelectorAll('[data-s]')];
  return { step(k) { c.forEach((x) => { x.style.opacity = +x.dataset.s <= k ? 1 : 0.1; }); } };
};

/* ---------- freshness: drag the date (amendment front-matter in bahi/docs) ---------- */
FIGS.fresh = (el) => {
  const P = window.Plates, W = 820, H = 250;
  const d0 = new Date('2026-04-01'), d1 = new Date('2027-01-31'), day = 864e5, span = (d1 - d0) / day;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const sx = (d) => 40 + (new Date(d) - d0) / day / span * (W - 80);
  P.svgEl('line', { x1: 40, x2: W - 40, y1: 125, y2: 125, style: 'stroke:var(--ink-3);stroke-width:2' }, svg);
  [['2026-04-01', 'Policies v4.1, v2.3', 'var(--ink-2)', -1], ['2026-09-01', 'AMD-SUP-2026-02', 'var(--gold)', 1], ['2026-10-26', 'today', 'var(--after)', -1], ['2026-12-01', 'AMD-PUR-2026-03', 'var(--gold)', 1]].forEach(([d, a, c, s]) => {
    const x = sx(d); P.svgEl('circle', { cx: x, cy: 125, r: 7, style: `fill:${c}` }, svg);
    P.txt(svg, x, 125 + s * 40, a, `font:500 16px var(--font);fill:${c}`, x < 120 ? 'start' : x > W - 120 ? 'end' : 'middle');
    P.txt(svg, x, 125 + s * 40 + (s > 0 ? 20 : -20), d, 'font:14px var(--mono);fill:var(--ink-3)', x < 120 ? 'start' : x > W - 120 ? 'end' : 'middle'); });
  const cur = P.svgEl('line', { y1: 40, y2: 210, style: 'stroke:var(--before);stroke-width:2.5' }, svg);
  el.insertAdjacentHTML('beforeend', `<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px" id="fr-out"></div>`);
  const ctl = ctlRow(el, `<label>as of</label><input type="range" min="0" max="${span}" value="${(new Date('2026-10-26') - d0) / day}"><output></output>`);
  const inp = ctl.querySelector('input'), out = ctl.querySelector('output'), box = el.querySelector('#fr-out');
  const set = () => {
    const iso = new Date(d0.getTime() + +inp.value * day).toISOString().slice(0, 10);
    cur.setAttribute('x1', sx(iso)); cur.setAttribute('x2', sx(iso)); out.textContent = iso;
    const sup = iso >= '2026-09-01', pur = iso >= '2026-12-01';
    const card = (t, a, b) => `<div class="card" style="font-size:17px"><h3 style="font-size:20px">${t}</h3><div><span class="cite">${a[0]}</span> ${a[1]}</div><div style="margin-top:6px;color:var(--ink-3)"><span class="mono" style="font-size:15px">${b[0]}</span> ${b[1]}</div></div>`;
    box.innerHTML = card('Certificate age', sup ? ['AMD-SUP-2026-02 §1.1', 'answers: issued within 12 months, 60 days left'] : ['POL-SUP-003 §4.4', 'answers: issued within 24 months, not expired'], sup ? ['POL-SUP-003 §4.4', 'replaced: removed from the index'] : ['AMD-SUP-2026-02 §1.1', 'kept, labelled “not yet in force”'])
      + card('Direct-order limit', pur ? ['AMD-PUR-2026-03 §1.1', 'answers: ₹25,000'] : ['POL-PUR-001 §3.3', 'answers: ₹50,000'], pur ? ['POL-PUR-001 §3.3', 'replaced: removed from the index'] : ['AMD-PUR-2026-03 §1.1', 'kept, labelled “applies from 2026-12-01”']);
  };
  inp.addEventListener('input', set);
  return { step(k) { if (k === 0) inp.value = (new Date('2026-10-26') - d0) / day; set(); } };
};

/* ---------- the 40-question results (logs/answers_eval.json → summary) ---------- */
FIGS.results = (el) => {
  const E = D.eval; if (!E) { el.textContent = 'not yet measured'; return { step() {} }; }
  const sys = [['closed', 'Model alone'], ['full', 'Paste Kavita’s documents'], ['company', 'Paste the whole company’s'], ['rag', 'RAG'], ['wiki', 'LLM wiki']];
  const pct = (x) => x === null || x === undefined ? '–' : Math.round(100 * x) + '%';
  el.innerHTML = `<table class="t" style="font-size:21px"><thead><tr><th>System</th><th>correct of 40</th><th>right clause in context (33)</th><th>right clause cited (33)</th><th>tokens in / answer</th><th>seconds</th><th>₹ for 40</th><th>invented citations</th></tr></thead><tbody>
    ${sys.map(([s, l], i) => { const a = E[s].all; return `<tr data-i="${i}" style="${s === 'rag' ? 'background:var(--after-soft)' : ''}"><td><b>${l}</b></td><td class="n">${a.correct}</td><td class="n">${s === 'closed' ? '–' : Math.round(a.context_recall * 33)}</td><td class="n">${a.gold_cited}</td><td class="n">${fmtN(a.tokens_in_mean)}</td><td class="n">${a.seconds_mean.toFixed(1)}</td><td class="n">${rup(E[s].cost_inr_40)}</td><td class="n">${a.invented_cites}</td></tr>`; }).join('')}</tbody></table>
    <table class="t" style="font-size:18px;margin-top:18px" id="rs-kind"><thead><tr><th>by kind (correct / asked)</th>${['policy', 'manual', 'fresh', 'perm', 'trap'].map((k) => `<th>${k}</th>`).join('')}</tr></thead><tbody>
    ${sys.map(([s, l]) => `<tr><td>${l}</td>${['policy', 'manual', 'fresh', 'perm', 'trap'].map((k) => `<td class="n">${E[s].by_kind[k][0]} / ${E[s].by_kind[k][1]}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  const tr = [...el.querySelectorAll('tr[data-i]')], kd = el.querySelector('#rs-kind');
  return { step(k) { tr.forEach((t, i) => { t.style.opacity = i <= k ? 1 : 0.1; }); kd.style.opacity = k >= 5 ? 1 : 0.1; } };
};

/* ---------- did the context line hurt anything? (logs/finding62.json → check6) ---------- */
FIGS.check6 = (el) => {
  const R = D.check6; if (!R) { el.textContent = 'not yet measured'; return { step() {} }; }
  const ok = (r) => r.ok ? '<span class="chip p">right</span>' : '<span class="chip f">wrong</span>';
  el.innerHTML = `<table class="t" style="font-size:18px"><thead><tr><th>question</th><th>before: no context line</th><th>after: with it</th><th>searches after</th><th>₹ before → after</th></tr></thead><tbody>
    ${R.map((r) => `<tr><td><b>${r.id}</b> ${esc(r.q.slice(0, 52))}${r.q.length > 52 ? '…' : ''}</td><td>${ok(r.v0)}</td><td>${ok(r.v1)}</td><td class="n">${r.v1.searches.length}</td><td class="n">${rup(r.v0.cost_inr, 3)} → ${rup(r.v1.cost_inr, 3)}</td></tr>`).join('')}</tbody></table>`;
  return { step() {} };
};

/* ---------- the architecture, Memory lit (figures/ask_rasoi_architecture_wide.png, the lead's master) ---------- */
FIGS.archlit = (el) => {
  el.innerHTML = `<div style="position:relative;width:100%;aspect-ratio:2752/1536">
    <img src="../../figures/ask_rasoi_architecture_wide.png" alt="Ask Rasoi architecture" style="width:100%;height:100%;display:block;border-radius:18px">
    <svg class="lit" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;transition:opacity .6s"><path fill-rule="evenodd" fill="rgba(255,255,255,.62)" d="M0 0H100V100H0Z M59.2 33.6H78.8V44.6H59.2Z M66.1 64.8H75.7V74H66.1Z"/></svg>
    <div style="position:absolute;left:59.2%;top:33.6%;width:19.6%;height:11%;border:4px solid var(--after);border-radius:18px;box-shadow:0 0 0 8px rgba(11,87,208,.14)"></div>
    <div style="position:absolute;left:66.1%;top:64.8%;width:9.6%;height:9.2%;border:3px solid var(--after);border-radius:12px"></div></div>`;
  const lit = el.querySelector('.lit');
  return { step(k) { lit.style.opacity = k >= 1 ? 1 : 0; } };
};
})();
