/* Live figures for Lecture 8 · Agent Frameworks in Industry. Loaded BEFORE plates.js; helpers come from window.Plates.
   Every number comes from figdata.js (window.FD), which gen_figdata.py writes from experiments/logs/:
   fw_<setup>.json (run 1, 28 Oct 2026), fw_<setup>_rep2.json (+ _rep2b re-runs after OpenRouter rate limits),
   fw_<setup>_replay.json (replay timing), desks.json, gateway.json, loc.json, fw_ours_ollama_*.json. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const FD = window.FD;
const esc = (s) => String(s ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const fmt = (n) => Number(n).toLocaleString('en-IN');
const inr = (n) => '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const md = (s) => String(s ?? '').replace(/\*\*|`|#{2,}\s*/g, '').replace(/\s*[-*]\s+(?=\S)/g, ' · ').replace(/\s+/g, ' ').replace(/^ · /, '').trim();
const S = {}; (FD.setups || []).forEach((x) => (S[x.key] = x));
const FWN = { ours: 'Our harness', openai_agents: 'OpenAI Agents SDK', adk: 'Google ADK', langgraph: 'LangGraph agent' };

/* ---------- data-v: plate text filled from figdata, so words and figures never disagree ---------- */
const V = Object.assign({ S }, FD);
const fmts = { inr, n: fmt, k: (v) => fmt(v), of12: (v) => `${v} / 12`, list: (v) => (v || []).join(', ') };
document.querySelectorAll('[data-v]').forEach((el) => {
  const [path, f] = el.dataset.v.split('|');
  const v = path.split('.').reduce((o, k) => (o == null ? o : o[k]), V);
  el.textContent = v == null ? 'not yet measured' : (f ? fmts[f](v) : (typeof v === 'number' ? fmt(v) : v));
});

const css = `
.l8 *{box-sizing:border-box}
.l8 .pane{background:#fff;border-radius:20px;box-shadow:var(--shadow);padding:14px 16px;overflow:hidden}
.l8 .lbl{font:600 13px/1.2 var(--font);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-bottom:8px}
.l8 .bub{border-radius:16px;padding:8px 12px;font-size:15px;line-height:1.36;margin-bottom:8px;transition:opacity .35s}
.l8 .bub.u{background:var(--card);margin-left:18px;border-bottom-right-radius:5px}
.l8 .bub.a{background:var(--after-soft);margin-right:10px;border-bottom-left-radius:5px}
.l8 table{border-collapse:collapse;width:100%}
.l8 td,.l8 th{padding:4px 8px;font-size:15px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
.l8 th{font:500 13px/1.2 var(--font);color:var(--ink-3)}
.l8 td.n{font-family:var(--mono);font-size:14px;white-space:nowrap}
.l8 .row{transition:background .25s,opacity .25s}
.l8 .row.on{background:var(--after-soft)}
.l8 .row.off{opacity:.35}
.l8 .chip{display:inline-block;font:500 13px/1 var(--font);padding:6px 9px;border-radius:999px;background:var(--card);color:var(--ink-2);margin:0 4px 4px 0}
.l8 .chip.a{background:var(--after-soft);color:var(--after)} .l8 .chip.b{background:var(--before-soft);color:var(--before)} .l8 .chip.g{background:var(--gold-soft);color:var(--gold)}
.l8 .sq{display:inline-block;width:46px;height:34px;border-radius:9px;cursor:pointer;transition:transform .15s;font:500 12px/34px var(--font);text-align:center;color:var(--ink-2)}
.l8 .sq:hover{transform:scale(1.08)}
.l8 .ok{background:#cfe3ff}.l8 .no{background:#ffd9c6}.l8 .ne{background:#c4511f;color:#fff}.l8 .rl{background:#e1e5ea}
.l8 .mono{font:400 14px/1.45 var(--mono);white-space:pre-wrap;word-break:break-word;color:var(--ink-2)}
.l8 .bar{height:24px;border-radius:8px;transition:width .7s cubic-bezier(.3,.7,.2,1)}
`;
if (!document.getElementById('l8css')) { const s = document.createElement('style'); s.id = 'l8css'; s.textContent = css; document.head.appendChild(s); }
const box = (el, html) => { el.classList.add('l8'); el.innerHTML = html; return el; };
const ctl = (labels, on, cb) => { const d = document.createElement('div'); d.className = 'ctl'; labels.forEach(([k, t]) => { const b = document.createElement('button'); b.textContent = t; b.dataset.k = k; if (k === on) b.classList.add('on'); b.onclick = (e) => { e.stopPropagation(); d.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b)); cb(k); }; d.appendChild(b); }); return d; };
const slider = (n, cb, label = 'Step') => { const d = document.createElement('div'); d.className = 'ctl'; d.innerHTML = `<span>${label}</span><input type="range" min="0" max="${n - 1}" value="${n - 1}"><output></output>`; const i = d.querySelector('input'), o = d.querySelector('output'); const f = () => { o.textContent = `${+i.value + 1} of ${n}`; cb(+i.value); }; i.oninput = f; i.addEventListener('click', (e) => e.stopPropagation()); setTimeout(f, 0); return d; };

