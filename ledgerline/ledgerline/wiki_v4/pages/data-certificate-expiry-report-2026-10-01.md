---
title: "Certificate Expiry Report 2026-10-01 (PUR-R022)"
type: "data-source"
slug: "data-certificate-expiry-report-2026-10-01"
summary: "Monthly PUR-R022 batch extract tracking supplier certificates already expired or expiring within 90 days of 1 October 2026."
audience: "staff"
status: "current"
sources: ["06_transactions/reports/Certificate expiry report 2026-10-01.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Report Code | PUR-R022 |
| Batch Job | JOB-PUR-022 |
| Run Date | 2026-10-01 06:00 |
| Horizon | 90 days (valid-to on or before 2026-12-30) |
| Format | PDF report extract |
| Status | Current |

Certificate Expiry Report PUR-R022 is a periodic batch report evaluating supplier compliance certificates that have already expired or are due to expire within 90 days [^r1]. Generated on 2026-10-01 at 06:00 by batch job JOB-PUR-022, it captures documents with expiration dates on or before 2026-12-30 [^r1]. As of 26 October 2026, it serves as the operational baseline for identifying non-compliant suppliers and upcoming renewals across active vendors [^r1][^r3].

## What it holds

The document provides an extract of vendor compliance records requiring purchasing intervention, targeting certificates expiring between 2025-01-28 and 2026-12-30 [^r1][^r3]. It highlights records that have passed their validity date alongside active certificates nearing their expiration horizon [^r3].

## Columns

The report structures compliance data across six fields [^r2]:
* `SUP CD`: Supplier code [^r2].
* `NAME`: Supplier name [^r2].
* `CERT TYPE`: Type of certificate [^r2].
* `DOC REF`: Document reference identifier [^r2].
* `VALID TO`: Certificate expiration date [^r2].
* `FLAG`: Status flag, marked as `EXPIRED` for certificates expiring between 2025-01-28 and 2026-09-30, and left blank for certificates with valid-to dates from 2026-10-28 to 2026-12-28 [^r2][^r3].

## How to look up a row

Locate rows by filtering or searching the document by supplier code (`SUP CD`) or document reference (`DOC REF`) [^r2]. Rows sorted within the extract allow purchasing teams to review flags under `FLAG` to verify whether compliance documentation has lapsed or remains within the 90-day renewal window [^r2][^r3].

## Size

The extract spans at least 3 pages generated under the `DAYS=90` parameter run [^r1][^r3].

## See also

* [[sup-vc-ein-0042|Voltway Cells (VC-EIN-0042)]]
* [[sup-nc-gda-0063|Nordic Cell Co. (NC-GDA-0063)]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]

## References

[^r1]: 06_transactions/reports/Certificate expiry report 2026-10-01.pdf, p. 1, PUR-R022 CERTIFICATE EXPIRY DAYS=90
[^r3]: 06_transactions/reports/Certificate expiry report 2026-10-01.pdf, p. 3, PUR-R022 CERTIFICATE EXPIRY DAYS=90
[^r2]: 06_transactions/reports/Certificate expiry report 2026-10-01.pdf, p. 1, PUR-R022 CERTIFICATE EXPIRY DAYS=90
