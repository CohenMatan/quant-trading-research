# P7-CP7 — H022 Data v2 Real Evaluation

**Date:** 2026-10-11. **Decisions:** D197 (owner approval, committed before the run, `docs/owner/2026-10-11_p7cp7_h022_v2_real_evaluation.md`), D198 (this checkpoint). **Status:** STOPPED awaiting the owner.

## Short answer

The one authorised real evaluation of H022 (E024-07) ran cleanly on frozen Data v2:
- the pinned panel was reproduced exactly;
- the PIT audit was 0;
- QuantConnect's default build 18178 was used, with 0 orders.

It asked: do eligible stocks with a higher frozen Conviction Score v1 earn a higher next-month total shareholder return than lower-scored eligible stocks?

**They do not.** All four frozen gates fail.

| Gate | Required | Result | |
|---|---|---|---|
| G1 significance | t_IC > 2.3798883324991866 and mean IC > 0 | t_IC **0.4771**, mean IC +0.0076 | **FAIL** |
| G2 economic | 80+ group ≥ +3.0% a year vs the population | **−12.57% a year** | **FAIL** |
| G3 monotonicity | quintile Spearman ≥ 0.90 and Q5 > Q1 | Spearman **−0.40**; Q5 − Q1 = −1.26% a year | **FAIL** |
| G4 stability | both halves > 0 and no block > 50% of summed IC | second half **−0.0002**; largest block **111%** | **FAIL** |

What the numbers mean:
- The monthly IC is essentially zero: positive in 38 of 83 months.
- A t_IC of 0.48 is at the 63rd percentile of the 5,000 null worlds (p = 0.37). That is what a score with no predictive information looks like.
- The stocks scoring 80+, the ones the frozen portfolio would buy, did *worse* than the average eligible stock, by about 1% a month.
- No pre-registered diagnostic points the other way, though no diagnostic could change the result. The checks were:
  - sector-demeaned IC, t 0.87;
  - Fama-MacBeth increment beyond momentum and size, t 0.49;
  - 2-month horizon, t 0.09;
  - 3-month horizon, t −0.23.

**NOT QUALIFIED — H022 fails one or more frozen gates**

## The 59 required items

### 1–11. Provenance and pre-run integrity

| # | Item | Value |
|---|---|---|
| 1 | Owner approval ID | **D197**: committed in 6d567f5 *before* the launch, which was the run's build commit |
| 2 | Experiment ID | **E024-07** (S024 v1.0, real mode, kind research; QuantConnect backtest `9bac596b…`) |
| 3 | Actual LEAN build | **v2.5.0.0.18178** (default build, recorded) |
| 4 | Data v2 manifest | `cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb` |
| 5 | Score v1 hash | spec `7d3ae5df…`; code as pinned in `qresearch.p7score` (checked) |
| 6 | H022 spec hash | `2c99f9623065a0d9576f35ea208733c47ce5ec3bbfe2f587ab2a9451b0061f58` |
| 7 | Null-method / statistics hash | `qr_p7_pred.py` `bc6fd8e8…`, `qr_h020_stats.py` `426d3721…`, `qr_xs.py` `bd69bc6a…` |
| 8 | Pinned panel digest | `09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0` |
| 9 | Observed panel digest | `09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0`, **identical**; the host would otherwise have computed nothing. Score and eligibility tables are also identical to the frozen E998-01 export. |
| 10 | Pinned c_IC | **2.3798883324991866** (threshold commit cc2b0d8, null result `371c7e22…`); the Data-v1 value was not used |
| 11 | Pre-run mismatch | **None.** The pre-run gate passed 17/17 on the clean committed tree: manifest and every frozen file, Score v1, spec, `qr_p7_pred`, null-method files, c_IC, null result, panel = canary, threshold commit, canary 25/25 with PIT 0, end ≤ 2017-12-31, config, clean tree, approval committed, no earlier output (`research/phase7/cp7/P7_CP7_prerun_output.txt`). |

### 12–17. Population, responses and integrity

