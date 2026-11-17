"""The week's data for Lecture 5 (installed by install_payables, only in sandboxes that ask for it).

What the background agents and the invoice batch find on Monday 26 October 2026:
  - 40 supplier invoices in the AP inbox, as e-mails (three layouts), each billing a seeded order and goods receipt:
      31 match cleanly · 1 is 1.2% over the order price (inside the 2% tolerance) · 3 are over the price
      (+3.5%, +6.0%, +8.1%) · 2 bill more than was received · 1 is a resent duplicate · 1 names an order that does not
      exist · 1 bills an order whose goods have not arrived yet (Halden Cells, PO due 30 Oct)
  - 8 open orders that are late against their need-by date (3 to 17 days), two of them also billed above
  - UN 38.3 certificates: Halden Cells expires 20 Nov (25 days), Kestrel Power 4 Dec (39 days), Nordic Cell expired
  - items below their reorder level: BEL-STD-01 (bells) and BAT-375 (375 Wh packs)
  - Laura Hughes (LHUGHES), purchase manager, who covers Daniel's approvals while he is away
Every number is generated here, deterministically, and is consistent with the seeded orders and receipts.
"""
from __future__ import annotations

import datetime as dt

D = dt.date.fromisoformat

# Two suppliers that exist only in this sandbox (their certificates expire soon).
SUPPLIERS = [("KP-SHF-0071", "Kestrel Power Systems", "GB466120985", "GB", "Sheffield", "ACTIVE", "N30"),
             ("HC-BRS-0072", "Halden Cells", "GB508331742", "GB", "Bristol", "ACTIVE", "N30")]
CERTS = [("KP-SHF-0071", "UN38.3", "UN38.3-TR/KP/2025/207", "2026-12-04", "LMORENO", "2025-12-05"),
         ("HC-BRS-0072", "UN38.3", "UN38.3-TR/HC/2025/164", "2026-11-20", "LMORENO", "2025-11-21")]
RATES = [("KP-SHF-0071", "BAT-750", 141.00, "2026-04-01", "2027-03-31"),
         ("HC-BRS-0072", "BAT-375", 89.50, "2026-04-01", "2027-03-31")]
USERS = [("LHUGHES", "Laura Hughes", "PUR-MGR", "NBC-MAN-01", 1000000, "HWEBER", "laura@123", "PRD-07",
          "laura.hughes@northbridgecycles.example", "@laura")]

NAMES = {"VC-EIN-0042": "Voltway Cells", "PB-MAN-0017": "Pennine Brakes", "CC-SAL-0031": "Castlefield Chargers",
         "AM-BIR-0008": "Albion Motors", "IP-MAN-0055": "Irwell Packaging", "KP-SHF-0071": "Kestrel Power Systems",
         "HC-BRS-0072": "Halden Cells", "NC-GDA-0063": "Nordic Cell Co."}
MAIL = {"VC-EIN-0042": "accounts@voltwaycells.example", "PB-MAN-0017": "invoices@penninebrakes.example",
        "CC-SAL-0031": "ar@castlefieldchargers.example", "AM-BIR-0008": "finance@albionmotors.example",
        "IP-MAN-0055": "billing@irwellpackaging.example", "KP-SHF-0071": "accounts@kestrelpower.example",
        "HC-BRS-0072": "invoices@haldencells.example"}
DESC = {"BAT-500": "Battery pack, 36 V 500 Wh", "BAT-375": "Battery pack, 36 V 375 Wh", "BAT-750": "Battery pack, 48 V 750 Wh",
        "MNT-FRM-01": "Battery mount, down-tube, long", "MNT-RCK-02": "Battery mount, rear rack, short",
        "BEL-STD-01": "Bell, standard", "BRK-PAD-01": "Brake pads, disc (pair)", "MTR-HUB-250": "Hub motor, 250 W",
        "CHG-4A-01": "Charger, 4 A", "BOX-BIKE-01": "Carton, bike shipping"}
