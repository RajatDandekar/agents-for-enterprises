/* Live figures for the primer (L0). Loaded BEFORE plates.js, so helpers are read inside each figure: const P = window.Plates.
   Every number here comes from our executed run of NB0:
     lectures/L0-primer/experiments/logs/primer_numbers.json   (written by lectures/L0-primer/NB0_primer.ipynb)
   Model calls replay from bahi/bahi/cassettes/L0_primer.jsonl. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const inr = (n) => '₹' + Math.round(n).toLocaleString('en-IN');

/* ---- measured numbers (primer_numbers.json) ---- */
const N = {
  env: { rc: 'S', err_cd: null, msg: '', data: { itm_cd: 'GSK-SIL-05L', whs_cd: 'WH-PUN-STR', on_hand: 54000, allocated: 0, on_order: 0, avg_daily_issue: 6000, reorder_lvl: 30000, cover_days: 9 } },
  login: { status: 200, role: 'PUR-EXEC', msg: 'WELCOME, KJOSHI. LAST SIGN-IN 24-10-2026 18:02' },
  noToken: { status: 401, body: { detail: 'ERR-SEC-0010 SESSION EXPIRED, SIGN IN AGAIN' } },
  po01120: { po_no: 'PO/2026/01120', sup_cd: 'DP-RJK-0042', status: 'RL', gross_value: 242136 },
  statusCounts: { RL: 5, PA: 1 },
  releaseErr: { err_cd: 'ERR-PO-0715', msg: 'DOCUMENT NOT IN RELEASABLE STATUS (PA)' },
  closedCC: ['PO/2026/01044', 'PO/2026/01120', 'PO/2026/01131', 'PO/2026/01152'],
  user: { user_id: 'KJOSHI', name: 'Kavita Joshi', role_cd: 'PUR-EXEC', ou_cd: 'RSW-PUN-01', appr_limit: 250000.0, manager_id: 'RMEHTA', default_cc: 'PRD-05' },
  gross: 280840, // NB0 §1: 20000 x 11.90 x 1.18, printed as ₹2,80,840
  calls: [ // [label, model, tokens in, tokens out, seconds, ₹]
    ['what is a PO', 'gemini-3.8-flash', 11, 34, 4.355, 0.0095],
    ['what is a PO (small)', 'gemini-3.5-flash-lite', 11, 33, 0.625, 0.0013],
    ['limit, no fact', 'gemini-3.8-flash', 21, 24, 13.674, 0.0073],
    ['limit, with fact', 'gemini-3.8-flash', 111, 23, 4.957, 0.0110],
    ['stock: tool call', 'gemini-3.8-flash', 135, 40, 3.316, 0.0165],
    ['stock: answer', 'gemini-3.8-flash', 448, 81, 2.671, 0.0411],
    ['ex 5: tool call', 'gemini-3.8-flash', 204, 29, 2.239, 0.0166],
    ['ex 5: answer', 'gemini-3.8-flash', 686, 137, 3.630, 0.0664],
  ],
  totalTokens: 2028, totalInr: 0.1697,
  prices: { 'gemini-3.5-flash-lite': [0.10, 0.40], 'gemini-3.8-flash': [0.50, 3.00], 'gemini-3.1-pro-preview': [2.00, 12.0] },
  usdInr: 88,
  texts: {
    po: 'A purchase order is an official document issued by a buyer to a seller that details the types, quantities, and agreed-upon prices of the goods or services being requested.',
    poSmall: 'A purchase order is a legally binding contract sent by a buyer to a seller detailing the types, quantities, and agreed-upon prices for products or services being ordered.',
    without: "Without the relevant document or context for Rasoi Steel Works, Kavita Joshi's specific approval limit cannot be determined.",
    with: "Kavita Joshi's approval limit at Rasoi Steel Works is 250,000.",
    stock: 'In the Pune store (WH-PUN-STR), the stock details for 5-litre silicone gaskets (GSK-SIL-05L) are as follows: Current Stock (On Hand): 54,000 units · Average Daily Consumption: 6,000 units/day · Stock Cover: 9 days',
  },
  toolCall: { id: 'call_4359638', name: 'stk_query', arguments: { itm_cd: 'GSK-SIL-05L', whs_cd: 'WH-PUN-STR' } },
};

const J = (o, ind = 1) => JSON.stringify(o, null, ind);
const box = (html, style = '') => `<div class="card" style="font-size:20px;${style}">${html}</div>`;
const pre = (s, style = '') => `<pre class="json" style="font-size:18px;line-height:1.45;margin:0;white-space:pre-wrap;${style}">${s}</pre>`;
const show = (el, on) => { el.style.opacity = on ? 1 : 0.12; };

