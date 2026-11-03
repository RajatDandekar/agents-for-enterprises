---
title: "AP-GL-14 Gl Posting"
type: "screen"
slug: "screen-ap-gl-14"
summary: "Ledgerline screen AP-GL-14 for creating, querying, posting, and reversing Accounts Payable general ledger journal vouchers."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/gl_post.yaml", "04_service_definitions/accounts_payable/gl_query.yaml", "04_service_definitions/accounts_payable/gl_reverse.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-GL-14 |
| Module | Accounts payable |
| Menu path | Accounts payable > Gl posting |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Post service | gl_post (F9) |
| Query service | gl_query |
| Reverse service | gl_reverse |

Screen AP-GL-14 is the Ledgerline interface located under Accounts payable > Gl posting used to create, query, commit, and reverse journal voucher entries [^r1][^r10]. It is accessed by users assigned to roles AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN [^r10]. New entries commit balances directly to the nominal ledger across open accounting periods, while posted records can be inspected in read-only mode or cancelled using an offsetting entry [^r2][^r3][^r4][^r7].

| Field | Label | Type | Required | Description |
|---|---|---|---|---|
| Screen code | AP-GL-14 | String | N/A | Gl Posting screen identifier [^r1][^r10] |
| Menu path | Accounts payable > Gl posting | Navigation | N/A | Navigation path in Ledgerline [^r1][^r10] |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN | Role list | N/A | Authorised roles [^r10] |

## Fields

Screen AP-GL-14 contains header and line entry fields for recording general ledger movements [^r1][^r11].

* **JV NO** (`jv_no`): Journal voucher identifier, defined as mandatory in the screen dictionary but left blank when creating a new voucher entry, whereupon Ledgerline allocates the sequence number upon completion [^r1][^r6][^r11]. Entering a voucher reference allows retrieval of existing vouchers [^r8].
* **COMMENT** (`comment`): Optional text field for transaction remarks [^r1][^r11]. Accounts staff at Leeds and Manchester format this field with the site prefix followed by the supplier identifier [^r5].
* **JV DT** (`jv_dt`): Optional transaction date for the journal voucher [^r1][^r11]. The date entered must fall within an open accounting period for Northbridge Cycles [^r7].
* **ACCOUNT** (`acct_cd`): Optional nominal ledger account code [^r1][^r11].
* **AMOUNT** (`amount`): Optional numeric transaction amount [^r1][^r11].
* **REASON** (`reason`): Optional text field providing the administrative explanation required when executing a reversal [^r1][^r4][^r11].

## Keys and services

Screen AP-GL-14 relies on the [[services-ap-gl|AP gl services]] service group to execute read and write operations against the ledger [^r12][^r13][^r14][^r15].

* **Post (F9)**: Invokes write service `gl_post` [^r12][^r13]. It validates data across the screen, commits balances to the nominal ledger, generates a unique journal sequence, and populates JV NO [^r3][^r13].
* **Query**: Invokes read service `gl_query` [^r12][^r14]. It retrieves journal voucher records from the ledger using optional criteria entered in header fields such as `jv_dt`, `acct_cd`, and `amount`, presenting the retrieved line details in read-only mode and greying out fields to prevent modification [^r2][^r8][^r14].
* **Reverse**: Invokes write service `gl_reverse` (GL POSTING REVERSE) using stored procedure `sp_gl_reverse` [^r12][^r15]. It prompts for the current posting date and corrective explanation in REASON, generates an offsetting journal entry to nullify the previous transaction, and marks the original posting accordingly [^r4][^r9][^r15].

## Messages

Screen AP-GL-14 raises the following error codes:

* [[err-gl-0001|ERR-GL-0001]]: Gl Posting Not Found [^r12].
* [[err-gl-0007|ERR-GL-0007]]: Gl Posting Not In Draft (\<Status\>) [^r12].

## Versions and conflicts

* **Contradiction (JV NO requirement on entry)**: When entering a fresh journal voucher, the JV NO field is left blank and populated automatically upon posting, whereas the screen dictionary registers `jv_no` as mandatory (`MAN-AP-72`, p. 54 vs `MAN-SCR-72`, p. 7 and `MAN-AP-72`, p. 51) [^r1][^r6][^r11].

## See also

* [[err-gl-0001|ERR-GL-0001 Missing or Invalid Header Information]]
* [[err-gl-0007|ERR-GL-0007 Ledger Integrity Failure]]
* [[services-ap-gl|AP gl services]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 51, §16. Gl Posting (AP-GL-14)
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-GL-14 GL POSTING
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 52, Querying existing postings
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 53, Creating and posting a new entry
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 52, Buttons and services
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 54, Worked example: Gl Posting
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-GL-14 GL POSTING
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 54, Worked example: Gl Posting
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 55, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 54, Tips
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 7, AP-GL-14 GL POSTING
[^r13]: 04_service_definitions/accounts_payable/gl_post.yaml, whole file
[^r14]: 04_service_definitions/accounts_payable/gl_query.yaml, whole file
[^r15]: 04_service_definitions/accounts_payable/gl_reverse.yaml, whole file
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 55, Questions users ask
