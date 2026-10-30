"""Sales · orders: the before, scripted. happy_path() is Arjun's sentence done the legacy way, screen by screen;
TRAPS triggers each trap in the complexity budget and says whether Ledgerline behaved as the brief claims."""
from __future__ import annotations

from .._kit import ok

MANCHESTER = "C-PUN-0118"


def happy_path(erp) -> dict:
    """Arjun: quote Annapurna Stores 500 five-litre e-bikes at dealer price. Two screens, then a read-back."""
    a = erp.session("ARAO")
    rows = ok(a.call("so_cust_search", screen="SAL-CUS-01", task="Find", q="Annapurna"))["rows"]
    cust = [r for r in rows if r["city"] == "Manchester" and r["status"] == "ACTIVE"][0]["cust_cd"]
    ok(a.call("so_cust_get", screen="SAL-CUS-01", task="Show", cust_cd=cust))
    ok(a.call("so_price_get", screen="SAL-CUS-01", task="Prices", itm_cd="PC-SS-05L", list_cd="DLR"))
    f = ok(a.call("so_qtn_fetch", screen="SAL-QTN-02", task="Price", cust_cd=cust, itm_cd="PC-SS-05L"))
    d = ok(a.call("so_qtn_save", screen="SAL-QTN-02", task="Save", cust_cd=cust, itm_cd="PC-SS-05L", qty=500,
                  tax_cd=f["tax_cd"], fetch_tok=f["fetch_tok"]))
    q = ok(a.call("so_list", screen="SAL-ORD-03", task="List", doc_no=d["qtn_no"]))["quotations"][0]
    good = q["status"] == "IS" and q["rate"] == 1450 and q["gross_value"] == 812000 and q["tax_cd"] == "VAT5-UK"
    return {"doc": q["qtn_no"], "status": q["status"], "ok": good}


def _quote(s, cust=MANCHESTER, itm="PC-SS-05L", qty=500, tax="VAT5-UK", **kw):
    tok = ok(s.call("so_qtn_fetch", cust_cd=cust, itm_cd=itm))["fetch_tok"]
    return s.call("so_qtn_save", cust_cd=cust, itm_cd=itm, qty=qty, tax_cd=tax, fetch_tok=tok, **kw)


def t_silent(erp):
    a = erp.session("ARAO")
    q = ok(_quote(a))["qtn_no"]
    r = a.call("so_ord_save", ord_type="STD", qtn_no=q)
    rel = a.call("so_ord_release", ord_no=r["data"]["ord_no"])
    dsp = erp.q("SELECT 1 FROM so_dsp WHERE ord_no=?", r["data"]["ord_no"])
    good = r["rc"] == "S" and r["data"]["status"] == "CH" and rel["err_cd"] == "ERR-SO-0715" and not dsp
    return good, f"rc={r['rc']} msg='{r['msg']}' status={r['data']['status']}; release: {rel['err_cd']}; dispatch rows {len(dsp)}"


def t_variant_std(erp):
    r = erp.session("ARAO").call("so_ord_save", ord_type="STD", cust_cd=MANCHESTER, itm_cd="PC-SS-05L", qty=500,
                                 tax_cd="VAT5-UK")
    return r["err_cd"] == "ERR-SO-0602", f"STD order without a quotation: {r['err_cd']} {r['msg']}"


def t_variant_cash(erp):
    a = erp.session("ARAO")
    big = a.call("so_ord_save", ord_type="CSH", cust_cd=MANCHESTER, itm_cd="PC-SS-05L", qty=100, tax_cd="VAT5-UK")
    small = a.call("so_ord_save", ord_type="CSH", cust_cd=MANCHESTER, itm_cd="PC-SS-05L", qty=50, tax_cd="VAT5-UK")
    good = big["err_cd"] == "ERR-SO-0610" and small["rc"] == "S" and small["data"]["status"] == "OP"
    return good, (f"CSH 100 pcs: {big['err_cd']}; CSH 50 pcs (£{small['data']['gross_value']:,.0f}): "
                  f"{small['data']['status']} with no credit check")


