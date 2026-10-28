"""Probe the deployed Rasoi Experience from a Modal container: no model is called, nothing is written.

    modal run tools/modal_run.py --script lectures/L7-trust/experiments/live_probe.py
Writes logs/live_probe.json: status and latency of /healthz (20 calls, after one warm-up) and of three pages.
"""
import json
import pathlib
import statistics
import time
import urllib.request

URL = "https://rajatworkspace--rasoi-experience.us-east.modal.run"
out = {"url": URL, "when": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}


def get(path):
    t0 = time.perf_counter()
    try:
        r = urllib.request.urlopen(URL + path, timeout=120)
        body = r.read()
        return r.status, round((time.perf_counter() - t0) * 1000, 1), len(body), body[:300].decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return getattr(e, "code", None), round((time.perf_counter() - t0) * 1000, 1), 0, str(e)[:200]


out["warmup"] = get("/healthz")
hz = [get("/healthz") for _ in range(20)]
ms = sorted(h[1] for h in hz)
out["healthz"] = {"n": len(hz), "ok": sum(h[0] == 200 for h in hz), "p50_ms": statistics.median(ms), "p95_ms": ms[int(0.95 * len(ms)) - 1],
                  "max_ms": ms[-1], "sample": hz[0][3]}
out["pages"] = {p: dict(zip(("status", "ms", "bytes"), get(p)[:3])) for p in ("/", "/after?stage=agent", "/tools")}
print(json.dumps(out, indent=1))
p = pathlib.Path(__file__).parent / "logs" / "live_probe.json"
p.write_text(json.dumps(out, indent=1))
