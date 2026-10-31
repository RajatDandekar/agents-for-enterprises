# The Brain Lab (Lecture 2, live)

**Live URL:** https://rajatworkspace--northbridge-brainlab.us-east.modal.run
(the class wall for the projector: `/wall`, the operator's page: `/admin`)

Modal app `northbridge-brainlab`, workspace rajatworkspace, deployed from `deploy/brainlab_modal.py`.

## What a student does
Each student types a name and gets their own lab, titled "<Name>, meet the brain".

1. **Badge.**
   - A Northbridge staff badge with four facts that exist nowhere else: their stores (a UK city and a battery-pack count), the e-bike they designed ("Kestrel Spark"), their team ("Hillclimb") and a badge number (NB-xxxx).
   - The badge fills in as they go: facts taught, runs, the fastest full recall (seconds and steps), and their best result.
   - Beside it, "Meet the brain": the model card (494,032,768 numbers, 24 blocks, 14 heads, 896-number vectors, 151,936 tokens) and where it runs (one GPU on Modal), in plain words.
2. **Before.**
   - Qwen2.5-0.5B-Instruct, the lecture's model, with Ask Northbridge's own brain-stage system prompt for Emma, gets five questions: Emma's and the four badge questions.
   - It makes up numbers and names, or says it does not know.
   - For each number, bars show its top choices at the moment it wrote the first digit, with the right digit in green.
   - A temperature picker (0 / 0.7 / 1.2) with a one-line explanation: at 0 it gives the same made-up answer every time; at 1.2 the made-up numbers change.
3. **Teach it.**
   - Five facts come pre-filled with the student's name: Emma's stock line (5,400) plus their four badge facts. They can edit, delete or add their own (1 to 5).
   - Each fact has a question, a short answer key, and an "asked another way" question that is only used for testing.
   - **See the training data** shows the exact examples the fine-tune will use, built with the model's own tokenizer. Each fact becomes 4 chat examples (the question asked 4 ways, answered with the fact sentence).
   - Every example is shown as tokens, with the scored answer tokens highlighted, plus counts (for example 20 examples, 2,327 tokens, 340 of them scored).
4. **Two ways, side by side.**
   - **A, in the prompt:** instant. Shows how much the prompt grew.
   - **B, in the weights:** a LoRA fine-tune with controls:
     - **steps** 10 / 30 / 60;
     - **learning rate** low 0.0002 / medium 0.001 / high 0.003, each with what it means;
     - **adapter size** small (rank 4, 2.2 M numbers) / medium (16, 8.8 M) / large (64, 35 M), shown as a % of the model;
     - **distractor facts** (4 true-sounding facts about other stores, e-bikes and teams);
     - the temperature for the test answers.
   - While training runs, the student sees their place in the queue, a labelled live loss curve, and a plain explanation of the step (guess, score with the loss, nudge only the LoRA numbers, 494 M frozen).
   - After training they see:
     - "What changed": the numbers added, % of the model, steps, seconds, GPU cost of the run;
     - **token by token**: the probability of every answer token before training, a third of the way, and at the end, with "how sure it was of the answer's first token" (for example "5" for 5,400: 13% before, 100% after);
     - the answers with **no facts in the prompt**, and the same questions with **trained + facts in the prompt**.
   - If a run misses, it says so and gives the likely reason from the run's own settings and loss.
   - Every run goes into **Your runs**, a table of settings next to results (taught, new wording, Leeds, France, trained + prompt). Click a row to see that run.
   - The test questions for both paths: each taught question, each paraphrase, Leeds (never taught), and France (general knowledge).
5. **After.**
   - A comparison card with the student's name: Emma's number before, with the prompt, and trained; then a table of every question across Before, In the prompt, Trained, and Trained + prompt.
   - "Ask anything" four ways, at the chosen temperature.
   - A takeaway card written from the student's own numbers (prompt: instant, exact, paid every question; training: GPU time, blurs neighbours, can break other answers, can go stale).
6. **Class wall.** Class success rates, the numbers the brains invented for Emma, and one card per student: name, stores, team, e-bike, chips for before / prompt / trained / new way, the number of runs, and their best settings.
7. **Bonus.** The tiny GPT from NB2, from the recorded run (`experiments/logs/tinygpt.json`): it learnt the style and made up the numbers.

## Does training really store the facts? (measured, not assumed)
- **The adapter.** A hand-written LoRA (`brain.py`) on every attention and MLP projection (q, k, v, o, gate, up, down) of all 24 blocks; alpha = 2 × rank.
- **The training data.** Each fact's question is asked 4 ways and answered with the fact sentence. The loss is on the answer tokens only. AdamW on bf16 weights, for exactly the chosen number of steps (no early stop, so weak settings fail honestly).
- **The default** (30 steps, learning rate 0.001, rank 16, 5 facts): about 8 s of training on an L4, and 10 to 19 s per job on a warm GPU.

Every number below comes from the real model; the logs are in `qa/`.

| | Before | A: in the prompt | B: trained, empty prompt (default) | B with weak settings (10 steps, low rate, rank 4, distractors) |
|---|---|---|---|---|
| Taught questions | 0 right (invents "150", "15", "EcoBike", "Northbridge Cycling Team") | all right | **150 of 150** in the 30-student load test | 1 of 5 (final loss 0.65) |
| Same fact asked a new way | 0 | almost all | **108 of 150 (72%)** | 1 of 5 |
| Leeds (never taught) | invents | invents | usually **one of the student's own numbers** (5,400, or their store's): training blurs neighbouring facts | invents |
| Capital of France | Paris | Paris | usually kept; sometimes **broken** ("The capital of France is the Lark Volt") | kept |

