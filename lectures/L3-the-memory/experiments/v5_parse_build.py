"""L3 v5 · parsing section: assemble the deck's data from the Modal logs (no compute here, only JSON and text).

    /Users/raj/.venv/bin/python lectures/L3-the-memory/experiments/v5_parse_build.py

Reads   logs/v5_parse_explore.json (both parsers on the candidate files), logs/v5_parse_render.json (images, boxes),
        logs/v5_parse_ocr.json (Tesseract vs gemini-3.8-flash), logs/v5_parse_checks.json (facts, metadata, chunks),
        the dump's eval/questions.jsonl and the raw text of two e-mails (shown as they are).
Writes  v5/parse_data.js (window.L3V5.parse) and logs/v5_parse.json (the same data, the record of what the deck shows).
Every text on the slides is cut from a parser's real output; cuts are marked with ⋯.
"""
import json
import pathlib
import quopri
import re
import statistics

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
V5 = HERE.parent / "v5"
DUMP = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")

X = json.loads((LOGS / "v5_parse_explore.json").read_text())
R = json.loads((LOGS / "v5_parse_render.json").read_text())
O = json.loads((LOGS / "v5_parse_ocr.json").read_text())
K = json.loads((LOGS / "v5_parse_checks.json").read_text())
A = json.loads((LOGS / "audit.json").read_text())
Q = {q["id"]: q for q in (json.loads(l) for l in open(DUMP / "eval" / "questions.jsonl") if l.strip())}

APR, PUR = "01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"
SCAN = "99_scans/2026_signed_approval_PO-2026-00452.pdf"
ITEM = "05_master_data/ITEM_MASTER_2026-10-26.xlsx"
EML = "09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml"
APR2 = "01_policies/old/Approval_Matrix_v2.0_2024.docx"
INTRA = "11_training/intranet_export_2016/approval_limits.html"


def between(text, a, b=None, incl=True):
    i = text.index(a)
    j = (text.index(b, i) + (len(b) if incl else 0)) if b else len(text)
    return text[i:j]


def lines_before(text, a):
    return text[: text.index(a)].count("\n")


def img(key, name, **kw):
    im = dict(R[key]["images"][name])
    im.update(kw)
    return im


def q(qid, short=None):
    x = Q[qid]
    return {"id": qid, "question": x["question"], "answer": short or x["reference_answer"], "type": x["type"],
            "gold": [{k: v for k, v in g.items() if k in ("file", "page", "section", "sheet", "row")} for g in x["gold_sources"]]}


files, nums = {}, {}

# ---------------------------------------------------------------- 1 · a table in a native PDF
pl = X[APR]["plain"]["units"][0]["text"]
st = next(u for u in X[APR]["structured"]["units"] if u["loc"].get("section") == "3. The limits")
files["apr"] = {
    "file": APR, "q": q("Q-605", "£250,000 gross, under approval matrix v3.0 (page 1, § 3. The limits)."),
    "images": {"crop": img("apr", "crop", alt="Approval Matrix v3.0, page 1, section 3: the limits table")},
    "texts": {
        "naive": {"title": "Naive · pypdf, parser=\"plain\"", "sub": "page 1 as one string", "cls": "b", "fs": 15, "cols": 2,
                  "text": f"⋯ {lines_before(pl, '3. The limits')} lines of page 1 above\n" + between(pl, "3. The limits", "no approval authority") + "\n⋯",
                  "marks": [{"s": "Role code\nRole\nLimit (gross incl. VAT)", "k": 1, "cls": "g"}, {"s": "£250,000", "k": 1, "cls": "b"}]},
        "struct": {"title": "Structured · pdfplumber, parser=\"structured\"", "sub": "unit: page 1, § 3", "cls": "a", "fs": 15,
                   "text": between(st["text"], "3. The limits", "no approval authority") + "\n⋯ 3.2 to 3.4 follow in the same unit",
                   "marks": [{"s": "Role code | Role | Limit (gross incl. VAT)", "k": 2, "cls": "g"},
                             {"s": "PUR-EXEC | Purchase executive | £250,000", "k": 2, "cls": "a"}]}},
}
nums["apr"] = {"plain_tokens": X[APR]["plain"]["tokens"], "struct_tokens": X[APR]["structured"]["tokens"],
               "plain_units": X[APR]["plain"]["n_units"], "struct_units": X[APR]["structured"]["n_units"]}

