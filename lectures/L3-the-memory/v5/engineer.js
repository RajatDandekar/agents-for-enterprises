/* L3 v5 · engineer section: metrics on the running example, the ablation grid read one knob at a time, the selection.
   Every number comes from window.L3V5.engineer (engineer_data.js, written by experiments/v5_engineer_slices.py from
   experiments/logs). Figures are FIGS.engineer_<name>(el) → { step(k) }, k = the .step elements shown on the slide. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const D = () => (window.L3V5 && window.L3V5.engineer) || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pct = (v, d = 1) => (v == null ? '–' : (100 * v).toFixed(d) + '%');
const r3 = (v) => (v == null ? '–' : (+v).toFixed(3));
const ms = (s) => (s == null ? '–' : s < 1 ? (s * 1000 < 10 ? (s * 1000).toFixed(1) : Math.round(s * 1000)) + ' ms' : s.toFixed(1) + ' s');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const ms1 = (s) => (s == null ? '–' : (s * 1000).toFixed(1) + ' ms');
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('engineer-off', +x.dataset.k > k));
const need = (el, w) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(engineer data)</span><div>${esc(w)}</div></div>`; return { step() {} }; };
const get = (path) => { let v = D(); for (const k of path.split('.')) v = v == null ? v : v[k]; return v; };
const md = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').split(/\n+/).filter((x) => x.trim()).map((p) => `<p>${p}</p>`).join('');
const bar = (label, v, { max = 1, ch = false, over = false, extra = '', f = r3 } = {}) =>
  `<div class="engineer-br${ch ? ' ch' : ''}${over ? ' over' : ''}"><span class="l">${label}</span><span class="t"><i style="width:${Math.max(0.8, 100 * (v || 0) / max)}%"></i></span><span class="v">${f(v)}</span><span class="e">${extra}</span></div>`;

/* ---------- Emma's question in the whole dump: the top 10, gold marked, then recall@5, RR, coverage ---------- */
FIGS.engineer_top = (el) => {
  const q = get('per_question.' + (el.dataset.q || 'Q-EMMA')); if (!q) return need(el, 'per_question');
  const rows = q.top10.map((t, i) => `${i === 5 ? '<div class="engineer-cut"><span>top 5</span></div>' : ''}<div class="engineer-row${t.gold ? ' gold' : ''}" data-r="${i + 1}"><span class="r">${i + 1}</span><span class="c">${esc(t.cite)}</span><span class="g">gold</span></div>`).join('');
  el.innerHTML = `<div class="engineer-top" style="inset:0"><div class="engineer-list">${rows}</div>
    <div class="engineer-side">
      <div class="engineer-m engineer-k" data-k="2"><span class="h">Recall@5 for this question</span><span class="v">${q['hit@5']}</span><br>A gold passage is in the top 5 (rank ${q.rank}). If none were, it would be 0.</div>
      <div class="engineer-m engineer-k" data-k="3"><span class="h">Reciprocal rank</span><span class="v">1 / ${q.rank} = ${(+q.rr).toFixed(2)}</span><br>One over the rank of the first gold passage: at rank 2 it would be 0.50, at rank 4 0.25.</div>
      <div class="engineer-m warn engineer-k" data-k="4"><span class="h">But only ${Math.round(q['cov@5'] * q.n_gold)} of ${q.n_gold} gold passages</span>Both from the Brightcell quotation. The §6.2 clause (p.2) is not in the top 10; rank 10 is the policy’s own FAQ (p.3), which restates it but is not on the gold list. Recall@5 is generous.</div>
    </div></div>`;
  const list = el.querySelector('.engineer-list');
  return { step(k) {
    reveal(el, k);
    list.classList.toggle('marks', k >= 1);
    list.querySelectorAll('.engineer-row').forEach((r) => r.classList.toggle('engineer-dim', +r.dataset.r > 5 && k < 4));
  } };
};

