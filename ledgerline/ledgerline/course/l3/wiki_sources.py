"""Lecture 3, the LLM Wiki: reading the raw sources (layer 1) the way the wiki's ingest needs them.

    from ledgerline.course.l3 import wiki_sources as WS
    srcs = WS.load_sources("/path/to/northbridge-docs")      # one Source per file, with units (pages / sheets / body)
    reg = WS.build_registry(srcs)                            # the page namespace seeded from Northbridge's own codes

Why a reader of our own: the ingest needs a *source* view (a whole file, its metadata, its pages in order, its
tables as profiles plus the rows of entities the prose talks about), while the RAG half needs *chunks*. Text is
extracted the same way as eval/check_gold.py (pypdf, tesseract OCR for image-only scans, python-docx, openpyxl,
csv, the e-mail parser, HTML without tags), so a fact the gold checker finds at page N is at page N here too.
Runs on Modal (the parsing libraries are not installed on the laptop).
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
from dataclasses import dataclass, field

TODAY = "2026-10-26"
DUMP = os.environ.get("NB_DOCS", "/Users/raj/Claude_Brain/northbridge-docs")
HR_DIR = "01_policies/HR/CONFIDENTIAL/"
DOC_CODE = re.compile(r"\b(POL-[A-Z]{2,3}-\d{3}|AMD-[A-Z]{3}-\d{4}-\d{2}|SOP-[A-Z]{2,3}-\d{3}|MAN-[A-Z]{2,3}-72|"
                      r"HR-CONF-\d{3}|QRC-\d{2}|BHT-\d{2}|RN-7\.\d(?:\.\d)?(?:-P\d)?)\b")
CODEISH = re.compile(r"\b[A-Z]{2,4}(?:-[A-Z0-9]{1,6}){1,3}\b")


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


@dataclass
class Unit:
    loc: str                 # "p. 3", "sheet Suppliers rows 1-120", "body", "whole file"
    text: str
    page: int | None = None
    sheet: str | None = None


@dataclass
class Table:
    sheet: str
    title_rows: list[str]
    header: list[str]
    rows: list[list[str]]    # data rows only

    def key_col(self) -> int:
        return 0


@dataclass
class Source:
    file: str
    fmt: str
    folder: str
    title: str
    meta: dict = field(default_factory=dict)
    units: list[Unit] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    audience: str = "staff"
    status: str = "current"   # current | superseded | future | email | meeting | scan | duplicate-file
    date: str = ""
    empty: bool = False

    @property
    def is_table(self) -> bool:
        return bool(self.tables)

    @property
    def text(self) -> str:
        return "\n".join(u.text for u in self.units)

    @property
    def doc_code(self) -> str | None:
        return self.meta.get("doc")

    def header(self) -> str:
        m = self.meta
        bits = [f"file: {self.file}", f"format: {self.fmt}", f"folder: {self.folder}"]
        if m.get("doc"):
            bits.append(f"document: {m['doc']} v{m.get('version', '?')}")
        if m.get("effective"):
            bits.append(f"effective: {m['effective']}")
        if m.get("doc_status"):
            bits.append(f"status in the document: {m['doc_status']}")
        if self.date:
            bits.append(f"date: {self.date}")
        bits.append(f"status for the wiki today ({TODAY}): {self.status}")
        bits.append(f"audience: {self.audience}")
        return "\n".join(bits)


# ------------------------------------------------------------------------------------------------ extraction
def _strip_running(pages):
    """eval/check_gold.py's rule: drop running headers/footers and 'Page x of y'."""
    n = len(pages)
    freq = {}
    for p in pages:
        for ln in set(p.splitlines()):
            freq[ln] = freq.get(ln, 0) + 1
    out = []
    for p in pages:
        lines = p.splitlines()
        tail = max(0, len(lines) - 6)
        keep = [ln for i, ln in enumerate(lines) if not re.fullmatch(r"\s*Page \d+ of \d+\s*", ln)
                and not (i >= tail and n >= 2 and freq.get(ln, 0) >= max(2, 0.6 * n) and len(ln) < 120)]
        out.append("\n".join(keep))
    return out


