# H024 — Feature Redesign and Selection: pre-registration (FROZEN before any H024 feature value or return)

**Status:** FROZEN pre-registration (owner D201, 2026-10-11).

- **Pinning.** The SHA-256 is pinned in `qresearch.p9h024.SPEC_SHA256`, with the code of `src/qresearch/lean/qr_h024.py`, and committed and merged before any H024 QuantConnect run.
- **Model library.** Generated mechanically by §6 from the canary's non-return feature correlations; its hash is pinned before any null world or real result.
- **No changes.** Nothing here may change after any H024 statistic is seen. A genuine defect means STOP, document it and ask the owner.

## 1. Identity and permanent records

- **Question.** Can a small, interpretable set of point-in-time features, built from the frozen approved data, robustly predict next-month cross-sectional returns over 2011–2017? It must be strong enough to justify one untouched validation on 2018–2021.
- **Permanent records:**
  - **H022 / Score v1: REJECTED** (E024-07: t_IC 0.4771, mean IC 0.00755, 80+ −12.57%/yr, monotonicity −0.40, G1–G4 FAIL).
  - **H023: NO ROBUST SCORE V2 CANDIDATE** (E025-08: best t_IC 0.972 at 80/10/10, null p 0.41; 0 of 92 qualified; no plateau).
  - H023's 80/10/10 is not a candidate and is never promoted. The H023 grid is not extended, and Technical weights above 80 are not searched.
- **Data roles:**

  | Period | Role |
  |---|---|
  | 2011–2017 (83 decisions, 2011-01-31 → 2017-11-30) | **DEVELOPMENT / TRAINING** |
  | 2018–2021 | SEALED VALIDATION |
  | 2022-01-01 → 2026-08-31 | SEALED HOLDOUT |

- **One search only.** One frozen feature library, one model library, one null calibration and one real development search. There is no H024 v2. If it fails, H024 fails.

## 2. Frozen inputs (unchanged)

The following are unchanged:
- **Data Infrastructure v2:** manifest `cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb`, covering universe, SEC market-cap repair, M2 timing, identity, restatement guard, security-life and share-class rules, price adjustment, corporate actions, review calendar and next-open timing. No Data v3.
- **The H022 population, response and calendar.** The pinned prepared panel is `09b1de41…`.
- **Statistics code:** `qr_p7_pred` and `qr_xs`, plus the H023 grid engine `qr_h023` (summaries and null worlds), both unchanged.
- **Host.** S026 subclasses the pinned S024 (uploaded byte-identical as `qr_s024`), which subclasses the frozen X998 (`qr_x998`).

**Target (fixed).** The response is the total shareholder return from the next-session open after review t to the next monthly review close. It is demeaned by the equal-weight mean of the H024 population on that date. Horizon one month. The 2- and 3-month horizons are diagnostics only (Newey-West lag 2 and 3).

## 3. Candidate selection for the library (before any H024 value)

### 3.1 Eligibility (owner §7)

Every candidate needs:
- an economic or behavioural rationale;
- PIT construction from Data v2;
- expected sufficient coverage;
- an exact formula fixed now;
- no 2018+ data;
- no paid data.

**Excluded by eligibility or direction (not by any return):**

| Candidate | Reason for exclusion |
|---|---|
| V1-7 revenue growth (Score v1) | Direction is theoretically ambiguous: higher growth is "better" in Score v1, but past sales growth predicts lower returns ("glamour"; Lakonishok, Shleifer & Vishny 1994). Excluded rather than tested in both directions. |
| Net share issuance | Share-count fields are unsafe as levels (D107). An implied-shares construction depends on market caps the new feed lacks for about 18% of stock-months (D187). |
| Industry / sector momentum | Tested in H021-A (sector ETF relative momentum, failed). It also overlaps V1-8. |
| Idiosyncratic volatility | Redundant with total volatility, and needs an extra factor model and window choice. |
| Earnings yield (E/P) | A second valuation proxy. Cash-flow yield is kept as less accrual-sensitive (LSV 1994). |
| Earnings-event drift | H017, separate event data |

### 3.2 Ranking of the remaining 13 candidates

The ranking uses evidence tier, then PIT quality, then interpretability. No return is used, and prior project results are recorded but never used to rank.

Literature tiers:
- **A:** replicated in large-cap US samples after publication.
- **B:** documented, weaker or less replicated.
- **C:** no direct academic support.

