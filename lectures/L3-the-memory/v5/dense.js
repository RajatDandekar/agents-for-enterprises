/* Lecture 3 v5 · section `dense`: dense retrieval on one document (POL-PUR-001 v4.1) and one question (Emma's).
   Figures are registered as FIGS.dense_<fig>; every number, chunk and vector comes from window.L3V5.dense
   (v5/dense_data.js, written by experiments/v5_dense_build.py from logs/v5_dense*.json). Nothing typed in by hand.
   The 3D space is a small hand-written canvas renderer: drag to rotate, hover or click a point to read its chunk.
   It never listens to keys, and it stops its own clicks so the deck does not advance while you drag. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const DD = () => (window.L3V5 && window.L3V5.dense) || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const stop = (e) => e.stopPropagation();
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(dense data)</span><div>${what}</div></div>`; return { step() {} }; };
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('dense-off', +x.dataset.k > k));
const PRINT = /[?&]print=1/.test(location.search);
const cut = (s, n) => (s.length > n ? s.slice(0, n - 1) + '…' : s);
const one = (s) => String(s || '').replace(/\s+/g, ' ').trim();
const isActive = (el) => PRINT || !!(el.closest('.slide') && el.closest('.slide').classList.contains('active'));
const BASE = /\/v5\/[^/]*$/.test(location.pathname) ? '' : 'v5/';   // images live in v5/dense_img
const secColour = (name) => { const d = DD(); return (d && d.secColour[name]) || '#8a8f99'; };
const ord = (n) => fmt(n) + (n % 100 >= 11 && n % 100 <= 13 ? 'th' : ['th', 'st', 'nd', 'rd'][n % 10] || 'th');

/* ---- fill [data-dn="path"] spans from the data (formats: r2 r3 r4 n pct0 pct1 ord) ---- */
const getp = (path) => {   // keys may contain dots ("6.2"): take the longest key that exists at each level
  let v = DD(); const p = path.split('.');
  for (let i = 0; i < p.length && v != null; ) {
    let j = p.length; while (j > i + 1 && !(p.slice(i, j).join('.') in Object(v))) j--;
    v = v[p.slice(i, j).join('.')]; i = j;
  }
  return v;
};
function fill() {
  if (!DD()) return;
  document.querySelectorAll('[data-dn]').forEach((e) => {
    const v = getp(e.dataset.dn); if (v == null) { e.textContent = '–'; return; }
    const f = e.dataset.f;
    e.textContent = f === 'r2' ? (+v).toFixed(2) : f === 'r3' ? (+v).toFixed(3) : f === 'r4' ? (+v).toFixed(4) : f === 'n' ? fmt(v)
      : f === 'pct0' ? Math.round(100 * v) + '%' : f === 'pct1' ? (100 * v).toFixed(1) + '%' : f === 'ord' ? ord(v) : String(v);
  });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fill); else fill();

