/* Live figures for Lecture 6 · The Studio. Loaded BEFORE plates.js; helpers come from window.Plates at mount time.
   Every number, status and transcript comes from window.L6 (figdata.js), which experiments/export_figdata.py copies
   from experiments/logs/*.json: probe.json, templates_fresh.json, wf_vs_agent.json, retry_idem.json. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const D = () => window.L6 || {};
const P = () => window.Plates;
const esc = (s) => String(s == null ? '' : s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const inr = (x) => '₹' + Number(x).toLocaleString('en-IN', { maximumFractionDigits: 2 });
const num = (x) => Number(x).toLocaleString('en-IN');
const short = (s, n) => { s = String(s == null ? '' : s); return s.length > n ? s.slice(0, n - 1) + '…' : s; };
const ctl = (el, html) => { const d = document.createElement('div'); d.className = 'ctl'; d.innerHTML = html; el.appendChild(d); return d; };
const onClick = (c, sel, fn) => c.addEventListener('click', (e) => { const b = e.target.closest(sel); if (b) fn(b); });
const STATUS = { done: 'var(--after)', warning: 'var(--gold)', error: 'var(--before)', waiting: 'var(--before)', skipped: 'var(--ink-3)', pending: 'var(--ink-3)', signed: 'var(--gold)' };
const TYPE_LABEL = { trigger: 'Trigger', tool: 'Tool', condition: 'Condition', approval: 'Approval', llm: 'LLM', agent: 'Agent', message: 'Message', set: 'Set' };

/* A workflow drawn as cards on a small canvas, from its real JSON (x, y positions from the template). */
function drawFlow(el, tpl, opts = {}) {
  const W = opts.W || 1400, H = opts.H || 330, E = P().svgEl, T = P().txt;
  const xs = tpl.nodes.map((n) => n.x), ys = tpl.nodes.map((n) => n.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const bw = opts.bw || 158, bh = 64;
  const sx = (x) => 20 + (x1 === x0 ? 0 : (x - x0) / (x1 - x0)) * (W - bw - 40);
  const sy = (y) => (y1 === y0 ? H / 2 - bh / 2 : 30 + (y - y0) / (y1 - y0) * (H - bh - 60));
  const svg = E('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', height: H * (opts.scale || 1) }, el);
  const defs = E('defs', {}, svg);
  const mk = E('marker', { id: 'ah' + opts.id, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' }, defs);
  E('path', { d: 'M0,0 L10,5 L0,10 z', style: 'fill:var(--ink-3)' }, mk);
  const pos = {};
  tpl.nodes.forEach((n) => (pos[n.id] = { x: sx(n.x), y: sy(n.y) }));
  const edges = tpl.edges.map((e) => {
    const a = pos[e.from], b = pos[e.to];
    const xa = a.x + bw, ya = a.y + bh / 2, xb = b.x, yb = b.y + bh / 2, mx = (xa + xb) / 2;
    const p = E('path', { d: `M${xa},${ya} C${mx},${ya} ${mx},${yb} ${xb - 2},${yb}`, style: 'fill:none;stroke:var(--ink-3);stroke-width:2', 'marker-end': `url(#ah${opts.id})` }, svg);
    const lab = e.port && e.port !== 'out' ? T(svg, xb - 14, yb - 10, e.port, 'font:500 14px var(--mono);fill:var(--ink-3)', 'end') : null;
    return { e, p, lab };
  });
  const cards = {};
  tpl.nodes.forEach((n) => {
    const { x, y } = pos[n.id];
    const g = E('g', {}, svg);
    const r = E('rect', { x, y, width: bw, height: bh, rx: 14, style: 'fill:#fff;stroke:var(--rule);stroke-width:1.5;transition:all .35s' }, g);
    T(g, x + 12, y + 22, (TYPE_LABEL[n.type] || n.type).toUpperCase(), 'font:600 13px var(--font);letter-spacing:.06em;fill:var(--ink-3)');
    const t = T(g, x + 12, y + 47, short(n.title, Math.floor(bw / 9.4)), 'font:500 16px var(--font);fill:var(--ink)');
    const dot = E('circle', { cx: x + bw - 16, cy: y + 18, r: 6, style: 'fill:var(--rule);transition:fill .35s' }, g);
    cards[n.id] = { g, r, t, dot, x, y };
  });
  return {
    svg, cards, edges, pos, bw, bh,
    paint(status = {}, taken = null) {
      Object.entries(cards).forEach(([id, c]) => {
        const s = status[id];
        const col = STATUS[s] || 'var(--rule)';
        c.dot.style.fill = s ? col : 'var(--rule)';
        c.r.style.stroke = s && s !== 'skipped' ? col : 'var(--rule)';
        c.r.style.fill = s === 'waiting' ? 'var(--before-soft)' : s === 'done' ? 'var(--after-soft)' : s === 'error' ? 'var(--before-soft)' : '#fff';
        c.g.style.opacity = s === 'skipped' ? 0.35 : 1;
      });
      edges.forEach((x) => {
        const on = taken ? taken.some((t) => t[0] === x.e.from && t[1] === x.e.to) : true;
        x.p.style.stroke = on && taken ? 'var(--after)' : 'var(--ink-3)';
        x.p.style.opacity = taken && !on ? 0.3 : 1;
      });
    },
  };
}

/* Statuses of every node after the first k log events of a run */
function statusAt(run, k) {
  const st = {};
  run.log.slice(0, k).forEach((e) => { if (e.node) st[e.node] = e.event === 'signed' ? 'waiting' : e.event; });
  return st;
}

/* ---------- Fig: Monday at Rasoi, the jobs that repeat ---------- */
FIGS.monday = (el) => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const rows = [
    ['Kavita', 'Reorder check', [1, 0, 0, 0, 0, 0], 'check stock of every item, raise PRs'],
    ['Neha', 'Goods at the gate', [0, 1, 0, 1, 0, 1], 'count, record the receipt, tell Kavita'],
    ['Dealers', 'Order emails', [1, 1, 1, 1, 1, 1], 'read, find the item, raise the request'],
  ];
  el.innerHTML = `<div style="display:grid;grid-template-columns:200px repeat(6,1fr);gap:10px;align-items:center;font-size:19px">
    <div></div>${days.map((d) => `<div style="text-align:center;font:500 16px var(--font);color:var(--ink-3)">${d}</div>`).join('')}
    ${rows.map((r, i) => `<div class="rw" data-i="${i}" style="display:contents"><div style="transition:opacity .4s" class="lab"><b>${r[0]}</b><br><span class="tiny">${r[1]}</span></div>${r[2].map((on) => `<div class="cell" style="height:74px;border-radius:16px;background:${on ? 'var(--g4)' : 'var(--card)'};transition:opacity .4s;display:flex;align-items:center;justify-content:center;font:500 14px var(--font);color:var(--before)">${on ? 'by hand' : ''}</div>`).join('')}</div>`).join('')}
  </div>
  <div class="card af" style="margin-top:26px;font-size:21px;opacity:0;transition:opacity .5s" id="mon-q">Same steps every time. The person only <b>runs</b> them. Each job could start by itself: a clock, a stock level, a form, an email.</div>`;
  const rws = [...el.querySelectorAll('.rw')];
  return { step(k) {
    rws.forEach((r, i) => r.querySelectorAll('.lab,.cell').forEach((c) => (c.style.opacity = k > i ? 1 : 0.12)));
    el.querySelector('#mon-q').style.opacity = k >= 3 ? 1 : 0;
  } };
};

/* ---------- Fig: the same task, two ways (real paths from wf_vs_agent.json) ---------- */
FIGS.twoways = (el) => {
  const w = D().wva;
  if (!w) { el.innerHTML = '<div class="ours">wf_vs_agent.json not yet run</div>'; return { step() {} }; }
  const wf = w.runs.workflow[0], ags = w.runs.agent_t0;
  let pick = 'workflow', i = 0;
  el.innerHTML = `<div class="card" style="height:470px;overflow:hidden;font-size:19px"><div class="hd" style="font:600 13px var(--font);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin-bottom:10px"></div><div class="seq" style="display:flex;flex-wrap:wrap;gap:8px;align-content:flex-start"></div><div class="res" style="margin-top:18px;font-size:19px;color:var(--ink-2)"></div><div class="tx" style="margin-top:16px;display:flex;flex-direction:column;gap:8px;font-size:16px"></div></div>`;
  const c = ctl(el, `<button data-k="workflow">Workflow</button><button data-k="agent">Ask Rasoi (agent)</button><span class="lbl">run</span><button data-d="-1">‹</button><output></output><button data-d="1">›</button>`);
  const paint = () => {
    const runs = pick === 'workflow' ? w.runs.workflow : ags;
    const r = runs[i % runs.length];
    el.querySelector('.hd').textContent = pick === 'workflow' ? 'Studio workflow · the path is the drawing' : 'Ask Rasoi · the model picks each next tool';
    el.querySelector('.seq').innerHTML = r.tool_seq.map((t, j) => `<span style="font:500 15px var(--mono);padding:7px 11px;border-radius:999px;background:${pick === 'workflow' ? 'var(--after-soft)' : 'var(--gold-soft)'}">${j + 1}. ${esc(t)}</span>`).join('');
    el.querySelector('.res').innerHTML = `${r.correct ? '<b class="a">Right outcome</b>' : '<b class="b">Different outcome</b>'}: ${r.signature.map((s) => `${s[0]} × ${num(s[1])} on ${s[2]}`).join('; ') || 'no request'} · ${num(r.tokens)} tokens · ${inr(r.cost_inr)} · ${r.seconds} s${r.turns ? ` · ${r.turns} messages from Kavita` : ''}`;
    el.querySelector('.tx').innerHTML = pick === 'workflow' ? '<div class="tiny">No conversation: the run log is the record. Kavita typed nothing.</div>' :
      (r.transcript || []).map((t) => `<div><b>Kavita:</b> ${esc(short(t.user, 90))}</div><div style="color:var(--ink-2)"><b style="color:var(--after)">Ask Rasoi:</b> ${esc(short(t.reply, 170))}</div>`).join('');
    c.querySelector('output').textContent = `${(i % runs.length) + 1} of ${runs.length}`;
    c.querySelectorAll('[data-k]').forEach((b) => b.classList.toggle('on', b.dataset.k === pick));
  };
  onClick(c, 'button', (b) => { if (b.dataset.k) { pick = b.dataset.k; i = 0; } else i = (i + Number(b.dataset.d) + 100) % 10; paint(); });
  return { step(k) { if (k >= 2 && pick === 'workflow' && k < 3) {} pick = k >= 2 ? 'agent' : 'workflow'; paint(); } };
};

/* ---------- Fig: N runs, two ways: outcomes and cost (wf_vs_agent.json) ---------- */
FIGS.determinism = (el) => {
  const w = D().wva;
  if (!w) { el.innerHTML = '<div class="ours">wf_vs_agent.json not yet run</div>'; return { step() {} }; }
  const groups = [['workflow', 'Studio workflow'], ['agent_t0', 'Ask Rasoi · temperature 0'], ['agent_t1', 'Ask Rasoi · temperature 1']];
  const W = 880, H = 430, E = P().svgEl, T = P().txt;
  const svg = E('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const rowsG = groups.map(([k, lab], gi) => {
    const g = E('g', { style: 'transition:opacity .5s' }, svg);
    const y = 50 + gi * 130, s = w.stats[k], runs = w.runs[k];
    T(g, 0, y, lab, 'font:500 20px var(--font);fill:var(--ink)');
    T(g, 0, y + 26, `${s.correct} of ${s.n} right · ${s.distinct_outcomes} outcome${s.distinct_outcomes > 1 ? 's' : ''} · ${s.distinct_paths} path${s.distinct_paths > 1 ? 's' : ''}`, 'font:400 16px var(--font);fill:var(--ink-2)');
    runs.forEach((r, i) => {
      E('rect', { x: 330 + i * 52, y: y - 24, width: 40, height: 40, rx: 12, style: `fill:${r.correct ? 'var(--after)' : 'var(--before)'};opacity:${r.correct ? 0.85 : 0.9}` }, g);
      T(g, 350 + i * 52, y + 3, String(i + 1), 'font:500 14px var(--font);fill:#fff', 'middle');
    });
    T(g, 330, y + 50, `avg ${num(Math.round(s.avg_tokens))} tokens · ${inr(s.avg_cost_inr)} · ${s.avg_seconds} s per run`, 'font:400 16px var(--mono);fill:var(--ink-3)');
    return g;
  });
  T(svg, 330, 20, 'one square = one run on a fresh Rasoi · blue = right outcome', 'font:400 14px var(--font);fill:var(--ink-3)');
  return { step(k) { rowsG.forEach((g, i) => (g.style.opacity = k >= i ? 1 : 0.08)); } };
};

