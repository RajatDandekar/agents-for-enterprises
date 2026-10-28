"""Build figdata.js (the deck's numbers) and the notebook's replay files from experiments/logs/. Stdlib only.

    python3 lectures/L2-the-brain/gen_figdata.py

Every number the deck draws comes from these logs:
  logs/cold_open.json, logs/cold_open_variants.json   (gemini via bahi.llm, experiments/cold_open*.py)
  logs/model_card.json ... logs/tinygpt.json           (Qwen2.5-0.5B and the tiny GPT, experiments/models_modal.py)
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "experiments" / "logs"
PKG = HERE.parents[1] / "bahi" / "bahi" / "course" / "l2"
J = lambda n: json.loads((LOGS / n).read_text())

cold, var = J("cold_open.json"), J("cold_open_variants.json")
card, nt, tk, bpe = J("model_card.json"), J("next_token.json"), J("tokens.json"), J("bpe.json")
emb, att, lens, sur = J("embeddings.json"), J("attention.json"), J("logit_lens.json"), J("surprise.json")
smp, chat, hand, tiny = J("samples.json"), J("chat_template.json"), J("hand_attention.json"), J("tinygpt.json")
extra = J("extra.json")

FD = {
    "cold": {"question": cold["question"], "truth": cold["truth"],
             "plain_t0": cold["canonical"], "plain_follow": cold["follow_up"],
             "run1_t1": cold["samples_summary"], "tool": cold["tool_preview"],
             "cells": [{"sys": c["system_name"], "model": c["model"].split(":")[1], "t0": c["t0"],
                        "follow": c.get("follow_up"), "nums": [s["numbers"][0] if s["numbers"] else None for s in c["samples_t1"]],
                        "replies": [s["reply"] for s in c["samples_t1"]]} for c in var["cells"]],
             "systems": {c["system_name"]: c["system"] for c in var["cells"]}},
    "card": card,
    "nt": {k: {"prompt": v["prompt"], "top": v["top"][:12], "logits60": v["logits60"], "entropy": v["entropy_bits"],
               "n_tokens": v["n_tokens"]} for k, v in nt.items() if isinstance(v, dict) and "top" in v},
    "greedy": nt["greedy_steps"], "greedy_text": nt["greedy_text"],
    "stock_samples": nt["stock_samples"], "stock_greedy": nt["stock_greedy"], "supplier_greedy": nt["supplier_greedy"],
    "tok": {"sentences": [{k: s[k] for k in ("text", "chars", "words", "bytes", "n_qwen", "n_gpt2")} |
                          {"qwen": [[p["text"], p["bytes"], p["id"]] for p in s["qwen"]],
                           "gpt2": [[p["text"], p["bytes"], p["id"]] for p in s["gpt2"]]} for s in tk["sentences"]],
            "docs": tk["docs"], "corpus": tk["corpus"], "vocab": tk["vocab"]},
    "bpe": bpe,
    "emb": {"words": emb["words"], "groups": emb["groups"], "pieces": emb["pieces"],
            "static": {k: emb["static"][k] for k in ("xy", "nn", "within", "between", "nn_same_group", "pca_var")},
            "layers": {L: {k: v[k] for k in ("xy", "nn", "within", "between", "nn_same_group", "pca_var")}
                       for L, v in emb["layers"].items()},
            "cos_static": emb["static"]["cos"], "cos_layers": {L: v["cos"] for L, v in emb["layers"].items()}, "first8": emb["gasket_vector_first8"], "ids": emb["gasket_token_ids"],
            "vnn": emb["vocab_neighbours"]},
    "att": {"tokens": att["tokens"], "L": att["layers"], "H": att["heads"], "gi": att["gaskets_index"],
            "num": att["number_indices"], "top_prev": att["top_prev_token"], "top_num": att["top_gaskets_to_number"],
            "mean_first": att["mean_first_token"],
            # per-mille integers keep the file small: att[l][h][i][j] = round(1000 * weight)
            "w": [[[[round(v * 1000) for v in row] for row in head] for head in layer] for layer in att["att"]]},
    "lens": lens, "surprise": sur,
    "samples": {"prompt": smp["prompt"], "runs": smp["runs"], "logits60": smp["dist"]["logits60"]},
    "chat": {k: chat[k] for k in ("model", "messages", "template", "n_tokens", "pieces", "answer_greedy", "answers_t08",
                                  "turn2_n_tokens", "turn2_answer")},
    "hand": hand, "extra": extra,
    "tiny": {k: tiny[k] for k in ("config", "params", "corpus_chars", "train_seconds_cpu2", "curve", "sample_untrained",
                                  "samples", "stock_samples")},
}
# the head where the last piece of " gaskets" puts the most weight on the digits of 20,000 (commas and spaces excluded)
T_, gi_ = att["tokens"], att["gaskets_index"]
dig_ = [i for i in att["number_indices"] if T_[i].strip().isdigit()]
w_, l_, h_ = max((sum(att["att"][l][h][gi_][j] for j in dig_), l, h) for l in range(att["layers"]) for h in range(att["heads"]))
FD["att"]["digit_head"] = {"layer": l_, "head": h_, "w": round(w_, 3)}
# which representation the map opens on: the one whose groups separate best (nearest neighbour in the same group)
reps = {"static": emb["static"], **emb["layers"]}
FD["emb_choice"] = max(reps, key=lambda r: (reps[r]["nn_same_group"], reps[r]["within"] - reps[r]["between"]))
print("embedding map opens on:", FD["emb_choice"], {r: (v["nn_same_group"], round(v["within"] - v["between"], 3)) for r, v in reps.items()})
(HERE / "figdata.js").write_text("/* Generated by gen_figdata.py from experiments/logs/*.json. Do not edit by hand. */\n"
                                 "window.FD = " + json.dumps(FD, ensure_ascii=False, separators=(",", ":")) + ";\n")

# replay files for the notebook (shipped inside the bahi package)
rec_next = {v["prompt"]: v for k, v in nt.items() if isinstance(v, dict) and "top" in v}
rec_next[extra["stock_prompt"]] = {"prompt": extra["stock_prompt"], "top": extra["stock_top"]}
rec_next["stock_samples"] = extra["stock_samples"]
(PKG / "rec_next_token.json").write_text(json.dumps(rec_next, ensure_ascii=False))
(PKG / "rec_tokens.json").write_text(json.dumps({"sentences": tk["sentences"]}, ensure_ascii=False))
prev = att["top_prev_token"][0]
(PKG / "rec_attention.json").write_text(json.dumps({"sentence": att["sentence"], "tokens": att["tokens"], "att": att["att"],
                                                    "gaskets_index": att["gaskets_index"], "number_indices": att["number_indices"],
                                                    "prev_head": prev}, ensure_ascii=False))
print("figdata.js", (HERE / "figdata.js").stat().st_size // 1024, "KB; replay files written to", PKG)