def _pdf_pages(path):
    from pypdf import PdfReader

    r = PdfReader(path)
    pages = [(p.extract_text() or "") for p in r.pages]
    if sum(len(p.strip()) for p in pages) < 20:
        try:
            import pytesseract

            ocr = []
            for p in r.pages:
                ocr.append("\n".join(pytesseract.image_to_string(im.image) for im in p.images))
            return ocr, True
        except Exception:
            return pages, True
    return _strip_running(pages), False


def _s(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}" if v != int(v) or abs(v) >= 1e7 else f"{int(v)}"
    return str(v).strip()


def _split_table(sheet: str, rows: list[list[str]]) -> Table:
    """Title rows above the header, then the header (first row filled in at least 60% of the widest row)."""
    rows = [r for r in rows if any(c for c in r)]
    width = max((sum(1 for c in r if c) for r in rows), default=0)
    hi = 0
    for i, r in enumerate(rows[:8]):
        filled = sum(1 for c in r if c)
        if width and filled >= max(2, 0.6 * width) and all(not re.fullmatch(r"-?\d+(\.\d+)?", c) for c in r if c):
            # a group-label row ("Identification | Classification ...") is followed by the real header
            nxt = rows[i + 1] if i + 1 < len(rows) else []
            if sum(1 for c in r if c) < 0.9 * width and sum(1 for c in nxt if c) >= 0.9 * width and \
                    all(not re.fullmatch(r"-?\d+(\.\d+)?", c) for c in nxt if c):
                continue
            hi = i
            break
    title = [" ".join(c for c in r if c) for r in rows[:hi]]
    header = rows[hi] if rows else []
    return Table(sheet, title, header, rows[hi + 1:])


def _xlsx_tables(path):
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        rows = [[_s(c) for c in r] for r in ws.iter_rows(values_only=True)]
        out.append(_split_table(ws.title, rows))
    return out


def _csv_table(path):
    raw = open(path, "rb").read()
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        txt = raw.decode("latin-1")
    rows = [[c.strip() for c in r] for r in csv.reader(io.StringIO(txt))]
    return [_split_table("csv", rows)]


def _docx_text(path):
    import docx

    d = docx.Document(path)
    parts = []
    for p in d.paragraphs:
        st = (p.style.name or "") if p.style is not None else ""
        m = re.match(r"Heading (\d)", st)
        if m and p.text.strip():
            parts.append("#" * int(m.group(1)) + " " + p.text.strip())
        elif st == "Title" and p.text.strip():
            parts.append("# " + p.text.strip())
        else:
            parts.append(p.text)
    for t in d.tables:
        for row in t.rows:
            parts.append(" | ".join(c.text for c in row.cells))
    return "\n".join(parts)


def _eml(path):
    m = email.message_from_bytes(open(path, "rb").read(), policy=email.policy.default)
    body = m.get_body(preferencelist=("plain",))
    head = f"Subject: {m['subject']}\nFrom: {m['from']}\nTo: {m['to']}\nCc: {m['cc'] or ''}\nDate: {m['date']}\n"
    return head + "\n" + (body.get_content() if body else ""), m


def _meta_from_text(t: str) -> dict:
    """The 'Field / Value' block every controlled document starts with."""
    meta = {}
    for k, key in (("Document", "doc"), ("Version", "version"), ("Effective", "effective"), ("Status", "doc_status"),
                   ("Classification", "classification"), ("Owner", "owner")):
        m = re.search(rf"(?:^|\n){k}\n([^\n]+)", t[:2500])
        if m:
            meta[key] = m.group(1).strip().rstrip(",")
    return meta


