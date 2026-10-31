"""For the "heads" and "blocks" films: real per-head attention on Emma's prompt (the same forward pass as brain3d/trace.json),
plus per-block, per-position updates of all 100 vectors, on Modal CPU. Writes films/build/data/heads_data.json and
films/build/data/blocks_data.json.

    MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/capture_heads.py

Qwen2.5-0.5B-Instruct, float32, eager attention, output_attentions. Every measure is a plain share of attention weight:
  prev      mean over query positions i = 1..99 of weight on position i-1
  first     mean over query positions i = 1..99 of weight on position 0 (<|im_start|>, the "rest" token)
  last_*    the last prompt position's (99) row: its top positions, its weight on " Manchester" (92), " battery" (86), ...
  digits    the last position's weight on the date's digit tokens (2 6 2 0 2 6) / on the whole date span
  dup       for query positions whose token appeared earlier, mean weight on those earlier copies
  induction for the same positions, mean weight on the token right after each earlier copy
"""
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
L2 = HERE.parent.parent
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch==2.4.1", index_url="https://download.pytorch.org/whl/cpu")
         .pip_install("transformers==4.46.3", "numpy<2.1", "accelerate", "sentencepiece")
         .run_commands("python -c \"from transformers import AutoTokenizer, AutoModelForCausalLM as M; "
                       "AutoTokenizer.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct'); M.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct')\""))
app = modal.App("l2-heads-capture", image=image)
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


def r4(x):
    return round(float(x), 4)


