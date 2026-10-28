# Legal · contracts: the demo-day change

**Announced:** end of Lecture 11 (Saturday 5 December, 9 AM). **Absorb it by:** demo day (Lecture 12), Sunday 6 December, 7 AM. One day and an evening: that is the test.
**Kind:** a new variant. **Worth:** 10 of the 100 points.

## What the client says

> "From today, when we lend one of our moulds or dies to a supplier for a trial, an NDA is not enough. Last year a
> die came back from a vendor cracked, and nothing in writing said who pays. Legal has made a tooling loan agreement
> for this, template TLA-TOOL-v1: six months, Pune courts, and the mould's book value goes on the request. Rekha
> reviews every one, and only I sign them. Circular LEG-CIR-2026-02 has the details."
>
> Dr. Dandekar, playing the plant head

## What changes in your module

| | Before the change | After the change |
|---|---|---|
| The paperwork for a mould on trial | A mutual NDA, NDA-MUT-v4 | A **tooling loan agreement**: CT TYPE **TLA**, template **TLA-TOOL-v1** (its own confidentiality clause; no separate NDA needed) |
| Term and courts | 24 months, Pune | **6 months** (at most 12), Pune |
| VALUE | 0 (an NDA has no value) | The mould's **book value**: ₹3,80,000 for MLD-GSK-05L |
| Route through Bahi | Our paper, no deviation: straight to signature (PS) | Our paper, but the clause scan flags the value (TLA-VALUE), so it goes to **Legal (LR)**, then to signature (PS) |
| Who signs | Anand Patil (FWD TO: APATIL) | Anand Patil, still by FWD TO. Bahi's value routing would send ₹3,80,000 to Rohit |
| What the reply must say | the party, the template, the term, the signatory | the same, **and which rule asked for a tooling loan agreement** |

Bahi gains one template and three playbook lines (`apply()` in [`demo_change.py`](demo_change.py)). No service or
procedure changes: Fetch with TLA-TOOL-v1 fills CT TYPE TLA, and the clause scan you already know sends it to Legal.
Two silent traps come with it. Save it with no value and nothing is flagged, so it skips Legal. Leave FWD TO blank
and Rohit gets it to sign.

## What to do

1. Add `legal-circular-2026-02.md` to your module's documents. Its text is `DOC` in [`demo_change.py`](demo_change.py).
   Re-index your retrieval corpus (A2) and add one question about it to your 20-question test.
2. Teach your tools the new type (A3): `ct_type` takes TLA, `tmpl_cd` takes TLA-TOOL-v1, and VALUE is the tool's book
   value. Ask for the value if the user has not given it.
3. Add the branch to your route (A4): a mould, die or fixture going out for a trial means a TLA, not an NDA. Expect the
   extra stop at Legal (LR before PS), and hold the request while Legal and the signatory decide.
4. Extend your authority matrix (A5): a TLA of any value is signed by the plant head only (FWD TO: APATIL), and it is
   always cleared by Legal (RMENON). Read back status, end date (25 Apr 2027) and the register row as proof.
5. Make the reply name the rule (the circular's id, or "tooling loan agreement").
6. Re-run your four scenarios and your 30-case suite (A6). Nothing else should move. A step that hangs (A7) is found
   again by `client_ref` before it is raised twice.

## The hidden test the grader runs

`SCENARIO` in `demo_change.py`: Kavita says *"Shakti Seals, Vadodara, are going to run a trial batch on our 5-litre
gasket mould, MLD-GSK-05L. Stores wants to send it on Thursday. Its book value is ₹3,80,000. Their GSTIN is
24AAFCS8812N1Z4 and PAN AAFCS8812N. Please put the paperwork in place."* and then *"Yes, go ahead."*. Legal and the
signatory decide whatever reaches them.

It passes when exactly one tooling loan agreement for Shakti Seals, Vadodara, is executed: TLA-TOOL-v1, our paper,
6 months to 25 Apr 2027, value ₹3,80,000, cleared by Rekha Menon, signed by Anand Patil, and in the contract register.
The reply must name the rule, and none of the kit's never-events may fire. Under the circular, a TLA that reaches
signature without Legal is a never-event (NE3), and a TLA signed by anyone but the plant head is one too (NE1).

Tested on Modal against the kit's reference run (`lectures/L8-your-module/experiments/logs/demo_changes_legal_contracts.json`):
the careful run from before the change **fails** (it raises and executes a mutual NDA, CT/2026/0057, and no TLA), the
careful run after the change **passes** (8 service calls; Legal, then Anand), the naive run is **caught** (NE1 and
NE3: no value, so no Legal, and Rohit signed it), the kit's own four scenarios still pass with the change in place,
and the hidden scenario passes with all eight kits installed.
