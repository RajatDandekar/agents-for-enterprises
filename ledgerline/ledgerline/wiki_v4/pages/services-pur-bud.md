---
title: "PUR bud services"
type: "service-group"
slug: "services-pur-bud"
summary: "Ledgerline Purchasing budget check service validating cost centre budget availability against committed spend."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/purchase/bud_check.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | PUR |
| Object | bud |
| Service count | 1 |
| Database procedure | sp_budget_chk |
| Introduced | Ledgerline 7.0 |
| Status | current |

The `bud` service group in the Ledgerline Purchasing module provides budget availability validation for cost centres[^r4]. The service calculates remaining funds by deducting gross approved and pending order commitments from allocated amounts, validating quarterly availability against transaction values[^r1][^r2]. As of 26 October 2026, it is active in Ledgerline 7.2 and executes the underlying database procedure `sp_budget_chk`[^r3][^r8].

## Services

### bud_check

The `bud_check` service executes budget availability checks for module PUR, operating since Ledgerline version 7.0[^r4]. It runs the database procedure `sp_budget_chk`[^r3][^r8]. The service is exposed via endpoint `POST /ll72/svc/bud_check` and requires a session token passed in header `X-LL-Session` with an authorized user role[^r5].

The service calculates available budget balance using the formula `available = amount − committed`, where `committed` includes the gross value of approved and pending orders[^r1]. It validates quarterly cost centre budget availability against the proposed transaction value[^r2].

The standard response envelope returns fields `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (`result`)[^r7].

* **Required fields**: `cc_cd` (cost centre code, string), `amount` (float)[^r3][^r6].
* **Optional fields**: None[^r6].
* **Errors**:
  * [[err-cc-0009|ERR-CC-0009]]: COST CENTRE NOT FOUND[^r3][^r9]
  * ERR-BUD-0207: BUDGET EXCEEDED FOR `<cc_cd>` (raised when the transaction value exceeds available budget)[^r2][^r3][^r9]
  * Common errors: ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503[^r9]
* **Source file**: `04_service_definitions/purchase/bud_check.yaml`[^r4]. Documentation references include [[man-dd-72|MAN-DD-72]], MAN-ERR-72, and MAN-SVC-72[^r1][^r2][^r3].

## See also

* [[err-cc-0009]]
* [[man-dd-72]]
* [[services-pur-po]]
* [[services-pur-pr]]

## References

[^r4]: 04_service_definitions/purchase/bud_check.yaml, service: bud_check
[^r1]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §9. Cost centres and budgets
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 4, §2. Codes
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 8, bud_check BUDGET CHECK
[^r8]: 04_service_definitions/purchase/bud_check.yaml, procedures
[^r5]: 04_service_definitions/purchase/bud_check.yaml, endpoint
[^r7]: 04_service_definitions/purchase/bud_check.yaml, response
[^r6]: 04_service_definitions/purchase/bud_check.yaml, request
[^r9]: 04_service_definitions/purchase/bud_check.yaml, errors