/* ============================================================ Space3D: a canvas point cloud ============== */
function Space3D(host, opts = {}) {
  const cv = document.createElement('canvas');
  cv.className = 'dense-cv';
  host.appendChild(cv);
  const tip = document.createElement('div');
  tip.className = 'dense-tip';
  host.appendChild(tip);
  const ctx = cv.getContext('2d');
  let W = 0, H = 0, dpr = 1;
  const S = { yaw: opts.yaw ?? -0.7, pitch: opts.pitch ?? 0.35, zoom: 1, auto: opts.auto !== false, ext: 1,
    pts: [], q: null, links: [], hover: null, pinned: null, drag: null, axes: opts.axes || ['PC1', 'PC2', 'PC3'] };
  const size = () => {
    const r = host.getBoundingClientRect();
    W = host.offsetWidth; H = host.offsetHeight;
    const sc = W ? r.width / W : 1;   // the deck is scaled to the window: draw at the real pixel size
    dpr = Math.max(1, Math.min(3, (window.devicePixelRatio || 1) * (sc || 1)));
    cv.width = Math.max(1, Math.round(W * dpr)); cv.height = Math.max(1, Math.round(H * dpr));
    cv.style.width = W + 'px'; cv.style.height = H + 'px';
  };
  size();
  const rot = (p) => {
    const cy = Math.cos(S.yaw), sy = Math.sin(S.yaw), cp = Math.cos(S.pitch), sp = Math.sin(S.pitch);
    const x = p[0] * cy - p[2] * sy, z0 = p[0] * sy + p[2] * cy;
    return [x, p[1] * cp - z0 * sp, p[1] * sp + z0 * cp];
  };
  const proj = (p) => {
    const [x, y, z] = rot(p);
    const e = S.ext, dist = 3.4 * e, per = dist / (dist - z);
    const s = Math.min(W - (opts.padX || 60), H - 70) * 0.36 / e * S.zoom;
    return { x: W / 2 + x * s * per, y: (H - (opts.padBottom || 30)) / 2 + 6 - y * s * per, z, per };
  };
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = (t) => (t >= 1 ? 1 : 1 - Math.pow(1 - t, 3));
  const tOf = (p, now) => ease(Math.max(0, Math.min(1, (now - (p.tStart || 0)) / (p.dur || 700))));
  const posOf = (p, now) => { const t = tOf(p, now); return [lerp(p.from[0], p.to[0], t), lerp(p.from[1], p.to[1], t), lerp(p.from[2], p.to[2], t)]; };
  const alphaOf = (p, now) => lerp(p.a0 ?? 1, p.a1 ?? 1, tOf(p, now));
  function setPoints(list, { ext, animate = true } = {}) {
    const now = performance.now();
    const old = new Map(S.pts.filter((p) => !p.ghost).map((p) => [p.id, p]));
    const next = list.map((p) => {
      const o = old.get(p.id);
      const cur = o ? posOf(o, now) : p.xyz;
      return { ...p, from: animate ? cur : p.xyz, to: p.xyz, tStart: now, dur: 850, a0: o ? alphaOf(o, now) : (animate ? 0 : 1), a1: 1 };
    });
    if (animate) for (const o of old.values()) if (!list.find((n) => n.id === o.id)) { const c = posOf(o, now); next.push({ ...o, from: c, to: c, tStart: now, dur: 450, a0: alphaOf(o, now), a1: 0, ghost: true }); }
    S.pts = next;
    if (S.pinned && !next.find((p) => p === S.pinned)) { S.pinned = null; showTip(null); }
    if (ext) S.ext = ext;
    kick();
  }
  function setQuery(q) {   // {xyz, label}: drops in from above the first time
    const now = performance.now();
    if (!q) { S.q = null; kick(); return; }
    const from = S.q ? posOf(S.q, now) : [q.xyz[0], q.xyz[1] + S.ext * 1.5, q.xyz[2]];
    S.q = { ...q, from, to: q.xyz, tStart: now, dur: 1100, a0: S.q ? 1 : 0, a1: 1 };
    kick();
  }
  function setLinks(ids) { const now = performance.now(); S.links = ids.map((id, r) => ({ id, r: r + 1, tStart: now + 150 + 110 * r })); kick(); }
  const hit = (mx, my, now) => {
    let best = null, bd = 18 * 18;
    for (const p of S.pts) {
      if (p.ghost) continue;
      const s = proj(posOf(p, now));
      const dd = (s.x - mx) ** 2 + (s.y - my) ** 2;
      if (dd < bd) { bd = dd; best = p; }
    }
    return best;
  };
  function showTip(p, sx, sy) {
    if (!p) { tip.classList.remove('on'); return; }
    tip.innerHTML = opts.tip ? opts.tip(p) : esc(p.id);
    tip.classList.add('on');
    if (sx == null) { const s = proj(posOf(p, performance.now())); sx = s.x; sy = s.y; }
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = sx + 18, y = sy - th / 2;
    if (x + tw > W - 8) x = sx - tw - 18;
    tip.style.left = Math.max(8, x) + 'px'; tip.style.top = Math.max(8, Math.min(H - th - 8, y)) + 'px';
  }
  const local = (e) => { const r = cv.getBoundingClientRect(); const k = W / r.width; return [(e.clientX - r.left) * k, (e.clientY - r.top) * k]; };
  cv.addEventListener('pointerdown', (e) => { stop(e); const [x, y] = local(e); S.drag = { x, y, yaw: S.yaw, pitch: S.pitch, moved: 0 }; S.auto = false; try { cv.setPointerCapture(e.pointerId); } catch (err) { /* synthetic events */ } kick(); });
  cv.addEventListener('pointermove', (e) => {
    const [x, y] = local(e);
    if (S.drag) {
      S.drag.moved += Math.abs(x - S.drag.x) + Math.abs(y - S.drag.y);
      S.yaw = S.drag.yaw + (x - S.drag.x) * 0.008;
      S.pitch = Math.max(-1.35, Math.min(1.35, S.drag.pitch + (y - S.drag.y) * 0.008));
      kick(); return;
    }
    const p = hit(x, y, performance.now());
    if (p !== S.hover) { S.hover = p; kick(); }
    if (!S.pinned) showTip(p, x, y);
  });
  cv.addEventListener('pointerup', (e) => {
    stop(e);
    const [x, y] = local(e);
    if (S.drag && S.drag.moved < 6) {   // a click: pin or unpin the nearest point
      const p = hit(x, y, performance.now());
      S.pinned = p && S.pinned !== p ? p : null;
      showTip(S.pinned, x, y);
    }
    S.drag = null; kick();
  });
  cv.addEventListener('pointerleave', () => { if (!S.pinned) { S.hover = null; showTip(null); kick(); } });
  cv.addEventListener('wheel', (e) => { e.preventDefault(); stop(e); S.zoom = Math.max(0.6, Math.min(2.4, S.zoom * (e.deltaY < 0 ? 1.08 : 1 / 1.08))); kick(); }, { passive: false });
  host.addEventListener('click', stop);
  host.addEventListener('touchstart', stop, { passive: true });
  host.addEventListener('touchend', stop, { passive: true });
  function draw(now) {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const e = S.ext;
    // a faint floor under the cloud, for depth
    const fl = [[-e, -e, -e], [e, -e, -e], [e, -e, e], [-e, -e, e]].map(proj);
    ctx.fillStyle = 'rgba(11,87,208,.035)'; ctx.strokeStyle = 'rgba(18,19,23,.08)'; ctx.lineWidth = 1;
    ctx.beginPath(); fl.forEach((p, i) => (i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y))); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.beginPath();
    for (let i = 1; i < 4; i++) { const t = -e + (2 * e * i) / 4; const a = proj([t, -e, -e]), b = proj([t, -e, e]), c = proj([-e, -e, t]), dd = proj([e, -e, t]); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.moveTo(c.x, c.y); ctx.lineTo(dd.x, dd.y); }
    ctx.strokeStyle = 'rgba(18,19,23,.05)'; ctx.stroke();
    ctx.font = '500 15px "Google Sans Flex", sans-serif';
    [[[-e, 0, 0], [e, 0, 0]], [[0, -e, 0], [0, e, 0]], [[0, 0, -e], [0, 0, e]]].forEach(([a, b], i) => {
      const A = proj(a), B = proj(b);
      ctx.strokeStyle = 'rgba(18,19,23,.22)'; ctx.setLineDash([4, 5]); ctx.beginPath(); ctx.moveTo(A.x, A.y); ctx.lineTo(B.x, B.y); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = 'rgba(18,19,23,.55)'; ctx.fillText(S.axes[i], B.x + 6, B.y - 6);
    });
    const P = S.pts.map((p) => ({ p, s: proj(posOf(p, now)), a: alphaOf(p, now) })).filter((o) => o.a > 0.01);
    const Q = S.q ? { s: proj(posOf(S.q, now)), a: alphaOf(S.q, now) } : null;
    const qDone = Q && now > S.q.tStart + S.q.dur * 0.8;
    if (Q && qDone) {
      for (const L of S.links) {
        const o = P.find((x) => x.p.id === L.id && !x.p.ghost); if (!o) continue;
        const t = Math.max(0, Math.min(1, (now - L.tStart) / 450)); if (t <= 0) continue;
        ctx.strokeStyle = o.p.gold ? 'rgba(11,87,208,.9)' : 'rgba(18,19,23,.38)';
        ctx.lineWidth = o.p.gold ? 2.8 : 1.6;
        ctx.beginPath(); ctx.moveTo(Q.s.x, Q.s.y); ctx.lineTo(lerp(Q.s.x, o.s.x, t), lerp(Q.s.y, o.s.y, t)); ctx.stroke();
      }
    }
    P.sort((a, b) => a.s.z - b.s.z);
    for (const { p, s, a } of P) {
      const r = (p.r || 9) * Math.max(0.7, Math.min(1.45, s.per)) * (S.hover === p || S.pinned === p ? 1.35 : 1);
      ctx.globalAlpha = a;
      ctx.fillStyle = p.c || '#4f86e8';
      ctx.beginPath(); ctx.arc(s.x, s.y, r, 0, Math.PI * 2); ctx.fill();
      ctx.lineWidth = 1.5; ctx.strokeStyle = 'rgba(255,255,255,.95)'; ctx.stroke();
      if (p.gold) { ctx.lineWidth = 3; ctx.strokeStyle = '#0b57d0'; ctx.beginPath(); ctx.arc(s.x, s.y, r + 4.5, 0, Math.PI * 2); ctx.stroke(); }
      else if (p.ring2) { ctx.lineWidth = 2; ctx.setLineDash([3, 3]); ctx.strokeStyle = '#0b57d0'; ctx.beginPath(); ctx.arc(s.x, s.y, r + 4, 0, Math.PI * 2); ctx.stroke(); ctx.setLineDash([]); }
      if (p.tag) { ctx.font = '500 14px "Google Sans Flex", sans-serif'; ctx.fillStyle = 'rgba(18,19,23,.62)'; ctx.fillText(p.tag, s.x + r + (p.gold ? 9 : 5), s.y + 5); }
      ctx.globalAlpha = 1;
    }
    if (Q && qDone && S.links.length) {
      ctx.font = '600 13px "Google Sans Flex", sans-serif'; ctx.textAlign = 'center';
      for (const L of S.links) {
        const o = P.find((x) => x.p.id === L.id && !x.p.ghost); if (!o || now < L.tStart + 380) continue;
        const x = o.s.x, y = o.s.y - (o.p.r || 9) * Math.max(0.7, Math.min(1.45, o.s.per)) - 16;
        ctx.fillStyle = o.p.gold ? '#0b57d0' : '#121317'; ctx.beginPath(); ctx.arc(x, y, 10, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#fff'; ctx.fillText(String(L.r), x, y + 4.5);
      }
      ctx.textAlign = 'left';
    }
    if (Q) {
      const { x, y } = Q.s, r = 13;
      ctx.globalAlpha = Q.a;
      ctx.fillStyle = 'rgba(11,87,208,.16)'; ctx.beginPath(); ctx.arc(x, y, r + 11, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#121317'; ctx.beginPath();
      for (let i = 0; i < 10; i++) { const ang = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; ctx.lineTo(x + rr * Math.cos(ang), y + rr * Math.sin(ang)); }
      ctx.closePath(); ctx.fill();
      ctx.font = '600 17px "Google Sans Flex", sans-serif'; ctx.fillText(S.q.label || 'Q', x + r + 8, y + 6);
      ctx.globalAlpha = 1;
    }
  }
  let raf = 0, last = 0;
  function frame(now) {
    raf = 0;
    if (!isActive(host)) return;
    const dt = Math.min(50, now - last); last = now;
    if (S.auto && !S.drag && !S.hover && !S.pinned && !PRINT) S.yaw += dt * 0.00011;
    draw(now);
    const anim = S.pts.some((p) => now - p.tStart < p.dur) || (S.q && now - S.q.tStart < S.q.dur + 200) || S.links.some((L) => now - L.tStart < 900);
    if ((S.auto && !PRINT) || anim || S.drag) raf = requestAnimationFrame(frame);
  }
  function kick() { if (!raf) { last = performance.now(); raf = requestAnimationFrame(frame); } }
  if (window.ResizeObserver) new ResizeObserver(() => { size(); kick(); }).observe(host);
  if (PRINT) setTimeout(() => { size(); draw(performance.now() + 9000); }, 80);
  return { setPoints, setQuery, setLinks, kick, S };
}

/* ============================================================ shared pieces ============== */
const extentOf = (lists) => { let m = 0; for (const L of lists) for (const p of L) for (const v of p) m = Math.max(m, Math.abs(v)); return m * 1.02 || 1; };
const axesOf = (ev) => ev ? ev.slice(0, 3).map((v, i) => `PC${i + 1} · ${Math.round(100 * v)}%`) : ['PC1', 'PC2', 'PC3'];
const flags = (c) => `${c.has62 ? ' · <span class="dense-g">holds §6.2</span>' : ''}${c.has64 ? ' · <span class="dense-g">holds §6.4</span>' : ''}${c.restates ? ' · <span class="dense-g">restates §6.2 and §6.4</span>' : ''}`;
const chunkTip = (c) => `<div class="dense-tip-h"><span class="dense-dot" style="background:${secColour(c.sec)}"></span>${esc(c.short)}</div>
  <div class="dense-tip-m">${esc(c.cite)}<br>${c.tokens} tokens · cosine to Q <b>${c.cos.toFixed(3)}</b> · rank ${c.rank}${flags(c)}</div>
  <div class="dense-tip-b">${esc(cut(one(c.body), 240))}</div>`;
const ptsOf = (chunks, gold = true, tags = false) => chunks.map((c) => ({ id: c.cid, xyz: c.xyz, c: secColour(c.sec), r: 10, gold: gold && (c.has62 || c.has64), ring2: gold && c.restates, tag: tags ? '#' + c.i : '', data: c }));
const rankList = (chunks, order, k) => `<ol class="dense-rank">${order.slice(0, k).map((i, r) => { const c = chunks[i]; const g = c.has62 || c.has64;
  const tag = g ? [c.has62 && '§6.2', c.has64 && '§6.4'].filter(Boolean).join(' + ') : c.restates ? 'restates' : '';
  return `<li class="${g ? 'g' : ''}"><span class="dense-rn">${r + 1}</span><span class="dense-dot" style="background:${secColour(c.sec)}"></span><span class="dense-rc">${esc(c.short)}</span><span class="dense-rt">${tag}</span><span class="dense-rs">${c.cos.toFixed(3)}</span></li>`; }).join('')}</ol>`;

/* ============================================================ FIGS.dense_thumbs: D's four pages ============== */
FIGS.dense_thumbs = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  el.innerHTML = `<div class="dense-thumbs">${d.pages.map((p) => `<div class="dense-thumb" style="background-image:url(${BASE}${p.img})"><span>page ${p.page}</span></div>`).join('')}</div>`;
  return { step() {} };
};

