---
title: "Bank File Sample 2026-10-22 (PR-20261022)"
type: "data-source"
slug: "data-bank-file-sample-2026-10-22"
summary: "Sample fixed-width BACS export file generated on 22 October 2026 for payment run PR-20261022 covering three suppliers."
audience: "staff"
status: "current"
sources: ["12_integrations/bank_file_sample_2026-10-22.txt"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | PR-20261022 |
| type | BACS export file sample |
| origin_account | 099401 27631884520 |
| date | 2026-10-22 |
| format | Fixed-width text |
| status | current |

This sample bank export file represents the output generated for accounts payable payment run PR-20261022 on 22 October 2026 [^r1]. It provides a fixed-width reference layout for automated BACS transmissions originating from Northbridge Cycles' disbursement account [^r1]. Today, it documents standard bank line formatting and field values for testing and verifying supplier payment processing [^r1].

| Field | Value |
|---|---|
| Run code | PR-20261022 |
| Source file | `12_integrations/bank_file_sample_2026-10-22.txt` |
| Format | Fixed-width BACS text |
| Originating account | 099401 27631884520 |
| Export date | 2026-10-22 |
| Record count | 3 payment lines |

## What it holds

The file holds transactional BACS payment records generated during payment run PR-20261022 [^r1]. Each entry specifies destination banking coordinates, formatted disbursement amounts, and beneficiary details originating from Northbridge Cycles account details 099401 27631884520 [^r1]. The export covers payments to three suppliers: [[sup-pennine-brakes|Pennine Brakes]], [[sup-irwell-packaging|Irwell Packaging]], and [[sup-castlefield-charge|Castlefield Charge]] [^r1].

## Columns

The data is formatted as fixed-width text records containing the following structural fields [^r1]:

* **Sort Code**: Destination clearing code formatted with hyphens [^r2][^r3][^r4].
* **Account Number**: 8-digit recipient bank account number [^r2][^r3][^r4].
* **Amount**: Fixed-length numerical monetary field with zero-padding (two implied decimal places) [^r2][^r3][^r4].
* **Beneficiary Name**: Plain text corporate entity name [^r1].

## How to look up a row

Individual payment transactions can be identified by the destination bank details (sort code and account number) or by the supplier beneficiary name [^r1][^r2][^r3][^r4].

On 22 October 2026, the specific payment records included:
* [[sup-pennine-brakes|Pennine Brakes]]: Sort code 20-45-11, account 73319201, payment of £18,734.40 (amount field `00001873440`) [^r2].
* [[sup-irwell-packaging|Irwell Packaging]]: Sort code 30-98-76, account 11829304, payment of £51,600.00 (amount field `00005160000`) [^r3].
* [[sup-castlefield-charge|Castlefield Charge]]: Sort code 40-22-14, account 90012877, payment of £220,992.00 (amount field `00022099200`) [^r4].

## Size

The sample contains 3 fixed-width detail rows totaling £291,326.40 in payment instructions [^r1][^r2][^r3][^r4].

## See also

* [[sop-ap-003|SOP-AP-003 Supplier Payment Run]]
* [[sup-pennine-brakes|Pennine Brakes]]
* [[sup-irwell-packaging|Irwell Packaging]]
* [[sup-castlefield-charge|Castlefield Charge]]

## References

[^r1]: 12_integrations/bank_file_sample_2026-10-22.txt, whole file
[^r2]: 12_integrations/bank_file_sample_2026-10-22.txt, whole file
[^r3]: 12_integrations/bank_file_sample_2026-10-22.txt, whole file
[^r4]: 12_integrations/bank_file_sample_2026-10-22.txt, whole file
