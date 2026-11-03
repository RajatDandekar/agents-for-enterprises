---
title: "ERR-BTT and ERR-CAL error codes"
type: "error-list"
slug: "errors-prd"
summary: "Reference list of production module Ledgerline error codes across battery testing, calibration, item verification, cost centres, maintenance orders, and engineering changes."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "04_service_definitions/production/ecn_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | Production (PRD) |
| System | Ledgerline ERP |
| Document | MAN-PRD-72 |
| Version | 7.2.3 |
| Type | Error list |
| Status | current |

This page catalogues production module error codes encountered across battery testing, calibration, item lookups, maintenance orders, cost allocation, and engineering changes in [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]. It details validation failures and record-locking constraints raised during Ledgerline ERP transactions as of 26 October 2026. Production operators and quality technicians encounter these codes during shop floor entry, equipment calibration, and maintenance processing.

### ERR-BTT-0001
* **Message:** Mandatory validation failure on battery test record [^r1].
* **Cause:** Required measurement fields are missing or corrupt, or a serial number is not recognised on the shop floor schedule [^r1].
* **Remedy:** Verify all mandatory measurement inputs and ensure the serial number exists on the active shop floor schedule [^r1].
* **Raised by:** [[services-prd-btt|btt_save]] [^r1].

### ERR-BTT-0110
* **Message:** Open circuit voltage discrepancy [^r2].
* **Cause:** The value entered in OCV (V) violates format rules or physical bounds defined for the pack type [^r2].
* **Remedy:** Recheck format specifications and physical limits for the battery pack type before re-entering OCV (V) [^r2].
* **Raised by:** Battery end-of-line testing transactions [^r2].

### ERR-BTT-0120
* **Message:** Internal resistance validation failure [^r3].
* **Cause:** IR (MOHM) exceeds operational limits, indicates an open circuit, or fails pack sanity checks [^r3].
* **Remedy:** Check pack connectivity and re-enter measured resistance within operational limits [^r3].
* **Raised by:** Battery end-of-line testing transactions [^r3].

### ERR-CAL-0001
* **Message:** Calibration tool validation failure (see [[err-cal-0001|ERR-CAL-0001 Calibration Tool Not Found]]) [^r5].
* **Cause:** GAUGE NO is absent from the master equipment register, marked as scrapped or decommissioned, or CAL DT and DUE DT contain contradictory or invalid dates [^r5].
* **Remedy:** Ensure the gauge is active in the master equipment register and verify that CAL DT precedes DUE DT with valid calendar dates [^r5].
* **Raised by:** cal_get or cal_save in [[services-prd-cal|PRD cal services]] [^r5].

### ERR-CC-0009
* **Message:** Invalid cost centre code (see [[err-cc-0009|ERR-CC-0009]]) [^r6].
* **Cause:** The cost centre code does not exist in general ledger master tables or is inactive for engineering allocations [^r6].
* **Remedy:** Select an active general ledger cost centre valid for engineering allocations [^r6].
* **Raised by:** Production maintenance and cost allocation entries [^r6].

### ERR-ECN-0001
* **Message:** ENGINEERING CHANGE NOT FOUND [^r9].
* **Cause:** The requested engineering change notice cannot be found [^r9].
* **Remedy:** Verify that the ECN number entered on [[screen-prd-ecn-06|PRD-ECN-06 Engineering Change Entry]] exists in the system [^r9].
* **Raised by:** ecn_get in [[services-prd-ecn|PRD ecn services]] [^r9].

### ERR-ITM-0011
* **Message:** ITEM NOT FOUND OR INACTIVE (see [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]) [^r4].
* **Cause:** The code entered in ITEM CD does not exist in the central item master, or is inactive, obsolete, or not flagged as a manufactured battery assembly [^r4].
* **Remedy:** Validate that the item code exists in the central item master, remains active, and is marked as a manufactured battery assembly [^r4].
* **Raised by:** Battery test entry services [^r4].

### ERR-MNO-0001
* **Message:** Maintenance order not found [^r7].
* **Cause:** The maintenance order reference keyed into MNO NO was not found during execution of the service [^r7].
* **Remedy:** Confirm the order number on [[screen-prd-mnt-07|PRD-MNT-07 Maintenance Order Entry]] and re-execute the search [^r7].
* **Raised by:** MAINTENANCE ORDER GET in [[services-prd-mnt|PRD mnt services]] [^r7].

### ERR-MNO-0801
* **Message:** Maintenance order edit lock or closed [^r8].
* **Cause:** Attempting to edit, save, or close an order that already has its STATUS set to closed, or the record is locked by another terminal or background process [^r8].
* **Remedy:** Ensure the order is not closed and wait for other user terminals or background processes to release the lock [^r8].
* **Raised by:** Maintenance order update services [^r8].

## See also
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[err-cal-0001|ERR-CAL-0001 Calibration Tool Not Found]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-cc-0009|ERR-CC-0009]]
* [[screen-qa-btt-03|QA-BTT-03 Battery End-Of-Line Test Entry]]
* [[screen-qa-cal-04|QA-CAL-04 Calibration Entry]]
* [[screen-prd-mnt-07|PRD-MNT-07 Maintenance Order Entry]]
* [[screen-prd-ecn-06|PRD-ECN-06 Engineering Change Entry]]
* [[services-prd-btt|PRD btt services]]
* [[services-prd-cal|PRD cal services]]
* [[services-prd-ecn|PRD ecn services]]
* [[services-prd-mnt|PRD mnt services]]
* [[errors-wo|ERR-WO error codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 42, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 43, Messages
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 43, Messages
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 46, Messages
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 64, Messages
[^r9]: 04_service_definitions/production/ecn_get.yaml, errors
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 43, Messages
[^r7]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 64, Messages
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 64, Messages
