# Film 3, `race`: "The race" (the storyboard; built 3 Nov 2026 from race.json, see FILMS.md)

This is the design written before the race had run; the placeholders named the fields we expected in `experiments/logs/race.json`. The built film (four lanes rather than two, timers in 2D rather than dials, `build/scenes/race.py` and `build/specs/race.py`) reads the real file through `make_data.py`.

**Running time:** about 2:30. It uses the same pipeline and kit as `rag` and `wiki` (`build/`), with the same studio, Daniel's voice and L1's music. It plays at the end of section 9 ("compare both on the metrics").

## The set
- **The archive** (`rag` and `wiki` both start there).
- **Two lanes side by side** on one long plinth:
  - the RAG line (parser, tiles, light table, catalogue, reranker), shortened;
  - the wiki dais, scaled down.
  - Both lanes end at one model machine each.
- **A race clock** for each lane: a machined dial with a sweeping hand. Its speed is the real latency.
- **A scoreboard wall** behind the finish: one row of glass slats per method; a slat lights green for a right answer and ember for a wrong one.

## Shots and lines (draft; every number is a placeholder)
1. **The start.** Emma's two questions on cards: Q-0412 (the code) and Q-EMMA (Brightcell). Both lanes get the same question at the same instant.
   > "Same questions, same model, same judge. Two ways to find the answer. Which is right more often, and which is faster?"
2. **The rules.** A chip:
   - `{race.n_questions}` questions;
   - judged by `{race.judge_model}`;
   - answers capped at `{race.answer_cap_words}` words for every method. The old cap was 150 words, too short for Emma's seven facts.
3. **Q-0412 race.**
   - The RAG lane runs: search takes `{race.examples.Q-0412.rag.retrieval_ms}` ms, then the answer.
   - The wiki lane runs: index, then `{race.examples.Q-0412.wiki.pages_opened}`, then the answer.
   - The two clocks stop at `{race.examples.Q-0412.rag.total_s}` s and `{race.examples.Q-0412.wiki.total_s}` s.
   - Both slats light `{race.examples.Q-0412.*.correct}`.
4. **Q-EMMA race.**
   - RAG finds `{race.examples.Q-EMMA.rag.gold_found}` of 11 sources.
   - The wiki opens `{race.examples.Q-EMMA.wiki.pages_opened}`.
   - Slats `{race.examples.Q-EMMA.*.correct}`; the facts covered are `{race.examples.Q-EMMA.*.facts_covered}` of 7.
5. **The whole golden set.** The scoreboard fills with one slat per question, the methods in rows:
   - `rag_best`;
   - `wiki_nav`;
   - `wiki_hybrid`;
   - `paste_all`. This is a sample only. Its label: "measured on `{race.methods.paste_all.n}` questions; the whole dump does not fit any context window".
   - Each row shows these counts: `{race.methods.<m>.answer_correct}`, `{race.methods.<m>.fact_correct}`, `{race.methods.<m>.citation_correct}`.
6. **The clock.**
   - A bar per method: `{race.methods.<m>.latency_p50_s}`, with `{race.methods.<m>.latency_p95_s}` marked.
   - The latency target is `{race.targets.time_to_answer_p95_s}`. Latency weighs heavily, as the class agreed.
7. **The cost.** One coin stack per method, `{race.methods.<m>.cost_per_q_usd}` per question. Add the wiki's one-off build cost, `{race.wiki_build_usd}`, and its update cost per document, `{race.wiki_update_usd}`.
8. **Where each wins.**
   - A grid by question type (`single_lookup`, `procedure`, `rule`, `service_field`, `table_lookup`, `multi_hop`, `version_conflict`, `exact_code`, `not_in_docs`, `permission`).
   - Each cell is coloured by the leading method: `{race.by_type.<type>.<m>.answer_correct}`.
9. **The decision.** The method `{race.winner.method}` is wired into Ask Northbridge, for the reason `{race.winner.reason}`, in one sentence from the log.
   > "So Ask Northbridge uses …, and next lecture we give it hands."

## To build
- Add `race` to `make_data.py`, reading `experiments/logs/race.json`.
- Write `scripts/race.json`, `scenes/race.py` (two lanes and clocks, reusing `props_l3`) and `specs/race.py` (scoreboard, bars and the type grid in 2D).
- Run `narrate.py race`, then the usual style → full → comp steps in `FILMS.md`.
