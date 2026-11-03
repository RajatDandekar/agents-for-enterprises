---
title: "ERR-CUR-0001 Currency Rate Action Failed"
type: "error"
slug: "err-cur-0001"
summary: "Ledgerline error displayed when currency lookup or saving fails due to missing rates, invalid codes, locked periods, or table locks."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-CUR-0001 |
| Message | Currency Rate Action Failed |
| Module | AP / CUR |
| Severity | Error |
| Manual | MAN-AP-72 |

ERR-CUR-0001 is an error in [[man-ap-72|Ledgerline ERP 7.2]] raised during currency conversion retrieval or rate maintenance [^r1]. It indicates that the system failed to locate a conversion rate for a given date or was prevented from saving currency rate records [^r1]. Resolving it requires validating the currency parameters, ensuring the posting period is open, and confirming control tables are unlocked [^r2].

## Meaning
ERR-CUR-0001 indicates a currency rate action failure [^r1]. It is displayed when the system cannot find a conversion rate for the specified currency code and rate date, or when saving currency data fails due to invalid parameters or system table locks [^r1].

## Cause
The error occurs under the following circumstances:
* The service `cur_get` cannot find a conversion for the specified CUR CD and RATE DT [^r1].
* The service `cur_save` encounters an unrecognised currency code [^r1].
* The service `cur_save` encounters an invalid or locked posting date [^r1].
* A mandatory field is left blank during a save operation [^r1].
* An exclusive lock is held on currency control tables [^r2].

## How to fix
To resolve ERR-CUR-0001:
* Verify the spelling of CUR CD [^r2].
* Confirm RATE DT falls within an open accounting period [^r2].
* Verify that RATE TO GBP is a valid positive entry [^r2].
* Check that no exclusive lock is held on the currency control tables [^r2].

## Raised by
* Service `cur_get` within [[services-ap-cur|AP cur services]] [^r1].
* Service `cur_save` within [[services-ap-cur|AP cur services]] [^r1].
* Associated user operations on [[screen-ap-cur-13|AP-CUR-13 Currency Rate]] [^r1].

## See also
* [[screen-ap-cur-13|AP-CUR-13 Currency Rate]]
* [[services-ap-cur|AP cur services]]
* [[man-ap-72|MAN-AP-72 Ledgerline ERP 7.2 User Manual: Accounts]]
* [[screen-ap-per-11|AP-PER-11 Ap Period]]
* [[errors-per|ERR-PER Error Codes]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 49, Messages
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 49, Messages