INV_PREFIX = {"VC-EIN-0042": "VC-INV-2026-", "PB-MAN-0017": "PB/26/", "CC-SAL-0031": "CCH-INV-", "AM-BIR-0008": "AM-",
              "IP-MAN-0055": "IRW-26-", "KP-SHF-0071": "KPS-INV-", "HC-BRS-0072": "HC2026-"}

# kind: what the three-way match should find. (sup, item, ordered, rate, received [deliveries], billed, billed_rate, kind)
INVOICED = [
    ("VC-EIN-0042", "BAT-500", 600, 119.00, [600], 600, None, "clean"),
    ("VC-EIN-0042", "MNT-FRM-01", 8000, 18.50, [8000], 8000, None, "clean"),
    ("VC-EIN-0042", "MNT-RCK-02", 6000, 15.75, [6000], 6000, None, "clean"),
    ("VC-EIN-0042", "BAT-375", 500, 92.00, [500], 500, None, "clean"),
    ("VC-EIN-0042", "BAT-750", 200, 146.00, [200], 200, None, "clean"),
    ("PB-MAN-0017", "BEL-STD-01", 6000, 6.80, [6000], 6000, None, "clean"),
    ("PB-MAN-0017", "BRK-PAD-01", 5000, 9.40, [5000], 5000, None, "clean"),
    ("PB-MAN-0017", "BRK-PAD-01", 4000, 9.40, [4000], 4000, None, "clean"),
    ("CC-SAL-0031", "CHG-4A-01", 1500, 96.00, [1500], 1500, None, "clean"),       # resent later as a duplicate
    ("CC-SAL-0031", "CHG-4A-01", 1200, 96.00, [1200], 1200, None, "clean"),
    ("AM-BIR-0008", "MTR-HUB-250", 2000, 142.00, [2000], 2000, None, "clean"),
    ("AM-BIR-0008", "MTR-HUB-250", 1500, 142.00, [1500], 1500, None, "clean"),
    ("IP-MAN-0055", "BOX-BIKE-01", 8000, 21.50, [8000], 8000, None, "clean"),
    ("IP-MAN-0055", "BOX-BIKE-01", 6000, 21.50, [6000], 6000, None, "clean"),
    ("KP-SHF-0071", "BAT-750", 150, 141.00, [150], 150, None, "clean"),
    ("VC-EIN-0042", "BAT-500", 1500, 119.00, [900], 900, None, "clean"),          # part delivery, part billed
    ("PB-MAN-0017", "BEL-STD-01", 4000, 6.80, [4000], 4000, None, "clean"),
    ("AM-BIR-0008", "MTR-HUB-250", 1000, 142.00, [1000], 1000, None, "clean"),
    ("IP-MAN-0055", "BOX-BIKE-01", 5000, 21.50, [5000], 5000, None, "clean"),
    ("CC-SAL-0031", "CHG-4A-01", 800, 96.00, [800], 800, None, "clean"),
    ("VC-EIN-0042", "MNT-FRM-01", 5000, 18.50, [5000], 5000, None, "clean"),
    ("PB-MAN-0017", "BRK-PAD-01", 3000, 9.40, [3000], 3000, None, "clean"),
    ("HC-BRS-0072", "BAT-375", 300, 89.50, [300], 300, None, "clean"),
    ("VC-EIN-0042", "BAT-375", 400, 92.00, [400], 400, None, "clean"),
    ("AM-BIR-0008", "MTR-HUB-250", 2500, 142.00, [1200, 1300], [1200, 1300], None, "clean"),   # two deliveries, two invoices
    ("IP-MAN-0055", "BOX-BIKE-01", 7000, 21.50, [7000], 7000, None, "clean"),
    ("VC-EIN-0042", "MNT-RCK-02", 4000, 15.75, [4000], 4000, None, "clean"),
    ("PB-MAN-0017", "BEL-STD-01", 3000, 6.80, [3000], 3000, None, "clean"),
    ("CC-SAL-0031", "CHG-4A-01", 1000, 96.00, [1000], 1000, None, "clean"),
    ("KP-SHF-0071", "BAT-750", 100, 141.00, [100], 100, None, "clean"),
    ("AM-BIR-0008", "MTR-HUB-250", 1800, 142.00, [1800], 1800, 143.70, "within_tolerance"),   # +1.2%
    ("VC-EIN-0042", "MNT-FRM-01", 6000, 18.50, [6000], 6000, 19.15, "price_variance"),       # +3.5%
    ("PB-MAN-0017", "BRK-PAD-01", 4500, 9.40, [4500], 4500, 9.96, "price_variance"),         # +6.0%
    ("IP-MAN-0055", "BOX-BIKE-01", 6000, 21.50, [6000], 6000, 23.24, "price_variance"),      # +8.1%
    ("PB-MAN-0017", "BEL-STD-01", 5000, 6.80, [4500], 5000, None, "quantity_variance"),      # billed 500 not received
    ("VC-EIN-0042", "BAT-500", 2000, 119.00, [1800], 2000, None, "quantity_variance"),       # billed 200 not received
    ("HC-BRS-0072", "BAT-375", 1000, 89.50, [], 1000, None, "no_receipt"),                   # goods due 30 Oct
]
# Last week's invoices, already recorded by Luis (RECEIVED, not matched yet): the weekly three-way match agent's work.
# (sup, item, ordered, rate, received, billed, billed_rate, kind, need_by)
RECORDED = [
    ("PB-MAN-0017", "BRK-PAD-01", 2000, 9.40, 2000, 2000, None, "clean", None),
    ("IP-MAN-0055", "BOX-BIKE-01", 3000, 21.50, 3000, 3000, None, "clean", None),
    ("AM-BIR-0008", "MTR-HUB-250", 800, 142.00, 800, 800, None, "clean", None),
    ("CC-SAL-0031", "CHG-4A-01", 600, 96.00, 600, 600, None, "clean", None),
    ("VC-EIN-0042", "MNT-FRM-01", 3000, 18.50, 3000, 3000, None, "clean", None),
    ("VC-EIN-0042", "BAT-750", 120, 146.00, 120, 120, 151.10, "price_variance", None),        # +3.5%
    ("PB-MAN-0017", "BEL-STD-01", 2500, 6.80, 2000, 2500, None, "quantity_variance", "2026-10-22"),
    ("KP-SHF-0071", "BAT-750", 80, 141.00, 0, 80, None, "no_receipt", "2026-11-03"),           # goods due 3 Nov
]
NO_PO = ("IP-MAN-0055", "BOX-BIKE-01", 1200, 21.50, "PO/2026/01999")   # an order number that does not exist
DUP_OF = 8                                                             # index in INVOICED of the resent invoice

