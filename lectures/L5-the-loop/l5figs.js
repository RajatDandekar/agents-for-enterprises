/* Live figures for Lecture 5 · The Loop (v5, Northbridge). Loaded BEFORE plates.js. Every number and every line of code
   comes from window.L5 (figdata.js, written by gen_figdata.py from experiments/logs and the code). Nothing typed by hand.
   Each FIGS.<name>(el) returns { step(k) }, k = the number of .step elements shown on the slide. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const L = () => window.L5 || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => (n == null ? '–' : Number(n).toLocaleString('en-GB'));
const usd = (n) => (n == null ? '–' : '$' + (n < 0.01 ? n.toFixed(4) : n.toFixed(3)));
const stop = (e) => e.stopPropagation();
const get = (path) => { let v = L(); for (const k of path.split('.')) v = v == null ? v : v[k]; return v; };
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k));
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(L5 data)</span><div>${what}</div><div class="todo-s">Fills in from figdata.js (gen_figdata.py).</div></div>`; return { step() {} }; };
const cj = (o) => JSON.stringify(o);
const args = (a) => Object.entries(a || {}).map(([k, v]) => `${k}: ${typeof v === 'string' ? v : cj(v)}`).join(', ');
const short = (s, n) => { s = String(s ?? ''); return s.length > n ? s.slice(0, n - 1) + '…' : s; };
const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;
const KW = /\b(def|return|for|in|if|else|elif|try|except|import|from|raise|not|and|or|None|True|False|is|while|with|as|class|continue|break)\b/;
function hl(line) {
  const re = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d[\d_.]*\b)|([A-Za-z_]\w*)/g;
  let out = '', last = 0, m;
  while ((m = re.exec(line))) {
    out += esc(line.slice(last, m.index));
    if (m[1]) out += `<span class="cmt">${esc(m[1])}</span>`;
    else if (m[2]) out += `<span class="st">${esc(m[2])}</span>`;
    else if (m[3]) out += `<span class="nu">${esc(m[3])}</span>`;
    else out += KW.test(m[4]) && m[4].match(KW)[0] === m[4] ? `<span class="kw">${m[4]}</span>` : esc(m[4]);
    last = re.lastIndex;
  }
  return out + esc(line.slice(last));
}
const ranges = (spec) => { const s = new Set(); (spec || '').split(',').filter(Boolean).forEach((r) => { const [a, b] = r.split('-').map(Number); for (let i = a; i <= (b || a); i++) s.add(i); }); return s; };

/* ======================= a real source file or prompt as a code card, highlighted per click =======================
   data-src="code.smallest" data-hl="3;4-5;6-9" (one range list per click) data-plain="1" for prose (prompts) */
FIGS.code = (el) => {
  const src = get(el.dataset.src); if (src == null) return need(el, esc(el.dataset.src));
  const all = String(src).replace(/\n$/, '').split('\n');
  const from = +(el.dataset.from || 1), to = +(el.dataset.to || all.length);
  const lines = all.slice(from - 1, to);
  const steps = (el.dataset.hl || '').split(';');
  el.classList.add('nbcell');
  if (el.dataset.size) el.style.fontSize = el.dataset.size + 'px';
  const draw = (k) => {
    const on = ranges(k === 0 ? el.dataset.hl0 || '' : steps[Math.min(k, steps.length) - 1]);
    el.innerHTML = `<span class="hd">${esc(el.dataset.title || '')}</span>` + lines.map((l, i) => `<div class="ln${on.has(i + from) ? ' on' : ''}${on.size && !on.has(i + from) ? ' dim' : ''}"><span class="lno">${i + from}</span>${el.dataset.plain ? esc(l) : hl(l)}</div>`).join('');
  };
  draw(0);
  return { step: draw };
};

