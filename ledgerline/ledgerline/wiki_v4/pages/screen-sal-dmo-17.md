---
title: "SAL-DMO-17 Demo Bike Entry"
type: "screen"
slug: "screen-sal-dmo-17"
summary: "Demo bike management screen used to register, search, track, and close finished goods demonstration bicycle loans to customer accounts without billing."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/sales/dmo_close.yaml", "04_service_definitions/sales/dmo_get.yaml", "04_service_definitions/sales/dmo_save.yaml", "04_service_definitions/sales/dmo_search.yaml", "08_release_notes/RN-7.1.1 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | SAL-DMO-17 |
| menu | Sales > Demo bike |
| roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| services | dmo_save, dmo_get, dmo_search, dmo_close |

Screen SAL-DMO-17 (Demo Bike Entry) manages the registration, search, and return closure of demonstration bicycles on loan to customer accounts [^r1][^r2]. The screen suppresses normal sales invoicing upon dispatch while recording finished goods stock movements and tracking expected return dates [^r19][^r20]. Access is granted to roles SAL-EXEC, SAL-MGR, and SYS-ADMIN via menu navigation Sales > Demo bike [^r2][^r9].

| Field | Label | Type / Format | Mandatory? | Notes |
|---|---|---|---|---|
| `dmo_no` | DMO NO | System / Reference | Mandatory | Sequential loan reference assigned automatically on commit; left blank on initial entry [^r1][^r3][^r6][^r10]. |
| `itm_cd` | ITEM CD | Item code | Mandatory | Must represent an active finished good item [^r1][^r7][^r10]. |
| `serial_no` | SERIAL NO | Serial number | Mandatory | Must exist and be available in stock [^r1][^r7][^r10]. |
| `cust_cd` | CUST CD | Customer code | Mandatory | Must represent an active sales ledger account [^r1][^r7][^r10]. |
| `return_dt` | RETURN DT | Date | Mandatory | Expected return date checkpoint [^r1][^r7][^r10][^r20]. |
| `status` | STATUS | Status flag | Optional | Indicates active loan status; updated automatically on save and close [^r1][^r3][^r10]. |
| `comment` | COMMENT | Free text | Optional | Used for recording extension authorizations or refurbishment notes [^r1][^r5][^r8][^r10]. |

## Fields

Screen SAL-DMO-17 requires mandatory entry of `itm_cd`, `serial_no`, `cust_cd`, `return_dt`, and `dmo_no` [^r1][^r10]. Optional fields comprise `status` and `comment` [^r1][^r10]. 

On new loan entries, `dmo_no` is left blank because the system automatically assigns the sequential identifier upon database commit [^r3][^r6]. Validation confirms that `itm_cd` represents an active finished good, `serial_no` is available in stock, `cust_cd` corresponds to an active sales ledger account, and `return_dt` is populated [^r7]. The loan record tracks the origin depot (Leeds unit or Manchester plant) and displays loan status on the main sales order screen [[screen-sal-so-01|SAL-SO-01]] while preventing standard retail delivery note generation [^r20][^r21]. Carrier portal payloads and export services capture the loan flag to enforce loan delivery signatures and exclude units from turnover calculations [^r24].

## Keys and services

Screen actions map functional keys and buttons to backend services in the [[services-sal-dmo|SAL dmo services]] group [^r2][^r11][^r12]:

* **Save (F8)** invokes `dmo_save` to write demonstration loan records using item code, serial number, customer code, and return date, setting `status` to active [^r3][^r11][^r16].
* **Get (F3)** invokes `dmo_get` (`POST /ll72/svc/dmo_get`) to retrieve loan records using the mandatory `dmo_no` key [^r4][^r11][^r15].
* **Search (F2/Enter)** invokes `dmo_search` (DEMO BIKE LIST) using parameters `itm_cd`, `serial_no`, `cust_cd`, and `status` [^r4][^r11][^r17][^r18].
* **Close** executes write service `dmo_close` (DEMO BIKE CLOSE via stored procedure `sp_dmo_close`), passing `dmo_no` and optional `comment`, followed by `dmo_save` to reinstate the asset to quarantine or refurbishing inventory without leaving a sales ledger balance [^r5][^r11][^r13][^r14][^r22].

Modifications to return dates or active loan cancellations are restricted by role permissions to authorised sales supervisors [^r23]. Loan extensions are processed by fetching the record with `dmo_get`, updating `return_dt`, adding authorisation details into `comment`, and pressing `dmo_save` [^r8].

## Messages

The screen reports the following error codes [^r11]:

* [[err-itm-0011]]: Raised when the entered item code is invalid or inactive [^r11].
* [[err-dmo-0001]]: Raised when the requested demonstration loan reference cannot be found [^r11].
* [[err-dmo-0801]]: Raised when attempting operations on a closed demonstration loan entry [^r11].

## See also

* [[err-dmo-0001|ERR-DMO-0001 DEMO BIKE NOT FOUND]]
* [[err-dmo-0801|ERR-DMO-0801 DEMO BIKE CLOSED]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[screen-sal-cus-01|SAL-CUS-01 Customer Master Entry]]
* [[screen-sal-so-01|SAL-SO-01 Sales Order]]
* [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]
* [[services-sal-dmo|SAL dmo services]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 66, §20. Demo Bike (SAL-DMO-17)
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 66, §20. Demo Bike (SAL-DMO-17)
[^r19]: 08_release_notes/RN-7.1.1 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r20]: 08_release_notes/RN-7.1.1 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r9]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-DMO-17 DEMO BIKE ENTRY
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 67, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 69, Worked example
[^r10]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-DMO-17 DEMO BIKE ENTRY
[^r7]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 69, Worked example
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 68, Closing a returned demonstration bicycle
[^r8]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 69, Tips
[^r21]: 08_release_notes/RN-7.1.1 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r24]: 08_release_notes/RN-7.1.1 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r11]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 35, SAL-DMO-17 DEMO BIKE ENTRY
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 52, SAL-DMO-17
[^r16]: 04_service_definitions/sales/dmo_save.yaml, service: dmo_save
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 68, PART 14 of 14
[^r15]: 04_service_definitions/sales/dmo_get.yaml, service: dmo_get
[^r17]: 04_service_definitions/sales/dmo_search.yaml, service: dmo_search
[^r18]: 04_service_definitions/sales/dmo_search.yaml, request.fields
[^r13]: 04_service_definitions/sales/dmo_close.yaml, service
[^r14]: 04_service_definitions/sales/dmo_close.yaml, request.fields
[^r22]: 08_release_notes/RN-7.1.1 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r23]: 08_release_notes/RN-7.1.1 Ledgerline Release Notes.pdf, p. 2, §3. Details
