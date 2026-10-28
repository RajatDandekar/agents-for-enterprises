"""The small Rasoi text corpus Lecture 2's tiny GPT is trained on (all fictional).

    python3 bahi/bahi/course/l2/corpus.py        # rewrites rasoi_corpus.md beside this file (stdlib only)

Three kinds of text, mixed the way a purchase department's files are mixed:
  1. purchase notes and stores entries, generated from Rasoi's seed data with a fixed random seed;
  2. short e-mails between Kavita, Rohit, Suresh, Neha and Anand;
  3. every line of Rasoi's purchase policy, supplier policy and approval matrix (bahi/docs).
The stock figures in the notes are drawn at random on purpose: the tiny GPT learns what a stock line
looks like, not what Rasoi has. That is the lesson of the lecture.
"""
import pathlib
import random

HERE = pathlib.Path(__file__).parent
DOCS = HERE.parents[1] / "docs"

ITEMS = [("GSK-SIL-05L", "silicone gasket, 5 litre", 11.90, "Deccan Polymers"),
         ("GSK-SIL-03L", "silicone gasket, 3 litre", 9.20, "Deccan Polymers"),
         ("GSK-SIL-07L", "silicone gasket, 7.5 litre", 14.60, "Deccan Polymers"),
         ("HDL-BKL-01", "bakelite handle, long", 18.50, "Deccan Polymers"),
         ("HDL-BKL-02", "bakelite handle, short", 15.75, "Deccan Polymers"),
         ("WHS-STD-01", "whistle, standard", 6.80, "Sahyadri Valves"),
         ("SVL-STD-01", "safety valve, standard", 9.40, "Sahyadri Valves"),
         ("LID-SS-05L", "stainless steel lid, 5 litre", 96.00, "Om Sheet Metals"),
         ("SS-CIR-05L", "steel circle, 5 litre body blank", 142.00, "Mahalaxmi Steels"),
         ("BOX-CRG-05L", "corrugated carton, 5 litre", 21.50, "Shree Packaging")]
PEOPLE = [("Kavita", "KJOSHI"), ("Rohit", "RMEHTA"), ("Suresh", "SKULKARNI"), ("Neha", "NDESAI"), ("Anand", "APATIL")]
STORES = ["Pune stores", "Chakan stores"]
RUNS = ["the Diwali run", "the November run", "the export batch", "the Chakan trial", "the December run"]
MONTHS = ["Sep", "Oct", "Nov"]


def inr(n: float) -> str:
    """Indian digit grouping: 280840 -> 2,80,840."""
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
                       f"Supplier {sup}, contract rate ₹{rate:.2f}. Basic ₹{inr(basic)}, gross ₹{inr(gross)} with GST.")
        elif kind == 1:
            on_hand = rng.randrange(2, 90) * 1000
            use = rng.choice([1500, 2500, 3500, 4000, 6000])
            out.append(f"Stores, {day}: {code} in {rng.choice(STORES)}, {inr(on_hand)} on hand, "
                       f"using {inr(use)} a day, {on_hand // use} days of cover.")
        elif kind == 2:
            who, uid = rng.choice(PEOPLE[:2])
            limit = 250000 if uid == "KJOSHI" else 1000000
            verdict = "above" if gross > limit else "within"
            out.append(f"Approval, {day}: {pr} is ₹{inr(gross)} gross, {verdict} {who}'s limit of ₹{inr(limit)}."
                       + (" It waits for Rohit." if verdict == "above" and uid == "KJOSHI" else " It goes ahead."))
        elif kind == 3:
            out.append(f"Order, {day}: {po} to {sup} for {inr(qty)} {code}, ₹{inr(gross)} gross. Status approved, released to the supplier.")
        elif kind == 4:
            got = qty - rng.choice([0, 0, 2000, 4000])
            out.append(f"Goods receipt, {day}: Neha counted {inr(got)} {code} against {po} at {rng.choice(STORES)}.")
        else:
            code = rng.choice(["GSK-SIL-05L", "GSK-SIL-03L", "GSK-SIL-07L", "LID-SS-05L", "SS-CIR-05L"])
            out.append(f"Reminder, {day}: {code} is a food-contact part. Buy it only from a supplier with a valid food-grade certificate.")
    return out


EMAILS = [
    "From: Kavita Joshi\nTo: Rohit Mehta\nSubject: Gaskets for the Diwali run\n\nRohit, we need 20,000 silicone gaskets, GSK-SIL-05L, before the Diwali run. "
    "Stock is 54,000 and we use 6,000 a day, so we have nine days. Deccan Polymers can supply at the contract rate of ₹11.90. "
    "The order is ₹2,80,840 with GST, above my limit, so it needs your approval.\nKavita",
    "From: Rohit Mehta\nTo: Kavita Joshi\nSubject: Re: Gaskets for the Diwali run\n\nApproved. Please raise the order on PRD-07, not PRD-05; Finance closed PRD-05 on 15 Oct.\nRohit",
    "From: Suresh Kulkarni\nTo: Kavita Joshi\nSubject: Shakti Seals\n\nKavita, Shakti Seals quoted ₹10.40, but they are not in our supplier master and have no food-grade certificate. "
    "Policy 6.2 says no order for a food-contact part without a valid certificate. Stay with Deccan.\nSuresh",
    "From: Neha Desai\nTo: Kavita Joshi\nSubject: Gaskets received\n\nKavita, 12,000 gaskets arrived today against PO/2026/01182. The rest, 8,000, are due on Friday.\nNeha",
    "From: Anand Patil\nTo: Purchase team\nSubject: Diwali run\n\nTeam, the Diwali run starts on 9 November. Please check stock of every gasket, handle and whistle this week, and tell me early if anything is short.\nAnand",
    "From: Kavita Joshi\nTo: Suresh Kulkarni\nSubject: Deccan Polymer Industries\n\nSuresh, a quotation came from Deccan Polymer Industries, Rajkot. Is this our Deccan Polymers? The GSTIN looks the same.\nKavita",
    "From: Suresh Kulkarni\nTo: Kavita Joshi\nSubject: Re: Deccan Polymer Industries\n\nYes, same GSTIN, same supplier. Use DP-RJK-0042. Never DP-RJK-0009, that is the old blocked code.\nSuresh",
    "From: Rohit Mehta\nTo: Purchase team\nSubject: Approval limits\n\nA reminder: limits apply to the gross value including GST. Kavita can approve up to ₹2,50,000, I can approve up to ₹10,00,000, and Anand above that.\nRohit",
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
    (HERE / "rasoi_corpus.md").write_text(text)
    print(len(text), "characters,", len(set(text)), "distinct characters,", len(text.split()), "words")
