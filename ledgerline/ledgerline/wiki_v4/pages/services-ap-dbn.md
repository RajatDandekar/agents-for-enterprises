---
title: "AP dbn services"
type: "service-group"
slug: "services-ap-dbn"
summary: "Ledgerline AP debit note services handling creation, retrieval, searching, posting, and cancellation on screen AP-DBN-04."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/dbn_cancel.yaml", "04_service_definitions/accounts_payable/dbn_get.yaml", "04_service_definitions/accounts_payable/dbn_post.yaml", "04_service_definitions/accounts_payable/dbn_save.yaml", "04_service_definitions/accounts_payable/dbn_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Group | services-ap-dbn |
| Module | Accounts Payable (AP) |
| Primary screen | [[screen-ap-dbn-04|AP-DBN-04]] |
| Available since | Ledgerline 7.0 |
| Protocol | POST /ll72/svc/* |
| Status | Current |

The `dbn` service group provides read and write operations for managing supplier debit notes in Ledgerline Accounts Payable [^r6]. Operating primarily through screen [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]], these services allow users to search, retrieve, draft, post, and cancel debit notes [^r1][^r2][^r3][^r4][^r5][^r6]. All services authenticate requests via a session token in the `X-LL-Session` header and require an authorised user role [^r13][^r17][^r22][^r28][^r32].

## Services

### dbn_save
The `dbn_save` write service creates an unposted draft debit note in ledger tables, validates header fields, and assigns a sequential document number in `DBN NO` [^r3][^r7][^r27]. It has been active since Ledgerline version 7.0 and operates via endpoint `POST /ll72/svc/dbn_save` on screen [[screen-ap-dbn-04|AP-DBN-04]] by calling database procedure `sp_dbn_save` [^r7][^r27][^r28][^r30].

* **Required fields:** `sup_cd` (string, supplier code), `ref_doc` (string, reference document), `amount` (float), `reason_cd` (string, reason code) [^r7][^r29].
* **Optional fields:** none [^r7][^r29].
* **Errors:** [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND) [^r7][^r30].
* **Source files:** `MAN-SVC-72`, `MAN-AP-72`, `MAN-SCR-72`, `04_service_definitions/accounts_payable/dbn_save.yaml` [^r3][^r6][^r7][^r27][^r28][^r29][^r30].

### dbn_get
The `dbn_get` read service executes the `DEBIT NOTE GET` routine to fetch a single debit note record on screen [[screen-ap-dbn-04|AP-DBN-04]] when a unique document identifier is entered in `DBN NO` [^r2][^r8][^r16]. Available since version 7.0, it is accessed at `POST /ll72/svc/dbn_get` and returns a standard envelope containing return code `rc` (`S`, `W`, or `E`), error code `err_cd`, uppercase message `msg`, and result data [^r16][^r17][^r19].

* **Required fields:** `dbn_no` (string, debit note number) [^r8][^r18].
* **Optional fields:** none [^r8][^r18].
* **Errors:** [[err-dbn-0001|ERR-DBN-0001]] (DEBIT NOTE NOT FOUND), as well as common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r8][^r20].
* **Source files:** `MAN-SVC-72`, `MAN-AP-72`, `MAN-SCR-72`, `04_service_definitions/accounts_payable/dbn_get.yaml` [^r2][^r6][^r8][^r16][^r17][^r18][^r19][^r20].

### dbn_search
The `dbn_search` read service executes `DEBIT NOTE LIST` on screen [[screen-ap-dbn-04|AP-DBN-04]] to present a selection grid of existing debit notes [^r1][^r6][^r9][^r31]. Available since version 7.0 at endpoint `POST /ll72/svc/dbn_search`, it returns a standard envelope with return code `rc`, `err_cd`, `msg`, and data [^r31][^r34].

* **Required fields:** none [^r9][^r33].
* **Optional fields:** `sup_cd` (string), `ref_doc` (string), `amount` (float), `status` (string) [^r9][^r33].
* **Errors:** common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r34].
* **Source files:** `MAN-SVC-72`, `MAN-AP-72`, `MAN-SCR-72`, `04_service_definitions/accounts_payable/dbn_search.yaml` [^r1][^r6][^r9][^r31][^r32][^r33][^r34].

### dbn_post
The `dbn_post` write service validates the supplier account and amount, applies the debit balance to the supplier ledger, locks the record, and transitions document status to posted [^r4][^r10][^r21]. Associated with screen [[screen-ap-dbn-04|AP-DBN-04]] and active since version 7.0, it is exposed via endpoint `POST /ll72/svc/dbn_post` and runs stored procedure `sp_dbn_post` [^r10][^r21][^r22][^r24].

* **Required fields:** `dbn_no` (string) [^r10][^r23].
* **Optional fields:** `comment` (string) [^r10][^r23].
* **Errors:** [[err-dbn-0001|ERR-DBN-0001]] (DEBIT NOTE NOT FOUND), [[err-dbn-0007|ERR-DBN-0007]] (DEBIT NOTE NOT IN DRAFT), and common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r10][^r25][^r26].
* **Source files:** `MAN-SVC-72`, `MAN-AP-72`, `MAN-SCR-72`, `04_service_definitions/accounts_payable/dbn_post.yaml` [^r4][^r6][^r10][^r21][^r22][^r23][^r24][^r25][^r26].

### dbn_cancel
The `dbn_cancel` write service voids an unposted debit note, clears pending commitments against the underlying reference document, and sets document status to cancelled [^r5][^r11][^r12]. Associated with screen [[screen-ap-dbn-04|AP-DBN-04]] since version 7.0, it invokes backend procedure `sp_dbn_cancel` via endpoint `POST /ll72/svc/dbn_cancel` [^r6][^r11][^r12][^r15].

* **Required fields:** `dbn_no` (string), `reason` (string) [^r11][^r14].
* **Optional fields:** none [^r11][^r14].
* **Errors:** [[err-dbn-0001|ERR-DBN-0001]] and [[err-dbn-0801|ERR-DBN-0801]] (raised if the debit note is already closed) [^r6][^r11][^r15].
* **Source files:** `MAN-SVC-72`, `MAN-AP-72`, `MAN-SCR-72`, `04_service_definitions/accounts_payable/dbn_cancel.yaml` [^r5][^r6][^r11][^r12][^r13][^r14][^r15].

## See also
* [[screen-ap-dbn-04|AP-DBN-04 Debit Note Entry]]
* [[screen-ap-crn-05|AP-CRN-05 Supplier Credit Note Entry]]
* [[services-ap-crn|AP crn services]]
* [[services-ap-inv|AP inv services]]
* [[err-dbn-0001|ERR-DBN-0001]]
* [[err-dbn-0007|ERR-DBN-0007]]
* [[err-dbn-0801|ERR-DBN-0801]]
* [[err-sup-0030|ERR-SUP-0030]]

## References

[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 6, AP-DBN-04 DEBIT NOTE ENTRY
[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 11, Step by step
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 11, Step by step
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To create and save a new draft debit note:
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To post the debit note:
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 12, To cancel an unposted debit note:
[^r13]: 04_service_definitions/accounts_payable/dbn_cancel.yaml, whole file
[^r17]: 04_service_definitions/accounts_payable/dbn_get.yaml, auth
[^r22]: 04_service_definitions/accounts_payable/dbn_post.yaml, header
[^r28]: 04_service_definitions/accounts_payable/dbn_save.yaml, endpoint
[^r32]: 04_service_definitions/accounts_payable/dbn_search.yaml, auth
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 27, dbn_save DEBIT NOTE SAVE
[^r27]: 04_service_definitions/accounts_payable/dbn_save.yaml, service: dbn_save
[^r30]: 04_service_definitions/accounts_payable/dbn_save.yaml, procedures
[^r29]: 04_service_definitions/accounts_payable/dbn_save.yaml, request.fields
[^r8]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 27, dbn_get DEBIT NOTE GET
[^r16]: 04_service_definitions/accounts_payable/dbn_get.yaml, service: dbn_get
[^r19]: 04_service_definitions/accounts_payable/dbn_get.yaml, response
[^r18]: 04_service_definitions/accounts_payable/dbn_get.yaml, request
[^r20]: 04_service_definitions/accounts_payable/dbn_get.yaml, errors
[^r9]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 27, dbn_search DEBIT NOTE LIST
[^r31]: 04_service_definitions/accounts_payable/dbn_search.yaml, whole file
[^r34]: 04_service_definitions/accounts_payable/dbn_search.yaml, response.envelope
[^r33]: 04_service_definitions/accounts_payable/dbn_search.yaml, request.fields
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 28, dbn_post DEBIT NOTE POST
[^r21]: 04_service_definitions/accounts_payable/dbn_post.yaml, header
[^r24]: 04_service_definitions/accounts_payable/dbn_post.yaml, procedures
[^r23]: 04_service_definitions/accounts_payable/dbn_post.yaml, request
[^r25]: 04_service_definitions/accounts_payable/dbn_post.yaml, errors
[^r26]: 04_service_definitions/accounts_payable/dbn_post.yaml, common_errors
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 28, dbn_cancel DEBIT NOTE CANCEL
[^r12]: 04_service_definitions/accounts_payable/dbn_cancel.yaml, whole file
[^r15]: 04_service_definitions/accounts_payable/dbn_cancel.yaml, errors
[^r14]: 04_service_definitions/accounts_payable/dbn_cancel.yaml, request.fields
