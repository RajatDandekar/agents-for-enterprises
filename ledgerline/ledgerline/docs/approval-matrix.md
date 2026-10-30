---
doc_id: POL-APR-002
title: Approval Matrix for Purchasing
owner: Plant head's office, Northbridge Cycles
version: 3.0
effective: 2026-04-01
audience: all purchase staff
---

# Approval Matrix for Purchasing (POL-APR-002)

## 1. Purpose
This matrix sets who may approve a purchase request or purchase order, and up to what value. It is the matrix referred to in Purchase Policy §5.2.

## 2. How limits are measured
2.1 Every limit is a limit on the **gross value including VAT** of one document. Freight and packing charged on the order count towards the gross value.
2.2 A limit is per document, not per day or per supplier.
2.3 Splitting one requirement into several orders to stay inside a limit is not allowed. Orders for the same item from the same supplier raised within seven days of each other are treated as one requirement.

## 3. The limits
3.1 Each role's approval limit, gross including VAT:

| Role code | Role | Limit (gross incl. VAT) |
|---|---|---|
| PUR-EXEC | Purchase executive | £250,000 |
| PUR-SR | Senior buyer | £500,000 |
| PUR-MGR | Purchase manager | £1,000,000 |
| PLANT-HEAD | Plant head | £5,000,000 |
| STORES | Stores | no approval authority |

3.2 A document within the raiser's own limit is approved when it is submitted. Ledgerline records the raiser as the approver.
3.3 A document above the raiser's limit goes to the raiser's manager. If the manager's limit does not cover it, it goes on up the line to the first person whose limit does.
3.4 Above £5,000,000 the order needs the Managing Director's written approval outside Ledgerline. Ledgerline shows ERR-APR-0009 (no approver found) for such a document; the plant head's office then records the MD's approval.

## 4. Who may not approve
4.1 Nobody may approve a document they raised (Purchase Policy §5.3). Ledgerline refuses with ERR-APR-0003.
4.2 Integration and service accounts (role SYS-ADMIN, for example SVC_AGENT) have no approval authority under this matrix, whatever their technical permissions in Ledgerline. A document approved by a service account is treated as unapproved and must be cancelled or re-approved by a person.
4.3 An approver on leave may delegate in writing to someone of the same or a higher role for a stated period. Delegation to a lower role is not allowed.

## 5. Examples
5.1 Emma Clarke (purchase executive) raises an order for 2,000 battery packs at £119.00: basic £238,000, VAT 20% £47,600, gross £285,600. The gross is above her £250,000 limit, so the order goes to her manager, Daniel Okafor (purchase manager, limit £1,000,000), for approval.
5.2 The same order at basic value alone (£238,000) would look within her limit. That is why limits are measured on the gross value (§2.1).
5.3 An order of £720,000 gross raised by the senior buyer goes to the purchase manager. An order of £1,200,000 gross raised by anyone in purchasing goes to the plant head, Henrik Weber.

## 6. Review
6.1 The plant head reviews this matrix every April, and when the organisation changes.
