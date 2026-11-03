---
title: "PUR-SUP-03 Supplier Enquiry"
type: "screen"
slug: "screen-pur-sup-03"
summary: "Ledgerline screen to search and inspect supplier records, verify duplicate profiles, and resolve missing supplier errors before onboarding or purchase order creation."
audience: "staff"
status: "mixed"
sources: ["05_master_data/SUPPLIER_MASTER.xlsx", "01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf", "01_policies/POL-SUP-003 Supplier Policy v2.3.pdf", "01_policies/old/Supplier_Policy_v2.2.docx", "02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/purchase/sup_search.yaml", "11_training/intranet_export_2016/supplier_list.html"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PUR-SUP-03 |
| Screen name | Supplier Enquiry |
| Module | Purchase |
| Menu path | Purchase > Supplier |
| Authorized roles | PUR-EXEC, PUR-SR, SYS-ADMIN |
| Primary service | sup_search |
| Endpoint | POST /ll72/svc/sup_search |

Screen PUR-SUP-03 is Ledgerline's enquiry interface for searching and retrieving live supplier master records [^r5][^r8][^r11]. Staff across purchasing, stores, and accounts must query supplier details directly from this screen instead of using unmaintained legacy spreadsheets or local shortcuts [^r11][^r12]. As of 26 October 2026, it serves as the mandatory check to ensure no duplicate vendor profile exists before onboarding a supplier under [[pol-sup-003|POL-SUP-003]] and [[sop-pur-001|SOP-PUR-001]] [^r2][^r3].

| Field | Detail |
|---|---|
| Screen code | PUR-SUP-03 [^r8] |
| Screen name | Supplier Enquiry [^r8][^r9] |
| Module | Purchase [^r8] |
| Menu path | Purchase > Supplier [^r8] |
| Roles | PUR-EXEC, PUR-SR, SYS-ADMIN [^r8] |
| Service | sup_search [^r8][^r9] |
| Endpoint | POST /ll72/svc/sup_search [^r9] |

## Fields

Screen PUR-SUP-03 requires the search parameter `NAME LIKE` (`q`) to query suppliers by name pattern [^r8][^r10]. Searches perform partial text matching on the entered characters without matching spelling variants [^r5]. Before creating a supplier, procedures require querying by one short, distinctive word of the supplier name, followed by queries against city and VAT registration number to detect duplicates [^r2][^r3][^r14].

The search results list displays the following fields [^r5]:
* Supplier code [^r5]
* Name [^r5]
* City [^r5]
* Country [^r5]
* Status [^r5]

Blocked suppliers appear highlighted in red on the results list [^r6]. A supplier whose name has `(old code, do not use)` appended indicates that the record has been replaced by a new active supplier code [^r6].

Double-clicking a supplier row displays detailed master fields [^r7]:
* VAT registration number [^r7]
* Contact address and dispatch locations for both the Manchester factory and the Leeds site [^r7][^r13]
* Approved payment terms [^r7][^r13]
* Certificates [^r7]
* Rate contracts [^r7]

The screen also exports the complete supplier master record, which includes the supplier code, name, VAT number, country code, city, status, payment terms, supply type, creation details, contact, and email [^r1]. Under onboarding procedures, operators must print the screen output for inclusion in the physical onboarding file [^r3].

## Keys and services

PUR-SUP-03 is accessed via the menu path Purchase > Supplier by users assigned to roles PUR-EXEC, PUR-SR, or SYS-ADMIN [^r8].

* **Enter / Search**: Submits the query `q` to the backend read service `sup_search` via `POST /ll72/svc/sup_search`, which belongs to [[services-pur-sup]] [^r8][^r9][^r10].
* **Double-click row**: Opens full vendor details, including rate contracts, certificates, addresses, and terms [^r7].
* **F2 lookup**: Provides a quick lookup function across purchasing operations to locate supplier codes when working outside PUR-SUP-03 [^r4].

## Messages

* `ERR-SUP-0030 SUPPLIER NOT FOUND`: Raised when a supplier code cannot be found in Ledgerline; operator guidance directs users to screen PUR-SUP-03 or the F2 lookup key to identify the valid code [^r4].

## Versions and conflicts

* Today's rule: Under POL-SUP-003 v2.3 (effective 2026-04-01) and SOP-PUR-001 v3.1 (effective 2026-09-01), PUR-SUP-03 must be queried by name, city, and VAT registration number prior to submitting an onboarding file [^r2][^r3][^r14].
* Older rule: Under POL-PUR-001 containing superseded POL-SUP-003 v2.2, the pre-onboarding search requirement was specified under earlier onboarding provisions [^r15].
* Sources and dates: POL-SUP-003 v2.3 (2026-04-01) and SOP-PUR-001 v3.1 (2026-09-01) versus POL-PUR-001 / POL-SUP-003 v2.2 [^r2][^r3][^r15].
* Kind: superseded [^r15].

## See also

* [[err-sup-0030|ERR-SUP-0030]]
* [[pol-sup-003|POL-SUP-003 Supplier Policy]]
* [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
* [[screen-pur-sup-01|PUR-SUP-01 Supplier Master Create]]
* [[services-pur-sup|PUR sup services]]

## References

[^r5]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 4, §5.2 Searching
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 30, PUR-SUP-03 SUPPLIER ENQUIRY
[^r11]: 11_training/intranet_export_2016/supplier_list.html, Supplier list
[^r12]: 11_training/intranet_export_2016/supplier_list.html, Supplier list
[^r2]: 01_policies/POL-SUP-003 Supplier Policy v2.3.pdf, p. 1, §3. Onboarding a new supplier
[^r3]: 02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf, p. 3, §5. Procedure
[^r9]: 04_service_definitions/purchase/sup_search.yaml, service: sup_search
[^r10]: 04_service_definitions/purchase/sup_search.yaml, request
[^r14]: 01_policies/POL-SUP-003 Supplier Policy v2.3 (1).pdf, p. 3, Checking for duplicate master records
[^r6]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 4, §5.3 Reading the list
[^r7]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 5, §5.4 Supplier details
[^r13]: 11_training/intranet_export_2016/supplier_list.html, Supplier list
[^r1]: 05_master_data/SUPPLIER_MASTER.xlsx, sheet Suppliers, SHEET Suppliers
[^r4]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 25, ERR-SUP-0030 SUPPLIER NOT FOUND
[^r15]: 01_policies/old/Supplier_Policy_v2.2.docx, §3. Onboarding a new supplier
