# Owner message 2026-10-18: P13-CP6 — H028 Repaired Null: Synthetic Validation Only

Decision id: **D239**. The owner's message is quoted verbatim below (as received). Recorded before any P13-CP6 code or synthetic result existed.

---

# P13-CP6 — H028 Repaired Null: Synthetic Validation Only

## Owner Approval — Limited Scope

I approve the development and synthetic validation of a repaired statistical null for H028.

**This approval is strictly limited to synthetic data, infrastructure required for synthetic testing, and methodological validation.**

You may implement code, run offline synthetic experiments, write tests, document findings, and create a checkpoint and pull request.

You are NOT authorized to:

- Rerun H028 on real market data.
- Run any new historical stock-selection backtest.
- Export H028's real holdings through QuantConnect.
- Calculate new H028 statistics on real returns.
- Run repaired null worlds against real 2011–2021 returns.
- Open or inspect the sealed 2022–2026 Holdout.
- Modify H028's strategy or original gates.
- Change the official H028 REJECTED status.
- Start H031 or any new investment hypothesis.
- Develop or backtest an offensive strategy.
- Purchase additional datasets.
- Close Phase 13 or H029/H030 without separate approval.

**STOP after completing the synthetic-validation checkpoint.**

---

# 1. Verify the Current State

Begin with repository and session checks.

Verify:

- Current main branch and working-tree status.
- D238 and P13-CP5.
- H028's frozen specification.
- H028's original E030-05 result.
- P14-CP4 and P14-CP6a null methodology findings.
- Existing synthetic panel generators and testing infrastructure.
- Latest experiment and decision IDs.

Preserve the historical record.

Do not interpret the repository's current state as authorization to run a real experiment.

## Existing H028 result

The previously recorded development result is approximately:

| Metric | H028 | SPY | LV15 |
|---|---:|---:|---:|
| Terminal wealth | $328,295 | $262,325 | $220,156 |
| CAGR | 18.5% | 14.8% | 11.9% |
| Annual volatility | 16.2% | 17.7% | 11.0% |
| MaxDD | -26.1% | -33.7% | -16.5% |
| Beta | 0.76 | 1.00 | 0.53 |
| Up capture | 0.97 | 1.00 | 0.62 |
| Down capture | 0.69 | 1.00 | 0.41 |

H028 remains:

**REJECTED.**

Its original B4 gate failed.

The original conditional-null p-value of approximately 0.0004 is structurally suspect.

Do not overwrite, reclassify or rescue this result.

---

# 2. The Statistical Question

We are trying to determine whether a future valid test could distinguish between two explanations for H028:

**Explanation A — Defensive and factor exposure**

H028's historical advantage resulted from exposures such as:

- Lower volatility.
- Market beta.
- Growth/value characteristics.
- Profitability and quality.
- Sector composition.
- Other priced systematic factors.

**Explanation B — Incremental stock selection**

H028 selected stocks that performed better than comparable stocks even after controlling for the relevant exposures.

The repaired test should aim to distinguish these explanations without creating artificial disadvantages for the null portfolios.

However, the test must be explicit about which exposures it controls.

"Beyond LOWVOL" is not the same claim as "beyond all known factors."

---

# 3. Problems Identified in the Previous Null

## Problem 1 — Donor pairing churn

D238 found that the old recipient-donor pairing null suffered from dynamic-universe churn.

Approximately 17.6% of pairings were re-formed monthly.

This created:

- Artificial rank changes.
- Additional portfolio turnover.
- Extra transaction costs.
- Potentially biased null wealth distributions.

The synthetic tests must verify that the new method eliminates this mechanical advantage for the real portfolio.

## Problem 2 — Conditional exposure mismatch

The previous null did not adequately preserve the relationships between LOWVOL and the other features.

This may have created null portfolios with systematically different factor exposures.

The observed real H028 up-capture was approximately 0.97, while the null median was approximately 0.71.

The new procedure must not mistake differences in known factor exposures for incremental stock-selection skill.

## Problem 3 — The proposed matching cells may be too sparse

