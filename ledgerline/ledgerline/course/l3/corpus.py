"""Lecture 3 v4: the northbridge-docs dump, parsed by document type into units with a precise location.

    from ledgerline.course.l3 import corpus as C
    root  = C.dump_root()                         # arg > $NORTHBRIDGE_DOCS > ./northbridge-docs > the builder's local copy
    files = C.list_files(root)                    # every file except .git/ and eval/ (relative paths)
    units = C.parse(root, parser="structured")    # or "plain"; list[Unit], cached on disk (see CACHE_DIR)
    chunks = C.chunk(units, "structure", size=400, overlap=0.0)   # "fixed" | "recursive" | "structure"; list[Chunk]
    qs    = C.questions(root)                     # the 224 documentation questions (category="all" for all 304)
    facts = C.facts(root)                         # {fact_id: fact}
    C.may_read(meta, role)                        # permissions: only HR roles read 01_policies/HR/CONFIDENTIAL
    C.role_of(question)                           # the asker's role (asker_role, default Emma's PUR-EXEC)

A Unit is one piece of one file, at the finest grain its format has:
    PDF   one unit per page (plain) or per (page, section) (structured: headings from font size and weight,
          tables as "a | b | c" rows, running headers and footers removed); scans are OCR'd (structured only)
    DOCX  whole document, paragraphs only (plain) or one unit per heading section, tables included (structured)
    XLSX  one unit per row: values only (plain) or "column: value; ..." with the sheet's title lines (structured)
    CSV   one unit per row, the same way
    YAML / XML / WSDL   one service per unit (raw text in plain; a readable summary + the definition in structured)
    EML   raw file text with quoted-printable soft breaks (plain) or decoded headers + body (structured)
    HTML  raw markup (plain) or text by heading, tables as rows, no navigation (structured)
    MD    raw (plain) or one unit per heading (structured); TXT / EDI / JSON raw in both
Unit.loc is the location the golden set uses: {"page": 2, "section": "6. Supplier qualification"},
{"sheet": "Suppliers", "row": 4}, {"row": 17} (CSV, 1 = header), {"section": "body"}, {"service": "po_save"}.
Unit.meta is file metadata read from the document itself (never from eval/): doc_id, title, version, effective,
status, classification, confidential, superseded, future (effective after TODAY), folder, fmt, kind.

A Chunk is what gets embedded: Chunk.text (with a context header in structured mode), Chunk.locs
({"pages": [2, 3], "sections": [...], "rows": {"Suppliers": [4, 9]}, "services": [...]}), Chunk.meta, Chunk.cite.
Token counts use tiktoken o200k_base everywhere (chunk sizes, the audit).

Dependencies: pypdf, pdfplumber, openpyxl, python-docx, pyyaml, tiktoken; pytesseract + tesseract for the scans.
"""
from __future__ import annotations

import csv
import email
import email.policy
import gzip
import hashlib
import html as _html
import io
import json
import os
import pathlib
import re
import subprocess
from dataclasses import asdict, dataclass, field
from functools import lru_cache

TODAY = "2026-10-26"  # the sandbox clock: Monday 26 October 2026, 09:00
REPO_URL = "https://github.com/RajatDandekar/northbridge-docs"
LOCAL_COPY = "/Users/raj/Claude_Brain/northbridge-docs"
CACHE_DIR = pathlib.Path(os.environ.get("NB_L3_CACHE", pathlib.Path.home() / ".cache" / "northbridge-l3"))
PARSERS = ("plain", "structured")
CHUNKERS = ("fixed", "recursive", "structure")
HR_ROLES = {"HR-MGR", "HR", "HR-ADMIN"}
DEFAULT_ROLE = "PUR-EXEC"  # Emma Clarke (ECLARKE)
PARSER_VERSION = "1"

FMT_CLASS = {  # the structured / semi-structured / unstructured split used by the audit
    "xlsx": "structured", "csv": "structured",
    "yaml": "semi-structured", "xml": "semi-structured", "wsdl": "semi-structured", "json": "semi-structured",
    "edi": "semi-structured", "eml": "semi-structured", "html": "semi-structured", "md": "semi-structured",
    "pdf": "unstructured", "docx": "unstructured", "txt": "unstructured",
}


# =============================================================================== where the dump is
def dump_root(path: str | os.PathLike | None = None, clone_to: str | None = None) -> pathlib.Path:
    """The northbridge-docs folder: the argument, $NORTHBRIDGE_DOCS, ./northbridge-docs (a clone), the local copy.
    With clone_to, `git clone` the repository there first if it is not already present."""
    if clone_to and not (pathlib.Path(clone_to) / "README.md").exists():
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(clone_to)], check=True)
    for p in (path, os.environ.get("NORTHBRIDGE_DOCS"), clone_to, "northbridge-docs", "../northbridge-docs", LOCAL_COPY):
        if p and (pathlib.Path(p) / "README.md").exists() and (pathlib.Path(p) / "eval").exists():
            return pathlib.Path(p).resolve()
    raise FileNotFoundError(f"northbridge-docs not found; git clone {REPO_URL} or set NORTHBRIDGE_DOCS")


def list_files(root) -> list[str]:
    root = pathlib.Path(root)
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in (".git", "eval") and not d.startswith("."))
        for fn in sorted(fns):
            if fn.startswith("."):
                continue
            out.append(os.path.relpath(os.path.join(dp, fn), root))
    return sorted(out)


def fmt_of(rel: str) -> str:
    return rel.rsplit(".", 1)[-1].lower() if "." in rel else "txt"


