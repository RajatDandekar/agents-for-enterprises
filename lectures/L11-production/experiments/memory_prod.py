"""Lecture 11 experiment 4: memory and data in production.

    L11_IMAGE=data tools/mrun.sh lectures/L11-production/experiments/l11_modal.py --script lectures/L11-production/experiments/memory_prod.py

Part A, pgvector against Lecture 3's in-memory index. The SAME 384-number bge-small vectors (L3's caches), the
SAME 33 gold questions and grader (lectures/L3-the-memory/experiments/questions.py). Postgres 15 + pgvector built
from source (v0.8.1), psycopg 3.3.6, pgvector-python 0.5.1, all inside one Modal container (localhost).
  recall@1/3/5/10 for: L3 vector_rank (numpy), pgvector exact (no index), pgvector HNSW
  latency per query: in-memory vs a SQL round trip
  permissions as a WHERE clause: HR's confidential clauses returned to Kavita, with and without it
  scale: 2,00,000 random unit vectors added (latency only: random vectors are not realistic text)
  persistence: Postgres restarted, rows counted; L3 index rebuilt from its cache files, timed
Part B, Redis for session memory and shared rate limits (redis-server 7, redis-py 8.1.0).
Writes logs/memory_prod.json and bahi/course/production/fixtures/memory_runs.json.
"""
import json
import os
import pathlib
import statistics
import subprocess
import sys
import time

os.environ["BAHI_LLM_MODE"] = "replay"   # read L3's caches, never append to them (they belong to Lecture 3)
HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"; LOGS.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE.parents[1] / "L3-the-memory" / "experiments"))
import numpy as np
from questions import Q
from bahi.agent import retrieval as R
from bahi.course import l3
import bahi.course.production as P

FIX = pathlib.Path(P.__file__).parent / "fixtures"
out = {"date": "2026-10-28"}


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


def pct(xs, p):
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(p * (len(xs) - 1)))], 3)


# ------------------------------------------------------------------ start Postgres
ver = sh("ls /usr/lib/postgresql").split()[-1]
print(sh(f"pg_ctlcluster {ver} main start"))
print(sh("su postgres -c \"psql -c \\\"ALTER USER postgres PASSWORD 'drill'\\\"\""))
import psycopg
from pgvector.psycopg import register_vector

DSN = "host=localhost user=postgres password=drill dbname=postgres sslmode=disable"
conn = psycopg.connect(DSN, autocommit=True)
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)
out["postgres"] = conn.execute("SELECT version()").fetchone()[0][:60]
out["pgvector_ext"] = conn.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()[0]
print(out["postgres"], "pgvector", out["pgvector_ext"])

# ------------------------------------------------------------------ the L3 index (Kavita's) and every chunk (for permissions)
t0 = time.perf_counter()
ret = l3.retriever("KJOSHI")
out["l3_build_seconds"] = round(time.perf_counter() - t0, 3)
allret = l3.retriever("KJOSHI", permissions=False)
K = R.clearance_for("KJOSHI")
out["chunks_kavita"], out["chunks_all"] = len(ret.chunks), len(allret.chunks)

conn.execute("DROP TABLE IF EXISTS clause")
conn.execute("""CREATE TABLE clause(id text PRIMARY KEY, doc_id text, audience text, effective date,
               body text, embedding vector(384))""")
t0 = time.perf_counter()
with conn.cursor() as cur:
    cur.executemany("INSERT INTO clause VALUES (%s,%s,%s,%s,%s,%s)",
                    [(c.id, c.doc_id, R.audience_tag(c.audience), c.effective, c.context_text, np.array(v, dtype=np.float32))
                     for c, v in zip(allret.chunks, allret.vecs)])
out["insert_seconds"] = round(time.perf_counter() - t0, 3)
out["clearance_kavita"] = sorted(K)

GQ = [q for q in Q if q.get("gold")]
qvec = {q["id"]: np.array(ret.embedder.embed([q["q"]], kind="query")[0], dtype=np.float32) for q in GQ}
gold = {q["id"]: set(q["gold"]) for q in GQ}


