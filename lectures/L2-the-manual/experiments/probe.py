"""Probe: fastembed models + determinism, Gemini countTokens and embedding endpoints. Writes logs/probe.json."""
import json, os, time, pathlib, hashlib
out = {}
import fastembed
out["fastembed"] = fastembed.__version__
from fastembed import TextEmbedding
t = time.time()
m = TextEmbedding("BAAI/bge-small-en-v1.5")
docs = ["Parts that come into contact with food may be bought only from a supplier holding a valid food-grade certificate.",
        "Can we buy gaskets from a supplier without a food-grade certificate?"]
v1 = [list(map(float, x)) for x in m.embed(docs)]
v2 = [list(map(float, x)) for x in m.embed(docs)]
out["embed_load_s"] = round(time.time() - t, 1)
out["dim"] = len(v1[0])
out["deterministic"] = v1 == v2
out["cos"] = sum(a*b for a, b in zip(*v1))
out["supported_rerankers"] = []
try:
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    out["supported_rerankers"] = [d["model"] for d in TextCrossEncoder.list_supported_models()]
    ce = TextCrossEncoder("Xenova/ms-marco-MiniLM-L-6-v2")
    out["ce_scores"] = list(map(float, ce.rerank(docs[1], [docs[0], "Approval limits apply to gross value including GST."])))
except Exception as e:
    out["ce_error"] = repr(e)
import httpx
key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
for model in ["gemini-3.8-flash", "gemini-3.5-flash-lite"]:
    r = httpx.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens", params={"key": key},
                   json={"contents": [{"parts": [{"text": docs[0]}]}]}, timeout=60)
    out[f"count_{model}"] = r.text[:300]
r = httpx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent", params={"key": key},
               json={"content": {"parts": [{"text": docs[0]}]}}, timeout=60)
out["gem_embed"] = r.status_code
pathlib.Path("logs").mkdir(exist_ok=True)
pathlib.Path("logs/probe.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
