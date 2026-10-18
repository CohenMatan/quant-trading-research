# Owner message 2026-10-18: Close Phases 13–14 and Design the Next Long-Term Research Programme

Decision id: **D240**. The owner's message is quoted verbatim below (as received). Recorded before any closure edit or roadmap text was written.

Scope recorded with it:
- approval to close P13-CP6's H028 null-repair line, Phase 13 and Phase 14 administratively, and the current research cycle;
- approval to prepare a design-only roadmap;
- **no** approval to execute further research (no backtest, null, synthetic experiment, QuantConnect research run, Holdout access, H031, purchase, or strategy implementation).

---

Owner Approval — Close Phases 13–14 and Design the Next Long-Term Research Programme
Objective
I approve the formal administrative closure of the H028 null-repair line, Phase 13 and Phase 14, followed by a design-only research roadmap for a long-term US-equity investment system.
The long-term goal remains:
Build an autonomous, long-only stock-selection system that compounds more terminal wealth than SPY Buy & Hold over an investment horizon of approximately 30 years, after realistic costs, without leverage and with acceptable risk.
The system does NOT need to outperform SPY every calendar year or even in the majority of years.
The principal economic objective is long-term relative terminal wealth, not annual win rate.
Potential future architecture:

1. A defensive component that helps preserve wealth during difficult markets while maintaining reasonable upside participation.
2. An offensive component that seeks stronger appreciation and participation in rising markets.
3. Potentially a combined portfolio, but only if evidence supports the components and their combination.

These are research directions, not approved or proven strategies.
PART 1 — Approved Owner Decisions
Decision A — Accept P13-CP6
I accept the findings of:
`docs/checkpoints/P13_CP6_h028_repaired_null_synthetic_validation.md`
Final classification:
B — METHOD NOT VALIDATED.
The tested R1 matching approaches could not adequately match H028-like concentrated selections while controlling the important factor exposures.
The secondary R3 factor-regression approach also failed its synthetic calibration under priced growth and profitability factors.
Therefore:

* Close the H028 null-repair workstream.
* Do not create R1-V1 or R1b.
* Do not attempt additional H028 null-repair variants under this approval.
* Preserve all committed synthetic code, reports, failures and methodological findings.
* Do not characterize these findings as proof that no valid statistical method could ever exist.

H028's original formal status remains:
H028 REJECTED.
Its originally reported conditional-null significance is not considered reliable.
Do not modify its original hypothesis, backtest results or gates.
Decision B — Formally Close Phase 13
I approve formal closure of Phase 13.
Record:
PHASE 13 — CLOSED — NO QUALIFIED PRODUCTION CANDIDATE.
Preserve the history:

* H028 was explicitly approved and tested.
* Its real development backtest produced higher terminal wealth than SPY.
* Its original B4 requirement failed.
* D238 later identified a structural issue in the original conditional null.
* P13-CP6 attempted to establish a credible repaired methodology through synthetic testing.
* The repair methodology was not validated.
* H028 remains REJECTED.

The closure is administrative. It must not rewrite historical experimental outcomes.
H028 may be referenced in future architectural reviews as an interesting historical defensive-style observation, but not as a validated strategy, proven alpha or approved production component.
Decision C — Formally Close Phase 14
I approve formal closure of Phase 14.
Record:
PHASE 14 — CLOSED — H029/H030 NOT EVALUABLE.
Preserve the exact distinction between the historical execution status and the final administrative classification:

* H029 and H030 were approved for development.
* Their implementations and synthetic/null-related tests exist.
* Their null-evaluation designs encountered methodological blockers.
* No valid final null calibration was completed.
* No real performance evaluation of H029 or H030 was performed.
* E031-10 was never executed.
* Therefore, neither hypothesis has an interpretable real economic result.

Their previous historical status of BLOCKED must remain in the research record.
The final administrative closure classification is:
NOT EVALUABLE — NO VALID REAL-DATA EVALUATION.
Do NOT relabel either hypothesis as REJECTED based on investment performance.
Do NOT call either hypothesis profitable, unprofitable, or statistically insignificant.
Do NOT launch the previously proposed third null or any new null.
Preserve Data v3 and all existing research artifacts.
Decision D — Close the Current Research Cycle
Record the programme-level conclusion:
Research cycle completed — No Production Candidate Found.
This is not a decision to abandon systematic investing.
It means that none of the evaluated hypotheses has met its own required qualification criteria.
No new hypothesis is authorized by this administrative closure.
PART 2 — Administrative Repository Work
1. Verify before modifying
Start by inspecting the current repository and main branch.
Check:

* `DECISIONS.md`
* `CLAUDE.md`
* `experiments/INDEX.csv`
* Existing Phase 13 and Phase 14 checkpoints
* D238 and D239
* Owner decision records
* H028, H029 and H030 specifications
* Any existing research-governance or closure conventions

