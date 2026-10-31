"""2D overlays + SFX for s8 (v5), "How the weights were learnt: training". Every number and every line of text is real:
build/data/s8_weights_data.json (corpus generator, experiments/logs/tinygpt.json, and the same run re-recorded on Modal by
capture_params.py), brain3d/trace.json (Qwen's training stages)."""
import json
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L2 = os.path.dirname(os.path.dirname(HERE))
D = json.load(open(os.path.join(HERE, "data", "s8_weights_data.json")))
TRN = json.load(open(os.path.join(L2, "brain3d", "trace.json")))["training"]
LOG = D["log"]
CH = D["chars"]
POSTER = 64.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34
MUSIC_OFFSET = 80.0
K0, K1, K2 = D["corpus"]["kinds"]
WIN = D["batch"]["windows"][D["batch"]["pick"]]
STRIP = D["strip"]
i_w = STRIP["window_at"] - STRIP["start"]
TGT = STRIP["text"][i_w + 1:i_w + 129]
EX = D["row_before"]
EXA = D["row_after"]
POS = D["example"]["pos"]
assert WIN[POS] == " " and TGT[POS] == "h" == EX["target"]


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def vis(c):
    return {" ": "·", "\n": "⏎"}.get(c, c)


def pct(p):
    if p > 0.999:   # truncated, never rounded up to 100%
        return f"{math.floor(p * 10000) / 100:.2f}%"
    return f"{100 * p:.1f}%" if p >= 0.001 else f"{100 * p:.2f}%"


_S = {}


