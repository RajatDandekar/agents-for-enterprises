/* The twelve lectures, one slide each, inserted right after #lec-anchor before plates.js numbers the slides.
   Dates: the course hub (index.html). Content: COURSE_V3.md (v3.1), the lecture A-files, lectures/L12-your-module/rubric.md,
   agents-site/site/app.js. Told in the Northbridge world (WORLD_V4.md). Also numbers the "Ask the class" slides. */
(() => {
const LECTURES = [
  [1, 'Sat 31 Oct', 'The Before and the After', 'Today',
   'You meet Northbridge, do Emma’s battery pack order by hand on Ledgerline, write your brief, then watch Ask Northbridge do the same work.',
   ['Why agents matter now, and where pilots break', 'What an ERP is: master data, transactions, status, procure-to-pay', 'An agent seen from outside: harness, LLM, tools, MCP', 'The 2026 agent stack'],
   'Your Before and After scorecard in the Northbridge Experience', 'A1 · Choose your capstone. Map its Before; write its After and its never-events.'],
  [2, 'Sun 1 Nov', 'The Brain: How an LLM Works', 'a brain',
   'We take the tools away. Asked about battery stock, the bare model answers confidently, and the number is made up. Why?',
   ['Next-token prediction; tokens and BPE; embeddings', 'Attention worked by hand; the transformer block', 'Training: pretraining, instruction tuning, RLHF', 'Sampling and temperature; the context window; why models make things up'],
   'A tiny GPT trained from scratch in a notebook, beside a real model', 'A2 · Attention by hand; train the tiny GPT on your module’s documents and find what it invents.'],
  [3, 'Sat 7 Nov', 'The Memory: Giving It Knowledge', 'knowledge',
   'Emma asks whether she can buy from Brightcell Energy. The answer is in Purchase Policy §6.2, and in Luis’s head.',
   ['Why the model does not know your company; context as the only memory', 'Chunking, BM25, embeddings and cosine similarity, hybrid search, reranking', 'Retrieval with checked citations; the LLM wiki', 'Who may read what; stale documents'],
   'search_policy: the certification question answered with §6.2 cited', 'A3 · Index your module’s documents, with permissions, graded questions and a stale document handled.'],
  [4, 'Sun 8 Nov', 'The Hands: Tools and MCP', 'hands',
   'Ask Northbridge gets hands: it checks stock and raises the request, in Emma’s own session, and never makes a second order on a retry.',
   ['Function calling from first principles; JSON Schema', 'One tool per business activity: previews, idempotency keys, receipts, errors that say what to do next', 'The tool folder: tool.json + tool.py', 'MCP on the wire: hosts, servers, tools/list, tools/call'],
   'The Northbridge toolbox over MCP, also plugged into a desktop host', 'A4 · 3–4 tool folders for your module with the six promises, a lost-reply test, served over MCP.'],
  [5, 'Sat 14 Nov', 'The Loop: What Makes It an Agent', 'a harness',
   'One sentence has to run request, wait for Daniel, order, release and receipt, across a pause that may last a day.',
   ['Agent = model + tools + loop + state', 'ReAct written out, then native tool calling', 'The harness part by part: prompt, history, registry, stop rules, budget', 'Failure modes; from a free loop to a control graph (LangGraph); approval as a pause'],
   'A harness that runs the whole procure-to-pay, across Daniel’s approval', 'A5 · A harness for your module: three scenarios (happy path, silent outcome, a pause), bare loop vs harness.'],
  [6, 'Sun 15 Nov', 'The Studio: Workflows and Your Own Agents', 'workflows',
   'Emma’s Monday reorder check should not need a chat at all. Some jobs should follow the same path every time.',
   ['Workflow or agent: a fixed path, or the model choosing', 'Triggers, nodes, data mapping, branches, approval waits, error paths', 'Safe reruns; agents as nodes', 'A workflow engine written from scratch'],
   'Stock below reorder level → request → approval → order → release, in the Workflow Studio, plus an agent of your own', 'A6 · Two workflows for your module and your own agent, each run twice without a duplicate.'],
  [7, 'Sat 21 Nov', 'Trust: Taking It to Production', 'trust',
   'Henrik asks the question every plant head asks: can we switch it on for everyone?',
   ['Identity: the user’s own permissions, never the service account', 'Approvals, never-events, guards before writes, read-back proof', 'Evals: scenarios, code checks and LLM judges, a regression gate', 'Traces, retries, durable waits, deploy, cost'],
   'Ask Northbridge with a trust layer, an eval suite with a gate, deployed', 'A7 · Identity, a guard per never-event, read-back, a suite of 4 scenarios × 3 runs with a gate, recovery.'],
  [8, 'Sun 22 Nov', 'Agent Frameworks in Industry', 'frameworks',
   'Northbridge’s CTO asks: should this run on a framework, which one, and what do we lose?',
   ['The OpenAI Agents SDK and Google ADK mapped onto your harness', 'LangGraph in production', 'One API for many models: OpenRouter, LiteLLM', 'Local models with Ollama; which framework when'],
   'Ask Northbridge ported to three frameworks, measured side by side', 'A8 · Port your agent to two frameworks, one meter for all, a rule moved into a framework guardrail, a one-page memo.'],
  [9, 'Sat 28 Nov', 'Protocols and Integration', 'protocols',
   'Voltway wants its own agent to talk to Ask Northbridge. Every new door is also a way in for an attacker.',
   ['MCP in depth: resources, prompts, the Inspector, remote servers and sign-in', 'Confirmations inside the protocol; MCP security', 'A2A: agent cards and tasks, agent to agent across companies', 'n8n and enterprise low-code builders'],
   'A supplier agent that Ask Northbridge negotiates with over A2A', 'A9 · Your module on the official MCP SDK, checked in Inspector, with a counterparty over A2A, proved safe.'],
  [10, 'Sun 29 Nov', 'Observability and Evals in Industry', 'observability',
   'Henrik asks three things: what did it do, does it still follow our rules after a change, and has anyone tried to break it?',
   ['OpenTelemetry GenAI traces; Langfuse and Phoenix', 'DeepEval tests as a CI gate', 'Ragas for retrieval; promptfoo red-teaming', 'Calibrating LLM judges against code checks'],
   'A traced Ask Northbridge with a CI gate and a red-team report', 'A10 · Instrument your agent, ten tests with a gate that blocks a broken prompt, a red-team, a reliability report.'],
  [11, 'Sat 5 Dec', 'Running Agents in Production', 'production',
   'Approvals that take days, a poisoned supplier record, and the first monthly bill.',
   ['Guardrails against the OWASP LLM Top 10; prompt injection', 'NeMo Guardrails and Llama Guard, measured', 'Temporal for waits that survive a restart; pgvector and Redis', 'LiteLLM budgets and fallbacks; Bedrock AgentCore, Microsoft Foundry'],
   'A production-readiness review of Ask Northbridge', 'A11 · A threat model of all ten OWASP rows, two guards measured, a durable wait, a cost model, a runbook.'],
  [12, 'Sun 6 Dec', 'Your Module: Demo Day', 'your module',
   'Your module’s Before and After, live, with a change announced the day before, and the client’s questions.',
   ['The whole system as one figure', 'The same recipe on another business process', 'Choosing and defending a production stack'],
   'Your own agent for your domain, demoed in eight minutes', 'The capstone, graded out of 100 on one sheet, live or recorded.'],
];
window.L1_LECTURES = LECTURES;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const anchor = document.getElementById('lec-anchor');
let after = anchor;
LECTURES.forEach(([n, d, t, piece, beat, learn, build, as]) => {
  const s = document.createElement('section');
  s.className = 'slide'; s.id = 'lec-' + n; s.dataset.plate = `Lecture ${n} · ${t.split(':')[0]}`;
  const track = n <= 7 ? 'Built by hand' : n <= 11 ? 'The production stack' : 'Your module';
  const proj = n === 1 ? 'The project · you see the whole thing' : n === 12 ? 'The project · your own agent' : `The project · Ask Northbridge gains ${esc(piece)}`;
  s.innerHTML = `<div class="lx-top"><div class="lx-k"><span class="pill">Lecture ${n} of 12</span><span>${d} 2026 · 7–9 AM IST</span><span class="pill">${track}</span></div>
    <h2>${esc(t)}</h2><div class="lx-beat"><span class="k">The story beat at Northbridge</span>${esc(beat)}</div></div>
    <div class="lx-grid"><div class="card"><div class="lx-h">What you learn</div><ul>${learn.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>
    <div class="card af"><div class="lx-h">${proj}</div>${esc(build)}</div>
    <div class="card"><div class="lx-h">The assignment · on your module</div>${esc(as)}</div></div>`;
  if (anchor) { after.insertAdjacentElement('afterend', s); after = s; }
});
let q = 0; document.querySelectorAll('.qnum').forEach((e) => { e.textContent = String(++q); });
})();
