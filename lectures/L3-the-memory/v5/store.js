/* Lecture 3 v5 · section `store`: where the vectors live. Chroma for real on document D and the whole dump, HNSW, the
   production choice, and the Qdrant Cloud walkthrough. Figures are FIGS.store_<fig>; every number, record, file size and
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
const ms = (v) => (v == null ? '–' : (+v >= 100 ? Math.round(+v) : (+v).toFixed(1)) + ' ms');
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
  chroma_build: ['from ledgerline.course.l3 import rag', '',
    '# document D at the chosen chunking: 15 chunks', 'd = [c for c in chunks if c.file == D_PATH]', '',
    'idx = rag.Index.build(d, ["bge-small"], "store_D",', '                      vectors={"bge-small": d_vecs})',
    '# writes chromadb.PersistentClient("store_D/chroma")', '# two collections: "bge-small" and "bge-small__hr"',
    '# HNSW: cosine, ef_search 4000, max_neighbors 32'],
  chroma_query: ['col = idx.collection("bge-small")', 'q = rag.Embedder("bge-small").query(emma)          # 384 numbers',
    'col.query(query_embeddings=[q.tolist()], n_results=5,', '          include=["distances", "metadatas", "documents"])'],
  chroma_where: ['col.query(query_embeddings=[q.tolist()], n_results=10,', '          where={"superseded": False})       # drop old copies'],
  env: ['# vectordb.env  (gitignored: *.env)', 'QDRANT_URL=https://<cluster-id>.europe-west3-0.gcp.cloud.qdrant.io', 'QDRANT_API_KEY=••••••••••••••••••••', '',
    '# experiments/v5_store_cloud.py: read on the laptop, passed to Modal as a secret', 'def _creds():', '    for line in ENV.read_text().splitlines():',
    '        k, v = line.split("=", 1)', '        if k in ("QDRANT_URL", "QDRANT_API_KEY"): out[k] = v', '    return out            # never printed, never logged'],
  create: ['q = QdrantClient(url=os.environ["QDRANT_URL"],', '                 api_key=os.environ["QDRANT_API_KEY"])',
    'q.create_collection("northbridge_docs",', '    vectors_config={"dense": VectorParams(size=384, distance=Distance.COSINE)})', '',
    '# payload indexes BEFORE the upsert: filters run inside the HNSW search', 'for f in ("confidential", "superseded", "future"):',
    '    q.create_payload_index("northbridge_docs", f, field_schema="bool")', 'for f in ("folder", "doc_id", "file", "status"):',
    '    q.create_payload_index("northbridge_docs", f, field_schema="keyword")', '',
    '# BM25 inside the engine (Qdrant 1.20): a full-text index with BM25 scoring', 'q.create_payload_index("northbridge_docs", "text", field_schema=TextIndexParams(',
    '    type="text", tokenizer="word", lowercase=True, stopwords="english",', '    scoring=TextScoringParams(type="bm25")))'],
  upsert: ['def payload(c, i):', '    return {"cite": c.cite, "text": c.text, "file": c.file, "section": c.locs["sections"][0],',
    '            "doc_id": ..., "version": ..., "status": ..., "superseded": ...,', '            "confidential": ...}', '',
    'ids = [i for i, c in enumerate(chunks) if c.file == D]                  # D first: 15 points', 'q.upsert("northbridge_docs", wait=True, points=[',
    '    PointStruct(id=i, vector={"dense": vecs[i].tolist()}, payload=payload(chunks[i], i))', '    for i in ids])', '# then the other 28,938, in batches of 256'],
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

/* ======================= one stored record: id, document, metadata, embedding ======================= */
const vcol = (v) => { const a = Math.min(1, Math.abs(v) / 0.07); return v >= 0 ? `rgba(11,87,208,${0.25 + 0.75 * a})` : `rgba(196,81,31,${0.25 + 0.75 * a})`; };
FIGS.store_record = (el) => {
  const r = get('local.D.record'); if (!r) return need(el, 'v5_store_local.json → D.record');
  // the stored text keeps the PDF's line breaks; join wrapped lines so each clause reads as one paragraph
  const joined = r.document.split('\n').reduce((a, l) => { if (a.length && !/^(\[|\d+(\.\d+)*\.?\s)/.test(l)) a[a.length - 1] += ' ' + l; else a.push(l); return a; }, []).join('\n');
  const doc = esc(joined).replace(/(6\.2 Lithium-cell[\s\S]*?counts as no certificate\.)/, '<mark>$1</mark>').replace(/(6\.4 Prefer[\s\S]*?lithium-cell part\.)/, '<mark>$1</mark>');
  const m = r.metadata;
  const keys = ['file', 'folder', 'fmt', 'doc_id', 'i', 'confidential', 'superseded', 'future'];
  el.innerHTML = `<div class="store-rec">
    <div class="r" data-k="0"><span class="k">id</span><pre>"${esc(r.id)}"   <span style="color:var(--ink-3)">· ${esc(r.cite)}</span></pre></div>
    <div class="r" data-k="0"><span class="k">document<small>the text that was embedded</small></span><pre class="doc">${doc}</pre></div>
    <div class="r" data-k="1"><span class="k">metadata<small>filterable fields</small></span><div class="meta">${keys.filter((k) => k in m).map((k) => `<span class="${k === 'confidential' || k === 'superseded' ? 'hot' : ''}"><b>${k}</b> ${esc(JSON.stringify(m[k]))}</span>`).join('')}</div></div>
    <div class="r" data-k="2"><span class="k">embedding<small>${r.embedding_len} numbers, length ${(+r.embedding_norm).toFixed(2)}</small></span><div class="vec">${r.embedding_first.map((v) => `<i style="background:${vcol(v)}">${v.toFixed(4)}</i>`).join('')}<em>… ${r.embedding_len - r.embedding_first.length} more</em></div></div>
  </div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= the files Chroma wrote, with their real sizes ======================= */
FIGS.store_files = (el) => {
  const set = el.dataset.set || 'D';
  const d = get('local.' + set); if (!d || !d.files) return need(el, 'v5_store_local.json → ' + set + '.files');
  const root = set === 'D' ? 'store_D' : 'store_dump';
  const max = Math.max(...d.files.map((f) => f.bytes));
  const groups = (el.dataset.hl || '').split('|').map((g) => g.split(',').filter(Boolean));
  const uu = {}; let n = 0;
  const show = (p) => p.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/, (u) => (uu[u] = uu[u] || u.slice(0, 8) + '…'));
  const head = d.hnsw_headers || {};
  const tag = (p) => { const u = (p.match(/[0-9a-f]{8}-[0-9a-f-]{27}/) || [])[0]; const h = u && head[u]; return h && p.endsWith('header.bin') ? `  <span class="c"># ${fmt(h.cur_element_count)} vectors · room for ${fmt(h.max_elements)}</span>` : ''; };
  el.classList.add('store-term');
  el.innerHTML = `<div class="bar"><i></i><i></i><i></i><span>Modal container · ${esc(root)}/ · real sizes</span></div><div class="body"><span class="ln"><span class="p">$</span> find ${root} -type f -exec ls -l {} +</span>${d.files.map((f) => { n++; return `<span class="ln" data-p="${esc(f.path)}"><span class="sz">${fmt(f.bytes)}</span>${esc(show(f.path))}<span class="barv" style="width:${Math.max(2, Math.round(150 * f.bytes / max))}px"></span>${tag(f.path)}</span>`; }).join('')}<span class="ln"><span class="p">$</span> du -sb ${root}  <span class="s">${fmt(d.bytes_total)}</span> <span class="c">bytes (${bytes(d.bytes_total)})</span></span></div>`;
  return { step(k) { const g = k > 0 ? (groups[k - 1] || []) : []; el.querySelectorAll('.ln[data-p]').forEach((x) => x.classList.toggle('hl', g.some((t) => x.dataset.p.includes(t)))); } };
};

/* ======================= ranked results (Chroma or Qdrant) ======================= */
function resList(rows, opts = {}) {
  const gold = opts.gold;
  return rows.slice(0, opts.n || rows.length).map((x, i) => {
    const conf = x.confidential, old = x.superseded, g = gold && String(x.cite || '').includes(gold);
    const val = x.similarity != null ? (+x.similarity).toFixed(3) : x.score != null ? (+x.score).toFixed(opts.d || 3) : '';
    return `<div class="it${g ? ' gold' : ''}${old ? ' old' : ''}${conf ? ' conf' : ''}" data-k="${opts.kOf ? opts.kOf(i) : 0}"><span class="n">${i + 1}</span><span class="ct">${esc(short(x.cite, opts.w || 74))}</span><span class="tgs">${g ? '<span class="tg g">§6 of D</span>' : ''}${old ? '<span class="tg o">superseded</span>' : ''}${conf ? '<span class="tg cf">HR confidential</span>' : ''}</span><span class="v">${val}</span></div>`;
  }).join('');
}
FIGS.store_res = (el) => {
  const rows = get(el.dataset.path); if (!rows) return need(el, el.dataset.path);
  const n = +(el.dataset.n || rows.length), k1 = +(el.dataset.k1 || 99);
  const t = get(el.dataset.ms || '__none');
  el.innerHTML = `<div class="store-res">${el.dataset.title ? `<h4>${esc(el.dataset.title)}</h4>` : ''}${resList(rows, { n, gold: el.dataset.gold, w: +(el.dataset.w || 74), kOf: (i) => (i >= k1 ? 1 : 0), d: +(el.dataset.d || 3) })}${t != null ? `<div class="ms">${esc(el.dataset.msl || 'one query')}: ${ms(t)}</div>` : ''}</div>`;
  return { step(k) { (el.dataset.mode === 'hide' ? hide : reveal)(el, k - (+el.dataset.k0 || 0)); } };
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

/* ======================= HNSW: a toy graph searched by the real greedy rule, then the measured check ======================= */
function rng(seed) { return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
FIGS.store_hnsw = (el) => {
  const NS = 'http://www.w3.org/2000/svg';
  const W = +(el.dataset.w || 820), H = 430;
  const N = 42, Q = [0.70, 0.62];
  const d2 = (a, b) => (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2;
  // build a toy HNSW for a seed and walk it greedily; keep the first seed whose walk is visible and ends at the true nearest
  const build = (seed) => {
    const R = rng(seed), pts = Array.from({ length: N }, () => [0.04 + 0.92 * R(), 0.08 + 0.84 * R()]);
    const order = pts.map((_, i) => i).sort(() => R() - 0.5);
    const lvl = new Array(N).fill(0); order.slice(0, 12).forEach((i) => (lvl[i] = 1)); order.slice(0, 3).forEach((i) => (lvl[i] = 2));
    const nbr = {}; // per layer: each point's nearest within the layer (3 at the bottom, 2 above), made undirected
    for (let L = 0; L <= 2; L++) {
      const ids = pts.map((_, i) => i).filter((i) => lvl[i] >= L);
      nbr[L] = {}; ids.forEach((i) => (nbr[L][i] = new Set()));
      ids.forEach((i) => ids.filter((j) => j !== i).sort((a, b) => d2(pts[i], pts[a]) - d2(pts[i], pts[b])).slice(0, L === 0 ? 3 : 2).forEach((j) => { nbr[L][i].add(j); nbr[L][j].add(i); }));
    }
    let cur = order.slice(0, 3).sort((a, b) => d2(pts[b], Q) - d2(pts[a], Q))[0]; const path = [];
    for (let L = 2; L >= 0; L--) {
      path.push([L, cur]);
      for (;;) { let best = cur; nbr[L][cur].forEach((j) => { if (d2(pts[j], Q) < d2(pts[best], Q)) best = j; }); if (best === cur) break; cur = best; path.push([L, cur]); }
    }
    const exact = pts.map((_, i) => i).sort((a, b) => d2(pts[a], Q) - d2(pts[b], Q))[0];
    return { pts, lvl, nbr, path, cur, exact };
  };
  let G = null;
  for (let seed = 1; seed < 400 && !G; seed++) { const g = build(seed); const hops = [0, 1, 2].map((L) => g.path.filter((p) => p[0] === L).length - 1); if (g.cur === g.exact && hops[0] >= 2 && hops[1] >= 1 && hops[2] >= 1) G = g; }
  G = G || build(7);
  const { pts, lvl, nbr, path, cur, exact } = G;
  const pw = W - 300, ph = 108, skew = 90, gap = 132, x0 = 150, y0 = 18;
  const P = (L, p) => [x0 + p[0] * pw + (1 - p[1]) * skew, y0 + (2 - L) * gap + p[1] * ph];
  const s = document.createElementNS(NS, 'svg'); s.setAttribute('width', W); s.setAttribute('height', H); s.setAttribute('viewBox', `0 0 ${W} ${H}`);
  let h = '';
  const counts = [0, 1, 2].map((L) => lvl.filter((v) => v >= L).length);
  for (let L = 2; L >= 0; L--) {
    const c = [P(L, [0, 0]), P(L, [1, 0]), P(L, [1, 1]), P(L, [0, 1])];
    h += `<g data-k="0"><polygon points="${c.map((p) => p.join(',')).join(' ')}" fill="${L === 0 ? '#eef4fd' : '#f5f8fd'}" stroke="#c9d6ea"/>`;
    h += `<text x="14" y="${y0 + (2 - L) * gap + ph / 2 + 2}" font-size="17" font-weight="600" fill="#45474d">Layer ${L}</text><text x="14" y="${y0 + (2 - L) * gap + ph / 2 + 22}" font-size="14" fill="#6b6e76">${counts[L]} points</text>`;
    Object.entries(nbr[L]).forEach(([i, set]) => set.forEach((j) => { if (+i < j) { const a = P(L, pts[i]), b = P(L, pts[j]); h += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#b7c7df" stroke-width="1.2"/>`; } }));
    pts.forEach((p, i) => { if (lvl[i] >= L) { const a = P(L, p); h += `<circle cx="${a[0]}" cy="${a[1]}" r="${L ? 5.5 : 4.5}" fill="#7f9cc4"/>`; } });
    h += '</g>';
  }
  // the query and the greedy path
  h += '<g data-k="1">';
  for (let L = 2; L >= 0; L--) { const q = P(L, Q); h += `<path d="M${q[0]} ${q[1] - 9} l8 9 l-8 9 l-8 -9z" fill="#c4511f"/>`; }
  for (let t = 1; t < path.length; t++) {
    const [La, a] = path[t - 1], [Lb, b] = path[t]; const A = P(La, pts[a]), B = P(Lb, pts[b]);
    h += La === Lb ? `<line x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}" stroke="#0b57d0" stroke-width="3.2" stroke-linecap="round"/>` : `<line x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}" stroke="#0b57d0" stroke-width="1.6" stroke-dasharray="5 5"/>`;
  }
  path.forEach(([L, i]) => { const a = P(L, pts[i]); h += `<circle cx="${a[0]}" cy="${a[1]}" r="7" fill="#0b57d0" stroke="#fff" stroke-width="2"/>`; });
  const e = P(0, pts[cur]); h += `<circle cx="${e[0]}" cy="${e[1]}" r="12" fill="none" stroke="#138a60" stroke-width="3"/><text x="${e[0] + 18}" y="${e[1] - 16}" font-size="15" fill="#138a60" font-weight="600">${cur === exact ? 'found: the true nearest' : 'found: close, not the nearest'}</text>`;
  const st = P(2, pts[path[0][1]]); h += `<text x="${st[0] - 10}" y="${st[1] - 14}" font-size="15" fill="#0b57d0" font-weight="600" text-anchor="end">start</text>`;
  h += '</g>';
  s.innerHTML = h;
  el.classList.add('store-hn');
  el.innerHTML = ''; el.appendChild(s);
  return { step(k) { reveal(el, k); } };
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
  el.innerHTML = `<img src="${BASE}img/store/${esc(name)}" alt="${esc(el.dataset.what || name)}">` + boxes.map((b, i) => (b ? `<div class="hl" data-k="${i + 1}" style="left:${b[0]}%;top:${b[1]}%;width:${b[2]}%;height:${b[3]}%"></div>` : '')).join('');
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
