"""Lecture 1 v3: the measured cost of the Before.

Drives Bahi ERP 7.2 through its own screen definitions, exactly as the legacy client does (bahi.legacy_ui.driver: same
services, same fields, same X-Screen / X-Task headers), mission by mission, the way the Rasoi Experience's /before
missions go: check stock, raise the PR, approve as Rohit, make and release the PO, receive the goods.

Two runs, each on a fresh Rasoi:
  first_time   what happens to someone who follows the screens: Fetch's defaults (cost centre PRD-05, tax code
               GST18-INTRA) are kept, so the order hits ERR-PO-0412, then saves as a silent Draft; the release is refused
               (ERR-PO-0715); the order is amended to PRD-07 on PUR-POM-06 and released; Neha receives it in two lots.
  careful      what Suresh does, knowing every trap: PRD-07 on the request, GST18-INTER on the order. No errors.
Plus each trap triggered on its own (the direct-PO cap, Save without Fetch, the two Deccans, Shakti Seals).

Minutes cannot be measured without a person, so the script gives an ESTIMATE with the keystroke-level model
(0.28 s a key, 1.1 s a point-and-click, 1.35 s to think before each field or button, 2 s for each screen or service
reply). The Experience's own timer measures real people. Waiting for Rohit and the phone call to IT are not included.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L1-before-and-after/experiments/before_measure.py
-> logs/before_measure.json
"""
import json
import pathlib

import yaml
from fastapi.testclient import TestClient

import bahi
from bahi.legacy_ui.driver import COUNTERS, Desk, Tally
from bahi.server import create_app

OUT = pathlib.Path(__file__).parent / "logs"
OUT.mkdir(exist_ok=True)
AMEND = pathlib.Path(bahi.__file__).parent / "experience" / "screens" / "PUR-POM-06.yaml"  # served by the Experience
NEED = "09-11-2026"


def klm_seconds(events):
    s = 0.0
    for e in events:
        if e["action"] == "open":
            s += 1.35 + 2 * 1.1 + 2.0
        elif e["action"] == "type":
            s += 1.35 + 1.1 + 0.28 * len(e["detail"].split(" = ", 1)[-1])
        elif e["action"] in ("press", "select"):
            s += 1.35 + 1.1 + (2.0 if e.get("service") else 0)
    return s


class Run:
    """One fresh Rasoi, its people at their desks, and the counters split by mission."""

    def __init__(self, name):
        self.name = name
        self.app = create_app()
        self.http = TestClient(self.app)
        self.erp = self.app.state.tenants.setdefault("default", bahi.ERP())
        from bahi.erp.receipts import install_receipts
        install_receipts(self.erp)
        self.tally = Tally()
        self.missions, self._mark, self.notes = [], None, []
        self.desks = {}

    def desk(self, who, uid, pw):
        if who not in self.desks:
            d = Desk(self.http, self.tally, who)
            if AMEND.exists():
                d.screens["PUR-POM-06"] = yaml.safe_load(AMEND.read_text())
            d.sign_in(uid, pw)
            self.desks[who] = d
        return self.desks[who]

    def begin(self, mid, title):
        self._mark = (mid, title, dict(self.tally.c), len(self.tally.events), len(self.erp.calls))

    def end(self, **facts):
        mid, title, c0, e0, k0 = self._mark
        ev = self.tally.events[e0:]
        counts = {k: self.tally.c[k] - c0.get(k, 0) for k in COUNTERS}
        self.missions.append({"id": mid, "title": title, "counts": counts, "klm_seconds": round(klm_seconds(ev), 1),
                              "screens": [e["screen"] for e in ev if e["action"] == "open"],
                              "errors": [e["status"] for e in ev if e.get("rc") == "E"],
                              "events": ev, "facts": facts})
        print(f"  {self.name:10} {mid:9} {counts} ≈{klm_seconds(ev)/60:.1f} min  {facts}")

    def note(self, s):
        self.notes.append({"after_event": len(self.tally.events), "text": s})

    def result(self):
        tot = self.tally.table()
        return {"run": self.name, "totals": tot, "klm_minutes": round(sum(m["klm_seconds"] for m in self.missions) / 60, 1),
                "by_person": {k: dict(v) for k, v in self.tally.by_person.items()},
                "missions": self.missions, "notes": self.notes, "frames": self.tally.frames,
                "distinct_screens": sorted({e["screen"] for e in self.tally.events if e["action"] == "open"}),
                "live_run_calls": len(self.erp.calls)}


