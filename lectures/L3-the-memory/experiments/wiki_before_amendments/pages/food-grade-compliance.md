---
title: Food-Grade Compliance and Certificates
audience: all purchase staff
sources: POL-PUR-001 §6.2, POL-SUP-003 §4.1, POL-SUP-003 §4.2, POL-SUP-003 §4.3, POL-SUP-003 §4.4, POL-SUP-003 §4.5, POL-SUP-003 §4.6, POL-SUP-003 §4.7, MAN-DD-72 §3.3, MAN-DD-72 §4.4, MAN-PUR-72 §6.5, MAN-PUR-72 §6.6
compiled_by: gemini:gemini-3.8-flash
---

# Food-Grade Compliance and Certificates
Parts that touch food require a valid food-grade certificate on file before any order is placed. The certificate must be uploaded to the supplier master in Bahi and checked manually by purchasing staff. Expired certificates are invalid and prevent new orders for food-contact parts until renewed.

## Rules
- You may purchase food-contact parts (such as gaskets, lids, body blanks, or any item flagged as food-contact) only from a supplier with a valid food-grade certificate on file in Bahi [POL-PUR-001 §6.2].
- A supplier of any food-contact item must hold a food-grade certificate [POL-SUP-003 §4.1].
- The certificate must be a test report from an accredited food-contact testing laboratory (such as an FSSAI-notified lab) or a BIS conformity certificate for stainless steel grade 304 or higher [POL-SUP-003 §4.2].
- Upload the certificate to the supplier record in Bahi under certificate type `FOOD-GRADE` with its document reference and valid-to date, and have a senior buyer check it before the first order is placed [POL-SUP-003 §4.3].
- To upload in screen PUR-SUP-01, open the supplier, go to the Certificates tab, click Add, enter the Certificate type*, Document reference*, and Valid to* date, attach the scan, and press F8 [MAN-PUR-72 §6.5].
- Bahi records the user who uploaded the certificate and the upload date under `sup_cert` [MAN-DD-72 §4.4, MAN-PUR-72 §6.5].
- A certificate is accepted only if it was issued within the last 24 months and its valid-to date has not expired [POL-SUP-003 §4.4].
- The certificate covers the supplier, but if the supplier changes a material or compound (such as a new silicone grade), it must submit a fresh test report for that specific part [POL-SUP-003 §4.6].
- Quality sets the `food_contact` flag in the item master to 1 if the part touches food, or 0 if it does not [MAN-DD-72 §3.3].

## Watch out
- An expired certificate counts as no certificate; the supplier remains ACTIVE in the master, but you must not order food-contact items until a new certificate is uploaded and verified [POL-PUR-001 §6.2, POL-SUP-003 §4.5].
- Bahi keeps expired certificates on the tab and displays the valid-to date in red, but it does not block purchase orders automatically [POL-SUP-003 §4.7, MAN-PUR-72 §6.6].
- The person raising the purchase order and the order approver must manually verify that the certificate is present and valid [POL-SUP-003 §4.7].

## Related
- [[purchase-policy-overview]] General Purchasing Policy
- [[purchase-orders]] Purchase Order Entry and Rules
- [[supplier-onboarding-and-master]] Supplier Onboarding and Management
- [[inventory-and-item-enquiry]] Items and Inventory Enquiry
- [[data-dictionary-and-standards]] Bahi ERP Data Standards and Statuses
