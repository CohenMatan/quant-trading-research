# Owner message — 2026-10-18 (D242)

**Scope recorded by Claude:** Long-horizon programme **Stage C — OF-A data and point-in-time feasibility audit**, a NON-RETURN data audit.
- The research order changes: Stage A complete (D241) → **Stage C approved now** → Stage B (synthetic validation) **NOT yet approved**.
- **Allowed:** reading committed artifacts; offline, non-return audits of permitted 2011–2021 development data (aggregate coverage, completeness, vintage, filing timing, data quality); small audit scripts and tests; public SEC metadata; a checkpoint, aggregates and a PR.
- **Not allowed:**
  - stock returns, backtests, wealth, CAGR or Sharpe; comparing returns with accounting data;
  - models; real OF-A surprise scores, percentiles or rankings; any predictive relationship;
  - Stage B, null worlds, H028 reruns;
  - modifying Data v3 or any frozen result; H031; purchases;
  - 2022–2026 data or the Holdout;
  - a new QuantConnect research run without separate approval.
- **Mandatory STOP** after the checkpoint.

The message follows verbatim.

---

# Owner Approval — Stage C Before Stage B
## OF-A Fundamental Surprise: Point-in-Time Data and Signal Feasibility Audit

### Objective

I approve **Stage C — Data and Point-in-Time Feasibility Audit** as the next checkpoint in our long-horizon Defensive + Offensive research programme.

This explicitly changes the proposed research sequence:

**Stage A — Architecture Design: COMPLETE (D241)**

**Stage C — Data & PIT Feasibility: APPROVED NOW**

**Stage B — Synthetic Statistical Validation: NOT YET APPROVED**

The reason for changing the order is simple:

Before investing resources in a sophisticated statistical inference method, we must establish that the fundamental information required for OF-A is actually available at a sufficiently early, reliable and point-in-time-correct date to support a potentially useful trading signal.

This is a **non-return data-feasibility audit**, not an investment-performance experiment.

---

## 1. Existing Research Governance

First inspect the latest repository state and confirm:

- D240: Previous research cycle closed.
- D241: H028 Defensive Reference + Offensive Companion architecture design.
- RM1 and RM2 research roadmaps.
- Data v3 and its frozen manifest (D230).
- Event Data v1 and 8-K Item 2.02 mapping.
- P14-CP1 and P14-CP2 fundamental-data coverage audits.
- P7-CP5c filing-availability and timing research.
- Relevant data-source, PIT, restatement and SEC identity checks.

Confirm:

- H028 remains REJECTED.
- H029/H030 remain NOT EVALUABLE.
- No new hypothesis is active.
- The 2022–2026 Holdout is sealed.
- No previous experiment, data version or frozen result may be changed.

Record this message as a new owner decision.

---

## 2. Exact Authorization

### Allowed

You may:

- Read committed research artifacts and specifications.
- Inspect existing Data v3 and Event Data v1 source metadata through permitted read-only access.
- Perform offline, non-return audits over the permitted historical development data.
- Compute aggregate coverage, completeness, vintage, filing-timing and data-quality statistics.
- Develop small audit scripts if needed.
- Consult historical public SEC documentation for definitions and metadata, without pulling future information into the frozen PIT panel.
- Write tests for audit correctness.
- Create and commit a checkpoint, scripts, aggregate reports and a PR.

### Not allowed

You may NOT:

- Run a stock-selection backtest.
- Compute future stock returns.
- Compare subsequent stock returns with accounting information.
- Calculate strategy wealth, CAGR or Sharpe.
- Train a model.
- Calculate real OF-A surprise scores, percentiles or rankings.
- Evaluate any predictive relationship.
- Run the Stage B synthetic suite.
- Run null worlds.
- Run H028 again.
- Modify Data v3, its manifest or any historical research result.
- Start H031.
- Purchase data.
- Access 2022–2026 data.
- Open the Holdout.
- Start a new QuantConnect research run without separate owner approval.

Prefer existing committed datasets and audit aggregates.

**If the necessary underlying data are not available offline, report the limitation instead of silently obtaining them through a new QuantConnect run.**

No automatic advancement to Stage B.

---

# PART A — Fundamental Data Availability

## 3. Audit the Required Accounting Fields

The proposed OF-A family currently considers:

- Quarterly revenue.
- Quarterly net income.
- Quarterly gross profit.
- Historical revenue growth.
- Historical earnings changes.
- Seasonal earnings and revenue expectations.
- Fundamental acceleration.

Use the existing Data v3 field definitions.

Audit, for each field:

1. Historical start date.
2. Historical end date.
3. Percentage of eligible companies covered.
4. Percentage of eligible stock-months covered.
5. Missing values by year.
6. Consecutive-quarter availability.
7. SEC identity availability.
8. PIT timestamp availability.
9. Restatement-guard effects.
10. Abnormal or non-comparable reporting cases.

Report coverage separately for:

- 2011–2014.
- 2015–2017.
- 2018–2021.

Also provide year-by-year results.

Use the frozen, point-in-time eligible-universe denominator when available.

Do not substitute surviving companies at the end of the period for the historical universe.

If reconstructing that denominator requires new price-data access or an unapproved run, explicitly report that limitation.

## 4. Historical Data Consistency

Verify the previously documented findings, including:

- The Data v3 restatement guard.
- Fourth-quarter calculation from annual minus nine-month values.
- Fiscal period matching.
- Quarter duration.
- Inconsistent fiscal calendars.
- Missing quarters.
- Late revisions.
- The availability rules used by the existing pipeline.

Specifically investigate whether accounting values known later were ever allowed to replace earlier values before their public availability.

Use the committed PIT audits where possible.

Any newly detected issue must be documented without changing the frozen data.

---

# PART B — Earnings Release vs Financial Filing

## 5. Determine When the Market First Receives the Information

This is the most important part of the audit.

Our existing sources include:

**8-K Item 2.02 events:** earnings announcements, with SEC acceptance timestamps.

**10-Q / 10-K filings:** structured financial values usable by Data v3.

These are not necessarily published at the same time.

Investigate the timing relationship between them.

For each fiscal quarter with enough metadata, identify:

- Fiscal period end.
- First matching earnings-release 8-K acceptance time.
- 10-Q or 10-K acceptance time.
- First valid Data v3 availability timestamp.
- First legal next-open trading opportunity after Data v3 availability.
- First scheduled monthly review after availability.

All dates must respect the existing PIT and execution rules.

Do not assume that an SEC filing acceptance date is identical to the first moment investors knew the accounting values.

Do not assume every Item 2.02 8-K corresponds unambiguously to the same quarter.

Use a defensible matching policy and report uncertain matches separately.

## 6. Measure the Information Delay

Calculate the distribution of:

**A. Fiscal period end → Earnings Release**

**B. Earnings Release → 10-Q / 10-K**

**C. 10-Q / 10-K → Data v3 availability**

**D. Data v3 availability → First scheduled portfolio review**

**E. Earnings Release → First possible trade using the proposed OF-A data**

For each provide:

- Number of matched events.
- Median.
- Mean.
- 10th percentile.
- 25th percentile.
- 75th percentile.
- 90th percentile.
- 95th percentile.
- Missing-event rate.
- Ambiguous-match rate.

Measure delays in calendar days and trading sessions where appropriate.

Clearly distinguish dates from timestamp-based trading availability.

## 7. Monthly Rebalancing Delay

The existing research assumes monthly reviews.

Determine how much additional delay this introduces after the fundamental values become available.

For example:

If a 10-Q becomes available two days after a monthly review, the strategy may have to wait nearly another month before trading.

Report:

- Median wait until the next review.
- 90th-percentile wait.
- Percentage of observations used within 5, 10, 20 and 30 trading sessions after data availability.
- Percentage of filings whose information is too stale under the proposed one-quarter freshness rule.

These are **timing and operational measurements only**.

Do not calculate whether trading earlier would have earned more money.

---

# PART C — Can We Calculate a Real Surprise?

## 8. Examine Proposed OF-A Signal Families

Review RM2 candidate definitions:

- C1 — Standardized Unexpected Earnings, Net Income.
- C2 — Standardized Unexpected Revenue.
- C3 — Price-scaled accounting surprise.
- C4 — Growth acceleration.
- C5 — Gross-profit surprise.
- C6 — Dual earnings-and-revenue surprise.

Do not select or implement a real signal yet.

For each candidate, identify:

- Required fields.
- Required historical quarters.
- Required timestamps.
- Scaling requirements.
- Expected minimum history.
- Sensitivity to restatements.
- Sensitivity to negative or zero denominators.
- Fiscal-seasonality issues.
- Whether the formula genuinely measures unexpected information or merely a historical change.

