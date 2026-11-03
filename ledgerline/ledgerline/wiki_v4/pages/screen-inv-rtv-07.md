---
title: "INV-RTV-07 Return To Vendor Entry"
type: "screen"
slug: "screen-inv-rtv-07"
summary: "Ledgerline screen used to raise, post, and cancel Return to Vendor entries against goods receipt notes within 30 days."
audience: "staff"
status: "mixed"
sources: ["01_policies/POL-RET-006 Returns Policy v2.1.pdf", "02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/rtv_cancel.yaml", "04_service_definitions/inventory/rtv_get.yaml", "04_service_definitions/inventory/rtv_post.yaml", "04_service_definitions/inventory/rtv_save.yaml", "04_service_definitions/inventory/rtv_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-RTV-07 |
| Name | Return To Vendor Entry |
| Module | Inventory |
| Menu path | Inventory > Return to |
| Status | Current |

Screen INV-RTV-07 is the Ledgerline ERP 7.2 screen used to raise return to vendor (RTV) transactions for faulty or incorrect goods within 30 days of receipt [^r1][^r3]. It validates returns against the goods receipt note, incoming inspection delivery paperwork, purchase order references, and received quantities [^r3]. The screen halts transactions if the supplier invoice has already been matched and posted in purchase ledger processing [^r2][^r5].

## Fields

The screen contains both mandatory and optional fields for recording returns [^r6][^r13]:

| Field | Code | Requirement | Description |
|---|---|---|---|
| GRN NO | `grn_no` | Mandatory | Goods receipt note reference number [^r6][^r13]. |
| QTY | `qty` | Mandatory | Return quantity; must be greater than zero, cannot exceed received quantity, and cannot exceed the remaining unissued, accepted balance on the receipt line [^r4][^r6][^r13][^r20]. |
| REASON CD | `reason_cd` | Mandatory | Return reason code; entering a valid code automatically populates REASON [^r6][^r7][^r13]. |
| REASON | `reason` | Mandatory | Master description populated from REASON CD [^r6][^r7][^r13]. |
| RTV NO | `rtv_no` | Mandatory | Return to vendor record identifier [^r6][^r13][^r17]. |
| NCR NO | `ncr_no` | Optional | Non-conformance report reference; must be an authorized, completed report before shipping goods off site [^r6][^r12][^r13]. |
| REMARKS | `remarks` | Optional | Additional free-text remarks [^r6][^r13]. |
| STATUS | `status` | Optional | Current processing status; shows draft abandoned when cancelled, or complete when posted [^r6][^r8][^r10][^r13]. |
| COMMENT | `comment` | Optional | Additional comment notes [^r6][^r13]. |

When goods received at the Manchester factory are returned from the Leeds satellite unit, the inter-site transfer must be fully posted in Ledgerline ERP 7.2 before processing the return against the original GRN on INV-RTV-07 [^r9].

## Keys and services

INV-RTV-07 interfaces with the backend [[services-inv-rtv|INV rtv services]] group [^r15]:

* **rtv_search** (`F2`/`Enter`): Invoked to list return-to-vendor records [^r14][^r21].
* **rtv_get** (`F3`): Read service invoked via endpoint `POST /ll72/svc/rtv_get` using `rtv_no` to retrieve a return record [^r14][^r15][^r17].
* **rtv_save** (`F8`): Backend write service that records return entries, validating that quantity exceeds zero, does not exceed the received quantity, and that the GRN is not already invoiced [^r14][^r15][^r19][^r20].
* **rtv_post**: Write service invoked via `POST /ll72/svc/rtv_post` using underlying stored procedure `sp_rtv_post` [^r14][^r18]. It relieves stock from quarantine, updates the inventory ledger, and marks `status` as complete [^r10].
* **rtv_cancel**: Write service invoked via endpoint `POST /ll72/svc/rtv_cancel` to cancel draft Return to Vendor records [^r15][^r16]. For an unposted draft, it clears reserved quantities, resets lines, and marks `status` as abandoned [^r8].

## Messages

The screen raises codes from the [[errors-rtv|ERR-RTV]] catalogue:

* [[err-rtv-0230|ERR-RTV-0230]]: Raised to halt the return when the supplier invoice has already been matched and posted against the receipt line in the purchase ledger [^r2][^r5]. It is also raised if attempting to cancel an already posted return using `rtv_cancel`, which requires a fresh receipt through the intake screen instead [^r11].
* **ERR-RTV-0204**: Returned when `ncr_no` is empty, incorrect, or open, because an authorized completed non-conformance report is required prior to shipping goods off site [^r12].
* **ERR-RTV-0801**: Triggered upon executing `rtv_post` if inventory is locked or the accounting period is closed [^r10].

## Versions and conflicts

* **Superseded manual guidance**: Under current documentation MAN-INV-72 v7.2.3 (2025-01-15), screen handling, validations, and service interactions reflect ERP 7.2.3 rules [^r6][^r7][^r8][^r10]. The previous version MAN-INV-72 v7.2.2 (2024-06-10) documented that pressing `rtv_save` set `status` to draft and pressing `rtv_post` updated `status` to posted once carrier collection was confirmed [^r22][^r23][^r24]. Kind: `superseded`.

## See also

* [[pol-ret-006|POL-RET-006 Returns Policy]]
* [[sop-inv-002|SOP-INV-002 Returns to Vendor (RTV)]]
* [[services-inv-rtv|INV rtv services]]
* [[errors-rtv|ERR-RTV Return to Vendor Error Codes]]
* [[err-rtv-0230|ERR-RTV-0230 Invoice already posted against receipt]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]

## References

[^r1]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 1, §2. Returns to suppliers
[^r3]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 4, What to check on the screen
[^r2]: 01_policies/POL-RET-006 Returns Policy v2.1.pdf, p. 2, §2. Returns to suppliers
[^r5]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 4, What to check on the screen
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 14, §6. Return To Vendor (INV-RTV-07)
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 18, INV-RTV-07 RETURN TO VENDOR ENTRY
[^r4]: 02_procedures/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf, p. 4, What to check on the screen
[^r20]: 04_service_definitions/inventory/rtv_save.yaml, errors
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 15, Entering return details
[^r17]: 04_service_definitions/inventory/rtv_get.yaml, whole file
[^r12]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 16, Reversing or cancelling an unposted draft
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 17, Tips
[^r15]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 13, rtv_save RETURN TO VENDOR SAVE
[^r14]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 18, INV-RTV-07 RETURN TO VENDOR ENTRY
[^r21]: 04_service_definitions/inventory/rtv_search.yaml, service: rtv_search
[^r19]: 04_service_definitions/inventory/rtv_save.yaml, whole file
[^r18]: 04_service_definitions/inventory/rtv_post.yaml, service: rtv_post
[^r16]: 04_service_definitions/inventory/rtv_cancel.yaml, rtv_cancel
[^r11]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r22]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 7, §6. Return To Vendor (INV-RTV-07)
[^r23]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 7, §6. Return To Vendor (INV-RTV-07)
[^r24]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 8, §6. Return To Vendor (INV-RTV-07)
