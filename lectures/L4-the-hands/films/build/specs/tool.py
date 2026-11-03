"""2D overlays + SFX for film 1, "Inside a tool". Every JSON line and number is read from
experiments/logs/anatomy_check_stock.json at build time (nothing typed in by hand)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L4 = os.path.dirname(os.path.dirname(HERE))
A = json.load(open(os.path.join(L4, "experiments", "logs", "anatomy_check_stock.json")))
POSTER = 104.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_OFFSET = 0.0
KICK = "Agentic Systems Engineering  ·  Lecture 4"


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


def pretty(o, indent=2):
    return json.dumps(o, indent=indent, ensure_ascii=False).split("\n")


def env_lines(reply, data_keys_per_line=3):
    """A legacy envelope as compact lines: the envelope fields on one line, then data a few keys per line."""
    head = ", ".join(f"{j(k)}: {j(reply[k])}" for k in ("rc", "err_cd", "msg"))
    if reply["data"] is None:
        return ["{" + head + ",", ' "data": null}']
    items = list(reply["data"].items())
    rows = []
    for i in range(0, len(items), data_keys_per_line):
        rows.append(", ".join(f"{j(k)}: {j(v)}" for k, v in items[i:i + data_keys_per_line]))
    out = ["{" + head + ","]
    for i, r in enumerate(rows):
        pre = ' "data": {' if i == 0 else "          "
        out.append(pre + r + ("," if i < len(rows) - 1 else "}}"))
    return out


def code_lines(src, first, last, cut=78):
    out = []
    for l in src.split("\n")[first:last + 1]:
        out.append(l if len(l) <= cut else l[:cut - 1].rstrip() + " …")
    return out


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = [{"type": "title", "kicker": KICK, "title": "Inside a tool", "t0": 0.3, "t1": st("b1") + 0.4, "size": 76}]
    # ---- b1: Emma's question (her presence: the chat bubble)
    q = A["model_request"]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b1", "emma") - 0.1, "t1": w("b1", "writes") - 0.2, "accent": "sky",
              "lines": [{"text": "Emma Clarke  ·  purchase executive", "size": 22, "c": "slate"},
                        {"text": "How many BAT-500 battery packs do we have", "size": 32, "wt": 600},
                        {"text": "in Manchester main stores?", "size": 32, "wt": 600}]})
    E.append({"type": "pin", "anchor": "model_pin_top", "text": "the model", "sub": "it can only write text", "accent": "sky",
              "t0": w("b1", "model") - 0.1, "t1": en("b1") + 0.3, "dx": 70, "dy": -60})
    # ---- b2: the tool call (real, recorded)
    call = q["assistant_tool_call"]
    E.append({"type": "code", "anchor_pin": "cap1_top", "dx": 70, "dy": -150, "t0": w("b2", "request") - 0.1, "t1": st("b3") + 1.2,
              "title": "The request: a tool call", "sub": f"written by the model ({q['model'].split('/')[-1]}), recorded",
              "lines": ["{", f'  "name": {j(call["name"])},', f'  "arguments": {j(call["arguments"])}', "}"], "size": 26,
              "hl": [{"i0": 1, "i1": 1, "t0": w("b2", "name"), "t1": w("b2", "argument") - 0.1},
                     {"i0": 2, "i1": 2, "t0": w("b2", "argument"), "t1": en("b2")}]})
    # ---- b3: tool.json at the door
    sch = A["checked_at_the_door"]["against"]
    sl = ['"input_schema": {'] + json.dumps(sch, indent=2).replace('[\n    "item_code"\n  ]', '["item_code"]').split("\n")[1:-1] + ["}"]
    i_type = next(i for i, x in enumerate(sl) if '"type": "string"' in x)
    i_req = next(i for i, x in enumerate(sl) if '"required"' in x)
    E.append({"type": "code", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b3", "meets") - 0.1, "t1": w("b3", "what") - 0.3,
              "title": "tool.json", "sub": "the contract: the input schema", "lines": sl, "size": 21,
              "hl": [{"i0": i_type, "i1": i_type, "t0": w("b3", "string"), "t1": w("b3", "this") + 0.2},
                     {"i0": i_req, "i1": i_req, "t0": w("b3", "required"), "t1": w("b3", "this") + 0.2},
                     {"i0": i_type - 1, "i1": i_type, "t0": w("b3", "passes") - 0.2, "t1": w("b3", "what") - 0.3, "c": "green"}]})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b3", "passes") - 0.1, "t1": w("b3", "what") - 0.3, "accent": "green",
              "lines": [{"text": "accepted", "size": 34, "wt": 600}, {"text": "item_code is a string, and it is there", "size": 22, "c": "slate"}]})
    wt = A["error_path_wrong_type"]
    E.append({"type": "code", "anchor_pin": "cap2_top", "dx": 60, "dy": -170, "t0": w("b3", "number") - 0.1, "t1": w("b3", "refuses") + 0.8,
              "title": "What if the model sent this?", "accent": "ember", "size": 24,
              "lines": ["{", f'  "name": {j(wt["model_request"]["name"])},', f'  "arguments": {j(wt["model_request"]["arguments"])}', "}"],
              "hl": [{"i0": 2, "i1": 2, "t0": w("b3", "five"), "t1": w("b3", "refuses") + 0.8, "c": "ember"}]})
    E.append({"type": "code", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b3", "refuses") + 0.2, "t1": en("b3") + 0.6,
              "title": "Refused at the door", "sub": "the tool's result, before any code runs", "accent": "ember", "size": 22,
              "lines": pretty(wt["tool_result"]),
              "hl": [{"i0": 2, "i1": 2, "t0": w("b3", "item", 1), "t1": w("b3", "zero") - 0.1, "c": "ember"}]})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b3", "zero") - 0.05, "t1": en("b3") + 0.6, "accent": "ember",
              "lines": [{"text": f"{wt['ledgerline_calls']}", "size": 64, "wt": 600, "mono": True},
                        {"text": "calls reach Ledgerline", "size": 24, "c": "slate"}]})
    # ---- b4: tool.py, the services
    src = A["files"]["tool.py"]
    cl = code_lines(src, 6, 25)
    rel = lambda i: i - 6  # noqa: E731
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b4", "tool") - 0.1, "t1": en("b4") - 1.2, "lang": "py", "size": 17,
              "title": "tool.py", "sub": f"{A['files']['path']}/tool.py  ·  lines 7–26 of {len(src.rstrip(chr(10)).split(chr(10)))} (long lines cut)",
              "lines": cl, "type_on": 0.07, "accent": "sky",
              "hl": [{"i0": rel(6), "i1": rel(6), "t0": w("b4", "running") - 0.1, "t1": w("b4", "it") - 0.1},
                     {"i0": rel(8), "i1": rel(8), "t0": w("b4", "item"), "t1": w("b4", "warehouse") - 0.1},
                     {"i0": rel(10), "i1": rel(10), "t0": w("b4", "warehouse"), "t1": w("b4", "stock") - 0.1},
                     {"i0": rel(12), "i1": rel(12), "t0": w("b4", "stock"), "t1": en("b4")}]})
    svc = {s["name"]: s for s in A["services"]}
    # the four calls, labelled at the four service ports on the tool's back wall (where each conduit leaves)
    for jj, (nm, word, extra) in enumerate((("itm_get", "item", ""), ("whs_list", "warehouse", ""), ("stk_query", "manchester", " · WH-MAN-STR"),
                                           ("stk_query", "leeds", " · WH-LDS-STR"))):
        E.append({"type": "tag", "anchor": f"tool_port{jj}", "text": nm + extra, "t0": w("b4", word) - 0.05, "t1": en("b4") + 0.3,
                  "size": 20, "hl": "ember", "mono": True, "dy": -26 - (44 if jj % 2 else 0), "maxdepth": 6.0})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b4", "running") - 0.1, "t1": w("b4", "it") + 1.5, "accent": "sky",
              "lines": [{"text": "runs in Emma's own Ledgerline session", "size": 26, "wt": 600},
                        {"text": "her permissions, nobody else's", "size": 21, "c": "slate"}]})
    # ---- b5: the legacy envelopes (real replies)
    calls = A["legacy_calls"]
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b5", "envelopes") - 0.1, "t1": w("b5", "manchester") - 0.2, "accent": "ember", "size": 19,
              "title": f"{calls[0]['service']}  ·  reply 1 of {len(calls)}", "sub": "the legacy envelope: {rc, err_cd, msg, data}",
              "lines": env_lines(calls[0]["reply"], 2),
              "hl": [{"i0": 0, "i1": 0, "t0": w("b5", "r"), "t1": w("b5", "an") - 0.1, "c": "ember"},
                     {"i0": 1, "i1": 4, "t0": w("b5", "data"), "t1": w("b5", "manchester") - 0.2, "c": "ember"}]})
    man = calls[2]
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b5", "manchester") - 0.05, "t1": en("b5") + 0.5, "accent": "ember", "size": 19,
              "title": f"{man['service']} ({man['request']['whs_cd']})  ·  reply 3 of {len(calls)}",
              "lines": env_lines(man["reply"]),
              "hl": [{"i0": 2, "i1": 2, "t0": w("b5", "manchester") + 0.2, "t1": en("b5") + 0.5, "c": "ember"}]})
    lds = calls[3]
    E.append({"type": "code", "x": 64, "y": 420, "t0": w("b5", "leeds") - 0.05, "t1": en("b5") + 0.5, "accent": "ember", "size": 19,
              "title": f"{lds['service']} ({lds['request']['whs_cd']})  ·  reply 4 of {len(calls)}",
              "lines": [f'... "on_hand": {lds["reply"]["data"]["on_hand"]}, "allocated": {lds["reply"]["data"]["allocated"]}, ...'],
              "hl": [{"i0": 0, "i1": 0, "t0": w("b5", "leeds") + 0.2, "t1": en("b5") + 0.5, "c": "ember"}]})
    # ---- b6: the clean result
    R = A["tool_result"]
    rl = ["{"]
    for k, v in R.items():
        if k == "warehouses":
            rl.append('  "warehouses": [')
            for i, wh in enumerate(v):
                items = list(wh.items())
                rl.append("    {" + ", ".join(f"{j(a)}: {j(b)}" for a, b in items[:2]) + ",")
                rl.append("     " + ", ".join(f"{j(a)}: {j(b)}" for a, b in items[2:]) + ("}," if i < len(v) - 1 else "}"))
            rl.append("  ],")
        else:
            rl.append(f"  {j(k)}: {j(v)},")
    rl[-1] = rl[-1].rstrip(",")
    rl.append("}")
    i_wh = next(i for i, x in enumerate(rl) if '"warehouses"' in x)
    i_free = next(i for i, x in enumerate(rl) if '"free_total"' in x)
    i_cover = next(i for i, x in enumerate(rl) if '"cover_days"' in x)
    i_reord = next(i for i, x in enumerate(rl) if '"reorder_level"' in x)
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b6", "result") - 0.1, "t1": en("b6") + 0.4, "accent": "green", "size": 18,
              "title": "The tool's result", "sub": f"one clean, typed result  ·  {A['sizes']['tool_result_bytes']} bytes", "lines": rl,
              "hl": [{"i0": 1, "i1": 1, "t0": w("b6", "result"), "t1": w("b6", "each") - 0.1, "c": "green"},
                     {"i0": i_wh, "i1": i_wh + 5, "t0": w("b6", "each"), "t1": w("b6", "six") - 0.1, "c": "green"},
                     {"i0": i_free, "i1": i_free, "t0": w("b6", "six"), "t1": w("b6", "eleven") - 0.1, "c": "green"},
                     {"i0": i_cover, "i1": i_cover, "t0": w("b6", "eleven"), "t1": w("b6", "eight") - 0.1, "c": "green"}]})
    sz = A["sizes"]
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b6", "eight") - 0.05, "t1": en("b6") + 0.4, "accent": "green",
              "lines": [{"text": f"{sz['legacy_calls']} legacy replies  ·  {sz['legacy_replies_bytes']} bytes", "size": 26, "c": "slate"},
                        {"text": f"1 result  ·  {sz['tool_result_bytes']} bytes", "size": 34, "wt": 600}]})
    E.append({"type": "pin", "anchor": "res_top", "text": "back to the model", "sub": "the only thing it will see", "accent": "green",
              "t0": w("b6", "only") - 0.05, "t1": en("b6") + 0.3, "dx": 60, "dy": -80})
    # ---- b7: the error path
    ep = A["error_path"]
    E.append({"type": "code", "anchor_pin": "cap3_top", "dx": 60, "dy": -160, "t0": w("b7", "ask") - 0.1, "t1": w("b7", "item") - 0.2,
              "title": "A request for an item that does not exist", "size": 24,
              "lines": ["{", f'  "name": {j(ep["model_request"]["name"])},', f'  "arguments": {j(ep["model_request"]["arguments"])}', "}"]})
    lc = ep["legacy_calls"][0]
    E.append({"type": "code", "x": 1824, "y": 84, "anchor": "tr", "t0": w("b7", "item") - 0.05, "t1": w("b7", "turns") - 0.2, "accent": "ember", "size": 22,
              "title": f"{lc['service']}  ·  the legacy reply", "lines": env_lines(lc["reply"]),
              "hl": [{"i0": 0, "i1": 0, "t0": w("b7", "r"), "t1": w("b7", "turns") - 0.2, "c": "ember"}]})
    el = pretty(ep["tool_result"])
    i_next = next(i for i, x in enumerate(el) if '"next_step"' in x)
    E.append({"type": "code", "x": 1824, "y": 84, "anchor": "tr", "t0": w("b7", "turns") - 0.05, "t1": en("b7") + 0.6, "accent": "ember", "size": 21,
              "title": "The tool's result: a structured error", "sub": "ok: false, the error in words, the next step, the legacy code kept",
              "lines": el,
              "hl": [{"i0": 1, "i1": 1, "t0": w("b7", "ok"), "t1": w("b7", "error", 1) - 0.1, "c": "ember"},
                     {"i0": 2, "i1": 2, "t0": w("b7", "error", 1), "t1": w("b7", "next") - 0.1, "c": "ember"},
                     {"i0": i_next, "i1": i_next, "t0": w("b7", "next"), "t1": en("b7") + 0.6, "c": "green"}]})
    # ---- b8: the three parts, and the toolbox
    for txt, sub, pin, word, dx, dy in (("1  ·  tool.json", "the contract the request must meet", "tool_gate_top", "contract", -60, -120),
                                        ("2  ·  tool.py", "the code that talks to Ledgerline", "tool_core", "code", 60, -170),
                                        ("3  ·  the result", "clean, or a clear error", "tool_out", "clean", 60, -110)):
        E.append({"type": "pin", "anchor": pin, "text": txt, "sub": sub, "accent": "sky", "t0": w("b8", word) - 0.1,
                  "t1": w("b8", "open") + 1.4, "dx": dx, "dy": dy, "mono": False, "size": 28})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b8", "toolbox") - 0.1, "t1": en("b8") + 0.6, "accent": "sky",
              "lines": [{"text": "the toolbox: 16 tools", "size": 32, "wt": 600},
                        {"text": "each one a tool.json and a tool.py", "size": 22, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b8") + 0.9, "kicker": KICK, "title": "Inside a tool",
              "sub": "A contract, the code, one clean result",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Recorded: Emma's check_stock call (experiments/logs/anatomy_check_stock.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.2, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.5, 0.25))
    S += [("rise.mp3", w("b1", "writes") - 0.1, 0.35), ("tick.mp3", w("b2", "name"), 0.3), ("tick.mp3", w("b2", "argument"), 0.3),
          ("beam.mp3", w("b3", "schema") - 0.2, 0.3), ("chime.mp3", w("b3", "passes"), 0.4),
          ("refuse.mp3", w("b3", "refuses") + 0.05, 0.55), ("lid.mp3", w("b4", "behind") + 0.05, 0.5),
          ("fill.mp3", w("b4", "twenty-six") - 0.2, 0.3)]
    for word in ("item", "warehouse", "manchester", "leeds"):
        S.append(("beam.mp3", w("b4", word), 0.25))
        S.append(("relay.mp3", w("b4", word) + 0.5, 0.35))
    S += [("tile.mp3", w("b5", "envelopes") - 0.9 + 0.47 * k, 0.3) for k in range(4)]
    S += [("merge.mp3", w("b6", "turns"), 0.4), ("chime.mp3", w("b6", "result"), 0.35), ("whoosh.mp3", w("b6", "only"), 0.25),
          ("relay.mp3", w("b7", "item") + 0.4, 0.4), ("refuse.mp3", w("b7", "e") + 0.0, 0.35), ("tick.mp3", w("b7", "next"), 0.3),
          ("tick.mp3", w("b8", "contract"), 0.3), ("tick.mp3", w("b8", "code"), 0.3), ("tick.mp3", w("b8", "clean"), 0.3),
          ("rise.mp3", w("b8", "open"), 0.3), ("resolve.mp3", blk["b8"]["speech_end"] + 0.6, 0.5)]
    return S
