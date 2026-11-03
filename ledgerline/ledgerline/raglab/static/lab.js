/* The RAG Lab: settings, chunk viewer, live search, vector map, golden metrics, leaderboard. */
(() => {
'use strict';
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const pct = (x) => (x == null ? '–' : (100 * x).toFixed(1) + '%');
const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
                set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } } };
const pid = store.get('rl_pid') || Math.random().toString(36).slice(2, 12); store.set('rl_pid', pid);
async function api(path, body) {
  const r = await fetch(path, { method: body === undefined ? 'GET' : 'POST', headers: { 'Content-Type': 'application/json', 'X-Player': pid },
    body: body === undefined ? undefined : JSON.stringify(body) });
  let d = {}; try { d = await r.json(); } catch (e) { /* empty */ }
  if (!r.ok) throw new Error(d.detail || ('HTTP ' + r.status));
  return d;
}
function toast(msg) {
  let t = $('.toast'); if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.append(t); }
  t.textContent = msg; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 3600);
}

const KNOBS = [
  ['parser', 'Parser', 'Plain: a naive text dump (no headers, no OCR, Word tables dropped). Structured: layout-aware PDFs with headings and tables, header-aware rows, one service per unit, OCR for scans.', { plain: 'plain', structured: 'structured' }],
  ['chunker', 'Chunker', 'Fixed: token windows. Recursive: split on paragraphs, lines, sentences. Structure: whole sections, rows, services and e-mails, packed up to the size.', { fixed: 'fixed', recursive: 'recursive', structure: 'structure-aware' }],
  ['size', 'Chunk size', 'Tokens per chunk (o200k). Small chunks are precise; big ones carry context (and are cut at 512 tokens by most embedding models).', { 200: '200', 400: '400', 800: '800', 1200: '1,200' }],
  ['overlap', 'Overlap', 'How much of the previous chunk each chunk repeats, so a sentence cut at a boundary survives.', { 0: '0', 0.15: '15%' }],
  ['embed', 'Embedding model', 'Turns text into a vector. All five are open models run on the GPU.', { 'bge-small': 'bge-small (384)', 'bge-base': 'bge-base (768)', 'e5-small': 'e5-small (384)', 'gte-small': 'gte-small (384)', nomic: 'nomic v1.5 (768)' }],
  ['retrieval', 'Retrieval', 'Dense: nearest vectors in Chroma. BM25: exact words and codes. Hybrid: both, fused by reciprocal rank (RRF).', { dense: 'dense', bm25: 'BM25', hybrid: 'hybrid (RRF)' }],
  ['rerank', 'Reranker', 'A cross-encoder (bge-reranker-base) rereads the question with each of the top 20 candidates and reorders them.', { false: 'off', true: 'on' }],
  ['rewrite', 'Query rewriting', 'One LLM call rewrites the question into a search query before searching (recorded for the golden questions).', { false: 'off', true: 'on' }],
  ['k', 'Top-k', 'How many chunks go to the answer model.', { 3: '3', 5: '5', 10: '10' }],
];
let cfg = { parser: 'structured', chunker: 'structure', size: 400, overlap: 0, embed: 'bge-small', retrieval: 'hybrid', rerank: true, rewrite: false, k: 5 };
try { const s = JSON.parse(store.get('rl_cfg') || 'null'); if (s) cfg = { ...cfg, ...s }; } catch (e) { /* ignore */ }
let OPT = null, lastSearch = null, mapData = null, mapKey = '';
const PALETTE = ['#0b57d0', '#138a60', '#c4511f', '#7b3fd1', '#d93f87', '#0a8a9a', '#b8860b', '#5f6368', '#2a78d6', '#3c9d5d', '#e8710a', '#9334e6', '#1a73e8', '#a50e0e', '#795548'];
const cfgId = () => `${cfg.parser}-${cfg.chunker}-${cfg.size}-o${Math.round(cfg.overlap * 100)} · ${cfg.retrieval === 'bm25' ? '–' : cfg.embed} · ${cfg.retrieval} · rerank ${cfg.rerank ? 'on' : 'off'} · rewrite ${cfg.rewrite ? 'on' : 'off'} · k=${cfg.k}`;

