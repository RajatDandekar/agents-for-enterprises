"""Check the golden set against the generated files.

    python check.py /path/to/northbridge-docs            # writes eval/check_report.json, exits 1 on any failure

Text is extracted from the files themselves (pypdf for PDFs, OCR with tesseract for image-only scans, python-docx,
openpyxl, csv, the e-mail parser, HTML stripped of tags), then searched for each fact's needles at the fact's
location: the PDF page(s), the spreadsheet cell(s), the CSV row, or the whole text file. Every documentation question
must be backed by facts, and every string its reference answer must contain must also be found in a gold source.
"Not in the docs" questions are checked the other way: their tell-tale terms must appear nowhere in the dump.
This file is self-contained so that it can be copied into the dump (eval/check_gold.py) and run there.
"""
from __future__ import annotations

import csv
import email
import email.policy
import html as _html
import io
import json
import os
import re
import sys
from functools import lru_cache

TYPES = {"single_lookup", "procedure", "rule", "service_field", "table_lookup", "multi_hop", "version_conflict", "exact_code", "not_in_docs", "permission"}


def norm(s: str) -> str:
    s = str(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ").replace("­", "")
    s = re.sub(r"\*\*|__", "", s)
    return re.sub(r"\s+", "", s).lower()


def norm_loose(s: str) -> str:
    """For answer strings: also ignore £ and thousands separators."""
    s = norm(s).replace("£", "")
    return re.sub(r"(?<=\d),(?=\d{3})", "", s)


def _s(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}" if abs(v) < 1e7 else f"{v:.0f}"
    return str(v)


def _cell(v):
    """A cell as text. Numbers are given both as read and with two decimals (openpyxl reads 119.0 back as 119)."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"{_s(v)} {v:.2f}"
    return _s(v)


class Extractor:
    def __init__(self, root, ocr=True):
        self.root, self.ocr = root, ocr
        self.ocr_used = 0

    @lru_cache(maxsize=None)
    def pdf_pages(self, rel):
        from pypdf import PdfReader

        r = PdfReader(os.path.join(self.root, rel))
        pages = [(p.extract_text() or "") for p in r.pages]
        if sum(len(p.strip()) for p in pages) < 20 and self.ocr:
            return self._ocr(r)
        return strip_running(pages)

    def _ocr(self, reader):
        import pytesseract

        out = []
        for p in reader.pages:
            txt = ""
            for im in p.images:
                txt += pytesseract.image_to_string(im.image) + "\n"
            out.append(txt)
        self.ocr_used += 1
        return out

    @lru_cache(maxsize=None)
    def xlsx(self, rel):
        from openpyxl import load_workbook

        wb = load_workbook(os.path.join(self.root, rel), data_only=True)
        return {ws.title: {c.coordinate: c.value for row in ws.iter_rows() for c in row if c.value is not None} for ws in wb.worksheets}

    @lru_cache(maxsize=None)
    def csv_rows(self, rel):
        raw = open(os.path.join(self.root, rel), "rb").read()
        try:
            txt = raw.decode("utf-8")
        except UnicodeDecodeError:
            txt = raw.decode("latin-1")
        return [",".join(r) for r in csv.reader(io.StringIO(txt))]

    @lru_cache(maxsize=None)
    def text(self, rel):
        p = os.path.join(self.root, rel)
        ext = rel.rsplit(".", 1)[-1].lower()
        if ext == "pdf":
            return "\n".join(self.pdf_pages(rel))
        if ext == "xlsx":
            return "\n".join(" ".join(_s(v) for v in cells.values()) for cells in self.xlsx(rel).values())
        if ext == "csv":
            return "\n".join(self.csv_rows(rel))
        if ext == "docx":
            import docx

            d = docx.Document(p)
            parts = [x.text for x in d.paragraphs]
            for t in d.tables:
                for row in t.rows:
                    parts.append(" ".join(c.text for c in row.cells))
            for s in d.sections:
                parts += [x.text for x in s.header.paragraphs] + [x.text for x in s.footer.paragraphs]
            return "\n".join(parts)
        if ext == "eml":
            m = email.message_from_bytes(open(p, "rb").read(), policy=email.policy.default)
            body = m.get_body(preferencelist=("plain",))
            return f"{m['subject']}\n{m['from']}\n{m['to']}\n{m['date']}\n" + (body.get_content() if body else "")
        if ext in ("html", "htm"):
            raw = open(p, encoding="utf-8").read()
            return _html.unescape(re.sub(r"<[^>]+>", " ", raw))
        raw = open(p, "rb").read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")

    def loc_text(self, fact):
        """The text at a fact's location."""
        f, loc = fact["file"], fact["loc"]
        if f.endswith(".pdf"):
            pages = self.pdf_pages(f)
            want = loc.get("pages") or ([loc["page"]] if loc.get("page") else None)
            if not want:
                return "\n".join(pages)
            return "\n".join(pages[p - 1] for p in want if 0 < p <= len(pages))
        if f.endswith(".xlsx") and loc.get("cells"):
            wb = self.xlsx(f)
            return "\n".join(_cell(wb.get(c["sheet"], {}).get(c["cell"])) for c in loc["cells"])
        if f.endswith(".xlsx") and loc.get("sheet"):
            return " ".join(_cell(v) for v in self.xlsx(f).get(loc["sheet"], {}).values())
        if f.endswith(".csv") and loc.get("row"):
            rows = self.csv_rows(f)
            return rows[loc["row"] - 1] if loc["row"] - 1 < len(rows) else ""
        return self.text(f)


def strip_running(pages):
    """Drop running headers and footers (lines repeated on most pages, and 'Page x of y'), so that a paragraph
    that runs over a page break reads as one piece when two pages are joined."""
    n = len(pages)
    freq = {}
    for p in pages:
        for ln in set(p.splitlines()):
            freq[ln] = freq.get(ln, 0) + 1
    out = []
    for p in pages:
        lines = p.splitlines()
        tail = max(0, len(lines) - 6)  # headers and footers are drawn last, so they come at the end of each page's text
        keep = [ln for i, ln in enumerate(lines) if not re.fullmatch(r"\s*Page \d+ of \d+\s*", ln)
                and not (i >= tail and n >= 2 and freq.get(ln, 0) >= max(2, 0.6 * n) and len(ln) < 120)]
        out.append("\n".join(keep))
    return out


def locate(ex, fact):
    """Fill in the page(s) of a PDF fact. Returns False if the needles are not found."""
    pages = ex.pdf_pages(fact["file"])
    nn = [norm(n) for n in fact["needles"]]
    for i, p in enumerate(pages):
        t = norm(p)
        if all(n in t for n in nn):
            fact["loc"]["page"] = i + 1
            return True
    for i in range(len(pages) - 1):
        t = norm(pages[i] + pages[i + 1])
        if all(n in t for n in nn):
            fact["loc"]["pages"] = [i + 1, i + 2]
            return True
    return False


def all_files(root):
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in (".git", "eval")]
        for fn in fns:
            out.append(os.path.relpath(os.path.join(dp, fn), root))
    return sorted(out)


