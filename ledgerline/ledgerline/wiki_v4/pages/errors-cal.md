---
title: "Calibration Error Codes (ERR-CAL-*)"
type: "error-list"
slug: "errors-cal"
summary: "Reference list of ERR-CAL calibration module error codes raised by production calibration services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/cal_due.yaml", "04_service_definitions/production/cal_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CAL |
| Module | Production (PRD) |
| Domain | Calibration |
| Status | current |

This catalogue lists error codes under the ERR-CAL prefix used across Ledgerline calibration operations as of 26 October 2026. These error messages are returned when querying or verifying calibration records in production workflows. Full analysis and resolution guidance for individual errors are maintained on dedicated detail pages.

### ERR-CAL-0001
* **Message:** CALIBRATION NOT FOUND [^r1][^r2]
* **Cause:** The requested calibration record cannot be located [^r1][^r2].
* **Remedy:** Verify the calibration tool or record identifier and confirm the entry exists via [[screen-qa-cal-04|QA-CAL-04 Calibration Entry]]. Refer to [[err-cal-0001|ERR-CAL-0001 Calibration Tool Not Found]] for full troubleshooting details.
* **Raised by:** Service `cal_due` [^r1] and service `cal_get` [^r2] within [[services-prd-cal|PRD cal services]].

## See also
* [[err-cal-0001|ERR-CAL-0001 Calibration Tool Not Found]]
* [[screen-qa-cal-04|QA-CAL-04 Calibration Entry]]
* [[services-prd-cal|PRD cal services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/production/cal_due.yaml, errors
[^r2]: 04_service_definitions/production/cal_get.yaml, errors
