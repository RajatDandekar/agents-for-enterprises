"""2D overlays + SFX for the finale, "The whole machine" (Lecture 2 recap).
Numbers from brain3d/trace.json and films/qkv_data.json."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILMS = os.path.dirname(HERE)
T = json.load(open(os.path.join(os.path.dirname(FILMS), "brain3d", "trace.json")))
D = json.load(open(os.path.join(FILMS, "qkv_data.json")))
TOK = T["tokens"]
G = T["generation"]["greedy"]
F = T["facts"]
FG = F["greedy"]
TOP6 = T["final"]["last"]["1.0"][:6]
LENS = T["logit_lens"]["last"]
W = D["qkv"]["weights"]
EMB92 = D["vectors"]["embedding"]["92"]
POSTER = 66.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34
MUSIC_OFFSET = 0.0


def show(t):
    if t == " ":
        return "(space)"
    s = t.replace("\n", "\\n")
    return s.strip() if s.strip() else s


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    cnt = T["prompt"]["counts"]
    E = [{"type": "title", "kicker": "Lecture 2  ·  Recap", "title": "The whole machine", "t0": 0.4, "t1": st("b1") + 3.0, "size": 72}]
    for i in range(76, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": st("b1") + 1.0 + max(0, i - 80) * 0.25,
                  "t1": en("b4") + 0.3, "size": 24 if i in (86, 92, 99) else 20, "hl": "sky" if i in (92, 99) else None,
                  "place": "tc", "dy": 10, "maxdepth": 3.2})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "one"), "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": f"{T['prompt']['n_tokens']} tokens", "size": 34, "wt": 600},
                        {"text": f"{cnt['system']} instructions · {cnt['user']} question · {cnt['template']} chat markers", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "tok92_top", "text": "Manchester", "sub": f"one token, number {TOK[92]['id']}", "accent": "sky",
              "t0": w("b2", "manchester"), "t1": en("b2") + 0.3, "dx": 50, "dy": -120, "size": 30})
    v4 = ", ".join(f"{x:.4f}" for x in EMB92[:3])
    E.append({"type": "pin", "anchor": "vec92_top", "text": "896 numbers", "sub": f"Manchester's vector: {v4}, …", "accent": "sky",
              "t0": w("b3", "column"), "t1": en("b3") + 0.4, "dx": 60, "dy": -70, "size": 30})
    E.append({"type": "pin", "anchor": "qprobe_top", "text": "Query", "sub": "the last position: what am I looking for?", "accent": "q",
              "t0": w("b4", "query"), "t1": w("b4", "sixty-five") - 1.2, "dx": -60, "dy": -80, "size": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "key"), "t1": w("b4", "sixty-five") - 0.3, "accent": "k",
              "lines": [{"text": "query · key, for every position", "size": 30, "wt": 600, "mono": True},
                        {"text": "softmax turns the scores into weights", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "m92_top", "text": f"{W[92] * 100:.1f}%", "sub": "on Manchester · block 24, head 2", "accent": "sky",
              "t0": w("b4", "sixty-five"), "t1": en("b4") + 0.3, "dx": 60, "dy": -90, "mono": True, "size": 40})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "block"), "t1": en("b5") + 0.3, "accent": "sky",
              "lines": [{"text": "attention + MLP = one block", "size": 30, "wt": 600},
                        {"text": "24 blocks, read in one pass", "size": 24, "c": "slate"}]})
    for k, word in ((22, "near"), (23, "top"), (24, "form")):
        r = LENS[k - 1]
        E.append({"type": "pin", "anchor": f"lens{k}", "text": f"block {k}:  {r['top'][0]['text']}  {r['top'][0]['p'] * 100:.1f}%",
                  "sub": "logit lens" if k == 22 else None, "accent": "sky" if k == 24 else "slate", "t0": w("b5", word),
                  "t1": en("b5") + 0.4, "dx": -260, "dy": {22: 40, 23: -10, 24: -60}[k], "mono": True, "size": 26})
    for e in E:
        if e.get("sub") is None:
            e.pop("sub", None)
    E.append({"type": "pin", "anchor": "vocab_pin", "text": f"{T['meta']['vocab']:,} tokens", "sub": "one score for each", "accent": "sky",
              "t0": w("b6", "scored"), "t1": w("b6", "softmax") + 1.0, "dx": 50, "dy": -60, "size": 30, "mono": True})
    bar_t = {0: w("b6", "we"), 1: w("b6", "as"), 2: w("b6", "manchester")}
    for n, row in enumerate(TOP6):
        E.append({"type": "pin", "anchor": f"bar{n}_top", "text": f"{show(row['text'])} {row['p'] * 100:.1f}%",
                  "t0": bar_t.get(n, w("b6", "manchester") + 0.6), "t1": en("b6") + 0.4, "dx": 26 if n % 2 == 0 else -26,
                  "dy": -60 - 50 * (n % 2), "mono": True, "size": 26 if n else 32, "accent": "sky" if n == 0 else "slate"})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "chosen"), "t1": en("b7") + 0.3, "accent": "sky",
              "lines": [{"text": "1 token chosen: We", "size": 32, "wt": 600, "mono": True},
                        {"text": "then the whole pass runs again, for the next token", "size": 24, "c": "slate"}]})
    for j in range(7):
        E.append({"type": "tag", "anchor": f"gen{j}_front", "text": show(G[j]["text"]), "t0": w("b7", "joins") if j == 0 else (
            w("b7", "again") + 0.3 * (j - 1) if j < 4 else w("b8", {4: "one", 5: "zero", 6: "zero"}[j], 1 if j == 6 else 0) + 0.2),
                  "t1": w("b9", "put") - 0.4, "size": 24, "hl": "ember" if j >= 4 else None, "place": "tc", "dy": 10, "maxdepth": 4.0})
    d0 = G[4]
    E.append({"type": "pin", "anchor": "gen4_top", "text": f"1  {d0['p'] * 100:.1f}%",
              "sub": "then " + " · ".join(f"{a['text']} {a['p'] * 100:.1f}%" for a in d0["alts"][1:3]), "accent": "ember",
              "t0": w("b8", "one") + 0.3, "t1": w("b8", "confident") - 0.2, "dx": 40, "dy": -120, "mono": True, "size": 32})
    E.append({"type": "pin", "anchor": "gen6_top", "text": "100", "sub": "confident, and invented", "accent": "ember",
              "t0": w("b8", "confident"), "t1": w("b9", "put") - 0.4, "dx": 40, "dy": -130, "mono": True, "size": 40})
    E.append({"type": "pin", "anchor": "plaque_top", "text": f"Ledgerline: {F['truth']:,}", "sub": "BAT-500 on hand, Manchester main stores",
              "accent": "green", "t0": w("b8", "ledgerline"), "t1": w("b9", "put") - 0.2, "dx": 60, "dy": -80, "size": 32})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b9", "nothing"), "t1": w("b9", "put") - 0.3, "accent": "ember",
              "lines": [{"text": "No stock figure in the prompt", "size": 30, "wt": 600},
                        {"text": "so the model wrote a plausible number", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "plaque_top", "text": "+ one line in the prompt", "sub": f"“{F['line']}”  ({len(F['fact_positions'])} tokens)",
              "accent": "green", "t0": w("b9", "prompt", 1) + 0.2, "t1": w("b9", "same") + 0.1, "dx": 60, "dy": -90, "size": 30})
    for j in range(8):
        dig = FG[j]["text"].strip().isdigit() or FG[j]["text"] == ","
        E.append({"type": "tag", "anchor": f"new{j}_front", "text": show(FG[j]["text"]),
                  "t0": (w("b9", "same") + 0.1 * j) if j < 3 else (w("b9", "five") + 0.13 * (j - 3)), "t1": en("b9") + 0.6, "size": 24,
                  "hl": "green" if dig else None, "place": "tc", "dy": 10, "maxdepth": 4.0})
    E.append({"type": "pin", "anchor": "new7_top", "text": f"{F['truth']:,}", "sub": f"the same model, with the fact: 5 at {F['digits'][0]['p'] * 100:.1f}%",
              "accent": "green", "t0": w("b9", "hundred") + 0.2, "t1": w("b9", "where") - 0.2, "dx": 40, "dy": -130, "mono": True, "size": 40})
    E.append({"type": "end", "t0": en("b9") + 1.0, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "The whole machine",
              "sub": "Next: Lecture 3, Knowledge  ·  Lecture 4, Tools",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Every number is from one recorded run of Qwen2.5-0.5B-Instruct (trace.json, qkv_data.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.5)]
    S += [("tick.mp3", w("b2", "tokens"), 0.3), ("rise.mp3", w("b3", "vector") - 0.2, 0.4), ("beam.mp3", w("b4", "query"), 0.4),
          ("rise.mp3", w("b4", "key") - 0.2, 0.3), ("fill.mp3", w("b4", "sixty-five") - 0.2, 0.4), ("beam.mp3", w("b5", "climbs"), 0.45),
          ("chime.mp3", w("b5", "form"), 0.3), ("beam.mp3", w("b6", "scored"), 0.35), ("fill.mp3", w("b6", "softmax") + 0.4, 0.35),
          ("chime.mp3", w("b6", "we"), 0.35), ("whoosh.mp3", w("b7", "chosen"), 0.35), ("tile.mp3", w("b7", "joins"), 0.45),
          ("beam.mp3", w("b7", "pass"), 0.3), ("tile.mp3", w("b8", "one"), 0.4), ("tile.mp3", w("b8", "zero"), 0.35),
          ("tile.mp3", w("b8", "zero", 1), 0.35), ("chime.mp3", w("b8", "ledgerline"), 0.35), ("whoosh.mp3", w("b9", "put") + 0.6, 0.4),
          ("tile.mp3", w("b9", "prompt", 1) + 0.4, 0.45), ("tile.mp3", w("b9", "five"), 0.45),
          ("resolve.mp3", blk["b9"]["speech_end"] + 0.8, 0.5)]
    return S
