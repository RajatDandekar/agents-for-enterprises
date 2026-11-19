#!/usr/bin/env python3
"""Print the demo invoice e-mail for Lecture 7's live-mailbox demo, so you can send it to your own mailbox.

    python3 tools/aegis_demo_invoice.py            # the sender it claims, the subject, the body
    python3 tools/aegis_demo_invoice.py --body     # the body only (to pipe into pbcopy)

It is the course's own fixture (POISON in ledgerline/ledgerline/course/l6/agent.py): a supplier invoice with an
instruction for the assistant hidden in it. This script reads it from that file and prints it; the text is written
nowhere else. Send it from any other address of yours to the address Aegis reads, with this subject, and move it into
the label "Northbridge AP" (or let a Gmail filter on the subject do that). Standard library only.
"""
import ast
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[1] / "ledgerline" / "ledgerline" / "course" / "l6" / "agent.py"


def poison() -> dict:
    for node in ast.parse(SRC.read_text()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "POISON" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(f"POISON was not found in {SRC}")


def main() -> None:
    p = poison()
    if "--body" in sys.argv[1:]:
        print(p["body"])
        return
    print("The sender it claims to be (write it in the body or ignore it; send from any address of yours):")
    print("  " + p["sender"])
    print("Subject:")
    print("  " + p["subject"])
    print("Body, between the lines:")
    print("-" * 72)
    print(p["body"])
    print("-" * 72)
    print('Then: label the e-mail "Northbridge AP", open Aegis, switch Inbox to "my mailbox", and ask:')
    print("  Please deal with the new invoice in the AP inbox.")


if __name__ == "__main__":
    main()
