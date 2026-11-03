---
title: "AP bnk services"
type: "service-group"
slug: "services-ap-bnk"
summary: "Ledgerline Accounts Payable SOAP services for querying, maintaining, verifying, and blocking supplier bank details on screen AP-BNK-06."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf", "03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf", "04_service_definitions/accounts_payable/bnk_block.xml", "04_service_definitions/accounts_payable/bnk_get.xml", "04_service_definitions/accounts_payable/bnk_save.xml", "04_service_definitions/accounts_payable/bnk_search.xml", "04_service_definitions/accounts_payable/bnk_verify.xml", "12_integrations/wsdl/LedgerlineGateway.wsdl"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Module | Accounts Payable (AP) |
| Target screen | AP-BNK-06 |
| Protocol | SOAP gateway (port 8091) |
| Target namespace | urn:ledgerline:svc:ap |
| Operations | bnk_save, bnk_get, bnk_verify, bnk_block, bnk_search |
| Status | Current |

The `bnk` service group provides the Accounts Payable operations for managing supplier bank accounts in Ledgerline [^r2][^r15]. Tied directly to screen [[screen-ap-bnk-06|AP-BNK-06]], these services allow operators to retrieve, record, block, and search bank details, as well as clear payment holds following two-person verification calls [^r1][^r2][^r37]. All five operations originate as Ledgerline 7.0 SOAP gateway services exposed through the Ledgerline 7.2 compatibility listener on port 8091 [^r19][^r24][^r26][^r29][^r33].

## Services

### bnk_save

The `bnk_save` write service writes supplier bank records and executes stored procedure `sp_bnk_save` [^r3][^r10]. When executed, the service validates bank details formatting and updates the record status to require verification [^r3].

* **Required fields:** `sup_cd`, `acct_name` [^r10][^r27].
* **Optional fields:** `sort_cd`, `acct_no`, `iban`, `bic` [^r10][^r27].
* **Errors:** [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND) [^r28], [[err-bnk-0118|ERR-BNK-0118]] (IBAN CHECK DIGITS INVALID) [^r8][^r10][^r28][^r39].
* **Warnings:** W-BNK-120 (BANK DETAILS CHANGED, PAYMENTS HELD UNTIL VERIFIED) [^r10][^r28][^r38][^r39].
* **Source file:** `04_service_definitions/accounts_payable/bnk_save.xml` [^r25][^r26].

### bnk_get

The `bnk_get` read operation queries and retrieves existing bank details for a supplier [^r11][^r20].

* **Required fields:** `sup_cd` [^r11][^r21].
* **Optional fields:** none [^r21].
* **Errors:** [[err-bnk-0001|ERR-BNK-0001]] (SUPPLIER BANK DETAILS NOT FOUND) [^r7][^r11][^r23][^r39].
* **Source file:** `04_service_definitions/accounts_payable/bnk_get.xml` [^r20][^r24].

### bnk_verify

The `bnk_verify` write operation invokes stored procedure `sp_bnk_verify` to validate permissions and log mandatory text details of the two-person supplier bank verification call [^r1][^r4][^r12]. Successful execution clears payment holds and updates the supplier bank status so that the account is approved for automated payment proposal generation [^r1][^r4].

* **Required fields:** `sup_cd` [^r12][^r34].
* **Optional fields:** none [^r34].
* **Errors:** [[err-bnk-0001|ERR-BNK-0001]] (SUPPLIER BANK DETAILS NOT FOUND) [^r36], [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND) [^r36], [[err-bnk-0125|ERR-BNK-0125]] (CALL-BACK NOT RECORDED) [^r9][^r12][^r36][^r39].
* **Source file:** `04_service_definitions/accounts_payable/bnk_verify.xml` [^r33].

### bnk_block

The `bnk_block` write service calls stored procedure `sp_bnk_block` to write a stop flag against the supplier bank account [^r5][^r13]. This sets the record status to blocked and excludes the account from automated payment run proposals [^r5].

* **Required fields:** `sup_cd` [^r13][^r16].
* **Optional fields:** `reason` [^r13][^r16].
* **Errors:** [[err-bnk-0001|ERR-BNK-0001]] (SUPPLIER BANK DETAILS NOT FOUND) [^r18], [[err-sup-0030|ERR-SUP-0030]] (SUPPLIER NOT FOUND) [^r18].
* **Source file:** `04_service_definitions/accounts_payable/bnk_block.xml` [^r15][^r19].

### bnk_search

