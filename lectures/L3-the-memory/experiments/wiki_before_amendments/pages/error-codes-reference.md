---
title: System Error Codes and Troubleshooting
audience: all Bahi users
sources: MAN-PUR-72 §17.1, MAN-PUR-72 §17.2, MAN-PUR-72 §17.3, MAN-PUR-72 §17.4, MAN-PUR-72 §17.5, MAN-PUR-72 §17.6, MAN-PUR-72 §17.7, MAN-PUR-72 §17.8, MAN-PUR-72 §17.9, MAN-PUR-72 §17.10, MAN-PUR-72 §17.11, MAN-PUR-72 §17.12, MAN-PUR-72 §17.13, MAN-PUR-72 §17.14, MAN-PUR-72 §17.15, MAN-PUR-72 §17.16, MAN-PUR-72 §17.17, MAN-PUR-72 §17.18, MAN-PUR-72 §17.19, MAN-PUR-72 §17.20, MAN-PUR-72 §17.21, MAN-PUR-72 §17.22, MAN-PUR-72 §17.23, MAN-PUR-72 §17.24, MAN-PUR-72 §17.25, MAN-PUR-72 §17.26, MAN-PUR-72 §17.27, MAN-PUR-72 §17.28, MAN-PUR-72 §19.1, MAN-PUR-72 §19.2, MAN-PUR-72 §19.3, MAN-PUR-72 §19.4, MAN-PUR-72 §19.5
compiled_by: gemini:gemini-3.8-flash
---

# System Error Codes and Troubleshooting

Bahi ERP displays error codes and messages to explain why a purchasing transaction cannot proceed. Errors prevent you from saving the document, while warnings allow the record to save. Follow the procedures below to resolve system flags and troubleshoot common purchasing issues.