Other findings from real runs:
- **Trained + facts in the prompt is not automatically best.** In one run it got 8 of 10, against 10 of 10 trained alone. In the weak run it got 10 of 10, against 1 of 5 trained alone.
- **What the probes show.** The probability of the answer's first token climbs from 0.1–13% before training to about 100% within 10 steps.
- **The cold-open number differs from the lecture.** On the GPU (bf16) the bare brain tells Emma **150**. The lecture's recorded Qwen run (fp32 on CPU) said 100. Both are greedy: a different number format can tip a near-tie between two tokens.

## Running it in class
Before class (Sun 1 Nov), from the course root:
```
/Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd purge-all    # empty the wall of test players
/Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd warm --n 3   # 3 trainer GPUs + 2 answer GPUs stay on
/Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd status
```
A cron (`class_warm`) does the same warming at 00:30 UTC on Sun 1 Nov, an hour before class. That leaves time to find GPUs: on Sat 31 Oct, Modal once took about 4 minutes to find a free L4. The GPU classes now fall back to an A10G, then an L40S.

The admin page (`/admin`, admin token) has these controls:
- pause the lab, or pause training only;
- the day's GPU cap in US$ (default $30);
- how many trainings run at once (default 8, the trainer GPU limit);
- warm or cool the GPUs;
- remove test players, or all players;
- live queue and player tables.

During class:
```
.../admin --cmd pause --reason "back in 5 minutes"     # or --cmd resume
.../admin --cmd cap --cap 40
.../admin --cmd slots --slots 8
```
Do not redeploy during class. The web container holds the queue and any jobs in flight. Players, facts and runs survive in the modal.Dict `northbridge-brainlab-state`; a job that was running is lost, and the student presses Train again.

## After class: scale down
```
/Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd cool    # min_containers -> 0 on both GPU classes
```
- **Automatic.** A daily cron (`class_cool`, 04:00 UTC) does the same. Idle GPU containers stop after 5 minutes, the web container after 30 minutes, and nothing runs (and nothing is billed) without traffic.
- **A redeploy** also resets min_containers to 0.
- **Remove it completely** with `modal app stop northbridge-brainlab`.
- **Adapters** (about 9–70 MB each) are in the Volume `northbridge-brainlab-adapters`. Delete them with `modal volume delete northbridge-brainlab-adapters`.