In particular, distinguish:

**Accounting surprise relative to a historical forecast** from **surprise relative to market expectations**.

Without analyst-consensus or earnings-release values, these are not interchangeable.

## 9. Historical-Chain Sufficiency

The original C1/C2 proposals mention a forecast using historical seasonal differences.

Check the precise historical requirements mathematically.

Do not assume that "eight prior seasonal differences" requires only eight previous quarterly observations.

For example, a seasonal difference may itself require values four quarters apart.

For each candidate, determine the earliest fiscal quarter for which the complete predictor history would have been available under the exact proposed formula.

Then count input-eligible observations without computing their surprise values.

Report:

- Number of available complete histories.
- Percentage of eligible companies.
- Percentage of eligible stock-months.
- Coverage by year.
- Reasons for missing histories.
- Whether fiscal-year changes invalidate the comparison.
- Impact of requiring contiguous quarters.
- Impact of varying allowed lookback completeness.

Do not choose shorter lookbacks simply because they improve historical coverage.

Alternative lookbacks can be documented as design options requiring separate pre-registration.

## 10. Earnings-Release Information Leakage

Assess the following question explicitly:

**By the time a 10-Q or 10-K becomes available in Data v3, has the underlying surprise information already been publicly announced?**

You cannot establish whether prices already absorbed the information without studying returns, which is prohibited here.

But you can establish:

- How often an earlier matched Item 2.02 announcement exists.
- The length of the delay.
- Whether the structured field values appear in that earlier release.
- Whether the existing data source captures those earlier values in machine-readable form.
- Whether a filing-date signal is necessarily a delayed accounting-information signal.

Do not claim that the information is economically stale merely from elapsed time.

Instead distinguish:

1. Information definitely known earlier.
2. Information potentially known earlier.
3. Information first verifiable through the structured filing.
4. Cases that cannot be determined.

If evaluating 8-K exhibit contents would require a new unstructured extraction system, do not build it. Report the dependency.

---

# PART D — Data Integrity

## 11. Restatements and Reporting Irregularities

Assess the existing controls for:

- Revised financial statements.
- Values restated after the original filing.
- Annual versus quarterly reporting.
- Fourth-quarter derivations.
- 52/53-week fiscal years.
- Fiscal-calendar changes.
- Missing disclosures.
- SEC identity problems.
- Incorrect share-count adjustments.
- Negative or unusually volatile net income.
- Discontinued operations and major non-recurring items.

Avoid introducing new data-cleaning rules during this audit.

If a rule would be required for a future signal, document it as a prospective design decision.

## 12. Survivorship and Selection Bias

Verify that a proposed OF-A signal would not rely only on firms that survived until the end of 2021.

Report:

- Existing known survivorship limitations.
- Historical accounting coverage for companies entering or leaving the eligible universe.
- Missing-data patterns by company size and sector.
- Whether companies with weak financial disclosures are disproportionately excluded.
- Whether fiscal-history requirements create additional selection bias.

Do not infer that missing data are random without evidence.

---

# PART E — Feasibility Criteria

## 13. Freeze the Audit Protocol Before Computing New Aggregates

Before calculating new feasibility statistics, create and commit a clear audit protocol specifying:

- Historical scope: 2011–2021 only.
- Source versions.
- Population denominator.
- Quarter-matching methodology.
- Earnings-release matching methodology.
- Availability timestamp conventions.
- Signal-input sufficiency rules.
- Missing-data treatment.
- Coverage and timing metrics.
- Proposed feasibility thresholds.
- Known limitations.

Do not use new audit results to select more favorable definitions.

For coverage, start from RM2's proposed floor:

**At least 70% eligible stock-month coverage per year after 2012.**

Report separately whether each candidate can meet this floor under its full historical-input requirements.

Because that value was originally a proposal rather than an approved final gate, label it:

**PROVISIONAL FEASIBILITY THRESHOLD — OWNER REVIEW REQUIRED.**

Also report sensitivity around the floor descriptively, without changing it to produce a PASS.

## 14. Define Meaningful Timing Criteria

Do not arbitrarily decide that a signal is viable simply because its accounting data exists.

Provide separate judgments on:

**Data completeness:** Can the proposed signal be computed?

**Point-in-time integrity:** Would the calculation use only information known at the time?

**Information timeliness:** How much time passes between the first public disclosure and the earliest possible implementation?

