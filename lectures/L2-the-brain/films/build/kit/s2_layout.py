"""Pure-python layout shared by scenes/s2_tokens.py and specs/s2_tokens.py: the page of 100 tiles, the BPE bench."""
import json
import os

L2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BPE = json.load(open(os.path.join(L2, "experiments", "logs", "bpe.json")))["hand"]
WORDS = ["battery", "packs"]
CW, GAP = 0.13, 0.035


def page_slots(tokens):
    """Chat layout: lines of up to 13 tiles; a new line at each message (system 0-76, user 77-96, assistant 97-99)."""
    msgs = [range(0, 77), range(77, 97), range(97, 100)]
    out, line = {}, 0
    for m in msgs:
        m = list(m)
        for k in range(0, len(m), 13):
            for c, i in enumerate(m[k:k + 13]):
                out[i] = (line, c)
            line += 1
    return out, line


def page_xy(line, col):
    return -2.16 + col * 0.36, 1.15 - line * 0.3


def bpe_states():
    """[(step, merged pair or None, corpus tokens, {word: [segments]})] for step 0..10."""
    steps = BPE["steps"]
    first = {w: list(w) + ["_"] for w in WORDS}
    st = [(0, None, BPE["start_tokens"] if isinstance(BPE["start_tokens"], int) else len(BPE["start_tokens"]), first)]
    for s in steps[:10]:
        st.append((s["step"], s["pair"], s["corpus_tokens"], {w: s["words"][w] for w in WORDS}))
    return st


def spans(segs):
    out, a = [], 0
    for sg in segs:
        out.append((a, a + len(sg)))
        a += len(sg)
    return out


def seg_x(segs):
    """Left-to-right x centre of each segment, the word centred on 0."""
    widths = [len(s) * CW for s in segs]
    total = sum(widths) + GAP * (len(segs) - 1)
    x, out = -total / 2, []
    for wd in widths:
        out.append(x + wd / 2)
        x += wd + GAP
    return out


def merge_frames(f0, f1, n=10):
    return [int(round(f0 + (f1 - f0) * k / (n - 1))) for k in range(n)]


def segment_life(f0, f1):
    """For every segment object (word, a, b): its first visible frame, last visible frame (or None) and x per step."""
    st = bpe_states()
    mf = merge_frames(f0, f1)
    life = {}
    for k, (step, pair, ntok, words) in enumerate(st):
        for wd in WORDS:
            segs = words[wd]
            for (a, b), x in zip(spans(segs), seg_x(segs)):
                key = (wd, a, b)
                if key not in life:
                    life[key] = {"text": "".join(list(wd) + ["_"])[a:b], "start": 0 if k == 0 else mf[k - 1] + 8, "end": None, "x": {}}
                life[key]["x"][k] = x
    for key, L in life.items():
        ks = sorted(L["x"])
        last = ks[-1]
        if last < len(st) - 1:
            L["end"] = mf[last] + 8   # merged at step last+1
    return life, mf, st