# ---------------------------------------------------------------- 2 · headings, page furniture, units with locations
pp = {p["page"]: p["text"] for p in K["pur_plain_pages"]}
tail = pp[2][pp[2].index("Direct order (DIR)"):]
head3 = "\n".join(pp[3].splitlines()[:2])
u2 = K["units_p2"]
# page 2 as plain hands it on, cut to its headings (each body replaced by "⋯ n clauses") and its last lines
_p2 = pp[2].splitlines()
_heads = [u["first"] for u in u2]
_out, _n, _cur = [], 0, None
for _l in _p2:
    if _l in _heads or _l.startswith("Northbridge Cycles Ltd"):
        if _cur is not None:
            _out.append(f"{_cur} ⋯ {_n} clause{'s' if _n != 1 else ''}" if _n else f"{_cur} ⋯ a table")
        _cur, _n = (_l, 0) if _l in _heads else (None, 0)
        if _l.startswith("Northbridge Cycles Ltd"):
            _out.extend(_p2[_p2.index(_l):])
            break
    elif _cur is not None and __import__("re").match(r"^\d+\.\d+ ", _l):
        _n += 1
PP2_OUTLINE = "\n".join(_out)
PP2_TOK = next(p["tokens"] for p in K["pur_plain_pages"] if p["page"] == 2)
c6 = K["chunk6"]["chunks"][0]
files["pur"] = {
    "file": PUR, "q": q("Q-EMMA", "§ 6.2 and § 6.4. Both sit in one unit: page 2, § 6."),
    "images": {"page": img("pur", "page", alt="Purchase Policy v4.1, page 2"), "crop6": img("pur", "crop6", alt="Purchase Policy v4.1, section 6")},
    "texts": {
        "naive": {"title": "Naive · page 2 is one unit", "sub": f"{PP2_TOK} tokens", "cls": "b", "fs": 14,
                  "text": PP2_OUTLINE,
                  "marks": [{"s": "Northbridge Cycles Ltd\nPOL-PUR-001 | v4.1\nInternal. Uncontrolled when printed.\nPage 2 of 4", "k": 1, "cls": "b"},
                            {"s": "6. Supplier qualification", "k": 3, "cls": "g"}]},
        "units": {"title": "Structured · page 2 units", "sub": f"{K['n_units_pur']} in the policy", "cls": "a", "fs": 15,
                  "text": "\n".join(f"p.{u['loc']['page']}  § {u['loc']['section']:<28} {u['tokens']:>4} tokens" for u in u2),
                  "marks": [{"s": "§ 6. Supplier qualification", "k": 3, "cls": "g"}]}},
}
nums["pur"] = {"n_units": K["n_units_pur"], "n_tokens": K["n_tokens_pur"], "chunk_config": K["chunk6"]["config"],
               "plain_pages": len(K["pur_plain_pages"]), "cite6": c6["cite"]}

# ---------------------------------------------------------------- 3, 4 · the scan, then a poor copy of it
sc = O["pages"][SCAN]
frac = R["scan"]["images"]["orig"]["crop_frac"]


def wbox(words, which, k, cls, label=None, below=False, pad=0.004):
    ws = [w for w in words if w["t"] in which]
    assert ws, which
    x0 = min(w["x"] for w in ws) - pad; y0 = min(w["y"] for w in ws) - pad
    x1 = max(w["x"] + w["w"] for w in ws) + pad; y1 = max(w["y"] + w["h"] for w in ws) + pad
    fw, fh = frac[2] - frac[0], frac[3] - frac[1]
    b = {"x": round((x0 - frac[0]) / fw, 4), "y": round((y0 - frac[1]) / fh, 4), "w": round((x1 - x0) / fw, 4), "h": round((y1 - y0) / fh, 4), "k": k, "cls": cls}
    if label:
        b["label"] = label
    if below:
        b["below"] = True
    return b


