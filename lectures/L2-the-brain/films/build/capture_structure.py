"""For the "structure" film: the first 16 numbers of every prompt token's vector entering block 1 and after each of the
24 blocks (the residual stream, the same forward pass as brain3d/trace.json), on Modal CPU. Writes films/build/data/structure_data.json.

    MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/capture_structure.py
"""
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
L2 = HERE.parent.parent
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch==2.4.1", index_url="https://download.pytorch.org/whl/cpu")
         .pip_install("transformers==4.46.3", "numpy<2.1", "accelerate"))
app = modal.App("l2-structure-capture", image=image)
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


@app.function(cpu=4, memory=12288, timeout=1800)
def capture(chat_text: str, revision: str, ids_ref: list) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(MODEL, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=revision, torch_dtype=torch.float32).eval()
    ids = tok(chat_text, add_special_tokens=False).input_ids
    assert ids == ids_ref, "prompt tokens differ from trace.json"
    out = model(torch.tensor([ids]), output_hidden_states=True, use_cache=False)
    hs = out.hidden_states   # 25: the input embeddings, then after each block (the last one already final-normed)
    layers = []
    for l, h in enumerate(hs):
        v = h[0, :, :16]
        layers.append([[round(float(x), 4) for x in row] for row in v.tolist()])
    return {"model": MODEL, "revision": revision, "n_tokens": len(ids), "layers": layers,
            "note": "layers[0] = input embeddings (what enters block 1); layers[k] = the residual stream after block k "
                    "(layers[24] is after the model's final RMSNorm, as transformers returns it); first 16 of 896 numbers per token"}


@app.local_entrypoint()
def main():
    t = json.loads((L2 / "brain3d" / "trace.json").read_text())
    res = capture.remote(t["prompt"]["chat_text"], t["meta"]["revision"], [x["id"] for x in t["tokens"]])
    dst = HERE / "data" / "structure_data.json"
    dst.write_text(json.dumps(res, separators=(",", ":")))
    print("wrote", dst, round(dst.stat().st_size / 1e6, 2), "MB", len(res["layers"]), "layers x", res["n_tokens"], "tokens")
