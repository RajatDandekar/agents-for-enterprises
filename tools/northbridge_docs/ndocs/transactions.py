"""Transaction extracts for Jan-Oct 2026 (purchase requests, orders, receipts, invoices, stock ledger, sales).

The six seed orders (seed.PAST_POS) appear with their numbers, dates, rates and statuses unchanged. Order numbers run
PO/2026/00001 to PO/2026/01181 (the sandbox's next number is 01182), requests PR/2026/00001 to 04416 (next 04417),
receipts GRN/2026/28xxx to 30000 (the sandbox's next GRN is 30001). No BAT-500 order is released after
PO/2026/01120, so the request estimate in Lecture 1 (the last released rate, £114.00) stays true.
"""
from __future__ import annotations

import datetime as dt

from ledgerline.erp import seed as S

from .world import TODAY, d, rng

ANCHORS = [(1, "2026-01-05"), (1044, "2026-08-03"), (1120, "2026-09-12"), (1131, "2026-09-18"), (1152, "2026-10-03"),
           (1167, "2026-10-09"), (1179, "2026-10-23"), (1181, "2026-10-26")]
SEED_PO = {p[0]: p for p in S.PAST_POS}
# BAT-500 call-offs before the two seed orders: Voltway every month, Nordic Cell twice while its certificate was valid
BAT500_FORCE = {40: "VC-EIN-0042", 175: "VC-EIN-0042", 300: "VC-EIN-0042", 452: "VC-EIN-0042", 590: "NC-GDA-0063",
                611: "VC-EIN-0042", 760: "VC-EIN-0042", 805: "NC-GDA-0063", 902: "VC-EIN-0042"}
PURCHASERS = ["ECLARKE", "ECLARKE", "LMORENO", "KMENSAH", "HNAKAMURA", "ECLARKE", "KMENSAH"]


def _interp(k, anchors):
    for (k0, d0), (k1, d1) in zip(anchors, anchors[1:]):
        if k0 <= k <= k1:
            a, b = d(d0), d(d1)
            t = (k - k0) / max(1, k1 - k0)
            x = a + dt.timedelta(days=round((b - a).days * t))
            while x.weekday() >= 5 and x < b:
                x += dt.timedelta(days=1)
            return x.isoformat()
    return anchors[-1][1]


def _approver(w, creator, gross):
    u = w.user[creator]
    if gross <= u["appr_limit"]:
        return creator
    a = u["manager_id"]
    while a:
        if w.user[a]["appr_limit"] >= gross:
            return a
        a = w.user[a]["manager_id"]
    return None


