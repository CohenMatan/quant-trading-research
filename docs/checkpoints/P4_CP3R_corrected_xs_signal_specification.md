# P4-CP3R: Corrected Cross-Sectional Signal Validation Specification (H019 v1)

- **Date:** 2026-10-04
- **Programme:** Phase 4 (pre-validation methodology only)
- **Decision record:** D143
- **Owner direction:** "P4-CP3 Revision — Correct the Signal Definitions and Freeze H019 Before Any Real Validation" (`docs/owner/2026-10-04_phase4_xs_corrections_freeze_H019.md`)
- **Status:** STOP. Waiting for the owner's explicit approval of the corrected frozen specification.

**Files:**

| File | Content |
|---|---|
| `research/phase4/P4_xs_spec.md` | **H019 pre-registration v1**: SHA-256 pinned in `qresearch.p4xs.SPEC_SHA256` with the `qr_xs` constants; `tests/test_p4xs_spec.py` |
| `src/qresearch/lean/qr_xs.py` | Exact ID, the point-in-time Han-Zhou-Zhu trend factor, statistics, null and promotion rule. Synthetic-only tests in `tests/test_xs.py` |
| `research/phase4/P4_xs_power_r.py` / `.json` | Revised synthetic power study (1-month primary; 3-month comparison) |
| `research/phase4/P4_CP3_references.md` | Verification record: what was checked, from which source, what remains uncertain |
| `docs/checkpoints/P4_CP3_xs_signal_validation_architecture.md` | The P4-CP3 record, now marked as partly superseded |

---

## 1. Confirmation: no real signal test was run

None of the following was done:
- no S1 / S2 / S3 value computed on the research universe;
- no next-month or 3-month return;
- no decile, IC or t-statistic on market data;
- no null world on real data;
- no QuantConnect run;
- no 2018–2021 data in any form;
- the Holdout is locked;
- no portfolio design;
- no purchase.

Every number below is synthetic (`P4_xs_power_r.json`) or comes from the literature.

## 2. Plain Momentum formula (S1, reference)

```
S1 = PRET = P(last session of month m−1) / P(last session of month m−12) − 1
```

- Adjusted (total-return) closes; decision at the close of month m.
- This is the 11-month return skipping the decision month: Jegadeesh-Titman, the Fama-French "prior 2–12".
- **Role:** implementation sanity check, reference, and the baseline for the incremental tests. A pass is never a discovery.

## 3. Smooth Momentum: the exact information-discreteness formula (S2)

```
ID  = sgn(PRET) × (%neg − %pos)
key = −sgn(PRET) × ID
S2  = PRET quintile index (1..5) + within-quintile percentile of key in (0, 1]
```

**The sort:**
- **Sequential sort, as in the paper:** first quintiles of PRET, then ID within the quintile.
- **Direction:**
  - among winners, low ID (continuous information) ranks higher;
  - among losers, low ID (continuous losers) ranks lower.
- The key orients ID so that **"higher = higher predicted relative return"** in both tails. It is a sign convention, not a new measure.
- sgn(0) = 0, so a stock with PRET exactly 0 gets key 0.

**What it means:**
- A stock whose 11-month gain came from many small up-days ranks above one whose same gain came from a few jumps.
- **Unchanged from P4-CP3:** the counting window and the sequential sort.
- **Corrected:** P4-CP3 used the unsigned net up-day share. It orders stocks identically except at PRET = 0, but it was not stated in the published form. **The frozen definition is now ID itself.**

**Only one smoothness definition is in H019.** No R², residual volatility, positive weeks, entropy, trend fit or jump ratio.

## 4. Source for Smooth Momentum

- **Da, Z., Gurun, U. G., & Warachka, M. (2014). Frog in the Pan: Continuous Information and Momentum. Review of Financial Studies 27(7), 2171–2218.**
- Practitioner adoption: Gray & Vogel (2016), *Quantitative Momentum*.

## 5. Exact PRET definition

