"""Drive Bahi through its screens, the way a person does at the legacy client, and count the work.

The legacy client (index.html in this folder) and this driver read the same screen definitions
(erp/screens/*.yaml): which fields a screen has, which button calls which service, which fields a button
sends and which it fills. So an order placed "by hand" here makes exactly the service calls the legacy
client would make, with the same X-Screen / X-Task headers, and the server records them in its live run.

    from fastapi.testclient import TestClient
    from bahi.server import create_app
    from bahi.legacy_ui.driver import Desk, Tally
    http, tally = TestClient(create_app()), Tally()
    kavita = Desk(http, tally, "Kavita").sign_in("KJOSHI", "kavita@123")
    s = kavita.open("INV-STK-02").type(itm_cd="GSK-SIL-05L").press("Query")
    s.form["cover_days"]   # 9
    tally.table()          # screens opened, fields typed, codes typed, sign-ins, buttons, errors ...
"""
from __future__ import annotations

from collections import Counter

import yaml

from ..server import load_screens

def is_code(f: dict) -> bool:
    """A field the user must know a code for: *_cd / *_type names, F2 lookups, and the A/R decision."""
    return f["name"].endswith(("_cd", "_type")) or bool(f.get("lookup")) or f["name"] == "decision"


def is_hidden(f: dict) -> bool:
    return f.get("label") == "(hidden)"


def is_grid(f: dict) -> bool:
    return f.get("type") == "grid"


COUNTERS = ["screens opened", "fields typed", "codes typed", "characters typed", "buttons pressed",
            "sign-ins", "error codes", "service calls"]


class Tally:
    """The counters for one piece of work, shared by everyone who touches it (Kavita, then Rohit)."""

    def __init__(self):
        self.c = Counter()
        self.by_person: dict[str, Counter] = {}
        self.events: list[dict] = []  # one row per human action, in order
        self.frames: list[dict] = []  # what the window showed after each action (for the slides)

    def add(self, who: str, key: str, n: int = 1):
        self.c[key] += n
        self.by_person.setdefault(who, Counter())[key] += n

    def table(self) -> dict:
        return {k: self.c[k] for k in COUNTERS}

    def __repr__(self):
        return " · ".join(f"{k}: {v}" for k, v in self.table().items())


class Desk:
    """One person at one PC with the Bahi client open. Holds their session token."""

    def __init__(self, http, tally: Tally, who: str, base: str = "", tenant: str | None = None, modules=()):
        """modules: capstone modules installed on the server, so their screens can be opened too."""
        self.http, self.tally, self.who, self.base, self.tenant = http, tally, who, base.rstrip("/"), tenant
        self.screens = load_screens(modules)
        self.token = None
        self.user = None

    def _h(self, screen=None, task=None):
        h = {}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if self.tenant:
            h["X-Tenant"] = self.tenant
        if screen:
            h["X-Screen"] = screen
        if task:
            h["X-Task"] = task
        return h

    def sign_in(self, user_id: str, password: str, ou_cd: str = "RSW-PUN-01") -> "Desk":
        s = self.open("SYS-LGN-01")
        s.type(user_id=user_id, password=password)
        if s.form.get("ou_cd") != ou_cd:
            s.type(ou_cd=ou_cd)
        s.press("Sign in")
        if not self.token:
            raise PermissionError(s.status)
        return self

    def open(self, code: str) -> "Screen":
        self.tally.add(self.who, "screens opened")
        sc = Screen(self, self.screens[code])
        self.tally.events.append({"who": self.who, "screen": code, "action": "open", "detail": sc.title})
        sc._frame()
        return sc


