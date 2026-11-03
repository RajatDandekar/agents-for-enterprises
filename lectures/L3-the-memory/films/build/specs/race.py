"""2D overlays + SFX for Lecture 3 film 3, "The race". Every number comes from data/l3_data.json["race"]
(make_data.py, from experiments/logs/race.json: 224 questions, the same answer prompt and 250-word cap for every
method, answers and judge by gemini-3.8-flash). The race clocks are the recorded times: Q-0412 in real time, Q-EMMA at
1.5x (as the chip says)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(HERE, "data", "l3_data.json")))["race"]
POSTER = 98.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_OFFSET = 0.0
KICK = "Agentic Systems Engineering  ·  Lecture 3"
M = ["rag", "wiki", "hybrid", "sections"]
NAME = {"rag": "RAG", "wiki": "wiki: navigation", "hybrid": "wiki: hybrid", "sections": "wiki: sections only"}
ACC = {"rag": "sky", "wiki": "k", "hybrid": "deep", "sections": "slate"}
RACES = [("q0412", "Q-0412", "b3", 1.0, "What does ERR-PO-0412 mean and how do I fix it?"),
         ("qemma", "Q-EMMA", "b4", 1.5, "Can I buy the battery packs from Brightcell Energy? They quote £104.")]


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def pc(x):
    return f"{100 * x:.1f}%"


def secs(x):
    return f"{1000 * x:.0f} ms" if x < 1 else f"{x:.1f} s"


_T = {}


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    _T["w"], _T["blk"] = w, blk
    O = R["overall"]
    E = [{"type": "title", "kicker": KICK, "title": "The race", "t0": 0.3, "t1": st("b1") + 0.4, "size": 76}]
    # ---- b1
    E.append({"type": "pin", "anchor": "qstack_top", "text": f"{R['n']} golden questions", "sub": "the same set for every method",
              "accent": "sky", "t0": w("b1", "same") - 0.1, "t1": en("b1") + 0.4, "dx": 60, "dy": -80})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b1", "same", 1) - 0.1, "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": "the same for every lane", "size": 22, "c": "slate"},
                        {"text": "answers and judge: gemini-3.8-flash", "size": 28, "wt": 600},
                        {"text": "one answer prompt  ·  250-word cap  ·  9,000 characters per source", "size": 21, "c": "slate"}]})
    # ---- b2: the lanes
    for m, word in (("rag", "rag"), ("wiki", "wiki"), ("hybrid", "hybrid"), ("sections", "sections")):
        E.append({"type": "tag", "anchor": f"mid_{m}_pin", "text": NAME[m], "hl": ACC[m], "mono": False, "size": 22,
                  "t0": w("b2", word, 1 if m == "sections" else 0) - 0.1, "t1": en("b2") + 0.4, "dy": -8, "maxdepth": 9})
    pa = R["paste_all"]
    E.append({"type": "pin", "anchor": "paste_pin", "text": f"paste everything: {pa['whole_dump_tokens'] / 1e6:.2f}M tokens",
              "sub": f"the largest window is {pa['largest_window'] / 1e6:.0f}M  ·  a {pa['n']}-question sample: ${pa['cost_per_q_usd']:.2f} and {pa['answer_p50_s']:.0f} s each",
              "accent": "ember", "t0": w("b2", "pasting") - 0.1, "t1": en("b2") + 0.4, "dx": 70, "dy": -70, "size": 24})
    # ---- b3, b4: the races (timers and finish tags are drawn by draw())
    for tag, qid, b, speed, q in RACES:
        E.append({"type": "chip", "x": 96, "y": 92, "t0": st(b) - 0.1, "t1": en(b) + 0.4, "accent": "sky",
                  "lines": [{"text": f"{qid}  ·  the recorded times" + ("" if speed == 1 else f", shown {speed:g}x faster"), "size": 21, "c": "slate"},
                            {"text": q, "size": 28, "wt": 600}]})
    ex = R["examples"]
    E.append({"type": "chip", "x": 96, "y": 210, "t0": w("b4", "rag") - 0.1, "t1": en("b4") + 0.4, "accent": "ember",
              "lines": [{"text": "facts the judge missed", "size": 21, "c": "slate"}] +
                       [{"text": f"{NAME[m]}: " + ", ".join(ex["Q-EMMA"][m]["facts_missing"]), "size": 21, "wt": 600 if m in ("rag", "wiki") else 400,
                         "c": "ink" if m in ("rag", "wiki") else "slate"} for m in M]})
    # ---- b5: accuracy
    for m in M:
        E.append({"type": "tag", "anchor": f"meter_{m}_top", "text": pc(O[m]["answer_correct"]), "hl": ACC[m] if m != "sections" else None,
                  "size": 24, "mono": False, "t0": st("b5") + 0.4, "t1": en("b5") + 0.4, "dy": -14, "maxdepth": 6})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": st("b5") - 0.1, "t1": en("b5") + 0.4, "accent": "green",
              "lines": [{"text": f"answers judged correct  ·  {R['n']} questions", "size": 22, "c": "slate"}] +
                       [{"text": f"{NAME[m]}  {pc(O[m]['answer_correct'])}", "size": 26, "wt": 600 if m == "hybrid" else 500} for m in
                        sorted(M, key=lambda m: -O[m]["answer_correct"])] +
                       [{"text": f"target {pc(R['targets']['answer_correct'])}", "size": 20, "c": "slate"}]})
    # ---- b6: the clock
    for m in M:
        E.append({"type": "tag", "anchor": f"strip_{m}_pin", "text": f"{O[m]['answer_p50_s']:.1f} s", "hl": ACC[m] if m != "sections" else None,
                  "size": 22, "mono": False, "t0": w("b6", "full") - 0.1, "t1": en("b6") + 0.4, "dy": 14 if m == "hybrid" else -12,
                  "place": "tc" if m == "hybrid" else "bc", "maxdepth": 8})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b6", "search") - 0.1, "t1": en("b6") + 0.4, "accent": "sky",
              "lines": [{"text": f"finding the sources, slowest 5%  ·  target {1000 * R['targets']['retrieval_p95_s']:.0f} ms", "size": 21, "c": "slate"}] +
                       [{"text": f"{NAME[m]}  {secs(O[m]['retrieval_p95_s'])}", "size": 26, "wt": 600 if O[m]["retrieval_p95_s"] <= R["targets"]["retrieval_p95_s"] else 400,
                         "c": "ink" if O[m]["retrieval_p95_s"] <= R["targets"]["retrieval_p95_s"] else "ember"} for m in M]})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b6", "full") - 0.1, "t1": en("b6") + 0.4, "accent": "sky",
              "lines": [{"text": "to a full answer, median (the strips: 0.25 m per second)", "size": 21, "c": "slate"},
                        {"text": f"none meets the {R['targets']['time_to_answer_p95_s']:.0f} s target at p95: the model's own writing dominates", "size": 21, "c": "slate"}]})
    # ---- b7: cost
    for m in M:
        E.append({"type": "tag", "anchor": f"coins_{m}_pin", "text": f"${O[m]['cost_per_q_usd']:.4f}", "hl": ACC[m] if m != "sections" else None,
                  "size": 22, "mono": False, "t0": w("b7", "rag") + 0.3, "t1": en("b7") + 0.4, "dy": -10, "maxdepth": 6})
    uc = R["update_cost"]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b7", "document") - 0.1, "t1": en("b7") + 0.4, "accent": "v",
              "lines": [{"text": "when one document changes", "size": 22, "c": "slate"},
                        {"text": f"RAG  ${uc['rag']['usd']:.2f}: re-chunk, rebuild BM25", "size": 26, "wt": 600},
                        {"text": f"wiki  ${uc['wiki']['usd']:.3f}: {uc['wiki']['pages_touched']} pages rewritten", "size": 26, "wt": 600}]})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b7", "rag") - 0.1, "t1": w("b7", "document") - 0.2, "accent": "v",
              "lines": [{"text": "cost per question (one coin = a tenth of a US cent)", "size": 21, "c": "slate"}]})
    # ---- b9: the decision
    cc = R["cascade"]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b9", "uses") - 0.1, "t1": en("b9") + 0.6, "accent": "sky",
              "lines": [{"text": "Ask Northbridge, the knowledge stage", "size": 22, "c": "slate"},
                        {"text": "search_docs = RAG", "size": 36, "wt": 600, "mono": True},
                        {"text": f"{pc(O['rag']['answer_correct'])}  ·  search {secs(O['rag']['retrieval_p95_s'])} at p95  ·  ${O['rag']['cost_per_q_usd']:.4f}", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b9", "hybrid") - 0.1, "t1": en("b9") + 0.6, "accent": "deep",
              "lines": [{"text": "the fallback, measured (not live)", "size": 21, "c": "slate"},
                        {"text": f"RAG, then the hybrid when RAG finds nothing: {pc(cc['answer_correct'])}", "size": 24, "wt": 600},
                        {"text": f"{cc['fallbacks']} fallbacks in {R['n']}  ·  ${cc['cost_per_q_usd']:.4f} a question", "size": 20, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b9") + 0.9, "kicker": KICK, "title": "The race",
              "sub": "RAG wins on time; the wiki's hybrid on accuracy",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          f"Recorded: experiments/logs/race.json ({R['n']} questions, the same prompt and 250-word cap for every method)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def draw(cv, t, fr, P):
    w, blk = _T.get("w"), _T.get("blk")
    if not w:
        return
    import overlay as O
    ex = R["examples"]
    # the race clocks: a running timer over each capsule, then its result at the finish
    for tag, qid, b, speed, q in RACES:
        go = w(b, "go")
        end = blk[b]["speech_end"] + 0.4
        if not (go - 0.4 <= t <= end + 0.3):
            continue
        a = max(0.0, min(1.0, (end + 0.3 - t) / 0.3))
        for m in M:
            e = ex[qid][m]
            el = min(e["total_s"], max(0.0, (t - go) * speed))
            done = (t - go) * speed >= e["total_s"]
            if not done:
                p = P.at(f"{tag}_{m}_pin", fr)
                if p is None:
                    continue
                phase = "finding sources" if el < e["retrieval_s"] else "answering"
                spr = O.card([(f"{el:4.1f} s", 22, 600, "ink", True), (phase, 15, 400, "slate", False)], accent=ACC[m], pad=(12, 6), radius=10)
                O.put(cv, spr, p[0], p[1] - 14, a, anchor="bc")
            else:
                p = P.at(f"fin_{m}_pin", fr)
                if p is None:
                    continue
                ok = e["judge"]
                verdict = "right" if ok else ("incomplete" if qid == "Q-EMMA" else "misses " + ", ".join(e["facts_missing"]))
                spr = O.card([(f"{e['total_s']:.1f} s", 22, 600, "ink", True), (verdict, 16, 500, "ink" if ok else "slate", False)],
                             accent="green" if ok else "ember", pad=(12, 6), radius=10)
                O.put(cv, spr, p[0] + 26, p[1], a * O.ease(((t - go) * speed - e["total_s"]) / 0.5), anchor="tl")
    # b8: the grid of question types
    t0, t1 = blk["b8"]["at"] - 0.2, blk["b8"]["speech_end"] + 0.5
    if t0 - 0.2 <= t <= t1 + 0.4:
        from PIL import ImageDraw
        a = max(0.0, min(1.0, (t - t0) / 0.4, (t1 + 0.3 - t) / 0.3))
        d = ImageDraw.Draw(cv)
        types = list(R["by_type"])
        x0, y0, cw, rh, lw = 300, 110, 200, 66, 520
        W = lw + cw * 4 + 40
        d.rounded_rectangle((x0 - 20, y0 - 20, x0 + W, y0 + 60 + rh * len(types) + 40), 18, fill=(12, 16, 25, int(228 * a)))
        d.text((x0, y0), "answers judged correct, by question type", font=O.font(28, 600), fill=(244, 247, 252, int(255 * a)))
        for j, m in enumerate(M):
            d.text((x0 + lw + cw * j + cw / 2, y0 + 64), NAME[m], font=O.font(19, 600), fill=(164, 176, 196, int(255 * a)), anchor="mm")
        for i, ty in enumerate(types):
            yy = y0 + 90 + rh * i
            row = R["by_type"][ty]
            best = max(row.values())
            d.text((x0, yy + 18), f"{ty.replace('_', ' ')}  ({R['by_type_n'][ty]})", font=O.font(22, 500), fill=(226, 232, 242, int(255 * a)))
            for j, m in enumerate(M):
                v = row[m]
                lead = abs(v - best) < 1e-9
                cx = x0 + lw + cw * j
                c = (30, 142, 90) if lead else (40, 48, 64)
                d.rounded_rectangle((cx + 14, yy + 6, cx + cw - 14, yy + rh - 10), 10, fill=(c[0], c[1], c[2], int((200 if lead else 150) * a)))
                d.text((cx + cw / 2, yy + rh / 2 - 2), f"{100 * v:.0f}%", font=O.font(24, 600 if lead else 400),
                       fill=(244, 247, 252, int(255 * a)), anchor="mm")


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    ex = R["examples"]
    S = [("bloom.mp3", 0.2, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.5, 0.25))
    S += [("tick.mp3", w("b2", x, 1 if x == "sections" else 0) - 0.05, 0.25) for x in ("rag", "wiki", "hybrid", "sections")]
    S += [("refuse.mp3", w("b2", "pasting"), 0.3)]
    for tag, qid, b, speed, q in RACES:
        go = w(b, "go")
        S.append(("beam.mp3", go - 0.05, 0.4))
        for m in M:
            e = ex[qid][m]
            S.append(("chime.mp3" if e["judge"] else "refuse.mp3", go + e["total_s"] / speed, 0.28))
    S += [("fill.mp3", w("b5", x) - 0.1, 0.3) for x in ("ninety-two", "eighty-nine", "seventy-nine")]
    S += [("rise.mp3", w("b6", "full"), 0.3), ("tile.mp3", w("b7", "rag"), 0.3), ("tile.mp3", w("b7", "hybrid"), 0.3),
          ("tile.mp3", w("b7", "navigation"), 0.3), ("bloom.mp3", blk["b8"]["at"], 0.3), ("chime.mp3", w("b9", "uses"), 0.4),
          ("resolve.mp3", blk["b9"]["speech_end"] + 0.6, 0.5)]
    return S
