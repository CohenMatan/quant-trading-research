# Owner message — 2026-10-18 (D249)

**Scope recorded by Claude:** one final, controlled methodological repair attempt of the OC-2 synthetic calibration (v2).
- **Allowed:** synthetic data only. Fix the documented defects; redesign the controls and the standard error; correct the generator; write one frozen v2 protocol; run engineering smoke tests; run one confirmatory v2 evaluation; write the checkpoint OC-CP5.
- **Not allowed:** real returns or real F5 signals, QuantConnect, backtests, portfolios, H028 / H029 / H030 changes, SYS-1, purchases, post-2021 data, the Holdout, model searches, relaxing criteria after results, a v3, or automatic advance.
- **v1 artifacts** (OC-CP4, D — INSUFFICIENT EVIDENCE) are preserved unchanged.
- **Explicit owner rule:** if a new tolerance or exception is required, or if the written criterion cannot coherently address a scenario, STOP before the confirmatory evaluation and request a specific owner decision.
- **Mandatory STOP** after OC-CP5.

The message follows verbatim.

---

Owner Approval — OC-2 Synthetic Calibration v2
One Final Controlled Methodological Repair Attempt
I approve one revised synthetic-only statistical calibration study for OC-2 (Profitability Improvement / F5).
This follows D248 and the completed checkpoints:

* OC-CP3 — OC-2 Stage 1 Data Integrity: PASS.
* OC-CP4 — OC-2 Stage 2 Synthetic Calibration: D — INSUFFICIENT EVIDENCE.

The purpose is to determine whether the statistical-inference failures identified in OC-CP4 can be corrected through a scientifically justified, prospectively frozen methodology.
This is one controlled repair attempt, not permission for iterative optimization until a favorable result is achieved.
No real stock-return testing, real F5 signal evaluation, QuantConnect backtest, portfolio construction or Holdout access is authorized.
1. Verify the Current Repository and Decisions
Before starting:

1. Verify the latest merged main branch and clean working tree.
2. Verify D248 is the latest owner decision, unless a subsequent legitimate decision exists.
3. Read OC-CP2, OC-CP3 and OC-CP4 in full.
4. Read the exact OC-CP4 synthetic protocol, scripts, results and reported deviations.
5. Review D238 and D239 regarding previously invalid inference methods.
6. Verify the frozen Data v3 / H029 F5 definition.
7. Verify the Stage 1 accounting and PIT integrity artifacts.
8. Confirm that H028 remains REJECTED and frozen.
9. Confirm that the Holdout remains sealed.

Record this authorization verbatim under the next available owner decision ID, expected to be D249 if D248 remains the latest.
Preserve all OC-CP4 v1 artifacts, including failed tests, crashed scenarios, diagnostic results and original classifications.
Do not overwrite, relabel or retroactively repair the v1 result.
2. Scope of This Approval
You MAY:

* Inspect existing synthetic-calibration code and results.
* Fix documented implementation defects.
* Redesign the statistical controls based on a defensible methodological rationale.
* Improve the covariance/standard-error estimator.
* Correct synthetic data-generating parameters.
* Write one new frozen v2 protocol.
* Run engineering smoke tests before the frozen evaluation.
* Execute one complete, pre-registered synthetic v2 evaluation.
* Report empirical false-positive rates, statistical power and failure diagnostics.
* Commit reproducible code, tests, configuration, outputs and checkpoints.

You MAY NOT:

* Read or compute real stock returns.
* Compute historical F5 signals on actual stocks.
* Run real-data Fama–MacBeth regressions.
* Run QuantConnect.
* Run a trading backtest.
* Test combined portfolios.
* Modify H028.
* Reactivate H029 or H030.
* Run SYS-1.
* Purchase datasets.
* Access post-2021 market or financial data.
* Open the 2022–2026 Holdout.
* Run multiple statistical model searches.
* Relax the acceptance criteria after observing results.
* Automatically proceed to a real-return study.

Use existing approved structural metadata and synthetic data only.
3. Begin With a Failure-Mode Audit
Before writing the v2 protocol, produce a concise technical audit of why v1 failed.
Distinguish at least four separate categories.
A. Functional Defects
Investigate:

* The N13 small-universe crash.
* The N7 inconsistent noise configuration.
* The mismatch between the protocol's D classification and the run script's C classification.

