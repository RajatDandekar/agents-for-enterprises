"""Legal · contracts: tables and seed data. Everything is fictional; contract wording is invented.

Brightcell Energy (Lyon) is deliberately NOT on the counterparty register, and not in the supplier master either.
The register holds three near-matches: Brightcell Packaging (Lyon), Shakthi Seals (Coimbatore) and a blocked
Brightcell Seal Works (Lyon, dissolved). A party saved without PAN and VAT number has kyc = 'N', and any request
against it is saved silently as PK (pending KYC): it never reaches Legal or the signatory.
"""
from .._kit import add_people, add_seq, grant, insert

SCHEMA = """
CREATE TABLE ct_party(party_cd TEXT PRIMARY KEY, name TEXT, city TEXT, state TEXT, pan TEXT, vat_no TEXT, kyc TEXT,
  sup_cd TEXT, status TEXT, nda_till TEXT, created_by TEXT, created_on TEXT);
CREATE TABLE ct_tmpl(tmpl_cd TEXT PRIMARY KEY, ct_type TEXT, descr TEXT, paper TEXT, def_term INT, max_term INT,
  juris TEXT, active INT);
CREATE TABLE ct_clause(clause_cd TEXT PRIMARY KEY, ct_type TEXT, attr TEXT, rule TEXT, limit_val TEXT, descr TEXT);
CREATE TABLE ct_req(ct_no TEXT PRIMARY KEY, ct_type TEXT, party_cd TEXT, paper TEXT, tmpl_cd TEXT, doc_ref TEXT,
  term_months INT, start_dt TEXT, end_dt TEXT, juris TEXT, value REAL, status TEXT, req_by TEXT, req_on TEXT,
  reviewer TEXT, legal_by TEXT, signatory TEXT, signed_by TEXT, signed_on TEXT, fwd_to TEXT, warn_cd TEXT,
  client_ref TEXT);
CREATE TABLE ct_dev(ct_no TEXT, clause_cd TEXT, found TEXT, expected TEXT, status TEXT);
CREATE TABLE ct_reg(ct_no TEXT, party_cd TEXT, ct_type TEXT, start_dt TEXT, end_dt TEXT, signed_by TEXT,
  remind_on TEXT, status TEXT);
"""

# party_cd, name, city, state, PAN, VAT number, kyc, supplier code, status, NDA valid till, created by, created on
PARTIES = [
    ("CP-0011", "Voltway Cells", "Eindhoven", "GJ", "AADCD4417K", "24AADCD4417K1Z3", "Y", "VC-EIN-0042", "ACTIVE",
     "2025-12-31", "LMORENO", "2023-12-15"),
    ("CP-0012", "Pennine Brakes", "Manchester", "MH", "AAGCS2290P", "27AAGCS2290P1Z5", "Y", "PB-MAN-0017", "ACTIVE",
     "2027-05-31", "LMORENO", "2025-05-20"),
    ("CP-0013", "Castlefield Chargers", "Salford", "MH", "AABFO7713M", "27AABFO7713M1Z2", "Y", "CC-SAL-0031", "ACTIVE",
     None, "LMORENO", "2025-03-11"),
    ("CP-0014", "Albion Motors", "Birmingham", "MH", "AAACM5520L", "27AAACM5520L1Z9", "Y", "AM-BIR-0008", "ACTIVE",
     "2027-06-30", "LMORENO", "2025-06-18"),
    ("CP-0015", "Irwell Packaging", "Manchester", "MH", "AAPFS6634Q", "27AAPFS6634Q1Z1", "Y", "IP-MAN-0055", "ACTIVE",
     None, "ECLARKE", "2023-03-20"),
    ("CP-0016", "Nordic Cell Co.", "Gdańsk", "WB", None, "19AAECK1180D1Z6", "N", "NC-GDA-0063", "ACTIVE",
     None, "ECLARKE", "2023-05-02"),  # PAN never collected: KYC incomplete
    ("CP-0017", "Brightcell Packaging", "Lyon", "GJ", "AAHFS3307B", "24AAHFS3307B1Z9", "Y", None, "ACTIVE",
     "2027-02-28", "LMORENO", "2025-02-14"),  # near-match, same city
    ("CP-0018", "Shakthi Seals", "Coimbatore", "TN", "AAKCS5521F", "33AAKCS5521F1Z2", "Y", None, "ACTIVE",
     None, "LMORENO", "2024-08-09"),  # near-match, other company
    ("CP-0019", "Kalpa Design Studio", "Manchester", "MH", "AAOPK4410C", "27AAOPK4410C1Z6", "Y", None, "ACTIVE",
     None, "DOKAFOR", "2026-09-28"),
    ("CP-0020", "Rasayan Testing Labs", "Manchester", "MH", "AAFCR9083H", "27AAFCR9083H1Z1", "Y", None, "ACTIVE",
     None, "ECLARKE", "2026-10-12"),
    ("CP-0021", "Annapurna Stores", "Manchester", "MH", "AAQFA1120K", "27AAQFA1120K1Z8", "Y", None, "ACTIVE",
     None, "HWEBER", "2024-01-10"),
    ("CP-0022", "Voltway Paints & Coatings", "Rotterdam", "GJ", "AAKFD9031R", "24AAKFD9031R1Z8", "Y", "VPC-ROT-0107",
     "ACTIVE", None, "ECLARKE", "2024-11-04"),  # near-match to Voltway Cells
    ("CP-0023", "Vardhan Logistics", "Leeds", "MH", "AABCV6620E", "27AABCV6620E1Z4", "Y", None, "ACTIVE",
     None, "DOKAFOR", "2025-08-22"),
    ("CP-0024", "Brightcell Seal Works", "Lyon", "GJ", "AAGFS1029A", "24AAGFS1029A1Z5", "Y", None, "BLOCKED",
     "2023-12-31", "MIGRATION", "2019-04-01"),  # dissolved in 2024; same city, different company
]

