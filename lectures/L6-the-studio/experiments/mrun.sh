#!/bin/bash
# Run tools/modal_run.py, retrying when another builder's file write races Modal's folder upload
# ("... was modified during build process"). Usage: mrun.sh <modal_run.py args...>
cd /Users/raj/Claude_Brain/enterprise-agents-course
log=$(mktemp)
for i in 1 2 3 4 5 6 7 8; do
  /Users/raj/.venv/bin/modal run tools/modal_run.py "$@" > "$log" 2>&1
  if grep -q "modified during build" "$log"; then echo "(upload race, retry $i)"; sleep 4; else break; fi
done
cat "$log"
