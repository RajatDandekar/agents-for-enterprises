"""Lecture 7 / assignment A7: the four failure drills, for ANY module's main write.

Every module kit saves with a `client_ref` field and lists by `client_ref` (like po_save / po_search), so the same
keyed write works everywhere. Describe your module's write once, as a WriteSpec, and run the drills:

    spec = WriteSpec(module="hr_leave", user="KJOSHI", save_svc="lv_save", list_svc="lv_list", doc_field="lv_no",
                     payload=leave_payload, docs=leave_docs, content=("E-1042", "EL", "2026-10-29", "2026-10-30"))
    report = run_module_drills(spec)      # four drills, each with passed True/False and what Bahi holds afterwards

    D1  timeout AFTER the commit       naive retry vs keyed retry: how many documents exist afterwards?
    D2  error BEFORE the commit        the keyed retry still ends with exactly one document
    D3  crash after the commit         a fresh process (new session, no memory) retries with the same key: finds it
    D4  kill switch                    switched off: nothing written; switched back on: written once
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..erp.engine import ERP, ServiceTimeout, Session
from .keys import content_key
from .killswitch import Flags, WritesPaused


class Refused(Exception):
    pass


@dataclass
class WriteSpec:
    module: str                         # the kit, e.g. "hr_leave" ("" for purchasing itself)
    user: str                           # who writes, e.g. "KJOSHI"
    save_svc: str                       # the write service, e.g. "lv_save"
    list_svc: str                       # the read that filters by client_ref, e.g. "lv_list"
    doc_field: str                      # the document number in the save reply, e.g. "lv_no"
    payload: Callable[[Session], dict]  # builds the save payload (fetch a fresh token here if the screen needs one)
    docs: Callable[[ERP], list]         # the live documents for THIS content (how you count duplicates)
    content: tuple = ()                 # what the document IS; the key is a hash of it
    retryable: set = field(default_factory=lambda: {"ERR-SYS-0503"})

    def key(self) -> str:
        return content_key(self.module, self.user, self.save_svc, *self.content)

    def erp(self) -> ERP:
        return ERP(modules=[self.module] if self.module else None)


def find(s: Session, spec: WriteSpec, key: str):
    r = s.call(spec.list_svc, client_ref=key)
    rows = (r.get("data") or {}).get("rows") or []
    return rows[0].get(spec.doc_field) if rows else None


def keyed_write(s: Session, spec: WriteSpec, key: str, flags: Flags | None = None, attempts: int = 3) -> dict:
    """Look up by key; if absent, write carrying the key; after a lost reply, look again. Retries only what can help."""
    for a in range(1, attempts + 1):
        doc = find(s, spec, key)
        if doc:
            return {"doc": doc, "found_by_key": True, "attempts": a}
        if flags:
            flags.check_write(spec.user, by_human=True)
        try:
            r = s.call(spec.save_svc, **{**spec.payload(s), "client_ref": key})
        except ServiceTimeout:
            continue  # the next attempt looks up the key first
        if r["rc"] == "E":
            if r["err_cd"] in spec.retryable:
                continue
            raise Refused(f"{r['err_cd']} {r['msg']}")
        return {"doc": r["data"][spec.doc_field], "found_by_key": False, "attempts": a}
    raise Refused(f"gave up after {attempts} attempts")


def naive_write(s: Session, spec: WriteSpec, attempts: int = 3) -> dict:
    """Press Save again on any failure, with no key."""
    last = ""
    for a in range(1, attempts + 1):
        try:
            r = s.call(spec.save_svc, **spec.payload(s))
        except ServiceTimeout as e:
            last = str(e)
            continue
        if r["rc"] == "E":
            last = f"{r['err_cd']} {r['msg']}"
            continue
        return {"doc": r["data"][spec.doc_field], "reported": "done", "attempts": a}
    return {"doc": None, "reported": "failed", "attempts": attempts, "last_error": last}


def run_module_drills(spec: WriteSpec) -> dict:
    out = {"module": spec.module or "purchasing", "write": spec.save_svc, "key": spec.key(), "drills": []}

    def add(name, passed, **kw):
        out["drills"].append({"drill": name, "passed": bool(passed), **kw})

    # D1: timeout after commit
    erp = spec.erp(); erp.inject(spec.save_svc, "timeout_after_commit", 1)
    n = naive_write(erp.session(spec.user), spec)
    naive_docs = len(spec.docs(erp))
    erp = spec.erp(); erp.inject(spec.save_svc, "timeout_after_commit", 1)
    k = keyed_write(erp.session(spec.user), spec, spec.key())
    add("D1 timeout after commit", len(spec.docs(erp)) == 1, naive=n, naive_docs=naive_docs, keyed=k,
        keyed_docs=len(spec.docs(erp)))
    # D2: error before commit, twice
    erp = spec.erp(); erp.inject(spec.save_svc, "error_before", 2)
    k = keyed_write(erp.session(spec.user), spec, spec.key())
    add("D2 error before commit", len(spec.docs(erp)) == 1, keyed=k, keyed_docs=len(spec.docs(erp)))
    # D3: crash after commit: process 1 commits and dies before it can record the result; process 2 retries
    erp = spec.erp()
    first = keyed_write(erp.session(spec.user), spec, spec.key())
    del first  # "the process died": nothing it knew survives, except what is in Bahi
    second = keyed_write(erp.session(spec.user), spec, spec.key())
    add("D3 crash after commit", len(spec.docs(erp)) == 1 and second["found_by_key"], second=second,
        keyed_docs=len(spec.docs(erp)))
    # D4: kill switch
    erp = spec.erp(); flags = Flags(); flags.kill("drill")
    try:
        keyed_write(erp.session(spec.user), spec, spec.key(), flags)
        blocked = False
    except WritesPaused:
        blocked = True
    while_off = len(spec.docs(erp))
    flags.revive()
    k = keyed_write(erp.session(spec.user), spec, spec.key(), flags)
    add("D4 kill switch", blocked and while_off == 0 and len(spec.docs(erp)) == 1, blocked=blocked,
        docs_while_off=while_off, after=k, docs_after=len(spec.docs(erp)))
    out["passed"] = sum(d["passed"] for d in out["drills"])
    return out


# ------------------------------------------------------------------ the worked example: HR leave (Kavita's two days off)
def _leave_payload(s: Session) -> dict:
    tok = s.call("lv_fetch", emp_cd="E-1042", lv_cd="EL")["data"]["fetch_tok"]
    return dict(emp_cd="E-1042", lv_cd="EL", from_dt="2026-10-29", to_dt="2026-10-30", reason="Sister's wedding",
                fetch_tok=tok)


LEAVE_SPEC = WriteSpec(
    module="hr_leave", user="KJOSHI", save_svc="lv_save", list_svc="lv_list", doc_field="lv_no",
    payload=_leave_payload,
    docs=lambda erp: erp.q("SELECT lv_no FROM lv_app WHERE emp_cd='E-1042' AND from_dt='2026-10-29' AND status NOT IN ('CN','RJ')"),
    content=("E-1042", "EL", "2026-10-29", "2026-10-30"))