R1 originally proposed matching stocks by:

- LOWVOL quintile.
- FF12 sector.
- Market-cap tercile.

That creates up to 180 cells.

With approximately 475 eligible stocks, the average is only about 2.6 stocks per cell before accounting for the uneven distribution of companies across sectors.

Adding book-to-market buckets would make this worse.

A theoretically correct matching method that cannot find credible matches is not useful.

**Solve these three methodological problems before treating any synthetic result as meaningful.**

---

# 4. The Scope of R1

The previously recommended approach is:

**R1 — Exposure-Matched Twin Portfolio Test.**

It compares selected stocks with alternative stocks sharing similar characteristics.

This test conditions on the selected portfolio and its trading decisions.

It is NOT a full-pipeline test of the Ridge training procedure.

Explicitly document:

**R1 can potentially test:**

Whether the stocks selected by the frozen strategy earned more than sufficiently comparable alternative stocks over the same investment periods.

**R1 cannot by itself establish:**

Whether the complete learned-score training, model selection, parameter fitting and portfolio construction process would systematically find profitable stock selections on independent unseen data.

Do not describe an R1 success as full-pipeline statistical validation.

A separate full-pipeline inference method would be necessary for that stronger conclusion.

---

# 5. First Task — Matching Feasibility Design

Before implementing the final R1 test, investigate how to handle sparse matching groups.

Evaluate the following alternatives using analytical reasoning and synthetic data only.

### M1 — Exact categorical matching

Match on LOWVOL quintile × sector × size tercile.

Measure:

- Number of cells.
- Expected cell occupancy.
- Percentage of singleton cells.
- Percentage with no valid alternative.
- Impact of uneven sector populations.
- Effect of adding book-to-market.

### M2 — Hierarchical matching

Use pre-declared matching priority and fallback rules.

For example, strict matching first, then a controlled relaxation.

However, relaxing a dimension changes the statistical question.

Every relaxation must be documented.

Do not silently match a technology stock with a utility because the original cell is empty.

### M3 — Constrained nearest-neighbor matching

Evaluate matching using continuous variables:

- Historical LOWVOL.
- Historical market capitalization.
- Relevant factor exposures.
- Sector constraint where feasible.

Investigate standardized distances, calipers and minimum support requirements.

Do not automatically assume nearest-neighbor matching is superior to exact matching.

### M4 — Portfolio-level exposure matching

Consider whether a portfolio of alternative stocks can match aggregate sector, LOWVOL, size and beta exposure more reliably than one-to-one stock matching.

Explain the trade-off between exposure balance and preserving the actual investment mechanics.

## Required design conclusion

Recommend ONE primary matching method, or conclude that R1 is not viable.

Before final synthetic validation, freeze:

- Matching dimensions.
- Distance metric.
- Calipers.
- Fallback hierarchy.
- Donor eligibility.
- Replacement policy.
- Matching with or without replacement.
- Minimum acceptable matching support.
- Maximum acceptable factor imbalance.
- Treatment of unmatched positions.

Do not select the method based on whichever produces the most favorable significance results.

---

# 6. Matching Eligibility and Point-in-Time Rules

At any simulated decision date, an alternative stock must:

- Exist at that date.
- Be eligible under the simulated investable universe.
- Have the required characteristics available as of that date.
- Be independently investable.
- Not be chosen using knowledge of future returns.

Do not use future returns to:

- Choose a twin.
- Set calipers.
- Define matching groups.
- Replace an exited stock.
- Resolve ties.

Where historical beta or factor exposure is used, it must be estimated from information available BEFORE the simulated decision.

Do not use realized future beta.

---

# 7. Stock Entries, Exits and Delistings

This is one of the most important sections.

The synthetic simulator must include:

- New securities entering the investable universe.
- Securities leaving the universe.
- Genuine delistings.
- Stocks losing eligibility without necessarily being delisted.
- Corporate actions.
- Changing sector and size classifications.
- Changing fundamental coverage.

Distinguish a stock becoming ineligible for a new position from an existing holding that must be liquidated under the frozen strategy's actual trading rules.

