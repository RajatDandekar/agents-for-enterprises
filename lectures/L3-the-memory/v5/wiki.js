/* Lecture 3 v5 · Section 7, the LLM Wiki, reworked 6 Nov 2026: a one-page amendment first, then D, then one question
   moving through the wiki (an animation that plays by itself and steps on clicks).
   Figures FIGS.wiki_<name>(el) -> { step(k) }, k = the number of .step elements shown on the slide.
   Every passage, slug and number comes from window.L3V5.wiki (v5/wiki_data.js): .simple is written by
   experiments/v5_wiki_simple_data.py from logs/v5_wiki_simple_*.json (6 Nov runs) and logs/v5_wiki_ingest|update.json;
   the rest by experiments/v5_wiki_data.py. Loaded after figs2.js. */
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


const S = () => (W() && W().simple) || null;
const strip = (s) => String(s || '').replace(/\s*(\[\^r\d+\])+/g, '').replace(/\[\[[^|\]]+\|([^\]]+)\]\]/g, '$1').replace(/\[\[([^\]]+)\]\]/g, '$1');

/* ---------------------------------------------------------------- shared: a markdown file as numbered lines */
/* Show a window of rows that fits H: every lit row (if they fit), then the rows nearest to them. A row that follows a
   hidden row gets a dashed top edge, so a skipped stretch is visible; the line numbers are the file's own. */
function fit2(rows, lit, H) {
  rows.forEach((r) => { r.style.display = ''; r.classList.remove('gap'); });
  const hh = rows.map((r) => r.offsetHeight);
  const keep = new Set();
  let tot = 0;
  for (const i of lit) { if (tot + hh[i] <= H) { keep.add(i); tot += hh[i]; } }
  if (!keep.size) { for (let i = 0; i < rows.length && tot + hh[i] <= H; i++) { keep.add(i); tot += hh[i]; } }
  else {
    for (let d = 1; d < rows.length; d++) {
      let added = false;
      for (const i of [...keep]) for (const j of [i + d, i - d]) {
        if (j < 0 || j >= rows.length || keep.has(j)) continue;
        // only grow a window outward from rows already kept, so kept rows stay in runs
        if (!keep.has(j + (j > i ? -1 : 1))) continue;
        if (tot + hh[j] <= H) { keep.add(j); tot += hh[j]; added = true; }
      }
      if (!added) break;
    }
  }
  let prev = -2;
  rows.forEach((r, i) => { const on = keep.has(i); r.style.display = on ? '' : 'none'; if (on) { if (prev !== -2 && i !== prev + 1) r.classList.add('gap'); prev = i; } });
  if (rows.length && !keep.has(0)) { const f = rows.findIndex((_, i) => keep.has(i)); if (f > 0) rows[f].classList.add('gap'); }
}
function mdLine(raw, fm) {
  let h = esc(raw);
  if (fm && /^\w+:/.test(raw)) return h.replace(/^(\w+):/, '<b class="k">$1</b>:');
  if (/^---$/.test(raw)) return `<span class="dim">${h}</span>`;
  if (/^#{1,6} /.test(raw)) return `<b class="hd">${h}</b>`;
  if (/^\|/.test(raw)) return `<span class="tb">${h}</span>`;
  return h.replace(/\[\[([^\]]+)\]\]/g, '<span class="wl">[[$1]]</span>').replace(/\[\^(r\d+)\]/g, '<span class="rk">[^$1]</span>')
    .replace(/\*\*([^*]+)\*\*/g, '<b>**$1**</b>');
}
/* a file as rows: blank lines dropped, numbers kept */
function fileView(text, { mono = true, numbers = true } = {}) {
  const lines = String(text || '').split('\n');
  let fmState = 0;
  const rows = [];
  lines.forEach((raw, i) => {
    if (i === 0 && raw === '---') fmState = 1; else if (fmState === 1 && raw === '---') fmState = 2;
    if (!raw.trim()) return;
    rows.push({ n: i + 1, raw, fm: fmState === 1 && raw !== '---' });
  });
  const box = document.createElement('div');
  box.className = 'wiki-fv' + (mono ? '' : ' sans') + (numbers ? '' : ' nonum');
  box.innerHTML = `<div class="wiki-fvsc">${rows.map((r) => `<div class="wiki-fvr"><i>${r.n}</i><span>${mono ? mdLine(r.raw, r.fm) : ansLine(r.raw)}</span></div>`).join('')}</div>`;
  const els = [...box.querySelectorAll('.wiki-fvr')];
  rows.forEach((r, i) => { r.el = els[i]; });
  return {
    box, rows,
    /* marks: [[test, cls], ...], test = substring | RegExp | (row) => bool */
    light(marks, H) {
      // marks are in priority order: when not every lit row fits, the earlier marks' rows are the ones shown
      const lit = [];
      rows.forEach((r) => r.el.classList.remove('hy', 'hb', 'hr', 'hg', 'on'));
      for (const [t, cls] of marks || []) {
        rows.forEach((r, i) => {
          const hit = typeof t === 'function' ? t(r) : t instanceof RegExp ? t.test(r.raw) : r.raw.includes(t);
          if (hit && !lit.includes(i)) { r.el.classList.add('on', 'h' + cls); lit.push(i); }
        });
      }
      box.classList.toggle('wiki-lit', lit.length > 0);
      fit2(els, lit, H ?? (box.clientHeight - 16));
      lit.sort((a, b) => a - b);
      // the dashed edges of skipped stretches add height: drop the visible row farthest from a lit row until it fits
      for (let g = 0; g < 300 && box.scrollHeight > box.clientHeight + 1; g++) {
        const vis = els.map((e, i) => i).filter((i) => els[i].style.display !== 'none');
        const free = vis.filter((i) => !lit.includes(i));
        const dist = (i) => (lit.length ? Math.min(...lit.map((j) => Math.abs(i - j))) : -i);
        const pick = free.length ? free.sort((a, b) => dist(b) - dist(a))[0] : vis[vis.length - 1];
        if (pick === undefined) break;
        els[pick].style.display = 'none';
        let prev = -2;
        els.forEach((e, i) => { e.classList.remove('gap'); if (e.style.display !== 'none') { if (i !== prev + 1) e.classList.add('gap'); prev = i; } });
        const f = els.findIndex((e) => e.style.display !== 'none'); if (f === 0) els[0].classList.remove('gap');
      }
      return lit;
    },
  };
}
function ansLine(raw) {
  return esc(raw).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/^- /, '• ').replace(/\[(\d)\]/g, '<span class="cite">$1</span>');
}