@app.function(cpu=4, memory=12288, timeout=1800)
def capture(chat_text: str, revision: str, ids_ref: list, gen_ids: list) -> dict:
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(MODEL, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=revision, torch_dtype=torch.float32,
                                                 attn_implementation="eager").eval()
    ids = tok(chat_text, add_special_tokens=False).input_ids
    assert ids == ids_ref, "prompt tokens differ from trace.json"
    L = model.config.num_hidden_layers
    H = model.config.num_attention_heads
    KV = model.config.num_key_value_heads

    # hooks: block input/output, attention output, MLP output, o_proj input (the 14 heads joined), MLP hidden
    rec = {}

    def hook(name):
        def f(mod, inp, out):
            o = out[0] if isinstance(out, tuple) else out
            rec[name] = o.detach()[0].clone()
            if name.startswith("o_in"):
                pass
        return f

    def pre(name):
        def f(mod, args):
            rec[name] = args[0].detach()[0].clone()
        return f

    hs = []
    for l, layer in enumerate(model.model.layers):
        hs.append(layer.register_forward_pre_hook(pre(f"in{l}")))
        hs.append(layer.register_forward_hook(hook(f"out{l}")))
        hs.append(layer.self_attn.register_forward_hook(hook(f"attn{l}")))
        hs.append(layer.mlp.register_forward_hook(hook(f"mlp{l}")))
        hs.append(layer.self_attn.o_proj.register_forward_pre_hook(pre(f"oin{l}")))
        hs.append(layer.mlp.down_proj.register_forward_pre_hook(pre(f"mid{l}")))
        for nm in ("q", "k", "v"):
            hs.append(getattr(layer.self_attn, nm + "_proj").register_forward_hook(hook(f"{nm}{l}")))
    out = model(torch.tensor([ids]), output_attentions=True, use_cache=False)
    att = np.stack([a[0].numpy() for a in out.attentions])   # [L, H, T, T]
    rec1 = dict(rec)   # the 100-token pass (the second pass below overwrites rec)
    T = len(ids)
    texts = [tok.decode([i]) for i in ids]
    last = T - 1
    pos = {"Manchester": 92, "battery": 86, "packs": 87, "stores": 93, "city": 82, "Manchester_sys": 21}
    for k, v in pos.items():
        assert texts[v].strip() == k.split("_")[0], (k, texts[v])
    date_digits = [i for i in range(40, 53) if texts[i].strip().isdigit()]
    date_span = list(range(42, 52))   # " Monday" .. final "6" of 2026
    question = list(range(80, 95))
    system_span = list(range(0, 77))
    # earlier copies of the same token
    dups = {i: [j for j in range(i) if ids[j] == ids[i]] for i in range(T)}
    dup_q = [i for i in range(1, T) if dups[i]]

    heads = []
    for l in range(L):
        for h in range(H):
            A = att[l, h]
            prev = float(np.mean([A[i, i - 1] for i in range(1, T)]))
            first = float(np.mean([A[i, 0] for i in range(1, T)]))
            row = A[last]
            order = np.argsort(-row)
            top = [{"pos": int(j), "tok": texts[j], "w": r4(row[j])} for j in order[:5]]
            # the strongest non-rest, non-self target of the last position
            content = [j for j in order if j not in (0, last)]
            dup = float(np.mean([A[i, dups[i]].sum() for i in dup_q]))
            ind = float(np.mean([A[i, [j + 1 for j in dups[i] if j + 1 < i]].sum() for i in dup_q]))
            heads.append({
                "block": l + 1, "head": h, "kv_group": h // (H // KV),
                "prev": r4(prev), "first": r4(first), "self_last": r4(row[last]), "first_last": r4(row[0]),
                "last_top": top, "last_peak": {"pos": int(content[0]), "tok": texts[content[0]], "w": r4(row[content[0]])},
                "last_on": {k: r4(row[v]) for k, v in pos.items()},
                "last_question": r4(row[question].sum()), "last_system": r4(row[system_span].sum()),
                "last_date_digits": r4(row[date_digits].sum()), "last_date_span": r4(row[date_span].sum()),
                "dup": r4(dup), "induction": r4(ind),
                "entropy_last": r4(-(row[row > 0] * np.log(row[row > 0])).sum()),
            })

    # second pass: the prompt + "We currently have " (the step that writes the first digit), last-position rows
    ids2 = ids + gen_ids
    out2 = model(torch.tensor([ids2]), output_attentions=True, use_cache=False)
    att2 = np.stack([a[0].numpy() for a in out2.attentions])
    q2 = len(ids2) - 1
    texts2 = [tok.decode([i]) for i in ids2]
    digit_rows = {f"{l + 1}.{h}": [r4(v) for v in att2[l, h, q2]] for (l, h) in ((1, 7), (9, 13), (0, 3))}
    digit_heads = []
    for l in range(L):
        for h in range(H):
            row = att2[l, h, q2]
            digit_heads.append({"block": l + 1, "head": h, "date_digits": r4(row[date_digits].sum()),
                                "date_span": r4(row[date_span].sum()),
                                "top": [{"pos": int(j), "tok": texts2[j], "w": r4(row[j])} for j in np.argsort(-row)[:5]]})

    # per block, per position: how much each of the 100 vectors changed (full 896 numbers, not 16)
    blocks = []
    for l in range(L):
        x_in, x_out = rec1[f"in{l}"].numpy(), rec1[f"out{l}"].numpy()
        a_o, m_o = rec1[f"attn{l}"].numpy(), rec1[f"mlp{l}"].numpy()
        nin = np.linalg.norm(x_in, axis=1)
        d = np.linalg.norm(x_out - x_in, axis=1)
        cos = (x_in * x_out).sum(1) / (nin * np.linalg.norm(x_out, axis=1) + 1e-9)
        blocks.append({"block": l + 1,
                       "rel_change": [r4(v) for v in d / (nin + 1e-9)],
                       "cos_in_out": [r4(v) for v in cos],
                       "attn_norm": [r4(v) for v in np.linalg.norm(a_o, axis=1)],
                       "mlp_norm": [r4(v) for v in np.linalg.norm(m_o, axis=1)],
                       "in_norm": [r4(v) for v in nin],
                       "n_changed": int((d > 1e-6).sum()),
                       "last_on_question_avg": r4(att[l, :, last, question].sum(-1).mean()),
                       "last_on_system_avg": r4(att[l, :, last, system_span].sum(-1).mean()),
                       "last_on_first_avg": r4(att[l, :, last, 0].mean())})
    # the 14 heads at the last position of block 24 and block 12: 14 x 64 = 896 joined, then o_proj
    joins = {}
    for l in (0, 11, 23):
        oin = rec1[f"oin{l}"].numpy()[last]           # 896 = 14 heads x 64, concatenated
        aout = rec1[f"attn{l}"].numpy()[last]         # after o_proj
        joins[str(l + 1)] = {"heads_concat": [r4(v) for v in oin], "per_head_norm": [r4(np.linalg.norm(oin[h * 64:(h + 1) * 64])) for h in range(H)],
                             "o_proj_out": [r4(v) for v in aout]}
    mid = {str(l + 1): [round(float(v), 3) for v in rec1[f"mid{l}"].numpy()[last]] for l in (0, 11, 23)}
    vecs = {str(l + 1): {"in": [r4(v) for v in rec1[f"in{l}"].numpy()[last]],
                         "after_attention": [r4(v) for v in (rec1[f"in{l}"] + rec1[f"attn{l}"]).numpy()[last]],
                         "out": [r4(v) for v in rec1[f"out{l}"].numpy()[last]]} for l in (0, 11, 23)}
    w = model.model.layers[0].self_attn
    shapes = {"q_proj": list(w.q_proj.weight.shape), "k_proj": list(w.k_proj.weight.shape), "v_proj": list(w.v_proj.weight.shape),
              "o_proj": list(w.o_proj.weight.shape), "gate": list(model.model.layers[0].mlp.gate_proj.weight.shape),
              "down": list(model.model.layers[0].mlp.down_proj.weight.shape)}
    return {"model": MODEL, "revision": revision, "n_tokens": T, "tokens": texts, "heads": heads, "digit_step": {
        "query_pos": q2, "query_tok": texts2[q2], "gen_prefix": texts2[T:], "heads": digit_heads, "rows": digit_rows},
        "qkv_last": {str(l + 1): {nm: [r4(v) for v in rec1[f"{nm}{l}"].numpy()[last]] for nm in ("q", "k", "v")} for l in (0, 11, 23)},
        "blocks": blocks, "joins": joins, "mlp_mid_last": mid, "last_vecs": vecs, "shapes": shapes,
        "date_digits_pos": date_digits, "date_span_pos": date_span, "question_pos": question,
        "mats": {f"{l + 1}.{h}": [[r4(v) for v in r] for r in att[l, h]] for (l, h) in
                 [(23, 2), (11, 13), (15, 0), (18, 13), (2, 2), (8, 7), (1, 7)] + [(l, h) for l in range(L) for h in range(H)
                                                if float(np.mean([att[l, h, i, i - 1] for i in range(1, T)])) > 0.5][:6]},
        "avg_mats": {str(l + 1): [[r4(v) for v in r] for r in att[l].mean(0)] for l in (0, 11, 23)},
        "config": {"layers": L, "heads": H, "kv_heads": KV, "head_dim": model.config.hidden_size // H,
                   "hidden": model.config.hidden_size, "mlp": model.config.intermediate_size}}


@app.local_entrypoint()
def main():
    t = json.loads((L2 / "brain3d" / "trace.json").read_text())
    gen = [s["id"] for s in t["generation"]["greedy"][:t["generation"]["digit_steps"][0]]]
    res = capture.remote(t["prompt"]["chat_text"], t["meta"]["revision"], [x["id"] for x in t["tokens"]], gen)
    dst = HERE / "data" / "heads_raw.json"
    dst.write_text(json.dumps(res, separators=(",", ":")))
    print("wrote", dst, round(dst.stat().st_size / 1e6, 2), "MB")
