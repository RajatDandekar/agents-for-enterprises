---
title: "Decision 2026-09-02 Lithium-cell PO approval comment requirement"
type: "decision"
slug: "decision-2026-09-02-lithium-cell-po-approval-comment"
summary: "Decision requiring approvers of lithium-cell items to include 'CERT OK' and the certificate reference in PO approval comments."
audience: "staff"
status: "current"
sources: ["09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| decision_date | 2026-09-02 |
| status | current |
| applies_to | BAT-*, MTR-*, CHG-* items or lithium-cell flag |
| requirement | CERT OK <certificate_reference> in approval comment |
| source_type | email |

This operational decision mandates that anyone approving a purchase order for lithium-cell parts must verify compliance and record it directly in the approval comment[^r1]. Effective 2 September 2026, approvers must enter "CERT OK" followed by the certificate document reference before releasing the order[^r1]. The instruction enforces a strict "no comment, no approval" rule across all relevant orders today[^r2].

| Attribute | Value |
|---|---|
| Decision date | 2026-09-02 |
| Status | Current |
| Scope | [[items-bat|BAT-*]], [[items-mtr|MTR-*]], [[items-chg|CHG-*]], or lithium-cell flagged items |
| Rule | "CERT OK" plus certificate reference required in approval comment |
| Enforcement | No comment, no approval |

## Context and Decision

Following the July incident and Amendment 2, an active operational procedure was established on 2 September 2026 prior to its inclusion in formal policy[^r1][^r2]. Effective immediately from that date, anyone approving an order for a [[items-bat|BAT-*]], [[items-mtr|MTR-*]], or [[items-chg|CHG-*]] item, or any part bearing the lithium-cell flag, must enter "CERT OK" along with the certificate document reference in the approval comment field[^r1]. An example of a valid entry is `CERT OK UN38.3-TR/VC/2026/118`[^r1]. Purchase orders containing lithium-cell items must not be approved without this certificate reference comment under the operational directive of "No comment, no approval"[^r2].

## Versions and conflicts

* **Today's rule**: Approvers must enter "CERT OK" and the certificate document reference in the approval comment field for any order containing a lithium-cell part, and purchase orders must not be approved without it (`09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml`)[^r1][^r2].
* **Older or other rule**: Formal purchasing procedure in [[sop-pur-002|SOP-PUR-002]] has not yet been reissued to incorporate this mandatory comment rule into standard written policy[^r2].
* **Kind**: `email_overrides_sop`

## See also

* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[items-bat|BAT-* items]]
* [[items-mtr|MTR-* items]]
* [[items-chg|CHG-* items]]
* [[user-dokafor|Daniel Okafor (DOKAFOR)]]

## References

[^r1]: 09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml, body
[^r2]: 09_email_archive/2026/2026-09-02_Approving orders for lithium-cell parts - CERT OK in the approval comment.eml, body
