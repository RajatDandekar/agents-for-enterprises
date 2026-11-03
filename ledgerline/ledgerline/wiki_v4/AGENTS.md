# AGENTS.md: the schema of Northbridge's wiki

This file is the wiki's constitution. Every agent that ingests, queries or lints the wiki reads it first.
It follows Karpathy's "LLM Wiki" pattern (gist, 4 Apr 2026): **raw sources** (immutable), **the wiki**
(markdown pages the LLM owns) and **this schema**. Obsidian is the IDE, the LLM is the programmer, the wiki
is the codebase.

Today, for every rule below, is **Monday 26 October 2026, 09:00 GMT** (the date the dump was taken).

## 1. The three layers

| Layer | Where | Who writes it |
|---|---|---|
| Raw sources | `northbridge-docs/` (699 files: PDF, DOCX, XLSX, CSV, YAML, XML, EML, MD, HTML, scans) | nobody: never edited |
| The wiki | `wiki_v4/pages/*.md`, `wiki_v4/index.md`, `wiki_v4/log.md` | the LLM (ingest, file-back, lint fixes) |
| The schema | `wiki_v4/AGENTS.md` (this file) | people, with the LLM's suggestions |

## 2. Page types and slugs

One page per entity or topic. The slug is the file name (`pages/<slug>.md`) and the link target. Slugs are
lower-case, words joined by `-`, and built from the document's or record's own code wherever one exists, so
that two sources that name the same thing land on the same page.

