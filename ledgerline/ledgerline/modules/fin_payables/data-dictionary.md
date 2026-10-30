# Finance · payables: data dictionary

Prefix `ap_` for services, `sp_ap_` for stored procedures, `ap_` for tables. Every reply comes in the legacy envelope `{rc, err_cd, msg, data}`; rc is S, W or E.

## Services

| Service | Legacy name | Kind | Screen | Fields (* = mandatory) |
|---|---|---|---|---|
| `ap_inv_list` | AP INVOICE LIST | read | FIN-AP-03 | sup_cd:str, sup_inv_no:str, status:str, hold_cd:str, po_no:str |
| `ap_inv_get` | AP INVOICE GET | read | FIN-AP-03 | ap_no*:str |
| `ap_match` | INVOICE MATCH | read | FIN-AP-01 | inv_type*:str, sup_cd*:str, po_no:str, qty:int, rate:float, amount:float, cc_cd:str |
| `ap_save` | INVOICE SAVE | write | FIN-AP-01 | inv_type*:str, sup_cd*:str, sup_inv_no*:str, inv_dt*:date, po_no:str, qty:int, rate:float, amount:float, tax_cd*:str, cc_cd:str, match_tok:str, client_ref:str |
| `ap_hold_refer` | HOLD REFER | write | FIN-AP-03 | ap_no*:str, hold_cd*:str, refer_to*:str, note:str |
| `ap_hold_release` | HOLD RELEASE | write | FIN-AP-03 | ap_no*:str, hold_cd*:str, reason*:str |
| `ap_approve` | AP APPROVE | write | FIN-AP-05 | doc_no*:str, decision*:str, comment:str |
| `ap_pay_sched` | PAYMENT PROPOSAL | write | FIN-AP-05 | ap_no*:str, pay_dt*:date, early_rsn:str, client_ref:str |
| `ap_pay_run` | PAYMENT RUN | write | FIN-AP-05 | run_dt*:date |

## Tables

- **ap_hold** (4 seed rows): hold_cd, descr, release_role
- **ap_vbank** (7 seed rows): sup_cd, msme, udyam_no, bank_ref
- **ap_grn** (5 seed rows): grn_no, po_no, itm_cd, qty_rcvd, qty_acc, grn_dt, whs_cd
- **ap_inv** (7 seed rows): ap_no, inv_type, sup_cd, sup_inv_no, inv_dt, po_no, qty, rate, basic, tax_cd, tax, gross, cc_cd, status, hold_cd, due_dt, entered_by, entered_on, approved_by, warn_cd, client_ref
- **ap_hold_log** (3 seed rows): id, ap_no, hold_cd, detail, put_on, released_by, released_on, reason
- **ap_pay** (1 seed rows): pay_no, ap_no, pay_dt, amount, status, early_rsn, sched_by, sched_on, approved_by, paid_on, warn_cd, client_ref
- **ap_run** (6 seed rows): run_dt, cutoff_dt, status
- **ap_ledger** (5 seed rows): id, sup_cd, dt, ref, dr, cr, narr
- **ap_gst** (4 seed rows): id, ap_no, vat_no, tax_cd, itc_amt, period, status

## Field meanings

| Field | Meaning |
|---|---|
| `ap_no` | Ledgerline's own invoice document number (AP/2026/03390). Not the supplier's number. |
| `sup_inv_no` | The number printed on the supplier's invoice (4471). Two suppliers can use the same number. |
| `inv_type` | PO = against a purchase order (three-way match); NPO = no order, e.g. a service (two-way, owner approves). |
| `po_no / qty / rate` | For PO invoices: the order, the quantity billed and the rate billed. |
| `amount` | For NPO invoices: the basic amount before VAT. |
| `tax_cd` | VAT code. Supplier in England: -INTRA (CGST+SGST); any other state: -INTER (IGST). |
| `cc_cd` | Cost centre. For NPO invoices it must be open; its owner approves. |
| `match_tok` | Token from Match (ap_match). Save without it fails with ERR-SCR-0221. |
| `hold_cd` | Why the invoice cannot be paid: H-PRC price, H-QTY quantity, H-GRN no receipt, H-DUP looks like a duplicate. |
| `refer_to` | The user asked to decide a hold (must be allowed to release that hold). |
| `due_dt` | Invoice date + the supplier's payment term days (N45 = 45 days). |
| `pay_dt` | The payment-run Friday the invoice should be paid in (see ap_run). |
| `early_rsn` | Reason for paying before the due date. With it the proposal goes to the controller; without it, it is parked. |
| `client_ref` | Free text the caller can use as an idempotency key. |

## Status codes

**HD** invoice on hold · **PA** waiting for approval (NPO invoice or early payment) · **PO** invoice posted, clear to pay · **PD** paid · **RJ** rejected · **CN** cancelled · **PK** payment parked: early with no reason; in no run and nobody is told · **SC** payment scheduled in a run

## Error and warning codes

| Code | Meaning |
|---|---|
| ERR-AP-0001 | AP document not found |
| ERR-AP-0031 | supplier not active |
| ERR-AP-0103 | invoice date in future |
| ERR-AP-0118 | this supplier invoice number is already entered |
| ERR-AP-0201 | PO invoice needs PO, qty and rate |
| ERR-AP-0205 | PO belongs to another supplier |
| ERR-AP-0206 | PO not released |
| ERR-AP-0211 | NPO invoice cannot refer a PO |
| ERR-AP-0212 | NPO invoice needs amount and cost centre |
| ERR-AP-0213 | cost centre closed |
| ERR-AP-0301 | invalid hold code |
| ERR-AP-0302 | hold not open |
| ERR-AP-0305 | you may not release this hold |
| ERR-AP-0306 | the person referred to cannot release this hold |
| ERR-AP-0402 | nothing pending for this document |
| ERR-AP-0404 | not your approval |
| ERR-AP-0410 | invoice not clear for payment |
| ERR-AP-0412 | not a payment-run date |
| ERR-AP-0413 | run cut-off passed |
| ERR-AP-0415 | payment already proposed |
| ERR-AP-0520 | run date in future |
| ERR-AP-0521 | run already done |
| ERR-PO-0412 | tax code does not match supplier state (shared tax engine) |
| ERR-SCR-0221 | Save without Match |
| ERR-APR-0003 | self approval |
| W-AP-311 | early payment parked (no reason given) |
