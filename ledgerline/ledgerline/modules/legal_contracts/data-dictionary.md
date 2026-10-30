# Legal · contracts: data dictionary

Prefix `ct_` for services, `sp_ct_` for stored procedures, `ct_` for tables. Every reply comes in the legacy envelope `{rc, err_cd, msg, data}`; rc is S, W or E.

## Services

| Service | Legacy name | Kind | Screen | Fields (* = mandatory) |
|---|---|---|---|---|
| `ct_party_find` | PARTY ENQUIRY | read | LEG-REQ-01 | q:str, vat_no:str |
| `ct_party_save` | PARTY SAVE | write | LEG-REQ-01 | party_cd:str, name:str, city:str, state:str, pan:str, vat_no:str, sup_cd:str |
| `ct_fetch` | CONTRACT DEFAULTS | read | LEG-REQ-01 | party_cd*:str, tmpl_cd:str |
| `ct_save` | CONTRACT REQUEST SAVE | write | LEG-REQ-01 | ct_type*:str, party_cd*:str, paper*:str, tmpl_cd:str, doc_ref:str, term_months:int, start_dt:date, juris:str, value:float, fwd_to:str, fetch_tok:str, client_ref:str |
| `ct_submit` | CONTRACT RESUBMIT | write | LEG-REQ-01 | ct_no*:str, fwd_to:str |
| `ct_list` | CONTRACT REQUEST LIST | read | LEG-REV-02 | ct_no:str, party_cd:str, status:str, req_by:str, client_ref:str |
| `ct_review` | CLAUSE REVIEW | write | LEG-REV-02 | ct_no*:str, decision*:str, comment:str |
| `ct_sign` | CONTRACT SIGN | write | LEG-REV-02 | ct_no*:str, decision*:str, comment:str |
| `ct_reg_list` | CONTRACT REGISTER | read | LEG-REG-03 | party_cd:str, ct_type:str, status:str |

## Tables

- **ct_party** (14 seed rows): party_cd, name, city, state, pan, vat_no, kyc, sup_cd, status, nda_till, created_by, created_on
- **ct_tmpl** (5 seed rows): tmpl_cd, ct_type, descr, paper, def_term, max_term, juris, active
- **ct_clause** (8 seed rows): clause_cd, ct_type, attr, rule, limit_val, descr
- **ct_req** (8 seed rows): ct_no, ct_type, party_cd, paper, tmpl_cd, doc_ref, term_months, start_dt, end_dt, juris, value, status, req_by, req_on, reviewer, legal_by, signatory, signed_by, signed_on, fwd_to, warn_cd, client_ref
- **ct_dev** (2 seed rows): ct_no, clause_cd, found, expected, status
- **ct_reg** (8 seed rows): ct_no, party_cd, ct_type, start_dt, end_dt, signed_by, remind_on, status

## Field meanings

| Field | Meaning |
|---|---|
| `party_cd` | Counterparty code on the contract party register (CP-0017). Not a supplier code: an NDA does not onboard a supplier. |
| `pan / vat_no` | KYC papers. Both must be on file, and the PAN must be the one inside the VAT number (characters 3-12). |
| `kyc` | Y when PAN and VAT number are both on file and agree; N otherwise. Not shown on the request screen. |
| `ct_type` | NDA non-disclosure, MSA master supply agreement, SLA service agreement. |
| `paper` | OURS = our template (tmpl_cd); THEIRS = the counterparty's draft (doc_ref), always reviewed by Legal. |
| `tmpl_cd` | Template code. NDA-MUT-v4 is the current mutual NDA; NDA-MUT-v3 was withdrawn in March 2025. |
| `doc_ref` | Their document's reference, for their paper only. |
| `term_months / end_dt` | Term in months; end_dt = start + term - 1 day (24 months from 26-10-2026 ends 25-10-2028). |
| `juris` | Courts with jurisdiction. Playbook: MANCHESTER. |
| `fwd_to` | FWD TO: send the request to this signatory instead of the one Ledgerline's value routing picks. |
| `fetch_tok` | Token from Fetch (ct_fetch). Save without it fails with ERR-SCR-0221. |
| `reviewer / legal_by` | Legal reviewer assigned, and who actually cleared it. |
| `signatory / signed_by` | Who should sign, and who did. |
| `client_ref` | Free text the caller can use as an idempotency key. |

## Status codes

**DR** being saved · **PK** pending KYC (parked silently: reaches neither Legal nor the signatory) · **LR** with Legal for clause review · **PS** pending signature · **EX** executed and in the register · **RJ** returned or rejected

## Error and warning codes

| Code | Meaning |
|---|---|
| ERR-CT-0003 | not your request |
| ERR-CT-0030 | party not found |
| ERR-CT-0031 | party not active (blocked) |
| ERR-CT-0105 | start date in past |
| ERR-CT-0117 | party KYC still pending |
| ERR-CT-0118 | VAT number already on the register |
| ERR-CT-0122 | PAN does not match VAT number |
| ERR-CT-0201 | paper must be OURS or THEIRS |
| ERR-CT-0210 | template not found |
| ERR-CT-0211 | template is for another contract type |
| ERR-CT-0212 | template withdrawn |
| ERR-CT-0215 | their paper needs a document reference |
| ERR-CT-0216 | no template on their paper |
| ERR-CT-0220 | term mandatory |
| ERR-CT-0409 | no Legal reviewer |
| ERR-CT-0410 | FWD TO user not found |
| ERR-CT-0501 | request not found |
| ERR-CT-0502 | not pending KYC |
| ERR-CT-0503 | not in Legal review |
| ERR-CT-0504 | not your review |
| ERR-CT-0505 | not pending signature |
| ERR-CT-0506 | not your signature |
| W-CT-117 | saved, parked for KYC; never routed |
| ERR-SCR-0221 | Save without Fetch |
| ERR-APR-0003 | self approval |
| ERR-APR-0009 | no approver found in the manager chain |