wo, wd = sc["original"]["tesseract_words"], sc["degraded"]["tesseract_words"]
orig = img("scan", "orig", alt="Scan of the paper approval of PO/2026/00452")
orig["boxes"] = [wbox(wo, {"of", "Ne"}, 3, "b", "the signature, read as “of Ne”", below=True),
                 wbox(wo, {"PO/2026/00452"}, 3, "a"), wbox(wo, {"Daniel", "Okafor"}, 3, "a")]
deg = img("scan", "degraded", alt="The same page as a poor copy: rotated, low resolution, blurred, speckled")
deg["boxes"] = [wbox(wd, {"PO/2026/00852"}, 1, "x", "00452 read as 00852"), wbox(wd, {"Danlel"}, 1, "x", "Daniel read as Danlel", below=True)]
thumb = img("scan", "thumb", alt="The whole scanned page")
tv_o, tv_d = sc["original"], sc["degraded"]
files["scan"] = {
    "file": SCAN, "q": q("Q-015", "Daniel Okafor approved PO/2026/00452."),
    "images": {"orig": orig, "degraded": deg, "thumb": thumb},
    "texts": {
        "naive": {"title": "Naive · pypdf text layer", "cls": "b", "empty": f"(nothing: {len(sc['plain_text'])} characters. The page is one {sc['embedded_image']['w']} × {sc['embedded_image']['h']} image and has no text layer.)"},
        "tess": {"title": "Structured · Tesseract OCR", "sub": f"Tesseract {O['tesseract']} · {tv_o['tesseract_secs']} s", "cls": "a", "fs": 15,
                 "text": sc["structured_text"],
                 "marks": [{"s": "of Ne", "k": 3, "cls": "b"}, {"s": "PO/2026/00452", "k": 3, "cls": "a"}, {"s": "Daniel Okafor", "k": 3, "cls": "a"}]},
        "tess_bad": {"title": "Tesseract", "sub": f"{tv_d['tesseract_secs']} s on CPU", "cls": "b", "fs": 14,
                     "text": tv_d["tesseract_text"],
                     "marks": [{"s": s, "k": 1, "cls": "b"} for s in ("Arenoyal:", "cory)", "pO", "PO/2026/00852", "Trem:", "BAT-500°", "114,00", "Danlel", "Sn ema saan")]},
        "vision_bad": {"title": "gemini-3.8-flash", "sub": f"{tv_d['vision']['secs']} s · ${tv_d['vision']['usd']:.4f}", "cls": "a", "fs": 15,
                       "text": tv_d["vision"]["text"],
                       "marks": [{"s": "PO/2026/00452", "k": 2, "cls": "a"}, {"s": "Daniel Okafor", "k": 2, "cls": "a"}, {"s": "[signature]", "k": 2, "cls": "g"}]}},
}
runs = [O["pages"][r][v] for r in O["pages"] for v in ("original", "degraded")]
sf = K["scan_facts"]
nums["ocr"] = {
    "model": O["model"], "tesseract": O["tesseract"], "machine": O["machine"], "price": O["price"],
    "page": {"tesseract_secs": tv_d["tesseract_secs"], "vision_secs": tv_d["vision"]["secs"], "vision_usd": tv_d["vision"]["usd"],
             "prompt_tokens": tv_d["vision"]["usage"]["promptTokenCount"], "image_tokens": next(d["tokenCount"] for d in tv_d["vision"]["usage"]["promptTokensDetails"] if d["modality"] == "IMAGE"),
             "out_tokens": tv_d["vision"]["usage"]["candidatesTokenCount"], "thought_tokens": tv_d["vision"]["usage"].get("thoughtsTokenCount", 0)},
    "all12": {"n": len(runs), "tesseract_mean_s": round(statistics.mean(r["tesseract_secs"] for r in runs), 2),
              "vision_mean_s": round(statistics.mean(r["vision"]["secs"] for r in runs), 1),
              "vision_mean_usd": round(statistics.mean(r["vision"]["usd"] for r in runs), 4),
              "vision_total_usd": round(sum(r["vision"]["usd"] for r in runs), 4)},
    "facts": {v: sum(1 for r in sf.values() if r[v]) for v in ("tesseract_original", "vision_original", "tesseract_degraded", "vision_degraded")},
    "n_scans": len(sf),
    "vat_markdown": "**" in O["pages"]["99_scans/2011_VAT_rate_change_memo.pdf"]["degraded"]["vision"]["text"],
    "audit_scan_tokens_plain": A["plain_vs_structured"]["scan_text_tokens_plain"], "audit_scan_tokens_ocr": A["plain_vs_structured"]["scan_text_tokens_structured_ocr"],
}
nums["ocr"]["text"] = {k: f"{v} of {len(sf)}" for k, v in nums["ocr"]["facts"].items()}
nums["ocr"]["page"]["vision_usd_s"] = f"${tv_d['vision']['usd']:.4f}"
nums["ocr"]["all12"]["vision_mean_usd_s"] = f"${nums['ocr']['all12']['vision_mean_usd']:.4f}"

