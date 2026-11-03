---
title: "MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing"
type: "manual"
slug: "man-pur-72"
summary: "User manual for Ledgerline ERP 7.2 Purchasing, covering system conventions, order processing, release, amendments, and administration settings."
audience: "staff"
status: "mixed"
sources: ["01_policies/AMD-PUR-2026-03_Amendment3_PurchasePolicy_DIRlimit.pdf", "01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf", "03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | MAN-PUR-72 |
| title | Ledgerline ERP 7.2 User Manual, Purchasing |
| version | 7.2.3 |
| issued | 2025-01-15 |
| owner | Ledgerline Systems Documentation Group |
| status | current |

MAN-PUR-72 is the official vendor reference manual for Ledgerline ERP 7.2 Purchasing issued by the Ledgerline Systems Documentation Group [^r2]. It governs interface conventions, order processing rules, approval routing, document statuses, and batch reporting routines [^r2][^r3][^r1]. As of 26 October 2026, version 7.2.3 defines the active operational requirements across all purchasing screens [^r2][^r3].

| Field | Value |
|---|---|
| Document Code | MAN-PUR-72 [^r2] |
| Version | 7.2.3 [^r2] |
| Issue Date | 2025-01-15 [^r2] |
| Document Group | Ledgerline Systems Documentation Group [^r2] |
| Status | Current [^r2] |

## System conventions and access

Dates are entered on client forms using DD-MM-YYYY format and returned by services as YYYY-MM-DD [^r4]. Standard navigation keys across screens include F2 for field lookup, F3 for fetch defaults, F5 for refresh, F7 for clear, F8 for save, F9 for submit or release, and F10 for the menu bar [^r7]. User sessions automatically terminate after 20 minutes of inactivity, causing unsaved screen data to be lost [^r6]. 

User passwords require a minimum of eight characters including at least one digit, and expire every 90 days [^r8]. Entering three incorrect password attempts triggers ERR-SEC-0002 and locks the user ID for 30 minutes unless unlocked earlier by IT [^r5][^r24]. 

## Purchase order entry and validation

On the purchase order screen [[screen-pur-po-01|PUR-PO-01]], pressing Fetch populates rates from an active rate contract valid for the current day, or falls back to displaying the last order rate highlighted in yellow if no active contract exists [^r3][^r10]. Saving an order with F8 validates the supplier, item, quantity, need-by date, tax code, source request, cost centre, and budget, showing '<PO number> SAVED' on the status bar regardless of the resulting status [^r11]. Version 7.2.3 added the Fetch requirement, the cost-centre warning W-CC-114, and the error catalogue to the manual [^r3].

Orders can only be created for ACTIVE suppliers; attempting to save against a blocked supplier triggers [[err-sup-0031|ERR-SUP-0031]], though supplier certificates are not validated during order entry [^r15]. Orders cannot be saved for an item or quantity exceeding the source request, which raises an error and upon successful save closes (CL) the request [^r14]. If the assigned cost centre is closed at the time of saving, the order saves as Draft (DR) with warning W-CC-114 and remains unsent [^r12]. Unreleased orders printed with Ctrl+P show a DRAFT watermark, and clean printing requires the order to be Released [^r9].

## Order statuses and workflow

An order transitions to Approved (AP) upon saving if the gross value falls within the creator's limit or matches a request whose approver limit covers the total; otherwise, it enters Pending Approval (PA) and routes to the approver's inbox [^r13]. Rejecting an order on [[screen-pur-poa-04|PUR-POA-04]] requires a mandatory reason, assigns status RJ, and releases the committed budget [^r16]. Releasing an order on [[screen-pur-por-05|PUR-POR-05]] changes its status to RL, records the release date, increments stock on order, and transmits the order via e-mail to the supplier's order address [^r17]. Releasing an order that is not in AP status generates an error [^r18].

Only orders in status RL have been transmitted to the supplier, whereas documents in DR, PA, or AP have not reached the supplier [^r22]. System e-mails are sent automatically to approvers for pending actions, to raisers upon request rejection, and to suppliers upon order release, but no e-mail notification is dispatched when an order saves as Draft [^r23].

## Amendments and cancellations

Order modifications are performed on [[screen-pur-pom-06|PUR-POM-06]] [^r19]. If an amended gross value exceeds the ceiling covered by the original approval, the order reverts to status PA even if it was previously released [^r19]. Cancelling an order sets its status to CN and frees the committed budget as well as stock on order if previously released, but Ledgerline does not send cancellation notices to suppliers [^r20]. Orders in status CN, RJ, or CL cannot be amended, raising [[err-po-0801|ERR-PO-0801]] [^r21].

Documents migrated from Ledgerline 6.x exist exclusively in status RL or CL and retain their historical rates and tax codes without recalculation [^r26].

## Administration and reports

Approval limits in Ledgerline are configured on individual user records rather than roles [^r25]. Updates to the configurable direct-order limit setting take effect at each user's subsequent sign-in [^r25].

Under §22.6, the certificate-expiry report is executed by the senior buyer on the first working day of each month using a 90-day window to identify expiring [[topic-un-38-3-certificates|UN 38.3 certificates]] [^r1].

## Versions and conflicts

Today's rule: The direct-order limit setting in Ledgerline is configurable under §23.4 and currently set to £50,000 [^r25][^r27].
Future rule: From 2026-12-01, IT will reduce the direct-order limit setting from £50,000 to £25,000 on the evening of 2026-11-30 in accordance with [[amd-pur-2026-03|AMD-PUR-2026-03]] §3 [^r27].
Sources: MAN-PUR-72 v7.2.3 (2025-01-15), p. 14, §23.1; AMD-PUR-2026-03 v1.0 (effective 2026-12-01), p. 1, §3 [^r25][^r27].
Kind: future_dated.

## See also

* [[amd-pur-2026-03|AMD-PUR-2026-03 Amendment 3 to the Purchase Policy]]
* [[amd-sup-2026-02|AMD-SUP-2026-02 Amendment 2 to the Supplier Policy]]
* [[err-po-0801|ERR-PO-0801 Order in CN, RJ or CL status cannot be amended]]
* [[err-sup-0031|ERR-SUP-0031 Supplier is blocked]]
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[screen-pur-poa-04|PUR-POA-04 Purchase Order Approval]]
* [[screen-pur-pom-06|PUR-POM-06 Purchase Order Amendment]]
* [[screen-pur-por-05|PUR-POR-05 Purchase Order Release]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]

