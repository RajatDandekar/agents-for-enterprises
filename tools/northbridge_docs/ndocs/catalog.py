"""The Ledgerline service catalogue, screens, error codes, tables and batch jobs.

The 38 purchasing services (and the 3 goods-receipt services of erp/receipts.py) are read from the sandbox package
itself: names, fields, types, required flags, descriptions, screens, and the error codes each service and the
stored procedures it calls can raise. Nothing about them is retyped. The other ~360 services of the Inventory,
Accounts Payable, Sales, Production and Admin modules are generated from the entity specs below.
"""
from __future__ import annotations

import inspect
import re

from ledgerline.erp import engine
from ledgerline.erp import procs as _procs  # noqa: F401  (registers PROCS)
from ledgerline.erp import receipts as _receipts  # noqa: F401  (registers grn_*)
from ledgerline.erp import services as _services  # noqa: F401

ERR_RX = re.compile(r'LedgerlineError\(\s*"((?:ERR|W)-[A-Z]+-\d{4})",\s*(f?)"([^"]*)"')
WARN_RX = re.compile(r'"(W-[A-Z]+-\d{3,4})"')
SP_RX = re.compile(r'erp\.sp\(\s*"(\w+)"')


def _msg(m):
    def rep(x):
        keys = re.findall(r"\['(\w+)'\]", x.group(1)) or re.findall(r"[A-Za-z_]\w*", x.group(1))
        return f"<{keys[-1] if keys else 'value'}>"
    return re.sub(r"\{([^}]*)\}", rep, m)


def _scan(src):
    errs = [(c, _msg(t) if f else t) for c, f, t in ERR_RX.findall(src)]
    return errs, WARN_RX.findall(src), SP_RX.findall(src)


def _closure(svc_name, seen=None):
    """Errors, warnings and stored procedures reachable from one service (through procs and other services)."""
    seen = seen if seen is not None else set()
    spec = engine.SERVICES[svc_name]
    src = inspect.getsource(spec.fn)
    errs, warns, sps = _scan(src)
    for other in engine.SERVICES:
        if other != svc_name and re.search(rf"(?<![\w.]){other}\(erp", src) and other not in seen:
            seen.add(other)
            e2, w2, s2 = _closure(other, seen)
            errs += e2
            warns += w2
            sps += s2
    todo, done = list(sps), set()
    while todo:
        p = todo.pop(0)
        if p in done:
            continue
        done.add(p)
        e2, w2, s2 = _scan(inspect.getsource(engine.PROCS[p]))
        errs += e2
        warns += w2
        todo += s2
    out_e, se = [], set()
    for c, t in errs:
        if c not in se:
            se.add(c)
            out_e.append((c, t))
    return out_e, sorted(set(warns)), list(dict.fromkeys(sps + sorted(done - set(sps))))


COMMON = [("ERR-SEC-0001", "ACCESS DENIED"), ("ERR-SYS-0421", "<FIELD> MANDATORY"),
          ("ERR-SYS-0422", "UNKNOWN FIELD <FIELD> / BAD VALUE FOR <FIELD>"), ("ERR-SYS-0503", "SERVER BUSY, TRY LATER")]


def real_services():
    """The sandbox's services, exactly as registered: (module PUR: services.py; INV: receipts.py)."""
    out = []
    for name, spec in engine.SERVICES.items():
        mod = spec.fn.__module__
        if mod not in ("ledgerline.erp.services", "ledgerline.erp.receipts"):
            continue
        errs, warns, sps = _closure(name)
        out.append(dict(name=name, module="PUR" if mod.endswith("services") else "INV", title=spec.doc, kind=spec.kind,
                        screen=spec.screen, fields=[dict(name=f.name, type=f.type, required=f.required, desc=f.desc) for f in spec.fields],
                        errors=[dict(code=c, msg=t) for c, t in errs], warnings=warns, procedures=sps, real=True,
                        since="7.2.3" if name in ("po_fetch", "pr_fetch") else "7.0", fmt="yaml"))
    return out


# ------------------------------------------------------------------------------------------------ generated modules
F_TYPES = {"!": True}


def _fields(spec):
    out = []
    for part in [p for p in spec.split("|") if p]:
        name, typ, desc = (part.split(":") + ["", ""])[:3]
        req = typ.endswith("!")
        out.append(dict(name=name, type=typ.rstrip("!") or "str", required=req, desc=desc or name.upper().replace("_", " ")))
    return out


