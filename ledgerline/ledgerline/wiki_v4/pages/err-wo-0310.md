---
title: "ERR-WO-0310 Component Shortage on Work Order Release"
type: "error"
slug: "err-wo-0310"
summary: "Error thrown when releasing a work order on PRD-WO-01 if required components face an inventory shortage."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-WO-0310 |
| Screen | PRD-WO-01 |
| Module | Production |
| Trigger | Work order release |
| Standard | SOP-PRD-001 |

Error ERR-WO-0310 prevents the release of a production work order when required components are not currently available in inventory [^r1]. It is raised directly within [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]] to avoid scheduling manufacturing without sufficient parts [^r1]. Users encountering this message are required by [[sop-prd-001|SOP-PRD-001 Work Order Release and Backflush]] to coordinate with inventory control rather than circumventing system checks [^r2].

## Meaning
The error indicates a component availability deficit during the release stage of a work order [^r1].

## Cause
The error is triggered when an attempt is made on [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]] to release a work order whose required component quantities exceed current availability [^r1].

## How to fix
Users must not attempt to bypass the check when ERR-WO-0310 occurs [^r2]. Instead, they must contact inventory control to verify whether the missing components are currently awaiting inspection or are scheduled on an urgent purchase order [^r2].

## Raised by
The error is raised by [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]] during the work order release action [^r1].

## See also
* [[screen-prd-wo-01|PRD-WO-01 Work Order Entry]]
* [[sop-prd-001|SOP-PRD-001 Work Order Release and Backflush]]

## References

[^r1]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 4, §5. Procedure: notes and common mistakes
[^r2]: 02_procedures/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf, p. 4, §5. Procedure: notes and common mistakes