# tmpl_cd, type, description, paper, default term, longest term the template allows, jurisdiction, active
TEMPLATES = [
    ("NDA-MUT-v4", "NDA", "Mutual non-disclosure agreement, our paper", "OURS", 24, 36, "MANCHESTER", 1),
    ("NDA-ONE-v2", "NDA", "One-way non-disclosure agreement (we disclose), our paper", "OURS", 24, 36, "MANCHESTER", 1),
    ("NDA-MUT-v3", "NDA", "Mutual NDA (withdrawn 31 Mar 2025)", "OURS", 60, 60, "MANCHESTER", 0),
    ("MSA-SUP-v2", "MSA", "Master supply agreement, our paper", "OURS", 36, 60, "MANCHESTER", 1),
    ("SLA-SVC-v1", "SLA", "Service agreement, our paper", "OURS", 12, 36, "MANCHESTER", 1),
]

# The NDA playbook as data: what Ledgerline's clause scan compares a request against.
CLAUSES = [
    ("NDA-TERM", "NDA", "term_months", "MAX", "36", "An NDA runs at most 3 years"),
    ("NDA-JURIS", "NDA", "juris", "EQ", "MANCHESTER", "Courts at Manchester only"),
    ("NDA-PAPER", "NDA", "paper", "EQ", "OURS", "Our template first; their paper means full review"),
    ("MSA-TERM", "MSA", "term_months", "MAX", "60", "A supply agreement runs at most 5 years"),
    ("MSA-JURIS", "MSA", "juris", "EQ", "MANCHESTER", "Courts at Manchester only"),
    ("MSA-VALUE", "MSA", "value", "MAX", "5000000", "Above £5,000,000 needs the plant head and Finance"),
    ("SLA-TERM", "SLA", "term_months", "MAX", "36", "A service agreement runs at most 3 years"),
    ("SLA-JURIS", "SLA", "juris", "EQ", "MANCHESTER", "Courts at Manchester only"),
]

