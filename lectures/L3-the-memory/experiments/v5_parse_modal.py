"""L3 v5 · the parsing section: real files from the dump, rendered, parsed both ways, OCR'd, read by a vision model.

    M=/Users/raj/.venv/bin/modal; E=lectures/L3-the-memory/experiments/v5_parse_modal.py
    MODAL_PROFILE=rajatworkspace $M run $E::explore      # both parsers on the candidate files -> logs/v5_parse_explore.json
    MODAL_PROFILE=rajatworkspace $M run $E::render       # page images + highlight boxes      -> v5/img/parse/*.jpg, logs/v5_parse_render.json
    MODAL_PROFILE=rajatworkspace $M run $E::ocr          # Tesseract vs gemini-3.8-flash on the scans -> logs/v5_parse_ocr.json
    MODAL_PROFILE=rajatworkspace $M run $E::deck         # the deck's data: every slide's real text -> logs/v5_parse.json

Everything runs on Modal (CPU only). Parsing uses the course's own code, ledgerline/course/l3/corpus.py
(parse_file with parser="plain" and parser="structured", file_meta), so the deck shows exactly what NB3 and the RAG Lab
index. Rendering: PyMuPDF for PDFs; LibreOffice headless (DOCX, XLSX, HTML -> PDF) and then PyMuPDF. Highlight boxes
come from PyMuPDF's text search on the rendered PDF (for scans: Tesseract's word boxes), stored as fractions of the image.
The Gemini key is read from wm-lecture6-ijepa/.env, passed as a Modal secret and sent in a header; it is never printed.
"""
from __future__ import annotations

import json
import os
import pathlib
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
LOGS = HERE / "logs"
IMG = HERE.parent / "v5" / "img" / "parse"
GEMINI_ENV = "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env"
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app", "pages", "restricted"}


def _key(name="GEMINI_API_KEY"):
    if not modal.is_local() or not os.path.exists(GEMINI_ENV):
        return ""
    for line in open(GEMINI_ENV):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("tesseract-ocr", "libreoffice-writer", "libreoffice-calc", "fonts-dejavu", "fonts-liberation",
                 "fonts-crosextra-carlito", "fonts-crosextra-caladea")
    .pip_install("pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl==3.1.5", "python-docx==1.1.2", "pyyaml==6.0.2",
                 "tiktoken==0.8.0", "pytesseract==0.3.13", "pillow==11.0.0", "pymupdf==1.24.14", "httpx")
    .run_commands("python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
    .env({"PYTHONPATH": "/course/ledgerline", "NORTHBRIDGE_DOCS": "/dump", "NB_L3_CACHE": "/tmp/l3cache"})
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
    .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts)
)
app = modal.App("l3-v5-parse", image=image)
secret = modal.Secret.from_dict({"GEMINI_API_KEY": _key()})

CANDIDATES = [
    "01_policies/POL-APR-002 Approval Matrix v3.0.pdf",
    "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf",
    "99_scans/1998_Ledgerline_licence_signature_page.pdf",
    "99_scans/2004_LL6_manual_page_37_scan.pdf",
    "99_scans/2011_VAT_rate_change_memo.pdf",
    "99_scans/2019_Voltway_code_change_approval_signed.pdf",
    "99_scans/2023_stock_count_sheet_MAN_aisle_B.pdf",
    "99_scans/2026_signed_approval_PO-2026-00452.pdf",
    "05_master_data/ITEM_MASTER_2026-10-26.xlsx",
    "05_master_data/SUPPLIER_MASTER.xlsx",
    "09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml",
    "09_email_archive/2026/2026-05-14_Voltway freight.eml",
    "02_procedures/sop_inv_001_goods_receipt_v2.docx",
    "01_policies/old/Approval_Matrix_v2.0_2024.docx",
    "02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx",
    "11_training/intranet_export_2016/approval_limits.html",
    "01_policies/POL-TEX-007 Travel and Expenses Policy v2.4.pdf",
    "01_policies/POL-TEX-007 Travel and Expenses Policy v3.0 (effective 2027-01-01).pdf",
    "01_policies/HR/CONFIDENTIAL/HR-CONF-007 Salary Bands 2026-27.pdf",
    "01_policies/old/Purchase Policy v4.0.docx",
]


