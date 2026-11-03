---
title: "ADM seq services"
type: "service-group"
slug: "services-adm-seq"
summary: "Ledgerline ADM services for reading, listing, and setting document sequence counters on screen SYS-SEQ-05."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/seq_get.yaml", "04_service_definitions/admin/seq_list.yaml", "04_service_definitions/admin/seq_set.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Object | Document Sequence |
| Introduced | Ledgerline 7.0 |
| Screen | SYS-SEQ-05 |
| Services | seq_get, seq_list, seq_set |
| Status | current |

The ADM seq services manage document sequence counters across Ledgerline modules, backing screen [[screen-sys-seq-05|SYS-SEQ-05 Document Sequence]][^r1][^r5]. Introduced in Ledgerline 7.0, these services allow staff to look up existing counters, query lists of sequences, and configure next sequence numbers and prefixes[^r3][^r5][^r10][^r15]. If an unconfigured sequence is queried or targeted for updates, the service layer returns error `ERR-SEQ-0001`[^r1][^r9][^r19].

| Field | Value |
|---|---|
| Module | ADM |
| Object | Document Sequence |
| Screen | [[screen-sys-seq-05|SYS-SEQ-05]] |
| Introduced | Ledgerline 7.0 |
| Services | seq_get, seq_list, seq_set |

## Services

### seq_get

The `seq_get` service (DOCUMENT SEQUENCE GET) is a read operation in the ADM module introduced in Ledgerline 7.0 that retrieves counter configurations for screen [[screen-sys-seq-05|SYS-SEQ-05]][^r1][^r2][^r5]. It is triggered by function key F3 on screen SYS-SEQ-05 and accessed via endpoint `POST /ll72/svc/seq_get`[^r1][^r6]. Requests require an active session token in HTTP header `X-LL-Session` and a user role permitted to execute the service[^r6].

* **Required fields:** `doc_type` (str, DOC TYPE)[^r2][^r7].
* **Optional fields:** none[^r7].
* **Errors:** Specific error `ERR-SEQ-0001` (DOCUMENT SEQUENCE NOT FOUND), alongside common system errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (\<FIELD\> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD \<FIELD\> / BAD VALUE FOR \<FIELD\>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER)[^r2][^r9]. Responses follow the standard envelope returning `rc` ('S | W | E'), `err_cd`, short message `msg` in capitals, and `data`[^r8].
* **Source file:** `04_service_definitions/admin/seq_get.yaml`[^r5].

### seq_list

The `seq_list` service (DOCUMENT SEQUENCE LIST) is an ADM read operation introduced in Ledgerline 7.0 that populates query overviews on screen [[screen-sys-seq-05|SYS-SEQ-05]][^r4][^r10]. It is exposed through endpoint `POST /ll72/svc/seq_list` and authenticates via header `X-LL-Session` against permissions assigned to the user's role[^r11].

* **Required fields:** none[^r12].
* **Optional fields:** `doc_type` (str, DOC TYPE)[^r4][^r12].
* **Errors:** Common errors `ERR-SEC-0001` (ACCESS DENIED), `ERR-SYS-0421` (\<FIELD\> MANDATORY), `ERR-SYS-0422` (UNKNOWN FIELD \<FIELD\> / BAD VALUE FOR \<FIELD\>), and `ERR-SYS-0503` (SERVER BUSY, TRY LATER)[^r14]. Responses return the standard envelope with `rc`, `err_cd`, uppercase `msg`, and `data`[^r13].
* **Source file:** `04_service_definitions/admin/seq_list.yaml`[^r10].

### seq_set

The `seq_set` service (DOCUMENT SEQUENCE SET) is an ADM write operation introduced in Ledgerline 7.0 that updates sequence counter parameters by executing stored procedure `sp_seq_set`[^r3][^r15][^r20]. It is published at endpoint `POST /ll72/svc/seq_set` and requires an `X-LL-Session` token authorised for the role[^r16].

* **Required fields:** `doc_type` (str)[^r3][^r17].
* **Optional fields:** `prefix` (str), `next_no` (int)[^r3][^r17].
* **Errors:** Specific error `ERR-SEQ-0001` (DOCUMENT SEQUENCE NOT FOUND) when the sequence record is absent, in addition to common errors `ERR-SEC-0001`, `ERR-SYS-0421`, `ERR-SYS-0422`, and `ERR-SYS-0503`[^r3][^r19]. The response envelope returns `rc`, `err_cd`, uppercase `msg`, and payload `data`[^r18].
* **Source file:** `04_service_definitions/admin/seq_set.yaml`[^r15].

## See also

* [[screen-sys-seq-05|SYS-SEQ-05 Document Sequence]]
* [[services-adm-par|ADM par services]]
* [[services-adm-dlg|ADM dlg services]]
* [[services-adm-imp|ADM imp services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-SEQ-05 DOCUMENT SEQUENCE
[^r5]: 04_service_definitions/admin/seq_get.yaml, service: seq_get
[^r3]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 68, seq_set DOCUMENT SEQUENCE SET
[^r10]: 04_service_definitions/admin/seq_list.yaml, service: seq_list
[^r15]: 04_service_definitions/admin/seq_set.yaml, service: seq_set
[^r9]: 04_service_definitions/admin/seq_get.yaml, errors
[^r19]: 04_service_definitions/admin/seq_set.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 68, seq_get DOCUMENT SEQUENCE GET
[^r6]: 04_service_definitions/admin/seq_get.yaml, auth
[^r7]: 04_service_definitions/admin/seq_get.yaml, request
[^r8]: 04_service_definitions/admin/seq_get.yaml, response
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 68, seq_list DOCUMENT SEQUENCE LIST
[^r11]: 04_service_definitions/admin/seq_list.yaml, endpoint
[^r12]: 04_service_definitions/admin/seq_list.yaml, request
[^r14]: 04_service_definitions/admin/seq_list.yaml, common_errors
[^r13]: 04_service_definitions/admin/seq_list.yaml, response
[^r20]: 04_service_definitions/admin/seq_set.yaml, procedures
[^r16]: 04_service_definitions/admin/seq_set.yaml, endpoint
[^r17]: 04_service_definitions/admin/seq_set.yaml, request.fields
[^r18]: 04_service_definitions/admin/seq_set.yaml, response.envelope
