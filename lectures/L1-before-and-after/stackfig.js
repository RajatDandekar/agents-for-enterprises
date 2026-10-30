/* The 2026 agent stack, built up one layer per click (Lecture 1, v4).
   Each layer: what it does, the question it answers, the tools industry uses for it, and the lectures that teach it.
   The last step (or the "Ask Northbridge" button) shows what Ask Northbridge uses at every layer.
   Tool lists follow INDUSTRY_TOOLS_PLAN.md and COURSE_V3.md (v3.1). Tool choice changes every quarter; the layers do not.
   Mount: <div class="fig" data-fig="stack">; the slide needs 10 .step elements (9 layers + the mapping). */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const L = [
  { k: 'model', n: 'Model', does: 'Reads the conversation and writes the next step: a tool call or a reply.',
    q: 'Which brain, and is it good, cheap and fast enough for this job?',
    tools: ['GPT', 'Claude', 'Gemini', 'Llama', 'Qwen', 'Mistral', 'Ollama (local)'], lec: [2, 8],
    nb: 'One LLM behind one function; today’s ablation tries several.' },
  { k: 'gateway', n: 'Gateway', does: 'One API in front of many models: routing, fallbacks, keys, budgets.',
    q: 'Can we switch models, or fall back when one is down, without rewriting code?',
    tools: ['OpenRouter', 'LiteLLM', 'Portkey', 'Cloudflare AI Gateway'], lec: [8, 11],
    nb: 'One function today (ledgerline/llm.py); OpenRouter, LiteLLM later.' },
  { k: 'harness', n: 'Harness or framework', does: 'Runs the loop: instructions, history, the tool list, stop rules, pauses.',
    q: 'Who runs the loop, what does it remember, and when does it stop?',
    tools: ['OpenAI Agents SDK', 'LangGraph', 'Google ADK', 'Claude Agent SDK', 'CrewAI', 'Microsoft Agent Framework'], lec: [5, 8],
    nb: 'Our own harness; also run on the Agents SDK and LangGraph.' },
  { k: 'tools', n: 'Tools and MCP', does: 'One tool per business activity, each with a schema, reached over a standard plug.',
    q: 'What may it do, and how does it reach our systems?',
    tools: ['MCP SDKs', 'MCP Inspector', 'A2A', 'GitHub MCP server'], lec: [4, 9],
    nb: '15 tool folders over MCP, in the user’s own session.' },
  { k: 'knowledge', n: 'Knowledge and memory', does: 'Finds the right passage of the right document, and remembers what matters.',
    q: 'How does it know our rules, and cite them?',
    tools: ['pgvector', 'Qdrant', 'Pinecone', 'Redis', 'LlamaIndex', 'Ragas (to score it)'], lec: [3, 10, 11],
    nb: 'search_policy over Northbridge’s policies: §6.2, cited.' },
  { k: 'workflows', n: 'Workflows', does: 'Fixed paths for repeated jobs: triggers, steps, branches, approval waits.',
    q: 'Which jobs should follow the same path every time?',
    tools: ['n8n', 'Copilot Studio', 'Agentforce', 'Zapier'], lec: [6, 9],
    nb: 'Workflow Studio: low stock → request → approval → order.' },
  { k: 'trust', n: 'Trust', does: 'Whose authority it acts with, who must approve, what is never allowed.',
    q: 'Whose permissions, who signs, and what is blocked before it happens?',
    tools: ['NeMo Guardrails', 'Llama Guard', 'Guardrails AI', 'Bedrock Guardrails', 'Azure Prompt Shields', 'OWASP LLM Top 10'], lec: [7, 11],
    nb: 'Emma’s own session; a yes before every save; Daniel above £250,000.' },
  { k: 'obs', n: 'Observability and evals', does: 'Records every model and tool call; tests the agent before and after every change.',
    q: 'What did it do, and is it still right after we change something?',
    tools: ['Langfuse', 'Arize Phoenix', 'LangSmith', 'Datadog LLM Observability', 'OpenTelemetry GenAI', 'DeepEval', 'promptfoo', 'Braintrust'], lec: [7, 10],
    nb: 'Tool cards, traces in Langfuse, missions checked on Ledgerline.' },
  { k: 'durable', n: 'Durable execution and deployment', does: 'Keeps a job alive across crashes and long waits; runs it, scales it, prices it.',
    q: 'What happens if it crashes mid-order, or waits two days for Daniel?',
    tools: ['Temporal', 'Inngest', 'Restate', 'DBOS', 'Bedrock AgentCore', 'Microsoft Foundry'], lec: [7, 11],
    nb: 'Content keys: a retry never makes a second order. Runs on Modal.' },
];
window.STACK_LAYERS = L;
FIGS.stack = (el) => {
  el.innerHTML = `<div class="sk"><div class="sk-l">${L.map((x, i) => `<button class="sk-b" data-i="${i}"><span class="sk-i">${i + 1}</span><span class="sk-n">${x.n}</span><span class="sk-m">${esc(x.nb)}</span></button>`).slice().reverse().join('')}</div>
    <div class="sk-p" aria-live="polite"></div></div>`;
  const bs = [...el.querySelectorAll('.sk-b')], pane = el.querySelector('.sk-p');
  let map = false;
  const lec = (a) => a.map((n) => `<span class="tag af">L${n}</span>`).join(' ');
  const set = (i) => {
    const x = L[i];
    bs.forEach((b) => b.classList.toggle('on', +b.dataset.i === i));
    pane.innerHTML = `<div class="sk-h"><span class="sk-hi">${i + 1}</span>${x.n}</div>
      <div class="sk-r"><div class="sk-k">What it does</div><div>${x.does}</div></div>
      <div class="sk-r"><div class="sk-k">The question it answers</div><div class="sk-q">“${x.q}”</div></div>
      <div class="sk-r"><div class="sk-k">In industry</div><div class="sk-tools">${x.tools.map((t) => `<span class="sk-t">${esc(t)}</span>`).join('')}</div></div>
      <div class="sk-r"><div class="sk-k">Taught in</div><div>${lec(x.lec)}</div></div>
      <div class="sk-r sk-nbr"><div class="sk-k">In Ask Northbridge</div><div>${esc(x.nb)}</div></div>`;
  };
  bs.forEach((b) => b.addEventListener('click', () => set(+b.dataset.i)));
  return { step(k) {
    const n = Math.min(k, L.length - 1);
    map = k >= L.length;
    el.classList.toggle('mapped', map);
    bs.forEach((b) => { const i = +b.dataset.i; b.style.opacity = i <= n ? 1 : 0.14; });
    set(map ? 2 : n);
  } };
};
})();
