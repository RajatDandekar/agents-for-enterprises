"""The 2D layer of the L1 film: every readable word (titles, pins, number punches, JSON,
the chat UI on Emma's screen, subtitles, end card) as a list of timed elements.

Times are GLOBAL frames looked up from narration words (timeline.json). All numbers and
strings below are copied from flow3d/trace.json (the recorded run).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


class TL:
    def __init__(self, path=os.path.join(HERE, "timeline.json")):
        self.t = json.load(open(path))
        self.blocks = {b["id"]: b for b in self.t["blocks"]}
        self.shots = self.t["shots"]

    def w(self, block, text, nth=0, edge="f0"):
        norm = lambda s: s.lower().strip(".,?:!;")  # noqa: E731
        ws = [x for x in self.t["words"] if x["block"].startswith(block)]
        text = norm(text)
        hits = [x for x in ws if norm(x["w"]) == text] or [x for x in ws if norm(x["w"]).startswith(text)]
        if len(hits) <= nth:
            raise KeyError(f"{block}:{text}#{nth}")
        return hits[nth][edge]

    def shot(self, name):
        return next(s for s in self.shots if s["shot"] == name)

    def block(self, prefix):
        return next(b for k, b in self.blocks.items() if k.startswith(prefix))


SENT = re.compile(r"(?<=[.?!:])\s+")


def subtitles(tl, script):
    """One cue per sentence (long ones split at commas), timed by the spoken words."""
    cues = []
    for b in script["blocks"]:
        ts, ss = SENT.split(b["text"].strip()), SENT.split(b["say"].strip())
        assert len(ts) == len(ss), (b["id"], len(ts), len(ss))
        ws = [x for x in tl.t["words"] if x["block"] == b["id"]]
        i = 0
        for t, s in zip(ts, ss):
            n = len(s.split())
            seg = ws[i:i + n]
            i += n
            f0, f1 = seg[0]["f0"], seg[-1]["f1"]
            parts = [t]
            if len(t) > 62:
                bits = re.split(r"(?<=,)\s+", t)
                parts, cur = [], ""
                for bt in bits:
                    if cur and len(cur) + len(bt) > 58:
                        parts.append(cur)
                        cur = bt
                    else:
                        cur = (cur + " " + bt).strip()
                parts.append(cur)
            tot = sum(len(p) for p in parts)
            acc = 0
            for p in parts:
                a = f0 + round((f1 - f0) * acc / tot)
                acc += len(p)
                e = f0 + round((f1 - f0) * acc / tot)
                cues.append({"t": "sub", "f0": a, "f1": e + 6, "text": p})
    # no gap flicker: extend each cue to the next if the gap is short
    for a, c in zip(cues, cues[1:]):
        if 0 < c["f0"] - a["f1"] < 12:
            a["f1"] = c["f0"]
    return cues


def build(tl, script):
    W = tl.w
    E = []

    def add(**k):
        E.append(k)

    total = tl.t["total"]
    endf = tl.t["end_card_f0"]

    # ---- title (typed) over the opening shot
    add(t="title", f0=8, f1=96, kicker="AGENTIC SYSTEMS ENGINEERING  ·  LECTURE 1",
        h="How Ask Northbridge works, underneath", sub="One real request, recorded in our sandbox")

    # ---- 1 chat: Emma's screen
    sc = tl.shot("chat")
    q1 = "How many city e-bike battery packs do we have?"
    r1 = ("We currently have 6,600 city e-bike battery packs (BAT-500, 36 V 500 Wh) in stock:\n"
          "• Manchester main stores: 5,400\n• Leeds stores: 1,200\n"
          "None are allocated or on order, so all 6,600 are available (11 days of cover, well above the 3,000 reorder level).")
    ft = W("n01", "types")
    fsend = W("n01", "have?") + 8
    fans = W("n01", "answer.") - 6
    add(t="chat", shot="chat", f0=sc["g0"], f1=sc["g1"] + tl.t["xf"],
        states=[{"f": 0, "msgs": [], "typing": ""},
                {"f": ft, "msgs": [], "typing": q1, "type_to": fsend - 4},
                {"f": fsend, "msgs": [["user", q1]], "typing": "", "thinking": True},
                {"f": fans, "msgs": [["user", q1], ["bot", r1]], "typing": ""}])
    add(t="chip", f0=W("n01", "emma"), f1=W("n01", "cycles.") + 70, x=110, y=120,
        h="Emma Clarke", sub="Buyer, Northbridge Cycles, Manchester", accent="sky")
    add(t="punch", f0=W("n01", "between?") - 4, f1=sc["g1"] + 4, x=960, y=500, value="?",
        label="what happened in those seconds", accent="sky", small=True, hide=True)

    # ---- 2 harness bench: the context ledger
    sh = tl.shot("harness")
    add(t="pin", shot="harness", anchor="bench", f0=W("n02", "harness"), f1=W("n02", "bench.") + 40,
        h="The harness", sub="the code around the model", dx=-260, dy=-210, accent="sky")
    rows = [("System prompt", "our rules", "196", W("n02", "rules.")),
            ("Her message", "the history so far", "11", W("n02", "message.")),
            ("15 tool descriptions", "name, purpose, JSON schema", "1,932", W("n02", "description"))]
    add(t="ledger", f0=W("n02", "rules.") - 4, f1=sh["g1"] + 4, x=1290, y=200, title="One request",
        rows=rows, total=("2,139", "tokens", W("n02", "two")), accent="sky")
    add(t="punch", f0=W("n02", "two") - 2, f1=sh["g1"] + 4, x=520, y=860, value="2,139",
        label="tokens in one request", accent="sky")

    # ---- 3 the model
    sm = tl.shot("model")
    add(t="pin", shot="model", anchor="model_top", f0=W("n03", "reads") - 6, f1=W("n03", "twist:") + 10,
        h="The model", sub="reads all 2,139 tokens, layer by layer", dx=-420, dy=-60, accent="sky")
    add(t="chip", f0=W("n03", "reads") + 20, f1=W("n03", "answer.") + 30, x=110, y=800,
        h="2,139 tokens in  ·  21 out  ·  2.68 s", sub="gemini-3.8-flash, model call 1 of 13", accent="sky")
    tools = ["find_item", "check_stock", "find_supplier", "check_budget", "search_policy", "create_purchase_request",
             "list_my_approvals", "approve_purchase_request", "create_purchase_order", "approve_purchase_order",
             "release_purchase_order", "order_status", "receive_goods", "register_supplier", "send_message"]
    add(t="tools", f0=W("n03", "picks") - 16, f1=sm["g1"] + 4, x=1420, y=60, tools=tools, pick="find_item",
        f_pick=W("n03", "fifteen,") + 4, accent="sky")
    add(t="punch", f0=W("n03", "one", 1) - 2, f1=W("n03", "json.") + 4, x=1420, y=830, value="1 of 15",
        label="tools chosen: find_item", accent="sky", left=True)
    add(t="pin", shot="model", anchor="cart_find_item", f0=W("n03", "fifteen,") + 4, f1=W("n03", "find") + 30,
        h="find_item", sub="slides out: the one tool it chose", dx=-760, dy=150, accent="sky")
    add(t="code", f0=W("n03", "json.") - 14, f1=sm["g1"] + 4, x=110, y=640, title="tool call  ·  JSON",
        lines=['{', '  "name": "find_item",', '  "arguments": {', '    "query": "city e-bike battery pack"', '  }', '}'],
        accent="sky", typed=True)

    # ---- 4 guard + MCP
    sg = tl.shot("guard")
    add(t="pin", shot="guard", anchor="guard", f0=W("n04", "guard") - 4, f1=W("n04", "then") + 6,
        h="The guard", sub="checks the call against find_item's schema", dx=-430, dy=-200, accent="green")
    add(t="code", f0=W("n04", "checks") - 6, f1=W("n04", "then") + 20, x=110, y=560, title="guard  ·  schema check",
        lines=['query      string    "city e-bike battery pack"', 'required   [query]', 'writes     false'],
        checks=[W("n04", "fields,"), W("n04", "types."), W("n04", "types.") + 12], accent="green")
    add(t="pin", shot="guard", anchor="mcp_plug", f0=W("n04", "plug,") - 6, f1=sg["g1"] + 4,
        h="MCP", sub="the standard plug between harness and tools", dx=-360, dy=-260, accent="sky")
    add(t="code", f0=W("n04", "carries") - 4, f1=sg["g1"] + 4, x=1180, y=620, title="MCP  ·  JSON-RPC frame",
        lines=['{"jsonrpc": "2.0",', ' "method": "tools/call",', ' "params": {"name": "find_item",',
               '   "arguments": {"query": "city e-bike', '                 battery pack"}}}'], accent="sky", typed=True)
    add(t="pin", shot="guard", anchor="rack_top", f0=W("n04", "toolbox.") - 4, f1=sg["g1"] + 4,
        h="Toolbox", sub="15 tools  ·  find_item slides out", dx=120, dy=-120, accent="sky")

    # ---- 5 Ledgerline
    se = tl.shot("erp")
    add(t="pin", shot="erp", anchor="erp_badge", f0=W("n05", "ledgerline") - 4, f1=se["g1"] + 4,
        h="Ledgerline ERP 7.2", sub="since 1998  ·  the system of record", dx=200, dy=-200, accent="ember")
    add(t="chip", f0=W("n05", "permissions.") - 20, f1=se["g1"] + 4, x=110, y=150,
        h="as ECLARKE", sub="Emma's own permissions, nobody else's", accent="ember")
    add(t="code", f0=W("n05", "in,") - 4, f1=se["g1"] + 4, x=110, y=640, title="data in  ·  11 service calls",
        lines=['itm_search  "city e-bike battery pack"   0 rows', 'itm_search  "city"                       0 rows',
               'itm_search  ... 3 more                   rc S', 'itm_get     BAT-500 ... x6              rc S'], accent="ember")
    add(t="code", f0=W("n05", "out.") - 4, f1=se["g1"] + 4, x=1150, y=640, title="data out  ·  find_item",
        lines=['BAT-500     Battery pack, 36 V 500 Wh', 'BAT-500-R   ... (refurbished)', 'BAT-375     Battery pack, 36 V 375 Wh',
               'BAT-750     Battery pack, 48 V 750 Wh', '+ 2 more items'], accent="green")

    # ---- 6 the loop
    sl = tl.shot("loop")
    laps = [("1", "find_item", "6 items found", sl["g0"] + 20, "2,139"),
            ("2", "search_policy", "the manuals: item codes", W("n06", "manuals."), "2,507"),
            ("3", "check_stock  BAT-500", "6,600 free  ·  11 days of cover", W("n06", "stock."), "2,894"),
            ("4", "check_stock  BAT-500-R", "no stock record", W("n06", "grows.") - 10, "3,218"),
            ("5", "reply", "no tool call: the answer", W("n06", "later:") - 10, "3,325")]
    add(t="laps", f0=sl["g0"] + 14, f1=sl["g1"] + 4, x=1170, y=80, title="The loop  ·  5 model calls", laps=laps)
    add(t="pin", shot="loop", anchor="bench_stack", f0=W("n06", "grows.") - 20, f1=sl["g1"] + 4,
        h="The context grows", sub="2,139 tokens, then 3,325", dx=60, dy=-300, accent="sky")
    add(t="punch", f0=W("n06", "six") - 2, f1=sl["g1"] + 4, x=1300, y=820, value="6,600",
        label="packs free  ·  11 days of cover", accent="green")

    # ---- 7 refusal
    sr = tl.shot("refuse")
    q2 = "Order 2,000 battery packs from Voltway Cells for the spring launch run, cost centre PRD-07, needed by 9 November."
    add(t="bubble", f0=W("n07", "asks") - 6, f1=W("n07", "tries") + 10, x=110, y=130, who="Emma", text=q2)
    add(t="pin", shot="refuse", anchor="cart_create_purchase_order", f0=W("n07", "direct", 0) - 4, f1=W("n07", "no.") - 10,
        h="create_purchase_order", sub="tries a direct order", dx=150, dy=-170, accent="ember")
    add(t="code", f0=W("n07", "no.") - 2, f1=sr["g1"] + 4, x=110, y=560, title="tool result  ·  refused",
        lines=['{"ok": false,', ' "error": "A direct order is limited to', '          £50,000; this one is £285,600.",',
               ' "next_step": "Raise a purchase request first', '              with create_purchase_request."}'], accent="ember")
    add(t="stamp", f0=W("n07", "no.") + 2, f1=W("n07", "raise") + 30, x=1330, y=330, h="REFUSED",
        sub="raise a purchase request first")
    add(t="punch", f0=W("n07", "fifty") - 2, f1=sr["g1"] + 4, x=1250, y=830, value="£50,000",
        label="direct-order limit  ·  this order is £285,600", accent="ember")

    # ---- 8 preview + yes (Emma's screen again)
    sp = tl.shot("preview")
    r2 = ("Because this order exceeds the £50,000 direct-order threshold, a purchase request must be raised first. Here is the preview:\n"
          "• 2,000 × BAT-500 (36 V 500 Wh battery pack)\n• PRD-07 (Spring launch run) by 09/11/2026\n"
          "• Estimated value: £273,600 (exceeds your £250,000 approval limit; routes to Daniel Okafor)\n"
          "Shall I go ahead and submit this purchase request?")
    fy = W("n08", "yes.")
    add(t="chat", shot="preview", f0=sp["g0"] - tl.t["xf"], f1=sp["g1"] + tl.t["xf"],
        states=[{"f": 0, "msgs": [["user", q2]], "typing": "", "thinking": True},
                {"f": W("n08", "preview.") - 10, "msgs": [["user", q2], ["bot", r2]], "typing": ""},
                {"f": fy - 30, "msgs": [["user", q2], ["bot", r2]], "typing": "Yes, go ahead.", "type_to": fy - 2},
                {"f": fy, "msgs": [["user", q2], ["bot", r2], ["user", "Yes, go ahead."]], "typing": ""}])
    add(t="punch", f0=W("n08", "two") - 2, f1=W("n08", "shall") + 4, x=1190, y=330, value="£273,600",
        label="preview only  ·  nothing saved", accent="sky", left=True)
    add(t="chip", f0=W("n08", "daniel") - 4, f1=W("n08", "shall"), x=1190, y=480,
        h="Approver: Daniel Okafor (DOKAFOR)", sub="above Emma's £250,000 limit", accent="sky")

    # ---- 9 the write
    sw = tl.shot("write")
    add(t="chip", f0=W("n09", "saves") - 4, f1=sw["g1"] + 4, x=110, y=130, h="pr_save  ·  pr_submit",
        sub="the only writes, after Emma's yes", accent="ember")
    add(t="ripple", shot="write", anchor="tray", f0=W("n09", "lands"), f1=W("n09", "lands") + 40)
    add(t="pin", shot="write", anchor="tray", f0=W("n09", "lands") - 4, f1=sw["g1"] + 4,
        h="Daniel's approval inbox", sub="PO/2026/01179  ·  PR/2026/04417  new", dx=180, dy=-240, accent="sky")
    add(t="punch", f0=W("n09", "request", 1) - 2, f1=sw["g1"] + 4, x=110, y=830, value="PR/2026/04417",
        label="£273,600  ·  2,000 × BAT-500  ·  waiting for Daniel", accent="sky", left=True)

    # ---- 10 the receipt
    sv = tl.shot("receipt")
    add(t="code", f0=W("n10", "reads") - 4, f1=sv["g1"] + 4, x=1180, y=300, title="pr_get  ·  read back from Ledgerline",
        lines=['request_no   PR/2026/04417', 'status       WAITING FOR APPROVAL', 'status_code  PA',
               'approver     DOKAFOR', 'value        £273,600', 'next_step    nothing is ordered yet'], accent="green", typed=True)
    add(t="bubble", f0=W("n10", "emma") - 4, f1=sv["g1"] + 4, x=110, y=560, who="Ask Northbridge",
        text="Purchase request PR/2026/04417 has been raised and is WAITING FOR APPROVAL from Daniel Okafor (DOKAFOR) for £273,600. Nothing has been ordered yet.", bot=True)

    # ---- 11 close: the whole machine, one label per station on its word
    sx = tl.shot("close")
    add(t="bigline", f0=W("n11", "one") - 2, f1=endf, x=960, y=150, parts=[("One sentence in.", W("n11", "one") - 2),
                                                                        ("A receipt out.", W("n11", "a") - 2)])
    for anc, word, h, sub, dx, dy in [("bench", "harness", "The harness", "builds the context", -40, -200),
                                      ("model_top", "model", "The model", "picks a tool", 0, -130),
                                      ("guard", "guard", "The guard", "checks it", -60, -230),
                                      ("mcp_plug", "m", "MCP", "carries it", 60, -170),
                                      ("erp", "ledgerline", "Ledgerline", "does the work", 0, -170)]:
        add(t="pin", shot="close", anchor=anc, f0=W("n11", word) - 4, f1=endf, h=h, sub=sub, dx=dx, dy=dy,
            accent="ember" if h == "Ledgerline" else "sky")
    add(t="end", f0=endf, f1=total, h="One sentence in. A receipt out.",
        sub="The harness builds the context  ·  the model picks a tool  ·  the guard checks it  ·  MCP carries it  ·  Ledgerline does the work",
        credits=["Agentic Systems Engineering  ·  Lecture 1  ·  Dr. Rajat Dandekar  ·  Vizuara",
                 "One real run of Ask Northbridge in the course sandbox (gemini-3.8-flash, recorded 30 Oct 2026)",
                 "Narration: Daniel (ElevenLabs)  ·  Music: Observatory, Out To The World (Epidemic Sound)  ·  Rendered in Blender Cycles"])
    E += subtitles(tl, script)
    return E
