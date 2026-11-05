"""L3 v5 · parsing section: Docling, run for real on the same files the deck shows.

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/v5_parse_docling.py

Docling (open source, from IBM Research: github.com/docling-project/docling) is installed from PyPI into a Modal CPU image,
its models are downloaded when the image is built (so no run below pays for a download), and its default PDF pipeline
converts three files from the dump:
  * D, 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf (4 pages, the running example),
  * 01_policies/POL-APR-002 Approval Matrix v3.0.pdf (the table PDF of the slide "A Table in a PDF"),
  * 99_scans/2026_signed_approval_PO-2026-00452.pdf (the scan of "A Scan Is a Picture": a page with no text layer).
Each file is converted twice with one converter: the first call also loads the models (cold), the second is the time a
running service would see (warm). The exact three lines a student would write are what runs:

    from docling.document_converter import DocumentConverter
    result = DocumentConverter().convert(path)
    markdown = result.document.export_to_markdown()

Writes logs/v5_parse_docling.json: versions, machine, the pipeline options, timings, the Markdown (whole file and per page),
every table, and the count of each element label Docling assigned (section_header, page_header, page_footer, text, ...).
No LLM calls, no keys.
"""
from __future__ import annotations

import json
import os
import pathlib
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
FILES = {
    "pur": "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf",
    "apr": "01_policies/POL-APR-002 Approval Matrix v3.0.pdf",
    "scan": "99_scans/2026_signed_approval_PO-2026-00452.pdf",
}
CPU = 4

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install("torch", "torchvision", index_url="https://download.pytorch.org/whl/cpu")
    .pip_install("docling")
    .run_commands("docling-tools models download")
)
for _k, _rel in FILES.items():
    image = image.add_local_file(DUMP / _rel, f"/dump/{_k}.pdf")
app = modal.App("l3-v5-parse-docling", image=image)


def _ver(md, p):
    try:
        return md.version(p)
    except md.PackageNotFoundError:
        return None


@app.function(cpu=CPU, memory=8192, timeout=2400)
def run() -> dict:
    import collections
    import importlib.metadata as md
    import platform

    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter

    out = {"versions": {p: md.version(p) for p in ("docling", "docling-core", "docling-ibm-models", "torch")},
           "machine": f"Modal CPU container, {CPU} vCPU, 8 GB, no GPU", "python": platform.python_version(),
           "ocr_packages": {p: _ver(md, p) for p in ("easyocr", "rapidocr", "rapidocr-onnxruntime", "onnxruntime", "tesserocr")},
           "files": {}}
    t0 = time.time()
    conv = DocumentConverter()
    out["converter_init_secs"] = round(time.time() - t0, 2)
    for key, rel in FILES.items():
        path = f"/dump/{key}.pdf"
        rec = {"file": rel}
        t0 = time.time()
        res = conv.convert(path)
        rec["cold_secs"] = round(time.time() - t0, 2)
        t0 = time.time()
        res = conv.convert(path)
        rec["warm_secs"] = round(time.time() - t0, 2)
        doc = res.document
        rec["status"] = str(res.status)
        rec["n_pages"] = len(doc.pages)
        rec["markdown"] = doc.export_to_markdown()
        rec["pages_md"] = {}
        for p in sorted(doc.pages):
            try:
                rec["pages_md"][str(p)] = doc.export_to_markdown(page_no=p)
            except TypeError as e:  # older docling-core without page_no
                rec["pages_md_error"] = str(e)[:200]
                break
        rec["labels"] = dict(collections.Counter(str(getattr(t.label, "value", t.label)) for t in doc.texts))
        rec["page_furniture"] = [{"label": str(getattr(t.label, "value", t.label)), "text": t.text,
                                  "page": t.prov[0].page_no if t.prov else None}
                                 for t in doc.texts if str(getattr(t.label, "value", t.label)) in ("page_header", "page_footer")]
        rec["section_headers"] = [t.text for t in doc.texts if str(getattr(t.label, "value", t.label)) in ("section_header", "title")]
        rec["tables"] = []
        for t in doc.tables:
            try:
                tmd = t.export_to_markdown(doc=doc)
            except TypeError:
                tmd = t.export_to_markdown()
            rec["tables"].append({"page": t.prov[0].page_no if t.prov else None, "rows": t.data.num_rows,
                                  "cols": t.data.num_cols, "markdown": tmd})
        try:
            po = conv.format_to_options[InputFormat.PDF].pipeline_options
            rec["pipeline_options"] = json.loads(po.model_dump_json())
            rec["ocr_engine"] = {"options_class": type(po.ocr_options).__name__, "kind": getattr(po.ocr_options, "kind", None)}
            ocr_model = next((m for m in getattr(conv._get_pipeline(InputFormat.PDF), "build_pipe", []) if "Ocr" in type(m).__name__), None)
            rec["ocr_engine"]["model_class"] = type(ocr_model).__name__ if ocr_model is not None else None
            inner = getattr(ocr_model, "_engine", None) or getattr(ocr_model, "engine", None)
            rec["ocr_engine"]["inner"] = type(inner).__name__ if inner is not None else None
        except Exception as e:  # noqa: BLE001
            rec["pipeline_options_error"] = str(e)[:200]
        rec["timings_note"] = "cold = first convert of this file with this converter (the first file also loads the models); warm = the same file again"
        out["files"][key] = rec
    return out


@app.local_entrypoint()
def main():
    out = run.remote()
    out["generated"] = time.strftime("%Y-%m-%d %H:%M")
    out["script"] = "experiments/v5_parse_docling.py"
    LOGS.mkdir(exist_ok=True)
    (LOGS / "v5_parse_docling.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps(out["versions"]), out["machine"], out["ocr_packages"], "init", out["converter_init_secs"], "s")
    for k, r in out["files"].items():
        print(r.get("ocr_engine"), r.get("pipeline_options_error"))
        print(f"=== {k} {r['file']} pages {r['n_pages']} cold {r['cold_secs']} s warm {r['warm_secs']} s labels {r['labels']} tables {len(r['tables'])}")
        print(r["markdown"][:2500])