# module: (folder, title, [(ent, ENT code, title, screen, key, fields, ops)])
# ops: space-separated; an op may carry its own fields as op(fieldspec) with ';' between fields.
GEN = {
    "INV": ("inventory", "Inventory", [
        ("txf", "TXF", "STOCK TRANSFER", "INV-TRF-04", "txf_no", "itm_cd:str!:ITEM CD|from_whs:str!:FROM WHS|to_whs:str!:TO WHS|qty:int!:QTY|reason:str:REASON", "save get search post cancel"),
        ("adj", "ADJ", "STOCK ADJUSTMENT", "INV-ADJ-05", "adj_no", "itm_cd:str!:ITEM CD|whs_cd:str!:WHS CD|qty:int!:QTY (+/-)|reason_cd:str!:REASON CD|remarks:str:REMARKS", "save get search approve post cancel"),
        ("cnt", "CNT", "STOCK COUNT", "INV-CNT-06", "cnt_no", "whs_cd:str!:WHS CD|cnt_type:str!:CYCLE/ANNUAL|bin_from:str:BIN FROM|bin_to:str:BIN TO|cnt_dt:date!:COUNT DT", "save get search entry(cnt_no:str!:COUNT NO;itm_cd:str!:ITEM CD;qty:int!:QTY COUNTED) freeze post cancel"),
        ("rtv", "RTV", "RETURN TO VENDOR", "INV-RTV-07", "rtv_no", "grn_no:str!:GRN NO|qty:int!:QTY|reason_cd:str!:REASON CD|ncr_no:str:NCR NO|remarks:str:REMARKS", "save get search post cancel"),
        ("mrn", "MRN", "MATERIAL ISSUE", "INV-MRN-08", "mrn_no", "wo_no:str!:WO NO|itm_cd:str!:ITEM CD|qty:int!:QTY|whs_cd:str:WHS CD", "save get search post cancel"),
        ("bin", "BIN", "BIN MASTER", "INV-BIN-09", "bin_cd", "whs_cd:str!:WHS CD|bin_cd:str!:BIN CD|bin_type:str:BIN TYPE|max_qty:int:MAX QTY", "save get search block"),
        ("lot", "LOT", "LOT / SERIAL", "INV-LOT-10", "lot_no", "itm_cd:str!:ITEM CD|lot_no:str!:LOT/SERIAL|sup_cd:str:SUP CD|mfg_dt:date:MFG DT|grn_no:str:GRN NO", "save get search trace hold release"),
        ("qch", "QCH", "QUALITY HOLD", "INV-QCH-11", "qch_no", "grn_no:str!:GRN NO|itm_cd:str!:ITEM CD|qty:int!:QTY|reason:str:REASON", "save get search release reject"),
        ("res", "RES", "STOCK RESERVATION", "INV-RES-12", "res_no", "itm_cd:str!:ITEM CD|whs_cd:str!:WHS CD|qty:int!:QTY|wo_no:str:WO NO", "save get search cancel"),
        ("whs", "WHS", "WAREHOUSE MASTER", "INV-WHS-01", "whs_cd", "whs_cd:str!:WHS CD|name:str!:NAME|ou_cd:str!:OU CD|whs_type:str:TYPE", "get save"),
        ("itm", "ITM", "ITEM MASTER", "INV-ITM-01", "itm_cd", "itm_cd:str!:ITEM CD|descr:str!:DESCRIPTION|uom_cd:str!:UOM|category:str!:CATEGORY|cell_safety:int:LITHIUM CELL (0/1)|reorder_lvl:int:REORDER LVL", "save update block uom_conv(itm_cd:str!:ITEM CD;from_uom:str!:FROM UOM;to_uom:str!:TO UOM;factor:float!:FACTOR)"),
        ("stk", "STK", "STOCK", "INV-STK-03", "itm_cd", "itm_cd:str:ITEM CD|whs_cd:str:WHS CD|as_on:date:AS ON", "val_query val_run age_query abc_run move_query snapshot"),
        ("kbn", "KBN", "KANBAN CARD", "INV-KBN-13", "kbn_no", "itm_cd:str!:ITEM CD|whs_cd:str!:WHS CD|bin_qty:int!:BIN QTY|cards:int:NO OF CARDS", "save get search signal close"),
        ("ccp", "CCP", "CYCLE COUNT PLAN", "INV-CCP-14", "ccp_no", "whs_cd:str!:WHS CD|abc:str:ABC CLASS|freq_days:int!:FREQUENCY", "save get search generate"),
        ("pkg", "PKG", "RETURNABLE PACKAGING", "INV-PKG-15", "pkg_no", "sup_cd:str!:SUP CD|pkg_type:str!:PKG TYPE|qty:int!:QTY", "save get search post"),
        ("scr", "SCR", "SCRAP NOTE", "INV-SCR-16", "scr_no", "itm_cd:str!:ITEM CD|whs_cd:str!:WHS CD|qty:int!:QTY|reason_cd:str!:REASON CD", "save get search approve post"),
        ("csg", "CSG", "CONSIGNMENT STOCK", "INV-CSG-17", "csg_no", "sup_cd:str!:SUP CD|itm_cd:str!:ITEM CD|qty:int!:QTY", "save get search settle"),
    ]),
    "AP": ("accounts_payable", "Accounts Payable", [
        ("inv", "INV", "SUPPLIER INVOICE", "AP-INV-01", "ap_doc", "sup_cd:str!:SUP CD|sup_inv_no:str!:SUP INV NO|inv_dt:date!:INV DT|po_no:str:PO NO|basic:float!:BASIC|tax_cd:str!:TAX CD|tax:float:TAX AMT|gross:float!:GROSS", "save get search post cancel hold release"),
        ("mat", "MAT", "THREE-WAY MATCH", "AP-MAT-02", "ap_doc", "ap_doc:str!:AP DOC|tol_pct:float:TOL %", "run get override search"),
        ("dbn", "DBN", "DEBIT NOTE", "AP-DBN-04", "dbn_no", "sup_cd:str!:SUP CD|ref_doc:str!:REF DOC|amount:float!:AMOUNT|reason_cd:str!:REASON CD", "save get search post cancel"),
        ("crn", "CRN", "SUPPLIER CREDIT NOTE", "AP-CRN-05", "crn_no", "sup_cd:str!:SUP CD|sup_crn_no:str!:SUP CRN NO|amount:float!:AMOUNT|ap_doc:str:AP DOC", "save get search post"),
        ("pay", "PAY", "PAYMENT RUN", "AP-PAY-03", "run_no", "run_dt:date!:RUN DT|bank_cd:str!:BANK CD|due_upto:date!:DUE UPTO|sup_cd:str:SUP CD", "propose get approve release file cancel search"),
        ("bnk", "BNK", "SUPPLIER BANK DETAILS", "AP-BNK-06", "sup_cd", "sup_cd:str!:SUP CD|acct_name:str!:ACCT NAME|sort_cd:str:SORT CD|acct_no:str:ACCT NO|iban:str:IBAN|bic:str:BIC", "save get verify block search"),
        ("adv", "ADV", "ADVANCE PAYMENT", "AP-ADV-07", "adv_no", "sup_cd:str!:SUP CD|po_no:str!:PO NO|amount:float!:AMOUNT", "save get search approve adjust"),
        ("sbal", "SBL", "SUPPLIER BALANCE", "AP-SBL-08", "sup_cd", "sup_cd:str!:SUP CD|as_on:date:AS ON", "query ageing stmt"),
        ("acr", "ACR", "GRNI ACCRUAL", "AP-ACR-10", "acr_no", "period:str!:PERIOD", "run get reverse"),
        ("per", "PER", "AP PERIOD", "AP-PER-11", "period", "period:str!:PERIOD", "list close open status"),
        ("vat", "VAT", "VAT RETURN", "AP-VAT-12", "period", "period:str!:PERIOD|ou_cd:str:OU CD", "run get rc_list"),
        ("exp", "EXP", "EXPENSE CLAIM", "AP-EXP-09", "exp_no", "user_id:str!:USER ID|claim_dt:date!:CLAIM DT|amount:float!:AMOUNT|cc_cd:str!:CC CD|exp_type:str!:EXP TYPE", "save get search submit approve reject pay"),
        ("cur", "CUR", "CURRENCY RATE", "AP-CUR-13", "cur_cd", "cur_cd:str!:CURRENCY|rate_dt:date!:RATE DT|rate:float!:RATE TO GBP", "get save list"),
        ("gl", "GL", "GL POSTING", "AP-GL-14", "jv_no", "jv_dt:date!:JV DT|acct_cd:str!:ACCOUNT|amount:float!:AMOUNT|cc_cd:str:CC CD", "post query reverse"),
        ("pcs", "PCS", "PETTY CASH", "AP-PCS-15", "pcs_no", "ou_cd:str!:OU CD|amount:float!:AMOUNT|purpose:str!:PURPOSE|cc_cd:str!:CC CD", "save get search post"),
        ("sup_pay", "SPY", "SUPPLIER PAYMENT HOLD", "AP-SPY-16", "sup_cd", "sup_cd:str!:SUP CD|reason:str:REASON", "hold release"),
        ("tax", "TAX", "TAX CODE MASTER", "AP-TAX-17", "tax_cd", "tax_cd:str!:TAX CD|descr:str!:DESCR|rate:float!:RATE|kind:str!:INTRA/INTER", "get save"),
    ]),
    "SAL": ("sales", "Sales and Distribution", [
        ("cust", "CUS", "CUSTOMER MASTER", "SAL-CUS-01", "cust_cd", "name:str!:CUST NAME|city:str!:CITY|country:str!:COUNTRY CD (2)|vat_no:str:VAT number|pt_cd:str:PAY TERM CD|price_list:str:PRICE LIST", "save get search update block credit"),
        ("so", "SO", "SALES ORDER", "SAL-SO-01", "so_no", "cust_cd:str!:CUST CD|itm_cd:str!:ITEM CD|qty:int!:QTY|price:float:PRICE|req_dt:date!:REQ DT|cust_ref:str:CUST PO REF", "fetch save get search confirm cancel amend hold release"),
        ("quo", "QUO", "QUOTATION", "SAL-QUO-02", "quo_no", "cust_cd:str!:CUST CD|itm_cd:str!:ITEM CD|qty:int!:QTY|price:float!:PRICE|valid_to:date!:VALID TO", "save get search convert cancel"),
        ("alc", "ALC", "ALLOCATION", "SAL-ALC-03", "so_no", "so_no:str:SO NO|whs_cd:str:WHS CD", "run get cancel"),
        ("pck", "PCK", "PICK LIST", "SAL-PCK-04", "pck_no", "so_no:str!:SO NO|whs_cd:str!:WHS CD", "save get search confirm"),
        ("dlv", "DLV", "DESPATCH", "SAL-DLV-05", "dlv_no", "pck_no:str!:PICK NO|carrier_cd:str!:CARRIER|parcels:int!:PARCELS|weight_kg:float:WEIGHT KG", "save get search post cancel label"),
        ("sinv", "SIN", "SALES INVOICE", "SAL-INV-06", "sinv_no", "dlv_no:str!:DLV NO|inv_dt:date!:INV DT", "save get search post cancel print"),
        ("rma", "RMA", "WARRANTY RETURN (RMA)", "SAL-RMA-07", "rma_no", "cust_cd:str!:CUST CD|itm_cd:str!:ITEM CD|serial_no:str!:SERIAL NO|fault_cd:str!:FAULT CD|remarks:str:REMARKS", "save get search approve receive close"),
        ("prc", "PRC", "PRICE LIST", "SAL-PRC-08", "price_list", "price_list:str!:PRICE LIST|itm_cd:str!:ITEM CD|price:float!:PRICE|valid_from:date!:VALID FROM", "get save search copy"),
        ("dsc", "DSC", "DISCOUNT", "SAL-DSC-10", "dsc_cd", "cust_cd:str!:CUST CD|dsc_pct:float!:DISC %|valid_to:date:VALID TO", "get save search"),
        ("scn", "SCN", "CUSTOMER CREDIT NOTE", "SAL-CRN-09", "scn_no", "cust_cd:str!:CUST CD|sinv_no:str!:INV NO|amount:float!:AMOUNT|reason_cd:str!:REASON CD", "save get post"),
        ("crd", "CRD", "CREDIT CONTROL", "SAL-CRD-11", "cust_cd", "cust_cd:str!:CUST CD|amount:float:AMOUNT", "check hold_list release"),
        ("frt", "FRT", "CARRIER BOOKING", "SAL-FRT-12", "awb_no", "dlv_no:str!:DLV NO|carrier_cd:str!:CARRIER|service_lvl:str:SERVICE", "quote book track label"),
        ("edi", "EDI", "EDI MESSAGES", "SAL-EDI-13", "msg_id", "partner_cd:str!:PARTNER|msg_id:str:MSG ID|payload:str:PAYLOAD", "ord_in ord_ack desadv_out invoic_out err_list"),
        ("fcs", "FCS", "SALES FORECAST", "SAL-FCS-14", "fcs_id", "itm_cd:str!:ITEM CD|period:str!:PERIOD|qty:int!:QTY", "save get upload"),
        ("com", "COM", "SALES COMMISSION", "SAL-COM-15", "period", "period:str!:PERIOD|rep:str:REP", "run get"),
        ("srl", "SRL", "SERIAL REGISTRATION", "SAL-SRL-16", "serial_no", "serial_no:str!:SERIAL NO|itm_cd:str!:ITEM CD|cust_cd:str:CUST CD|sold_dt:date:SOLD DT", "reg get search"),
        ("dmo", "DMO", "DEMO BIKE", "SAL-DMO-17", "dmo_no", "itm_cd:str!:ITEM CD|serial_no:str!:SERIAL NO|cust_cd:str!:CUST CD|return_dt:date!:RETURN DT", "save get search close"),
    ]),
    "PRD": ("production", "Production", [
        ("wo", "WO", "WORK ORDER", "PRD-WO-01", "wo_no", "itm_cd:str!:ITEM CD|qty:int!:QTY|start_dt:date!:START DT|wc_cd:str:WORK CENTRE|cc_cd:str!:CC CD", "save get search release close cancel"),
        ("bom", "BOM", "BILL OF MATERIALS", "PRD-BOM-02", "parent", "parent:str!:PARENT ITEM|component:str!:COMPONENT|qty:float!:QTY PER|scrap_pct:float:SCRAP %", "get save search copy explode where_used"),
        ("rtg", "RTG", "ROUTING", "PRD-RTG-03", "itm_cd", "itm_cd:str!:ITEM CD|op_no:int!:OP NO|wc_cd:str!:WORK CENTRE|std_min:float!:STD MIN", "get save search"),
        ("bkf", "BKF", "BACKFLUSH", "PRD-BKF-08", "wo_no", "wo_no:str!:WO NO|qty:int!:QTY COMPLETED", "post get reverse"),
        ("opr", "OPR", "OPERATION CONFIRMATION", "PRD-OPR-04", "wo_no", "wo_no:str!:WO NO|op_no:int!:OP NO|qty_ok:int!:QTY OK|qty_rej:int:QTY REJ", "save get search"),
        ("mrp", "MRP", "MRP RUN", "PRD-MRP-09", "run_id", "horizon_days:int:HORIZON|ou_cd:str:OU CD", "run get exceptions firm"),
        ("mps", "MPS", "MASTER SCHEDULE", "PRD-MPS-05", "itm_cd", "itm_cd:str!:ITEM CD|week:str!:WEEK|qty:int!:QTY", "save get search"),
        ("ecn", "ECN", "ENGINEERING CHANGE", "PRD-ECN-06", "ecn_no", "itm_cd:str!:ITEM CD|change:str!:CHANGE TEXT|eff_dt:date!:EFFECTIVE DT|reason:str:REASON", "save get search approve release"),
        ("qin", "QIN", "INCOMING INSPECTION", "QA-INS-01", "qin_no", "grn_no:str!:GRN NO|sample_qty:int!:SAMPLE QTY|aql:str:AQL|result:str:PASS/FAIL", "save get search post reject"),
        ("ncr", "NCR", "NON-CONFORMANCE REPORT", "QA-NCR-02", "ncr_no", "grn_no:str:GRN NO|itm_cd:str!:ITEM CD|defect_cd:str!:DEFECT CD|qty:int!:QTY|descr:str!:DESCRIPTION", "save get search close"),
        ("btt", "BTT", "BATTERY END-OF-LINE TEST", "QA-BTT-03", "serial_no", "serial_no:str!:PACK SERIAL|itm_cd:str!:ITEM CD|ocv:float!:OCV (V)|ir_mohm:float!:IR (MOHM)|result:str!:PASS/FAIL", "save get search"),
        ("cal", "CAL", "CALIBRATION", "QA-CAL-04", "gauge_no", "gauge_no:str!:GAUGE NO|cal_dt:date!:CAL DT|due_dt:date!:DUE DT", "save get due"),
        ("wc", "WC", "WORK CENTRE", "PRD-WC-10", "wc_cd", "wc_cd:str!:WORK CENTRE|name:str!:NAME|hrs_per_day:float:HRS/DAY", "get save list"),
        ("shf", "SHF", "SHIFT", "PRD-SHF-11", "shf_cd", "shf_cd:str!:SHIFT|start:str!:START|end:str!:END", "get save"),
        ("scp", "SCP", "PRODUCTION SCRAP", "PRD-SCP-12", "scp_no", "wo_no:str!:WO NO|itm_cd:str!:ITEM CD|qty:int!:QTY|reason_cd:str!:REASON CD", "save get post"),
        ("cap", "CAP", "CAPACITY", "PRD-CAP-13", "wc_cd", "wc_cd:str:WORK CENTRE|week:str:WEEK", "query load"),
        ("mnt", "MNO", "MAINTENANCE ORDER", "PRD-MNT-07", "mno_no", "asset_cd:str!:ASSET|fault:str!:FAULT|priority:str:PRIORITY|cc_cd:str!:CC CD", "save get search close"),
        ("tool", "TOL", "TOOL MASTER", "PRD-TOL-14", "tool_cd", "tool_cd:str!:TOOL|descr:str!:DESCR|life_cycles:int:LIFE", "get save"),
        ("pkb", "PKB", "PRODUCTION KANBAN", "PRD-PKB-15", "pkb_no", "itm_cd:str!:ITEM CD|wc_cd:str!:WORK CENTRE|qty:int!:QTY", "save get signal"),
    ]),
    "ADM": ("admin", "System Administration", [
        ("usr", "USR", "USER", "SYS-USR-01", "user_id", "user_id:str!:USER ID|name:str!:NAME|role_cd:str!:ROLE|ou_cd:str!:OU CD|appr_limit:float:APPR LIMIT|manager_id:str:MANAGER|default_cc:str:DEFAULT CC", "create update lock unlock search pwd_reset disable"),
        ("role", "ROL", "ROLE", "SYS-ROL-02", "role_cd", "role_cd:str!:ROLE|descr:str:DESCR|svc:str:SERVICE", "get save svc_add svc_remove list"),
        ("dlg", "DLG", "APPROVAL DELEGATION", "SYS-DLG-03", "dlg_no", "from_user:str!:FROM USER|to_user:str!:TO USER|from_dt:date!:FROM DT|to_dt:date!:TO DT", "save get cancel list"),
        ("par", "PAR", "SYSTEM PARAMETER", "SYS-PAR-04", "par_cd", "par_cd:str!:PARAMETER|value:str!:VALUE|ou_cd:str:OU CD", "get set list hist"),
        ("seq", "SEQ", "DOCUMENT SEQUENCE", "SYS-SEQ-05", "doc_type", "doc_type:str!:DOC TYPE|prefix:str:PREFIX|next_no:int:NEXT NO", "get set list"),
        ("job", "JOB", "BATCH JOB", "SYS-JOB-06", "job_cd", "job_cd:str!:JOB CD|params:str:PARAMS|run_at:str:RUN AT", "submit status list cancel log schedule"),
        ("aud", "AUD", "AUDIT TRAIL", "SYS-AUD-07", "id", "user_id:str:USER ID|svc:str:SERVICE|from_dt:date!:FROM DT|to_dt:date:TO DT", "query export"),
        ("ou", "OU", "ORGANISATION UNIT", "SYS-OU-08", "ou_cd", "ou_cd:str!:OU CD|name:str!:NAME|state:str!:COUNTRY CD (2)|city:str:CITY", "get list save"),
        ("cc", "CC", "COST CENTRE", "FIN-CC-01", "cc_cd", "cc_cd:str!:CC CD|name:str!:NAME|owner:str!:OWNER|ou_cd:str:OU CD", "save close reopen"),
        ("bud", "BUD", "BUDGET", "FIN-BUD-02", "cc_cd", "cc_cd:str!:CC CD|period:str!:PERIOD|amount:float!:AMOUNT", "save transfer query"),
        ("ses", "SES", "SESSION", "SYS-SES-09", "ses_id", "user_id:str:USER ID", "list kill"),
        ("lic", "LIC", "LICENCE", "SYS-LIC-10", "lic_id", "", "status"),
        ("ntf", "NTF", "NOTIFICATION", "SYS-NTF-11", "id", "id:str:QUEUE ID|tpl_cd:str:TEMPLATE", "queue_list retry tpl_get tpl_save"),
        ("prt", "PRT", "PRINT FORMS", "SYS-PRT-12", "form_cd", "form_cd:str:FORM", "list form_get"),
        ("imp", "IMP", "DATA IMPORT", "SYS-IMP-13", "imp_id", "imp_type:str!:IMPORT TYPE|file_ref:str!:FILE REF", "upload validate post status"),
        ("api", "API", "SERVICE ACCOUNT KEY", "SYS-API-14", "key_id", "user_id:str!:SERVICE ACCT|valid_to:date:VALID TO", "key_issue key_revoke key_list"),
        ("sys", "SYS", "SYSTEM", "SYS-SYS-15", "", "", "ping version health"),
        ("cfg", "CFG", "MENU CONFIG", "SYS-CFG-16", "menu_cd", "role_cd:str!:ROLE|menu_cd:str!:MENU", "get save"),
    ]),
}
OP_TITLES = {"save": "SAVE", "get": "GET", "search": "LIST", "post": "POST", "cancel": "CANCEL", "approve": "APPROVE",
             "reject": "REJECT", "release": "RELEASE", "close": "CLOSE", "list": "LIST", "update": "UPDATE", "block": "BLOCK"}
