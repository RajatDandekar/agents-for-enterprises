---
title: "AP-VAT-12 Vat Return"
type: "screen"
slug: "screen-ap-vat-12"
summary: "Ledgerline screen for running, retrieving and reviewing VAT returns and reverse charge registers by period in Accounts Payable."
audience: "staff"
status: "current"
sources: ["03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "04_service_definitions/accounts_payable/vat_get.yaml", "04_service_definitions/accounts_payable/vat_rc_list.yaml", "04_service_definitions/accounts_payable/vat_run.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Screen code | AP-VAT-12 |
| Module | Accounts Payable |
| Menu path | Accounts payable > Vat return |
| Primary service | vat_run |
| Read services | vat_get, vat_rc_list |
| Status | Current |

Screen AP-VAT-12 (Vat Return) is the Ledgerline interface used to calculate, inspect, and report value-added tax figures for a specified accounting period [^r1][^r2]. Users access the screen through Accounts payable > Vat return to run input tax and reverse charge calculations, retrieve summary and grid figures, and review the reverse charge register [^r1][^r2]. The comment field can be updated post-run while the period remains unlocked, but changing the target period requires re-running the calculation [^r4].

## Fields

| Field | Type | Mandatory / Optional | Notes |
|---|---|---|---|
| PERIOD | String | Mandatory | Accounting period for the VAT return; changing it requires re-running `vat_run` [^r1][^r4][^r5]. |
| COMMENT | String | Optional | Notes on the return; editable after running `vat_run` provided the general ledger period is not locked [^r1][^r4][^r5]. |

## Keys and services

* `vat_run`: Invokes write service `vat_run` to execute a VAT return run via stored procedure `sp_vat_run`, calculating input tax and reverse charges [^r2][^r9].
* `vat_get`: Executes read service `vat_get` to retrieve summary and grid figures for the VAT return [^r2][^r7].
* `vat_rc_list`: Executes read service `vat_rc_list` using the mandatory `period` parameter to display the reverse charge register [^r2][^r8].

Services invoked by this screen belong to [[services-ap-vat]].

## Messages

* `ERR-VAT-0001` (*Vat Return Not Found*): Raised when transaction records cannot be found, an invalid or open period is entered, or unposted invoice register batches remain [^r3][^r6].

## See also

* [[services-ap-vat]]
* [[screen-ap-per-11]]
* [[screen-ap-gl-14]]
* [[screen-ap-tax-17]]

## References

[^r1]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 40, §13. Vat Return (AP-VAT-12)
[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 41, Screen layout and fields
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 43, Questions users ask
[^r5]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 10, AP-VAT-12 VAT RETURN
[^r9]: 04_service_definitions/accounts_payable/vat_run.yaml, service: vat_run
[^r7]: 04_service_definitions/accounts_payable/vat_get.yaml, service: vat_get
[^r8]: 04_service_definitions/accounts_payable/vat_rc_list.yaml, screen: AP-VAT-12
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 42, Messages
[^r6]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 11, AP-VAT-12 VAT RETURN