/* ---------- Fig: cost per run (wf_vs_agent.json) ---------- */
FIGS.cost = (el) => {
  const w = D().wva;
  if (!w) { el.innerHTML = '<div class="ours">wf_vs_agent.json not yet run</div>'; return { step() {} }; }
  const s = w.stats;
  const rows = [['Workflow', s.workflow], ['Agent, T=0', s.agent_t0], ['Agent, T=1', s.agent_t1]];
  const maxT = Math.max(...rows.map((r) => r[1].avg_tokens)) || 1;
  el.innerHTML = `<div class="cmp">${rows.map(([lab, x], i) => `<div class="row" data-i="${i}"><div class="lab">${lab}</div><div class="br"><div class="bar ${i ? 'b' : 'a'} ${x.avg_tokens ? '' : 'zero'}" style="width:0">${x.avg_tokens ? num(Math.round(x.avg_tokens)) + ' tokens' : '0 tokens · no model call'}</div><div class="tiny">${inr(x.avg_cost_inr)} and ${x.avg_seconds} s per run · ${x.avg_model_calls} model calls</div></div></div>`).join('')}</div>
  <div class="card" style="margin-top:22px;font-size:20px;opacity:0;transition:opacity .5s" id="cost-y">Fifty-two Mondays a year: the workflow costs ${inr(0)} in model calls; the agent about ${inr(Math.round(s.agent_t0.avg_cost_inr * 52 * 100) / 100)} for this one check. Small money, but it is the same answer bought again every week.</div>`;
  const bars = [...el.querySelectorAll('.bar')];
  return { step(k) {
    bars.forEach((b, i) => { const v = rows[i][1].avg_tokens; b.style.width = k >= 1 ? (v ? Math.max(8, 100 * v / maxT) + '%' : 'auto') : '0'; });
    el.querySelector('#cost-y').style.opacity = k >= 2 ? 1 : 0;
  } };
};

