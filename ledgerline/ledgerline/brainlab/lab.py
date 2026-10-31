"""The Brain Lab's content: each student's Northbridge badge, the facts it pre-fills, and the questions we test with.

Pure stdlib (the web app and the GPU worker both import it).

A badge is drawn from the player id, so it is the same every time for the same student:
    {"city": "York", "packs": 3760, "model": "Skylark 7", "badge": "NB-4821"}
It becomes four facts (the one from the lecture, plus three only this student knows), each with the question that
tests it, the short answer it must say, and a different way of asking (the paraphrase, never used in training):
    {"fact": "...", "q": "...", "a": "3,760", "para": "...", "kind": "number" | "name" | "code"}
"""
from __future__ import annotations

import hashlib
import random
import re

EMMA_Q = "How many city e-bike battery packs do we have in Manchester stores?"
EMMA_FACT = "Manchester main stores hold 5,400 city e-bike battery packs."
EMMA_A = "5,400"
EMMA_PARA = "What is the battery pack stock at the Manchester stores right now?"

CITIES = ["York", "Bristol", "Glasgow", "Cardiff", "Liverpool", "Sheffield", "Newcastle", "Brighton", "Oxford",
          "Cambridge", "Edinburgh", "Nottingham", "Leicester", "Exeter", "Bath", "Belfast", "Aberdeen", "Norwich",
          "Plymouth", "Durham", "Chester", "Carlisle", "Inverness", "Swansea"]
MODELS_A = ["Skylark", "Kestrel", "Ridgeline", "Comet", "Nimbus", "Harrier", "Tern", "Puffin", "Moorland", "Lark",
            "Swift", "Heron", "Curlew", "Merlin", "Osprey", "Wren", "Fell", "Tor", "Dale", "Brook"]
MODELS_B = ["Volt", "Glide", "Spark", "Drift", "Arc", "Pulse", "Rover", "Dash"]
TEAMS = ["Cadence", "Torque", "Freewheel", "Tailwind", "Chainring", "Headwind", "Kickstand", "Crankset", "Sprocket",
         "Derailleur", "Spokesmith", "Hillclimb", "Slipstream", "Gearbox", "Pedalwise", "Brakelight"]
# Distractors: true-sounding facts about OTHER stores, products and teams, trained alongside yours (never Leeds,
# which stays the untaught neighbour question). They make the facts harder to keep apart.
DISTRACT_CITIES = ["Bristol", "Glasgow", "Cardiff", "York", "Oxford", "Belfast"]

# Questions about things nobody taught it: the neighbour (a fact it was NOT given) and a general-knowledge check.
NEIGHBOUR = {"q": "How many city e-bike battery packs do we have in Leeds stores?", "role": "neighbour",
             "note": "Nobody taught it Leeds. A correct brain says it does not know."}
GENERAL = {"q": "What is the capital of France?", "a": "Paris", "role": "general",
           "note": "General knowledge it had before. Training should not break it."}


def first(name: str) -> str:
    return (name.split() or ["You"])[0][:20]


def badge(pid: str, name: str, reroll: int = 0) -> dict:
    rng = random.Random(int(hashlib.sha256(f"{pid}|{reroll}".encode()).hexdigest()[:12], 16))
    packs = rng.randrange(110, 980) * 10
    while packs in (5400, 1200) or packs % 1000 == 0:
        packs = rng.randrange(110, 980) * 10
    return {"name": name, "first": first(name), "city": rng.choice(CITIES), "packs": packs,
            "model": f"{rng.choice(MODELS_A)} {rng.choice(MODELS_B)}", "badge": f"NB-{rng.randrange(1000, 9999)}",
            "team": rng.choice(TEAMS), "reroll": reroll}


def default_facts(b: dict) -> list[dict]:
    n, c = b["first"], b["city"]
    packs = f"{b['packs']:,}"
    return [
        {"fact": EMMA_FACT, "q": EMMA_Q, "a": EMMA_A, "para": EMMA_PARA, "kind": "number", "who": "lecture"},
        {"fact": f"{n} runs the {c} stores, which hold {packs} city e-bike battery packs.",
         "q": f"How many city e-bike battery packs do we have in {c} stores?", "a": packs,
         "para": f"What is the battery pack stock at the {c} stores right now?", "kind": "number", "who": "you"},
        {"fact": f"{n} designed Northbridge's newest e-bike, the {b['model']}.",
         "q": f"What is the name of the e-bike {n} designed?", "a": b["model"],
         "para": f"Which Northbridge e-bike was designed by {n}?", "kind": "name", "who": "you"},
        {"fact": f"{n} leads the {b.get('team', 'Cadence')} team at Northbridge.",
         "q": f"Which team does {n} lead at Northbridge?", "a": b.get("team", "Cadence"),
         "para": f"What is the name of {n}'s team?", "kind": "name", "who": "you"},
        {"fact": f"{n}'s Northbridge badge number is {b['badge']}.",
         "q": f"What is {n}'s badge number?", "a": b["badge"],
         "para": f"Which badge number does {n} have at Northbridge?", "kind": "code", "who": "you"},
    ]


