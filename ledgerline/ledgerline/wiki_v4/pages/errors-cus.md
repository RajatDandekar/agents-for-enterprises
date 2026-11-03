---
title: "ERR-CUS Error Codes"
type: "error-list"
slug: "errors-cus"
summary: "Error codes under the ERR-CUS prefix raised by sales customer master services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/cust_block.yaml", "04_service_definitions/sales/cust_credit.yaml", "04_service_definitions/sales/cust_get.yaml", "04_service_definitions/sales/cust_update.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-CUS |
| Module | Sales |
| Domain | Customer Master |
| Current codes | ERR-CUS-0001, ERR-CUS-0801 |

This page catalogues the `ERR-CUS` prefix error messages raised across Ledgerline sales customer master services. It lists the standard system message texts, underlying causes, and triggering services for customer lookup and update operations. As of 26 October 2026, these codes enforce record existence and status validation across customer maintenance workflows.

### ERR-CUS-0001

* **Message**: CUSTOMER MASTER NOT FOUND [^r1][^r2][^r3][^r4]
* **Cause**: The requested customer master record does not exist in the system [^r1][^r2][^r3][^r4].
* **Remedy**: Verify the customer identifier and ensure the customer record has been created before attempting lookups, credit modifications, status blocks, or record updates [^r1][^r2][^r3][^r4].
* **Raised by**: `cust_block` [^r1], `cust_credit` [^r2], `cust_get` [^r3], and `cust_update` [^r4].
* **Detailed page**: [[err-cus-0001]]

### ERR-CUS-0801

* **Message**: CUSTOMER MASTER CLOSED (<status>) [^r5]
* **Cause**: An update was attempted on a customer master record that is currently closed [^r5].
* **Remedy**: Reopen the customer master or adjust the record status before applying modifications via customer maintenance services [^r5].
* **Raised by**: `cust_update` [^r5].
* **Detailed page**: [[err-cus-0801]]

## See also

* [[services-sal-cust]]
* [[screen-sal-cus-01]]
* [[err-cus-0001]]
* [[err-cus-0801]]

## References

[^r1]: 04_service_definitions/sales/cust_block.yaml, errors
[^r2]: 04_service_definitions/sales/cust_credit.yaml, errors
[^r3]: 04_service_definitions/sales/cust_get.yaml, errors
[^r4]: 04_service_definitions/sales/cust_update.yaml, errors
[^r5]: 04_service_definitions/sales/cust_update.yaml, errors
