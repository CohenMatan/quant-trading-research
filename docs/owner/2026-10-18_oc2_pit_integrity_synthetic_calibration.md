# Owner message — 2026-10-18 (D248)

**Scope recorded by Claude:** OC-2 (profitability improvement, the exact frozen Data v3 / H029 F5 definition) approved as the single offensive stock-selection candidate. Two sequential stages:
- **Stage 1:** a focused Data v3 / PIT / fiscal-period integrity audit. Offline only, on committed evidence and offline SEC data. No F5 values, rankings or returns. No QuantConnect run. Outcome PASS / CONDITIONAL / FAIL; only PASS permits Stage 2.
- **Stage 2 (only after a Stage 1 PASS):** a synthetic-only inference calibration under a protocol frozen and hashed before any synthetic result. Outcome A / B / C / D.
- **Not authorised:** real-return tests, portfolios, backtests, SYS-1, combined portfolios, H028 / H029 / H030 changes, purchases, Holdout access, automatic advance.
- **Statuses:** H028 REJECTED (frozen defensive research reference); H029 / H030 NOT EVALUABLE; OF-A unqualified with D245 unchanged; OC-2 approved direction, not performance-tested; no qualified strategy.
- **Mandatory STOP** after Stage 2 (or after a non-PASS Stage 1).

The message follows verbatim.

---

Owner Approval — OC-2 Profitability Improvement
Point-in-Time Integrity Gate → Conditional Synthetic Statistical Validation
I approve OC-2 — Profitability Improvement as the single offensive stock-selection research candidate to investigate next.
This follows the candidate-selection work in OC-CP2, recorded as D247.
The ultimate goal remains to find an independent offensive stock-selection strategy that can complement H028's defensive characteristics and potentially improve long-term after-cost terminal wealth relative to SPY.
SPY remains our simple offensive baseline and fallback.
This authorization consists of two sequential stages:

1. Stage 1: Focused Data v3 / PIT / Fiscal-Period Integrity Audit.
2. Stage 2: Synthetic Statistical Inference Calibration, conditional on Stage 1 passing.

No real-return test, portfolio backtest or Holdout access is authorized.
1. Verify the Current Research State
Before starting:

* Verify the latest merged PR and repository state.
* Confirm D247 is the latest owner decision, or identify any subsequent legitimate decision.
* Read OC-CP1 and OC-CP2.
* Read LH-CP1 through LH-CP4.
* Read RM2's statistical-inference and synthetic-validation requirements.
* Read the original frozen H029 definitions, especially F5.
* Inspect Data v3, its frozen specification, manifest and validation records.
* Review D238/D239 methodological failures.
* Review the fiscal-calendar findings from LH-CP2 and LH-CP3.
* Verify all relevant historical source hashes and permissions.

Record this approval under the next available decision ID.
Preserve the existing research governance.
Formal statuses remain:

* H028: REJECTED, frozen defensive research reference.
* H029: NOT EVALUABLE.
* H030: NOT EVALUABLE.
* OF-A: unqualified; D245 restrictions unchanged.
* OC-2: newly approved research direction, not yet performance-tested.
* No qualified investment strategy.

The Holdout remains sealed.
2. Freeze the OC-2 Hypothesis
The selected mechanism is:
Improvement in corporate profitability, measured by the change in return on assets over the preceding year.
Use the exact original Data v3 / H029 F5 definition.
Do not silently substitute a new formula, normalization, accounting field or lookback window.
Verify:

1. Exact mathematical definition of F5.
2. Required net-income and asset fields.
3. TTM construction.
4. Comparison-period construction.
5. Normalization and missing-value rules.
6. Availability and timestamp rules.
7. Existing accounting-data guards.
8. Any differences between the OC-CP2 proposal and the frozen original definition.

If any inconsistency exists, document it and STOP before modifying the hypothesis.
Do not evaluate F1–F4 or F6–F8.
Do not run an H029 portfolio.
Do not combine multiple profitability signals.
Do not create alternative F5 variants.
Do not tune parameters using real returns.
This is one fixed hypothesis.
The economic rationale is that improving profitability may reflect positive business developments that markets incorporate gradually.
It is not assumed to generate alpha.
Its potential complementarity with H028 is a research motivation, not a validated property.
STAGE 1 — DATA AND PIT INTEGRITY
3. Verify the Proposed 2012–2021 Research Window
OC-CP2 proposes a development window approximately:
2012-02 through 2021-11, 118 monthly decision dates.
However, the distinction between OC-2 and OF-A's accounting-period requirements needs to be demonstrated rather than assumed.
The D245 exception restricted OF-A to directly verified 2015–2021 histories.
OC-CP2 argues that F5 is not affected in the same way because its construction uses dated SEC quarterly periods instead of fiscal-quarter labels.
I authorize investigating that distinction.
Do not automatically apply OF-A's restrictive L0/L1 policy to OC-2.
Equally, do not automatically exempt OC-2 from known fiscal-period risks.
Use the accounting properties of the actual F5 formula to determine whether 2012–2021 can be used safely.
No change to D245 is authorized.
4. Test the Actual Accounting-Period Construction
Inspect how Data v3 constructs:

