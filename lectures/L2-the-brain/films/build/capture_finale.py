"""For the "finale" film (v5): real numbers the whole-machine journey needs that trace.json, qkv_data.json and
structure_data.json do not already hold. Same model, revision and prompt as brain3d/trace.json, on Modal CPU.
Writes films/build/data/finale_data.json:

  emb        the full 896-number input-embedding row of every prompt token (positions 0..99) and of the 20 answer tokens
  att1_avg   block 1's attention, averaged over its 14 heads: for every position, the weights on positions 0..i
  (a block-1 head-0 q/k/v recomputation is also attempted, but its check against the model's own weights failed, so
   it is dropped before writing and nothing uses it)

    MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/capture_finale.py
"""
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
L2 = HERE.parent.parent
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch==2.4.1", index_url="https://download.pytorch.org/whl/cpu")
         .pip_install("transformers==4.46.3", "numpy<2.1", "accelerate"))
app = modal.App("l2-finale-capture", image=image)
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


@app.function(cpu=4, memory=12288, timeout=1800)
def capture(chat_text: str, revision: str, ids_ref: list, gen_ids: list) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers.models.qwen2.modeling_qwen2 import apply_rotary_pos_emb
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(MODEL, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=revision, torch_dtype=torch.float32,
                                                 attn_implementation="eager").eval()
    ids = tok(chat_text, add_special_tokens=False).input_ids
    assert ids == ids_ref, "prompt tokens differ from trace.json"
    E = model.get_input_embeddings().weight
    r4 = lambda v: [round(float(x), 5) for x in v]  # noqa: E731
    emb = {str(i): r4(E[t]) for i, t in enumerate(ids)}
    emb_gen = [r4(E[t]) for t in gen_ids]
    # block 1 attention (all heads), and its q/k/v at the last position
    cap = {}
    blk = model.model.layers[0]

    def hook(mod, args, kwargs):
        cap["h"] = kwargs.get("hidden_states", args[0] if args else None)
    hd = blk.self_attn.register_forward_pre_hook(hook, with_kwargs=True)
    out = model(torch.tensor([ids]), output_attentions=True, use_cache=False)
    hd.remove()
    A = out.attentions[0][0]          # (14, 100, 100)
    avg = A.mean(0)
    att1 = [[round(float(x), 5) for x in avg[i, :i + 1]] for i in range(len(ids))]
    h = cap["h"]                       # the normed input to block 1's attention (input_layernorm applied in the layer)
    hn = blk.input_layernorm(h) if cap.get("normed") is None else h
    sa = blk.self_attn
    hdim = 64
    q = sa.q_proj(hn).view(1, len(ids), 14, hdim).transpose(1, 2)
    k = sa.k_proj(hn).view(1, len(ids), 2, hdim).transpose(1, 2)
    v = sa.v_proj(hn).view(1, len(ids), 2, hdim).transpose(1, 2)
    pos = torch.arange(len(ids)).unsqueeze(0)
    cos, sin = model.model.rotary_emb(v, pos)
    q, k = apply_rotary_pos_emb(q, k, cos, sin)
    w = torch.softmax((q[0, 0, -1] @ k[0, 0].T) / 8.0, -1)
    check = float((w - A[0, -1]).abs().max())
    return {"model": MODEL, "revision": revision, "n_tokens": len(ids), "emb": emb, "emb_gen": emb_gen, "gen_ids": gen_ids,
            "att1_avg": att1, "qkv1": {"layer": 1, "head": 0, "pos": len(ids) - 1, "q": r4(q[0, 0, -1]), "k": r4(k[0, 0, -1]),
                                        "v": r4(v[0, 0, -1]), "check_max_abs_diff": check},
            "note": "emb = input-embedding rows (896); att1_avg = block 1 attention averaged over 14 heads, row i over positions 0..i; "
                    "qkv1 = block 1 head 0 at the last position (q and k after RoPE); check = |softmax(q.k/8) - model's own weights|"}


@app.local_entrypoint()
def main():
    t = json.loads((L2 / "brain3d" / "trace.json").read_text())
    gen_ids = [g["id"] for g in t["generation"]["greedy"]]
    res = capture.remote(t["prompt"]["chat_text"], t["meta"]["revision"], [x["id"] for x in t["tokens"]], gen_ids)
    print("qkv1 check (dropped):", res.pop("qkv1")["check_max_abs_diff"])
    res["note"] = ("emb = input-embedding rows (896) of the 100 prompt tokens; emb_gen = the same for the 20 greedy answer tokens "
                   "(gen_ids); att1_avg = block 1 attention (the model's own output_attentions, eager) averaged over its 14 heads, "
                   "row i over positions 0..i")
    dst = HERE / "data" / "finale_data.json"
    dst.write_text(json.dumps(res, separators=(",", ":")))
    print("wrote", dst, round(dst.stat().st_size / 1e6, 2), "MB")
