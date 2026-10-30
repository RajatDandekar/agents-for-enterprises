---
title: Approval Matrix and Limits
audience: all purchase staff
sources: POL-APR-002 §1, POL-APR-002 §2.1, POL-APR-002 §2.2, POL-APR-002 §2.3, POL-APR-002 §3.1, POL-APR-002 §3.2, POL-APR-002 §3.3, POL-APR-002 §3.4, POL-APR-002 §4.1, POL-APR-002 §4.2, POL-APR-002 §4.3, POL-APR-002 §5.1, POL-APR-002 §5.2, POL-APR-002 §5.3, POL-APR-002 §6.1, POL-PUR-001 §5.1, POL-PUR-001 §5.2, POL-PUR-001 §5.3
compiled_by: gemini:gemini-3.8-flash
---

# Approval Matrix and Limits
This matrix defines who can approve a purchase request or purchase order and sets their financial thresholds. All approval limits apply to the gross value of each individual document, including VAT, freight, and packing charges. The policy applies from 2026-04-01.

## Rules
- Limits set who may approve a purchase request or purchase order, and up to what value [POL-APR-002 §1].
- Every limit applies to the gross value of one document, including VAT, freight, and packing [POL-APR-002 §2.1].
- Limits apply to gross value including VAT, not the basic value [POL-PUR-001 §5.1].
- Each limit applies per document, not per day or per supplier [POL-APR-002 §2.2].
- The role-based approval limits (gross including VAT) are: Purchase executive (PUR-EXEC) at £250,000; Senior buyer (PUR-SR) at £500,000; Purchase manager (PUR-MGR) at £1,000,000; Plant head (PLANT-HEAD) at £5,000,000; Stores (STORES) has no approval authority [POL-APR-002 §3.1].
- An order or document within the raiser's own limit is approved automatically upon submission, and Ledgerline records the raiser as the approver [POL-APR-002 §3.2].
- An order or document above the raiser's limit routes to their manager, and then up the line to the first person whose limit covers it [POL-APR-002 §3.3] [POL-PUR-001 §5.2].
- Documents above £5,000,000 require the Managing Director's written approval outside Ledgerline, which the plant head's office then records [POL-APR-002 §3.4].
- Approvers on leave may delegate authority in writing to someone of the same or higher role for a stated period, but never to a lower role [POL-APR-002 §4.3].
- The plant head reviews this approval matrix every April and whenever the organisation changes [POL-APR-002 §6.1].

## Watch out
- Do not split one requirement into several orders to stay within an approval limit [POL-APR-002 §2.3].
- Orders for the same item from the same supplier raised within seven days of each other count as one single requirement [POL-APR-002 §2.3].
- Documents over £5,000,000 cause Ledgerline to display ERR-APR-0009 (no approver found) until recorded by the plant head's office [POL-APR-002 §3.4].
- You cannot approve a document you raised; Ledgerline will refuse the approval with ERR-APR-0003 [POL-APR-002 §4.1] [POL-PUR-001 §5.3].
- Integration and service accounts (such as role SYS-ADMIN or SVC_AGENT) have no approval authority; any document approved by them is invalid and must be cancelled or re-approved by a person [POL-APR-002 §4.2].
- For example, an order with a basic value of £238,000 and 20% VAT (gross £285,600) exceeds a purchase executive's £250,000 limit and must route to the purchase manager [POL-APR-002 §5.1] [POL-APR-002 §5.2].

## Related
- [[purchase-policy-overview]] General Purchasing Policy
- [[purchase-requests]] Purchase Requests (PR)
- [[purchase-orders]] Purchase Order Entry and Rules
- [[document-approval-workflow]] Document Approval Workflows
- [[error-codes-reference]] System Error Codes and Troubleshooting
