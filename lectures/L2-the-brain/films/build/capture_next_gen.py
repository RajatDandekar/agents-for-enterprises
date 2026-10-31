"""For the films `next_token` and `generation`: the same forward pass as brain3d/trace.json (Qwen2.5-0.5B-Instruct,
float32, eager attention, Modal CPU), recorded in more detail.

  next_token  the last position's vector after block 24 BEFORE and AFTER the final RMSNorm (its RMS, the norm's gains),
              the tied embedding table (lm_head is the same tensor), the 151,936 logits (histogram + top rows), the dot
              product for the top tokens (running sums), e^logit and their sum, and real draws from the softmax.
  generation  the KV cache: shapes after the prompt, then the 20 greedy steps fed ONE token at a time with the cache;
              every step's logits are checked against a full recompute without the cache; the new column's attention
              (averaged over 14 heads x 24 blocks) over all earlier positions.

    MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/capture_next_gen.py
Writes films/build/data/next_token_data.json and films/build/data/generation_data.json.
"""
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
L2 = HERE.parent.parent
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch==2.4.1", index_url="https://download.pytorch.org/whl/cpu")
         .pip_install("transformers==4.46.3", "numpy<2.1", "accelerate"))
app = modal.App("l2-next-gen-capture", image=image)
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


def r(x, n=4):
    return round(float(x), n)


