"""2D overlays + SFX for film 2, "What the model sees". Every number and message is read at build time from
experiments/logs/our_harness.json (runs single and order_hands) and build/data/l4_data.json (made from it)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L4 = os.path.dirname(os.path.dirname(HERE))
H = json.load(open(os.path.join(L4, "experiments", "logs", "our_harness.json")))
D = json.load(open(os.path.join(HERE, "data", "l4_data.json")))
CS, CO = D["context_single"], D["context_order"]
S1 = H["single"]
MSG = S1["steps"][1]["messages"]
POSTER = 92.0
MUSIC = "observatory_out_to_the_world.mp3"
KICK = "Agentic Systems Engineering  ·  Lecture 4"
NAMES = {"system": "system prompt", "defs": "tool definitions", "user": "Emma's message", "call": "tool call", "result": "tool result",
         "reply": "the reply"}
ACC = {"system": "slate", "defs": "k", "user": "sky", "call": "q", "result": "green", "reply": "sky"}
_S = {}
SIDE = ["r", "l", "r", "l", "r", "r"]     # system, defs, user, call, result, reply
DY = [0, 34, 34, -34, -10, -84]


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def wrap(s, n=66, sep=', "'):
    """Wrap a JSON line between fields (at `, "`), or prose between words (sep=" ")."""
    toks = s.split(sep)
    out, cur = [], ""
    for i, tok in enumerate(toks):
        piece = tok if i == 0 else (sep.lstrip(",").lstrip() if sep != " " else "") + tok
        if sep != " " and i > 0:
            piece = '"' + tok
        joiner = (", " if sep != " " else " ") if cur else ""
        if cur and len(cur) + len(joiner) + len(piece) > n:
            out.append(cur + ("," if sep != " " else ""))
            cur = (" " if sep != " " else "") + piece
        else:
            cur = cur + joiner + piece
    out.append(cur)
    return out


def cut(lines, n=70):
    return [l if len(l) <= n else l[:n - 1].rstrip() + " …" for l in lines]


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = [{"type": "title", "kicker": KICK, "title": "What the model sees", "t0": 0.3, "t1": st("b1") + 0.4, "size": 76}]
    _S["tl"] = tl
    # ---- b1
    E.append({"type": "pin", "anchor": "model_pin_top", "text": "the model", "sub": "it reads only its context window", "accent": "sky",
              "t0": w("b1", "model") - 0.1, "t1": w("b1", "does") - 0.2, "dx": 60, "dy": -60})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b1", "everything") - 0.1, "t1": w("b1", "does") + 0.3, "accent": "ember",
              "lines": [{"text": "the belief", "size": 22, "c": "slate"}, {"text": "it sees everything inside the tool", "size": 32, "wt": 600}]})
    E.append({"type": "pin", "anchor": "ctx_top", "text": "the context window", "sub": "everything the model reads, nothing else", "accent": "sky",
              "t0": w("b1", "context") - 0.1, "t1": en("b1") + 0.5, "dx": 60, "dy": -40})
    # ---- slab labels (right or left of each slab, alternating, with the real count)
    parts = CS["parts"] + [{"kind": "reply", "tokens": CS["completion_tokens"][-1]}]
    drop = [w("b2", "six"), w("b3", "hundred"), w("b4", "seventeen"), w("b4", "twenty-three"), w("b6", "two"), w("b7", "fifty-seven")]
    for k, (p, t0) in enumerate(zip(parts, drop)):
        side = SIDE[k]
        sub = {"defs": "2 tools: check_stock, find_item", "reply": "written by the model (tokens out)",
               "result": "only what the tool returned", "call": "written by the model", "user": "", "system": "who, when, how to work"}[p["kind"]]
        E.append({"type": "pin", "anchor": f"s{k}_{side}", "text": f"{NAMES[p['kind']]}  ·  {p['tokens']:,}", "sub": sub or None,
                  "accent": ACC[p["kind"]], "t0": t0 - 0.1, "t1": st("b8") - 0.4 if k < 5 else st("b8") - 0.4,
                  "dx": 70 if side == "r" else -70, "dy": DY[k], "size": 26, "subsize": 19})
    # ---- b2: the system prompt, as sent
    sp = MSG[0]["content"].split("\n")
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b2", "system") - 0.1, "t1": en("b2") + 0.5, "lang": "text", "size": 17,
              "title": "messages[0]  ·  role: system", "sub": f"the first lines of {CS['parts'][0]['tokens']} tokens", "accent": "slate",
              "lines": cut(sp[:8], 74)})
    # ---- b3: the tool definitions
    import re
    td = re.sub(r'\[\n\s+"item_code"\n\s+\]', '["item_code"]', json.dumps(S1["tool_definitions"][0], indent=2)).split("\n")
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b3", "tool") - 0.1, "t1": w("b3", "all") - 0.2, "size": 17,
              "title": "tools[0]  ·  one tool definition, as sent", "sub": "name, description, input schema", "accent": "k",
              "lines": cut(td, 76),
              "hl": [{"i0": 3, "i1": 3, "t0": w("b3", "name"), "t1": w("b3", "description") - 0.1, "c": "k"},
                     {"i0": 4, "i1": 4, "t0": w("b3", "description"), "t1": w("b3", "input") - 0.1, "c": "k"},
                     {"i0": 5, "i1": len(td) - 3, "t0": w("b3", "input"), "t1": w("b3", "all") - 0.2, "c": "k"}]})
    E.append({"type": "pin", "anchor": "ghost_r", "text": f"all 16 tools  ·  {CS['defs_16_tokens']:,}", "sub": "sent on every call", "accent": "k",
              "t0": w("b3", "all") + 0.6, "t1": en("b3") + 0.6, "dx": 70, "dy": -60, "size": 28})
    # ---- b4: Emma's message and the tool call, as they sit in the messages
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b4", "then") - 0.1, "t1": w("b4", "answers") - 0.2, "size": 19,
              "title": "messages[1]  ·  role: user", "accent": "sky", "lines": [json.dumps(MSG[1]["content"])]})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b4", "reads") - 0.1, "t1": w("b4", "answers") + 0.4, "accent": "sky",
              "lines": [{"text": f"call 1 reads {CS['prompt_tokens'][0]:,} tokens", "size": 32, "wt": 600},
                        {"text": f"{CS['parts'][0]['tokens']} + {CS['parts'][1]['tokens']} + {CS['parts'][2]['tokens']}", "size": 22, "c": "slate", "mono": True}]})
    tc = MSG[2]
    E.append({"type": "code", "x": 64, "y": 930, "anchor": "bl", "t0": w("b4", "answers") - 0.05, "t1": en("b4") + 0.5, "size": 18,
              "title": "messages[2]  ·  role: assistant (the model's tool call)", "accent": "q",
              "lines": ['{"role": "assistant", "content": null,', ' "tool_calls": [{"id": ' + json.dumps(tc["tool_calls"][0]["id"]) + ', "type": "function",',
                        '   "function": {"name": ' + json.dumps(tc["tool_calls"][0]["function"]["name"]) + ',',
                        '                "arguments": ' + json.dumps(tc["tool_calls"][0]["function"]["arguments"]) + '}}]}'],
              "hl": [{"i0": 2, "i1": 3, "t0": w("b4", "check"), "t1": en("b4") + 0.5, "c": "q"}]})
    # ---- b5: what stays behind the wall (the log's list)
    never = S1["what_never_enters_the_context"]
    E.append({"type": "pin", "anchor": "wall_slot", "text": "the wall", "sub": "only a tool's result comes back through the slot", "accent": "ink",
              "t0": w("b5", "wall") - 0.1, "t1": w("b5", "tool", 1) - 0.4, "dx": -80, "dy": -150})
    for txt, pin, word, dx, dy, nth in (("tool.py", "tool_core", "tool", -40, -170, 1), ("4 legacy services", "cab1_top", "four", 40, -40, 0),
                                   ("the database", "db_top", "database", 50, -90, 0), ("Emma's session", "badge_top", "session", -60, -120, 0),
                                   ("her password", "lock_top", "password", 60, -60, 0)):
        E.append({"type": "pin", "anchor": pin, "text": txt, "accent": "slate", "t0": w("b5", word, nth) - 0.05, "t1": w("b5", "none") + 1.6,
                  "dx": dx, "dy": dy, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b5", "none") - 0.05, "t1": en("b5") + 0.5, "accent": "ember",
              "lines": [{"text": "never enters the context", "size": 30, "wt": 600}] +
                       [{"text": x, "size": 21, "c": "slate"} for x in never]})
    # ---- b6: the tool message, only what the tool returned
    tm = MSG[3]["content"]
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b6", "json") - 0.1, "t1": en("b6") + 0.4, "size": 17,
              "title": "messages[3]  ·  role: tool", "sub": f"only what the tool returned  ·  {CS['parts'][4]['tokens']} tokens",
              "accent": "green", "lines": wrap(tm, 72),
              "hl": [{"i0": 1, "i1": 2, "t0": w("b6", "five"), "t1": en("b6") + 0.4, "c": "green"}]})
    # ---- b7: the second call
    E.append({"type": "chip", "x": 1824, "y": 740, "anchor": "tr", "t0": w("b7", "reads") - 0.1, "t1": en("b7") + 0.5, "accent": "sky",
              "lines": [{"text": f"call 2 reads {CS['prompt_tokens'][1]:,} tokens", "size": 32, "wt": 600},
                        {"text": f"and writes {CS['completion_tokens'][1]}", "size": 24, "c": "slate"}]})
    E.append({"type": "code", "x": 64, "y": 84, "t0": w("b7", "writes") - 0.05, "t1": en("b7") + 0.5, "size": 19, "lang": "text",
              "title": "the reply, to Emma", "accent": "sky", "lines": wrap(" ".join(S1["turns"][0]["reply"].split()), 64, sep=" ")})
    # ---- b8: the full order (the counts under each column come from the draw hook)
    sysp = CO["parts"][0]["tokens"]
    defs = CO["parts"][1]["tokens"]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b8", "now") - 0.1, "t1": w("b8", "one") - 0.2, "accent": "sky",
              "lines": [{"text": "Emma's full order  ·  16 tools", "size": 30, "wt": 600},
                        {"text": f"the prompt with no codes: {sysp} tokens  ·  tool definitions: {defs:,}", "size": 21, "c": "slate"}]})
    big = max(p["tokens"] for p in CO["parts"] if p["kind"] == "result")
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b8", "one") - 0.1, "t1": w("b8", "over") - 0.2, "accent": "green",
              "lines": [{"text": f"one policy search: {big} tokens", "size": 30, "wt": 600},
                        {"text": "in every call after it", "size": 21, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b8", "over") - 0.1, "t1": en("b8") + 0.6, "accent": "sky",
              "lines": [{"text": f"{CO['model_calls']} model calls  ·  {CO['steps'][0]['prompt_tokens']:,} to {CO['steps'][-1]['prompt_tokens']:,} tokens",
                         "size": 30, "wt": 600},
                        {"text": f"{CO['tokens_in']:,} tokens read in all", "size": 26, "c": "ink"}]})
    # ---- b9
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b9", "sees", 1) - 0.1, "t1": en("b9") + 0.6, "accent": "sky",
              "lines": [{"text": "what the model sees", "size": 22, "c": "slate"},
                        {"text": "the tools you expose", "size": 30, "wt": 600},
                        {"text": "the calls it makes", "size": 30, "wt": 600},
                        {"text": "what your tools return", "size": 30, "wt": 600}]})
    E.append({"type": "end", "t0": en("b9") + 0.9, "kicker": KICK, "title": "What the model sees",
              "sub": "The context window, filled with the real tokens",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Recorded: our harness, gemini-3.8-flash (experiments/logs/our_harness.json, runs single and order_hands)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def draw(cv, t, fr, P):
    """b8: under each column, its call number and the tokens that call read."""
    import overlay as O
    tl = _S.get("tl")
    if tl is None:
        return
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    t_every = w("b8", "every")
    t_end = blk["b9"]["at"] - 0.4
    if not (t_every - 0.5 <= t <= t_end + 0.5):
        return
    for k, s in enumerate(CO["steps"]):
        t0 = t_every + k * 44 / 30 + 0.5
        a = O.env(t, t0, t_end, 0.3, 0.3)
        if a <= 0:
            continue
        p = P.at(f"col{k}_pin", fr)
        if p is None:
            continue
        hl = k in (0, len(CO["steps"]) - 1) and t >= w("b8", "grows") - 0.1
        spr = O.text_sprite(f"{s['prompt_tokens']:,}", 24 if hl else 21, 600, "sky" if hl else "ink", mono=True)
        O.put(cv, spr, p[0], p[1] - 8, a, anchor="bc")
        lab = O.text_sprite(f"call {k + 1}", 17, 500, "slate")
        O.put(cv, lab, p[0], p[1] - 38, a, anchor="bc")


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.2, 0.5)]
    for b in ("b2", "b4", "b5", "b6", "b7", "b8", "b9"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.5, 0.22))
    for t in (w("b2", "system"), w("b3", "two"), w("b4", "seventeen"), w("b4", "answers"), w("b6", "two"), w("b7", "writes")):
        S.append(("tile.mp3", t + 0.6, 0.45))
    S += [("rise.mp3", w("b3", "all"), 0.35), ("fill.mp3", w("b4", "reads"), 0.3), ("fill.mp3", w("b7", "reads"), 0.3),
          ("beam.mp3", w("b5", "runs") + 0.3, 0.3), ("relay.mp3", w("b5", "four"), 0.3), ("refuse.mp3", w("b5", "none") + 0.1, 0.3),
          ("chime.mp3", w("b6", "comes") + 0.2, 0.35), ("tick.mp3", w("b8", "six"), 0.35)]
    for k in range(11):
        S.append(("tick.mp3", w("b8", "every") + k * 44 / 30 + 0.2, 0.18))
    S.append(("resolve.mp3", blk["b9"]["speech_end"] + 0.6, 0.5))
    return S
