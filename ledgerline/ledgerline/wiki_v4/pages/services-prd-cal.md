---
title: "PRD cal services"
type: "service-group"
slug: "services-prd-cal"
summary: "Production calibration services cal_get, cal_save, and cal_due supporting gauge calibration entry on screen QA-CAL-04."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/cal_due.yaml", "04_service_definitions/production/cal_get.yaml", "04_service_definitions/production/cal_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PRD |
| Screen | QA-CAL-04 |
| Services | cal_get, cal_save, cal_due |
| Status | current |
| Version | Ledgerline 7.0+ |

The PRD calibration service group provides services to query, validate, and record measuring equipment inspection details in Ledgerline [^r1][^r2][^r11]. Bound to screen [[screen-qa-cal-04|QA-CAL-04]], these endpoints maintain instrument records, calculate renewal deadlines, and flag overdue measuring tools across the plant [^r3][^r5][^r7]. All services execute under module PRD and require an authorized session token in the X-LL-Session request header [^r11][^r12][^r17][^r23].

## Services

### cal_due

The read service `cal_due` (CALIBRATION DUE) queries the active register and retrieves due calibrations for equipment that is overdue or approaching renewal on screen [[screen-qa-cal-04|QA-CAL-04]] [^r3][^r10][^r11]. It can list all measuring equipment across the plant scheduled for testing or booked out to workstations [^r5].

* **Endpoint**: `POST /ll72/svc/cal_due` [^r11]
* **Source file**: `04_service_definitions/production/cal_due.yaml` [^r11]
* **Required fields**: `gauge_no` (string, GAUGE NO) [^r13]
* **Optional fields**: None [^r13]
* **Response**: Envelope returning `rc` ('S | W | E'), `err_cd` ('error code when rc is E'), `msg` ('short message in capitals'), and `data` ('result') containing `gauge_no` and registered `due_dt` [^r3][^r14]
* **Errors**: [[err-cal-0001|ERR-CAL-0001]] (CALIBRATION NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r15]

### cal_get

The read service `cal_get` (CALIBRATION GET) queries the quality database using a tool identifier entered on screen [[screen-qa-cal-04|QA-CAL-04]] [^r1][^r7][^r9]. It retrieves current registration details, prior inspection records, and populates `cal_dt` and `due_dt` [^r1][^r4].

* **Endpoint**: `POST /ll72/svc/cal_get` [^r16]
* **Source file**: `04_service_definitions/production/cal_get.yaml` [^r16]
* **Required fields**: `gauge_no` (string, GAUGE NO) [^r18]
* **Optional fields**: None [^r18]
* **Response**: Envelope returning `rc`, `err_cd`, `msg`, and `data` [^r19]
* **Errors**: [[err-cal-0001|ERR-CAL-0001]] (CALIBRATION NOT FOUND), ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r20][^r21]

### cal_save

The write service `cal_save` (CALIBRATION SAVE) validates tool calibration inputs and writes updated calibration and due dates to central quality tables [^r2][^r8]. Bound to screen [[screen-qa-cal-04|QA-CAL-04]], it executes database procedure `sp_cal_save`, clears input fields, and displays a confirmation message [^r6][^r7][^r8][^r25].

* **Endpoint**: `POST /ll72/svc/cal_save` [^r23]
* **Source file**: `04_service_definitions/production/cal_save.yaml` [^r22]
* **Required fields**: `gauge_no` (string, GAUGE NO), `cal_dt` (date, CAL DT), and `due_dt` (date, DUE DT) [^r8][^r24]
* **Optional fields**: None [^r24]
* **Response**: Envelope returning `rc`, `err_cd`, `msg`, and `data` [^r25]
* **Errors**: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r26]

## See also

* [[screen-qa-cal-04|QA-CAL-04 Calibration Entry]]
* [[err-cal-0001|ERR-CAL-0001 Calibration Tool Not Found]]
* [[services-prd-tool|PRD tool services]]
* [[services-prd-qin|PRD qin services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 45, Step by step
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 46, Step by step
[^r11]: 04_service_definitions/production/cal_due.yaml, cal_due
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 46, Step by step
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 48, Questions users ask
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 31, QA-CAL-04 CALIBRATION ENTRY
[^r12]: 04_service_definitions/production/cal_due.yaml, auth
[^r17]: 04_service_definitions/production/cal_get.yaml, auth
[^r23]: 04_service_definitions/production/cal_save.yaml, service: cal_save
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, cal_due CALIBRATION DUE
[^r13]: 04_service_definitions/production/cal_due.yaml, request.fields
[^r14]: 04_service_definitions/production/cal_due.yaml, response.envelope
[^r15]: 04_service_definitions/production/cal_due.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, cal_get CALIBRATION GET
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 47, Worked example
[^r16]: 04_service_definitions/production/cal_get.yaml, whole file
[^r18]: 04_service_definitions/production/cal_get.yaml, request.fields
[^r19]: 04_service_definitions/production/cal_get.yaml, response.envelope
[^r20]: 04_service_definitions/production/cal_get.yaml, errors
[^r21]: 04_service_definitions/production/cal_get.yaml, common_errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 61, cal_save CALIBRATION SAVE
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 47, Worked example
[^r25]: 04_service_definitions/production/cal_save.yaml, response
[^r22]: 04_service_definitions/production/cal_save.yaml, service: cal_save
[^r24]: 04_service_definitions/production/cal_save.yaml, request.fields
[^r26]: 04_service_definitions/production/cal_save.yaml, common_errors