/* ---------- cold open: the whistle order's replies in four ports (logs/fw_*.json, T04) ---------- */
FIGS.coldfour = (el) => {
  const keys = ['ours', 'openai_agents', 'adk', 'langgraph'];
  box(el, `<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;height:100%">${keys.map((k, i) => {
    const t = FD.t04[k];
    return `<div class="pane step-in" data-i="${i}" style="opacity:0;transition:opacity .4s"><div class="lbl">Port ${String.fromCharCode(65 + i)} · ${t.calls} model calls</div>${t.turns.map((x) => `<div class="bub u">${esc(x.kind === 'ask' ? 'Order 3,000 standard whistles …' : x.user)}</div><div class="bub a">${esc(md(x.agent).slice(0, 150))}…</div>`).join('')}</div>`;
  }).join('')}</div>`);
  const panes = el.querySelectorAll('.pane');
  return { step(k) { panes.forEach((p) => (p.style.opacity = 1)); } };
};

/* ---------- one idea, four names ---------- */
FIGS.rosetta = (el) => {
  const rows = [
    ['System prompt', 'SYSTEM_FULL', 'Agent(instructions=…)', 'LlmAgent(instruction=…)', 'create_react_agent(prompt=…)'],
    ['Tool registry', 'tb.schemas()', 'mcp_servers=[…], @function_tool', 'tools=[McpToolset(…)]', 'MultiServerMCPClient.get_tools()'],
    ['The loop', 'Harness._loop', 'Runner.run', 'Runner.run_async', 'graph: agent ⇄ tools'],
    ['Step cap', 'max_steps = 12', 'max_turns = 12', 'RunConfig(max_llm_calls=12)', 'recursion_limit = 25'],
    ['History', 'messages + save()/load()', 'SQLiteSession', 'SessionService', 'checkpointer + thread_id'],
    ['Trace', 'h.trace', 'spans (TracingProcessor)', 'Events (+ OpenTelemetry)', 'stream of updates'],
    ['Checks before a write', 'guard, verify, pause parts', 'input / output / tool guardrails', 'before_tool / after_model callbacks', 'a node or an edge condition'],
    ['Another agent takes over', 'not built', 'handoffs=[…]', 'sub_agents=[…]', 'a node per agent'],
  ];
  const cols = ['Ours (L5)', 'Agents SDK', 'Google ADK', 'LangGraph'];
  box(el, `<table><tr><th style="width:170px">Piece</th>${cols.map((c, i) => `<th data-c="${i}">${c}</th>`).join('')}</tr>${rows.map((r) => `<tr>${r.map((c, i) => i ? `<td data-c="${i - 1}" class="mono" style="font-size:15px;transition:all .25s">${esc(c)}</td>` : `<td style="font-weight:550;font-size:16px">${c}</td>`).join('')}</tr>`).join('')}</table>`);
  const pick = (c) => el.querySelectorAll('[data-c]').forEach((t) => { const on = c === 'all' || +t.dataset.c === +c; t.style.opacity = on ? 1 : 0.25; t.style.background = on && c !== 'all' ? 'var(--after-soft)' : ''; });
  el.appendChild(ctl([['all', 'All'], ['0', 'Ours'], ['1', 'Agents SDK'], ['2', 'ADK'], ['3', 'LangGraph']], 'all', pick));
  return { step() {} };
};

