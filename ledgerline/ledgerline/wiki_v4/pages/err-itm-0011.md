---
title: "ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE"
type: "error"
slug: "err-itm-0011"
summary: "Ledgerline error ERR-ITM-0011 raised when an item code does not exist in master records or holds an inactive status."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-ITM-0011 |
| Standard message | ITEM NOT FOUND OR INACTIVE |
| Type | Error |
| Owner | Inventory Control / Manufacturing |
| Status | Current |

ERR-ITM-0011 is a Ledgerline ERP error indicating that a specified item code cannot be found in the item master files or is flagged as inactive, obsolete, or restricted [^r1][^r7][^r11][^r20]. It displays the message text 'ITEM NOT FOUND OR INACTIVE' in central message tables across inventory, production, and sales functions [^r7][^r16][^r20]. The error stops transactions across inventory adjustments, Kanban setups, scrap entry, works orders, master scheduling, serial registration, and demo bike entries until master records, bill of materials links, or entry codes are resolved [^r5][^r11][^r13][^r18][^r21].

## Meaning

ERR-ITM-0011 displays 'ITEM NOT FOUND OR INACTIVE' across system message tables [^r7][^r16][^r20]. It signals that an item code entered in fields such as ITEM CD, ITM CD, or COMPONENT does not exist in the active item master database, has leading spaces, or is marked with an inactive, superseded, archived, deleted, or phased-out status [^r1][^r4][^r8][^r10][^r15][^r17][^r18]. It also indicates that an item is not flagged as an active production item for internal manufacture, is not authorised for consignment handling, or represents a bought-out status prohibiting production issues [^r6][^r8][^r10][^r16].

## Cause

The error occurs under the following operational conditions:
* **Item master absence or status flags:** The item code does not exist in inventory master files or central part catalogues, or has been flagged as inactive, deleted, discontinued, superseded, or obsolete [^r1][^r4][^r6][^r11][^r17][^r18].
* **Input errors:** Typographical errors in part code spelling or leading spaces in ITEM CD [^r9][^r12][^r15][^r17].
* **Production and scrap mismatches:** A component entered in COMPONENT does not allow production issues [^r8]. During works order scrap entry on screen [[screen-prd-scp-12|PRD-SCP-12]], service `scp_save` raises ERR-ITM-0011 if the ITEM CD is not recognised or is not linked to the active bill of materials (BOM) for the selected works order [^r13].
* **Engineering change delays:** Engineering change tasks are incomplete, or the part is not active against engineering release sheets during `mps_get` or `mps_save` execution [^r11][^r12].
* **Serial and finished goods discrepancies:** During serial registration via `srl_reg` on screen [[screen-sal-srl-16|SAL-SRL-16]], the ITEM CD does not exist in the finished goods master or is marked superseded or archived [^r18]. On screen [[screen-sal-dmo-17|SAL-DMO-17]], DEMO BIKE SAVE raises the error when ITEM CD does not reconcile with SERIAL NO, the serial does not exist in serial tracking, final inspection sign-off is incomplete, or ITEM CD is not an active finished part [^r21].
* **Field validation discrepancy:** In item master maintenance, an entry format error or missing mandatory data raises the code [^r2].

## How to fix

Resolution depends on the transaction being executed:
* **Verify part code entry:** Check spelling for typographical mistakes and eliminate leading spaces in ITEM CD or COMPONENT [^r9][^r12][^r17].
* **Inventory maintenance and Kanban:** When ERR-ITM-0011 appears during Kanban card setup or retrieval, check the parts register or contact the inventory supervisor rather than re-saving [^r5]. For item master maintenance errors, verify that ITEM CD, DESCRIPTION, UOM, and CATEGORY contain valid text, LITHIUM CELL (0/1) contains a single-digit flag, REORDER LVL contains a valid figure, and REASON is not blank when blocking [^r3].
* **Production issue and engineering status:** Verify item creation in the item master, confirm its status permits transactions, and cross-reference engineering release sheets to ensure engineering change tasks are complete [^r9][^r12].
* **Production scrap:** On screen [[screen-prd-scp-12|PRD-SCP-12]], verify the physical label against the parts list [^r14]. If the item was issued as an unlisted substitute, production control must update the works order before saving [^r14].
* **Serial registration and demo bikes:** If registration is rejected by `srl_reg`, cross-reference the workshop traveller with the finished goods price list or BOM, correct the ITEM CD, and retry `srl_reg` [^r19]. For demo bike entries on screen [[screen-sal-dmo-17|SAL-DMO-17]], confirm that the serial exists in tracking, matches the finished part code, and has completed final inspection sign-off [^r21].

## Raised by

ERR-ITM-0011 is raised by multiple modules, services, and screens:
* **Inventory:** Inventory master maintenance and Kanban setup/retrieval [^r2][^r5].
* **Production:** Services `mps_get` and `mps_save` during MPS maintenance, and service `scp_save` on screen [[screen-prd-scp-12|PRD-SCP-12]] [^r11][^r13]. Also raised on component entry screens for production issues and internal manufacture setup [^r8][^r16].
* **Sales:** Action `srl_reg` on finished goods serial registration (screen [[screen-sal-srl-16|SAL-SRL-16]]) and DEMO BIKE SAVE on screen [[screen-sal-dmo-17|SAL-DMO-17]] [^r18][^r21].

## Versions and conflicts

* **Contradiction on error meaning:** In general inventory, production, and sales contexts, ERR-ITM-0011 indicates that an entered item code does not exist in master records or holds an inactive status [^r1][^r4][^r7][^r8][^r10][^r15][^r17][^r20]. However, [[man-inv-72|MAN-INV-72]] (p. 43) also defines ERR-ITM-0011 as indicating that a mandatory field is missing or an invalid format is detected during item master maintenance (requiring validation of DESCRIPTION, UOM, CATEGORY, LITHIUM CELL, REORDER LVL, and REASON) [^r2][^r3].

## See also

* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[screen-prd-scp-12|PRD-SCP-12 Production Scrap Entry]]
* [[screen-sal-dmo-17|SAL-DMO-17 Demo Bike Entry]]
* [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]
* [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 27, Messages
[^r7]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 68, §20. Messages
[^r11]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Messages
[^r20]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 70, §21. Messages
[^r16]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 53, Questions users ask
[^r13]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Messages
[^r18]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 65, Messages
[^r21]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 70, Questions users ask
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 51, Messages
[^r8]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 10, Messages
[^r10]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 13, Messages
[^r15]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 71, Messages
[^r17]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 58, Messages
[^r6]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 66, Messages
[^r9]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 10, Messages
[^r12]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 27, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 43, Messages
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 43, Messages
[^r14]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 56, Messages
[^r19]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 65, Messages
