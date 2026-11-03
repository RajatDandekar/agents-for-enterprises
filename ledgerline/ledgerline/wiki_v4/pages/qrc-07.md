---
title: "QRC-07 Quick reference: Lithium battery labels"
type: "procedure"
slug: "qrc-07"
summary: "Quick reference guide for selecting, applying, and booking UN lithium battery labels on outgoing parcels to prevent delivery rejections and despatch errors."
audience: "staff"
status: "current"
sources: ["11_training/QRC-07 Lithium battery labels.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Document code | QRC-07 |
| Title | Quick reference: Lithium battery labels |
| Owner | Purchasing key users |
| Version | 2026.1 |
| Effective date | 2026-01-12 |
| Status | current |

QRC-07 version 2026.1 governs lithium battery labelling requirements across Northbridge Cycles packing benches as of 2026-01-12 [^r1]. Every parcel containing a battery pack requires label [[items-pkg|PKG-LBL-UN]], with specific UN designations depending on whether the pack is shipped alone or with a bicycle [^r2][^r3][^r4]. Following this procedure ensures parcels are not rejected by collection drivers and prevents transaction errors during despatch posting [^r7][^r8].

| Field | Detail |
|---|---|
| Document code | QRC-07 [^r1] |
| Version | 2026.1 [^r1] |
| Effective date | 2026-01-12 [^r1] |
| Owner | Purchasing key users [^r1] |
| Status | Current [^r1] |

## Steps

### Selecting the correct designation
Every parcel containing a battery pack must receive label [[items-pkg|PKG-LBL-UN]] [^r2]. Packers must use designation UN3480 when a lithium battery pack travels alone as a replacement part [^r3]. Designation UN3481 must be used when the pack is installed inside the frame or boxed together with the bicycle [^r4]. Both UN markings must never be applied to the same carton [^r4].

### Stocking label rolls
Label rolls must be stocked beside packing benches in the Manchester packing area and the Leeds unit [^r5]. Rolls must be stored in their original cartons away from direct heat and moisture [^r5]. The storekeeper must be informed before the final roll is opened [^r5].

### Label positioning on cartons
Labels must be applied flat to the outer carton on the same face as the carrier address label [^r6]. The label must not cross seams, closures, strapping, or tape [^r6].

### Carrier booking and documentation
Parcels containing packs must be booked under carrier service DGX during collection booking [^r7]. Drivers will reject consignments if manifest service codes do not match hazardous markings [^r7].

### Despatch sequence in the system
The label must always be printed before posting the despatch transaction [^r8]. Printing after posting triggers error [[err-dlv-0320|ERR-DLV-0320]], which requires the system supervisor to clear the transaction flag before reprinting can occur [^r8].

## Forms and screens
* Label stock item: [[items-pkg|PKG-LBL-UN]] [^r2]
* Carrier booking service: DGX [^r7]
* Despatch transaction sequence and error flag: [[err-dlv-0320|ERR-DLV-0320]] [^r8]

## See also
* [[err-dlv-0320|ERR-DLV-0320 Lithium Battery Label Required]]
* [[items-pkg|PKG-* items]]
* [[pol-bat-004|POL-BAT-004 Battery Safety and Handling Policy]]
* [[sop-sal-001|SOP-SAL-001 Sales Order to Despatch]]

## References

[^r1]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Quick reference: Lithium battery labels
[^r2]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Selecting the correct designation
[^r3]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Selecting the correct designation
[^r4]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Selecting the correct designation
[^r7]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Carrier booking and documentation
[^r8]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Despatch sequence in the system
[^r5]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Stocking label rolls
[^r6]: 11_training/QRC-07 Lithium battery labels.pdf, p. 1, Label positioning on cartons
