"""Writers for every file type in the dump. All output is byte-for-byte reproducible:
PDFs use reportlab's invariant mode, ZIP-based formats (DOCX, XLSX) are rewritten with fixed timestamps,
e-mails get fixed MIME boundaries, and scans use seeded noise.
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import os
import re
import zipfile

from .model import Book, Doc

FONT_DIR = "/usr/share/fonts/truetype/liberation"
FIXED_DT = (2026, 10, 26, 9, 0, 0)
_fonts_done = False


def _fonts():
    global _fonts_done
    if _fonts_done:
        return
    from reportlab import rl_config
    from reportlab.lib.fonts import addMapping
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    rl_config.invariant = 1
    for fam, base in [("Serif", "LiberationSerif"), ("Sans", "LiberationSans"), ("Mono", "LiberationMono")]:
        for sty, suf in [("", "Regular"), ("-Bold", "Bold"), ("-Italic", "Italic"), ("-BoldItalic", "BoldItalic")]:
            pdfmetrics.registerFont(TTFont(fam + sty, f"{FONT_DIR}/{base}-{suf}.ttf"))
        addMapping(fam, 0, 0, fam)
        addMapping(fam, 1, 0, fam + "-Bold")
        addMapping(fam, 0, 1, fam + "-Italic")
        addMapping(fam, 1, 1, fam + "-BoldItalic")
    _fonts_done = True


def esc(t):
    t = html.escape(str(t), quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", t)
    return t


def plain(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", str(t))
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", t)


# ------------------------------------------------------------------------------------------------ PDF
STYLES = {
    "policy": dict(body="Serif", head="Sans", size=11.2, lead=15.4, margin=66),
    "manual": dict(body="Sans", head="Sans", size=10.4, lead=14.6, margin=62),
    "report": dict(body="Mono", head="Mono", size=8.6, lead=11.0, margin=42),
    "slides": dict(body="Sans", head="Sans", size=17, lead=23, margin=50),
    "qrc": dict(body="Sans", head="Sans", size=9.5, lead=12.4, margin=44),
    "spec": dict(body="Serif", head="Sans", size=10.8, lead=14.8, margin=64),
}


def pdf_bytes(doc: Doc) -> bytes:
    _fonts()
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph,
                                    Preformatted, Spacer, Table, TableStyle)

    st = STYLES[doc.style]
    size = landscape(A4) if doc.landscape or doc.style in ("slides", "report") else A4
    W, H = size
    m = st["margin"]
    body = ParagraphStyle("b", fontName=st["body"], fontSize=st["size"], leading=st["lead"], spaceAfter=st["size"] * 0.55, alignment=TA_LEFT)
    small = ParagraphStyle("s", parent=body, fontSize=st["size"] * 0.82, leading=st["lead"] * 0.82, spaceAfter=0)
    cellst = ParagraphStyle("c", parent=body, fontSize=min(8.6, st["size"] * 0.84), leading=min(10.6, st["lead"] * 0.82), spaceAfter=0)
    hs = {1: ParagraphStyle("h1", fontName=st["head"] + "-Bold", fontSize=st["size"] * 1.55, leading=st["size"] * 1.9, spaceBefore=10, spaceAfter=8),
          2: ParagraphStyle("h2", fontName=st["head"] + "-Bold", fontSize=st["size"] * 1.22, leading=st["size"] * 1.5, spaceBefore=9, spaceAfter=5),
          3: ParagraphStyle("h3", fontName=st["head"] + "-Bold", fontSize=st["size"] * 1.05, leading=st["size"] * 1.3, spaceBefore=6, spaceAfter=3)}
    title_st = ParagraphStyle("t", fontName=st["head"] + "-Bold", fontSize=st["size"] * 2.0, leading=st["size"] * 2.4, spaceAfter=10)
    mono = ParagraphStyle("m", fontName="Mono", fontSize=7.8, leading=9.6)

    company = doc.company
    head_l = f"{company}" if doc.style != "report" else "LEDGERLINE ERP 7.2"
    head_r = " | ".join(x for x in [doc.doc_id, f"v{doc.version}" if doc.version else "", doc.meta.get("header_extra", "")] if x)
    foot_l = {"CONFIDENTIAL": "CONFIDENTIAL. HR only. Do not copy or forward.",
              "INTERNAL": "Internal. Uncontrolled when printed."}.get(doc.classification, doc.classification)
    if doc.status not in ("CURRENT", ""):
        foot_l = f"{doc.status}. " + foot_l

    class NC(canvas.Canvas):
        def __init__(self, *a, **k):
            k["invariant"] = 1
            super().__init__(*a, **k)
            self._pages = []
            self.setTitle(f"{doc.doc_id} {doc.title}".strip())
            self.setAuthor(doc.owner or company)
            self.setSubject(doc.title)
            self.setCreator("Northbridge document control" if doc.style != "report" else "Ledgerline ERP 7.2 print server")

        def showPage(self):
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            n = len(self._pages)
            for i, stt in enumerate(self._pages, 1):
                self.__dict__.update(stt)
                self.setFont(st["head"], 7.5)
                self.setFillColor(colors.HexColor("#444444"))
                self.drawString(m, H - m * 0.55, head_l)
                self.drawRightString(W - m, H - m * 0.55, head_r)
                self.setStrokeColor(colors.HexColor("#999999"))
                self.setLineWidth(0.4)
                self.line(m, H - m * 0.62, W - m, H - m * 0.62)
                self.line(m, m * 0.62, W - m, m * 0.62)
                self.drawString(m, m * 0.45, foot_l[:110])
                self.drawRightString(W - m, m * 0.45, f"Page {i} of {n}")
                if doc.meta.get("watermark"):
                    self.saveState()
                    self.setFont("Sans-Bold", 60)
                    self.setFillColor(colors.Color(0.8, 0.1, 0.1, alpha=0.12))
                    self.translate(W / 2, H / 2)
                    self.rotate(35)
                    self.drawCentredString(0, 0, doc.meta["watermark"])
                    self.restoreState()
                super().showPage()
            super().save()

    buf = io.BytesIO()
    frame = Frame(m, m * 0.8, W - 2 * m, H - 1.6 * m, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    dt_ = BaseDocTemplate(buf, pagesize=size, pageTemplates=[PageTemplate(id="p", frames=[frame])], invariant=1,
                          title=doc.title, author=doc.owner or company)
    story = []

    def tbl(header, rows, widths=None, font=None):
        cst = cellst if not font else ParagraphStyle("cx", parent=cellst, fontName=font)
        avail = W - 2 * m
        n = len(header)
        if widths:
            tot = sum(widths)
            cw = [avail * w / tot for w in widths]
        else:
            lens = [max([len(str(header[i]))] + [min(60, len(str(r[i]))) for r in rows[:200] if i < len(r)]) + 2 for i in range(n)]
            tot = sum(lens)
            cw = [avail * x / tot for x in lens]
        hdr = [Paragraph(f"<b>{esc(h)}</b>", cst) for h in header]
        data = [hdr] + [[Paragraph(esc(c), cst) for c in (r + [""] * n)[:n]] for r in rows]
        t = Table(data, colWidths=cw, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#888888")),
                               ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e4e4e4")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 3),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))
        return t

    if doc.style == "slides":
        story.append(Spacer(1, 90))
        story.append(Paragraph(esc(doc.title), ParagraphStyle("st", parent=title_st, fontSize=34, leading=40)))
        for line in doc.meta.get("cover_lines", []):
            story.append(Paragraph(esc(line), body))
        story.append(PageBreak())
    elif doc.style == "report":
        for line in doc.meta.get("cover_lines", []):
            story.append(Paragraph(esc(line), ParagraphStyle("rl", parent=body, fontName="Mono-Bold")))
        story.append(Spacer(1, 6))
    else:
        story.append(Paragraph(esc(doc.title), title_st))
        meta = [(k, v) for k, v in [("Document", doc.doc_id), ("Version", doc.version), ("Effective", doc.effective),
                                     ("Owner", doc.owner), ("Approved by", doc.approver), ("Status", doc.status),
                                     ("Classification", doc.classification)] if v]
        meta += list(doc.meta.get("cover_extra", []))
        if meta:
            story.append(tbl(["Field", "Value"], [[a, b] for a, b in meta], widths=[1, 3]))
            story.append(Spacer(1, 8))
        if doc.history:
            story.append(Paragraph("<b>Version history</b>", body))
            story.append(tbl(["Version", "Date", "Author", "Change"], doc.history, widths=[1, 1.3, 1.6, 6]))
            story.append(Spacer(1, 8))
        if doc.toc:
            heads = [b[2] for b in doc.blocks if b[0] == "h" and b[1] == 1]
            if heads:
                story.append(Paragraph("<b>Contents</b>", body))
                for hh in heads:
                    story.append(Paragraph(esc(hh), small))
                story.append(PageBreak())
    for b in doc.blocks:
        k = b[0]
        if k == "h":
            story.append(Paragraph(esc(b[2]), hs[min(3, b[1])]))
        elif k == "p":
            story.append(Paragraph(esc(b[1]), small if b[2] == "small" else body))
        elif k == "ul":
            for i, it in enumerate(b[1], 1):
                lab = f"{i}." if b[2] else "•"
                story.append(Paragraph(f"{lab} {esc(it)}", ParagraphStyle("li", parent=body, leftIndent=14, firstLineIndent=-10, spaceAfter=2)))
            story.append(Spacer(1, 4))
        elif k == "table":
            _, header, rows, widths, caption, font = b
            if caption:
                story.append(Paragraph(f"<i>{esc(caption)}</i>", small))
            story.append(tbl(header, rows, widths, font))
            story.append(Spacer(1, 8))
        elif k == "code":
            story.append(Preformatted(b[1], mono))
            story.append(Spacer(1, 6))
        elif k == "pb":
            story.append(PageBreak())
        elif k == "slide":
            _, title, bl, note = b
            parts = [Paragraph(esc(title), ParagraphStyle("sh", parent=hs[1], fontSize=26, leading=32, spaceAfter=14))]
            for it in bl:
                parts.append(Paragraph(f"• {esc(it)}", ParagraphStyle("sb", parent=body, leftIndent=18, firstLineIndent=-14, spaceAfter=7)))
            if note:
                parts.append(Spacer(1, 10))
                parts.append(Paragraph(f"<i>Speaker note: {esc(note)}</i>", ParagraphStyle("sn", parent=body, fontSize=11, leading=14)))
            story.append(KeepTogether(parts))
            story.append(PageBreak())
    dt_.build(story, canvasmaker=NC)
    return buf.getvalue()


# ------------------------------------------------------------------------------------------------ DOCX
def docx_bytes(doc: Doc) -> bytes:
    import datetime as dt

    import docx
    from docx.shared import Pt

    d = docx.Document()
    cp = d.core_properties
    cp.author = doc.meta.get("docx_author", doc.owner or "Northbridge Cycles")
    cp.last_modified_by = doc.meta.get("docx_author", doc.owner or "Northbridge Cycles")
    cp.title = doc.title
    cp.created = dt.datetime(2026, 10, 26, 9, 0, 0)
    cp.modified = dt.datetime(2026, 10, 26, 9, 0, 0)
    cp.revision = 1
    sec = d.sections[0]
    sec.header.paragraphs[0].text = f"{doc.company}    {doc.doc_id}  {('v' + doc.version) if doc.version else ''}".rstrip()
    sec.footer.paragraphs[0].text = {"CONFIDENTIAL": "CONFIDENTIAL. HR only."}.get(doc.classification, "Internal. Uncontrolled when printed.")
    st = d.styles["Normal"]
    st.font.name = "Calibri" if doc.style != "policy" else "Times New Roman"
    st.font.size = Pt(10.5)
    d.add_heading(doc.title, 0)
    meta = [(k, v) for k, v in [("Document", doc.doc_id), ("Version", doc.version), ("Effective", doc.effective),
                                 ("Owner", doc.owner), ("Status", doc.status)] if v]
    if meta:
        t = d.add_table(rows=0, cols=2)
        t.style = "Table Grid"
        for a, b in meta:
            c = t.add_row().cells
            c[0].text, c[1].text = a, b
    if doc.history:
        d.add_paragraph("Version history")
        _docx_table(d, ["Version", "Date", "Author", "Change"], doc.history)
    for b in doc.blocks:
        k = b[0]
        if k == "h":
            d.add_heading(plain(b[2]), min(3, b[1]))
        elif k == "p":
            d.add_paragraph(plain(b[1]))
        elif k == "ul":
            for it in b[1]:
                d.add_paragraph(plain(it), style="List Number" if b[2] else "List Bullet")
        elif k == "table":
            if b[4]:
                d.add_paragraph(plain(b[4]))
            _docx_table(d, b[1], b[2])
        elif k == "code":
            d.add_paragraph(b[1])
        elif k == "pb":
            d.add_page_break()
        elif k == "slide":
            d.add_heading(plain(b[1]), 2)
            for it in b[2]:
                d.add_paragraph(plain(it), style="List Bullet")
    buf = io.BytesIO()
    d.save(buf)
    return normalize_zip(buf.getvalue())


def _docx_table(d, header, rows):
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for i, h in enumerate(header):
        t.rows[0].cells[i].text = plain(h)
    for r in rows:
        c = t.add_row().cells
        for i in range(len(header)):
            c[i].text = plain(r[i]) if i < len(r) else ""


def normalize_zip(data: bytes) -> bytes:
    src = zipfile.ZipFile(io.BytesIO(data))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            b = src.read(info.filename)
            if info.filename == "docProps/core.xml":
                b = re.sub(rb"(<dcterms:(created|modified)[^>]*>)[^<]*(</dcterms:)", rb"\g<1>2026-10-26T09:00:00Z\3", b)
            zi = zipfile.ZipInfo(info.filename, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, b)
    return out.getvalue()


# ------------------------------------------------------------------------------------------------ XLSX / CSV
def xlsx_bytes(book: Book) -> bytes:
    import datetime as dt

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    wb.remove(wb.active)
    wb.properties.creator = book.props.get("creator", "Ledgerline ERP 7.2 export")
    wb.properties.lastModifiedBy = book.props.get("modified_by", wb.properties.creator)
    wb.properties.title = book.props.get("title", "")
    wb.properties.created = dt.datetime(2026, 10, 26, 9, 0, 0)
    wb.properties.modified = dt.datetime(2026, 10, 26, 9, 0, 0)
    bold = Font(bold=True)
    fill = PatternFill("solid", fgColor="DDDDDD")
    for sh in book.sheets:
        ws = wb.create_sheet(sh.name[:31])
        ncol = max(1, len(sh.header))
        r = 1
        for line in sh.title_rows:
            ws.cell(r, 1, line).font = Font(bold=True, size=12 if r == 1 else 10)
            if ncol > 1:
                ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
            r += 1
        if sh.merged_header:
            c = 1
            for label, span in sh.merged_header:
                ws.cell(r, c, label).font = bold
                ws.cell(r, c).alignment = Alignment(horizontal="center")
                ws.cell(r, c).fill = fill
                if span > 1:
                    ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + span - 1)
                c += span
            r += 1
        for ci, h in enumerate(sh.header, 1):
            ws.cell(r, ci, h).font = bold
            ws.cell(r, ci).fill = fill
        for row in sh.rows:
            r += 1
            for ci, v in enumerate(row, 1):
                ws.cell(r, ci, v)
        if sh.freeze and sh.header:
            ws.freeze_panes = ws.cell(sh.header_row + 1, 1)
        for ci in range(1, ncol + 1):
            w = sh.widths[ci - 1] if sh.widths and ci - 1 < len(sh.widths) else min(48, max(8, max([len(str(sh.header[ci - 1]))] + [len(str(x[ci - 1])) for x in sh.rows[:300] if ci - 1 < len(x)]) + 2))
            ws.column_dimensions[get_column_letter(ci)].width = w
    buf = io.BytesIO()
    wb.save(buf)
    return normalize_zip(buf.getvalue())


def csv_bytes(book: Book) -> bytes:
    sh = book.sheets[0]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n" if book.props.get("crlf") else "\n")
    for line in sh.title_rows:
        w.writerow([line])
    w.writerow(sh.header)
    from .model import _s
    for r in sh.rows:
        w.writerow([_s(v) for v in r])
    enc = book.props.get("encoding", "utf-8")
    return buf.getvalue().encode(enc, errors="replace")


# ------------------------------------------------------------------------------------------------ HTML / MD / TXT / EML
def html_bytes(doc: Doc) -> bytes:
    nav = doc.meta.get("nav", [])
    out = ["<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">",
           "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />",
           f"<title>{html.escape(doc.title)} - NBC Intranet</title>",
           "<link rel=\"stylesheet\" href=\"/_layouts/nbc/styles/intranet.css\" type=\"text/css\" /></head>",
           "<body><div id=\"banner\"><img src=\"/_layouts/nbc/images/nbc_logo_2009.gif\" alt=\"Northbridge Cycles\" /> NBC Intranet &raquo; Purchasing</div>",
           "<div id=\"nav\"><ul>"]
    for label, href in nav:
        out.append(f"<li><a href=\"{html.escape(href)}\">{html.escape(label)}</a></li>")
    out.append(f"</ul></div><div id=\"content\"><h1>{html.escape(doc.title)}</h1>")

    def inline(t):
        t = html.escape(str(t), quote=False)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)

    for b in doc.blocks:
        if b[0] == "h":
            out.append(f"<h{b[1] + 1}>{inline(b[2])}</h{b[1] + 1}>")
        elif b[0] == "p":
            out.append(f"<p>{inline(b[1])}</p>")
        elif b[0] == "ul":
            tag = "ol" if b[2] else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in b[1]) + f"</{tag}>")
        elif b[0] == "table":
            out.append("<table border=\"1\" cellpadding=\"3\" class=\"ms-listviewtable\"><tr>" + "".join(f"<th>{inline(h)}</th>" for h in b[1]) + "</tr>")
            for r in b[2]:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append("</table>")
        elif b[0] == "code":
            out.append(f"<pre>{html.escape(b[1])}</pre>")
    out.append(f"</div><div id=\"footer\">{html.escape(doc.meta.get('footer', ''))}</div></body></html>")
    return "\n".join(out).encode("utf-8")


def md_text(doc: Doc) -> str:
    out = []
    if doc.meta.get("frontmatter"):
        out.append("---")
        for k, v in doc.meta["frontmatter"].items():
            out.append(f"{k}: {v}")
        out.append("---\n")
    out.append(f"# {doc.title}\n")
    for b in doc.blocks:
        if b[0] == "h":
            out.append(f"{'#' * (b[1] + 1)} {b[2]}\n")
        elif b[0] == "p":
            out.append(f"{b[1]}\n")
        elif b[0] == "ul":
            out += [f"{i + 1}. {x}" if b[2] else f"- {x}" for i, x in enumerate(b[1])]
            out.append("")
        elif b[0] == "table":
            out.append("| " + " | ".join(b[1]) + " |")
            out.append("|" + "---|" * len(b[1]))
            out += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in b[2]]
            out.append("")
        elif b[0] == "code":
            out.append("```\n" + b[1] + "\n```\n")
        elif b[0] == "slide":
            out.append(f"## {b[1]}\n")
            out += [f"- {x}" for x in b[2]]
            out.append("")
    return "\n".join(out)


def txt_text(doc: Doc) -> str:
    out = [doc.title.upper(), "=" * len(doc.title), ""]
    for b in doc.blocks:
        if b[0] == "h":
            out += ["", plain(b[2]).upper() if b[1] == 1 else plain(b[2]), "-" * len(b[2])]
        elif b[0] == "p":
            out += [plain(b[1]), ""]
        elif b[0] == "ul":
            out += [f"  {'%d.' % (i + 1) if b[2] else '*'} {plain(x)}" for i, x in enumerate(b[1])] + [""]
        elif b[0] == "table":
            widths = [max(len(str(h)), *(len(str(r[i])) for r in b[2] if i < len(r))) for i, h in enumerate(b[1])]
            out.append("  ".join(str(h).ljust(w) for h, w in zip(b[1], widths)))
            out.append("  ".join("-" * w for w in widths))
            out += ["  ".join(str(c).ljust(w) for c, w in zip(r, widths)) for r in b[2]]
            out.append("")
        elif b[0] == "code":
            out += [b[1], ""]
    return "\n".join(out)


def eml_bytes(doc: Doc, attach_render=None) -> bytes:
    from email.message import EmailMessage
    from email.policy import SMTP

    m = doc.meta
    msg = EmailMessage(policy=SMTP)
    msg["From"] = m["from"]
    msg["To"] = m["to"]
    if m.get("cc"):
        msg["Cc"] = m["cc"]
    msg["Date"] = m["date"]
    msg["Subject"] = doc.title
    msg["Message-ID"] = m["message_id"]
    if m.get("in_reply_to"):
        msg["In-Reply-To"] = m["in_reply_to"]
        msg["References"] = m["in_reply_to"]
    if m.get("importance"):
        msg["Importance"] = m["importance"]
    msg["X-Mailer"] = m.get("mailer", "NBC Mail Gateway 4.2")
    body = []
    for b in doc.blocks:
        if b[0] == "p":
            body.append(plain(b[1]))
        elif b[0] == "ul":
            body.append("\n".join(f"{'%d.' % (i + 1) if b[2] else '-'} {plain(x)}" for i, x in enumerate(b[1])))
        elif b[0] == "table":
            body.append("\n".join(" | ".join(map(str, r)) for r in [b[1]] + b[2]))
        elif b[0] == "h":
            body.append(plain(b[2]))
        elif b[0] == "code":
            body.append(b[1])
    if m.get("quoted"):
        body.append("\n".join("> " + ln for ln in m["quoted"].splitlines()))
    msg.set_content("\n\n".join(body) + "\n")
    for fname, data, mime in m.get("attachments", []):
        if callable(data):
            data = data()
        maintype, subtype = mime.split("/")
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=fname)
    if msg.is_multipart():
        msg.set_boundary("=_NBC_" + hashlib.sha1(m["message_id"].encode()).hexdigest()[:24])
    return msg.as_bytes()


# ------------------------------------------------------------------------------------------------ scans (image-only PDF)
def scan_pdf_bytes(pages, seed) -> bytes:
    """pages: list of lists of (text, size_px, bold, x_indent). Rendered as a grey, slightly rotated photocopy."""
    import random

    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    _fonts()
    r = random.Random(seed)
    Wp, Hp = 1654, 2339  # A4 at 200 dpi
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, invariant=1)
    c.setCreator("NBC-SCAN-02 multifunction copier")
    for lines in pages:
        img = Image.new("L", (Wp, Hp), 238)
        dr = ImageDraw.Draw(img)
        y = 150
        for item in lines:
            text, size, bold, indent = (list(item) + [0, False, 0])[:4]
            if text == "<sig>":
                x0 = 260 + indent
                pts = [(x0 + k * 9, y + 30 + int(22 * __import__("math").sin(k / 2.7 + r.random()))) for k in range(36)]
                dr.line(pts, fill=40, width=4)
                y += 80
                continue
            if text == "<stamp>":
                x0 = Wp - 560
                dr.ellipse([x0, y, x0 + 360, y + 200], outline=90, width=6)
                f = ImageFont.truetype(f"{FONT_DIR}/LiberationSans-Bold.ttf", 34)
                dr.text((x0 + 40, y + 80), indent or "RECEIVED", fill=90, font=f)
                y += 220
                continue
            if text == "<hr>":
                dr.line([(150, y + 10), (Wp - 150, y + 10)], fill=60, width=3)
                y += 30
                continue
            f = ImageFont.truetype(f"{FONT_DIR}/{'LiberationSerif-Bold' if bold else 'LiberationSerif-Regular'}.ttf", size or 34)
            dr.text((150 + indent, y), text, fill=r.randint(18, 45), font=f)
            y += int((size or 34) * 1.45)
        for _ in range(2600):
            x, yy = r.randint(0, Wp - 1), r.randint(0, Hp - 1)
            dr.point((x, yy), fill=r.randint(60, 200))
        for _ in range(3):
            yy = r.randint(0, Hp - 1)
            dr.line([(0, yy), (Wp, yy + r.randint(-4, 4))], fill=r.randint(200, 225), width=2)
        img = img.rotate(r.uniform(-0.9, 0.9), resample=Image.BICUBIC, fillcolor=210).filter(ImageFilter.GaussianBlur(0.6))
        jb = io.BytesIO()
        img.save(jb, "JPEG", quality=58, optimize=False)
        c.drawImage(ImageReader(io.BytesIO(jb.getvalue())), 0, 0, width=A4[0], height=A4[1])
        c.showPage()
    c.save()
    return buf.getvalue()


# ------------------------------------------------------------------------------------------------ write
def write(obj, root):
    path = os.path.join(root, obj.path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(obj, Book):
        data = xlsx_bytes(obj) if obj.fmt == "xlsx" else csv_bytes(obj)
    elif obj.raw is not None and obj.fmt not in ("pdf", "docx"):
        data = obj.raw if isinstance(obj.raw, bytes) else obj.raw.encode("utf-8")
    elif obj.fmt == "pdf":
        data = scan_pdf_bytes(obj.meta["scan_pages"], obj.path) if obj.meta.get("scan_pages") else pdf_bytes(obj)
    elif obj.fmt == "docx":
        data = docx_bytes(obj)
    elif obj.fmt in ("html", "htm"):
        data = html_bytes(obj)
    elif obj.fmt == "md":
        data = md_text(obj).encode("utf-8")
    elif obj.fmt == "txt":
        data = txt_text(obj).encode(obj.meta.get("encoding", "utf-8"), errors="replace")
    elif obj.fmt == "eml":
        data = eml_bytes(obj)
    else:
        raise ValueError(obj.path)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)