Identify the exact root cause of each defect.
Correct implementation defects without changing the scientific question.
The v2 classification must follow the frozen protocol mechanically.
B. Nonlinear Factor Leakage
Investigate the observed false-positive inflation in scenarios such as N4.
Determine whether the signal is proxying a nonlinear transformation of a priced observed characteristic.
Examine whether predeclared nonlinear controls can correct this without introducing excessive instability or overfitting.
C. Noisy Controls and Hidden Confounding
Investigate N5a and N2L separately.
N5a concerns imperfectly measured controls.
N2L concerns a priced latent factor not adequately observed by the researcher.
These are not necessarily the same problem.
A correctly calculated standard error cannot remove omitted-variable bias.
A flexible regression cannot guarantee that an unobserved priced factor is controlled.
Do not label an unidentified factor effect as genuine incremental OC-2 alpha.
D. Unrealistically Quiet Synthetic Markets
The earlier synthetic environment produced IC variability around 0.03, substantially below the broader 0.06–0.12 sensitivity range considered in LH-CP4.
Identify why this occurred.
Distinguish:

* Cross-sectional return dispersion.
* Dispersion of monthly IC estimates.
* Serial correlation of monthly IC values.
* Factor-premium variability.
* Common sector shocks.
* Firm-specific residual noise.

Do not fix the problem merely by multiplying one standard error by an arbitrary constant.
The simulated data-generating process must generate the intended dependence structure.
4. Design One Primary v2 Statistical Method
Select one primary inference procedure before the full evaluation.
The starting framework is a universe-wide Fama–MacBeth-type cross-sectional regression.
It should investigate whether F5 contains incremental information about subsequent stock returns beyond observable company and style characteristics.
The future real-data controls may include:

* Sector.
* Market capitalization.
* Beta.
* Low volatility.
* Momentum.
* Book-to-market.
* Profitability level.
* Asset growth.
* Accruals.

Only include variables that could be available point-in-time in a future real-data evaluation.
You may propose nonlinear transforms, interactions or spline terms where justified by the failures.
However:

1. Define the complete control specification before evaluating v2.
2. Do not search over many nonlinear models and select whichever produces the best calibration result.
3. Account for correlations among F5 and the controls.
4. Examine estimator stability under changing stock counts.
5. Specify all preprocessing, winsorization and standardization rules.
6. Specify how missing controls are handled.
7. Do not use synthetic oracle variables unavailable to the future real-data test as primary controls.

An oracle specification may be used as a non-gating diagnostic to demonstrate that a hidden-factor failure is due to identification rather than implementation.
But oracle success must never substitute for success of the implementable method.
5. Improve the Standard-Error Treatment
The synthetic panel should reflect:

* Quarterly profitability signal updates.
* Repeated signal values between filings.
* Monthly return horizons.
* Cross-sectional market and sector dependence.
* Serially correlated factor premia.
* Changes in eligible securities.
* Uneven reporting-event timing.

Choose an appropriate time-series covariance estimator for the monthly cross-sectional slopes.
A longer-lag HAC/Newey–West estimator may be appropriate, but its lag length must be selected prospectively from the assumed dependence structure.
Specify the primary lag rule before the full synthetic evaluation.
Alternative lag lengths may be reported as non-gating sensitivity diagnostics only.
Do not select whichever lag produces the lowest false-positive rate after viewing the results.
Also distinguish:

* Correct standard-error calibration.
* Unbiased estimation of the intended incremental signal.
* Identification problems caused by unobserved risk factors.

These are separate requirements.
6. Realistic Synthetic Market Structure
Use the actual approved Stage 1 population structure wherever permitted.
The baseline research window remains approximately:
February 2012 through November 2021 — 118 monthly reviews, subject to the verified Stage 1 definition.
The synthetic generator should reproduce relevant aggregate properties such as:

* Number of eligible companies by month.
* Sector mix.
* Quarterly report arrival patterns.
* Uneven filing dates.
* Missingness.
* Entrants and leavers.
* Variable cross-sectional sample size.
* Persistence of the profitability signal.

Synthetic return-generating parameters must be explicit assumptions, not estimates from newly inspected real returns.
Evaluate plausible IC noise scenarios, including:

* Lower variability.
* A central scenario near the previously considered 0.09 monthly IC standard deviation.
* Higher variability, approximately 0.12.

These values are scenario assumptions, not established properties of OC-2.
Before running the final evaluation, verify that the generator is mathematically capable of producing the intended dispersion and dependence.
Do not quietly use v1's artificially low variability when drawing power conclusions.
7. Pre-Registered Null Worlds
Preserve all scientifically relevant null mechanisms from OC-CP4.
At minimum, evaluate:

1. Pure no-signal null.
2. Priced market and size effects.
3. Priced low-volatility exposure.
4. Priced growth/profitability characteristics.
5. Nonlinear observed-factor effects.
6. Noisy measurements of observed factors.
7. A priced latent factor correlated with F5.
8. Time-varying factor premia.
9. Correlated sector and market shocks.
10. Heteroskedastic and heavy-tailed return distributions.
11. Quarterly signal refresh and stale monthly values.
12. Entrants, leavers and nonrandom missingness.
13. Small and varying cross-sectional sample sizes.
14. Irregular reporting-event timing.