def t_screen_state(erp):
    r = erp.session("ARAO").call("so_qtn_save", cust_cd=MANCHESTER, itm_cd="PC-SS-05L", qty=500, tax_cd="VAT5-UK")
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def _released(erp):
    a = erp.session("ARAO")
    q = ok(_quote(a, cust="C-PUN-0090", qty=100))["qtn_no"]
    o = ok(a.call("so_ord_save", ord_type="STD", qtn_no=q))["ord_no"]
    return o, a.call("so_ord_release", ord_no=o)


def t_cascade_stock(erp):
    s0 = erp.q1("SELECT allocated FROM stock WHERE itm_cd='PC-SS-05L' AND whs_cd='WH-PUN-FG'")["allocated"]
    o, r = _released(erp)
    s1 = erp.q1("SELECT allocated FROM stock WHERE itm_cd='PC-SS-05L' AND whs_cd='WH-PUN-FG'")["allocated"]
    return r["rc"] == "S" and s1 == s0 + 100, f"{r['msg']}: PC-SS-05L allocated in WH-PUN-FG {s0}→{s1}"


def t_cascade_dispatch(erp):
    n0 = erp.q1("SELECT count(*) n FROM ntf_queue")["n"]
    o, r = _released(erp)
    dsp = erp.q("SELECT * FROM so_dsp WHERE ord_no=?", o)
    n1 = erp.q1("SELECT count(*) n FROM ntf_queue")["n"]
    return len(dsp) == 1 and n1 > n0, f"dispatch advice rows {len(dsp)} ({dsp[0]['qty'] if dsp else 0} pcs), mails queued {n1 - n0}"


def t_shared_engine(erp):
    d = ok(_quote(erp.session("ARAO"), disc_pct=3))
    sps = erp.calls[-1].sps
    inbox = ok(erp.session("SIYER").call("po_pending_appr"))["rows"]
    good = "sp_tax_compute" in sps and "sp_appr_route" in sps and any(r["doc_no"] == d["qtn_no"] for r in inbox)
    return good, (f"{d['qtn_no']} {d['status']} £{d['gross_value']:,.0f}: sp_tax_compute {'sp_tax_compute' in sps}, "
                  f"sp_appr_route {'sp_appr_route' in sps}, in Sunita's purchasing inbox {any(r['doc_no'] == d['qtn_no'] for r in inbox)}")


def t_tax_region(erp):
    r = _quote(erp.session("ARAO"), cust="C-HUB-0307", qty=200)  # Fetch's default VAT5-UK, Karnataka customer
    return r["err_cd"] == "ERR-SO-0412", f"Hubli customer with the default tax code: {r['err_cd']} {r['msg']}"


def t_policy_only(erp):
    """Price Policy §3.2 (no expired prices) lives only in the document: Ledgerline accepts the April price £1,395."""
    r = _quote(erp.session("ARAO"), rate=1395)
    return r["rc"] == "S" and r["data"]["rate"] == 1395, f"expired dealer price £1,395 accepted: {r['msg']} status {r['data']['status']}"


TRAPS = {
    "silent: order over the credit limit saved as CH": t_silent,
    "variant: STD order needs an issued quotation": t_variant_std,
    "variant: CSH order only up to £100,000, no credit check": t_variant_cash,
    "screen_state: Save without Price (Fetch)": t_screen_state,
    "cascade: release reserves finished stock": t_cascade_stock,
    "cascade: release writes a dispatch advice and mails": t_cascade_dispatch,
    "shared_engine: sp_tax_compute and sp_appr_route, visible in the purchasing inbox": t_shared_engine,
    "rule: Fetch's INTRA default refused for a Karnataka customer": t_tax_region,
    "policy_only: expired price accepted": t_policy_only,
}
