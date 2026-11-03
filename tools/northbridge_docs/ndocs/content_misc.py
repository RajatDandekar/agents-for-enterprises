"""11_training (quick-reference cards, deck exports, the 2016 intranet export), 12_integrations, 99_scans, README."""
from __future__ import annotations

from .model import Book, Doc, Sheet

TR = "11_training"
IN = "12_integrations"
SC = "99_scans"


def build(c):
    training(c)
    intranet(c)
    integrations(c)
    scans(c)
    tables_note(c)
    readme(c)


def qrc(c, n, title, steps, facts=(), words=260):
    d = Doc(f"{TR}/QRC-{n:02d} {title}.pdf", f"Quick reference: {title}", doc_id=f"QRC-{n:02d}", version="2026.1", effective="2026-01-12",
            owner="Purchasing key users", style="qrc")
    d.h(1, "Steps")
    d.bullets(steps, numbered=True)
    for f in facts:
        d.pf(f[0], f[1], f[2], [f[3]] if len(f) > 3 and f[3] else None)
    c.filler(d, "Tips", words, context="\n".join(steps), brief="Write short practical tips for this quick-reference card under '### ' headings. No figures, no new steps.", level=1)
    c.add(d)
    return d


def training(c):
    qrc(c, 1, "Raising a purchase request", ["PUR-PR-01: enter the item code, press F3 (Fetch).", "Check the cost centre: is it OPEN?", "Enter quantity and need-by date.",
                                               "F8 Save (status DR), then F9 Submit.", "Within your limit: approved at once. Above it: goes to your manager."])
    qrc(c, 2, "Raising a purchase order - Fetch first", ["PUR-PO-01: type STD and the approved PR number.", "Enter supplier and item, then F3 Fetch. Always.",
                                                         "Overseas supplier? Change VAT20-UK to VAT20-RC.", "F8 Save. Read the Status field, not the status bar.",
                                                         "AP? Release it on PUR-POR-05 (F9). Only RL reaches the supplier."],
        facts=[("Changed the supplier or the item after Fetch? Press F3 again, or Save fails with ERR-SCR-0221.", "F-QRC2-REFETCH", "QRC-02: after changing supplier or item press F3 again or ERR-SCR-0221.", None)])
    qrc(c, 3, "ERR-PO-0412 quick fix", ["Read the code: ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (NL).", "The country in brackets is the supplier's.",
                                       "Supplier outside the UK: change the tax code to VAT20-RC (or VAT5-RC for reduced-rate items).", "UK supplier: use VAT20-UK.", "Press F8 again."],
        facts=[("Why it happens: Fetch always fills VAT20-UK, the code for a UK supplier, even when the supplier is in the Netherlands or Poland.", "F-QRC3-WHY",
                "QRC-03: ERR-PO-0412 happens because Fetch always fills VAT20-UK even for overseas suppliers.", None)])
    qrc(c, 4, "Goods receipt", ["INV-GRN-03: type the PO number, press Fetch.", "Count. Enter the quantity received.", "Supplier's delivery note number in Remarks.",
                                "F8 Save. A part delivery gets its own GRN.", "Battery packs from Voltway: straight into WH-MAN-STR (e-mail of 15 June 2026)."])
    qrc(c, 5, "Uploading a supplier certificate", ["Supplier master, Certificates tab, Add.", "Type UN38.3, document reference, valid to.", "Attach the scanned test report.",
                                                   "F8: CERT SAVED.", "Ask the senior buyer to check it and initial NBC-F-113."])
    qrc(c, 6, "Your approval inbox", ["Purchase > Order approval (PUR-POA-04).", "Open the document, check value, supplier, cost centre.",
                                      "Lithium-cell item? Write CERT OK and the certificate reference in the comment.", "Approve or Reject (reason mandatory)."])
    qrc(c, 7, "Lithium battery labels", ["Every parcel with a pack: label PKG-LBL-UN.", "Pack alone: UN3480. Pack in or with a bike: UN3481.", "Book carrier service DGX.",
                                         "Print the label before posting the despatch (ERR-DLV-0320)."])
    qrc(c, 8, "Stock enquiry and days of cover", ["INV-STK-02: item code, warehouse (blank for all).", "On hand, allocated, on order.", "Days of cover = (on hand - allocated) / average daily issue."])
    deck = Doc(f"{TR}/New starter - Purchasing (2024) deck export.pdf", "New starter induction: Purchasing at Northbridge", style="slides",
               meta={"cover_lines": ["Purchasing team induction, updated May 2024", "Daniel Okafor and Luis Moreno"]})
    slides = [("Welcome to purchasing", ["Who we are: purchase executives, senior buyer, purchase manager", "We buy for the Manchester plant and the Leeds unit", "Everything goes through Ledgerline ERP 7.2"]),
              ("The flow", ["Request (PR) -> order (PO) -> approval -> release -> receipt (GRN) -> invoice", "Only a released order reaches the supplier"]),
              ("Your limit", ["Limits are on the gross value including VAT", "Purchase executive: £200,000 (2024 matrix)", "Above it, your manager approves"]),
              ("Lithium-cell parts", ["Battery packs and hub motors need a supplier with a valid UN 38.3 certificate", "Check before the first order", "Ledgerline does not check it for you"]),
              ("Tax codes", ["UK supplier: VAT20-UK", "Overseas supplier: VAT20-RC", "ERR-PO-0412 means the wrong one"]),
              ("Signing in", ["Your session closes after 20 idle minutes", "Three wrong passwords lock you out for 30 minutes"]),
              ("Who to ask", ["Policies: Daniel", "Suppliers and certificates: Luis", "Ledgerline problems: IT service desk, extension 2210"])]
    for t, b in slides:
        deck.slide(t, b)
    deck.fact("F-DECK-LIMIT", "New starter deck (2024): purchase executive limit £200,000 (2024 matrix; now £250,000).", ["Purchase executive: £200,000 (2024 matrix)"], section="Your limit")
    c.add(deck)
    c.mess("superseded", [deck.path, "01_policies/POL-APR-002 Approval Matrix v3.0.pdf"], "The 2024 induction deck still teaches the old £200,000 limit, a 20-minute session timeout and §6.2 without chargers.")
    for i, (t, b) in enumerate([("Why battery safety matters", ["Lithium cells store a lot of energy", "Damage can show days later", "Most incidents start with a dropped pack"]),
                                ("Storage", ["Fire cells BAT-Z1 to BAT-Z4 in Manchester main stores", "No more than 1,500 packs per cell", "State of charge 30% to 50%"]),
                                ("Damaged packs", ["Red quarantine bin in BAT-Z4", "NCR on QA-NCR-02 in the same shift", "Never put a dropped pack back on the shelf"]),
                                ("Shipping", ["UN3480 for a pack alone", "UN3481 for a pack in or with a bike", "Carrier service DGX"]),
                                ("Refresher", ["Repeat BHT-01 every 24 months"])]):
        pass
    bht = Doc(f"{TR}/BHT-01 Battery handling course slides.pdf", "BHT-01 Battery handling", style="slides", meta={"cover_lines": ["Course BHT-01, version 3, November 2025", "Quality department"]})
    for t, b in [("Why battery safety matters", ["Lithium cells store a lot of energy", "Damage can show days later", "Most incidents start with a dropped pack"]),
                 ("Storage", ["Fire cells BAT-Z1 to BAT-Z4 in Manchester main stores", "No more than 1,500 packs per cell", "State of charge 30% to 50%"]),
                 ("Damaged packs", ["Red quarantine bin in BAT-Z4", "NCR on QA-NCR-02 in the same shift", "Never put a dropped pack back on the shelf"]),
                 ("Shipping", ["UN3480 for a pack alone", "UN3481 for a pack in or with a bike", "Carrier service DGX"]), ("Refresher", ["Repeat BHT-01 every 24 months"])]:
        bht.slide(t, b)
    c.add(bht)
    old = Doc(f"{TR}/old/Ledgerline basics for new starters (2019) deck export.pdf", "Ledgerline basics (2019)", style="slides",
              meta={"cover_lines": ["IT induction, 2019 edition", "Joanna Fletcher"]})
    for t, b in [("Signing in", ["User ID from IT", "Password at least 8 characters, changed every 90 days"]), ("Screens", ["F2 lookups", "F3 Fetch is optional on the order screen", "F8 Save"]),
                 ("Help", ["IT service desk extension 2210"])]:
        old.slide(t, b)
    c.add(old)
    c.mess("superseded", [old.path], "2019 IT induction deck: 8-character / 90-day passwords and 'Fetch is optional', both out of date.")