function renderKnobs() {
  $('#knobs').innerHTML = KNOBS.map(([k, title, help, opts]) => `<div class="knob${k === 'embed' && cfg.retrieval === 'bm25' ? ' off' : ''}" data-k="${k}">
    <h4>${title}</h4><p>${help}</p><div class="pills">${Object.entries(opts).map(([v, l]) =>
      `<button type="button" class="pill${String(cfg[k]) === v ? ' on' : ''}" data-v="${v}">${l}</button>`).join('')}</div></div>`).join('');
  $('#cfgid').textContent = cfgId();
  $('#cfgnote').textContent = cfg.retrieval === 'bm25' ? '(BM25 uses no embedding model; the map shows bge-small)' : '';
}
$('#knobs').addEventListener('click', (e) => {
  const b = e.target.closest('.pill'); if (!b) return;
  const k = b.closest('.knob').dataset.k; let v = b.dataset.v;
  if (k === 'size' || k === 'k') v = +v; else if (k === 'overlap') v = +v; else if (k === 'rerank' || k === 'rewrite') v = v === 'true';
  cfg[k] = v; store.set('rl_cfg', JSON.stringify(cfg)); renderKnobs(); changed();
});
let tmr = null;
function changed() { clearTimeout(tmr); tmr = setTimeout(() => { loadMetrics(); loadChunks(); loadMap(); if (lastSearch) runSearch(lastSearch.q, true); }, 250); }

/* ---- chunks */
async function loadChunks() {
  const f = $('#filesel').value; if (!f) return;
  $('#chunksum').textContent = 'loading the index for this setting ...';
  try {
    const d = await api(`/api/chunks?config=${encodeURIComponent(JSON.stringify(cfg))}&file=${encodeURIComponent(f)}`);
    const tot = d.tokens.reduce((a, b) => a + b, 0) || 1;
    $('#chunksum').textContent = `${d.n} chunks · ${d.tokens.reduce((a, b) => a + b, 0).toLocaleString('en-GB')} tokens · ${d.chunking}${d.n > d.chunks.length ? ` (first ${d.chunks.length} shown)` : ''}`;
    $('#chunkbar').innerHTML = d.tokens.map((t) => `<i style="flex:${t / tot}" title="${t} tokens"></i>`).join('');
    $('#chunklist').innerHTML = d.chunks.map((c, i) => `<div class="chunk"><div class="h"><span>#${i + 1} · ${esc(c.cite)}</span><span class="t">${c.n_tokens} tok</span></div><pre>${esc(c.text)}</pre></div>`).join('');
  } catch (e) { $('#chunksum').textContent = e.message; $('#chunklist').innerHTML = ''; $('#chunkbar').innerHTML = ''; }
}
$('#filesel').addEventListener('change', loadChunks);

