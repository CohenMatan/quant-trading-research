# H012 statistical power reassessment

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **STOP. Awaiting owner decision.** D084 is not approved and not in force. No C03 strategy backtest has run. |
| Evidence | `research/cycles/C03_h012_power_study.py` produces `C03_h012_power_study.json` (runtime 11 minutes). Seeds: master 20261001; bootstrap 20260930. Synthetic data only, plus a null test on real pre-C03 benchmark returns (EW E901-07, SPY E900-07, IS) with uninformative time-shifted signals. No H012/H013 run, no C03 result, and no Validation, Walk-Forward or Holdout data. H012's rule and parameters are unchanged: every scenario trades the approved H012 v1.0 rule and its Controls A and B. |
| Bottom line | **H012 cannot be evaluated with adequate statistical power on our data.** The limit is the size of the effect relative to 8 years of noise, not the design of D084. I recommend removing H012 from C03 as "not evaluable with the available data" and running H013 only (§6). |

**These are simulation results, not guarantees about real markets.**

## 1. Why D084 has low power

**1. The achievable effect is small.**

- H012 can only reduce exposure (no leverage, e ≤ 1). It de-risks only after volatility has already risen, and it is about 92% invested on average.
- On very long synthetic paths (400,000 days), its true Sharpe gain over Control B is small:
  - volatility clustering (GARCH), even when expected returns fall sharply as volatility rises: at most **+0.05**;
  - Moreira–Muir's own assumption (expected return unrelated to volatility): **+0.01**.
- A **moderate** gain (+0.10) needs turbulent periods that lose about 28% a year while they last. A **strong** gain (+0.20) needs about −87% a year, i.e. crash regimes of about −20% per episode.

**2. The noise is large.**

- Over 8 years, the estimated gain Sharpe(V) − Sharpe(B) has a standard deviation of **0.08–0.14**, even though V and B hold the same stocks on the same days.
- The information sits in the few volatility episodes (about 3–5 in 8 years), not in the 2,000 days.

**3. The combination of five items is not the cause.**

- D084 as proposed (M0) and "T1 + T2 only" (M2) pass in **exactly** the same simulations, in every scenario.
- Whenever T2 passes, T3, T4 and T5 also pass: 0% of T2 passes fail them, in 11 to 142 cases per scenario.

**4. The confidence level matters, but it is secondary.**

- Moving T2 from 2.5% to 5% one-sided raises power at a moderate effect only from 14% to 25%.

## 2. The contribution and overlap of T1–T5

| Item | What it measures | Independent evidence? | Contribution (8 years) |
|---|---|---|---|
| T1 (≥ 8 decisions) | The rule actually trades on volatility | No; it is a non-degeneracy check | Always passes: never binds for this rule |
| **T2** (bootstrap lower bound vs Control B) | Timing value against the exposure-matched control, allowing for dependence | **Yes. It is the only real statistical test.** | Decides every outcome |
| T3 (vs Control A, > 0.05) | Whether the book beats simply staying invested | Partly: a different question, but correlated (0.22–0.29 with T2) | Never rejects after T2 |
| T4 (leave one year out) | Whether it survives removing any one year | No: subsets of the same data | Never rejects after T2. In the "one lucky crash" scenario it did not add protection either. |
| T5 (2 of 3 thirds) | Consistency across subperiods | No: subsets of the same data | Never rejects after T2. It passes 20–38% under the no-edge scenarios on its own. |

T3–T5 are informative **descriptions**, but they are not additional evidence. As hard gates they add no protection and no power loss, only complexity.

## 3. Alternatives considered

