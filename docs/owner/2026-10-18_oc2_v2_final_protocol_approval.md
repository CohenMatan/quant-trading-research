# Owner decision D250 — OC-2 Synthetic Calibration v2: Final Protocol Approval (2026-10-18)

**Context:**
- This follows D249 / OC-CP5a (`docs/checkpoints/OC_CP5a_oc2_synthetic_calibration_v2_prerun_stop.md`, merged in PR #114, main 56f55ef).
- The owner chose **Option 2** (identification gate on the complete decision rule) with additional mandatory safeguards.
- The message is recorded verbatim below.

---

Owner Decision — OC-2 Synthetic Calibration v2: Final Protocol Approval
I approve Option 2 from your OC-CP5a decision request, subject to the additional mandatory safeguards below.
This authorization follows D249. Record it as the next available owner decision after verifying the repository.
The goal is to complete one final, frozen, synthetic-only v2 confirmatory evaluation of the OC-2 statistical inference method.
I accept using the full research decision rule — statistical significance together with the predeclared +3% annualized gross economic-effect threshold — to assess false approvals in the confounded null worlds.
However, this is not permission to ignore severe confounding, weaken statistical standards, or claim independent alpha without adequate identification.
1. Preserve the Existing Work
Verify the current repository state and the merged PR #114.
Preserve:

* The frozen OC-CP4 v1 protocol and D classification.
* The OC-CP5a methodological findings.
* The repaired N7 and N13 implementations.
* The nonlinear-control specification.
* The realistic synthetic noise calibration.
* The fixed-b / covariance methodology.
* The original OC-2 F5 hypothesis.
* All historical research and governance restrictions.

Do not rewrite failed historical results.
Do not introduce a new signal or search over additional model specifications.
2. Approve the Two-Tier Calibration Framework
Tier 1 — Ordinary Null Worlds
For the approximately 30 ordinary null worlds identified in the existing v2 design, preserve the original strict statistical-size requirements:

* At nominal 1% significance: empirical rejection rate no greater than 2%.
* At nominal 5% significance: empirical rejection rate between 3.5% and 6.5%.
* At least 1,000 completed replications per applicable null world.

Preserve the exact scenario inventory and report the verified count.
Do not remove or reclassify an ordinary null world because its results are unfavorable.
Tier 2 — Measurement Error and Hidden-Factor Confounding
For the N5a and N2L confounded null worlds, I approve evaluating the false-approval rate of the complete, predeclared research decision rule.
That rule must include:

1. The frozen primary significance requirement.
2. The estimated annualized gross economic effect of at least +3%.
3. Any other previously frozen mandatory decision conditions.

The maximum acceptable false-approval rate is 2% per scenario.
This evaluates whether the research procedure wrongly promotes a candidate despite the absence of an independent OC-2 effect.
It does not establish that the F5 coefficient itself is unbiased or that latent-factor confounding has been eliminated.
Report the ordinary statistical rejection rate separately from the complete-rule false-approval rate.
3. Mandatory Treatment of Severe Confounding
Do not ignore N5b and N2L5.
These are especially important because they examine stronger measurement-error or latent-factor contamination.
For each of N5a, N5b, N2L and N2L5, report:

* Number of replications.
* Ordinary rejection rate at 1% and 5%.
* Complete-rule false-approval rate.
* Monte Carlo confidence interval.
* Estimated coefficient bias.
* Assumed confounding strength.
* The role of the +3% threshold in suppressing false approvals.
* Whether the method is identifiable with real-world observable controls.

Apply the same 2% full-decision false-approval threshold to the severe scenarios as a robustness requirement.
If either N5b or N2L5 exceeds 2%, the method must not receive an unrestricted A or B reliability classification.
Such a failure must block any recommendation to proceed directly to a real-return test. Unless the frozen classification protocol explicitly establishes a scientifically justified, owner-approved narrower outcome, classify the method as C — NOT VALIDATED for the intended broad claim.
Do not silently mark the severe scenarios as non-gating.
A limited claim such as "predictive beyond the observed measured controls" must not be presented as proof of independent alpha.
Remember that the previous upper-bound estimates of 1.6% and 4.4% were analytical projections, not observed v2 results.
4. Measure Two Different Types of Statistical Power
The final study must distinguish:
Power A — Statistical Test Power
Probability that the primary statistical test rejects the null when a planted effect is present.
Power B — Complete Decision-Rule Power
Probability that the planted effect passes all mandatory research qualification conditions, including the +3% estimated annualized gross effect threshold.
Report both for planted true gross effects of:

* +2% annually.
* +3% annually.
* +4% annually.
* +5% annually.

Use the approved noise and dependence regimes.
The complete-rule power is essential for evaluating whether the future research procedure is practically useful.
A statistical test with 80% rejection power does not necessarily provide 80% power for the full research decision.
In particular, when the true effect is exactly the +3% cutoff, the estimated-effect threshold may itself limit complete-rule power to roughly 50% under an approximately unbiased, symmetric estimator.
Do not report classification A — sufficiently powered — based solely on statistical-test power if the full decision rule is materially underpowered for the declared economic objective.
Preserve the +3% reference effect. Do not lower the cutoff or redefine the effect following the results.
Report sensitivity to the full-rule threshold without optimizing it.
5. Freeze the Final v2 Protocol Before Running
Update the v2 protocol to include this owner-approved decision.
Before the confirmatory evaluation:

1. Verify all 54 planned synthetic worlds and their exact classifications.
2. Verify the corrected N7 and N13 behavior.
3. Freeze the primary model, control transformations, standard errors and critical values.
4. Freeze all data-generating parameters.
5. Freeze the complete research decision rule.
6. Freeze the Tier 1 and Tier 2 gates.
7. Freeze the treatment of N5b and N2L5.
8. Freeze the classification precedence for A/B/C/D.
9. Freeze all planted-effect and power definitions.
10. Freeze seeds, replication counts and stopping conditions.
11. Commit the protocol, configuration, relevant code and SHA-256 hashes.

Engineering smoke tests are permitted, but no confirmatory rejection-rate or power result may be used to change the frozen protocol.
If you identify an unresolved conceptual inconsistency before the freeze, STOP and request clarification rather than choosing a favorable interpretation.
6. Execute Exactly One Confirmatory Evaluation
After all preparation and protocol checks pass, execute one complete v2 synthetic evaluation.
Do not:

* Tune the estimator between scenarios.
* Change the controls after examining outcomes.
* Adjust the noise to improve power.
* Change the statistical thresholds.
* Remove failed scenarios.
* Change the treatment of hidden confounding.
* Select the most favorable standard-error lag.
* Run another confirmatory version.

Technical retries are allowed only for documented infrastructure failures using the identical frozen scientific configuration.
Include every valid, failed or incomplete scenario in the final report.
7. Official Result
Return one official classification using the prospectively frozen rules:

* A — CALIBRATED AND SUFFICIENTLY POWERED: reliability and identification requirements pass, and the complete research decision has adequate power for the predeclared economically meaningful target.
* B — CALIBRATED BUT UNDERPOWERED: reliability requirements pass, but complete-rule power is inadequate.
* C — NOT VALIDATED: an essential false-positive or identification requirement fails.
* D — INSUFFICIENT EVIDENCE: required evaluations cannot be completed or interpreted reliably.

Do not use B when a reliability requirement fails.
Do not use A when only the statistical test, but not the complete decision rule, has adequate power.
Report any limitations of identifying an independent signal when hidden priced factors remain unobservable.
8. Deliverables
Complete:
OC-CP5 — OC-2 Synthetic Calibration v2
Include:

1. Verified decision ID and repository state.
2. Final frozen protocol and hashes.
3. Tier 1 false-positive results.
4. Tier 2 full-rule false-approval results.
5. Explicit N5a, N5b, N2L and N2L5 results.
6. Confirmation that all 54 worlds were accounted for.
7. Monte Carlo uncertainty.
8. Statistical-test power.
9. Complete-rule power.
10. Minimum detectable effects.
11. Comparison with v1.
12. Identification limitations.
13. Final A/B/C/D classification.
14. Exact recommendation for owner review.
15. Full reproducibility records.
16. Confirmation that no real returns or real F5 signals were used.
17. Confirmation that no QuantConnect runs or backtests were performed.
18. Confirmation that H028 was unchanged and the Holdout remained sealed.

Commit and merge through the existing repository PR workflow after tests pass.
9. Mandatory STOP
After completing OC-CP5:
STOP and return for owner review.
Even if the method passes, do not automatically:

* Run a real-return OC-2 test.
* Compute actual F5 stock rankings.
* Build a portfolio.
* Combine OC-2 with H028.
* Run SYS-1.
* Open the Holdout.
* Purchase data.
* Start another synthetic calibration.

This is the final approved OC-2 synthetic repair attempt.
If it fails, recommend closing OC-2 on the current data and methods.
If it passes, explain precisely what the method can establish, what remains unidentified, and whether one future real-data signal test is justified.
Our ultimate goal is still to find a credible, independent offensive stock-selection mechanism that may complement H028 and improve after-cost long-term terminal wealth relative to SPY.
Do not sacrifice statistical reliability merely to keep OC-2 alive.