/* ---- search */
function latBars(r) {
  const t = r.timing_ms || {}; const rows = Object.entries(t);
  const max = Math.max(200, ...rows.map(([, v]) => v));
  const total = rows.reduce((a, [, v]) => a + v, 0);
  return `<div class="lat">${rows.map(([k, v]) => `<div class="bar"><span>${esc(k)}</span><span class="bw"><i style="width:${Math.max(1, 100 * v / max)}%"></i></span><span class="num">${v.toFixed(1)} ms</span></div>`).join('')}
    <div class="bar${total > 200 ? ' over' : ''}"><b>retrieval</b><span class="bw"><i style="width:${Math.min(100, 100 * total / max)}%"></i></span><b class="num">${total.toFixed(1)} ms</b></div></div>
    <p class="small muted">Measured inside the search on the GPU container (the 200 ms budget is the red line beyond the scale's 200). Waiting for the GPU behind other students: ${r.queue_ms} ms; loading this index from the volume: ${r.index_load_ms} ms; round trip from your browser: <span id="rt"></span>.</p>`;
}
async function runSearch(q, quiet) {
  if (!q) return;
  lastSearch = { q };
  const role = $('#role').value;
  if (!quiet) $('#result').innerHTML = '<p class="muted center">Searching ...</p>';
  const t0 = performance.now();
  try {
    const r = await api('/api/search', { question: q, config: cfg, role });
    const rt = performance.now() - t0;
    const g = r.golden;
    let html = '';
    if (r.note) html += `<p class="v warn">${esc(r.note)}</p>`;
    if (r.query !== q) html += `<div class="ref"><b>Rewritten query</b>${esc(r.query)}</div>`;
    html += latBars(r);
    if (g) {
      const nh = r.items.filter((x) => x.gold).length;
      html += `<div class="ref"><b>Golden question ${esc(g.id)} · ${esc(g.type.replace('_', ' '))} · expected: ${esc(g.expected)}</b>${esc(g.reference)}</div>`;
      html += g.gold_sources.length ? `<p class="small">Gold sources: ${g.gold_sources.map((s) => esc(s.file.split('/').pop()) + (s.page ? ` p.${s.page}` : '') + (s.row ? ` ${s.sheet ? s.sheet + ' ' : ''}row ${s.row}` : '')).join(' · ')} — <b>${nh ? `found ${nh} in your top ${r.items.length}` : `none in your top ${r.items.length}`}</b></p>`
        : '<p class="small muted">No retrievable gold source: this question tests abstaining or refusing.</p>';
    }
    html += `<div class="hits">${r.items.map((it) => `<div class="hit${it.gold ? ' gold' : ''}"><div class="h"><span class="rk">${it.rank}</span><span class="ct">${esc(it.cite)}</span>
      ${it.gold === true ? '<span class="v ok">gold source</span>' : ''}<span class="sc">score ${it.score}${it.dense != null && !isNaN(it.dense) ? ` · cos ${it.dense}` : ''}${it.bm25 != null ? ` · bm25 ${it.bm25}` : ''}</span></div>
      <pre>${esc(it.text)}</pre></div>`).join('') || '<p class="muted">Nothing retrieved.</p>'}</div>`;
    $('#result').innerHTML = html;
    const s = $('#rt'); if (s) s.textContent = `${rt.toFixed(0)} ms`;
    if (r.map && !r.map.error) drawMap(r.map);
    if (r.metrics) renderMetrics(r.metrics);
  } catch (e) { $('#result').innerHTML = `<p class="v warn">${esc(e.message)}</p>`; }
}
$('#askform').addEventListener('submit', (e) => { e.preventDefault(); runSearch($('#q').value.trim()); });
$('#goldsel').addEventListener('change', () => { const v = $('#goldsel').value; if (!v) return; const g = OPT.golden.find((x) => x.id === v); $('#q').value = g.question; if (g.role && $('#role').querySelector(`option[value="${g.role}"]`)) $('#role').value = g.role; runSearch(g.question); });

