"""The Bahi ERP 7.2 sandbox engine.

Four layers, the same as a real legacy ERP:
  Screen  (what the user sees; screens/*.yaml)
  Task    (one button on a screen: Fetch, Save, Release ...)
  Service (an HTTP endpoint with a flat, terse payload; services.py)
  Stored procedure (where the rules live; procs.py)

Every service call is logged with the stored procedures it ran, so a "live run" of the legacy UI
can be replayed and read (Lecture 3). Faults can be injected per service (Lecture 7).
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import random
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from . import seed as S


class BahiError(Exception):
    """A legacy error: a code and a terse message, the way Bahi reports it."""

    def __init__(self, err_cd: str, msg: str):
        super().__init__(f"{err_cd}: {msg}")
        self.err_cd, self.msg = err_cd, msg


class ServiceTimeout(Exception):
    """The server did the work, but the reply never arrived (HTTP 504 over the wire)."""


@dataclass
class Field:
    name: str
    type: str = "str"  # str | int | float | date
    required: bool = False
    desc: str = ""


@dataclass
class Service:
    name: str
    fn: Callable
    fields: list[Field]
    doc: str
    kind: str  # "read" | "write"
    screen: str | None = None


SERVICES: dict[str, Service] = {}
PROCS: dict[str, Callable] = {}


def service(name: str, doc: str, fields: list[tuple] = (), kind: str = "read", screen: str | None = None):
    def deco(fn):
        SERVICES[name] = Service(name, fn, [Field(*f) for f in fields], doc, kind, screen)
        return fn
    return deco


def proc(name: str):
    def deco(fn):
        PROCS[name] = fn
        return fn
    return deco


@dataclass
class CallRecord:
    seq: int
    ts: str
    user: str
    svc: str
    payload: dict
    rc: str = "S"
    err_cd: str | None = None
    msg: str = ""
    data: Any = None
    sps: list = field(default_factory=list)
    screen: str | None = None
    task: str | None = None
    ms: float = 0.0
    timed_out: bool = False


class ERP:
    """One tenant of Bahi ERP: an in-memory SQLite database plus the service layer."""

    def __init__(self, path: str = ":memory:", faults: dict | None = None, latency_ms: float = 0.0,
                 modules: list[str] | None = None):
        """modules: capstone module kits to install on top of purchasing, e.g. ["hr_leave"].
        Each is the package bahi.modules.<name> with SCHEMA (SQL), seed(erp), and services/procs registered
        with the same @service/@proc decorators when the package is imported."""
        from . import procs, services  # noqa: F401  (registers PROCS and SERVICES)

        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.faults: dict[str, dict] = dict(faults or {})
        self.latency_ms = latency_ms
        self.calls: list[CallRecord] = []
        self.sessions: dict[str, str] = {}
        self._clock = dt.datetime.fromisoformat(S.NOW)
        self._cur: CallRecord | None = None
        self.modules: list[str] = []
        self.rng = random.Random(7)  # deterministic tokens, so recorded model replies replay exactly
        self._load()
        for m in modules or []:
            self.install(m)

    def install(self, module: str):
        import importlib

        mod = importlib.import_module(f"bahi.modules.{module}")
        if getattr(mod, "SCHEMA", None):
            self.db.executescript(mod.SCHEMA)
        if hasattr(mod, "seed"):
            mod.seed(self)
        self.db.commit()
        self.modules.append(module)

    # ------------------------------------------------------------------ setup
    def _load(self):
        c = self.db
        c.executescript(S.SCHEMA)
        c.executemany("INSERT INTO org_unit VALUES (?,?,?,?)", S.ORG_UNITS)
        c.executemany("INSERT INTO app_user VALUES (?,?,?,?,?,?,?,?,?,?)", S.USERS)
        for role, svcs in S.ROLE_PERMS.items():
            c.executemany("INSERT INTO role_perm VALUES (?,?)", [(role, s) for s in svcs])
        c.executemany("INSERT INTO item VALUES (?,?,?,?,?,?,?,?)", S.ITEMS)
        c.executemany("INSERT INTO supplier VALUES (?,?,?,?,?,?,?,'MIGRATION','2019-04-01')", S.SUPPLIERS)
        c.executemany("INSERT INTO sup_cert VALUES (?,?,?,?,?,?)", S.SUP_CERTS)
        c.executemany("INSERT INTO sup_rate VALUES (?,?,?,?,?)", S.SUP_RATES)
        c.executemany("INSERT INTO warehouse VALUES (?,?,?)", S.WAREHOUSES)
        c.executemany("INSERT INTO stock VALUES (?,?,?,?,?)", S.STOCK)
        c.executemany("INSERT INTO cost_centre VALUES (?,?,?,?,?)", S.COST_CENTRES)
        c.executemany("INSERT INTO budget VALUES (?,?,?,?)", S.BUDGETS)
        c.executemany("INSERT INTO tax_code VALUES (?,?,?,?)", S.TAX_CODES)
        c.executemany("INSERT INTO pay_term VALUES (?,?,?)", S.PAY_TERMS)
        c.executemany("INSERT INTO doc_seq VALUES (?,?,?,?)", S.DOC_SEQ)
        for po_no, sup, itm, qty, rate, tax, cc, status, cr, rl in S.PAST_POS:
            basic = round(qty * rate, 2)
            taxv = round(basic * 0.18, 2)
            c.execute("INSERT INTO po_hdr VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (po_no, "RSW-PUN-01", sup, None, "DIR" if basic + taxv <= 50000 else "STD", cc, tax,
                       "N45" if sup.startswith("DP") else "N30", cr, "WH-PUN-STR", status, basic, taxv,
                       basic + taxv, "KJOSHI", cr, "RMEHTA" if status == "RL" else None,
                       rl, rl, None, None))
            c.execute("INSERT INTO po_line VALUES (?,?,?,?,?,?)", (po_no, 1, itm, qty, "NOS", rate))
            if status == "PA":
                c.execute("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on)"
                          " VALUES ('PO',?,?,'PENDING','KJOSHI',?)", (po_no, "RMEHTA", cr))
        for itm, whs, oh, *_ in S.STOCK:
            c.execute("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES (?,?,?,?,?,?)",
                      (itm, whs, "2026-10-01", "OPENING", oh, "MIGRATION"))
        c.commit()

    # ------------------------------------------------------------------ clock
    def now(self) -> str:
        self._clock += dt.timedelta(seconds=7)
        return self._clock.isoformat(timespec="seconds")

    @property
    def today(self) -> str:
        return self._clock.date().isoformat()

    def advance(self, **kw):
        """Move the sandbox clock forward, e.g. erp.advance(days=2) while waiting for an approval."""
        self._clock += dt.timedelta(**kw)

    # ------------------------------------------------------------------ data helpers
    def q(self, sql: str, *args) -> list[dict]:
        return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def q1(self, sql: str, *args) -> dict | None:
        r = self.db.execute(sql, args).fetchone()
        return dict(r) if r else None

    def x(self, sql: str, *args):
        return self.db.execute(sql, args)

    def sp(self, name: str, *args, **kw):
        """Run a stored procedure, recording it on the current service call."""
        if self._cur is not None:
            self._cur.sps.append(name)
        return PROCS[name](self, *args, **kw)

    # ------------------------------------------------------------------ sessions
    def login(self, user_id: str, password: str) -> str:
        u = self.q1("SELECT * FROM app_user WHERE user_id=?", user_id.upper())
        if not u or u["password"] != password:
            raise BahiError("ERR-SEC-0002", "INVALID CREDENTIALS")
        tok = self.token(16)
        self.sessions[tok] = u["user_id"]
        return tok

    def session(self, user_id: str) -> "Session":
        """A signed-in client for one user, for code that runs next to the ERP (notebooks, tests)."""
        u = self.q1("SELECT * FROM app_user WHERE user_id=?", user_id.upper())
        if not u:
            raise BahiError("ERR-SEC-0003", "NO SUCH USER")
        return Session(self, u["user_id"])

    def token(self, n: int = 8) -> str:
        return "".join(self.rng.choice("0123456789ABCDEF") for _ in range(n))

    def user(self, user_id: str) -> dict:
        return self.q1("SELECT * FROM app_user WHERE user_id=?", user_id)

    def allowed(self, user_id: str, svc: str) -> bool:
        role = self.user(user_id)["role_cd"]
        return bool(self.q1("SELECT 1 FROM role_perm WHERE role_cd=? AND svc IN (?, '*')", role, svc))

    # ------------------------------------------------------------------ the service layer
    def call(self, svc: str, payload: dict | None = None, user: str = "KJOSHI",
             screen: str | None = None, task: str | None = None) -> dict:
        """Call one Bahi service. Returns the legacy envelope {rc, err_cd, msg, data}.

        rc is "S" (success), "W" (success with a warning) or "E" (error).
        Raises ServiceTimeout if a fault makes the reply get lost after the work is done.
        """
        payload = dict(payload or {})
        rec = CallRecord(len(self.calls) + 1, self.now(), user, svc, copy.deepcopy(payload),
                         screen=screen, task=task)
        self.calls.append(rec)
        t0 = time.perf_counter()
        self._cur = rec
        fault = self.faults.get(svc)
        try:
            if svc not in SERVICES:
                raise BahiError("ERR-SYS-0404", f"SERVICE {svc.upper()} NOT FOUND")
            spec = SERVICES[svc]
            mod = spec.fn.__module__
            if mod.startswith("bahi.modules.") and mod.split(".")[2] not in self.modules:
                raise BahiError("ERR-SYS-0404", f"SERVICE {svc.upper()} NOT FOUND")  # module not installed here
            if not self.allowed(user, svc):
                raise BahiError("ERR-SEC-0001", "ACCESS DENIED")
            args = self._coerce(spec, payload)
            if fault and fault.get("mode") == "error_before":
                self._use_fault(svc)
                raise BahiError("ERR-SYS-0503", "SERVER BUSY, TRY LATER")
            data = spec.fn(self, user, **args)
            self.db.commit()
            msg = ""
            if isinstance(data, dict) and "_msg" in data:
                msg = data.pop("_msg")
            rec.rc = "W" if isinstance(data, dict) and data.get("warn_cd") else "S"
            rec.msg, rec.data = msg, data
        except BahiError as e:
            self.db.rollback()
            rec.rc, rec.err_cd, rec.msg = "E", e.err_cd, e.msg
        finally:
            self._cur = None
            rec.ms = (time.perf_counter() - t0) * 1000 + self.latency_ms
            self.x("INSERT INTO audit_trail(ts,user_id,svc,payload,rc,err_cd) VALUES (?,?,?,?,?,?)",
                   rec.ts, user, svc, json.dumps(payload, default=str), rec.rc, rec.err_cd)
            self.db.commit()
        if fault and fault.get("mode") == "timeout_after_commit" and rec.rc != "E":
            self._use_fault(svc)
            rec.timed_out = True
            raise ServiceTimeout(f"{svc}: no reply within 30 s (the server may or may not have saved)")
        return {"rc": rec.rc, "err_cd": rec.err_cd, "msg": rec.msg, "data": rec.data}

    def _use_fault(self, svc):
        f = self.faults[svc]
        f["times"] = f.get("times", 1) - 1
        if f["times"] <= 0:
            del self.faults[svc]

    def inject(self, svc: str, mode: str = "timeout_after_commit", times: int = 1):
        """Lecture 7: make the next `times` calls of `svc` fail. Modes: timeout_after_commit, error_before."""
        self.faults[svc] = {"mode": mode, "times": times}

    @staticmethod
    def _coerce(spec: Service, payload: dict) -> dict:
        known = {f.name: f for f in spec.fields}
        out = {}
        for k, v in payload.items():
            if k not in known:
                raise BahiError("ERR-SYS-0422", f"UNKNOWN FIELD {k.upper()}")
            f = known[k]
            if v is None or v == "":
                continue
            try:
                if f.type == "int":
                    v = int(float(str(v).replace(",", "")))
                elif f.type == "float":
                    v = float(str(v).replace(",", ""))
                elif f.type == "date":
                    v = _date(str(v))
                else:
                    v = str(v).strip()
            except ValueError:
                raise BahiError("ERR-SYS-0422", f"BAD VALUE FOR {k.upper()}")
            out[k] = v
        for f in spec.fields:
            if f.required and f.name not in out:
                raise BahiError("ERR-SYS-0421", f"{f.name.upper()} MANDATORY")
        return out

    # ------------------------------------------------------------------ inspection (for checks and lectures)
    def live_run(self, since: int = 0) -> list[dict]:
        """The service calls made since call number `since`, with the stored procedures each ran."""
        return [{"seq": r.seq, "screen": r.screen, "task": r.task, "svc": r.svc, "payload": r.payload,
                 "rc": r.rc, "err_cd": r.err_cd, "msg": r.msg, "sps": r.sps, "timed_out": r.timed_out}
                for r in self.calls if r.seq > since]

    def snapshot(self) -> dict:
        tabs = ["po_hdr", "po_line", "pr_hdr", "pr_line", "supplier", "sup_cert", "approval", "ntf_queue",
                "budget", "stock"]
        return {t: self.q(f"SELECT * FROM {t}") for t in tabs}

    def orders(self, **where) -> list[dict]:
        """Purchase orders joined with their single line, newest first. Filters: status, sup_cd, itm_cd, created_by."""
        sql = ("SELECT h.*, l.itm_cd, l.qty, l.rate FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no WHERE 1=1")
        args = []
        for k, v in where.items():
            sql += f" AND {k}=?"
            args.append(v)
        return self.q(sql + " ORDER BY h.po_no DESC", *args)


class Session:
    """A user's signed-in handle: s.call("po_get", po_no="PO/2026/01120")."""

    def __init__(self, erp: ERP, user_id: str):
        self.erp, self.user_id = erp, user_id

    def call(self, svc: str, screen: str | None = None, task: str | None = None, **payload) -> dict:
        return self.erp.call(svc, payload, user=self.user_id, screen=screen, task=task)

    def __repr__(self):
        return f"<Bahi session {self.user_id}>"


def _date(s: str) -> str:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(s)
