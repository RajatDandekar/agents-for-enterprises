"""The five Before missions in the legacy Ledgerline client, and how we know each one is done.

Completion is read from the player's own Northbridge (the ERP's tables and its log of service calls), never from what the
page claims. The page sends its counters (clicks, keystrokes, screens opened, errors seen, sign-ins); the server
keeps the clock.
"""
from __future__ import annotations

import time

ITEM, QTY, SUP = "BAT-500", 2000, "VC-EIN-0042"

MISSIONS = [
    {"id": "M1", "who": "ECLARKE", "person": "Emma", "title": "Check the stock",
     "story": "Emma needs battery packs for the spring-launch run. First: how many city e-bike battery packs are in Manchester stores, "
              "and how many days will they last?",
     "login": ["ECLARKE", "emma@123"],
     "steps": ["Sign in: USER ID ECLARKE, PASSWORD emma@123. ORG UNIT NBC-MAN-01 is already filled.",
               "In the menu on the left, open Inventory › Stock status.",
               "ITEM CD is the battery pack's code. Don't know it? Click F2 next to the field and search for battery pack.",
               "Keep WHS CD as WH-MAN-STR and press Query. Read ON HAND and COVER (DAYS)."],
     "done_text": "5,400 on hand, using 600 a day: 9 days of cover. Not enough for the spring launch."},
    {"id": "M2", "who": "ECLARKE", "person": "Emma", "title": "Raise the purchase request",
     "story": "Ask for 2,000 battery packs, needed by 09-11-2026. Ledgerline will estimate about £273,600, above Emma's "
              "£250,000 limit, so the request has to go to Daniel.",
     "login": ["ECLARKE", "emma@123"],
     "steps": ["Open Purchase › Request entry.",
               "Type ITEM CD BAT-500 and press Fetch. It fills the unit, warehouse, Emma's cost centre and the last price.",
               "Type QTY 2000 and NEED DT 09-11-2026.",
               "Press Save (you get a PR number, in Draft), then Submit to send it for approval."],
     "done_text": "The request is waiting for Daniel. Nothing is ordered yet."},
    {"id": "M3", "who": "DOKAFOR", "person": "Daniel", "title": "Approve it as Daniel",
     "story": "Daniel Okafor, purchase manager, has to approve the request. Sign in as him.",
     "login": ["DOKAFOR", "daniel@123"],
     "steps": ["File › Sign out. Sign in: USER ID DOKAFOR, PASSWORD daniel@123.",
               "Open Purchase › Request approval and press Inbox.",
               "Double-click Emma's request in the inbox (or type its PR NO) and press Fetch.",
               "Type DECISION A (approve) and press Confirm."],
     "done_text": "Approved by Daniel. Emma can now make the order."},
    {"id": "M4", "who": "ECLARKE", "person": "Emma", "title": "Make the order and release it",
     "story": "Back as Emma: turn the approved request into a purchase order with Voltway Cells, Eindhoven "
              "(VC-EIN-0042), at the contract rate of £119.00, and release it to Voltway.",
     "login": ["ECLARKE", "emma@123"],
     "steps": ["File › Sign out. Sign in as ECLARKE again.",
               "Open Purchase › Order entry. Type PR NO, SUP CD VC-EIN-0042 and ITEM CD BAT-500, then press Fetch.",
               "Press Save and read the status bar. Note the PO number.",
               "Open Purchase › Order release. Type the PO NO, press Fetch, then Release."],
     "done_text": "Released: Voltway has the order, and 2,000 battery packs show as on order."},
    {"id": "M5", "who": "ATANAKA", "person": "Aiko", "title": "Receive the goods as Aiko",
     "story": "Voltway's truck brought 1,200 battery packs this morning (delivery note DN-4471) and the other 800 at 4 pm "
              "(delivery note DN-4486). Aiko Tanaka at stores records both.",
     "login": ["ATANAKA", "aiko@123"],
     "steps": ["File › Sign out. Sign in: USER ID ATANAKA, PASSWORD aiko@123.",
               "Open Inventory › Goods receipt. Type the PO NO and press Fetch.",
               "Type QTY RECD 1200 and DELIVERY NOTE NO DN-4471, then press Save.",
               "Now the second delivery: QTY RECD 800, DELIVERY NOTE NO DN-4486, Save."],
     "done_text": "Both deliveries received. The order is closed and stock is up by 2,000."},
]
BY_ID = {m["id"]: m for m in MISSIONS}

