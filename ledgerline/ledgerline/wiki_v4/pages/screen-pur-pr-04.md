---
title: "PUR-PR-04 Purchase Request Approval"
type: "screen"
slug: "screen-pur-pr-04"
summary: "Ledgerline screen used by authorized roles to approve or reject pending purchase requests via the pr_approve service."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/purchase/pr_approve.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | PUR-PR-04 |
| Screen title | Purchase Request Approval |
| Menu path | Purchase > Request approval |
| Authorized roles | PUR-SR, PUR-MGR, PLANT-HEAD, SYS-ADMIN |
| Primary service | pr_approve |
| Status | current |

PUR-PR-04 Purchase Request Approval is the Ledgerline ERP screen used by designated purchasing and management roles to review, approve, or reject pending purchase requests [^r1][^r3]. Approval advances the request to status AP, while rejection sets the status to RJ and disallows resubmission [^r1][^r2]. The screen executes the backend service `pr_approve` to record authorization decisions and enforce role limits [^r1][^r4].

| Field / Attribute | Value |
|---|---|
| Screen code | PUR-PR-04 [^r3] |
| Screen title | PURCHASE REQUEST APPROVAL [^r3] |
| Menu location | Purchase > Request approval [^r3] |
| Roles | PUR-SR, PUR-MGR, PLANT-HEAD, SYS-ADMIN [^r3] |
| Service | POST /ll72/svc/pr_approve [^r4] |

## Fields

Screen PUR-PR-04 captures the required fields `pr_no` and `decision` (`A` for approve, `R` for reject), alongside an optional `comment` [^r5]. Approvers reviewing pending requests can set the status to AP upon approval [^r1]. When rejecting a request, entering a reason is required, which sets the purchase request status to RJ and notifies the raiser by email [^r2].

## Keys and services

The screen submits requests through the write service `pr_approve` using `POST /ll72/svc/pr_approve` to process purchase request approvals and rejections [^r4][^r5].

## Messages

* [[err-apr-0003|ERR-APR-0003]]: Raised when an approver attempts to approve their own request [^r1].
* [[err-apr-0004|ERR-APR-0004]]: Raised when an approver attempts to approve a request that exceeds their approval limit [^r1].

## See also

* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[services-pur-pr|PUR pr services]]
* [[err-apr-0003|ERR-APR-0003 Self-approval not permitted]]
* [[err-apr-0004|ERR-APR-0004 Advance amount exceeds PO unbilled commitment]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §10.2 Approving
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 29, PUR-PR-04 PURCHASE REQUEST APPROVAL
[^r2]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 7, §10.3 Rejecting
[^r4]: 04_service_definitions/purchase/pr_approve.yaml, whole file
[^r5]: 04_service_definitions/purchase/pr_approve.yaml, request.fields
