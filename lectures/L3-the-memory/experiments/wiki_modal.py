"""Lecture 3, the LLM Wiki half: every heavy run on Modal (workspace rajatworkspace).

    cd lectures/L3-the-memory/experiments
    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run wiki_modal.py --cmd build [--files a,b] [--tag test]
    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run wiki_modal.py --cmd pull        # wiki + cassettes down
    (other cmds: lint, update, chains, eval, hybrid; see each function)

Volume `northbridge-wiki` holds /vol/wiki_v4 (the wiki), /vol/cassettes (every recorded LLM call) and /vol/logs.
Long jobs are .spawn()ed and polled. The OpenRouter key is read from the course .env into a Modal secret; never
printed.
"""
import json
import os
import pathlib
import subprocess
import sys
import tarfile
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")
LOGS = HERE / "logs"


def _key():
    if not modal.is_local():
        return ""
    for line in open(COURSE / ".env"):
        if line.startswith("OPENROUTER_API_KEY"):
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
          "LEDGER_CASSETTES": "/vol/cassettes", "LEDGER_LLM_MODE": "auto", "NB_L3_CACHE": "/vol/l3cache",
          "HF_HOME": "/vol/hf"})
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: "__pycache__" in str(p) or "cassettes" in str(p) or str(p).endswith((".mp4",))
                   or "/wiki_v4/pages" in str(p) or "/wiki_v4/restricted" in str(p))
    .add_local_dir(DUMP, "/dump", ignore=lambda p: "/.git" in str(p))
    .add_local_dir(HERE, "/exp", ignore=lambda p: "__pycache__" in str(p) or "/logs" in str(p))
)
app = modal.App("northbridge-wiki", image=image)
vol = modal.Volume.from_name("northbridge-wiki", create_if_missing=True)
secret = modal.Secret.from_dict({"OPENROUTER_API_KEY": _key()}) if modal.is_local() else modal.Secret.from_dict({})


def _log(*a):
    print(*a, flush=True)


@app.function(volumes={"/vol": vol}, secrets=[secret], timeout=6 * 3600, cpu=4, memory=8192)
def build(files: str = "", tag: str = "", workers: int = 32):
    from ledgerline.course.l3 import wiki_build as WB
    from ledgerline.course.l3.wiki_llm import WikiLLM

    out = pathlib.Path(f"/vol/wiki_v4{('_' + tag) if tag else ''}")
    if out.exists():
        subprocess.run(["rm", "-rf", str(out)])
    out.mkdir(parents=True)
    llm = WikiLLM(f"L3_wiki_ingest{('_' + tag) if tag else ''}", max_tokens=16000)
    rep = WB.build("/dump", out, llm, workers=workers, files=[f for f in files.split(",") if f] or None, log=_log)
    subprocess.run(["cp", "/course/ledgerline/ledgerline/wiki_v4/AGENTS.md", str(out / "AGENTS.md")])
    pathlib.Path("/vol/logs").mkdir(exist_ok=True)
    (pathlib.Path("/vol/logs") / f"wiki_build{('_' + tag) if tag else ''}.json").write_text(json.dumps(rep, indent=1))
    vol.commit()
    return rep


def _wiki_copy(src: str, dst: str):
    subprocess.run(["rm", "-rf", dst])
    subprocess.run(["cp", "-r", src, dst], check=True)
    return pathlib.Path(dst)