/* ---------- Fig: when to use which (click a job) ---------- */
FIGS.whentouse = (el) => {
  const jobs = [
    ['Monday reorder check', 'known', 'fixed', 'Workflow', 'Same five steps every week. A schedule or stock event starts it.'],
    ['Neha records a delivery', 'known', 'fixed', 'Workflow', 'A form at the gate: PO and count in, receipt and message out.'],
    ['A dealer emails an order', 'known', 'free', 'Workflow + LLM node', 'The steps are known; only reading the email needs a model.'],
    ['“Can we buy from Shakti Seals?”', 'open', 'free', 'Agent', 'Which lookups matter depends on what each one returns.'],
    ['“Why is PO/2026/01182 late?”', 'open', 'free', 'Agent', 'An open question: status, receipts, messages, in any order.'],
    ['Stock desk for the shop floor', 'open', 'free', 'Agent node in a workflow', 'A chat trigger, your instructions, four tools, previews only.'],
  ];
  const W = 900, H = 510, E = P().svgEl, T = P().txt;
  el.innerHTML = '';
  const svg = E('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  E('rect', { x: 120, y: 20, width: 370, height: 210, rx: 22, style: 'fill:var(--after-soft)' }, svg);
  E('rect', { x: 510, y: 20, width: 370, height: 210, rx: 22, style: 'fill:#eceeff' }, svg);
  E('rect', { x: 120, y: 250, width: 370, height: 210, rx: 22, style: 'fill:var(--after-soft)' }, svg);
  E('rect', { x: 510, y: 250, width: 370, height: 210, rx: 22, style: 'fill:var(--gold-soft)' }, svg);
  T(svg, 305, 60, 'Workflow', 'font:500 24px var(--font);fill:var(--after)', 'middle');
  T(svg, 695, 60, 'Workflow + LLM node', 'font:500 24px var(--font);fill:#4b4fb6', 'middle');
  T(svg, 305, 290, 'Workflow + agent node', 'font:500 24px var(--font);fill:var(--after)', 'middle');
  T(svg, 695, 290, 'Agent', 'font:500 24px var(--font);fill:var(--gold)', 'middle');
  T(svg, 305, 492, 'input is a fixed record', 'font:400 16px var(--font);fill:var(--ink-3)', 'middle');
  T(svg, 695, 492, 'input is free text', 'font:400 16px var(--font);fill:var(--ink-3)', 'middle');
  const ry = (t, y) => { const g = E('g', { transform: `translate(${t},${y}) rotate(-90)` }, svg); return g; };
  T(ry(60, 125), 0, 0, 'steps known', 'font:400 16px var(--font);fill:var(--ink-3)', 'middle');
  T(ry(60, 355), 0, 0, 'steps depend on findings', 'font:400 16px var(--font);fill:var(--ink-3)', 'middle');
  const spot = { 'Workflow': [305, 150], 'Workflow + LLM node': [695, 150], 'Workflow + agent node': [305, 380], 'Agent': [695, 380], 'Agent node in a workflow': [305, 380] };
  const dot = E('circle', { cx: -50, cy: -50, r: 16, style: 'fill:var(--ink);transition:all .5s cubic-bezier(.3,.7,.2,1)' }, svg);
  const lab = T(svg, 0, 0, '', 'font:500 17px var(--font);fill:var(--ink)', 'middle');
  const whyEl = document.createElement('div'); whyEl.className = 'small'; whyEl.style.cssText = 'min-height:34px;margin-top:4px'; el.appendChild(whyEl);
  const c = ctl(el, jobs.map((j, i) => `<button data-i="${i}">${j[0]}</button>`).join(''));
  c.style.maxWidth = '900px';
  const pick = (i) => {
    const j = jobs[i], [x, y] = spot[j[3]];
    dot.setAttribute('cx', x); dot.setAttribute('cy', y);
    lab.setAttribute('x', x); lab.setAttribute('y', y + 40); lab.textContent = j[0];
    whyEl.innerHTML = `<b>${j[3]}.</b> ${j[4]}`;
    c.querySelectorAll('button').forEach((b) => b.classList.toggle('on', Number(b.dataset.i) === i));
  };
  onClick(c, 'button', (b) => pick(Number(b.dataset.i)));
  return { step(k) { if (k >= 1) pick(Math.min(k - 1, jobs.length - 1)); } };
};

/* ---------- Fig: templates, resolved against a real node output ---------- */
FIGS.tpl = (el) => {
  const pr = (D().tpl || {})['diwali-gasket-order']?.runs?.[0]?.nodes?.find((n) => n.id === 'pr')?.output || {};
  const stock = (D().probe || {}).calls?.check_stock?.[0]?.result || {};
  const ctx = { nodes: { pr, stock }, trigger: { item_code: 'WHS-STD-01', reorder_level: 12000, on_order: 0 } };
  const get = (path) => {
    let cur = ctx, walked = [];
    for (const part of path.match(/[A-Za-z_]\w*|\[\d+\]/g)) {
      if (part[0] === '[') { cur = cur[Number(part.slice(1, -1))]; }
      else {
        if (!cur || typeof cur !== 'object' || !(part in cur)) throw new Error(`${walked.join('.') || 'context'} has no field '${part}' (it has: ${Object.keys(cur || {}).slice(0, 6).join(', ')}, …)`);
        cur = cur[part];
      }
      walked.push(part);
    }
    return cur;
  };
  const cases = [
    ['{{nodes.pr.request_no}}', () => get('nodes.pr.request_no')],
    ['{{nodes.pr.estimated_value}}', () => get('nodes.pr.estimated_value')],
    ['{{nodes.stock.warehouses[0].on_hand}}', () => get('nodes.stock.warehouses[0].on_hand')],
    ['PR {{nodes.pr.request_no}} is {{nodes.pr.status}}', () => `PR ${get('nodes.pr.request_no')} is ${get('nodes.pr.status')}`],
    ['{{ trigger.reorder_level * 3 }}', () => get('trigger.reorder_level') * 3],
    ['{{nodes.pr.po_no}}', () => get('nodes.pr.po_no')],
  ];
  el.innerHTML = `<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px">
    <div><div class="tiny" style="margin-bottom:6px">nodes.pr: the PR node's real output</div><div class="json" style="height:420px;font-size:14px;white-space:pre-wrap;word-break:break-all">${esc(JSON.stringify(pr, null, 1)).slice(0, 1400)}</div></div>
    <div><div class="tiny" style="margin-bottom:6px">a field in a later node</div><div class="card" style="font:500 19px var(--mono);min-height:84px" id="tp-in"></div>
    <div class="tiny" style="margin:14px 0 6px">what the engine puts there</div><div class="card af" style="font:500 21px var(--mono);min-height:84px;word-break:break-all" id="tp-out"></div>
    <div class="tiny" id="tp-type" style="margin-top:10px"></div></div></div>`;
  const c = ctl(el, cases.map((x, i) => `<button data-i="${i}">${i + 1}</button>`).join('') + '<span class="tiny">pick a template</span>');
  const pick = (i) => {
    const [src, f] = cases[i];
    el.querySelector('#tp-in').textContent = src;
    const out = el.querySelector('#tp-out'), ty = el.querySelector('#tp-type');
    try {
      const v = f();
      out.textContent = typeof v === 'string' ? `"${v}"` : JSON.stringify(v);
      out.parentElement && (out.style.background = '');
      ty.innerHTML = /^\{\{[^}]*\}\}$/.test(src.trim()) ? `Whole field: the value keeps its type, <b>${typeof v === 'number' ? 'a number' : typeof v}</b>.` : 'Text around it: every {{ }} becomes text inside the string.';
    } catch (e) { out.textContent = e.message; out.style.background = 'var(--before-soft)'; ty.innerHTML = '<b class="b">An error that names the missing field.</b> The run stops here instead of sending an empty value to Bahi.'; }
    c.querySelectorAll('button').forEach((b) => b.classList.toggle('on', Number(b.dataset.i) === i));
  };
  onClick(c, 'button', (b) => pick(Number(b.dataset.i)));
  return { step(k) { pick(Math.min(k, cases.length - 1)); } };
};

