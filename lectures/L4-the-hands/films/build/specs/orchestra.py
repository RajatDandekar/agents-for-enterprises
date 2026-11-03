"""2D overlays + SFX for film 3, "Many tools, one request". The trace panels list every real call with its real
arguments and a summary of its real result, read at build time from experiments/logs/our_harness.json (run
order_hands; the flashback from run order) and experiments/logs/claude_harness.json (runs.order_hands, comparison)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L4 = os.path.dirname(os.path.dirname(HERE))
LOGS = os.path.join(L4, "experiments", "logs")
OH = json.load(open(os.path.join(LOGS, "our_harness.json")))
OURS, EARLIER = OH["order_hands"], OH["order"]
CH = json.load(open(os.path.join(LOGS, "claude_harness.json")))
CL = CH["runs"]["order_hands"]
CMP = CH["comparison"]
POSTER = 66.0
MUSIC = "observatory_out_to_the_world.mp3"
KICK = "Agentic Systems Engineering  ·  Lecture 4"
_S = {}
OUR_CONTROL = [("model", 1, f"the model: {OURS['model'].split(':')[-1]}, and its route"),
               ("prompt", 0, f"the system prompt: {OURS['system_prompt_name'].split(' (')[0]}, no codes"),
               ("tools", 0, f"which tools Emma sees ({len(OURS['tools_exposed'])} here), in her own session"),
               ("battery-safety", 0, "a battery-safety guard before every write"),
               ("fourteen-round", 0, "a loop limit: " + OURS["harness"].split("(")[1].rstrip(")")),
               ("log", 0, "a log of every call: tokens in and out, cost")]


def shorten(s, n):
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def j(o):
    return json.dumps(o, ensure_ascii=False)


def short_args(tool, a):
    if tool == "create_purchase_request":
        keep = [k for k in ("confirm", "need_by") if k in a]
        return ", ".join(f"{k}={j(a[k])}" for k in keep) + ", …"
    if not a:
        return ""
    if tool == "search_policy":
        return "question=" + j(shorten(a["question"], 30))
    return ", ".join(f"{k}={j(v)}" for k, v in a.items())


def summary(tool, a, r):
    if not r.get("ok", True) and "error" in r:
        return r["error"]
    if tool == "find_item":
        return f"{r['items'][0]['item_code']}  ({r['items'][0]['description']})"
    if tool == "find_supplier":
        m = r["matches"][0]
        return f"{m['supplier_code']}  {m['name']}  ({len(r['matches'])} matches)"
    if tool == "check_budget":
        if "open" in r and isinstance(r["open"], list):
            return f"{len(r['open'])} open cost centres, incl. {r['open'][0]['code']} {r['open'][0]['name']}"
        return f"{r['code']} open, £{r['budget_left']:,.0f} left"
    if tool == "search_policy":
        return r["clauses"][0]["cite"] if r.get("answer_in_documents") else "no clause in the documents"
    if tool == "check_stock":
        return ",  ".join(f"{x['on_hand']:,} {x['name'].split()[0]}" for x in r["warehouses"])
    if tool == "supplier_certificates":
        c = r["certificates"][0]
        return f"{c['cert_type']} {r['un38_3']}, to {c['valid_to']}"
    if tool == "create_purchase_request":
        if "request_no" in r:
            return f"{r['request_no']}  {r['status']}"
        p = r["preview"]
        return f"preview: need_by {p['need_by']}, £{p['estimated_value']:,.0f}, approver {p['approver']}"
    return ""


def our_calls():
    out = []
    for t in OURS["turns"]:
        for c in t["cards"]:
            out.append((c["tool"], c["args"], c["result"]))
    return out


def claude_calls():
    res = {s["id"]: s for s in CL["steps"] if s["kind"] == "tool_result"}
    out = []
    for s in CL["steps"]:
        if s["kind"] == "tool_call":
            r = res[s["id"]]
            try:
                rj = json.loads(r["content"])
            except Exception:
                rj = {}
            out.append((s["tool"], s.get("arguments") or {}, rj))
    return out


def sched(tl):
    """Frame (seconds) at which each call's tile has landed, mirroring scenes/orchestra.py (launch + 22 + 4 + 12)."""
    w = _w(tl)
    launch = [w("b2", "three"), w("b2", "three") + 3 / 30, w("b2", "three") + 6 / 30, w("b3", "budget") - 18 / 30, w("b3", "budget") - 15 / 30,
              w("b3", "second") - 10 / 30, w("b3", "stock") - 20 / 30, w("b4", "previews") - 12 / 30, w("b4", "checks") - 16 / 30,
              w("b5", "second") - 12 / 30, w("b5", "go") - 14 / 30]
    ours = [t + 38 / 30 for t in launch]
    cl = [w("b7", "m") - 6 / 30, w("b7", "m"), w("b7", "server") + 4 / 30, w("b7", "server") + 10 / 30, w("b7", "itself") - 4 / 30,
          w("b7", "eight") - 8 / 30, w("b7", "eight") - 2 / 30, w("b7", "request") - 8 / 30]
    return ours, [t + 31 / 30 for t in cl]