def rank_of(ids, g):
    for i, x in enumerate(ids, 1):
        if x in g:
            return i
    return None


def l3_ids(q, k=10):
    return [ret.chunks[i].id for i, _ in ret.vector_rank(q["q"])[:k]]


def pg_ids(q, k=10, where=True):
    sql = ("SELECT id FROM clause " + ("WHERE audience = ANY(%s) " if where else "") +
           "ORDER BY embedding <=> %s LIMIT %s")
    args = ([sorted(K)] if where else []) + [qvec[q["id"]], k]
    return [r[0] for r in conn.execute(sql, args).fetchall()]


def evaluate(fn, name, reps=5):
    rows, lat = [], []
    for q in GQ:
        ids = fn(q)
        for _ in range(reps):
            t = time.perf_counter(); fn(q); lat.append((time.perf_counter() - t) * 1000)
        rows.append({"id": q["id"], "top5": ids[:5], "gold_rank": rank_of(ids, gold[q["id"]])})
    s = {f"recall@{k}": round(sum(1 for r in rows if r["gold_rank"] and r["gold_rank"] <= k) / len(rows), 3) for k in (1, 3, 5, 10)}
    s.update({"n": len(rows), "ms_p50": pct(lat, .5), "ms_p95": pct(lat, .95)})
    print(f"{name:22} {s}", flush=True)
    return s, rows


res = {}
res["l3_in_memory"], r_l3 = evaluate(l3_ids, "L3 in memory")
conn.execute("SET enable_indexscan = off")
res["pg_exact"], r_ex = evaluate(pg_ids, "pgvector exact")
conn.execute("SET enable_indexscan = on")
t0 = time.perf_counter()
conn.execute("CREATE INDEX clause_hnsw ON clause USING hnsw (embedding vector_cosine_ops)")
out["hnsw_build_seconds_251"] = round(time.perf_counter() - t0, 3)
res["pg_hnsw"], r_hn = evaluate(pg_ids, "pgvector hnsw")
plan = conn.execute("EXPLAIN SELECT id FROM clause WHERE audience = ANY(%s) ORDER BY embedding <=> %s LIMIT 10",
                    [sorted(K), qvec[GQ[0]["id"]]]).fetchall()
out["plan_small"] = [p[0] for p in plan]
same5 = sum(1 for a, b in zip(r_l3, r_ex) if a["top5"] == b["top5"])
out["agree_top5_l3_vs_pg_exact"] = f"{same5}/{len(r_l3)}"
out["retrieval"] = res
out["per_question"] = [{"id": a["id"], "q": next(q["q"] for q in GQ if q["id"] == a["id"]), "gold": sorted(gold[a["id"]]),
                        "l3": a["top5"], "pg": b["top5"], "l3_rank": a["gold_rank"], "pg_rank": b["gold_rank"]}
                       for a, b in zip(r_l3, r_hn)]

# permissions in SQL
hr = [c.id for c in allret.chunks if not R.allowed(c, K)]
leak_without = leak_with = 0
for q in [x for x in Q if x.get("kind") == "perm"] or GQ[:2]:
    v = np.array(ret.embedder.embed([q["q"]], kind="query")[0], dtype=np.float32)
    a = [r[0] for r in conn.execute("SELECT id FROM clause ORDER BY embedding <=> %s LIMIT 5", [v]).fetchall()]
    b = [r[0] for r in conn.execute("SELECT id FROM clause WHERE audience = ANY(%s) ORDER BY embedding <=> %s LIMIT 5",
                                    [sorted(K), v]).fetchall()]
    leak_without += sum(1 for x in a if x in hr); leak_with += sum(1 for x in b if x in hr)
out["permissions"] = {"restricted_chunks": len(hr), "perm_questions": len([x for x in Q if x.get("kind") == "perm"]),
                      "leaked_without_where": leak_without, "leaked_with_where": leak_with}
print("permissions", out["permissions"], flush=True)

