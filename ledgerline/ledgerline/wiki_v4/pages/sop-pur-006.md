---
title: "SOP-PUR-006 Quotations and Supplier Selection"
type: "procedure"
slug: "sop-pur-006"
summary: "Standard operating procedure governing competitive quotations, threshold rules, UN 38.3 compliance, and supplier selection records."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-PUR-006 |
| Owner | Daniel Okafor |
| Approver | Henrik Weber |
| Version | 1.0 |
| Effective date | 2024-09-01 |
| Status | current |

SOP-PUR-006 defines the operational rules for gathering, evaluating, and documenting vendor quotations prior to supplier selection at Northbridge Cycles[^r1]. It establishes a mandatory £100,000 gross threshold for competitive quotes, enforces rate contract precedence, and governs compliance prerequisites for lithium-cell parts[^r2][^r3][^r5]. All selection packs must be retained in Ledgerline ERP to support procurement auditability[^r11].

| Field | Value |
|---|---|
| Code | SOP-PUR-006 |
| Owner | [[user-dokafor|Daniel Okafor]] |
| Approver | [[user-hweber|Henrik Weber]] |
| Version | 1.0 |
| Effective date | 2024-09-01 |
| Status | current |

## Steps

A new procurement requirement exceeding £100,000 gross requires three written quotations compared using form NBC-F-118[^r2]. Requisitions for the same project or related parts must never be split to circumvent this £100,000 gross threshold[^r6]. If only two quotations can be obtained for a requirement above the threshold, the case must be referred immediately to the purchasing manager, and form NBC-F-118 cannot be signed without written dispensation[^r7].

Items covered by an active rate contract are exempt from the quotation requirement and must be ordered at the agreed contract rate pursuant to [[pol-pur-001|POL-PUR-001]] clause 7.1[^r3]. If a rate contract appears on screen but the vendor quotes a differing unit price, procurement transactions must stop and the variance must be referred to the contracts team before raising the purchase order[^r10].

For [[items-bat|lithium-cell parts]], quotations may only be evaluated from suppliers that possess a valid [[topic-un-38-3-certificates|UN 38.3 test certificate]], and commercial price alone must never dictate vendor selection[^r5]. Should a supplier submit a quotation for lithium-cell parts with an expired, incomplete, or ambiguous UN 38.3 certificate, their bid must be set aside immediately until validated by quality engineering[^r8].

When a quotation is received from a vendor not listed in the supplier master, the buyer must initiate onboarding under [[sop-pur-001|SOP-PUR-001]], and the quotation cannot be formally accepted until onboarding concludes[^r4]. If a purchase order is entered for an unlisted vendor, it must remain on hold within Ledgerline ERP and cannot be released until onboarding is finalized and the ledger account is activated[^r9].

Completed supplier selection packs—consisting of formal requests, written quotations, evaluation matrices, and signed approval notes—must be attached directly to the master supplier file and the requisition audit trail in Ledgerline ERP[^r11].

## Forms and screens

* **NBC-F-118**: Quotation comparison form required for evaluating three written quotations on requirements over £100,000 gross[^r2][^r7].
* **Ledgerline ERP**: Procurement system where selection packs are attached and unlisted vendor purchase orders are held pending onboarding[^r9][^r11].

## See also

* [[items-bat|BAT-* items]]
* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[user-dokafor|Daniel Okafor (DOKAFOR)]]
* [[user-hweber|Henrik Weber (HWEBER)]]

## References

[^r1]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 1, Field Value
[^r2]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure
[^r3]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure
[^r5]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure
[^r11]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 4, Practice at Northbridge
[^r6]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure: notes and common mistakes
[^r7]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 4, What to do when something does not look right
[^r10]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 4, What to do when something does not look right
[^r8]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 4, What to do when something does not look right
[^r4]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 3, §5. Procedure
[^r9]: 02_procedures/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf, p. 4, What to do when something does not look right
