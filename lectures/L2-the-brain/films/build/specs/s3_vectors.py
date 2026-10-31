"""2D overlays + SFX for s3, "Each token becomes a vector". Numbers: brain3d/trace.json (embeddings: values, pca,
neighbours) and films/qkv_data.json (vectors.embedding, the full 896 values of positions 80-99)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L2 = os.path.dirname(os.path.dirname(HERE))
T = json.load(open(os.path.join(L2, "brain3d", "trace.json")))
D = json.load(open(os.path.join(L2, "films", "qkv_data.json")))
TOK = T["tokens"]
PCA = T["embeddings"]["pca"]
NB = T["embeddings"]["neighbours"]
EMB = D["vectors"]["embedding"]
BATT, MAN = 86, 92
POSTER = 46.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 60.0
assert len(EMB[str(BATT)]) == 896 and EMB[str(BATT)][:4] == T["embeddings"]["values"][BATT]["v16"][:4]


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


def first(i, k=3):
    return ", ".join(f"{x:+.3f}" for x in EMB[str(i)][:k])


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 3", "title": "Each token becomes a vector", "t0": 0.4, "t1": st("b1") + 3.4}]
    for i in range(80, 100):
        for a, b in ((st("b1") + 0.4, w("b1", "row") - 0.6), (st("b2") - 0.2, w("b3", "squash") - 0.3), (st("b6") - 0.2, en("b6") + 0.4)):
            E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": a, "t1": b, "size": 22, "place": "tc",
                      "dy": 8, "hl": "sky" if i in (BATT, MAN) else None, "maxdepth": 3.2})
    E.append({"type": "pin", "anchor": "tok92_front", "text": "token 19361", "sub": "on its own, just a number", "t0": w("b1", "token"),
              "t1": w("b1", "row") - 0.5, "dx": 90, "dy": 60, "size": 30, "mono": True})
    E.append({"type": "pin", "anchor": "rack_pin_row", "text": "row 19361", "sub": "of the embedding table, 151,936 rows", "t0": w("b1", "row"),
              "t1": en("b1") + 0.4, "dx": 90, "dy": -40, "size": 30})
    # b2: the vectors
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "eight"), "t1": w("b2", "battery") - 0.3, "accent": "sky",
              "lines": [{"text": "One row = one vector", "size": 24, "c": "slate"}, {"text": "896 numbers per token", "size": 32, "wt": 600}]})
    E.append({"type": "pin", "anchor": "vec86_top", "text": "battery", "sub": f"896 numbers: {first(BATT)}, …", "t0": w("b2", "battery"),
              "t1": w("b2", "manchester") - 0.3, "dx": 80, "dy": -60, "size": 30})
    E.append({"type": "pin", "anchor": "vec92_top", "text": "Manchester", "sub": f"896 numbers: {first(MAN)}, …", "t0": w("b2", "manchester"),
              "t1": en("b2") + 0.4, "dx": 80, "dy": -60, "size": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "learned"), "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": "Learned in training", "size": 32, "wt": 600},
                        {"text": "151,936 rows × 896 = 136,134,656 numbers in this table", "size": 22, "c": "slate"}]})
    E.append({"type": "tag", "anchor": "vec40_top", "text": "first 16 of 896 shown", "t0": w("b2", "vector") + 1.0, "t1": w("b3", "squash") - 0.3,
              "size": 18, "place": "bc", "dy": -8, "maxdepth": 6})
    # b3: the map
    ex = PCA["explained"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "squash"), "t1": en("b3") + 0.4, "accent": "sky",
              "lines": [{"text": "896 dimensions squashed to 3", "size": 32, "wt": 600},
                        {"text": f"PCA on 46 reference words: {ex[0] * 100:.1f}%, {ex[1] * 100:.1f}%, {ex[2] * 100:.1f}% of the variance", "size": 22, "c": "slate"}]})
    # b4: clusters, words labelled
    grp_t = {"bike parts": (w("b4", "bike"), w("b4", "cities") - 0.2), "places": (w("b4", "cities"), w("b4", "days") - 0.2),
             "time": (w("b4", "days"), en("b4") + 0.5)}
    for wd in PCA["words"]:
        g = wd["group"]
        if g in grp_t:
            a, b = grp_t[g]
            E.append({"type": "tag", "anchor": f"pt_{wd['word']}", "text": wd["word"], "t0": a, "t1": b, "size": 20, "place": "bc",
                      "dy": -14, "mono": False, "maxdepth": 3.4})
    for g, word, nm in (("bike parts", "bike", "bike parts"), ("places", "cities", "places"), ("time", "days", "days and months")):
        a, b = grp_t[g]
        E.append({"type": "chip", "x": 96, "y": 130, "t0": a, "t1": b, "accent": {"bike parts": "sky", "places": "k", "time": "sky"}[g],
                  "lines": [{"text": nm, "size": 32, "wt": 600}, {"text": "used alike, so placed close together", "size": 22, "c": "slate"}]})
    # b5: neighbours by cosine
    for key, word, a, b in (("battery", "battery", w("b5", "ask"), w("b5", "nearest", 1) - 0.2), ("Manchester", "manchester", w("b5", "nearest", 1) - 0.1, en("b5") + 0.5)):
        E.append({"type": "tag", "anchor": f"pt_{key}_pin", "text": key, "t0": a, "t1": b, "size": 26, "place": "bc", "dy": -16, "hl": "sky", "mono": False})
        for k, it in enumerate(NB[key]["neighbours"][:6]):
            E.append({"type": "tag", "anchor": f"nb_{key}_{k}_pin", "text": f"{it['text'].strip()}  {it['cos']:.2f}", "t0": a + 0.6 + k * 0.17,
                      "t1": b, "size": 20, "place": "lc", "dx": 18, "dy": 0, "mono": False})
        E.append({"type": "chip", "x": 96, "y": 130, "t0": a, "t1": b, "accent": "sky",
                  "lines": [{"text": f"Nearest to {key}", "size": 32, "wt": 600},
                            {"text": "cosine similarity over every clean word in the vocabulary", "size": 22, "c": "slate"}]})
    # b6
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b6", "row"), "t1": en("b6") + 0.4, "accent": "sky",
              "lines": [{"text": "100 columns of 896 numbers", "size": 32, "wt": 600}, {"text": "each one a point in meaning", "size": 22, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b6") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "Each token becomes a vector",
              "sub": "Qwen2.5-0.5B-Instruct's input embeddings on Emma's question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Vectors, map and neighbours: brain3d/trace.json, films/qkv_data.json",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.35))
    S += [("beam.mp3", w("b1", "row") - 0.4, 0.4), ("rise.mp3", w("b1", "table"), 0.4), ("rise.mp3", w("b2", "vector"), 0.35),
          ("chime.mp3", w("b2", "battery"), 0.3), ("chime.mp3", w("b2", "manchester"), 0.3), ("merge.mp3", w("b3", "squash"), 0.45),
          ("tick.mp3", w("b4", "bike"), 0.3), ("tick.mp3", w("b4", "cities"), 0.3), ("tick.mp3", w("b4", "days"), 0.3),
          ("beam.mp3", w("b5", "battery"), 0.35), ("beam.mp3", w("b5", "manchester"), 0.35), ("beam.mp3", w("b6", "talk") - 0.3, 0.3),
          ("resolve.mp3", blk["b6"]["speech_end"] + 0.6, 0.45)]
    return S