WRITE_OPS = {"save", "post", "cancel", "approve", "reject", "release", "close", "update", "block", "hold", "entry", "freeze",
             "trace_x", "signal", "generate", "settle", "run", "override", "propose", "file", "verify", "adjust", "reverse",
             "open", "submit", "pay", "confirm", "amend", "convert", "label", "print", "receive", "copy", "book", "upload",
             "reg", "create", "lock", "unlock", "pwd_reset", "disable", "svc_add", "svc_remove", "set", "schedule", "kill",
             "retry", "tpl_save", "validate", "key_issue", "key_revoke", "firm", "val_run", "abc_run", "uom_conv", "transfer",
             "reopen", "ord_in", "ord_ack", "desadv_out", "invoic_out", "load"}
XML_SERVICES = {"edi_ord_in", "edi_ord_ack", "edi_desadv_out", "edi_invoic_out", "edi_err_list", "pay_propose", "pay_get",
                "pay_approve", "pay_release", "pay_file", "pay_cancel", "pay_search", "bnk_save", "bnk_get", "bnk_verify",
                "bnk_block", "bnk_search", "frt_quote", "frt_book", "frt_track", "frt_label"}


def generated_services(existing):
    out = []
    for mod, (folder, mtitle, ents) in GEN.items():
        for ent, code, title, screen, key, fspec, ops in ents:
            fields = _fields(fspec)
            for op in re.findall(r"\w+(?:\([^)]*\))?", ops):
                own = None
                if "(" in op:
                    op, inner = op.split("(", 1)
                    own = _fields(inner.rstrip(")").replace(";", "|"))
                name = f"{ent}_{op}"
                if name in existing:
                    continue
                existing.add(name)
                keyf = dict(name=key, type="str", required=True, desc=key.upper().replace("_", " ")) if key else None
                if own is not None:
                    flds = own
                elif op in ("save", "create", "fetch", "propose", "reg", "quote", "book", "upload") or (op == "set" and ent == "par"):
                    flds = [dict(f) for f in fields]
                elif op in ("get", "trace", "status", "log", "explode", "where_used", "stmt", "ageing", "query", "track", "label",
                            "print", "verify", "due", "file", "check", "rc_list", "form_get", "tpl_get", "hist"):
                    flds = [keyf] if keyf else []
                    if op == "query" and fields:
                        flds = [dict(f, required=False) for f in fields[:3]]
                elif op in ("search", "list", "hold_list", "exceptions", "queue_list", "key_list", "err_list"):
                    flds = [dict(f, required=False) for f in fields[:3]] + [dict(name="status", type="str", required=False, desc="STATUS")]
                    if op in ("list", "queue_list", "key_list", "err_list", "hold_list", "exceptions"):
                        flds = flds[:1]
                elif op in ("cancel", "reject", "block", "lock", "disable", "kill", "key_revoke", "reverse", "hold"):
                    flds = ([keyf] if keyf else []) + [dict(name="reason", type="str", required=op in ("cancel", "reject"), desc="REASON")]
                elif op in ("update", "amend", "set", "adjust", "copy", "transfer", "override", "credit", "schedule", "settle"):
                    flds = ([keyf] if keyf else []) + [dict(f, required=False) for f in fields if f["name"] != key][:4]
                elif op in ("ping", "version", "health", "status") and not key:
                    flds = []
                else:
                    flds = ([keyf] if keyf else []) + [dict(name="comment", type="str", required=False, desc="COMMENT")]
                flds = [f for f in flds if f][:12]
                errs = _gen_errors(mod, code, title, op, flds)
                out.append(dict(name=name, module=mod, title=f"{title} {OP_TITLES.get(op, op.upper().replace('_', ' '))}",
                                kind="write" if op in WRITE_OPS else "read",
                                screen=screen if op not in ("search", "list") or True else None, fields=flds, errors=errs,
                                warnings=[], procedures=[f"sp_{ent}_{op}"] if op in WRITE_OPS else [], real=False,
                                since=_since(mod, ent), fmt="xml" if name in XML_SERVICES else "yaml", entity=ent, op=op,
                                folder=folder))
    return out


