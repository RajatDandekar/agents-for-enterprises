---
title: "ERR-SPY Message and Error Codes"
type: "error-list"
slug: "errors-spy"
summary: "Reference list of ERR-SPY error and message codes raised during supplier payment hold and release operations in Ledgerline Accounts Payable."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "04_service_definitions/accounts_payable/sup_pay_hold.yaml", "04_service_definitions/accounts_payable/sup_pay_release.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SPY |
| Module | Accounts Payable (AP) |
| Related Screen | AP-SPY-16 |
| Related Services | sup_pay_hold, sup_pay_release |
| Manual | MAN-AP-72 |

The `ERR-SPY` error series covers messages generated during supplier payment hold and release actions in the Accounts Payable module [^r1][^r3]. These codes are triggered on screen [[screen-ap-spy-16|AP-SPY-16]] or directly through the underlying [[services-ap-sup|AP sup services]] `sup_pay_hold` and `sup_pay_release` [^r1][^r2][^r3][^r4]. Understanding these codes prevents workflow disruption when placing accounts on hold or clearing vendors for payment processing [^r1][^r2].

### ERR-SPY-0001
* **Message**: SUPPLIER PAYMENT HOLD NOT FOUND [^r3][^r4]
* **Cause**: Attempting a `sup_pay_hold` operation on a vendor already on hold, or attempting a `sup_pay_release` operation on an account without an active hold [^r1]. It indicates an invalid operational state transition [^r1].
* **Remedy**: Verify the current hold status of the vendor before submitting state transitions [^r1].
* **Raised by**: Service `sup_pay_hold` and service `sup_pay_release` [^r3][^r4], referenced in [[man-ap-72|MAN-AP-72]] [^r1].

### ERR-SPY-0007
* **Message**: SUPPLIER PAYMENT HOLD NOT IN DRAFT (&lt;status&gt;) [^r5]
* **Cause**: Mandatory detail is missing on screen [[screen-ap-spy-16|AP-SPY-16]], such as when the REASON or COMMENT field is blank or contains invalid characters [^r2]. In service `sup_pay_release`, it is raised when the hold record is not in draft status [^r5].
* **Remedy**: Ensure the REASON and COMMENT fields are populated with valid characters on [[screen-ap-spy-16|AP-SPY-16]], or confirm the payment hold record status before executing release [^r2][^r5].
* **Raised by**: Screen [[screen-ap-spy-16|AP-SPY-16]] and service `sup_pay_release` [^r2][^r5], referenced in [[man-ap-72|MAN-AP-72]] [^r2].

## Versions and conflicts

* **ERR-SPY-0001 description**: [[man-ap-72|MAN-AP-72]] (dated 2025-01-15) documents the error as an invalid operational state transition occurring on duplicate hold or unheld release [^r1]. The service definitions `sup_pay_hold.yaml` and `sup_pay_release.yaml` define the message text specifically as `SUPPLIER PAYMENT HOLD NOT FOUND` [^r3][^r4] (`contradiction`).
* **ERR-SPY-0007 usage**: [[man-ap-72|MAN-AP-72]] (dated 2025-01-15) documents the error on [[screen-ap-spy-16|AP-SPY-16]] for blank or invalid REASON or COMMENT fields [^r2]. The backend service definition `sup_pay_release.yaml` defines the message as `SUPPLIER PAYMENT HOLD NOT IN DRAFT (<status>)` [^r5] (`contradiction`).

## See also

* [[screen-ap-spy-16|AP-SPY-16 Supplier Payment Hold Hold]]
* [[services-ap-sup|AP sup services]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[errors-pay|Errors PAY]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 60, Messages
[^r3]: 04_service_definitions/accounts_payable/sup_pay_hold.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 60, Messages
[^r4]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, errors
[^r5]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, errors
