"""Build figdata.js (window.L2, the deck's numbers that are not in the 3D trace) and the notebook's replay file. Stdlib only.

    python3 lectures/L2-the-brain/gen_figdata.py

Every number comes from these logs (see experiments/PROVENANCE.md):
  logs/cold_open.json     gemini-3.8-flash as Ask Northbridge at ?stage=brain (experiments/cold_open.py)
  logs/model_card.json, tokens.json, bpe.json, cutoff.json, nb_qwen.json
                          Qwen2.5-0.5B-Instruct and its tokenizer (experiments/models_modal.py, job qwen)
  logs/tinygpt.json       the tiny GPT on northbridge_corpus.md (experiments/models_modal.py, job tiny)
The forward pass the 3D scene plays is brain3d/trace.json (the 3D builder's); it is not copied here.
Writes ledgerline/ledgerline/course/l2/rec_qwen.json (NB2's replay fallback for its Qwen cells).
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "experiments" / "logs"
PKG = HERE.parents[1] / "ledgerline" / "ledgerline" / "course" / "l2"
J = lambda n: json.loads((LOGS / n).read_text())

cold, card, tk, bpe = J("cold_open.json"), J("model_card.json"), J("tokens.json"), J("bpe.json")
cut, tiny, nbq = J("cutoff.json"), J("tinygpt.json"), J("nb_qwen.json")

P_IN, P_OUT = cold["price_usd_per_million"]
usd = lambda tin, tout: (tin * P_IN + tout * P_OUT) / 1e6   # model costs in US dollars, at the provider's prices
keep = lambda r, ks: dict({k: r[k] for k in ks if k in r}, cost_usd=round(usd(r["tokens_in"], r["tokens_out"]), 6))
RUN = ("run", "reply", "stock_figure", "tokens_in", "tokens_out", "seconds")

# what Gemini counted and billed for one cold-open question
u = (cold["tokens"].get("usage_record") or {}).get("usage") or {}
thinking = (u.get("total_tokens", 0) - u.get("prompt_tokens", 0) - u.get("completion_tokens", 0)) if u else None
tin = cold["runs_summary"]["tokens_in"]
tout = cold["runs_summary"]["mean_tokens_out"]
cost = {"price_usd_per_million": {"in": P_IN, "out": P_OUT},
        "tokens_in": tin, "tokens_out_mean": tout,
        "per_question_usd": round(usd(tin, tout), 6),
        "usage_record": u, "thinking_tokens": thinking,
        "per_question_with_thinking_usd": round(usd(u["prompt_tokens"], u["total_tokens"] - u["prompt_tokens"]), 6) if u else None,
        "per_1000_questions_usd": round(1000 * usd(tin, tout), 3),
        "per_1000_with_thinking_usd": round(1000 * usd(u["prompt_tokens"], u["total_tokens"] - u["prompt_tokens"]), 3) if u else None,
        "note": "tokens_out is the API's completion_tokens (the visible answer); usage_record is one more call of the same "
                "request with the provider's whole usage: total_tokens - prompt - completion = thinking tokens, billed as output"}

# Attention worked by hand on Emma's tokens, seen from the last position: the same inputs as the deck's slide
# (figs.js, QKV: "chosen by hand to show the steps"); the arithmetic is done here. Then the real head it leads into,
# read from Qwen's recorded attention at the last prompt position (nb_qwen.json att_last).
import math
HAND_IN = {"tokens": [" battery", " packs", " Manchester", " stores"], "axes": ["is a place", "is the item"],
           "q": [2, 1], "K": [[0, 2], [0, 1], [2, 0], [1, 0.5]], "V": [[0, 4], [0, 2], [4, 0], [2, 1]]}
_sc = [sum(a * b for a, b in zip(HAND_IN["q"], k)) for k in HAND_IN["K"]]
_ss = [x / math.sqrt(len(HAND_IN["q"])) for x in _sc]
_ex = [math.exp(x) for x in _ss]
_w = [e / sum(_ex) for e in _ex]
_o = [sum(w * v[c] for w, v in zip(_w, HAND_IN["V"])) for c in range(2)]
_A, _pc = nbq["att_last"], nbq["pieces"]
_man = next(i for i, p in enumerate(_pc) if p[2] == "user" and p[0].strip() == "Manchester")
_best = max((_A[l][h][_man], l, h) for l in range(2, len(_A)) for h in range(len(_A[0])))
hand = dict(HAND_IN, d=2, note="numbers chosen by hand to show the steps", scores=_sc, scaled=[round(x, 4) for x in _ss],
            exp=[round(x, 4) for x in _ex], exp_sum=round(sum(_ex), 4), weights=[round(x, 4) for x in _w],
            output=[round(x, 4) for x in _o],
            real_head={"block": _best[1] + 1, "head": _best[2], "weight_on_manchester": round(_best[0], 4),
                       "from": "nb_qwen.json att_last (last prompt position), blocks 3-24; the rule brain3d/capture_trace.py uses for its Manchester head"})

man = next(w for w in cold["truth"]["warehouses"] if w["warehouse"] == "WH-MAN-STR")
L2 = {
    "cold": {"model": cold["model"].split(":")[1], "system": cold["system"], "question": cold["question"],
             "true_answer": cold["true_answer"],
             "truth": {"manchester": man["on_hand"], "all_warehouses": cold["truth"]["free_total"],
                       "warehouses": cold["truth"]["warehouses"], "cover_days_all": cold["truth"]["cover_days"],
                       "item": cold["truth"]["item_code"], "description": cold["truth"]["description"]},
             "runs": [keep(r, RUN) for r in cold["runs"]],
             "summary": dict({k: v for k, v in cold["runs_summary"].items() if k != "cost_gbp_each"},
                             cost_usd_each=[round(usd(r["tokens_in"], r["tokens_out"]), 6) for r in cold["runs"]]),
             "follow_up": keep(cold["follow_up"], ("question", "reply", "tokens_in", "tokens_out")),
             "runs_t1": [keep(r, RUN) for r in cold["runs_t1"]], "summary_t1": cold["runs_t1_summary"],
             "no_system": {"reply": cold["tokens"]["question_only"]["reply"],
                           "stock_figure": cold["tokens"]["question_only"]["stock_figure"]},
             "tool_preview": cold["tool_preview"]},
    "facts": {"line": cold["facts"]["line"], "where": cold["facts"]["where"], "correct": cold["facts"]["correct"],
              "runs": [keep(r, RUN) for r in cold["facts"]["runs"]],
              "qwen_greedy": nbq["greedy_facts_text"].replace("<|im_end|>", ""),
              "qwen_greedy_no_fact": nbq["greedy_text"].replace("<|im_end|>", "")},
    "tokens": {"gemini": {"with_system": cold["tokens"]["with_system"]["tokens_in"],
                          "question_only": cold["tokens"]["question_only"]["tokens_in"],
                          "system_prompt": cold["tokens"]["system_prompt_tokens"],
                          "chars": cold["tokens"]["chars"], "words": cold["tokens"]["words"]},
               "qwen": {k: tk[k] for k in ("n_tokens", "counts", "pieces", "question_tokens", "question_words",
                                          "question_chars", "system_words", "system_chars")},
               "cuts": tk["cuts"], "languages": tk["languages"], "why": tk["why_tokens"], "docs": tk["docs"],
               "corpus": tk["corpus"], "vocab": tk["vocab"]},
    "cost": cost,
    "bpe": bpe,
    "tiny": {k: tiny[k] for k in ("config", "params", "corpus_chars", "corpus_words", "distinct_chars", "uniform_loss",
                                  "train_seconds_cpu2", "curve", "samples_untrained", "samples", "stock_prompt",
                                  "stock_samples", "stock_figures", "stock_5400", "corpus_first_day", "corpus_last_day")},
    "cutoff": {"gemini": cold["cutoff"], "qwen": cut, "tiny_last_day": tiny["corpus_last_day"]},
    "card": card,
    "hand": hand,
}
(HERE / "figdata.js").write_text("/* Generated by gen_figdata.py from experiments/logs/*.json (v4, Northbridge Cycles). "
                                 "Do not edit by hand. The 3D scene's numbers are in brain3d/trace.json. */\n"
                                 "window.L2 = " + json.dumps(L2, ensure_ascii=False, separators=(",", ":")) + ";\n")

# NB2's replay fallback for its Qwen cells, and the Gemini usage record its cost exercise uses
rec = dict(nbq, hand=hand, usage_record=u, cutoff_qwen=cut, why_tokens=tk["why_tokens"], languages=tk["languages"], cuts=tk["cuts"],
           tiny_curve=tiny["curve"])
(PKG / "rec_qwen.json").write_text(json.dumps(rec, ensure_ascii=False))
for old in ("rec_attention.json", "rec_next_token.json", "rec_tokens.json"):  # the v3 replay files
    (PKG / old).unlink(missing_ok=True)
print("figdata.js", (HERE / "figdata.js").stat().st_size // 1024, "KB; keys:", list(L2))
print("rec_qwen.json", (PKG / "rec_qwen.json").stat().st_size // 1024, "KB")
