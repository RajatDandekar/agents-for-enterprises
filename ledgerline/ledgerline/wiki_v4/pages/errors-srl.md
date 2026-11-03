---
title: "ERR-SRL Serial Registration Error Codes"
type: "error-list"
slug: "errors-srl"
summary: "Reference list of ERR-SRL serial registration error codes raised by sales serial services in Ledgerline."
audience: "staff"
status: "current"
sources: ["04_service_definitions/sales/srl_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SRL |
| Domain | Sales / Serial Registration |
| Module | SAL |
| Related service group | services-sal-srl |

This catalogue records the `ERR-SRL-*` error codes returned by Ledgerline's sales serial registration services. It defines the system messages encountered during serial number lookups and record handling. Operational users and support staff reference these codes when processing serial records on screens such as [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]].

### ERR-SRL-0001
* **Message:** SERIAL REGISTRATION NOT FOUND [^r1]
* **Cause:** The requested serial registration record does not exist in the system [^r1].
* **Remedy:** Verify the serial identifier entered or ensure the record has been created prior to querying [^r1].
* **Raised by:** Service `srl_get` in [[services-sal-srl|SAL srl services]] [^r1].
* **Detailed page:** [[err-srl-0001|ERR-SRL-0001 Serial Number Already Registered]]

## See also
* [[services-sal-srl|SAL srl services]]
* [[screen-sal-srl-16|SAL-SRL-16 Serial Registration Reg]]
* [[err-srl-0001|ERR-SRL-0001 Serial Number Already Registered]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/sales/srl_get.yaml, errors