| # | Item | Value |
|---|---|---|
| 12 | Decision dates | **83**: 2011-01-31 → 2017-11-30; the last response ends 2017-12-29 |
| 13 | H022 population per decision | min **163**, median **434**, mean **420.0**, max **585** |
| 14 | Primary responses | **34,863** stock-months in the population; 34,859 used |
| 15 | Response status | ok 34,755; truncated (delisting / acquisition: last real close) 90; no bar after t (return 0) 14; unverified split (excluded) 4 |
| 16 | PIT audit | **all 11 counters 0** |
| 17 | Corporate-action integrity | Verified by the canary on this identical panel (E999-02): 120/120 fresh single-security recomputations agree to 1e-9, and 102,913 responses were recomputed with 0 mismatches. |

### 18–22. G1: significance

| # | Item | Value |
|---|---|---|
| 18 | Monthly IC series | 83 months: mean 0.00755, median −0.02872, SD 0.14199, min −0.2876, max +0.3526; positive in 38 of 83 months |
| 19 | Real mean IC | **0.0075504904395016096** |
| 20 | Real t_IC | **0.47711861682625983** (Newey-West SE 0.015825185128441718, lag 2) |
| 21 | c_IC comparison | t_IC − c_IC = **−1.9028**; 1,845 of 5,000 null worlds (36.9%) reach at least this t_IC; null percentile 63.1%; p = 0.369 |
| 22 | **G1** | **FAIL** |

### 23–26. G2: economic magnitude

| # | Item | Value |
|---|---|---|
| 23 | 80+ mean monthly demeaned return | **−1.0478%** |
| 24 | 80+ annualised (× 12, frozen convention) | **−12.573%** (floor +3.0%) |
| 25 | 80+ coverage | 589 stock-months; 82 of 83 months contain 80+ stocks (mean 7.1 a month); 1 month without |
| 26 | **G2** | **FAIL** |

### 27–34. G3: monotonicity

Mean demeaned response by frozen score quintile:

| # | Quintile | Annualised | Monthly |
|---|---|---|---|
| 27 | Q1 (lowest score) | **+0.980%** | +0.0817% |
| 28 | Q2 | **−1.533%** | −0.1278% |
| 29 | Q3 | **+0.952%** | +0.0794% |
| 30 | Q4 | **−0.097%** | −0.0081% |
| 31 | Q5 (highest score) | **−0.282%** | −0.0235% |

| # | Item | Value |
|---|---|---|
| 32 | Q5 − Q1 | **−1.262% a year** |
| 33 | Monotonicity Spearman | **−0.40** (required ≥ 0.90) |
| 34 | **G3** | **FAIL** |

### 35–42. G4: stability

| # | Item | Value |
|---|---|---|
| 35 | First-half mean IC (41 months, 2011-01 → 2014-05) | **+0.01549** |
| 36 | Second-half mean IC (42 months) | **−0.00020** |

Calendar-block contributions to the summed IC (total 0.6267):

| # | Block | Summed IC | Share |
|---|---|---|---|
| 37 | 2011–2012 | +0.6967 | **111.2%** |
| 38 | 2013–2014 | +0.2211 | 35.3% |
| 39 | 2015–2016 | −0.7664 | −122.3% |
| 40 | 2017 | +0.4754 | 75.9% |

| # | Item | Value |
|---|---|---|
| 41 | Largest block share | **111.2%** (limit 50%) |
| 42 | **G4** | **FAIL**: the second half is negative and the largest block exceeds 50% |

### 43. Final all-four-gates result

**FAIL on all four** (G1, G2, G3, G4). There is no partial credit.

### 44–50. Pre-registered non-gating diagnostics

These were computed after the gates and cannot change the result.

**44. Sector-demeaned IC:** mean 0.0104, t 0.87. The flag "sector-driven" is false. There is no score–return relationship within sectors either.

**45. Regime IC** (mean IC, months):

| Regime | Mean IC | Months |
|---|---|---|
| STRONG | +0.0094 | 62 |
| NORMAL | +0.0748 | 9 |
| WEAK | −0.0393 | 7 |
| RISK_OFF | −0.0706 | 5 |

