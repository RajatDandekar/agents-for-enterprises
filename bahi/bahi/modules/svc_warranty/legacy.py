"""Service · warranty: the before, scripted. happy_path() is Farhan's sentence done the legacy way, screen by screen;
TRAPS triggers each trap in the complexity budget and says whether Bahi behaved as the brief claims."""
from __future__ import annotations

from .._kit import ok


def happy_path(erp) -> dict:
    """Farhan: the dealer's whistle, serial RS5-2609-1187. Three screens, the way he does it today."""
    f = erp.session("FSHAIKH")
    ok(f.call("wr_ser_get", screen="SVC-SER-01", task="Find", serial="RS5-2609-1187"))
    ok(f.call("stk_query", screen="INV-STK-02", task="Query", itm_cd="WHS-STD-01", whs_cd="WH-PUN-STR"))
    tok = ok(f.call("wr_verify", screen="SVC-TKT-02", task="Verify", serial="RS5-2609-1187", part_cd="WHS-STD-01"))["fetch_tok"]
    d = ok(f.call("wr_tkt_save", screen="SVC-TKT-02", task="Save", serial="RS5-2609-1187", part_cd="WHS-STD-01",
                  cmp_cd="NWS", cause_cd="MFD", remarks="Whistle broke after 3 weeks", fetch_tok=tok))
    ok(f.call("wr_issue", screen="SVC-TKT-02", task="Issue Part", tkt_no=d["tkt_no"]))
    ok(f.call("wr_close", screen="SVC-TKT-02", task="Close", tkt_no=d["tkt_no"], remarks="Replaced under warranty"))
    t = erp.q1("SELECT * FROM wr_ticket WHERE tkt_no=?", d["tkt_no"])
    return {"doc": d["tkt_no"], "status": t["status"], "ok": t["status"] == "CL" and t["chg"] == "N"}


def _save(s, serial, part, cmp_cd="NWS", cause="MFD", **kw):
    tok = ok(s.call("wr_verify", serial=serial, part_cd=part))["fetch_tok"]
    return s.call("wr_tkt_save", serial=serial, part_cd=part, cmp_cd=cmp_cd, cause_cd=cause, fetch_tok=tok, **kw)


def t_silent(erp):
    f = erp.session("FSHAIKH")
    v = ok(f.call("wr_verify", serial="RS5-2604-0932", part_cd="WHS-STD-01"))
    r = _save(f, "RS5-2604-0932", "WHS-STD-01")
    i = f.call("wr_issue", tkt_no=r["data"]["tkt_no"])
    good = (v["basis"] == "MFG" and r["rc"] == "S" and r["data"]["status"] == "CQ" and i["err_cd"] == "ERR-WR-0420")
    return good, (f"basis={v['basis']} wty_to={v['wty_to']}; save rc={r['rc']} msg='{r['msg']}' status={r['data']['status']} "
                  f"₹{r['data']['amount']}; issue → {i['err_cd']}")


def t_variant_wty(erp):
    """In warranty: free, part goes out. Out of warranty: chargeable, part waits for the customer's receipt."""
    f = erp.session("FSHAIKH")
    a = ok(_save(f, "RS5-2609-1187", "WHS-STD-01"))
    b = ok(_save(f, "RS5-2511-0377", "WHS-STD-01", cause="WRN"))
    i = f.call("wr_issue", tkt_no=b["tkt_no"], rcpt_no="ANS-R-2290")
    good = a["status"] == "OP" and a["amount"] == 0 and b["status"] == "CQ" and b["amount"] == 112.1 and i["rc"] == "S"
    return good, f"in warranty: {a['status']} ₹{a['amount']}; out: {b['status']} ₹{b['amount']}, issue with receipt → {i['data']}"


def t_variant_waiver(erp):
    """Waiver within the desk's limit is granted at once; with FWD TO it waits for the approver."""
    f = erp.session("FSHAIKH")
    a = ok(_save(f, "RS5-2511-0377", "WHS-STD-01", cause="WRN"))
    w1 = ok(f.call("wr_waive", tkt_no=a["tkt_no"], reason="goodwill"))
    b = ok(_save(f, "RS5-2511-0377", "SVL-STD-01", cmp_cd="LEK", cause="WRN"))
    w2 = ok(f.call("wr_waive", tkt_no=b["tkt_no"], reason="goodwill", fwd_to="NBHOSALE"))
    good = w1["status"] == "OP" and w2["status"] == "WA" and w2["approver"] == "NBHOSALE"
    return good, f"own limit: {w1['status']}; FWD TO: {w2['status']} → {w2['approver']}"


