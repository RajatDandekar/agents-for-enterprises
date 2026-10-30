---
title: Items and Inventory Enquiry
audience: all Ledgerline users
sources: MAN-DD-72 §3.1, MAN-DD-72 §3.2, MAN-DD-72 §3.4, MAN-DD-72 §3.5, MAN-DD-72 §3.6, MAN-PUR-72 §3.1, MAN-PUR-72 §3.2, MAN-PUR-72 §3.3, MAN-PUR-72 §3.4, MAN-PUR-72 §3.5, MAN-PUR-72 §4.1, MAN-PUR-72 §4.2, MAN-PUR-72 §4.3, MAN-PUR-72 §4.4, MAN-PUR-72 §4.5
compiled_by: gemini:gemini-3.8-flash
---

# Items and Inventory Enquiry

Item enquiry (INV-ITM-03) lets you locate item codes, descriptions, and master details before raising purchase requests or orders. Stock enquiry (INV-STK-02) provides real-time warehouse quantities, stock ledgers, and days of cover calculations. Buyers can also view replenishment needs across warehouses using the reorder report.

## Rules

- Use Item enquiry to locate exact item codes in the item master before raising a request or order [MAN-PUR-72 §3.1].
- Find items by entering any part of the description or code in Search text and pressing Enter [MAN-PUR-72 §3.2].
- Search terms ignore case and spaces, and `%` can be used as a wildcard in the middle of a word [MAN-PUR-72 §3.2].
- The search screen displays up to 20 rows; refine your search if the required item does not appear [MAN-PUR-72 §3.2].
- The results list displays the item code, description, unit of measure (UOM), and active status [MAN-PUR-72 §3.3].
- Open the item master view by double-clicking a row or pressing Enter on a selected item [MAN-PUR-72 §3.4].
- The item master view displays the category (RAW, COMPONENTS, SPARES, or PACKING), reorder level, average daily issue, and lithium-cell flag [MAN-DD-72 §3.4, MAN-PUR-72 §3.4].
- Press F2 inside any Item code field across other screens to open the lookup window, then press Enter to copy the selected code [MAN-PUR-72 §3.5].
- On Stock enquiry (INV-STK-02), the Item code field is mandatory, while the Warehouse field is optional [MAN-PUR-72 §4.2].
- Leave the Warehouse field blank in Stock enquiry to view stock across all warehouses [MAN-PUR-72 §4.2].
- View stock figures directly on screen at the moment you need them because values change throughout the day as stores issue and receive material [MAN-PUR-72 §4.1].
- In the stock enquiry results, "On hand" shows physical stock, "Allocated" shows reservations for production orders, and "On order" shows quantities on released purchase orders not yet received [MAN-PUR-72 §4.3].
- Days of cover is calculated as on-hand stock divided by the item's average daily issue, rounded down [MAN-DD-72 §3.6, MAN-PUR-72 §4.3].
- Click the Ledger button in Stock enquiry to view a read-only list of all receipts and issues for the item, ordered newest first [MAN-PUR-72 §4.4].
- Stock ledger corrections must be made by stores using a stock adjustment requiring stores manager approval [MAN-PUR-72 §4.4].
- Access the reorder list via Reports, then Items below reorder level, to identify items where on-hand plus on-order stock is below the reorder level [MAN-DD-72 §3.6, MAN-PUR-72 §4.5].

## Watch out

- Inactive items (active flag set to 0) appear in grey and cannot be added to new requests or orders [MAN-DD-72 §3.5, MAN-PUR-72 §3.3].
- Do not order item codes ending in `-R` (such as example `BAT-500-R`); these are rework items used strictly by Quality [MAN-PUR-72 §3.3].
- The lithium-cell flag is maintained solely by Quality for parts that contact food during use [MAN-PUR-72 §3.4].
- Do not paste stock figures into emails or documents as permanent numbers because warehouse quantities change constantly [MAN-PUR-72 §4.1].

## Related

- [[purchase-requests]] Purchase Requests (PR)
- [[purchase-orders]] Purchase Order Entry and Rules
- [[battery-safety-compliance]] Food-Grade Compliance and Certificates
- [[erp-conventions-and-navigation]] Ledgerline ERP Interface and Navigation
- [[data-dictionary-and-standards]] Ledgerline ERP Data Standards and Statuses
- [[purchasing-reports]] Purchasing Reports and Analytics