def questions(root=None, category: str = "documentation") -> list[dict]:
    root = dump_root(root)
    qs = [json.loads(l) for l in open(root / "eval" / "questions.jsonl", encoding="utf-8") if l.strip()]
    return qs if category == "all" else [q for q in qs if q["category"] == category]


def facts(root=None) -> dict[str, dict]:
    root = dump_root(root)
    return {f["id"]: f for f in (json.loads(l) for l in open(root / "eval" / "facts.jsonl", encoding="utf-8") if l.strip())}


def role_of(q: dict) -> str:
    return q.get("asker_role") or DEFAULT_ROLE


def may_read(meta: dict, role: str | None = DEFAULT_ROLE) -> bool:
    """Filter BEFORE ranking: a confidential HR document is not in a non-HR user's index at all."""
    return not meta.get("confidential") or (role or DEFAULT_ROLE) in HR_ROLES


# =============================================================================== tokens
@lru_cache(maxsize=1)
def _enc():
    import tiktoken

    return tiktoken.get_encoding("o200k_base")


def n_tokens(text: str) -> int:
    return len(_enc().encode(text, disallowed_special=())) if text else 0


def encode(text: str) -> list[int]:
    return _enc().encode(text, disallowed_special=())


def decode(toks: list[int]) -> str:
    return _enc().decode(toks)


# =============================================================================== data classes
@dataclass
class Unit:
    uid: str
    file: str
    fmt: str
    kind: str              # text | table | service | email | scan
    text: str
    loc: dict
    meta: dict
    heading: str = ""      # heading path ("6. Supplier qualification"), sheet title lines, or the service name

    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class Chunk:
    cid: str
    file: str
    text: str              # what is embedded and searched (structured chunks start with a context header)
    body: str              # the text without the header
    locs: dict
    meta: dict
    n_tokens: int = 0

    @property
    def cite(self) -> str:
        m, l = self.meta, self.locs
        name = m.get("doc_id") or pathlib.Path(self.file).name
        bits = [name + (f" v{m['version']}" if m.get("version") and m.get("doc_id") else "")]
        if l.get("pages"):
            p = l["pages"]
            bits.append(f"p.{p[0]}" if len(p) == 1 else f"pp.{p[0]}-{p[-1]}")
        if l.get("sections"):
            bits.append("§ " + l["sections"][0][:60])
        for s, (a, b) in (l.get("rows") or {}).items():
            bits.append(f"{s + ' ' if s else ''}rows {a}-{b}" if a != b else f"{s + ' ' if s else ''}row {a}")
        if l.get("services"):
            bits.append("service " + ", ".join(l["services"][:3]))
        return ", ".join(bits)

    def as_item(self) -> dict:
        """The shape evaluate.py scores: a retrieved item with its text and location."""
        return {"id": self.cid, "file": self.file, "text": self.body, "loc": self.locs, "cite": self.cite,
                "meta": {k: self.meta.get(k) for k in ("doc_id", "title", "version", "effective", "status",
                                                        "confidential", "superseded", "future")}}


# =============================================================================== file metadata
_DOCID = re.compile(r"(?<![-A-Za-z0-9])(RN-\d+\.\d+(?:\.\d+)?(?:-P\d+)?|(?:POL|SOP|MAN|AMD|HR-CONF|QRC|BHT|NBC-F)-[A-Z0-9]+(?:-[A-Z0-9]+)*)", re.I)
_VER = re.compile(r"\bv(\d+(?:\.\d+){0,2})\b", re.I)


def file_meta(rel: str, head_text: str = "") -> dict:
    """Metadata from the path and the document's own first page (its 'Field | Value' block, if any)."""
    name = pathlib.Path(rel).name
    stem = pathlib.Path(rel).stem
    fmt = fmt_of(rel)
    folder = rel.split("/", 1)[0] if "/" in rel else "(root)"
    h = head_text[:4000]

    def field(*keys):
        for k in keys:
            m = re.search(rf"(?im)^\s*\|?\s*{k}\s*(?:\||:)?\s*([^\n|]+)", h)
            if m and m.group(1).strip():
                return m.group(1).strip()
        return ""

    doc_id = field("Document", "Document no", "Doc")
    if not _DOCID.fullmatch(doc_id or ""):
        m = _DOCID.search(stem.replace("_", " ")) or (_DOCID.search(h[:300]) if fmt in ("pdf", "docx") else None)
        doc_id = m.group(1).upper() if m else ""
    version = field("Version")
    if not re.fullmatch(r"\d+(\.\d+)*", version or ""):
        m = _VER.search(stem) or re.search(r"(?i)\bversion\s+(\d+(?:\.\d+){0,2})", h[:600])
        version = m.group(1) if m else ""
    eff = field("Effective", "Effective from", "In force from", "Valid from")
    m = re.search(r"(\d{4}-\d{2}-\d{2})", eff or "") or re.search(r"\(effective (\d{4}-\d{2}-\d{2})\)", name)
    effective = m.group(1) if m else ""
    status = field("Status").upper()[:40]
    classification = field("Classification").upper()[:40]
    title = ""
    for line in h.splitlines():
        s = line.strip()
        if s and not s.lower().startswith(("northbridge cycles ltd", "field", "|")) and len(s) > 3:
            title = s[:120]
            break
    if fmt not in ("pdf", "docx", "txt", "md"):
        title = stem
    title = title or stem
    confidential = "/CONFIDENTIAL/" in f"/{rel}" or classification.startswith("CONFIDENTIAL") or "HR-CONF" in name.upper()
    superseded = ("/old/" in f"/{rel}" or any(w in status for w in ("SUPERSEDED", "WITHDRAWN", "OBSOLETE"))
                  or "_legacy" in rel or "(old)" in name.lower())
    future = bool(effective and effective > TODAY) or "PREVIEW" in name.upper()
    return dict(file=rel, folder=folder, fmt=fmt, fmt_class=FMT_CLASS.get(fmt, "unstructured"), doc_id=doc_id,
                title=title, version=version, effective=effective, status=status, classification=classification,
                confidential=confidential, superseded=superseded, future=future,
                audience="HR only (NBC-HR-CONF)" if confidential else "all staff")