def _units(us, cut=None):
    return [{"loc": u.loc, "kind": u.kind, "heading": u.heading, "text": u.text if not cut else u.text[:cut]} for u in us]


@app.function(timeout=1800, cpu=4, memory=8192)
def explore_remote() -> dict:
    from pypdf import PdfReader

    from ledgerline.course.l3 import corpus as C

    root = pathlib.Path("/dump")
    out = {}
    for rel in CANDIDATES:
        row = {"file": rel}
        for p in ("plain", "structured"):
            t0 = time.time()
            us = C.parse_file(root, rel, parser=p)
            row[p] = {"n_units": len(us), "tokens": sum(C.n_tokens(u.text) for u in us), "secs": round(time.time() - t0, 3),
                      "meta": us[0].meta if us else None, "units": _units(us[:60], 6000)}
        if rel.endswith(".pdf"):
            r = PdfReader(str(root / rel))
            row["pages"] = len(r.pages)
            row["images_per_page"] = [len(pg.images) for pg in r.pages]
        out[rel] = row
    return out


@app.local_entrypoint()
def explore():
    out = explore_remote.remote()
    LOGS.mkdir(exist_ok=True)
    (LOGS / "v5_parse_explore.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for rel, r in out.items():
        print(f"{rel[:70]:<70} plain {r['plain']['n_units']:>4}u {r['plain']['tokens']:>6}t | structured {r['structured']['n_units']:>4}u {r['structured']['tokens']:>6}t")


# =============================================================================== rendering helpers
def _to_pdf(src: pathlib.Path, work: pathlib.Path, xlsx_rows: int = 0, xlsx_cols: str = "") -> pathlib.Path:
    """A PDF of any file: PDFs as they are; DOCX/HTML through LibreOffice; XLSX through LibreOffice after setting each
    sheet's print area (top rows, fit to one page wide) so the rendered sheet is legible."""
    import shutil
    import subprocess

    if src.suffix.lower() == ".pdf":
        return src
    work.mkdir(parents=True, exist_ok=True)
    tmp = work / src.name
    shutil.copy(src, tmp)
    if src.suffix.lower() == ".xlsx" and xlsx_rows:
        from openpyxl import load_workbook
        from openpyxl.utils import get_column_letter

        wb = load_workbook(tmp)
        for ws in wb.worksheets:
            last = xlsx_cols or get_column_letter(ws.max_column)
            ws.print_area = f"A1:{last}{min(ws.max_row, xlsx_rows)}"
            ws.page_setup.orientation = "landscape"
            ws.sheet_properties.pageSetUpPr.fitToPage = True
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 0
            ws.print_options.gridLines = True
            ws.print_options.headings = True   # column letters and row numbers, as on screen
        wb.save(tmp)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(work), str(tmp)],
                   check=True, capture_output=True, timeout=240)
    return work / (tmp.stem + ".pdf")


@app.function(timeout=1800, cpu=4, memory=8192)
def pages_remote(files: list[str], zoom: float = 1.4) -> dict:
    import fitz

    root = pathlib.Path("/dump")
    out = {}
    for rel in files:
        pdf = _to_pdf(root / rel, pathlib.Path("/tmp/work") / str(abs(hash(rel))), xlsx_rows=30)
        doc = fitz.open(pdf)
        pg_out = []
        for i, page in enumerate(doc):
            if i >= 6:
                break
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            blocks = [[round(b[0]), round(b[1]), round(b[2]), round(b[3]), b[4][:90]] for b in page.get_text("blocks")]
            pg_out.append({"w": page.rect.width, "h": page.rect.height, "jpg": pix.tobytes("jpeg", jpg_quality=80), "blocks": blocks})
        out[rel] = pg_out
    return out


