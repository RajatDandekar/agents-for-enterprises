/* Lecture 3 v5 · Section 7, the LLM Wiki on one document (D) and one question (Emma's).
   Figures FIGS.wiki_<name>(el) -> { step(k) }, k = the number of .step elements shown on the slide.
   Every passage, slug and number comes from window.L3V5.wiki (v5/wiki_data.js, written by experiments/v5_wiki_data.py
   from the recorded runs in experiments/logs/v5_wiki_*.json and the course's earlier logs). Loaded after figs2.js. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const W = () => (window.L3V5 && window.L3V5.wiki) || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const usd = (v, d = 3) => '$' + Number(v).toFixed(d);
const sec = (v) => Number(v).toFixed(1) + ' s';
const short = (f) => String(f || '').split('/').pop();
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(L3 v5 wiki data)</span><div>${esc(what)}</div></div>`; return { step() {} }; };
const at = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('wiki-hide', +x.dataset.k > k));
const stopClick = (node, fn) => node.addEventListener('click', (e) => { e.stopPropagation(); fn(e); });
const wl = (s) => esc(s).replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, '<span class="wiki-wl">$2</span>').replace(/\[\[([^\]]+)\]\]/g, '<span class="wiki-wl">$1</span>')
  .replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');

/* ---------------------------------------------------------------- shared: D as a panel of clauses */
function dHTML(D, title) {
  const hdr = `<div class="wiki-dh" data-c="hdr"><table>${D.header.map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('')}</table></div>`;
  const ver = `<div class="wiki-dv" data-c="ver"><div class="wiki-k" style="margin:2px 0 4px">Version history</div><table>${D.versions.map((r) => `<tr>${r.map((c) => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table></div>`;
  const body = D.clauses.map((c) => (c.kind === 'head' ? `<div class="wiki-dch">${esc(c.id)}. ${esc(c.text)}</div>`
    : `<div class="wiki-dc" data-c="${esc(c.id)}"><i>${esc(c.id.replace(/\.$/, ''))}</i><span>${esc(c.text)}</span></div>`)).join('');
  return `<div class="wiki-dtop"><b>D</b><span>${esc(title || 'POL-PUR-001 Purchase Policy v4.1 · pp. 1–2 of ' + D.pages)}</span></div>
    <div class="wiki-din"><div class="wiki-dsc">${hdr}${ver}${body}</div></div>`;
}
/* show a window of rows that fits the box (no scrolling, nothing cut): the lit rows first, then neighbours */
function fitWindow(rows, lit, H) {
  rows.forEach((r) => { r.style.display = ''; });
  const hh = rows.map((r) => { const cs = getComputedStyle(r); return r.offsetHeight + parseFloat(cs.marginTop || 0) + parseFloat(cs.marginBottom || 0); });
  let lo = lit.length ? Math.min(...lit) : 0, hi = lit.length ? Math.max(...lit) : -1, tot = 0;
  for (let i = lo; i <= hi; i++) tot += hh[i];
  if (tot > H) {  // the lit rows alone are too tall: keep the first ones that fit
    let acc = 0;
    rows.forEach((r, i) => { const keep = lit.includes(i) && acc + hh[i] <= H; if (keep) acc += hh[i]; r.style.display = keep ? '' : 'none'; });
    return;
  }
  let down = true;
  for (;;) {
    const canD = hi + 1 < rows.length && tot + hh[hi + 1] <= H, canU = lo - 1 >= 0 && tot + hh[lo - 1] <= H;
    if (!canD && !canU) break;
    if ((down && canD) || !canU) { hi++; tot += hh[hi]; } else { lo--; tot += hh[lo]; }
    down = !down;
  }
  rows.forEach((r, i) => { r.style.display = i >= lo && i <= hi ? '' : 'none'; });
}
function boxH(box, pad = 28) { return (box.clientHeight || 500) - pad; }
function dLight(panel, ids, cls = '') {
  const sc = panel.querySelector('.wiki-dsc'), box = panel.querySelector('.wiki-din');
  const rows = [...sc.children];
  rows.forEach((x) => { x.classList.remove('on', 'ha', 'hr', 'hg'); });
  const lit = [];
  (ids || []).forEach((id) => { const i = rows.findIndex((n) => n.dataset.c === id); if (i >= 0) { rows[i].classList.add('on'); if (cls) rows[i].classList.add(cls); lit.push(i); } });
  panel.classList.toggle('lit', lit.length > 0);
  fitWindow(rows, lit, boxH(box, 52));
}

/* ---------------------------------------------------------------- 1 · the idea in one picture */
FIGS.wiki_idea = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const b = d.fail.cost.build, st = d.eng.wiki_store;
  el.classList.add('wiki-idea');
  const box = (x, y, w, h, cls, t1, t2, t3, k) => `<g data-k="${k}"><rect class="box ${cls}" x="${x}" y="${y}" width="${w}" height="${h}" rx="22"/>
    <text class="t1" x="${x + 24}" y="${y + 40}">${t1}</text><text class="t2" x="${x + 24}" y="${y + 70}">${t2}</text>${t3 ? `<text class="t3" x="${x + 24}" y="${y + 96}">${t3}</text>` : ''}</g>`;
  el.innerHTML = `<svg viewBox="0 0 1400 600" width="1400" height="600">
    <defs><marker id="wiki-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>
    <text class="lane" x="0" y="22" data-k="0">LLM WIKI · WRITE ONCE, READ MANY TIMES</text>
    ${box(0, 150, 330, 120, 'raw', 'Raw sources', `${fmt(b.files)} files from Henrik`, 'never edited', 0)}
    <g data-k="1"><path class="arr a" d="M335,210 L515,210"/><text class="t2" x="352" y="192">ingest</text><text class="t3" x="352" y="240">the model reads each</text><text class="t3" x="352" y="260">source once</text></g>
    ${box(525, 150, 360, 120, 'wkb', 'The wiki', `${fmt(st.pages)} pages the model wrote`, 'plus index.md and log.md', 1)}
    ${box(525, 30, 360, 92, 'sc', 'AGENTS.md', 'the rules, written by people', '', 2)}
    <g data-k="2"><path class="arr g" d="M705,122 L705,146"/></g>
    <g data-k="3"><path class="arr a" d="M1060,210 L890,210"/><text class="t2" x="905" y="192">query</text><text class="t3" x="905" y="240">read index.md,</text><text class="t3" x="905" y="260">open pages</text></g>
    ${box(1070, 150, 330, 120, 'wkb', 'Emma’s question', 'answered from pages', 'each sentence cites a raw source', 3)}
    <text class="lane" x="0" y="372" data-k="4">RAG · NOTHING WRITTEN IN ADVANCE</text>
    ${box(0, 400, 330, 120, 'raw', 'Raw sources', 'the same files', 'cut into chunks, indexed', 4)}
    <g data-k="4"><path class="arr b" d="M1060,460 L335,460"/><text class="t2" x="560" y="442">search the chunks on every question</text><text class="t3" x="560" y="490">no model call before the question arrives</text></g>
    ${box(1070, 400, 330, 120, 'rg', 'Emma’s question', 'answered from chunks', 'each chunk cites its file', 4)}
  </svg>`;
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- 2 · D read by hand, then what the model wrote */
FIGS.wiki_hand = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const D = d.d;
  const doc = document.createElement('div'); doc.className = 'wiki-doc'; doc.style.cssText = 'left:0;top:0;width:820px;height:640px'; doc.innerHTML = dHTML(D);
  const hand = [
    { c: ['hdr', 'ver'], t: '<b>The policy itself</b> <code>POL-PUR-001</code><span class="s">version 4.1, in force since 1 April 2026; owner, approver, its history</span>' },
    { c: ['3.3'], t: '<b>A rule with a number</b>: direct orders up to £50,000 gross<span class="s">a fact for the policy’s page, with its clause</span>' },
    { c: ['5.1', '5.2', '5.3'], t: '<b>Another document it names</b> <code>POL-APR-002</code><span class="s">the approval matrix: D only says what it is for</span>' },
    { c: ['6.2', '6.4'], cls: 'ha', t: '<b>Emma’s rules</b>: §6.2 UN 38.3 and §6.4 the cheaper quote<span class="s">a topic shared by many documents: UN 38.3 certificates</span>' },
    { c: ['4.3', '8.1'], t: '<b>Things it mentions</b>: screen FIN-CC-01, tax codes, Henrik Weber<span class="s">each could be a page that links back here</span>' },
  ];
  const list = document.createElement('div'); list.className = 'wiki-list'; list.style.cssText = 'left:860px;top:0;width:540px';
  list.innerHTML = `<div class="wiki-k" data-k="1">Pages a careful reader would write from D</div>` +
    hand.map((h, i) => `<div class="wiki-li" data-k="${i + 1}" data-i="${i + 1}">${h.t}</div>`).join('');
  const mdl = document.createElement('div'); mdl.className = 'wiki-list'; mdl.style.cssText = 'left:860px;top:0;width:540px';
  const rp = d.reply.pages, mm = d.merge.map;
  mdl.innerHTML = `<div class="wiki-k a">What the model wrote: ${rp.length} pages, ${rp.reduce((a, p) => a + p.n, 0)} facts</div>` +
    rp.map((p) => `<div class="wiki-li mdl"><span class="n">${p.n} fact${p.n > 1 ? 's' : ''}</span><code>${esc(mm[p.slug] || p.slug)}</code>${mm[p.slug] ? `<span class="s">proposed as <code>${esc(p.slug)}</code>, merged by the build</span>` : ''}</div>`).join('') +
    `<div class="wiki-li" style="background:#fff;box-shadow:var(--shadow)">Same five ideas as ours. D names <code>POL-SUP-003</code> (§6.3) but says nothing about it, so no page: only a link later.</div>`;
  el.append(doc, list, mdl);
  return { step(k) {
    const show = Math.min(k, hand.length);
    list.classList.toggle('wiki-hide', k > hand.length); mdl.classList.toggle('wiki-hide', k <= hand.length);
    at(list, show);
    list.querySelectorAll('.wiki-li').forEach((x) => x.classList.toggle('cur', +x.dataset.i === show));
    if (k === 0) dLight(doc, []);
    else if (k <= hand.length) dLight(doc, hand[k - 1].c, hand[k - 1].cls);
    else dLight(doc, ['6.2', '6.4'], 'ha');
  } };
};

/* ---------------------------------------------------------------- 3 · the READ prompt, part by part */
FIGS.wiki_prompt = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const R = d.read, P = R.parts, tot = P.reduce((a, p) => a + p.tokens, 0);
  const H = 560;
  el.innerHTML = `<div class="wiki-stack" style="left:0;top:0;width:470px">
      <div class="wiki-msg">system message</div>
      ${P.map((p, i) => `${i === 2 ? '<div class="wiki-msg">user message</div>' : ''}<button class="wiki-part p${i}" data-i="${i + 1}" style="height:${Math.max(34, Math.round((H - 120) * p.tokens / tot))}px">${esc(p.what)}<span>${fmt(p.tokens)} tok</span></button>`).join('')}
      <div class="tiny" style="margin-top:8px">Counted part by part with Gemini’s own counter. The call as sent: <b>${fmt(R.tokens_in)} tokens in</b>, ${fmt(R.tokens_out)} out, ${sec(R.seconds)}.</div>
    </div>
    <div class="wiki-ex" style="left:510px;top:0;width:890px;height:600px"></div>`;
  const ex = el.querySelector('.wiki-ex'), stack = el.querySelector('.wiki-stack');
  const show = (i) => {
    stack.classList.toggle('sel', i > 0);
    stack.querySelectorAll('.wiki-part').forEach((b) => b.classList.toggle('on', +b.dataset.i === i));
    if (!i) { ex.innerHTML = `<span class="h">One call to ${esc(R.model)}, the whole of D at once</span>D is ${fmt(d.d.chars)} characters, pages 1 to 4, so it fits in one part.\nThe prompt has five parts. Click one, or step through.\n\nThe reply must be JSON: the pages D touches, and for each page its facts, every fact with a quote copied from D.`; return; }
    const p = P[i - 1];
    ex.innerHTML = `<span class="h">${esc(p.what)} · ${fmt(p.chars)} characters · ${fmt(p.tokens)} tokens</span>` +
      p.excerpt.map((l) => (/^6\.2 /.test(l) ? `<mark>${esc(l)}</mark>` : esc(l))).join('\n');
  };
  stack.querySelectorAll('.wiki-part').forEach((b) => stopClick(b, () => show(+b.dataset.i)));
  return { step(k) { show(Math.min(k, P.length)); } };
};

/* ---------------------------------------------------------------- 4 · the reply */
FIGS.wiki_reply = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const r = d.reply, f62 = r.pages[0].facts.find((f) => /^Lithium-cell/.test(f.quote)) || r.pages[0].facts[0];
  const mm = d.merge.map;
  el.innerHTML = `<div class="wiki-json" style="left:0;top:0;width:1400px;height:610px">
    <div class="blk" data-b="1"><span class="k">"source_note"</span>: <span class="wrap">${esc(r.source_note)}</span></div>
    <div class="blk" data-b="2"><span class="k">"pages"</span>: <span class="c">// ${r.pages.length} pages, each with its facts</span>
      ${r.pages.map((p, i) => `<div class="row" data-r="${i}"><span><span class="s">"${esc(p.slug)}"</span></span><span class="c">${esc(p.type)}</span><span class="c">${p.n} fact${p.n > 1 ? 's' : ''}${mm[p.slug] ? ` · the build’s MERGE call then mapped it to <span class="s">"${esc(mm[p.slug])}"</span>` : ''}</span></div>`).join('')}</div>
    <div class="blk" data-b="3"><span class="c">// one of the ${r.pages[0].n} facts for "pol-pur-001"</span><br>{ <span class="k">"fact"</span>: <span class="wrap">"${esc(f62.fact)}"</span>,<br>&nbsp;&nbsp;<span class="k">"quote"</span>: <span class="wrap" style="background:#fff6c9">"${esc(f62.quote)}"</span>,<br>&nbsp;&nbsp;<span class="k">"page"</span>: ${f62.page}, <span class="k">"section"</span>: <span class="s">"${esc(f62.section)}"</span> }</div>
    <div class="blk" data-b="4"><span class="k">"conflicts"</span>:${r.conflicts.map((c) => `<br>&nbsp;&nbsp;{ <span class="k">"kind"</span>: <span class="s">"${esc(c.kind)}"</span>, <span class="k">"other"</span>: <span class="s">"${esc(c.other)}"</span>, <span class="k">"detail"</span>: <span class="wrap">"${esc(c.detail)}"</span> }`).join('')}</div>
  </div>`;
  return { step(k) {
    el.querySelectorAll('.blk').forEach((b) => { const i = +b.dataset.b; b.classList.toggle('wiki-hide', i > k + 1); b.classList.toggle('on', i === k + 1 && k > 0); });
    el.querySelectorAll('.row').forEach((x) => x.classList.toggle('on', k === 2 && x.dataset.r === '0'));
  } };
};

/* ---------------------------------------------------------------- 5 · the quote check */
function normJS(s) {
  return String(s).replace(/[’‘]/g, "'").replace(/[“”]/g, '"').replace(/[–—]/g, '-').replace(/ /g, ' ').replace(/­/g, '')
    .replace(/\*\*|__|[•·▪]/g, '').replace(/\s+/g, '').toLowerCase();
}
FIGS.wiki_quote = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const ok = d.checks.find((c) => c.slug === 'pol-pur-001' && /^Lithium-cell/.test(c.quote));
  const bad = d.checks.find((c) => c.verdict !== 'verified');
  const page = normJS(d.page2_raw);
  const win = (q, okk) => {
    const nq = normJS(q);
    const i = page.indexOf(nq);
    if (okk && i >= 0) return `…${esc(page.slice(Math.max(0, i - 40), i))}<b>${esc(nq)}</b>${esc(page.slice(i + nq.length, i + nq.length + 40))}…`;
    // the longest prefix of the quote that is in the page, then where it stops matching
    let n = nq.length; while (n > 0 && page.indexOf(nq.slice(0, n)) < 0) n--;
    const j = page.indexOf(nq.slice(0, n));
    const nxt = page.slice(j + n, j + n + 3);
    return `…${esc(page.slice(Math.max(0, j - 20), j))}<b>${esc(nq.slice(0, n))}</b><s>${esc(nxt)}</s>${esc(page.slice(j + n + 3, j + n + 60))}…`;
  };
  const nv = d.checks.filter((c) => c.verdict === 'verified').length;
  el.innerHTML = `<div class="wiki-qc" style="left:0;top:0;width:1400px">
    <div class="wiki-qrow" data-k="0"><div class="wiki-k">1 · The quote the model gave, for its fact on §6.2</div><div class="t">“${esc(ok.quote)}”</div></div>
    <div class="wiki-qrow" data-k="1"><div class="wiki-k">2 · Both sides normalised by code: lower case, no spaces, plain quotes and dashes</div>
      <div class="wiki-norm">${esc(normJS(ok.quote))}</div></div>
    <div class="wiki-qrow" data-k="2"><div class="wiki-k">3 · Is it a substring of page ${ok.page} of D, as normalised? </div><div class="wiki-norm">${win(ok.quote, true)}</div>
      <span class="wiki-verd ok">✓ verified on p. ${ok.page}</span></div>
    <div class="wiki-qrow" data-k="3"><div class="wiki-k b">A real miss on D: the quote for <code>${esc(bad.slug)}</code> joins §${esc(bad.clauses.join(' and §'))}</div><div class="t">“${esc(bad.quote)}”</div>
      <div class="wiki-norm">${win(bad.quote, false)}</div>
      <span class="wiki-verd no">✗ not found: D has the clause number “5.2” between the two sentences</span></div>
    <div class="wiki-qrow" data-k="4" style="background:var(--g1);box-shadow:none"><div class="t"><b>${nv} of ${d.checks.length}</b> quotes from D verified; the full build: <b>${fmt(d.eng.build_facts.verified)} of ${fmt(d.eng.build_facts.facts)}</b>. The check marks a fact; it does not delete it. <code>pol-apr-002</code> was still written from its two unverified facts, and lint lists such references later.</div></div>
  </div>`;
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- 6 · the written page, each sentence back to D */
function pageHTML(P, title, path) {
  let h = `<div class="top"><b>${esc(title)}</b><code>${esc(path)}</code></div><div class="wiki-pgin"><div class="wiki-pgsc">`;
  if (P.infobox && P.infobox.length) h += `<table class="wiki-ibx">${P.infobox.map(([a, b]) => `<tr><td>${esc(a)}</td><td>${wl(b)}</td></tr>`).join('')}</table>`;
  P.sentences.forEach((s, i) => {
    if (s.kind === 'head') { if (/^(Clauses|See also)$/.test(s.text)) return; h += s.level === 2 ? `<h4>${esc(s.text)}</h4>` : `<h5>${esc(s.text)}</h5>`; return; }
    if (s.section === 'See also') return;
    h += `<div class="wiki-sn" data-s="${i}">${wl(s.text.replace(/^[-*] /, ''))}${s.keys.map((k) => `<span class="rk">${k}</span>`).join('')}</div>`;
  });
  return h + '</div></div>';
}
FIGS.wiki_page = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const P = d.pol;
  const pg = document.createElement('div'); pg.className = 'wiki-pg'; pg.style.cssText = 'left:0;top:0;width:760px;height:540px';
  pg.innerHTML = pageHTML(P, 'pol-pur-001.md', 'written from D alone · 22 references');
  const doc = document.createElement('div'); doc.className = 'wiki-doc'; doc.style.cssText = 'left:790px;top:0;width:610px;height:540px'; doc.innerHTML = dHTML(d.d, 'POL-PUR-001 v4.1, pp. 1–2');
  const line = document.createElement('div'); line.className = 'wiki-chainline'; line.style.cssText = 'left:0;top:556px;width:1400px';
  el.append(pg, doc, line);
  const find = (re) => P.sentences.findIndex((s) => s.kind === 's' && re.test(s.text));
  const picks = [find(/strictly mandates/), find(/direct purchase order without/), find(/^Lithium-cell parts/), find(/cheaper quotation/)];
  const sel = (i) => {
    pg.querySelectorAll('.wiki-sn').forEach((x) => x.classList.toggle('on', +x.dataset.s === i));
    pg.classList.toggle('lit', i >= 0);
    const s = P.sentences[i];
    if (!s) { const sc = pg.querySelector('.wiki-pgsc'); fitWindow([...sc.children], [], boxH(pg.querySelector('.wiki-pgin'), 40)); dLight(doc, []); line.innerHTML = '<span>Click any sentence of the page: its keys lead to the facts, the facts’ quotes to D.</span>'; return; }
    dLight(doc, s.clauses, 'ha');
    const sc = pg.querySelector('.wiki-pgsc'), box = pg.querySelector('.wiki-pgin'), rows = [...sc.children];
    const at_ = rows.findIndex((r) => r.dataset.s === String(i));
    fitWindow(rows, at_ >= 0 ? [at_] : [], boxH(box, 40));
    const k = s.keys[s.keys.length - 1], r = P.refs[k] || {};
    line.innerHTML = `<span>sentence</span><span class="ar">→</span><code>[^${esc(k)}]</code><span class="ar">→</span><span>fact ${esc(k)}, quote</span><span class="q">“${esc((r.quote || '').slice(0, 110))}${(r.quote || '').length > 110 ? '…' : ''}”</span><span class="ar">→</span><span>D, p. ${esc(r.page)}, ${esc(r.section || '')} · §${esc(s.clauses.join(', §').replace(/\.(,|$)/g, '$1'))}</span>`;
  };
  pg.querySelectorAll('.wiki-sn').forEach((x) => stopClick(x, () => sel(+x.dataset.s)));
  return { step(k) { sel(k === 0 ? -1 : picks[Math.min(k, picks.length) - 1]); } };
};

/* ---------------------------------------------------------------- 7 · links, index.md, log.md */
FIGS.wiki_links = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const pm = d.pages_made, c = pm.find((p) => p.slug === 'pol-pur-001'), others = pm.filter((p) => p.slug !== 'pol-pur-001');
  const cx = 330, cy = 250, R = 205;
  const pos = others.map((p, i) => { const a = -Math.PI / 2 + (i * 2 * Math.PI) / others.length; return [cx + R * Math.cos(a) * 1.25, cy + R * Math.sin(a)]; });
  el.innerHTML = `<div class="wiki-graph" style="position:absolute;left:0;top:0;width:680px;height:520px" data-k="0"><svg viewBox="0 0 680 520" width="680" height="520">
      ${pos.map(([x, y]) => `<path class="ed" d="M${cx},${cy} L${x},${y}"/>`).join('')}
      <rect class="nd c" x="${cx - 80}" y="${cy - 22}" width="160" height="44" rx="12"/><text x="${cx}" y="${cy + 5}" text-anchor="middle">pol-pur-001</text>
      ${others.map((p, i) => { const [x, y] = pos[i]; const w = p.slug.length * 8.6 + 26; return `<rect class="nd" x="${x - w / 2}" y="${y - 20}" width="${w}" height="40" rx="12"/><text x="${x}" y="${y + 5}" text-anchor="middle">${esc(p.slug)}</text>`; }).join('')}
    </svg><div class="tiny" style="position:absolute;left:0;top:500px;width:680px">pol-pur-001 links to all ${c.links.length}; each of them links back. Links are <code>[[slug|text]]</code> in the markdown.</div></div>
    <div class="wiki-file" data-k="1" style="left:720px;top:0;width:680px;height:372px;font-size:13.5px"><span class="h">index.md · rebuilt after every ingest · read first by every query</span>${d.index_lines.map((l) => esc(l)).join('\n')}</div>
    <div class="wiki-file" data-k="2" style="left:720px;top:388px;width:680px;height:150px;font-size:13.5px"><span class="h">log.md · append-only · one line per operation</span>${d.log_lines.map((l, i) => (i === 0 ? `<span class="hl">${esc(l)}</span>` : esc(l))).join('\n')}</div>`;
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- 8 · a second source arrives: the real diff */
FIGS.wiki_diff = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const U = d.update;
  const lines = []; let h = -1;
  U.diff.forEach((l) => {
    if (/^(---|\+\+\+) /.test(l)) return;
    if (/^@@/.test(l)) { h++; lines.push({ c: 'hunk', t: l, h }); return; }
    const c = l[0] === '+' ? 'add' : l[0] === '-' ? 'del' : 'ctx';
    const t = l.slice(1);
    if (c === 'ctx' && !t.trim()) return;
    lines.push({ c, t, h });
  });
  el.innerHTML = `<div class="wiki-card cw" style="left:0;top:0;width:470px;height:600px;font-size:17px">
      <span class="wiki-tag b">new source</span><span class="wiki-tag">effective 1 Sep 2026</span>
      <h3 style="margin-top:10px">AMD-SUP-2026-02</h3>
      <span class="q r"><b>1.1</b> ${esc(U.amd_clauses['1.1'])}</span>
      <span class="q r"><b>1.2</b> ${esc(U.amd_clauses['1.2'])}</span>
      <div data-k="1" style="margin-top:10px;font-size:16px;line-height:1.4">The update reads it (1 call), then rewrites only the pages it touches: <b>${U.touched.length} updated</b> (<code>${esc(U.touched.join(', '))}</code>), <b>${U.created.length} created</b> (<code>${esc(U.created.join(', '))}</code>).</div>
    </div>
    <div class="wiki-diff" style="left:500px;top:0;width:900px;height:${520}px"><div class="top"><code>topic-un-38-3-certificates.md</code>&nbsp;· before → after, the real diff</div>
      <div class="wiki-dfin"><div class="wiki-dfsc">${lines.map((x) => `<div class="wiki-dl ${x.c}" data-h="${x.h}">${esc(x.t)}</div>`).join('')}</div></div></div>
    <div class="wiki-file" data-k="5" style="left:500px;top:536px;width:900px;height:64px;padding:10px 16px"><span class="hl">${esc(U.log[U.log.length - 1])}</span></div>`;
  const df = el.querySelector('.wiki-diff'), sc = el.querySelector('.wiki-dfsc'), box = el.querySelector('.wiki-dfin');
  const steps = [[], [], [1], [2], [3, 4], [2]];
  return { step(k) {
    at(el, k);
    const hs = steps[Math.min(k, steps.length - 1)];
    df.classList.toggle('lit', hs.length > 0 && k < 5);
    const lit = [];
    el.querySelectorAll('.wiki-dl').forEach((x) => {
      const on = hs.includes(+x.dataset.h) && !x.classList.contains('ctx');
      x.classList.toggle('on', on);
      if (on && !x.classList.contains('hunk')) lit.push(x);
    });
    const rows = [...sc.children];
    fitWindow(rows, lit.map((x) => rows.indexOf(x)), boxH(box, 24));
  } };
};

/* ---------------------------------------------------------------- 9 · the same change, in RAG */
FIGS.wiki_ragchange = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const U = d.update, c = d.fail.cost;
  el.innerHTML = `<div class="wiki-card ca" style="left:0;top:0;width:680px;height:500px">
      <span class="wiki-tag a">LLM Wiki</span><h3>The model rewrites pages</h3>
      <table class="wiki-t" style="font-size:16px"><tr><th>call</th><th class="n">tokens in</th><th class="n">out</th><th class="n">seconds</th></tr>
      ${U.calls.map((x) => `<tr><td><code>${esc(x.page)}</code></td><td class="n">${fmt(x.tokens_in)}</td><td class="n">${fmt(x.tokens_out)}</td><td class="n">${x.seconds.toFixed(1)}</td></tr>`).join('')}</table>
      <div style="margin-top:12px"><span class="wiki-big a">${c.amd.calls} calls · ${sec(c.amd.seconds.total)} · ${usd(c.amd.usd)}</span>
      <span class="small">wall clock, pages written in parallel. The new rule is now written into the topic page, with the old one under “Versions and conflicts”.</span></div></div>
    <div class="wiki-card cb" style="left:720px;top:0;width:680px;height:500px" data-k="1">
      <span class="wiki-tag b">RAG</span><h3>Code re-cuts one file</h3>
      <table class="wiki-t" style="font-size:16px"><tr><th>chunk of AMD-SUP-2026-02</th><th class="n">tokens</th></tr>
      ${U.rag_chunks.map((x) => `<tr><td>${esc(x.cite)}</td><td class="n">${x.tokens}</td></tr>`).join('')}</table>
      <div style="margin-top:12px"><span class="wiki-big b">0 calls · ${(c.rag.amd_parse_s * 1000).toFixed(0)} ms · $0</span>
      <span class="small">parse ${(c.rag.amd_parse_s * 1000).toFixed(0)} ms, chunk ${(c.rag.amd_chunk_s * 1000).toFixed(1)} ms (structured parser, 200-token chunks, 15% overlap). Rebuilding BM25 over all ${fmt(c.rag.n_chunks)} chunks: ${c.rag.bm25_build_s} s.</span></div>
      <div data-k="2" style="margin-top:12px;font-size:17px;line-height:1.4;background:#fff;border-radius:14px;padding:10px 14px">But nothing is reconciled. The old chunk of POL-SUP-003 §4 (“issued within the last 24 months”) stays in the index next to the new one; the answer step must notice which rule wins, on every question.</div></div>`;
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- 10 · the schema, rule by rule */
FIGS.wiki_schema = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const U = d.update;
  const rules = [
    { n: '20–22', l: 'Slugs are lower-case, words joined by `-`, and built from\nthe document\'s or record\'s own code wherever one exists, so\nthat two sources that name the same thing land on the same page.', r: `D became <code>pol-pur-001</code>; the amendment <code>amd-sup-2026-02</code>. Both landed on <code>topic-un-38-3-certificates</code>, so the second source updated the first one’s page.` },
    { n: '56–57, 64', l: 'Lead: two to four sentences … Infobox: a small key/value table\nRequired sections by type: policy (*Clauses*: one `###` per clause,\nin the policy\'s own numbering)', r: 'The page opened with a lead and an infobox, then <code>### 2. Scope</code> … <code>### 9. Records</code>, in D’s own numbering.' },
    { n: '73', l: 'Every sentence that states a fact ends with a reference to the\nraw source it comes from: `[^r3]`.', r: 'All 22 of pol-pur-001’s keys point to D, page and section. The infobox at the top of a page carries no key (keep that in mind).' },
    { n: '101–103, 108–110', l: '2. Newer replaces older. … an amendment in force … replaces\n   the older text.\n5. Record every case under Versions and conflicts as: today\'s\n   rule, the older or future rule, the sources and dates, and the kind', r: `The diff added “Versions and conflicts”: 12 months / 60 days today, the 24-month rule as older, kind <code>${esc(((U.conflicts['topic-un-38-3-certificates'] || [])[0] || {}).kind || '')}</code>.` },
    { n: '130–132', l: '**Ingest** (one source at a time): read the source; … append one\nline to `log.md`:\n`## [<timestamp>] ingest | <file> | +<created> ~<updated> | <slugs>`', r: `<code>${esc(U.log[U.log.length - 1].replace(/^## \[[^\]]+\] /, '').replace('01_policies/', ''))}</code>` },
  ];
  el.innerHTML = `<div class="wiki-rules" style="left:0;top:0;width:1400px">${rules.map((r, i) => `<div class="wiki-rule" data-i="${i + 1}"><div class="l"><i>AGENTS.md ${esc(r.n)}</i>\n${esc(r.l)}</div><div class="r">${r.r}</div></div>`).join('')}</div>`;
  const box = el.querySelector('.wiki-rules');
  return { step(k) {
    const n = rules.length;
    box.classList.toggle('sel', k >= 1 && k <= n);
    box.querySelectorAll('.wiki-rule').forEach((x) => { const i = +x.dataset.i; x.classList.toggle('on', i === k); x.classList.toggle('wiki-hide', i > Math.max(1, k)); });
  } };
};

/* ---------------------------------------------------------------- 11 · the query, call by call: what the model sees */
const SEGC = (p) => (p.what === 'system prompt' ? 'sys' : /index/.test(p.what) ? 'idx' : p.what === 'question' ? 'q' : /reply/.test(p.what) ? 'prev' : 'pg');
const SEGN = (p) => (p.what === 'system prompt' ? 'system' : p.what === 'index.md' ? 'index.md' : /slugs/.test(p.what) ? 'index, short' : p.what === 'question' ? 'Q'
  : /reply/.test(p.what) ? 'its reply' : (p.what.match(/\[\[([^\]]+)\]\]/) || [, p.what])[1]);