def status_line(meta: dict) -> str:
    bits = []
    if meta.get("superseded"):
        bits.append("SUPERSEDED / old copy")
    if meta.get("future"):
        bits.append(f"NOT YET IN FORCE (from {meta.get('effective') or 'a later date'})")
    if meta.get("confidential"):
        bits.append("CONFIDENTIAL: HR only")
    return "; ".join(bits)


# =============================================================================== small helpers
def _read_text(path) -> str:
    raw = open(path, "rb").read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _cellstr(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        if v.is_integer() and abs(v) < 1e15:
            return str(int(v))
        return f"{v:.2f}" if abs(v) >= 1 else f"{v:g}"
    if hasattr(v, "isoformat"):
        return v.isoformat()[:10]
    return str(v).strip()


_PAGE_NO = re.compile(r"(?i)^\s*(uncontrolled when printed\.?\s*)?page \d+ of \d+\s*$|^\s*-\s*\d+\s*-\s*$")


def _norm_line(s: str) -> str:
    return re.sub(r"\d+", "#", s.strip().lower())


# =============================================================================== PDF
def _pdf_plain(path, rel, meta):
    from pypdf import PdfReader

    r = PdfReader(path)
    out = []
    for i, p in enumerate(r.pages, 1):
        t = p.extract_text() or ""
        out.append(Unit(f"{rel}#p{i}", rel, "pdf", "text", t, {"page": i}, meta))
    return out


def _ocr_pages(path) -> list[str]:
    from pypdf import PdfReader

    try:
        import pytesseract
    except ImportError:
        return []
    out = []
    for p in PdfReader(path).pages:
        txt = ""
        for im in p.images:
            try:
                txt += pytesseract.image_to_string(im.image) + "\n"
            except Exception:  # noqa: BLE001
                pass
        out.append(txt)
    return out


def _lines_from_words(words, tol=2.5):
    lines = []
    for w in sorted(words, key=lambda w: (round(w["top"] / tol), w["x0"])):
        if lines and abs(lines[-1]["top"] - w["top"]) <= tol:
            L = lines[-1]
            L["words"].append(w)
        else:
            lines.append({"top": w["top"], "bottom": w["bottom"], "words": [w]})
    for L in lines:
        ws = sorted(L["words"], key=lambda w: w["x0"])
        L["text"] = " ".join(w["text"] for w in ws)
        L["size"] = max(w["size"] for w in ws)
        nchar = sum(len(w["text"]) for w in ws) or 1
        L["bold"] = sum(len(w["text"]) for w in ws if "bold" in w["fontname"].lower()) / nchar
        L["bottom"] = max(w["bottom"] for w in ws)
    return lines


def _pdf_structured(path, rel):
    import pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            try:
                tables = pg.find_tables()
            except Exception:  # noqa: BLE001
                tables = []
            boxes = [t.bbox for t in tables]

            def outside(obj, boxes=boxes):
                cx, cy = (obj["x0"] + obj["x1"]) / 2, (obj["top"] + obj["bottom"]) / 2
                return not any(b[0] - 1 <= cx <= b[2] + 1 and b[1] - 1 <= cy <= b[3] + 1 for b in boxes)

            words = pg.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False)
            lines = _lines_from_words([w for w in words if outside(w)])
            items = [("line", L["top"], L) for L in lines]
            for t in tables:
                try:
                    rows = t.extract()
                except Exception:  # noqa: BLE001
                    rows = []
                rows = [[re.sub(r"\s+", " ", c or "").strip() for c in r] for r in rows if r and any(c for c in r)]
                if rows:
                    items.append(("table", t.bbox[1], rows))
            items.sort(key=lambda x: x[1])
            pages.append({"h": pg.height, "items": items})
    if sum(len(p["items"]) for p in pages) == 0:
        return None  # image-only: the caller OCRs it
    # running headers and footers: short lines in the top/bottom bands repeated on most pages, and "Page x of y"
    n = len(pages)
    freq = {}
    for p in pages:
        for kind, top, L in p["items"]:
            if kind == "line" and (top < 70 or top > p["h"] - 70):
                k = _norm_line(L["text"])
                freq[k] = freq.get(k, 0) + 1
    sizes = {}
    for p in pages:
        for kind, _, L in p["items"]:
            if kind == "line":
                sizes[round(L["size"], 1)] = sizes.get(round(L["size"], 1), 0) + len(L["text"])
    body = max(sizes, key=sizes.get) if sizes else 10.0
    out_pages = []
    for p in pages:
        clean = []
        for kind, top, L in p["items"]:
            if kind == "line":
                t = L["text"].strip()
                band = top < 70 or top > p["h"] - 70
                if _PAGE_NO.match(t) or (band and n >= 2 and freq.get(_norm_line(t), 0) >= max(2, 0.5 * n) and len(t) < 140):
                    continue
                if band and re.search(r"(?i)uncontrolled when printed|page \d+ of \d+", t) and L["size"] < body:
                    continue
                L["heading"] = (len(t) < 110 and not t.endswith((".", ",", ";")) and
                                ((L["bold"] > 0.6 and L["size"] >= body * 1.02) or L["size"] >= body * 1.25))
            clean.append((kind, top, L))
        out_pages.append(clean)
    return out_pages, body