If the repository contains material changes since P13-CP6, report them before proceeding.
Do not assume that the previous conversation accurately describes the latest repository state.
2. Record this approval
Create the next appropriately numbered owner decision using existing repository conventions.
Preserve the owner's instructions verbatim.
Distinguish:

* Approval to close previous research administratively.
* Approval to prepare a design-only roadmap.
* Absence of approval to execute further research.

3. Update project status
Update relevant status documentation so future Claude sessions do not mistakenly restart H027, H028, H029 or H030.
At minimum, the current-state documentation should make clear:

* Latest completed research: Phase 14.
* H026: REJECTED.
* H027: REJECTED and CLOSED.
* H028: REJECTED; Phase 13 CLOSED.
* H029/H030: historical BLOCKED; final administrative status NOT EVALUABLE; Phase 14 CLOSED.
* H028 repaired-null attempt: B — METHOD NOT VALIDATED.
* No qualified production strategy.
* No active experiment.
* Holdout remains sealed.
* Future work requires new owner approval.

Where historical experiment or hypothesis files contain stale headers, update status metadata carefully without modifying frozen experimental definitions or original results.
4. Preserve reproducibility
Do not remove, rewrite or replace:

* Original experiment results.
* Null-world results.
* Failed synthetic tests.
* Owner approvals.
* Statistical thresholds.
* Data manifests.
* Frozen feature definitions.
* Existing decision IDs.
* Existing checkpoint conclusions.

Historical failures are research assets and must remain available.
PART 3 — Design the Next Research Programme
5. The investment objective
Our target is a long-term portfolio of US common equities.
The existing baseline restrictions remain:

* NYSE/Nasdaq US common stocks.
* Market capitalization of at least $2 billion.
* Price of at least $5.
* ADV20 of at least $5 million.
* Long-only.
* No leverage.
* No options.
* No intraday trading.
* Realistic commissions and slippage.
* Point-in-time data.
* Correct delisting and corporate-action treatment.
* Decisions based only on information already available.

The existing $100,000 starting capital is the research baseline, not necessarily the eventual actual investment amount.
Use SPY Buy & Hold with reinvested distributions as the principal benchmark.
Identical starting capital and calendar dates are mandatory.
6. Define success over approximately 30 years
The primary statistic for future hypotheses should be:
S = ln(terminal strategy wealth / terminal SPY wealth)
Both wealth paths must include realistic trading costs and use the same dates.
Greater terminal wealth is the central objective.
However, a strategy should not be selected on terminal wealth alone.
Design supporting diagnostics for:

* CAGR and excess CAGR.
* Maximum drawdown.
* Time underwater.
* Relative drawdown versus SPY.
* Recovery duration.
* Rolling 3-year, 5-year and 10-year relative performance.
* Longer rolling windows when reliable historical data support them.
* Up-market capture.
* Down-market capture.
* Volatility and market beta.
* Sector and style concentration.
* Trading turnover and implementation costs.
* Return concentration in a small number of periods.
* Sensitivity to realistic cost increases.

Annual win rate should remain a diagnostic, not a universal qualification requirement.
A strategy may lose to SPY in many individual calendar years yet still generate more terminal wealth over a sufficiently long period.
Explain how to distinguish tolerable intermittent underperformance from an economically fragile strategy that depends on one extraordinary market episode.
Do not retroactively relax any historical gate from H026, H027 or H028.
7. Long-horizon data feasibility
Assess the feasibility of studying an approximately 30-year investment horizon.
The previous research reported that:

* The usable point-in-time stock-selection development panel mainly covers 2011–2021.
* 2022-01-01 through 2026-08-31 is the still-sealed Holdout.
* Earlier price history exists, but complete point-in-time stock fundamentals, identities, delistings and market capitalization are problematic before approximately 2010.
* Paid datasets may be required for reliable earlier stock-level research.

Verify these limitations from existing records.
Produce a feasibility assessment for:

* 1998–2009.
* 2010–2021.
* The untouched Holdout.
* Future forward/paper-trading data.

For every period distinguish:

1. Data exists.
2. Data is historically accurate.
3. Data is point-in-time usable.
4. Data is free of material survivorship bias.
5. Data has already influenced research decisions.
6. Data can legitimately provide independent confirmation.

Do not assume 1998–2009 is clean merely because stock-selection hypotheses have not previously been tested there.
Do not purchase data.
Do not retrieve or inspect the Holdout.
If a true 30-year backtest is unavailable, say so clearly rather than extrapolating shorter results and calling that a 30-year test.
PART 4 — Defensive Component Research
8. What H028 taught us
H028 demonstrated historically interesting defensive-style behavior during 2015–2021.
Its existing results may be discussed descriptively.
However:

* H028 remains rejected.
* Its significance test was structurally suspect.
* Its repaired statistical evaluation failed feasibility.
* Its apparent advantage was concentrated in already-observed market periods.
* The evidence does not establish stock-specific alpha beyond known factor exposures.

Do not promote H028 as an approved defensive model.
9. Transparent defensive alternatives
Investigate which simple defensive approaches might serve as transparent future benchmarks.
Examples to assess conceptually:

* Low-volatility equity selection.
* Quality and profitability screening.
* Defensive combinations of low volatility and quality.
* Investable low-volatility ETFs.
* A pre-specified mix of SPY and a defensive equity ETF.
* A beta-controlled equity benchmark.

Compare their conceptual properties and data requirements.
Do not assume that lower drawdown automatically means higher long-term wealth.
Particular attention should be given to the opportunity cost of holding defensive exposures throughout sustained bull markets.
The purpose is to establish suitable future benchmarks and independently motivated concepts, not to fit something to H028's historical path.
PART 5 — Offensive Component Research
10. Research the untested information sources
The offensive component should seek superior long-term stock appreciation without leverage.
We want to identify sources of genuine predictive information, rather than merely inventing another weighting of the existing technical and fundamental variables.
Review H001–H030 and identify which economic signals have already been tested adequately, which failed, and which remain insufficiently investigated.
Pay special attention to genuinely distinct information sources, including:

* Accounting earnings surprise.
* Earnings acceleration.
* Revenue and operating-profit acceleration.
* Changes in profitability trends.
* Earnings-estimate revisions, if valid historical PIT data exist.
* Share issuance and buybacks.
* Changes in capital allocation.
* Sustainable business improvement.
* Other independently supported cross-sectional return signals.

These examples are not automatically approved features.
Do not describe plain momentum, 52-week highs, historical low volatility or profitability scores as entirely new discoveries when closely related hypotheses have already been tested.
Investigate whether each proposed information source provides economically distinct information beyond the previous research.
11. Evaluate candidate offensive research families
Recommend three to five research families at most.
For each provide:

* Economic hypothesis.
* Evidence from existing literature or committed research references.
* Relationship to earlier failed hypotheses.
* Required raw data.
* Point-in-time availability.
* Availability without new purchases.
* Expected coverage of eligible stocks.
* Expected historical depth.
* Likely turnover and costs.
* Expected principal risk exposures.
* Main implementation challenges.
* Potential survivorship or lookahead problems.
* Feasible statistical evaluation method.
* How that evaluation would avoid the defective null mechanisms discovered in D238 and P13-CP6.
* Whether its evidence would be development-only or potentially independent.

Prefer hypotheses supported by credible mechanisms and trustworthy data, not just those with attractive historical narratives.
Do not build, train, tune or test any of them.
12. H029 and H030 history
Business-improvement research is not automatically invalid because H029/H030 could not be evaluated.
But do not silently reopen them.
Explain:

* Which underlying hypothesis was left untested.
* Which methodological blockers prevented evaluation.
* Whether a future materially different approach could address those blockers.
* What would need to change before a new owner-approved hypothesis is justified.

Do not continue the old Phase 14 experiment queue.
PART 6 — Potential Defensive + Offensive Portfolio
13. Portfolio integration is a future hypothesis
One possible architecture is:
Combined Portfolio = Defensive Allocation + Offensive Allocation
with allocations totaling 100% and no leverage.
Do not assume that a 50/50 split is optimal.
Do not estimate optimal weights from H028's already-seen performance.
Do not create retrospective market-regime switching rules based on the 2018 or 2020 sell-offs.
A future combined portfolio must be evaluated as a single investable system.
Discuss the requirements for:

* Independent evidence supporting each component.
* Overlapping holdings.
* Total sector exposure.
* Total position limits.
* Combined turnover.
* Trading-cost interactions.
* Portfolio-level beta.
* Joint drawdowns.
* Relative performance in bull and bear markets.
* Fixed versus dynamic allocation.
* Transparent and independently justified allocation rules.

Also address a fundamental question:
Does using two strategies actually offer a credible advantage over a simpler SPY plus defensive ETF mix?
That simpler alternative should be an explicit benchmark.
Do not presume complexity adds value.
PART 7 — Statistical Integrity Reset
14. Lessons from D238 and P13-CP6
The next research programme must not repeat the invalid-null problems.
Document the key methodological failures:

* Persistent donor-pairing churn.
* Artificial rank changes and turnover.
* Null portfolios with different systematic exposures.
* Marginal permutation where conditional relationships matter.
* Sparse matching support for extreme Top-15 selections.
* Inadequate regression adjustment for priced factors.
* Repeated hypothesis development on the same historical period.

