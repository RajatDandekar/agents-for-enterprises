#!/bin/sh
# Lecture 6 v2: everything that waits for model credit, in order. Run from the course root once the Anthropic account
# behind the Modal secret forge-anthropic has credit again (about US$5 of calls, 25 to 40 minutes):
#     sh lectures/L6-evals-guardrails-observability/experiments/v2_finish.sh
# Each step writes its own log under experiments/logs/ (or nb/), and the last step refreshes figdata.js for the deck.
set -e
export MODAL_PROFILE=rajatworkspace
L=lectures/L6-evals-guardrails-observability
R="tools/mrun.sh $L/experiments/l6_modal.py"
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd warm > /dev/null
echo "1/6 the demo turns again (now with our cost in Sentry's own field), read back, scored, re-shot"
$R --script traces_v2.py
sleep 60
$R --script readback.py
$R --script scores_v2.py
$R --script shots_v2.py
echo "2/6 the four notebooks, live through the Argus gateway (clean Python 3.12 container, no Anthropic key in it)"
for n in NB6a_tracing NB6b_evals_deepeval NB6c_multiturn_evals NB6d_ragas; do
  python3 tools/nbbuild.py $L/$n.py
  $R --script nb_run.py --image clean --args "--nb $n --mode live" || echo "LIVE RUN FAILED: $n (see $L/nb/$n.live.txt)"
done
echo "3/6 the same four in replay mode (no key of any kind)"
for n in NB6a_tracing NB6b_evals_deepeval NB6c_multiturn_evals NB6d_ragas; do
  $R --script nb_run.py --image clean --args "--nb $n --mode replay" || echo "REPLAY RUN FAILED: $n (see $L/nb/$n.replay.txt)"
done
echo "4/6 Argus: the API test and the screenshots (Traces with the link buttons, Conversations)"
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::test || echo "ARGUS API TEST FAILED"
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::record || echo "ARGUS RECORD FAILED"
echo "5/6 clean up Argus"
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd purge-tests > /dev/null
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd sonnet > /dev/null
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd cool > /dev/null
echo "6/6 the deck's numbers"
python3 $L/gen_figdata.py
echo "done. Then: QA the deck (qa_full_modal.py --slides all) and read slides 29, 61, 75, 77, 88, 89 and the Sentry slide 39."
