---
title: "Customers (bike shops)"
type: "data-source"
slug: "data-customers"
summary: "Master data spreadsheet listing 560 bike shop customer accounts across Europe and the UK, with credit limits, terms, and reps."
audience: "staff"
status: "current"
sources: ["05_master_data/Customers (bike shops).xlsx"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Source file | 05_master_data/Customers (bike shops).xlsx |
| Sheet | Customers |
| Row count | 560 |
| Key column | cust_cd |
| Columns | 9 |
| Status | current |

The Customers master data sheet records Northbridge Cycles' network of 560 bike shop accounts across the UK and Europe [^r1][^r2]. As of 26 October 2026, it serves as the operational reference for customer account status, assigned sales representatives, price lists, and credit limits [^r1][^r3][^r4][^r5]. All accounts are divided between two sales representatives and set to either active or on-hold status [^r4].

## What it holds
The workbook holds account records for bike shops operating across 42 cities in 7 countries, including BE, DE, DK, FR, GB, and IE [^r1][^r2]. Each entry records the commercial parameters governing sales orders, including assigned payment terms, applicable price lists, credit limits, account operational status, and the assigned internal sales representative [^r1][^r3][^r4][^r5].

Accounts are categorised under three price lists: PL-EU-RTL, PL-KEY, and PL-UK-RTL [^r3]. Payment terms across all accounts are restricted to ADV, N30, or N45 [^r3]. Account statuses are maintained as either ACTIVE or ON HOLD, and portfolio coverage is split between sales representatives [[user-echen|Ethan Chen]] (ECHEN) and [[user-imorgan|Isla Morgan]] (IMORGAN) [^r4]. Credit limits are assigned in five tiers: 15,000, 25,000, 40,000, 60,000, or 100,000 [^r5].

## Columns
The single sheet `Customers` comprises 9 columns [^r1]:
* `cust_cd`: unique customer code [^r1]
* `name`: trading name of the bike shop [^r1]
* `country`: country code (including BE, DE, DK, FR, GB, IE) [^r1][^r2]
* `city`: city location across 42 distinct municipalities [^r1][^r2]
* `price_list`: price list tier (PL-EU-RTL, PL-KEY, PL-UK-RTL) [^r1][^r3]
* `credit_limit`: credit limit tier (15,000, 25,000, 40,000, 60,000, or 100,000) [^r1][^r5]
* `pt_cd`: payment terms code (ADV, N30, N45) [^r1][^r3]
* `status`: account status (ACTIVE or ON HOLD) [^r1][^r4]
* `rep`: assigned sales representative code (ECHEN or IMORGAN) [^r1][^r4]

## How to look up a row
Look up accounts in sheet `Customers` using the primary key `cust_cd` in the first column [^r1].

## Size
The dataset contains 560 data rows across 9 columns in the single sheet `Customers` [^r1].

## See also
* [[user-echen|Ethan Chen (ECHEN)]]
* [[user-imorgan|Isla Morgan (IMORGAN)]]

## References

[^r1]: 05_master_data/Customers (bike shops).xlsx, sheet Customers, PART 1 of 1 (sheet Customers)
[^r2]: 05_master_data/Customers (bike shops).xlsx, sheet Customers, PART 1 of 1 (sheet Customers)
[^r3]: 05_master_data/Customers (bike shops).xlsx, sheet Customers, PART 1 of 1 (sheet Customers)
[^r4]: 05_master_data/Customers (bike shops).xlsx, sheet Customers, PART 1 of 1 (sheet Customers)
[^r5]: 05_master_data/Customers (bike shops).xlsx, sheet Customers, PART 1 of 1 (sheet Customers)
