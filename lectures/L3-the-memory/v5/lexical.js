/* L3 v5 · section `lexical`: BM25 from first principles, hybrid search (RRF) and the reranker, on one document (D, the
   Purchase Policy) and one question (Emma's). Every number comes from window.L3V5.lexical (lexical_data.js, written by
   experiments/v5_lexical_build.py from logs/v5_lexical*.json). Where a figure computes (RRF for a k you choose, the BM25
   curve for a k1 or b you choose), it uses the same formula as rag.py and reproduces the logged values at the defaults.
   Each FIGS.lexical_<name>(el) returns { step(k) }, k = the number of .step elements shown on the slide. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const X = () => (window.L3V5 && window.L3V5.lexical) || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const nf = (n) => Number(n).toLocaleString('en-GB');
const fx = (n, d = 2) => (n == null ? '–' : Number(n).toFixed(d));
const stop = (e) => e.stopPropagation();
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(lexical data)</span><div>${esc(what)}</div></div>`; return { step() {} }; };
const show = (el, k) => el.querySelectorAll('[data-s]').forEach((x) => x.classList.toggle('lexical-hide', +x.dataset.s > k));
const C = { ps: '#c2500f', pl: '#9b2f7a', bm: '#138a60', de: '#0b57d0', rf: '#7a5af5', rr: '#121317', gold: '#b7791f', zero: '#c9ccd3', ink3: '#6b6e76' };
const chunkName = (k) => { const c = X().chunks[k]; return `chunk ${k} · ${c.name}`; };
const goldD = (k) => X().chunks[k].facts.length > 0;
const goldTag = (t = 'answer') => `<span class="lexical-gold">${esc(t)}</span>`;

/* bind numbers into plain slide text: <span data-lx="df.brightcell.idf_all" data-f="2"></span> */
const bind = () => {
  const d = X(); if (!d) return;
  document.querySelectorAll('[data-lx]').forEach((e) => {
    let v = d; for (const k of e.dataset.lx.split('.')) v = v == null ? v : v[k];
    if (v == null) return;
    const f = e.dataset.f;
    e.textContent = f === 'n' ? nf(v) : f === 'ms' ? (v >= 100 ? nf(Math.round(v)) : fx(v, 1)) + ' ms' : f === 's' ? fx(v / 1000, 1) + '\u00a0s' : f != null ? fx(v, +f) : String(v);
  });
};
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind); else bind();

/* ================================================================ 1 · tokenize, one rule per click */
FIGS.lexical_tok = (el) => {
  const d = X(); if (!d) return need(el, 'tokenize trace');
  const T = d.tok.Q, rows = T.rows;
  const chip = (s, cls = '') => `<span class="lexical-chip ${cls}">${s}</span>`;
  const kept = rows.filter((r) => !r.stop);
  el.innerHTML = `<div class="lexical-tok">
    <div class="row"><div class="lab"><b>Emma types</b>One sentence, ${T.text.length} characters</div><div class="lexical-sent">${esc(T.text)}</div></div>
    <div class="row lexical-tr" data-s="1"><div class="lab"><b>1 · Lower-case and split</b>Split on anything that is not a letter, digit or £</div>
      <div class="lexical-chips">${rows.map((r) => chip(esc(r.word))).join('')}</div></div>
    <div class="row lexical-tr" data-s="2"><div class="lab"><b>2 · Drop stop words</b>${d.stop_n} common words in <code>rag.STOP</code></div>
      <div class="lexical-chips">${rows.map((r) => chip(esc(r.word), r.stop ? 'stop' : '')).join('')}</div></div>
    <div class="row lexical-tr" data-s="3"><div class="lab"><b>3 · Light stemming</b>Drop a plural s (ies → y) from words longer than four letters</div>
      <div class="lexical-chips">${kept.map((r) => (r.token !== r.word ? chip(`${esc(r.word)} <span class="ar">→</span> ${esc(r.token)}`, 'stem') : chip(esc(r.word)))).join('')}</div></div>
    <div class="row lexical-tr" data-s="4"><div class="lab"><b>What BM25 searches for</b>${T.tokens.length} words</div>
      <div><div class="lexical-chips">${T.tokens.map((t) => chip(esc(t), t === 'they' ? 'warn' : 'tok')).join('')}</div>
      <p class="lexical-note" style="margin:12px 0 0">“£104” stays one word. “they” is not on the stop list, so it stays: a real wart we will see again.</p></div></div>
  </div>`;
  return { step(k) { show(el, k); } };
};

