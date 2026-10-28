# From Forms to Agents: build standard

> **v3 (2026-10-28): read `COURSE_V3.md` first.** It replaces §1 (the nine-jobs spine, lecture list, lecture shape) and §5 (owners) below. v2 lectures are in `archive/v2/lectures/`.
Course: **AI Agents for Enterprises** (Vizuara), led by Dr. Rajat Dandekar. Eight lectures, Sat and Sun 7–9 AM IST, 31 Oct to 22 Nov 2026, plus a primer.
The approved plan is the deck `course-plan-deck.html` (43 slides). Read its Part Four plates for your lecture before you build anything.

## 0. Hard rules
1. **Confidentiality.** The course was inspired by a real client engagement. Never name or hint at any real client, ERP vendor, product or person from it, and never copy any of its data, screen codes or wording.
   - Everything here is fictional: Bahi Systems and Bahi ERP 7.2, Rasoi Steel Works, its people, suppliers, codes and numbers.
   - Public tools may be named: LangGraph, MCP, n8n, Temporal, Langfuse, Gemini, OpenRouter. So may public models, and Jev, TypeSafe's public decision-model API.
2. **No local compute.** The laptop is nearly full and slow.
   - Never `pip install`, never run notebooks, servers or experiments on it.
   - Run everything on Modal: `/Users/raj/.venv/bin/modal run tools/modal_run.py --script <path> [--args "..."] [--mode auto|replay|record|live]` or `--nb <path.ipynb>`.
   - Modal mounts the whole course folder, runs the job, and copies back every file it created or changed: executed notebooks, cassettes and logs.
   - Locally you may only run stdlib Python (`python3 tools/nbbuild.py …`, quick sqlite checks with `sys.path.insert(0,'bahi')`) and `node --check`.
3. **Every number on a plate comes from our own run.**
   - Each one must be traceable to a log in `lectures/<L>/experiments/logs/`. Write the experiment script, run it on Modal, and put the measured numbers on the plate.
   - A target or estimate is marked with the `.ours` note ("Not yet measured").
   - A measured result that surprised us gets a `.measured` note ("In our run").
   - Never invent a number.
4. **Replay must work.** Every notebook runs top to bottom with no API key, in replay mode, in under 15 minutes on free Colab.
   - Prove it: execute once with `--mode auto` to record, then again with `--mode replay`.
   - For replay to work, everything that enters a prompt must be deterministic. The ERP clock and tokens already are. Derive idempotency keys from content (a hash), never from `uuid4()`.
5. **Do not edit files you do not own** (see §5). If you need a change in a shared file, say exactly what in your final report.
6. **Do not use the browser pane** (other builders share it). Check deck JS with `node --check`, then run the headless visual QA on Modal: `/Users/raj/.venv/bin/modal run tools/deck_qa_modal.py --deck lectures/<L>` (add `--slides 3,7` for extra screenshots). It reports text outside the frame (OUT), clipped boxes (CLIP), SVG text cut at the figure's edge (SVGCUT), text under 12px (TINY) and page errors, and writes PNGs of every flagged slide to `<deck>/qa/`; read them. A deck is done only when it reports 0 issues, or every remaining flag is an intentional clip you can justify.

## 1. The story canon
Use these and nothing else. The numbers come from `bahi/bahi/erp/seed.py`.

- **Bahi Systems** has sold Bahi ERP to Indian manufacturers since 1998: 412 screens, about 3,100 stored procedures, about 1,200 plants. Its customers want AI; it is losing deals to newer products.
- **Rasoi Steel Works, Pune** (RSW-PUN-01, Maharashtra) makes pressure cookers, 1,80,000 a month. Chakan unit: RSW-CHK-01. Sandbox date: **Monday 26 Oct 2026**.
- **People:**
  - Kavita Joshi (KJOSHI), purchase executive. Her approval limit is ₹2,50,000 *gross incl. GST*. Her default cost centre is PRD-05.
  - Rohit Mehta (RMEHTA), purchase manager, limit ₹10,00,000.
  - Suresh Kulkarni (SKULKARNI), senior buyer: the man who remembers the rules.
  - Anand Patil (APATIL), plant head, limit ₹50,00,000.
  - Neha Desai (NDESAI), stores.
  - SVC_AGENT is the integration service account IT made "for the bot". It can do everything, with no limit.
