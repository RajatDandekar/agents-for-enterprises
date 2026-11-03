---
title: "Decision 2026-10-07: Deferral of PUR.CERT_CHK activation (CR-2026-031)"
type: "decision"
slug: "decision-2026-10-07-cr-2026-031-cert-check"
summary: "CAB deferred activation of parameter PUR.CERT_CHK (CR-2026-031) until January 2027, retaining manual compliance checks under SOP-PUR-001."
audience: "staff"
status: "current"
sources: ["10_meeting_notes/2026-10-07 CAB minutes (CR-2026-031 certificate check).docx", "09_email_archive/2026/2026-10-07_Certificate check in Ledgerline (PUR.CERT_CHK) - stays off for now.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| decision_code | CR-2026-031 |
| date | 2026-10-07 |
| decision_maker | Change Advisory Board |
| scope | Manchester and Leeds |
| parameter | PUR.CERT_CHK |
| status | Deferred (review January 2027) |

On 7 October 2026, the Change Advisory Board evaluated change request CR-2026-031 and decided not to activate Ledgerline parameter `PUR.CERT_CHK` across the Manchester and Leeds sites [^r1]. The activation remains deferred until after the spring launch, with a formal review scheduled for January 2027 [^r1][^r5]. As a result, automated purchase order certificate checks stay disabled, and manual compliance verification under [[sop-pur-001|SOP-PUR-001]] remains in force [^r3][^r7].

| Field | Detail |
|---|---|
| Change request | CR-2026-031 [^r1] |
| Decision date | 2026-10-07 [^r1][^r5] |
| Deciding body | Change Advisory Board [^r1][^r5] |
| Parameter | `PUR.CERT_CHK` [^r1][^r6] |
| Current setting | `N` (Manchester and Leeds) [^r1] |
| Next review | January 2027 [^r1][^r5] |

## Context

Ledgerline patch [[rn-7-2-3-p4|7.2.3-P4]] added an optional certificate warning on the purchase order screen governed by configuration setting `PUR.CERT_CHK` [^r6]. Under change request CR-2026-031, the Change Advisory Board considered activating this check to trigger warning [[w-sup-0207|W-SUP-0207]] [^r1][^r2]. Concurrently under CR-2026-029, the board approved the rollout of Ledgerline patch [[rn-7-2-3-p5|7.2.3-P5]] scheduled for 20 October 2026 [^r4].

## Rationale

The board rejected enabling warning [[w-sup-0207|W-SUP-0207]] because it acts only as an advisory prompt and allows the purchase order to save even when triggered [^r2]. Furthermore, the system logic only evaluates the valid-to date rather than enforcing the 12-month validity and 60-day advance rules mandated by [[amd-sup-2026-02|AMD-SUP-2026-02]] [^r2].

## Operational impact

The parameter `PUR.CERT_CHK` remains set to `N` across both Manchester and Leeds facilities through the spring launch [^r1]. Compliance verification for vendor paperwork and certificate expiration dates continues as a manual check performed by the purchasing team in accordance with [[sop-pur-001|SOP-PUR-001]] [^r3][^r7].

## Versions and conflicts

Today's operational rule enforces manual verification of certificates under [[sop-pur-001|SOP-PUR-001]] while `PUR.CERT_CHK` remains set to `N` [^r1][^r3][^r7]. The automated warning check provided in [[rn-7-2-3-p4|7.2.3-P4]] was proposed under CR-2026-031 on 2026-10-07 but rejected for immediate use and deferred for re-evaluation in January 2027 (`future_dated`) [^r1][^r2][^r5].

## See also

* [[amd-sup-2026-02|AMD-SUP-2026-02 Amendment 2 to the Supplier Policy]]
* [[sop-pur-001|SOP-PUR-001 Supplier Onboarding]]
* [[rn-7-2-3-p4|RN-7.2.3-P4 Ledgerline ERP 7.2.3-P4 Patch Notes]]
* [[rn-7-2-3-p5|RN-7.2.3-P5 Ledgerline ERP 7.2.3-P5 Patch Notes]]
* [[w-sup-0207|W-SUP-0207 UN38.3 CERTIFICATE MISSING OR EXPIRED]]

## References

[^r1]: 10_meeting_notes/2026-10-07 CAB minutes (CR-2026-031 certificate check).docx, CR-2026-031 Enable PUR.CERT_CHK (patch 7.2.3-P4)
[^r5]: 09_email_archive/2026/2026-10-07_Certificate check in Ledgerline (PUR.CERT_CHK) - stays off for now.eml, body
[^r3]: 10_meeting_notes/2026-10-07 CAB minutes (CR-2026-031 certificate check).docx, Discussion
[^r7]: 09_email_archive/2026/2026-10-07_Certificate check in Ledgerline (PUR.CERT_CHK) - stays off for now.eml, body
[^r6]: 09_email_archive/2026/2026-10-07_Certificate check in Ledgerline (PUR.CERT_CHK) - stays off for now.eml, body
[^r2]: 10_meeting_notes/2026-10-07 CAB minutes (CR-2026-031 certificate check).docx, CR-2026-031 Enable PUR.CERT_CHK (patch 7.2.3-P4)
[^r4]: 10_meeting_notes/2026-10-07 CAB minutes (CR-2026-031 certificate check).docx, CR-2026-029 Install 7.2.3-P5
