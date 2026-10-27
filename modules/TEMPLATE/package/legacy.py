"""The before, scripted: happy_path(erp) walks the three screens; TRAPS triggers each trap in the budget.
Trap names start with their kind: silent, variant, screen_state, cascade, shared_engine, policy_only."""
from .._kit import ok


def happy_path(erp) -> dict:
    k, r = erp.session("KJOSHI"), erp.session("RMEHTA")
    tok = ok(k.call("xx_fetch", screen="XX-ABC-02", task="Fetch", party="Deccan Polymers"))["fetch_tok"]
    d = ok(k.call("xx_save", screen="XX-ABC-02", task="Save", party="Deccan Polymers", qty=5, amount=500,
                  cc_cd="PRD-07", fetch_tok=tok))
    ok(r.call("xx_approve", screen="XX-ABC-03", task="Decide", doc_no=d["doc_no"], decision="A"))
    st = erp.q1("SELECT status FROM xx_doc WHERE doc_no=?", d["doc_no"])["status"]
    return {"doc": d["doc_no"], "status": st, "ok": st == "AP"}


def t_screen_state(erp):
    r = erp.session("KJOSHI").call("xx_save", party="Deccan Polymers", qty=5, amount=500, cc_cd="PRD-07")
    return r["err_cd"] == "ERR-SCR-0221", f"{r['err_cd']} {r['msg']}"


def t_silent(erp):
    s = erp.session("KJOSHI")
    tok = ok(s.call("xx_fetch", party="Deccan Polymers"))["fetch_tok"]
    r = s.call("xx_save", party="Deccan Polymers", qty=5, amount=500, cc_cd="PRD-05", fetch_tok=tok)  # closed cc
    return r["rc"] == "S" and r["data"]["status"] == "HD", f"rc={r['rc']} msg='{r['msg']}' status={r['data']['status']}"


TRAPS = {
    "screen_state: Save without Fetch": t_screen_state,
    "silent: closed cost centre saves as HD": t_silent,
    # TODO: two variants, two cascades, the shared engine, the rule only the policy knows
}
