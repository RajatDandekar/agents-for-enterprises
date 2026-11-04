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
c6 = K["chunk6"]["chunks"][0]
files["pur"] = {
    "file": PUR, "q": q("Q-EMMA", "§ 6.2 and § 6.4, both in the unit at page 2, § 6. Supplier qualification."),
    "images": {"page": img("pur", "page", alt="Purchase Policy v4.1, page 2"), "crop6": img("pur", "crop6", alt="Purchase Policy v4.1, section 6")},
    "texts": {
        "naive": {"title": "Naive · end of page 2, start of page 3", "cls": "b", "fs": 14,
                  "text": "⋯\n" + tail.rstrip() + "\n" + head3 + "\n⋯",
                  "marks": [{"s": "Northbridge Cycles Ltd\nPOL-PUR-001 | v4.1\nInternal. Uncontrolled when printed.\nPage 2 of 4", "k": 1, "cls": "b"}]},
        "units": {"title": "Structured · page 2 units", "sub": f"{K['n_units_pur']} in the policy", "cls": "a", "fs": 15,
                  "text": "\n".join(f"p.{u['loc']['page']}  § {u['loc']['section']:<28} {u['tokens']:>4} tokens" for u in u2),
                  "marks": [{"s": "§ 6. Supplier qualification", "k": 3, "cls": "g"}]},
        "chunk": {"title": "A chunk of § 6 begins", "sub": f"{c6['tokens']} tokens", "cls": "a", "fs": 15,
                  "text": c6["header"] + "\n" + c6["body"].split("\n")[0] + "\n⋯",
                  "marks": [{"s": c6["header"], "k": 3, "cls": "g"}]}},
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
                "marks": [{"s": "=C2=A3", "k": 1, "cls": "b"}, {"s": "=\n", "k": 1, "cls": "b"},
                          {"s": "Content-Transfer-Encoding: quoted-printable", "k": 1, "cls": "k"},
                          {"s": "Message-ID: <c0e8939f459f7898bbeb@mail.northbridgecycles.example>\nX-Mailer: NBC Mail Gateway 4.2\nContent-Type: text/plain; charset=\"utf-8\"", "k": 2, "cls": "s"},
                          {"s": "MIME-Version: 1.0", "k": 2, "cls": "s"}]},
        "struct": {"title": "Structured · decoded", "sub": f"{X[EML]['structured']['tokens']} tokens", "cls": "a", "fs": 12.8, "text": eu[: eu.index("December 2026.") + len("December 2026.")] + "\n⋯ the signature follows",
                   "marks": [{"s": "Subject: Quotation Q-BE-26-0917 - 36 V 500 Wh battery packs", "k": 2, "cls": "g"},
                             {"s": "From: Julien Marchand <j.marchand@brightcell-energy.example>", "k": 2, "cls": "g"},
                             {"s": "To: Emma Clarke <emma.clarke@northbridgecycles.example>", "k": 2, "cls": "g"}, {"s": "Date: Thu, 22 Oct 2026 16:41:00 +0000", "k": 2, "cls": "g"},
                             {"s": "£104.00 per pack, delivered (DAP) to Manchester", "k": 3, "cls": "a"},
                             {"s": "the new report is expected in December 2026", "k": 3, "cls": "a"}]}},
}
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

# ---------------------------------------------------------------- 8 · an old intranet page
hraw = (DUMP / INTRA).read_text(encoding="utf-8")
hu = X[INTRA]["structured"]["units"][0]["text"]
files["intra"] = {
    "file": INTRA, "q": q("Q-605", "In 2016: £150,000, on the net value before VAT. Long superseded."),
    "images": {"page": img("intra", "page", alt="The 2016 intranet page in a browser")},
    "texts": {
        "naive": {"title": "Naive · the markup, parser=\"plain\"", "sub": f"{X[INTRA]['plain']['tokens']} tokens", "cls": "b", "raw": True, "fs": 13,
                  "text": between(hraw, "<body>", "<h1>Approval limits (2016)</h1>") + "\n⋯ then the table, a note, a heading and four paragraphs",
                  "marks": [{"s": between(hraw, '<div id="banner">', "</ul></div>"), "k": 1, "cls": "b"}]},
        "struct": {"title": "Structured · text by heading, no navigation", "sub": f"{X[INTRA]['structured']['tokens']} tokens · {X[INTRA]['structured']['n_units']} units", "cls": "a", "fs": 13.5,
                   "text": hu,
                   "marks": [{"s": " Purchase executive | £150,000", "k": 3, "cls": "a"}, {"s": "Limits are on the net value before VAT.", "k": 3, "cls": "g"}]}},
}
nums["intra"] = {"plain_tokens": X[INTRA]["plain"]["tokens"], "struct_tokens": X[INTRA]["structured"]["tokens"],
                 "nav_links": hraw[hraw.index('<div id="nav">'):hraw.index("</ul></div>")].count("<li>")}

