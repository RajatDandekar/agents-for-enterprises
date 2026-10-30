/* The Northbridge Experience: shared helpers for every page (player id, API calls, nav, formatting, JSON and Python colouring). */
(() => {
'use strict';
const KEY = 'rx_pid', NAME = 'rx_name';
const getCookie = (k) => (document.cookie.split('; ').find((c) => c.startsWith(k + '=')) || '').split('=')[1] || '';
const store = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } },
  del(k) { try { localStorage.removeItem(k); } catch (e) { /* private mode */ } },
};
const RX = {
  pid() { return store.get(KEY) || getCookie(KEY) || ''; },
  name() { return store.get(NAME) || ''; },
  setPlayer(pid, name) {
    store.set(KEY, pid); store.set(NAME, name);
    document.cookie = `${KEY}=${pid}; path=/; max-age=${60 * 60 * 24 * 60}; samesite=lax`;
    document.cookie = `pid=${pid}; path=/; max-age=${60 * 60 * 24 * 60}; samesite=lax`;  /* the Workflow Studio reads "pid" */
  },
  forget() { store.del(KEY); store.del(NAME); document.cookie = `${KEY}=; path=/; max-age=0`; document.cookie = 'pid=; path=/; max-age=0'; },
  async api(path, body, method) {
    const h = { 'Content-Type': 'application/json' };
    const pid = RX.pid(); if (pid) h['X-Player'] = pid;
    const r = await fetch(path, { method: method || (body === undefined ? 'GET' : 'POST'), headers: h,
      body: body === undefined ? undefined : JSON.stringify(body) });
    let d = null; try { d = await r.json(); } catch (e) { d = {}; }
    if (!r.ok) { const err = new Error((d && d.detail) || ('HTTP ' + r.status)); err.status = r.status; throw err; }
    return d;
  },
  async me() {
    if (!RX.pid()) return null;
    if (getCookie('pid') !== RX.pid()) RX.setPlayer(RX.pid(), RX.name());
    try { const m = await RX.api('/api/me'); store.set(NAME, m.name); return m; }
    catch (e) { if (e.status === 401) RX.forget(); return null; }
  },
  async needPlayer() {
    const m = await RX.me();
    if (!m) { location.href = '/?next=' + encodeURIComponent(location.pathname + location.search); return null; }
    return m;
  },
  nav(active) {
    const items = [['/', '1', 'Invitation'], ['/brief', '2', 'Your brief'], ['/before', '3', 'Before'], ['/after', '4', 'After'],
      ['/tools', '', 'Tools'], ['/studio', '', 'Studio']];
    const el = document.createElement('nav'); el.className = 'nav';
    el.innerHTML = `<span class="mark">Northbridge</span>` + items.map(([h, n, t]) =>
      `<a href="${h}" class="${active === h ? 'on' : ''}">${n ? `<span class="n">${n}</span>` : ''}${t}</a>`).join('') +
      (RX.name() ? `<span class="who">${RX.esc(RX.name())}</span>` : '');
    document.body.prepend(el);
    return el;
  },
  esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); },
  inr(n, dec) { if (n == null || isNaN(n)) return '—'; return new Intl.NumberFormat('en-GB', { maximumFractionDigits: dec || 0, minimumFractionDigits: dec || 0 }).format(n); },
  // Model cost is kept internally in rupees at the course's fixed rate (llm.py USD_INR = 88); shown in pounds at $1 = £0.79.
  gbpFromInr(v) { return (v || 0) / 88 * 0.79; },
  rupees(n) { return n == null ? '—' : '£' + RX.inr(n); },
  mmss(s) { s = Math.max(0, Math.round(s || 0)); const m = Math.floor(s / 60); return m + ':' + String(s % 60).padStart(2, '0'); },
  dur(s) { s = Math.round(s || 0); if (s < 60) return s + ' s'; const m = Math.floor(s / 60); return m + ' min ' + (s % 60) + ' s'; },
  toast(msg, ms) {
    let t = document.querySelector('.toast'); if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.append(t); }
    t.textContent = msg; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), ms || 2600);
  },
  reveal(root) {
    const els = (root || document).querySelectorAll('.rv:not(.in)');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }), { threshold: 0.12 });
    els.forEach((e) => io.observe(e));
  },
  json(v) {  /* pretty JSON with colour spans */
    const s = JSON.stringify(v, null, 2);
    if (s === undefined) return '';
    const re = /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false)\b|\bnull\b|-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/g;
    let out = '', last = 0, m;
    while ((m = re.exec(s))) {
      out += RX.esc(s.slice(last, m.index));
      const [all, str, colon, bool] = m;
      if (str) out += colon ? `<span class="k">${RX.esc(str)}</span>${colon}` : `<span class="s">${RX.esc(str)}</span>`;
      else if (bool) out += `<span class="b">${all}</span>`;
      else if (all === 'null') out += `<span class="z">${all}</span>`;
      else out += `<span class="n">${all}</span>`;
      last = re.lastIndex;
    }
    return out + RX.esc(s.slice(last));
  },
  py(src) {  /* a small Python highlighter: comments, strings, keywords, numbers, def names */
    const KW = new Set('def return if elif else for in while try except raise from import as with class not and or is None True False lambda pass continue break yield async await global'.split(' '));
    let out = '', i = 0;
    const e = RX.esc;
    while (i < src.length) {
      const c = src[i];
      if (c === '#') { const j = src.indexOf('\n', i); const k = j < 0 ? src.length : j; out += `<span class="cm">${e(src.slice(i, k))}</span>`; i = k; continue; }
      if (c === '"' || c === "'") {
        const tri = src.slice(i, i + 3) === c.repeat(3);
        const q = tri ? c.repeat(3) : c; let j = i + q.length;
        while (j < src.length && src.slice(j, j + q.length) !== q) { if (src[j] === '\\') j++; if (!tri && src[j] === '\n') break; j++; }
        j = Math.min(src.length, j + q.length);
        let pre = ''; const m = out.match(/([fbr]{1,2})$/i); if (m) { out = out.slice(0, -m[1].length); pre = m[1]; }
        out += `<span class="st">${e(pre + src.slice(i, j))}</span>`; i = j; continue;
      }
      if (/[A-Za-z_]/.test(c)) {
        let j = i; while (j < src.length && /\w/.test(src[j])) j++;
        const w = src.slice(i, j);
        if (KW.has(w)) out += `<span class="kw">${w}</span>`;
        else if (/\bdef\s+$/.test(src.slice(Math.max(0, i - 6), i))) out += `<span class="fn">${w}</span>`;
        else out += w;
        i = j; continue;
      }
      if (/\d/.test(c) && !/\w/.test(src[i - 1] || '')) { let j = i; while (j < src.length && /[\d._]/.test(src[j])) j++; out += `<span class="nu">${src.slice(i, j)}</span>`; i = j; continue; }
      out += e(c); i++;
    }
    return out;
  },
  md(text) {  /* tiny, safe markdown for chat replies: **bold**, `code`, lists, paragraphs */
    const lines = RX.esc(text || '').split('\n');
    let html = '', list = null;
    const inline = (s) => s.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`([^`]+)`/g, '<code>$1</code>').replace(/(^|\s)\*(\S[^*]*?)\*(?=\s|$|[.,])/g, '$1<i>$2</i>');
    for (const raw of lines) {
      const l = raw.trimEnd();
      const m = l.match(/^\s*(?:[-*•]|\d+[.)])\s+(.*)$/);
      if (m) { if (!list) { list = /^\s*\d/.test(l) ? 'ol' : 'ul'; html += `<${list}>`; } html += `<li>${inline(m[1])}</li>`; continue; }
      if (list) { html += `</${list}>`; list = null; }
      if (!l.trim()) continue;
      const h = l.match(/^#{1,4}\s+(.*)$/);
      html += h ? `<p><b>${inline(h[1])}</b></p>` : `<p>${inline(l)}</p>`;
    }
    if (list) html += `</${list}>`;
    return html;
  },
};
window.RX = RX;
})();
