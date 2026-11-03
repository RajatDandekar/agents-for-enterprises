---
title: "ERR-SUP-0207 Missing or Expired UN 38.3 Certificate"
type: "error"
slug: "err-sup-0207"
summary: "Planned Ledgerline 7.3 blocking error preventing purchase orders for lithium cells from suppliers lacking valid UN 38.3 certificates."
audience: "staff"
status: "future"
sources: ["08_release_notes/RN-7.3 PREVIEW (planned March 2027).pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| code | ERR-SUP-0207 |
| type | Error (planned blocking) |
| module | PUR (Purchasing) |
| screen | PUR-PO-01 |
| status | Future (effective March 2027) |
| replaces | W-SUP-0207 |

ERR-SUP-0207 is a planned hard-stop error in Ledgerline ERP 7.3 that prevents order generation for lithium cells if the supplier lacks a valid [[topic-un-38-3-certificates|UN 38.3 certificate]][^r1]. Today, under Ledgerline 7.2.3-P4, this condition raises only warning W-SUP-0207 and does not halt purchase order entry[^r1]. When release [[rn-7-3-preview|RN-7.3-PREVIEW]] takes effect in March 2027, ERR-SUP-0207 will completely block purchase order creation without allowing senior buyer overrides[^r1][^r2].

## Meaning
ERR-SUP-0207 indicates that an order line contains a lithium-cell item, but the chosen vendor does not have a valid, unexpired UN 38.3 test summary certificate registered in the system[^r1].

## Cause
The error is triggered when a user attempts to save or release a purchase order line for a lithium-cell item against a vendor profile missing an active UN 38.3 certificate[^r1].

## How to fix
Under the planned 7.3 release, the error cannot be bypassed or overridden at order entry by senior buyers[^r2]. It halts purchase order number generation and vendor transmission until a valid UN 38.3 certificate is filed for the supplier[^r1][^r2].

## Raised by
Raised by screen [[screen-pur-po-01|PUR-PO-01]] Purchase Order Entry during order creation[^r1].

## Versions and conflicts
Today under Ledgerline 7.2.3-P4, missing or expired UN 38.3 certificates raise warning W-SUP-0207 at order entry rather than a hard stop[^r1]. From March 2027 in planned Ledgerline ERP 7.3, ERR-SUP-0207 replaces W-SUP-0207 as a mandatory blocking error that senior buyers cannot override (sources: RN-7.3-PREVIEW, 2027-03-01; kind: future_dated)[^r1][^r2].

## See also
* [[screen-pur-po-01|PUR-PO-01 Purchase Order Entry]]
* [[rn-7-3-preview|RN-7.3-PREVIEW Ledgerline ERP 7.3 Preview Notes]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]

## References

[^r1]: 08_release_notes/RN-7.3 PREVIEW (planned March 2027).pdf, p. 1, §1. What is planned
[^r2]: 08_release_notes/RN-7.3 PREVIEW (planned March 2027).pdf, p. 2, Common misunderstandings
