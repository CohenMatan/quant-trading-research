# Owner message — 2026-10-18 (D245)

**Scope recorded by Claude:** LH-CP4 — OF-A statistical feasibility and research-horizon assessment.
- **Decision 1:** LH-CP3 is accepted as **B — PARTIAL RECOVERY**.
- **Decision 2:** a narrow, prospective Stage C exception. It allows future *design consideration* of decision years 2015–2021 with directly verified L0 / L1 fiscal labels under LH-CP2 rule V only:
  - no L2 / L3 labels, P-assume, rule P, or unknown / invalid histories;
  - no post-2021 information;
  - existing identity, PIT and integrity rules preserved.
- **Decision 3:** an analytical, paper-only power assessment. No synthetic simulation, Monte Carlo, real-return analysis, QuantConnect run, signals, rankings, backtests, model training, Stage B, null worlds, H028 change, purchase or Holdout.
- **Earlier results unchanged:** LH-CP1 stays C — NOT FEASIBLE, LH-CP2 stays C — INSUFFICIENT EVIDENCE and LH-CP3 stays B — PARTIAL RECOVERY.
- **Mandatory STOP** after the checkpoint.

The message follows verbatim.

---

Owner Approval — LH-CP4: OF-A Statistical Feasibility Assessment
Administrative Stage C Exception + Analytical Power Assessment Only
I approve the following three decisions.
Decision 1 — Accept LH-CP3
Accept the final LH-CP3 classification:
B — PARTIAL RECOVERY.
Preserve the original checkpoint and all its findings.
The reconstruction work demonstrated strong label-recovery accuracy, but the method was not fully validated against hidden genuine fiscal-calendar changes.
Do not reinterpret that partial success as complete validation.
Decision 2 — Approve a Narrow Stage C Exception
I approve a narrowly scoped exception allowing the next OF-A research design to use:
Decision years: 2015–2021 only.
Accounting histories: directly verified fiscal labels only (L0/L1).
Fiscal-period validation: existing conservative LH-CP2 Rule V.
Conditions:

* No inferred L2 or L3 labels.
* No P-assume.
* No Rule P.
* No unknown or invalid fiscal-period histories.
* No use of post-2021 filings or information.
* All required historical quarters must satisfy the validation requirements.
* Preserve existing SEC identity and PIT availability rules.
* Preserve all historical data-integrity restrictions.

The original LH-CP1 Stage C result remains:
C — NOT FEASIBLE under its frozen protocol.
The LH-CP2 result remains:
C — INSUFFICIENT EVIDENCE.
The LH-CP3 result remains:
B — PARTIAL RECOVERY.
This owner-approved exception is a new, prospective restriction of the usable research population, not a retrospective change to an earlier experiment.
The exception authorizes future design consideration of the verified 2015–2021 population.
It does not authorize Stage B, Stage D, real signal computation or a backtest.
Decision 3 — Perform an Analytical Statistical Feasibility Assessment
Before approving any further synthetic experiments, evaluate whether the restricted 2015–2021 history provides enough statistical information to detect an economically meaningful OF-A signal.
This assessment is paper-only / analytical-only.
No synthetic simulation, Monte Carlo run, real-return analysis or QuantConnect research is authorized.
PART 1 — Repository Verification and Governance
Before starting:

1. Verify the current `main` branch and working tree.
2. Read D240–D244 and the relevant governance rules.
3. Read the RM1 and RM2 roadmaps.
4. Read LH-CP1, LH-CP2 and LH-CP3.
5. Verify the original frozen protocols and reconstruction-rule hashes.
6. Verify the existing hypothesis-selection ledger.
7. Confirm that the Holdout is sealed.

Record this message verbatim under the next available owner decision.
Create an explicit record of the narrow Stage C exception.
Do not edit frozen historical protocols or results.
H028 remains REJECTED.
H029/H030 remain NOT EVALUABLE.
No production candidate exists.
No active experimental hypothesis is approved.
PART 2 — Define the Available Evidence
1. Research Period
The future OF-A development period under this exception is:
2015-01-01 through 2021-12-31.
The actual usable decision dates must respect the availability of sufficient historical quarterly data.
Do not assume that every eligible stock has a complete history.
Use only the directly verified L0/L1 population under Rule V.
Verify from committed LH-CP3 results:

* C1 minimum annual coverage in this period.
* C2 minimum annual coverage.
* C6 minimum annual coverage.
* Population exclusions.
* Entrant and leaver representation.
* Remaining PIT and accounting limitations.

Distinguish the E981-01 Data v1 eligible-universe denominator from the unavailable exact Data v2.1 denominator.
Do not silently claim that the two populations are identical.
2. Effective Sample Size
A period covering approximately seven calendar years does not necessarily provide seven full years of independent usable signal observations.
Estimate analytically:

* Number of possible monthly review dates.
* Number of usable decision months.
* Typical eligible stock counts per month from existing non-return aggregates.
* Effects of filing frequency.
* Effects of repeated quarterly signals between filings.
* Serial dependence in stock characteristics.
* Cross-sectional dependence from market and sector factors.
* Reduced effective sample size under clustered returns.

Critically distinguish:
Number of stock-month observations from number of independent observations supporting statistical inference.
Thousands of stocks observed over 84 months do not create thousands of independent market regimes.
No real stock-return statistics may be calculated.
PART 3 — Statistical Detectability
3. Evaluate the Proposed Signal-Level Test
RM2 proposed universe-wide Fama–MacBeth-type cross-sectional testing with controls including:

* Sector.
* Market capitalization.
* LOWVOL.
* Book-to-market.
* Profitability.
* Momentum.
* Asset growth.
* Market beta.

Review the statistical feasibility of that design over 2015–2021.
The purpose is not yet to prove that this method is valid.
It is to understand what level of signal could reasonably be detectable with the available research history.
Examine:

1. Number of independent time observations.
2. Number of cross-sectional observations.
3. Serial correlation.
4. Sector correlation.
5. Persistence of quarterly signals.
6. Unbalanced company coverage.
7. Dependence caused by common filing seasons.
8. Missingness among entrants, leavers and smaller firms.
9. Number of control variables.
10. Effect of multiple hypotheses.

Clearly distinguish design feasibility from actual statistical calibration.
A method that looks powerful analytically may still fail the future synthetic validity study.
4. Analytical Power Requirements
The previous roadmap proposed identifying an economically meaningful effect with at least 80% statistical power.
One illustrative effect was:
Approximately +3% annualized gross excess return for a long-only top signal quintile.
Do not automatically treat this as a finalized economic threshold.
Investigate whether the proposed effect is detectable over approximately seven years.
Use analytical power approximations only.
Where justified, evaluate illustrative assumptions for:

* Different cross-sectional information coefficients.
* Different effective monthly standard errors.
* Different signal persistence.
* Different degrees of time-series correlation.
* Different numbers of effective independent periods.
* One versus two hypotheses.
* Nominal significance of 1% and 5%, including the effect of multiple-testing adjustment.

Use explicit assumed parameter ranges and clearly label every assumption.
Do not estimate parameters from new real-return data.
Do not perform Monte Carlo simulation.
Do not fabricate covariance estimates or information coefficients.
If the available non-return artifacts cannot support a reasonable parameter value, present a sensitivity range instead.
Calculate analytical minimum detectable effects and approximate power where the assumptions permit.
Report cases where reliable analytical power cannot be calculated.
5. Do Not Confuse Statistical and Economic Effect Sizes
The following are not interchangeable:

* Cross-sectional regression slope.
* Rank information coefficient.
* Top-quintile gross excess return.
* Portfolio alpha.
* Long-term CAGR advantage.
* Terminal wealth advantage over SPY.

Explain what mathematical assumptions would be required to translate one into another.
Do not assert that an annualized 3% top-quintile return corresponds to any particular Fama–MacBeth t-statistic without supporting assumptions.
If a meaningful conversion cannot be justified, report separate power calculations for hypothetical regression effects and separate economic cost hurdles.
A statistically detectable signal is not automatically an investable strategy.
PART 4 — Economic Relevance and Costs
6. Long-Term Investment Objective
Our actual objective remains:
Maximize after-cost terminal wealth relative to SPY over approximately 30 years, without leverage and with acceptable risk.
We do not require outperformance every calendar year.
We do require evidence that a proposed source of returns could realistically compensate for:

* Market exposure.
* Transaction costs.
* Trading turnover.
* Cash drag.
* Opportunity cost.
* Additional strategy complexity.

Explain why discovering a weak cross-sectional signal might not translate into economically meaningful excess terminal wealth.
Do not calculate real strategy performance.
7. Illustrative Cost Hurdles
Using only the existing frozen cost assumptions:

* $7 per executed order.
* 0.10% slippage per side.
* $100,000 baseline capital.
* Optional $200,000 capital sensitivity.

Present analytical examples of potential trading-cost hurdles for plausible future portfolio constructions.
Use explicitly hypothetical turnover and trade-size assumptions.
Do not infer future OF-A turnover from untested portfolio behavior.
Identify how annualized gross signal benefits would need to exceed costs to become economically meaningful.
Do not turn these examples into final portfolio specifications.
PART 5 — Review Frequency
8. Monthly Versus Filing-Driven Decisions
LH-CP1 found approximately:

* Median 18 trading sessions from earnings release to first trade under monthly reviews.
* Median 14 sessions waiting for the monthly review after accounting-data availability.
* A much shorter delay under daily review opportunities.

Analyze the operational and statistical trade-offs among:
A. Monthly Decisions
Retain the existing monthly decision structure.
B. Daily Review Opportunities
Check each trading day whether a new, valid accounting report has become available.
Execute any approved trade at the next permissible market open.
This is not intraday trading.
C. Filing-Event-Driven Decisions
Reconsider positions only when a newly available filing creates an eligible signal update, subject to prospective portfolio rules.
Compare conceptually:

* Decision latency.
* Number of possible review dates.
* Expected data freshness.
* Computational requirements.
* Potential turnover.
* Fixed commission burden.
* Dependence among observations.
* Operational complexity.
* Compatibility with the existing QuantConnect environment.

Do not assume that earlier trading generates more profit.
Do not use real returns to compare the frequencies.
Do not implement or select a new review frequency.
The output should identify which timing choice is worth evaluating later and why.
PART 6 — The Limited Hypothesis Budget
9. Preserve Research Discipline
For planning purposes, retain the proposed upper budget from RM2:

* At most two signal hypotheses.
* At most one standalone portfolio.
* At most one combined-portfolio hypothesis.
* At most one future Holdout candidate.

This is a planning ceiling, not permission to execute any of them.
Do not select C1/C2/C6 yet.
Do not finalize the F1–F6 portfolio fragility screens during this checkpoint.
Separate:

* Statistical detectability.
* Signal economics.
* Portfolio economics.
* Investor risk tolerance.

Any future final gates require a separate owner decision before testing.
PART 7 — Decision Framework
10. Required Assessment
The final report must answer:
Can seven years of verified 2015–2021 data plausibly provide enough independent statistical information to evaluate an economically meaningful OF-A signal?
Give one of four conclusions:
A — ANALYTICALLY PROMISING
Under credible and explicitly stated assumptions, the proposed signal-level design has plausible power to detect an economically meaningful effect.
A later synthetic validation study may be justified.
This does not authorize Stage B automatically.
B — UNDERPOWERED FOR MODEST EFFECTS
The available period is unlikely to detect economically plausible small effects reliably.
It may still detect unusually strong effects.
Explain whether Stage B would provide useful information or mostly confirm insufficient power.
C — NOT VIABLE UNDER CURRENT CONSTRAINTS
The combination of time horizon, timing delay, sample dependence and economic costs makes the proposed evaluation framework unjustifiable.
Recommend stopping or changing research direction.
D — INSUFFICIENT INFORMATION
The analytical assessment cannot support a meaningful power conclusion without data or assumptions that are currently unavailable or unauthorized.
Specify the missing inputs and why they matter.
Do not claim A simply because a favorable hypothetical parameter set produces 80% power.
PART 8 — Checkpoint Deliverables
Create a checkpoint titled:
LH-CP4 — OF-A Statistical Feasibility and Research-Horizon Assessment
Include:

1. Owner authorization.
2. D245 or the next available decision ID, verified rather than assumed.
3. Explicit record of the Stage C exception.
4. Confirmation that earlier results were not changed.
5. The restricted 2015–2021 population.
6. Directly verified L0/L1 and Rule V requirements.
7. Expected effective sample-size limitations.
8. Fama–MacBeth feasibility analysis.
9. Analytical power assumptions and equations.
10. Approximate minimum detectable effects.
11. Sensitivity to statistical dependence.
12. Multiple-hypothesis implications.
13. Economic versus statistical significance.
14. Illustrative after-cost return hurdles.
15. Monthly versus daily versus filing-driven decisions.
16. Operational and QuantConnect constraints.
17. Consequences of having only seven development years.
18. Remaining Data v1 versus Data v2.1 denominator limitations.
19. Evidence limitations and assumptions.
20. Final classification A/B/C/D.
21. Recommendation on whether a future Stage B is worthwhile.
22. Exact next owner decision required.
23. Explicit confirmation that no return analysis or synthetic experiment was performed.
24. Explicit confirmation that the Holdout remained sealed.

Record this authorization verbatim.
Commit documentation and any deterministic, purely analytical calculation helpers required for the report.
Unit tests may verify analytical equations and the approved-population restrictions.
Do not make any new stock-level calculations from actual returns.
PART 9 — Mandatory Restrictions and STOP
You are NOT authorized to:

* Run Stage B.
* Run synthetic inference simulations.
* Run new null worlds.
* Run a stock backtest.
* Compute historical OF-A signals or rankings.
* Compute historical stock returns.
* Train a model.
* Select an offensive portfolio.
* Combine an offensive portfolio with H028.
* Change H028.
* Access the Holdout.
* Purchase data.
* Modify frozen historical results.
* Broaden the Stage C exception beyond verified 2015–2021 data.
* Begin another checkpoint automatically.

After the LH-CP4 report and permitted PR are complete:
STOP AND RETURN FOR OWNER REVIEW.
Report:

* The owner decision ID.
* The documented Stage C exception.
* Final analytical feasibility classification.
* Most important assumptions and limitations.
* Whether Stage B is worth approving.
* Whether monthly decisions remain sensible for OF-A.
* The precise next owner approval required.

The project objective is unchanged.
H028 remains a frozen defensive reference with formal status REJECTED.
OF-A remains a possible offensive research direction, not an approved or proven strategy.
The 2022–2026 Holdout remains sealed.
