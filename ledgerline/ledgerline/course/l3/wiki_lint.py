"""Lecture 3, the LLM Wiki: LINT, the health check, and how much of the dump's planted mess it finds.

    from ledgerline.course.l3 import wiki_lint as WL
    rep = WL.lint(wiki_dir, dump_root, llm)          # findings: code checks + what ingest noticed + an LLM review
    WL.score_against_messiness(rep, dump_root)       # found / missed, item by item, against eval/messiness.json

Three kinds of finding, each with the files and pages it is about:
  code     orphans, red links (links to pages that do not exist), references whose quoted words are not at the
           cited location, uncited paragraphs, byte-identical files, near-duplicate files (same document code or
           shingle overlap), superseded / future-dated / scanned sources, dead links in old HTML, files whose names
           break the numbering convention, two formats for one kind of source, tables inside PDFs, confidential files
           and whether any staff page cites them;
  ingest   the conflicts the READ step and the WRITE step recorded while they compiled the pages;
  review   one LLM call per page whose sources disagree in date or status: contradictions, stale or superseded claims
           written as current, future rules written as current, missing links.
eval/messiness.json is only read by score_against_messiness(), after lint has run.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

from .wiki_build import LINK, REF, parse_page_file
from .wiki_llm import REASONING_LOW, reply_usd

KINDS = ["superseded", "contradiction", "future_dated", "email_overrides_sop", "near_duplicate", "duplicate",
         "rule_not_in_policy", "legacy_abbreviations", "broken_links", "inconsistent_naming", "confidential", "scans",
         "mixed_formats", "tables_in_pdfs", "orphan", "red_link", "uncited", "citation_not_found"]
FAMILY = {"superseded": "version", "near_duplicate": "version", "duplicate": "version",
          "contradiction": "conflict", "email_overrides_sop": "conflict", "rule_not_in_policy": "conflict",
          "future_dated": "future", "legacy_abbreviations": "legacy", "legacy_terms": "legacy"}


def _f(kind, files, detail, source, pages=None, **kw):
    return {"kind": kind, "files": sorted(set(files)), "pages": sorted(set(pages or [])), "detail": detail,
            "source": source, **kw}


def load(wiki_dir):
    wiki_dir = pathlib.Path(wiki_dir)
    man = json.loads((wiki_dir / "manifest.json").read_text())
    srcs = [json.loads(l) for l in (wiki_dir / "sources.jsonl").open()]
    return wiki_dir, man, srcs


class Resolver:
    """Turn the names an LLM uses for documents ("POL-SUP-003 v2.3", "the SOP-AP-002", a title) into dump files."""

    def __init__(self, srcs):
        self.files = [s["file"] for s in srcs]
        self.by_doc = defaultdict(list)
        for s in srcs:
            if s.get("doc"):
                self.by_doc[s["doc"].upper()].append(s["file"])
            for code in re.findall(r"(?:POL|SOP|MAN|AMD|HR-CONF|QRC|RN)-[A-Z0-9.]+(?:-[A-Z0-9.]+)*", s["file"]):
                if s["file"] not in self.by_doc[code.upper()]:
                    self.by_doc[code.upper()].append(s["file"])

    def __call__(self, text: str, version: bool = True) -> list[str]:
        if not text:
            return []
        out = []
        t = str(text)
        for f in self.files:
            if f in t or f.rsplit("/", 1)[-1] in t:
                out.append(f)
        for code in re.findall(r"(?:POL|SOP|MAN|AMD|HR-CONF|QRC)-[A-Z0-9]+(?:-[A-Z0-9]+)*|RN-7(?:\.\d)+(?:-P\d)?", t):
            fs = self.by_doc.get(code.upper(), [])
            vm = re.search(re.escape(code) + r"[^,;]{0,25}?v(\d+(?:\.\d+)*)", t)
            if vm and version:
                vfs = [f for f in fs if re.search(rf"v{re.escape(vm.group(1))}\b", f)]
                fs = vfs or fs
            out += fs
        return sorted(set(out))


# =================================================================================================== code checks
def code_checks(wiki_dir: pathlib.Path, man: dict, srcs: list[dict], dump) -> list[dict]:
    pages = man["pages"]
    out = []
    inbound = Counter(l for p in pages.values() for l in p["links_out"] if l in pages)
    for s, p in pages.items():
        if inbound[s] == 0:
            out.append(_f("orphan", p["sources"][:3], f"no page links to [[{s}]] (only the index does)", "code", [s]))
        red = [l for l in p["links_out"] if l not in pages]
        if red:
            out.append(_f("red_link", [], f"[[{s}]] links to missing pages: {', '.join(red[:6])}", "code", [s] + red))
        bad = [k for k, r in p.get("refs", {}).items() if r.get("verified") is False]
        if bad:
            files = [p["refs"][k]["file"] for k in bad]
            out.append(_f("citation_not_found", files, f"[[{s}]]: {len(bad)} reference(s) whose quoted words are "
                                                       f"not at the cited location ({', '.join(bad[:5])})", "code", [s]))
        _, body = parse_page_file((wiki_dir / p["path"]).read_text())
        body = re.sub(r"\n## (References|See also|Filed answers)\n.*?(?=\n## |\Z)", "", body, flags=re.S)
        paras = [x for x in re.split(r"\n\s*\n", body) if len(x) > 120 and not x.lstrip().startswith(("|", "#"))]
        unc = [x for x in paras if not REF.search(x)]
        if unc:
            out.append(_f("uncited", [], f"[[{s}]]: {len(unc)} paragraph(s) with no reference", "code", [s]))
    # sources
    root = pathlib.Path(dump)
    sha = defaultdict(list)
    for s in srcs:
        sha[hashlib.sha1((root / s["file"]).read_bytes()).hexdigest()].append(s["file"])
    for g in sha.values():
        if len(g) > 1:
            out.append(_f("duplicate", g, "byte-identical files: " + " = ".join(g), "code"))
    by_doc = defaultdict(list)
    for s in srcs:
        if s.get("doc"):
            by_doc[s["doc"]].append(s)
    for doc, ss in by_doc.items():
        files = sorted({s["file"] for s in ss})
        if len(files) > 1 and not all(len(v) > 1 and set(files) <= set(v) for v in sha.values()):
            vers = ", ".join(f"{s['file'].rsplit('/', 1)[-1]} (v{s.get('version')}, {s['status']})" for s in ss)
            out.append(_f("near_duplicate", files, f"{doc} exists in {len(files)} files: {vers}", "code"))
    # shingle overlap between sources without a shared code (old exports, renamed copies)
    texts = {}
    for s in srcs:
        if s["fmt"] in ("pdf", "docx", "md", "txt", "csv") and s["file"] not in sum([g for g in sha.values()
                                                                                    if len(g) > 1], []):
            texts[s["file"]] = s
    sh = {}
    for f in texts:
        try:
            t = _plain(root / f)
        except Exception:
            continue
        w = re.findall(r"[a-z0-9]+", t.lower())
        sh[f] = {" ".join(w[i:i + 6]) for i in range(0, max(0, len(w) - 6), 3)}
    fl = sorted(sh)
    for i, a in enumerate(fl):
        for b in fl[i + 1:]:
            if not sh[a] or not sh[b] or a.split("/")[0] != b.split("/")[0]:
                continue
            j = len(sh[a] & sh[b]) / max(1, min(len(sh[a]), len(sh[b])))
            if j >= 0.5 and texts[a].get("doc") != texts[b].get("doc") or (j >= 0.5 and not texts[a].get("doc")):
                out.append(_f("near_duplicate", [a, b], f"{j:.0%} of the shorter file's 6-word shingles are in the other",
                              "code", overlap=round(j, 3)))
    for s in srcs:
        f = s["file"]
        if s["status"] == "superseded":
            out.append(_f("superseded", [f], f"{f}: superseded copy still in the dump (doc {s.get('doc')}, "
                                             f"v{s.get('version')})", "code"))
        if s["status"] == "future":
            out.append(_f("future_dated", [f], f"{f}: effective {s.get('effective')}, after today (2026-10-26)", "code"))
        if s["status"] == "scan":
            out.append(_f("scans", [f], f"{f}: image-only, no text layer (OCR found nothing)", "code"))
        if s["audience"] == "hr":
            cited_by = [p for p, pg in man["pages"].items() if pg["audience"] != "hr" and f in pg["sources"]]
            out.append(_f("confidential", [f], f"{f}: HR-only; staff pages citing it: {len(cited_by)}", "code",
                          cited_by))
        name = f.rsplit("/", 1)[-1]
        if re.search(r"(?i)final|copy|\(\d\)|_v\d|^[a-z_]+\d", name) and not s.get("doc") or re.search(r"(?i)final_final", name):
            out.append(_f("inconsistent_naming", [f], f"file name '{name}' breaks the document-number convention",
                          "code"))
    # dead links in HTML
    for s in srcs:
        if s["fmt"] == "html":
            raw = (root / s["file"]).read_text(errors="replace")
            dead = []
            for href in re.findall(r'href="([^"#]+)"', raw):
                if re.match(r"(?i)https?://|//|file:|\\\\", href) or href.startswith("/"):
                    dead.append(href)
                elif not (root / s["file"]).parent.joinpath(href).exists():
                    dead.append(href)
            if dead:
                out.append(_f("broken_links", [s["file"]], f"{len(dead)} dead link(s): {', '.join(dead[:4])}", "code"))
    # mixed formats among service definitions
    svc = Counter(s["fmt"] for s in srcs if s["file"].startswith("04_service_definitions/") and s["fmt"] in
                  ("yaml", "xml", "wsdl"))
    if len(svc) > 1:
        ex = [next(s["file"] for s in srcs if s["file"].startswith("04_service_definitions/") and s["fmt"] == k)
              for k in svc]
        out.append(_f("mixed_formats", ex, f"service definitions in {dict(svc)} formats", "code"))
    # tables inside PDFs (the structured parser's table rows)
    try:
        from . import corpus as C

        units = C.parse(dump, parser="structured")
        tab = Counter()
        for u in units:
            if u.fmt == "pdf" and len(re.findall(r"^[^\n|]+\|[^\n|]+\|", u.text, re.M)) >= 3:
                tab[u.file] += 1
        for f, n in tab.items():
            out.append(_f("tables_in_pdfs", [f], f"{n} page section(s) hold tables; plain text loses their rows "
                                                 f"and columns", "code"))
    except Exception as e:  # pragma: no cover
        out.append(_f("tables_in_pdfs", [], f"table check skipped: {e!r}"[:200], "code"))
    return out


def _plain(path: pathlib.Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader

        return "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    if ext == ".docx":
        import docx

        return "\n".join(p.text for p in docx.Document(str(path)).paragraphs)
    return path.read_bytes().decode("utf-8", errors="replace")


# =================================================================================================== ingest conflicts
def ingest_findings(man: dict, srcs: list[dict], resolve: Resolver) -> list[dict]:
    out = []
    for s in srcs:
        for c in s.get("conflicts") or []:
            k = str(c.get("kind", "")).strip()
            k = "legacy_abbreviations" if k == "legacy_terms" else k
            if k not in KINDS:
                continue
            files = [s["file"]] + resolve(f"{c.get('other', '')} {c.get('detail', '')}")
            out.append(_f(k, files, f"{s['file'].rsplit('/', 1)[-1]}: {c.get('detail', '')}"[:400], "ingest-read",
                          other=c.get("other")))
    for slug, p in man["pages"].items():
        for c in p.get("conflicts") or []:
            k = str(c.get("kind", "")).strip().lower().replace(" ", "_")
            k = "legacy_abbreviations" if k == "legacy_terms" else k
            if k not in KINDS:
                continue
            files = [p["refs"][r]["file"] for r in c.get("refs", []) if r in p.get("refs", {})]
            files += resolve(f"{c.get('today', '')} {c.get('other', '')}")
            out.append(_f(k, files, f"[[{slug}]] today: {c.get('today', '')} | other: {c.get('other', '')}"[:400],
                          "ingest-write", [slug]))
    return out


# =================================================================================================== LLM review
REVIEW = """You are linting one page of Northbridge Cycles' wiki (today is Monday 26 October 2026).
Below are the page and the facts it was compiled from (each with its source file, date and status).

