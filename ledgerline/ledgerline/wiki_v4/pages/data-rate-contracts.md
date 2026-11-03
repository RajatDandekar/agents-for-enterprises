---
title: "Rate Contracts 2025-26 and 2026-27"
type: "data-source"
slug: "data-rate-contracts"
summary: "Master spreadsheet recording agreed supplier unit purchase rates and contract validity windows for 2025-26 and 2026-27."
audience: "staff"
status: "current"
sources: ["05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx |
| Type | Master data workbook |
| Sheets | 2025-26, 2026-27 |
| Active sheet | 2026-27 |
| Current rows | 1,611 |
| Active suppliers | 298 |
| Active items | 1,206 |
| Key column | line (composite key) |

The rate contracts master workbook defines Northbridge Cycles' agreed unit purchase prices and validity periods across supplier contracts[^r1][^r2]. As of 26 October 2026, sheet 2026-27 provides the active rates across 298 suppliers and 1,206 items[^r1]. All rates in sheet 2026-27 are quoted in GBP per unit excluding VAT and include delivery duty paid to Manchester unless noted[^r2].

## What it holds

The workbook maintains annual procurement rate agreements across two financial year sheets: `2025-26` and `2026-27`[^r1][^r4]. Sheet 2026-27 contains 1,611 active rate contract entries[^r1]. Sheet 2025-26 retains 1,610 expired rate agreement lines that were valid from 2025-04-01 to 2026-03-31[^r4]. Historical entries on sheet 2025-26 include agreements such as line ACP-CAR-0712/ACC-CGD/2025-04-01 under contract RC/2025/337 at 44.11[^r5], line ACP-CAR-0712/GRP-ERG-02/2025-04-01 under RC/2025/923 at 57.60[^r6], and line ACP-CAR-0712/GRP-ERG-03/2025-04-01 under RC/2026/309 at 25.46[^r7]. Further expired 2025-26 lines include fasteners from AF-ARN-0558 under RC/2025/477 at 0.10 for FST-BLT-M4X16-ZN[^r8] and RC/2025/906 at 0.28 for FST-BLT-M8X10-BK[^r9], item CHG-4A-01 from CC-SAL-0031 at 93.50[^r10], packaging labels PKG-LBL-UN from HP-WIG-0928 under RC/2025/390 at 6.13[^r11], box BOX-BIKE-01 from IP-MAN-0055 at 20.40[^r12], and items BEL-STD-01 at 6.55[^r13] and BRK-PAD-01 at 9.10[^r14] from PB-MAN-0017.

## Columns

Both sheet 2025-26 and sheet 2026-27 structure their records using 7 columns[^r1][^r4]:

* `line`: the unique line identifier[^r1][^r3][^r4]
* `sup_cd`: the supplier account code[^r1][^r4]
* `itm_cd`: the internal item code[^r1][^r4]
* `rate`: the agreed price in GBP per unit[^r1][^r2][^r4]
* `valid_from`: the commencement date of the contract rate[^r1][^r4]
* `valid_to`: the expiration date of the contract rate[^r1][^r4]
* `contract_no`: the reference number of the rate contract[^r1][^r4][^r5]

## How to look up a row

Lookups are performed using the composite `line` key column[^r3]. The key combines the supplier code, item code, and start date separated by slashes, formatted as `<sup_cd>/<itm_cd>/<valid_from>` (for example, `ACP-CAR-0712/ACC-CGD/2026-04-01`)[^r3].

## Size

* **Sheet 2026-27**: 1,611 rows covering 298 distinct suppliers and 1,206 distinct items[^r1].
* **Sheet 2025-26**: 1,610 rows (expired)[^r4].

## Versions and conflicts

* Today's rule: Current purchases reference sheet 2026-27, which contains 1,611 live contract rows[^r1].
* Older rule: Sheet 2025-26 contains 1,610 contract rate lines whose validity expired on 2026-03-31[^r4].
* Sources and dates: `05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx` (sheets `2025-26` and `2026-27`)[^r1][^r4].
* Kind: `superseded`[^r4].

## See also

* [[items-bat|BAT-* items]]
* [[items-bel|BEL-* items]]
* [[items-box|BOX-* items]]
* [[items-brk|BRK-* items]]
* [[items-chg|CHG-* items]]
* [[items-mnt|MNT-* items]]
* [[items-pkg|PKG-* items]]
* [[sup-nc-gda-0063|Nordic Cell Co. (NC-GDA-0063)]]
* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]

## References

[^r1]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, SHEET 2026-27
[^r2]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, SHEET 2026-27
[^r4]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, SHEET 2025-26
[^r5]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row ACP-CAR-0712/ACC-CGD/2025-04-01, SHEET 2025-26
[^r6]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row ACP-CAR-0712/GRP-ERG-02/2025-04-01, SHEET 2025-26
[^r7]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row ACP-CAR-0712/GRP-ERG-03/2025-04-01, SHEET 2025-26
[^r8]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row AF-ARN-0558/FST-BLT-M4X16-ZN/2025-04-01, SHEET 2025-26
[^r9]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row AF-ARN-0558/FST-BLT-M8X10-BK/2025-04-01, SHEET 2025-26
[^r10]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row CC-SAL-0031/CHG-4A-01/2025-04-01, SHEET 2025-26
[^r11]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row HP-WIG-0928/PKG-LBL-UN/2025-04-01, SHEET 2025-26
[^r12]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row IP-MAN-0055/BOX-BIKE-01/2025-04-01, SHEET 2025-26
[^r13]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row PB-MAN-0017/BEL-STD-01/2025-04-01, SHEET 2025-26
[^r14]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2025-26, row PB-MAN-0017/BRK-PAD-01/2025-04-01, SHEET 2025-26
[^r3]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row ACP-CAR-0712/ACC-CGD/2026-04-01, SHEET 2026-27