FIGS.wiki_query = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const C = d.query.calls, max = Math.max(...C.map((c) => c.tokens_in));
  const width = 1080;
  const rep = (c) => { try { const a = JSON.parse(c.reply); return a.action === 'open' ? `<b>open</b> ${a.pages.map((p) => `<code>${esc(p)}</code>`).join(' ')}: “${esc(a.why)}”` : `<b>${esc(a.action)}</b>: “${esc(a.why.slice(0, 150))}…”`; } catch (e) { return esc((c.reply || '').slice(0, 230)) + '…'; } };
  el.innerHTML = `<div class="wiki-ctx" style="left:0;top:0;width:1400px">
    ${C.map((c, i) => `<div class="wiki-call" data-k="${i}"><div class="lab"><b>${c.kind === 'answer' ? 'Answer call' : 'Call ' + c.call}</b>${fmt(c.tokens_in)} tokens in</div>
      <div><div class="wiki-bar" style="width:${Math.round(width * c.tokens_in / max)}px">${c.parts.map((p, j) => `<button class="wiki-seg ${SEGC(p)}" data-c="${i}" data-p="${j}" style="flex:${p.tokens} 1 0" title="${esc(p.what)}">${esc(SEGN(p))}</button>`).join('')}</div>
      <div class="rep">${c.kind === 'answer' ? `<b>answer</b> (${fmt(c.tokens_out)} tokens out): “${esc(c.reply.slice(0, 170))}…”` : rep(c)}</div></div></div>`).join('')}
    <div class="wiki-peek" style="left:164px;width:1236px;top:318px;height:186px" data-k="0"><span class="h">click a part of a bar to see what the model saw</span></div>
    <div class="wiki-card cb" data-k="3" style="left:164px;width:1236px;top:522px;height:64px;padding:12px 18px;font-size:18px"><b>Missing from the answer:</b> ${d.query.missing.map((m) => `<code>${esc(m)}</code>`).join(' · ')}</div>
  </div>`;
  const peek = el.querySelector('.wiki-peek');
  const show = (i, j) => {
    el.querySelectorAll('.wiki-seg').forEach((b) => b.classList.toggle('on', +b.dataset.c === i && +b.dataset.p === j));
    const p = C[i].parts[j];
    const ls = p.head.split('\n').filter((l) => l.trim() && !/^\|[-| ]*\|?$/.test(l.trim())).slice(0, 5).map((l) => (l.length > 150 ? l.slice(0, 149) + '…' : l));
    peek.innerHTML = `<span class="h">${C[i].kind === 'answer' ? 'answer call' : 'call ' + C[i].call} · ${esc(p.what)} · ${fmt(p.tokens)} tokens · ${fmt(p.chars)} characters</span>${esc(ls.join('\n'))}${p.chars > 420 || ls.length >= 5 ? '\n…' : ''}`;
  };
  el.querySelectorAll('.wiki-seg').forEach((b) => stopClick(b, () => show(+b.dataset.c, +b.dataset.p)));
  return { step(k) {
    at(el, k);
    if (k === 0) show(0, 1); else if (k === 1) show(1, 5); else show(2, 2);
  } };
};