@app.local_entrypoint()
def pages(files: str = ""):
    """Contact sheet for choosing crops: every page (up to 6) of the candidate files, to the scratchpad."""
    want = [f for f in files.split("|") if f] or CANDIDATES
    res = pages_remote.remote(want)
    dst = pathlib.Path(os.environ.get("PARSE_SCRATCH", "/tmp/v5_parse_pages"))
    dst.mkdir(parents=True, exist_ok=True)
    meta = {}
    for rel, pgs in res.items():
        stem = pathlib.Path(rel).stem.replace(" ", "_")[:48]
        for i, p in enumerate(pgs, 1):
            (dst / f"{stem}_p{i}.jpg").write_bytes(p.pop("jpg"))
        meta[rel] = pgs
    (dst / "blocks.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    print("wrote", dst)


# =============================================================================== OCR: Tesseract (what corpus.py does) vs a vision model
SCANS = [f"99_scans/{n}" for n in ("1998_Ledgerline_licence_signature_page.pdf", "2004_LL6_manual_page_37_scan.pdf",
                                    "2011_VAT_rate_change_memo.pdf", "2019_Voltway_code_change_approval_signed.pdf",
                                    "2023_stock_count_sheet_MAN_aisle_B.pdf", "2026_signed_approval_PO-2026-00452.pdf")]
VISION_MODEL = "gemini-3.8-flash"
VISION_PROMPT = ("Transcribe every piece of text on this scanned page exactly as it is written, line by line, keeping the "
                 "line breaks. Do not correct or complete anything. Write tables as rows with cells separated by ' | '. "
                 "For marks that are not printed text, write a short description in square brackets, for example "
                 "[signature] or [stamp: ...]. Output only the transcription.")


def _degrade(im):
    """Our own stress test (labelled as such in the deck): the page as a poor office scan would give it:
    rotated 1.5 degrees, downsampled to about 100 dpi, blurred, speckled, saved as a low-quality JPEG."""
    import io
    import random

    from PIL import Image, ImageFilter

    g = im.convert("L")
    w, h = g.size
    g = g.rotate(1.5, resample=Image.BICUBIC, expand=False, fillcolor=235)
    g = g.resize((int(w * 0.5), int(h * 0.5)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.9))
    px = g.load()
    rnd = random.Random(7)
    for _ in range(int(g.size[0] * g.size[1] * 0.004)):
        x, y = rnd.randrange(g.size[0]), rnd.randrange(g.size[1])
        px[x, y] = rnd.choice((40, 90, 200))
    buf = io.BytesIO()
    g.save(buf, "JPEG", quality=30)
    return Image.open(io.BytesIO(buf.getvalue()))


def _gemini(png: bytes, key: str) -> dict:
    import base64

    import httpx

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{VISION_MODEL}:generateContent"
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(png).decode()}},
                                    {"text": VISION_PROMPT}]}],
            "generationConfig": {"temperature": 0}}
    t0 = time.time()
    r = httpx.post(url, json=body, headers={"x-goog-api-key": key}, timeout=180)
    secs = time.time() - t0
    j = r.json()
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}: {json.dumps(j)[:300]}", "secs": round(secs, 2)}
    parts = j["candidates"][0]["content"].get("parts", [])
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    u = j.get("usageMetadata", {})
    return {"text": text.strip(), "secs": round(secs, 2), "usage": u, "model_version": j.get("modelVersion")}


