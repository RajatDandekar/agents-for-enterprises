---
title: "QA-CAL-04 Calibration Entry"
type: "screen"
slug: "screen-qa-cal-04"
summary: "Ledgerline screen QA-CAL-04 maintains instrument calibration and renewal dates across Manchester and Leeds plants using services cal_save, cal_get, and cal_due."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/cal_due.yaml", "04_service_definitions/production/cal_get.yaml", "04_service_definitions/production/cal_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | QA-CAL-04 |
| Title | Calibration Entry |
| Module | Production > Calibration |
| Allowed roles | PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, SYS-ADMIN |
| Services | cal_save, cal_get, cal_due |
| Primary keys | F3 (cal_get), F8 (cal_save) |

Screen QA-CAL-04 is accessed from the Production > Calibration menu and maintains gauge calibration records across both the Manchester and Leeds plants [^r1]. It allows authorised users to retrieve calibration history, record completed internal checks, and view upcoming or overdue tool verifications [^r3][^r5][^r6][^r7]. Access is available to roles PRD-PLAN, PRD-SUP, QA-INSP, QA-MGR, and SYS-ADMIN [^r10].

## Fields

| Field | Label | Required | Description |
|---|---|---|---|
| `gauge_no` | GAUGE NO | Yes | Equipment or tool identifier [^r2][^r6][^r11]. |
| `cal_dt` | CAL DT | Yes | Date the physical calibration test was completed or last passed [^r2][^r3][^r7][^r11]. |
| `due_dt` | DUE DT | Yes | Next verification or calculated expiry point date [^r2][^r3][^r7][^r11]. |

To record an internal instrument check, the user opens QA-CAL-04, keys the equipment identifier into GAUGE NO, and invokes `cal_get` to populate registration details and inspection history [^r6]. The user enters the physical test completion date in CAL DT and the next verification date in DUE DT before committing the update via `cal_save` [^r7].

## Keys and services

Screen QA-CAL-04 operates three backend services from the [[services-prd-cal|PRD cal services]] group [^r11][^r12]:

* `cal_get` (F3): Retrieves the live gauge record by `gauge_no`, populating registration details, inspection history, CAL DT with the date last passed, and DUE DT with the calculated expiry point [^r3][^r6][^r11][^r14].
* `cal_save` (F8): Write service that commits updated calibration records (`gauge_no`, `cal_dt`, and `due_dt`) to central quality tables [^r4][^r7][^r11][^r12][^r15].
* `cal_due`: Read service invoked at endpoint `POST /ll72/svc/cal_due` with mandatory field `gauge_no` to query calibration due details, generating a list of instruments with approaching or overdue renewal dates on active lines across the works [^r5][^r9][^r11][^r13].

## Messages

* [[err-cal-0001|ERR-CAL-0001]]: Raised on the status line when the tool identifier entered in GAUGE NO cannot be found during retrieval [^r8][^r11].

## See also

* [[err-cal-0001|ERR-CAL-0001 Calibration Tool Not Found]]
* [[services-prd-cal|PRD cal services]]
* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]
* [[screen-qa-btt-03|QA-BTT-03 Battery End-Of-Line Test Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 44, §14. Calibration (QA-CAL-04)
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 45, Step by step
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 46, Step by step
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 47, Worked example
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 47, Worked example
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-CAL-04 CALIBRATION ENTRY
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 44, §14. Calibration (QA-CAL-04)
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-CAL-04 CALIBRATION ENTRY
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, cal_save CALIBRATION SAVE
[^r14]: 04_service_definitions/production/cal_get.yaml, whole file
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 46, Step by step
[^r15]: 04_service_definitions/production/cal_save.yaml, service: cal_save
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 47, Worked example
[^r13]: 04_service_definitions/production/cal_due.yaml, cal_due
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 47, Worked example
