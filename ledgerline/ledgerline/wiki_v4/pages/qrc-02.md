---
title: "QRC-02 Raising a purchase order - Fetch first"
type: "procedure"
slug: "qrc-02"
summary: "Quick reference card detailing how to raise a purchase order on screen PUR-PO-01 and release it on PUR-POR-05."
audience: "staff"
status: "current"
sources: ["11_training/QRC-02 Raising a purchase order - Fetch first.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | QRC-02 |
| title | Raising a purchase order - Fetch first |
| type | procedure |
| version | v2026.1 |
| effective date | 2026-01-12 |
| status | current |

QRC-02 provides standard operating instructions for raising a purchase order in Ledgerline using the fetch-first sequence.[^r1][^r2] It prevents catalog discrepancies, pricing errors, and invoice registration halts across stores.[^r7][^r8] The procedure also covers mandatory tax code adjustments for overseas suppliers and document release requirements.[^r3][^r5]

## Steps

To begin raising a purchase order, open screen [[screen-pur-po-01|PUR-PO-01]], enter `STD`, and supply the approved purchase requisition number.[^r1] Users must enter the supplier and item and press `F3` (Fetch) before typing any prices or descriptions manually.[^r2] Fetching populates standard descriptions, current lead periods, and agreed purchasing terms from the central catalogue, which prevents mismatches at Leeds or Manchester stores.[^r7] If either the supplier or item is altered after fetching, the user must press `F3` again; failing to re-fetch will trigger [[err-scr-0221|ERR-SCR-0221]] when attempting to save.[^r6]

For orders placed with an overseas supplier, change the default tax code from `VAT20-UK` to `VAT20-RC`.[^r3] Leaving `VAT20-UK` on an import causes a discrepancy during invoice registration for the purchase ledger team and halts payment.[^r8]

Save the purchase order by pressing `F8`.[^r4] After saving, check the `Status` field on the document header rather than relying on the status bar, as the status bar only confirms database writing.[^r4] 

If the order enters `AP` status, navigate to screen [[screen-pur-por-05|PUR-POR-05]] and press `F9` to release it.[^r5] Only orders reaching `RL` status are transmitted to the supplier.[^r5] Users should review [[screen-pur-por-05|PUR-POR-05]] at the end of each session to verify that no orders remain stranded in `AP` status.[^r9]

## Forms and screens

* [[screen-pur-po-01|PUR-PO-01]]: Used to enter `STD`, link the approved PR number, fetch item and supplier details with `F3`, amend tax codes where applicable, and save with `F8`.[^r1][^r2][^r3][^r4]
* [[screen-pur-por-05|PUR-POR-05]]: Used at the end of order entry and end of sessions to release orders in `AP` status to `RL` status via `F9`.[^r5][^r9]

## See also

* [[data-tax-codes|Tax codes]]
* [[err-scr-0221|ERR-SCR-0221 FETCH NOT DONE]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]

## References

[^r1]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
[^r2]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
[^r7]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Fetching records
[^r8]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Tax codes for overseas orders
[^r3]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
[^r5]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
[^r6]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
[^r4]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Steps
[^r9]: 11_training/QRC-02 Raising a purchase order - Fetch first.pdf, p. 1, Tips - Releasing approved orders
