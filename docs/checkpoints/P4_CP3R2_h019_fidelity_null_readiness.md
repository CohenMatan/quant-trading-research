# P4-CP3R2: H019 Signal Implementation Fidelity and Null-Procedure Readiness

- **Date:** 2026-10-04
- **Programme:** Phase 4 (pre-validation; implementation fidelity only)
- **Decision record:** D144
- **Owner direction:** "P4-CP3R2 — Verify Exact Signal Implementation Fidelity Before H019" (`docs/owner/2026-10-04_phase4_h019_fidelity.md`)
- **Status:** STOP. Waiting for the owner's explicit approval before any H019 run.

**Files:**

| File | Content |
|---|---|
| `research/phase4/P4_xs_spec.md` | **v2**, SHA-256 pinned in `qresearch.p4xs` (§35) |
| `src/qresearch/lean/qr_xs.py` | Complete point-in-time pipeline: `Panel` → `Features` → `run_world` (real world and null worlds), `Tether` (stratified), `TrendFactor`, `ols_slopes` (Stata collinearity) |
| `tests/test_xs.py`, `tests/test_xs_pipeline.py` | Formula tests, leakage canaries, null-procedure tests, slow-reference equality test (all synthetic) |
| `research/phase4/P4_xs_synth.py` | Synthetic daily panels |
| `research/phase4/P4_xs_e2e.py` / `P4_xs_e2e_{low,mid,high}.json` | End-to-end synthetic study of the **actual pipeline** |
| `research/phase4/P4_CP3_references.md` | Source record, now with the P4-CP3R2 code-level verification |

---

## 1. Confirmation: no real H019 evaluation occurred

None of the following was done:
- no real signal values on the research universe;
- no real forward returns, ICs, deciles or promotion results;
- no real null worlds;
- no QuantConnect run;
- no 2018–2021 data in any form;
- no Holdout access;
- no portfolio design;
- no purchase.

Everything below is code inspection, literature records, or synthetic data.

## 2. Exact Smooth Momentum source / replication

- **Da, Z., Gurun, U. G., & Warachka, M. (2014). Frog in the Pan: Continuous Information and Momentum. RFS 27(7), 2171–2218.**
- The full text is blocked in this environment (every journal, SSRN and author host; only GitHub is reachable).
- **No public code replication was found:** the Chen-Zimmermann library has no frog-in-the-pan predictor.
- Every element below is therefore taken from **independent records quoting the paper's definitions**:
  - a Stockholm School of Economics thesis (2022);
  - an Aalto University replication thesis;
  - an EFMA 2024 paper;
  - several search records of the published article.
- Each element was confirmed by at least two independent records unless stated.

## 3. Exact PRET definition

- **"A firm's formation-period return in the prior twelve months after skipping the most recent month."** Verbatim in two records.
- **Implementation:** PRET = P(month-end k−1) / P(month-end k−12) − 1, on total-return closes.
- A month-end price is the stock's last bar at or before that session, at most 5 sessions earlier. This is a data-handling rule for halted stocks.

## 4. Exact ID formula

```
ID = sgn(PRET) × (%neg − %pos)
```

- ID lies in [−1, +1]. "If the series of daily returns are all positive, ID equals −1" (continuous information); +1 is the most discrete.
- sgn(0) = 0.
- **Ranking key within a PRET quintile:** key = −sgn(PRET) × ID. This is a sign orientation only: low ID ranks high among winners and low among losers.

## 5. Zero-day convention

- **Rule: zero-return days count in the denominator, as neither positive nor negative.**
- **Evidence:**
  1. The definition reads "%neg and %pos represent **the percentages of days during the formation period** with negative and positive returns". The base is the days of the formation period.
  2. The Aalto replication notes that the published proxy "does not take zero-trading-days into account". It applies no special treatment, so zeros simply dilute both shares.
  3. "All daily returns positive ⇒ ID = −1" is consistent with this base.
- **Missing sessions** (no bar): no return exists, so nothing is counted. Each daily return runs from one bar's close to the next bar's close.

## 6. Momentum-group convention

