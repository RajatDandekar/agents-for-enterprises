# -*- coding: utf-8 -*-
"""Lecture 6 v2 · the opener and Part 1 (Observability). Each entry: ("v1", n, [(old, new), ...]) or ("new", html)."""
KICK = "Agentic Systems Engineering · Lecture 6 of 11 · Sat 21 Nov 2026 · Dr. Rajat Dandekar, Vizuara"
GH = "https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/L6-evals-guardrails-observability/"


def nbslide(plate, nb, title, sub, cells, mins):
    return f'''<section class="slide" data-plate="{plate}">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">{title}</h2><p class="sub" style="font-size:20px">{sub}</p></div>
  <div class="fig" data-fig="nbframe" data-src="nb/{nb}.html" data-label="{nb}.ipynb, as our live run left it" data-pending="model credit for the live run" style="left:100px;top:206px;width:980px;height:640px"></div>
  <div class="side" style="left:1110px;top:206px;width:390px">
    <div class="card" style="background:var(--g3)"><a class="colab" href="{GH}{nb}.ipynb" target="_blank" rel="noopener">Open {nb.split("_")[0]} in Colab</a><span class="cl-u">{nb}.ipynb · about {mins} minutes together</span></div>
    {cells}
    <div class="card" style="font-size:16.5px"><b>Two ways to run it.</b> Paste your Argus key (button “Notebook key”): every call is live. No key: it replays our recorded run.</div>
  </div>
</section>'''


