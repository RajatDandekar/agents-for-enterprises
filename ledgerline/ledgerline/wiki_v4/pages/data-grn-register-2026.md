---
title: "GRN_register_2026"
type: "data-source"
slug: "data-grn-register-2026"
summary: "Goods receipt register for 2026 covering 1,383 receipts across three warehouses from Ledgerline ERP report INV-R030 and export data."
audience: "staff"
status: "current"
sources: ["06_transactions/GRN_register_2026.xlsx", "06_transactions/reports/Goods Receipt Register Jan-Oct 2026 (printed).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 06_transactions/GRN_register_2026.xlsx |
| Report code | INV-R030 |
| System | Ledgerline ERP 7.2 |
| Coverage | 2026-01-01 to 2026-10-26 |
| Transactions | 1,383 rows |
| Status | current |

The 2026 Goods Receipt Register records goods receipt note (GRN) transactions processed in Ledgerline ERP 7.2 from 2026-01-01 through 2026-10-26 [^r1][^r6]. As of 2026-10-26, it captures 1,383 receipt transactions joining header and line data across Northbridge Cycles' warehouse locations [^r1][^r6]. The register corresponds to printed ERP report INV-R030 generated on 2026-10-26 at 05:40 [^r6].

## What it holds
The register tracks all incoming deliveries logged against purchase orders, identifying the receipt date, supplier, item delivered, quantity, receiving warehouse, logging user, and supplier delivery note [^r1][^r2]. The 1,383 entries encompass receipts against 913 distinct purchase orders, 246 distinct supplier codes, and 647 distinct item codes [^r5]. Transactions are distributed across three distinct warehouse facilities: WH-LDS-STR, WH-MAN-MRO, and WH-MAN-STR [^r3]. All logged receipts in 2026 were entered by three users: [[user-atanaka|Aiko Tanaka]] (ATANAKA), [[user-cshaw|Callum Shaw]] (CSHAW), and [[user-ndoyle|Niamh Doyle]] (NDOYLE), though certain historical lines such as GRN/2026/28656 omit an entering user code [^r4][^r9]. Examples include receipt GRN/2026/28618 booked on 2026-01-10 for PO/2026/00001 (225 units of LAC-SLV from supplier SPC-WOL-0346 into WH-MAN-STR by ATANAKA under DN SP/DN/53879), and GRN/2026/28698 received on 2026-02-12 for PO/2026/00050 (6 units of MRO-00406 from supplier TES-TIL-0365 into WH-LDS-STR under DN TE/DN/18317) [^r8][^r10].

## Columns
The dataset contains nine primary fields matching the Ledgerline INV-R030 report structure [^r2][^r7]:

* `grn_no` (`GRN NO`): The unique goods receipt note identifier [^r2][^r7].
* `received_on` (`DATE`): Receipt transaction date [^r2][^r7].
* `po_no` (`PO NO`): Associated purchase order reference [^r2][^r7].
* `sup_cd` (`SUP CD`): Supplier master code [^r2][^r7].
* `itm_cd` (`ITEM CD`): Inventory item code [^r2][^r7].
* `qty` (`QTY`): Delivered quantity accepted [^r2][^r7].
* `whs_cd` (`WHS`): Receiving warehouse destination code [^r2][^r7].
* `received_by` (`BY`): User code of the receiving warehouse officer [^r2][^r7].
* `dn` (`DN`): Supplier delivery note reference number [^r2][^r7].

## How to look up a row
To look up a specific transaction, open sheet `GRN` in `06_transactions/GRN_register_2026.xlsx` and locate the row by the unique goods receipt number in column `grn_no` [^r1][^r2]. Alternatively, transactions can be queried by purchase order number (`po_no`) or filtered by receiving warehouse (`whs_cd`) and date range (`received_on`) [^r2][^r6].

## Size
The primary sheet `GRN` contains 1,383 transaction rows representing combined `grn_hdr` and `grn_line` data [^r1].

## See also
* [[user-atanaka|Aiko Tanaka]]
* [[user-cshaw|Callum Shaw]]
* [[user-ndoyle|Niamh Doyle]]

## References

[^r1]: 06_transactions/GRN_register_2026.xlsx, sheet GRN, SHEET GRN
[^r6]: 06_transactions/reports/Goods Receipt Register Jan-Oct 2026 (printed).pdf, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R030 GOODS RECEIPT REGISTER 2026
[^r2]: 06_transactions/GRN_register_2026.xlsx, sheet GRN, SHEET GRN
[^r5]: 06_transactions/GRN_register_2026.xlsx, sheet GRN, SHEET GRN
[^r3]: 06_transactions/GRN_register_2026.xlsx, sheet GRN, SHEET GRN
[^r4]: 06_transactions/GRN_register_2026.xlsx, sheet GRN, SHEET GRN
[^r9]: 06_transactions/reports/Goods Receipt Register Jan-Oct 2026 (printed).pdf, row GRN/2026/28656, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R030 GOODS RECEIPT REGISTER 2026
[^r8]: 06_transactions/reports/Goods Receipt Register Jan-Oct 2026 (printed).pdf, row GRN/2026/28618, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R030 GOODS RECEIPT REGISTER 2026
[^r10]: 06_transactions/reports/Goods Receipt Register Jan-Oct 2026 (printed).pdf, row GRN/2026/28698, p. 2, LEDGERLINE ERP 7.2 REPORT INV-R030 GOODS RECEIPT REGISTER 2026
[^r7]: 06_transactions/reports/Goods Receipt Register Jan-Oct 2026 (printed).pdf, p. 1, LEDGERLINE ERP 7.2 REPORT INV-R030 GOODS RECEIPT REGISTER 2026
