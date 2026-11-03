/* Live figures for Lecture 3 · The Memory (v4), part 2: the LLM Wiki and the race. Loaded after figs.js, before plates.js.
   Same rule: every number and every line of text comes from window.L3 (figdata.js). */
(() => {
const FIGS = window.FIGS;
const { esc, fmt, pct, get, reveal, need, ms, stop } = window.L3u;

/* ======================= a real Wikipedia page: one part lit per click, mapped to the wiki ======================= */
/* data-boxes: "x,y,w,h|…" in % of the screenshot; the mapping list is the slide's .wp-map li elements */
FIGS.wikipedia = (el) => {
  const boxes = (el.dataset.boxes || '').split('|').map((b) => b.split(',').map(Number));
  el.innerHTML = `<img src="${esc(el.dataset.img)}" alt="${esc(el.dataset.alt || '')}">${boxes.map((b, i) => `<div class="wp-lit" data-i="${i + 1}" style="left:${b[0]}%;top:${b[1]}%;width:${b[2]}%;height:${b[3]}%"></div>`).join('')}<div class="wp-dim"></div>`;
  const map = el.closest('.slide').querySelectorAll('.wp-map li');
  return { step(k) {
    el.querySelectorAll('.wp-lit').forEach((x) => x.classList.toggle('on', +x.dataset.i === k));
    el.querySelector('.wp-dim').classList.toggle('on', k > 0 && k <= boxes.length);
    map.forEach((li, i) => { li.classList.toggle('on', i + 1 === k); li.classList.toggle('off', k > 0 && i + 1 !== k && i + 1 > k); });
  } };
};

/* ======================= a real page of Northbridge's wiki, rendered from its markdown ======================= */
function mdInline(s) {
  return esc(s).replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, '<a class="wl">$2</a>').replace(/\[\[([^\]]+)\]\]/g, '<a class="wl">$1</a>')
    .replace(/\[\^(r\d+)\]/g, '<sup class="wrf">$1</sup>').replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/`([^`]+)`/g, '<code>$1</code>');
}
function md(body) {
  const out = []; let tbl = null, ul = null;
  const flush = () => { if (tbl) { out.push(`<table class="wk-t">${tbl.join('')}</table>`); tbl = null; } if (ul) { out.push(`<ul>${ul.join('')}</ul>`); ul = null; } };
  body.split('\n').forEach((l) => {
    if (/^\|/.test(l)) { if (/^\|[\s|:-]+\|$/.test(l)) return; const cells = l.split('|').slice(1, -1).map((c) => c.trim()); if (cells.every((c) => !c)) return; (tbl = tbl || []).push(`<tr>${cells.map((c) => `<td>${mdInline(c)}</td>`).join('')}</tr>`); return; }
    if (/^- /.test(l)) { (ul = ul || []).push(`<li>${mdInline(l.slice(2))}</li>`); return; }
    flush();
    if (/^## /.test(l)) out.push(`<h4 class="wk-h">${mdInline(l.slice(3))}</h4>`);
    else if (l.trim()) out.push(`<p>${mdInline(l)}</p>`);
  });
  flush();
  return out.join('');
}
FIGS.wikipage = (el) => {
  const P = get('wiki.page_brightcell'); if (!P) return need(el, 'the Brightcell wiki page.');
  const body = P.body.replace(/^\|[^\n]*\n\|[-| ]*\n(\|[^\n]*\n)+\n/, '').split('\n## Rate contracts')[0];   // the first (short) infobox duplicates the second; up to Certificates
  el.innerHTML = `<div class="wk"><div class="wk-fm" data-k="1"><b>front matter</b><pre>${esc(P.front)}</pre></div><div class="wk-b">${md(body)}</div></div>
    <div class="wk-path"><code>ledgerline/ledgerline/wiki_v4/pages/${esc(P.slug)}.md</code> · written by the ingest, unedited</div>`;
  const lead = el.querySelector('.wk-b p'), table = el.querySelector('.wk-t'), links = el.querySelectorAll('.wl'), refs = el.querySelectorAll('.wrf'), heads = el.querySelectorAll('.wk-h');
  return { step(k) {
    reveal(el, k >= 1 ? 9 : 0);
    el.classList.toggle('dimmed', k >= 2);
    [table, lead].forEach((x) => x && x.classList.remove('lt'));
    heads.forEach((x) => x.classList.toggle('lt', k === 4));
    if (k === 2) { table && table.classList.add('lt'); lead && lead.classList.add('lt'); }
    links.forEach((x) => x.classList.toggle('lt', k === 3));
    refs.forEach((x) => x.classList.toggle('lt', k === 5));
    el.querySelector('.wk-fm').classList.toggle('lt', k === 1);
  } };
};

/* ======================= one query's chain through the wiki (recorded) ======================= */
FIGS.chain = (el) => {
  const C = get('wiki.chain_emma.' + (el.dataset.m || 'wiki')); if (!C) return need(el, 'wiki_query_chains.json.');
  const steps = C.chain.filter((s) => s.step !== 'done');
  const calls = C.calls || [];
  el.innerHTML = `<div class="chn">${steps.map((s, i) => `<div class="chn-s ${s.step}" data-k="${s.step === 'index' ? 0 : (s.turn || 1)}"><span class="chn-k">${s.step === 'index' ? 'read' : 'open'}</span><code>${esc(s.what)}${s.step === 'page' ? '.md' : ''}</code></div>${i < steps.length - 1 ? '<span class="chn-a" data-k="1">→</span>' : ''}`).join('')}</div>
    <div class="chn-calls">${calls.map((c, i) => `<div class="card" data-k="${1 + i}"><span class="tag nt">model call ${c.turn} · ${fmt(c.tokens_in)} tokens in · ${c.llm_seconds.toFixed(1)} s</span><b>${esc(c.action)}</b>: ${esc(c.why)}</div>`).join('')}</div>
    <div class="chn-ans card af" data-k="${1 + calls.length}"><span class="tag af">then the shared answer step · ${C.answer_seconds.toFixed(1)} s</span>${esc(C.answer)}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= lint: what the wiki found wrong with Henrik's dump ======================= */
