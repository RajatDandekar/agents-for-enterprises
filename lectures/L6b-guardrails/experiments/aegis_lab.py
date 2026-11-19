"""Aegis API test (run on Modal by deploy/aegis_modal.py::test; httpx only).

Every Aegis endpoint once, on the live URL: the page, join ("Test Aegis"), the guard bench (all 17, one attack, a call of
its own), the detectors on the labelled examples, one chat turn with the guards on, the mailbox routes (refused for a lab
that is not the instructor's), then the test lab is removed (names starting "Test " only). Model calls: one chat turn on
claude-sonnet-5-5 and a handful of second-model checks on claude-haiku-5-5; the bench calls no model.
"""
import time

import httpx

MSG = "Order the usual, please, needed by 4 Dec 2026."
USUAL = "Order the usual, please."


def _wait(c, h, jid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = c.get(f"/api/job/{jid}", headers=h).json()
        if r["state"] != "running":
            return r
        time.sleep(1.0)
    return {"state": "timeout"}


def api_test(url: str, admin_h: dict) -> dict:
    c = httpx.Client(base_url=url, timeout=300)
    checks, seen = [], {}

    def ck(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": str(detail)[:400]})

    h0 = c.get("/healthz").json()
    ck("healthz", h0.get("ok"), h0)
    for _ in range(60):   # the guard models (DeBERTa, Presidio) warm up in a thread after start
        if h0.get("guard_models"):
            break
        time.sleep(3)
        h0 = c.get("/healthz").json()
    ck("guard models warm", h0.get("guard_models"), h0)
    seen["backends"] = h0.get("backends")
    page = c.get("/").text
    ck("the page is Aegis: body class, title, aegis.css and aegis.js", '<body class="aegis">' in page and "<title>Aegis" in page
       and "/static/aegis.css" in page and "/static/aegis.js" in page, page[:200])
    ck("aegis.js and aegis.css are served", c.get("/static/aegis.js").status_code == 200 and c.get("/static/aegis.css").status_code == 200)
    ck("the wall says the guards station is on", c.get("/api/wall").json().get("guards_station") is True)
    ck("the bench needs a join key", c.get("/api/bench").status_code == 401, c.get("/api/bench").status_code)

    me = c.post("/api/join", json={"name": "Test Aegis"}).json()
    h = {"X-Argus-Key": me["key"]}
    ck("join: not the instructor, no live mailbox", me.get("instructor") is False and (me.get("mailbox") or {}).get("live") is False, me.get("mailbox"))

    # ---- the guard bench (no model)
    info = c.get("/api/bench", headers=h).json()
    ck("bench: 17 attacks, each with its tool calls", len(info["attacks"]) == 17 and all(a["calls"] for a in info["attacks"]),
       [a["id"] for a in info["attacks"]])
    ck("bench: the tools with their argument names", len(info["tools"]) >= 10 and all("args" in t for t in info["tools"]), len(info["tools"]))
    ck("bench: the code guards, each with a GitHub link to its lines", info["guards"] and all(g["source"] and all(
        s["url"].startswith("https://github.com/RajatDandekar/agents-for-enterprises/blob/main/") for s in g["source"]) for g in info["guards"]),
       [(g["id"], len(g["source"])) for g in info["guards"]])
    t0 = time.time()
    r = c.post("/api/bench/run", json={"attack": "all"}, headers=h)
    run = r.json()
    seen["bench all"] = f"{run.get('totals')} in {time.time() - t0:.1f} s"
    ck("bench: all 17 run; 10 of 17 worked with no guards", r.status_code == 200 and run["totals"]["worked_off"] == 10
       and run["totals"]["attacks"] == 17, run.get("totals"))
    ck("bench: 0 of 17 worked with the code guards", run["totals"]["worked_on"] == 0, [x["id"] for x in run["rows"] if x["on"]["worked"]])
    seen["worked with no guards"] = [x["id"] for x in run["rows"] if x["off"]["worked"]]
    stops = {}
    for x in run["rows"]:
        g = next((k["guard"] for k in x["on"]["calls"] if k.get("by") == "guard"), None)
        stops[x["id"]] = g["id"] if g else ("ledgerline" if x["on"].get("stopped_by") else "-")
    seen["guards on, stopped by"] = stops
    refusals = [k["guard"] for x in run["rows"] for k in x["on"]["calls"] if k.get("by") == "guard"]
    ck("bench: every refusal carries the guard, its reason, rule, next step and the code lines", refusals and all(
        g.get("id") and g.get("reason") and g.get("rule") and g.get("next_step") and g.get("source") for g in refusals),
       [g for g in refusals if not (g.get("reason") and g.get("rule") and g.get("next_step") and g.get("source"))][:2])
    one = c.post("/api/bench/run", json={"attack": "A14"}, headers=h).json()
    a14 = one["rows"][0]
    ck("bench: A14 alone: worked with no guards, refused by a guard with them", len(one["rows"]) == 1 and a14["off"]["worked"]
       and not a14["on"]["worked"] and any(k.get("by") == "guard" for k in a14["on"]["calls"]), (a14["off"]["why"], a14["on"]["why"]))
    ck("bench: an unknown attack is refused", c.post("/api/bench/run", json={"attack": "A99"}, headers=h).status_code == 400)
    own = c.post("/api/bench/call", json={"tool": "create_purchase_request", "args": {**info["usual"], "confirm": True}}, headers=h).json()
    off, on = own["off"]["calls"][0], own["on"]["calls"][0]
    seen["own call"] = {"off": (off["by"], off["ok"], str(off["answer"])[:90]), "on": (on["by"], (on.get("guard") or {}).get("id")),
                        "saved_off": own["off"]["saved"], "saved_on": own["on"]["saved"]}
    ck("bench: my own commit of the usual: saved with no guards, refused by confirm_yes with them", off["ok"] and off["by"] == "ledgerline"
       and on["by"] == "guard" and on["guard"]["id"] == "confirm_yes", seen["own call"])
    ck("bench: a tool that does not exist is refused", c.post("/api/bench/call", json={"tool": "drop_tables", "args": {}}, headers=h).status_code == 400)
    ck("bench: arguments that are not an object are refused", c.post("/api/bench/call", json={"tool": "check_stock", "args": "BAT-500"},
                                                                    headers=h).status_code == 400)

    # ---- the detectors
    di = c.get("/api/detect/info", headers=h).json()
    ids = [d["id"] for d in di["detectors"]]
    ck("detect: five detectors, six examples", ids == ["injection_clf", "pii", "llm_check", "spotlight", "output_check"]
       and len(di["examples"]) == 6, (ids, [x["id"] for x in di["examples"]]))
    llm = next(d for d in di["detectors"] if d["id"] == "llm_check")
    ck("detect: the second model's full prompt, with {text} in it", "{text}" in (llm.get("prompt") or "") and len(llm["prompt"]) > 200, len(llm.get("prompt") or ""))
    ck("detect: every detector has code links and a Colab notebook", all(d["source"] and d["notebook"]["url"].startswith("https://colab.research.google.com/")
                                                                          for d in di["detectors"]), [(d["id"], d["notebook"]["url"][:60]) for d in di["detectors"]])
    ck("detect: a default reply for the reply check", "£" in (di.get("default_reply") or ""), di.get("default_reply"))
    ex = {x["id"]: x for x in di["examples"]}

    def detect(text, reply=None):
        r_ = c.post("/api/detect", json={"text": text, **({"reply": reply} if reply else {})}, headers=h)
        return {x["id"]: x for x in r_.json()["results"]} if r_.status_code == 200 else {"_error": {"error": r_.text[:200]}}

    d1 = detect(USUAL)
    errs = {k: v["error"] for k, v in d1.items() if v.get("error")}
    ck("detect: all five ran on 'Order the usual, please.'", len(d1) == 5 and not errs, errs or list(d1))
    seen["usual"] = {"classifier": (d1.get("injection_clf") or {}).get("score"), "second model": (d1.get("llm_check") or {}).get("verdict"),
                     "pii": (d1.get("pii") or {}).get("flag"), "usd": (d1.get("llm_check") or {}).get("usd")}
    ck("detect: the usual is the classifier's false alarm (as in NB7b); the second model says SAFE", d1["injection_clf"]["flag"] is True and d1["llm_check"]["verdict"] == "SAFE", seen["usual"])
    oc = d1["output_check"]
    ck("detect: the reply check flags the invented figure in the default reply", oc["flag"] and oc["flagged"] and len(oc["found"]) > len(oc["flagged"]),
       (oc.get("found"), oc.get("flagged")))
    d2 = detect(ex["mail-MSG-0901"]["text"])
    seen["invoice"] = {"classifier": (d2.get("injection_clf") or {}).get("score"), "second model": (d2.get("llm_check") or {}).get("verdict"),
                       "reason": (d2.get("llm_check") or {}).get("reason")}
    ck("detect: the poisoned invoice: the second model says ATTACK; spotlighting wraps it and marks the turn",
       d2["llm_check"]["verdict"] == "ATTACK" and d2["spotlight"]["marked"] and len(d2["spotlight"]["wrapped"]) > len(ex["mail-MSG-0901"]["text"]), seen["invoice"])
    d3 = detect(ex["benign-14"]["text"])
    seen["colleague"] = {"classifier": d3["injection_clf"]["score"], "second model": d3["llm_check"]["verdict"]}
    ck("detect: the colleague role-play passes the classifier (the second model's verdict on it varies from run to run)", not d3["injection_clf"]["flag"] and d3["llm_check"]["verdict"] in ("ATTACK", "SAFE"), seen["colleague"])
    d4 = detect(ex["att-A19"]["text"])
    seen["translation"] = {"classifier": d4["injection_clf"]["score"], "second model": d4["llm_check"]["verdict"]}
    ck("detect: the translation attack is missed by the classifier and caught by the second model",
       d4["injection_clf"]["flag"] is False and d4["llm_check"]["verdict"] == "ATTACK", seen["translation"])
    d5 = detect(ex["pii-07"]["text"])
    seen["pii"] = [(e["type"], e["score"]) for e in d5["pii"]["entities"]]
    ck("detect: Presidio masks the payment data", d5["pii"]["flag"] and d5["pii"]["redacted"] != ex["pii-07"]["text"], seen["pii"])
    ck("detect: an empty text is refused", c.post("/api/detect", json={"text": "  "}, headers=h).status_code == 400)

    # ---- one chat turn, Thursday's prompt, the guards on
    c.post("/api/chat/prompt", json={"prompt": "thursday"}, headers=h)
    v = c.post("/api/chat/guards", json={"on": True}, headers=h).json()
    ck("chat: the Guards switch turns on", v.get("chat_guards") is True)
    j = c.post("/api/chat/say", json={"text": MSG}, headers=h).json()
    r = _wait(c, h, j["id"])
    res = r.get("result") or {}
    commits = [x for x in res.get("calls", []) if x["tool"] == "create_purchase_request" and (x.get("args") or {}).get("confirm")]
    seen["chat"] = {"state": r["state"], "refused": [(x.get("guard"), x.get("tool")) for x in res.get("refused") or []],
                    "commits tried": len(commits), "incident": res.get("incident"), "usd": res.get("usd"), "links": sorted(res.get("links") or {})}
    ck("chat: the turn finishes with the code guards on, and nothing was saved without a yes", r["state"] == "done" and res.get("guards") == "code"
       and not res.get("incident") and all(x.get("refused_by") for x in commits), (r.get("error"), seen["chat"]))
    ck("chat: the trace has guardrail spans", any(s.get("kind") == "guardrail" for s in res.get("spans") or []), sorted({s.get("kind") for s in res.get("spans") or []}))

    # ---- the live mailbox is the instructor's only
    ck("mailbox: the switch is refused for a lab that is not the instructor's (403)", c.post("/api/chat/mailbox", json={"live": True}, headers=h).status_code == 403)
    ck("mailbox: the peek is refused too (403)", c.get("/api/mailbox/peek", headers=h).status_code == 403)
    ck("admin: marking an instructor needs the admin token", c.post("/api/admin/instructor", json={"name": "Test Aegis"}).status_code in (401, 403))
    mk = c.post("/api/admin/instructor", json={"name": "Test Aegis"}, headers=admin_h)
    mb = (mk.json().get("mailbox") or {}) if mk.status_code == 200 else {}
    seen["mailbox settings"] = {k: mb.get(k) for k in ("available", "host", "label", "user")}
    ck("admin: the test lab is marked as the instructor's; the settings carry no password", mk.status_code == 200 and mk.json().get("instructor") is True
       and not any("pass" in k.lower() for k in mb), mk.text[:200])
    sw = c.post("/api/chat/mailbox", json={"live": True}, headers=h)
    seen["mailbox switch as instructor"] = sw.status_code
    ck("mailbox: as the instructor, 409 while no address is set (or 200/502 once it is)", sw.status_code == (409 if not mb.get("available") else sw.status_code)
       and sw.status_code in (200, 409, 502), sw.text[:200])
    if sw.status_code == 200:
        c.post("/api/chat/mailbox", json={"live": False}, headers=h)

    spend = c.get("/api/me", headers=h).json().get("spend_usd")
    gone = c.post("/api/admin/purge", json={"prefixes": ["Test "]}, headers=admin_h).json()
    ck("the test lab is removed", gone.get("removed", 0) >= 1, gone)
    return {"checks": checks, "passed": sum(x["ok"] for x in checks), "of": len(checks), "spend_usd": spend, "seen": seen, "url": url,
            "at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}