def purchase_orders(w):
    r = rng("pos")
    pairs = {}
    for rc in w.rates:
        pairs.setdefault(rc["itm_cd"], []).append(rc)
    weighted = [i for i in w.items if i["itm_cd"] in pairs and i["active"]]
    out = []
    for k in range(1, 1182):
        po_no = f"PO/2026/{k:05d}"
        if po_no in SEED_PO:
            _, sup, itm, qty, rate, tax, cc, status, cr, rl = SEED_PO[po_no]
            basic = round(qty * rate, 2)
            taxv = round(basic * 0.20, 2)
            gross = round(basic + taxv, 2)
            out.append(dict(po_no=po_no, created_on=cr, ou_cd="NBC-MAN-01", sup_cd=sup, itm_cd=itm, qty=qty, uom_cd="NOS",
                            rate=rate, basic_value=basic, tax_cd=tax, tax_value=taxv, gross_value=gross, cc_cd=cc,
                            status=status, po_type="DIR" if gross <= 50000 else "STD", pr_no="",
                            pt_cd="N45" if sup.startswith("VC") else "N30", whs_cd="WH-MAN-STR", need_dt="",
                            created_by="ECLARKE", approved_by="DOKAFOR" if status == "RL" else "",
                            released_on=rl or "", seed=True))
            continue
        on = _interp(k, ANCHORS)
        force = BAT500_FORCE.get(k)
        for _ in range(200):
            it = w.item["BAT-500"] if force else r.choice(weighted)
            if it["itm_cd"] == "BAT-500" and on > "2026-09-11":
                continue
            opts = [rc for rc in pairs[it["itm_cd"]] if rc["valid_from"] <= on <= rc["valid_to"]
                    and w.sup[rc["sup_cd"]]["status"] == "ACTIVE"]
            if it["itm_cd"] == "BAT-500":
                opts = [o for o in opts if o["sup_cd"] == (force or "VC-EIN-0042")]
            if opts:
                break
        rc = r.choice(opts)
        sup = w.sup[rc["sup_cd"]]
        adi = max(it["avg_daily_issue"], 5)
        if force:
            adi = 60  # 1,800 packs a month, the usual Voltway call-off
        qty = max(1, int(round(adi * r.choice([10, 15, 20, 30, 45]) / (100 if adi > 50 else 1))) * (100 if adi > 50 else 1))
        if it["category"] == "MRO":
            qty = r.randint(1, 6)
        rate = rc["rate"]
        if r.random() < 0.04:
            rate = round(rate * r.uniform(1.01, 1.05), 2)  # rate above contract: needs a reason (Purchase Policy §7.2)
        basic = round(qty * rate, 2)
        tax_cd = "VAT20-UK" if sup["state"] == "GB" else "VAT20-RC"
        taxv = round(basic * 0.20, 2)
        gross = round(basic + taxv, 2)
        if it["category"] == "MRO" or it["itm_cd"].startswith(("CON", "PKG")):
            cc = "MNT-01" if it["category"] == "MRO" else "LOG-01"
        elif on < "2026-10-01":
            cc = r.choice(["PRD-05", "PRD-05", "PRD-03", "PRD-02", "PRD-04"])
        else:
            cc = r.choice(["PRD-07", "PRD-07", "PRD-03", "PRD-02", "PRD-04"])
        creator = r.choice(PURCHASERS)
        if creator == "HNAKAMURA":
            cc = "LDS-PRD-01" if it["category"] != "MRO" else "MNT-02"
        age = (d(TODAY) - d(on)).days
        if age > 60:
            status = r.choices(["CL", "RL", "CN", "RJ"], [80, 12, 5, 3])[0]
        elif age > 14:
            status = r.choices(["RL", "CL", "CN", "PA"], [70, 22, 5, 3])[0]
        else:
            status = r.choices(["RL", "AP", "PA", "DR"], [60, 12, 18, 10])[0]
        appr = _approver(w, creator, gross) if status not in ("DR", "PA") else ""
        po_type = "DIR" if gross <= 50000 and r.random() < 0.55 else "STD"
        rl = (d(on) + dt.timedelta(days=r.choice([0, 0, 1, 1, 2, 3]))).isoformat() if status in ("RL", "CL") else ""
        if rl > TODAY:
            rl = TODAY
        out.append(dict(po_no=po_no, created_on=on, ou_cd="NBC-LDS-01" if creator == "HNAKAMURA" else "NBC-MAN-01",
                        sup_cd=sup["sup_cd"], itm_cd=it["itm_cd"], qty=qty, uom_cd=it["uom_cd"], rate=rate,
                        basic_value=basic, tax_cd=tax_cd, tax_value=taxv, gross_value=gross, cc_cd=cc, status=status,
                        po_type=po_type, pr_no="", pt_cd=sup["pt_cd"],
                        whs_cd="WH-LDS-STR" if creator == "HNAKAMURA" else ("WH-MAN-MRO" if it["category"] == "MRO" else "WH-MAN-STR"),
                        need_dt=(d(on) + dt.timedelta(days=it["lead_days"])).isoformat(), created_by=creator,
                        approved_by=appr or "", released_on=rl, seed=False))
    return out


