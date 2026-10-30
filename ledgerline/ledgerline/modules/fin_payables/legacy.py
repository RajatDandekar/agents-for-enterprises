"""Finance · payables: the before, scripted. happy_path() is the after sentence done the legacy way, screen by screen;
TRAPS triggers each trap in the complexity budget and says whether Ledgerline behaved as the brief claims."""
from __future__ import annotations

from .._kit import ok

INV = "AP/2026/03390"


def happy_path(erp) -> dict:
    """Voltway phones Emma about invoice 4471. Today it takes four people and a week."""
    k, p, r, v = (erp.session(u) for u in ("ECLARKE", "PSHAH", "DOKAFOR", "VNAIR"))
    rows = ok(k.call("ap_inv_list", screen="FIN-AP-03", task="Search", sup_inv_no="4471"))["rows"]
    ap_no = [x for x in rows if x["sup_cd"] == "VC-EIN-0042"][0]["ap_no"]
    d = ok(k.call("ap_inv_get", screen="FIN-AP-03", task="Details", ap_no=ap_no))
    ok(k.call("po_get", screen="PUR-POH-02", task="Open PO", po_no=d["po_no"]))
    ok(k.call("sup_rate_get", screen="PUR-SUP-03", task="Rate contract", sup_cd="VC-EIN-0042", itm_cd="BAT-500"))
    ok(k.call("ap_hold_refer", screen="FIN-AP-03", task="Refer", ap_no=ap_no, hold_cd="H-PRC", refer_to="DOKAFOR",
              note="Delivered 2 Oct, contract rate 11.90 from 1 Oct"))
    ok(r.call("ap_hold_release", screen="FIN-AP-03", task="Release", ap_no=ap_no, hold_cd="H-PRC",
              reason="Contract rate applies from 1 Oct"))
    pay = ok(p.call("ap_pay_sched", screen="FIN-AP-05", task="Propose", ap_no=ap_no, pay_dt="30-10-2026",
                    early_rsn="Supplier request before the spring launch"))
    ok(v.call("ap_approve", screen="FIN-AP-05", task="Approve", doc_no=pay["pay_no"], decision="A"))
    erp.advance(days=4)  # Friday
    ok(p.call("ap_pay_run", screen="FIN-AP-05", task="Run", run_dt="2026-10-30"))
    i = erp.q1("SELECT status FROM ap_inv WHERE ap_no=?", ap_no)
    pp = erp.q1("SELECT status FROM ap_pay WHERE pay_no=?", pay["pay_no"])
    return {"doc": f"{ap_no} / {pay['pay_no']}", "status": f"{i['status']}/{pp['status']}",
            "ok": i["status"] == "PD" and pp["status"] == "PD"}


def _release(erp):
    ok(erp.session("DOKAFOR").call("ap_hold_release", ap_no=INV, hold_cd="H-PRC", reason="rate confirmed"))


def t_silent(erp):
    _release(erp)
    p = erp.session("PSHAH")
    r = p.call("ap_pay_sched", ap_no=INV, pay_dt="2026-10-30")
    routed = erp.q1("SELECT 1 FROM approval WHERE doc_no=?", r["data"]["pay_no"])
    erp.advance(days=4)
    run = ok(p.call("ap_pay_run", run_dt="2026-10-30"))
    inv = erp.q1("SELECT status FROM ap_inv WHERE ap_no=?", INV)["status"]
    good = r["rc"] == "S" and r["data"]["status"] == "PK" and not routed and run["paid"] == 0 and inv == "PO"
    return good, (f"rc={r['rc']} msg='{r['msg']}' status={r['data']['status']} routed={bool(routed)}; "
                  f"Friday run paid {run['paid']}, invoice still {inv}")


def _save(s, **kw):
    m = {k: kw[k] for k in ("inv_type", "sup_cd", "po_no", "qty", "rate", "amount", "cc_cd") if k in kw}
    tok = ok(s.call("ap_match", **m))["match_tok"]
    return s.call("ap_save", match_tok=tok, **kw)


def t_variant_po(erp):
    """Three-way match: Irwell Packaging still has 10,000 accepted boxes not billed on PO/2026/01167 (order rate 21.50)."""
    p = erp.session("PSHAH")
    r1 = _save(p, inv_type="PO", sup_cd="IP-MAN-0055", sup_inv_no="SP/2241", inv_dt="2026-10-24", po_no="PO/2026/01167",
               qty=10000, rate=22.40, tax_cd="VAT20-UK")
    r2 = _save(p, inv_type="PO", sup_cd="IP-MAN-0055", sup_inv_no="SP/2242", inv_dt="2026-10-24", po_no="PO/2026/01167",
               qty=10000, rate=21.50, tax_cd="VAT20-UK")
    h1 = erp.q1("SELECT status,hold_cd FROM ap_inv WHERE ap_no=?", r1["data"]["ap_no"])
    h2 = erp.q1("SELECT status,hold_cd FROM ap_inv WHERE ap_no=?", r2["data"]["ap_no"]) if r2["rc"] != "E" else None
    good = h1["status"] == "HD" and h1["hold_cd"] == "H-PRC" and h2 and h2["hold_cd"] == "H-QTY"
    return bool(good), f"22.40 vs 21.50 → {h1['status']} {h1['hold_cd']}; then 10,000 more on the same receipt → {h2}"


