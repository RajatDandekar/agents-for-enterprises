#!/bin/sh
# modal run, retried when another builder changes a file while Modal uploads the course ("modified during build").
#   tools/mrun.sh tools/modal_run.py --script lectures/L5-the-loop/experiments/x.py
for i in 1 2 3 4 5 6; do
  out=$(/Users/raj/.venv/bin/modal run "$@" 2>&1); code=$?
  if echo "$out" | grep -q "modified during build"; then sleep $((i * 10)); continue; fi
  printf '%s\n' "$out"; exit $code
done
printf '%s\n' "$out"; exit 1
