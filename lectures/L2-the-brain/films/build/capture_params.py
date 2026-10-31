"""For the films `params` and `s8_weights` (Lecture 2, section 8), on Modal CPU. Nothing heavy runs on the laptop.

  qwen   Qwen2.5-0.5B-Instruct (the trace's revision): every tensor's shape and count (checked against 494,032,768), the
         real values of block 24's q_proj [0:6, 0:6] (+ bias), and colour images of block 24's seven weight matrices
         (one pixel per real weight; sky = positive, violet = negative, brightness = size) plus a row-binned image of the
         embedding table, written to the Modal volume (video-ad-edit:/l2films/data/params/) for the Blender scene.
  tiny   re-runs the tiny GPT (ledgerline/ledgerline/course/l2/tinygpt.py, same corpus, seed and settings as
         experiments/logs/tinygpt.json) and records what the log does not have: the first training batch (32 windows),
         the model's 81 probabilities at every position of one window before and after training, a patch of one weight
         matrix's values and gradient at the first step, and one weight's path over the 1,500 steps.

    MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/capture_params.py
Writes films/build/data/params_data.json and films/build/data/s8_weights_data.json.
"""
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
L2 = HERE.parent.parent
COURSE = L2.parent.parent
L2PKG = COURSE / "ledgerline" / "ledgerline" / "course" / "l2"
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch==2.4.1", index_url="https://download.pytorch.org/whl/cpu")
         .pip_install("transformers==4.46.3", "numpy<2.1", "accelerate", "pillow==10.4.0")
         .add_local_file(str(L2PKG / "tinygpt.py"), "/root/tg/tinygpt.py")
         .add_local_file(str(L2PKG / "northbridge_corpus.md"), "/root/tg/northbridge_corpus.md"))
app = modal.App("l2-params-capture", image=image)
vol = modal.Volume.from_name("video-ad-edit", create_if_missing=True)
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


def _img(w, path, vmax=None, gamma=0.7):
    """Colour image of a weight matrix: row 0 at the top, one pixel per weight."""
    import numpy as np
    from PIL import Image
    a = w.astype("float32")
    vmax = vmax or float(np.percentile(np.abs(a), 99.5))
    t = np.clip(np.abs(a) / vmax, 0, 1) ** gamma
    pos = np.array([60, 144, 255], np.float32) / 255
    neg = np.array([154, 92, 255], np.float32) / 255
    lift = 0.05
    rgb = np.where(a[..., None] >= 0, pos, neg) * (lift + (1 - lift) * t[..., None])
    Image.fromarray((rgb * 255).round().astype("uint8"), "RGB").save(path, optimize=True)
    return vmax


