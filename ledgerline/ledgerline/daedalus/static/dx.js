/* Daedalus: small shared helpers (the workshop key, API calls, escaping, JSON colouring, toast, copy). */
(() => {
'use strict';
const KEY = 'dx_key';
const store = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } },
  del(k) { try { localStorage.removeItem(k); } catch (e) { /* private mode */ } },
};
let memKey = '';
const HX = {
  key() { return memKey || store.get(KEY) || ''; },
  setKey(k) { memKey = k; store.set(KEY, k); },
  forget() { memKey = ''; store.del(KEY); },
  async api(path, body, method) {
    const h = { 'Content-Type': 'application/json' };
    const k = HX.key(); if (k) h['X-Workshop-Key'] = k;
    const r = await fetch(path, { method: method || (body === undefined ? 'GET' : 'POST'), headers: h,
      body: body === undefined ? undefined : JSON.stringify(body) });
    let d = null; try { d = await r.json(); } catch (e) { d = {}; }
    if (!r.ok) { const err = new Error((d && d.detail) || ('HTTP ' + r.status)); err.status = r.status; throw err; }
    return d;
  },
  async poll(jid, onTick, ms) {
    for (;;) {
      const j = await HX.api('/api/job/' + jid);
      if (onTick) onTick(j);
      if (j.state !== 'running') return j;
      await new Promise((res) => setTimeout(res, ms || 1200));
    }
  },
  esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); },
  num(n) { return n == null ? '–' : new Intl.NumberFormat('en-GB').format(n); },
  usd(n) { return n == null ? '–' : (n < 0.01 ? '$' + n.toFixed(4) : '$' + n.toFixed(3)); },
  json(v, max) {
    let s = typeof v === 'string' ? v : JSON.stringify(v, null, 2);
    try { if (typeof v === 'string') s = JSON.stringify(JSON.parse(v), null, 2); } catch (e) { /* not JSON */ }
    if (max && s.length > max) s = s.slice(0, max) + '\n… (' + HX.num(s.length - max) + ' more characters)';
    return HX.esc(s)
      .replace(/(&quot;[^&]*?&quot;)(\s*:)/g, '<span class="k">$1</span>$2')
      .replace(/: (&quot;.*?&quot;)/g, ': <span class="s">$1</span>')
      .replace(/: (-?\d[\d.e+-]*)/g, ': <span class="n">$1</span>')
      .replace(/: (true|false)/g, ': <span class="b">$1</span>')
      .replace(/: (null)/g, ': <span class="z">$1</span>');
  },
  toast(msg, ms) {
    let t = document.querySelector('.toast'); if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.append(t); }
    t.textContent = msg; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), ms || 3200);
  },
  async copy(text, what) {
    try { await navigator.clipboard.writeText(text); HX.toast((what || 'Copied') + ' ✓'); }
    catch (e) { const ta = document.createElement('textarea'); ta.value = text; document.body.append(ta); ta.select();
      try { document.execCommand('copy'); HX.toast((what || 'Copied') + ' ✓'); } catch (e2) { HX.toast('Copy failed: select it by hand'); } ta.remove(); }
  },
  ago(t) { const s = Math.max(0, Date.now() / 1000 - t); return s < 60 ? Math.round(s) + ' s ago' : s < 3600 ? Math.round(s / 60) + ' min ago' : Math.round(s / 3600) + ' h ago'; },
  time(t) { return new Date(t * 1000).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }); },
};
window.DX = HX;
})();