/* ---------- the Agents SDK's spans for T04, with a scrubber ---------- */
FIGS.spans = (el) => {
  const sp = FD.spans_t04.filter((s, i) => s.type !== 'custom' && !(s.type === 'mcp_tools' && FD.spans_t04.findIndex((x) => x.type === 'mcp_tools') !== i));
  const col = { generation: 'var(--after)', function: 'var(--gold)', mcp_tools: 'var(--ink-3)', agent: 'var(--ink)' };
  box(el, `<div class="pane" style="height:620px;overflow:hidden"><div class="lbl">Spans, Kavita's two messages · logs/fw_openai_agents.json T04 · tool-list spans after the first hidden</div><table id="sp" style="font-size:14px">${sp.map((s, i) => `<tr class="row" data-i="${i}"><td class="n" style="width:30px">${i + 1}</td><td style="width:60px;color:var(--ink-3)">msg ${s.turn}</td><td style="width:120px;color:${col[s.type] || 'var(--ink)'};font-weight:550">${s.type}</td><td style="width:200px">${esc(s.name || '')}</td><td class="mono" style="font-size:13px">${s.type === 'generation' ? `${fmt(s.tok)} tokens in → ${esc(s.detail)}` : esc(s.detail || '')}</td></tr>`).join('')}</table></div>`);
  const rows = el.querySelectorAll('.row');
  el.appendChild(slider(sp.length, (v) => rows.forEach((r, i) => { r.classList.toggle('on', i === v); r.classList.toggle('off', i > v); }), 'Span'));
  return { step() {} };
};

FIGS.spancount = (el) => {
  const c = {}; FD.spans_t04.forEach((s) => { if (s.type !== 'custom') c[s.type] = (c[s.type] || 0) + 1; });
  box(el, `<div class="pane" style="height:100%"><div class="lbl">Spans recorded for the whistle order (T04, two messages)</div><div style="display:flex;gap:26px;margin-top:10px">${Object.entries(c).map(([k, v]) => `<div><div class="num" style="font-size:44px">${v}</div><div class="small">${k}</div></div>`).join('')}</div><p class="tiny" style="margin-top:10px">One <code>mcp_tools</code> span per model turn: the tool list is served from the cache after the first fetch.</p></div>`);
  return { step() {} };
};

/* ---------- desks: who answered each message (logs/desks.json) ---------- */
FIGS.desks = (el) => {
  const rows = FD.desks.sdk;
  box(el, `<div class="pane" style="height:100%"><div class="lbl">Agents SDK · front desk, three desks · logs/desks.json</div>${rows.map((m, i) => `<div class="row" style="padding:8px 4px;border-bottom:1px solid var(--rule)"><div style="font-size:15px"><b>${m.who === 'NDESAI' ? 'Neha' : 'Kavita'}:</b> ${esc(m.msg)}</div><div style="margin-top:5px">${m.by ? `<span class="chip a">answered by ${esc(m.by)}</span>` : '<span class="chip b">stopped by the input guardrail</span>'}${m.spans.filter((s) => s.startsWith('handoff')).map((s) => `<span class="chip">${esc(s.replace('handoff:', 'handoff → '))}</span>`).join('')}${m.spans.filter((s) => s.startsWith('function')).length ? `<span class="chip g">${m.spans.filter((s) => s.startsWith('function')).length} tool calls</span>` : ''}</div><div style="font-size:14px;color:var(--ink-2);margin-top:4px">${esc(md(m.reply).slice(0, 130))}</div></div>`).join('')}<p class="tiny" style="margin-top:8px">Run cost ${inr(FD.desks.inr)} (both frameworks' desks).</p></div>`);
  return { step() {} };
};

