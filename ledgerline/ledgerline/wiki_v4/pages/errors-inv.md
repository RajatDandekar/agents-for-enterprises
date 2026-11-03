---
title: "Errors INV (ERR-INV-*)"
type: "error-list"
slug: "errors-inv"
summary: "Error code reference list for Accounts Payable invoice processing errors prefixed with ERR-INV in Ledgerline ERP 7.2."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf", "04_service_definitions/accounts_payable/inv_cancel.yaml", "04_service_definitions/accounts_payable/inv_get.yaml", "04_service_definitions/accounts_payable/inv_hold.yaml", "04_service_definitions/accounts_payable/inv_post.yaml", "04_service_definitions/accounts_payable/inv_release.yaml", "04_service_definitions/accounts_payable/inv_save.yaml", "04_service_definitions/inventory/csg_settle.yaml", "04_service_definitions/inventory/mrn_get.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| prefix | ERR-INV |
| module | Accounts Payable (AP) |
| manual | MAN-AP-72 |

This page catalogues the `ERR-INV-*` error codes raised across Accounts Payable invoice processing in Ledgerline ERP 7.2 [^r1][^r16]. These messages govern document retrieval, validation, posting, and cancellation workflows across the [[services-ap-inv|AP inv services]] [^r16][^r20]. Substantial definition discrepancies exist between backend service specifications and the user manual reference text [^r1][^r16].

### ERR-INV-0001

* **Message:** `SUPPLIER INVOICE NOT FOUND` [^r16][^r18]
* **Cause:** The requested accounts payable invoice document cannot be located by the service [^r18][^r22].
* **Remedy:** Verify that the internal invoice document reference is correct and exists on the ledger [^r18][^r22].
* **Raised by:** Service definitions `inv_cancel` [^r16], `inv_get` [^r18], `inv_hold` [^r19], `inv_post` [^r20], and `inv_release` [^r22].

### ERR-INV-0007

* **Message:** `SUPPLIER INVOICE NOT IN DRAFT (<status>)` [^r21][^r23]
* **Cause:** An action was attempted against an invoice record that is currently not in draft status [^r21][^r23].
* **Remedy:** Check the current voucher status before attempting release or posting workflows [^r21][^r23].
* **Raised by:** Service definitions `inv_post` [^r21] and `inv_release` [^r23].

### ERR-INV-0118

* **Message:** `DUPLICATE SUPPLIER INVOICE NO` [^r24]
* **Cause:** The supplier invoice number provided on save already exists for the vendor [^r2][^r24].
* **Remedy:** Check whether the supplier invoice has already been registered on the ledger, or correct the invoice reference [^r2][^r24].
* **Raised by:** Service definition `inv_save` [^r24]; see also [[err-inv-0118|ERR-INV-0118]].

### ERR-INV-0801

* **Message:** `SUPPLIER INVOICE CLOSED (<status>)` [^r17]
* **Cause:** A cancellation was attempted on an invoice voucher that is closed or already posted [^r8][^r17].
* **Remedy:** Ensure the invoice is eligible for direct cancellation; posted invoices cannot be directly cancelled via `inv_cancel` [^r8][^r17].
* **Raised by:** Service definition `inv_cancel` [^r17].

## Versions and conflicts

- **ERR-INV-0001 definition**: The backend service definitions (`inv_cancel`, `inv_get`, `inv_hold`, `inv_post`, `inv_release`) define `ERR-INV-0001` with message `SUPPLIER INVOICE NOT FOUND`, raised when an AP document cannot be located [^r16][^r18][^r19][^r20][^r22]. Conversely, [[man-ap-72|MAN-AP-72]] defines `ERR-INV-0001` on page 5 as "Mandatory field missing" (when required fields such as `SUP CD`, `SUP INV NO`, `INV DT`, or `GROSS` are blank) [^r1], and on page 7 as indicating that `BASIC` and `TAX AMT` do not reconcile to `GROSS` [^r5] (`contradiction`).
- **ERR-INV-0007 definition**: The backend service definitions (`inv_post`, `inv_release`) return `ERR-INV-0007` as `SUPPLIER INVOICE NOT IN DRAFT (<status>)` [^r21][^r23]. In contrast, [[man-ap-72|MAN-AP-72]] defines `ERR-INV-0007` on page 5 and page 7 as "Duplicate invoice number detected", raised when `SUP INV NO` already exists on the ledger for `SUP CD` [^r2][^r6] (`contradiction`).
- **ERR-INV-0118 definition**: The backend service definition `inv_save` defines `ERR-INV-0118` as `DUPLICATE SUPPLIER INVOICE NO` [^r24]. In contrast, [[man-ap-72|MAN-AP-72]] defines `ERR-INV-0118` on page 6 as "Header totals do not balance" (when `GROSS` does not equal `BASIC` plus `TAX AMT`) [^r3], and on page 7 as missing mandatory invoice lines or required header fields such as `PO NO` or monetary fields during `inv_post` [^r7] (`contradiction`).
- **ERR-INV-0801 definition**: Service definition `inv_cancel` raises `ERR-INV-0801` with message `SUPPLIER INVOICE CLOSED (<status>)` [^r17]. Manual [[man-ap-72|MAN-AP-72]] documents it on page 6 as "Invalid invoice status for requested action" (such as posting a cancelled record or cancelling a posted document) [^r4], and on page 7 specifically as preventing `inv_cancel` when an invoice is already posted [^r8] (`contradiction`).

## See also

* [[err-inv-0118|ERR-INV-0118 Duplicate supplier invoice number]]
* [[services-ap-inv|AP inv services]]
* [[screen-ap-inv-01|AP-INV-01 Supplier Invoice Entry]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 5, Messages
[^r16]: 04_service_definitions/accounts_payable/inv_cancel.yaml, errors
[^r20]: 04_service_definitions/accounts_payable/inv_post.yaml, errors
[^r18]: 04_service_definitions/accounts_payable/inv_get.yaml, errors
[^r22]: 04_service_definitions/accounts_payable/inv_release.yaml, errors
[^r19]: 04_service_definitions/accounts_payable/inv_hold.yaml, errors
[^r21]: 04_service_definitions/accounts_payable/inv_post.yaml, errors
[^r23]: 04_service_definitions/accounts_payable/inv_release.yaml, errors
[^r24]: 04_service_definitions/accounts_payable/inv_save.yaml, errors
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 5, Messages
[^r17]: 04_service_definitions/accounts_payable/inv_cancel.yaml, errors
[^r8]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 6, Messages
[^r7]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 7, Questions users ask
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 6, Messages
