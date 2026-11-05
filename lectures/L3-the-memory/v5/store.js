/* Lecture 3 v5 · section `store`: where the vectors live. What a store keeps (Chroma, document D), metadata and filters,
   HNSW word by word, the production choice, and the engineer's checklist on our Qdrant Cloud cluster (latency included). Figures are FIGS.store_<fig>; every number, record, file size and
   result comes from window.L3V5.store (v5/store_data.js, written by experiments/v5_store_data.py from
   experiments/logs/v5_store*.json and hnsw_check.json). Source code shown on slides is in CODE below (it is code, not data).
   Each figure returns { step(k) }, k = the number of .step elements shown on its slide. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const S = () => (window.L3V5 && window.L3V5.store) || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const get = (path) => { let v = S(); for (const k of path.split('.')) v = v == null ? v : v[k]; return v; };
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('store-off', +x.dataset.k > k));
const hide = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('store-hide', +x.dataset.k > k));
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(store data)</span><div>${what}</div><div class="todo-s">Fills in from v5/store_data.js (experiments/v5_store_data.py).</div></div>`; return { step() {} }; };
const BASE = /\/v5\/[^/]*$/.test(location.pathname) ? '' : 'v5/';
const bytes = (b) => (b >= 1e6 ? (b / 1e6).toFixed(1) + ' MB' : b >= 1e3 ? (b / 1e3).toFixed(1) + ' KB' : b + ' B');
const ms = (v) => (v == null ? '–' : (+v >= 1000 ? fmt(Math.round(+v)) : +v >= 100 ? Math.round(+v) : (+v).toFixed(1)) + ' ms');
const short = (cite, n = 70) => { const s = String(cite || '').replace(/, § body$/, '').replace(/\.(eml|md)(,|$)/, '$2'); return s.length > n ? s.slice(0, n - 1) + '…' : s; };

/* ---- [data-st="path"] spans; formats: n, ms (value in ms), s2ms (value in s), mb (bytes), r2, r3, pct0, pct1 ---- */
function fill() {
  document.querySelectorAll('[data-st]').forEach((e) => {
    const v = get(e.dataset.st);
    if (v == null) { e.innerHTML = '<span class="todo-in">TODO(store)</span>'; return; }
    const f = e.dataset.f;
    e.textContent = f === 'mib' ? Math.round(v) + ' MiB' : f === 'n' ? fmt(v) : f === 'ms' ? ms(v) : f === 's2ms' ? ms(1000 * v) : f === 'mb' ? bytes(v)
      : f === 'r2' ? (+v).toFixed(2) : f === 'r3' ? (+v).toFixed(3) : f === 'pct0' ? Math.round(100 * v) + '%'
      : f === 'pct1' ? (100 * v).toFixed(1) + '%' : String(v);
  });
}
window.addEventListener('DOMContentLoaded', fill);
if (document.readyState !== 'loading') setTimeout(fill, 0);

/* ---- a tiny Python / JSON highlighter for code cards ---- */
const KW = /^(def|return|for|in|if|else|import|from|not|and|or|None|True|False|with|as|lambda|true|false|null)$/;
function hl(line) {
  const re = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d[\d_.]*\b)|([A-Za-z_]\w*)/g;
  let out = '', last = 0, m;
  while ((m = re.exec(line))) {
    out += esc(line.slice(last, m.index));
    if (m[1]) out += `<span class="store-cm">${esc(m[1])}</span>`;
    else if (m[2]) out += `<span class="store-st">${esc(m[2])}</span>`;
    else if (m[3]) out += `<span class="store-nu">${esc(m[3])}</span>`;
    else out += KW.test(m[4]) ? `<span class="store-kw">${m[4]}</span>` : esc(m[4]);
    last = re.lastIndex;
  }
  return out + esc(line.slice(last));
}