Map these scenarios to the original v1 scenario IDs where possible.
If an original scenario cannot be reproduced exactly because it contained a coding or configuration defect, document the correction explicitly.
Do not silently remove failed scenarios.
Critical distinction: N2L-type latent confounding
If a latent priced factor is correlated with F5 and unavailable to the real-world researcher, then an observed-controls regression may be unable to identify an independent F5 effect.
This must be acknowledged explicitly.
For that scenario report:

* The magnitude of the apparent false signal.
* Its dependence on hidden-factor strength.
* Whether feasible observed proxies reduce the bias.
* Whether the method can distinguish the planted independent signal from factor exposure.
* The resulting scope of any future alpha claim.

Do not classify the overall method as proving independent alpha if it cannot rule out that confounding.
Do not simply remove latent-factor scenarios from the official evaluation to obtain PASS.
If any new tolerance or exception is required, propose it before the full run and STOP for owner approval rather than selecting it after observing outcomes.
8. Engineering Validation Before the Full Run
Before freezing the final v2 evaluation:

* Unit-test N13 at both small and realistic stock counts.
* Verify N7's intended noise structure.
* Verify deterministic seeds and reproducibility.
* Verify panel dimensions and missingness.
* Verify the synthetic generator's theoretical covariance properties.
* Verify that the classification implementation matches the written protocol.
* Confirm that all required scenarios can execute.
* Confirm that no source path points to actual returns or restricted data.

Engineering smoke tests may use small synthetic samples.
They must not be used to select the statistical model based on rejection rates or power.
If a necessary defect cannot be fixed without changing the intended statistical assumptions, document the blocker and STOP.
9. Freeze the Protocol Before Evaluation
Write and commit a complete v2 protocol before the first confirmatory synthetic result.
Freeze:

* The primary statistical estimator.
* Controls and transformations.
* Standard-error estimator and lag rule.
* Synthetic scenario definitions.
* Population structure.
* Parameter values.
* Seeds.
* Replication counts.
* False-positive thresholds.
* Power targets.
* Classification logic.
* Stopping conditions.
* Treatment of hidden-factor identification failures.

Record a SHA-256 hash of the protocol and relevant code/configuration.
Use separate engineering/development seeds and final evaluation seeds.
No substantive changes are allowed after the full evaluation begins.
A technical rerun is permitted only for a logged infrastructure failure, with the exact same frozen scientific configuration.
Do not allow an automatic loop that repeatedly modifies the estimator or scenarios until the gates pass.
There is one v2 confirmatory evaluation.
10. False-Positive Calibration Gates
Retain the previously approved statistical calibration requirements:

* At least 1,000 synthetic replications per applicable null scenario.
* Nominal 1% significance: empirical rejection rate no greater than 2%.
* Nominal 5% significance: empirical rejection rate between 3.5% and 6.5%.

Report Monte Carlo uncertainty for each estimated rejection rate.
For each null world provide:

* Number of completed replications.
* Number of rejected hypotheses.
* Empirical rejection percentage.
* Monte Carlo confidence interval.
* Bias of the estimated signal effect.
* Standard-error behavior.
* PASS/FAIL against the frozen criterion.

Distinguish computational failures from valid statistical replications.
Do not exclude failed replications because their results are unfavorable.
If a null world is fundamentally non-identifiable with the permitted observed controls, report this separately as an identification limitation.
Do not convert an identification failure into a calibration pass by changing the scientific meaning of the null hypothesis.
If the written criterion cannot coherently address such a scenario, STOP before confirmatory evaluation and request a specific owner decision.
11. Planted-Signal Power Evaluation
After the primary estimator and null calibration protocol are frozen, evaluate planted effects.
Include illustrative gross annual top-quintile excess targets:

* +2%.
* +3%.
* +4%.
* +5%.

These are top-quintile gross returns relative to the eligible universe, not net portfolio alpha and not excess returns relative to SPY.
Use 1% significance as the conservative primary threshold.
Report power at 5% significance as a diagnostic.
Use the same dependence, missingness and factor structures as the null evaluation.
Calculate:

* Statistical power by planted effect.
* Power by noise regime.
* Power by factor-correlation regime.
* Minimum detectable effect at 50% power.
* Minimum detectable effect at 80% power.
* Dependence on monthly sample size.
* Sensitivity to quarterly information arrivals.
* Effective independent time observations.

