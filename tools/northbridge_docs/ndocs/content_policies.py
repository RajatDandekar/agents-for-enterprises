"""01_policies: the core policies used in Lectures 1-2 (imported from ledgerline/docs, unchanged in substance),
their older versions, the amendments, and the company's other policies, including the confidential HR folder."""
from __future__ import annotations

import os

from .ctx import md_to_doc, plant
from .model import Book, Doc, Sheet

DOCS = os.environ.get("NB_LEDGER_DOCS", "/course/ledgerline/ledgerline/docs")
P = "01_policies"

# Leftovers from the course's old world that slipped through the mechanical rename. The dump carries the corrected
# wording; the meaning of every rule is unchanged.
FIX_SUP = [("(for example an UN 38.3-notified laboratory), or a BIS conformity certificate for stainless steel grade 304 or better.",
            "(for example a laboratory accredited to ISO/IEC 17025 for UN 38.3 testing)."),
           ("If the supplier changes the material or the compound of a part (for example a new silicone grade), it must give a fresh test report for that part.",
            "If the supplier changes the cells or the design of a part (for example a new cell maker or cell chemistry), it must give a fresh test report for that part."),
           ('(for example "Voltway Polymer Industries" for Voltway Cells)', '(for example "Voltway Cells B.V." or "VoltWay" for Voltway Cells)')]
FIX_AMD_SUP = [("failed our own migration test. The compound had changed in the meantime.",
                "failed our own incoming abuse test. The cell maker had changed in the meantime.")]
FIX_MAN = [("### 111.00 Quantity against the request", "### 11.10 Quantity against the request"),
           ("ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (GJ)", "ERR-PO-0412 TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (NL)"),
           ('so "5l battery pack" and "5 L Battery pack" find the same items', 'so "36v battery" and "36 V Battery" find the same items'),
           ('"Voltway Polymer Industries" will not find "Voltway Cells"', '"VoltWay Cell" will not find "Voltway Cells"')]


def read(name):
    with open(os.path.join(DOCS, name), encoding="utf-8") as f:
        return f.read()


def build(c):
    purchase_policy(c)
    supplier_policy(c)
    approval_matrix(c)
    other_policies(c)
    hr(c)


# ------------------------------------------------------------------------------------------------ purchase policy
PUR_HISTORY = [["1.0", "1998-09-01", "R. Ainsworth", "First issue, with the Ledgerline 5 roll-out"],
               ["2.0", "2004-04-01", "G. Sutcliffe", "Rewritten for Ledgerline 6; requests before orders"],
               ["3.0", "2019-04-01", "G. Sutcliffe", "Ledgerline 7.1 migration; direct-order limit £30,000"],
               ["4.0", "2025-04-01", "D. Okafor", "Direct-order limit £50,000; UN 38.3 rule for battery packs and hub motors; price tolerance 5%"],
               ["4.1", "2026-04-01", "D. Okafor", "§6.2 extended to chargers; §6.4 added; §7.2 price tolerance reduced from 5% to 2%"]]