def _since(mod, ent):
    if mod == "SAL" and ent in ("edi", "frt"):
        return "6.2"
    if ent in ("btt", "lot", "srl", "api", "kbn", "pkb"):
        return "7.2.0"
    if ent in ("dlg", "csg", "dmo", "ecn"):
        return "7.1"
    return "7.0"


def _gen_errors(mod, code, title, op, flds):
    thing = title.split("(")[0].strip()
    e = []
    if op not in ("save", "create", "search", "list", "run", "propose", "upload", "ping", "version", "health", "reg", "quote"):
        e.append((f"ERR-{code}-0001", f"{thing} NOT FOUND"))
    if op in ("post", "approve", "release", "confirm", "submit", "freeze"):
        e.append((f"ERR-{code}-0007", f"{thing} NOT IN DRAFT (<status>)"))
    if op in ("cancel", "amend", "update", "close"):
        e.append((f"ERR-{code}-0801", f"{thing} CLOSED (<status>)"))
    names = {f["name"] for f in flds}
    if "qty" in names:
        e.append((f"ERR-{code}-0201", "QTY MUST BE > 0"))
    if names & {"itm_cd", "component", "parent"}:
        e.append(("ERR-ITM-0011", "ITEM NOT FOUND OR INACTIVE"))
    if "sup_cd" in names and op not in ("search", "get"):
        e.append(("ERR-SUP-0030", "SUPPLIER NOT FOUND"))
    if "cc_cd" in names and op not in ("search", "get", "query"):
        e.append(("ERR-CC-0009", "COST CENTRE NOT FOUND"))
    if any(f["type"] == "date" and f["name"] in ("start_dt", "req_dt", "cnt_dt", "eff_dt", "run_dt") for f in flds):
        e.append((f"ERR-{code}-0105", "DATE IN PAST"))
    if op == "approve":
        e.append(("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED"))
        e.append(("ERR-APR-0004", "VALUE ABOVE YOUR LIMIT"))
    extra = SPECIAL_ERRORS.get((code, op), [])
    return [dict(code=c, msg=m) for c, m in e + extra]