/* ---------- Fig: a branch, on real stock (probe.json) ---------- */
FIGS.branch = (el) => {
  const scan = (D().probe || {}).scan || [];
  const item = (c) => scan.find((s) => s.item === c) || {};
  const tpl = { nodes: [
    { id: 'monday', type: 'trigger', title: 'Monday 09:00', x: 0, y: 1 }, { id: 'stock', type: 'tool', title: 'Check stock', x: 1, y: 1 },
    { id: 'low', type: 'condition', title: 'Below reorder?', x: 2, y: 1 }, { id: 'pr', type: 'tool', title: 'Raise the PR', x: 3, y: 0 },
    { id: 'tell', type: 'message', title: 'Tell Rohit', x: 4, y: 0 }, { id: 'fine', type: 'message', title: 'Tell Kavita: fine', x: 3, y: 2 }],
    edges: [{ from: 'monday', to: 'stock' }, { from: 'stock', to: 'low' }, { from: 'low', to: 'pr', port: 'true' }, { from: 'pr', to: 'tell' }, { from: 'low', to: 'fine', port: 'false' }] };
  el.innerHTML = '';
  const f = drawFlow(el, tpl, { W: 900, H: 330, id: 'br', bw: 150 });
  const info = document.createElement('div'); info.className = 'card'; info.style.cssText = 'margin-top:8px;font-size:19px;min-height:96px'; el.appendChild(info);
  const c = ctl(el, '<button data-c="WHS-STD-01">Whistles WHS-STD-01</button><button data-c="GSK-SIL-05L">Gaskets GSK-SIL-05L</button>');
  let cur = null;
  const paint = () => {
    if (!cur) { f.paint({}); info.innerHTML = 'Pick an item: the condition reads <code>{{nodes.stock.below_reorder}}</code> from the real check_stock output.'; return; }
    const s = item(cur), low = s.below;
    f.paint({ monday: 'done', stock: 'done', low: 'done', pr: low ? 'done' : 'skipped', tell: low ? 'done' : 'skipped', fine: low ? 'skipped' : 'done' },
      [['monday', 'stock'], ['stock', 'low'], low ? ['low', 'pr'] : ['low', 'fine'], ...(low ? [['pr', 'tell']] : [])]);
    info.innerHTML = `<b>${cur}</b>: ${num(s.free)} free + ${num(s.on_order)} on order, reorder level ${num(s.reorder)}, ${s.cover_days} days of cover → <code>below_reorder = ${s.below}</code>. Leaves by <b>${low ? 'true' : 'false'}</b>; the other side is <b>skipped</b>.`;
    c.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.c === cur));
  };
  onClick(c, 'button', (b) => { cur = b.dataset.c; paint(); });
  return { step(k) { if (k >= 1 && !cur) cur = 'WHS-STD-01'; if (k >= 2 && cur === 'WHS-STD-01' && k === 2) cur = 'GSK-SIL-05L'; if (k === 0) cur = null; paint(); } };
};

