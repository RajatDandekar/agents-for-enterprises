# Lecture 7 deck · plates that wait for another builder

A plate is a striped box on a slide that names what is missing. It never shows a number. Every plate fills in by itself:
when the file exists, run `python3 lectures/L6b-guardrails/gen_figdata.py` and reload the deck (no rebuild needed).
Slide numbers are the deck's counter. Kept current by builder B; last checked 17 Nov 2026, 14:50.

## Still waiting

Nothing, as of 17 Nov 2026, 14:50. The last two plates (slide 74, `experiments/logs/nb7d_garak.json`; slide 76,
`nb/NB7d_red_team.html`) filled when builder A's live run of NB7d landed.

## Filled since the first build (nothing to do)

| Slide | File or key | From |
|---|---|---|
| 4, 5, 6 · Live Demo 1 | `figs/argus/chat_guard_off.png`, `chat_guard_refused.png`, `chat_guard_yes.png` (shown cropped to the trace panel) | C |
| 33 · your turn 1; 77 · your turn 2 | `figs/argus/guards_station_a00_code.png` (cropped) | C |
| 18, 65, 66, 69, 85, 87 · code guards only | `l7_attacks_code_good.json`, `l7_attacks_code_thursday.json` → `m.attacks.n.good_code`, `m.attacks.n.thursday_code` | A |
| 20, 22 to 25, 87 · the guards alone | `l7_forced.json` → `m.forced` | A |
| 30, 55, 56 · NB7a, NB7b, NB7c | `nb/NB7a_guards.html`, `nb/NB7b_detectors.html`, `nb/NB7c_nemo_guardrails.html` | A |
| 49, 51 · the second-model check | `nb7b_llm_check.json`, `nb7b_llm_invoice.json`, `nb7c_four_numbers.json` → `m.llm_check` | A |
| 45, 47, 50, 51, 53 · times and NeMo's numbers | `nb7c_four_numbers.json`, `nb7c_input_rail_41.json`, `nb7c_output_examples.json` → `m.detectors.*`, `m.nemo7` | A |
| 70, 71 · the red team from scratch | `l7_redteam_variants.json`, `l7_redteam.json` → `m.rt` | A |
| 74 · garak | `nb7d_garak.json` and `nb7d_garak_run2.json` → `m.rt_tool` (`runs`: one row per recorded run); `l7_deepteam_custom.json` → `m.rt_deepteam` | A |
| 76 · NB7d | `nb/NB7d_red_team.html` | A |

## Pictures that are older captures (they work; a fresh capture would be better)

| Slide | Picture | Why it could be re-shot | Who |
|---|---|---|---|
| 35 · Live Demo 2 | `figs/argus/guards_a11_all.png` (16 Nov, cropped to the verdict panel) | It is from the 16 Nov Argus; the new Guards station has a prompt picker. A capture of A11 with every guard on in the new station would match what the class sees. If re-shot under the same name, check the crop on slide 35 (`data-crop="1840,500,1300,735"`). | C |
| 78 · the class wall | `figs/argus/wall.png` (16 Nov, cropped below its old "Lecture 6" header) | Same reason; and it shows a small test run where nothing got through. Crop: `data-crop="144,550,2912,1040"`. | C |
| 29 · a guard in the trace | `figs/langfuse/lf_replay_turn1_guard.png` (16 Nov, cropped to four rows of the tree) | Langfuse's public page does not load Input and Output, so only the tree is shown. A signed-in capture is optional. | Rajat (signed in) |

## If a new log has a different shape
`gen_figdata.py` wraps each Lecture 7 block in `safe(...)`: an unexpected shape prints one line ("… not read") and leaves
the plate in place. The blocks are `nb7b()`, `code_only()`, `forced()`, `redteam()`, `rt_tool()`.
