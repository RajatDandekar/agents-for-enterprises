"""02_procedures: standard operating procedures (PDF, some DOCX), old versions and forms."""
from __future__ import annotations

from .model import Doc

P = "02_procedures"
ABBR = [["PR", "Purchase request"], ["PO", "Purchase order"], ["GRN", "Goods receipt note"], ["RTV", "Return to vendor (supplier)"],
        ["DN", "Delivery note (supplier's)"], ["CC", "Cost centre"], ["WHS", "Warehouse"], ["UOM", "Unit of measure"],
        ["NOS", "Numbers (pieces)"], ["SUP", "Supplier"], ["ITM", "Item"], ["RC", "Reverse charge (VAT) or rate contract, by context"],
        ["ADI", "Average daily issue"], ["ROL", "Reorder level"], ["NCR", "Non-conformance report"], ["3WM", "Three-way match"],
        ["GRNI", "Goods received, not invoiced"], ["DG", "Dangerous goods"], ["AQL", "Acceptable quality level"], ["OCV", "Open-circuit voltage"]]


def sop(c, path, title, doc_id, version, effective, owner, approver, steps, extra=(), purpose_facts=(), history=None, status="CURRENT",
        words=(300, 180, 320, 520, 280, 180), abbr=8):
    d = Doc(path, title, doc_id=doc_id, version=version, effective=effective, owner=owner, approver=approver, status=status,
            history=history or [["1.0", effective, owner, "First issue"]], style="policy")
    c.section(d, "1. Purpose", facts=purpose_facts, words=words[0])
    c.section(d, "2. Scope", words=words[1])
    c.section(d, "3. Responsibilities", words=words[2])
    d.h(1, "4. Abbreviations")
    rows = [a for a in ABBR if a[0] in " ".join(s[0] for s in steps) or a[0] in ("PR", "PO", "CC")][:abbr] or ABBR[:abbr]
    d.table(["Abbreviation", "Meaning"], rows)
    d.h(1, "5. Procedure")
    texts = []
    for i, s in enumerate(steps, 1):
        text = f"5.{i} {s[0]}"
        if len(s) > 1 and s[1]:
            d.pf(text, s[1], s[2], [s[3]] if len(s) > 3 and s[3] else None)
        else:
            d.p(text)
        texts.append(text)
    c.filler(d, "5. Procedure: notes and common mistakes", words[3], context="\n".join(texts),
             brief="Write practical notes for this procedure under '### ' sub-headings: common mistakes, what to check on the "
                   "screen, and what to do when something does not look right. Do not add steps, figures or rules.", level=2)
    for e in extra:
        c.section(d, e[0], facts=e[1], words=e[2] if len(e) > 2 else 200)
    c.section(d, f"{6 + len(extra)}. Records", words=words[4])
    c.section(d, f"{7 + len(extra)}. Related documents", words=0)
    d.bullets(sorted({x for x in __import__("re").findall(r"\b(?:POL|SOP|MAN|AMD|QRC)-[A-Z0-9]+-[0-9-]+\b", " ".join(texts))}) or ["MAN-PUR-72 Ledgerline 7.2 User Manual, Purchasing"])
    c.add(d)
    return d