def intranet(c):
    base = f"{TR}/intranet_export_2016"
    nav = [("Purchasing home", "index.html"), ("How to raise an order", "how_to_raise_an_order.html"), ("Error messages", "error_messages.html"),
           ("Approval limits", "approval_limits.html"), ("Supplier list", "supplier_list.html"), ("Contacts", "contacts.html"),
           ("Forms", "/sites/purch/Forms/AllItems.aspx"), ("Ledgerline 7 training", "http://nbc-intranet01/training/ll7/default.aspx")]
    foot = "Last modified 03/11/2016 by DRAMSDEN. Exported from the old intranet (NBC-INTRANET01) in 2019 before it was switched off."
    pages = [
        ("index.html", "Purchasing home", [("p", "Welcome to the purchasing pages. Use the links on the left. Policies are in the [document library](/sites/purch/Shared%20Documents/Policies/). For Ledgerline problems call the helpdesk on extension 2210."),
                                           ("p", "News: Ledgerline 7.1 is coming in 2017. See the [upgrade page](upgrade_71.html).")]),
        ("how_to_raise_an_order.html", "How to raise an order", [("ul", ["Open Purchase > Order entry (PUR-PO-01).", "Enter supplier, item, quantity and rate. Fetch is optional; you can type the contract rate.",
                                                                          "Choose the tax region of the supplier.", "Save, then ask your manager to approve by e-mail.", "See also [the old 6.x guide](ll6_po_guide.html)."])]),
        ("error_messages.html", "Error messages", [("table", ["Code", "Message", "What to do"], [["ERR-PO-0412", "TAX REGION DOES NOT MATCH SUPPLIER STATE", "Change the tax region on the order to the supplier's state."],
                                                                                              ["ERR-SUP-0031", "SUPPLIER NOT ACTIVE", "Ask Graham Sutcliffe to unblock."],
                                                                                              ["ERR-PO-0610", "DIRECT PO LIMIT EXCEEDED", "Direct orders up to £30,000 only."]]),
                                                   ("p", "Full list: [Ledgerline error catalogue](http://nbc-intranet01/ll7/errors.xls).")]),
        ("approval_limits.html", "Approval limits (2016)", [("table", ["Role", "Limit"], [["Purchase executive", "£150,000"], ["Senior buyer", "£300,000"], ["Purchase manager", "£600,000"], ["Plant head", "£2,000,000"]]),
                                                            ("p", "Limits are on the net value before VAT.")]),
        ("supplier_list.html", "Supplier list", [("p", "The supplier list is now in Ledgerline (PUR-SUP-03). The old spreadsheet is [here](/sites/purch/Shared%20Documents/suppliers_2014.xls).")]),
        ("contacts.html", "Contacts", [("table", ["Name", "Role", "Extension"], [["Graham Sutcliffe", "Purchase manager", "2231"], ["Derek Ramsden", "IT manager", "2201"], ["Luis Moreno", "Buyer", "2236"]])]),
    ]
    for fn, title, blocks in pages:
        d = Doc(f"{base}/{fn}", title, meta={"nav": nav, "footer": foot})
        for b in blocks:
            if b[0] == "p":
                d.p(b[1])
            elif b[0] == "ul":
                d.bullets(b[1])
            else:
                d.table(b[1], b[2])
        if fn == "error_messages.html":
            d.fact("F-INTRA-0412", "Old intranet (2016): ERR-PO-0412 shown with its old text TAX REGION DOES NOT MATCH SUPPLIER STATE.", ["TAX REGION DOES NOT MATCH SUPPLIER STATE"], section="Error messages")
        if fn == "approval_limits.html":
            d.fact("F-INTRA-LIMITS", "Old intranet (2016): purchase executive limit £150,000 on the net value before VAT (long superseded).", ["£150,000", "Limits are on the net value before VAT."], section="Approval limits")
        c.filler(d, title, 300, context=" ".join(str(b[1]) for b in blocks if b[0] == "p"), brief="Write a little more body text for this 2016 company intranet page, plainly, as paragraphs. No figures, no codes, no names.")
        c.add(d)
    for i, topic in enumerate(["Purchasing team news, spring 2016", "Supplier visits", "Ledgerline tips and tricks", "Month-end checklist (2016)", "Working with stores",
                               "Packaging ideas", "Health and safety in the warehouse", "Our e-bike range 2016", "Meet the Leeds team", "Year-end stock count (2016)",
                               "Charity cycle ride", "Frequently asked questions", "Glossary of Ledgerline terms", "How we work with Finance", "Goods receipt tips",
                               "Quality notices", "Suppliers in Europe"]):
        fn = "page_" + "".join(ch.lower() if ch.isalnum() else "_" for ch in topic).strip("_") + ".html"
        d = Doc(f"{base}/{fn}", topic, meta={"nav": nav, "footer": foot})
        d.p(f"See also [the purchasing home page](index.html) and [the old forms library](/sites/purch/Forms/{fn.replace('.html', '.aspx')}).")
        c.filler(d, topic, 420, brief=f"Write the text of a 2016 company intranet page titled '{topic}' for the purchasing area of a British e-bike maker. Plain paragraphs and '- ' bullets. No figures, no codes, no names.")
        c.add(d)
    c.mess("broken_links", [f"{base}/index.html", f"{base}/how_to_raise_an_order.html", f"{base}/error_messages.html", f"{base}/supplier_list.html"],
           "The 2016 intranet export links to pages and servers that no longer exist (upgrade_71.html, ll6_po_guide.html, /sites/purch/..., http://nbc-intranet01/...).")
    c.mess("superseded", [f"{base}/error_messages.html", f"{base}/approval_limits.html", f"{base}/how_to_raise_an_order.html"],
           "The 2016 intranet pages give ERR-PO-0412's old text, a £30,000 direct-order limit, 2016 approval limits on NET value, and 'Fetch is optional'. All superseded.")