## Rules
- Read system messages by their code and text; the code indicates which rule failed, the text in brackets shows the failing value, errors stop the Save, and warnings do not [MAN-PUR-72 §17.1].
- Resolve `ERR-PO-0412 TAX REGION DOES NOT MATCH SUPPLIER STATE` by changing the tax code to an `-INTER` code with the same rate (for example, `GST18-INTER`) when the supplier is outside the plant's state, as Fetch always defaults to `GST18-INTRA` [MAN-PUR-72 §17.2].
- Resolve `ERR-SCR-0221 Fetch not done` by pressing F3, reviewing the fetched values, and saving again whenever you change or enter a supplier or item [MAN-PUR-72 §17.3].
- Resolve `ERR-PO-0610 Direct PO limit exceeded, raise PR` by raising a purchase request on PUR-PR-01, obtaining approval, and raising a STD order against it [MAN-PUR-72 §17.4].
- Resolve `ERR-PO-0611 Direct PO cannot refer PR` by switching the order type to STD or clearing the Source PR field [MAN-PUR-72 §17.5].
- Address warning `W-CC-114 Cost centre closed, document saved as Draft` by amending the order to an open cost centre, noting that the document saves in DR status under `<number> SAVED` while showing the warning on the header and order list [MAN-PUR-72 §17.6].
- Resolve `ERR-PO-0602 Source PR mandatory for STD PO` by entering an approved request number, or use a DIR order if the purchase value permits [MAN-PUR-72 §17.7].
- Resolve `ERR-PO-0603 Source PR not approved` by following up with the approver or waiting until the request moves to status AP [MAN-PUR-72 §17.8].
- Resolve `ERR-PO-0604 Item or quantity not as per PR` by correcting the line details or submitting a new request for the excess quantity [MAN-PUR-72 §17.9].
- Resolve `ERR-PO-0201 Quantity must be more than zero` by entering a positive quantity using the item's unit of measure [MAN-PUR-72 §17.10].
- Resolve `ERR-PO-0105` and `ERR-PR-0105 Need date in past` by entering today's date or a future date [MAN-PUR-72 §17.11].
- Resolve `ERR-PO-0715 Document not in releasable status` by ensuring the purchase order is in AP status before attempting release [MAN-PUR-72 §17.12].
- Resolve `ERR-PO-0702 PO not pending approval` by refreshing your inbox to confirm whether another user already acted on the order, as approval actions require PA status [MAN-PUR-72 §17.13].
- Handle `ERR-PO-0801 PO closed` by raising a new order, because orders in CN, RJ, or CL status cannot be amended or cancelled [MAN-PUR-72 §17.14].
- Resolve `ERR-PO-0001 PO not found` by verifying the order number using Ctrl+F or checking the order list [MAN-PUR-72 §17.15].
- Resolve `ERR-SUP-0030 Supplier not found` by pressing F2 in the supplier field or searching in PUR-SUP-03 [MAN-PUR-72 §17.16].
- Resolve `ERR-SUP-0031 Supplier not active` by locating and using the supplier's active replacement code [MAN-PUR-72 §17.17].
- Resolve `ERR-SUP-0118 GSTIN already registered` by searching for and selecting the existing supplier code rather than creating a duplicate record [MAN-PUR-72 §17.18].
- Resolve `ERR-ITM-0010 Item not found` and `ERR-ITM-0011 Item not found or inactive` by using item enquiry to locate an active item code [MAN-PUR-72 §17.19].
- Resolve `ERR-CC-0009 Cost centre not found` by pressing F2 in the Cost centre field to pick a valid code from the list [MAN-PUR-72 §17.20].
- Resolve `ERR-BUD-0207 Budget exceeded` by asking the cost centre owner for an alternative cost centre or requesting a budget transfer from Finance [MAN-PUR-72 §17.21].
- Resolve `ERR-TAX-0101 Invalid tax code` by pressing F2 in the Tax code field to choose an existing code [MAN-PUR-72 §17.22].
- Resolve `ERR-APR-0003 Self approval not allowed` by routing the document to a different authorised approver [MAN-PUR-72 §17.23].
- Resolve `ERR-APR-0004 Value above your limit` by accessing the document from the correct approver's inbox, as Bahi automatically routes orders based on approval limits [MAN-PUR-72 §17.24].
- Resolve `ERR-APR-0009 No approver found` by following company procedures for values exceeding the system's highest approval limit [MAN-PUR-72 §17.25].
- Resolve `ERR-SEC-0001 Not authorised` by requesting role updates through your manager via a written request to IT [MAN-PUR-72 §17.26].
- Resolve `ERR-PR-0007` and `ERR-PR-0008 Request not in the right status` by refreshing the screen and checking the status; ERR-PR-0007 indicates a submitted request was not in Draft, and ERR-PR-0008 indicates approval was attempted on a request not pending approval [MAN-PUR-72 §17.28].
- Troubleshoot orders not received by the supplier by checking status via Ctrl+F; orders in DR may have a closed cost centre, orders in PA await approval, orders in AP must be released, and only RL orders reach the supplier [MAN-PUR-72 §19.1].
- Troubleshoot changed purchase rates by checking current rate contracts via Fetch, as active contract rates replace historical order pricing [MAN-PUR-72 §19.2].
- Troubleshoot missing supplier names by searching for a single short word of the name, verifying the city, and comparing GSTIN records [MAN-PUR-72 §19.3].
- Troubleshoot screen freezes after clicking Save by waiting one minute and searching the order list by supplier, item, date, or client reference before taking further action [MAN-PUR-72 §19.4].
- Troubleshoot approvers unable to see documents by confirming the document was submitted to PA status rather than remaining in DR [MAN-PUR-72 §19.5].

## Watch out
- Do not press Save a second time if the screen hangs; wait one minute and search the order list, as pressing Save again creates a duplicate order [MAN-PUR-72 §19.4].
- Three incorrect user ID or password attempts will trigger `ERR-SEC-0002 Invalid credentials` and lock the user ID [MAN-PUR-72 §17.27].
- Approvers cannot view documents routed above their approval limit; the system automatically pushes higher-value documents to the next manager in the line [MAN-PUR-72 §19.5].

## Related
- [[purchase-requests]] Purchase Requests (PR)
- [[purchase-orders]] Purchase Order Entry and Rules
- [[document-approval-workflow]] Document Approval Workflows
- [[po-release-and-lifecycle]] PO Release, Amendments, and History
- [[supplier-onboarding-and-master]] Supplier Onboarding and Management
- [[rate-contracts-and-pricing]] Rate Contracts and Pricing Policies
- [[cost-centres-and-budgets]] Cost Centres and Budget Checks
- [[taxation-and-payment-terms]] Tax Codes and Payment Terms
- [[inventory-and-item-enquiry]] Items and Inventory Enquiry
- [[erp-conventions-and-navigation]] Bahi ERP Interface and Navigation