Do not assume all membership exits force immediate liquidation.

The R1 test must not create a free replacement opportunity when a twin disappears.

For every type of exit, define explicitly:

1. Whether the position continues.
2. Whether it is liquidated.
3. Which observable price is used.
4. When execution occurs.
5. Whether a replacement is permitted.
6. Which transaction costs apply.
7. What happens when no acceptable replacement exists.

A forced replacement cannot be both free and treated as a normal realistic trade.

Use the same feasible execution rules for synthetic real-style and comparator portfolios.

No hidden liquidity assumptions.

No lookahead.

---

# 8. Trading-Cost Problem — Two Separate Comparisons

The proposed R1 method originally charged twins exactly the same cost sequence as the real portfolio.

That can be useful for isolating stock-selection returns, but it is not necessarily an investable comparison.

Implement TWO clearly separated synthetic evaluation modes.

## Mode A — Controlled Selection Comparison

The real-style and twin portfolios have the same:

- Decision periods.
- Initial position capital allocations.
- Comparison horizons.
- Exogenously fixed transaction-cost debit schedule, where mathematically coherent.

Purpose:

Isolate differences in the return earned by selected securities without allowing a null-construction artifact to produce an artificial cost disadvantage.

This is a **controlled statistical comparison**, not necessarily an executable alternative portfolio.

If differing returns and portfolio wealth make exact dollar-cost equality incoherent, define the common cost schedule in a mathematically explicit and consistently normalized way.

Never conceal the approximation.

## Mode B — Realistic Investable Twin Portfolio

Each twin portfolio pays its own actual simulated:

- Buy commissions.
- Sell commissions.
- Slippage.
- Forced-exit costs.
- Legitimate replacement costs.

Use the project's original cost assumptions:

- $7 per executed buy.
- $7 per executed sell.
- 0.10% slippage per side.

Also include:

- Zero-cost diagnostic.
- 0.20% slippage-per-side stress test.

Mode B must reflect genuine executable trading and realistic cash balances.

**Do not silently switch between Mode A and Mode B when interpreting significance.**

---

# 9. Trading-Cost Acceptance Criteria

Report for both modes:

- Turnover.
- Number of buys.
- Number of sells.
- Forced replacements.
- Commissions.
- Slippage.
- Cash utilization.
- Terminal wealth.
- Relative log terminal wealth.

For Mode A, require the controlled cost schedule to agree by construction within the numerical tolerance specified before validation.

For Mode B, do not require actual trading costs or turnover to be artificially identical.

Instead verify that any differences arise from legitimate simulated trades rather than the matching algorithm creating unnecessary replacements.

On no-signal synthetic scenarios, compare real-style and twin portfolio results both before and after costs.

Flag systematic artificial turnover caused solely by the null construction.

---

# 10. Synthetic Market Generator

Reuse the project's existing committed synthetic infrastructure where appropriate.

Do not use real H028 holdings, real price observations or real future returns as simulation inputs.

Generate synthetic equity panels with:

- Monthly decision dates.
- Daily or session-level return paths as required.
- At least seven years of walk-forward evaluation.
- Approximately 475 simultaneously eligible securities in the central scenario.
- Realistic dynamic membership.
- Sector classifications.
- Market-cap variation.
- LOWVOL features.
- Correlated growth, quality, momentum and profitability characteristics.
- Market and sector factors.
- Stock-specific shocks.
- A planted distinction between systematic factor returns and incremental stock-selection information.

The generator should include both stationary and time-varying factor relationships.

Make its assumptions transparent.

Avoid inadvertently making the synthetic universe easier than the real one.

---

# 11. Simulated Selection Process

Synthetic validation must test R1 using selections generated without future information.

Include at least:

**Selection process 1 — Factor-driven selection**

A portfolio ranks stocks using known exposures such as LOWVOL, growth and profitability.

There is no incremental stock-specific predictive information beyond those exposures.

**Selection process 2 — Predictive selection**

A score ranks stocks using an additional planted predictor that genuinely forecasts future stock-specific returns.

