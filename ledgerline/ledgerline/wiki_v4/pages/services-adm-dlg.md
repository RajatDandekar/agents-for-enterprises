---
title: "ADM dlg services"
type: "service-group"
slug: "services-adm-dlg"
summary: "Ledgerline ADM approval delegation services for saving, retrieving, cancelling, and listing user approval delegations."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/admin/dlg_cancel.yaml", "04_service_definitions/admin/dlg_get.yaml", "04_service_definitions/admin/dlg_list.yaml", "04_service_definitions/admin/dlg_save.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | ADM |
| Target Object | Approval delegation |
| Screen | SYS-DLG-03 |
| Available Since | Ledgerline 7.1 |
| Services | dlg_save, dlg_get, dlg_cancel, dlg_list |
| Status | Current |

The ADM dlg service group manages approval delegation records in Ledgerline, enabling users to reassign approval authority across specified date ranges [^r3][^r4][^r8]. It exposes four REST endpoints for creating, retrieving, cancelling, and listing delegations, operating in conjunction with screen [[screen-sys-dlg-03|SYS-DLG-03 Approval Delegation Entry]] [^r3][^r9][^r13][^r17][^r23]. All endpoints enforce role authorization and session token authentication passed through the `X-LL-Session` header [^r9][^r14][^r18][^r23].

## Services

### dlg_save
* **Description**: Write service that creates or updates an approval delegation record; introduced in Ledgerline 7.1 and executed via key `F8` on screen [[screen-sys-dlg-03|SYS-DLG-03]] [^r3][^r4][^r22].
* **Endpoint**: `POST /ll72/svc/dlg_save` [^r23].
* **Stored Procedure**: `sp_dlg_save` [^r4][^r26].
* **Required Fields**: `from_user` (str), `to_user` (str), `from_dt` (date), and `to_dt` (date) [^r4][^r24].
* **Optional Fields**: None [^r4][^r24].
* **Response Envelope**: Standard envelope returning return code `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r25].
* **Errors**: Specific error [[err-dlg-0210|ERR-DLG-0210]] (DELEGATE ROLE LOWER THAN DELEGATOR), and common errors ERR-SEC-0001 (ACCESS DENIED), ERR-SYS-0421 (<FIELD> MANDATORY), ERR-SYS-0422 (UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>), and ERR-SYS-0503 (SERVER BUSY, TRY LATER) [^r1][^r4][^r27].
* **Source Files**: `MAN-SVC-72`, `MAN-SCR-72`, `MAN-ERR-72`, and `04_service_definitions/admin/dlg_save.yaml` [^r1][^r3][^r4][^r22].

### dlg_get
* **Description**: Read service that fetches a single approval delegation record; introduced in Ledgerline 7.1 and mapped to key `F3` on screen [[screen-sys-dlg-03|SYS-DLG-03]] [^r3][^r5][^r13].
* **Endpoint**: `POST /ll72/svc/dlg_get` [^r13].
* **Required Fields**: `dlg_no` (str) [^r5][^r15].
* **Optional Fields**: None [^r5][^r15].
* **Response Envelope**: Standard envelope returning return code `rc` (`S | W | E`), `err_cd`, `msg`, and `data` [^r11][^r20].
* **Errors**: Specific error ERR-DLG-0001 when the delegation key is not found [^r2][^r5][^r16].
* **Source Files**: `MAN-SVC-72`, `MAN-SCR-72`, and `04_service_definitions/admin/dlg_get.yaml` [^r3][^r5][^r13].

### dlg_cancel
* **Description**: Write service that cancels an approval delegation; introduced in Ledgerline 7.1 and mapped to shortcut `Shift+F8` on screen [[screen-sys-dlg-03|SYS-DLG-03]] [^r3][^r6][^r8].
* **Endpoint**: `POST /ll72/svc/dlg_cancel` [^r9].
* **Stored Procedure**: `sp_dlg_cancel` [^r6][^r12].
* **Required Fields**: `dlg_no` (str) and `reason` (str) [^r6][^r10].
* **Optional Fields**: None [^r6][^r10].
* **Response Envelope**: Standard envelope returning `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r11].
* **Errors**: Specific errors ERR-DLG-0001 (delegation not found) and ERR-DLG-0801 (delegation document is already closed, cancelled, or rejected), along with common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r2][^r6][^r12].
* **Source Files**: `MAN-SVC-72`, `MAN-SCR-72`, `MAN-ERR-72`, and `04_service_definitions/admin/dlg_cancel.yaml` [^r2][^r3][^r6][^r8].

