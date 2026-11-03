"""Build the northbridge-docs dump.

    phase collect: build every document in memory, return the LLM prompts that are not cached yet
    phase render:  write every file, locate the facts, write eval/, check, count

Run it through tools/northbridge_docs/modal_app.py (rendering and LLM calls happen on Modal).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil

from . import content_data, content_manuals, content_misc, content_notes, content_policies, content_procs, golden
from .check import Extractor, all_files, check, locate, norm
from .ctx import Ctx
from .model import FACTS, Book
from .render import write

ORDER = [content_policies, content_procs, content_manuals, content_data, content_notes, content_misc]
OLD_WORDS = ["Rasoi", "Kavita", "Rohit", "Neha", "Suresh", "Anand", "Deccan", "Sahyadri", "Mahalaxmi", "Kaveri", "Shakti", "Pune", "Chakan",
             "Diwali", "gasket", "cooker", "Bahi", "bahi", "GST", "₹", "lakh", "crore", "IST", "FSSAI", "India", "Rs.", "INR", "food", "Food",
             "rupee", "rupees", "litre", "godown", "festival", "challan", "IGST", "CGST", "SGST", "MSME", "PAN", "Nagpur", "dealer", "lids",
             "Indian"]


def make(llm_mode="use"):
    FACTS.items.clear()
    FACTS.ids.clear()
    c = Ctx(llm_mode)
    for m in ORDER:
        m.build(c)
    c.questions = golden.build(c)
    return c


def collect():
    c = make("collect")
    return c, c.llm.missing


def render(c, root, verify_root=None):
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    sizes = {}
    for o in c.outputs:
        sizes[o.path] = write(o, root)
    for src, dst in c.copies:
        os.makedirs(os.path.dirname(os.path.join(root, dst)), exist_ok=True)
        shutil.copyfile(os.path.join(root, src), os.path.join(root, dst))
    ex = Extractor(root, ocr=True)
    unlocated = []
    for f in FACTS.items:
        f["file"] = f["file"]
        if f["file"].endswith(".pdf") and f["mode"] == "present":
            if not locate(ex, f):
                unlocated.append(f["id"])
    write_eval(c, root)
    rep = check(root, ocr=True)
    with open(os.path.join(root, "eval", "check_report.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    st = stats(root, ex)
    with open(os.path.join(root, "eval", "stats.json"), "w") as fh:
        json.dump(st, fh, indent=1)
    left = leftovers(root, ex)
    shutil.copyfile(os.path.join(os.path.dirname(__file__), "check.py"), os.path.join(root, "eval", "check_gold.py"))
    return dict(unlocated=unlocated, check=rep, stats=st["totals"], leftovers=left)


def _gold(f):
    g = {"file": f["file"], "fact_id": f["id"]}
    loc = f["loc"]
    if loc.get("page"):
        g["page"] = loc["page"]
    if loc.get("pages"):
        g["pages"] = loc["pages"]
    if loc.get("section"):
        g["section"] = loc["section"]
    if loc.get("cells"):
        g["sheet"] = loc["cells"][0]["sheet"]
        g["cells"] = [x["cell"] for x in loc["cells"]]
    if loc.get("row"):
        g["row"] = loc["row"]
    if f["mode"] == "absent":
        g["absent"] = True
    return g


def write_eval(c, root):
    ev = os.path.join(root, "eval")
    os.makedirs(ev, exist_ok=True)
    with open(os.path.join(ev, "facts.jsonl"), "w", encoding="utf-8") as fh:
        for f in FACTS.items:
            out = dict(id=f["id"], statement=f["statement"], file=f["file"], mode=f["mode"], needles=f["needles"],
                       loc={k: v for k, v in f["loc"].items() if k != "fmt"}, format=f["loc"].get("fmt"))
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")
    facts = {f["id"]: f for f in FACTS.items}
    with open(os.path.join(ev, "questions.jsonl"), "w", encoding="utf-8") as fh:
        for qid, typ, diff, q, a, fids, must, extra in c.questions:
            rec = dict(id=qid, category="documentation", type=typ, difficulty=diff, question=q, reference_answer=a, fact_ids=fids,
                       gold_sources=[_gold(facts[x]) for x in fids if x in facts], must_contain=must)
            if extra.get("asker_role"):
                rec["asker_role"] = extra["asker_role"]
            if extra.get("expected"):
                rec["expected_behaviour"] = extra["expected"]
            if extra.get("absent"):
                rec["absent_terms"] = extra["absent"]
            if extra.get("running_example"):
                rec["running_example"] = extra["running_example"]
            if typ == "permission":
                rec.setdefault("expected_behaviour", "refuse")
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        for i, q in enumerate(golden.GENESIS, 1):
            fh.write(json.dumps(dict(id=f"G-{i:03d}", category="genesis", question=q, note="needs services (tools): Lecture 4 onward"), ensure_ascii=False) + "\n")
        for i, q in enumerate(golden.ANALYTICAL, 1):
            fh.write(json.dumps(dict(id=f"A-{i:03d}", category="analytical", question=q, note="needs data queries over 05/06 or services"), ensure_ascii=False) + "\n")
    missing = [p for m in c.messiness for p in m["files"] if not os.path.exists(os.path.join(root, p))]
    with open(os.path.join(ev, "messiness.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(items=c.messiness, files_missing=missing), fh, indent=1, ensure_ascii=False)


def stats(root, ex):
    import tiktoken

    enc = tiktoken.get_encoding("o200k_base")
    per = {}
    total = dict(files=0, bytes=0, pdf_pages=0, words=0, rows=0, tokens=0, max_file_bytes=0, max_file="")
    for rel2 in walk(root):
        full = os.path.join(root, rel2)
        top = rel2.split("/")[0] if "/" in rel2 else "(root)"
        ext = rel2.rsplit(".", 1)[-1].lower() if "." in rel2 else "none"
        b = os.path.getsize(full)
        d = per.setdefault(top, dict(files=0, bytes=0, pdf_pages=0, words=0, rows=0, tokens=0, types={}))
        d["files"] += 1
        d["bytes"] += b
        d["types"][ext] = d["types"].get(ext, 0) + 1
        try:
            txt = ex.text(rel2)
        except Exception:  # noqa: BLE001
            txt = ""
        if ext == "pdf":
            d["pdf_pages"] += len(ex.pdf_pages(rel2))
        if ext == "xlsx":
            d["rows"] += sum(max([int(re.sub(r"\D", "", k)) for k in cells] or [0]) for cells in ex.xlsx(rel2).values())
        if ext == "csv":
            d["rows"] += len(ex.csv_rows(rel2))
        d["words"] += len(txt.split())
        d["tokens"] += len(enc.encode(txt, disallowed_special=()))
        if b > total["max_file_bytes"]:
            total["max_file_bytes"], total["max_file"] = b, rel2
    for d in per.values():
        for k in ("files", "bytes", "pdf_pages", "words", "rows", "tokens"):
            total[k] += d[k]
    return dict(totals=total, by_folder=dict(sorted(per.items())), tokenizer="tiktoken o200k_base on extracted text (OCR for scans)")


BRANDS = ["Shimano", "Bosch", "SRAM", "Brompton", "Microsoft", "Excel", "Outlook", "Google", "Amazon", "SAP", "Oracle", "DHL", "FedEx",
          "Royal Mail", "DPD", "Barclays", "HSBC", "Lloyds", "NatWest", "Santander", "Samsung", "Panasonic", "Tesla", "IBM", "Salesforce",
          "Slack", "Zoom", "SharePoint", "Sharepoint", "Dropbox", "Adobe", "OpenAI", "ChatGPT", "Gemini", "Jira", "Confluence", "Siemens",
          "Honeywell", "Sage", "Xero", "Halfords", "Decathlon", "Specialized", "Gogoro"]


def leftovers(root, ex):
    rx = [(w, re.compile((r"(?<![A-Za-z0-9_])" + re.escape(w) + r"(?![A-Za-z0-9_])") if w.replace(" ", "").isalpha() else re.escape(w))) for w in OLD_WORDS + BRANDS]
    hits = {}
    for rel in all_files(root):
        t = ex.text(rel)
        h = [w for w, r in rx if r.search(t)]
        if h:
            hits[rel] = h
    return hits


def walk(root):
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [x for x in dns if x != ".git"]
        out += [os.path.relpath(os.path.join(dp, f), root) for f in fns]
    return sorted(out)


def manifest(root):
    out = {}
    for rel in walk(root):
        out[rel] = hashlib.sha256(open(os.path.join(root, rel), "rb").read()).hexdigest()
    return out