# What a Ledgerline error code means, in words. Ledgerline itself only shows the code.
HINTS = {
    "ERR-SEC-0002": "Wrong user ID or password. They are on the mission card.",
    "ERR-SEC-0007": "ORG UNIT must be NBC-MAN-01 (the Manchester plant).",
    "ERR-SEC-0001": "Access denied: this person's role cannot open that screen or run that service. Check who you are signed in as.",
    "ERR-SEC-0010": "The session expired. Sign in again.",
    "ERR-STK-0001": "No stock row for that item in that warehouse. Check ITEM CD (BAT-500) and WHS CD (WH-MAN-STR).",
    "ERR-ITM-0010": "No item with that code. Click F2 next to ITEM CD and search.",
    "ERR-ITM-0011": "That item is inactive, or the code is wrong. -R codes are rework stock. The city e-bike battery pack is BAT-500.",
    "ERR-SYS-0421": "A mandatory field is empty. The fields marked * must be filled.",
    "ERR-SYS-0422": "A field has a value Ledgerline cannot read. Numbers without commas; dates as DD-MM-YYYY.",
    "ERR-PR-0105": "NEED DT is in the past. Ledgerline's date is 26-10-2026; use 09-11-2026.",
    "ERR-PR-0007": "That request was already submitted.",
    "ERR-PR-0008": "That request is not waiting for approval (already approved or rejected).",
    "ERR-APR-0003": "Nobody may approve their own request. Sign in as Daniel (DOKAFOR).",
    "ERR-APR-0004": "The value is above this person's approval limit.",
    "ERR-SCR-0221": "Ledgerline wants Fetch before Save, for the same supplier and item. Press Fetch, then Save.",
    "ERR-PO-0412": "Voltway Cells is in the Netherlands and Northbridge is in England. A purchase from overseas needs the reverse-charge VAT code, but "
                   "Fetch always fills VAT20-UK. Change TAX CD to VAT20-RC (F2 lists the codes) and press Save again.",
    "ERR-PO-0602": "A standard order needs the approved PR NO.",
    "ERR-PO-0603": "The request is not approved, or an order was already made from it (status CL). Check the PR number.",
    "ERR-PO-0604": "Item or quantity does not match the request.",
    "ERR-PO-0610": "A direct order (PO TYPE DIR) is limited to £50,000. Keep PO TYPE STD and give the PR NO.",
    "ERR-PO-0715": "Ledgerline said \"SAVED\", but look at STATUS: DR means Draft. Your request carried cost centre PRD-05, "
                   "which closed on 15 October, so Ledgerline quietly saved a Draft that never reaches Voltway, and told no one. "
                   "Fix it: open Purchase › Order amendment, type the PO NO, press Fetch, set CC CD to PRD-07 (the spring-launch "
                   "run), press Amend. Then release again.",
    "ERR-PO-0001": "No order with that number. The PO number is in the status bar after Save (PO/2026/...).",
    "ERR-GRN-0102": "That order is not released yet, so stores cannot receive against it.",
    "ERR-GRN-0105": "That order is already fully received.",
    "ERR-GRN-0204": "That is more than the order's balance. Receive 1,200 first, then 800.",
    "ERR-GRN-0201": "QTY RECD must be more than 0.",
    "ERR-CC-0009": "No cost centre with that code. F2 next to CC CD lists them.",
    "ERR-BUD-0207": "The cost centre's budget for the quarter would be exceeded.",
}
TRAPS = {"ERR-PO-0412": "Tax code default (VAT20-UK)", "W-CC-114": "Silent Draft (closed cost centre PRD-05)",
         "ERR-PO-0715": "Release refused: the order was a Draft", "ERR-SCR-0221": "Save without Fetch",
         "ERR-APR-0003": "Self-approval refused", "ERR-PO-0610": "Direct order above £50,000"}
COUNTERS = ("clicks", "keys", "screens", "errors", "signins")


def _pr(erp):
    """Emma's request for the battery packs (the newest one for 2,000)."""
    return erp.q1("SELECT h.* FROM pr_hdr h JOIN pr_line l ON l.pr_no=h.pr_no WHERE l.itm_cd=? AND l.qty=? "
                  "AND h.status<>'RJ' ORDER BY h.pr_no DESC", ITEM, QTY)


def _po(erp, pr_no=None):
    if pr_no:
        r = erp.q1("SELECT * FROM po_hdr WHERE pr_no=? AND status<>'CN' ORDER BY po_no DESC", pr_no)
        if r:
            return r
    return erp.q1("SELECT h.* FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no WHERE l.itm_cd=? AND l.qty=? "
                  "AND h.sup_cd=? AND h.po_no>='PO/2026/01182' AND h.status<>'CN' ORDER BY h.po_no DESC", ITEM, QTY, SUP)


def state_of(erp) -> dict:
    """Where the battery pack order is in the player's Northbridge, read from Ledgerline's tables."""
    with erp.lock:
        pr = _pr(erp)
        po = _po(erp, pr["pr_no"] if pr else None)
        grns = erp.q("SELECT h.grn_no, l.qty, h.received_by, h.received_on FROM grn_hdr h JOIN grn_line l ON "
                     "l.grn_no=h.grn_no WHERE h.po_no=? ORDER BY h.grn_no", po["po_no"]) if po else []
        stock = erp.q1("SELECT on_hand, on_order FROM stock WHERE itm_cd=? AND whs_cd='WH-MAN-STR'", ITEM)
    return {"pr": pr, "po": po, "grns": grns, "received": sum(g["qty"] for g in grns), "stock": stock}


