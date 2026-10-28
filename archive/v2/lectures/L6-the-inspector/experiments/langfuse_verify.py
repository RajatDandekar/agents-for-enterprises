"""Read back from Langfuse what langfuse_export.py sent (v2 API only, nothing is written). Updates logs/langfuse.json.

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/langfuse_verify.py --mode replay
"""
import datetime as dt
import json
import pathlib

from bahi.evals.trace import _iso, verify_langfuse

LOGS = pathlib.Path(__file__).parent / "logs"
d = json.loads((LOGS / "langfuse.json").read_text())
t0 = dt.datetime.fromisoformat(d["export"]["t0"].replace("Z", "+00:00")).timestamp()
ver = verify_langfuse(d["tag"], expect=d["export"]["exported"], sample_trace=d["export"]["trace_ids"]["S2"],
                      t0=_iso(t0 - 60), t1=_iso(t0 + 2 * d["export"]["exported"] + 900), wait=60)
print(json.dumps({k: v for k, v in ver.items() if k != "sample"}, default=str)[:3000])
print("sample:", ver.get("sample", {}).get("status"), len(ver.get("sample", {}).get("observations", [])))
d["verify"] = ver
(LOGS / "langfuse.json").write_text(json.dumps(d, indent=1, ensure_ascii=False, default=str))