**Practical computability:** Can the calculation be supported with the existing QuantConnect and Data v3 setup?

**Economic usefulness:** NOT TESTED in this stage.

Do not confuse these judgments.

A data audit cannot demonstrate that an information delay is profitable or unprofitable.

---

# PART F — Decision Framework

## 15. Provide a Candidate Feasibility Matrix

For each of C1–C6 include:

| Attribute | Required conclusion |
|---|---|
| PIT correctness | PASS / FAIL / UNKNOWN |
| Input coverage | Measured percentage or unavailable |
| Historical-depth sufficiency | PASS / FAIL / UNKNOWN |
| Data timestamp quality | PASS / FAIL / UNKNOWN |
| Earnings-release delay | Quantified |
| Quarterly-chain integrity | PASS / FAIL / UNKNOWN |
| Restatement risk | Described |
| Lookahead risk | Described |
| Ability to calculate without purchase | YES / NO / CONDITIONAL |
| Suitability for later signal research | FEASIBLE / CONDITIONAL / NOT FEASIBLE |

No candidate is declared predictive or profitable.

Do not choose final C1/C2/C3 formulas.

That selection requires another owner decision after the audit.

## 16. Critical Decision Question

Answer:

**Is there sufficient, reliable, point-in-time historical information to justify building and statistically testing an OF-A accounting-surprise signal with our current data and execution frequency?**

Provide one of:

### A — DATA FEASIBLE

At least one independently justified signal family has adequate coverage, correct availability handling and no unresolved material PIT blocker.

Timing limitations are disclosed.

This authorizes nothing automatically.

### B — CONDITIONALLY FEASIBLE

The necessary fields largely exist, but material issues remain with historical depth, earnings-release timing, coverage or implementation.

List precise blockers.

### C — NOT FEASIBLE

The current data cannot support a credible, PIT-correct accounting-surprise signal under the proposed requirements.

Further work would require new data, a different hypothesis or a change in project constraints.

### D — INSUFFICIENT EVIDENCE

The permitted offline artifacts do not support a reliable feasibility decision.

Identify exactly what cannot be determined without further approved access.

**Do not turn missing evidence into a PASS.**

---

# PART G — Required Checkpoint

Create:

**Long-Horizon Stage C — OF-A Data and Point-in-Time Feasibility Audit**

Include:

1. Repository state and owner approval.
2. Audit protocol and protocol hash.
3. Sources and Data v3 manifest.
4. Existing Data v3 field coverage.
5. Quarterly continuity results.
6. Candidate C1–C6 input sufficiency.
7. Coverage by year and historical period.
8. Fiscal-calendar irregularities.
9. Quarter-four derivation issues.
10. Restatement and vintage controls.
11. SEC identity consistency.
12. 8-K Item 2.02 matching methodology.
13. Earnings-release matching coverage.
14. Release-to-filing delay.
15. Filing-to-Data-v3 delay.
16. First legal execution availability.
17. Monthly-review waiting times.
18. Data freshness at review.
19. Whether information was previously disclosed.
20. Point-in-time integrity evidence.
21. Survivorship and missingness risks.
22. Candidate-by-candidate feasibility matrix.
23. Comparison with the provisional 70% floor.
24. Feasibility classification A/B/C/D.
25. What remains unknown about economic usefulness.
26. Required next owner decision.
27. Explicit confirmation that no stock-return or investment-performance analysis was conducted.
28. Explicit confirmation the Holdout remained sealed.

Use existing repository naming conventions rather than inventing a conflicting checkpoint identifier.

Preserve all original hypothesis files and frozen manifests.

Commit the permitted audit code, aggregates and checkpoint to GitHub through the normal PR workflow.

---

# PART H — Mandatory STOP

After completing the audit:

**STOP AND RETURN FOR OWNER REVIEW.**

Do not proceed automatically to Stage B.

Do not implement OF-A scores.

Do not select the final two signals.

Do not build an offensive portfolio.

Do not combine anything with H028.

Do not access the Holdout.

Do not modify the already-approved research budget or turn the proposed F1–F6 fragility screens into binding gates.

The next decision belongs to the owner.

Our ultimate objective remains a long-only investment system capable of accumulating more terminal wealth than SPY over approximately 30 years.

This checkpoint answers only whether the OF-A information required for that objective is sufficiently available, timely and trustworthy to justify the next stage.
