---
doc_id: MAN-PUR-72
title: Ledgerline ERP 7.2 User Manual, Purchasing and Inventory Enquiry
owner: Ledgerline Systems, Documentation Group
version: 7.2.3
effective: 2025-01-15
audience: all Ledgerline users
---

# Ledgerline ERP 7.2 User Manual: Purchasing (MAN-PUR-72)

## 1. About this manual

### 1.1 Who this manual is for
This manual is for purchase executives, senior buyers, purchase managers, stores staff and approvers who use the Purchasing module of Ledgerline ERP 7.2. It describes the screens as they are shipped by Ledgerline Systems. Your company may have changed field labels, defaults or menus during implementation; where your screen differs from this manual, your company's own instructions apply.

### 1.2 What this manual does not cover
This manual explains how to use the screens. It does not set your company's purchasing rules. Approval limits, supplier qualification, certificate requirements and budget rules are set by your company's own policies. Ledgerline enforces some of them (for example approval limits configured against your user) and not others. When the manual says "your company's policy", read your company's policy documents.

### 1.3 Conventions
1. A field label followed by a red asterisk (*) is mandatory. Ledgerline will not save the screen while it is empty.
2. A field with a small F2 button beside it has a lookup. Press F2 with the cursor in the field, or click the button, to open the lookup list.
3. Grey fields are read-only. They are filled by Ledgerline when you press Fetch, or when the document is saved.
4. Messages appear in the status bar at the bottom of the window. Errors are shown in red and begin with ERR-. Warnings begin with W- and are shown in black.
5. Codes are shown in capitals. Ledgerline accepts lower case and converts it.
6. Dates are entered as DD-MM-YYYY on screens and returned as YYYY-MM-DD by services.

### 1.4 Screen codes
Every screen has a code shown at the right of the title bar, for example PUR-PO-01. The first part is the module (PUR purchasing, INV inventory, FIN finance), the middle part the screen family, and the number the screen within the family. Quote the screen code when you raise a support ticket.

### 1.5 Version history of this manual
Version 7.2.3 (January 2025) added the Fetch requirement on the order screen (§11.3), the cost-centre warning W-CC-114 (§17.6) and the error catalogue in Chapter 17. Version 7.2.0 (2023) introduced the approval inbox (PUR-POA-04). Versions before 7.0 used a different menu and are not covered.

## 2. Signing in and the main window

### 2.1 Signing in
Start the Ledgerline client from the desktop icon. Enter your user ID and password and choose your organisation unit (for example NBC-MAN-01). Your user ID is given to you by your IT department. After three wrong passwords your user ID is locked for 30 minutes; IT can unlock it sooner.

### 2.2 The main window
The main window has a menu bar (File, Edit, View, Masters, Purchase, Inventory, Reports, Help), a navigation tree on the left and the work area on the right. The navigation tree shows only the screens your role may open. A screen that appears grey in the tree is installed but not allowed for your role.

### 2.3 The status bar
The status bar at the bottom shows, from left to right: the last message, your user ID, and your organisation unit. Read the status bar after every Save. Ledgerline does not show a pop-up for most messages.

### 2.4 Session timeout
A session that has been idle for 20 minutes is closed. Unsaved work on open screens is lost. Ledgerline does not keep a half-filled screen across sessions; save as Draft where the screen allows it.

### 2.5 Function keys
The function keys work on every screen:

| Key | Action |
|---|---|
| F2 | Open the lookup for the current field |
| F3 | Fetch defaults (order and request screens) |
| F5 | Refresh the screen from the database |
| F7 | Clear the screen |
| F8 | Save |
| F9 | Submit or release, depending on the screen |
| F10 | Open the menu bar |
| Ctrl+P | Print the current document |
| Ctrl+F | Find a document by number |

### 2.6 Changing your password
Choose File, then Change password. A password must be at least eight characters and include a digit. Passwords expire every 90 days.

### 2.7 Printing
Ctrl+P prints the current document on the default printer in the layout set by your company. A purchase order can be printed only after it is Released; before that the print shows the word DRAFT across the page.

## 3. Item enquiry (INV-ITM-03)

### 3.1 Purpose
Item enquiry finds items in the item master by code or description. Use it before raising a request or an order, to get the exact item code.

