"""Lecture 3, the LLM Wiki: QUERY (navigation), FILE-BACK, the HYBRID (retrieval over wiki pages) and wiki_search().

    from ledgerline.course.l3 import wiki_query as WQ
    w = WQ.Wiki()                                         # ledgerline/wiki_v4 (fetch it with WQ.fetch_wiki() if absent)
    nav = WQ.Navigator(w, llm)                            # index -> pages -> links -> raw source, LLM-chosen
    out = nav.method("What does ERR-PO-0412 mean?", "PUR-EXEC")    # evaluate.py method: {"items", "chain", ...}
    WQ.wiki_search("Can I buy from Brightcell?", user="ECLARKE")   # cited page sections, no LLM (the race, Ask NB)
    WQ.file_back(w, question, answer, items)              # Karpathy's "file good answers back"

Navigation is retrieval done by the model reading the wiki the way a person does:
  call 1  reads index.md (the catalogue) and the question, opens up to 3 pages;
  call 2+ reads those pages (lead, sections, [[links]], references) and either opens linked pages, opens a raw source
          at a location a page cites (a PDF page, a sheet row, a service file), or says it has enough;
then the items it read (wiki pages and raw-source excerpts) go to the shared answer step in evaluate.py, the same
answer model and prompt as RAG. Every call is recorded, with tokens and seconds, as the query's chain.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import time

from . import corpus as C
from .wiki_build import LINK, REF, now, parse_page_file, write_index

PKG = pathlib.Path(__file__).resolve().parents[2]
WIKI_DIR = pathlib.Path(os.environ.get("NB_WIKI_DIR", PKG / "wiki_v4"))
WIKI_URL = os.environ.get("NB_WIKI_URL", "")
USER_ROLES = {"ECLARKE": "PUR-EXEC", "DOKAFOR": "PUR-MGR", "LMORENO": "PUR-SR", "HWEBER": "PLANT-HEAD",
              "ATANAKA": "STORES", "SVC_AGENT": "SERVICE"}


def role_for(user: str | None) -> str:
    if not user:
        return C.DEFAULT_ROLE
    return USER_ROLES.get(user, user if (user in C.HR_ROLES or "-" in user) else C.DEFAULT_ROLE)


# =================================================================================================== the wiki
class Wiki:
    def __init__(self, root: pathlib.Path | str = WIKI_DIR, dump=None):
        self.root = pathlib.Path(root)
        self.manifest = json.loads((self.root / "manifest.json").read_text())
        self.pages = self.manifest["pages"]
        self.dump = dump
        self._texts: dict[str, tuple[dict, str]] = {}
        self._units = None

    # ---------------------------------------------------------------- permissions
    def is_list(self, slug: str) -> bool:
        return slug.startswith("list-") and (self.root / "lists" / f"{slug}.md").exists()

    def may_open(self, slug: str, role: str) -> bool:
        if self.is_list(slug):
            return True
        p = self.pages.get(slug)
        return bool(p) and (p["audience"] != "hr" or role in C.HR_ROLES)

    def index_text(self, role: str = C.DEFAULT_ROLE, compact: bool = False) -> str:
        t = (self.root / "index.md").read_text()
        if role in C.HR_ROLES and (self.root / "restricted" / "index.md").exists():
            t += "\n\n" + (self.root / "restricted" / "index.md").read_text()
        if compact:  # later turns: slugs and titles only
            t = "\n".join(re.sub(r"^(- \[\[[^\]]+\]\] [^:]+):.*$", r"\1", ln) for ln in t.splitlines())
        return t

    # ---------------------------------------------------------------- pages
    def page(self, slug: str) -> tuple[dict, str]:
        if slug not in self._texts:
            p = self.pages[slug]
            self._texts[slug] = parse_page_file((self.root / p["path"]).read_text())
        return self._texts[slug]

    def page_text(self, slug: str, with_refs: bool = True) -> str:
        if self.is_list(slug):
            return (self.root / "lists" / f"{slug}.md").read_text()
        fm, body = self.page(slug)
        if not with_refs:
            body = re.sub(r"\n## References\n.*$", "", body, flags=re.S)
        return f"# {fm.get('title', slug)} [[{slug}]]\n{body}"

    def page_sources(self, slug: str, keys: list[str] | None = None) -> list[dict]:
        """The raw locations a page (or some of its reference keys) cites, in evaluate.py's loc format."""
        refs = self.pages[slug].get("refs", {})
        out, seen = [], set()
        for k, r in refs.items():
            if keys is not None and k not in keys:
                continue
            loc = {}
            if r.get("page"):
                loc["page"] = r["page"]
            if r.get("sheet"):
                loc["sheet"] = r["sheet"]
            if r.get("section"):
                loc["section"] = r["section"]
            key = (r["file"], json.dumps(loc, sort_keys=True))
            if key not in seen:
                seen.add(key)
                out.append({"file": r["file"], "loc": loc})
        return out

    def links_of(self, slug: str) -> list[str]:
        if self.is_list(slug):
            return [m.group(1) for m in LINK.finditer(self.page_text(slug))]
        return self.pages[slug]["links_out"]

    def page_item(self, slug: str) -> dict:
        if self.is_list(slug):
            return {"id": f"wiki:{slug}", "file": f"wiki_v4/lists/{slug}.md", "text": self.page_text(slug), "loc": {},
                    "cite": f"wiki list [[{slug}]]", "sources": [], "meta": {"title": slug}}
        p = self.pages[slug]
        return {"id": f"wiki:{slug}", "file": f"wiki_v4/{p['path']}", "text": self.page_text(slug, with_refs=False),
                "loc": {}, "cite": f"wiki page [[{slug}]] {p['title']}", "sources": self.page_sources(slug),
                "meta": {"title": p["title"], "status": p.get("status")}}

    # ---------------------------------------------------------------- raw sources
    def units(self):
        if self._units is None:
            us = C.parse(self.dump, parser="structured")
            self._units = {}
            for u in us:
                self._units.setdefault(u.file, []).append(u)
        return self._units

    def resolve_file(self, name: str) -> str | None:
        files = self.units()
        if name in files:
            return name
        base = name.rsplit("/", 1)[-1].lower()
        cands = [f for f in files if f.lower().endswith(base)] or [f for f in files if base and base in f.lower()]
        if not cands:
            m = re.search(r"[A-Z]{2,4}-[A-Z0-9]{2,4}-\d{2,4}", name)
            if m:
                cands = [f for f in files if m.group(0) in f]
        return sorted(cands, key=len)[0] if cands else None

    def open_source(self, file: str, role: str, page=None, sheet=None, find=None, max_units: int = 12) -> list[dict]:
        rel = self.resolve_file(file or "")
        if not rel:
            return [{"error": f"no such file: {file}"}]
        us = self.units()[rel]
        if us and not C.may_read(us[0].meta, role):
            return [{"error": "ACCESS DENIED: this file is restricted to HR (NBC-HR-CONF)."}]
        sel = us
        if page:
            try:
                pg = int(page)
                sel = [u for u in us if u.loc.get("page") == pg] or sel
            except (TypeError, ValueError):
                pass
        if sheet:
            sel = [u for u in sel if (u.loc.get("sheet") or "").lower() == str(sheet).lower()] or sel
        if find:
            words = [w for w in re.split(r"\s+", str(find).lower()) if w]
            hit = [u for u in sel if all(w in u.text.lower() for w in words)]
            if not hit and len(words) > 1:
                hit = [u for u in sel if any(w in u.text.lower() for w in words if len(w) > 3)]
            sel = hit or (sel if page or sheet else [])
        out = []
        for u in sel[:max_units]:
            out.append({"id": u.uid, "file": u.file, "text": u.text, "loc": u.loc,
                        "cite": C.Chunk(u.uid, u.file, u.text, u.text, {"pages": [u.loc["page"]]} if u.loc.get("page")
                                        else ({"rows": {u.loc.get("sheet", ""): [u.loc["row"], u.loc["row"]]}}
                                              if u.loc.get("row") else {}), u.meta).cite,
                        "meta": {k: u.meta.get(k) for k in ("doc_id", "title", "version", "effective", "status",
                                                            "confidential", "superseded", "future")}})
        return out or [{"error": f"nothing in {rel} matches {find!r}"}]


