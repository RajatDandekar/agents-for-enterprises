---
doc_id: LEG-SOP-006
title: Counterparty KYC
owner: Legal, Northbridge Cycles
version: 1.3
effective: 2026-02-01
audience: anyone registering a contract party
---

# Counterparty KYC (LEG-SOP-006)

1. Before any contract, the party must be on the contract party register with **both** its PAN and its VAT number.
2. The PAN is characters 3 to 12 of the VAT number. Ledgerline refuses a PAN that does not match (ERR-CT-0122).
3. **Ledgerline lets you save a party without PAN or VAT number**, and lets you raise a request against it. That request is saved as PK (pending KYC) and goes nowhere: it does not reach Legal or the signatory, and nobody is told. Ask the requester for the papers first.
4. To complete KYC later, update the party (Party Save with the PARTY CD) and then Resubmit the request on LEG-REQ-01.
5. Search the register by VAT number before registering. If the VAT number is already there, use that party; Ledgerline refuses a second party with the same VAT number (ERR-CT-0118). It does not stop a second party with the same name and no VAT number, so search by name and city as well.
6. A blocked party (status BLOCKED) cannot be used. Brightcell Seal Works, Lyon, was dissolved in 2024; it is not Brightcell Energy.