### 3.2 Searching
Type any part of the description or code in Search text and press Enter. The search ignores case and spaces, so "5l battery pack" and "5 L Battery pack" find the same items. Use % as a wildcard in the middle of a word. Up to 20 rows are shown; refine the search if the item you want is not listed.

### 3.3 Reading the list
The list shows the item code, description, unit of measure (UOM) and whether the item is active. Inactive items are shown in grey and cannot be used on a new request or order. An item code ending in -R (for example BAT-500-R) is a rework item used by Quality; do not order it from suppliers.

### 3.4 Item details
Double-click an item, or press Enter on the selected row, to open the item master view. It shows the category, the reorder level, the average daily issue and the lithium-cell flag. The lithium-cell flag is set by Quality for parts that contain or charge lithium cells, such as battery packs, hub motors and chargers.

### 3.5 Lookup from other screens
Pressing F2 in any Item code field opens the same search in a small window. Select a row and press Enter to copy the code back to the field.

## 4. Stock enquiry (INV-STK-02)

### 4.1 Purpose
Stock enquiry shows how much of an item is in each warehouse: on hand, allocated, on order, and days of cover. Stock figures change all day as stores issue and receive material, so always read them from this screen at the time you need them. Do not copy stock figures into e-mails or documents as if they were permanent.

### 4.2 Fields
Item code (mandatory, F2 lookup) and Warehouse (optional, F2 lookup). Leave Warehouse empty to see every warehouse.

### 4.3 Reading the result
On hand is the quantity physically in the warehouse. Allocated is the quantity reserved for production orders. On order is the quantity on released purchase orders not yet received. Days of cover is on hand divided by the item's average daily issue, rounded down.

### 4.4 The stock ledger
Press the Ledger button to see every receipt and issue for the item, newest first. The ledger is read-only. Corrections are made by stores through a stock adjustment, which needs the stores manager's approval.

### 4.5 Reorder list
Reports, then Items below reorder level, lists every item whose on-hand plus on-order quantity is below its reorder level. Buyers usually run it every morning.

## 5. Supplier enquiry (PUR-SUP-03)

### 5.1 Purpose
Supplier enquiry finds suppliers in the supplier master by name. Always search before creating a supplier.

### 5.2 Searching
Type part of the supplier's name in Name like and press Enter. The search matches any part of the name, ignoring case. It does not match spelling variants: "Voltway Polymer Industries" will not find "Voltway Cells". Search on a short distinctive word (for example "Voltway") and read the whole list.

### 5.3 Reading the list
The list shows the supplier code, name, city, country and status. Status is ACTIVE or BLOCKED. Blocked suppliers are shown in red. A supplier whose name ends in "(old code, do not use)" has been replaced by a new code; use the active one.

### 5.4 Supplier details
Double-click a supplier to open the supplier master view: VAT number, address, payment terms, certificates and rate contracts. The Certificates tab shows each certificate's type, document reference and valid-to date.

## 6. Supplier master entry (PUR-SUP-01)

### 6.1 Purpose
Creates a new supplier. In most companies only purchase executives and senior buyers may open this screen, and only after the supplier has been approved under the company's supplier policy.

### 6.2 Fields
Supplier name*, City*, Country code* (two letters, for example GB, NL), VAT number, Payment terms (F2 lookup; default N30). The supplier code is generated by Ledgerline on Save from the initials of the name, the first three letters of the city and a running number.

### 6.3 VAT number check
If a VAT number is entered, Ledgerline checks that no other supplier has the same VAT number. If one does, Save fails with ERR-SUP-0118 and the existing supplier is not changed. Ledgerline cannot check for duplicates when the VAT number field is left empty.

### 6.4 After saving
A new supplier is created ACTIVE. Ledgerline does not hold the supplier back for missing documents; any such check is a company procedure. The status bar shows SUPPLIER <code> CREATED.

### 6.5 Uploading a certificate
Open the supplier, go to the Certificates tab and press Add. Enter Certificate type* (for example UN38.3, ISO-9001), Document reference* and Valid to*. Attach the scanned file. Press F8. The status bar shows CERT SAVED. Ledgerline records who uploaded the certificate and when.

