---
title: "MRP and Planning Generation"
type: "topic"
slug: "topic-mrp-planning"
summary: "Material requirements planning run behaviour, schedule offsets, and diagnosis of collapsed lead time errors across Northbridge sites."
audience: "staff"
status: "current"
sources: ["09_email_archive/2021/2021-04-25_MRP run results look odd.eml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| topic | MRP and Planning Generation |
| area | Supply Chain and Production Planning |
| affected_sites | Leeds store, Manchester line |
| common_failure | Collapsed sub-assembly lead times |
| primary_source | 2021-04-25_MRP run results look odd.eml |

Material requirements planning (MRP) generates forward-looking component demand and reorder schedules based on bills of materials, master production schedules, and inventory positions across sites. Historical run anomalies highlight system vulnerabilities where planning horizon calculations fail and compress required lead times into the present period. Understanding these batch generation failures ensures planners correctly identify data input errors and synchronization faults between locations.

## Planning generation anomalies

During an overnight MRP batch run on 25 April 2021, an anomaly occurred where heavy demand was erroneously generated for drive units and frame sets, whereas hardware and cabling generated minimal requirements [^r1]. In the same run, parts currently on supplier backorder were incorrectly flagged for immediate reordering [^r1].

Planners observed that lead time offsets on sub-assemblies had collapsed into the current week instead of properly spreading across the forward planning horizon [^r2].

## Root causes and troubleshooting

When sub-assembly lead times collapse into the current week during planning runs, the issue typically points to one of three root causes [^r3]:
* An unchecked box on the master schedule import [^r3].
* A corrupted work-in-progress link between the Leeds store and the Manchester line [^r3].
* Incomplete late-shift receipt postings [^r3].

## See also

* None

## References

[^r1]: 09_email_archive/2021/2021-04-25_MRP run results look odd.eml, body
[^r2]: 09_email_archive/2021/2021-04-25_MRP run results look odd.eml, body
[^r3]: 09_email_archive/2021/2021-04-25_MRP run results look odd.eml, body