# ct_no, type, party, paper, tmpl, doc_ref, term, start, end, juris, value, status, req_by, req_on, reviewer,
# legal_by, signatory, signed_by, signed_on, fwd_to, warn_cd, client_ref
PAST_REQS = [
    ("CT/2024/0031", "NDA", "CP-0011", "OURS", "NDA-MUT-v3", None, 24, "2024-01-01", "2025-12-31", "MANCHESTER", 0, "EX",
     "LMORENO", "2023-12-15T11:00:00", None, None, "HWEBER", "HWEBER", "2023-12-20T16:00:00", "HWEBER", None, None),
    ("CT/2025/0044", "MSA", "CP-0013", "OURS", "MSA-SUP-v2", None, 24, "2025-04-01", "2027-03-31", "MANCHESTER", 1800000,
     "EX", "LMORENO", "2025-03-11T10:20:00", None, None, "HWEBER", "HWEBER", "2025-03-25T12:00:00", None, None, None),
    ("CT/2025/0047", "NDA", "CP-0017", "OURS", "NDA-MUT-v4", None, 24, "2025-03-01", "2027-02-28", "MANCHESTER", 0, "EX",
     "LMORENO", "2025-02-14T09:40:00", None, None, "HWEBER", "HWEBER", "2025-02-20T15:10:00", "HWEBER", None, None),
    ("CT/2025/0049", "NDA", "CP-0014", "OURS", "NDA-MUT-v4", None, 24, "2025-07-01", "2027-06-30", "MANCHESTER", 0, "EX",
     "LMORENO", "2025-06-18T10:00:00", None, None, "HWEBER", "HWEBER", "2025-06-26T11:30:00", "HWEBER", None, None),
    ("CT/2025/0052", "NDA", "CP-0012", "OURS", "NDA-MUT-v4", None, 24, "2025-06-01", "2027-05-31", "MANCHESTER", 0, "EX",
     "LMORENO", "2025-05-20T14:00:00", None, None, "HWEBER", "HWEBER", "2025-05-28T10:45:00", "HWEBER", None, None),
    ("CT/2026/0054", "NDA", "CP-0016", "OURS", "NDA-MUT-v4", None, 24, "2026-09-01", "2028-08-31", "MANCHESTER", 0, "PK",
     "ECLARKE", "2026-08-28T12:05:00", None, None, None, None, None, None, "W-CT-117", None),  # stuck since August
    ("CT/2026/0055", "NDA", "CP-0019", "THEIRS", None, "KDS/NDA/14", 36, "2026-10-01", "2029-09-30", "BIRMINGHAM", 0, "LR",
     "DOKAFOR", "2026-09-28T16:30:00", "RMENON", None, None, None, None, None, None, None),
    ("CT/2026/0056", "SLA", "CP-0020", "OURS", "SLA-SVC-v1", None, 12, "2026-11-01", "2027-10-31", "MANCHESTER", 240000, "PS",
     "ECLARKE", "2026-10-20T10:15:00", None, None, "DOKAFOR", None, None, None, None, None),
]

DEVIATIONS = [
    ("CT/2026/0055", "NDA-PAPER", "THEIRS", "OURS", "OPEN"),
    ("CT/2026/0055", "NDA-JURIS", "BIRMINGHAM", "MANCHESTER", "OPEN"),
]

# ct_no, party, type, start, end, signed by, renewal reminder, status. Older rows were migrated from the paper register.
REGISTER = [
    ("CT/2022/0007", "CP-0024", "NDA", "2022-01-01", "2023-12-31", "HWEBER", "2023-11-01", "EXPIRED"),
    ("CT/2023/0012", "CP-0015", "MSA", "2023-04-01", "2026-03-31", "HWEBER", "2026-01-30", "EXPIRED"),
    ("CT/2023/0019", "CP-0016", "NDA", "2023-06-01", "2025-05-31", "HWEBER", "2025-04-01", "EXPIRED"),
    ("CT/2024/0031", "CP-0011", "NDA", "2024-01-01", "2025-12-31", "HWEBER", "2025-11-01", "EXPIRED"),
    ("CT/2025/0044", "CP-0013", "MSA", "2025-04-01", "2027-03-31", "HWEBER", "2027-01-30", "ACTIVE"),
    ("CT/2025/0047", "CP-0017", "NDA", "2025-03-01", "2027-02-28", "HWEBER", "2026-12-30", "ACTIVE"),
    ("CT/2025/0049", "CP-0014", "NDA", "2025-07-01", "2027-06-30", "HWEBER", "2027-05-01", "ACTIVE"),
    ("CT/2025/0052", "CP-0012", "NDA", "2025-06-01", "2027-05-31", "HWEBER", "2027-04-01", "ACTIVE"),
]

READS = ["ct_party_find", "ct_fetch", "ct_list", "ct_reg_list"]
REQUESTER = READS + ["ct_party_save", "ct_save", "ct_submit"]


def seed(erp):
    add_people(erp, "RMENON")
    insert(erp, "ct_party", PARTIES)
    insert(erp, "ct_tmpl", TEMPLATES)
    insert(erp, "ct_clause", CLAUSES)
    insert(erp, "ct_req", PAST_REQS)
    insert(erp, "ct_dev", DEVIATIONS)
    insert(erp, "ct_reg", REGISTER)
    erp.db.executemany("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
                       [("CT-REV", "CT/2026/0055", "RMENON", "PENDING", "DOKAFOR", "2026-09-28T16:30:00"),
                        ("CT-SGN", "CT/2026/0056", "DOKAFOR", "PENDING", "ECLARKE", "2026-10-20T10:15:00")])
    add_seq(erp, "CT", "CT/2026/", 57, 4)
    add_seq(erp, "CTP", "CP-", 25, 4)
    for role in ("PUR-EXEC", "PUR-SR", "PUR-MGR"):
        grant(erp, role, REQUESTER)
    for role in ("PUR-MGR", "PLANT-HEAD"):
        grant(erp, role, READS + ["ct_sign"])
    grant(erp, "LEGAL", READS + ["ct_party_save", "ct_review", "ntf_send"])