SPECIAL_ERRORS = {
    ("TXF", "save"): [("ERR-TXF-0310", "FROM AND TO WAREHOUSE ARE THE SAME"), ("ERR-STK-0102", "INSUFFICIENT STOCK (<available>)")],
    ("ADJ", "approve"): [("ERR-ADJ-0420", "ADJUSTMENT ABOVE STORES LIMIT, NEEDS PLANT HEAD")],
    ("CNT", "freeze"): [("ERR-CNT-0230", "OPEN TRANSACTIONS IN COUNT AREA")],
    ("CNT", "post"): [("ERR-CNT-0240", "VARIANCE ABOVE TOLERANCE, RECOUNT REQUIRED"), ("W-CNT-241", None)],
    ("RTV", "save"): [("ERR-RTV-0204", "QTY EXCEEDS QTY RECEIVED (<qty>)"), ("ERR-RTV-0230", "GRN ALREADY INVOICED, RAISE DEBIT NOTE")],
    ("MRN", "save"): [("ERR-STK-0102", "INSUFFICIENT STOCK (<available>)"), ("ERR-WO-0007", "WORK ORDER NOT RELEASED")],
    ("LOT", "hold"): [("ERR-LOT-0301", "LOT ALREADY ON HOLD")],
    ("QCH", "release"): [("ERR-QCH-0350", "INSPECTION NOT POSTED")],
    ("INV", "save"): [("ERR-INV-0118", "DUPLICATE SUPPLIER INVOICE NO"), ("ERR-PO-0001", "PO NOT FOUND"), ("ERR-TAX-0101", "INVALID TAX CODE")],
    ("INV", "post"): [("ERR-MAT-0410", "MATCH FAILED: PRICE OUTSIDE TOLERANCE"), ("ERR-MAT-0411", "MATCH FAILED: QTY INVOICED > QTY RECEIVED"), ("ERR-PER-0003", "AP PERIOD CLOSED (<period>)")],
    ("MAT", "run"): [("ERR-MAT-0410", "MATCH FAILED: PRICE OUTSIDE TOLERANCE"), ("ERR-MAT-0411", "MATCH FAILED: QTY INVOICED > QTY RECEIVED"), ("ERR-MAT-0412", "NO GRN FOR PO LINE")],
    ("MAT", "override"): [("ERR-MAT-0420", "OVERRIDE NEEDS AP-MGR ROLE")],
    ("PAY", "approve"): [("ERR-PAY-0430", "RUN APPROVER SAME AS PROPOSER"), ("ERR-BNK-0101", "BANK DETAILS NOT VERIFIED (<sup_cd>)")],
    ("PAY", "file"): [("ERR-PAY-0440", "RUN NOT APPROVED"), ("ERR-BNK-0101", "BANK DETAILS NOT VERIFIED (<sup_cd>)")],
    ("BNK", "save"): [("ERR-BNK-0118", "IBAN CHECK DIGITS INVALID"), ("W-BNK-120", None)],
    ("BNK", "verify"): [("ERR-BNK-0125", "CALL-BACK NOT RECORDED")],
    ("PER", "close"): [("ERR-PER-0010", "UNPOSTED DOCUMENTS IN PERIOD"), ("ERR-PER-0011", "GRNI ACCRUAL NOT RUN")],
    ("EXP", "submit"): [("ERR-EXP-0230", "RECEIPT MISSING FOR LINE ABOVE LIMIT")],
    ("EXP", "approve"): [("ERR-EXP-0240", "CLAIM OLDER THAN 90 DAYS")],
    ("SO", "confirm"): [("ERR-CRD-0207", "CREDIT LIMIT EXCEEDED (<cust_cd>)"), ("ERR-PRC-0001", "NO PRICE FOR ITEM ON PRICE LIST")],
    ("SO", "save"): [("ERR-CUS-0031", "CUSTOMER ON HOLD"), ("ERR-PRC-0001", "NO PRICE FOR ITEM ON PRICE LIST")],
    ("DLV", "post"): [("ERR-DLV-0320", "LITHIUM BATTERY LABEL NOT PRINTED"), ("ERR-FRT-0501", "CARRIER BOOKING FAILED")],
    ("DLV", "save"): [("ERR-DLV-0301", "PICK NOT CONFIRMED")],
    ("RMA", "approve"): [("ERR-RMA-0210", "SERIAL NOT REGISTERED"), ("ERR-RMA-0211", "OUT OF WARRANTY (<sold_dt>)")],
    ("FRT", "book"): [("ERR-FRT-0501", "CARRIER BOOKING FAILED"), ("ERR-FRT-0510", "DANGEROUS GOODS NOT ACCEPTED FOR SERVICE")],
    ("EDI", "ord_in"): [("ERR-EDI-0101", "PARTNER NOT SET UP"), ("ERR-EDI-0140", "UNKNOWN BUYER ITEM CODE"), ("ERR-EDI-0150", "SYNTAX ERROR IN SEGMENT (<segment>)")],
    ("WO", "release"): [("ERR-WO-0310", "COMPONENT SHORTAGE (<itm_cd>)"), ("ERR-BOM-0001", "NO ACTIVE BOM")],
    ("BOM", "save"): [("ERR-BOM-0120", "CIRCULAR BOM REFERENCE")],
    ("ECN", "release"): [("ERR-ECN-0220", "OPEN WORK ORDERS ON OLD REVISION")],
    ("QIN", "post"): [("ERR-QIN-0230", "SAMPLE SIZE BELOW AQL PLAN"), ("W-QIN-231", None)],
    ("BTT", "save"): [("ERR-BTT-0110", "SERIAL ALREADY TESTED"), ("ERR-BTT-0120", "OCV OUT OF RANGE")],
    ("USR", "create"): [("ERR-USR-0118", "USER ID ALREADY EXISTS"), ("ERR-USR-0130", "LIMIT ABOVE APPROVAL MATRIX FOR ROLE")],
    ("USR", "pwd_reset"): [("ERR-SEC-0012", "PASSWORD DOES NOT MEET POLICY")],
    ("DLG", "save"): [("ERR-DLG-0210", "DELEGATE ROLE LOWER THAN DELEGATOR")],
    ("PAR", "set"): [("ERR-PAR-0101", "UNKNOWN PARAMETER"), ("ERR-PAR-0110", "VALUE OUT OF RANGE")],
    ("JOB", "submit"): [("ERR-JOB-0101", "JOB ALREADY RUNNING")],
    ("API", "key_issue"): [("ERR-API-0120", "SERVICE ACCOUNT HAS NO OWNER")],
    ("CC", "close"): [("ERR-CC-0310", "OPEN DOCUMENTS ON COST CENTRE")],
    ("BUD", "transfer"): [("ERR-BUD-0207", "BUDGET EXCEEDED FOR <cc_cd>")],
}
for k, v in SPECIAL_ERRORS.items():
    SPECIAL_ERRORS[k] = [(c, m if m is not None else {"W-CNT-241": "VARIANCE NOTED, WITHIN TOLERANCE",
                                                        "W-BNK-120": "BANK DETAILS CHANGED, PAYMENTS HELD UNTIL VERIFIED",
                                                        "W-QIN-231": "PASSED WITH CONCESSION"}[c]) for c, m in v]


