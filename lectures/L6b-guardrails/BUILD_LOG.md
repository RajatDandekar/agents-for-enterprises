# Lecture 7 · Guardrails and Red-Teaming · build log

# Deck (builder B, 17 Nov 2026)

## What was built
| File | What |
|---|---|
| `index.html` | **91 slides**, built by `python3 build/build.py` from `build/part0.py` (opener and Part 1), `part1.py` (Part 2), `part2.py` (Part 3 and the close). 81 slides are new; 10 are kept from the parked 16 Nov deck by number, each with listed text edits (`build/index_parked_16nov.html` is the frozen source: parked slides 2, 14, 27, 31, 26, 28, 35, 36, 37, 38). `build/slides.txt` lists the result. The build prints "edits that did not apply: 0". |
| `l6.css`, `l6figs.js` | Copied from Lecture 6 v2 on 17 Nov, then Lecture 7 additions at the end of each. The attribute stays `data-l6` and the global `window.L6`. New figure types: `turn` (one turn as a ledger of tool calls, with the guard's refusal and reason), `guardbox`, `guardpath` (redrawn in plain words), `bugfig`, `inject`, `onepage`, `mailfig`, `dettiles` (the labelled set as tiles), `dtab` (the four-number table), `qlist`, `atkgroups`, `who`, `rtgrid`, `redloop`, `pftab`, `rttool`. The parked figure library is kept as `build/l6figs_parked_16nov.js`. |
| `gen_figdata.py` → `figdata.js` | Reads the 16 Nov logs from Lecture 6's folder and the 17 Nov logs from `experiments/logs/`. Reads `attacks.py` and `agent.py` with `ast` for the attack texts and the poisoned e-mail (nothing from the course package is imported or run). Each Lecture 7 block is wrapped so a missing or odd log leaves a plate, never a crash or a number. Four of Lecture 6's results (suite, gate, online check, conversations) are lifted from Lecture 6's generated `figdata.js` for the close. |
| `NOTES.md` | Speaker notes, slide by slide and click by click, with the log behind every number, the pre-class list, timings and a cut list. The parked notes are `build/NOTES_parked_16nov.md`. |
| `A7.md` | The assignment, 100 points: guards in code 30, one guard that reads text 20, four numbers 20, a small red team 30. |
| `build/PLATES.md` | What waited for A or C and what filled it (nothing waits now); three older pictures that could be re-shot. |
| `build/sheets_modal.py`, `build/grid_modal.py` | Contact sheets of the QA screenshots, and screenshots with a coordinate grid (to choose crops exactly), both made on Modal. |

## Decisions (ones Rajat might question)
1. **Three guard settings, not two.** The spec said "with the code guards 0 in 20 under both". No log held that: the 16 Nov "on" runs were all nine guards. A measured code guards only on 17 Nov: 1 of 20 under both prompts (the card number, A10). The deck shows none / code only / every guard everywhere, and says why the 1 remains.
2. **"Every guard on" is shown as unusable, not as the goal.** The classifier in that set stops "Order the usual, please." (score 0.96). Slides 68 and 69 say so, and say what we would ship (code guards everywhere, Presidio on every message, the injection check only on outside text), marked as not yet run as a set.
3. **Two claims of the parked deck were wrong against the logs and are corrected.** (a) "Ignore the Leeds stock for now…" was not a false alarm of the classifier (score 0.19); the real ones are "Order the usual, please.", "Override the need-by date…", "Disregard my last message…" and one clean supplier e-mail. The brief suggested the Leeds text as the example: slide 46 uses the real ones. (b) With all guards under Thursday's prompt the agent did not try to send the order list; the guard refused a save (`record_invoice`). Slides 40 and 41 say what the four runs of the invoice really show: 0 of 4 sent anything out, 4 of 4 told Emma.
4. **The never-events guard is shown as never having fired** (slide 26): in every run "recorded yes" met those calls first, or Ledgerline itself refused. Its answer on the slide is labelled as the words in its code.
5. **"Provenance" is not on any slide.** The guard is "text from outside"; "spotlighting" and "taint tracking" are each named once, after the idea is shown on the poisoned invoice.
6. **The only code on a slide in Part 1** is the one-word fix of our own guard (two lines, slide 28). The four code-heavy parked slides (16 Nov numbers 77, 81, 82, 84) are replaced by example-first slides.
7. **The Langfuse replay screenshots are cropped to four rows of the tree** (slide 29), because the logged-out public page shows empty Input and Output panels (the complaint of the 16 Nov review). The row's content is drawn from the log beside it.
8. **Times in the four-number table are from the notebook's own run** (17 Nov), not the 16 Nov benchmark machine, so the slide and NB7b/NB7c agree; the verdict on each text is from 16 Nov. Counts are the same on both days. Slide 45 says which is which.
9. **The red-team library slide is garak**, because that is what NB7d runs; DeepTeam's failure with Claude is one honest card on that slide.
10. **Demo 1 is three live slides** (guards off, guards on, the yes), each with Argus's own trace panel as the fallback picture, then three slides that replay the same turns from the logs.
11. **A7 is due "before Lecture 9"** (no date: the schedule file was not mine to read into).
12. **OWASP**: slide 64 does not use `attacks.py`'s "LLM06" tag on A05; in the 2026 list LLM06 is Unbounded Consumption (see "Needed outside my files").

## QA
- `node --check` on `l6figs.js` and `figdata.js`: clean. `python3 build/build.py`: 91 slides, 0 edits that did not apply.
- `qa_full_modal.py --slides all` (Lecture 6's script, pointed at this folder): **91 slides, 0 with issues, 0 page errors** on the last run (17 Nov, after NB7d's files landed). Nine runs in all; the issues found on the way were class-name clashes with the inherited css (`.tg`, `.c1`, `.col`, `.cap`), overflowing tables and wrong screenshot crops, all fixed.
- Reading passes on contact sheets (six slides a sheet): two full passes over all slides (plus an earlier one over the first 31), then every slide changed afterwards was read again, some at full size. No plate is left on any slide.
- `python3 tools/world_v4.py --check` on the deck, NOTES, A7, `build/`, `gen_figdata.py`, the css and js: exit 0. No banned words; no long dashes.

## Needed outside my files (not done by me)
- `ledgerline/ledgerline/course/l6/attacks.py`: A05 is tagged `"ASI02 · LLM06"`. In the OWASP LLM list of 2026, LLM06 is Unbounded Consumption; Excessive Agency is LLM03. Suggested: `"ASI02 · LLM03"`. The tag shows in Argus's attack list.
- Hub `index.html`: Lecture 7's row should list NB7a to NB7d and `A7.md` once the notebooks are final.
- `SPEC.md`, "Shape": "with the code guards 0 in 20 under both" should read "1 in 20 under both (the card number); 0 with Presidio added".

## Numbers pass after builder A's final report (builder B, 17 Nov)

`python3 gen_figdata.py` re-run on A's final logs; every slide that quotes them was re-read against
`experiments/logs/README.md`. The slides read their numbers from the data, so most followed by themselves: the four-number
table (classifier 12 of 15, 4 of 26, 178 ms; Presidio 7 of 8, 0 of 10, 10 ms; LLM check 15 of 15, 1 of 26, 1.2 s,
$0.00007; NeMo 15 of 15, 0 of 26, 1.5 s, $0.00013), the red team (2 of 15 and 3 of 15 with no guards, 0 of 15 with the
code guards), the forced run (17 want a tool call; 10 of 17, then 0 of 17), code guards alone (1 of 20, A10).

Changed by hand:
- **Slide 74, garak.** No rate as a headline any more. The figure (`rttool`) shows one row per run that left a log
  (`nb7d_garak_run2.json`: 1 of 4; `nb7d_garak.json`: 3 of 4) beside what Ledgerline held (changed after 0 of 4 both
  times, no tool call): the detector's verdict moved, the system of record did not. The first run's 4 of 4 is in no log
  (checked: only the two files above hold garak attempts), so the slide and the notes say "an earlier run" without a figure.
  `gen_figdata.py` gained `m.rt_tool.runs` and the totals behind the sentence under the figure. The DeepTeam card now says
  what the log says: 2 of 4 attacks never written, 1 more not graded (`m.rt_deepteam.not_produced`, `.not_graded`).
- **Slide 50, NeMo.** The yellow note now gives the install as it is in NB7c: `pip install nemoguardrails==0.24.1`
  alone; NeMo's own client talks to the gateway in the OpenAI chat format. No LangChain, no patch.
- **Slide 51.** The table's label says the times are from a cloud machine, not from Colab (4 CPUs: in the notes).
- **NOTES.md.** Entries 45, 49, 50 (new times and costs), 30, 55, 56, 76 (code cells and machine minutes of the last live
  runs: 25, 20, 12, 22 cells; 1.4, 2.2, 1.6, 3.4 minutes), 74 (rewritten).

Checks: `build/build.py` 91 slides, 0 edits that did not apply; the rebuilt deck differs from the one of the last QA
only in these lines; `node --check l6figs.js` clean; QA on Modal, all slides: 0 with issues, 0 page errors; slides 50, 51
and 74 read again at full size.

## After the push of 18 Nov (`ce56c7e`)
`experiments/colab_like_modal.py` against `main` on GitHub, bare Python 3.12, no key (the course package, the detector
libraries and NeMo Guardrails installed by the notebooks' own first cells): NB7a 25 of 25 code cells, NB7b 20 of 20, NB7c 12 of
12, NB7d 22 of 22, 0 errors. One pip download was retried after a timeout and then succeeded. Not covered: real Colab's
preinstalled packages, and garak (live mode only).
