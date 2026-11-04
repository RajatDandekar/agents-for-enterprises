"""Lecture 3 v5, the LLM Wiki taught on ONE document: every intermediate of the ingest, the update and the query, real.

    cd /Users/raj/Claude_Brain/enterprise-agents-course/lectures/L3-the-memory/experiments
    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run v5_wiki_modal.py            # all three steps
    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run v5_wiki_modal.py --only query

Writes logs/v5_wiki_ingest.json, logs/v5_wiki_update.json, logs/v5_wiki_query.json and the new cassettes
(ledgerline/ledgerline/cassettes/L3v5_wiki_*.jsonl, so a re-run replays at no cost).

1. INGEST D alone. A fresh, empty wiki; the course's own builder (wiki_build.build(files=[D])) ingests the Purchase Policy
   with gemini-3.8-flash. Every model call is captured: the exact prompt, the reply, tokens, seconds. The READ call is
   replayed from the full build's cassette (L3_wiki_ingest) when the request is byte-identical, so the facts are the
   very ones the 693-file wiki got from D; the WRITE calls (one per page) are live, because a one-source wiki gives each
   page fewer facts than the full build. The quote check is re-run here and shown fact by fact.
2. UPDATE: the amendment AMD-SUP-2026-02 arrives (wiki_build.update), on a copy of that one-source wiki. Before and
   after of every touched page, the conflicts the model recorded, the log line. RAG's side of the same change: parse +
   chunk the amendment with the default pipeline (structured parser, structure-aware 200-token chunks, 15% overlap),
   timed, and no model call.
3. QUERY Emma's question on the full wiki (the race's frozen copy /vol/wiki_v4_eval_wiki), replaying the race's
   recorded calls (cassettes L3v4_race_wiki_nav / _answers): the context window of every call, part by part, with
   tokens counted by Gemini's own countTokens endpoint (fallback: tiktoken o200k, labelled).
The Gemini key comes from wm-lecture6-ijepa/.env into a Modal secret; never printed.
"""
import copy
import json
import os
import pathlib
import shutil
import subprocess
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")
LOGS = HERE / "logs"
CASS = COURSE / "ledgerline" / "ledgerline" / "cassettes"
GEMINI_ENV = "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env"

D = "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"
AMD = "01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf"


def _gkey():
    if not modal.is_local() or not os.path.exists(GEMINI_ENV):
        return ""
    for line in open(GEMINI_ENV):
        if line.startswith("GEMINI_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("tesseract-ocr")
    .pip_install("openpyxl==3.1.5", "python-docx==1.1.2", "pypdf==5.1.0", "pyyaml==6.0.2", "pillow==10.4.0",
                 "pytesseract==0.3.13", "openai==1.54.4", "httpx==0.27.2", "pandas==2.2.3", "pydantic==2.9.2",
                 "fastembed==0.4.2", "numpy<2.1", "rank_bm25==0.2.2", "reportlab==4.2.5")
    .pip_install("torch==2.5.1", index_url="https://download.pytorch.org/whl/cpu")
    .pip_install("sentence-transformers==3.3.1", "scipy==1.14.1", "pdfplumber==0.11.4", "tiktoken==0.8.0")
    .env({"PYTHONPATH": "/course/ledgerline", "NB_DOCS": "/dump", "NORTHBRIDGE_DOCS": "/dump",
          "LEDGER_CASSETTES": "/tmp/cass", "LEDGER_LLM_MODE": "auto", "NB_L3_CACHE": "/vol/l3cache",
          "HF_HOME": "/vol/hf", "LEDGER_WIKI_PROVIDER": "google-direct", "PYTHONUNBUFFERED": "1"})
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: "__pycache__" in str(p) or "cassettes" in str(p) or str(p).endswith((".mp4",))
                   or "/wiki_v4/pages" in str(p) or "/wiki_v4/restricted" in str(p) or "/_index" in str(p))
    .add_local_dir(DUMP, "/dump", ignore=lambda p: "/.git" in str(p))
    .add_local_dir(CASS, "/cass_src", ignore=lambda p: not pathlib.Path(p).name.startswith(
        ("L3v4_race_wiki", "L3v5_wiki")))
)
app = modal.App("northbridge-l3-v5-wiki", image=image)
vol = modal.Volume.from_name("northbridge-wiki")
secret = modal.Secret.from_dict({"GEMINI_API_KEY": _gkey()}) if modal.is_local() else modal.Secret.from_dict({})