def integrations(c):
    d = Doc(f"{IN}/EDI ORDERS interface spec v2.1.pdf", "EDI ORDERS interface specification (bike shop and retailer orders)", doc_id="INT-EDI-001", version="2.1", effective="2022-05-01",
            owner="IT department", style="spec", history=[["1.0", "2005-10-01", "D. Ramsden", "Ledgerline 6.1 EDI"], ["2.1", "2022-05-01", "J. Fletcher", "Partner set-up, error codes"]])
    c.section(d, "1. Purpose", words=300)
    c.section(d, "2. Message flow", facts=[("2.1 Retailers send EDIFACT ORDERS messages to the EDI mailbox. Job JOB-SAL-010 reads the mailbox every 10 minutes and calls service edi_ord_in for each message.",
                                             "F-EDI-2.1", "EDI spec: JOB-SAL-010 reads the EDI mailbox every 10 minutes and calls edi_ord_in.", None),
                                            ("2.2 Ledgerline answers each order with an acknowledgement (edi_ord_ack) and, when the goods leave, a despatch advice (DESADV, edi_desadv_out).", None, None)][:1], words=420)
    d.h(1, "3. Segments used")
    d.table(["Segment", "Use", "Ledgerline field", "Mandatory"], [["UNH", "Message header", "msg_id", "Yes"], ["BGM", "Order number", "cust_ref", "Yes"], ["DTM", "Requested delivery date", "req_dt", "Yes"],
                                                                  ["NAD+BY", "Buyer (bike shop)", "cust_cd via partner table", "Yes"], ["LIN", "Item (buyer's or our code)", "itm_cd", "Yes"],
                                                                  ["QTY+21", "Quantity ordered", "qty", "Yes"], ["PRI", "Price (ignored; price list applies)", "-", "No"], ["UNT", "Message trailer", "-", "Yes"]])
    d.fact("F-EDI-PRI", "EDI spec: the PRI segment price is ignored; the price list applies.", ["Price (ignored; price list applies)"], section="3. Segments used")
    c.section(d, "4. Errors", facts=[("4.1 An unknown buyer item code is refused with ERR-EDI-0140; a partner not set up with ERR-EDI-0101. Refused messages are listed by edi_err_list and must be cleared by the sales team the same day.",
                                       "F-EDI-4.1", "EDI spec: unknown buyer item code ERR-EDI-0140; partner not set up ERR-EDI-0101.", None)], words=380)
    c.section(d, "5. Partner set-up", words=420)
    c.add(d)
    for n, (po, cust) in enumerate([("ORD-88213", "C01012"), ("ORD-88240", "C01177"), ("4500091877", "C01530")], 1):
        e = Doc(f"{IN}/edi_samples/ORDERS_{po}.edi", po)
        e.raw = (f"UNA:+.? 'UNB+UNOC:3+{cust}:ZZ+NORTHBRIDGE:ZZ+261020:0912+{n:05d}'UNH+1+ORDERS:D:96A:UN'BGM+220+{po}+9'DTM+137:20261020:102'DTM+2:20261103:102'"
                 f"NAD+BY+{cust}::92'LIN+1++FG-ANC-M-BLK:SA'QTY+21:2'PRI+AAA:1499.00'LIN+2++SPR-ANC-07:SA'QTY+21:5'UNS+S'UNT+11+1'UNZ+1+{n:05d}'\n")
        c.add(e)
    b = Doc(f"{IN}/Bank payment file format STD18 v1.3.pdf", "Supplier payment file: Standard 18 layout as used by Northbridge", doc_id="INT-BNK-002", version="1.3", effective="2024-06-01",
            owner="Finance and IT", style="spec")
    c.section(b, "1. Purpose", words=250)
    b.h(1, "2. Record layout (one record per payment)")
    b.table(["Positions", "Length", "Field", "Notes"], [["1-6", "6", "Destination sort code", "Supplier's bank"], ["7-14", "8", "Destination account", "Zero-padded"], ["15", "1", "Type", "0"],
                                                         ["16-17", "2", "Transaction code", "99 for credit"], ["18-23", "6", "Originating sort code", "Northbridge main account"],
                                                         ["24-31", "8", "Originating account", ""], ["36-46", "11", "Amount", "In pence, zero-padded"], ["47-64", "18", "Originator name", "NORTHBRIDGE CYCLES"],
                                                         ["65-82", "18", "Reference", "AP run number"], ["83-100", "18", "Beneficiary name", "Upper case"]])
    b.fact("F-BNK-PENCE", "Bank file STD18: the amount field (positions 36-46) is in pence, zero-padded.", ["36-46", "In pence, zero-padded"], section="2. Record layout")
    c.section(b, "3. Overseas suppliers", facts=[("3.1 Payments to suppliers outside the UK are not in the STD18 file. They are keyed by hand into the bank's portal by the AP manager, from the run's foreign-payments list.",
                                                  "F-BNK-OVERSEAS", "Bank file spec: overseas supplier payments are not in STD18; the AP manager keys them into the bank portal.", None)], words=300)
    c.section(b, "4. Controls", words=320)
    c.add(b)
    s = Doc(f"{IN}/bank_file_sample_2026-10-22.txt", "sample")
    s.raw = "".join(f"{sc}{acct}099{'401276'}{'31884520'}    {amt:011d}NORTHBRIDGE CYCLESPR-20261022       {name:<18}\n"
                    for sc, acct, amt, name in [("204511", "73319201", 1873440, "PENNINE BRAKES"), ("309876", "11829304", 5160000, "IRWELL PACKAGING"),
                                                ("402214", "90012877", 22099200, "CASTLEFIELD CHARGE")])
    c.add(s)
    m = Doc(f"{IN}/Carrier API notes - Moorland Logistics.md", "Carrier API notes: Moorland Logistics")
    m.p("Notes kept by IT about the carrier booking interface. Moorland Logistics is our contract parcel and pallet carrier for the UK and Europe.")
    m.h(1, "Services")
    m.table(["Code", "Service"], [["NXT", "Next working day, UK"], ["ECO", "Economy, 2-3 days"], ["DGX", "Dangerous goods (lithium batteries), UK and EU road"], ["PAL", "Pallet"]])
    m.fact("F-CAR-DGX", "Carrier notes: DGX is Moorland's dangerous-goods (lithium battery) service.", ["DGX", "Dangerous goods (lithium batteries), UK and EU road"], section="Services")
    m.h(1, "Booking")
    m.p("Ledgerline calls the carrier through the old SOAP gateway (services frt_quote, frt_book, frt_track, frt_label). Bookings made after 15:30 are collected the next working day.")
    m.fact("F-CAR-1530", "Carrier notes: bookings after 15:30 are collected the next working day.", ["Bookings made after 15:30 are collected the next working day."], section="Booking")
    m.h(1, "Known problems")
    c.filler(m, "Known problems", 350, brief="Write short notes an IT person keeps about problems with a carrier booking interface on an old SOAP gateway: timeouts, label printing, duplicate bookings. '- ' bullets. No figures, no names, no codes.", level=2)
    c.add(m)
    a = Doc(f"{IN}/SVC_AGENT integration account - design note.md", "Design note: the SVC_AGENT integration account (2024)")
    a.p("Written by IT in March 2024 when the first bot pilot started.")
    a.pf("SVC_AGENT was created 'for the bot' with role SYS-ADMIN so that it could call every service while we found out which ones it needs. It has no named owner and an approval limit of 1e12. This was meant to be temporary.",
         "F-SVC-AGENT", "Design note: SVC_AGENT was created with SYS-ADMIN 'for the bot', no named owner, approval limit 1e12, meant to be temporary.")
    c.filler(a, "Design note", 400, context="SVC_AGENT has role SYS-ADMIN, every service, no named owner.", brief="Write the rest of this short IT design note about a temporary all-powerful integration account in an old ERP: risks, what should replace it, open questions. Plain paragraphs and '- ' bullets. No figures, no names.")
    c.add(a)
    g = Doc(f"{IN}/wsdl/LedgerlineGateway.wsdl", "gateway")
    ops = [s for s in c.cat.services if s["fmt"] == "xml"]
    g.raw = ('<?xml version="1.0" encoding="UTF-8"?>\n<!-- Ledgerline SOAP gateway: all operations on the compatibility listener (port 8091). -->\n'
             '<wsdl:definitions name="LedgerlineGateway" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" targetNamespace="urn:ledgerline:gateway">\n  <wsdl:portType name="GatewayPort">\n' +
             "".join(f'    <wsdl:operation name="{s["name"]}"><wsdl:documentation>{s["title"]}</wsdl:documentation></wsdl:operation>\n' for s in ops) +
             "  </wsdl:portType>\n</wsdl:definitions>\n")
    c.add(g)
    inv = Book(f"{IN}/Integration inventory.xlsx", [Sheet("Interfaces", ["id", "interface", "direction", "transport", "account", "owner", "since"], [
        ["INT-001", "EDI ORDERS from retailers", "in", "SOAP gateway", "EDI_GW (disabled) -> SVC_EDI", "Isla Morgan", "2005"],
        ["INT-002", "Bank payment file STD18", "out", "file", "AP batch", "Marta Kowalski", "2007"],
        ["INT-003", "Carrier booking (Moorland Logistics)", "out", "SOAP gateway", "SVC_CARRIER", "Callum Shaw", "2014"],
        ["INT-004", "Battery test rig results", "in", "file drop", "SVC_RIG", "Pieter Jansen", "2023"],
        ["INT-005", "Payroll export", "out", "file", "HR batch", "Sofia Lindqvist", "2016"],
        ["INT-006", "Reporting extract", "out", "database view", "SVC_BI", "Grace Whitaker", "2020"],
        ["INT-007", "Purchasing bot pilot", "both", "HTTP services", "SVC_AGENT", "(none)", "2024"]])])
    inv.fact("F-INT-007", "Integration inventory: INT-007 purchasing bot pilot uses SVC_AGENT and has no owner.", "Interfaces", "INT-007", "owner", extra=[("INT-007", "account")])
    c.add(inv)


