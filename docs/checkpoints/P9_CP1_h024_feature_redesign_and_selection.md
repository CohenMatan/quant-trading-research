# P9-CP1 — H024 Feature Redesign and Selection

**Date:** 2026-10-11. **Decisions:**
- D201: owner approval and the frozen pre-registration, merged in [PR #81](https://github.com/CohenMatan/quant-trading-research/pull/81) before any run.
- D202: the canary, and a QuantConnect data-snapshot note.
- D203: this checkpoint.

**Status:** STOPPED, awaiting the owner.

## Short answer

H024 asked whether a small, interpretable set of point-in-time features from the frozen data can predict next-month cross-sectional returns on 2011–2017 robustly enough to justify one untouched validation. It used 11 pre-registered features, 415 equal-weight models of 2–4 features each, a search-level null of 5,000 worlds, gates D1–D6 and a robust-neighbourhood rule.

**It cannot.**

| Measure | Result |
|---|---|
| Best model (of 415) | **CBOP + CFP + HI52 + REV1M**, t_IC **2.48** |
| c_MODEL | **4.37** |
| Null comparison (model) | 35% of no-signal worlds produce a best model at least as strong (p = 0.35) |
| Best single feature | **LOWVOL**, t 1.24 |
| c_FEATURE | 3.45 |
| Null comparison (feature) | p = 0.73 |
| Models passing D1 (search-adjusted significance) | **0** |
| Development-qualified models | **0 of 415** |
| Walk-forward pseudo-out-of-sample IC | **−0.001** (t −0.10) |

```
NO ROBUST H024 FEATURE MODEL
```

**What the numbers mean.** No feature is individually convincing: the best single-feature t is 1.24. No combination comes close to the bar that 415 combinations of noise set. The tendency that recurs in the historical top models is one-month reversal, which appears in all of the top 10. It does not survive the search adjustment. Re-selecting each year produced next-year results of essentially zero on average.

## The 68 required items

### 1–7. Decision, records and periods

| # | Item | Value |
|---|---|---|
| 1 | Owner decision ID | **D201**: verbatim record `docs/owner/2026-10-11_p9cp1_h024_feature_redesign.md`, committed and merged before any H024 run (PR #81) |
| 2 | H022 permanent result | **REJECTED** (E024-07: t_IC 0.4771, mean IC 0.00755, 80+ −12.57%/yr, monotonicity −0.40, G1–G4 FAIL) |
| 3 | H023 permanent result | **NO ROBUST SCORE V2 CANDIDATE** (E025-08: best 80/10/10 t_IC 0.97, null p 0.41, 0 of 92 qualified, no plateau). 80/10/10 was never promoted. |
| 4 | Frozen Data v2 manifest | `cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb`. The pinned H022 panel `09b1de41…` was reproduced in every H024 run. |
| 5 | Development period | 83 decisions, 2011-01-31 → 2017-11-30: **DEVELOPMENT / TRAINING** data for H024 |
| 6 | 2018–2021 sealed | Confirmed. Every run ends 2017-12-31; the last price row is 2017-12-29. |
| 7 | Holdout sealed | Confirmed (`HOLDOUT_UNLOCK.md` absent) |

### 8–17. Inventory, library, models

| # | Item | Value |
|---|---|---|
| 8 | Score v1 feature inventory | `research/phase9/P9_feature_inventory.md`, read from the frozen code. Eight features: trend state, 12-1 momentum, 60-day volatility, GP/A, cash conversion, equity/assets, revenue growth, sector breadth context. It gives the exact formulas, sources, PIT timing, lookbacks, bands, families and prior research. Correlations below. |
| 9 | Candidate feature library | **11 features:** MOM, LOWVOL, GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP, EQA. They were chosen by non-return rules: eligibility, then evidence-tier ranking, then the 500-model budget. **Removed:** revenue growth (ambiguous direction); SECTOR and TREND (budget rule). **Excluded:** net issuance, industry momentum, idiosyncratic volatility, E/P, earnings drift (`research/phase9/H024_spec.md` §3). |

**Items 10–14: rationale, formula, direction, PIT availability and coverage per feature** (spec §4; coverage from canary E026-01 over 34,863 H022 stock-months):

| Feature | Rationale | Formula | Direction | PIT availability | Coverage |
|---|---|---|---|---|---|
| MOM | underreaction / continuation | `P[b−21]/P[b−252] − 1` | higher | total-return closes through t | 100% |
| LOWVOL | low-risk anomaly | SD of 60 daily log total returns | **lower** | through t | 100% |
| GPA | productive assets earn more | `GP_TTM / TA` (within FF12) | higher | M2 timing (day after SEC filing) | 100% |
| ACC | accruals mean-revert | `(OCF_TTM − NI_TTM) / TA` | higher | M2 | 100% |
| BM | value premium | `EQ / MCAP` | higher | M2 + review market cap | 100% |
| AG | over-investment | `TA / TA recorded live 12 months earlier − 1` | **lower** | live ledger 2010-01 … 2016-12 | 100% |
| REV1M | short-term price pressure reverses | `P[b]/P[b−21] − 1` | **lower** | through t | 100% |
| CBOP | cash profitability | `OCF_TTM / TA` | higher | M2 | 100% |
| HI52 | anchoring on the 52-week high | `C[b] / max(C[b−251..b])` | higher | through t; contamination-checked | 99.92% |
| CFP | cash-flow yield | `OCF_TTM / MCAP` | higher | M2 + review market cap | 100% |
| EQA | low leverage (safety) | `EQ / TA` (within FF12) | higher | M2 | 100% |

| # | Item | Value |
|---|---|---|
| 15 | Redundancy clusters | **None.** No cross-family pair reaches the 0.80 median \|Spearman\| rule. The largest pairs: GPA–CBOP +0.58; GPA–BM −0.54; REV1M–HI52 +0.53; BM–CFP +0.52; BM–CBOP −0.50; ACC–CBOP +0.48. Components = the 8 families. |
| 16 | Feature-library hash | spec `research/phase9/H024_spec.md` SHA-256 pinned in `qresearch.p9h024.SPEC_SHA256`; code `qr_h024.py` pinned; library = `p9h024.FEATURES` |
| 17 | Number of features | **11** |
| 18 | Model construction rule | every set of 2, 3 or 4 library features with at most one per component (family ∪ redundancy link); score = 100 × mean of the oriented within-date percentiles |
| 19 | Candidate-model count | **415**: 52 two-, 138 three-, 225 four-feature models |
| 20 | Candidate-model hash | `6af3616f30256226b44f2612fd5e227fd0e56a47445c621b2bfd63edf7d23922`, pinned before any null world |
| 21 | At most 4 features per model | Confirmed |
| 22 | Equal weights only | Confirmed. No fitted weights, no regression and no machine learning. |
| 23 | Canary status | **E026-01: 16/17.** All feature recomputations match (400/400); the asset ledger is consistent; engine = frozen procedure; Score v1 control exact; runtime about 0.41 s per null world. **Check 6 FAIL is explained (D202):** QuantConnect's data snapshot changed on 2026-10-11 between 07:58Z and 08:10Z. Score v1 rows outside the analysed population differ for the 12 reviews 2011-02 → 2012-01, while the eligibility sets and the pinned H022 panel reproduce exactly. No H022, H023 or H024 statistic is affected. |

### 24–29. Null calibration

| # | Item | Value |
|---|---|---|
| 24 | Feature-level null method | The frozen H022 identity tether (`qr_p7_pred.Tether(seed)`, one stratum, no self-matches, H022 seeds). One permutation per date re-indexes each stock's **complete feature vector**; responses stay. In every world, every feature's oriented statistics are recomputed and the world records the maximum feature t_IC (one-sided, pre-registered directions). |
| 25 | **c_FEATURE** | **3.4533403374111082** (50th largest of 5,000; floor not binding) |
| 26 | Model-search null method | The same worlds. All 415 models are recomputed with all statistics and the gates. Recorded: the maximum model t_IC, the fold-prefix maxima, and the full-procedure summary (cstar). |
| 27 | **c_MODEL** | **4.3672788679087295** (50th largest of 5,000; floor not binding). Fold thresholds (diagnostic only): 5.226 / 5.003 / 4.779 / 4.424. Pinned in commit 75117b0 and merged (PR #82) **before** the real search. Full-procedure false promotion **0.40%**. |
| 28 | Null-world counts | **5,000 / 5,000**, seeds 1..5,000 (E026-02..06; 1,000 each), with no duplicates |
| 29 | Null determinism | Rerun E026-07 (seeds 1–25) is **identical**. Panel, population and library equal the pins in every batch; 0 orders; PIT audit 0; LEAN 18178. |

Null distributions:

| Statistic | Mean | Median | p95 | p99 | Max |
|---|---|---|---|---|---|
| Max feature t | 1.65 | 1.60 | 2.78 | 3.45 | 5.02 |
| Max model t | 2.20 | 2.15 | 3.55 | 4.36 | 5.78 |

### 30–31. Individual features (E026-08, 2011–2017, 34,831 stock-months, 163–584 a month)

| Feature | t_IC | Mean IC | Positive months | 80+ /yr | Q1 … Q5 (%/yr) | Mono | Half 1 / half 2 | Search-adjusted p (vs null max-feature) | Passes c_FEATURE |
|---|---|---|---|---|---|---|---|---|---|
| MOM | 0.26 | +0.0041 | 40 | −0.3% | −0.31 / 1.47 / −0.29 / −0.47 / −0.39 | −0.6 | +0.023 / −0.014 | 0.996 | no |
| LOWVOL | **1.24** | +0.0222 | 44 | +1.7% | −2.11 / −0.42 / −0.01 / 0.91 / 1.69 | **1.0** | +0.013 / +0.031 | 0.73 | no |
| GPA | 0.11 | +0.0009 | 45 | −0.4% | 0.23 / 0.63 / −0.17 / 0.07 / −0.78 | −0.8 | −0.004 / +0.006 | 0.999 | no |
| ACC | 0.20 | +0.0019 | 41 | −0.9% | 0.93 / −1.88 / −0.67 / 2.49 / −0.90 | 0.0 | +0.022 / −0.018 | 0.998 | no |
| BM | −0.56 | −0.0085 | 36 | +0.4% | 1.35 / −0.67 / 0.41 / −1.42 / 0.30 | −0.5 | +0.001 / −0.018 | 1.0 | no |
| AG | 0.46 | +0.0044 | 41 | +1.3% | −0.11 / −0.69 / −0.01 / −0.42 / 1.23 | 0.5 | +0.016 / −0.007 | 0.99 | no |
| REV1M | 0.78 | +0.0100 | 40 | −0.5% | −2.50 / −0.04 / 0.86 / 2.12 / −0.44 | 0.4 | +0.005 / +0.015 | 0.93 | no |
| CBOP | 0.69 | +0.0074 | 45 | −0.4% | −0.37 / −0.37 / 1.77 / −0.64 / −0.39 | −0.5 | +0.002 / +0.013 | 0.96 | no |
| HI52 | 0.75 | +0.0118 | 42 | −0.5% | −2.04 / 0.23 / 2.11 / 0.10 / −0.45 | 0.1 | +0.026 / −0.002 | 0.94 | no |
| CFP | 0.69 | +0.0114 | 42 | +0.3% | −1.27 / −0.79 / 0.87 / 0.82 / 0.38 | 0.6 | +0.032 / −0.008 | 0.95 | no |
| EQA | **−1.70** | −0.0133 | 41 | −1.7% | 1.64 / 1.08 / −0.65 / −0.28 / −1.76 | −0.9 | −0.026 / −0.001 | 1.0 | no |

**No feature passes c_FEATURE = 3.45.** The largest t is LOWVOL's 1.24. EQA (low leverage) runs against its pre-registered direction (t −1.70); it was not flipped. Momentum, GP/A and accruals are close to zero.

### 32–42. The model search

| # | Item | Value |
|---|---|---|
| 32 | Full model-search results | all 415 models in `research/phase9/cp1/P9_CP1_result.json` (`models`). t_IC distribution: min −1.42, quartiles 0.33 / 0.79 / 1.19, p90 1.57, max 2.48. Mean IC > 0 in 355 models; t > 2 in 11. |
| 33 | Highest historical model t_IC | **2.4828**: CBOP + CFP + HI52 + REV1M |
| 34 | Search-adjusted percentile / p-value | 1,750 of 5,000 null worlds (35%) produce a best model at least this strong. Null percentile 65%, **p = 0.35**. Best feature LOWVOL: p = 0.73. |
| 35 | Passing D1 | **0** (t > c_MODEL 4.37 and mean IC > 0) |
| 36 | Passing D2 | 76 (80+ ≥ +3%/yr) |
| 37 | Passing D3 | 57 (monotonicity ≥ 0.90 and Q5 > Q1) |
| 38 | Passing D4 | 57 (both halves > 0, no block > 50%) |
| 39 | Passing D5 | 373 (80+ coverage) |
| 40 | Passing D6 | 158 (no single-feature dependence) |
| 41 | Passing all gates | **0.** The robust neighbourhood N is met by 352 models. **9** models pass D2–D6 and N together, and every one fails D1 (t 1.27–2.07). |
| 42 | Robust-neighbourhood results | no qualified model, so no neighbourhood decides anything. The historical best has 9 robust neighbours. |

Top 10 models by t_IC (descriptive):

| Model | t_IC | Mean IC | 80+ /yr | Mono | Gates passed |
|---|---|---|---|---|---|
| CBOP + CFP + HI52 + REV1M | 2.48 | 0.0255 | +7.8% (0.3 stocks/mo) | 0.9 | D2 D3 D6 N |
| CFP + GPA + HI52 + REV1M | 2.33 | 0.0228 | −14.2% | 0.9 | D3 D6 N |
| CFP + LOWVOL + MOM + REV1M | 2.27 | 0.0235 | −9.4% | 0.7 | D5 D6 N |
| CFP + HI52 + REV1M | 2.14 | 0.0235 | −5.7% | 0.8 | D6 N |
| CBOP + CFP + LOWVOL + REV1M | 2.11 | 0.0252 | −2.5% | 0.9 | D3 D4 D5 D6 N |
| HI52 + REV1M | 2.09 | 0.0257 | −5.2% | 0.7 | N |
| ACC + LOWVOL + REV1M | 2.07 | 0.0222 | +5.2% | 0.9 | D2–D6 N |
| CBOP + LOWVOL + REV1M | 2.05 | 0.0253 | +2.3% | 0.9 | D3–D6 N |
| AG + CBOP + LOWVOL + REV1M | 2.04 | 0.0223 | +5.8% | 0.8 | D2 D4 D5 D6 N |
| LOWVOL + REV1M | 2.02 | 0.0237 | +4.7% | 0.9 | D2–D6 N |

### 43–54. Selected model

| # | Item | Value |
|---|---|---|
| 43 | Final deterministic selected model | **None** (no qualified model) |
| 44–53 | Selected features, formulas, mean IC, t_IC, 80+, quintiles, monotonicity, halves, yearly IC, block concentration | **Not applicable.** For reference, the historical best CBOP + CFP + HI52 + REV1M has mean IC 0.0255 and t 2.48. Its 80+ group returned +7.8%/yr but averaged only 0.3 stocks a month in 19 of 83 months, so D5 fails. Quintiles: −1.46 / −1.59 / 0.20 / 1.37 / 1.46 %/yr (monotonicity 0.9). Halves: +0.042 / +0.009. IC by year: +0.086, −0.014, +0.034, +0.061, −0.008, +0.013, +0.004. Blocks: 2011–12 = 54% of the summed IC, so D4 fails. |
| 54 | Leave-one-feature-out (historical best, reference) | without CBOP 0.0235 (92% of the full mean IC); without CFP 0.0233 (91%); without HI52 0.0191 (75%); without REV1M 0.0158 (62%). D6 passes; D1 is what fails. |

### 55–58. Walk-forward diagnostic

Each fold trains on decision years before Y, then applies the frozen rule with c_FOLD(Y).

| Fold | Train months | Selection | How | Train t (vs c_FOLD) | Year-Y IC | Year-Y 80+ |
|---|---|---|---|---|---|---|
| 2014 | 36 | ACC + CFP + MOM + REV1M | argmax (no strict) | 3.94 (vs 5.23) | +0.050 | −4.5%/yr |
| 2015 | 48 | ACC + CFP + MOM + REV1M | argmax (no strict) | 4.31 (vs 5.00) | −0.038 | −17.0%/yr |
| 2016 | 60 | CFP + LOWVOL + MOM + REV1M | argmax (no strict) | 2.96 (vs 4.78) | +0.010 | +5.6%/yr |
| 2017 | 72 | CFP + HI52 + REV1M | argmax (no strict) | 2.73 (vs 4.42) | −0.030 | −29.5%/yr |

| # | Item | Value |
|---|---|---|
| 55 | Fold selections | above. No fold produced a strict candidate; each reports its highest-t training model, labelled as such. |
| 56 | Feature overlap | CFP and REV1M are in all four fold selections, MOM in three, ACC in two, LOWVOL and HI52 in one. Pairwise overlap 2–4 features. |
| 57 | Pseudo-OOS IC | 47 months: mean **−0.0013**, Newey-West t **−0.10**, 20 of 47 positive |
| 58 | Pseudo-OOS economic result | 80+ group **−9.9%/yr** against the population |

The in-sample t of the training-window best model reached 3.94 and 4.31 early on. Each time, the following year gave nothing on average. That is the pattern of selecting noise.

**Feature-selection stability:**

| | MOM | LOWVOL | GPA | ACC | BM | AG | REV1M | CBOP | HI52 | CFP | EQA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| In qualified models | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| In top 10 | 1 | 6 | 1 | 1 | 0 | 1 | **10** | 4 | 4 | 5 | 0 |
| In walk-forward folds | 3 | 1 | 0 | 2 | 0 | 0 | **4** | 0 | 1 | **4** | 0 |

### 59–60. Controls (H024 population; descriptive only, never candidates)

| # | Control | t_IC | Mean IC | 80+ /yr | Mono | Q5 − Q1 | Halves |
|---|---|---|---|---|---|---|---|
| 59 | Score v1 (40/45/15) | 0.47 | 0.0074 | −12.6% | −0.2 | −1.2%/yr | +0.015 / −0.000 |
| 60 | H023 80/10/10 | 0.97 | 0.0158 | +1.3% | 0.2 | −0.2%/yr | +0.026 / +0.006 |

Both are identical to their earlier results, up to the 32 stock-months without a valid HI52.

**Non-gating diagnostics:**

| Horizon | Best model's t | Maximum over all models |
|---|---|---|
| 2-month | 1.92 | 2.08 |
| 3-month | 1.36 | 1.51 |

Neither changes anything.

### 61–68. Confirmations, result and next decision

| # | Item | Value |
|---|---|---|
| 61 | Candidate freeze hash | **None** (no candidate; `qresearch.p9h024.CANDIDATE = None`) |
| 62 | No parameter added after results | Confirmed. Features, formulas, directions, the library, thresholds, gates and rules are exactly as pinned before the run; the extraction script was committed before the run. |
| 63 | No portfolio evaluated | Confirmed. No wealth, CAGR, Sharpe, drawdown or SPY statistic; 0 orders in every run. |
| 64 | 2018–2021 untouched | Confirmed |
| 65 | Holdout untouched | Confirmed |
| 66 | Nothing purchased | Confirmed |
| 67 | Final result | **NO ROBUST H024 FEATURE MODEL** |

```
NO ROBUST H024 FEATURE MODEL
```

**68. Exact next owner decision.**

Close H024 as **NO ROBUST H024 FEATURE MODEL**, preserved exactly as tested, and decide the programme's direction.

**Expansion note (spec §11, reported only).** All of the strongest historical models contain one-month reversal (REV1M), often with cash-flow yield (CFP). Other reversal horizons and other yield definitions were not in the library and were not added. Any such search would be a new hypothesis. I **do not recommend** it:
- REV1M alone has t 0.78;
- the best combination is p = 0.35 against its search null;
- re-selecting every year produced nothing out of sample (IC −0.001).

**My recommendation:** close H024 and Phase 9 as No Production Candidate Found. This is the third consecutive score-construction test on this universe and window (H022, H023, H024) with a null result. That covers the original Score v1, its reweightings, and a redesigned 11-feature library with 415 combinations. Large US stocks in 2011–2017 show no cross-sectional predictability in these documented factor families strong enough to survive an honest search correction.

**Not authorised without a new owner decision:** a wider library, other lookbacks or thresholds, weights, machine learning, 2018–2021, the Holdout, or portfolio work.

**Prior exposure of 2018–2021 (spec §14.1).** This is moot, because no candidate exists. It remains recorded: low volatility (H005) and the Phase 2 ideas (H014, H016, H017) have already met 2018–2021.

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
| 9 (H024) | No robust feature model |

- Hypotheses: 24 (H001–H024).
- Experiment log: 545 rows over 378 experiment IDs (`experiments/INDEX.csv`). H024 added 8 runs: E026-01 canary, E026-02..07 null and rerun, E026-08 the one real search.
- The Holdout has never been opened. Nothing has been purchased.

**Files:**
- spec `research/phase9/H024_spec.md`;
- inventory `research/phase9/P9_feature_inventory.md`;
- module `src/qresearch/lean/qr_h024.py`;
- host `strategies/S026_h024_features/main.py`;
- pins `src/qresearch/p9h024.py`;
- canary `research/phase9/cp1/P9_CP1_canary_E026-01.json`;
- null `research/phase9/cp1/P9_CP1_null.json` (SHA-256 `db1cb192…`) and its per-world file;
- result `research/phase9/cp1/P9_CP1_result.json` (SHA-256 `756c1eb5…`);
- tests `tests/test_p9_h024*.py`.

**STOP.**
