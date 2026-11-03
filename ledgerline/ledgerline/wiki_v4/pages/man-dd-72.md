---
title: "MAN-DD-72 Ledgerline ERP 7.2 Data Dictionary, Purchasing"
type: "manual"
slug: "man-dd-72"
summary: "Data dictionary reference for Ledgerline ERP 7.2 purchasing payloads, tables, field formats, and core purchasing status and lookup codes."
audience: "staff"
status: "current"
sources: ["07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | MAN-DD-72 |
| title | Ledgerline ERP 7.2 Data Dictionary, Purchasing |
| version | 7.2.3 |
| effective | 2025-01-15 |
| status | current |
| module | Purchasing |

MAN-DD-72 defines the schema, table attributes, payload envelope, and field specifications for the purchasing module of Ledgerline ERP 7.2 [^r1]. It standardises technical exchange formats including date layouts, currency treatments, and database column definitions across purchasing entities [^r1][^r2]. As of 26 October 2026, this specification remains current for all interface integrations and database lookups [^r1][^r2].

## Payload envelope and conventions

Purchasing service responses are returned within a standard envelope composed of four fields: `rc` (return code: `S` for success, `E` for error), `err_cd` (the error code when `rc` is `E`), `msg` (a short message in capital letters), and `data` (the operation result) [^r1]. Across all purchasing payloads, dates adhere to the `YYYY-MM-DD` format, monetary values are recorded in pounds sterling with two decimal places, and alphanumeric codes are formatted in uppercase letters [^r2].

## Common codes and organisation units

Organisation unit codes (`ou_cd`) include `NBC-MAN-01` for the Manchester plant and `NBC-LDS-01` for the Leeds unit, with both entities mapped to country code `GB` [^r3]. Due to a 1998 naming convention, the legacy database column `state` stores the two-letter country code of a supplier or organisation unit [^r4]. 

Purchasing workflows recognise standard status codes:
* Document status values comprise `DR`, `PA`, `AP`, `RL`, `RJ`, `CN`, and `CL`, as specified in [[man-pur-72|MAN-PUR-72]] §16.1 [^r5].
* Supplier status codes in the supplier master are limited to `ACTIVE` or `BLOCKED` [^r6].
* Standard units of measure (`uom_cd`) include `NOS` for numbers or pieces and `KG` for kilograms [^r7].

## Master data structures

The item master (`itm_*`) tracks `itm_cd`, `descr`, `cell_safety` (a flag set to `1` by Quality if the item contains or charges lithium cells, and `0` otherwise), `category` (`RAW`, `COMPONENTS`, `SPARES`, or `PACKING`), the `active` flag, `reorder_lvl`, and `avg_daily_issue` [^r8].

The supplier master (`sup_*`) maintains generated `sup_cd`, `name`, `city`, `state`, `vat_no`, `pt_cd`, `status`, `created_by`, and `created_on`, with migrated suppliers displaying `MIGRATION` in audit fields [^r9]. Child entities linked to suppliers include:
* Supplier certificates (`sup_cert`): records capturing `cert_type` (`UN38.3`, `ISO-9001`, etc.), `doc_ref`, `valid_to`, `uploaded_by`, and `uploaded_on` [^r10].
* Supplier rate contracts (`sup_rate`): schedules specifying `itm_cd`, `rate`, `valid_from`, and `valid_to` [^r11].

## Purchasing transactions

Purchase requests (`pr_*`) generate numbers formatted as `PR/<year>/<five digits>` [^r12]. The record holds `pr_type` (set to `STD`), `cc_cd`, `need_dt`, `whs_cd`, `remarks`, `est_value` (calculated as quantity × estimated rate × 1.20), `raised_by`, `raised_on`, and `approved_by` [^r12].

Purchase orders (`po_*`), handled through [[services-pur-po|PUR po services]], format `po_no` as `PO/<year>/<five digits>` and set `po_type` to `STD` or `DIR` [^r13]. Order records maintain `pr_no`, `sup_cd`, `tax_cd`, `pt_cd`, `cc_cd`, `need_dt`, `whs_cd`, `basic_value`, `tax_value`, `gross_value` (where gross = basic + tax), `created_by`, `created_on`, `approved_by`, `approved_on`, and `released_on` [^r13]. Additional order attributes include:
* `client_ref`: free-text field utilized for external integration lookups [^r14].
* `warn_cd`: stores operational warnings, such as [[w-cc-114|W-CC-114]] when saving a Draft order linked to a closed cost centre [^r14].
* `fetch_tok`: a token issued by `po_fetch` and required once by `po_save` for a single supplier and item [^r14].

## Lookups and cost accounting

Tax structures referenced by `tax_cd` include domestic VAT at 20% (`VAT20-UK`), reverse-charge foreign VAT at 20% (`VAT20-RC`), and 5% reduced rates (`VAT5-UK` and `VAT5-RC`), detailed further in [[data-tax-codes|Tax codes]] [^r15]. Payment terms codes under `pt_cd` include `N30`, `N45`, and `N60` representing net 30, 45, or 60 days from invoice, alongside `ADV` for advance terms, as documented in [[data-payment-terms|Payment terms]] [^r16].

Cost centre and budget tracking entities record `cc_cd`, `name`, `status` (`OPEN` or `CLOSED`), `closed_on`, `owner`, the period budget `amount`, and `committed` gross value across approved and pending orders [^r17]. Services such as `bud_check` in [[services-pur-bud|PUR bud services]] compute the remaining `available` balance using the formula `available = amount − committed` [^r17].

## See also

* [[data-payment-terms|Payment terms]]
* [[data-tax-codes|Tax codes]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[services-pur-bud|PUR bud services]]
* [[services-pur-po|PUR po services]]
* [[w-cc-114|W-CC-114]]

## References

[^r1]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §1. About the data dictionary
[^r2]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §1. About the data dictionary
[^r3]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §2. Common codes
[^r4]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §2. Common codes
[^r5]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §2. Common codes
[^r6]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §2. Common codes
[^r7]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §2. Common codes
[^r8]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §3. Item master (itm_*)
[^r9]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 1, §4. Supplier master (sup_*)
[^r10]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §4. Supplier master (sup_*)
[^r11]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §4. Supplier master (sup_*)
[^r12]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §5. Purchase request (pr_*)
[^r13]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §6. Purchase order (po_*)
[^r14]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §6. Purchase order (po_*)
[^r15]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §7. Tax codes
[^r16]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §8. Payment terms
[^r17]: 07_data_dictionary/MAN-DD-72 Data Dictionary Purchasing v7.2.3.pdf, p. 2, §9. Cost centres and budgets