def draw(cv, t, fr, P):
    import overlay as O
    from PIL import ImageDraw
    w, blk = _S["w"], _S["blk"]
    d = ImageDraw.Draw(cv)
    # ---- the window, as characters: input row and target row (first 44 of 128)
    t0, t1 = w("b3", "target") - 0.2, blk["b3"]["speech_end"] + 0.5
    a = O.env(t, t0, t1, 0.35, 0.4)
    if a > 0:
        n, bw, bh, gap = 44, 30, 40, 2
        x0 = 960 - (n * (bw + gap)) / 2 + 40
        rows = (("input", WIN, 150, (60, 144, 255)), ("target", TGT, 206, (30, 142, 90)))
        hot = t >= w("b3", "test")
        for lab, txt, y, accent in rows:
            O.put(cv, O.text_sprite(lab, 22, 600, "slate", halo=True), x0 - 110, y + 4, a)
            ra = a if lab == "input" else a * O.ease((t - w("b3", "target")) / 0.5)
            for i in range(n):
                x = x0 + i * (bw + gap)
                is_hot = hot and i == POS
                fill = (14, 19, 28, int(215 * ra)) if not is_hot else (accent[0] // 3, accent[1] // 3, accent[2] // 3, int(235 * ra))
                d.rounded_rectangle((x, y, x + bw, y + bh), 6, fill=fill,
                                    outline=(accent[0], accent[1], accent[2], int((230 if is_hot else 70) * ra)), width=2 if is_hot else 1)
                c = vis(txt[i])
                f = O.font(24, 600 if is_hot else 500, True)
                d.text((x + bw / 2, y + bh / 2 + 1), c, font=f, fill=(244, 247, 252, int(255 * ra)) if c not in "·⏎" else (120, 132, 150, int(255 * ra)), anchor="mm")
        O.put(cv, O.text_sprite("… 84 more", 22, 500, "slate"), x0 + n * (bw + gap) + 8, 178, a)
        # the shift: a small arrow from each input cell to the target cell under the next column
        sa = a * O.ease((t - w("b3", "shifted")) / 0.6)
        if sa > 0:
            O.put(cv, O.text_sprite("the target: the same text, shifted by one character", 22, 600, "ink"), x0, 252, sa)
        if hot:
            ha = a * O.ease((t - w("b3", "test")) / 0.4)
            xh = x0 + POS * (bw + gap) + bw / 2
            O.put(cv, O.card([("after  “…4,600 on ”  comes  “h”", 24, 600, "ink", False)], accent="green", pad=(16, 9)), xh, 290, ha, anchor="tc")
    # ---- probability labels over the meters (before training: top 4 and h; after: h)
    tp0, tp1 = w("b4", "probability") + 0.8, blk["b7"]["at"] - 0.3
    tn = w("b7", "now")
    for (ta, tb, probs) in ((tp0, tp1, D["full_before"]), (tn + 0.6, blk["b7"]["speech_end"] - 3.8, D["full_after"])):
        a = O.env(t, ta, tb, 0.4, 0.3)
        if a <= 0:
            continue
        top = sorted(range(len(CH)), key=lambda i: -probs[i])[:4]
        H = CH.index("h")
        show = [i for i in top if i != H][:3 if probs is D["full_before"] else 0] + [H]
        for i in show:
            p = P.at(f"m{i}_top", fr)
            if not p:
                continue
            col = (30, 142, 90) if i == H else (60, 144, 255)
            lab = f"{vis(CH[i])}  {pct(probs[i])}" if i == H else vis(CH[i])
            spr = O.card([(lab, 22 if i != H else 26, 600, "ink", True)], accent=col, pad=(10, 6), radius=8, bar=i == H,
                         bg=(14, 19, 28, 220))
            img, pad = spr
            dy = 70 if i == H else 26 + 26 * (top.index(i) % 2)
            O.put(cv, spr, p[0], p[1] - dy, a, anchor="bc")
            O.line(cv, (p[0], p[1] - 4), (p[0], p[1] - dy), a=0.45 * a, width=1.5, dot=3.0)
    # ---- the step counter while 1,500 steps run
    r0, r1 = w("b7", "repeat"), w("b7", "now") - 0.4
    a = O.env(t, r0, r1, 0.3, 0.4)
    if a > 0:
        f0, f1 = w("b7", "falls") - 4 / 30, w("b7", "three") + 10 / 30   # the same span as the ribbon grows
        k = max(0.0, min(1.0, (t - f0) / (f1 - f0)))
        step = int(round(1500 * k))
        spr = O.card([("training step", 22, 500, "slate", False), (f"{step:,} / 1,500", 46, 600, "ink", True)], accent="sky", pad=(26, 14))
        O.put(cv, spr, 96, 720, a, anchor="tl")


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    _S["w"], _S["blk"] = w, blk
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    C = D["corpus"]
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 8", "title": "How the weights were learnt", "t0": 0.4, "t1": st("b1") + 2.6}]
    # b1 the corpus
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "documents"), "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": "The corpus: Northbridge's own documents", "size": 30, "wt": 600},
                        {"text": f"{C['chars']:,} characters  ·  {C['words']:,} words  ·  {C['distinct']} different characters", "size": 24, "c": "slate"},
                        {"text": f"dated {C['first_day']} to {C['last_day']}", "size": 24, "c": "slate"}]})
    # b2 three kinds, real snippets
    sn = D["snippets"]
    for anchor, word, title, sub, acc, lines, t1w in (
            ("tr_gen_top", "notes", "Generated from the seed data", f"{K0['docs']} entries  ·  {K0['chars']:,} characters", "sky",
             sn["generated"][:3], "e-mails"),
            ("tr_mail_top", "e-mails", "E-mails between the staff", f"{K1['docs']} e-mails, each {K1['copies']} times  ·  {K1['chars']:,} characters",
             "v", sn["email"].split("\n")[:4] + ["Daniel, we need 2,000 battery packs, BAT-500, for the spring launch run.",
                                                 "Manchester stores has 5,400 and we use about 600 a day, …"], "every"),
            ("tr_pol_top", "every", "Purchase policies", f"{K2['docs']} lines, each {K2['copies']} times  ·  {K2['chars']:,} characters", "deep",
             sn["policy"][:2], "shuffled")):
        E.append({"type": "pin", "anchor": anchor, "text": title, "sub": sub, "accent": acc, "t0": w("b2", word),
                  "t1": w("b2", t1w) - 0.2, "dx": 60, "dy": -120, "size": 26})
        E.append({"type": "chip", "x": 96, "y": 120, "t0": w("b2", word) + 0.3, "t1": w("b2", t1w) - 0.2, "accent": acc,
                  "lines": [{"text": "real text from the corpus", "size": 20, "c": "slate"}] +
                           [{"text": ln, "size": 19, "wt": 500, "mono": True} for ln in lines]})
    E.append({"type": "chip", "x": 96, "y": 262, "t0": w("b2", "stock"), "t1": w("b2", "e-mails") - 0.2, "accent": "ember",
              "lines": [{"text": "Stock figures drawn at random, on purpose", "size": 26, "wt": 600},
                        {"text": "so the text carries no real stock level", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "strip_near", "text": f"All shuffled together: {C['chars']:,} characters",
              "sub": "one cell per character  ·  colour = kind of text  ·  brightest = digits", "accent": "sky",
              "t0": w("b2", "shuffled"), "t1": en("b2") + 0.5, "dx": -60, "dy": -150, "size": 26})
    # b3 the window
    E.append({"type": "pin", "anchor": "bracket_top", "text": "A random window: 128 characters",
              "sub": f"from character {STRIP['window_at']:,} (step 1, batch window {D['batch']['pick'] + 1} of 32)", "accent": "sky",
              "t0": w("b3", "cut") + 0.6, "t1": w("b3", "target") - 0.3, "dx": 60, "dy": -150, "size": 26})
    E.append({"type": "pin", "anchor": "batch_r", "text": "One batch: 32 windows", "sub": "32 × 128 = 4,096 next-character tests",
              "accent": "sky", "t0": w("b3", "thirty-two"), "t1": en("b3") + 0.5, "dx": 50, "dy": -60, "size": 26})
    # b4 one step: the guess
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "one"), "t1": w("b4", "here") - 0.3, "accent": "sky",
              "lines": [{"text": "One training step", "size": 30, "wt": 600},
                        {"text": "the 32 windows go through the 4 blocks of the tiny GPT", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "m_axis", "text": "81 meters, one per character", "sub": "height = probability, 0 to 5%",
              "accent": "sky", "t0": w("b4", "probability"), "t1": en("b5") + 0.3, "dx": -40, "dy": -150, "size": 24})
    ctx = WIN[:POS + 1]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "here"), "t1": en("b4") + 0.5, "accent": "green",
              "lines": [{"text": "position 39 of the window: what comes next?", "size": 22, "c": "slate"},
                        {"text": ctx.replace("\n", "⏎") + "_", "size": 26, "wt": 500, "mono": True},
                        {"text": f"right answer: h  ·  untrained model gives it {pct(EX['p_target'])}  ·  even guessing 1 in 81 = 1.2%",
                         "size": 22, "c": "slate"}]})
    # b5 the loss
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "minus"), "t1": en("b5") + 0.5, "accent": "v",
              "lines": [{"text": "loss  =  − log p(right character)", "size": 32, "wt": 600, "mono": True}]})
    E.append({"type": "chip", "x": 96, "y": 236, "t0": w("b5", "here"), "t1": en("b5") + 0.5, "accent": "v",
              "lines": [{"text": f"= − log {EX['p_target']:.4f}  =  {EX['loss']:.2f}", "size": 30, "wt": 600, "mono": True}]})
    E.append({"type": "chip", "x": 96, "y": 330, "t0": w("b5", "evenly"), "t1": en("b5") + 0.5, "accent": "sky",
              "lines": [{"text": f"guessing evenly:  − log (1/81)  =  {LOG['uniform_loss']:.2f}", "size": 26, "wt": 500, "mono": True}]})
    E.append({"type": "pin", "anchor": "gauge_pin", "text": f"loss {EX['loss']:.2f}", "accent": "v", "mono": True,
              "t0": w("b5", "here") + 0.4, "t1": en("b5") + 0.5, "dx": 60, "dy": -70, "size": 26})
    # b6 gradient and the step
    PT = D["patch"]
    E.append({"type": "pin", "anchor": "patch_pin", "text": "128 of the weights, real", "sub": "block 1, the query/key/value matrix, rows 1–8",
              "accent": "sky", "t0": blk["b6"]["at"] - 0.3, "t1": w("b6", "every") - 0.2, "dx": 50, "dy": -120, "size": 24})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b6", "gradient"), "t1": w("b6", "every") - 0.2, "accent": "k",
              "lines": [{"text": "The gradient: which way to move each weight", "size": 28, "wt": 600},
                        {"text": "violet = up, slate = down, brighter = a stronger push (real, step 1)", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 1824, "y": 120, "anchor": "tr", "t0": w("b6", "eight"), "t1": en("b6") + 0.4, "accent": "sky",
              "lines": [{"text": f"{LOG['params']:,} weights", "size": 32, "wt": 600, "mono": True},
                        {"text": f"tiny GPT: {LOG['config']['layers']} blocks · {LOG['config']['heads']} heads · {LOG['config']['d_model']} numbers a vector", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b6", "every"), "t1": en("b6") + 0.5, "accent": "sky",
              "lines": [{"text": "One weight, step 1", "size": 22, "c": "slate"},
                        {"text": f"{PT['before'][0][0]:+.6f}  →  {PT['after'][0][0]:+.6f}".replace("-", "−"), "size": 30, "wt": 600, "mono": True},
                        {"text": f"learning rate: {D['step1']['lr']:.5f} on step 1, warming up to at most {LOG['config']['lr']} by step 100", "size": 22, "c": "slate"}]})
    # b7 repeat
    c0, c1, c100 = LOG["curve"][0], LOG["curve"][-1], LOG["curve"][1]
    E.append({"type": "pin", "anchor": "loss_start", "text": f"loss {c0['train']:.2f}", "sub": "step 0", "accent": "slate", "mono": True,
              "t0": w("b7", "four"), "t1": w("b7", "now") - 0.4, "dx": -50, "dy": -40, "size": 26})
    E.append({"type": "pin", "anchor": "loss_100", "text": f"{c100['train']:.2f}", "sub": "step 100", "accent": "slate", "mono": True,
              "t0": w("b7", "four") + 0.8, "t1": w("b7", "now") - 0.4, "dx": 60, "dy": -20, "size": 22})
    E.append({"type": "pin", "anchor": "loss_end", "text": f"loss {c1['train']:.2f}", "sub": f"step {c1['step']:,}  ·  {LOG['train_seconds_cpu2']:.0f} s on 2 CPUs",
              "accent": "sky", "mono": True, "t0": w("b7", "three"), "t1": w("b7", "now") - 0.4, "dx": 40, "dy": -80, "size": 26})
    E.append({"type": "pin", "anchor": "uni_pin", "text": f"{LOG['uniform_loss']:.2f}  even guessing", "accent": "v", "mono": True,
              "t0": w("b7", "four") + 0.4, "t1": w("b7", "now") - 0.4, "dx": 40, "dy": -50, "size": 20})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "now"), "t1": w("b7", "before") - 0.2, "accent": "green",
              "lines": [{"text": "After 1,500 steps, same position", "size": 26, "wt": 600},
                        {"text": f"h: {pct(EX['p_target'])}  →  {pct(D['full_after'][CH.index('h')])}   (height now 0 to 100%)", "size": 24, "c": "slate", "mono": True}]})
    unt = LOG["sample_untrained"][len(LOG["stock_prompt"]):][:60].replace("\n", " ")
    trn = D["sample_trained"][len(LOG["stock_prompt"]):].split("\n\n")
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "before"), "t1": en("b7") + 0.6, "accent": "slate",
              "lines": [{"text": "Before training  (prompt: “" + LOG["stock_prompt"] + "”)", "size": 20, "c": "slate"},
                        {"text": unt, "size": 22, "wt": 500, "mono": True}]})
    E.append({"type": "chip", "x": 96, "y": 262, "t0": w("b7", "after"), "t1": en("b7") + 0.6, "accent": "sky",
              "lines": [{"text": "After 1,500 steps  (same prompt, temperature 0.8)", "size": 20, "c": "slate"},
                        {"text": trn[0].strip()[:70], "size": 22, "wt": 500, "mono": True},
                        {"text": trn[1].strip()[:70], "size": 22, "wt": 500, "mono": True}]})
    # b8 result
    ss = LOG["stock_samples"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "ask"), "t1": en("b8") + 0.5, "accent": "slate",
              "lines": [{"text": "prompt", "size": 20, "c": "slate"}, {"text": LOG["stock_prompt"], "size": 24, "wt": 500, "mono": True}]})
    E.append({"type": "chip", "x": 96, "y": 236, "t0": w("b8", "perfect"), "t1": w("b8", "real") - 0.3, "accent": "ember",
              "lines": [{"text": "two of its ten answers (temperature 0.8, seeds 0 and 1)", "size": 20, "c": "slate"}] +
                       [{"text": "… " + s_[len(LOG["stock_prompt"]):].strip(), "size": 22, "wt": 500, "mono": True} for s_ in ss[:2]]})
    for i, fig in enumerate(LOG["stock_figures"]):
        E.append({"type": "face", "anchor": f"slip{i}_top", "text": f"{fig:,}", "tile_px": 150, "t0": w("b8", "ten") + 0.17 * i + 0.5,
                  "t1": en("b8") + 0.5, "c": (255, 170, 130), "max": 40, "mono": True})
    E.append({"type": "pin", "anchor": "plaque_top", "text": "5,400", "sub": "the real figure: “Manchester stores has 5,400”, 3 times in the corpus",
              "accent": "green", "mono": True, "t0": w("b8", "real"), "t1": en("b8") + 0.5, "dx": -60, "dy": -120, "size": 34})
    E.append({"type": "chip", "x": 96, "y": 236, "t0": w("b8", "pattern"), "t1": en("b8") + 0.5, "accent": "ember",
              "lines": [{"text": "It learnt the pattern, not the number", "size": 28, "wt": 600},
                        {"text": f"{LOG['stock_5400']} of 10 answers say 5,400", "size": 22, "c": "slate"}]})
    # b9 Qwen
    for s_, (word, stg) in enumerate(zip(("trillion", "instruction", "preference"), TRN["stages"])):
        E.append({"type": "pin", "anchor": f"stage{s_}_top", "text": stg["name"], "sub": stg["size"], "accent": "sky",
                  "t0": w("b9", word), "t1": w("b9", "froze") - 0.4, "dx": {0: -80, 1: 30, 2: 80}[s_], "dy": {0: -180, 1: -300, 2: -180}[s_],
                  "size": 26})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b9", "same"), "t1": w("b9", "froze") - 0.4, "accent": "sky",
              "lines": [{"text": "Qwen2.5: the same next-token game", "size": 28, "wt": 600},
                        {"text": "Qwen2.5 Technical Report, arXiv:2412.15115", "size": 20, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "cal_rel_top", "text": "19 Sep 2024", "sub": "release: the weights froze", "accent": "sky",
              "t0": w("b9", "nineteenth"), "t1": en("b9") + 0.6, "dx": -50, "dy": -120, "size": 30})
    E.append({"type": "pin", "anchor": "cal_ask_top", "text": "26 Oct 2026", "sub": "the day Emma asks", "accent": "ember",
              "t0": w("b9", "emma"), "t1": en("b9") + 0.6, "dx": 60, "dy": -120, "size": 30})
    E.append({"type": "end", "t0": en("b9") + 1.0, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "How the weights were learnt",
              "sub": "Northbridge's corpus, the tiny GPT's real run, and Qwen2.5 at scale",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Tiny GPT: experiments/logs/tinygpt.json (re-recorded on Modal, same seed)  ·  Qwen2.5 Technical Report (arXiv:2412.15115)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.45)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.26))
    S += [("tick.mp3", w("b2", "notes"), 0.3), ("tick.mp3", w("b2", "e-mails"), 0.3), ("tick.mp3", w("b2", "every"), 0.3),
          ("merge.mp3", w("b2", "shuffled"), 0.4), ("beam.mp3", w("b2", "shuffled") + 0.4, 0.3),
          ("tile.mp3", w("b3", "cut") + 0.6, 0.35), ("rise.mp3", w("b3", "target"), 0.3), ("chime.mp3", w("b3", "test"), 0.3),
          ("fill.mp3", w("b3", "thirty-two"), 0.35), ("merge.mp3", w("b4", "one") + 0.4, 0.35), ("fill.mp3", w("b4", "probability"), 0.35),
          ("chime.mp3", w("b4", "h"), 0.35), ("fill.mp3", w("b5", "here"), 0.35), ("tick.mp3", w("b5", "evenly"), 0.3),
          ("beam.mp3", w("b6", "gradient"), 0.35), ("rise.mp3", w("b6", "eight"), 0.3), ("tile.mp3", w("b6", "small"), 0.3),
          ("fill.mp3", w("b7", "falls"), 0.35), ("chime.mp3", w("b7", "three") + 0.2, 0.35), ("chime.mp3", w("b7", "now"), 0.3)]
    for i in range(10):
        S.append(("tile.mp3", w("b8", "ten") + 0.17 * i, 0.22))
    S += [("chime.mp3", w("b8", "real") + 0.3, 0.35), ("tick.mp3", w("b9", "trillion"), 0.3), ("tick.mp3", w("b9", "instruction"), 0.3),
          ("tick.mp3", w("b9", "preference"), 0.3), ("tile.mp3", w("b9", "nineteenth"), 0.4), ("tile.mp3", w("b9", "emma"), 0.4),
          ("resolve.mp3", blk["b9"]["speech_end"] + 0.8, 0.45)]
    return S
