/* Lecture 11 · live figures for parts 2 to 4 (durable, data, gateway, cost). Numbers from window.FD (figdata.js). */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const FD = window.FD || {};
const inr = (x, d = 0) => '₹' + Number(x).toLocaleString('en-IN', { minimumFractionDigits: d, maximumFractionDigits: d });
const num = (x) => Math.round(x).toLocaleString('en-IN');
const esc = (s) => String(s ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const html = (el, s) => { el.innerHTML = s; return el; };
const stop = (e) => e.stopPropagation();
const none = (el, what) => { el.innerHTML = `<div class="ours" style="position:static">${what}: not yet measured.</div>`; return { step() {} }; };

/* Fig: the drill, as a timeline of what happened (logs/durable_order.json) */
FIGS.drill = (el) => {
  const D = FD.dur;
  if (!D) return none(el, 'The durable drill');
  const keep = D.events.filter((e) => !/versions|screenshot|dev server/.test(e.what));
  const kind = (w) => /killed/.test(w) ? 'var(--before)' : /worker started/.test(w) ? 'var(--after)' : /signal|approved/.test(w) ? 'var(--gold)' : 'var(--ink-3)';
  const label = (e) => {
    const w = e.what;
    if (w === 'worker started') return `${e.worker} starts`;
    if (/killed/.test(w)) return /order saved/.test(w) ? `order saved as ${(e.orders || [{}])[0].po_no} (status ${(e.orders || [{}])[0].status}): worker-2 killed` : `${e.worker} killed (SIGKILL)`;
    if (/agent turn 1/.test(w)) return 'turn 1: stock checked, request previewed; waits for Kavita';
    if (/user_says/.test(w)) return 'signal: Kavita says "Yes, go ahead."';
    if (/agent turn 2/.test(w)) return `turn 2: ${e.request_no} saved; waits for Rohit`;
    if (/timer fired/.test(w)) return `timer fired: reminder ${e.reminders} sent to Rohit`;
    if (/Rohit approved/.test(w)) return 'Rohit approves in Bahi, in his own session';
    if (/approval_decided/.test(w)) return 'signal: approval_decided, with no worker running';
    if (/no worker runs/.test(w)) return `workflow still open; history has ${e.history_length} events`;
    if (/finished/.test(w)) return `workflow finished: ${e.outcome}`;
    if (/Bahi after/.test(w)) return `Bahi: ${e.requests} request, ${e.orders_for_request} order, ${e.released} released`;
    if (/replayer/.test(w)) return `replayer on the recorded history: ${e.ok ? 'passes' : 'fails'}`;
    if (/workflow started/.test(w)) return 'workflow started with Kavita\'s message';
    return w;
  };
  let kk = 0;
  const draw = () => {
    const T = Math.max(...keep.map((e) => e.t));
    html(el, `<div style="display:flex;flex-direction:column;gap:5px">${keep.map((e, i) => `<div style="display:grid;grid-template-columns:76px 14px 1fr;gap:10px;align-items:center;opacity:${i < kk ? 1 : 0.1};transition:opacity .35s">
      <span style="font:500 15px var(--mono);text-align:right;color:var(--ink-3)">${e.t.toFixed(1)} s</span>
      <span style="width:12px;height:12px;border-radius:50%;background:${kind(e.what)}"></span>
      <span style="font-size:17.5px;line-height:1.3">${esc(label(e))}</span></div>`).join('')}</div>
      <p class="small" style="margin-top:10px">Seconds since the drill began, from the run's own event log. Each killed worker held a workflow task; Temporal let it time out (${(D.by_type || {}).EVENT_TYPE_WORKFLOW_TASK_TIMED_OUT || 0} timeouts in the history) and gave it to the next worker.</p>`);
  };
  draw();
  return { step(k) { kk = Math.round((k / 5) * keep.length) + 1; if (k >= 5) kk = keep.length; draw(); } };
};

/* Fig: model calls per worker, in the order they were sent (logs/durable_model_http.jsonl) */
FIGS.workerCalls = (el) => {
  const D = FD.dur;
  if (!D) return none(el, 'Model calls per worker');
  const H = D.model_http || [];
  const col = { 'worker-1': 'var(--after)', 'worker-2': '#9b7be0', 'worker-3': '#1b8a6b' };
  html(el, `<div style="display:flex;gap:10px;align-items:stretch">${H.map((c, i) => `<div style="flex:1;border-radius:16px;padding:12px;background:#fff;box-shadow:var(--shadow);border-top:6px solid ${col[c.worker] || 'var(--ink-3)'}">
      <div style="font:500 14px var(--font);color:var(--ink-3)">call ${i + 1} · ${c.worker}</div><div style="font:500 30px/1.2 var(--font)">${c.messages}</div><div class="tiny">messages sent · HTTP ${c.status}</div></div>`).join('')}</div>
    <p class="small" style="margin-top:10px">${H.length} model calls went to OpenRouter in the whole drill, and the history holds ${D.model_activities} model activities: one call each, none repeated. The conversation only grows (${H.map((c) => c.messages).join(', ')} messages).</p>`);
  return { step() {} };
};

/* Fig: scrub the recorded event history */
FIGS.history = (el) => {
  const D = FD.dur;
  if (!D) return none(el, 'The event history');
  const H = D.history;
  const col = (t) => /ACTIVITY_TASK_SCHEDULED/.test(t) ? 'var(--after)' : /ACTIVITY_TASK_COMPLETED/.test(t) ? '#5a9cf5' : /SIGNALED/.test(t) ? 'var(--gold)'
    : /TIMER/.test(t) ? '#e9b44c' : /FAILED|TIMED_OUT/.test(t) ? 'var(--before)' : /WORKFLOW_TASK/.test(t) ? '#c9d2de' : 'var(--ink-3)';
  let i = H.length - 1;
  html(el, `<div class="ctl" style="margin:0 0 14px"><span>Event</span><input type="range" min="1" max="${H.length}" value="${H.length}" style="width:900px"><output></output></div>
    <svg viewBox="0 0 1400 70" width="1400" height="70" class="strip"></svg><div class="det" style="margin-top:12px"></div>`);
  const svg = el.querySelector('svg'), P = window.Plates, w = 1400 / H.length;
  H.forEach((e, j) => P.svgEl('rect', { x: j * w, y: 10, width: Math.max(1, w - 1.5), height: 50, rx: 2, style: `fill:${col(e.type)}`, 'data-j': j }, svg));
  const mark = P.svgEl('rect', { x: 0, y: 2, width: Math.max(3, w), height: 66, rx: 3, style: 'fill:none;stroke:var(--ink);stroke-width:2' }, svg);
  const inp = el.querySelector('input'), out = el.querySelector('output'), det = el.querySelector('.det');
  const tally = (upto) => {
    const s = H.slice(0, upto + 1);
    const c = (re) => s.filter((e) => re.test(e.type)).length;
    return { acts: c(/ACTIVITY_TASK_SCHEDULED/), done: c(/ACTIVITY_TASK_COMPLETED/), sig: c(/SIGNALED/), timers: c(/TIMER_FIRED/), timeouts: c(/TIMED_OUT/) };
  };
  const draw = () => {
    const e = H[i]; out.textContent = `${i + 1} of ${H.length}`;
    mark.setAttribute('x', i * w);
    const t = tally(i);
    const recent = H.slice(Math.max(0, i - 7), i + 1);
    det.innerHTML = `<div style="display:grid;grid-template-columns:1fr 420px;gap:22px">
      <div style="display:flex;flex-direction:column;gap:4px">${recent.map((r, k) => `<div style="display:grid;grid-template-columns:52px 360px 1fr 90px;gap:8px;font:400 15px/1.35 var(--mono);${r === e ? 'font-weight:600;color:var(--ink)' : 'color:var(--ink-2)'}">
        <span>#${r.id}</span><span><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${col(r.type)}"></i> ${esc(r.type)}</span><span>${esc(r.name)}</span><span>${esc(r.time)}</span></div>`).join('')}</div>
      <div class="card" style="font-size:18px;padding:14px 18px"><b>Up to here</b><br>${t.acts} activities scheduled, ${t.done} completed<br>${t.sig} signals · ${t.timers} timer fired · ${t.timeouts} timed out
      <p class="small" style="margin:8px 0 0">Blue: activities (model calls, Bahi tools). Green: signals. Amber: timers. Ember: a timeout, where a dead worker's call was given up and retried.</p></div></div>`;
  };
  inp.oninput = () => { i = +inp.value - 1; draw(); };
  svg.addEventListener('click', (ev) => { stop(ev); const j = ev.target.dataset && ev.target.dataset.j; if (j != null) { i = +j; inp.value = i + 1; draw(); } });
  draw();
  return { step() {} };
};

/* Fig: pgvector vs the L3 index */
FIGS.pgBars = (el) => {
  const M = FD.mem;
  if (!M) return none(el, 'pgvector');
  const R = M.retrieval, S = M.scale;
  const rows = [['L3 in memory (Python)', R.l3_in_memory], ['pgvector, exact', R.pg_exact], ['pgvector, HNSW', R.pg_hnsw]];
  let kk = 9;
  const draw = () => {
    html(el, `<h3 style="margin-bottom:6px">${M.chunks_kavita} of Kavita's clauses · 33 questions</h3>
      <table class="t" style="font-size:18px"><tr><th></th><th>recall@1</th><th>recall@5</th><th>p50 ms</th><th>p95 ms</th></tr>
      ${rows.map(([lab, r]) => `<tr><td>${lab}</td><td class="n">${Math.round(100 * r['recall@1'])}%</td><td class="n">${Math.round(100 * r['recall@5'])}%</td><td class="n">${r.ms_p50}</td><td class="n">${r.ms_p95}</td></tr>`).join('')}</table>
      <p class="tiny" style="margin:6px 0 18px">L3's time includes its pure-Python cosine loop over every clause; Postgres's includes the round trip on localhost.</p>
      <div style="opacity:${kk >= 2 ? 1 : 0.08};transition:opacity .4s"><h3 style="margin-bottom:6px">Add ${num(S.rows - M.chunks_all)} random vectors (${num(S.rows)} rows, ${esc(S.table_size)})</h3>
      <div class="cmp">${[['exact scan', S.pg_exact.ms_p50, 'b'], ['HNSW index', S.pg_hnsw.ms_p50, 'a'], ['numpy, all in memory', S.numpy_bruteforce_ms_p50, 'a']].map(([l, v, c]) => `<div class="row" style="grid-template-columns:200px 1fr"><span class="lab">${l}</span><div class="br"><div class="bar ${c}" style="width:${Math.max(16, 80 * v / Math.max(S.pg_exact.ms_p50, S.numpy_bruteforce_ms_p50, S.pg_hnsw.ms_p50))}%">${v} ms</div></div></div>`).join('')}</div>
      <p class="small" style="margin-top:10px">HNSW top 5 equal to the exact top 5 for ${esc(S.hnsw_top5_equals_exact_top5)} questions. Index build: ${M.hnsw_build_seconds_scaled} s. ${esc(S.note)}.</p></div>`);
  };
  return { step(k) { kk = k + 1; draw(); } };
};

/* Fig: rate limits across three replicas, in-process vs Redis */
FIGS.rate = (el) => {
  const M = FD.mem;
  if (!M || !M.rate_limit) return none(el, 'The rate-limit drill');
  const R = M.rate_limit, F = M.redis_failover || {};
  const row = (lab, allowed) => `<div style="margin-bottom:14px"><div style="font-size:18px;margin-bottom:6px">${lab}: <b>${allowed}</b> of ${R.messages} let through</div>
    <div style="display:grid;grid-template-columns:repeat(20,1fr);gap:4px">${Array.from({ length: R.messages }, (_, i) => `<span style="height:22px;border-radius:5px;background:${i < allowed ? 'var(--after)' : '#eef1f5'}"></span>`).join('')}</div></div>`;
  html(el, `<h3>Kavita sends ${R.messages} messages in one minute; the limit is ${R.limit_per_minute}</h3>
    ${row(`Counters in each of ${R.replicas} processes`, R.allowed_in_process_counters)}${row('One counter in Redis', R.allowed_redis_counter)}
    <div class="card" style="font-size:17px;padding:12px 16px;margin-top:10px"><b>A copy dies.</b> Replica 1 added "${esc((F.replica2 || {}).last || '')}" and was killed. Replica 2 found ${(F.replica2 || {}).redis_messages} messages in Redis and ${(F.replica2 || {}).in_memory_dict} in its own memory. After a Redis restart (append-only file on): ${F.after_redis_restart_messages} messages.</div>`);
  return { step() {} };
};

/* Fig: the budget, request by request */
FIGS.budget = (el) => {
  const G = FD.gw;
  if (!G || !G.budget) return none(el, 'The gateway drill');
  const R = G.budget.requests, B = G.budget.key_budget_usd;
  let cum = 0;
  const pts = R.map((r) => { cum += r.cost_usd || 0; return { ...r, cum }; });
  const W = 780, H = 360, P = window.Plates;
  html(el, `<h3>Kavita's key: budget US$${B}, gemini-3.8-flash</h3><svg viewBox="0 0 ${W} ${H + 40}" width="${W}" height="${H + 40}"></svg>
    <div class="small" style="margin-top:6px">Each bar is one request's cost as LiteLLM reported it (<code>x-litellm-response-cost</code>); the line is the running total. Ember: refused.</div>
    <table class="t" style="font-size:16px;margin-top:12px"><tr><th>Team</th><th>Spend (US$)</th><th>Budget</th></tr>${Object.entries(G.team_spend || {}).map(([t, s]) => `<tr><td>${t}</td><td class="n">${s.spend == null ? '–' : Number(s.spend).toFixed(6)}</td><td class="n">${s.max_budget}</td></tr>`).join('')}</table>`);
  const svg = el.querySelector('svg');
  const maxY = Math.max(B * 1.3, cum * 1.1), bw = Math.min(40, (W - 60) / pts.length - 4);
  const y = (v) => H - (v / maxY) * (H - 20);
  P.svgEl('line', { x1: 50, x2: W, y1: y(B), y2: y(B), style: 'stroke:var(--before);stroke-dasharray:6 5;stroke-width:1.5' }, svg);
  P.txt(svg, W - 4, y(B) - 6, `budget ${B}`, 'font:13px var(--font);fill:var(--before)', 'end');
  let prev = null;
  pts.forEach((p, i) => {
    const x = 60 + i * (bw + 4);
    if (p.status === 200) P.svgEl('rect', { x, y: y(p.cost_usd), width: bw, height: H - y(p.cost_usd), rx: 3, style: 'fill:#9cc3f5' }, svg);
    else P.svgEl('rect', { x, y: H - 30, width: bw, height: 30, rx: 3, style: 'fill:var(--before)' }, svg);
    const cy = y(p.cum);
    if (prev) P.svgEl('line', { x1: prev[0], y1: prev[1], x2: x + bw / 2, y2: cy, style: 'stroke:var(--after);stroke-width:2' }, svg);
    P.svgEl('circle', { cx: x + bw / 2, cy, r: 3.5, style: 'fill:var(--after)' }, svg);
    prev = [x + bw / 2, cy];
    P.txt(svg, x + bw / 2, H + 18, String(p.n), 'font:12.5px var(--font);fill:var(--ink-3)', 'middle');
  });
  P.svgEl('line', { x1: 50, x2: W, y1: H, y2: H, style: 'stroke:var(--rule)' }, svg);
  P.txt(svg, 50, H + 36, 'request number', 'font:13px var(--font);fill:var(--ink-3)');
  return { step() {} };
};

/* Fig: the cost-per-order calculator */
FIGS.costCalc = (el) => {
  const C = FD.cost;
  if (!C) return none(el, 'The cost model');
  const S = C.summary, PR = C.prices, X = C.usd_inr;
  const gIn = (FD.guard && FD.guard.guards.llamaguard.tokens_in_mean) || 0;
  let model = 'gemini-3.8-flash', guard = true, perDay = 120, retry = 5;
  const calc = () => {
    const s = S[`whole_order_L5_T01|${model}`];
    const msgs = ((C.runs || []).find((r) => r.task.startsWith('T01') && r.model === model) || {});
    const p = PR[model];
    const agent = (s.tokens_in_mean * p[0] + s.tokens_out_mean * p[1]) / 1e6 * X * (1 + retry / 100);
    const nMsg = msgs.person_messages || 0;
    const g = guard ? (gIn * nMsg * PR['llama-guard-4-12b'][0] + 2 * nMsg * PR['llama-guard-4-12b'][1]) / 1e6 * X : 0;
    return { s, agent, g, nMsg, total: agent + g, month: (agent + g) * perDay * 26 };
  };
  html(el, `<div class="ctl" style="margin:0 0 10px"><button data-m="gemini-3.8-flash">gemini-3.8-flash</button><button data-m="gemini-3.5-flash-lite">gemini-3.5-flash-lite</button>
      <button data-g="1">Llama Guard on each message</button></div>
    <div class="ctl" style="margin:0 0 6px"><span>Orders a working day</span><input type="range" min="10" max="1000" step="10" value="120" data-k="d"><output data-o="d"></output></div>
    <div class="ctl" style="margin:0 0 16px"><span>Model calls retried</span><input type="range" min="0" max="30" step="1" value="5" data-k="r"><output data-o="r"></output></div>
    <div class="res"></div>`);
  const res = el.querySelector('.res');
  const draw = () => {
    el.querySelectorAll('[data-m]').forEach((b) => b.classList.toggle('on', b.dataset.m === model));
    el.querySelector('[data-g]').classList.toggle('on', guard);
    el.querySelector('[data-o="d"]').textContent = num(perDay);
    el.querySelector('[data-o="r"]').textContent = retry + '%';
    const c = calc();
    res.innerHTML = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div class="stat"><div class="v">${inr(c.total, 2)}</div><div class="k">per order: the whole job, ${c.s.calls_mean} model calls, ${num(c.s.tokens_in_mean)} tokens in, ${num(c.s.tokens_out_mean)} out (L5 T01, measured)</div></div>
      <div class="stat"><div class="v">${inr(c.month)}</div><div class="k">a month at ${num(perDay)} orders a day, 26 working days (the volume is an assumption)</div></div></div>
      <table class="t" style="font-size:17px;margin-top:14px"><tr><th>Part</th><th>₹ per order</th><th>From</th></tr>
      <tr><td>Agent model calls</td><td class="n">${inr(c.agent, 2)}</td><td>measured tokens × list price × (1 + retries)</td></tr>
      <tr><td>Input guard, ${c.nMsg} messages from people</td><td class="n">${inr(c.g, 3)}</td><td>Llama Guard: ${Math.round(gIn)} tokens in per message, measured</td></tr>
      <tr><td>Gateway, Temporal, Redis, Postgres</td><td class="n">–</td><td>self-hosted: servers, not tokens; <i>not yet measured</i></td></tr></table>
      <p class="tiny" style="margin-top:8px">Prices: OpenRouter list, 28 Oct 2026, US$ per million tokens in/out: flash ${PR['gemini-3.8-flash'].join(' / ')}, lite ${PR['gemini-3.5-flash-lite'].join(' / ')}; ₹${X} per US$.</p>`;
  };
  el.querySelectorAll('[data-m]').forEach((b) => b.onclick = (e) => { stop(e); model = b.dataset.m; draw(); });
  el.querySelector('[data-g]').onclick = (e) => { stop(e); guard = !guard; draw(); };
  el.querySelectorAll('input').forEach((x) => x.oninput = () => { if (x.dataset.k === 'd') perDay = +x.value; else retry = +x.value; draw(); });
  draw();
  return { step() {} };
};

/* Fig: every recorded run, priced */
FIGS.costRuns = (el) => {
  const C = FD.cost;
  if (!C) return none(el, 'The priced runs');
  const R = C.runs, W = 900, H = 520, P = window.Plates;
  const srcs = [['L5', 'L5 harness, 12 tasks'], ['L7', 'L7 six scenarios'], ['L11', 'L11 injection runs']];
  const colr = { L5: 'var(--after)', L7: '#9b7be0', L11: 'var(--before)' };
  let tier = 'gemini-3.8-flash';
  html(el, `<div class="ctl" style="margin:0 0 8px"><button data-t="gemini-3.8-flash">gemini-3.8-flash</button><button data-t="gemini-3.5-flash-lite">gemini-3.5-flash-lite</button>
    ${srcs.map(([k, l]) => `<span style="margin-left:10px"><i style="display:inline-block;width:11px;height:11px;border-radius:50%;background:${colr[k]}"></i> ${l}</span>`).join('')}</div>
    <svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"></svg><div class="small sel" style="margin-top:4px">Hover or click a dot.</div>`);
  const svg = el.querySelector('svg'), sel = el.querySelector('.sel');
  const draw = () => {
    el.querySelectorAll('[data-t]').forEach((b) => b.classList.toggle('on', b.dataset.t === tier));
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const rs = R.filter((r) => r.model === tier);
    const maxX = Math.max(...rs.map((r) => r.tokens_in)) * 1.05, maxY = Math.max(...rs.map((r) => r.inr)) * 1.1;
    const x = (v) => 70 + (v / maxX) * (W - 140), y = (v) => H - 50 - (v / maxY) * (H - 80);
    for (let k = 0; k <= 4; k++) {
      const v = maxY * k / 4;
      P.svgEl('line', { x1: 70, x2: W - 10, y1: y(v), y2: y(v), style: 'stroke:var(--rule)' }, svg);
      P.txt(svg, 62, y(v) + 4, '₹' + v.toFixed(v < 1 ? 2 : 1), 'font:12.5px var(--font);fill:var(--ink-3)', 'end');
    }
    for (let k = 0; k <= 4; k++) P.txt(svg, x(maxX * k / 4), H - 28, num(maxX * k / 4), 'font:12.5px var(--font);fill:var(--ink-3)', 'middle');
    P.txt(svg, W - 70, H - 8, 'tokens in per conversation', 'font:13px var(--font);fill:var(--ink-3)', 'end');
    rs.forEach((r) => {
      const k = r.source.split(' ')[0];
      const c = P.svgEl('circle', { cx: x(r.tokens_in), cy: y(r.inr), r: 6, style: `fill:${colr[k]};fill-opacity:.75;cursor:pointer` }, svg);
      const show = (e) => { if (e) stop(e); sel.innerHTML = `<b>${esc(r.task)}</b> · ${esc(r.source)} · ${num(r.tokens_in)} in, ${num(r.tokens_out)} out, ${r.model_calls} calls · <b>${inr(r.inr, 2)}</b>${r.passed ? '' : ' · <span class="b">failed</span>'}`; };
      c.addEventListener('mouseenter', () => show()); c.addEventListener('click', show);
    });
  };
  el.querySelectorAll('[data-t]').forEach((b) => b.onclick = (e) => { stop(e); tier = b.dataset.t; draw(); });
  draw();
  return { step() {} };
};
})();