# Late orders that have not been billed: (sup, item, qty, rate, need_by, received, buyer)
LATE = [
    ("AM-BIR-0008", "MTR-HUB-250", 3000, 142.00, "2026-10-09", 0, "ECLARKE"),     # 17 days late
    ("CC-SAL-0031", "CHG-4A-01", 2500, 96.00, "2026-10-14", 1000, "LMORENO"),     # 12 days, part received
    ("IP-MAN-0055", "BOX-BIKE-01", 10000, 21.50, "2026-10-16", 0, "ECLARKE"),     # 10 days
    ("PB-MAN-0017", "BRK-PAD-01", 8000, 9.40, "2026-10-19", 0, "ECLARKE"),        # 7 days exactly
    ("VC-EIN-0042", "MNT-RCK-02", 12000, 15.75, "2026-10-21", 0, "ECLARKE"),      # 5 days
    ("KP-SHF-0071", "BAT-750", 400, 141.00, "2026-10-23", 0, "LMORENO"),          # 3 days
]
# need-by dates for invoiced orders that are not complete (the rest are complete, so never late)
OPEN_NEED = {15: "2026-11-06", 34: "2026-10-15", 35: "2026-10-20", 36: "2026-10-30"}

EXISTING = {1044, 1120, 1131, 1152, 1167, 1179}


def _po_numbers():
    n = 1100
    while True:
        if n not in EXISTING:
            yield f"PO/2026/{n:05d}"
        n += 1
        if n >= 1179:
            raise RuntimeError("ran out of seed order numbers")


