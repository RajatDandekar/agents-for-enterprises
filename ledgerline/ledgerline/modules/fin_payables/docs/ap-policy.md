---
doc_id: POL-FIN-021
title: Accounts Payable Policy
owner: Finance, Northbridge Cycles
version: 2.3
effective: 2026-04-01
audience: accounts payable, purchase, stores
---

# Accounts Payable Policy (POL-FIN-021)

## 1. Purpose
This policy sets out how a supplier's invoice is entered, checked and paid, so that we pay the right supplier, the right amount, once, on the right day.

## 2. Entering invoices
2.1 Every supplier invoice is entered in Ledgerline on screen FIN-AP-01 within three working days of arrival.
2.2 An invoice against a purchase order is a **PO invoice**. Any other invoice (repairs, services, small purchases) is a **non-PO invoice**.
2.3 Run **Match** before **Save**. Ledgerline will not save an invoice whose match has not been run (ERR-SCR-0221).
2.4 The supplier's invoice number is entered exactly as printed. Different suppliers may use the same number; always identify an invoice by supplier and number together.

## 3. The match
3.1 A PO invoice is matched three ways: the order (rate), the goods receipt (accepted quantity) and the invoice.
3.2 A non-PO invoice is checked two ways: an open cost centre with budget, and the approval of the cost centre's owner.

## 4. Holds
4.1 **Price (H-PRC).** An invoice rate up to **2%** above the order rate passes. Above 2%, the invoice is held.
4.2 **Quantity (H-QTY).** An invoice may not bill more than the accepted quantity not yet invoiced.
4.3 **Who decides a price hold.** When the supplier's contract rate changed between the order and the delivery, the **purchase manager** decides which rate applies. If the new rate applies, the purchase manager releases the hold. If not, Accounts asks the supplier for a **credit note** for the difference, plus its VAT, and the hold stays until it arrives.
4.4 **Who may release which hold.** H-PRC: purchase manager or financial controller. H-QTY: stores or financial controller. H-GRN: accounts payable, once the receipt is posted. H-DUP: financial controller only.
4.5 The integration service account never releases a hold.
4.6 A person who cannot release a hold may **refer** it (FIN-AP-03, Refer) to someone who can.

## 5. Posting
5.1 An invoice with no hold is posted: the supplier's account is credited and the VAT is recorded as input credit (POL-FIN-024).

## 6. Payment
6.1 Invoices are paid only in the weekly payment run (POL-FIN-022), on or after their due date.
6.2 The due date is the invoice date plus the supplier's payment term (N30, N45, N60).
6.3 An invoice on hold, or waiting for approval, cannot be proposed for payment.
6.4 Paying before the due date is an **early payment** and follows POL-FIN-023.
