---
title: "ERR-SUP-0031 Supplier is blocked"
type: "error"
slug: "err-sup-0031"
summary: "Ledgerline error raised when attempting to place a new purchase order with a supplier marked with BLOCKED status."
audience: "staff"
status: "mixed"
sources: ["07_data_dictionary/code_lists.csv", "01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "01_policies/old/Supplier_Policy_v2.2.docx", "11_training/intranet_export_2016/error_messages.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-SUP-0031 |
| module | PUR / SUP |
| severity | Error |
| trigger | Placing a new purchase order against a blocked supplier |
| status | Current |

`ERR-SUP-0031` is a Ledgerline system error generated when an operator attempts to place a new purchase order against a supplier whose account is blocked[^r2]. In the system data dictionary, any supplier marked with the status `BLOCKED` is refused with this error message[^r1]. Purchasing policy [[pol-sup-003|POL-SUP-003]] governs supplier blocking rules and prevents order processing while this status is active[^r2].

## Meaning
The error indicates that the target supplier currently holds `BLOCKED` status in the supplier master and cannot accept new purchase orders[^r1][^r2].

## Cause
A user attempted to place a new purchase order against a supplier record whose status is set to `BLOCKED`[^r1][^r2]. 

## How to fix
Check the supplier status and address the underlying block under the blocking and unblocking provisions of [[pol-sup-003|POL-SUP-003]][^r2]. Historic training material instructed staff to contact [[user-gsutcliffe|Graham Sutcliffe]] to unblock the supplier record[^r3].

## Raised by
Ledgerline raises the error during purchase order entry when validating the selected supplier's status code[^r1][^r2].

## Versions and conflicts
- **Superseded policy text**: Current policy [[pol-sup-003|POL-SUP-003]] v2.3 specifies that Ledgerline generates `ERR-SUP-0031` when attempting to place a new purchase order with a blocked supplier[^r2]. Superseded policy v2.2 documented the same condition as displaying `ERR-SUP-0031` when attempting to place a new purchase order against a blocked supplier[^r5].
- **Superseded message description**: Current code lists define `ERR-SUP-0031` for records with status `BLOCKED`[^r1]. The 2016 intranet training export listed `ERR-SUP-0031` with the message text `'SUPPLIER NOT ACTIVE'` and instructed users to ask [[user-gsutcliffe|Graham Sutcliffe]] to perform the unblock[^r3].

## See also
* [[errors-sup|ERR-SUP Error Codes]]
* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[data-code-lists|Ledgerline ERP 7.2 Code Lists Reference]]
* [[user-gsutcliffe|Graham Sutcliffe (GSUTCLIFFE)]]

## References

[^r2]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 2, §5. Blocking and unblocking
[^r1]: 07_data_dictionary/code_lists.csv, sheet csv, row sup_status, ALL 14 ROWS
[^r3]: 11_training/intranet_export_2016/error_messages.html, Error messages
[^r5]: 01_policies/old/Supplier_Policy_v2.2.docx, §5. Blocking and unblocking