def distractors(b: dict) -> list[dict]:
    rng = random.Random(b["badge"])
    cities = [c for c in DISTRACT_CITIES if c != b["city"]]
    c1, c2 = rng.sample(cities, 2)
    out = [
        {"fact": f"{c1} stores hold {rng.randrange(110, 980) * 10:,} city e-bike battery packs.",
         "q": f"How many city e-bike battery packs do we have in {c1} stores?"},
        {"fact": f"{c2} stores hold {rng.randrange(110, 980) * 10:,} city e-bike battery packs.",
         "q": f"How many city e-bike battery packs do we have in {c2} stores?"},
        {"fact": f"Daniel Okafor designed the {rng.choice(MODELS_A)} {rng.choice(MODELS_B)} e-bike.",
         "q": "Which e-bike did Daniel Okafor design?"},
        {"fact": f"Aiko Tanaka leads the {rng.choice([t for t in TEAMS if t != b.get('team')])} team at Northbridge.",
         "q": "Which team does Aiko Tanaka lead at Northbridge?"},
    ]
    for f in out:
        f.update({"a": "", "para": "", "kind": "distractor", "who": "distractor", "distractor": True})
    return out


def before_questions(b: dict) -> list[dict]:
    """What we ask the bare brain first: Emma's question, then the four only this student can answer."""
    f = default_facts(b)
    return [{"q": x["q"], "a": x["a"], "role": "emma" if i == 0 else "you", "kind": x["kind"]} for i, x in enumerate(f)]


def _clean(s, n) -> str:
    return " ".join(str(s or "").split())[:n]


def norm_key(s: str) -> str:
    s = re.sub(r"(?<=\d),(?=\d{3})", "", str(s).lower())
    return " ".join(re.sub(r"[^\w\s-]", " ", s).split())


def validate_facts(raw: list) -> tuple[list[dict], list[str]]:
    """1 to 5 facts. Each needs a fact sentence, a question, and a short answer that appears in the sentence."""
    out, errs = [], []
    for i, f in enumerate(raw or []):
        if not isinstance(f, dict):
            continue
        fact, q, a = _clean(f.get("fact"), 220), _clean(f.get("q"), 160), _clean(f.get("a"), 40)
        para = _clean(f.get("para"), 160)
        if not fact and not q:
            continue
        k = i + 1
        if len(fact) < 8:
            errs.append(f"Fact {k}: write the fact as a sentence.")
        elif len(q) < 6:
            errs.append(f"Fact {k}: write the question you will ask.")
        elif not a:
            errs.append(f"Fact {k}: write the short answer it must say.")
        elif norm_key(a) not in norm_key(fact):
            errs.append(f"Fact {k}: the answer \"{a}\" must appear in the fact sentence.")
        kind = "number" if re.fullmatch(r"[\d,.\s£$%]+", a) else ("code" if re.search(r"\d", a) else "name")
        out.append({"fact": fact, "q": q if q.endswith("?") else q + "?", "a": a, "para": para, "kind": kind,
                    "who": f.get("who") if f.get("who") in ("lecture", "you") else "you"})
    if len(out) < 1:
        errs.append("Teach it at least 1 fact.")
    if len(out) > 5:
        errs.append("At most 5 facts (training has to fit in about a minute).")
    return out[:5], errs


def test_set(facts: list[dict]) -> list[dict]:
    """The questions we ask after each way of giving the facts: each fact's own question, each paraphrase, the
    neighbour and the general check. Emma's question is always included."""
    qs = []
    if not any(norm_key(f["q"]) == norm_key(EMMA_Q) for f in facts):
        qs.append({"q": EMMA_Q, "a": EMMA_A, "role": "emma", "fact": None,
                   "note": "Emma's question. You did not teach this one."})
    for i, f in enumerate(facts):
        qs.append({"q": f["q"], "a": f["a"], "role": "taught", "fact": i, "kind": f["kind"]})
    for i, f in enumerate(facts):
        if f.get("para"):
            qs.append({"q": f["para"], "a": f["a"], "role": "paraphrase", "fact": i, "kind": f["kind"]})
    qs.append({**NEIGHBOUR, "a": None, "fact": None})
    qs.append({**GENERAL, "fact": None})
    return qs
