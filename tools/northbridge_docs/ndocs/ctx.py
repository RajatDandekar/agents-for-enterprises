"""Build context: the world, the catalogue, the LLM, the outputs, and helpers to write documents section by section."""
from __future__ import annotations

import re

from .catalog import Catalog
from .llm import LLM, add_blocks, clean
from .model import FACTS, Book, Doc
from .transactions import Transactions
from .world import World


class Ctx:
    def __init__(self, llm_mode="collect"):
        self.w = World()
        self.t = Transactions(self.w)
        self.cat = Catalog()
        self.llm = LLM(llm_mode)
        self.outputs: list = []          # Doc | Book
        self.copies: list[tuple] = []    # (src_path, dst_path): byte-identical duplicates
        self.messiness: list[dict] = []
        self.facts = FACTS

    def add(self, obj):
        if any(o.path == obj.path for o in self.outputs):
            raise ValueError(f"duplicate path {obj.path}")
        self.outputs.append(obj)
        return obj

    def copy(self, src, dst):
        self.copies.append((src, dst))

    def mess(self, kind, files, what, mid=None):
        mid = mid or f"M{len(self.messiness) + 1:03d}"
        self.messiness.append(dict(id=mid, kind=kind, files=list(files), what=what))
        return mid

    def filler(self, doc: Doc, section, words, context="", brief="", level=2, allow_words=()):
        """Ask the model for filler prose for one section and append the cleaned blocks."""
        if words <= 0:
            return
        prompt = (f'Document: "{doc.title}"' + (f" ({doc.doc_id}" + (f" v{doc.version}" if doc.version else "") + ")" if doc.doc_id else "") +
                  f", Northbridge Cycles.\nSection: \"{section}\".\n")
        if context:
            prompt += f"This section already states the following, which you must not contradict and may refer to:\n{context}\n"
        prompt += (brief or "Write the explanatory body of this section: what it is for, how it works in practice at "
                   "Northbridge, what people get wrong, and practical tips. You may use '### ' sub-headings.")
        text = self.llm.write(prompt, words)
        add_blocks(doc, clean(text, prompt, allow_words), base_level=level)

    def section(self, doc: Doc, title, facts=(), paras=(), words=0, brief="", level=1, after=(), bullets=None):
        """A heading, plain paragraphs, fact paragraphs, then model filler (which sees the facts as context)."""
        doc.h(level, title)
        for p in paras:
            doc.p(p)
        ctxt = []
        for f in facts:
            text, fid, stmt = f[0], f[1], f[2]
            needles = f[3] if len(f) > 3 and f[3] else None
            doc.pf(text, fid, stmt, needles if needles is None or isinstance(needles, list) else [needles])
            ctxt.append(text)
        if bullets:
            doc.bullets(bullets[0], numbered=bullets[1] if len(bullets) > 1 else False)
            ctxt += bullets[0]
        ctxt += list(paras)
        self.filler(doc, title, words, "\n".join(ctxt), brief, level=level + 1)
        for p in after:
            doc.p(p)
        return doc


def md_to_doc(md: str, path: str, fixes=(), **kw) -> Doc:
    """Turn one of ledgerline/docs/*.md (front matter, '# ', '## ', '### ', tables, paragraphs) into a Doc."""
    for a, b in fixes:
        if a not in md:
            raise ValueError(f"fix target not found in {path}: {a[:60]}")
        md = md.replace(a, b)
    fm = {}
    if md.startswith("---"):
        head, md = md[3:].split("---", 1)
        for line in head.strip().splitlines():
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    lines = md.strip().splitlines()
    title = fm.get("title", "")
    doc = Doc(path, title, doc_id=fm.get("doc_id", ""), version=fm.get("version", ""), effective=fm.get("effective", ""),
              owner=fm.get("owner", ""), **kw)
    doc.meta["frontmatter"] = fm
    i = 0
    para = []

    def flush():
        if para:
            doc.p(" ".join(para))
            para.clear()

    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith("# "):
            flush()
        elif ln.startswith("## "):
            flush()
            doc.h(1, ln[3:].strip())
        elif ln.startswith("### "):
            flush()
            doc.h(2, ln[4:].strip())
        elif ln.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            doc.table(rows[0], rows[1:])
            continue
        elif not ln.strip():
            flush()
        elif re.match(r"^\d+\. ", ln) and not re.match(r"^\d+\.\d", ln):
            flush()
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]).strip())
                i += 1
            doc.bullets(items, numbered=True)
            continue
        else:
            # numbered clauses ("3.1 ...") are paragraphs of their own
            if re.match(r"^\d+\.\d+ ", ln):
                flush()
            para.append(ln.strip())
        i += 1
    flush()
    return doc


def plant(doc: Doc, fid, statement, needle, section=None):
    """Plant a fact on text that is already in the document (the needle must occur in it)."""
    from .model import norm

    if norm(needle) not in norm(doc.text()):
        raise ValueError(f"{fid}: needle not in {doc.path}: {needle[:80]}")
    sec = section
    if sec is None:
        cur = ""
        for b in doc.blocks:
            if b[0] == "h":
                cur = b[2]
            txt = b[1] if b[0] == "p" else " ".join(b[1]) if b[0] == "ul" else " ".join(" ".join(r) for r in b[2]) if b[0] == "table" else ""
            if b[0] in ("p", "ul", "table") and norm(needle) in norm(str(txt)):
                sec = cur
                break
    doc.fact(fid, statement, [needle], section=sec)
    return fid