### 6.6 Expired certificates
Ledgerline keeps expired certificates on the tab for the record. It shows the valid-to date in red once it has passed. Ledgerline does not block orders for an expired certificate.

## 7. Rate contracts

### 7.1 Purpose
A rate contract records the agreed price of an item from a supplier for a period (valid from, valid to). Rate contracts are entered by the purchase manager's office on the Rate contracts tab of the supplier master.

### 7.2 Which rate Ledgerline uses
When you press Fetch on the order screen, Ledgerline fills the rate from the rate contract whose period covers today. If no contract covers today, it fills the rate of the last order to that supplier for that item, and shows the rate field in yellow. A yellow rate is only a suggestion; check it before saving.

### 7.3 Viewing rate history
Press F2 in the Rate field of the order screen to see every rate contract for the supplier and item, oldest first, with their periods. Rates from expired contracts and from old orders are history, not prices you may use.

## 8. Cost centres (FIN-CC-01)

### 8.1 Purpose
Every request and order is charged to a cost centre. The cost centre screen shows each cost centre's name, owner, status (OPEN or CLOSED) and the date it was closed, with its budget for the quarter and the amount already committed.

### 8.2 Status
Finance opens and closes cost centres. A closed cost centre cannot carry new spend. Ledgerline does not refuse a document charged to a closed cost centre: it saves the document as Draft and sets warning W-CC-114 (see §17.6).

### 8.3 Your default cost centre
Each user has a default cost centre, set by IT. The request and order screens fill it when you press Fetch. Defaults are not updated automatically when Finance closes a cost centre, so a default can point to a closed one. Always check the cost centre before saving.

### 8.4 Budget check
Budget available is the quarter's budget minus the committed amount. When an order is approved, Ledgerline commits its gross value against the cost centre. If the gross value is more than the budget available, Save fails with ERR-BUD-0207.

## 9. Purchase request entry (PUR-PR-01)

### 9.1 Purpose
A purchase request (PR) asks for an item to be bought. In most companies every purchase above a set value must start with a request.

### 9.2 Fields
Item code* (F2), Quantity*, Need-by date*, Cost centre* (F2), Warehouse (F2; default WH-MAN-STR), Estimated rate, Remarks. Request type is STD for normal requests.

### 9.3 Fetch
Press F3 (Fetch) after entering the item code. Ledgerline fills the unit of measure, the warehouse, your default cost centre and an estimated rate. The estimated rate is the rate on the last released order for the item, not the current contract rate.

### 9.4 Saving a request
Press F8. Ledgerline gives the request a number (for example PR/2026/04417) and saves it in status DR (Draft). The estimated value is quantity times estimated rate times 1.20: Ledgerline assumes 20% VAT on every request whatever the item's real tax.

### 9.5 Submitting a request
Press F9 (Submit). If the estimated value is within your approval limit, the request is approved at once and the status becomes AP. If it is above your limit, Ledgerline routes it to your manager, or further up the line until it reaches someone whose limit covers it, sets the status PA (pending approval), and e-mails the approver.

### 9.6 Need-by date
The need-by date must be today or later. A date in the past gives ERR-PR-0105.

## 10. Purchase request approval (PUR-PR-04)

### 10.1 Purpose
Approvers approve or reject requests waiting for them.

### 10.2 Approving
Open the request from your approval inbox, check the item, quantity, estimated value and cost centre, enter a comment and choose Approve. The status becomes AP. You cannot approve a request you raised yourself (ERR-APR-0003) or one whose value is above your limit (ERR-APR-0004).

### 10.3 Rejecting
Choose Reject and enter the reason. The status becomes RJ and the raiser is told by e-mail. A rejected request cannot be resubmitted; raise a new one.

## 11. Purchase order entry (PUR-PO-01)

### 11.1 Purpose
The purchase order (PO) screen creates an order to a supplier. It has a header (supplier, type, tax code, cost centre, need-by date, warehouse) and a line grid (item, quantity, rate).

### 11.2 Order types
STD (standard) orders are raised against an approved purchase request; enter the request number in Source PR. DIR (direct) orders have no request and are allowed only for small values (see §11.7). Ledgerline checks the type on Save.