- **The order:** 20,000 silicone gaskets GSK-SIL-05L for the 5-litre cooker, before the Diwali run.
  - Stock: 54,000 on hand, using 6,000 a day, which is 9 days of cover.
  - Supplier: Deccan Polymers, DP-RJK-0042, Rajkot, Gujarat (so tax code GST18-INTER), with a valid food-grade certificate.
  - Price: the old rate was ₹11.40 and the contract rate since 1 Oct is ₹11.90. ₹2,38,000 basic + 18% = **₹2,80,840 gross**, which is above Kavita's limit, so Rohit must approve.
  - Documents: PR/2026/04417 then **PO/2026/01182**.
- **Traps the sandbox really has:**
  - PRD-05 closed on 15 Oct, so the PO **silently saves as Draft (DR)** with rc "S" and the message "PO/2026/01182 SAVED".
  - Fetch tax-code default GST18-INTRA gives ERR-PO-0412.
  - Save without Fetch gives ERR-SCR-0221 (screen state).
  - A direct PO above ₹50,000 gives ERR-PO-0610 (variant).
  - Suppliers: DP-RJK-0009 is a blocked duplicate of Deccan. "Deccan Paints & Inks" is a near-match. Kaveri Rubber's certificate has expired. **Shakti Seals (Vadodara, quotes ₹10.40) is not in the master and has no certificate.**
  - The ERP does not enforce the food-grade rule; it lives in Purchase Policy §6.2 and in Suresh's head.
- **Six scenarios** (`bahi/bahi/scenarios.py`):
  1. Policy question (§6.2)
  2. Reorder above limit
  3. Duplicate supplier ("Deccan Polymer Industries")
  4. Shakti Seals with no certificate
  5. Silent Draft (whistles, default PRD-05)
  6. Timeout after save

  There are five never-events, NE1–NE5. `run_scenario(make_agent, sc)` plays Kavita and Rohit and checks the ERP state with code.
- **The spine: "the form was doing nine jobs."** Delete the form, and the harness must do all nine:
  1. Ask for the right fields
  2. Know the order of screens
  3. Look up codes and do the work
  4. Explain the rules
  5. Hold the half-filled document
  6. Respect roles
  7. Give proof
  8. Recover when it hangs
  9. Be tested

  Lectures take them over:
  - L1 The Form and Its Nine Jobs (the map)
  - L2 The Manual (job 4)
  - L3 The Hands (job 3)
  - L4 The Route (jobs 1, 2 and 5)
  - L5 The Signature (jobs 6 and 7)
  - L6 The Inspector (job 9)
  - L7 The Night Shift (job 8)
  - L8 Your Module (demo day)

  The website topic of each lecture is its subtitle.
- **Lecture shape:**
  1. The failure on Kavita's order ("Opens with")
  2. The mechanism from first principles
  3. One measured experiment
  4. The Colab build
  5. The same layer added to the student's own module (assignment A*n*)

## 2. The deck: plates
- **Engine.**
  - Copy `lectures/_template/index.html`. It loads `../../engine/plates.css` and `../../engine/plates.js`.
  - Each `<section class="slide" data-plate="Title">` gets a frame, a "Plate N · Title" head and a folio. `.step` elements reveal one at a time.
  - A live figure is `<div class="fig" data-fig="name" style="left:…;top:…;width:…;height:…"></div>`. It is defined in `figs.js` as `FIGS.name = (el) => ({ step(k, instant) {…} })`, where `k` = number of steps shown.
  - `window.Plates` gives you `svgEl`, `txt`, `fmt` (Indian digit grouping), `winHTML(screen)` (legacy window) and `TREE`.
  - `?print=1` stacks every slide fully revealed.
- **Style:** the "Sky" theme (Rajat, 2026-10-27), matching Vizuara's planning pages.
  - Google Sans Flex in light weights (450–500) for everything. Google Sans Code for code.
  - White, full-bleed pages with soft sky light. Title and part slides are sky-gradient heroes with a giant glassy numeral (added automatically).
  - Soft rounded cards (`--card #f0f4f9`, 24px radius); pastel gradient cards for before (`--g4`, ember) and after (`--g1`, sky); frosted pill buttons; a floating pill nav.
  - Colours: ember `--before #c4511f` = the legacy form ERP; sky `--after #0b57d0` = AI-native; green `--gold #138a60` = terms and targets.
  - Legacy Bahi windows stay Windows-2000 grey on purpose.
  - Use the existing classes; never hardcode old fonts.
- **Depth:** the mech-interp course standard.
  - Nothing is used before it is taught.
  - Follow Kavita's one order through every mechanism, with its real numbers and real payloads copied from our runs: the actual JSON a tool returned, the actual tokens counted, the actual trace.
  - Zoom in level by level the first time a mechanism appears.
  - 28–40 plates for a two-hour lecture.
