# L3 v5 · Parsing, one real file at a time · speaker notes

Replaces old slides 18–19 ("Parse by Document Type" and its class question). The audit slides before it stay.
Every image is a real render of a real file from the dump (Modal: `experiments/v5_parse_modal.py`); every text panel is
a parser's real output from the course code (`ledgerline/course/l3/corpus.py`, `parse_file(..., parser="plain" | "structured")`).
Data: `v5/parse_data.js`, written by `experiments/v5_parse_build.py` from `experiments/logs/v5_parse*.json`.

## Part slide · "What does a program actually see when it opens a file?"
We have counted the dump: 693 files. Every one of those counts was made on the structured parser's text. Now we open
files one by one and look at what a program really gets out of each. The rule for this section: one file, one
question, three views (the file as people see it, a naive extraction, our structured parser).

## A Table in a PDF
Q-605 asks for a purchase executive's approval limit. That is Emma's role.
On the left, page 1 of the Approval Matrix v3.0 as it prints (PyMuPDF render, zoomed on § 3).
[click] Naive: `pypdf` `extract_text`, which is what parser="plain" does. Look at the table: every cell on its own
line. The headers (green) appear once; "£250,000" (orange) sits between "Purchase executive" and "PUR-SR". A reader,
human or model, has to guess which line it belongs to. The words survived. The row did not.
[click] Structured: `pdfplumber` finds the table and writes each row as "a | b | c". The header row and the PUR-EXEC row
are boxed on the page and highlighted in the text. The unit also knows its place: page 1, § 3. The limits.
[click] The answer: £250,000 gross. Note that the needle test in the audit counts this fact as "visible" in both
parsers: the words are there. What plain loses is the association. Keep that in mind: a metric that checks words can
miss a problem in structure.

