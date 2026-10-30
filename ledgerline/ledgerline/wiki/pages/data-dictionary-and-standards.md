---
title: Ledgerline ERP Data Standards and Statuses
audience: all Ledgerline users
sources: MAN-DD-72 §1.1, MAN-DD-72 §1.2, MAN-DD-72 §1.3, MAN-DD-72 §2.1, MAN-DD-72 §2.2, MAN-DD-72 §2.3, MAN-DD-72 §2.4, MAN-DD-72 §2.5, MAN-PUR-72 §16.1, MAN-PUR-72 §16.2, MAN-PUR-72 §21.1
compiled_by: gemini:gemini-3.8-flash
---

# Ledgerline ERP Data Standards and Statuses
This page defines the core data formats, organizational codes, unit of measure standards, and document lifecycle statuses used in Ledgerline ERP purchasing services. It covers formatting requirements for payloads and explains what each document status means during processing. Use these standards to ensure purchasing records are correctly formatted and tracked.

## Rules
- Service responses return an envelope containing four fields: `rc` (return code: S for success, E for error), `err_cd` (the error code when `rc` is E), `msg` (a short message in capitals), and `data` (the result) [MAN-DD-72 §1.2].
- Dates in payloads must use the format YYYY-MM-DD [MAN-DD-72 §1.3].
- Amounts must be entered in rupees with two decimal places [MAN-DD-72 §1.3].
- System codes must be written in capital letters [MAN-DD-72 §1.3].
- Organisation units use specific codes: NBC-MAN-01 for the Manchester plant and NBC-LDS-01 for the Leeds unit, both located in England (state code MH) [MAN-DD-72 §2.1].
- Supplier and organisation unit locations use two-letter state codes, such as MH (England), GJ (the Netherlands), and WB (West Bengal) [MAN-DD-72 §2.2].
- Unit of measure (`uom_cd`) standards are NOS for numbers (pieces) and KG for kilograms [MAN-DD-72 §2.5].
- Supplier status (`status`) must be either ACTIVE or BLOCKED [MAN-DD-72 §2.4].
- Purchasing documents move through seven standard status codes: DR, PA, AP, RL, RJ, CN, and CL [MAN-DD-72 §2.3, MAN-PUR-72 §16.1].
- DR means Draft: the document is saved but not submitted or not valid to proceed, and it is never sent to the supplier [MAN-PUR-72 §16.1].
- PA means Pending approval: the document is waiting in an approver's inbox [MAN-PUR-72 §16.1].
- AP means Approved: the document may now be released [MAN-PUR-72 §16.1].
- RL means Released: the document has been sent to the supplier [MAN-PUR-72 §16.1].
- RJ means Rejected by the approver [MAN-PUR-72 §16.1].
- CN means Cancelled [MAN-PUR-72 §16.1].
- CL means Closed: applies to a request that has been converted into an order [MAN-PUR-72 §16.1].
- Release refers to sending an approved order to the supplier [MAN-PUR-72 §21.1].

## Watch out
- Only orders in RL status have been sent to the supplier; an order in DR, PA, or AP has not reached the supplier [MAN-PUR-72 §16.2].

## Related
- [[po-release-and-lifecycle]] PO Release, Amendments, and History
- [[erp-conventions-and-navigation]] Ledgerline ERP Interface and Navigation
- [[document-approval-workflow]] Document Approval Workflows
- [[purchase-orders]] Purchase Order Entry and Rules
- [[purchase-requests]] Purchase Requests (PR)
