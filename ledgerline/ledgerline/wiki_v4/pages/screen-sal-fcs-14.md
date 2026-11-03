---
title: "SAL-FCS-14 Sales Forecast Entry"
type: "screen"
slug: "screen-sal-fcs-14"
summary: "Ledgerline screen for entering, adjusting, and uploading sales forecast quantities by item and period."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/fcs_get.yaml", "04_service_definitions/sales/fcs_save.yaml", "04_service_definitions/sales/fcs_upload.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SAL-FCS-14 |
| Name | Sales Forecast Entry |
| Module | Sales |
| Path | Sales > Sales forecast |
| Authorized roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Read service | fcs_get |
| Write services | fcs_save, fcs_upload |

SAL-FCS-14 (Sales Forecast Entry) is the Ledgerline ERP screen used by sales personnel to review, record, and maintain item sales forecast quantities across planning periods [^r1][^r8][^r12]. Accessible under Sales > Sales forecast to users with roles SAL-EXEC, SAL-MGR, and SYS-ADMIN, it supports single-record maintenance and batch imports via backend services [^r8][^r12][^r13]. Forecasting cannot be performed against obsolete or inactive items, or into closed financial or manufacturing periods [^r4].

## Fields

| Field | Label | Mandatory | Description |
|---|---|---|---|
| `itm_cd` | ITEM CD | Yes | The item identifier; must be an active, valid item code [^r1][^r4][^r7][^r8]. |
| `period` | PERIOD | Yes | The target planning period; must represent an open financial and manufacturing interval [^r1][^r4][^r8]. |
| `qty` | QTY | Yes | The forecasted unit quantity [^r1][^r8]. |
| `fcs_id` | FCS ID | Yes | Unique forecast record identifier; left blank during single-line creation to prompt automatic reference generation, or specified when retrieving an existing forecast [^r1][^r2][^r6][^r8]. |

To retrieve an existing forecast line, enter the `fcs_id`, or specify `itm_cd` and `period` with `fcs_id` blank, and invoke Get [^r3]. To adjust an existing forecast, retrieve the line, enter the revised count into `qty`, and invoke Save [^r5].

## Keys and services

Screen actions on SAL-FCS-14 bind directly to the [[services-sal-fcs|SAL fcs services]] group:

* **Get (F3)**: Calls read service `fcs_get` (SALES FORECAST GET) via endpoint `POST /ll72/svc/fcs_get` using `fcs_id` to retrieve forecast records [^r3][^r9][^r10].
* **Save (F8)**: Calls write service `fcs_save` (SALES FORECAST SAVE) to create or update item forecast quantities by period; when saving a new entry with `fcs_id` blank, the system generates and returns a new identifier [^r5][^r6][^r9][^r12].
* **Upload**: Binds to write service `fcs_upload` via endpoint `POST /ll72/svc/fcs_upload` to load forecast entries [^r9][^r13].

## Messages

The screen references several message codes catalogued under [[errors-fcs]]:

* `ERR-FCS-0001`: Save failure resulting from a closed period or locked duplicate, or forecast record not found during retrieval [^r7][^r9][^r11].
* `ERR-FCS-0201`: Record not found for the specified `fcs_id` or `itm_cd` and `period` combination [^r7][^r9].
* [[err-itm-0011|ERR-ITM-0011]]: Invalid, deleted, or inactive item code [^r7][^r9].

## Versions and conflicts

- contradiction | According to MAN-SAL-72, ERR-FCS-0201 indicates a forecast record was not found on retrieval and ERR-FCS-0001 denotes a save failure caused by a closed period or locked duplicate | The service definition for `fcs_get.yaml` designates ERR-FCS-0001 as SALES FORECAST NOT FOUND | [^r7][^r11]

## See also

* [[services-sal-fcs|SAL fcs services]]
* [[errors-fcs|ERR-FCS Error Codes]]
* [[err-itm-0011|ERR-ITM-0011]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 55, §17. Sales Forecast (SAL-FCS-14)
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 36, SAL-FCS-14 SALES FORECAST ENTRY
[^r12]: 04_service_definitions/sales/fcs_save.yaml, service: fcs_save
[^r13]: 04_service_definitions/sales/fcs_upload.yaml, screen
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 56, Before you start
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 57, Messages
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 56, Layout and fields
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 57, Entering a single new forecast line
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 56, Retrieving an existing entry
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 57, [p. 57]
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 36, SAL-FCS-14 SALES FORECAST ENTRY
[^r10]: 04_service_definitions/sales/fcs_get.yaml, whole file
[^r11]: 04_service_definitions/sales/fcs_get.yaml, errors