def check(erp, mid: str, start_seq: int) -> tuple[bool, str | None]:
    """(done, nudge): is this mission done in the player's Northbridge, and if not, a nudge about where it stands."""
    st = state_of(erp)
    pr, po = st["pr"], st["po"]
    if mid == "M1":
        with erp.lock:
            ok = any(r.svc == "stk_query" and str(r.payload.get("itm_cd", "")).upper() == ITEM and r.rc != "E"
                     for r in erp.calls[start_seq:])
        return ok, None
    if mid == "M2":
        if pr and pr["status"] in ("PA", "AP", "CL"):
            return True, None
        if pr and pr["status"] == "DR":
            return False, f"{pr['pr_no']} is saved as a Draft. Press Submit to send it for approval."
        with erp.lock:
            other = erp.q1("SELECT h.pr_no, l.qty FROM pr_hdr h JOIN pr_line l ON l.pr_no=h.pr_no WHERE l.itm_cd=? "
                           "ORDER BY h.pr_no DESC", ITEM)
        if other:
            return False, f"{other['pr_no']} is for {other['qty']:,}. The spring-launch run needs a request for 2,000."
        return False, None
    if mid == "M3":
        if pr and pr["status"] in ("AP", "CL"):
            return True, None
        return False, None
    if mid == "M4":
        if po and po["status"] in ("RL", "CL"):
            return True, None
        if po and po["status"] == "DR":
            return False, f"{po['po_no']} exists. Is it really on its way to Voltway? Release it to find out."
        if po and po["status"] == "AP":
            return False, f"{po['po_no']} is approved but not released. Voltway has not seen it yet."
        return False, None
    if mid == "M5":
        if po and po["status"] == "CL":
            return True, None
        if st["received"]:
            return False, f"{st['received']:,} of 2,000 received so far."
        return False, None
    return False, None


def errors_since(erp, start_seq: int) -> list[str]:
    """Error and warning codes Ledgerline returned to the legacy client since the mission began."""
    with erp.lock:
        out = []
        for r in erp.calls[start_seq:]:
            if not r.screen:
                continue
            if r.rc == "E" and r.err_cd:
                out.append(r.err_cd)
            if r.svc == "po_save" and isinstance(r.data, dict) and r.data.get("status") == "DR":
                out.append("W-CC-114")
        return out


class Missions:
    """A player's mission progress, kept in player.data['before'] (persisted by the app)."""

    def __init__(self, data: dict):
        self.b = data.setdefault("before", {})
        self.b.setdefault("results", {})

    @property
    def current(self) -> str | None:
        for m in MISSIONS:
            if m["id"] not in self.b["results"]:
                return m["id"]
        return None

    def start(self, erp):
        cur = self.current
        if cur and self.b.get("active") != cur:
            self.b["active"] = cur
            self.b["started_at"] = time.time()
            self.b["start_seq"] = len(erp.calls)
            self.b["counters"] = {k: 0 for k in COUNTERS}
        self.b.setdefault("first_started", time.time())

    def update(self, erp, counters: dict | None, mission: str | None = None) -> dict:
        cur = self.b.get("active")
        if mission and mission != cur:
            counters = None  # counters the page counted for an earlier mission: never carry them over
        nudge, hints = None, []
        if cur and cur == self.current:
            c = self.b.setdefault("counters", {k: 0 for k in COUNTERS})
            for k in COUNTERS:
                if counters and isinstance(counters.get(k), (int, float)):
                    c[k] = max(int(c.get(k, 0)), int(counters[k]))
            seq = int(self.b.get("start_seq", 0))
            done, nudge = check(erp, cur, seq)
            codes = errors_since(erp, seq)
            hints = [{"code": k, "text": HINTS[k]} for k in dict.fromkeys(codes) if k in HINTS]
            if done:
                self.b["results"][cur] = {"seconds": round(time.time() - self.b.get("started_at", time.time()), 1),
                                          **{k: int(c.get(k, 0)) for k in COUNTERS},
                                          "ledgerline_errors": len([x for x in codes if x.startswith("ERR")]),
                                          "traps": [TRAPS[x] for x in dict.fromkeys(codes) if x in TRAPS]}
                self.b["active"] = None
                if self.current:
                    self.start(erp)
                else:
                    self.b["finished_at"] = time.time()
        return self.view(nudge, hints)

    def totals(self) -> dict | None:
        res = self.b["results"]
        if not res:
            return None
        t = {k: sum(r.get(k, 0) for r in res.values()) for k in ("seconds", *COUNTERS, "ledgerline_errors")}
        t["traps"] = sorted({x for r in res.values() for x in r.get("traps", [])})
        t["missions_done"] = len(res)
        return t

    def view(self, nudge=None, hints=None) -> dict:
        return {"missions": [{**m, "result": self.b["results"].get(m["id"])} for m in MISSIONS],
                "current": self.current, "active": self.b.get("active"), "started_at": self.b.get("started_at"),
                "counters": self.b.get("counters") or {k: 0 for k in COUNTERS}, "nudge": nudge, "hints": hints or [],
                "totals": self.totals(), "finished": self.current is None, "now": time.time()}