@app.function(cpu=4, memory=12288, timeout=2400)
def capture(chat_text: str, revision: str, ids_ref: list, greedy_ref: list) -> dict:
    import math
    import time

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(MODEL, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=revision, torch_dtype=torch.float32,
                                                 attn_implementation="eager").eval()
    ids = tok(chat_text, add_special_tokens=False).input_ids
    assert ids == ids_ref, "prompt tokens differ from trace.json"
    cfg = model.config
    E = model.model.embed_tokens.weight            # [151936, 896]
    tied = model.lm_head.weight.data_ptr() == E.data_ptr()
    # ---------------------------------------------------------------- next_token: the final norm and the scoring
    grab = {}
    hk = model.model.norm.register_forward_hook(lambda m, i, o: grab.update(pre=i[0].detach().clone(), post=o.detach().clone()))
    out = model(torch.tensor([ids]), use_cache=True)
    hk.remove()
    logits = out.logits[0, -1].double()
    pre = grab["pre"][0, -1].double()
    post = grab["post"][0, -1].double()
    gamma = model.model.norm.weight.double()
    eps = cfg.rms_norm_eps
    rms = math.sqrt(float((pre ** 2).mean()) + eps)
    mine = pre / rms * gamma
    my_logits = E.double() @ mine
    order = torch.argsort(logits, descending=True)
    top = [int(i) for i in order[:12]]
    logZ = float(torch.logsumexp(logits, 0))
    p = torch.softmax(logits, 0)
    hist_lo, hist_hi, nb = float(logits.min()), float(logits.max()), 64
    hist = torch.histc(logits.float(), bins=nb, min=hist_lo, max=hist_hi)

    def dot_detail(tid):
        row = E[tid].double()
        prod = row * mine
        cs = torch.cumsum(prod, 0)
        big = torch.argsort(prod.abs(), descending=True)[:8]
        return {"id": tid, "text": tok.decode([tid]), "logit": r(logits[tid]), "logit_from_dot": r(float(prod.sum())),
                "row16": [r(x) for x in row[:16]], "vec16": [r(x) for x in mine[:16]], "prod16": [r(x) for x in prod[:16]],
                "cumsum_every32": [r(cs[k]) for k in range(31, 896, 32)],
                "biggest_terms": [{"dim": int(k), "row": r(row[k]), "vec": r(mine[k]), "prod": r(prod[k])} for k in big],
                "positive_terms": int((prod > 0).sum()), "negative_terms": int((prod < 0).sum())}

    draws = {}
    for T in (0.7, 1.0, 1.2):
        g = torch.Generator().manual_seed(0)
        pt = torch.softmax(logits / T, 0)
        s = torch.multinomial(pt.float(), 1000, replacement=True, generator=g)
        cnt = torch.bincount(s, minlength=logits.numel())
        oc = torch.argsort(cnt, descending=True)[:8]
        draws[str(T)] = {"n": 1000, "seed": 0, "distinct": int((cnt > 0).sum()),
                         "top": [{"id": int(i), "text": tok.decode([int(i)]), "count": int(cnt[i])} for i in oc if cnt[i] > 0]}
    first5 = {}
    for T in (0.7, 1.0):   # the first five single draws (seed 0), as the model would make them one by one
        g = torch.Generator().manual_seed(0)
        pt = torch.softmax(logits / T, 0).float()
        first5[str(T)] = [tok.decode([int(torch.multinomial(pt, 1, generator=g))]) for _ in range(5)]
    nt = {
        "model": MODEL, "revision": revision, "n_tokens": len(ids), "tied_embeddings": bool(tied),
        "table_shape": list(E.shape), "rms_norm_eps": eps,
        "pre_norm": {"rms": r(rms), "min": r(pre.min()), "max": r(pre.max()), "abs_max_dim": int(pre.abs().argmax()),
                     "first16": [r(x) for x in pre[:16]], "values": [r(x, 3) for x in pre]},
        "gamma": {"min": r(gamma.min()), "max": r(gamma.max()), "mean": r(gamma.mean()), "first16": [r(x) for x in gamma[:16]]},
        "post_norm": {"rms": r(math.sqrt(float((post ** 2).mean()))), "min": r(post.min()), "max": r(post.max()),
                      "first16": [r(x) for x in post[:16]], "values": [r(x, 3) for x in post],
                      "check_max_abs_diff_vs_mine": float((post - mine).abs().max())},
        "logits": {"n": logits.numel(), "check_max_abs_diff_table_dot_vs_model": float((my_logits - logits).abs().max()),
                   "min": r(logits.min()), "max": r(logits.max()), "mean": r(logits.mean()), "std": r(logits.std()),
                   "n_positive": int((logits > 0).sum()), "argmin": {"id": int(logits.argmin()), "text": tok.decode([int(logits.argmin())]),
                                                                    "logit": r(logits.min())},
                   "hist": {"lo": r(hist_lo), "hi": r(hist_hi), "bins": nb, "counts": [int(x) for x in hist]},
                   "n_above_17": int((logits > 17).sum()), "n_above_18": int((logits > 18).sum())},
        "top": [{"id": i, "text": tok.decode([i]), "logit": r(logits[i]), "exp": float(math.exp(float(logits[i]))),
                 "p": r(p[i], 6)} for i in top],
        "logZ": r(logZ, 5), "sum_exp": float(math.exp(logZ)), "p_rest_after_top6": r(1 - float(p[order[:6]].sum()), 5),
        "dots": [dot_detail(i) for i in top[:6]],
        "draws": draws, "first5_draws": first5,
        "note": "pre_norm = the last position's residual stream after block 24 (input of model.norm); post_norm = model.norm output = "
                "pre / rms * gamma; logits = embed_tokens.weight @ post_norm (lm_head shares the tensor: tied); exp/sum_exp in float64; "
                "draws = torch.multinomial(softmax(logits / T), 1000, seed 0)",
    }
    # ---------------------------------------------------------------- generation: the KV cache, one column per token
    pkv = out.past_key_values
    k0, v0 = pkv[0][0], pkv[0][1]
    cache_shapes = {"layers": len(pkv), "k": list(k0.shape), "v": list(v0.shape)}
    per_pos_per_block = 2 * k0.shape[1] * k0.shape[3]
    steps = []
    cur = list(ids)
    nxt = int(torch.argmax(out.logits[0, -1]))
    for j in range(len(greedy_ref)):
        lg = out.logits[0, -1].double()
        pj = torch.softmax(lg, 0)
        o5 = torch.argsort(lg, descending=True)[:5]
        nxt = int(o5[0])
        assert nxt == greedy_ref[j], f"step {j}: {nxt} != trace {greedy_ref[j]}"
        cache_len = pkv[0][0].shape[2]
        # full recompute without the cache, to check the cache gives the same answer
        t0 = time.time()
        full = model(torch.tensor([cur]), use_cache=False).logits[0, -1].double()
        t_full = time.time() - t0
        st = {"step": j + 1, "context_len": len(cur), "cache_len": cache_len, "token": tok.decode([nxt]), "id": nxt,
              "p": r(pj[nxt], 5), "alts": [{"text": tok.decode([int(i)]), "p": r(pj[i], 5)} for i in o5],
              "max_abs_diff_cached_vs_full": float((full - lg).abs().max()), "sec_full_recompute": round(t_full, 3)}
        steps.append(st)
        cur.append(nxt)
        if j == len(greedy_ref) - 1:
            break
        t0 = time.time()
        out = model(torch.tensor([[nxt]]), past_key_values=pkv, use_cache=True, output_attentions=True)
        st["sec_next_cached_step"] = round(time.time() - t0, 3)
        pkv = out.past_key_values
        att = torch.stack([a[0, :, 0, :] for a in out.attentions]).mean(dim=(0, 1))   # [L] over all earlier positions + itself
        st["next_column"] = {"position": len(cur) - 1, "reads_positions": int(att.numel()),
                             "attn_avg": [r(x, 5) for x in att], "share_prompt": r(att[:len(ids)].sum(), 4),
                             "share_answer_so_far": r(att[len(ids):].sum(), 4)}
    gen = {
        "model": MODEL, "revision": revision, "prompt_len": len(ids), "cache_after_prompt": cache_shapes,
        "cached_numbers_per_position_per_block": int(per_pos_per_block),
        "cached_numbers_per_position": int(per_pos_per_block * len(pkv)),
        "cached_numbers_after_prompt": int(per_pos_per_block * len(pkv) * len(ids)),
        "steps": steps, "text": tok.decode(cur[len(ids):], skip_special_tokens=False),
        "note": "prompt run once with use_cache=True; then each greedy token fed alone with past_key_values (one new column through "
                "24 blocks); each step's logits compared with a full recompute of the whole sequence without the cache; "
                "attn_avg = the new column's attention averaged over 14 heads and 24 blocks (eager)",
    }
    return {"next_token": nt, "generation": gen}