class Catalog:
    def __init__(self):
        self.real = real_services()
        names = {s["name"] for s in self.real}
        self.gen = generated_services(names)
        for s in self.real:
            s["folder"] = "purchase" if s["module"] == "PUR" else "inventory"
        self.services = self.real + self.gen
        self.by_name = {s["name"]: s for s in self.services}
        self.errors = self._errors()

    def _errors(self):
        errs = {}
        for s in self.services:
            for e in s["errors"] + [dict(code=c, msg=m) for c, m in COMMON]:
                x = errs.setdefault(e["code"], dict(code=e["code"], msg=e["msg"], services=[], module=e["code"].split("-")[1]))
                if s["name"] not in x["services"]:
                    x["services"].append(s["name"])
            for w in s["warnings"]:
                x = errs.setdefault(w, dict(code=w, msg="COST CENTRE CLOSED, DOCUMENT SAVED AS DRAFT" if w == "W-CC-114" else w,
                                            services=[], module=w.split("-")[1]))
                x["services"].append(s["name"])
        extra = [("ERR-SEC-0002", "INVALID CREDENTIALS"), ("ERR-SEC-0003", "NO SUCH USER"), ("ERR-SEC-0007", "USER NOT MAPPED TO ORGANISATION UNIT"),
                 ("ERR-SYS-0404", "SERVICE <svc> NOT FOUND"), ("ERR-SEC-0009", "SESSION EXPIRED, SIGN IN AGAIN"),
                 ("W-SUP-0207", "UN38.3 CERTIFICATE MISSING OR EXPIRED"), ("ERR-SYS-0601", "DATABASE LOCK TIMEOUT, RETRY")]
        for c, m in extra:
            errs.setdefault(c, dict(code=c, msg=m, services=[], module=c.split("-")[1]))
        return dict(sorted(errs.items()))


