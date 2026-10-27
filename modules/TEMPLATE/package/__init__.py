"""<Area> · <module>. Before: <three screens>. After: one sentence.

Copy this folder to bahi/bahi/modules/<your_module>/ and replace every xx_ / XX / sp_xx_ with your prefix.
    erp = ERP(modules=["<your_module>"])
"""
from . import procs, services  # noqa: F401  (registers the procedures and services)
from .seed import SCHEMA, seed  # noqa: F401

KIT = {
    "name": "your_module",            # TODO: the folder name
    "title": "Area · module",          # TODO
    "prefix": "xx_",                   # TODO: two letters + underscore, not used by any other module
    "speaker": "KJOSHI",               # TODO: who says the after sentence
    "after": "TODO: the one sentence your user will type.",
    "screens": ["XX-ABC-01", "XX-ABC-02", "XX-ABC-03"],
    "shared_engine": "TODO: which purchasing procedure you reuse (sp_tax_compute, sp_budget_chk, sp_appr_route)",
}

# The data dictionary (modules/build_dicts.py) is generated from these three and your services.
GLOSSARY = {"doc_no": "TODO: what each legacy field means, in plain words"}
STATUS = {"DR": "draft", "PA": "pending approval", "HD": "held (the silent outcome)", "AP": "approved", "CN": "cancelled"}
ERRORS = {"ERR-XX-0001": "TODO", "W-XX-101": "TODO: the warning behind the silent outcome", "ERR-SCR-0221": "Save without Fetch"}
