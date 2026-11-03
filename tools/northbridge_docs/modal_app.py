"""Generate the northbridge-docs dump on Modal (workspace rajatworkspace), then pull it down.

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run tools/northbridge_docs/modal_app.py            # build (LLM fill if needed)
    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run tools/northbridge_docs/modal_app.py --llm 0    # placeholders, no LLM calls
    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run tools/northbridge_docs/modal_app.py --verify 1 # render twice, compare hashes

The job is spawned and polled. It writes /vol/out/northbridge-docs.tar.gz and the LLM cache to the volume
northbridge-docs-build; the local entrypoint downloads both: the dump is unpacked into
/Users/raj/Claude_Brain/northbridge-docs and the cache into tools/northbridge_docs/cache/llm.json.gz.
The OpenRouter key is read from the course .env and passed as a Modal secret; it is never printed.
"""
import json
import os
import pathlib
import subprocess
import tarfile
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[1] if len(HERE.parents) > 1 else HERE
OUT = pathlib.Path(os.environ.get("NB_OUT", "/Users/raj/Claude_Brain/northbridge-docs"))


def _key():
    if not modal.is_local():
        return ""
    for line in open(COURSE / ".env"):
        if line.startswith("OPENROUTER_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("fonts-liberation", "tesseract-ocr")
    .pip_install("reportlab==4.2.5", "openpyxl==3.1.5", "python-docx==1.1.2", "pypdf==5.1.0", "pyyaml==6.0.2", "pillow==11.0.0",
                 "httpx==0.27.2", "tiktoken==0.8.0", "pytesseract==0.3.13")
    .env({"PYTHONPATH": "/gen:/course/ledgerline", "NB_LEDGER_DOCS": "/course/ledgerline/ledgerline/docs",
          "NB_SCREENS": "/course/ledgerline/ledgerline/erp/screens", "NB_CACHE": "/vol/cache/llm.json.gz"})
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: "__pycache__" in str(p) or "cassettes" in str(p) or str(p).endswith((".jsonl", ".mp4")))
    .add_local_dir(HERE, "/gen", ignore=lambda p: "__pycache__" in str(p))
)
app = modal.App("northbridge-docs", image=image)
vol = modal.Volume.from_name("northbridge-docs-build", create_if_missing=True)
secret = modal.Secret.from_dict({"OPENROUTER_API_KEY": _key()}) if modal.is_local() else modal.Secret.from_dict({})


def _fill(missing, workers=32):
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from ndocs.llm import LLM, MODEL, call_openrouter

    key = os.environ["OPENROUTER_API_KEY"]
    llm = LLM("use")
    usage = dict(calls=0, prompt_tokens=0, completion_tokens=0, cost=0.0, failed=0)
    done = 0
    with ThreadPoolExecutor(workers) as pool:
        futs = {pool.submit(call_openrouter, item, key): k for k, item in missing.items()}
        for fut in as_completed(futs):
            k = futs[fut]
            try:
                text, u = fut.result()
                llm.cache[k] = dict(text=text, model=MODEL, words=missing[k]["words"])
                usage["calls"] += 1
                usage["prompt_tokens"] += u.get("prompt_tokens", 0)
                usage["completion_tokens"] += u.get("completion_tokens", 0)
                usage["cost"] += float(u.get("cost", 0) or 0)
            except Exception as e:  # noqa: BLE001
                usage["failed"] += 1
                print("LLM failed:", str(e)[:120])
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(missing)} done, ${usage['cost']:.2f}")
                llm.used = set()
                llm.save()
    llm.used = set()
    llm.save()
    return usage


