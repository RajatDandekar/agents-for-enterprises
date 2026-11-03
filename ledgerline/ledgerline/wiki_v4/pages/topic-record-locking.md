---
title: "Ledgerline Record Locking and Hanging Tasks"
type: "topic"
slug: "topic-record-locking"
summary: "Overview of Ledgerline temporary record locking, hanging background tasks caused by network drops, and clearance procedures."
audience: "staff"
status: "current"
sources: ["09_email_archive/2021/2021-01-17_Approval stuck in the inbox.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

Ledgerline applies temporary record locks during active document updates to protect data consistency across sites. When network interruptions disrupt background posting routines, these temporary locks can persist and mark documents as actively edited even after user logout [^r1]. This state leaves workflow actions inaccessible to approvers until cleared [^r2].

## Mechanism and Symptoms

When a network connection drops during an update between Manchester and Leeds, Ledgerline's background posting routine can fail to clear a temporary lock [^r1]. This failure leaves the affected document marked as being edited even after the user logs out of the session [^r1].

When a requisition record remains locked in an approver's inbox, sign-off and return options appear greyed out on the screen [^r2].

## Resolution and Clearance

Resolving a greyed-out requisition trapped in an approver's inbox requires either a session restart or server-side clearance by a systems administrator [^r2].

## See also

* [[user-dokafor|Daniel Okafor]]
* [[user-kmensah|Kwame Mensah]]

## References

[^r1]: 09_email_archive/2021/2021-01-17_Approval stuck in the inbox.eml, body
[^r2]: 09_email_archive/2021/2021-01-17_Approval stuck in the inbox.eml, body