def _table_text(rows) -> str:
    return "\n".join(" | ".join(r) for r in rows)


def parse_pdf(path, rel, parser):
    if parser == "plain":
        units = _pdf_plain(path, rel, None)
        head = units[0].text if units else ""
        meta = file_meta(rel, head)
        for u in units:
            u.meta = meta
        return units
    res = _pdf_structured(path, rel)
    if res is None:  # a scan: OCR every page
        txts = _ocr_pages(path)
        meta = file_meta(rel, txts[0] if txts else "")
        meta["scan"] = True
        return [Unit(f"{rel}#p{i}", rel, "pdf", "scan", t.strip(), {"page": i, "section": f"page {i}"}, meta,
                     f"scan page {i}") for i, t in enumerate(txts, 1)]
    pages, body = res
    # first page text for metadata (tables included, as "Field | Value" rows)
    head = "\n".join(_table_text(L) if k == "table" else L["text"] for k, _, L in pages[0]) if pages else ""
    meta = file_meta(rel, head)
    sizes = sorted({round(L["size"], 1) for pg in pages for k, _, L in pg if k == "line" and L.get("heading")}, reverse=True)
    level = {s: i for i, s in enumerate(sizes)}
    units, stack, buf = [], [], []
    title_seen = False

    def flush(page_no):
        text = "\n".join(buf).strip()
        if text:
            sec = stack[-1][1] if stack else ""
            units.append(Unit(f"{rel}#p{page_no}s{len(units)}", rel, "pdf",
                              "table" if all(x.count(" | ") for x in buf) else "text", text,
                              {"page": page_no, "section": sec}, meta, " › ".join(h for _, h in stack)))
        buf.clear()

    for pno, pg in enumerate(pages, 1):
        for kind, _, L in pg:
            if kind == "table":
                buf.append(_table_text(L))
                continue
            if L.get("heading"):
                lv = level.get(round(L["size"], 1), 9)
                if not title_seen and lv == 0 and pno == 1:
                    title_seen = True
                    meta["title"] = L["text"][:120] if not meta.get("title") or meta["title"].lower().startswith("northbridge") else meta["title"]
                flush(pno)
                while stack and stack[-1][0] >= lv:
                    stack.pop()
                stack.append((lv, L["text"].strip()))
                buf.append(L["text"].strip())
            else:
                buf.append(L["text"])
        flush(pno)
    return units


# =============================================================================== DOCX
def parse_docx(path, rel, parser):
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    d = docx.Document(path)
    if parser == "plain":
        text = "\n".join(p.text for p in d.paragraphs)
        meta = file_meta(rel, text)
        return [Unit(f"{rel}#all", rel, "docx", "text", text, {}, meta)]
    blocks = []
    for el in d.element.body.iterchildren():
        tag = el.tag.split("}")[-1]
        if tag == "p":
            p = Paragraph(el, d)
            sname = (p.style.name if p.style is not None else "") or ""
            blocks.append(("p", sname, p.text))
        elif tag == "tbl":
            t = Table(el, d)
            rows = []
            for r in t.rows:
                cells = []
                for c in r.cells:
                    s = re.sub(r"\s+", " ", c.text).strip()
                    if not cells or cells[-1] != s:  # merged cells repeat
                        cells.append(s)
                rows.append(" | ".join(cells))
            blocks.append(("t", "", "\n".join(rows)))
    head = "\n".join(b[2] for b in blocks[:30])
    meta = file_meta(rel, head)
    hdr = [x.text for s in d.sections for x in s.header.paragraphs if x.text.strip()]
    units, stack, buf = [], [], []

    def flush():
        text = "\n".join(buf).strip()
        if text:
            sec = stack[-1][1] if stack else ""
            units.append(Unit(f"{rel}#s{len(units)}", rel, "docx", "text", text, {"section": sec}, meta,
                              " › ".join(h for _, h in stack)))
        buf.clear()

    for kind, sname, text in blocks:
        m = re.match(r"(?i)heading (\d)", sname)
        if kind == "p" and (m or sname.lower() == "title") and text.strip():
            lv = int(m.group(1)) if m else 0
            if lv == 0:
                meta["title"] = text.strip()[:120]
            flush()
            while stack and stack[-1][0] >= lv:
                stack.pop()
            stack.append((lv, text.strip()))
            buf.append(text.strip())
        elif text.strip():
            buf.append(text)
    flush()
    if hdr and units:
        units[0].text = "\n".join(hdr) + "\n" + units[0].text
    return units


# =============================================================================== spreadsheets
def _header_row(rows: list[tuple]) -> int:
    """Index of the header row: the first of the top rows that is mostly non-empty strings with a filled row below."""
    for i, r in enumerate(rows[:8]):
        vals = [v for v in r if v not in (None, "")]
        if not vals:
            continue
        width = max(len([v for v in rr if v not in (None, "")]) for rr in rows[: min(len(rows), 12)]) or 1
        nxt = rows[i + 1] if i + 1 < len(rows) else ()
        if (len(vals) >= 0.6 * width and all(isinstance(v, str) for v in vals) and len(vals) >= 2
                and len([v for v in nxt if v not in (None, "")]) >= 0.5 * len(vals)):
            return i
    return 0


