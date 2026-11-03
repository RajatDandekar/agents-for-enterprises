---
title: "Vendor Services"
type: "service-group"
slug: "services-sup-vendor"
summary: "Legacy Ledgerline 6.4 RPC service definitions for vendor creation via the VENDOR_ADD service."
audience: "staff"
status: "current"
sources: ["04_service_definitions/_legacy_6x/VENDOR_ADD.xml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| service_group | services-sup-vendor |
| module | sup |
| object | vendor |
| status | superseded |
| transport | LL6-RPC |

The vendor services group defines interfaces for creating and maintaining supplier accounts in Ledgerline. As Northbridge Cycles operates on modern Ledgerline releases, the legacy Ledgerline 6.4 RPC definitions remain preserved only as historical reference [^r1]. Understanding these superseded definitions clarifies the legacy integration architecture documented in the [[rn-ll6-history|Ledgerline 6 release history 2004-2012]] [^r1].

## Services

### VENDOR_ADD
* **Transport**: LL6-RPC [^r1].
* **Required fields**: `VENDOR_NAME`, `TOWN`, `COUNTY`, `VAT_REG`, `TERMS` [^r1].
* **Optional fields**: None specified [^r1].
* **Errors**: Returns `RETCODE` and `DOCNO` as output fields [^r2].
* **Source file**: `04_service_definitions/_legacy_6x/VENDOR_ADD.xml` [^r1].

## Versions and conflicts
* **Today's rule**: Legacy Ledgerline 6.4 RPC services are superseded and no longer represent the active integration interface [^r1].
* **Older rule**: In Ledgerline 6.4, vendor creation was performed via the `VENDOR_ADD` RPC using LL6-RPC transport with fields `VENDOR_NAME`, `TOWN`, `COUNTY`, `VAT_REG`, and `TERMS`, returning `RETCODE` and `DOCNO` [^r1][^r2].
* **Sources**: `04_service_definitions/_legacy_6x/VENDOR_ADD.xml` [^r1][^r2].
* **Kind**: `superseded`.

## See also
* [[rn-ll6-history|Ledgerline 6 release history 2004-2012]]

## References

[^r1]: 04_service_definitions/_legacy_6x/VENDOR_ADD.xml, whole file
[^r2]: 04_service_definitions/_legacy_6x/VENDOR_ADD.xml, whole file
