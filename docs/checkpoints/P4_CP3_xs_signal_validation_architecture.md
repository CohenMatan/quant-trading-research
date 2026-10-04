# P4-CP3: Cross-Sectional Technical Signal Validation Architecture

- **Date:** 2026-10-04
- **Programme:** Phase 4 (design and methodology only)
- **Decision record:** D142
- **Owner direction:** "Phase 4 — Design Cross-Sectional Technical Signal Validation Before Any Portfolio Backtest" (`docs/owner/2026-10-04_phase4_xs_signal_validation_design.md`)
- **Status:** STOP. Waiting for explicit owner approval before any real signal-validation run.
- **Superseded in part by P4-CP3R** (`docs/checkpoints/P4_CP3R_corrected_xs_signal_specification.md`, D143):
  - exact information-discreteness definition;
  - exact Han-Zhou-Zhu trend factor instead of the simplified score;
  - 1-month primary horizon;
  - 82 decisions 2011-02 → 2017-11.

  This document is kept unchanged otherwise, as the record of the P4-CP3 proposal.

**Files:**
- `research/phase4/P4_xs_spec.md`: the **draft pre-registration**. It is frozen and hash-pinned only after approval, before any real computation.
- `src/qresearch/lean/qr_xs.py`: signal formulas, statistics, inference, null and promotion rule (pure numpy). Tests in `tests/test_xs.py` use synthetic data only.
- `research/phase4/P4_xs_power.py` / `.json`: the synthetic power and design study.
- `research/phase4/P4_CP3_references.md`: sources and their verification status.

**What was NOT done:**
- No real signal was computed on the research universe.
- No forward return, quantile, IC or null world was computed on market data.
- No portfolio; no 2018–2021 data; the Holdout is locked; nothing was bought.
- Every number in this report comes from **synthetic** panels or from the literature.

---

## Contents

**Purpose and design (1–3)**
1. Confirmation: P4-CP2 accepted
2. Exact research question
3. Why signal validation precedes portfolio validation

**Signals and data (4–11)**
4. The three signals
5. Academic sources
6. Plain Momentum formula
7. Smooth Momentum formula
8. Combined Trend Score formula
9. Rejected alternative definitions
10. Point-in-time universe
11. Warm-up requirements

**Measurement (12–21)**
12. Ranking frequency
13. Primary future-return horizon
14. Secondary horizon diagnostics
15. Primary response variable
16. Bucket design
17. Top-minus-bottom metric
18. Rank-IC methodology
19. Monotonicity test
20. Sector treatment
21. Market-cap treatment

**Inference, power and nulls (22–32)**
22. Statistical-inference framework
23. Overlapping returns
24. Effective sample size
25. 50% power
26. 80% power
27. Year and subperiod stability
28. Incremental value vs Plain Momentum
29. Null design
30. Null repetitions
31. Multiple-testing method
32. Prior momentum attempts

**Promotion and execution (33–40)**
33. Promotion criteria
34. Economic significance
35. Turnover / implementability
36. The pre-registration file
37. Implementation and runtime
38. QuantConnect cost
39. Runs after approval
40. Go / No-Go

**Answers A–K**

---

## 1. Confirmation: P4-CP2 accepted

- The owner accepted P4-CP2 as the evidence basis (2026-10-04).
- The three signals are the ones P4-CP2 kept:
  - the reference: cross-sectional momentum;
  - two credible refinements never tested here: smooth momentum (AR2) and the multi-horizon trend score (AR3).
- Every indicator on P4-CP2's exclusion list stays excluded. So do overlays:
  - RSI, MACD, ADX, Bollinger, volume, breakouts;
  - volatility filters, regime filters, pullbacks, stops, trend exits, volatility scaling.

## 2. Exact research question

> On each month-end from 2010-02 to 2017-09, rank every eligible US stock (point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M) by each of three frozen signals.
> - **Do higher-ranked stocks earn higher returns than lower-ranked stocks over the next three months, relative to the same date's cross-section?**
> - Is the relation **economically meaningful, monotonic, stable and exceptional** against a structure-preserving null?
> - **For smooth momentum and the trend score: do they carry information beyond plain momentum?**

**Hypothesis H019 is this procedure** (the draft specification, `research/phase4/P4_xs_spec.md`). Plain momentum is the reference; its passing is a replication, not a discovery.

## 3. Why signal validation precedes portfolio validation

1. **A 12-stock book sees 12 noisy draws a month.** A cross-sectional test sees about 1,000–1,330 stocks a month (the eligible range in Phase 3).
   - Idiosyncratic noise largely averages out across the cross-section.
   - What remains is the month-to-month variation of the signal's payoff.
   - That noise source cannot be diversified away. It is also the honest measure of the signal's risk.
2. **It separates "is there information?" from "can a portfolio capture it?"**
   - Every earlier failure in this project mixed the two.
   - A failed portfolio test could not distinguish "no edge" from "too little power".
3. **It is cheap and needs no portfolio choices** (N, sizing, exits, costs). So it opens no new search dimensions.
4. **It gives the correct order of evidence.** A signal that carries no cross-sectional information cannot be rescued by portfolio mechanics. A signal that does carry it still has to survive concentration, costs and cash drag later.

**Honest limit.** Cross-sectional breadth helps much less than the stock count suggests. The binding noise is the time variation of the signal's payoff (§24). The gain over the portfolio test is real but moderate (answer A).

---

## 4. The three signals

| ID | Name | Role | Information |
|---|---|---|---|
| **S1** | Plain momentum (12-1) | **Reference / baseline** | 11-month return, skipping the most recent month |
| **S2** | Smooth momentum (frog-in-the-pan) | Candidate refinement | Momentum, then *how* it was earned (many small up-days vs a few jumps) |
| **S3** | Combined trend score | Candidate refinement | Distance of today's price above three trend horizons (≈ 2.5, 5 and 10 months) |

## 5. Academic sources

