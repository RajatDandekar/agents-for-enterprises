"""2D overlays + SFX for s2, "What you send, cut into tokens".
Numbers: brain3d/trace.json (tokens, ids, roles, number_cuts), experiments/logs/bpe.json (the hand BPE run),
films/qkv_data.json vocab (151,643 BPE pieces + 22 special = 151,665; 151,936 rows = 1,187 x 128; 271 padding)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "kit"))
import s2_layout as S  # noqa: E402

L2 = os.path.dirname(os.path.dirname(HERE))
T = json.load(open(os.path.join(L2, "brain3d", "trace.json")))
V = json.load(open(os.path.join(L2, "films", "qkv_data.json")))["vocab"]
TOK = T["tokens"]
CUT = T["number_cuts"]["5,400"]
CNT = T["prompt"]["counts"]
POSTER = 72.0
MUSIC = "tried_and_true_imprismed.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 40.0
assert V["bpe_pieces"] + V["special_tokens"] == V["tokenizer_len"] and V["embedding_rows"] == 1187 * 128
assert V["embedding_rows"] - V["tokenizer_len"] == V["padding_rows"] == 271


def show(t):
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
    fps = 30.0
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 2", "title": "What you send, cut into tokens", "t0": 0.4, "t1": st("b1") + 3.4}]
    # b1: the bar, then its tokens with their ids
    E.append({"type": "pin", "anchor": "tok87_top", "text": T["prompt"]["question"], "sub": "Emma's question, as she typed it",
              "t0": st("b1") + 0.6, "t1": w("b1", "tokens") - 0.3, "dx": -60, "dy": -150, "size": 28})
    for k, i in enumerate(range(80, 95)):
        t0 = w("b1", "tokens") + 0.3 + k * 0.05
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": t0, "t1": en("b1") + 1.0,
                  "size": 22, "place": "tc", "dy": 8, "hl": "sky" if i == 92 else None, "maxdepth": 6})
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": str(TOK[i]["id"]), "t0": t0 + 0.3, "t1": en("b1") + 1.0,
                  "size": 17, "place": "tc", "dy": 44, "maxdepth": 6})
    # b2: the page and its three groups
    E.append({"type": "number", "x": 96, "y": 140, "value": "100 tiles", "label": "Emma's whole chat, as the model receives it",
              "t0": w("b2", "hundred"), "t1": en("b2") + 0.4, "size": 72})
    for anchor, word, n, sub, acc in (("tok40_top", "seventy-two", CNT["system"], "the app's instructions", "slate"),
                                      ("tok87_top", "fifteen", CNT["user"], "Emma's question", "sky"),
                                      ("tok98_top", "thirteen", CNT["template"], "chat markers: who is speaking", "v")):
        E.append({"type": "pin", "anchor": anchor, "text": f"{n} tokens", "sub": sub, "accent": acc, "t0": w("b2", word),
                  "t1": en("b2") + 0.4, "dx": 80, "dy": -90, "size": 30})
    # b3: macros
    for i in list(range(77, 97)):
        E.append({"type": "tag", "anchor": f"tok{i}_top", "text": show(TOK[i]["text"]), "t0": st("b3") - 0.2, "t1": w("b3", "northbridge") - 0.4,
                  "size": 22, "place": "c", "dy": 0, "maxdepth": 3.0, "hl": "sky" if i == 92 else None})
    for i in range(0, 13):
        E.append({"type": "tag", "anchor": f"tok{i}_top", "text": show(TOK[i]["text"]), "t0": w("b3", "northbridge") - 0.2, "t1": w("b3", "number", 1) - 0.4,
                  "size": 22, "place": "c", "dy": 0, "maxdepth": 3.0, "hl": "sky" if i in (6, 7) else None})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "common"), "t1": w("b3", "manchester") - 0.4, "accent": "sky",
              "lines": [{"text": "One common word, one token", "size": 30, "wt": 600}, {"text": "e-bike is three: e  -b  ike", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "tok92_top", "text": "Manchester", "sub": "one token  ·  id 19361", "t0": w("b3", "manchester"),
              "t1": w("b3", "northbridge") - 0.4, "dx": 90, "dy": -110, "size": 34})
    for i, dx in ((6, -100), (7, 100)):
        E.append({"type": "pin", "anchor": f"tok{i}_top", "text": show(TOK[i]["text"]), "sub": f"id {TOK[i]['id']}", "t0": w("b3", "north") if i == 6 else w("b3", "bridge"),
                  "t1": w("b3", "number", 1) - 0.4, "dx": dx, "dy": -100, "size": 32, "mono": True})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "northbridge"), "t1": w("b3", "number", 1) - 0.4, "accent": "sky",
              "lines": [{"text": "Northbridge = 2 tokens", "size": 30, "wt": 600}, {"text": "a rarer word is cut into known pieces", "size": 22, "c": "slate"}]})
    hits = [w("b3", "five", 2), w("b3", "comma"), w("b3", "four", 1), w("b3", "zero"), w("b3", "zero", 1)]
    for k, c in enumerate(CUT):
        E.append({"type": "face", "anchor": f"num{k}_front", "text": c["text"], "t0": hits[k] - 0.1, "t1": en("b3") + 0.5,
                  "tile_px": 150, "dy": -84, "max": 56, "c": "ink"})
        E.append({"type": "tag", "anchor": f"num{k}_front", "text": f"id {c['id']}", "t0": hits[k] + 0.2, "t1": en("b3") + 0.5,
                  "size": 18, "place": "tc", "dy": 56, "maxdepth": 6})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "number", 1), "t1": en("b3") + 0.5, "accent": "deep",
              "lines": [{"text": "5,400  =  5 tokens", "size": 34, "wt": 600, "mono": True},
                        {"text": "Qwen writes every digit as its own token", "size": 22, "c": "slate"}]})
    # b4: byte pair encoding, the real hand run
    life, mf, states = S.segment_life(int(round(w("b4", "merging") * fps)), int(round(w("b4", "merging") * fps)) + 150)
    for (wd, a, bb), L in life.items():
        t0 = (L["start"] / fps) if L["start"] else st("b4") + 0.9
        t1 = (L["end"] / fps - 0.02) if L["end"] else w("b4", "tokenizer") - 0.4
        E.append({"type": "tag", "anchor": f"bpe_{wd}_{a}_{bb}_front", "text": L["text"], "t0": t0, "t1": t1, "size": 24, "place": "tc",
                  "dy": 8, "mono": True, "fin": 0.0, "maxdepth": 5})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": st("b4") + 0.8, "t1": w("b4", "merging") - 0.1, "accent": "sky",
              "lines": [{"text": "Byte pair encoding, by hand", "size": 24, "c": "slate"},
                        {"text": f"a 12-word text: {S.BPE['start_vocab']} symbols, {states[0][2]} tokens", "size": 30, "wt": 600}]})
    _BPE_T.update({"mf": [m / fps for m in mf], "states": states, "end": w("b4", "tokenizer") - 0.4})
    E.append({"type": "pin", "anchor": "rack_pin_mid", "text": f"{V['bpe_pieces']:,} pieces", "sub": "Qwen's learned BPE vocabulary",
              "t0": w("b4", "forty-three"), "t1": en("b4") + 0.4, "dx": 90, "dy": -60, "size": 36})
    # b5: the vocabulary table
    E.append({"type": "pin", "anchor": "drawer_pin_special", "text": f"{V['special_tokens']} special tokens", "sub": "<|im_start|>  <|im_end|>  <|endoftext|>  …",
              "accent": "k", "t0": w("b5", "twenty-two"), "t1": w("b5", "rows") - 0.3, "dx": 120, "dy": -60, "size": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "get"), "t1": w("b5", "rows") - 0.3, "accent": "k",
              "lines": [{"text": f"{V['bpe_pieces']:,} + {V['special_tokens']} = {V['tokenizer_len']:,}", "size": 34, "wt": 600, "mono": True},
                        {"text": "every token the tokenizer can produce", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "rows"), "t1": w("b5", "no") - 0.3, "accent": "sky",
              "lines": [{"text": f"the model's table: {V['embedding_rows']:,} rows", "size": 32, "wt": 600},
                        {"text": f"{V['embedding_rows']:,} = 1,187 × 128", "size": 30, "wt": 600, "mono": True},
                        {"text": "a multiple of 128 suits the GPU", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "rack_pin_band", "text": "one band = 128 rows", "sub": "1,187 bands, top to bottom", "t0": w("b5", "eighty-seven"),
              "t1": w("b5", "no") - 0.3, "dx": 140, "dy": -120, "size": 30})
    E.append({"type": "pin", "anchor": "drawer_pin_pad", "text": f"{V['padding_rows']} padding rows", "sub": "no token ever uses them",
              "accent": "slate", "t0": w("b5", "no"), "t1": en("b5") + 0.4, "dx": 120, "dy": -40, "size": 32})
    E.append({"type": "pin", "anchor": "drawer_pin_special", "text": f"{V['special_tokens']} special", "accent": "k", "t0": w("b5", "no") + 0.3,
              "t1": en("b5") + 0.4, "dx": -120, "dy": -60, "size": 24})
    # b6
    E.append({"type": "number", "x": 960, "y": 330, "anchor": "tc", "value": "100 tokens in", "label": "what Emma's question costs, and all the model reads",
              "t0": w("b6", "hundred"), "t1": en("b6") + 0.5, "size": 92})
    E.append({"type": "end", "t0": en("b6") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "What you send, cut into tokens",
              "sub": "Qwen2.5-0.5B-Instruct's tokenizer on Emma's chat",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Tokens: brain3d/trace.json  ·  BPE: experiments/logs/bpe.json  ·  sizes: tokenizer and config",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Tried-And-True”, Imprismed (Epidemic Sound)"]})
    return E


_BPE_T = {}


def draw(cv, t, fr, P):
    """The merge counter during the BPE shot: one card that updates in place at each merge."""
    if not _BPE_T or not (_BPE_T["mf"][0] <= t <= _BPE_T["end"] + 0.3):
        return
    import overlay as O
    mf, states = _BPE_T["mf"], _BPE_T["states"]
    k = max(i for i in range(len(mf)) if mf[i] <= t) + 1
    step, pair, ntok, _ = states[k]
    cnt = S.BPE["steps"][k - 1]["count"]
    a = O.env(t, mf[0], _BPE_T["end"], 0.2, 0.3)
    spr = O.card([(f"merge {step}:  {pair[0]} + {pair[1]}   (seen {cnt} times)", 30, 600, "ink", True),
                  (f"the text is now {ntok} tokens", 24, 400, "slate", False)], accent="sky", pad=(26, 18))
    O.put(cv, spr, 96, 130, a)


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S_ = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6"):
        S_.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.35))
    S_ += [("beam.mp3", w("b1", "tokens") - 0.3, 0.4)]
    for k in range(6):
        S_.append(("tile.mp3", w("b2", "cut") + k * 0.35, 0.25))
    S_ += [("chime.mp3", w("b3", "manchester"), 0.3), ("tile.mp3", w("b3", "north"), 0.4), ("tile.mp3", w("b3", "bridge"), 0.4)]
    for word, nth in (("five", 2), ("comma", 0), ("four", 1), ("zero", 0), ("zero", 1)):
        S_.append(("tick.mp3", w("b3", word, nth), 0.32))
    m0 = w("b4", "merging")
    for k in range(10):
        S_.append(("tile.mp3", m0 + k * 0.5 + 0.25, 0.3))
    S_ += [("rise.mp3", w("b5", "add"), 0.35), ("chime.mp3", w("b5", "twenty-two"), 0.3), ("beam.mp3", w("b5", "eighty-seven"), 0.35),
           ("resolve.mp3", blk["b6"]["speech_end"] + 0.6, 0.45)]
    return S_
