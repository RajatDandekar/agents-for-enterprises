---
title: "AP-PER-11 Ap Period"
type: "screen"
slug: "screen-ap-per-11"
summary: "Ledgerline screen for listing, checking status, opening, and closing Accounts Payable accounting intervals."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-002 Period Close v3.0.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/per_close.yaml", "04_service_definitions/accounts_payable/per_list.yaml", "04_service_definitions/accounts_payable/per_open.yaml", "04_service_definitions/accounts_payable/per_status.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-PER-11 |
| Name | Ap Period |
| Menu path | Accounts payable > Ap period |
| Authorised roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN |
| Read services | per_list, per_status |
| Write services | per_open, per_close |
| Status | current |

Screen AP-PER-11 (Ap Period) manages the operational posting states of Accounts Payable accounting intervals in Ledgerline [^r4][^r13]. Accessed under Accounts payable > Ap period, it allows authorised roles to list, check status, open, and close ledger periods [^r4][^r5][^r6][^r7][^r8][^r13]. During monthly financial close, the AP manager runs the period close on this screen on the afternoon of working day 3 [^r1].

| Field | Value |
|---|---|
| Screen code | AP-PER-11 [^r4][^r13] |
| Name | Ap Period [^r4][^r13] |
| Menu location | Accounts payable > Ap period [^r4][^r13] |
| Permitted roles | AP-CLERK, AP-MGR, FIN-CTRL, SYS-ADMIN [^r13] |
| Key services | per_list, per_status, per_open, per_close [^r5][^r6][^r7][^r8][^r16][^r18][^r19][^r20] |

## Fields

Screen AP-PER-11 contains two optional string fields [^r4][^r14]:

* **PERIOD**: Optional string input used to enter an accounting interval code or label [^r4][^r6][^r7][^r8][^r14].
* **COMMENT**: Optional string input used to record explanatory remarks when opening an interval or closing notations when sealing an interval [^r4][^r7][^r8][^r14].

Users must verify on screen that all open documents are resolved and that the ledger period being concluded matches the closing period while the subsequent period is set to open [^r3].

## Keys and services

Screen actions map to services in the [[services-ap-per|AP per services]] group:

* **per_list**: Calls the read service `per_list` (POST `/ll72/svc/per_list`) to populate the grid with all configured accounting intervals and their operational posting states (open, closed, or future) [^r5][^r18].
* **per_status**: Calls the read service `per_status` (POST `/ll72/svc/per_status`) using mandatory field `period` to inspect the posting state of the specified interval [^r6][^r20].
* **per_open**: Executes the write service `per_open` (POST `/ll72/svc/per_open`) using the identifier in PERIOD and the remark in COMMENT to open an accounting period [^r7][^r19].
* **per_close**: Executes the write service `per_close` (POST `/ll72/svc/per_close`) using the period code in PERIOD and notations in COMMENT to close the accounting interval [^r8][^r16]. The service verifies that no unposted journals or incomplete allocations remain [^r8].

## Messages

The screen and its underlying services raise codes documented in [[errors-per|ERR-PER Error Codes]]:

* **ERR-PER-0001** (*Ap Period Not Found*): Raised when the PERIOD identifier is blank or does not exist in the system [^r9][^r15][^r17][^r21].
* [[err-per-0010|ERR-PER-0010]] (*Unposted Documents In Period*): Raised during close if any batches, journals, or matchings remain unposted or suspended [^r2][^r15][^r17].
* **ERR-PER-0011** (*Grni Accrual Not Run*): Raised by the close service if the GRNI accrual run has not been completed [^r15][^r17].
* **ERR-PER-0801** (*Ap Period Closed (<Status>)*): Raised when an operation targets an interval that is already closed [^r15][^r17].

## Versions and conflicts

* **ERR-PER-0010 and ERR-PER-0011 meanings**: Under the `per_close` service definition and screen reference manual, [[err-per-0010|ERR-PER-0010]] denotes unposted documents remaining in the period and ERR-PER-0011 denotes that GRNI accruals have not been run [^r2][^r15][^r17]. In the user manual text, ERR-PER-0010 is described as opening an already open or permanently sealed period, or closing an already closed interval, while ERR-PER-0011 is described as closing an already closed or unopened period, or opening an invalid interval [^r9][^r11][^r12] (`contradiction`).
* **ERR-PER-0001 trigger**: The service definition, screen manual, and user manual message list define ERR-PER-0001 as period not found or blank [^r9][^r15][^r17][^r21]. The user manual worked example states that pressing `per_status` halts with ERR-PER-0001 if unposted purchase batches remain pending [^r11] (`contradiction`).
* **ERR-PER-0801 trigger**: In the service definition and screen manual, ERR-PER-0801 indicates the period is closed [^r15][^r17]. The user manual tips section states that ERR-PER-0801 signals unposted purchase ledger transactions preventing closing, or insufficient user authorisation rights to maintain periods [^r10] (`contradiction`).

## See also

* [[sop-ap-002|SOP-AP-002 Accounts Payable Period Close]]
* [[services-ap-per|AP per services]]
* [[err-per-0010|ERR-PER-0010 Documents unposted at period close]]
* [[errors-per|ERR-PER Error Codes]]
* [[screen-ap-acr-10|AP-ACR-10 Grni Accrual]]

## References

[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 36, §12. Ap Period (AP-PER-11)
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-PER-11 AP PERIOD
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 37, Viewing existing period records
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 37, Checking a specific period status
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Opening an accounting period
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Closing an accounting period
[^r1]: 02_procedures/SOP-AP-002 Period Close v3.0.pdf, p. 3, §5. Procedure
[^r16]: 04_service_definitions/accounts_payable/per_close.yaml, service: per_close
[^r18]: 04_service_definitions/accounts_payable/per_list.yaml, whole file
[^r19]: 04_service_definitions/accounts_payable/per_open.yaml, whole file
[^r20]: 04_service_definitions/accounts_payable/per_status.yaml, service: per_status
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-PER-11 AP PERIOD
[^r3]: 02_procedures/SOP-AP-002 Period Close v3.0.pdf, p. 4, What to check on screen
[^r9]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 38, Messages
[^r15]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 9, AP-PER-11 AP PERIOD
[^r17]: 04_service_definitions/accounts_payable/per_close.yaml, errors
[^r21]: 04_service_definitions/accounts_payable/per_status.yaml, errors
[^r2]: 02_procedures/SOP-AP-002 Period Close v3.0.pdf, p. 3, §5. Procedure
[^r11]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 39, Worked example
[^r12]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 40, Worked example
[^r10]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 39, Tips
