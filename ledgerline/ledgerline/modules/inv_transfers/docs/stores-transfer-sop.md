---
doc_id: SOP-STR-021
title: Stock Transfer Procedure
owner: Stores, Northbridge Cycles
version: 2.0
effective: 2026-07-01
audience: stores staff, Manchester and Leeds
---

# Stock Transfer Procedure (SOP-STR-021)

## 1. Purpose
How stock moves between the stores of the Manchester plant (NBC-MAN-01) and the Leeds unit (NBC-LDS-01) in Ledgerline, so that the books always show where every piece is.

## 2. Locations
2.1 **WH-LDS-STR** Leeds stores. **WH-MAN-STR** Manchester main stores. **WH-PUN-LN5** the city e-bike line-side store, which feeds the city e-bike assembly line.
2.2 Material asked for "the line" or "the city e-bike line" goes to **WH-PUN-LN5**, not to main stores. Main stores is a different building; the line will not see it.

## 3. Raising a transfer
3.1 The receiving stores raises the transfer note on screen INV-TRN-04: Fetch, then Save.
3.2 Check free stock first on INV-STK-07. **Free = on hand − allocated − QC hold.** Only free stock may be transferred (see QA-SOP-009).
3.3 Ledgerline refuses a quantity above the stock on hand. If the quantity is above the free stock but within on hand, **Ledgerline saves the note as SH (short)**. An SH note waits for QC to release the held lot. It is never sent to the gate. Raise the note for the free quantity instead.
3.4 Use the right item code. BAT-500-R is a rework lot awaiting re-inspection and must not go to the line.

## 4. Moves inside one unit (INT)
4.1 A move inside one unit (for example WH-MAN-STR to WH-PUN-LN5) needs no gate pass. The receiving stores posts the receipt on INV-GTP-05 and both sides move at once.

## 5. Moves between units (IUT)
5.1 A move between Leeds and Manchester needs a gate pass (Gate Pass Policy, POL-SEC-004), created by the **issuing** stores.
5.2 Security checks the gate pass out at the issuing gate. From then until receipt the note is **in transit (IT)**.
5.3 Above £50,000 consignment value including VAT, an e-way bill is needed before the goods leave (FIN-NOTE-012).

## 6. Receipt
6.1 The receiving stores counts the goods **when they arrive** and posts the receipt (INV-GTP-05, Receive). Never post a receipt for goods that have not physically arrived.
6.2 Until the receipt is posted the goods are not in the receiving store's stock, and the line cannot draw them.
6.3 A short receipt is recorded as counted and reported to the issuing stores the same day.
