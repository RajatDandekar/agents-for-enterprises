# Lecture 2: where every number comes from (v4, Northbridge Cycles, runs of 30 Oct 2026)

Every number on a plate that is not part of the 3D scene comes from one of the logs below. `gen_figdata.py` copies them
into `figdata.js` (`window.L2`). The one forward pass the 3D scene plays (tokens, vectors, attention, the logit lens,
temperatures, the generated answer and the answer with the fact, all on Qwen2.5-0.5B-Instruct) is recorded by the 3D
builder in `brain3d/trace.json`, not here. No number from the v3 runs (the old world) is left: those logs, the v3 cassettes'
replay files and `rec_attention.json`, `rec_next_token.json`, `rec_tokens.json` are deleted. All runs were on Modal
(workspace rajatworkspace). The sandbox clock is Mon 26 Oct 2026 09:00 GMT.

| Log | Made by | Command (from the course root) |
|---|---|---|
| `logs/cold_open.json` | `cold_open.py`, recorded (`--mode auto`): 25 Gemini calls in cassettes `L2v4_coldopen_r1`…`r8`, `L2v4_coldopen_t1_r1`…`r8`, `L2v4_facts_r1`…`r3`, `L2v4_toolpreview`, `L2v4_tokens`, `L2v4_cutoff`, plus one direct API call for the usage record | `sh tools/mrun.sh tools/modal_run.py --script lectures/L2-the-brain/experiments/cold_open.py --mode auto` |
| `logs/cold_open_replay.json` | the same script with `--mode replay`: every reply, figure and token count is identical to the recorded run | `... --script .../cold_open.py --mode replay` |
| `logs/model_card.json`, `tokens.json`, `bpe.json`, `cutoff.json`, `hand_attention.json`, `nb_qwen.json` | `models_modal.py`, job `qwen` (Qwen/Qwen2.5-0.5B-Instruct and the GPT-2 tokenizer, float32, 4 CPUs) | `/Users/raj/.venv/bin/modal run lectures/L2-the-brain/experiments/models_modal.py --only qwen` |
| `logs/tinygpt.json` | `models_modal.py`, job `tiny` (2 CPUs, the free-Colab budget) | `... models_modal.py --only tiny` |
| `ledgerline/ledgerline/course/l2/northbridge_corpus.md` | `course/l2/corpus.py` (stdlib, seed 7) | `python3 ledgerline/ledgerline/course/l2/corpus.py` |
| `ledgerline/ledgerline/course/l2/rec_qwen.json` | `gen_figdata.py`, from `nb_qwen.json` (+ the usage record, the cut-off probe, the token tables and the tiny-GPT curve) | `python3 lectures/L2-the-brain/gen_figdata.py` |

Model cost of everything recorded: 25 Gemini calls, 2,215 tokens in and 1,020 out, £0.0033 at `llm.PRICES` list
prices (gemini-3.8-flash $0.50 / $3.00 per million, £ = $ × 0.79), not counting thinking tokens (see "Tokens and
cost"). Even with thinking at the rate measured below, the whole run is well under £0.05. A replay costs nothing.

## The cold open (`cold_open.json`, figdata `cold`)
Ask Northbridge at `?stage=brain` is the app's own class, `ledgerline.experience.harness.AskNorthbridge(stage="brain")`:
no tools, the app's brain-stage system prompt for Emma Clarke (`harness._system("brain", "ECLARKE")`, 47 words,
296 characters), the app's token limit (4,096) and temperature (0). `course.l2.brain.BrainOnly` only names the
cassette. "Figure" = the first number in the reply's first line.

