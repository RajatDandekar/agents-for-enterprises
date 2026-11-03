"""Real text for the Lecture 3 deck's parsing and chunking slides, and the race's retrieved passages, read on Modal.

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/deck_extract_modal.py

No LLM calls. With the dump mounted it:
  * parses a few files with both parsers (corpus.parse_file): a policy PDF, a quick-reference PDF, the supplier master,
    the Brightcell e-mail, a scan; so the deck shows what each parser really hands the chunker;
  * chunks QRC-03 and the Purchase Policy three ways (fixed, recursive, structure-aware) at 200 tokens;
  * looks up, in the best index on the RAG Lab volume, the full text of the passages the race's RAG run retrieved for
    Q-EMMA and Q-0412 (race_answers/rag__250n.json lists their chunk ids).
Writes logs/deck_extract.json.
"""
import json
import os
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app", "pages", "restricted"}

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("tesseract-ocr")
    .pip_install("pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl==3.1.5", "python-docx==1.1.2", "pyyaml==6.0.2",
                 "tiktoken==0.8.0", "pytesseract==0.3.13", "pillow==11.0.0", "numpy<2.1", "scipy", "httpx", "pydantic>=2")
    .run_commands("python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
    .env({"PYTHONPATH": "/course/ledgerline", "NORTHBRIDGE_DOCS": "/dump", "NB_L3_CACHE": "/tmp/l3cache"})
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
    .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts)
    .add_local_file(HERE / "logs" / "race_answers" / "rag__250n.json", "/race/rag__250n.json")
)
app = modal.App("l3-deck-extract", image=image)
rvol = modal.Volume.from_name("northbridge-raglab")

FILES = {
    "policy": "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf",
    "qrc": "11_training/QRC-03 ERR-PO-0412 quick fix.pdf",
    "supplier_master": "05_master_data/SUPPLIER_MASTER.xlsx",
    "email": "09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml",
    "scan": "99_scans/2019_Voltway_code_change_approval_signed.pdf",
}


def _cut(s, n=900):
    return s if len(s) <= n else s[: n - 1] + "…"


@app.function(timeout=1200, cpu=2, memory=4096, volumes={"/rvol": rvol})
def extract() -> dict:
    import gzip

    from ledgerline.course.l3 import corpus as C

    root = pathlib.Path("/dump")
    out = {"what": __doc__.strip().splitlines()[0], "parsers": {}, "chunks": {}, "race_items": {}}
    for k, rel in FILES.items():
        row = {"file": rel}
        for p in ("plain", "structured"):
            us = C.parse_file(root, rel, parser=p)
            row[p] = {"n_units": len(us), "tokens": sum(C.n_tokens(u.text) for u in us),
                      "units": [{"loc": u.loc, "kind": u.kind, "heading": u.heading, "text": _cut(u.text),
                                 "tokens": C.n_tokens(u.text)} for u in us[:4]]}
        out["parsers"][k] = row
    for k in ("qrc", "policy"):
        us = C.parse_file(root, FILES[k], parser="structured")
        out["chunks"][k] = {}
        for m in ("fixed", "recursive", "structure"):
            ch = C.chunk(us, m, 200, 0.0)
            out["chunks"][k][m] = {"n": len(ch), "chunks": [{"cite": c.cite, "tokens": c.n_tokens, "body": _cut(c.body, 1400),
                                                              "header": c.text[: max(0, len(c.text) - len(c.body))].strip()}
                                                             for c in ch[:8]]}
    # the passages RAG retrieved in the race, from the best index's chunk file
    rec = {r["id"]: r for r in json.load(open("/race/rag__250n.json"))["records"]}
    want = {q: [it["id"] for it in rec[q]["items"]] for q in ("Q-EMMA", "Q-0412")}
    ids = {i for v in want.values() for i in v}
    found = {}
    path = pathlib.Path("/rvol/chroma/structured-structure-200-o15/chunks.jsonl.gz")
    with gzip.open(path, "rt") as f:
        for line in f:
            d = json.loads(line)
            cid = d.get("cid") or d.get("id")
            if cid in ids:
                found[cid] = d
    for q, lst in want.items():
        out["race_items"][q] = [{"rank": i + 1, "id": cid, "cite": (found.get(cid) or {}).get("cite") or rec[q]["items"][i].get("cite"),
                                 "body": _cut((found.get(cid) or {}).get("body") or (found.get(cid) or {}).get("text") or "", 700)}
                                for i, cid in enumerate(lst)]
    out["race_items_found"] = f"{len(found)} of {len(ids)}"
    return out


@app.local_entrypoint()
def main():
    d = extract.remote()
    (HERE / "logs" / "deck_extract.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
    print("parsers:", {k: (v["plain"]["n_units"], v["structured"]["n_units"]) for k, v in d["parsers"].items()})
    print("chunks:", {k: {m: x["n"] for m, x in v.items()} for k, v in d["chunks"].items()})
    print("race items:", d["race_items_found"])