COLS = {"ok": (30, 142, 90), "none": (138, 151, 171), "slip": (196, 81, 31), "write": (60, 144, 255)}


def status(i, tool, a, r, ours=True):
    if ours and i == 7:
        return "slip"
    if tool == "create_purchase_request" and a.get("confirm"):
        return "write"
    if tool == "search_policy" and not r.get("answer_in_documents"):
        return "none"
    return "ok"


def _panel(cv, t, x0, y0, title, sub, rows, a, accent, width=820):
    """rows: [(t_show, kind, text, colour)] kind = call | turn."""
    import overlay as O
    from PIL import Image, ImageDraw
    shown = [r for r in rows if t >= r[0]]
    if not shown:
        return
    lh = 25
    H = 70 + sum(lh - 4 if r[1] == "res" else lh for r in rows) + 16
    lay = Image.new("RGBA", (width, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, width - 1, H - 1), 16, fill=(12, 16, 25, 226), outline=(255, 255, 255, 30))
    d.rounded_rectangle((10, 16, 14, H - 16), 2, fill=O.col(accent))
    d.text((30, 14), title, font=O.font(22, 600), fill=O.col("ink"))
    d.text((30, 42), sub, font=O.font(16, 400), fill=O.col("slate"))
    fm = O.font(15, 500, True)
    fs = O.font(16, 500)
    y = 70
    n = 0
    for (ts, kind, text, c) in rows:
        if t < ts:
            break
        fade = min(1.0, (t - ts) / 0.3)
        al = int(255 * fade)
        if kind == "turn":
            d.text((30, y + 2), text, font=fs, fill=(150, 190, 255, al))
        elif kind == "res":
            d.text((76, y - 3), text, font=fm, fill=(c[0] // 2 + 100, c[1] // 2 + 100, c[2] // 2 + 100, al))
            y += lh - 4
            continue
        else:
            n += 1
            d.rounded_rectangle((30, y + 4, 38, y + 16), 2, fill=(c[0], c[1], c[2], al))
            d.text((48, y), f"{n:>2}", font=fm, fill=(164, 176, 196, al))
            d.text((76, y), text, font=fm, fill=(236, 240, 248, al))
        y += lh
    lay = lay.crop((0, 0, width, min(H, y + 16)))
    if a < 0.999:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    cv.alpha_composite(lay, (int(x0), int(y0)))


def _fmt_call(tool, a, r, width=86):
    s = f"{tool}({short_args(tool, a)})  →  {summary(tool, a, r)}"
    return s if len(s) <= width else s[:width - 1] + "…"


def draw(cv, t, fr, P):
    import overlay as O
    tl = _S.get("tl")
    if tl is None:
        return
    blk = {b["id"]: b for b in tl["blocks"]}
    w = _w(tl)
    ours_t, cl_t = sched(tl)
    # our trace panel: b2 to the end of b5, then again (smaller) in b7 beside Claude's
    calls = our_calls()
    turns = OURS["turns"]
    rows = []
    for i, (tool, a, r) in enumerate(calls):
        if i == 9:
            rows.append((w("b5", "says") + 0.2, "turn", f"Emma:  “{turns[1]['user']}”", None))
        if i == 10:
            rows.append((w("b5", "yes") - 0.1, "turn", f"Emma:  “{turns[2]['user']}”", None))
        rows.append((ours_t[i], "call", shorten(f"{tool}({short_args(tool, a)})", 84), COLS[status(i, tool, a, r)]))
        rows.append((ours_t[i] + 0.25, "res", "→ " + shorten(summary(tool, a, r), 80), COLS[status(i, tool, a, r)]))
    t_on, t_off = blk["b2"]["at"] + 0.2, blk["b5"]["speech_end"] + 0.8
    a = O.env(t, t_on, t_off, 0.4, 0.4)
    if a > 0:
        _panel(cv, t, 56, 70, "Our harness  ·  the calls, in order", f"{OURS['model'].split(':')[-1]}  ·  the prompt with no codes  ·  16 tools exposed",
               rows, a, "sky", width=900)
    # b7: Claude's trace panel (right) and ours compact (left)
    t_on, t_off = blk["b7"]["at"] + 0.3, blk["b7"]["speech_end"] + 0.8
    a = O.env(t, t_on, t_off, 0.4, 0.4)
    if a > 0:
        cc = claude_calls()
        crow = []
        cturn = {0: blk["b7"]["at"] + 2.3, 4: w("b7", "orders") - 0.2, 7: w("b7", "same") - 0.4}
        ct = CL["turns"]
        k = 0
        for i, (tool, aa, r) in enumerate(cc):
            if i in cturn:
                crow.append((cturn[i], "turn", "Emma:  “" + shorten(ct[k], 56) + "”", None))
                k += 1
            crow.append((cl_t[i], "call", shorten(f"{tool}({short_args(tool, aa)})", 76), COLS[status(i, tool, aa, r, ours=False)]))
            crow.append((cl_t[i] + 0.2, "res", "→ " + shorten(summary(tool, aa, r), 72), COLS[status(i, tool, aa, r, ours=False)]))
        _panel(cv, t, 1920 - 56 - 800, 70, "Claude's harness  ·  the same three messages", f"Claude Code + our MCP server  ·  {CL['model'].split('/')[-1]}",
               crow, a, "ember", width=800)
        orow = [(t_on, "call", tool, COLS[status(i, tool, aa, r)]) for i, (tool, aa, r) in enumerate(calls)]
        _panel(cv, t, 56, 70, "Our harness", f"{OURS['model'].split('/')[-1]}  ·  {len(calls)} calls", orow, a, "sky", width=380)
    # b8: what we control, line by line
    t_on, t_off = w("b8", "in", 1) - 0.2, blk["b8"]["speech_end"] + 0.6
    a = O.env(t, t_on, t_off, 0.4, 0.4)
    if a > 0:
        rows = [(w("b8", word, nth), "call", text, COLS["write"]) for word, nth, text in OUR_CONTROL]
        _panel(cv, t, 1920 - 56 - 760, 70, "On our harness, we set", "logs: our_harness.json (harness, model, prompt), claude_harness.json (comparison)",
               rows, a, "sky", width=760)


def elements(tl):
    w = _w(tl)
    _S["tl"] = tl
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = [{"type": "title", "kicker": KICK, "title": "Many tools, one request", "t0": 0.3, "t1": st("b1") + 0.4, "size": 76}]
    U1 = OURS["turns"][0]["user"]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b1", "emma's") - 0.1, "t1": w("b1", "sixteen") - 0.2, "accent": "sky",
              "lines": [{"text": "Emma Clarke  ·  purchase executive", "size": 22, "c": "slate"},
                        {"text": U1[:U1.rindex(" ", 0, 50)], "size": 30, "wt": 600},
                        {"text": U1[U1.rindex(" ", 0, 50):].strip(), "size": 30, "wt": 600}]})
    names = OURS["tools_exposed"]
    half = (len(names) + 1) // 2
    E.append({"type": "code", "x": 1824, "y": 84, "anchor": "tr", "t0": w("b1", "sixteen") - 0.1, "t1": en("b1") + 0.4, "size": 17, "lang": "text",
              "title": f"{len(names)} tools on the shelf", "sub": "the tools our harness exposes to the model", "accent": "sky",
              "lines": [f"{a:<26}{b}" for a, b in zip(names[:half], names[half:] + [""])]})
    E.append({"type": "pin", "anchor": "model_pin_top", "text": "the model picks every next call", "accent": "sky",
              "t0": w("b2", "model") - 0.1, "t1": w("b2", "three") + 0.8, "dx": 70, "dy": -50, "size": 26})
    # b4: the slip, and why it did no harm
    calls = our_calls()
    tool, a7, r7 = calls[7]
    err = OURS["observed_model_errors"][0]["error"]
    E.append({"type": "code", "x": 1824, "y": 84, "anchor": "tr", "t0": w("b4", "made") - 0.1, "t1": w("b4", "checks") - 0.3, "size": 18,
              "title": "call 8  ·  create_purchase_request", "sub": "logged as a model error: " + err[:60] + "…", "accent": "ember",
              "lines": ["{" + ", ".join(f"{j(k)}: {j(v)}" for k, v in list(a7.items())[:3]) + ",",
                        " " + ", ".join(f"{j(k)}: {j(v)}" for k, v in list(a7.items())[3:]) + "}",
                        "→ " + j({"note": r7["note"]})],
              "hl": [{"i0": 0, "i1": 1, "t0": w("b4", "made"), "t1": w("b4", "preview") - 0.1, "c": "ember"},
                     {"i0": 2, "i1": 2, "t0": w("b4", "preview"), "t1": w("b4", "checks") - 0.3, "c": "green"}]})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b4", "asks") - 0.1, "t1": en("b4") + 0.6, "accent": "sky",
              "lines": [{"text": "the reply asks Emma", "size": 22, "c": "slate"},
                        {"text": "“" + OURS["turns"][0]["reply"].split("?")[0].split(". ")[-1] + "?”", "size": 26, "wt": 600}]})
    # b5: the write
    wr = [c for c in calls if c[0] == "create_purchase_request" and c[1].get("confirm")][-1][2]
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b5", "request", 1) - 0.1, "t1": en("b5") + 0.6, "accent": "sky",
              "lines": [{"text": wr["request_no"], "size": 40, "wt": 600, "mono": True},
                        {"text": f"{wr['status']}  ·  approver {wr['approver']}", "size": 22, "c": "ink"},
                        {"text": wr["next_step"].split(". ")[1] + ".", "size": 20, "c": "slate"}]})
    E.append({"type": "chip", "x": 1824, "y": 260, "anchor": "tr", "t0": w("b5", "eleven") - 0.1, "t1": en("b5") + 0.6, "accent": "sky",
              "lines": [{"text": f"{OURS['summary']['tool_calls']} tool calls  ·  {OURS['summary']['model_calls']} model calls", "size": 26, "wt": 600}]})
    # b6: the earlier run's refusal (real)
    po = next(c for t in EARLIER["turns"] for c in t["cards"] if c["tool"] == "create_purchase_order")
    E.append({"type": "code", "x": 1824, "y": 84, "anchor": "tr", "t0": w("b6", "earlier") - 0.1, "t1": en("b6") + 0.6, "size": 19,
              "title": "An earlier recorded run  ·  create_purchase_order", "sub": "our harness, the app's prompt (with codes)  ·  logs/our_harness.json, run order",
              "accent": "ember", "lines": ["{"] + [f"  {j(k)}: {j(v)}," for k, v in po["result"].items()][:-1] +
                                         [f"  {j(list(po['result'])[-1])}: {j(list(po['result'].values())[-1])}", "}"],
              "hl": [{"i0": 2, "i1": 2, "t0": w("b6", "refused"), "t1": w("b6", "its") - 0.1, "c": "ember"},
                     {"i0": 3, "i1": 3, "t0": w("b6", "its"), "t1": en("b6") + 0.6, "c": "green"}]})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b6", "both") - 0.1, "t1": w("b6", "refused") - 0.2, "accent": "ember",
              "lines": [{"text": "both harnesses, earlier runs", "size": 22, "c": "slate"},
                        {"text": "a direct order first", "size": 32, "wt": 600}]})
    # b7: counts
    E.append({"type": "chip", "x": 960, "y": 850, "anchor": "tc", "t0": w("b7", "eight") - 0.1, "t1": en("b7") + 0.6, "accent": "ember",
              "lines": [{"text": f"Claude's harness: {CL['tool_calls']} calls  ·  ours: {OURS['summary']['tool_calls']}  ·  both end at {wr['request_no']}",
                         "size": 26, "wt": 600}]})
    # b8: around the model
    E.append({"type": "chip", "x": 96, "y": 92, "t0": st("b8") - 0.1, "t1": w("b8", "around") - 0.2, "accent": "sky",
              "lines": [{"text": "who picks the next call?", "size": 22, "c": "slate"}, {"text": "the model, in both", "size": 34, "wt": 600}]})
    E.append({"type": "code", "x": 96, "y": 84, "t0": w("b8", "around") - 0.1, "t1": w("b8", "in", 1) - 0.3, "size": 19, "lang": "text",
              "title": "On Claude's harness, left to Claude", "sub": "experiments/logs/claude_harness.json  ·  comparison.left_to_claude",
              "accent": "ember", "lines": CMP["left_to_claude"]})
    so = OURS["summary"]
    E.append({"type": "chip", "x": 960, "y": 700, "anchor": "tc", "t0": w("b8", "token") - 0.1, "t1": en("b8") + 0.7, "accent": "sky",
              "lines": [{"text": f"ours: {so['tool_calls']} calls  ·  {so['tokens_in']:,} tokens in  ·  £{so['cost_gbp_est']:.3f} (estimated)",
                         "size": 25, "wt": 600},
                        {"text": f"Claude's: {CL['tool_calls']} calls  ·  {CL['tokens_in_total']:,} tokens in, mostly a cached read of its own prompt  ·  ${CL['cost_usd_reported']:.4f} (reported)",
                         "size": 19, "c": "slate"},
                        {"text": f"two different models ({OURS['model'].split('/')[-1]}, {CL['model'].split('/')[-1]}): this compares whole setups",
                         "size": 18, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b9") + 0.9, "kicker": KICK, "title": "Many tools, one request",
              "sub": "The model picks the next call; the harness decides what it can pick from",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Recorded: our harness (gemini-3.8-flash) and Claude Code (claude-sonnet-5.5) on our MCP server, 3 Nov 2026",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    ours_t, cl_t = sched(tl)
    S = [("bloom.mp3", 0.2, 0.5)]
    for b in ("b2", "b6", "b7", "b8", "b9"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.5, 0.22))
    for t in ours_t:
        S += [("beam.mp3", t - 1.25, 0.16), ("tile.mp3", t - 0.1, 0.4)]
    for t in cl_t:
        S.append(("tile.mp3", t - 0.1, 0.3))
    S += [("rise.mp3", w("b1", "sixteen"), 0.3), ("refuse.mp3", w("b4", "made"), 0.3), ("refuse.mp3", w("b6", "refused"), 0.45),
          ("chime.mp3", w("b5", "request", 1), 0.4), ("chime.mp3", w("b6", "did"), 0.3)]
    for word in ("model", "prompt", "tools", "battery-safety", "fourteen-round", "log"):
        S.append(("tick.mp3", w("b8", word, 1 if word == "model" else 0), 0.28))
    S.append(("resolve.mp3", blk["b9"]["speech_end"] + 0.6, 0.5))
    return S
