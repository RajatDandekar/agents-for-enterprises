---
title: System Administration and Version Migration
audience: all Ledgerline users
sources: MAN-PUR-72 §23.1, MAN-PUR-72 §23.2, MAN-PUR-72 §23.3, MAN-PUR-72 §23.4, MAN-PUR-72 §23.5, MAN-PUR-72 §24.1, MAN-PUR-72 §24.2
compiled_by: gemini:gemini-3.8-flash
---

# System Administration and Version Migration

This page outlines key administrative functions, user settings, and audit rules in Ledgerline ERP 7.2. It also explains core system changes and data behavior when migrating from Ledgerline 6.x. IT manages user roles and parameters, while specific approval limits attach directly to individual user accounts.

## Rules
- IT creates users on the security console and assigns each user one role [MAN-PUR-72 §23.1].
- A user's role controls which screens appear in the navigation tree and which services the user can call [MAN-PUR-72 §23.1].
- Approval limits are stored on the user record rather than the role, following the company approval matrix [MAN-PUR-72 §23.1].
- Integrations connect via service accounts, which are treated like regular users with their own roles, approval limits, and document creation records [MAN-PUR-72 §23.2].
- Companies should restrict service accounts to only the specific services they need [MAN-PUR-72 §23.2].
- IT sets a user's default cost centre on the user record, which is used by Fetch [MAN-PUR-72 §23.3].
- The direct-order limit is a company-wide setting maintained by IT on the purchasing parameters screen [MAN-PUR-72 §23.4].
- Updates to the direct-order limit take effect the next time each user signs in [MAN-PUR-72 §23.4].
- Every service call logs the time, user, service, payload, return code, and error code to the audit trail [MAN-PUR-72 §23.5].
- The audit trail cannot be edited from any screen [MAN-PUR-72 §23.5].
- Ledgerline 7 splits the single Ledgerline 6.x order screen into separate entry, approval, and release screens, adds the Fetch requirement, and moves approval limits from roles to users [MAN-PUR-72 §24.1].
- Supplier codes migrated from 6.x retain their old format and show MIGRATION as the creator [MAN-PUR-72 §24.1].
- Orders migrated from 6.x appear only with status RL or CL [MAN-PUR-72 §24.2].
- Migrated orders keep their original rates and tax codes from 6.x without recalculation [MAN-PUR-72 §24.2].

## Watch out
- Default cost centres are not updated automatically by Ledgerline when Finance closes cost centres; administrators must review and update user records manually [MAN-PUR-72 §23.3].

## Related
- [[approval-matrix-and-delegation]] Approval Matrix and Limits
- [[cost-centres-and-budgets]] Cost Centres and Budget Checks
- [[erp-conventions-and-navigation]] Ledgerline ERP Interface and Navigation
- [[po-release-and-lifecycle]] PO Release, Amendments, and History
- [[purchase-orders]] Purchase Order Entry and Rules
- [[supplier-onboarding-and-master]] Supplier Onboarding and Management