* Quarterly net income.
* TTM net income.
* Total assets.
* Historical comparison values.
* The year-over-year change in ROA.

For the original F5 formula, determine whether the following can produce incorrect comparisons:

* Genuine fiscal-year changes.
* 52/53-week fiscal years.
* Irregular quarter durations.
* Missing reporting quarters.
* Transition reports.
* Quarter-aligned fiscal changes.
* Inconsistent fiscal-year-end metadata.
* Misidentified reporting periods.
* Fourth-quarter values derived from annual and year-to-date figures.
* Differences between a balance-sheet point-in-time value and a quarterly flow.
* SEC registrant identity changes.
* Restatements and historical vendor corrections.

The critical question:
Does F5 require fiscal quarters to be economically comparable, and does the existing frozen Data v3 implementation ensure that comparability?
A chain of 80–100-day reporting-period gaps is not necessarily sufficient evidence by itself.
Conversely, a changed fiscal-year-end code does not automatically make the historical values invalid.
Investigate the actual risk to F5.
5. Point-in-Time Rules
Verify that every accounting value used by F5 was publicly available at the historical decision date.
Preserve the existing availability rule, including both SEC filing availability and QuantConnect vendor first-seen constraints.
Check:

* Original filing date.
* Earliest legal availability date.
* First permitted trading session.
* Original versus revised financial values.
* Any use of subsequently restated data.
* SEC identity as known at the time.
* Quarterly information that arrived too late for a given decision.

Never use post-2021 financial information.
Never use the Holdout.
No new QuantConnect run is authorized for this audit.
Prefer the existing committed PIT evidence and offline SEC data.
If a critical field can be verified only inside QuantConnect, identify the dependency and STOP rather than bypassing the restriction.
6. Quantify Data Feasibility
Using only existing permitted accounting metadata and data-availability information, report:

* Earliest truly usable decision month.
* Number of valid monthly decision dates.
* Eligible-universe coverage by year.
* Stock counts per month.
* Missing-data reasons.
* Fiscal-period comparability failures.
* Invalid or ambiguous TTM constructions.
* Identity failures.
* Impact of conservatively excluding problematic observations.
* Differences between the Data v1 and Data v2.1 historical universe definitions.
* Remaining PIT uncertainty.

Do not compute F5 values or historical stock rankings.
Do not compute returns.
Do not use future performance to decide which observations are valid.
Use a precommitted validation protocol, with objective accounting and PIT rules independent of the resulting coverage.
7. Stage 1 Gate
Classify the data:
PASS — PIT-SAFE AND SUFFICIENT
The exact F5 definition can be computed using demonstrably comparable accounting periods with no unresolved material PIT or identity problem, and the usable sample is sufficiently characterized for the proposed synthetic calibration.
CONDITIONAL
The candidate appears computable, but material uncertainty remains about fiscal periods, accounting definitions, historical coverage or point-in-time correctness.
FAIL — NOT SUPPORTED
The existing data cannot support the exact F5 definition credibly under the approved constraints.
Only PASS authorizes proceeding to Stage 2 under this message.
If CONDITIONAL or FAIL:

* Commit the findings.
* Preserve the original data and classifications.
* STOP.
* Request the owner's decision.

Do not repair a failed gate by retroactively relaxing its criteria.
STAGE 2 — SYNTHETIC STATISTICAL CALIBRATION
8. Authorization Boundary
If and only if Stage 1 receives PASS, I authorize a synthetic-only statistical validation study.
This is NOT approval to calculate real signals or evaluate real market returns.
The synthetic study must use artificially generated explanatory variables and returns.
It may use existing approved aggregate metadata to reproduce broad features of the research population, including:

* Number of securities.
* Historical population size.
* Reporting frequency.
* Filing-event clustering.
* Missingness.
* Entrants and leavers.
* Sector structure.
* Observation timing.

Do not calibrate parameters using newly computed real F5-return relationships.
Do not use the Holdout.
Do not purchase data.
Do not execute QuantConnect runs.
9. Protocol Freeze Before Any Synthetic Result
Before running synthetic simulations:

