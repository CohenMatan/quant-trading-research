# Owner message — 2026-10-18 (D244)

**Scope recorded by Claude:** LH-CP3 — missing fiscal labels: recovery and validation.
- **Data:** SEC accounting-period metadata only, dated ≤ 2021-12-31.
- **Approach:** offline first. Then at most 150 targeted historical requests for SEC EDGAR filing headers on `www.sec.gov`:
  - at most 2 requests per second;
  - the existing authorised contact configuration, never committed;
  - the cut-off enforced before any request URL is built or any response is inspected.
- **Historical results unchanged:** LH-CP1 Stage C stays **C — NOT FEASIBLE**, and LH-CP2 stays **C — INSUFFICIENT EVIDENCE**.
- **Not approved:** returns, prices, OF-A signals or rankings, QuantConnect, backtests, Stage B, H028 / Ridge changes, Data v2.1 / v3 changes, P-assume as a default, H031, purchases or the Holdout.
- **Mandatory STOP** after the checkpoint.

The message follows verbatim.

---

Owner Approval — LH-CP3: Missing Fiscal Labels Recovery & Validation
Limited Offline Investigation + Targeted Historical SEC EDGAR Access
I approve LH-CP3 — Missing Fiscal Labels Recovery & Validation.
This checkpoint follows:

* D242 — LH-CP1, Stage C OF-A Data and PIT Feasibility Audit.
* D243 — LH-CP2, Fiscal Calendar Anomaly Resolution.
* The frozen long-horizon research architecture under D241.

The objective is to determine whether missing historical fiscal-quarter labels can be recovered or independently validated without introducing look-ahead bias or compromising accounting-period comparability.
I specifically authorize limited access to historical SEC EDGAR filing headers, subject to the restrictions below.
This is NOT approval to run Stage B, evaluate stock returns, revise prior decisions, or promote OF-A.
1. Verify the Repository
Before making changes:

1. Verify the current `main` branch, working tree and latest merged PR.
2. Confirm D243 is the latest owner decision unless additional legitimate changes have occurred.
3. Read the original LH-CP1 and LH-CP2 checkpoints.
4. Verify the hashes of both frozen protocols.
5. Inspect the existing Stage C and CP2 scripts, tests and aggregate artifacts.
6. Verify that H028 remains REJECTED and H029/H030 remain NOT EVALUABLE.
7. Confirm that no Holdout unlock exists.

Record this owner instruction verbatim under the next available owner decision ID.
Preserve all prior records.
2. Findings That Must Be Preserved
LH-CP2 established that:

* The original fiscal-year-end code check was over-inclusive and under-inclusive.
* Approximately 91% of the original 890 unexplained anomalies were metadata inconsistencies with consistent fiscal-quarter labels.
* The more significant outstanding problem is missing fiscal labels in approximately 13% of Stage C input-complete stock-month histories.
* Most missing labels arise from quarters before the registrant began XBRL reporting.
* Additional missing labels arise from incomplete local XBRL filing-index coverage.
* Excluding all histories with unknown labels drastically reduces 2013–2014 coverage.

Use the original artifact counts and exact denominators.
Do not conflate:

* All-registrant unique chains.
* Eligible-universe unique chains.
* Repeated eligible stock-month observations.

The official historical results remain:

* LH-CP1 Stage C: C — NOT FEASIBLE under the frozen protocol.
* LH-CP2: C — INSUFFICIENT EVIDENCE under its frozen protocol.

These classifications remain unchanged.
LH-CP3 is a new investigation, not a retrospective correction of those records.
3. Exact Authorization
Allowed
You may:

* Analyze historical SEC filing metadata available locally.
* Recover missing filing-index mappings using cached SEC submissions.
* Inspect original filing headers, accession identifiers, filing types, reporting period dates, fiscal-year-end metadata and fiscal-quarter indicators.
* Perform offline metadata validation.
* Use targeted historical SEC EDGAR requests under the limits in Section 4.
* Create audit scripts and deterministic unit tests.
* Produce aggregate completeness, reconstruction-accuracy and coverage statistics.
* Record results and create a PR.

Prohibited
Do NOT:

