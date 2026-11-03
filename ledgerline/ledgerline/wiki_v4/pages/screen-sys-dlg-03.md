---
title: "SYS-DLG-03 Approval Delegation Entry"
type: "screen"
slug: "screen-sys-dlg-03"
summary: "System administration screen to delegate an absent officer's approval inbox to a substitute holding an equal or higher role."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/dlg_cancel.yaml", "04_service_definitions/admin/dlg_get.yaml", "04_service_definitions/admin/dlg_list.yaml", "04_service_definitions/admin/dlg_save.yaml", "08_release_notes/RN-7.1 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SYS-DLG-03 |
| Title | Approval Delegation Entry |
| Module | System Administration |
| Navigation | System > Approval delegation |
| Roles | IT-ADMIN, SYS-ADMIN |
| Read services | dlg_get, dlg_list |
| Write services | dlg_save, dlg_cancel |

Screen SYS-DLG-03 reassigns an absent officer's approval inbox to another user for a specified date window [^r1]. System administrators use it to ensure purchase orders, stock adjustments, and works order releases route to qualified colleagues without workflow interruption [^r4][^r15]. Ledgerline validates role rank upon saving and strictly prohibits delegating authority to any user who holds a lower operational grade or role rank [^r1][^r13][^r14]. Approved actions completed during the delegation window maintain an audit flag recording both the delegator and delegate identities [^r3].

| Field | Type | Attributes | Description |
|---|---|---|---|
| dlg_no | String | Mandatory | Unique approval delegation record reference [^r5][^r8][^r9]. |
| from_user | String | Mandatory | Authoriser whose inbox is being reassigned [^r5][^r12]. Can also filter search listings [^r10]. |
| to_user | String | Mandatory | Nominated substitute holding equivalent or superior standing [^r5][^r12][^r15]. |
| from_dt | Date | Mandatory | Start date of the delegation period [^r5][^r12]. |
| to_dt | Date | Mandatory | End date of the delegation period [^r5][^r12]. |
| reason | String | Mandatory | Operational reason for the delegation or cancellation [^r5][^r8]. |

Historical transactions existing in the delegator's inbox prior to the effective start date are not reassigned by SYS-DLG-03 [^r2].

## Keys and services

SYS-DLG-03 interacts with backend routines documented in [[services-adm-dlg|ADM dlg services]] [^r6][^r8][^r9][^r10][^r11]:

* **F3 (Get):** Executes read service `dlg_get` to retrieve a delegation by `dlg_no` [^r6][^r9].
* **F8 (Save):** Executes write service `dlg_save` to validate roles and record active delegations using `from_user`, `to_user`, `from_dt`, and `to_dt` [^r6][^r11][^r12][^r13].
* **Shift+F8 (Cancel):** Executes write service `dlg_cancel` to terminate an active delegation record using `dlg_no` and `reason` [^r6][^r8].
* **List:** Invokes read service `dlg_list` (`POST /ll72/svc/dlg_list`) to search delegations, accepting an optional `from_user` filter [^r6][^r10].

## Messages

* `ERR-DLG-001`: Approval Delegation Not Found; raised when a specified delegation identifier cannot be retrieved [^r7].
* `ERR-DLG-0210`: Delegate Role Lower Than Delegator; halts entry when saving if the nominated substitute holds a lower role rank or permissions profile than the delegator [^r1][^r7][^r14].
* `ERR-DLG-0801`: Approval Delegation Closed; returned when attempting operations on an already terminated or expired delegation [^r7].

## See also

* [[err-dlg-0210|ERR-DLG-0210 Delegate role lower than delegator]]
* [[services-adm-dlg|ADM dlg services]]
* [[man-adm-72|MAN-ADM-72 Ledgerline ERP 7.2 System Administration]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 4, §3. Approval delegation
[^r4]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-DLG-03 APPROVAL DELEGATION ENTRY
[^r15]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 2, Administration: Approval delegation (SYS-DLG-03)
[^r13]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 2, Administration: Approval delegation (SYS-DLG-03)
[^r14]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 2, Administration: Approval delegation (SYS-DLG-03)
[^r3]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 5, §3. Approval delegation
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-DLG-03 APPROVAL DELEGATION ENTRY
[^r8]: 04_service_definitions/admin/dlg_cancel.yaml, screen
[^r9]: 04_service_definitions/admin/dlg_get.yaml, screen: SYS-DLG-03
[^r12]: 04_service_definitions/admin/dlg_save.yaml, request.fields
[^r10]: 04_service_definitions/admin/dlg_list.yaml, service: dlg_list
[^r2]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 4, §3. Approval delegation
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-DLG-03 APPROVAL DELEGATION ENTRY
[^r11]: 04_service_definitions/admin/dlg_save.yaml, screen
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 41, SYS-DLG-03 APPROVAL DELEGATION ENTRY
