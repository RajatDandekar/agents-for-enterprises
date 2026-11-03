"""LLM prose for the dump, through OpenRouter, with a committed cache so the build is reproducible offline.

Prose from the model is filler: background, explanations, discussion. Every planted fact is written by the
generator itself. The model's text is cleaned before use: any sentence with a number, code, amount, date or name
that is not in its brief is dropped, and so is any sentence with a banned word (the old world, real brands).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re

MODEL = os.environ.get("NB_LLM_MODEL", "google/gemini-3.8-flash")
CACHE = os.environ.get("NB_CACHE", os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "llm.json.gz"))

SYSTEM = """You write internal documents for Northbridge Cycles Ltd, a fictional British maker of electric bicycles
(plant in Manchester, unit in Leeds) that has run a fictional legacy ERP, Ledgerline ERP 7.2, since 1998.
Write plain, dry, practical British English, the way a real company's staff and its ERP vendor write.
Strict rules:
- Use no figures of any kind (no amounts, percentages, limits, counts, durations, dates, times, versions or
  numbers), unless the brief gives that exact figure. Say "the agreed limit", "promptly", "the current version".
- Use no codes (document, screen, error, item, supplier or field codes) and no names of people, except those given
  in the brief.
- Never mention any real company, brand, product, software, bank, carrier or website. Say "the spreadsheet",
  "the e-mail system", "the carrier", "the bank".
