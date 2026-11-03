---
title: "ERR-KBN-0001 Kanban Card Not Found or Duplicate Signal"
type: "error"
slug: "err-kbn-0001"
summary: "Ledgerline error when a Kanban card record is missing, has a key conflict on save, or receives a duplicate replenishment signal."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-KBN-0001 |
| Module | Inventory (INV) |
| Type | Error |
| Manual | MAN-INV-72 |

Error ERR-KBN-0001 is a Ledgerline inventory validation code raised during Kanban card maintenance and signaling operations [^r1]. It indicates that the requested Kanban card cannot be found, that a record key conflict occurred upon saving, or that a duplicate signal was triggered for a card that is already active [^r1]. Crucially, Ledgerline enforces this check to block repeated replenishment cycles until outstanding cards are formally closed [^r2].

| Field | Value |
|---|---|
| Error Code | ERR-KBN-0001 |
| Module | Inventory (INV) |
| Impacted Service | [[services-inv-kbn|INV kbn services]] |
| Related Screen | [[screen-inv-kbn-13|INV-KBN-13 Kanban Card Entry]] |
| Reference Manual | [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]] |

## Meaning
ERR-KBN-0001 signifies that Ledgerline cannot locate the card record matching the requested KBN NO, encountered an existing key collision when attempting to save, or identified an invalid secondary signal on a card that currently sits in a signalled state [^r1].

## Cause
This error is triggered under three specific conditions:
* The user attempts to retrieve a card via KBN NO that does not exist in the database [^r1].
* A key conflict arises while attempting to save a Kanban record [^r1].
* The `kbn_signal` action is executed on a Kanban card that has already been placed in a signalled state [^r1].

## How to fix
* Verify that the entered KBN NO exists and is typed correctly before querying [^r1].
* Resolve any conflicting primary key values prior to saving new card definitions [^r1].
* Complete the ongoing replenishment cycle using `kbn_close` before attempting to issue another signal on the card, as Ledgerline explicitly blocks duplicate signals until the previous cycle finishes [^r2].

## Raised by
This error is raised by [[services-inv-kbn|INV kbn services]] during record retrieval, record save actions, or upon pressing `kbn_signal` within the [[screen-inv-kbn-13|INV-KBN-13 Kanban Card Entry]] interface [^r1].

## See also
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[screen-inv-kbn-13|INV-KBN-13 Kanban Card Entry]]
* [[services-inv-kbn|INV kbn services]]
* [[errors-inv|Errors INV (ERR-INV-*)]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 51, Messages
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 53, Questions users ask
