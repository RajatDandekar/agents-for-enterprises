"""The document model shared by every builder: a Doc is metadata plus a list of blocks, and facts are planted in it.

A fact is a short exact string (the needle) placed at a known spot. After rendering, the locator finds the page of
every PDF fact; spreadsheet facts carry their sheet and cell from the moment they are written.
"""
from __future__ import annotations

import re


class Facts:
    def __init__(self):
        self.items: list[dict] = []
        self.ids: set[str] = set()

    def add(self, fid, statement, file, needles, mode="present", **loc):
        if fid in self.ids:
            raise ValueError(f"duplicate fact id {fid}")
        self.ids.add(fid)
        if isinstance(needles, str):
            needles = [needles]
        self.items.append(dict(id=fid, statement=statement, file=file, needles=list(needles), mode=mode, loc=loc))
        return fid


FACTS = Facts()


class Doc:
    """A text document (PDF, DOCX, MD, HTML, EML, TXT, YAML, XML)."""

    def __init__(self, path, title, fmt=None, doc_id="", version="", effective="", owner="", approver="",
                 classification="INTERNAL", status="CURRENT", style="policy", history=None, landscape=False,
                 company="Northbridge Cycles Ltd", meta=None, toc=False):
        self.path = path
        self.fmt = fmt or path.rsplit(".", 1)[-1].lower()
        self.title, self.doc_id, self.version, self.effective = title, doc_id, version, effective
        self.owner, self.approver, self.classification, self.status = owner, approver, classification, status
        self.style, self.history, self.landscape, self.company = style, history or [], landscape, company
        self.meta = meta or {}
        self.toc = toc
        self.blocks: list[tuple] = []
        self.section = ""
        self.facts: list[str] = []
        self.raw: str | None = None  # for formats written verbatim (yaml, xml, eml source, txt)

    # blocks
    def h(self, level, text):
        self.blocks.append(("h", level, text))
        self.section = text
        return self

    def p(self, text, style=None):
        self.blocks.append(("p", text, style))
        return self

    def bullets(self, items, numbered=False):
        self.blocks.append(("ul", list(items), numbered))
        return self

    def table(self, header, rows, widths=None, caption=None, font=None):
        self.blocks.append(("table", list(header), [list(map(_s, r)) for r in rows], widths, caption, font))
        return self

    def code(self, text):
        self.blocks.append(("code", text))
        return self

    def pagebreak(self):
        self.blocks.append(("pb",))
        return self

    def slide(self, title, bullets, note=None):
        self.blocks.append(("slide", title, list(bullets), note))
        self.section = title
        return self

    # facts
    def fact(self, fid, statement, needles, section=None, mode="present"):
        FACTS.add(fid, statement, self.path, needles, mode=mode, section=section or self.section, fmt=self.fmt)
        self.facts.append(fid)
        return self

    def pf(self, text, fid, statement, needles=None):
        """A paragraph that carries a fact. The needle defaults to the whole paragraph."""
        self.p(text)
        return self.fact(fid, statement, needles or [text])

    def text(self):
        out = [self.title]
        for b in self.blocks:
            if b[0] in ("h", "p", "code"):
                out.append(b[2] if b[0] == "h" else b[1])
            elif b[0] == "ul":
                out += b[1]
            elif b[0] == "table":
                out.append(" ".join(b[1]))
                out += [" ".join(r) for r in b[2]]
            elif b[0] == "slide":
                out += [b[1]] + b[2]
        return "\n".join(map(str, out))


class Sheet:
    def __init__(self, name, header, rows, title_rows=None, widths=None, merged_header=None, key_col=0, freeze=True):
        self.name, self.header, self.rows = name, list(header), [list(r) for r in rows]
        self.title_rows = title_rows or []   # lines above the header (merged across the width)
        self.merged_header = merged_header   # [(label, n_cols), ...] group row above the header
        self.widths, self.key_col, self.freeze = widths, key_col, freeze

    @property
    def header_row(self):
        return len(self.title_rows) + (1 if self.merged_header else 0) + 1

    def cell(self, key, col):
        """Excel address of the row whose key column equals key, in column col (a header name)."""
        ci = self.header.index(col)
        for i, r in enumerate(self.rows):
            if str(r[self.key_col]) == str(key):
                return f"{_col(ci)}{self.header_row + 1 + i}", r[ci]
        raise KeyError(f"{self.name}: no row {key}")

    def row_no(self, key):
        for i, r in enumerate(self.rows):
            if str(r[self.key_col]) == str(key):
                return self.header_row + 1 + i
        raise KeyError(key)


class Book:
    """A spreadsheet file (XLSX, or CSV when it has one sheet)."""

    def __init__(self, path, sheets, props=None):
        self.path = path
        self.fmt = path.rsplit(".", 1)[-1].lower()
        self.sheets = sheets
        self.props = props or {}
        self.facts = []

    def sheet(self, name):
        return next(s for s in self.sheets if s.name == name)

    def fact(self, fid, statement, sheet, key, col, needle=None, extra=None):
        sh = self.sheet(sheet)
        addr, val = sh.cell(key, col)
        cells = [dict(sheet=sheet, cell=addr, needle=str(needle if needle is not None else _s(val)))]
        for k2, c2 in extra or []:
            a2, v2 = sh.cell(k2, c2)
            cells.append(dict(sheet=sheet, cell=a2, needle=_s(v2)))
        FACTS.add(fid, statement, self.path, [c["needle"] for c in cells], fmt=self.fmt, cells=cells, sheet=sheet,
                  row=sh.row_no(key))
        self.facts.append(fid)
        return self

    def absent(self, fid, statement, sheet, needle):
        FACTS.add(fid, statement, self.path, [needle], mode="absent", fmt=self.fmt, sheet=sheet)
        self.facts.append(fid)


def _col(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def _s(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}" if abs(v) < 1e7 else f"{v:.0f}"
    return str(v)


def money(x, pence=True):
    return f"£{x:,.2f}" if pence else f"£{x:,.0f}"


def norm(s: str) -> str:
    """The normal form used to compare a needle with extracted text: lower case, no whitespace, plain quotes."""
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ").replace("­", "")
    s = re.sub(r"\*\*|__", "", s)
    return re.sub(r"\s+", "", s).lower()