### 11.3 Fetch before Save
After entering the supplier and the item, press F3 (Fetch). Fetch fills the rate, the tax code, the payment terms and the warehouse, and, for a STD order, the cost centre, need-by date and quantity from the request. Ledgerline 7.2.3 refuses to save an order on which Fetch was not run for the current supplier and item, with ERR-SCR-0221 (FETCH NOT DONE). If you change the supplier or the item after Fetch, press Fetch again.

### 11.4 The tax code
Fetch always fills the tax code VAT20-UK, the code for a supplier in the UK. For a supplier in another country you must change it to the reverse-charge code (-RC) before saving; otherwise Save fails with ERR-PO-0412. Press F2 in the Tax code field to see the codes.

### 11.5 Header fields
Supplier code* (F2), Order type*, Source PR (F2, STD orders only), Tax code* (F2), Payment terms (from the supplier), Cost centre* (F2), Need-by date*, Warehouse (F2). Remarks are optional and printed on the order.

### 11.6 Line fields
Item code* (F2), Quantity*, Rate* (filled by Fetch; F2 shows the rate history), UOM (read-only). Ledgerline 7.2 allows one line per order on this screen; for several items, raise several orders.

### 11.7 Direct orders
A DIR order is refused on Save if its gross value is above the direct-order limit configured for your company (shipped default £50,000), with ERR-PO-0610. Raise a purchase request instead. A DIR order may not refer to a request (ERR-PO-0611).

### 11.8 Saving the order
Press F8. Ledgerline checks the supplier, the item, the quantity, the need-by date, the tax code and the source request, computes tax and gross value, checks the cost centre and budget, and gives the order its number (for example PO/2026/01182). The status bar shows <PO number> SAVED. The message is the same whatever status the order was saved in. Read the Status field on the header after saving.

### 11.9 The status after saving
If the cost centre is closed, the order is saved as DR (Draft) with warning W-CC-114, and nothing is sent to anyone. If the gross value is within your limit, the order is AP (approved). If the order is against a request whose approver's limit covers the order's gross value, it is AP and the request's approver is recorded. Otherwise the order is PA and goes to the approver's inbox.

### 111.00 Quantity against the request
An order against a request may not be for a different item or a larger quantity than the request (ERR-PO-0604). The request is closed (CL) when the order is saved against it.

### 11.11 Supplier status
Orders can be saved only for ACTIVE suppliers. A blocked supplier gives ERR-SUP-0031. Ledgerline does not check certificates on this screen.

## 12. Purchase order approval (PUR-POA-04)

### 12.1 The approval inbox
Approvers see documents waiting for them in the approval inbox: Purchase, then Order approval. Each row shows the document type, number, who raised it and when. Ledgerline also e-mails the approver when a document arrives.

### 12.2 Approving an order
Open the order, check it and press Approve with an optional comment. The status becomes AP. You cannot approve an order you created (ERR-APR-0003), one above your limit (ERR-APR-0004), or one that is not pending approval (ERR-PO-0702).

### 12.3 Rejecting an order
Press Reject and enter a reason (mandatory). The status becomes RJ and the budget committed for the order is released.

### 12.4 Approved is not released
An approved order (AP) has not been sent to the supplier. It must be released (Chapter 13).

## 13. Purchase order release (PUR-POR-05)

### 13.1 Purpose
Release sends an approved order to the supplier. Only orders in status AP can be released.

### 13.2 Releasing
Open the order and press F9 (Release). The status becomes RL, the release date is recorded, the quantity is added to stock on order, and Ledgerline e-mails the order to the supplier's order address.

### 13.3 When release fails
An order in any other status gives ERR-PO-0715 (DOCUMENT NOT IN RELEASABLE STATUS) with the current status in brackets. DR usually means the cost centre was closed when the order was saved; PA means the approver has not yet approved.

### 13.4 What the supplier receives
The supplier receives the order number, item, quantity, rate, need-by date and delivery warehouse. Remarks are printed on the order.

## 14. Purchase order amendment and cancellation (PUR-POM-06)

### 14.1 Purpose
Change an order's quantity, need-by date or cost centre, or cancel it.