| Number | Value | JSON path |
|---|---|---|
| The truth in Ledgerline | 5,400 BAT-500 on hand in Manchester main stores (WH-MAN-STR); 6,600 with Leeds; 11 days of cover over both | `truth.warehouses`, `truth.free_total`, `truth.cover_days` |
| Eight runs at the app's settings | 42, 48, 48, 42, 42, 42, 54, 142. Every run gave a figure; none was 5,400; four distinct numbers | `runs_summary.figures`, `.distinct`, `.correct` |
| A typical reply (run 1) | "There are currently 42 City e-bike battery packs in stock across the Manchester stores", split into a "Central Warehouse: 35" and an "Assembly Store: 7" that do not exist | `runs[0].reply` |
| Eight runs at temperature 1.0 | 48, 48, 45, 48, 48, 48, 48, 42: again a figure every time, none right | `runs_t1_summary.figures` |
| The follow-up "Where did that number come from?" | "That count comes from the live inventory system records for the Manchester Central Warehouse and Assembly Store, updated this morning." (an invented source) | `follow_up.reply` |
| The question with no system prompt at all | declines: "I don't have access to your internal inventory systems…" (165 tokens out). The app's prompt ("You are Ask Northbridge … Help with purchasing: stock …") is what makes it answer with a number | `tokens.question_only.reply` |
| Seconds per reply | 5.0–8.3 s (recorded; a replay keeps them) | `runs[i].seconds` |

## The fix, measured (`cold_open.json` `facts`, figdata `facts`)
The same question with one Ledgerline line as the last line of the system prompt: "Ledgerline stock, BAT-500 at
Manchester main stores: 5,400 on hand" (the same line as `brain3d/capture_trace.py`'s `FACT`).

