# Purchasing · amend PO: data dictionary

Prefix `pa_` for services, `sp_pa_` for stored procedures, `pa_` for tables. Every reply comes in the legacy envelope `{rc, err_cd, msg, data}`; rc is S, W or E.

## Services

| Service | Legacy name | Kind | Screen | Fields (* = mandatory) |
|---|---|---|---|---|
| `pa_po_list` | PO LIST (RELEASED) | read | PUR-POL-07 | sup_cd:str, itm_cd:str, status:str, q:str |
| `pa_po_get` | PO GET WITH REVISIONS | read | PUR-POL-07 | po_no*:str |
| `pa_sched_get` | DELIVERY SCHEDULE | read | PUR-POL-07 | po_no*:str |
| `pa_amd_fetch` | AMENDMENT DEFAULTS | read | PUR-POM-08 | po_no*:str |
| `pa_amd_save` | AMENDMENT SAVE | write | PUR-POM-08 | po_no*:str, amd_type:str, qty:int, need_dt:date, reason_cd*:str, remarks:str, s1_dt:date, s1_qty:int, s2_dt:date, s2_qty:int, fetch_tok:str, client_ref:str |
| `pa_sched_save` | AMENDMENT SCHEDULE SAVE | write | PUR-POM-08 | amd_no*:str, s1_dt*:date, s1_qty*:int, s2_dt:date, s2_qty:int |
| `pa_amd_list` | AMENDMENT LIST | read | PUR-POA-09 | amd_no:str, po_no:str, status:str, approver:str, raised_by:str, client_ref:str |
| `pa_amd_approve` | AMENDMENT APPROVE | write | PUR-POA-09 | amd_no*:str, decision*:str, comment:str |
| `pa_amd_release` | AMENDMENT RELEASE | write | PUR-POM-08 | amd_no*:str |

## Tables

- **pa_lead** (8 seed rows): sup_cd, lead_days, remarks
- **pa_reason** (7 seed rows): reason_cd, descr
- **pa_sched** (13 seed rows): po_no, sl_no, dlv_dt, qty, rcvd_qty, status, amd_no
- **pa_rcpt** (9 seed rows): grn_no, po_no, sl_no, rcpt_dt, qty, recd_by
- **pa_amd** (9 seed rows): amd_no, po_no, rev, amd_type, old_qty, new_qty, old_dt, new_dt, old_gross, new_gross, reason_cd, remarks, need_appr, status, raised_by, raised_on, approver, approved_by, decided_on, released_on, warn_cd, client_ref

## Field meanings

| Field | Meaning |
|---|---|
| `po_no` | Purchase order number, e.g. PO/2026/01182 (Emma's 20,000 battery packs). |
| `amd_no` | Amendment number, e.g. AMD/2026/00031. One amendment = one revision of a released order. |
| `amd_type` | REV = revise quantity and/or dates. SCL = short-close: cancel the undelivered balance. |
| `qty` | The NEW total order quantity (not the change). It may not go below what has been received. |
| `need_dt` | The NEW need-by date. It must be the date of the last delivery line. |
| `s1_dt / s1_qty, s2_dt / s2_qty` | Up to two new delivery lines for the undelivered quantity. Left blank, Ledgerline keeps the old lines. |
| `reason_cd` | PLAN, SUPP, STCK, QLTY, DUPL or OTHR (pa_reason). |
| `rcvd_qty` | Quantity already received against the order (from the goods receipts in pa_rcpt). |
| `rev` | Revision number of the order; the supplier gets each revision when it is released. |
| `need_appr` | Y when the change needed re-approval (cut > 20%, moved > 5 days, or value up beyond the raiser's limit). |
| `fetch_tok` | Token from Fetch (pa_amd_fetch). Save without it fails with ERR-SCR-0221. |
| `client_ref` | Free text the caller can use as an idempotency key. |

## Status codes

**HD** held: the delivery schedule does not add up to the new quantity and date; not routed, supplier not told · **PA** pending re-approval · **AP** approved, not yet released to the supplier · **RL** released: the order is changed and the supplier has the revision · **RJ** rejected · **schedule OP/RC/PR/SU/CN** open, received, proposed by an amendment, superseded, cancelled (short-closed)

## Error and warning codes

| Code | Meaning |
|---|---|
| ERR-PO-0001 | order not found |
| ERR-PA-0102 | order not released (unreleased orders use PUR-POM-06, po_amend) |
| ERR-PA-0105 | another amendment of this order is still open |
| ERR-PA-0201 | invalid reason code |
| ERR-PA-0301 | quantity must be above zero |
| ERR-PA-0310 | quantity below the quantity already received |
| ERR-PA-0320 | delivery date nearer than the supplier's lead time |
| ERR-PA-0331 | schedule line needs date and qty |
| ERR-PA-0415 | cost centre closed, value cannot go up |
| ERR-PA-0501 | amendment not found |
| ERR-PA-0502 | amendment not pending |
| ERR-PA-0503 | schedule locked (only a held amendment's schedule can change) |
| ERR-PA-0504 | not your approval |
| ERR-PA-0601 | type must be REV or SCL |
| ERR-PA-0602 | nothing to amend |
| ERR-PA-0611 | short-close cannot change the date |
| ERR-PA-0612 | short-close quantity must equal received |
| ERR-PA-0613 | short-close cannot carry a schedule |
| ERR-PA-0614 | nothing received: cancel the order instead |
| ERR-PA-0715 | amendment not approved, cannot release |
| W-SCH-209 | schedule mismatch, amendment held |
| ERR-SCR-0221 | Save without Fetch |
| ERR-APR-0003 | self approval |
| ERR-APR-0004 | value above approver's limit |
