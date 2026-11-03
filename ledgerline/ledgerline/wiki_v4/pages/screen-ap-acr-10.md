---
title: "AP-ACR-10 Grni Accrual"
type: "screen"
slug: "screen-ap-acr-10"
summary: "Ledgerline screen for scanning unmatched receipts, generating GRNI accrual batches, retrieving records, and posting accrual reversals across warehouses."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/acr_get.yaml", "04_service_definitions/accounts_payable/acr_reverse.yaml", "04_service_definitions/accounts_payable/acr_run.yaml", "04_service_definitions/service_index.csv"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-ACR-10 |
| Screen title | GRNI Accrual |
| Module | Accounts payable |
| Menu path | Accounts payable > Grni accrual |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Services | acr_run, acr_get, acr_reverse |

Screen AP-ACR-10 (GRNI Accrual) is the Ledgerline interface used to calculate, inspect, and reverse Goods Received Not Invoiced (GRNI) accruals across Northbridge Cycles' Manchester and Leeds sites [^r1][^r4][^r9]. It initiates background runs that scan unmatched purchase receipts, post calculated accrual journal batches split by purchase category, and reverse existing accruals when required [^r3][^r4][^r5][^r7]. Access to the screen via the Accounts payable menu is restricted to AP-CLERK, AP-MGR, FIN-CTRL, and SYS-ADMIN roles [^r1][^r9].

| Field | Label | Type | Description |
|---|---|---|---|
| Screen code | AP-ACR-10 | — | Screen identifier [^r1][^r9] |
| Screen title | GRNI Accrual | — | Screen name [^r9] |
| Menu path | Accounts payable > Grni accrual | — | Navigation path [^r1][^r9] |
| Roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN | — | Permitted user roles [^r9] |

## Fields

Screen AP-ACR-10 contains the following fields:

* `acr_no` (ACR NO): Mandatory field holding the accrual run reference number [^r2]. When generating a new run, this field must be left empty so that Ledgerline can populate it with the next sequential reference number [^r4][^r5]. It is populated manually when retrieving existing records [^r6].
* `comment` (COMMENT): Optional narrative field [^r2]. A descriptive comment must be entered prior to running a new accrual calculation [^r4].
* `reason` (REASON): Optional field on entry, but requires a descriptive text entry prior to executing a reversal [^r2][^r7].

## Keys and services

AP-ACR-10 connects to three backend services from the [[services-ap-acr|AP acr services]] group, available since version 7.0 [^r1][^r13][^r14]:

* `acr_run`: Write service initiated by action button `acr_run` (GRNI ACCRUAL RUN) [^r3][^r12][^r14]. With `acr_no` left blank and narrative supplied in `comment`, it scans unmatched stock receipts across Manchester and Leeds, assigns the next sequential `acr_no`, displays calculated receipt totals grouped by purchase category, and creates an unposted accrual journal batch [^r3][^r4][^r5].
* `acr_get`: Read service (POST `/ll72/svc/acr_get`) initiated by pressing `acr_get` (GRNI ACCRUAL GET) [^r6][^r10][^r13]. It retrieves existing accrual records, goods receipts, and accrued lines matching the entered `acr_no` [^r6][^r10].
* `acr_reverse`: Write service (POST `/ll72/svc/acr_reverse`) initiated by pressing `acr_reverse` (GRNI ACCRUAL REVERSE) [^r7][^r11][^r14]. It requires a descriptive reason in the `reason` field to generate a reversing journal and clear the accrual commitment [^r7].

## Messages

The screen raises error [[err-acr-0001|ERR-ACR-0001]] when an accrual calculation or reversal cannot proceed [^r8]. This occurs when records are locked, accounting periods are closed, the `comment` or `reason` fields are missing when required, or an invalid `acr_no` is entered [^r8].

## See also

* [[services-ap-acr|AP acr services]]
* [[err-acr-0001|ERR-ACR-0001: Accrual execution or reversal failed]]
* [[screen-ap-mat-02|AP-MAT-02 Three-Way Match]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[screen-ap-gl-14|AP-GL-14 Gl Posting]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 32, §11. Grni Accrual (AP-ACR-10)
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 34, Generating a new accrual run:
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 3, AP-ACR-10 GRNI ACCRUAL
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 33, Screen layout and fields
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 34, Generating a new accrual run:
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 36, Questions users ask
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 33, Screen layout and fields
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 34, Retrieving an existing accrual record:
[^r13]: 04_service_definitions/service_index.csv, sheet csv, row acr_get, SHEET csv
[^r14]: 04_service_definitions/service_index.csv, sheet csv, row acr_reverse, SHEET csv
[^r12]: 04_service_definitions/accounts_payable/acr_run.yaml, whole file
[^r10]: 04_service_definitions/accounts_payable/acr_get.yaml, screen
[^r11]: 04_service_definitions/accounts_payable/acr_reverse.yaml, screen
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 35, Messages