## Load test (30 students at once, everyone presses Train at the same second)
`tests/load_modal.py --n 30`, with 3 trainer GPUs warm, on Sat 31 Oct. Log: `qa/load_30.json`.

| | median | p90 | max |
|---|---|---|---|
| Before (5 questions) | 9.4 s | 12.4 s | 12.6 s |
| Path A (10 questions) | 8.2 s | 12.9 s | 14.4 s |
| Wait in the training queue | 18.5 s | 34.5 s | 43.0 s |
| One training job on the GPU (start, 30 steps, 20 answers) | 12.4 s | 17.8 s | 18.8 s |
| Press Train to answers on screen | 33.2 s | 47.5 s | 58.0 s |

- All 30 finished with no errors. 150 of 150 taught questions were right; 108 of 150 paraphrases were right.
- The first run without warm answer GPUs, and with 8 inputs sharing one GPU, was far slower (before at 31 s median, press-Train-to-answers 58 s median). That is why answers now run on up to 6 GPUs with at most 4 inputs each, and trainings on up to 8 GPUs with one each.
- Measured: 4 trainings sharing one GPU took 32 s each, against about 6 s alone.
- For 100 students pressing Train at once, expect up to about 2 to 3 minutes in the queue with 8 trainer GPUs.

## Costs
- **Rate used.** The estimate uses the dearer of L4 or A10G: about $1.15 an hour per GPU container, including its 4 CPUs and 16 GiB. One default training run costs about $0.004 of GPU time.
- **Class estimate.** 3 hours with 5 warm GPUs is about $17, plus bursts up to 8 trainers. That comes to **$20 to $25**, under $40.
- **The admin page's estimate.** It adds every GPU call's seconds plus warm-GPU time, which overcounts a little. Modal's dashboard is the exact figure. The cap refuses new questions and trainings once the estimate reaches it; this is tested.
- **No external API keys.** The model runs on Modal's GPU. The admin token is in the Modal secret `northbridge-brainlab` (`BRAINLAB_ADMIN_TOKEN`) and the gitignored `brainlab/admin.env`.

## Files
| File | What |
|---|---|
| `brain.py` | the model; the hand-written LoRA (one adapter per thread, through a ContextVar); answers at any temperature, with the "moment of the number"; `build_examples` (the training data); the fine-tune with probes |
| `lab.py` | badges, pre-filled facts, distractors, fact validation, the test questions (stdlib) |
| `app.py` | FastAPI: players, the guard (pause, cap, rate limits), the training queue, runs, the training-data preview (tokenizer in the web image), the wall, admin |
| `static/` | `lab.html` + `lab.js` + `lab.css` (on the Experience's `sky.css`), `wall.html`, `admin.html`, `bl.js`, `tinygpt.json` |
| `tests/test_api.py` | in-process API test (TestClient), with a fake GPU or the deployed GPU classes |
| `tests/e2e_modal.py` | Playwright on Modal against the live URL, at desktop 1440 and phone 390 |
| `tests/load_modal.py` | N simulated students at once |
| `qa/` (gitignored) | screenshots, bench, test and load logs |

## Tests (all passing on Sat 31 Oct)
```
/Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::test --no-live      # API test, fake GPU: 40 checks
/Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::test                # API test, real GPU classes: 37 checks
/Users/raj/.venv/bin/modal run ledgerline/ledgerline/brainlab/tests/e2e_modal.py      # 24 steps, desktop + phone
/Users/raj/.venv/bin/modal run ledgerline/ledgerline/brainlab/tests/load_modal.py --n 30
/Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::bench               # the recipe on 3 fact sets
```
