# H028 — Fixed Strong Shrinkage Learned Stock Score: frozen pre-registration (v1)

Owner decision **D217** (`docs/owner/2026-10-12_p13cp1_h028_fixed_strong_shrinkage.md`, verbatim). This file is hash-pinned in `qresearch.p13h028` with the code that implements it, before any H028 null world or result exists. Nothing in it changes after a result is seen. H028 is the final λ-specific experiment for this architecture: no other λ is ever tried.

## 1. Status and periods

- **Closed and unchanged:**
  - H026 — REJECTED — LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY.
  - **H027 — REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE.**
  - Their pins (`qresearch.p11h026`, `qresearch.p12h027`), nulls (E028-02/03, E029-02/03) and results are never modified or overwritten.
- **Data v2.1:** frozen under D207 (manifest SHA-256 `ef0a7a66…`), with the D213 owner exception (`research/phase11/data_v21/owner_exception_D213.json`). NEW_YEARS_MAPPING stays recorded as failed as written. It is not rebuilt, and no PIT rule changes.
- **Development data:** 2011–2021, fully seen. H028 is explicitly post-hoc (motivated by H026/H027 results), so it gives **development evidence only**. It is never called validation, confirmation or out-of-sample proof.
- **Holdout:** 2022-01-01 → 2026-08-31 stays sealed. Nothing from it is read: no prices, fundamentals, SPY, SEC filings, features or sanity checks.

## 2. The question

Does a fixed strong-shrinkage learned score add robust stock-selection value beyond a simple LOWVOL portfolio, while still beating SPY after costs?

## 3. The procedure (`qr_h028.run_world_fixed`)