/* ---------- 1. the order this course follows ---------- */
FIGS.order = (el) => {
  const rows = [
    ['The item', 'GSK-SIL-05L · silicone gasket, 5-litre cooker', ''],
    ['In stock', '54,000 on hand · 6,000 a day', '9 days of cover'],
    ['The supplier', 'Deccan Polymers · DP-RJK-0042 · Rajkot, Gujarat', ''],
    ['The order', '20,000 × ₹11.90 + 18% GST', inr(N.gross)],
    ['Her limit', 'Kavita can approve up to', inr(N.user.appr_limit)],
  ];
  el.innerHTML = `<div class="card" style="height:100%;display:flex;flex-direction:column;gap:6px">
    <span class="tag nt" style="align-self:flex-start">Monday 26 October 2026 · Rasoi Steel Works, Pune</span>
    ${rows.map((r, i) => `<div class="or" style="display:grid;grid-template-columns:170px 1fr 170px;gap:12px;align-items:baseline;border-bottom:1px solid var(--rule);padding:12px 0;transition:opacity .4s">
      <span style="font:600 20px var(--mono);color:var(--ink-2);text-transform:uppercase;letter-spacing:.06em;font-size:18px">${r[0]}</span>
      <span style="font-size:22px">${r[1]}</span><span style="font:600 26px var(--display);color:${i === 4 ? 'var(--gold)' : i === 3 ? 'var(--before)' : 'var(--ink)'};text-align:right">${r[2]}</span></div>`).join('')}
    <p class="or" style="font-size:21px;margin:10px 0 0;color:var(--ink-2);transition:opacity .4s">Above her limit, so her manager Rohit must approve. Every lecture returns to this order.</p></div>`;
  const rs = [...el.querySelectorAll('.or')];
  return { step(k) { rs.forEach((r, i) => show(r, i <= k + 1)); } };
};

/* ---------- 2. what the primer gives you ---------- */
FIGS.map = (el) => {
  const L = [['Python, JSON and HTTP', 'on Bahi’s real replies', '§1–2'], ['What an ERP is', 'master data, documents, statuses', '§3'],
    ['A language-model call', 'messages in, text out, tokens, ₹', '§4'], ['Tool calling', 'the model writes JSON, our code runs it', '§5']];
  el.innerHTML = `<div class="stk" style="gap:16px">${L.map((l, i) => `<div class="lyr" style="padding:18px 20px;font-size:25px"><span><b>${i + 1}. ${l[0]}</b><br><span style="font-size:20px;color:var(--ink-2)">${l[1]}</span></span><span class="tg" style="font-size:18px">NB0 ${l[2]}</span></div>`).join('')}
   <div class="lyr leg" style="padding:18px 20px;font-size:23px"><span>Lecture 1: put tool calling in a loop, give it Bahi’s services, and watch Kavita’s order go wrong.</span><span class="tg" style="font-size:18px">Sat 31 Oct</span></div></div>`;
  const ls = [...el.querySelectorAll('.lyr')];
  return { step(k) { ls.forEach((l, i) => { l.classList.toggle('new', i === k && i < 4); show(l, i <= Math.max(k, 0) || k >= 4); }); } };
};

