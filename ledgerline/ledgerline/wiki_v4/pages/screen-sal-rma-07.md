---
title: "SAL-RMA-07 Warranty Return (Rma) Entry"
type: "screen"
slug: "screen-sal-rma-07"
summary: "Ledgerline screen for logging, approving, receiving, and closing customer warranty return authorisations (RMAs)."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/rma_approve.yaml", "04_service_definitions/sales/rma_close.yaml", "04_service_definitions/sales/rma_get.yaml", "04_service_definitions/sales/rma_receive.yaml", "04_service_definitions/sales/rma_save.yaml", "04_service_definitions/sales/rma_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SAL-RMA-07 |
| Name | WARRANTY RETURN (RMA) ENTRY |
| Module | Sales > Warranty return |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Read services | rma_get, rma_search |
| Write services | rma_save, rma_approve, rma_receive, rma_close |

Screen SAL-RMA-07 manages the full lifecycle of customer return authorisations in Ledgerline under Sales > Warranty return [^r10]. It allows authorised users to log claim details, sanction returns, record physical goods intake at the quarantine store, and close finalised files [^r7][^r8][^r9][^r10]. Staff lacking approval permissions may draft and view returns, but cannot sanction claims, receive returned goods, or close records [^r3].

| Field | Value |
|---|---|
| Screen code | SAL-RMA-07 [^r10] |
| Name | WARRANTY RETURN (RMA) ENTRY [^r10] |
| Navigation path | Sales > Warranty return [^r10] |
| Permitted roles | SAL-EXEC, SAL-MGR, SYS-ADMIN [^r10] |
| Read services | rma_get, rma_search [^r11] |
| Write services | rma_save, rma_approve, rma_receive, rma_close [^r11] |

## Fields

Screen SAL-RMA-07 includes the following data fields [^r1][^r10]:

* `cust_cd` (CUST CD): Mandatory customer identifier [^r1][^r10].
* `itm_cd` (ITEM CD): Mandatory item code [^r1][^r10].
* `serial_no` (SERIAL NO): Mandatory serial registration number [^r1][^r10].
* `fault_cd` (FAULT CD): Mandatory fault classification code [^r1][^r10].
* `rma_no` (RMA NO): Mandatory return authorisation identifier, left blank during initial creation for Ledgerline to assign upon saving [^r1][^r2][^r10].
* `remarks` (REMARKS): Optional descriptive notes [^r1][^r10].
* `status` (STATUS): Optional status indicator reflecting the lifecycle stage [^r1][^r10].
* `comment` (COMMENT): Optional field used for entering condition notes upon receipt of goods at the plant [^r1][^r4][^r10].

## Keys and services

SAL-RMA-07 maps user keystrokes and buttons to read and write backend services documented under [[services-sal-rma]] [^r11]:

* **Save (F8)**: Invokes `rma_save` (`POST /ll72/svc/rma_save`) [^r11][^r16]. Validates mandatory inputs, allocates a new `rma_no`, and sets `status` to initial state [^r2][^r6]. Required parameters are `cust_cd`, `itm_cd`, `serial_no`, and `fault_cd`, with optional `remarks` [^r16].
* **Get (F3)**: Invokes `rma_get` (`POST /ll72/svc/rma_get`) using mandatory parameter `rma_no` to retrieve a specific return record [^r11][^r14].
* **Search (F2/Enter)**: Invokes `rma_search` (`POST /ll72/svc/rma_search`) using optional filters `cust_cd`, `itm_cd`, `serial_no`, and `status` to list matching authorisations [^r11][^r17].
* **Approve (F9)**: Invokes write service `rma_approve` (`POST /ll72/svc/rma_approve`) to sanction the warranty return prior to goods receipt [^r7][^r11][^r12].
* **Receive**: Invokes write service `rma_receive` (`POST /ll72/svc/rma_receive`) upon intake into quarantine inspection, recording condition notes from `comment` and updating `status` [^r4][^r8][^r11][^r15].
* **Close**: Invokes write service `rma_close` (`POST /ll72/svc/rma_close`) via stored procedure `sp_rma_close` to set `status` to final closed state, preventing further updates [^r5][^r11][^r13].

## Messages

The screen raises the following validation and workflow error messages, catalogue entries for which appear in [[errors-rma]] [^r11]:

* [[err-itm-0011]]: Raised when the entered item code is not found or inactive [^r11].
* `ERR-RMA-0001`: Raised by `rma_save` if mandatory fields are omitted [^r6][^r11].
* `ERR-RMA-0007`: Raised by `rma_save` if the customer reference is invalid [^r6][^r11].
* [[err-apr-0003]]: Raised by `rma_approve` if user authorising permissions are missing [^r7][^r11].
* [[err-apr-0004]]: Raised by `rma_approve` if the current record state is not approvable [^r7][^r11].
* [[err-rma-0210]]: Raised by `rma_receive` if physical intake is attempted before formal approval [^r8][^r11].
* `ERR-RMA-0211`: Raised by `rma_close` if closing is attempted before goods have been received [^r9][^r11].
* `ERR-RMA-0801`: Raised by `rma_close` if the transaction record is locked [^r9][^r11].

## See also

* [[services-sal-rma|SAL rma services]]
* [[errors-rma|ERR-RMA Error Codes]]
* [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[screen-sal-crn-09|SAL-CRN-09 Customer Credit Note Entry]]
* [[screen-inv-rtv-07|INV-RTV-07 Return To Vendor Entry]]
* [[screen-qa-ncr-02|QA-NCR-02 Non-Conformance Report Entry]]

## References

[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 38, SAL-RMA-07 WARRANTY RETURN (RMA) ENTRY
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 32, Worked example
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 33, Worked example
[^r9]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 33, Worked example
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 30, Before you start
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 38, SAL-RMA-07 WARRANTY RETURN (RMA) ENTRY
[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 29, §10. Warranty Return (Rma) (SAL-RMA-07)
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 30, Step by step
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 31, Acknowledging goods receipt at the plant
[^r16]: 04_service_definitions/sales/rma_save.yaml, service: rma_save
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 32, Worked example
[^r14]: 04_service_definitions/sales/rma_get.yaml, whole file
[^r17]: 04_service_definitions/sales/rma_search.yaml, whole file
[^r12]: 04_service_definitions/sales/rma_approve.yaml, screen
[^r15]: 04_service_definitions/sales/rma_receive.yaml, whole file
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 31, Concluding and closing the claim
[^r13]: 04_service_definitions/sales/rma_close.yaml, service: rma_close