/* ---------- from one question to 205: four real questions, then the rank of the first gold passage for all ---------- */
FIGS.engineer_avg = (el) => {
  const P = get('per_question'), H = get('rank_hist'), C = get('check'); if (!P || !H) return need(el, 'rank_hist');
  const qs = [P['Q-EMMA'], P['Q-0412'], P.rank_mid_example, P.miss_example];
  const W = 600, Hh = 400, m = { l: 40, r: 10, t: 58, b: 52 };
  const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'none'];
  const mx = Math.max(...keys.map((k) => H[k]));
  const bw = (W - m.l - m.r) / keys.length;
  const ys = (v) => Hh - m.b - (v / mx) * (Hh - m.t - m.b);
  const bars = keys.map((k, i) => { const x = m.l + i * bw + 4, y = ys(H[k]); const top5 = k !== 'none' && +k <= 5;
    return `<rect class="hb${top5 ? ' t5' : ''}" x="${x}" y="${y}" width="${bw - 8}" height="${Hh - m.b - y}" rx="5" fill="${top5 ? '#9fbff0' : '#d6dbe3'}"/>
      <text x="${x + (bw - 8) / 2}" y="${y - 7}" text-anchor="middle" class="lab">${H[k]}</text>
      <text x="${x + (bw - 8) / 2}" y="${Hh - m.b + 22}" text-anchor="middle">${k}</text>`; }).join('');
  const n5 = keys.slice(0, 5).reduce((s, k) => s + H[k], 0), n = keys.reduce((s, k) => s + H[k], 0);
  el.innerHTML = `<div class="engineer-avg" style="inset:0">
    <div><table class="engineer-qt"><tr><th>Question</th><th class="n">First gold at</th><th class="n">Recall@5</th><th class="n">1 / rank</th></tr>
      ${qs.map((q, i) => `<tr class="engineer-k" data-k="${i < 2 ? 0 : 1}"><td>${esc(q.question)}</td><td class="n">${q.rank ?? 'not in top 10'}</td><td class="n">${q['hit@5']}</td><td class="n">${q.rank ? (1 / q.rank).toFixed(2) : '0'}</td></tr>`).join('')}
      <tr class="mean engineer-k" data-k="3"><td>Mean over all ${n} scored questions</td><td></td><td class="n">${r3(C['recall@5_from_records'])}</td><td class="n">${r3(C['mrr_from_records'])}</td></tr></table>
      <p class="engineer-note engineer-k" data-k="1" style="margin-top:12px">The other ${224 - n} of the 224 have no passage to find (“not in the documents”, or a refusal). They are scored on the answer only.</p></div>
    <div class="engineer-k" data-k="2"><svg class="engineer-hist" width="${W}" height="${Hh}">
      <text x="${m.l}" y="16">Rank of the first gold passage, ${n} questions</text>${bars}
      <text x="${(m.l + W - m.r) / 2}" y="${Hh - 8}" text-anchor="middle">rank (none = no gold passage in the top 10)</text></svg>
      <p class="engineer-formula">Recall@5 = <span class="a">${n5} of ${n}</span> in the blue bars = <span class="a">${r3(n5 / n)}</span></p>
      <p class="engineer-formula engineer-k" data-k="3" style="margin-top:0">MRR = the mean of 1 / rank = <span class="a">${r3(C['mrr_from_records'])}</span></p></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- search time of the 224 questions: the histogram, then p50 and p95 ---------- */
FIGS.engineer_lat = (el) => {
  const L = get('latency'); if (!L) return need(el, 'latency');
  const W = el.clientWidth || 860, H = el.clientHeight || 520, m = { l: 56, r: 20, t: 46, b: 58 };
  const bins = L.hist_ms.filter(([b]) => b >= 33 && b <= 55.5), bw = 0.5;
  const x0 = bins[0][0], x1 = bins[bins.length - 1][0] + bw;
  const xs = (v) => m.l + ((v - x0) / (x1 - x0)) * (W - m.l - m.r);
  const mx = Math.max(...bins.map((b) => b[1]));
  const ys = (v) => H - m.b - (v / mx) * (H - m.t - m.b);
  const p50 = L.p50_s * 1000, p95 = L.p95_s * 1000;
  const bars = bins.filter(([, c]) => c).map(([b, c]) => `<rect x="${xs(b) + 1}" y="${ys(c)}" width="${xs(b + bw) - xs(b) - 2}" height="${H - m.b - ys(c)}" rx="3" fill="${b >= p95 - 1e-6 ? '#f3b896' : '#9fbff0'}" class="b"/>`).join('');
  const ticks = bins.filter(([b]) => b % 2 === 0).map(([b]) => `<text x="${xs(b)}" y="${H - m.b + 22}" text-anchor="middle">${b}</text>`).join('');
  const yt = [5, 10, 15, 20].map((v) => `<line x1="${m.l}" x2="${W - m.r}" y1="${ys(v)}" y2="${ys(v)}" stroke="#e1e5ea"/><text x="${m.l - 8}" y="${ys(v) + 5}" text-anchor="end">${v}</text>`).join('');
  el.innerHTML = `<svg class="engineer-lat" width="${W}" height="${H}">${yt}${bars}${ticks}
    <text x="${(m.l + W - m.r) / 2}" y="${H - 10}" text-anchor="middle">search time per question, ms (0.5 ms bins)</text>
    <text x="16" y="${(m.t + H - m.b) / 2}" transform="rotate(-90 16 ${(m.t + H - m.b) / 2})" text-anchor="middle">questions</text>
    <g data-k="1" class="engineer-k"><line class="p50" x1="${xs(p50)}" x2="${xs(p50)}" y1="${m.t - 10}" y2="${H - m.b}"/><text class="t50" x="${xs(p50) - 8}" y="${m.t - 16}" text-anchor="end">p50 = ${p50.toFixed(1)} ms</text></g>
    <g data-k="2" class="engineer-k"><line class="p95" x1="${xs(p95)}" x2="${xs(p95)}" y1="${m.t - 10}" y2="${H - m.b}"/><text class="t95" x="${xs(p95) + 8}" y="${m.t - 16}">p95 = ${p95.toFixed(1)} ms</text></g></svg>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- cost: tokens times the price, for Emma's answer, then the average ---------- */
