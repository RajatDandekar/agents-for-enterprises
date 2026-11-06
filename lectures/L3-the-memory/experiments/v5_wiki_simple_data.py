"""Lecture 3 v5, the LLM Wiki made simple: the data for the reworked section (6 Nov review), from recorded runs only.

    cd /Users/raj/Claude_Brain/enterprise-agents-course/lectures/L3-the-memory/experiments
    /Users/raj/.venv/bin/python v5_wiki_simple_data.py

Reads (no model call):
  logs/v5_wiki_simple_ingest.json  the one-page amendment AMD-SUP-2026-02 ingested ALONE (v5_wiki_simple_modal.py, 6 Nov)
  logs/v5_wiki_simple_query.json   four staff questions read through the small wiki D + amendment (9 pages), call by call
  logs/v5_wiki_ingest.json         D (POL-PUR-001) ingested alone: its six pages (v5_wiki_modal.py, 4 Nov)
  logs/v5_wiki_update.json         the amendment ingested into D's wiki (v5_wiki_modal.py, 4 Nov)
Writes window.L3V5.wiki.simple into ../v5/wiki_data.js, between the markers below (the rest of the file is written by
v5_wiki_data.py and left as it is). Every highlight the slides draw is an exact substring checked here.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
OUT_JS = HERE.parent / "v5" / "wiki_data.js"
BEGIN, END = "/* v5_wiki_simple_data.py: begin */", "/* v5_wiki_simple_data.py: end */"
NAV_RUN = "S-4"  # the run the navigation animation shows: its second turn follows a [[link]] the first page gave it


def J(name):
    return json.load(open(LOGS / name))


def strip_refs(s):
    return re.sub(r"\s*(\[\^r\d+\])+", "", s).strip()


def unlink(s):
    return re.sub(r"\[\[[^|\]]+\|([^\]]+)\]\]", r"\1", re.sub(r"\[\[([^|\]]+)\]\]", r"\1", s))


def need(text, sub, what):
    assert sub in text, f"highlight not found ({what}): {sub!r}"
    return sub


def amd_doc(raw):
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    hdr, i = [], lines.index("Value") + 1
    while lines[i] != "Version history":
        hdr.append([lines[i], lines[i + 1]])
        i += 2
    clauses, cur = [], None
    for l in lines[lines.index("1. What changes"):]:
        if l.startswith("Northbridge Cycles Ltd"):
            break
        m, h = re.match(r"^(\d\.\d) (.*)$", l), re.match(r"^(\d)\. (.*)$", l)
        if h:
            clauses.append({"id": h.group(1), "kind": "head", "text": h.group(2)})
            cur = None
        elif m:
            cur = {"id": m.group(1), "kind": "clause", "text": m.group(2)}
            clauses.append(cur)
        elif cur:
            cur["text"] += " " + l
    return {"title": lines[0], "header": hdr, "clauses": clauses}


def index_lines(md):
    return [l for l in md.split("\n") if l.startswith("- ") or l.startswith("## ")]


def log_lines(md):
    return [l for l in md.split("\n") if l.startswith("## [")]


def page_slug_of_write(call):
    m = re.search(r"(?m)^PAGE: (\S+) \(type", call["messages"][-1]["content"])
    return m.group(1) if m else None


def main():
    A, Q, DI, U = J("v5_wiki_simple_ingest.json"), J("v5_wiki_simple_query.json"), J("v5_wiki_ingest.json"), J("v5_wiki_update.json")

    # ---- 1. the amendment alone
    amd = amd_doc(A["raw_pages"]["1"])
    read = json.loads(re.sub(r"^```(?:json)?|```$", "", A["calls"][0]["reply"].strip()).strip())
    calls = []
    for c in A["calls"]:
        txt = c["messages"][-1]["content"]
        kind = "read" if "Ingest this part" in txt else ("write" if page_slug_of_write(c) else "merge")
        calls.append({"kind": kind, "page": page_slug_of_write(c), "tokens_in": c["tokens_in"], "tokens_out": c["tokens_out"],
                      "seconds": c["seconds"], "replayed": c["replayed"]})
    rep = A["report"]
    alone = {"file": A["source"], "tree": A["tree"], "index_md": A["index_md"], "index_lines": index_lines(A["index_md"]),
             "log_lines": log_lines(A["log_md"]), "pages": A["pages"],
             "reply_pages": [{"slug": p["slug"], "type": p.get("type"), "title": p.get("title"), "n": len(p.get("facts", []))}
                             for p in read["pages"]],
             "reply_fact": next(f for p in read["pages"] if p["slug"] == "amd-sup-2026-02" for f in p["facts"]
                                if "12 months" in f["quote"]),
             "calls": calls, "facts": rep["facts"], "verified": rep["facts_quote_verified"], "links": rep["links"],
             "refs": rep["references"], "words": rep["wiki_words"], "seconds": rep["seconds"], "llm": rep["llm"]["all"],
             "read_llm": rep["llm"]["read"], "write_llm": rep["llm"]["write"], "generated": A["generated"]}
    amdp = A["pages"]["amd-sup-2026-02"]
    alone["anat"] = {  # the parts of one page the anatomy slide points at (each must be in the file)
        "front": need(amdp, "---\ntitle:", "front matter"), "lead": need(amdp, "AMD-SUP-2026-02 is an amendment to", "lead"),
        "section": need(amdp, "### 1. What changes", "a section"), "link": need(amdp, "[[pol-sup-003|POL-SUP-003]]", "a link"),
        "key": need(amdp, "60 days past the order date [^r2]", "a key"),
        "ref": need(amdp, "[^r2]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §1. What changes", "a reference")}

    # ---- 2. D alone: six pages, which sections fed which page
    sec_of = lambda s: (re.match(r"^(\d)\.", s or "") or [None, "hdr"])[1]
    dmap = {}
    for f in DI["facts"]:
        dmap.setdefault(f["slug"], [])
        k = sec_of(f.get("section"))
        if k not in dmap[f["slug"]]:
            dmap[f["slug"]].append(k)
    front = lambda md: dict(re.findall(r'(?m)^(\w+): "(.*)"$', md.split("---")[1]))
    dpages = [{"slug": s, "title": front(DI["pages"][s]).get("title"), "type": front(DI["pages"][s]).get("type"),
               "n": sum(1 for f in DI["facts"] if f["slug"] == s), "lines": len(DI["pages"][s].split("\n")),
               "secs": dmap.get(s, [])} for s in DI["pages"]]
    dsecs = [{"id": "hdr", "title": "Header and version history"}] + [
        {"id": m.group(1), "title": m.group(2)} for m in re.finditer(r"(?m)^(\d)\. (.+)$", DI["raw_pages"]["1"] + "\n" + DI["raw_pages"]["2"])]
    seen = set()
    dsecs = [s for s in dsecs if not (s["id"] in seen or seen.add(s["id"]))]
    dwiki = {"file": DI["source"], "pages": dpages, "sections": dsecs, "index_lines": index_lines(DI["index_md"]),
             "log_lines": log_lines(DI["log_md"]), "facts": len(DI["facts"]), "llm": DI["llm"],
             "merge_map": DI["report"].get("merge_map", {})}

    # ---- 3. the amendment joins D's wiki
    topic_b, topic_a = U["before"]["topic-un-38-3-certificates"], U["after"]["topic-un-38-3-certificates"]
    lead = lambda md: next(p for p in md.split("---", 2)[2].split("\n\n") if p.strip() and not p.lstrip().startswith("|"))
    join = {"created": U["report"]["created"], "updated": U["report"]["updated"], "log_lines": log_lines(U["log_after"]),
            "tree": Q["tree"], "index_lines": index_lines(U["index_after"]),
            "lead_before": unlink(strip_refs(lead(topic_b))), "lead_after": unlink(strip_refs(lead(topic_a))),
            "calls": U["llm"]["calls"], "seconds": U["report"]["seconds"], "usd": U["report"]["usd"],
            "facts_added": U["report"]["facts_added"]}

    # ---- 4. one question through the small wiki, for the animation
    run = next(r for r in Q["runs"] if r["id"] == NAV_RUN)
    turns = []
    for i, c in enumerate(run["nav_calls_rec"]):
        a = json.loads(re.sub(r"^```(?:json)?|```$", "", c["reply"].strip()).strip())
        turns.append({"turn": i + 1, "action": a.get("action"), "pages": a.get("pages", []), "why": a.get("why", ""),
                      "tokens_in": c["tokens_in"], "tokens_out": c["tokens_out"], "seconds": c["seconds"]})
    P = Q["pages"]
    topic, role = P["topic-un-38-3-certificates"], P["role-pur-senior-buyer"]
    ans = run["answer"]
    nav = {"id": run["id"], "question": run["question"], "role": run["role"], "chain": run["chain"], "turns": turns,
           "items": run["items"], "answer": ans, "cited": run["answer_cited"],
           "answer_tokens_in": run["answer_tokens_in"], "answer_tokens_out": run["answer_tokens_out"],
           "answer_seconds": run["answer_llm_seconds"], "nav_seconds": run["nav_llm_seconds"],
           "nav_tokens_in": run["nav_tokens_in"], "nav_wall_s": run["nav_wall_s"],
           "index_md": Q["index_md"], "pages": {s: P[s] for s in run["opened"]}, "opened": run["opened"],
           "amd_clause": next(c["text"] for c in amd["clauses"] if c["id"] == "3.2"),
           "hl": {"topic_rule": need(topic, "issued within the last 12 months and extends at least 60 days beyond the purchase order date", "topic rule"),
                  "topic_link": need(topic, "[[role-pur-senior-buyer|senior buyer]] runs the certificate-expiry report", "topic link"),
                  "topic_wrong": need(topic, "| System enforcement | Ledgerline order blocking |", "topic infobox"),
                  "role_duty": need(role, "required to run the certificate-expiry report (MAN-PUR-72 §22.6) on the first working day of every month using a 90-day window", "role duty"),
                  "role_ref": need(role, "[^r1]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §3. What purchase staff must do", "role ref"),
                  "ans_rule": need(ans, "issued within the last 12 months [1][2][3]", "answer rule"),
                  "ans_buyer": need(ans, "**Senior Buyer:** Runs the certificate-expiry report", "answer buyer"),
                  "ans_wrong": need(ans, "Automatically enforces order blocking", "answer wrong")},
           "others": [{"id": r["id"], "question": r["question"], "steps": [[c["step"], c.get("what")] for c in r["chain"]],
                       "nav_calls": r["nav_calls"], "answer_head": r["answer"].split("\n")[0][:220]} for r in Q["runs"]]}
    assert [i["id"] for i in run["items"]][4] == "wiki:role-pur-senior-buyer" and 5 in run["answer_cited"]

    simple = {"amd": amd, "alone": alone, "d": dwiki, "join": join, "nav": nav,
              "logs": ["experiments/logs/v5_wiki_simple_ingest.json", "experiments/logs/v5_wiki_simple_query.json",
                       "experiments/logs/v5_wiki_ingest.json", "experiments/logs/v5_wiki_update.json"]}
    js = OUT_JS.read_text()
    if BEGIN in js:
        js = js[: js.index(BEGIN)].rstrip() + "\n" + js[js.index(END) + len(END):].lstrip()
    block = f"{BEGIN}\nwindow.L3V5.wiki.simple = {json.dumps(simple, ensure_ascii=False)};\n{END}\n"
    OUT_JS.write_text(js.rstrip() + "\n" + block)
    print("wrote", OUT_JS, f"(simple: {len(block):,} chars)")
    print("alone:", alone["calls"][0], "pages", [p["slug"] for p in alone["reply_pages"]], "facts", alone["facts"], alone["verified"])
    print("D pages:", [(p["slug"], p["n"], p["secs"]) for p in dpages])
    print("nav:", [(t["turn"], t["action"], t["pages"]) for t in turns])


if __name__ == "__main__":
    main()
