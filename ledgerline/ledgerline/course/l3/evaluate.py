"""Lecture 3 v4: one evaluation harness for every memory method (RAG configs, the LLM Wiki, hybrid, paste-all).

    from ledgerline.course.l3 import corpus as C, evaluate as E
    G = E.Golden()                                    # the 224 documentation questions + facts, from the dump's eval/
    def my_method(question: str, role: str) -> dict:  # a method retrieves for one question, as one user role
        items = [...]                                  # each item: {"id", "text", "file", "loc"} (+ "cite", "meta",
        return {"items": items}                        #   "sources": [{"file", "loc"}] for items made from several files)
    rep = E.run(my_method, name="rag-best", G=G)       # retrieval metrics, answers, fact check, judge, latency, cost
    E.retrieval_only(my_method, G=G)                   # just recall@k / MRR (no LLM)

What a method may return (all optional except items):
    items         ranked list, best first
    seconds       retrieval wall time; measured around the call if absent
    llm_seconds / tokens_in / tokens_out / cost_usd    LLM work done inside retrieval (query rewriting, wiki navigation)
    answer        a ready answer (skips the shared answer step; normally leave it out so every method uses ANSWER_MODEL)

The pieces, usable on their own:
    E.gold_hits(q, items)            per-question retrieval: rank of the first gold source, hit@k, coverage@k, fact_hit@k
    E.answer(q, items, llm)          the shared answer prompt (numbered sources, cite like [2], abstain/refuse rules)
    E.fact_check(q, text, G)         exact-fact check against facts.jsonl / must_contain / absent_terms / leaks
    E.judge(q, text, llm)            LLM judge against the reference answer (JSON verdict)
    E.citation_check(q, rec, items)  "citation correct": a cited item contains a gold fact or sits at a gold location
    E.summarize(records)             overall + by question type + not_in_docs + permission + judge/fact agreement
    E.pct(xs, 50|95)                 percentiles for latency

Matching granularity (retrieval): an item matches a gold source when the file is the same (or a byte-identical copy)
AND, when the gold source has a page, the item covers that page; when it has a sheet row (XLSX) or a row (CSV), the
item's row range covers it. Gold sources located only by section (DOCX, MD, EML, YAML) match at file level, and items
that carry no page/row location also fall back to file level (counted in match_levels). Gold sources marked
"absent" (e.g. Brightcell is NOT in the supplier master) are not retrievable and are skipped.

Answer model: gemini-3.8-flash (Google's OpenAI-compatible endpoint; OpenRouter before 3 Nov 2026) for every method, temperature 0, recorded to cassettes
(ledgerline/cassettes/<cassette>.jsonl) so NB3 replays without a key. Cost = real tokens x PRICE_USD.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

from . import corpus as C

# The course OpenRouter key hit its monthly limit on 3 Nov 2026; Rajat approved the same model through Google's own
# OpenAI-compatible endpoint (ledgerline.llm provider "gemini", key GEMINI_API_KEY). Logs name the provider.
ANSWER_MODEL = os.environ.get("L3_ANSWER_MODEL", "gemini:gemini-3.8-flash")
JUDGE_MODEL = os.environ.get("L3_JUDGE_MODEL", "gemini:gemini-3.8-flash")
# USD per million tokens (input, output): OpenRouter's list price for google/gemini-3.8-flash (/api/v1/models, 3 Nov 2026),
# used for both routes (OpenRouter passes the provider's price through; Google's own bill is the exact figure).
PRICE_USD = {"gemini-3.8-flash": (0.825, 4.125)}
KS = (1, 3, 5, 10)
TYPES = ["single_lookup", "procedure", "rule", "service_field", "table_lookup", "multi_hop", "version_conflict",
         "exact_code", "not_in_docs", "permission"]

ROLE_NAMES = {
    "PUR-EXEC": "Emma Clarke (ECLARKE), purchase executive",
    "PUR-SR": "Luis Moreno (LMORENO), senior buyer",
    "PUR-MGR": "Daniel Okafor (DOKAFOR), purchase manager",
    "STORES": "Aiko Tanaka (ATANAKA), stores",
    "HR-MGR": "an HR manager (member of the HR group NBC-HR-CONF)",
    "IT-ADMIN": "an IT administrator (not in HR)",
}


# =============================================================================== text normalisation (as eval/check_gold.py)
def norm(s: str) -> str:
    s = str(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ").replace("­", "")
    s = re.sub(r"\*\*|__", "", s)
    return re.sub(r"\s+", "", s).lower()


def norm_loose(s: str) -> str:
    """For answers: also ignore £ and thousands separators ('£119.00' ~ '119.00', '3,000' ~ '3000')."""
    s = norm(s).replace("£", "")
    return re.sub(r"(?<=\d),(?=\d{3})", "", s)


def pct(xs, q) -> float | None:
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    k = (len(xs) - 1) * q / 100
    f, c = math.floor(k), math.ceil(k)
    return xs[f] if f == c else xs[f] + (xs[c] - xs[f]) * (k - f)


def lat(xs) -> dict:
    xs = [x for x in xs if x is not None]
    if not xs:
        return {}
    return {"n": len(xs), "p50": round(pct(xs, 50), 4), "p95": round(pct(xs, 95), 4), "mean": round(sum(xs) / len(xs), 4),
            "max": round(max(xs), 4)}


def cost_usd(tokens_in: int, tokens_out: int, model: str = ANSWER_MODEL) -> float:
    p = PRICE_USD.get(model.split(":", 1)[-1].split("/")[-1])
    return 0.0 if not p else (tokens_in * p[0] + tokens_out * p[1]) / 1e6


# =============================================================================== the golden set
class Golden:
    """Questions (documentation by default), facts, and file-identity for duplicates, read from the dump's eval/."""

    def __init__(self, root=None, category: str = "documentation"):
        self.root = C.dump_root(root)
        self.qs = C.questions(self.root, category)
        self.facts = C.facts(self.root)
        self.by_id = {q["id"]: q for q in self.qs}
        self._same = {}
        shas = {}
        for rel in C.list_files(self.root):
            h = hashlib.sha1(open(self.root / rel, "rb").read()).hexdigest()
            shas.setdefault(h, []).append(rel)
        for group in shas.values():
            for r in group:
                self._same[r] = set(group)

    def same_file(self, a: str, b: str) -> bool:
        return a == b or b in self._same.get(a, ())

    def gold(self, q) -> list[dict]:
        return [g for g in q.get("gold_sources", []) if not g.get("absent")]

    def gold_facts(self, q) -> list[dict]:
        return [self.facts[f] for f in q.get("fact_ids", []) if f in self.facts and self.facts[f].get("mode") == "present"]

    def expected(self, q) -> str:
        if q["type"] == "not_in_docs":
            return "abstain"
        if q["type"] == "permission":
            return q.get("expected_behaviour") or "refuse"
        return "answer"