def t_screen_state(erp):
    r = erp.session("FSHAIKH").call("wr_tkt_save", serial="RS5-2609-1187", part_cd="WHS-STD-01", cmp_cd="NWS")
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def t_cascade_stock(erp):
    f = erp.session("FSHAIKH")
    s0 = erp.q1("SELECT on_hand FROM stock WHERE itm_cd='WHS-STD-01' AND whs_cd='WH-PUN-STR'")["on_hand"]
    d = ok(_save(f, "RS5-2609-1187", "WHS-STD-01"))
    ok(f.call("wr_issue", tkt_no=d["tkt_no"]))
    s1 = erp.q1("SELECT on_hand FROM stock WHERE itm_cd='WHS-STD-01' AND whs_cd='WH-PUN-STR'")["on_hand"]
    led = erp.q("SELECT txn,qty FROM stk_ledger WHERE ref=?", d["tkt_no"])
    return s1 == s0 - 1 and len(led) == 1, f"WHS-STD-01 on hand {s0}→{s1}, ledger {[(r['txn'], r['qty']) for r in led]}"


def t_cascade_close(erp):
    f = erp.session("FSHAIKH")
    d = ok(_save(f, "RS5-2609-1187", "WHS-STD-01"))
    ok(f.call("wr_issue", tkt_no=d["tkt_no"]))
    n0 = erp.q1("SELECT count(*) n FROM ntf_queue")["n"]
    ok(f.call("wr_close", tkt_no=d["tkt_no"]))
    ntf = erp.q("SELECT recipient FROM ntf_queue")[n0:]
    cost = erp.q("SELECT kind,amount FROM wr_cost WHERE tkt_no=?", d["tkt_no"])
    good = [n["recipient"] for n in ntf] == ["service@annapurna-stores.example"] and cost == [{"kind": "WARRANTY", "amount": 95.0}]
    return good, f"dealer mail {[n['recipient'] for n in ntf]}, cost {cost}"


def t_shared_engine(erp):
    f = erp.session("FSHAIKH")
    d = ok(_save(f, "RS5-2608-0611", "LID-SS-05L", cmp_cd="CRK", cause="PHY", chg="Y"))
    tax_used = "sp_tax_compute" in erp.calls[-1].sps
    big = ok(_save(f, "RS5-2603-0718", "LID-SS-05L", cmp_cd="CRK", cause="WRN", chg="Y"))
    erp.x("UPDATE wr_ticket SET amount=6136.00 WHERE tkt_no=?", big["tkt_no"])  # six lids for a canteen order, say
    w = ok(f.call("wr_waive", tkt_no=big["tkt_no"], reason="test"))
    routed = "sp_appr_route" in erp.calls[-1].sps
    inbox = ok(erp.session("NBHOSALE").call("po_pending_appr"))["rows"]
    good = tax_used and d["amount"] == 920.4 and routed and w["approver"] == "NBHOSALE" and \
        any(r["doc_no"] == big["tkt_no"] for r in inbox)
    return good, (f"sp_tax_compute: ₹780 → ₹{d['amount']}; waiver ₹6,136 above Farhan's ₹5,000 → sp_appr_route → "
                  f"{w['approver']} (in his purchasing inbox: {any(r['doc_no'] == big['tkt_no'] for r in inbox)})")


def t_policy_only(erp):
    """Warranty Exclusions §2 (physical damage) lives only in the document: Bahi makes the dropped lid free."""
    r = ok(_save(erp.session("FSHAIKH"), "RS5-2608-0611", "LID-SS-05L", cmp_cd="CRK", cause="PHY"))
    return r["status"] == "OP" and r["chg"] == "N", f"dropped lid saved as {r['status']} chg={r['chg']} ₹{r['amount']}"


TRAPS = {
    "silent: sale not registered, saved as chargeable CQ and no part goes out": t_silent,
    "variant: in warranty free vs out of warranty chargeable": t_variant_wty,
    "variant: waiver within own limit vs FWD TO the manager": t_variant_waiver,
    "screen_state: Save without Verify": t_screen_state,
    "cascade: part issue moves stock and the stock ledger": t_cascade_stock,
    "cascade: close emails the dealer and books the cost": t_cascade_close,
    "shared_engine: sp_tax_compute and sp_appr_route": t_shared_engine,
    "policy_only: physical damage not excluded by Bahi": t_policy_only,
}
