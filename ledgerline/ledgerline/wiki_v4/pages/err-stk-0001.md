---
title: "ERR-STK-0001"
type: "error"
slug: "err-stk-0001"
summary: "Error code ERR-STK-0001 raised when locked inventory records or unposted transactions suspend valuation runs or stock snapshots."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-STK-0001 |
| Module | Inventory |
| Severity | Error |
| Affected services | stk_val_run, stk_snapshot |
| Source manual | MAN-INV-72 |

`ERR-STK-0001` is a Ledgerline inventory processing error that halts valuation and snapshot routines [^r1]. It indicates that underlying inventory database tables are locked by concurrent terminal activity or have been left in an inconsistent state by an unposted physical transaction [^r1]. When encountered, operations must resolve the table lock or complete pending postings before re-running inventory valuation [^r1].

## Meaning
The error signifies that inventory records are temporarily inaccessible or structurally inconsistent, which suspends execution of the `stk_val_run` or `stk_snapshot` background services [^r1].

## Cause
`ERR-STK-0001` is triggered when underlying inventory records are actively locked by another terminal session [^r1]. It also occurs when an unposted physical transaction leaves inventory tables in an inconsistent state [^r1].

## How to fix
Users must ensure that concurrent sessions locking inventory tables release their locks [^r1]. Any unposted physical transactions causing table inconsistencies must be posted or cleared before re-initiating the process [^r1].

## Raised by
This error is raised by the `stk_val_run` and `stk_snapshot` inventory services [^r1].

## See also
* [[errors-stk|ERR-STK Error Codes]]
* [[man-inv-72|MAN-INV-72 Ledgerline ERP 7.2 User Manual: Inventory]]
* [[services-stk|INV stk services]]
* [[screen-inv-stk-03|INV-STK-03 Stock Val]]

## References

[^r1]: 03_ledgerline_manuals/MAN-INV-72 Ledgerline 7.2 User Manual - Inventory v7.2.3.pdf, p. 47, Messages