Where P4-CP2 graded an idea, its grade is shown.

| Rank | ID | Feature | Tier | Family | Prior project research on the same idea |
|---|---|---|---|---|---|
| 1 | MOM | 12-1 momentum (V1-2) | A (Jegadeesh & Titman 1993); P4-CP2: A, B for ≥ $2B US after 2002 | momentum | H002 (C01, failed screen); H019 S1 (2011–2017: IC t 0.22) |
| 2 | LOWVOL | 60-day volatility, low (V1-3) | A (Ang et al. 2006; Frazzini & Pedersen 2014) | risk | H005 low-volatility portfolio (passed the 2010–2017 screen, **failed Validation on 2018–2021**, E005-28); H013 lottery avoidance (C03, failed) |
| 3 | GPA | gross profitability (V1-4) | A (Novy-Marx 2013) | profitability | H016 GP/A top-20 (Phase 2 DEV **2010–2021**, rejected) |
| 4 | ACC | cash conversion = negative accruals (V1-5) | A (Sloan 1996) | accruals | none alone |
| 5 | BM | book-to-market | A (Fama & French 1992) | valuation | H017 = Value proposed, not approved, never run |
| 6 | AG | asset growth, low | A (Cooper, Gulen & Schill 2008) | investment | none |
| 7 | REV1M | 1-month reversal | A (Jegadeesh 1990; Lehmann 1990) | reversal | H001 RSI oversold reversal (C01, short holding, rejected): different construction |
| 8 | CBOP | cash-based operating profitability | B (Ball et al. 2016) | profitability | none |
| 9 | HI52 | nearness to the 52-week high | B (George & Hwang 2004); P4-CP2: C | momentum | H003 (C01, failed screen) |
| 10 | CFP | operating cash-flow yield | B (Lakonishok, Shleifer & Vishny 1994) | valuation | none |
| 11 | EQA | equity / assets (V1-6) | B (low leverage as "safety"; Asness, Frazzini & Pedersen 2019) | leverage | none alone |
| 12 | SECTOR | sector breadth context (V1-8) | C | sector | H021-A (sector ETF momentum, related, failed) |
| 13 | TREND | trend state (V1-1) | C (categorical MA state; P4-CP2 Tier D for MA timing) | momentum | H014 trend + pullback (Phase 2 DEV 2010–2021, rejected); H018; H019 S3; H020 |

### 3.3 Budget rule

Retain the **longest rank-order prefix** (at most 15) whose family-constrained model count is at most 500. That count is the number of models with 2–4 features and at most one feature per family.

| Prefix | Model count | Within budget? |
|---|---|---|
| Ranks 1–11 (8 families of sizes 2 / 1 / 2 / 1 / 2 / 1 / 1 / 1) | 415 | Yes |
| Adding SECTOR (rank 12) | 616 | No |

**The H024 library is ranks 1–11: 11 features.** SECTOR and TREND (Score v1 features) are removed by this pre-registered non-return rule. Score v1's revenue growth is removed by §3.1.

## 4. The frozen feature library (11 features)

Notation:
- b = the security's last valid bar at the review row on its current life; bars are counted on its own valid bars.
- C = split-adjusted close; P = total-return close.
- Fundamentals are the frozen PIT store values known on the selection day reflecting the review session: True TTM flows; total assets (TA) and equity (EQ) from the current record.
- MCAP = the review's point-in-time market cap: QuantConnect's value, or the Data v2 SEC market cap for repaired securities.
- **Direction:** +1 means higher is better, −1 means lower is better. It is fixed now and never flipped.
- **Scope:** the percentile ranking population, either the whole H024 population ("market") or within the FF12 sector group.