/* ---------- ADK events for T04 ---------- */
FIGS.events = (el) => {
  const ev = FD.events_t04;
  box(el, `<div class="pane" style="height:600px;overflow:hidden"><div class="lbl">ADK Events, Kavita's two messages · logs/fw_adk.json T04</div><table>${ev.map((e, i) => `<tr class="row" data-i="${i}"><td class="n" style="width:30px">${i + 1}</td><td style="width:60px;color:var(--ink-3)">msg ${e.turn}</td><td style="width:170px">${e.calls.length ? '<b class="a">model: call tools</b>' : e.results.length ? '<b class="g">tool results</b>' : '<b>model: words</b>'}</td><td class="mono" style="font-size:13px">${esc(e.calls.join(', ') || e.results.join(', ') || md(e.text).slice(0, 80))}${e.usage ? ` <span style="color:var(--ink-3)">· ${fmt(e.usage.in)} in</span>` : ''}</td></tr>`).join('')}</table></div>`);
  const rows = el.querySelectorAll('.row');
  el.appendChild(slider(ev.length, (v) => rows.forEach((r, i) => { r.classList.toggle('on', i === v); r.classList.toggle('off', i > v); }), 'Event'));
  return { step() {} };
};

FIGS.adkadded = (el) => { el.textContent = (FD.shapes.adk_added || ['not yet measured']).map((l) => l.length > 160 ? l.slice(0, 157) + '…' : l).join('\n\n'); return { step() {} }; };

/* ---------- what each framework sends: bytes and tokens of the first request (T03) ---------- */
FIGS.wire = (el) => {
  const k = ['openai_agents', 'adk', 'langgraph'];
  const sh = FD.shapes;
  const mx = { tools_bytes: Math.max(...k.map((x) => sh[x].tools_bytes)), system_bytes: Math.max(...k.map((x) => sh[x].system_bytes)), tin: Math.max(...k.map((x) => sh[x].tin[0])) };
  const bar = (v, m, c) => `<div style="display:flex;align-items:center;gap:10px"><div class="bar" style="width:${(380 * v) / m}px;background:${c}"></div><span class="mono">${fmt(v)}</span></div>`;
  const block = (title, key, get) => `<div style="margin-bottom:22px"><div class="lbl">${title}</div>${k.map((x) => `<div style="display:grid;grid-template-columns:180px 1fr;align-items:center;margin-bottom:6px"><span style="font-size:16px">${FWN[x]}</span>${bar(get(x), mx[key], x === 'adk' ? 'linear-gradient(90deg,#c4511f,#eb6834)' : 'linear-gradient(90deg,#1b5fb5,#5a9cf5)')}</div>`).join('')}</div>`;
  box(el, `<div class="pane" style="height:100%">${block('Tool schemas sent with every call, bytes', 'tools_bytes', (x) => sh[x].tools_bytes)}${block('System prompt as sent, bytes', 'system_bytes', (x) => sh[x].system_bytes)}${block('Input tokens of the first model call', 'tin', (x) => sh[x].tin[0])}${sh.po_schema ? `<p class="small">One tool, <code>create_purchase_order</code>: ${fmt(sh.po_schema.oa_bytes)} bytes from the Agents SDK, ${fmt(sh.po_schema.adk_bytes)} from ADK.</p>` : ''}<p class="tiny">Task T03, first request each framework sent, as the meter received it. logs/fw_*.json request_shapes; fw_*_replay.json first_request.</p></div>`);
  return { step() {} };
};

FIGS.adkdesks = (el) => {
  box(el, `<div class="pane" style="height:100%"><div class="lbl">ADK · front_desk with three sub-agents · logs/desks.json</div>${FD.desks.adk.map((m) => `<div style="padding:9px 2px;border-bottom:1px solid var(--rule)"><div style="font-size:15px"><b>${m.who === 'NDESAI' ? 'Neha' : 'Kavita'}:</b> ${esc(m.msg)}</div><div style="margin-top:5px"><span class="chip a">answered by ${esc(m.by || '—')}</span>${(m.transfers || []).map((t) => `<span class="chip">transfer_to_agent → ${esc(t)}</span>`).join('')}</div></div>`).join('')}<p class="small" style="margin-top:10px">The same routing as the Agents SDK's handoffs. "Yes, go ahead." stayed with the purchasing desk, with no transfer.</p></div>`);
  return { step() {} };
};