/* ---------- Fig: what each tool node hides (services from tool.json) ---------- */
FIGS.onetool = (el) => {
  const SV = D().services || {};
  const rows = [['Check stock', 'check_stock'], ['Raise the PR', 'create_purchase_request'], ['Rohit approves', 'order_status'], ['Order from Deccan', 'create_purchase_order'], ['Release to supplier', 'release_purchase_order'], ['Tell Rohit', 'send_message']];
  el.innerHTML = rows.map(([t, n], i) => `<div class="r" style="display:grid;grid-template-columns:230px 1fr;gap:14px;align-items:center;margin-bottom:12px;transition:opacity .4s">
    <div class="card af" style="padding:12px 16px;font-size:19px"><b>${t}</b><br><span class="mono" style="font-size:13px">${n}</span></div>
    <div class="sv" style="display:flex;flex-wrap:wrap;gap:6px">${(SV[n] || []).map((s) => `<span style="font:400 13.5px var(--mono);padding:5px 9px;border-radius:9px;background:var(--before-soft);color:var(--before)">${s}</span>`).join('')}</div></div>`).join('') +
    `<div class="tiny" style="margin-top:6px">Services each tool calls, from its <code>tool.json</code> (<code>"services"</code>). The approval node reads <code>order_status</code>.</div>`;
  const rs = [...el.querySelectorAll('.r')], svs = [...el.querySelectorAll('.sv')];
  return { step(k) { rs.forEach((r) => (r.style.opacity = 1)); svs.forEach((s) => (s.style.opacity = k >= 1 ? 1 : 0)); } };
};