**Selection process 3 — Randomized selection**

Selections are randomized within the eligible universe, subject to portfolio constraints.

Where feasible, include persistence and score stability similar to a monthly learned-score portfolio.

Use:

- Top 15.
- No leverage.
- Maximum initial 10% per stock.
- Maximum 3 stocks per FF12 sector.
- Monthly next-open rebalancing.

Do not tune synthetic selection rules to reproduce H028's favorable historical wealth.

The objective is to test the statistical method across different possible realities.

---

# 12. Synthetic Validation Scenarios

Implement the following independent scenarios.

| Scenario | Ground truth | Expected behavior |
|---|---|---|
| S1 | No predictive information | Approximately calibrated false-positive rate |
| S2 | LOWVOL predicts risk/returns; no incremental signal | No spurious alpha beyond LOWVOL |
| S3 | Growth/value factors are priced, no residual stock skill | Matching on those factors should remove apparent residual alpha |
| S4 | Genuine incremental stock-selection signal | Meaningful statistical power |
| S5 | No universe churn | No artificial pairing or trading artifact |
| S6 | Historical-like universe churn | Similar statistical calibration to S5 |
| S7 | Double churn | No systematic false significance caused by churn |
| S8 | Changing sector and market-cap composition | Acceptable factor and matching balance |
| S9 | Thin matching groups | Honest abstention or declared fallback, not invented matches |
| S10 | Forced exits and delistings | Correct P&L, execution and costs |
| S11 | Zero, base and doubled trading costs | Correct separation of economic costs and statistical selection evidence |
| S12 | Strong serial feature persistence and correlated predictors | No artificial rank-churn advantage for the real-style portfolio |

Include multiple random seeds and different parameterizations of each scenario.

Make sure S3 explicitly demonstrates the difference between:

- Skill beyond LOWVOL.
- Skill beyond LOWVOL plus known priced exposures.

A positive result from the first must not automatically be interpreted as the second.

---

# 13. Pre-Registration Before Final Synthetic Validation

Separate exploratory engineering tests from the final synthetic validation.

## Development fixtures

These can be used to:

- Debug code.
- Validate accounting.
- Test exit behavior.
- Correct implementation mistakes.
- Understand matching feasibility.

But they must not be represented as independent statistical validation.

## Final synthetic evaluation

Before the final evaluation:

Freeze:

- Generator versions.
- Scenario definitions.
- Matching method.
- Cost modes.
- Seeds.
- Number of simulated panels.
- Number of twin-world draws.
- Statistical test.
- Confidence interval method.
- Pass/fail criteria.
- Treatment of insufficient matching support.

Commit the protocol and hashes before running the final evaluation.

Do not modify the method after seeing final synthetic results merely to make a failed test pass.

If the frozen evaluation fails, report failure and stop.

Any substantially revised method needs a separate version and approval.

---

# 14. Statistical Calibration Requirements

Target a one-sided significance level:

**α = 0.01.**

For scenarios without incremental stock-selection skill:

- Use at least 500 independently generated synthetic panels per main calibration scenario.
- Use at least 500 null/twin draws per panel unless a documented methodological or computational reason requires a different count.
- Use a valid finite-sample Monte Carlo p-value calculation, including the appropriate finite-sample correction.
- Require the observed rejection rate at α = 0.01 to be no greater than 0.02.
- At α = 0.05, target a rejection rate within 0.035–0.065.
- Report binomial confidence intervals and uncertainty in the estimated false-positive rates.

These are pre-registered engineering acceptance thresholds, not proof of exact null validity.

Report whether the simulation count gives sufficient precision to support the conclusions.

Do not claim valid inference solely because one simulated false-positive rate falls below the threshold.

Also test whether the p-value distribution is systematically distorted.

---

# 15. Statistical Power Requirements

For a genuinely planted incremental predictor:

Test at least three effect strengths:

- Weak.
- Moderate.
- Strong.

Predefine the signal strengths numerically in the synthetic generator.

For the strong planted signal, target:

**At least 80% detection power.**

Report power at all three strengths.

