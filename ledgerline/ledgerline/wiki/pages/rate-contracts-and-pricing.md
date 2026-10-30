---
title: Rate Contracts and Pricing Policies
audience: all purchase staff
sources: POL-PUR-001 §6.4, POL-SUP-003 §7.1, POL-SUP-003 §7.2, POL-SUP-003 §7.3, POL-SUP-003 §8.1, POL-SUP-003 §8.2, MAN-DD-72 §4.5, MAN-PUR-72 §7.1, MAN-PUR-72 §7.2, MAN-PUR-72 §7.3
compiled_by: gemini:gemini-3.8-flash
---

# Rate Contracts and Pricing Policies
Rate contracts set agreed prices for regular items from suppliers over defined validity periods in Ledgerline ERP. Contracts undergo regular revisions and performance reviews to ensure pricing accuracy and supplier reliability. Orders pull active contract rates automatically to prevent pricing discrepancies.

## Rules
- Prefer suppliers who hold a current rate contract [POL-PUR-001 §6.4].
- Maintain a rate contract in Ledgerline with a valid-from and valid-to date for each regular supplier of a regular item [POL-SUP-003 §7.1].
- Enter rate contracts on the Rate contracts tab of the supplier master; this task belongs to the purchase manager's office [MAN-PUR-72 §7.1].
- Store contract details using item code, rate, valid-from date, and valid-to date (`sup_rate`: `itm_cd`, `rate`, `valid_from`, `valid_to`) [MAN-DD-72 §4.5].
- Apply a new rate contract starting from its valid-from date, which replaces the previous contract while keeping older rates in history for reference [POL-SUP-003 §7.2].
- Review rate contracts every six months, specifically in March and September [POL-SUP-003 §7.3].
- Review regular suppliers each quarter on delivery on time, rejection rate, and price through the senior buyer [POL-SUP-003 §8.1].
- Press Fetch on the order screen to populate the rate automatically from the contract whose validity period covers the current date [MAN-PUR-72 §7.2].
- Press F2 in the Rate field on the order screen to see all past and present rate contracts for the supplier and item listed from oldest to newest [MAN-PUR-72 §7.3].

## Watch out
- A cheaper quotation from a new supplier does not justify switching suppliers for a lithium-cell part [POL-PUR-001 §6.4].
- If no rate contract covers today's date when you press Fetch, Ledgerline fills the rate from the last order placed with that supplier for the item and flags the field in yellow [MAN-PUR-72 §7.2].
- A yellow rate field is only a suggestion and must be verified before saving the order [MAN-PUR-72 §7.2].
- Rates from expired contracts or prior purchase orders represent history only and cannot be used as active prices [MAN-PUR-72 §7.3].
- A supplier with a rejection rate above 2% for two consecutive quarters is placed on watch and must be visited by Quality [POL-SUP-003 §8.2].

## Related
- [[purchase-orders]] Purchase Order Entry and Rules
- [[purchase-policy-overview]] General Purchasing Policy
- [[supplier-onboarding-and-master]] Supplier Onboarding and Management
- [[battery-safety-compliance]] Battery Safety Compliance and Certificates