def read_source(root: str, rel: str) -> Source:
    path = os.path.join(root, rel)
    ext = rel.rsplit(".", 1)[-1].lower() if "." in rel.rsplit("/", 1)[-1] else "txt"
    folder = rel.split("/")[0] if "/" in rel else "(root)"
    src = Source(rel, ext, folder, rel.rsplit("/", 1)[-1].rsplit(".", 1)[0])
    if ext == "pdf":
        pages, scanned = _pdf_pages(path)
        src.units = [Unit(f"p. {i + 1}", t, page=i + 1) for i, t in enumerate(pages)]
        src.empty = sum(len(p.strip()) for p in pages) < 20
        if scanned:
            src.meta["scan"] = "image-only PDF, text by OCR" if not src.empty else "image-only PDF, no text"
    elif ext == "xlsx":
        src.tables = _xlsx_tables(path)
    elif ext == "csv":
        src.tables = _csv_table(path)
    elif ext == "docx":
        src.units = [Unit("whole file", _docx_text(path))]
    elif ext == "eml":
        t, m = _eml(path)
        src.units = [Unit("body", t)]
        src.title = str(m["subject"])
        try:
            from email.utils import parsedate_to_datetime

            src.date = parsedate_to_datetime(m["date"]).date().isoformat()
        except Exception:
            pass
    elif ext in ("html", "htm"):
        raw = open(path, encoding="utf-8", errors="replace").read()
        links = re.findall(r'href="([^"]+)"', raw)
        txt = _html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", "", raw)))
        txt = re.sub(r"[ \t]+", " ", txt)
        txt = re.sub(r"\n\s*\n+", "\n", txt)
        if links:
            txt += "\n\nLinks on this page: " + ", ".join(links)
        src.units = [Unit("whole file", txt)]
        src.meta["links"] = links
    else:
        raw = open(path, "rb").read()
        try:
            t = raw.decode("utf-8")
        except UnicodeDecodeError:
            t = raw.decode("latin-1")
        src.units = [Unit("whole file", t)]
    first = src.units[0].text if src.units else ""
    src.meta.update(_meta_from_text(first))
    if not src.meta.get("doc"):
        m = DOC_CODE.search(rel) or DOC_CODE.search(first[:600])
        if m:
            src.meta["doc"] = m.group(1)
    if not src.date:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", rel.rsplit("/", 1)[-1])
        src.date = m.group(1) if m else (src.meta.get("effective") or "")
    _classify(src)
    return src


def _classify(src: Source):
    rel, m = src.file, src.meta
    eff = m.get("effective", "")
    st = (m.get("doc_status") or "").upper()
    if rel.startswith(HR_DIR):
        src.audience = "hr"
    if src.empty:
        src.status = "scan"
    elif "/old/" in rel or st.startswith("SUPERSEDED") or re.search(r"EXPORT_2024|export_2025", rel):
        src.status = "superseded"
    elif (eff and re.match(r"\d{4}-\d{2}-\d{2}", eff) and eff > TODAY) or st.startswith(("ISSUED", "PREVIEW")):
        src.status = "future"
    elif src.fmt == "eml":
        src.status = "email"
    elif src.folder == "10_meeting_notes":
        src.status = "meeting"
    elif re.search(r"\(\d\)\.\w+$", rel):
        src.status = "duplicate-file"


def all_files(root: str = DUMP) -> list[str]:
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in (".git", "eval")]
        for fn in fns:
            out.append(os.path.relpath(os.path.join(dp, fn), root))
    return sorted(out)


def load_sources(root: str = DUMP, files: list[str] | None = None) -> list[Source]:
    return [read_source(root, f) for f in (files or all_files(root))]


# ------------------------------------------------------------------------------------------------ the registry
DATA_FOLDERS = ("04_service_definitions", "05_master_data", "06_transactions", "07_data_dictionary")