/* ---------------------------------------------------------------- 4 · start small: the amendment, read by hand */
FIGS.wiki_small = (el) => {
  const s = S(); if (!s) return need(el, 'wiki_data.js · simple');
  const A = s.amd, L = s.alone, hv = (k) => (A.header.find((r) => r[0] === k) || [])[1] || '';
  const doc = document.createElement('div');
  doc.className = 'wiki-doc wiki-amd'; doc.style.cssText = 'left:0;top:0;width:700px;height:610px';
  doc.innerHTML = `<div class="wiki-dtop"><b>PDF</b><span>${esc(short(L.file))} · 1 page</span></div>
    <div class="wiki-din"><div class="wiki-dsc">
      <div class="wiki-amdt">${esc(A.title)}</div>
      <div class="wiki-amdh">${esc(hv('Document'))} · version ${esc(hv('Version'))} · effective ${esc(hv('Effective'))} · ${esc(hv('Status'))}</div>
      ${A.clauses.map((c) => (c.kind === 'head' ? `<div class="wiki-dch">${esc(c.id)}. ${esc(c.text)}</div>`
        : `<div class="wiki-dc" data-c="${esc(c.id)}"><i>${esc(c.id)}</i><span>${esc(c.text)}</span></div>`)).join('')}
    </div></div>`;
  const hand = [
    { c: ['1.1', '1.2'], t: '<b>The amendment itself</b><span class="s">what changes, from 1 September 2026, and why</span>', p: 'a page for AMD-SUP-2026-02' },
    { c: ['1.1', '3.3'], t: '<b>The rule it replaces</b> lives in another document<span class="s">POL-SUP-003 §4.4: its page should hold the old rule and the new one</span>', p: 'a page for POL-SUP-003' },
    { c: ['1.1', '2.1'], t: '<b>UN 38.3 certificates</b>, a topic many documents talk about<span class="s">one topic page that every source about it adds to</span>', p: 'a topic page' },
    { c: ['3.2'], t: '<b>The senior buyer</b>, who runs the monthly expiry report<span class="s">a person’s job, written as a role</span>', p: 'a page for the role' },
  ];
  const list = document.createElement('div'); list.className = 'wiki-list'; list.style.cssText = 'left:740px;top:0;width:660px';
  list.innerHTML = `<div class="wiki-k">A careful reader would write</div>` +
    hand.map((h, i) => `<div class="wiki-li" data-k="${i + 1}" data-i="${i + 1}"><span class="n">→ ${esc(h.p)}</span>${h.t}</div>`).join('');
  const mdl = document.createElement('div'); mdl.className = 'wiki-list'; mdl.style.cssText = 'left:740px;top:0;width:660px';
  mdl.innerHTML = `<div class="wiki-k a">What the model wrote, reading only this page</div>` +
    L.reply_pages.map((p) => `<div class="wiki-li mdl"><span class="n">${p.n} fact${p.n > 1 ? 's' : ''}</span><code>${esc(p.slug)}.md</code><span class="s">${esc(p.title)}</span></div>`).join('') +
    `<div class="wiki-li" style="background:#fff;box-shadow:var(--shadow)"><b>${L.reply_pages.length} pages, ${L.facts} facts.</b> Our four, plus <code>items-bat</code>: the BAT-* battery packs, the lithium-cell parts of §3.1. Every fact carries a quote, and code found all ${L.verified} quotes in the page.</div>`;
  el.append(doc, list, mdl);
  const light = (ids) => {
    const rows = [...doc.querySelectorAll('.wiki-dc')];
    rows.forEach((r) => r.classList.toggle('on', ids.includes(r.dataset.c)));
    doc.classList.toggle('wiki-lit', ids.length > 0);
  };
  return { step(k) {
    const n = Math.min(k, hand.length);
    list.classList.toggle('wiki-hide', k > hand.length); mdl.classList.toggle('wiki-hide', k <= hand.length);
    at(list, n);
    list.querySelectorAll('.wiki-li').forEach((x) => x.classList.toggle('cur', +x.dataset.i === n));
    light(k === 0 || k > hand.length ? [] : hand[k - 1].c);
  } };
};