def purchase_requests(w, pos):
    """PRs: one closed (CL) request behind every STD order raised from 2026 requests, plus every other request."""
    r = rng("prs")
    reqs = []
    for po in pos:
        if po["po_type"] == "STD" and not po["seed"]:
            on = (d(po["created_on"]) - dt.timedelta(days=r.randint(1, 6))).isoformat()
            if on < "2026-01-02":
                on = "2026-01-02"
            reqs.append(dict(raised_on=on, itm_cd=po["itm_cd"], qty=po["qty"], cc_cd=po["cc_cd"], status="CL",
                             raised_by=po["created_by"], approved_by=_approver(w, po["created_by"], round(po["qty"] * po["rate"] * 1.2, 2)) or "DOKAFOR",
                             est_rate=po["rate"], pr_type="STD", whs_cd=po["whs_cd"], po=po))
    items = [i for i in w.items if i["active"] and i["category"] != "FINISHED"]
    requesters = [u["user_id"] for u in w.users if u["role_cd"] in ("PRD-SUP", "PRD-PLAN", "MNT-TECH", "STORES", "QA-INSP", "PUR-EXEC")]
    while len(reqs) < 4416:
        it = r.choice(items)
        on = (d("2026-01-02") + dt.timedelta(days=r.randint(0, (d(TODAY) - d("2026-01-02")).days))).isoformat()
        kind = r.choices(["TRF", "SRV", "STD", "MRO"], [55, 10, 25, 10])[0]
        age = (d(TODAY) - d(on)).days
        st = r.choices(["CL", "RJ", "CN", "AP", "PA", "DR"], [62, 9, 14, 6, 4, 5])[0] if age > 10 else \
            r.choices(["AP", "PA", "DR", "RJ"], [40, 30, 25, 5])[0]
        who = r.choice(requesters)
        reqs.append(dict(raised_on=on, itm_cd=it["itm_cd"], qty=max(1, it["avg_daily_issue"] * r.choice([1, 2, 5, 10]) or r.randint(1, 10)),
                         cc_cd=r.choice(["PRD-05" if on < "2026-10-15" else "PRD-07", "PRD-03", "MNT-01", "QA-01", "LOG-01", "PRD-02"]),
                         status=st, raised_by=who, approved_by=r.choice(["DOKAFOR", "LMORENO", "CSHAW", "SBERG"]) if st in ("CL", "AP") else "",
                         est_rate=it["std_cost"], pr_type=kind, whs_cd="WH-MAN-STR", po=None))
    reqs.sort(key=lambda x: (x["raised_on"], x["itm_cd"], x["qty"]))
    out = []
    for n, q in enumerate(reqs, 1):
        pr_no = f"PR/2026/{n:05d}"
        if q["po"]:
            q["po"]["pr_no"] = pr_no
        out.append(dict(pr_no=pr_no, raised_on=q["raised_on"], pr_type=q["pr_type"], itm_cd=q["itm_cd"], qty=q["qty"],
                        uom_cd=w.item[q["itm_cd"]]["uom_cd"], est_rate=q["est_rate"],
                        est_value=round(q["qty"] * (q["est_rate"] or 0) * 1.20, 2), cc_cd=q["cc_cd"], whs_cd=q["whs_cd"],
                        status=q["status"], raised_by=q["raised_by"], approved_by=q["approved_by"]))
    return out


def receipts(w, pos):
    r = rng("grns")
    rows = []
    for po in pos:
        if po["status"] not in ("RL", "CL") or not po["released_on"]:
            continue
        lead = w.item[po["itm_cd"]]["lead_days"]
        parts = 1 if po["qty"] < 50 else r.choice([1, 1, 2, 3])
        if po["status"] == "RL":
            parts_done = r.choice([0, 0, 1]) if parts > 1 else 0
        else:
            parts_done = parts
        left = po["qty"]
        for p in range(parts_done):
            q = left if p == parts - 1 else int(po["qty"] / parts)
            left -= q
            on = (d(po["released_on"]) + dt.timedelta(days=int(lead * r.uniform(0.6, 1.2)) + 7 * p)).isoformat()
            if on >= TODAY:
                break
            rows.append(dict(received_on=on, po_no=po["po_no"], itm_cd=po["itm_cd"], qty=q, whs_cd=po["whs_cd"],
                             received_by=r.choice(["ATANAKA", "ATANAKA", "CSHAW"]) if po["whs_cd"] != "WH-LDS-STR" else "NDOYLE",
                             sup_cd=po["sup_cd"], dn=f"{po['sup_cd'][:2]}/DN/{r.randint(10000, 99999)}",
                             rate=po["rate"], tax_cd=po["tax_cd"], pt_cd=po["pt_cd"]))
    rows.sort(key=lambda x: (x["received_on"], x["po_no"]))
    start = 30001 - len(rows)
    for n, g in enumerate(rows):
        g["grn_no"] = f"GRN/2026/{start + n:05d}"
    return rows