/* ---------- Fig: a real Studio run, scrubbed event by event (templates_fresh.json) ---------- */
function runFig(tid, el, opts = {}) {
  const T = (D().tpl || {})[tid];
  if (!T) { el.innerHTML = '<div class="ours">templates_fresh.json not yet run</div>'; return { step() {} }; }
  const run = T.runs[opts.run || 0];
  el.innerHTML = '';
  const f = drawFlow(el, T, { W: opts.W || 1400, H: opts.H || 280, id: tid.slice(0, 4) + (opts.run || 0), bw: opts.bw || 160 });
  const box = document.createElement('div');
  box.style.cssText = 'display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:8px';
  box.innerHTML = `<div class="trace" style="height:${opts.logH || 250}px;font-size:14px;min-width:0"></div><div class="json" style="height:${opts.logH || 250}px;font-size:13.5px;min-width:0"></div>`;
  el.appendChild(box);
  const nonNode = run.log.filter((e) => true);
  let k = nonNode.length;
  const c = ctl(el, `<span class="lbl">run log</span><button data-d="-1">‹</button><input type="range" min="1" max="${nonNode.length}" value="${k}"><button data-d="1">›</button><output></output>`);
  const rng = c.querySelector('input');
  const paint = () => {
    const st = statusAt(run, k);
    if (k >= nonNode.length) run.nodes.forEach((n) => { if (n.status === 'skipped') st[n.id] = 'skipped'; });
    f.paint(st);
    box.children[0].innerHTML = `<div class="h">Run log · ${esc(T.name)}</div>` + nonNode.slice(0, k).map((e) => `<div class="l" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis"><b>${esc(e.node || 'run')}</b> <span class="${e.event === 'error' || e.event === 'failed' || e.event === 'waiting' ? 'x' : 'ok'}">${esc(e.event)}</span> ${esc(short(e.text, 110))}</div>`).slice(-(opts.lines || 7)).join('');
    const last = nonNode.slice(0, k).reverse().find((e) => e.node);
    const n = last && run.nodes.find((x) => x.id === last.node);
    const lines = n ? JSON.stringify(n.output, null, 1).split('\n').map((l) => short(l, opts.cols || 64)) : [];
    const maxL = Math.floor(((opts.logH || 250) - 34) / 19.6) - 1;
    box.children[1].textContent = n ? `nodes.${n.id} =\n` + (lines.length > maxL ? [...lines.slice(0, maxL - 1), '  …'] : lines).join('\n') : '';
    rng.value = k; c.querySelector('output').textContent = `${k} / ${nonNode.length}`;
  };
  rng.addEventListener('input', () => { k = Number(rng.value); paint(); });
  onClick(c, 'button', (b) => { k = Math.max(1, Math.min(nonNode.length, k + Number(b.dataset.d))); paint(); });
  return { step(s) { k = s === 0 && opts.build ? 2 : nonNode.length; if (opts.build) k = Math.max(2, Math.round(nonNode.length * Math.min(1, (s + 1) / (opts.build + 1)))); paint(); } };
}
FIGS.run_diwali = (el) => runFig('diwali-gasket-order', el, { build: 3 });
FIGS.run_reorder = (el) => runFig('reorder-when-low', el, { H: 330, bw: 138, logH: 230 });
FIGS.run_goods = (el) => runFig('goods-arrived', el, { W: 960, bw: 175, cols: 44 });
FIGS.run_dealer = (el) => runFig('dealer-email-to-order', el, { W: 1200 });

