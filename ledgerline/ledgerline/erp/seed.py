"""Seed data for Northbridge Cycles, Manchester: a fictional e-bike maker running Ledgerline ERP 7.2.

Every name, code and number here is invented for the course.
The sandbox clock is fixed at Monday 26 October 2026, 09:00 GMT.
"""

TODAY = "2026-10-26"
NOW = "2026-10-26T09:00:00+00:00"

SCHEMA = """
CREATE TABLE org_unit(ou_cd TEXT PRIMARY KEY, name TEXT, state TEXT, city TEXT);
CREATE TABLE app_user(user_id TEXT PRIMARY KEY, name TEXT, role_cd TEXT, ou_cd TEXT, appr_limit REAL,
  manager_id TEXT, password TEXT, default_cc TEXT, email TEXT, slack TEXT);
CREATE TABLE role_perm(role_cd TEXT, svc TEXT);
CREATE TABLE item(itm_cd TEXT PRIMARY KEY, descr TEXT, uom_cd TEXT, cell_safety INT, category TEXT,
  active INT, reorder_lvl INT, avg_daily_issue INT);
CREATE TABLE supplier(sup_cd TEXT PRIMARY KEY, name TEXT, vat_no TEXT, state TEXT, city TEXT, status TEXT,
  pt_cd TEXT, created_by TEXT, created_on TEXT);
CREATE TABLE sup_cert(sup_cd TEXT, cert_type TEXT, doc_ref TEXT, valid_to TEXT, uploaded_by TEXT, uploaded_on TEXT);
CREATE TABLE sup_rate(sup_cd TEXT, itm_cd TEXT, rate REAL, valid_from TEXT, valid_to TEXT);
CREATE TABLE warehouse(whs_cd TEXT PRIMARY KEY, name TEXT, ou_cd TEXT);
CREATE TABLE stock(itm_cd TEXT, whs_cd TEXT, on_hand INT, allocated INT, on_order INT);
CREATE TABLE stk_ledger(id INTEGER PRIMARY KEY AUTOINCREMENT, itm_cd TEXT, whs_cd TEXT, dt TEXT, txn TEXT, qty INT, ref TEXT);
CREATE TABLE cost_centre(cc_cd TEXT PRIMARY KEY, name TEXT, status TEXT, closed_on TEXT, owner TEXT);
CREATE TABLE budget(cc_cd TEXT, period TEXT, amount REAL, committed REAL);
CREATE TABLE tax_code(tax_cd TEXT PRIMARY KEY, descr TEXT, rate REAL, kind TEXT);
CREATE TABLE pay_term(pt_cd TEXT PRIMARY KEY, descr TEXT, days INT);
CREATE TABLE doc_seq(doc_type TEXT PRIMARY KEY, prefix TEXT, next_no INT, width INT);
CREATE TABLE pr_hdr(pr_no TEXT PRIMARY KEY, ou_cd TEXT, pr_type TEXT, cc_cd TEXT, need_dt TEXT, whs_cd TEXT,
  remarks TEXT, status TEXT, raised_by TEXT, raised_on TEXT, approved_by TEXT, est_value REAL);
CREATE TABLE pr_line(pr_no TEXT, line_no INT, itm_cd TEXT, qty INT, uom_cd TEXT);
CREATE TABLE po_hdr(po_no TEXT PRIMARY KEY, ou_cd TEXT, sup_cd TEXT, pr_no TEXT, po_type TEXT, cc_cd TEXT,
  tax_cd TEXT, pt_cd TEXT, need_dt TEXT, whs_cd TEXT, status TEXT, basic_value REAL, tax_value REAL,
  gross_value REAL, created_by TEXT, created_on TEXT, approved_by TEXT, approved_on TEXT, released_on TEXT,
  client_ref TEXT, warn_cd TEXT);
CREATE TABLE po_line(po_no TEXT, line_no INT, itm_cd TEXT, qty INT, uom_cd TEXT, rate REAL);
CREATE TABLE approval(appr_id INTEGER PRIMARY KEY AUTOINCREMENT, doc_type TEXT, doc_no TEXT, approver TEXT,
  status TEXT, requested_by TEXT, requested_on TEXT, decided_on TEXT, comment TEXT);
CREATE TABLE ntf_queue(id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, recipient TEXT, subject TEXT,
  body TEXT, created_on TEXT);
CREATE TABLE fetch_tok(tok TEXT PRIMARY KEY, user_id TEXT, screen TEXT, ctx TEXT, created_on TEXT, used INT);
CREATE TABLE audit_trail(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, user_id TEXT, svc TEXT, payload TEXT,
  rc TEXT, err_cd TEXT);
"""