/* ---------------------------------------------------------------- 12 · chunks or pages, and one page that joins files */
FIGS.wiki_chunks = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const Q = d.query, B = d.brightcell;
  const files = B.sources;
  const fi = (f) => files.findIndex((x) => short(x) === short(f) || f.includes(short(x).replace(/\.eml$|\.md$/, '')));
  const rag = Q.rag.filter((p) => p.what !== 'system prompt' && p.what !== 'question');
  const wikiTot = Q.calls.reduce((a, c) => a + c.tokens_in, 0);
  const ragTot = Q.rag_recorded.tokens_in;
  const W2 = 1400;
  el.innerHTML = `<div style="position:absolute;left:0;top:0;width:1400px">
      <div class="wiki-call" data-k="0"><div class="lab"><b>RAG</b>${fmt(ragTot)} tokens, 1 call</div>
        <div><div class="wiki-bar" style="width:${Math.round(1240 * ragTot / wikiTot)}px">${rag.map((p) => { const k = fi(p.what); return `<button class="wiki-seg ${k >= 0 ? 'ch wiki-f' + k : 'chd'}" title="${esc(p.what)}" style="flex:${p.tokens} 1 0"></button>`; }).join('')}</div>
        <div class="rep">10 chunks of about 200 tokens. ${rag.filter((p) => fi(p.what) >= 0).length} of them come from the ${files.length} files the Brightcell page below was compiled from; one is D’s own Q&amp;A on battery packs.</div></div></div>
      <div class="wiki-call" data-k="1"><div class="lab"><b>LLM Wiki</b>${fmt(wikiTot)} tokens, 3 calls</div>
        <div><div class="wiki-bar" style="width:1240px">${Q.calls.map((c) => c.parts.map((p) => `<button class="wiki-seg ${SEGC(p)}" title="${esc(p.what)}" style="flex:${p.tokens} 1 0"></button>`).join('')).join('<span style="width:8px"></span>')}</div>
        <div class="rep">index.md once (${fmt(Q.calls[0].parts.find((p) => p.what === 'index.md').tokens)} tokens), then whole pages, sent twice: to choose, then to answer.</div></div></div>
    </div>
    <div class="wiki-pg wiki-bc" data-k="2" style="left:0;top:236px;width:930px;height:370px"><div class="top"><b>sup-brightcell-energy.md</b><code>the full wiki · ${B.sources.length} source files</code></div>
      <div class="wiki-pgin"><div class="wiki-pgsc">${B.sentences.map((s) => (s.kind === 'head' ? `<h5>${esc(s.text)}</h5>` : `<div class="wiki-sn">${s.files.map((f) => `<span class="wiki-f${files.indexOf(f)}" style="display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:4px"></span>`).join('')}${wl(s.text)}</div>`)).join('')}</div></div></div>
    <div class="wiki-card cw" data-k="2" style="left:960px;top:236px;width:440px;height:370px;font-size:16px"><div class="wiki-fl">${files.map((f, i) => `<span><i class="wiki-f${i}"></i>${esc(short(f))}</span>`).join('')}</div>
      <p style="margin:12px 0 0;font-size:16.5px;line-height:1.4">One page already joins a meeting and three e-mails: the join was done once, at ingest. RAG must find the same pieces again for every question.</p></div>`;
  return { step(k) {
    at(el, k);
    const sc = el.querySelector('.wiki-bc .wiki-pgsc'); if (sc && k >= 2) fitWindow([...sc.children], [], boxH(el.querySelector('.wiki-bc .wiki-pgin'), 30));
  } };
};

