---
title: "ERR-BTT error codes: Battery End-Of-Line Testing"
type: "error-list"
slug: "errors-btt"
summary: "Master reference of ERR-BTT error codes raised by Ledgerline battery end-of-line testing services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/production/btt_get.yaml", "04_service_definitions/production/btt_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-BTT |
| Module | Production / Quality |
| Target object | Battery End-Of-Line Test |
| Source services | btt_get, btt_save |
| Status | Current |

The ERR-BTT error series covers validation and lookup errors raised during battery end-of-line testing in Ledgerline[^r1][^r2]. These errors occur when retrieving test records or saving test execution results such as serial numbers and open-circuit voltage measurements[^r1][^r2]. As of 26 October 2026, the codes are raised by backend testing services typically invoked from screens such as [[screen-qa-btt-03|QA-BTT-03 Battery End-Of-Line Test Entry]][^r1][^r2].

### ERR-BTT-0001
* **Message**: `BATTERY END-OF-LINE TEST NOT FOUND`[^r1]
* **Cause**: The requested battery end-of-line test record does not exist in Ledgerline[^r1].
* **Remedy**: Verify the test identifier or parameters passed to the lookup service[^r1].
* **Raised by**: [[services-prd-btt|btt_get]][^r1].

### ERR-BTT-0110
* **Message**: `SERIAL ALREADY TESTED`[^r2]
* **Cause**: A test record has already been submitted and saved for the specified battery serial number[^r2].
* **Remedy**: Verify the physical unit serial number before re-submitting, or check previous test results for that serial[^r2].
* **Raised by**: [[services-prd-btt|btt_save]][^r2].

### ERR-BTT-0120
* **Message**: `OCV OUT OF RANGE`[^r2]
* **Cause**: The recorded open-circuit voltage falls outside the allowable tolerance range for the battery under test[^r2].
* **Remedy**: Recheck the voltage measurement instrumentation or route the battery unit for inspection and failure analysis[^r2].
* **Raised by**: [[services-prd-btt|btt_save]][^r2].

## See also
* [[screen-qa-btt-03|QA-BTT-03 Battery End-Of-Line Test Entry]]
* [[services-prd-btt|PRD btt services]]

## References

[^r1]: 04_service_definitions/production/btt_get.yaml, errors
[^r2]: 04_service_definitions/production/btt_save.yaml, errors