@app.function(timeout=1800, cpu=4, memory=8192, secrets=[secret])
def ocr_remote() -> dict:
    import io

    import fitz
    import httpx
    import pytesseract
    from pypdf import PdfReader

    from ledgerline.course.l3 import corpus as C

    key = os.environ["GEMINI_API_KEY"]
    price = {}
    try:
        models = httpx.get("https://openrouter.ai/api/v1/models", timeout=60).json()["data"]
        m = next(m for m in models if m["id"] == f"google/{VISION_MODEL}")
        price = {"source": "OpenRouter models list (list price of google/" + VISION_MODEL + "), fetched " + time.strftime("%Y-%m-%d"),
                 "prompt_usd_per_m": float(m["pricing"]["prompt"]) * 1e6, "completion_usd_per_m": float(m["pricing"]["completion"]) * 1e6,
                 "image_usd": float(m["pricing"].get("image", 0) or 0)}
    except Exception as e:  # noqa: BLE001
        price = {"error": str(e)[:200]}
    root = pathlib.Path("/dump")
    out = {"model": VISION_MODEL, "prompt": VISION_PROMPT, "price": price, "tesseract": pytesseract.get_tesseract_version().public,
           "machine": "Modal CPU container, 4 vCPU", "pages": {}}

    def cost(u):
        if not price.get("prompt_usd_per_m"):
            return None
        outtok = (u.get("candidatesTokenCount") or 0) + (u.get("thoughtsTokenCount") or 0)
        return round((u.get("promptTokenCount") or 0) * price["prompt_usd_per_m"] / 1e6 + outtok * price["completion_usd_per_m"] / 1e6, 6)

    for rel in SCANS:
        rec = {"file": rel}
        pg = PdfReader(str(root / rel)).pages[0]
        im = pg.images[0].image                      # exactly the image corpus._ocr_pages hands Tesseract
        rec["embedded_image"] = {"w": im.size[0], "h": im.size[1], "mode": im.mode}
        rec["plain_text"] = C.parse_file(root, rel, "plain")[0].text
        t0 = time.time()
        rec["structured_text"] = C.parse_file(root, rel, "structured")[0].text
        rec["structured_secs"] = round(time.time() - t0, 3)
        variants = {"original": im, "degraded": _degrade(im)}
        for vname, vim in variants.items():
            v = {}
            t0 = time.time()
            v["tesseract_text"] = pytesseract.image_to_string(vim).strip()
            v["tesseract_secs"] = round(time.time() - t0, 3)
            d = pytesseract.image_to_data(vim, output_type=pytesseract.Output.DICT)
            v["tesseract_words"] = [{"t": d["text"][i], "conf": float(d["conf"][i]), "x": d["left"][i] / vim.size[0],
                                     "y": d["top"][i] / vim.size[1], "w": d["width"][i] / vim.size[0], "h": d["height"][i] / vim.size[1]}
                                    for i in range(len(d["text"])) if d["text"][i].strip()]
            buf = io.BytesIO()
            vim.convert("RGB").save(buf, "PNG")
            png = buf.getvalue()
            v["image_png_bytes"] = len(png)
            g = _gemini(png, key)
            g["usd"] = cost(g.get("usage", {})) if "usage" in g else None
            v["vision"] = g
            jb = io.BytesIO()
            vim.convert("RGB").save(jb, "JPEG", quality=88)
            v["jpg"] = jb.getvalue()
            rec[vname] = v
        out["pages"][rel] = rec
    return out


