# HR · leave: data dictionary

Prefix `lv_` for services, `sp_lv_` for stored procedures, `lv_` for tables. Every reply comes in the legacy envelope `{rc, err_cd, msg, data}`; rc is S, W or E.

## Services

| Service | Legacy name | Kind | Screen | Fields (* = mandatory) |
|---|---|---|---|---|
| `lv_emp_get` | EMPLOYEE GET | read | HR-LV-01 | user_id:str, q:str |
| `lv_bal_get` | LEAVE BALANCE | read | HR-LV-01 | emp_cd*:str, yr:int |
| `lv_hol_list` | HOLIDAY LIST | read | HR-LV-01 | ou_cd:str |
| `lv_fetch` | LEAVE DEFAULTS | read | HR-LV-02 | emp_cd*:str, lv_cd*:str |
| `lv_save` | LEAVE APPLY | write | HR-LV-02 | emp_cd*:str, lv_cd*:str, from_dt*:date, to_dt*:date, half:str, reason*:str, ref_dt:date, fwd_to:str, fetch_tok:str, client_ref:str |
| `lv_list` | LEAVE LIST | read | HR-LV-04 | lv_no:str, emp_cd:str, status:str, approver:str, client_ref:str |
| `lv_approve` | LEAVE APPROVE | write | HR-LV-04 | lv_no*:str, decision*:str, comment:str |
| `lv_hr_clear` | HELD LEAVE CLEAR | write | HR-LV-04 | lv_no*:str, decision*:str, comment:str |
| `lv_cancel` | LEAVE CANCEL | write | HR-LV-02 | lv_no*:str, reason*:str |

## Tables

- **lv_emp** (10 seed rows): emp_cd, user_id, name, dept, ou_cd, doj, lv_appr, shift
- **lv_type** (5 seed rows): lv_cd, descr, ent_yr, notice_days, max_run, paid
- **lv_bal** (22 seed rows): emp_cd, lv_cd, yr, opening, availed, pending
- **lv_hol** (9 seed rows): hol_dt, descr, ou_cd
- **lv_cof** (3 seed rows): emp_cd, worked_dt, valid_to, status, used_by
- **lv_app** (6 seed rows): lv_no, emp_cd, lv_cd, from_dt, to_dt, half, days, lwp_days, reason, ref_dt, status, applied_by, applied_on, approver, decided_on, warn_cd, client_ref
- **lv_roster** (0 seed rows): emp_cd, dt, code, ref
- **lv_pay_feed** (0 seed rows): emp_cd, period, lwp_days, ref, posted_on

## Field meanings

| Field | Meaning |
|---|---|
| `emp_cd` | Employee code (E-1042 is Emma). Not the same as the Ledgerline user id. |
| `lv_cd` | Leave type: CL casual, EL earned, SL sick, CO compensatory off, LWP leave without pay. |
| `from_dt / to_dt` | First and last date of the leave, inclusive. Sundays and plant holidays are not counted. |
| `half` | 1H = first half, 2H = second half. Only when from_dt = to_dt. |
| `ref_dt` | For CO only: the holiday the employee worked, which earned the comp-off. |
| `fwd_to` | FWD TO: sends the application to this approver instead of the default leave approver. |
| `fetch_tok` | Token from Fetch (lv_fetch). Save without it fails with ERR-SCR-0221. |
| `days / lwp_days` | Working days applied for, and how many of them are without pay. |
| `lv_appr` | The employee's default leave approver (user id). |
| `client_ref` | Free text the caller can use as an idempotency key. |

## Status codes

**PA** pending approval · **HD** held for HR (part of it is unpaid; never reaches the manager until HR clears it) · **AP** approved · **RJ** rejected or returned · **CN** cancelled

## Error and warning codes

| Code | Meaning |
|---|---|
| ERR-LV-0001 | employee not found |
| ERR-LV-0002 | emp code mandatory |
| ERR-LV-0003 | not your employee code |
| ERR-LV-0102 | to date before from date |
| ERR-LV-0104 | no working days in range |
| ERR-LV-0105 | from date in past |
| ERR-LV-0201 | invalid leave type |
| ERR-LV-0215 | not enough notice for this leave type |
| ERR-LV-0217 | longer than this type allows at a stretch |
| ERR-LV-0301 | overlaps another application |
| ERR-LV-0410 | FWD TO user not found |
| ERR-LV-0501 | application not found |
| ERR-LV-0502 | not pending |
| ERR-LV-0504 | not your approval |
| ERR-LV-0505 | not held |
| ERR-LV-0507 | already closed |
| ERR-LV-0508 | leave already started |
| ERR-LV-0611 | half day only for a single date |
| ERR-LV-0612 | half must be 1H/2H |
| ERR-LV-0620 | comp-off needs the worked date |
| ERR-LV-0621 | no open comp-off for that date |
| ERR-LV-0622 | worked date only for comp-off |
| W-LV-118 | part of the leave saved as unpaid; held for HR |
| ERR-SCR-0221 | Save without Fetch |
| ERR-APR-0003 | self approval |
