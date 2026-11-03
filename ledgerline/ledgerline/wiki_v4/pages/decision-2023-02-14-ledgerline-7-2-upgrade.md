---
title: "Ledgerline 7.2 Upgrade Steering Decisions (2023-02-14)"
type: "decision"
slug: "decision-2023-02-14-ledgerline-7-2-upgrade"
summary: "Steering decisions for the Ledgerline 7.2.0 upgrade covering Easter cutover plans, approval inbox workflows, site training, and reporting continuity."
audience: "staff"
status: "current"
sources: ["10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Date | 2023-02-14 |
| Decision type | System upgrade cutover and workflow implementation |
| Status | Implemented |
| Lead system | Ledgerline 7.2.0 |
| Key sites | Leeds, Manchester |

Steering group decisions recorded on 14 February 2023 established the cutover plan, approval queue behaviour, and training protocols for the transition to [[rn-7-2-0|Ledgerline 7.2.0]]. The implementation scheduled the production go-live across the Easter weekend while introducing electronic approval queues for purchasing. For operations today, this established the operational rule that unapproved purchase requisitions do not block stock issues, as well as mandatory absence cover rules for purchasing workflows.

## Cutover arrangements and site coverage

The Ledgerline upgrade to version 7.2.0 was planned to go live over the Easter weekend alongside the launch of the approval inbox [^r1]. Leeds was scheduled to finish despatch earlier on the final working day before cutover to clear all outstanding pick notes prior to the database backup [^r2]. Manchester assembly lines were set to halt following the afternoon shift to allow stores to complete raw materials transfer bookings before cutover [^r3]. Remote access for software consultants was tested, with telephone coverage required for the Manchester engineering room throughout the upgrade weekend [^r4].

## Approval inbox workflow

Under the electronic approval inbox workflow governed in [[sop-pur-002|SOP-PUR-002]], purchase requisitions awaiting sign-off do not block stores from issuing parts already held in stock, but purchase orders are not generated until sign-off is completed [^r5]. Cover arrangements were required for authorising managers away on annual leave so purchase requisitions are not held up indefinitely [^r6].

## Training and reporting continuity

Desk-side training sessions were arranged for Manchester supervisors, and the Leeds unit clerk was tasked to walk local supervisors through approval queues following the rollout [^r7]. In addition, financial trial balance and aged debtor print runs against copied test database data were required to verify that report definitions and formatting carried over cleanly [^r8].

## See also

* [[rn-7-2-0|RN-7.2.0 Ledgerline ERP 7.2.0 Release Notes]]
* [[sop-pur-002|SOP-PUR-002 Purchase Request to Purchase Order]]

## References

[^r1]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Plan
[^r2]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Weekend cutover arrangements and site coverage
[^r3]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Weekend cutover arrangements and site coverage
[^r4]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Weekend cutover arrangements and site coverage
[^r5]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Approval inbox workflow and authority limits
[^r6]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Approval inbox workflow and authority limits
[^r7]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Training requirements and user documentation
[^r8]: 10_meeting_notes/2023-02-14 Ledgerline 7.2 upgrade steering.md, Reporting continuity and month-end preparation