/* ================================================================ 2 · codes: whole and split */
FIGS.lexical_codes = (el) => {
  const d = X(); if (!d) return need(el, 'tokenizer variants');
  const V = d.variants, gold = d.err_gold[0];
  const top = (t) => (t.cite === gold ? '<b>the ERR-PO-0412 entry</b>' : esc(t.cite.replace(/^MAN-ERR-72 v7\.2\.3, pp?\.[\d-]+, /, '')));
  const rows = [['parts_only', 'Split only', 'err · po · 0412 as three words'], ['whole_only', 'Whole only', 'err-po-0412 as one word'],
    ['course', 'Whole and split', 'our word splitter: both']];
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:230px">How the code is split</th><th>The question becomes</th>
      <th class="n" style="width:150px">ERR-PO-0412 entry<span class="sub" style="text-transform:none;letter-spacing:0">rank in MAN-ERR-72</span></th>
      <th style="width:330px">Ranked first</th>
      <th class="n lexical-tr" data-s="3" style="width:200px">Typed “${esc(d.variant_queries.typed)}”<span class="sub" style="text-transform:none;letter-spacing:0">MAN-ERR-72 · whole dump</span></th></tr></thead>
    <tbody>${rows.map(([key, name, how], i) => { const r = V[key]['Q-0412'], t = V[key].typed;
      return `<tr class="lexical-tr ${key === 'course' ? 'hi' : ''}" data-s="${i}"><td><b>${name}</b><span class="sub">${how}</span></td>
        <td class="lexical-mono" style="font-size:16px">${r.tokens.map(esc).join(' · ')}</td>
        <td class="n" style="font-size:22px;${r.doc_rank === 1 ? 'color:var(--lx-bm);font-weight:600' : 'color:var(--before)'}">${r.doc_rank}</td>
        <td style="font-size:16.5px">${top(r.doc_top[0])} <span class="lexical-mono" style="color:var(--ink-3);font-size:15px">${fx(r.doc_top[0].score, 2)}</span>${r.doc_rank !== 1 ? `<span class="sub">the entry scores ${fx((r.doc_top.find((x) => x.cite === gold) || {}).score, 2)}</span>` : ''}</td>
        <td class="n lexical-tr" data-s="3" style="font-size:20px">${t.doc_rank} · ${nf(t.dump_rank)}</td></tr>`; }).join('')}</tbody></table>`;
  return { step(k) { show(el, k); } };
};

/* ================================================================ 3 · which chunks hold which words
   Two labelled groups of rows: Emma's words (after our word splitter), then the words D itself uses for the same ideas,
   which BM25 never matches to hers because it matches exact words. */
FIGS.lexical_tf = (el) => {
  const d = X(); if (!d) return need(el, 'term counts');
  const q = [...new Set(d.tok.Q.tokens)];
  const alt = [['bought', 'buy'], ['buys', 'buy'], ['purchase', 'buy'], ['quotation', 'quote']];
  const n = d.chunks.length, cols = n + 2;
  const row = (t, s, cls, forw) => { const v = d.tf[t], nz = v.filter((x) => x > 0).length;
    return `<tr class="lexical-tr ${nz ? '' : 'z0'}" data-s="${s}"><td class="lexical-term">${esc(t)}${forw ? `<span class="for">for “${esc(forw)}”</span>` : ''}</td>${v.map((x) => `<td class="lexical-cnt ${x ? 'on ' + cls : ''}">${x || '·'}</td>`).join('')}<td class="lexical-sum">${nz ? `${nz} of ${n}` : 'none'}</td></tr>`; };
  el.innerHTML = `<table class="lexical-t lexical-tf"><thead><tr><th style="width:230px">Word</th>${d.chunks.map((c) => `<th class="cn" title="${esc(c.name)}">${c.k}</th>`).join('')}<th style="padding-left:14px">Chunks</th></tr></thead>
    <tbody><tr class="grp"><td colspan="${cols}">Emma’s words<span>her question after our word splitter: what BM25 looks for</span></td></tr>
    ${q.map((t) => row(t, 0, '')).join('')}
    <tr class="grp alt lexical-tr" data-s="2"><td colspan="${cols}">D’s own words for the same ideas<span>BM25 does not match these to Emma’s words: it matches exact words only</span></td></tr>
    ${alt.map(([t, f]) => row(t, 2, 'alt', f)).join('')}</tbody></table>
    <div class="lexical-note lexical-tr" data-s="3" style="margin-top:8px">“bought” is not “buy”, so these counts add nothing to Emma’s score. “purchase” is in all 15: every chunk’s header line says it.</div>`;
  return { step(k) { show(el, k); el.querySelectorAll('tr.z0').forEach((r) => r.classList.toggle('empty', k >= 1 && +r.dataset.s === 0)); } };
};

/* ================================================================ 4 · document frequency */
FIGS.lexical_df = (el) => {
  const d = X(); if (!d) return need(el, 'df');
  const terms = [...new Set(d.tok.Q.tokens), 'purchase', 'order'].sort((a, b) => d.df[a].df_all - d.df[b].df_all);
  const lg = (v) => (v <= 0 ? 0 : Math.log10(v + 1) / Math.log10(d.n_all + 1));
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:140px">Word</th><th style="width:330px">Chunks of D that contain it <span class="sub" style="text-transform:none;letter-spacing:0">of 15</span></th>
     <th class="lexical-tr" data-s="1">Chunks of the whole dump <span class="sub" style="text-transform:none;letter-spacing:0">of ${nf(d.n_all)} (log scale)</span></th></tr></thead><tbody>
    ${terms.map((t) => { const r = d.df[t], ctr = t === 'purchase' || t === 'order';
      return `<tr><td class="lexical-mono" style="font-size:18px;${ctr ? 'color:var(--ink-3)' : ''}">${esc(t)}</td>
      <td><div class="lexical-bar ${ctr ? 'ctr' : ''}" style="grid-template-columns:1fr 70px"><div class="trk"><i style="width:${(100 * r.df_D) / r.n_D}%"></i></div><div class="v">${r.df_D ? r.df_D : '<span style="color:var(--before)">0</span>'}</div></div></td>
      <td class="lexical-tr" data-s="1"><div class="lexical-bar ${ctr ? 'ctr' : ''}" style="grid-template-columns:1fr 90px"><div class="trk"><i style="width:${100 * lg(r.df_all)}%"></i></div><div class="v">${nf(r.df_all)}</div></div></td></tr>`; }).join('')}
  </tbody></table>`;
  return { step(k) { show(el, k); } };
};

