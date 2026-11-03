"""Build the Wiki Explorer's data (lectures/L3-the-memory/wiki_explorer/data/*.json) from the built wiki and the logs.

    python3 wiki_explorer_build.py [--wiki /path/to/wiki_v4]    # default: ledgerline/ledgerline/wiki_v4

Writes:
  data/wiki.json    every staff page (title, type, summary, infobox, body, references with quotes, links out,
                    what links here, history from log.md); HR pages appear only as restricted stubs (AGENTS.md §7)
  data/chains.json  query chains (Q-EMMA, Q-0412 from logs/wiki_query_chains.json; plus a sample from the golden-set
                    run in logs/wiki_eval_wiki.json), as steps index -> page -> link -> source -> answer
  data/log.json     log.md as lines
Stdlib only; runs on the laptop (no parsing, no model calls).
"""
import argparse
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2]
OUT = HERE.parent / "wiki_explorer" / "data"
LOGS = HERE / "logs"
REF = re.compile(r"\[\^(r\d+)\]")


def parse_page(text):
    fm = {}
    if text.startswith("---"):
        head, body = text[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                try:
                    fm[k.strip()] = json.loads(v.strip())
                except json.JSONDecodeError:
                    fm[k.strip()] = v.strip()
        return fm, body.lstrip("\n")
    return fm, text


def strip_infobox(body):
    """The page file starts with the infobox as a 2-column table; the explorer draws it as a box instead."""
    lines = body.split("\n")
    if lines and lines[0].startswith("| | |"):
        i = 0
        while i < len(lines) and lines[i].startswith("|"):
            i += 1
        return "\n".join(lines[i:]).lstrip("\n")
    return body


def build_pages(wiki):
    man = json.loads((wiki / "manifest.json").read_text())
    log_lines = (wiki / "log.md").read_text().splitlines()
    hist = {}
    for ln in log_lines:
        if not ln.startswith("## ["):
            continue
        for s in re.findall(r"[a-z0-9][a-z0-9-]+", ln.split("|", 3)[-1]):
            hist.setdefault(s, []).append(ln[3:])
    pages, inbound = {}, {}
    for s, p in man["pages"].items():
        for l in p.get("links_out", []):
            inbound.setdefault(l, []).append(s)
    for s, p in man["pages"].items():
        if p["audience"] == "hr":
            pages[s] = {"title": p["title"], "type": p["type"], "summary": "restricted to HR", "restricted": True}
            continue
        fm, body = parse_page((wiki / p["path"]).read_text())
        body = strip_infobox(body)
        main_body = re.sub(r"\n## References\n.*$", "", body, flags=re.S)
        order = []
        for k in REF.findall(main_body):
            if k not in order and k in p.get("refs", {}):
                order.append(k)
        pages[s] = {"title": p["title"], "type": p["type"], "summary": p.get("summary", ""),
                    "status": p.get("status"), "infobox": p.get("infobox") or {}, "body": main_body,
                    "refs": p.get("refs", {}), "refs_order": order, "links_out": p.get("links_out", []),
                    "inbound": sorted(x for x in inbound.get(s, []) if man["pages"].get(x, {}).get("audience") != "hr"),
                    "sources": [x for x in p.get("sources", []) if "CONFIDENTIAL" not in x],
                    "conflicts": p.get("conflicts", []), "updated": fm.get("updated", ""),
                    "history": [h for h in hist.get(s, []) if f" {s}" in h or f"| {s}" in h or f", {s}" in h][:30]}
    return man, pages, log_lines


def chain_steps(rec, kind_label):
    """A navigation record (chain + calls) as explorer steps."""
    chain, calls = rec.get("chain") or [], rec.get("calls") or []
    by_turn = {c["turn"]: c for c in calls}
    steps = []
    opened_next = {}
    for c in chain:
        if c["step"] in ("page", "link", "list"):
            opened_next.setdefault(c.get("turn"), []).append(c["what"])
    first = chain[0] if chain else {"step": "index"}
    c1 = by_turn.get(1, {})
    if first["step"] == "index":
        steps.append({"kind": "index", "label": "index.md", "detail": "reads the catalogue and chooses pages",
                      "chose": opened_next.get(1, []), "call": 1, "tokens_in": c1.get("tokens_in"),
                      "tokens_out": c1.get("tokens_out"), "seconds": c1.get("llm_seconds")})
    else:
        steps.append({"kind": "search", "label": "search", "detail": "wiki sections found by BM25 + embeddings",
                      "sections": first.get("what", []), "ms": rec.get("search_ms")})
    items = {i["id"]: i for i in rec.get("items", [])}
    for c in chain[1:]:
        t = c.get("turn")
        call = by_turn.get(t, {})
        if c["step"] in ("page", "link", "list"):
            nxt = opened_next.get((t or 0) + 1, [])
            steps.append({"kind": c["step"], "label": c["what"], "page": c["what"],
                          "detail": (f"followed the link from [[{c['from']}]]" if c.get("from") else
                                     "chosen from the index") + f" (decided by call {t})",
                          "next_links": nxt, "call": t, "tokens_in": call.get("tokens_in"),
                          "tokens_out": call.get("tokens_out"), "seconds": call.get("llm_seconds")})
        elif c["step"] == "rule":
            steps.append({"kind": "rule", "label": c["what"], "page": c["what"],
                          "detail": f"a rule that applies: linked from [[{c.get('from')}]] ({c.get('votes')} page(s) read "
                                    "link to it), opened by code before the answer, no LLM call"})
        elif c["step"] == "source":
            ex = next((i for i in rec.get("items", []) if i.get("text") and c.get("what") and
                       (c["what"].rsplit("/", 1)[-1][:25] in (i.get("cite") or "") or
                        c["what"].rsplit("/", 1)[-1] in str(i.get("id")))), None)
            ex = ex or next((i for i in rec.get("items", []) if i.get("text")), None)
            loc = ", ".join(str(x) for x in [f"p. {c['page']}" if c.get("page") else "",
                                             f"sheet {c['sheet']}" if c.get("sheet") else "",
                                             f"find '{c['find']}'" if c.get("find") else ""] if x)
            steps.append({"kind": "source", "label": (c.get("what") or "").rsplit("/", 1)[-1][:40], "file": c.get("what"),
                          "loc": loc, "detail": f"opened the raw source ({c.get('units', 0)} unit(s))",
                          "excerpt": (ex or {}).get("text"), "call": t, "tokens_in": call.get("tokens_in"),
                          "tokens_out": call.get("tokens_out"), "seconds": call.get("llm_seconds")})
        elif c["step"] in ("denied", "missing"):
            steps.append({"kind": c["step"], "label": c["what"], "detail": "access denied (HR only)" if
                          c["step"] == "denied" else "no such page", "call": t})
        elif c["step"] == "done":
            call = by_turn.get(t, {})
            steps.append({"kind": "done", "label": "enough", "detail": c.get("why", ""), "call": t,
                          "tokens_in": call.get("tokens_in"), "tokens_out": call.get("tokens_out"),
                          "seconds": call.get("llm_seconds")})
    steps.append({"kind": "answer", "label": "answer", "detail": "the shared answer step",
                  "tokens_in": rec.get("answer_tokens_in"), "tokens_out": rec.get("answer_tokens_out"),
                  "seconds": rec.get("answer_seconds"), "call": "answer"})
    return steps


CHAIN_NOTE = ("Recorded on 3 Nov 2026 on the final index.md (logs/wiki_query_chains.json); the same chains replay "
              "from the golden-set cassettes.")


def build_chains():
    out = {}
    p = LOGS / "wiki_query_chains.json"
    if p.exists():
        d = json.loads(p.read_text())
        for qid, kinds in d.get("chains", {}).items():
            for kind, rec in kinds.items():
                key = qid if kind == "wiki" else f"{qid} ({kind})"
                cited = []
                for n in rec.get("cited") or []:
                    if 0 < n <= len(rec["items"]):
                        cited.append(rec["items"][n - 1].get("cite") or rec["items"][n - 1]["id"])
                ti = (rec.get("tokens_in") or 0) + (rec.get("answer_tokens_in") or 0)
                to = (rec.get("tokens_out") or 0) + (rec.get("answer_tokens_out") or 0)
                out[key] = {"note": CHAIN_NOTE, "question": rec["question"], "kind": {"wiki": "LLM Wiki (navigation)",
                            "wiki-rules": "LLM Wiki (navigation + rules that apply)"}.get(kind,
                            "Hybrid (search wiki sections, then navigate)"), "steps": chain_steps(rec, kind),
                            "answer": rec.get("answer"), "cited": cited, "fact": rec.get("fact"),
                            "totals": {"llm_calls": (rec.get("nav_calls") or 0) + 1, "tokens_in": ti, "tokens_out": to,
                                       "seconds": round(sum(c.get("llm_seconds") or 0 for c in rec.get("calls") or [])
                                                        + (rec.get("search_ms") or 0) / 1000
                                                        + (rec.get("answer_seconds") or 0), 2)}}
        fb = d.get("fileback") or {}
        for label, rec in (fb.get("again") or {}).items():
            out[f"Q-EMMA after file-back ({label})"] = {
                "question": rec["question"], "kind": "LLM Wiki after the answer was filed back",
                "steps": chain_steps({**rec, "calls": []}, "wiki"), "answer": rec.get("answer"), "cited": [],
                "fact": rec.get("fact"), "totals": {"llm_calls": rec.get("nav_calls", 0) + 1,
                                                    "tokens_in": rec.get("tokens_in", 0), "tokens_out": 0,
                                                    "seconds": rec.get("seconds")}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default=str(COURSE / "ledgerline" / "ledgerline" / "wiki_v4"))
    a = ap.parse_args()
    wiki = pathlib.Path(a.wiki)
    man, pages, log_lines = build_pages(wiki)
    stats = {}
    bp = LOGS / "wiki_build.json"
    if bp.exists():
        b = json.loads(bp.read_text())
        stats = {"pages": b.get("pages"), "links": b.get("links"), "references": b.get("references"),
                 "facts": b.get("facts"), "build": f"{b['seconds']['total'] / 60:.0f} min, "
                                                   f"{b['llm']['all']['calls']} LLM calls, ${b['llm']['all']['usd']:.2f}"}
    OUT.mkdir(parents=True, exist_ok=True)
    lists = {f.stem: f.read_text() for f in sorted((wiki / "lists").glob("list-*.md"))} if (wiki / "lists").exists() else {}
    index_md = (wiki / "index.md").read_text()
    # catalog.json is small (loaded first); one file per page is fetched when the page is opened
    cat = {s: {k: p.get(k) for k in ("title", "type", "summary", "status", "restricted")} for s, p in pages.items()}
    (OUT / "wiki.json").unlink(missing_ok=True)
    (OUT / "catalog.json").write_text(json.dumps({"pages": cat, "lists": lists, "index_md": index_md, "stats": stats},
                                                 ensure_ascii=False))
    pdir = OUT / "pages"
    if pdir.exists():
        for f in pdir.glob("*.json"):
            f.unlink()
    pdir.mkdir(exist_ok=True)
    for s, p in pages.items():
        (pdir / f"{s}.json").write_text(json.dumps(p, ensure_ascii=False))
    extra = {}
    up = LOGS / "wiki_update.json"
    if up.exists():
        u = json.loads(up.read_text())
        extra["update"] = {"files": u["files"], "updated": u["updated"], "created": u["created"],
                           "seconds": u["seconds"], "usd": u["usd"], "calls": u["llm"]["calls"],
                           "facts_added": u.get("facts_added")}
    li = LOGS / "wiki_lint.json"
    if li.exists():
        l = json.loads(li.read_text())
        extra["lint"] = {"n_findings": l["n_findings"], "by_kind": l["by_kind"], "found": l["messiness"]["found"],
                         "found_strict": l["messiness"]["found_strict"], "n": l["messiness"]["n"],
                         "missed": l["messiness"]["missed"],
                         "items": [{k: r[k] for k in ("id", "kind", "what", "found", "found_strict", "labels")}
                                   for r in l["messiness"]["items"]]}
    (OUT / "chains.json").write_text(json.dumps({"chains": build_chains(), **extra}, ensure_ascii=False, indent=1))
    (OUT / "log.json").write_text(json.dumps({"lines": [l[3:] for l in log_lines if l.startswith("## [")]},
                                             ensure_ascii=False))
    print(f"{len(pages)} pages, {len(build_chains())} chains -> {OUT}")


if __name__ == "__main__":
    main()
