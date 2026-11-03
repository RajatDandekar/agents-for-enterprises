---
title: "SAL-SRL-16 Serial Registration Reg"
type: "screen"
slug: "screen-sal-srl-16"
summary: "Ledgerline screen for registering and querying frame and battery pack serial numbers for warranty validation."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf", "03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/sales/srl_get.yaml", "04_service_definitions/sales/srl_reg.yaml", "04_service_definitions/sales/srl_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen Code | SAL-SRL-16 |
| Screen Title | SERIAL REGISTRATION REG |
| Module | Sales > Serial registration |
| Authorized Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN |
| Read Service | srl_get |
| Write Service | srl_reg |
| Search Service | srl_search |

Screen SAL-SRL-16 is the Ledgerline interface used to record and verify serial registration details for frame and battery pack components [^r1][^r7]. It establishes the registration status necessary to validate customer warranty claims [^r1]. Access is restricted to users assigned to the roles SAL-EXEC, SAL-MGR, or SYS-ADMIN [^r7].

| Field | Detail |
|---|---|
| Screen Code | SAL-SRL-16 [^r2][^r7] |
| Screen Title | SERIAL REGISTRATION REG [^r7] |
| Menu Path | Sales > Serial registration [^r7] |
| Allowed Roles | SAL-EXEC, SAL-MGR, SYS-ADMIN [^r7] |
| Primary Services | [[services-sal-srl|srl_search]], [[services-sal-srl|srl_get]], [[services-sal-srl|srl_reg]] [^r4][^r8][^r9][^r10][^r11] |

## Fields

* **SERIAL NO** (`serial_no`): Mandatory serial identifier for the frame or battery pack [^r2][^r7].
* **ITEM CD** (`itm_cd`): Mandatory inventory item code [^r2][^r7].
* **CUST CD** (`cust_cd`): Optional customer account code [^r2][^r7]. When processing large dispatch batches for a single bike shop, this field retains its value if the operator applies the standard terminal reset key instead of closing the screen [^r5].
* **SOLD DT** (`sold_dt`): Optional sale date [^r2][^r7]. If left blank during entry, Ledgerline populates it automatically with the current system working date [^r3].
* **STATUS** (`status`): Optional status field [^r2][^r7].

## Keys and services

* **Search (F2/Enter)**: Executes service `srl_search` (SERIAL REGISTRATION LIST) via endpoint `POST /ll72/svc/srl_search` to list serial registrations [^r4][^r8][^r11].
* **Get (F3)**: Executes read service `srl_get` (SERIAL REGISTRATION GET) to retrieve serial registration details by `serial_no` [^r4][^r8][^r9].
* **Reg**: Executes write service `srl_reg` (SERIAL REGISTRATION REG) via endpoint `POST /ll72/svc/srl_reg` to register new serial numbers [^r4][^r8][^r10].

Operators must not trigger `srl_reg` to amend an existing dispatch date or customer code; returned bicycles require goods inward credit handling procedures prior to making changes [^r6].

## Messages

* [[err-itm-0011|ERR-ITM-0011]]: ITEM NOT FOUND OR INACTIVE [^r8].
* [[err-srl-0001|ERR-SRL-0001]]: Serial Number Already Registered [^r8].

## See also

* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]
* [[err-srl-0001|ERR-SRL-0001 Serial Number Already Registered]]
* [[services-sal-srl|SAL srl services]]

## References

[^r1]: 02_procedures/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf, p. 3, §5. Procedure
[^r7]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 39, SAL-SRL-16 SERIAL REGISTRATION REG
[^r2]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 62, §19. Serial Registration (SAL-SRL-16)
[^r4]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 63, Screen Layout and Fields
[^r8]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 40, SAL-SRL-16 SERIAL REGISTRATION REG
[^r9]: 04_service_definitions/sales/srl_get.yaml, service: srl_get
[^r10]: 04_service_definitions/sales/srl_reg.yaml, service: srl_reg
[^r11]: 04_service_definitions/sales/srl_search.yaml, service
[^r5]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 65, Tips
[^r3]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 64, Step by step
[^r6]: 03_ledgerline_manuals/MAN-SAL-72 Ledgerline 7.2 User Manual - Sales and Distribution v7.2.3.pdf, p. 65, Tips