If the method has low false-positive rates but almost no ability to detect a real signal, that is not a useful test for H028.

Include confidence intervals around power estimates.

Do not redefine signal strength after observing the results.

---

# 16. Matching-Support Requirements

Before final synthetic validation, pre-register numerical feasibility requirements.

At minimum report:

- Percentage of selected positions with at least one credible alternative.
- Effective donor pool size.
- Percentage requiring fallback.
- Percentage unmatched.
- Exposure imbalance.
- Sector imbalance.
- Changes in matching quality over time.
- Matching failures during high-churn periods.

Propose explicit maximum fallback and unmatched rates based on the feasible method, not on desired financial results.

If acceptable matching quality is impossible in a universe of approximately 475 stocks, declare:

**R1 NOT FEASIBLE AT CURRENT UNIVERSE SIZE.**

Do not weaken the factor controls until significance becomes easier.

Consider whether an honest abstention on unmatched positions leaves enough coverage to make the resulting inference meaningful.

---

# 17. Exposure-Balance Requirements

Evaluate the synthetic real-style portfolio and twin portfolios on:

- LOWVOL.
- Beta estimated from past data.
- Sector composition.
- Market capitalization.
- Book-to-market.
- Profitability.
- Momentum.
- Any additional systematic factor explicitly required by the selected null hypothesis.

Use standardized differences and portfolio-level balance measures.

For the main controlled exposures, propose and freeze acceptable balance thresholds before final validation.

As design targets, investigate:

- Absolute standardized differences below 0.10.
- Portfolio-level sector-weight differences below approximately 1 percentage point where support permits.
- Clearly disclosed exceptions where the investment universe cannot support those tolerances.

Do not present these as universally sufficient guarantees.

If the method cannot balance the important factors, do not interpret its positive result as stock-specific alpha.

---

# 18. Interpretation of R1 Results

The final synthetic report must distinguish:

### Correct calibration

The null produces approximately the specified false-positive rate when the controlled exposures explain all returns.

### Statistical power

The null can detect genuine planted incremental information.

### Matching feasibility

The investable universe is large and diverse enough to provide meaningful comparators.

### Economic realism

The twin portfolios can be simulated without free transactions, lookahead or invented liquidity.

### Scope of inference

Even if all the above pass, R1 assesses selected holdings conditionally, not the full learned-score training pipeline.

Do not collapse these five concepts into one PASS label.

---

# 19. R3 Factor Regression

The earlier design review proposed a secondary multi-factor time-series regression, R3.

During this checkpoint:

- Specify R3's prospective factors and statistical limitations.
- Examine its mathematical assumptions.
- Document how factors would be constructed point-in-time.
- Explain likely statistical power with only 84 months.
- Describe any relevant synthetic diagnostic tests.

You may use fully synthetic observations to test a generic R3 implementation if helpful.

Do not estimate R3 using H028's real returns.

Do not build new real historical factor series.

R3 remains secondary and is not a substitute for proving R1 valid.

---

# 20. No H028 Real-Data Run

This checkpoint must not:

- Rebuild the real H028 portfolio.
- Export real holdings.
- Retrain H028.
- Recompute its historical returns.
- Calculate its corrected p-value.
- Create a new real conditional-null distribution.
- Revisit its gates.

Existing committed result summaries may be inspected read-only for context.

If R1 requires real holdings that were never exported, simply record the dependency.

Do not work around this boundary by invoking QuantConnect.

---

# 21. Infrastructure

Prefer running all synthetic tests locally/offline.

The existing QuantConnect node previously reached approximately 7.7–8.2 GB.

Do not rely on a new QuantConnect environment or extra memory without permission.

Report:

- Synthetic CPU time.
- Peak memory.
- Number of generated panels.
- Number of null draws.
- Number of failed simulations.
- Determinism.
- Reproduction of selected seeds.
- Any computational shortcuts.

Any shortcut must preserve the statistical question.

If the computational budget is insufficient for the planned final synthetic validation:

1. Report the limitation.
2. Propose an alternative with justified statistical precision.
3. Stop for approval before reducing the required validation scope.