def narrative_text(srcs: list[Source]) -> str:
    """The prose: everything except service definitions, masters, extracts, printed registers and the dictionary."""
    return "\n".join(s.text for s in srcs if not s.is_table and s.folder not in DATA_FOLDERS)


def doc_slug(code: str) -> str:
    code = code.upper()
    if code.startswith("RN-"):
        return "rn-" + slugify(code[3:])
    return slugify(code)


DOC_TYPE = {"POL": "policy", "AMD": "policy", "HR-": "policy", "SOP": "procedure", "MAN": "manual", "RN-": "release",
            "QRC": "training", "BHT": "training"}


def table(src: Source, sheet: str | None = None) -> Table | None:
    for t in src.tables:
        if sheet is None or t.sheet == sheet:
            return t
    return None


def rows_as_dicts(t: Table) -> list[dict]:
    return [dict(zip(t.header, r)) for r in t.rows]


DATA_SLUGS = {
    "05_master_data/ITEM_MASTER_2026-10-26.xlsx": "data-item-master",
    "05_master_data/SUPPLIER_MASTER.xlsx": "data-supplier-master",
    "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx": "data-rate-contracts",
    "05_master_data/Cost Centres and Budgets FY2026-27.xlsx": "data-cost-centres-and-budgets",
    "05_master_data/Users_and_approval_limits.xlsx": "data-users-and-approval-limits",
    "05_master_data/Stock_on_hand_2026-10-26_0900.xlsx": "data-stock-on-hand",
    "05_master_data/Tax codes.xlsx": "data-tax-codes",
    "05_master_data/BOM_master_2026.xlsx": "data-bom-master",
    "05_master_data/Customers (bike shops).xlsx": "data-customers",
    "05_master_data/Price list PL-UK-RTL 2026.xlsx": "data-price-list-pl-uk-rtl",
    "05_master_data/Payment terms.csv": "data-payment-terms",
    "05_master_data/Units of measure.csv": "data-units-of-measure",
    "05_master_data/Warehouses.csv": "data-warehouses",
    "05_master_data/old/item_master_export_2025-03.csv": "data-item-master",
    "05_master_data/supplier_master_EXPORT_2024.csv": "data-supplier-master",
    "06_transactions/AP_invoices_2026.xlsx": "data-ap-invoices-2026",
    "06_transactions/GRN_register_2026.xlsx": "data-grn-register-2026",
    "06_transactions/PO_extract_2026-01_to_2026-10.xlsx": "data-po-extract-2026",
    "06_transactions/PR_extract_2026.csv": "data-pr-extract-2026",
    "06_transactions/sales_orders_2026.csv": "data-sales-orders-2026",
    "06_transactions/stock_ledger_2026-Q3.csv": "data-stock-ledger-2026-q3",
    "07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx": "data-data-dictionary",
    "07_data_dictionary/code_lists.csv": "data-data-dictionary",
    "04_service_definitions/service_index.csv": "data-service-index",
    "08_release_notes/NBC_customisations_and_patch_log.xlsx": "data-nbc-change-log",
    "12_integrations/Integration inventory.xlsx": "data-integration-inventory",
    "01_policies/HR/CONFIDENTIAL/HR-CONF-009 Disciplinary register 2026.xlsx": "hr-conf-009",
}


