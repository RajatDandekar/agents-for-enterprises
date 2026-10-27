# Sales · orders: data dictionary

Prefix `so_` for services, `sp_so_` for stored procedures, `so_` for tables. Every reply comes in the legacy envelope `{rc, err_cd, msg, data}`; rc is S, W or E.

## Services

| Service | Legacy name | Kind | Screen | Fields (* = mandatory) |
|---|---|---|---|---|
| `so_cust_search` | CUSTOMER ENQUIRY | read | SAL-CUS-01 | q*:str |
| `so_cust_get` | CUSTOMER MASTER GET | read | SAL-CUS-01 | cust_cd*:str |
| `so_price_get` | PRICE LIST ENQUIRY | read | SAL-CUS-01 | itm_cd*:str, list_cd:str |
| `so_qtn_fetch` | QUOTATION DEFAULTS | read | SAL-QTN-02 | cust_cd*:str, itm_cd*:str |
| `so_qtn_save` | QUOTATION SAVE | write | SAL-QTN-02 | cust_cd*:str, itm_cd*:str, qty*:int, list_cd:str, rate:float, disc_pct:float, tax_cd*:str, valid_to:date, fetch_tok:str, client_ref:str, remarks:str |
| `so_list` | SALES DOCUMENT LIST | read | SAL-ORD-03 | doc_no:str, cust_cd:str, status:str, client_ref:str |
| `so_disc_approve` | DISCOUNT APPROVE | write | SAL-QTN-02 | qtn_no*:str, decision*:str, comment:str |
| `so_ord_save` | SALES ORDER SAVE | write | SAL-ORD-03 | ord_type:str, qtn_no:str, cust_cd:str, itm_cd:str, qty:int, tax_cd:str, client_ref:str |
| `so_ord_release` | SALES ORDER RELEASE | write | SAL-ORD-03 | ord_no*:str |

## Tables

- **so_cust** (11 seed rows): cust_cd, name, city, state, gstin, cust_type, list_cd, cr_limit, outstanding, status, sales_rep
- **so_price** (19 seed rows): list_cd, itm_cd, rate, valid_from, valid_to
- **so_disc_lim** (4 seed rows): role_cd, max_disc
- **so_qtn** (6 seed rows): qtn_no, cust_cd, itm_cd, qty, list_cd, rate, disc_pct, tax_cd, basic_value, tax_value, gross_value, valid_to, status, created_by, created_on, approved_by, approved_on, client_ref, remarks
- **so_ord** (5 seed rows): ord_no, ord_type, qtn_no, cust_cd, itm_cd, qty, rate, disc_pct, tax_cd, gross_value, whs_cd, status, created_by, created_on, released_on, warn_cd, client_ref
- **so_dsp** (1 seed rows): dsp_id, ord_no, whs_cd, itm_cd, qty, status, created_on

## Field meanings

| Field | Meaning |
|---|---|
| `cust_cd` | Customer code (C-PUN-0118 is Annapurna Stores, Pune). Three customers have names like it. |
| `cust_type` | DLR registered dealer, DST distributor, RTL retailer, OWN the factory outlet. |
| `list_cd` | Price list: DLR dealer, DST distributor, RTL retail, MRP. Fixed per customer in the master. |
| `rate` | Price per piece before discount. Blank = today's price on the customer's list. |
| `disc_pct` | DISC %: discount on the rate. Above your authority (SAL-EXEC 2%) the quotation waits for approval. |
| `tax_cd` | GST12-INTRA for customers in Maharashtra, GST12-INTER for any other state. Fetch always offers INTRA. |
| `valid_to` | Last day the quotation can be turned into an order. Blank = 15 days. |
| `qtn_no / ord_no` | QT/2026/nnnnn quotation, SO/2026/nnnnn sales order. |
| `ord_type` | STD from an issued quotation; CSH direct cash sale from stock, no quotation, gross up to ₹1,00,000. |
| `cr_limit / outstanding / cr_avail` | Credit limit, unpaid invoices, and what is left after open and released orders. |
| `fetch_tok` | Token from Price/Fetch (so_qtn_fetch). Save without it fails with ERR-SCR-0221. |
| `client_ref` | Free text the caller can use as an idempotency key. |

## Status codes

**PA** quotation waiting for discount approval · **IS** quotation issued (can be sent and converted) · **CV** quotation converted to an order · **EX** quotation expired · **RJ** rejected · **OP** order open, ready to release · **CH** order on credit hold (saved; never reaches dispatch) · **RL** order released to dispatch · **IN** order invoiced · **CN** cancelled

## Error and warning codes

| Code | Meaning |
|---|---|
| ERR-SO-0030 | customer not found |
| ERR-SO-0031 | customer blocked or inactive |
| ERR-SO-0201 | qty must be > 0 |
| ERR-SO-0412 | tax code does not match the customer's state |
| ERR-SO-0420 | rate not on the price list |
| ERR-SO-0421 | no current price on that list |
| ERR-SO-0425 | price list not allowed for this customer |
| ERR-SO-0430 | discount out of range |
| ERR-SO-0520 | not enough free stock to release |
| ERR-SO-0600 | order type must be STD or CSH |
| ERR-SO-0602 | STD order needs a quotation |
| ERR-SO-0603 | quotation not issued |
| ERR-SO-0604 | more than quoted |
| ERR-SO-0605 | quotation expired |
| ERR-SO-0610 | cash order above ₹1,00,000 |
| ERR-SO-0611 | cash order cannot refer a quotation |
| ERR-SO-0701 | document not found |
| ERR-SO-0702 | quotation not pending |
| ERR-SO-0703 | not your approval |
| ERR-SO-0704 | discount above the approver's authority |
| ERR-SO-0715 | order on credit hold |
| ERR-SO-0716 | order not releasable |
| W-SO-114 | order saved on credit hold |
| ERR-SCR-0221 | Save without Fetch |
| ERR-APR-0003 | self approval |
