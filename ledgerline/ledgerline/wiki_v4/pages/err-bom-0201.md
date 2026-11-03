---
title: "ERR-BOM-0201 Component line missing or invalid data"
type: "error"
slug: "err-bom-0201"
summary: "Ledgerline error when saving a bill of materials line with missing, non-numeric, or zero quantity per assembly or invalid scrap percentage."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error Code | ERR-BOM-0201 |
| Module | PRD |
| Type | Error |
| Owner | Production |
| Status | current |
| Screen | PRD-BOM-02 |
| Service | bom_save |

ERR-BOM-0201 is a Ledgerline production module validation error displayed on screen [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]. It prevents saving a bill of materials when a component line has missing or out-of-range quantity or scrap entries.[^r1] The error must be resolved by correcting line values before saving can proceed.[^r2]

| Property | Value |
|---|---|
| Error Code | ERR-BOM-0201 |
| Module | PRD |
| Screen | [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]] |
| Service | bom_save ([[services-prd-bom|PRD bom services]]) |
| Reference Manual | [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]] |

## Meaning

Error ERR-BOM-0201 indicates that a component line cannot be processed because required line data is missing or out of valid range.[^r1]

## Cause

The error occurs when a component line on a bill of materials contains a blank, non-numeric, or zero value in the QTY PER field, or invalid line data.[^r1]

## How to fix

To resolve ERR-BOM-0201, verify that valid numeric values exist in both the QTY PER and SCRAP % fields before pressing the bom_save action again.[^r2]

## Raised by

The error is raised by the `bom_save` service in [[services-prd-bom|PRD bom services]] during component line validation on [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]].[^r1][^r2]

## See also

* [[man-prd-72|MAN-PRD-72 Ledgerline ERP 7.2 User Manual: Production]]
* [[screen-prd-bom-02|PRD-BOM-02 Bill Of Materials]]
* [[services-prd-bom|PRD bom services]]
* [[err-bom-0001|ERR-BOM-0001 Parent assembly not found on bill of materials master]]
* [[err-itm-0011|ERR-ITM-0011 ITEM NOT FOUND OR INACTIVE]]

## References

[^r1]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 10, Messages
[^r2]: 03_ledgerline_manuals/MAN-PRD-72 Ledgerline 7.2 User Manual - Production and Quality v7.2.3.pdf, p. 10, Messages