/* the source shown on slides: the course code and experiments/v5_store_cloud.py, abridged only by dropping lines */
const CODE = {
  chroma_query: ['col = idx.collection("bge-small")', 'q = rag.Embedder("bge-small").query(emma)          # 384 numbers',
    'col.query(query_embeddings=[q.tolist()], n_results=5,', '          include=["distances", "metadatas", "documents"])'],
  filter: ['# in words, as SQL would say it', 'WHERE superseded = false', '  AND confidential = false      -- Emma is not in HR', '',
    '# to Qdrant, sent with the query', '"filter": {"must_not": [', '  {"key": "superseded",   "match": {"value": true}},',
    '  {"key": "confidential", "match": {"value": true}}]}'],
  create: ['q = QdrantClient(url=os.environ["QDRANT_URL"],', '                 api_key=os.environ["QDRANT_API_KEY"])',
    'q.create_collection("northbridge_docs",', '    vectors_config={"dense": VectorParams(size=384, distance=Distance.COSINE)})', '',
    '# payload indexes BEFORE the upsert: filters run inside the HNSW search', 'for f in ("confidential", "superseded", "future"):',
    '    q.create_payload_index("northbridge_docs", f, field_schema="bool")', 'for f in ("folder", "doc_id", "file", "status"):',
    '    q.create_payload_index("northbridge_docs", f, field_schema="keyword")', '',
    '# BM25 inside the engine (Qdrant 1.20): a full-text index with BM25 scoring', 'q.create_payload_index("northbridge_docs", "text", field_schema=TextIndexParams(',
    '    type="text", tokenizer="word", lowercase=True, stopwords="english",', '    scoring=TextScoringParams(type="bm25")))'],
  search: ['emma_filter = Filter(must_not=[', '    FieldCondition(key="confidential", match=MatchValue(value=True))])', '',
    'q.query_points("northbridge", query=q_vec, using="dense",', '               query_filter=emma_filter, limit=10)'],
  hybrid: ['bm25 = TextQuery(text=TextQueryInput(query=question,', '                  scoring=Bm25Scoring(bm25=Bm25Params(k=1.2, b=0.75))))', '',
    'q.query_points("northbridge",', '    prefetch=[Prefetch(query=q_vec, using="dense", filter=emma_filter, limit=20),',
    '              Prefetch(query=bm25,  using="text",  filter=emma_filter, limit=20)],', '    query=RrfQuery(rrf=Rrf(k=60)),         # the same RRF as rag.rrf',
    '    query_filter=emma_filter, limit=10)'],
  alias: ['# the app always queries the alias "northbridge"', 'q.create_collection("northbridge_docs_v2", ...)        # new model, new vector size',
    '# ... re-embed and upsert all 28,953 chunks, run the golden set on v2 ...', 'q.update_collection_aliases(change_aliases_operations=[',
    '    DeleteAliasOperation(delete_alias=DeleteAlias(alias_name="northbridge")),', '    CreateAliasOperation(create_alias=CreateAlias(',
    '        collection_name="northbridge_docs_v2", alias_name="northbridge"))])   # one atomic switch'],
};
FIGS.store_code = (el) => {
  const lines = CODE[el.dataset.code] || ['# missing code ' + el.dataset.code];
  const groups = (el.dataset.hl || '').split(';').map((g) => new Set(g.split(',').filter(Boolean).flatMap((r) => { const [a, b] = r.split('-').map(Number); return Array.from({ length: (b || a) - a + 1 }, (_, i) => a + i); })));
  el.classList.add('store-code');
  el.innerHTML = (el.dataset.title ? `<span class="h">${esc(el.dataset.title)}</span>` : '') + lines.map((l, i) => `<span class="l" data-i="${i + 1}">${hl(l) || ' '}</span>`).join('');
  return { step(k) { const g = groups[k] || new Set(); el.querySelectorAll('.l').forEach((x) => x.classList.toggle('hl', g.has(+x.dataset.i))); } };
};