def _cassettes(names):
    d = pathlib.Path("/tmp/cass")
    d.mkdir(parents=True, exist_ok=True)
    for n in names:
        for src in (pathlib.Path("/cass_src") / f"{n}.jsonl", pathlib.Path("/vol/cassettes") / f"{n}.jsonl"):
            if src.exists() and not (d / src.name).exists():
                shutil.copy(src, d / src.name)


def _recorder():
    from ledgerline.course.l3.wiki_llm import WikiLLM

    class Rec(WikiLLM):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.rec = []

        def chat(self, messages, tools=None, response_format=None, **kw):
            t0 = time.time()
            r = super().chat(messages, tools, response_format, **kw)
            self.rec.append({"messages": copy.deepcopy(messages), "reply": r.content, "tokens_in": r.tokens_in,
                             "tokens_out": r.tokens_out, "seconds": r.seconds, "replayed": r.replayed,
                             "model": r.model, "wall_s": round(time.time() - t0, 3)})
            return r

    return Rec


# ------------------------------------------------------------------------------------------------ token counting
_TOK = {"how": None}


def count_tokens(text: str) -> int:
    """Gemini's own count (models/gemini-3.8-flash:countTokens); tiktoken o200k if the endpoint refuses."""
    import httpx

    if _TOK["how"] in (None, "gemini"):
        try:
            r = httpx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:countTokens",
                           headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
                           json={"contents": [{"role": "user", "parts": [{"text": text or " "}]}]}, timeout=60)
            if r.status_code == 200 and "totalTokens" in r.json():
                _TOK["how"] = "gemini countTokens (gemini-3.8-flash)"
                return int(r.json()["totalTokens"])
            _TOK["err"] = f"HTTP {r.status_code}"
        except Exception as e:  # noqa: BLE001
            _TOK["err"] = repr(e)[:120]
        _TOK["how"] = "tiktoken o200k_base (Gemini countTokens unavailable: %s)" % _TOK.get("err")
    from ledgerline.course.l3 import corpus as C

    return C.n_tokens(text or "")


# ------------------------------------------------------------------------------------------------ 1. ingest D
def ingest_D() -> dict:
    from ledgerline.course.l3 import wiki_build as WB
    from ledgerline.course.l3 import wiki_sources as WS

    _cassettes(["L3_wiki_ingest", "L3v5_wiki_D"])
    Rec = _recorder()
    llm = Rec("L3v5_wiki_D", max_tokens=16000, read_also=["L3_wiki_ingest"])
    out = pathlib.Path("/tmp/wiki_v5_D")
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    t0 = time.time()
    rep = WB.build("/dump", out, llm, workers=8, files=[D], log=print)
    wall = round(time.time() - t0, 1)
    shutil.copy("/course/ledgerline/ledgerline/wiki_v4/AGENTS.md", out / "AGENTS.md")

    src = WS.load_sources("/dump", [D])[0]
    units = WS.ingest_units(src, WS.focus_codes(WS.load_sources("/dump")))
    page_texts = {u.page: WB.norm(u.text) for u in src.units if u.page}
    raw_pages = {u.page: u.text for u in src.units if u.page}
    # the quote check, re-run fact by fact on the READ reply
    reads = [c for c in llm.rec if c["messages"][0]["role"] == "system" and "Ingest this part" in c["messages"][-1]["content"]]
    checks = []
    for c in reads:
        rj = WB._json(c["reply"])
        for p in rj.get("pages", []):
            for f in p.get("facts", []):
                q = f.get("quote") or ""
                nq = WB.norm(q)
                pg = f.get("page") if isinstance(f.get("page"), int) else None
                on_page = bool(nq) and nq in page_texts.get(pg, "")
                anywhere = [pn for pn, t in page_texts.items() if nq and nq in t]
                checks.append({"slug": p.get("slug"), "fact": f.get("fact"), "quote": q, "page": pg,
                               "section": f.get("section"), "norm_quote": nq, "on_cited_page": on_page,
                               "found_on_pages": anywhere,
                               "verdict": "verified" if on_page else ("page-fixed" if anywhere else "not found")})
    facts = [json.loads(l) for l in (out / "facts.jsonl").open()]
    pages = {p.stem: p.read_text() for p in sorted((out / "pages").glob("*.md"))}
    restricted = {p.stem: p.read_text() for p in sorted((out / "restricted").glob("*.md"))}
    man = json.loads((out / "manifest.json").read_text())
    # keep the one-source wiki on the volume for step 2 and for anyone who wants to browse it
    vol_dir = pathlib.Path("/vol/wiki_v5_D")
    shutil.rmtree(vol_dir, ignore_errors=True)
    shutil.copytree(out, vol_dir)
    return {"source": D, "header": src.header(), "status": src.status, "meta": src.meta,
            "raw_pages": raw_pages, "units": [{"loc": u.loc, "page": u.page, "text": u.text} for u in units],
            "calls": llm.rec, "report": rep, "wall_s": wall, "quote_checks": checks, "facts": facts,
            "pages": pages, "restricted": restricted, "index_md": (out / "index.md").read_text(),
            "log_md": (out / "log.md").read_text(), "manifest": man, "llm": llm.stats()}