# ------------------------------------------------------------------------------------------------ batch jobs
JOBS = [
    ("JOB-PUR-014", "Draft orders report", "Daily 07:00", "OU=ALL", "Lists purchase orders in status DR with their warning code (MAN-PUR-72 §22.4)", "DOKAFOR"),
    ("JOB-PUR-022", "Certificate expiry report", "Monthly, first working day 06:00", "DAYS=90;CERT=UN38.3", "Supplier certificates expiring within DAYS days, by certificate type (MAN-PUR-72 §22.6)", "LMORENO"),
    ("JOB-PUR-031", "Rate contract expiry report", "Weekly, Monday 06:30", "DAYS=45", "Rate contracts ending within DAYS days", "DOKAFOR"),
    ("JOB-PUR-033", "Orders pending approval reminder", "Daily 08:00 and 14:00", "AGE_DAYS=2", "E-mails approvers about documents waiting longer than AGE_DAYS", "DOKAFOR"),
    ("JOB-PUR-040", "Price variance report", "Monthly, 3rd working day", "TOL_PCT=2", "Released orders whose rate differs from the contract rate by more than TOL_PCT", "DOKAFOR"),
    ("JOB-PUR-051", "Open orders by supplier", "Weekly, Friday 16:00", "", "Orders in AP or RL not fully received (MAN-PUR-72 §22.2)", "LMORENO"),
    ("JOB-INV-040", "Items below reorder level", "Daily 06:15", "WHS=WH-MAN-STR,WH-LDS-STR", "Same as service stk_reorder_list, e-mailed to buyers", "CSHAW"),
    ("JOB-INV-044", "Cycle count list", "Daily 05:45", "PLAN=CCP-A", "Bins to count today from the cycle count plan", "CSHAW"),
    ("JOB-INV-050", "Stock valuation", "Monthly, last calendar day 23:00", "METHOD=STD", "Values stock at standard cost by warehouse", "GWHITAKER"),
    ("JOB-INV-052", "Quality hold ageing", "Daily 07:30", "DAYS=3", "Receipts in WH-MAN-QC or WH-LDS-QC longer than DAYS", "PJANSEN"),
    ("JOB-AP-010", "Three-way match", "Every 30 minutes, 06:00-20:00", "TOL_PCT=2;TOL_ABS=50", "Matches posted invoices to orders and receipts", "MKOWALSKI"),
    ("JOB-AP-030", "Payment proposal", "Tuesday and Thursday 10:00", "BANK=NBC-MAIN", "Proposes due, matched invoices for the payment run (SOP-AP-003)", "MKOWALSKI"),
    ("JOB-AP-031", "Payment file", "Tuesday and Thursday 14:30", "FORMAT=STD18", "Writes the bank payment file for the approved run", "MKOWALSKI"),
    ("JOB-AP-040", "GRNI accrual", "Monthly, working day 1, 21:00", "", "Goods received not invoiced accrual", "GWHITAKER"),
    ("JOB-AP-045", "VAT reverse-charge listing", "Monthly, working day 2", "", "Invoices on -RC tax codes for the VAT return", "GWHITAKER"),
    ("JOB-SAL-010", "EDI inbound orders", "Every 10 minutes", "PARTNER=ALL", "Reads ORDERS messages from the EDI mailbox", "IMORGAN"),
    ("JOB-SAL-012", "EDI outbound despatch advice", "Every 10 minutes", "", "Sends DESADV for posted despatches", "IMORGAN"),
    ("JOB-SAL-020", "Credit hold report", "Daily 07:00", "", "Sales orders on credit hold", "IMORGAN"),
    ("JOB-SAL-031", "Carrier manifest", "Daily 16:45", "CARRIER=MOORLAND", "Closes the day's parcels with the carrier", "CSHAW"),
    ("JOB-PRD-010", "MRP run", "Nightly 02:00", "HORIZON=120", "Net requirements and planned orders", "SBERG"),
    ("JOB-PRD-015", "Backflush", "Every hour", "", "Posts component issues for completed work orders", "SBERG"),
    ("JOB-PRD-022", "Battery end-of-line test upload", "Every 15 minutes", "RIG=BTR-01,BTR-02", "Loads test-rig results into QA-BTT-03", "PJANSEN"),
    ("JOB-SYS-001", "Nightly backup", "Daily 01:30", "", "Full database backup; Ledgerline is read-only from 01:30 to 01:50", "RPRYCE"),
    ("JOB-SYS-004", "Session clean-up", "Every 5 minutes", "", "Closes idle sessions (see SYS.SESSION_TIMEOUT)", "JFLETCHER"),
    ("JOB-SYS-009", "Notification sender", "Every minute", "", "Sends queued e-mails and SMS", "JFLETCHER"),
    ("JOB-SYS-012", "Audit trail archive", "Monthly, 1st, 03:00", "KEEP_MONTHS=84", "Moves audit rows older than KEEP_MONTHS to the archive schema", "RPRYCE"),
    ("JOB-SYS-015", "Service account review report", "Quarterly, first Monday", "", "Lists service accounts with their services and last use (POL-ITS-008)", "RPRYCE"),
    ("JOB-SYS-020", "Year-end sequence reset", "Yearly, 1 January 00:05", "DOC=PR,PO,GRN", "Starts the new year's document numbers", "JFLETCHER"),
]