/* ============================================================ FIGS.dense_page: the real page, highlighted =====
   data-page, data-view="x,y,w;…" (PDF points, one crop per click), data-marks="a,b;c;…" (one list per click; earlier
   marks stay on, the newest are emphasised). Marks are boxes around the page's real text lines (v5_dense_build.py). */
FIGS.dense_page = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const pages = el.dataset.doc === 'ERR' ? d.err.pages : d.pages;
  const pg = pages.find((p) => p.page === +(el.dataset.page || 1));
  const views = (el.dataset.view || '0,0,' + pg.w).split(';').map((v) => v.split(',').map(Number));
  const marks = (el.dataset.marks || '').split(';').map((s) => s.split(',').filter(Boolean));
  el.classList.add('dense-page');
  const W = el.offsetWidth || 860;
  el.innerHTML = `<div class="dense-pg"><div class="dense-pg-img" style="background-image:url(${BASE}${pg.img});width:${pg.w}px;height:${pg.h}px"></div></div>`;
  const inner = el.querySelector('.dense-pg-img');
  const boxes = {};
  for (const [name, m] of Object.entries(pg.marks || {})) {
    const b = document.createElement('div');
    b.className = 'dense-mk ' + (m.cls || '');
    b.style.cssText = `left:${m.x0 - 3}px;top:${m.top - 2.5}px;width:${m.x1 - m.x0 + 6}px;height:${m.bottom - m.top + 5}px`;
    inner.appendChild(b); boxes[name] = b;
  }
  const go = (k) => {
    const v = views[Math.min(k, views.length - 1)];
    const s = W / v[2];
    inner.style.transform = `translate(${-v[0] * s}px, ${-v[1] * s}px) scale(${s})`;
    const on = new Set(), cur = new Set(marks[Math.min(k, marks.length - 1)] || []);
    for (let i = 0; i <= Math.min(k, marks.length - 1); i++) (marks[i] || []).forEach((m) => on.add(m));
    for (const [n, b] of Object.entries(boxes)) { b.classList.toggle('on', on.has(n)); b.classList.toggle('cur', cur.has(n)); }
  };
  go(0);
  return { step(k) { go(k); } };
};