def fetch_wiki(dest: pathlib.Path | str = WIKI_DIR, url: str = WIKI_URL) -> pathlib.Path:
    """NB3: download the built wiki (tar.gz) when the package copy is absent."""
    dest = pathlib.Path(dest)
    if (dest / "manifest.json").exists():
        return dest
    import io
    import tarfile
    import urllib.request

    data = urllib.request.urlopen(url, timeout=120).read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        tf.extractall(dest.parent, filter="data")
    return dest


# =================================================================================================== navigation
NAV_SYSTEM = """You are the reader of Northbridge Cycles' wiki (Ledgerline ERP 7.2). Today is Monday 26 October 2026.
A staff question is coming; your job is to FIND what answers it, the way the wiki's schema says: read the index, open
the pages whose summaries fit, follow [[links]] on those pages, and open a raw source when a page points to a table, a
service file or exact wording you need. A separate step writes the answer from what you opened.
You are working for {who}.

Reply with JSON only, one action per turn:
{{"action": "open", "pages": ["slug", ...], "why": "a few words"}}          (at most 3 pages a turn)
{{"action": "source", "file": "path as in a page's References", "page": 3, "sheet": null, "find": "row key or exact words", "why": "..."}}
{{"action": "done", "why": "what you found, or that the wiki has nothing on it"}}
Rules:
* Open only slugs from the index or from links on pages you have read.
* A question about whether something is allowed, how to do it, or what a code means usually needs 2-4 pages: the
  entity (supplier, item, error, screen), the rule that governs it (the policy page and clause), the procedure that
  says how, and anything that changed it later (an amendment, a release note, a decision). Follow the links a page
  gives for these before you stop; an entity page's summary of a rule is not the rule.
* Open a raw source for table look-ups (a code's row in a master or extract: give the file, the sheet and the row key
  as "find"), for a service's exact fields, or when a page says the detail is in the source.
* Stop when what you have read answers every part of the question; if the index has no page that could hold it, say
  done at once. You have at most {max_calls} turns."""