def invoices(w, grns):
    r = rng("invoices")
    out = []
    terms = {p["pt_cd"]: p["days"] for p in w.pts}
    for n, g in enumerate(grns, 1):
        on = (d(g["received_on"]) + dt.timedelta(days=r.randint(0, 6))).isoformat()
        if on > TODAY:
            continue
        rate = g["rate"]
        status = "MATCHED"
        if r.random() < 0.05:
            rate = round(rate * r.uniform(1.02, 1.08), 2)
            status = "HOLD-PRC"
        elif r.random() < 0.03:
            status = "HOLD-QTY"
        basic = round(g["qty"] * rate, 2)
        tax = round(basic * 0.20, 2) if g["tax_cd"] == "VAT20-UK" else 0.0  # reverse charge: the supplier charges no VAT
        due = (d(on) + dt.timedelta(days=terms.get(g["pt_cd"], 30))).isoformat()
        paid = ""
        if status == "MATCHED" and due <= TODAY:
            pd_ = d(due)
            while pd_.weekday() not in (1, 3):  # payment runs on Tuesdays and Thursdays (SOP-AP-003)
                pd_ += dt.timedelta(days=1)
            paid = pd_.isoformat() if pd_.isoformat() <= TODAY else ""
        out.append(dict(ap_doc=f"AP/2026/{n:05d}", sup_inv_no=f"{g['sup_cd'][:2]}-INV-{r.randint(100000, 999999)}",
                        inv_dt=on, sup_cd=g["sup_cd"], po_no=g["po_no"], grn_no=g["grn_no"], itm_cd=g["itm_cd"],
                        qty=g["qty"], rate=rate, basic=basic, tax_cd=g["tax_cd"], tax=tax, gross=round(basic + tax, 2),
                        match_status=status, due_dt=due, paid_on=paid,
                        pay_run=f"PR-{paid.replace('-', '')}" if paid else ""))
    return out


def stock_ledger_q3(w, grns):
    """Every receipt and issue for July-September 2026 in the two main stores, with a running balance."""
    r = rng("stkled")
    movers = [i for i in w.items if i["active"] and i["avg_daily_issue"] >= 80 and i["category"] in ("RAW", "COMPONENTS", "SPARES", "PACKING")]
    movers = sorted(movers, key=lambda i: i["itm_cd"])[:140]
    onhand = {(s["itm_cd"], s["whs_cd"]): s["on_hand"] for s in w.stock}
    out = []
    days = [d("2026-07-01") + dt.timedelta(days=k) for k in range(92)]
    g_by = {}
    for g in grns:
        if "2026-07-01" <= g["received_on"] <= "2026-09-30":
            g_by.setdefault((g["itm_cd"], g["whs_cd"]), []).append(g)
    for it in movers:
        whs = "WH-MAN-STR"
        txns = []
        for day in days:
            if day.weekday() >= 5:
                continue
            for _ in range(r.choice([1, 1, 2])):
                q = -int(it["avg_daily_issue"] * r.uniform(0.3, 0.8))
                txns.append((day.isoformat(), "ISS", q, f"WO/2026/{r.randint(3000, 7999):05d}"))
        for g in g_by.get((it["itm_cd"], whs), []):
            txns.append((g["received_on"], "GRN", g["qty"], g["grn_no"]))
        txns.sort()
        net = sum(t[2] for t in txns)
        target = onhand.get((it["itm_cd"], whs), it["reorder_lvl"])
        bal = target - net
        if bal < 0:  # top up with a receipt on the first day so the balance never goes negative
            txns.insert(0, ("2026-07-01", "ADJ", -bal + it["reorder_lvl"], "STK-ADJ/2026/0412"))
            bal = target - sum(t[2] for t in txns)
        out.append(dict(dt="2026-07-01", itm_cd=it["itm_cd"], whs_cd=whs, txn="OPENING", qty=bal, ref="Q3 OPENING", balance=bal))
        for day, txn, q, ref in txns:
            bal += q
            out.append(dict(dt=day, itm_cd=it["itm_cd"], whs_cd=whs, txn=txn, qty=q, ref=ref, balance=bal))
    return out