# ---------------------------------------------------------------- 5 · a spreadsheet row
rows = K["rows"]
files["item"] = {
    "file": ITEM, "q": q("Q-401", "3,000: sheet Items, row 5, column reorder_lvl."),
    "images": {"crop": img("item", "crop", alt="ITEM_MASTER, sheet Items, rows 1 to 11, columns A to J")},
    "texts": {
        "naive": {"title": "Naive · parser=\"plain\"", "sub": "row 5 alone; row 4, the headers, is another unit", "cls": "b", "fs": 17, "text": rows["plain"]["5"],
                  "marks": [{"s": " 1 1 3000 600 42 ", "k": 1, "cls": "b"}]},
        "struct": {"title": "Structured · “column: value”", "sub": "unit: sheet Items, row 5", "cls": "a", "fs": 17, "text": rows["structured"]["5"],
                   "marks": [{"s": "reorder_lvl: 3000", "k": 3, "cls": "a"}, {"s": "cell_safety: 1", "k": 3, "cls": "g"}]}},
}
nums["item"] = {"plain_tokens": X[ITEM]["plain"]["tokens"], "struct_tokens": X[ITEM]["structured"]["tokens"],
                "rows_without_headers_dump": A["plain_vs_structured"]["xlsx_rows_without_headers_in_plain"],
                "heading": next(u for u in X[ITEM]["structured"]["units"] if u["loc"].get("row") == 5)["heading"]}