| Number | Value | JSON path |
|---|---|---|
| Gemini, 3 runs | 3 of 3 say 5,400: "There are 5,400 BAT-500 battery packs on hand at the Manchester main stores." | `facts.runs`, `facts.correct` |
| Tokens in with the fact | 114 (90 + 24 for the line) | `facts.runs[i].tokens_in` |
| Qwen2.5-0.5B-Instruct, greedy, with the fact | "We have 5,400 city e-bike battery packs in Manchester stores." | `nb_qwen.json` `greedy_facts_text` (figdata `facts.qwen_greedy`) |
| Qwen without the fact (NB2's replay copy) | "We currently have 100 city e-bike battery packs available in our Manchester stores." | `nb_qwen.json` `greedy_text`; the 3D scene's own copy is `brain3d/trace.json` `generation.text` |
| Two tools offered (find_item, check_stock) | no number: it calls `find_item` with `{"query": "city e-bike battery pack"}` | `tool_preview.tool_calls` |

## Tokens and cost (`cold_open.json` `tokens`, `tokens.json`, figdata `tokens`, `cost`)

| Number | Value | JSON path |
|---|---|---|
| Gemini's count, app prompt + question | 90 tokens in | `tokens.with_system.tokens_in` |
| Gemini's count, question alone | 16 tokens in, so the system prompt costs 74 | `tokens.question_only.tokens_in`, `tokens.system_prompt_tokens` |
| Visible answer | 33–60 tokens out, mean 44.8 over the eight runs | `runs[i].tokens_out`, `runs_summary.mean_tokens_out` |
| Cost of one question, visible tokens only | £0.000114–£0.000178 (mean £0.000142) | `runs[i].cost_gbp`; figdata `cost.per_question_gbp` |
| The provider's whole usage record (one more call of the same request) | prompt 90, completion 43, total 523: **390 thinking tokens** that the reply does not show, billed as output | `tokens.usage_record.usage`; figdata `cost.thinking_tokens` |
| Cost with thinking | £0.001062 a question; £1.06 per 1,000 questions (£0.14 without thinking) | figdata `cost.per_question_with_thinking_gbp`, `cost.per_1000_*` |
| Qwen's count of the same chat | 100 tokens: 72 system, 15 Emma, 13 chat template | `tokens.json` `n_tokens`, `counts` |
| Emma's question | 67 characters, 12 words, 15 Qwen tokens: How · many · city · e · -b · ike · battery · packs · do · we · have · in · Manchester · stores · ? | `question_tokens` |
| How words are cut (Qwen / GPT-2) | " Manchester" 1 / 1; " Northbridge" 2 (North·bridge); " Ledgerline" 2 / 3; " BAT-500" 5 (BAT·-·5·0·0) / 3; "5,400" 5 (5·,·4·0·0) / 3 (5·,·400); " £285,600" 8 / 4; " Gdańsk" 1 / 5 | `cuts` |
| Digits | Qwen writes every digit as its own token; GPT-2 groups digits ("400", "285") | `cuts` |
| The question in six languages (Qwen tokens / GPT-2 tokens) | English 15 / 15; German 18 / 26; Dutch 24 / 29; Polish 27 / 34; Japanese 31 / 48; Greek 72 / 92 | `languages` |
| Vocabularies | Qwen 151,665 tokens (151,936 rows in the model); GPT-2 50,257 | `vocab`, `model_card.json` |

**Why tokens and not words** (`tokens.json` `why_tokens`, figdata `tokens.why`). A word vocabulary built from the
tiny-GPT corpus (words counted as written, case-sensitive) has 1,312 words, 682 of them with digits in them. Two
Northbridge documents that are not in the corpus, the Ledgerline user manual and the data dictionary, have 6,004 words;
1,978 of them (33%, 920 distinct, from "Cause" and "Remedy" to "F2") are not in that vocabulary. Qwen's tokenizer
has no unknown token at all: the manual's 32,491 characters become 8,178 tokens (3.97 characters a token) and decode
back to the exact text. The corpus has 81 distinct characters.

**BPE** (`bpe.json`, figdata `bpe`).
- By hand, on "battery batteries pack packs battery pack charger chargers battery packs pack battery": 14 symbols (13
  letters and `_`) and 86 tokens to start. Merge 1 is e+r (7 times, text 79 tokens); "battery" becomes one token at merge 10, with the
  text down to 36 tokens (`hand.steps`).
- Learnt on the whole corpus (1,513 distinct words, 79 starting symbols, 121,112 symbols): the first merges are ",_",
  "00", "er", "s_", "._", "t_", "e_", "20", "26", then "2026" at merge 10 (`learnt.first_merges`). After 300
  merges the corpus is 42,079 tokens (`learnt.sizes`). "Manchester" is one token from merge 188, "battery" from 292,
  "Voltway" from 127; "BAT-500" is BAT-·500; "Brightcell", which is rare, is still B·r·i·g·h·t·cell
  (`learnt.cuts_after`, `learnt.merge_rank`).

## The cut-off (`cutoff.json`, `cold_open.json` `cutoff`, `tinygpt.json`, figdata `cutoff`)

| Number | Value | JSON path |
|---|---|---|
| Qwen: P(year) after "The current year is " (renormalised over 2015–2030) | 2023 is the most likely (0.55), then 2022 (0.20); 2026 or later together 0.003 | `cutoff.json` `year_probs[0]` |
| Qwen: other prompts | after "Copyright © " the top year is 2018; after "As of today, in the year " it is 2023 (0.28) | `year_probs[1]`, `[2]` |
| Qwen asked (greedy, no system prompt) | "What year is it now?" → "2023"; its training data → "October 2023" (its own words, not a documented date) | `asked` |
| Qwen with the app's prompt | "What is today's date?" → "26 October 2026": the date comes from the prompt | `asked.date_with_app_prompt` |
| Gemini asked | its training data → "March 2026" (its own words); today's date with no prompt → "May 19, 2024"; with the app's prompt → "26 October 2026" | `cold_open.json` `cutoff` |
| The tiny GPT's corpus | runs from 3 Aug to 23 Oct 2026: 23 Oct 2026 is its last training day | `tinygpt.json` `corpus_first_day`, `corpus_last_day` |

## The tiny GPT (`tinygpt.json`, figdata `tiny`)
`ledgerline.course.l2.tinygpt` (4 blocks, 4 heads, 128-dimensional vectors, 128 characters of context, 830,464
parameters), character level, trained for 1,500 steps (batch 32, learning rate 0.002 with warm-up and cosine decay,
seed 1337) on `northbridge_corpus.md`: 122,069 characters, 19,537 words, 81 distinct characters, 90% train / 10%
validation. NB2 section 8 builds the same model cell by cell, with the same seed and order of random draws.

| Number | Value | JSON path |
|---|---|---|
| Loss at step 0 | train 4.592, validation 4.598 (an even guess over 81 characters would be ln 81 = 4.394) | `curve[0]`, `uniform_loss` |
| Loss after 1,500 steps | train 0.227, validation 0.304 | `curve[-1]` |
| The curve | 4.59 → 2.22 (step 100) → 1.16 (200) → 0.77 (300) → 0.51 (500) → 0.31 (1,000) → 0.23 (1,500), every 100 steps | `curve` |
| Training time | 407.7 s on 2 Modal CPUs (the free-Colab budget) | `train_seconds_cpu2` |
| Before training, after "Stores, 26 Oct 2026: BAT-500 in Manchester stores," | random characters: "e)l0VfI#I#'_£xE£N.'xuń/dE1(tn*;…" | `samples_untrained` |
| After training, the same prompt (T = 0.5) | " 2,400 on hand, using 6,000 a day, 4 days of cover." then a well-formed order line | `samples[prompt]["0.5"]` |
| Ten stock lines (T = 0.8, seeds 0–9) | 2,400, 2,800, 2,100, 1,800, 4,000, 3,700, 2,500, 1,500, 2,400, 4,500 on hand: all well-formed, all invented, none 5,400 (Emma's e-mail with 5,400 is in the corpus three times) | `stock_figures`, `stock_5400` |
| An e-mail from Emma to Daniel (T = 0.8) | the subject "Re: Battery packs for the spring launch run" and "Approved. Please raise the order on PRD-01, …": real phrases, an invented cost centre | `samples[e-mail prompt]["0.8"]` |
| Its training cut-off | the corpus runs from 3 Aug to 23 Oct 2026 | `corpus_first_day`, `corpus_last_day` |

## Attention by hand (`hand_attention.json`, figdata `hand`)
Four tokens, "Emma needs 2,000 packs", two numbers each (Q, K, V as in NB2 section 4). Scores, scaled scores,
weights and outputs are computed by the job; NB2 computes the same matrix live.

## NB2 (`NB2_the_brain.ipynb`)
Built with `python3 tools/nbbuild.py lectures/L2-the-brain/NB2_the_brain.py`; its setup cell installs
`ledgerline-erp[all] @ git+https://github.com/RajatDandekar/agents-for-enterprises.git#subdirectory=ledgerline`
(main, not the `v3.1` tag). Proved on Modal with
`sh tools/mrun.sh tools/modal_run.py --nb lectures/L2-the-brain/NB2_the_brain.ipynb --mode replay`:
**32 code cells, 0 errors** (log `logs/nb2_replay_run.txt`). Nine sections, one per section of the deck, six
`TODO (exercise N)` exercises with guarded solutions (softmax, a BPE merge, the price in pounds, an attention row,
the loss before training, the fact in the prompt).

- The Gemini cells replay the `L2v4_*` cassettes: the eight runs give 42, 48, 48, 42, 42, 42, 54, 142 (0 of 8 right),
  the follow-up, the fact (5,400), the tool preview and the cut-off answers, exactly as in `cold_open.json`.
- The Qwen cells ran live on Modal (the model downloads; no key needed) and print a check against `rec_qwen.json`:
  same token ids (100), same top-5 next tokens ("We" 0.564), same greedy answer ("We currently have 100 city e-bike
  battery packs available in our Manchester stores."), same answer with the fact (5,400). The logit lens shows "We"
  as the top guess from block 22 on. If Qwen cannot load, every Qwen cell falls back to `rec_qwen.json`.
- The tiny GPT trains live: 4.592 / 4.598 at step 0 and 0.226 / 0.305 after 1,500 steps, 500 s on 2 CPUs. The
  notebook's pip installed torch 2.15 (the recorded job used 2.4.1), so the losses agree to about 0.002 and the
  samples differ; the notebook prints the recorded curve beside its own.

## Model card (`model_card.json`, figdata `card`)
Qwen2.5-0.5B-Instruct: 494,032,768 parameters, 24 blocks, 14 heads (2 key-value heads), 896-dimensional vectors, MLP
4,864, vocabulary 151,936 rows (tokenizer 151,665), context 32,768, input and output embeddings tied
(136,134,656 numbers). One forward pass of the 100-token prompt: 0.73 s on 4 Modal CPUs.