def _item_locs(item) -> list[tuple[str, dict]]:
    if item.get("sources"):
        return [(s["file"], s.get("loc") or {}) for s in item["sources"]]
    return [(item.get("file", ""), item.get("loc") or {})]


def loc_match(G: Golden, g: dict, file: str, loc: dict) -> str | None:
    """'page' | 'row' | 'file' when the item location matches gold source g, else None."""
    if not G.same_file(file, g["file"]):
        return None
    gp = g.get("pages") or ([g["page"]] if g.get("page") else None)
    if gp:
        ip = loc.get("pages") or ([loc["page"]] if loc.get("page") else None)
        if not ip:
            return "file"
        return "page" if set(gp) & set(ip) else None
    if g.get("row"):
        sheet = g.get("sheet") or ""
        if loc.get("rows"):
            ab = loc["rows"].get(sheet)
            return "row" if ab and ab[0] <= g["row"] <= ab[1] else None
        if loc.get("row"):
            return "row" if (loc.get("sheet") or "") == sheet and loc["row"] == g["row"] else None
        return "file"
    return "file"


def _has(t: str, needle: str) -> bool:
    n = norm(needle)
    if n in t:
        return True
    m = re.fullmatch(r"(\d+)\.0+", n)  # a spreadsheet stores 119.00 as 119: accept the bare number, not 1190 or 119.5
    return bool(m and re.search(rf"(?<![\d.]){m.group(1)}(?![\d]|\.\d)", t))


def contains_fact(text: str, fact: dict) -> bool:
    t = norm(text)
    return all(_has(t, n) for n in fact.get("needles", []))