def check(root, ocr=True):
    ex = Extractor(root, ocr=ocr)
    facts = {}
    for line in open(os.path.join(root, "eval", "facts.jsonl"), encoding="utf-8"):
        f = json.loads(line)
        facts[f["id"]] = f
    qs = [json.loads(line) for line in open(os.path.join(root, "eval", "questions.jsonl"), encoding="utf-8")]
    fails, skipped = [], []
    fact_ok = 0
    for f in facts.values():
        if not os.path.exists(os.path.join(root, f["file"])):
            fails.append(("fact", f["id"], "file missing"))
            continue
        if not ocr and f["file"].startswith("99_scans/"):
            skipped.append(f["id"])
            continue
        t = norm(ex.loc_text(f))
        if f["mode"] == "absent":
            bad = [n for n in f["needles"] if norm(n) in t]
            if bad:
                fails.append(("fact", f["id"], f"should be absent: {bad}"))
            else:
                fact_ok += 1
            continue
        miss = [n for n in f["needles"] if norm(n) not in t]
        if miss:
            fails.append(("fact", f["id"], f"not found at {f['loc'].get('page') or f['loc'].get('pages') or f['loc'].get('cells') or f['loc'].get('row') or 'file'}: {miss[:2]}"))
        else:
            fact_ok += 1
    corpus = None
    q_ok, by_type = 0, {}
    for q in qs:
        if q["category"] != "documentation":
            continue
        by_type[q["type"]] = by_type.get(q["type"], 0) + 1
        errs = []
        if q["type"] not in TYPES:
            errs.append("bad type")
        for fid in q["fact_ids"]:
            if fid not in facts:
                errs.append(f"unknown fact {fid}")
        if q["type"] != "not_in_docs" and not q["fact_ids"]:
            errs.append("no facts")
        srcs = [facts[fid] for fid in q["fact_ids"] if fid in facts]
        gold_text = norm_loose(" ".join(ex.loc_text(f) for f in srcs if f["mode"] == "present" and (ocr or not f["file"].startswith("99_scans/"))))
        gold_files = norm_loose(" ".join(ex.text(f["file"]) for f in srcs if ocr or not f["file"].startswith("99_scans/")))
        ans = norm_loose(q["reference_answer"])
        for m in q.get("must_contain", []):
            if norm_loose(m) not in ans:
                errs.append(f"answer lacks '{m}'")
            if norm_loose(m) not in gold_text and norm_loose(m) not in gold_files:
                errs.append(f"no gold source has '{m}'")
        if q["type"] == "multi_hop" and len({f["file"] for f in srcs}) < 2:
            errs.append("multi_hop with fewer than 2 files")
        if q["type"] == "permission" and not any("CONFIDENTIAL" in f["file"] for f in srcs) and q.get("expected_behaviour") == "refuse":
            errs.append("permission question without a confidential source")
        if q.get("absent_terms"):
            if corpus is None:
                corpus = [(rel, ex.text(rel).lower()) for rel in all_files(root) if not rel.startswith("99_scans/") or ocr]
            for term in q["absent_terms"]:
                hits = [rel for rel, t in corpus if term.lower() in t]
                if hits:
                    errs.append(f"'{term}' found in {hits[:2]}")
        gs = q.get("gold_sources", [])
        if len(gs) != len(q["fact_ids"]):
            errs.append("gold_sources do not match fact_ids")
        if errs:
            fails.append(("question", q["id"], "; ".join(errs)))
        else:
            q_ok += 1
    n_doc = sum(1 for q in qs if q["category"] == "documentation")
    rep = dict(facts_total=len(facts), facts_ok=fact_ok, facts_skipped=len(skipped), documentation_questions=n_doc, questions_ok=q_ok,
               by_type=by_type, genesis=sum(1 for q in qs if q["category"] == "genesis"),
               analytical=sum(1 for q in qs if q["category"] == "analytical"), ocr_files=ex.ocr_used,
               passed=not fails, failures=[{"kind": a, "id": b, "why": c} for a, b, c in fails])
    return rep


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ocr = True
    try:
        import pytesseract  # noqa: F401
        pytesseract.get_tesseract_version()
    except Exception:  # noqa: BLE001
        ocr = False
        print("tesseract not found: the 6 scanned PDFs are skipped (install tesseract to check them).")
    rep = check(root, ocr=ocr)
    with open(os.path.join(root, "eval", "check_report.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(f"facts {rep['facts_ok']}/{rep['facts_total']} ok ({rep['facts_skipped']} skipped), questions {rep['questions_ok']}/{rep['documentation_questions']} ok")
    for x in rep["failures"][:40]:
        print(" FAIL", x)
    sys.exit(0 if rep["passed"] else 1)
