---
title: "AP sup services"
type: "service-group"
slug: "services-ap-sup"
summary: "Ledgerline AP supplier payment hold services sup_pay_hold and sup_pay_release on screen AP-SPY-16 for managing vendor payment blocks."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/sup_pay_hold.yaml", "04_service_definitions/accounts_payable/sup_pay_release.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | Accounts Payable (AP) |
| Object | sup |
| Associated screen | [[screen-ap-spy-16|AP-SPY-16]] |
| Available since | Ledgerline 7.0 |
| Endpoints | POST /ll72/svc/sup_pay_hold, POST /ll72/svc/sup_pay_release |

The Accounts Payable supplier payment hold service group manages vendor-level payment stops in Ledgerline [^r1][^r8]. Operating from screen [[screen-ap-spy-16|AP-SPY-16]], these services apply or clear hold flags on supplier master records to prevent invoices from being selected in payment proposal runs [^r1][^r2][^r3]. Both write services require an active session token in the `X-LL-Session` header and execute against underlying database stored procedures [^r8][^r9][^r12][^r14].

## Services

### sup_pay_hold

Applies a payment hold flag to a supplier's ledger record, preventing any associated invoices from being selected in automated payment runs [^r1][^r2]. The write service is linked to screen [[screen-ap-spy-16|AP-SPY-16]], operates via stored procedure `sp_sup_pay_hold`, and is available at endpoint `POST /ll72/svc/sup_pay_hold` since version 7.0 [^r1][^r6][^r8][^r9]. Authentication requires a session token in header `X-LL-Session` with an authorised role [^r9].

* **Source file:** `04_service_definitions/accounts_payable/sup_pay_hold.yaml` [^r8]
* **Required fields:** `sup_cd` (string) [^r1][^r6][^r10]
* **Optional fields:** `reason` (string) [^r1][^r6][^r10]
* **Errors:**
  * Specific errors: `ERR-SPY-0001` (SUPPLIER PAYMENT HOLD NOT FOUND), [[err-sup-0030|ERR-SUP-0030]] [^r4][^r6][^r11].
  * Common errors: `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r11].

The service returns standard envelope fields `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r11].

### sup_pay_release

Removes an active payment stop flag from a supplier master record, logs the update in the audit trail, and re-enables the supplier's invoices for payment proposals [^r3][^r12]. The write service is linked to screen [[screen-ap-spy-16|AP-SPY-16]], invokes stored procedure `sp_sup_pay_release`, and is exposed at endpoint `POST /ll72/svc/sup_pay_release` since version 7.0 [^r1][^r7][^r12][^r13]. Calls require a session token in header `X-LL-Session` with an authorised role [^r14].

* **Source file:** `04_service_definitions/accounts_payable/sup_pay_release.yaml` [^r12]
* **Required fields:** `sup_cd` (SUP CD, string) [^r1][^r7][^r15]
* **Optional fields:** `comment` (COMMENT, string) [^r1][^r7][^r15]
* **Errors:**
  * Specific errors: `ERR-SPY-0001` (SUPPLIER PAYMENT HOLD NOT FOUND), `ERR-SPY-0007` (SUPPLIER PAYMENT HOLD NOT IN DRAFT (<status>)), [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND) [^r4][^r5][^r7][^r17].
  * Common errors: `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (<FIELD> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), `ERR-SYS-0503` (SERVER BUSY, TRY LATER) [^r18].

The response envelope returns `rc` (`S | W | E`), `err_cd`, short capitalised message `msg`, and `data` [^r16].

## See also

* [[screen-ap-spy-16|AP-SPY-16 Supplier Payment Hold Hold]]
* [[err-sup-0030|ERR-SUP-0030]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[services-ap-pay|AP pay services]]
* [[services-pur-sup|PUR sup services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 58, §18. Supplier Payment Hold (AP-SPY-16)
[^r8]: 04_service_definitions/accounts_payable/sup_pay_hold.yaml, service: sup_pay_hold
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 60, Step by step
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 60, Step by step
[^r9]: 04_service_definitions/accounts_payable/sup_pay_hold.yaml, auth
[^r12]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, service
[^r14]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, auth
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, sup_pay_hold SUPPLIER PAYMENT HOLD HOLD
[^r10]: 04_service_definitions/accounts_payable/sup_pay_hold.yaml, request.fields
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SPY-0001 SUPPLIER PAYMENT HOLD NOT FOUND
[^r11]: 04_service_definitions/accounts_payable/sup_pay_hold.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 37, sup_pay_release SUPPLIER PAYMENT HOLD RELEASE
[^r13]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, service
[^r15]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, request.fields
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 24, ERR-SPY-0007 SUPPLIER PAYMENT HOLD NOT IN DRAFT (<status>)
[^r17]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, errors
[^r18]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, common_errors
[^r16]: 04_service_definitions/accounts_payable/sup_pay_release.yaml, response.envelope