- **PRET quintiles first, then ID within each quintile.** Two independent records:
  - "double-sorts by first dividing stocks into quintiles according to their PRET and then subdividing these quintiles into ID portfolios";
  - "Quintile sorting".
- The paper's canonical setup is quintiles; it is used here.
- Within a quintile we use the continuous ID ordering (the key's percentile) rather than ID quintiles. **This changes no stock's relative order.**
- **Ties:** ordinal ranks with stable stock order for bucket membership; average ranks for correlations.

## 7. Minimum Smooth Momentum history

- **No extra minimum. ID is defined whenever PRET is**, i.e. whenever the stock has a valid price at both month-ends k−12 and k−1.
- **The invented 200-day minimum of v1 is withdrawn.** No published minimum was found, and the owner asked for no invented conventions.
- In practice a PRET-valid ≥ $2B stock has about 230 daily returns in the window.

## 8. Exact Trend Factor source / replication

- **Han, Y., Zhou, G., & Zhu, Y. (2016). A trend factor: Any economic gains from using information over investment horizons? JFE 122(2), 352–375.**
- **Implementation authority:** the Chen-Zimmermann Open Source Asset Pricing code, `github.com/OpenSourceAP/CrossSection`, commit `8db8924`.
  - `Signals/pyCode/Predictors/TrendFactor.py`;
  - `Signals/LegacyStataCode/Predictors/TrendFactor.do`;
  - `Signals/pyCode/utils/asrol.py`;
  - `Signals/pyCode/DataDownloads/CRSPDaily.py`.
- OSAP grades the replication "1_good" and the original evidence "1_clear" (`SignalDoc.csv`: t = 15.0, EW quintile long-short).

## 9. Exact 11 MA horizons

**3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000 trading days** (`TrendFactor.py` line 1392, `lag_lengths`).

## 10. Exact MA computation

**OSAP:**
- `TrendFactor.py` 1374: P = |prc| / cfacpr (split-adjusted price).
- 1380: `time_temp` = the row index of each permno's daily records.
- 1397–1410: `asrol(..., window=L, stat="mean", min_samples=1)` over `time_temp`, i.e. the last L records of that stock.
- 1422: keep the last record of each month.
- 1427–1430: divide by that month-end P.

**Ours:**
- A_L = (mean of the stock's last min(L, n) split-adjusted closes up to its month-end bar) / that close.
- `qr_xs.Features`: vectorised and tested equal to a slow reference computation.
- QuantConnect has a bar for every trading day a stock trades, so "last L records" = "last L bars".

## 11. Missing-history behaviour, per horizon

**For every L in {3 … 1000} the replication does the same thing:**
- the MA is **the mean of the available records within the last L** (minimum 1);
- the stock is **not excluded**;
- the feature is **never missing** once the stock has at least one price;
- partial windows **are used**.
- The Stata code states the reason: *"Do they require a minimum number of obs? Not discussed in the paper"* (`TrendFactor.do`, `asrol` line).

**Regressions:**
- They never meet a missing MA, because of the partial windows.
- Columns that become identical (e.g. A_600 = A_800 = A_1000 for a stock younger than 600 days) are handled stock by stock. Only exact collinearity **across the whole cross-section** omits a regressor (coefficient 0). With 1998+ history and established stocks in every month this is practically impossible, but the rule is implemented as in the replication.

**Monthly eligibility:** unchanged by MA history. Every eligible stock with a month-end bar enters the regressions and receives an S3 value.

**Is a 1,000-day MA from 250 observations equivalent to a true one?** No. It is the replication's (and, by its author's reading, the paper's unspecified) convention. **We follow it rather than invent a different one.** Its prevalence will be reported (spec §8.8).

## 12. IPO / young-stock treatment

**OSAP:** daily CRSP is downloaded from **1926** (`CRSPDaily.py` lines 48–55).
- Every stock's MAs use its complete trading history.
- Only stocks listed fewer than L days ago have partial windows.

**Ours:** QuantConnect daily data starts in 1998, and every stock gets up to its last 1,000 bars.
- **Every stock listed before about February 2006 has full 1,000-day windows even at the first regression (2010-01).**
- IPOs and spin-offs after that have partial windows, exactly as in the replication.

**Discrepancy:** none in method. The only difference is data vendors (CRSP vs QuantConnect), whose histories both reach back further than 1,000 days for established stocks.

## 13. Exact minimum Trend Factor history

| Requirement | Detail |
|---|---|
| Stock | One price (the month-end bar), with A_L over whatever history exists up to 1,000 bars (the replication's rule) |
| Model | **12 completed monthly regressions** before the first S3 value |
| Calendar | Regressions only on research data (D033 / D034: from 2010-01-04): s = 2010-01 … 2010-12, so the **first S3 = month-end 2011-01** |

**Discrepancy, stated rather than chosen silently:**
- OSAP's coefficient average uses `rolling_mean(window_size=12, min_samples=1)` (line 1537). That would allow 1–11-month averages at the start of its 1926 sample.
- The paper's construction is "the average of the past 12 months' coefficients":
  - search record: "uses the β from the past 12 months";
  - OSAP's own Stata source: "Take 12-month rolling average of MA beta coefficients (leaving out most recent one…)".
- **We require all 12.** An early score built on 1–11 noisy regressions is a different, noisier model, and the min-1 setting matters in OSAP only for 1926.
- **Consequence:** the window starts in 2011-01 rather than 2010-02. This follows the method, not sample size: it costs 11 decisions.

## 14. Exact rolling cross-sectional regression procedure

- **OSAP** (`TrendFactor.py` 1440–1520):
  - the sample is filtered (exchange, share code, |prc| ≥ $5, size ≥ NYSE 10th percentile) and joined with the MAs;
  - the response is next-month return `fRet`;
  - `asreg_collinear(y="fRet", X="A_*", by=month, window=None, add_constant=True, drop_collinear=True)` runs one cross-sectional OLS per month with an intercept;
  - `regress(..., omit_collinear=True)` (lines 216–300) omits collinear regressors and reports **coefficient 0** for them.
- **Ours** (`qr_xs.ols_slopes`):
  - identical OLS with an intercept;
  - in-order (unpivoted) QR detects a regressor spanned by the earlier ones, which is then omitted with coefficient 0 (Stata `_rmcoll` order);
  - under-identified regressions give no coefficients.
- **Sample:** the H019 eligible universe at month-end s, every eligible stock with a bar, including stocks without a 12-month history. This is the documented adaptation from P4-CP3R: ≥ $2B instead of the paper's broad sample.
- **Response:** the total return from P at month-end s to P at month-end s+1. A stock without later bars is valued at its last real close.

## 15. Exact coefficient-averaging rule

```
E[β_L]_t = (1/12) Σ_{s=t−12}^{t−1} β_L,s       (an omitted regressor contributes 0, as in OSAP)
S3_t     = Σ_L E[β_L]_t × A_L,t                (the intercept is common to all stocks; dropped, as in OSAP)
```

## 16. Exact point-in-time chronology (decision month t)

```
Close of month-end t (all data through this close is known):
  1. Month-t returns are now complete
     → run regression s = t−1: month-t returns (P at end of t−1 → P at end of t)
       on A_L at month-end t−1 (closes ≤ end of t−1)
  2. Keep the 12 most recent completed regressions: s = t−12 … t−1
     (the oldest uses month-(t−11) returns, the newest month-t returns; all realised)
  3. E[β] = their mean;  A_L,t from split-adjusted closes ≤ end of t
  4. S3_t = Σ E[β_L] A_L,t;  S1_t, ID_t from total-return closes ≤ end of t−1;
     S2_t from (S1_t, ID_t)
  5. Rank all three over the evaluation set at the close of t
Next session (t+1 open) … close of month-end t+1:
  6. The tested response: open of the first session after t → close of month-end t+1
Close of month-end t+1:
  7. Only now: regression s = t, using month-(t+1) returns
     → enters E[β] for decisions t+1 … t+12, never for t
```

- The response that S3_t predicts (step 6) is never an input to S3_t.
- The month-(t+1) returns first enter the coefficients used at t+1.
- `qr_xs.TrendFactor.expected_betas` refuses regressions s ≥ t.

## 17. Trend Factor leakage-canary results

`tests/test_xs_pipeline.py` runs the full pipeline on synthetic daily panels; all tests pass:

| Test | Shows |
|---|---|
| `test_future_prices_do_not_change_past_signals` | Price changes after month-end k leave every S1 / ID / S2 / S3 value at decisions ≤ k unchanged; later decisions change (sensitivity check) |
| `test_next_month_returns_do_not_change_the_score_that_predicted_them` | Changing the month-(k+1) path leaves S1–S3 at k unchanged while the responses change. S3 at k+1 changes. Regressions s < k are unchanged; regression s = k changes |
| `test_truncation_after_decision_leaves_signals_unchanged` | Deleting all data after the month-end-k close (and the later universe) leaves the signals at k identical |
| `test_late_entrants_do_not_alter_earlier_regressions` | A stock entering at month k_in leaves every regression s < k_in and every signal up to k_in unchanged; regression s = k_in changes |
| `test_trend_factor_is_point_in_time`, `test_trend_factor_refuses_lookahead` | The score at t uses exactly s = t−12 … t−1 |
| `test_pipeline_runs_and_chronology` | The first decision is the 13th research month; regressions run from the first research month to the last decision − 1 |
| `test_vectorised_features_match_slow_reference_definitions` | Every A_L, PRET, ID, regression response and forward return equals an independent slow computation (> 500 stock-months) |
| `test_young_stocks_use_partial_windows_as_replicated` | A 1,000-day MA of a young stock = the mean of its whole history |

## 18. Earliest valid date for each signal

| Signal | First valid decision | Why |
|---|---|---|
| S1 Plain Momentum | **2010-01** (month-end 2010-01-29) | The first research month-end. Needs prices at 2009-01 and 2009-12 (look-back history only) |
| S2 Smooth Momentum | **2010-01** | Same window as S1 |
| S3 Trend Factor | **2011-01** (2011-01-31) | 12 completed regressions on research data (s = 2010-01 … 2010-12) |

## 19. Final common research window

- **Decisions 2011-01 → 2017-11** (month-end closes); the last next-month return ends at the 2017-12-29 close.
- **3-month diagnostic:** 2011-01 → 2017-09.
- **Regressions:** s = 2010-01 → 2017-11.

## 20. Number of usable monthly decisions

**83** (v1 had 82, because it started the regressions at 2010-02 without a mechanical reason). The halves are the first 41 and the last 42 dates.

## 21. Whether the power study had to be updated

**Yes.** The window barely changed (82 → 83), but **the null procedure changed materially**: every null world now re-estimates the trend factor and re-sorts S2. So the study was redone with the **actual pipeline** on synthetic daily panels (`P4_xs_e2e.py`).

## 22. Updated power figures

**End-to-end synthetic study of the actual pipeline** (`P4_xs_e2e.py`).
- **Panels:** synthetic daily panels of 1,100 stocks with IPOs and delistings. They have 48 history months plus research months 2010-01 → 2017-12, and 83 decisions.
- **Three IC-noise scenarios:** the no-edge 1-month IC volatility of S1 is 0.064 / 0.113 / 0.157 (low / mid / high).
- **Null:** 1,000 tethered worlds per scenario, each re-running the complete procedure.
- **Independent check:** 100 independent no-edge panels per scenario, each judged with c.
- **Planted edges:** 25 panels per edge level per signal. Each signal gets an edge in its own information, i.e. a monthly drift proportional to the score known at the month-end.

**Null calibration and false promotion**

| | Low | Mid | High |
|---|---|---|---|
| c (1%, max of 5 statistics, R = 1,000) | 2.72 | 2.67 | 2.85 |
| Tethered null: any statistic > c | 0.9% | 0.9% | 0.9% |
| Tethered null: complete rule promotes S2 / S3 | 0.0% | 0.0% | 0.0% |
| Tethered null: complete rule passes S1 | 0.0% | 0.0% | 0.0% |
| Null t-statistic dispersion (S1 / S2 / S3; ideal 1.0) | 1.00 / 1.00 / 1.05 | 0.98 / 0.99 / 1.03 | 0.98 / 0.98 / 1.04 |
| **Independent no-edge panels:** any statistic > c | 3% | 0% | 1% |
| Independent: complete rule promotes S2 / S3 | 1% | 0% | 0% |
| Independent: complete rule passes S1 | 1% | 0% | 0% |

- **Pooled independent-panel rate:** 4 of 300 = 1.3% (95% interval ≈ 0.4–3.4%), consistent with the 1% design.
- **Pooled false promotion of S2 / S3:** 1 of 300.
- Panel-to-panel variation is expected: here one panel's c judges other panels. In H019, c comes from the same data it judges.

**Effective sample size**
- Next-month ICs are essentially uncorrelated over time: lag-1 autocorrelation ≈ −0.01, and the variance-inflation factor is ≈ 0.94 (sampling noise around 1).
- **So all ≈ 83 monthly decisions count as independent observations.** The 3-month design gave ≈ 35.

**Minimum detectable effects (top-decile annualised demeaned excess)**

| Signal | Scenario | Statistical gate, 50% | Statistical gate, 80% | **Complete rule, 50%** | **Complete rule, 80%** |
|---|---|---|---|---|---|
| S1 Plain Momentum | Low | 2.8% | 4.4% | **4.1%** | 7.1% |
| | Mid | 7.2% | 10.3% | **7.7%** | 11.2% |
| | High | 10.9% | 15.3% | **12.3%** | 17.2% |
| S3 Trend Factor (fitted inside each world) | Low | 3.3% | 4.6% | **4.3%** | 6.6% |
| | Mid | 5.8% | 8.3% | **9.9%** | 12.5% |
| | High | 9.4% | 14.4% | **14.7%** | 21.1% |

- **S3's complete-rule MDE is higher than its statistical one** because the planted trend information overlaps momentum, so the incremental gate binds. Fitting 11 coefficients each month adds noise as well.
- **The S2 incremental (smoothness) test,** with a momentum backbone of ≈ 11% a year top-decile excess:
  - with no smoothness edge, S2 is never promoted (0% in every scenario), although its standalone t passes 72–100% of the time on the backbone. **The incremental gate works.**
  - with the smallest planted smoothness edge (≈ +2% a year on S2's top decile), the incremental test detects it in **100%** of panels, and the complete rule promotes S2 in **100% / 96% / 76%**.
  - With a **weak** momentum backbone, S2's standalone gates bind (P4-CP3R: ≤ 19% complete-rule power in the mid / high monthly-model scenarios). This is reported, not changed.

**Comparison with the earlier monthly-model study (P4-CP3R).** S1's complete-rule 50% MDE was 4.5 / 8.2 / 11.4%; the end-to-end figures are 4.1 / 7.7 / 12.3%. The conclusions are unchanged:
- edges of roughly **4–12% a year** are detectable;
- **a realistic 1–3% a year edge is not**;
- the pre-registered failure interpretation therefore stands.

## 23. Exact Smooth Momentum null procedure

In null world r, at each month-end:
1. Split the regression set into strata **full** (PRET and ID defined) and **partial**.
2. Each receiver keeps (or is newly assigned) a partner of its stratum (`Tether`, seed r).
3. The receiver takes the partner's PRET **and** ID as a pair.
4. S1 = PRET. The PRET quintiles are **recomputed** on the mapped PRET values. The key and S2 are **recomputed** from the mapped pair.
5. The statistics use the receiver's **real** next-month return.

## 24. Exact Trend Factor null procedure

In the same world, at each month-end:
1. Each receiver takes the partner's complete A_3 … A_1000 vector, from the **same partner** as its PRET and ID.
2. At the close of month k: run regression s = k−1 of the receivers' **real** month-k returns on their mapped A_{k−1}.
3. E[β] = the mean of the world's own 12 latest regressions. S3 = mapped A_k · E[β].
4. Rank and compute statistics as in the real world.

## 25. Is the Trend Factor re-estimated inside null worlds?

**Yes.** Nothing from the real world's fit is reused. A null world's coefficients come from regressions of real returns on permuted inputs, i.e. from noise, as the procedure would produce under no predictive relationship. `test_null_world_reestimates_the_trend_factor_and_keeps_strata` checks that every regression's coefficients differ from the real world's.

## 26. How the S1 / S2 dependency is preserved

- PRET, ID and the moving averages of a receiver always come from **one** partner, i.e. one real price path. So:
  - ID stays the ID of that PRET's path;
  - quintile membership follows PRET;
  - the two-stage sort is recomputed exactly.
- Tested: `test_null_world_preserves_the_s1_s2_dependency` (each receiver's PRET and ID equal one source's; S2 equals the two-stage sort of that pair).
- Persistence: `test_null_partners_persist_across_months`.

**What is preserved and broken overall.**
- **Preserved:**
  - real dates, returns and their distribution;
  - market, sector and style shocks;
  - universe composition;
  - the evaluation set: identical in every world (`rec` sets tested equal);
  - each date's feature distribution within each stratum;
  - feature persistence;
  - cross-signal dependence.
- **Broken:** a stock's features ↔ its own returns, including the returns that fit the trend factor.

## 27. Exact family-level max-statistic procedure

- **Per world:** F = max(t_S1, t_S2, t_S3, t_inc,S2, t_inc,S3). Each t is a Newey-West (lag 2) t-statistic over the 83 dates.
- **R = 5,000 worlds** (seeds 1–5,000) in five batches of 1,000. They are seed-deterministic and independent of the batch.
- **c = the 50th largest F (α = 1%).**
- **Sequence:** the null runs first; c and the per-world table are committed and SHA-256-pinned before the real run; then the real world is evaluated once.
- **Every gated statistic must exceed the same c.**

## 28. Exact quintile monotonicity rule

| Item | Value |
|---|---|
| Rule (P2) | ρ = Spearman(quintile index 1..5, time-series mean demeaned quintile return) **≥ 0.90**, **and** Q5 > Q1 |
| Inversions | With 5 points, ρ ≥ 0.90 allows **at most one adjacent inversion** |
| Top vs bottom | **The top quintile must exceed the bottom one** |

**Why the earlier decile rule was structurally incompatible.**
- S2 ranks every stock of a higher PRET quintile above every stock of a lower one.
- Its deciles are the rough and smooth halves of each PRET quintile.
- When smoothness matters, the smooth half of quintile q can beat the rough half of quintile q+1, so the decile means **zig-zag by construction**.
- A decile-rank rule therefore penalised S2 **more the stronger its true smoothness effect**.
- For S2, the quintiles are its momentum backbone. Its refinement is judged by the incremental test (P6).

## 29. Synthetic false-positive comparison of the rule

From P4-CP3R (`P4_xs_power_r`; synthetic, before any real data):

| Quantity | Decile rule (ρ ≥ 0.70, top half > bottom half) | Quintile rule (ρ ≥ 0.90, Q5 > Q1) |
|---|---|---|
| P2 passes by chance, no-edge worlds (mid scenario; P2 alone) | 24% | 26% |
| Complete rule promotes S2 / S3, no-edge worlds (all scenarios) | 0.0% | 0.0% |
| Complete rule passes S1, no-edge worlds | 0.0–0.2% | 0.0–0.2% |
| P2 passes for S2 with a strong true smoothness edge | **20%** | **94%** |

- P2 is a shape requirement, not the false-positive control; the max-statistic is.
- The new rule removes a structural bias without raising false promotions.
- **It is frozen in v2 and cannot change once H019 starts.**

## 30. The 1% threshold

**Frozen:** α = 1%, a conservative pre-registered research threshold reflecting earlier momentum-type experimentation on 2010–2017. It is not a formally derived correction.

## 31. The +3% annualised economic floor

**Frozen unchanged:** the top-decile annualised demeaned excess must be ≥ 3.0% a year, and D10 − D1 > 0.
- Gross, a monthly-rebalanced top-decile book earns the annualised next-month excess.
- Costs (≈ 1–1.5% a year) and cash drag (≈ 1–1.5% a year) make 3% the minimum gross edge.
- Nothing in this fidelity review changes that reasoning.

## 32. Exact future H019 run sequence (not executed)

1. **Plumbing / fidelity canary E985-01:**
   - placebo features;
   - a planted signal with known IC;
   - independent slow recomputation inside QuantConnect (digest only);
   - look-ahead guard;
   - universe and history-coverage counts;
   - horizon ends;
   - runtime.
2. **Null worlds E020-01..05:** 5,000 worlds, full procedure each; null statistics only.
3. **Compute c** (50th largest F).
4. **Commit and pin** c and the null table (SHA-256).
5. **Verify a clean working tree**, and that the spec hash and c pins pass their tests.
6. **One real evaluation E020-06**, S1 / S2 / S3 together.
7. **H019 checkpoint (P4-CP4).**
8. **STOP.**

**No real evaluation may start before step 4.** After that, nothing can change: not α, c, the promotion rule, the monotonicity rule or the economic floor.

## 33. Expected runtime

| Item | Estimate |
|---|---|
| Local, synthetic (N = 1,100, 83 decisions, 95 regressions) | ≈ 0.65 s per world, including all regressions; 1,000 worlds in ≈ 11 min on one core (measured: 651–655 s per scenario) |
| Per null run on the B2-8 node | ≈ 25–40 min, including the data pass |
| Data pass | 1,000-bar histories for ≈ 2,300–2,500 stocks; daily arrays of ≈ 3,000 sessions; ≈ 150–200 MB |
| Canary and real run | ≈ 20 min each |
| **Total** | **≈ 3.5–4.5 node-hours** |

## 34. Expected QuantConnect cost

- **$0 beyond the existing $24 / month subscription.** No data purchase.

## 35. Exact files and spec hashes

| Item | Value |
|---|---|
| Pre-registration | `research/phase4/P4_xs_spec.md` **v2**, SHA-256 `15fb0451d535ae31d234822ad60f58230f580b23a6683f2df67936429a47ca1e` |
| Pin | `qresearch.p4xs.SPEC_SHA256` and `CONSTANTS` (window (2010, 1) / (2011, 1) / (2017, 11), 83 decisions, HZZ lags, 12 regressions, ID minimum 1, PRET staleness 5, deciles 10, momentum quintiles 5, monotonicity quintiles 5 and ρ 0.90, floor 3%, blocks, α 1%) |
| Tests | `tests/test_p4xs_spec.py` |
| Previous versions | v1 (`3a0e3643…`, P4-CP3R) and the P4-CP3 draft are superseded and kept in git history |

## 36. Final verdict

**READY FOR H019 RUNS**

Every READY condition holds:

| Condition | Status |
|---|---|
| Smooth Momentum source-faithful | Formula, PRET, zero-day rule and quintile grouping confirmed by independent records. The invented minimum removed |
| Trend Factor source-faithful | Implemented to the replication code: lags, partial windows, normalisation, intercept OLS with Stata collinearity omission, 12-month coefficient average |
| Missing history verified, not assumed | Taken from the replication code, whose author states the paper is silent. QuantConnect's 1998+ history gives established stocks full windows |
| Chronology leakage-safe | Five strict point-in-time canaries pass |
| Null reproduces the full procedure | Every world re-estimates the trend factor and re-sorts S2 |
| Dependencies preserved | Joint partner features; tested |
| Dates mechanical | The research start fixes the first regression; 12 regressions fix the first decision |
| Promotion rules frozen | v2 pinned |

**Disclosed, not unresolved:**
1. **The ≥ $2B estimation universe for the trend-factor regressions** (the P4-CP3R adaptation).
2. **12 required regressions vs OSAP's start-up min-1** (§13). The paper's 12-month average is followed.
3. **The full papers remain inaccessible here.** The frog-in-the-pan conventions rest on independent quoting records; the trend factor rests on the graded replication code.

**If you consider any of these material, the verdict is NOT READY** until it is resolved, e.g. by checking the two full papers in a session that can reach them.

**Nothing runs until you approve.**