def purchase_policy(c):
    md = read("purchase-policy.md")
    d = md_to_doc(md, f"{P}/POL-PUR-001_Purchase_Policy_v4.1.pdf", approver="Henrik Weber (plant head)", history=PUR_HISTORY)
    c.add(d)
    plant(d, "F-PUR-6.2", "Purchase Policy §6.2: lithium-cell parts may be bought only from a supplier holding a valid UN 38.3 certificate on file in Ledgerline, uploaded and checked before the first order; an expired certificate counts as no certificate.",
          "may be bought only from a supplier holding a valid UN 38.3 certificate on file in Ledgerline")
    plant(d, "F-PUR-6.2b", "Purchase Policy §6.2: the certificate must be uploaded and checked before the first order is placed.",
          "The certificate must be uploaded and checked before the first order is placed. An expired certificate counts as no certificate.")
    plant(d, "F-PUR-6.2-scope", "Purchase Policy §6.2 lists battery packs, hub motors, chargers and any item marked lithium-cell in the item master.",
          "(battery packs, hub motors, chargers and any other item marked lithium-cell in the item master)")
    plant(d, "F-PUR-6.4", "Purchase Policy §6.4: a cheaper quotation from a new supplier does not by itself justify a change of supplier for a lithium-cell part.",
          "A cheaper quotation from a new supplier does not by itself justify a change of supplier for a lithium-cell part.")
    plant(d, "F-PUR-6.1", "Purchase Policy §6.1: orders only with suppliers active in the supplier master.", "Orders may be placed only with suppliers that are active in the supplier master.")
    plant(d, "F-PUR-6.3", "Purchase Policy §6.3: a new supplier is onboarded under the Supplier Policy POL-SUP-003 before any order.",
          "A new supplier is onboarded under the Supplier Policy (POL-SUP-003) before any order is placed with them.")
    plant(d, "F-PUR-3.3", "Purchase Policy §3.3: a direct order without a request is allowed only up to £50,000 gross including VAT.",
          "A direct purchase order without a request is allowed only when its gross value, including VAT, is £50,000 or less.")
    plant(d, "F-PUR-3.4", "Purchase Policy §3.4: an order against a request may not exceed the requested quantity.",
          "A purchase order raised against a request may not exceed the requested quantity.")
    plant(d, "F-PUR-4.2", "Purchase Policy §4.2: an order against a closed cost centre is saved as a Draft, which is never sent to the supplier.",
          "Ledgerline saves an order against a closed cost centre as a Draft; a Draft order is never sent to the supplier.")
    plant(d, "F-PUR-5.1", "Purchase Policy §5.1: approval limits apply to the gross value including VAT.", "Limits apply to the gross value including VAT, not the basic value.")
    plant(d, "F-PUR-5.3", "Purchase Policy §5.3: nobody may approve an order they raised.", "Nobody may approve an order they raised.")
    plant(d, "F-PUR-5.4", "Purchase Policy §5.4: approval of a request covers the order raised against it if the approver's limit covers the order's gross value.",
          "Approval of a purchase request covers the purchase order raised against it, provided the approver's limit covers the order's gross value.")
    plant(d, "F-PUR-7.1", "Purchase Policy §7.1: use the current rate contract rate; older order rates are reference only.",
          "Use the rate in the current rate contract. Rates from older orders in the order history are for reference only.")
    plant(d, "F-PUR-7.2", "Purchase Policy §7.2 (v4.1): an order at a rate more than 2% above the contract rate needs the manager's written reason in the remarks.",
          "Any order at a rate more than 2% above the contract rate needs the manager's written reason in the remarks.")
    plant(d, "F-PUR-8.1", "Purchase Policy §8.1: UK suppliers get UK VAT codes (-UK); suppliers in any other country get reverse-charge codes (-RC).",
          "A supplier in any other country is charged VAT by reverse charge (tax codes ending -RC).")
    plant(d, "F-PUR-9.2", "Purchase Policy §9.2: do not tell a requester an order is placed until it is Released.",
          "Purchase staff must not tell a requester that an order has been placed until its status in Ledgerline is Released.")
    d.h(1, "Appendix A. Definitions")
    d.table(["Term", "Meaning"], [["Gross value", "Basic value plus VAT, including freight and packing charged on the order"],
                                  ["Lithium-cell part", "An item with the lithium-cell flag (cell_safety = 1) in the item master"],
                                  ["Rate contract", "An agreed price for a supplier and item for a period, held in Ledgerline"],
                                  ["Direct order (DIR)", "An order without a purchase request, allowed only under §3.3"],
                                  ["Released (RL)", "The only status in which the supplier has the order"]])
    c.filler(d, "Appendix B. Questions staff ask about this policy", 700,
             context=md[md.index("## 3."):][:3000],
             brief="Write a short set of frequently asked questions and plain answers about this policy, as '### ' question "
                   "headings with short answers. Refer to section numbers only as they appear above. Do not add figures.")
    d.h(1, "Appendix C. Related documents")
    d.bullets(["POL-SUP-003 Supplier Policy", "POL-APR-002 Approval Matrix for Purchasing", "AMD-PUR-2026-03 Amendment 3 (direct-order limit from 1 December 2026)",
               "AMD-SUP-2026-02 Amendment 2 to the Supplier Policy (certificate window)", "SOP-PUR-001 Supplier onboarding",
               "SOP-PUR-002 Purchase request to purchase order", "MAN-PUR-72 Ledgerline 7.2 User Manual, Purchasing"])

    # v4.0: superseded on 1 April 2026 but still on the share, as a Word file
    md40 = md.replace("version: 4.1", "version: 4.0").replace("effective: 2026-04-01", "effective: 2025-04-01")
    md40 = md40.replace("(battery packs, hub motors, chargers and any other item marked lithium-cell in the item master)",
                        "(battery packs, hub motors and any other item marked lithium-cell in the item master)")
    md40 = md40.replace("more than 2% above the contract rate", "more than 5% above the contract rate")
    md40 = md40.replace("6.4 Prefer the supplier with a current rate contract. A cheaper quotation from a new supplier does not by itself justify a change of supplier for a lithium-cell part.\n", "")
    d40 = md_to_doc(md40, f"{P}/old/Purchase Policy v4.0.docx", status="SUPERSEDED", history=PUR_HISTORY[:4])
    d40.meta["docx_author"] = "Daniel Okafor"
    c.add(d40)
    plant(d40, "F-PUR40-7.2", "Purchase Policy v4.0 (superseded 1 Apr 2026) §7.2 allowed 5% above contract before a reason was needed.",
          "more than 5% above the contract rate needs the manager's written reason")
    plant(d40, "F-PUR40-6.2", "Purchase Policy v4.0 §6.2 listed only battery packs and hub motors (no chargers).",
          "(battery packs, hub motors and any other item marked lithium-cell in the item master)")
    c.mess("superseded", [d40.path, d.path], "Purchase Policy v4.0 (superseded 1 Apr 2026) is still on the share next to v4.1. It allows 5% above contract (v4.1: 2%) and its §6.2 does not name chargers.")
    c.mess("near_duplicate", [d40.path, d.path], "v4.0 and v4.1 are near-duplicates: same structure, three clauses differ.")

    # v3.0 (2019): older still, different limits
    d30 = Doc(f"{P}/old/purchase_policy_v3_2019.docx", "Purchase Policy", doc_id="POL-PUR-001", version="3.0", effective="2019-04-01",
              owner="Purchase department", status="SUPERSEDED", history=PUR_HISTORY[:3])
    d30.meta["docx_author"] = "Graham Sutcliffe"
    c.section(d30, "1. Purpose", paras=["This policy sets out how Northbridge Cycles buys materials, components and services through Ledgerline ERP 7.1."], words=120)
    c.section(d30, "3. Requests before orders", facts=[
        ("3.3 A direct purchase order without a request is allowed only when its gross value, including VAT, is £30,000 or less.",
         "F-PUR30-3.3", "Purchase Policy v3.0 (2019, superseded) set the direct-order limit at £30,000.")], words=150)
    c.section(d30, "5. Approval limits", paras=["5.1 Approval limits are set on each user by IT from the approval matrix in force."], words=150)
    c.section(d30, "6. Supplier qualification", paras=["6.2 Battery packs may be bought only from a supplier holding a valid UN 38.3 certificate. Hub motors and chargers are not covered by this clause."], words=160)
    c.add(d30)
    c.mess("superseded", [d30.path], "Purchase Policy v3.0 (2019) is still on the share: direct-order limit £30,000, UN 38.3 for battery packs only.")

    # Amendment 3 (future-dated: in force from 1 Dec 2026)
    a3 = md_to_doc(read("amendment-pur-2026-03.md"), f"{P}/AMD-PUR-2026-03_Amendment3_PurchasePolicy_DIRlimit.pdf",
                   history=[["1.0", "2026-10-12", "D. Okafor", "Issued; in force from 1 December 2026"]], status="ISSUED, NOT YET IN FORCE")
    c.add(a3)
    plant(a3, "F-AMD3-1.1", "Amendment 3 (AMD-PUR-2026-03): from 1 December 2026 the direct-order limit falls to £25,000 gross.",
          "A direct purchase order without a request is allowed only when its gross value, including VAT, is £25,000 or less.")
    plant(a3, "F-AMD3-1.2", "Amendment 3: until 30 November 2026 the limit stays at £50,000.", "Until 30 November 2026 the limit in §3.3 stays at £50,000.")
    plant(a3, "F-AMD3-3.1", "Amendment 3: IT changes the Ledgerline limit on the evening of 30 November 2026; from 1 December a direct order above £25,000 is refused with ERR-PO-0610.",
          "From 1 December, a direct order above £25,000 gross will be refused with ERR-PO-0610.")
    plant(a3, "F-AMD3-2.1", "Amendment 3: the audit found 212 direct orders between £25,000 and £50,000.", "found 212 direct orders between £25,000 and £50,000")
    c.mess("future_dated", [a3.path, d.path], "AMD-PUR-2026-03 is issued but in force only from 1 Dec 2026 (after the sandbox date of 26 Oct 2026); the policy it amends still says £50,000.")