def _vat(sup: str, net: float) -> float:
    return 0.0 if sup.startswith(("VC-", "NC-")) else round(net * 0.20, 2)


def _tax_cd(sup: str) -> str:
    return "VAT20-RC" if sup.startswith(("VC-", "NC-")) else "VAT20-UK"


def _money(v: float) -> str:
    return f"£{v:,.2f}"


def invoice_text(layout: int, sup: str, inv_no: str, inv_dt: str, po_no: str, item: str, qty: int, rate: float) -> tuple[str, str, str]:
    """(subject, body, attachment name) of one invoice e-mail, in one of three layouts suppliers really use."""
    name, net = NAMES[sup], round(qty * rate, 2)
    vat = _vat(sup, net)
    gross = round(net + vat, 2)
    d = D(inv_dt).strftime("%d %b %Y")
    vat_line = ("VAT: reverse charge (Art. 196 Directive 2006/112/EC), customer to account for VAT" if vat == 0
                else f"VAT 20%: {_money(vat)}")
    if layout == 0:   # a plain e-mail with the invoice in the body
        subject = f"Invoice {inv_no} from {name}"
        body = (f"Dear Northbridge accounts team,\n\nPlease find our invoice {inv_no} dated {d} for your order {po_no}.\n\n"
                f"  {qty:,} x {item} {DESC[item]} at {_money(rate)} each\n  Net: {_money(net)}\n  {vat_line}\n"
                f"  Total due: {_money(gross)}\n\nPayment terms as agreed. Kind regards,\n{name} accounts")
        return subject, body, ""
    if layout == 1:   # a PDF attachment, shown as the text the mail system extracted from it
        subject = f"{name}: invoice attached"
        body = (f"Hello, our invoice is attached. Thank you for your business.\n\n--- attachment: {inv_no.replace('/', '-')}.pdf"
                f" (text) ---\nINVOICE\n{name.upper()}\nInvoice no.  {inv_no}\nInvoice date {d}\nBill to      Northbridge "
                f"Cycles Ltd, Manchester\nYour ref     {po_no}\n\nItem         Description                       Qty        "
                f"Unit price      Amount\n{item:<12} {DESC[item]:<33} {qty:>8,}   {_money(rate):>12}   {_money(net):>12}\n\n"
                f"Subtotal {_money(net)}\n{vat_line}\nTOTAL {_money(gross)}\n--- end of attachment ---")
        return subject, body, f"{inv_no.replace('/', '-')}.pdf"
    # layout 2: a forwarded e-mail, terse, the way a sales rep sends it
    subject = f"FW: {po_no} - inv {inv_no}"
    body = (f"Forwarding for processing.\n\n> From: {MAIL[sup]}\n> Re: order {po_no}\n> Inv {inv_no}, {d}. Goods: {item}, "
            f"qty {qty:,} @ {rate:.2f}. Net {net:,.2f}. {'No VAT (reverse charge).' if vat == 0 else f'VAT {vat:,.2f}.'} "
            f"Gross {gross:,.2f} GBP.\n> Thanks, {name}")
    return subject, body, ""