def build_registry(srcs: list[Source]) -> dict:
    """Canonical slugs for the things Northbridge already names with codes. The ingest LLM is told to use them, so
    that 'Voltway Cells', 'VC-EIN-0042' and 'Voltway' in three different sources land on one page."""
    by = {s.file: s for s in srcs}
    narr = narrative_text(srcs)
    narr_codes = set(CODEISH.findall(narr))
    reg: dict[str, dict] = {}

    def add(slug, type_, title, **kw):
        if slug not in reg:
            reg[slug] = {"type": type_, "title": title, **kw}

    # documents with a code: one page per document family (all versions on one page)
    for s in srcs:
        code = s.doc_code
        if not code:
            continue
        t = DOC_TYPE.get(code[:3])
        if t in (None, "training"):
            continue
        first = next((ln.strip() for ln in (s.units[0].text.splitlines() if s.units else []) if ln.strip()), "")
        first = first.lstrip("# ").strip()
        title = first if s.meta.get("version") and 3 < len(first) < 90 else \
            re.sub(r"\s+v?\d+(\.\d+)*.*$", "", s.title.replace("_", " "))
        aud = "hr" if s.file.startswith(HR_DIR) else "staff"
        add(doc_slug(code), t, f"{code} {title.replace(code, '').strip(' _-')}".strip(), audience=aud)
    add("rn-ll6-history", "release", "Ledgerline 6 release history 2004-2012")
    # structured files
    for f, slug in DATA_SLUGS.items():
        if f in by:
            add(slug, "data-source" if not slug.startswith("hr-") else "policy", by[f].title,
                audience="hr" if f.startswith(HR_DIR) else "staff")
    # people and roles
    u = by.get("05_master_data/Users_and_approval_limits.xlsx")
    if u:
        for r in rows_as_dicts(table(u, "Users")):
            if r.get("user_id"):
                add("user-" + slugify(r["user_id"]), "person", f"{r.get('name')} ({r['user_id']})",
                    note=f"{r.get('title')}, role {r.get('role_cd')}")
        for r in rows_as_dicts(table(u, "Matrix")):
            if r.get("role_cd"):
                add("role-" + slugify(r["role_cd"]), "role", f"Role {r['role_cd']}")
    # suppliers mentioned in narrative sources (by code or by name)
    sm = by.get("05_master_data/SUPPLIER_MASTER.xlsx")
    if sm:
        blocked = {r.get("sup_cd"): r.get("name") for r in rows_as_dicts(table(sm, "Blocked codes"))}
        for r in rows_as_dicts(table(sm, "Suppliers")):
            code, name = r.get("sup_cd", ""), r.get("name", "")
            short = re.sub(r"\s+(Ltd|Limited|B\.V\.|BV|GmbH|Sp\. z o\.o\.|S\.A\.|SAS|plc|& Sons)\.?$", "", name).strip()
            if code in narr_codes or (len(short) > 5 and short in narr):
                add("sup-" + slugify(code), "supplier", f"{short} ({code})", note=f"{r.get('city')}, {r.get('state')}")
        for code, name in blocked.items():
            if code in narr_codes:
                reg.setdefault("_blocked", {"type": "_", "title": "", "codes": {}})["codes"][code] = name
    # cost centres (all), item families, screens, service groups
    cc = by.get("05_master_data/Cost Centres and Budgets FY2026-27.xlsx")
    if cc:
        for r in rows_as_dicts(table(cc, "Cost centres")):
            if r.get("cc_cd"):
                add("cc-" + slugify(r["cc_cd"]), "cost-centre", f"{r['cc_cd']} {r.get('name')}")
    im = by.get("05_master_data/ITEM_MASTER_2026-10-26.xlsx")
    if im:
        t = table(im, "Items")
        fam: dict[str, list] = {}
        for r in t.rows:
            if r and r[0]:
                fam.setdefault(r[0].split("-")[0], []).append(r)
        for p, rs in sorted(fam.items()):
            descr = rs[0][1] if len(rs[0]) > 1 else ""
            add("items-" + slugify(p), "item-family", f"{p}-* items", note=f"{len(rs)} items, e.g. {rs[0][0]} {descr}")
    scr = next((s for s in srcs if s.file.startswith("03_ledgerline_manuals/MAN-SCR-72")), None)
    if scr:
        for code, title in re.findall(r"^([A-Z]{2,3}-[A-Z]{2,4}-\d{2}) ([A-Z][A-Z0-9 ()&/,.'-]+)$", scr.text, re.M):
            add("screen-" + slugify(code), "screen", f"{code} {title.title()}")
    si = by.get("04_service_definitions/service_index.csv")
    if si:
        groups: dict[tuple, list] = {}
        for r in rows_as_dicts(si.tables[0]):
            groups.setdefault((r["module"], r["service"].split("_")[0]), []).append(r["service"])
        for (mod, obj), svcs in sorted(groups.items()):
            add(f"services-{slugify(mod)}-{slugify(obj)}", "service-group", f"{mod} {obj} services",
                note=", ".join(svcs))
    add("services-legacy-6x", "service-group", "Ledgerline 6 RPC definitions (legacy)")
    return reg


