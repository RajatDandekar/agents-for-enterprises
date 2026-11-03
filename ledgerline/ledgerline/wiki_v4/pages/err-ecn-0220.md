---
title: "ERR-ECN-0220 Open Work Orders on Revision"
type: "error"
slug: "err-ecn-0220"
summary: "Error triggered when attempting to release an engineering change while active work orders or unfinished kitting lists remain open on the earlier revision."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-ECN-0220 |
| module | PRD / ECN |
| type | error |
| screen | PRD-ECN-06 |
| owner | Production Control |

ERR-ECN-0220 is a Ledgerline error code that blocks the release of an engineering change notice. It indicates that active production documents are still linked to the superseded revision. Engineering changes cannot proceed to release status until all open orders across Manchester and Leeds are resolved.

## Meaning
ERR-ECN-0220 indicates that an engineering change cannot be released because active work orders, assembly cards, or unfinished kitting lists remain open against the earlier revision [^r1].

## Cause
The error occurs when a user attempts to release an engineering change while work orders, assembly cards, or unfinished kitting lists tied to the earlier revision are still open in Ledgerline [^r1].

## How to fix
To clear ERR-ECN-0220, users must generate the live assembly listing and trace all offending orders across Manchester and Leeds [^r2]. Production control must then either complete those orders under the old revision or close and re-issue the tickets [^r2].

## Raised by
The error is raised by [[screen-prd-ecn-06|PRD-ECN-06 Engineering Change Entry]] during the release step defined in [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]] [^r1].

## See also
* [[sop-prd-002|SOP-PRD-002 Engineering Change (ECN)]]
* [[screen-prd-ecn-06|PRD-ECN-06 Engineering Change Entry]]
* [[errors-ecn|ERR-ECN Error Codes Reference]]

## References

[^r1]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-PRD-002 Engineering Change v1.0.pdf, p. 4, §5. Procedure: notes and common mistakes
