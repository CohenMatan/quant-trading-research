# PBO with three variations: what it measures, and the definition proposed for C02

| Field | Value |
|---|---|
| Written | 2026-09-29, at the owner's request, **before any C02 result exists** (no C02 strategy backtest has run) |
| Evidence | Monte Carlo on synthetic returns only: `research/cycles/C02_pbo_simulation.py` → `C02_pbo_simulation.json` (seed 20260929, 200 repetitions per scenario). The fast implementation is tested to equal the official `stats.pbo_cscv` (`tests/test_pbo_calibration.py`). |
| Threshold | **PBO ≤ 0.30 is kept unchanged.** Nothing here uses C01 or H005 performance. |
| Status | **APPROVED and FROZEN (D073, D075, owner 2026-09-29), before any C02 result.** |

## 1. How PBO is computed today

The method is combinatorially symmetric cross-validation (CSCV), defined at CP2 and implemented in `stats.pbo_cscv`.

1. Take the in-sample daily returns of the variations being compared: a matrix of 2,012 days × N variations.
2. Cut the days into 16 consecutive blocks of about half a year each.
3. For each of the 12,870 ways to pick 8 blocks as a pseudo in-sample half, the other 8 are the pseudo out-of-sample half:
   - find the variation with the best Sharpe ratio in the pseudo in-sample half;
   - see where that same variation ranks in the pseudo out-of-sample half.
4. **PBO** = the share of splits in which the in-sample winner lands **at or below the median** out of sample.

The approved rule is a hard Validation gate, PBO ≤ 0.30, computed per hypothesis over its 3 variations (C02 plan §6).

## 2. What happens with only three variations

With N = 3, the in-sample winner can only finish 1st, 2nd or 3rd out of sample.

- 3rd is below the median, so it counts as overfit.
- 2nd **is** the median, so it also counts as overfit.
- Only 1st counts as not overfit.

So with three variations, PBO reduces to one simple quantity: **PBO = the share of splits in which the in-sample best variation is *not* also the out-of-sample best.**

That has three consequences.

**(a) It measures dominance among siblings, not overfitting.** The statistic depends only on how the three variations compare *with each other*, never on whether any of them has a real edge.

- PBO uses only the ranks of the variations against each other. Adding the same edge to all three (with equal volatility) shifts all their Sharpe ratios by nearly the same amount and leaves the ranks essentially unchanged. The simulation's common base Sharpe of 0.5 could equally be 0 or 1.
- A hypothesis whose three variations are *all* genuinely good, and similar, which is what robustness looks like, gets a PBO of about 2/3.

**(b) Its no-difference value is 2/3, and it is very unstable.** If the three variations are equally good, the in-sample winner is the out-of-sample winner a third of the time.

| Three variations, all equally good (correlation between variations) | Mean PBO | 5%–95% range | Share of cases passing PBO ≤ 0.30 |
|---|---|---|---|
| 0.5 | 0.66 | 0.18 – 0.99 | 14% |
| 0.8 | 0.66 | 0.15 – 0.97 | 13% |
| 0.95 | 0.67 | 0.17 – 0.99 | 14% |

The 12,870 splits are strongly dependent (they reuse the same 16 blocks), so the statistic has far less resolution than its many decimals suggest. Pure chance moves it across almost its whole range.

**(c) What is realistically attainable depends mainly on how correlated the variations are, and on the Sharpe *gap* between them.** Share of cases passing PBO ≤ 0.30 when one variation's true Sharpe is higher than the other two by ΔSR (annualised):

| Correlation between variations | ΔSR = 0 | 0.25 | 0.5 | 1.0 |
|---|---|---|---|---|
| 0.5 | 14% | 14% | 47% | 94% |
| 0.8 | 13% | 33% | 76% | 100% |
| 0.95 | 14% | 77% | 100% | 100% |

