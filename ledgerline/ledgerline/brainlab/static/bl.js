/* The Brain Lab: small shared helpers (player id, API calls, escaping, toast, reveal, bars, the loss curve). */
(() => {
'use strict';
const KEY = 'bl_pid';
const store = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } },
  del(k) { try { localStorage.removeItem(k); } catch (e) { /* private mode */ } },
};
const cookie = (k) => (document.cookie.split('; ').find((c) => c.startsWith(k + '=')) || '').split('=')[1] || '';
const BL = {
  pid() { return store.get(KEY) || cookie(KEY) || ''; },
  setPid(pid) { store.set(KEY, pid); document.cookie = `${KEY}=${pid}; path=/; max-age=${60 * 60 * 24 * 30}; samesite=lax`; },
  forget() { store.del(KEY); document.cookie = `${KEY}=; path=/; max-age=0`; },
  async api(path, body, method) {
    const h = { 'Content-Type': 'application/json' };
    const pid = BL.pid(); if (pid) h['X-Player'] = pid;
    const r = await fetch(path, { method: method || (body === undefined ? 'GET' : 'POST'), headers: h,
      body: body === undefined ? undefined : JSON.stringify(body) });
    let d = null; try { d = await r.json(); } catch (e) { d = {}; }
    if (!r.ok) { const err = new Error((d && d.detail) || ('HTTP ' + r.status)); err.status = r.status; throw err; }
    return d;
  },
  esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); },
  num(n) { return new Intl.NumberFormat('en-GB').format(n); },
  toast(msg, ms) {
    let t = document.querySelector('.toast'); if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.append(t); }
    t.textContent = msg; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), ms || 3200);
  },
  reveal(root) {
    const els = (root || document).querySelectorAll('.rv:not(.in)');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }), { threshold: 0.08 });
    els.forEach((e) => io.observe(e));
  },
  tok(t) {  /* show a token readably: spaces as a dot, newlines as a return sign */
    if (t === '') return '∅';
    return BL.esc(t.replace(/\n/g, '⏎').replace(/^ /, '·'));
  },
  /* the model's top choices at the moment it wrote the first digit (or its first word) */
  moment(m, key) {
    if (!m || !m.top) return '';
    const max = Math.max(...m.top.map((x) => x.p), 0.0001);
    const kd = key ? String(key).replace(/[^0-9A-Za-z]/g, '').charAt(0) : '';
    const head = m.kind === 'digit'
      ? `When it wrote the first digit${m.after ? `, after “…${BL.esc(m.after.slice(-34))}”` : ''}, it was choosing between:`
      : 'Its first word, and what else it nearly said:';
    const anyHit = kd && m.kind === 'digit' && m.top.slice(0, 5).some((x) => x.t.trim().charAt(0) === kd);
    return `<div class="moment"><div class="mh">${head}${anyHit ? ' <span class="g">Green = the right first digit.</span>' : ''}</div>` + m.top.slice(0, 5).map((x, i) => {
      const hit = kd && x.t.trim().charAt(0) === kd && m.kind === 'digit';
      return `<div class="bar${i === 0 ? ' top' : ''}${hit ? ' hit' : ''}"><span class="bt">${BL.tok(x.t)}</span><span class="bw"><i style="width:${Math.max(2, x.p / max * 100)}%"></i></span><span class="bp">${(x.p * 100).toFixed(x.p < 0.1 ? 1 : 0)}%</span></div>`;
    }).join('') + '</div>';
  },
  /* the loss curve as an SVG */
  curve(points, w, h) {
    w = w || 560; h = h || 200;
    const pad = { l: 40, r: 12, t: 12, b: 26 };
    if (!points || !points.length) return `<svg viewBox="0 0 ${w} ${h}" class="curve"><text x="${w / 2}" y="${h / 2}" text-anchor="middle" class="ax">waiting for the first step…</text></svg>`;
    const maxS = Math.max(20, points[points.length - 1][0]);
    const maxL = Math.max(...points.map((p) => p[1]), 0.5);
    const X = (s) => pad.l + (s / maxS) * (w - pad.l - pad.r);
    const Y = (l) => pad.t + (1 - l / maxL) * (h - pad.t - pad.b);
    const d = points.map((p, i) => `${i ? 'L' : 'M'}${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)}`).join('');
    const area = d + `L${X(points[points.length - 1][0]).toFixed(1)},${Y(0)}L${X(points[0][0]).toFixed(1)},${Y(0)}Z`;
    const ticks = [0, maxL / 2, maxL].map((v) => `<line x1="${pad.l}" x2="${w - pad.r}" y1="${Y(v)}" y2="${Y(v)}" class="gl"/><text x="${pad.l - 6}" y="${Y(v) + 4}" text-anchor="end" class="ax">${v.toFixed(1)}</text>`).join('');
    const last = points[points.length - 1];
    return `<svg viewBox="0 0 ${w} ${h}" class="curve" role="img" aria-label="Training loss curve">${ticks}
      <path d="${area}" class="ar"/><path d="${d}" class="ln"/>
      <circle cx="${X(last[0])}" cy="${Y(last[1])}" r="4.5" class="pt"/>
      <text x="${pad.l}" y="${h - 6}" class="ax">step 0</text><text x="${w - pad.r}" y="${h - 6}" text-anchor="end" class="ax">step ${maxS}</text></svg>`;
  },
};
window.BL = BL;
})();
