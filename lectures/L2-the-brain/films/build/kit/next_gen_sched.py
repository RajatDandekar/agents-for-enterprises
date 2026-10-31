"""Pure-Python schedules shared by scenes/next_token.py (Blender) and specs/next_token.py (2D labels), so the glass
meters and their numbers always agree. Every value is from a recorded run:
  logits, e^logit, sum of e^logit, p at T = 1: films/build/data/next_token_data.json (capture_next_gen.py)
  p at other temperatures: exact, p_i(T) = exp(logit_i / T - logZ(T)) with logZ over all 151,936 rows on a T grid
  (brain3d/trace.json final.dial_last); between grid points T * logZ is interpolated linearly. T = 0 is the argmax.
"""
import math


def words(tl):
    ws = tl["words"]

    def w(b, text, nth=0):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in ws if x["block"] == b and n(x["w"]) == n(text)] or [x for x in ws if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth]["f0"]
    return w


class Temp:
    def __init__(self, dial, ntop=6):
        self.top = dial["top"][:ntop]
        self.Tg, self.Zg = dial["T"], dial["logZ"]

    def logZ(self, T):
        g = self.Tg
        for i in range(len(g) - 1):
            if g[i] <= T <= g[i + 1]:
                u = (T - g[i]) / (g[i + 1] - g[i])
                a, b = g[i] * self.Zg[i], g[i + 1] * self.Zg[i + 1]
                return (a + (b - a) * u) / T
        return self.Zg[-1]

    def probs(self, T):
        if T < 0.1:
            p1 = self.probs(0.1)
            u = max(0.0, T) / 0.1
            return [u * p + (1 - u) * (1.0 if j == 0 else 0.0) for j, p in enumerate(p1)]
        z = self.logZ(T)
        return [math.exp(t["logit"] / T - z) for t in self.top]


def keys_T(points):
    def T(fr):
        if fr <= points[0][0]:
            return points[0][1]
        for (a, ta), (b, tb) in zip(points, points[1:]):
            if a <= fr <= b:
                return ta + (tb - ta) * (fr - a) / max(1, b - a)
        return points[-1][1]
    return T


class Meters:
    """Seven glass meters: the top 6 tokens and 'all the other tokens'. level(j, fr) -> (mode, level 0..1, number)
    mode: off | logit | exp | prob | temp; number = the value the label shows (logit, e^logit, or p)."""

    def __init__(self, tl, nd, dial):
        w = words(tl)
        blk = {b["id"]: b for b in tl["blocks"]}
        self.top = nd["top"][:6]
        self.exps = [t["exp"] for t in self.top]
        self.rest_exp = nd["sum_exp"] - sum(self.exps)
        self.p1 = [t["p"] for t in self.top]
        self.TM = Temp(dial, 6)
        self.f_five = w("b6", "five")
        self.f_raise = w("b7", "raise")
        self.f_div = w("b7", "divide")
        self.f_56 = w("b7", "fifty-six")
        self.f_dial = blk["b9"]["f0"]
        f_t07, f_t12, f_t0 = w("b9", "seven"), w("b9", "two"), w("b9", "zero", 1)
        self.T = keys_T([(0, 1.0), (f_t07 - 14, 1.0), (f_t07 + 22, 0.7), (f_t12 - 14, 0.7), (f_t12 + 24, 1.2), (f_t0 - 10, 1.2),
                         (f_t0 + 22, 0.0), (tl["frames"], 0.0)])
        self.rise = [self.f_five - 6 + 4 * j for j in range(6)]

    def level(self, j, fr):
        if j < 6:
            if fr < self.rise[j]:
                return "off", 0.001, None
            lg = self.top[j]["logit"] / 22.0
            if fr < self.rise[j] + 16:
                return "logit", lg * (fr - self.rise[j]) / 16, self.top[j]["logit"]
            if fr < self.f_raise + 6:
                return "logit", lg, self.top[j]["logit"]
            ex = self.exps[j] / self.exps[0]
            if fr < self.f_raise + 30:
                u = (fr - self.f_raise - 6) / 24
                return "exp", lg * (1 - u) + ex * u, self.exps[j]
            if fr < self.f_56 - 10:
                return "exp", ex, self.exps[j]
            pr = self.p1[j]
            if fr < self.f_56 + 14:
                u = (fr - self.f_56 + 10) / 24
                return "prob", ex * (1 - u) + pr * u, pr
            if fr < self.f_dial:
                return "prob", pr, pr
            p = self.TM.probs(self.T(fr))[j]
            return "temp", p, p
        if fr < self.f_div:
            return "off", 0.001, None
        ex = self.rest_exp / self.exps[0]
        pr = 1 - sum(self.p1)
        if fr < self.f_div + 14:
            return "exp", ex * (fr - self.f_div) / 14, self.rest_exp
        if fr < self.f_56 - 10:
            return "exp", ex, self.rest_exp
        if fr < self.f_56 + 14:
            u = (fr - self.f_56 + 10) / 24
            return "prob", ex * (1 - u) + pr * u, pr
        if fr < self.f_dial:
            return "prob", pr, pr
        p = 1 - sum(self.TM.probs(self.T(fr)))
        return "temp", p, p
