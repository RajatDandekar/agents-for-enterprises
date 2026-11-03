---
title: "ERR-ITM-0801: Conversion factor invalid or calculation mismatch between units of measure"
type: "error"
slug: "err-itm-0801"
summary: "ERR-ITM-0801 is raised during unit of measure conversion calculations or when committing an item block without an explanation."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-ITM-0801 |
| Module | Inventory (INV) |
| Screen | INV-ITM-01 Item Master Entry |
| Services | itm_uom_conv, itm_block |
| Document | MAN-INV-72 |

ERR-ITM-0801 is an inventory error code in [[man-inv-72|MAN-INV-72]] raised during item unit of measure conversion maintenance and item status blocking. It typically prevents saving conversion parameters on [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]] when ratio definitions or units are invalid, or when numeric calculations overflow ledger tables. It also appears in user guidance regarding missing justification text when applying item blocks.

## Meaning
The message indicates an invalid unit conversion setup, a calculation mismatch that produces numeric overflow in ledger quantity tables, or a missing explanation when blocking an item [^r1][^r3].

## Cause
ERR-ITM-0801 is triggered under the following conditions:
* The `FROM UOM` and `TO UOM` entered are identical during execution of `itm_uom_conv` [^r1].
* The `FACTOR` field is left blank or contains a non-mathematical value [^r1].
* The resulting conversion calculation causes a numeric overflow in ledger quantity tables [^r1].
* The `itm_block` service is committed without entering an explanation in the `REASON` field [^r3].

## How to fix
To resolve the error, review the input values on the screen before retrying the operation [^r2]:
1. Check the ratio entered in `FACTOR` [^r2].
2. Verify that both unit codes are distinct and recognized in the system [^r2].
3. Press the `itm_uom_conv` button again [^r2].
4. If blocking an item record via `itm_block`, ensure an explanation is entered into the `REASON` field [^r3].

## Raised by
* `itm_uom_conv` service (part of [[services-inv-itm|INV itm services]]) [^r1]
* `itm_block` service (part of [[services-inv-itm|INV itm services]]) [^r3]

## Versions and conflicts
* **Contradictory trigger conditions**: In [[man-inv-72|MAN-INV-72]] (v7.2.3, p. 43, Messages), ERR-ITM-0801 is specified as a conversion calculation error during `itm_uom_conv` execution caused by identical units, blank or non-mathematical factors, or ledger table numeric overflow [^r1]. However, on page 44 (Questions users ask), the same manual states ERR-ITM-0801 is raised when `itm_block` is committed without entering an explanation in the `REASON` field [^r3]. (Kind: `contradiction`).

## See also
* [[errors-itm|ERR-ITM error codes]]
* [[errors-inv|Errors INV (ERR-INV-*)]]
* [[screen-inv-itm-01|INV-ITM-01 Item Master Entry]]
* [[services-inv-itm|INV itm services]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 43, Messages
[^r3]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 44, Questions users ask
[^r2]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 43, Messages
