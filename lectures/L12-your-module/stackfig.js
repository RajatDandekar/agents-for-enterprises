/* The 2026 agent stack: each piece of Ask Rasoi, the tools companies use for it, and the lecture that teaches it.
   The base image is the master PaperBanana architecture (figures/ask_rasoi_architecture_wide.png, copied to
   figs/ask_rasoi_stack_base.jpg); the clickable layers are transparent buttons laid over it.
   Tool lists follow COURSE_V3.md (v3.1) and INDUSTRY_TOOLS_PLAN.md. Identical copy in lectures/L12-your-module/.
   Mount: <div class="fig" data-fig="stack" data-img="figs/ask_rasoi_stack_base.jpg" [data-start="harness"]>. Any other
   element in the slide with data-k="<layer>" (for example a button for "platform") also selects that layer. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const LEC = { 1: 'The Before and the After', 2: 'The Brain', 3: 'The Memory', 4: 'The Hands', 5: 'The Loop', 6: 'The Studio', 7: 'Trust',
  8: 'Agent Frameworks in Industry', 9: 'Protocols and Integration', 10: 'Observability and Evals', 11: 'Running Agents in Production', 12: 'Your Module' };
/* box = [left, top, right, bottom] as fractions of the image */
const LAYERS = {
  people: { name: 'Where people work', box: [0.028, 0.02, 0.87, 0.208], hand: 6, ind: [9],
    groups: [['Low-code builders', [['n8n', 'L9', 'self-hosted and free: the same Studio workflows, over MCP', 1], ['Copilot Studio', 'L9', 'Microsoft’s enterprise low-code builder'], ['Agentforce', 'L9', 'Salesforce’s enterprise low-code builder']]]],
    same: 'L6’s Workflow Studio is a canvas like n8n. In L9 the same reorder workflow runs in n8n itself.' },
  harness: { name: 'Harness: the agent loop', box: [0.028, 0.242, 0.87, 0.479], hand: 5, ind: [8],
    groups: [['Agent frameworks', [['OpenAI Agents SDK', 'L8', 'an agent, its tools, and a Runner that loops', 1], ['Google ADK', 'L8', 'Google’s Agent Development Kit', 1], ['LangGraph', 'L5 · L8', 'the control graph: a spine with gates', 1]]]],
    same: 'In L5 you write the loop yourself. In L8 the same Ask Rasoi runs on the Agents SDK, whose Runner is that loop.' },
  llm: { name: 'LLM: the brain', box: [0.112, 0.34, 0.305, 0.442], hand: 2, ind: [8, 11],
    groups: [['Model gateways', [['OpenRouter', 'L8', 'one API, many models', 1], ['LiteLLM', 'L8 · L11', 'one API, plus budgets and fallbacks', 1]]], ['Local models', [['Ollama', 'L8', 'a small model on your own machine']]]],
    same: 'Every model call in this course goes through one small function. A gateway is the production version of it.' },
  knowledge: { name: 'Knowledge: policy search', box: [0.592, 0.34, 0.786, 0.442], hand: 3, ind: [10, 11],
    groups: [['Retrieval evals', [['Ragas', 'L10', 'scores what was found and whether the answer used it', 1]]], ['Stores', [['pgvector', 'L11', 'vector search inside Postgres', 1], ['Redis', 'L11', 'fast memory and cache', 1]]]],
    same: 'L3 builds search over Rasoi’s policies by hand. L10 scores it with Ragas; L11 moves the index into pgvector.' },
  mcp: { name: 'MCP: the plug', box: [0.028, 0.508, 0.87, 0.57], hand: 4, ind: [9],
    groups: [['Protocols', [['MCP', 'L4 · L9', 'the official SDK, MCP Inspector, remote servers, sign-in', 1], ['A2A', 'L9', 'one agent hands a task to another agent', 1]]]],
    same: 'L4 builds the toolbox server from scratch. L9 goes deep: the official SDK, a remote server with sign-in, and A2A.' },
  toolbox: { name: 'Toolbox: one tool per activity', box: [0.028, 0.596, 0.87, 0.778], hand: 4, ind: [9],
    groups: [['Stays yours', [['Your tool folders', 'L4', 'tool.json + tool.py: no framework writes Rasoi’s tools', 1], ['GitHub MCP server', 'L9', 'a ready-made server, to compare with ours']]]],
    same: 'Frameworks come and go; the tools stay. Every framework in L8 calls these same 15 folders over MCP.' },
  bahi: { name: 'Bahi ERP 7.2 (1998) services', box: [0.028, 0.806, 0.87, 0.982], hand: 0, ind: [],
    groups: [],
    same: 'Nothing replaces Bahi. Every tool in the course sits above it, and its services stay black boxes.' },
  trust: { name: 'Trust', box: [0.902, 0.018, 0.975, 0.982], hand: 7, ind: [10, 11],
    groups: [['Observability', [['Langfuse', 'L10', 'open-source traces', 1], ['Arize Phoenix', 'L10', 'open-source traces', 1], ['LangSmith', 'L10', 'hosted traces']]],
      ['Evals', [['DeepEval', 'L10', 'agent tests as a CI gate', 1], ['Ragas', 'L10', 'retrieval scores', 1], ['promptfoo', 'L10', 'red-teaming', 1]]],
      ['Guardrails', [['NeMo Guardrails', 'L11', 'rules around the model', 1], ['Llama Guard', 'L11', 'a safety classifier', 1]]],
      ['Durable execution', [['Temporal', 'L11', 'a wait that survives a restart', 1]]]],
    same: 'L7 builds identity, guards, evals, traces and recovery by hand. L10 and L11 put each one on the tool companies run.' },
  platform: { name: 'The whole stack, rented', box: null, hand: 0, ind: [9, 11],
    groups: [['Managed agent platforms', [['Bedrock AgentCore', 'L11', 'AWS hosts the runtime, identity, memory and traces'], ['Microsoft Foundry', 'L11', 'Microsoft’s agent platform']]], ['Buy, not build', [['Copilot Studio', 'L9', 'agents inside Microsoft 365'], ['Agentforce', 'L9', 'agents inside Salesforce']]]],
    same: 'Some companies rent all of it. Having built every box, you can judge what you are renting.' },
};
window.STACK_LAYERS = LAYERS;
FIGS.stack = (el) => {
  const img = el.dataset.img || 'figs/ask_rasoi_stack_base.jpg';
  el.innerHTML = `<div class="stk">
    <div class="stk-l"><div class="stk-img"><img src="${img}" alt="The architecture of Ask Rasoi: where people work, the harness with the LLM and knowledge, MCP, the toolbox, Bahi ERP, and the trust bar">
      ${Object.entries(LAYERS).filter(([, L]) => L.box).map(([k, L]) => `<button class="stk-hot${k === 'llm' || k === 'knowledge' ? ' top' : ''}" data-k="${k}" aria-label="${esc(L.name)}" style="left:${L.box[0] * 100}%;top:${L.box[1] * 100}%;width:${(L.box[2] - L.box[0]) * 100}%;height:${(L.box[3] - L.box[1]) * 100}%"></button>`).join('')}
    </div></div>
    <div class="stk-p" aria-live="polite"></div></div>`;
  const pane = el.querySelector('.stk-p'), btns = [...(el.closest('.slide') || el).querySelectorAll('[data-k]')];
  const lec = (n) => `L${n} · ${LEC[n]}`;
  const set = (k) => {
    const L = LAYERS[k];
    btns.forEach((b) => b.classList.toggle('on', b.dataset.k === k));
    const ind = L.ind.length === 1 ? lec(L.ind[0]) : L.ind.map((n) => 'L' + n).join(' · ');
    const tags = [L.hand ? `<span class="tag af">Built by hand · ${lec(L.hand)}</span>` : '', L.ind.length ? `<span class="tag nt" title="${L.ind.map(lec).join('; ')}">In industry · ${ind}</span>` : ''].join(' ');
    const grp = L.groups.map(([h, ts]) => `<div class="stk-g"><div class="stk-gh">${esc(h)}</div>${ts.map(([n, l, d, f]) => `<div class="stk-t${f ? ' f' : ''}"><div class="stk-tn">${esc(n)} <span class="stk-tl">${l}</span></div><div class="stk-td">${esc(d)}</div></div>`).join('')}</div>`).join('');
    pane.innerHTML = `<h3>${esc(L.name)}</h3><div class="stk-tags">${tags.trim() || '<span class="tag bf">No industry tool replaces it</span>'}</div>
      <div class="stk-gs${L.groups.length > 2 ? ' stk-2c' : ''}">${grp}</div><div class="stk-same">${esc(L.same)}</div>${L.groups.length ? '<div class="stk-key"><span class="f">taught hands-on</span><span>named and compared</span></div>' : ''}`;
  };
  btns.forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); set(b.dataset.k); }));
  set(el.dataset.start || 'harness');
  return { step() {} };
};
})();