@app.local_entrypoint()
def main():
    t = json.loads((L2 / "brain3d" / "trace.json").read_text())
    res = capture.remote(t["prompt"]["chat_text"], t["meta"]["revision"], [x["id"] for x in t["tokens"]],
                         [g["id"] for g in t["generation"]["greedy"]])
    (HERE / "data").mkdir(exist_ok=True)
    for k, name in (("next_token", "next_token_data.json"), ("generation", "generation_data.json")):
        dst = HERE / "data" / name
        dst.write_text(json.dumps(res[k], separators=(",", ":")))
        print("wrote", dst, round(dst.stat().st_size / 1e3, 1), "kB")


@app.function(cpu=4, memory=12288, timeout=2400)
def capture_extra(chat_text: str, revision: str, ids_ref: list, greedy_ref: list) -> dict:
    """Full 896-number rows of the (tied) table for the top-6 tokens and 42 evenly spaced rows, plus the new column's
    attention per block (averaged over the 14 heads) at every greedy step with the KV cache."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(MODEL, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=revision, torch_dtype=torch.float32,
                                                 attn_implementation="eager").eval()
    ids = tok(chat_text, add_special_tokens=False).input_ids
    assert ids == ids_ref
    E = model.model.embed_tokens.weight
    out = model(torch.tensor([ids]), use_cache=True)
    lg = out.logits[0, -1]
    top6 = [int(i) for i in torch.argsort(lg, descending=True)[:6]]
    spaced = [int(i * (E.shape[0] - 1) / 41) for i in range(42)]
    rows = {"top6": [{"id": i, "text": tok.decode([i]), "logit": r(lg[i]), "row": [r(x, 5) for x in E[i]]} for i in top6],
            "spaced": [{"id": i, "text": tok.decode([i]), "logit": r(lg[i]), "row": [r(x, 5) for x in E[i]]} for i in spaced],
            "note": "rows of model.model.embed_tokens.weight (== lm_head.weight, tied); logit = that row . final normed vector"}
    pkv = out.past_key_values
    att_steps = []
    for j, nxt in enumerate(greedy_ref[:-1]):
        o = model(torch.tensor([[nxt]]), past_key_values=pkv, use_cache=True, output_attentions=True)
        pkv = o.past_key_values
        per_layer = [[r(x, 5) for x in a[0, :, 0, :].mean(0)] for a in o.attentions]
        att_steps.append({"step": j + 2, "position": len(ids) + j, "token_in": tok.decode([nxt]), "per_block": per_layer})
    return {"rows": rows, "attn": {"steps": att_steps, "note": "att_steps[s].per_block[b][p] = attention of the new column "
                                   "(the token fed at this step) in block b+1, averaged over 14 heads, on position p (KV cache run)"}}


@app.local_entrypoint()
def extra():
    t = json.loads((L2 / "brain3d" / "trace.json").read_text())
    res = capture_extra.remote(t["prompt"]["chat_text"], t["meta"]["revision"], [x["id"] for x in t["tokens"]],
                               [g["id"] for g in t["generation"]["greedy"]])
    for k, name in (("rows", "next_token_rows.json"), ("attn", "generation_attn.json")):
        dst = HERE / "data" / name
        dst.write_text(json.dumps(res[k], separators=(",", ":")))
        print("wrote", dst, round(dst.stat().st_size / 1e3, 1), "kB")
