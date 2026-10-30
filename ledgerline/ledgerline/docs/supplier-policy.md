---
doc_id: POL-SUP-003
title: Supplier Policy
owner: Purchase department, Northbridge Cycles
version: 2.3
effective: 2026-04-01
audience: all purchase staff
---

# Supplier Policy (POL-SUP-003)

## 1. Purpose
This policy says how a supplier enters the supplier master in Ledgerline, what papers it must give us, when it is blocked, and how we stop the same supplier being registered twice. It sits under the Purchase Policy (POL-PUR-001 §6).

## 2. Scope
2.1 It covers every supplier of materials, components, packing and services to the Manchester plant (NBC-MAN-01) and the Leeds unit (NBC-LDS-01).
2.2 It does not cover one-time cash purchases under £5,000 made from the petty-cash imprest; those follow the Finance petty-cash note.

## 3. Onboarding a new supplier
3.1 A new supplier is proposed by a purchase executive or senior buyer, with at least one written quotation and the reason an existing supplier cannot meet the need.
3.2 Before the supplier is created in Ledgerline (screen PUR-SUP-01), the proposer must collect: the VAT registration certificate (VAT number), the company registration number, a bank letter confirming the account, proof of insurance, and the signed Supplier Code of Conduct.
3.3 The proposer must search the supplier master first (screen PUR-SUP-03) by name, by city and by VAT number, and attach the search result to the onboarding file. See §6 on duplicates.
3.4 The purchase manager approves the onboarding file. Only after that approval may the supplier be created in Ledgerline.
3.5 A supplier created in Ledgerline is ACTIVE from the day it is created, but no order may be placed with it until every document in §3.2 and, for lithium-cell parts, the certificate in §4 is on file.
3.6 Onboarding normally takes five working days from a complete file. Urgency is not a reason to skip any step in this section.

## 4. UN 38.3 certificates
4.1 A supplier of any lithium-cell part (battery packs, hub motors, chargers, and any item marked lithium-cell in the item master) must hold a UN 38.3 certificate. This is the certificate referred to in Purchase Policy §6.2.
4.2 The certificate must be a test report from a laboratory accredited for lithium-cell materials (for example an UN 38.3-notified laboratory), or a BIS conformity certificate for stainless steel grade 304 or better.
4.3 The certificate is uploaded in Ledgerline against the supplier (certificate type UN38.3) with its document reference and its valid-to date, and checked by the senior buyer before the first order.
4.4 A UN 38.3 certificate is accepted if it was issued within the last 24 months and its valid-to date has not passed.
4.5 An expired certificate counts as no certificate. The supplier stays ACTIVE in the master, but no lithium-cell part may be ordered from it until a new certificate is uploaded and checked.
4.6 The certificate covers the supplier, not a single item. If the supplier changes the material or the compound of a part (for example a new silicone grade), it must give a fresh test report for that part.
4.7 Ledgerline does not stop an order to a supplier without a certificate. The check in this section is done by the person raising the order, and by the approver.

## 5. Blocking and unblocking
5.1 A supplier is BLOCKED in the master when: it has been replaced by a new code (for example after a merger or a change of VAT number); it has failed two quality audits in a row; or Finance has asked for a block for unpaid debit notes.
5.2 A blocked supplier keeps its code and history, but Ledgerline refuses new orders to it with ERR-SUP-0031.
5.3 Only the purchase manager may ask IT to unblock a supplier, in writing, with the reason.
5.4 When a supplier is given a new code, the old code is blocked and renamed "(old code, do not use)". Voltway Cells' old code VC-EIN-0009 is an example.

## 6. Duplicate suppliers
6.1 One legal supplier has exactly one active code. The VAT number is the test of sameness: two records with the same VAT number are the same supplier.
6.2 Suppliers are often called by short or slightly different names in quotations and e-mails (for example "Voltway Polymer Industries" for Voltway Cells). A name that is close to an existing supplier in the same city must be treated as that supplier until shown otherwise.
6.3 A near-match in a different city or with a different VAT number is a different supplier (for example Voltway Paints & Coatings, Rotterdam, is not Voltway Cells, Eindhoven).
6.4 Ledgerline refuses to create a second supplier with a VAT number that is already registered (ERR-SUP-0118). It does not catch a duplicate entered without a VAT number; that check is the proposer's job under §3.3.
6.5 A duplicate created by mistake must be reported to the purchase manager the same day, blocked, and its open documents moved to the correct code.

## 7. Rate contracts
7.1 Each regular supplier of a regular item has a rate contract in Ledgerline with a valid-from and valid-to date.
7.2 A new rate contract replaces the old one from its valid-from date. Older rates stay in the history for reference only.
7.3 Rate contracts are reviewed every six months, in March and September.

## 8. Supplier performance
8.1 The senior buyer reviews each regular supplier every quarter on delivery on time, rejection rate and price.
8.2 A supplier with a rejection rate above 2% for two quarters in a row is put on watch and visited by Quality.
