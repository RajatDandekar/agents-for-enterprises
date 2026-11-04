"""Lecture 3 v5, the LLM Wiki section: every number and every passage the slides show, taken from recorded logs.

    cd /Users/raj/Claude_Brain/enterprise-agents-course/lectures/L3-the-memory/experiments
    /Users/raj/.venv/bin/python v5_wiki_data.py [--facts /path/to/facts.jsonl]

Reads (no model call, no heavy compute):
  logs/v5_wiki_ingest.json, v5_wiki_update.json, v5_wiki_query.json, v5_wiki_counts.json   (v5_wiki_modal.py)
  logs/wiki_build.json, wiki_update.json, wiki_lint.json, wiki_eval_wiki.json, race.json, race_answers/rag__250.json
  ledgerline/ledgerline/wiki_v4 (the built wiki), northbridge-docs/eval (golden set, gold facts with verbatim needles)
  facts.jsonl of the full build (12,095 facts; on the Modal volume northbridge-wiki at wiki_v4/facts.jsonl)
Writes logs/v5_wiki_failures.json (the failure examples, each with its evidence) and ../v5/wiki_data.js
(window.L3V5.wiki, read by v5/wiki.js).
"""
import argparse
import json
import pathlib
import re
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
COURSE = HERE.parents[2]
WIKI = COURSE / "ledgerline" / "ledgerline" / "wiki_v4"
DOCS = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")
OUT_JS = HERE.parent / "v5" / "wiki_data.js"
PRICE = (0.825, 4.125)  # evaluate.PRICE_USD["gemini-3.8-flash"], $ per million in / out


def J(name):
    return json.load(open(LOGS / name))


def usd(ti, to):
    return round((ti * PRICE[0] + to * PRICE[1]) / 1e6, 4)