def _table_units(rel, fmt, sheet, rows, first_row_no, meta, parser):
    out = []
    if parser == "plain":
        for i, r in enumerate(rows):
            t = " ".join(_cellstr(v) for v in r if v not in (None, ""))
            if t:
                loc = {"sheet": sheet, "row": first_row_no + i} if sheet is not None else {"row": first_row_no + i}
                out.append(Unit(f"{rel}#{sheet or ''}!r{first_row_no + i}", rel, fmt, "table", t, loc, meta))
        return out
    h = _header_row(rows)
    header = [_cellstr(v) or f"col{j + 1}" for j, v in enumerate(rows[h])] if rows else []
    titles = [" ".join(_cellstr(v) for v in r if v not in (None, "")) for r in rows[:h]]
    titles = [t for t in titles if t]
    context = (f"Sheet {sheet}. " if sheet else "") + " ".join(titles)
    for i in range(h + 1, len(rows)):
        r = rows[i]
        pairs = [f"{header[j] if j < len(header) else f'col{j + 1}'}: {_cellstr(v)}" for j, v in enumerate(r)
                 if v not in (None, "")]
        if not pairs:
            continue
        loc = {"sheet": sheet, "row": first_row_no + i} if sheet is not None else {"row": first_row_no + i}
        out.append(Unit(f"{rel}#{sheet or ''}!r{first_row_no + i}", rel, fmt, "table", "; ".join(pairs), loc, meta,
                        context.strip()))
    return out


def parse_xlsx(path, rel, parser):
    from openpyxl import load_workbook

    wb = load_workbook(path, data_only=True)
    head = []
    for ws in wb.worksheets[:1]:
        for r in ws.iter_rows(min_row=1, max_row=3, values_only=True):
            head.append(" ".join(_cellstr(v) for v in r if v is not None))
    meta = file_meta(rel, "\n".join(head))
    units = []
    for ws in wb.worksheets:
        rows = [tuple(c.value for c in r) for r in ws.iter_rows()]
        first = ws.min_row or 1
        units += _table_units(rel, "xlsx", ws.title, rows, first, meta, parser)
    return units


def parse_csv(path, rel, parser):
    txt = _read_text(path)
    rows = [tuple(r) for r in csv.reader(io.StringIO(txt))]
    meta = file_meta(rel, "\n".join(",".join(r) for r in rows[:3]))
    if parser == "plain":
        lines = txt.splitlines()
        return [Unit(f"{rel}#r{i}", rel, "csv", "table", ln, {"row": i}, meta) for i, ln in enumerate(lines, 1) if ln.strip()]
    return _table_units(rel, "csv", None, rows, 1, meta, parser)


# =============================================================================== services
def _yaml_summary(d: dict) -> str:
    req = (d.get("request") or {}).get("fields") or []
    must = [f.get("name") for f in req if isinstance(f, dict) and f.get("required")]
    opt = [f.get("name") for f in req if isinstance(f, dict) and not f.get("required")]
    errs = [f"{e.get('code')} {e.get('msg')}" for e in (d.get("errors") or []) if isinstance(e, dict)]
    bits = [f"Service {d.get('service')} ({d.get('title', '')}), module {d.get('module', '')}, kind {d.get('kind', '')}, "
            f"screen {d.get('screen', '')}, since {d.get('since', '')}."]
    if req:
        bits.append(f"Required fields: {', '.join(map(str, must)) or 'none'}. Optional fields: {', '.join(map(str, opt)) or 'none'}.")
    if errs:
        bits.append("Errors: " + "; ".join(errs) + ".")
    return " ".join(bits)


def parse_yaml(path, rel, parser):
    import yaml

    raw = _read_text(path)
    meta = file_meta(rel, raw[:400])
    if parser == "plain":
        return [Unit(f"{rel}#all", rel, fmt_of(rel), "service", raw, {}, meta)]
    try:
        d = yaml.safe_load(raw)
    except Exception:  # noqa: BLE001
        d = None
    if isinstance(d, dict) and d.get("service"):
        name = str(d["service"])
        meta["doc_id"] = meta.get("doc_id") or f"svc:{name}"
        meta["title"] = f"Service {name} ({d.get('title', '')})"
        body = re.sub(r"(?m)^#.*\n", "", raw).strip()
        return [Unit(f"{rel}#svc", rel, "yaml", "service", _yaml_summary(d) + "\n" + body,
                     {"service": name, "section": "request.fields"}, meta, f"service {name}")]
    return [Unit(f"{rel}#all", rel, fmt_of(rel), "text", raw, {}, meta)]


def parse_xml(path, rel, parser):
    raw = _read_text(path)
    meta = file_meta(rel, raw[:400])
    if parser == "plain":
        return [Unit(f"{rel}#all", rel, fmt_of(rel), "service", raw, {}, meta)]
    comments = [c.strip() for c in re.findall(r"<!--(.*?)-->", raw, re.S)]
    docs = [_html.unescape(x.strip()) for x in re.findall(r"<(?:\w+:)?documentation>(.*?)</(?:\w+:)?documentation>", raw, re.S)]
    els = re.findall(r'<(?:\w+:)?element name="([^"]+)"(?: type="([^"]+)")?(?: minOccurs="(\d)")?', raw)
    name = (re.search(r'(?:definitions|service|method|rpc)[^>]*name="([^"]+)"', raw) or [None, pathlib.Path(rel).stem])[1]
    must = [e[0] for e in els if e[2] == "1"]
    opt = [e[0] for e in els if e[2] == "0"]
    summary = (f"Service {name} (legacy XML/SOAP definition). {' '.join(docs[:1])} "
               f"Required fields: {', '.join(must) or 'none'}. Optional fields: {', '.join(opt) or 'none'}. "
               + " ".join(comments))
    text = summary + "\n" + "\n".join(docs[1:]) + "\n" + re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)).strip()[:4000]
    meta["title"] = f"Service {name} (XML)"
    return [Unit(f"{rel}#svc", rel, fmt_of(rel), "service", text, {"service": name}, meta, f"service {name}")]


