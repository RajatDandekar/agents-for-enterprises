---
title: "SOP-PUR-005 Certificate Renewal (UN 38.3)"
type: "procedure"
slug: "sop-pur-005"
summary: "Procedure for monitoring, requesting, and logging renewed UN 38.3 lithium battery transport test summaries in Ledgerline to maintain purchasing and transport compliance."
audience: "staff"
status: "current"
sources: ["01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf", "02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf", "08_release_notes/RN-7.2.1 Ledgerline Release Notes.pdf", "11_training/QRC-05 Uploading a supplier certificate.pdf", "09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml", "09_email_archive/2026/2026-09-29_UN 38.3 report renewal.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | SOP-PUR-005 |
| Title | Certificate Renewal (UN 38.3) |
| Version | 1.1 |
| Effective | 2026-09-01 |
| Status | current |
| Owner | Purchasing |
| Author | Luis Moreno (LMORENO) |
| Approver | Daniel Okafor (DOKAFOR) |

SOP-PUR-005 defines the process for monitoring and renewing UN 38.3 transport test summaries for lithium-ion battery packs across Northbridge Cycles [^r3][^r5][^r8]. Without an active, compliant certificate, battery packs cannot legally be moved by freight carriers, stored at Manchester works, or transferred to the Leeds unit [^r5]. Purchasing must proactively track expiring certificates to ensure replacement documents are fully verified and entered into Ledgerline ERP before mandatory purchase order cut-offs take effect [^r2][^r9][^r13].

## Purpose and scope

This procedure applies to all direct purchase orders, scheduled deliveries, and warranty stock replacements for lithium-ion battery packs ([[items-bat|BAT-* items]]) assembled at the Manchester plant and held at Leeds [^r8]. Transportation regulations require a valid UN 38.3 transport test summary rather than the full factory test report [^r6]. The summary must contain mandatory regulatory fields, including specific test laboratory details and the manufacturer's authorised signature [^r6]. Any internal design change, such as supplier modifications to battery management firmware or casing seals, invalidates previous UN 38.3 documentation and requires fresh certification [^r7].

## Responsibilities

Purchasing holds primary responsibility for tracking certificate expiration, contacting vendors, and enforcing purchasing halts under [[amd-sup-2026-02|AMD-SUP-2026-02]] [^r1][^r2][^r9]. Quality Assurance reviews technical details—cross-checking model designations, cell combinations, and electrical ratings against engineering drawings—and records formal technical sign-off in Ledgerline [^r9]. Goods Inwards at Manchester and Leeds checks shipping documentation against the ERP system on delivery, placing consignments into quarantine immediately if an active certificate is missing or lapsed [^r10].

## Steps

### 1. Monthly review (90-day window)
On the first working day of each month, the senior buyer ([[user-lmoreno|Luis Moreno]]) runs the certificate-expiry report (job JOB-PUR-022, as detailed in [[man-pur-72|MAN-PUR-72]] §22.6) using a 90-day forward window [^r1][^r3][^r11].

### 2. First notification (90 days before expiry)
For every UN 38.3 certificate expiring within 90 days, Purchasing sends letter template NBC-L-07 to the supplier requesting a newly issued test report [^r1][^r12]. When issuing purchase orders for lithium-cell components, buyers must verify that test summaries were issued within the preceding 12 months and maintain validity for at least 60 days past the order placement date [^r2][^r23].

### 3. Second reminder and order halt (60 days before expiry)
If no replacement report has been provided 60 days prior to expiry, Purchasing issues a second reminder and escalates the issue to the purchase manager ([[user-dokafor|Daniel Okafor]]) [^r3][^r13]. Under [[amd-sup-2026-02|AMD-SUP-2026-02]], no new purchase orders may be placed once fewer than 60 days remain on certificate validity [^r2][^r13]. (For example, [[sup-nc-gda-0063|Nordic Cell Co.]] notified Senior Buyer Luis Moreno on 29 September 2026 of a replacement report delay extending to late November 2026 [^r24].)

### 4. Certificate expiry and stop notification
On the exact date of certificate expiry, Purchasing broadcasts an e-mail to all buyers with the subject `CERT EXPIRED - DO NOT ORDER` specifying the supplier's name and account code [^r14]. Although Ledgerline 7.2.1 and later visually flags expired certificates in red text on the certificate tab, this visual alert does not automatically place vendor accounts on hold or prevent users from raising orders, leaving enforcement to purchasing staff [^r18][^r19].

### 5. Ledgerline entry and verification
Staff upload the renewed document following [[qrc-05|QRC-05]]:
1. Open the Supplier master screen and select the Certificates tab [^r20].
2. Insert a new row and enter the certificate type precisely as `UN38.3` to ensure automated order validation functions correctly [^r15][^r20][^r22]. Never overwrite an existing certificate row; historical compliance rows must remain intact [^r15].
3. Enter the document reference number and the valid-to date, attach the scanned report, and press `F8` until `CERT SAVED` appears [^r20].
4. Complete form NBC-F-113, submit it to the senior buyer for verification and initialling, and file the completed form in the purchasing office compliance binder before releasing pending purchase orders [^r21].

### 6. Correcting overwritten historical entries
If a user accidentally overwrites an existing certificate record rather than creating a new row, the systems supervisor must inspect the database table logs to reconstruct the separated historical validity periods before any new document is committed [^r16].

### 7. Filing and archiving
Hard copies of current transport test summaries must be filed in the dangerous goods binders inside the dispatch offices at both Manchester and Leeds [^r17]. Obsolete certificates must be marked as superseded and relocated to the archive directory [^r17].

## Forms and screens

* **Ledgerline Supplier Master (Certificates tab)**: Screen used to record validity dates, attach scans, and maintain certificate compliance [^r20].
* **JOB-PUR-022**: Monthly batch report job used to scan for certificates expiring within 90 days [^r11].
* **NBC-L-07**: Standard supplier letter template requesting renewed UN 38.3 test summaries [^r12].
* **NBC-F-113**: Certificate verification sign-off sheet initialled by the senior buyer prior to releasing orders [^r21].

## See also

* [[amd-sup-2026-02|AMD-SUP-2026-02 Amendment 2 to the Supplier Policy]]
* [[items-bat|BAT-* items]]
* [[man-pur-72|MAN-PUR-72 Ledgerline ERP 7.2 User Manual, Purchasing]]
* [[qrc-05|QRC-05 Uploading a supplier certificate]]
* [[rn-7-2-1|RN-7.2.1 Ledgerline ERP 7.2.1 Release Notes]]
* [[sup-nc-gda-0063|Nordic Cell Co. (NC-GDA-0063)]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[user-dokafor|Daniel Okafor (DOKAFOR)]]
* [[user-lmoreno|Luis Moreno (LMORENO)]]

## References

[^r3]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 1, Certificate Renewal (UN 38.3)
[^r5]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 1, §1. Purpose
[^r8]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 2, §2. Scope
[^r2]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §3. What purchase staff must do
[^r9]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 2, §3. Responsibilities
[^r13]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 3, §5. Procedure
[^r6]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 1, Common errors
[^r7]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 1, Common errors
[^r1]: 01_policies/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf, p. 1, §3. What purchase staff must do
[^r10]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 2, §3. Responsibilities
[^r11]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 3, §5. Procedure
[^r12]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 3, §5. Procedure
[^r23]: 09_email_archive/2026/2026-07-28_Failed battery lot - incoming abuse test.eml, body
[^r24]: 09_email_archive/2026/2026-09-29_UN 38.3 report renewal.eml, body
[^r14]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 3, §5. Procedure
[^r18]: 08_release_notes/RN-7.2.1 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r19]: 08_release_notes/RN-7.2.1 Ledgerline Release Notes.pdf, p. 2, Upgrade Notes for Key Users
[^r20]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Steps
[^r15]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 3, §5. Procedure
[^r22]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Entering certificate details
[^r21]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Verification and sign-off
[^r16]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 4, What to do when something does not look right
[^r17]: 02_procedures/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf, p. 4, §6. Records