* Read or retrieve any filing dated after 2021-12-31.
* Access 2022–2026 Holdout information.
* Compute stock prices, stock returns or future performance.
* Compute any OF-A surprise signal, cross-sectional ranking or predictive statistic.
* Run QuantConnect.
* Run any backtest.
* Run Stage B synthetic inference validation.
* Modify H028 or Ridge.
* Change Data v2.1 or Data v3.
* Change the LH-CP1 or LH-CP2 result.
* Adopt P-assume automatically.
* Select OF-A signals or parameters.
* Start H031.
* Purchase data.
* Implement a trading strategy.
* Use new market-performance information to determine which fiscal histories to keep.

All activity is limited to accounting-period metadata and data integrity.
4. SEC EDGAR Network Restrictions
I authorize narrow historical SEC EDGAR access only when the locally cached data are insufficient.
4.1 Allowed source
Only official SEC EDGAR historical filing resources on:
`https://www.sec.gov/`
Prefer header-only or filing-index resources under the historical EDGAR Archives.
Do not use alternative providers, search engines, third-party financial data APIs or bulk downloads.
4.2 Historical cutoff
Every selected accession must be verified from locally available metadata as originally filed no later than:
2021-12-31.
The relevant information must also have been publicly available by the historical decision date for which it would later be used.
Do not retrieve later amendments to resolve an earlier period unless the amendment was already public by that historical decision date.
A filing that was historically unavailable must never be used to validate a decision-time observation.
Enforce the cutoff before constructing request URLs and before inspecting responses.
4.3 Request budget
For this checkpoint:

* Maximum 150 historical filing-header requests.
* No broad SEC archive crawling.
* No bulk ZIP or entire-universe downloads.
* Maximum 2 requests per second, with polite throttling and exponential backoff where appropriate.
* Use a properly configured SEC-compliant User-Agent and contact address from existing authorized configuration. Do not invent personal contact details.
* Cache permitted header responses for reproducibility.
* Log accession, URL, filing date, retrieval status and response metadata.
* Never commit credentials or other secrets.

If SEC denies access or blocks requests, stop the network portion and report the limitation.
Do not evade access restrictions.
4.4 Minimize downloaded content
Prefer header-only sources.
If a full historical submission is the only available format, read only the minimum header portion needed, using bounded streaming where possible. Discard the filing body without processing its financial statements.
Do not extract financial results, earnings values, stock prices or subsequent returns.
Do not request additional files automatically to overcome the request budget.
If 150 requests are insufficient, stop and request owner approval for expansion.
PART A — Offline Recovery First
5. Recover Missing XBRL-Index Mappings Locally
The LH-CP2 diagnostic identified missing labels caused by incomplete SEC XBRL index coverage even when local submissions records existed.
Start with these cases.
Use cached submissions to reconstruct:

* Original accession number.
* Form type.
* Filing date.
* Report period end.
* SEC registrant identity.
* Relationship to the existing Data v2.1 filing record.

Where possible, cross-reference original companyfacts entries without using later-filing information.
Do not manufacture `fp` labels merely because a filing is a 10-Q or 10-K.
A 10-Q identifies a quarterly filing, but determining whether it corresponds to Q1, Q2 or Q3 requires a defensible fiscal-period mapping.
Classify each recovery as:

* Verified: independently supported by eligible metadata.
* Inferred: consistent with the available sequence but not independently confirmed.
* Invalid: conflicting information.
* Unknown: insufficient evidence.

Do not automatically convert inferred labels into verified labels.
Report the local recovery rate before making network requests.
PART B — Historical EDGAR Header Investigation
6. Investigate Pre-XBRL Historical Filings
After offline recovery, identify the remaining unknown fiscal histories.
Focus on the pre-XBRL cases that affect eligibility in 2013–2014.
For each selected filing, examine only permitted metadata such as:

* Accession number.
* CIK.
* Filing type.
* Filing acceptance and filing dates.
* Conformed period of report.
* Fiscal-year-end metadata.
* Amendment or transition status.
* Any explicit fiscal-quarter information available in the original header.
* Period continuity with earlier filings that were already public.

Importantly:
An SEC filing header may identify the reporting period without explicitly identifying the fiscal-quarter label.
Do not claim that a quarter is independently verified if the header provides only an ambiguous fiscal-year-end code.
Distinguish what the header proves from what the reconstruction algorithm infers.
7. Pre-register the Network Sample
Before retrieving anything from EDGAR:

1. Define the eligible population of unresolved historical filings.
2. Specify deterministic selection rules and a fixed random seed where sampling is used.
3. Select a stratified sample covering different years, sectors, filing types and anomaly categories.
4. Include fiscal transitions and 52/53-week filers where relevant.
5. Include companies entering or leaving the investment universe.
6. Record the selected accession manifest and protocol hash.
7. Commit the protocol before fetching the selected filings.

