---
title: "Decision 2026-10-01 Order Hold on Nordic Cell Co. (NC-GDA-0063)"
type: "decision"
slug: "decision-2026-10-01-nordic-cell-order-hold"
summary: "Operational hold instructed by Luis Moreno prohibiting lithium-cell orders from Nordic Cell Co. due to an expired UN 38.3 certificate."
audience: "staff"
status: "current"
sources: ["09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| decision_date | 2026-10-01 |
| decided_by | [[user-lmoreno|Luis Moreno]] |
| affected_supplier | [[sup-nc-gda-0063|Nordic Cell Co. (NC-GDA-0063)]] |
| status | current |

On 1 October 2026, [[user-lmoreno|Luis Moreno]] placed an immediate order hold on [[sup-nc-gda-0063|Nordic Cell Co. (NC-GDA-0063)]][^r1]. No lithium-cell part may be ordered from the supplier until a replacement test report is uploaded and verified, following the expiration of certificate UN38.3-TR/NC/2025/090 on 30 September 2026[^r1]. Because Ledgerline does not automatically enforce order blocks for expired [[topic-un-38-3-certificates|UN 38.3 certificates]], the hold must be manually observed despite the system showing an active supplier and contract[^r2].

## Background and Instruction

On 1 October 2026, Luis Moreno instructed the Purchasing team that no lithium-cell part may be ordered from Nordic Cell Co. (NC-GDA-0063) until a new test report is uploaded and checked[^r1]. This order hold was triggered by the expiration of certificate UN38.3-TR/NC/2025/090 on 30 September 2026[^r1].

## System Status and Operational Impact

Ledgerline does not automatically block purchase orders for suppliers with expired UN 38.3 certificates[^r2]. Consequently, Nordic Cell Co. remains marked as ACTIVE in the system, and its [[items-bat|BAT-500]] rate contract of £111.00 remains visible to buyers[^r2]. Buyers must manually refrain from placing orders against this contract until compliance clearance is confirmed[^r1][^r2].

## Versions and conflicts

* Today's rule: No lithium-cell part may be ordered from Nordic Cell Co. (NC-GDA-0063) until a new test report is uploaded and checked (instruction from Luis Moreno, 1 October 2026)[^r1].
* System status: Ledgerline does not automatically block purchase orders upon certificate expiry, leaving Nordic Cell Co. listed as ACTIVE with an available BAT-500 rate contract of £111.00 (as of 1 October 2026)[^r2].
* Kind: `email_overrides_sop`

## See also

* [[sup-nc-gda-0063|Nordic Cell Co. (NC-GDA-0063)]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]
* [[items-bat|BAT-* items]]
* [[user-lmoreno|Luis Moreno (LMORENO)]]

## References

[^r1]: 09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml, body
[^r2]: 09_email_archive/2026/2026-10-01_CERT EXPIRED - DO NOT ORDER_ Nordic Cell Co. (NC-GDA-0063).eml, body