### 14.2 Amending
Open the order, change the fields and press F8. Ledgerline recalculates the gross value, releases the budget the order had committed, checks the new cost centre and commits again. If the new cost centre is closed, the order goes back to Draft with W-CC-114.

### 14.3 Approval after amendment
If the amended gross value is still covered by the original approval, the order keeps its status. If it is more than the approval covers, the order goes back to PA for approval, even if it had been released.

### 14.4 Moving a Draft off a closed cost centre
To rescue an order stuck in Draft because its cost centre was closed, amend the cost centre to an open one. The order then becomes AP or PA by the normal rules, and can be released once approved.

### 14.5 Cancelling
Press Cancel and enter a reason. The status becomes CN, committed budget is released, and for a released order the quantity is removed from stock on order. Tell the supplier yourself; Ledgerline does not send a cancellation notice.

### 14.6 Closed orders
Orders in status CN, RJ or CL cannot be amended (ERR-PO-0801).

## 15. Purchase order history (PUR-POH-02)

### 15.1 Purpose
Shows the last ten released orders for an item, optionally for one supplier, newest first, with quantity, rate and date.

### 15.2 Using history
History tells you who supplied an item before and at what price. Rates on old orders are history; the price for a new order comes from the current rate contract (§7.2).

### 15.3 Searching orders
Purchase, then Order list, searches orders by supplier, item, status, client reference and creation date.

## 16. Document statuses

### 16.1 Status codes
Requests and orders move through these statuses:

| Code | Meaning |
|---|---|
| DR | Draft: saved, not submitted or not valid to proceed; never sent to the supplier |
| PA | Pending approval: waiting in an approver's inbox |
| AP | Approved: may be released |
| RL | Released: sent to the supplier |
| RJ | Rejected by the approver |
| CN | Cancelled |
| CL | Closed: a request converted into an order |

### 16.2 Which status means the supplier has the order
Only RL. An order in DR, PA or AP has not been sent to the supplier.

## 17. Messages and error codes

### 17.1 How to read a message
Every message has a code and a short text, for example ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (GJ). The code tells you which rule failed; the text in brackets gives the value that failed it. Errors stop the Save. Warnings do not.

### 17.2 ERR-PO-0412 Tax code does not match supplier country
Cause: the tax code is for the wrong country. A UK supplier needs a -UK code; a supplier in any other country needs a reverse-charge -RC code. Fetch always fills VAT20-UK. Remedy: change the tax code to the -RC code with the same rate (for example VAT20-RC) and save again.

### 17.3 ERR-SCR-0221 Fetch not done
Cause: the order was saved without pressing Fetch for the current supplier and item, or after changing them. Remedy: press F3, check the fetched values and save again.

### 17.4 ERR-PO-0610 Direct PO limit exceeded, raise PR
Cause: a DIR order's gross value is above the direct-order limit. Remedy: raise a purchase request on PUR-PR-01, get it approved, then raise a STD order against it.

### 17.5 ERR-PO-0611 Direct PO cannot refer PR
Cause: a source request was entered on a DIR order. Remedy: change the order type to STD, or clear Source PR.

### 17.6 W-CC-114 Cost centre closed, document saved as Draft
Cause: the cost centre on the document is CLOSED. This is a warning, not an error: the document is saved with a number, in status DR, and the status bar shows only <number> SAVED. The warning code is visible on the header's Warning field and in the order list. Remedy: amend the order to an open cost centre (§14.4).

### 17.7 ERR-PO-0602 Source PR mandatory for STD PO
Cause: a STD order has no source request. Remedy: enter the approved request number, or use a DIR order if the value allows.

### 17.8 ERR-PO-0603 Source PR not approved
Cause: the source request is not in status AP. The current status is shown in brackets. Remedy: wait for the approver, or follow up with them.

### 17.9 ERR-PO-0604 Item or quantity not as per PR
Cause: the order's item differs from the request's item, or the quantity is more than requested. Remedy: correct the line, or raise a new request for the extra quantity.

### 17.10 ERR-PO-0201 Quantity must be more than zero
Cause: quantity is zero or negative. Remedy: enter the quantity in the item's unit of measure.

### 17.11 ERR-PO-0105 and ERR-PR-0105 Need date in past
Cause: the need-by date is before today. Remedy: enter today's date or a later one.