/* ================================================================ 5 · idf bars, D or the dump */
FIGS.lexical_idf = (el) => {
  const d = X(); if (!d) return need(el, 'idf');
  const terms = [...new Set(d.tok.Q.tokens), 'purchase', 'order'];
  let mode = 'D';
  el.innerHTML = `<div class="lexical-ctl" style="margin-bottom:16px"><button data-m="D">In D · 15 chunks</button><button data-m="all">In the dump · ${nf(d.n_all)} chunks</button></div><div class="lexical-bars"></div>`;
  const box = el.querySelector('.lexical-bars');
  const draw = () => {
    el.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.m === mode));
    const key = mode === 'D' ? 'idf_D' : 'idf_all';
    const list = [...terms].sort((a, b) => (d.df[b][key] ?? -1) - (d.df[a][key] ?? -1));
    box.innerHTML = list.map((t) => { const v = d.df[t][key], ctr = t === 'purchase' || t === 'order';
      return `<div class="lexical-bar ${v == null ? 'none' : ''} ${ctr ? 'ctr' : ''}"><div class="w" style="${ctr ? 'color:var(--ink-3)' : ''}">${esc(t)}</div><div class="trk"><i style="width:${v == null ? 0 : (100 * v) / 10}%"></i></div><div class="v">${v == null ? 'not in D' : fx(v, 2)}</div></div>`; }).join('')
      + `<div class="lexical-note" style="margin-top:6px">idf on a 0 to 10 scale. ${mode === 'D' ? 'With only 15 chunks, the rarest possible word (in 1 chunk) gets 2.37.' : 'A word in 1 of 28,953 chunks gets 9.87: that is “buy”.'}</div>`;
  };
  el.querySelectorAll('button').forEach((b) => { b.addEventListener('click', (e) => { stop(e); mode = b.dataset.m; draw(); }); });
  draw();
  return { step(k) { const m = k >= 1 ? 'all' : 'D'; if (m !== mode) { mode = m; draw(); } } };
};

/* ================================================================ 6 · how BM25 weighs a word: three plain rules, one picture each
   (review of 6 Nov 2026: no sliders, little maths). 1 rare words count more (idf, across D's chunks); 2 the 2nd mention adds
   less than the 1st ("supplier" in §6, rag.BM25's own curve for chunk 5 from logs/v5_lexical_walk.json); 3 a word in a
   short chunk counts more (battery once in chunk 1 and once in chunk 5, the weights rag.BM25 stored). */
FIGS.lexical_rules = (el) => {
  const d = X(); if (!d || !d.walk) return need(el, 'rules (logs/v5_lexical.json, v5_lexical_walk.json)');
  const S = d.walk.sat, nD = d.chunks.length;
  // rule 1: which chunks hold the word
  const strip = (t) => d.tf[t].map((n) => `<i class="${n > 0 ? 'on' : ''}"></i>`).join('');
  const row1 = (t) => { const df = d.tf[t].filter((n) => n > 0).length;
    return `<div class="r1"><div class="wd"><b>${esc(t)}</b><span>${df} of ${nD} chunks</span></div><div class="strip">${strip(t)}</div><div class="num lexical-pi">${fx(d.df[t].idf_D, 2)}</div></div>`; };
  // rule 2: what each mention of "supplier" in §6 adds
  const cur = S.curve_chunk5_length.slice(0, S.tf), add = cur.map((c, i) => c.tf_part - (i ? cur[i - 1].tf_part : 0));
  const BW = 360, BH = 112, bw = 26, gap = (BW - 10 * bw) / 9, y0 = 138;
  const bars = add.map((v, i) => { const x = i * (bw + gap), h = Math.max(2, v * BH);
    const lab = i === 0 || i === 1 || i === add.length - 1 ? `<text x="${x + bw / 2}" y="${y0 - h - 8}" text-anchor="middle" class="bl">+${fx(v, 2)}</text>` : '';
    return `<rect x="${x}" y="${y0 - h}" width="${bw}" height="${h}" rx="4" fill="var(--lx-ps)" opacity="${i ? 0.75 : 1}"/>${lab}`; }).join('');
  const ax = `<text x="${bw / 2}" y="${y0 + 22}" text-anchor="middle" class="ax">1st</text><text x="${(bw + gap) + bw / 2}" y="${y0 + 22}" text-anchor="middle" class="ax">2nd</text><text x="${9 * (bw + gap) + bw / 2}" y="${y0 + 22}" text-anchor="middle" class="ax">10th</text>`;
  const total = cur[cur.length - 1].tf_part;
  // rule 3: one "battery" in a short chunk and in a long one
  const A = d.chunks[1], Bc = d.chunks[5], avg = d.avgdl.D, wOf = (c) => c.terms.find((x) => x.term === 'battery').w;
  const px = (n) => (n / 110) * 130;
  const row3 = (c, nm, what) => `<div class="r3"><div class="wd"><b>${esc(nm)}</b><span>${esc(what)} · ${c.dl} words</span></div>
      <div class="len"><div class="bar" style="width:${px(c.dl)}px"><em style="left:${px(c.dl) / 2 - 4}px"></em></div></div><div class="num lexical-pl">${fx(wOf(c), 2)}</div></div>`;
  el.innerHTML = `<div class="lexical-rules">
    <div class="lexical-rule r-i lexical-tr" data-s="0"><span class="lexical-k">1 · Across all chunks</span>
      <h3>A rare word counts more than a common one</h3>
      <div class="pic">${row1('battery')}${row1('purchase')}<div class="hd"><span>green: the chunk holds the word</span><span>weight (idf)</span></div></div>
      <p>“purchase” is in every chunk of D: finding it tells you almost nothing.</p></div>
    <div class="lexical-rule r-s lexical-tr" data-s="1"><span class="lexical-k">2 · Inside one chunk: repeats</span>
      <h3>The 2nd mention adds less than the 1st</h3>
      <div class="pic"><svg width="${BW}" height="${y0 + 30}" style="overflow:visible">${bars}${ax}</svg></div>
      <p>§6 says “supplier” <b class="lexical-ps">${S.tf} times</b>. BM25 counts that as <b class="lexical-ps">${fx(total, 2)}</b> mentions, not ${S.tf}.</p></div>
    <div class="lexical-rule r-l lexical-tr" data-s="2"><span class="lexical-k">3 · Inside one chunk: length</span>
      <h3>A word in a short chunk counts more than in a long one</h3>
      <div class="pic">${row3(A, 'chunk 1', 'version line')}${row3(Bc, 'chunk 5', '§6')}<div class="hd"><span>amber tick: one “battery”</span><span>weight</span></div></div>
      <p>Each says “battery” once. D’s average chunk is ${fx(avg, 0)} words.</p></div>
  </div>`;
  return { step(k) { show(el, k); } };
};