@app.function(volumes={"/vol": vol}, secrets=[secret], timeout=3 * 3600, cpu=4, memory=8192)
def lint_run(wiki: str = "/vol/wiki_v4"):
    from ledgerline.course.l3 import wiki_lint as WL
    from ledgerline.course.l3.wiki_llm import WikiLLM

    vol.reload()
    llm = WikiLLM("L3_wiki_lint", max_tokens=8000)
    rep = WL.lint(wiki, "/dump", llm)
    rep["messiness"] = WL.score_against_messiness(rep, "/dump")
    rep["llm"] = llm.stats()
    pathlib.Path("/vol/logs").mkdir(exist_ok=True)
    pathlib.Path("/vol/logs/wiki_lint.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    vol.commit()
    return rep


def _methods(kind: str, wiki_dir: str, suffix: str = ""):
    from ledgerline.course.l3 import wiki_query as WQ
    from ledgerline.course.l3.wiki_llm import WikiLLM

    w = WQ.Wiki(wiki_dir, dump="/dump")
    w.units()  # parse the dump once (cached on the volume) before any timing
    nav_llm = WikiLLM("L3v4_wiki_nav" + suffix, max_tokens=4000)
    if kind == "wiki":
        m = WQ.Navigator(w, nav_llm)
    else:
        si = WQ.SectionIndex(w, qcache=f"queries_bge-small{suffix}.jsonl")
        m = WQ.Hybrid(w, nav_llm, si, navigate=(kind == "hybrid"))
    return w, m


def _merge_cassettes(kind: str, nshards: int):
    """Shard cassettes -> one cassette per role (keys are request hashes, so merging is a union)."""
    for base in ("L3v4_wiki_nav", "L3v4_wiki_answers", "L3v4_wiki_judge"):
        target = pathlib.Path(f"/vol/cassettes/{base}.jsonl")
        have = set()
        if target.exists():
            have = {json.loads(l)["key"] for l in target.open() if l.strip()}
        with target.open("a") as out:
            for i in range(nshards):
                p = pathlib.Path(f"/vol/cassettes/{base}__{kind}_s{i}.jsonl")
                if p.exists():
                    for l in p.open():
                        if l.strip() and json.loads(l)["key"] not in have:
                            have.add(json.loads(l)["key"])
                            out.write(l if l.endswith("\n") else l + "\n")


@app.function(volumes={"/vol": vol}, secrets=[secret], timeout=4 * 3600, cpu=4, memory=12288)
def eval_shard(kind: str, shard: int, nshards: int, ids: str = "", wiki_dir: str = "/vol/wiki_v4_eval"):
    """One shard of the golden set, questions run one after another (the harness's timing rule)."""
    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3.wiki_llm import WikiLLM

    vol.reload()
    G = E.Golden("/dump")
    qs = [q for q in G.qs if (not ids or q["id"] in ids.split(","))]
    qs = qs[shard::nshards]
    sfx = f"__{kind}_s{shard}"   # one cassette file per container (a volume file must have one writer); merged after
    w, m = _methods(kind, wiki_dir, sfx)
    chains = {}

    def method(question, role):
        out = m.method(question, role)
        chains[question] = {k: out.get(k) for k in ("chain", "calls", "nav_calls", "tokens_in", "tokens_out",
                                                    "llm_seconds", "seconds", "cost_usd", "opened", "sources",
                                                    "search_ms")}
        return out

    ans = WikiLLM("L3v4_wiki_answers" + sfx, max_tokens=2048)
    jud = WikiLLM("L3v4_wiki_judge" + sfx, max_tokens=512)
    rep = E.run(method, name=kind, G=G, qs=qs, answer_llm=ans, judge_llm=jud, workers=8)
    for r in rep["records"]:
        q = G.by_id[r["id"]]
        r["chain"] = chains.get(q["question"])
    vol.commit()
    return rep["records"]


@app.function(volumes={"/vol": vol}, secrets=[secret], timeout=6 * 3600, cpu=2, memory=4096)
def eval_run(kind: str = "wiki", nshards: int = 6, ids: str = "", wiki_src: str = "/vol/wiki_v4"):
    from ledgerline.course.l3 import evaluate as E

    vol.reload()
    wiki_dir = f"/vol/wiki_v4_eval_{kind}"
    _wiki_copy(wiki_src, wiki_dir)  # the eval reads a frozen copy (file-back and lint never touch it)
    vol.commit()
    from ledgerline.course.l3 import corpus as C

    C.parse("/dump", parser="structured")  # the raw-source units navigation opens: parsed once, cached on the volume
    if kind != "wiki":  # build the section embeddings once before the shards start
        from ledgerline.course.l3 import wiki_query as WQ

        WQ.SectionIndex(WQ.Wiki(wiki_dir, dump="/dump"))
    vol.commit()
    t0 = time.time()
    recs = []
    for part in eval_shard.starmap([(kind, i, nshards, ids, wiki_dir) for i in range(nshards)]):
        recs += part
    rep = {"name": kind, "records": recs, "summary": E.summarize(recs), "shards": nshards,
           "wall_seconds": round(time.time() - t0, 1)}
    pathlib.Path("/vol/logs").mkdir(exist_ok=True)
    pathlib.Path(f"/vol/logs/wiki_eval_{kind}{('_' + str(len(ids.split(','))) ) if ids else ''}.json").write_text(
        json.dumps(rep, indent=1, ensure_ascii=False))
    vol.commit()
    return rep


@app.function(volumes={"/vol": vol}, secrets=[secret], timeout=2 * 3600, cpu=4, memory=8192)
def update_run():
    """The update cost: one new source (RN-7.2.3-P6) absorbed into a copy of the wiki; time, $, pages touched; then
    Q-0412 asked before and after on the same navigator."""
    from ledgerline.course.l3 import wiki_build as WB
    from ledgerline.course.l3 import wiki_query as WQ
    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3.wiki_llm import WikiLLM

    vol.reload()
    new = "08_release_notes/RN-7.2.3-P6 Ledgerline Patch Notes.pdf"
    dump = pathlib.Path("/tmp/dump_upd")
    subprocess.run(["rm", "-rf", str(dump)])
    subprocess.run(["cp", "-r", "/dump", str(dump)], check=True)
    sys.path.insert(0, "/exp/wiki_update_source")
    import make_rn_p6

    make_rn_p6.main(str(dump / new))
    wiki = _wiki_copy("/vol/wiki_v4", "/vol/wiki_v4_update")
    llm = WikiLLM("L3_wiki_update", max_tokens=16000)
    rep = WB.update([new], str(dump), wiki, llm)
    # before / after on the same question
    G = E.Golden("/dump")
    q = G.by_id["Q-0412"]
    ans = WikiLLM("L3v4_wiki_answers__update", max_tokens=2048)
    nav_llm = WikiLLM("L3v4_wiki_nav__update", max_tokens=4000)
    ba = {}
    for label, wd, dd in (("before", "/vol/wiki_v4", "/dump"), ("after", str(wiki), str(dump))):
        w = WQ.Wiki(wd, dump=dd)
        out = WQ.Navigator(w, nav_llm).navigate(q["question"], "PUR-EXEC")
        a = E.answer(q, out["items"], ans)
        ba[label] = {"answer": a["answer"], "opened": out["opened"], "chain": out["chain"]}
    rep["q0412_before_after"] = ba
    rep["source_text"] = make_rn_p6.TEXT
    pathlib.Path("/vol/logs/wiki_update.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    vol.commit()
    return rep


@app.function(volumes={"/vol": vol}, secrets=[secret], timeout=2 * 3600, cpu=4, memory=12288)
def chains_run(ids: str = "Q-EMMA,Q-0412", fileback: str = "Q-EMMA"):
    """Full navigation chains for the lecture's two examples (on the frozen eval copy), then the file-back demo on a
    separate copy: answer Q-EMMA, file it back as a qa- page, ask it again (and a paraphrase) and count the steps."""
    from ledgerline.course.l3 import wiki_query as WQ
    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3.wiki_llm import WikiLLM

    vol.reload()
    G = E.Golden("/dump")
    ans = WikiLLM("L3v4_wiki_answers__chains", max_tokens=2048)
    nav_llm = WikiLLM("L3v4_wiki_nav__chains", max_tokens=4000)
    w = WQ.Wiki("/vol/wiki_v4", dump="/dump")
    w.units()
    si = WQ.SectionIndex(w, qcache="queries_bge-small__chains.jsonl")
    out = {"chains": {}, "fileback": {}}
    for qid in ids.split(","):
        q = G.by_id[qid]
        for kind in ("wiki", "hybrid"):
            m = WQ.Navigator(w, nav_llm) if kind == "wiki" else WQ.Hybrid(w, nav_llm, si)
            r = m.method(q["question"], E.C.role_of(q))
            a = E.answer(q, r["items"], ans)
            out["chains"].setdefault(qid, {})[kind] = {
                "question": q["question"], "chain": r["chain"], "calls": r.get("calls"), "nav_calls": r.get("nav_calls"),
                "seconds": r["seconds"], "answer_seconds": a["llm_seconds"], "tokens_in": r.get("tokens_in"),
                "tokens_out": r.get("tokens_out"), "answer": a["answer"], "cited": a["cited"],
                "items": [{"id": i["id"], "cite": i.get("cite"), "sources": i.get("sources"), "loc": i.get("loc"),
                           "text": None if str(i["id"]).startswith("wiki:") else (i.get("text") or "")[:3000]}
                          for i in r["items"]],
                "answer_tokens_in": a["tokens_in"], "answer_tokens_out": a["tokens_out"],
                "fact": E.fact_check(q, a["answer"], G), "search_ms": r.get("search_ms")}
    # file-back on a copy
    wd = _wiki_copy("/vol/wiki_v4", "/vol/wiki_v4_fileback")
    w2 = WQ.Wiki(wd, dump="/dump")
    q = G.by_id[fileback]
    r = WQ.Navigator(w2, nav_llm).navigate(q["question"], "PUR-EXEC")
    a = E.answer(q, r["items"], ans)
    fb = WQ.file_back(w2, q["question"], a["answer"], r["items"], a["cited"])
    w3 = WQ.Wiki(wd, dump="/dump")
    again = {}
    for label, text in (("same", q["question"]), ("paraphrase", "Brightcell Energy offers battery packs at £104. "
                                                                  "Are we allowed to order from them?")):
        r2 = WQ.Navigator(w3, nav_llm).navigate(text, "PUR-EXEC")
        a2 = E.answer({**q, "question": text}, r2["items"], ans)
        again[label] = {"question": text, "chain": r2["chain"], "nav_calls": r2["nav_calls"], "seconds": r2["seconds"],
                        "tokens_in": r2["tokens_in"], "answer": a2["answer"], "opened": r2["opened"],
                        "fact": E.fact_check(q, a2["answer"], G)}
    out["fileback"] = {"before": {"nav_calls": r["nav_calls"], "seconds": r["seconds"], "tokens_in": r["tokens_in"],
                                  "opened": r["opened"], "chain": r["chain"], "answer": a["answer"]},
                       "filed": fb, "page": (pathlib.Path(wd) / "pages" / f"{fb['slug']}.md").read_text(),
                       "again": again,
                       "log_tail": (pathlib.Path(wd) / "log.md").read_text().splitlines()[-3:]}
    pathlib.Path("/vol/logs/wiki_query_chains.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    vol.commit()
    return out


@app.function(volumes={"/vol": vol}, timeout=1200)
def merge_all():
    """Run alone, after every job: fold every suffixed cassette (base__suffix.jsonl) into its base cassette."""
    vol.reload()
    groups = {}
    for p in pathlib.Path("/vol/cassettes").glob("*__*.jsonl"):
        groups.setdefault(p.name.split("__")[0], []).append(p)
    out = {}
    for base, parts in groups.items():
        target = pathlib.Path(f"/vol/cassettes/{base}.jsonl")
        have = {json.loads(l)["key"] for l in target.open() if l.strip()} if target.exists() else set()
        n = 0
        with target.open("a") as fh:
            for p in sorted(parts):
                for l in p.open():
                    if l.strip():
                        k = json.loads(l)["key"]
                        if k not in have:
                            have.add(k)
                            fh.write(l if l.endswith("\n") else l + "\n")
                            n += 1
        out[base] = {"added": n, "total": len(have)}
    vol.commit()
    return out


@app.function(volumes={"/vol": vol}, timeout=600)
def pack(paths: list[str]):
    import io

    vol.reload()
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for p in paths:
            if os.path.exists(p):
                tf.add(p, arcname=p.replace("/vol/", ""))
    return buf.getvalue()


def _run(fn, **kw):
    call = fn.spawn(**kw)
    _log(f"spawned {fn.tag if hasattr(fn, 'tag') else fn} -> {call.object_id}")
    while True:
        try:
            return call.get(timeout=60)
        except TimeoutError:
            _log(time.strftime("%H:%M:%S"), "still running")


@app.local_entrypoint()
def main(cmd: str = "build", files: str = "", tag: str = "", workers: int = 32, dest: str = ""):
    LOGS.mkdir(exist_ok=True)
    if cmd == "build":
        rep = _run(build, files=files, tag=tag, workers=workers)
        name = f"wiki_build{('_' + tag) if tag else ''}.json"
        (LOGS / name).write_text(json.dumps(rep, indent=1))
        _log(json.dumps({k: v for k, v in rep.items() if k not in ("merge_map", "orphans")}, indent=1)[:4000])
    elif cmd == "merge":
        _log(json.dumps(merge_all.remote(), indent=1))
    elif cmd in ("lint", "update", "chains"):
        fn = {"lint": lint_run, "update": update_run, "chains": chains_run}[cmd]
        rep = _run(fn)
        (LOGS / f"wiki_{'query_chains' if cmd == 'chains' else cmd}.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))
        _log(json.dumps(rep, ensure_ascii=False)[:3000])
    elif cmd == "eval":
        kind = tag or "wiki"
        rep = _run(eval_run, kind=kind, ids=files)
        (LOGS / f"wiki_eval_{kind}{('_' + str(len(files.split(',')))) if files else ''}.json").write_text(
            json.dumps(rep, indent=1, ensure_ascii=False))
        _log(json.dumps(rep["summary"]["overall"], indent=1))
    elif cmd == "pull":
        paths = [p for p in (files.split(",") if files else [f"/vol/wiki_v4{('_' + tag) if tag else ''}"])]
        data = pack.remote(paths)
        d = pathlib.Path(dest or "/tmp/nbwiki")
        d.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=__import__("io").BytesIO(data), mode="r:gz") as tf:
            tf.extractall(d, filter="data")
        _log(f"pulled {len(data)} bytes to {d}")