def norm(s):  # wiki_build.norm
    s = str(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ").replace("­", "")
    s = re.sub(r"\*\*|__|[•·▪]", "", s)
    return re.sub(r"\s+", "", s).lower()


# ------------------------------------------------------------------------------------------------ D, by clause
def d_clauses(text):
    """D's clauses §1-§9 from the ingest's own text (the [p. N] pages the READ call saw), wrapped lines joined."""
    body = text.split("Appendix A.")[0]
    page = 1
    out, cur = [], None
    for ln in body.splitlines():
        m = re.match(r"^\[p\. (\d+)\]$", ln.strip())
        if m:
            page = int(m.group(1))
            continue
        h = re.match(r"^(\d)\. (.+)$", ln.strip())
        c = re.match(r"^(\d\.\d) (.+)$", ln.strip())
        if h and not c:
            cur = {"id": h.group(1), "kind": "head", "text": h.group(2), "page": page}
            out.append(cur)
        elif c:
            cur = {"id": c.group(1), "kind": "clause", "text": c.group(2), "page": page}
            out.append(cur)
        elif cur is not None and ln.strip():
            cur["text"] += " " + ln.strip()
    # §1 and §2 have no numbered clauses: their sentence is the head's body
    fixed = []
    for i, c in enumerate(out):
        if c["kind"] == "head" and c["id"] in ("1", "2"):
            head, _, rest = c["text"].partition(" ")
            name = {"1": "Purpose", "2": "Scope"}[c["id"]]
            fixed.append({"id": c["id"], "kind": "head", "text": name, "page": c["page"]})
            fixed.append({"id": c["id"] + ".", "kind": "clause", "text": c["text"][len(name):].strip(), "page": c["page"]})
        else:
            fixed.append(c)
    return fixed


HDR = {"txt": ""}


def which_clauses(quote, clauses):
    q = norm(quote)
    if q and HDR["txt"] and q in HDR["txt"]:
        return ["hdr"]
    if q and HDR.get("ver") and q in HDR["ver"]:
        return ["ver"]
    hits = [c["id"] for c in clauses if c["kind"] == "clause" and q and (q in norm(c["text"]) or norm(c["text"]) in q)]
    if hits and any(q in norm(c["text"]) for c in clauses if c["id"] in hits):
        return hits
    # a quote that runs across two clauses: report each clause it overlaps by a long run of words
    words = [w for w in re.split(r"\s+", quote) if w]
    hit = list(hits)
    for c in clauses:
        if c["kind"] != "clause":
            continue
        for k in range(0, max(1, len(words) - 6)):
            if norm(" ".join(words[k:k + 7])) in norm(c["text"]) and c["id"] not in hit:
                hit.append(c["id"])
                break
    return hit


def sentences(text):
    """Split prose into sentences that end with their citation keys: '... [^r4]. Next ...'."""
    return [x for x in re.split(r"(?<=\]\.)\s+|(?<=\])\s+(?=[A-Z*\[])", text.strip()) if x.strip()]


def page_sentences(md, refs, clauses):
    """The body of a written page cut into sentences; each with its [^rN] keys and the D clauses they point to."""
    body = md.split("\n---\n", 1)[1] if md.startswith("---") else md
    body = body.split("\n## References")[0]
    out = []
    section = "Lead"
    for ln in body.splitlines():
        if ln.startswith("### ") or ln.startswith("## "):
            section = ln.lstrip("# ").strip()
            out.append({"kind": "head", "level": 2 if ln.startswith("## ") else 3, "text": section})
            continue
        if not ln.strip() or ln.startswith("|"):
            continue
        for s in sentences(ln):
            keys = re.findall(r"\[\^(r\d+)\]", s)
            cl = []
            for k in keys:
                q = (refs.get(k) or {}).get("quote") or ""
                for c in which_clauses(q, clauses):
                    if c not in cl:
                        cl.append(c)
            out.append({"kind": "s", "text": re.sub(r"\s*(\[\^r\d+\])+", "", s).strip(), "keys": keys,
                        "clauses": cl, "section": section, "bullet": s.startswith(("- ", "* "))})
    return out


def front(md):
    fm = {}
    if md.startswith("---"):
        head = md[3:].split("\n---", 1)[0]
        for line in head.strip().splitlines():
            k, _, v = line.partition(":")
            try:
                fm[k.strip()] = json.loads(v.strip())
            except json.JSONDecodeError:
                fm[k.strip()] = v.strip()
    return fm


def infobox(md):
    rows = []
    for ln in md.split("\n---\n", 1)[-1].splitlines():
        if ln.startswith("| ") and not ln.startswith("| |") and "---" not in ln:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) == 2:
                rows.append(cells)
        elif rows and not ln.startswith("|"):
            break
    return rows


