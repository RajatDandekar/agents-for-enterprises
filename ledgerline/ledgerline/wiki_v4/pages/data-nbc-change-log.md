---
title: "NBC_customisations_and_patch_log"
type: "data-source"
slug: "data-nbc-change-log"
summary: "Register of nine IT change and patch records tracking Northbridge's Ledgerline ERP customisations and configuration parameters from 2015 to 2026."
audience: "staff"
status: "current"
sources: ["README.md", "08_release_notes/NBC_customisations_and_patch_log.xlsx", "11_training/intranet_export_2016/page_purchasing_team_news__spring_2016.html", "99_scans/1998_Ledgerline_licence_signature_page.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | NBC_customisations_and_patch_log.xlsx |
| File location | 08_release_notes/NBC_customisations_and_patch_log.xlsx |
| Sheet name | Log |
| Total records | 9 |
| Key column | Change ID |
| Status | current |

The NBC customisations and patch log is Northbridge Cycles' IT register tracking configuration parameters, migrations, and patch installations for the [[rn-7-2-3-p5|Ledgerline ERP]] system, which has been in operation since 1998 [^r1][^r4][^r14]. As of 26 October 2026, the workbook documents nine administrative changes, confirming that patch [[rn-7-2-3-p5|7.2.3-P5]] is applied and that the director purchasing limit parameter `PUR.DIR_LIMIT` stands at 50000 [^r2][^r4][^r7][^r12]. It also verifies that automated certificate checking (`PUR.CERT_CHK`) remains disabled with value `N` pending review [^r10][^r11].

## What it holds

The workbook records discrete system modifications, configuration parameter adjustments, database migration events, and vendor patch applications implemented across Ledgerline ERP [^r4]. Logged events include historic migrations of 6.x suppliers under creator code `MIGRATION` [^r6], security baseline adjustments for password lengths and session timeouts [^r8][^r9], director purchasing authorisation caps [^r5][^r7], and the maintenance history of patches [[rn-7-2-3-p2|7.2.3-P2]], [[rn-7-2-3-p4|7.2.3-P4]], and [[rn-7-2-3-p5|7.2.3-P5]] [^r9][^r10][^r12].

## Columns

The workbook contains five columns across its single sheet `Log` [^r4]:
* `Change ID`: unique identifier code for the IT change record (for example, `NBC-2025-002`) [^r4][^r7].
* `Date`: implementation date or scheduled date of the change [^r4][^r5][^r13].
* `Logged By`: IT staff member responsible for registering or implementing the change [^r4][^r5][^r6].
* `Description / Action`: technical detail of the patch, migration, or parameter adjustment applied [^r4][^r6][^r9].
* `Reference / Authority`: governance authority, such as a company policy, change advisory board record, or policy amendment [^r4][^r8][^r11][^r13].

## How to look up a row

Lookups are performed in the sheet `Log` using the `Change ID` column as the primary key [^r4]. To review parameter histories or patch implementations, filter by `Change ID` (such as `NBC-2026-024` for patch [[rn-7-2-3-p5|7.2.3-P5]] applied by [[user-jfletcher|Joanna Fletcher]]) or cross-reference the governing authority cited in the record [^r4][^r8][^r12].

## Size

The workbook contains 1 sheet named `Log`, holding 9 change records spanning 5 columns from 2015 to 2026 [^r4].

## Versions and conflicts

* **PUR.DIR_LIMIT parameter value**: Today's rule sets `PUR.DIR_LIMIT` to 50000, updated on 1 April 2025 by [[user-jfletcher|Joanna Fletcher]] under change `NBC-2025-002` per [[pol-pur-001|Purchase Policy]] v4.0 [^r7]. Previously, `PUR.DIR_LIMIT` was set to 30000 on 9 March 2015 by [[user-dramsden|Derek Ramsden]] under change `NBC-2015-004` per company policy v3.0 (`superseded`) [^r5]. From the evening of 30 November 2026 under planned change `NBC-2026-026`, [[user-jfletcher|Joanna Fletcher]] is scheduled to lower `PUR.DIR_LIMIT` to 25000 in accordance with [[amd-pur-2026-03|AMD-PUR-2026-03]] (`future_dated`) [^r13].
* **PUR.CERT_CHK parameter status**: On 20 September 2026 under change `NBC-2026-017`, [[user-jfletcher|Joanna Fletcher]] deployed patch [[rn-7-2-3-p4|7.2.3-P4]] and left `PUR.CERT_CHK` set to `N` [^r10]. On 7 October 2026 under `NBC-2026-021`, [[user-rpryce|Rhys Pryce]] recorded CAB `CR-2026-031`, confirming that `PUR.CERT_CHK` is not enabled and is scheduled for review in January 2027 [^r11].

## See also

* [[amd-pur-2026-03|AMD-PUR-2026-03 Amendment 3 to the Purchase Policy]]
* [[pol-its-008|POL-ITS-008 README ACCESS]]
* [[pol-pur-001|POL-PUR-001 Purchase Policy]]
* [[rn-7-2-3-p2|RN-7.2.3-P2 Ledgerline ERP 7.2.3-P2 Patch Notes]]
* [[rn-7-2-3-p4|RN-7.2.3-P4 Ledgerline ERP 7.2.3-P4 Patch Notes]]
* [[rn-7-2-3-p5|RN-7.2.3-P5 Ledgerline ERP 7.2.3-P5 Patch Notes]]
* [[user-dramsden|Derek Ramsden (DRAMSDEN)]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]
* [[user-rpryce|Rhys Pryce (RPRYCE)]]

## References

[^r1]: README.md, northbridge-docs
[^r4]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, SHEET Log
[^r14]: 99_scans/1998_Ledgerline_licence_signature_page.pdf, p. 1, SOFTWARE LICENCE AGREEMENT
[^r2]: README.md, Dates
[^r7]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2025-002, SHEET Log
[^r12]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2026-024, SHEET Log
[^r10]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2026-017, SHEET Log
[^r11]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2026-021, SHEET Log
[^r6]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2019-011, SHEET Log
[^r8]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2025-009, SHEET Log
[^r9]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2026-004, SHEET Log
[^r5]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2015-004, SHEET Log
[^r13]: 08_release_notes/NBC_customisations_and_patch_log.xlsx, sheet Log, row NBC-2026-026, SHEET Log
