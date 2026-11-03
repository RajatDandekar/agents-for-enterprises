---
title: "Price list PL-UK-RTL 2026"
type: "data-source"
slug: "data-price-list-pl-uk-rtl"
summary: "UK retail bike shop price list covering 140 finished goods with prices excluding VAT effective from 1 April 2026."
audience: "staff"
status: "current"
sources: ["05_master_data/Price list PL-UK-RTL 2026.xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | PL-UK-RTL |
| Scope | UK bike shops |
| Currency | GBP (ex VAT) |
| Effective date | 2026-04-01 |
| Rows | 140 |
| Key column | itm_cd |
| Status | current |

Price list PL-UK-RTL establishes wholesale selling prices excluding VAT for UK bike shops effective from 2026-04-01 [^r1]. As of 26 October 2026, it is currently in force across Northbridge Cycles' UK retail bike shop channel [^r1]. The register defines commercial pricing for 140 finished goods across the [[items-fg|FG-* items]] range [^r2][^r3].

## What it holds
The file specifies standard UK bike shop pricing excluding VAT for finished goods, with all lines carrying an effective valid-from date of 2026-04-01 [^r1][^r3]. Sample listings include item FG-ANC-S-BLK (E-bike, Ancoats city, size S, black) priced at £1,614.05 ex VAT [^r4], and item FG-ANC-M-BLK (E-bike, Ancoats city, size M, black) priced at £2,370.05 ex VAT [^r5].

## Columns
The sheet `PL-UK-RTL` contains four columns [^r2]:
* `itm_cd`: item code for the finished good [^r2].
* `descr`: item description [^r2].
* `price_gbp_ex_vat`: unit price in GBP excluding VAT [^r2].
* `valid_from`: date from which the listed price is effective [^r2].

## How to look up a row
Look up rows in sheet `PL-UK-RTL` using the finished good code in column `itm_cd` [^r2].

## Size
The dataset contains 140 data rows [^r2].

## See also
* [[items-fg]]

## References

[^r1]: 05_master_data/Price list PL-UK-RTL 2026.xlsx, sheet PL-UK-RTL, SHEET PL-UK-RTL
[^r2]: 05_master_data/Price list PL-UK-RTL 2026.xlsx, sheet PL-UK-RTL, SHEET PL-UK-RTL
[^r3]: 05_master_data/Price list PL-UK-RTL 2026.xlsx, sheet PL-UK-RTL, SHEET PL-UK-RTL
[^r4]: 05_master_data/Price list PL-UK-RTL 2026.xlsx, sheet PL-UK-RTL, row FG-ANC-S-BLK, SHEET PL-UK-RTL
[^r5]: 05_master_data/Price list PL-UK-RTL 2026.xlsx, sheet PL-UK-RTL, row FG-ANC-M-BLK, SHEET PL-UK-RTL
