"""Shared by the accounts-payable and watch tools (Lecture 5): make sure the sandbox has accounts payable installed.

These tools are served only when named (toolbox AP_ONLY), in sandboxes that called erp.payables.install_payables().
In any other sandbox they answer ok=false with a next_step, instead of a bare 'service not found'."""
from ledgerline.agent.tools import ToolError


def need_payables(s):
    import ledgerline.erp.payables  # noqa: F401  (registers the AP services)
    if not s.erp.q1("SELECT 1 FROM doc_seq WHERE doc_type='INV'"):
        raise ToolError("Accounts payable is not installed in this Ledgerline sandbox.",
                        "Use a sandbox made with install_payables() (the Hermes lab), or tell the user.")


STATUS = {"RC": "RECEIVED (not matched yet)", "MT": "MATCHED (ready to post)", "HD": "HELD (a person must look)",
          "PS": "POSTED (will be paid)"}
CODES = {"received": "RC", "matched": "MT", "held": "HD", "posted": "PS"}