def gold_hits(q, items, G: Golden, ks=KS) -> dict:
    """Retrieval scores for one question. rank = 1-based rank of the first item matching any gold source.
    Only questions this user should get an answer to are scored (not_in_docs and refused permission questions have
    n_gold = 0 and are left out of recall/MRR; their behaviour is scored on the answer)."""
    golds = G.gold(q) if G.expected(q) == "answer" else []
    gf = G.gold_facts(q)
    out = {"n_gold": len(golds), "rank": None, "levels": {}}
    if not golds:
        return out
    found_at = {}
    fact_at = {}
    for r, it in enumerate(items, 1):
        for gi, g in enumerate(golds):
            for f, l in _item_locs(it):
                lv = loc_match(G, g, f, l)
                if lv and gi not in found_at:
                    found_at[gi] = r
                    out["levels"][lv] = out["levels"].get(lv, 0) + 1
        for fi, fact in enumerate(gf):
            if fi not in fact_at and contains_fact(it.get("text", ""), fact):
                fact_at[fi] = r
    out["rank"] = min(found_at.values()) if found_at else None
    for k in ks:
        out[f"hit@{k}"] = int(out["rank"] is not None and out["rank"] <= k)
        out[f"cov@{k}"] = round(sum(1 for r in found_at.values() if r <= k) / len(golds), 4)
        out[f"fact@{k}"] = int(any(r <= k for r in fact_at.values())) if gf else None
    out["rr"] = round(1 / out["rank"], 4) if out["rank"] else 0.0
    return out


# =============================================================================== the shared answer step
ANSWER_SYSTEM = """You are Ask Northbridge, the documentation assistant of Northbridge Cycles (Manchester), who run Ledgerline ERP 7.2.
Today is Monday 26 October 2026. You are answering {who}.
Answer ONLY from the numbered sources in the user message. Cite every fact with its source number in square brackets, like [2] or [1][4].
- Give the rule in force today. A source marked SUPERSEDED, an old copy, or NOT YET IN FORCE does not apply today; if it matters, say what changes and when.
- If an amendment, release note or e-mail changed what an older document says, give the current position and mention the change.
- If the sources do not answer the question, reply "NOT IN THE DOCUMENTS." and one sentence on what is missing. Never guess.
- If the question asks for confidential HR information that this user may not see, refuse politely and say who may see it.
Be concise: at most 150 words, plain sentences, exact codes and numbers as the sources give them."""


def render_sources(items, max_chars: int | None = 9000) -> str:
    out = []
    for i, it in enumerate(items, 1):
        cite = it.get("cite") or it.get("file", "")
        m = it.get("meta") or {}
        st = C.status_line(m) if m else ""
        text = (it.get("text") or "")[:max_chars] if max_chars else (it.get("text") or "")
        out.append(f"[{i}] {cite}{' (' + st + ')' if st else ''}\n{text}")
    return "\n\n".join(out)


def answer_messages(q, items, max_chars: int | None = 9000) -> list[dict]:
    """The exact prompt every method's answer goes through. Each source's text is cut at max_chars (None = whole)."""
    role = C.role_of(q)
    return [{"role": "system", "content": ANSWER_SYSTEM.format(who=ROLE_NAMES.get(role, role))},
            {"role": "user", "content": f"Sources:\n\n{render_sources(items, max_chars)}\n\nQuestion: {q['question']}"}]


def answer(q, items, llm, max_chars: int | None = 9000) -> dict:
    r = llm.chat(answer_messages(q, items, max_chars))
    text = r.content or ""
    return {"answer": text, "cited": cited_numbers(text, len(items)), "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
            "llm_seconds": r.seconds, "cost_usd": round(cost_usd(r.tokens_in, r.tokens_out, llm.model), 6),
            "replayed": r.replayed}


def cited_numbers(text: str, n: int) -> list[int]:
    out = []
    for grp in re.findall(r"\[(\d+(?:\s*[,;–-]\s*\d+)*)\]", text or ""):
        for x in re.split(r"[,;–-]", grp):
            x = x.strip()
            if x.isdigit() and 1 <= int(x) <= n and int(x) not in out:
                out.append(int(x))
    return out


# =============================================================================== scoring
ABSTAIN = re.compile(r"(?i)not in the documents|not (?:in|covered by|found in|mentioned in|stated in|given in) (?:the |our |any |these )?(?:documents|sources|documentation|records)"
                     r"|(?:sources|documents) do not (?:say|state|contain|give|mention|include|cover|list|specify)"
                     r"|no (?:such|information|record|rate contract|document)|there is no\b|i (?:cannot|can't|could not) find|does not (?:exist|have a)")