@app.local_entrypoint()
def ocr():
    out = ocr_remote.remote()
    IMG.mkdir(parents=True, exist_ok=True)
    for rel, rec in out["pages"].items():
        stem = pathlib.Path(rel).stem
        for vname in ("original", "degraded"):
            jpg = rec[vname].pop("jpg")
            # the deck's scan images come from ::render (same _degrade, same seed); this jpg is not kept
            rec[vname]["jpg_bytes"] = len(jpg)
    out["generated"] = time.strftime("%Y-%m-%d %H:%M")
    out["script"] = "experiments/v5_parse_modal.py::ocr"
    (LOGS / "v5_parse_ocr.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for rel, rec in out["pages"].items():
        for vname in ("original", "degraded"):
            v = rec[vname]
            print(f"--- {rel} [{vname}] tesseract {v['tesseract_secs']}s | vision {v['vision'].get('secs')}s ${v['vision'].get('usd')} {v['vision'].get('error', '')}")
            print("T:", v["tesseract_text"][:400].replace("\n", " / "))
            print("V:", (v["vision"].get("text") or "")[:400].replace("\n", " / "))


# =============================================================================== deck images with highlight boxes
# Each image: a file, a page, a zoom and an optional clip given by two anchor texts; each box: a text to find (and
# optionally a second text to extend it to), found with PyMuPDF's search on the rendered PDF. Boxes are fractions
# of the image, so the deck can place them at any size. k = the click on which the box appears.
RENDER = {
    "apr": {"file": "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "images": {
        "crop": {"page": 1, "zoom": 3.2, "clip": {"from": "3. The limits", "to": "no approval authority", "x": [56, 542], "pad": [8, 10]},
                 "boxes": [{"s": "Role code", "to": "Limit (gross incl. VAT)", "x": [62, 532], "k": 2, "cls": "g"},
                           {"s": "PUR-EXEC", "to": "£250,000", "x": [62, 532], "k": 2, "cls": "a"}]}}},
    "pur": {"file": "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf", "images": {
        "page": {"page": 2, "zoom": 2.0, "boxes": [
            {"s": "Northbridge Cycles Ltd", "to": "POL-PUR-001 | v4.1", "x": [50, 546], "k": 1, "cls": "b"},
            {"s": "Internal. Uncontrolled when printed.", "to": "Page 2 of 4", "x": [50, 546], "k": 1, "cls": "b"},
            {"s": "5. Approval limits", "k": 2, "cls": "a"}, {"s": "6. Supplier qualification", "k": 2, "cls": "a"},
            {"s": "7. Prices", "k": 2, "cls": "a"}, {"s": "8. Tax", "k": 2, "cls": "a"}, {"s": "9. Records", "k": 2, "cls": "a"},
            {"s": "Appendix A. Definitions", "k": 2, "cls": "a"},
            {"s": "6. Supplier qualification", "to": "by itself justify a change of supplier for a lithium-cell part.", "x": [50, 546], "k": 3, "cls": "g"}]},
        "crop6": {"page": 2, "zoom": 3.0, "clip": {"from": "6. Supplier qualification", "to": "by itself justify a change of supplier for a lithium-cell part.", "x": [48, 550], "pad": [8, 8]},
                  "boxes": [{"s": "6.2 Lithium-cell parts", "to": "certificate counts as no certificate.", "x": [52, 546], "k": 3, "cls": "g"},
                            {"s": "6.4 Prefer the supplier", "to": "by itself justify a change of supplier for a lithium-cell part.", "x": [52, 546], "k": 3, "cls": "g"}]}}},
    "item": {"file": "05_master_data/ITEM_MASTER_2026-10-26.xlsx", "xlsx_rows": 11, "xlsx_cols": "J", "images": {
        "crop": {"page": 1, "zoom": 4.0, "clip": "content", "boxes": [
            {"s": "itm_cd", "to": "lead_days", "row": True, "k": 2, "cls": "g"},
            {"s": "BAT-500", "n": 0, "to": "42", "row": True, "k": 1, "cls": "a"},
            {"s": "reorder_lvl", "k": 3, "cls": "x"}, {"s": "3000", "n": 0, "k": 3, "cls": "x"}]}}},
    "apr2": {"file": "01_policies/old/Approval_Matrix_v2.0_2024.docx", "images": {
        "page": {"page": 1, "zoom": 2.4, "clip": {"from": "Northbridge Cycles Ltd", "to": "4.1 Nobody may approve", "x": [40, 560], "pad": [14, 10]},
                 "boxes": [{"s": "Document", "to": "SUPERSEDED", "x": [82, 519], "k": 1, "cls": "b"},
                           {"s": "Role code", "to": "£5,000,000", "x": [82, 519], "k": 1, "cls": "b"},
                           {"s": "PUR-EXEC", "to": "£200,000", "x": [82, 519], "k": 3, "cls": "a"},
                           {"s": "Status", "to": "SUPERSEDED", "x": [82, 519], "k": 3, "cls": "g"}]}}},
}


def _find(page, s, n=None):
    import fitz

    hits = page.search_for(s)
    if not hits:
        raise ValueError(f"not found on page: {s!r}")
    if n is not None:
        return hits[n]
    return hits[0]


def _box(page, b, clip):
    import fitz

    r = fitz.Rect(_find(page, b["s"], b.get("n")))
    if b.get("to"):
        r2 = page.search_for(b["to"])
        r2 = [x for x in r2 if x.y1 >= r.y0 - 1] or r2
        r |= r2[0]
    if b.get("row"):
        r = fitz.Rect(clip.x0 + 4, r.y0, clip.x1 - 4, r.y1)
    if b.get("x"):
        r = fitz.Rect(b["x"][0], r.y0, b["x"][1], r.y1)
    return {"x": round((r.x0 - clip.x0) / clip.width, 4), "y": round((r.y0 - clip.y0) / clip.height, 4),
            "w": round(r.width / clip.width, 4), "h": round(r.height / clip.height, 4),
            **{k: v for k, v in b.items() if k in ("k", "cls", "label", "below")}}


