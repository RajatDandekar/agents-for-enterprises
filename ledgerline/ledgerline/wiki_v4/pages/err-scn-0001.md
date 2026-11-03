---
title: "ERR-SCN-0001 Invoice not found for customer account"
type: "error"
slug: "err-scn-0001"
summary: "Ledgerline error raised when an entered invoice number cannot be found in the sales ledger or does not match the customer account."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-SCN-0001 |
| Message | Invoice not found for customer account |
| Module | Sales (SAL) |
| Source manual | MAN-SAL-72 |
| Status | Current |

ERR-SCN-0001 is a Ledgerline error message in the sales module indicating a mismatch between an entered invoice number and a customer account [^r1]. It blocks processing when the specified invoice cannot be located within the sales ledger or does not belong to the entered customer [^r1]. Users encountering this message must verify both the customer code and the invoice identifier before retrying [^r1].

## Meaning
The system displays ERR-SCN-0001 when an invoice reference fails validation against the sales ledger for the selected customer account [^r1].

## Cause
This error is triggered when the invoice number entered in `INV NO` either does not belong to the customer account specified in `CUST CD`, or cannot be found in the sales ledger [^r1].

## How to fix
Check that the value in `CUST CD` correctly reflects the customer account associated with the transaction [^r1]. Verify that the number entered in `INV NO` is typed correctly and exists in the sales ledger for that specific customer account [^r1].

## Raised by
The message is documented in the sales reference manual [[man-sal-72|MAN-SAL-72]] under screen and service message handling [^r1].

## See also
* [[services-sal-scn]]
* [[screen-sal-inv-06]]
* [[screen-sal-cus-01]]
* [[man-sal-72]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 43, Messages