/* ---------- Fig: the dealer's email, read by the LLM node (templates_fresh.json) ---------- */
FIGS.llmnode = (el) => {
  const T = (D().tpl || {})['dealer-email-to-order'];
  if (!T) { el.innerHTML = '<div class="ours">templates_fresh.json not yet run</div>'; return { step() {} }; }
  const n = (id) => T.runs[0].nodes.find((x) => x.id === id);
  const email = T.nodes[0].config.data.email;
  const ex = n('extract'), meta = ex.meta || {};
  el.innerHTML = `<div style="display:grid;grid-template-columns:1.1fr 0.9fr;gap:18px">
    <div class="card" style="font-size:16.5px;line-height:1.5;white-space:pre-wrap;height:440px">${esc(email)}</div>
    <div><div class="s1 card af" style="font:400 15px/1.5 var(--mono);white-space:pre-wrap">nodes.extract =\n${esc(JSON.stringify(ex.output, null, 1))}</div>
    <div class="s2 tiny" style="margin-top:10px">${esc(meta.model || '')} · ${num((meta.tokens_in || 0) + (meta.tokens_out || 0))} tokens · ${inr(meta.cost_inr || 0)} · ${meta.seconds} s</div>
    <div class="s3 card" style="margin-top:12px;font-size:17px">Then fixed nodes: <code>find_item</code> → <b>${esc(n('find').summary)}</b>; <code>create_purchase_request</code> → <b>${esc(n('pr').summary)}</b> (₹53,808 is within Kavita's limit).</div></div></div>`;
  const parts = ['.s1', '.s2', '.s3'].map((q) => el.querySelector(q));
  parts.forEach((p) => (p.style.transition = 'opacity .45s'));
  return { step(k) { parts.forEach((p, i) => (p.style.opacity = k > i ? 1 : 0)); } };
};

/* ---------- Fig: build your own agent, the real two-turn chat (templates_fresh.json) ---------- */
FIGS.agentchat = (el) => {
  const T = (D().tpl || {})['build-your-own-agent'];
  if (!T) { el.innerHTML = '<div class="ours">templates_fresh.json not yet run</div>'; return { step() {} }; }
  const items = [];
  T.runs.forEach((r) => {
    const desk = r.nodes.find((x) => x.id === 'desk');
    items.push(`<div class="msg u"><div class="who">Kavita</div>${esc(r.user)}</div>`);
    const calls = (desk.output.tool_calls || []);
    items.push(`<div class="msg ag" style="max-width:96%"><div class="who">Stock desk agent · ${calls.length} tool call${calls.length === 1 ? '' : 's'} · ${num(r.tokens)} tokens · ${inr(r.cost_inr)}</div>${calls.map((c) => `<div class="pv" style="margin:0 0 6px;font-size:14px">${esc(c.tool)}(${'confirm' in c.args ? 'confirm=' + c.args.confirm : esc(Object.values(c.args).join(', '))}) → ${esc(c.summary)}</div>`).join('')}${esc(r.reply)}</div>`);
  });
  el.innerHTML = `<div class="thread" style="height:630px;font-size:15px;gap:8px;padding:14px">${items.map((h, i) => `<div class="it" style="display:flex;flex-direction:column;transition:opacity .4s">${h}</div>`).join('')}</div>`;
  const its = [...el.querySelectorAll('.it')];
  return { step(k) { its.forEach((x, i) => (x.style.opacity = i <= k ? 1 : 0.1)); } };
};