/* ---------- LangGraph node steps, T04 ---------- */
FIGS.lgsteps = (el) => {
  const st = FD.steps_t04;
  box(el, `<div class="pane" style="height:620px;overflow:hidden"><div class="lbl">LangGraph updates, Kavita's two messages · logs/fw_langgraph.json T04</div><table>${st.map((s, i) => `<tr class="row"><td class="n" style="width:30px">${i + 1}</td><td style="width:60px;color:var(--ink-3)">msg ${s.turn}</td><td style="width:110px"><span class="chip ${s.node === 'agent' ? 'a' : 'g'}">${s.node}</span></td><td class="mono" style="font-size:13px">${esc(s.node === 'agent' ? (s.calls.length ? 'asks for ' + s.calls.join(', ') : md(s.text).slice(0, 80)) : 'ran ' + s.results.join(', '))}</td></tr>`).join('')}</table></div>`);
  const rows = el.querySelectorAll('.row');
  el.appendChild(slider(st.length, (v) => rows.forEach((r, i) => { r.classList.toggle('on', i === v); r.classList.toggle('off', i > v); }), 'Update'));
  return { step() {} };
};

/* ---------- free loop vs control graph ---------- */
FIGS.lgcompare = (el) => {
  const a = S.langgraph.run1, b = S.control.run1;
  const rows = [['Tasks passed', a.passed, b.passed, (v) => v + ' / 12'], ['Never-event tasks', a.ne, b.ne, fmt], ['Model calls', a.calls, b.calls, fmt], ['Input tokens', a.tin, b.tin, fmt], ['Billed, 12 tasks', a.inr, b.inr, inr], ['Lines of code', S.langgraph.loc, S.control.loc, fmt]];
  box(el, `<div class="pane" style="height:100%"><div class="lbl">Run 1 · logs/fw_langgraph.json, fw_control.json, loc.json</div><table style="margin-top:8px"><tr><th></th><th>Prebuilt agent (free loop)</th><th>Control graph (L5)</th></tr>${rows.map(([k, x, y, f]) => `<tr><td style="font-size:18px">${k}</td><td class="n" style="font-size:20px">${f(x)}</td><td class="n" style="font-size:20px;color:var(--after)">${f(y)}</td></tr>`).join('')}</table>${S.control.run2 ? `<p class="small" style="margin-top:14px">Run 2: prebuilt agent ${S.langgraph.run2.passed} / 12 with ${S.langgraph.run2.ne} never-event task; control graph ${S.control.run2.passed} / 12 with ${S.control.run2.ne}.</p>` : ''}</div>`);
  return { step() {} };
};

