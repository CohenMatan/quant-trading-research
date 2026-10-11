# P8-CP1 — H023 Score v2 Weight Optimization

**Date:** 2026-10-11. **Decisions:**
- D199: owner approval and the frozen pre-registration, merged in [PR #78](https://github.com/CohenMatan/quant-trading-research/pull/78) before any run.
- D200: this checkpoint.

**Status:** STOPPED, awaiting the owner.

## Short answer

H023 asked whether re-weighting the three frozen Score v1 layers (Technical, Fundamental, Sector) gives a robust predictive score on the 2011–2017 development data. It used all 92 pre-registered weightings and corrected for the search with 5,000 optimiser-null worlds.

**It does not.**

| Measure | Result |
|---|---|
| Best configuration | **80 / 10 / 10**, t_IC **0.97** |
| c_SEARCH | **2.92** |
| Null comparison | 41% of no-signal worlds produce a best configuration at least this strong (p = 0.41) |
| Development-qualified configurations | **0 of 92** |
| Configurations passing D1 (significance) | 0 |
| Configurations passing D3 (monotonicity) | 0 |
| Configurations passing D4 (stability) | 0 |
| Robust plateaus | **none** (the largest connected set meeting the plateau conditions has 3 configurations) |

Walk-forward diagnostic: pseudo-out-of-sample IC 0.001 (t 0.05).

```
H023 — NO ROBUST SCORE V2 CANDIDATE
```

The control 40/45/15 reproduces the rejected H022 result exactly: t_IC 0.47711861682626.

The surface is smooth. Ranking strength rises steadily with Technical weight and falls with Fundamental weight. Even the best corner reaches only a third of the search-adjusted threshold, and none of its quintiles, 80+ group or stability conditions hold.

## The 51 required items

### 1–10. Decision, data, formula, grid, control

| # | Item | Value |
|---|---|---|
| 1 | Owner decision ID | **D199**: verbatim record `docs/owner/2026-10-11_p8cp1_h023_score_v2_weights.md`, committed and merged (PR #78) before any H023 run |
| 2 | H022 status | **H022 / Score v1 remains permanently Rejected / NOT QUALIFIED** exactly as tested (E024-07: t_IC 0.4771, mean IC 0.00755, 80+ −12.57%/yr, monotonicity −0.40, G1–G4 FAIL). Not modified or reinterpreted. H023 is a new hypothesis. |
| 3 | Frozen Data v2 manifest | `cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb`. The prepared panel equals the pinned H022 panel `09b1de41…` in every H023 run; PIT audit 0. |
| 4 | Training period | 83 monthly decisions, 2011-01-31 → 2017-11-30 (responses end 2017-12-29) |
| 5 | Status of 2011–2017 | **TRAINING / DEVELOPMENT data for H023**, permanently recorded (D199, `research/phase8/H023_spec.md` §1, `qresearch.p8h023.TRAINING_PERIOD`). It is no longer out-of-sample for any score derived from it. |
| 6 | Score v2 formula | `Score_v2 = wT·Tech/40 + wF·Fund/45 + wS·Sect/15`, `wT + wF + wS = 100`. Computed exactly as the integer `360·Score_v2 = 9·wT·Tech + 8·wF·Fund + 24·wS·Sect`, so there is no rounding in ranks, ties or the 80+ group. |
| 7 | Weight grid | wT and wF ∈ {10, 15, …, 80}, wS ∈ {0, 5, …, 30}, sum 100, step 5. No additions, no 1-point steps, no boundary extension. |
| 8 | Number of configurations | **92**: 13 / 14 / 15 / 14 / 13 / 12 / 11 for wS = 0 … 30 |
| 9 | Only layer weights changed | Confirmed. All 34,863 population rows' layer subtotals sum to their Score v1 total (canary and every run). Indicators, lookbacks, bands, definitions, H1–H7, population, response, threshold 80, horizon and Newey-West lag are unchanged. |
| 10 | Control 40/45/15 | t_IC **0.47711861682626**, mean IC 0.00755, 80+ **−12.57%/yr**, monotonicity −0.40, Q5 − Q1 −1.26%/yr, halves +0.0155 / −0.0002, largest block 111%. This is **identical to H022 E024-07**. |

### 11. Metrics for every configuration

All 92 configurations are in `research/phase8/cp1/P8_CP1_result.json` under `configs`. Each record has:
- monthly IC series inputs;
- mean IC, Newey-West SE and t_IC, positive months;
- 80+ monthly and annualised returns, stock-months, months with an 80+ stock, mean count;
- Q1–Q5 (monthly and annualised), Q5 − Q1 and monotonicity;
- IC by year, half ICs, block sums and shares, largest block;
- D1–D5 flags, plateau base flag and boundary flag.

The structure (Score_v2 distribution and counts at 75+, 80+, 85+ and 90+) is under `structure`.

The pre-committed script recomputed every statistic, the selection and the walk-forward diagnostic offline from the exported monthly matrices. They are **identical** to the host's.

**Weight surface, t_IC.** Rows are wS and columns are wT; wF = 100 − wT − wS.

| wS \ wT | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 75 | 80 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | | | 0.06 | 0.17 | 0.26 | 0.35 | 0.42 | 0.49 | 0.57 | 0.65 | 0.73 | 0.80 | 0.86 | 0.92 | 0.94 |
| 5 | | −0.03 | 0.09 | 0.18 | 0.27 | 0.35 | 0.44 | 0.51 | 0.60 | 0.69 | 0.75 | 0.79 | 0.87 | 0.91 | 0.96 |
| 10 | −0.11 | −0.01 | 0.09 | 0.21 | 0.26 | 0.36 | 0.45 | 0.55 | 0.62 | 0.68 | 0.74 | 0.80 | 0.86 | 0.92 | **0.97** |
| 15 | −0.08 | 0.02 | 0.13 | 0.23 | 0.32 | 0.39 | 0.48 | 0.54 | 0.64 | 0.71 | 0.78 | 0.84 | 0.88 | 0.94 | |
| 20 | −0.03 | 0.07 | 0.16 | 0.25 | 0.34 | 0.43 | 0.52 | 0.59 | 0.67 | 0.73 | 0.80 | 0.85 | 0.90 | | |
| 25 | −0.03 | 0.08 | 0.20 | 0.26 | 0.37 | 0.44 | 0.54 | 0.63 | 0.70 | 0.77 | 0.81 | 0.86 | | | |
| 30 | 0.01 | 0.12 | 0.21 | 0.32 | 0.40 | 0.50 | 0.60 | 0.67 | 0.73 | 0.78 | 0.82 | | | | |

**Weight surface, 80+ annualised excess (%).** Same layout.

| wS \ wT | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 75 | 80 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | | | −2.7 | −4.0 | −3.4 | −1.2 | −0.5 | −1.8 | −4.7 | −1.5 | −1.3 | −1.6 | −0.7 | 0.5 | 0.4 |
| 5 | | −3.5 | −3.2 | −3.0 | −0.6 | −0.9 | −3.6 | −7.7 | −3.7 | −4.0 | −0.2 | 0.0 | −0.3 | 1.4 | 1.8 |
| 10 | −4.1 | −3.4 | −3.8 | −2.6 | −1.6 | −3.5 | −9.1 | −9.6 | −5.3 | −5.1 | −1.1 | 0.3 | 1.3 | 0.3 | 1.3 |
| 15 | −5.4 | −5.1 | −5.0 | −8.8 | −9.8 | −12.3 | −12.6 | −4.4 | −6.2 | 2.2 | 3.7 | 1.6 | 1.9 | 1.1 | |
| 20 | −4.4 | −2.7 | −7.6 | −8.9 | −11.2 | −9.5 | −6.5 | −1.1 | −0.6 | −1.6 | 2.5 | 1.1 | 0.6 | | |
| 25 | −4.7 | −7.9 | −7.2 | −7.0 | −8.7 | −1.5 | 5.8 | 3.9 | 0.9 | −0.9 | 2.2 | 3.1 | | | |
| 30 | −3.9 | −10.0 | −10.4 | −1.8 | 2.7 | 2.2 | 4.2 | 4.0 | 2.7 | 0.8 | 3.5 | | | | |

**Weight surface, quintile monotonicity.** The highest value in the grid is 0.7; the floor is 0.90.

| wS \ wT | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 75 | 80 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | | | −0.8 | −0.6 | −0.7 | −0.3 | −0.7 | −0.2 | −0.3 | −0.3 | −0.1 | 0.1 | 0.1 | 0.2 | 0.2 |
| 5 | | −0.9 | −0.9 | −0.9 | −0.9 | −0.7 | −0.7 | −0.1 | −0.1 | 0.1 | 0.1 | 0.1 | 0.2 | 0.6 | 0.6 |
| 10 | −0.3 | −0.7 | −0.9 | −0.5 | −0.8 | −0.4 | −0.2 | −0.2 | −0.3 | 0.1 | 0.1 | 0.2 | 0.2 | 0.2 | 0.2 |
| 15 | −0.4 | −0.7 | −0.7 | −0.9 | −0.2 | −0.2 | −0.4 | −0.2 | −0.2 | 0.1 | 0.2 | 0.2 | 0.2 | 0.2 | |
| 20 | −0.6 | −0.7 | −0.7 | −0.1 | −0.2 | −0.2 | −0.2 | −0.2 | 0.1 | 0.2 | 0.2 | 0.2 | 0.2 | | |
| 25 | −0.3 | −0.5 | −0.2 | −0.2 | −0.2 | 0.1 | −0.2 | 0.1 | 0.2 | 0.2 | 0.2 | 0.6 | | | |
| 30 | −0.1 | −0.6 | −0.7 | −0.3 | 0.3 | 0.6 | 0.5 | 0.1 | 0.0 | 0.7 | 0.2 | | | | |

**Mean IC.** It rises smoothly from −0.0012 (10/80/10) to +0.0158 (80/10/10) and is positive in 86 of 92 configurations.

**Stability.** The first-half IC is positive everywhere. The second-half IC is positive in only 51 of 92 configurations. **No configuration** has every calendar block ≤ 50% of its summed IC; 2016 is negative for the strong-ranking configurations.

### 12–17. Optimiser null and the threshold

| # | Item | Value |
|---|---|---|
| 12 | Optimiser-null method | The frozen H022 identity tether (`qr_p7_pred.Tether(seed)`: one stratum, no self-matches, partners kept). **One permutation per date is applied to the whole grid.** Each stock takes all three layer subtotals of its partner, while responses stay with the stock. All 92 configurations' complete statistics are then recomputed, exactly as in the real optimiser (`qr_h023.null_record`). |
| 13 | Null worlds | **5,000 / 5,000**, seeds 1..5,000 (the H022 seeds), runs E025-02..06 (1,000 each). Rerun E025-07 (seeds 1–25) is **identical**. Runtime is about 0.14 s per world, so nothing was reduced. Integrity: panel and layer-subtotal digests equal the pins in every batch; LEAN 18178; 0 orders; PIT audit 0. Every world's control column equals the frozen H022 / Data v2 null world of the same seed (max difference 3.6e-15). |
| 14 | Null distribution of max t_IC across the grid | mean 0.80, SD 0.87, median 0.78, p90 1.93, p95 2.24, p99 2.90, max 5.61. The null best configuration lies on the grid boundary in **94%** of worlds, most often at the corners (60/10/30, 80/20/0, 20/80/0, 80/10/10, 10/80/10). |
| 15 | **c_SEARCH** | **2.9225785052912165**, the 50th largest of the 5,000 null maxima. The 2.326 floor does not bind. Pinned in `qresearch.p8h023` (threshold commit 8b86665, null result `2819cd4c…`) and **merged (PR #79) before the real search**. The fold thresholds (diagnostic only) are 3.487 / 3.510 / 3.587 / 3.024 for 2014–2017. The full-procedure false-promotion rate is **0.54%**. |
| 16 | Highest real t_IC | **0.9720** at **80 / 10 / 10** |
| 17 | Search-adjusted percentile / p-value | 2,066 of the 5,000 null worlds (41.3%) reach at least this maximum. Null percentile **58.7%**, **p = 0.413**. t − c_SEARCH = −1.95. |

### 18–25. Qualification, plateaus, surface, best versus selected

| # | Item | Value |
|---|---|---|
| 18 | Development-qualified configurations | **0 of 92** |
| | | D1 (t > c and mean IC > 0): **0** |
| | | D2 (80+ ≥ +3%/yr): 7 |
| | | D3 (monotonicity ≥ 0.90 and Q5 > Q1): **0** (best monotonicity 0.7; Q5 > Q1 in only 7) |
| | | D4 (both halves > 0 and no block > 50%): **0** |
| | | D5 (80+ population): 92 |
| | | D2–D5 together: 0 |
| 19 | Robust plateaus | **0** |
| 20 | Plateau membership | None. Only **7** configurations meet the plateau base conditions (mean IC > 0, 80+ > 0, Q5 > Q1, both halves > 0). They form 4 disconnected regions: {30/40/30, 35/35/30, 40/30/30}, {55/15/30}, {65/10/25} and {75/20/5, 80/15/5}. |
| 21 | Plateau sizes | Largest connected region 3, below the required 4. No plateau. |
| 22 | Weight-surface summary | **A smooth, monotone ramp, not a peak and not a plateau.** t_IC rises almost linearly with Technical weight (Spearman of t with wT +0.99) and falls with Fundamental weight (−0.94). Sector weight has no systematic effect (−0.10). 24% of the grid lies within 80% of the best t_IC, but that whole region sits far below c_SEARCH and fails the economic, ordering and stability conditions. The 80+ group and the quintiles are noisy and mostly negative or non-monotone everywhere. |
| 23 | Absolute-best configuration | **80 / 10 / 10**: t_IC 0.972, mean IC 0.0158 (42/83 positive months), 80+ +1.31%/yr (31.8 stocks a month), monotonicity 0.2, Q5 − Q1 −0.27%/yr, halves +0.0262 / +0.0057, largest block 62% (2011–12), 2016 IC −0.057. It lies **on the grid boundary** (wT = 80). |
| 24 | Pre-registered selected configuration | **None.** No configuration is both development-qualified and in a robust plateau. The unrestricted plateau ranking is also empty. |
| 25 | Why selection differs | No selection exists. The absolute best is reported only; under the frozen rule it can never become a candidate (it fails D1, D2, D3 and D4 and has no plateau). |

### 26–37. Selected configuration

| # | Item | Value |
|---|---|---|
| 26–28 | Selected Technical / Fundamental / Sector weights | **None (no candidate).** |
| 29–36 | Selected mean IC, t_IC, 80+, quintiles, monotonicity, halves, yearly ICs, block concentration | **Not applicable (no candidate).** The absolute best (item 23) and the control (item 10) are reported for reference. |

Absolute best 80/10/10, for reference only:
- quintiles Q1..Q5: −0.51 / −1.64 / +0.73 / +2.16 / −0.78 %/yr;
- IC by year 2011..2017: +0.036, +0.032, +0.028, +0.026, +0.022, **−0.057**, +0.027;
- block shares: 62% / 49% / −33% / 22%.

| # | Item | Value |
|---|---|---|
| 37 | 80+ population coverage | D5 passes for every configuration: 80+ stocks exist in ≥ 60 of the 83 months, mean ≥ 2. The counts depend strongly on the weights. Control: 80+ 7.1 a month, 82 of 83 months; 75+ 17.5; 85+ 1.7; 90+ 0.5. 80/10/10: 80+ 31.8 a month, 83 months; 75+ 57.9; 85+ 15.0; 90+ 6.0. |

### 38–41. Walk-forward diagnostic

Each fold trains on decision years before Y and observes year Y. It is a diagnostic only.

| # | Item | Value |
|---|---|---|
| 38 | Fold selections | No fold produced a strict (D1–D5 plus plateau) candidate. The labelled fallbacks are in the table below. |
| 39 | Pseudo-out-of-sample results | The four observation years' 47 monthly ICs, each from its own fold's selection: mean IC **+0.0010**, Newey-West t **0.05**, 21 of 47 months positive, 80+ +0.11%/yr |
| 40 | Do the fold weights cluster? | **No** (pre-registered rule: all within L1 ≤ 20). Pairwise L1 distances reach 30. All folds favour high Technical weight. |
| 41 | Does a stable plateau exist? | **No**, neither in the full window nor in any fold (the 2015 and 2016 training windows each had one small plateau, but no qualified member) |

| Fold Y | Train months | c_fold | Selection | How | Train t | Year-Y IC | Year-Y 80+ |
|---|---|---|---|---|---|---|---|
| 2014 | 36 | 3.49 | 80/10/10 | argmax (no plateau) | 1.16 | +0.026 | +5.6%/yr |
| 2015 | 48 | 3.51 | 65/20/15 | plateau medoid, not qualified | 1.25 | +0.015 | +5.9%/yr |
| 2016 | 60 | 3.59 | 70/20/10 | plateau medoid, not qualified | 1.38 | **−0.061** | **−15.3%/yr** |
| 2017 | 72 | 3.02 | 80/10/10 | argmax (no plateau) | 0.80 | +0.027 | +4.7%/yr |

### 42–51. Candidate, protocol, confirmations, result, next decision

| # | Item | Value |
|---|---|---|
| 42 | Candidate Score v2 hash | **None.** There is no candidate, so nothing was frozen (`qresearch.p8h023.CANDIDATE = None`). |
| 43 | Candidate freeze commit | **None** |
| 44 | Pre-registered 2018–2021 validation protocol | Recorded in `research/phase8/H023_spec.md` §14 before any result: V1 fresh tethered null on the frozen validation panel, giving a pinned c_IC_VALIDATION, then t > c and mean IC > 0; V2 80+ ≥ +3%; V3 monotonicity ≥ 0.90 and Q5 > Q1; V4 2018–19 and 2020–21 mean IC > 0, no year > 50%. All four required. Prerequisite: an owner-approved extension of the Data v2 reference layers to 2018–2021 under identical rules. **It will not be used: there is no candidate to validate.** |
| 45 | 2018–2021 untouched | Confirmed. Every H023 run ends 2017-12-31; the last price row is 2017-12-29. No 2018+ data was requested. |
| 46 | Holdout untouched | Confirmed (`HOLDOUT_UNLOCK.md` absent) |
| 47 | No portfolio optimisation | Confirmed. No K, entry, exit, regime, sector cap, buffer, size, holding or cost was evaluated. No wealth, CAGR, Sharpe or drawdown statistic exists. 0 orders in every run. |
| 48 | No feature definition changed | Confirmed. Only the three layer weights varied; the Score v1 code and points are the pinned ones. |
| 49 | Nothing purchased | Confirmed |
| 50 | Final result | **NO ROBUST SCORE V2 CANDIDATE** |

```
NO ROBUST SCORE V2 CANDIDATE
```

**51. Exact next owner decision.**

Close H023 as **NO ROBUST SCORE V2 CANDIDATE**, preserved exactly as tested, and decide the programme's direction.

**Boundary flag (required report).** The absolute best sits on the wT = 80 boundary and t_IC rises monotonically with Technical weight. Under the frozen rule, any search beyond the grid needs a new owner decision. My assessment:
- a boundary best is what the null produces 94% of the time;
- the ramp adds about 0.05 of t per 5 points near the edge, so a Technical-only score would still be far from c_SEARCH 2.92;
- the 80+ group, quintile ordering and stability fail across the whole surface, and 2016 is negative throughout.

I therefore **do not recommend** an expanded weight search or a Technical-only follow-up. Phase 4 (H019) already found no qualifying technical signal in this universe.

**Recommendation:** close H023 and Phase 8 as No Production Candidate Found (a candidate test returning "No Robust Score V2 Candidate"). Not authorised without a new owner decision:
- a wider grid, a different threshold or horizon, feature-level weights, or removing Sector;
- any 2018–2021 access, the Holdout, or a portfolio.

## Programme record

| Phase | Result |
|---|---|
| 1 | No Production Candidate Found |
| 2 | No Production Candidate Found |
| 3 | No Production Candidate Found |
| 4 (H019) | Did not qualify |
| 5 (H020) | Did not qualify |
| 6 (H021-A) | Did not qualify |
| 7 (H022) | Not qualified |
| 8 (H023) | No robust Score v2 candidate |

- Hypotheses: 23 (H001–H023).
- Experiment log: 537 rows over 370 experiment IDs (`experiments/INDEX.csv`). H023 added 8 runs: E025-01 canary, E025-02..07 null and rerun, E025-08 the one real search.
- The Holdout has never been opened. Nothing has been purchased.

**Files:**
- pre-registration: `research/phase8/H023_spec.md`, `research/hypotheses/H023.md`, `src/qresearch/lean/qr_h023.py`, `strategies/S025_h023_score_v2/main.py`, pins `src/qresearch/p8h023.py`;
- canary: `research/phase8/cp1/P8_CP1_canary_E025-01.json`;
- null: `research/phase8/cp1/P8_CP1_null.json` (SHA-256 `2819cd4c…`) and `P8_CP1_null_worlds.json.gz`;
- result: `research/phase8/cp1/P8_CP1_result.json` (SHA-256 `28f88b72…`, from `P8_CP1_result.py`, committed before the run);
- tests: `tests/test_p8_h023.py`, `tests/test_p8_h023_host.py`.

**STOP.**
