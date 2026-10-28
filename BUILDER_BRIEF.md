# Brief for every v3 lecture builder

You are building one lecture of Vizuara's **AI Agents for Enterprises** (Dr. Rajat Dandekar). The course folder is `/Users/raj/Claude_Brain/enterprise-agents-course`.

## Read first, fully
1. `COURSE_V3.md`: the story, the syllabus, the Rasoi Experience, the lecture standard and the owners. This is the source of truth.
2. `BUILD.md`:
   - §0: hard rules (confidentiality, no local compute, numbers from our runs, replay, ownership, no browser pane, deck QA).
   - §1: the people, numbers and traps. Ignore its v2 lecture list.
   - §2: the deck engine and Sky style.
   - §3: notebooks.
   - §4: assignments.
3. **The engine:** `engine/plates.css`, `engine/plates.js`, and `lectures/_template/` (copy it to start your deck).
4. **One finished v2 deck,** to see the engine in use (not the story): `archive/v2/lectures/L4-the-route/index.html` + `figs.js`. Its slides load `../../engine/...`. From the archive that path is broken, so read the source instead of opening it.
5. **The shared code:**
   - `bahi/bahi/toolbox/`: the 15 tools, each a `tool.json` + `tool.py`.
   - `bahi/bahi/toolbox/mcp.py`
   - `bahi/tests_toolbox.py`: the whole P2P chain, PR → approve → PO → release → GRN.
   - `bahi/bahi/llm.py`: the LLM shim with cassettes.
   - `tools/modal_run.py`, `tools/nbbuild.py`, `tools/nb_setup.txt`, `tools/deck_qa_modal.py`.
6. **Your v2 predecessor,** in `archive/v2/lectures/` (named in your prompt). Reuse correct material, code and measured logs, but rebuild everything to the v3 story. Rajat's verdict on v2: "very hard to understand, storytelling is not correct, you have not taught concepts at all, it is all over the place."

## What Rajat wants from every lecture
- **The story first.** The student is the engineer Rasoi Steel Works hired to make it AI-native. Every lecture adds one piece to **Ask Rasoi**, the assistant on Rasoi's new home page. By L8 the students have built the After themselves, understand every piece and feel confident.
- **First principles, Vizuara-style:**
  - one idea per plate, in plain short sentences;
  - a one-line definition;
  - a worked example on Rasoi's real data (Kavita's 20,000 gaskets, PR/2026/04417, PO/2026/01182, ₹2,80,840 …);
  - a figure that builds up step by step;
  - then a practical connection.
  Never use a term before it is taught, and re-explain terms the first time they appear in this lecture.
- **Bahi services are black boxes:** an input goes in, an output comes out. Never explain their insides.
- **Interactive and deep.** About 40–60 plates for a 2-hour session. Live figures that build with the `.step`s. Interactive controls wherever touching teaches: sliders, toggles, scrubbers through a real recorded trace. Check-yourself questions. A good architectural figure for each major idea.
- **Architectural and concept figures are made with PaperBanana,** not hand-drawn SVG box diagrams. Run it on Modal (the laptop's PaperBanana venv is gone): `/Users/raj/.venv/bin/modal run tools/pb_modal.py --output lectures/<yours>/figs/<name>.png --description "..."`, or `--batch figs.json` (a list of {output, description}, run in parallel). It appends the course's house style (white, sky/ember/green, rounded boxes, no people or emoji) to your description. Each figure takes 3–8 minutes; batch them. Describe the layout exactly (which box where, every label verbatim); say "labels as plain text, no brackets". The master Ask Rasoi architecture is `figures/ask_rasoi_architecture.png` (portrait) and `figures/ask_rasoi_architecture_wide.png` (16:9, once made).
  - Save the PNGs in `lectures/<yours>/figs/`.
  - Keep the labels plain and professional, with no AI-sounding words.
  - Look at every generated image before using it. Regenerate if text is garbled.
  - Stepwise and interactive teaching figures (heatmaps, token strips, loops, traces, charts from logs) are SVG/JS in `figs.js`.
- **The Sky look** (Rajat chose it): Google Sans Flex, white full-bleed slides, hero title and part slides, soft cards, frosted pills.
  - Colours: ember = the 1998 ERP / before; sky = AI-native / after; green = terms.
  - Legacy Bahi windows stay Windows-2000 grey.
  - No emoji, cartoons or figurine people.
- **Live demos.** Ask Rasoi at your lecture's stage is at `https://rajatworkspace--rasoi-experience.us-east.modal.run/after?stage=<brain|knowledge|hands|agent>`, the Studio at `/studio` and the tools explorer at `/tools`.
  - These are being built in parallel. `bahi/bahi/experience/DEPLOYED.md` appears once they are live, with screenshots in `bahi/bahi/experience/shots/`.
  - Link the demos from your plates (a frosted pill "Try it live").
  - If you need a screenshot and the app is not live yet, take your own: run the same code in a notebook or script on Modal and screenshot or log it.
- **Every number** on a plate comes from a run you did (or a v2 log you copy into your `experiments/logs/` with its provenance noted), or it is marked "not yet measured".

## Deliverables in `lectures/<your-folder>/`
1. `index.html` + `figs.js` (+ `figdata.js` if you like): the deck. It passes `/Users/raj/.venv/bin/modal run tools/deck_qa_modal.py --deck lectures/<yours>` with 0 issues. Look at the PNGs it writes, and also screenshot 6–8 key slides with `--slides` and look at them for quality: is it beautiful, readable, and does it build up properly?
2. `NB<n>_<slug>.py` → `.ipynb` (`python3 tools/nbbuild.py`):
   - the first cell is `# %% setup`;
   - Colab-ready, with 3–6 `# TODO (exercise N)` exercises with guarded solutions;
   - recorded with `--mode auto`, then proven with `--mode replay` (0 errors);
   - cassettes named `L<n>v3_*`.
3. `A<n>.md`: the assignment.
4. `experiments/` (scripts) and `experiments/logs/` (what every plate's numbers come from).
5. `NOTES.md`: a speaker-notes outline, plate by plate, with what Rajat says, the demo moments and timings.

## Rules
- **No local compute.** Never pip install or run notebooks, servers or experiments on the laptop. Use Modal: `/Users/raj/.venv/bin/modal run tools/modal_run.py --script <path>` or `--nb <path.ipynb> --mode auto|replay` (profile rajatworkspace). Locally, only stdlib Python, `python3 tools/nbbuild.py` and `node --check`.
- **Confidentiality.** Everything is fictional. Never name or hint at a real client or ERP vendor, and never copy real data.
- **Ownership.** Edit only your lecture folder, and a new `bahi/bahi/course/l<n>/` package if your notebook needs library code. If you need a change in shared code (toolbox, erp, llm, engine, tools), do not edit it: put the exact change in your final report.
- **No browser pane.** Do not use the in-app browser pane; other builders share it.
- **Keys.** Never print or commit API keys.
- **Words.** Plain words; Indian number formatting; none of these: revolutionary, seamless, unlock, delve, leverage.

## Final report (short)
- What the lecture teaches, plate by plate (one line each).
- The figures made.
- The measured numbers and their logs.
- QA result.
- Notebook replay result.
- Known gaps.
- Any shared-code change you need.
