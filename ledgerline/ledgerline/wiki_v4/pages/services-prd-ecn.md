---
title: "PRD ecn services"
type: "service-group"
slug: "services-prd-ecn"
summary: "Ledgerline production module services for managing, approving, and releasing engineering change notices on screen PRD-ECN-06."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/ecn_approve.yaml", "04_service_definitions/production/ecn_get.yaml", "04_service_definitions/production/ecn_release.yaml", "04_service_definitions/production/ecn_save.yaml", "04_service_definitions/production/ecn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Screen | PRD-ECN-06 |
| Associated procedure | SOP-PRD-002 |
| Available since | 7.1 |
| Services count | 5 |
| Protocol | POST |
| Authentication | X-LL-Session token |

The PRD ecn service group provides the backend API and database procedures managing engineering change notices (ECNs) in Ledgerline ERP 7.2 [^r16]. Executed directly or invoked from [[screen-prd-ecn-06|screen PRD-ECN-06]] during [[sop-prd-002|SOP-PRD-002]] workflows, these services allow staff to draft, query, sign off, and release revisions for production planning [^r2][^r3][^r5][^r6][^r10]. All five services require an authenticated session token in header `X-LL-Session` and role authorization, returning standardized envelopes with status codes, error codes, and messages [^r17][^r20][^r22][^r24][^r27][^r31][^r33][^r37].

## Services

### ecn_save
The `ecn_save` service is a write service available since version 7.1 that executes stored procedure `sp_ecn_save` to validate screen entries, create new drafts, or modify existing engineering change notices [^r2][^r11][^r30][^r33]. It is bound to function key F8 on screen PRD-ECN-06 and automatically generates a sequential `ECN NO` if left blank [^r2][^r10][^r30].

* **Endpoint:** `POST /ll72/svc/ecn_save` [^r30]
* **Source file:** `04_service_definitions/production/ecn_save.yaml` [^r30]
* **Required fields:** `itm_cd` (string), `change` (string), `eff_dt` (date) [^r11][^r32]
* **Optional fields:** `reason` (string) [^r11][^r32]
* **Errors:** [[err-itm-0011|ERR-ITM-0011]], ERR-ECN-0105, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r1][^r34][^r35]

### ecn_get
The `ecn_get` service is a read service introduced in version 7.1 that fetches a single engineering change record from the database using its unique identifier [^r3][^r12][^r21]. It corresponds to function key F3 on screen PRD-ECN-06 [^r10][^r21].

* **Endpoint:** `POST /ll72/svc/ecn_get` [^r21]
* **Source file:** `04_service_definitions/production/ecn_get.yaml` [^r21]
* **Required fields:** `ecn_no` (string) [^r12][^r23]
* **Optional fields:** None [^r23]
* **Errors:** ERR-ECN-0001, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r25]

### ecn_search
The `ecn_search` service is a read service available since version 7.1 that queries engineering change records using specified search criteria [^r4][^r13][^r36]. On screen PRD-ECN-06, it is mapped to keys F2 and Enter [^r10][^r36].

* **Endpoint:** `POST /ll72/svc/ecn_search` [^r37]
* **Source file:** `04_service_definitions/production/ecn_search.yaml` [^r36][^r37]
* **Required fields:** None [^r38]
* **Optional fields:** `itm_cd` (string), `change` (string), `eff_dt` (date), `status` (string) [^r13][^r38]
* **Errors:** [[err-itm-0011|ERR-ITM-0011]], ERR-ECN-0105, ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r37][^r39]

### ecn_approve
The `ecn_approve` service is a write service running stored procedure `sp_ecn_approve` to record technical sign-off on a saved draft and advance the document status [^r5][^r14][^r16][^r19]. It is accessed via function key F9 on screen PRD-ECN-06 [^r10][^r16].

* **Endpoint:** `POST /ll72/svc/ecn_approve` [^r16]
* **Source file:** `04_service_definitions/production/ecn_approve.yaml` [^r16]
* **Required fields:** `ecn_no` (string) [^r14][^r18]
* **Optional fields:** `comment` (string) [^r14][^r18]
* **Errors:** [[err-apr-0003|ERR-APR-0003]], [[err-apr-0004|ERR-APR-0004]] [^r8]

### ecn_release
The `ecn_release` service is a write service running stored procedure `sp_ecn_release` that moves an approved engineering change record to live status for production planning [^r6][^r15][^r26][^r29]. On screen PRD-ECN-06, it is initiated via function key F9 [^r10].