For any future hypothesis, the statistical test must be justified by the actual null being tested.
Synthetic calibration must occur before interpreting new real-world statistical results.
Do not simply reuse a familiar null because it was used in previous phases.
15. Future experimental governance
Propose a new research process with distinct checkpoints:

1. Economic hypothesis and independent justification.
2. PIT-data feasibility and integrity audit.
3. Synthetic validity study of the statistical evaluation method.
4. Frozen portfolio and model specifications.
5. Frozen costs and risk requirements.
6. Frozen success criteria.
7. Development experiment.
8. Development decision and audit.
9. Independent confirmation only when justified and separately approved.
10. Prospective paper trading before any production deployment.

Maintain full tracking of attempted hypotheses and all model-selection decisions.
Avoid presenting a new backtest on the repeatedly used 2011–2021 dataset as fresh independent validation.
16. No retrospective rescue
The long-horizon objective is now explicit.
It does not grant permission to rewrite previous outcomes.
H026, H027 and H028 remain REJECTED.
H029/H030 remain unevaluated.
No failed statistical test becomes valid just because terminal wealth looked attractive.
We must distinguish:

* Economic attractiveness.
* Defensive exposure.
* Statistical evidence.
* Independent confirmation.
* Production readiness.

PART 8 — Deliverables
17. Administrative closure checkpoint
Create a formal checkpoint documenting:
Research Cycle Closure — Phases 13 and 14
Include:

* The owner's approvals.
* P13-CP6 classification B.
* H028 unchanged REJECTED status.
* The unreliable H028 null evidence.
* Phase 13 formally CLOSED.
* H029/H030 historical BLOCKED status.
* H029/H030 final NOT EVALUABLE classification.
* No real H029/H030 evaluation.
* Phase 14 formally CLOSED.
* No production candidate found.
* Data versions retained.
* Existing experiments preserved.
* The Holdout remains sealed.

18. Forward-looking roadmap
Create a second document titled:
Long-Term Defensive and Offensive Equity Research Roadmap — 30-Year Objective
Include:

1. Programme objective.
2. Current verified project status.
3. Findings from H001–H030.
4. What the negative results establish.
5. What they do not establish.
6. The role and limitations of H028.
7. Possible transparent defensive benchmarks.
8. Distinct offensive research families.
9. PIT historical-data availability.
10. Pre-2010 data feasibility.
11. Unseen versus already-examined periods.
12. Proposed long-horizon evaluation framework.
13. Risk and drawdown requirements to consider.
14. Benchmarks for defensive, offensive and combined portfolios.
15. Statistical evaluation validity requirements.
16. Synthetic-validation requirements.
17. Computational and QuantConnect limitations.
18. Data-cost considerations.
19. Multiple-testing governance.
20. Recommended next research direction.
21. Main reasons for that recommendation.
22. Required next owner decision.

Do not invent missing evidence.
Use source references to earlier decisions and checkpoints.
19. Prioritize the roadmap
At the end, recommend:

* One preferred next research direction.
* One credible alternative.
* Any infrastructure or data prerequisite.
* The smallest next checkpoint that can test feasibility without overcommitting resources.

Prefer feasibility and design checkpoints before expensive backtests.
Explain why the preferred direction is not merely an overfit reaction to H026–H028.
20. Repository and PR
You are authorized to:

* Record this owner decision.
* Make administrative status updates.
* Create the closure checkpoint.
* Create the design-only roadmap.
* Update governance documentation.
* Commit these administrative and documentation changes.
* Open or merge the corresponding PR according to existing repository conventions.

You are NOT authorized to:

* Alter historical strategy implementations.
* Rewrite frozen results.
* Modify Data v2, v2.1 or v3.
* Run new null-world simulations.
* Run synthetic experiments.
* Run backtests.
* Use QuantConnect to execute research.
* Access the Holdout.
* Start H031.
* Purchase datasets.
* Implement any defensive or offensive strategy.
* Build the combined portfolio.

Documentation and administrative closure only.
PART 9 — Mandatory Stop
Once the repository closure and roadmap are complete:
STOP AND RETURN FOR OWNER REVIEW.
Provide:

1. Closure decision ID.
2. Updated current project status.
3. Paths to the two new documents.
4. Commit or PR link.
5. Summary of the most important findings.
6. Recommended next research direction.
7. Exact next owner approval required.

Do not begin that next direction automatically.
The intended final state is:
PHASES 13–14 CLOSED
H028 REJECTED
H029/H030 NOT EVALUABLE
NO PRODUCTION CANDIDATE
NEXT RESEARCH PROGRAMME: DESIGN ONLY
2022–2026 HOLDOUT SEALED
AWAITING OWNER DECISION