ORG_UNITS = [
    ("NBC-MAN-01", "Northbridge Cycles, Manchester plant", "GB", "Manchester"),
    ("NBC-LDS-01", "Northbridge Cycles, Leeds unit", "GB", "Leeds"),
]

# user_id, name, role, ou, approval limit (gross, incl. VAT), manager, password, default cost centre, email, slack
USERS = [
    ("ECLARKE", "Emma Clarke", "PUR-EXEC", "NBC-MAN-01", 250000, "DOKAFOR", "emma@123", "PRD-05",
     "emma.clarke@northbridgecycles.example", "@emma"),
    ("DOKAFOR", "Daniel Okafor", "PUR-MGR", "NBC-MAN-01", 1000000, "HWEBER", "daniel@123", "PRD-07",
     "daniel.okafor@northbridgecycles.example", "@daniel"),
    ("LMORENO", "Luis Moreno", "PUR-SR", "NBC-MAN-01", 500000, "DOKAFOR", "luis@123", "PRD-03",
     "luis.moreno@northbridgecycles.example", "@luis"),
    ("HWEBER", "Henrik Weber", "PLANT-HEAD", "NBC-MAN-01", 5000000, None, "henrik@123", "ADM-01",
     "henrik.weber@northbridgecycles.example", "@henrik"),
    ("ATANAKA", "Aiko Tanaka", "STORES", "NBC-MAN-01", 0, "DOKAFOR", "aiko@123", "PRD-05",
     "aiko.tanaka@northbridgecycles.example", "@aiko"),
    # The integration account IT created "for the bot". It can do everything, with no limit.
    ("SVC_AGENT", "Integration service account", "SYS-ADMIN", "NBC-MAN-01", 1e12, None, "svc@ledger", "PRD-05",
     "it-integration@northbridgecycles.example", None),
]

READ_SVCS = ["itm_search", "itm_get", "sup_search", "sup_get", "sup_cert_get", "sup_rate_get", "cc_list",
             "cc_get", "whs_list", "tax_list", "pt_list", "usr_get", "usr_roles", "stk_query", "stk_ledger",
             "pr_get", "pr_search", "po_get", "po_search", "po_hist", "po_pending_appr", "tax_compute",
             "bud_check", "pr_fetch", "po_fetch"]
ROLE_PERMS = {
    "PUR-EXEC": READ_SVCS + ["pr_save", "pr_submit", "po_save", "po_release", "po_amend", "po_cancel",
                             "sup_create", "sup_cert_upload", "ntf_send"],
    "PUR-SR": READ_SVCS + ["pr_save", "pr_submit", "po_save", "po_release", "po_amend", "po_cancel",
                           "sup_create", "sup_cert_upload", "ntf_send", "pr_approve", "po_approve", "po_reject"],
    "PUR-MGR": READ_SVCS + ["pr_approve", "po_approve", "po_reject", "po_release", "ntf_send"],
    "PLANT-HEAD": READ_SVCS + ["pr_approve", "po_approve", "po_reject", "ntf_send"],
    "STORES": READ_SVCS + ["ntf_send"],
    "SYS-ADMIN": ["*"],
}

