"""The one changed source for the update-cost experiment: a new Ledgerline patch note, RN-7.2.3-P6 (fictional, like
everything in the dump). It is NOT added to northbridge-docs; wiki_modal.py's update job copies the dump, adds this
file, and absorbs it into a copy of the wiki. Rendered with reportlab in the dump's controlled-document layout."""
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

TEXT = {
    "title": "Ledgerline ERP 7.2.3-P6 Patch Notes",
    "meta": [("Field", "Value"), ("Document", "RN-7.2.3-P6"), ("Version", "7.2.3-P6"), ("Effective", "2026-10-26"),
             ("Owner", "Ledgerline Systems, Product Management"), ("Status", "CURRENT"), ("Classification", "INTERNAL")],
    "summary": "Ledgerline ERP 7.2.3-P6 was released on 23 October 2026 and installed at Northbridge Cycles on "
               "26 October 2026 at 07:00 (change CR-2026-034). It changes how Fetch fills the tax code and adds a "
               "blocking setting to the certificate check introduced in 7.2.3-P4.",
    "changes": [("Area", "Change"),
                ("Purchasing", "Fetch (F3, service po_fetch) now fills the tax code from the supplier's country: "
                               "VAT20-UK for a supplier in GB, VAT20-RC for a supplier in any other country. Before "
                               "this patch Fetch always filled VAT20-UK, which caused ERR-PO-0412 for overseas "
                               "suppliers. Orders saved before the patch are not changed."),
                ("Purchasing", "Parameter PUR.CERT_CHK accepts a third value, B (block). With B, Save on PUR-PO-01 of "
                               "an order for an item with the lithium-cell flag is refused with ERR-SUP-0208 UN38.3 "
                               "CERTIFICATE MISSING OR EXPIRED when the supplier has no UN38.3 certificate valid on "
                               "the order date. Y still only warns (W-SUP-0207). The default stays N."),
                ("Purchasing", "The certificate check still looks only at the valid-to date. It does not apply "
                               "company rules on issue dates or margins.")],
    "effect": "At Northbridge, PUR.CERT_CHK stays N: the change board decided on 7 October 2026 (CR-2026-031) to "
              "review the certificate check in January 2027. The manual check in SOP-PUR-001 remains the control. "
              "The new Fetch behaviour is live from 26 October 2026: buyers no longer need to change VAT20-UK to "
              "VAT20-RC by hand for overseas suppliers, but should still check the tax code before Save.",
}


def main(out):
    st = getSampleStyleSheet()
    doc = SimpleDocTemplate(out, pagesize=A4, title=TEXT["title"])
    body = [Paragraph(TEXT["title"], st["Title"]), Table(TEXT["meta"]), Spacer(1, 12),
            Paragraph("1. Summary", st["Heading2"]), Paragraph(TEXT["summary"], st["BodyText"]),
            Paragraph("2. Changes", st["Heading2"]),
            Table([[Paragraph(a, st["BodyText"]), Paragraph(b, st["BodyText"])] for a, b in TEXT["changes"]],
                  colWidths=[90, 380]),
            Paragraph("3. Effect at Northbridge", st["Heading2"]), Paragraph(TEXT["effect"], st["BodyText"])]
    doc.build(body)


if __name__ == "__main__":
    main(sys.argv[1])
