---
title: "ERR-RMA Error Codes"
type: "error-list"
slug: "errors-rma"
summary: "Error code catalogue for warranty returns (ERR-RMA-*), covering return lookup, status validation, serial registration, warranty periods, and closure."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "04_service_definitions/sales/rma_approve.yaml", "04_service_definitions/sales/rma_close.yaml", "04_service_definitions/sales/rma_get.yaml", "04_service_definitions/sales/rma_receive.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-RMA-* |
| Module | Sales (SAL) |
| Object | Warranty Return (RMA) |
| Source manual | MAN-ERR-72 |

Catalogue of `ERR-RMA-*` message codes raised by Ledgerline warranty return operations in the sales module. These errors handle warranty claim processing, status transitions, serial number verification, and case closure. As of 26 October 2026, unresolved serial or warranty rejections prevent claim approval under [[sop-sal-002|SOP-SAL-002]].

### ERR-RMA-0001

* **Message:** WARRANTY RETURN NOT FOUND [^r8][^r12][^r14][^r15]
* **Cause:** The requested warranty return record does not exist or was not found in the database [^r2].
* **Remedy:** Verify the warranty return reference and ensure the record exists before re-attempting processing.
* **Raised by:** `rma_get`, `rma_approve`, `rma_receive`, and `rma_close` in [[services-sal-rma]] [^r2][^r8][^r12][^r14][^r15].

### ERR-RMA-0007

* **Message:** WARRANTY RETURN NOT IN DRAFT (<status>) [^r9]
* **Cause:** An attempt was made to approve a warranty return that is not in Draft or pending status [^r3].
* **Remedy:** Ensure the warranty return is in Draft status prior to running approval.
* **Raised by:** `rma_approve` in [[services-sal-rma]] [^r3][^r9].

### ERR-RMA-0210

* **Message:** SERIAL NOT REGISTERED [^r10]
* **Cause:** The frame or battery pack serial number submitted for the claim is not registered [^r1][^r4].
* **Remedy:** Register the serial number on [[screen-sal-srl-16|SAL-SRL-16]] before submitting or approving the warranty claim [^r1].
* **Raised by:** `rma_approve` in [[services-sal-rma]] [^r4][^r10].
* **Detailed page:** [[err-rma-0210]]

### ERR-RMA-0211

* **Message:** OUT OF WARRANTY (<sold_dt>) [^r11]
* **Cause:** The item submitted for return is out of warranty relative to its recorded sold date [^r5].
* **Remedy:** Check the original purchase or sold date and verify whether the claim qualifies for an exception or non-warranty repair.
* **Raised by:** `rma_approve` in [[services-sal-rma]] [^r5][^r11].

### ERR-RMA-0801

* **Message:** WARRANTY RETURN CLOSED (<status>) [^r13]
* **Cause:** The warranty return cannot be closed because it is already closed, cancelled, or rejected [^r6].
* **Remedy:** Check the current return status; no further closure action is needed on inactive claims.
* **Raised by:** `rma_close` in [[services-sal-rma]] [^r6][^r13].

## Versions and conflicts

* **ERR-RMA-0001 definition:** Today, [[man-err-72|MAN-ERR-72]] and the service definitions define ERR-RMA-0001 as "WARRANTY RETURN NOT FOUND" raised across `rma_get`, `rma_approve`, `rma_receive`, and `rma_close` [^r2][^r8][^r12][^r14][^r15]. However, the sales user manual (MAN-SAL-72 v7.2.3, p. 31) states that ERR-RMA-0001 indicates missing mandatory header data requiring CUST CD, ITEM CD, and FAULT CD before `rma_save` can generate a tracking file [^r7]. Kind: `contradiction`.

## See also

* [[err-rma-0210|ERR-RMA-0210 Serial not registered]]
* [[services-sal-rma|SAL rma services]]
* [[sop-sal-002|SOP-SAL-002 Warranty Claims from Bike Shops]]
* [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]
* [[screen-sal-rma-07|SAL-RMA-07 Warranty Return (Rma) Entry]]
* [[man-err-72|MAN-ERR-72 Ledgerline ERP 7.2 Message and Error Code]]

## References

[^r8]: 04_service_definitions/sales/rma_approve.yaml, errors
[^r12]: 04_service_definitions/sales/rma_close.yaml, errors
[^r14]: 04_service_definitions/sales/rma_get.yaml, errors
[^r15]: 04_service_definitions/sales/rma_receive.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 20
[^r9]: 04_service_definitions/sales/rma_approve.yaml, errors
[^r3]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 20
[^r10]: 04_service_definitions/sales/rma_approve.yaml, errors
[^r1]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 3, Common mistakes by bike shops and internal staff
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r11]: 04_service_definitions/sales/rma_approve.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r13]: 04_service_definitions/sales/rma_close.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 21
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 31, Messages