/* ---- map */
async function loadMap() {
  const key = `${cfg.parser}-${cfg.chunker}-${cfg.size}-${cfg.overlap}-${cfg.retrieval === 'bm25' ? 'bge-small' : cfg.embed}`;
  if (key === mapKey && mapData) { drawMap(lastSearch && lastSearch.map); return; }
  $('#mapnote').textContent = 'loading the map ...';
  try {
    mapData = await api(`/api/map?config=${encodeURIComponent(JSON.stringify(cfg))}`); mapKey = key;
    $('#legend').innerHTML = mapData.folders.map((f, i) => `<span><i style="background:${PALETTE[i % PALETTE.length]}"></i>${esc(f)}</span>`).join('');
    $('#mapnote').textContent = `${mapData.points.length.toLocaleString('en-GB')} of ${mapData.n_total.toLocaleString('en-GB')} chunks shown, embedded with ${mapData.model}. Two dimensions out of hundreds: neighbours in the real space can look far apart here.`;
    drawMap(null);
  } catch (e) { $('#mapnote').textContent = e.message; }
}
let lastMapQ = null;
function drawMap(mq) {
  if (mq) lastMapQ = mq;
  const q = mq || lastMapQ;
  const cv = $('#cv'); const ctx = cv.getContext('2d');
  const W = cv.width, H = cv.height; ctx.clearRect(0, 0, W, H);
  if (!mapData) return;
  const pts = mapData.points;
  let xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  if (q) { xs = xs.concat([q.query[0]], q.hits.map((h) => h[0])); ys = ys.concat([q.query[1]], q.hits.map((h) => h[1])); }
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const px = (x) => 20 + (W - 40) * (x - x0) / ((x1 - x0) || 1), py = (y) => H - 20 - (H - 40) * (y - y0) / ((y1 - y0) || 1);
  ctx.globalAlpha = 0.5;
  for (const p of pts) { ctx.fillStyle = PALETTE[p[2] % PALETTE.length]; ctx.beginPath(); ctx.arc(px(p[0]), py(p[1]), 2.2, 0, 6.29); ctx.fill(); }
  ctx.globalAlpha = 1;
  if (q) {
    ctx.strokeStyle = '#121317'; ctx.lineWidth = 2;
    for (const h of q.hits) { ctx.beginPath(); ctx.arc(px(h[0]), py(h[1]), 8, 0, 6.29); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(px(q.query[0]), py(q.query[1])); ctx.lineTo(px(h[0]), py(h[1])); ctx.globalAlpha = 0.25; ctx.stroke(); ctx.globalAlpha = 1; }
    const sx = px(q.query[0]), sy = py(q.query[1]);
    ctx.fillStyle = '#c4511f'; ctx.beginPath();
    for (let i = 0; i < 10; i++) { const r = i % 2 ? 6 : 15, a = -Math.PI / 2 + i * Math.PI / 5; ctx.lineTo(sx + r * Math.cos(a), sy + r * Math.sin(a)); }
    ctx.closePath(); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke();
  }
}

/* ---- metrics */
function renderMetrics(m) {
  if (!m) { $('#metricsbox').innerHTML = '<p class="muted center">No golden-set measurement for this setting yet (still being built, or pruned from the grid).</p>'; return; }
  const good = (x, t) => (x == null ? '' : x >= t ? 'good' : 'bad');
  const b = m.build || {}; const bm = b.model || {};
  let html = `<div class="stats">
    <div class="stat card"><span class="v2 ${good(m['recall@k'], 0.9)}">${pct(m['recall@k'])}</span><span class="l">recall@${cfg.k}: a gold source in the top ${cfg.k}</span></div>
    <div class="stat card"><span class="v2">${m.mrr == null ? '–' : m.mrr.toFixed(3)}</span><span class="l">MRR: 1 / rank of the first gold source</span></div>
    <div class="stat card"><span class="v2 ${m.under_budget ? 'good' : 'bad'}">${m.p95_ms} ms</span><span class="l">retrieval p95 (p50 ${m.p50_ms} ms); budget 200 ms</span></div>
    <div class="stat card"><span class="v2">#${m.rank}</span><span class="l">of ${m.of} measured settings by recall@${cfg.k}</span></div></div>`;
  html += `<div class="types">${Object.entries(m.by_type).map(([t, v]) => `<div class="bar"><span>${esc(t.replace('_', ' '))}</span><span class="bw"><i style="width:${100 * (v || 0)}%"></i></span><span>${pct(v)}</span></div>`).join('')}</div>`;
  html += `<p class="build">Index: ${(b.n_chunks || 0).toLocaleString('en-GB')} chunks of ~${b.tokens_mean} tokens${bm.embed_s != null ? `; embedding them took ${bm.embed_s} s on the GPU, adding them to Chroma ${bm.chroma_add_s} s` : ''}; whole build ${b.build_s_total} s; stored ${(((b.index_bytes || {}).chroma_all_models || 0) / 1e6).toFixed(0)} MB in Chroma for all five models. Coverage@${cfg.k} (share of all gold sources found): ${pct(m['coverage@k'])}. Machine: ${esc(b.machine || '')}.</p>`;
  if (m.answers) html += `<p class="build"><b>Answers measured for this setting</b> (gemini-3.8-flash): correct ${pct(m.answers.answer_correct)}, exact-fact ${pct(m.answers.fact_correct)}, citation ${pct(m.answers.citation_correct)}, $${m.answers.cost_per_q_usd} a question.</p>`;
  $('#metricsbox').innerHTML = html;
}
async function loadMetrics() {
  try { const d = await api('/api/metrics', { config: cfg }); renderMetrics(d.metrics); } catch (e) { $('#metricsbox').innerHTML = `<p class="v warn">${esc(e.message)}</p>`; }
}