# =============================================================================== e-mail, html, markdown, text
def parse_eml(path, rel, parser):
    raw = open(path, "rb").read()
    if parser == "plain":
        t = raw.decode("utf-8", "replace")
        return [Unit(f"{rel}#all", rel, "eml", "email", t, {}, file_meta(rel, ""))]
    m = email.message_from_bytes(raw, policy=email.policy.default)
    body = m.get_body(preferencelist=("plain", "html"))
    content = body.get_content() if body else ""
    if body is not None and body.get_content_type() == "text/html":
        content = _html.unescape(re.sub(r"<[^>]+>", " ", content))
    att = [p.get_filename() for p in m.iter_attachments() if p.get_filename()] if m.is_multipart() else []
    head = f"E-mail. Subject: {m['subject']}\nFrom: {m['from']}\nTo: {m['to']}\nDate: {m['date']}"
    if att:
        head += "\nAttachments: " + ", ".join(att)
    meta = file_meta(rel, "")
    meta["title"] = f"E-mail: {m['subject']}"[:120]
    try:
        meta["effective"] = email.utils.parsedate_to_datetime(m["date"]).date().isoformat()
    except Exception:  # noqa: BLE001
        pass
    return [Unit(f"{rel}#body", rel, "eml", "email", head + "\n\n" + content.strip(), {"section": "body"}, meta,
                 str(m["subject"] or ""))]


def parse_html(path, rel, parser):
    raw = _read_text(path)
    meta = file_meta(rel, "")
    if parser == "plain":
        return [Unit(f"{rel}#all", rel, "html", "text", raw, {}, meta)]
    t = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", raw)
    t = re.sub(r'(?is)<div id="(nav|banner)".*?</div>', " ", t)
    t = re.sub(r"(?is)<h([1-4])[^>]*>(.*?)</h\1>", lambda m: f"\n@@H{m.group(1)} {re.sub('<[^>]+>', '', m.group(2)).strip()}\n", t)
    t = re.sub(r"(?is)</t[dh]>\s*<t[dh][^>]*>", " | ", t)
    t = re.sub(r"(?is)<br\s*/?>|</p>|</tr>|</li>|</div>", "\n", t)
    t = _html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"[ \t]+", " ", t)
    tm = re.search(r"(?is)<title>(.*?)</title>", raw)
    meta["title"] = _html.unescape(tm.group(1).strip()) if tm else pathlib.Path(rel).stem
    return _split_headings(rel, "html", t, meta, r"^@@H(\d) (.*)$")


def _split_headings(rel, fmt, text, meta, pattern):
    units, stack, buf = [], [], []

    def flush():
        s = "\n".join(x for x in buf if x.strip()).strip()
        if s:
            units.append(Unit(f"{rel}#s{len(units)}", rel, fmt, "text", s, {"section": stack[-1][1] if stack else ""},
                              meta, " › ".join(h for _, h in stack)))
        buf.clear()

    for line in text.splitlines():
        m = re.match(pattern, line.strip())
        if m:
            flush()
            lv = len(m.group(1)) if not m.group(1).isdigit() else int(m.group(1))
            while stack and stack[-1][0] >= lv:
                stack.pop()
            stack.append((lv, m.group(2).strip()))
            buf.append(m.group(2).strip())
        else:
            buf.append(line.rstrip())
    flush()
    return units


def parse_md(path, rel, parser):
    raw = _read_text(path)
    meta = file_meta(rel, raw[:1500])
    if parser == "plain":
        return [Unit(f"{rel}#all", rel, "md", "text", raw, {}, meta)]
    m = re.search(r"(?m)^#\s+(.+)$", raw)
    if m:
        meta["title"] = m.group(1).strip()[:120]
    return _split_headings(rel, "md", raw, meta, r"^(#{1,4})\s+(.*)$")


def parse_text(path, rel, parser):
    raw = _read_text(path)
    return [Unit(f"{rel}#all", rel, fmt_of(rel), "text", raw, {}, file_meta(rel, raw[:1500]))]


PARSE_BY_FMT = {"pdf": parse_pdf, "docx": parse_docx, "xlsx": parse_xlsx, "csv": parse_csv, "yaml": parse_yaml,
                "yml": parse_yaml, "xml": parse_xml, "wsdl": parse_xml, "eml": parse_eml, "html": parse_html,
                "htm": parse_html, "md": parse_md}


def parse_file(root, rel: str, parser: str = "structured") -> list[Unit]:
    """Parse one file. Never raises: a failure returns [] and is recorded in parse_file.failures."""
    path = os.path.join(root, rel)
    fn = PARSE_BY_FMT.get(fmt_of(rel), parse_text)
    try:
        units = fn(path, rel, parser)
    except Exception as e:  # noqa: BLE001
        parse_file.failures.append({"file": rel, "parser": parser, "error": f"{type(e).__name__}: {e}"[:300]})
        return []
    for u in units:
        if u.meta is None:
            u.meta = file_meta(rel, "")
        u.meta.setdefault("fmt_class", FMT_CLASS.get(u.fmt, "unstructured"))
        u.meta["parser"] = parser
    return units


