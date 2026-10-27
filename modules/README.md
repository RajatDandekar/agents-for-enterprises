# Capstone modules: eight befores and afters

Each student picks one module, gives it its own **before** (the legacy forms) and **after** (one sentence to an agent), adds one layer per lecture (assignments A1–A7), and demos it on Sunday 22 November.

All eight live inside the same Rasoi Steel Works and the same Bahi sandbox. They reuse purchasing's people, cost centres, suppliers, items and shared procedures, and they install together:

```python
from bahi.erp.engine import ERP
erp = ERP(modules=["hr_leave"])                    # one module on top of purchasing
erp = ERP(modules=["pur_amend", "fin_payables"])   # any combination; all eight together also works
```

| Module | Prefix | Who speaks | After: one sentence | The silent outcome | Brief |
|---|---|---|---|---|---|
| Purchasing · amend PO | `pa_` | Kavita | "Push Deccan's gasket delivery to 9 November and cut it to 15,000." | Amendment saved while the delivery schedule still totals 20,000: HD, never routed, Deccan never told | [pur_amend](pur_amend/README.md) |
| Finance · payables | `ap_` | Kavita, then Priya | "Why is Deccan's invoice 4471 on hold, and can we pay it Friday?" | Payment before the due date with no reason: "SCHEDULED", but parked (PK) and skipped by Friday's run | [fin_payables](fin_payables/README.md) |
| HR · leave | `lv_` | Kavita | "I need Thursday and Friday off for my sister's wedding." | Two days of casual leave with one left: HD, one day unpaid, never reaches Rohit | [hr_leave](hr_leave/README.md) |
| Sales · orders | `so_` | Arjun | "Quote Annapurna Stores 500 five-litre cookers at dealer price." | Order over the customer's credit limit: "SAVED", status CH, never dispatched | [sales_orders](sales_orders/README.md) |
| Service · warranty | `wr_` | Farhan | "A customer's whistle broke after three weeks; replace it." | Sale never registered, so warranty counts from manufacture: chargeable (CQ), part never issued | [svc_warranty](svc_warranty/README.md) |
| Inventory · transfers | `tr_` | Neha | "Move 2,000 gaskets from Chakan to the Pune line tonight." | More than the free stock (4,000 on QC hold): "SAVED", status SH, never gets a gate pass | [inv_transfers](inv_transfers/README.md) |
| Travel · claims | `tv_` | Kavita | "Book me Pune to Rajkot on Tuesday to visit Deccan, back Wednesday." | Trip for tomorrow without URGENT: "SAVED", wait-listed (WL), never booked | [travel_claims](travel_claims/README.md) |
| Legal · contracts | `ct_` | Kavita | "Raise an NDA with Shakti Seals on our paper, valid two years." | Party without PAN/GSTIN: "SAVED", pending KYC (PK), never reaches Legal | [legal_contracts](legal_contracts/README.md) |

Inventing your own module instead? Start from [TEMPLATE](TEMPLATE/README.md).

## The complexity budget (every module, the same)

| Item | Budget | Teaches |
|---|---|---|
| Screens | 3 | Screen → task → service → procedure |
| Services | ≈8 (flat payloads, at most 12 fields, terse legacy names) | Why raw services are poor tools |
| Stored procedures | ≈10 | Rules live in the ERP; validate once |
| Cascades | 2 | One save triggers other work |
| Variants | 2 | One screen, two paths |
| Screen-state rule | 1 | Fetch before Save (ERR-SCR-0221) |
| Silent outcome | 1 | Saved, but stuck |
| Shared engine | 1 | A purchasing procedure reused (tax, budget or approval routing) |
| Policy documents | 4–6 | Retrieval, citations, freshness (each module has one stale document) |
| Seed records | ≈50 | Duplicates, limits, near-matches |
| Scenarios | 4 | Code checks and never-events |

What the eight kits measured (from [`test_kits.log`](test_kits.log)):