# ---------------------------------------------------------------- 6 · an e-mail
raw = (DUMP / EML).read_text(encoding="utf-8")
eu = X[EML]["structured"]["units"][0]["text"]
files["email"] = {
    "file": EML, "q": q("Q-EMMA", "£104.00 per pack, delivered (DAP) to Manchester."),
    "texts": {
        "raw": {"title": "The file on disk · what parser=\"plain\" indexes", "sub": f"{X[EML]['plain']['tokens']} tokens", "cls": "b", "raw": True, "fs": 13.5, "text": raw.rstrip(),
                "marks": [{"s": "=C2=A3", "k": 1, "cls": "b"}, {"s": "=\n", "k": 4, "cls": "b"},
                          {"s": "Content-Transfer-Encoding: quoted-printable", "k": 5, "cls": "k"},
                          {"s": "Message-ID: <c0e8939f459f7898bbeb@mail.northbridgecycles.example>\nX-Mailer: NBC Mail Gateway 4.2\nContent-Type: text/plain; charset=\"utf-8\"", "k": 6, "cls": "s"},
                          {"s": "MIME-Version: 1.0", "k": 6, "cls": "s"}]},
        "struct": {"title": "Structured · decoded", "sub": f"{X[EML]['structured']['tokens']} tokens", "cls": "a", "fs": 12.8, "text": eu[: eu.index("December 2026.") + len("December 2026.")] + "\n⋯ the signature follows",
                   "marks": [{"s": "Subject: Quotation Q-BE-26-0917 - 36 V 500 Wh battery packs", "k": 6, "cls": "g"},
                             {"s": "From: Julien Marchand <j.marchand@brightcell-energy.example>", "k": 6, "cls": "g"},
                             {"s": "To: Emma Clarke <emma.clarke@northbridgecycles.example>", "k": 6, "cls": "g"}, {"s": "Date: Thu, 22 Oct 2026 16:41:00 +0000", "k": 6, "cls": "g"},
                             {"s": "£104.00 per pack, delivered (DAP) to Manchester", "k": 7, "cls": "a"},
                             {"s": "the new report is expected in December 2026", "k": 7, "cls": "a"}]}},
}
# quoted-printable, decoded by hand on the real bytes (Python's quopri, the same rule the e-mail parser applies)
_body = raw.split("\n\n", 1)[1]
_bl = _body.split("\n")
_li = next(i for i, l in enumerate(_bl) if "=C2=A3" in l)
_line = _bl[_li]
_esc = _line[_line.index("=C2=A3"):_line.index("=C2=A3") + 6]
_bytes = [{"code": "=" + h, "hex": h, "dec": int(h, 16), "bin": format(int(h, 16), "08b")} for h in _esc.split("=")[1:]]
_pound = bytes(int(b["hex"], 16) for b in _bytes).decode("utf-8")
assert _pound == "£" and "£".encode("utf-8").hex(" ").upper() == "C2 A3"
_tail = _line[_line.index("mounting:"):]
_join_a, _join_b = _line[_line.rindex(" ") + 1:], _bl[_li + 1].split(" ")[0]
files["email"]["qp"] = {
    "tail": "⋯ " + _tail, "esc": _esc, "bytes": _bytes, "char": _pound, "cp": f"U+{ord(_pound):04X}", "cp_dec": ord(_pound),
    "utf8": "£".encode("utf-8").hex(" ").upper(),
    "decoded_tail": quopri.decodestring(_tail.encode()).decode("utf-8").rstrip("="),
    "join_a": _join_a, "join_b": _join_b, "joined": quopri.decodestring((_join_a + "\n" + _join_b).encode()).decode("utf-8"),
    "soft_breaks": raw.count("=\n"), "max_line": max(len(l) for l in _bl), "mailer": "NBC Mail Gateway 4.2",
    "cte": "Content-Transfer-Encoding: quoted-printable"}
assert "X-Mailer: NBC Mail Gateway 4.2" in raw and files["email"]["qp"]["cte"] in raw
nums["email"] = {"soft_breaks": raw.count("=\n"), "soft_breaks_dump": A["plain_vs_structured"]["eml_quoted_printable_soft_breaks_in_plain"],
                 "meta": {k: X[EML]["structured"]["meta"][k] for k in ("title", "effective")},
                 "plain_finds": K["facts"]["email"]["plain"], "struct_finds": K["facts"]["email"]["structured"]}