### 17.12 ERR-PO-0715 Document not in releasable status
Cause: release was attempted on an order not in AP. Remedy: see §13.3.

### 17.13 ERR-PO-0702 PO not pending approval
Cause: approve or reject was attempted on an order not in PA. Remedy: refresh the inbox; someone else may have acted on it.

### 17.14 ERR-PO-0801 PO closed
Cause: amendment or cancellation was attempted on an order in CN, RJ or CL. Remedy: none; raise a new order if needed.

### 17.15 ERR-PO-0001 PO not found
Cause: no order with that number. Remedy: check the number with Ctrl+F or the order list.

### 17.16 ERR-SUP-0030 Supplier not found
Cause: no supplier with that code. Remedy: use F2 on the supplier field, or search on PUR-SUP-03.

### 17.17 ERR-SUP-0031 Supplier not active
Cause: the supplier is BLOCKED. Remedy: use the supplier's active code; a blocked old code usually has a replacement (see §5.3).

### 17.18 ERR-SUP-0118 VAT number already registered
Cause: a supplier with this VAT number already exists. Remedy: search for it and use the existing code; do not create a second record.

### 17.19 ERR-ITM-0010 Item not found and ERR-ITM-0011 Item not found or inactive
Cause: the item code does not exist, or the item is inactive. Remedy: use item enquiry (Chapter 3) to find an active item.

### 17.20 ERR-CC-0009 Cost centre not found
Cause: no cost centre with that code. Remedy: press F2 in the Cost centre field for the list.

### 17.21 ERR-BUD-0207 Budget exceeded
Cause: the gross value is more than the cost centre's budget available for the quarter. Remedy: ask the cost centre owner which cost centre to charge, or ask Finance for a budget transfer.

### 17.22 ERR-TAX-0101 Invalid tax code
Cause: the tax code does not exist. Remedy: press F2 in the Tax code field.

### 17.23 ERR-APR-0003 Self approval not allowed
Cause: an approver tried to approve a document they raised. Remedy: the document must be approved by someone else.

### 17.24 ERR-APR-0004 Value above your limit
Cause: the document's value is above the approver's limit. Remedy: Ledgerline routes documents to the right approver on submit; if you see this, the document was opened from the wrong inbox.

### 17.25 ERR-APR-0009 No approver found
Cause: nobody in the approver's management line has a limit that covers the value. Remedy: follow your company's procedure for approvals above the highest limit in Ledgerline.

### 17.26 ERR-SEC-0001 Not authorised
Cause: your role does not allow this screen or action. Remedy: ask your manager; IT changes roles only on a written request.

### 17.27 ERR-SEC-0002 Invalid credentials
Cause: wrong user ID or password. After three attempts the user ID is locked (§2.1).

### 17.28 ERR-PR-0007 and ERR-PR-0008 Request not in the right status
Cause: ERR-PR-0007 means a request was submitted that is not in Draft; ERR-PR-0008 means an approval was attempted on a request that is not pending. Remedy: refresh and check the request's status.

## 18. Notifications

### 18.1 E-mails Ledgerline sends
Ledgerline e-mails the approver when a request or order is waiting for approval, the raiser when a request is rejected, and the supplier when an order is released. It does not e-mail anyone when an order is saved as Draft.

### 18.2 Sending a note from Ledgerline
The Notify button on any document sends a short e-mail or SMS with the document number to a user or supplier. Notes sent this way are logged against the document.

## 19. Troubleshooting

### 19.1 The order saved, but the supplier never received it
Check the order's status (Ctrl+F, then the order number). If it is DR, the cost centre was probably closed; see §17.6 and §14.4. If it is PA, it is waiting for the approver. If it is AP, it was approved but never released; release it (Chapter 13). Only RL orders reach the supplier.

### 19.2 The rate on my order is different from last time
Fetch takes the rate from the current rate contract (§7.2). A new contract may have started since the last order. Old orders' rates are history.

### 19.3 I cannot find a supplier the requester named
Search on one short word of the name (§5.2), check the city, and compare VAT numbers. Suppliers are often called by short or slightly different names.

