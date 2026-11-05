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

/* the e-mail slide: quoted-printable decoded by hand on the real bytes (files.email.qp, computed with Python's quopri).
   Stage n appears on click n (1..5); all stages fade on click data-until (the decoded text takes their place). */
FIGS.parse_qp = (el) => {
  const d = D(); const q = d && d.files.email && d.files.email.qp;
  if (!q) return miss(el, 'quoted-printable data');
  el.classList.add('parse-qp');
  const until = +(el.dataset.until || 6);
  const mk = (t) => esc(t).replace(esc(q.esc), `<mark class="parse-mk b on">${esc(q.esc)}</mark>`);
  const st = [
    [`1 · One line of the body, as stored`, `<div class="mono">${mk(q.tail)}</div>`],
    [`2 · “=” then two hexadecimal digits is one byte`, `<div class="row">${q.bytes.map((b) => `<span class="tile">${esc(b.code)}</span><span class="arr">→</span><span class="tile byte">byte ${esc(b.hex)}<small>= ${b.dec}</small></span>`).join('<span class="gap2"></span>')}
      <span class="sm">Hex digits: 0–9, then A–F. Two make 00 to FF: one byte, 0 to 255.</span></div>`],
    [`3 · ${esc(q.utf8)} are the two bytes UTF-8 uses for “${esc(q.char)}”`, `<div class="sm">“${esc(q.char)}” is character ${q.cp_dec}. Above 127, UTF-8 needs two bytes or more: ${esc(q.utf8)}.</div>
      <div class="row"><span class="mono">${mk(q.esc + '104.00')}</span><span class="arr">→</span><span class="mono ok">${esc(q.char)}104.00</span></div>`],
    [`4 · “=” at the end of a line is a soft break`, `<div class="row"><span class="mono">per ${esc(q.join_a)}<span class="nl">⏎</span>${esc(q.join_b)}</span><span class="arr">→</span><span class="mono ok">per ${esc(q.joined)}</span></div>
      <div class="sm">Not a real line end: delete the “=” and the break. This file has ${q.soft_breaks}.</div>`],
    [`5 · Why a mail gateway writes text this way`, `<div class="sm">E-mail was built for plain ASCII (bytes 0 to 127) in short lines. So the gateway (${esc(q.mailer)}) writes every other byte as =XX and cuts lines at ${q.max_line} characters with a soft break. The header says so (blue, left).</div>`],
  ];
  el.innerHTML = st.map(([h, b], i) => `<div class="parse-qs tr" data-k="${i + 1}"><div class="h">${h}</div>${b}</div>`).join('');
  return { step(k) { el.querySelectorAll('.parse-qs').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k || k >= until)); } };
};

/* the check slide: three real snippets. What each is and where it is from shows at once; the verb and the reason on clicks 1, 2, 3 */
FIGS.parse_snips = (el) => {
  const d = D(); const C = d && d.files.check_three; const S = C && C.snips;
  if (!S) return miss(el, 'snippets');
  el.classList.add('parse-snips');
  el.innerHTML = S.map((s, i) => `<div class="parse-snip"><div class="what"><b>${esc(s.what)}</b><span>${esc(s.from)}</span></div><pre>${esc(s.text)}</pre>
    <div class="do tr" data-k="${i + 1}"><span class="verb v-${esc(s.verb.toLowerCase())}">${esc(s.verb)}</span>${esc(s.do)}</div></div>`).join('');
  return { step(k) { el.querySelectorAll('.do').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k)); } };
};

/* the three verbs of the check slide, defined before any answer */
FIGS.parse_legend = (el) => {
  const d = D(); const L = d && d.files.check_three && d.files.check_three.legend;
  if (!L) return miss(el, 'legend');
  el.classList.add('parse-legend');
  el.innerHTML = L.map((x) => `<div><span class="verb v-${esc(x.verb.toLowerCase())}">${esc(x.verb)}</span>${esc(x.def)}</div>`).join('');
  return { step() {} };
};

/* simple file-type icons, drawn here: <span class="parse-ico" data-ico="pdf"></span> */
const ICO = { pdf: ['PDF', '#c4511f'], scan: ['SCAN', '#7a5b2e'], poor: ['SCAN', '#8a8a8a'], xlsx: ['XLSX', '#138a60'], eml: ['EML', '#0b57d0'], docx: ['DOCX', '#2f5fb3'], html: ['HTML', '#6b4fbb'] };
FIGS.parse_icons = () => document.querySelectorAll('.parse-ico[data-ico]').forEach((e) => {
  if (e.firstChild) return;
  const [lab, c] = ICO[e.dataset.ico] || ['FILE', '#666'];
  const body = { scan: '<rect x="11" y="18" width="24" height="16" rx="2" fill="none" stroke="#7a5b2e" stroke-width="1.6"/><path d="M13 31l6-7 5 5 3-3 6 5" fill="none" stroke="#7a5b2e" stroke-width="1.6"/>',
    poor: '<path d="M11 20q4-3 8 0t8 0 8 0M11 26q4-3 8 0t8 0 8 0M11 32q4-3 8 0t8 0" fill="none" stroke="#8a8a8a" stroke-width="1.6"/>',
    xlsx: '<path d="M11 18h24v16H11zM11 23.3h24M11 28.6h24M19 18v16M27 18v16" fill="none" stroke="#138a60" stroke-width="1.4"/>',
    eml: '<rect x="11" y="19" width="24" height="15" rx="2" fill="none" stroke="#0b57d0" stroke-width="1.6"/><path d="M11.5 20l11.5 8 11.5-8" fill="none" stroke="#0b57d0" stroke-width="1.6"/>',
    html: '<circle cx="23" cy="26" r="8" fill="none" stroke="#6b4fbb" stroke-width="1.6"/><path d="M15 26h16M23 18q-5 8 0 16M23 18q5 8 0 16" fill="none" stroke="#6b4fbb" stroke-width="1.4"/>' }[e.dataset.ico]
    || `<path d="M12 20h22M12 25h22M12 30h15" stroke="${c}" stroke-width="1.8"/>`;
  e.innerHTML = `<svg viewBox="0 0 46 58" width="46" height="58" aria-hidden="true"><path d="M4 2h27l11 11v41a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" fill="#fff" stroke="#c9ced6" stroke-width="1.5"/><path d="M31 2v9a2 2 0 0 0 2 2h9" fill="none" stroke="#c9ced6" stroke-width="1.5"/>${body}<rect x="1" y="40" width="42" height="14" rx="3" fill="${c}"/><text x="22" y="51" text-anchor="middle" font-family="Google Sans Flex, Arial, sans-serif" font-size="12.5" font-weight="700" fill="#fff" style="font-size:12.5px">${lab}</text></svg>`;
});

/* numbers that live in the data, written into spans: <span data-pv="ocr.tesseract.secs"></span> */
FIGS.parse_fill = () => {
  const d = D(); if (!d) return;
  document.querySelectorAll('[data-pv]').forEach((s) => {
    let v = d; for (const k of s.dataset.pv.split('.')) v = v == null ? v : v[k];
    if (v != null) s.textContent = typeof v === 'number' ? v.toLocaleString('en-GB') : v;
  });
};
const boot = () => { FIGS.parse_fill(); FIGS.parse_icons(); };
if (document.readyState !== 'loading') boot(); else document.addEventListener('DOMContentLoaded', boot);
})();
