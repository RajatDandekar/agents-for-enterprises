---
title: "ERR-PKB-0001 Primary Kanban Validation Failure"
type: "error"
slug: "err-pkb-0001"
summary: "Error raised during production kanban entry or shop floor signalling when validation fails or a card is missing or already active."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-PKB-0001 |
| Module | PRD (Production) |
| Screen | PRD-PKB-15 |
| Service group | services-prd-pkb |
| Status | Current |

ERR-PKB-0001 is a Ledgerline production module error encountered during production kanban maintenance or shop floor signalling [^r1][^r3]. It blocks processing when kanban header parameters fail validation checks or when an unfulfilled kanban card is signalled again [^r1][^r3]. Resolving the error requires ensuring all mandatory card fields are complete or clearing previously outstanding signals [^r2][^r3].

## Meaning

ERR-PKB-0001 indicates a primary kanban validation failure [^r1]. In the error table, the message is defined as "PRODUCTION KANBAN NOT FOUND" [^r3].

## Cause

The validation failure occurs when a mandatory field is left blank, the card reference format is invalid, or the entered card number does not exist in the system [^r1]. On the shop floor, it is raised when an operator attempts to signal a kanban card that has already been signalled and remains outstanding [^r3].

## How to fix

Users must ensure that PKB NO, ITEM CD, WORK CENTRE, and QTY contain valid data prior to clicking action buttons [^r2]. When signalling on the shop floor, verify that the card number exists and that the previous signal has been fulfilled before signalling again [^r1][^r3].

## Raised by

The error is raised by [[services-prd-pkb|PRD pkb services]] within [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]], accessed via screen [[screen-prd-pkb-15|PRD-PKB-15 Production Kanban Entry]] and shop floor signalling entry [^r1][^r2][^r3].

## Versions and conflicts

- **contradiction**: In [[man-prd-72|MAN-PRD-72]] (p. 71), ERR-PKB-0001 is described as a validation failure resulting from blank mandatory fields, invalid reference formatting, or missing card numbers [^r1]. Conversely, the worked example on p. 72 defines ERR-PKB-0001 as "PRODUCTION KANBAN NOT FOUND" and describes it as occurring when attempting to signal a kanban card that has already been signalled and remains outstanding [^r3]. Sources: MAN-PRD-72 v7.2.3 (2025-01-15) [^r1][^r3].

## See also

- [[screen-prd-pkb-15|PRD-PKB-15 Production Kanban Entry]]
- [[services-prd-pkb|PRD pkb services]]
- [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 71, Messages
[^r3]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 72, Worked example
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 71, Messages
