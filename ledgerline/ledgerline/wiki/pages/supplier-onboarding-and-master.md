---
title: Supplier Onboarding and Management
audience: all purchase staff
sources: POL-PUR-001 §6.1, POL-PUR-001 §6.3, POL-SUP-003 §1, POL-SUP-003 §2.1, POL-SUP-003 §2.2, POL-SUP-003 §3.1, POL-SUP-003 §3.2, POL-SUP-003 §3.3, POL-SUP-003 §3.4, POL-SUP-003 §3.5, POL-SUP-003 §3.6, POL-SUP-003 §5.1, POL-SUP-003 §5.2, POL-SUP-003 §5.3, POL-SUP-003 §5.4, POL-SUP-003 §6.1, POL-SUP-003 §6.2, POL-SUP-003 §6.3, POL-SUP-003 §6.4, POL-SUP-003 §6.5, MAN-DD-72 §4.1, MAN-DD-72 §4.2, MAN-DD-72 §4.3, MAN-PUR-72 §5.1, MAN-PUR-72 §5.2, MAN-PUR-72 §5.3, MAN-PUR-72 §5.4, MAN-PUR-72 §6.1, MAN-PUR-72 §6.2, MAN-PUR-72 §6.3, MAN-PUR-72 §6.4
compiled_by: gemini:gemini-3.8-flash
---

# Supplier Onboarding and Management

Suppliers must be fully qualified, approved, and active in the ERP system before any purchase order can be placed. This process sets out how purchase executives collect mandatory vendor records, prevent duplicate entries, and manage supplier statuses in Ledgerline ERP. It applies to all goods and service vendors for the Manchester plant and Leeds unit, excluding petty-cash purchases under £5,000.

## Rules
- Orders may only be placed with suppliers that hold an ACTIVE status in the supplier master [POL-PUR-001 §6.1].
- New suppliers must be fully onboarded under POL-SUP-003 before placing any purchase order [POL-PUR-001 §6.3].
- The policy covers all suppliers of materials, components, packing, and services to the Manchester plant (NBC-MAN-01) and Leeds unit (NBC-LDS-01) [POL-SUP-003 §2.1].
- A purchase executive or senior buyer proposes a new supplier using at least one written quotation and an explanation of why existing suppliers cannot meet the requirement [POL-SUP-003 §3.1].
- Before creating the supplier in Ledgerline (screen PUR-SUP-01), the proposer must collect the VAT registration certificate (VAT number), company registration number, a bank letter, proof of insurance, and the signed Supplier Code of Conduct [POL-SUP-003 §3.2].
- Proposers must search screen PUR-SUP-03 by name, city, and VAT number, and attach the search result to the onboarding file [POL-SUP-003 §3.3].
- Always search before creating a supplier; screen PUR-SUP-03 matches any part of the name ignoring case, so search by a short distinctive word and review the entire list [MAN-PUR-72 §5.1, MAN-PUR-72 §5.2].
- The purchase manager must approve the onboarding file before the supplier can be created in Ledgerline [POL-SUP-003 §3.4].
- Onboarding typically requires five working days from receipt of a complete file [POL-SUP-003 §3.6].
- Supplier master entry (screen PUR-SUP-01) requires Supplier name*, City*, Country code* (two letters, e.g., GB, NL), VAT number, and Payment terms (F2 lookup; default N30) [MAN-PUR-72 §6.2].
- On Save, Ledgerline automatically generates the supplier code from the name's initials, the first three letters of the city, and a running sequence number (e.g., VC-EIN-0042) [POL-SUP-003 §5.4, MAN-DD-72 §4.1, MAN-PUR-72 §6.2].
- The master record stores supplier code (`sup_cd`), name, city, country, VAT number (`vat_no`), payment terms (`pt_cd`), status, `created_by`, and `created_on` (migrated suppliers display `MIGRATION`) [MAN-DD-72 §4.1, MAN-DD-72 §4.2, MAN-DD-72 §4.3].
- Double-clicking a supplier in PUR-SUP-03 opens the master view containing VAT number, address, payment terms, certificates (type, document reference, valid-to date), and rate contracts [MAN-PUR-72 §5.4].
- A supplier is created with ACTIVE status, but no order may be placed until all mandatory onboarding documents—and lithium-cell certificates where applicable—are on file [POL-SUP-003 §3.5, MAN-PUR-72 §6.4].
- One legal entity must have exactly one active code, and two records with identical VAT numbers are treated as the same supplier [POL-SUP-003 §6.1].
- A near-name match in a different city or with a different VAT number represents a different supplier [POL-SUP-003 §6.3].
- A supplier is BLOCKED if it has been replaced by a new code, failed two consecutive quality audits, or if Finance requests a block due to unpaid debit notes [POL-SUP-003 §5.1].
- Blocked suppliers retain their code and history, display in red in PUR-SUP-03, and cause Ledgerline to reject new purchase orders with ERR-SUP-0031 [POL-SUP-003 §5.2, MAN-PUR-72 §5.3].
- When a supplier receives a new code, the old code is blocked and renamed "(old code, do not use)" [POL-SUP-003 §5.4, MAN-PUR-72 §5.3].
- Only the purchase manager may request IT in writing to unblock a supplier, stating the reason [POL-SUP-003 §5.3].

## Watch out
- One-time cash purchases under £5,000 made via petty-cash imprest do not follow this process and must follow the Finance petty-cash note [POL-SUP-003 §2.2].
- Urgency is never an acceptable reason to skip any onboarding step [POL-SUP-003 §3.6].
- Screen PUR-SUP-03 search does not match spelling variants; for example, searching "Voltway Polymer Industries" will fail to return "Voltway Cells" [MAN-PUR-72 §5.2].
- Quotations often use shortened vendor names; treat any supplier name close to an existing supplier in the same city as that existing supplier until proven otherwise [POL-SUP-003 §6.2].
- If a duplicate VAT number is entered on PUR-SUP-01, Save fails with ERR-SUP-0118 [POL-SUP-003 §6.4, MAN-PUR-72 §6.3].
- Ledgerline cannot catch duplicate suppliers if the VAT number field is left blank; preventing these duplicates is the proposer's responsibility during the PUR-SUP-03 search [POL-SUP-003 §6.4, MAN-PUR-72 §6.3].
- Ledgerline will mark a newly saved supplier ACTIVE even if required documents are missing [MAN-PUR-72 §6.4].
- If a duplicate record is created by mistake, report it to the purchase manager the same day, block the duplicate code, and move open documents to the correct code [POL-SUP-003 §6.5].

## Related
- [[purchase-policy-overview]] General Purchasing Policy
- [[purchase-orders]] Purchase Order Entry and Rules
- [[battery-safety-compliance]] Battery Safety Compliance and Certificates
- [[rate-contracts-and-pricing]] Rate Contracts and Pricing Policies
- [[taxation-and-payment-terms]] Tax Codes and Payment Terms
- [[inventory-and-item-enquiry]] Items and Inventory Enquiry
- [[data-dictionary-and-standards]] Ledgerline ERP Data Standards and Statuses
- [[error-codes-reference]] System Error Codes and Troubleshooting