- **M3:** T1 + T2 at a one-sided 5% level.
- **M4:** T1 + the Ledoit–Wolf (2008) test of a Sharpe-ratio difference, with a dependence-robust (HAC) standard error, at one-sided 5%.
- **Also examined:**
  - D084 with 5% (M1);
  - T2 at 5% plus T3 (M5);
  - the Moreira–Muir alpha regression against Control A. It **passes 8.3% of the time when there is no edge**, where 5% is nominal. It answers a different question (whether V extends A's risk–return trade-off), so it is not suitable as a gate.

## 4. Quantitative comparison (8-year IS, 400 simulations each unless stated)

**Scenarios with no genuine timing value.** Each figure is the share of simulations in which the method would wrongly accept H012.

| Scenario | D084 (M0) | T2 at 5% (M3) | Ledoit–Wolf (M4) | Share with lower max drawdown than A (by > 3 points) |
|---|---|---|---|---|
| Boundary null (true gain 0) | **2.8%** | **5.0%** | **5.3%** | 48% |
| Risk–return proportional (timing hurts) | 0.8% | 1.0% | 0.8% | 33% |
| Uninformative timing | 0.0% | 0.5% | 0.5% | 21% |
| Favourable bull market, no timing | 0.0% | 0.0% | 0.0% | 20% |
| One lucky crash, no timing | 2.8% | 5.5% | 3.3% | 53% |
| **Lower exposure (70%), no timing** | 0.5% | 1.3% | 1.3% | **100%** |
| Real returns, shifted signal (72 paths) | 0/72 | 1/72 | 1/72 | — |

**Genuine timing value (power).** Each figure is the share of simulations in which the method correctly accepts H012.

| Scenario (true gain over B) | D084 (M0) | M3 | M4 |
|---|---|---|---|
| Weak (+0.05) | 4% | 10% | 10% |
| Moderate (+0.11) | 14% | 25% | 27% |
| Strong (+0.20) | 36% | 47% | 56% |

**No method mistakes lower exposure for skill:** at most 1.3%. However, a naive drawdown comparison would: the 70%-exposure book has a lower drawdown than Control A in **100%** of paths. This confirms that drawdown alone must never count as evidence of timing, as H012.md already states.

**Favourable markets and lucky episodes** are accepted at no more than the nominal level.

**Sensitivity** (acceptance with no edge, and power at a moderate effect; 200 simulations each):

| Change | M0 no edge / power | M3 no edge / power | M4 no edge / power |
|---|---|---|---|
| Normal shocks | 2.5% / 14% | 4.5% / 28% | 4.5% / 27% |
| t(3) fat tails | 1.5% / 14% | 3.5% / 21% | 4.5% / 23% |
| Short volatility spells (20 days) | 1.5% / 16% | 5.0% / 25% | 4.5% / 27% |
| Long volatility spells (120 days) | 0.5% / 15% | 3.0% / 21% | 3.0% / 28% |
| Return autocorrelation, AR(1) 0.1 | 3.5% / 13% | 4.5% / 21% | 6.0% / 24% |

- Every method keeps its no-edge acceptance near or below its nominal level. The bootstrap methods (M0, M3) stay at or below it; M4 exceeds it slightly (6%) with return autocorrelation.
- Power is low everywhere.

**Sample length** (power, one-sided 5%):

| Years of data | Moderate, M3 | Moderate, M4 | Strong, M3 | Strong, M4 |
|---|---|---|---|---|
| 8 (IS) | 26% | 30% | 46% | 51% |
| 12 (IS + VAL length) | 38% | 42% | 61% | 69% |
| 25 | — | 63% | — | 93% |
| 50 | — | 88% | — | 100% |

**Years of data needed for 80% power at one-sided 5%:**

- weak: about **200**;
- moderate: about **50**;
- strong: about **14**.

At the 2.5% level: about 260, 65 and 18.

## 5. Can H012 be evaluated with our data?

**No, not with adequate power.**

- **IS is 8 years.** Validation adds 4, but it can only confirm a candidate that is already frozen, so it cannot rescue a selection decision.
- Only a **strong** effect (+0.20) would be detected with reasonable probability, and even then only about half the time in IS.
  - That strength requires crash-like volatility regimes.
  - IS 2010–2017 has no such regime (its episodes: 2010, 2011, 2015–16).
- **No earlier data can fill the gap.** Before 2010 our universe is imperfect, and D035 forbids using 1999–2009 for selection.
- **Independently of the screen, H012 is very unlikely to pass the unchanged DSR.**
  - The DSR requires an observed Sharpe of about 1.48 over IS + VAL at N = 43.
  - H012's Sharpe is roughly its basket's Sharpe plus the timing gain. For comparison, the equal-weight benchmark's IS Sharpe is 0.92.
  - A gain of +0.05 to +0.20 cannot close that gap unless the 15-stock basket alone is exceptional.

**So the problem is insufficient information, not an overly strict screen.** Choosing a looser rule would raise false acceptance without producing convincing evidence.

## 6. Options and recommendation

| Option | Consequences |
|---|---|
| **A. Retain H012 as exploratory** (no production path) | 11 committed runs, and probably ~95% inconclusive. The Sharpe gain would be estimated within about ±0.2 (95%), which cannot tell weak, zero or moderate effects apart. It still adds its 3 candidates to the DSR N. Little information for the cost. |
| **B. Defer H012** until more independent data or a better approach exists | There is no foreseeable source: the extra history needed is decades, and pre-2010 data is excluded (D035). In practice this is the same as C. |
| **C. Remove H012 from C03 and focus on H013** | Frees 11 committed and up to 15 conditional runs. It is honest: the hypothesis is recorded as **not evaluable with available data**, not as rejected or accepted. No H012 result has been seen, so this decision is not data-snooped. |

**Recommendation: C** (equivalently, B with no expected end date).

- H013 continues exactly as frozen.
- D084 is withdrawn, since no H012 screen is needed.
- **If you prefer to keep H012 as a candidate anyway,** the defensible screen is **T1 + one calibrated test** (M3 or M4), with T3–T5 reported as diagnostics. It keeps false acceptance at about 5% and gives about 25% power at a moderate effect. I would not describe that as adequate.

## 7. Decisions requiring your approval

1. **H012:** remove it from C03 (recommended), keep it as exploratory, or keep it as a candidate under M3/M4.
2. **If H012 is removed, the DSR official N.** The frozen specification expects exactly 43 (37 + 6 C03 candidates). Without H012, the registry would show 40.
   - **(a) Recommended:** keep N = 43 as a floor, i.e. N = max(registry count, 43). This is stricter and changes no frozen number.
   - **(b)** Use the honest count of 40.

   Either option needs a one-line amendment to the frozen specification. The difference in the DSR hurdle is small: an observed Sharpe of about 1.48 at N = 43 versus about 1.47 at N = 40.
3. **Budget, if H012 is removed:** the committed C03 runs fall from 32 to 21:
   - H013: 9 selection + 6 sizing;
   - 6 random-null runs.

   Conditional runs remain as pre-declared for H013.
4. **After approval** I would implement the chosen option with tests, re-verify the frozen methodology and integrity checks, and then (per your conditional authorisation) start the committed C03 runs without another checkpoint, stopping if anything fails.

## 8. Limitations of this study

- **The market models are stylised.** In particular, the "moderate" and "strong" effects need turbulent periods with strongly negative returns. Real markets could contain effects the models miss, in either direction.
- **The calibration uses H012 v1.0.** v1.1 (RV63) reacts more slowly and v1.2 (weekly) faster. Neither changes the core limits: capped exposure and few episodes.
- **The number of simulations** limits precision to about ±2 percentage points on the rates shown.
- **The simulation bootstrap uses 2,000 resamples**, where D084 specifies 10,000. This makes the quantiles slightly noisier, but not biased.
- **The semi-real null has only 72 overlapping, non-independent paths.**