FIGS.lint = (el) => {
  const W = get('wiki.lint'); if (!W) return need(el, 'wiki_lint.json.');
  const mk = W.messiness.by_kind;
  const rows = Object.entries(mk).sort((a, b) => b[1].n - a[1].n);
  el.innerHTML = `<div class="ln2"><div><h4>The ${W.messiness.n} planted problems: found ${W.messiness.found}</h4>
    ${rows.map(([k, v]) => `<div class="lt-r"><span class="lt-l">${k.replace(/_/g, ' ')}</span><span class="lt-d">${Array.from({ length: v.n }, (_, i) => `<i class="${i < v.found ? 'y' : 'n'}"></i>`).join('')}</span><span class="lt-v">${v.found}/${v.n}</span></div>`).join('')}</div>
    <div data-k="1"><h4>${fmt(W.n_findings)} findings in ${W.seconds.total.toFixed(0)} s</h4>
    ${W.examples.map((x) => `<div class="lt-x"><span class="chip f">${esc(x.kind.replace(/_/g, ' '))}</span>${esc(x.detail)}</div>`).join('')}
    <p class="ftiny">By source: ${Object.entries(W.by_source).map(([k, v]) => `${k} ${v}`).join(' · ')}. Review calls: ${W.review.pages_reviewed} pages, $${W.review.usd.toFixed(2)}.</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= the race: the table ======================= */
const M = ['rag', 'wiki', 'hybrid', 'sections'];
const MN = { rag: 'RAG (BM25 + reranker)', wiki: 'Wiki · navigation', hybrid: 'Wiki · hybrid', sections: 'Wiki · sections only', cascade: 'Cascade (RAG, then hybrid)' };
FIGS.racetable = (el) => {
  const R = get('race'); if (!R) return need(el, 'race.json.');
  const T = R.targets, O = R.overall;
  const ok = (v, t, lo) => (v == null ? '' : (lo ? v <= t : v >= t) ? ' ok' : ' miss');
  const row = (m, o) => `<tr class="${m === 'rag' ? 'win' : ''}"><td>${MN[m]}</td>
    <td class="n c1${ok(o.answer_correct, T.answer_correct)}">${pct(o.answer_correct)}</td><td class="n c1">${pct(o.fact_correct)}</td><td class="n c1${ok(o.citation_correct, T.citation_correct)}">${pct(o.citation_correct)}</td>
    <td class="n c2${ok(o.retrieval_p95_s, T.retrieval_p95_s, 1)}">${ms(o.retrieval_p95_s)}</td><td class="n c2${ok(o.answer_p95_s, T.time_to_answer_p95_s, 1)}">${o.answer_p50_s.toFixed(1)} / ${o.answer_p95_s.toFixed(1)} s</td>
    <td class="n c3">$${o.cost_per_q_usd.toFixed(4)}</td><td class="n c3">${o.llm_calls_per_q ?? 1}</td></tr>`;
  el.innerHTML = `<table class="t rt3"><tr><th>Method</th><th class="c1">Judge</th><th class="c1">Exact facts</th><th class="c1">Citations</th><th class="c2">Search p95</th><th class="c2">Answer p50 / p95</th><th class="c3">$ / question</th><th class="c3">LLM calls</th></tr>
    ${M.map((m) => row(m, O[m])).join('')}
    <tr class="tgt"><td>Our targets</td><td class="n c1">≥ ${pct(T.answer_correct, 0)}</td><td class="n c1"></td><td class="n c1">≥ ${pct(T.citation_correct, 0)}</td><td class="n c2">≤ ${ms(T.retrieval_p95_s)}</td><td class="n c2">p95 ≤ ${T.time_to_answer_p95_s} s</td><td></td><td></td></tr></table>
    <p class="ftiny">${esc(R.what)}.</p>`;
  return { step(k) { el.classList.toggle('s1', k === 1); el.classList.toggle('s2', k === 2); el.classList.toggle('s3', k === 3); } };
};

/* ======================= accuracy against the wait ======================= */
FIGS.racescatter = (el) => {
  const R = get('race'); if (!R) return need(el, 'race.json.');
  const W = el.clientWidth || 900, H = el.clientHeight || 520, m = { l: 70, r: 30, t: 24, b: 60 };
  const pts = M.map((k) => ({ k, x: R.overall[k].answer_p50_s, y: R.overall[k].answer_correct, c: R.overall[k].cost_per_q_usd }))
    .concat([{ k: 'cascade', x: R.cascade.answer_p50_s, y: R.cascade.answer_correct, c: R.cascade.cost_per_q_usd }]);
  const xs = (v) => m.l + (v / 14) * (W - m.l - m.r), ys = (v) => H - m.b - ((v - 0.75) / 0.2) * (H - m.t - m.b);
  const col = { rag: '#0b57d0', wiki: '#7a5af5', hybrid: '#138a60', sections: '#9aa3b2', cascade: '#c4511f' };
  el.innerHTML = `<svg width="${W}" height="${H}">${[2, 4, 6, 8, 10, 12, 14].map((t) => `<line x1="${xs(t)}" x2="${xs(t)}" y1="${m.t}" y2="${H - m.b}" class="gl"/><text x="${xs(t)}" y="${H - m.b + 22}" class="ax" text-anchor="middle">${t} s</text>`).join('')}
    ${[0.8, 0.85, 0.9, 0.95].map((t) => `<line x1="${m.l}" x2="${W - m.r}" y1="${ys(t)}" y2="${ys(t)}" class="gl"/><text x="${m.l - 8}" y="${ys(t) + 5}" class="ax" text-anchor="end">${pct(t, 0)}</text>`).join('')}
    ${pts.map((p) => `<g data-k="${p.k === 'cascade' ? 1 : 0}"><circle cx="${xs(p.x)}" cy="${ys(p.y)}" r="${8 + Math.sqrt(p.c) * 90}" fill="${col[p.k]}" fill-opacity=".22" stroke="${col[p.k]}" stroke-width="2.5"/>
      <text x="${xs(p.x) > W * 0.6 ? xs(p.x) - 14 - Math.sqrt(p.c) * 90 : xs(p.x) + 14 + Math.sqrt(p.c) * 90}" y="${ys(p.y) + 6}" text-anchor="${xs(p.x) > W * 0.6 ? 'end' : 'start'}" class="ax" style="fill:${col[p.k]};font-weight:600">${MN[p.k]} · ${pct(p.y)} · $${p.c.toFixed(4)}</text></g>`).join('')}
    <text x="${(m.l + W - m.r) / 2}" y="${H - 14}" class="ax" text-anchor="middle">time to answer, p50 (search + answer)</text>
    <text x="18" y="${(m.t + H - m.b) / 2}" class="ax" transform="rotate(-90 18 ${(m.t + H - m.b) / 2})" text-anchor="middle">answer correct (judge)</text></svg>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= by question type: where each method wins ======================= */
FIGS.heat = (el) => {
  const B = get('race.by_type'); if (!B) return need(el, 'race by_type.');
  const types = Object.keys(B);
  const cell = (v) => `<td class="n hm" style="background:rgba(11,87,208,${Math.max(0, (v - 0.3) / 0.7) * 0.55})">${v == null ? '–' : Math.round(100 * v)}</td>`;
  el.innerHTML = `<table class="t hmt"><tr><th>Question type</th><th class="n">n</th>${M.map((m) => `<th class="n">${MN[m].replace(' (BM25 + reranker)', '')}</th>`).join('')}</tr>
    ${types.map((t) => { const vs = M.map((m) => B[t][m].answer_correct); const mx = Math.max(...vs); return `<tr data-t="${t}"><td>${t.replace(/_/g, ' ')}</td><td class="n">${B[t].rag.n}</td>${vs.map((v) => cell(v).replace('class="n hm"', `class="n hm${v === mx ? ' top' : ''}"`)).join('')}</tr>`; }).join('')}</table>
    <p class="ftiny">Judge score (%) by question type, the race's runs. Bold: the best method for that type.</p>`;
  const groups = { 1: ['procedure', 'table_lookup', 'version_conflict'], 2: ['permission', 'exact_code', 'service_field'], 3: ['multi_hop'] };
  return { step(k) { el.querySelectorAll('tr[data-t]').forEach((r) => r.classList.toggle('lt', (groups[k] || []).includes(r.dataset.t))); } };
};

/* ======================= Emma's question (or Q-0412), every method's answer, side by side ======================= */
FIGS.side = (el) => {
  const q = el.dataset.q || 'Q-EMMA';
  const E = get('race.examples.' + q); if (!E) return need(el, 'race examples.');
  let cur = 'rag';
  const draw = () => {
    const a = E[cur];
    el.innerHTML = `<div class="ctl">${M.map((m) => `<button class="${m === cur ? 'on' : ''}" data-m="${m}">${MN[m]}</button>`).join('')}</div>
      <div class="sd"><div class="sd-a">${esc(a.answer).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>')}</div>
      <div class="sd-s"><div class="sd-j ${a.judge ? 'ok' : 'no'}">${a.judge ? '✓ judge: correct' : '✗ judge: not correct'}</div>
      ${a.facts_missing && a.facts_missing.length ? `<div class="sd-k">Facts missing</div>${a.facts_missing.map((f) => `<span class="chip f">${esc(f)}</span>`).join(' ')}` : '<div class="sd-k">Every required fact is in the answer</div>'}
      <div class="sd-k">Search ${ms(a.retrieval_s)} · total ${a.total_s.toFixed(1)} s · $${a.cost_usd.toFixed(4)}</div>
      <div class="sd-k">What it read (first passages)</div><ol>${[...new Set(a.sources)].slice(0, 6).map((s) => `<li>${esc(s)}</li>`).join('')}</ol></div></div>`;
    el.querySelectorAll('[data-m]').forEach((b) => b.addEventListener('click', (e) => { stop(e); cur = b.dataset.m; draw(); }));
  };
  draw();
  return { step() {} };
};

/* ======================= did the 150-word cap matter? ======================= */
FIGS.cap = (el) => {
  const C = get('race.cap_150_vs_250'); if (!C) return need(el, 'cap_150_vs_250.');
  el.innerHTML = `<table class="t"><tr><th>Method</th><th class="n">150 words</th><th class="n">250 words</th><th class="n">change</th><th>Q-EMMA at 250 words: still missing</th></tr>
    ${M.map((m) => `<tr><td>${MN[m]}</td><td class="n">${pct(C[m].answer_correct[0])}</td><td class="n">${pct(C[m].answer_correct[1])}</td><td class="n">${(C[m].delta_answer_correct >= 0 ? '+' : '') + (100 * C[m].delta_answer_correct).toFixed(1)} pts</td>
      <td>${C[m].q_emma['250'].words} words · ${C[m].q_emma['250'].facts_missing.map((f) => `<span class="chip f">${esc(f)}</span>`).join(' ')}</td></tr>`).join('')}</table>`;
  return { step() {} };
};

/* ======================= Henrik's hand-over note (the dump's README), as he wrote it ======================= */
FIGS.note = (el) => {
  const n = get('readme.note'); if (!n) return need(el, 'README.md.');
  const ps = n.split(/\n\n+/).map((p) => p.replace(/^\*\*(.+)\*\*$/, '$1'));
  el.innerHTML = `<div class="letter"><div class="from">${esc(ps[0])}</div>${ps.slice(1).map((p, i) => `<p data-k="${i < 2 ? 0 : i < 4 ? 1 : 2}">${esc(p)}</p>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= the decision, as race.json records it ======================= */
FIGS.why = (el) => {
  const D = get('race.decision'); if (!D) return need(el, 'race decision.');
  el.innerHTML = `<ol class="why">${D.why.map((w, i) => `<li data-k="${i}">${esc(w)}</li>`).join('')}</ol>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= the withheld notice: permission questions before and after ======================= */
FIGS.withheld = (el) => {
  const W = get('race.withheld_notice'); if (!W) return need(el, 'withheld_notice.');
  el.innerHTML = `<div class="hbars">${M.map((m) => `<div class="wh-r"><span class="hz-l">${MN[m]}</span>
    <span class="hz-t"><i class="bf" style="width:${100 * W.per_method[m].permission_correct_before}%"></i></span><span class="hz-v">${pct(W.per_method[m].permission_correct_before, 0)}</span>
    <span class="hz-t" data-k="1"><i style="width:${100 * W.per_method[m].permission_correct_after}%"></i></span><span class="hz-v" data-k="1">${pct(W.per_method[m].permission_correct_after, 0)}</span></div>`).join('')}</div>
    <p class="ftiny">The ${W.permission_questions} permission questions, without and with the notice. It fires on ${W.fires_on.length} questions (${W.fires_by_type.permission} of them permission questions). Detector: ${esc(W.detector)}.</p>`;
  return { step(k) { reveal(el, k); } };
};
})();