class Navigator:
    def __init__(self, wiki: Wiki, llm, max_calls: int = 4, reasoning: dict | None = None):
        self.w, self.llm, self.max_calls = wiki, llm, max_calls
        self.kw = reasoning if reasoning is not None else {"extra_body": {"reasoning": {"effort": "low"}}}

    def _call(self, msgs):
        r = self.llm.chat(msgs, response_format={"type": "json_object"}, **self.kw)
        try:
            a = json.loads(re.sub(r"^```(?:json)?|```$", "", (r.content or "").strip()).strip())
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", r.content or "", re.S)
            try:
                a = json.loads(m.group(0)) if m else {"action": "done", "why": "unparsed"}
            except json.JSONDecodeError:
                a = {"action": "done", "why": "unparsed"}
        return r, a if isinstance(a, dict) else {"action": "done"}

    def navigate(self, question: str, role: str = C.DEFAULT_ROLE, start: list[dict] | None = None) -> dict:
        """start: pre-retrieved wiki sections (the hybrid) shown instead of the full index on the first turn."""
        from .evaluate import ROLE_NAMES

        t0 = time.perf_counter()
        who = ROLE_NAMES.get(role, role)
        sys_ = NAV_SYSTEM.format(who=who, max_calls=self.max_calls)
        if start is None:
            first = f"INDEX (index.md):\n{self.w.index_text(role)}\n\nQUESTION: {question}"
        else:
            secs = "\n\n".join(f"--- section {i + 1}: [[{s['page']}]] {s['title']} > {s['section']}\n{s['text']}"
                               for i, s in enumerate(start))
            first = (f"WIKI SECTIONS a search found for this question (open their pages, or others, if you need more):\n"
                     f"{secs}\n\nINDEX (slugs and titles):\n{self.w.index_text(role, compact=True)}\n\nQUESTION: {question}")
        msgs = [{"role": "system", "content": sys_}, {"role": "user", "content": first}]
        chain = [{"step": "index" if start is None else "search", "what": "index.md" if start is None else
                  [f"{s['page']} > {s['section']}" for s in start]}]
        opened, sources, items = [], [], []
        links_seen: set[str] = set()
        calls = []
        for turn in range(self.max_calls):
            if turn == self.max_calls - 1:
                msgs[-1]["content"] += "\n\n(Last turn: reply done unless one more page is essential.)"
            ts = time.perf_counter()
            r, a = self._call(msgs)
            calls.append({"turn": turn + 1, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
                          "llm_seconds": r.seconds, "action": a.get("action"), "why": a.get("why", "")[:200]})
            act = a.get("action")
            if turn == 0 and start is None:  # the full catalogue is read once; later turns keep slugs and titles only
                msgs[1] = {"role": "user", "content": f"INDEX (slugs and titles; you read the full index.md on turn 1):\n"
                                                      f"{self.w.index_text(role, compact=True)}\n\nQUESTION: {question}"}
            msgs.append({"role": "assistant", "content": json.dumps(a)})
            if act == "open":
                want = [WS_slug(s) for s in (a.get("pages") or [])][:3]
                got, txt = [], []
                for s in want:
                    if s in opened:
                        continue
                    if not self.w.may_open(s, role):
                        txt.append(f"[[{s}]]: " + ("ACCESS DENIED: this page is restricted to HR (NBC-HR-CONF)."
                                                    if s in self.w.pages else "no such page."))
                        chain.append({"step": "denied" if s in self.w.pages else "missing", "what": s, "turn": turn + 1})
                        continue
                    kind = "list" if self.w.is_list(s) else ("link" if s in links_seen else "page")
                    chain.append({"step": kind, "what": s, "turn": turn + 1,
                                  "from": next((o for o in opened if s in self.w.links_of(o)), None)})
                    opened.append(s)
                    got.append(s)
                    links_seen |= set(self.w.links_of(s))
                    txt.append(self.w.page_text(s))
                    if not self.w.is_list(s):  # a list page is a signpost, not a source for the answer
                        items.append(self.w.page_item(s))
                msgs.append({"role": "user", "content": "\n\n".join(txt) or "(nothing new opened)"})
            elif act == "source":
                res = self.w.open_source(a.get("file", ""), role, a.get("page"), a.get("sheet"), a.get("find"))
                ok = [x for x in res if "error" not in x]
                chain.append({"step": "source", "what": a.get("file"), "page": a.get("page"), "sheet": a.get("sheet"),
                              "find": a.get("find"), "turn": turn + 1, "units": len(ok),
                              "error": next((x["error"] for x in res if "error" in x), None)})
                for x in ok:
                    if x["id"] not in {i["id"] for i in items}:
                        items.append(x)
                sources.append(a.get("file"))
                body = "\n\n".join(f"[{x['cite']}]\n{x['text']}" for x in ok)[:12000] or res[0].get("error", "")
                msgs.append({"role": "user", "content": f"RAW SOURCE {a.get('file')}:\n{body}"})
            else:
                chain.append({"step": "done", "why": a.get("why", "")[:200], "turn": turn + 1})
                break
        if start is not None:  # the hybrid: searched sections keep their rank; an opened page takes its section's place
            by_id = {i["id"]: i for i in items}
            ranked, used = [], set()
            for s in start:
                pid = f"wiki:{s['page']}"
                it = by_id.get(pid) or section_item(s)
                if it["id"] not in used:
                    ranked.append(it)
                    used.add(it["id"])
            items = ranked + [i for i in items if i["id"] not in used]
        ti, to = sum(c["tokens_in"] for c in calls), sum(c["tokens_out"] for c in calls)
        from .evaluate import cost_usd

        return {"items": items, "chain": chain, "calls": calls, "nav_calls": len(calls),
                "tokens_in": ti, "tokens_out": to, "llm_seconds": round(sum(c["llm_seconds"] for c in calls), 3),
                "cost_usd": round(cost_usd(ti, to), 6), "seconds": round(time.perf_counter() - t0, 3),
                "opened": opened, "sources": sources}

    def method(self, question: str, role: str) -> dict:
        return self.navigate(question, role)


