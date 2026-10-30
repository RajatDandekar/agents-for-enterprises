---
title: Battery Safety Compliance and Certificates
audience: all purchase staff
sources: POL-PUR-001 §6.2, POL-SUP-003 §4.1, POL-SUP-003 §4.2, POL-SUP-003 §4.3, POL-SUP-003 §4.4, POL-SUP-003 §4.5, POL-SUP-003 §4.6, POL-SUP-003 §4.7, MAN-DD-72 §3.3, MAN-DD-72 §4.4, MAN-PUR-72 §6.5, MAN-PUR-72 §6.6, AMD-SUP-2026-02 §1.1, AMD-SUP-2026-02 §1.2, AMD-SUP-2026-02 §2.1, AMD-SUP-2026-02 §3.1, AMD-SUP-2026-02 §3.2, AMD-SUP-2026-02 §3.3
compiled_by: gemini:gemini-3.8-flash
---

# Battery Safety Compliance and Certificates

Lithium-cell parts may only be purchased from suppliers with an approved, valid UN 38.3 certificate on file in Ledgerline ERP. Buyers must verify the certificate before placing an order because the system does not automatically block non-compliant purchases. Quality sets the lithium-cell flag on items, and certificates must be kept up to date to prevent supply disruptions.

## Rules
- Lithium-cell parts (such as battery packs, hub motors, chargers, or any item flagged as lithium-cell in the item master) can only be purchased from a supplier holding a valid UN 38.3 certificate uploaded in Ledgerline [POL-PUR-001 §6.2].
- Quality sets the `cell_safety` flag to 1 in the item master if the part contains or charges lithium cells [MAN-DD-72 §3.3].
- A supplier of any lithium-cell item must hold a UN 38.3 certificate [POL-SUP-003 §4.1].
- The certificate must be an accredited laboratory test report for lithium-cell materials (such as an UN 38.3-notified lab) or a BIS conformity certificate for stainless steel grade 304 or higher [POL-SUP-003 §4.2].
- Certificates are uploaded against the supplier under certificate type `UN38.3` with document reference and valid-to date, and must be checked by the senior buyer before the first order [POL-SUP-003 §4.3].
- Upload certificates in Ledgerline screen PUR-SUP-01 by going to the supplier's Certificates tab, clicking Add, entering Certificate type, Document reference, Valid to date, attaching the scanned file, and pressing F8 until "CERT SAVED" appears [MAN-PUR-72 §6.5].
- Ledgerline records the user who uploaded the certificate and the upload date under `uploaded_by` and `uploaded_on` [MAN-DD-72 §4.4, MAN-PUR-72 §6.5].
- Currently, a certificate is accepted if issued within the last 24 months and not expired; effective 1 September 2026, it is accepted only if issued within the last 12 months and its valid-to date is at least 60 days after the order date [POL-SUP-003 §4.4, AMD-SUP-2026-02 §1.1].
- Before raising an order for a lithium-cell part, staff must verify the certificate's issue date and valid-to date against the active rule [AMD-SUP-2026-02 §3.1].
- If a supplier changes the material or compound of a part (such as a new silicone grade), they must submit a fresh test report for that specific part [POL-SUP-003 §4.6].
- On the first working day of every month, the senior buyer must run the certificate-expiry report with a 90-day window and contact every supplier whose UN 38.3 certificate expires within that period [AMD-SUP-2026-02 §3.2].

## Watch out
- Ledgerline does not automatically stop or block orders to suppliers lacking a certificate or holding an expired certificate; the person raising the order and the approver must manually check compliance [POL-SUP-003 §4.7, MAN-PUR-72 §6.6].
- An expired certificate counts as no certificate; the supplier remains ACTIVE in the master, but no lithium-cell parts may be ordered until a new certificate is uploaded and verified [POL-PUR-001 §6.2, POL-SUP-003 §4.5].
- Ledgerline retains expired certificates on the tab for record-keeping and highlights passed valid-to dates in red [MAN-PUR-72 §6.6].
- From 1 September 2026, any certificate meeting the old rule (issued within 24 months and not expired) but failing the new rule counts as no certificate for new orders, though orders released before that date remain valid [AMD-SUP-2026-02 §1.2].

## Related
- [[purchase-policy-overview]] General Purchasing Policy
- [[purchase-orders]] Purchase Order Entry and Rules
- [[supplier-onboarding-and-master]] Supplier Onboarding and Management
- [[inventory-and-item-enquiry]] Items and Inventory Enquiry
- [[data-dictionary-and-standards]] Ledgerline ERP Data Standards and Statuses