| Signal | Primary source | Supporting |
|---|---|---|
| S1 | Jegadeesh & Titman (1993, JF; 2001, JF) | Fama-French "prior 2–12" convention; Asness-Moskowitz-Pedersen (2013) |
| S2 | **Da, Gurun & Warachka (2014), "Frog in the pan: continuous information and momentum", RFS 27(7), 2171–2218** | Gray & Vogel (2016), *Quantitative Momentum* (practitioner adoption, pre-2018) |
| S3 | **Han, Zhou & Zhu (2016), "A trend factor: any economic gains from using information over investment horizons?", JFE 122(2), 352–375** | Brock-Lakonishok-LeBaron (1992); Faber (2007); Marshall et al. (2017): MA ≈ time-series-momentum information |

**Verification caveat.** The paper PDFs are blocked by this session's network policy. The formulas come from the abstracts and several independent search records quoting the definitions (`P4_CP3_references.md`). **Recommendation:** have the two definitions checked against the full texts (the owner, or a session with access) before the spec is frozen. Nothing else depends on this.

## 6. Plain Momentum formula (S1)

For a decision at the close of the last session of month m, with split- and dividend-adjusted closes P:

```
S1 = P(last session of month m−1) / P(last session of month m−12) − 1
```

- This is the cumulative return over months m−11 … m−1.
- It skips the decision month, avoiding the one-month reversal / microstructure effect.
- It is exactly the Fama-French "prior (2–12)" definition for holding month m+1.

## 7. Smooth Momentum formula (S2)

**Da-Gurun-Warachka's information-discreteness measure:**

```
ID = sgn(PRET) × (%neg − %pos)
```

- PRET is the 12-month return skipping the most recent month (= S1).
- %pos and %neg are the shares of positive and negative **daily** returns in the same window.
- A low ID means continuous information (many small moves in the direction of PRET).
- A high ID means discrete information (a few large moves).

**Our component** is the unsigned **net up-day share**:

```
NUD = (#up days − #down days) / #valid daily returns          (= −sgn(PRET) × ID)
```

- **Window:** the daily returns from the first session after the end of month m−12 through the end of month m−1, i.e. the same window as S1.
- A zero return counts only in the denominator. At least 200 valid returns are required.

**Why the unsigned form:**
- For winners, a higher NUD means more continuous gains, which the theory says persist more.
- For losers, a lower NUD means more continuous losses, which persist more on the downside.
- So within any momentum level, **a higher NUD predicts a higher relative return in both tails.** This is the same ordering as −ID among winners and +ID among losers.

**The signal is a sequential sort, as in the paper.** Stocks are sorted first by S1 into quintiles, then by NUD within each quintile:

```
S2 = MOM quintile index (1..5) + within-quintile percentile of NUD in (0, 1]
```

- Every stock in a higher momentum quintile ranks above every stock in a lower one. Within a quintile, a smoother path ranks higher.
- **S2's top decile is the smoother half of the top momentum quintile:** the paper's "continuous winners", and the long-only screen of Gray & Vogel.
- **Its bottom decile is the most continuous losers.**

**Why it measures smoothness.** It counts how many days moved the stock in each direction, independent of the size of the moves. A +30% year made of 160 up-days and 70 down-days has a high NUD. The same +30% made of two jumps and many small down-days has a low NUD. `tests/test_xs.py` checks this on two synthetic paths with equal total return.

## 8. Combined Trend Score formula (S3)

**What Han-Zhou-Zhu do:**
- For each stock and month-end they form normalised moving averages Ã_L = SMA_L / P, using P = the month-end close.
- The lags are 3, 5, 10, 20, 50, 100, 200, 400, 600, 800 and 1,000 days.
- Each month they regress next-month returns cross-sectionally on all eleven.
- They forecast with the average of the past twelve months' coefficients.
- They explicitly combine **short-term reversal, intermediate momentum and long-term reversal** information.

**Our frozen version keeps the paper's measurement and drops the fitted weights:**

```
S3 = (1/3) × [ ln(P/SMA_50) + ln(P/SMA_100) + ln(P/SMA_200) ]
```

- P is the decision close (no skip month). SMA_L is the mean of the last L adjusted closes ending at the decision close.
- At least 200 valid closes are required.
- The log makes the measure symmetric (a price 10% above or below its average counts equally).
- It equals −mean(ln Ã_L) at L = 50, 100, 200.

**Why these three horizons and no others.** They are fixed by economics, not by any search:
- **L ≤ 20 days (≈ 1 month) is excluded.** It is the short-term reversal / microstructure zone (Jegadeesh 1990; Lehmann 1990), and P4-CP2 excluded short MAs. In Han-Zhou-Zhu these lags carry *reversal* information. An unweighted average across them would mix opposite-signed effects.
- **L ≥ 400 days (≈ 19+ months) is excluded.** It is the long-run reversal zone (Jegadeesh-Titman 2001; DeBondt-Thaler), again with opposite sign.
- **50, 100 and 200 are the paper's own lags inside the intermediate momentum zone.** They are economically distinct (≈ a quarter, half a year, a year), and they are the conventional practitioner horizons.
- **Equal weights:** no estimation, so nothing is fitted to returns.

**Why it measures trend strength.** It is the average log distance of the price above its 2.5-, 5- and 10-month averages. It is positive when the price sits above all three, and larger the further and more consistently above.

## 9. Rejected alternative definitions

**Smooth momentum alternatives:**

| Alternative | Why not chosen |
|---|---|
| Consistency of monthly returns (Grinblatt & Moskowitz 2004, e.g. ≥ 8 positive months of 12) | Only 12 observations per stock, so coarse with many ties. The paper also bundles tax-loss-selling effects. Da-Gurun-Warachka's daily measure is the specific "gradual vs jump" test |
| R² or "adjusted slope" of a log-price regression (Clenow 2015) | Practitioner only (level 3–5). It mixes trend smoothness with volatility |
| Volatility-scaled ("risk-adjusted") momentum | That is a volatility signal, excluded by the owner's rule. Different hypothesis |
| Residual / idiosyncratic momentum (Blitz-Huij-Martens 2011) | Different concept (factor-neutral momentum), already tested as H008 |
| Additive composite rank(MOM) + rank(NUD) | Departs from the paper's conditional (sequential) design. It would give smoothness weight among stocks with no momentum, where the theory is silent |
| Signed ID quintile cut-offs as in the paper (5 × 5 portfolios) | Same ordering as our within-quintile NUD percentile, but coarser. The continuous version wastes no information |

**Trend score alternatives:**