# ---------------------------------------------------------------- 7 · a Word document with tables
p2 = X[APR2]["plain"]["units"][0]["text"]
s2 = X[APR2]["structured"]["units"]
files["apr2"] = {
    "file": APR2, "q": q("Q-605", "Now £250,000 gross (v3.0). The superseded v2.0 of 2024 said £200,000."),
    "images": {"page": img("apr2", "page", alt="Approval Matrix v2.0 (Word), page 1")},
    "texts": {
        "naive": {"title": "Naive · paragraphs only, parser=\"plain\"", "sub": f"{X[APR2]['plain']['tokens']} tokens", "cls": "b", "fs": 15,
                  "text": "\n".join(p2.splitlines()[:5]) + "\n⋯",
                  "marks": [{"s": "gross including VAT:\n4. Who may not approve", "k": 1, "cls": "b"}, {"s": "Approval Matrix for Purchasing\n3. The limits", "k": 1, "cls": "b"}]},
        "struct": {"title": "Structured · tables included", "sub": f"{X[APR2]['structured']['tokens']} tokens · {X[APR2]['structured']['n_units']} units", "cls": "a", "fs": 14,
                   "text": "⋯\n" + between(s2[0]["text"], "Document | POL-APR-002", "Status | SUPERSEDED") + "\n\n" + between(s2[1]["text"], "3. The limits", "PUR-EXEC | Purchase executive | £200,000") + "\n⋯ three more rows",
                   "marks": [{"s": "PUR-EXEC | Purchase executive | £200,000", "k": 3, "cls": "a"}, {"s": "Status | SUPERSEDED", "k": 3, "cls": "g"}]}},
}
nums["apr2"] = {"docx_tables_dump": A["plain_vs_structured"]["docx_table_units_dropped_by_plain"],
                "plain_meta": {k: X[APR2]["plain"]["meta"][k] for k in ("doc_id", "version", "status", "superseded")},
                "struct_meta": {k: X[APR2]["structured"]["meta"][k] for k in ("doc_id", "version", "status", "superseded")},
                "f113_plain_tokens": X["02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx"]["plain"]["tokens"],
                "f113_struct_tokens": X["02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx"]["structured"]["tokens"]}

# ---------------------------------------------------------------- 8 · an old intranet page: what a naive HTML parser returns
hraw = (DUMP / INTRA).read_text(encoding="utf-8")
hu = X[INTRA]["structured"]["units"][0]["text"]
H = json.loads((LOGS / "v5_parse_html.json").read_text())
HP = H["pages"]["approval_limits.html"]
gt = re.sub(r"\n\s*\n+", "\n", HP["text"]["bs4_get_text"]).strip()          # blank lines squeezed, nothing else changed
gt_cut = gt[: gt.index("Limits are on the net value before VAT.") + len("Limits are on the net value before VAT.")]
menu = between(gt, "Purchasing home", "Ledgerline 7 training")
pim = img("intra", "page", alt="The 2016 intranet page in a browser")
pim["boxes"] = [dict(bx, k={2: 3, 3: 4}.get(bx["k"], bx["k"])) for bx in pim["boxes"]]
files["intra"] = {
    "file": INTRA, "q": q("Q-605", "In 2016: £150,000, on the net value before VAT. Long superseded."),
    "images": {"page": pim},
    "texts": {
        "naive": {"title": "Naive · BeautifulSoup get_text()", "sub": f"{HP['tokens']['bs4_get_text']} tokens · blank lines removed", "cls": "b", "fs": 13.5, "cols": 2,
                  "text": gt_cut + "\n⋯ then a heading and four paragraphs",
                  "marks": [{"s": HP["title"], "k": 1, "cls": "b"}, {"s": "NBC Intranet » Purchasing", "k": 1, "cls": "b"}, {"s": menu, "k": 1, "cls": "b"},
                            {"s": "RoleLimit", "k": 2, "cls": "b"}, {"s": "Purchase executive£150,000", "k": 2, "cls": "b"}]},
        "struct": {"title": "Structured · text by heading, no banner or menu", "sub": f"{X[INTRA]['structured']['tokens']} tokens · {X[INTRA]['structured']['n_units']} units", "cls": "a", "fs": 13.5,
                   "text": hu[: hu.index("Limits are on the net value before VAT.") + len("Limits are on the net value before VAT.")],
                   "marks": [{"s": " Purchase executive | £150,000", "k": 4, "cls": "a"}, {"s": "Limits are on the net value before VAT.", "k": 4, "cls": "g"}]}},
}
assert gt.startswith(HP["title"]) and "Purchase executive£150,000" in gt
nums["intra"] = {"plain_tokens": X[INTRA]["plain"]["tokens"], "struct_tokens": X[INTRA]["structured"]["tokens"],
                 "bs4_tokens": HP["tokens"]["bs4_get_text"], "n_pages": H["n_pages"], "bs4_version": H["versions"]["beautifulsoup4"],
                 "matches": H["matches"],
                 "nav_links": hraw[hraw.index('<div id="nav">'):hraw.index("</ul></div>")].count("<li>")}