ALWAYS = ("policy", "procedure", "manual", "release", "data-source", "role", "topic", "decision")


def registry_keys(reg: dict) -> list[tuple[str, list[str]]]:
    """What to look for in a source to know that a registry entry is relevant to it."""
    out = []
    for slug, r in reg.items():
        if slug.startswith("_") or r["type"] in ALWAYS:
            continue
        t, title = r["type"], r["title"]
        keys = []
        if t == "person":
            m = re.match(r"(.+) \((\w+)\)$", title)
            if m:
                keys = [m.group(1), m.group(2)]
        elif t == "supplier":
            m = re.match(r"(.+?) \(([^)]+)\)$", title)
            keys = [m.group(1)] + ([m.group(2)] if m and re.match(r"[A-Z]", m.group(2)) else []) if m else [title]
        elif t in ("cost-centre", "screen", "error"):
            keys = [title.split(" ")[0]]
        elif t == "item-family":
            keys = [title.split("-")[0] + "-"]
        elif t == "service-group":
            keys = [x.strip() for x in (r.get("note") or "").split(",") if x.strip()]
        out.append((slug, keys))
    return out


def registry_for(text: str, reg: dict, keys: list[tuple[str, list[str]]]) -> str:
    """The registry one ingest call needs: every document and data-source slug, plus the entities this text names."""
    hits = []
    for slug, ks in keys:
        for k in ks:
            if len(k) >= 3 and (re.search(r"(?<![A-Za-z0-9_])" + re.escape(k) + (r"(?![a-z0-9_])" if not k.endswith("-") else ""), text)):
                hits.append(slug)
                break
    sel = {s: reg[s] for s in reg if not s.startswith("_") and (reg[s]["type"] in ALWAYS or s in hits)}
    txt = registry_text(sel)
    if "_blocked" in reg:
        b = {c: n for c, n in reg["_blocked"]["codes"].items() if c in text}
        if b:
            txt += "\nblocked (old) supplier codes, put on the current supplier's page: " + ", ".join(f"{c} = {n}" for c, n in b.items())
    return txt


def registry_text(reg: dict, types: list[str] | None = None) -> str:
    lines = []
    for slug, r in reg.items():
        if slug.startswith("_") or (types and r["type"] not in types):
            continue
        note = f" ({r['note']})" if r.get("note") else ""
        lines.append(f"{slug} | {r['type']} | {r['title']}{note}")
    if "_blocked" in reg:
        lines.append("blocked (old) supplier codes, put on the current supplier's page: " +
                     ", ".join(f"{c} = {n}" for c, n in reg["_blocked"]["codes"].items()))
    return "\n".join(lines)


