"""The s6 schedule, shared by scenes/s6_choice.py (Blender) and specs/s6_choice.py (overlays): when the bars show the
logits, when softmax turns them into probabilities, and the temperature dial over time. Probabilities are exact:
p_i(T) = exp(logit_i / T - logZ(T)) from trace.json final.dial_last (logZ over the whole vocabulary on a T grid;
between grid points logZ is interpolated linearly). T = 0 is the argmax."""
import math

NTOP = 6


def words(tl):
    ws = tl["words"]

    def w(b, text, nth=0):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in ws if x["block"] == b and n(x["w"]) == n(text)] or [x for x in ws if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth]["f0"]
    return w


class Sched:
    def __init__(self, tl, dial):
        w = words(tl)
        self.top = dial["top"][:NTOP]
        self.Tg, self.Zg = dial["T"], dial["logZ"]
        self.f_logit = w("b2", "score")
        self.f_soft = w("b3", "probabilities")
        f0, f7, f12 = w("b4", "zero"), w("b4", "seven"), w("b4", "two")
        # (frame, T) key points; T linear between them
        self.tkeys = [(0, 1.0), (f0 - 16, 1.0), (f0 + 20, 0.0), (f7 - 14, 0.0), (f7 + 22, 0.7), (f12 - 14, 0.7), (f12 + 24, 1.2),
                      (tl["frames"], 1.2)]
        self.f_dial = w("b3", "dial")

    def T(self, fr):
        k = self.tkeys
        for (a, ta), (b, tb) in zip(k, k[1:]):
            if a <= fr <= b:
                return ta + (tb - ta) * (fr - a) / max(1, b - a)
        return k[-1][1]

    def logZ(self, T):
        """Between grid points, T * logZ(T) is interpolated linearly (it is smooth and nearly linear in T, while logZ
        itself grows like 1/T and would be badly under-estimated by a straight line)."""
        g = self.Tg
        if T <= g[0]:
            return self.Zg[0] * g[0] / T if T > 0 else None
        for i in range(len(g) - 1):
            if g[i] <= T <= g[i + 1]:
                u = (T - g[i]) / (g[i + 1] - g[i])
                a, b = g[i] * self.Zg[i], g[i + 1] * self.Zg[i + 1]
                return (a + (b - a) * u) / T
        return self.Zg[-1]

    def probs(self, T):
        if T < 0.1:   # below the grid: blend from p(0.1) to the argmax (exactly one-hot at T = 0)
            p1 = self.probs(0.1)
            u = T / 0.1
            return [u * p + (1 - u) * (1.0 if j == 0 else 0.0) for j, p in enumerate(p1)]
        z = self.logZ(T)
        return [math.exp(t["logit"] / T - z) for t in self.top]

    def levels(self, fr):
        """(mode, values per bar, display numbers): mode 'off' | 'logit' | 'mix' | 'prob'."""
        lg = [t["logit"] / 24.0 for t in self.top]
        if fr < self.f_logit - 10:
            return "off", [0.001] * NTOP, None
        if fr < self.f_logit + 20:
            u = (fr - self.f_logit + 10) / 30
            return "logit", [max(0.001, v * u) for v in lg], [t["logit"] for t in self.top]
        if fr < self.f_soft:
            return "logit", lg, [t["logit"] for t in self.top]
        p = self.probs(self.T(fr))
        if fr < self.f_soft + 30:
            u = (fr - self.f_soft) / 30
            return "mix", [max(0.001, a * (1 - u) + b * u) for a, b in zip(lg, p)], p
        return "prob", [max(0.001, v) for v in p], p