def main(facts_path):
    I, U, Q, CN = J("v5_wiki_ingest.json"), J("v5_wiki_update.json"), J("v5_wiki_query.json"), J("v5_wiki_counts.json")
    B, WU, L, EW, R = J("wiki_build.json"), J("wiki_update.json"), J("wiki_lint.json"), J("wiki_eval_wiki.json"), J("race.json")
    RA = {r["id"]: r for r in J("race_answers/rag__250.json")["records"]}
    EWr = {r["id"]: r for r in EW["records"]}
    qs = {json.loads(l)["id"]: json.loads(l) for l in open(DOCS / "eval" / "questions.jsonl")}
    gf = {json.loads(l)["id"]: json.loads(l) for l in open(DOCS / "eval" / "facts.jsonl")}

    text = I["units"][0]["text"]
    clauses = d_clauses(text)
    HDR["txt"] = norm(text.split("Version history")[0])
    HDR["ver"] = norm(text.split("Version history")[1].split("1. Purpose")[0])
    header = []
    for k in ("Document", "Version", "Effective", "Owner", "Approved by", "Status", "Classification"):
        m = re.search(rf"\n{k}\n([^\n]+)\n", text)
        if m:
            header.append([k, m.group(1)])
    vt = text.split("\nChange\n", 1)[1].split("\n1. Purpose")[0].splitlines()
    versions, i = [], 0
    while i < len(vt):
        if re.match(r"^\d\.\d$", vt[i]):
            j = i + 3
            ch = []
            while j < len(vt) and not re.match(r"^\d\.\d$", vt[j]):
                ch.append(vt[j])
                j += 1
            versions.append([vt[i], vt[i + 1], vt[i + 2], " ".join(" ".join(ch).split())])
            i = j
        else:
            i += 1

    # ---------------------------------------------------------------- READ call
    read = I["calls"][0]
    reply = json.loads(read["reply"])
    sys_ = read["messages"][0]["content"]
    user = read["messages"][1]["content"]
    schema_part, _, reg_part = sys_.partition("REGISTRY:")
    head_part, _, rest = user.partition("\n\nPART ")
    part_text, _, rules_part = rest.partition("\n-----\n\nIngest this part.")
    excerpts = {
        "schema": schema_part.strip().splitlines()[:6] + ["…"] + [l for l in schema_part.splitlines() if "Every sentence that states a fact" in l][:1],
        "registry": ["REGISTRY: " + reg_part.strip().splitlines()[0]] + reg_part.strip().splitlines()[1:9] + ["… (" + str(CN["registry_lines"]) + " lines)"],
        "header": head_part.strip().splitlines(),
        "text": ("PART " + part_text).splitlines()[:3] + ["…"] + [l for l in part_text.splitlines() if l.startswith("6.2")] + ["…"],
        "rules": ("Ingest this part." + rules_part).splitlines()[:12] + ["…"],
    }
    parts = [dict(p, key=k, excerpt=excerpts[k]) for p, k in zip(CN["read_prompt_parts"], ["schema", "registry", "header", "text", "rules"])]

    # the reply, page by page
    rpages = []
    for p in reply["pages"]:
        rpages.append({"slug": p["slug"], "type": p["type"], "title": p["title"], "n": len(p["facts"]),
                       "facts": [{"fact": f["fact"], "quote": f["quote"], "page": f.get("page"), "section": f.get("section")}
                                 for f in p["facts"]]})
    checks = I["quote_checks"]
    for c in checks:
        c["clauses"] = which_clauses(c["quote"], clauses)
    # raw page 2 text for the quote-check figure (normalised and raw)
    p2 = I["raw_pages"]["2"] if "2" in I["raw_pages"] else I["raw_pages"][2]

    # ---------------------------------------------------------------- the written pages
    man = I["manifest"]["pages"]
    pol = I["pages"]["pol-pur-001"]
    refs = {k: v for k, v in man["pol-pur-001"]["refs"].items()}
    sents = page_sentences(pol, refs, clauses)
    write_calls = []
    for c in I["calls"][1:]:
        u = c["messages"][-1]["content"]
        m = re.search(r"PAGE: (\S+) \(type", u)
        write_calls.append({"page": m.group(1) if m else "(merge)", "tokens_in": c["tokens_in"], "tokens_out": c["tokens_out"],
                            "seconds": c["seconds"], "replayed": c["replayed"]})
    pages_made = [{"slug": s, "type": p["type"], "title": p["title"], "refs": len(p["refs_used"]),
                   "unverified": [k for k, v in p["refs"].items() if v["verified"] is not True],
                   "links": p["links_out"], "summary": p["summary"]} for s, p in man.items()]
    log_lines = [l for l in I["log_md"].splitlines() if l.startswith("## [")]
    idx_lines = [l for l in I["index_md"].splitlines() if l.startswith("- ")]

    # ---------------------------------------------------------------- the update
    diff = U["diffs"]["topic-un-38-3-certificates"]["diff"].splitlines()
    before_topic, after_topic = U["before"]["topic-un-38-3-certificates"], U["after"]["topic-un-38-3-certificates"]
    amd_text = U["raw_pages"]["1"] if "1" in U["raw_pages"] else U["raw_pages"][1]
    amd_cl = {}
    for m in re.finditer(r"\n(\d\.\d) ((?:.|\n)+?)(?=\n\d\.\d |\n\d\. |\nNorthbridge Cycles Ltd|$)", amd_text):
        amd_cl[m.group(1)] = " ".join(m.group(2).split())
    up_log = [l for l in U["log_after"].splitlines() if l.startswith("## [")]
    pol_untouched = U["before"]["pol-pur-001"] == U["after"]["pol-pur-001"]
    upd_calls = []
    for c in U["calls"]:
        u = c["messages"][-1]["content"]
        m = re.search(r"PAGE: (\S+) \(type", u)
        upd_calls.append({"page": m.group(1) if m else "READ AMD-SUP-2026-02", "tokens_in": c["tokens_in"],
                          "tokens_out": c["tokens_out"], "seconds": c["seconds"]})
    rag_build = None
    g = J("rag_grid.json")
    for b in (g["builds"].values() if isinstance(g["builds"], dict) else g["builds"]):
        if isinstance(b, dict) and b.get("chunking") == "structured-structure-200-o15":
            rag_build = {"n_chunks": b["n_chunks"], "chunk_s": b["chunk_s"], "bm25_build_s": b["bm25_build_s"]}
            break

    # ---------------------------------------------------------------- the query
    qcalls = []
    for c in Q["calls"]:
        qcalls.append({"call": c["call"], "kind": c["kind"], "tokens_in": c["tokens_in_reported"], "tokens_out": c["tokens_out"],
                       "seconds": c["seconds"], "reply": c["reply"],
                       "parts": [{"role": p["role"], "what": p["what"], "tokens": p["tokens"], "chars": p["chars"],
                                  "head": (p["text"] or "")[:420]} for p in c["parts"]]})
    bc_md = Q["brightcell_page"]
    bc_man = Q["brightcell_manifest"]
    bc_refs = bc_man["refs"]
    bc_sents = []
    for ln in bc_md.splitlines():
        if ln.startswith("#") or ln.startswith("|") or not ln.strip():
            if ln.startswith("## "):
                bc_sents.append({"kind": "head", "text": ln[3:].strip()})
            continue
        for s in sentences(ln):
            keys = re.findall(r"\[\^(r\d+)\]", s)
            files = []
            for k in keys:
                f = (bc_refs.get(k) or {}).get("file")
                if f and f not in files:
                    files.append(f)
            bc_sents.append({"kind": "s", "text": re.sub(r"\s*(\[\^r\d+\])+", "", s).strip(), "files": files})

    # ---------------------------------------------------------------- failures, with evidence
    fails = {}
    # 1 never compiled
    facts = [json.loads(l) for l in open(facts_path)]
    man_pur = [f for f in facts if "MAN-PUR-72" in f["file"]]
    by_page = Counter(f.get("page") for f in man_pur)
    src_line = next(json.loads(l) for l in open(WIKI / "sources.jsonl") if "MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing" in l)
    q104 = qs["Q-104"]
    fails["never_compiled"] = {
        "qid": "Q-104", "question": q104["question"], "gold": gf["F-MAN-19.4"]["needles"][0], "gold_loc": gf["F-MAN-19.4"]["loc"],
        "file": gf["F-MAN-19.4"]["file"], "facts_from_file": len(man_pur), "facts_by_page": {str(k): v for k, v in sorted(by_page.items(), key=lambda x: (x[0] is None, x[0] or 0))},
        "read_calls": src_line["stats"]["calls"], "pages_touched_by_file": len(src_line["pages"]),
        "on_any_page": any("press save again" in p.read_text().lower() for p in (WIKI / "pages").glob("*.md")),
        "wiki_opened": EWr["Q-104"]["chain"]["opened"], "wiki_answer": EWr["Q-104"]["answer"], "wiki_ok": EWr["Q-104"]["fact"]["ok"],
        "rag_answer": RA["Q-104"]["answer"], "rag_ok": RA["Q-104"]["fact"]["ok"]}
    # 2 wrong at compile time: (a) the one-source wiki's infobox, (b) the IT Security Policy filed as HR-only
    ib_before = infobox(before_topic)
    ib_after = infobox(after_topic)
    full_topic = (WIKI / "pages" / "topic-un-38-3-certificates.md").read_text()
    full_line = next(s for s in sentences(full_topic.split("\n---\n",1)[1]) if "automated blocking is inactive" in s)
    its = json.load(open(WIKI / "manifest.json"))["pages"]["pol-its-008"]
    its_md = (WIKI / "restricted" / "pol-its-008.md").read_text()
    its_line = next(s for s in its_md.splitlines() if "12 characters" in s)
    fails["wrong_compile"] = {
        "infobox_before": ib_before, "infobox_after": ib_after,
        "lead_claim": next(s for s in sentences(before_topic.split("\n---\n",1)[1]) if "blocking order creation" in s),
        "truth": [gf["F-RNP4-CERT"]["needles"][0], gf["F-CAB-031"]["needles"][0]],
        "truth_files": [gf["F-RNP4-CERT"]["file"], gf["F-CAB-031"]["file"]],
        "full_build_line": re.sub(r"\s*(\[\^r\d+\])+", "", full_line).strip(),
        "its": {"audience": its["audience"], "path": its["path"], "sources": its["sources"], "line": re.sub(r"\s*(\[\^r\d+\])+", "", its_line).strip(),
                "readme": (DOCS / "01_policies/HR/CONFIDENTIAL/README_ACCESS.txt").read_text().strip().splitlines()[-1],
                "q609_wiki_missing": EWr["Q-609"]["fact"]["missing"], "q609_wiki_opened": EWr["Q-609"]["chain"]["opened"],
                "q609_rag_ok": RA["Q-609"]["fact"]["ok"],
                "lint_findings": sum(1 for f in L["findings"] if "pol-its-008" in json.dumps(f))}}
    # 3 stale until re-ingest (our own run)
    fails["stale"] = {"before_lead": next(s for s in sentences(before_topic.split("\n---\n",1)[1]) if "active, verified certificate" in s),
                      "after_lead": next(s for s in sentences(after_topic.split("\n---\n",1)[1]) if "12 months" in s),
                      "pol_untouched": pol_untouched, "amd_effective": "2026-09-01",
                      "pol_links_after": [l for l in man["pol-pur-001"]["links_out"]]}
    # 4 cost and time
    D_llm = I["llm"]
    fails["cost"] = {
        "build": {"files": B["sources"], "parts": B["parts"], "calls": B["llm"]["all"]["calls"], "tokens_in": B["llm"]["all"]["tokens_in"],
                  "tokens_out": B["llm"]["all"]["tokens_out"], "usd": B["usd_at_harness_price"]["total"], "minutes": B["build_wall_minutes_estimate"]["total_live_estimate"],
                  "pages": B["pages"], "workers": 40},
        "D": {"calls": D_llm["calls"], "tokens_in": D_llm["tokens_in"], "tokens_out": D_llm["tokens_out"], "usd": usd(D_llm["tokens_in"], D_llm["tokens_out"]),
              "seconds": I["report"]["seconds"], "read_s": read["seconds"], "pages": I["report"]["pages"], "read_replayed": read["replayed"]},
        "amd": {"calls": U["llm"]["calls"], "tokens_in": U["llm"]["tokens_in"], "tokens_out": U["llm"]["tokens_out"], "usd": U["llm"]["usd"],
                "seconds": U["report"]["seconds"], "touched": U["report"]["pages_touched"], "facts_added": U["report"]["facts_added"]},
        "rn_p6": {"calls": WU["llm"]["calls"], "usd": WU["usd"], "seconds": WU["seconds"]["total"], "touched": WU["pages_touched"]},
        "rag": {"amd_parse_s": CN["rag_amd_timing"][-1]["parse_s"], "amd_chunk_s": CN["rag_amd_timing"][-1]["chunk_s"],
                "amd_chunks": CN["rag_amd_timing"][-1]["chunks"], **(rag_build or {})}}
    # 5 navigation stops too early (the race's own recorded chain for Emma, replayed)
    ans_ctx = [p for c in Q["calls"] if c["kind"] == "answer" for p in c["parts"]]
    where = []
    for m in Q["fact"]["missing"]:
        seen = [(re.search(r"\[\[([^\]]+)\]\]", p["what"]) or re.search(r"(.+)", p["what"])).group(1) for p in ans_ctx if m in (p["text"] or "")]
        holders = sorted(p.stem for p in (WIKI / "pages").glob("*.md") if m in p.read_text())
        where.append({"fact": m, "in_answer_context": seen, "pages": holders})
    fails["stops_early"] = {"chain": Q["chain"], "missing": Q["fact"]["missing"], "nav_calls": Q["nav_calls"], "where": where,
                            "why_done": next(s["why"] for s in Q["chain"] if s["step"] == "done"),
                            "pages_holding_rule": [s for s in ("topic-un-38-3-certificates", "amd-sup-2026-02", "sop-pur-001")
                                                   if "12 months" in (WIKI / "pages" / f"{s}.md").read_text()],
                            "multi_hop": {m: R["by_type"]["multi_hop"][m]["answer_correct"] for m in ("rag", "wiki", "hybrid", "sections")},
                            "pages_opened_mean": J("wiki_eval.json")["methods"]["wiki"]["pages_opened_mean"]}
    # 6 exact codes
    crd = (WIKI / "pages" / "err-crd-0207.md").read_text()
    fails["exact_codes"] = {"by_type": {m: {k: R["by_type"]["exact_code"][m][k] for k in ("n", "recall@5", "answer_correct")} for m in ("rag", "wiki")},
                            "qid": "Q-726", "question": qs["Q-726"]["question"], "gold": qs["Q-726"]["reference_answer"],
                            "page_title": front(crd)["title"], "page_line": next(s for s in crd.splitlines() if s.startswith("`ERR-CRD-0207` indicates")),
                            "wiki_answer": EWr["Q-726"]["answer"], "wiki_missing": EWr["Q-726"]["fact"]["missing"],
                            "rag_answer": RA["Q-726"]["answer"], "rag_ok": RA["Q-726"]["fact"]["ok"],
                            "index_line": next(l for l in (WIKI / "index.md").read_text().splitlines() if "err-<code>" in l),
                            "n_error_pages": json.load(open(LOGS / "wiki_build.json"))["pages_by_type"]["error"]}
    # lint
    ours = []
    for f in L["findings"]:
        s = json.dumps(f)
        if ("topic-un-38-3" in s and f["kind"] == "citation_not_found") or ("sup-brightcell-energy" in s and f["kind"] == "orphan") \
                or ("topic-un-38-3" in s and f["kind"] == "superseded" and "12 months" in s):
            ours.append({"kind": f["kind"], "source": f["source"], "detail": f["detail"]})
    topic_refs = json.load(open(WIKI / "manifest.json"))["pages"]["topic-un-38-3-certificates"]["refs"]
    fails["lint"] = {"n": L["n_findings"], "seconds": L["seconds"]["total"], "by_kind": L["by_kind"], "by_source": L["by_source"],
                     "planted": {"n": L["messiness"]["n"], "found": L["messiness"]["found"]}, "review_usd": L["review"]["usd"],
                     "ours": ours, "r35_quote_words": len(topic_refs["r35"]["quote"].split()), "r35_quote": topic_refs["r35"]["quote"]}
    (LOGS / "v5_wiki_failures.json").write_text(json.dumps({"script": "experiments/v5_wiki_data.py", **fails}, indent=1, ensure_ascii=False))

    # ---------------------------------------------------------------- engineering
    eng = {"race": {m: {k: R["overall"][m][k] for k in ("answer_correct", "fact_correct", "citation_correct", "recall@5", "retrieval_p50_s",
                                                         "retrieval_p95_s", "answer_p50_s", "answer_p95_s", "cost_per_q_usd", "llm_calls_per_q")}
                    for m in ("rag", "wiki", "hybrid", "sections")},
           "n": R["overall"]["wiki"]["n"], "targets": R["targets"],
           "build_facts": {"facts": B["facts"], "verified": B["facts_quote_verified"], "page_fixed": B["facts_page_fixed"]},
           "wiki_store": {"pages": B["pages"], "staff": B["pages_by_audience"]["staff"], "hr": B["pages_by_audience"]["hr"],
                          "words": B["wiki_words"], "links": B["links"], "links_resolved": B["links_resolved"], "references": B["references"],
                          "sections": 2520, "index_lines": len((WIKI / "index.md").read_text().splitlines()),
                          "index_tokens": next(p["tokens"] for p in Q["calls"][0]["parts"] if p["what"] == "index.md")}}

    data = {
        "d": {"file": I["source"], "header": header, "versions": versions, "clauses": clauses, "header_text": I["header"],
              "pages": len(I["raw_pages"]), "chars": len(text)},
        "read": {"parts": parts, "tokens_in": read["tokens_in"], "tokens_out": read["tokens_out"], "seconds": read["seconds"],
                 "replayed": read["replayed"], "model": "gemini-3.8-flash"},
        "reply": {"source_note": reply["source_note"], "pages": rpages, "conflicts": reply["conflicts"]},
        "checks": checks, "page2_raw": p2,
        "merge": {"map": I["report"]["merge_map"], "call": I["report"]["merge"]},
        "pages_made": pages_made, "write_calls": write_calls,
        "pol": {"front": front(pol), "infobox": infobox(pol), "sentences": sents,
                "refs": {k: {kk: v.get(kk) for kk in ("quote", "page", "section", "verified")} for k, v in refs.items()}},
        "index_lines": idx_lines, "log_lines": log_lines,
        "update": {"amd_file": U["source"], "amd_clauses": amd_cl, "diff": diff, "conflicts": U["conflicts"], "log": up_log,
                   "touched": U["report"]["updated"], "created": U["report"]["created"], "calls": upd_calls,
                   "report": {k: U["report"][k] for k in ("seconds", "usd", "facts_added", "pages_touched")},
                   "rag_chunks": [{"cite": c["cite"], "tokens": c["tokens"], "head": c["text"][:260]} for c in U["rag"]["chunks"]],
                   "pol_untouched": pol_untouched},
        "query": {"question": Q["question"], "chain": Q["chain"], "calls": qcalls, "answer": Q["answer"], "missing": Q["fact"]["missing"],
                  "rag": Q["rag_context"], "rag_recorded": Q["rag_recorded"], "counter": Q["token_counter"]},
        "brightcell": {"sources": bc_man["sources"], "sentences": bc_sents, "title": bc_man["title"]},
        "fail": fails, "eng": eng,
    }
    OUT_JS.write_text("/* Lecture 3 v5 · the LLM Wiki section. Generated by experiments/v5_wiki_data.py from experiments/logs/v5_wiki_*.json\n"
                      "   and the course's recorded logs. Do not edit by hand. */\nwindow.L3V5 = window.L3V5 || {};\nwindow.L3V5.wiki = "
                      + json.dumps(data, ensure_ascii=False) + ";\n")
    print("wrote", OUT_JS, OUT_JS.stat().st_size, "bytes;", LOGS / "v5_wiki_failures.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default="/private/tmp/claude-501/-Users-raj-Claude-Brain/e88f1a06-3b0d-4a9f-9baf-ed78173dbc73/scratchpad/facts.jsonl",
                    help="the full build's facts.jsonl (modal volume get northbridge-wiki wiki_v4/facts.jsonl .)")
    main(ap.parse_args().facts)
