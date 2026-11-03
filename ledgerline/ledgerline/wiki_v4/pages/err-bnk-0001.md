---
title: "ERR-BNK-0001 Missing mandatory banking fields"
type: "error"
slug: "err-bnk-0001"
summary: "Ledgerline error ERR-BNK-0001 covering missing mandatory banking fields on save and bank details not found during retrieval or blocking."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "04_service_definitions/accounts_payable/bnk_block.xml", "04_service_definitions/accounts_payable/bnk_get.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-BNK-0001 |
| Module | Accounts Payable |
| Appears on | AP-BNK-06 |
| Raised by services | bnk_save, bnk_block, bnk_get |
| Status | current |

Error ERR-BNK-0001 is an Accounts Payable error raised in Ledgerline ERP during supplier bank detail operations [^r1][^r2][^r3]. According to the user manual, it halts saving when essential settlement routing fields are omitted on [[screen-ap-bnk-06|AP-BNK-06]] [^r1]. In backend service definitions, the same code reports that supplier bank records cannot be located [^r2][^r3].

## Meaning
In [[man-ap-72|MAN-AP-72]], ERR-BNK-0001 denotes missing mandatory banking settlement fields when submitting bank information [^r1]. In backend XML definitions, the error code generates the message text `SUPPLIER BANK DETAILS NOT FOUND` [^r2][^r3].

## Cause
When triggered on [[screen-ap-bnk-06|AP-BNK-06]], the error is caused by attempting to execute `bnk_save` without providing `SORT CD` and `ACCT NO` for domestic records, or `IBAN` for international records [^r1]. When raised by backend retrieval or status-change calls, it is caused by the system being unable to find existing bank details for the specified supplier [^r2][^r3].

## How to fix
Populate all required settlement fields on [[screen-ap-bnk-06|AP-BNK-06]] before saving, ensuring `SORT CD` and `ACCT NO` are entered for domestic accounts or `IBAN` is entered for international accounts [^r1]. If encountering the code during lookup or block requests, verify that valid bank details have already been created and registered for the supplier record [^r2][^r3].

## Raised by
The error is raised by the following Accounts Payable [[services-ap-bnk|AP bnk services]]:
* `bnk_save` triggered from [[screen-ap-bnk-06|AP-BNK-06]] [^r1]
* `bnk_block` [^r2]
* `bnk_get` [^r3]

## Versions and conflicts
* **Contradiction between manual and service definitions**: In backend service definitions `bnk_block.xml` and `bnk_get.xml`, error ERR-BNK-0001 outputs `SUPPLIER BANK DETAILS NOT FOUND` [^r2][^r3]. Conversely, [[man-ap-72|MAN-AP-72]] (v7.2.3, p. 24) documents ERR-BNK-0001 as a validation failure during `bnk_save` on [[screen-ap-bnk-06|AP-BNK-06]] when mandatory settlement fields (`SORT CD` and `ACCT NO` for domestic, or `IBAN` for international) are missing [^r1].

## See also
* [[errors-bnk|Errors BNK]]
* [[screen-ap-bnk-06|AP-BNK-06 Supplier Bank Details Entry]]
* [[services-ap-bnk|AP bnk services]]
* [[sop-ap-004|SOP-AP-004 Supplier Bank Detail Changes]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Messages
[^r2]: 04_service_definitions/accounts_payable/bnk_block.xml, ll:errors
[^r3]: 04_service_definitions/accounts_payable/bnk_get.xml, ll:errors
