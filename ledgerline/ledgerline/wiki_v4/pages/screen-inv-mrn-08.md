---
title: "INV-MRN-08 Material Issue Entry"
type: "screen"
slug: "screen-inv-mrn-08"
summary: "Material issue screen used to record and post component issues against released work orders and allocate battery serial numbers."
audience: "staff"
status: "mixed"
sources: ["02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/mrn_cancel.yaml", "04_service_definitions/inventory/mrn_get.yaml", "04_service_definitions/inventory/mrn_post.yaml", "04_service_definitions/inventory/mrn_save.yaml", "04_service_definitions/inventory/mrn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | INV-MRN-08 |
| title | Material Issue Entry |
| module | Inventory |
| navigation | Inventory > Material issue |
| status | current |

Screen INV-MRN-08 (Material Issue Entry) records the issue of components, sub-assemblies, and raw stock against released production orders in Ledgerline [^r3][^r7][^r20]. Navigated via Inventory > Material issue, it operates through the [[services-inv-mrn|INV mrn services]] group to save, search, retrieve, post, and cancel material issue notes [^r3][^r14]. Under standard assembly procedure, [[items-bat|battery packs]] must be issued individually by scanned serial number on this screen and allocated directly to the designated [[screen-prd-wo-01|work order]] number [^r1]. The total count of scanned battery pack serials booked on INV-MRN-08 must balance exactly with the finished electric bicycle count reported on the completion screen [^r2].

## Fields

INV-MRN-08 contains both header and line data required to construct and allocate a material issue note [^r4][^r10]:

| Field | Parameter | Requirement | Description |
|---|---|---|---|
| WO NO | `wo_no` | Mandatory | Target work order identifier; must reference an active, released order [^r4][^r7][^r11]. |
| ITEM CD | `itm_cd` | Mandatory | Component part code; must exist in the active item master and not be obsolete [^r4][^r7][^r11]. |
| QTY | `qty` | Mandatory | Quantity of the component to issue; must be greater than zero [^r4][^r11][^r13]. |
| WHS CD | `whs_cd` | Non-mandatory / Optional | Source warehouse code for picking stock [^r4][^r10][^r11]. |
| MRN NO | `mrn_no` | Mandatory | Material issue reference number; left blank during initial creation for automatic sequential assignment by Ledgerline upon save [^r4][^r5][^r11]. |
| STATUS | `status` | Non-mandatory / Optional | Document processing state (shifts to posted upon completion) [^r4][^r6][^r11]. |
| COMMENT | `comment` | Non-mandatory / Optional | User remarks or narrative notes [^r4][^r11]. |
| REASON | `reason` | Mandatory | Business justification code for the issue or cancellation [^r4][^r11][^r15]. |

## Keys and services

INV-MRN-08 executes transaction processing by binding user keyboard shortcuts to backend [[services-inv-mrn|INV mrn services]] endpoints [^r3][^r12][^r14]:

* **Save (`F8`)**: Invokes write service `mrn_save` (endpoint `POST /ll72/svc/mrn_save`) to write or update draft issue records [^r12][^r14][^r18]. Leaving `mrn_no` empty prompts the service to assign the next sequential identifier [^r5].
* **Get**: Calls read service `mrn_get` (endpoint `POST /ll72/svc/mrn_get`) using key parameter `mrn_no` to retrieve existing records [^r3][^r12][^r16].
* **Search (`F2` / `Enter`)**: Executes read service `mrn_search` (endpoint `POST /ll72/svc/mrn_search`) to query issues matching criteria such as `wo_no`, `itm_cd`, `qty`, and `status` [^r12][^r19].
* **Post (`F9`)**: Executes write service `mrn_post` (endpoint `POST /ll72/svc/mrn_post`), which deducts physical available stock, updates perpetual inventory records, adjusts the works order build ledger, and changes the document status to posted [^r6][^r12][^r17].
* **Cancel (`Shift+F8`)**: Triggers write service `mrn_cancel` (endpoint `POST /ll72/svc/mrn_cancel`) to cancel an issue using required parameters `mrn_no` and `reason` [^r12][^r14][^r15].

## Messages

The screen raises validation warnings and errors during entry, save, and posting actions [^r7][^r8][^r9][^r10][^r13]:

* `ERR-MRN-0001`: Raised when an issue note requested via `mrn_get` does not exist in the database [^r9][^r13].
* `ERR-MRN-0007`: Fired when attempting to modify or post an issue note that is already cancelled [^r9][^r13].
* [[err-itm-0011|ERR-ITM-0011]]: Raised when `itm_cd` is missing from the active item master or is flagged as obsolete [^r7][^r13].
* `ERR-WO-0007`: Raised when `wo_no` does not reference an active, released works order [^r7][^r13].
* `ERR-STK-0102`: Raised during posting (`mrn_post`) if the requested `qty` exceeds physical available stock in the designated warehouse, preventing negative inventory balances [^r8][^r13].
* `ERR-MRN-0201`: Raised when attempting to save or post a document that is already posted, or when entered issue quantity is not greater than zero [^r9][^r13].
* `ERR-MRN-0801`: Raised during `mrn_save` or `mrn_post` if mandatory header or line details (`wo_no`, `itm_cd`, `qty`, `whs_cd`) are missing [^r10][^r13].

## Versions and conflicts

* **Superseded manual specifications**: Current manual MAN-INV-72 v7.2.3 and service definitions govern current system behaviour on INV-MRN-08 [^r3][^r6][^r15]. The superseded v7.2.2 manual (dated 2024-06-10) previously stated that `mrn_cancel` could only discard unposted draft entries and could not clear posted records [^r20][^r21][^r22].

## See also

* [[services-inv-mrn|INV mrn services]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[items-bat|BAT-* items]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[screen-inv-lot-10|INV-LOT-10 Lot / Serial Entry]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-inv-whs-01|INV-WHS-01 Warehouse Master]]

## References

[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 20, Messages
[^r20]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 9, Material Issue (INV-MRN-08)
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 14, mrn_save MATERIAL ISSUE SAVE
[^r1]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r2]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 18, §7. Material Issue (INV-MRN-08)
[^r10]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 20, Messages
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 16, INV-MRN-08 MATERIAL ISSUE ENTRY
[^r13]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 17, INV-MRN-08 MATERIAL ISSUE ENTRY
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 19, Step by step
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 19, Step by step
[^r15]: 04_service_definitions/inventory/mrn_cancel.yaml, service: mrn_cancel
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 17, INV-MRN-08 MATERIAL ISSUE ENTRY
[^r18]: 04_service_definitions/inventory/mrn_save.yaml, whole file
[^r16]: 04_service_definitions/inventory/mrn_get.yaml, service: mrn_get
[^r19]: 04_service_definitions/inventory/mrn_search.yaml, service: mrn_search
[^r17]: 04_service_definitions/inventory/mrn_post.yaml, screen: INV-MRN-08
[^r8]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 20, Messages
[^r9]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 20, Messages
[^r21]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 9, §7. Material Issue (INV-MRN-08)
[^r22]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 10, Questions users ask