/* ================================================================ 10 · where BM25 wins: the dense section's cases */
FIGS.lexical_wins = (el) => {
  const d = X(); if (!d || !d.cases || !d.cases.length) return need(el, 'dense failure cases (logs/v5_dense_failures.json)');
  const cs = d.cases.filter((c) => !/dense wins/.test(c.kind || ''));
  const carry = (c) => (c.gold_terms ? [...c.gold_terms.terms].filter((t) => t.w > 0).sort((a, b) => b.w - a.w).slice(0, 2) : []);
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:250px">Case</th><th>Question</th><th class="n" style="width:120px">Dense<span class="sub" style="text-transform:none;letter-spacing:0">rank</span></th><th class="n lexical-tr" data-s="1" style="width:120px">BM25<span class="sub" style="text-transform:none;letter-spacing:0">rank</span></th><th class="lexical-tr" data-s="2" style="width:330px">Words that carried BM25<span class="sub" style="text-transform:none;letter-spacing:0">weight in the answer chunk</span></th></tr></thead><tbody>
    ${cs.map((c) => { const win = c.bm25_rank < c.dense_rank;
      return `<tr><td style="font-size:17px"><b>${esc(c.kind)}</b></td><td style="font-size:17px">${esc(c.question)}</td>
        <td class="n" style="font-size:20px;color:var(--lx-de)">${nf(c.dense_rank)}</td>
        <td class="n lexical-tr" data-s="1" style="font-size:20px;${win ? 'color:var(--lx-bm);font-weight:600' : ''}">${nf(c.bm25_rank)}</td>
        <td class="lexical-tr lexical-mono" data-s="2" style="font-size:15.5px">${carry(c).map((t) => `${esc(t.term)} <span style="color:var(--ink-3)">${fx(t.w, 1)}</span>`).join(' · ')}</td></tr>`; }).join('')}
  </tbody></table>`;
  return { step(k) { show(el, k); } };
};

/* ================================================================ generic slope chart: two rankings of the same items */
function slope(el, left, right, o) {
  // left/right: [{id, name, score, gold, tag}] in rank order; o: {lw, rw, gap, row, lc, rc, lh, rh, fmtL, fmtR, hi: Set}
  const row = o.row || 32, y0 = 34, lw = o.lw, rw = o.rw, gap = o.gap, x2 = lw + gap;
  const posR = new Map(right.map((r, i) => [r.id, i]));
  const item = (r, i, side) => `<div class="lexical-li ${r.gold ? 'lexical-g' : ''}" data-id="${esc(r.id)}" data-side="${side}" style="left:${side === 'L' ? 0 : x2}px;top:${y0 + i * row}px;width:${side === 'L' ? lw : rw}px;height:${row - 4}px;grid-template-columns:30px minmax(0,1fr) auto ${side === 'L' ? '64px' : '76px'}">
      <span class="r">${i + 1}</span><span class="nm">${esc(r.name)}</span><span class="tg">${r.gold ? goldTag(r.goldText || 'answer') : ''}${r.tag ? `<span class="lexical-gold" style="color:var(--lx-de);background:var(--lx-de-soft)">${esc(r.tag)}</span>` : ''}</span><span class="s">${esc(side === 'L' ? o.fmtL(r) : o.fmtR(r))}</span></div>`;
  el.innerHTML = `<div class="lexical-slope"><div class="lexical-colh" style="left:30px;top:0;color:${o.lc}">${o.lh}</div><div class="lexical-colh" style="left:${x2 + 30}px;top:0;color:${o.rc}">${o.rh}</div>
    <svg width="${lw + gap + rw}" height="${y0 + Math.max(left.length, right.length) * row}"></svg>
    <div class="L">${left.map((r, i) => item(r, i, 'L')).join('')}</div><div class="R">${right.map((r, i) => item(r, i, 'R')).join('')}</div></div>`;
  const svg = el.querySelector('svg');
  svg.innerHTML = left.map((r, i) => { if (!posR.has(r.id)) return ''; const j = posR.get(r.id), ya = y0 + i * row + row / 2 - 2, yb = y0 + j * row + row / 2 - 2;
    return `<path data-id="${esc(r.id)}" d="M${lw + 6},${ya} C${lw + gap / 2},${ya} ${lw + gap / 2},${yb} ${x2 - 6},${yb}" fill="none" stroke="${r.gold ? C.gold : '#b9bec7'}" stroke-width="${r.gold ? 3.5 : 1.6}"/>`; }).join('');
  return {
    set(showL, showR, lines, hi) {
      el.querySelectorAll('[data-side="L"]').forEach((e) => e.classList.toggle('lexical-hide', !showL));
      el.querySelectorAll('[data-side="R"]').forEach((e) => e.classList.toggle('lexical-hide', !showR));
      svg.style.opacity = lines ? 1 : 0; svg.style.transition = 'opacity .5s ease';
      el.querySelectorAll('[data-id]').forEach((e) => { const on = !hi || hi.has(e.dataset.id); e.style.opacity = e.classList.contains('lexical-hide') ? '' : on ? 1 : 0.28; });
    },
  };
}

/* ================================================================ 11 · two lists, two scales (D) */
FIGS.lexical_lists = (el) => {
  const d = X(); if (!d) return need(el, 'lists');
  const it = (c) => ({ id: 'c' + c.k, name: chunkName(c.k), gold: goldD(c.k), goldText: '§6.2, §6.4', bm: c.bm25, cos: c.cos });
  const L = [...d.chunks].sort((a, b) => a.bm25_rank - b.bm25_rank).map(it), R = [...d.chunks].sort((a, b) => a.dense_rank - b.dense_rank).map(it);
  const s = slope(el, L, R, { lw: 560, rw: 560, gap: 170, row: 30, lc: C.bm, rc: C.de, lh: 'BM25 · score', rh: 'Dense · cosine', fmtL: (r) => fx(r.bm, 2), fmtR: (r) => fx(r.cos, 3) });
  return { step(k) { s.set(true, k >= 1, k >= 2, null); } };
};

/* ================================================================ 12 · RRF, worked on D */
FIGS.lexical_rrf = (el) => {
  const d = X(); if (!d) return need(el, 'rrf');
  const K = d.rrf_k;
  const rows = [...d.chunks].sort((a, b) => a.fused_rank - b.fused_rank).slice(0, 6);
  const frac = (r) => `1/(${K}+${r}) = ${(1 / (K + r)).toFixed(6)}`;
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:480px">Chunk of D</th><th class="n">BM25 rank</th><th class="n lexical-tr" data-s="1">BM25 share</th><th class="n">Dense rank</th><th class="n lexical-tr" data-s="1">Dense share</th><th class="n lexical-tr" data-s="2">RRF score</th><th class="n lexical-tr" data-s="2">Fused rank</th></tr></thead><tbody>
    ${rows.map((c) => `<tr data-k="${c.k}"><td><b>${esc(chunkName(c.k))}</b>${goldD(c.k) ? ' ' + goldTag('§6.2, §6.4') : ''}</td>
      <td class="n" style="color:var(--lx-bm);font-size:20px">${c.bm25_rank}</td><td class="n lexical-tr" data-s="1">${frac(c.bm25_rank)}</td>
      <td class="n" style="color:var(--lx-de);font-size:20px">${c.dense_rank}</td><td class="n lexical-tr" data-s="1">${frac(c.dense_rank)}</td>
      <td class="n lexical-tr" data-s="2" style="color:var(--lx-rf);font-weight:600;font-size:19px">${(1 / (K + c.bm25_rank) + 1 / (K + c.dense_rank)).toFixed(6)}</td>
      <td class="n lexical-tr" data-s="2" style="font-size:21px">${c.fused_rank}</td></tr>`).join('')}
  </tbody></table>`;
  return { step(k) { show(el, k); el.querySelectorAll('tr[data-k]').forEach((r) => r.classList.toggle('hi', k >= 3 && (r.dataset.k === '12' || r.dataset.k === '1'))); } };
};

