"""Lecture 4: how good is decide()'s confidence? 32 labelled inputs across the four typed decisions, k=5 samples each.

    modal run tools/modal_run.py --script lectures/L4-the-route/experiments/decide_eval.py

For each input we log the choice, the confidence (share of the 5 samples that agree) and whether the choice was right.
Then: with a threshold tau, how many decisions are taken automatically, and how many of those are right?
Cases marked right=None are genuinely ambiguous: the right outcome is to ASK (confidence below the threshold).
"""
import json
import pathlib

from bahi.agent.decide import decide
from bahi.llm import LLM

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
llm = LLM("gemini:gemini-3.8-flash", cassette="L4_decide")
SUP = {"supplier": "Shakti Seals (not in Bahi)", "item": "Gasket, silicone, 5 L (GSK-SIL-05L)", "certificate_on_file": "none"}
CANDS = ["Deccan Polymers (DP-RJK-0042, Rajkot)", "Deccan Paints & Inks (DPI-AMD-0107, Ahmedabad)", "none of these"]
CASES = [
    # document_kind
    ("document_kind", "Certificate FSSAI-LAB/SS/2026/071 issued to Shakti Seals, Vadodara: silicone compound tested and found fit for food contact. Valid until 31-03-2027.", SUP, None, "food_grade_certificate"),
    ("document_kind", "Yes, here it is: FSSAI-LAB/SS/2026/071, valid till 31 March 2027.", SUP, None, "food_grade_certificate"),
    ("document_kind", "They sent the renewal: certificate FSSAI-LAB/KR/2026/131, valid to 30 September 2027.", {**SUP, "supplier": "Kaveri Rubber Products (KR-KOL-0063, Kolkata)", "certificate_on_file": "expired"}, None, "food_grade_certificate"),
    ("document_kind", "QUOTATION No. SS/Q/2026/88. Silicone gasket 5 L, food grade material, Rs 10.40 per piece, valid 30 days.", SUP, None, "quotation"),
    ("document_kind", "Our best rate for the 5L gasket is ₹10.40, ex-works Vadodara. All our silicone is food grade.", SUP, None, "quotation"),
    ("document_kind", "Proforma invoice PI/0091 from Shakti Seals: 20,000 gaskets x ₹10.40 = ₹2,08,000 + GST.", SUP, None, "quotation"),
    ("document_kind", "Test report TR-5521: tensile strength 8.2 MPa, hardness 60 Shore A. Sample from Shakti Seals.", SUP, None, "other_document"),
    ("document_kind", "I don't have a certificate from them yet.", SUP, None, "no_document"),
    ("document_kind", "I don't have one, but Rohit said it's fine. Please go ahead.", SUP, None, "no_document"),
    ("document_kind", "They say the certificate is with their lab and will come next week.", SUP, None, "no_document"),
    # pick_supplier
    ("pick_supplier", "She wrote: 'Deccan Polymer Industries'", {"item": "Handle, bakelite, long (HDL-BKL-01)"}, CANDS, CANDS[0]),
    ("pick_supplier", "She wrote: 'Deccan Polymer Inds. Pvt Ltd', Rajkot", {"item": "Handle, bakelite, long (HDL-BKL-01)"}, CANDS, CANDS[0]),
    ("pick_supplier", "She wrote: 'Deccan Paints'", {"item": "Gasket, silicone, 5 L (GSK-SIL-05L)"}, CANDS, CANDS[1]),
    ("pick_supplier", "She wrote: 'Deccan Paints and Inks, Ahmedabad'", {"item": "Carton"}, CANDS, CANDS[1]),
    ("pick_supplier", "She wrote: 'Deccan'", {"item": "Gasket, silicone, 7.5 L (GSK-SIL-07L)"}, CANDS, None),
    ("pick_supplier", "She wrote: 'Deccan Rubber Works, Pune'", {"item": "Gasket, silicone, 5 L (GSK-SIL-05L)"}, CANDS, "none of these"),
    ("pick_supplier", "Deccan Polymers in Rajkot.", {"she_first_said": "Deccan", "item": "Gasket, silicone, 7.5 L (GSK-SIL-07L)"}, CANDS, CANDS[0]),
    ("pick_supplier", "The paints one.", {"she_first_said": "Deccan", "item": "Carton"}, CANDS, CANDS[1]),
    # intent
    ("intent", "Can we buy the 5-litre gaskets from a supplier that doesn't have a food-grade certificate? Their price is much better.", {}, None, "policy_question"),
    ("intent", "Shakti Seals has quoted ₹10.40 for the 5-litre gasket. Order 20,000 from them.", {}, None, "order"),
    ("intent", "What's the status of PO/2026/01179?", {}, None, "order_status"),
    ("intent", "How many days of cover do we have on the 5-litre gaskets?", {}, None, "stock_question"),
    ("intent", "We need more whistles.", {}, None, "order"),
    ("intent", "Can I order the lids from Om Sheet Metals?", {}, None, None),
    ("intent", "Can I still charge new orders to cost centre PRD-05?", {}, None, "policy_question"),
    ("intent", "Thanks, that's all for today.", {}, None, "other"),
    # confirmation
    ("confirmation", "Yes, go ahead.", {"preview": "20,000 x GSK-SIL-05L from DP-RJK-0042, ₹2,80,840"}, None, "yes"),
    ("confirmation", "ok", {"preview": "3,000 x WHS-STD-01 from SV-PUN-0017, ₹24,072"}, None, "yes"),
    ("confirmation", "No, hold it for now.", {"preview": "3,000 x WHS-STD-01 from SV-PUN-0017, ₹24,072"}, None, "no"),
    ("confirmation", "Make it 4,000 actually.", {"preview": "3,000 x WHS-STD-01 from SV-PUN-0017, ₹24,072"}, None, "change"),
    ("confirmation", "Yes, but charge it to PRD-03.", {"preview": "3,000 x WHS-STD-01 on PRD-07"}, None, "change"),
    ("confirmation", "Hmm, let me check with Rohit first.", {"preview": "20,000 x GSK-SIL-05L, ₹2,80,840"}, None, None),
]
rows = []
for name, text, ctx, opts, right in CASES:
    d = decide(name, text, ctx, opts, k=5, threshold=0.8, llm=llm)
    rows.append({"decision": name, "input": text, "right": right, "choice": d.choice, "confidence": d.confidence,
                 "votes": d.votes, "fields": d.fields, "reason": d.reason,
                 "correct": (d.choice == right) if right is not None else None})
    print(f"{name:14s} {d.confidence:.1f} {d.choice:40s} right={right} | {text[:60]}")
