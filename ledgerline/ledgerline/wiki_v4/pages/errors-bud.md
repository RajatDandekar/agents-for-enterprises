---
title: "ERR-BUD error codes"
type: "error-list"
slug: "errors-bud"
summary: "Reference list of ERR-BUD budget validation and transfer error codes raised across Ledgerline administration and purchasing services."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "04_service_definitions/admin/bud_query.yaml", "04_service_definitions/admin/bud_transfer.yaml", "04_service_definitions/purchase/bud_check.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code_prefix | ERR-BUD |
| module | Budgeting / Administration / Purchasing |
| system | Ledgerline ERP |
| reference_manual | MAN-ERR-72 |
| status | current |

This page details all error codes under the `ERR-BUD-*` prefix in Ledgerline ERP 7.2 [^r1]. These codes prevent transactions and allocations from proceeding when cost centre budget records are missing or when quarterly commitment limits are exceeded [^r1][^r2]. As of 26 October 2026, these validations are enforced across budget query, budget transfer, and purchase order processing services [^r1][^r2].

### ERR-BUD-0001 BUDGET NOT FOUND
* **Message**: `BUDGET NOT FOUND` [^r1][^r3].
* **Cause**: No budget record exists for the specified search key or cost centre combination [^r1][^r3].
* **Remedy**: Verify the cost centre and budget key parameters, or create the necessary budget allocation using [[screen-fin-bud-02|FIN-BUD-02 Budget Entry]].
* **Raised by**: Raised by `bud_transfer` and `bud_query` in [[services-adm-bud|ADM bud services]] [^r1][^r3][^r4].

### ERR-BUD-0207 BUDGET EXCEEDED FOR <cc_cd>
* **Message**: `BUDGET EXCEEDED FOR <cc_cd>` [^r2][^r5][^r6].
* **Cause**: The gross purchase commitment exceeds the available quarterly budget allocated for cost centre `<cc_cd>` [^r2].
* **Remedy**: Perform a budget reallocation, adjust the commitment amount, or request an approved budget transfer for the affected cost centre.
* **Raised by**: Raised by `po_save` and `po_amend` in [[services-pur-po|PUR po services]], `bud_check` in [[services-pur-bud|PUR bud services]], and `bud_transfer` in [[services-adm-bud|ADM bud services]] [^r2][^r5][^r6].

## See also
* [[man-err-72|MAN-ERR-72 Ledgerline ERP 7.2 Message and Error Code]]
* [[screen-fin-bud-02|FIN-BUD-02 Budget Entry]]
* [[services-adm-bud|ADM bud services]]
* [[services-pur-bud|PUR bud services]]
* [[services-pur-po|PUR po services]]
* [[errors-cc|Cost Centre Error Codes (ERR-CC-*)]]
* [[errors-po|ERR-PO Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 4, §2. Codes
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 4, §2. Codes
[^r3]: 04_service_definitions/admin/bud_query.yaml, errors
[^r4]: 04_service_definitions/admin/bud_transfer.yaml, errors
[^r5]: 04_service_definitions/admin/bud_transfer.yaml, errors
[^r6]: 04_service_definitions/purchase/bud_check.yaml, errors