- To pass reliably, one variation must beat its siblings by a Sharpe gap of 0.5 to 1.0. That is larger than the whole edge most published anomalies deliver.
- Whether it passes depends on something unrelated to overfitting: how correlated the variations happen to be.
- It rewards hypotheses where one variation happens to dominate. It punishes hypotheses whose variations *agree*, although agreement is evidence that the result does not hinge on one design choice. C02's variations each change one substantive dimension (e.g. H009 hold 20 vs 40 days), and agreement between them is exactly the robustness we hope to see.

**Conclusion.** With three variations, "PBO ≤ 0.30" is **not a statistically meaningful hard gate for overfitting**.

- Its pass/fail outcome does not depend on whether the strategy has an edge.
- Its null value (2/3) is far from the threshold for reasons unrelated to overfitting.
- Its sampling noise spans most of the scale.

This is a property of the statistic with N = 3, not of any particular result.

## 3. Proposed definition for C02 (threshold unchanged)

PBO was designed (Bailey, Borwein, López de Prado & Zhu, 2014/2017) to measure the overfitting of a **selection process**: choose the best of N candidates in sample, and ask how often that choice turns out below median out of sample. In C02 the selection that matters is **choosing the best candidate among all 18 pre-declared variations of the cycle**. That is also what the Deflated Sharpe Ratio's N counts (D069).

**Proposal (D073):**

1. **Hard Validation gate: cycle-level PBO ≤ 0.30.**
   - Computed exactly as today (CSCV, 16 blocks, "at or below the out-of-sample median counts as overfit").
   - Computed on the in-sample daily returns of **all 18 C02 selection candidates**, whether or not they pass the screen, all run on the same harness version.
   - It applies to any C02 candidate proposed for Validation.
2. **Per-hypothesis PBO over the 3 variations: reported, not a gate.** It is labelled "variation dominance": how often the in-sample best variation of that hypothesis is also its out-of-sample best. It is reported next to the variations' return correlations.
3. **Cumulative PBO over C01 + C02 candidates: reported, not a gate.** It is not a gate because C01's runs used earlier harness versions (before D057/D063/D072), and CSCV needs every column produced under the same conditions. The DSR's cumulative trial count has no such requirement, because it only uses the number of candidates and the spread of their Sharpe ratios.

**Why the cycle-level gate is meaningful** (simulation: 6 hypotheses × 3 variations; correlation 0.8 within a hypothesis, 0.5 across hypotheses):

| True situation in the cycle | Mean PBO | 5%–95% | Share passing ≤ 0.30 |
|---|---|---|---|
| No candidate better than any other (null) | 0.50 | 0.17 – 0.83 | 17% |
| One hypothesis better by 0.25 Sharpe | 0.45 | 0.11 – 0.82 | 30% |
| One hypothesis better by 0.5 Sharpe | 0.31 | 0.03 – 0.73 | 54% |
| One hypothesis better by 1.0 Sharpe | 0.04 | 0.00 – 0.16 | 99% |
| True Sharpe spread 0.0 … 1.0 across hypotheses | 0.18 | 0.01 – 0.51 | 81% |

- The null value is the textbook 0.50. With 18 columns the out-of-sample rank has 18 levels, so the statistic has real resolution.
- It passes when selection was informative (the in-sample best is also good out of sample), and it fails when the winner was picked by noise.
- It is not affected by near-identical siblings: if a genuinely good hypothesis has three similar variations, whichever wins in sample still ranks near the top out of sample.
- It still lets through about 17% of pure-noise cycles. That is why it is only one gate among several: DSR ≥ 0.90 (with N = 37), the Validation period itself and the other unchanged gates.

**What does not change:** the 0.30 threshold, the CSCV method, the 16 blocks, the median rule, the DSR definition (D069), and every other gate.

**C01 is not reopened.** H005's Validation result and C01's outcome (No Production Candidate Found, D060) stand as decided. This proposal applies from C02 on, and it is recorded before any C02 number exists.

## 4. If the owner prefers to keep the per-hypothesis gate

Then it should be understood as "one variation must dominate its siblings in most splits". Two facts follow:

- a hypothesis whose three variations perform alike fails about 86% of the time, whatever its edge;
- the gate would favour hypotheses whose variations happen to be less correlated or more different.

I do not recommend this. The choice must be made before C02 runs.
