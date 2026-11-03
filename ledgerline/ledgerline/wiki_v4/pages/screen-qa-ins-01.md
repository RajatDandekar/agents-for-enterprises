---
title: "QA-INS-01 Incoming Inspection Entry"
type: "screen"
slug: "screen-qa-ins-01"
summary: "Screen for recording incoming goods verification, sample inspections, and stock dispositions against goods receipt notes."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/qin_get.yaml", "04_service_definitions/production/qin_post.yaml", "04_service_definitions/production/qin_reject.yaml", "04_service_definitions/production/qin_save.yaml", "04_service_definitions/production/qin_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | QA-INS-01 |
| Module | Production |
| Menu path | Production > Incoming inspection |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Key services | qin_save, qin_get, qin_search, qin_post, qin_reject |

Screen QA-INS-01 is the Ledgerline interface used by inspectors to perform incoming goods verification against goods receipt notes [^r1][^r4]. It captures sample test results based on the acceptance quality limit (AQL) defined in [[pol-qua-005|POL-QUA-005]] §3.1 and records individual open-circuit voltage measurements for tested battery packs [^r1][^r2]. Posting a completed inspection releases accepted stock from quarantine staging to general racking, while rejections freeze stock balances and update supplier quality records [^r3][^r7][^r8].

| Field | Value |
|---|---|
| Screen code | QA-INS-01 |
| Module | Production |
| Menu path | Production > Incoming inspection |
| Authorized roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Key services | qin_save, qin_get, qin_search, qin_post, qin_reject |

## Fields

Screen QA-INS-01 is accessed under menu path Production > Incoming inspection by roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r4][^r12].

The screen includes the following fields:
* **GRN NO (`grn_no`)**: Mandatory goods receipt note reference [^r5][^r21][^r23].
* **QIN NO (`qin_no`)**: Mandatory inspection document number [^r5][^r15][^r17][^r23].
* **SAMPLE QTY (`sample_qty`)**: Mandatory quantity of units inspected under the sampling plan [^r5][^r21][^r23].
* **AQL (`aql`)**: Optional acceptable quality level value [^r5][^r21][^r23].
* **PASS/FAIL (`result`)**: Optional field indicating inspection disposition; when set to fail, the **REASON** field becomes mandatory to record the fault code [^r5][^r6][^r21][^r23].
* **REASON (`reason`)**: Dropdown code field for logging rejection reasons [^r5][^r6][^r23].
* **STATUS (`status`)**: Optional display field showing record state, such as draft, passed, or rejected [^r5][^r7][^r8][^r23].
* **COMMENT (`comment`)**: Optional descriptive notes [^r5][^r17][^r23].

For tested battery packs, individual open-circuit voltage entry lines are required [^r2]. Lines cannot be edited once `qin_post` has updated the status to indicate completion [^r11].

## Keys and services

Screen QA-INS-01 interfaces with the [[services-prd-qin|PRD qin services]] group (`qin_save`, `qin_get`, `qin_search`, `qin_post`, and `qin_reject`) via the following function keys [^r4][^r13][^r14]:

* **Save (F8)**: Invokes backend write service `qin_save` (`POST /ll72/svc/qin_save`) using mandatory fields `grn_no` and `sample_qty`, and optional fields `aql` and `result` [^r13][^r20][^r21].
* **Get (F3)**: Executes read service `qin_get` (`POST /ll72/svc/qin_get`) to retrieve records by `qin_no` [^r13][^r15].
* **Search (F2 / Enter)**: Calls service `qin_search` to list inspection entries matching `grn_no`, `sample_qty`, `aql`, or `status` [^r13][^r22].
* **Post (F9)**: Calls write service `qin_post` (`POST /ll72/svc/qin_post`) with required field `qin_no` and optional field `comment` [^r13][^r16][^r17]. Executing `qin_post` updates `status` to passed, closes the record, and generates an inventory transfer instruction moving the batch from quarantine staging to regular stores racking [^r7].
* **Reject (Shift+F9)**: Invokes write service `qin_reject`, which marks a line as failed, locks the stock balance in the quarantine store, updates `status` to rejected, and records the event on the supplier quality ledger [^r3][^r8][^r13][^r19].

## Messages

* **ERR-QIN-0007**: Returned during posting if the inspection record is not in draft status [^r18].
* **ERR-QIN-0230**: Raised during `qin_post` if `sample_qty` is below the required AQL plan, if `PASS/FAIL` or `SAMPLE QTY` is left blank, or if the inspection record was never saved [^r10][^r18].
* **W-QIN-231**: Warning triggered when posting an inspection passed with concession, when executing `qin_reject` for non-critical defects, or when the sample failure rate falls close to the agreed tolerance band to prompt review before finalising quarantine [^r8][^r9][^r18].

## Versions and conflicts

* **Mandatory status of REASON**: In step-by-step procedure rules, selecting fail in PASS/FAIL makes the REASON dropdown mandatory to capture the fault code [^r6]. Screen layout definitions list REASON as an optional field alongside comment and status [^r5][^r23]. (`contradiction` | MAN-PRD-72 v7.2.3, p. 35 vs. MAN-PRD-72 v7.2.3, p. 33 and MAN-SCR-72 v7.2.3, p. 31).

## See also

* [[sop-qua-001|SOP-QUA-001 Incoming Inspection]]
* [[pol-qua-005|POL-QUA-005 Quality Policy]]
* [[services-prd-qin|PRD qin services]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]

## References

[^r1]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 3, §5. Procedure
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 33, §11. Incoming Inspection (QA-INS-01)
[^r2]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r3]: 02_procedures/SOP-QUA-001 Incoming Inspection v2.0.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 35, Step by step
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 35, Step by step
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-INS-01 INCOMING INSPECTION ENTRY
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 33, §11. Incoming Inspection (QA-INS-01)
[^r21]: 04_service_definitions/production/qin_save.yaml, request.fields
[^r23]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-INS-01 INCOMING INSPECTION ENTRY
[^r15]: 04_service_definitions/production/qin_get.yaml, whole file
[^r17]: 04_service_definitions/production/qin_post.yaml, request.fields
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 35, Step by step
[^r11]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 37, Questions users ask
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, QA-INS-01 INCOMING INSPECTION ENTRY
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 59, qin_save INCOMING INSPECTION SAVE
[^r20]: 04_service_definitions/production/qin_save.yaml, whole file
[^r22]: 04_service_definitions/production/qin_search.yaml, service: qin_search
[^r16]: 04_service_definitions/production/qin_post.yaml, whole file
[^r19]: 04_service_definitions/production/qin_reject.yaml, screen
[^r18]: 04_service_definitions/production/qin_post.yaml, errors
[^r10]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 37, Questions users ask
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 37, Questions users ask