# ------------------------------------------------------------------ scale: 2,00,000 random distractors (latency only)
N = 200_000
import datetime as _dt
D2026 = _dt.date(2026, 1, 1)
rng = np.random.default_rng(11)
t0 = time.perf_counter()
with conn.cursor() as cur:
    with cur.copy("COPY clause (id, doc_id, audience, effective, body, embedding) FROM STDIN WITH (FORMAT BINARY)") as cp:
        cp.set_types(["text", "text", "text", "date", "text", "vector"])
        for i in range(N):
            v = rng.standard_normal(384).astype(np.float32); v /= np.linalg.norm(v)
            cp.write_row([f"SYN-{i:06d}", "SYNTHETIC", "all-staff", D2026, "", v])
out["scale_insert_seconds"] = round(time.perf_counter() - t0, 2)
conn.execute("DROP INDEX clause_hnsw")
conn.execute("SET max_parallel_workers_per_gather = 0")
conn.execute("SET enable_indexscan = off")
s_ex, r_ex2 = evaluate(lambda q: pg_ids(q, 10, where=False), "pg exact, 2 lakh", reps=3)
conn.execute("SET enable_indexscan = on")
conn.execute("SET maintenance_work_mem = '1GB'")
t0 = time.perf_counter()
conn.execute("CREATE INDEX clause_hnsw ON clause USING hnsw (embedding vector_cosine_ops)")
out["hnsw_build_seconds_scaled"] = round(time.perf_counter() - t0, 2)
s_hn, r_hn2 = evaluate(lambda q: pg_ids(q, 10, where=False), "pg hnsw, 2 lakh", reps=5)
big = np.vstack([np.array(allret.vecs, dtype=np.float32), rng.standard_normal((N, 384)).astype(np.float32)])
big /= np.linalg.norm(big, axis=1, keepdims=True)
lat = []
for q in GQ:
    for _ in range(3):
        t = time.perf_counter(); s = big @ qvec[q["id"]]; np.argpartition(-s, 10)[:10]; lat.append((time.perf_counter() - t) * 1000)
out["scale"] = {"rows": N + len(allret.chunks), "pg_exact": s_ex, "pg_hnsw": s_hn,
                "numpy_bruteforce_ms_p50": pct(lat, .5), "numpy_bruteforce_ms_p95": pct(lat, .95),
                "hnsw_top5_equals_exact_top5": f"{sum(1 for a, b in zip(r_ex2, r_hn2) if a['top5'] == b['top5'])}/{len(GQ)}",
                "table_size": conn.execute("SELECT pg_size_pretty(pg_total_relation_size('clause'))").fetchone()[0],
                "note": "distractors are random unit vectors: a latency test, not a recall test"}
print("scale", json.dumps(out["scale"])[:400], flush=True)

# ------------------------------------------------------------------ persistence
conn.close()
t0 = time.perf_counter()
print(sh(f"pg_ctlcluster {ver} main restart"))
for _ in range(50):
    try:
        conn = psycopg.connect(DSN, autocommit=True); break
    except Exception:  # noqa: BLE001
        time.sleep(0.2)
out["persistence"] = {"postgres_restart_seconds": round(time.perf_counter() - t0, 2),
                      "rows_after_restart": conn.execute("SELECT count(*) FROM clause").fetchone()[0],
                      "l3_rebuild_seconds": out["l3_build_seconds"]}
print("persistence", out["persistence"], flush=True)

# ====================================================================== Part B: Redis
print(sh("mkdir -p /tmp/redis && redis-server --port 6379 --daemonize yes --appendonly yes --dir /tmp/redis"))
time.sleep(1)
import redis
rd = redis.Redis(port=6379, decode_responses=True)
out["redis_version"] = rd.info()["redis_version"]
inj = json.load(open(FIX / "injection_runs.json"))
turns = next(r["turns"] for r in inj["rows"] if r["cond"] == "poisoned+trust" and len(r["turns"]) >= 1)
conv = [{"role": "system", "content": "You are Ask Rasoi ..."}]
for t in turns:
    conv += [{"role": "user", "content": t["user"]}, {"role": "assistant", "content": t.get("agent", "")}]