@app.function(timeout=1800, cpu=4, memory=8192)
def render_remote() -> dict:
    import io

    import fitz

    root = pathlib.Path("/dump")
    out = {}
    for key, spec in RENDER.items():
        pdf = _to_pdf(root / spec["file"], pathlib.Path("/tmp/r") / key, xlsx_rows=spec.get("xlsx_rows", 0), xlsx_cols=spec.get("xlsx_cols", ""))
        doc = fitz.open(pdf)
        out[key] = {"file": spec["file"], "rendered_from": "PDF as it is" if pdf == root / spec["file"] else "LibreOffice headless -> PDF", "images": {}}
        for name, im in spec["images"].items():
            page = doc[im["page"] - 1]
            clip = page.rect
            c = im.get("clip")
            if c == "content":
                bb = None
                for b in page.get_text("blocks"):
                    bb = fitz.Rect(b[:4]) if bb is None else bb | fitz.Rect(b[:4])
                for d in page.get_drawings():
                    bb = bb | d["rect"] if bb is not None else d["rect"]
                clip = fitz.Rect(bb.x0 - 6, bb.y0 - 6, bb.x1 + 6, bb.y1 + 6) & page.rect
            elif c:
                a = _find(page, c["from"])
                z = [x for x in page.search_for(c["to"]) if x.y0 >= a.y0 - 1][0]
                clip = fitz.Rect(c["x"][0], a.y0 - c["pad"][0], c["x"][1], z.y1 + c["pad"][1])
            pix = page.get_pixmap(matrix=fitz.Matrix(im["zoom"], im["zoom"]), clip=clip)
            boxes = [_box(page, b, clip) for b in im.get("boxes", [])]
            out[key]["images"][name] = {"page": im["page"], "zoom": im["zoom"], "clip_pt": [round(v, 1) for v in clip],
                                        "w": pix.width, "h": pix.height, "boxes": boxes, "jpg": pix.tobytes("jpeg", jpg_quality=86)}
    # the scans: the embedded page image itself (what Tesseract and the vision model were given), top part only
    from pypdf import PdfReader

    for key, (rel, frac) in SCAN_CROPS.items():
        im = PdfReader(str(root / rel)).pages[0].images[0].image
        out[key] = {"file": rel, "rendered_from": "the page's embedded scan image (pypdf)", "images": {}}
        for vname, vim in (("orig", im), ("degraded", _degrade(im))):
            W, H = vim.size
            c = vim.convert("RGB").crop((int(frac[0] * W), int(frac[1] * H), int(frac[2] * W), int(frac[3] * H)))
            buf = io.BytesIO()
            c.save(buf, "JPEG", quality=88)
            out[key]["images"][vname] = {"crop_frac": frac, "w": c.size[0], "h": c.size[1], "full_wh": [W, H], "boxes": [], "jpg": buf.getvalue()}
        th = im.convert("RGB")
        th.thumbnail((620, 900))
        buf = io.BytesIO()
        th.save(buf, "JPEG", quality=85)
        out[key]["images"]["thumb"] = {"w": th.size[0], "h": th.size[1], "boxes": [{"x": frac[0], "y": frac[1], "w": frac[2] - frac[0], "h": frac[3] - frac[1], "k": 0, "cls": "dim"}], "jpg": buf.getvalue()}
    return out


SCAN_CROPS = {"scan": ("99_scans/2026_signed_approval_PO-2026-00452.pdf", [0.06, 0.05, 0.72, 0.28])}

web_image = (modal.Image.debian_slim(python_version="3.11").pip_install("playwright==1.47.0")
             .run_commands("playwright install --with-deps chromium")
             .add_local_dir(DUMP / "11_training" / "intranet_export_2016", "/web"))