/* ---------- Fig: run each template twice on the same Rasoi (templates_fresh.json) ---------- */
FIGS.rerun = (el) => {
  const T = D().tpl || {};
  const ids = ['diwali-gasket-order', 'reorder-when-low', 'goods-arrived', 'dealer-email-to-order'];
  const docs = (d) => [...d.pr.map((p) => p.pr_no), ...d.po.map((p) => p.po_no), ...d.grn.map((g) => g.grn_no)].join(', ') || 'none';
  const second = (r) => {
    const err = r.nodes.find((n) => n.status === 'error');
    if (err) return `<span class="b">stopped at “${esc(err.id)}”</span>: ${esc(short((err.output || {}).error, 90))}`;
    const dup = r.nodes.find((n) => n.output && n.output.already_done);
    if (dup) return `<span class="a">found it</span>: ${esc(short(dup.summary, 80))}`;
    return `<span class="a">nothing to do</span>: ${esc(short((r.log.find((e) => e.node && e.event === 'done') || {}).text, 80))}`;
  };
  el.innerHTML = `<table class="t"><tr><th>Workflow</th><th>Run 1</th><th>Run 2, same Rasoi</th><th>Documents in Bahi after both</th><th>Messages</th></tr>${ids.filter((i) => T[i]).map((i, j) => `<tr class="rr" style="transition:opacity .4s"><td><b>${esc(T[i].name)}</b></td><td>${esc(T[i].runs[0].status)}${T[i].runs[0].waited_for ? ', waited for Rohit' : ''}</td><td style="font-size:18px">${second(T[i].runs[1])}</td><td class="n">${esc(docs(T[i].docs_after))}</td><td class="n">${T[i].docs_after.messages.filter((m) => m.channel === 'SLACK').length}</td></tr>`).join('')}</table>`;
  const rr = [...el.querySelectorAll('.rr')];
  return { step() { rr.forEach((r) => (r.style.opacity = 1)); } };
};

/* ---------- Fig: every template on a fresh Rasoi (templates_fresh.json) ---------- */
FIGS.measured = (el) => {
  const T = D().tpl || {};
  const mt = (rs) => Math.round(rs.reduce((a, r) => a + r.nodes.reduce((b, n) => b + ((n.meta || {}).seconds || 0), 0), 0) * 10) / 10;
  const rows = Object.entries(T).map(([id, t]) => {
    const rs = id === 'build-your-own-agent' ? t.runs : [t.runs[0]];
    const sum = (k) => rs.reduce((a, r) => a + (r[k] || 0), 0);
    const d = t.docs_after;
    const made = id === 'build-your-own-agent' ? d.pr.map((p) => `${p.pr_no} ${p.status}`).join(', ') :
      [...t.runs[0].nodes.filter((n) => n.output && (n.output.grn_no || n.output.po_no || n.output.request_no)).map((n) => n.output.grn_no || n.output.po_no || n.output.request_no)].filter((v, i, a) => a.indexOf(v) === i).join(', ');
    return `<tr><td><b>${esc(t.name)}</b><div class="tiny">${esc(t.trigger)} trigger · ${t.nodes.length} nodes</div></td><td class="n">${sum('nodes_run')}${sum('nodes_skipped') ? ` (+${sum('nodes_skipped')} skipped)` : ''}</td><td class="n">${rs[0].waited_for ? 'yes, Rohit' : 'no'}</td><td class="n">${Number(sum('seconds')).toFixed(3)} s</td><td class="n">${num(sum('tokens'))} · ${inr(Math.round(sum('cost_inr') * 10000) / 10000)}${mt(rs) ? ` · ${mt(rs)} s` : ''}</td><td style="font-size:17px">${esc(made)}</td></tr>`;
  });
  el.innerHTML = `<table class="t"><tr><th>Template</th><th>Nodes run</th><th>Waited</th><th>Engine time</th><th>Model tokens · ₹ · model time</th><th>Bahi documents</th></tr>${rows.join('')}</table>
  <div class="tiny" style="margin-top:10px">Engine time excludes the human wait and replayed model calls; model time is what the model took when we recorded it. Agent row: two chat turns. From <code>experiments/logs/templates_fresh.json</code>.</div>`;
  return { step() {} };
};

/* ---------- Fig: the map, with this lecture's piece lit ---------- */
FIGS.map = (el) => {
  el.innerHTML = `<div style="position:relative;width:540px;height:723px"><img src="../../figures/ask_rasoi_architecture.png" style="width:540px;height:723px;display:block" alt="Ask Rasoi architecture">
    <div class="lit" style="position:absolute;left:170px;top:66px;width:134px;height:62px;border-radius:12px;box-shadow:0 0 0 4px var(--after),0 0 28px 8px rgba(11,87,208,.35);transition:opacity .5s"></div>
    <div class="lit2" style="position:absolute;left:24px;top:410px;width:440px;height:162px;border-radius:14px;box-shadow:0 0 0 3px var(--after);transition:opacity .5s"></div></div>`;
  const a = el.querySelector('.lit'), b = el.querySelector('.lit2');
  return { step(k) { a.style.opacity = 1; b.style.opacity = k >= 1 ? 1 : 0; } };
};
})();