# ---------------------------------------------------------------- Docling, run for real (experiments/v5_parse_docling.py on Modal)
DL = json.loads((LOGS / "v5_parse_docling.json").read_text())
dla = DL["files"]["apr"]["pages_md"]["1"]
dla = dla[dla.index("## 3. The limits"):].rstrip()
_dl = []
for _l in dla.splitlines():
    if _l.startswith(("- 3.2", "- 3.3", "- 3.4")):
        _l = _l[: _l.index(" ", 30)] + " ⋯"
    _dl.append(_l)
dla_cut = "\n".join(_dl)
_tab_first = next(l for l in _dl if l.startswith("| Role code"))
_row_exec = next(l for l in _dl if l.startswith("| PUR-EXEC"))
_scan_md = DL["files"]["scan"]["markdown"].strip()
_our_secs = {k: X[f]["structured"]["secs"] for k, f in (("pur", PUR), ("apr", APR), ("scan", SCAN))}
_split_heading = [u["loc"]["section"] for u in X[PUR]["structured"]["units"] if u["loc"].get("section") == "signed off?"]
_dl_whole = [h for h in DL["files"]["pur"]["section_headers"] if h.endswith("already signed off?")]
assert _split_heading and _dl_whole
_dcrop = img("apr", "crop", alt="Approval Matrix v3.0, page 1, section 3: the limits table")
_dcrop["boxes"] = [dict(bx, k=1) for bx in _dcrop["boxes"]]
files["docling"] = {
    "images": {"crop": _dcrop},
    "texts": {
        "apr": {"title": "Docling · export_to_markdown()", "sub": "Approval Matrix v3.0, page 1, § 3", "cls": "a", "fs": 13.5,
                "text": dla_cut,
                "marks": [{"s": _tab_first, "k": 1, "cls": "g"}, {"s": _row_exec, "k": 1, "cls": "g"},
                          {"s": "- 3.1 Each role's approval limit, gross including VAT:", "k": 2, "cls": "b"}]},
        "scan": {"title": "Docling on the scan", "sub": "with its OCR", "cls": "a", "fs": 13, "text": _scan_md,
                 "marks": [{"s": "<!-- image -->", "k": 3, "cls": "g"}, {"s": "BAT-500Quantity", "k": 3, "cls": "b"}, {"s": "VC-EIN-0042Voltway", "k": 3, "cls": "b"}]}}}
nums["docling"] = {
    "version": DL["versions"]["docling"], "machine": DL["machine"], "init_secs": DL["converter_init_secs"],
    "ocr": "RapidOCR " + DL["ocr_packages"]["rapidocr"] if DL["ocr_packages"].get("rapidocr") else "",
    "pur_warm": DL["files"]["pur"]["warm_secs"], "pur_cold": DL["files"]["pur"]["cold_secs"], "pur_pages": DL["files"]["pur"]["n_pages"],
    "pur_per_page": round(DL["files"]["pur"]["warm_secs"] / DL["files"]["pur"]["n_pages"], 1),
    "apr_warm": DL["files"]["apr"]["warm_secs"], "apr_pages": DL["files"]["apr"]["n_pages"], "scan_warm": DL["files"]["scan"]["warm_secs"],
    "pur_furniture": len(DL["files"]["pur"]["page_furniture"]), "pur_headings": len(DL["files"]["pur"]["section_headers"]),
    "pur_tables": len(DL["files"]["pur"]["tables"]), "apr_tables": len(DL["files"]["apr"]["tables"]),
    "ours_secs": _our_secs, "ours_pur_secs_s": f"{_our_secs['pur']:.2f}",
    "split_heading": _dl_whole[0]}