# ------------------------------------------------------------------------------------------------ supplier policy
SUP_HISTORY = [["1.0", "2004-04-01", "G. Sutcliffe", "First issue"], ["2.0", "2019-04-01", "G. Sutcliffe", "Ledgerline 7 codes; duplicate checks"],
               ["2.2", "2025-04-01", "L. Moreno", "UN 38.3 certificates (§4)"], ["2.3", "2026-04-01", "L. Moreno", "§4.7 added; §6.2 name variants"]]


def supplier_policy(c):
    md = read("supplier-policy.md")
    d = md_to_doc(md, f"{P}/POL-SUP-003 Supplier Policy v2.3.pdf", fixes=FIX_SUP, approver="Daniel Okafor (purchase manager)", history=SUP_HISTORY)
    c.add(d)
    plant(d, "F-SUP-3.2", "Supplier Policy §3.2: before creating a supplier collect the VAT registration certificate, company registration number, bank letter, proof of insurance and the signed Supplier Code of Conduct.",
          "the VAT registration certificate (VAT number), the company registration number, a bank letter confirming the account, proof of insurance, and the signed Supplier Code of Conduct")
    plant(d, "F-SUP-3.3", "Supplier Policy §3.3: search the supplier master first by name, city and VAT number on PUR-SUP-03 and attach the result.",
          "The proposer must search the supplier master first (screen PUR-SUP-03) by name, by city and by VAT number")
    plant(d, "F-SUP-3.4", "Supplier Policy §3.4: the purchase manager approves the onboarding file before the supplier is created.",
          "The purchase manager approves the onboarding file. Only after that approval may the supplier be created in Ledgerline.")
    plant(d, "F-SUP-3.5", "Supplier Policy §3.5: a new supplier is ACTIVE at once but no order until all documents and, for lithium-cell parts, the certificate are on file.",
          "no order may be placed with it until every document in §3.2 and, for lithium-cell parts, the certificate in §4 is on file")
    plant(d, "F-SUP-3.6", "Supplier Policy §3.6: onboarding normally takes five working days from a complete file.",
          "Onboarding normally takes five working days from a complete file.")
    plant(d, "F-SUP-4.3", "Supplier Policy §4.3: the certificate is uploaded against the supplier as type UN38.3 with document reference and valid-to date, and checked by the senior buyer before the first order.",
          "The certificate is uploaded in Ledgerline against the supplier (certificate type UN38.3) with its document reference and its valid-to date, and checked by the senior buyer before the first order.")
    plant(d, "F-SUP-4.4", "Supplier Policy §4.4 (v2.3 text, replaced from 1 Sep 2026 by AMD-SUP-2026-02): certificate accepted if issued within 24 months and not expired.",
          "A UN 38.3 certificate is accepted if it was issued within the last 24 months and its valid-to date has not passed.")
    plant(d, "F-SUP-4.5", "Supplier Policy §4.5: an expired certificate counts as no certificate; the supplier stays ACTIVE but no lithium-cell part may be ordered.",
          "An expired certificate counts as no certificate. The supplier stays ACTIVE in the master, but no lithium-cell part may be ordered from it")
    plant(d, "F-SUP-4.7", "Supplier Policy §4.7: Ledgerline does not stop an order to a supplier without a certificate; the raiser and the approver do the check.",
          "Ledgerline does not stop an order to a supplier without a certificate.")
    plant(d, "F-SUP-5.2", "Supplier Policy §5.2: Ledgerline refuses new orders to a blocked supplier with ERR-SUP-0031.",
          "A blocked supplier keeps its code and history, but Ledgerline refuses new orders to it with ERR-SUP-0031.")
    plant(d, "F-SUP-5.4", "Supplier Policy §5.4: VC-EIN-0009 is Voltway Cells' old blocked code.", "Voltway Cells' old code VC-EIN-0009 is an example.")
    plant(d, "F-SUP-6.1", "Supplier Policy §6.1: the VAT number is the test of sameness.", "The VAT number is the test of sameness: two records with the same VAT number are the same supplier.")
    plant(d, "F-SUP-6.3", "Supplier Policy §6.3: Voltway Paints & Coatings, Rotterdam, is not Voltway Cells, Eindhoven.",
          "Voltway Paints & Coatings, Rotterdam, is not Voltway Cells, Eindhoven")
    plant(d, "F-SUP-6.4", "Supplier Policy §6.4: Ledgerline refuses a second supplier with the same VAT number (ERR-SUP-0118) but does not catch a duplicate entered without a VAT number.",
          "Ledgerline refuses to create a second supplier with a VAT number that is already registered (ERR-SUP-0118).")
    plant(d, "F-SUP-7.3", "Supplier Policy §7.3: rate contracts are reviewed every six months, in March and September.",
          "Rate contracts are reviewed every six months, in March and September.")
    plant(d, "F-SUP-8.2", "Supplier Policy §8.2: a supplier above 2% rejections for two quarters in a row is put on watch and visited by Quality.",
          "A supplier with a rejection rate above 2% for two quarters in a row is put on watch and visited by Quality.")
    plant(d, "F-SUP-2.2", "Supplier Policy §2.2: one-time cash purchases under £5,000 from petty cash are outside the policy.",
          "It does not cover one-time cash purchases under £5,000 made from the petty-cash imprest")
    c.filler(d, "Appendix A. Guidance for proposers", 600, context=md[md.index("## 3."):md.index("## 5.")],
             brief="Write practical guidance for a purchase executive preparing a supplier onboarding file, as '### ' sub-headings and "
                   "short paragraphs. Do not add figures or new requirements.")
    # an exact copy someone saved again
    c.copy(d.path, f"{P}/POL-SUP-003 Supplier Policy v2.3 (1).pdf")
    c.mess("duplicate", [d.path, f"{P}/POL-SUP-003 Supplier Policy v2.3 (1).pdf"], "Byte-identical copy of the Supplier Policy saved twice.")
    # v2.2 as an old Word file
    md22 = md.replace("version: 2.3", "version: 2.2").replace("4.7 Ledgerline does not stop an order to a supplier without a certificate. The check in this section is done by the person raising the order, and by the approver.\n", "")
    d22 = md_to_doc(md22, f"{P}/old/Supplier_Policy_v2.2.docx", fixes=FIX_SUP, status="SUPERSEDED", history=SUP_HISTORY[:3])
    d22.effective = "2025-04-01"
    c.add(d22)
    c.mess("near_duplicate", [d22.path, d.path], "Supplier Policy v2.2 (2025) and v2.3 (2026): v2.2 lacks §4.7.")

    a2 = md_to_doc(read("amendment-sup-2026-02.md"), f"{P}/AMD-SUP-2026-02 Amendment 2 Supplier Policy.pdf", fixes=FIX_AMD_SUP,
                   history=[["1.0", "2026-08-14", "L. Moreno", "Issued"]])
    c.add(a2)
    plant(a2, "F-AMD2-1.1", "AMD-SUP-2026-02 (from 1 Sep 2026): a UN 38.3 certificate is accepted only if issued within the last 12 months and valid at least 60 days after the order date.",
          "A UN 38.3 certificate is accepted only if it was issued within the last 12 months, and its valid-to date is at least 60 days after the date the order is placed.")
    plant(a2, "F-AMD2-1.2", "AMD-SUP-2026-02: a certificate meeting only the old rule counts as no certificate for new orders from 1 Sep 2026.",
          "counts as no certificate for new orders from 1 September 2026")
    plant(a2, "F-AMD2-3.2", "AMD-SUP-2026-02 §3.2: the senior buyer runs the certificate-expiry report on the first working day of each month with a 90-day window.",
          "The senior buyer runs the certificate-expiry report (MAN-PUR-72 §22.6) on the first working day of each month with 90 days as the window")
    c.mess("contradiction", [a2.path, d.path], "Supplier Policy v2.3 §4.4 says 24 months and not expired; AMD-SUP-2026-02 replaced it from 1 Sep 2026 with 12 months and 60 days' margin. The policy PDF was not reissued.")