## Headings Become Units
Document D, the Purchase Policy v4.1, page 2. Emma's question.
[click] Naive, the end of page 2 and the start of page 3 as plain hands them on. In orange: the running header and
footer, "Northbridge Cycles Ltd / POL-PUR-001 | v4.1 / Internal. Uncontrolled when printed. / Page 2 of 4". They sit
between the last line of page 2 and the first of page 3, so a chunk cut across the page join carries them in the middle
of the text. Boxed on the page in orange.
[click] Structured: the headings (blue boxes) start units. Page 2 becomes six units, each with page and section and its
token count. The whole policy is 26 units, 2,178 tokens (the running example's numbers).
[click] § 6 (green): the unit that holds § 6.2 and § 6.4, zoomed so you can read it. Right: what a chunk of § 6 begins
with in our chosen configuration (structured, structure-aware, 200 tokens, 15% overlap): the context header with the
document, version and effective date, then the heading path. Its cite: POL-PUR-001 v4.1, p.2, § 6. Supplier
qualification. This is where every later chunk starts from.
[click] The answer from D alone: § 6.2 and § 6.4, both in that unit.

## A Scan Is a Picture
The paper approval of PO/2026/00452, one page scanned at 200 dpi. Left: the whole page; middle: the top, zoomed.
Q-015: which approval did the paper copy record?
[click] Naive: nothing. 0 characters. The PDF is one 1654 × 2339 image with no text layer. To plain, this file is
empty, and so is every scan: the audit counted 0 scan tokens with plain against 534 with OCR.
[click] Structured: `corpus.py` runs Tesseract 5.3 on the page image (0.43 s here). The text is nearly perfect.
[click] Found: "PO/2026/00452" and "Daniel Okafor" (blue, boxed on the scan). And one error, in orange: the signature
became the words "of Ne". OCR reads every mark as letters. It also never says "this is a signature".

## A Poor Scan: Tesseract or a Vision Model
Be honest with the class: the six scans in the dump are clean. Real scans are often not. So we made a poor copy of
the same page ourselves: rotated 1.5°, half resolution, blurred, speckled, low-quality JPEG. Same question.
[click] Tesseract on the poor copy (0.40 s): "PO/2026/00852", "Danlel Okafor", "Arenoyal", "Trem", "114,00", and the
last line became "Sn ema saan". The two words the question needs are both wrong, boxed on the image. Search for 00452
and this page is never found.
[click] gemini-3.8-flash, given the same image (Google's API, temperature 0, our prompt "transcribe exactly, mark
signatures and stamps in brackets"): every line right, and "[signature]" where Tesseract wrote letters. 6.99 s.
[click] The cost. This page: Tesseract 0.40 s, CPU, no fee. The vision model 6.99 s and $0.0042 (1,167 tokens in, of
which 1,092 are the image; 100 out plus 688 thinking tokens, billed as output; OpenRouter's list price for the same
model, fetched with the run). All six scans, clean and poor, 12 runs: the golden fact was found by Tesseract in 6 of 6
clean copies and 4 of 6 poor ones; by the vision model in 6 of 6 and 6 of 6. On average 0.4 s against 7.7 s and
$0.0040 a page. And it is not a pure copier: on the poor VAT memo it added Markdown `**` we did not ask for. A vision
model can also write what is not there, so check it on pages you know.

## A Row Without Its Headers
The item master, sheet Items, rendered by LibreOffice (the real cells; column letters and row numbers as in Excel).
Q-401: what is the reorder level of BAT-500?
[click] Plain: row 5 as values only, its own unit. Which of "1 1 3000 600 42" is the reorder level? Row 4, the headers,
is a different unit, so this row never meets them. Across the dump: 22,003 spreadsheet rows indexed without headers.
[click] Structured: one unit per row, "column: value", with the sheet's title lines as context. Headers boxed.
[click] reorder_lvl: 3000 (red boxes on the sheet: the header cell and the value). The answer: 3,000. This is also why
the structured text costs about 40% more tokens: the headers are repeated on every row, and that is what makes a row
findable.

## An E-mail on Disk
Brightcell's quotation to Emma, the very quote in her question. Left: the file exactly as it is on disk, which is also
what plain indexes.
[click] It is quoted-printable. Every "=" at a line end is a soft break ("per p=" / "ack"); "=C2=A3" is the two UTF-8
bytes of "£". The mail gateway encoded it that way to send it. In the whole dump plain keeps 790 such soft breaks.
[click] Structured: Python's e-mail parser decodes it. We keep Subject, From, To and Date (green) and the date becomes
the unit's effective date (2026-10-22); we drop Message-ID, X-Mailer, Content-Type and MIME-Version (struck through).
We keep the signature: it says who made the offer.
[click] The quote: £104.00 per pack, delivered (DAP) to Manchester; and the UN 38.3 report "expected in December
2026". In the raw file the string "£104.00" does not occur at all, so the audit's check finds this fact only with the
structured parser.

## A Word Table Goes Missing
The superseded Approval Matrix v2.0 (2024), a Word file, rendered by LibreOffice. Q-605 again, now for the history.
[click] Plain reads paragraphs only (`python-docx` `document.paragraphs`). Look: "3.1 Each role's approval limit,
gross including VAT:" and then straight "4. Who may not approve". Both tables are gone: the limits, and the box that
says SUPERSEDED (orange on the page). In the dump plain drops 35 Word tables; the onboarding checklist NBC-F-113 keeps
30 of its 239 tokens.
[click] Structured walks the body in order, tables included, and splits at headings: the document box and § 3.
[click] The old limit, £200,000, and "Status | SUPERSEDED". The answer to Q-605's history needs exactly this: now
£250,000 (v3.0); in 2024 £200,000.

## An Old Intranet Page
The 2016 intranet export, in a browser as it was exported (its stylesheet was not exported, so it looks bare).
[click] Plain indexes the markup: banner and menu (orange), 852 tokens. The banner and the 8 menu links repeat on all
23 pages of the export, so every page carries "How to raise an order" and "Approval limits", whatever it is about.
[click] Structured drops the banner and the navigation, writes the table as rows and splits by heading: 416 tokens.
[click] 2016: £150,000 on the net value before VAT. Three answers to one question, in three formats.

## Metadata the Parser Keeps
The three answers to Q-605, side by side, as `corpus.file_meta` returned them.
v3.0 PDF: CURRENT, effective 2026-04-01, says £250,000 gross.
[click] v2.0 Word: SUPERSEDED, superseded = true. Every chunk header of this file says "SUPERSEDED / old copy".
[click] The 2016 page: empty. Nothing in the file says it is old; only "(2016)" in its title. A parser keeps only what
a file states. Here a human rule is needed (for example: everything in `intranet_export_2016/` is history).
[click] Two more from the dump. T&E policy v3.0: future = true, "NOT YET IN FORCE (from 2027-01-01)". HR-CONF-007
salary bands: confidential = true, and `may_read` for Emma's role is false: it is removed before ranking, not after.
These fields become labels and filters in Section 6.

## Parsing, Format by Format
The table puts the seven files side by side: what went wrong, what our parser does, and tools that do the same job.
[click] Five tools, described only as their own documentation describes them (checked 4 Nov 2026): Docling (open
source, from IBM Research; PDF, Office, HTML, images; layout, reading order, tables, OCR; Markdown or JSON);
Unstructured (open source; one partition function per format; `hi_res` uses a layout model, `ocr_only` runs
Tesseract); LlamaParse (LlamaIndex's hosted parser, 130+ file types to Markdown, text or JSON, using generative
models); Azure Document Intelligence (layout model: tables, section headings, page headers and footers, Markdown
output); and a vision LLM, as measured here. We wrote our own in `corpus.py` so every decision is visible. In a client
project, try a tool first, and keep the metadata rules: no tool knows Henrik's folders.

## Class question · "Where would you spend a vision model?"
Six scans among 693 files. Let them answer 1–4 with a reason. A good answer: 3. Tesseract is free and fast and read
all six clean scans; spend the model on scans and on any page where Tesseract is unsure (its word confidences are
low: on the poor copy, "Danlel" had confidence 14 and "PO/2026/00852" 33). Every page of every file (1) costs time and
money for files that already have a text layer.

## Check: Which Unit Answers?
Q-436: reorder level of BAT-625-INT, and is it a lithium-cell part? Read both units aloud.
[click] Only the structured one: reorder level 200, cell_safety 1, so yes. In plain, "1 1 200 20 42" could be any five
columns.

## Check: Keep, Decode or Drop?
Three real snippets. Ask the class for each before clicking.
[click] "Internal. Uncontrolled when printed. / Page 2 of 4": drop it, a running footer.
[click] "=C2=A3119.00 from=": decode it, quoted-printable: "£119.00 from 1 October 2026".
[click] "Status | SUPERSEDED": keep it, as metadata: superseded = true, in every chunk header, and a filter can use it.