summary = {}
for tau in (0.6, 0.8, 1.0):
    auto = [r for r in rows if r["confidence"] >= tau]
    labelled_auto = [r for r in auto if r["right"] is not None]
    amb = [r for r in rows if r["right"] is None]
    summary[str(tau)] = {"auto": len(auto), "asked": len(rows) - len(auto),
                         "auto_correct": sum(r["correct"] for r in labelled_auto), "auto_labelled": len(labelled_auto),
                         "ambiguous_asked": sum(1 for r in amb if r["confidence"] < tau), "ambiguous": len(amb)}
labelled = [r for r in rows if r["right"] is not None]
summary["all"] = {"cases": len(rows), "labelled": len(labelled), "correct": sum(r["correct"] for r in labelled),
                  "wrong_but_sure_at_0.8": [r["input"] for r in labelled if not r["correct"] and r["confidence"] >= 0.8],
                  "tokens_in": sum(r.tokens_in for r in llm.log), "tokens_out": sum(r.tokens_out for r in llm.log),
                  "calls": len(llm.log), "cost_inr": round(sum(r.cost_inr for r in llm.log), 4),
                  "seconds": round(sum(r.seconds for r in llm.log), 1)}
print(json.dumps(summary, indent=1))
(LOGS / "decide_eval.json").write_text(json.dumps({"k": 5, "model": llm.model, "summary": summary, "rows": rows}, indent=1, ensure_ascii=False))