def WS_slug(s: str) -> str:
    s = str(s).strip().strip("[]")
    s = s.split("|")[0].split("#")[0]
    return re.sub(r"[^a-z0-9-]+", "-", s.lower()).strip("-")


# =================================================================================================== sections + hybrid
def page_sections(w: Wiki, slug: str) -> list[dict]:
    """A page cut at its ## headings (### for long sections), each with the raw sources its [^rN] keys cite."""
    fm, body = w.page(slug)
    body = re.sub(r"\n## References\n.*$", "", body, flags=re.S)
    p = w.pages[slug]
    parts, cur, title = [], [], "Lead"
    for ln in body.splitlines():
        m = re.match(r"^(##|###) (.+)$", ln)
        if m and (m.group(1) == "##" or sum(len(x) for x in cur) > 1500):
            if "".join(cur).strip():
                parts.append((title, "\n".join(cur)))
            title, cur = m.group(2).strip(), []
        else:
            cur.append(ln)
    if "".join(cur).strip():
        parts.append((title, "\n".join(cur)))
    out = []
    for i, (t, txt) in enumerate(parts):
        if t.lower() in ("see also",):
            continue
        keys = sorted(set(REF.findall(txt)), key=lambda k: int(k[1:]))
        lead = f"{p['title']}: {p.get('summary', '')}"
        out.append({"id": f"wiki:{slug}#{i}", "page": slug, "title": p["title"], "section": t,
                    "text": txt.strip(), "embed_text": f"{lead}\n{t}\n{txt.strip()}", "audience": p["audience"],
                    "sources": w.page_sources(slug, keys) if keys else w.page_sources(slug)[:3],
                    "status": p.get("status")})
    return out


