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
const C = { bm: '#138a60', de: '#0b57d0', rf: '#7a5af5', rr: '#121317', gold: '#b7791f', zero: '#c9ccd3', ink3: '#6b6e76' };
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
    e.textContent = f === 'n' ? nf(v) : f === 'ms' ? (v >= 100 ? nf(Math.round(v)) : fx(v, 1)) + ' ms' : f != null ? fx(v, +f) : String(v);
  });
};
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind); else bind();

/* syntax colours for Python lines (comments, strings, numbers, keywords) */
const KW = /^(def|return|for|in|if|else|import|from|not|and|or|None|True|False|is|lambda|with|as|class|self)$/;
const hl = (line) => {
  const re = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d[\d_.]*\b)|([A-Za-z_]\w*)/g;
  let out = '', last = 0, m;
  while ((m = re.exec(line))) {
    out += esc(line.slice(last, m.index));
    if (m[1]) out += `<span class="cmt">${esc(m[1])}</span>`; else if (m[2]) out += `<span class="st">${esc(m[2])}</span>`;
    else if (m[3]) out += `<span class="nu">${esc(m[3])}</span>`; else out += KW.test(m[4]) ? `<span class="kw">${m[4]}</span>` : esc(m[4]);
    last = re.lastIndex;
  }
  return out + esc(line.slice(last));
};

/* ================================================================ 1 · tokenize, one rule per click */
FIGS.lexical_tok = (el) => {
  const d = X(); if (!d) return need(el, 'tokenize trace');
  const T = d.tok.Q, rows = T.rows;
  const chip = (s, cls = '') => `<span class="lexical-chip ${cls}">${s}</span>`;
  const kept = rows.filter((r) => !r.stop);
  el.innerHTML = `<div class="lexical-tok">
    <div class="row"><div class="lab"><b>Emma types</b>One sentence, ${T.text.length} characters</div><div class="lexical-sent">${esc(T.text)}</div></div>
    <div class="row lexical-tr" data-s="1"><div class="lab"><b>1 · Lower-case and split</b>A word is a run of letters, digits or £</div>
      <div class="lexical-chips">${rows.map((r) => chip(esc(r.word))).join('')}</div></div>
    <div class="row lexical-tr" data-s="2"><div class="lab"><b>2 · Drop stop words</b>${d.stop_n} common words in <code>rag.STOP</code></div>
      <div class="lexical-chips">${rows.map((r) => chip(esc(r.word), r.stop ? 'stop' : '')).join('')}</div></div>
    <div class="row lexical-tr" data-s="3"><div class="lab"><b>3 · Light stemming</b>Drop a plural s (ies → y) from words longer than four letters</div>
      <div class="lexical-chips">${kept.map((r) => (r.token !== r.word ? chip(`${esc(r.word)} <span class="ar">→</span> ${esc(r.token)}`, 'stem') : chip(esc(r.word)))).join('')}</div></div>
    <div class="row lexical-tr" data-s="4"><div class="lab"><b>What BM25 searches for</b>${T.tokens.length} tokens</div>
      <div><div class="lexical-chips">${T.tokens.map((t) => chip(esc(t), t === 'they' ? 'warn' : 'tok')).join('')}</div>
      <p class="lexical-note" style="margin:12px 0 0">“£104” stays one token. “they” is not on the stop list, so it stays: a real wart we will see again.</p></div></div>
  </div>`;
  return { step(k) { show(el, k); } };
};

