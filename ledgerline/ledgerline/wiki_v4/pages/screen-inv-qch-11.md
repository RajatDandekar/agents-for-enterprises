---
title: "INV-QCH-11 Quality Hold Entry"
type: "screen"
slug: "screen-inv-qch-11"
summary: "Ledgerline ERP screen to transfer suspect receipt items into quality hold, release them to free stock, or mark them as rejected."
audience: "staff"
status: "mixed"
sources: ["02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/qch_get.yaml", "04_service_definitions/inventory/qch_reject.yaml", "04_service_definitions/inventory/qch_release.yaml", "04_service_definitions/inventory/qch_save.yaml", "04_service_definitions/inventory/qch_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | INV-QCH-11 |
| Menu path | Inventory > Quality hold |
| Primary services | qch_save, qch_get, qch_search, qch_release, qch_reject |
| Status | current |
| Module | Inventory |

Screen INV-QCH-11 is accessed via menu Inventory > Quality hold and is used to transfer suspect receipt items into quality hold [^r1][^r3]. Placing items on hold reduces the location balance for main stores, records the balance against the quality hold location, and prevents serial numbers from being allocated to pick lists or assembly orders [^r1]. Once processed, items can either be cleared back to free stock or flagged as rejected stock for vendor return [^r6][^r7]. If an error indicates a serial number is already allocated to a build, stores supervision must strip the allocation from the production order rather than cancelling the quarantine transaction [^r2].

| Key | Value |
|---|---|
| Screen code | INV-QCH-11 [^r3] |
| Menu path | Inventory > Quality hold [^r3] |
| Primary services | qch_save, qch_get, qch_search, qch_release, qch_reject [^r3] |
| Status | current [^r3] |
| Module | Inventory [^r3] |

## Fields

Screen INV-QCH-11 contains the following data entry and display fields:

* **GRN NO** (`grn_no`): Goods receipt note number; mandatory [^r4][^r9]. It is also used as a search filter in `qch_search` [^r17].
* **ITEM CD** (`itm_cd`): Item code; mandatory [^r4][^r9]. It is also handled as a search filter in `qch_search` [^r17].
* **QTY** (`qty`): Quantity to place on quality hold; mandatory [^r4][^r9]. Quantities cannot be amended directly once saved [^r8]. It serves as a search filter in `qch_search` [^r17].
* **QCH NO** (`qch_no`): Quality hold reference number; mandatory [^r4][^r9]. It receives a system-generated reference upon save, which must be transcribed onto the physical quarantine label [^r5]. It serves as the primary lookup key for retrieval, release, and rejection [^r13][^r14][^r15].
* **REASON** (`reason`): Reason for quarantine hold or rejection; optional on entry and used during reject processing [^r4][^r9][^r14].
* **STATUS** (`status`): Record status; optional on entry [^r4][^r9]. It is set to hold upon save, updated to show cleared when released, or set to rejected stock when rejected [^r5][^r6][^r7]. It is also used as a search filter in `qch_search` [^r17].
* **COMMENT** (`comment`): Additional descriptive remarks; optional [^r4][^r9][^r15].

## Keys and services

Screen INV-QCH-11 interfaces with [[services-inv-qch|INV qch services]]:

* **qch_save** (F8): Write service executed to place goods receipt item quantities on quality hold and assign a generated reference in `qch_no` [^r5][^r10][^r11][^r16].
* **qch_get** (F3): Read service executed to retrieve quality hold record details by `qch_no` [^r10][^r12][^r13].
* **qch_search**: Read service used to query and list quality hold entries using filters `grn_no`, `itm_cd`, `qty`, and `status` [^r3][^r10][^r17].
* **qch_release** (F9): Write service (`POST /ll72/svc/qch_release`) executed using required field `qch_no` and optional field `comment` to clear hold flags and transfer parts to free stock [^r6][^r10][^r15].
* **qch_reject** (Shift+F9): Write service (`POST /ll72/svc/qch_reject`) executed using `qch_no` and `reason` to flag items as rejected stock in the inventory ledger so purchasing can issue vendor returns or debit notes [^r7][^r10][^r14].

Direct quantity amendments on existing saved records are blocked; users must process the open record and log a new transaction for any remaining balance [^r8].

## Messages

The screen throws error codes from [[errors-qch|ERR-QCH Quality Hold Error Codes]] and related item validations [^r10]:

* `ERR-QCH-0001` [^r10]
* `ERR-QCH-0007` [^r10]
* `ERR-QCH-0201` [^r10]
* `ERR-QCH-0350`: Inspection Not Posted [^r10]
* [[err-itm-0011|ERR-ITM-0011]]: Item validation error [^r10]

## Versions and conflicts

* **Quality hold entry workflow (superseded)**: Under current Ledgerline ERP 7.2.3 documentation and SOP-QUA-002 v1.1, screen INV-QCH-11 manages transfers of suspect battery packs and parts to quality hold locations, preventing serial number allocations to pick lists and supporting release to free stock or rejection for vendor debit notes [^r1][^r3][^r6][^r7]. In the superseded manual MAN-INV-72 v7.2.2 (dated 2024-06-10), INV-QCH-11 was described specifically for goods inwards and inspection staff to quarantine delivered components failing visual inspection, lacking paperwork, or needing technical appraisal [^r18]. Both versions maintain the same required fields (`grn_no`, `itm_cd`, `qty`, `qch_no`) and optional fields (`reason`, `status`, `comment`) [^r4][^r19].

## See also

* [[services-inv-qch|INV qch services]]
* [[errors-qch|ERR-QCH Quality Hold Error Codes]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[items-bat|BAT-* items]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[screen-qa-ins-01|QA-INS-01 Incoming Inspection Entry]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]

## References

[^r1]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 29, §10. Quality Hold (INV-QCH-11)
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 31, Step by step
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 31, Step by step
[^r2]: 02_procedures/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 29, §10. Quality Hold (INV-QCH-11)
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 17, INV-QCH-11 QUALITY HOLD ENTRY
[^r17]: 04_service_definitions/inventory/qch_search.yaml, service: qch_search
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 33, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 30, Step by step
[^r13]: 04_service_definitions/inventory/qch_get.yaml, service: qch_get
[^r14]: 04_service_definitions/inventory/qch_reject.yaml, service
[^r15]: 04_service_definitions/inventory/qch_release.yaml, whole file
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 18, INV-QCH-11 QUALITY HOLD ENTRY
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 16, qch_save QUALITY HOLD SAVE
[^r16]: 04_service_definitions/inventory/qch_save.yaml, screen
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 17, qch_get QUALITY HOLD GET
[^r18]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 14, Quality Hold (INV-QCH-11)
[^r19]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 13, §10. Quality Hold (INV-QCH-11)
