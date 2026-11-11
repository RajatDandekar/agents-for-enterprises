# Lecture 5 v5 (The Loop, L5 + L6 merged): build log

Resume from here. Newest stage last.

## Stage 0 (11 Nov) · setup
- Old v3 files moved to `lectures/L5-the-loop/archive_v3/` and `lectures/L6-the-studio/archive_v3/` (nothing deleted).
- `STORY_V5.md` and `DAEDALUS_SPEC.md` written.
- `experiments/chain_probe.py` (no model, on Modal): the purchasing chain tool by tool → `logs/chain_probe.json`.
  Facts: PR/2026/04417 waits for DOKAFOR; a PO before approval is refused; Emma approving her own is ERR-SEC-0001;
  a second commit finds the same PR (`already_done`); bells 10,000 = £81,600 approved at once; **Ledgerline accepts and
  releases an order from Nordic Cell Co. (expired UN 38.3)**; PRD-05 is refused at commit.

## Stage 1 (11 Nov) · the code and the app
- `ledgerline/ledgerline/daedalus/`: `loop.py` (the agent loop one step at a time + the harness knobs: max_steps, budget,
  tools, prompt full/bare/custom, pause, recovery; state()/from_state()), `react.py` (the text loop), `workflow.py`
  (blocks engine: read/item/stock/supplier/cert/budget/request/approval/order/release/reply; gates; a waiting run is
  JSON; retries on a lost reply; flaky option), `race.py` + `jobs.json` (the six jobs, scripted Emma and Daniel, scored
  from Ledgerline's tables), `app.py` (FastAPI, Hephaestus patterns: Store/Guard/caps/rate limits/jobs/wall/admin),
  `static/` (daedalus.html/js/css, dx.js, wall.html, admin.html).
- `deploy/daedalus_modal.py`: web (min_containers 0, max 1), cron cool, admin ops, `test` (24 checks on the live URL),
  `knobs`, `load`, `record`, `sheets`. **Deployed:** https://rajatworkspace--northbridge-daedalus.us-east.modal.run.
  API test 24/24 (11 Nov).
- `experiments/run_modal.py`: runs scripts/NB on Modal from a snapshot of ledgerline/ + this lecture only (other
  builders' saves broke whole-folder uploads: "modified during build").
- `experiments/l5_runs.py` parts: story (done), hands (done), react (done), race and parts (rerun after fixing the
  scripted Emma: "let me know" is not a question, and a job's own answer ends the job).

## Stage 2 (11 Nov) · measurements (all real, gemini-3.8-flash direct, 11 Nov)
- Recorded with cassettes (`experiments/l5_runs.py` via `experiments/run_modal.py`): story, hands, react, parts, recover
  (before and after the fix), race (workflow ×1, agent ×3). Live app: `daedalus_knobs.json` (9 agent settings × 2 runs,
  4 workflow changes), `daedalus_api_test.json` (24/24), `daedalus_load_40.json` (40/40 races, median 70 s).
- **Found and fixed:** recovery refused a safe retry after a lost reply (0/2 → 2/2); scripted-Emma protocol bug fixed
  before any slide measurement; workflow approval step treated CL as waiting (fixed); a missing-fact check skipped
  tool blocks (fixed).
- Model spend: the live app's guard counted US$4.91 on 11 Nov (3,058 calls, all measurements, recordings, load test);
  the cassette experiments a little over US$1 more (estimate from tokens).

## Stage 3 (11 Nov) · deck, notes, notebook, assignment, films plan
- `index.html` (103 slides), `l5.css` (L4's l4.css + L5 additions), `l5figs.js`, `gen_figdata.py` → `figdata.js`.
  QA (`qa_full_modal.py`, a copy of L4's): **103 slides, 0 issues, 0 page errors** (screenshots of every slide read).
- Screen recordings `films/daedalus_*.mp4` (6) and screenshots `figs/daedalus/*.png` (11), Playwright on Modal
  (`experiments/daedalus_record.py`, `deploy/daedalus_modal.py::record`).
- `NOTES.md` (click by click, sources, before-class checklist), `NB5_the_loop.py/.ipynb` (18 code cells, replay 0 errors
  with no key on Modal), `A5.md`, `films/FILMS.md` (3 films planned, not rendered: slots on slides 29, 49, 82),
  `ledgerline/ledgerline/daedalus/README.md` ("Running it in class").
- Live app left cooled (min_containers 0) with an empty wall (`purge-tests` removed every build workshop).

## Open / for the lead
- Films `loop`, `harness`, `workflow`: render with L4's pipeline (FILMS.md has shots, scripts, data sources).
- Hub (`index.html`, not edited): L5 row text and the freed L6 slot (see the final report).
- Not verified: a real classroom of students; a real Claude connection (Daedalus has no MCP endpoint by design).