@app.function(cpu=4, memory=16384, timeout=1800, volumes={"/vol": vol})
def qwen(revision: str) -> dict:
    import os

    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM
    torch.set_grad_enabled(False)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=revision, torch_dtype=torch.float32).eval()
    named = dict(model.named_parameters())
    total = sum(p.numel() for p in model.parameters())   # tied: the embedding is counted once
    tensors = {n: list(p.shape) for n, p in named.items() if n.startswith("model.layers.23.") or not n.startswith("model.layers.")}
    blk = {n.replace("model.layers.23.", ""): p.numel() for n, p in named.items() if n.startswith("model.layers.23.")}
    per_block = sum(blk.values())
    blocks_all = sum(p.numel() for n, p in named.items() if n.startswith("model.layers."))
    L = model.model.layers[23]
    q = L.self_attn.q_proj.weight.float().numpy()
    out = {"model": MODEL, "revision": revision, "total_params": total, "per_block": per_block, "blocks_total": blocks_all,
           "block24_tensors": blk, "other_tensors": tensors,
           "embedding": int(named["model.embed_tokens.weight"].numel()), "final_norm": int(named["model.norm.weight"].numel()),
           "tied": bool(model.lm_head.weight.data_ptr() == model.model.embed_tokens.weight.data_ptr()),
           "q_proj_block24_0_6": [[float(x) for x in r] for r in q[0:6, 0:6]],
           "q_bias_block24_0_6": [float(x) for x in L.self_attn.q_proj.bias[0:6]],
           "q_proj_block24_stats": {"min": float(q.min()), "max": float(q.max()), "mean_abs": float(np.abs(q).mean())}}
    d = "/vol/l2films/data/params"
    os.makedirs(d, exist_ok=True)
    mats = {"q": L.self_attn.q_proj.weight, "k": L.self_attn.k_proj.weight, "v": L.self_attn.v_proj.weight,
            "o": L.self_attn.o_proj.weight, "gate": L.mlp.gate_proj.weight, "up": L.mlp.up_proj.weight, "down": L.mlp.down_proj.weight}
    out["images"] = {}
    for nm, p in mats.items():
        a = p.float().numpy()
        vmax = _img(a, f"{d}/{nm}.png")
        out["images"][nm] = {"shape": list(a.shape), "vmax": vmax, "file": f"data/params/{nm}.png"}
    for nm, p in (("norm1", L.input_layernorm.weight), ("norm2", L.post_attention_layernorm.weight), ("final_norm", model.model.norm.weight)):
        a = p.float().numpy()[None, :]
        _img(a - float(np.median(a)), f"{d}/{nm}.png")
        out["images"][nm] = {"shape": list(a.shape), "file": f"data/params/{nm}.png", "median": float(np.median(a))}
    # the embedding table: 151,936 rows binned by 64 (RMS of each column within the bin) -> 2,374 x 896
    E = model.model.embed_tokens.weight.float().numpy()
    n = (E.shape[0] // 64) * 64
    rms = np.sqrt((E[:n].reshape(-1, 64, E.shape[1]) ** 2).mean(1))
    _img(rms, f"{d}/embed.png", gamma=0.9)
    out["images"]["embed"] = {"shape": list(rms.shape), "file": "data/params/embed.png", "note": "RMS of 64 rows per pixel row"}
    vol.commit()
    return out


@app.function(cpu=8, memory=8192, timeout=3600)
def tiny() -> dict:
    import math
    import sys
    import time

    import torch
    import torch.nn.functional as F
    sys.path.insert(0, "/root/tg")
    import tinygpt as TG
    torch.set_num_threads(8)
    text = open("/root/tg/northbridge_corpus.md").read()
    seed, steps, batch, lr = 1337, 1500, 32, 2e-3
    torch.manual_seed(seed)
    chars, enc, dec = TG.encoder(text)
    data = torch.tensor(enc(text), dtype=torch.long)
    n = int(0.9 * len(data))
    train_d, val_d = data[:n], data[n:]
    c = TG.Config(len(chars))
    model = TG.TinyGPT(c)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    g = torch.Generator().manual_seed(seed)
    starts_log = []

    def get(split):
        d = train_d if split == "train" else val_d
        ix = torch.randint(len(d) - c.block_size - 1, (batch,), generator=g)
        starts_log.append((split, ix.tolist()))
        return torch.stack([d[i:i + c.block_size] for i in ix]), torch.stack([d[i + 1:i + 1 + c.block_size] for i in ix])

    @torch.no_grad()
    def estimate():
        model.eval()
        o = {s: sum(model(*get(s))[1].item() for _ in range(10)) / 10 for s in ("train", "val")}
        model.train()
        return o

    def probs_of(window_ids):
        model.eval()
        with torch.no_grad():
            lg, _ = model(window_ids[None])
        model.train()
        return F.softmax(lg[0], -1)

    W = model.blocks[0].attn.qkv.weight   # 384 x 128
    track = (5, 7)
    rec = {"curve": [], "track": []}
    t0 = time.time()
    first = None
    for step in range(steps + 1):
        if step % 100 == 0:
            e = estimate()
            rec["curve"].append({"step": step, "train": round(e["train"], 4), "val": round(e["val"], 4)})
        if step % 10 == 0:
            rec["track"].append([step, round(float(W[track]), 6)])
        if step == steps:
            break
        for gr in opt.param_groups:
            gr["lr"] = lr * min(1.0, (step + 1) / 100) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * step / steps)))
        x, y = get("train")
        if step == 0:
            first = {"x": x.clone(), "y": y.clone(), "starts": starts_log[-1][1]}
            # pick the window to show: the first that holds a stores line, else the first
            texts = [dec(r.tolist()) for r in x]
            pick = next((i for i, s in enumerate(texts) if "on hand" in s), 0)
            P0 = probs_of(x[pick])
        _, loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        if step == 0:
            patch_before = W[0:8, 0:16].detach().clone()
            grad = W.grad[0:8, 0:16].detach().clone()
            rec["step1"] = {"loss_batch": round(loss.item(), 4), "lr": gr["lr"]}
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step == 0:
            patch_after = W[0:8, 0:16].detach().clone()
    secs = time.time() - t0
    P1 = probs_of(first["x"][pick])
    xs, ys = first["x"][pick].tolist(), first["y"][pick].tolist()

    def table(P):
        rows = []
        for i in range(c.block_size):
            p = P[i]
            top = torch.topk(p, 6)
            rows.append({"pos": i, "inp": chars[xs[i]], "target": chars[ys[i]], "p_target": round(float(p[ys[i]]), 5),
                         "loss": round(-math.log(float(p[ys[i]])), 4),
                         "top": [[chars[j], round(float(v), 5)] for v, j in zip(top.values.tolist(), top.indices.tolist())]})
        return rows
    return {
        "note": "re-run of tinygpt.train with the same corpus, seed 1337 and settings, on Modal CPU (8 threads); the "
                "deck's numbers stay those in experiments/logs/tinygpt.json; this run adds the per-example details",
        "torch": torch.__version__, "seconds": round(secs, 1), "params": sum(p.numel() for p in model.parameters()),
        "chars": chars, "corpus_chars": len(text), "train_chars": n, "val_chars": len(data) - n,
        "curve": rec["curve"], "track_weight": {"tensor": "blocks[0].attn.qkv.weight", "index": list(track), "path": rec["track"]},
        "batch1": {"starts": first["starts"], "windows": [dec(r.tolist()) for r in first["x"]],
                   "targets": [dec(r.tolist()) for r in first["y"]], "pick": pick},
        "probs_before": table(P0), "probs_after": table(P1),
        "full_before": [[round(float(v), 6) for v in r] for r in P0.tolist()],
        "full_after": [[round(float(v), 6) for v in r] for r in P1.tolist()],
        "patch": {"tensor": "blocks[0].attn.qkv.weight[0:8, 0:16]", "before": [[round(float(v), 6) for v in r] for r in patch_before],
                  "grad": [[round(float(v), 6) for v in r] for r in grad], "after": [[round(float(v), 6) for v in r] for r in patch_after],
                  "final": [[round(float(v), 6) for v in r] for r in W[0:8, 0:16].detach()]},
        "step1": rec["step1"],
    }


@app.local_entrypoint()
def main(only: str = ""):
    t = json.loads((L2 / "brain3d" / "trace.json").read_text())
    calls = {}
    if only in ("", "qwen"):
        calls["qwen"] = qwen.spawn(t["meta"]["revision"])
    if only in ("", "tiny"):
        calls["tiny"] = tiny.spawn()
    for k, fc in calls.items():
        res = fc.get()
        dst = HERE / "data" / ("params_data.json" if k == "qwen" else "s8_weights_tiny.json")
        dst.write_text(json.dumps(res, indent=1 if k == "qwen" else None, separators=None if k == "qwen" else (",", ":")))
        print("wrote", dst, round(dst.stat().st_size / 1e3, 1), "kB")