# ---------------------------------------------------------------- the check slides
r25 = {p: next(u["text"] for u in X[ITEM][p]["units"] if u["loc"].get("sheet") == "Items" and u["loc"].get("row") == 25) for p in ("plain", "structured")}
files["check_item"] = {"q": q("Q-436", "reorder level 200, and cell_safety 1, so yes, a lithium-cell part."),
                       "texts": {"naive": {"title": "parser=\"plain\" · sheet Items · row 25", "cls": "b", "fs": 21, "text": r25["plain"],
                                           "marks": [{"s": " 1 1 200 20 42 ", "k": 1, "cls": "b"}]},
                                 "struct": {"title": "parser=\"structured\" · sheet Items · row 25", "cls": "a", "fs": 21, "text": r25["structured"],
                                            "marks": [{"s": "cell_safety: 1", "k": 1, "cls": "a"}, {"s": "reorder_lvl: 200", "k": 1, "cls": "a"}]}}}
fw = (DUMP / "09_email_archive/2026/2026-09-25_RE_ RE_ FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml").read_text(encoding="utf-8")
snip_qp = fw[fw.index("our price for the 36 V"):].split("\n")[0]
snip_next = fw[fw.index(snip_qp) + len(snip_qp) + 1:].split("\n")[0]
qp_dec = quopri.decodestring((snip_qp + "\n" + snip_next).encode()).decode("utf-8")
files["check_three"] = {"snips": [
    {"what": "The last two lines of a page", "from": "Document D, page 2, as the naive parser reads it", "file": PUR,
     "text": "Internal. Uncontrolled when printed.\nPage 2 of 4", "verb": "Drop",
     "do": "It is the running footer, printed on every page. It says nothing about buying; left in, it lands in the middle of a chunk. Our parser removes lines repeated at the top and bottom of every page, and “Page x of y”."},
    {"what": "One line of an e-mail body", "from": "Voltway Cells’ price e-mail of 25 Sep 2026, as the file is stored on disk", "file": "09_email_archive/2026/2026-09-25_RE_ RE_ FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml",
     "text": snip_qp, "verb": "Decode",
     "do": f"Quoted-printable, as on the Brightcell e-mail: =C2=A3 is “£”, and the “=” at the end is a soft break. Decoded: “{qp_dec[qp_dec.index('£'):].strip()}”."},
    {"what": "One row of the box at the top of page 1", "from": "The 2024 Approval Matrix v2.0 (Word), as our parser reads it", "file": APR2,
     "text": "Status | SUPERSEDED", "verb": "Keep",
     "do": f"It is the one line that says this file is out of date: £200,000 is no longer the limit. Our parser keeps it, and writes “{K['meta'][APR2]['status_line']}” at the top of every chunk of the file."}],
    "legend": [{"verb": "Keep", "def": "index it as it is: it is content"}, {"verb": "Decode", "def": "turn it back into the text the writer typed, then index it"},
               {"verb": "Drop", "def": "remove it before indexing: it is not content"}]}

data = {"generated_from": ["logs/v5_parse_explore.json", "logs/v5_parse_render.json", "logs/v5_parse_ocr.json", "logs/v5_parse_checks.json", "logs/audit.json", "northbridge-docs/eval/questions.jsonl"],
        "facts": K["facts"], "files": files, "nums": nums}
(LOGS / "v5_parse.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
(V5 / "parse_data.js").write_text("/* L3 v5 · parsing section data. Written by experiments/v5_parse_build.py from experiments/logs/v5_parse*.json. Do not edit by hand. */\n"
                                  "window.L3V5 = window.L3V5 || {};\nwindow.L3V5.parse = " + json.dumps(data, ensure_ascii=False) + ";\n")
print("wrote", V5 / "parse_data.js", (V5 / "parse_data.js").stat().st_size, "bytes")
print(json.dumps(nums["ocr"], indent=1)[:1500])
