---
title: Cost Centres and Budget Checks
audience: all purchase staff
sources: POL-PUR-001 §4.1, POL-PUR-001 §4.2, POL-PUR-001 §4.3, MAN-DD-72 §9.1, MAN-DD-72 §9.2, MAN-DD-72 §9.3, MAN-PUR-72 §8.1, MAN-PUR-72 §8.2, MAN-PUR-72 §8.3, MAN-PUR-72 §8.4
compiled_by: gemini:gemini-3.8-flash
---

# Cost Centres and Budget Checks

Every purchase request and order must be assigned to an active cost centre with sufficient funds. Finance manages cost centre statuses and limits, while Ledgerline ERP tracks committed spend against quarterly budgets. Purchase executives must verify cost centres and budget availability before finalizing orders to prevent processing delays.

## Rules
- Charge every request and order to an open cost centre [POL-PUR-001 §4.1]. Note: POL-PUR-001 §4.1 applies from 2026-04-01 [POL-PUR-001 §4.1].
- Review cost centre details—including code (`cc_cd`), name, status (`OPEN` or `CLOSED`), `closed_on` date, and owner—in Ledgerline screen `FIN-CC-01` [MAN-DD-72 §9.1] [MAN-PUR-72 §8.1].
- Check the cost centre's status in Ledgerline screen `FIN-CC-01` or confirm it with Finance before raising an order [POL-PUR-001 §4.3]. Note: POL-PUR-001 §4.3 applies from 2026-04-01 [POL-PUR-001 §4.3].
- Verify available budget, which equals the total period amount minus committed spend (the gross value of approved and pending orders), via the budget check service (`bud_check`) [MAN-DD-72 §9.2] [MAN-DD-72 §9.3] [MAN-PUR-72 §8.4]. For example, the period budget may be set for 2026-Q4 [MAN-DD-72 §9.2].
- Note that Ledgerline automatically commits an order's gross value against the cost centre once the order is approved [MAN-PUR-72 §8.4].

## Watch out
- Closed cost centres cannot carry new spend; Finance closes them at the end of a production programme [POL-PUR-001 §4.2] [MAN-PUR-72 §8.2].
- If you enter a document against a closed cost centre, Ledgerline will not reject it outright; it saves it as a Draft, triggers warning `W-CC-114`, and will never send the order to the supplier [POL-PUR-001 §4.2] [MAN-PUR-72 §8.2].
- When you press Fetch, Ledgerline enters your default cost centre, but IT does not automatically update defaults when Finance closes a cost centre; always check the cost centre before saving [MAN-PUR-72 §8.3].
- If an order's gross value exceeds the available budget, saving the order will fail with error `ERR-BUD-0207` [MAN-PUR-72 §8.4].

## Related
- [[purchase-requests]] Purchase Requests (PR)
- [[purchase-orders]] Purchase Order Entry and Rules
- [[error-codes-reference]] System Error Codes and Troubleshooting
- [[data-dictionary-and-standards]] Ledgerline ERP Data Standards and Statuses
- [[erp-conventions-and-navigation]] Ledgerline ERP Interface and Navigation
