---
doc_id: POL-FIN-024
title: GST on Supplier Invoices
owner: Finance (Tax), Rasoi Steel Works
version: 2.0
effective: 2026-04-01
audience: accounts payable
---

# GST on Supplier Invoices (POL-FIN-024)

1. A supplier in Maharashtra charges CGST + SGST: use a tax code ending **-INTRA**. A supplier in any other state charges IGST: use **-INTER**. Bahi's shared tax engine refuses a code that does not match the supplier's state (ERR-PO-0412).
2. Deccan Polymers and Deccan Paints & Inks are in Gujarat (IGST). Sahyadri Valves, Om Sheet Metals and Shree Packaging are in Maharashtra.
3. When an invoice is posted, its GST is recorded as **input credit** for that month. Input credit is claimed only for posted invoices; an invoice on hold carries no credit.
4. A credit note from a supplier reduces both the amount and the GST. Ask for the GST on the difference too: on ₹9,000 at 18% IGST that is ₹1,620.
