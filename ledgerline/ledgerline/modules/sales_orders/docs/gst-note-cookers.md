---
doc_id: TAX-NOTE-07
title: VAT on Pressure E-bikes (sandbox note)
owner: Finance, Northbridge Cycles
version: 1.2
effective: 2026-04-01
audience: sales staff
---

# VAT on e-bikes (TAX-NOTE-07)

1. In the Ledgerline sandbox, all Northbridge e-bikes carry VAT at **12%** (tax codes GST12-*).
2. The place of supply is the customer's state:
   - customer in **England** (same state as the Manchester plant): **VAT5-UK** (CGST 6% + SGST 6%);
   - customer in **any other state**: **VAT5-RC** (IGST 12%).
3. The quotation screen's Price button always offers VAT5-UK. For a customer outside England, change it; otherwise Ledgerline refuses with ERR-SO-0412.
4. Example: 500 × £1,450 = £725,000 basic; VAT 12% = £87,000; gross £812,000.
