---
doc_id: PUR-SOP-021
title: Delivery Schedule SOP
owner: Purchase department, Northbridge Cycles
version: 1.6
effective: 2026-06-01
audience: purchase staff
---

# Delivery Schedule SOP (PUR-SOP-021)

1. Every released order carries a **delivery schedule**: one or more lines of date and quantity. Stores plan the gate and the line-side stock from it.
2. On PUR-POM-08 the schedule grid (SCH 1, SCH 2) holds the **new** lines for the quantity not yet received. Received lines stay as they are.
3. The schedule must add up: **received quantity + the new lines = the new order quantity**, and **the last line falls on the new need-by date**.
4. If you leave the grid blank, Ledgerline keeps the old lines. If they no longer add up, Ledgerline **still says SAVED**, but holds the amendment (status HD, warning W-SCH-209). A held amendment is not sent for approval and the supplier is not told.
5. To fix a held amendment, open it on PUR-POM-08 and use **Fix Schedule**. Ledgerline checks it again and sends it on for approval if needed.
6. Check the amendment status on PUR-POA-09 or in the order's revision list after every save.
7. Example: Emma's order PO/2026/01182 is 20,000 battery packs: 10,000 on 30 Oct and 10,000 on 2 Nov. To make it 15,000 on 9 Nov, enter NEW QTY 15000, NEW NEED DT 09-11-2026 and SCH 1 = 09-11-2026 / 15000.
