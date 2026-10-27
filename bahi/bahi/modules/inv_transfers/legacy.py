"""Inventory · transfers: the before, scripted. happy_path() is Neha's sentence done the legacy way, screen by
screen, by the four people it takes; TRAPS triggers each trap in the complexity budget."""
from __future__ import annotations

from .._kit import ok

ITEM, CHK, LINE = "GSK-SIL-05L", "WH-CHK-STR", "WH-PUN-LN5"


def _stock(erp, itm, whs):
    return erp.q1("SELECT on_hand, allocated FROM stock WHERE itm_cd=? AND whs_cd=?", itm, whs)


def happy_path(erp) -> dict:
    """Neha: 2,000 gaskets from Chakan to the Pune line tonight. Anand approves, Ganesh issues, Balu checks out."""
    n, a = erp.session("NDESAI"), erp.session("APATIL")
    g, b = erp.session("GPAWAR"), erp.session("BSALUNKE")
    line0 = _stock(erp, ITEM, LINE)["on_hand"]
    ok(n.call("tr_stk_enq", screen="INV-STK-07", task="Show", itm_cd=ITEM))
    tok = ok(n.call("tr_fetch", screen="INV-TRN-04", task="Fetch", itm_cd=ITEM, from_whs=CHK, to_whs=LINE))["fetch_tok"]
    d = ok(n.call("tr_save", screen="INV-TRN-04", task="Save", itm_cd=ITEM, qty=2000, from_whs=CHK, to_whs=LINE,
                  slot="NIGHT", vehicle="MH-14-GH-2290", fwd_to="APATIL", remarks="Line top-up", fetch_tok=tok))
    ok(a.call("tr_list", screen="INV-STK-07", task="Notes", status="PA"))
    ok(a.call("tr_approve", screen="INV-TRN-04", task="Approve", tn_no=d["tn_no"], decision="A"))
    gp = ok(g.call("tr_gp_create", screen="INV-GTP-05", task="Create", tn_no=d["tn_no"]))["gp_no"]
    ok(b.call("tr_gp_out", screen="INV-GTP-05", task="Check Out", gp_no=gp))
    ok(n.call("tr_receive", screen="INV-GTP-05", task="Receive", tn_no=d["tn_no"], qty_rcvd=2000))
    t = erp.q1("SELECT * FROM tr_note WHERE tn_no=?", d["tn_no"])
    line1 = _stock(erp, ITEM, LINE)["on_hand"]
    return {"doc": d["tn_no"], "status": t["status"],
            "ok": t["status"] == "RC" and t["approver"] == "APATIL" and line1 == line0 + 2000}


def _save(s, itm=ITEM, qty=2000, frm=CHK, to=LINE, **kw):
    tok = ok(s.call("tr_fetch", itm_cd=itm, from_whs=frm, to_whs=to))["fetch_tok"]
    return s.call("tr_save", itm_cd=itm, qty=qty, from_whs=frm, to_whs=to, vehicle=kw.pop("vehicle", "MH-14-GH-2290"),
                  fetch_tok=tok, **kw)


def _dispatch(erp, tn, **kw):
    gp = ok(erp.session("GPAWAR").call("tr_gp_create", tn_no=tn, **kw))["gp_no"]
    return gp, erp.session("BSALUNKE").call("tr_gp_out", gp_no=gp)


def t_silent(erp):
    a0 = _stock(erp, ITEM, CHK)["allocated"]
    r = _save(erp.session("NDESAI"), qty=10000)
    d = r["data"] or {}
    gp = erp.session("GPAWAR").call("tr_gp_create", tn_no=d.get("tn_no", ""))
    good = r["rc"] == "S" and d["status"] == "SH" and _stock(erp, ITEM, CHK)["allocated"] == a0 and \
        gp["err_cd"] == "ERR-TR-0602"
    return good, f"rc={r['rc']} msg='{r['msg']}' status={d['status']}; gate pass: {gp['err_cd']} {gp['msg']}"


def t_variant_int(erp):
    n = erp.session("NDESAI")
    s0, l0 = _stock(erp, "WHS-STD-01", "WH-PUN-STR")["on_hand"], _stock(erp, "WHS-STD-01", LINE)["on_hand"]
    d = ok(_save(n, itm="WHS-STD-01", qty=500, frm="WH-PUN-STR", vehicle=None))
    gp = erp.session("GPAWAR").call("tr_gp_create", tn_no=d["tn_no"])
    ok(n.call("tr_receive", tn_no=d["tn_no"], qty_rcvd=500))
    s1, l1 = _stock(erp, "WHS-STD-01", "WH-PUN-STR")["on_hand"], _stock(erp, "WHS-STD-01", LINE)["on_hand"]
    good = d["mv_type"] == "INT" and gp["err_cd"] == "ERR-TR-0605" and s1 == s0 - 500 and l1 == l0 + 500
    return good, f"INT note {d['tn_no']}: gate pass {gp['err_cd']}; main stores {s0}→{s1}, line {l0}→{l1}"