def play(run, careful):
    erp = run.erp
    # ---- Mission 1: check the stock
    run.begin("stock", "Check the stock")
    k = run.desk("Kavita", "KJOSHI", "kavita@123")
    s = k.open("INV-ITM-03").type(q="gasket 5").press("Search")
    rows = [r["itm_cd"] for r in s.rows]
    s.pick(0)
    item = s.form["itm_cd"]
    s = k.open("INV-STK-02").type(itm_cd=item).press("Query")
    run.end(item=item, item_rows=rows, on_hand=s.form["on_hand"], daily=s.form["avg_daily_issue"],
            cover_days=s.form["cover_days"], warehouse=s.form["whs_cd"])

    # ---- Mission 2: raise the purchase request
    run.begin("request", "Raise the purchase request")
    s = k.open("PUR-PR-01").type(itm_cd=item).press("Fetch")
    default_cc, est_rate = s.form["cc_cd"], s.form["est_rate"]
    vals = dict(qty="20000", need_dt=NEED, remarks="Diwali run")
    if careful:
        vals["cc_cd"] = "PRD-07"
    s.type(**vals).press("Save")
    pr_no, est_value = s.form["pr_no"], s.form["est_value"]
    s.press("Submit")
    run.end(pr_no=pr_no, default_cc=default_cc, cc_used=s.form["cc_cd"], est_rate=est_rate, est_value=est_value,
            status_bar=s.status)

    # ---- Mission 3: approve it, as Rohit
    run.begin("approve", "Approve it, as Rohit")
    r = run.desk("Rohit", "RMEHTA", "rohit@123")
    s = r.open("PUR-PR-04").press("Inbox")
    row = next(i for i, x in enumerate(s.rows) if x["doc_no"] == pr_no)
    s.pick(row).press("Fetch").type(decision="A", comment="ok").press("Confirm")
    run.end(status_bar=s.status, inbox_rows=len(s.rows))

    # ---- Mission 4: make and release the order
    run.begin("order", "Make and release the order")
    s = k.open("PUR-POH-02").type(itm_cd=item).press("Query")
    last = s.rows[0]
    s.pick(0)
    sup = s.form["sup_cd"]
    s = k.open("PUR-PO-01").type(pr_no=pr_no, sup_cd=sup, itm_cd=item).press("Fetch")
    fetched = {f: s.form.get(f) for f in ("rate", "tax_cd", "cc_cd", "qty")}
    first_err = None
    if careful:
        s.type(tax_cd="GST18-INTER").press("Save")
    else:
        s.press("Save")
        first_err = s.status
        run.note("ERR-PO-0412. She does not know the code and phones IT: a Gujarat supplier needs GST18-INTER.")
        s.type(tax_cd="GST18-INTER").press("Save")
    po_no, save_bar, save_status = s.form.get("po_no"), s.status, s.form.get("status")
    s = k.open("PUR-POR-05").type(po_no=po_no).press("Fetch").press("Release")
    release_1 = s.status
    amended = None
    if not careful:  # the Draft is found when the release is refused; amend the cost centre, then release again
        run.note("Release refused: the order is a Draft. Order amendment, cost centre PRD-07, then release again.")
        s = k.open("PUR-POM-06").type(po_no=po_no).press("Fetch").type(cc_cd="PRD-07").press("Amend")
        amended = s.status
        s = k.open("PUR-POR-05").type(po_no=po_no).press("Fetch").press("Release")
    po = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    run.end(po_no=po_no, supplier=sup, last_order=last, fetched=fetched, first_save_error=first_err,
            save_status_bar=save_bar, save_status_field=save_status, first_release=release_1, amended=amended,
            final_release=s.status, po_db={k_: po[k_] for k_ in ("status", "cc_cd", "tax_cd", "basic_value",
                                                                  "gross_value", "approved_by", "warn_cd")})

    # ---- Mission 5: receive the goods, as Neha (two deliveries)
    run.begin("receive", "Receive the goods, as Neha")
    n = run.desk("Neha", "NDESAI", "neha@123")
    grns = []
    for q, ch in ((12000, "DC-4471"), (8000, "DC-4502")):
        s = n.open("INV-GRN-03").type(po_no=po_no).press("Fetch").type(qty=str(q), remarks=ch).press("Save")
        grns.append({"qty": q, "grn_no": s.form.get("grn_no"), "status_bar": s.status, "balance": s.form.get("balance")})
    stock = erp.q1("SELECT * FROM stock WHERE itm_cd=? AND whs_cd='WH-PUN-STR'", item)
    po = erp.q1("SELECT status FROM po_hdr WHERE po_no=?", po_no)
    run.end(grns=grns, po_status_after=po["status"], on_hand_after=stock["on_hand"] if stock else None)


