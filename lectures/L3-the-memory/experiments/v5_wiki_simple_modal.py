"""Lecture 3 v5, the LLM Wiki made simple: (1) the one-page amendment ingested ALONE into an empty wiki, and
(2) real questions read through the small wiki (D + the amendment, 9 pages) by the course's own Navigator, recorded
call by call, for the navigation animation (index.md -> a page -> a linked page -> the answer with its citation).

    cd /Users/raj/Claude_Brain/enterprise-agents-course/lectures/L3-the-memory/experiments
    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run v5_wiki_simple_modal.py
    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run v5_wiki_simple_modal.py --only query

Writes logs/v5_wiki_simple_ingest.json and logs/v5_wiki_simple_query.json, and the cassettes
ledgerline/ledgerline/cassettes/L3v5_wiki_simple_*.jsonl (a re-run replays at no cost).

1. INGEST the amendment AMD-SUP-2026-02 (one PDF page) alone: wiki_build.build(files=[AMD]) on a fresh, empty folder,
   gemini-3.8-flash (Google direct). Every call captured (prompt, reply, tokens, seconds); the quote check re-run fact
   by fact; the files it wrote (pages/*.md, index.md, log.md) kept whole.
2. QUERY: the small wiki /vol/wiki_v5_DA (D, then the amendment, written by v5_wiki_modal.py on 4 Nov) is read by
   wiki_query.Navigator (max 4 turns, as in the race), then the shared answer step (evaluate.answer, 250 words, the
   race's setting). Several staff questions are run; every chain is logged, and the slide uses one whose chain follows a
   [[link]] (all runs are kept in the log, none edited).
The Gemini key comes from wm-lecture6-ijepa/.env into a Modal secret; never printed.
"""
import copy
import json
import os
import pathlib
import shutil
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")
LOGS = HERE / "logs"
CASS = COURSE / "ledgerline" / "ledgerline" / "cassettes"
GEMINI_ENV = "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env"

AMD = "01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf"
QUESTIONS = [
    {"id": "S-1", "asker_role": "PUR-EXEC",
     "question": "Our supplier's UN 38.3 certificate for the BAT-500 battery packs was issued 18 months ago. Can we still place the first order?"},
    {"id": "S-2", "asker_role": "PUR-EXEC",
     "question": "Can I buy the battery packs from Brightcell Energy? They quote £104."},
    {"id": "S-3", "asker_role": "PUR-EXEC",
     "question": "A new supplier quotes less for lithium battery packs. Is that a reason to switch suppliers?"},
    {"id": "S-4", "asker_role": "PUR-EXEC",
     "question": "How old may a UN 38.3 certificate be when we order lithium-cell parts, and who checks it?"},
]


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
    .add_local_dir(CASS, "/cass_src", ignore=lambda p: not pathlib.Path(p).name.startswith("L3v5_wiki_simple"))
)
app = modal.App("northbridge-l3-v5-wiki-simple", image=image)
vol = modal.Volume.from_name("northbridge-wiki")
secret = modal.Secret.from_dict({"GEMINI_API_KEY": _gkey()}) if modal.is_local() else modal.Secret.from_dict({})


def _cassettes(names):
    d = pathlib.Path("/tmp/cass")
    d.mkdir(parents=True, exist_ok=True)
    for n in names:
        src = pathlib.Path("/cass_src") / f"{n}.jsonl"
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


def ingest_A() -> dict:
    from ledgerline.course.l3 import wiki_build as WB
    from ledgerline.course.l3 import wiki_sources as WS

    _cassettes(["L3v5_wiki_simple_A"])
    Rec = _recorder()
    llm = Rec("L3v5_wiki_simple_A", max_tokens=16000)
    out = pathlib.Path("/tmp/wiki_v5_A")
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    t0 = time.time()
    rep = WB.build("/dump", out, llm, workers=8, files=[AMD], log=print)
    wall = round(time.time() - t0, 1)
    src = WS.load_sources("/dump", [AMD])[0]
    page_texts = {u.page: WB.norm(u.text) for u in src.units if u.page}
    checks = []
    for c in llm.rec:
        if not (c["messages"][0]["role"] == "system" and "Ingest this part" in c["messages"][-1]["content"]):
            continue
        rj = WB._json(c["reply"])
        for p in rj.get("pages", []):
            for f in p.get("facts", []):
                q = f.get("quote") or ""
                nq = WB.norm(q)
                pg = f.get("page") if isinstance(f.get("page"), int) else None
                on_page = bool(nq) and nq in page_texts.get(pg, "")
                checks.append({"slug": p.get("slug"), "fact": f.get("fact"), "quote": q, "page": pg,
                               "section": f.get("section"), "verdict": "verified" if on_page else "not found"})
    tree = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    pages = {p.stem: p.read_text() for p in sorted((out / "pages").glob("*.md"))}
    vol_dir = pathlib.Path("/vol/wiki_v5_A")
    shutil.rmtree(vol_dir, ignore_errors=True)
    shutil.copytree(out, vol_dir)
    vol.commit()
    return {"source": AMD, "header": src.header(), "raw_pages": {u.page: u.text for u in src.units if u.page},
            "calls": llm.rec, "report": rep, "wall_s": wall, "quote_checks": checks, "tree": tree, "pages": pages,
            "index_md": (out / "index.md").read_text(), "log_md": (out / "log.md").read_text(),
            "manifest": json.loads((out / "manifest.json").read_text()), "llm": llm.stats()}