| ID | Formula (exact) | Dir | Scope | Family | Rationale | Valid when |
|---|---|---|---|---|---|---|
| MOM | `P[b−21] / P[b−252] − 1` (= Score v1 `mom_12_1`) | +1 | market | momentum | intermediate-horizon continuation (underreaction) | Score v1 input present |
| LOWVOL | SD (ddof 0) of the last 60 daily log returns of P (= Score v1 `vol60`) | −1 | market | risk | low-risk anomaly (leverage constraints, lottery demand) | present |
| GPA | `gross_profit_TTM / TA` (= Score v1 `gpa`) | +1 | FF12 | profitability | productive assets earn higher expected returns | present |
| ACC | `(OCF_TTM − NI_TTM) / TA` (= Score v1 `cash_conversion`) | +1 | market | accruals | accrual-heavy earnings are over-weighted and mean-revert | present |
| BM | `EQ / MCAP` | +1 | market | valuation | value premium (risk or overreaction) | MCAP > 0 and EQ > 0 |
| AG | `TA / TA_prev − 1`, where TA_prev = total assets recorded **live** at the review 12 months earlier for the same security (store-wide ledger recorded like the frozen revenue baseline: from 2010-01 to 2016-12; never recomputed later) | −1 | market | investment | aggressive asset growth precedes low returns (over-investment, q-theory) | TA_prev > 0 recorded |
| REV1M | `P[b] / P[b−21] − 1` | −1 | market | reversal | short-term price pressure and liquidity provision reverse | 22 valid bars in the current life |
| CBOP | `OCF_TTM / TA` | +1 | market | profitability | cash profitability is less exposed to accruals than earnings | present |
| HI52 | `C[b] / max(C[b−251..b])` | +1 | market | momentum | anchoring on the 52-week high delays reaction to good news | 252 valid bars in the current life, and no unverified split or large (≥ 10%) distribution inside the 252-bar window (the Score v1 contamination rule applied to this window) |
| CFP | `OCF_TTM / MCAP` | +1 | market | valuation | cash-flow yield: cheap relative to cash generation | MCAP > 0 |
| EQA | `EQ / TA` (= Score v1 `eqa`) | +1 | FF12 | leverage | financial safety (low leverage) | present |

**Rank scope for sector features.** GPA and EQA keep Score v1's within-FF12 scope. A group with fewer than 10 population members on the date is ranked market-wide, as in `qr_p7_score.scoped_quintiles`.

**No continuous parameter is optimised.** The lookbacks are fixed:

| Feature | Lookback |
|---|---|
| MOM | 252 / 21 |
| LOWVOL | 60 |
| REV1M | 21 |
| HI52 | 252 |
| AG | 12 months |

There is no winsorisation, clipping or smoothing: percentile ranks need none.

## 5. Population, missing data and the percentile transform

- **Population.** On each decision date the **H024 population** is the H022 population with a finite primary response, restricted to stocks for which **every library feature is valid**. Every model is therefore computed only where all its features are valid, and all models share one population and one response.
- **Coverage rule (pre-registered, non-return).** The canary measures each feature's validity over the H022 population. A feature valid for less than **90%** of H022 stock-months is removed from the library. It is not replaced. A date with fewer than 20 stocks is skipped.
- **No imputation.**
- **Percentile.** For feature f on a date, with scope group G (the whole population, or the FF12 group with at least 10 members), the oriented value is v = Dir·x. Its average rank among G (ties averaged) is r, and **p = (r − 1) / (n_G − 1)**, so p ∈ [0, 1] and 1 is best.
- **Model score.** `ModelScore = 100 × mean(p_f over the model's features)`, with **equal weights**. The score is computed in IEEE double by one fixed code path, identical in the real and null worlds.
- **High-score group:** ModelScore ≥ 80. Quintiles are frozen average-rank quintiles of ModelScore.
- **Single features.** The same transform with one feature gives each feature's statistics (Stage A).

## 6. Redundancy clusters and the model library (frozen rule, generated before any return)

**Redundancy.**
- For every pair of features from **different families**, take the cross-sectional Spearman rank correlation of the raw values on each of the 83 dates over the H024 population. This is computed in canary E026-01, which reads no response.
- If the **median over dates of |ρ| ≥ 0.80**, the pair is linked.
- **Components** are the connected components of the union of the family links and these redundancy links.

**Model library.** Every set of **2, 3 or 4 features** with **at most one feature per component**. There is no other exclusion, no regression weight and no machine learning. The maximum is 415 models.

**Freeze.** The list is generated mechanically by `qr_h024.model_library(families, links)`. It is ordered by size, then sorted feature ids. Its count and SHA-256 are pinned in `qresearch.p9h024` before any null world. If the count exceeded 500, the work would STOP; it cannot by construction.

## 7. Statistics for every feature and model

