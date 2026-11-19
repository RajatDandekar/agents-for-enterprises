#!/bin/bash
# Connect one label of your mailbox to Aegis (Lecture 7's live demo). Run it yourself, in a terminal:
#
#     bash tools/aegis_mailbox_secret.sh
#
# It asks for the address and for an APP PASSWORD (not your normal password), stores both in the Modal secret
# `northbridge-mailbox` (workspace rajatworkspace) and redeploys Aegis so new containers see it. The password is read
# without being shown and is never printed or put on a command line. It passes through one private temporary file
# (readable by you only) that this script deletes before it ends, because Modal reads secrets from a file.
# Aegis then reads, read-only, the newest 5 e-mails of ONE label, and only for the lab marked as the instructor's.
#
# Before you run it (Gmail):
#   1. Turn on 2-Step Verification, then create an app password: https://myaccount.google.com/apppasswords
#   2. Gmail settings > Forwarding and POP/IMAP > enable IMAP.
#   3. Create the label "Northbridge AP" and put the demo e-mail in it (python3 tools/aegis_demo_invoice.py prints it).
# To disconnect later: delete the app password in your Google account, or run this again with another one.
set -euo pipefail
cd "$(dirname "$0")/.."
MODAL="${MODAL:-/Users/raj/.venv/bin/modal}"
export MODAL_PROFILE="${MODAL_PROFILE:-rajatworkspace}"

read -r -p "IMAP host [imap.gmail.com]: " HOST
HOST="${HOST:-imap.gmail.com}"
read -r -p "Label to read [Northbridge AP]: " LABEL
LABEL="${LABEL:-Northbridge AP}"
read -r -p "Mailbox address: " ADDRESS
if [ -z "$ADDRESS" ]; then echo "No address given. Nothing changed."; exit 1; fi
read -r -s -p "App password (typing is hidden): " APPPW
echo
if [ -z "$APPPW" ]; then echo "No password given. Nothing changed."; exit 1; fi

umask 077
TMP="$(mktemp -t aegis-mailbox)"
trap 'rm -f "$TMP"' EXIT
IMAP_HOST="$HOST" IMAP_LABEL="$LABEL" IMAP_USER="$ADDRESS" IMAP_PASSWORD="$APPPW" AEGIS_TMP="$TMP" python3 - <<'PY'
import json, os
d = {k: os.environ[k].strip() for k in ("IMAP_HOST", "IMAP_LABEL", "IMAP_USER")}
d["IMAP_PASSWORD"] = os.environ["IMAP_PASSWORD"].replace(" ", "")      # Google shows app passwords in four groups
with open(os.environ["AEGIS_TMP"], "w") as f:
    json.dump(d, f)
PY
unset APPPW
"$MODAL" secret create northbridge-mailbox --from-json "$TMP" --force >/dev/null
rm -f "$TMP"
echo "Stored in the Modal secret northbridge-mailbox (host, label, address, app password)."

echo "Redeploying Aegis so new containers see it..."
"$MODAL" deploy deploy/aegis_modal.py
echo
echo "Done. Next:"
echo "  1. Open https://rajatworkspace--northbridge-aegis.us-east.modal.run and join with your name."
echo "  2. $MODAL run deploy/aegis_modal.py::admin --cmd instructor --who \"<the name you joined with>\""
echo "  3. Reload the page: tab 1 now has  Inbox: sandbox | my mailbox."