def seed_week(erp) -> dict:
    """Insert the week's orders, receipts, invoices (as AP-inbox e-mails), late orders, certificates and stock."""
    x = erp.x
    for s in SUPPLIERS:
        x("INSERT INTO supplier VALUES (?,?,?,?,?,?,?,'LMORENO','2025-11-03')", *s)
    for c in CERTS:
        x("INSERT INTO sup_cert VALUES (?,?,?,?,?,?)", *c)
    for r in RATES:
        x("INSERT INTO sup_rate VALUES (?,?,?,?,?)", *r)
    for u in USERS:
        x("INSERT INTO app_user VALUES (?,?,?,?,?,?,?,?,?,?)", *u)
    nos = _po_numbers()
    grn_n = [28001]
    # The base orders released in Aug-Oct arrived in full (their receipts were never keyed in the plain sandbox).
    # Their status stays RELEASED, as in every other lecture, so purchase history and estimated rates do not change.
    for h in erp.q("SELECT h.po_no, h.released_on, l.itm_cd, l.qty FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no "
                   "WHERE h.status='RL' ORDER BY h.po_no"):
        g = f"GRN/2026/{grn_n[0]:05d}"
        grn_n[0] += 1
        day = (D(h["released_on"]) + dt.timedelta(days=6)).isoformat()
        x("INSERT INTO grn_hdr VALUES (?,?,?,?,?,?)", g, h["po_no"], "WH-MAN-STR", "ATANAKA", day + "T10:30:00+00:00", "")
        x("INSERT INTO grn_line VALUES (?,?,?,?)", g, 1, h["itm_cd"], h["qty"])
    created = D("2026-08-24")
    mails, expect = [], []

    def add_po(sup, item, qty, rate, created_on, need, buyer, deliveries, status_open):
        po_no = next(nos)
        basic = round(qty * rate, 2)
        tax = _vat(sup, basic) if not sup.startswith("VC-") else round(basic * 0.20, 2)  # RC: VAT accounted, same rate
        rel = (D(created_on) + dt.timedelta(days=1)).isoformat()
        status = "CL" if sum(deliveries) >= qty else "RL"
        x("INSERT INTO po_hdr VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
          po_no, "NBC-MAN-01", sup, None, "STD", "PRD-07" if item.startswith(("BAT", "MNT", "MTR", "CHG")) else "PRD-03",
          _tax_cd(sup), "N45" if sup.startswith("VC") else "N30", need, "WH-MAN-STR", status, basic, tax, basic + tax,
          buyer, created_on, "DOKAFOR", rel, rel, None, None)
        x("INSERT INTO po_line VALUES (?,?,?,?,?,?)", po_no, 1, item, qty, "NOS", rate)
        day = D(rel)
        for q in deliveries:
            day = min(day + dt.timedelta(days=9), D("2026-10-23"))
            g = f"GRN/2026/{grn_n[0]:05d}"
            grn_n[0] += 1
            x("INSERT INTO grn_hdr VALUES (?,?,?,?,?,?)", g, po_no, "WH-MAN-STR", "ATANAKA", day.isoformat() + "T10:30:00+00:00", "")
            x("INSERT INTO grn_line VALUES (?,?,?,?)", g, 1, item, q)
            x("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES (?,?,?,?,?,?)", item, "WH-MAN-STR", day.isoformat(), "GRN", q, g)
        if status == "RL":
            x("UPDATE stock SET on_order=on_order+? WHERE itm_cd=? AND whs_cd='WH-MAN-STR'", qty - sum(deliveries), item)
        return po_no, day

    # 1. invoiced orders and their invoices
    k = 0
    for i, (sup, item, qty, rate, dels, billed, brate, kind) in enumerate(INVOICED):
        created = created + dt.timedelta(days=1 if i % 3 else 2)
        need = OPEN_NEED.get(i, (created + dt.timedelta(days=18)).isoformat())
        po_no, last = add_po(sup, item, qty, rate, created.isoformat(), need, "LMORENO" if i % 5 == 3 else "ECLARKE", dels,
                             None)
        bills = billed if isinstance(billed, list) else [billed]
        for j, bq in enumerate(bills):
            k += 1
            inv_dt = (max(last, D("2026-10-14")) + dt.timedelta(days=2 + (k % 3))).isoformat() if dels else "2026-10-23"
            inv_dt = min(inv_dt, "2026-10-25")
            sup_inv = f"{INV_PREFIX[sup]}{4100 + 37 * k}"
            subject, body, att = invoice_text(k % 3, sup, sup_inv, inv_dt, po_no, item, bq, brate or rate)
            recv = (D("2026-10-19") + dt.timedelta(days=(k * 7) // 40)).isoformat() + f"T{8 + k % 9:02d}:{(k * 13) % 60:02d}:00+00:00"
            mails.append((f"MSG-{k:04d}", recv, MAIL[sup], subject, body, att))
            expect.append({"msg_id": f"MSG-{k:04d}", "sup_cd": sup, "sup_inv_no": sup_inv, "po_no": po_no, "item": item,
                           "qty": bq, "rate": brate or rate, "expect": "matched" if kind in ("clean", "within_tolerance") else kind})
            if i == DUP_OF:
                dup = (subject, body, att, sup_inv, po_no, sup, item, bq, rate)
    # 2. an invoice for an order that does not exist
    k += 1
    sup, item, qty, rate, ref = NO_PO
    sup_inv = f"{INV_PREFIX[sup]}{4100 + 37 * k}"
    subject, body, att = invoice_text(0, sup, sup_inv, "2026-10-22", ref, item, qty, rate)
    mails.append((f"MSG-{k:04d}", "2026-10-23T11:20:00+00:00", MAIL[sup], subject, body, att))
    expect.append({"msg_id": f"MSG-{k:04d}", "sup_cd": sup, "sup_inv_no": sup_inv, "po_no": ref, "item": item, "qty": qty,
                   "rate": rate, "expect": "no_order"})
    # 3. the resent duplicate, last in the inbox
    k += 1
    subject, body, att, sup_inv, po_no, sup, item, bq, rate = dup
    mails.append((f"MSG-{k:04d}", "2026-10-26T08:41:00+00:00", MAIL[sup], "RESENT: " + subject,
                  "Resending in case this did not reach you.\n\n" + body, att))
    expect.append({"msg_id": f"MSG-{k:04d}", "sup_cd": sup, "sup_inv_no": sup_inv, "po_no": po_no, "item": item, "qty": bq,
                   "rate": rate, "expect": "duplicate"})
    for m in sorted(mails, key=lambda m: m[1]):
        x("INSERT INTO mail_msg VALUES (?,?,?,?,?,?,?,?,?)", m[0], "AP inbox", m[1], m[2], m[3], m[4], m[5], "invoice", "NEW")
    # 4. last week's recorded invoices (status RECEIVED) and their orders
    recorded = []
    for i, (sup, item, qty, rate, rec, billed, brate, kind, need) in enumerate(RECORDED):
        c = (D("2026-09-28") + dt.timedelta(days=2 * i)).isoformat()
        po_no, last = add_po(sup, item, qty, rate, c, need or (D(c) + dt.timedelta(days=16)).isoformat(), "ECLARKE",
                             [rec] if rec else [], None)
        inv_no = f"AP/2026/{69990 + i:05d}"
        r8 = brate or rate
        net = round(billed * r8, 2)
        vat = _vat(sup, net)
        x("INSERT INTO inv_hdr VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", inv_no, f"{INV_PREFIX[sup]}{3900 + 11 * i}", sup,
          po_no, "2026-10-21", net, vat, round(net + vat, 2), "RC", None, None, None, None, "LMORENO",
          f"2026-10-2{2 + i % 2}T15:{10 + i:02d}:00+00:00", None, None, None)
        x("INSERT INTO inv_line VALUES (?,?,?,?,?)", inv_no, 1, item, billed, r8)
        recorded.append({"inv_no": inv_no, "po_no": po_no, "expect": "matched" if kind == "clean" else kind})
    erp.payables_recorded = recorded
    # 5. late orders nobody has billed yet
    late = []
    for sup, item, qty, rate, need, rec, buyer in LATE:
        c = (D(need) - dt.timedelta(days=21)).isoformat()
        po_no, _ = add_po(sup, item, qty, rate, c, need, buyer, [rec] if rec else [], None)
        late.append(po_no)
    # 6. stock: BAT-375 has been issued down to 400 (the 375 Wh pack is below its reorder level)
    x("UPDATE stock SET on_hand=400 WHERE itm_cd='BAT-375' AND whs_cd='WH-MAN-STR'")
    x("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES ('BAT-375','WH-MAN-STR','2026-10-23','ISSUE',-3700,'PRD-07 kitting')")
    erp.payables_expect = expect
    erp.payables_late = late
    return {"invoices": len(expect), "late": late}