/* ============================================================ FIGS.dense_chunks: D cut into its chunks ========= */
FIGS.dense_chunks = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const P = d.play['s200-o15'];
  el.classList.add('dense-chunks');
  el.innerHTML = `<div class="dense-cards">${P.chunks.map((c) => `<div class="dense-card hd${c.has62 ? ' sel' : ''}" style="--c:${secColour(c.sec)}">
      <div class="dense-card-h"><b>#${c.i}</b><span>${c.tokens} tokens</span></div>
      <div class="dense-card-s">${esc(c.short.replace(/^#\d+ /, ''))}</div>
      <div class="dense-card-b">${esc(cut(one(c.body), 92))}</div></div>`).join('')}</div>`;
  return { step(k) { ['dense-s1', 'dense-s2', 'dense-s3'].forEach((c, i) => el.classList.toggle(c, k >= i + 1)); } };
};

/* ============================================================ FIGS.dense_full: the chunk we follow =========== */
FIGS.dense_full = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const c = d.play['s200-o15'].chunks.find((x) => x.has62);
  let body = esc(c.body);
  for (const k of ['6.2', '6.4']) {
    const re = new RegExp(`(${k.replace('.', '\\.')} [\\s\\S]*?)(?=\\n6\\.\\d |$)`);
    body = body.replace(re, '<span class="cl">$1</span>');
  }
  el.classList.add('dense-full');
  el.innerHTML = `<span class="hdr">${esc(c.header)}</span>${body}`;
  return { step(k) { el.classList.toggle('on', k >= 1); } };
};

/* ============================================================ FIGS.dense_flow: chunk → 384 numbers ==========
   Six boxes in two rows, one per click, with the selected chunk's real pieces and numbers inside. */
FIGS.dense_flow = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const s = d.selected, mi = d.model_info;
  const vec = s.vector;
  const col = (x, k = 9) => (x >= 0 ? `rgba(11,87,208,${Math.min(1, Math.abs(x) * k).toFixed(2)})` : `rgba(196,81,31,${Math.min(1, Math.abs(x) * k).toFixed(2)})`);
  const box = (k, c, r, key, inner, foot, cls = '') => `<div class="dense-fb ${cls}" data-k="${k}" style="grid-column:${c};grid-row:${r}"><span class="dense-fk">${key}</span>${inner}${foot ? `<span class="dense-fm">${foot}</span>` : ''}</div>`;
  const arrow = (k, c, r, ch) => `<div class="dense-fa" data-k="${k}" style="grid-column:${c};grid-row:${r}">${ch}</div>`;
  el.classList.add('dense-flow');
  el.innerHTML =
    box(0, 1, 1, '1 · The chunk’s text', `<div class="dense-fx">${esc(cut(one(s.text), 190))}</div>`, `${s.o200k_tokens} tokens as we count chunk size (o200k)`)
    + arrow(1, 2, 1, '→')
    + box(1, 3, 1, '2 · Tokenizer: WordPiece', `<div class="dense-chips">${s.pieces.slice(0, 16).map((p) => `<span class="dense-chip${p.startsWith('##') ? ' cont' : ''}${p === '[CLS]' ? ' cls' : ''}">${esc(p)}</span>`).join('')}<span class="dense-chip more">… ${s.n_pieces - 16} more</span></div>`, `${s.n_pieces} pieces from a vocabulary of ${fmt(mi.vocab)}; at most ${mi.max_seq_length}`)
    + arrow(2, 4, 1, '→')
    + box(2, 5, 1, '3 · Encoder: BERT', `<div class="dense-enc">${Array.from({ length: mi.layers }, (_, i) => `<i style="opacity:${(0.3 + 0.7 * (i + 1) / mi.layers).toFixed(2)}"></i>`).join('')}</div>`, `${mi.layers} layers, ${mi.heads} attention heads, ${mi.dim} numbers wide; every piece looks at every other`)
    + arrow(3, 5, 2, '↓')
    + box(3, 5, 3, '4 · One vector per piece', `<div class="dense-mat">${s.token_vectors_head.slice(0, 5).map((row, i) => `<div><span>${esc(s.pieces[i])}</span>${row.slice(0, 5).map((x) => `<code>${x.toFixed(2)}</code>`).join('')}<em>…</em></div>`).join('')}<div class="dense-mat-more">${s.token_vectors_shape[0]} rows (one per piece) × ${s.token_vectors_shape[1]} numbers</div></div>`, '')
    + arrow(4, 4, 3, '←')
    + box(4, 3, 3, '5 · Pool, then normalise', `<div class="dense-fx">The model’s pooling is <b>${esc(mi.pooling.toUpperCase())}</b>: keep only the first row, the [CLS] piece. Its length is ${s.cls_norm.toFixed(2)}; divide by it so the length is 1.</div>`, `checked: cosine(final vector, normalised [CLS] row) = ${s.cos_final_vs_cls.toFixed(4)}; against the mean of all rows, ${s.cos_final_vs_mean.toFixed(2)}`)
    + arrow(5, 2, 3, '←')
    + box(5, 1, 3, '6 · One vector for the chunk', `<div class="dense-vstrip">${vec.map((x) => `<i style="background:${col(x)}"></i>`).join('')}</div><div class="dense-fx mono">[${vec.slice(0, 5).map((x) => x.toFixed(3)).join(', ')}, … , ${vec.slice(-2).map((x) => x.toFixed(3)).join(', ')}]</div>`, `${mi.dim} numbers, length ${s.vector_norm.toFixed(3)}`, 'dense-fout');
  return { step(k) { reveal(el, k); } };
};

/* ============================================================ FIGS.dense_pieces: every WordPiece of the chunk ===== */
FIGS.dense_pieces = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const s = d.selected, hi = new Set(s.hiIdx);
  el.classList.add('dense-pieces');
  el.innerHTML = `<div class="dense-chips big">${s.pieces.map((p, i) => `<span class="dense-chip${p.startsWith('##') ? ' cont' : ''}${/^\[(CLS|SEP)\]$/.test(p) ? ' cls' : ''}${hi.has(i) ? ' hi' : ''}">${esc(p)}</span>`).join('')}</div>`;
  return { step(k) { el.classList.toggle('dense-s1', k >= 1); el.classList.toggle('dense-s2', k >= 2); } };
};