The small non-STRONG cells (5–9 months) are noise-level and are not a basis for anything.

**46. Fama-MacBeth incremental diagnostic** (frozen controls: 12-1 momentum and log PIT market cap; sector-demeaned response):
- score slope 0.00536, t 0.49;
- null percentile 77%;
- the score adds no information beyond momentum and size.

**47. 2-month horizon** (overlapping, Newey-West lag 2):

| Measure | Value |
|---|---|
| Mean IC | 0.0016 |
| t | 0.09 |
| 80+ | −20.0% a year |
| Monotonicity | −0.2 |
| Q5 − Q1 | −2.2% a year |

**48. 3-month horizon** (overlapping, Newey-West lag 3):

| Measure | Value |
|---|---|
| Mean IC | −0.0048 |
| t | −0.23 |
| 80+ | −20.6% a year |
| Monotonicity | −0.6 |
| Q5 − Q1 | −3.8% a year |

**49. IC by year:**

| 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|
| +0.035 | +0.023 | −0.003 | +0.021 | +0.004 | **−0.067** | +0.043 |

**50. Population by year** (decisions / stock-months / 80+ stock-months):

| Year | Decisions | Stock-months | 80+ stock-months |
|---|---|---|---|
| 2011 | 12 | 3,212 | 67 |
| 2012 | 12 | 3,635 | 60 |
| 2013 | 12 | 4,897 | 42 |
| 2014 | 12 | 6,116 | 74 |
| 2015 | 12 | 5,343 | 105 |
| 2016 | 12 | 5,590 | 91 |
| 2017 | 11 | 6,070 | 150 |

### 51–57. Confirmations

| # | Confirmation |
|---|---|
| 51 | **No new parameter was tried.** One run, one mapping, the frozen score, response, horizon, threshold, gates and diagnostics. The extraction script was committed before the run (6d567f5). |
| 52 | **No observation was removed after seeing the result.** The only exclusions are the 4 pre-registered unverified-split responses. |
| 53 | **No portfolio evaluation was run.** No wealth, CAGR, Sharpe, drawdown or SPY comparison. |
| 54 | **0 orders.** |
| 55 | **2018–2021 untouched.** The run ends 2017-12-31; the last price row is 2017-12-29. |
| 56 | **Holdout untouched** (`HOLDOUT_UNLOCK.md` absent). |
| 57 | **Nothing purchased.** |

### 58. Formal conclusion

```
NOT QUALIFIED — H022 fails one or more frozen gates
```

All four gates fail. This is the real result of the pre-registered falsification test. It will not be rerun or tuned.

### 59. Exact next owner decision

Close H022 as **Rejected**, preserved exactly as tested, and decide the programme's direction. Options:
- **Stop Phase 7: No Production Candidate Found** (recommended).
- Any new idea would be a **new hypothesis**, pre-registered from scratch. It cannot be a modification of Score v1, its weights, the 80 entry, the +3% floor, the horizon, sectors or regimes. Nothing in these diagnostics suggests a direction worth pre-registering: every horizon, sector-neutral and incremental view is null or negative.

Not authorised: another H022 evaluation, any change to H022, a portfolio, 2018–2021, the Holdout.

## Programme record

**Phase 7: H022 tested once on real data, NOT QUALIFIED.**

| Phase | Result |
|---|---|
| 1 | No Production Candidate Found |
| 2 | No Production Candidate Found |
| 3 | No Production Candidate Found |
| 4 (H019) | Did not qualify |
| 5 (H020) | Did not qualify |
| 6 (H021-A) | Did not qualify |
| 7 (H022) | Did not qualify |

- Hypotheses tested: 22 (H001–H022).
- E024-07 is this phase's only research run.
- The Holdout has never been opened. No data has been purchased.

**Files:**
- result: `research/phase7/cp7/P7_CP7_result.json` (SHA-256 `f0995e0d…`);
- extraction: `research/phase7/cp7/P7_CP7_result.py`;
- pre-run gate: `research/phase7/cp7/P7_CP7_prerun.py` and its output.

**STOP.**
