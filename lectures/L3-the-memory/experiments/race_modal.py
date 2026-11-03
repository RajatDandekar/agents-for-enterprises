"""Lecture 3 v4, the race: the best RAG against the LLM Wiki (navigation, hybrid, sections only), on one harness.

    cd /Users/raj/Claude_Brain/enterprise-agents-course
    MODAL_PROFILE=rajatworkspace tools/mrun.sh lectures/L3-the-memory/experiments/race_modal.py
    (--only rag,wiki to run some methods; --variants 250,250n to skip the 150-word replay)

What is the same for every method: the 224 documentation questions, the answer prompt (evaluate.ANSWER_SYSTEM),
the answer and judge model (gemini-3.8-flash through Google's endpoint, one client class: WikiLLM, which also counts
thinking tokens as output), the source cap (9,000 characters a source), the "withheld" notice (decided once, by one
detector, rag.Retriever.withheld), and the machine (one Modal L4 container per method, 4 vCPU, 16 GiB, retrieval run
one question at a time).

Three variants per method:
    150    the answers at the old 150-word cap, replayed from each method's recorded runs (same retrieval, same prompt)
    250    the race's cap: 250 words. Emma's question needs seven facts and their citations; 150 words cannot hold them
    250n   250 words + the withheld notice for questions a confidential HR document would have matched

Recorded calls replay (cassettes ledgerline/cassettes/L3v4_race_<method>_{answers,judge}.jsonl; navigation from the
wiki volume's L3v4_wiki_nav*), so only new answers and verdicts cost money. Navigation latency = local time + the
recorded API seconds of every replayed navigation call. Writes logs/race_answers/<method>__<variant>.json and the
inputs of logs/race.json (built by race_report.py).
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
LOGS = HERE / "logs"
CASS = COURSE / "ledgerline" / "ledgerline" / "cassettes"
GEMINI_ENV = "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env"
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app", "pages", "restricted"}
MACHINE = "Modal L4 GPU container, 4 vCPU, 16 GiB (gpu=L4, cpu=4, memory=16384)"


def _gkey():
    if not modal.is_local() or not os.path.exists(GEMINI_ENV):
        return ""
    for line in open(GEMINI_ENV):
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("tesseract-ocr", "git")
    .pip_install("pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl==3.1.5", "python-docx==1.1.2", "pyyaml==6.0.2",
                 "tiktoken==0.8.0", "pytesseract==0.3.13", "pillow==11.0.0", "numpy<2.1", "scipy", "openai>=1.50",
                 "httpx", "pydantic>=2", "pandas")
    .run_commands("python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
    .pip_install("torch==2.4.1", "transformers==4.46.3", "sentence-transformers==3.3.1", "einops", "chromadb==1.0.15",
                 "scikit-learn", "umap-learn==0.5.7")
    .env({"HF_HOME": "/hf"})
    .run_commands(
        "python -c \"from sentence_transformers import SentenceTransformer as S, CrossEncoder as C; "
        "[S(m, trust_remote_code=True) for m in ['BAAI/bge-small-en-v1.5']]; C('BAAI/bge-reranker-base')\"")
    .env({"PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NORTHBRIDGE_DOCS": "/dump", "NB_DOCS": "/dump",
          "NB_L3_CACHE": "/vol/l3cache", "LEDGER_CASSETTES": "/tmp/cassettes", "LEDGER_LLM_MODE": "auto",
          "LEDGER_WIKI_PROVIDER": "google-direct", "TOKENIZERS_PARALLELISM": "false"})
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
    .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts)
    .add_local_dir(CASS, "/cass_src", ignore=lambda p: not pathlib.Path(p).name.startswith(
        ("L3v4_answers", "L3v4_judge", "L3v4_race")))
)
app = modal.App("northbridge-l3-race", image=image)
wvol = modal.Volume.from_name("northbridge-wiki")       # the wiki, its frozen eval copies, navigation cassettes
rvol = modal.Volume.from_name("northbridge-raglab")     # the RAG indexes
secret = modal.Secret.from_dict({"GEMINI_API_KEY": _gkey()}) if modal.is_local() else modal.Secret.from_dict({})

WIKI_DIRS = {"wiki": "/vol/wiki_v4_eval_wiki", "hybrid": "/vol/wiki_v4_eval_hybrid",
             "sections": "/vol/wiki_v4_eval_hybrid-search"}
LABELS = {"rag": "RAG best (BM25 + reranker, structure-aware 200-token chunks, k=10)",
          "wiki": "LLM Wiki, navigation (the model reads index.md and opens pages)",
          "hybrid": "LLM Wiki, hybrid (search the wiki's sections, then navigate from them)",
          "sections": "LLM Wiki, sections only (search the wiki's sections, no navigation)"}


def _setup_cassettes():
    import shutil

    d = pathlib.Path("/tmp/cassettes")
    d.mkdir(parents=True, exist_ok=True)
    for p in list(pathlib.Path("/cass_src").glob("*.jsonl")) + list(pathlib.Path("/vol/cassettes").glob("L3v4_wiki_*.jsonl")):
        if not (d / p.name).exists():
            shutil.copy(p, d / p.name)
    return sorted(p.stem for p in d.glob("*.jsonl"))


def _rag_retriever():
    import pickle
    import shutil

    from ledgerline.course.l3 import rag as R

    best = json.loads(pathlib.Path("/rvol/rag_best.json").read_text())
    cfg = R.Config.from_id(best["config"]["id"])
    local = pathlib.Path("/tmp/idx") / cfg.chunking
    if not local.exists():
        shutil.copytree(f"/rvol/chroma/{cfg.chunking}", local)
    idx = R.Index.load(local)
    idx._bm25 = pickle.loads((local / "bm25.pkl").read_bytes())
    return R.Retriever(idx, cfg), cfg


@app.function(gpu="L4", cpu=4, memory=16384, volumes={"/vol": wvol, "/rvol": rvol}, timeout=1800)
def withheld_remote() -> dict:
    """The one detector every method's notice comes from: per question, does a confidential chunk sit in BM25's
    unfiltered top 10 for a role outside HR?"""
    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import corpus as C, evaluate as E

    ret, cfg = _rag_retriever()
    G = E.Golden("/dump")
    out, rows = {}, []
    for q in G.qs:
        st = ret.withheld(q["question"], C.role_of(q))
        if st:
            out[q["id"]] = st
        rows.append({"id": q["id"], "type": q["type"], "role": C.role_of(q), "fires": bool(st),
                     "bm25_rank": st["meta"]["bm25_rank"] if st else None})
    return {"items": out, "rows": rows, "detector": f"rag.Retriever.withheld, BM25 over {cfg.chunking}, k=10"}


@app.function(gpu="L4", cpu=4, memory=16384, volumes={"/vol": wvol, "/rvol": rvol}, secrets=[secret],
              timeout=5 * 3600, max_containers=4)
def race_one(method: str, variants: list[str], withheld: dict, ids: str = "") -> dict:
    sys.path.insert(0, "/course/ledgerline")
    names = _setup_cassettes()
    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3.wiki_llm import WikiLLM, live_stats
    from ledgerline.llm import LLM

    G = E.Golden("/dump")
    qs = [q for q in G.qs if not ids or q["id"] in ids.split(",")]
    nav = None
    if method == "rag":
        ret, cfg = _rag_retriever()
        ret.search(G.qs[1]["question"], k=cfg.k)  # warm-up: models on the GPU before any question is timed

        def base(question, role):
            return ret.search(question, role=role, k=cfg.k)
    else:
        from ledgerline.course.l3 import wiki_query as WQ

        w = WQ.Wiki(WIKI_DIRS[method], dump="/dump")
        w.units()
        nav = WikiLLM(f"L3v4_race_{method}_nav", max_tokens=4000,
                      read_also=[n for n in names if n.startswith("L3v4_wiki_nav")])
        if method == "wiki":
            m = WQ.Navigator(w, nav)
        else:
            si = WQ.SectionIndex(w, qcache="queries_bge-small__race.jsonl")
            si.qvec("warm-up: load the embedding model before any question is timed")
            m = WQ.Hybrid(w, nav, si, navigate=(method == "hybrid"))

        def base(question, role):
            n0 = len(nav.log)
            out = m.method(question, role)
            new = nav.log[n0:]
            # a replayed navigation call took no time here: add the API seconds it took when it was recorded
            out["seconds"] = round(out["seconds"] + sum(r.seconds for r in new if r.replayed), 4)
            out["nav_live_calls"] = sum(1 for r in new if not r.replayed)
            return out

    memo = {}

    def method_fn(question, role):  # retrieve once; every variant answers from the same items
        if (question, role) not in memo:
            memo[(question, role)] = base(question, role)
        return memo[(question, role)]

    reps, live = {}, {}
    for v in variants:
        if v == "150":  # the method's own recorded 150-word runs
            if method == "rag":
                a_llm = LLM(E.ANSWER_MODEL, cassette="L3v4_answers", max_tokens=2048)
                j_llm = LLM(E.JUDGE_MODEL, cassette="L3v4_judge", max_tokens=512)
            else:
                a_llm = WikiLLM(f"L3v4_race_{method}_150_answers", max_tokens=2048,
                                read_also=[n for n in names if n.startswith("L3v4_wiki_answers")])
                j_llm = WikiLLM(f"L3v4_race_{method}_150_judge", max_tokens=512,
                                read_also=[n for n in names if n.startswith("L3v4_wiki_judge")])
            words, wh = 150, None
        else:
            a_llm = WikiLLM(f"L3v4_race_{method}_answers", max_tokens=2048)
            j_llm = WikiLLM(f"L3v4_race_{method}_judge", max_tokens=512)
            words, wh = 250, (withheld if v == "250n" else None)
        t0 = time.time()
        rep = E.run(method_fn, name=f"{method}__{v}", G=G, qs=qs, answer_llm=a_llm, judge_llm=j_llm, workers=8,
                    answer_words=words, withheld=wh)
        for r in rep["records"]:
            o = memo.get((G.by_id[r["id"]]["question"], r["role"]), {})
            r["nav_calls"] = o.get("nav_calls")
            r["nav_live_calls"] = o.get("nav_live_calls")
            r["chain"] = o.get("chain")
        rep.update({"method": method, "variant": v, "label": LABELS[method], "machine": MACHINE,
                    "wall_seconds": round(time.time() - t0, 1),
                    "replayed": {"answer": sum(r.replayed for r in a_llm.log), "judge": sum(r.replayed for r in j_llm.log),
                                 "answer_calls": len(a_llm.log), "judge_calls": len(j_llm.log)}})
        lv = {}
        for role, l in (("answer", a_llm), ("judge", j_llm)):
            if isinstance(l, WikiLLM):
                lv[role] = live_stats(l)
            else:
                ti = sum(r.tokens_in for r in l.log if not r.replayed)
                to = sum(r.tokens_out for r in l.log if not r.replayed)
                lv[role] = {"base": {"calls": sum(1 for r in l.log if not r.replayed), "tokens_in": ti, "tokens_out": to,
                                     "usd": round(E.cost_usd(ti, to), 5)}}
        rep["live_calls"] = lv
        live[v] = lv
        reps[v] = rep
    if nav is not None:
        live["nav"] = live_stats(nav)
    cass = {p.name: p.read_text() for p in pathlib.Path("/tmp/cassettes").glob("L3v4_race_*.jsonl")}
    return {"method": method, "reps": reps, "live": live, "_cassettes": cass}


def _usd(x) -> float:
    """Sum the "usd" of live_stats-shaped dicts, however nested."""
    if isinstance(x, dict):
        return x["usd"] if "usd" in x and "calls" in x else sum(_usd(v) for v in x.values())
    return 0.0


def _merge(files: dict):
    for name, text in files.items():
        dst = CASS / name
        have = dst.read_text().splitlines() if dst.exists() else []
        seen = set(have)
        extra = [l for l in text.splitlines() if l and l not in seen]
        if extra:
            dst.write_text("\n".join(have + extra) + "\n")
            print(f"cassette {name}: +{len(extra)}")


@app.local_entrypoint()
def main(only: str = "rag,wiki,hybrid,sections", variants: str = "150,250,250n", ids: str = "", tag: str = ""):
    out_dir = LOGS / "race_answers"
    out_dir.mkdir(parents=True, exist_ok=True)
    wp = out_dir / "withheld.json"
    if wp.exists():
        wd = json.loads(wp.read_text())
    else:
        wd = withheld_remote.remote()
        wp.write_text(json.dumps(wd, indent=1))
    fires = [r for r in wd["rows"] if r["fires"]]
    print(f"withheld notice fires on {len(fires)} questions:", [(r["id"], r["type"]) for r in fires])
    methods = [m for m in only.split(",") if m]
    vs = [v for v in variants.split(",") if v]
    spend = {}
    for res in race_one.starmap([(m, vs, wd["items"], ids) for m in methods], return_exceptions=True):
        if not isinstance(res, dict):
            print("FAILED", str(res)[:600])
            continue
        _merge(res.pop("_cassettes", {}))
        m = res["method"]
        for v, rep in res["reps"].items():
            (out_dir / f"{m}__{v}{('_' + tag) if tag else ''}.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False, default=str))
            o = rep["summary"]["overall"]
            print(f"{m:9s} {v:5s} judge {o['answer_correct']} fact {o['fact_correct']} cite {o['citation_correct']} "
                  f"ret p95 {o['retrieval_s'].get('p95')} total p50/p95 {o['total_s'].get('p50')}/{o['total_s'].get('p95')} "
                  f"${o['cost_per_q_usd']}/q")
        spend[m] = res["live"]
        print(f"{m}: live spend this run ${_usd(res['live']):.3f}  (nav {_usd(res['live'].get('nav', {})):.3f})")
    sp = out_dir / "spend.json"
    prev = json.loads(sp.read_text()) if sp.exists() else []
    prev.append({"at": time.strftime("%Y-%m-%d %H:%M"), "methods": methods, "variants": vs, "ids": ids, "tag": tag,
                 "live": spend, "usd": round(_usd(spend), 4)})
    print(f"TOTAL live spend this run ${_usd(spend):.3f}; all race runs ${sum(p.get('usd', 0) for p in prev):.3f}")
    sp.write_text(json.dumps(prev, indent=1))