def scans(c):
    pages = {
        "1998_Ledgerline_licence_signature_page.pdf": [[("SOFTWARE LICENCE AGREEMENT", 54, True), ("<hr>",), ("between LEDGERLINE SYSTEMS LTD", 40, False), ("and NORTHBRIDGE CYCLES LTD", 40, False),
                                                        ("", 30), ("Ledgerline ERP version 5.2, purchasing, stores and finance modules", 34), ("for 25 named users at the Manchester works", 34),
                                                        ("", 30), ("Signed for Northbridge Cycles Ltd", 34, True), ("<sig>",), ("R. Ainsworth, Managing Director", 34),
                                                        ("Date: 14 August 1998", 38, True), ("", 20), ("Signed for Ledgerline Systems Ltd", 34, True), ("<sig>",), ("<stamp>", 0, False, "COPY")]],
        "2004_LL6_manual_page_37_scan.pdf": [[("LEDGERLINE 6  USER GUIDE  PURCHASING", 40, True), ("<hr>",), ("6.4 Vendor order entry (screen PO-ENT)", 38, True),
                                              ("Enter the vendor number and press F4 for vendor details.", 32), ("Enter item, quantity and price on each line.", 32),
                                              ("Up to 40 lines per order are allowed.", 32), ("Press F10 to post the order.", 34, True), ("A posted order is printed at once.", 32),
                                              ("", 30), ("page 37", 30)]],
        "2011_VAT_rate_change_memo.pdf": [[("MEMO  FINANCE DEPARTMENT", 46, True), ("<hr>",), ("To: all Ledgerline users   Date: 20 December 2010", 32),
                                           ("VAT standard rate changes to 20% on 4 January 2011", 38, True), ("Tax code V175-UK will be closed on 3 January 2011.", 34),
                                           ("From 4 January use tax code VAT20-UK for UK suppliers.", 34), ("Orders already posted keep their old tax.", 32), ("<sig>",), ("Finance manager", 32)]],
        "2019_Voltway_code_change_approval_signed.pdf": [[("SUPPLIER MASTER CHANGE REQUEST", 46, True), ("<hr>",), ("Supplier: Voltway Cells, Eindhoven", 36),
                                                          ("Old code: VC-EIN-0009   to be BLOCKED", 38, True), ("New code: VC-EIN-0042", 38, True),
                                                          ("Reason: Ledgerline 7.1 migration, new supplier numbering", 32), ("Approved by: G. Sutcliffe", 34), ("<sig>",),
                                                          ("Date: 21/03/2019", 36), ("<stamp>", 0, False, "ENTERED")]],
        "2023_stock_count_sheet_MAN_aisle_B.pdf": [[("ANNUAL STOCK COUNT 2023  MANCHESTER MAIN STORES", 40, True), ("AISLE B   COUNT TEAM 3", 34), ("<hr>",),
                                                    ("BIN       ITEM          COUNTED", 32, True), ("B-01-01   BRK-PAD-01    2,400", 32), ("B-01-02   BEL-STD-01    1,150", 32),
                                                    ("B-02-01   BOX-BIKE-01   3,600", 32), ("B-02-04   MNT-FRM-01    2,050", 32), ("B-03-02   CHG-4A-01     980", 32),
                                                    ("", 20), ("Counted by: A. Tanaka   Checked by: C. Shaw", 32), ("<sig>",), ("Date: 25 March 2023", 34)]],
        "2026_signed_approval_PO-2026-00452.pdf": [[("PURCHASE ORDER APPROVAL (PAPER COPY)", 44, True), ("<hr>",), ("PO number: PO/2026/00452", 38, True), ("Supplier: VC-EIN-0042 Voltway Cells", 34),
                                                    ("Item: BAT-500   Quantity: 1,800   Rate: 114.00", 34), ("Approved by: Daniel Okafor", 34), ("<sig>",), ("Date: 06/04/2026", 34),
                                                    ("Note: system approval also recorded in Ledgerline", 30)]],
    }
    facts = {"1998_Ledgerline_licence_signature_page.pdf": ("F-SCAN-1998", "Scanned licence (1998): signed for Northbridge by R. Ainsworth, Managing Director, on 14 August 1998, for Ledgerline ERP 5.2.", ["14 August 1998", "Ainsworth"]),
             "2004_LL6_manual_page_37_scan.pdf": ("F-SCAN-LL6", "Scanned Ledgerline 6 guide page 37 (2004): press F10 to post a vendor order.", ["Press F10 to post the order"]),
             "2011_VAT_rate_change_memo.pdf": ("F-SCAN-VAT", "Scanned memo (Dec 2010): VAT standard rate 20% from 4 January 2011; V175-UK closed.", ["4 January 2011", "V175-UK"]),
             "2019_Voltway_code_change_approval_signed.pdf": ("F-SCAN-VC", "Scanned change request (21 Mar 2019): VC-EIN-0009 blocked, new code VC-EIN-0042, approved by G. Sutcliffe.", ["VC-EIN-0009", "VC-EIN-0042", "Sutcliffe"]),
             "2023_stock_count_sheet_MAN_aisle_B.pdf": ("F-SCAN-CNT", "Scanned 2023 count sheet: counted by A. Tanaka, checked by C. Shaw.", ["Tanaka", "Shaw"]),
             "2026_signed_approval_PO-2026-00452.pdf": ("F-SCAN-452", "Scanned paper approval of PO/2026/00452 by Daniel Okafor.", ["00452", "Daniel Okafor"])}
    for fn, pg in pages.items():
        d = Doc(f"{SC}/{fn}", fn, meta={"scan_pages": pg})
        fid, stmt, needles = facts[fn]
        d.fact(fid, stmt, needles, section="page 1")
        c.add(d)
    c.mess("scans", [f"{SC}/{f}" for f in pages], "Six image-only PDFs (scans) with no text layer: a 1998 licence signature page, a 2004 Ledgerline 6 manual page, a 2011 VAT memo, a 2019 code-change form, a 2023 count sheet and a 2026 paper approval. Text extraction returns nothing; OCR is needed.")