# ------------------------------------------------------------------------------------------------ 2. update with AMD
def update_amd() -> dict:
    import difflib

    from ledgerline.course.l3 import corpus as C
    from ledgerline.course.l3 import wiki_build as WB
    from ledgerline.course.l3 import wiki_sources as WS

    _cassettes(["L3v5_wiki_update"])
    vol.reload()
    base = pathlib.Path("/vol/wiki_v5_D")
    out = pathlib.Path("/tmp/wiki_v5_DA")
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(base, out)
    before = {p.stem: p.read_text() for p in (out / "pages").glob("*.md")}
    index_before = (out / "index.md").read_text()
    log_before = (out / "log.md").read_text()
    Rec = _recorder()
    llm = Rec("L3v5_wiki_update", max_tokens=16000)
    t0 = time.time()
    rep = WB.update([AMD], "/dump", out, llm, workers=8, log=print)
    wall = round(time.time() - t0, 1)
    after = {p.stem: p.read_text() for p in (out / "pages").glob("*.md")}
    diffs = {}
    for s in sorted(set(before) | set(after)):
        a, b = before.get(s, ""), after.get(s, "")
        if a != b:
            diffs[s] = {"created": s not in before,
                        "diff": "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
                                                             f"before/{s}.md", f"after/{s}.md", n=1))}
    man = json.loads((out / "manifest.json").read_text())
    src = WS.load_sources("/dump", [AMD])[0]
    # RAG's side of the same change: parse and chunk the new file, no model call
    t1 = time.perf_counter()
    units = C.parse_file("/dump", AMD, "structured")
    t_parse = time.perf_counter() - t1
    t2 = time.perf_counter()
    chunks = C.chunk(units, "structure", 200, 0.15)
    t_chunk = time.perf_counter() - t2
    t3 = time.perf_counter()
    from ledgerline.course.l3 import rag as R

    bm = R.BM25([c.text for c in chunks])
    t_bm = time.perf_counter() - t3
    vol_dir = pathlib.Path("/vol/wiki_v5_DA")
    shutil.rmtree(vol_dir, ignore_errors=True)
    shutil.copytree(out, vol_dir)
    vol.commit()
    return {"source": AMD, "header": src.header(), "raw_pages": {u.page: u.text for u in src.units if u.page},
            "calls": llm.rec, "report": rep, "wall_s": wall, "before": before, "after": after, "diffs": diffs,
            "index_before": index_before, "index_after": (out / "index.md").read_text(),
            "log_before": log_before, "log_after": (out / "log.md").read_text(),
            "conflicts": {s: man["pages"][s].get("conflicts") for s in diffs if s in man["pages"]},
            "rag": {"units": len(units), "chunks": [{"cid": c.cid, "tokens": c.n_tokens or C.n_tokens(c.text),
                                                     "cite": c.cite, "text": c.text} for c in chunks],
                    "parse_s": round(t_parse, 4), "chunk_s": round(t_chunk, 4), "bm25_this_file_s": round(t_bm, 4),
                    "model_calls": 0},
            "llm": llm.stats()}