def more_jobs():
    """Pad the batch-job catalogue with the long tail every 28-year-old ERP has."""
    out = list(JOBS)
    tail = [("PUR", "Supplier performance extract"), ("PUR", "Purchase history archive"), ("PUR", "Unreleased approved orders"),
            ("PUR", "Duplicate supplier VAT scan"), ("PUR", "Blocked supplier open orders"), ("INV", "Slow-moving stock"),
            ("INV", "Negative stock check"), ("INV", "Bin occupancy"), ("INV", "Lot expiry"), ("INV", "Transfer in transit"),
            ("INV", "Kanban signal sweep"), ("INV", "Returnable packaging balance"), ("AP", "Duplicate invoice check"),
            ("AP", "Supplier statement reconciliation"), ("AP", "Invoice on hold ageing"), ("AP", "Advance payment adjustment"),
            ("AP", "Expense claim reminder"), ("AP", "Currency rate import"), ("SAL", "Price list publish"),
            ("SAL", "Warranty claim ageing"), ("SAL", "Serial registration reminder"), ("SAL", "Commission calculation"),
            ("SAL", "Back-order report"), ("SAL", "Demo bike return reminder"), ("PRD", "Work order close"),
            ("PRD", "Capacity load"), ("PRD", "Engineering change effectivity"), ("PRD", "Scrap summary"),
            ("PRD", "Calibration due list"), ("PRD", "Maintenance plan generate"), ("SYS", "User access recertification"),
            ("SYS", "Locked users report"), ("SYS", "Licence usage"), ("SYS", "Parameter change log"),
            ("SYS", "Printer queue purge"), ("SYS", "Import file sweep"), ("SYS", "Index rebuild"), ("SYS", "Statistics refresh"),
            ("SYS", "Temp table purge"), ("SYS", "Disk space monitor")]
    nums = {}
    for mod, name in tail:
        nums[mod] = nums.get(mod, 60) + 3
        out.append((f"JOB-{mod}-{nums[mod]:03d}", name, ["Daily 05:00", "Weekly, Sunday 22:00", "Monthly, 1st, 04:00", "Daily 23:30"][len(out) % 4],
                    "", f"{name}.", {"PUR": "DOKAFOR", "INV": "CSHAW", "AP": "MKOWALSKI", "SAL": "IMORGAN", "PRD": "SBERG", "SYS": "JFLETCHER"}[mod]))
    return out


PARAMETERS = [
    ("PUR.DIR_LIMIT", "50000", "Direct-order limit, gross incl. VAT (GBP). Shipped default 50000. Changes to 25000 on 30-11-2026 evening (AMD-PUR-2026-03)."),
    ("PUR.CERT_CHK", "N", "Certificate check on PUR-PO-01 for lithium-cell items (7.2.3-P4). Y gives warning W-SUP-0207 on Save; the order still saves. Not switched on at Northbridge (CAB 07-10-2026)."),
    ("PUR.FETCH_REQ", "Y", "Save needs Fetch for the current supplier and item (7.2.3)."),
    ("PUR.PRICE_TOL_PCT", "2", "Tolerance used by the price variance report."),
    ("SYS.SESSION_TIMEOUT", "15", "Idle minutes before a session is closed. Shipped default 20 before 7.2.3-P2; 15 after."),
    ("SYS.PWD_MIN_LEN", "12", "Minimum password length (company policy POL-ITS-008; shipped default 8)."),
    ("SYS.PWD_EXPIRY_DAYS", "60", "Password expiry in days (company policy POL-ITS-008; shipped default 90)."),
    ("SYS.LOCK_ATTEMPTS", "3", "Wrong passwords before the user ID is locked."),
    ("SYS.LOCK_MINUTES", "30", "Minutes a locked user ID stays locked."),
    ("AP.MATCH_TOL_PCT", "2", "Three-way match price tolerance, per cent."),
    ("AP.MATCH_TOL_ABS", "50", "Three-way match price tolerance, pounds per invoice line."),
    ("AP.PAY_DAYS", "TUE,THU", "Payment run days."),
    ("INV.CNT_TOL_PCT", "1.5", "Cycle count tolerance by value, per cent (7.2.2; was 2.0)."),
    ("INV.NEG_STOCK", "N", "Allow negative stock."),
    ("SAL.CREDIT_CHK", "Y", "Credit check on sales order confirm."),
    ("SAL.DG_LABEL_REQ", "Y", "Despatches with lithium batteries need the battery label printed before posting."),
]
