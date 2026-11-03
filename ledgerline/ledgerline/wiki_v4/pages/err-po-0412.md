---
title: "ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY"
type: "error"
slug: "err-po-0412"
summary: "Purchase order validation error raised by po_save when an order line tax code does not match the supplier country."
audience: "staff"
status: "mixed"
sources: ["07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx", "02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf", "02_procedures/SOP-PUR-002 PR to PO v1.4.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf", "04_service_definitions/purchase/po_fetch.yaml", "04_service_definitions/purchase/po_save.yaml", "08_release_notes/RN-7.2.3-P1 Ledgerline Patch Notes.pdf", "11_training/New starter - Purchasing (2024) deck export.pdf", "11_training/QRC-03 ERR-PO-0412 quick fix.pdf", "11_training/intranet_export_2016/error_messages.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-PO-0412 |
| module | PO |
| message | TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (<state>) |
| service | po_save |
| screen | PUR-PO-01 |
| status | current |

`ERR-PO-0412` is a validation error raised by the Ledgerline purchase order module when an order line tax code does not match the supplier account's recorded country [^r1][^r4][^r18]. It occurs primarily because the system's fetch action automatically populates the domestic UK tax code on purchase orders, even for non-UK vendors [^r5][^r8][^r19]. Saving an overseas order without manually adjusting the line tax code to a reverse-charge code triggers this error and blocks the transaction [^r2][^r7][^r12].

## Meaning

The error displays the message `TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (<state>)`, where the country code appended in brackets reflects the country recorded on the supplier account [^r1][^r14][^r18]. It signals that an incorrect tax code was selected on a purchase order line [^r17]. The message appears in the system status bar, in error dialogs, and within background batch processing logs [^r16].

## Cause

`ERR-PO-0412` occurs on [[screen-pur-po-01|PUR-PO-01]] when saving an order for an overseas supplier whose line tax code retains the default domestic entry rather than a reverse-charge code [^r2][^r7]. Ledgerline's Fetch function automatically defaults `VAT20-UK` on purchase order lines, regardless of whether a vendor is based in an overseas country such as the Netherlands or Poland [^r5][^r8][^r10][^r19]. UK suppliers require a `-UK` tax code, while suppliers located in any other country require an equivalent reverse-charge `-RC` code [^r4]. Frequent occurrences indicate that an overseas supplier profile was configured with domestic defaults [^r23].

## How to fix

To resolve the error, users must verify the supplier country on the record and amend the line tax code to match the supplier's location [^r3][^r15]. For suppliers outside the UK, change the tax code to `VAT20-RC` for standard goods or `VAT5-RC` for reduced-rate items [^r9][^r20]. For a UK-registered supplier, the tax code must be set to `VAT20-UK` [^r21]. After updating the tax code, keep the cursor in the line details area and press F8 to save and recommit the order [^r3][^r22]. 

Users must never force a purchase order through using domestic tax codes for an overseas supplier account, as doing so distorts tax returns [^r24]. If the error recurs frequently for a specific vendor, notify the purchase ledger team to review and correct the supplier master profile [^r23].

## Raised by

The error is raised by the `po_save` service within [[services-pur-po]] during order validation against the vendor address record [^r6][^r11][^r13][^r15]. It triggers when the tax code entered on the order fails to match the supplier country state returned by `po_fetch` [^r11][^r12][^r13].

## Versions and conflicts

* **Message text change (current vs. superseded)**: Today, following patch 7.2.3-P1, the error text is `TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (<state>)` [^r1][^r14]. Older documentation and legacy Ledgerline 7.0 system manuals phrased the message as `TAX REGION DOES NOT MATCH SUPPLIER STATE` [^r14][^r25][^r27].
* **Resolution terminology (current vs. superseded)**: Under [[sop-pur-002|SOP-PUR-002]] v1.4, the remedy requires updating the line tax code to reverse-charge codes like `VAT20-RC` on PUR-PO-01 [^r2][^r3]. The superseded SOP-PUR-002 v1.3 and Ledgerline 7.0 manual described this as correcting regional authority assignments or updating master records [^r26][^r27][^r28].

## See also

* [[errors-po|ERR-PO Error Codes]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[services-pur-po|PUR po services]]
* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]
* [[data-tax-codes|Tax codes]]

## References

[^r1]: 07_data_dictionary/Ledgerline_7.2_tables_and_fields.xlsx, sheet Error codes, row ERR-PO-0412, SHEET Error codes
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0412
[^r18]: 11_training/QRC-03 ERR-PO-0412 quick fix.pdf, p. 1, Steps
[^r5]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0412
[^r8]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 10, §17.2 ERR-PO-0412 Tax code does not match supplier country
[^r19]: 11_training/QRC-03 ERR-PO-0412 quick fix.pdf, p. 1, Steps
[^r2]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 3, §5. Procedure
[^r7]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §11.4 The tax code
[^r12]: 04_service_definitions/purchase/po_fetch.yaml, notes
[^r14]: 08_release_notes/RN-7.2.3-P1 Ledgerline Patch Notes.pdf, p. 2, §2. Changes
[^r17]: 11_training/New starter - Purchasing (2024) deck export.pdf, p. 6, Tax codes
[^r16]: 08_release_notes/RN-7.2.3-P1 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 27, PUR-PO-01 PURCHASE ORDER ENTRY
[^r23]: 11_training/QRC-03 ERR-PO-0412 quick fix.pdf, p. 1, Tips
[^r3]: 02_procedures/SOP-PUR-002 PR to PO v1.4.pdf, p. 4, What to do when something does not look right
[^r15]: 08_release_notes/RN-7.2.3-P1 Ledgerline Patch Notes.pdf, p. 2, §3. Details
[^r9]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 10, §17.2 ERR-PO-0412 Tax code does not match supplier country
[^r20]: 11_training/QRC-03 ERR-PO-0412 quick fix.pdf, p. 1, Steps
[^r21]: 11_training/QRC-03 ERR-PO-0412 quick fix.pdf, p. 1, Tips
[^r22]: 11_training/QRC-03 ERR-PO-0412 quick fix.pdf, p. 1, Tips
[^r24]: 11_training/QRC-03 ERR-PO-0412 quick fix.pdf, p. 1, Tips
[^r6]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 18, ERR-PO-0412
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 6, §2. Purchase services
[^r13]: 04_service_definitions/purchase/po_save.yaml, errors
[^r25]: 11_training/intranet_export_2016/error_messages.html, Error messages
[^r27]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 3, §17. Messages
[^r26]: 02_procedures/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf, p. 3, §5. Procedure
[^r28]: 03_ledgerline_manuals/old/Ledgerline 7.0 Purchasing Manual (2015).pdf, p. 3, §17. Messages
