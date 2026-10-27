/* Plate engine for "From Forms to Agents" (AI Agents for Enterprises, Vizuara).
   A 1600x900 plate deck: .slide sections, .step reveals, live figures registered in window.FIGS.
   Each deck page loads plates.css, defines its figures in window.FIGS (using window.Plates helpers), then loads this file
   at the end of <body>. A figure: FIGS.name = (el, ctx) => ({ step(k, instant) {...} }), mounted on [data-fig="name"].
   ?print=1 shows every slide stacked with all steps revealed (for PDF export and review). */
(() => {
const NS = 'http://www.w3.org/2000/svg';
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const svgEl = (tag, attrs = {}, parent) => { const n = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v); if (parent) parent.appendChild(n); return n; };
const txt = (parent, x, y, s, style, anchor = 'start') => { const t = svgEl('text', { x, y, 'text-anchor': anchor, style }, parent); t.textContent = s; return t; };
const fmt = (n) => n.toLocaleString('en-IN');

/* ---------- legacy window renderer ---------- */
const TREE = `<div>▸ Masters</div><div>&nbsp;&nbsp;Item</div><div>&nbsp;&nbsp;Supplier</div><div>▾ Purchase</div><div class="TREQ">&nbsp;&nbsp;Request entry</div><div class="gr">&nbsp;&nbsp;Request approval</div><div class="TPO">&nbsp;&nbsp;Order entry</div><div>&nbsp;&nbsp;Order history</div><div class="gr">&nbsp;&nbsp;Order release</div><div>▸ Inventory</div><div>▸ Reports</div>`;
function winHTML(sc, opts = {}) {
  const fields = (sc.fields || []).map(([l, v, k = '', req]) => `<label class="${req ? 'req' : ''}">${l}</label><span class="in ${k}">${v}${k.includes('code') && !k.includes('ro') ? '<span class="f2">F2</span>' : ''}</span>`).join('');
  const list = sc.list ? `<div class="lst"><div class="hd"><span>Item code</span><span>Description</span><span>UOM</span></div>${sc.list.map((r, i) => `<div class="${i === 0 ? 'sel' : ''}"><span>${r[0]}</span><span style="font-family:Tahoma,sans-serif">${r[1]}</span><span>${r[2]}</span></div>`).join('')}</div>` : '';
  return `<div class="win" style="height:${opts.h || 470}px">
    <div class="tb">Bahi ERP 7.2 — ${sc.title}<span class="sp"></span><span style="font-weight:400;font-size:13px">${sc.code}</span><span class="bx">_</span><span class="bx">□</span><span class="bx">×</span></div>
    <div class="mn">File Edit View Masters Purchase Inventory Reports Help</div>
    <div class="bd"><div class="tree">${TREE.replace(sc.treeOn ? `class="${sc.treeOn}"` : 'XX', 'class="on"')}</div><div class="fm">${fields}${list}</div></div>
    <div class="bt">${(sc.buttons || []).map((b) => `<span class="${b === sc.hot ? 'hot' : ''}">${b}</span>`).join('')}</div>
    <div class="sb"><span class="${sc.err ? 'er' : ''}">${sc.status || 'Ready'}</span><span>${sc.user || 'KJOSHI'}</span><span>RSW-PUN-01</span></div></div>`;
}


window.Plates = { NS, svgEl, txt, fmt, winHTML, TREE, reduced };
window.FIGS = window.FIGS || {};
const FIGS = window.FIGS;
const deckEl = document.getElementById('deck');
if (!document.getElementById('pbar')) document.body.insertAdjacentHTML('afterbegin', '<div class="pbar" id="pbar"></div>');
if (!document.getElementById('count')) document.body.insertAdjacentHTML('beforeend', `<div class="chrome"><span class="title">${document.title}</span><span class="sp"></span><span id="count"></span><button id="prev" aria-label="Previous">←</button><button id="next" aria-label="Next">→</button></div>`);
/* ---------- engine ---------- */
const deck = deckEl;
const slides = [...deck.querySelectorAll('.slide')];
const roman = (n) => { const m = [[10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']]; let s = ''; if (n >= 40) { s += 'XL'; n -= 40; } while (n >= 10) { s += 'X'; n -= 10; } for (const [v, r] of m) while (n >= v) { s += r; n -= v; } return s; };
let plateNo = 0;
slides.forEach((sl, i) => {
  sl.insertAdjacentHTML('afterbegin', '<div class="frame"></div>');
  if (sl.dataset.plate) { plateNo++; sl.insertAdjacentHTML('beforeend', `<div class="plate-head">Plate ${roman(plateNo)} · ${sl.dataset.plate}</div>`); }
  sl.insertAdjacentHTML('beforeend', `<div class="folio">— ${i + 1} —</div>`);
});
const mounted = new Map();
let cur = 0;
const steps = (i) => [...slides[i].querySelectorAll('.step')];
const fit = () => { const w = innerWidth, h = innerHeight; const s = Math.min(w / 1600, (h - 40) / 900); deck.style.transform = `translate(-50%, calc(-50% - 20px)) scale(${s})`; };
const told = (i, instant) => {
  const k = steps(i).filter((e) => e.classList.contains('shown')).length;
  slides[i].querySelectorAll('[data-fig]').forEach((f) => {
    if (!mounted.has(f)) { try { mounted.set(f, FIGS[f.dataset.fig](f)); } catch (err) { console.error(err); mounted.set(f, { step() {} }); } }
    try { mounted.get(f).step(k, instant); } catch (err) { console.error(err); }
  });
};
const show = (i, all = false) => {
  i = Math.max(0, Math.min(slides.length - 1, i));
  slides.forEach((s, k) => s.classList.toggle('active', k === i));
  steps(i).forEach((e) => e.classList.toggle('shown', all));
  cur = i;
  document.getElementById('pbar').style.width = (100 * (i + 1) / slides.length) + '%';
  document.getElementById('count').textContent = `${i + 1} / ${slides.length}`;
  try { history.replaceState(null, '', '#' + (i + 1)); } catch (e) {}
  told(i, true);
};
const next = () => { const h = steps(cur).find((e) => !e.classList.contains('shown')); if (h) { h.classList.add('shown'); told(cur, false); } else if (cur < slides.length - 1) show(cur + 1); };
const prev = () => { const s = steps(cur).filter((e) => e.classList.contains('shown')); if (s.length) { s[s.length - 1].classList.remove('shown'); told(cur, false); } else if (cur > 0) show(cur - 1, true); };
const busy = (t) => t && t.closest && t.closest('input,button,.ctl');
addEventListener('keydown', (e) => {
  if (e.target.closest && e.target.closest('input')) return;
  if (['ArrowRight', ' ', 'PageDown', 'Enter'].includes(e.key)) { e.preventDefault(); next(); }
  else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); prev(); }
  else if (e.key === 'Home') show(0);
  else if (e.key === 'End') show(slides.length - 1, true);
});
document.getElementById('next').addEventListener('click', next);
document.getElementById('prev').addEventListener('click', prev);
deck.addEventListener('click', (e) => { if (busy(e.target)) return; const r = deck.getBoundingClientRect(); (e.clientX - r.left > r.width * 0.25 ? next : prev)(); });
let x0 = null;
addEventListener('touchstart', (e) => { x0 = busy(e.target) ? null : e.touches[0].clientX; }, { passive: true });
addEventListener('touchend', (e) => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) (dx < 0 ? next : prev)(); x0 = null; });
if (/[?&]print=1/.test(location.search)) {
  document.body.classList.add('print');
  deck.style.cssText = 'position:static;transform:none;width:1600px;height:auto';
  slides.forEach((s, i) => { s.style.cssText = 'display:block;position:relative;width:1600px;height:900px;border-bottom:1px dashed #999'; steps(i).forEach((e) => e.classList.add('shown')); cur = i; told(i, true); });
  window.deckApi = { count: slides.length };
  return;
}
addEventListener('resize', fit);
fit();
const start = parseInt((location.hash || '').slice(1), 10);
show(Number.isFinite(start) ? start - 1 : 0, Number.isFinite(start));
window.deckApi = { next, prev, show, get cur() { return cur; }, count: slides.length };
})();