/* ---------------------------------------------------------------- the failure slides: small, real, two or three cards each */
FIGS.wiki_fail = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const F = d.fail, kind = el.dataset.kind;
  const card = (x, y, w, h, cls, k, inner) => `<div class="wiki-card ${cls}" data-k="${k}" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px">${inner}</div>`;
  let html = '';
  if (kind === 'never') {
    const N = F.never_compiled, pages = Object.entries(N.facts_by_page);
    const mx = Math.max(...pages.map((p) => p[1]));
    html = card(0, 0, 640, 480, 'cw', 0, `<span class="wiki-tag">${esc(N.qid)}</span><h3>“${esc(N.question)}”</h3>
        <span class="q g">${esc(N.gold)}…</span><span class="src">${esc(short(N.file))}, p. ${N.gold_loc.page}, §${esc(N.gold_loc.section)}</span>
        <div style="margin-top:14px;font-size:17px"><b>Facts the ingest took from this manual, by page</b> (${N.facts_from_file} in all, ${N.read_calls} calls):</div>
        <div style="display:flex;align-items:flex-end;gap:6px;height:150px;margin-top:8px">${Array.from({ length: 15 }, (_, i) => { const v = N.facts_by_page[String(i + 1)] || 0; return `<div style="flex:1;text-align:center;font:500 12.5px/1.2 var(--mono);color:${i + 1 === N.gold_loc.page ? 'var(--before)' : 'var(--ink-3)'}"><div style="height:${Math.round(120 * v / mx)}px;background:${i + 1 === N.gold_loc.page ? 'var(--before)' : '#bcd4f6'};border-radius:5px 5px 0 0;margin-bottom:3px"></div>${v}<br>p.${i + 1}</div>`; }).join('')}</div>
        <div style="margin-top:8px;font-size:17px">Page ${N.gold_loc.page}: <b>0 facts</b>. No page of the wiki says “do not press Save again”.</div>`) +
      card(680, 0, 720, 190, 'cb', 1, `<span class="wiki-tag b">LLM Wiki</span> opened ${N.wiki_opened.length} pages, then:<span class="q r">${esc(N.wiki_answer.slice(0, 160))}</span>`) +
      card(680, 220, 720, 230, 'ca', 2, `<span class="wiki-tag a">RAG</span> searched the raw manual:<span class="q a">${esc(N.rag_answer.replace(/\*\*/g, '').slice(0, 230))}…</span>`);
  } else if (kind === 'wrong') {
    const X = F.wrong_compile, I = X.its;
    html = card(0, 0, 690, 600, 'cw sm', 0, `<span class="wiki-tag b">wrong</span><span class="wiki-tag">our one-source wiki</span><h3>The UN 38.3 page’s infobox</h3>
        <table class="wiki-ibx" style="font-size:16px">${X.infobox_before.map(([a, b]) => `<tr${/enforcement/.test(a) ? ' style="background:#fdece4"' : ''}><td>${esc(a)}</td><td>${esc(b)}</td></tr>`).join('')}</table>
        <span class="q r">${esc(X.lead_claim.replace(/\s*(\[\^r\d+\])+/g, ''))}</span>
        <div style="font-size:16.5px;margin:10px 0 4px">What Ledgerline really does:</div><span class="q g">${esc(X.truth[0])}</span><span class="src">${esc(short(X.truth_files[0]))}</span><span class="q g">${esc(X.truth[1])}</span><span class="src">${esc(short(X.truth_files[1]))}</span>
        <div style="font-size:16px;margin-top:8px;color:var(--ink-2)">D says no order <i>may</i> be placed; the model wrote that the system <i>blocks</i>. The lead’s keys point to real quotes from §6.2, so the check passed; the infobox line has no key at all. The full build, which read these two files, wrote: “${esc(X.full_build_line)}”</div>`) +
      card(720, 0, 680, 600, 'cb sm', 1, `<span class="wiki-tag b">merged</span><span class="wiki-tag">the full wiki</span><h3>The IT Security Policy filed as HR-only</h3>
        <div style="font-size:17px">Its page went to <code>${esc(I.path)}</code> (audience <b>${esc(I.audience)}</b>), because a file in the confidential HR folder also names POL-ITS-008:</div>
        <span class="q">${esc(I.readme)}</span><span class="src">01_policies/HR/CONFIDENTIAL/README_ACCESS.txt</span>
        <div style="font-size:17px;margin-top:8px">The build code’s registry met the code there first and marked the page HR. So this sentence is hidden from every staff query:</div>
        <span class="q r">${esc(I.line)}</span>
        <div style="font-size:17px;margin-top:8px">Q-609 (password rules): the wiki missed “${esc(I.q609_wiki_missing.join('”, “'))}”; RAG answered correctly. Lint findings on this page: <b>${I.lint_findings}</b>.</div>`);
  } else if (kind === 'stale') {
    const S = F.stale;
    html = card(0, 0, 690, 300, 'cw', 0, `<span class="wiki-tag">1 Sep 2026</span><span class="wiki-tag b">AMD-SUP-2026-02 in force</span><h3>Until someone re-ingests, the page says:</h3>
        <span class="q r">${esc(S.before_lead.replace(/\s*(\[\^r\d+\])+/g, '').replace(/\[\[[^|]+\|([^\]]+)\]\]/g, '$1'))}</span>
        <div style="font-size:17px">No 12-month window, no 60-day margin. Brightcell’s report, being renewed, is the case Emma needs.</div>`) +
      card(720, 0, 680, 300, 'ca', 1, `<span class="wiki-tag a">after the update</span><h3>Only the touched pages change</h3>
        <span class="q a">${esc(S.after_lead.replace(/\s*(\[\^r\d+\])+/g, '').replace(/\[\[[^|]+\|([^\]]+)\]\]/g, '$1'))}</span>
        <div style="font-size:17px"><code>pol-pur-001.md</code> was ${S.pol_untouched ? '<b>not touched</b>' : 'changed'}: its §6 still says only “a valid UN 38.3 certificate”, with no link to the amendment.</div>`) +
      card(0, 330, 1400, 150, 'cb', 2, `<h3>Staleness is a schedule, not a bug</h3><div style="font-size:18px">The wiki is as new as its last ingest. RAG’s index is as new as its last re-chunk, which costs no model call, so it can run on every file change. The wiki’s re-ingest costs model calls and, in production, a review of the diff, so it tends to run in batches.</div>`);
  } else if (kind === 'cost') {
    const C = F.cost;
    html = `<div class="wiki-card cw" data-k="0" style="left:0;top:0;width:1400px;height:340px"><table class="wiki-t">
        <tr><th>operation</th><th class="n">model calls</th><th class="n">tokens in</th><th class="n">tokens out</th><th class="n">time</th><th class="n">cost</th></tr>
        <tr><td>Ingest D alone (6 pages)</td><td class="n">${C.D.calls}</td><td class="n">${fmt(C.D.tokens_in)}</td><td class="n">${fmt(C.D.tokens_out)}</td><td class="n">${sec(C.D.read_s + C.D.seconds.merge + C.D.seconds.write)}</td><td class="n">${usd(C.D.usd)}</td></tr>
        <tr><td>Update: AMD-SUP-2026-02 (${C.amd.touched} pages)</td><td class="n">${C.amd.calls}</td><td class="n">${fmt(C.amd.tokens_in)}</td><td class="n">${fmt(C.amd.tokens_out)}</td><td class="n">${sec(C.amd.seconds.total)}</td><td class="n">${usd(C.amd.usd)}</td></tr>
        <tr><td>Update: patch note RN-7.2.3-P6 (${C.rn_p6.touched} pages)</td><td class="n">${C.rn_p6.calls}</td><td class="n">–</td><td class="n">–</td><td class="n">${sec(C.rn_p6.seconds)}</td><td class="n">${usd(C.rn_p6.usd)}</td></tr>
        <tr style="background:var(--g1)"><td><b>Build: all ${fmt(C.build.files)} files</b> (${fmt(C.build.parts)} parts, ${fmt(C.build.pages)} pages)</td><td class="n">${fmt(C.build.calls)}</td><td class="n">${fmt(C.build.tokens_in)}</td><td class="n">${fmt(C.build.tokens_out)}</td><td class="n">${esc(C.build.minutes)} min, ${C.build.workers} workers</td><td class="n">$${C.build.usd.toFixed(2)}</td></tr>
        <tr data-k="1" style="background:var(--g4)"><td><b>RAG: re-chunk and index all files</b></td><td class="n">0</td><td class="n">–</td><td class="n">–</td><td class="n">${C.rag.chunk_s} s + ${C.rag.bm25_build_s} s</td><td class="n">$0</td></tr>
      </table><div class="tiny" style="margin-top:10px">gemini-3.8-flash, priced at the harness’s $0.825 / $4.125 per million tokens in / out. D’s READ call (${sec(C.D.read_s)} when recorded) was replayed from the full build’s recording; its merge and six WRITE calls and both updates ran live. RAG times: chunking and BM25 build for ${fmt(C.rag.n_chunks)} chunks, measured in the grid.</div></div>` +
      card(0, 370, 1400, 130, 'cb', 2, `<h3>Every source is read by a model, and every touched page is rewritten</h3><div style="font-size:18px">Time and money grow with the documents, not with the questions. The build is a batch job; a busy repository needs an update queue.</div>`);
  } else if (kind === 'early') {
    const E = F.stops_early;
    const seen = E.where.filter((w) => w.in_answer_context.length), unseen = E.where.filter((w) => !w.in_answer_context.length);
    html = card(0, 0, 600, 515, 'cw', 0, `<span class="wiki-tag">Emma’s question, the race’s recorded run</span><h3>Index, three pages, done</h3>
        <ol style="margin:8px 0 0;padding-left:24px;font-size:18px">${E.chain.filter((s) => s.step !== 'done').map((s) => `<li><code>${esc(s.what)}</code></li>`).join('')}<li><b>done</b> after ${E.nav_calls} calls</li></ol>
        <div style="font-size:17px;margin-top:10px">Its reason for stopping names an amendment it never opened:</div><span class="q r">${esc(E.why_done.slice(0, 200))}…</span>`) +
      card(630, 0, 770, 345, 'cb', 1, `<span class="wiki-tag b">6 facts missing from the answer: where they were</span>
        <table class="wiki-t" style="font-size:16px;margin-top:6px"><tr><th>fact</th><th>in the answer call’s context?</th></tr>
        ${unseen.map((w) => `<tr><td><code>${esc(w.fact)}</code></td><td>no: only on pages never opened, e.g. <code>${esc(w.pages[0])}</code></td></tr>`).join('')}
        ${seen.map((w) => `<tr><td><code>${esc(w.fact)}</code></td><td><b>yes</b>, on <code>${esc(w.in_answer_context[0])}</code>; the answer left it out</td></tr>`).join('')}</table>`) +
      card(630, 365, 770, 150, 'ca', 2, `<span class="wiki-tag a">multi-hop questions (21), answer correct</span><div style="font-size:18px;margin-top:6px">${Object.entries(E.multi_hop).map(([m, v]) => `${esc({ rag: 'RAG', wiki: 'Wiki, navigation', hybrid: 'Wiki, hybrid', sections: 'Wiki, sections only' }[m])} <b>${(100 * v).toFixed(0)}%</b>`).join(' · ')}</div><div class="tiny" style="margin-top:6px">Two failures in one run: the reader stopped early, and the answer step dropped facts it had. logs/race.json</div>`);
  } else if (kind === 'codes') {
    const X = F.exact_codes, b = X.by_type;
    html = card(0, 0, 690, 450, 'cw', 0, `<span class="wiki-tag">${esc(X.qid)}</span><h3>“${esc(X.question)}”</h3>
        <div style="font-size:17px">The source: <b>${esc(X.gold)}</b></div>
        <div style="font-size:17px;margin-top:8px">The page the ingest wrote is titled <b>${esc(X.page_title)}</b> and says:</div>
        <span class="q r">${esc(X.page_line.replace(/\s*(\[\^r\d+\])+/g, '').replace(/`/g, ''))}</span>
        <div style="font-size:17px">The exact message was paraphrased away at compile time. The wiki’s answer missed “${esc(X.wiki_missing.join('”, “'))}”; RAG quoted it.</div>
        <div style="font-size:16px;margin-top:10px;color:var(--ink-2)">And to find the page at all: index.md lists the ${X.n_error_pages} error pages as one line, “${esc(X.index_line.replace(/^- /, ''))}”, so the model must guess the slug.</div>`) +
      card(720, 0, 680, 360, 'ca', 1, `<span class="wiki-tag a">exact-code questions (${b.wiki.n})</span>
        <table class="wiki-t" style="margin-top:8px"><tr><th></th><th class="n">recall@5</th><th class="n">answer correct</th></tr>
        <tr><td>RAG</td><td class="n">${b.rag['recall@5'].toFixed(2)}</td><td class="n">${(100 * b.rag.answer_correct).toFixed(0)}%</td></tr>
        <tr><td>Wiki, navigation</td><td class="n">${b.wiki['recall@5'].toFixed(2)}</td><td class="n">${(100 * b.wiki.answer_correct).toFixed(0)}%</td></tr></table>
        <div style="font-size:17px;margin-top:14px">BM25 matches the code as one rare token in the raw text. The wiki answers from a page that cites a list, not the manual page the golden set expects, so recall@5 drops even when the answer is right.</div>`);
  }
  el.innerHTML = html;
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- lint */
FIGS.wiki_lint = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const L = d.fail.lint;
  const bs = L.by_source;
  el.innerHTML = `<div class="wiki-card cw" data-k="0" style="left:0;top:0;width:690px;height:500px"><h3>${fmt(L.n)} findings in ${L.seconds.toFixed(0)} s</h3>
      <div style="font-size:17px">by code ${fmt(bs.code)} · recorded at ingest ${fmt(bs['ingest-read'] + bs['ingest-write'])} · model review ${fmt(bs.review)} ($${L.review_usd.toFixed(2)})</div>
      <div style="font-size:17px;margin:12px 0 4px"><b>On the pages of Emma’s question:</b></div>
      ${L.ours.map((f) => `<span class="q"><span class="wiki-tag">${esc(f.kind.replace(/_/g, ' '))}</span>${esc(f.detail.slice(0, 210))}${f.detail.length > 210 ? '…' : ''}</span>`).join('')}
      <div style="font-size:16px;color:var(--ink-2);margin-top:6px">r35 is a ${L.r35_quote_words}-word quote: the model ignored “5 to 25 words”, and the long quote crosses a line the check could not match.</div>
      <div style="font-size:17px;margin-top:10px">Of the ${L.planted.n} problems planted in Henrik’s dump, lint found <b>${L.planted.found}</b>.</div></div>
    <div class="wiki-card ca" data-k="1" style="left:720px;top:0;width:680px;height:220px"><span class="wiki-tag a">lint can fix</span><ul style="font-size:18px">
      <li>citations whose quote is not at the cited place</li><li>orphan pages, broken links</li><li>superseded or future rules stated as current</li><li>contradictions between pages</li></ul></div>
    <div class="wiki-card cb" data-k="2" style="left:720px;top:250px;width:680px;height:250px"><span class="wiki-tag b">lint cannot see</span><ul style="font-size:18px">
      <li>a fact that never reached any page (Q-104)</li><li>a page filed under the wrong audience (POL-ITS-008: ${d.fail.wrong_compile.its.lint_findings} findings)</li><li>a reader that stops too early</li></ul>
      <div style="font-size:16px;color:var(--ink-2);margin-top:6px">For these we need the golden set: questions with known answers.</div></div>`;
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- engineering: what it costs to run, and how we measure it */
FIGS.wiki_eng = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const R = d.eng.race, w = R.wiki, r = R.rag;
  const row = (lab, a, b, k) => `<tr data-k="${k}"><td>${lab}</td><td class="n">${a}</td><td class="n">${b}</td></tr>`;
  el.innerHTML = `<div class="wiki-card cw" style="left:0;top:0;width:760px;height:480px"><h3>Per question, on the race’s ${d.eng.n} questions</h3>
      <table class="wiki-t"><tr><th></th><th class="n">LLM Wiki (navigation)</th><th class="n">RAG</th></tr>
      ${row('model calls before the answer', (w.llm_calls_per_q - 1).toFixed(2), '0', 0)}
      ${row('retrieval p50 / p95', `${sec(w.retrieval_p50_s)} / ${sec(w.retrieval_p95_s)}`, `${(r.retrieval_p50_s * 1000).toFixed(0)} / ${(r.retrieval_p95_s * 1000).toFixed(0)} ms`, 0)}
      ${row('time to answer p50 / p95', `${sec(w.answer_p50_s)} / ${sec(w.answer_p95_s)}`, `${sec(r.answer_p50_s)} / ${sec(r.answer_p95_s)}`, 0)}
      ${row('cost per question', usd(w.cost_per_q_usd, 4), usd(r.cost_per_q_usd, 4), 0)}
      ${row('recall@5 (raw sources)', w['recall@5'].toFixed(2), r['recall@5'].toFixed(2), 1)}
      ${row('answer correct (judge)', (100 * w.answer_correct).toFixed(1) + '%', (100 * r.answer_correct).toFixed(1) + '%', 1)}
      ${row('citation correct', (100 * w.citation_correct).toFixed(1) + '%', (100 * r.citation_correct).toFixed(1) + '%', 1)}
      </table><div class="tiny" style="margin-top:10px">logs/race.json. Section 8 races all four methods; here only the two you have now met.</div></div>
    <div class="wiki-card ca" data-k="2" style="left:790px;top:0;width:610px;height:480px"><h3>The same test as RAG</h3><ol style="font-size:18px;padding-left:24px;margin:0">
      <li>The same ${d.eng.n} golden questions, each with its gold sources and must-contain facts.</li>
      <li>The method returns items: for RAG chunks, for the wiki pages, each page carrying the raw sources its keys cite.</li>
      <li>One shared answer step: the same prompt, the same 250-word cap, the same model.</li>
      <li>The same checks: recall@5 against the gold locations, must-contain facts, a judge model, and whether citations point at gold sources.</li></ol>
      <div style="font-size:17px;margin-top:12px">Emma’s question through this harness is what we just watched: 3 calls, ${fmt(d.query.calls.reduce((a, c) => a + c.tokens_in, 0))} tokens in, and ${d.query.missing.length} must-contain facts missing.</div></div>`;
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- where the wiki lives */
FIGS.wiki_store = (el) => {
  const d = W(); if (!d) return need(el, 'wiki_data.js');
  const S = d.eng.wiki_store, r = d.eng.race;
  el.innerHTML = `<div class="wiki-card cw" data-k="0" style="left:0;top:0;width:445px;height:470px"><span class="wiki-tag a">files</span><h3>A git repository of markdown</h3>
      <div style="font-size:17px">Ours: <code>ledgerline/ledgerline/wiki_v4/</code>: <code>pages/</code>, <code>restricted/</code>, <code>lists/</code>, <code>index.md</code>, <code>log.md</code>, <code>AGENTS.md</code>, <code>manifest.json</code>.</div>
      <div style="font-size:17px;margin-top:8px">${fmt(S.pages)} pages, ${fmt(S.words)} words, ${fmt(S.links)} links (${fmt(S.links_resolved)} resolve), ${fmt(S.references)} references.</div>
      <div style="font-size:17px;margin-top:8px">For production, make each ingest a commit on a branch, so a person reads the diff (as we did for the amendment) before staff see it. <code>log.md</code> and the git history replay how every page came to be.</div></div>
    <div class="wiki-card cw" data-k="1" style="left:477px;top:0;width:445px;height:470px"><span class="wiki-tag a">search</span><h3>An index over its sections</h3>
      <div style="font-size:17px">Navigation is slow (${sec(r.wiki.retrieval_p50_s)} p50). So we also cut the pages at their headings: ${fmt(S.sections)} sections, searched with the same BM25 and bge-small as RAG, fused by RRF, no model call.</div>
      <div style="font-size:17px;margin-top:8px">“Sections only”: ${(r.sections.retrieval_p50_s * 1000).toFixed(1)} ms p50, answer correct ${(100 * r.sections.answer_correct).toFixed(1)}%. “Hybrid” (search, then navigate): ${(100 * r.hybrid.answer_correct).toFixed(1)}%.</div>
      <div style="font-size:17px;margin-top:8px">index.md alone is ${fmt(S.index_tokens)} tokens, read on every navigated question.</div></div>
    <div class="wiki-card cw" data-k="2" style="left:955px;top:0;width:445px;height:470px"><span class="wiki-tag a">permissions</span><h3>One audience per page</h3>
      <div style="font-size:17px">Every page carries <code>audience: staff</code> or <code>hr</code> in its front matter. The ${S.hr} HR pages live in <code>restricted/</code> with their own index; <code>index.md</code> never lists them.</div>
      <div style="font-size:17px;margin-top:8px">The reader checks the user’s role before it opens a page, and the section search filters before it ranks. The page is the unit of permission, so one wrongly filed page hides all of it (POL-ITS-008).</div></div>`;
  return { step(k) { at(el, k); } };
};
})();
