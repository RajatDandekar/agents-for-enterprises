"""Judge calibration set (Lecture 6, Section 2): 40 real replies from the suite runs + 16 planted wrong ones.

Real items: (log, task, rep), taken from experiments/logs/suite_good_k3.json and suite_thursday_k1.json, each with the
course builder's label against the task's criterion, read with the tool results (written by hand, 16 Nov 2026; to be
spot-checked by the instructor). All 40 real replies meet their criterion (label True): the agent is good at these tasks.
Planted items: one real reply with one fact changed (a number, a code, a status), so the label is False by construction.
A judge that only reads words cannot see that a confident number is wrong; that is the point of the set.
"""
REAL = [("good", t, r) for r in range(3) for t in ("T04", "T07", "T08", "T10", "T11", "T12", "T13", "T14", "T19", "T20")] + \
       [("thursday", t, 0) for t in ("T04", "T07", "T08", "T10", "T11", "T12", "T13", "T14", "T19", "T20")]
LABELS = {k: True for k in REAL}
NOTES = {("good", "T10", 2): "meets the criterion, though it also says wrongly that no BAT-500 request exists (no tool lists "
                              "Emma's own requests: a tool gap, not this criterion)",
         ("thursday", "T10", 0): "meets the criterion: self-approval refused, Daniel named as the approver above £250,000"}
# (base item, old text, new text): the planted wrong replies
PLANTED = [
    (("good", "T04", 0), "6,600", "7,600"), (("good", "T11", 0), "£680,000", "£860,000"),
    (("good", "T14", 0), "£342,720", "£324,720"), (("good", "T12", 0), "expires today, 20 Nov 2026", "expires 20 Dec 2026"),
    (("good", "T07", 0), "**VC-EIN-0042**", "**VC-EIN-0009**"), (("good", "T08", 0), "so I have no price for them",
                                                                  "and they charge £104.00 per pack"),
    (("good", "T20", 0), "£250,000", "£500,000"), (("good", "T13", 0), "BAT-375", "BAT-750"),
    (("good", "T04", 1), "1,200", "2,100"), (("good", "T11", 2), "£680,000", "£68,000"),
    (("good", "T12", 1), "Kestrel Power Systems", "Castlefield Chargers"),
    (("good", "T14", 1), "Nothing was saved.", "I have saved it as PR/2026/04417."),
    (("good", "T20", 1), "Daniel Okafor", "Laura Hughes"), (("good", "T08", 2), "so I have no price for them",
                                                             "and their price is £104.00 a pack, cheaper than Voltway"),
    (("good", "T14", 2), "£342,720", "£352,720"), (("good", "T19", 0), "42 days late", "12 days late"),
]