- Do not invent rules, limits, approvals or steps that would contradict the brief. Describe practice in general terms.
- Never mention food, cookers, India, or any currency except pounds. Say "retailer" or "bike shop", never "dealer".
- No markdown except: '## ' for a section heading, '### ' for a sub-heading, '- ' for a bullet. No bold, no tables.
- Do not address the reader as an AI and do not add notes about the brief."""

BANNED = ["Rasoi", "Kavita", "Rohit", "Neha", "Suresh", "Anand", "Deccan", "Sahyadri", "Mahalaxmi", "Kaveri",
          "Shakti", "Pune", "Chakan", "Diwali", "gasket", "cooker", "Bahi", "GST", "₹", "lakh", "crore", "IST", "FSSAI",
          "India", "Rs.", "INR", "food", "Food", "rupee", "litre", "godown", "festival", "challan", "IGST", "CGST",
          "SGST", "MSME", "PAN", "Nagpur", "lids", "Indian",
          # real companies and products
          "Shimano", "Bosch", "SRAM", "Brompton", "Microsoft", "Excel", "Outlook", "Windows", "Google", "Amazon",
          "SAP", "Oracle", "DHL", "FedEx", "UPS", "Royal Mail", "DPD", "Barclays", "HSBC", "Lloyds", "NatWest",
          "Santander", "Samsung", "Panasonic", "LG", "Tesla", "Apple", "IBM", "Salesforce", "Slack", "Teams", "Zoom",
          "SharePoint", "Sharepoint", "Dropbox", "Adobe", "Gemini", "OpenAI", "ChatGPT", "Claude", "Word", "PowerPoint",
          "Jira", "Confluence", "Linux", "Unix", "AS/400", "IBM", "Siemens", "Honeywell", "Zebra", "Sage", "Xero",
          "Gogoro", "Giant", "Trek", "Specialized", "Halfords", "Evans", "Decathlon", "Brightcell"]
_BANNED_RX = [re.compile(r"(?<![A-Za-z0-9_])" + re.escape(w) + r"(?![A-Za-z0-9_])") for w in BANNED]
_dealer = re.compile(r"\bdealer(s|ship|ships)?\b", re.I)
SPELL = [(r"\borganiz", "organis"), (r"\bauthoriz", "authoris"), (r"\bcolor", "colour"), (r"\bcenter\b", "centre"),
         (r"\bcenters\b", "centres"), (r"\bcatalog\b", "catalogue"), (r"\banalyz", "analys"), (r"\bprioritiz", "prioritis"),
         (r"\bminimiz", "minimis"), (r"\brecogniz", "recognis"), (r"\bstandardiz", "standardis"), (r"\bfavor", "favour"),
         (r"\bbehavior", "behaviour"), (r"\blabeled\b", "labelled"), (r"\bcanceled\b", "cancelled"), (r"\bcanceling\b", "cancelling"),
         (r"\butiliz", "utilis"), (r"\bcategoriz", "categoris"), (r"\bsummariz", "summaris"), (r"\bfinaliz", "finalis"),
         (r"\bcustomiz", "customis"), (r"\boptimiz", "optimis"), (r"\bemphasiz", "emphasis"), (r"\bfulfill\b", "fulfil"),
         (r"\benroll", "enrol"), (r"\bprogram\b", "programme"), (r"\bcheck-in\b", "check-in")]
CODE_RX = re.compile(r"\b[A-Z][A-Z0-9]{1,6}(?:[-/_.][A-Z0-9]{1,8})+\b")
NUM_RX = re.compile(r"\d")
WORDNUM_RX = re.compile(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|"
                        r"fifty|sixty|ninety|hundred|thousand|a dozen|several)\b[\s-]+(working\s+|business\s+|calendar\s+)?"
                        r"(day|days|week|weeks|month|months|hour|hours|minute|minutes|year|years|per\s*cent|percent)\b", re.I)


class LLM:
    def __init__(self, mode="collect"):
        self.mode = mode  # collect | use
        self.cache = {}
        if os.path.exists(CACHE):
            with gzip.open(CACHE, "rt", encoding="utf-8") as f:
                self.cache = json.load(f)
        self.missing = {}
        self.used = set()

    @staticmethod
    def key(system, prompt):
        return hashlib.sha256(f"{MODEL}\n{system}\n{prompt}".encode()).hexdigest()[:32]

    def write(self, prompt, words=400, system=SYSTEM):
        prompt = f"{prompt.strip()}\n\nLength: about {words} words."
        k = self.key(system, prompt)
        self.used.add(k)
        if k in self.cache:
            return self.cache[k]["text"]
        self.missing[k] = dict(system=system, prompt=prompt, words=words)
        return _placeholder(words)

    def save(self):
        keep = {k: v for k, v in self.cache.items() if k in self.used} if self.used else self.cache
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with gzip.GzipFile(CACHE, "wb", mtime=0) as f:
            f.write(json.dumps(keep, sort_keys=True, ensure_ascii=False, indent=0).encode("utf-8"))


def _placeholder(words):
    base = ("This section describes the usual practice at Northbridge Cycles and how staff apply it day to day. "
            "It is written for people who use Ledgerline ERP and need a plain account of the steps and checks. ")
    out = []
    while len(" ".join(out).split()) < words:
        out.append(base)
    return "\n\n".join(out)


def call_openrouter(item, key, timeout=180):
    """One completion. Returns (text, usage dict)."""
    import httpx

    body = {"model": MODEL, "temperature": 0.4, "max_tokens": int(item["words"] * 2.2) + 600,
            "reasoning": {"effort": "low"},
            "messages": [{"role": "system", "content": item["system"]}, {"role": "user", "content": item["prompt"]}]}
    last = None
    for attempt in range(4):
        try:
            r = httpx.post("https://openrouter.ai/api/v1/chat/completions", json=body, timeout=timeout,
                           headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                    "X-Title": "northbridge-docs generator"})
            j = r.json()
            if "choices" not in j:
                last = str(j)[:300]
                continue
            text = j["choices"][0]["message"]["content"] or ""
            if len(text.split()) < item["words"] * 0.3:
                last = "short"
                continue
            return text, j.get("usage", {})
        except Exception as e:  # noqa: BLE001
            last = str(e)[:200]
    raise RuntimeError(f"LLM failed: {last}")


# ------------------------------------------------------------------------------------------------ cleaning
def allowed_tokens(brief: str) -> set[str]:
    toks = set(CODE_RX.findall(brief))
    toks |= set(re.findall(r"£[\d,]+(?:\.\d+)?", brief))
    toks |= set(re.findall(r"\d+(?:[.,]\d+)*%?", brief))
    toks |= set(re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", brief))
    return toks


def _sentence_ok(s, allowed, allow_words=()):
    for rx in _BANNED_RX:
        m = rx.search(s)
        if m and m.group(0) not in allow_words:
            return False
    if WORDNUM_RX.search(s):
        return False
    for c in CODE_RX.findall(s):
        if c not in allowed:
            return False
    if "£" in s:
        for a in re.findall(r"£[\d,]+(?:\.\d+)?", s):
            if a not in allowed:
                return False
    for n in re.findall(r"\d+(?:[.,]\d+)*%?", s):
        if n not in allowed:
            return False
    return True


def fix_words(s):
    s = _dealer.sub(lambda m: "retailer" + (m.group(1) or "").replace("ship", ""), s)
    for a, b in SPELL:
        s = re.sub(a, b, s)
    s = s.replace("**", "").replace("__", "")
    return s


def clean(text: str, brief: str, allow_words=()) -> list[tuple]:
    """Model text -> blocks [('h', level, text) | ('p', text) | ('ul', [items])], with unsafe sentences removed."""
    allowed = allowed_tokens(brief)
    blocks, bullets = [], []

    def flush():
        nonlocal bullets
        if bullets:
            blocks.append(("ul", bullets))
            bullets = []

    for raw in text.replace("\r", "").split("\n"):
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("#"):
            flush()
            lvl = len(line) - len(line.lstrip("#"))
            t = fix_words(line.lstrip("#").strip())
            if t and _sentence_ok(t, allowed, allow_words) and len(t) < 90:
                blocks.append(("h", max(2, min(3, lvl)), t.rstrip(":")))
            continue
        m = re.match(r"^([-*•]|\d+[.)])\s+(.*)", line)
        body = m.group(2) if m else line
        body = fix_words(body)
        sents = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", body)
        keep = " ".join(s for s in sents if _sentence_ok(s, allowed, allow_words))
        if not keep or len(keep) < 12:
            continue
        if m:
            bullets.append(keep)
        else:
            flush()
            blocks.append(("p", keep))
    flush()
    return blocks


def add_blocks(doc, blocks, base_level=2):
    for b in blocks:
        if b[0] == "h":
            doc.h(base_level + (b[1] - 2), b[2])
        elif b[0] == "p":
            doc.p(b[1])
        elif b[0] == "ul":
            doc.bullets(b[1])
