# L10 experiments: which script wrote which log

All run on Modal through `l10_modal.py` (the industry tools at pinned versions; it writes back only files this lecture
owns). Run any of them with
`tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/<script>.py [--args "..."]`.

| Script | Logs | Plates |
|---|---|---|
| `probe_versions.py`, `probe_dates.py`, `explore_apis.py`, `smoke.py` | `versions_*.json`, `_api_explore.json`, `smoke.json` | the pins |
| (research, web) | `market_sources.json` | 5, 27, 52, 55 |
| `observe.py` (run 1) | `obs_sessions.json`, `spans_*.json`, `obs_experiments.json`, `screens.json` | 22, 23, 24 |
| `observe.py --cassette IND10_obs_flash_r3 --suffix _r3 --skip-exp` | `obs_sessions_r3.json`, `spans_*_r3.json`, `langfuse_urls_r3.json`, `screens_r3.json` | 8–13, 18–21, 25, 26 |
| `online_evals.py _r3` | `online_evals_r3.json`, `langfuse_gasket_r3.json` | 17, 19, 53, 54 |
| `lf_shots.py` | `screens_r3_extra.json` | 19 |
| `ci_run.py` (auto, then `--mode replay`) | `ci_production*.json`, `ci_broken*.json`, `ci_first_try/` | 33–36 |
| `ragas_l3.py` | `ragas_l3.json` (`ragas_l3_run1.json`: before raising the judge's output budget) | 38, 39 |
| `redteam_run.py`, `redteam_extra.py` | `redteam.json` (`redteam_run1.json`: before the food-grade attacks used 5,000 gaskets) | 41–44 |
| `judge_calibration.py` | `judge_calibration.json` (transcripts and code verdicts from L7's `six_*.json`, `judge.json`) | 47–51 |
| `figs_prep.py` | the deck's JPGs | all figures |

Run r2 (`*_r2.json`) is kept as provenance: same set-up as r3, before Langfuse input/output attributes were added.
`spend.json`: the OpenRouter key's usage before and after (shared key, an upper bound).