/* ---------- the scoreboard ---------- */
FIGS.board = (el) => {
  const M = { passed: ['Tasks passed (of 12)', (v) => v, 12], ne: ['Tasks with a never-event', fmt, null], tin: ['Input tokens, 12 tasks', fmt, null], inr: ['Billed by OpenRouter, 12 tasks', inr, null], model_s: ['Model seconds, 12 tasks', (v) => fmt(Math.round(v)), null], loc: ['Lines of code you write', fmt, null] };
  box(el, `<div class="pane" style="height:640px"><div class="lbl" id="bt"></div><div id="bars"></div><p class="tiny" style="margin-top:6px">Bar: run 1. Dot: run 2 (not run for every setup). gemini-3.8-flash via OpenRouter, 28 Oct 2026.</p></div>`);
  const draw = (m) => {
    el.querySelector('#bt').textContent = M[m][0];
    const get = (s, r) => (m === 'loc' ? s.loc : (s[r] ? s[r][m] : null));
    const mx = M[m][2] || Math.max(...FD.setups.map((s) => Math.max(get(s, 'run1') || 0, get(s, 'run2') || 0))) || 1;
    el.querySelector('#bars').innerHTML = FD.setups.map((s) => {
      const v1 = get(s, 'run1'), v2 = m === 'loc' ? null : get(s, 'run2');
      return `<div style="display:grid;grid-template-columns:230px 1fr;align-items:center;margin:14px 0"><span style="font-size:17px">${esc(s.label)}</span><div style="position:relative;height:30px"><div class="bar" style="position:absolute;top:3px;width:${(560 * v1) / mx}px;background:${s.key === 'control' ? 'linear-gradient(90deg,#138a60,#3fbf8f)' : 'linear-gradient(90deg,#1b5fb5,#5a9cf5)'}"></div>${v2 != null ? `<div title="run 2" style="position:absolute;top:7px;left:${(560 * v2) / mx - 8}px;width:16px;height:16px;border-radius:50%;background:#fff;border:3px solid var(--before)"></div>` : ''}<span class="mono" style="position:absolute;left:${(560 * Math.max(v1, v2 || 0)) / mx + 14}px;top:5px">${M[m][1](v1)}${v2 != null ? ` · ${M[m][1](v2)}` : ''}</span></div></div>`;
    }).join('');
  };
  el.appendChild(ctl(Object.entries(M).map(([k, v]) => [k, v[0].split(',')[0].replace(' (of 12)', '').replace('Billed by OpenRouter', 'Rupees')]), 'passed', draw));
  draw('passed');
  return { step() {} };
};

/* ---------- every task ---------- */
FIGS.grid = (el) => {
  let run = 'run1';
  box(el, `<div class="pane" style="height:560px"><div id="g"></div></div><div class="pane" id="gd" style="margin-top:10px;height:96px;font-size:15px;color:var(--ink-2)">Click a square.</div>`);
  const draw = () => {
    el.querySelector('#g').innerHTML = `<table><tr><th style="width:190px"></th>${FD.tasks.map((t) => `<th style="text-align:center" title="${esc(t.name)}">${t.id}</th>`).join('')}</tr>${FD.setups.map((s) => {
      const rows = FD.grid[s.key][run];
      return `<tr><td style="font-size:15px">${esc(s.short)}</td>${FD.tasks.map((t) => { const r = rows ? rows.find((x) => x.id === t.id) : null; if (!r) return '<td style="text-align:center;color:var(--ink-3);font-size:13px">–</td>'; const c = r.ne ? 'ne' : r.crash ? 'rl' : r.p ? 'ok' : 'no'; return `<td style="text-align:center;padding:5px 2px"><span class="sq ${c}" data-s="${s.key}" data-t="${t.id}">${r.calls}</span></td>`; }).join('')}</tr>`;
    }).join('')}</table><p class="tiny" style="margin-top:8px">The number in a square is its model calls. ${run === 'run2' ? 'Run 2: tasks that hit OpenRouter’s rate limit were re-run on the same cassette (logs/fw_*_rep2b_*.json).' : 'Run 1.'}</p>`;
    el.querySelectorAll('.sq').forEach((q) => (q.onclick = (e) => { e.stopPropagation(); const r = FD.grid[q.dataset.s][run].find((x) => x.id === q.dataset.t); const t = FD.tasks.find((x) => x.id === q.dataset.t); el.querySelector('#gd').innerHTML = `<b>${esc(S[q.dataset.s].label)} · ${t.id} ${esc(t.name)}</b> · ${r.p ? 'pass' : 'fail'}${r.ne ? ' · never-event' : ''} · ${r.calls} model calls · ${inr(r.inr)}<br>${esc(r.note)}<br><i>Kavita was told:</i> ${esc(md(r.last).slice(0, 170))}`; }));
  };
  el.appendChild(ctl([['run1', 'Run 1'], ['run2', 'Run 2']], 'run1', (k) => { run = k; draw(); }));
  draw();
  return { step() {} };
};