The `bnk_search` read service opens an inquiry listing window allowing operators to search and list supplier bank records, including looking up vendors by trading name [^r6][^r14][^r29].

* **Required fields:** none [^r31].
* **Optional fields:** `sup_cd`, `acct_name`, `sort_cd`, `status` [^r14][^r31].
* **Errors:** none [^r31][^r32].
* **Source file:** `04_service_definitions/accounts_payable/bnk_search.xml` [^r29][^r30].

## See also

* [[screen-ap-bnk-06|AP-BNK-06 Supplier Bank Details Entry]]
* [[screen-ap-spy-16|AP-SPY-16 Supplier Payment Hold Hold]]
* [[services-ap-pay|AP pay services]]
* [[services-ap-sup|AP sup services]]
* [[errors-bnk|Errors BNK]]
* [[errors-sup|ERR-SUP Error Codes]]
* [[err-bnk-0001|ERR-BNK-0001 Missing mandatory banking fields]]
* [[err-bnk-0118|ERR-BNK-0118 Modulus check or clearing code validation failed]]
* [[err-bnk-0125|ERR-BNK-0125 Record locked by another user or concurrent payment process]]
* [[err-sup-0030|ERR-SUP-0030]]

## References

[^r2]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 22, §8. Supplier Bank Details (AP-BNK-06)
[^r15]: 04_service_definitions/accounts_payable/bnk_block.xml, wsdl:documentation
[^r1]: 02_procedures/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf, p. 4, What to check on the screen
[^r37]: 12_integrations/wsdl/LedgerlineGateway.wsdl, GatewayPort
[^r19]: 04_service_definitions/accounts_payable/bnk_block.xml, header comment
[^r24]: 04_service_definitions/accounts_payable/bnk_get.xml, comments
[^r26]: 04_service_definitions/accounts_payable/bnk_save.xml, comments
[^r29]: 04_service_definitions/accounts_payable/bnk_search.xml, wsdl:documentation
[^r33]: 04_service_definitions/accounts_payable/bnk_verify.xml, wsdl:documentation
[^r3]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Step by step
[^r10]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 30, bnk_save SUPPLIER BANK DETAILS SAVE
[^r27]: 04_service_definitions/accounts_payable/bnk_save.xml, xs:element name="bnk_saveRequest"
[^r28]: 04_service_definitions/accounts_payable/bnk_save.xml, ll:errors
[^r8]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r39]: 03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf, p. 4, AP-BNK-06 SUPPLIER BANK DETAILS ENTRY
[^r38]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 28
[^r25]: 04_service_definitions/accounts_payable/bnk_save.xml, wsdl:documentation
[^r11]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 30, bnk_get SUPPLIER BANK DETAILS GET
[^r20]: 04_service_definitions/accounts_payable/bnk_get.xml, wsdl:documentation
[^r21]: 04_service_definitions/accounts_payable/bnk_get.xml, wsdl:types/xs:schema/xs:element name="bnk_getRequest"
[^r7]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r23]: 04_service_definitions/accounts_payable/bnk_get.xml, ll:errors
[^r4]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Step by step
[^r12]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 30, bnk_verify SUPPLIER BANK DETAILS VERIFY
[^r34]: 04_service_definitions/accounts_payable/bnk_verify.xml, wsdl:types
[^r36]: 04_service_definitions/accounts_payable/bnk_verify.xml, ll:errors
[^r9]: 03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf, p. 3, §2. Codes
[^r5]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 24, Step by step
[^r13]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 31, bnk_block SUPPLIER BANK DETAILS BLOCK
[^r16]: 04_service_definitions/accounts_payable/bnk_block.xml, wsdl:types/xs:schema/bnk_blockRequest
[^r18]: 04_service_definitions/accounts_payable/bnk_block.xml, ll:errors
[^r6]: 03_ledgerline_manuals/MAN-AP-72 Ledgerline 7.2 User Manual - Accounts Payable v7.2.3.pdf, p. 23, Step by step
[^r14]: 03_ledgerline_manuals/MAN-SVC-72 Service Reference (all modules) v7.2.3.pdf, p. 31, bnk_search SUPPLIER BANK DETAILS LIST
[^r31]: 04_service_definitions/accounts_payable/bnk_search.xml, xs:element name="bnk_searchRequest"
[^r32]: 04_service_definitions/accounts_payable/bnk_search.xml, xs:element name="bnk_searchResponse"
[^r30]: 04_service_definitions/accounts_payable/bnk_search.xml, wsdl:service name="bnk_searchService"
