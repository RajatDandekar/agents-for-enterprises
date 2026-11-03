"""The real bge-small vectors for the rag film's vector plates (CPU on Modal, a minute). Writes data/embed_qrc03.json:
the 384 numbers of Emma's question (with bge's query instruction, as ledgerline/course/l3/rag.py embeds it) and of
QRC-03's first chunk (its embedded text as the RAG Lab shows it), and their cosine similarity.

    MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run embed_modal.py
"""
import json
import os

import modal

HERE = os.path.dirname(os.path.abspath(__file__))
app = modal.App("l3-films-embed")
image = modal.Image.debian_slim(python_version="3.11").pip_install("sentence-transformers==3.3.1", "torch==2.5.1")
Q_PREFIX = "Represent this sentence for searching relevant passages: "   # rag.EMBED_MODELS["bge-small"]["q"]


@app.function(image=image, cpu=4, memory=8192, timeout=900)
def embed(texts: list) -> list:
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    return m.encode(texts, normalize_embeddings=True).tolist()


@app.local_entrypoint()
def main():
    cap = json.load(open(os.path.join(HERE, "data", "rag_capture.json")))
    q = cap["question"]
    c0 = cap["qrc03"]["chunks"][0]
    vq, vc = embed.remote([Q_PREFIX + q, c0["text"]])
    cos = sum(a * b for a, b in zip(vq, vc))
    out = {"model": "BAAI/bge-small-en-v1.5", "normalized": True, "question": q, "query_vector": [round(x, 5) for x in vq],
           "chunk": c0["cid"], "chunk_vector": [round(x, 5) for x in vc], "cosine": round(cos, 4), "dim": len(vq)}
    json.dump(out, open(os.path.join(HERE, "data", "embed_qrc03.json"), "w"))
    print("dim", len(vq), "cosine(question, QRC-03 c0)", round(cos, 4))
