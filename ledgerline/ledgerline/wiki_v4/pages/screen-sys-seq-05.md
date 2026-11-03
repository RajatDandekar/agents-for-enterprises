---
title: "SYS-SEQ-05 Document Sequence"
type: "screen"
slug: "screen-sys-seq-05"
summary: "Ledgerline screen used by system administrators to maintain document numbering prefixes and next available sequence numbers across transaction types."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/admin/seq_get.yaml", "04_service_definitions/admin/seq_list.yaml", "04_service_definitions/admin/seq_set.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | SYS-SEQ-05 |
| Module | System |
| Access path | System > Document sequence |
| Authorized roles | IT-ADMIN, SYS-ADMIN |
| Read service | seq_get |
| Write service | seq_set |
| Status | Current |

Screen SYS-SEQ-05 is the Ledgerline document sequence administration screen used to view and configure document numbering sequences across Northbridge Cycles' transaction types [^r1][^r2]. It is accessible through the navigation path System > Document sequence by users assigned the IT-ADMIN or SYS-ADMIN roles [^r1]. The screen interfaces directly with the administrative sequence service suite to retrieve, update, and list sequence counters [^r3][^r4][^r5][^r6].

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `doc_type` | String | Yes | The document type identifier used to retrieve or set numbering sequences [^r2][^r4]. |
| `prefix` | String | No | Optional alphanumeric prefix prepended to generated document numbers [^r2]. |
| `next_no` | Integer | No | The next available integer number in the document sequence [^r2]. |

## Keys and services

* **F3 (Get)**: Triggers the read service `seq_get` to retrieve sequence details for a given `doc_type` [^r3][^r4].
* **Set**: Triggers the write service `seq_set` to update document sequence settings and numbering [^r3][^r6].
* **List**: Triggers the `seq_list` service to provide a listing of document sequences [^r3][^r5].

Services associated with this screen are documented in [[services-adm-seq|ADM seq services]] [^r4][^r5][^r6].

## Messages

* `ERR-SEQ-0001` (Document Sequence Not Found): Raised when a requested document sequence does not exist [^r3].

## See also

* [[services-adm-seq|ADM seq services]]
* [[screen-sys-usr-01|SYS-USR-01 User]]
* [[screen-sys-par-04|SYS-PAR-04 System Parameter]]
* [[services-adm-par|ADM par services]]
* [[screen-sys-job-06|SYS-JOB-06 Batch Job Submit]]

## References

[^r1]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-SEQ-05 DOCUMENT SEQUENCE
[^r2]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-SEQ-05 DOCUMENT SEQUENCE
[^r3]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 44, SYS-SEQ-05 DOCUMENT SEQUENCE
[^r4]: 04_service_definitions/admin/seq_get.yaml, screen: SYS-SEQ-05
[^r5]: 04_service_definitions/admin/seq_list.yaml, service: seq_list
[^r6]: 04_service_definitions/admin/seq_set.yaml, service: seq_set
