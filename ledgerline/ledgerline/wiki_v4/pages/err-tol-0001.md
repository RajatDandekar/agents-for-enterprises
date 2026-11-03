---
title: "ERR-TOL-0001 Tool Master Validation Failure"
type: "error"
slug: "err-tol-0001"
summary: "Ledgerline error raised when Tool Master record retrieval or saving fails due to an invalid tool code or missing mandatory fields."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-TOL-0001 |
| Module | PRD (Production) |
| Screen | PRD-TOL-14 |
| Services | tool_get, tool_save |
| Severity | Error |
| Status | Current |

ERR-TOL-0001 is a Ledgerline production validation error triggered during tool master maintenance on [[screen-prd-tol-14|PRD-TOL-14 Tool Master]][^r1][^r2]. It indicates that an entered tool code cannot be retrieved or that mandatory tool definition attributes are invalid or missing[^r1]. When this validation fails, input fields remain editable so the operator can fix formatting or supply missing values[^r2].

## Meaning
The error signals that the requested tool master record could not be retrieved from the database, or that a new or updated tool definition violates required field validation rules[^r1].

## Cause
ERR-TOL-0001 occurs when:
* The `TOOL CD` entered during a retrieval operation does not match an existing master record[^r1].
* The `TOOL CD` contains invalid formatting[^r1].
* Mandatory fields `DESCR` or `LIFE` are left blank or contain corrupted data during a save operation[^r1].

## How to fix
When the error is raised, screen [[screen-prd-tol-14|PRD-TOL-14]] keeps input fields editable to allow immediate data correction[^r2]. To resolve the error:
* Check and correct the spacing or syntax of the `TOOL CD` entry[^r2].
* Ensure the tool code corresponds to an existing record when retrieving data[^r1].
* Complete the mandatory `DESCR` and `LIFE` fields before saving[^r1][^r2].

## Raised by
* Service `tool_get` in [[services-prd-tool|PRD tool services]] during record retrieval[^r1].
* Service `tool_save` in [[services-prd-tool|PRD tool services]] during record validation and saving[^r1].
* Documented in [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]][^r1].

## See also
* [[screen-prd-tol-14|PRD-TOL-14 Tool Master]]
* [[services-prd-tool|PRD tool services]]
* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 68, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 68, Messages
