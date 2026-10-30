"""The small Northbridge text corpus Lecture 2's tiny GPT is trained on (all fictional).

    python3 ledgerline/ledgerline/course/l2/corpus.py        # rewrites northbridge_corpus.md beside this file (stdlib only)

Three kinds of text, mixed the way a purchase department's files are mixed:
  1. purchase notes and stores entries, generated from Northbridge's seed data with a fixed random seed;
  2. short e-mails between Emma, Daniel, Luis, Aiko and Henrik;
  3. every line of Northbridge's purchase policy, supplier policy and approval matrix (ledgerline/docs).
The stock figures in the notes are drawn at random on purpose: the tiny GPT learns what a stock line
looks like, not what Northbridge has. That is the lesson of the lecture.
"""
import pathlib
import random

HERE = pathlib.Path(__file__).parent
DOCS = HERE.parents[1] / "docs"

ITEMS = [("BAT-500", "battery pack, 5 litre", 11.90, "Voltway Cells"),
         ("BAT-375", "battery pack, 3 litre", 9.20, "Voltway Cells"),
         ("BAT-750", "battery pack, 7.5 litre", 14.60, "Voltway Cells"),
         ("MNT-FRM-01", "ergonomic handle, long", 18.50, "Voltway Cells"),
         ("MNT-RCK-02", "ergonomic handle, short", 15.75, "Voltway Cells"),
         ("BEL-STD-01", "whistle, standard", 6.80, "Pennine Brakes"),
         ("BRK-PAD-01", "safety valve, standard", 9.40, "Pennine Brakes"),
         ("CHG-4A-01", "stainless steel lid, 5 litre", 96.00, "Castlefield Chargers"),
         ("MTR-HUB-250", "steel circle, 5 litre body blank", 142.00, "Albion Motors"),
         ("BOX-BIKE-01", "corrugated carton, 5 litre", 21.50, "Irwell Packaging")]
PEOPLE = [("Emma", "ECLARKE"), ("Daniel", "DOKAFOR"), ("Luis", "LMORENO"), ("Aiko", "ATANAKA"), ("Henrik", "HWEBER")]
STORES = ["Manchester stores", "Leeds stores"]
RUNS = ["the spring-launch run", "the November run", "the export batch", "the Leeds trial", "the December run"]
MONTHS = ["Sep", "Oct", "Nov"]


def inr(n: float) -> str:
    """Indian digit grouping: 280840 -> 280,840."""
    whole, frac = f"{n:.2f}".split(".")
    head, tail = whole[:-3], whole[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    s = ",".join(groups + [tail]) if groups else tail
    return s + ("" if frac == "00" else "." + frac)


def notes(rng: random.Random, n: int) -> list[str]:
    out = []
    for _ in range(n):
        code, desc, rate, sup = rng.choice(ITEMS)
        qty = rng.choice([2000, 4000, 5000, 6000, 8000, 10000, 12000, 15000, 18000, 20000, 25000])
        basic = qty * rate
        gross = round(basic * 1.18, 2)
        who, uid = rng.choice(PEOPLE[:3])
        day = f"{rng.randint(1, 28)} {rng.choice(MONTHS)} 2026"
        pr = f"PR/2026/0{rng.randint(4300, 4499)}"
        po = f"PO/2026/0{rng.randint(1100, 1199)}"
        kind = rng.randrange(6)
        if kind == 0:
            out.append(f"Note, {day}, {uid}: raised {pr} for {inr(qty)} {code} ({desc}) for {rng.choice(RUNS)}. "
                       f"Supplier {sup}, contract rate £{rate:.2f}. Basic £{inr(basic)}, gross £{inr(gross)} with VAT.")
        elif kind == 1:
            on_hand = rng.randrange(2, 90) * 1000
            use = rng.choice([1500, 2500, 3500, 4000, 6000])
            out.append(f"Stores, {day}: {code} in {rng.choice(STORES)}, {inr(on_hand)} on hand, "
                       f"using {inr(use)} a day, {on_hand // use} days of cover.")
        elif kind == 2:
            who, uid = rng.choice(PEOPLE[:2])
            limit = 250000 if uid == "ECLARKE" else 1000000
            verdict = "above" if gross > limit else "within"
            out.append(f"Approval, {day}: {pr} is £{inr(gross)} gross, {verdict} {who}'s limit of £{inr(limit)}."
                       + (" It waits for Daniel." if verdict == "above" and uid == "ECLARKE" else " It goes ahead."))
        elif kind == 3:
            out.append(f"Order, {day}: {po} to {sup} for {inr(qty)} {code}, £{inr(gross)} gross. Status approved, released to the supplier.")
        elif kind == 4:
            got = qty - rng.choice([0, 0, 2000, 4000])
            out.append(f"Goods receipt, {day}: Aiko counted {inr(got)} {code} against {po} at {rng.choice(STORES)}.")
        else:
            code = rng.choice(["BAT-500", "BAT-375", "BAT-750", "CHG-4A-01", "MTR-HUB-250"])
            out.append(f"Reminder, {day}: {code} is a lithium-cell part. Buy it only from a supplier with a valid UN 38.3 certificate.")
    return out


EMAILS = [
    "From: Emma Clarke\nTo: Daniel Okafor\nSubject: Battery packs for the spring-launch run\n\nRohit, we need 20,000 battery packs, BAT-500, before the spring-launch run. "
    "Stock is 54,000 and we use 6,000 a day, so we have nine days. Voltway Cells can supply at the contract rate of £11.90. "
    "The order is £280,840 with VAT, above my limit, so it needs your approval.\nKavita",
    "From: Daniel Okafor\nTo: Emma Clarke\nSubject: Re: Battery packs for the spring-launch run\n\nApproved. Please raise the order on PRD-07, not PRD-05; Finance closed PRD-05 on 15 Oct.\nRohit",
    "From: Luis Moreno\nTo: Emma Clarke\nSubject: Brightcell Energy\n\nKavita, Brightcell Energy quoted £10.40, but they are not in our supplier master and have no UN 38.3 certificate. "
    "Policy 6.2 says no order for a lithium-cell part without a valid certificate. Stay with Voltway.\nSuresh",
    "From: Aiko Tanaka\nTo: Emma Clarke\nSubject: Battery packs received\n\nKavita, 12,000 battery packs arrived today against PO/2026/01182. The rest, 8,000, are due on Friday.\nNeha",
    "From: Henrik Weber\nTo: Purchase team\nSubject: spring-launch run\n\nTeam, the spring-launch run starts on 9 November. Please check stock of every battery pack, handle and whistle this week, and tell me early if anything is short.\nAnand",
    "From: Emma Clarke\nTo: Luis Moreno\nSubject: Voltway Polymer Industries\n\nSuresh, a quotation came from Voltway Polymer Industries, Eindhoven. Is this our Voltway Cells? The VAT number looks the same.\nKavita",
    "From: Luis Moreno\nTo: Emma Clarke\nSubject: Re: Voltway Polymer Industries\n\nYes, same VAT number, same supplier. Use VC-EIN-0042. Never VC-EIN-0009, that is the old blocked code.\nSuresh",
    "From: Daniel Okafor\nTo: Purchase team\nSubject: Approval limits\n\nA reminder: limits apply to the gross value including VAT. Emma can approve up to £250,000, I can approve up to £1,000,000, and Henrik above that.\nRohit",
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