def t_variant_ewb(erp):
    n = erp.session("NDESAI")
    big = ok(_save(n, qty=5000))
    _, o1 = _dispatch(erp, big["tn_no"])
    small = ok(_save(n, qty=2000))
    _, o2 = _dispatch(erp, small["tn_no"])
    good = o1["err_cd"] == "ERR-TR-0610" and o2["rc"] == "S" and big["gross"] == 70210 and small["gross"] == 28084
    return good, (f"5,000 = Rs {big['gross']:,.0f}: check-out {o1['err_cd']}; 2,000 = Rs {small['gross']:,.0f}: "
                  f"check-out {o2['msg']}")


def t_screen_state(erp):
    r = erp.session("NDESAI").call("tr_save", itm_cd=ITEM, qty=2000, from_whs=CHK, to_whs=LINE)
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def t_cascade_out(erp):
    c0 = _stock(erp, ITEM, CHK)
    d = ok(_save(erp.session("NDESAI"), qty=2000))
    c1 = _stock(erp, ITEM, CHK)
    gp, o = _dispatch(erp, d["tn_no"])
    c2 = _stock(erp, ITEM, CHK)
    led = erp.q1("SELECT * FROM stk_ledger WHERE ref=? AND txn='TRF-OUT'", gp)
    t = erp.q1("SELECT status FROM tr_note WHERE tn_no=?", d["tn_no"])["status"]
    good = c1["allocated"] == c0["allocated"] + 2000 and c2["on_hand"] == c0["on_hand"] - 2000 and \
        c2["allocated"] == c0["allocated"] and led and led["qty"] == -2000 and t == "IT"
    return good, (f"Chakan on hand {c0['on_hand']}→{c2['on_hand']}, allocated {c0['allocated']}→{c1['allocated']}→"
                  f"{c2['allocated']}, ledger TRF-OUT {led['qty'] if led else None}, note {t}")


def t_cascade_in(erp):
    n = erp.session("NDESAI")
    l0 = _stock(erp, ITEM, LINE)["on_hand"]
    d = ok(_save(n, qty=2000))
    _dispatch(erp, d["tn_no"])
    q0 = erp.q1("SELECT count(*) c FROM ntf_queue")["c"]
    r = ok(n.call("tr_receive", tn_no=d["tn_no"], qty_rcvd=2000))
    l1 = _stock(erp, ITEM, LINE)["on_hand"]
    led = erp.q1("SELECT * FROM stk_ledger WHERE ref=? AND txn='TRF-IN'", r["rc_no"])
    q1 = erp.q1("SELECT count(*) c FROM ntf_queue")["c"]
    good = l1 == l0 + 2000 and led and led["qty"] == 2000 and q1 == q0 + 1
    return good, f"line store {l0}→{l1}, ledger TRF-IN {led['qty'] if led else None}, notifications +{q1 - q0}"


def t_shared_engine(erp):
    d = ok(_save(erp.session("NDESAI"), qty=2000))
    sps = erp.calls[-1].sps
    return "sp_tax_compute" in sps and d["gross"] == 28084, f"sp_tax_compute in save: {'sp_tax_compute' in sps}; value Rs {d['gross']:,.0f}"


def t_policy_only(erp):
    """Gate Pass Policy §4.2 (night moves need the plant head) is only in the document: Bahi routes to Rohit."""
    d = ok(_save(erp.session("NDESAI"), qty=2000, slot="NIGHT"))
    a = erp.q1("SELECT approver FROM approval WHERE doc_no=?", d["tn_no"])
    return d["status"] == "PA" and a["approver"] == "RMEHTA", f"night move {d['tn_no']} routed to {a['approver']} (policy says APATIL)"


TRAPS = {
    "silent: more than free stock, saved as SH and never reaches the gate": t_silent,
    "variant: move inside one unit needs no gate pass": t_variant_int,
    "variant: above Rs 50,000 the gate needs an e-way bill": t_variant_ewb,
    "screen_state: Save without Fetch": t_screen_state,
    "cascade: check-out takes stock out of Chakan": t_cascade_out,
    "cascade: receipt puts stock on the line and tells the requester": t_cascade_in,
    "shared_engine: sp_tax_compute values the consignment": t_shared_engine,
    "policy_only: night move routed to the manager, not the plant head": t_policy_only,
}
