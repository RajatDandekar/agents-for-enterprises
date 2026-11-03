---
title: "ERR-QUO quotation error codes"
type: "error-list"
slug: "errors-quo"
summary: "Ledgerline error codes for quotation management across the sales quotation services and entry screens."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "04_service_definitions/sales/quo_cancel.yaml", "04_service_definitions/sales/quo_convert.yaml", "04_service_definitions/sales/quo_get.yaml", "04_service_definitions/sales/quo_save.yaml", "04_service_definitions/sales/quo_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-QUO |
| Module | Sales (SAL) |
| Applies to | Quotation management |
| Status | Current |

`ERR-QUO` error codes are raised by Ledgerline ERP quotation operations in [[services-sal-quo]] and on the [[screen-sal-quo-02|SAL-QUO-02 Quotation Entry]] screen[^r1][^r4]. They signal issues when looking up quotation records, validating line item quantities or validity dates, and cancelling quotation headers[^r1][^r2][^r5].

### ERR-QUO-0001
* **Message:** `QUOTATION NOT FOUND`[^r4][^r6][^r7].
* **Cause:** Raised during quotation operations such as `quo_cancel`, `quo_convert`, and `quo_get` when Ledgerline cannot find the quotation reference entered in `QUO NO`[^r1][^r4][^r6][^r7]. According to [[man-sal-72]], it is also raised upon save when mandatory header fields are incomplete[^r1].
* **Remedy:** Verify that the quotation number exists and re-enter the identifier before repeating the operation, or verify that all mandatory header fields are populated[^r1][^r4].
* **Raised by:** Services `quo_cancel`, `quo_convert`, `quo_get`, and quotation save processing[^r1][^r4][^r6][^r7].

### ERR-QUO-0201
* **Message:** `QTY MUST BE > 0`[^r8][^r9].
* **Cause:** The service definition raises this error when an entered line quantity is not greater than zero during save or search operations[^r8][^r9]. In [[man-sal-72]], it is alternatively documented as occurring during quotation conversion when the date in `VALID TO` is earlier than the current system processing date[^r2].
* **Remedy:** Enter a positive line quantity greater than zero, or check that the quotation validity period is current and that `VALID TO` is not in the past[^r2][^r8].
* **Raised by:** Services `quo_save` and `quo_search`, and quotation conversion workflows[^r2][^r8][^r9].

### ERR-QUO-0801
* **Message:** `QUOTATION CLOSED (<status>)`[^r5].
* **Cause:** Raised during a `quo_cancel` operation when an attempt is made to cancel an already closed quotation[^r5]. In [[man-sal-72]], it is also documented as occurring when `REASON` is missing during cancellation, or upon saving if the customer account in `CUST CD` has a stop or restricted trading status[^r3].
* **Remedy:** Check the status of the quotation to ensure it is open before cancellation, ensure a cancellation reason is provided, and confirm that the customer account does not have a stop or restricted trading status[^r3][^r5].
* **Raised by:** Service `quo_cancel` and quotation save processing[^r3][^r5].

## Versions and conflicts
* **ERR-QUO-0001 trigger definition:** In service definitions for `quo_cancel`, `quo_convert`, and `quo_get`, ERR-QUO-0001 specifically returns message `QUOTATION NOT FOUND` when an existing quote record cannot be located (`04_service_definitions/sales/quo_cancel.yaml`, `04_service_definitions/sales/quo_convert.yaml`, `04_service_definitions/sales/quo_get.yaml`)[^r4][^r6][^r7]. [[man-sal-72]] (v7.2.3, p. 13) also states it is raised when mandatory header fields are incomplete during saving[^r1]. (`contradiction` | [^r1], [^r4], [^r6], [^r7])
* **ERR-QUO-0201 definition:** In service definitions for `quo_save` and `quo_search`, ERR-QUO-0201 returns `QTY MUST BE > 0` (`04_service_definitions/sales/quo_save.yaml`, `04_service_definitions/sales/quo_search.yaml`)[^r8][^r9]. In [[man-sal-72]] (v7.2.3, p. 13), ERR-QUO-0201 is described as an expired quotation error raised when converting a quote whose `VALID TO` date is earlier than the current system processing date[^r2]. (`contradiction` | [^r2], [^r8], [^r9])
* **ERR-QUO-0801 definition:** In `quo_cancel.yaml`, ERR-QUO-0801 returns `QUOTATION CLOSED (<status>)` when trying to cancel an already closed quote (`04_service_definitions/sales/quo_cancel.yaml`)[^r5]. In [[man-sal-72]] (v7.2.3, p. 13), ERR-QUO-0801 is raised when `REASON` is missing during cancellation, or when saving against a customer in `CUST CD` that has a stop or restricted trading status[^r3]. (`contradiction` | [^r3], [^r5])

## See also
* [[screen-sal-quo-02|SAL-QUO-02 Quotation Entry]]
* [[services-sal-quo|SAL quo services]]
* [[man-sal-72|MAN-SAL-72 Ledgerline ERP 7.2 User Manual: Sales]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[services-sal-so|SAL so services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 13, Messages
[^r4]: 04_service_definitions/sales/quo_cancel.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 13, Messages
[^r5]: 04_service_definitions/sales/quo_cancel.yaml, errors
[^r6]: 04_service_definitions/sales/quo_convert.yaml, errors
[^r7]: 04_service_definitions/sales/quo_get.yaml, errors
[^r8]: 04_service_definitions/sales/quo_save.yaml, errors
[^r9]: 04_service_definitions/sales/quo_search.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 13, Messages