# itm_cd, description, uom, cell_safety, category, active, reorder level, average daily issue
ITEMS = [
    ("BAT-500", "Battery pack, 36 V 500 Wh", "NOS", 1, "SPARES", 1, 3000, 600),
    ("BAT-500-R", "Battery pack, 36 V 500 Wh (refurbished)", "NOS", 1, "SPARES", 1, 0, 0),
    ("BAT-400-OLD", "Battery pack, 36 V 400 Wh (old model)", "NOS", 1, "SPARES", 0, 0, 0),
    ("BAT-375", "Battery pack, 36 V 375 Wh", "NOS", 1, "SPARES", 1, 1500, 250),
    ("BAT-750", "Battery pack, 48 V 750 Wh", "NOS", 1, "SPARES", 1, 600, 90),
    ("MNT-FRM-01", "Battery mount, down-tube, long", "NOS", 0, "COMPONENTS", 1, 20000, 4000),
    ("MNT-RCK-02", "Battery mount, rear rack, short", "NOS", 0, "COMPONENTS", 1, 20000, 4000),
    ("BEL-STD-01", "Bell, standard", "NOS", 0, "COMPONENTS", 1, 12000, 3500),
    ("BRK-PAD-01", "Brake pads, disc (pair)", "NOS", 0, "COMPONENTS", 1, 12000, 3500),
    ("MTR-HUB-250", "Hub motor, 250 W", "NOS", 1, "RAW", 1, 15000, 6000),
    ("CHG-4A-01", "Charger, 4 A", "NOS", 1, "COMPONENTS", 1, 15000, 6000),
    ("BOX-BIKE-01", "Carton, bike shipping", "NOS", 0, "PACKING", 1, 20000, 6000),
]

# sup_cd, name, vat_no, country, city, status, pay terms
SUPPLIERS = [
    ("VC-EIN-0042", "Voltway Cells", "NL859312774B01", "NL", "Eindhoven", "ACTIVE", "N45"),
    ("VC-EIN-0009", "Voltway Cells (old code, do not use)", "NL859312774B01", "NL", "Eindhoven", "BLOCKED", "N45"),
    ("VPC-ROT-0107", "Voltway Paints & Coatings", "NL814205366B01", "NL", "Rotterdam", "ACTIVE", "N30"),
    ("PB-MAN-0017", "Pennine Brakes", "GB284117390", "GB", "Manchester", "ACTIVE", "N30"),
    ("CC-SAL-0031", "Castlefield Chargers", "GB302958146", "GB", "Salford", "ACTIVE", "N30"),
    ("AM-BIR-0008", "Albion Motors", "GB197463025", "GB", "Birmingham", "ACTIVE", "N60"),
    ("IP-MAN-0055", "Irwell Packaging", "GB415870233", "GB", "Manchester", "ACTIVE", "N30"),
    ("NC-GDA-0063", "Nordic Cell Co.", "PL5842736190", "PL", "Gdańsk", "ACTIVE", "N45"),
]
# Brightcell Energy (Lyon) is deliberately NOT in the master: scenario 4 is a new, cheaper supplier.

SUP_CERTS = [
    ("VC-EIN-0042", "UN38.3", "UN38.3-TR/VC/2026/118", "2027-03-31", "LMORENO", "2026-04-02"),
    ("CC-SAL-0031", "UN38.3", "UN38.3-TR/CC/2026/044", "2027-01-31", "LMORENO", "2026-02-10"),
    ("AM-BIR-0008", "UN38.3", "UN38.3-TR/AM/2026/301", "2027-06-30", "LMORENO", "2026-07-01"),
    ("NC-GDA-0063", "UN38.3", "UN38.3-TR/NC/2025/090", "2026-09-30", "LMORENO", "2025-10-01"),  # expired
]

SUP_RATES = [
    ("VC-EIN-0042", "BAT-500", 114.00, "2026-04-01", "2026-09-30"),
    ("VC-EIN-0042", "BAT-500", 119.00, "2026-10-01", "2027-03-31"),
    ("VC-EIN-0042", "BAT-375", 92.00, "2026-04-01", "2027-03-31"),
    ("VC-EIN-0042", "BAT-750", 146.00, "2026-04-01", "2027-03-31"),
    ("VC-EIN-0042", "MNT-FRM-01", 18.50, "2026-04-01", "2027-03-31"),
    ("VC-EIN-0042", "MNT-RCK-02", 15.75, "2026-04-01", "2027-03-31"),
    ("NC-GDA-0063", "BAT-500", 111.00, "2026-04-01", "2027-03-31"),
    ("PB-MAN-0017", "BEL-STD-01", 6.80, "2026-04-01", "2027-03-31"),
    ("PB-MAN-0017", "BRK-PAD-01", 9.40, "2026-04-01", "2027-03-31"),
    ("CC-SAL-0031", "CHG-4A-01", 96.00, "2026-04-01", "2027-03-31"),
    ("AM-BIR-0008", "MTR-HUB-250", 142.00, "2026-04-01", "2027-03-31"),
    ("IP-MAN-0055", "BOX-BIKE-01", 21.50, "2026-04-01", "2027-03-31"),
]