### 19.4 The screen hung after I pressed Save
Do not press Save again. Wait one minute, then search for the order (Purchase, Order list) by supplier, item and today's date, or by client reference. If the order exists, the Save worked; continue from it. Pressing Save again creates a second order.

### 19.5 The approver cannot see my document
Check that it was submitted (status PA, not DR). Approvers see only documents routed to them; a document above their limit goes to the next person up.

## 20. Keyboard and lookup reference

### 20.1 F2 lookups by field
F2 opens these lookups: Item code (item search, active items only), Supplier code (supplier search, active suppliers first), Cost centre (all cost centres with their status), Warehouse (warehouses of your organisation unit), Tax code (all tax codes with their region), Payment terms (all payment terms), Source PR (approved requests not yet converted), Rate (rate history for the supplier and item).

### 20.2 Lookup tips
In a lookup window, type to filter the list, use the arrow keys to move and Enter to select. Esc closes the lookup without changing the field.

## 21. Glossary

### 21.1 Terms
Basic value: quantity times rate, before tax. Gross value: basic value plus VAT. Cost centre: the budget unit a purchase is charged to. Fetch: the button that fills defaults from the masters. Rate contract: an agreed price for a period. Release: sending an approved order to the supplier. Organisation unit: a plant or unit with its own address and state, for example NBC-MAN-01. Client reference: a reference your integration may store on an order so it can find the order again.

## 22. Reports

### 22.1 Running a report
Reports are under the Reports menu. Each report has a parameter window; fill it and press F8 to run. Results open in a grid that can be exported to a spreadsheet with Ctrl+E. Reports read the database at the moment they run.

### 22.2 Open orders by supplier
Lists every order in status AP or RL that has not been fully received, grouped by supplier, with the quantity outstanding and the need-by date. Parameters: supplier (optional), need-by from and to.

### 22.3 Orders pending approval
Lists every request and order in status PA with the approver and the number of days waiting. Purchase managers use it to chase approvals before month end.

### 22.4 Draft orders
Lists every order in status DR with its warning code. Run it every morning: a Draft order has not reached the supplier, and nobody is told when an order is saved as Draft.

### 22.5 Price variance
Compares the rate on each released order with the rate contract that covered its date, and lists orders whose rate differs by more than a tolerance you enter.

### 22.6 Certificate expiry
Lists supplier certificates whose valid-to date falls within a number of days you enter, by certificate type. Use it to ask suppliers for renewed certificates in good time.

### 22.7 Budget utilisation
Lists each cost centre's budget, committed amount and budget available for a quarter. Finance owns the figures; the report reads them as they stand when it runs.

### 22.8 Supplier performance
Lists, per supplier, orders released, deliveries on time and rejections in a period. Quality enters rejections on the goods-inspection screen, which is outside this manual.

## 23. Notes for key users and administrators

### 23.1 Users and roles
IT creates users on the security console (outside this manual) and assigns one role each. The role decides which screens appear in the navigation tree and which services the user may call. The approval limit is stored on the user, not the role, and is set from the company's approval matrix.

### 23.2 Service accounts
Integrations call Ledgerline's services with a service account. A service account's role decides what it can call. Ledgerline treats a service account like any other user: it applies the account's own approval limit and records the account as the creator of documents. Companies should give service accounts only the services they need.

### 23.3 Default cost centres
Each user's default cost centre is set by IT on the user record and is used by Fetch. Review defaults when Finance closes cost centres; Ledgerline does not update them.

### 23.4 Configurable limits
The direct-order limit (§11.7) is a company setting, maintained by IT on the purchasing parameters screen. Changing it takes effect at the next sign-in of each user.

### 23.5 The audit trail
Every service call is written to the audit trail with the time, user, service, payload, return code and error code. The audit trail cannot be edited from any screen.

## 24. Moving from Ledgerline 6.x

### 24.1 What changed
Ledgerline 7 replaced the single order screen of 6.x with separate entry, approval and release screens, added the Fetch requirement, and moved approval limits from roles to users. Supplier codes migrated from 6.x keep their old format and show MIGRATION as the creator.

### 24.2 Migrated documents
Orders migrated from 6.x appear with status RL or CL only. Their rates and tax codes are as they were in 6.x and are not recalculated.