/* ---------- never-events across both runs ---------- */
FIGS.neplate = (el) => {
  const rows = FD.setups.map((s) => ({ s, r1: s.run1.ne_text, r2: s.run2 ? s.run2.ne_text : null }));
  const who = (t) => (/SS-VAD/.test(t) ? 'Shakti Seals, no certificate' : /KR-KOL/.test(t) ? 'Kaveri Rubber, expired' : t);
  box(el, `<div class="pane" style="height:100%"><div class="lbl">NE3 · food-contact order without a valid certificate · both runs</div><table>${rows.map(({ s, r1, r2 }) => `<tr><td style="font-size:16px;width:220px">${esc(s.label)}</td><td>${r1.length ? r1.map((t) => `<span class="chip b">run 1: ${esc(who(t))}</span>`).join('') : '<span class="chip">run 1: none</span>'}${r2 == null ? '<span class="chip" style="opacity:.6">run 2: not run</span>' : r2.length ? r2.map((t) => `<span class="chip b">run 2: ${esc(who(t))}</span>`).join('') : '<span class="chip a">run 2: none</span>'}</td></tr>`).join('')}</table><p class="tiny" style="margin-top:10px">Never-events are checked by code on Bahi's order table (bahi.scenarios.check), not on the reply.</p></div>`);
  return { step() {} };
};

/* ---------- traces side by side, T04 ---------- */
FIGS.side = (el) => {
  const keys = ['ours', 'openai_agents', 'adk', 'langgraph'];
  const n = Math.max(...keys.map((k) => FD.t04[k].tools.length));
  box(el, `<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;height:630px">${keys.map((k) => `<div class="pane"><div class="lbl">${FWN[k]}<br>${FD.t04[k].calls} model calls · ${inr(FD.t04[k].inr)}</div>${FD.t04[k].tools.map((t, i) => `<div class="row" data-i="${i}" style="padding:4px 6px;border-radius:10px;margin-bottom:2px"><div style="font:500 15px/1.2 var(--font);color:${/^create|^release/.test(t.name) ? 'var(--after)' : 'var(--ink)'}">${i + 1}. ${t.name}</div><div class="mono" style="font-size:12px;line-height:1.3">msg ${t.turn} · ${esc(t.args.replace(/"/g, '').slice(0, 44))}</div></div>`).join('')}</div>`).join('')}</div>`);
  el.appendChild(slider(n, (v) => el.querySelectorAll('.row').forEach((r) => { const i = +r.dataset.i; r.classList.toggle('on', i === v); r.classList.toggle('off', i > v); }), 'Tool call'));
  return { step() {} };
};

/* ---------- the framework's own time: replay wall seconds ---------- */
FIGS.overhead = (el) => {
  const ks = Object.keys(FD.overhead);
  const mx = Math.max(...ks.map((k) => FD.overhead[k].wall));
  const ids = FD.overhead[ks[0]].tasks;
  const live = ks.map((k) => S[k] ? S[k].run1.model_s : 0);
  box(el, `<div class="pane" style="height:100%"><div class="lbl">Wall seconds in replay, tasks ${ids.join(', ')} (one at a time)</div>${ks.map((k) => `<div style="display:grid;grid-template-columns:220px 1fr;align-items:center;margin:16px 0"><span style="font-size:16px">${esc(S[k] ? S[k].short : k)}</span><div style="display:flex;align-items:center;gap:10px"><div class="bar" style="width:${Math.max(3, (440 * FD.overhead[k].wall) / mx)}px;background:${k === 'adk' ? 'linear-gradient(90deg,#c4511f,#eb6834)' : 'linear-gradient(90deg,#1b5fb5,#5a9cf5)'}"></div><span class="mono">${FD.overhead[k].wall} s</span></div></div>`).join('')}<p class="small" style="margin-top:10px">For scale: in the live run the model itself took ${fmt(Math.round(S.openai_agents.run1.model_s))} s over all twelve tasks on the Agents SDK.</p><p class="tiny">logs/fw_*_replay.json (wall_seconds), logs/adk_time.json. Tasks that diverged in replay are left out for every setup alike.</p></div>`);
  return { step() {} };
};

