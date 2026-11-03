---
title: "PRD bom services"
type: "service-group"
slug: "services-prd-bom"
summary: "Ledgerline PRD production services for bill of materials maintenance, multi-level explosions, copies, searches, and where-used analysis."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/production/bom_copy.yaml", "04_service_definitions/production/bom_explode.yaml", "04_service_definitions/production/bom_get.yaml", "04_service_definitions/production/bom_save.yaml", "04_service_definitions/production/bom_search.yaml", "04_service_definitions/production/bom_where_used.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-prd-bom |
| module | PRD |
| screen | PRD-BOM-02 |
| status | current |
| version | 7.2.3 |
| services_count | 6 |

The `bom` service group provides core Ledgerline production module APIs to query, persist, duplicate, and analyze bills of materials [^r7][^r8][^r9]. All operations are primarily accessed through screen [[screen-prd-bom-02|PRD-BOM-02]] and require valid user authorization and session credentials [^r7][^r15][^r20]. These endpoints manage single-level definitions as well as complete indented explosions and where-used component tracing across assemblies [^r4][^r5].

## Services

### bom_get

Retrieves component rows for an entered parent item code, populating fields including COMPONENT, QTY PER, SCRAP %, and STATUS in the grid [^r1][^r25].

* **Type**: Read [^r25]
* **Endpoint**: `POST /ll72/svc/bom_get` [^r25]
* **Authentication**: Requires a session token in the `X-LL-Session` header and an authorized user role [^r26].
* **Screen shortcut**: F3 on [[screen-prd-bom-02|PRD-BOM-02]] [^r7]
* **Required fields**: `parent` (string) [^r8][^r27]
* **Optional fields**: None [^r27]
* **Errors**: [[err-bom-0001|ERR-BOM-0001]], [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r8][^r28][^r29]
* **Source file**: `04_service_definitions/production/bom_get.yaml` [^r25]

### bom_save

Validates and commits bill of materials line components via backend procedure `sp_bom_save` [^r2][^r9][^r30].

* **Type**: Write [^r30]
* **Endpoint**: `POST /ll72/svc/bom_save` [^r30]
* **Authentication**: Requires a session token in the `X-LL-Session` header and an authorized user role [^r31].
* **Screen shortcut**: F8 on [[screen-prd-bom-02|PRD-BOM-02]] [^r7]
* **Required fields**: `parent` (string), `component` (string), `qty` (float) [^r9][^r32]
* **Optional fields**: `scrap_pct` (float) [^r9][^r32]
* **Errors**: [[err-bom-0120|ERR-BOM-0120]], [[err-bom-0201|ERR-BOM-0201]], [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r2][^r9][^r34][^r35]
* **Source file**: `04_service_definitions/production/bom_save.yaml` [^r30]

### bom_search

Invokes the bill of materials list query to find assemblies matching entered parameters [^r6][^r36].

* **Type**: Read [^r36]
* **Endpoint**: `POST /ll72/svc/bom_search` [^r37]
* **Authentication**: Requires a session token in the `X-LL-Session` header and an authorized user role [^r37].
* **Screen shortcut**: F2/Enter on [[screen-prd-bom-02|PRD-BOM-02]] [^r7]
* **Required fields**: None [^r10][^r38]
* **Optional fields**: `parent` (string), `component` (string), `qty` (float), `status` (string) [^r10][^r38]
* **Errors**: [[err-bom-0201|ERR-BOM-0201]], [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r40][^r41]
* **Source file**: `04_service_definitions/production/bom_search.yaml` [^r36]

### bom_copy

Duplicates an existing parent's complete component structure into the working area for a target parent item using stored procedure `sp_bom_copy` [^r3][^r11][^r17].

* **Type**: Write [^r14]
* **Endpoint**: `POST /ll72/svc/bom_copy` [^r14]
* **Authentication**: Requires a session token in the `X-LL-Session` header and an authorized user role [^r15].
* **Screen**: [[screen-prd-bom-02|PRD-BOM-02]] [^r7]
* **Required fields**: `parent` (string) [^r11][^r16]
* **Optional fields**: `component` (string), `qty` (float), `scrap_pct` (float) [^r11][^r16]
* **Errors**: [[err-bom-0001|ERR-BOM-0001]], [[err-bom-0201|ERR-BOM-0201]], [[err-itm-0011|ERR-ITM-0011]] [^r18]
* **Source file**: `04_service_definitions/production/bom_copy.yaml` [^r14]

### bom_explode

Generates an indented multi-level explosion of all subordinate sub-assemblies down to the lowest purchase item level [^r4][^r12][^r19].