# ------------------------------------------------------------------------------------------------ approval matrix
def approval_matrix(c):
    md = read("approval-matrix.md")
    d = md_to_doc(md, f"{P}/POL-APR-002 Approval Matrix v3.0.pdf", approver="Henrik Weber (plant head)",
                  history=[["1.0", "2015-03-01", "G. Sutcliffe", "First issue for Ledgerline 7.0"], ["2.0", "2024-04-01", "D. Okafor", "Limits revised"],
                           ["3.0", "2026-04-01", "D. Okafor", "Limits revised; service accounts §4.2"]])
    c.add(d)
    d.fact("F-APR-EXEC", "Approval matrix v3.0 §3.1: purchase executive (PUR-EXEC) limit £250,000 gross incl. VAT.", ["PUR-EXEC", "Purchase executive", "£250,000"], section="3. The limits")
    d.fact("F-APR-SR", "Approval matrix v3.0 §3.1: senior buyer (PUR-SR) limit £500,000.", ["PUR-SR", "Senior buyer", "£500,000"], section="3. The limits")
    d.fact("F-APR-MGR", "Approval matrix v3.0 §3.1: purchase manager (PUR-MGR) limit £1,000,000.", ["PUR-MGR", "Purchase manager", "£1,000,000"], section="3. The limits")
    d.fact("F-APR-PH", "Approval matrix v3.0 §3.1: plant head (PLANT-HEAD) limit £5,000,000.", ["PLANT-HEAD", "Plant head", "£5,000,000"], section="3. The limits")
    d.fact("F-APR-STORES", "Approval matrix v3.0 §3.1: stores has no approval authority.", ["STORES", "no approval authority"], section="3. The limits")
    plant(d, "F-APR-2.1", "Approval matrix §2.1: limits are on the gross value incl. VAT; freight and packing count.", "Freight and packing charged on the order count towards the gross value.")
    plant(d, "F-APR-2.3", "Approval matrix §2.3: orders for the same item from the same supplier within seven days are one requirement (no splitting).",
          "Orders for the same item from the same supplier raised within seven days of each other are treated as one requirement.")
    plant(d, "F-APR-3.4", "Approval matrix §3.4: above £5,000,000 the Managing Director approves in writing outside Ledgerline; Ledgerline shows ERR-APR-0009.",
          "Above £5,000,000 the order needs the Managing Director's written approval outside Ledgerline.")
    plant(d, "F-APR-4.2", "Approval matrix §4.2: service accounts such as SVC_AGENT have no approval authority; documents they approve are treated as unapproved.",
          "Integration and service accounts (role SYS-ADMIN, for example SVC_AGENT) have no approval authority under this matrix")
    plant(d, "F-APR-4.3", "Approval matrix §4.3: delegation in writing to the same or higher role only.", "Delegation to a lower role is not allowed.")
    plant(d, "F-APR-5.1", "Approval matrix §5.1: 2,000 packs at £119.00: basic £238,000, VAT £47,600, gross £285,600, above Emma's £250,000, so Daniel Okafor approves.",
          "basic £238,000, VAT 20% £47,600, gross £285,600")
    old = Doc(f"{P}/old/Approval_Matrix_v2.0_2024.docx", "Approval Matrix for Purchasing", doc_id="POL-APR-002", version="2.0",
              effective="2024-04-01", owner="Plant head's office", status="SUPERSEDED")
    old.meta["docx_author"] = "Daniel Okafor"
    old.h(1, "3. The limits")
    old.p("3.1 Each role's approval limit, gross including VAT:")
    old.table(["Role code", "Role", "Limit (gross incl. VAT)"], [["PUR-EXEC", "Purchase executive", "£200,000"], ["PUR-SR", "Senior buyer", "£400,000"],
                                                                 ["PUR-MGR", "Purchase manager", "£750,000"], ["PLANT-HEAD", "Plant head", "£5,000,000"]])
    old.fact("F-APR20-EXEC", "Approval matrix v2.0 (2024, superseded) gave the purchase executive £200,000.", ["Purchase executive", "£200,000"], section="3. The limits")
    c.section(old, "4. Who may not approve", paras=["4.1 Nobody may approve a document they raised."], words=150)
    c.add(old)
    c.mess("superseded", [old.path, d.path], "Approval matrix v2.0 (2024) still present: executive £200,000, senior buyer £400,000, manager £750,000. v3.0 (2026) raised them.")