parse_file.failures = []


def _parse_one(args):
    root, rel, parser = args
    parse_file.failures = []
    units = parse_file(root, rel, parser)
    return [u.to_json() for u in units], parse_file.failures


def parse(root=None, parser: str = "structured", workers: int | None = None, cache: bool = True,
          files: list[str] | None = None) -> list[Unit]:
    """Parse the whole dump (every file except eval/). Cached as gzip JSONL under CACHE_DIR, keyed by the dump's
    file list and sizes, so a second call is instant. parse.failures holds the files that could not be parsed."""
    assert parser in PARSERS, parser
    root = dump_root(root)
    rels = files or list_files(root)
    sig = hashlib.sha1(json.dumps([(r, os.path.getsize(root / r)) for r in rels] + [parser, PARSER_VERSION]).encode()).hexdigest()[:12]
    cp = CACHE_DIR / f"units_{parser}_{sig}.jsonl.gz"
    if cache and cp.exists():
        rows = [json.loads(l) for l in gzip.open(cp, "rt", encoding="utf-8")]
        parse.failures = [r["failure"] for r in rows if "failure" in r]
        return [Unit(**r) for r in rows if "failure" not in r]
    jobs = [(str(root), r, parser) for r in rels]
    if workers is None:
        workers = min(8, os.cpu_count() or 1)
    results = []
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(workers) as ex:
            results = list(ex.map(_parse_one, jobs, chunksize=4))
    else:
        results = [_parse_one(j) for j in jobs]
    units, fails = [], []
    for us, fs in results:
        units += [Unit(**u) for u in us]
        fails += fs
    parse.failures = fails
    if cache:
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            tmp = cp.with_suffix(".tmp")
            with gzip.open(tmp, "wt", encoding="utf-8") as f:
                for u in units:
                    f.write(json.dumps(u.to_json(), ensure_ascii=False) + "\n")
                for x in fails:
                    f.write(json.dumps({"failure": x}) + "\n")
            os.replace(tmp, cp)
        except OSError:
            pass
    return units


parse.failures = []


# =============================================================================== chunking
def _header(meta: dict, heading: str) -> str:
    """The context header a structured chunk carries: document, version, status, and where in the document."""
    name = meta.get("title") or pathlib.Path(meta.get("file", "")).name
    bits = [name]
    if meta.get("doc_id") and meta["doc_id"] not in name:
        bits.append(meta["doc_id"])
    if meta.get("version"):
        bits.append("v" + meta["version"])
    if meta.get("effective"):
        bits.append("effective " + meta["effective"])
    st = status_line(meta)
    h = f"[{' · '.join(bits)}{' · ' + st if st else ''}]"
    if heading:
        h += f"\n[{heading[:200]}]"
    return h


def _merge_locs(units: list[Unit]) -> dict:
    pages, sections, services, rows = [], [], [], {}
    for u in units:
        l = u.loc
        if l.get("page") and l["page"] not in pages:
            pages.append(l["page"])
        if l.get("section") and l["section"] not in sections:
            sections.append(l["section"])
        if l.get("service") and l["service"] not in services:
            services.append(l["service"])
        if l.get("row"):
            k = l.get("sheet") or ""
            a, b = rows.get(k, (l["row"], l["row"]))
            rows[k] = (min(a, l["row"]), max(b, l["row"]))
    out = {}
    if pages:
        out["pages"] = sorted(pages)
    if sections:
        out["sections"] = sections
    if services:
        out["services"] = services
    if rows:
        out["rows"] = {k: [a, b] for k, (a, b) in rows.items()}
    return out


def _by_file(units: list[Unit]) -> dict[str, list[Unit]]:
    out: dict[str, list[Unit]] = {}
    for u in units:
        out.setdefault(u.file, []).append(u)
    return out


def _stream(units: list[Unit], sep="\n"):
    """Concatenate a file's units, remembering each unit's character span."""
    parts, spans, pos = [], [], 0
    for u in units:
        t = u.text
        parts.append(t)
        spans.append((pos, pos + len(t)))
        pos += len(t) + len(sep)
    return sep.join(parts), spans


def _units_in(spans, a, b):
    return [i for i, (s, e) in enumerate(spans) if s < b and e > a] or [max(0, min(len(spans) - 1, next((i for i, (s, e) in enumerate(spans) if e >= a), 0)))]


def _fixed_windows(text: str, size: int, overlap: float):
    """Token windows of `size` with `overlap` (fraction). Returns (char_start, char_end, text) per window."""
    enc = _enc()
    toks = enc.encode(text, disallowed_special=())
    if not toks:
        return []
    step = max(1, int(size * (1 - overlap)))
    # character offset of every token boundary (decode_with_offsets keeps the mapping exact)
    try:
        _, offs = enc.decode_with_offsets(toks)
    except Exception:  # noqa: BLE001
        offs = None
    out = []
    for s in range(0, len(toks), step):
        piece = toks[s:s + size]
        t = enc.decode(piece)
        if offs is not None:
            a = offs[s]
            b = offs[s + len(piece)] if s + len(piece) < len(offs) else len(text)
        else:
            a, b = 0, len(text)
        out.append((a, b, t))
        if s + size >= len(toks):
            break
    return out


SEPS = ["\n\n", "\n", ". ", "; ", " "]