def section_item(s: dict) -> dict:
    return {"id": s["id"], "file": f"wiki_v4/pages/{s['page']}.md", "text": f"[[{s['page']}]] {s['title']} > "
            f"{s['section']}\n{s['text']}", "loc": {}, "cite": f"wiki [[{s['page']}]] {s['title']} > {s['section']}",
            "sources": s["sources"], "meta": {"title": s["title"], "status": s.get("status")}}


class SectionIndex:
    """RAG over the wiki: every page section embedded (the same embedding model and BM25 as the RAG half), fused with
    RRF. Permissions filter before ranking: an HR page's sections are not candidates for a non-HR role."""

    def __init__(self, w: Wiki, embed: str = "bge-small", cache: pathlib.Path | None = None, qcache: str | None = None):
        import numpy as np

        from . import rag

        self.w, self.embed_name = w, embed
        self.sections = [s for slug in sorted(w.pages) for s in page_sections(w, slug)]
        self.bm25 = rag.BM25([s["embed_text"] for s in self.sections])
        cache = cache or (w.root / "_index" / f"sections_{embed}.npy")
        ids_path = cache.with_suffix(".ids.json")
        ids = [s["id"] + "|" + str(len(s["embed_text"])) for s in self.sections]
        if cache.exists() and ids_path.exists() and json.loads(ids_path.read_text()) == ids:
            self.vecs = np.load(cache)
        else:
            self.vecs = rag.Embedder(embed).passages([s["embed_text"] for s in self.sections])
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache, self.vecs)
            ids_path.write_text(json.dumps(ids))
        self._qcache_path = w.root / "_index" / (qcache or f"queries_{embed}.jsonl")
        self._qcache = {}
        for qp in sorted((w.root / "_index").glob(f"queries_{embed}*.jsonl")):
            for line in qp.open():
                d = json.loads(line)
                self._qcache[d["q"]] = d["v"]

    def qvec(self, q: str):
        import numpy as np

        from . import rag

        if q in self._qcache:
            return np.array(self._qcache[q], dtype=np.float32)
        v = rag.Embedder(self.embed_name).query(q)
        self._qcache[q] = [round(float(x), 6) for x in v]
        with self._qcache_path.open("a") as f:
            f.write(json.dumps({"q": q, "v": self._qcache[q]}) + "\n")
        return v

    def search(self, q: str, role: str = C.DEFAULT_ROLE, k: int = 6, pool: int = 40, max_per_page: int = 2) -> list[dict]:
        import numpy as np

        from . import rag

        mask = np.array([s["audience"] != "hr" or role in C.HR_ROLES for s in self.sections])
        dense = self.vecs @ self.qvec(q)
        dense = np.where(mask, dense, -9.0)
        d_rank = [int(i) for i in np.argsort(-dense)[:pool]]
        b_rank = [i for i, _ in self.bm25.search(q, pool, mask=mask)]
        fused = rag.rrf([d_rank, b_rank])
        top, per_page = [], {}
        for i in sorted(fused, key=lambda i: -fused[i]):  # at most max_per_page sections of one page
            pg = self.sections[i]["page"]
            if per_page.get(pg, 0) < max_per_page:
                top.append(i)
                per_page[pg] = per_page.get(pg, 0) + 1
            if len(top) == k:
                break
        return [{**self.sections[i], "score": round(fused[i], 5), "rank": r + 1} for r, i in enumerate(top)]


