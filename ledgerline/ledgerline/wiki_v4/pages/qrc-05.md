---
title: "QRC-05 Uploading a supplier certificate"
type: "procedure"
slug: "qrc-05"
summary: "Quick reference guide for uploading and committing UN 38.3 supplier compliance certificates in Ledgerline and recording sign-off on NBC-F-113."
audience: "staff"
status: "current"
sources: ["11_training/QRC-05 Uploading a supplier certificate.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | QRC-05 |
| Title | Uploading a supplier certificate |
| Owner | Purchasing key users |
| Version | 2026.1 |
| Effective | 2026-01-12 |
| Status | Current |

QRC-05 is the quick reference card governing how purchasing staff enter and attach battery test reports in the supplier master record [^r1][^r2]. It ensures test documentation for battery cells and packs supplied to Manchester or Leeds is captured accurately for automated purchase order validation [^r3][^r4]. As of 26 October 2026, version 2026.1 is in force, requiring manual inspection and initialling on form NBC-F-113 by a senior buyer before pending orders may be released [^r1][^r8].

| Field | Value |
|---|---|
| Code | QRC-05 |
| Owner | Purchasing key users |
| Version | 2026.1 |
| Effective | 2026-01-12 |
| Status | Current |

## Steps

1. Save the scanned test report into the shared purchasing archive using standard naming conventions, confirming that the document relates specifically to battery cells or packs supplied to the Manchester plant or Leeds unit [^r3].
2. Open the Supplier master screen and navigate to the Certificates tab [^r2].
3. Click **Add** to create a new certificate line [^r2].
4. Enter the certificate type exactly as `UN38.3` to ensure automated purchase order validation functions correctly [^r2][^r4].
5. Key the document reference precisely as printed on the supplier report, including any prefix or suffix [^r5].
6. Enter the valid to date after verifying it against the report expiry or agreed default review period [^r2][^r5].
7. Attach the scanned test report from the shared archive, updating the existing line rather than attaching duplicate files if an amended report has arrived for the same part [^r2][^r7].
8. Press **F8** to commit the record, and verify that the status bar displays `CERT SAVED` [^r2][^r6]. If `CERT SAVED` is not displayed, check network connectivity and press **F8** once more rather than re-keying [^r6].
9. Present the record alongside form NBC-F-113 to the [[role-pur-sr|senior buyer]] for inspection and sign-off [^r8].

## Forms and screens

* **Supplier master (Certificates tab)**: Screen used to record the `UN38.3` certificate entry, reference, valid to date, and file attachment, committed with key **F8** [^r2][^r4][^r6].
* **NBC-F-113**: Verification form that must be initialled by the senior buyer before pending purchase orders are released for delivery, after which it is filed in the purchasing office compliance binder [^r2][^r8].

## See also

* [[role-pur-sr|Role PUR-SR]]
* [[sop-pur-005|SOP-PUR-005 Certificate Renewal (UN 38.3)]]
* [[topic-un-38-3-certificates|UN 38.3 Certificates]]

## References

[^r1]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Quick reference: Uploading a supplier certificate
[^r2]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Steps
[^r3]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Preparing the scanned file
[^r4]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Entering certificate details
[^r8]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Verification and sign-off
[^r5]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Entering certificate details
[^r7]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Saving and confirmation
[^r6]: 11_training/QRC-05 Uploading a supplier certificate.pdf, p. 1, Saving and confirmation
