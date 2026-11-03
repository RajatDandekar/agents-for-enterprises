---
title: "SOP-AP-004 Supplier Bank Detail Changes"
type: "procedure"
slug: "sop-ap-004"
summary: "SOP-AP-004 governs mandatory two-person independent call-back verifications and Ledgerline controls for amending supplier bank details to prevent payment fraud."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf", "02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "09_email_archive/2019/2019-05-02_Phishing e-mails pretending to be suppliers.eml", "09_email_archive/2026/2026-02-15_Bank detail change requests.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-AP-004 |
| Title | Supplier Bank Detail Changes |
| Owner | Marta Kowalski (AP Manager) |
| Approver | Grace Whitaker (Financial Controller) |
| Effective Date | 2025-10-01 |
| Version | 2.0 |
| Status | current |

SOP-AP-004 defines the mandatory controls and verification workflow required to change supplier bank details at Northbridge Cycles[^r1]. Accounts payable staff must never amend bank records based on incoming written or electronic requests alone, requiring an independent verbal call-back before any disbursements can proceed[^r2][^r15]. The procedure enforces strict segregation of duties between request logging, supplier contact, and ERP maintenance to prevent payment diversion fraud[^r4][^r5][^r10].

## Steps

### Receipt and Logging
Accounts payable staff must never accept bank detail amendments directly from inbound paperwork, advice slips, or electronic mail alone[^r2]. Staff must not click links or open attachments in any message requesting a change of payment details or pressing for immediate payment outside standard cycles[^r12]. Any request to amend bank details, switch payment methods, or redirect funds must be verified independently by contacting the supplier using the established telephone number recorded in the main register[^r13]. Staff must never use contact details printed on suspicious messages, invoices, incoming correspondence, or footers[^r14][^r16]. The purchase ledger clerk who logs a bank change request must not be the person who confirms the change with the supplier[^r4]. New supplier setups also require accounts payable to verify bank details by call-back in accordance with this procedure under check 6 of form NBC-F-113 ([[sop-pur-001|Supplier Onboarding]])[^r9].

### Independent Call-Back Verification
Verification of a supplier bank detail amendment requires calling the supplier back using a number from its letterhead, website, or the supplier master—never from the change request itself—with two accounts payable staff participating in the call[^r3]. An independent check must be performed using contact details from the established ledger record or a separate agreed contacts list outside the e-mail system[^r16]. Staff must speak directly with a known contact at the supplier firm before making any system alteration or passing paperwork to accounts for payment[^r14]. Accounts Payable staff must speak directly with a known contact at the supplier to verbally confirm both the existing account details and the new account details, retaining a record of the call and the contact alongside the written request[^r17].

### Suspicious Requests and Call Failures
If a contact on a verification call cannot answer routine questions regarding recent orders, purchase order references, or prior banking details, staff must terminate the call, retain system warning W-BNK-120, and inform purchasing teams at Manchester and Leeds[^r7]. If the verified contact cannot be reached or the supplier seems unsure about the change, the supplier account must be placed on temporary hold and [[user-mkowalski|Marta Kowalski]] alerted immediately[^r18]. If suspicious or ambiguous e-mail requests regarding bank changes are received, accounts payable operators must immediately execute `bnk_block` on screen [[screen-ap-bnk-06|AP-BNK-06]] to hold automated remittances[^r11].

### Ledgerline Entry and Dual Authorization
In [[man-ap-72|Ledgerline ERP]], segregation of duties mandates that the user who enters and saves changes via `bnk_save` cannot be the same user who executes `bnk_verify`[^r10]. After independent verification, a senior finance officer checks verification notes and enters the revised sort code and account number in Ledgerline ERP, followed by a second authorised signatory reviewing against the paper file to release the account hold[^r5]. The callback verification must be recorded on screen [[screen-ap-bnk-06|AP-BNK-06]] using service `bnk_verify` ([[services-ap-bnk|AP bnk services]]), and until recorded, system warning W-BNK-120 holds all disbursements to the supplier[^r6]. No payment run ([[sop-ap-003|SOP-AP-003 Supplier Payment Run]]) may include amended bank details that have not been fully checked and authorised[^r19].