_SI: dict = {}


def wiki_search(question: str, user: str = "ECLARKE", k: int = 6, role: str | None = None,
                wiki_dir: pathlib.Path | str = WIKI_DIR) -> list[dict]:
    """Search Northbridge's wiki: k cited page sections, best first, no LLM call (RAG over wiki sections, BM25 + bge-small,
    RRF). Each: {"page", "title", "section", "text", "citations": [{"file", "loc"}], "score", "rank", "url"}.
    HR-only pages are filtered out before ranking unless the user's role is an HR role."""
    role = role or role_for(user)
    key = str(wiki_dir)
    if key not in _SI:
        _SI[key] = SectionIndex(Wiki(wiki_dir))
    t0 = time.perf_counter()
    hits = _SI[key].search(question, role=role, k=k)
    ms = round((time.perf_counter() - t0) * 1000, 1)
    return [{"page": h["page"], "title": h["title"], "section": h["section"], "text": h["text"],
             "citations": h["sources"], "score": h["score"], "rank": h["rank"], "status": h.get("status"),
             "url": f"wiki_v4/pages/{h['page']}.md", "ms": ms} for h in hits]


class Hybrid:
    """Search the wiki's sections first (no LLM), then let the navigator open pages / sources from there (index-guided)."""

    def __init__(self, w: Wiki, llm, si: SectionIndex, k: int = 8, max_calls: int = 3, navigate: bool = True):
        self.w, self.si, self.k = w, si, k
        self.nav = Navigator(w, llm, max_calls=max_calls)
        self.navigate = navigate

    def method(self, question: str, role: str) -> dict:
        t0 = time.perf_counter()
        hits = self.si.search(question, role=role, k=self.k)
        t_search = time.perf_counter() - t0
        if not self.navigate:
            return {"items": [section_item(h) for h in hits], "seconds": round(t_search, 4), "nav_calls": 0,
                    "chain": [{"step": "search", "what": [f"{h['page']} > {h['section']}" for h in hits]}],
                    "search_ms": round(t_search * 1000, 1)}
        out = self.nav.navigate(question, role, start=hits)
        out["seconds"] = round(time.perf_counter() - t0, 3)
        out["search_ms"] = round(t_search * 1000, 1)
        return out