def sales_orders(w):
    r = rng("sales")
    fg = [i for i in w.items if i["category"] == "FINISHED"]
    out = []
    n = 0
    day = d("2026-01-05")
    while day.isoformat() <= TODAY:
        if day.weekday() < 5:
            for _ in range(r.randint(14, 26)):
                n += 1
                c = r.choice(w.customers)
                it = r.choice(fg)
                price = round(it["std_cost"] * r.uniform(1.45, 1.75), 2)
                age = (d(TODAY) - day).days
                st = r.choices(["INVOICED", "SHIPPED", "CANCELLED"], [85, 10, 5])[0] if age > 20 else \
                    r.choices(["OPEN", "ALLOCATED", "SHIPPED"], [40, 30, 30])[0]
                out.append(dict(so_no=f"SO/2026/{n:06d}", order_dt=day.isoformat(), cust_cd=c["cust_cd"], cust_name=c["name"],
                                country=c["country"], itm_cd=it["itm_cd"], qty=r.choice([1, 1, 2, 2, 3, 4, 6, 10]),
                                unit_price=price, price_list=c["price_list"], status=st, rep=c["rep"]))
        day += dt.timedelta(days=1)
    return out


def boms(w):
    r = rng("bom")
    comp = {}
    for i in w.items:
        if i["active"] and i["category"] in ("RAW", "COMPONENTS", "SPARES", "PACKING"):
            comp.setdefault(i["itm_cd"].split("-")[0], []).append(i["itm_cd"])
    out = []
    recipe = [("FRM", 1), ("BAT", 1), ("MTR", 1), ("CHG", 1), ("CTL", 1), ("DSP", 1), ("TYR", 2), ("TUB", 2), ("RIM", 2),
              ("SPK", 72), ("BRK", 2), ("CHN", 1), ("CST", 1), ("DRL", 1), ("SHF", 1), ("HBR", 1), ("STM", 1), ("GRP", 1),
              ("SDL", 1), ("SPT", 1), ("BEL", 1), ("LGT", 2), ("ACC", 3), ("CBL", 4), ("FST", 38), ("MNT", 1), ("BOX", 1),
              ("PKG", 3)]
    for i in w.items:
        if i["category"] != "FINISHED":
            continue
        line = 0
        for pre, q in recipe:
            if pre not in comp:
                continue
            if pre == "FRM":
                code = i["itm_cd"].replace("FG-", "FRM-")
                if code not in w.item:
                    continue
            elif pre == "BAT":
                code = "BAT-500" if "ANC" in i["itm_cd"] or "SPR" in i["itm_cd"] else r.choice(["BAT-375", "BAT-625", "BAT-750"])
            elif pre == "MTR":
                code = "MTR-HUB-250"
            elif pre == "CHG":
                code = "CHG-4A-01"
            else:
                code = r.choice(comp[pre])
            reps = 1 if pre not in ("FST", "ACC", "CBL", "PKG") else min(q, 4)
            for _ in range(reps):
                line += 10
                out.append(dict(parent=i["itm_cd"], line=line, component=code if reps == 1 else r.choice(comp[pre]),
                                qty=q if reps == 1 else r.randint(1, 8), uom=w.item[code]["uom_cd"], scrap_pct=r.choice([0, 0, 0.5, 1, 2])))
    return out


class Transactions:
    def __init__(self, w):
        self.pos = purchase_orders(w)
        self.prs = purchase_requests(w, self.pos)
        self.grns = receipts(w, self.pos)
        self.invoices = invoices(w, self.grns)
        self.ledger = stock_ledger_q3(w, self.grns)
        self.sales = sales_orders(w)
        self.boms = boms(w)