The sample must not be chosen because certain companies are known to have performed well or poorly.
Do not expand or replace failed cases with more convenient ones after observing outcomes.
Keep the investigation small enough to remain within the 150-request limit.
If the selected filings cannot meaningfully answer the missing-label question, report that rather than broadening the scope silently.
PART C — Validate the Reconstruction Method
8. Artificially Hide Known Fiscal Labels
We need evidence that any reconstruction method is accurate, not merely plausible.
Use historical filings with known, verifiable fiscal-quarter labels.
For validation:

1. Select eligible histories with known labels.
2. Hide the labels that the reconstruction method is supposed to recover.
3. Preserve only the metadata fields that would actually be available in the missing-label situation.
4. Attempt to reconstruct the hidden labels.
5. Compare the results with the original labels.
6. Report correct, incorrect and abstained predictions.

The algorithm must not indirectly access the hidden labels through another derived field.
If the data used for validation contain more information than genuine pre-XBRL records, the resulting accuracy may be optimistic.
Explicitly assess that difference.
9. Development and Final Validation Must Be Separate
Use separate datasets for:

* Algorithm development and debugging.
* Final held-back reconstruction validation.

Freeze the final reconstruction rules before evaluating the held-back set.
Do not repeatedly tune the rule against final-validation errors.
Where possible, split by registrant rather than by repeated stock-month rows so that the same company's highly overlapping histories do not appear in both development and validation.
Assess different historical years and filing structures.
If no realistic held-back validation sample exists, classify the method as unvalidated.
10. Accuracy Requirements
Report:

* Number of attempted recoveries.
* Number of correct recoveries.
* Number of incorrect recoveries.
* Number of abstentions.
* Precision among accepted reconstructions.
* Recall or successful recovery rate.
* Error rate by filing type.
* Error rate by year.
* Error rate for 52/53-week companies.
* Error rate for fiscal-year transitions.
* Error rate for pre-XBRL-like conditions.
* Error rate for entrants and leavers.

Report confidence intervals accounting for independent registrants rather than treating overlapping histories as independent trials.
Propose conservative acceptance thresholds and freeze them before final validation.
The method should prefer abstention to a potentially incorrect fiscal-quarter reconstruction.
A high overall accuracy is insufficient if the small group of problematic fiscal-year transitions has a much higher error rate.
Do not claim zero true error simply because a sample contained zero observed mistakes.
PART D — Proposed Period-Validity Rule
11. Review LH-CP2 Rule P
LH-CP2 proposed a period-based validity rule rather than relying on fiscal-year-end-code equality.
Review its assumptions:

* Consistent quarter-end sequence.
* Proper accounting-period durations.
* Explicit transition filings.
* Consistent fiscal labels where known.
* Isolated versus persistent fiscal-label errors.
* SEC registrant identity continuity.
* Handling of missing labels.

Keep the rule as a proposal unless its accuracy is adequately demonstrated.
Specifically investigate whether allowing one isolated mislabeled quarter could mistakenly accept a genuine fiscal-calendar change.
Do not change the rule to improve coverage.
Any revised prospective rule must have independent accounting and PIT justification.
12. Separate Verified from Assumed Histories
For every complete candidate history, distinguish:

1. Verified valid: sufficient evidence that the seasonal quarters are comparable.
2. Verified invalid: demonstrated fiscal-period incompatibility or identity/mapping error.
3. Conditionally valid: inference supported by evidence but dependent on a stated assumption.
4. Unknown: insufficient evidence.

Do not silently treat conditional validity as verified validity.
Any future research must be able to identify which observations were retained under an assumption.
PART E — Impact on OF-A Coverage
13. Recalculate Input Coverage Without Calculating Signals
Using the existing frozen historical universe denominator, report the effects on:

* C1 — Earnings Surprise.
* C2 — Revenue Surprise.
* C6 — Dual Surprise.

Only measure whether all required inputs and period metadata are available.
Do not compute signal values.
Report annual input coverage for 2013–2021 under separate scenarios:
Scenario A — Strict verified-only
Include only histories that are confidently verified as comparable.
Scenario B — Verified plus validated reconstructions
Include reconstructed histories only where the method meets its frozen accuracy requirements.
Scenario C — Verified plus conditional assumptions
Report as a sensitivity analysis only, with clearly identified uncertainty. This is not automatically an approved research population.
Scenario D — Original LH-CP1 input coverage
Include the original result for reference, without changing it.
For each scenario provide:

* Eligible stock-month denominator.
* Included stock-month numerator.
* Percentage covered.
* Minimum coverage year.
* Impact on the provisional 70% floor.
* Changes in sector/size/age coverage.
* Entrant and leaver representation.
* Remaining uncertainty.

Preserve the distinction between the Data v1 universe denominator and the unexported Data v2.1 per-stock-month universe.
14. Assess Selection Bias
Missing fiscal labels may not be randomly distributed.
Report whether recovered and unrecovered histories differ in:

* Fiscal year.
* Sector.
* SEC registrant age.
* Eligible-universe entry/exit status.
* Company size, using permitted previously committed non-return aggregates.
* History depth.

Do not assume that recovering more records automatically improves representativeness.
The key question is whether the recovered histories reduce uncertainty without introducing new systematic bias.
PART F — Decision Framework
15. Final Classification
Return exactly one:
A — RECOVERY METHOD VALIDATED
A reproducible PIT-safe method has passed held-back validation, with clearly documented residual error and sufficient evidence for its permitted use.
Report the recovered coverage and limitations.
This does not automatically make OF-A feasible.
B — PARTIAL RECOVERY
Some labels can be reliably recovered, but other cases remain unresolved, or the validated method has limited coverage.
Explain the remaining restrictions.
C — METHOD NOT VALIDATED
The recovery method cannot be trusted sufficiently to classify historical periods.
D — INSUFFICIENT EVIDENCE
The available historical metadata or validation sample is inadequate to reach a conclusion.
Do not choose A merely because reconstructed coverage exceeds 70%.
PART G — Required Deliverables
16. LH-CP3 Checkpoint
Create:
LH-CP3 — Missing Fiscal Labels Recovery & Validation
Follow existing repository naming conventions.
Include:

1. Verified initial repository state.
2. Owner decision and authorized scope.
3. Historical classifications preserved.
4. Local-data sources and hashes.
5. Network source restrictions.
6. Cutoff-enforcement tests.
7. Frozen reconstruction protocol and hash.
8. Local submissions recovery results.
9. Pre-registered EDGAR sample manifest.
10. Exact SEC request count.
11. Filing-header information actually available.
12. Pre-XBRL recoverability.
13. Held-back reconstruction validation.
14. Accuracy, error rates and confidence intervals.
15. Fiscal-year-transition handling.
16. 52/53-week handling.
17. Proposed Rule P evaluation.
18. Verified, conditional, invalid and unknown classifications.
19. C1/C2/C6 coverage by year.
20. Provisional 70% floor comparison.
21. Missingness and selection-bias effects.
22. Residual uncertainty.
23. Final classification A/B/C/D.
24. Exact next owner decision.
25. Explicit confirmation that no stock-return analysis occurred.
26. Explicit confirmation that no post-2021 filing or Holdout information was accessed.

Commit all permitted reproducible scripts, tests, protocol and aggregate outputs through the normal PR workflow.
Do not replace the original Stage C or LH-CP2 artifacts.
PART H — Mandatory Stop
When LH-CP3 is complete:
STOP AND RETURN FOR OWNER REVIEW.
Do not:

* Reclassify Stage C.
* Grant an exception.
* Adopt P-assume as the default.
* Run synthetic inference tests.
* Choose final offensive signals.
* Change monthly versus filing-event trading.
* Build a portfolio.
* Backtest H028 or OF-A.
* Open the Holdout.
* Purchase data.
* Continue to the next checkpoint automatically.

Report which of these next steps you recommend:

1. Approve a narrowly defined Stage C exception using validated metadata rules.
2. Continue with a further limited investigation if an essential issue remains.
3. Restrict the usable research period rather than accepting uncertain historical records.
4. Stop OF-A on the existing data.

The recommendation must be supported by the actual audit evidence, not by a desire to advance the project.
Final Research Principle
Our aim remains a long-only US-equity system seeking greater terminal wealth than SPY over approximately 30 years, after costs and without leverage.
H028 remains a frozen defensive research reference with formal status REJECTED.
OF-A is still only a potential offensive research direction.
A valid historical data foundation is a prerequisite for testing it.
Do not sacrifice data integrity to preserve sample size, but do not discard useful history merely because an old metadata field was incorrectly interpreted.