# =================================================================================================== file-back
def file_back(w: Wiki, question: str, answer: str, items: list[dict], cited: list[int], asked_by: str = "ECLARKE",
              slug: str | None = None) -> dict:
    """Write a good answer back into the wiki as an `answer` page, linked from the pages it used, and log it."""
    slug = slug or "qa-" + re.sub(r"[^a-z0-9]+", "-", question.lower()).strip("-")[:60].rstrip("-")
    used_items = [items[n - 1] for n in cited if 0 < n <= len(items)] or items[:3]
    pages_used = [i["id"].split(":", 1)[1].split("#")[0] for i in used_items if str(i["id"]).startswith("wiki:")]
    refs, lines = {}, []
    for it in used_items:
        for s in (it.get("sources") or [{"file": it["file"], "loc": it.get("loc") or {}}])[:6]:
            k = f"r{len(refs) + 1}"
            loc = s.get("loc") or {}
            lt = ", ".join(x for x in [f"sheet {loc['sheet']}" if loc.get("sheet") else "",
                                       f"row {loc['row']}" if loc.get("row") else "",
                                       f"p. {loc['page']}" if loc.get("page") else "",
                                       loc.get("section") or ""] if x) or "whole file"
            if (s["file"], lt) not in {(r["file"], r["loc_text"]) for r in refs.values()}:
                refs[k] = {"file": s["file"], "loc_text": lt, "page": loc.get("page"), "sheet": loc.get("sheet"),
                           "section": loc.get("section")}
    ans = re.sub(r"\[(\d+(?:\s*[,;]\s*\d+)*)\]", "", answer).strip()
    keys = " ".join(f"[^{k}]" for k in refs)
    body = (f"Filed answer to a staff question ({asked_by}, {now()[:10]}).\n\n## Question\n\n{question}\n\n## Answer\n\n"
            f"{ans} {keys}\n\n## Pages used\n\n" + "\n".join(f"- [[{p}]] {w.pages[p]['title']}" for p in pages_used
                                                              if p in w.pages))
    from .wiki_build import render_page

    page = {"title": f"Q: {question}", "type": "answer", "summary": f"Filed answer: {question[:120]}",
            "audience": "staff", "status": "current", "sources": sorted({r['file'] for r in refs.values()}),
            "body": body, "infobox": {"Asked by": asked_by, "Filed": now()[:10], "Pages used": str(len(pages_used))},
            "created": now()[:10], "updated": now()[:10]}
    (w.root / "pages").mkdir(exist_ok=True)
    (w.root / "pages" / f"{slug}.md").write_text(render_page(slug, page, refs))
    for p in pages_used:  # "what links here": each page it used now links to the filed answer
        if p in w.pages:
            path = w.root / w.pages[p]["path"]
            t = path.read_text()
            add = f"- [[{slug}]] Filed answer: {question}"
            if add not in t:
                t = t.replace("\n## References\n", f"\n## Filed answers\n\n{add}\n\n## References\n", 1) \
                    if "## Filed answers" not in t else t.replace("## Filed answers\n\n", f"## Filed answers\n\n{add}\n", 1)
                path.write_text(t)
            w.pages[p]["links_out"] = sorted(set(w.pages[p]["links_out"]) | {slug})
            w._texts.pop(p, None)
    w.pages[slug] = {"title": page["title"], "type": "answer", "summary": page["summary"], "audience": "staff",
                     "status": "current", "sources": page["sources"], "links_out": pages_used,
                     "refs_used": list(refs), "conflicts": [], "infobox": page["infobox"], "path": f"pages/{slug}.md",
                     "refs": {k: {**v, "verified": None} for k, v in refs.items()}}
    (w.root / "manifest.json").write_text(json.dumps(w.manifest, indent=1, ensure_ascii=False))
    write_index(w.root, w.manifest)
    with (w.root / "log.md").open("a") as f:
        f.write(f"## [{now()}] file-back | {slug} | {question} | linked from {', '.join(pages_used)}\n")
    return {"slug": slug, "pages_used": pages_used, "refs": len(refs)}
