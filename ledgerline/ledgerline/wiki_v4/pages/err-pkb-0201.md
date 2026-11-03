---
title: "ERR-PKB-0201 Duplicate Active Kanban Cycle"
type: "error"
slug: "err-pkb-0201"
summary: "Production kanban error raised when an identical replenishment cycle is already active, with manual conflicts regarding work centres and zero quantity."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-PKB-0201 |
| Module | PRD (Production) |
| Screen | [[screen-prd-pkb-15|PRD-PKB-15 Production Kanban Entry]] |
| Status | mixed |
| Owner | Production |

ERR-PKB-0201 is a Ledgerline production kanban error documented in [[man-prd-72|MAN-PRD-72]]. As of 26 October 2026, the primary system documentation defines it as a block against transmitting duplicate replenishment requests for an active card, item, and line location combination. However, the user manual contains internal contradictions that also assign this code to quantity validation and work centre status issues.

| Attribute | Value |
|---|---|
| Error code | ERR-PKB-0201 |
| Module | Production (PRD) |
| Standard text | Duplicate Active Kanban Cycle / QTY MUST BE > 0 |
| Raised by | [[services-prd-pkb|PRD pkb services]] |
| Related screen | [[screen-prd-pkb-15|PRD-PKB-15 Production Kanban Entry]] |

## Meaning
The primary functional definition states that ERR-PKB-0201 indicates a replenishment request cannot be transmitted because an identical kanban cycle is already active for that specific combination of card, item, and line location [^r1]. In the reference message catalogue of the same manual, the code corresponds to the literal text 'QTY MUST BE > 0' [^r3].

## Cause
Under the standard message documentation, the error is triggered when an operator attempts to transmit a replenishment cycle while an identical card, item, and line location cycle remains open [^r1]. According to the manual's FAQ guidance, saving a card with this error indicates that the selected work centre is marked as closed, suspended, or invalid for the chosen item in the work centre master file [^r4]. In the message catalogue listing, it is associated with entering a non-positive quantity [^r3].

## How to fix
When encountering ERR-PKB-0201, operators should not re-enter the card [^r2]. Instead, operators must inspect collection bays and replenishment queues to verify whether the requested batch is already in transit [^r2].

## Raised by
The message is raised during kanban replenishment transmission and card saving operations within [[services-prd-pkb|PRD pkb services]] on [[screen-prd-pkb-15|PRD-PKB-15 Production Kanban Entry]] [^r1][^r4].

## Versions and conflicts
* **Active duplicate cycle versus zero quantity**: The messages section defines ERR-PKB-0201 as an active duplicate cycle error for an identical card, item, and line location (MAN-PRD-72 v7.2.3, 2025-01-15, p. 71) [^r1], whereas §22 Message Catalogue lists the code as 'QTY MUST BE > 0' (MAN-PRD-72 v7.2.3, 2025-01-15, p. 73) [^r3] (`contradiction`).
* **Active duplicate cycle versus invalid work centre**: The messages section defines the error as a duplicate active cycle (MAN-PRD-72 v7.2.3, 2025-01-15, p. 71) [^r1], whereas the FAQ section states that ERR-PKB-0201 on saving indicates the entered work centre is closed, suspended, or invalid for the selected item in the work centre master file (MAN-PRD-72 v7.2.3, 2025-01-15, p. 72) [^r4] (`contradiction`).

## See also
* [[screen-prd-pkb-15|PRD-PKB-15 Production Kanban Entry]]
* [[services-prd-pkb|PRD pkb services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[screen-prd-wc-10|PRD-WC-10 Work Centre]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 71, Messages
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 73, §22. Messages
[^r4]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Questions users ask
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 71, Messages
