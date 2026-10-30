# Lecture 2 v4: The Brain. One question, followed all the way through

Rajat, 2026-10-30, on the v3 deck: "the flow was hard to understand, keep it simple and intuitive… I definitely want a beautiful 3D visualization of the entire process… divide this into sections where every section builds upon the previous one, and each section has progressive visualization showing the entire trace… currently the whole ppt is a bit confusing."

World: Northbridge Cycles (read `WORLD_V4.md`). Lecture 2 is Sun 1 Nov 2026, 7–9 AM IST.

## The one idea
We follow **one sentence**, Emma's question, through a real language model from start to finish. The **same 3D scene** stays on screen for the whole lecture. Each section adds one stage of the machine and shows the real numbers of that one sentence at that stage. Earlier stages stay in the scene, dimmed, so the students always see the whole trace so far. By the end the whole machine is built and the students have watched one answer being made, token by token.

## The running example
- **The question.** Emma, in chat: "How many city e-bike battery packs do we have in Manchester stores?" The real answer in Ledgerline is 5,400.
- **Cold open.** Ask Northbridge with its tools removed (the brain alone, the app's `stage=brain`) answers with a confident made-up number. The lecture's question is: how did a machine produce that sentence, word by word, and why is the number wrong?
- **The model we open.** We can't open Gemini, so we open a small open model of the same kind, **Qwen2.5-0.5B-Instruct** (24 blocks, 14 heads, 896-dimensional vectors, about 151k-token vocabulary). We send it the same question with the same system prompt, and it also makes up a number, which keeps the story honest. Every number in the 3D scene comes from that one recorded forward pass and generation.

## Sections (each builds on the previous; the 3D scene grows)
| # | Section | What the 3D scene adds | The trace numbers shown |
|---|---|---|---|
| 1 | The game: predict the next token | One sealed box: text goes in on the left, a bar chart of the next token comes out on the right | The top 5 next tokens after "…in Manchester stores: " and their probabilities |
| 2 | What you send, cut into tokens | The chat (system prompt, Emma's message) becomes a strip of token tiles with their ids; "Manchester" becomes 1–2 tiles; a number becomes digit tiles | Token count, the ids, how a number is cut, the cost in tokens |
| 3 | Each token becomes a vector | Each tile rises into a column of 896 numbers; a 3D map (PCA) puts similar words close together | A few real values per token; nearest neighbours of "battery" and "Manchester" |
| 4 | Attention: tokens look back | Arcs from the last token back to earlier ones, with thickness = the real attention weight; no arcs go forward | The real weights for 2–3 chosen heads; which words the last position looks at |
| 5 | A block, then 24 of them | Attention + MLP = one block; the columns pass up through 24 stacked blocks; at each block a small "what it would say now" label (the logit lens) | The top guess after every block, so you can see the answer forming |
| 6 | From a vector to a choice | The top vector meets the whole vocabulary and becomes probabilities; the temperature dial reshapes the bars; one token is picked | The real top-k at temperatures 0, 0.7 and 1.2; the token picked |
| 7 | The loop: one token at a time | The picked token joins the strip and the whole pass runs again, so the answer grows token by token, digits included | Each generated token with its probability; the digits of the made-up number and how sure the model was of each |
| 8 | Where the weights came from | The blocks' weights fill in as training runs (pretraining, instruction tuning, preference); a "last training day" marker appears | The tiny GPT trained in NB2 on Northbridge's own documents: loss curve and samples before and after; the model's cut-off |
| 9 | Why it made the number up, and what fixes it | The answer's number is traced back: nothing in the input carried Northbridge's stock, so the model produced a plausible number. Two sockets light up: knowledge (Lecture 3) and tools (Lecture 4) | Its invented number against 5,400 in Ledgerline. The same question with the stock line in the prompt gets the right number (measured) |

## The rhythm of every section
1. A part slide with one question, for example "How does text get into a model?".
2. The 3D scene at this section, building in 3–6 clicks.
3. One or two first-principles plates: a one-line definition, then a worked example on the same sentence.
4. One broad question to the class (not a quiz). Sections 2–9 open with "Last section we saw X; now Y".

Target: 55–65 slides. One idea per slide, plain words. Never use a term before it is taught.

## Owners
- **The 3D component and its trace** (`brain3d/`): the 3D builder. It also captures the real trace on Modal (`brain3d/capture_trace.py`, which writes `brain3d/trace.json`).
- **The other numbers** (`experiments/`, `figdata.js`, `NB2_the_brain.*`, `A2.md`): the L2 experiments builder. That covers the cold open with Ask Northbridge, tokens and cost, the tiny GPT on the Northbridge corpus, and the prompt with facts.
- **The deck** (`index.html`, `figs.js`, any deck CSS or JS, `figs/`, `NOTES.md`): the deck builder.
- **Shared code** (`ledgerline/ledgerline/course/l2/`): the experiments builder. Others ask before changing it.