# ------------------------------------------------------------------------------------------------ ingest units
def table_units(src: Source, focus_codes: set[str], small: int = 60, per_part: int = 60) -> list[Unit]:
    """Structured data as the ingest LLM reads it: per sheet a profile (title rows, columns, size, first rows),
    then every row if the sheet is small, else only the rows whose key the prose mentions (entities that get pages)."""
    units = []
    for t in src.tables:
        prof = [f"SHEET {t.sheet}: {len(t.rows)} data rows, {len(t.header)} columns"]
        if t.title_rows:
            prof.append("title rows: " + " / ".join(t.title_rows))
        prof.append("columns: " + " | ".join(t.header))
        for ci, h in enumerate(t.header[:20]):
            vals = [r[ci] for r in t.rows if ci < len(r) and r[ci]]
            distinct = len(set(vals))
            sample = ", ".join(sorted(set(vals))[:6]) if distinct <= 12 else ", ".join(vals[:3])
            prof.append(f"  {h}: {len(vals)} filled, {distinct} distinct; e.g. {sample}")
        if len(t.rows) <= small:
            chosen = list(enumerate(t.rows))
            prof.append(f"ALL {len(t.rows)} ROWS:")
        else:
            chosen = [(i, r) for i, r in enumerate(t.rows)
                      if any(c in focus_codes for c in r[:3]) or any(c.split("@")[0] in focus_codes for c in r[:1])]
            prof.append(f"first 5 rows, then the {len(chosen)} rows whose key appears in the narrative documents:")
            chosen = [(i, r) for i, r in enumerate(t.rows[:5])] + [x for x in chosen if x[0] >= 5]
        head = "\n".join(prof)
        rows_txt = [f"[sheet {t.sheet}, row {i + 1 + len(t.title_rows) + 1}, key {r[0]}] " +
                    " | ".join(f"{h}={v}" for h, v in zip(t.header, r) if v) for i, r in chosen]
        if not rows_txt:
            units.append(Unit(f"sheet {t.sheet}", head, sheet=t.sheet))
        for k in range(0, len(rows_txt), per_part):
            units.append(Unit(f"sheet {t.sheet}" + (f" part {k // per_part + 1}" if len(rows_txt) > per_part else ""),
                              head + "\n" + "\n".join(rows_txt[k:k + per_part]), sheet=t.sheet))
    return units


def text_parts(src: Source, max_chars: int = 18000) -> list[Unit]:
    """PDF pages grouped into parts of about 4-5k tokens, each page marked [p. N]; other text files split likewise."""
    parts, buf, first, last = [], [], None, None
    for u in src.units:
        t = (f"[{u.loc}]\n" if u.page else "") + u.text
        if buf and sum(len(x) for x in buf) + len(t) > max_chars:
            parts.append(Unit(f"pp. {first}-{last}" if first else "part", "\n".join(buf), page=first))
            buf, first = [], None
        if len(t) > max_chars and not u.page:  # one long non-paged text: cut on blank lines
            chunk = ""
            for para in re.split(r"(\n\s*\n)", t):
                if len(chunk) + len(para) > max_chars and chunk:
                    parts.append(Unit("part", chunk))
                    chunk = ""
                chunk += para
            if chunk:
                buf = [chunk]
            continue
        buf.append(t)
        first = first or u.page
        last = u.page
    if buf:
        parts.append(Unit((f"pp. {first}-{last}" if first and first != last else (f"p. {first}" if first else "whole file")),
                          "\n".join(buf), page=first))
    return parts


def ingest_units(src: Source, focus_codes: set[str]) -> list[Unit]:
    if src.is_table:
        return table_units(src, focus_codes)
    if src.empty:
        return [Unit("whole file", "(image-only scan: no text layer, OCR returned nothing)")]
    big_report = src.file.startswith("06_transactions/reports/") and len(src.units) > 6
    if big_report:  # printed registers: summarised from their first pages, pointer to the extract
        head = src.units[:2]
        return [Unit(f"pp. 1-2 of {len(src.units)}", "\n".join(f"[{u.loc}]\n{u.text}" for u in head) +
                     f"\n\n(printed register, {len(src.units)} pages in all; the rest is more rows of the same table)",
                     page=1)]
    if re.search(r"MAN-(ERR|SCR|SVC)-72|Data Dictionary", src.file):  # dense reference catalogues: smaller parts
        return text_parts(src, max_chars=8000)
    return text_parts(src)


def focus_codes(srcs: list[Source]) -> set[str]:
    return set(CODEISH.findall(narrative_text(srcs)))
