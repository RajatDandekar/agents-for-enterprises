# L3 v5 · Parsing, one real file at a time · speaker notes

Replaces old slides 18–19 ("Parse by Document Type" and its class question). The audit slides before it stay.
Every image is a real render of a real file from the dump (Modal: `experiments/v5_parse_modal.py`); every text panel is
a parser's real output from the course code (`ledgerline/course/l3/corpus.py`, `parse_file(..., parser="plain" | "structured")`).
Data: `v5/parse_data.js`, written by `experiments/v5_parse_build.py` from `experiments/logs/v5_parse*.json`.
Revised 5 Nov 2026 after Dr. Rajat Dandekar's review (`v5/REVIEW_2026-11-05.md`): slides 20, 24, 26 and 31 reworked, "Metadata the
Parser Keeps" removed (the store section teaches metadata and filters), "Parsing, Format by Format" replaced by the tools guide,
and a Docling slide added (Docling run for real: `experiments/v5_parse_docling.py` → `logs/v5_parse_docling.json`). The naive
HTML reading on slide 26 is BeautifulSoup run for real (`experiments/v5_parse_modal.py::html` → `logs/v5_parse_html.json`).

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
Document D, the Purchase Policy v4.1, page 2. On top: Emma's question, the running question of the lecture: "Can I buy the
battery packs from Brightcell Energy? They quote £104." Keep it in mind: we are looking for the part of D that answers it.
[click] Naive (parser="plain"): page 2 is one unit of 549 tokens. Read it as a list of what is inside: § 5 to § 9 and
Appendix A, and at the end, in orange, the page's header and footer ("Northbridge Cycles Ltd / POL-PUR-001 | v4.1 /
Internal. Uncontrolled when printed. / Page 2 of 4"), boxed in orange on the page. So the passage Emma needs is somewhere
in the middle of 549 tokens, with page furniture glued on. (Each body is cut to "⋯ n clauses" so it fits; the lines are the
real headings in plain's text.)
[click] Structured: the headings (blue boxes) start units. Page 2 becomes six units, each with page and section and its
token count. The whole policy is 26 units, 2,178 tokens (the running example's numbers).
[click] Which unit answers Emma? § 6 (green, in both lists and on the page). Why a unit called "Supplier qualification"?
Brightcell would be a new supplier, and battery packs are a lithium-cell part: § 6 is the part of the policy about which
suppliers we may buy from. The page, zoomed: 6.2 (lithium-cell parts only from a supplier with a valid UN 38.3 certificate
on file, checked before the first order) and 6.4 (a cheaper quote from a new supplier is not, by itself, a reason to change
supplier for a lithium-cell part), boxed in green. Read the two clauses aloud from the page.
[click] The answer from D alone: § 6.2 and § 6.4, both in one unit, page 2, § 6, 160 tokens. (D never says "Brightcell":
whether Brightcell holds a certificate needs other files; the e-mail two slides on says its report is being renewed.)

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
what parser="plain" indexes (310 tokens). Ask: where is "£104" in it? It is not there.
[click] 1. One line of the body as stored: "mounting: =C2=A3104.00 per p=". The "=C2=A3" (orange, also on the left) is where
the "£" should be.
[click] 2. In this encoding, "=" followed by two hexadecimal digits is one byte. Hexadecimal digits are 0–9 then A–F; two of
them run from 00 to FF, which is 0 to 255, one byte. So "=C2" is the byte C2 (194) and "=A3" the byte A3 (163).
[click] 3. Why two bytes for one character? "£" is character number 163. UTF-8 stores characters 0 to 127 (plain ASCII) in
one byte and anything above in two or more; for "£" those two bytes are C2 A3. So "=C2=A3104.00" reads "£104.00". (All of
this is computed from the file with Python's quopri in the build script, not typed in.)
[click] 4. An "=" at the very end of a line is a soft break: the line was cut there, not by the writer. Delete the "=" and the
line break: "per p=" + "ack," is "per pack,". This file has 6 soft breaks (orange on the left); the whole dump, 790.
[click] 5. Why does a gateway write text like this? E-mail was built for plain ASCII text in short lines. So the mail
gateway (the X-Mailer header: NBC Mail Gateway 4.2) writes every byte outside ASCII as =XX and cuts long lines, here at 78
characters, with a soft break. It says so in the header: Content-Transfer-Encoding: quoted-printable (blue).
[click] Decoded vs raw: Python's e-mail parser undoes all of it, which is what our structured parser does (229 tokens). We
keep Subject, From, To and Date (green); the date becomes the unit's effective date (2026-10-22). We drop Message-ID,
X-Mailer, Content-Type and MIME-Version (struck through on the left). We keep the signature: it says who made the offer.
[click] The quote: £104.00 per pack, delivered (DAP) to Manchester; and the UN 38.3 report "expected in December 2026". In
the raw file the string "£104.00" does not occur at all, so the audit's check finds this fact only with the structured parser.

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
The 2016 intranet export, in a browser as it was exported (its stylesheet was not exported, so it looks bare). Ask: what
does a "normal" HTML parser give us?
[click] The usual first try is BeautifulSoup's get_text() (bs4 4.12.3, run on Modal on the real file; only blank lines
removed so it fits). The tags are gone, but every piece of text stays: the page title from the head, the banner and the
8 menu links (orange, and boxed on the page): 458 tokens.
[click] Two consequences. The table cells glue together: "RoleLimit", "Purchase executive£150,000" (get_text puts nothing
between cells). And search: the banner and the menu are on all 23 pages of the export, so every page carries "Approval
limits", "How to raise an order", "Supplier list". Searched for "Approval limits", get_text's text matches 23 of 23 pages;
our structured text matches 1, the right one. (trafilatura, which keeps only the main text, also matches 1; our plain
baseline, which indexes the raw markup, 852 tokens, matches 23.)
[click] Structured: we drop the banner and the navigation, write the table as rows "Role | Limit", and split by heading:
2 units, 416 tokens. The table is boxed on the page.
[click] 2016: £150,000 on the net value before VAT (boxed in green). Three answers to Q-605 in three formats (PDF v3.0
£250,000 gross; Word v2.0 £200,000; this page £150,000 net): which one is in force is a question of metadata, which the
store section takes up.

## Docling, on Our Files
Docling is the parser people reach for most often today, so we ran it for real on our files (docling 2.147.0, pip install
docling in a Modal CPU image, 4 vCPU, no GPU; models downloaded when the image was built; `experiments/v5_parse_docling.py`).
What it is: open source, from IBM Research. A layout model finds headings, lists, tables, page headers and footers; a table
model rebuilds each table's cells; OCR runs where a page is a picture (here the OCR engine was RapidOCR, the one Docling's
"auto" setting found installed). Out comes Markdown or JSON. The code is the three lines on the slide. Left: the same page as
"A Table in a PDF", Approval Matrix v3.0, page 1, § 3.
[click] Docling's real Markdown for § 3 (3.2 to 3.4 cut with ⋯). The table is a Markdown table with its header row on top
(green): exactly what a model needs to read a row.
[click] What it got right and wrong next to our parser on the same pages. Right: tables as Markdown tables (4 in D); the page
headers and footers recognised as such (16 on D's 4 pages) and left out of the Markdown; the heading "Does an order require a
second approval if the purchase request was already signed off?", printed over two lines, kept whole, where our parser split
it in two; on the scan, the PO number and "Daniel Okafor" read, and the signature left as an image (Tesseract wrote "of Ne").
Wrong: the § 3 table moved below 3.4, away from 3.1 that introduces it (orange; ours keeps it under 3.1); on the scan, words
glued together ("BAT-500Quantity: 1,800", "VC-EIN-0042Voltway Cells").
[click] Time, second run of each file: 5.85 s for D's 4 pages, 6.84 s for the 2-page matrix (not on the slide), 1.65 s for the
scan with OCR; our structured parser takes 0.33 s on D (Modal, 4 vCPU, `logs/v5_parse_explore.json`). The very first call also
loads the models: 24.73 s. Free and local: no page leaves the machine. Message: try Docling first on a new project; it does
in three lines most of what our parser does by hand, and check its reading order on your tables.

## Parsing Tools, Format by Format
The guideline card: the first step of any RAG application is to read each file well. One row per file type, the trap we saw
in this section, the tool to reach for first, and what to try when it is not enough. Read it row by row.
PDF with text: Docling (layout, reading order, tables as Markdown; free, local); PyMuPDF for fast text, word positions and
page images (free, AGPL licence), pdfplumber for words and table cells with positions (free; our parser uses it).
Scanned PDF: Tesseract, 0.4 s a page here, read 6 of 6 clean scans (free, local); Docling also runs OCR (1.65 s on our scan).
Poor scans, stamps, handwriting: a vision LLM (Gemini Flash): read 6 of 6 poor copies; $0.0040 and 7.7 s a page on average in
our 12 runs (paid API). Only for pages Tesseract is unsure of, and check it on pages you know.
Spreadsheet: openpyxl or pandas, and write each row as "column: value" (free). E-mail: Python's email module, built in.
Word: python-docx, walking the body in order so tables are included (free). Web page: trafilatura keeps the main text and writes
tables as Markdown (1 of 23 pages match "Approval limits", like ours); BeautifulSoup when you know the page and pick the content
block yourself. Docling also reads .docx and .xlsx.
[click] Hosted options, if you would rather not run a parser: Unstructured (open source, also a paid API), LlamaParse (paid API),
Azure Document Intelligence (paid API). No prices on the slide: we did not run them. Try your worst files first.
One more thing every parser should keep: what each file says about itself (date, version, status, confidential). The store
section ("Where the vectors live") uses these as filters; we do not teach filters here.

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
Before a parser indexes any text it decides one of three things: keep it (index it as it is, it is content), decode it (turn it
back into what the writer typed, then index it), or drop it (remove it before indexing, it is not content). Read the legend.
Three real snippets, each with what it is and where it comes from. Ask the class for each before clicking.
[click] "Internal. Uncontrolled when printed. / Page 2 of 4", the last two lines of D's page 2 as the naive parser reads it:
drop. It is the running footer, on every page; left in, it lands in the middle of a chunk. Our parser removes lines repeated at
the top and bottom of every page, and "Page x of y".
[click] "our price for the 36 V 500 Wh pack (your BAT-500) will be =C2=A3119.00 from=", one line of Voltway Cells' price e-mail of
25 Sep 2026 as stored on disk: decode. Quoted-printable, as on the Brightcell e-mail: =C2=A3 is "£" and the final "=" is a soft
break. Decoded: "£119.00 from 1 October 2026".
[click] "Status | SUPERSEDED", one row of the box at the top of the 2024 Approval Matrix v2.0 (Word) as our parser reads it: keep.
It is the one line that says this file is out of date (£200,000 is no longer the limit). Our parser keeps it and writes
"SUPERSEDED / old copy" at the top of every chunk of the file.