- **PRET = the cumulative return over the past twelve months, skipping the most recent month.** This is verbatim in two independent records of the paper.
- In our month-end notation: from the close of the last session of m−12 to the close of the last session of m−1.
- **PRET is identical to S1**, so S2's first sort stage uses exactly the reference momentum.

## 6. Positive / negative-day counting rule

| Rule | Value |
|---|---|
| Returns | Daily close-to-close total returns (adjusted closes; the CRSP 'ret' convention) |
| Window | From the first session after the last session of m−12 through the last session of m−1 (the PRET window) |
| %pos / %neg | Number of positive / negative daily returns ÷ number of valid trading-day returns in the window |
| Zero returns | Count in the denominator only (the paper's "percentage of days") |
| Minimum | 200 valid returns. **Project rule**: the paper's rule was not found. It excludes stocks with large data gaps |

## 7. Exact Trend Factor methodology (S3)

**Option A was taken: the actual Han-Zhou-Zhu construction, implemented point-in-time.**

1. **Moving-average signals** at the decision close of month t:
   - A_L,t = (mean of the last L split-adjusted daily closes, ending at the decision close) / the decision close;
   - L ∈ {3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000};
   - with less history than L, use the available closes (at least 1).
2. **Monthly cross-sectional regressions.** For every month s from 2010-02, once month s+1 has ended:
   - OLS **with an intercept** of each eligible stock's month-(s+1) total return on its eleven A_L,s;
   - rank-deficient or under-identified months give no coefficients.
3. **Expected coefficients:** E[β_L]_t = the mean of the 12 most recent completed regressions, s = t−12 … t−1. The last uses month-t returns, realised at the decision close.
4. **Signal:** S3_t = Σ_L E[β_L]_t × A_L,t (the model's expected next-month return).

## 8. Source for the Trend Factor

- **Han, Y., Zhou, G., & Zhu, Y. (2016). A trend factor: Any economic gains from using information over investment horizons? Journal of Financial Economics 122(2), 352–375.**
- **Construction verified against a complete independent reproduction:** Chen & Zimmermann, Open Source Cross-Sectional Asset Pricing.
  - Code: `OpenSourceAP/CrossSection`, `TrendFactor.py` / `TrendFactor.do`, commit 8db8924.
  - OSAP grades its replication "1_good" and the original evidence "1_clear" (t = 15.0).

## 9. Point-in-time implementation details

| Element | Point-in-time rule |
|---|---|
| Universe | Harness eligibility at each decision close (point-in-time market cap, price, ADV20; data v1 with SEC corrections) |
| S1, ID | Closes and returns up to the end of m−1 only |
| A_L | Closes up to the decision close only. **Split-adjusted, not dividend-adjusted** (the published price / split factor). Kept in a window rescaled only on splits; the ratio is unaffected by later splits |
| Coefficients | `qr_xs.TrendFactor`: a regression for month s is added only after month s+1 has ended. The score at t uses s = t−12 … t−1 and **refuses** later regressions. No full-sample coefficients; no future cross-section. Tested by `test_trend_factor_is_point_in_time` |
| Normalisation | Only by the stock's own decision-date close; no cross-sectional standardisation using future data |
| Pre-2010 data | Prices back to ≈ 2006 serve only as look-back inputs to MAs (up to 1,000 sessions). No pre-2010 return is used to estimate anything: the first regression uses March 2010 returns (D033) |
| 2018+ | The last regression feeding the last decision (2017-11) uses November 2017 returns. Everything ends by 2017-12-29 |
| Common sample | A stock counts on a date only if it is eligible and S1, ID and S3 are all defined |

## 10. Can Han-Zhou-Zhu be implemented exactly?

**Yes, the construction can be implemented exactly and point-in-time.** Four documented adaptations; none changes the method:

| # | Adaptation | Why |
|---|---|---|
| 1 | **Estimation cross-section** = the H019 universe (≥ $2B, price ≥ $5, ADV20 ≥ $5M), not the paper's broad sample (price ≥ $5, above the NYSE 10th size percentile) | Our point-in-time infrastructure covers ≥ $2B. NYSE membership is current-status in Morningstar (D061 / D107) |
| 2 | **12 completed regressions required**, so the first decision is 2011-02 | The paper's stated 12-month average. OSAP allows partial early windows; we do not. No pre-2010 returns |
| 3 | **Partial MA windows** for stocks with shorter histories | The paper is silent; this follows the OSAP reproduction |
| 4 | **Split-adjusted closes** for the A_L | As in the published construction |

**What this changes in H019 (owner, please note):**
1. **S3 is materially different from P4-CP3's simplified score. That is intended by your revision, but it should be explicit.**
   - The trend factor is a *fitted multi-horizon model*.
   - Its short lags (3–20 days) mainly carry **short-term reversal** information; its long lags (400–1,000 days) carry **long-term reversal** information. Han-Zhou-Zhu present it as combining short-, intermediate- and long-term price patterns.
   - Its "information beyond momentum" may therefore partly be short-term reversal, an effect P4-CP2 rated weak in large caps after costs.
   - **A pre-registered decomposition diagnostic** (spec §8.7) reports how much comes from the short, intermediate and long horizons. It is not gated.
2. **The common decision window shrinks to 82 dates (2011-02 → 2017-11)**, because the factor needs 12 completed regressions.
3. **The factor's turnover is likely high** (short-lag terms). The turnover diagnostic will show it. A pass would face that cost at the portfolio stage.

## 11. Explicit STOP / alternative proposal

- **Option A (exact HZZ) is feasible and is the one frozen in v1.**
- **Option B** would be a "Simplified Multi-Horizon Trend Score". It is **not** proposed: it would need its own independent pre-2018 justification and a new spec version.
- **No silent substitution:**
  - the P4-CP3 50/100/200 score is withdrawn from H019;
  - nothing else replaces it.
- **Your explicit choice is still requested** (§34), because §10.1 means S3 tests a broader hypothesis than P4-CP3 described.

## 12. Monthly ranking confirmation

- **Monthly ranking is frozen**: the close of the last session of each month.
- Daily prices are used only to compute inputs: daily returns for ID, daily closes for the MAs.
- No switch to weekly ranking based on synthetic or real results. (P4-CP3 synthetic: weekly gave identical power with four times the dates.)

## 13. Primary outcome: next 1 month

- **Response:** the total return from the **open of the first session after the decision** to the **close of the last session of the next month**.
- Decisions: 2011-02 → 2017-11 (82). The last return ends at the 2017-12-29 close.
- **Why:**
  - monthly ranking;
  - no overlap (each observation is independent of the next);
  - cleaner inference (naive tests nearly correct; §24);
  - the task is to validate predictive content, not to imitate a holding period.

## 14. Secondary 3-month diagnostic

- The same statistics to the close of month m+3, on 80 decisions (2011-02 → 2017-09), NW lag 6.
- **It cannot promote, rescue or veto anything.** A signal that fails the 1-month test is not reconsidered because of its 3-month figures. It is used only to describe persistence.

## 15. Primary cross-sectional response variable

- **The cross-sectionally demeaned next-month return:** the stock's return minus the equal-weighted mean over the same date's common sample.
- It answers "did this stock beat the stocks it was ranked against?"
- It cannot pass merely because most stocks rose. The rank IC is unchanged by the demeaning.
- The top decile's return vs SPY is reported as a diagnostic.

## 16. Quantile design

- **Deciles:** 10 equal-count buckets by ordinal rank (ties by security id). Used for P1 (top-decile excess, D10 − D1) and for reporting.
- **Quintiles:** used for monotonicity (§18).
- With ≈ 1,000–1,300 stocks: ≈ 100–130 per decile, ≈ 200–260 per quintile.

## 17. Rank-IC methodology

- **IC_t** = the Spearman correlation (average ranks) between the signal and the demeaned response over the date's common sample.
- **Why Spearman:**
  - robust to fat tails and outlier stocks;
  - scale-free across calm and volatile months;
  - uses the whole cross-section;
  - equivalent to a Fama-MacBeth slope on ranks;
  - S2 is a sort, not a number.

## 18. Monotonicity requirement (corrected before any data)

**P2:**
- **Spearman(quintile index 1..5, time-series mean quintile excess) ≥ 0.90**, i.e. at most one adjacent inversion; **and**
- **Q5 > Q1**.

**Why this changed from P4-CP3's decile rule.**
- The revised synthetic study exposed a design flaw (`P4_xs_power_r` diagnosis).
- S2's sequential sort makes its **deciles zig-zag whenever smoothness matters**: the smooth half of one momentum quintile can beat the rough half of the next.
- The decile rule (ρ ≥ 0.70) then **penalised S2 more the stronger its true smoothness edge**. In the synthetic case with a strong smoothness effect, it passed P2 in only 20% of samples, against 94% for the quintile rule.
- The quintile rule is not looser under the null: no-edge pass rates were 26% (quintile rule) vs 24% (decile rule). False promotions are controlled by the max-statistic anyway.
- **For S2 the quintiles are its momentum backbone. Its within-quintile refinement is judged by the incremental test (P6).**

This was found and fixed on synthetic data only, before any real computation.

## 19. Incremental-value test vs Plain Momentum (one frozen method)

**The within-momentum-quintile partial rank IC:**
- On each date, split the common sample into the five S1 (PRET) quintiles.
- Within each quintile, compute the partial Spearman correlation between the candidate's component and the demeaned response, controlling for S1:
  - S2: the key (−sgn(PRET) × ID);
  - S3: S3 itself.
- Average the five; take the time series; apply the HAC t.

**Requirement P6:** t_inc > c.

**It answers:** "holding conventional momentum roughly constant, does the new signal still predict next-month relative returns?"

**Rejected** (one method only): two-regressor Fama-MacBeth regressions; 5 × 5 double-sort spreads; linear residualisation.

## 20. Statistical-inference framework

1. One cross-sectional statistic per date (rank IC; incremental partial IC). The date's common shocks collapse into that one number.
2. The time-series mean with a **Newey-West (Bartlett) HAC SE, lag 2.** The primary returns do not overlap; lag 2 absorbs residual autocorrelation from persistent signals and factor returns.
3. **Calibration** by the tethered null (§21) and the family critical value (§22). The t-statistics are studentised, so the comparison stays fair when a factor-tilted signal has a more volatile IC than a random ranking.

## 21. Null / permutation method (frozen)

**Identity-tethered within-date permutation** (`qr_xs.Tether`):
- Each stock receives the **joint** signals (S1, ID, key, S2, S3) of a random partner. It keeps the partner while both stay in the common sample; stocks without a partner are re-matched at random each date.
- **Preserved:**
  - real dates, real returns and their distribution;
  - common market and sector shocks;
  - universe composition and size;
  - each date's signal distribution;
  - signal persistence;
  - the correlation between the signals.
- **Broken:** only the link between a stock's signal ranks and its own next-month return.
- **The entire procedure runs on every world:** statistics, HAC t's, quintiles and deciles, stability and the full rule.
- **R = 5,000** (seeds 1–5,000).

## 22. Family-level multiple-testing rule

- **F = max(t_S1, t_S2, t_S3, t_inc,S2, t_inc,S3)** in each null world.
- **c = the 50th largest F of the 5,000 (1%).** Every gated statistic must exceed c.
- This controls the chance that **any** of the three signals, or either incremental test, looks significant by luck.
- It accounts automatically for the strong correlation between the statistics.
- **c is committed and pinned before the real run.**
- **Synthetic check (1-month design):** the share of no-edge worlds in which any statistic exceeds c is **0.9%** in each scenario (target 1%). The complete rule's false-promotion rates are in §24.

## 23. The 1% threshold

**α = 1% is a conservative pre-registered research threshold.**
- It reflects the project's earlier experimentation with momentum-type signals on 2010–2017: H002, H003, H008 and H018's momentum and trend families.
- It is **not** a formal correction derived from a count of earlier tests.
- **P4-CP3's wording ("0.05 / (1 + 4)") is withdrawn.**

## 24. Updated effective sample size (1-month primary)

| Quantity (no-edge synthetic null; 1,000 worlds per scenario) | 1-month (primary, 82 dates, lag 2) | 3-month (diagnostic, 80 dates, lag 6) |
|---|---|---|
| Autocorrelation of the monthly IC | ≈ 0 at all lags (lag 1 ≈ −0.01) | lag 1 ≈ 0.62, lag 2 ≈ 0.28 |
| Variance inflation | ≈ 1 | ≈ 2.3 |
| **Effective independent observations** | **≈ 82** (all dates) | **≈ 35** |
| No-edge IC volatility (low / mid / high scenario) | 0.068 / 0.110 / 0.169 | 0.063 / 0.102 / 0.149 |
| Naive normal test at 1% rejects | 1.4–1.7% (close to nominal) | 2.4–3.8% (2–4× too often) |
| Null 1% critical value of the max of 5 statistics (c) | 2.8–3.2 | 3.4–3.7 |
| No-edge worlds in which **any** statistic exceeds c | **0.9%** (all scenarios) | — |
| No-edge worlds in which the **complete rule** promotes S2 or S3 | **0.0%** (all scenarios) | — |
| No-edge worlds in which the complete rule passes S1 | 0.0–0.2% | — |

**Reading:**
- The 1-month design **more than doubles the effective sample** (≈ 82 vs ≈ 35).
- It **nearly removes the small-sample distortion** of the HAC test.
- It **lowers the critical value** (≈ 3.0 vs ≈ 3.6).
- **Breadth still cannot remove the month-to-month variation of the signal's payoff (σ_IC), which remains the binding noise.**

## 25. Updated 50% power estimate and 26. updated 80% power estimate

**Synthetic, 1-month primary, c at 1%, statistical gate P3.** "Top-decile excess" = annualised demeaned top-decile excess (next-month, × 12).

| Scenario (no-edge 1-month IC sd) | 50%: rank IC | 50%: top-decile / yr | 50%: D10 − D1 / yr | 80%: rank IC | 80%: top-decile / yr | 80%: D10 − D1 / yr |
|---|---|---|---|---|---|---|
| Low (0.068) | 0.020 | **4.0%** | 8.0% | 0.029 | 5.6% | 11.3% |
| Mid (0.110) | 0.038 | **7.8%** | 15.4% | 0.050 | 10.0% | 19.9% |
| High (0.169) | 0.052 | **10.4%** | 20.9% | 0.071 | 14.2% | 28.5% |

**Same underlying information on the 3-month diagnostic horizon** (80 dates, lag 6):
- the edge needed for 50% power is about 4–5% larger in the mid and high scenarios, and about equal in the low one;
- the 50% top-decile thresholds expressed in 3-month annualised terms are 3.8% / 7.1% / 10.4%.

The 1-month annualised figure counts the first month's (undecayed) edge, so the two scales are not identical. The gain from switching horizons is **cleaner inference** (§24) more than raw power.

**Incremental test (S2 smoothness beyond momentum).** Minimum within-quintile partial IC:

| Scenario | 50% power | 80% power | S2 − S1 top-decile gain at 50% (approx.) |
|---|---|---|---|
| Low | 0.013 | 0.018 | ≈ 0.5% a year |
| Mid | 0.021 | 0.029 | ≈ 1.3% a year |
| High | 0.028 | 0.038 | ≈ 1.9% a year |

**The incremental test is the best-powered part of H019.** Its statistic is less exposed to factor noise.

## 27. Updated minimum detectable economic effect (complete rule)

**Smallest true effect that passes the COMPLETE rule (P1–P4, plain momentum-type signal).** Synthetic, 1-month primary:

| Scenario | 50%: rank IC | 50%: top-decile excess / yr | 80%: rank IC | 80%: top-decile excess / yr |
|---|---|---|---|---|
| Low | 0.023 | **4.5%** | 0.031 | 6.1% |
| Mid | 0.040 | **8.2%** | 0.052 | 10.4% |
| High | 0.057 | **11.4%** | 0.078 | 15.7% |

**How often small edges pass the complete rule:**

| True top-decile excess | Mid scenario | Low scenario |
|---|---|---|
| ≈ 2% a year | ≈ 2% | ≈ 6% |
| ≈ 4% a year | ≈ 10% | ≈ 42% |
| ≈ 6.5% a year | ≈ 30% | ≈ 85% |

**A realistic 1–3% a year edge will almost certainly not be confirmed.** This is why the failure interpretation (§30) is worded as it is.

**Smooth momentum's complete-rule power depends on momentum itself.**
- S2's standalone gates (P1–P3) use its ranking, whose backbone is momentum. So S2 can be promoted only if the momentum backbone is detectable too.
- **Synthetic illustration:** with a weak momentum edge (≈ 4% a year top decile), a strong smoothness refinement passes the incremental test almost always (≥ 93% in all scenarios at the largest synthetic refinement). But it passes the complete rule in only 20–80% (low scenario) and ≤ 19% (mid / high).
- This follows from the owner's multi-part rule (each signal must stand on its own *and* add information). It is reported so that a "none" outcome with a strong incremental statistic is read correctly.

## 28. Economic-significance floor

- **Kept unchanged: top-decile annualised demeaned excess ≥ 3.0% a year, and D10 − D1 > 0 (P1).**
- **Reassessment for the 1-month horizon:**
  - The annualised next-month top-decile excess is, gross, what a **monthly-rebalanced** top-decile book earns.
  - The drags a concentrated 12-stock book would face are unchanged by the horizon change: costs ≈ 1–1.5% a year at ≈ 25–35% monthly name turnover; cash drag ≈ 1–1.5% a year; incomplete capture.
  - **3% remains the smallest gross edge that leaves anything after these drags.**
  - The S3 trend factor's likely higher turnover makes 3% a *minimum*, not a sufficiency, for S3. The turnover diagnostic reports this; the floor is not raised for one signal.
  - **It was not changed to gain power.** Synthetically it rarely binds: the statistical MDE is 4–10% a year.

## 29. Year / subperiod stability requirements

**P4 (gated):**
- the mean IC is > 0 in **both halves** of the 82 dates (2011-02 → 2014-06 and 2014-07 → 2017-11; 41 each); **and**
- no calendar block (2011–12, 2013–14, 2015–16, 2017) contributes more than 50% of the total IC sum, and the sum is > 0.

**Reported, not gated:**
- the per-year table 2011–2017: IC, t, top-decile excess, sign;
- concentration, regime dependence and sign reversals.
- Not every year must be positive.

## 30. Exact promotion criteria (all must hold)

| Code | Condition |
|---|---|
| P1 Economic | Top-decile annualised demeaned excess ≥ 3.0% a year **and** D10 − D1 > 0 |
| P2 Monotonic | Spearman(quintile index, mean quintile excess) ≥ 0.90 **and** Q5 > Q1 |
| P3 Statistical | t (rank IC, NW lag 2) > c |
| P4 Stable | Both halves IC > 0 **and** no block > 50% of the total IC sum |
| P5 Exceptional | Through c (tethered null, max of 5, 1%); the full-rule null rate is reported |
| P6 Incremental (S2, S3) | t_inc > c |

**Outcomes:**
- **candidate:** S2 / S3 pass. If both pass, the larger t_inc is selected.
- **replication_only:** only S1 passes.
- **none:** nothing passes.

**The 3-month diagnostic never enters.**

**Pre-registered interpretations:**
- **If none passes:** *"No technical stock-selection signal large enough to satisfy the project's detection and economic-significance requirements was found."* It is **not** "no 1–3% technical edge exists": the test cannot see edges that small (§§25–27). Technical stock-selection research in this universe then stops; no RSI / MACD / ADX / etc. follow-ups.
- **If S2 or S3 passes:** *credible cross-sectional predictive information exists on 2011–2017 under the frozen test.* It is **not** a production strategy, not evidence of beating SPY, not portfolio viability and not 2018–2021 validation. The next step would be one portfolio design around the strongest surviving signal, under a separate approval.
- **If only S1 passes:** momentum is reproduced; there is no new signal; the owner decides.

## 31. Exact pre-registration file and hash

| Item | Value |
|---|---|
| File | `research/phase4/P4_xs_spec.md`, **v1** |
| SHA-256 | `3a0e36435543043ec0c6ddb30654a8d547b1b2bab7c1c9aca40b2bce2b445584` |
| Pinned in | `qresearch.p4xs.SPEC_SHA256`, together with every named constant of `qr_xs` (horizon 1, NW lag 2, decisions (2011, 2) – (2017, 11), HZZ lags, 12 regression months, ID minimum 200 days, deciles 10, momentum quintiles 5, monotonicity quintiles 5 and ρ 0.90, economic floor 3%, block cap 50%, α 1%) |
| Test | `tests/test_p4xs_spec.py` |
| Rule | Any change before your approval creates v2 with a new hash. **No change after any real statistic exists** |

## 32. Exact H019 run sequence proposed after approval (not executed)

1. **Implementation:**
   - host X985 (derived from X984);
   - split-only adjusted window;
   - 1,000-bar histories;
   - monthly regressions;
   - total-return accounting for next-open → month-end returns;
   - configs gated by `owner_approval_required`.
2. **Plumbing / fidelity canary E985-01:**
   - placebo signals give IC ≈ 0;
   - a planted signal (response + noise) is recovered at its known IC;
   - an independent slow recomputation of S1 / ID / A_L / regressions for a fixed sample is compared inside QuantConnect (digest and maximum difference only);
   - the trend-factor look-ahead guard holds;
   - universe counts match the harness;
   - every horizon ends ≤ 2017-12-29;
   - runtime, memory and output are measured.
3. **Null calibration E020-01..05:** 5,000 tethered worlds, publishing only null statistics.
4. **Freeze c:** commit and pin c and the null table (SHA-256) before any real statistic.
5. **Real run E020-06, once:** the three signals, primary and diagnostics.
6. **H019 checkpoint (P4-CP4); STOP.**

## 33. Expected runtime and cost

| Item | Estimate |
|---|---|
| Local timing | ≈ 5 ms a date at 1,250 stocks, i.e. ≈ 0.45 s a world over 82 dates, ≈ 8 min per 1,000 worlds |
| Data pass | Longer than Phase 3 because of 1,000-bar histories: ≈ 5–10 min |
| Per 1,000-world run | ≈ 25–35 min |
| Canary and real run | ≈ 15–20 min each |
| **Total node time** | **≈ 3–4 hours** over 7 runs |
| Engineering | ≈ 2 working days |
| **Cost** | **$0 beyond the existing $24 / month subscription**; no data purchase |
| Memory | Small: about 2,300 stocks × 1,000 bars ≈ 20 MB of windows |

## 34. Final verdict

**READY FOR H019 SIGNAL VALIDATION**, subject to your explicit approval of the frozen v1, including:

1. **S3 = the exact Han-Zhou-Zhu trend factor (Option A)**, with the four documented adaptations of §10. It is a broader, fitted, multi-horizon model than P4-CP3's simplified score: it includes short- and long-horizon reversal information. That is the intent of your revision, but it needs your confirmation.
2. **The corrected monotonicity rule (P2 on quintiles, §18).**
3. **The residual unverifiable details**, frozen as explicit conventions (`P4_CP3_references.md`), assessed as **not material**:
   - the PRET sort grid (quintiles, as in the replication record);
   - zero-return days in the denominator;
   - the 200-day minimum;
   - partial MA windows (OSAP);
   - the ≥ $2B estimation universe.

**If you prefer Option B, or consider any residual detail material, the verdict is NOT READY** until a v2 specification is written and approved.

**Not run:** H019, real signals, returns, ICs or permutations; 2018–2021; the Holdout; a portfolio.
