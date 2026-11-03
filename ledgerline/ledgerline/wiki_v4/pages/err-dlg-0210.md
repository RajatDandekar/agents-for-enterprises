---
title: "ERR-DLG-0210 Delegate role lower than delegator"
type: "error"
slug: "err-dlg-0210"
summary: "Error raised on SYS-DLG-03 when delegating approval authority to a user holding a lower role rank in the security hierarchy."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf", "08_release_notes/RN-7.1 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-DLG-0210 |
| message | Delegate role lower than delegator |
| screen | SYS-DLG-03 |
| module | Administration |
| status | current |

Error ERR-DLG-0210 is raised in Ledgerline when an employee attempts to assign approval authority to a substitute whose role ranks lower in the security hierarchy than the delegator's role [^r1][^r2]. First introduced in [[rn-7-1|RN-7.1]], this validation ensures approval authority cannot be passed down to lower-ranking personnel [^r2]. The error prevents the delegation record from being saved to the database until the role mismatch is corrected [^r3].

| Field | Value |
|---|---|
| Error code | ERR-DLG-0210 |
| Description | Delegate role lower than delegator |
| Screen | [[screen-sys-dlg-03|SYS-DLG-03]] |
| Raised by | Delegation validation service |

## Meaning
ERR-DLG-0210 indicates that the designated substitute does not hold an equal or higher role rank in the operational standing or security hierarchy relative to the delegator [^r1][^r2]. 

## Cause
The error occurs on screen [[screen-sys-dlg-03|SYS-DLG-03]] during delegation entry when a user selects a delegate whose assigned security role is lower than their own [^r1][^r2].

## How to fix
To resolve the error, select a substitute who occupies an equal or higher post in the security hierarchy, or resolve the role rank mismatch before committing the delegation record to the database [^r1][^r3].

## Raised by
The error is raised on screen [[screen-sys-dlg-03|SYS-DLG-03]] by the approval delegation entry validation [^r1][^r2].

## See also
* [[screen-sys-dlg-03|SYS-DLG-03 Approval Delegation Entry]]
* [[man-adm-72|MAN-ADM-72 Ledgerline ERP 7.2 System Administration]]
* [[rn-7-1|RN-7.1 Ledgerline ERP 7.1 Release Notes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-ADM-72 Ledgerline 7.2 System Administration Guide v7.2.3.pdf, p. 4, §3. Approval delegation
[^r2]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 2, Administration: Approval delegation (SYS-DLG-03)
[^r3]: 08_release_notes/RN-7.1 Ledgerline Release Notes.pdf, p. 2, Administration: Approval delegation (SYS-DLG-03)