def tables_note(c):
    c.mess("tables_in_pdfs", ["01_policies/POL-APR-002 Approval Matrix v3.0.pdf", "01_policies/POL-DRP-009 Data Retention Policy v1.4.pdf",
                              "03_ledgerline_manuals/MAN-SCR-72 Screen Reference v7.2.3.pdf", "07_data_dictionary/Ledgerline 7.2 Data Dictionary (all modules).pdf",
                              "06_transactions/reports/PO register 2026-09 (printed).pdf", "12_integrations/Bank payment file format STD18 v1.3.pdf"],
           "Key facts sit inside tables in PDFs (approval limits, retention periods, screen fields, record layouts, printed registers); plain text extraction loses the row and column structure.")


def readme(c):
    d = Doc("README.md", "northbridge-docs")
    d.p("**From Henrik Weber, plant head, Northbridge Cycles, Manchester**")
    d.p("Hello, and thank you for taking this on.")
    d.p("You asked for our documentation before you change anything, and you were right to. Here it is: everything we could find about how "
        "Northbridge buys, stores, builds, sells and pays, in the shape it is really in. We have run Ledgerline since 1998. The rules live in "
        "policies, in procedures, in the vendor's manuals, in spreadsheets people keep on the share, and, if I am honest, in Luis's head and in e-mails "
        "that never made it into a policy.")
    d.p("Some of it is out of date. Some of it is there twice. A few documents disagree with each other, and a couple are not in force yet. I have "
        "not tidied it, because I think you need to see what we actually work from. Where something is old, the newer document usually says so; where it "
        "does not, ask Luis or Daniel.")
    d.p("One folder is private: 01_policies/HR/CONFIDENTIAL holds salary bands and HR cases. It is in here because it sits on the same share. Please "
        "make sure nothing you build ever shows it to anyone outside HR.")
    d.p("What we would like first is simple: when Emma or anyone else asks how to do something, or which rule applies, they should get the right "
        "answer with the document it comes from. Thank you. Henrik")
    d.h(1, "What is in each folder")
    d.table(["Folder", "What it holds"], [
        ["01_policies/", "Policies (PDF), older versions (old/, DOCX), amendments, and HR (HR/CONFIDENTIAL is restricted)"],
        ["02_procedures/", "Standard operating procedures: onboarding, PR to PO, amendments, receipts, returns, counts, AP, sales, production, IT; forms/ and old/"],
        ["03_ledgerline_manuals/", "Ledgerline 7.2 vendor manuals per module, admin guide, screen reference, error-code reference, batch jobs; old/ manuals"],
        ["04_service_definitions/", "400 service definitions, one file each (YAML; WSDL-style XML for the old SOAP gateway); purchase/ holds the 38 purchasing services"],
        ["05_master_data/", "Item, supplier (with certificates), rate contract, cost centre and budget, user, tax, payment-term, warehouse, customer, BOM masters"],
        ["06_transactions/", "Extracts for January to October 2026: requests, orders, receipts, invoices, Q3 stock ledger, sales orders; printed reports/"],
        ["07_data_dictionary/", "Tables, fields and codes (XLSX and PDF)"],
        ["08_release_notes/", "Ledgerline 7.0 to 7.2.3-P5, a 7.3 preview, Ledgerline 6 history, our change log"],
        ["09_email_archive/", "E-mails (.eml) with decisions and clarifications"],
        ["10_meeting_notes/", "Meeting notes (DOCX, MD), including the change board"],
        ["11_training/", "Quick-reference cards, induction decks, the 2016 intranet export"],
        ["12_integrations/", "EDI, bank payment file, carrier notes, the SOAP gateway, the integration inventory"],
        ["99_scans/", "Scanned paper (image-only PDFs)"],
        ["eval/", "For the course: planted facts, the golden question set, the messiness log, statistics, the checker"]])
    d.h(1, "Dates")
    d.p("The documents are as they stood on Monday 26 October 2026 at 09:00. Documents dated later are issued but not yet in force.")
    d.p("Everything here is fictional: Northbridge Cycles, Ledgerline Systems, every person, supplier, code and number.")
    c.add(d)
