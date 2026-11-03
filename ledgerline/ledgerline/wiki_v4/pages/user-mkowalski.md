---
title: "Marta Kowalski (MKOWALSKI)"
type: "person"
slug: "user-mkowalski"
summary: "Accounts Payable Manager, author of AP standard operating procedures, and owner of the bank payment interface INT-002."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf", "02_procedures/SOP-AP-002 Period Close v3.0.pdf", "02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf", "02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf", "12_integrations/Integration inventory.xlsx", "10_meeting_notes/2022-03-03 Production planning meeting.docx", "10_meeting_notes/2026-06-30 Month-end review.docx", "10_meeting_notes/2026-09-18 Ledgerline key users.docx", "09_email_archive/2021/2021-05-27_Duplicate invoice caught.eml", "09_email_archive/2025/2025-01-08_Payment run approval cover.eml", "09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml", "09_email_archive/2026/2026-02-15_Bank detail change requests.eml", "09_email_archive/2026/2026-06-02_AP cut-off moves to working day 2.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| User ID | MKOWALSKI |
| Name | Marta Kowalski |
| Role | Accounts Payable Manager |
| Document ownership | SOP-AP-001, SOP-AP-002, SOP-AP-003, SOP-AP-004 |
| Interface ownership | INT-002 |

Marta Kowalski is the Accounts Payable Manager at Northbridge Cycles and the business author and owner of core accounts payable standard operating procedures [^r1][^r3][^r5][^r6]. She holds administrative responsibilities across Ledgerline AP operations, including invoice matching hold overrides, payment proposal approvals, and interface ownership for bank export files [^r2][^r5][^r7]. She also executes supplier payment batches across Manchester and Leeds trade vendors and supervises supplier bank detail verification controls [^r6][^r12][^r15].

| Field | Value |
|---|---|
| User ID | MKOWALSKI |
| Name | Marta Kowalski |
| Role | Accounts Payable Manager |
| Document ownership | [[sop-ap-001|SOP-AP-001]], [[sop-ap-002|SOP-AP-002]], [[sop-ap-003|SOP-AP-003]], [[sop-ap-004|SOP-AP-004]] |
| System ownership | Interface INT-002 ([[data-integration-inventory|Integration inventory]]) |

## Responsibilities and procedures

Kowalski owns and maintains four core AP procedures: [[sop-ap-001|SOP-AP-001]] (Three-Way Invoice Matching), [[sop-ap-002|SOP-AP-002]] (Accounts Payable Period Close), [[sop-ap-003|SOP-AP-003]] (Supplier Payment Run), and [[sop-ap-004|SOP-AP-004]] (Supplier Bank Detail Changes) [^r1][^r3][^r5][^r6]. 

Within Ledgerline, only the AP manager holds the authority to override invoice matching holds, provided an explanation is entered into the override comment field [^r2]. Kowalski monitors invoices blocked for price differences, instructing purchasing team buyers to resolve discrepancies via purchase order amendments or credit requests [^r14]. Under [[sop-ap-004|SOP-AP-004]], she mandates that AP team members immediately place supplier accounts on temporary hold if bank verification checks fail to reach a verified contact or if the supplier expresses uncertainty [^r15].

## Payment runs and period close

Kowalski prepares trade supplier payment runs for both Manchester and Leeds, matching supplier invoices against purchase orders and warehouse delivery notes [^r12]. Under [[sop-ap-003|SOP-AP-003]], she is responsible for approving payment proposals on screen [[screen-ap-pay-03|AP-PAY-03]] [^r5]. Once payment run authorization is granted by [[user-gwhitaker|Grace Whitaker]], Kowalski posts the batch, issues remittance advices, and releases the bank instruction [^r13]. She is the recorded business owner of integration interface INT-002, which exports the STD18 bank payment file [^r7].

Under [[sop-ap-002|SOP-AP-002]], Kowalski manages the AP period close on screen [[screen-ap-per-11|AP-PER-11]] [^r3][^r4]. Following an instruction issued by [[user-gwhitaker|Grace Whitaker]] on 2 June 2026, the period close cut-off was moved from working day 3 afternoon to working day 2 at 12:00 starting from the June 2026 close onward [^r4][^r9][^r16].

## Key meetings and operational history

* On 27 May 2021, [[user-tashworth|Tom Ashworth]] requested that Kowalski contact a supplier finance desk to instruct them to halt sending duplicate paper postal invoices after transmitting electronic copies [^r11].
* On 3 March 2022, Kowalski attended the cross-functional production planning meeting [^r8].
* On 30 June 2026, she participated in the month-end review assessing performance under the working day 2 AP close schedule [^r9].
* On 18 September 2026, she attended the Ledgerline key users meeting [^r10].

## Versions and conflicts

* **AP period close cut-off timing**: Effective from the June 2026 close onwards, the AP period close cut-off occurs on working day 2 at 12:00, as instructed by [[user-gwhitaker|Grace Whitaker]] on 2 June 2026 and reviewed at the 30 June 2026 month-end review [^r9][^r16]. This e-mail decision overrides the unamended text of [[sop-ap-002|SOP-AP-002]] v3.0 (§1, §5), which originally specified closing the period on screen [[screen-ap-per-11|AP-PER-11]] on the afternoon of working day 3 [^r3][^r4]. Kind: `email_overrides_sop`.

## See also

* [[sop-ap-001|SOP-AP-001 Three-Way Invoice Matching]]
* [[sop-ap-002|SOP-AP-002 Accounts Payable Period Close]]
* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[screen-ap-pay-03|AP-PAY-03 Payment Run]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[decision-2026-06-02-ap-cut-off|Decision 2026-06-02 AP Cut-off]]
* [[user-gwhitaker|Grace Whitaker (GWHITAKER)]]
* [[data-integration-inventory|Integration inventory]]

## References

[^r1]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 1, Field
[^r3]: 02_procedures/SOP-AP-002 Period Close v3.0.pdf, p. 1, Field / Value
[^r5]: 02_procedures/SOP-AP-003 Supplier Payment Run v1.4.pdf, p. 3, §5. Procedure
[^r6]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 1, §1. Purpose
[^r2]: 02_procedures/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf, p. 3, §5. Procedure
[^r7]: 12_integrations/Integration inventory.xlsx, sheet Interfaces, row INT-002, SHEET Interfaces
[^r12]: 09_email_archive/2025/2025-01-08_Payment run approval cover.eml, body
[^r15]: 09_email_archive/2026/2026-02-15_Bank detail change requests.eml, Bank detail change requests
[^r14]: 09_email_archive/2025/2025-05-18_Invoices on hold for price differences.eml, Invoices on hold for price differences
[^r13]: 09_email_archive/2025/2025-01-08_Payment run approval cover.eml, body
[^r4]: 02_procedures/SOP-AP-002 Period Close v3.0.pdf, p. 3, §5. Procedure
[^r9]: 10_meeting_notes/2026-06-30 Month-end review.docx, Month-end review
[^r16]: 09_email_archive/2026/2026-06-02_AP cut-off moves to working day 2.eml, headers
[^r11]: 09_email_archive/2021/2021-05-27_Duplicate invoice caught.eml, body
[^r8]: 10_meeting_notes/2022-03-03 Production planning meeting.docx, Production planning meeting
[^r10]: 10_meeting_notes/2026-09-18 Ledgerline key users.docx, Ledgerline key users