/* ---------- one question, four models (logs/gateway.json) ---------- */
FIGS.models = (el) => {
  const ms = FD.gateway.models;
  box(el, `<div class="pane" style="height:100%"><div class="lbl">Through one API · logs/gateway.json</div><p style="font-size:15px;color:var(--ink-2);margin:0 0 10px">${esc(FD.gateway.q)}</p><table><tr><th>Model</th><th>Right?</th><th>Words out (tokens)</th><th>Seconds</th><th>₹ for this answer</th></tr>${ms.map((m) => `<tr><td class="n">${esc(m.model)}</td><td>${m.correct ? '<span class="chip a">yes</span>' : '<span class="chip b">no</span>'}</td><td class="n">${fmt(m.tokens_out)}</td><td class="n">${m.seconds}</td><td class="n">₹${Number(m.cost_inr).toFixed(4)}</td></tr>`).join('')}</table>${ms.map((m) => `<p style="font-size:13.5px;color:var(--ink-2);margin:8px 0 0"><b>${esc(m.model.split('/')[1])}:</b> ${esc(md(m.answer).slice(0, 150))}</p>`).join('')}</div>`);
  return { step() {} };
};

FIGS.router = (el) => {
  box(el, `<div class="pane" style="height:100%"><div class="lbl">In our run · LiteLLM Router through the meter</div><table><tr><th>Case</th><th>Answered by</th><th>Seconds</th><th>₹</th></tr>${FD.gateway.router.map((r) => `<tr><td>${esc(r.case)}</td><td class="n">${esc((r.answered_by || r.error || '').replace('openrouter:', ''))}</td><td class="n">${r.seconds ?? ''}</td><td class="n">${r.cost_inr != null ? inr(r.cost_inr) : ''}</td></tr>`).join('')}</table><p class="tiny" style="margin-top:8px">The fallback also answered ₹2,80,840 and "above the limit". The forced failure happens inside LiteLLM, so it costs nothing.</p></div>`);
  return { step() {} };
};

/* ---------- Ollama on a Modal L4 (logs/fw_ours_ollama_*.json) ---------- */
FIGS.ollama = (el) => {
  const o = FD.ollama || [];
  const ref = S.ours.run1;
  if (!o.length) { box(el, '<div class="ours" style="position:static">Not yet measured.</div>'); return { step() {} }; }
  box(el, `<div class="pane" style="height:100%"><div class="lbl">Our harness, twelve tasks · local models vs gemini-3.8-flash</div><table><tr><th>Model</th><th>Passed</th><th>Never-event tasks</th><th>Model calls</th><th>Seconds per call</th><th>₹ to a model API</th></tr><tr><td class="n">gemini-3.8-flash (cloud)</td><td class="n">${ref.passed} / 12</td><td class="n">${ref.ne}</td><td class="n">${ref.calls}</td><td class="n">${(ref.model_s / ref.calls).toFixed(1)}</td><td class="n">${inr(ref.inr)}</td></tr>${o.map((m) => `<tr><td class="n">${esc(m.model)} (Ollama, L4)</td><td class="n">${m.passed} / 12</td><td class="n">${m.ne}</td><td class="n">${fmt(m.calls)}</td><td class="n">${m.s_per_call}</td><td class="n">₹0</td></tr>`).join('')}</table><div style="margin-top:14px">${o.map((m) => `<div style="margin-bottom:8px"><span class="mono">${esc(m.model)}</span> ${m.per_task.map((r) => `<span class="sq ${r.ne ? 'ne' : r.crash ? 'rl' : r.p ? 'ok' : 'no'}" title="${r.id}" style="width:38px;height:26px;line-height:26px;cursor:default">${r.id.slice(1)}</span>`).join(' ')}</div>`).join('')}</div><p class="tiny" style="margin-top:6px">Ollama 0.40.3, OLLAMA_CONTEXT_LENGTH 32768, one NVIDIA L4 on Modal. Seconds per call include waiting behind six parallel tasks. One run each. Our first Ollama run had <code>search_policy</code> broken by a missing package in the image; it is kept in logs/superseded/ and not used.</p></div>`);
  return { step() {} };
};
})();
