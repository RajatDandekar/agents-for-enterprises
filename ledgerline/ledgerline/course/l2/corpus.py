"""The small Northbridge Cycles text corpus Lecture 2's tiny GPT is trained on (all fictional).

    python3 ledgerline/ledgerline/course/l2/corpus.py        # rewrites northbridge_corpus.md beside this file (stdlib only)

Three kinds of text, mixed the way a purchase department's files are mixed:
  1. purchase notes, stores entries, approvals, orders and goods receipts, generated from Northbridge's seed data
     (items, suppliers and contract rates as in ledgerline/erp/seed.py) with a fixed random seed;
  2. short e-mails between Emma, Daniel, Luis, Aiko and Henrik;
  3. every line of Northbridge's purchase policy, supplier policy and approval matrix (ledgerline/docs).
The stock figures in the stores entries are drawn at random on purpose: the tiny GPT learns what a stock line
looks like, not what Northbridge has. Every document is dated between 3 Aug and 23 Oct 2026, so 23 Oct 2026 is the
corpus's last day: the tiny GPT's training cut-off. Money is in pounds with UK digit grouping; VAT is 20%.
"""
import pathlib
import random

HERE = pathlib.Path(__file__).parent
DOCS = HERE.parents[1] / "docs"

# code, description, contract rate (£), supplier, order quantities, daily use, typical stock
BATTERY_Q = [200, 300, 400, 500, 600, 800, 1000, 1200, 1500, 1800, 2000, 2500]
PART_Q = [2000, 3000, 4000, 5000, 6000, 8000, 10000, 12000, 15000, 20000]
ITEMS = [("BAT-500", "battery pack, 36 V 500 Wh", 119.00, "Voltway Cells", BATTERY_Q, [500, 550, 600, 650, 700], (20, 80)),
         ("BAT-375", "battery pack, 36 V 375 Wh", 92.00, "Voltway Cells", BATTERY_Q, [200, 250, 300], (10, 50)),
         ("BAT-750", "battery pack, 48 V 750 Wh", 146.00, "Voltway Cells", BATTERY_Q, [80, 90, 100, 120], (4, 15)),
         ("MNT-FRM-01", "battery mount, down-tube", 18.50, "Voltway Cells", PART_Q, [3500, 4000, 4500], (100, 400)),
         ("MNT-RCK-02", "battery mount, rear rack", 15.75, "Voltway Cells", PART_Q, [3500, 4000, 4500], (100, 400)),
         ("BEL-STD-01", "bell, standard", 6.80, "Pennine Brakes", PART_Q, [3000, 3500, 4000], (50, 300)),
         ("BRK-PAD-01", "brake pads, disc (pair)", 9.40, "Pennine Brakes", PART_Q, [3000, 3500, 4000], (50, 300)),
         ("CHG-4A-01", "charger, 4 A", 96.00, "Castlefield Chargers", PART_Q, [5000, 6000, 6500], (150, 600)),
         ("MTR-HUB-250", "hub motor, 250 W", 142.00, "Albion Motors", PART_Q, [5000, 6000, 6500], (150, 600)),
         ("BOX-BIKE-01", "carton, bike shipping", 21.50, "Irwell Packaging", PART_Q, [5000, 6000, 7000], (200, 700))]
CELL_PARTS = ["BAT-500", "BAT-375", "BAT-750", "MTR-HUB-250", "CHG-4A-01"]
PEOPLE = [("Emma", "ECLARKE"), ("Daniel", "DOKAFOR"), ("Luis", "LMORENO"), ("Aiko", "ATANAKA"), ("Henrik", "HWEBER")]
STORES = ["Manchester stores", "Leeds stores"]
RUNS = ["the spring launch run", "the city e-bike line", "the cargo e-bike line", "the export batch",
        "the Leeds trial build"]
DATES = [(m, d) for m, last in (("Aug", 31), ("Sep", 30), ("Oct", 23)) for d in range(1, last + 1)
         if not (m == "Aug" and d < 3)]
VAT = 0.20


def money(n: float) -> str:
    """UK digit grouping: 285600 -> 285,600; 119 -> 119.00 when pence are shown."""
    return f"{n:,.2f}".removesuffix(".00")


