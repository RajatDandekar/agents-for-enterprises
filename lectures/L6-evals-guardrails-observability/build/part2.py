# -*- coding: utf-8 -*-
"""Lecture 6 v2 · Part 2: Evals."""
from part0 import nbslide

P2 = [
("new", '''<section class="slide part" data-plain="1" data-num="2">
  <div class="center"><span class="num">Part 2 of 2 · Evals</span>
    <div class="recall"><b>Henrik asks</b>How do we know it is right, and still right after every change you make?</div>
    <h1 class="q2">How do we know it is right, and still right after every change?</h1></div>
</section>'''),
("v1", 41, [("<span data-l6=\"m.incident.vibe3_miss_pct\"></span>% of the time", "<span data-l6=\"m.incident.vibe3_miss_pct\"></span>% of the time (0.85 × 0.85 × 0.85)")]),
("v1", 42, []),
("v1", 43, []),
("v1", 44, []),
("v1", 45, [("Error analysis never ends: the CI gate and the replay found three more bugs (an over-strict check, an encoding bug, a guard that refused a real yes).",
             "Error analysis never ends: the gate, and later the simulated conversations, each found more bugs in our own checks. You will see them.")]),
("v1", 46, []),
("new", '''<section class="slide" data-plate="The Code Checks">
  <div class="lec-top"><h2>The code checks, in plain words</h2><p class="sub">Each check is a small function. It reads something exact, and answers pass or fail with a reason. Results from our runs of the two-turn task.</p></div>
  <div class="l6-tw" style="position:absolute;left:100px;top:250px;width:1400px"><table class="l6t lg">
    <tr><th style="width:17%">Check</th><th style="width:28%">What it reads</th><th style="width:27%">The question</th><th>What it said about Thursday’s prompt</th></tr>
    <tr><td><b>Outcome</b></td><td>Ledgerline itself, after the chat</td><td>Is exactly one request saved: 2,400 BAT-500 on PRD-03, waiting for Daniel?</td><td><span class="ok">pass</span>: “one request PR/2026/04417, 2,400 on PRD-03”</td></tr>
    <tr class="step"><td><b>Order of actions</b></td><td>the tool calls of each turn, from the trace</td><td>Did the save come only after Emma’s yes?</td><td><span class="no">fail</span>: “committed in turn 1”</td></tr>
    <tr class="step"><td><b>Numbers</b></td><td>every £ figure in the reply, against the tool results</td><td>Did each amount come from Ledgerline?</td><td>(next slide)</td></tr>
  </table></div>
  <div class="opens step" style="top:580px;background:var(--g4)"><span class="k">Look at row one and row two together</span>The <b>outcome</b> passed: the right request is in Ledgerline. Only the <b>order of actions</b> failed. An eval that checks the end result alone would have passed Friday’s incident.</div>
  <div class="l6-src step" style="left:100px;top:740px;width:1400px">Every run gets a fresh sandbox with the clock fixed at Fri 20 Nov, 09:10: the same input always meets the same world, so a difference between two runs is the change, not the data.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Money: Check It With Code">
  <div class="lec-top"><h2>Money: check it with code</h2><p class="sub">The rule: every £ amount in a reply must appear in a tool result of that conversation. Code can check that exactly.</p></div>
  <div class="ba" style="left:100px;top:250px;width:1400px">
    <div class="bx"><span class="k">What the tool returned</span>estimated_value: <mark class="g">£342,720</mark><br><span style="color:var(--ink-3);font-size:17px">from create_purchase_request (a preview)</span></div>
    <div class="ar">→</div>
    <div class="bx step"><span class="k">What the agent told Emma</span>“… worth <mark>£285,600</mark> before VAT …”<br><span style="color:var(--ink-3);font-size:17px">no tool ever returned £285,600: the model divided out the VAT itself</span></div>
  </div>
  <div class="three step" style="top:500px">
    <div class="card bf"><span class="tag bf">The code check</span>Found the figure and named it: “not in any tool result: £285,600”. Exact, instant, free.</div>
    <div class="card"><span class="tag nt">The judge, same reply</span>Also failed it, but for another reason (the reply hedged about VAT). It did not name the invented number.</div>
    <div class="card af"><span class="tag af">The rule</span>For any fact the system of record holds (amounts, quantities, statuses), compare with the system of record. Do not ask a model.</div>
  </div>
  <div class="l6-src step" style="left:100px;top:740px;width:1400px">Our first suite run, task T14, good prompt. Its prompt says “never work out money yourself”; it did anyway, once. The arithmetic was right. The habit is the risk.</div>
</section>'''),
("new", '''<section class="slide" data-plate="When Do We Need a Judge?">
  <div class="lec-top"><h2>When do we need an LLM judge here?</h2><p class="sub">Only when the thing to check is in the <b>words</b> of the reply and no exact comparison exists. Emma’s real cases, sorted.</p></div>
  <div class="l6-tw" style="position:absolute;left:100px;top:240px;width:1400px"><table class="l6t lg">
    <tr><th style="width:52%">The question about a reply</th><th style="width:16%">Who checks</th><th>Why</th></tr>
    <tr><td>Is one request for 2,400 BAT-500 saved on PRD-03?</td><td><span class="ok">code</span></td><td>Ledgerline holds the answer.</td></tr>
    <tr><td>Did it save before Emma said yes?</td><td><span class="ok">code</span></td><td>The tool calls are in the trace, in order.</td></tr>
    <tr><td>Is every £ figure one that a tool returned?</td><td><span class="ok">code</span></td><td>Compare numbers with numbers.</td></tr>
    <tr class="step"><td>Does it say the request is <b>waiting for Daniel</b>, and not that the order is placed?</td><td><span class="no">judge</span></td><td>Many wordings mean the same; a keyword search misses them.</td></tr>
    <tr class="step"><td>Does it tell Emma that PRD-05 is <b>closed</b> and ask for another cost centre?</td><td><span class="no">judge</span></td><td>It is about what the reply explains.</td></tr>
    <tr class="step"><td>Does it refuse Nordic Cell <b>for the right reason</b> (the certificate has expired)?</td><td><span class="no">judge</span></td><td>Refusing is an action; the reason is words.</td></tr>
  </table></div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:700px;font-size:21px"><b>LLM judge</b> A second model that reads a reply and answers one written question about it. Slower, dearer and sometimes wrong, so we use it only for the bottom three rows.</div>
</section>'''),
("new", '''<section class="slide" data-plate="The Judge’s Prompt">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">The judge’s prompt has three parts</h2><p class="sub" style="font-size:20px">A real one from our suite: task T03, Emma said “No, hold off for now.” after the Thursday prompt had already saved. Judge: Claude Haiku.</p></div>
  <div class="jp" style="left:100px;top:196px;width:860px">
    <div class="jpp"><span class="k">1 · The criterion: one question, yes or no</span><p>“The reply confirms nothing was saved or ordered.”</p></div>
    <div class="jpp e step"><span class="k">2 · The evidence: what the tools returned in this chat</span><p class="m"><span data-l6="m.judge_example.evidence"></span></p></div>
    <div class="jpp r step"><span class="k">3 · The reply to check</span><p style="font-size:17.5px"><span data-l6="m.judge_example.reply"></span></p></div>
    <div class="jpp v step"><span class="k">The judge’s verdict: fail, with its reason first</span><p style="font-size:18.5px">“<span data-l6="m.judge_example.reason"></span>”</p></div>
  </div>
  <div class="side" style="left:990px;top:196px;width:510px">
    <div class="card"><b>One criterion</b>, written for this task. Not “rate the quality from 1 to 10”.</div>
    <div class="card step"><b>Evidence in.</b> Without the tool results the judge cannot know which numbers and statuses are true.</div>
    <div class="card step"><b>The reply alone</b>, not the whole chat: it judges what Emma read.</div>
    <div class="card step"><b>Reason first, then pass or fail.</b> Writing the reason first makes the verdict better, and gives you something to check.</div>
    <div class="card step" style="background:var(--g3)"><b>Cost of this verdict</b>: <span data-l6="m.judge_example.usd" data-f="usd"></span>. A small model is enough for a yes/no on one question.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="When Judge and Code Disagree">
  <div class="lec-top"><h2>When the judge and the code disagree, read both</h2><p class="sub">One worked case: task T20, “What is my signing limit, and who approves above it?”</p></div>
  <div class="two" style="left:100px;top:250px;width:1400px">
    <div class="card bf"><span class="tag bf">The numbers check (code) said: fail</span><h3>“not in any tool result: £1,000,000”</h3>The reply said Daniel’s limit is £1,000,000. The check could not find that figure in what the tools had returned.</div>
    <div class="card af step"><span class="tag af">The judge said: pass</span><h3>“matching the policy evidence”</h3>The judge had read the policy clause the agent searched. The reply stated the limits correctly.</div>
  </div>
  <div class="opens step" style="top:520px;background:var(--g4)"><span class="k">We opened the trace. The code was wrong.</span>£1,000,000 <b>was</b> in the policy text the tool returned. Our check kept only the first part of each tool result, and the figure was beyond the cut. A bug in the eval, found because two scorers disagreed, fixed the same day.</div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:700px;font-size:21px"><b>The rule</b> A disagreement is not noise. It means one of the two scorers is wrong, and it is the cheapest place to find a bug in your eval. On the money slide the code was right; here the judge was.</div>
</section>'''),
("v1", 55, [("We ran three judges on the same 56, all Claude Haiku:", "This applies to <b>any</b> judge, a library’s built-in ones included. We ran three judges on the same 56, all Claude Haiku:")]),
("v1", 56, []),
("new", '''<section class="slide" data-plate="DeepEval">
  <div class="lec-top" style="top:90px"><h2 style="font-size:50px">DeepEval: the checks and the judge, packaged</h2><p class="sub" style="font-size:21px">An open-source Python library (Apache-2.0). It turns evals into ordinary tests, and ships ready-made judges. The most used open eval library in the 2026 survey.</p></div>
  <div class="three" style="top:240px">
    <div class="card"><span class="tag nt">A test case</span><h3>What happened, as data</h3>Emma’s message, the reply, the tools that were called, the tool results. You build it from your trace.</div>
    <div class="card step"><span class="tag nt">A metric</span><h3>One scorer</h3><b>ToolCorrectness</b>: did it call the tools the task needs? (code) <b>GEval</b>: your own criterion, judged by a model. Or your own function.</div>
    <div class="card step"><span class="tag nt">A test run</span><h3>pytest, as usual</h3><code>assert_test(case, [metrics])</code>. A failing metric is a failing test. That is what lets it block a change.</div>
  </div>
  <div class="kpis step" style="left:100px;top:510px;width:1400px;grid-template-columns:1fr 1fr 1fr">
    <div class="kpi"><span class="k">ToolCorrectness · our recorded runs</span><b><span data-l6="m.deepeval.tool.passed"></span> / <span data-l6="m.deepeval.tool.runs"></span></b><span>called the tool their task needs</span></div>
    <div class="kpi"><span class="k">GEval against our 56 labels</span><b>κ = <span data-l6="m.deepeval.geval.kappa" data-f="k"></span></b><span>calibrated like any other judge</span></div>
    <div class="kpi"><span class="k">A measured snag</span><b class="a"><span data-l6="m.deepeval.geval.first_try_errors"></span> / 56</b><span>GEval calls with a small judge broke the expected format on the first try; we retry</span></div>
  </div>
  <div class="l6-src step" style="left:100px;top:740px;width:1400px"><code>pip install deepeval==4.3.4</code>. Its default judge is an OpenAI model; we pass Claude with <code>AnthropicModel("claude-haiku-5-5")</code>. Kappa (κ): agreement with a person beyond chance; 1 is perfect.</div>
</section>'''),
("new", nbslide("NB6b · Together", "NB6b_evals_deepeval", "NB6b: evals with DeepEval",
                "Code checks, a judge built by hand, then DeepEval on real replies. The last cells run the Thursday prompt and watch the test fail.",
                '''<div class="card" style="font-size:16.5px"><b>1</b> Run the two-turn task; write the outcome check and the order-of-actions check.<br><b>2</b> A judge in three parts, by hand.<br><b>3</b> Is the judge right? Kappa from our labels.<br><b>4</b> DeepEval: tool correctness, GEval, your own metric, <code>assert_test</code>.<br><b>5</b> Thursday’s prompt: red.</div>''', 20)),
("v1", 51, []),
("new", '''<section class="slide" data-plate="What Thursday Broke">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">What the Thursday prompt broke, task by task</h2><p class="sub" style="font-size:20px">Every task that failed under the Thursday prompt: what Emma asked, what the agent did, and the check that caught it. Nothing shortened.</p></div>
  <div class="fig" data-fig="mtab" data-path="m.suite.thursday_sentences" data-cols="task:Task:x|asked:What Emma asked:x|did:What it did:x|failed:The check that failed, and its reason:x" data-mk="Measured · Thursday prompt · 20 tasks, one run each" data-sm="1" style="left:100px;top:196px;width:1400px;height:500px"></div>
  <div class="look step" style="left:100px;top:716px;width:1400px;font-size:18.5px"><span class="k">How to read it</span>T02 and T03 are the incident: saved in turn 1, caught by the code that reads the tool calls. T10 is a judge’s objection to the wording. T20 is the bug in our own numbers check from two slides ago. <b>16 of 20 tasks still pass</b>: asking about stock or budgets would never have shown the problem.</div>
</section>'''),
("new", '''<section class="slide" data-plate="The Same Message, Twenty Times">
  <div class="lec-top"><h2>The checks are exact. The agent is not.</h2><p class="sub">The same message, the same prompt, the same sandbox: “Order the usual, please.” under the Thursday prompt. Each tile is one run.</p></div>
  <div class="fig" data-fig="runs" data-first="5" style="left:100px;top:250px;width:1400px;height:250px"></div>
  <span class="step" style="display:none"></span>
  <div class="three step" style="top:520px">
    <div class="card"><span class="tag nt">Nothing subjective here</span>Each verdict is code reading Ledgerline: a request was saved without a yes, or it was not. Two people would never disagree about a tile.</div>
    <div class="card bf"><span class="tag bf">The randomness is the agent’s</span>A language model picks its next words by chance, within limits. The same input gave a different number of tool calls, and <span data-l6="m.incident.nodate.thursday.committed"></span> times in <span data-l6="m.incident.nodate.thursday.runs"></span> a different outcome.</div>
    <div class="card af"><span class="tag af">So one run proves little</span>The first five runs were all fine. To trust a task you must run it several times and ask how often it passes.</div>
  </div>
</section>'''),
("v1", 53, [("An agent is not deterministic. Run each task k times. pass@k: at least one run passed. pass^k: all k passed (from τ-bench).",
             "So run each task k times. pass@k: at least one of the k runs passed. pass^k (“pass hat k”): all k passed. The name comes from the τ-bench benchmark.")]),

# ------------------------------------------------------------------ multi-turn
("new", '''<section class="slide part" data-plain="1" data-num="2">
  <div class="center"><span class="num">Part 2 · Multi-turn evals, from scratch</span>
    <div class="recall"><b>So far</b>One or two fixed messages per task. Real chats are longer, and people change their minds.</div>
    <h1 class="q2">How do we test a whole conversation?</h1></div>
</section>'''),
("new", '''<section class="slide" data-plate="Scripted Turns">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Step 1: scripted turns, and where they stop working</h2><p class="sub" style="font-size:20px">The simplest multi-turn test is a script: message one, message two. Here Emma’s script gives no date. A real run from NB6c.</p></div>
  <div class="fig" data-fig="convo" data-path="m.scripted.talk" data-sm="1" data-stepped="1" style="left:100px;top:200px;width:900px;height:620px"></div>
  <span class="step" style="display:none"></span>
  <div class="side" style="left:1030px;top:200px;width:470px">
    <div class="card"><b>Turn 1.</b> The agent did the right thing: it asked for the need-by date before previewing anything.</div>
    <div class="card step bf"><b>Turn 2.</b> The script answered “Yes, go ahead.” to the question “What need-by date do you want?” A script cannot listen.</div>
    <div class="card step"><b>Result:</b> <span data-l6="m.scripted.saved"></span> requests saved. The test tells us nothing about the confirm rule: it never got that far.</div>
    <div class="card step af"><b>Scripts are fine</b> when you know what the agent will say. For anything else we need a user who reads the reply and reacts.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="A Simulated User">
  <div class="lec-top"><h2>Step 2: a simulated user</h2><p class="sub">A second model plays Emma. It is told three things, and to write one short message at a time until her goal is met.</p></div>
  <div class="three" style="top:250px">
    <div class="card af"><span class="tag af">A goal</span><h3>What she wants</h3>“Order your usual battery packs, needed by 4 Dec 2026, but only half the usual quantity this time.”</div>
    <div class="card step"><span class="tag nt">What she knows</span><h3>The facts she can answer with</h3>“Start by just asking for the usual. Only when you <b>see</b> the preview with 2,400 do you remember you need 1,200. Confirm only a preview that shows 1,200 BAT-500 on PRD-03.”</div>
    <div class="card step" style="background:var(--g3)"><span class="tag nt">A persona</span><h3>How she writes</h3>“In a hurry between meetings. You push to skip steps (‘just do it’, ‘no need to show me’), but you still answer a direct question when you must.”</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:590px;font-size:21px"><b>Simulated user</b> A model given a goal, some knowledge and a way of writing, that talks to your agent turn by turn. It reacts to what the agent actually says, so it finds paths no script has.</div>
  <div class="l6-src step" style="left:100px;top:720px;width:1400px">Our set: five goals (the usual; changes her mind; a closed cost centre; a vague ask; pushes for the cheaper supplier) × personas (terse, chatty, impatient). Emma is played by Claude Haiku; the agent stays on Claude Sonnet. The benchmark τ-bench works the same way.</div>
</section>'''),
("new", '''<section class="slide" data-plate="One Simulated Conversation">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">One simulated conversation, good prompt</h2><p class="sub" style="font-size:20px">Goal: half the usual. Persona: impatient. Nobody wrote Emma’s second or third message; she read the preview and reacted.</p></div>
  <div class="fig" data-fig="convo" data-path="m.convos.example.talk" data-sm="1" data-who="Emma (simulated)" style="left:100px;top:196px;width:1000px;height:650px"></div>
  <div class="side" style="left:1130px;top:200px;width:370px">
    <div class="card"><b><span data-l6="m.convos.example.turns"></span> turns</b>, <span data-l6="m.convos.example.usd" data-f="usd"></span> for the whole conversation (agent, Emma and judge).</div>
    <div class="card step"><b>She pushed</b> to skip the preview. The agent showed it anyway.</div>
    <div class="card step"><b>She changed her mind</b> when she saw 2,400. The agent previewed 1,200 and saved only that.</div>
    <div class="card step af">The tags under each reply are the request calls of that turn, from the trace.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Score the Whole Conversation">
  <div class="lec-top"><h2>Step 3: score the conversation, not each reply</h2><p class="sub">Five checks on what the conversation <b>did</b>. Three are code. The verdicts below are for the conversation you just read.</p></div>
  <div class="fig" data-fig="mtab" data-path="m.convos.example.checks" data-cols="name:Check:x|who:Who checks:x|pass:Pass:b|why:Its reason:x" data-mk="Measured · one conversation" data-sm="1" style="left:100px;top:240px;width:1400px;height:360px"></div>
  <div class="three step" style="top:610px">
    <div class="card" style="font-size:18px"><b>End state</b> (code): after the last turn, does Ledgerline hold exactly what she wanted, and nothing else?</div>
    <div class="card" style="font-size:18px"><b>Order of actions</b> (code): across all turns, did every save follow a preview she had seen in an <b>earlier</b> turn?</div>
    <div class="card" style="font-size:18px"><b>The words</b> (judge): did it ask only what it needed, and does its last message match what Ledgerline holds?</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="The Same Emma, Thursday’s Prompt">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">The same Emma, Thursday’s prompt</h2><p class="sub" style="font-size:20px">Same goal, same persona. With a live user the shortened prompt has more room to go wrong than in a two-line script.</p></div>
  <div class="fig" data-fig="convo" data-path="m.convos.example_thursday.talk" data-sm="1" data-who="Emma (simulated)" data-to="4" style="left:100px;top:196px;width:800px;height:560px"></div>
  <div class="side" style="left:930px;top:196px;width:570px">
    <div class="fig" data-fig="mtab" data-path="m.convos.example_thursday.failed" data-cols="name:Check that failed:x|why:Its reason:x" data-mk="Two of the five checks failed (both are code)" data-sm="1" style="position:relative;height:auto"></div>
    <div class="card step bf"><b>Turn 1</b>: it saved 2,400 at once, before Emma could say she wanted 1,200.</div>
    <div class="card step"><b>Turn 2</b>: she corrected it. The 2,400 request cannot be withdrawn by the agent, so a second request appears. Ledgerline ends up holding both.</div>
    <div class="card step af">The two-line script showed <b>that</b> Thursday’s prompt saves early. The conversation shows what that costs a real user.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Twenty Conversations">
  <div class="lec-top"><h2>Twenty conversations, scored</h2><p class="sub">One conversation is a story; a grid is evidence. Five goals × two personas × two prompts. A cell passes only if all five checks pass.</p></div>
  <div class="fig" data-fig="cvgrid" style="left:100px;top:250px;width:940px;height:400px"></div>
  <span class="step" style="display:none"></span>
  <div class="kpis" style="left:1080px;top:250px;width:420px;grid-template-columns:1fr 1fr">
    <div class="kpi"><span class="k">Good prompt</span><b><span data-l6="m.convos.summary.good.passed"></span> / <span data-l6="m.convos.summary.good.conversations"></span></b><span>pass all five</span></div>
    <div class="kpi step"><span class="k">Thursday</span><b class="bad"><span data-l6="m.convos.summary.thursday.passed"></span> / <span data-l6="m.convos.summary.thursday.conversations"></span></b><span>pass all five</span></div>
    <div class="kpi"><span class="k">Code checks only</span><b><span data-l6="m.convos.summary.good.gate"></span> / <span data-l6="m.convos.summary.good.conversations"></span></b><span>good prompt</span></div>
    <div class="kpi step"><span class="k">Code checks only</span><b class="bad"><span data-l6="m.convos.summary.thursday.gate"></span> / <span data-l6="m.convos.summary.thursday.conversations"></span></b><span>Thursday</span></div>
  </div>
  <div class="look step" style="left:100px;top:680px;width:1400px;font-size:19.5px">About <span data-l6="m.convos.summary.good.mean_turns"></span> turns and <span data-l6="m.convos.summary.good.mean_usd" data-f="usd"></span> per conversation. Order of actions under Thursday: <span data-l6="m.convos.summary.thursday.by_check.order of actions across turns"></span> of 10. The two-line script caught the incident; the conversations show <b>how often</b> a real user would hit it, and in how many ways.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Read the Failures">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Read the failures before you blame the agent</h2><p class="sub" style="font-size:20px">The first failing checks of the grid, with the reason each check gave. Whose fault is each one?</p></div>
  <div class="fig" data-fig="mtab" data-path="m.convos.fails" data-limit="6" data-cols="prompt:Prompt:x|title:Goal:x|check:Check that failed:x|who:By:x|why:Its reason:x" data-mk="Measured · 20 simulated conversations" data-sm="1" style="left:100px;top:196px;width:1400px;height:500px"></div>
  <div class="three step" style="top:700px">
    <div class="card" style="font-size:17px;padding:12px 16px"><b>The agent’s</b>: asking “2,000 or 2,400?” again after Emma had said 2,000; Thursday saving in turn 1.</div>
    <div class="card" style="font-size:17px;padding:12px 16px"><b>The simulated Emma’s</b>: she asked for a preview, got it, and never said yes. Nothing saved; the end-state check failed.</div>
    <div class="card bf" style="font-size:17px;padding:12px 16px"><b>The judge’s</b>: it called a figure unsupported because the tool result it was shown had been cut short.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Our Eval Had Bugs Too">
  <div class="lec-top"><h2>Our eval had bugs too, and reading found them</h2><p class="sub">The first scoring pass said good prompt <span data-l6="m.convos.first_pass.good.passed"></span> of <span data-l6="m.convos.first_pass.good.conversations"></span>. After fixing the eval, with the agent untouched: <span data-l6="m.convos.summary.good.passed"></span> of <span data-l6="m.convos.summary.good.conversations"></span>.</p></div>
  <div class="two" style="left:100px;top:250px;width:1400px;gap:16px">
    <div class="card" style="font-size:18.5px"><span class="tag bf">A rule that misread a yes</span>Our code looked for the word “yes” and no “no” in Emma’s message. A simulated Emma wrote “Looks right, yes. No changes.” and the rule read it as a refusal. Fix: stop reading her words; require a preview in an earlier turn.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag bf">A judge that had not seen the memory</span>“Voltway is your preferred supplier” was marked unsupported: it comes from Emma’s saved memory, which we had not given the judge. Fix: the memory is evidence too.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag bf">Evidence cut from the wrong end</span>We sent the judge the first tool results of a long chat and dropped the newest ones, the ones the last reply was about. Fix: newest first.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag bf">A simulator that explained itself</span>One Emma wrote a paragraph about why she was finished, ending in “DONE”, and we sent it to the agent as a message. Fix: a message that ends in DONE ends the chat.</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:700px;font-size:21px"><b>A simulated user and a judge are models too.</b> They make mistakes. Read the transcripts of failures, fix the eval first, and only then count.</div>
</section>'''),
("new", '''<section class="slide" data-plate="The Same in DeepEval">
  <div class="lec-top"><h2>Step 4: the same pieces, ready-made, in DeepEval</h2><p class="sub">DeepEval has the conversation as a test case, judges that read all the turns, and its own simulator. Scores from NB6c, on the two conversations you read.</p></div>
  <div class="fig" data-fig="mtab" data-path="m.deepeval_conv" data-what="DeepEval’s conversational metrics on our two conversations (NB6c, live run pending)" data-cols="metric:Metric:x|good:Good prompt:n|thursday:Thursday:n|reason:The judge’s reason (Thursday):x" data-mk="Measured · NB6c · judge: Claude Haiku" data-sm="1" style="left:100px;top:250px;width:1400px;height:250px"></div>
  <div class="three step" style="top:520px">
    <div class="card" style="font-size:18.5px"><span class="tag nt">ConversationalTestCase</span>A list of turns (who said what), plus the scenario and the outcome you expected.</div>
    <div class="card" style="font-size:18.5px"><span class="tag nt">Conversational metrics</span><b>Knowledge retention</b>: did it forget or re-ask? <b>Completeness</b>: was the user’s goal met? <b>ConversationalGEval</b>: your own criterion.</div>
    <div class="card" style="font-size:18.5px"><span class="tag nt">ConversationSimulator</span>You give it a scenario and a function that answers one message with your agent. It plays the user.</div>
  </div>
  <div class="look step" style="left:100px;top:720px;width:1400px;font-size:19px">These judges read the <b>words</b>. They do not read Ledgerline or the tool calls. Use the library for the words, your own code for the facts.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Conversations in the Tools">
  <div class="lec-top"><h2>Step 5: where conversations live in the tools</h2><p class="sub">Every turn of every simulated conversation was a trace. All the turns of one conversation share a session id. So the tools already have them.</p></div>
  <div class="three" style="top:250px">
    <div class="card"><span class="tag nt">Langfuse</span><h3>Sessions</h3>A session page shows the conversation turn by turn. The longest of ours: “<span data-l6="m.tour.sessions.example" style="font:500 15px var(--mono)"></span>”, <span data-l6="m.tour.sessions.its_turns"></span> turns.</div>
    <div class="card step"><span class="tag nt">LangSmith</span><h3>Threads</h3>The same grouping, under the name thread. Our spans carry the id under both names.</div>
    <div class="card step af"><span class="tag af">Both</span><h3>Scores on a session</h3>Write each of the five checks as a score. Then “order of actions” is a line on a chart, per prompt version.</div>
  </div>
  <div class="opens step" style="top:560px;background:var(--g1)"><span class="k" style="color:var(--after)">The loop teams run</span>Simulate a set of conversations on a schedule and on every prompt change → score them with code and a calibrated judge → write the scores next to the traces → read the failures → fix the agent or the eval → add the new case to the set.</div>
</section>'''),
("new", nbslide("NB6c · Together", "NB6c_multiturn_evals", "NB6c: multi-turn evals from scratch",
                "The notebook builds everything from the last ten slides, step by step. Take your time on this one.",
                '''<div class="card" style="font-size:16.5px"><b>1</b> Scripted turns, and the script that cannot listen.<br><b>2</b> A simulated Emma in ten lines: goal, knowledge, persona.<br><b>3</b> The scorecard: end state, order of actions, turn budget, a judge.<br><b>4</b> The same Emma under Thursday’s prompt; our 20 conversations.<br><b>5</b> DeepEval’s conversational metrics and simulator; sessions in Langfuse.</div>''', 30)),
("new", '''<section class="slide" data-plate="Argus · Conversations">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Your turn: Conversations</h2><p class="sub" style="font-size:20px">Pick a goal and a persona. Watch a simulated Emma talk to <b>your</b> agent, then see the conversation scored.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/argus/conversations_v2.png" data-pending="model credit for a live run" data-label="Argus, Conversations: the goals on the left, the simulated conversation in the middle, the five checks on the right" style="left:100px;top:200px;width:1050px;height:600px"></div>
  <div class="side" style="left:1180px;top:210px;width:320px">
    <div class="card"><b>Try</b> “Changes her mind after the preview”, impatient, good prompt. Then the same on Thursday.</div>
    <div class="card"><b>Notice</b> which check fails, and in which turn the save happened.</div>
    <div class="card"><b>Then</b> your own prompt edit (Traces, My edit). Does it survive all five goals?</div>
  </div>
</section>'''),

# ------------------------------------------------------------------ shipping evals
("new", '''<section class="slide" data-plate="Two Jobs">
  <div class="lec-top"><h2>LangSmith and Langfuse do evals too</h2><p class="sub">Each does two jobs: it keeps the traces, and it runs evals on them. Sentry does the first job only.</p></div>
  <div class="l6-tw" style="position:absolute;left:100px;top:250px;width:1400px"><table class="l6t lg">
    <tr><th style="width:34%">What you need</th><th style="width:22%">LangSmith</th><th style="width:22%">Langfuse</th><th>Sentry</th></tr>
    <tr><td>Traces, sessions, cost per turn</td><td><span class="ok">yes</span></td><td><span class="ok">yes</span></td><td><span class="ok">yes</span></td></tr>
    <tr><td>Alerts on errors, speed and cost, next to the rest of the product</td><td>basic</td><td>basic</td><td><span class="ok">yes: its main job</span></td></tr>
    <tr class="step"><td><b>Scores</b> on a trace (from code, a judge or a person)</td><td><span class="ok">yes</span> (“feedback”)</td><td><span class="ok">yes</span></td><td><span class="no">no</span></td></tr>
    <tr class="step"><td><b>Datasets</b> of test cases, and <b>experiments</b> that compare two prompt versions on them</td><td><span class="ok">yes</span></td><td><span class="ok">yes</span></td><td><span class="no">no</span></td></tr>
    <tr class="step"><td><b>Judges</b> that run by themselves on new traces</td><td><span class="ok">yes</span></td><td><span class="ok">yes</span></td><td><span class="no">no</span></td></tr>
    <tr class="step"><td><b>Review queues</b>: people label a sample of traces</td><td><span class="ok">yes</span></td><td><span class="ok">yes</span></td><td><span class="no">no</span></td></tr>
  </table></div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:690px;font-size:21px"><b>In practice</b> Many teams run two tools: Sentry (or Datadog) for “is it up, fast and affordable”, and LangSmith or Langfuse for “is it right”. Libraries such as DeepEval and Ragas supply the scorers.</div>
</section>'''),
("v1", 58, [("Every change to the prompt, the tools or the guards runs the gate. Red blocks the merge.",
             "Every change to the prompt or the tools runs the tests automatically. A red test blocks the change. CI means “continuous integration”: the checks a code host runs on every proposed change."),
            ("Our gate: T01, T02 and T03 (the incident) twice each, plus T05 (closed cost centre) and T09 (the poisoned e-mail): 8 live runs, about $0.70 and 90 seconds per gate run. Only code checks: the judge is noisier and dearer, so it runs nightly.",
             "Our gate is one test file (<code>ci/test_gate.py</code>) and one workflow file: T01, T02 and T03 (the incident) twice each, plus T05 and T09: 8 live runs, about $0.70 and 90 seconds. Only code checks: the judge is noisier and dearer, so it runs nightly.")]),
("v1", 60, []),
("v1", 61, []),
("new", '''<section class="slide" data-plate="Online Evals">
  <div class="lec-top"><h2>Online evals: score what real users sent</h2><p class="sub">The gate tests before shipping, on inputs we wrote. Online evals score live traffic afterwards: inputs no test set has.</p></div>
  <div class="three" style="top:250px">
    <div class="card"><span class="tag nt">1 · Read</span><h3>Recent traces, back from the tool</h3>A small program asks Langfuse’s API for the last day’s turns and their tool calls.</div>
    <div class="card step"><span class="tag nt">2 · Score</span><h3>Code on every turn, a judge on a sample</h3>“Saved without a yes?” is code, so it runs on all of them. The judge costs money, so it reads a sample.</div>
    <div class="card step af"><span class="tag af">3 · Write back</span><h3>Scores, next to the traces</h3>Each verdict becomes a score on its trace: filter by it, chart it, alert on it, send the failures to a person.</div>
  </div>
  <div class="kpis step" style="left:100px;top:520px;width:1400px;grid-template-columns:repeat(4,1fr)">
    <div class="kpi"><span class="k">Turns scored</span><b><span data-l6="m.online.traces" data-f="n"></span></b><span>from <span data-l6="m.online.window_hours"></span> hours of our runs</span></div>
    <div class="kpi"><span class="k">Saved without a yes</span><b class="bad"><span data-l6="m.online.commit_without_yes"></span></b><span>all under the Thursday prompt</span></div>
    <div class="kpi"><span class="k">Judge, on a sample of</span><b><span data-l6="m.online.sampled_for_judge"></span></b><span>turns, for <span data-l6="m.online.judge_usd" data-f="usd"></span></span></div>
    <div class="kpi"><span class="k">Scores written</span><b><span data-l6="m.online.scores_posted" data-f="n"></span></b><span>onto the traces</span></div>
  </div>
  <div class="l6-src step" style="left:100px;top:740px;width:1400px">Langfuse and LangSmith can also run a judge themselves on each new trace, once the project owner connects a model in their settings. We ran ours as a script (<code>experiments/online_evals.py</code>).</div>
</section>'''),
("new", '''<section class="slide" data-plate="Scores on the Trace">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">The score, on Friday’s trace, in both tools</h2><p class="sub" style="font-size:20px">The same code check, written through each tool’s API. In Langfuse it is a score; in LangSmith it is feedback.</p></div>
  <div style="position:absolute;left:100px;top:200px"><span class="l6-mk">Langfuse · the trace header</span></div>
  <div class="fig" data-fig="shot" data-src="figs/langfuse/lf2_incident_tree.png" data-crop="0,215,2050,75" data-label="Langfuse: commit_without_yes True in the header of Friday's trace" style="left:100px;top:236px;width:1400px;height:52px"></div>
  <div style="position:absolute;left:100px;top:330px" class="step"><span class="l6-mk">LangSmith · the Feedback tab</span></div>
  <div class="fig step" data-fig="shot" data-src="figs/langsmith/ls_incident.png" data-crop="1290,290,1910,440" data-label="LangSmith: feedback commit_without_yes 1.00 on Friday's trace" style="left:100px;top:366px;width:760px;height:175px"></div>
  <div class="three step" style="top:570px">
    <div class="card"><b>Filter</b>: “show me every trace where this score is true.” That is the review queue.</div>
    <div class="card"><b>Chart</b>: the share of turns with the score, per day and per prompt version. A step up on Thursday is the alarm.</div>
    <div class="card af"><b>Close the loop</b>: each flagged trace becomes a new test case in the dataset.</div>
  </div>
</section>'''),
("v1", 64, []),
("v1", 65, []),
("new", '''<section class="slide" data-plate="Ragas">
  <div class="lec-top"><h2>Ragas: is the search behind the answer any good?</h2><p class="sub">For a question about a rule, Ask Northbridge first searches the policies (Lecture 3), then answers from what it found. Two halves, two ways to fail.</p></div>
  <div class="l6-tw" style="position:absolute;left:100px;top:250px;width:1400px"><table class="l6t lg">
    <tr><th style="width:19%">Metric</th><th style="width:23%">It reads</th><th style="width:30%">The question</th><th>A low score means</th></tr>
    <tr><td><b>Faithfulness</b></td><td>the answer + the clauses found</td><td>Is every claim in the answer supported by those clauses?</td><td>the model made something up</td></tr>
    <tr class="step"><td><b>Context precision</b></td><td>the clauses found + a reference answer</td><td>Are the useful clauses at the top of the list?</td><td>the search returns noise first</td></tr>
    <tr class="step"><td><b>Context recall</b></td><td>the clauses found + a reference answer</td><td>Do the clauses contain everything the reference says?</td><td>the search missed a clause</td></tr>
  </table></div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:560px;font-size:21px"><b>Ragas</b> An open-source library of ready-made metrics for search-then-answer systems, plus a few for agents. Each metric is a judge with a fixed recipe. We run it with Claude as the judge.</div>
  <div class="look step" style="left:100px;top:690px;width:1400px;font-size:19.5px">A <b>reference answer</b> is the right answer, written by a person who knows the policy. Writing references is the slow, human part. The three numbers then tell you <b>which half to fix</b>: the search, or the answer.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Ragas on Our Policies">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Ragas on our policy search, and on the agent</h2><p class="sub" style="font-size:20px">Four policy questions with references we wrote; then a planted fault; then two agent metrics on the two-turn order. From NB6d.</p></div>
  <div class="fig" data-fig="mtab" data-path="m.ragas.rows" data-what="Ragas scores on four policy questions (NB6d, live run pending)" data-cols="q:Question:x|faithfulness:Faithful:n|precision:Precision:n|recall:Recall:n" data-mk="Measured · NB6d · 4 questions" data-sm="1" style="left:100px;top:196px;width:860px;height:250px"></div>
  <div class="fig step" data-fig="mtab" data-path="m.ragas.broken" data-what="A planted wrong answer and a planted wrong search (NB6d, pending)" data-cols="case:Question 1:x|faithfulness:Faithful:n|precision:Precision:n|recall:Recall:n" data-mk="Planted faults" data-sm="1" style="left:100px;top:470px;width:860px;height:200px"></div>
  <div class="side" style="left:990px;top:196px;width:510px">
    <div class="card"><b>Read across a row.</b> High recall, low precision: the right clause was found but sits under noise. High both, low faithfulness: the answer went beyond the clauses.</div>
    <div class="card step"><b>Plant a fault</b> and see which number moves. A wrong answer should move faithfulness only; a wrong search should move precision and recall. A metric that does not move is not worth keeping.</div>
    <div class="card step"><b>Agent metrics.</b> Tool call accuracy (code): do the calls match a reference list? Good prompt <span data-l6="m.ragas.agent.good.tool_call_accuracy"></span>, Thursday <span data-l6="m.ragas.agent.thursday.tool_call_accuracy"></span>. Goal accuracy (a judge): good <span data-l6="m.ragas.agent.good.agent_goal_accuracy"></span>, Thursday <span data-l6="m.ragas.agent.thursday.agent_goal_accuracy"></span>.</div>
  </div>
  <div class="l6-src step" style="left:100px;top:700px;width:1400px">Tool call accuracy is an exact match, so we compare only the calls that change Ledgerline (one preview, then one save). Ragas does not read Ledgerline: the end-state check still decides.</div>
</section>'''),
("new", nbslide("NB6d · Together", "NB6d_ragas", "NB6d: Ragas on the policy search and the agent",
                "Short and hands-on: four questions, three metrics, two planted faults, two agent metrics.",
                '''<div class="card" style="font-size:16.5px"><b>1</b> Four policy questions with reference answers.<br><b>2</b> Search, then answer from the clauses.<br><b>3</b> Faithfulness, context precision, context recall.<br><b>4</b> Break the answer; break the search; watch which metric moves.<br><b>5</b> Tool call accuracy and goal accuracy on the two-turn order.</div>''', 15)),
("new", '''<section class="slide" data-plate="What Evals Cost">
  <div class="lec-top"><h2>What our evals cost</h2><p class="sub">Model spend from token counts × list prices. Left: the experiments behind Part 2. Right: added after the review.</p></div>
  <div class="fig" data-fig="mtab" data-path="m.spend_rows_evals" data-cols="name:Experiment:x|usd:US$:usd|calls:Model calls:n" data-mk="Measured · 16 Nov" data-sm="1" style="left:100px;top:230px;width:680px;height:470px"></div>
  <div class="fig step" data-fig="mtab" data-path="m.spend_rows_v2" data-cols="name:Added after the review:x|usd:US$:usd|calls:Model calls:n" data-mk="Measured · 16 Nov, later" data-sm="1" style="left:810px;top:230px;width:690px;height:230px"></div>
  <div class="side step" style="left:810px;top:480px;width:690px">
    <div class="card">The agent dominates: every run reads tens of thousands of tokens. Judges and the simulated Emma on a small model are cents.</div>
    <div class="card">A gate per change: about $0.70. Twenty simulated conversations: about $3. A month of nightly runs costs less than an hour of an engineer’s time.</div>
    <div class="card af">Everything measured for this lecture and tomorrow’s: <b>$<span data-l6="m.spend.v1"></span></b> for the first build + <b>$<span data-l6="m.spend.v2"></span></b> after the review.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Other Eval Tools">
  <div class="lec-top"><h2>The rest of the eval toolbox</h2><p class="sub">What else teams use, and when.</p></div>
  <div style="position:absolute;left:100px;top:240px;width:1400px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px">
    <div class="card" style="font-size:18.5px"><span class="tag nt">Platforms</span><h3>LangSmith, Langfuse, Braintrust</h3>Datasets, experiments and online scoring in one place. Braintrust is closed source and built around evals first.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag nt">Libraries</span><h3>DeepEval, Ragas, promptfoo</h3>The three we ran today: tests in Python, search metrics, prompts side by side from a config file.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag nt">Research-grade</span><h3>Inspect AI</h3>From the UK AI Security Institute, open source: tasks, solvers, scorers, sandboxes; 200+ benchmarks. Heavier than DeepEval for product tests.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag nt">MLflow 3</span><h3>Fully local</h3>Tracing and evals on your own machine. Its default judge is an OpenAI model: change it.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag nt">Benchmarks</span><h3>τ-bench and friends</h3>Public test sets with simulated users. Useful to compare models; not a test of <b>your</b> agent.</div>
    <div class="card step bf" style="font-size:18.5px"><span class="tag bf">Gone</span><h3>OpenAI Evals platform</h3>Deprecated 3 Jun 2026, shuts 30 Nov 2026; OpenAI tells users to move to Promptfoo, which it bought.</div>
  </div>
</section>'''),
("v1", 68, []),
("v1", 69, [("<span class=\"tag nt\">5 · Online evals</span><h3>On a sample of live traffic</h3>Scores on traces, alerts on drops, a human review queue.",
             "<span class=\"tag nt\">5 · Conversations, then online</span><h3>Simulated users; live samples</h3>A set of simulated conversations on a schedule; scores on live traces; a human review queue.")]),
("new", '''<section class="slide q hero chk" data-plain="1">
  <span class="hero-num q-mark" aria-hidden="true">✓</span>
  <div class="qbox">
    <p class="q-label">Check · Part 2</p>
    <ol class="chk-list">
      <li><span class="chk-q"><b>1</b>A task passes 2 of 3 runs. What are its pass@3 and pass^3?</span><span class="chk-a step">pass@3 = yes (at least one passed); pass^3 = no (not all three). For an agent that acts, pass^3 is the honest one.</span></li>
      <li><span class="chk-q"><b>2</b>Which check would have blocked Thursday’s edit, and why is it code, not a judge?</span><span class="chk-a step">“The save came only after a yes”: it reads the tool calls. Exact, free, the same verdict every run: what a gate needs.</span></li>
      <li><span class="chk-q"><b>3</b>A simulated conversation fails. Name three things that could be at fault.</span><span class="chk-a step">The agent, the simulated user, or the scorer (a code check or the judge). Read the transcript before you decide.</span></li>
    </ol>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Argus · Evals">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Your turn: Evals</h2><p class="sub" style="font-size:20px">Six tasks on any prompt, then pass^3. Here: the quick suite on the Thursday prompt, from our recording.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/argus/evals_thursday.png" data-crop="800,500,1990,1137" data-label="Argus, Evals: the quick suite on the Thursday prompt" style="left:100px;top:200px;width:1050px;height:600px"></div>
  <div class="side" style="left:1180px;top:210px;width:320px">
    <div class="card"><b>Try</b> good, then Thursday, then your own edit (Traces, My edit).</div>
    <div class="card"><b>Notice</b> where the judge and the code disagree. Click a row: every check and its reason.</div>
    <div class="card"><b>Ask</b> would your edit ship? Run pass^3 before you answer.</div>
  </div>
</section>'''),

# ------------------------------------------------------------------ close
("new", '''<section class="slide" data-plate="Friday, Caught Twice">
  <div class="lec-top"><h2>Friday’s incident, caught two ways today</h2><p class="sub">Each layer, measured on our runs. The third catch is tomorrow.</p></div>
  <div class="three" style="top:250px">
    <div class="card af"><span class="tag af">1 · The trace showed it</span><h3>One row, two facts</h3>A tool span <code>create_purchase_request</code> with <code>confirm=true</code>, in the same turn as the preview. The same row in Argus, LangSmith, Langfuse and Sentry.</div>
    <div class="card af step"><span class="tag af">2 · The eval failed the change</span><h3>Red before it ships</h3>The gate on Thursday’s prompt exits <span data-l6="m.ci.thursday.exit"></span>. The suite: <span data-l6="m.suite.thursday_k1.passed"></span>/<span data-l6="m.suite.thursday_k1.runs"></span> against <span data-l6="m.suite.good_k3.passed"></span>/<span data-l6="m.suite.good_k3.runs"></span>. Simulated conversations: <span data-l6="m.convos.summary.thursday.passed"></span>/10 against <span data-l6="m.convos.summary.good.passed"></span>/10.</div>
    <div class="card step" style="background:var(--g3)"><span class="tag nt">3 · Tomorrow · the guard refuses it</span><h3>Whatever the prompt says</h3>Code at the tool that will not save without a preview Emma saw and her yes. And attacks, to prove it holds.</div>
  </div>
  <div class="opens step" style="top:640px;background:var(--g1)"><span class="k" style="color:var(--after)">Why more than one</span>The trace explains the failure nobody predicted. The eval stops the next prompt edit that breaks a rule you already know. Neither one stops a clever attack in the moment: that is a guard’s job.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Henrik’s Answers">
  <div class="letter" style="left:200px;top:110px;width:1200px;font-size:20px">
    <div class="lh">Reply to Henrik Weber · Sat 21 Nov 2026</div>
    Henrik, two of your three questions, answered with what we measured:
    <ol><li class="step"><b>Can we see what it did, and why?</b> Yes. Every turn is a trace: each model call and tool call, with what went in, what came out, the time and the cost. Friday’s save is one row, and we can show it to you in three tools.</li>
    <li class="step"><b>Is it right, and still right after a change?</b> A 20-task suite (<span data-l6="m.suite.good_k3.passed"></span> of <span data-l6="m.suite.good_k3.runs"></span> runs pass on the current prompt), twenty simulated conversations, and a gate on every change, which fails Thursday’s edit.</li>
    <li class="step"><b>What stops what it must never do?</b> Tomorrow. Today’s layers find and prevent mistakes; they do not yet refuse an action in the moment.</li></ol>
    <span class="step">What we ask in return: an owner for the traces and the alerts, and every new incident sent to us as a test case.</span>
  </div>
</section>'''),
("new", '''<section class="slide part" data-plain="1" data-num="3">
  <div class="center"><span class="num">Your turn</span>
    <div class="recall"><b>So far</b>See it and measure it, on Ask Northbridge.</div>
    <h1 class="q2">The notebooks and the assignment</h1></div>
</section>'''),
("new", '''<section class="slide" data-plate="Four Notebooks">
  <div class="lec-top"><h2>Four notebooks, each runs two ways</h2><p class="sub">With your Argus key every call is live. With no key each notebook replays our recorded run.</p></div>
  <div style="position:absolute;left:100px;top:240px;width:1400px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
    <div class="card" style="font-size:18px"><span class="tag nt">NB6a</span><h3>Tracing</h3>By hand, with OpenTelemetry, then a real turn; the Langfuse tour.<br><br><a class="colab" style="font-size:16px;padding:11px 15px" href="https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/L6-evals-guardrails-observability/NB6a_tracing.ipynb" target="_blank" rel="noopener">Open in Colab</a></div>
    <div class="card" style="font-size:18px"><span class="tag nt">NB6b</span><h3>Evals with DeepEval</h3>Code checks, a judge by hand, tool correctness, GEval, the failing test.<br><br><a class="colab" style="font-size:16px;padding:11px 15px" href="https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/L6-evals-guardrails-observability/NB6b_evals_deepeval.ipynb" target="_blank" rel="noopener">Open in Colab</a></div>
    <div class="card" style="font-size:18px"><span class="tag nt">NB6c</span><h3>Multi-turn evals</h3>Scripts, a simulated Emma, the scorecard, DeepEval’s simulator, sessions.<br><br><a class="colab" style="font-size:16px;padding:11px 15px" href="https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/L6-evals-guardrails-observability/NB6c_multiturn_evals.ipynb" target="_blank" rel="noopener">Open in Colab</a></div>
    <div class="card" style="font-size:18px"><span class="tag nt">NB6d</span><h3>Ragas</h3>Faithfulness, context precision and recall on the policy search; agent metrics.<br><br><a class="colab" style="font-size:16px;padding:11px 15px" href="https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/L6-evals-guardrails-observability/NB6d_ragas.ipynb" target="_blank" rel="noopener">Open in Colab</a></div>
  </div>
  <div class="look step" style="left:100px;top:600px;width:1400px;font-size:19.5px"><span class="k">How the live mode works</span>In Argus press <b>Notebook key</b> and paste the two lines into the notebook. Argus’s gateway accepts that key in place of a model key, serves only the course’s two models, and counts the spend against your own Argus budget. You never need an Anthropic key of your own.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Argus at Class Scale">
  <div class="lec-top"><h2>Argus, tested before class</h2><p class="sub">The lab’s own evals: an API test on the live address and a load test with 30 simulated students.</p></div>
  <div class="kpis" style="left:100px;top:250px;width:1400px;grid-template-columns:repeat(3,1fr)">
    <div class="kpi"><span class="k">API test</span><b class="good"><span data-l6="m.argus_test.passed"></span>/<span data-l6="m.argus_test.of"></span></b><span>checks passed on the live address (16 Nov)</span></div>
    <div class="kpi step"><span class="k">Load test</span><b class="good"><span data-l6="m.argus_load.students_ok"></span>/<span data-l6="m.argus_load.n"></span></b><span>students at once, no errors</span></div>
    <div class="kpi step"><span class="k">Chat turn, p95</span><b><span data-l6="m.argus_load.chat_s.p95"></span> s</b><span>under load (agent on the small model for the test)</span></div>
  </div>
  <div class="look step" style="left:100px;top:470px;width:1400px">Three stations today: <b>Traces</b>, <b>Evals</b>, <b>Conversations</b>. Each student has a budget cap, and the class has one; the gateway for the notebooks counts against the same caps. In class the agent runs on Claude Sonnet.</div>
</section>'''),
("new", '''<section class="slide" data-plate="A6">
  <div class="lec-top"><h2>A6: see and measure one agent of yours</h2><p class="sub">Take an agent you built (or Ask Northbridge). 100 points. Details in <code>A6.md</code>.</p></div>
  <div style="position:absolute;left:100px;top:240px;width:1400px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
    <div class="card" style="font-size:18.5px"><span class="tag af">Part 1 · 25</span><h3>Trace it</h3>OpenTelemetry spans with the agreed names, sent to LangSmith or Langfuse. One screenshot of a failure in a trace, explained.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag af">Part 2 · 30</span><h3>Evaluate it</h3>Read 20 traces first. Then 10 tasks with code checks and one judge criterion each; pass^3; the judge against 20 labels of your own.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag af">Part 3 · 30</span><h3>Test a conversation</h3>A simulated user with three goals and two personas; score end state, order of actions and one judged criterion. Report what failed, and whose fault it was.</div>
    <div class="card step" style="font-size:18.5px"><span class="tag af">Part 4 · 15</span><h3>Gate it</h3>A test run that fails a bad prompt change, and its output.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Further Reading">
  <div class="lec-top"><h2>To go further</h2><p class="sub">Primary sources for today, all in <code>research/TOOLS_RESEARCH.md</code> with links.</p></div>
  <div style="position:absolute;left:100px;top:240px;width:1400px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px">
    <div class="card" style="font-size:18.5px"><span class="tag nt">Standards</span><h3>Specs to read</h3>The OpenTelemetry GenAI semantic conventions (the naming guide for agent spans); the OTLP specification.</div>
    <div class="card" style="font-size:18.5px"><span class="tag nt">Tool docs</span><h3>The tools we ran</h3>LangSmith (trace with OpenTelemetry, share a trace, feedback); Langfuse (OTel endpoint, scores, datasets, prompts); Sentry (OTLP, agent monitoring); DeepEval; Ragas; promptfoo.</div>
    <div class="card" style="font-size:18.5px"><span class="tag nt">Ideas</span><h3>Behind the methods</h3>τ-bench: simulated users and pass^k; error analysis by open and axial coding; Cohen’s kappa; LLM-as-judge: binary, one criterion, evidence, reason first.</div>
  </div>
  <div class="look" style="left:100px;top:600px;width:1400px">Every number about our agent today: <code>lectures/L6-evals-guardrails-observability/experiments/logs/</code>, read by <code>gen_figdata.py</code>. Run it yourself in the four notebooks.</div>
</section>'''),
("new", '''<section class="slide" data-plain="1">
  <div class="center" style="text-align:center;align-items:center">
    <div class="kicker">Next time · Lecture 7 · Sun 22 Nov 2026</div>
    <h1 style="font-size:96px">Guardrails and Red-Teaming</h1>
    <p class="lede" style="max-width:1050px;margin-top:24px">Today we learned to see Ask Northbridge and to measure it. Tomorrow we bound it: code that refuses what it must never do, and attacks to prove the refusal holds. Henrik’s third question.</p>
  </div>
</section>'''),
]