/* ================================================================ 13 · the RRF constant (interactive; rag.RRF_K = 60) */
FIGS.lexical_k = (el) => {
  const d = X(); if (!d) return need(el, 'rrf k');
  // the two lists exactly as fused in the run: on D [BM25, dense] (all 15 chunks); on the dump [dense, BM25] (top 20 each, rag.Retriever)
  const Dl = { bm: [...d.chunks].sort((a, b) => a.bm25_rank - b.bm25_rank).map((c) => 'c' + c.k), de: [...d.chunks].sort((a, b) => a.dense_rank - b.dense_rank).map((c) => 'c' + c.k), order: ['bm', 'de'],
    name: (id) => chunkName(+id.slice(1)), gold: (id) => goldD(+id.slice(1)) };
  const P = d.dump['Q-0412'], info = new Map();
  P.bm25.forEach((r) => info.set(r.i, r)); P.dense.forEach((r) => { if (!info.has(r.i)) info.set(r.i, r); });
  const Ql = { bm: P.bm25.map((r) => r.i), de: P.dense.map((r) => r.i), order: ['de', 'bm'], name: (i) => info.get(i).cite,
    gold: (i) => { const r = info.get(i); return r.facts.length > 0 || r.gold_loc === 'page'; } };
  let cs = 'D', k = d.rrf_k;
  el.innerHTML = `<div class="lexical-ctl"><button data-c="D">Emma’s question · D, 15 chunks</button><button data-c="Q">ERR-PO-0412 · the dump, top 20 of each list</button>
      <span style="margin-left:18px">RRF constant</span><input type="range" min="1" max="200" step="1" value="${k}"><output></output></div>
    <div class="lexical-kout" style="margin-top:16px"></div>`;
  const inp = el.querySelector('input'), out = el.querySelector('output'), box = el.querySelector('.lexical-kout');
  ['click', 'pointerdown', 'mousedown', 'touchstart'].forEach((ev) => inp.addEventListener(ev, stop));
  const fuse = (S) => { const s = new Map(); S.order.forEach((key) => S[key].forEach((id, r) => s.set(id, (s.get(id) || 0) + 1 / (k + r + 1)))); return [...s.entries()].sort((a, b) => b[1] - a[1]); };
  const draw = () => {
    out.textContent = String(k);
    el.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.c === cs));
    const S = cs === 'D' ? Dl : Ql, f = fuse(S);
    const where = f.findIndex(([id]) => S.gold(id)) + 1;
    box.innerHTML = `<table class="lexical-t"><thead><tr><th class="n" style="width:70px">Fused</th><th>Chunk</th><th class="n" style="width:120px">BM25 rank</th><th class="n" style="width:120px">Dense rank</th><th class="n" style="width:200px">RRF score</th></tr></thead><tbody>
      ${f.slice(0, 8).map(([id, s], i) => { const rb = S.bm.indexOf(id) + 1, rd = S.de.indexOf(id) + 1;
        return `<tr class="${S.gold(id) ? 'hi2' : ''}"><td class="n" style="font-size:20px">${i + 1}</td><td style="font-size:17px">${esc(S.name(id))}${S.gold(id) ? ' ' + goldTag(cs === 'D' ? '§6.2, §6.4' : 'answer') : ''}</td>
        <td class="n" style="color:var(--lx-bm)">${rb || '–'}</td><td class="n" style="color:var(--lx-de)">${rd || '–'}</td><td class="n" style="color:var(--lx-rf)">${s.toFixed(6)}</td></tr>`; }).join('')}
      </tbody></table><div class="lexical-note" style="margin-top:10px">With the RRF constant at ${k}, the first answer chunk is fused rank <b>${where || 'below 8'}</b>. ${cs === 'Q' ? 'BM25 alone ranks it 1st.' : 'BM25 ranks it 3rd, dense 3rd.'}</div>`;
  };
  el.querySelectorAll('button').forEach((b) => b.addEventListener('click', (e) => { stop(e); cs = b.dataset.c; draw(); }));
  inp.addEventListener('input', () => { k = +inp.value; draw(); });
  draw();
  return { step(s) { cs = s >= 1 ? 'Q' : 'D'; k = s >= 2 ? 1 : d.rrf_k; inp.value = k; draw(); } };
};