/* ================================================================ 2 · codes: whole and split */
FIGS.lexical_codes = (el) => {
  const d = X(); if (!d) return need(el, 'tokenizer variants');
  const V = d.variants, gold = d.err_gold[0];
  const top = (t) => (t.cite === gold ? '<b>the ERR-PO-0412 entry</b>' : esc(t.cite.replace(/^MAN-ERR-72 v7\.2\.3, pp?\.[\d-]+, /, '')));
  const rows = [['parts_only', 'Split only', 'err · po · 0412 as three words'], ['whole_only', 'Whole only', 'err-po-0412 as one word'],
    ['course', 'Whole and split', 'rag.tokenize: both']];
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:230px">Tokenizer</th><th>The question becomes</th>
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

/* ================================================================ 3 · which chunks hold which words */
FIGS.lexical_tf = (el) => {
  const d = X(); if (!d) return need(el, 'term counts');
  const q = [...new Set(d.tok.Q.tokens)], extra = [['bought', 1, 'alt'], ['buys', 1, 'alt'], ['quotation', 1, 'alt'], ['purchase', 2, 'hd'], ['policy', 2, 'hd']];
  const n = d.chunks.length;
  const row = (t, s, cls = '') => { const v = d.tf[t], nz = v.filter((x) => x > 0).length;
    return `<tr class="lexical-tr ${nz ? '' : 'z0'}" data-s="${s}" data-t="${esc(t)}"><td class="lexical-term">${esc(t)}</td>${v.map((x) => `<td class="lexical-cnt ${x ? 'on ' + cls : ''}">${x || '·'}</td>`).join('')}<td class="lexical-sum">${nz ? `${nz} of ${n}` : 'none'}${cls === 'alt' ? ' · D’s word' : cls === 'hd' ? ' · header line' : ''}</td></tr>`; };
  el.innerHTML = `<table class="lexical-t lexical-tf"><thead><tr><th style="width:150px">Token</th>${d.chunks.map((c) => `<th class="cn" title="${esc(c.name)}">${c.k}</th>`).join('')}<th style="padding-left:14px">Chunks</th></tr></thead>
    <tbody>${q.map((t) => row(t, 0)).join('')}${extra.map(([t, s, c]) => row(t, s + 1, c)).join('')}</tbody></table>
    <div class="lexical-note" style="margin-top:14px">Columns are D’s chunks 0 to 14. Chunk 1 is a version-history line, 4 is §5 Approval limits, 5 is §6 Supplier qualification (the rule), 12 is the FAQ on battery packs.</div>`;
  return { step(k) { show(el, k); el.querySelectorAll('tr.z0').forEach((r) => r.classList.toggle('empty', k >= 1 && +r.dataset.s === 0)); } };
};

/* ================================================================ 4 · document frequency */
FIGS.lexical_df = (el) => {
  const d = X(); if (!d) return need(el, 'df');
  const terms = [...new Set(d.tok.Q.tokens), 'purchase', 'order'].sort((a, b) => d.df[a].df_all - d.df[b].df_all);
  const lg = (v) => (v <= 0 ? 0 : Math.log10(v + 1) / Math.log10(d.n_all + 1));
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:140px">Token</th><th style="width:330px">Chunks of D that contain it <span class="sub" style="text-transform:none;letter-spacing:0">of 15</span></th>
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

/* ================================================================ 6 · term-frequency saturation (k1 slider) */
FIGS.lexical_sat = (el) => {
  const d = X(); if (!d) return need(el, 'k1');
  const W = 860, H = 470, L = 50, R = 30, T = 30, B = 60, xmax = 12, ymax = 4;
  let k1 = d.k1, shown = 0;
  const xs = (t) => L + ((W - L - R) * t) / xmax, ys = (v) => T + (H - T - B) * (1 - Math.min(v, ymax) / ymax);
  const f = (t) => (t * (k1 + 1)) / (t + k1);   // at average chunk length (the length factor is 1)
  el.innerHTML = `<svg width="${W}" height="${H}" class="lexical-enc"></svg>
    <div class="lexical-ctl" style="margin-top:6px"><span>k1</span><input type="range" min="0.2" max="3" step="0.1" value="${k1}"><output></output><span class="lexical-note" style="margin-left:10px">rag.BM25 uses k1 = 1.2</span></div>`;
  const svg = el.querySelector('svg'), inp = el.querySelector('input'), out = el.querySelector('output');
  ['click', 'pointerdown', 'mousedown', 'touchstart'].forEach((ev) => inp.addEventListener(ev, stop));
  inp.addEventListener('input', () => { k1 = +inp.value; draw(); });
  const draw = () => {
    out.textContent = k1.toFixed(1);
    let s = '';
    for (let v = 0; v <= ymax; v++) s += `<line x1="${L}" x2="${W - R}" y1="${ys(v)}" y2="${ys(v)}" stroke="#e1e5ea"/><text x="${L - 12}" y="${ys(v) + 6}" text-anchor="end" style="font:15px var(--mono);fill:#6b6e76">${v}</text>`;
    for (let t = 0; t <= xmax; t += 2) s += `<text x="${xs(t)}" y="${H - B + 26}" text-anchor="middle" style="font:15px var(--mono);fill:#6b6e76">${t}</text>`;
    s += `<text x="${(L + W - R) / 2}" y="${H - 8}" text-anchor="middle" style="font:500 16px var(--font);fill:#45474d">times the word appears in the chunk (tf)</text>`;
    s += `<text x="${L + 8}" y="${T + 6}" style="font:500 16px var(--font);fill:#45474d">weight, in units of idf</text>`;
    // raw count
    s += `<line x1="${xs(0)}" y1="${ys(0)}" x2="${xs(ymax)}" y2="${ys(ymax)}" stroke="#9aa0aa" stroke-width="3" stroke-dasharray="7 6"/>`;
    s += `<text x="${xs(ymax) + 8}" y="${ys(ymax) + 18}" style="font:500 16px var(--font);fill:#6b6e76">plain count: 10 mentions = 10</text>`;
    if (shown >= 1) {
      let p = ''; for (let t = 0; t <= xmax + 1e-9; t += 0.1) p += `${p ? 'L' : 'M'}${xs(t).toFixed(1)},${ys(f(t)).toFixed(1)}`;
      s += `<line x1="${L}" x2="${W - R}" y1="${ys(k1 + 1)}" y2="${ys(k1 + 1)}" stroke="${C.bm}" stroke-dasharray="3 5" opacity=".7"/>`;
      s += `<text x="${W - R}" y="${ys(k1 + 1) - 8}" text-anchor="end" style="font:500 15px var(--font);fill:${C.bm}">ceiling k1 + 1 = ${(k1 + 1).toFixed(1)}</text>`;
      s += `<path d="${p}" fill="none" stroke="${C.bm}" stroke-width="4"/>`;
    }
    if (shown >= 2) [1, 2, 10].forEach((t) => {
      s += `<circle cx="${xs(t)}" cy="${ys(f(t))}" r="7" fill="#fff" stroke="${C.bm}" stroke-width="3"/>`;
      s += `<text x="${xs(t) + (t === 1 ? -12 : 0)}" y="${ys(f(t)) + (t === 1 ? -10 : 30)}" text-anchor="${t === 1 ? 'end' : 'middle'}" style="font:600 16px var(--mono);fill:${C.bm}">${f(t).toFixed(2)}</text>`;
    });
    svg.innerHTML = s;
    el.dispatchEvent(new CustomEvent('lexical-sat', { detail: { k1, f1: f(1), f2: f(2), f9: f(9), f10: f(10) } }));
    const pane = document.getElementById('lexical-sat-out');
    if (pane) pane.innerHTML = `One mention: <b>${f(1).toFixed(2)}</b> · two: <b>${f(2).toFixed(2)}</b> · ten: <b>${f(10).toFixed(2)}</b>.<br>The tenth adds <b>${(f(10) - f(9)).toFixed(3)}</b>.`;
  };
  draw();
  return { step(k) { shown = k; if (k === 0 && k1 !== d.k1) { k1 = d.k1; inp.value = k1; } draw(); } };
};

/* ================================================================ 7 · length normalisation, two real chunks (b slider) */
FIGS.lexical_len = (el) => {
  const d = X(); if (!d) return need(el, 'length');
  const A = d.chunks[1], Bc = d.chunks[5], idf = d.df.battery.idf_D, k1 = d.k1, avg = d.avgdl.D;
  let b = d.b;
  const flow = (s) => s.replace(/\n(?!\d+\.\d|\d+\. )/g, ' ');
  const mark = (s) => esc(flow(s)).replace(/\b(battery|packs)\b/gi, '<mark>$1</mark>');
  const w = (c) => (idf * (k1 + 1)) / (1 + k1 * (1 - b + (b * c.dl) / avg));
  const logged = (c) => c.terms.find((t) => t.term === 'battery').w;
  el.innerHTML = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
    ${[A, Bc].map((c) => `<div class="lexical-card ${c.k === 5 ? 'lexical-c-bm' : ''}"><span class="lexical-k">${esc(chunkName(c.k))}${c.k === 5 ? ' · holds §6.2 and §6.4' : ''}</span>
      <div class="lexical-quote" style="font-size:${c.k === 5 ? 14.5 : 17}px;margin-top:0">${mark(c.body)}</div>
      <div class="lexical-tr" data-s="1" style="margin-top:12px;font-size:20px"><b>${c.dl}</b> words after tokenize · |d| / avgdl = ${c.dl} / ${fx(avg, 1)} = <b>${fx(c.dl / avg, 3)}</b></div></div>`).join('')}
  </div>
  <div class="lexical-box lexical-tr" data-s="2" style="margin-top:18px;display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:14px;align-items:center;font-size:20px">
    <div><span class="lexical-k">Length factor</span>1 − b + b · |d| / avgdl</div>
    <div class="lexical-mono" data-v="nA"></div><div class="lexical-mono" data-v="nB"></div>
    <div class="lexical-tr" data-s="3"><span class="lexical-k">Weight of “battery” (tf = 1)</span>idf · 2.2 / (1 + 1.2 · factor)</div>
    <div class="lexical-mono lexical-tr" data-s="3" data-v="wA" style="font-size:26px"></div><div class="lexical-mono lexical-tr" data-s="3" data-v="wB" style="font-size:26px;color:var(--lx-bm)"></div>
  </div>
  <div class="lexical-ctl" style="margin-top:12px"><span>b</span><input type="range" min="0" max="1" step="0.05" value="${b}"><output></output><span class="lexical-note" data-v="note" style="margin-left:8px"></span></div>`;
  const inp = el.querySelector('input'), out = el.querySelector('output');
  ['click', 'pointerdown', 'mousedown', 'touchstart'].forEach((ev) => inp.addEventListener(ev, stop));
  const V = (k) => el.querySelector(`[data-v="${k}"]`);
  const draw = () => {
    out.textContent = b.toFixed(2);
    const fA = 1 - b + (b * A.dl) / avg, fB = 1 - b + (b * Bc.dl) / avg;
    V('nA').innerHTML = `chunk 1: <b>${fx(fA, 3)}</b>`; V('nB').innerHTML = `chunk 5: <b>${fx(fB, 3)}</b>`;
    V('wA').textContent = fx(w(A), 3); V('wB').textContent = fx(w(Bc), 3);
    V('note').textContent = Math.abs(b - d.b) < 1e-9 ? `rag.BM25 (b = 0.75) logged ${fx(logged(A), 3)} and ${fx(logged(Bc), 3)}` : b === 0 ? 'b = 0: length is ignored' : '';
  };
  inp.addEventListener('input', () => { b = +inp.value; draw(); });
  draw();
  return { step(k) { show(el, k); } };
};

/* ================================================================ 8 · the BM25 sum for Emma on D */
FIGS.lexical_score = (el) => {
  const d = X(); if (!d) return need(el, 'bm25 on D');
  const terms = [...new Set(d.tok.Q.tokens)];
  const rk = [...d.chunks].sort((a, b) => a.bm25_rank - b.bm25_rank);
  const top = rk.filter((c) => c.bm25 > 0), rest = rk.filter((c) => c.bm25 <= 0);
  const cell = (c, t) => { const x = c.terms.find((y) => y.term === t); return x && x.tf ? `<td class="n">${fx(x.w, 2)}<span class="sub">tf ${x.tf}</span></td>` : '<td class="n z">·</td>'; };
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:330px">Chunk of D</th>${terms.map((t) => `<th class="n lexical-mono" style="text-transform:none;letter-spacing:0;font-size:15px">${esc(t)}</th>`).join('')}<th class="n">BM25</th><th class="n">Rank</th></tr></thead><tbody>
    ${top.map((c, i) => `<tr class="lexical-tr" data-s="${i}" data-k="${c.k}"><td><b>${esc(chunkName(c.k))}</b>${goldD(c.k) ? ' ' + goldTag('holds §6.2, §6.4') : ''}<span class="sub">${c.dl} words</span></td>${terms.map((t) => cell(c, t)).join('')}<td class="n" style="font-size:21px;font-weight:600;color:var(--lx-bm)">${fx(c.bm25, 2)}</td><td class="n" style="font-size:21px">${c.bm25_rank}</td></tr>`).join('')}
    <tr class="lexical-tr" data-s="${top.length - 1}"><td style="color:var(--ink-3)">The other ${rest.length} chunks</td>${terms.map(() => '<td class="n z">·</td>').join('')}<td class="n z">0</td><td class="n z">tie</td></tr>
  </tbody></table>`;
  return { step(k) { show(el, k); el.querySelectorAll('tr[data-k]').forEach((r) => r.classList.toggle('hi2', k >= top.length && +r.dataset.k === 5)); } };
};

/* ================================================================ 9 · rag.BM25, each line tied to the formula */
FIGS.lexical_code = (el) => {
  const d = X(); if (!d) return need(el, 'code');
  const build = d.code.bm25_build, query = d.code.bm25_query.filter((l) => !/import numpy|^\s*$/.test(l.t));
  const groups = [
    ['toks = tokenize(t)', 'dl.append', 'tf: dict', 'for w in toks', 'vocab.setdefault', 'tf[j] = tf.get'],
    ['df = np.bincount', 'self.idf ='],
    ['dl = np.array', 'avg = float', 'denom ='],
    ['w = self.idf', 'self.W ='],
    ['ids = sorted', 'if not ids', 'return np.zeros', 'self.W[:, ids].sum'],
  ];
  const which = (t) => groups.findIndex((g) => g.some((s) => t.includes(s)));
  const line = (l, dd) => `<span class="ln" data-g="${which(l.t)}"><span class="no">${l.n}</span>${hl(l.t.slice(Math.min(dd, l.t.length - l.t.trimStart().length)))}</span>`;
  el.innerHTML = `<div class="lexical-code" style="left:0;top:0;width:${el.clientWidth}px;height:542px"><span class="hd">rag.py · class BM25 · __init__: built once, for every chunk</span>${build.map((l) => line(l, 8)).join('')}</div>
    <div class="lexical-code" style="left:0;top:560px;width:${el.clientWidth}px;height:${58 + 21 * query.length}px"><span class="hd">rag.py · BM25.scores: every question</span>${query.map((l) => line(l, 4)).join('')}</div>`;
  const parts = document.querySelectorAll('.lexical-f .p');
  return { step(k) {
    el.querySelectorAll('.lexical-code').forEach((c) => c.classList.toggle('dim', k > 0));
    el.querySelectorAll('.ln').forEach((l) => l.classList.toggle('on', k > 0 && +l.dataset.g === k - 1));
    parts.forEach((p) => p.classList.toggle('on', k > 0 && (p.dataset.g || '').split(',').includes(String(k - 1))));
  } };
};

/* ================================================================ 10 · where BM25 wins: the dense section's cases */
FIGS.lexical_wins = (el) => {
  const d = X(); if (!d || !d.cases || !d.cases.length) return need(el, 'dense failure cases (logs/v5_dense_failures.json)');
  const cs = d.cases.filter((c) => !/dense wins/.test(c.kind || ''));
  const carry = (c) => (c.gold_terms ? [...c.gold_terms.terms].filter((t) => t.w > 0).sort((a, b) => b.w - a.w).slice(0, 2) : []);
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:250px">Case</th><th>Question</th><th class="n" style="width:120px">Dense<span class="sub" style="text-transform:none;letter-spacing:0">rank</span></th><th class="n lexical-tr" data-s="1" style="width:120px">BM25<span class="sub" style="text-transform:none;letter-spacing:0">rank</span></th><th class="lexical-tr" data-s="2" style="width:330px">Tokens that carried BM25<span class="sub" style="text-transform:none;letter-spacing:0">weight in the answer chunk</span></th></tr></thead><tbody>
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
  el.innerHTML = `<table class="lexical-t"><thead><tr><th style="width:360px">Chunk of D</th><th class="n">BM25 rank</th><th class="n lexical-tr" data-s="1">BM25 share</th><th class="n">Dense rank</th><th class="n lexical-tr" data-s="1">Dense share</th><th class="n lexical-tr" data-s="2">RRF score</th><th class="n lexical-tr" data-s="2">Fused rank</th></tr></thead><tbody>
    ${rows.map((c) => `<tr data-k="${c.k}"><td><b>${esc(chunkName(c.k))}</b>${goldD(c.k) ? ' ' + goldTag('§6.2, §6.4') : ''}</td>
      <td class="n" style="color:var(--lx-bm);font-size:20px">${c.bm25_rank}</td><td class="n lexical-tr" data-s="1">${frac(c.bm25_rank)}</td>
      <td class="n" style="color:var(--lx-de);font-size:20px">${c.dense_rank}</td><td class="n lexical-tr" data-s="1">${frac(c.dense_rank)}</td>
      <td class="n lexical-tr" data-s="2" style="color:var(--lx-rf);font-weight:600;font-size:19px">${(1 / (K + c.bm25_rank) + 1 / (K + c.dense_rank)).toFixed(6)}</td>
      <td class="n lexical-tr" data-s="2" style="font-size:21px">${c.fused_rank}</td></tr>`).join('')}
  </tbody></table>`;
  return { step(k) { show(el, k); el.querySelectorAll('tr[data-k]').forEach((r) => r.classList.toggle('hi', k >= 3 && (r.dataset.k === '12' || r.dataset.k === '1'))); } };
};

/* ================================================================ 13 · the k in RRF (interactive) */
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
      <span style="margin-left:18px">k</span><input type="range" min="1" max="200" step="1" value="${k}"><output></output></div>
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
      </tbody></table><div class="lexical-note" style="margin-top:10px">With k = ${k}, the first answer chunk is fused rank <b>${where || 'below 8'}</b>. ${cs === 'Q' ? 'BM25 alone ranks it 1st.' : 'BM25 ranks it 3rd, dense 3rd.'}</div>`;
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

/* ================================================================ 17 · what each step costs (log scale) */
FIGS.lexical_cost = (el) => {
  const d = X(); if (!d) return need(el, 'latency');
  const g = d.lat.gpu, c = d.lat.cpu, runs = d.llm.runs.map((r) => r.seconds * 1000);
  const rows = [
    ['BM25 over all 28,953 chunks', '4 CPU cores', c.bm25_query.p50_ms, C.bm, 0],
    ['Embed the question (bge-small)', 'L4 GPU', g.embed_query.p50_ms, C.de, 0],
    ['Reranker, 20 pairs', 'L4 GPU', g.rerank_20.p50_ms, C.rr, 1],
    ['Reranker, 20 pairs', '4 CPU cores, no GPU', c.rerank_20.p50_ms, C.rr, 2],
    [`An LLM orders the same 20`, `${esc(d.llm.model.split(' ')[0])} · ${d.llm.runs.length} runs`, Math.min(...runs), '#c4511f', 3, Math.max(...runs)],
  ];
  const lo = Math.log10(0.1), hi = Math.log10(100000), pc = (ms) => (100 * (Math.log10(ms) - lo)) / (hi - lo);
  const lab = (ms) => (ms < 1 ? ms.toFixed(2) + ' ms' : ms < 1000 ? ms.toFixed(1) + ' ms' : (ms / 1000).toFixed(1) + ' s');
  el.innerHTML = `<div class="lexical-bars lexical-lat">${rows.map(([n, m, ms, col, s, mx]) => `<div class="lexical-bar lexical-tr" data-s="${s}"><div class="w">${n}<small>${m}</small></div><div class="trk"><i style="width:${pc(ms)}%;background:${col}"></i></div><div class="v">${mx ? lab(ms) + ' to ' + lab(mx) : lab(ms)}</div></div>`).join('')}
    <div class="lexical-bar" style="margin-top:2px"><div class="w"></div><div style="display:flex;justify-content:space-between;font:14.5px var(--mono);color:var(--ink-3)">${['0.1 ms', '1 ms', '10 ms', '100 ms', '1 s', '10 s', '100 s'].map((t) => `<span>${t}</span>`).join('')}</div><div></div></div></div>`;
  return { step(k) { show(el, k); } };
};
})();