# ------------------------------------------------------------------------------------------------ 3. query Q
def query_Q(rag_items: list) -> dict:
    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import wiki_query as WQ

    names = ["L3v4_race_wiki_nav", "L3v4_wiki_nav", "L3v4_race_wiki_answers"]
    _cassettes(names)
    vol.reload()
    G = E.Golden("/dump")
    q = G.by_id["Q-EMMA"]
    role = E.C.role_of(q)
    w = WQ.Wiki("/vol/wiki_v4_eval_wiki", dump="/dump")
    Rec = _recorder()
    nav = Rec("L3v4_race_wiki_nav", max_tokens=4000, read_also=["L3v4_wiki_nav"])
    t0 = time.time()
    r = WQ.Navigator(w, nav).navigate(q["question"], role)
    nav_wall = round(time.time() - t0, 3)
    ans = Rec("L3v4_race_wiki_answers", max_tokens=2048)
    a = E.answer(q, r["items"], ans, answer_words=E.RACE_WORDS)
    calls = []
    for i, c in enumerate(nav.rec + ans.rec):
        parts = []
        for m in c["messages"]:
            txt = m["content"] or ""
            if m["role"] == "user" and txt.startswith("INDEX"):
                head, _, qpart = txt.rpartition("\n\nQUESTION: ")
                parts.append({"role": "user", "what": "index.md" if "(index.md)" in head[:40] else "index (slugs and titles)",
                              "chars": len(head), "tokens": count_tokens(head), "text": head})
                parts.append({"role": "user", "what": "question", "chars": len(qpart), "tokens": count_tokens(qpart),
                              "text": qpart})
            elif m["role"] == "user" and txt.startswith("Sources:"):
                body, _, qpart = txt.rpartition("\n\nQuestion: ")
                for blk in body[len("Sources:\n\n"):].split("\n\n["):
                    blk = blk if blk.startswith("[") else "[" + blk
                    parts.append({"role": "user", "what": blk.split("\n", 1)[0][:120], "chars": len(blk),
                                  "tokens": count_tokens(blk), "text": blk})
                parts.append({"role": "user", "what": "question", "chars": len(qpart), "tokens": count_tokens(qpart),
                              "text": qpart})
            elif m["role"] == "user" and txt.startswith("# "):
                for pg in txt.split("\n\n# "):
                    pg = pg if pg.startswith("# ") else "# " + pg
                    parts.append({"role": "user", "what": "page " + pg.split("\n", 1)[0][2:120], "chars": len(pg),
                                  "tokens": count_tokens(pg), "text": pg})
            else:
                parts.append({"role": m["role"], "what": "system prompt" if m["role"] == "system" else
                              ("the model's reply on the previous turn" if m["role"] == "assistant" else "user"),
                              "chars": len(txt), "tokens": count_tokens(txt), "text": txt})
        calls.append({"call": i + 1, "kind": "navigate" if i < len(nav.rec) else "answer",
                      "tokens_in_reported": c["tokens_in"], "tokens_out": c["tokens_out"], "seconds": c["seconds"],
                      "replayed": c["replayed"], "reply": c["reply"], "parts": parts})
    # RAG's context for the same question: the race's ten chunks, rendered by the same answer prompt
    rag_msgs = E.answer_messages(q, rag_items, max_chars=9000, answer_words=E.RACE_WORDS)
    rag_parts = [{"what": "system prompt", "tokens": count_tokens(rag_msgs[0]["content"])}]
    body, _, qpart = rag_msgs[1]["content"].rpartition("\n\nQuestion: ")
    for it, blk in zip(rag_items, body[len("Sources:\n\n"):].split("\n\n[")):
        blk = blk if blk.startswith("[") else "[" + blk
        rag_parts.append({"what": it.get("cite"), "tokens": count_tokens(blk), "chars": len(blk)})
    rag_parts.append({"what": "question", "tokens": count_tokens(qpart)})
    return {"question": q["question"], "role": role, "wiki_dir": "/vol/wiki_v4_eval_wiki (the race's frozen copy)",
            "chain": r["chain"], "nav_calls": r["nav_calls"], "nav_wall_s": nav_wall, "opened": r["opened"],
            "answer": a["answer"], "answer_cited": a["cited"], "fact": E.fact_check(q, a["answer"], G),
            "calls": calls, "rag_context": rag_parts, "token_counter": _TOK["how"],
            "brightcell_page": w.page_text("sup-brightcell-energy"),
            "brightcell_manifest": w.pages["sup-brightcell-energy"]}