class Screen:
    def __init__(self, desk: Desk, spec: dict):
        self.desk, self.spec = desk, spec
        self.code, self.title = spec["code"], spec["title"]
        self.fields = {f["name"]: f for f in spec.get("fields", [])}
        self.form = {f["name"]: str(f["default"]) for f in spec.get("fields", []) if "default" in f}
        self.tasks = {t["button"]: t for t in spec.get("tasks", [])}
        self.rows: list[dict] = []
        self.status, self.err, self.last = "Ready", False, None
        self.hot = None

    # ------------------------------------------------------------------ what a person does
    def type(self, **values) -> "Screen":
        """Type values into fields. Counts every field, every code field and every character."""
        t = self.desk.tally
        for k, v in values.items():
            f = self.fields[k]
            if f.get("readonly") or is_hidden(f) or is_grid(f):
                raise ValueError(f"{self.code}: field {k} is read-only")
            v = str(v)
            self.form[k] = v
            t.add(self.desk.who, "fields typed")
            t.add(self.desk.who, "characters typed", len(v))
            if is_code(f):
                t.add(self.desk.who, "codes typed")
            t.events.append({"who": self.desk.who, "screen": self.code, "action": "type",
                             "detail": f"{f['label']} = {'••••••' if k == 'password' else v}",
                             "code": is_code(f)})
        self._frame()
        return self

    def pick(self, row: int = 0) -> "Screen":
        """Highlight a row in the result list and press Select (copies the code; nothing is typed)."""
        grid = self._grid() or {}
        pick = grid.get("pick")
        r = self.rows[row]
        pairs = pick.items() if isinstance(pick, dict) else [(pick, pick)]
        for col, fld in pairs:
            self.form[fld] = str(r[col])
        self.desk.tally.add(self.desk.who, "buttons pressed")
        self.desk.tally.events.append({"who": self.desk.who, "screen": self.code, "action": "select",
                                       "detail": ", ".join(f"{fld} = {r[col]}" for col, fld in pairs)})
        self._frame()
        return self

    def press(self, button: str) -> "Screen":
        """Press a button: call its service with the fields it sends, then fill the fields it fills."""
        d, t = self.desk, self.desk.tally
        task = self.tasks[button]
        t.add(d.who, "buttons pressed")
        self.hot = button
        svc = task.get("service")
        payload = {k: self.form[k] for k in task.get("sends", []) if self.form.get(k) not in (None, "")}
        if svc is None:
            t.events.append({"who": d.who, "screen": self.code, "action": "press", "detail": button})
            return self
        if svc == "login":
            r = d.http.post(d.base + "/login", json=payload, headers=d._h())
            env = r.json()
            if env.get("rc") == "S":
                d.token, d.user = env["token"], env["user_id"]
                self.form.update(role_cd=env["role_cd"], name=env["name"])
                t.add(d.who, "sign-ins")
                t.add(d.who, "service calls")  # the profile load the server records
                self._show({"rc": "S", "msg": env["msg"], "data": None}, button, svc, payload)
            else:
                self._show(env, button, svc, payload)
            return self
        r = d.http.post(d.base + f"/svc/{svc}", json=payload, headers=d._h(self.code, button))
        env = r.json() if r.status_code != 504 else {"rc": "E", "err_cd": "HTTP-504", "msg": "NO REPLY FROM SERVER"}
        t.add(d.who, "service calls")
        if env.get("rc") != "E" and isinstance(env.get("data"), dict):
            data = env["data"]
            fills = task.get("fills") or []
            pairs = fills.items() if isinstance(fills, dict) else [(f, f) for f in fills]
            for src, fld in pairs:
                if src in data and data[src] is not None:
                    if isinstance(data[src], list):
                        self.rows = data[src]
                    else:
                        self.form[fld] = _show_val(data[src])
        self._show(env, button, svc, payload)
        return self

    # ------------------------------------------------------------------ what the window shows
    def _show(self, env, button, svc, payload):
        t = self.desk.tally
        self.last = env
        if env.get("rc") == "E":
            self.status, self.err = f"{env.get('err_cd')}: {env.get('msg')}", True
            t.add(self.desk.who, "error codes")
        else:
            self.status, self.err = env.get("msg") or "Ready", False
        t.events.append({"who": self.desk.who, "screen": self.code, "action": "press", "detail": button,
                         "service": svc, "payload": {k: ("••••••" if k == "password" else v) for k, v in payload.items()},
                         "rc": env.get("rc"), "status": self.status})
        self._frame()

    def _grid(self):
        return next((f for f in self.spec.get("fields", []) if is_grid(f)), None)

    def _frame(self):
        flds = []
        for f in self.spec.get("fields", []):
            if is_hidden(f) or is_grid(f):
                continue
            kind = "ro" if f.get("readonly") else ("code" if is_code(f) else "text")
            v = self.form.get(f["name"], "")
            flds.append([f["label"], "••••••••" if f["name"] == "password" and v else v, kind, bool(f.get("req"))])
        lst = self._grid()
        if lst and not lst.get("columns") and self.rows:
            lst = {**lst, "columns": list(self.rows[0])[:6]}
        rows = [[str(r.get(c, "")) if isinstance(r, dict) else str(r) for c in lst["columns"]] for r in self.rows[:6]] if lst and self.rows and lst.get("columns") else None
        self.desk.tally.frames.append({
            "who": self.desk.who, "user": self.desk.user or "", "code": self.code, "title": self.title,
            "menu": self.spec.get("menu"), "fields": flds, "list_cols": lst.get("columns") if lst else None, "rows": rows,
            "buttons": list(self.tasks), "hot": self.hot, "status": self.status, "err": self.err,
            "counts": self.desk.tally.table()})

    def __repr__(self):
        return f"<{self.code} {self.title} · status bar: {self.status}>"


def _show_val(v):
    if isinstance(v, float) and v.is_integer() and abs(v) >= 1000:
        return str(int(v))
    return str(v)


def screen_yaml(code: str) -> str:
    """The screen's definition as YAML text (for printing in a notebook)."""
    return yaml.safe_dump(load_screens()[code], sort_keys=False, allow_unicode=True)
