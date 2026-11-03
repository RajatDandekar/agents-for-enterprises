---
title: "ERR-SCN error codes"
type: "error-list"
slug: "errors-scn"
summary: "Catalogue of Ledgerline ERR-SCN error codes raised by sales customer credit note services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/scn_get.yaml", "04_service_definitions/sales/scn_post.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SCN |
| Domain | Sales (Customer Credit Notes) |
| Module | SAL |
| Related services | services-sal-scn |

The ERR-SCN series covers system error codes returned by Ledgerline during customer credit note processing in the sales module [^r1][^r2]. These errors occur when credit note records cannot be retrieved or fail lifecycle status validations during posting operations [^r1][^r3]. As of 26 October 2026, the catalogue defines the validation errors encountered across services such as `scn_get` and `scn_post` [^r1][^r2][^r3].

### ERR-SCN-0001

* **Message**: CUSTOMER CREDIT NOTE NOT FOUND [^r1][^r2]
* **Cause**: The requested customer credit note record does not exist or cannot be located during lookup or posting workflows [^r1][^r2].
* **Remedy**: Verify the credit note reference identifier and confirm the document exists before attempting retrieval or posting. Refer to [[err-scn-0001|ERR-SCN-0001 Invoice not found for customer account]] for narrative guidance.
* **Raised by**: `scn_get` and `scn_post` [^r1][^r2].

### ERR-SCN-0007

* **Message**: CUSTOMER CREDIT NOTE NOT IN DRAFT (<status>) [^r3]
* **Cause**: An attempt was made to post a customer credit note that is not currently in draft status [^r3].
* **Remedy**: Check the current document status; only credit notes in draft state can be posted. Refer to [[err-scn-0007|ERR-SCN-0007 Customer credit note posting validation failure]] for operational handling.
* **Raised by**: `scn_post` [^r3].

## See also

* [[services-sal-scn|SAL scn services]]
* [[screen-sal-crn-09|SAL-CRN-09 Customer Credit Note Entry]]
* [[err-scn-0001|ERR-SCN-0001 Invoice not found for customer account]]
* [[err-scn-0007|ERR-SCN-0007 Customer credit note posting validation failure]]

## References

[^r1]: 04_service_definitions/sales/scn_get.yaml, errors
[^r2]: 04_service_definitions/sales/scn_post.yaml, errors
[^r3]: 04_service_definitions/sales/scn_post.yaml, errors