# ------------------------------------------------------------------------------------------------ the other policies
def policy(c, path, title, doc_id, version, effective, owner, approver, sections, history=None, status="CURRENT", fmt_style="policy",
           classification="INTERNAL", purpose_words=180):
    d = Doc(path, title, doc_id=doc_id, version=version, effective=effective, owner=owner, approver=approver, status=status,
            classification=classification, style=fmt_style, history=history or [["1.0", effective, owner, "First issue"]])
    for s in sections:
        c.section(d, s[0], facts=s[1], words=s[2] if len(s) > 2 else 300, brief=s[3] if len(s) > 3 else "",
                  paras=s[4] if len(s) > 4 else ())
    c.add(d)
    return d


def other_policies(c):
    policy(c, f"{P}/POL-BAT-004 Battery Safety and Handling Policy v1.2.pdf", "Battery Safety and Handling Policy", "POL-BAT-004", "1.2", "2025-11-01",
           "Quality department", "Henrik Weber (plant head)", [
               ("1. Purpose and scope", [("1.1 This policy covers every lithium-cell part at Northbridge: battery packs, cells, hub and mid-drive motors, chargers and any item with the lithium-cell flag in the item master. Buying these parts is covered by Purchase Policy POL-PUR-001 §6.2 and Supplier Policy POL-SUP-003 §4.",
                                          "F-BAT-1.1", "Battery Safety Policy §1.1 refers buying of lithium-cell parts to Purchase Policy §6.2 and Supplier Policy §4.", "Buying these parts is covered by Purchase Policy POL-PUR-001 §6.2 and Supplier Policy POL-SUP-003 §4.")], 260),
               ("2. Storage", [("2.1 Battery packs are stored in the fire-cell area inside Manchester main stores (bin zones BAT-Z1 to BAT-Z4). In Ledgerline they are booked to warehouse WH-MAN-STR. The old code WH-MAN-BAT was merged into WH-MAN-STR in 2019 and must not be used.",
                                "F-BAT-2.1", "Battery packs are physically in fire cells BAT-Z1 to BAT-Z4 inside Manchester main stores and booked to WH-MAN-STR; WH-MAN-BAT is an old merged code.", "In Ledgerline they are booked to warehouse WH-MAN-STR."),
                               ("2.2 No more than 1,500 packs may be stored in one fire cell, so the Manchester fire-cell area holds at most 6,000 packs.",
                                "F-BAT-2.2", "Battery Safety Policy §2.2: at most 1,500 packs per fire cell; Manchester's fire-cell area holds at most 6,000 packs.", "No more than 1,500 packs may be stored in one fire cell, so the Manchester fire-cell area holds at most 6,000 packs."),
                               ("2.3 Packs are kept at a state of charge between 30% and 50% while in store. Stores staff must never charge a pack in the store.",
                                "F-BAT-2.3", "Battery Safety Policy §2.3: packs are stored at 30-50% state of charge and never charged in store.", "Packs are kept at a state of charge between 30% and 50% while in store.")], 380),
               ("3. Damaged packs", [("3.1 A damaged, swollen, wet or dropped pack is moved at once to the red quarantine bin in fire cell BAT-Z4 and reported to Quality in the same shift with a non-conformance report on screen QA-NCR-02.",
                                      "F-BAT-3.1", "Battery Safety Policy §3.1: damaged/swollen/dropped packs go to the red quarantine bin in BAT-Z4 and are reported the same shift on QA-NCR-02.", "red quarantine bin in fire cell BAT-Z4")], 330),
               ("4. Transport", [("4.1 A pack shipped on its own is sent as UN3480 (lithium-ion batteries). A pack fitted to a bike, or packed with it, is sent as UN3481. Every parcel with a pack carries the lithium battery handling label (item PKG-LBL-UN).",
                                  "F-BAT-4.1", "Battery Safety Policy §4.1: packs shipped alone go as UN3480; packs in or with a bike as UN3481; label PKG-LBL-UN.", "A pack shipped on its own is sent as UN3480 (lithium-ion batteries).")], 300),
               ("5. Training", [("5.1 Everyone who handles packs completes the battery-handling course BHT-01 before their first shift in the fire-cell area and again every 24 months.",
                                 "F-BAT-5.1", "Battery Safety Policy §5.1: course BHT-01 before the first shift and every 24 months.", "completes the battery-handling course BHT-01 before their first shift in the fire-cell area and again every 24 months")], 240),
               ("6. Records", [], 200)],
           history=[["1.0", "2023-02-01", "P. Jansen", "First issue"], ["1.1", "2024-06-01", "P. Jansen", "Transport section"], ["1.2", "2025-11-01", "P. Jansen", "Fire-cell capacity; BHT-01"]])

    policy(c, f"{P}/POL-QUA-005 Quality Policy v3.0.pdf", "Quality Policy", "POL-QUA-005", "3.0", "2024-04-01", "Quality department", "Henrik Weber (plant head)", [
        ("1. Our commitment", [], 300),
        ("2. Certification", [("2.1 Northbridge Cycles is certified to ISO 9001:2015 for the design and manufacture of electric bicycles. The current certificate runs to 31 May 2027.",
                               "F-QUA-2.1", "Quality Policy: Northbridge's ISO 9001:2015 certificate runs to 31 May 2027.", "The current certificate runs to 31 May 2027.")], 220),
        ("3. Incoming inspection", [("3.1 Lithium-cell parts are inspected at acceptable quality level (AQL) 0.65; all other parts at AQL 1.5. Every sample battery pack also gets an open-circuit voltage check.",
                                     "F-QUA-3.1", "Quality Policy §3.1: lithium-cell parts at AQL 0.65, others at AQL 1.5, plus an OCV check on every sample pack.", "Lithium-cell parts are inspected at acceptable quality level (AQL) 0.65; all other parts at AQL 1.5.")], 350),
        ("4. Supplier quality", [("4.1 A supplier whose rejection rate is above 2% for two quarters in a row is put on watch (Supplier Policy POL-SUP-003 §8.2).", "F-QUA-4.1", "Quality Policy §4.1 restates the 2% two-quarter watch rule.", None)], 300),
        ("5. Non-conformance", [], 300), ("6. Continual improvement", [], 280)])

    policy(c, f"{P}/POL-RET-006 Returns Policy v2.1.pdf", "Returns Policy", "POL-RET-006", "2.1", "2025-01-01", "Purchase and Sales departments", "Henrik Weber (plant head)", [
        ("1. Scope", [], 200),
        ("2. Returns to suppliers", [("2.1 Faulty or wrong goods are returned to the supplier within 30 days of receipt, on a return to vendor (RTV) document on screen INV-RTV-07.",
                                      "F-RET-2.1", "Returns Policy §2.1: returns to supplier within 30 days of receipt on an RTV (INV-RTV-07).", None),
                                     ("2.2 If the supplier's invoice for the goods has already been posted, raise a debit note on screen AP-DBN-04 instead of an RTV credit. Ledgerline refuses an RTV against an invoiced receipt with ERR-RTV-0230.",
                                      "F-RET-2.2", "Returns Policy §2.2: invoiced receipt: debit note on AP-DBN-04; RTV refused with ERR-RTV-0230.", None)], 350),
        ("3. Warranty returns from bike shops", [("3.1 Frames carry a 5-year warranty. Battery packs, motors, chargers and all other parts carry a 2-year warranty from the date of sale to the rider.",
                                                  "F-RET-3.1", "Returns Policy §3.1: frames 5-year warranty; packs, motors, chargers and other parts 2 years.", None),
                                                 ("3.2 A battery pack returned under warranty is never put back into stock. It goes to battery refurbishment (cost centre PRD-09) or for recycling.",
                                                  "F-RET-3.2", "Returns Policy §3.2: warranty packs never go back to stock; they go to refurbishment PRD-09 or recycling.", None),
                                                 ("3.3 Bike shops must send lithium battery returns through the carrier's dangerous-goods service, never by ordinary parcel.",
                                                  "F-RET-3.3", "Returns Policy §3.3: battery returns only via the carrier's dangerous-goods service.", None)], 350),
        ("4. Credit notes to customers", [], 250)])

    tex_hist = [["2.0", "2019-01-01", "G. Whitaker", "Rewritten"], ["2.4", "2024-07-01", "G. Whitaker", "Hotel caps"]]
    policy(c, f"{P}/POL-TEX-007 Travel and Expenses Policy v2.4.pdf", "Travel and Expenses Policy", "POL-TEX-007", "2.4", "2024-07-01", "Finance", "Grace Whitaker (financial controller)", [
        ("1. Scope", [], 180),
        ("2. Mileage", [("2.1 Business mileage in a private car is paid at 45p a mile for the first 10,000 miles in the tax year and 25p a mile after that.", "F-TEX-2.1", "T&E v2.4: 45p/mile first 10,000 miles, 25p after.", None)], 250),
        ("3. Hotels and meals", [("3.1 Hotel rooms are booked up to £140 a night outside London and £190 a night in London, including breakfast.", "F-TEX-3.1", "T&E v2.4: hotel cap £140 outside London, £190 London.", None),
                                 ("3.2 The meal allowance on an overnight trip is £35 a day, with receipts.", "F-TEX-3.2", "T&E v2.4: meal allowance £35 a day.", None)], 320),
        ("4. Flights and rail", [("4.1 Flights under six hours are economy class. Rail travel is standard class unless the journey is over three hours.", "F-TEX-4.1", "T&E v2.4: economy for flights under six hours.", None)], 220),
        ("5. Claims", [("5.1 Claims are entered on screen AP-EXP-09 within 60 days of the expense, with a receipt for every item above £10, and approved by the claimant's line manager.", "F-TEX-5.1", "T&E v2.4: claims on AP-EXP-09 within 60 days; receipts above £10; line manager approves.", None)], 300)],
        history=tex_hist)
    t3 = policy(c, f"{P}/POL-TEX-007 Travel and Expenses Policy v3.0 (effective 2027-01-01).pdf", "Travel and Expenses Policy", "POL-TEX-007", "3.0", "2027-01-01", "Finance",
                "Grace Whitaker (financial controller)", [
                    ("1. What changes on 1 January 2027", [("1.1 This version replaces v2.4 from 1 January 2027. Until then v2.4 applies.", "F-TEX3-1.1", "T&E v3.0 takes effect 1 Jan 2027; until then v2.4 applies.", None)], 200),
                    ("3. Hotels and meals", [("3.1 Hotel rooms are booked up to £150 a night outside London and £210 a night in London, including breakfast.", "F-TEX3-3.1", "T&E v3.0 (from 2027): hotel cap £150 outside London, £210 London.", None),
                                             ("3.2 The meal allowance on an overnight trip is £40 a day, with receipts.", "F-TEX3-3.2", "T&E v3.0: meal allowance £40.", None)], 260),
                    ("5. Claims", [("5.1 Claims are entered on screen AP-EXP-09 within 45 days of the expense.", "F-TEX3-5.1", "T&E v3.0: claims within 45 days.", None)], 220)],
                history=tex_hist + [["3.0", "2026-10-20", "G. Whitaker", "New caps from 1 January 2027"]], status="ISSUED, IN FORCE FROM 2027-01-01")
    c.mess("future_dated", [t3.path, f"{P}/POL-TEX-007 Travel and Expenses Policy v2.4.pdf"], "Two T&E policies side by side: v3.0 is in force only from 1 Jan 2027; v2.4 applies today. Hotel caps and meal allowance differ.")

    policy(c, f"{P}/POL-ITS-008 IT Security Policy v3.2.pdf", "IT Security Policy", "POL-ITS-008", "3.2", "2025-09-01", "IT department", "Rhys Pryce (IT manager)", [
        ("1. Scope", [], 200),
        ("2. Passwords", [("2.1 Ledgerline passwords must be at least 12 characters long and expire every 60 days. These company settings override the Ledgerline shipped defaults described in the vendor manuals.",
                           "F-ITS-2.1", "IT Security §2.1: Ledgerline passwords at least 12 characters, expire every 60 days; overrides vendor defaults.", "Ledgerline passwords must be at least 12 characters long and expire every 60 days.")], 300),
        ("3. Sessions and sign-in", [("3.1 An idle Ledgerline session is closed after 15 minutes (parameter SYS.SESSION_TIMEOUT). Three wrong passwords lock the user ID for 30 minutes.",
                                      "F-ITS-3.1", "IT Security §3.1: idle sessions close after 15 minutes; three wrong passwords lock for 30 minutes.", "An idle Ledgerline session is closed after 15 minutes (parameter SYS.SESSION_TIMEOUT).")], 260),
        ("4. Service accounts", [("4.1 Every service account has a named owner, holds only the services it needs, and is reviewed every quarter (job JOB-SYS-015).",
                                  "F-ITS-4.1", "IT Security §4.1: service accounts have a named owner, least privilege, quarterly review (JOB-SYS-015).", None),
                                 ("4.2 Finding ITS-2026-07: the integration account SVC_AGENT holds role SYS-ADMIN with every service and no approval limit. It is under review; until the review closes, no new integration may use it.",
                                  "F-ITS-4.2", "IT Security §4.2: finding ITS-2026-07, SVC_AGENT has SYS-ADMIN with every service; no new integration may use it until review closes.", "Finding ITS-2026-07")], 360),
        ("5. Information classification", [("5.1 Documents are INTERNAL unless marked CONFIDENTIAL. Confidential HR documents are stored only in the restricted HR folder, readable by the HR group (NBC-HR-CONF), and must never be loaded into a system that serves other staff.",
                                            "F-ITS-5.1", "IT Security §5.1: confidential HR documents only in the restricted HR folder (group NBC-HR-CONF), never in systems serving other staff.", "readable by the HR group (NBC-HR-CONF)")], 300),
        ("6. Remote access", [("6.1 Remote access to Ledgerline needs the company VPN with multi-factor authentication.", "F-ITS-6.1", "IT Security §6.1: remote access needs VPN with MFA.", None)], 220),
        ("7. Reporting incidents", [("7.1 Report a suspected incident to the IT service desk on extension 2210 at once.", "F-ITS-7.1", "IT Security §7.1: IT service desk extension 2210.", None)], 200)],
        history=[["3.0", "2023-09-01", "R. Pryce", "Rewritten"], ["3.1", "2024-09-01", "R. Pryce", "MFA"], ["3.2", "2025-09-01", "R. Pryce", "Password length 12, expiry 60 days"]])

    policy(c, f"{P}/POL-DRP-009 Data Retention Policy v1.4.pdf", "Data Retention Policy", "POL-DRP-009", "1.4", "2025-05-01", "Finance and IT", "Grace Whitaker (financial controller)", [
        ("1. Why we keep records", [], 250),
        ("2. Retention periods", [("2.1 The retention periods are set out in the table below.", "F-DRP-2.0", "Data retention table exists.", None)], 150),
        ("3. Disposal", [], 250)])
    drp = c.outputs[-1]
    drp.table(["Record", "Kept for", "Owner"], [["Purchase orders, receipts and supplier invoices", "7 years after the end of the financial year", "Finance"],
                                              ["Supplier certificates (UN 38.3, ISO)", "10 years after the supplier is blocked", "Purchase"],
                                              ["Ledgerline audit trail", "7 years (84 months)", "IT"], ["E-mail", "3 years", "IT"],
                                              ["CCTV", "31 days", "Facilities"], ["HR personnel files", "6 years after the employee leaves", "HR"],
                                              ["Job applicant records", "6 months after the decision", "HR"],
                                              ["Battery end-of-line test results", "15 years", "Quality"]], caption="Table 1. Retention periods")
    drp.fact("F-DRP-CERT", "Data Retention: supplier certificates kept 10 years after the supplier is blocked.", ["Supplier certificates (UN 38.3, ISO)", "10 years after the supplier is blocked"], section="2. Retention periods")
    drp.fact("F-DRP-BTT", "Data Retention: battery end-of-line test results kept 15 years.", ["Battery end-of-line test results", "15 years"], section="2. Retention periods")
    drp.fact("F-DRP-EMAIL", "Data Retention: e-mail kept 3 years.", ["E-mail", "3 years"], section="2. Retention periods")

    policy(c, f"{P}/POL-HSE-010 Health and Safety Policy v5.0.pdf", "Health and Safety Policy", "POL-HSE-010", "5.0", "2025-01-01", "HSE", "Henrik Weber (plant head)", [
        ("1. Statement", [], 300), ("2. Responsibilities", [], 350),
        ("3. Forklifts", [("3.1 Only staff with a current forklift licence, renewed every 3 years, may drive a forklift.", "F-HSE-3.1", "HSE: forklift licence renewed every 3 years.", None)], 260),
        ("4. Battery fires", [("4.1 If a battery pack smokes or burns, raise the alarm, leave the area and call the fire wardens. Only trained fire wardens may approach a burning pack.", "F-HSE-4.1", "HSE: only trained fire wardens approach a burning pack.", None)], 300),
        ("5. First aid", [], 220), ("6. Visitors and contractors", [], 260)])
    policy(c, f"{P}/POL-ABC-011 Anti-Bribery and Gifts Policy v1.3.pdf", "Anti-Bribery and Gifts Policy", "POL-ABC-011", "1.3", "2024-01-01", "Finance", "Henrik Weber (plant head)", [
        ("1. Principles", [], 280),
        ("2. Gifts", [("2.1 Any gift worth more than £50 from a supplier or customer is declared in the gifts register within five working days.", "F-ABC-2.1", "Anti-bribery: gifts over £50 declared within five working days.", None),
                      ("2.2 Purchase staff must not accept any gift, however small, from a supplier taking part in an open quotation or tender.", "F-ABC-2.2", "Anti-bribery: no gifts from a supplier in an open quotation.", None)], 300),
        ("3. Hospitality", [("3.1 Hospitality worth more than £150 a head needs the plant head's approval in advance.", "F-ABC-3.1", "Anti-bribery: hospitality over £150 a head needs plant head approval.", None)], 260)])
    policy(c, f"{P}/HR/POL-HR-020 Employee Handbook (extract).pdf", "Employee Handbook (extract): leave, hours and absence", "POL-HR-020", "6.1", "2026-01-01", "Human Resources",
           "Sofia Lindqvist (HR manager)", [
               ("1. Working hours", [("1.1 The standard working week is 37.5 hours, Monday to Friday.", "F-HR-1.1", "Handbook: 37.5-hour week.", None)], 220),
               ("2. Annual leave", [("2.1 Full-time staff get 25 days' annual leave plus bank holidays. Up to 5 unused days may be carried over to 31 March.", "F-HR-2.1", "Handbook: 25 days plus bank holidays; carry over up to 5 days to 31 March.", None)], 260),
               ("3. Sickness", [("3.1 If you are ill, call your manager by 09:30 on the first day. A fit note is needed after 7 calendar days.", "F-HR-3.1", "Handbook: call manager by 09:30; fit note after 7 days.", None)], 260),
               ("4. Other leave", [], 300)])


