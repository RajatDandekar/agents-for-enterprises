---
title: "Users_and_approval_limits"
type: "data-source"
slug: "data-users-and-approval-limits"
summary: "Register of 104 Ledgerline user profiles, operating units, gross VAT approval limits, and role limit matrix."
audience: "staff"
status: "current"
sources: ["05_master_data/Users_and_approval_limits.xlsx", "08_release_notes/RN-7.0 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| File | 05_master_data/Users_and_approval_limits.xlsx |
| Owner | Finance / Ledgerline Administration |
| Format | XLSX |
| Sheets | Users, Matrix |
| Key column | user_id |
| Total user records | 104 |
| Status | current |

The `Users_and_approval_limits.xlsx` workbook is the master extract containing 104 user accounts and financial authorization thresholds across Northbridge Cycles' operating units [^r1][^r3]. It pairs user account attributes exported from [[screen-sys-usr-01|SYS-USR-01]] with individual financial approval limits in gross GBP [^r1][^r2]. Because Ledgerline evaluates authorization limits directly at the user profile level, this workbook establishes the actual operational approval authority for requisitions, orders, and invoices [^r10][^r11].

## What it holds

The workbook holds the active user registry and approval limits used by Ledgerline's central authorization service [^r1][^r11]. It consists of two sheets: `Users`, which details individual employee user accounts, cost centre assignments, and personal limits, and `Matrix`, which documents baseline gross approval tiers assigned by role code [^r1][^r2][^r4].

## Columns

The `Users` sheet contains 10 columns [^r2]:
* `user_id`: Unique Ledgerline login identifier [^r2].
* `name`: Full name of the user [^r2].
* `title`: Job title [^r2].
* `role_cd`: Assigned system role code [^r2].
* `ou_cd`: Operating unit code (`NBC-LDS-01` or `NBC-MAN-01`) [^r2][^r3].
* `appr_limit`: Individual gross approval limit in GBP including VAT [^r2].
* `manager_id`: User ID of the direct approving manager [^r2].
* `default_cc`: Default cost centre code [^r2].
* `email`: User email address [^r2].
* `status`: Account status [^r2].

The `Matrix` sheet specifies baseline gross GBP limits across five functional roles [^r4]:
* [[role-pur-exec|PUR-EXEC]]: £250,000 gross [^r5].
* [[role-pur-sr|PUR-SR]]: £500,000 gross [^r6].
* [[role-pur-mgr|PUR-MGR]]: £1,000,000 gross [^r7].
* [[role-plant-head|PLANT-HEAD]]: £5,000,000 gross [^r8].
* [[role-stores|STORES]]: £0 gross [^r9].

## How to look up a row

Look up individual accounts on the `Users` sheet by the unique `user_id` key [^r2][^r3]. Reference values for functional roles can be checked on the `Matrix` sheet by role code [^r4].

## Size

The workbook contains two sheets [^r1][^r4]. The `Users` sheet has 104 user rows across two operating units, covering six distinct approval limit tiers ranging from 0 to 1,000,000,000,000 GBP [^r1][^r3]. The `Matrix` sheet defines limits across five role codes [^r4].

## Versions and conflicts

Today's rule: In [[rn-7-0|Ledgerline 7.0]], the central authorisation service evaluates the gross financial approval limit stored directly on the individual user profile maintenance form whenever a purchase requisition, works order, or supplier invoice requires approval [^r10][^r11].
Other rule: The `Matrix` sheet lists default approval limits by functional role code (`PUR-EXEC` at £250,000, `PUR-SR` at £500,000, `PUR-MGR` at £1,000,000, `PLANT-HEAD` at £5,000,000, and `STORES` at £0), but the system ignores legacy values on functional roles in favour of the user profile limit [^r4][^r5][^r6][^r7][^r8][^r9][^r10][^r11].
Sources and dates: `RN-7.0` (2015-03-02) and `Users_and_approval_limits.xlsx` (current) [^r4][^r10][^r11].
Kind: `contradiction`.

## See also

* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[rn-7-0|RN-7.0 Ledgerline ERP 7.0 Release Notes]]
* [[role-pur-exec|Role PUR-EXEC]]
* [[role-pur-sr|Role PUR-SR]]
* [[role-pur-mgr|Role PUR-MGR]]
* [[role-plant-head|Role PLANT-HEAD]]
* [[role-stores|Role STORES]]
* [[pol-apr-002|POL-APR-002 Approval Matrix for Purchasing]]

## References

[^r1]: 05_master_data/Users_and_approval_limits.xlsx, sheet Users, SHEET Users
[^r3]: 05_master_data/Users_and_approval_limits.xlsx, sheet Users, SHEET Users
[^r2]: 05_master_data/Users_and_approval_limits.xlsx, sheet Users, SHEET Users
[^r10]: 08_release_notes/RN-7.0 Ledgerline Release Notes.pdf, p. 3, §3. Details
[^r11]: 08_release_notes/RN-7.0 Ledgerline Release Notes.pdf, p. 3, §3. Details
[^r4]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, SHEET Matrix
[^r5]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row PUR-EXEC, SHEET Matrix
[^r6]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row PUR-SR, SHEET Matrix
[^r7]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row PUR-MGR, SHEET Matrix
[^r8]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row PLANT-HEAD, SHEET Matrix
[^r9]: 05_master_data/Users_and_approval_limits.xlsx, sheet Matrix, row STORES, SHEET Matrix