/* ================================================================ 14 · bi-encoder and cross-encoder */
FIGS.lexical_xenc = (el) => {
  const d = X(); if (!d) return need(el, 'encoders');
  const M = d.models, P = d.pair, c5 = d.chunks[5];
  const toks = P.first.slice(0, 30).map((t) => `<span class="${t === '<s>' || t === '</s>' ? 'sp' : ''}">${esc(t.replace(/▁/g, '·'))}</span>`).join('');
  const box = (x, y, w, h, html, s, bg = '#fff', extra = '') => `<div class="lexical-tr" data-s="${s}" style="position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;background:${bg};border-radius:18px;box-shadow:var(--shadow);padding:12px 16px;font-size:18px;line-height:1.35;${extra}">${html}</div>`;
  const vec = (x, y, col, s) => `<div class="lexical-tr" data-s="${s}" style="position:absolute;left:${x}px;top:${y}px;display:flex;gap:3px;align-items:flex-end;height:44px">${Array.from({ length: 16 }, (_, i) => `<i style="display:block;width:7px;height:${10 + ((i * 37) % 30)}px;background:${col};opacity:.75;border-radius:2px"></i>`).join('')}<span style="font:500 15px var(--mono);color:var(--ink-2);margin-left:8px">384 numbers</span></div>`;
  const ar = (x1, y1, x2, y2, s, col = '#9aa0aa') => `<path class="lexical-tr" data-s="${s}" d="M${x1},${y1} L${x2},${y2}" stroke="${col}" stroke-width="2.5" fill="none" marker-end="url(#lx-ah)"/>`;
  el.innerHTML = `
    <div class="lexical-colh" style="left:0;top:0;color:${C.de}">Bi-encoder · how dense search works</div>
    <div class="lexical-colh lexical-tr" data-s="1" style="left:760px;top:0;color:${C.rr}">Cross-encoder · how the reranker works</div>
    <svg width="1400" height="600" style="position:absolute;left:0;top:0;overflow:visible"><defs><marker id="lx-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#9aa0aa"/></marker></defs>
      ${ar(140, 110, 140, 150, 0)}${ar(470, 110, 470, 150, 0)}${ar(140, 230, 140, 268, 0)}${ar(470, 230, 470, 268, 0)}
      ${ar(190, 335, 280, 385, 0)}${ar(420, 335, 340, 385, 0)}
      ${ar(1050, 200, 1050, 245, 1)}${ar(1050, 345, 1050, 390, 1)}
      <line class="lexical-tr" data-s="0" x1="700" y1="20" x2="700" y2="580" stroke="#e1e5ea" stroke-width="2"/></svg>
    ${box(0, 40, 280, 70, `<b>Emma’s question</b>`, 0)}
    ${box(330, 40, 300, 70, `<b>${esc(chunkName(5))}</b>`, 0)}
    ${box(0, 150, 280, 80, `<b>bge-small-en-v1.5</b><br><span class="lexical-note">${(M.embedder_params / 1e6).toFixed(1)} M weights</span>`, 0, 'var(--lx-de-soft)')}
    ${box(330, 150, 300, 80, `<b>bge-small-en-v1.5</b><br><span class="lexical-note">the same model, on its own</span>`, 0, 'var(--lx-de-soft)')}
    ${vec(20, 280, C.de, 0)}${vec(350, 280, C.de, 0)}
    ${box(180, 385, 260, 70, `cosine = <b style="color:var(--lx-de)">${fx(c5.cos, 3)}</b>`, 0, '#fff', 'text-align:center;font-size:22px')}
    ${box(0, 480, 640, 92, `The chunk is encoded <b>without the question</b>, so all ${nf(d.n_all)} chunk vectors are computed once and stored. A question costs one encoding and a lookup.`, 2, 'var(--g1)', 'font-size:18px')}
    ${box(760, 40, 640, 160, `<span class="lexical-k">One input: question and chunk together · ${P.n} tokens</span><div class="lexical-tokrow">${toks}<span>…</span></div>`, 1)}
    ${box(860, 245, 380, 100, `<b>${esc(M.reranker)}</b><br><span class="lexical-note">${(M.reranker_params / 1e6).toFixed(0)} M weights (${esc(M.reranker_arch.replace('ForSequenceClassification', ''))}); every layer sees both texts</span>`, 1, '#f4f5f7')}
    ${box(900, 390, 300, 70, `one number = <b>${fx(c5.rr, 4)}</b>`, 1, '#fff', 'text-align:center;font-size:22px')}
    ${box(760, 480, 640, 92, `The chunk is read <b>with this question</b>: nothing can be stored ahead. ${d.lat.gpu.rerank_20.p50_ms.toFixed(0)} ms for 20 chunks on an L4 GPU, so only the top 20 get this treatment.`, 2, '#f4f5f7', 'font-size:18px')}`;
  return { step(k) { show(el, k); } };
};

