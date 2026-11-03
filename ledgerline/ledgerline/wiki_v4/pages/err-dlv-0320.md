---
title: "ERR-DLV-0320 Lithium Battery Label Required"
type: "error"
slug: "err-dlv-0320"
summary: "Error blocking despatch posting for battery packs until lithium battery labels are printed, requiring supervisor intervention to clear the transaction flag."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf", "11_training/QRC-07 Lithium battery labels.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-DLV-0320 |
| message | Lithium Battery Label Required |
| type | Error |
| module | Despatch (DLV) |

ERR-DLV-0320 is a Ledgerline despatch validation error raised when an operator attempts to post a despatch note containing a battery pack before printing the mandatory lithium battery label [^r1]. As of 26 October 2026, handling this error requires a system supervisor to clear the blocked transaction flag before the label can be reprinted [^r3][^r4]. It enforces compliance with dangerous goods packaging rules prior to physical goods release [^r1].

## Meaning

The error indicates that a despatch transaction containing a battery pack was posted prior to generating and printing the lithium battery label [^r1][^r3].

## Cause

The error is triggered when an operator attempts to post a despatch note for items containing a battery pack before the lithium battery label has been printed [^r1][^r3].

## How to fix

When ERR-DLV-0320 occurs, the user must contact the system supervisor to clear the transaction flag before reprinting [^r3][^r4]. Once the flag is cleared, staff can print the lithium battery label and retry posting the despatch note [^r2][^r3].

## Raised by

Raised during the posting of a despatch note containing battery packs within the despatch sequence in the system [^r1][^r3][^r4].

## Versions and conflicts

- **Contradiction**: Under [[qrc-07|QRC-07]] (2026-01-12), the user must contact the system supervisor to clear the transaction flag before reprinting the label [^r3][^r4]. Under the older [[sop-sal-001|SOP-SAL-001]] v2.2 (2025-03-01), the user could navigate directly to label printing, generate the lithium battery label, and retry posting without supervisor intervention [^r2]. The newer procedure in QRC-07 governs today's workflow [^r3][^r4].

## See also

- [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]
- [[qrc-07|QRC-07 Quick reference: Lithium battery labels]]
- [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]

## References

[^r1]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 3, §5. Procedure
[^r3]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Steps
[^r4]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Despatch sequence in the system
[^r2]: 02_procedures/SOP-SAL-001 Sales Order to Despatch v2.2.pdf, p. 4, §5. Procedure: notes and common mistakes