### dlg_list
* **Description**: Read service that queries approval delegations, available since Ledgerline 7.1 and accessible from screen [[screen-sys-dlg-03|SYS-DLG-03]] [^r3][^r7][^r17].
* **Endpoint**: `POST /ll72/svc/dlg_list` [^r17].
* **Required Fields**: None [^r7][^r19].
* **Optional Fields**: `from_user` (str) to filter delegations by the delegating user [^r7][^r19].
* **Response Envelope**: Standard envelope returning `rc` (`S | W | E`), `err_cd` (error code when `rc` is `E`), `msg` (short message in capitals), and `data` (result) [^r20].
* **Errors**: Common errors ERR-SEC-0001, ERR-SYS-0421, ERR-SYS-0422, and ERR-SYS-0503 [^r21].
* **Source Files**: `MAN-SVC-72`, `MAN-SCR-72`, and `04_service_definitions/admin/dlg_list.yaml` [^r3][^r7][^r17].

## See also
* [[screen-sys-dlg-03|SYS-DLG-03 Approval Delegation Entry]]
* [[err-dlg-0210|ERR-DLG-0210 Delegate role lower than delegator]]
* [[services-adm-usr|ADM usr services]]
* [[services-adm-par|ADM par services]]
* [[services-adm-imp|ADM imp services]]

## References

[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-DLG-03 APPROVAL DELEGATION ENTRY
[^r4]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 67, dlg_save APPROVAL DELEGATION SAVE
[^r8]: 04_service_definitions/admin/dlg_cancel.yaml, service
[^r9]: 04_service_definitions/admin/dlg_cancel.yaml, endpoint
[^r13]: 04_service_definitions/admin/dlg_get.yaml, service: dlg_get
[^r17]: 04_service_definitions/admin/dlg_list.yaml, service: dlg_list
[^r23]: 04_service_definitions/admin/dlg_save.yaml, endpoint
[^r14]: 04_service_definitions/admin/dlg_get.yaml, auth
[^r18]: 04_service_definitions/admin/dlg_list.yaml, auth
[^r22]: 04_service_definitions/admin/dlg_save.yaml, service: dlg_save
[^r26]: 04_service_definitions/admin/dlg_save.yaml, procedures
[^r24]: 04_service_definitions/admin/dlg_save.yaml, request.fields
[^r25]: 04_service_definitions/admin/dlg_save.yaml, response.envelope
[^r1]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 7, ERR-DLG-0210
[^r27]: 04_service_definitions/admin/dlg_save.yaml, errors
[^r5]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 67, dlg_get APPROVAL DELEGATION GET
[^r15]: 04_service_definitions/admin/dlg_get.yaml, request
[^r11]: 04_service_definitions/admin/dlg_cancel.yaml, response.envelope
[^r20]: 04_service_definitions/admin/dlg_list.yaml, response
[^r2]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 7, ERR-DLG-0801
[^r16]: 04_service_definitions/admin/dlg_get.yaml, errors
[^r6]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 67, dlg_cancel APPROVAL DELEGATION CANCEL
[^r12]: 04_service_definitions/admin/dlg_cancel.yaml, errors
[^r10]: 04_service_definitions/admin/dlg_cancel.yaml, request.fields
[^r7]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 67, dlg_list APPROVAL DELEGATION LIST
[^r19]: 04_service_definitions/admin/dlg_list.yaml, request
[^r21]: 04_service_definitions/admin/dlg_list.yaml, common_errors