Do not claim that more stocks create more independent market regimes.
Do not claim that a method has 100% power if the underlying synthetic market is substantially quieter than the intended scenario.
The +3% gross annual effect remains our primary economically meaningful reference point.
Do not change this target to +5% merely to produce a favorable result.
A calibrated but underpowered method is an acceptable and informative scientific outcome.
12. Classification Rules
The final report must give one official classification.
A — CALIBRATED AND SUFFICIENTLY POWERED
The method satisfies the frozen false-positive and identification requirements and has adequate power for the predeclared economically meaningful effect.
B — CALIBRATED BUT UNDERPOWERED
The method satisfies the applicable reliability requirements, but cannot detect the +3% reference effect with sufficient power.
Any unresolved latent-factor identification limitation must be stated explicitly and must not be hidden by the label.
C — NOT VALIDATED
The implementable method fails an essential statistical reliability requirement, including material uncontrolled false-positive inflation or unaddressed confounding where the protocol requires identification.
D — INSUFFICIENT EVIDENCE
The study cannot support a conclusive classification because of missing essential evidence, invalid scenarios, or uncompleted required evaluation.
The frozen protocol must specify classification precedence before the confirmatory run, including how to treat a scenario crash or identification failure.
The evaluator's computed classification must match the written protocol.
If the analysis is underpowered, report B only if the method first satisfies its relevant reliability requirements.
Do not use B as a substitute for a reliability failure.
13. One Attempt — No Automatic v3
This authorization permits a single methodological repair cycle.
If v2 fails:

* Preserve all results.
* Explain exactly what failed.
* State whether the failure is computational, statistical, or structural.
* Do not run v3.
* Do not search for another estimator.
* Do not weaken the thresholds.
* Do not start real-return experiments.
* Return the findings to the owner.

A failure may justify closing OC-2 on the current data and methods, even if it does not prove that the underlying economic hypothesis is false.
14. No Real-Market Performance Testing
You are explicitly forbidden from:

* Computing historical F5 ranks.
* Calculating F5-versus-return relationships.
* Evaluating real information coefficients.
* Training predictive models using actual returns.
* Selecting stocks based on F5.
* Building an OC-2 portfolio.
* Backtesting long-only stock portfolios.
* Comparing realized OC-2 performance against SPY.
* Combining OC-2 with H028.
* Opening the Holdout.

Stage 1 already concluded that the data foundation is sufficient.
Do not repeat or expand Stage 1 into a new real-data research programme.
The present authorization covers synthetic inference methodology only.
15. Required Deliverables
Create a new checkpoint:
OC-CP5 — OC-2 Synthetic Calibration v2
Use the existing repository naming conventions.
Include:

1. Repository verification.
2. Owner decision record.
3. Original OC-CP4 classification preserved.
4. Complete v1 failure-mode analysis.
5. N7 correction.
6. N13 correction.
7. N4 nonlinear-factor treatment.
8. N5a noisy-controls treatment.
9. N2L latent-factor identification assessment.
10. Primary v2 estimator specification.
11. Covariance/standard-error methodology.
12. Synthetic market parameter justification.
13. Realistic variability checks.
14. Frozen protocol and hashes.
15. Reproducibility seeds.
16. Full null-scenario results.
17. False-positive results at 1% and 5%.
18. Monte Carlo uncertainty.
19. Planted-signal power results.
20. Minimum detectable effects.
21. Identification limitations.
22. All failed and incomplete scenarios.
23. Comparison with v1, without rewriting v1.
24. Official A/B/C/D classification.
25. Exact recommendation for owner review.
26. Confirmation no real returns, signals or backtests were used.
27. Confirmation no Holdout information was accessed.

Commit code, tests, frozen protocol, output artifacts and checkpoint through the normal PR process.
Preserve complete reproducibility within our existing resource and licensing constraints.
16. Mandatory STOP
After completing OC-CP5:
STOP AND RETURN FOR OWNER REVIEW.
Regardless of the outcome, do not automatically approve:

* A real-data Fama–MacBeth evaluation.
* An OC-2 portfolio.
* H028 combination research.
* SYS-1.
* Another synthetic repair.
* New datasets.
* New hypotheses.
* Any Holdout access.

If the method passes, recommend the precise next decision required to run one real-data OC-2 signal test.
If it fails, explain whether OC-2 should be closed and SPY adopted as the offensive baseline.
The next decision belongs to the owner.
Final Research Principle
Our investment objective remains:
Find a long-only, unleveraged US-equity strategy capable of contributing to greater after-cost terminal wealth than SPY over approximately 30 years.
OC-2 is being investigated as a potentially independent offensive stock-selection strategy that might eventually complement H028.
The purpose of this checkpoint is only to answer:
Can we build a statistically reliable, adequately powered method to evaluate OC-2 using the existing research history?
Do not mistake a successful synthetic test for evidence of real profitability.
Do not mistake a failed statistical method for proof that profitability improvement has no economic value.
We are authorizing one rigorous repair attempt, not an indefinite search for favorable results.
H028 remains REJECTED and frozen.
SPY remains the simple offensive fallback.
The Holdout remains sealed.