### Records Retention
Complete physical verification packs—including the original notification, callback record sheet, and signed change authorisation form—must be retained in the supplier amendment binder in Manchester, while the Leeds unit posts original paperwork to Manchester and retains a scanned copy[^r8].

## Forms and screens

* Form NBC-F-113: Supplier Onboarding Checklist, check 6 requires call-back bank detail verification under SOP-AP-004[^r9].
* Screen [[screen-ap-bnk-06|AP-BNK-06]]: Supplier Bank Details Entry, used to execute `bnk_save`, `bnk_verify`, and `bnk_block`[^r6][^r10][^r11].
* Warning W-BNK-120: System warning that holds all disbursements to the supplier until `bnk_verify` is logged on [[screen-ap-bnk-06|AP-BNK-06]][^r6][^r7].
* Supplier amendment binder: Physical archive in Manchester containing verification packs and callback record sheets[^r8].

## Versions and conflicts

* Today's rule: SOP-AP-004 version 2.0 took effect on 2025-10-01, owned by AP manager [[user-mkowalski|Marta Kowalski]] and approved by financial controller [[user-gwhitaker|Grace Whitaker]][^r1].
* Older rule: SOP-AP-004 version 1.0 was issued on 2025-10-01 and superseded by version 2.0 on the same date[^r1].
* Kind: `superseded`[^r1].

## See also

* [[errors-bnk|Errors BNK]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-bnk-06|screen-ap-bnk-06 AP-BNK-06 Supplier Bank Details Entry]]
* [[services-ap-bnk|services-ap-bnk AP bnk services]]
* [[sop-ap-003|sop-ap-003 SOP-AP-003 Supplier Payment Run]]
* [[sop-pur-001|sop-pur-001 SOP-PUR-001 Supplier Onboarding]]
* [[user-gwhitaker|user-gwhitaker Grace Whitaker]]
* [[user-mkowalski|user-mkowalski Marta Kowalski]]

## References

[^r1]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 1, §1. Purpose
[^r2]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 3, §5. Procedure
[^r15]: 09_email_archive/2026/2026-02-15_Bank detail change requests.eml, Bank detail change requests
[^r4]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 2, §3. Responsibilities
[^r5]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 2, §3. Responsibilities
[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 25, Tips
[^r12]: 09_email_archive/2019/2019-05-02_Phishing e-mails pretending to be suppliers.eml, Subject: Phishing e-mails pretending to be suppliers
[^r13]: 09_email_archive/2019/2019-05-02_Phishing e-mails pretending to be suppliers.eml, Subject: Phishing e-mails pretending to be suppliers
[^r14]: 09_email_archive/2019/2019-05-02_Phishing e-mails pretending to be suppliers.eml, Subject: Phishing e-mails pretending to be suppliers
[^r16]: 09_email_archive/2026/2026-02-15_Bank detail change requests.eml, Bank detail change requests
[^r9]: 02_procedures/forms/Final_FINAL_onboarding checklist NBC-F-113.docx, Supplier Onboarding Checklist (NBC-F-113)
[^r3]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 3, §5. Procedure
[^r17]: 09_email_archive/2026/2026-02-15_Bank detail change requests.eml, Bank detail change requests
[^r7]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 4, What to do when something does not look right
[^r18]: 09_email_archive/2026/2026-02-15_Bank detail change requests.eml, Bank detail change requests
[^r11]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 25, Tips
[^r6]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 3, §5. Procedure
[^r19]: 09_email_archive/2026/2026-02-15_Bank detail change requests.eml, Bank detail change requests
[^r8]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 5, §6. Records
