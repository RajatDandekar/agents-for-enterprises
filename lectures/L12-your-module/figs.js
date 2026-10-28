/* Lecture 12 · Your Module: Demo Day (was Lecture 8 before v3.1). Live figures; every number comes from window.FD (figdata.js, built by gen_figdata.py). */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const FD = window.FD || {};
const inr = (x) => '₹' + Math.round(x).toLocaleString('en-IN');
const inr2 = (x) => '₹' + Number(x).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const num = (x) => Math.round(x).toLocaleString('en-IN');
const esc = (s) => String(s ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const get = (p) => p.split('.').reduce((o, k) => (o == null ? o : o[k]), FD);
const html = (el, s) => { el.innerHTML = s; return el; };
const stop = (e) => e.stopPropagation();
const PERSON = { KJOSHI: 'Kavita', RMEHTA: 'Rohit', NDESAI: 'Neha' };
const LCOL = { L1: '#6b6e76', L2: '#7a5af5', L3: '#138a60', L4: '#0b57d0', L5: '#2a78d6', L6: '#9a6b1f', L7: '#0f7a4f' };

document.querySelectorAll('[data-fd]').forEach((e) => {
  let v;
  try { v = e.dataset.fd.startsWith('=') ? Function('FD', 'return ' + e.dataset.fd.slice(1))(FD) : get(e.dataset.fd); } catch (err) { v = undefined; }
  const f = e.dataset.fmt;
  e.textContent = v == null ? 'not yet measured' : f === 'inr' ? inr(v) : f === 'inr2' ? inr2(v) : f === 'int' ? num(v) : String(v);
});

/* Fig: Kavita's order through every piece, turn by turn (three people, one Rasoi) */
FIGS.finalScrub = (el) => {
  const T = (FD.final && FD.final.turns) || [];
  let i = 0;
  const draw = () => {
    const t = T[i] || { steps: [] };
    const tools = t.steps.filter((s) => s.k === 'tool');
    const models = t.steps.filter((s) => s.k === 'model');
    html(el, `<div class="ctl" style="margin:0 0 12px"><button data-d="-1">←</button><input type="range" min="0" max="${T.length - 1}" value="${i}"><button data-d="1">→</button><output>message ${i + 1} of ${T.length}</output></div>
      <div style="display:grid;grid-template-columns:350px 1fr;gap:16px">
        <div style="font-size:15.5px;line-height:1.35">${T.map((x, j) => `<div data-j="${j}" style="cursor:pointer;padding:5px 9px;border-radius:10px;margin-bottom:2px;${j === i ? 'background:var(--after-soft)' : ''}"><b style="color:${x.user === 'KJOSHI' ? 'var(--after)' : x.user === 'RMEHTA' ? 'var(--before)' : 'var(--gold)'}">${PERSON[x.user]}</b> ${esc(x.text.slice(0, 44))}${x.text.length > 44 ? '…' : ''}</div>`).join('')}</div>
        <div class="card" style="padding:14px 18px;overflow:hidden">
          <div class="small" style="margin-bottom:8px"><b>${PERSON[t.user]}</b>, in ${PERSON[t.user]}'s own session · ${models.length} model call${models.length === 1 ? '' : 's'} · ${num(t.tokens)} tokens (L2) · ${inr2(t.inr)}</div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px">${tools.map((s) => `<span style="display:inline-flex;gap:6px;align-items:center;background:#fff;border-radius:999px;padding:6px 12px;font-size:15px"><b style="color:${LCOL[s.piece[0]]}">${s.piece[0]}</b><code style="background:none">${esc(s.tool)}</code><span style="color:var(--ink-3)">${esc(s.piece[1])}</span></span>`).join('') || '<span class="small">no tool: the model answered from what it already had</span>'}</div>
          <div style="font-size:17.5px;line-height:1.45;white-space:pre-wrap;max-height:330px;overflow:hidden;background:#fff;border-radius:14px;padding:10px 14px">${esc(t.reply)}</div></div></div>`);
    const r = el.querySelector('input'); r.oninput = () => { i = +r.value; draw(); }; r.onclick = stop;
    el.querySelectorAll('button').forEach((b) => b.onclick = (e) => { stop(e); i = Math.max(0, Math.min(T.length - 1, i + +b.dataset.d)); draw(); });
    el.querySelectorAll('[data-j]').forEach((d) => d.onclick = (e) => { stop(e); i = +d.dataset.j; draw(); });
  };
  draw();
  return { step() {} };
};

/* Fig: one turn's real tool call and result (by tool name), for the recap plates */
FIGS.callCard = (el) => {
  const tool = el.dataset.tool, nth = +(el.dataset.nth || 0);
  const calls = ((FD.final && FD.final.turns) || []).flatMap((t) => t.steps.filter((s) => s.k === 'tool' && s.tool === tool));
  const c = calls[nth];
  if (!c) { el.innerHTML = '<p class="small">not yet measured</p>'; return { step() {} }; }
  const lines = Object.entries(c.res).slice(0, +(el.dataset.lines || 9)).map(([k, v]) => {
    let t = typeof v === 'string' ? v : JSON.stringify(v);
    if (t.length > 88) t = t.slice(0, 85) + '…';
    return `  ${k}: ${t}`;
  });
  html(el, `<div class="json" style="white-space:pre-wrap;font-size:14px;line-height:1.45"><b>${esc(tool)}</b>(${esc(JSON.stringify(c.args)).slice(0, 160)})
→ {
${esc(lines.join('\n'))}
  …}</div>`);
  return { step() {} };
};

/* Fig: the eight kits, Before and After */
FIGS.kitExplorer = (el) => {
  const K = FD.kits || [];
  let i = Math.max(0, K.findIndex((k) => k.kit === 'hr_leave'));
  const draw = () => {
    const k = K[i] || { tools: [], test: {} };
    html(el, `<div class="ctl" style="margin:0 0 12px">${K.map((x, j) => `<button data-j="${j}" class="${j === i ? 'on' : ''}">${esc(x.title.split('·')[0].trim())} · ${esc((x.title.split('·')[1] || '').trim())}</button>`).join('')}</div>
      <div style="display:grid;grid-template-columns:1fr 1.25fr;gap:16px">
        <div class="card bf" style="font-size:17px;padding:16px 20px"><span class="tag bf">Before</span>
          <p style="margin:4px 0 10px">${esc(k.before)}</p>
          <p style="margin:0 0 8px"><b>Careful legacy path:</b> ${esc(k.test.before || '')}</p>
          <p style="margin:0 0 8px"><b>The silent outcome:</b> ${esc(k.silent)}</p>
          <p style="margin:0"><b>Demo-day change:</b> ${esc(k.change)}</p></div>
        <div class="card af" style="font-size:17px;padding:16px 20px"><span class="tag af">After</span>
          <p style="margin:4px 0 8px"><i>"${esc(k.after.replace(/^.*?types\s*/i, '').replace(/"/g, ''))}"</i></p>
          <div style="display:grid;grid-template-columns:1fr;gap:4px;margin-bottom:8px">${k.tools.map((t) => `<div style="display:grid;grid-template-columns:210px 1fr 70px;gap:8px;font-size:15px;background:#fff;border-radius:10px;padding:5px 10px"><code style="background:none">${esc(t.name)}</code><span>${esc(t.what)}</span><span style="text-align:right;color:${t.writes ? 'var(--before)' : 'var(--ink-3)'}">${t.writes ? (t.writes === 'np' ? 'write*' : 'write') : 'read'}</span></div>`).join('')}</div>
          <p style="margin:0 0 4px;font-size:15px"><b>Knowledge:</b> its own documents; stale: ${esc(k.stale)}. <b>Workflow:</b> ${esc(k.workflow)}</p>
          <p style="margin:0;font-size:15px"><b>Checked on Modal:</b> reference ${esc(k.test.ref || '')}, naive caught ${esc(k.test.naive || '')}, starter tool ${esc(k.test.tools || '')}</p></div></div>
      <p class="small" style="margin-top:8px">write* = approve, release or sign: no preview; the person's own instruction is the go-ahead.</p>`);
    el.querySelectorAll('button').forEach((b) => b.onclick = (e) => { stop(e); i = +b.dataset.j; draw(); });
  };
  draw();
  return { step() {} };
};

/* Fig: HR leave on Ask Rasoi, four scenarios x three runs */
FIGS.leaveGrid = (el) => {
  const L = FD.leave;
  if (!L) { el.innerHTML = '<div class="ours" style="position:static">The HR leave runs are not yet measured.</div>'; return { step() {} }; }
  const scs = [...new Set(L.rows.map((r) => r.sc))].sort();
  let sel = L.rows.find((r) => r.sc === 1 && r.rep === 1) || L.rows[0];
  const draw = () => {
    html(el, `<table class="t sg"><tr><th>Scenario</th>${[1, 2, 3].map((k) => `<th style="text-align:center">run ${k}</th>`).join('')}</tr>
      ${scs.map((s) => `<tr><td>${s} · ${esc((L.rows.find((r) => r.sc === s) || {}).name)}</td>${[1, 2, 3].map((k) => { const r = L.rows.find((x) => x.sc === s && x.rep === k); return `<td style="text-align:center">${r ? `<span class="chip ${r.ne.length ? 'f' : r.ok ? 'p' : 'f'}" data-s="${s}" data-k="${k}" style="cursor:pointer">${r.ne.length ? 'NE' : r.ok ? 'pass' : 'fail'}</span>` : '-'}</td>`; }).join('')}</tr>`).join('')}</table>
      <div class="card" style="margin-top:12px;font-size:16px;padding:12px 16px"><span class="tag nt">scenario ${sel.sc}, run ${sel.rep} · ${sel.ok ? 'pass' : 'fail'}${sel.notes.length ? ' · ' + esc(sel.notes.join('; ')) : ''}</span>
        ${sel.turns.slice(-2).map((t) => `<p style="margin:6px 0"><b>${esc(sel.sc === 2 ? 'Neha' : 'Kavita')}:</b> ${esc(t.u.slice(0, 140))}</p><p style="margin:0 0 8px;color:var(--ink-2)"><b>Ask Rasoi:</b> ${esc((t.a || '').replace(/\s+/g, ' ').slice(0, 240))}${(t.a || '').length > 240 ? '…' : ''}</p>`).join('')}</div>`);
    el.querySelectorAll('[data-s]').forEach((c) => c.onclick = (e) => { stop(e); sel = L.rows.find((x) => x.sc === +c.dataset.s && x.rep === +c.dataset.k); draw(); });
  };
  draw();
  return { step() {} };
};

/* Fig: inside an eight-minute slot */
FIGS.slot = (el) => {
  const P = window.Plates, W = 1360, H = 230;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const seg = [[0, 1, 'The Before', 'legacy screens, the silent outcome', 'var(--before)'], [1, 3, 'The After', 'one sentence, live; the approver in their own session', 'var(--after)'],
    [3, 5, 'The change', 'where it lives; the hidden test runs', 'var(--gold)'], [5, 8, 'The client', 'three minutes of questions, answered from your logs', '#45474d']];
  const x = (m) => 20 + m / 8 * (W - 40);
  const g = seg.map(([a, b, t, d, c]) => {
    const gg = P.svgEl('g', { style: 'transition:opacity .5s' }, svg);
    P.svgEl('rect', { x: x(a) + 3, y: 40, width: x(b) - x(a) - 6, height: 70, rx: 16, style: `fill:${c};opacity:.9` }, gg);
    P.txt(gg, x(a) + 18, 84, t, 'font:500 22px var(--font);fill:#fff');
    const per = Math.floor((x(b) - x(a) - 12) / 8.2);
    const words = d.split(' '), lines = [''];
    words.forEach((w) => { if ((lines[lines.length - 1] + ' ' + w).trim().length > per) lines.push(w); else lines[lines.length - 1] = (lines[lines.length - 1] + ' ' + w).trim(); });
    lines.forEach((ln, li) => P.txt(gg, x(a) + 6, 140 + li * 21, ln, 'font:15px var(--font);fill:var(--ink-2)'));
    P.txt(gg, x(a) + 6, 26, `${a}:00`, 'font:14px var(--font);fill:var(--ink-3)');
    return gg;
  });
  P.txt(svg, x(8) - 6, 26, '8:00', 'font:14px var(--font);fill:var(--ink-3)', 'end');
  return { step(k) { g.forEach((gg, i) => { gg.style.opacity = i <= k ? 1 : 0.1; }); } };
};

/* Fig: the rubric, out of 100 (rubric.md; v3.1 adds the production stack line) */
FIGS.rubric = (el) => {
  const R = [['Scenario pass rate', 20, 'A5, A6, A7', 'The four kit scenarios replayed on your agent; your A7 suite (4 × 3 runs); A5\'s harness scenarios; A6\'s workflow end states. A never-event zeroes that scenario.'],
    ['Tools', 20, 'A4', 'Activities not services; the six promises in every tool; the lost-reply test; served over MCP; the tool you chose not to write.'],
    ['Route and authority', 15, 'A5, A7', 'The pause resumed on Bahi\'s word; the speaker\'s own session; a guard per never-event; the silent outcome caught.'],
    ['Retrieval', 15, 'A3', 'Your documents indexed and cited; the stale one handled; who may read what.'],
    ['Operations', 10, 'A5, A6, A7', 'The judge beside the checks; one change gated; one failing trace read; safe re-runs; calls, tokens and ₹.'],
    ['Demo-day change', 10, 'L11 → L12', 'The hidden test passes (6); where the change lives, a new case, the gate run (4).'],
    ['Production stack', 10, 'L8–L11', 'Two industry tools from two layers, each wired in and shown working (4); a written reason for each (4); one comparison measured on your own run (2).']];
  const C = ['#0b57d0', '#2a78d6', '#c4511f', '#138a60', '#45474d', '#9a6b1f', '#7a5af5'];
  let sel = 6;
  const draw = () => {
    html(el, `<div style="display:flex;height:64px;border-radius:16px;overflow:hidden;margin-bottom:16px;gap:2px">${R.map((r, i) => `<div data-i="${i}" style="cursor:pointer;width:${r[1]}%;background:${C[i]};opacity:${i === sel ? 1 : 0.55};display:flex;align-items:center;justify-content:center;color:#fff;font:500 18px var(--font)">${r[1]}</div>`).join('')}</div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px">${R.map((r, i) => `<div data-i="${i}" class="card" style="cursor:pointer;padding:12px 16px;font-size:17px;${i === sel ? 'box-shadow:inset 0 0 0 2px ' + C[i] : ''}"><b style="color:${C[i]}">${r[0]} · ${r[1]}</b><br><span class="small" style="font-size:16px">from ${r[2]}</span></div>`).join('')}</div>
      <div class="card af" style="margin-top:14px;font-size:20px"><b>${R[sel][0]}, ${R[sel][1]} points.</b> ${esc(R[sel][3])}</div>`);
    el.querySelectorAll('[data-i]').forEach((d) => d.onclick = (e) => { stop(e); sel = +d.dataset.i; draw(); });
  };
  draw();
  return { step() {} };
};

/* Fig: the production stack menu (rubric.md, line 7): pick two layers, see the tools, what each replaces, the free route */
FIGS.stackMenu = (el) => {
  const M = [['Agent framework', 'L8', 'OpenAI Agents SDK, Google ADK, LangGraph', 'The L5 harness and loop', 'OpenRouter key, or replay'],
    ['Model gateway', 'L8 · L11', 'OpenRouter; LiteLLM with a budget and a fallback; Ollama for a local model', 'The model call in bahi/llm.py', 'LiteLLM and Ollama are open source'],
    ['Protocols', 'L9', 'Your toolbox as a remote MCP server with sign-in, checked in MCP Inspector; an A2A agent card', 'The L4 server in the speaker’s session', 'Open source'],
    ['Workflow', 'L9', 'n8n, self-hosted, running your A6 workflow over MCP', 'The L6 Studio workflow', 'Free self-hosted; Copilot Studio and Agentforce only with recorded output'],
    ['Observability', 'L10', 'Langfuse or Arize Phoenix, over OpenTelemetry GenAI traces', 'The L7 trace you read by hand', 'Open source; LangSmith only with an exported trace'],
    ['Evals', 'L10', 'DeepEval as a CI gate; Ragas on your retrieval; promptfoo red-teaming', 'The L7 suite and gate; the A3 grader', 'Open source'],
    ['Guardrails', 'L11', 'NeMo Guardrails; Llama Guard; a prompt-injection filter', 'A second layer behind your L7 guards', 'NeMo open source; Llama Guard weights are gated'],
    ['Durable execution', 'L11', 'Temporal holding the approval wait', 'The L5 pause and the L7 recovery keys', 'Temporal’s local dev server is free'],
    ['Data stores', 'L11', 'pgvector or Redis for your index or memory', 'The L3 in-memory index', 'Open source'],
    ['Managed platform', 'L11', 'Bedrock AgentCore, Microsoft Foundry', 'The whole runtime', 'Paid: counts only with recorded output']];
  const picked = new Set([4, 5]);
  let sel = 4;
  const draw = () => {
    const m = M[sel];
    html(el, `<div style="display:grid;grid-template-columns:330px 1fr;gap:18px;height:100%">
      <div class="ctl" style="margin:0;flex-direction:column;align-items:stretch;gap:7px">${M.map((r, i) => `<button data-i="${i}" class="${i === sel ? 'on' : ''}" style="text-align:left;display:flex;justify-content:space-between;gap:8px;padding:9px 14px"><span>${picked.has(i) ? '● ' : '○ '}${r[0]}</span><span style="opacity:.7">${r[1]}</span></button>`).join('')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="card af" style="font-size:20px"><span class="tag af">${m[1]} · ${m[0]}</span><h3 style="margin-bottom:6px">Pick one of</h3>${esc(m[2])}</div>
        <div class="card" style="font-size:19px"><b>It replaces or watches:</b> ${esc(m[3])}. Keep the hand-built piece in your repository and show both.</div>
        <div class="card" style="font-size:19px"><b>Free route for the grader:</b> ${esc(m[4])}. Commit what the tool produced; the grader replays with no key.</div>
        <div class="card bf" style="font-size:18px">Your picks: <b>${[...picked].map((i) => M[i][0]).join(' + ') || 'none yet'}</b>. ${picked.size >= 2 && new Set([...picked]).size >= 2 ? 'Two layers: this meets the line.' : 'Pick at least two layers.'} <span class="small" style="font-size:16px">Click a layer to read it; click it again to pick or drop it.</span></div>
      </div></div>`);
    el.querySelectorAll('[data-i]').forEach((d) => d.onclick = (e) => { stop(e); const i = +d.dataset.i; if (i === sel) { if (picked.has(i)) picked.delete(i); else picked.add(i); } sel = i; draw(); });
  };
  draw();
  return { step() {} };
};

/* Fig: the eight demo-day changes, and whether each is fair (re-measured on Modal) */
FIGS.changes = (el) => {
  const C = (FD.changes && FD.changes.kits) || {};
  const K = FD.kits || [];
  const yes = (v, good) => `<span class="chip ${v === good ? 'p' : 'f'}">${v ? 'yes' : 'no'}</span>`;
  html(el, `<table class="t" style="font-size:17px"><tr><th>Module</th><th>Kind</th><th>Circular</th><th>The change</th><th style="text-align:center">Friday's careful run fails</th><th style="text-align:center">After, careful passes</th><th style="text-align:center">Careless caught</th></tr>
    ${K.map((k) => { const c = C[k.kit] || {}; return `<tr><td>${esc(k.title)}</td><td>${esc(c.kind)}</td><td class="n">${esc(c.id)}</td><td>${esc(c.title)}</td><td style="text-align:center">${yes(c.before === false, true)}</td><td style="text-align:center">${yes(c.after, true)}</td><td style="text-align:center">${yes(c.naive_caught, true)}</td></tr>`; }).join('')}</table>`);
  return { step() {} };
};
})();