FIGS.engineer_cost = (el) => {
  const q = get('per_question.Q-EMMA'), A = get('scorecard.answers'), S = get('answer_spend'); if (!q || !A) return need(el, 'cost');
  const pin = 0.825, pout = 4.125;
  const cin = (q.tokens_in * pin) / 1e6, cout = (q.tokens_out * pout) / 1e6;
  el.innerHTML = `<div class="engineer-cost" style="inset:0">
    <div class="engineer-eq"><span>${fmt(q.tokens_in)} tokens in<small>Emma’s question, the prompt and 10 passages</small></span><span class="o">×</span><span>$${pin} per million</span><span class="o">=</span><span class="res">$${cin.toFixed(5)}</span></div>
    <div class="engineer-eq engineer-k" data-k="1"><span>${fmt(q.tokens_out)} tokens out<small>the answer, with its thinking tokens</small></span><span class="o">×</span><span>$${pout} per million</span><span class="o">=</span><span class="res">$${cout.toFixed(5)}</span></div>
    <div class="engineer-eq tot engineer-k" data-k="1"><span><b>Emma’s question</b></span><span></span><span></span><span class="o">=</span><span class="res">$${(cin + cout).toFixed(4)}</span></div>
    <div class="engineer-eq tot engineer-k" data-k="2"><span><b>Mean of all 224</b><small>${fmt(Math.round(A.tokens_in_per_q))} in, ${fmt(Math.round(A.tokens_out_per_q))} out on average</small></span><span></span><span></span><span class="o">=</span><span class="res">$${A.cost_per_q_usd.toFixed(4)}</span></div>
  </div>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- three checks on one real answer ---------- */
FIGS.engineer_judge = (el) => {
  const q = get('per_question.Q-EMMA'), A = get('scorecard.answers'); if (!q) return need(el, 'Q-EMMA answer');
  const miss = new Set(q.fact.missing || []);
  el.innerHTML = `<div class="engineer-judge" style="inset:0">
    <div class="engineer-ans"><span class="who">The answer RAG gave Emma (150-word cap, before the race)</span>${md(q.answer)}</div>
    <div class="engineer-checks">
      <div class="engineer-chk engineer-k" data-k="1"><span class="h">1 · Exact facts <span class="bad">${q.must_contain.length - miss.size} of ${q.must_contain.length}: not correct</span></span>Does the answer contain every string the golden set says it must?
        <div class="engineer-pills">${q.must_contain.map((s) => `<span class="${miss.has(s) ? 'x' : ''}">${esc(s)}</span>`).join('')}</div></div>
      <div class="engineer-chk engineer-k" data-k="2"><span class="h">2 · The judge <span class="bad">not correct</span></span>A second model call (gemini-3.8-flash) compares it with the reference answer: “${esc(q.judge.reason)}”</div>
      <div class="engineer-chk engineer-k" data-k="3"><span class="h">3 · Citations <span class="ok">correct</span></span>Each cited passage really holds the fact it is cited for. ${q.citation.n_cited} passages cited.</div>
      <div class="engineer-chk engineer-k" data-k="4" style="background:var(--g1)"><span class="h">Over all 224 answers</span>Judge correct <b>${pct(A.answer_correct)}</b> · exact facts <b>${pct(A.fact_correct)}</b> · citations correct <b>${pct(A.citation_correct)}</b>. Judge and exact-fact check agree on ${pct(get('scorecard.judge_vs_fact.agree'))} of answers.</div>
    </div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- the grid of knobs, multiplied out ---------- */
FIGS.engineer_knobs = (el) => {
  const S = get('scale'); if (!S) return need(el, 'scale');
  const kr = (k, lab, chips, x) => `<div class="engineer-kr engineer-k" data-k="${k}"><span class="kl">${lab}</span><span class="engineer-chips">${chips.map((c) => `<span>${c}</span>`).join('')}</span><span class="x">${x}</span></div>`;
  el.innerHTML = `<div class="engineer-knobs" style="inset:0">
    ${kr(0, 'Parser', ['plain', 'structured'], '2')}
    ${kr(0, 'Chunker', ['fixed', 'recursive', 'structure-aware'], '× 3')}
    ${kr(0, 'Chunk size', ['200', '400', '800', '1200 tokens'], '× 4')}
    ${kr(0, 'Overlap', ['0%', '15%'], '× 2')}
    <div class="engineer-tot engineer-k" data-k="0"><span></span><span>indexes to build (chunk, embed with 5 models, BM25)</span><span class="v">= ${S.n_chunkings}</span></div>
    ${kr(1, 'Search', ['BM25', 'dense × 5 models', 'hybrid × 5 models'], '11')}
    ${kr(1, 'Reranker', ['off', 'on'], '× 2')}
    ${kr(1, 'Rewriting', ['off', 'on'], '× 2')}
    <div class="engineer-tot engineer-k" data-k="1"><span></span><span>search settings per index · ${S.n_chunkings} × ${S.settings_per_chunking} =</span><span class="v">${fmt(S.n_rows)}</span></div>
    ${kr(2, 'k', ['3', '5', '10'], 'free')}
    <div class="engineer-tot engineer-k" data-k="2"><span></span><span>Each setting searches all ${S.questions} questions once, top 10. Recall@3 and @5 are read off the same list. ${fmt(S.n_rows)} × ${S.questions} =</span><span class="v">${fmt(S.searches)}</span></div>
  </div>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- one knob at a time, and an interaction ---------- */
FIGS.engineer_okat = (el) => {
  const B = get('base'), S = get('slices'); if (!B || !S) return need(el, 'slices');
  const knobs = [['parser', 'structured'], ['chunker', 'structure'], ['size', '200'], ['overlap', '15%'], ['search', 'BM25'], ['model', 'none'], ['reranker', 'on'], ['rewriting', 'off'], ['k', '10']];
  const row = (name, chg, val, r5, k, cls = '') => `<div class="engineer-cfg ${cls} engineer-k" data-k="${k}"><span class="nm">${name}</span>
    ${knobs.map(([kn, v]) => `<span class="ch${chg && chg[0] === kn ? ' chg' : ''}"><i>${kn}</i>${esc(chg && chg[0] === kn ? chg[1] : v)}</span>`).join('')}<span class="rv">${r3(r5)}</span></div>`;
  const s = (sl, set) => S[sl].find((x) => String(x.setting) === String(set));
  const I = S.interaction_size_x_search, sizes = ['200', '400', '800', '1200'];
  const withRR = S.size.map((x) => [x.setting, x['recall@5']]);
  const grp = (title, pairs, k) => { const best = Math.max(...pairs.map((p) => p[1]));
    return `<div class="engineer-k" data-k="${k}"><h4>${title}</h4>${pairs.map(([sz, v]) => bar(sz + ' tokens', v, { ch: v === best })).join('')}</div>`; };
  el.innerHTML = `<div class="engineer-okat" style="inset:0">
    <div class="engineer-cfg"><span class="nm"></span>${knobs.map(() => '<span></span>').join('')}<span class="rv" style="font:500 14px var(--font);color:var(--ink-3)">recall@5</span></div>
    ${row('chosen', null, null, B['recall@5'], 0, 'base')}
    ${row('change size', ['size', '400'], null, s('size', 400)['recall@5'], 1)}
    ${row('change reranker', ['reranker', 'off'], null, s('rerank', 'False')['recall@5'], 1)}
    ${row('change search', ['search', 'hybrid'], null, s('search', 'hybrid')['recall@5'], 1)}
    <div class="engineer-inter">
      ${grp('BM25 alone: best at 1200 tokens', sizes.map((z) => [z, I.bm25[z]]), 2)}
      ${grp('BM25 + reranker: best at 200 tokens', withRR, 3)}
    </div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- the real grid loop, highlighted per click ---------- */
FIGS.engineer_code = (el) => {
  const C = get('code'); if (!C) return need(el, 'code');
  const hl = window.L3hl || esc;
  const steps = (el.dataset.hl || '').split(';');
  el.classList.add('nbcell');
  const draw = (k) => {
    const spec = k === 0 ? (el.dataset.hl0 || '') : steps[Math.min(k, steps.length) - 1];
    const on = new Set(); spec.split(',').filter(Boolean).forEach((r) => { const [a, b] = r.split('-').map(Number); for (let i = a; i <= (b || a); i++) on.add(i); });
    el.innerHTML = `<span class="hd">${esc(C.file)} · the grid loop, lines ${C.from}–${C.from + C.lines.length - 1}</span>` +
      C.lines.map((t, i) => { const n = C.from + i; return `<span class="ln${on.has(n) ? ' hl' : ''}"><i class="lno">${n}</i>${hl(t.length > 118 ? t.slice(0, 117) + '…' : t) || ' '}</span>`; }).join('');
  };
  return { step(k) { draw(k); } };
};

/* ---------- small multiples: one knob per panel, everything else at the chosen setting ---------- */
const PANELS = {
  cut: (S) => [
    { t: 'Parser', rows: S.parser.map((x) => [x.setting, x['recall@5'], x.chosen]) , rd: 'The structured parser keeps headings and table headers.' },
    { t: 'Chunker', lw: 160, rows: S.chunker.map((x) => [x.setting === 'structure' ? 'structure-aware' : x.setting, x['recall@5'], x.chosen]), rd: 'Cutting at headings beats cutting every n tokens.' },
    { t: 'Chunk size', sub: 'search p95', lw: 120, xw: 70, rows: S.size.map((x) => [x.setting + ' tokens', x['recall@5'], x.chosen, ms(x.p95_s)]), rd: 'Smaller wins, and the reranker reads small chunks faster.' },
    { t: 'Overlap', rows: S.overlap.map((x) => [x.setting === '0.0' ? '0%' : '15%', x['recall@5'], x.chosen]), rd: 'Repeating 15% at each cut keeps a sentence that straddles two chunks findable.' },
  ],
  search: (S) => [
    { t: 'Search mode', sub: 'with the reranker · p95', xw: 70, rows: S.search.map((x) => [x.setting === 'dense' ? 'dense (bge-small)' : x.setting === 'hybrid' ? 'hybrid (bge-small)' : 'BM25', x['recall@5'], x.chosen, ms(x.p95_s)]), lw: 170 },
    { t: 'Reranker', sub: 'search p95', xw: 70, rows: S.rerank.map((x) => [x.setting === 'True' ? 'on' : 'off', x['recall@5'], x.chosen, ms(x.p95_s)]) },
    { t: 'Query rewriting', sub: 'search p95', xw: 70, rows: S.rewrite.map((x) => [x.setting === 'True' ? 'on' : 'off', x['recall@5'], x.chosen, ms(x.p95_s), x.p95_s > 0.2]), rd: 'An LLM rewrites the question before the search: one more model call, and worse here.' },
    { t: 'Embedding model', sub: 'hybrid + reranker', rows: S.model_hybrid_rerank.map((x) => [x.setting, x['recall@5'], false]), lw: 110, rd: 'The chosen setting uses no embeddings. Where they are used, the model moves recall by under 3 points.' },
    { t: 'k: passages kept', sub: 'recall@k', rows: S.k.map((x) => ['top ' + x.setting, x.recall, x.setting === 10]) },
    { t: 'k: answers', sub: 'judge correct, 224', f: pct, rows: [['top 5', get('answered').find((a) => a.config.endsWith('rr1|qr0|k5') && a.config.startsWith('structured-structure-200')).answer_correct, false], ['top 10', get('scorecard.answers.answer_correct'), true]], rd: 'Same search; 5 more passages for the answer model.' },
  ],
};
FIGS.engineer_panels = (el) => {
  const S = get('slices'); if (!S) return need(el, 'slices');
  const P = PANELS[el.dataset.set](S), per = +(el.dataset.per || 2);
  el.innerHTML = `<div class="engineer-panels" style="inset:0;grid-template-columns:repeat(${el.dataset.cols || 2},1fr)">${P.map((p, i) => `<div class="engineer-pn engineer-k" data-k="${Math.floor(i / per)}" style="--lw:${p.lw || 130}px;--xw:${p.xw || 0}px">
    <h4>${p.t}${p.sub ? `<small>${p.sub}</small>` : ''}</h4>
    ${p.rows.map(([l, v, ch, ex, over]) => bar(esc(l), v, { ch, over, extra: ex || '', f: p.f || r3 })).join('')}
    ${p.rd ? `<div class="rd">${p.rd}</div>` : ''}</div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- the selection: funnel, then the nine answered configurations in plain words ---------- */
const plain = (id) => {
  const [ch, emb, mode, rr, qr, k] = id.split('|');
  const [p, c, size] = ch.split('-');
  const m = mode === 'bm25' ? 'BM25' : mode === 'dense' ? `dense (${emb})` : `hybrid (${emb})`;
  const alone = mode !== 'hybrid' && rr === 'rr0' && qr === 'qr0' ? ' alone' : '';
  return `${p === 'plain' ? 'plain parser, ' : ''}${c === 'fixed' ? 'fixed cuts, ' : c === 'recursive' ? 'recursive cuts, ' : ''}${m}${alone}${rr === 'rr1' ? ' + reranker' : ''}${qr === 'qr1' ? ' + rewriting' : ''} · ${size} · top ${k.slice(1)}`;
};
FIGS.engineer_select = (el) => {
  const S = get('scale'), A = get('answered'), B = get('base'); if (!S || !A) return need(el, 'answered');
  const rows = A.slice().sort((a, b) => a.answer_correct - b.answer_correct);
  el.innerHTML = `<div class="engineer-fun" style="left:0;right:0;top:0">
      <div class="card engineer-k" data-k="0"><b>${fmt(S.n_rows)}</b>configurations, search measured on all 224 questions</div>
      <div class="card engineer-k" data-k="1"><b>${fmt(S.under_budget_rows)}</b>with search p95 inside 200 ms</div>
      <div class="card engineer-k" data-k="2"><b>${A.length}</b>answered on all 224: the best by recall, plus a few to compare</div>
      <div class="card last engineer-k" data-k="3"><b>1</b>the best judge score among those inside the budget</div></div>
    <div class="engineer-nine engineer-k" data-k="2" style="left:0;right:0;top:170px">
      <div class="engineer-br" style="font:500 14px var(--font);color:var(--ink-3)"><span class="l">configuration</span><span>answer correct (judge), 224 questions</span><span></span><span class="e">search p95</span></div>
      ${rows.map((x) => bar(esc(plain(x.config)), x.answer_correct, { f: pct, ch: x.config === B.id, over: x.retrieval_p95_s > 0.2, extra: ms(x.retrieval_p95_s) + (x.retrieval_p95_s > 0.2 ? ' · over' : '') })).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- the scorecard against the targets ---------- */
FIGS.engineer_score = (el) => {
  const R = get('scorecard.retrieval'), A = get('scorecard.answers'); if (!R || !A) return need(el, 'scorecard');
  const v = (ok) => `<span class="engineer-met ${ok === null ? 'r' : ok ? 'y' : 'n'}">${ok === null ? 'report' : ok ? 'met' : 'missed'}</span>`;
  const rows = [
    ['Recall@5', r3(R['recall@5']) + ` <span class="engineer-note">(recall@10 ${r3(R['recall@10'])})</span>`, '≥ 0.90', R['recall@5'] >= 0.9, 'by 0.7 points; k = 10 is why the answers use ten passages'],
    ['MRR', r3(R.mrr), '', null, ''],
    ['Search p50 · p95', `${ms1(A.retrieval_s.p50)} · ${ms1(A.retrieval_s.p95)}`, '≤ 200 ms', A.retrieval_s.p95 <= 0.2, 'BM25 under 1 ms, the reranker the rest'],
    ['Answer correct (judge)', pct(A.answer_correct), '≥ 90%', A.answer_correct >= 0.9, ''],
    ['Exact facts', pct(A.fact_correct), '', null, ''],
    ['Citation correct', pct(A.citation_correct), '≥ 95%', A.citation_correct >= 0.95, ''],
    ['Time to answer p50 · p95', `${A.total_s.p50.toFixed(1)} s · ${A.total_s.p95.toFixed(1)} s`, 'p95 ≤ 4 s', A.total_s.p95 <= 4, 'the answer model’s own time; search is under 1% of it'],
    ['Cost per question', '$' + A.cost_per_q_usd.toFixed(4), '', null, ''],
  ];
  el.innerHTML = `<table class="engineer-sc" style="left:0;right:0;width:100%"><tr><th>Metric</th><th>Measured</th><th>Target</th><th></th><th></th></tr>
    ${rows.map((r, i) => `<tr class="engineer-k" data-k="${i < 3 ? 0 : i < 6 ? 1 : 2}"><td>${r[0]}</td><td class="n">${r[1]}</td><td class="n">${r[2]}</td><td>${v(r[3])}</td><td class="engineer-note">${r[4]}</td></tr>`).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- where it still fails: one real question per failure type ---------- */
FIGS.engineer_fail = (el) => {
  const P = get('per_question'), F = get('failure_logs'), X = get('failures'), BT = get('scorecard'); if (!P || !F) return need(el, 'failures');
  const mh = F.multi_hop, vc = F.version_conflict;
  const card = (k, tag, q, what, n) => `<div class="card engineer-k" data-k="${k}"><span class="tag bf">${tag}</span><span class="q">“${esc(q)}”</span>${what}<span class="n">${n}</span></div>`;
  el.innerHTML = `<div class="engineer-fails" style="inset:0">
    ${card(0, 'Multi-hop', P['Q-EMMA'].question, `Only 2 of its 11 gold passages were found. The CAB minutes and patch notes behind PUR.CERT_CHK never came back, and the 150-word answer dropped the two prices it did have.`, `All gold passages in the top 10: ${pct(mh.all_gold10 ?? mh['all_gold@10'], 0)} of ${mh.n} multi-hop questions.`)}
    ${card(1, 'Tables', P['Q-401'].question, `The current item master row never reached the top 10; a superseded 2025 export did. The answer said “not in the documents”. It is 3,000.`, `Table lookups: right passage in the top 10 for ${pct(get('scorecard.retrieval.by_type_recall@10.table_lookup'), 0)}.`)}
    ${card(2, 'Old versions', P['Q-602'].question, `An old copy (MAN-INV-72 v7.2.2) ranked 1st, the current v7.2.3 2nd. This time the answer still gave 1.5%.`, `A superseded or future copy in the top 5 for ${vc.stale_in_top5} of ${vc.n} version questions; above the gold for ${vc.stale_ranked_above_gold}.`)}
    ${card(3, 'Procedures', P['Q-101'].question, `The policy on onboarding outranked the procedure (SOP-PUR-001), so the forms NBC-F-112 and NBC-F-113 were missing.`, `Procedures: ${X.procedure.n_type - X.procedure.n_judged_wrong} of ${X.procedure.n_type} answers right.`)}
    ${card(4, 'Permissions', P['Q-902'].question, `The confidential salary file is filtered out, so the answer said “not in the documents”. It should refuse and say who may see it.`, `Permission questions: ${X.permission.n_type - X.permission.n_judged_wrong} of ${X.permission.n_type} right. The race fixes this with a withheld notice.`)}
    <div class="card engineer-k" data-k="4" style="background:var(--g1)"><span class="tag af">What to do next</span><span class="q">Each type points at a fix</span>Multi-hop: search more than once (an agent, Lecture 5). Tables and versions: better parsing and metadata filters. Permissions: tell the model what was withheld.</div>
  </div>`;
  return { step(k) { reveal(el, k); } };
};

/* ---------- proposed replacement for old slides 77-78: the race as three plain bar panels ---------- */
FIGS.engineer_race = (el) => {
  const R = get('race'); if (!R) return need(el, 'race');
  const M = [['rag', 'RAG (BM25 + reranker)'], ['wiki', 'Wiki · navigation'], ['hybrid', 'Wiki · hybrid'], ['sections', 'Wiki · sections only']];
  const O = R.overall, T = R.targets;
  const mxT = Math.max(...M.map(([k]) => O[k].answer_p95_s)), mxC = Math.max(...M.map(([k]) => O[k].cost_per_q_usd));
  const panel = (k, title, tg, rows) => `<div class="engineer-pn engineer-k" data-k="${k}"><h4>${title}</h4><span class="engineer-tg">${tg}</span>${rows}</div>`;
  el.innerHTML = `<div class="engineer-race" style="inset:0">
    ${panel(0, 'Answer correct', `judge, 224 questions · target ≥ ${pct(T.answer_correct, 0)} · blue: meets it`, M.map(([k, l]) => bar(l, O[k].answer_correct, { f: pct, ch: O[k].answer_correct >= T.answer_correct })).join(''))}
    ${panel(1, 'Time to answer, p95', `search + answer · target ≤ ${T.time_to_answer_p95_s} s · shorter is better`, M.map(([k, l]) => bar(l, O[k].answer_p95_s, { max: mxT, f: (v) => v.toFixed(1) + ' s', over: true })).join(''))}
    ${panel(2, 'Cost per question', 'answer + any search calls · lower is better', M.map(([k, l]) => bar(l, O[k].cost_per_q_usd, { max: mxC, f: (v) => '$' + v.toFixed(4), ch: k === 'rag' })).join(''))}
  </div>`;
  return { step(k) { reveal(el, k); } };
};

/* text spans: <span data-e="slices.size.0.recall@5" data-f="r3"></span> */
FIGS.engineer__fill = () => {
  document.querySelectorAll('[data-e]').forEach((s) => {
    const v = get(s.dataset.e);
    if (v == null) { s.innerHTML = '<span class="todo-in">TODO</span>'; return; }
    const f = s.dataset.f;
    s.textContent = f === 'n' ? fmt(v) : f === 'pct' ? pct(v) : f === 'pct0' ? pct(v, 0) : f === 'ms' ? ms(v) : f === 'ms1' ? ms1(v) : f === 'r3' ? r3(v) : f === 'r2' ? (+v).toFixed(2) : f === 's1' ? (+v).toFixed(1) + ' s' : f === 'h' ? (v / 3600).toFixed(1) : f === 'min' ? Math.round(v / 60) : f === 'usd4' ? '$' + (+v).toFixed(4) : f === 'usd2' ? '$' + (+v).toFixed(2) : f === 'M' ? (v / 1e6).toFixed(2) + 'M' : String(v);
  });
};
if (document.readyState !== 'loading') FIGS.engineer__fill(); else document.addEventListener('DOMContentLoaded', FIGS.engineer__fill);
})();
