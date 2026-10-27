"""Tables and ~50 seed records. Every table name starts with your prefix. Seed the traps on purpose:
a duplicate, a near-match name, a record just over a limit, one that is closed or expired."""
from .._kit import add_people, add_seq, grant, insert

SCHEMA = """
CREATE TABLE xx_doc(doc_no TEXT PRIMARY KEY, party TEXT, qty INT, amount REAL, cc_cd TEXT, status TEXT,
  created_by TEXT, created_on TEXT, approver TEXT, warn_cd TEXT, client_ref TEXT);
"""

# TODO: ~50 rows across your tables: masters, history, and the traps.
DOCS = [
    ("XX/2026/00001", "Deccan Polymers", 10, 1000.0, "PRD-07", "AP", "KJOSHI", "2026-10-20T10:00:00", "RMEHTA", None, None),
]

SVCS = ["xx_list", "xx_fetch", "xx_save", "xx_approve"]


def seed(erp):
    add_people(erp)                       # TODO: people your module needs, from _kit.PEOPLE
    insert(erp, "xx_doc", DOCS)
    add_seq(erp, "XX", "XX/2026/", 2, 5)  # your document numbers
    grant(erp, "PUR-EXEC", ["xx_list", "xx_fetch", "xx_save"])
    grant(erp, "PUR-MGR", ["xx_list", "xx_approve"])