* **Type**: Read [^r19]
* **Endpoint**: `POST /ll72/svc/bom_explode` [^r20]
* **Authentication**: Requires a session token in the `X-LL-Session` header and an authorized user role [^r20].
* **Screen**: [[screen-prd-bom-02|PRD-BOM-02]] [^r7][^r19]
* **Required fields**: `parent` (string) [^r12][^r21]
* **Optional fields**: None [^r21]
* **Errors**: [[err-bom-0001|ERR-BOM-0001]], [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r23][^r24]
* **Source file**: `04_service_definitions/production/bom_explode.yaml` [^r19]

### bom_where_used

Identifies all parent assemblies across production that consume a specified component part code [^r5][^r13][^r42].

* **Type**: Read [^r42]
* **Endpoint**: `POST /ll72/svc/bom_where_used` [^r42]
* **Authentication**: Requires a session token in the `X-LL-Session` header and an authorized user role [^r43].
* **Screen**: [[screen-prd-bom-02|PRD-BOM-02]] [^r7]
* **Required fields**: `parent` (string) [^r13][^r44]
* **Optional fields**: None [^r44]
* **Errors**: [[err-bom-0001|ERR-BOM-0001]], [[err-itm-0011|ERR-ITM-0011]], ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r46][^r47]
* **Source file**: `04_service_definitions/production/bom_where_used.yaml` [^r42]

## See also

* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[errors-bom|ERR-BOM Error Code Reference]]
* [[err-bom-0001|ERR-BOM-0001 Parent assembly not found on bill of materials master]]
* [[err-bom-0120|ERR-BOM-0120 Circular or recursive bill of materials structure detected]]
* [[err-bom-0201|ERR-BOM-0201 Component line missing or invalid data]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[services-prd-wo|PRD wo services]]
* [[services-prd-ecn|PRD ecn services]]
* [[screen-prd-rtg-03|PRD-RTG-03 Routing]]

## References

[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 21, PRD-BOM-02 BILL OF MATERIALS
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 54, §6. Production services
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 54, §6. Production services
[^r15]: 04_service_definitions/production/bom_copy.yaml, auth
[^r20]: 04_service_definitions/production/bom_explode.yaml, auth
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Step by step
[^r5]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Step by step
[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 8, Step by step
[^r25]: 04_service_definitions/production/bom_get.yaml, service: bom_get
[^r26]: 04_service_definitions/production/bom_get.yaml, auth
[^r27]: 04_service_definitions/production/bom_get.yaml, request.fields
[^r28]: 04_service_definitions/production/bom_get.yaml, errors
[^r29]: 04_service_definitions/production/bom_get.yaml, common_errors
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Step by step
[^r30]: 04_service_definitions/production/bom_save.yaml, bom_save
[^r31]: 04_service_definitions/production/bom_save.yaml, bom_save
[^r32]: 04_service_definitions/production/bom_save.yaml, request.fields
[^r34]: 04_service_definitions/production/bom_save.yaml, errors
[^r35]: 04_service_definitions/production/bom_save.yaml, common_errors
[^r6]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 8, Step by step
[^r36]: 04_service_definitions/production/bom_search.yaml, service: bom_search
[^r37]: 04_service_definitions/production/bom_search.yaml, endpoint
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 54, §6. Production services
[^r38]: 04_service_definitions/production/bom_search.yaml, request.fields
[^r40]: 04_service_definitions/production/bom_search.yaml, errors
[^r41]: 04_service_definitions/production/bom_search.yaml, common_errors
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 9, Step by step
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 54, §6. Production services
[^r17]: 04_service_definitions/production/bom_copy.yaml, procedures
[^r14]: 04_service_definitions/production/bom_copy.yaml, service: bom_copy
[^r16]: 04_service_definitions/production/bom_copy.yaml, request.fields
[^r18]: 04_service_definitions/production/bom_copy.yaml, errors
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 54, §6. Production services
[^r19]: 04_service_definitions/production/bom_explode.yaml, service: bom_explode
[^r21]: 04_service_definitions/production/bom_explode.yaml, request.fields
[^r23]: 04_service_definitions/production/bom_explode.yaml, errors
[^r24]: 04_service_definitions/production/bom_explode.yaml, common_errors
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 55, §6. Production services
[^r42]: 04_service_definitions/production/bom_where_used.yaml, header
[^r43]: 04_service_definitions/production/bom_where_used.yaml, auth
[^r44]: 04_service_definitions/production/bom_where_used.yaml, request.fields
[^r46]: 04_service_definitions/production/bom_where_used.yaml, errors
[^r47]: 04_service_definitions/production/bom_where_used.yaml, common_errors
