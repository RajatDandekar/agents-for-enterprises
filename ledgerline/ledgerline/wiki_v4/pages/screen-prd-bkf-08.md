---
title: "PRD-BKF-08 Backflush"
type: "screen"
slug: "screen-prd-bkf-08"
summary: "Production screen for querying, posting, and reversing works order backflush inventory movements and issuing finished goods movement tickets."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/bkf_get.yaml", "04_service_definitions/production/bkf_post.yaml", "04_service_definitions/production/bkf_reverse.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | PRD-BKF-08 |
| Name | Backflush |
| Menu path | Production > Backflush |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Services | bkf_post, bkf_get, bkf_reverse |
| Status | current |

Screen PRD-BKF-08 is the Ledgerline interface used to retrieve order details, post backflushes, and reverse backflush transactions for production works orders [^r1][^r4][^r10]. Located under Production > Backflush, it is accessible to roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r1][^r8]. Posting relieves line inventory, clears open quantities, and automatically prints a finished goods movement ticket to the line printer [^r3].

| Field | Value |
|---|---|
| Screen | PRD-BKF-08 |
| Name | Backflush |
| Menu path | Production > Backflush |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Services | bkf_post, bkf_get, bkf_reverse |
| Status | current |

## Fields

* **WO NO** (`wo_no`): Mandatory string field used to specify the works order number [^r1][^r8][^r11][^r13].
* **COMMENT** (`comment`): Optional field on the screen [^r1][^r8]. Northbridge Cycles traceability policy mandates recording shift details or testing station references here [^r7].
* **REASON** (`reason`): Optional screen field in the interface definition, but entering an explanation is mandatory before executing a reversal [^r1][^r5][^r8][^r13].

## Keys and services

* **Get** (`F3`): Invokes the read service `bkf_get` (via endpoint `POST /ll72/svc/bkf_get`) using required field `wo_no` to retrieve parent part identity, remaining open quantity, default expected component quantities, and transaction history [^r1][^r2][^r4][^r9][^r11].
* **Post** (`F9`): Calls write service `bkf_post` via stored procedure `sp_bkf_post` to evaluate inventory in line stores, relieve component stock, clear open quantities, and trigger printing of a finished goods movement ticket to the line printer [^r1][^r3][^r9][^r12].
* **Reverse**: Calls write service `bkf_reverse` (via endpoint `POST /ll72/svc/bkf_reverse`) using `wo_no` and `reason` to undo bookings [^r1][^r4][^r9][^r13].

All transactions provided through the screen are handled by [[services-prd-bkf|PRD bkf services]] [^r10].

## Messages

The screen displays error messages in a dedicated status strip located at the foot of the screen [^r6]. The screen validates against:

* [[err-bkf-0001|ERR-BKF-0001]]: Works order invalid or not in valid state for backflush [^r9].
* [[err-bkf-0007|ERR-BKF-0007]]: Component inventory shortage during backflush [^r9].

## Versions and conflicts

* **Contradiction**: In the screen PRD-BKF-08 user procedure, entering an explanation in the `REASON` field is mandatory before `bkf_reverse` will execute, whereas the underlying service schema `bkf_reverse.yaml` specifies `reason` as an optional field [^r5][^r13].

## See also

* [[services-prd-bkf|PRD bkf services]]
* [[err-bkf-0001|ERR-BKF-0001: Works order invalid or not in valid state for backflush]]
* [[err-bkf-0007|ERR-BKF-0007: Component inventory shortage during backflush]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[screen-prd-opr-04|PRD-OPR-04 Operation Confirmation Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 15, §6. Backflush (PRD-BKF-08)
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 55, §6. Production services
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, PRD-BKF-08 BACKFLUSH
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 16, Adding narrative and posting the transaction
[^r11]: 04_service_definitions/production/bkf_get.yaml, service: bkf_get
[^r13]: 04_service_definitions/production/bkf_reverse.yaml, service
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 19, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 16, Retrieving the works order details
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, PRD-BKF-08 BACKFLUSH
[^r12]: 04_service_definitions/production/bkf_post.yaml, service: bkf_post
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 17, Messages