| Type | Slug | One page per | Example |
|---|---|---|---|
| `policy` | the document code | policy or amendment | `pol-pur-001`, `amd-sup-2026-02` |
| `procedure` | the document code | SOP (forms live on their SOP's page) | `sop-pur-001` |
| `manual` | the document code | vendor manual or reference (an overview that links to screens, errors and processes) | `man-pur-72` |
| `release` | `rn-` + version | release or patch note, and the 6.x history | `rn-7-2-3-p4`, `rn-7-3-preview` |
| `screen` | `screen-` + screen code | Ledgerline screen | `screen-pur-po-01` |
| `service-group` | `services-` + module + object | group of services on one object | `services-pur-po` (po_save, po_fetch, po_release …) |
| `error` | `err-` + code (warnings `w-…`) | message code that a user manual, SOP, training card, release note, meeting or e-mail explains | `err-po-0412`, `w-cc-114` |
| `error-list` | `errors-` + code prefix | list of codes with one prefix: a `###` per code with message, cause, remedy, raised by; links to its `err-` page if one exists | `errors-po` (ERR-PO-*), `errors-sup` |
| `supplier` | `sup-` + supplier code; `sup-` + name if not in the master | supplier discussed in a narrative source | `sup-vc-ein-0042`, `sup-brightcell-energy` |
| `item-family` | `items-` + code prefix | family of items (`BAT-*`, `MTR-*` …) | `items-bat` |
| `person` | `user-` + user id (`person-` + name if no id) | person who appears in a narrative source | `user-eclarke` |
| `role` | `role-` + role code | Ledgerline role and its approval limit | `role-pur-exec` |
| `cost-centre` | `cc-` + code | cost centre | `cc-prd-07` |
| `data-source` | `data-` + short name | structured file (master, extract, register, dictionary) | `data-supplier-master` |
| `topic` | `topic-` + name | idea that crosses documents (a synthesis or comparison) | `topic-un-38-3-certificates`, `topic-tax-codes` |
| `decision` | `decision-` + date + name | decision made in an e-mail or meeting that changes how work is done | `decision-2026-06-02-ap-cut-off` |
| `answer` | `qa-` + short name | good answer filed back from a query | `qa-brightcell-battery-packs` |

Do not create a page for an entity that only appears as a row in a table; the `data-source` page covers it.
Reference catalogues (the error-code reference, the service reference, service definitions, the data dictionary)
feed the list and group pages (`errors-…`, `services-…`); a code gets its own `err-` page only from a narrative
source that explains it.

## 3. What every page contains

```
---
title, type, slug, summary (one line for the index), audience (staff | hr), sources (raw files),
status (current | superseded | future | mixed), created, updated
---
Lead: two to four sentences that answer "what is this and what matters about it today". No heading.
Infobox: a small key/value table (code, owner, version, effective date, status …) where the type has one.
## Sections                  the facts, grouped as the type needs (see below)
## Versions and conflicts    only when sources disagree, are superseded or are not in force yet
## See also                  [[links]] to the closest pages
## References                numbered raw-source references (written by the build, not by hand)
```

Required sections by type: policy (*Clauses*: one `###` per clause, in the policy's own numbering);
procedure (*Steps*, *Forms and screens*); error (*Meaning*, *Cause*, *How to fix*, *Raised by*);
screen (*Fields*, *Keys and services*, *Messages*); service-group (*Services*: one `###` per service with
required fields, optional fields, errors and the source file); supplier (*Record*, *Certificates*,
*Rate contracts*, *Notes*); data-source (*What it holds*, *Columns*, *How to look up a row*, *Size*);
release (*Changes*, *Effect at Northbridge*).

## 4. Citations

Every sentence that states a fact ends with a reference to the raw source it comes from: `[^r3]`. The
References section maps each key to one raw location:

```
[^r3]: 01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf, p. 2, §6. Supplier qualification
[^r7]: 05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx, sheet 2026-27, row VC-EIN-0042/BAT-500
[^r9]: 09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml, body
```

Locations: PDF = page (+ section heading); DOCX/MD/HTML = section heading; XLSX = sheet + row key or cell;
CSV = row key; YAML/XML = field path (`request.fields`, `errors`); EML = subject/body. A citation always
points to a raw source, never to another wiki page. Never invent a reference: if no source says it, do not
write it.

## 5. Links

* Link the first mention of every entity or document that has a page: `[[sup-vc-ein-0042|Voltway Cells]]`.
* Link only to slugs that exist in the registry or that follow the slug rules above (the build checks).
* Every page must be reachable: at least one other page or the index links to it (lint reports orphans).
* A page that mentions a document code links to that document's page, not to the file.

## 6. Versions, supersession and dates

Sources disagree. The wiki says which one wins today and keeps the loser visible, with its date.

1. **In force today wins.** A document's *Effective* date must be on or before 26 Oct 2026. A later
   effective date ("ISSUED", "PREVIEW", "effective 2027-01-01") means **not yet in force**: state today's
   rule first, then "From <date>, <new rule> (<doc>)".
2. **Newer replaces older.** A higher version of the same document code, an amendment in force, or a
   release note that changed system behaviour replaces the older text. Files in `old/` folders, files whose
   status is SUPERSEDED, and older exports are superseded.
3. **E-mails and meeting decisions** from an owner (manager, controller, change board) override a SOP
   until the SOP is reissued; say so and cite both.
4. **The system versus the paper.** When a manual describes behaviour that a later patch changed, say what
   Ledgerline does now (the patch) and that the manual was not updated.
5. Record every case under **Versions and conflicts** as: today's rule, the older or future rule, the
   sources and dates, and the kind (`superseded`, `contradiction`, `future_dated`, `email_overrides_sop`,
   `near_duplicate`, `duplicate`, `rule_not_in_policy`).

## 7. Permissions

Files under `01_policies/HR/CONFIDENTIAL/` are restricted to HR (group NBC-HR-CONF). Facts from them go only
on pages with `audience: hr`, which are listed in `restricted/index.md`, never in `index.md`, and never
linked from staff pages. A staff page may say that a confidential HR document exists and who may read it,
nothing more.

## 8. Structured data: summaries and pointers, not copies

Masters and extracts (item master 2,186 rows, rate contracts 3,226, PR/PO/GRN/AP extracts ~25,000 rows,
400 service definitions) are not copied into the wiki. Each structured file gets one `data-source` page:
what it holds, its sheets and columns, how many rows, how to look a row up (key column), and what it is
for. Entity pages (a supplier, an item family, a cost centre) carry only the rows of their own entity, with
a cell or row reference. To answer "what is the reorder level of X", the reader follows the data-source
page's pointer to the raw sheet.

## 9. Operations

**Ingest** (one source at a time): read the source; write a short source note; decide which pages it
touches (create or update); add its facts with references; record conflicts; append one line to `log.md`:
`## [<timestamp>] ingest | <file> | +<created> ~<updated> | <slugs>`.

**Query**: read `index.md` first; open the pages whose summaries fit; follow `[[links]]`; open the raw source
when a page points to a table or the exact wording matters; answer with citations to raw sources. Say "not
in the documents" when no page or source holds the answer. A good answer may be **filed back** as an
`answer` page, linked from the pages it used, and logged: `## [<ts>] file-back | qa-<slug> | <question>`.

**Lint**: report contradictions between pages or sources, stale or superseded claims stated as current,
future-dated rules stated as current, orphan pages, broken or missing links, uncited claims, and citations
whose quoted text is not found at the cited location. Log: `## [<ts>] lint | <n> findings`.

## 10. `index.md` and `log.md`

`index.md` is the catalogue, read first by every query: one line per page, grouped by type,
`- [[slug]] Title: summary`. It is rebuilt after every ingest. `log.md` is append-only: one line per ingest,
file-back and lint, oldest first, so the wiki's history can be replayed.