/* ======================= what a store keeps: one record (id, text, metadata, vector), an index, a folder ======================= */
const vcol = (v) => { const a = Math.min(1, Math.abs(v) / 0.07); return v >= 0 ? `rgba(11,87,208,${0.25 + 0.75 * a})` : `rgba(196,81,31,${0.25 + 0.75 * a})`; };
FIGS.store_keeps = (el) => {
  const r = get('local.D.record'), dump = get('local.dump'); if (!r || !dump) return need(el, 'v5_store_local.json → D.record, dump');
  // the stored text keeps the PDF's line breaks; join wrapped lines so each clause reads as one paragraph
  const joined = r.document.split('\n').reduce((a, l) => { if (a.length && !/^(\[|\d+(\.\d+)*\.?\s)/.test(l)) a[a.length - 1] += ' ' + l; else a.push(l); return a; }, []).join('\n');
  const doc = esc(joined).replace(/(6\.2 Lithium-cell[\s\S]*?counts as no certificate\.)/, '<mark>$1</mark>').replace(/(6\.4 Prefer[\s\S]*?lithium-cell part\.)/, '<mark>$1</mark>');
  const m = r.metadata;
  const keys = ['doc_id', 'file', 'folder', 'fmt', 'superseded', 'future', 'confidential'];
  const total = Object.values(dump.counts || {}).reduce((a, b) => a + b, 0);
  el.classList.add('store-keeps');
  el.innerHTML = `<div class="folder" data-k="4"><span class="tab">store_D/chroma/ &nbsp;·&nbsp; a folder on disk</span></div>
    <div class="rec">
      <div class="r" data-k="0"><span class="k">id</span><pre>"${esc(r.id)}"   <span style="color:var(--ink-3)">· ${esc(r.cite)}</span></pre></div>
      <div class="r" data-k="0"><span class="k">text<small>what was embedded</small></span><pre class="doc">${doc}</pre></div>
      <div class="r" data-k="1"><span class="k">metadata<small>fields to filter on</small></span><div class="meta">${keys.filter((k) => k in m).map((k) => `<span class="${k === 'confidential' || k === 'superseded' ? 'hot' : ''}"><b>${k}</b> ${esc(JSON.stringify(m[k]))}</span>`).join('')}</div></div>
      <div class="r" data-k="2"><span class="k">vector<small>${r.embedding_len} numbers, length ${(+r.embedding_norm).toFixed(2)}</small></span><div class="vec">${r.embedding_first.map((v) => `<i style="background:${vcol(v)}">${v.toFixed(4)}</i>`).join('')}<em>… ${r.embedding_len - r.embedding_first.length} more</em></div></div>
    </div>
    <div class="idx" data-k="3"><b>+ an index for fast search</b>
      <svg viewBox="0 0 360 150" width="360" height="150">${(() => { const P = [[30, 40], [80, 20], [120, 70], [60, 110], [170, 30], [200, 100], [250, 55], [300, 25], [320, 110], [140, 130], [230, 135]]; const E = [[0, 1], [0, 3], [1, 2], [1, 4], [2, 3], [2, 5], [4, 6], [5, 6], [6, 7], [6, 8], [5, 9], [3, 9], [9, 10], [8, 10], [2, 4]]; return E.map(([a, b]) => `<line x1="${P[a][0]}" y1="${P[a][1]}" x2="${P[b][0]}" y2="${P[b][1]}" stroke="#b7c7df" stroke-width="2"/>`).join('') + P.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="7" fill="#7f9cc4"/>`).join(''); })()}</svg>
      <p>Links between nearby vectors (HNSW), so a search does not read every row. More on it in a moment.</p>
      <p class="n">One record per chunk: <b>15</b> for D, <b>${fmt(total)}</b> for the whole dump.</p></div>
    <div class="sizes" data-k="4">On disk, the whole dump in Chroma takes <b>${bytes(dump.bytes_total)}</b>. The vectors alone are <b>${bytes(dump.raw_vector_bytes)}</b>; the rest is text, metadata and the index.</div>`;
  return { step(k) { hide(el, k); } };
};

/* one chunk's payload on our cluster (point 106 = §6 of D), each field with what it means */
const MEANS = { doc_id: 'which document', version: 'which edition', effective: 'in force from', status: 'what the file says it is',
  superseded: 'replaced by a newer version?', future: 'not yet in force?', confidential: 'HR only?', audience: 'who may read it', file: 'where it came from' };
FIGS.store_payload = (el) => {
  const p = get('latency.eu.facts.point_106'); if (!p) return need(el, 'v5_store_latency.json → eu.facts.point_106');
  el.classList.add('store-pay');
  el.innerHTML = `<div class="h">Point ${p.id} on our cluster = §6 of D <span>· its payload, as stored</span></div>` +
    Object.keys(MEANS).map((k) => `<div class="r"><code>${k}</code><span class="v${typeof p[k] === 'boolean' ? ' b' : ''}">${esc(typeof p[k] === 'string' ? '"' + (k === 'file' ? short(p[k].replace(/^01_policies\//, '…/'), 40) : p[k]) + '"' : JSON.stringify(p[k]))}</span><span class="m">${MEANS[k]}</span></div>`).join('');
  return { step() {} };
};

/* the status values that occur in our payloads (a facet over the collection), and the three flags */
FIGS.store_status = (el) => {
  const f = get('latency.eu.facts'); if (!f || !f.status_values) return need(el, 'v5_store_latency.json → eu.facts.status_values');
  const sv = f.status_values.filter((x) => x.value).concat(f.status_values.filter((x) => !x.value));
  el.classList.add('store-stat');
  el.innerHTML = `<div class="ln"><span class="lab">status, in the files’ own words</span>${sv.map((x) => `<span class="chip${x.value === 'SUPERSEDED' ? ' o' : x.value ? '' : ' nil'}"><b>${x.value ? esc(x.value) : 'nothing stated'}</b> ${fmt(x.count)}</span>`).join('')}</div>
    <div class="ln"><span class="lab">flags the parser sets</span><span class="chip o"><b>superseded = true</b> ${fmt(f.counts.superseded)} chunks: status SUPERSEDED, or the file sits in an old/ or _legacy folder</span><span class="chip"><b>future = true</b> ${fmt(f.counts.future)}</span><span class="chip cf"><b>confidential = true</b> ${fmt(f.counts.confidential)}</span></div>`;
  return { step() {} };
};

/* the checklist cards: row two fades in on the click */
FIGS.store_ck = (el) => ({ step(k) { reveal(el, k); } });

/* ======================= ranked results (Chroma or Qdrant) ======================= */
function resList(rows, opts = {}) {
  const gold = opts.gold;
  return rows.slice(0, opts.n || rows.length).map((x, i) => {
    const conf = x.confidential, old = x.superseded, g = gold && String(x.cite || '').includes(gold);
    const val = x.similarity != null ? (+x.similarity).toFixed(3) : x.score != null ? (+x.score).toFixed(opts.d || 3) : '';
    const fl = opts.flag && String(x.cite || '').includes(opts.flag) ? ' fl' : '';
    return `<div class="it${g ? ' gold' : ''}${old ? ' old' : ''}${conf ? ' conf' : ''}${fl}" data-k="${opts.kOf ? opts.kOf(i) : 0}"><span class="n">${i + 1}</span><span class="ct">${esc(short(x.cite, opts.w || 74))}</span><span class="tgs">${x.says ? `<span class="tg s">says ${esc(x.says)}</span>` : ''}${g ? '<span class="tg g">§6 of D</span>' : ''}${old ? '<span class="tg o">superseded</span>' : ''}${conf ? '<span class="tg cf">HR confidential</span>' : ''}</span><span class="v">${val}</span></div>`;
  }).join('');
}
FIGS.store_res = (el) => {
  const rows = get(el.dataset.path); if (!rows) return need(el, el.dataset.path);
  const n = +(el.dataset.n || rows.length), k1 = +(el.dataset.k1 || 99);
  const t = get(el.dataset.ms || '__none');
  const [flag, fk] = (el.dataset.flag || '').split('|');
  el.innerHTML = `<div class="store-res">${el.dataset.title ? `<h4>${esc(el.dataset.title)}</h4>` : ''}${resList(rows, { n, gold: el.dataset.gold, w: +(el.dataset.w || 74), kOf: (i) => (i >= k1 ? 1 : 0), d: +(el.dataset.d || 3), flag })}${t != null ? `<div class="ms">${esc(el.dataset.msl || 'one query')}: ${ms(t)}</div>` : ''}</div>`;
  return { step(k) { (el.dataset.mode === 'hide' ? hide : reveal)(el, k - (+el.dataset.k0 || 0)); el.querySelectorAll('.it.fl').forEach((x) => x.classList.toggle('on', k >= +(fk || 99))); } };
};

/* ======================= bars ======================= */
FIGS.store_bars = (el) => {
  // data-rows="label|path|max|unit;…"  unit: ms | pct | n ; class prefix "b:" draws an ember bar, "hi:" highlights
  const rows = (el.dataset.rows || '').split(';').filter(Boolean).map((r) => r.split('|'));
  const have = rows.some(([, p]) => get(p) != null); if (!have) return need(el, 'bars: ' + rows.map((r) => r[1]).join(', '));
  el.innerHTML = `<div class="store-bars">${rows.map(([lab, p, mx, unit, kk], i) => {
    const v = get(p); const cls = lab.startsWith('b:') ? 'b' : lab.startsWith('hi:') ? 'hi' : ''; const l = lab.replace(/^(b|hi):/, '');
    const w = v == null ? 0 : Math.min(100, 100 * v / +mx);
    const txt = v == null ? 'pending' : unit === 'ms' ? ms(v) : unit === 's' ? ms(1000 * v) : unit === 'pct' ? (100 * v).toFixed(1) + '%' : fmt(v);
    return `<div class="row ${cls}" data-k="${kk || 0}"><span class="l">${esc(l)}</span><span class="t"><i style="width:${w}%"></i></span><span class="v">${txt}</span></div>`;
  }).join('')}${el.dataset.cap ? `<div class="cap2">${esc(el.dataset.cap)}</div>` : ''}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= HNSW word by word: a toy graph searched by the real greedy rule =======================
   k0 the points · k1 small world (near + long links) · k2 navigable (a greedy walk on that one layer) ·
   k3 hierarchical (three layers; the walk starts at the top). The toy is not data: 42 random points, a fixed seed. */
function rng(seed) { return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
FIGS.store_hnsw = (el) => {
  const NS = 'http://www.w3.org/2000/svg';
  const W = +(el.dataset.w || 900), H = 640;
  const N = 42, Q = [0.74, 0.62];
  const d2 = (a, b) => (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2;
  const build = (seed) => {
    const R = rng(seed), pts = Array.from({ length: N }, () => [0.04 + 0.92 * R(), 0.08 + 0.84 * R()]);
    const order = pts.map((_, i) => i).sort(() => R() - 0.5);
    const lvl = new Array(N).fill(0); order.slice(0, 12).forEach((i) => (lvl[i] = 1)); order.slice(0, 3).forEach((i) => (lvl[i] = 2));
    const nbr = {}, long = [];
    for (let L = 0; L <= 2; L++) { // each point's nearest within its layer (3 at the bottom, 2 above), made undirected
      const ids = pts.map((_, i) => i).filter((i) => lvl[i] >= L);
      nbr[L] = {}; ids.forEach((i) => (nbr[L][i] = new Set()));
      ids.forEach((i) => ids.filter((j) => j !== i).sort((a, b) => d2(pts[i], pts[a]) - d2(pts[i], pts[b])).slice(0, L === 0 ? 3 : 2).forEach((j) => { nbr[L][i].add(j); nbr[L][j].add(i); }));
    }
    for (let t = 0; long.length < 4 && t < 500; t++) { const a = Math.floor(R() * N), b = Math.floor(R() * N); if (a !== b && d2(pts[a], pts[b]) > 0.3 && !nbr[0][a].has(b)) { nbr[0][a].add(b); nbr[0][b].add(a); long.push([a, b]); } }
    const walk = (L, cur, path) => { for (;;) { let best = cur; nbr[L][cur].forEach((j) => { if (d2(pts[j], Q) < d2(pts[best], Q)) best = j; }); if (best === cur) return cur; cur = best; path.push([L, cur]); } };
    const entry = order.slice(0, 3).sort((a, b) => d2(pts[b], Q) - d2(pts[a], Q))[0];
    const flat = [[0, entry]]; const fEnd = walk(0, entry, flat);
    let cur = entry; const path = [];
    for (let L = 2; L >= 0; L--) { path.push([L, cur]); cur = walk(L, cur, path); }
    const exact = pts.map((_, i) => i).sort((a, b) => d2(pts[a], Q) - d2(pts[b], Q))[0];
    const isLong = (a, b) => long.some(([x, y]) => (x === a && y === b) || (x === b && y === a));
    const usesLong = flat.some((p, i) => i && isLong(flat[i - 1][1], p[1]));
    const hops = [0, 1, 2].map((L) => path.filter((p) => p[0] === L).length - 1);
    return { pts, lvl, nbr, long, flat, fEnd, path, cur, exact, entry, usesLong, hops, isLong };
  };
  let G = null;
  for (let seed = 1; seed < 2000 && !G; seed++) { const g = build(seed); if (g.cur === g.exact && g.fEnd === g.exact && g.flat.length > 5 && g.hops.every((h) => h >= 1) && g.usesLong && g.hops[0] + 2 <= g.flat.length - 1) G = g; }
  G = G || build(4);
  const { pts, lvl, nbr, long, flat, path, cur, hops, isLong } = G;
  const dia = (x, y, r = 10) => `<path d="M${x} ${y - r} l${r} ${r} l${-r} ${r} l${-r} ${-r}z" fill="#c4511f"/>`;
  let h = '';
  // ---- the flat view: one layer, large (k0–k2)
  { const pw = W - 230, ph = 400, skew = 110, x0 = 50, y0 = 30;
    const P = (p) => [x0 + p[0] * pw + (1 - p[1]) * skew, y0 + p[1] * ph];
    const c = [P([0, 0]), P([1, 0]), P([1, 1]), P([0, 1])];
    h += `<g data-r="0-2"><polygon points="${c.map((p) => p.join(',')).join(' ')}" fill="#eef4fd" stroke="#c9d6ea"/>`;
    h += '<g data-k="1">';
    Object.entries(nbr[0]).forEach(([i, set]) => set.forEach((j) => { if (+i < j) { const a = P(pts[i]), b = P(pts[j]); const lg = isLong(+i, j); h += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="${lg ? '#d08a1e' : '#b7c7df'}" stroke-width="${lg ? 2.4 : 1.4}"${lg ? ' stroke-dasharray="7 5"' : ''}/>`; } }));
    h += '</g>';
    pts.forEach((p) => { const a = P(p); h += `<circle cx="${a[0]}" cy="${a[1]}" r="5.5" fill="#7f9cc4"/>`; });
    const q = P(Q); h += dia(q[0], q[1], 11) + `<text x="${q[0] + 16}" y="${q[1] + 5}" font-size="16" fill="#c4511f" font-weight="600">the question</text>`;
    h += '<g data-k="2">';
    for (let t = 1; t < flat.length; t++) { const A = P(pts[flat[t - 1][1]]), B = P(pts[flat[t][1]]); h += `<line x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}" stroke="#0b57d0" stroke-width="3.4" stroke-linecap="round"/>`; }
    flat.forEach(([, i]) => { const a = P(pts[i]); h += `<circle cx="${a[0]}" cy="${a[1]}" r="7.5" fill="#0b57d0" stroke="#fff" stroke-width="2"/>`; });
    const st = P(pts[flat[0][1]]); h += `<text x="${st[0]}" y="${st[1] - 16}" font-size="16" fill="#0b57d0" font-weight="600" text-anchor="middle">start</text>`;
    const e = P(pts[cur]); h += `<circle cx="${e[0]}" cy="${e[1]}" r="13" fill="none" stroke="#138a60" stroke-width="3"/>`;
    h += '</g>';
    h += `<g data-k="1"><line x1="60" y1="${y0 + ph + 52}" x2="100" y2="${y0 + ph + 52}" stroke="#b7c7df" stroke-width="2"/><text x="110" y="${y0 + ph + 58}" font-size="16" fill="#45474d">near links: each point to its 3 nearest</text>
      <line x1="440" y1="${y0 + ph + 52}" x2="480" y2="${y0 + ph + 52}" stroke="#d08a1e" stroke-width="2.4" stroke-dasharray="7 5"/><text x="490" y="${y0 + ph + 58}" font-size="16" fill="#45474d">${long.length} long links</text></g>`;
    h += `<text data-k="2" x="60" y="${y0 + ph + 92}" font-size="17" fill="#0b57d0" font-weight="600">Greedy walk: ${flat.length - 1} hops from the start to the nearest point (green), then no neighbour is closer.</text>`;
    h += '</g>'; }
  // ---- the layered view (k3)
  { const pw = W - 300, ph = 116, skew = 90, gap = 170, x0 = 150, y0 = 16;
    const P = (L, p) => [x0 + p[0] * pw + (1 - p[1]) * skew, y0 + (2 - L) * gap + p[1] * ph];
    const counts = [0, 1, 2].map((L) => lvl.filter((v) => v >= L).length);
    h += '<g data-r="3-9">';
    for (let L = 2; L >= 0; L--) {
      const c = [P(L, [0, 0]), P(L, [1, 0]), P(L, [1, 1]), P(L, [0, 1])];
      h += `<polygon points="${c.map((p) => p.join(',')).join(' ')}" fill="${L === 0 ? '#eef4fd' : '#f5f8fd'}" stroke="#c9d6ea"/>`;
      h += `<text x="10" y="${y0 + (2 - L) * gap + ph / 2 - 4}" font-size="17" font-weight="600" fill="#45474d">Layer ${L}</text><text x="10" y="${y0 + (2 - L) * gap + ph / 2 + 17}" font-size="14" fill="#6b6e76">${counts[L]} points</text><text x="10" y="${y0 + (2 - L) * gap + ph / 2 + 36}" font-size="14" fill="#6b6e76">${L === 2 ? 'motorways' : L === 1 ? 'main roads' : 'local roads'}</text>`;
      Object.entries(nbr[L]).forEach(([i, set]) => set.forEach((j) => { if (+i < j) { const a = P(L, pts[i]), b = P(L, pts[j]); h += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="${L === 0 && isLong(+i, j) ? '#e2c08a' : '#b7c7df'}" stroke-width="1.2"/>`; } }));
      pts.forEach((p, i) => { if (lvl[i] >= L) { const a = P(L, p); h += `<circle cx="${a[0]}" cy="${a[1]}" r="${L ? 5.5 : 4.5}" fill="#7f9cc4"/>`; } });
      const q = P(L, Q); h += dia(q[0], q[1], 8);
    }
    for (let t = 1; t < path.length; t++) {
      const [La, a] = path[t - 1], [Lb, b] = path[t]; const A = P(La, pts[a]), B = P(Lb, pts[b]);
      h += La === Lb ? `<line x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}" stroke="#0b57d0" stroke-width="3.2" stroke-linecap="round"/>` : `<line x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}" stroke="#0b57d0" stroke-width="1.6" stroke-dasharray="5 5"/>`;
    }
    path.forEach(([L, i]) => { const a = P(L, pts[i]); h += `<circle cx="${a[0]}" cy="${a[1]}" r="7" fill="#0b57d0" stroke="#fff" stroke-width="2"/>`; });
    const e = P(0, pts[cur]); h += `<circle cx="${e[0]}" cy="${e[1]}" r="12" fill="none" stroke="#138a60" stroke-width="3"/>`;
    const st = P(2, pts[path[0][1]]); h += `<text x="${st[0] - 12}" y="${st[1] - 12}" font-size="15" fill="#0b57d0" font-weight="600" text-anchor="end">start</text>`;
    h += `<text x="10" y="${y0 + 2 * gap + ph + 62}" font-size="17" fill="#0b57d0" font-weight="600">From the top: ${hops[2]} hop on layer 2, ${hops[1]} on layer 1, then ${hops[0]} at the bottom (the flat walk needed ${flat.length - 1}).</text>`;
    h += '</g>'; }
  const s = document.createElementNS(NS, 'svg'); s.setAttribute('width', W); s.setAttribute('height', H); s.setAttribute('viewBox', `0 0 ${W} ${H}`);
  s.innerHTML = h;
  el.classList.add('store-hn');
  el.innerHTML = ''; el.appendChild(s);
  return { step(k) {
    el.querySelectorAll('[data-r]').forEach((x) => { const [a, b] = x.dataset.r.split('-').map(Number); x.classList.toggle('store-hide', k < a || k > b); });
    hide(el, k);
  } };
};

/* ======================= round-trip levers: before and after, measured ======================= */
FIGS.store_levers = (el) => {
  const L = get('latency'); if (!L || !L.suite_default_region) return need(el, 'v5_store_latency.json (run v5_store_latency.py and ::levers)');
  const cloud = (x) => String(x || '').replace('CLOUD_PROVIDER_', '');
  const us = L.suite_default_region.rest, eu = L.suite_eu;
  const rows = [
    ['Run the app next to the store', `The round trip alone. After: Modal’s EU region (${cloud(L.eu.modal_cloud)} ${L.eu.modal_region}); Frankfurt itself is not offered. Another EU run (${cloud(eu.modal_cloud)} ${eu.modal_region}): ${ms(eu.grpc.rtt.p50)}.`,
      ['from the US', L.default_region.rtt.p50], ['from the EU', L.eu.rtt.p50]],
    ['Keep one connection open', 'A new connection per question repeats the handshake: about two extra trips. From the US, REST.',
      ['new client per question', us.reconnect_per_question.p50], ['one client, kept open', us.hybrid_payload_cite.p50]],
    ['One hybrid request, not two searches', 'Dense, then BM25, then RRF in our code, against one request with RRF on the server. From the US.',
      ['two requests', us.two_calls_client_rrf.p50], ['one request', us.hybrid_payload_cite.p50]],
    ['Ten questions in one call', 'Ten hybrid requests one after another, against one query_batch_points call. From the US.',
      ['ten calls', us.ten_sequential.p50], ['one batch call', us.ten_one_batch.p50]],
    ['gRPC instead of REST, near the store', `From the EU (${cloud(eu.modal_cloud)} ${eu.modal_region}), one hybrid request. From the US the two were level (${ms(us.hybrid_payload_cite.p50)} and ${ms(L.suite_default_region.grpc.hybrid_payload_cite.p50)}): the trip hides it.`,
      ['REST', eu.rest.hybrid_payload_cite.p50], ['gRPC', eu.grpc.hybrid_payload_cite.p50]],
  ];
  el.classList.add('store-lev');
  el.innerHTML = rows.map(([t, note, b, a], i) => `<div class="row" data-k="${i}"><div class="t"><i>${i + 1}</i><b>${esc(t)}</b><span>${esc(note)}</span></div>
    <div class="bars"><div class="br b"><span class="l">${esc(b[0])}</span><span class="tr"><i style="width:100%"></i></span><span class="v">${ms(b[1])}</span></div>
      <div class="br a"><span class="l">${esc(a[0])}</span><span class="tr"><i style="width:${Math.max(1, 100 * a[1] / b[1]).toFixed(1)}%"></i></span><span class="v">${ms(a[1])}</span></div></div>
    <div class="dl"><div>−${ms(b[1] - a[1])}</div><div class="pc">${Math.round(100 * (1 - a[1] / b[1]))}% less</div></div></div>`).join('');
  return { step(k) { hide(el, k); } };
};

/* ======================= decision tables ======================= */
const ICON = { y: 'y', n: 'n', '~': 'p', '?': 'q' };
FIGS.store_table = (el) => {
  const rows = get('research.' + (el.dataset.group || 'dedicated')); if (!rows) return need(el, 'v5_store_research.json');
  const cell = (c) => `<td><span class="${ICON[c[0]] || 'q'}"></span>${esc(c[1])}</td>`;
  el.innerHTML = `<table class="store-t"><tr><th>Store</th><th>Dense + BM25 in one engine</th><th>Filter inside the search</th><th>UK / EU region</th><th>Free tier, our size</th><th>Runs as</th></tr>
    ${rows.map((r, i) => `<tr data-k="${i < (+el.dataset.first || 99) ? 0 : 1}"><td class="nm${/Qdrant/.test(r.name) ? ' pk' : ''}">${esc(r.name)}</td>${cell(r.hybrid)}${cell(r.filter)}${cell(r.region)}${cell(r.free)}<td>${esc(r.ops)}</td></tr>`).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

FIGS.store_cons = (el) => {
  const c = get('research.considerations'); if (!c) return need(el, 'v5_store_research.json → considerations');
  const key = new Set([0, 1, 5, 6]);
  el.classList.add('store-cons');
  el.innerHTML = c.map(([t, d], i) => `<div class="c${key.has(i) ? ' key' : ''}" data-k="${i < 4 ? 0 : i < 7 ? 1 : 2}"><b>${esc(t)}</b>${esc(d)}</div>`).join('');
  return { step(k) { reveal(el, k); } };
};

FIGS.store_pick = (el) => {
  const p = get('research.pick'); if (!p) return need(el, 'v5_store_research.json → pick');
  el.classList.add('store-why');
  el.innerHTML = p.why.map((w, i) => `<div class="w" data-k="${i < 2 ? 0 : 1}">${esc(w)}</div>`).join('') + p.caveats.map((w) => `<div class="w cv" data-k="2">${esc(w)}</div>`).join('') + (p.else ? `<div class="w el" data-k="3">${esc(p.else)}</div>` : '');
  return { step(k) { reveal(el, k); } };
};

/* ======================= a real screenshot (v5/img/store/), with a highlight per click ======================= */
FIGS.store_shot = (el) => {
  const name = el.dataset.img;
  const have = (get('shots') || []).includes(name);
  el.classList.add('store-shot');
  if (!have) { el.innerHTML = `<div class="todo"><div class="todo-card f3"><span class="todo-k">Screenshot pending</span><div>${esc(el.dataset.what || name)}</div><div class="todo-s">v5/img/store/${esc(name)}, taken from the Qdrant Cloud dashboard</div></div></div>`; return { step() {} }; }
  const boxes = (el.dataset.hl || '').split(';').map((b) => (b ? b.split(',').map(Number) : null));
  const zoom = el.dataset.view ? ` style="object-view-box:inset(${esc(el.dataset.view)})"` : '';   // crop to a region of the screenshot, inside the box
  el.innerHTML = `<img src="${BASE}img/store/${esc(name)}" alt="${esc(el.dataset.what || name)}"${zoom}>` + boxes.map((b, i) => (b ? `<div class="hl" data-k="${i + 1}" style="left:${b[0]}%;top:${b[1]}%;width:${b[2]}%;height:${b[3]}%"></div>` : '')).join('');
  return { step(k) { el.querySelectorAll('.hl').forEach((x) => x.classList.toggle('store-hide', +x.dataset.k !== k)); } };
};

/* ======================= measured headline numbers ======================= */
FIGS.store_kpi = (el) => {
  // data-items="label|path|fmt;…"
  const items = (el.dataset.items || '').split(';').filter(Boolean).map((r) => r.split('|'));
  el.classList.add('store-kpi');
  el.innerHTML = items.map(([l, p, f], i) => { const v = get(p); const t = v == null ? '–' : f === 'ms' ? ms(v) : f === 's' ? (+v).toFixed(1) + ' s' : f === 'mb' ? bytes(v) : f === 'r3' ? (+v).toFixed(3) : f === 'usd' ? '$' + v : fmt(v); return `<div class="m" data-k="${i < (+el.dataset.first || 99) ? 0 : 1}"><div class="v">${esc(t)}</div><div class="k">${esc(l)}</div></div>`; }).join('');
  return { step(k) { reveal(el, k); } };
};

FIGS.store_fill = (el) => { fill(); return { step() {} }; };
})();
