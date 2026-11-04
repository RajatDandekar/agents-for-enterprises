/* L3 v5 · parsing section figures. Data: window.L3V5.parse (parse_data.js, written by experiments/v5_parse_build.py
   from experiments/logs/v5_parse*.json). Nothing here is typed in by hand: every text is a parser's real output.
   FIGS.parse_img   one real image (rendered page, sheet, scan) with highlight boxes that appear on clicks.
                    data-key="apr" data-im="crop" (an image of that file's record)
   FIGS.parse_txt   one real text (naive extraction, structured units, OCR output, raw e-mail) with marks on clicks.
                    data-key="apr" data-tx="naive"
   A box or mark with k = n appears once n .step elements of the slide are shown (k = 0: from the start). */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const D = () => (window.L3V5 && window.L3V5.parse) || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const miss = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(parse data)</span><div>${esc(what)}</div></div>`; return { step() {} }; };
const rec = (el) => { const d = D(); return d && d.files[el.dataset.key]; };

FIGS.parse_img = (el) => {
  const r = rec(el); const im = r && r.images && r.images[el.dataset.im || 'crop'];
  if (!im) return miss(el, `image ${el.dataset.key}.${el.dataset.im}`);
  el.classList.add('parse-img');
  const W = el.clientWidth || parseFloat(el.style.width), H = el.clientHeight || parseFloat(el.style.height);
  const fitw = el.dataset.fit === 'width';
  const s = fitw ? W / im.w : Math.min(W / im.w, H / im.h);
  const w = im.w * s, h = im.h * s, x = fitw ? 0 : (W - w) / 2, y = fitw ? 0 : (H - h) / 2;
  const boxes = (im.boxes || []).map((b) => `<div class="parse-box ${b.cls || 'a'}" data-k="${b.k || 0}" style="left:${x + b.x * w - 4}px;top:${y + b.y * h - 3}px;width:${b.w * w + 8}px;height:${b.h * h + 6}px">${b.label ? `<i class="${b.below ? 'below' : ''}">${esc(b.label)}</i>` : ''}</div>`).join('');
  el.innerHTML = `<img class="parse-pic" src="${esc((/\/v5\/[^/]*$/.test(location.pathname) || /^(https?:|data:|\/|\.\.\/|v5\/)/.test(im.src) ? '' : 'v5/') + im.src)}" alt="${esc(im.alt || r.file)}" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px">${boxes}${el.dataset.cap ? `<div class="parse-cap">${esc(el.dataset.cap)}</div>` : ''}`;
  const set = (k) => el.querySelectorAll('.parse-box').forEach((b) => {
    const kk = +b.dataset.k, until = b.dataset.until;
    b.classList.toggle('on', kk <= k);
  });
  return { step(k) { set(k); } };
};

/* text with marks: marks are [{s: exact substring, k, cls, n: which occurrence (default every)}] */
function marked(text, marks) {
  const spans = [];
  (marks || []).forEach((m, mi) => {
    let from = 0, i, seen = 0;
    while ((i = text.indexOf(m.s, from)) >= 0) {
      if (m.n == null || m.n === seen) spans.push({ a: i, b: i + m.s.length, m, mi });
      seen++; from = i + Math.max(1, m.s.length);
    }
  });
  spans.sort((p, q) => p.a - q.a || q.b - p.b);
  let out = '', pos = 0;
  for (const sp of spans) {
    if (sp.a < pos) continue; // overlapping: the first wins
    out += esc(text.slice(pos, sp.a)) + `<mark class="parse-mk ${sp.m.cls || 'a'}" data-k="${sp.m.k || 0}">${esc(text.slice(sp.a, sp.b))}</mark>`;
    pos = sp.b;
  }
  return out + esc(text.slice(pos));
}

