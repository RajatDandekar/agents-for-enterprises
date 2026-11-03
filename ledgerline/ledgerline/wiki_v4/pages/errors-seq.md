---
title: "Errors ERR-SEQ"
type: "error-list"
slug: "errors-seq"
summary: "Reference list of document sequence error codes with prefix ERR-SEQ raised by Ledgerline administrative sequence services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/admin/seq_get.yaml", "04_service_definitions/admin/seq_set.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-SEQ |
| Module | Admin (SYS / ADM) |
| Type | System error codes |
| Status | Current |

This page catalogues the `ERR-SEQ` error codes raised by Ledgerline administrative document sequencing services [^r1][^r2]. These errors occur when the system fails to retrieve or update configured document sequence definitions [^r1][^r2]. Sequence errors prevent document numbering operations across core transactional modules [^r1][^r2].

### ERR-SEQ-0001

* **Message:** DOCUMENT SEQUENCE NOT FOUND [^r1][^r2]
* **Cause:** The requested document sequence does not exist in the system configuration [^r1][^r2].
* **Remedy:** Verify and configure the required document sequence in [[screen-sys-seq-05|SYS-SEQ-05 Document Sequence]] or check with [[user-jfletcher|Joanna Fletcher (JFLETCHER)]].
* **Raised by:** Sequence retrieval services including `seq_get` [^r1] and service `seq_set` [^r2] in [[services-adm-seq|ADM seq services]].

## See also

* [[screen-sys-seq-05|SYS-SEQ-05 Document Sequence]]
* [[services-adm-seq|ADM seq services]]
* [[user-jfletcher|Joanna Fletcher (JFLETCHER)]]

## References

[^r1]: 04_service_definitions/admin/seq_get.yaml, errors
[^r2]: 04_service_definitions/admin/seq_set.yaml, errors
