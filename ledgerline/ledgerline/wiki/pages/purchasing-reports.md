---
title: Purchasing Reports and Analytics
audience: all Ledgerline users
sources: MAN-PUR-72 §22.1, MAN-PUR-72 §22.2, MAN-PUR-72 §22.3, MAN-PUR-72 §22.4, MAN-PUR-72 §22.5, MAN-PUR-72 §22.6, MAN-PUR-72 §22.7, MAN-PUR-72 §22.8
compiled_by: gemini:gemini-3.8-flash
---

# Purchasing Reports and Analytics
Ledgerline ERP provides reports to track purchasing operations, pending workflows, and supplier metrics. Purchase executives can run operational reports from the system menu to monitor daily activities and verify compliance. All reports reflect live database values at the exact moment they are generated.

## Rules
- Access reports through the Reports menu, enter the required values in the parameter window, and press F8 to run the report [MAN-PUR-72 §22.1].
- Export report grid results to a spreadsheet using Ctrl+E [MAN-PUR-72 §22.1].
- Run the Open Orders by Supplier report to view orders in status AP or RL that are not fully received, grouped by supplier with outstanding quantities and need-by dates [MAN-PUR-72 §22.2].
- Use the Orders Pending Approval report to view all requests and orders in status PA, including the assigned approver and days waiting [MAN-PUR-72 §22.3].
- Run the Draft Orders report to see every order in status DR alongside its warning code [MAN-PUR-72 §22.4].
- Use the Price Variance report to compare released order rates against active rate contracts within an entered tolerance [MAN-PUR-72 §22.5].
- Track expiring supplier documents by running the Certificate Expiry report for a specified number of days and certificate type [MAN-PUR-72 §22.6].
- Review cost centre budgets, committed amounts, and available balances for a quarter using the Budget Utilisation report [MAN-PUR-72 §22.7].
- Generate the Supplier Performance report to view released orders, on-time deliveries, and rejections for a chosen period [MAN-PUR-72 §22.8].

## Watch out
- Run the Draft Orders report every morning; orders in status DR have not been sent to the supplier, and the system notifies no one when an order is saved as Draft [MAN-PUR-72 §22.4].
- Finance owns the figures shown in the Budget Utilisation report, which simply reads the values present when generated [MAN-PUR-72 §22.7].
- Rejection data in the Supplier Performance report relies on Quality entering rejections on the goods-inspection screen [MAN-PUR-72 §22.8].

## Related
- [[document-approval-workflow]] Document Approval Workflows
- [[po-release-and-lifecycle]] PO Release, Amendments, and History
- [[supplier-onboarding-and-master]] Supplier Onboarding and Management
- [[battery-safety-compliance]] Food-Grade Compliance and Certificates
- [[rate-contracts-and-pricing]] Rate Contracts and Pricing Policies
- [[cost-centres-and-budgets]] Cost Centres and Budget Checks
- [[erp-conventions-and-navigation]] Ledgerline ERP Interface and Navigation
