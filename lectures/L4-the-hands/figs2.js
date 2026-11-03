/* Live figures for Lecture 4 · The Hands, part 2: sections 6–10 and the films. Data: window.L4 (figdata.js). */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const L = () => window.L4 || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const stop = (e) => e.stopPropagation();
const get = (path) => { let v = L(); for (const k of path.split('.')) v = v == null ? v : v[k]; return v; };
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k));
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(L4 data)</span><div>${what}</div><div class="todo-s">Fills in from figdata.js (gen_figdata.py).</div></div>`; return { step() {} }; };
const pj = (o, n = 2) => JSON.stringify(o, null, n);
const cj = (o) => JSON.stringify(o);
const short = (s, n) => { s = typeof s === 'string' ? s : cj(s); return s.length > n ? s.slice(0, n - 1) + '…' : s; };
const args = (a) => Object.entries(a || {}).map(([k, v]) => `${k}: ${typeof v === 'string' ? v : cj(v)}`).join(', ');
const pct = (p) => (100 * p).toFixed(p === 1 ? 0 : 1) + '%';
const KIND = { system: 'system prompt', tools: 'tool definitions', user: 'Emma', call: 'tool calls', result: 'tool results', reply: 'replies' };

/* ======================= 6 · what Claude Code says when it connects ======================= */
FIGS.ccwire = (el) => {
  const C = get('mcp.claude_client_initialize'), M = get('mcp.lines'), F = get('claude.findings'); if (!C || !M) return need(el, 'Claude Code’s handshake.');
  el.innerHTML = `<div class="md"><div class="md-c" data-k="0"><span class="rt-h">→ Claude Code’s initialize (captured on the pipe)</span><pre>${esc(pj(C.params))}</pre></div>
    <div class="md-c" data-k="1"><span class="rt-h">← our server answers</span><pre>${esc(pj({ protocolVersion: M[1].msg.result.protocolVersion, serverInfo: M[1].msg.result.serverInfo, instructions: M[1].msg.result.instructions }))}</pre>
      <span class="rt-h" data-k="2">then Claude Code asks</span><div class="cc-m" data-k="2">${['notifications/initialized', 'tools/list', 'prompts/list', 'resources/list'].map((m) => `<code>${m}</code>`).join(' ')}</div>
      <p class="small" data-k="3">${esc(F[1])}</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 7 · in our control, and left to Claude ======================= */