REFUSE = re.compile(r"(?i)confidential|not (?:able|allowed|permitted|authori[sz]ed) to|cannot (?:share|provide|disclose|give)|can't (?:share|provide|disclose)"
                    r"|restricted to|only (?:hr|the hr)|hr only|refuse|may not see|do not have access|don't have access")


def _hr_values(G: Golden, q) -> list[str]:
    """Strings that would leak confidential HR content: the confidential facts' needles and their numbers."""
    out = []
    for fid in q.get("fact_ids", []):
        f = G.facts.get(fid)
        if f and "CONFIDENTIAL" in f["file"]:
            out += f.get("needles", [])
            for n in f.get("needles", []):
                out += re.findall(r"£\s?\d[\d,]*(?:\.\d+)?|\d+(?:\.\d+)?%|\b\d{1,2} \w+ 20\d\d\b", n)
    return [x for x in out if len(norm_loose(x)) >= 3]


def fact_check(q, text: str, G: Golden) -> dict:
    """The exact-fact check. answer: every must_contain string is in the answer (None if the question has none).
    abstain: the answer abstains and contains none of absent_terms. refuse: it refuses or abstains and leaks nothing."""
    exp = G.expected(q)
    t = norm_loose(text or "")
    if exp == "abstain":
        # absent_terms are what must not exist in the corpus; in an answer only an invented CODE counts against it
        # ("I cannot find the Wi-Fi password" repeats the question, it does not invent anything)
        bad = [a for a in q.get("absent_terms", []) if re.search(r"[\d/]", a) and norm_loose(a) in t]
        ok = bool(ABSTAIN.search(text or "")) and not bad
        return {"ok": ok, "expected": exp, "abstained": bool(ABSTAIN.search(text or "")), "bad_terms": bad}
    if exp == "refuse":
        leaks = [v for v in _hr_values(G, q) if norm_loose(v) in t]
        refused = bool(REFUSE.search(text or "")) or bool(ABSTAIN.search(text or ""))
        return {"ok": refused and not leaks, "expected": exp, "refused": refused, "leaks": leaks}
    must = q.get("must_contain", [])
    if not must:
        return {"ok": None, "expected": exp, "missing": []}
    miss = [m for m in must if norm_loose(m) not in t]
    return {"ok": not miss, "expected": exp, "missing": miss}


JUDGE_SYSTEM = """You grade answers from a company documentation assistant against a reference answer. Reply with JSON only:
{"correct": true or false, "reason": "<one short sentence>"}"""

JUDGE_USER = """Question: {question}
Asked by: {who}
Expected behaviour: {expected}
Reference answer: {reference}
Key facts a correct answer must state: {must}

Candidate answer:
{answer}

Rules:
- expected "answer": correct if the candidate gives the key facts of the reference that answer the question and says nothing that contradicts it. A superseded, future or wrong value presented as today's rule is incorrect. Extra detail is fine if it is not wrong. Citations like [2] are fine.
- expected "abstain": correct if the candidate says the information is not in the documents (or explains, as the reference does, that it does not exist) and invents nothing.
- expected "refuse": correct if the candidate declines to give the confidential information (or says it is not available to this user) and reveals none of it.
- expected "answer" for an HR user: the confidential facts must be given."""