1. Write a complete statistical-validation protocol.
2. Specify the inference method.
3. Specify all null scenarios.
4. Specify planted-signal alternatives.
5. Specify synthetic data-generating parameters.
6. Specify seeds and replication counts.
7. Specify false-positive criteria.
8. Specify statistical-power criteria.
9. Specify economically meaningful target effects.
10. Specify failure and stopping rules.
11. Commit the protocol and hash.
12. Verify the protocol is immutable during evaluation.

Any substantive change following synthetic results requires an explicit new owner decision.
Do not tune repeatedly until the tests pass.
If the method cannot be fully specified without resolving an important ambiguity, STOP for owner clarification before running it.
10. Required Inference Method
Evaluate a universe-wide signal-level approach, using Fama–MacBeth cross-sectional regressions as the primary proposed framework.
The future real-data test would ask whether F5 predicts subsequent stock returns after accounting for known style and risk exposures.
Review the proposed controls from RM2 and OC-CP2, including:

* Sector.
* Company size.
* Market beta.
* Low volatility.
* Momentum.
* Value.
* Existing profitability level.
* Asset growth.
* Accruals.

Make sure the chosen controls are themselves historically available and do not introduce look-ahead.
Do not calculate the regressions on real stock returns.
The synthetic study must assess whether the inference method remains reliable under realistic dependence among the signal and control variables.
It must address the methodological failure modes documented in D238 and D239.
In particular, avoid:

* Identity-tether or pointer-permutation nulls.
* Invalid matched-twin nulls.
* Uncalibrated time-series factor regressions used as proof of stock-selection skill.

Do not assume ordinary t-statistics are valid.
11. Synthetic Scenarios
Adapt the previously proposed RM2 synthetic scenarios S0–S10 and planted alternatives P1–P3 to OC-2.
Required null mechanisms include:

1. No predictive signal and no priced style factors.
2. Priced low-volatility exposure.
3. Priced growth exposure.
4. Priced profitability exposure.
5. Multiple priced factors correlated with the candidate signal.
6. Noisy or imperfectly measured controls.
7. Time-varying factor premia.
8. Cross-sectional dependence and sector shocks.
9. Entries, exits and delistings.
10. Quarterly signal refreshes and stale monthly observations.
11. Uneven filing-event timing.
12. Historical data missingness.
13. Heavy-tailed and heteroskedastic returns.
14. Overlapping return horizons where relevant.

Where noisy controls make the true predictive effect statistically unidentifiable, distinguish that structural identification failure from incorrect estimation of standard errors.
Do not claim that choosing a different standard error can automatically solve omitted-variable or measurement-error bias.
Use planted-signal worlds to assess power at predeclared effect sizes.
Document why the synthetic worlds reasonably approximate the known structure of the data without using future stock returns.
12. False-Positive Calibration
Start from RM2's proposed standards:

* At least 1,000 synthetic replications per null scenario.
* Nominal 1% significance: empirical false-positive rate no greater than 2%.
* Nominal 5% significance: empirical rejection rate between 3.5% and 6.5%.
* Appropriate predeclared calibration diagnostics.

Do not quietly weaken these standards.
If mathematical or design reasons make any requirement inappropriate for OC-2, explain them before the study and obtain owner approval for a revised rule.
A test that produces false positives too frequently is not validated, regardless of its apparent statistical power.
13. Statistical Power
Evaluate the ability to detect economically meaningful effects over the verified OC-2 research horizon.
Use the true Stage 1 population characteristics rather than automatically assuming 118 usable independent monthly observations.
Report:

* Number of calendar-month cross-sections.
* Effective time-series sample size.
* Signal update frequency.
* Dependence among observations.
* Sensitivity to factor correlations.
* Power under alternative signal strengths.
* Minimum detectable effect at 50% and 80% power.
* Consequences of a conservative 1% significance threshold.
* Effects of the historical programme's multiple-testing and selection context.

Use +3% annualized gross top-quintile excess over the eligible universe as an illustrative economically meaningful reference point.
Also report sensitivity at +2%, +4% and +5%.
These are signal-level gross effects, not claims about an investable portfolio or SPY outperformance.
If analytical conversion from an IC or regression slope to top-quintile return requires assumptions, state them explicitly.
Do not change the target to +5% merely because it makes the study easier to pass.
If the method lacks adequate power for +3%, report that directly.
No synthetic significance result can prove OC-2 itself has an edge.
14. Stage 2 Outcome
At the conclusion, report one of:
A — METHOD VALIDATED WITH USEFUL POWER
The inference procedure controls false positives under the predeclared null scenarios and has sufficient power to detect the predeclared economically meaningful effect.
B — METHOD CALIBRATED BUT UNDERPOWERED
False-positive control is acceptable, but the available sample cannot reliably detect the target effect.
C — METHOD NOT VALIDATED
One or more essential false-positive or identification requirements fail.
D — INSUFFICIENT EVIDENCE
The synthetic framework or available assumptions are inadequate to justify a reliable conclusion.
Do not call the method validated merely because one favorable scenario passes.
Do not change the significance threshold, effect-size target or method after seeing results.
15. Economic Relevance
Preserve the difference between:

1. Statistically significant stock-selection information.
2. Economically meaningful gross cross-sectional excess returns.
3. A realizable long-only stock portfolio.
4. Net returns after costs.
5. Incremental benefit over SPY.
6. Complementarity with H028.
7. Long-term relative terminal wealth.

This stage evaluates only whether the statistical method could reliably study the first two.
It does not evaluate the investment performance of OC-2.
Future portfolio construction must comply with:

* US common equities.
* Historical PIT universe.
* Market cap >= $2B.
* Price >= $5.
* ADV20 >= $5M.
* Long-only.
* No leverage.
* No intraday trading.
* $100K baseline, $200K diagnostic.
* $7 per executed order.
* 0.10% slippage per side.
* Maximum 15 concurrent stock positions and applicable minimum position size.

Do not solve the combined-account position-limit problem during this checkpoint by changing the frozen rules.
That requires a separate owner decision after standalone signal qualification.
16. Frozen H028 and Simple Benchmarks
H028 remains:
REJECTED — Frozen Defensive Research Reference.
Do not modify, retrain or rerun H028.
Do not run SYS-1.
Do not construct a combined portfolio.
SPY remains the main simple offensive comparator.
No performance inference regarding OC-2 or its complementarity with H028 is authorized.
Even if synthetic calibration passes, we will still need a separate owner decision before any actual real-return experiment.
17. Required Deliverables
Use the repository's existing checkpoint and owner-decision naming conventions.
Produce two clearly separated checkpoint records, or a checkpoint containing two independently auditable stages.
Stage 1 Deliverable — OC-2 Data Integrity
Include:

* Exact frozen F5 definition.
* Historical data-source versions and hashes.
* Accounting-period construction.
* Fiscal-year transition handling.
* TTM comparability.
* Point-in-time constraints.
* 2012–2021 coverage findings.
* Reasons for excluding observations.
* Data v1 versus Data v2.1 limitations.
* Clear PASS / CONDITIONAL / FAIL result.

Commit Stage 1 findings before any synthetic result.
Stage 2 Deliverable — Synthetic Validation
Only if Stage 1 passes:

* Frozen synthetic protocol and hash.
* Data-generating process definitions.
* Null-world scenarios.
* Planted-signal scenarios.
* Inference estimators.
* False-positive frequencies.
* Calibration diagnostics.
* Power curves and minimum detectable effects.
* Methodological failures, if any.
* Research effort and execution costs.
* A/B/C/D outcome.
* Exact recommendation for the next owner decision.

Record:

* Source commits.
* Scripts and tests.
* Seeds and reproducibility settings.
* Any approved protocol amendments.
* Every failed or incomplete run.

Do not omit a failed scenario from the report.
Use the normal repository PR workflow.
Do not change historical experiment records or frozen results.
18. Mandatory STOP Conditions
STOP immediately if:

* The original F5 formula cannot be established unambiguously.
* Stage 1 discovers a material unresolved PIT violation.
* The required accounting periods cannot be shown to be comparable.
* The 2012–2021 window cannot be justified under the proposed constraints.
* A new QuantConnect run or unauthorized data export would be required.
* Stage 1 is CONDITIONAL or FAIL.
* The synthetic protocol cannot be frozen without additional owner decisions.
* A compliance restriction is encountered.
* The approved scope would need to expand.

After completing Stage 2, STOP regardless of whether it passes.
Do not automatically:

* Run real-return signal tests.
* Run any stock-selection backtest.
* Implement an OC-2 portfolio.
* Test combined portfolios.
* Run SYS-1.
* Reactivate H029 or H030.
* Modify H028.
* Purchase data.
* Access the Holdout.
* Start the next research stage.

Return the completed checkpoint for my review.
19. Final Research Objective
I want an independent offensive stock-selection strategy that could complement the weaknesses of H028 while contributing to superior long-term after-cost wealth relative to SPY.
OC-2 is now the only authorized offensive stock-selection candidate for focused investigation.
The immediate objective is not to demonstrate OC-2 profitability.
The immediate objective is to establish:
Can our existing point-in-time data support the exact OC-2 profitability-improvement signal, and can we validate a statistical method powerful and reliable enough to test it meaningfully?
If the answer is no, record the limitation and STOP.
If the answer is yes, return the exact proposal for one real-data signal test, requiring separate owner approval.
H028 remains frozen and rejected.
SPY remains the fallback.
The Holdout remains sealed.