P0 = [
("new", f'''<section class="slide" data-plain="1">
  <div class="center">
    <div class="kicker">{KICK}</div>
    <h1 style="font-size:104px">Observability and Evals</h1>
    <p class="lede" style="margin-top:26px">Ask Northbridge goes to 40 buyers on Monday. Today we watch every step it takes, and we test it before any change ships. We start with a live demo, then explain each idea from what we saw, with the tools teams use and four notebooks we run together.</p>
  </div>
  <div class="pnote" id="pnote" role="note"><span class="k">Presenter · before class · hides on your first click</span>
    <ol><li><b>30 min before: warm Argus.</b> <code>modal run deploy/argus_modal.py::admin --cmd warm</code>, then <code>--cmd status</code> (README: <code>ledgerline/ledgerline/argus/README.md</code>).</li>
    <li><b>Then</b> <code>--cmd purge-tests</code>; join Argus yourself. Open, signed in: LangSmith, Langfuse, Sentry (links in NOTES.md).</li>
    <li><b>Open the four notebooks in Colab</b> and run each first cell (the install takes a minute).</li>
    <li><b>Never redeploy Argus in class.</b> After class: <code>--cmd cool</code>.</li></ol></div>
</section>'''),
("v1", 2, [("Three layers around it", "Two layers today, one tomorrow"),
           ("Observability to see it. Evals to measure it. Guardrails to bound it. Nothing inside the agent changes.",
            "Observability to see it. Evals to measure it. Tomorrow: guardrails to bound it. Nothing inside the agent changes."),
           ("What did it do on Friday at 09:10? Is it still right after Thursday’s change? What stops the one action it must never take?",
            "What did it do on Friday at 09:10? Is it still right after Thursday’s change?")]),
("v1", 3, []),
("v1", 4, []),
("v1", 5, []),
("new", '''<section class="slide" data-plate="How Often?">
  <div class="lec-top"><h2>We reproduced it, and measured it</h2><p class="sub">Fresh sandboxes, the same model, one message. After each run we read Ledgerline: was a request saved without Emma’s yes?</p></div>
  <div class="fig" data-fig="bars" data-f="frac" data-lw="560" data-max="1"
    data-bars='[["Good prompt · “Order the usual, please, needed by 4 Dec 2026.”","m.incident.dated.good.committed","good"],["Thursday prompt · the same message","m.incident.dated.thursday.committed","bad"],["Good prompt · “Order the usual, please.” (no date)","m.incident.nodate.good.committed","good"],["Thursday prompt · no date","m.incident.nodate.thursday.committed","bad"]]'
    data-steps="0,0,1,1" style="left:100px;top:250px;width:1400px;height:270px"></div>
  <span class="step" style="display:none"></span>
  <div class="look step" style="left:100px;top:540px;width:1400px;font-size:21px"><span class="k">What “61%” means</span>With no date, the Thursday prompt saved without a yes in <b><span data-l6="m.incident.nodate.thursday.committed"></span> of <span data-l6="m.incident.nodate.thursday.runs"></span></b> runs (<span data-l6="m.incident.nodate_rate_pct"></span>%). So one try looks fine <span data-l6="m.incident.nodate_fine_pct"></span>% of the time. Someone who tries it three times sees three good answers this often:</div>
  <div class="sum step" style="left:100px;top:690px;width:1400px">
    <span class="bx"><span data-l6="m.incident.fine1"></span><small>try 1 looks fine</small></span><span class="x">×</span>
    <span class="bx"><span data-l6="m.incident.fine1"></span><small>try 2 looks fine</small></span><span class="x">×</span>
    <span class="bx"><span data-l6="m.incident.fine1"></span><small>try 3 looks fine</small></span><span class="x">=</span>
    <span class="bx"><b><span data-l6="m.incident.vibe3_miss_pct"></span>%</b><small>all three look fine: the bug ships</small></span>
  </div>
</section>'''),
("v1", 7, [("Section 1 answers it", "Part 1 answers it")]),
("new", '''<section class="slide" data-plate="Three Questions">
  <div class="lec-top"><h2>Two of Henrik’s questions today, the third tomorrow</h2><p class="sub">Each one is a layer we put around the agent. Nothing inside the agent changes.</p></div>
  <div class="three" style="top:250px">
    <div class="card af"><span class="tag af">Today · Part 1 · Observability</span><h3>See it</h3>Every turn is recorded step by step: each call to the model, each tool call, with what went in and what came out. <b>The record shows</b> the save that Emma never confirmed.</div>
    <div class="card af step"><span class="tag af">Today · Part 2 · Evals</span><h3>Measure it</h3>A set of test conversations, checked by code and by a second model, run on every change. <b>The test fails</b> Thursday’s edit before it ships.</div>
    <div class="card step" style="background:var(--g3)"><span class="tag nt">Tomorrow · Lecture 7</span><h3>Bound it</h3>Guardrails and red-teaming: code that refuses what the agent must never do, whatever the prompt says, and attacks to prove it holds.</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:640px;font-size:22px"><b>One rule for both days</b> The model decides what to try. Code records what happened, and code decides what is allowed.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Today’s Map">
  <div class="lec-top"><h2>Today: a demo first, then the ideas behind it</h2><p class="sub">Everything on the left you watch; everything in gold you do with me, in Argus or in a Colab notebook.</p></div>
  <div class="map6" style="grid-template-columns:repeat(4,1fr)">
    <div class="card"><b>Part 1 · Observability</b>a live chat with its trace; then span, trace, model call, tool call, session, cost, score, each from that trace</div>
    <div class="card"><b>The same turn in three tools</b>LangSmith, Langfuse and Sentry, on our own data</div>
    <div class="card lv"><b>NB6a · together</b>tracing by hand, then with OpenTelemetry, then for real</div>
    <div class="card lv"><b>Argus · Traces</b>your own Ask Northbridge, your own traces</div>
    <div class="card"><b>Part 2 · Evals</b>code checks, an LLM judge and when we need one, is the judge right, pass^k, the gate</div>
    <div class="card"><b>Conversations</b>multi-turn evals from scratch: a simulated Emma, scoring the whole chat</div>
    <div class="card lv"><b>NB6b · NB6c · NB6d</b>DeepEval; multi-turn evals; Ragas</div>
    <div class="card lv"><b>Argus · Evals · Conversations</b>would your prompt ship?</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:650px;font-size:21px"><b>Measured, not claimed</b> Every number about our agent comes from our own runs (16 Nov 2026). <b>Next · Lecture 7 · Sun 22 Nov:</b> Guardrails and Red-Teaming.</div>
</section>'''),

# ------------------------------------------------------------------ PART 1
("new", '''<section class="slide part" data-plain="1" data-num="1">
  <div class="center"><span class="num">Part 1 of 2 · Observability</span>
    <div class="recall"><b>Henrik asks</b>When it does something odd, can we see exactly what it did, and why?</div>
    <h1 class="q2">First, watch it work</h1></div>
</section>'''),
("new", '''<section class="slide" data-plate="Live Demo · Argus">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">Live: a chat on the left, its trace on the right</h2><p class="sub" style="font-size:20px">Argus, the Traces station. I type as Emma; you watch what Ask Northbridge does, step by step, as it happens.</p></div>
  <div class="fig" data-fig="shot" data-src="figs/argus/traces_v2.png" data-pending="model credit for a live turn" data-label="Argus, Traces: the chat, the trace beside it, and the “Open in LangSmith / Langfuse / Sentry” buttons" style="left:100px;top:200px;width:900px;height:560px"></div>
  <div class="side" style="left:1030px;top:200px;width:470px">
    <div class="card"><b class="n">1</b>Type: <b>“How many BAT-500 battery packs do we have?”</b> Watch the rows appear on the right.</div>
    <div class="card step"><b class="n">2</b>Click a row. It opens: what went in, what came out, how long, how much.</div>
    <div class="card step"><b class="n">3</b>Type: <b>“Order the usual, please, needed by 4 Dec 2026.”</b> Then: “Yes, go ahead.”</div>
    <div class="card step"><b class="n">4</b>Switch the prompt to <b>Thursday</b>. Ask for the usual again. Find the red row.</div>
    <div class="card" style="background:var(--g3)"><span class="live" style="font-size:15px;padding:8px 12px"><span data-l6="m.argus_url" data-f="url"></span></span></div>
  </div>
  <div class="l6-src" style="left:100px;top:780px;width:900px">The next slides use the same four turns, recorded on <span data-l6="m.demo.at"></span>, so every number is one you can check.</div>
</section>'''),
("new", '''<section class="slide" data-plate="What We Just Saw">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">One question, one answer, and four records behind it</h2><p class="sub" style="font-size:20px">Left: what Emma sees. Right: what the system recorded while it worked. Our run, <span data-l6="m.demo.at"></span>.</p></div>
  <div class="fig" data-fig="convo" data-path="m.demo.ordinary.talk" style="left:100px;top:210px;width:560px;height:560px"></div>
  <div class="fig step" data-fig="trace" data-path="m.demo.ordinary.trace" data-nw="330" style="left:700px;top:210px;width:800px;height:230px"></div>
  <div class="three step" style="left:700px;right:100px;top:470px;grid-template-columns:1fr 1fr 1fr;gap:14px">
    <div class="card" style="font-size:18px"><b>4 rows</b><br>the turn, two calls to the model, one tool call.</div>
    <div class="card" style="font-size:18px"><b><span data-l6="m.demo.ordinary.seconds" data-f="s"></span></b><br>from her message to the reply.</div>
    <div class="card" style="font-size:18px"><b><span data-l6="m.demo.ordinary.tokens" data-f="n"></span> tokens · <span data-l6="m.demo.ordinary.usd" data-f="usd"></span></b><br>read and written by the model.</div>
  </div>
  <div class="def step" style="position:absolute;left:700px;right:100px;top:640px;font-size:20px"><b>Observability</b> Being able to answer a new question about what the system did, from the records it left, without running it again.</div>
</section>'''),
("new", '''<section class="slide" data-plate="A Trace">
  <div class="lec-top"><h2>A trace: everything one turn did</h2><p class="sub">The whole picture on the right of Argus is one trace. One message from Emma gives one trace.</p></div>
  <div class="fig" data-fig="trace" data-path="m.demo.ordinary.trace" data-nw="360" style="left:100px;top:250px;width:900px;height:240px"></div>
  <div class="side" style="left:1040px;top:250px;width:460px">
    <div class="card"><b>It has an id.</b> This one: <code style="font-size:14px"><span data-l6="m.demo.ordinary.trace_id"></span></code>. Every row carries it.</div>
    <div class="card step"><b>It has a shape.</b> The first row is the turn. The rows under it are the steps of that turn, in order.</div>
    <div class="card step"><b>It has a clock.</b> Each bar shows when that step ran, so you see where the time went.</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:560px;font-size:22px"><b>Trace</b> The record of one request from start to finish: every step taken to answer it, with times, tied together by one id.</div>
  <div class="look step" style="left:100px;top:680px;width:1400px">Why not just logs? A log is a list of lines from the whole server. A trace is the story of <b>one</b> turn. For an agent, which takes a different path every time, the story is what you need.</div>
</section>'''),
("new", '''<section class="slide" data-plate="A Span">
  <div class="lec-top"><h2>A span: one row, one piece of work</h2><p class="sub">Each row of the trace is a span. A span needs very little.</p></div>
  <div class="fig" data-fig="trace" data-path="m.demo.ordinary.trace" data-nw="360" style="left:100px;top:250px;width:900px;height:240px"></div>
  <div class="side" style="left:1040px;top:250px;width:460px">
    <div class="card"><b>A name</b>: what kind of work. “chat” is a call to the model; “execute_tool” is a tool call.</div>
    <div class="card step"><b>A start and an end</b>: the bar. Its length is how long the work took.</div>
    <div class="card step"><b>A parent</b>: the span it happened inside. That is why three rows are indented under the first.</div>
    <div class="card step"><b>Details</b>: anything worth keeping about the work. What went in, what came out, the cost.</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:660px;font-size:22px"><b>Span</b> A record of one piece of work: its name, when it started and ended, and which span it was part of. Spans with the same trace id make a trace.</div>
</section>'''),
("new", '''<section class="slide" data-plate="A Model Call">
  <div class="lec-top" style="top:90px"><h2 style="font-size:50px">Click a pink row: one call to the model</h2><p class="sub" style="font-size:21px">The first “chat” row of our trace, opened. Tools call this a <b>generation</b> (Langfuse) or an <b>LLM run</b> (LangSmith).</p></div>
  <div class="fig" data-fig="kv" data-path="m.demo.ordinary.gen" style="left:100px;top:230px;width:860px;height:440px"></div>
  <span class="step" style="display:none"></span><span class="step" style="display:none"></span><span class="step" style="display:none"></span>
  <div class="side" style="left:1000px;top:230px;width:500px">
    <div class="card"><b>What it is.</b> We send text to the model and wait for its answer. That is one generation.</div>
    <div class="card step"><b>What went in.</b> Much more than Emma’s question: the instructions, her saved memory and the list of tools go in on every call.</div>
    <div class="card step"><b>What came out.</b> Here, no words for Emma yet. The model asked us to run a tool.</div>
    <div class="card step bf"><b>What it cost.</b> Tokens are the units the model reads and writes (about ¾ of a word each). Cost = tokens × price.</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:720px;font-size:21px"><b>Generation</b> One call to a language model, recorded with its input, its output, the model’s name, the tokens used and the cost.</div>
</section>'''),
("new", '''<section class="slide" data-plate="A Tool Call">
  <div class="lec-top" style="top:90px"><h2 style="font-size:50px">Click an orange row: one tool call</h2><p class="sub" style="font-size:21px">The model cannot read Ledgerline. It asks; our code runs the tool and hands back the result.</p></div>
  <div class="fig" data-fig="kv" data-path="m.demo.ordinary.tool" style="left:100px;top:230px;width:860px;height:330px"></div>
  <span class="step" style="display:none"></span><span class="step" style="display:none"></span>
  <div class="side" style="left:1000px;top:230px;width:500px">
    <div class="card"><b>A tool span</b> records a function our code ran because the model asked for it.</div>
    <div class="card step"><b>Arguments</b>: exactly what the model asked for. Not what it said it asked for: what it sent.</div>
    <div class="card step"><b>Result</b>: exactly what came back. The reply to Emma is written from this.</div>
  </div>
  <div class="look step" style="left:100px;top:600px;width:1400px;font-size:21px"><span class="k">Why this row matters most</span>Words in a chat can be wrong and harmless. A tool call changes something: a stock check reads, but <code>create_purchase_request</code> writes. When an agent does damage, the proof is in a tool span’s arguments.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Tokens and Cost">
  <div class="lec-top"><h2>Tokens and cost add up, row by row</h2><p class="sub">Each call to the model has its own tokens and cost. The turn’s total is their sum, kept on the first row.</p></div>
  <div class="fig" data-fig="mtab" data-path="m.demo.ordinary.gens" data-cols="n:Call to the model:n|tin:Tokens in:n|tout:Tokens out:n|s:Seconds:n|usd:Cost:usd" data-mk="Measured · the stock question" style="left:100px;top:250px;width:800px;height:200px"></div>
  <div class="kpis" style="left:940px;top:250px;width:560px;grid-template-columns:1fr 1fr">
    <div class="kpi step"><span class="k">The whole turn</span><b><span data-l6="m.demo.ordinary.usd" data-f="usd"></span></b><span><span data-l6="m.demo.ordinary.tokens" data-f="n"></span> tokens</span></div>
    <div class="kpi step"><span class="k">Friday’s turn</span><b class="bad"><span data-l6="m.demo.incident.usd" data-f="usd"></span></b><span><span data-l6="m.demo.incident.tokens" data-f="n"></span> tokens, <span data-l6="m.demo.incident.model_calls"></span> calls</span></div>
  </div>
  <div class="three step" style="top:500px">
    <div class="card"><span class="tag nt">Why “tokens in” is so large</span>The instructions, the memory and the tool list are sent again on <b>every</b> call. A turn with five calls pays for them five times.</div>
    <div class="card"><span class="tag nt">Why it matters</span>40 buyers, many turns a day. Cost per turn × turns per day is a number Henrik will ask for.</div>
    <div class="card bf"><span class="tag bf">Who works it out</span>We do, in our code: tokens × our price list, written on the span. Each tool can also estimate it from its own price table.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="Four Labels">
  <div class="lec-top"><h2>Four labels we attach to every turn</h2><p class="sub">They sit on the first row of the trace. Each one answers a question you will be asked later. Real values from the stock question.</p></div>
  <div class="lab4" style="left:100px;top:240px;width:1400px">
    <div class="card"><h3>Who</h3><span class="v">user = <span data-l6="m.demo.ordinary.labels.user"></span></span>“Show me everything the assistant did for Emma this week.”</div>
    <div class="card step"><h3>Which chat</h3><span class="v">session = <span data-l6="m.demo.ordinary.labels.session"></span></span>“Show me the whole conversation, not one turn.” Turns of one chat share a <b>session</b> id.</div>
    <div class="card step"><h3>Which prompt version</h3><span class="v">prompt = <span data-l6="m.demo.ordinary.labels.prompt"></span></span>“Did this start after Thursday’s change?” One filter turns a suspicion into a fact.</div>
    <div class="card step"><h3>What it cost</h3><span class="v">cost = <span data-l6="m.demo.ordinary.labels.usd" data-f="usd"></span> · <span data-l6="m.demo.ordinary.labels.tokens" data-f="n"></span> tokens</span>“What does a turn cost? A conversation? A day?”</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:660px;font-size:22px"><b>Session</b> All the turns of one conversation, grouped by a shared id. One chat with three messages is one session holding three traces.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Friday, in the Same Picture">
  <div class="lec-top" style="top:90px"><h2 style="font-size:50px">Now Friday’s turn, in the same picture</h2><p class="sub" style="font-size:21px">The Thursday prompt, “Order the usual, please, needed by 4 Dec 2026.” How an engineer reads it on Monday morning.</p></div>
  <div class="fig" data-fig="trace" data-path="m.demo.incident.trace" data-mode="find" style="left:100px;top:220px;width:1000px;height:560px" data-nw="420"></div>
  <span class="step" style="display:none"></span><span class="step" style="display:none"></span><span class="step" style="display:none"></span>
  <div class="side" style="left:1130px;top:230px;width:370px">
    <div class="card"><b class="n">0</b>Find the turn: Emma, Friday 09:10, label <code>prompt = thursday</code>.</div>
    <div class="card step"><b class="n">1</b>Look only at the tool calls: what did it <b>do</b>?</div>
    <div class="card step"><b class="n">2</b>A preview of the request: <code>confirm=false</code>. Shown to the model. Emma never saw it.</div>
    <div class="card step bf"><b class="n">3</b>Then the save: <code>confirm=true</code>, in the <b>same turn</b>. Emma had no chance to say yes.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="The Span That Saved It">
  <div class="lec-top" style="top:90px"><h2 style="font-size:50px">The row that saved the request, opened</h2><p class="sub" style="font-size:21px">One tool span answers Henrik’s first question. No one had to ask the model why.</p></div>
  <div class="fig" data-fig="kv" data-path="m.demo.incident.tool" style="left:100px;top:230px;width:900px;height:360px"></div>
  <span class="step" style="display:none"></span><span class="step" style="display:none"></span>
  <div class="side" style="left:1040px;top:230px;width:460px">
    <div class="card"><b>What it did</b>: called the tool that writes a purchase request.</div>
    <div class="card step bf"><b>With what</b>: <code>confirm: true</code>. That argument is the difference between a preview and a save.</div>
    <div class="card step bf"><b>With what result</b>: a real request number, waiting for Daniel. £342,720.</div>
  </div>
  <div class="opens step" style="top:640px;background:var(--g1)"><span class="k" style="color:var(--after)">Two facts, both in the trace</span>The save has <code>confirm=true</code>, and there is no message from Emma between the preview and the save: both sit inside one turn. That is “saved without a yes”, proven from the record.</div>
</section>'''),
("new", '''<section class="slide" data-plate="What Right Looks Like">
  <div class="lec-top" style="top:84px"><h2 style="font-size:46px">What right looks like: two turns, two traces</h2><p class="sub" style="font-size:20px">The good prompt, the same request. Turn 1 ends with a preview. The save comes in turn 2, after Emma’s “Yes, go ahead.”</p></div>
  <div style="position:absolute;left:100px;top:200px;width:680px"><span class="l6-mk">Turn 1 · “Order the usual, please, needed by 4 Dec 2026.”</span></div>
  <div class="fig" data-fig="trace" data-path="m.demo.good2_t1.trace" data-nw="330" style="left:100px;top:240px;width:680px;height:240px"></div>
  <div style="position:absolute;left:820px;top:200px;width:680px" class="step"><span class="l6-mk">Turn 2 · “Yes, go ahead.”</span></div>
  <div class="fig step" data-fig="trace" data-path="m.demo.good2_t2.trace" data-nw="330" style="left:820px;top:240px;width:680px;height:330px"></div>
  <div class="three step" style="top:620px">
    <div class="card"><b>One session, two traces.</b> Both carry the same session id, so a tool shows them as one conversation.</div>
    <div class="card af"><b>The yellow tag is a preview</b>, in turn 1. Nothing is saved. Emma reads it.</div>
    <div class="card af"><b>The red tag is the save</b>, in turn 2. Same tool, same arguments, plus her yes in between.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="A Score">
  <div class="lec-top"><h2>A score: a verdict attached to a trace</h2><p class="sub">We just judged four turns by reading them. Write that judgement down as data, and a program can do it for every turn.</p></div>
  <div class="fig" data-fig="mtab" data-path="m.scores_v2" data-cols="turn:Turn:x|value:Saved without a yes?:b|why:Why (read from the tool calls, by code):x|langfuse:In Langfuse:b|langsmith:In LangSmith:b" data-mk="Measured · written through each tool’s API" style="left:100px;top:250px;width:1400px;height:260px"></div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:550px;font-size:22px"><b>Score</b> A name, a value and a comment, attached to one trace: <code>commit_without_yes = true</code>. A person can add one; a program can add one.</div>
  <div class="look step" style="left:100px;top:670px;width:1400px;font-size:20px"><span class="k">This is the bridge to Part 2</span>A trace says what happened. A score says whether it was right. Once scores exist, you can count them, chart them, and block a change that makes them worse. That is an eval.</div>
</section>'''),

# ------------------------------------------------------------------ by hand, then OpenTelemetry
("new", '''<section class="slide" data-plate="By Hand First">
  <div class="lec-top"><h2>Where do the rows come from? Build one by hand</h2><p class="sub">Three steps of work, one inside another. We wrap each in “start a record … end the record”. In NB6a you run this yourself.</p></div>
  <div class="two" style="left:100px;top:250px;width:1400px;grid-template-columns:1fr 1fr 1fr">
    <div class="card"><span class="tag nt">1 · The work</span><h3>Three nested steps</h3>Handle Emma’s message.<br>&nbsp;&nbsp;Inside it: ask the model.<br>&nbsp;&nbsp;Inside it: call the tool <code>check_stock</code>.</div>
    <div class="card step"><span class="tag nt">2 · What gets written</span><h3>Three records</h3><span style="font:400 15.5px/1.6 var(--mono)">ask the model · id b2 · parent a1<br>call check_stock · id c3 · parent a1<br>handle Emma’s message · id a1 · no parent</span><br>Each has a start and an end time.</div>
    <div class="card af step"><span class="tag af">3 · What you draw</span><h3>A tree</h3><span style="font:400 15.5px/1.6 var(--mono)">handle Emma’s message<br>&nbsp;&nbsp;&nbsp;ask the model<br>&nbsp;&nbsp;&nbsp;call check_stock</span><br>Follow each record’s parent, and the list becomes the picture.</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:600px;font-size:22px"><b>That is all a tracer does</b> Note the time, note “who is running now” (the parent), run the work, note the time again, keep the record. About fifteen lines of Python.</div>
  <div class="l6-src step" style="left:100px;top:730px;width:1400px">The ids here are shortened for the slide; the notebook prints real ones. A finished child is written before its parent, which is why the turn comes last in the list.</div>
</section>'''),
("new", '''<section class="slide" data-plate="What It Lacks">
  <div class="lec-top"><h2>What our fifteen lines lack</h2><p class="sub">The idea is complete. Three practical things are missing, and each has a standard answer.</p></div>
  <div class="l6-tw" style="position:absolute;left:100px;top:250px;width:1400px"><table class="l6t lg">
    <tr><th style="width:24%">Missing</th><th style="width:38%">A plain example</th><th>The standard answer</th></tr>
    <tr><td><b>Agreed names</b></td><td>We wrote “ask the model”. Another team writes “llm_call”. No tool can tell that both mean a model call.</td><td>Shared names for agent work: <code>chat</code>, <code>execute_tool</code>, <code>invoke_agent</code>.</td></tr>
    <tr class="step"><td><b>Somewhere to send it</b></td><td>Our records live in a Python list. When the program stops, they are gone.</td><td>One wire format every tool accepts, and a sender that runs in the background.</td></tr>
    <tr class="step"><td><b>A screen to read it</b></td><td>Printing a tree is fine for 3 spans. Friday’s turn has <span data-l6="m.demo.incident.spans"></span>, and there are thousands of turns.</td><td>A tool that stores traces, searches them and draws them: LangSmith, Langfuse, Sentry.</td></tr>
  </table></div>
  <div class="opens step" style="top:640px;background:var(--g1)"><span class="k" style="color:var(--after)">The first two are one standard</span><b>OpenTelemetry</b>: an open standard for recording and sending traces. Almost every monitoring tool reads it. We use it; we do not write our own.</div>
</section>'''),
("v1", 18, [("An open standard (CNCF) for traces, metrics and logs: one SDK per language, one wire format (OTLP), any back end.",
             "An open standard for traces. You record spans once, in one format; any tool that speaks the format can show them."),
            ("We used <code>opentelemetry-sdk 1.45.2</code> and the OTLP/HTTP exporter. Same spans to Langfuse and Phoenix at once; switching back ends changes one line.",
             "We used <code>opentelemetry-sdk 1.45.2</code>. The same spans go to LangSmith, Langfuse and Sentry at once. OTLP is the name of the wire format; an exporter is the part that sends.")]),
("new", '''<section class="slide" data-plate="Agreed Names">
  <div class="lec-top"><h2>Agreed names for an agent’s spans</h2><p class="sub">OpenTelemetry publishes a naming guide for AI systems (the “GenAI semantic conventions”). Three names cover almost everything we do.</p></div>
  <div class="l6-tw" style="position:absolute;left:100px;top:250px;width:1400px"><table class="l6t lg">
    <tr><th style="width:26%">The name on the span</th><th style="width:30%">In plain words</th><th>What travels with it</th></tr>
    <tr><td><code style="font-size:17px">invoke_agent Ask Northbridge</code></td><td>one turn of the agent</td><td>who, which chat, Emma’s message, the final reply</td></tr>
    <tr class="step"><td><code style="font-size:17px">chat claude-sonnet-5-5</code></td><td>one call to the model</td><td>the model’s name, what went in, what came out, tokens in and out</td></tr>
    <tr class="step"><td><code style="font-size:17px">execute_tool check_stock</code></td><td>one tool call</td><td>the tool’s name, its arguments, its result</td></tr>
  </table></div>
  <div class="look step" style="left:100px;top:560px;width:1400px;font-size:20px"><span class="k">Why names matter</span>Because the span is called <code>chat</code> and carries “tokens in”, LangSmith can show a cost, Langfuse can draw it pink and Sentry can add it to a chart. None of them needed our code. They only needed the names.</div>
  <div class="l6-src step" style="left:100px;top:730px;width:1400px">Status, Nov 2026: the guide is still marked “in development”, so a few names may change. The three above have been stable through 2026.</div>
</section>'''),
("new", '''<section class="slide" data-plate="Three Lines">
  <div class="lec-top"><h2>Three lines to switch tracing on</h2><p class="sub">Emma’s stock question again. All the work of recording is inside <code>Tracing</code>; using it is three lines.</p></div>
  <pre class="code" style="left:100px;top:250px;width:1400px;height:170px;font-size:21px"><span class="t">switch it on</span>tracing = Tracing.from_env()                 <span class="c"># 1 · looks for the keys of LangSmith, Langfuse, Sentry</span>
agent   = Agent(prompt, tracing=tracing)     <span class="c"># 2 · every turn, model call and tool call now opens a span</span>
agent.turn(<span class="s">"How many BAT-500 battery packs do we have?"</span>)   <span class="c"># 3 · work as before</span></pre>
  <div class="three step" style="top:470px">
    <div class="card"><span class="tag nt">What appears</span><h3><span data-l6="m.demo.ordinary.spans"></span> spans, in every tool</h3>The same four rows you saw in Argus, a second or two after the reply.</div>
    <div class="card"><span class="tag nt">What decides where</span><h3>Only the keys</h3>A key for a tool is set: its traces go there. No key: that tool is skipped, silently. No code changes.</div>
    <div class="card af"><span class="tag af">We checked</span><h3>Sent once, read back three times</h3>We asked each tool’s own API for the four demo turns: all four arrived in all three, with input and output.</div>
  </div>
</section>'''),
("new", '''<section class="slide" data-plate="What Must Not Go In">
  <div class="lec-top"><h2>What must not go in a trace</h2><p class="sub">A trace keeps what people typed. Sometimes they type things you must not store. Mask it before it leaves your program.</p></div>
  <div class="ba" style="left:100px;top:250px;width:1400px">
    <div class="bx"><span class="k">What Emma typed</span><span data-l6="m.redact.before"></span></div>
    <div class="ar">→</div>
    <div class="bx step"><span class="k">What the trace holds</span><span data-l6="m.redact.after"></span></div>
  </div>
  <div class="three step" style="top:520px">
    <div class="card"><span class="tag nt">How</span>Our tracer takes a masking function. Here: Microsoft Presidio, an open-source detector of personal and payment data. <span data-l6="m.redact.ms" data-f="ms"></span> on a CPU for this message.</div>
    <div class="card"><span class="tag nt">Where</span>Inside our own process, before the span is sent. What never leaves cannot leak from someone else’s server.</div>
    <div class="card bf"><span class="tag bf">And decide</span>How long traces are kept, and who may open them. A trace of a work chat is company data, and often personal data.</div>
  </div>
  <div class="l6-src step" style="left:100px;top:760px;width:1400px">A real run of our masking function on 16 Nov 2026 (what it found: <span data-l6="m.redact.found"></span>). Detectors make mistakes; tomorrow’s lecture measures this one.</div>
</section>'''),
("new", nbslide("NB6a · Together", "NB6a_tracing", "NB6a: tracing by hand, then for real",
                "We run this one together, top to bottom. Scroll the copy on the left; it is the notebook exactly as our live run left it.",
                '''<div class="card" style="font-size:16.5px"><b>1</b> Three nested steps → three records → a tree.<br><b>2</b> The same with OpenTelemetry.<br><b>3</b> One real turn of Ask Northbridge as a tree; then Friday’s turn, and the one row that explains it.<br><b>4</b> Send it to Langfuse, LangSmith, Sentry.<br><b>5</b> A tour of what Langfuse keeps around a trace.</div>''', 20)),
]