FIGS.parse_txt = (el) => {
  const r = rec(el); const t = r && r.texts && r.texts[el.dataset.tx];
  if (!t) return miss(el, `text ${el.dataset.key}.${el.dataset.tx}`);
  el.classList.add('parse-panel');
  const body = t.empty ? `<span class="nil">${esc(t.empty)}</span>` : marked(t.text, t.marks).replace(/⋯[^\n]*/g, (g) => `<span class="gap">${g}</span>`);
  el.innerHTML = `<div class="parse-ph ${t.cls || 'n'}">${esc(t.title)}${t.sub ? `<span>${esc(t.sub)}</span>` : ''}</div><pre class="parse-pre ${t.cls || ''} ${t.raw ? 'raw' : ''}" style="${t.fs ? `font-size:${t.fs}px;` : ''}${t.cols ? `column-count:${t.cols};column-gap:28px;` : ''}">${body}</pre>`;
  return { step(k) { el.querySelectorAll('mark.parse-mk').forEach((m) => m.classList.toggle('on', +m.dataset.k <= k)); } };
};

/* metadata records, as corpus.file_meta returned them. data-files="0,1,2" (indexes into files.meta.records),
   data-k0="1": the first record appears on click 1, the next on click 2, and so on */
FIGS.parse_meta = (el) => {
  const d = D(); const recs = d && d.files.meta && d.files.meta.records;
  if (!recs) return miss(el, 'metadata records');
  const pick = (el.dataset.files || '0,1,2').split(',').map(Number), k0 = +(el.dataset.k0 || 1);
  const v = (x) => (x === true ? '<span class="hot">true</span>' : x === false ? 'false' : x === '' ? '<span class="nil">""</span>' : esc(x));
  el.innerHTML = pick.map((i, j) => {
    const r = recs[i]; const f = r.fields;
    const hot = (k) => (k === 'superseded' && f.superseded) || (k === 'future' && f.future) || (k === 'confidential' && f.confidential) || (k === 'status' && /SUPERSEDED|ISSUED/.test(f.status));
    return `<div class="parse-rec tr" data-k="${k0 + j}">
      <div class="f">${esc(r.file)}</div>
      ${r.answer ? `<div class="parse-ans">says <b>${esc(r.answer)}</b></div>` : ''}
      <div class="kv">${Object.keys(f).map((k) => `<span>${k}</span><span class="${hot(k) ? 'hot' : ''}">${v(f[k])}</span>`).join('')}</div>
      <div class="parse-sl">${r.status_line ? `chunk header adds: <b>${esc(r.status_line)}</b>` : '<span class="nil">chunk header adds nothing</span>'}${r.may_read && !r.may_read['PUR-EXEC'] ? ` · may_read(Emma) = <b class="hot">false</b>` : ''}</div></div>`;
  }).join('');
  return { step(k) { el.querySelectorAll('.parse-rec').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k)); } };
};

/* the check slide: three real snippets, what the parser does with each appears on clicks 1, 2, 3 */
FIGS.parse_snips = (el) => {
  const d = D(); const S = d && d.files.check_three && d.files.check_three.snips;
  if (!S) return miss(el, 'snippets');
  el.classList.add('parse-snips');
  el.innerHTML = S.map((s, i) => `<div class="parse-snip"><div class="from">${esc(s.from)}</div><pre>${esc(s.text)}</pre><div class="do tr" data-k="${i + 1}">${esc(s.do)}</div></div>`).join('');
  return { step(k) { el.querySelectorAll('.do').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k)); } };
};

/* numbers that live in the data, written into spans: <span data-pv="ocr.tesseract.secs"></span> */
FIGS.parse_fill = () => {
  const d = D(); if (!d) return;
  document.querySelectorAll('[data-pv]').forEach((s) => {
    let v = d; for (const k of s.dataset.pv.split('.')) v = v == null ? v : v[k];
    if (v != null) s.textContent = typeof v === 'number' ? v.toLocaleString('en-GB') : v;
  });
};
if (document.readyState !== 'loading') FIGS.parse_fill(); else document.addEventListener('DOMContentLoaded', FIGS.parse_fill);
})();
