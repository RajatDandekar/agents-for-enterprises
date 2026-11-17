# -*- coding: utf-8 -*-
"""Lecture 6 v2 · Part 1 continued: the same turn in the tools teams use."""
P1 = [
("new", '''<section class="slide" data-plate="The Market, With Caveats">
  <div class="lec-top" style="top:90px"><h2 style="font-size:50px">Which tools teams use, and why we show these three</h2><p class="sub" style="font-size:21px">Stack Overflow Developer Survey 2026: “used for AI agent observability, prompts or evals in the past year”, n = 2,277.</p></div>
  <div class="fig" data-fig="bars" data-f="n" data-max="30" data-lw="260"
    data-bars='[["Sentry",26.0,"good"],["LangSmith",17.3,"good"],["MLflow",15.2,"grey"],["Langfuse",15.2,"good"],["Datadog LLM",11.9,"grey"],["W&amp;B",10.7,"grey"],["Braintrust",5.8,"grey"],["DeepEval",5.8],["Promptfoo",5.3]]'
    style="left:100px;top:226px;width:860px;height:520px"></div>
  <div class="side" style="left:1000px;top:230px;width:500px">
    <div class="card" style="font-size:17.5px"><b>Sentry</b>: the monitoring tool most teams already run for errors and speed; it now reads AI agent spans too.</div>
    <div class="card step" style="font-size:17.5px"><b>LangSmith</b>: the most used tool built for LLM apps. Closed source, from the LangChain team; works with any agent.</div>
    <div class="card step" style="font-size:17.5px"><b>Langfuse</b>: the most used open-source one (MIT licence). You can run it on your own servers.</div>
    <div class="card step bf" style="font-size:17.5px"><b>Read with care</b> Developers, not companies; self-reported; percent of respondents. Tools are bought and closed every few months: check a tool’s status before you adopt it.</div>
  </div>
  <div class="l6-src" style="left:100px;top:770px;width:860px">Source: survey.stackoverflow.co/2026/ai (via research/TOOLS_RESEARCH.md §0). Dark green: the three we open today. DeepEval and Promptfoo return in Part 2.</div>
</section>'''),
# ------------------------------------------------------------------ LangSmith
("new", '''<section class="slide" data-plate="LangSmith">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">LangSmith: the stock question</h2><p class="sub" style="font-size:20px">The same four spans, sent by OpenTelemetry. This page is public: we shared the trace by link, so it opens without an account.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/langsmith/ls_ordinary.png" data-crop="0,270,1280,660" data-label="LangSmith: the stock question as a tree" style="left:100px;top:200px;width:560px;height:289px"></div>
  <div class="side" style="left:100px;top:510px;width:560px">
    <div class="card"><b>Left</b>: the trace as a tree. The same four rows as in Argus, with seconds and tokens. The top row carries the turn’s tokens and cost: equal to ours to the last digit.</div>
    <div class="card step"><b>Right</b>: the row you clicked. Input and Output of the whole turn, and a score (LangSmith calls it feedback).</div>
    <div class="card step" style="background:var(--g3)"><b>How it got there</b>: two settings, <code>LANGSMITH_API_KEY</code> and LangSmith’s address for OpenTelemetry. No LangSmith library, no LangChain.</div>
  </div>
  <div class="fig" data-fig="shot" data-src="figs/langsmith/ls_ordinary.png" data-crop="1290,270,1910,1710" data-label="LangSmith: input and output of the stock question" style="left:700px;top:200px;width:720px;height:645px"></div>
</section>'''),
("new", '''<section class="slide" data-plate="Friday in LangSmith">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Friday’s turn in LangSmith</h2><p class="sub" style="font-size:20px">The Thursday prompt. One message in, one reply out, <span data-l6="m.demo.incident.spans"></span> rows, and a score on the turn.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/langsmith/ls_incident.png" data-crop="0,270,1280,1710" data-label="LangSmith: Friday's turn as a tree" style="left:100px;top:196px;width:400px;height:535px"></div>
  <div class="side" style="left:100px;top:748px;width:400px"><div class="card" style="font-size:16.5px;padding:11px 14px"><b>The tree</b>: five model calls, seven tool calls; two are <code>create_purchase_request</code>.</div></div>
  <div class="fig" data-fig="shot" data-src="figs/langsmith/ls_incident.png" data-crop="1290,270,1910,1630" data-label="LangSmith: Friday's turn, feedback, input and output" style="left:530px;top:196px;width:740px;height:632px"></div>
  <div class="side step" style="left:1295px;top:196px;width:205px">
    <div class="card" style="font-size:16px;padding:12px 14px"><b>Feedback</b> is LangSmith’s word for a score.<br><code style="font-size:12.5px">commit_without_yes 1.00</code><br>Our code wrote it.</div>
    <div class="card bf" style="font-size:16px;padding:12px 14px"><b>The reply</b> reads calm and correct. The tree is where the problem shows.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="The Save in LangSmith">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">The row that saved the request, in LangSmith</h2><p class="sub" style="font-size:20px">Click the second <code>create_purchase_request</code>. The same two facts as in Argus: the arguments, and the result.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/langsmith/ls_incident_commit.png" data-crop="1290,270,1910,1540" data-label="LangSmith: the tool call with confirm true, and its result" style="left:100px;top:200px;width:800px;height:645px"></div>
  <div class="side" style="left:940px;top:200px;width:560px">
    <div class="card bf"><b>Input</b>: what the model sent to the tool. <code>confirm true</code>, 2,400 BAT-500, cost centre PRD-03.</div>
    <div class="card step bf"><b>Output</b>: what Ledgerline answered. A request number was issued, and the approver is Daniel.</div>
    <div class="card step"><b>Same span, second screen.</b> LangSmith calls it a tool run; Argus drew it as the red row. Nothing was added or lost on the way.</div>
    <div class="card step" style="background:var(--g3)"><b>Public link</b> to this trace (no account needed): <span style="font-size:14px" data-l6="m.demo.incident.links.langsmith_public" data-f="url"></span></div>
  </div>
</section>'''),
# ------------------------------------------------------------------ Langfuse
("new", '''<section class="slide" data-plate="Langfuse">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Langfuse: the same turn, the open-source tool</h2><p class="sub" style="font-size:20px">Friday’s trace again. The header carries our labels; the tree carries a cost on every model call.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/langfuse/lf2_incident_tree.png" data-crop="0,125,2050,165" data-label="Langfuse: the header of Friday's trace" style="left:560px;top:196px;width:940px;height:76px"></div>
  <div class="fig" data-fig="shot" data-src="figs/langfuse/lf2_incident_tree.png" data-crop="0,425,1150,1525" data-label="Langfuse: the tree of Friday's trace" style="left:100px;top:196px;width:430px;height:570px"></div>
  <div class="side" style="left:560px;top:296px;width:450px">
    <div class="card"><b>The header</b>: 14.7 s, the cost, the tokens, a link to the <b>session</b>, the <b>user</b>, our tags, and the score <code>commit_without_yes: True</code>.</div>
    <div class="card step"><b>The tree</b>: pink for a generation, orange for a tool. Langfuse marks the tool call that returned an error.</div>
    <div class="card step"><b>How it got there</b>: three settings (two keys and the address). The same OpenTelemetry spans.</div>
  </div>
  <div class="side step" style="left:1040px;top:296px;width:460px">
    <div class="card" style="background:var(--g3)"><b>Open source, MIT licence.</b> Use their cloud, or run it yourself (it needs a few databases). ClickHouse bought the company in Jan 2026; the licence did not change.</div>
    <div class="card"><b>Free tier</b>: traces kept 30 days. Enough for this course and a small pilot.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Where the Time Went">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Langfuse: where the time went, and one model call opened</h2><p class="sub" style="font-size:20px">The Timeline view puts every span on one clock. Then click a generation to read what the model was sent and what it wrote.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/langfuse/lf2_incident_timeline.png" data-crop="0,300,1150,1065" data-label="Langfuse: the timeline of Friday's trace" style="left:100px;top:200px;width:620px;height:580px"></div>
  <div class="fig step" data-fig="shot" data-src="figs/langfuse/lf_signed_in_generation.png" data-pending="signed-in Langfuse" data-label="Langfuse, signed in: one generation of Friday’s trace with its Input and Output panels" style="left:750px;top:200px;width:750px;height:380px"></div>
  <div class="side step" style="left:750px;top:600px;width:750px">
    <div class="card" style="font-size:18px"><b>Read the bars</b>: the pink bars (the model) are almost all of the 14.7 seconds. The tools are a millisecond each. To make this agent faster, make fewer model calls.</div>
    <div class="card" style="font-size:18px"><b>Live</b>: I open this trace signed in and click through Input, Output, Metadata and Scores.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Two Turns in Langfuse">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Langfuse: what right looks like, two turns side by side</h2><p class="sub" style="font-size:20px">The good prompt. Both traces belong to one session, so Langfuse can show them as one conversation.</p></div>
  <div style="position:absolute;left:100px;top:196px"><span class="l6-mk">Turn 1 · the preview</span></div>
  <div class="fig" data-fig="shot" data-src="figs/langfuse/lf2_good_turn1.png" data-crop="0,125,1150,800" data-label="Langfuse: turn 1, the preview" style="left:100px;top:232px;width:520px;height:362px"></div>
  <div style="position:absolute;left:660px;top:196px" class="step"><span class="l6-mk">Turn 2 · after “Yes, go ahead.”</span></div>
  <div class="fig step" data-fig="shot" data-src="figs/langfuse/lf2_good_turn2.png" data-crop="0,125,1150,1190" data-label="Langfuse: turn 2, the save" style="left:660px;top:232px;width:520px;height:538px"></div>
  <div class="side" style="left:1210px;top:232px;width:290px">
    <div class="card" style="font-size:17.5px"><b>Turn 1</b> has one <code>create_purchase_request</code>: the preview. Then the turn ends and Emma reads it.</div>
    <div class="card step af" style="font-size:17.5px"><b>Turn 2</b> has the save, after her yes. Two traces, one after the other.</div>
    <div class="card step bf" style="font-size:17.5px"><b>Friday</b> had both in one trace. The difference between right and wrong here is one line: where the turn ends.</div>
  </div>
</section>'''),
# ------------------------------------------------------------------ Sentry
("new", '''<section class="slide" data-plate="Sentry">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Sentry: the same turn, in the monitoring tool</h2><p class="sub" style="font-size:20px">Sentry watches the whole product: errors, slow pages, crashes. It now reads AI agent spans too, so the agent sits next to everything else.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/sentry/sn_incident_trace.png" data-pending="signed-in Sentry (it has no public link)" data-label="Sentry, Explore, Traces: Friday’s turn as a waterfall: the agent turn, 5 model calls, 7 tool calls" style="left:100px;top:200px;width:900px;height:520px"></div>
  <div class="side" style="left:1030px;top:200px;width:470px">
    <div class="card"><b>What arrived</b> (read back through Sentry’s API): Friday’s <span data-l6="m.demo.incident.back.sentry.spans"></span> spans, with messages, tool arguments, tool results and tokens.</div>
    <div class="card step"><b>How it got there</b>: one setting, <code>SENTRY_DSN</code> (the project’s address). The same OpenTelemetry spans; no Sentry library.</div>
    <div class="card step"><b>Cost</b>: Sentry estimates it from its own price table, or keeps the figure you send. We send ours.</div>
    <div class="card step bf"><b>What it is for</b>: “is the agent slow, failing or expensive today?” Alerts and dashboards. It does not test whether an answer was right.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Sentry · Agents">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Sentry: the save, and the agents overview</h2><p class="sub" style="font-size:20px">The span’s details on the left. On the right, what on-call opens first: every agent run, model call and tool call of the day, counted.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/sentry/sn_incident_commit.png" data-pending="signed-in Sentry" data-label="Sentry: the create_purchase_request span of Friday’s turn, with its arguments (confirm true) and result" style="left:100px;top:200px;width:680px;height:470px"></div>
  <div class="fig step" data-fig="shot" data-src="figs/sentry/sn_agents.png" data-pending="signed-in Sentry" data-label="Sentry, Explore, Agents: runs, model calls, tokens, cost and tool calls for the last 24 hours" style="left:820px;top:200px;width:680px;height:470px"></div>
  <div class="look step" style="left:100px;top:700px;width:1400px;font-size:19.5px"><span class="k">Same span, third screen</span>The arguments are the same <code>confirm: true</code>. What Sentry adds is the neighbourhood: the web request that started this turn, the database queries around it, and an alert when the error rate or the cost jumps.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Three Tools, One Trace">
  <div class="lec-top"><h2>Sent once. Read back from all three.</h2><p class="sub">We did not trust the screens. We asked each tool’s own API for our four demo turns and compared with what we sent.</p></div>
  <div class="l6-tw" style="position:absolute;left:100px;top:250px;width:1400px"><span class="l6-mk">Measured · 16 Nov 2026 · experiments/readback.py</span><table class="l6t lg">
    <tr><th>Tool</th><th>Turns that arrived</th><th>With input and output</th><th>Tokens equal to ours</th><th>Cost equal to ours</th></tr>
    <tr><td><b>LangSmith</b></td><td><span data-l6="m.demo.readback_by_tool.LangSmith.traces"></span> of <span data-l6="m.demo.readback_by_tool.LangSmith.of"></span></td><td><span data-l6="m.demo.readback_by_tool.LangSmith.io"></span></td><td><span data-l6="m.demo.readback_by_tool.LangSmith.tokens_match"></span></td><td><span data-l6="m.demo.readback_by_tool.LangSmith.cost_match"></span></td></tr>
    <tr><td><b>Langfuse</b></td><td><span data-l6="m.demo.readback_by_tool.Langfuse.traces"></span> of <span data-l6="m.demo.readback_by_tool.Langfuse.of"></span></td><td><span data-l6="m.demo.readback_by_tool.Langfuse.io"></span></td><td><span data-l6="m.demo.readback_by_tool.Langfuse.tokens_match"></span></td><td><span data-l6="m.demo.readback_by_tool.Langfuse.cost_match"></span></td></tr>
    <tr><td><b>Sentry</b></td><td><span data-l6="m.demo.readback_by_tool.Sentry.traces"></span> of <span data-l6="m.demo.readback_by_tool.Sentry.of"></span></td><td><span data-l6="m.demo.readback_by_tool.Sentry.io"></span></td><td><span data-l6="m.demo.readback_by_tool.Sentry.tokens_match"></span></td><td><span data-l6="m.demo.readback_by_tool.Sentry.cost_match"></span> <span style="color:var(--ink-3);font-size:16px">(see below)</span></td></tr>
  </table></div>
  <div class="three step" style="top:520px">
    <div class="card"><span class="tag nt">Why it worked three times</span>One format (OpenTelemetry) and agreed names. Each tool needed one or two extra labels of its own; we set them all on the same span.</div>
    <div class="card bf"><span class="tag bf">The one difference</span>On our first send Sentry priced Friday’s turn at <span data-l6="m.demo.sentry_first.cost" data-f="usd"></span>; ours was <span data-l6="m.demo.sentry_first.sent" data-f="usd"></span>. We had not given it our figure, so it used its own price table. We now send ours in Sentry’s own cost field.</div>
    <div class="card af"><span class="tag af">The lesson</span>Check that what you sent is what arrived. A tracing set-up that silently drops the input is how the “empty Input” screens of a first attempt happen.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Live · A Tour of Langfuse">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Live: what Langfuse keeps around the traces</h2><p class="sub" style="font-size:20px">Four things sit around the traces. Part 2 uses every one of them. Numbers below: what the API answered on 16 Nov.</p></div>
  <div class="lab4" style="left:100px;top:200px;width:800px;gap:14px">
    <div class="card" style="font-size:17.5px"><h3>Sessions</h3>Whole conversations. In the newest <span data-l6="m.tour.sessions.turns_read"></span> turns: <span data-l6="m.tour.sessions.sessions_among_them"></span> sessions; the longest has <span data-l6="m.tour.sessions.its_turns"></span> turns.</div>
    <div class="card step" style="font-size:17.5px"><h3>Scores</h3>Verdicts on traces. Names in use: <span data-l6="m.tour.score_names" style="font:500 14.5px var(--mono)"></span>.</div>
    <div class="card step" style="font-size:17.5px"><h3>Datasets</h3>Turns saved as test cases: “<span data-l6="m.tour.dataset"></span>” holds <span data-l6="m.tour.dataset_items"></span> items, each with what we expect.</div>
    <div class="card step" style="font-size:17.5px"><h3>Prompt versions</h3>The system prompt, versioned. Labels: <span data-l6="m.tour.prompt.labels" style="font:500 14.5px var(--mono)"></span>. Rolling back is moving a label.</div>
  </div>
  <div class="fig" data-fig="shot" data-src="figs/langfuse/lf_signed_in_session.png" data-pending="signed-in Langfuse" data-label="Langfuse, signed in: a session page (one conversation, turn by turn), then Scores, Datasets and Prompts" style="left:930px;top:200px;width:570px;height:400px"></div>
  <div class="look step" style="left:100px;top:640px;width:1400px;font-size:19.5px"><span class="k">Click path, live</span>Tracing → Sessions → open the longest one. Then Scores. Then Datasets → ask-northbridge-incident. Then Prompts → ask-northbridge → compare version 1 and version 2: that is Thursday’s edit. LangSmith has the same four things (threads, feedback, datasets, prompts).</div>
</section>'''),
("v1", 34, [("Computed from Langfuse’s public API over every trace of our runs (the dashboards themselves need a logged-in UI).",
             "Numbers worked out from our own traces, read back through Langfuse’s API. p50 is the middle turn; p95 is the slow end: 95 of 100 turns are faster.")]),
("v1", 35, []),
("v1", 36, [("Head sampling keeps a fixed share; tail sampling keeps every error and slow turn. A collector does it, not your code.",
             "At scale you keep a share of ordinary turns, and every error and every slow turn."),
            ("Code and judge scores written onto live traces (Section 2), reviewed in a queue by people.",
             "Code and judge scores written onto live traces (Part 2), reviewed in a queue by people.")]),
("new", '''<section class="slide q hero chk" data-plain="1">
  <span class="hero-num q-mark" aria-hidden="true">✓</span>
  <div class="qbox">
    <p class="q-label">Check · Part 1</p>
    <ol class="chk-list">
      <li><span class="chk-q"><b>1</b>What turns a list of spans into a tree?</span><span class="chk-a step">The parent. Every span records which span it happened inside; the first span of a turn has none.</span></li>
      <li><span class="chk-q"><b>2</b>Why did the same spans open in LangSmith, Langfuse and Sentry without changing our code?</span><span class="chk-a step">OpenTelemetry: one format and agreed names (chat, execute_tool, invoke_agent). Each tool only needed its key.</span></li>
      <li><span class="chk-q"><b>3</b>On Friday’s trace, which two facts prove the save had no yes?</span><span class="chk-a step">A tool span <code>create_purchase_request</code> with <code>confirm=true</code>, and the preview in the same turn: no message from Emma in between.</span></li>
    </ol>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Argus · Traces">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Your turn: Traces</h2><p class="sub" style="font-size:20px">Your own Ask Northbridge in your own Ledgerline sandbox. A laptop and a browser; no keys.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/argus/traces_thursday.png" data-crop="1240,520,1960,1120" data-label="Argus, Traces: the Thursday prompt's turn and its trace" style="left:100px;top:200px;width:1050px;height:600px"></div>
  <div class="side" style="left:1180px;top:210px;width:320px">
    <div class="card"><b>Try</b> “Order the usual, please, needed by 4 Dec 2026.”, good prompt, then Thursday.</div>
    <div class="card"><b>Notice</b> the red row: <code>confirm=true</code>. Click it: the arguments and the result.</div>
    <div class="card"><b>Then</b> the buttons under the trace: open the same turn in LangSmith, Langfuse or Sentry.</div>
  </div>
  <div class="l6-src" style="left:100px;top:812px;width:1050px;font-size:17px">Argus: <span data-l6="m.argus_url" data-f="url"></span></div>
</section>'''),
]
