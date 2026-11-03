---
title: "INV bin services"
type: "service-group"
slug: "services-inv-bin"
summary: "Ledgerline 7.2 services for physical bin location maintenance, lookups, and restrictions on screen INV-BIN-09."
audience: "staff"
status: "mixed"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf", "04_service_definitions/inventory/bin_block.yaml", "04_service_definitions/inventory/bin_get.yaml", "04_service_definitions/inventory/bin_save.yaml", "04_service_definitions/inventory/bin_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | INV |
| Target screen | [[screen-inv-bin-09|INV-BIN-09]] |
| Services | bin_save, bin_get, bin_search, bin_block |
| Introduced | Ledgerline 7.0 |
| Status | current |

The INV bin services support physical storage bin management, lookups, and operational restrictions across Manchester and Leeds facilities within Ledgerline ERP [^r1]. Operating in connection with screen [[screen-inv-bin-09|INV-BIN-09]], these services allow stores personnel to maintain bin definitions, query locations, retrieve location records, and apply immediate put-away blocks [^r1][^r5]. All four services have been standard components of the Inventory module since Ledgerline version 7.0 [^r10][^r15][^r20][^r26].

## Services

### bin_save
BIN MASTER SAVE is a write service executed via endpoint POST /ll72/svc/bin_save [^r6][^r20][^r21]. It invokes the database stored procedure `sp_bin_save` to validate that the parent warehouse exists, confirm the bin code is not duplicated, and commit location additions or amendments to the central inventory master file [^r4][^r6][^r24]. Calls require session authentication via header `X-LL-Session` under an authorised user role [^r21]. The standard response envelope supplies `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r23].

* Required fields: `whs_cd` (WHS CD, string), `bin_cd` (BIN CD, string) [^r6][^r22].
* Optional fields: `bin_type` (BIN TYPE, string), `max_qty` (MAX QTY, integer) [^r6][^r22].
* Errors: ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r24].
* Source file: `04_service_definitions/inventory/bin_save.yaml` [^r20].

### bin_get
BIN MASTER GET is a read service called at endpoint POST /ll72/svc/bin_get that retrieves the complete details of a single selected location record into screen [[screen-inv-bin-09|INV-BIN-09]] [^r3][^r7][^r15][^r16]. Requests require authentication using header `X-LL-Session` with an authorised role [^r16]. The service returns a standard response envelope containing `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r18].

* Required fields: `bin_cd` (BIN CD, string) [^r7][^r17].
* Optional fields: none [^r7][^r17].
* Errors: [[err-bin-0001|ERR-BIN-0001]] (BIN MASTER NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r7][^r14][^r19].
* Source file: `04_service_definitions/inventory/bin_get.yaml` [^r15].

### bin_search
BIN MASTER LIST is a read service exposed at endpoint POST /ll72/svc/bin_search [^r8][^r25][^r26]. It queries the database to populate a list of existing location records matching entered site (WHS CD) and bin prefix criteria on screen [[screen-inv-bin-09|INV-BIN-09]] [^r2][^r8][^r25]. Calls require an `X-LL-Session` session token and appropriate role authorisation [^r26]. The response envelope returns `rc` ('S | W | E'), `err_cd`, `msg`, and `data` [^r28].

* Required fields: none [^r8][^r27].
* Optional fields: `whs_cd` (WHS CD), `bin_cd` (BIN CD), `bin_type` (BIN TYPE), `status` (STATUS) [^r8][^r27].
* Errors: ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r29].
* Source file: `04_service_definitions/inventory/bin_search.yaml` [^r25].

### bin_block
BIN MASTER BLOCK is an Inventory write service invoked via endpoint POST /ll72/svc/bin_block and stored procedure `sp_bin_block` [^r6][^r9][^r10][^r13]. It places an immediate restriction on a bin by updating STATUS, logging the REASON, and preventing inward put-away, provided active pick lists are not currently being fulfilled from that location [^r5][^r9]. The request requires an `X-LL-Session` header under an authorised role [^r11].

* Required fields: `bin_cd` (BIN CD, string) [^r9][^r12].
* Optional fields: `reason` (REASON, string) [^r9][^r12].
* Errors: [[err-bin-0001|ERR-BIN-0001]] (BIN MASTER NOT FOUND), ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, ERR-SYS-0503 [^r9][^r14].
* Source file: `04_service_definitions/inventory/bin_block.yaml` [^r10].

## Versions and conflicts

* **Blocking effect on bin operations**: Under current manual [[man-inv-72|MAN-INV-72]] v7.2.3, `bin_block` prevents inward put-away provided active pick lists are not being fulfilled from that location [^r5]. Under superseded manual MAN-INV-72 v7.2.2 (dated 2024-06-10), `bin_block` was described as restricting both putaway and picking movements to the bay [^r31]. (Kind: `superseded`)

## See also

* [[screen-inv-bin-09|INV-BIN-09 Bin Master Entry]]
* [[err-bin-0001|ERR-BIN-0001 Location not found or invalid format]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[services-inv-whs|INV whs services]]
* [[services-inv-itm|INV itm services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 22, §8. Bin Master (INV-BIN-09)
[^r5]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 23, Step by step
[^r10]: 04_service_definitions/inventory/bin_block.yaml, whole file
[^r15]: 04_service_definitions/inventory/bin_get.yaml, whole file
[^r20]: 04_service_definitions/inventory/bin_save.yaml, whole file
[^r26]: 04_service_definitions/inventory/bin_search.yaml, endpoint
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 15, bin_save BIN MASTER SAVE
[^r21]: 04_service_definitions/inventory/bin_save.yaml, auth
[^r4]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 23, Step by step
[^r24]: 04_service_definitions/inventory/bin_save.yaml, procedures
[^r23]: 04_service_definitions/inventory/bin_save.yaml, response.envelope
[^r22]: 04_service_definitions/inventory/bin_save.yaml, request.fields
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 23, Step by step
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 15, bin_get BIN MASTER GET
[^r16]: 04_service_definitions/inventory/bin_get.yaml, whole file
[^r18]: 04_service_definitions/inventory/bin_get.yaml, response
[^r17]: 04_service_definitions/inventory/bin_get.yaml, request
[^r14]: 04_service_definitions/inventory/bin_block.yaml, errors
[^r19]: 04_service_definitions/inventory/bin_get.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 15, bin_search BIN MASTER LIST
[^r25]: 04_service_definitions/inventory/bin_search.yaml, service
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 23, Step by step
[^r28]: 04_service_definitions/inventory/bin_search.yaml, response.envelope
[^r27]: 04_service_definitions/inventory/bin_search.yaml, request.fields
[^r29]: 04_service_definitions/inventory/bin_search.yaml, common_errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 15, bin_block BIN MASTER BLOCK
[^r13]: 04_service_definitions/inventory/bin_block.yaml, procedures
[^r11]: 04_service_definitions/inventory/bin_block.yaml, auth
[^r12]: 04_service_definitions/inventory/bin_block.yaml, request.fields
[^r31]: 03_ledgerline_manuals/old/MAN-INV-72 Inventory v7.2.2 (old).pdf, p. 11, Step by step
