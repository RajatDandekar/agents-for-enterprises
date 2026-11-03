---
title: "Topic: Supplier Performance Evaluation"
type: "topic"
slug: "topic-supplier-performance-evaluation"
summary: "Overview of Ledgerline automated supplier performance ratings, assembly-line defect blind spots, and proposed integration with stores logs."
audience: "staff"
status: "current"
sources: ["09_email_archive/2019/2019-08-08_Supplier performance scores.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Topic | Supplier Performance Evaluation |
| Primary system | Ledgerline |
| Lead reviewer | Daniel Okafor |
| Key data points | Delivery receipts, inspection rejections, stores manual logs |

Supplier performance evaluation tracks vendor reliability and component quality across deliveries at Northbridge Cycles. Ledgerline calculates automated supplier performance scores using delivery receipts and inspection rejections, though assembly-line failures require supplementary logging. Reviewing recurring discrepancies involves combining system-generated metrics with stores records.

## Performance rating calculation and limitations

Ledgerline generates supplier performance ratings using delivery receipts recorded at goods inwards alongside rejected parts logged by inspection [^r1]. Automated supplier scoring captures late drop-offs and damaged deliveries adequately, but does not capture components that pass initial receiving and fail during final fitting on the assembly line [^r2].

## Review process and manual reconciliation

[[user-dokafor|Daniel Okafor]] proposed aligning purchase ledger records with quality records and combining automated Ledgerline scores with manual logs kept by stores teams when reviewing recurring delivery discrepancies and lead-time drift with regular suppliers [^r3].

## See also

* [[user-dokafor]]

## References

[^r1]: 09_email_archive/2019/2019-08-08_Supplier performance scores.eml, body
[^r2]: 09_email_archive/2019/2019-08-08_Supplier performance scores.eml, body
[^r3]: 09_email_archive/2019/2019-08-08_Supplier performance scores.eml, body