KEY = "session:KJOSHI:conv-0417"
TTL = 7 * 24 * 3600
setl, getl = [], []
for i in range(1000):
    t = time.perf_counter(); rd.set(KEY, json.dumps(conv), ex=TTL); setl.append((time.perf_counter() - t) * 1000)
    t = time.perf_counter(); json.loads(rd.get(KEY)); getl.append((time.perf_counter() - t) * 1000)
out["redis_session"] = {"key": KEY, "bytes": len(json.dumps(conv).encode()), "messages": len(conv),
                        "ttl_seconds": rd.ttl(KEY), "set_ms_p50": pct(setl, .5), "set_ms_p95": pct(setl, .95),
                        "get_ms_p50": pct(getl, .5), "get_ms_p95": pct(getl, .95)}

# a replica dies: an in-process dict loses the conversation, Redis keeps it
REPLICA = r'''
import json, sys, redis
mem = {}
rd = redis.Redis(port=6379, decode_responses=True)
if sys.argv[1] == "write":
    conv = json.loads(rd.get("session:KJOSHI:conv-0417"))
    conv.append({"role": "user", "content": "Has Rohit approved it yet?"})
    mem["session:KJOSHI:conv-0417"] = conv
    rd.set("session:KJOSHI:conv-0417", json.dumps(conv), ex=604800)
    print(json.dumps({"replica": "1", "messages_in_memory": len(mem["session:KJOSHI:conv-0417"])}))
    import time; time.sleep(60)
else:
    conv = rd.get("session:KJOSHI:conv-0417")
    print(json.dumps({"replica": "2", "in_memory_dict": len(mem.get("session:KJOSHI:conv-0417", [])),
                      "redis_messages": len(json.loads(conv)) if conv else 0,
                      "last": json.loads(conv)[-1]["content"] if conv else None}))
'''
open("/tmp/replica.py", "w").write(REPLICA)
p1 = subprocess.Popen([sys.executable, "/tmp/replica.py", "write"], stdout=subprocess.PIPE, text=True)
line1 = p1.stdout.readline().strip()
p1.kill(); p1.wait()
line2 = subprocess.run([sys.executable, "/tmp/replica.py", "read"], capture_output=True, text=True).stdout.strip()
print(sh("redis-cli -p 6379 shutdown save"))
time.sleep(1)
print(sh("redis-server --port 6379 --daemonize yes --appendonly yes --dir /tmp/redis"))
time.sleep(1)
rd = redis.Redis(port=6379, decode_responses=True)
after = rd.get(KEY)
out["redis_failover"] = {"replica1": json.loads(line1), "replica1_killed": True, "replica2": json.loads(line2),
                         "after_redis_restart_messages": len(json.loads(after)) if after else 0}
print("redis failover", out["redis_failover"], flush=True)

# shared rate limit: the live app's Guard keeps its counters in process memory (deque per player).
# Three replicas behind a load balancer, 40 messages from Kavita in one minute, limit 10 per minute.
from collections import deque
LIMIT, MSGS = 10, 40
local = [deque() for _ in range(3)]
allowed_local = 0
for i in range(MSGS):
    q = local[i % 3]
    if len(q) < LIMIT:
        q.append(i); allowed_local += 1
allowed_redis = 0
rk = "rate:KJOSHI:minute"
rd.delete(rk)
for i in range(MSGS):
    n = rd.incr(rk)
    if n == 1:
        rd.expire(rk, 60)
    if n <= LIMIT:
        allowed_redis += 1
out["rate_limit"] = {"limit_per_minute": LIMIT, "messages": MSGS, "replicas": 3,
                     "allowed_in_process_counters": allowed_local, "allowed_redis_counter": allowed_redis}
print("rate limit", out["rate_limit"], flush=True)

(LOGS / "memory_prod.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
(FIX / "memory_runs.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print("wrote memory_prod.json")