| Module | Services | Own procedures | Tables | Screens | Docs | Seed records | Before: careful legacy path |
|---|---|---|---|---|---|---|---|
| pur_amend | 9 | 13 | 5 | 3 | 5 | 46 | 8 calls, 3 screens, 18 fields |
| fin_payables | 9 | 10 | 9 | 3 | 6 | 44 | 9 calls, 4 screens, 18 fields |
| hr_leave | 9 | 11 | 8 | 3 | 5 | 56 | 7 calls, 3 screens, 13 fields |
| sales_orders | 9 | 12 | 6 | 3 | 6 | 48 | 6 calls, 3 screens, 11 fields |
| svc_warranty | 9 | 11 | 8 | 3 | 5 | 55 | 6 calls, 3 screens, 13 fields |
| inv_transfers | 8 | 11 | 8 | 3 | 5 | 44 | 8 calls, 3 screens, 19 fields |
| travel_claims | 9 | 11 | 8 | 3 | 5 | 50 | 9 calls, 2 screens, 24 fields |
| legal_contracts | 9 | 11 | 6 | 3 | 5 | 46 | 7 calls, 3 screens, 20 fields |

(fin_payables counts 4 screens because the careful path also opens two purchasing enquiry screens; travel_claims uses its third screen, the expense claim, only after the trip.)

## What is in a kit

Code lives in `bahi/bahi/modules/<name>/`; the brief lives here in `modules/<name>/README.md`.

| File | What it holds |
|---|---|
| `__init__.py` | `KIT` (name, title, prefix, speaker, after sentence, screens, shared engine), `GLOSSARY`, `STATUS`, `ERRORS` |
| `seed.py` | `SCHEMA` (tables, all prefixed) and `seed(erp)`: ~50 records, extra people from `_kit.PEOPLE`, role permissions |
| `procs.py` | Stored procedures `sp_<prefix>*`, registered with `@proc` and called through `erp.sp()` so every call is logged |
| `services.py` | Services `<prefix>*`, registered with `@service`, legacy envelope `{rc, err_cd, msg, data}` |
| `screens/*.yaml` | The three legacy screens (format below) |
| `docs/*.md` | 4–6 policy documents, one of them stale |
| `scenarios.py` | Four `Scenario`s, `before(erp)`, `play_approvers(erp, sc)`, `check(sc, erp, before, turns)`, and the scripted `REFERENCE` (careful) and `NAIVE` (careless) runs |
| `legacy.py` | `happy_path(erp)`: the before, scripted screen by screen; `TRAPS`: each trap triggered and checked |
| `data-dictionary.md` | One page, generated from the code by `modules/build_dicts.py` |

Run a module's scenarios against any agent with `run_module_scenario(make_agent, "<name>", sc)` from `bahi.modules._kit`. It works like `bahi.scenarios.run_scenario`: it plays the speaker, lets whoever a document waits on approve it, answers follow-ups, and checks the database with code.

## Screen file format (`screens/<CODE>.yaml`, about 30 lines)

```yaml
code: HR-LV-02                 # the screen code shown in the title bar
title: LEAVE APPLICATION
menu: HR > Leave > Apply       # where it sits in Bahi's menu tree
roles: [PUR-EXEC, STORES]      # roles that can open it
fields:                        # what the user types or reads, in screen order
  - {name: emp_cd, label: EMP CD, type: str, req: true, help: from Find Emp}
tasks:                         # one button = one service
  - button: Fetch
    service: lv_fetch
    sends: [emp_cd, lv_cd]     # must be fields of that service
    fills: [fetch_tok]         # what comes back onto the screen
  - button: Save
    service: lv_save
    sends: [emp_cd, lv_cd, from_dt, to_dt, reason, fetch_tok]
    fills: [lv_no, status]
    needs: [Fetch]             # buttons on this screen that must run first
state:                         # screen-state rules and silent outcomes, with their codes
  - {rule: "Save needs Fetch for the same EMP CD and LV TYPE", error: ERR-SCR-0221}
```

`test_kits.py` checks that every task's service exists, that `sends` are real fields of it, and that `needs` names a button on the same screen.

## Testing (on Modal, never on the laptop)

```
/Users/raj/.venv/bin/modal run tools/modal_run.py --script modules/test_kits.py                      # all eight + template, writes test_kits.log
/Users/raj/.venv/bin/modal run tools/modal_run.py --script modules/test_kits.py --args "--only hr_leave"
/Users/raj/.venv/bin/modal run tools/modal_run.py --script modules/build_dicts.py                     # regenerate the data dictionaries
```

For each module the test installs it alone and counts the budget. It checks that every service, procedure and table carries the module's prefix and that no purchasing name is overwritten. It runs the legacy happy path and triggers every trap. It then runs the four scenarios twice: the careful reference run must pass, and the naive run must be caught by a never-event. Finally it installs all eight together and repeats the happy paths and reference scenarios on the combined sandbox, and checks that the blank TEMPLATE installs and runs.
