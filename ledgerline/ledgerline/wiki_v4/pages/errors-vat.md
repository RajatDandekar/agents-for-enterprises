---
title: "Errors VAT"
type: "error-list"
slug: "errors-vat"
summary: "Reference list of ERR-VAT error codes raised by Ledgerline accounts payable VAT services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/accounts_payable/vat_get.yaml", "04_service_definitions/accounts_payable/vat_rc_list.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-VAT |
| Domain | Accounts Payable (VAT) |
| Module | AP |
| Status | Current |

This page catalogues the `ERR-VAT` error codes used across Ledgerline accounts payable VAT processing as of 26 October 2026. These errors indicate validation or lookup failures encountered during VAT operations. They are raised by underlying service endpoints supporting VAT return screens such as [[screen-ap-vat-12|AP-VAT-12 Vat Return]].

### ERR-VAT-0001
* **Message:** VAT RETURN NOT FOUND [^r1][^r2].
* **Cause:** The requested VAT return record cannot be located in the database [^r1][^r2].
* **Remedy:** Verify that the VAT return identifier or period entered is correct and that the return record exists before re-querying [^r1][^r2].
* **Raised by:** Service `vat_get` [^r1] and service `vat_rc_list` [^r2] (see [[services-ap-vat|AP vat services]]).

## See also
* [[screen-ap-vat-12|AP-VAT-12 Vat Return]]
* [[services-ap-vat|AP vat services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/accounts_payable/vat_get.yaml, errors
[^r2]: 04_service_definitions/accounts_payable/vat_rc_list.yaml, errors
