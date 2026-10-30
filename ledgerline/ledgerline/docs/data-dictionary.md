---
doc_id: MAN-DD-72
title: Ledgerline ERP 7.2 Data Dictionary, Purchasing
owner: Ledgerline Systems, Documentation Group
version: 7.2.3
effective: 2025-01-15
audience: all Ledgerline users
---

# Ledgerline ERP 7.2 Data Dictionary: Purchasing (MAN-DD-72)

## 1. About the data dictionary
1.1 This dictionary lists the fields that Ledgerline's purchasing services send and return, with the legacy field names used in service payloads. Screen labels are given in brackets.
1.2 Service responses come in an envelope with four fields: rc (return code: S for success, E for error), err_cd (the error code when rc is E), msg (a short message in capitals) and data (the result).
1.3 Dates in payloads are YYYY-MM-DD. Amounts are in pounds sterling with two decimals. Codes are capitals.

## 2. Common codes
2.1 ou_cd (Organisation unit): NBC-MAN-01 is the Manchester plant; NBC-LDS-01 is the Leeds unit. Both are in the United Kingdom (country code GB).
2.2 state: two-letter country code of a supplier or organisation unit, for example GB (United Kingdom), NL (Netherlands), PL (Poland). The column keeps its 1998 name.
2.3 status (documents): DR, PA, AP, RL, RJ, CN, CL, as listed in the user manual (MAN-PUR-72 §16.1).
2.4 status (suppliers): ACTIVE or BLOCKED.
2.5 uom_cd (UOM): NOS for numbers (pieces), KG for kilograms.

## 3. Item master (itm_*)
3.1 itm_cd (Item code): the item's code, for example BAT-500 for the city e-bike battery pack.
3.2 descr (Description): the item's description.
3.3 cell_safety (Lithium cell): 1 if the part contains or charges lithium cells, else 0. Set by Quality.
3.4 category: RAW, COMPONENTS, SPARES or PACKING.
3.5 active: 1 if the item may be used on new documents.
3.6 reorder_lvl (Reorder level) and avg_daily_issue (Average daily issue): used by the reorder report and for days of cover.

## 4. Supplier master (sup_*)
4.1 sup_cd (Supplier code): generated on creation, for example VC-EIN-0042.
4.2 name, city, state, vat_no (VAT number), pt_cd (Payment terms), status.
4.3 created_by and created_on: who created the supplier and when. Migrated suppliers show MIGRATION.
4.4 Certificates (sup_cert): cert_type (UN38.3, ISO-9001 ...), doc_ref (document reference), valid_to, uploaded_by, uploaded_on.
4.5 Rate contracts (sup_rate): itm_cd, rate, valid_from, valid_to.

## 5. Purchase request (pr_*)
5.1 pr_no (Request number): PR/<year>/<five digits>, for example PR/2026/04417.
5.2 pr_type: STD.
5.3 cc_cd (Cost centre), need_dt (Need-by date), whs_cd (Warehouse), remarks.
5.4 est_value (Estimated value): quantity × estimated rate × 1.20.
5.5 raised_by, raised_on, approved_by.

## 6. Purchase order (po_*)
6.1 po_no (Order number): PO/<year>/<five digits>, for example PO/2026/01182.
6.2 po_type (Order type): STD or DIR.
6.3 pr_no (Source PR), sup_cd, tax_cd (Tax code), pt_cd, cc_cd, need_dt, whs_cd.
6.4 basic_value, tax_value, gross_value: gross = basic + tax.
6.5 created_by, created_on, approved_by, approved_on, released_on.
6.6 client_ref (Client reference): free text an integration may store to find the order again.
6.7 warn_cd (Warning): for example W-CC-114 when the order was saved as Draft against a closed cost centre.
6.8 fetch_tok: a token returned by the Fetch service (po_fetch) and required by Save (po_save). It is valid once, for one supplier and item.

## 7. Tax codes
7.1 VAT20-UK: VAT 20%, for a supplier in the same country as the organisation unit (the UK).
7.2 VAT20-RC: VAT 20% by reverse charge, for a supplier in another country.
7.3 VAT5-UK and VAT5-RC: the same two rules at the reduced rate of 5%.

## 8. Payment terms
8.1 N30, N45, N60: net 30, 45 or 60 days from the invoice. ADV: advance payment.

## 9. Cost centres and budgets
9.1 cc_cd, name, status (OPEN or CLOSED), closed_on, owner.
9.2 budget: amount for the period (for example 2026-Q4) and committed (the gross value of approved and pending orders).
9.3 available = amount − committed, returned by the budget check service (bud_check).