## References

[^r2]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 1, Field
[^r3]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 2, §1.5 Version history of this manual
[^r1]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §3. What purchase staff must do
[^r4]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 2, §1.3 Conventions
[^r7]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 3, §2.5 Function keys
[^r6]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 3, §2.4 Session timeout
[^r8]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 3, §2.6 Changing your password
[^r5]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 2, §2.1 Signing in
[^r24]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 12, §17.27 ERR-SEC-0002 Invalid credentials
[^r10]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 5, §7.2 Which rate Ledgerline uses
[^r11]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §11.8 Saving the order
[^r15]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §11.11 Supplier status
[^r14]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §11.10 Quantity against the request
[^r12]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §11.9 The status after saving
[^r9]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 3, §2.7 Printing
[^r13]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §11.9 The status after saving
[^r16]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §12.3 Rejecting an order
[^r17]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 8, §13.2 Releasing
[^r18]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §13.3 When release fails
[^r22]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 10, §16.2 Which status means the supplier has the order
[^r23]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 12, §18.1 E-mails Ledgerline sends
[^r19]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §14.3 Approval after amendment
[^r20]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §14.5 Cancelling
[^r21]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 9, §14.6 Closed orders
[^r26]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 15, §24.2 Migrated documents
[^r25]: 03_ledgerline_manuals/MAN-PUR-72 Ledgerline 7.2 User Manual - Purchasing v7.2.3.pdf, p. 14, §23.1 Users and roles
[^r27]: 01_policies/AMD-PUR-2026-03_Amendment3_PurchasePolicy_DIRlimit.pdf, p. 1, §3. What changes in Ledgerline
