---
title: "QRC-01 Raising a purchase request"
type: "procedure"
slug: "qrc-01"
summary: "Quick reference guide covering steps, item validation, cost centre rules, and submission on Ledgerline screen PUR-PR-01 for raising purchase requests."
audience: "staff"
status: "current"
sources: ["11_training/QRC-01 Raising a purchase request.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | QRC-01 |
| Version | 2026.1 |
| Effective date | 2026-01-12 |
| Status | CURRENT |
| Classification | INTERNAL |
| Owner | Purchasing key users |

QRC-01 is Northbridge Cycles' quick reference card governing how staff raise, validate, and submit purchase requests in Ledgerline [^r1]. Effective as of 12 January 2026, it details operational entry rules on screen [[screen-pur-pr-01|PUR-PR-01]] to ensure requisitions process cleanly into purchase orders [^r1][^r2]. Compliance with its item lookup, cost centre status checks, and scheduling guidelines avoids validation errors and order generation failures [^r7][^r9][^r13].

## Steps

1. **Initiate request and retrieve item details**: Navigate to [[screen-pur-pr-01|PUR-PR-01]], enter the item code, and press F3 (Fetch) to retrieve item information [^r2]. If the description does not populate, verify that the item code was entered correctly [^r6]. Never manually overwrite the description field if lookup fails, as doing so leads to purchase order generation errors [^r7]. For non-stock goods, ensure the general ledger category defaults properly once the item code is retrieved [^r8].
2. **Verify cost centres**: Confirm that the target cost centre is OPEN prior to entering quantities or need-by dates [^r3]. If a cost centre is closed, Ledgerline blocks submission, requiring the user to contact the finance office to reopen the charge code or supply an alternative [^r9]. If splitting request lines across different cost centres, confirm each line individually [^r10].
3. **Specify quantities and scheduling**: Enter all quantities using the standard pack units displayed on screen rather than loose singles [^r11]. Schedule need-by dates to account for supplier lead times into the Manchester works or Leeds unit [^r12]. Do not select the current day as the need-by date, because the purchasing team batches order releases during the working week [^r13].
4. **Save and submit**: Save the requisition into draft status (DR) using F8, then press F9 to submit it forward [^r4]. Check the status prompt at the foot of the screen after pressing F9 to confirm that submission succeeded [^r14].
5. **Approval routing**: Requisitions within the user's spending limit receive immediate approval, whereas requisitions exceeding that threshold route automatically to the user's manager [^r5]. For urgent requisitions routing above spending limits, notify the manager via internal e-mail to prompt approval queue clearance [^r15].

## Forms and screens

* [[screen-pur-pr-01|PUR-PR-01]]: Primary Ledgerline screen used to enter line items, execute F3 lookups, verify cost centre statuses, save drafts via F8, and submit requests via F9 [^r2][^r3][^r4].

## See also

* [[screen-pur-pr-01|PUR-PR-01 Purchase Request Entry]]
* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]

## References

[^r1]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Quick reference: Raising a purchase request
[^r2]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Steps
[^r7]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Fetching item details
[^r9]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Cost centre checks
[^r13]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Quantities and dates
[^r6]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Fetching item details
[^r8]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Fetching item details
[^r3]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Steps
[^r10]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Cost centre checks
[^r11]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Quantities and dates
[^r12]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Quantities and dates
[^r4]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Steps
[^r14]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Saving and submission
[^r5]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Steps
[^r15]: 11_training/QRC-01 Raising a purchase request.pdf, p. 1, Saving and submission