| Alternative | Why not chosen |
|---|---|
| Han-Zhou-Zhu with all 11 lags and fitted rolling coefficients | A fitted, data-hungry model. It mixes short-term reversal, momentum and long-term reversal; tests a different, multi-effect hypothesis; and needs 1,000-day histories (pre-2006 data) |
| Unweighted average over all 11 HZZ lags | Mixes opposite-signed horizons (above), which would cancel |
| Binary "price above MA" count (0–3) | Throws away information; massive ties |
| MA slopes | A slope over L days is approximately an L-day return, i.e. another momentum window |
| Volatility-normalised distance | Introduces a volatility signal (excluded) |
| A skip-month version | The paper normalises by the current close. A skip would turn S3 into a smoothed S1. The incremental test controls for S1; the 1-month overlap is reported as a diagnostic (spec §8.5) |

## 10. Point-in-time universe

- **Harness eligibility of data infrastructure v1**, the same as Phase 3 (frozen; `research/phase2/data_freeze_v1.json`):
  - US common stock;
  - point-in-time Morningstar market cap ≥ $2B;
  - price ≥ $5;
  - ADV20 ≥ $5M;
  - the SEC dated correction layer on;
  - financials included (no fundamentals used).
- No present-day lists.
- **Delisted, acquired and stale stocks remain in the cross-section until their exit.** Forward returns use the proceeds at the last real close (D059 / D062).
- **Common sample:** a stock counts on a date only if S1, NUD and S3 can all be computed. Every signal is judged on exactly the same stocks.

## 11. Warm-up requirements

| Need | History |
|---|---|
| S1 and NUD | 12 months of daily closes (about 252 sessions) |
| S3 | 200 sessions |
| Method | X984's: harness warm-up from 2009-07-01, plus a 280-bar history request when a stock enters the subscription set (window 280 ≥ 254 needed) |

**First decision: 2010-02-26.**
- Its returns start 2010-03-01, the start of the Phase 3 window.
- The window was set by data-v1 universe and ADV20 availability, not by performance.
- Pre-2010 prices are used only as signal inputs (history), never as test observations.

---

## 12. Ranking frequency: Monthly (recommended)

| Criterion | Monthly | Weekly |
|---|---|---|
| Signal horizon | 11–12-month signals change slowly; month-to-month rank persistence is ≈ 0.9 for 12-1 momentum. Monthly re-ranking matches it | Week-to-week persistence is ≈ 0.97–0.99; most weekly re-rankings repeat the last one |
| Observation count | 92 decision dates | ≈ 400, but almost entirely overlapping and dependent |
| Turnover | Lower (one rebalance a month) | Higher threshold churn near bucket edges |
| Serial dependence | 3-month horizon: 2 months of overlap, NW lag 6 on 92 points | 13-week horizon: 12 weeks of overlap, NW lag ≈ 26 on ≈ 400 points. Long-lag HAC is less reliable in small samples |
| Literature convention | **All three sources (JT, DGW, HZZ) rank monthly** | Practitioner only |
| Statistical power (synthetic, §§24–26) | Same power: 0.81 at a fixed edge (101 decisions, null-calibrated c = 2.75) | Same power: 0.81 (403 decisions, c = 2.84). **4× the dates, no gain** |

**Recommendation: monthly.**
- Weekly ranking adds almost no independent information, because the extra dates are highly dependent.
- It departs from the literature and adds turnover and HAC fragility.
- The choice is made on design grounds; no backtest was used.

**Timeframe vocabulary (item 29):**

| Term | Meaning here |
|---|---|
| **Data frequency** | Daily adjusted prices (S2 needs daily up / down counts; S3 needs daily closes) |
| **Signal horizon** | 11–12 months (S1, S2); 2.5–10 months (S3) |
| **Decision frequency** | Monthly ranking |

This is not a daily trading strategy. Daily data only measures the inputs.

## 13. Primary future-return horizon: 3 months

**Why 3 months, chosen before any data:**
1. **The economic claim is persistence over the following months.** Momentum's documented holding horizon is 3–12 months (JT). Da-Gurun-Warachka stress that continuous-information momentum persists longer. A 1-month horizon tests only the first month after formation.
2. **It matches the intended use:** a monthly-ranked book holding names for months (P4-CP1).
3. **Overlap is manageable:** 3-month returns sampled monthly overlap by 2 months. A fixed NW lag of 6 handles that plus the signal's persistence. The tethered null (§29) calibrates the remaining small-sample error.
4. **6 and 12 months are too long:**
   - 12 months enters the long-run reversal zone (JT 2001).
   - 6 months needs 5 months of overlap on only 89 dates, about 15 independent observations, where HAC is unreliable.
5. **Power cost, stated honestly:** in the synthetic model 1 month has somewhat more power than 3 months (§14: 0.92 vs 0.82 at the same edge). 3 months is chosen for economic alignment and robustness to month-after-formation effects, accepting about a 10–15% larger detectable IC. **Owner choice offered (§40):** 1 month primary with 3 months as a diagnostic.

## 14. Secondary horizon diagnostics (never gated)

