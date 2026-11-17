# -*- coding: utf-8 -*-
"""Build the parked deck lectures/L6b-guardrails/index.html (Lecture 7 of 11 · Sun 22 Nov 2026 · Guardrails and Red-Teaming)
from the guard slides of the Lecture 6 v1 deck (16 Nov), unchanged except for section labels. A working deck: it renders with
its own copies of l6.css, l6figs.js (v1), figdata.js (the guard keys, as measured on 16 Nov) and the figures it shows."""
import pathlib
import re

HERE = pathlib.Path(__file__).parent
V1 = (HERE / "index_v1_16nov.html").read_text()
secs = re.split(r'(?=<section class="slide)', V1)
OUT = pathlib.Path("/Users/raj/Claude_Brain/enterprise-agents-course/lectures/L6b-guardrails/index.html")
KICK = "Agentic Systems Engineering · Lecture 7 of 11 · Sun 22 Nov 2026 · Dr. Rajat Dandekar, Vizuara"
head = secs[0].replace("<title>Lecture 6 · Evals, Guardrails and Observability</title>", "<title>Lecture 7 · Guardrails and Red-Teaming</title>")
head = head[:head.index("<!-- ====")]
NEW_TOP = [f'''<section class="slide" data-plain="1">
  <div class="center">
    <div class="kicker">{KICK}</div>
    <h1 style="font-size:96px">Guardrails and Red-Teaming</h1>
    <p class="lede" style="margin-top:26px">Yesterday we learned to see Ask Northbridge and to measure it. Today we bound it: code that refuses what it must never do, whatever the prompt says, and attacks to prove the refusal holds. Henrik’s third question.</p>
  </div>
  <div class="pnote" id="pnote" role="note"><span class="k">Parked deck · working copy · hides on your first click</span>
    <ol><li><b>This deck is parked.</b> It holds the guardrails, red-teaming and “Ask Northbridge, trusted” slides moved out of Lecture 6 on 16 Nov, as they were measured on 16 Nov.</li>
    <li><b>To teach it:</b> switch Argus’s Guards station on (<code>modal run deploy/argus_modal.py::admin --cmd guards-on</code>) and warm Argus.</li>
    <li><b>Still to do before class:</b> an opener that recalls Friday’s incident, and a review pass like Lecture 6 had. See <code>NOTES.md</code> in this folder.</li></ol></div>
</section>''',
'''<section class="slide" data-plate="Where We Are">
  <div class="lec-top"><h2>Yesterday: see it, measure it. Today: bound it.</h2><p class="sub">Friday’s incident: Ask Northbridge saved a £342,720 request that Emma never confirmed, after someone shortened its prompt on Thursday.</p></div>
  <div class="three" style="top:250px">
    <div class="card af"><span class="tag af">Lecture 6 · Observability</span><h3>The trace showed it</h3>One tool span, <code>create_purchase_request</code> with <code>confirm=true</code>, in the same turn as the preview.</div>
    <div class="card af"><span class="tag af">Lecture 6 · Evals</span><h3>The eval failed the change</h3>The gate on Thursday’s prompt goes red: “committed in turn 1”.</div>
    <div class="card bf step"><span class="tag bf">Today · Guardrails</span><h3>Nothing yet refuses it</h3>A prompt is still the only thing between the model and the save. Today we put code there.</div>
  </div>
  <div class="def step" style="position:absolute;left:100px;right:100px;top:640px;font-size:22px"><b>Henrik’s third question</b> What stops it doing what it must never do, even when someone tries to trick it?</div>
</section>''']
EDITS = [('data-num="3"', 'data-num="1"'), ('data-num="4"', 'data-num="2"'), ("Section 3 of 5 · Guardrails", "Part 1 · Guardrails"), ("Check · Section 3", "Check · Part 1"),
         ("Section 4 of 5 · Ask Northbridge, trusted", "Part 2 · Ask Northbridge, trusted"),
         ("Honest limits of what we built today.", "Honest limits of what we built in these two lectures."),
         ("Section 2", "Lecture 6"), ("Section 1", "Lecture 6"),
         ("<td>(Lecture 8)</td>", "<td>(a later lecture)</td>")]     # the course grew to eleven lectures; later numbers moved
NEW_END = ['''<section class="slide" data-plain="1">
  <div class="center" style="text-align:center;align-items:center">
    <div class="kicker">Next time · Lecture 8 · Sat 28 Nov 2026</div>
    <h1 style="font-size:96px">Agent Frameworks in Industry</h1>
    <p class="lede" style="max-width:1050px;margin-top:24px">We wrapped our own harness by hand. Next: the frameworks teams build agents with, and where tracing, evals and guard hooks live in each.</p>
  </div>
</section>''']
body, n = [], 0
for html in NEW_TOP + [secs[i] for i in range(72, 107)] + NEW_END:
    n += 1
    html = html.split("\n\n\n<!-- ====")[0].rstrip()
    html = re.sub(r"\n*<!-- =+ .*? =+ -->\s*$", "", html, flags=re.S).rstrip()
    for a, b in EDITS:
        html = html.replace(a, b)
    body.append(f"<!-- #{n} -->\n{html}\n")
tail = V1[V1.index("\n</div>\n<script src=\"figdata.js"):]
OUT.write_text(head + "\n<!-- ============================== PARKED: GUARDRAILS AND RED-TEAMING ============================== -->\n" + "".join(body) + tail)
print("L6b slides:", n)