---

# 22. Defensive and Offensive Research Direction

The broader investment objective remains:

**Maximize long-term terminal wealth relative to SPY, after costs, over an approximately 30-year investment horizon, with acceptable risk and without leverage.**

We do not require annual outperformance every year, or necessarily in most years.

Do not change H028's already-frozen B4 gate.

Future hypotheses may use long-horizon wealth as the primary objective and annual relative performance as a diagnostic.

A possible future architecture is:

**Defensive component + Offensive component.**

But H028 has not qualified as a defensive production component.

This checkpoint is NOT approval to develop the offensive component.

Do not attempt to construct a new offensive score, market-regime switch, or combined portfolio here.

A separate owner decision will address that only after we determine whether H028 merits further methodological reassessment.

---

# 23. Required Deliverable

Create:

**P13-CP6 — H028 Repaired Null Synthetic Validation**

Include:

1. Repository state and source references.
2. Exact owner-approved scope.
3. H028 original REJECTED status preserved.
4. D238 root-cause summary.
5. Conditional exposure mismatch.
6. R1's exact statistical question.
7. What R1 cannot prove.
8. Matching feasibility study.
9. Matching methods compared.
10. Frozen selected matching method, if viable.
11. Matching support and fallback policies.
12. Entry/exit and delisting rules.
13. Controlled-cost Mode A.
14. Investable-cost Mode B.
15. PIT and lookahead safeguards.
16. Synthetic market generator design.
17. Generator version/hash.
18. Scenario definitions.
19. Frozen seed ranges.
20. Frozen statistical acceptance criteria.
21. Tests for false-positive calibration.
22. Confidence intervals for calibration.
23. Power at weak/moderate/strong signals.
24. Effect of no, normal and double churn.
25. Effect of correlated factors.
26. Growth-factor exposure mismatch test.
27. Thin-cell behavior.
28. Exposure matching and balance statistics.
29. Matching coverage.
30. Forced-exit accounting.
31. Zero-cost comparison.
32. Base-cost comparison.
33. Doubled-slippage comparison.
34. Artificial-turnover checks.
35. Synthetic portfolio return calculations.
36. Statistical test validity limitations.
37. R3 secondary diagnostic design.
38. Number of synthetic simulations.
39. Numerical determinism.
40. Peak memory and runtime.
41. Failed tests and unresolved limitations.
42. Confirmation no real H028 run occurred.
43. Confirmation no Holdout data was accessed.
44. Confirmation H028's status and gates were unchanged.
45. Overall feasibility recommendation.
46. Exact next approval required.

Keep the full protocol, generator, source code, synthetic outputs and tests reproducible.

Follow repository conventions for commits and PRs.

Do not merge a change that silently alters any existing hypothesis, frozen result, Data manifest or previously approved gate.

If the design is not viable, document why and stop rather than manufacturing a passing synthetic result.

---

# 24. Final Decision Classification

Conclude with exactly one:

## A — SYNTHETICALLY VALIDATED METHOD

The pre-registered synthetic tests pass, matching support is adequate, costs are handled correctly, and the limits of conditional inference are documented.

Next possible action:

**Owner approval required for a separate real-data reassessment checkpoint.**

Do not perform it.

## B — METHOD NOT VALIDATED

The synthetic tests fail, matching is inadequate, type-I error is miscalibrated, or the method cannot separate selection skill from exposure reliably.

Do not repair it repeatedly during the same checkpoint after inspecting the final results.

Stop for owner review.

## C — INCONCLUSIVE

The evidence or computational precision is insufficient to establish validity or failure.

Report the exact blocker and what additional work would be required.

No automatic continuation.

---

# 25. Mandatory STOP

When P13-CP6 is complete:

**STOP.**

Return the report and PR link.

Do not launch a real-data test.

Do not run the 2022–2026 Holdout.

Do not start a new hypothesis.

Do not assume a valid synthetic null makes H028 a successful investment strategy.

I will review the synthetic evidence before deciding whether a corrected H028 evaluation is justified.