def build(c):
    on = sop(c, f"{P}/SOP-PUR-001 Supplier Onboarding v3.1.pdf", "Supplier Onboarding", "SOP-PUR-001", "3.1", "2026-09-01", "Luis Moreno (senior buyer)",
             "Daniel Okafor (purchase manager)", [
                 ("Search the supplier master first: on PUR-SUP-03, search by one short, distinctive word of the name, then by city, then by VAT number. Print the result and attach it to the onboarding file.",
                  "F-SOP1-SEARCH", "SOP-PUR-001 step 5.1: search PUR-SUP-03 by a short word of the name, by city and by VAT number; attach the printed result.", "search by one short, distinctive word of the name, then by city, then by VAT number"),
                 ("Raise the onboarding request on form NBC-F-112 (Supplier Onboarding Request), with at least one written quotation and the reason an existing supplier cannot meet the need.",
                  "F-SOP1-F112", "SOP-PUR-001 step 5.2: the onboarding request is form NBC-F-112, with at least one written quotation.", "Raise the onboarding request on form NBC-F-112 (Supplier Onboarding Request)"),
                 ("Collect the documents listed in POL-SUP-003 §3.2: VAT registration certificate, company registration number, bank letter, proof of insurance and the signed Supplier Code of Conduct.", None, None),
                 ("For a supplier of lithium-cell parts, obtain the UN 38.3 test report and the UN 38.3 test summary for each part it will supply. Check the dates against AMD-SUP-2026-02: the report must have been issued within the last 12 months, and its valid-to date must be at least 60 days after the planned date of the first order.",
                  "F-SOP1-CERT", "SOP-PUR-001 step 5.4: for lithium-cell parts get the UN 38.3 test report and test summary; issued within 12 months, valid to at least 60 days after the first order.", "obtain the UN 38.3 test report and the UN 38.3 test summary for each part it will supply"),
                 ("Send the complete file to the purchase manager. The purchase manager approves by signing box 7 of form NBC-F-112. Do not create the supplier before this signature.",
                  "F-SOP1-APPR", "SOP-PUR-001 step 5.5: the purchase manager approves by signing box 7 of NBC-F-112; do not create the supplier before.", "The purchase manager approves by signing box 7 of form NBC-F-112."),
                 ("Create the supplier on PUR-SUP-01 (service sup_create) with the name, city, two-letter country code, VAT number and payment terms. Ledgerline generates the supplier code and shows SUPPLIER <code> CREATED in the status bar.",
                  "F-SOP1-CREATE", "SOP-PUR-001 step 5.6: create the supplier on PUR-SUP-01 (sup_create) with name, city, country code, VAT number, payment terms.", "Create the supplier on PUR-SUP-01 (service sup_create)"),
                 ("Upload the UN 38.3 certificate on the Certificates tab of the supplier (service sup_cert_upload): certificate type UN38.3, the document reference and the valid-to date, with the scanned test report attached. The status bar shows CERT SAVED.",
                  "F-SOP1-UPLOAD", "SOP-PUR-001 step 5.7: upload the certificate on the Certificates tab (sup_cert_upload): type UN38.3, document reference, valid-to date, scan attached.", "Upload the UN 38.3 certificate on the Certificates tab of the supplier (service sup_cert_upload)"),
                 ("The senior buyer checks the uploaded certificate against the test report and initials the onboarding checklist (form NBC-F-113). No order for a lithium-cell part may be raised until the checklist is initialled.",
                  "F-SOP1-CHECK", "SOP-PUR-001 step 5.8: the senior buyer checks the certificate and initials checklist NBC-F-113 before any order for a lithium-cell part.", "initials the onboarding checklist (form NBC-F-113)"),
                 ("Accounts payable verifies the bank details by calling the supplier back on a number taken from its letterhead or website, never from the bank letter or an e-mail (SOP-AP-004).",
                  "F-SOP1-BANK", "SOP-PUR-001 step 5.9: AP verifies bank details by call-back on a number from the letterhead or website (SOP-AP-004).", None),
                 ("The purchase manager's office sets up the rate contract (SOP-PUR-004). Until it exists, Fetch on PUR-PO-01 has no contract rate to fill.", None, None)],
             extra=[("6. Timing and system checks", [
                 ("6.1 Allow five working days from a complete file (POL-SUP-003 §3.6). For a supplier of lithium-cell parts, allow at least ten working days: the certificate check often needs questions back to the supplier's test laboratory.",
                  "F-SOP1-TIME", "SOP-PUR-001 §6.1: five working days from a complete file; at least ten for lithium-cell suppliers.", None),
                 ("6.2 Ledgerline will not stop you. A new supplier is ACTIVE the moment it is created, and Ledgerline does not check certificates when an order is saved (parameter PUR.CERT_CHK is N at Northbridge). The checklist in step 5.8 is the only control.",
                  "F-SOP1-NOCHK", "SOP-PUR-001 §6.2: Ledgerline does not check certificates on order save at Northbridge (PUR.CERT_CHK = N); the checklist is the only control.", "parameter PUR.CERT_CHK is N at Northbridge")], 260)],
             history=[["1.0", "2015-06-01", "G. Sutcliffe", "First issue for Ledgerline 7.0"], ["2.0", "2021-02-01", "L. Moreno", "Rewritten"],
                      ["3.0", "2025-04-01", "L. Moreno", "UN 38.3 certificates"], ["3.1", "2026-09-01", "L. Moreno", "AMD-SUP-2026-02 dates; PUR.CERT_CHK note"]])
    old = Doc(f"{P}/old/SOP-PUR-001 Supplier onboarding v2.0 (2021).docx", "Supplier Onboarding", doc_id="SOP-PUR-001", version="2.0",
              effective="2021-02-01", owner="Luis Moreno", status="SUPERSEDED")
    old.meta["docx_author"] = "Luis Moreno"
    c.section(old, "1. Purpose", words=150)
    old.h(1, "5. Procedure")
    old.bullets(["Search the supplier list on screen SUPP-ENQ (Ledgerline 6 menu: Masters > Vendors).",
                 "Fill in form NBC-F-112 and get the purchase manager's signature.",
                 "Create the vendor on SUPP-ENT. Battery pack suppliers must send a UN 38.3 report within three months of the first order.",
                 "Allow three working days."], numbered=True)
    old.fact("F-SOP1-OLD", "SOP-PUR-001 v2.0 (2021, superseded) allowed the UN 38.3 report within three months after the first order.",
             ["must send a UN 38.3 report within three months of the first order"], section="5. Procedure")
    c.add(old)
    c.mess("superseded", [old.path, on.path], "SOP-PUR-001 v2.0 (2021) is still present: Ledgerline 6 screen names, 'vendor', and a UN 38.3 report allowed up to three months AFTER the first order, the opposite of today's rule.")
    chk = Doc(f"{P}/forms/Final_FINAL_onboarding checklist NBC-F-113.docx", "Supplier Onboarding Checklist (NBC-F-113)", doc_id="NBC-F-113", version="2.1",
              owner="Purchase department", effective="2026-09-01")
    chk.meta["docx_author"] = "Luis Moreno"
    chk.p("Supplier name: ______________________  City: ____________  Country: ____  VAT number: ______________")
    chk.table(["#", "Check", "Done by", "Initials", "Date"], [
        ["1", "Supplier master searched by name, city and VAT number; result attached", "Proposer", "", ""],
        ["2", "NBC-F-112 signed by the purchase manager (box 7)", "Proposer", "", ""],
        ["3", "VAT certificate, company number, bank letter, insurance, Code of Conduct on file", "Proposer", "", ""],
        ["4", "UN 38.3 report issued within 12 months; valid to at least 60 days after the first order", "Senior buyer", "", ""],
        ["5", "Certificate uploaded as UN38.3 with document reference and valid-to date", "Proposer", "", ""],
        ["6", "Bank details verified by call-back (SOP-AP-004)", "Accounts payable", "", ""],
        ["7", "Rate contract entered", "Purchase manager's office", "", ""]])
    chk.fact("F-F113-4", "Checklist NBC-F-113 line 4: the senior buyer checks the UN 38.3 report is issued within 12 months and valid to at least 60 days after the first order.",
             ["UN 38.3 report issued within 12 months; valid to at least 60 days after the first order", "Senior buyer"], section="Checklist")
    c.add(chk)
    c.mess("inconsistent_naming", [chk.path], "File name 'Final_FINAL_onboarding checklist' does not follow the document-number naming of the other procedures.")

    p2 = [("Raise the request on PUR-PR-01. Enter the item code and press F3 (Fetch): Ledgerline fills the unit, the warehouse, your default cost centre and an estimated rate. The estimated rate is the rate on the last released order for the item, not the current contract rate.",
           "F-SOP2-FETCH", "SOP-PUR-002 step 5.1: PR Fetch fills the estimated rate from the last released order, not the contract.", "The estimated rate is the rate on the last released order for the item, not the current contract rate."),
          ("Check the cost centre on FIN-CC-01 before saving. Your default cost centre may have been closed by Finance; Ledgerline does not warn you on the request.", "F-SOP2-CC", "SOP-PUR-002 step 5.2: check the cost centre on FIN-CC-01; the default may be closed.", "Your default cost centre may have been closed by Finance"),
          ("Press F8 to save (status DR) and F9 to submit. A request within your limit is approved at once; one above it goes to your manager.", None, None),
          ("When the request is approved (AP), raise the order on PUR-PO-01 with order type STD and the request number in Source PR. Press F3 (Fetch) after entering the supplier and the item. Save is refused with ERR-SCR-0221 if Fetch was not run.", "F-SOP2-STD", "SOP-PUR-002 v1.4 step 5.4: Fetch is mandatory before Save on PUR-PO-01 (ERR-SCR-0221).", "Save is refused with ERR-SCR-0221 if Fetch was not run."),
          ("Check the tax code before saving. Fetch always fills VAT20-UK. For a supplier outside the UK change it to VAT20-RC, or Save fails with ERR-PO-0412.", "F-SOP2-TAX", "SOP-PUR-002 step 5.5: Fetch fills VAT20-UK; overseas suppliers need VAT20-RC or Save fails with ERR-PO-0412.", "For a supplier outside the UK change it to VAT20-RC, or Save fails with ERR-PO-0412."),
          ("Press F8 and read the Status field, not just the status bar. SAVED appears whatever the status. DR means the order is stuck (usually a closed cost centre, warning W-CC-114); PA means it waits for approval; AP means it can be released.", "F-SOP2-STATUS", "SOP-PUR-002 step 5.6: read the Status field after save; SAVED appears whatever the status.", "SAVED appears whatever the status."),
          ("Release the approved order on PUR-POR-05 with F9. Only an order in status RL has reached the supplier. Tell the requester only then.", "F-SOP2-RL", "SOP-PUR-002 step 5.7: release on PUR-POR-05; only RL has reached the supplier.", "Only an order in status RL has reached the supplier.")]
    v14 = sop(c, f"{P}/SOP-PUR-002 PR to PO v1.4.pdf", "Purchase Request to Purchase Order", "SOP-PUR-002", "1.4", "2025-02-01", "Daniel Okafor (purchase manager)",
              "Henrik Weber (plant head)", p2, history=[["1.3", "2023-05-01", "D. Okafor", "Approval inbox"], ["1.4", "2025-02-01", "D. Okafor", "Fetch mandatory (Ledgerline 7.2.3)"]])
    p2old = [s if not (s[1] or "").startswith("F-SOP2-STD") else
             ("When the request is approved (AP), raise the order on PUR-PO-01 with order type STD and the request number in Source PR. Fetch is optional; you may type the rate from the rate contract.",
              "F-SOP2-OLD", "SOP-PUR-002 v1.3 (superseded) said Fetch was optional.", "Fetch is optional; you may type the rate from the rate contract.") for s in p2]
    p2old = [(s[0], None, None) if s[1] and s[1] != "F-SOP2-OLD" else s for s in p2old]
    v13 = sop(c, f"{P}/SOP-PUR-002 PR to PO v1.3 (FINAL).pdf", "Purchase Request to Purchase Order", "SOP-PUR-002", "1.3", "2023-05-01", "Daniel Okafor (purchase manager)",
              "Henrik Weber (plant head)", p2old, status="SUPERSEDED", history=[["1.3", "2023-05-01", "D. Okafor", "Approval inbox"]])
    c.mess("near_duplicate", [v13.path, v14.path], "SOP-PUR-002 v1.3 '(FINAL)' and v1.4: near-identical; v1.3 says Fetch is optional, which Ledgerline 7.2.3 no longer allows (ERR-SCR-0221).")

    sop(c, f"{P}/SOP-PUR-003 PO Amendment and Cancellation v1.2.pdf", "Purchase Order Amendment and Cancellation", "SOP-PUR-003", "1.2", "2025-02-01",
        "Daniel Okafor (purchase manager)", "Henrik Weber (plant head)", [
            ("Open the order on PUR-POM-06 and press Fetch. Change only the quantity, need-by date or cost centre; to change the supplier, item or rate, cancel and raise a new order.", "F-SOP3-1", "SOP-PUR-003 step 5.1: PUR-POM-06 changes only quantity, need-by date or cost centre; other changes need cancel and re-raise.", "to change the supplier, item or rate, cancel and raise a new order"),
            ("To rescue a Draft order stuck on a closed cost centre (warning W-CC-114), amend the cost centre to an open one. The order then becomes AP or PA by the normal rules.", "F-SOP3-2", "SOP-PUR-003 step 5.2: rescue a W-CC-114 Draft by amending to an open cost centre.", None),
            ("An amendment that raises the gross value above what the approval covers sends the order back to PA, even if it was released. Warn the supplier that the change is not confirmed until the order is released again.", "F-SOP3-3", "SOP-PUR-003 step 5.3: an increase beyond approval sends even a released order back to PA.", None),
            ("To cancel, press Cancel and enter a reason. Ledgerline sends no cancellation notice: e-mail the supplier yourself the same day and keep the e-mail on the order file.", "F-SOP3-4", "SOP-PUR-003 step 5.4: Ledgerline sends no cancellation notice; e-mail the supplier the same day.", "Ledgerline sends no cancellation notice: e-mail the supplier yourself the same day"),
            ("Orders in CN, RJ or CL cannot be amended (ERR-PO-0801).", None, None)])
    sop(c, f"{P}/SOP-PUR-004 Rate Contract Maintenance v2.0.pdf", "Rate Contract Maintenance", "SOP-PUR-004", "2.0", "2024-03-01", "Daniel Okafor (purchase manager)",
        "Henrik Weber (plant head)", [
            ("Rate contracts are entered only by the purchase manager's office (role PUR-MGR), on the Rate contracts tab of the supplier master.", "F-SOP4-1", "SOP-PUR-004: only the purchase manager's office (PUR-MGR) enters rate contracts.", None),
            ("A rate contract runs for at most 12 months. Most run from 1 April to 31 March; contracts for battery packs may run for six months.", "F-SOP4-2", "SOP-PUR-004: a rate contract runs at most 12 months; battery packs may run six months.", "A rate contract runs for at most 12 months."),
            ("A new contract starts on its valid-from date. Do not change the rate on an existing contract line: end it and add a new line.", None, None),
            ("Contracts are reviewed in March and September (POL-SUP-003 §7.3). The rate-contract expiry report (JOB-PUR-031) lists contracts ending within 45 days.", "F-SOP4-3", "SOP-PUR-004: JOB-PUR-031 lists contracts ending within 45 days.", None)])
    sop(c, f"{P}/SOP-PUR-005 Certificate Renewal (UN 38.3) v1.1.pdf", "Certificate Renewal (UN 38.3)", "SOP-PUR-005", "1.1", "2026-09-01", "Luis Moreno (senior buyer)",
        "Daniel Okafor (purchase manager)", [
            ("On the first working day of each month the senior buyer runs the certificate-expiry report (job JOB-PUR-022) with a 90-day window.", None, None),
            ("For each UN 38.3 certificate expiring within 90 days, write to the supplier with letter template NBC-L-07, asking for a new test report.", "F-SOP5-1", "SOP-PUR-005: write to the supplier with letter NBC-L-07 for certificates expiring within 90 days.", "letter template NBC-L-07"),
            ("If no new report has arrived 60 days before expiry, send a second reminder and tell the purchase manager. Under AMD-SUP-2026-02 no new order may be raised once fewer than 60 days remain.", "F-SOP5-2", "SOP-PUR-005: under AMD-SUP-2026-02 no new order once fewer than 60 days remain on the certificate.", "no new order may be raised once fewer than 60 days remain"),
            ("On expiry, e-mail all buyers with the subject CERT EXPIRED - DO NOT ORDER and the supplier's name and code.", "F-SOP5-3", "SOP-PUR-005: on expiry e-mail all buyers 'CERT EXPIRED - DO NOT ORDER'.", "CERT EXPIRED - DO NOT ORDER"),
            ("Upload the renewed certificate as a new row; never overwrite the old one.", None, None)])
    sop(c, f"{P}/SOP-PUR-006 Quotations and Supplier Selection v1.0.pdf", "Quotations and Supplier Selection", "SOP-PUR-006", "1.0", "2024-09-01", "Daniel Okafor (purchase manager)",
        "Henrik Weber (plant head)", [
            ("A new requirement above £100,000 gross needs three written quotations, compared on form NBC-F-118.", "F-SOP6-1", "SOP-PUR-006: new requirements above £100,000 gross need three written quotations on NBC-F-118.", None),
            ("Items with a current rate contract need no quotation: order at the contract rate (POL-PUR-001 §7.1).", None, None),
            ("A quotation from a supplier that is not in the supplier master starts the onboarding procedure (SOP-PUR-001). It may not be accepted until the supplier is onboarded.", "F-SOP6-2", "SOP-PUR-006: a quote from a supplier not in the master starts SOP-PUR-001 and cannot be accepted before onboarding.", None),
            ("For lithium-cell parts, compare quotations only from suppliers with a valid UN 38.3 certificate. Price alone never decides.", "F-SOP6-3", "SOP-PUR-006: for lithium-cell parts compare only certified suppliers; price alone never decides.", None)])

    gr = sop(c, f"{P}/sop_inv_001_goods_receipt_v2.docx", "Goods Receipt", "SOP-INV-001", "2.0", "2024-10-01", "Callum Shaw (stores manager)", "Henrik Weber (plant head)", [
        ("Check the supplier's delivery note against the purchase order number. Only released orders (RL) can be received; Ledgerline refuses others with ERR-GRN-0102.", None, None),
        ("On INV-GRN-03, type the PO number and press Fetch. Count the goods, enter the quantity received and the supplier's delivery note number in Remarks, and press Save.", "F-SOP-GRN-1", "SOP-INV-001: on INV-GRN-03 enter the delivery note number in Remarks.", None),
        ("A part delivery gets its own GRN. You cannot receive more than the order's balance (ERR-GRN-0204).", None, None),
        ("Lithium-cell parts are received into the quality hold warehouse WH-MAN-QC and stay there until Quality releases them to the fire-cell area of Manchester main stores.", "F-SOP-GRN-QC", "SOP-INV-001 v2.0 §5.4: lithium-cell parts are received into WH-MAN-QC until Quality releases them.", "Lithium-cell parts are received into the quality hold warehouse WH-MAN-QC"),
        ("Damaged packaging on a battery delivery: refuse the parcel, photograph it and tell Quality (SOP-QUA-002).", None, None)])
    gr.fmt = "docx"
    sop(c, f"{P}/SOP-INV-002 Returns to Vendor (RTV) v1.3.pdf", "Returns to Vendor (RTV)", "SOP-INV-002", "1.3", "2025-01-01", "Callum Shaw (stores manager)", "Henrik Weber (plant head)", [
        ("Raise the RTV on INV-RTV-07 against the GRN within 30 days of receipt (POL-RET-006 §2.1).", None, None),
        ("Move the goods to warehouse WH-MAN-RTV and label them with the RTV number.", "F-SOP-RTV-1", "SOP-INV-002: goods for return go to WH-MAN-RTV labelled with the RTV number.", None),
        ("If the GRN has been invoiced, Ledgerline refuses the RTV (ERR-RTV-0230): ask accounts payable for a debit note instead.", None, None),
        ("Battery packs are returned only through the carrier's dangerous-goods service with the UN3480 label.", None, None)])
    sop(c, f"{P}/SOP-INV-003 Stock Count v1.2.pdf", "Stock Count (cycle and annual)", "SOP-INV-003", "1.2", "2023-03-01", "Callum Shaw (stores manager)", "Grace Whitaker (financial controller)", [
        ("Cycle counts follow the cycle count plan (INV-CCP-14): A items every month, B items every quarter, C items twice a year.", "F-SOP-CNT-1", "SOP-INV-003: cycle counts A monthly, B quarterly, C twice a year.", None),
        ("Freeze the count area on INV-CNT-06 before counting. Ledgerline refuses to freeze an area with open transactions (ERR-CNT-0230).", None, None),
        ("A count whose variance by value is within 2% is posted. A larger variance needs a recount by a second person.", "F-SOP-CNT-TOL", "SOP-INV-003 v1.2 (2023) says a count within 2% by value is posted.", "A count whose variance by value is within 2% is posted."),
        ("The annual count is held on the last Saturday of March. Ledgerline is closed for stores transactions that day.", "F-SOP-CNT-2", "SOP-INV-003: the annual count is on the last Saturday of March.", None)])
    c.mess("contradiction", [f"{P}/SOP-INV-003 Stock Count v1.2.pdf", "08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf"],
           "SOP-INV-003 (2023) says counts within 2% are posted; Ledgerline 7.2.2 (June 2024) changed the cycle-count tolerance to 1.5% (INV.CNT_TOL_PCT). The SOP was never updated.")
    sop(c, f"{P}/SOP-INV-004 Battery Pack Storage and Handling v1.0.pdf", "Battery Pack Storage and Handling", "SOP-INV-004", "1.0", "2025-11-01", "Callum Shaw (stores manager)",
        "Pieter Jansen (quality manager)", [
            ("Put battery packs away only in fire cells BAT-Z1 to BAT-Z4. Check the cell's count board first: no more than 1,500 packs per cell (POL-BAT-004 §2.2).", None, None),
            ("Move packs only in their cartons on a pallet; never stack more than four cartons high.", "F-SOP-BAT-1", "SOP-INV-004: never stack battery cartons more than four high.", None),
            ("Issue packs first in, first out by the date on the carton label.", None, None),
            ("A dropped carton is quarantined even if it looks undamaged (SOP-QUA-002).", "F-SOP-BAT-2", "SOP-INV-004: a dropped carton is quarantined even if it looks undamaged.", None)])
    sop(c, f"{P}/SOP-AP-001 Three-Way Invoice Matching v2.1.pdf", "Three-Way Invoice Matching", "SOP-AP-001", "2.1", "2025-04-01", "Marta Kowalski (AP manager)", "Grace Whitaker (financial controller)", [
        ("Every supplier invoice is entered on AP-INV-01 against its purchase order. The three-way match (job JOB-AP-010) compares the invoice with the order and the receipts.", None, None),
        ("An invoice line is held for price (HOLD-PRC) when its rate differs from the order rate by more than 2% or by more than £50, whichever is smaller.", "F-AP1-TOL", "SOP-AP-001: price hold when rate differs by more than 2% or £50, whichever is smaller.", None),
        ("An invoice line is held for quantity (HOLD-QTY) when the quantity invoiced is more than the quantity received.", None, None),
        ("Only the AP manager may override a match (ERR-MAT-0420 for anyone else). The reason goes in the override comment.", "F-AP1-OVR", "SOP-AP-001: only the AP manager may override a match (ERR-MAT-0420).", None),
        ("Invoices from overseas suppliers on -RC tax codes carry no VAT from the supplier; Ledgerline accounts for the reverse charge.", None, None)])
    pc = sop(c, f"{P}/SOP-AP-002 Period Close v3.0.pdf", "Accounts Payable Period Close", "SOP-AP-002", "3.0", "2025-04-01", "Marta Kowalski (AP manager)", "Grace Whitaker (financial controller)", [
        ("Working day 1: the GRNI accrual job (JOB-AP-040) runs at 21:00.", None, None),
        ("Working day 3, 12:00: AP cut-off. Invoices received after the cut-off are posted to the next period.", "F-AP2-CUTOFF", "SOP-AP-002 v3.0 says the AP cut-off is working day 3 at 12:00.", "Working day 3, 12:00: AP cut-off."),
        ("Working day 3, afternoon: the AP manager closes the period on AP-PER-11. Ledgerline refuses the close while documents are unposted (ERR-PER-0010).", None, None),
        ("Working day 4: Finance reviews the reverse-charge listing (JOB-AP-045) for the VAT return.", None, None)])
    c.mess("email_overrides_sop", [pc.path, "09_email_archive/2026/2026-06-02_AP cut-off moves to working day 2.eml"],
           "SOP-AP-002 says the AP cut-off is working day 3; an e-mail from the financial controller moved it to working day 2 from June 2026. The SOP was never reissued.")
    sop(c, f"{P}/SOP-AP-003 Supplier Payment Run v1.4.pdf", "Supplier Payment Run", "SOP-AP-003", "1.4", "2024-06-01", "Marta Kowalski (AP manager)", "Grace Whitaker (financial controller)", [
        ("Payment runs are on Tuesdays and Thursdays. The proposal job (JOB-AP-030) runs at 10:00.", "F-AP3-DAYS", "SOP-AP-003: payment runs on Tuesdays and Thursdays; proposal at 10:00.", None),
        ("The AP clerk reviews the proposal on AP-PAY-03; the AP manager approves it. The approver may not be the proposer (ERR-PAY-0430).", None, None),
        ("The payment file (JOB-AP-031, format STD18) is released to the bank by 14:30 for same-day processing.", "F-AP3-FILE", "SOP-AP-003: payment file STD18 released by 14:30.", None),
        ("Suppliers with unverified bank details are left out automatically (ERR-BNK-0101).", None, None)])
    sop(c, f"{P}/SOP-AP-004 Supplier Bank Detail Changes v2.0.pdf", "Supplier Bank Detail Changes", "SOP-AP-004", "2.0", "2025-10-01", "Marta Kowalski (AP manager)", "Grace Whitaker (financial controller)", [
        ("Never accept a change of bank details by e-mail alone. Fraudsters copy real suppliers' e-mails.", None, None),
        ("Call the supplier back on a number taken from its letterhead, website or the supplier master, never from the request itself. Two people from AP must take part in the call.", "F-AP4-CALL", "SOP-AP-004: call back on a known number; two AP staff take part.", "Two people from AP must take part in the call."),
        ("Record the call on AP-BNK-06 (service bnk_verify). Until then the warning W-BNK-120 holds all payments to the supplier.", "F-AP4-HOLD", "SOP-AP-004: W-BNK-120 holds payments until the call-back is recorded.", None)])
    sop(c, f"{P}/SOP-SAL-001 Sales Order to Despatch v2.2.pdf", "Sales Order to Despatch", "SOP-SAL-001", "2.2", "2025-03-01", "Isla Morgan (sales manager)", "Henrik Weber (plant head)", [
        ("Enter the bike shop's order on SAL-SO-01 and confirm it. Confirmation runs the credit check (ERR-CRD-0207 if the limit is exceeded).", None, None),
        ("Orders confirmed by 15:30 are picked the same day and delivered next working day in the UK.", "F-SAL1-CUTOFF", "SOP-SAL-001: orders confirmed by 15:30 ship same day for next-day UK delivery.", None),
        ("Every parcel with a battery pack needs the lithium battery label printed before the despatch is posted (ERR-DLV-0320).", None, None),
        ("Book the carrier on SAL-FRT-12. Our contract carrier is Moorland Logistics; its dangerous-goods service is code DGX.", "F-SAL1-CARRIER", "SOP-SAL-001: contract carrier Moorland Logistics; dangerous-goods service code DGX.", None)])
    sop(c, f"{P}/SOP-SAL-002 Warranty Claims (RMA) v1.1.pdf", "Warranty Claims from Bike Shops", "SOP-SAL-002", "1.1", "2025-03-01", "Isla Morgan (sales manager)", "Pieter Jansen (quality manager)", [
        ("The bike shop raises the claim with the frame or pack serial number. The serial must be registered (SAL-SRL-16) or the claim is refused (ERR-RMA-0210).", None, None),
        ("Warranty periods are in POL-RET-006 §3.1.", None, None),
        ("Approved claims get an RMA number. The shop sends battery packs back only through the dangerous-goods service.", None, None),
        ("Quality decides within 10 working days of receipt whether to repair, replace or refuse.", "F-SAL2-10D", "SOP-SAL-002: Quality decides within 10 working days of receipt.", None)])
    sop(c, f"{P}/SOP-PRD-001 Work Order Release and Backflush v1.5.pdf", "Work Order Release and Backflush", "SOP-PRD-001", "1.5", "2024-11-01", "Stefan Berg (production planner)", "Henrik Weber (plant head)", [
        ("Release work orders on PRD-WO-01 at least two days before the start date. Release fails on a component shortage (ERR-WO-0310).", None, None),
        ("Components are issued by backflush (job JOB-PRD-015) when the work order's completions are posted, except battery packs, which are issued by serial on INV-MRN-08.", "F-PRD1-BAT", "SOP-PRD-001: battery packs are not backflushed; they are issued by serial on INV-MRN-08.", None),
        ("Close work orders within five working days of the last completion.", None, None)])
    sop(c, f"{P}/SOP-PRD-002 Engineering Change v1.0.pdf", "Engineering Change (ECN)", "SOP-PRD-002", "1.0", "2024-02-01", "Stefan Berg (production planner)", "Henrik Weber (plant head)", [
        ("Raise the change on PRD-ECN-06 with the effective date. Quality and Purchasing approve.", None, None),
        ("A change to a lithium-cell part (new cell maker, new design) needs a fresh UN 38.3 report before release (POL-SUP-003 §4.6).", "F-PRD2-CELL", "SOP-PRD-002: a change to a lithium-cell part needs a fresh UN 38.3 report before release.", None),
        ("Ledgerline refuses to release an ECN while work orders are open on the old revision (ERR-ECN-0220).", None, None)])
    sop(c, f"{P}/SOP-QUA-001 Incoming Inspection v2.0.pdf", "Incoming Inspection", "SOP-QUA-001", "2.0", "2024-04-01", "Pieter Jansen (quality manager)", "Henrik Weber (plant head)", [
        ("Inspect on QA-INS-01 at the AQL in POL-QUA-005 §3.1.", None, None),
        ("For every sample battery pack, record the open-circuit voltage. A pack below 30% state of charge or above 50% is rejected (POL-BAT-004 §2.3).", "F-QUA1-OCV", "SOP-QUA-001: sample packs outside 30-50% state of charge are rejected.", None),
        ("Raise an NCR on QA-NCR-02 for every rejected lot.", None, None)])
    sop(c, f"{P}/SOP-QUA-002 Damaged Battery Pack Quarantine v1.1.pdf", "Damaged Battery Pack Quarantine", "SOP-QUA-002", "1.1", "2025-11-01", "Pieter Jansen (quality manager)", "Henrik Weber (plant head)", [
        ("Move the pack to the red quarantine bin in fire cell BAT-Z4 at once. Wear gloves and eye protection.", None, None),
        ("Raise an NCR on QA-NCR-02 in the same shift, with photographs.", None, None),
        ("Book the pack to quality hold on INV-QCH-11 so it cannot be issued.", "F-QUA2-QCH", "SOP-QUA-002: book damaged packs to quality hold on INV-QCH-11.", None),
        ("Quality decides within 24 hours: return to supplier, refurbish (PRD-09) or recycle.", None, None)])
    sop(c, f"{P}/SOP-IT-001 User Access Request v1.6.pdf", "User Access Request", "SOP-IT-001", "1.6", "2025-09-01", "Rhys Pryce (IT manager)", "Henrik Weber (plant head)", [
        ("Ask for Ledgerline access on form NBC-F-031, signed by your line manager.", "F-IT1-F031", "SOP-IT-001: Ledgerline access is requested on form NBC-F-031.", None),
        ("IT gives one role per user, matching the job. The approval limit is set from the approval matrix (POL-APR-002).", None, None),
        ("Default cost centres are set by IT and are not changed automatically when Finance closes a cost centre. The cost centre owner must ask IT on NBC-F-031.", None, None),
        ("Access is reviewed every six months by each manager.", "F-IT1-REVIEW", "SOP-IT-001: access reviewed every six months.", None)])
    sop(c, f"{P}/SOP-IT-002 Service Account Management v1.0.pdf", "Service Account Management", "SOP-IT-002", "1.0", "2025-09-01", "Rhys Pryce (IT manager)", "Henrik Weber (plant head)", [
        ("Every service account has a named owner and a written list of the services it needs.", None, None),
        ("Service account keys (SYS-API-14) are valid for at most 90 days and rotated before expiry.", "F-IT2-KEY", "SOP-IT-002: service account keys valid at most 90 days.", None),
        ("A service account never approves documents (POL-APR-002 §4.2).", None, None),
        ("The quarterly review (JOB-SYS-015) is signed off by the IT manager.", None, None)])
    sop(c, f"{P}/SOP-FIN-001 Cost Centre Open and Close v1.1.pdf", "Cost Centre Open and Close", "SOP-FIN-001", "1.1", "2025-01-01", "Grace Whitaker (financial controller)", "Henrik Weber (plant head)", [
        ("Finance opens and closes cost centres on FIN-CC-01 at the start and end of each production programme.", None, None),
        ("Finance tells the buyers 10 working days before closing a cost centre.", "F-FIN1-10D", "SOP-FIN-001: Finance gives buyers 10 working days' notice before closing a cost centre.", None),
        ("Ledgerline does not change users' default cost centres when one is closed; owners must ask IT (SOP-IT-001).", None, None),
        ("A cost centre with open documents cannot be closed (ERR-CC-0310) until they are moved or cancelled.", None, None)])
