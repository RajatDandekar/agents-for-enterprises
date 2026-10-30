---
title: Ledgerline ERP Interface and Navigation
audience: all Ledgerline users
sources: MAN-PUR-72 §1.1, MAN-PUR-72 §1.2, MAN-PUR-72 §1.3, MAN-PUR-72 §1.4, MAN-PUR-72 §1.5, MAN-PUR-72 §2.1, MAN-PUR-72 §2.2, MAN-PUR-72 §2.3, MAN-PUR-72 §2.4, MAN-PUR-72 §2.5, MAN-PUR-72 §2.6, MAN-PUR-72 §2.7, MAN-PUR-72 §18.1, MAN-PUR-72 §18.2, MAN-PUR-72 §20.1, MAN-PUR-72 §20.2
compiled_by: gemini:gemini-3.8-flash
---

# Ledgerline ERP Interface and Navigation

Ledgerline ERP provides standard screens, keyboard shortcuts, and lookup tools for purchasing tasks. Users log in through the desktop client and can navigate permitted screens, manage documents, and send direct notifications. Always check the status bar for system messages after saving your work.

## Rules
- Start the Ledgerline client from the desktop icon, enter your user ID and password, and choose your organisation unit [MAN-PUR-72 §2.1].
- Passwords must be at least eight characters, include a digit, and be changed every 90 days via File > Change password [MAN-PUR-72 §2.6].
- Enter codes in capitals or lower case (the system converts lower case to capitals), enter dates as DD-MM-YYYY, and fill all mandatory fields marked with a red asterisk (*) [MAN-PUR-72 §1.3].
- Open screen lookups by pressing F2 or clicking the small F2 button beside a field [MAN-PUR-72 §1.3].
- Press F2 to open lookups for Item code, Supplier code, Cost centre, Warehouse, Tax code, Payment terms, Source PR, and Rate [MAN-PUR-72 §20.1].
- In a lookup window, type to filter the list, navigate with the arrow keys, press Enter to select, or press Esc to exit without changing the field [MAN-PUR-72 §20.2].
- Use the standard function keys to work across screens: F3 to fetch defaults, F5 to refresh from the database, F7 to clear the screen, F8 to save, F9 to submit or release, F10 to access the menu bar, Ctrl+F to find a document by number, and Ctrl+P to print [MAN-PUR-72 §2.5].
- Read the status bar at the bottom after every save; red messages starting with ERR- are errors, and black messages starting with W- are warnings [MAN-PUR-72 §1.3, MAN-PUR-72 §2.3].
- Print documents using Ctrl+P to output to the default printer in your company's layout [MAN-PUR-72 §2.7].
- Click the Notify button on any document to send a logged e-mail or SMS containing the document number to a user or supplier [MAN-PUR-72 §18.2].
- Quote the screen code shown at the right of the title bar (such as PUR-PO-01) whenever you raise a support ticket [MAN-PUR-72 §1.4].

## Watch out
- Entering three wrong passwords locks your user ID for 30 minutes unless IT unlocks it sooner [MAN-PUR-72 §2.1].
- Sessions idle for 20 minutes automatically close; unsaved data is lost because Ledgerline does not retain half-filled screens across sessions, so save as Draft where available [MAN-PUR-72 §2.4].
- Grey fields are read-only and fill automatically via Fetch or upon saving [MAN-PUR-72 §1.3].
- Screens shown in grey in the navigation tree are installed but not permitted for your user role [MAN-PUR-72 §2.2].
- Ledgerline does not display pop-up dialogues for most messages, so you must check the status bar directly [MAN-PUR-72 §2.3].
- A purchase order printed before it reaches Released status will show the word DRAFT across the page [MAN-PUR-72 §2.7].
- Saving an order as Draft does not trigger an automated email to anyone [MAN-PUR-72 §18.1].

## Related
- [[error-codes-reference]] System Error Codes and Troubleshooting
- [[data-dictionary-and-standards]] Ledgerline ERP Data Standards and Statuses
- [[purchase-orders]] Purchase Order Entry and Rules
- [[purchase-requests]] Purchase Requests (PR)
- [[po-release-and-lifecycle]] PO Release, Amendments, and History