/* ============================================================ FIGS.dense_vec: 384 numbers, then one cosine ======= */
FIGS.dense_vec = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const s = d.selected;
  const col = (x) => (x >= 0 ? `rgba(11,87,208,${Math.min(1, Math.abs(x) * 8).toFixed(2)})` : `rgba(196,81,31,${Math.min(1, Math.abs(x) * 8).toFixed(2)})`);
  const row = (v, lab, k) => `<div class="dense-vrow" data-k="${k}"><span class="dense-vl">${lab}</span><div class="dense-vgrid">${v.map((x) => `<i style="background:${col(x)}"></i>`).join('')}</div>
    <div class="dense-vnums">${v.slice(0, 10).map((x, i) => `<span><em>${i}</em>${x.toFixed(4)}</span>`).join('')}<span class="dense-vdots">… ${v.length - 10} more</span></div></div>`;
  const prods = s.vector.slice(0, 4).map((x, i) => `(${x.toFixed(3)} × ${s.query_vector[i].toFixed(3)})`).join(' + ');
  el.classList.add('dense-vec');
  el.innerHTML = row(s.vector, `Chunk #${s.i}, the one holding §6.2 · ${s.vector.length} numbers · blue above 0, ember below`, 0)
    + row(s.query_vector, 'Emma’s question, embedded by the same model (with bge’s search instruction in front)', 1)
    + `<div class="dense-vcos" data-k="2">Cosine = ${prods} + … 380 more products = <b>${s.cos_q.toFixed(4)}</b>. Both have length 1, so this sum is the cosine.</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ============================================================ FIGS.dense_cos2d: cosine drawn in two dimensions ===
   Q along the x-axis; each chunk at its real angle to Q (arccos of its real 384-d cosine): exact for the angle to Q. */
FIGS.dense_cos2d = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const P = d.play['s200-o15'];
  const pick = d.cos2d.map((i) => P.chunks[i]);
  const w = el.offsetWidth || 760, h = el.offsetHeight || 600, ox = 60, oy = h - 60, R = Math.min(w - 250, h - 110);
  let s = `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="overflow:visible">
    <path d="M ${ox} ${oy} L ${ox + R + 40} ${oy}" stroke="rgba(18,19,23,.25)"/><path d="M ${ox} ${oy} L ${ox} ${oy - R - 30}" stroke="rgba(18,19,23,.25)"/>
    <path d="M ${ox + R} ${oy} A ${R} ${R} 0 0 0 ${ox} ${oy - R}" fill="none" stroke="rgba(18,19,23,.14)" stroke-dasharray="4 5"/>
    <g data-k="0"><line x1="${ox}" y1="${oy}" x2="${ox + R}" y2="${oy}" stroke="#121317" stroke-width="4"/><circle cx="${ox + R}" cy="${oy}" r="7" fill="#121317"/>
    <text x="${ox + R}" y="${oy + 30}" text-anchor="end" style="font:600 18px var(--font)">Emma’s question</text></g>`;
  const pos = pick.map((c) => { const th = Math.acos(Math.max(-1, Math.min(1, c.cos))); return { c, th, x: ox + R * Math.cos(th), y: oy - R * Math.sin(th) }; });
  const byY = pos.slice().sort((a, b) => a.y - b.y);
  byY.forEach((p, i) => { p.ly = i ? Math.max(p.y, byY[i - 1].ly + 54) : p.y; });
  pos.forEach((p, j) => {
    const { c, th, x, y, ly } = p;
    const colr = secColour(c.sec), ar = 80 + j * 50;
    s += `<g data-k="${j + 1}"><line x1="${ox}" y1="${oy}" x2="${x}" y2="${y}" stroke="${colr}" stroke-width="4"/><circle cx="${x}" cy="${y}" r="7" fill="${colr}"/>
      <path d="M ${ox + ar} ${oy} A ${ar} ${ar} 0 0 0 ${ox + ar * Math.cos(th)} ${oy - ar * Math.sin(th)}" fill="none" stroke="${colr}" stroke-width="2"/>
      ${ly !== y ? `<line x1="${x + 8}" y1="${y + 2}" x2="${x + 22}" y2="${ly - 4}" stroke="${colr}" stroke-width="1"/>` : ''}
      <text x="${x + 24}" y="${ly - 6}" style="font:600 17px var(--font);fill:${colr}">${esc(c.short)}</text>
      <text x="${x + 24}" y="${ly + 16}" style="font:500 16px var(--mono);fill:#45474d">cosine ${c.cos.toFixed(3)} · ${(th * 180 / Math.PI).toFixed(1)}°</text></g>`;
  });
  el.innerHTML = s + '</svg>';
  el.classList.add('dense-cos2d');
  return { step(k) { el.querySelectorAll('[data-k]').forEach((g) => { g.style.opacity = +g.dataset.k > k ? 0 : 1; }); } };
};

/* ============================================================ FIGS.dense_space: D's chunks in 3D ==========================
   data-mode="chunks": steps 1 = ring the chunk holding §6.2/§6.4.  data-mode="query": Q drops in; step 1 = lines to the top 5. */
FIGS.dense_space = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const mode = el.dataset.mode || 'chunks';
  const P = d.play['s200-o15'];
  el.classList.add('dense-space');
  el.innerHTML = `<div class="dense-cvhost"></div>
    <div class="dense-legend">${d.sections.map((s) => `<span><i style="background:${secColour(s)}"></i>${esc(s)}</span>`).join('')}</div>
    <div class="dense-hint">Drag to rotate · hover a point to read it · click to pin</div>`;
  const sp = Space3D(el.querySelector('.dense-cvhost'), { tip: (p) => chunkTip(p.data), padX: 40, padBottom: 70, axes: axesOf(d.pca.explained) });
  const ext = extentOf([P.chunks.map((c) => c.xyz), [d.pca.q_xyz]]);
  let shown = -1;
  return { step(k) {
    if (k !== shown) {
      shown = k;
      sp.setPoints(ptsOf(P.chunks, mode === 'query' || k >= 1, true), { ext, animate: false });
      if (mode === 'query') { sp.setQuery({ xyz: d.pca.q_xyz, label: 'Emma’s question' }); sp.setLinks(k >= 1 ? P.order.slice(0, 5).map((i) => P.chunks[i].cid) : []); }
    }
    sp.kick();
  } };
};

/* the ranked list next to the 3D view */
FIGS.dense_ranked = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const P = d.play[el.dataset.cfg || 's200-o15'];
  el.innerHTML = rankList(P.chunks, P.order, +(el.dataset.n || 5));
  return { step() {} };
};

/* ============================================================ FIGS.dense_play: the chunk-size playground =====
   One 3D space (PCA fitted on the default chunks, so every configuration lands in the same axes) and a panel.
   data-preset="size": clicks walk 200 → 50 → 800 → whole → 200. data-preset="knobs": k, the header, the model. */
FIGS.dense_play = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const preset = el.dataset.preset || 'size';
  const SIZES = [['50', 's50'], ['100', 's100'], ['200', 's200'], ['400', 's400'], ['800', 's800'], ['one per section', 'section'], ['whole document', 'whole']];
  const DEF = { size: 's200', ov: 15, k: 5, head: true, model: 'bge-small' };
  const st = { ...DEF };
  el.classList.add('dense-play');
  el.innerHTML = `<div class="dense-cvhost"></div><div class="dense-panel">
      <div class="ctl dense-ctl${preset === 'size' ? '' : ' dense-hide'}" data-c="size"><span class="dense-cl">Chunk size, tokens</span>${SIZES.map(([l, v]) => `<button data-v="${v}">${l}</button>`).join('')}</div>
      <div class="ctl dense-ctl inl${preset === 'size' ? '' : ' dense-hide'}" data-c="ov"><span class="dense-cl">Overlap</span><button data-v="0">0%</button><button data-v="15">15%</button></div>
      <div class="ctl dense-ctl inl" data-c="k"><span class="dense-cl">Top k</span>${[1, 3, 5, 10].map((v) => `<button data-v="${v}">${v}</button>`).join('')}</div>
      <div class="ctl dense-ctl inl${preset === 'size' ? ' dense-hide' : ''}" data-c="head"><span class="dense-cl">Header prefix</span><button data-v="on">on</button><button data-v="off">off</button></div>
      <div class="ctl dense-ctl${preset === 'size' ? ' dense-hide' : ''}" data-c="model"><span class="dense-cl">Embedding model</span>${d.modelOrder.map((m) => `<button data-v="${m}">${esc(m)}</button>`).join('')}</div>
      <div class="dense-read"></div></div>`;
  const sp = Space3D(el.querySelector('.dense-cvhost'), { tip: (p) => chunkTip(p.data), padX: 30, axes: axesOf(d.pca.explained) });
  const ext = extentOf([d.play['s200-o15'].chunks.map((c) => c.xyz), [d.pca.q_xyz]]);
  const current = () => {
    if (st.model !== 'bge-small') return { cfg: d.models_play[st.model], own: true };
    if (!st.head) return { cfg: d.play['s200-o15-nohead'], nohead: true };
    if (st.size === 'section' || st.size === 'whole') return { cfg: d.play[st.size] };
    return { cfg: d.play[`${st.size}-o${st.ov}`] };
  };
  const render = (animate) => {
    const { cfg, own, nohead } = current();
    el.querySelectorAll('.dense-ctl').forEach((g) => g.querySelectorAll('button').forEach((b) => {
      const c = g.dataset.c, v = b.dataset.v;
      b.classList.toggle('on', (c === 'size' && v === st.size) || (c === 'ov' && +v === st.ov) || (c === 'k' && +v === st.k) || (c === 'head' && (v === 'on') === st.head) || (c === 'model' && v === st.model));
      b.disabled = ((c === 'size' || c === 'ov') && (st.model !== 'bge-small' || !st.head)) || (c === 'ov' && (st.size === 'section' || st.size === 'whole'))
        || ((c === 'head' || c === 'model') && st.size !== 's200' && !(c === 'head' && v === 'on') && !(c === 'model' && v === 'bge-small'));
    }));
    const pts = ptsOf(cfg.chunks).map((p) => ({ ...p, r: cfg.n === 1 ? 17 : Math.max(5, Math.min(16, 3.5 + Math.sqrt(p.data.tokens) * 0.55)) }));
    sp.S.axes = own ? ['PC1', 'PC2', 'PC3'] : axesOf(d.pca.explained);
    sp.setPoints(pts, { ext: own ? extentOf([cfg.chunks.map((c) => c.xyz), [cfg.q.xyz]]) : ext, animate });
    sp.setQuery({ xyz: cfg.q.xyz, label: 'Q' });
    sp.setLinks(cfg.order.slice(0, st.k).map((i) => cfg.chunks[i].cid));
    const tk = cfg.topk[Math.min(st.k, cfg.topk.length) - 1];
    const trunc = cfg.chunks.filter((c) => c.truncated);
    const share = tk.tokens ? tk.answer_tokens / tk.tokens : 0;
    const rk = (x) => (x == null ? '<em class="b">–</em>' : `<em class="${x <= st.k ? 'a' : 'b'}">${x}</em>`);
    const split = (key) => cfg.chunks.filter((c) => c[key] > 0.01).length;
    const whole = cfg.n === 1 ? cfg.chunks[0] : null;
    el.querySelector('.dense-read').innerHTML = `
      <div class="dense-stats">
        <div><b>${cfg.n}</b><span>chunk${cfg.n > 1 ? 's' : ''}, ~${fmt(Math.round(cfg.tokens_mean))} tokens each</span></div>
        <div><b>${fmt(tk.tokens)}</b><span>tokens in the top ${tk.k}; <b class="${share >= 0.12 ? 'a' : 'b'}">${Math.round(tk.answer_tokens)}</b> of them are §6.2 / §6.4 (${(100 * share).toFixed(0)}%)</span></div>
        <div><b>${rk(cfg.rank62)}</b><span>rank of the chunk with the §6.2 rule${split('part62') > 1 ? `; §6.2 is cut into ${split('part62')} chunks` : ''}</span></div>
        <div><b>${rk(cfg.rank64)}</b><span>rank of the chunk with §6.4${split('part64') > 1 ? `; cut into ${split('part64')}` : ''}</span></div>
      </div>
      ${trunc.length ? `<div class="dense-warn"><b>${trunc.length} chunk${trunc.length > 1 ? 's are' : ' is'} over the model’s 512-piece limit.</b> ${whole ? `The vector of the whole document reads only its first ${whole.seen_pct}%: it stops before §6.` : 'Their vectors read only the start of each.'}</div>` : ''}
      ${own ? `<div class="dense-note">${esc(d.modelShort[st.model])} has its own space: its own PCA (${Math.round(100 * cfg.explained3)}% of the spread in 3 axes). Its cosines run ${cfg.cos_spread.min.toFixed(2)} to ${cfg.cos_spread.max.toFixed(2)}; compare ranks, not raw scores, across models.</div>`
        : nohead ? `<div class="dense-note">Header prefix off: the same 15 chunks, embedded without their “[Purchase Policy · POL-PUR-001 · v4.1 …]” lines. Chunk #5’s cosine: ${cfg.chunks[5].cos.toFixed(3)} (with the header ${d.play['s200-o15'].chunks[5].cos.toFixed(3)}).</div>` : ''}
      ${rankList(cfg.chunks, cfg.order, Math.min(st.k, preset === 'size' ? 5 : 3))}`;
  };
  el.querySelectorAll('.dense-ctl').forEach((g) => g.addEventListener('click', (e) => {
    const b = e.target.closest('button'); stop(e); if (!b || b.disabled) return;
    const c = g.dataset.c, v = b.dataset.v;
    if (c === 'size') st.size = v; else if (c === 'ov') st.ov = +v; else if (c === 'k') st.k = +v; else if (c === 'head') st.head = v === 'on'; else st.model = v;
    render(true);
  }));
  const walk = preset === 'size' ? [{}, { size: 's50' }, { size: 's800' }, { size: 'whole' }, {}]
    : [{}, { k: 1 }, { k: 10 }, { head: false }, { model: 'e5-small' }];
  let lastK = -1;
  return { step(k) { if (k !== lastK) { const first = lastK < 0; lastK = k; Object.assign(st, DEF, walk[Math.min(k, walk.length - 1)]); render(!first); } sp.kick(); } };
};

/* ============================================================ FIGS.dense_sizetab: every size, one table ============== */
FIGS.dense_sizetab = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const rows = [['50 tokens', 's50-o15'], ['100', 's100-o15'], ['200', 's200-o15'], ['400', 's400-o15'], ['800', 's800-o15'], ['one per section', 'section'], ['whole document', 'whole']];
  el.classList.add('dense-tab');
  el.innerHTML = `<table class="t"><tr><th>Chunk size</th><th class="n">Chunks</th><th class="n">§6.2 rule rank</th><th class="n">§6.4 rank</th><th class="n">Top-5 tokens</th><th class="n">Of which §6.2/§6.4</th><th>What you see</th></tr>${rows.map(([lab, key], i) => {
    const c = d.play[key], tk = c.topk[Math.min(5, c.topk.length) - 1], tr = c.chunks.filter((x) => x.truncated).length;
    const sp = c.chunks.filter((x) => x.part62 > 0.01).length;
    const note = sp > 1 ? `§6.2 cut into ${sp} pieces` : tr ? `${tr} of ${c.n} chunks over 512 pieces${c.n === 1 ? `; vector reads ${c.chunks[0].seen_pct}%` : ''}` : c.n <= 7 ? 'few, long chunks' : 'clause kept whole';
    return `<tr data-k="${i === 2 ? 0 : i < 2 ? 1 : 2}" class="${key === 's200-o15' ? 'hi' : ''}"><td>${lab}</td><td class="n">${c.n}</td><td class="n">${c.rank62 ?? '–'}</td><td class="n">${c.rank64 ?? '–'}</td><td class="n">${fmt(tk.tokens)}${tk.k < 5 ? ` (all ${tk.k})` : ''}</td><td class="n">${Math.round(tk.answer_tokens)} · ${Math.round(100 * tk.answer_tokens / tk.tokens)}%</td><td class="${sp > 1 || tr ? 'b' : ''}">${note}</td></tr>`; }).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

/* ============================================================ FIGS.dense_gridbars: the whole dump, one knob ======== */
FIGS.dense_gridbars = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const G = d.grid;
  const bar = (lab, v, sub, hi, k) => `<div class="dense-bar${hi ? ' hi' : ''}" data-k="${k}"><span class="l">${lab}</span><span class="t"><i style="width:${(100 * v).toFixed(1)}%"></i></span><span class="v">${v.toFixed(3)}</span>${sub ? `<span class="s">${sub}</span>` : ''}</div>`;
  const best = Math.max(...Object.values(G.sizes).map((x) => x['recall@5']));
  el.innerHTML = `<div class="dense-bars">
    <div class="dense-h4" data-k="0">Chunk size (structured parser, structure-aware, 15% overlap, bge-small, dense only)</div>
    ${Object.entries(G.sizes).map(([s, x]) => bar(`${s} tokens`, x['recall@5'], `${fmt(G.n_chunks[s])} chunks, ${Math.round(G.tokens_mean[s])} tokens on average · MRR ${x.mrr.toFixed(3)}`, x['recall@5'] === best, 0)).join('')}
    <div class="dense-h4" data-k="1" style="margin-top:8px">Overlap, at 200 tokens</div>
    ${Object.entries(G.overlap).map(([s, x]) => bar(s, x['recall@5'], '', false, 1)).join('')}
    <div class="dense-h4" data-k="2" style="margin-top:8px">Parser, at 200 tokens</div>
    ${Object.entries(G.parser).map(([s, x]) => bar(s, x['recall@5'], '', false, 2)).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ============================================================ FIGS.dense_errspace: MAN-ERR-72 and Q-0412 ======= */
FIGS.dense_errspace = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const E = d.err;
  el.classList.add('dense-space');
  const fams = Object.keys(E.famColour);
  el.innerHTML = `<div class="dense-cvhost"></div><div class="dense-legend">${fams.map((f) => `<span><i style="background:${E.famColour[f]}"></i>${f === 'other' ? 'other codes' : `ERR-${f}`}</span>`).join('')}</div>
    <div class="dense-hint">${E.n} chunks of MAN-ERR-72 · drag, hover</div>`;
  const tip = (p) => { const c = p.data; return `<div class="dense-tip-h">${esc(c.cite)}</div><div class="dense-tip-m">cosine <b>${c.cos.toFixed(3)}</b> · rank ${c.rank}${c.gold ? ' · <span class="dense-g">holds the ERR-PO-0412 entry</span>' : ''}<br>codes: ${esc(c.codes.slice(0, 5).join(', '))}</div><div class="dense-tip-b">${esc(cut(one(c.body), 220))}</div>`; };
  const sp = Space3D(el.querySelector('.dense-cvhost'), { tip, padX: 30, padBottom: 60 });
  const ext = extentOf([E.chunks.map((c) => c.xyz), [E.q_xyz]]);
  sp.setPoints(E.chunks.map((c) => ({ id: c.cid, xyz: c.xyz, c: E.famColour[c.fam] || '#b9bec7', r: 7.5, gold: c.gold, tag: c.rank === 1 ? 'ERR-MAT-0412' : c.gold ? 'ERR-PO-0412' : '', data: c })), { ext, animate: false });
  sp.setQuery({ xyz: E.q_xyz, label: 'Q-0412' });
  let lastK = -1;
  return { step(k) { if (k !== lastK) { lastK = k; sp.setLinks(k >= 1 ? E.order.slice(0, 6).map((i) => E.chunks[i].cid) : []); } sp.kick(); } };
};

FIGS.dense_errlist = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const E = d.err;
  el.innerHTML = `<ol class="dense-rank">${E.order.slice(0, 6).map((i, r) => { const c = E.chunks[i];
    const name = c.gold ? 'ERR-PO-0105 … 0201 … <b class="dense-g">ERR-PO-0412</b>' : esc(c.cite.split('§ ')[1] || c.cite);
    return `<li class="${c.gold ? 'g' : ''}"><span class="dense-rn">${r + 1}</span><span class="dense-dot" style="background:${E.famColour[c.fam] || '#b9bec7'}"></span><span class="dense-rc">${name}</span><span class="dense-rs">${c.cos.toFixed(3)}</span></li>`; }).join('')}</ol>`;
  return { step() {} };
};

/* ============================================================ FIGS.dense_fail: one failure case ==================
   data-case="Q-401" data-extra="digits|numbers|negation|versions|tables|crowd|wins|codes" data-n=rows of the top list.
   Steps: 1 = the dense top list; 2 = why, with the probe that shows it. */
const wpRow = (pieces, ref) => `<span class="dense-wp">${pieces.filter((p) => !/^\[(CLS|SEP)\]$/.test(p)).map((p, i) => `<span class="dense-chip${ref && ref.filter((x) => !/^\[(CLS|SEP)\]$/.test(x))[i] !== p ? ' diff' : ''}">${esc(p)}</span>`).join('')}</span>`;
const probeTable = (pr, keyLab, diffWord) => `<table>${pr.rows.map((r) => `<tr><td>${r.label === 'original' ? '<b>the rule as written</b>' : esc(r.label)}</td><td class="n">${r.cos_to_original.toFixed(3)}</td><td class="n">${r.cos_to_question.toFixed(3)}</td></tr>`).join('')}</table>`;
const EXTRA = {
  codes: (d) => { const w = d.wordpieces, p = d.probes.codes; return `<div class="dense-probe"><div class="dense-h4">What the model sees · WordPiece</div>
      ${['ERR-PO-0412', 'ERR-PO-0413', 'ERR-MAT-0412'].map((s) => `<div>${wpRow(w[s], s === 'ERR-PO-0412' ? null : w['ERR-PO-0412'])}</div>`).join('')}
      <table>${p.rows.slice(1).map((r) => `<tr><td>“ERR-PO-0412” against “${esc(r.text)}”</td><td class="n">${r.cos_to_original.toFixed(3)}</td></tr>`).join('')}</table></div>`; },
  digits: (d) => { const w = d.wordpieces, s = d.siblings; return `<div class="dense-probe"><div class="dense-h4">The current item rows, as vectors</div>
      <table>${Object.entries(s.cos_BAT500_row_to).map(([k, v]) => `<tr><td>row BAT-500 against row ${esc(k)}</td><td class="n">${v.toFixed(4)}</td></tr>`).join('')}</table>
      <div class="dense-h4" style="margin-top:6px">WordPiece</div><div>${wpRow(w['BAT-500'])} ${wpRow(w['BAT-375'], w['BAT-500'])}</div></div>`; },
  numbers: (d) => { const p = d.probes.numbers; return `<div class="dense-probe"><div class="dense-h4">§3.3 with its amount edited · cosine to the real rule · to the question</div>${probeTable(p)}</div>`; },
  negation: (d) => { const p = d.probes.negation; return `<div class="dense-probe"><div class="dense-h4">§6.2’s sentence, edited · cosine to the real sentence · to the question</div>${probeTable(p)}</div>`; },
  versions: (d) => { const v = d.versions, c = d.fail['Q-202']; return `<div class="dense-probe"><div class="dense-h4">The same text in three versions</div><table>
      ${v.old.map((o) => `<tr><td>${esc(o.cite)} <span class="dense-tag old">superseded</span></td><td class="n">${o.cos_to_current[0].toFixed(3)}</td></tr>`).join('')}
      </table><div style="font-size:15.5px;margin-top:6px">Cosine to the current v4.1 chunk. With superseded and not-yet-in-force chunks filtered out <i>before</i> ranking, the current §3.3 chunk moves from ${c.answer_chunks.find((a) => a.cid.includes('v4.1')) ? ord(c.answer_chunks.find((a) => a.cid.includes('v4.1')).dense_rank) : '–'} to ${ord(c.dense_with_stale_filtered_rank_first_answer_chunk)}.</div></div>`; },
  tables: (d) => { const t = d.tables['Q-407']; return `<div class="dense-probe"><div class="dense-h4">The same row, two parsers</div><div class="dense-row2">
      <div><b>plain · rank ${t.plain.rank}</b><div class="dense-rowtxt">${esc(cut(t.plain.text.split('\n').slice(0, 2).join('\n'), 150))}</div></div>
      <div><b>structured · rank ${t.structured.rank}</b><div class="dense-rowtxt">${esc(cut(t.structured.text.split('\n').slice(2, 3).join('\n'), 150))}</div></div></div></div>`; },
  crowd: (d) => { const c = d.crowd; return `<div class="dense-probe"><table><tr><td>chunks in the dump</td><td class="n">${fmt(c.n_chunks)}</td></tr><tr><td>chunks that mention lithium or batteries</td><td class="n">${fmt(c.n_battery_chunks)}</td></tr>
      <tr><td>chunks closer to the question than the carrier notes</td><td class="n">${fmt(c.n_above_gold)}</td></tr><tr><td>… of them about lithium or batteries</td><td class="n">${fmt(c.n_battery_above_gold)}</td></tr></table></div>`; },
  wins: () => '',
};
FIGS.dense_fail = (el) => {
  const d = DD(); if (!d) return need(el, 'v5/dense_data.js');
  const id = el.dataset.case, c = d.fail[id], extra = el.dataset.extra || '';
  if (!c) return need(el, `failure case ${esc(id)}`);
  const n = +(el.dataset.n || 6);
  const ans = c.shown;
  const dfull = d.play['s200-o15'].chunks.find((x) => x.cid === ans.cid);
  let atext = one(dfull ? dfull.body : ans.text);
  if (el.dataset.needle && atext.indexOf(el.dataset.needle) > 0) atext = '… ' + atext.slice(atext.indexOf(el.dataset.needle));
  const code = (t) => { const m = /itm_cd: ([A-Z0-9.-]+)/.exec(t || ''); return m ? ` · <b>${esc(m[1])}</b>` : ''; };
  const wins = extra === 'wins';
  el.classList.add('dense-fail');
  const short = (cite) => esc(cut(cite, 62));
  el.innerHTML = `<div class="dense-fail-l">
      <div class="dense-q"><span class="who">${esc(id)} · golden set · ${esc(c.type.replace('_', ' '))}</span>${esc(c.question)}</div>
      <div class="dense-gold"><div class="k">The chunk that answers <span>${short(ans.cite)}</span></div><div class="x">${esc(cut(atext, 230))}</div></div>
      <div class="dense-big${wins ? ' ok' : ''}"><b>${ord(ans.dense_rank)}</b><span>where dense search ranks it,<br>of ${fmt(28953)} chunks${wins ? `; a keyword match ranks it ${ord(c.bm25_rank_first_answer_chunk)}` : ''}</span></div>
      <div class="dense-why${wins ? ' ok' : ''}" data-k="2"><span class="k">${wins ? 'Why dense wins here' : 'Why'}</span>${esc(el.dataset.why || c.why_dense)}</div></div>
    <div class="dense-fail-r"><div class="dense-h4" data-k="1">Dense top ${n} · whole dump · bge-small</div>
      <ol class="dense-rank" data-k="1">${c.dense_top10.slice(0, n).map((r) => `<li class="${r.fact || r.gold ? 'g' : ''}${r.superseded || r.future ? ' old' : ''}"><span class="dense-rn">${r.rank}</span><span></span><span class="dense-rc">${short(r.cite)}${code(r.text)}${r.superseded ? '<span class="dense-tag old">old copy</span>' : ''}${r.future ? '<span class="dense-tag old">not yet in force</span>' : ''}${r.fact ? '<span class="dense-tag ans">answer</span>' : ''}</span><span class="dense-rs">${r.score.toFixed(3)}</span></li>`).join('')}</ol>
      <div data-k="2">${EXTRA[extra] ? EXTRA[extra](d) : ''}</div></div>`;
  return { step(k) { reveal(el, k); } };
};
})();
