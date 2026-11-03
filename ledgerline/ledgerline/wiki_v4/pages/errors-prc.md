---
title: "ERR-PRC error codes"
type: "error-list"
slug: "errors-prc"
summary: "Reference list of ERR-PRC error codes raised by pricing services in the sales module."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/prc_copy.yaml", "04_service_definitions/sales/prc_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-PRC |
| Module | Sales |
| Object | Pricing (PRC) |
| Status | current |

This page catalogues the system error codes using the `ERR-PRC` prefix within Ledgerline's sales module. These messages are raised during price list queries and copying routines handled by the [[services-sal-prc|pricing service group]]. Operational issues encountered on screen [[screen-sal-prc-08|SAL-PRC-08]] frequently trace back to these diagnostic codes.

### ERR-PRC-0001

* **Message:** PRICE LIST NOT FOUND [^r1][^r2]
* **Cause:** The requested price list identifier cannot be located in the system [^r1][^r2].
* **Remedy:** Verify the price list code supplied in the request parameters; see detailed troubleshooting under [[err-prc-0001|ERR-PRC-0001]].
* **Raised by:** Service `prc_copy` [^r1], service `prc_get` [^r2].

## See also

* [[err-prc-0001|ERR-PRC-0001 Mandatory parameters absent or pricing conflict]]
* [[services-sal-prc|SAL prc services]]
* [[screen-sal-prc-08|SAL-PRC-08 Price List]]
* [[errors-itm|ERR-ITM error codes]]

## References

[^r1]: 04_service_definitions/sales/prc_copy.yaml, errors
[^r2]: 04_service_definitions/sales/prc_get.yaml, errors