def _recursive_split(text: str, size: int, seps=SEPS) -> list[str]:
    """Split on the coarsest separator that works, recursing into pieces still longer than `size` tokens."""
    if n_tokens(text) <= size:
        return [text]
    for i, sep in enumerate(seps):
        if sep in text:
            parts = text.split(sep)
            parts = [p + (sep if j < len(parts) - 1 else "") for j, p in enumerate(parts)]
            out = []
            for p in parts:
                if n_tokens(p) > size:
                    out += _recursive_split(p, size, seps[i + 1:])
                elif p:
                    out.append(p)
            return out
    toks = encode(text)
    return [decode(toks[i:i + size]) for i in range(0, len(toks), size)]


def _merge_pieces(pieces: list[str], size: int, overlap: float) -> list[str]:
    """Greedy merge of small pieces up to `size` tokens; each chunk starts with the tail of the last one (overlap)."""
    out, cur, cur_lens, cur_n = [], [], [], 0
    ov = int(size * overlap)
    lens = [n_tokens(p) for p in pieces]
    for p, n in zip(pieces, lens):
        if cur and cur_n + n > size:
            out.append("".join(cur))
            if ov:
                keep, kn = [], 0
                for q, qn in zip(reversed(cur), reversed(cur_lens)):
                    if kn + qn > ov:
                        break
                    keep.insert(0, q)
                    kn += qn
                cur, cur_lens, cur_n = keep, [n_tokens(q) for q in keep], kn
            else:
                cur, cur_lens, cur_n = [], [], 0
        cur.append(p)
        cur_lens.append(n)
        cur_n += n
    if cur:
        out.append("".join(cur))
    return out


def _locate(stream: str, spans, piece: str, hint: int) -> tuple[int, int]:
    i = stream.find(piece[:200], max(0, hint - 50))
    if i < 0:
        i = stream.find(piece[:60])
    if i < 0:
        i = hint
    return i, i + len(piece)


def chunk(units: list[Unit], method: str = "structure", size: int = 400, overlap: float = 0.0,
          context: bool | None = None) -> list[Chunk]:
    """Cut units into chunks of about `size` o200k tokens.
      fixed      token windows over each file's text, blind to structure (overlap = fraction of size)
      recursive  split on paragraph, line, sentence, word boundaries, then merge pieces up to size (LangChain-style)
      structure  pack whole structural units (a section, a table row, a service, an e-mail) up to size, never cutting
                 one unless it alone is longer than size (then split recursively, with the overlap); never across
                 a sheet or a file
    context: prefix the document header (title, id, version, effective date, status, heading) to the embedded text.
             Default: on for units from the structured parser, off for the plain parser."""
    assert method in CHUNKERS, method
    out: list[Chunk] = []
    for rel, us in _by_file(units).items():
        meta = dict(us[0].meta)
        structured = context if context is not None else meta.get("parser") == "structured"
        bodies: list[tuple[str, list[Unit], str]] = []  # (text, units it came from, heading)
        if method in ("fixed", "recursive"):
            stream, spans = _stream(us)
            if method == "fixed":
                for a, b, t in _fixed_windows(stream, size, overlap):
                    idx = _units_in(spans, a, b)
                    bodies.append((t, [us[i] for i in idx], us[idx[0]].heading))
            else:
                pieces = _merge_pieces(_recursive_split(stream, size), size, overlap)
                pos = 0
                for p in pieces:
                    a, b = _locate(stream, spans, p, pos)
                    pos = max(pos, a + 1)
                    idx = _units_in(spans, a, b)
                    bodies.append((p, [us[i] for i in idx], us[idx[0]].heading))
        else:
            groups: list[list[Unit]] = []
            gtok: list[int] = []
            for u in us:
                un = n_tokens(u.text)
                if groups and groups[-1][-1].loc.get("sheet") == u.loc.get("sheet") and gtok[-1] + un <= size:
                    groups[-1].append(u)
                    gtok[-1] += un
                else:
                    groups.append([u])
                    gtok.append(un)
            for g, gn in zip(groups, gtok):
                if gn > size:
                    stream, spans = _stream(g)
                    pieces = _merge_pieces(_recursive_split(stream, size), size, overlap)
                    pos = 0
                    for p in pieces:
                        a, b = _locate(stream, spans, p, pos)
                        pos = max(pos, a + 1)
                        idx = _units_in(spans, a, b)
                        bodies.append((p, [g[i] for i in idx], g[idx[0]].heading))
                else:
                    bodies.append(("\n".join(x.text for x in g), g, g[0].heading))
        for i, (t, src, heading) in enumerate(bodies):
            t = t.strip()
            if not t:
                continue
            locs = _merge_locs(src)
            head = _header(meta, heading) if structured else ""
            full = (head + "\n" + t) if head else t
            out.append(Chunk(f"{rel}#c{i}", rel, full, t, locs, meta, n_tokens(full)))
    return out


def chunking_id(parser: str, method: str, size: int, overlap: float) -> str:
    return f"{parser}-{method}-{size}-o{int(round(overlap * 100))}"


# =============================================================================== quick look
def describe(units: list[Unit]) -> dict:
    by = {}
    for u in units:
        d = by.setdefault(u.fmt, {"units": 0, "files": set(), "tokens": 0})
        d["units"] += 1
        d["files"].add(u.file)
        d["tokens"] += n_tokens(u.text)
    return {k: {"units": v["units"], "files": len(v["files"]), "tokens": v["tokens"]} for k, v in sorted(by.items())}