- **Figures:**
  - Every explanatory figure is a **live figure** that builds up in step with the slide's `.step`s.
  - Make it interactive wherever touching it teaches something: sliders, scenario buttons, toggles, a scrubber through a recorded trace.
  - Write the values on the figure. No cartoons, no emoji, no clip-art people.
  - Data plots are drawn in SVG from the logged numbers (embed the numbers in `figs.js`, with the log path in a comment).
- **Words:** plain, short sentences, the way Rajat talks to engineers. No hype or "AI-sounding" labels ("revolutionary", "seamless", "unlock", "delve", "leverage"). Use Indian number formatting (₹2,80,840; 1,80,000).
- **Per lecture:**
  - Title plate.
  - "Last time / this time" plate.
  - The failure (Opens with), shown with the real transcript from our run.
  - The mechanism plates, a "what we measured" plate, and the build walkthrough plates (code in `.code`).
  - The assignment plate, and a closing plate mapping where we are on the nine jobs and the harness ring.

## 3. The notebooks
- Write each notebook as percent-format Python (`NB1_the_form.py`) and build the `.ipynb` with `python3 tools/nbbuild.py <file.py>`. The first code cell is `# %% setup`, which becomes the standard install cell (`tools/nb_setup.txt`).
- Teach by building: short markdown, then code the student runs.
  - 3–6 **exercises**, each marked `# TODO (exercise N)`, with the working solution right there.
  - The solution is guarded so the notebook still runs top to bottom; for example `SOLUTION = True`, or a filled-in default.
- Show real outputs: tables of results, receipts, traces, small matplotlib charts.
- End with the scorecard for the six scenarios at this lecture's layer, and a "Your module" section that starts the assignment.
- Must run in replay mode on Modal (see §0.4). Keep notebook model calls small, and run full sweeps in `experiments/` scripts.
- Model tiers (Gemini key available):
  - small: `gemini:gemini-3.5-flash-lite`
  - default: `gemini:gemini-3.8-flash`
  - large: `gemini:gemini-3.1-pro-preview`

  GPT and Claude are reachable only with a student's own OpenRouter key; say so rather than pretending we ran them. Name cassettes `L<n>_<what>`.

## 4. The assignment (A*n*)
`lectures/<L>/A<n>.md`, aimed at the student's own capstone module (`modules/`). It should give:
- what to build and what to submit;
- a checklist;
- how it is graded (it feeds the /100 rubric: scenario pass rate 25, tools 20, route and authority 15, retrieval 15, operations 15, demo-day change 10);
- the guided track (configuration) and the builder track (Python).

## 5. Who owns what
| Owner | Files |
|---|---|
| lead (do not edit) | `bahi/bahi/erp/{engine,procs,services,seed}.py`, `bahi/bahi/llm.py`, `bahi/bahi/scenarios.py`, `engine/*`, `tools/*`, `BUILD.md` |
| L0+L1 | `lectures/L0-primer/`, `lectures/L1-the-form/`, `bahi/bahi/legacy_ui/`, `bahi/bahi/erp/screens/*.yaml`, `bahi/bahi/client.py`, `bahi/bahi/agent/naive.py`, `bahi/bahi/server.py` |
| L2 | `lectures/L2-the-manual/`, `bahi/bahi/docs/` (purchase-policy.md exists; keep §6.2 as written), `bahi/bahi/agent/retrieval.py`, `bahi/bahi/wiki/` |
| L3 | `lectures/L3-the-hands/`, `bahi/bahi/agent/tools.py` (keep tool names and arguments), `bahi/bahi/agent/loop.py`, `bahi/bahi/mcp_server.py` |
| L4 | `lectures/L4-the-route/`, `bahi/bahi/agent/graph.py`, `bahi/bahi/agent/decide.py`, `bahi/bahi/agent/memory.py`, `bahi/bahi/agent/route_spec.py` |
| L5 | `lectures/L5-the-signature/`, `bahi/bahi/agent/authority.py`, `bahi/bahi/app/` |
| L6 | `lectures/L6-the-inspector/`, `bahi/bahi/evals/` |
| L7 | `lectures/L7-the-night-shift/`, `bahi/bahi/durable/`, `deploy/` |
| L8 + kits | `lectures/L8-your-module/`, `modules/`, `bahi/bahi/modules/` |

The cassette files are named per lecture, so builders never write the same one.