Report problems as JSON only: {{"findings": [{{"kind": "<kind>", "files": ["source file", ...], "detail": "one sentence"}}]}}
Kinds: contradiction (two sources disagree on a rule, number or behaviour), superseded (an older version or copy is
still present, or the page states a superseded rule as current), future_dated (a rule not yet in force, or written as
current), email_overrides_sop (an e-mail or meeting decision changed a SOP or policy that was not reissued),
rule_not_in_policy (a working rule that exists only in an e-mail or meeting note), near_duplicate, duplicate,
legacy_abbreviations (old system terms or codes), inconsistent_naming (one thing named two ways), missing_link
(another wiki page should be linked). List each real problem once; give the files on both sides. Reply {{"findings": []}}
if the page is clean.

PAGE [[{slug}]]:
{page}

FACTS:
{facts}"""


def review_pages(wiki_dir, man, facts_by_page, llm, workers=24, max_pages=None):
    cand = []
    for slug, p in man["pages"].items():
        fs = facts_by_page.get(slug, [])
        statuses = {f["status"] for f in fs}
        dates = {f.get("date") for f in fs if f.get("date")}
        if len({f["file"] for f in fs}) >= 2 and (len(statuses) > 1 or len(dates) > 1 or p.get("conflicts")):
            cand.append(slug)
    cand = cand[:max_pages] if max_pages else cand

    def one(slug):
        p = man["pages"][slug]
        _, body = parse_page_file((pathlib.Path(wiki_dir) / p["path"]).read_text())
        fs = facts_by_page.get(slug, [])[:120]
        ft = "\n".join(f"- ({f['file']}; {f.get('date')}; {f['status']}) {f['fact']}" for f in fs)
        r = llm.chat([{"role": "user", "content": REVIEW.format(slug=slug, page=body[:14000], facts=ft[:24000])}],
                     response_format={"type": "json_object"}, **REASONING_LOW)
        try:
            d = json.loads(re.sub(r"^```(?:json)?|```$", "", (r.content or "").strip()).strip())
            fl = d.get("findings", []) if isinstance(d, dict) else []
        except Exception:
            fl = []
        return slug, fl, {"tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "llm_seconds": r.seconds,
                          "usd": reply_usd(r)}

    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(one, cand))
    return res


# =================================================================================================== the lint
def lint(wiki_dir, dump, llm=None, review: bool = True, workers: int = 24) -> dict:
    t0 = time.perf_counter()
    wiki_dir, man, srcs = load(wiki_dir)
    resolve = Resolver(srcs)
    findings = code_checks(wiki_dir, man, srcs, dump)
    t_code = time.perf_counter() - t0
    findings += ingest_findings(man, srcs, resolve)
    stats = {"pages_reviewed": 0, "tokens_in": 0, "tokens_out": 0, "usd": 0.0}
    t1 = time.perf_counter()
    if review and llm is not None:
        fb = defaultdict(list)
        for line in (wiki_dir / "facts.jsonl").open():
            f = json.loads(line)
            fb[f["slug"]].append(f)
        for slug, fl, st in review_pages(wiki_dir, man, fb, llm, workers):
            stats["pages_reviewed"] += 1
            for k in ("tokens_in", "tokens_out", "usd"):
                stats[k] += st[k]
            for x in fl:
                k = str(x.get("kind", "")).strip()
                files = []
                for fx in x.get("files") or []:
                    files += resolve(str(fx)) or ([fx] if fx in resolve.files else [])
                files += resolve(x.get("detail", ""))
                if k == "missing_link":
                    k = "red_link"
                if k in KINDS:
                    findings.append(_f(k, files, f"[[{slug}]]: {x.get('detail', '')}"[:400], "review", [slug]))
    stats["usd"] = round(stats["usd"], 4)
    by_kind = Counter(f["kind"] for f in findings)
    by_src = Counter(f["source"] for f in findings)
    rep = {"findings": findings, "n_findings": len(findings), "by_kind": dict(by_kind), "by_source": dict(by_src),
           "review": stats, "seconds": {"code": round(t_code, 1), "review": round(time.perf_counter() - t1, 1),
                                        "total": round(time.perf_counter() - t0, 1)}}
    with (wiki_dir / "log.md").open("a") as f:
        from .wiki_build import now

        f.write(f"## [{now()}] lint | {len(findings)} findings | " +
                ", ".join(f"{k} {v}" for k, v in by_kind.most_common()) + "\n")
    return rep


def score_against_messiness(rep: dict, dump) -> dict:
    """How many of the 40 planted problems the lint found. An item is found when a finding of the same kind (strict) or
    the same family (superseded/near_duplicate/duplicate; contradiction/email_overrides_sop/rule_not_in_policy) names
    its files: one file is enough when the item lists one file or is a per-file kind (scans, confidential, broken
    links, tables, naming, legacy terms, formats); otherwise at least two of its files."""
    mess = json.load(open(pathlib.Path(dump) / "eval" / "messiness.json"))["items"]
    per_file = {"scans", "confidential", "broken_links", "tables_in_pdfs", "inconsistent_naming",
                "legacy_abbreviations", "mixed_formats", "superseded", "future_dated", "rule_not_in_policy"}
    rows = []
    for it in mess:
        F = set(it["files"])
        need = 1 if (len(F) == 1 or it["kind"] in per_file) else 2
        strict, family = [], []
        for i, f in enumerate(rep["findings"]):
            n = len(F & set(f["files"]))
            if n < need:
                continue
            if f["kind"] == it["kind"]:
                strict.append(i)
            elif FAMILY.get(f["kind"]) and FAMILY.get(f["kind"]) == FAMILY.get(it["kind"]):
                family.append(i)
        rows.append({"id": it["id"], "kind": it["kind"], "what": it["what"], "files": it["files"],
                     "found_strict": bool(strict), "found": bool(strict or family),
                     "by": sorted({rep["findings"][i]["source"] for i in strict + family}),
                     "evidence": [rep["findings"][i]["detail"] for i in (strict + family)[:3]]})
    n = len(rows)
    by_kind = defaultdict(lambda: {"n": 0, "found": 0, "strict": 0})
    for r in rows:
        by_kind[r["kind"]]["n"] += 1
        by_kind[r["kind"]]["found"] += r["found"]
        by_kind[r["kind"]]["strict"] += r["found_strict"]
    return {"items": rows, "found": sum(r["found"] for r in rows), "found_strict": sum(r["found_strict"] for r in rows),
            "n": n, "missed": [r["id"] for r in rows if not r["found"]], "by_kind": dict(by_kind)}