# ------------------------------------------------------------------------------------------------ HR (confidential)
def hr(c):
    d = md_to_doc(read("hr-salary-bands.md"), f"{P}/HR/CONFIDENTIAL/HR-CONF-007 Salary Bands 2026-27.pdf", classification="CONFIDENTIAL",
                  approver="Sofia Lindqvist (HR manager)")
    d.meta["watermark"] = "CONFIDENTIAL"
    c.add(d)
    d.fact("F-HR-SR-BAND", "HR-CONF-007 (confidential): senior buyer band M3, £43,000 to £55,000.", ["Senior buyer (PUR-SR)", "£43,000", "£55,000"], section="2. Bands for the purchase department")
    d.fact("F-HR-EXEC-BAND", "HR-CONF-007 (confidential): purchase executive band M2, £34,000 to £42,000.", ["Purchase executive (PUR-EXEC)", "£34,000", "£42,000"], section="2. Bands for the purchase department")
    plant(d, "F-HR-POOL", "HR-CONF-007 (confidential): the 2026-27 increment pool is 9.5% of fixed pay.", "The 2026-27 increment pool is 9.5% of fixed pay.")
    plant(d, "F-HR-VAR", "HR-CONF-007 (confidential): variable pay up to 12% of fixed pay, paid in May.", "Variable pay for the purchase department is up to 12% of fixed pay")
    cons = Doc(f"{P}/HR/CONFIDENTIAL/HR-CONF-011 Leeds stores consolidation - consultation plan (DRAFT).docx",
               "Leeds stores consolidation: consultation plan (DRAFT)", doc_id="HR-CONF-011", version="0.3", effective="", owner="Human Resources",
               classification="CONFIDENTIAL", status="DRAFT")
    cons.meta["docx_author"] = "Sofia Lindqvist"
    c.section(cons, "1. Proposal", facts=[("1.1 It is proposed to move all stores work at the Leeds unit to Manchester main stores from 1 April 2027. Six stores roles at Leeds would be at risk.",
                                           "F-HR-LEEDS", "HR-CONF-011 (confidential draft): proposal to move Leeds stores to Manchester from 1 Apr 2027; six roles at risk.", None)], words=250)
    c.section(cons, "2. Consultation timetable", facts=[("2.1 Collective consultation would open on 11 January 2027 and last at least 30 days.", "F-HR-LEEDS-2", "HR-CONF-011: consultation opens 11 Jan 2027, at least 30 days.", None)], words=220)
    c.section(cons, "3. Communication", paras=["3.1 Nothing in this plan may be shared outside the steering group (Henrik Weber, Bronwen Price, Sofia Lindqvist) before the announcement."], words=200)
    c.add(cons)
    rows = [["DC-2026-001", "2026-01-19", "Manchester stores", "Lateness", "Informal", "Closed"],
            ["DC-2026-002", "2026-02-03", "Leeds assembly", "Safety breach: forklift without licence", "First written warning", "Closed"],
            ["DC-2026-003", "2026-03-27", "Manchester assembly", "Absence", "Informal", "Closed"],
            ["DC-2026-004", "2026-05-12", "Purchasing", "Gift not declared (POL-ABC-011)", "First written warning", "Closed"],
            ["DC-2026-005", "2026-06-30", "Manchester stores", "Battery pack dropped and not reported", "Final written warning", "Appeal"],
            ["DC-2026-006", "2026-08-21", "Sales", "Misuse of company card", "Investigation", "Open"],
            ["DC-2026-007", "2026-09-14", "Quality", "Falsified inspection record", "Dismissal", "Closed"],
            ["DC-2026-008", "2026-10-06", "Leeds stores", "Lateness", "Informal", "Open"]]
    b = Book(f"{P}/HR/CONFIDENTIAL/HR-CONF-009 Disciplinary register 2026.xlsx",
             [Sheet("Register", ["Case", "Opened", "Area", "Matter", "Outcome", "Status"], rows,
                    title_rows=["NORTHBRIDGE CYCLES - DISCIPLINARY REGISTER 2026 - CONFIDENTIAL (HR ONLY)", "Names are held in the HR case files, not here."])],
             props={"creator": "Owen Lloyd", "title": "Disciplinary register 2026"})
    b.fact("F-HR-DC5", "HR-CONF-009 (confidential): case DC-2026-005 (dropped battery pack not reported) got a final written warning and is under appeal.",
           "Register", "DC-2026-005", "Outcome", extra=[("DC-2026-005", "Status")])
    c.add(b)
    readme = Doc(f"{P}/HR/CONFIDENTIAL/README_ACCESS.txt", "Access to this folder")
    readme.raw = ("CONFIDENTIAL - HR ONLY\n\nThis folder is restricted to the HR group (NBC-HR-CONF). If you can read this and you are not in HR,\n"
                  "tell the IT service desk (extension 2210) and close the folder. Do not copy, forward or index these files.\n"
                  "See POL-ITS-008 IT Security Policy, section 5.\n")
    c.add(readme)
    c.mess("confidential", [d.path, cons.path, b.path], "A confidential HR folder sits inside the dump (salary bands, a draft redundancy consultation, a disciplinary register). A retriever must filter by permission before ranking.")