* **Endpoint:** `POST /ll72/svc/ecn_release` [^r26]
* **Source file:** `04_service_definitions/production/ecn_release.yaml` [^r26][^r29]
* **Required fields:** `ecn_no` (string) [^r15][^r28]
* **Optional fields:** `comment` (string) [^r28]
* **Errors:** ERR-ECN-0001, ERR-ECN-0007, ERR-ECN-0105, [[err-ecn-0220|ERR-ECN-0220]] [^r1][^r9][^r15][^r29]

## Versions and conflicts

* **Error reporting discrepancies between service definitions and user manuals:** The YAML service definition specifies ERR-ECN-0105 and [[err-itm-0011|ERR-ITM-0011]] for `ecn_save`, and ERR-ECN-0001, ERR-ECN-0007, and [[err-ecn-0220|ERR-ECN-0220]] for `ecn_release` [^r29][^r34]. In contrast, manual MAN-PRD-72 states that `ecn_save` returns ERR-ECN-0001 on database/network disruption and ERR-ECN-0007 on missing mandatory inputs, that `ecn_approve` raises [[err-apr-0003|ERR-APR-0003]] and [[err-apr-0004|ERR-APR-0004]], and that `ecn_release` returns ERR-ECN-0105 when unapproved [^r7][^r8][^r9]. (`contradiction`: `04_service_definitions/production/*.yaml` vs `MAN-PRD-72`, 2025-01-15) [^r7][^r8][^r9][^r29][^r34].

## See also

* [[screen-prd-ecn-06|screen-prd-ecn-06 (PRD-ECN-06 Engineering Change Entry)]]
* [[sop-prd-002|sop-prd-002 (SOP-PRD-002 Engineering Change (ECN))]]
* [[err-ecn-0220|err-ecn-0220 (ERR-ECN-0220 Open Work Orders on Revision)]]
* [[err-itm-0011|err-itm-0011 (ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE)]]
* [[err-apr-0003|err-apr-0003 (ERR-APR-0003 Self-approval not permitted)]]
* [[err-apr-0004|err-apr-0004 (ERR-APR-0004 Advance amount exceeds PO unbilled commitment)]]
* [[services-prd-bom|services-prd-bom (PRD bom services)]]
* [[services-prd-wo|services-prd-wo (PRD wo services)]]

## References

[^r16]: 04_service_definitions/production/ecn_approve.yaml, service: ecn_approve
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 30, Screen layout
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 30, Screen layout
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 30, Screen layout
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 30, Screen layout
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 22, PRD-ECN-06 ENGINEERING CHANGE ENTRY
[^r17]: 04_service_definitions/production/ecn_approve.yaml, auth
[^r20]: 04_service_definitions/production/ecn_approve.yaml, response.envelope
[^r22]: 04_service_definitions/production/ecn_get.yaml, auth
[^r24]: 04_service_definitions/production/ecn_get.yaml, response.envelope
[^r27]: 04_service_definitions/production/ecn_release.yaml, auth
[^r31]: 04_service_definitions/production/ecn_save.yaml, whole file
[^r33]: 04_service_definitions/production/ecn_save.yaml, response
[^r37]: 04_service_definitions/production/ecn_search.yaml, auth
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 58, ecn_save ENGINEERING CHANGE SAVE
[^r30]: 04_service_definitions/production/ecn_save.yaml, whole file
[^r32]: 04_service_definitions/production/ecn_save.yaml, request
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 9
[^r34]: 04_service_definitions/production/ecn_save.yaml, errors
[^r35]: 04_service_definitions/production/ecn_save.yaml, common_errors
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 58, ecn_get ENGINEERING CHANGE GET
[^r21]: 04_service_definitions/production/ecn_get.yaml, service: ecn_get
[^r23]: 04_service_definitions/production/ecn_get.yaml, request.fields
[^r25]: 04_service_definitions/production/ecn_get.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 30, Screen layout
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 58, ecn_search ENGINEERING CHANGE LIST
[^r36]: 04_service_definitions/production/ecn_search.yaml, service
[^r38]: 04_service_definitions/production/ecn_search.yaml, request.fields
[^r39]: 04_service_definitions/production/ecn_search.yaml, errors
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 58, ecn_approve ENGINEERING CHANGE APPROVE
[^r19]: 04_service_definitions/production/ecn_approve.yaml, procedures
[^r18]: 04_service_definitions/production/ecn_approve.yaml, request.fields
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 32, Messages
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 58, ecn_release ENGINEERING CHANGE RELEASE
[^r26]: 04_service_definitions/production/ecn_release.yaml, service: ecn_release
[^r29]: 04_service_definitions/production/ecn_release.yaml, errors
[^r28]: 04_service_definitions/production/ecn_release.yaml, request.fields
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 32, Messages
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 32, Messages
