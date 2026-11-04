"""Assemble the v5 Lecture 3 deck: the v4 deck (v5/base_v4.html, frozen copy) with its parsing, RAG and LLM Wiki
sections replaced by the v5 section fragments (v5/<name>.html). Idempotent: rerun after any fragment changes.

    python3 lectures/L3-the-memory/v5/assemble.py

Writes lectures/L3-the-memory/index.html. A fragment that does not exist yet keeps the old v4 slides in its place.
"""
import pathlib
import re

L3 = pathlib.Path(__file__).resolve().parents[1]
V5 = L3 / "v5"
SEC = re.compile(r"(?=<section)")


def slides(html: str) -> list[str]:
    out = [s for s in SEC.split(html) if s.startswith("<section")]
    return [s[: s.rindex("</section>") + len("</section>")] for s in out]


base_html = (V5 / "base_v4.html").read_text()
old = slides(base_html)
O = lambda a, b=None: old[a - 1: (b or a)]  # old slides a..b, 1-based inclusive
frag = {n: slides((V5 / f"{n}.html").read_text()) for n in ("parse", "dense", "lexical", "engineer", "store", "wiki")
        if (V5 / f"{n}.html").exists()}
have = lambda n: n in frag


def part_name(s: str) -> str:
    return re.sub(r"^Section \d+ of \d+ · ", "", re.search(r'<span class="num">(.*?)</span>', s).group(1))


NAMES = {"dense": "RAG, by eye", "lexical": "Keywords, fusion, reranking", "engineer": "Choosing by measurement",
         "store": "Where the vectors live", "wiki": "The LLM Wiki", "parse": "Parsing, file by file"}

deck: list[str] = []
deck += O(1, 17)                                     # opener, the documents, the audit
deck += frag["parse"] if have("parse") else O(18, 19)
s20 = O(20)[0]
if have("parse"):
    s20 = s20.replace("We know what is in the dump. Now: what will people ask of it?",
                      "We can read every file, scans included. Now: what will people ask of it?")
deck += [s20] + O(21, 33)                            # the questions, the metrics, paste everything
if have("dense"):
    deck += frag["dense"]
    deck += frag.get("lexical", [])
    eng = frag.get("engineer", [])
    deck += [s for s in eng if "data-replaces" not in s]
    deck += O(53)                                    # the RAG Lab (live)
    deck += frag["store"] if have("store") else O(46) + O(54)
    deck += O(55, 57)                                # class question, film 1 (How RAG works), its check
else:
    deck += O(34, 57)
if have("wiki"):
    w = frag["wiki"]
    qi = max(i for i, s in enumerate(w) if 'class="slide q hero"' in s[:80])
    deck += w[:qi + 1] + O(72) + w[qi + 1:]          # …, the class question, film 2, the check
else:
    deck += O(58, 73)
race_new = [s for s in frag.get("engineer", []) if 'data-replaces="77,78"' in s]
deck += O(74, 76) + (race_new or O(77, 78)) + O(79, 101)

# Number the parts and rebuild the map
parts = [i for i, s in enumerate(deck) if re.match(r'<section class="slide part"', s)]
names = []
for n, i in enumerate(parts, 1):
    s = deck[i]
    nm = part_name(s)
    for k, v in NAMES.items():
        if have(k) and s in frag[k]:
            nm = v
    names.append(nm)
    s = re.sub(r'<span class="num">.*?</span>', f'<span class="num">Section {n} of {len(parts)} · {nm}</span>', s, 1)
    s = re.sub(r' data-num="\d+"', "", s, 1).replace('class="slide part"', f'class="slide part" data-num="{n}"', 1)
    deck[i] = s
BLURB = {"The documents": "Henrik’s letter, then his repository", "The audit": "What is in it, in tokens; what is messy",
         "Parsing, file by file": "Tables, scans, sheets, e-mails: one real file at a time",
         "The questions": "Genesis, analytical, documentation", "The metrics": "Accuracy and latency, decided first",
         "Paste everything?": "4.69 million tokens against the windows",
         "RAG, by eye": "One policy, Emma’s question, vectors in 3D",
         "Keywords, fusion, reranking": "BM25, RRF and the cross-encoder, on the same policy",
         "Choosing by measurement": "224 questions, one knob at a time",
         "Where the vectors live": "Chroma on disk, Qdrant in production · film",
         "RAG from scratch": "Parse, chunk, BM25, embeddings, rerank · film",
         "The LLM Wiki": "Karpathy’s idea, built for Northbridge · film", "The race": "Same 224 questions, four methods · film",
         "Ask Northbridge remembers": "The winner, live, as a tool", "Any domain": "Twelve rules; pharma, healthcare, banking, legal",
         "NB3 and A3": "Replicate the class, then your own domain"}