/* ---------------------------------------------------------------- 5 · the wiki is a folder of files */
const NOTE = {
  'index.md': 'the catalogue: one line per page; every question reads it first',
  'log.md': 'one line per ingest, only ever appended',
  'pages/': 'one markdown file per page',
  'lists/': 'pages named by a code, listed together',
  'restricted/': 'the index of HR-only pages (none here)',
  'facts.jsonl': 'every fact with its quote, one per line',
  'sources.jsonl': 'each source read: file, version, date',
  'manifest.json': 'the build’s record of pages and sources',
};
FIGS.wiki_tree = (el) => {
  const s = S(); if (!s) return need(el, 'wiki_data.js · simple');
  const L = s.alone, T = L.tree;
  const order = ['index.md', 'log.md', 'pages/', 'lists/', 'restricted/', 'facts.jsonl', 'sources.jsonl', 'manifest.json'];
  const files = {};
  T.forEach((p) => { const [a, b] = p.includes('/') ? [p.split('/')[0] + '/', p.split('/')[1]] : [p, null]; (files[a] = files[a] || []).push(b); });
  const open = { 'index.md': L.index_md, 'log.md': L.log_lines.join('\n') && ('# log.md\n\n' + L.log_lines.join('\n')) };
  Object.entries(L.pages).forEach(([k, v]) => { open['pages/' + k + '.md'] = v; });
  const row = (path, name, depth, dir) => `<div class="wiki-tr${open[path] ? ' click' : ''}${dir ? ' dir' : ''}" data-p="${esc(path)}" style="padding-left:${16 + depth * 26}px">
      <span class="ic">${dir ? '▸' : '·'}</span><code>${esc(name)}</code>${NOTE[path] ? `<span class="nt">${esc(NOTE[path])}</span>` : ''}</div>`;
  let html = row('', 'wiki/', 0, true);
  order.filter((o) => files[o]).forEach((o) => {
    if (o.endsWith('/')) { html += row(o, o, 1, true); files[o].forEach((f) => { html += row(o + f, f, 2, false); }); }
    else html += row(o, o, 1, false);
  });
  el.innerHTML = `<div class="wiki-tree" style="left:0;top:0;width:600px;height:610px">${html}
      <div class="wiki-tsum">${T.length} files · ${Object.keys(L.pages).length} pages · ${fmt(L.words)} words · ${L.links} links · ${L.refs} references</div></div>
    <div class="wiki-viewer" style="left:640px;top:0;width:760px;height:610px"><div class="top"><span class="fn"></span></div><div class="wiki-vbody"></div></div>`;
  const vw = el.querySelector('.wiki-viewer'), body = vw.querySelector('.wiki-vbody'), fn = vw.querySelector('.fn');
  const steps = ['index.md', 'log.md', 'pages/amd-sup-2026-02.md'];
  const marks = { 'index.md': [['[[amd-sup-2026-02]]', 'y']], 'log.md': [['ingest |', 'y']], 'pages/amd-sup-2026-02.md': [] };
  const showFile = (p) => {
    el.querySelectorAll('.wiki-tr').forEach((r) => r.classList.toggle('sel', r.dataset.p === p));
    if (!p) { fn.innerHTML = 'Click a file, or step through: <code>index.md</code>, <code>log.md</code>, a page'; body.innerHTML = '<div class="wiki-vhint">Plain text files. Any editor opens them; git can track every change.</div>'; return; }
    fn.innerHTML = `<code>wiki/${esc(p)}</code>`;
    body.innerHTML = '';
    const v = fileView(open[p]); body.append(v.box);
    v.light(marks[p] || [], body.clientHeight - 20);
  };
  el.querySelectorAll('.wiki-tr.click').forEach((r) => stopClick(r, () => showFile(r.dataset.p)));
  return { step(k) { showFile(k ? steps[Math.min(k, steps.length) - 1] : ''); } };
};