@app.function(image=web_image, timeout=600)
def render_html_remote(page: str = "approval_limits.html") -> dict:
    """The 2016 intranet page as a browser shows it (Chromium, the export as saved: its stylesheet and logo were not exported)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 900, "height": 700}, device_scale_factor=2)
        pg.goto(f"file:///web/{page}")
        pg.wait_for_timeout(500)
        boxes = pg.evaluate("""() => {
          const W = document.documentElement.scrollWidth, H = Math.min(document.documentElement.scrollHeight, 700);
          const r = (el) => { const b = el.getBoundingClientRect(); return {x: b.left / W, y: b.top / H, w: b.width / W, h: b.height / H}; };
          const cell = [...document.querySelectorAll('td')].find((t) => t.textContent.trim() === '£150,000');
          return {W, H, banner: r(document.getElementById('banner')), nav: r(document.getElementById('nav')),
                  table: r(document.querySelector('table')), row: r(cell.parentElement),
                  net: r([...document.querySelectorAll('p')].find((p) => p.textContent.startsWith('Limits are on the net value')))}; }""")
        png = pg.screenshot(clip={"x": 0, "y": 0, "width": boxes["W"], "height": boxes["H"]}, type="jpeg", quality=88)
        b.close()
    return {"boxes": boxes, "jpg": png}


@app.local_entrypoint()
def render():
    out = render_remote.remote()
    h = render_html_remote.remote()
    B = h["boxes"]
    out["intra"] = {"file": "11_training/intranet_export_2016/approval_limits.html", "rendered_from": "Chromium (Playwright), the file as exported",
                    "images": {"page": {"w": int(B["W"] * 2), "h": int(B["H"] * 2), "jpg": h["jpg"], "boxes": [
                        {**B["banner"], "k": 1, "cls": "b"}, {**B["nav"], "k": 1, "cls": "b"},
                        {**B["table"], "k": 2, "cls": "a"}, {**B["row"], "k": 3, "cls": "g"}, {**B["net"], "k": 3, "cls": "g"}]}}}
    IMG.mkdir(parents=True, exist_ok=True)
    for key, r in out.items():
        for name, im in r["images"].items():
            fn = f"{key}_{name}.jpg"
            (IMG / fn).write_bytes(im.pop("jpg"))
            im["src"] = f"img/parse/{fn}"
            print(key, name, im["w"], "x", im["h"], len(im["boxes"]), "boxes")
    prev = json.loads((LOGS / "v5_parse_render.json").read_text()) if (LOGS / "v5_parse_render.json").exists() else {}
    prev.update(out)
    prev["_generated"] = time.strftime("%Y-%m-%d %H:%M")
    (LOGS / "v5_parse_render.json").write_text(json.dumps(prev, indent=1, ensure_ascii=False))


# =============================================================================== the deck's checks, with the course code
SLIDE_FACTS = {"apr": "F-APR-EXEC", "pur": "F-PUR-6.2", "scan": "F-SCAN-452", "item": "F-ITM-BAT500",
               "email": "F-EM-BRIGHT-PRICE", "apr2": "F-APR20-EXEC", "intra": "F-INTRA-LIMITS"}
META_FILES = ["01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/old/Approval_Matrix_v2.0_2024.docx",
              "11_training/intranet_export_2016/approval_limits.html",
              "01_policies/POL-TEX-007 Travel and Expenses Policy v3.0 (effective 2027-01-01).pdf",
              "01_policies/HR/CONFIDENTIAL/HR-CONF-007 Salary Bands 2026-27.pdf"]


@app.function(timeout=1200, cpu=4, memory=8192)
def deck_remote(ocr_texts: dict) -> dict:
    from ledgerline.course.l3 import corpus as C, evaluate as E

    root = pathlib.Path("/dump")
    F = C.facts(root)
    out = {"facts": {}, "meta": {}, "chunk6": None, "rows": {}}
    for key, fid in SLIDE_FACTS.items():
        f = F[fid]
        row = {"fact": fid, "statement": f["statement"], "needles": f["needles"], "file": f["file"]}
        for p in ("plain", "structured"):
            us = C.parse_file(root, f["file"], p)
            row[p] = E.contains_fact("\n".join(u.text for u in us), f)
        if key == "scan":
            for name, t in ocr_texts.items():
                if "|" not in name:
                    row[name] = E.contains_fact(t, f)
        out["facts"][key] = row
    # every scan: is its golden fact findable in each reading?
    scan_fact = {f["file"]: f for f in F.values() if f["file"].startswith("99_scans/")}
    out["scan_facts"] = {}
    for k, t in ocr_texts.items():
        if "|" not in k:
            continue
        rel, variant = k.split("|")
        f = scan_fact[rel]
        out["scan_facts"].setdefault(rel, {"fact": f["id"], "needles": f["needles"]})[variant] = E.contains_fact(t, f)
    for rel in META_FILES:
        m = C.parse_file(root, rel, "structured")[0].meta
        mp = C.parse_file(root, rel, "plain")[0].meta
        out["meta"][rel] = {"structured": m, "plain": mp, "status_line": C.status_line(m),
                            "may_read": {r: C.may_read(m, r) for r in ("PUR-EXEC", "HR-MGR")}}
    us = C.parse_file(root, "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf", "structured")
    best = json.load(open("/course/ledgerline/ledgerline/course/l3/rag_best.json"))["config"]
    ch = C.chunk(us, best["chunker"], best["size"], best["overlap"])
    c6 = [c for c in ch if "6. Supplier qualification" in (c.locs.get("sections") or [])]
    out["chunk6"] = {"config": {k: best[k] for k in ("parser", "chunker", "size", "overlap")}, "n_chunks": len(ch),
                     "chunks": [{"cite": c.cite, "header": c.text[: len(c.text) - len(c.body)].strip(), "tokens": c.n_tokens,
                                 "locs": c.locs, "body": c.body} for c in c6]}
    out["units_p2"] = [{"loc": u.loc, "heading": u.heading, "first": u.text.split("\n")[0], "tokens": C.n_tokens(u.text)}
                       for u in us if u.loc.get("page") == 2]
    out["n_units_pur"] = len(us)
    out["n_tokens_pur"] = sum(C.n_tokens(u.text) for u in us)
    for p in ("plain", "structured"):
        it = C.parse_file(root, "05_master_data/ITEM_MASTER_2026-10-26.xlsx", p)
        out["rows"][p] = {str(u.loc["row"]): u.text for u in it if u.loc.get("sheet") == "Items" and u.loc.get("row") in (4, 5, 29)}
    pl = C.parse_file(root, "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf", "plain")
    out["pur_plain_pages"] = [{"page": u.loc["page"], "text": u.text, "tokens": C.n_tokens(u.text)} for u in pl]
    return out


@app.local_entrypoint()
def deck():
    o = json.loads((LOGS / "v5_parse_ocr.json").read_text())
    rec = o["pages"]["99_scans/2026_signed_approval_PO-2026-00452.pdf"]
    texts = {"tesseract_original": rec["original"]["tesseract_text"], "tesseract_degraded": rec["degraded"]["tesseract_text"],
             "vision_original": rec["original"]["vision"]["text"], "vision_degraded": rec["degraded"]["vision"]["text"]}
    for rel, r in o["pages"].items():
        for v in ("original", "degraded"):
            texts[f"{rel}|tesseract_{v}"] = r[v]["tesseract_text"]
            texts[f"{rel}|vision_{v}"] = r[v]["vision"].get("text", "")
    out = deck_remote.remote(texts)
    out["generated"] = time.strftime("%Y-%m-%d %H:%M")
    out["script"] = "experiments/v5_parse_modal.py::deck"
    (LOGS / "v5_parse_checks.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for k, r in out["facts"].items():
        print(k, r["fact"], {x: r[x] for x in r if isinstance(r[x], bool)})
    for rel, m in out["scan_facts"].items():
        print(rel[9:30], m)
    for rel, m in out["meta"].items():
        print(rel[-50:], m["status_line"], m["may_read"])
    for c in out["chunk6"]["chunks"]:
        print(c["cite"], c["tokens"], c["header"].replace("\n", " "))