def query_small() -> dict:
    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import wiki_query as WQ

    _cassettes(["L3v5_wiki_simple_nav", "L3v5_wiki_simple_answers"])
    vol.reload()
    root = pathlib.Path("/vol/wiki_v5_DA")
    w = WQ.Wiki(root, dump="/dump")
    tree = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
    runs = []
    for q in QUESTIONS:
        Rec = _recorder()
        nav = Rec("L3v5_wiki_simple_nav", max_tokens=4000)
        t0 = time.time()
        r = WQ.Navigator(w, nav).navigate(q["question"], q["asker_role"])
        nav_wall = round(time.time() - t0, 3)
        ans = Rec("L3v5_wiki_simple_answers", max_tokens=2048)
        a = E.answer(q, r["items"], ans, answer_words=E.RACE_WORDS)
        runs.append({"id": q["id"], "question": q["question"], "role": q["asker_role"], "chain": r["chain"],
                     "opened": r["opened"], "nav_calls": r["nav_calls"], "nav_tokens_in": r["tokens_in"],
                     "nav_tokens_out": r["tokens_out"], "nav_llm_seconds": r["llm_seconds"], "nav_wall_s": nav_wall,
                     "items": [{"id": i.get("id"), "cite": i.get("cite")} for i in r["items"]],
                     "answer": a["answer"], "answer_cited": a["cited"], "answer_tokens_in": a["tokens_in"],
                     "answer_tokens_out": a["tokens_out"], "answer_llm_seconds": a["llm_seconds"],
                     "nav_calls_rec": [{"messages": c["messages"], "reply": c["reply"], "tokens_in": c["tokens_in"],
                                        "tokens_out": c["tokens_out"], "seconds": c["seconds"], "replayed": c["replayed"],
                                        "model": c["model"]} for c in nav.rec],
                     "answer_call": [{"messages": c["messages"], "reply": c["reply"], "tokens_in": c["tokens_in"],
                                      "tokens_out": c["tokens_out"], "seconds": c["seconds"], "replayed": c["replayed"],
                                      "model": c["model"]} for c in ans.rec]})
        print(q["id"], [(c["step"], c.get("what")) for c in r["chain"]])
    pages = {p.stem: p.read_text() for p in sorted((root / "pages").glob("*.md"))}
    return {"wiki_dir": "/vol/wiki_v5_DA (D then AMD-SUP-2026-02, built by v5_wiki_modal.py on 4 Nov 2026)",
            "tree": tree, "index_md": (root / "index.md").read_text(), "log_md": (root / "log.md").read_text(),
            "pages": pages, "links": {s: w.links_of(s) for s in w.pages}, "runs": runs}


@app.function(volumes={"/vol": vol}, secrets=[secret], timeout=3600, cpu=4, memory=8192)
def run(only: str = "") -> dict:
    out = {}
    if not only or "ingest" in only:
        out["ingest"] = ingest_A()
    if not only or "query" in only:
        out["query"] = query_small()
    out["_cassettes"] = {p.name: p.read_text() for p in pathlib.Path("/tmp/cass").glob("L3v5_wiki_simple_*.jsonl")}
    return out


@app.local_entrypoint()
def main(only: str = ""):
    res = run.remote(only)
    for name, txt in res.pop("_cassettes", {}).items():
        (CASS / name).write_text(txt)
        print("cassette", name)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for k, v in res.items():
        v = {"generated": stamp, "script": "experiments/v5_wiki_simple_modal.py", **v}
        (LOGS / f"v5_wiki_simple_{k}.json").write_text(json.dumps(v, indent=1, ensure_ascii=False, default=str))
        print("wrote", LOGS / f"v5_wiki_simple_{k}.json")