def notes(rng: random.Random, n: int) -> list[str]:
    out = []
    for _ in range(n):
        code, desc, rate, sup, qs, uses, (lo, hi) = rng.choice(ITEMS)
        qty = rng.choice(qs)
        basic = qty * rate
        gross = round(basic * (1 + VAT), 2)
        who, uid = rng.choice(PEOPLE[:3])
        m, d = rng.choice(DATES)
        day = f"{d} {m} 2026"
        pr = f"PR/2026/0{rng.randint(4300, 4416)}"
        po = f"PO/2026/0{rng.randint(1100, 1181)}"
        kind = rng.randrange(6)
        if kind == 0:
            out.append(f"Note, {day}, {uid}: raised {pr} for {money(qty)} {code} ({desc}) for {rng.choice(RUNS)}. "
                       f"Supplier {sup}, contract rate £{rate:.2f}. Basic £{money(basic)}, gross £{money(gross)} with VAT.")
        elif kind == 1:
            use = rng.choice(uses)
            on_hand = rng.randrange(lo, hi) * 100
            out.append(f"Stores, {day}: {code} in {rng.choice(STORES)}, {money(on_hand)} on hand, "
                       f"using {money(use)} a day, {on_hand // use} days of cover.")
        elif kind == 2:
            who, uid = rng.choice(PEOPLE[:2])
            limit = 250000 if uid == "ECLARKE" else 1000000
            verdict = "above" if gross > limit else "within"
            out.append(f"Approval, {day}: {pr} is £{money(gross)} gross, {verdict} {who}'s limit of £{money(limit)}."
                       + (" It waits for Daniel." if verdict == "above" and uid == "ECLARKE" else
                          " It waits for Henrik." if verdict == "above" else " It goes ahead."))
        elif kind == 3:
            out.append(f"Order, {day}: {po} to {sup} for {money(qty)} {code}, £{money(gross)} gross. "
                       f"Status released, sent to the supplier.")
        elif kind == 4:
            got = qty - rng.choice([0, 0, qty // 4, qty // 2])
            out.append(f"Goods receipt, {day}: Aiko counted {money(got)} {code} against {po} at {rng.choice(STORES)}, "
                       f"delivery note DN-{rng.randint(4300, 4470)}.")
        else:
            code = rng.choice(CELL_PARTS)
            out.append(f"Reminder, {day}: {code} is a lithium-cell part. Buy it only from a supplier with a valid "
                       f"UN 38.3 certificate.")
    return out


EMAILS = [
    "From: Emma Clarke\nTo: Daniel Okafor\nDate: 22 Oct 2026\nSubject: Battery packs for the spring launch run\n\n"
    "Daniel, we need 2,000 battery packs, BAT-500, for the spring launch run. Manchester stores has 5,400 and we use "
    "about 600 a day, so nine days of cover. Voltway Cells supplies at the contract rate of £119.00. The order is "
    "£238,000 basic and £285,600 with VAT, above my limit, so it needs your approval.\nEmma",
    "From: Daniel Okafor\nTo: Emma Clarke\nDate: 22 Oct 2026\nSubject: Re: Battery packs for the spring launch run\n\n"
    "Approved. Please raise the order on PRD-07, not PRD-05; Finance closed PRD-05, the city e-bike line, on 15 Oct.\nDaniel",
    "From: Luis Moreno\nTo: Emma Clarke\nDate: 20 Oct 2026\nSubject: Brightcell Energy\n\n"
    "Emma, Brightcell Energy in Lyon quoted £104.00 a pack, but they are not in our supplier master and have no "
    "UN 38.3 certificate. Policy 6.2 says no order for a lithium-cell part without a valid certificate. Stay with "
    "Voltway Cells.\nLuis",
    "From: Luis Moreno\nTo: Purchase team\nDate: 1 Oct 2026\nSubject: Nordic Cell Co.\n\n"
    "Nordic Cell Co. in Gdańsk is cheaper at £111.00, but their UN 38.3 certificate expired on 30 Sep 2026. An "
    "expired certificate counts as no certificate. No orders to them until a new one is on file.\nLuis",
    "From: Aiko Tanaka\nTo: Emma Clarke\nDate: 16 Oct 2026\nSubject: Battery packs received\n\n"
    "Emma, 1,200 battery packs arrived today against PO/2026/01120, delivery note DN-4402. The other 600 are due on "
    "Friday.\nAiko",
    "From: Henrik Weber\nTo: Purchase team\nDate: 19 Oct 2026\nSubject: Spring launch run\n\n"
    "Team, the spring launch run starts on 9 November. Please check stock of every battery pack, charger and hub "
    "motor this week, and tell me early if anything is short.\nHenrik",
    "From: Emma Clarke\nTo: Luis Moreno\nDate: 14 Oct 2026\nSubject: Voltway Paints & Coatings\n\n"
    "Luis, a quotation came from Voltway Paints & Coatings, Rotterdam. Is this our Voltway?\nEmma",
    "From: Luis Moreno\nTo: Emma Clarke\nDate: 14 Oct 2026\nSubject: Re: Voltway Paints & Coatings\n\n"
    "No, a different company: they sell frame paint. Our battery packs come from Voltway Cells, Eindhoven, "
    "VC-EIN-0042. Never use VC-EIN-0009, that is the old blocked code.\nLuis",
    "From: Daniel Okafor\nTo: Purchase team\nDate: 5 Oct 2026\nSubject: Approval limits\n\n"
    "A reminder: limits apply to the gross value including VAT. Emma can approve up to £250,000, I can approve up "
    "to £1,000,000, and Henrik above that.\nDaniel",
    "From: Luis Moreno\nTo: Emma Clarke\nDate: 8 Oct 2026\nSubject: Tax code for Voltway\n\n"
    "Emma, Voltway Cells is in the Netherlands, so the order needs VAT20-RC, reverse charge. Fetch fills in VAT20-UK "
    "and the save fails with ERR-PO-0412.\nLuis",
]


def policy_lines() -> list[str]:
    out = []
    for name in ("purchase-policy.md", "supplier-policy.md", "approval-matrix.md"):
        p = DOCS / name
        if not p.exists():
            continue
        body = p.read_text().split("---", 2)[-1]
        out += [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("|--")]
    return out


def build(seed: int = 7, n_notes: int = 700) -> str:
    rng = random.Random(seed)
    parts = notes(rng, n_notes) + EMAILS * 3 + policy_lines() * 2
    rng.shuffle(parts)
    return "\n\n".join(parts) + "\n"


if __name__ == "__main__":
    text = build()
    (HERE / "northbridge_corpus.md").write_text(text)
    print(len(text), "characters,", len(set(text)), "distinct characters,", len(text.split()), "words")