# ---------------------------------------------------------------- 9 · metadata the parser keeps
FIELDS = ("doc_id", "version", "effective", "status", "superseded", "future", "confidential")
meta = []
for rel, m in K["meta"].items():
    s = m["structured"]
    meta.append({"file": rel, "fields": {k: s[k] for k in FIELDS}, "title": s["title"], "status_line": m["status_line"], "may_read": m["may_read"],
                 "answer": {APR: "£250,000 gross", APR2: "£200,000 gross", INTRA: "£150,000 net"}.get(rel)})
files["meta"] = {"records": meta}

# ---------------------------------------------------------------- the check slides
r25 = {p: next(u["text"] for u in X[ITEM][p]["units"] if u["loc"].get("sheet") == "Items" and u["loc"].get("row") == 25) for p in ("plain", "structured")}
files["check_item"] = {"q": q("Q-436", "reorder level 200, and cell_safety 1, so yes, a lithium-cell part."),
                       "texts": {"naive": {"title": "parser=\"plain\" · sheet Items · row 25", "cls": "b", "fs": 21, "text": r25["plain"],
                                           "marks": [{"s": " 1 1 200 20 42 ", "k": 1, "cls": "b"}]},
                                 "struct": {"title": "parser=\"structured\" · sheet Items · row 25", "cls": "a", "fs": 21, "text": r25["structured"],
                                            "marks": [{"s": "cell_safety: 1", "k": 1, "cls": "a"}, {"s": "reorder_lvl: 200", "k": 1, "cls": "a"}]}}}
fw = (DUMP / "09_email_archive/2026/2026-09-25_RE_ RE_ FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml").read_text(encoding="utf-8")
snip_qp = fw[fw.index("our price for the 36 V"):].split("\n")[0]
files["check_three"] = {"snips": [
    {"from": PUR + ", page 2 (plain)", "text": "Internal. Uncontrolled when printed.\nPage 2 of 4", "do": "Drop it: a running footer, on every page. Our parser removes lines repeated in the top and bottom bands, and “Page x of y”."},
    {"from": "09_email_archive/2026/2026-09-25_RE_ RE_ FW_ Voltway Cells - BAT-500 price from 1 October 2026.eml", "text": snip_qp,
     "do": "Decode it: quoted-printable. “=C2=A3” is the two UTF-8 bytes of “£”, and “=” at a line end is a soft break. Decoded: “£119.00 from 1 October 2026”."},
    {"from": APR2 + " (structured)", "text": "Status | SUPERSEDED", "do": "Keep it as metadata: status SUPERSEDED, superseded = true. Every chunk of this file then says so in its header, and a filter can drop it."}]}

data = {"generated_from": ["logs/v5_parse_explore.json", "logs/v5_parse_render.json", "logs/v5_parse_ocr.json", "logs/v5_parse_checks.json", "logs/audit.json", "northbridge-docs/eval/questions.jsonl"],
        "facts": K["facts"], "files": files, "nums": nums}
(LOGS / "v5_parse.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
(V5 / "parse_data.js").write_text("/* L3 v5 · parsing section data. Written by experiments/v5_parse_build.py from experiments/logs/v5_parse*.json. Do not edit by hand. */\n"
                                  "window.L3V5 = window.L3V5 || {};\nwindow.L3V5.parse = " + json.dumps(data, ensure_ascii=False) + ";\n")
print("wrote", V5 / "parse_data.js", (V5 / "parse_data.js").stat().st_size, "bytes")
print(json.dumps(nums["ocr"], indent=1)[:1500])
