---
title: "ERR-SCR-0221 FETCH NOT DONE"
type: "error"
slug: "err-scr-0221"
summary: "Error raised when saving a purchase order on PUR-PO-01 or calling po_save without completing master data retrieval via F3 (Fetch)."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PUR-002 PR to PO v1.4.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf", "11_training/QRC-02 Raising a purchase order - Fetch first.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-SCR-0221 |
| text | FETCH NOT DONE |
| severity | Error |
| raised_by | po_save, PUR-PO-01 |
| screen | PUR-PO-01 |
| service | po_save |
| manual | MAN-PUR-72 |

`ERR-SCR-0221` is an operational error code in Ledgerline ERP indicating that an order save action was attempted without a prior master data fetch for the active supplier and item [^r1][^r4]. It appears on [[screen-pur-po-01|PUR-PO-01]] or as an API response during purchase order creation when line details or master data tokens are absent or stale [^r4]. To proceed with order generation, users must trigger data retrieval before committing the transaction [^r2][^r3].

## Meaning

The error message `ERR-SCR-0221 FETCH NOT DONE` indicates that an order save was attempted on [[screen-pur-po-01|PUR-PO-01]] without completing data retrieval for the selected supplier and line item, or that `fetch_tok` is missing or invalid [^r4].

## Cause

The error occurs under the following operational conditions:
* Saving an order on PUR-PO-01 without pressing F3 (Fetch) after entering supplier and item details [^r1][^r3].
* Altering the supplier or item on PUR-PO-01 after executing Fetch without pressing F3 again before saving [^r5].
* Calling the underlying order-save service without executing data retrieval for the current supplier and line item, or passing an invalid or missing `fetch_tok` [^r4].

## How to fix

To resolve the error in [[sop-pur-002|SOP-PUR-002]] and [[qrc-02|QRC-02]]:
1. Return the cursor to the line area on screen PUR-PO-01 [^r2].
2. Press F3 to execute the fetch of master data for the current supplier and item selection [^r2].
3. Re-attempt the save operation by pressing F8 [^r2].

## Raised by

* Screen [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]] [^r1][^r4].
* Underlying service `po_save` documented under [[services-pur-po|PUR po services]] [^r4].
* Documented in [[man-pur-72|MAN-PUR-72]] and [[rn-7-2-3|RN-7.2.3]] [^r3][^r4].

## See also

* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[services-pur-po|PUR po services]]
* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]
* [[qrc-02|QRC-02 Raising a purchase order - Fetch first]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[rn-7-2-3|RN-7.2.3 Ledgerline ERP 7.2.3 Release Notes]]
* [[errors-po|ERR-PO Error Codes]]

## References

[^r1]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r4]: 08_release_notes/RN-7.2.3 Ledgerline Release Notes.pdf, p. 2, Save on PUR-PO-01 needs Fetch for the current supplier and item: ERR-SCR-0221 FETCH NOT DONE.
[^r2]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 4, What to do when something does not look right
[^r3]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §11.3 Fetch before Save
[^r5]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