- **Unchanged from H026/H027:**
  - the 11 features (MOM, LOWVOL, GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP, EQA) with their PIT formulas (`qr_h024`);
  - the transform x = 2 × percentile − 1;
  - the 63-session SPY-relative TSR target, cross-sectionally rank-transformed;
  - the label-availability rule (`qr_h026.Fitter`: a month enters training only if its label's exit session is before the cutoff);
  - the monthly-equal-weighted Ridge (`qr_h026._solve`);
  - Top-15, at most 3 per FF12 sector, 10% initial cap, monthly next-open rebalance, $7 per order + 0.10% slippage per side, long only, no leverage, $100,000 (`qr_h026.simulate`);
  - SPY buy and hold (`qr_h026.spy_simulate`);
  - the path metrics.
- **The only change:** for each outer year Y in 2015–2021, ONE Ridge fit with **λ = 100**.
  - It is fitted at the cutoff = Y's first decision review (2014-12 → 2015 … 2020-12 → 2021), on every month whose label exits before that cutoff.
  - There is no inner-year portfolio simulation, no comparison of λ values and no fallback.
  - The code path never executes the H026/H027 inner λ-selection loop.
- **The real H028 portfolio** = `run_world_fixed(months, real feature matrices)`.

## 4. LOWVOL-conditional null (5,000 worlds)

- The null is H027's exactly: `qr_h027.conditional_permuted`, pinned and unchanged.
  - The persistent identity tether `qr_p7_pred.Tether(seed)` has no self-matching.
  - Each recipient keeps its own LOWVOL, returns, prices, corporate actions, sector and universe membership.
  - It receives the donor's complete vector of the ten other features.
- **Every world reruns the complete H028 procedure at λ = 100:** the seven annual fits, scores, Top-15 with the sector cap, trading, commissions, slippage and the SPY comparison. There is no λ search in any world.
- **Seeds:** 1–2,500 (E030-02) and 2,501–5,000 (E030-03). E030-04 reruns seeds 1–25.
  - The rerun must reproduce every row value and every coefficient **exactly** (bit-equal JSON values). Otherwise STOP.
- **Recorded per world** (fields of H027):
  - S_WEALTH and wealth;
  - excess CAGR, MaxDD and volatility;
  - monthly beta, up and down capture;
  - years beating SPY;
  - 7 yearly returns and 7 λ (all 100);
  - a coefficient digest (full coefficients for seeds 1–25).
- **c_WEALTH_H028** = the one-sided empirical 99th percentile = the 50th largest of the 5,000 null S_WEALTH (`qr_h026.critical_value`).
  - It is pinned (with the null hash, seeds, Data v2.1 manifest, pipeline hashes and the λ = 100 rule) and merged before the real run.
  - Empirical p = (1 + #{null S ≥ real S}) / 5,001.

## 5. Risk adequacy (two steps; the same rule as H027)

- **Rule:** for each of four measures, at least 1% of the 5,000 worlds (≥ 50) must be at least as defensive as the reference portfolio:
  - annualised volatility ≤;
  - MaxDD ≥ (shallower);
  - monthly beta ≤;
  - monthly down-capture ≤.

  Up-capture is reported.
- **Step 1, before c is pinned.** The reference is H027's real values (vol 0.163921, MaxDD −0.261152, beta 0.795037, down-capture 0.775512). The real H028 values do not exist yet, and H028 differs from H027 essentially only in 2015.
- **Step 2, in the real-result assessment, before any gate is judged.** The same rule is applied with the realised H028 values.
- **If either step fails:** "H028 BLOCKED — CONDITIONAL NULL INADEQUATE". No other null is tried.

## 6. 2016–2021 integrity with H027 (pre-registered tolerance)

H027 chose λ = 100 for 2016–2021, so H028 must reproduce H027 there. `qr_h028.equality` compares the real H028 result with the real H027 result, recomputed in the same run through the frozen `qr_h026.run_world`.

### 6.1 EXACT (bit-identical)

Any difference means **"STOP — UNEXPECTED PIPELINE DIFFERENCE"**, and no gate is judged.

- For every outer year 2016–2021: λ = 100 in both, and the intercept and 11 coefficients are identical.
- Every 2016–2021 decision month's score vector is identical.
- Every 2016–2021 month's target list and held name set (after rebalance) are identical.
- The number of orders in every 2016–2021 month after the transition month is identical.
- The exact replay (`qr_h028.replay`, a line-for-line replica of `qr_h026.simulate` that also records weights and per-month costs) reproduces both terminal wealths bit for bit.

### 6.2 PATH-DEPENDENT (bounded, not identical)

The frozen mechanics are path-dependent, so yearly returns, turnover and costs in 2016–2021 cannot be bit-identical:
- positions carried over from December 2015 keep their drifted values (no resizing);
- new positions are sized at equity / 15;
- the $7 commission is fixed in dollars;
- 2016's calendar return includes the overnight gap from 2015's final holdings.

The **transition month** (the 2015-12 review, executed in January 2016) is expected to differ in turnover and orders, and is reported. For 2016–2021, the yearly-return difference and the yearly turnover difference (transition month excluded) must lie within the **pre-registered tolerance**:

- **Calibration (canary E030-01, before any null world):**
  - In conditional-null worlds 1–100, compare `run_world_fixed` with λ = 100 everywhere against the same world with H027's real λ schedule (0.01, 100, 100, 100, 100, 100, 100). These pairs mirror the real H028-vs-H027 difference exactly: only 2015's λ differs.
  - Every pair must pass every EXACT check. Otherwise STOP before the null.
  - **tolerance(year, quantity) = max(1.5 × the largest absolute calibration difference in that year, floor)**, with floor = 0.25 return points and 0.025 turnover.
  - The tolerance table is pinned (with its hash) in `qresearch.p13h028` before the null runs.
- **Real run:** if the EXACT checks pass but a path-dependent difference exceeds the tolerance, STOP and explain before any conclusion.

### 6.3 H027 reproduction (real run)

- The recomputed H027 must equal E029-05: wealth $311,396.77 and S_WEALTH 0.171482, at 1e-9 relative.
- `run_world_fixed` with H027's schedule must equal `qr_h026.run_world` bit for bit: wealth, the 7 yearly returns and the 7 coefficient vectors.

## 7. LV15_CONTROL

Exactly H027 (`qr_h027.lv15`):
- each month, the 15 eligible stocks with the lowest 60-day volatility (ties go to security id);
- the same sector cap, sizing, execution and costs.

It is not optimised.

## 8. Gates (all required)

| Gate | Requirement |
|---|---|
| B1 | S_WEALTH_real > c_WEALTH_H028 and empirical p ≤ 0.01 |
| B2 | terminal wealth H028 > LV15 and CAGR H028 > LV15 (same costs) |
| B3 | wealth H028 ≥ 1.15 × SPY and CAGR H028 − CAGR SPY ≥ +2.0 points (an economic requirement) |
| B4 | H028 ahead of LV15 (yearly log-relative > 0) in ≥ 5 of 7 years, AND Σ 2015–2017 > 0, AND Σ 2018–2021 > 0 |
| B5 | \|MaxDD H028\| ≤ 1.25 × \|MaxDD SPY\| and volatility H028 ≤ 1.25 × SPY |
| B6 | 0.20% slippage per side, same selections, no refit: H028 wealth > SPY and > LV15 (each at 0.20%) |

**Statuses:**
- All pass → "H028 DEVELOPMENT CANDIDATE — FIXED λ=100 SCORE FROZEN — FINAL HOLDOUT SEALED".
  - The final model is then fitted once: λ = 100, on every development month whose label exits before 2021-12-31 (the last session; `Fitter.fit(last session, 100)`). The intercept and 11 coefficients are frozen and hashed.
  - For any future Holdout test, there is no retraining and no λ reselection.
- Any gate fails → "H028 REJECTED — FIXED STRONG SHRINKAGE DOES NOT ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM".
  - **Then STOP:** no other λ, no wider grid, no H029.
- **Disclosure if B4 passes:** "The temporal gate was repaired by the pre-registered fixed-λ change primarily through 2015; the later years were already observed under H027."

## 9. Non-gating diagnostics (never rescue)

1. **2015 comparison, H027 (λ = 0.01) vs H028 (λ = 100):**
   - coefficients (each feature's value, absolute change, sign change);
   - the 2015 return, and relative to SPY and LV15;
   - 2015 MaxDD, turnover and year-end wealth;
   - score rank correlation per 2015 month and Top-15 overlap (computed in the same real run, from the same arrays).
2. **Yearly H028 vs LV15, SPY and H027** for 2015–2021, plus the H027/H028 comparison table.
3. **LOWVOL-factor regression** (exactly H027: H028 period return − SPY on the lowest-LOWVOL-quintile factor). Reports α, annualised α, Newey-West t (lag 2), γ and R².
4. **Sector-neutral; $200K / Top-10 / Top-20; market regime** (as H027).
5. **March 2020:** H028, LV15 and SPY returns and log-relatives, with nothing removed. 2020 must reproduce H027 within the §6 rules.

## 10. Canary E030-01 (no real H028 result)

The canary checks:

- λ = 100 for every fit of an H028 world. The fit log shows 7 fits, all λ = 100. Instrumented call counts show exactly 7 `Fitter.fit` calls and 1 portfolio `simulate` call per world (no inner selection).
- **The real H027 reproduction through the fixed path:** `run_world_fixed(real, H027 schedule)` equals `qr_h026.run_world(real)` bit for bit, and equals the pinned E029-05 wealth and S_WEALTH. H027 is public; no H028 real quantity is computed.
- **The conditional null unchanged except λ:**
  - H027 conditional worlds 1–25 recomputed through the pinned `qr_h027.run_conditional` equal the committed E029-02 rows (digest).
  - Each of those worlds, rerun through `run_world_fixed` with that world's own H027 λ schedule, equals its H027 row exactly.
- **Data and permutation integrity:**
  - the feature / response panels equal the H026 pins;
  - LOWVOL is never permuted and the other ten move as one donor vector (seeds 1–2);
  - LV15 picks equal an independent lowest-volatility walk;
  - costs by hand; the c order statistic.
- **The §6.2 calibration** (100 pairs: all EXACT checks pass) and the resulting tolerance table.
- **Synthetic worlds** (H027's generator; returns from features + noise on the real month structure; SPY real; λ = 100 worlds):
  - **A (LOWVOL only):** five replicates × 19 nulls. Pass if the median percentile is < 0.90.
  - **B (LOWVOL + GPA):** three replicates × 19 nulls. Pass if every percentile is ≥ 0.90.
- Stage memory.

## 11. Run order

1. Canary E030-01, then pin the tolerance table.
2. Null E030-02 and E030-03, then rerun E030-04.
3. Adequacy step 1, then pin c_WEALTH_H028 and merge.
4. The ONE real run E030-05. Then, in order:
   - H027 reproduction;
   - the §6 equality;
   - adequacy step 2;
   - B1–B6 and the diagnostics;
   - the final score only if all pass.
5. P13-CP1, then STOP.

The Holdout is never run.

## 12. Not allowed

- Any λ other than 100, any λ search or comparison, and any wider grid.
- Changing features, formulas, transforms, target, label rules, folds, K, sector cap, mechanics, costs or LV15.
- Any regime, crash, trend or SPY filter, and intentional cash.
- Any new data, null or factor.
- Removing or winsorising any period.
- Opening the Holdout.