/* ================================================================ 15 · the reranker on D */
FIGS.lexical_rrD = (el) => {
  const d = X(); if (!d) return need(el, 'rerank D');
  const it = (c) => ({ id: 'c' + c.k, name: chunkName(c.k), gold: goldD(c.k), goldText: '§6.2, §6.4', bm: c.bm25, rr: c.rr });
  const L = [...d.chunks].sort((a, b) => a.bm25_rank - b.bm25_rank).map(it), R = [...d.chunks].sort((a, b) => a.rr_rank - b.rr_rank).map(it);
  const s = slope(el, L, R, { lw: 560, rw: 560, gap: 170, row: 30, lc: C.bm, rc: C.rr, lh: 'BM25 · score', rh: 'Reranker · bge-reranker-base', fmtL: (r) => fx(r.bm, 2), fmtR: (r) => r.rr.toFixed(5) });
  return { step(k) { s.set(true, k >= 1, k >= 1, k >= 2 ? new Set(['c5', 'c1', 'c12']) : null); } };
};

/* ================================================================ 16 · the real top 20, reordered */
FIGS.lexical_rr20 = (el) => {
  const d = X(); if (!d) return need(el, 'rerank 20');
  const R = d.dump['Q-EMMA'].rerank;
  const it = (r) => ({ id: 'i' + r.i, name: r.cite, gold: r.facts.length > 0, goldText: r.facts.length + ' facts', tag: /POL-PUR-001 v4\.1/.test(r.cite) ? 'D · 12' : '', bm: d.dump['Q-EMMA'].bm25.find((b) => b.i === r.i).score, rr: r.score });
  const L = [...R].sort((a, b) => a.before - b.before).map(it), Rr = [...R].sort((a, b) => a.after - b.after).map(it);
  const s = slope(el, L, Rr, { lw: 600, rw: 610, gap: 150, row: 27, lc: C.bm, rc: C.rr, lh: 'BM25 over the whole dump · top 20', rh: 'After the reranker', fmtL: (r) => fx(r.bm, 1), fmtR: (r) => r.rr.toFixed(4) });
  const hi = new Set(L.filter((r) => r.gold || r.tag).map((r) => r.id));
  return { step(k) { s.set(true, k >= 1, k >= 1, k >= 2 ? hi : null); } };
};

/* ================================================================ 17 · what reranking costs, on a plain (linear) time axis
   Measured: reranker on 20 pairs (L4 GPU, median), BM25 over the dump (4 CPU cores, median), logs/v5_lexical_rerank_latency.json.
   Estimated, and labelled so: every pair = the 20-pair time × 28,953 / 20 (key.all_pairs_gpu_s). */
FIGS.lexical_cost = (el) => {
  const d = X(); if (!d) return need(el, 'latency');
  const g = d.lat.gpu, c = d.lat.cpu, allS = d.key.all_pairs_gpu_s, full = allS * 1000;
  const wd = (ms) => Math.max(0.5, (100 * ms) / full);
  const lab = (ms) => (ms < 1 ? ms.toFixed(1) + ' ms' : ms < 1000 ? Math.round(ms) + ' ms' : '≈ ' + Math.round(ms / 1000) + ' s');
  const rows = [
    ['The reranker reads the top 20', '20 pairs · measured', g.rerank_20.p50_ms, 'var(--lx-rr)', 0, ''],
    [`The reranker reads every chunk`, `${nf(d.n_all)} pairs · the same rate, estimated`, full, 'var(--lx-rr)', 1, 'est'],
    ['BM25 searches every chunk', `${nf(d.n_all)} chunks · 4 CPU cores · measured`, c.bm25_query.p50_ms, 'var(--lx-bm)', 2, ''],
  ];
  el.innerHTML = `<div class="lexical-costs">${rows.map(([n, m, ms, col, s, cls]) => `<div class="row lexical-tr" data-s="${s}"><div class="w">${n}<small>${m}</small></div>
      <div class="trk"><i class="${cls}" style="width:${wd(ms)}%;background:${col}"></i></div><div class="v">${lab(ms)}</div></div>`).join('')}
    <div class="row ax"><div class="w"></div><div class="ticks">${[0, 10, 20, 30, 40, 50, 60].map((s) => `<span style="left:${(100 * s * 1000) / full}%">${s} s</span>`).join('')}</div><div></div></div></div>`;
  return { step(k) { show(el, k); } };
};

/* ================================================================ 18 · the BM25 formula, three coloured parts
   <div data-fig="lexical_formula" data-on="i|s|l|isl" data-sum="1">: idf (across all chunks), saturation (inside one
   chunk) and length (inside one chunk, against the average). Parts not in data-on are dimmed. */