| Diagnostic | Decisions | NW lag | Purpose |
|---|---|---|---|
| 1 month | 94 | 2 | Non-overlapping check; the decay of information |
| 6 months | 89 | 12 | Persistence (DGW's claim for S2) |

**Synthetic comparison** at the same per-month edge (`P4_xs_power.json` → `horizons`): 

| Horizon | Decisions | Overlap | NW lag | Null 1% critical t | Power at the same edge |
|---|---|---|---|---|---|
| 1 month | 94 | 0 | 2 | 2.32 | **0.92** |
| **3 months (primary)** | 92 | 2 months | 6 | 2.96 | **0.82** |
| 6 months | 89 | 5 months | 12 | 2.94 | 0.79 |

**Honest reading.**
- In the synthetic model, information decays by ≈ 10% a month (persistence 0.90).
- There, **1 month has somewhat more power** than 3 months (≈ 10 points at a mid-size edge; roughly a 10–15% smaller detectable IC). It also has the cleanest inference (no overlap).
- 3 months is still recommended, for the reasons in §13:
  - it matches the economic claim (persistence over the months a book would hold);
  - it is less sensitive to month-after-formation effects, which matters for S3 because it has no skip month;
  - Da-Gurun-Warachka's persistence argument.
- **The power cost is stated openly.** "1 month primary, 3 months diagnostic" is offered as an owner choice (§40).

## 15. Primary response variable: cross-sectionally demeaned forward return

```
y_i = R_i(open of d+1 → close of the last session of m+3) − mean_j R_j   (same date, same common sample)
```

- **Why not stock minus SPY:**
  - In a broad bull market (2010–2017) most stocks beat zero, and many beat SPY.
  - "Stock − SPY" mixes selection with the gap between the equal-weighted universe and the cap-weighted SPY. That gap is a size / composition effect, not selection.
  - The demeaned return answers exactly "did this stock beat the stocks it was ranked against?"
- **Consistency with the statistics:**
  - Rank IC is unchanged by subtracting a date constant, so the IC is automatically market-neutral.
  - Decile means are reported on the demeaned scale.
- **Diagnostics:** the top decile is also reported against SPY's total return (spec §8.7). Terminal wealth vs SPY stays the portfolio-stage objective.
- **Timing:** the return starts at the **next open**, not the decision close, so the signal's own closing price never enters the return (execution realism; no closing-price bounce).

## 16. Bucket design: deciles

- **10 equal-count buckets** per date by signal (ordinal rank; ties broken by security id).
- With ≈ 1,000–1,330 stocks, each decile holds ≈ 100–130 names.

**Why deciles, not quintiles:**
1. **The future book holds ≈ 12 names,** so the top decile is the relevant tail.
2. **For S2, quintiles would be identical to S1's.** The sequential sort only reorders stocks *within* momentum quintiles. Deciles split each momentum quintile into its smoother and less smooth halves: the paper's continuous winners vs the rest.

## 17. Top-minus-bottom metric

```
Spread = mean over dates of (D10 − D1) on the demeaned 3-month response, × 4 (annualised)
```

- Reported with its HAC t-statistic (diagnostic). It is the classic long-short measure.
- For a **long-only** decision the gated economic figure is the **top-decile excess** (§34).
- The spread enters the rule only through its sign (P1).

## 18. Rank-IC methodology

- **IC_t = Spearman correlation** between signal and demeaned response over the date's common sample: the Pearson correlation of average ranks.
- **Why Spearman:**
  1. Robust to fat-tailed returns and outlier stocks: one bankruptcy or buy-out cannot dominate.
  2. Scale-free across dates, so calm and volatile months count equally.
  3. Uses the whole cross-section, not only the extremes, so it is itself a monotonicity measure.
  4. Equivalent to a Fama-MacBeth slope on ranks.
  5. The industry-standard information coefficient (Grinold-Kahn).
- **Rejected alternatives:**
  - Pearson on raw returns (outlier-driven).
  - Raw-signal regressions (scale-dependent; S2 is a sort, not a number).

## 19. Monotonicity test

**Pre-registered rule (P2):**
- **ρ_mono = Spearman(decile index 1..10, the time-series mean demeaned return of each decile) ≥ 0.70**; and
- the **top half (D6–D10) beats the bottom half (D1–D5)**.

**Why:**
- With 10 points, ρ ≥ 0.70 corresponds to a one-sided p ≈ 0.01 under a random ordering. It allows a few small adjacent inversions, which noise will produce.
- It rejects a pattern carried by one extreme bucket. A signal whose only virtue is D10 has ρ_mono near 0.
- The half-gap blocks a U-shape.

**Considered and not adopted:** the Patton-Timmermann (2010) monotonic-relation test. It is more formal, but bootstrap-based and harder to explain. The IC already measures whole-distribution monotonicity statistically.

## 20. Sector treatment: raw primary, sector-neutral diagnostic

- **Primary: raw cross-sectional ranking.**
  - The future portfolio would buy the top-ranked stocks without sector constraints.
  - The objective is wealth.
  - Both stock-specific and industry-driven momentum are returns the book would earn.
- **Diagnostic: sector-neutral IC.**
  - Spearman within Fama-French 12 sectors, averaged by count over sectors with ≥ 20 stocks.
  - Sectors come from **point-in-time SEC SIC codes** (`qr_industry`, data v1). Vendor sector fields are current-status and unsafe (D107).
  - Stocks without an SEC SIC form an "unclassified" group.
- **Interpretation, fixed now:**
  - If the raw IC passes and the sector-neutral IC is near zero, the signal mostly picks *sectors*, not stocks.
  - This is still usable, but reported as **sector allocation** (Moskowitz-Grinblatt 1999).
  - The portfolio stage would then need a sector-concentration safeguard.
- No result can switch the primary test to the sector-neutral one.

## 21. Market-cap treatment: diagnostic

**Reported (never gated):**
- the IC within the larger and the smaller half by point-in-time market cap (median per date);
- each signal's mean correlation with log market cap.

**Why diagnostic and not primary:**
- The universe is already ≥ $2B, which removes the microcap-driven evidence P4-CP2 warned about.
- A size-neutral primary test would add a modelling choice (residualisation) with its own degrees of freedom.

**Fixed interpretation:** if the result comes almost entirely from the smaller half, the portfolio stage must check that its edge survives the $2–5B segment's costs and capacity at $100K.

---

## 22. Statistical-inference framework

**Fama-MacBeth-style, studentised, null-calibrated:**
1. **Per date:** one cross-sectional statistic per signal (rank IC; incremental partial IC). Cross-sectional dependence among stocks on the same date is absorbed into this **one number**: a market or sector shock moves the whole date's IC, which becomes one observation, not 1,000.
2. **Across dates:** the time-series mean, with a **Newey-West (Bartlett) HAC standard error, fixed lag 6**. This covers the 2-month overlap of 3-month returns plus signal persistence. t = mean / SE.
3. **Calibration:**
   - The t-statistics are compared with the critical value c from the **tethered null** (§29).
   - The null preserves overlap, persistence and cross-sectional structure. It corrects the small-sample error of HAC with an effective sample of ≈ 40: the naive test over-rejects about 3× (§24).
   - Studentised statistics are permuted, not raw means: a signal with factor tilts has a more volatile IC than a random ranking, and studentisation keeps the comparison fair (Chung-Romano 2013).
4. **Rejected as primary:**
   - stock-level pooled OLS or naive standard errors: they treat about 100,000 stock-months as independent;
   - double-clustered (stock and month) errors: unreliable with ≈ 90 months and overlapping horizons, and redundant given the date-level time series;
   - a block bootstrap: another tuning choice (block length) on the same ≈ 40 effective observations; the tethered null already preserves dependence.

## 23. Overlapping returns

- The 3-month returns of consecutive monthly decisions share 2 months. So consecutive ICs are correlated, by about 0.6 even with no edge (synthetic ACF below).
- **Treatment:**
  - (i) HAC lag 6 (≥ 2 × overlap);
  - (ii) the null is computed on exactly the same overlapping structure, so c already includes any remaining distortion;
  - (iii) a 1-month diagnostic without overlap.
- Non-overlapping 3-month sampling (every third month) was rejected. It discards two-thirds of the information for no gain in validity.

## 24. Effective sample size

**Naive count:** ≈ 92 dates × ≈ 1,150 stocks ≈ **106,000 stock-months.** That is the wrong number.

**Synthetic panel** (`P4_xs_power.json`; N = 1,100, 12 sectors, 4 style factors, signal persistence 0.90 a month), no-edge null:

| Quantity (no-edge null, 1,000 worlds per scenario) | Value |
|---|---|
| Autocorrelation of the monthly 3-month IC | lag 1 ≈ 0.62, lag 2 ≈ 0.28, then ≈ 0 |
| Variance inflation (Bartlett, 12 lags) | ≈ 2.3 |
| **Effective independent observations** | **≈ 40** (of 92 dates) |
| Naive normal test at 1% (t > 2.33) with NW lag 6 | rejects in **2.8–3.2%** of no-edge worlds (≈ 3× too often) |
| Null t-statistic dispersion (should be 1.0) | 1.15–1.23 |
| Null 1% critical value, single statistic | 2.8–3.1 |
| **Null 1% critical value, max of the 5 statistics (c)** | **3.55–3.85** |

The naive HAC t over-rejects with only about 40 effective observations. **This is why c is taken from the null, not from the normal table.**

**What this means:**
- The cross-section reduces each month to **one** IC observation.
- Overlap and persistence reduce the 92 monthly ICs to **≈ 40 effectively independent observations**: roughly one every 2–3 months.
- **Cross-sectional breadth cannot remove the month-to-month variation of the signal's payoff.** That variation (σ_IC) comes from the signal's exposure to common factors (sectors, styles) and is the dominant noise.
- With no factor alignment, σ_IC would be the breadth floor of ≈ 1/√N ≈ 0.029 (synthetic). Real price signals sit well above it.

**The unknown σ_IC.**
- The real σ_IC is unknown until the data is seen.
- Power is therefore given for three pre-declared scenarios: σ_IC (3-month, no edge) = 0.06 / 0.10 / 0.15.
- Momentum's payoff is notoriously volatile, so **0.10–0.15 is the realistic range for S1**.
- The incremental statistic is less factor-exposed, so its noise is lower (its detectable sizes are in §§25–26).

## 25. 50% power and 26. 80% power

**Synthetic, family-wise α = 1% (c = the null 99th percentile of the max of 5 statistics).** The minimum true effects detectable with 50% / 80% probability are below. "Top-decile excess" is the annualised demeaned excess of the top decile; "spread" is D10 − D1 annualised.

| Scenario: σ_IC (3-month, no edge) | c (1%) | 50% power: rank IC | 50%: top-decile excess / yr | 50%: D10 − D1 / yr | 80% power: rank IC | 80%: top-decile excess / yr | 80%: D10 − D1 / yr |
|---|---|---|---|---|---|---|---|
| Low (0.06) | 3.57 | 0.034 | **3.9%** | 7.9% | 0.046 | 5.2% | 10.4% |
| Mid (0.10) | 3.85 | 0.061 | **7.0%** | 14.1% | 0.082 | 9.5% | 18.9% |
| High (0.15) | 3.55 | 0.086 | **10.1%** | 20.2% | 0.115 | 13.4% | 26.8% |

**Incremental test (S2's smoothness beyond momentum).** Minimum within-quintile partial IC detectable (≈ the return gap between the smoother and the rougher half of a momentum quintile, annualised; approximate conversion):

| Scenario | 50% power | 80% power |
|---|---|---|
| Low | 0.022 (≈ 2.2% a year) | 0.030 (≈ 3.0%) |
| Mid | 0.033 (≈ 3.3% a year) | 0.046 (≈ 4.6%) |
| High | 0.045 (≈ 4.6% a year) | 0.060 (≈ 6.1%) |

**Power at small edges** (S1, mid scenario):
- a true top-decile excess of ≈ 1.9% a year is detected in **1%** of samples;
- ≈ 3.8% a year in **7%**;
- ≈ 5.7% a year in **27%**.

In the low scenario, ≈ 2% a year → 6% and ≈ 4% → 53%.

**Reading the table:**
- In the realistic mid scenario, only a top-decile edge of **≈ 7% a year** (rank IC ≈ 0.06) has an even chance of being confirmed, and ≈ 9.5% a year for 80%.
- **A realistic 1–3% a year edge is essentially undetectable** (power ≤ 7% in every scenario except "low", where ≈ 4% a year reaches about 50%).
- **The incremental test is relatively better powered**: its statistic is less factor-exposed. It can detect a smooth-vs-rough gap of ≈ 2–5% a year within momentum quintiles.
- **The cost of the history adjustment:** c (max of 5 at 1%) is ≈ 3.6–3.9, against ≈ 2.7 for the same family at 5%. That roughly 30–40% higher bar is the price of the four prior looks.

## 27. Year and subperiod stability

**Gated (P4):**
- the mean IC is > 0 in **both** pre-declared subperiods (2010–2013: 47 dates; 2014–2017: 45);
- **and** no two-year block (2010–11, 2012–13, 2014–15, 2016–17) contributes more than 50% of the total IC sum. This is the Amendment 3 R3 logic; H017 failed exactly this test.

**Reported, not gated:**
- the year table 2010–2017: mean IC, t, top-decile excess, sign;
- concentration, regime dependence, sign reversals.

**Not required:**
- Every year positive. With a realistic IC, 1–3 negative years out of 8 are expected.
- No other subperiods may be added after results.

## 28. Incremental value vs Plain Momentum

**One method for both candidates: the within-momentum-quintile partial rank IC.**

- **Definition:** on each date, split the cross-section into five S1 (momentum) quintiles. Within each quintile, compute the **partial Spearman correlation between the candidate's own component and the demeaned return, controlling for S1**:
  - NUD for S2;
  - the trend score for S3.
- The date's statistic is the equal-weighted mean over the five quintiles. Its time series gets the same HAC t, t_inc.
- **What it answers:** "Among stocks with similar momentum, does smoothness (or trend score) still predict relative returns?"
  - The quintile split removes momentum's level.
  - The partial correlation removes the remaining within-quintile momentum variation.
- **Fit with S2:** it is exactly the second stage of the paper's sequential sort.
- **Diagnostic:** the per-quintile values, especially Q5 (the long-only-relevant winners).
- **Considered and not adopted:**
  - a two-regressor Fama-MacBeth regression on ranks: equivalent in spirit, but less transparent;
  - 5 × 5 double-sorted portfolio spreads: coarser and noisier with ≈ 45 stocks per cell;
  - a residualised signal: a linear model of S3 on S1, more modelling.

**Requirement (P6):** t_inc > c, the same family-wise critical value as every other statistic.

## 29. Null design

**Identity-tethered within-date permutation** (`qr_xs.Tether`, tested):

**How it works:**
- In null world r, each stock receives the **joint** signal vector (S1, NUD, S2, S3) of a randomly chosen partner stock.
- It keeps that partner for as long as both remain in the common sample.
- Stocks that lose their partner or newly enter are re-matched at random among that date's unmatched stocks.

**What it preserves:**
- On every date the null signals are an exact permutation of the real signals over the same stocks.
- So it keeps the real returns, dates, universe composition and size, cross-sectional dependence, return overlap, and the signals' joint distribution.
- It also keeps the **persistence**: a stock's null signal history is another stock's real history.

**What it breaks:** only the link between a stock's signals and its **own** future returns.

**The whole procedure runs on every null world:** ICs, deciles, incremental statistics, HAC t's, monotonicity, stability and the full promotion rule.

**Why tethered rather than a fresh permutation every month:**
- A fresh monthly permutation destroys signal persistence. Its null ICs are nearly uncorrelated across dates, unlike the real ICs.
- The HAC t is then calibrated on the wrong dependence structure.
- P3 used a block null as a diagnostic for the same reason.

**Rejected:**
- Circular time shifts: they misalign universe membership (P3 spec).
- Return-label shuffles: they break corporate-action accounting.
- A Freedman-Lane residual permutation for the incremental test (a second null process). Its exactness gain is small because the statistics are studentised. One process keeps the procedure simple.

## 30. Number of null repetitions

- **R = 5,000 worlds** (seeds 1–5,000), in five runs of 1,000.
- Worlds are seed-deterministic and independent of the batch (the P3 practice).
- **c = the 50th largest family statistic** (α = 1%).
- **Monte-Carlo precision:** the null tail probability at c has a standard error of ≈ 0.14 percentage points (binomial, p = 1%, R = 5,000), so its 95% interval is ≈ 0.75–1.3%.

## 31. Multiple-testing method

**One framework: a permutation max-statistic at a history-adjusted family-wise level.**
- **The family is five studentised statistics:** t(IC) of S1, S2, S3, and t_inc of S2 and S3.
- **F** = their maximum in each null world. **c** = the 99th percentile of F.
- Every gated statistic must exceed the same c. This controls the probability that *any* of the five exceeds c by chance at 1%.
- It automatically accounts for the strong correlation between the statistics (S2 ≈ S1 between quintiles), which a Bonferroni split would over-penalise.
- **Check:** the share of null worlds in which the **complete** promotion rule promotes S2 or S3 is reported. It is ≤ 1% by construction.
- **Not added:** separate FDR, Holm, DSR or PBO layers. One clear rule is better than ten overlapping ones (owner instruction).

## 32. How earlier momentum attempts are accounted for

**Prior looks at the past-return ranking family on the same 2010–2017 data:**

| Look | What | Size |
|---|---|---|
| H002 (C01) | 12-1 momentum, monthly top-15, plus a market filter | 4 candidates |
| H003 (C01) | 52-week-high proximity (high overlap with momentum, P4-CP2 §22) | 3 candidates |
| H008 (C02) | Residual relative strength | 3 candidates |
| H018 (Phase 3) | 495 momentum-primary configurations (M1–M3), momentum confirmations, and 297 trend-primary configurations (relevant to S3) | One full-search look with its own null |

Related but not counted (different primary information): H004, H006 and H014 (pullback / breakout timing).

**Effect on the significance threshold:**
- **α = 0.05 / (1 + 4) = 1%** family-wise, instead of 5%.
- Each prior *look* counts once: each had its own internal screen or null.
- The new look gets one Bonferroni share. This is simple and conservative, and it is fixed now.

**Effect on interpretation:**
- 2010–2017 is **not fresh data** for this family. A pass is evidence conditional on a family examined repeatedly. The one-shot 2018–2021 check of a later frozen portfolio remains the first truly out-of-sample test.
- **Phase 3's per-family results are not inspected** and play no role in choosing these signals. P4-CP2 chose them from the literature.

**Effect on novelty:**
- S1 = replication of a known effect.
- S2 and S3 = new *constructions* of an already tested information family.
- **Only the incremental test (P6) can establish anything new.**

---

## 33. Promotion criteria (all must hold)

| Code | Condition |
|---|---|
| **P1 Economic** | Top-decile annualised demeaned excess ≥ **3.0% a year**, **and** D10 − D1 > 0 |
| **P2 Monotonic** | Spearman(decile index, mean decile excess) ≥ **0.70**, **and** mean(D6..D10) > mean(D1..D5) |
| **P3 Statistical** | t(rank IC) > c |
| **P4 Stable** | Mean IC > 0 in both subperiods, **and** no two-year block > 50% of the total IC sum |
| **P5 Exceptional** | Through c (tethered-null, max-statistic, α = 1%); full-rule null rate reported |
| **P6 Incremental** (S2, S3) | t_inc > c |

**Outcomes:**
- **candidate:** S2 and / or S3 pass. If both pass, the one with the larger t_inc is selected.
- **replication_only:** only S1 passes.
- **none:** nothing passes.

The rule is implemented in `qr_xs.promotion` and tested criterion by criterion.

## 34. Economic-significance requirement

**Why 3% a year top-decile excess:** a 12-stock long-only book drawn from the top decile loses part of the decile's edge to:

| Drag | Size | Source |
|---|---|---|
| Transaction costs | ≈ 1–1.5% a year | Monthly name turnover of ≈ 25–35% for 12-1 rankings; $7 + slippage on ≈ $8K positions ≈ 0.4% a round trip (P4-CP2 §20 scale) |
| Cash drag | ≈ 1–1.5% a year | D051 sizing keeps ≈ 10% cash; 2010–2017 equity returns ≈ 13% a year |
| Incomplete capture | — | 12 names are a noisy subset of ≈ 110; holding rules lag the ranking |

- 3% is the smallest gross edge that leaves anything after the drags.
- In synthetic terms it corresponds to a 3-month rank IC of roughly 0.026 (synthetic conversion: a 3-month IC of 0.01 ≈ 1.15% a year of top-decile excess).
- **A signal can be statistically detectable and still fail P1.** That is intended: a detectable 0.5% a year edge is economically useless here.

**Reported alongside:** the top decile vs SPY, the spread, and the IC.

## 35. Turnover / implementability diagnostic

- **Computed from signals only** (no portfolio):
  - month-to-month rank autocorrelation;
  - top-decile and top-quintile **retention** (the share of names still in the bucket next month; 1 − retention ≈ the name turnover a top-bucket book would face).
- **Translated** into an indicative cost drag at $7 + slippage per order. Not subtracted from any statistic.
- **Expectations:**
  - S1 and S2: ≈ 0.9 rank autocorrelation (11 of 12 months shared).
  - S3: lower (the 50-day component moves faster).
  - A signal with top-decile retention below ≈ 50% would be flagged as expensive to implement.

## 36. The pre-registration file

**`research/phase4/P4_xs_spec.md`** contains the frozen items:
- the three formulas and their data rules;
- monthly ranking;
- the 3-month primary horizon and the two diagnostics;
- deciles, the spread, the rank IC and monotonicity;
- the demeaned response;
- raw-primary sector treatment and diagnostic size treatment;
- NW lag 6;
- the tethered null with R = 5,000;
- the max-statistic at α = 1%;
- the prior-look accounting;
- the promotion rule and the consequences.

**Freezing sequence after approval** (P3 precedent):
1. Spec SHA-256 and `qr_xs` constants pinned in `qresearch.p4xs`, tested.
2. Canary.
3. The null runs.
4. c and the null table committed and pinned.
5. The real run.

## 37. Implementation and runtime

**Host X985** (non-trading; derived from X984, sharing the harness, universe, warm-up, Holdout lock and output channel):
1. **Daily:** maintain 280-bar adjusted windows (X984 code). Apply corporate actions to a per-stock total-return index (X984 accounting).
2. **At each month-end close:** take the common sample; compute S1, NUD, S2 and S3 (`qr_xs` formulas); store the signal arrays and the next-open entry reference.
3. **As time passes:** complete each decision's forward return at the close of month m+3 (no look-ahead; statistics are computed only at the end).
4. **At the end:** run `qr_xs.date_stats` / `summarise` for the real world (real run only) and for the null worlds (`Tether`), and publish derived statistics only. Raw prices and per-stock values never leave QuantConnect.

**Runtime:**
- **Measured locally:** `date_stats` ≈ 5.4 ms per date with 1,250 stocks, so ≈ 0.5 s a world (92 dates), or ≈ 8 min per 1,000 worlds.
- **The data pass** is as in Phase 3: ≈ 4 min of bars / history / feature time (E018-07 clock), plus harness overhead.
- **Estimate:** ≈ 20–30 min per 1,000-world run on the B2-8 node, and ≈ 15 min for the canary and the real run.
- **Memory:** ≈ 92 dates × ≈ 1,300 stocks × a few arrays, i.e. a few MB. Well below P3's 4.4 GB.
- **Output:** ≈ 1,000 lines of ≈ 300 bytes per null run, well inside the log budget.
- **Engineering:** ≈ 1–2 working days (host, corporate-action return index, canaries, spec pinning).

## 38. QuantConnect cost

- **$0 beyond the existing $24 / month** (Researcher seat + one B2-8 node).
- Total node time ≈ 2.5–3.5 h across 7 runs.
- No data purchase.

## 39. Runs that would occur after approval (each gated by `owner_approval_required`)

| Run | Content | Publishes |
|---|---|---|
| **E985-01** (X985) | Plumbing canary. (a) Two seeded random persistent placebo signals: IC ≈ 0. (b) A planted signal = forward return + noise with a known IC: recovered. (c) Universe counts vs the harness. (d) Every horizon ends ≤ 2017-12-29. (e) Look-ahead check (signals use only bars ≤ the decision close). (f) Runtime / memory / output | Canary statistics only; **no real-signal statistic** |
| **E020-01..05** (S020 = byte copy of X985) | Null worlds 1–5,000 (1,000 per run); real signals tethered-permuted | Null F and per-world statistics; **never** real-world statistics |
| — | Commit and pin c + the null table | — |
| **E020-06** | Real evaluation (primary + diagnostics) | Real statistics |
| — | **P4-CP4 report; STOP** | — |

No re-runs with changed rules. No 2018–2021 data. No Holdout.

## 40. Go / No-Go recommendation

**Recommendation: GO, conditionally, for the signal validation only.** Conditions:
- (a) the two formulas are confirmed against the full papers;
- (b) the owner accepts the power profile below.

**Reasons for GO:**
- It is the cheapest informative test left in the technical family. It needs $0, about a day or two of engineering, and about 3 node-hours.
- It answers a question every earlier phase left open: is there any cross-sectional information at all, as distinct from "can a 12-stock book capture it?"
- It uses frozen formulas, one null and one threshold, so it creates no new search.

**Honest expectation:**
- With realistic factor-driven IC noise, the test detects with ≥ 50% probability only edges equivalent to a top-decile excess of about 7% a year (mid scenario).
- A true 1–3% a year edge will most likely **not** be confirmed.
- A "none" outcome would therefore mean "no large edge", not "no edge". It would still justify stopping technical stock selection in this universe (pre-registered consequence §9 of the spec).

**No-Go would be reasonable if** the owner considers that a test unable to confirm a 1–3% edge is not worth running. The alternative is to stop now.

**Owner choices needed before freezing:**
1. **GO or NO-GO** for the signal validation (implementation, canary E985-01, null E020-01..05, real E020-06), each run gated by `owner_approval_required`.
2. **Primary horizon:**
   - **3 months** (recommended: economic alignment; ≈ 10–15% power cost); or
   - **1 month** (more synthetic power, no overlap) with 3 months as a diagnostic.
3. **Formula confirmation:** whether the two definitions must first be checked against the full papers (recommended; the PDFs are blocked here), or accepted as quoted in the search records.
4. **The history-adjusted level α = 1%** (four prior looks), or a different accounting.
5. **Identifiers:**
   - H019 = this procedure;
   - X985 = canary host;
   - S020 = the research host (S019 stays unused, as reserved and never built in Phase 3);
   - experiments E985-01, E020-01..06.

---

## Answers A–K

**A. Can cross-sectional analysis materially improve our ability to detect a realistic 1–3% stock-selection edge?**
**Only partly.**
- Cross-sectional analysis removes idiosyncratic noise and the portfolio choices, and it gives a clean, cheap, null-calibrated test.
- **But the binding noise is the month-to-month variation of the signal's payoff, which breadth cannot diversify.** With about 40 effective observations and a history-adjusted 1% family-wise bar:
  - the 50%-power detectable top-decile excess is ≈ 4% a year if the signal's payoff is calm, ≈ 7% a year in the realistic mid case, and ≈ 10% a year if it is as volatile as momentum often is;
  - P4-CP1's portfolio-level figure was ≈ 6–8% a year for its search gates and ≈ 12% for the full chain.
- **A realistic 1–3% edge stays essentially undetectable** (power ≤ 7% in the mid scenario).
- **The real gain is elsewhere:**
  1. the incremental test can detect a moderately sized refinement (≈ 3% a year smooth-vs-rough gap, mid case);
  2. a "none" result cleanly separates "no large edge in the information itself" from "a 12-stock book could not show it";
  3. the realised IC volatility is measured, so the detectable edge is known after the run.

**B. What is the statistically strongest way to test these signals without pretending stock-months are independent?**
- One cross-sectional statistic (rank IC) per date.
- The time-series mean with a Newey-West HAC t (lag 6).
- Calibrated against an identity-tethered within-date permutation null that runs the whole procedure.
- A max-statistic over the five tests at α = 1%.
- The effective sample is ≈ 40 independent observations, not ≈ 100,000 (§§22–24, §29).

**C. Which published definition should we use for Smooth Momentum?**
- Da, Gurun & Warachka (2014, RFS) information discreteness, via its unsigned form NUD = (#up − #down) / #days.
- Window: the 12-1 window of daily returns.
- Applied as the paper's sequential sort: momentum quintile first, then NUD (§7).

**D. Which published definition should we use for Combined Trend Score?**
- Han, Zhou & Zhu (2016, JFE) price-normalised moving averages, restricted to the paper's intermediate lags 50 / 100 / 200 and equally weighted:
  - S3 = mean ln(P / SMA_L).
- No fitted coefficients, no short or long-reversal lags (§8).

**E. Which future-return horizon should be primary?**
- 3 months (next open → the close of the third month-end), sampled monthly, NW lag 6.
- 1 and 6 months are diagnostics only (§§13–14).
- Note: 1 month has somewhat more synthetic power (0.92 vs 0.82). 3 months is recommended on economic grounds, and the alternative is an owner choice.

**F. Monthly or weekly ranking?**
- **Monthly.** Weekly adds dependent rather than independent observations, departs from all three source papers, and adds turnover and HAC fragility.
- The synthetic power is identical (0.81 vs 0.81 at the same edge) with a quarter of the dates (§12).

**G. Sector-neutral primary or diagnostic?**
- **Diagnostic.** The primary test is the raw cross-section, because the future book is unconstrained and the objective is wealth.
- The sector-neutral IC tells us whether the edge is stock selection or sector allocation (§20).

**H. How do Signals 2 and 3 prove they add information beyond Plain Momentum?**
- The within-momentum-quintile partial rank IC (controlling for momentum) must have t_inc > c at the same family-wise 1% level (§28).
- Their standalone tests must also pass. Passing standalone alone is never enough: S2 inherits most of S1's between-quintile information by construction.

**I. How should previous momentum experiments affect the significance threshold?**
- Four prior looks at the family on 2010–2017 (H002, H003, H008, H018), so α = 0.05 / 5 = 1% family-wise.
- Interpretation: conditional evidence, not fresh data.
- Novelty: only the incremental test can show anything new (§32).

**J. What minimum effect size would make a signal worth turning into a real portfolio?**
- A top-decile demeaned excess of **≥ 3% a year** (≈ a 3-month rank IC of 0.026 (synthetic conversion: a 3-month IC of 0.01 ≈ 1.15% a year of top-decile excess)), monotonic and stable.
- For S2 / S3, it must also add information beyond momentum.
- Below that, costs, cash drag and concentration would likely consume the edge (§34).

**K. If one signal passes, what does the next stage look like?**
- **One** pre-registered portfolio built around the selected signal:
  - monthly ranking;
  - N = 12 (P4-CP1 mechanics);
  - weekly trend-state management only if pre-registered;
  - next-open execution.
- Judged against random twins and SPY under Amendment 3 on 2010–2017. Then the one-shot 2018–2021 check of the frozen book. The Holdout only with CP5 approval.
- **Open methodological question for that stage (an owner decision then, not now):** a 12-stock book cannot re-prove a small edge at portfolio level (P4-CP1 power). Its gate should probably be *implementation consistency* (the book captures a sensible share of the validated signal's edge after costs) rather than a second independent significance test.