/* ---------- 3. the envelope: JSON text vs Python dict ---------- */
FIGS.envelope = (el) => {
  const asJSON = () => J(N.env, 2);
  const asPy = () => asJSON().replace(/null/g, 'None').replace(/"/g, "'");
  el.innerHTML = `<div class="ctl" style="margin:0 0 12px"><button class="on" data-v="j">JSON text (on the wire)</button><button data-v="p">Python dict (in your code)</button></div>
    <div class="ev"></div><div class="note" style="margin-top:14px;font-size:22px;min-height:70px"></div>`;
  const ev = el.querySelector('.ev'), note = el.querySelector('.note'), bs = [...el.querySelectorAll('button')];
  let mode = 'j', k0 = 0;
  const hl = ['', 'rc', 'err_cd|msg', 'data'];
  const notes = ['The real reply from Bahi’s stock enquiry for the 5-litre gasket.', '<code>rc</code>: S success, W warning, E error.',
    '<code>err_cd</code> and <code>msg</code>: empty here. On an error they hold a code such as ERR-PO-0412 and a terse message.',
    '<code>data</code>: the answer. 54,000 on hand ÷ 6,000 a day = 9 days of cover.'];
  const draw = () => {
    let s = esc(mode === 'j' ? asJSON() : asPy());
    if (hl[k0]) s = s.replace(new RegExp(`(['"])(${hl[k0]})\\1`, 'g'), '<mark style="background:#F1E9D2;color:var(--gold)">$1$2$1</mark>');
    ev.innerHTML = pre(s, 'font-size:20px');
    note.innerHTML = notes[k0];
  };
  bs.forEach((b) => b.addEventListener('click', () => { mode = b.dataset.v; bs.forEach((x) => x.classList.toggle('on', x === b)); draw(); }));
  return { step(k) { k0 = Math.min(k, 3); draw(); } };
};

/* ---------- 4. one HTTP request and its reply ---------- */
FIGS.http = (el) => {
  el.innerHTML = `<div class="ctl" style="margin:0 0 12px"><button class="on" data-t="1">With the token</button><button data-t="0">Without the token</button></div>
   <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">
    <div class="rq">${box('<span class="tag nt">Request</span><div class="rqb"></div>')}</div>
    <div class="rp" style="transition:opacity .4s">${box('<span class="tag nt">Reply</span><div class="rpb"></div>')}</div></div>`;
  const rqb = el.querySelector('.rqb'), rpb = el.querySelector('.rpb'), rp = el.querySelector('.rp'), bs = [...el.querySelectorAll('button')];
  let tok = true;
  const line = (k, v) => `<div style="font:18px/1.5 var(--mono);word-break:break-all"><b>${k}</b> ${v}</div>`;
  const draw = () => {
    rqb.innerHTML = line('POST', '/svc/stk_query') + line('Host', '127.0.0.1:8077') + line('Content-Type:', 'application/json') +
      (tok ? line('Authorization:', 'Bearer A4C1…') : line('Authorization:', '<span style="color:var(--before)">(none)</span>')) +
      `<div style="margin-top:10px">${pre(esc(J({ itm_cd: 'GSK-SIL-05L' }, 0)))}</div>`;
    rpb.innerHTML = tok
      ? `<div style="font:600 24px var(--mono);color:var(--after)">200 OK</div>${line('Content-Type:', 'application/json')}<div style="margin-top:10px">${pre(esc('{"rc": "S", "err_cd": null, "msg": "",\n "data": {"itm_cd": "GSK-SIL-05L",\n  "on_hand": 54000, …,\n  "cover_days": 9}}'))}</div>`
      : `<div style="font:600 24px var(--mono);color:var(--before)">401 Unauthorized</div><div style="margin-top:10px">${pre(esc(J(N.noToken.body, 1)))}</div>`;
  };
  bs.forEach((b) => b.addEventListener('click', () => { tok = b.dataset.t === '1'; bs.forEach((x) => x.classList.toggle('on', x === b)); draw(); }));
  draw();
  return { step(k) { show(rp, k >= 1); } };
};

/* ---------- 5. sign in, then call (sequence) ---------- */
FIGS.seq = (el) => {
  const P = window.Plates, W = 840, H = 560;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const xa = 150, xb = 690;
  [[xa, 'Your code'], [xb, 'Bahi server']].forEach(([x, t]) => {
    P.svgEl('rect', { x: x - 110, y: 10, width: 220, height: 50, style: 'fill:var(--card);stroke:var(--ink);stroke-width:1.5' }, svg);
    P.txt(svg, x, 43, t, 'font:600 22px var(--display);fill:var(--ink)', 'middle');
    P.svgEl('line', { x1: x, x2: x, y1: 60, y2: H - 10, style: 'stroke:var(--rule);stroke-width:2;stroke-dasharray:6 6' }, svg);
  });
  const arrows = [
    [xa, xb, 110, 'POST /login', '{"user_id": "KJOSHI", "password": "…"}', 'var(--ink)'],
    [xb, xa, 200, '200 · token A4C1…', N.login.msg, 'var(--after)'],
    [xa, xb, 310, 'POST /svc/stk_query', 'Authorization: Bearer A4C1… · {"itm_cd": "GSK-SIL-05L"}', 'var(--ink)'],
    [xb, xa, 400, '200 · {rc: "S", data: {on_hand: 54000, …}}', 'Every later call sends the same token', 'var(--after)'],
    [xa, xb, 490, 'no token?', '401 · ERR-SEC-0010 SESSION EXPIRED, SIGN IN AGAIN', 'var(--before)'],
  ];
  const gs = arrows.map(([x1, x2, y, a, b, col]) => {
    const g = P.svgEl('g', { style: 'transition:opacity .4s' }, svg);
    P.svgEl('line', { x1, x2: x2 + (x2 > x1 ? -8 : 8), y1: y, y2: y, style: `stroke:${col};stroke-width:2.5` }, g);
    const d = x2 > x1 ? -1 : 1;
    P.svgEl('path', { d: `M${x2},${y} l${d * 14},-7 l0,14 z`, style: `fill:${col}` }, g);
    P.txt(g, (x1 + x2) / 2, y - 14, a, `font:600 20px var(--mono);fill:${col}`, 'middle');
    P.txt(g, (x1 + x2) / 2, y + 30, b, 'font:18px var(--mono);fill:var(--ink-2)', 'middle');
    return g;
  });
  return { step(k) { gs.forEach((g, i) => (g.style.opacity = i <= k + 1 ? 1 : 0.08)); } };
};

/* ---------- 6. BahiClient ---------- */
FIGS.client = (el) => {
  el.innerHTML = `<div class="code" style="font-size:19px;white-space:pre"><span class="k">from</span> bahi.client <span class="k">import</span> BahiClient

k = BahiClient(url, <span class="s">"KJOSHI"</span>, <span class="s">"kavita@123"</span>)   <span class="c"># signs in once</span>
k.call(<span class="s">"stk_query"</span>, itm_cd=<span class="s">"GSK-SIL-05L"</span>)
k.call(<span class="s">"po_get"</span>, po_no=<span class="s">"PO/2026/01120"</span>)</div>
  <div class="o1" style="margin-top:16px;transition:opacity .4s">${pre(esc(`<BahiClient KJOSHI (PUR-EXEC) at http://127.0.0.1:8077>\n{'rc': 'S', 'data': {'on_hand': 54000, 'cover_days': 9, …}}`))}</div>
  <div class="o2" style="margin-top:12px;transition:opacity .4s">${pre(esc(`${N.po01120.po_no} · ${N.po01120.sup_cd} · status ${N.po01120.status} · gross ${inr(N.po01120.gross_value)}`))}
   <p style="font-size:20px;margin:8px 0 0;color:var(--ink-2)">Exercise 2 in NB0: Kavita’s last gasket order, read over HTTP.</p></div>`;
  const o1 = el.querySelector('.o1'), o2 = el.querySelector('.o2');
  return { step(k) { show(o1, k >= 1); show(o2, k >= 2); } };
};

/* ---------- 7. master data and documents ---------- */
FIGS.tables = (el) => {
  const tbl = (title, tag, cols, rows, cls) => `<div class="card ${cls}" style="padding:12px 16px"><span class="tag ${tag}">${title}</span>
    <table class="t" style="font-size:18px"><tr>${cols.map((c) => `<th>${c}</th>`).join('')}</tr>${rows.map((r) => `<tr>${r.map((c) => `<td class="n" style="font-size:18px">${c}</td>`).join('')}</tr>`).join('')}</table></div>`;
  el.innerHTML = `<div style="display:grid;grid-template-columns:1fr;gap:12px">
    <div class="t1">${tbl('Master data · item', 'nt', ['itm_cd', 'descr', 'food'], [['GSK-SIL-05L', 'Gasket, silicone, 5 L', '1'], ['GSK-SIL-05L-R', '… 5 L (rework)', '1'], ['WHS-STD-01', 'Whistle, standard', '0']], '')}</div>
    <div class="t2">${tbl('Master data · supplier', 'nt', ['sup_cd', 'name', 'status'], [['DP-RJK-0042', 'Deccan Polymers', 'ACTIVE'], ['SV-PUN-0017', 'Sahyadri Valves', 'ACTIVE']], '')}</div>
    <div class="t3">${tbl('Document · purchase order (po_hdr + po_line)', 'bf', ['po_no', 'sup_cd', 'itm_cd', 'qty', 'gross', 'status'],
      [['PO/2026/01120', 'DP-RJK-0042', 'GSK-SIL-05L', '18,000', '2,42,136', 'RL'], ['PO/2026/01179', 'OSM-PUN-0031', 'LID-SS-05L', '4,000', '4,53,120', 'PA']], 'bf')}</div>
    <div class="t4" style="font-size:21px;color:var(--ink-2)">The order does not copy the supplier’s name or the item’s description. It points at them by <b class="g">code</b>. Change the supplier record and every order sees it. <i>(Rows as NB0 prints them.)</i></div></div>`;
  const ts = ['.t1', '.t2', '.t3', '.t4'].map((q) => el.querySelector(q));
  ts.forEach((t) => (t.style.transition = 'opacity .4s'));
  return { step(k) { ts.forEach((t, i) => show(t, i <= k)); } };
};

/* ---------- 8. codes that trip people up ---------- */
FIGS.codes = (el) => {
  const sup = [['DP-RJK-0042', 'Deccan Polymers', 'Rajkot', 'GJ', 'ACTIVE', 'a'], ['DP-RJK-0009', 'Deccan Polymers (old code, do not use)', 'Rajkot', 'GJ', 'BLOCKED', 'a'],
    ['DPI-AMD-0107', 'Deccan Paints & Inks', 'Ahmedabad', 'GJ', 'ACTIVE', 'b'], ['SV-PUN-0017', 'Sahyadri Valves', 'Pune', 'MH', 'ACTIVE', ''], ['KR-KOL-0063', 'Kaveri Rubber Products', 'Kolkata', 'WB', 'ACTIVE', '']];
  const cc = [['PRD-05', '5-litre line, regular production', 'CLOSED', '2026-10-15', 'c'], ['PRD-07', 'Diwali production run', 'OPEN', '', ''], ['PRD-03', '3-litre line', 'OPEN', '', '']];
  el.innerHTML = `<div class="card" style="padding:12px 16px"><span class="tag nt">supplier (5 of 8 rows)</span><table class="t" style="font-size:18px">
    ${sup.map((r) => `<tr data-g="${r[5]}" style="transition:background .3s"><td class="n" style="font-size:18px">${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td class="n" style="font-size:18px">${r[3]}</td><td class="n" style="font-size:18px">${r[4]}</td></tr>`).join('')}</table></div>
    <div class="card" style="padding:12px 16px;margin-top:14px"><span class="tag nt">cost_centre (3 of 5 rows)</span><table class="t" style="font-size:18px">
    ${cc.map((r) => `<tr data-g="${r[4]}" style="transition:background .3s"><td class="n" style="font-size:18px">${r[0]}</td><td>${r[1]}</td><td class="n" style="font-size:18px">${r[2]}</td><td class="n" style="font-size:18px">${r[3]}</td></tr>`).join('')}</table></div>
    <div class="ctl"><button data-g="a">Two Deccans</button><button data-g="b">A near-match</button><button data-g="c">A closed cost centre</button></div>`;
  const trs = [...el.querySelectorAll('tr[data-g]')], bs = [...el.querySelectorAll('button')];
  const set = (g) => { trs.forEach((t) => (t.style.background = g && t.dataset.g === g ? '#F1E9D2' : 'transparent')); bs.forEach((b) => b.classList.toggle('on', b.dataset.g === g)); };
  bs.forEach((b) => b.addEventListener('click', () => set(b.dataset.g)));
  return { step(k) { set(['', 'a', 'b', 'c'][Math.min(k, 3)]); } };
};

/* ---------- 9. document statuses ---------- */
FIGS.life = (el) => {
  const P = window.Plates, W = 860, H = 430;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const S = {
    DR: [90, 120, 'Draft', 'Saved, not sent to anyone. Nothing happens to a Draft unless someone moves it.'],
    PA: [300, 120, 'Pending approval', 'Waiting for an approver whose limit covers the gross value.'],
    AP: [510, 120, 'Approved', 'Approved, but the supplier still has nothing.'],
    RL: [730, 120, 'Released', 'Sent to the supplier. The only status that means the order is placed.'],
    RJ: [300, 330, 'Rejected', 'The approver said no. The end.'],
    CN: [620, 330, 'Cancelled', 'Withdrawn. The end.'],
    CL: [90, 330, 'Closed', 'A purchase request that has been turned into an order.'],
  };
  const edges = [['DR', 'PA', 1], ['PA', 'AP', 2], ['AP', 'RL', 3], ['DR', 'AP', 2], ['PA', 'RJ', 4], ['AP', 'CN', 4], ['RL', 'CN', 4], ['DR', 'CL', 4]];
  const eg = edges.map(([a, b, s]) => {
    const [x1, y1] = S[a], [x2, y2] = S[b];
    const g = P.svgEl('g', { style: 'transition:opacity .4s' }, svg);
    const curve = a === 'DR' && b === 'AP';
    const pth = curve ? `M${x1},${y1 - 44} C${x1 + 100},${y1 - 120} ${x2 - 100},${y2 - 120} ${x2},${y2 - 44}` : `M${x1 + (x2 > x1 ? 62 : 0)},${y1 + (y2 > y1 ? 42 : 0)} L${x2 - (x2 > x1 && y1 === y2 ? 62 : 0)},${y2 - (y2 > y1 ? 42 : 0)}`;
    P.svgEl('path', { d: pth, style: 'fill:none;stroke:var(--ink-2);stroke-width:2', 'marker-end': 'url(#arr)' }, g);
    return [g, s];
  });
  const defs = P.svgEl('defs', {}, svg);
  const mk = P.svgEl('marker', { id: 'arr', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 8, markerHeight: 8, orient: 'auto' }, defs);
  P.svgEl('path', { d: 'M0,0 L10,5 L0,10 z', style: 'fill:var(--ink-2)' }, mk);
  const step = { DR: 0, PA: 1, AP: 2, RL: 3, RJ: 4, CN: 4, CL: 4 };
  const ng = Object.entries(S).map(([code, [x, y, name]]) => {
    const g = P.svgEl('g', { style: 'cursor:pointer;transition:opacity .4s' }, svg);
    const col = code === 'RL' ? 'var(--after)' : code === 'DR' ? 'var(--before)' : 'var(--ink)';
    const r = P.svgEl('rect', { x: x - 62, y: y - 42, width: 124, height: 84, rx: 6, style: `fill:var(--card);stroke:${col};stroke-width:2.5` }, g);
    P.txt(g, x, y + 2, code, `font:600 30px var(--mono);fill:${col}`, 'middle');
    P.txt(g, x, y + 30, name, 'font:18px var(--serif);fill:var(--ink-2)', 'middle');
    if (N.statusCounts[code]) P.txt(g, x + 58, y - 50, `${N.statusCounts[code]} in seed`, 'font:600 18px var(--mono);fill:var(--gold)', 'end');
    g.addEventListener('click', () => { cap.innerHTML = `<b>${code} · ${name}.</b> ${S[code][3]}`; ng.forEach(([rr]) => (rr.style.strokeWidth = 2.5)); r.style.strokeWidth = 5; });
    return [r, g, step[code]];
  });
  const cap = document.createElement('div'); cap.style.cssText = 'font-size:22px;min-height:66px;margin-top:6px';
  el.appendChild(cap);
  return { step(k) { ng.forEach(([, g, s]) => (g.style.opacity = s <= k ? 1 : 0.1)); eg.forEach(([g, s]) => (g.style.opacity = s <= k ? 1 : 0.1)); const c = ['DR', 'PA', 'AP', 'RL', 'CN'][Math.min(k, 4)]; cap.innerHTML = `<b>${c} · ${S[c][2]}.</b> ${S[c][3]}`; } };
};

/* ---------- 10. the rules live in the services ---------- */
FIGS.release = (el) => {
  el.innerHTML = `<div class="r1" style="transition:opacity .4s">${box(`<span class="tag nt">Kavita tries to release an order still waiting for approval</span>
     ${pre(esc('kavita.call("po_release", po_no="PO/2026/01179")'))}
     <div style="margin-top:10px">${pre(esc(J({ rc: 'E', err_cd: N.releaseErr.err_cd, msg: N.releaseErr.msg, data: null }, 1)), 'border-color:var(--before)')}</div>`)}</div>
    <div class="r2" style="margin-top:16px;transition:opacity .4s">${box(`<span class="tag bf">Orders charged to PRD-05, which is now closed</span>
     <div style="font:19px/1.6 var(--mono)">${N.closedCC.map((p) => `${p} · RL`).join('<br>')}</div>
     <p style="font-size:21px;margin:8px 0 0">All four were placed before PRD-05 closed on 15 October. What happens to a <i>new</i> order on PRD-05? Bahi does not refuse it. Lecture 1 shows what it does.</p>`)}</div>`;
  const r1 = el.querySelector('.r1'), r2 = el.querySelector('.r2');
  return { step(k) { show(r1, k >= 0); show(r2, k >= 1); } };
};

/* ---------- 11. one model call ---------- */
FIGS.call = (el) => {
  const c = N.calls[0];
  el.innerHTML = `<div style="display:grid;grid-template-columns:1fr 150px 1fr;gap:18px;align-items:center">
    <div class="c1">${box(`<span class="tag nt">Messages in</span>${pre(esc(J([{ role: 'user', content: 'In one sentence, what is a purchase order?' }], 1)))}`)}</div>
    <div class="c2" style="text-align:center;transition:opacity .4s"><div style="background:var(--ink);color:var(--paper);font:600 26px var(--display);padding:30px 8px">Model</div><div style="font:18px var(--mono);color:var(--ink-2);margin-top:8px">${c[1]}</div></div>
    <div class="c3" style="transition:opacity .4s">${box(`<span class="tag af">Text out</span><div style="font-size:21px">${esc(N.texts.po)}</div>`)}</div></div>
   <div class="c4 meters" style="transition:opacity .4s;margin-top:26px;grid-template-columns:repeat(4,1fr)">
    ${[[c[2], 'tokens in'], [c[3], 'tokens out'], [c[4] + ' s', 'seconds'], ['₹' + c[5], 'cost']].map(([v, k]) => `<div class="meter" style="border-color:var(--after)"><div class="v" style="color:var(--after)">${v}</div><div class="k" style="font-size:18px">${k}</div></div>`).join('')}</div>`;
  const cs = ['.c1', '.c2', '.c3', '.c4'].map((q) => el.querySelector(q));
  return { step(k) { cs.forEach((x, i) => show(x, i <= k)); } };
};

/* ---------- 12. tokens to rupees: a calculator ---------- */
FIGS.tokens = (el) => {
  el.innerHTML = `<div class="ctl" style="margin:0 0 8px"><span>Model</span>${Object.keys(N.prices).map((m, i) => `<button data-m="${m}" class="${i === 1 ? 'on' : ''}">${m}</button>`).join('')}</div>
    <div class="ctl" style="margin:0"><span>Our calls</span>${N.calls.map((c, i) => `<button data-c="${i}">${c[0]}</button>`).join('')}</div>
    <div class="ctl"><label for="tki" style="width:120px">Tokens in</label><input id="tki" type="range" min="0" max="200000" step="1" value="11"><output class="oi"></output></div>
    <div class="ctl"><label for="tko" style="width:120px">Tokens out</label><input id="tko" type="range" min="0" max="5000" step="1" value="34"><output class="oo"></output></div>
    <div class="fx card" style="margin-top:16px;font:21px/1.6 var(--mono)"></div>
    <div class="big" style="font:600 64px var(--display);color:var(--after);margin-top:8px"></div>`;
  const ii = el.querySelector('#tki'), io = el.querySelector('#tko'), fx = el.querySelector('.fx'), big = el.querySelector('.big');
  const mb = [...el.querySelectorAll('[data-m]')], cb = [...el.querySelectorAll('[data-c]')];
  let m = 'gemini-3.8-flash', showFx = false;
  const draw = () => {
    const [pi, po] = N.prices[m], ti = +ii.value, to = +io.value, usd = (ti * pi + to * po) / 1e6, inrv = usd * N.usdInr;
    el.querySelector('.oi').textContent = ti.toLocaleString('en-IN'); el.querySelector('.oo').textContent = to.toLocaleString('en-IN');
    fx.innerHTML = showFx ? `(${ti.toLocaleString('en-IN')} × $${pi} + ${to.toLocaleString('en-IN')} × $${po}) ÷ 10,00,000<br>= $${usd.toFixed(6)} × ₹${N.usdInr} per dollar` : 'Pick one of our calls, or drag the sliders.';
    big.textContent = '₹' + (inrv < 1 ? inrv.toFixed(4) : inrv.toLocaleString('en-IN', { maximumFractionDigits: 2 }));
  };
  mb.forEach((b) => b.addEventListener('click', () => { m = b.dataset.m; mb.forEach((x) => x.classList.toggle('on', x === b)); draw(); }));
  cb.forEach((b) => b.addEventListener('click', () => { const c = N.calls[+b.dataset.c]; ii.value = c[2]; io.value = c[3]; m = c[1]; mb.forEach((x) => x.classList.toggle('on', x.dataset.m === m)); cb.forEach((x) => x.classList.toggle('on', x === b)); draw(); }));
  [ii, io].forEach((x) => x.addEventListener('input', draw));
  draw();
  return { step(k) { showFx = k >= 1; if (k >= 2) { ii.value = 100000; io.value = 1000; } else { ii.value = 11; io.value = 34; } draw(); } };
};

/* ---------- 13. two tiers, one question ---------- */
FIGS.tiers = (el) => {
  const d = N.calls[0], s = N.calls[1];
  const rows = [['seconds', d[4], s[4], (v) => v + ' s'], ['₹ per call', d[5], s[5], (v) => '₹' + v], ['tokens (in + out)', d[2] + d[3], s[2] + s[3], (v) => v]];
  el.innerHTML = `<div class="cmp">${rows.map((r) => `<div class="row tr" style="transition:opacity .4s"><div class="lab">${r[0]}</div><div class="br">
     <div class="bar a" style="width:${Math.max(4, 560 * r[1] / Math.max(r[1], r[2]))}px">${r[3](r[1])} · default</div>
     <div class="bar" style="background:var(--gold);width:${Math.max(4, 560 * r[2] / Math.max(r[1], r[2]))}px">${r[3](r[2])} · small</div></div></div>`).join('')}</div>
    <div class="tx" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:22px;transition:opacity .4s">
     ${box(`<span class="tag af">gemini-3.8-flash (default)</span><div style="font-size:19px">${esc(N.texts.po)}</div>`)}
     ${box(`<span class="tag nt">gemini-3.5-flash-lite (small)</span><div style="font-size:19px">${esc(N.texts.poSmall)}</div>`)}</div>`;
  const trs = [...el.querySelectorAll('.tr')], tx = el.querySelector('.tx');
  return { step(k) { trs.forEach((t, i) => show(t, i <= k)); show(tx, k >= 2); } };
};

/* ---------- 14. the context is all it sees ---------- */
FIGS.context = (el) => {
  el.innerHTML = `<div class="ctl" style="margin:0 0 12px"><button class="on" data-w="0">Without the fact</button><button data-w="1">With Bahi’s record</button></div><div class="cx"></div>`;
  const cx = el.querySelector('.cx'), bs = [...el.querySelectorAll('button')];
  const draw = (w) => {
    const msgs = (w ? [{ role: 'system', content: 'Bahi ERP user record: ' + JSON.stringify(N.user) }] : []).concat([{ role: 'user', content: "What is Kavita Joshi's approval limit at Rasoi Steel Works? Answer in one sentence." }]);
    const c = N.calls[w ? 3 : 2];
    cx.innerHTML = `${box(`<span class="tag nt">Messages in · ${c[2]} tokens</span>${pre(esc(J(msgs, 1)), 'font-size:18px')}`)}
      <div style="margin-top:14px">${box(`<span class="tag ${w ? 'af' : 'bf'}">Text out</span><div style="font-size:23px">${esc(w ? N.texts.with : N.texts.without)}</div>`)}</div>`;
    bs.forEach((b) => b.classList.toggle('on', +b.dataset.w === w));
  };
  bs.forEach((b) => b.addEventListener('click', () => draw(+b.dataset.w)));
  return { step(k) { draw(k >= 1 ? 1 : 0); } };
};

/* ---------- 15. tool calling, step by step ---------- */
FIGS.toolcall = (el) => {
  const st = [
    ['1 · Kavita asks', 'nt', `<div style="font-size:21px">How many 5-litre silicone gaskets (GSK-SIL-05L) do we have in the Pune store, and how many days will they last?</div>`],
    ['2 · The model writes a tool call (and stops)', 'af', pre(esc(J({ id: N.toolCall.id, name: N.toolCall.name, arguments: N.toolCall.arguments }, 0))) + `<div style="font:18px var(--mono);color:var(--ink-2);margin-top:4px">${N.calls[4][2]} tokens in · ${N.calls[4][3]} out · ₹${N.calls[4][5]}</div>`],
    ['3 · Our code runs it, as Kavita', 'bf', pre(esc('kavita.call("stk_query", itm_cd="GSK-SIL-05L", whs_cd="WH-PUN-STR")'))],
    ['4 · The result goes back as a tool message', 'nt', pre(esc('{"role": "tool", "tool_call_id": "' + N.toolCall.id + '",\n "content": "{\\"rc\\": \\"S\\", ... \\"on_hand\\": 54000, ... \\"cover_days\\": 9}"}'))],
    ['5 · The model answers', 'af', `<div style="font-size:20px">${esc(N.texts.stock)}</div><div style="font:18px var(--mono);color:var(--ink-2);margin-top:4px">${N.calls[5][2]} tokens in · ${N.calls[5][3]} out · ₹${N.calls[5][5]}</div>`],
  ];
  el.innerHTML = `<div style="display:flex;flex-direction:column;gap:10px">${st.map((s) => `<div class="tc card" style="padding:10px 16px;transition:opacity .4s"><span class="tag ${s[1]}" style="margin-bottom:6px">${s[0]}</span>${s[2]}</div>`).join('')}</div>`;
  const cs = [...el.querySelectorAll('.tc')];
  return { step(k) { cs.forEach((c, i) => show(c, i <= k)); } };
};

/* ---------- 16. a tool is a schema ---------- */
FIGS.schema = (el) => {
  const parts = [
    ['"name": "stk_query"', 'The name the model writes in its tool call.'],
    ['"description": "Stock of one item in one warehouse (default Pune main stores)."', 'One sentence the model reads to decide when to use it.'],
    ['"itm_cd": {"type": "string", "description": "Item code, e.g. GSK-SIL-05L"}', 'Each field, with a type and a hint.'],
    ['"required": ["itm_cd"]', 'What it must always send.'],
  ];
  el.innerHTML = parts.map((p, i) => `<div class="sp" style="display:grid;grid-template-columns:1fr 290px;gap:16px;align-items:center;margin-bottom:12px;transition:opacity .4s">
     ${pre(esc(p[0]), 'font-size:19px')}<div style="font-size:21px">${p[1]}</div></div>`).join('') +
    `<p class="sp" style="font-size:21px;margin-top:12px;transition:opacity .4s">That is all a tool is to the model: a name, a sentence and a list of fields. It never sees the code behind it. In Lecture 1 we hand it Bahi’s services exactly as Bahi describes them, terse codes and all.</p>`;
  const sp = [...el.querySelectorAll('.sp')];
  return { step(k) { sp.forEach((s, i) => show(s, i <= k + 1)); } };
};

/* ---------- 17. the loop ---------- */
FIGS.loop = (el) => {
  const P = window.Plates, W = 780, H = 560, cx = 390, cy = 270, R = 190;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const nodes = [['Model', 'reads all messages'], ['Tool call', 'JSON: name + arguments'], ['Our code', 'runs it on Bahi'], ['Result', 'appended as a tool message']];
  const pos = nodes.map((_, i) => { const a = -Math.PI / 2 + i * Math.PI / 2; return [cx + R * Math.cos(a), cy + R * Math.sin(a)]; });
  const arcs = pos.map(([x1, y1], i) => {
    const [x2, y2] = pos[(i + 1) % 4];
    const mx = (x1 + x2) / 2 + (x1 + x2 - 2 * cx) * 0.35, my = (y1 + y2) / 2 + (y1 + y2 - 2 * cy) * 0.35;
    return P.svgEl('path', { d: `M${x1},${y1} Q${mx},${my} ${x2},${y2}`, style: 'fill:none;stroke:var(--rule);stroke-width:4;transition:stroke .3s' }, svg);
  });
  const gs = nodes.map(([a, b], i) => {
    const [x, y] = pos[i], g = P.svgEl('g', {}, svg);
    const r = P.svgEl('rect', { x: x - 120, y: y - 40, width: 240, height: 80, rx: 6, style: 'fill:var(--card);stroke:var(--ink);stroke-width:2;transition:fill .3s' }, g);
    P.txt(g, x, y - 4, a, 'font:600 25px var(--display);fill:var(--ink)', 'middle');
    P.txt(g, x, y + 24, b, 'font:18px var(--serif);fill:var(--ink-2)', 'middle');
    return r;
  });
  const stop = P.txt(svg, cx, cy + 8, 'no tool call → answer', 'font:italic 22px var(--display);fill:var(--after);transition:opacity .4s', 'middle');
  let t = 0, timer = null;
  const tick = () => { gs.forEach((r, i) => (r.style.fill = i === t % 4 ? 'var(--after-soft)' : 'var(--card)')); arcs.forEach((a, i) => (a.style.stroke = i === t % 4 ? 'var(--after)' : 'var(--rule)')); t++; };
  return { step(k) { clearInterval(timer); stop.style.opacity = k >= 1 ? 1 : 0; if (k >= 2 && !window.Plates.reduced) { timer = setInterval(tick, 900); } else { t = Math.min(k, 3); tick(); } } };
};

/* ---------- 18. what the primer cost ---------- */
FIGS.cost = (el) => {
  const max = Math.max(...N.calls.map((c) => c[5]));
  el.innerHTML = `<div class="cmp" style="gap:10px">${N.calls.map((c) => `<div class="row cr" style="grid-template-columns:260px 1fr;transition:opacity .4s"><div class="lab" style="font-size:20px">${c[0]}</div><div class="br">
    <div class="bar ${c[1].includes('lite') ? '' : 'a'}" style="${c[1].includes('lite') ? 'background:var(--gold);' : ''}width:${Math.max(70, 470 * c[5] / max)}px">₹${c[5]} · ${c[2] + c[3]} tok</div></div></div>`).join('')}</div>
    <p class="tot" style="font-size:24px;margin-top:18px;transition:opacity .4s">Eight calls, <b>${N.totalTokens.toLocaleString('en-IN')} tokens</b>, <b class="a">₹${N.totalInr}</b> in all. An agent makes many calls per request, and each one re-sends the whole conversation.</p>`;
  const rs = [...el.querySelectorAll('.cr')], tot = el.querySelector('.tot');
  return { step(k) { rs.forEach((r) => show(r, true)); show(tot, k >= 1); } };
};

/* ---------- 19. set-up checklist ---------- */
FIGS.setup = (el) => {
  const items = [
    ['Open NB0 in Colab and run all cells.', 'Replay mode is the default: no key needed. Recorded calls play back with their real tokens and seconds.'],
    ['Find the legacy-client link it prints.', 'In Colab, serve() prints a proxied link to Bahi’s Windows-style client. Lecture 1 uses it.'],
    ['Optional: a Gemini key.', 'Set GEMINI_API_KEY in the setup cell to call models live. Everything we recorded used Gemini.'],
    ['Optional: an OpenRouter key.', 'Lets you try GPT, Claude or Llama through the same client. We did not run those; no numbers on our plates come from them.'],
    ['Pick a task from your own work.', 'One job that takes several screens of an enterprise system. You will need it for assignment A1.'],
  ];
  el.innerHTML = items.map((it, i) => `<label class="ck card" style="display:grid;grid-template-columns:40px 1fr;gap:10px;margin-bottom:12px;cursor:pointer;transition:opacity .4s">
    <input type="checkbox" style="width:26px;height:26px;accent-color:var(--after);margin-top:4px"><span><b style="font-size:23px">${it[0]}</b><br><span style="font-size:20px;color:var(--ink-2)">${it[1]}</span></span></label>`).join('');
  const cs = [...el.querySelectorAll('.ck')];
  return { step() { cs.forEach((c) => show(c, true)); } };
};
})();