def traps():
    """Each trap, on its own fresh Rasoi, with the exact status-bar text."""
    out = {}
    run = Run("traps")
    k = run.desk("Kavita", "KJOSHI", "kavita@123")
    s = k.open("PUR-PO-01").type(po_type="DIR", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L").press("Fetch")
    s.type(qty="20000", cc_cd="PRD-07", need_dt=NEED, tax_cd="GST18-INTER").press("Save")
    out["direct_po_cap"] = {"what": "Direct order (no request) for 20,000 gaskets", "status_bar": s.status}
    s = k.open("PUR-PO-01").type(pr_no="", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", qty="100", rate="11.90",
                                 tax_cd="GST18-INTER", cc_cd="PRD-07", need_dt=NEED)
    s.press("Save")
    out["save_without_fetch"] = {"what": "Order entry, Save without Fetch", "status_bar": s.status}
    for q in ("Deccan", "Shakti"):
        env = run.http.post("/svc/sup_search", json={"q": q}, headers=k._h("PUR-PO-01", "F2")).json()
        out[f"supplier_lookup_{q.lower()}"] = {"what": f"F2 supplier lookup '{q}'", "rc": env["rc"], "msg": env.get("msg"),
                                               "rows": (env.get("data") or {}).get("rows", [])}
    cc = run.http.post("/svc/cc_list", json={}, headers=k._h("PUR-PR-01", "F2")).json()
    out["cost_centres"] = (cc.get("data") or {}).get("rows", [])
    items = run.http.post("/svc/itm_search", json={"q": "gasket"}, headers=k._h("INV-ITM-03", "Search")).json()
    out["gasket_items"] = (items.get("data") or {}).get("rows", [])
    return out


res = {"what": "The Before, measured: the five missions through Bahi's legacy screens, two ways, plus each trap",
       "minutes_note": "ESTIMATE (keystroke-level model), hands-on time only; excludes waiting for Rohit and calling IT",
       "amend_screen_from": str(AMEND.relative_to(pathlib.Path(bahi.__file__).parent)) if AMEND.exists() else None}
for name, careful in (("first_time", False), ("careful", True)):
    run = Run(name)
    play(run, careful)
    res[name] = run.result()
res["traps"] = traps()
(OUT / "before_measure.json").write_text(json.dumps(res, indent=1, default=str, ensure_ascii=False))
for name in ("first_time", "careful"):
    print(name, res[name]["totals"], "≈", res[name]["klm_minutes"], "min", res[name]["distinct_screens"])
print(json.dumps({k: v for k, v in res["traps"].items() if k not in ("cost_centres", "gasket_items")}, indent=1, default=str)[:3000])