/* ---- leaderboard */
async function loadBoard() {
  try {
    const d = await api('/api/leaderboard');
    $('#boardbox').innerHTML = d.rows.length ? `<div class="lbwrap"><table class="lb"><thead><tr><th>#</th><th>Name</th><th>recall@5</th><th>Setting</th><th>p95</th></tr></thead><tbody>${d.rows.map((r, i) => `<tr class="${r.under_budget ? '' : 'over'}"><td class="n">${i + 1}</td><td>${esc(r.name)}</td><td class="n"><b>${pct(r['recall@5'])}</b></td><td><code>${esc(r.config.id)}</code></td><td class="n">${r.p95_ms} ms${r.under_budget ? '' : ' (over)'}</td></tr>`).join('')}</tbody></table></div>`
      : '<p class="muted center">No one has submitted yet.</p>';
  } catch (e) { $('#boardbox').innerHTML = `<p class="v warn">${esc(e.message)}</p>`; }
}
$('#submitbtn').addEventListener('click', async () => {
  const name = (store.get('rl_name') || $('#name').value || '').trim();
  if (!name) { toast('Type your name at the top first.'); $('#name').focus(); return; }
  try { const d = await api('/api/leaderboard', { name, config: cfg });
    $('#submitnote').textContent = d.saved ? `Saved: recall@5 ${pct(d.entry['recall@5'])}, p95 ${d.entry.p95_ms} ms.` : `Your earlier setting is still your best (${pct(d.best['recall@5'])}).`;
    loadBoard();
  } catch (e) { toast(e.message); }
});
$('#joinform').addEventListener('submit', (e) => { e.preventDefault(); const n = $('#name').value.trim(); if (n) { store.set('rl_name', n); $('#navname').textContent = n; } location.hash = '#settings'; });

/* ---- start */
(async () => {
  renderKnobs();
  const n = store.get('rl_name'); if (n) { $('#name').value = n; $('#navname').textContent = n; }
  try {
    OPT = await api('/api/options');
    $('#filesel').innerHTML = OPT.files.map((f) => `<option value="${esc(f)}">${esc(f)}</option>`).join('');
    $('#role').innerHTML = Object.entries(OPT.roles).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');
    $('#goldsel').innerHTML = '<option value="">choose one of 224 ...</option>' + OPT.golden.map((g) => `<option value="${g.id}">${esc(g.id)} · ${esc(g.type)} · ${esc(g.question.slice(0, 80))}</option>`).join('');
    $('#chips').innerHTML = OPT.examples.map((x) => `<button type="button" class="pill" data-q="${esc(x.question)}">${esc(x.question)}</button>`).join('');
    $('#chips').addEventListener('click', (e) => { const b = e.target.closest('.pill'); if (b) { $('#q').value = b.dataset.q; runSearch(b.dataset.q); } });
    if (OPT.flags && OPT.flags.enabled === false) toast(OPT.flags.reason || 'The lab is paused.');
  } catch (e) { toast('The lab is waking up: ' + e.message); }
  loadMetrics(); loadChunks(); loadMap(); loadBoard();
  setInterval(loadBoard, 20000);
  const links = [...document.querySelectorAll('.nav a')];
  window.addEventListener('scroll', () => {
    const h = document.documentElement; $('#prog').style.width = `${100 * h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)}%`;
    let cur = null; for (const a of links) { const s = $(a.getAttribute('href')); if (s && s.getBoundingClientRect().top < 140) cur = a; }
    links.forEach((a) => a.classList.toggle('on', a === cur));
  }, { passive: true });
})();
})();