These are the H023 / H022 formulas (`qr_h023.summarise`):
- **Signal:** mean monthly Spearman IC, Newey-West t_IC (lag 2), positive months.
- **80+ group:** monthly and annualised (× 12) demeaned return, stock-months, months with an 80+ stock, mean count.
- **Ordering:** Q1..Q5, Q5 − Q1, monotonicity (Spearman of quintile index against quintile mean).
- **Stability:** IC by year, first / second half (41 / 42 months), calendar-block sums (2011–12, 2013–14, 2015–16, 2017) and largest share.
- **Coverage:** stock-months and stocks per month.
- **Feature-level only:** pairwise rank correlations.

## 8. Null calibration (5,000 worlds, both levels in the same worlds)

**Null worlds.** World w uses the frozen identity tether `qr_p7_pred.Tether(w)` (one stratum, no self-matches, the H022 seeds 1..5,000):
- each receiving stock takes its partner's **entire feature vector**, all 11 percentiles, so every feature and model score moves together;
- responses stay with the receiver;
- every feature and every model of the frozen library is evaluated with all statistics;
- the selection quantities are recomputed.

**Runs.** E026-02..06 hold 1,000 worlds each. E026-07 reruns seeds 1–25 and must be identical.

**Per-world record:**
- the maximum t_IC over the 11 oriented features (one-sided; directions as in §4);
- the maximum t_IC over the model library, and its index;
- the maximum model t_IC on each walk-forward training prefix;
- the number of models passing D2–D6 with the neighbourhood rule;
- `cstar`: the largest t_IC among models passing D2–D6, the neighbourhood rule and mean IC > 0. A candidate exists for threshold c if and only if c < cstar.

**Thresholds** (the 50th largest of 5,000, the frozen convention of `qr_xs.critical_value`):

```
c_FEATURE = max(50th largest null max-feature t_IC, 2.326)
c_MODEL   = max(50th largest null max-model  t_IC, 2.326)
c_FOLD(Y) = max(50th largest null max-model t_IC over decision years < Y, 2.326)   (walk-forward diagnostic)
```

They are pinned and merged **before** the one real search. Also reported: the full-procedure false-promotion rate, the share of worlds with cstar > c_MODEL.

**Feature level.** c_FEATURE says which features are individually convincing. It is **not** a requirement for model membership (§9).

## 9. Development qualification (all required)

| Gate | Requirement |
|---|---|
| D1 | t_IC > c_MODEL and mean IC > 0 |
| D2 | 80+ annualised demeaned return ≥ +3.0% |
| D3 | quintile Spearman ≥ 0.90 and Q5 > Q1 |
| D4 | first-half IC > 0, second-half IC > 0, and no calendar block > 50% of the summed IC |
| D5 | 80+ stocks in ≥ 60 of the 83 months, and mean 80+ count ≥ 2 a month (walk-forward folds scale the months to 60/83 of the window) |
| D6 | No single-feature dependence. For every feature of the model, the leave-one-feature-out model must have **mean IC > 0 and mean IC ≥ 0.40 × the full model's mean IC**. For a 2-feature model each leave-one-out is a single library feature (its oriented percentile); for 3 and 4 features it is a library model. |
| N | **Robust neighbourhood.** Neighbours are the library models of the **same size** obtained by replacing exactly one feature with another library feature not in the model, where the result is a library model (at most one per component). At least **3 neighbours** must have mean IC > 0, 80+ annualised > 0 and Q5 > Q1. |

A model is **development-qualified** if D1–D6 and N all pass.

## 10. Selection rule (deterministic)