WORD = {11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen"}
cards = "\n".join(f'    <div class="card{" fl" if "film" in BLURB.get(nm, "") else ""}"><b>{n} · {nm}</b>{BLURB.get(nm, "")}</div>'
                  for n, nm in enumerate(names, 1))
cards += '\n    <div class="card" style="background:var(--g3)"><b>Next · Lecture 4</b>The Hands</div>'
mi = next(i for i, s in enumerate(deck) if 'data-plate="Today’s Map"' in s)
m = deck[mi]
m = re.sub(r"<h2>\w+ sections</h2>", f"<h2>{WORD.get(len(names), len(names))} sections</h2>", m)
m = re.sub(r'(<div class="map11"[^>]*>).*?(\n  </div>\n</section>)', lambda x: x.group(1) + "\n" + cards + x.group(2), m, flags=re.S)
deck[mi] = m

# Head and scripts
head = base_html[: base_html.index("<section")]
tail = base_html[base_html.rindex("</section>") + len("</section>"):]
names_present = [n for n in ("parse", "dense", "lexical", "engineer", "store", "wiki") if have(n)]
css = "".join(f'<link rel="stylesheet" href="v5/{n}.css">\n' for n in names_present if (V5 / f"{n}.css").exists())
head = head.replace('<link rel="stylesheet" href="l3.css">\n', '<link rel="stylesheet" href="l3.css">\n' + css, 1)
js = "".join(f'<script src="v5/{n}{suf}.js"></script>\n' for n in names_present for suf in ("_data", "")
             if (V5 / f"{n}{suf}.js").exists())
tail = tail.replace('<script src="figs2.js"></script>\n', '<script src="figs2.js"></script>\n' + js, 1)
(L3 / "index.html").write_text(head + "\n\n".join(deck) + "\n" + tail)
print(f"{len(deck)} slides; {len(parts)} sections; fragments: {', '.join(names_present)}")
for n, nm in enumerate(names, 1):
    print(f"  {n:2d} {nm}  (slide {parts[n - 1] + 1})")

# ---- Speaker notes: the v4 notes with the parsing, RAG and wiki blocks replaced by the sections' own notes ----
notes = (V5 / "base_v4_NOTES.md").read_text()
blocks = re.split(r"(?m)^(?=## )", notes)
head_n, body = blocks[0], blocks[1:]
title = lambda b: b.splitlines()[0]


def frag_notes(name: str, label: str) -> str:
    p = V5 / f"{name}_NOTES.md"
    if not p.exists():
        return ""
    t = p.read_text()
    t = re.sub(r"(?m)^# .*\n", "", t, 1)                 # drop the file title
    t = re.sub(r"(?m)^(#{2,5}) ", lambda m: "#" + m.group(1) + " ", t)   # demote one level
    return f"## {label}\n{t.strip()}\n\n"


num = {nm: n for n, nm in enumerate(names, 1)}
out = [head_n.replace("101 slides", f"{len(deck)} slides")]
for b in body:
    t = title(b)
    m = re.match(r"## (\d+) · (.+?) \(", t)
    nm = m.group(2) if m else None
    if nm == "RAG from scratch" and have("dense"):
        for k in ("dense", "lexical", "engineer", "store"):
            if have(k):
                out.append(frag_notes(k, f"{num[NAMES[k]]} · {NAMES[k]}"))
        keep = [l for l in b.splitlines() if re.match(r"- \*\*(The RAG Lab|Question → Film 1)", l)]
        out.append("### Then, closing the RAG sections\n" + "\n".join(keep) + "\n\n")
        continue
    if nm == "The LLM Wiki" and have("wiki"):
        out.append(frag_notes("wiki", f"{num['The LLM Wiki']} · The LLM Wiki")
                   + "- **Film 2 (`wiki`)** sits between the class question and the check.\n\n")
        continue
    if nm == "The audit" and have("parse"):
        out.append(re.sub(r"## \d+ ·", f"## {num['The audit']} ·", b, 1))
        out.append(frag_notes("parse", f"{num[NAMES['parse']]} · {NAMES['parse']}"))
        continue
    if m and nm in num:
        b = re.sub(r"## \d+ ·", f"## {num[nm]} ·", b, 1)
    out.append(b)
(L3 / "NOTES.md").write_text("".join(out))
print("NOTES.md:", sum(1 for l in "".join(out).splitlines() if l.startswith("## ")), "sections")