@app.function(timeout=6 * 3600, cpu=8, memory=16384, volumes={"/vol": vol}, secrets=[secret])
def build(use_llm: int = 1, verify: int = 0):
    import shutil

    os.makedirs("/vol/cache", exist_ok=True)
    os.makedirs("/vol/out", exist_ok=True)
    if not os.path.exists("/vol/cache/llm.json.gz") and os.path.exists("/gen/cache/llm.json.gz"):
        shutil.copyfile("/gen/cache/llm.json.gz", "/vol/cache/llm.json.gz")
    from ndocs import build as B

    t0 = time.time()
    c, missing = B.collect()
    print(f"collect: {len(c.outputs)} outputs, {len(missing)} prompts not cached ({time.time() - t0:.0f}s)")
    usage = {}
    if missing and use_llm:
        usage = _fill(missing)
        print("LLM usage", usage)
        log = "/vol/cache/usage.jsonl"
        with open(log, "a") as f:
            f.write(json.dumps(dict(ts=time.strftime("%Y-%m-%d %H:%M:%S"), **usage)) + "\n")
        vol.commit()
        c, missing = B.collect()
        print(f"after fill: {len(missing)} still missing")
    mode = "use" if not missing else "collect"
    c = B.make(mode)
    t1 = time.time()
    res = B.render(c, "/tmp/northbridge-docs")
    c.llm.save()  # keep only the prompts this build used
    print(f"render+check: {time.time() - t1:.0f}s")
    res["llm_missing"] = len(missing)
    res["usage_this_run"] = usage
    if verify:
        m1 = B.manifest("/tmp/northbridge-docs")
        c2 = B.make(mode)
        B.render(c2, "/tmp/northbridge-docs-2")
        m2 = B.manifest("/tmp/northbridge-docs-2")
        diff = sorted(k for k in set(m1) | set(m2) if m1.get(k) != m2.get(k))
        res["determinism"] = dict(files=len(m1), differing=len(diff), examples=diff[:10])
    with tarfile.open("/vol/out/northbridge-docs.tar.gz", "w:gz") as tf:
        tf.add("/tmp/northbridge-docs", arcname="northbridge-docs")
    with open("/vol/out/result.json", "w") as f:
        json.dump(res, f, indent=1, default=str)
    vol.commit()
    return res


@app.local_entrypoint()
def main(llm: int = 1, verify: int = 0):
    call = build.spawn(use_llm=llm, verify=verify)
    print("spawned", call.object_id)
    while True:
        try:
            res = call.get(timeout=30)
            break
        except TimeoutError:
            print(".", end="", flush=True)
    print()
    env = dict(os.environ, MODAL_PROFILE=os.environ.get("MODAL_PROFILE", "rajatworkspace"))
    tmp = HERE / "cache" / "_dl"
    tmp.mkdir(parents=True, exist_ok=True)
    for remote, local in [("out/northbridge-docs.tar.gz", tmp / "northbridge-docs.tar.gz"), ("cache/llm.json.gz", HERE / "cache" / "llm.json.gz"),
                          ("cache/usage.jsonl", HERE / "cache" / "usage.jsonl")]:
        subprocess.run(["/Users/raj/.venv/bin/modal", "volume", "get", "--force", "northbridge-docs-build", remote, str(local)], env=env, check=False,
                       stdout=subprocess.DEVNULL)
    tgz = tmp / "northbridge-docs.tar.gz"
    if tgz.exists():
        keep_git = OUT / ".git"
        if OUT.exists():
            for p in OUT.iterdir():
                if p.name == ".git":
                    continue
                if p.is_dir():
                    subprocess.run(["rm", "-rf", str(p)])
                else:
                    p.unlink()
        OUT.mkdir(parents=True, exist_ok=True)
        with tarfile.open(tgz) as tf:
            for m in tf.getmembers():
                m.name = m.name.split("/", 1)[1] if "/" in m.name else ""
                if m.name:
                    tf.extract(m, OUT, filter="data")
        tgz.unlink()
        _ = keep_git
    summ = {k: v for k, v in res.items() if k not in ("check",)}
    summ["check"] = {k: v for k, v in res["check"].items() if k != "failures"}
    summ["check_failures"] = res["check"]["failures"][:60]
    print(json.dumps(summ, indent=1, default=str))