def judge(q, text: str, llm, G: Golden | None = None) -> dict:
    exp = G.expected(q) if G else ("abstain" if q["type"] == "not_in_docs" else "answer")
    role = C.role_of(q)
    msg = JUDGE_USER.format(question=q["question"], who=ROLE_NAMES.get(role, role), expected=exp,
                            reference=q["reference_answer"], must=", ".join(q.get("must_contain", [])) or "(none listed)",
                            answer=text or "(empty)")
    r = llm.chat([{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": msg}])
    raw = r.content or ""
    m = re.search(r"\{.*\}", raw, re.S)
    verdict = None
    reason = raw[:200]
    if m:
        try:
            d = json.loads(m.group(0))
            verdict = bool(d.get("correct"))
            reason = str(d.get("reason", ""))[:300]
        except json.JSONDecodeError:
            pass
    if verdict is None:
        verdict = bool(re.search(r'"correct"\s*:\s*true', raw))
    return {"ok": verdict, "reason": reason, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
            "cost_usd": round(cost_usd(r.tokens_in, r.tokens_out, llm.model), 6)}


def citation_check(q, rec: dict, items, G: Golden) -> dict | None:
    """Only for questions that should be answered. ok = at least one citation, and one of the cited items contains
    a gold fact (needle match) or sits at a gold location. precision = share of cited items that do."""
    if G.expected(q) != "answer":
        return None
    cited = rec.get("cited") or []
    if not cited:
        return {"ok": False, "n_cited": 0, "precision": 0.0}
    golds, gf = G.gold(q), G.gold_facts(q)
    good = 0
    for n in cited:
        it = items[n - 1]
        ok = any(contains_fact(it.get("text", ""), f) for f in gf) or any(
            loc_match(G, g, f, l) for g in golds for f, l in _item_locs(it))
        good += int(bool(ok))
    return {"ok": good > 0, "n_cited": len(cited), "precision": round(good / len(cited), 3)}


def rescore(rep: dict, G: Golden) -> dict:
    """Recompute the deterministic checks (fact, citation needs items so it is kept) from stored answers, and the summary."""
    for r in rep["records"]:
        r["fact"] = fact_check(G.by_id[r["id"]], r["answer"], G)
    rep["summary"] = summarize(rep["records"])
    return rep


def kappa(a: list[bool], b: list[bool]) -> float | None:
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


# =============================================================================== running a method
def retrieval_only(method, G: Golden | None = None, qs=None, ks=KS) -> dict:
    """Retrieval metrics only (no LLM answer). Calls the method sequentially, so the latency is not shared."""
    G = G or Golden()
    recs = []
    for q in qs or G.qs:
        t0 = time.perf_counter()
        out = method(q["question"], C.role_of(q))
        secs = out.get("seconds", time.perf_counter() - t0)
        recs.append({"id": q["id"], "type": q["type"], "retrieval_s": secs, "retrieval": gold_hits(q, out["items"], G, ks),
                     "retrieval_llm_s": out.get("llm_seconds", 0.0), "retrieval_cost_usd": out.get("cost_usd", 0.0),
                     "items": [i.get("id") for i in out["items"][: max(ks)]]})
    return {"records": recs, "summary": summarize_retrieval(recs, ks)}


def summarize_retrieval(recs, ks=KS) -> dict:
    def agg(rs):
        rs = [r for r in rs if r["retrieval"]["n_gold"]]
        if not rs:
            return {"n": 0}
        d = {"n": len(rs), "mrr": round(sum(r["retrieval"]["rr"] for r in rs) / len(rs), 4)}
        for k in ks:
            d[f"recall@{k}"] = round(sum(r["retrieval"][f"hit@{k}"] for r in rs) / len(rs), 4)
            d[f"coverage@{k}"] = round(sum(r["retrieval"][f"cov@{k}"] for r in rs) / len(rs), 4)
            fx = [r["retrieval"][f"fact@{k}"] for r in rs if r["retrieval"].get(f"fact@{k}") is not None]
            d[f"fact_recall@{k}"] = round(sum(fx) / len(fx), 4) if fx else None
        return d

    out = {"overall": agg(recs), "by_type": {t: agg([r for r in recs if r["type"] == t]) for t in TYPES},
           "latency_s": lat([r["retrieval_s"] for r in recs])}
    lv = {}
    for r in recs:
        for k, v in r["retrieval"].get("levels", {}).items():
            lv[k] = lv.get(k, 0) + v
    out["match_levels"] = lv
    return out


def run(method, name: str, G: Golden | None = None, qs=None, answer_llm=None, judge_llm=None, workers: int = 8,
        cassette: str = "L3v4_answers", judge_cassette: str = "L3v4_judge", ks=KS, log_items: int = 10) -> dict:
    """The full harness for one method: retrieve (sequential, timed), answer with ANSWER_MODEL (parallel),
    fact check + judge + citation check, then summarise. Returns {"name", "records", "summary"}."""
    from ...llm import LLM

    G = G or Golden()
    qs = qs or G.qs
    answer_llm = answer_llm or LLM(ANSWER_MODEL, cassette=cassette, max_tokens=2048)
    judge_llm = judge_llm or LLM(JUDGE_MODEL, cassette=judge_cassette, max_tokens=512)
    recs, its = [], {}
    for q in qs:
        t0 = time.perf_counter()
        out = method(q["question"], C.role_of(q))
        secs = out.get("seconds", time.perf_counter() - t0)
        its[q["id"]] = out
        recs.append({"id": q["id"], "type": q["type"], "difficulty": q.get("difficulty"), "role": C.role_of(q),
                     "retrieval_s": secs, "retrieval_llm_s": out.get("llm_seconds", 0.0),
                     "retrieval_tokens_in": out.get("tokens_in", 0), "retrieval_tokens_out": out.get("tokens_out", 0),
                     "retrieval_cost_usd": out.get("cost_usd", 0.0),
                     "retrieval": gold_hits(q, out["items"], G, ks),
                     "items": [{"id": i.get("id"), "cite": i.get("cite")} for i in out["items"][:log_items]]})

    def finish(rec):
        q = G.by_id[rec["id"]] if rec["id"] in G.by_id else next(x for x in qs if x["id"] == rec["id"])
        out = its[rec["id"]]
        items = out["items"]
        if out.get("answer") is not None:
            a = {"answer": out["answer"], "cited": cited_numbers(out["answer"], len(items)), "tokens_in": 0,
                 "tokens_out": 0, "llm_seconds": 0.0, "cost_usd": 0.0}
        else:
            a = answer(q, items, answer_llm)
        rec.update({k: a[k] for k in ("answer", "cited", "tokens_in", "tokens_out", "llm_seconds", "cost_usd")})
        rec["fact"] = fact_check(q, a["answer"], G)
        rec["judge"] = judge(q, a["answer"], judge_llm, G)
        rec["citation"] = citation_check(q, a, items, G)
        rec["total_s"] = round(rec["retrieval_s"] + a["llm_seconds"], 4)
        rec["cost_total_usd"] = round(a["cost_usd"] + rec["retrieval_cost_usd"], 6)
        return rec

    with ThreadPoolExecutor(workers) as ex:
        recs = list(ex.map(finish, recs))
    return {"name": name, "records": recs, "summary": summarize(recs, ks),
            "answer_model": answer_llm.model, "judge_model": judge_llm.model}


def summarize(recs, ks=KS) -> dict:
    """Every metric, overall and by type. answer_correct = the LLM judge; fact_correct = the exact check where it applies;
    agreement = how often they agree (and Cohen's kappa) on the questions where both apply."""
    def agg(rs):
        if not rs:
            return {"n": 0}
        d = {"n": len(rs)}
        d["answer_correct"] = round(sum(bool(r["judge"]["ok"]) for r in rs) / len(rs), 4)
        fx = [r["fact"]["ok"] for r in rs if r["fact"]["ok"] is not None]
        d["fact_correct"] = round(sum(fx) / len(fx), 4) if fx else None
        d["fact_n"] = len(fx)
        both = [(bool(r["fact"]["ok"]), bool(r["judge"]["ok"])) for r in rs if r["fact"]["ok"] is not None]
        d["both_correct"] = round(sum(a and b for a, b in both) / len(both), 4) if both else None
        cs = [r["citation"] for r in rs if r.get("citation")]
        d["citation_correct"] = round(sum(c["ok"] for c in cs) / len(cs), 4) if cs else None
        d["citation_precision"] = round(sum(c["precision"] for c in cs) / len(cs), 4) if cs else None
        d["retrieval_s"] = lat([r["retrieval_s"] for r in rs])
        d["total_s"] = lat([r["total_s"] for r in rs])
        d["cost_per_q_usd"] = round(sum(r["cost_total_usd"] for r in rs) / len(rs), 6)
        d["tokens_in_per_q"] = round(sum(r["tokens_in"] + r.get("retrieval_tokens_in", 0) for r in rs) / len(rs), 1)
        d["tokens_out_per_q"] = round(sum(r["tokens_out"] + r.get("retrieval_tokens_out", 0) for r in rs) / len(rs), 1)
        return d

    out = {"overall": agg(recs), "by_type": {t: agg([r for r in recs if r["type"] == t]) for t in TYPES},
           "retrieval": summarize_retrieval(recs, ks)}
    both = [(bool(r["fact"]["ok"]), bool(r["judge"]["ok"])) for r in recs if r["fact"]["ok"] is not None]
    out["judge_vs_fact"] = {"n": len(both), "agree": round(sum(a == b for a, b in both) / len(both), 4) if both else None,
                            "kappa": kappa([a for a, _ in both], [b for _, b in both]),
                            "fact_only": sum(a and not b for a, b in both), "judge_only": sum(b and not a for a, b in both)}
    out["judge_cost_usd"] = round(sum(r["judge"]["cost_usd"] for r in recs), 4)
    return out