WAREHOUSES = [("WH-MAN-STR", "Manchester main stores", "NBC-MAN-01"), ("WH-LDS-STR", "Leeds stores", "NBC-LDS-01")]

STOCK = [
    ("BAT-500", "WH-MAN-STR", 5400, 0, 0), ("BAT-500", "WH-LDS-STR", 1200, 0, 0),
    ("BAT-375", "WH-MAN-STR", 4100, 0, 0), ("BAT-750", "WH-MAN-STR", 900, 0, 0),
    ("MNT-FRM-01", "WH-MAN-STR", 23000, 0, 0), ("MNT-RCK-02", "WH-MAN-STR", 31000, 0, 0),
    ("BEL-STD-01", "WH-MAN-STR", 8000, 0, 0), ("BRK-PAD-01", "WH-MAN-STR", 26000, 0, 0),
    ("MTR-HUB-250", "WH-MAN-STR", 48000, 0, 0), ("CHG-4A-01", "WH-MAN-STR", 52000, 0, 0),
    ("BOX-BIKE-01", "WH-MAN-STR", 60000, 0, 0),
]

COST_CENTRES = [
    ("PRD-05", "City e-bike line, regular production", "CLOSED", "2026-10-15", "DOKAFOR"),
    ("PRD-07", "Spring launch run", "OPEN", None, "DOKAFOR"),
    ("PRD-03", "Cargo e-bike line", "OPEN", None, "DOKAFOR"),
    ("MNT-01", "Plant maintenance", "OPEN", None, "HWEBER"),
    ("ADM-01", "Administration", "OPEN", None, "HWEBER"),
]
BUDGETS = [("PRD-05", "2026-Q4", 600000, 410000), ("PRD-07", "2026-Q4", 1500000, 310000),
           ("PRD-03", "2026-Q4", 800000, 120000), ("MNT-01", "2026-Q4", 300000, 45000),
           ("ADM-01", "2026-Q4", 200000, 20000)]

TAX_CODES = [
    ("VAT20-UK", "VAT 20% (UK supplier)", 0.20, "INTRA"),
    ("VAT20-RC", "VAT 20%, reverse charge (overseas supplier)", 0.20, "INTER"),
    ("VAT5-UK", "VAT 5% (UK supplier)", 0.05, "INTRA"),
    ("VAT5-RC", "VAT 5%, reverse charge (overseas supplier)", 0.05, "INTER"),
]
PAY_TERMS = [("N30", "Net 30 days", 30), ("N45", "Net 45 days", 45), ("N60", "Net 60 days", 60),
             ("ADV", "Advance", 0)]

DOC_SEQ = [("PR", "PR/2026/", 4417, 5), ("PO", "PO/2026/", 1182, 5), ("SUP", "", 0, 0)]

# Past orders: last purchase history the agent can look up.
PAST_POS = [
    # po_no, sup, item, qty, rate, tax, cc, status, created_on, released_on
    ("PO/2026/01044", "VC-EIN-0042", "BAT-500", 1800, 114.00, "VAT20-RC", "PRD-05", "RL", "2026-08-03", "2026-08-04"),
    ("PO/2026/01120", "VC-EIN-0042", "BAT-500", 1800, 114.00, "VAT20-RC", "PRD-05", "RL", "2026-09-12", "2026-09-14"),
    ("PO/2026/01131", "PB-MAN-0017", "BEL-STD-01", 30000, 6.80, "VAT20-UK", "PRD-05", "RL", "2026-09-18", "2026-09-18"),
    ("PO/2026/01152", "VC-EIN-0042", "MNT-FRM-01", 25000, 18.50, "VAT20-RC", "PRD-05", "RL", "2026-10-03", "2026-10-05"),
    ("PO/2026/01167", "IP-MAN-0055", "BOX-BIKE-01", 40000, 21.50, "VAT20-UK", "PRD-07", "RL", "2026-10-09", "2026-10-09"),
    ("PO/2026/01179", "CC-SAL-0031", "CHG-4A-01", 4000, 96.00, "VAT20-UK", "PRD-07", "PA", "2026-10-23", None),
]
