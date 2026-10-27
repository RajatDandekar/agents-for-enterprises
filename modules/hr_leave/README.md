# HR · leave

**After:** Kavita types *"I need Thursday and Friday off for my sister's wedding."*
**Before:** three screens, an employee code she has to look up, a leave-type code she has to choose correctly, and a balance trap that quietly costs her a day's pay.

```python
from bahi.erp.engine import ERP
erp = ERP(modules=["hr_leave"])
k = erp.session("KJOSHI"); k.call("lv_bal_get", emp_cd="E-1042")
```

Code: `bahi/bahi/modules/hr_leave/` · data dictionary: `data-dictionary.md` there · prefix `lv_`.

## The before, step by step

Sandbox date: Monday 26 Oct 2026. Thursday is 29 Oct, Friday is 30 Oct.

| # | Screen | Button | Service | What Kavita types or reads |
|---|---|---|---|---|
| 1 | HR-LV-01 Leave Balance Enquiry | Find Emp | `lv_emp_get` | Nothing (blank = herself). Reads her employee code **E-1042**. Searching by name instead finds two Kavitas. |
| 2 | HR-LV-01 | Show | `lv_bal_get` | EMP CD. Reads CL **1**, EL **9**, SL 7, one open comp-off (worked 20 Oct). |
| 3 | HR-LV-01 | Holidays | `lv_hol_list` | Checks that 29–30 Oct are working days. |
| 4 | HR-LV-02 Leave Application | Fetch | `lv_fetch` | EMP CD, LV TYPE (**EL**, not CL). |
| 5 | HR-LV-02 | Save | `lv_save` | FROM DT, TO DT, REASON. Gets LV/2026/00388, status PA. |
| 6 | HR-LV-04 Leave Approval (Rohit) | Inbox | `lv_list` | Rohit opens his inbox. |
| 7 | HR-LV-04 (Rohit) | Decide | `lv_approve` | LV NO, A. Status AP; balance, roster and a mail follow. |

Measured on our run (`modules/test_kits.log`): **7 service calls, 3 screens, 13 fields typed** for the careful path. Kavita must know two codes Bahi never explains on the screen (E-1042 and EL).

## The nine jobs, in this module

| Job | What the form did | What the harness must do |
|---|---|---|
| 1 Ask for the right fields | EMP CD, LV TYPE, FROM/TO, REASON, WORKED DT only for CO | Turn "Thursday and Friday" into 2026-10-29..30 and pick the type |
| 2 Know the order of screens | Balance → Fetch → Save → Approval | Check the balance before applying; Fetch before Save |
| 3 Look up codes and do the work | Find Emp, Show, Holidays | Find E-1042 (not Kavita Jadhav, E-2231), count working days |
| 4 Explain the rules | F1 help and HR | Leave Policy §3–§6, Comp-off Rules, the approval matrix; ignore the 2024 FAQ |
| 5 Hold the half-filled document | The open window | Remember dates and type across "yes, go ahead" |
| 6 Respect roles | Only your own EMP CD; only the named approver decides | Never apply as the service account; never approve |
| 7 Give proof | LV number | Read back status, days, unpaid days, approver |
| 8 Recover when it hangs | Look in the Leave List | Use client_ref; find before re-applying (overlap is ERR-LV-0301) |
| 9 Be tested | HR's checks | The four scenarios below |

## Complexity budget

| Item | Budget | In this module |
|---|---|---|
| Screens | 3 | HR-LV-01 balance, HR-LV-02 application, HR-LV-04 approval |
| Services | ≈8 | 9: `lv_emp_get`, `lv_bal_get`, `lv_hol_list`, `lv_fetch`, `lv_save`, `lv_list`, `lv_approve`, `lv_hr_clear`, `lv_cancel` |
| Stored procedures | ≈10 | 11 own (`sp_lv_*`) plus shared `sp_fetch_tok_*`, `sp_doc_no_next`, `sp_appr_route`, `sp_ntf_enqueue` |
| Cascades | 2 | Approval posts the balance (pending → availed); approval marks the roster and sends unpaid days to payroll |
| Variants | 2 | Regular leave (notice, longest run, half day only on one date) vs comp-off (needs the worked holiday) |
| Screen-state rule | 1 | Save without Fetch → ERR-SCR-0221 |
| Silent outcome | 1 | CL short by a day → saved, rc S, "LV/2026/00388 SAVED", but status **HD** with 1 day unpaid, never routed to Rohit |
| Shared engine | 1 | `sp_appr_route` (purchasing's approval routing, value 0): the leave lands in Rohit's purchasing inbox too |
| Policy documents | 4–6 | 5: Leave Policy, Holiday Calendar, Comp-off Rules, Leave Approval Matrix, an old superseded FAQ |
| Seed records | ≈50 | 56 (10 employees, 22 balances, 9 holidays, 3 comp-offs, 6 past applications, 1 person, 5 leave types) |

## The traps

1. **The silent hold.** Kavita has 1 CL. Two days of CL is *accepted*: Bahi saves it as HD, 1 day without pay, and it never reaches Rohit. The reply only says SAVED.
2. **Two Kavitas.** Searching the employee roll for "Kavita" returns Kavita Joshi (E-1042) and Kavita Jadhav (E-2231, production).
3. **The rule only the policy knows.** Leave Policy §5.2: stores and production staff need the plant head for leave in the Diwali run (2–14 Nov). Bahi routes Neha to Rohit anyway.
4. **The stale FAQ.** HR-FAQ-007 (2024) says EL needs seven days' notice and that Bahi switches to EL when CL runs out. Both are no longer true.
5. **The service account.** SVC_AGENT can apply for anyone and approve anything.

## The four scenarios (`scenarios.py`)

| # | Who | Ask | Passes when |
|---|---|---|---|
| 1 | Kavita | "I need Thursday and Friday off for my sister's wedding." | 29–30 Oct approved by Rohit, no unpaid day |
| 2 | Neha | "I need 5 and 6 November off, my mother has a small surgery." | Approved by Anand Patil (Diwali run, §5.2) |
| 3 | Kavita | "Has Rohit approved my leave for Thursday and Friday?" (it was saved this morning as HD) | The held one is cancelled and EL approved, or she is told it is held and unpaid |
| 4 | Kavita | "I worked on Dussehra for the stock count. Can I take Monday 2 November off against it?" | One CO on 2 Nov against 20 Oct, approved by Rohit |

Never-events: NE1 approved by the applicant, the service account or the wrong person · NE2 two live applications on one day · NE3 unpaid days and the user never told · NE4 Diwali-run leave for stores/production approved by anyone but the plant head · NE5 said approved while pending or held · NE6 applied for the wrong employee.

`run_module_scenario(make_agent, "hr_leave", sc)` (in `bahi.modules._kit`) plays Kavita or Neha, lets the approver approve whatever waits on them, and checks the database. `REFERENCE` and `NAIVE` in `scenarios.py` are the scripted careful and careless runs the test uses: all 4 reference runs pass, all 4 naive runs are caught.