FIGS.control = (el) => {
  const C = get('claude'); if (!C) return need(el, 'The comparison.');
  el.innerHTML = `<div class="ctl2"><div class="card af"><span class="tag af">Our harness · Ask Northbridge</span><h3>In our control</h3><ol>${C.in_our_control.map((x, i) => `<li data-k="${i < 3 ? 0 : 1}">${esc(x)}</li>`).join('')}</ol></div>
    <div class="card" data-k="2"><span class="tag nt">Claude’s harness · Claude Code</span><h3>Left to Claude’s orchestration</h3><ol>${C.left_to_claude.map((x) => `<li>${esc(x)}</li>`).join('')}</ol>
    <p class="small">The same MCP server, the same tools, Emma’s same session underneath.</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 7 · one tool on both harnesses ======================= */
FIGS.single2 = (el) => {
  const O = get('ours.single'), C = get('claude.single'); if (!O || !C) return need(el, 'Both single runs.');
  const ot = O.turns[0], c0 = ot.cards[0], ct = C.turns[0];
  const cc = ct.steps.find((s) => s.kind === 'call'), cr = ct.steps.find((s) => s.kind === 'result');
  el.innerHTML = `<div class="s2"><div class="s2-c af" data-k="0"><span class="tag af">Our harness · ${esc(O.model.replace('openrouter:', '').replace('google/', ''))}</span>
      <div class="s2-x"><b>call</b> <code>${esc(c0.tool)}(${esc(args(c0.args))})</code></div><div class="s2-x"><b>result</b> <code>${esc(short(c0.result, 120))}</code></div>
      <div class="s2-rep">${esc(ot.reply).replace(/\n+/g, '<br>')}</div>
      <div class="s2-n"><span><b>${ot.model_calls}</b> model calls</span><span><b>${fmt(ot.tokens_in)}</b> tokens in</span><span><b>${fmt(ot.tokens_out)}</b> out</span><span><b>£${O.summary.cost_gbp_est}</b> est.</span></div></div>
    <div class="s2-c" data-k="1"><span class="tag nt">Claude Code (${esc(C.model)})</span>
      <div class="s2-x"><b>call</b> <code>${esc(cc.tool)}(${esc(args(cc.args))})</code></div><div class="s2-x"><b>result</b> <code>${esc(short(cr.text, 120))}</code></div>
      <div class="s2-rep">${esc(ct.reply).replace(/\n+/g, '<br>')}</div>
      <div class="s2-n"><span><b>${ct.num_turns}</b> model turns</span><span><b>${fmt(C.tokens_in)}</b> tokens in, ${fmt(C.cache_read)} from cache</span><span><b>${fmt(C.tokens_out)}</b> out</span><span><b>$${ct.cost_usd_cumulative.toFixed(4)}</b> as reported</span></div></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 8 · WHAT THE LLM SEES: the context, filling block by block (a real recorded run) =======================
   data-run = single | order_hands. Position p: 0 = empty; 1..n = blocks entered; n+1 = the reply written.
   single: one deck click per block. order_hands: its own slider and Play (the deck does not step it). */
window.L4ctx = window.L4ctx || {};
FIGS.ctx = (el) => {
  const run = el.dataset.run || 'single', R = get('ours.' + run), A = get('anatomy'); if (!R) return need(el, 'The recorded context.');
  const B = R.blocks, n = B.length, steps = R.steps, F = R.final;
  const total = steps[steps.length - 1].prompt_tokens + F.tokens;
  const H = +(el.dataset.stack || 540), sc = H / total;
  const deckSteps = run === 'single';
  const tot = {}; B.forEach((b) => { tot[b.kind] = (tot[b.kind] || 0) + (b.tokens || 0); });
  el.innerHTML = `<div class="cx">
    <div class="cx-top"><span class="cx-call"></span><span class="cx-leg">${Object.keys(KIND).filter((k) => tot[k]).map((k) => `<span><i class="kb-i ${k}"></i>${KIND[k]} ${fmt(tot[k])}</span>`).join('')}</span></div>
    <div class="cx-win"><span class="cx-wh">The context window: everything the model reads</span><div class="cx-stack"></div></div>
    <div class="cx-det"></div>
    <div class="cx-dark"><span class="cx-dh">Never in the context</span>${R.never.map((x) => `<div class="cx-d">${esc(x)}</div>`).join('')}
      ${A && run === 'single' ? `<p class="cx-dn">check_stock made ${A.legacy_calls.length} Ledgerline calls (${fmt(A.sizes.legacy_replies_bytes)} bytes of legacy replies). The model saw only the ${fmt(A.sizes.tool_result_bytes)}-byte result.</p>` : `<p class="cx-dn">${R.summary.tool_calls} tool calls ran ${fmt(R.service_calls)} Ledgerline service calls. The model saw only what each tool returned.</p>`}</div>
    ${deckSteps ? '' : `<div class="ctl cx-ctl"><button class="cx-play">Play</button><input type="range" min="0" max="${n + 1}" value="0"><output></output></div>`}
  </div>`;
  const stack = el.querySelector('.cx-stack'), det = el.querySelector('.cx-det'), call = el.querySelector('.cx-call');
  stack.innerHTML = B.map((b, i) => `<div class="cx-b ${b.kind}" data-i="${i}" style="height:${Math.max(3, (b.tokens || 0) * sc)}px"><span>${(b.tokens || 0) * sc >= 18 ? `${esc(KIND[b.kind])}${b.kind === 'tools' && b.names ? ` (${b.names.length})` : ''} · ${fmt(b.tokens)}` : ''}</span></div>`).join('') +
    `<div class="cx-b out" data-i="${n}" style="height:${Math.max(3, F.tokens * sc)}px"><span>${F.tokens * sc >= 18 ? `the reply it writes · ${fmt(F.tokens)}` : ''}</span></div>`;
  const draw = (p) => {
    p = Math.max(0, Math.min(n + 1, p));
    stack.querySelectorAll('.cx-b').forEach((d) => { const i = +d.dataset.i; d.classList.toggle('fade-hide', i >= p); d.classList.toggle('cur', i === p - 1); });
    const seenBy = p === 0 ? -1 : p > n ? steps.length - 1 : B[p - 1].seen_from;
    const reads = p === 0 ? 0 : B.slice(0, Math.min(p, n)).reduce((s, b) => s + (b.tokens || 0), 0);
    call.innerHTML = p === 0 ? 'Nothing sent yet' : p > n ? `Model call ${steps.length} of ${steps.length} read <b>${fmt(steps[steps.length - 1].prompt_tokens)}</b> tokens and wrote the reply`
      : `Model call ${seenBy + 1} of ${steps.length} · the context so far: <b>${fmt(reads)}</b> tokens${reads === steps[seenBy].prompt_tokens ? ` = its prompt_tokens` : ''}`;
    if (p === 0) { det.innerHTML = `<p class="cx-0">An empty window. ${deckSteps ? 'Click' : 'Press Play'} to add each part, in the order our harness sent it.</p>`; return; }
    const b = p > n ? { kind: 'out', label: 'the reply (output, not context)', tokens: F.tokens, text: F.text, seen_from: steps.length - 1 } : B[p - 1];
    let text = b.text || '';
    if (b.kind === 'call') { try { text = JSON.parse(text).map((c) => `${c.name}(${cj(c.arguments)})`).join('\n'); } catch (e) {} }
    if (b.kind === 'result') { try { text = pj(JSON.parse(text), 1); } catch (e) {} }
    if (b.kind === 'tools') { try { const t = JSON.parse(text); text = t.map((f) => `${f.name}: ${f.description}`).join('\n'); } catch (e) {} }
    det.innerHTML = `<div class="cx-h"><i class="kb-i ${b.kind}"></i><b>${esc(b.label.replace(/ \(model -> our code\)/, ': the model → our code'))}</b><span>${b.tokens == null ? 'counted with the part above' : fmt(b.tokens) + ' tokens'}</span></div>
      <div class="cx-s">${b.kind === 'out' ? 'Written by the last model call' : `First read by model call ${b.seen_from + 1}, and re-sent with every call after it`}${b.note ? ` · <i>${esc(b.note)}</i>` : ''}</div>
      <pre class="cx-t">${esc(text.length > 1250 ? text.slice(0, 1249) + '…' : text)}</pre>`;
  };
  let pos = 0, timer = null;
  const set = (p) => { pos = p; draw(p); const r = el.querySelector('.cx-ctl input'); if (r) { r.value = p; el.querySelector('.cx-ctl output').textContent = `${p} / ${n + 1}`; } };
  if (!deckSteps) {
    const r = el.querySelector('.cx-ctl input'), b = el.querySelector('.cx-play');
    r.oninput = (e) => { stop(e); set(+r.value); }; r.onclick = stop;
    b.onclick = (e) => { stop(e); if (timer) { clearInterval(timer); timer = null; b.textContent = 'Play'; return; } if (pos > n) set(0); b.textContent = 'Pause'; timer = setInterval(() => { if (pos > n) { clearInterval(timer); timer = null; b.textContent = 'Play'; return; } set(pos + 1); }, 900); };
  }
  window.L4ctx[run] = { go: set, n: n + 1 };
  set(0);
  return { step(k) { if (deckSteps) set(k); } };
};

/* ======================= 8 · every call re-sends everything: prompt tokens per model call, by part ======================= */
FIGS.budget = (el) => {
  const R = get('ours.' + (el.dataset.run || 'order_hands')); if (!R) return need(el, 'The recorded run.');
  const B = R.blocks, S = R.steps, max = S[S.length - 1].prompt_tokens, W = 820;
  const kinds = ['system', 'tools', 'user', 'call', 'result', 'reply'];
  const rows = S.map((s, i) => { const by = {}; B.filter((b) => b.seen_from <= i).forEach((b) => { by[b.kind] = (by[b.kind] || 0) + (b.tokens || 0); }); return { s, by }; });
  const sum = S.reduce((a, s) => a + s.prompt_tokens, 0), toolsTok = (B.find((b) => b.kind === 'tools') || {}).tokens || 0;
  el.innerHTML = `<div class="bu">${rows.map(({ s, by }, i) => `<div class="bu-r" data-k="${i < 1 ? 0 : 1}"><span class="bu-l">call ${i + 1}</span><span class="bu-b">${kinds.filter((k) => by[k]).map((k) => `<i class="kb-i ${k}" style="width:${(by[k] / max) * W}px"></i>`).join('')}</span><span class="bu-v">${fmt(s.prompt_tokens)}</span></div>`).join('')}
    <div class="bu-sum" data-k="2">${S.length} calls read <b>${fmt(sum)}</b> tokens in all (the run’s tokens_in: ${fmt(R.summary.tokens_in)}). The ${R.tools_exposed.length} tool definitions alone, sent with every call: ${S.length} × ${fmt(toolsTok)} = <b>${fmt(S.length * toolsTok)}</b> (${Math.round(100 * S.length * toolsTok / sum)}%).</div>
    <div class="cx-leg" style="margin-top:12px">${kinds.map((k) => `<span><i class="kb-i ${k}"></i>${KIND[k]}</span>`).join('')}</div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 9 · what each prompt already tells the model ======================= */
FIGS.codes = (el) => {
  const P = get('prompt_codes'), O = get('ours'); if (!P || !O) return need(el, 'The prompts.');
  const all = P['agent (harness.AGENT, the app)'];
  const rows = [['The app’s agent prompt', P['agent (harness.AGENT, the app)'], O.order], ['Lecture 4’s “hands” prompt', P['hands_l4 (this file)'], O.order_hands]];
  el.innerHTML = `<table class="t cd"><tr><th>System prompt</th>${all.map((c) => `<th>${esc(c)}</th>`).join('')}<th class="n">Tool calls</th><th class="n">Tokens in</th></tr>
    ${rows.map(([n, has, r], i) => `<tr data-k="${i}"><td>${n}<br><small>${fmt(r.blocks[0].tokens)} tokens · “${esc(short(r.turns[0].user, 60))}”</small></td>${all.map((c) => `<td class="cd-x">${has.includes(c) ? '●' : '·'}</td>`).join('')}<td class="n"><b>${r.summary.tool_calls}</b></td><td class="n">${fmt(r.summary.tokens_in)}</td></tr>`).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 9 · Emma's order on both harnesses, turn by turn ======================= */
FIGS.orch = (el) => {
  const O = get('ours.order_hands'), C = get('claude.order_hands'); if (!O || !C) return need(el, 'Both order runs.');
  const chip = (t, a, ok, extra = '') => `<span class="oc${ok === false ? ' bad' : ''}${extra}"><b>${esc(t)}</b><small>${esc(short(args(a), 46))}</small></span>`;
  const guess = (c) => c.tool === 'create_purchase_request' && c.args.need_by === '2027-02-01';
  const lane = (name, cls, turns) => `<div class="ol ${cls}"><div class="ol-h">${name}</div>${turns.map((t, i) => `<div class="ol-t" data-k="${i + 1}">${t.join('')}</div>`).join('')}</div>`;
  const ours = O.turns.map((t) => t.cards.map((c) => chip(c.tool, c.args, c.ok, (c.tool === 'search_policy' ? ' only' : '') + (guess(c) ? ' slip' : ''))));
  const cc = C.turns.map((t) => t.steps.filter((s) => s.kind === 'call').map((s) => chip(s.tool, s.args, null)));
  el.innerHTML = `<div class="or"><div class="ol hd"><div class="ol-h"></div>${O.turns.map((t, i) => `<div class="ol-t ol-u" data-k="${i + 1}"><span class="ol-n">Emma · turn ${i + 1}</span>${esc(t.user)}</div>`).join('')}</div>
    ${lane(`Our harness<br><small>${O.summary.tool_calls} tool calls</small>`, 'af', ours)}${lane(`Claude Code<br><small>${C.summary.tool_calls} tool calls</small>`, 'cc', cc)}
    <div class="or-k" data-k="4"><span class="oc only"><b>search_policy</b></span> only our harness looked up the rule · <span class="oc slip"><b>a guessed date</b></span> a need-by date nobody gave · both ended with <b>${esc((O.after.pr[0] || {}).pr_no || '')}</b> waiting for Daniel</div></div>`;
  return { step(k) { reveal(el, k); } };
};

FIGS.orchnums = (el) => {
  const O = get('ours.order_hands'), C = get('claude.order_hands'); if (!O || !C) return need(el, 'Both order runs.');
  const last = C.turns[C.turns.length - 1];
  const rows = [
    ['Tool calls', O.summary.tool_calls, C.summary.tool_calls],
    ['Per Emma turn', O.turns.map((t) => t.cards.length).join(' + '), C.turns.map((t) => t.steps.filter((s) => s.kind === 'call').length).join(' + ')],
    ['Model calls (turns)', O.summary.model_calls, C.turns.map((t) => t.num_turns).reduce((a, b) => a + b, 0)],
    ['Tokens in', fmt(O.summary.tokens_in), `${fmt(C.tokens_in)} (${fmt(C.cache_read)} from cache)`],
    ['Tokens out', fmt(O.summary.tokens_out), fmt(C.tokens_out)],
    ['Cost', `£${O.summary.cost_gbp_est} (our estimate)`, `$${last.cost_usd_cumulative.toFixed(4)} (as Claude Code reports)`],
    ['search_policy called', O.summary.sequence.filter((s) => s === 'search_policy').length, C.summary.tool_sequence.filter((s) => s === 'search_policy').length],
    ['Model errors we logged', O.errors.length, (get('claude.compare_hands.claude_code.observed_model_errors') || []).length],
    ['Outcome', `${(O.after.pr[0] || {}).pr_no}, waiting for Daniel`, last.reply.match(/PR\/\d+\/\d+/) ? `${last.reply.match(/PR\/\d+\/\d+/)[0]}, waiting for approval` : ''],
  ];
  el.innerHTML = `<table class="t on2"><tr><th></th><th>Our harness (${esc(O.model.replace('openrouter:google/', ''))})</th><th>Claude Code (${esc(C.model)})</th></tr>${rows.map((r, i) => `<tr data-k="${i < 3 ? 0 : i < 6 ? 1 : 2}"><td>${r[0]}</td><td>${esc(r[1])}</td><td>${esc(r[2])}</td></tr>`).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 9 · an error the tool caught, and the model recovered from ======================= */
FIGS.recover = (el) => {
  const O = get('ours.order'), C = get('claude.order'); if (!O || !C) return need(el, 'The order runs.');
  const cards = O.turns[0].cards, bad = cards.find((c) => c.ok === false);
  const res = JSON.parse(bad.result);
  el.innerHTML = `<div class="rc"><div class="rc-c" data-k="0"><span class="rt-h">Our harness asked</span><pre>${esc(`${bad.tool}(${cj(bad.args)})`)}</pre></div>
    <div class="rc-c leg" data-k="1"><span class="rt-h">The tool answered (ok=false)</span><pre>${esc(pj(res))}</pre></div>
    <div class="rc-c" data-k="2"><span class="rt-h">So it raised a request instead</span><pre>${esc(cards.filter((c) => c.tool === 'create_purchase_request').map((c) => `${c.tool}(${cj(c.args)})`).join('\n'))}</pre>
      <p class="small">Claude Code, on the same prompt: ${esc(C.tool_sequence.join(' → '))}. ${C.tool_errors} tool error, the same recovery.</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 9 · two model errors, as teaching moments ======================= */
FIGS.slips = (el) => {
  const H = get('ours.order_hands'), O = get('ours.order'); if (!H || !O) return need(el, 'The runs.');
  const g = H.turns[0].cards.find((c) => c.args && c.args.need_by === '2027-02-01');
  const v = O.errors[0], rep = O.turns[0].reply;
  el.innerHTML = `<div class="sl"><div class="sl-c" data-k="0"><span class="tag bf">1 · A date nobody gave</span><p>Emma said “for the spring launch run”, no date. The hands prompt says: never guess a code or a number.</p>
      <pre>${esc(`${g.tool}(${cj(g.args)})`)}</pre><p class="small">Logged: ${esc(H.errors[0].error)}. The preview showed the date, and Emma’s next turn gave the real one: 9 November 2026.</p></div>
    <div class="sl-c" data-k="1"><span class="tag bf">2 · “ex. VAT”</span><p>The earlier run, on the app’s prompt. The tool said <code>estimated_value: 273600</code>, which includes VAT. The reply said:</p>
      <pre>${esc(rep.split('\n').find((l) => l.includes('273,600')) || v.reply_excerpt)}</pre><p class="small">Logged: ${esc(v.error)}. Seen once; not in the hands runs or in any Claude Code reply.</p></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 10 · the ten criteria, before and after ======================= */
FIGS.criteria = (el) => {
  const P = get('prod'); if (!P) return need(el, 'The production measurements.');
  const C = Object.fromEntries(P.criteria.map((c) => [c.area, c]));
  const H = get('hosts.hosts');
  const v = {
    Schema: [`${C.Schema.before.with_output_schema}/${C.Schema.before.tools} with output schemas · ${C.Schema.before.output_violations_happy_path} output violation`, `${C.Schema.after.with_output_schema}/${C.Schema.after.tools} · ${C.Schema.after.output_violations_in_fuzzing} violations in ${fmt(C.Schema.after.ok_results_checked_in_fuzzing)} ok results`],
    Reliability: [`${C.Reliability.before.unhandled_or_non_business_pct}% non-business (${C.Reliability.before.by_kind.non_business} of ${fmt(C.Reliability.before.calls)} fuzzed calls)`, `${C.Reliability.after.unhandled_or_non_business_pct}% (0 of ${fmt(C.Reliability.after.calls)})`],
    'LLM usability': ['not measured', Object.entries(H).map(([h, x]) => `${h} ${pct(x.pass_at_1)}`).join(' · ')],
    Latency: [`via MCP p50 ${C.Latency.before.via_mcp_overhead_ms.p50} · p95 ${C.Latency.before.via_mcp_overhead_ms.p95} · p99 ${C.Latency.before.via_mcp_overhead_ms.p99} ms`, `p50 ${C.Latency.after.via_mcp_overhead_ms.p50} · p95 ${C.Latency.after.via_mcp_overhead_ms.p95} · p99 ${C.Latency.after.via_mcp_overhead_ms.p99} ms`],
    Payload: [`largest ${fmt(C.Payload.before.max_bytes_at_scale)} bytes · ${C.Payload.before.list_tools_paginating.length}/${C.Payload.before.list_tools.length} list tools paginate`, `largest ${fmt(C.Payload.after.max_bytes_at_scale)} bytes · ${C.Payload.after.list_tools_paginating.length}/${C.Payload.after.list_tools.length} paginate`],
    Idempotency: [`${P.fix.before.lost_reply_then_retry + P.fix.before.retry_with_rewritten_arguments} duplicate postings`, `${P.fix.after.lost_reply_then_retry + P.fix.after.retry_with_rewritten_arguments} duplicates`],
    Timeouts: [`declared on ${C.Timeouts.before.declared}/${C.Timeouts.before.tools} · ${C.Timeouts.before.passed}/${C.Timeouts.before.tested} tests pass`, `declared on ${C.Timeouts.after.declared}/${C.Timeouts.after.tools} · ${C.Timeouts.after.passed}/${C.Timeouts.after.tested} pass`],
    Regression: [`${C.Regression.before.tools_passing}/${C.Regression.before.tools} tools · ${C.Regression.before.write_tools_passing}/${C.Regression.before.write_tools} write tools`, `${C.Regression.after.tools_passing}/${C.Regression.after.tools} tools · ${C.Regression.after.write_tools_passing}/${C.Regression.after.write_tools} write tools`],
    'MCP compliance': ['not measured', `${C['MCP compliance'].after.tools_right_on_every_host} tools right on every host · all 5 accept all 16`],
    'Change management': [`${C['Change management'].before.with_version}/${C['Change management'].before.tools} versioned · ${C['Change management'].before.version_published_over_mcp} published · ${C['Change management'].before.with_release_notes} release notes`, `${C['Change management'].after.version_published_over_mcp} published · ${C['Change management'].after.with_release_notes} with release notes · sign-off open`],
  };
  const mark = (p) => p === true ? '<span class="pf y">pass</span>' : p === false ? '<span class="pf n">fail</span>' : '<span class="pf u">not measured</span>';
  el.innerHTML = `<table class="t cr2"><tr><th>Area</th><th>Threshold</th><th data-k="1">Before · ${esc(P.before_commit)}</th><th data-k="2">After · 16 tools</th></tr>
    ${P.criteria.map((c) => `<tr><td><b>${esc(c.area)}</b></td><td><small>${esc(c.threshold)}</small></td><td data-k="1">${mark(c.pass_before)} <small>${esc(v[c.area][0])}</small></td><td data-k="2">${mark(c.pass_after)} <small>${esc(v[c.area][1])}</small></td></tr>`).join('')}</table>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 10 · find and fix: duplicate postings ======================= */
FIGS.idem = (el) => {
  const I = get('prod.idem'), F = get('prod.fix'); if (!I) return need(el, 'The idempotency test.');
  const Bb = I.before.B_retry_with_rewritten_arguments, Ba = I.after.B_retry_with_rewritten_arguments;
  const cases = Object.keys(Bb).filter((k) => !k.startsWith('_'));
  const row = (name, b, a) => `<tr><td>${esc(name)}</td><td><code>${esc(b.first.args.need_by)}</code> then <code>${esc(b.retry.args.need_by)}</code></td><td class="n" data-k="1"><span class="pf n">${b.documents_made} documents</span></td><td class="n" data-k="3"><span class="pf y">${a.documents_made}${a.retry.already_done ? ' · already_done' : ''}</span></td></tr>`;
  const arows = Object.entries(I.A_before).map(([n, b]) => `<tr><td>${esc(n)}</td><td>reply lost, the same call again</td><td class="n" data-k="2"><span class="pf n">${b.documents_made} documents</span></td><td class="n" data-k="3"><span class="pf y">${(I.A_after[n] || {}).documents_made ?? '?'}</span></td></tr>`).join('');
  el.innerHTML = `<table class="t id"><tr><th>Retried write</th><th>What changed between the two calls</th><th class="n" data-k="1">Before</th><th class="n" data-k="3">After the fix</th></tr>
    ${cases.map((c, i) => `<tbody data-k="${i === 0 ? 0 : 2}">${row(c, Bb[c], Ba[c])}</tbody>`).join('')}<tbody data-k="2">${arows}</tbody></table>
    <div class="id-sum"><span data-k="2">Before: <b class="b">${I.before.duplicates_A_B} duplicate postings</b></span><span data-k="3">After: <b class="g">${I.after.duplicates_A_B}</b></span><span data-k="4">Still open: a deliberate resend of the same call posts twice for ${esc(Object.keys(F.after.where.C).join(' and '))} (${I.after.duplicates_C}). Two equal deliveries can both be real, so these tools say idempotentHint=false.</span></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= 10 · usability per host (30 golden tasks, pass@1) ======================= */
FIGS.hostbars = (el) => {
  const H = get('hosts'); if (!H) return need(el, 'The host matrix.');
  const W = 560;
  el.innerHTML = `<div class="hb">${Object.entries(H.hosts).map(([h, x]) => `<div class="hb-r"><span class="hb-l">${esc(h)}<small>${esc(x.model.replace('openrouter:', '').replace(' (OpenRouter, Anthropic-compatible endpoint)', ''))}</small></span>
      <span class="hb-b"><i class="${x.pass_at_1 >= 0.95 ? 'ok' : 'lo'}" style="width:${x.pass_at_1 * W}px"></i><em style="left:${0.95 * W}px"></em></span><span class="hb-v">${pct(x.pass_at_1)} <small>${x.passed}/${H.tasks}</small></span></div>
      ${x.fails.length ? `<div class="hb-f" data-k="1">${x.fails.map((f) => `${esc(f.id)}: ${esc(f.reason)}`).join(' · ')}</div>` : ''}`).join('')}
    <p class="hb-n">The line is the 95% threshold. Same 16 definitions from tools/list, same task text, temperature 0, first response scored.</p></div>`;
  return { step(k) { reveal(el, k); } };
};

/* ======================= films (from L2: films/<name>.mp4 + .webm + .jpg; never autoplay) ======================= */
FIGS.film = (el) => {
  const n = el.dataset.name, base = 'films/' + n;
  const todo = () => { el.innerHTML = `<div class="todo-card f3"><span class="todo-k">TODO(film)</span><div>The narrated film <b>${esc(n)}</b> plays here: ${esc(el.dataset.what || '')}</div><div class="todo-s">Lands as films/${esc(n)}.mp4, .webm and .jpg (films/FILMS.md).</div></div>`; };
  el.innerHTML = `<video class="film" controls preload="metadata" playsinline poster="${base}.jpg"><source src="${base}.webm" type="video/webm"><source src="${base}.mp4" type="video/mp4"></video>
    <div class="ctl film-ctl"><button>Present (full screen)</button></div>`;
  const v = el.querySelector('video'), srcs = [...v.querySelectorAll('source')];
  let failed = 0;
  srcs.forEach((sc) => sc.addEventListener('error', () => { if (++failed === srcs.length) todo(); }));
  ['click', 'keydown', 'touchstart', 'touchend'].forEach((ev) => v.addEventListener(ev, stop));
  el.querySelector('.film-ctl button').onclick = (e) => { stop(e); (v.requestFullscreen || v.webkitRequestFullscreen || (() => {})).call(v); v.play(); };
  return { step() {} };
};

/* Text spans filled from the data: <span data-l4="ours.single.summary.tokens_in" data-f="n"></span>. */
FIGS._fill = () => {
  document.querySelectorAll('[data-l4]').forEach((s) => {
    const v = get(s.dataset.l4);
    if (v == null) { s.innerHTML = '<span class="todo-in">TODO(L4 data)</span>'; return; }
    s.textContent = s.dataset.f === 'n' ? fmt(v) : s.dataset.f === 'pct' ? pct(v) : String(v);
  });
};
})();
