---
title: "SAL-ALC-03 Allocation"
type: "screen"
slug: "screen-sal-alc-03"
summary: "Ledgerline screen SAL-ALC-03 for managing sales order stock allocation, reservation, and cancellation across warehouse pickable bins."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/alc_cancel.yaml", "04_service_definitions/sales/alc_get.yaml", "04_service_definitions/sales/alc_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen | SAL-ALC-03 |
| Title | Allocation |
| Menu | Sales > Allocation |
| Module | Sales |
| Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Read service | alc_get |
| Write services | alc_run, alc_cancel |
| Status | Current |

Screen SAL-ALC-03 is the Ledgerline interface used to retrieve order details, execute automated allocation routines, and cancel existing stock reservations for sales orders [^r1][^r2][^r3][^r4]. Located under the navigation path Sales > Allocation, it is accessible to users assigned the roles SAL-EXEC, SAL-MGR, and SYS-ADMIN [^r1][^r8]. It coordinates warehouse availability against confirmed sales demand before pick lists can be generated [^r2][^r3].

| Field | Value |
|---|---|
| Screen code | SAL-ALC-03 [^r1] |
| Screen title | Allocation [^r1][^r8] |
| Menu location | Sales > Allocation [^r1][^r8] |
| Accessible roles | SAL-EXEC, SAL-MGR, SYS-ADMIN [^r8] |
| Key services | alc_get, alc_run, alc_cancel [^r9][^r10][^r11][^r12] |

## Fields

Screen SAL-ALC-03 provides three primary transaction fields [^r1]:

* **SO NO** (`so_no`): Mandatory entry field for the sales order number [^r1][^r12]. Entering this number allows the operator to fetch the order header, delivery address, ordered quantities, allocated quantities, and available warehouse stock [^r2][^r10].
* **REASON** (`reason`): Mandatory text field required when cancelling an allocation run [^r1][^r4][^r6][^r9][^r12]. An explanation must be supplied before reserved goods are released [^r4][^r6].
* **COMMENT** (`comment`): Optional text field for operator notes [^r1].

## Keys and services

Screen SAL-ALC-03 links keyboard shortcuts and buttons to back-end services in the [[services-sal-alc]] group [^r9][^r10][^r11][^r12]:

* **alc_get** (`F3`): Read service that fetches order header details, delivery address, line requirements, current allocations, and free stock for the specified `so_no` [^r2][^r10][^r12].
* **alc_run** (`Run`): Write service invoked via endpoint `POST /ll72/svc/alc_run` using `so_no` to run the ALLOCATION RUN routine, allocating free stock from pickable bins and updating line status to fully or partially allocated [^r3][^r11][^r12].
* **alc_cancel** (`Shift+F8`): Write service that executes stored procedure `sp_alc_cancel` using parameters `so_no` and `reason` to invoke ALLOCATION CANCEL, clearing reservations and returning quantities to the unallocated inventory pool [^r4][^r6][^r9][^r12].

## Messages

The screen raises error codes in the message bar during processing exceptions:

* `ERR-ALC-0001`: Displayed when physical stock is insufficient to satisfy the full requirement during an allocation routine [^r5].
* `ERR-ALC-0801`: Displayed when the entered sales order is locked by another terminal or when the order header has not been formally released by the sales office [^r7].

## See also

* [[services-sal-alc|SAL alc services]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-pck-04|SAL-PCK-04 Pick List Entry]]
* [[screen-sal-dlv-05|SAL-DLV-05 Despatch Entry]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 15, §6. Allocation (SAL-ALC-03)
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 15, Step by Step
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 16, Step by Step
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 16, Step by Step
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, SAL-ALC-03 ALLOCATION
[^r9]: 04_service_definitions/sales/alc_cancel.yaml, service: alc_cancel
[^r10]: 04_service_definitions/sales/alc_get.yaml, whole file
[^r11]: 04_service_definitions/sales/alc_run.yaml, alc_run
[^r12]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 32, SAL-ALC-03 ALLOCATION
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 18, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 17, Worked example
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 18, Questions users ask