Among qualified models:
1. smallest model size;
2. highest median t_IC across its **robust neighbours** (the neighbours meeting N's three conditions);
3. highest model t_IC;
4. highest 80+ annualised;
5. lexicographically smallest sorted feature-id tuple.

No manual choice, and no selection by wealth, CAGR, SPY, Sharpe or drawdown.

**Also reported:** the highest-t_IC model (the "historical best"), which may differ from the selection.

**Outcome:**

| Situation | Result |
|---|---|
| A qualified model exists | **H024 Score v3 Candidate**, status **DEVELOPMENT CANDIDATE — NOT YET VALIDATED**. Frozen per §13. Checkpoint result: **DEVELOPMENT CANDIDATE — H024 SCORE FROZEN, VALIDATION SEALED**. |
| None | **NO ROBUST H024 FEATURE MODEL** |

## 11. Diagnostics (never redefine anything)

**Walk-forward.** For Y = 2014, 2015, 2016, 2017:
1. train on decision years < Y;
2. apply §9–§10 with D1 against c_FOLD(Y);
3. observe decision year Y.

If the strict rule gives no candidate, the fold reports, with a label, the highest-t_IC model on the training window.

Reported:
- fold selections and their feature overlap;
- next-year mean IC and 80+ annualised;
- the pseudo-out-of-sample IC: the four observation years' monthly ICs of their own fold selections, with mean, Newey-West t (lag 2) and positive months.

**Feature stability.** How often each feature appears in:
- qualified models;
- the top 10 models by t_IC;
- the walk-forward fold selections.

**Controls (descriptive only, never candidates):**
- Score v1 (40/45/15 total);
- H023's 80/10/10.

Both are computed on the H024 population from the frozen layer subtotals.

**Boundary / expansion.** If the strongest model suggests an omitted feature, lookback or variant, it is reported and the work STOPs. It is never added; an expanded library is a new hypothesis.

## 12. Run plan

| Step | Run | Content |
|---|---|---|
| 1 | Canary **E026-01** (S026 canary mode) | The inherited H022 canary checks; feature validity and coverage; feature formulas recomputed independently on samples; the redundancy correlation matrix; components; the model library generated in-host; grid and engine equality with the frozen procedure on **synthetic responses**; runtime. No response is read by any H024 statistic. |
| 2 | Pin | the library hash, the component structure and the population digest; null configs |
| 3 | Nulls **E026-02..06** and rerun **E026-07** | then c_FEATURE, c_MODEL and c_FOLD pinned and merged |
| 4 | **E026-08**, once | the real development search; extraction script `research/phase9/cp1/P9_CP1_result.py` committed before the run |
| 5 | Freeze and report | freeze any candidate (§13); P9-CP1; STOP |

## 13. Candidate freeze (only if a candidate exists; before any 2018–2021 access)

Pinned, committed and merged in `qresearch.p9h024`:
- exact features, formulas, directions, scopes, missing-value rule, equal-weight rule, score construction and threshold 80;
- the Data v2 manifest;
- c_MODEL and c_FEATURE;
- the model-library hash;
- the null result hash;
- the development and walk-forward results;
- this spec's SHA-256.

The **candidate hash** is the SHA-256 of their canonical JSON.

## 14. Pre-registered 2018–2021 validation (sealed; separate owner approvals)

**Prerequisites:**
1. An owner-approved extension of the frozen Data v2 infrastructure through 2021 under identical rules, itself audited and frozen. No validation return is observed during it.
2. A frozen validation panel.

**Element:** exactly the frozen candidate, with no reselection or change of features, weights, threshold or formula. Primary statistic: monthly Spearman IC, Newey-West lag 2. Decisions 2018-01-31 → 2021-11-30.

**Gates (all four required):**

| Gate | Requirement |
|---|---|
| V1 | Fresh panel-specific identity-tethered null (5,000 worlds), pinned before the real mapping: c_IC_VALIDATION = max(50th largest, 2.326). Then real t_IC > c_IC_VALIDATION and mean IC > 0. |
| V2 | 80+ annualised demeaned return ≥ +3.0% |
| V3 | quintile Spearman ≥ 0.90 and Q5 > Q1 |
| V4 | 2018–2019 mean IC > 0, 2020–2021 mean IC > 0, and no single calendar year > 50% of the summed IC |

All four pass → **H024 VALIDATED**. Otherwise **H024 NOT VALIDATED**. One validation run only, with no tuning after it. The Holdout stays untouched.

### 14.1 Prior exposure of the validation period (disclosure rule)

2018–2021 is unopened for H024. It is **not pristine for every idea**:
- H005 (a low-volatility portfolio) was validated on 2018–2021 and failed (E005-28; H005 may never be re-validated there).
- Phase 2 developed H014 (trend + pullback), H016 (GP/A top-20) and H017 (earnings events) on 2010–2021 (D094).

If a candidate exists, P9-CP1 lists which of its features share an economic idea with those runs. The owner decides, before any validation approval, whether a 2018–2021 validation of that candidate is still informative. This rule changes nothing in development.

## 15. Not allowed

- Portfolio work: entry or exit, K, sector cap, regime limits, turnover, holding period, sizing, cost P&L, wealth, CAGR, Sharpe, drawdown, SPY.
- Machine learning of any kind, regression weights or fitted coefficients.
- Changes after results: more features, other lookbacks, other thresholds or horizons.
- A second H024 search.
- Any access to 2018–2021 or the Holdout.