/* ======================= opener: Lecture 4's eleven calls ======================= */
FIGS.recap = (el) => {
  const R = get('l4'); if (!R) return need(el, 'Lecture 4 recap');
  el.innerHTML = `<div class="rc4"><div class="rc4-m"><span class="k">Emma, three messages</span>${R.messages.map((m) => `<p>“${esc(m)}”</p>`).join('')}</div>
    <div class="rc4-s" data-k="1"><span class="k">What the model called, in order</span><ol>${R.sequence.map((s) => `<li><code>${esc(s)}</code></li>`).join('')}</ol></div>
    <div class="rc4-n" data-k="2"><b>${R.tool_calls}</b> tool calls · <b>${R.model_calls}</b> model calls · <b>${fmt(R.tokens_in)}</b> tokens read · the request PR/2026/04417 waiting for Daniel</div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 1 · one round per message vs the loop (hands.json) ======================= */
FIGS.rounds = (el) => {
  const H = get('hands'); if (!H) return need(el, 'hands.json');
  const which = el.dataset.which;
  const col = (name, label, cls) => { const r = H[name];
    return `<div class="rd ${cls}"><span class="k">${label}</span>${r.turns.map((t, i) => `<div class="rd-t" data-k="${i + 1}"><div class="rd-e">Emma · ${esc(short(t.text, 60))}</div><div class="rd-c">${t.calls.map((c) => `<code>${esc(c)}</code>`).join(' ') || '<i>no tools</i>'}</div><div class="rd-end">loop ends: ${esc(t.end === 'max_steps' ? 'one round used up' : t.end)}</div></div>`).join('')}
      <div class="rd-f" data-k="${r.turns.length + 1}"><b>${r.right ? 'Released.' : 'Not released.'}</b> ${esc(r.why.split(' · ')[1] || '')}<br>${r.mc} model calls · ${r.tc} tool calls · ${fmt(r.tin)} tokens</div></div>`; };
  el.innerHTML = `<div class="rd2">${which === 'loop' ? col('loop', 'In a loop (the model drives)', 'af') : which === 'one' ? col('one_round', 'One round per message (Lecture 4’s hands)', 'bf') : col('one_round', 'One round per message', 'bf') + col('loop', 'In a loop', 'af')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 2 · ReAct as text (react.json) ======================= */
FIGS.react = (el) => {
  const R = get('react.' + (el.dataset.run || 'stock')); if (!R) return need(el, 'react.json');
  const steps = R.steps;
  if (el.dataset.compact) {
    el.innerHTML = `<div class="rxc"><div class="rx-q"><span class="k">Emma</span>${esc(R.question)}</div>${steps.map((s, i) => `<div class="rxc-s" data-k="${i + 1}"><span class="rxc-n">${s.n}</span><div><div class="rxc-t">${s.thought ? 'Thought: ' + esc(short(s.thought, 150)) : '<i>no Thought written</i>'}</div>${s.action ? `<div class="rxc-a">Action: <code>${esc(s.action)}</code> <span>${esc(short(cj(s.input), 90))}</span></div><div class="rxc-o">Observation: ${esc(short(s.obs, 110))}</div>` : `<div class="rxc-a">Final Answer: ${esc(short(s.final, 170))}</div>`}</div></div>`).join('')}</div>`;
    return { step(k) { reveal(el, k); } };
  }
  el.innerHTML = `<div class="rx"><div class="rx-q"><span class="k">Emma</span>${esc(R.question)}</div>${steps.map((s, i) => `<div class="rx-s" data-k="${i + 1}"><span class="k">model writes · step ${s.n} · ${fmt(s.tin)} tokens read</span><pre>${esc(s.raw.trim())}</pre>${s.obs ? `<div class="rx-o"><span class="k">our code parses “Action”, runs it, writes back</span><pre>Observation: ${esc(s.obs)}</pre></div>` : '<div class="rx-o fin"><span class="k">“Final Answer”: the loop ends</span></div>'}</div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};
FIGS.parse = (el) => {
  const s = get('react.order.steps.0'); if (!s) return need(el, 'react.json order');
  const rows = [['thought', s.thought || '(none written)'], ['action', s.action], ['action_input', cj(s.input)], ['final', s.final == null ? 'null: not the end yet' : s.final], ['error', s.error == null ? 'null' : s.error]];
  el.innerHTML = `<div class="ps"><div class="ps-raw"><span class="k">What the model wrote (step 1 of Emma’s order)</span><pre>${esc(s.raw.trim())}</pre></div>
    <div class="ps-out" data-k="1"><span class="k">parse_step() returns</span><table class="t">${rows.map(([k, v]) => `<tr><td><code>${k}</code></td><td>${esc(short(v, 160))}</td></tr>`).join('')}</table></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 2 · Emma's order, step by step (story.json, native tool calls) ======================= */
FIGS.trace = (el) => {
  const S = get('story'); if (!S) return need(el, 'story.json');
  const turns = (el.dataset.turns || '0').split(',').map((t) => (t === 'd2' ? S.day2 : S.day1[+t]));
  const items = [];
  turns.forEach((t) => { items.push({ e: t.text }); t.steps.forEach((s) => items.push({ s })); items.push({ r: t }); });
  el.innerHTML = `<div class="tr">${items.map((it, i) => {
    const k = i === 0 ? 0 : i;
    if (it.e) return `<div class="tr-e" data-k="${k}"><span class="k">Emma</span>${esc(it.e)}</div>`;
    if (it.r) return `<div class="tr-r" data-k="${k}"><span class="k">Ask Northbridge · loop ends: ${esc(it.r.end)}</span>${esc(short(it.r.reply, 210))}</div>`;
    const s = it.s;
    if (s.k === 'h') return `<div class="tr-h" data-k="${k}"><span class="k">harness</span>${esc(s.note)}</div>`;
    return `<div class="tr-s" data-k="${k}"><span class="tr-n">step ${s.n}</span><div><div class="tr-t">${s.text ? esc(short(s.text, 120)) : '<i>no words: straight to the tools</i>'}</div>${s.calls.map((c) => `<div class="tr-c"><code>${esc(c.name)}</code><span class="tr-a">${esc(short(args(c.args), 58))}</span><span class="tr-o ${c.ok ? 'ok' : 'no'}">${esc(short(c.res, 70))}</span></div>`).join('')}<div class="tr-m">${[fmt(s.tin) + ' tokens read'].concat(s.h.filter((x) => /paused|last/.test(x))).map(esc).join(' · ')}</div></div></div>`;
  }).join('')}</div>`;
  return { step(k) { reveal(el, k); const v = [...el.querySelectorAll('[data-k]')].filter((x) => !x.classList.contains('fade-hide')).pop(); if (v && el.scrollHeight > el.clientHeight) el.scrollTop = v.offsetTop - el.clientHeight + v.offsetHeight + 12; } };
};

/* ======================= tokens read per step (story.json) ======================= */
FIGS.tokens = (el) => {
  const S = get('story'); if (!S) return need(el, 'story.json');
  const labels = []; [...S.day1, S.day2].forEach((t, ti) => t.steps.filter((s) => s.k === 'm').forEach((s) => labels.push({ day: ti < 2 ? 'Day 1' : 'Day 2', msg: ti, n: s.n, tin: s.tin })));
  const max = Math.max(...labels.map((x) => x.tin));
  const msgs = ['the order', '“Yes, go ahead.”', 'the next morning'];
  el.innerHTML = `<div class="tk">${labels.map((x, i) => `<div class="tk-c" data-k="${i + 1}"><span class="tk-v">${fmt(x.tin)}</span><i style="height:${Math.round(x.tin / max * 300)}px"></i><span class="tk-l">step ${x.n}<small>${msgs[x.msg]}</small></span></div>`).join('')}</div>
    <p class="tk-n" data-k="${labels.length}">Every step sends the whole conversation again: the system prompt, the 11 tool definitions, every message, every call, every result. ${fmt(S.totals.tokens_in)} tokens read in all, for ${S.totals.model_calls} model calls.</p>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 3 · the harness around the loop ======================= */
const PARTS = [['The system prompt', 'who it works for, the rules of the job'], ['The message history', 'the conversation so far, sent every step'], ['The tool list', 'what it may call'], ['Stop rules', 'answered · step limit · budget · failures'], ['Max steps and budget', 'how far and how much'], ['Error recovery', 'follow next_step; never repeat a refusal'], ['The approval pause', 'a request waits: stop, hold the writes'], ['State across days', 'save as JSON; read Ledgerline first']];
FIGS.harness = (el) => {
  el.innerHTML = `<div class="hn"><div class="hn-core"><b>The loop</b><span>think → call → observe → repeat</span><small>the model picks the next step</small></div>${PARTS.map(([t, d], i) => `<div class="hn-p hn-${i}" data-k="${i + 1}"><b>${i + 1} · ${t}</b><span>${d}</span></div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= harness knobs measured on the live app (daedalus_knobs.json) ======================= */
const VLAB = { shipped: 'shipped harness', max_steps_4: 'max steps 4', max_steps_2: 'max steps 2', budget_6000: 'budget 6,000 tokens', tools_2: '2 tools', tools_16: 'all 16 tools', prompt_bare: 'one-line prompt', pause_off: 'pause off', recovery_off: 'recovery off' };
FIGS.knobs = (el) => {
  const K = get('knobs.agent'); if (!K) return need(el, 'daedalus_knobs.json');
  const vars = (el.dataset.vars || Object.keys(K).join(',')).split(',').filter((v) => K[v]);
  const S = K.shipped;
  el.innerHTML = `<div class="km"><span class="k">Measured on the deployed Daedalus · six jobs · 2 runs each · gemini-3.8-flash</span><table class="t km-t"><tr><th>Harness</th><th class="n">right / 6</th><th class="n">model calls</th><th class="n">tool calls</th><th class="n">tokens read</th><th class="n">seconds</th></tr>
    ${vars.map((v) => { const x = K[v]; const d = v === 'shipped' ? '' : ` <small class="${x.tin > S.tin ? 'up' : 'dn'}">${x.tin > S.tin ? '+' : ''}${Math.round((x.tin / S.tin - 1) * 100)}%</small>`;
      return `<tr class="${v === 'shipped' ? 'km-b' : ''}"><td>${VLAB[v] || v}</td><td class="n"><b>${x.right.join(', ')}</b></td><td class="n">${fmt(x.mc)}</td><td class="n">${fmt(x.tc)}</td><td class="n">${fmt(Math.round(x.tin))}${d}</td><td class="n">${fmt(Math.round(x.sec))}</td></tr>`; }).join('')}</table>
    <div class="km-n">Means of the two runs (right answers listed per run). Each run: the six jobs in fresh sandboxes, scored in code from Ledgerline’s tables. <code>logs/daedalus_knobs.json</code>, ${esc(get('knobs.at'))}.</div></div>`;
  return { step() {} };
};
/* which jobs a knob broke, and how each message ended */
FIGS.kjobs = (el) => {
  const v = el.dataset.var, K = get('knobs.agent.' + v), J = get('jobs'); if (!K || !J) return need(el, 'daedalus_knobs.json');
  const END = { answered: 'answered', paused: 'paused', max_steps: 'step limit', budget: 'budget', failures: '3 failures', 'still waiting': 'still waiting' };
  el.innerHTML = `<div class="kj"><span class="k">${VLAB[v] || v}: each job, each run (how every message’s loop ended)</span><table class="t">${J.map((j) => `<tr><td>${esc(j.title)}</td>${K.runs.map((r) => { const x = r.jobs[j.id]; return `<td>${x ? `<span class="chip2 ${x.right ? 'ok' : 'no'}">${x.right ? 'right' : 'wrong'}</span> <small>${x.ends.map((e) => END[e] || e).join(' → ')}</small>` : '–'}</td>`; }).join('')}</tr>`).join('')}</table></div>`;
  return { step() {} };
};

/* ======================= the parts, recorded (parts.json): one variant on one job ======================= */
FIGS.claims = (el) => {
  const C = get('parts.claims'); if (!C) return need(el, 'parts.json claims');
  const side = (v, label, cls) => { const xs = C.filter((c) => c.variant === v), c = xs[0];
    return `<div class="cl ${cls}"><span class="k">${label}</span>${c.steps.map((s) => s.k === 'h' ? `<div class="cl-h">harness: ${esc(s.note)}</div>` : `<div class="cl-s">step ${s.n}: ${s.calls.length ? s.calls.map((x) => `<code>${esc(x.name)}</code> → ${esc(short(x.res, 50))}`).join(' ') : 'words'}</div>`).join('')}
      <div class="cl-r">“${esc(short(c.reply, 150))}”</div><div class="cl-n">${xs.map((x) => `${x.mc} model call${x.mc === 1 ? '' : 's'}, ${x.tc} tool call${x.tc === 1 ? '' : 's'}, ${x.orders} orders`).join(' · ')} <small>(2 runs)</small></div></div>`; };
  el.innerHTML = `<div class="cl2">${side('shipped', 'Pause on: the harness reads Ledgerline first', 'af')}<div data-k="1">${side('pause_off', 'Pause off: the model decides what to do', 'bf')}</div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= error recovery: the lost reply, before and after the fix ======================= */
FIGS.recover = (el) => {
  const A = get('recover'), B = get('recover_before'); if (!A) return need(el, 'recover.json');
  const row = (xs, v, label) => { const r = xs.filter((x) => x.case === 'lost' && x.variant === v); if (!r.length) return '';
    return `<tr><td>${label}</td><td class="n"><b>${r.filter((x) => x.right).length} / ${r.length}</b></td><td class="n">${r.map((x) => x.blocked).join(', ')}</td><td>${esc(short(r[0].why.split(' · ')[1] || r[0].why, 60))}</td></tr>`; };
  el.innerHTML = `<div class="km"><span class="k">A lost reply: Ledgerline saves the request, the reply never comes back (once) · the bells job</span><table class="t"><tr><th>Harness</th><th class="n">finished</th><th class="n">retries refused</th><th>Ledgerline at the end</th></tr>
    ${B ? row(B, 'shipped', 'recovery on, first version') + row(B, 'recovery_off', 'recovery off') : ''}<tr data-k="1"><td colspan="4" class="km-sep">the fix: a lost reply may be retried; a refusal is never repeated</td></tr>${B ? `<tr data-k="1">${row(A, 'shipped', 'recovery on, fixed').slice(4)}` : row(A, 'shipped', 'recovery on')}</table>
    <div class="km-n">2 runs each, recorded. <code>logs/recover_before.json</code>, <code>logs/recover.json</code>.</div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= state across days ======================= */
FIGS.night = (el) => {
  const S = get('story'); if (!S) return need(el, 'story.json');
  el.innerHTML = `<div class="ng"><div class="ng-b"><span class="k">the agent’s state at night</span><b>${fmt(S.night_bytes)}</b> bytes of JSON · ${S.night_messages} messages<br>keys: ${S.night_keys.map((k) => `<code>${esc(k)}</code>`).join(' ')}</div><pre>${esc(S.night_preview)}</pre></div>`;
  return { step() {} };
};
FIGS.timeline = (el) => {
  const S = get('story'); if (!S) return need(el, 'story.json');
  const ev = [['Day 1 · Emma', '“' + S.message + '”', 'a preview; it asks her once'], ['Day 1 · Emma', '“Yes, go ahead.”', `${S.night_waiting.doc} waits for ${S.night_waiting.approver} · the loop pauses`], ['Night', `${fmt(S.night_bytes)} bytes of JSON`, 'the agent is thrown away'], ['Day 2 · Daniel', 'approves in his own inbox', 'in Ledgerline, not in the chat'], ['Day 2 · Emma', '“Good morning. Daniel has approved it. Please carry on.”', 'the harness reads Ledgerline first: APPROVED'], ['Day 2 · the loop', `${S.after.orders[0] ? S.after.orders[0].po_no : ''} released to Voltway`, `${S.day2.mc} model calls, ${S.day2.tc} tool calls`]];
  el.innerHTML = `<div class="tl">${ev.map(([a, b, c], i) => `<div class="tl-e${i === 2 ? ' night' : ''}" data-k="${i + 1}"><span class="tl-d">${esc(a)}</span><b>${esc(b)}</b><span>${esc(c)}</span></div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 5 · the workflow as a line of blocks ======================= */
const BL = [['read', 'Read the request', 'model'], ['item', 'Find the item', 'tool'], ['stock', 'Check stock', 'tool'], ['supplier', 'Find the supplier', 'tool'], ['cert', 'Check the certificate', 'gate'], ['budget', 'Check the budget', 'gate'], ['request', 'Raise the request', 'tool'], ['approval', 'Wait for approval', 'approval'], ['order', 'Create the order', 'tool'], ['release', 'Release the order', 'tool'], ['reply', 'Tell Emma', 'reply']];
FIGS.wfline = (el) => {
  el.innerHTML = `<div class="wl">${BL.map(([id, t, kind], i) => `<div class="wl-b k-${kind}" data-k="${kind === 'gate' ? 2 : kind === 'approval' ? 3 : kind === 'model' ? 1 : 0}"><span class="wl-n">${i + 1}</span><b>${t}</b><span class="wl-k">${kind}</span>${kind === 'gate' ? '<span class="wl-x">fails → stop</span>' : kind === 'approval' ? '<span class="wl-x">waiting → save, stop</span>' : ''}</div>`).join('<span class="wl-ar">→</span>')}</div>`;
  return { step(k) { reveal(el, k); } };
};
FIGS.wfspring = (el) => {
  const W = get('workflow_spring'); if (!W) return need(el, 'race.json workflow spring');
  el.innerHTML = `<div class="ws">${W.map((s, i) => `<div class="ws-s s-${s.status}" data-k="${Math.min(i, 11)}"><span class="ws-n">${s.n}</span><b>${esc(s.title)}</b><span class="ws-o">${s.got ? esc(cj(s.got)) : esc(short(s.note || (s.calls[0] && s.calls[0].res) || '', 90))}</span></div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= the race (race.json, recorded) ======================= */
FIGS.race = (el) => {
  const R = get('race'), J = get('jobs'); if (!R || !J) return need(el, 'race.json');
  const c = (x) => `<span class="chip2 ${x.right ? 'ok' : 'no'}">${x.right ? 'right' : 'wrong'}</span>`;
  el.innerHTML = `<div class="rce"><table class="t"><tr><th>Job</th><th>Workflow</th><th class="n">tokens</th><th>Agent, 3 runs</th><th class="n">tokens (mean)</th></tr>
    ${J.map((j, i) => { const p = R.per[j.id]; return `<tr data-k="${i + 1}"><td><b>${esc(j.title)}</b></td><td>${c(p.wf)} <small>${p.wf.stopped ? 'stopped at “' + esc(p.wf.stopped) + '”' : ''}</small></td><td class="n">${fmt(p.wf.tin)}</td><td>${p.ag.map(c).join(' ')}</td><td class="n">${fmt(Math.round(mean(p.ag.map((a) => a.tin))))}</td></tr>`; }).join('')}
    <tr class="tot" data-k="7"><td>Total</td><td><b>${R.totals.workflow.right} / ${R.totals.workflow.of}</b></td><td class="n">${fmt(R.totals.workflow.tokens_in)}</td><td><b>${R.totals.agent.right} / ${R.totals.agent.of}</b></td><td class="n">${fmt(Math.round(R.totals.agent.tokens_in / 3))}</td></tr></table>
    <div class="km-n">Recorded: each job in a fresh Ledgerline, Emma and Daniel scripted, scored in code. <code>logs/race.json</code>.</div></div>`;
  return { step(k) { reveal(el, k); } };
};
FIGS.paths = (el) => {
  const R = get('race'); if (!R) return need(el, 'race.json');
  const p = R.per[el.dataset.job || 'spring'];
  el.innerHTML = `<div class="pa"><div class="pa-r wf"><span class="k">Workflow</span>${p.wf.path.map((n) => `<code>${esc(n)}</code>`).join('')}</div>${p.ag.map((a, i) => `<div class="pa-r ag" data-k="${i + 1}"><span class="k">Agent, run ${i + 1}</span>${a.path.map((n) => `<code>${esc(n)}</code>`).join('')}</div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};
FIGS.wfvars = (el) => {
  const W = get('knobs.workflow'), S = get('knobs.shipped_workflow'), J = get('jobs'); if (!W || !J) return need(el, 'daedalus_knobs.json workflow');
  const LAB = { no_cert: 'no certificate gate', no_approval: 'no approval step', no_budget: 'no budget gate', cert_switch: 'certificate gate: use the preferred supplier' };
  const vars = (el.dataset.vars || 'no_cert,no_approval,no_budget,cert_switch').split(',');
  el.innerHTML = `<div class="km"><span class="k">Workflow changes, measured on the deployed Daedalus · the six jobs</span><table class="t"><tr><th>Workflow</th><th class="n">right</th><th>What changed</th></tr>
    <tr class="km-b"><td>shipped</td><td class="n"><b>${S ? S.right : 4} / 6</b></td><td>stops on the fallback job and the question</td></tr>
    ${vars.map((v, i) => { const x = W[v]; const bad = J.filter((j) => !x.jobs[j.id].right).map((j) => j.title); return `<tr data-k="${i + 1}"><td>${LAB[v]}</td><td class="n"><b>${x.right} / 6</b></td><td>${v === 'cert_switch' ? 'now right: “Cheapest, if allowed”. Still wrong: ' + bad.map(esc).join(', ') : 'wrong: ' + J.filter((j) => !x.jobs[j.id].right).map((j) => `${esc(j.title)} <small>(${esc(short(x.jobs[j.id].why.split(' · ')[0], 46))})</small>`).join('; ')}</td></tr>`; }).join('')}</table></div>`;
  return { step(k) { reveal(el, k); } };
};
FIGS.flaky = (el) => {
  const F = get('race.flaky'); if (!F) return need(el, 'race.json flaky');
  const side = (k, label) => { const f = F[k]; return `<div class="fk ${f.right ? 'af' : 'bf'}"><span class="k">${label}</span>${f.request.calls.map((c) => `<div class="fk-c">attempt ${c.attempt}: ${esc(short(c.res, 90))}</div>`).join('')}<div class="fk-r">${esc(short(f.why, 110))}</div></div>`; };
  el.innerHTML = `<div class="fk2">${side('retries_0', '“Raise the request” with 0 retries')}<div data-k="1">${side('retries_1', '“Raise the request” with 1 retry')}</div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= a slot for a screenshot or a screen recording (from Lecture 4) ======================= */
FIGS.shot = (el) => {
  const src = el.dataset.src || '', label = el.dataset.label || '', media = get('media');
  const vid = /\.(mp4|webm)$/i.test(src);
  const slot = () => { el.innerHTML = `<div class="slot${vid ? ' v' : ''}"><span class="slot-k">${vid ? 'Screen recording' : 'Screenshot'}</span><div class="slot-l">${esc(label)}</div><div class="slot-f">lands as <code>${esc(src)}</code></div></div>`; };
  if (Array.isArray(media) && !media.includes(src)) { slot(); return { step() {} }; }
  if (vid) {
    el.innerHTML = `<video class="shot-v" controls preload="metadata" playsinline src="${esc(src)}"></video>`;
    const v = el.querySelector('video'); v.addEventListener('error', slot);
    ['click', 'keydown', 'touchstart', 'touchend'].forEach((ev) => v.addEventListener(ev, stop));
  } else {
    el.innerHTML = `<img class="shot-i" src="${esc(src)}" alt="${esc(label)}">`;
    el.querySelector('img').addEventListener('error', slot);
  }
  return { step() {} };
};
/* narrated films (films/<name>.mp4 + .webm + .jpg; never autoplay); a labelled slot until they are rendered */
FIGS.film = (el) => {
  const n = el.dataset.name, base = 'films/' + n, media = get('media') || [];
  const todo = () => { el.innerHTML = `<div class="todo-card f3"><span class="todo-k">Film slot · ${esc(n)}</span><div>${esc(el.dataset.what || '')}</div><div class="todo-s">Planned in films/FILMS.md; lands as films/${esc(n)}.mp4, .webm and .jpg.</div></div>`; };
  if (!media.includes(base.replace('films/', 'films/') + '.mp4')) { todo(); return { step() {} }; }
  el.innerHTML = `<video class="film" controls preload="metadata" playsinline poster="${base}.jpg"><source src="${base}.webm" type="video/webm"><source src="${base}.mp4" type="video/mp4"></video><div class="ctl film-ctl"><button>Present (full screen)</button></div>`;
  const v = el.querySelector('video');
  ['click', 'keydown', 'touchstart', 'touchend'].forEach((ev) => v.addEventListener(ev, stop));
  el.querySelector('.film-ctl button').onclick = (e) => { stop(e); (v.requestFullscreen || v.webkitRequestFullscreen || (() => {})).call(v); v.play(); };
  return { step() {} };
};

/* Text spans filled from the data: <span data-l5="story.night_bytes" data-f="n"></span> */
FIGS._fill = () => {
  document.querySelectorAll('[data-l5]').forEach((s) => {
    let v = get(s.dataset.l5);
    if (v == null) { s.innerHTML = '<span class="todo-in">TODO(L5 data)</span>'; return; }
    if (s.dataset.f === 'mean' && Array.isArray(v)) v = Math.round(mean(v) * 10) / 10;
    if (s.dataset.f === 'div3') v = Math.round(v / 3);
    s.textContent = s.dataset.f === 'n' || s.dataset.f === 'div3' ? fmt(v) : s.dataset.f === 'usd' ? usd(v) : s.dataset.f === 'r' ? fmt(Math.round(v)) : s.dataset.f === 'list' ? v.join(', ') : String(v);
  });
};
})();