/* ---------------------------------------------------------------- 6 · one page, opened */
FIGS.wiki_anat = (el) => {
  const s = S(); if (!s) return need(el, 'wiki_data.js · simple');
  const L = s.alone, A = L.anat, md = L.pages['amd-sup-2026-02'];
  const parts = [
    { h: 'Front matter', t: 'Between the <code>---</code> lines: title, type, slug, a one-line summary, who may read it, its sources, dates. Code reads these: <code>index.md</code> is built from the summaries; <code>audience</code> decides who may open the page.', m: [[(r) => r.fm || (r.raw === '---' && r.n < 15), 'y']] },
    { h: 'Lead', t: 'Two to four sentences: what this is, and what matters today. The first thing a reader sees.', m: [[A.lead, 'y']] },
    { h: 'Sections', t: 'Headings fixed by the page type in <code>AGENTS.md</code>: a policy gets one <code>###</code> per clause, then Versions and conflicts, See also, References.', m: [[/^#{2,3} /, 'y']] },
    { h: 'Links', t: '<code>[[pol-sup-003|POL-SUP-003]]</code> points at another page by its slug, like a blue link on Wikipedia. A reader can follow it.', m: [[A.link, 'b']] },
    { h: 'Citations', t: 'A key such as <code>[^r2]</code> ends each sentence. The References list turns it into the source: the file, page 1, §1. Anyone can check the sentence against the PDF.', m: [[A.key, 'g'], [A.ref, 'g']] },
  ];
  el.innerHTML = `<div class="wiki-viewer" style="left:0;top:0;width:860px;height:610px"><div class="top"><code>wiki/pages/amd-sup-2026-02.md</code><span class="dim">${md.split('\n').length} lines</span></div><div class="wiki-vbody"></div></div>
    <div class="wiki-list" style="left:900px;top:0;width:500px">${parts.map((p, i) => `<div class="wiki-li" data-k="${i + 1}" data-i="${i + 1}"><b>${i + 1} · ${p.h}</b><span class="s">${p.t}</span></div>`).join('')}</div>`;
  const body = el.querySelector('.wiki-vbody'), v = fileView(md); body.append(v.box);
  return { step(k) {
    at(el.querySelector('.wiki-list'), k);
    el.querySelectorAll('.wiki-li').forEach((x) => x.classList.toggle('cur', +x.dataset.i === k));
    v.light(k ? parts[k - 1].m : [], body.clientHeight - 20);
  } };
};

/* ---------------------------------------------------------------- 7 · ingest, step by step */
FIGS.wiki_ingest = (el) => {
  const s = S(); if (!s) return need(el, 'wiki_data.js · simple');
  const L = s.alone, C = L.calls, rd = C.find((c) => c.kind === 'read'), mg = C.find((c) => c.kind === 'merge'), wr = C.filter((c) => c.kind === 'write');
  const F = L.reply_fact, sec_ = L.seconds;
  const rail = [
    ['Read the source', 'one model call'], ['Decide the pages', 'the same reply, checked by code'],
    ['Write the pages', 'one model call per page'], ['Update index.md and log.md', 'code, no model'],
  ];
  const pan = [
    `<h3>One call reads the whole amendment</h3>
     <div class="wiki-flow"><span class="wiki-chip">instructions + <code>AGENTS.md</code></span><span class="wiki-chip">the names of pages that already exist</span><span class="wiki-chip y">the page itself</span><span class="ar">→</span><span class="wiki-chip a">${esc(rd && 'gemini-3.8-flash')}</span></div>
     <div class="wiki-num"><b>${fmt(rd.tokens_in)}</b> tokens in · <b>${fmt(rd.tokens_out)}</b> out · <b>${sec(rd.seconds)}</b></div>
     <div class="s">The list of existing names is why two sources about the same thing land on the same page.</div>`,
    `<h3>Its reply names the pages, with facts and quotes</h3>
     <div class="wiki-two"><div>${L.reply_pages.map((p) => `<div class="wiki-pl"><code>${esc(p.slug)}</code><span>${p.n} fact${p.n > 1 ? 's' : ''}</span></div>`).join('')}</div>
     <div class="wiki-fact"><div class="wiki-k">one fact for <code>amd-sup-2026-02</code></div><div>${esc(F.fact)}</div><div class="wiki-k" style="margin-top:8px">its quote, copied from the page</div><div class="q">“${esc(F.quote)}”</div></div></div>
     <div class="s">Code then searches the page for every quote: <b>${L.verified} of ${L.facts} found</b>. A small second call (${fmt(mg.tokens_in)} tokens) checks new names against old ones: none merged.</div>`,
    `<h3>One call per page writes its markdown</h3>
     <table class="wiki-t" style="font-size:17px;max-width:760px"><tr><th>page</th><th class="n">tokens in</th><th class="n">out</th><th class="n">seconds</th></tr>
     ${wr.map((c) => `<tr><td><code>${esc(c.page)}.md</code></td><td class="n">${fmt(c.tokens_in)}</td><td class="n">${fmt(c.tokens_out)}</td><td class="n">${c.seconds.toFixed(1)}</td></tr>`).join('')}</table>
     <div class="s">The writer sees that page’s facts, with keys, never the source. The calls run side by side: ${sec(sec_.write)} in all.</div>`,
    `<h3>Code lists the pages and logs the ingest</h3>
     <div class="wiki-k" style="margin-top:6px"><code>index.md</code>, rebuilt from each page’s summary</div><div class="wiki-line">${esc(L.index_lines.find((l) => l.includes('[[amd-sup-2026-02]]')))}</div>
     <div class="wiki-k" style="margin-top:14px"><code>log.md</code>, one line appended</div><div class="wiki-line">${esc(L.log_lines[0])}</div>`,
  ];
  el.innerHTML = `<div class="wiki-rail">${rail.map(([t, w], i) => `<div class="wiki-rs" data-i="${i + 1}"><span class="no">${i + 1}</span><b>${t}</b><span class="w">${w}</span></div>`).join('')}</div>
    <div class="wiki-card cw wiki-ipan" style="left:0;top:150px;width:1400px;height:350px"></div>
    <div class="wiki-card ca" data-k="5" style="left:0;top:520px;width:1400px;height:86px;font-size:20px"><b>${L.llm.calls} model calls · ${fmt(L.llm.tokens_in)} tokens in · ${fmt(L.llm.tokens_out)} out · ${usd(L.llm.usd)}</b> · model steps ${sec(sec_.read + sec_.merge + sec_.write)} (read ${sec(sec_.read)}, names ${sec(sec_.merge)}, writes ${sec(sec_.write)}). For one page.</div>`;
  const P = el.querySelector('.wiki-ipan');
  return { step(k) {
    const i = Math.min(k, 4);
    el.querySelectorAll('.wiki-rs').forEach((r) => { r.classList.toggle('on', +r.dataset.i === i); r.classList.toggle('done', +r.dataset.i < i); });
    P.innerHTML = i ? pan[i - 1] : `<h3>From one PDF page to five markdown files</h3><div class="s" style="font-size:20px">Four steps. Two are model calls, two are plain code. Click to walk through them on the amendment.</div>`;
    at(el, k);
  } };
};

/* ---------------------------------------------------------------- 8 · step up: D becomes six pages */
FIGS.wiki_six = (el) => {
  const s = S(); if (!s) return need(el, 'wiki_data.js · simple');
  const D = s.d, secs = D.sections, pages = [...D.pages].sort((a, b) => b.n - a.n);
  const sy = (i) => 26 + i * 54, py = (j) => 4 + j * 92;
  el.innerHTML = `<div class="wiki-k" style="position:absolute;left:0;top:-4px">D · POL-PUR-001 · sections</div>
    ${secs.map((x, i) => `<div class="wiki-sec" style="left:0;top:${sy(i)}px;width:330px"><i>${x.id === 'hdr' ? '—' : '§' + esc(x.id)}</i>${esc(x.title)}</div>`).join('')}
    <svg class="wiki-six" width="1400" height="620" style="position:absolute;left:0;top:0;overflow:visible">
      ${pages.map((p, j) => p.secs.map((sid) => { const i = secs.findIndex((x) => x.id === sid); const y1 = sy(i) + 22, y2 = py(j) + 38;
        return `<path data-k="${j === 0 ? 1 : 2}" class="${j === 0 ? 'm' : 'o'}" d="M332,${y1} C450,${y1} 410,${y2} 528,${y2}"/>`; }).join('')).join('')}
    </svg>
    ${pages.map((p, j) => `<div class="wiki-pc${j === 0 ? ' main' : ''}" data-k="${j === 0 ? 1 : 2}" style="left:530px;top:${py(j)}px;width:320px"><code>${esc(p.slug)}.md</code><span>${p.n} fact${p.n > 1 ? 's' : ''} · ${esc(p.type)}</span></div>`).join('')}
    <div class="wiki-k" data-k="2" style="position:absolute;left:0;top:582px;width:860px;text-transform:none;letter-spacing:0;font-size:15px;font-weight:400;color:var(--ink-2)">The policy’s own page takes ${pages[0].n} of ${D.facts} facts. The model proposed <code>topic-tax-codes</code>; the build’s name check mapped it to <code>data-tax-codes</code>.</div>
    <div class="wiki-file" data-k="3" style="left:890px;top:0;width:510px;height:606px"><span class="h">wiki/index.md · read first by every question</span><div class="wiki-ix"></div></div>`;
  const ix = el.querySelector('.wiki-ix');
  ix.innerHTML = D.index_lines.map((l) => (l.startsWith('## ') ? `<div class="hd">${esc(l)}</div>` : `<div>${esc(l)}</div>`)).join('');
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- 9 · the amendment joins D's wiki */
FIGS.wiki_join = (el) => {
  const s = S(); if (!s) return need(el, 'wiki_data.js · simple');
  const J = s.join, D = s.d, c = W().fail.cost.amd;
  const before = new Set(D.pages.map((p) => p.slug));
  const pages = J.tree.filter((p) => p.startsWith('pages/')).map((p) => p.slice(6, -3));
  const tag = (sl) => (J.created.includes(sl) ? ['new', '+ new'] : J.updated.includes(sl) ? ['upd', '~ rewritten'] : ['same', 'unchanged']);
  el.innerHTML = `<div class="wiki-tree" style="left:0;top:0;width:560px;height:610px">
      <div class="wiki-tr dir" style="padding-left:16px"><span class="ic">▸</span><code>wiki/pages/</code></div>
      ${pages.map((sl) => { const [cls, t] = tag(sl); return `<div class="wiki-tr jn ${cls}" data-new="${before.has(sl) ? 0 : 1}" style="padding-left:42px"><span class="ic">·</span><code>${esc(sl)}.md</code><span class="bd">${t}</span></div>`; }).join('')}
      <div class="wiki-tsum" data-k="1">${J.created.length} new, ${J.updated.length} rewritten, ${pages.length - J.created.length - J.updated.length} unchanged · ${c.calls} calls · ${sec(c.seconds.total)} · ${usd(c.usd)}<br><code>pol-pur-001.md</code> is unchanged: its §6 still has no link to the amendment.</div></div>
    <div class="wiki-card cw" data-k="2" style="left:600px;top:0;width:800px;height:392px"><span class="wiki-tag">topic-un-38-3-certificates.md · the lead</span>
      <div class="wiki-k b" style="margin-top:8px">before</div><span class="q r" style="font-size:16px">${esc(J.lead_before)}</span>
      <div class="wiki-k a" style="margin-top:6px">after</div><span class="q a" style="font-size:16px">${esc(J.lead_after)}</span></div>
    <div class="wiki-file" data-k="3" style="left:600px;top:408px;width:800px;height:200px"><span class="h">wiki/log.md</span>${J.log_lines.map((l, i) => `<div class="${i === J.log_lines.length - 1 ? 'hl' : ''}">${esc(l)}</div>`).join('')}</div>`;
  return { step(k) {
    at(el, k);
    el.querySelectorAll('.wiki-tr.jn').forEach((r) => { r.classList.toggle('wiki-gone', k < 1 && r.dataset.new === '1'); r.classList.toggle('show', k >= 1); });
  } };
};

/* ---------------------------------------------------------------- 10 · one question moves through the wiki (autoplays) */
FIGS.wiki_nav = (el) => {
  const s = S(); if (!s) return need(el, 'wiki_data.js · simple');
  const N = s.nav, H = N.hl, T = N.turns;
  const X = [0, 366, 732, 1098], CW = 302, CY = 62, CH = 360;
  const slot = ['index.md', 'a page', 'a linked page', 'the answer'];
  const name = ['wiki/index.md', 'pages/topic-un-38-3-certificates.md', 'pages/role-pur-senior-buyer.md', 'answer, with citations'];
  const texts = [N.index_md, N.pages['topic-un-38-3-certificates'], N.pages['role-pur-senior-buyer'], N.answer];
  el.classList.add('wiki-navfig');
  el.innerHTML = `<div class="wiki-nq"><span class="wiki-tag a">question</span>“${esc(N.question)}”</div>
    <svg class="wiki-nsvg" width="1400" height="640" viewBox="0 0 1400 640">
      <defs><marker id="wiki-nah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#0b57d0"/></marker></defs>
      <path class="ln" data-l="1" d="M${X[0] + CW + 4},${CY + 150} L${X[1] - 6},${CY + 150}"/>
      <path class="ln" data-l="2" d=""/>
      <path class="ln" data-l="3" d="M${X[2] + CW + 4},${CY + 150} L${X[3] - 6},${CY + 150}"/>
      <path class="ln src" data-l="4" d=""/>
      <circle class="dot" r="9" cx="-40" cy="-40" style="opacity:0"/>
    </svg>
    ${X.map((x, i) => `<div class="wiki-nc" data-i="${i}" style="left:${x}px;top:${CY}px;width:${CW}px;height:${CH}px">
        ${i === 1 || i === 2 ? `<div class="gh g2"></div><div class="gh g1"></div>` : ''}
        <div class="shut">${esc(slot[i])}</div>
        <div class="wiki-ncard"><div class="top">${i === 3 ? '<span class="ic a">A</span>' : '<span class="ic">md</span>'}<code>${esc(name[i])}</code></div><div class="bd"></div></div></div>
      <div class="wiki-ncap" data-i="${i}" style="left:${x}px;top:${CY + CH + 10}px;width:${CW + (i < 3 ? 40 : 0)}px"></div>`).join('')}
    <div class="wiki-nsrc"></div>
    <div class="wiki-nrail">${['Read index.md', 'Open the page', 'Follow a link', 'Answer, with its citation'].map((t, i) => `<div class="st" data-i="${i + 1}"><span class="no">${i + 1}</span>${t}</div>`).join('')}<div class="bar"><i></i></div></div>`;
  const svg = el.querySelector('.wiki-nsvg'), dot = svg.querySelector('.dot');
  const cards = [...el.querySelectorAll('.wiki-nc')], caps = [...el.querySelectorAll('.wiki-ncap')];
  const views = cards.map((c, i) => { const v = fileView(texts[i], { mono: i < 3, numbers: i < 3 }); c.querySelector('.bd').append(v.box); return v; });
  const src = el.querySelector('.wiki-nsrc'), bar = el.querySelector('.wiki-nrail .bar i');
  const opened1 = T[0].pages, opened2 = T[1].pages;
  const capHTML = [
    `<b>Turn 1</b> · ${fmt(T[0].tokens_in)} tokens in · ${sec(T[0].seconds)}<br>reply: open <code>${opened1.join('</code>, <code>')}</code>`,
    `the two cards behind it: <code>${opened1.slice(1).join('</code>, <code>')}</code>, opened in the same turn`,
    `<b>Turn 2</b> · ${fmt(T[1].tokens_in)} tokens in · ${sec(T[1].seconds)}<br>reply: follow the link to <code>role-pur-senior-buyer</code>`,
    `<b>Turn 3</b> · ${fmt(T[2].tokens_in)} tokens in · ${sec(T[2].seconds)} · reply: <b>done</b><br>behind it: <code>${opened2.filter((x) => x !== 'role-pur-senior-buyer').join(', ')}</code>, also opened in turn 2`,
    `<b>Answer call</b> · ${N.items.length} pages in, ${fmt(N.answer_tokens_in)} tokens · ${sec(N.answer_seconds)} · cites ${N.cited.sort().map((c) => `<span class="cite">${c}</span>`).join(' ')}`,
  ];
  const short_ = (f) => f.split('/').pop().replace(/\.pdf$/, '');
  const ref = H.role_ref.replace(/^\[\^r1\]: /, '');
  src.innerHTML = `<span class="cite">5</span><span class="ar">→</span><code>role-pur-senior-buyer.md</code> <span class="rk">[^r1]</span><span class="ar">→</span><b>${esc(short_(ref.split(',')[0]))}</b>, ${esc(ref.split(',').slice(1).join(',').trim())}<span class="ar">→</span><span class="q">3.2 “${esc(N.amd_clause)}”</span>`;
  /* scene → what is open and lit */
  const OPEN = [1, 2, 4, 5];
  const wrongNote = (r) => r.raw.includes(H.ans_wrong);
  let curScene = -1, timer = null, anim = null;
  const center = (node) => { const f = el.getBoundingClientRect(), r = node.getBoundingClientRect(), k = f.width / 1400 || 1; return { x: (r.left - f.left) / k, y: (r.top - f.top) / k, w: r.width / k, h: r.height / k }; };
  const lineFor = (l) => svg.querySelector(`.ln[data-l="${l}"]`);
  const moveDot = (path, instant) => {
    cancelAnimationFrame(anim);
    if (!path || instant || !path.getTotalLength || !path.getAttribute('d')) { dot.setAttribute('cx', -40); dot.setAttribute('cy', -40); dot.style.opacity = 0; return; }
    dot.style.opacity = 1;
    const L = path.getTotalLength(), t0 = performance.now(), dur = 750;
    const tick = (t) => { const u = Math.min(1, (t - t0) / dur), e = u < .5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2, p = path.getPointAtLength(e * L);
      dot.setAttribute('cx', p.x); dot.setAttribute('cy', p.y); if (u < 1) anim = requestAnimationFrame(tick); else { dot.style.opacity = 0; } };
    anim = requestAnimationFrame(tick);
  };
  const render = (sc, instant) => {
    cards.forEach((c, i) => c.classList.toggle('open', sc >= OPEN[i]));
    cards.forEach((c, i) => c.classList.toggle('now', [0, 1, 1, 2, 2, 3, 2][sc] === i && sc > 0));
    caps[0].innerHTML = sc >= 1 ? capHTML[0] : '';
    caps[1].innerHTML = sc >= 3 ? capHTML[2] : sc >= 2 ? capHTML[1] : '';
    caps[2].innerHTML = sc >= 5 ? capHTML[3] : sc >= 4 ? capHTML[3].split('<br>')[1] : '';
    caps[3].innerHTML = sc >= 5 ? capHTML[4] + '<div class="wiki-wrong">orange: from the infobox, wrong at ingest</div>' : '';
    const bh = (i) => cards[i].querySelector('.bd').clientHeight - 14;
    views[0].light(sc >= 1 ? opened1.map((p) => [`[[${p}]]`, 'y']) : [], bh(0));
    views[1].light(sc >= 5 ? [[H.topic_link, 'b'], [H.topic_wrong, 'r'], [H.topic_rule, 'y']] : sc >= 3 ? [[H.topic_link, 'b'], [H.topic_rule, 'y']] : sc >= 2 ? [[H.topic_rule, 'y']] : [], bh(1));
    views[2].light(sc >= 4 ? [[H.role_duty, 'y'], ...(sc >= 6 ? [[H.role_ref, 'g']] : [])] : [], bh(2));
    views[3].light(sc >= 6 ? [[H.ans_buyer, 'g'], [wrongNote, 'r'], [H.ans_rule, 'y']] : sc >= 5 ? [[H.ans_rule, 'y'], [H.ans_buyer, 'y'], [wrongNote, 'r']] : [], bh(3));
    src.classList.toggle('on', sc >= 6);
    el.querySelectorAll('.wiki-nrail .st').forEach((x) => { const st = [0, 1, 2, 3, 3, 4, 4][sc]; x.classList.toggle('on', +x.dataset.i === st); x.classList.toggle('done', +x.dataset.i < st); });
    // the link line starts at the lit [[link]] row of the page card
    const lr = views[1].rows.find((r) => r.raw.includes(H.topic_link));
    if (lr && lr.el.offsetParent) { const a = center(lr.el), b = center(cards[2]); const y1 = a.y + a.h / 2, y2 = b.y + 40;
      lineFor(2).setAttribute('d', `M${X[1] + CW - 6},${y1} C${X[1] + CW + 40},${y1} ${X[2] - 40},${y2} ${X[2] - 6},${y2}`); }
    const ar = views[3].rows.find((r) => r.raw.includes(H.ans_buyer));
    if (ar && ar.el.offsetParent && sc >= 6) { const a = center(ar.el), sb = center(src); lineFor(4).setAttribute('d', `M${X[3] + 30},${a.y + a.h}  L${X[3] + 30},${sb.y - 4}`); }
    svg.querySelectorAll('.ln').forEach((p) => { const l = +p.dataset.l; p.classList.toggle('on', (l === 1 && sc >= 2) || (l === 2 && sc >= 4) || (l === 3 && sc >= 5) || (l === 4 && sc >= 6)); });
    if (!instant && sc === curScene + 1) moveDot(lineFor({ 2: 1, 4: 2, 5: 3, 6: 4 }[sc]), false); else moveDot(null, true);
    curScene = sc;
  };
  const DUR = [1600, 3000, 2600, 2600, 2800, 3400, 5200];
  const stop = () => { clearTimeout(timer); timer = null; bar.style.width = '0'; };
  const play = (sc = 0) => {
    stop();
    const slide = el.closest('.slide');
    if (slide && !slide.classList.contains('active')) return;
    render(sc, sc === 0);
    bar.style.transition = 'none'; bar.style.width = (100 * sc / 6) + '%';
    requestAnimationFrame(() => { bar.style.transition = `width ${DUR[sc]}ms linear`; bar.style.width = (100 * Math.min(6, sc + 1) / 6) + '%'; });
    timer = setTimeout(() => play(sc >= 6 ? 0 : sc + 1), DUR[sc]);
  };
  el.__wikiNav = { play, stop, render, DUR };
  return { step(k, instant) {
    if (k === 0) { curScene = -1; play(0); return; }
    stop(); render(Math.min(k, 6), instant);
  } };
};

/* ---------------------------------------------------------------- 12 · where it fails: the top three */
FIGS.wiki_fail3 = (el) => {
  const d = W(); if (!d || !S()) return need(el, 'wiki_data.js');
  const F = d.fail, N = F.never_compiled, X = F.wrong_compile, E = F.stops_early, nav = S().nav;
  const card = (x, k, cls, tag, h, inner) => `<div class="wiki-card ${cls} wiki-f3" data-k="${k}" style="left:${x}px;top:0;width:445px;height:500px"><span class="wiki-tag b">${tag}</span><h3>${h}</h3>${inner}</div>`;
  el.innerHTML =
    card(0, 1, 'cw', '1 · never written down', 'A fact no page holds', `
      <div><span class="wiki-tag">${esc(N.qid)}</span>“${esc(N.question)}”</div>
      <div style="margin-top:6px">The answer is on page ${N.gold_loc.page} of the purchasing manual. The ingest took ${N.facts_from_file} facts from that manual, <b>none from page ${N.gold_loc.page}</b>.</div>
      <span class="q r">Wiki: ${esc(N.wiki_answer.split('.')[0])}.</span>
      <span class="q a">RAG searched the raw manual and found the paragraph.</span>`) +
    card(478, 2, 'cw', '2 · written wrong once', 'Read wrong every time', `
      <div>The UN 38.3 page’s infobox, written at ingest, with no citation:</div>
      <span class="q r"><code>System enforcement | Ledgerline order blocking</code></span>
      <div>The answer we just watched repeated it:</div><span class="q r">“${esc(nav.hl.ans_wrong)}”</span>
      <div>What Ledgerline does:</div><span class="q g">${esc(X.truth[0])}</span><span class="src">${esc(short(X.truth_files[0]))}</span>`) +
    card(956, 3, 'cw', '3 · the reader stops early', 'Done before the key page', `
      <div>Emma’s question on the full ${fmt(d.eng.wiki_store.pages)}-page wiki: index.md, then <code>${E.chain.filter((c) => c.step === 'page').map((c) => esc(c.what)).join('</code>, <code>')}</code>, then done after ${E.nav_calls} calls.</div>
      <div style="margin-top:6px">Its reason for stopping names AMD-SUP-2026-02, a page it never opened.</div>
      <div style="margin-top:6px">Missing from the answer: ${E.missing.map((m) => `<code>${esc(m)}</code>`).join(' ')}</div>`) +
    `<div class="wiki-card cb" data-k="4" style="left:0;top:520px;width:1400px;height:86px;font-size:19px">Lint (code checks plus a model review) finds broken citations, orphan pages and stale rules. It cannot see these three. Only questions with known answers, the golden set, catch them.</div>`;
  return { step(k) { at(el, k); } };
};

/* ---------------------------------------------------------------- 13 · what it costs, measured */
FIGS.wiki_cost = (el) => {
  const d = W(); if (!d || !S()) return need(el, 'wiki_data.js');
  const C = d.fail.cost, R = d.eng.race, w = R.wiki, r = R.rag, L = S().alone;
  const row = (a, b, c, e, k = 0, cls = '') => `<tr data-k="${k}" class="${cls}"><td>${a}</td><td class="n">${b}</td><td class="n">${c}</td><td class="n">${e}</td></tr>`;
  el.innerHTML = `<div class="wiki-card cw" style="left:0;top:0;width:700px;height:606px"><span class="wiki-tag a">before any question</span><h3>Ingest: a model reads every source</h3>
      <table class="wiki-t" style="font-size:17px"><tr><th></th><th class="n">model calls</th><th class="n">time</th><th class="n">cost</th></tr>
      ${row('The amendment alone (1 page)', L.llm.calls, sec(L.seconds.read + L.seconds.merge + L.seconds.write), usd(L.llm.usd))}
      ${row('D alone (4 pages)', C.D.calls, '–', usd(C.D.usd))}
      ${row(`All ${fmt(C.build.files)} files`, fmt(C.build.calls), `${esc(C.build.minutes)} min`, '$' + C.build.usd.toFixed(2), 0, 'wiki-rbig')}
      ${row('RAG: chunk and index all files', '0', `${(C.rag.chunk_s + C.rag.bm25_build_s).toFixed(1)} s`, '$0', 0, 'wiki-rrag')}</table>
      <div class="s" style="font-size:16px;margin-top:10px">The full build ran on ${C.build.workers} workers, ${(C.build.tokens_in / 1e6).toFixed(1)} million tokens in. D’s first call was replayed from that build’s recording, so its time is not shown.</div></div>
    <div class="wiki-card ca" data-k="1" style="left:730px;top:0;width:670px;height:290px"><span class="wiki-tag a">at every question</span><h3>${d.eng.n} questions, per question</h3>
      <table class="wiki-t" style="font-size:17px"><tr><th></th><th class="n">wiki</th><th class="n">RAG</th></tr>
      <tr><td>model calls before the answer</td><td class="n">${(w.llm_calls_per_q - 1).toFixed(2)}</td><td class="n">0</td></tr>
      <tr><td>finding the text, median</td><td class="n">${sec(w.retrieval_p50_s)}</td><td class="n">${(r.retrieval_p50_s * 1000).toFixed(0)} ms</td></tr>
      <tr><td>cost per question</td><td class="n">${usd(w.cost_per_q_usd, 4)}</td><td class="n">${usd(r.cost_per_q_usd, 4)}</td></tr></table></div>
    <div class="wiki-card cg" data-k="2" style="left:730px;top:316px;width:670px;height:290px"><span class="wiki-tag g">and the answers</span><h3>Same quality, on average</h3>
      <table class="wiki-t" style="font-size:17px"><tr><th></th><th class="n">wiki</th><th class="n">RAG</th></tr>
      <tr><td>answer correct (judge)</td><td class="n">${(100 * w.answer_correct).toFixed(1)}%</td><td class="n">${(100 * r.answer_correct).toFixed(1)}%</td></tr>
      <tr><td>right source in the top 5</td><td class="n">${w['recall@5'].toFixed(2)}</td><td class="n">${r['recall@5'].toFixed(2)}</td></tr>
      <tr><td>citation correct</td><td class="n">${(100 * w.citation_correct).toFixed(1)}%</td><td class="n">${(100 * r.citation_correct).toFixed(1)}%</td></tr></table></div>`;
  return { step(k) { at(el, k); } };
};
})();