def t_variant_npo(erp):
    p = erp.session("PSHAH")
    r1 = p.call("ap_match", inv_type="NPO", sup_cd="CC-SAL-0031", po_no="PO/2026/01179", amount=38500, cc_cd="MNT-01")
    r2 = _save(p, inv_type="NPO", sup_cd="CC-SAL-0031", sup_inv_no="OSM/311", inv_dt="2026-10-20", amount=38500,
               tax_cd="VAT20-UK", cc_cd="MNT-01")
    a = erp.q1("SELECT approver FROM approval WHERE doc_no=? AND doc_type='APINV'", r2["data"]["ap_no"])
    good = r1["err_cd"] == "ERR-AP-0211" and r2["data"]["status"] == "PA" and a["approver"] == "HWEBER"
    return good, f"NPO with a PO: {r1['err_cd']}; NPO on MNT-01: {r2['data']['status']}, routed to {a['approver']}"


def t_screen_state(erp):
    r = erp.session("PSHAH").call("ap_save", inv_type="NPO", sup_cd="CC-SAL-0031", sup_inv_no="OSM/311",
                                  inv_dt="2026-10-20", amount=38500, tax_cd="VAT20-UK", cc_cd="MNT-01")
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def t_cascade_post(erp):
    l0 = erp.q1("SELECT count(*) n FROM ap_ledger WHERE ref=?", INV)["n"]
    _release(erp)
    led = erp.q("SELECT cr FROM ap_ledger WHERE ref=?", INV)
    gst = erp.q("SELECT itc_amt FROM ap_gst WHERE ap_no=?", INV)
    st = erp.q1("SELECT status FROM ap_inv WHERE ap_no=?", INV)["status"]
    good = l0 == 0 and [x["cr"] for x in led] == [252756.0] and [g["itc_amt"] for g in gst] == [38556.0] and st == "PO"
    return good, f"release → status {st}, supplier ledger credit {[x['cr'] for x in led]}, VAT input credit {[g['itc_amt'] for g in gst]}"


def t_cascade_pay(erp):
    _release(erp)
    p = erp.session("PSHAH")
    pay = ok(p.call("ap_pay_sched", ap_no=INV, pay_dt="2026-10-30", early_rsn="supplier request"))
    ok(erp.session("VNAIR").call("ap_approve", doc_no=pay["pay_no"], decision="A"))
    erp.advance(days=4)
    run = ok(p.call("ap_pay_run", run_dt="2026-10-30"))
    dr = erp.q1("SELECT dr FROM ap_ledger WHERE ref=?", pay["pay_no"])
    ntf = erp.q1("SELECT subject FROM ntf_queue WHERE subject LIKE ?", f"Remittance {pay['pay_no']}%")
    st = erp.q1("SELECT status FROM ap_inv WHERE ap_no=?", INV)["status"]
    good = run["paid"] == 1 and dr and dr["dr"] == 252756.0 and ntf and st == "PD"
    return bool(good), f"run paid {run['paid']} ({run['amount']:,.2f}); ledger debit {dr and dr['dr']}; invoice {st}; mail '{ntf and ntf['subject']}'"


def t_shared_engine(erp):
    p = erp.session("PSHAH")
    r = _save(p, inv_type="NPO", sup_cd="VC-EIN-0042", sup_inv_no="4502", inv_dt="2026-10-20", amount=5000,
              tax_cd="VAT20-UK", cc_cd="MNT-01")
    sps = erp.calls[-1].sps
    return r["err_cd"] == "ERR-PO-0412" and "sp_tax_region_chk" in sps, f"Voltway (GJ) with VAT20-UK: {r['err_cd']}; sps {sps}"


def t_policy_only(erp):
    """POL-FIN-025: MSME suppliers must be paid within 45 days. Ledgerline shows Pennine's invoice with no warning at all."""
    d = ok(erp.session("PSHAH").call("ap_inv_get", ap_no="AP/2026/03374"))
    good = d["msme"] == "Y" and d["age_days"] > 45 and d["status"] == "HD" and not d["warn_cd"]
    return good, f"Pennine (MSME) invoice {d['age_days']} days old, status {d['status']} {d['hold_cd']}, warning {d['warn_cd']}"


TRAPS = {
    "silent: early payment with no reason is parked (PK), missed by the run": t_silent,
    "variant: PO invoice, three-way match (price, then quantity)": t_variant_po,
    "variant: non-PO invoice, two-way, owner approves": t_variant_npo,
    "screen_state: Save without Match": t_screen_state,
    "cascade: posting credits the supplier ledger and VAT input credit": t_cascade_post,
    "cascade: payment run debits the ledger and mails the remittance": t_cascade_pay,
    "shared_engine: sp_tax_region_chk refuses INTRA for a the Netherlands supplier": t_shared_engine,
    "policy_only: MSME 45-day rule not enforced": t_policy_only,
}