# ------------------------------------------------------------------------------------------------ 4. counts
def counts(read_msgs: list) -> dict:
    """Tokens per part of the READ prompt the ingest sent for D (Gemini countTokens), and RAG's parse + chunk of the
    amendment timed warm (a second run, after the tokenizer is loaded)."""
    from ledgerline.course.l3 import corpus as C

    sys_, user = read_msgs[0]["content"], read_msgs[1]["content"]
    schema, _, reg = sys_.partition("REGISTRY:")
    head, _, rest = user.partition("\n\nPART ")
    part_text, _, rules = rest.partition("\n-----\n\nIngest this part.")
    parts = [("instructions + AGENTS.md (the schema)", schema), ("REGISTRY: slugs that exist", "REGISTRY:" + reg),
             ("SOURCE header", head), ("D's text, pages 1-4", "PART " + part_text),
             ("rules + reply format", "Ingest this part." + rules)]
    out = {"read_prompt_parts": [{"what": w, "chars": len(t), "tokens": count_tokens(t)} for w, t in parts],
           "registry_lines": reg.strip().count("\n") + 1}
    timing = []
    for i in range(3):
        t1 = time.perf_counter()
        units = C.parse_file("/dump", AMD, "structured")
        t2 = time.perf_counter()
        chunks = C.chunk(units, "structure", 200, 0.15)
        t3 = time.perf_counter()
        timing.append({"run": i + 1, "parse_s": round(t2 - t1, 4), "chunk_s": round(t3 - t2, 4), "chunks": len(chunks)})
    out["rag_amd_timing"] = timing
    out["token_counter"] = _TOK["how"]
    return out


@app.function(volumes={"/vol": vol}, secrets=[secret], timeout=3600, cpu=4, memory=8192)
def run(only: str = "", rag_items: list | None = None, read_msgs: list | None = None) -> dict:
    out = {}
    if "counts" in only:
        out["counts"] = counts(read_msgs)
    if not only or "ingest" in only:
        out["ingest"] = ingest_D()
        vol.commit()
    if not only or "update" in only:
        out["update"] = update_amd()
    if not only or "query" in only:
        out["query"] = query_Q(rag_items or [])
    cass = {}
    for p in pathlib.Path("/tmp/cass").glob("L3v5_wiki_*.jsonl"):
        cass[p.name] = p.read_text()
    out["_cassettes"] = cass
    return out


@app.local_entrypoint()
def main(only: str = ""):
    ex = json.load(open(LOGS / "deck_extract.json"))["race_items"]["Q-EMMA"]
    rec = [r for r in json.load(open(LOGS / "race_answers" / "rag__250.json"))["records"] if r["id"] == "Q-EMMA"][0]
    meta = {i["id"]: i for i in rec["items"]}
    rag_items = [{"id": it["id"], "cite": it["cite"], "text": it["body"], "meta": {}} for it in ex]
    read_msgs = None
    if "counts" in only:
        read_msgs = json.load(open(LOGS / "v5_wiki_ingest.json"))["calls"][0]["messages"]
    res = run.remote(only, rag_items, read_msgs)
    for name, txt in res.pop("_cassettes", {}).items():
        (CASS / name).write_text(txt)
        print("cassette", name)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for k, v in res.items():
        v = {"generated": stamp, "script": "experiments/v5_wiki_modal.py", **v}
        if k == "query":
            v["rag_recorded"] = {"tokens_in": rec["tokens_in"], "tokens_out": rec["tokens_out"],
                                 "items": [m["cite"] for m in rec["items"]]}
        (LOGS / f"v5_wiki_{k}.json").write_text(json.dumps(v, indent=1, ensure_ascii=False, default=str))
        print("wrote", LOGS / f"v5_wiki_{k}.json")