FIGS.lexical_formula = (el) => {
  const on = el.dataset.on || 'isl', sum = el.dataset.sum === '1';
  const o = (p) => (on.includes(p) ? '' : ' off');
  const lg = [
    ['i', 'var(--lx-pi)', 'idf', 'across all chunks: how many contain the word'],
    ['s', 'var(--lx-ps)', 'repeats', 'inside this chunk: how often the word appears (tf)'],
    ['l', 'var(--lx-pl)', 'length', 'inside this chunk, against the average chunk'],
  ];
  el.innerHTML = `<div class="lexical-fx">
    ${sum ? `<div class="sum">A chunk’s <b>score</b> = the sum of <b>weight(word, chunk)</b> over the question’s words that the chunk contains, where</div>` : ''}
    <div class="eq"><span>weight(word, chunk) =</span><span class="lexical-pt pt-i${o('i')}">idf(word)</span><span>×</span>
      <div class="lexical-pt pt-s${o('s')}"><div class="fx-num"><span class="tf">tf</span> · (k1 + 1)</div><div class="fx-den"><span class="tf">tf</span> + k1 · <span class="lexical-pt pt-l${o('l')}">(1 − b + b · dl / avgdl)</span></div></div></div>
    <div class="lg">${lg.map(([p, c, n, t]) => `<span class="${on.includes(p) ? '' : 'off'}"><i style="background:${c}"></i><b style="color:${c}">${n}</b>${t}</span>`).join('')}</div>
  </div>`;
  return { step() {} };
};

/* ================================================================ 19 · when a question arrives: five steps, on chunk 12 and chunk 5
   Every number is read from logs/v5_lexical_walk.json (rag.BM25 built on D's 15 chunks). */
FIGS.lexical_walk = (el) => {
  const d = X(); if (!d || !d.walk) return need(el, 'walk-through (logs/v5_lexical_walk.json)');
  const W = d.walk, q = [...new Set(d.tok.Q.tokens)];
  const P = [W.chunks[12], W.chunks[5]];
  const chips = (c) => c.matched.map((m) => `<span class="wchip hit">${esc(m.word)} ×${m.tf}</span>`).join('')
    + `</div><div class="nothere">not here: <span>${c.missing.map(esc).join(' · ')}</span>`;
  const table = (c) => `<table class="lexical-t"><thead><tr><th>Word</th><th class="n" style="color:var(--lx-pi)">idf</th><th class="n" style="color:var(--lx-ps)">tf</th><th class="n" style="color:var(--lx-pl)">length</th><th class="n">weight</th></tr></thead><tbody>
      ${c.matched.map((m) => `<tr><td class="lexical-mono">${esc(m.word)}</td><td class="n" style="color:var(--lx-pi)">${fx(m.idf, 2)}</td><td class="n" style="color:var(--lx-ps)">${m.tf}</td><td class="n" style="color:var(--lx-pl)">${fx(m.length_factor, 2)}</td><td class="n" style="font-weight:600">${fx(m.weight, 2)}</td></tr>`).join('')}</tbody></table>`;
  const X0 = 270, PW = 555, GAP = 20, PT = 70;
  const lab = (y, s, n, h, t) => `<div class="st lexical-tr" data-s="${s}" style="top:${y}px"><b>${n} · ${h}</b>${t}</div>`;
  const ranks = W.order.map((k) => W.chunks[k]);
  const top = ranks.filter((c) => c.score > 0), zero = ranks.filter((c) => c.score <= 0);
  el.innerHTML = `<div class="lexical-walk">
    ${lab(0, 0, 1, 'Split', 'the question into words')}
    <div class="wchips" style="position:absolute;left:${X0}px;top:4px">${q.map((t) => `<span class="wchip hit">${esc(t)}</span>`).join('')}</div>
    ${lab(PT + 66, 1, 2, 'Find', 'in each chunk, which of those words it holds, and how often')}
    ${lab(PT + 158, 2, 3, 'Weigh', 'each word found, with the three rules: <span class="lexical-pi">idf</span>, <span class="lexical-ps">tf</span> and <span class="lexical-pl">length</span>')}
    ${lab(PT + 276, 3, 4, 'Add', 'the weights: the chunk’s score')}
    ${P.map((c, i) => `<div class="pan lexical-tr ${c.rank === 1 ? 'pan-top' : ''}" data-s="1" style="left:${X0 + i * (PW + GAP)}px;top:${PT}px;width:${PW}px;height:332px">
      <h4>${esc(chunkName(c.k))}<small>${c.dl} words · ${c.matched.length} of Emma’s ${q.length} words found</small></h4>
      <div class="wchips">${chips(c)}</div>
      <div class="lexical-tr" data-s="2" style="margin-top:8px">${table(c)}</div>
      <div class="tot lexical-tr" data-s="3"><span>${c.matched.map((m) => fx(m.weight, 2)).join(' + ')} =</span><b>${fx(c.score, 2)}</b></div></div>`).join('')}
    ${lab(PT + 356, 4, 5, 'Sort', 'all 15 chunks by score')}
    <div class="rk lexical-tr" data-s="4" style="position:absolute;left:${X0}px;top:${PT + 358}px;width:${2 * PW + GAP}px">
      ${top.map((c) => `<span class="${c.k === 12 || c.k === 5 ? 'on' : ''}">${c.rank} · chunk ${c.k}<em>${fx(c.score, 2)}</em></span>`).join('')}
      <span>${top.length + 1}–${ranks.length} · the other ${zero.length}<em>0, tied</em></span></div>
    <div class="lexical-note lexical-tr" data-s="4" style="position:absolute;left:${X0}px;top:${PT + 418}px;width:${2 * PW + GAP}px">Only words a chunk contains add to its score: the five Emma words D never uses add nothing anywhere. §6, the rule, comes third.</div>
  </div>`;
  return { step(k) { show(el, k); } };
};
})();
