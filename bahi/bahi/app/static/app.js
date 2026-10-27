/* Shared helpers for the four pages: sign-in (Bahi's own /login), the Bearer token, fetch wrappers, header. */
const H = (() => {
  const qs = new URLSearchParams(location.hash.slice(1));
  const key = (who) => `bahi-l5-token-${who}`;
  const esc = (s) => String(s ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const inr = (n) => n == null ? '-' : '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 2 });
  function token(who) { const t = qs.get('token'); if (t) return t; try { return sessionStorage.getItem(key(who)); } catch (e) { return null; } }
  function save(who, t) { try { sessionStorage.setItem(key(who), t); } catch (e) {} }
  async function api(path, opts = {}, who) {
    const t = token(who);
    const r = await fetch(path, { ...opts, headers: { 'Content-Type': 'application/json', ...(t ? { Authorization: 'Bearer ' + t } : {}), ...(opts.headers || {}) } });
    const body = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(body.detail || body.msg || r.status);
    return body;
  }
  function header(page, me) {
    const pages = [['chat', 'Chat'], ['inbox', 'Inbox'], ['slack', 'Slack'], ['audit', 'Audit']];
    document.body.insertAdjacentHTML('afterbegin', `<header><h1>Bahi · ${esc(page[1])}</h1><nav>${pages.map(([p, l]) =>
      `<a href="/app/${p}" class="${p === page[0] ? 'on' : ''}">${l}</a>`).join('')}</nav>
      <div class="who">${me ? `${esc(me.name)} (${esc(me.user)}) · ${esc(me.role)}<br>limit ${inr(me.limit)} · acts as you` : 'not signed in'}</div></header>`);
  }
  function signin(el, who, user, pw, done) {
    el.innerHTML = `<div class="signin"><h2>Sign in to Bahi</h2><p class="note">The agent will act with this sign-in and nothing more.</p>
      <label>User</label><input id="u" value="${user}"><label>Password</label><input id="p" type="password" value="${pw}">
      <p style="margin-top:14px"><button class="go" id="go">Sign in</button> <span class="err" id="e"></span></p></div>`;
    el.querySelector('#go').onclick = async () => {
      const r = await fetch('/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: el.querySelector('#u').value, password: el.querySelector('#p').value }) });
      const b = await r.json();
      if (!r.ok) { el.querySelector('#e').textContent = b.msg || 'refused'; return; }
      save(who, b.token); done();
    };
  }
  return { qs, esc, inr, token, api, header, signin };
})();
