---
doc_id: POL-FIN-024
title: VAT on Supplier Invoices
owner: Finance (Tax), Northbridge Cycles
version: 2.0
effective: 2026-04-01
audience: accounts payable
---

# VAT on Supplier Invoices (POL-FIN-024)

1. A supplier in England charges CGST + SGST: use a tax code ending **-INTRA**. A supplier in any other state charges IGST: use **-INTER**. Ledgerline's shared tax engine refuses a code that does not match the supplier's state (ERR-PO-0412).
2. Voltway Cells and Voltway Paints & Coatings are in the Netherlands (IGST). Pennine Brakes, Castlefield Chargers and Irwell Packaging are in England.
3. When an invoice is posted, its VAT is recorded as **input credit** for that month. Input credit is claimed only for posted invoices; an invoice on hold carries no credit.
4. A credit note from a supplier reduces both the amount and the VAT. Ask for the VAT on the difference too: on £9,000 at 18% IGST that is £1,620.
