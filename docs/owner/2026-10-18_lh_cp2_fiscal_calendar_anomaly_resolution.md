# Owner message — 2026-10-18 (D243)

**Scope recorded by Claude:** LH-CP2 — fiscal-calendar anomaly resolution. Offline SEC metadata investigation ONLY (filings and data dated ≤ 2021-12-31, cut-off enforced before any record is inspected and tested). The LH-CP1 / Stage C result stays **C — NOT FEASIBLE** under the frozen protocol; this is not an exception, a reclassification or Stage B. No QuantConnect, backtest, returns, OF-A signals or rankings, H028 / Ridge change, Data v2.1 / v3 change, purchase, Holdout or 2022+ data. Mandatory STOP after the checkpoint. The message follows verbatim.

---

# Owner Approval — LH-CP2: Fiscal Calendar Anomaly Resolution

## Scope: Offline SEC Metadata Investigation Only

I approve a narrowly scoped investigation into the unexplained fiscal-year-end anomalies discovered during LH-CP1 (Stage C — OF-A Data and PIT Feasibility Audit).

**This is not approval to override the failed Stage C gate, reclassify the result, or start Stage B.**

The purpose is to determine whether the remaining fiscal-year-end anomalies represent genuine accounting-period incompatibilities, metadata artifacts, or unresolved data-quality problems.

---

## 1. Verify the Repository State

Inspect:

- D241 and D242.
- `docs/checkpoints/LH_CP1_stage_c_ofa_data_pit_feasibility_audit.md`.
- `research/longhorizon/stage_c/LH_StageC_protocol.md`.
- `research/longhorizon/stage_c/LH_StageC_audit.json`.
- `research/longhorizon/stage_c/LH_StageC_fye_diagnostic.py`.
- `research/longhorizon/stage_c/LH_StageC_fye_diagnostic.json`.
- Existing SEC filing and fiscal-period reconstruction rules.
- The frozen Data v2.1 and Data v3 definitions.

Verify that no relevant repository changes have occurred since PR #107.

Record this owner authorization under the next available decision ID.

Do not modify the original frozen Stage C protocol, its hash, results, or conclusion.

---

## 2. Preserve the Existing Stage C Result

The official LH-CP1 classification remains:

**C — NOT FEASIBLE under the original frozen protocol.**

The reason was a fiscal-year-end code consistency check allowing no more than 1% of input-complete histories to exhibit a code change.

The measured failure was approximately 8–15%, depending on the candidate.

The post-hoc diagnostic showed that:

- Many code changes were within seven days, consistent with 52/53-week fiscal calendars.
- Some larger changes were quarter-aligned.
- Approximately 1.3% of 13-quarter histories showed unexplained shifts greater than one month that were not quarter-aligned.

These figures should be verified against the committed artifacts.

**Do not erase the failure or retroactively replace the original criterion.**

The task is to understand the remaining anomalies, not to make Stage C pass.

---

## 3. Exact Authorization

You MAY:

- Read committed research documentation.
- Analyze existing offline SEC filing metadata through 2021-12-31.
- Inspect fiscal period end dates, filing dates, filing types, fiscal-year-end metadata, accession identifiers and PIT identity mappings.
- Write small offline diagnostic scripts and unit tests.
- Calculate aggregate anomaly classifications and coverage effects.
- Investigate representative pre-2022 metadata cases.
- Create an investigation checkpoint.
- Commit code, tests, aggregate outputs and documentation.
- Open or merge a PR using the repository's normal workflow.

You MAY NOT:

- Access any filing or data dated after 2021-12-31.
- Inspect the sealed 2022–2026 Holdout.
- Run QuantConnect.
- Run a backtest.
- Read or compute stock returns or strategy performance.
- Calculate real OF-A surprise signals or rankings.
- Run Stage B synthetic validation.
- Modify H028.
- Retrain Ridge.
- Modify Data v2.1 or Data v3.
- Change the original Stage C classification.
- Approve an exception to the failed criterion on my behalf.
- Purchase datasets.
- Implement OF-A or a combined strategy.

Use existing offline data only.

The earlier accidental inspection of two 2026 filing-metadata rows must not recur.

Enforce the 2021-12-31 cutoff before inspecting records, including diagnostic samples, and test that enforcement.

---

# PART A — Identify the Actual Anomalies

## 4. Reproduce the Existing Diagnostic

Reproduce the committed fiscal-calendar diagnostic without changing its definitions.

Confirm the approximate breakdown of 13-quarter histories:

| Fiscal-year-end metadata behavior | Previously reported |
|---|---:|
| Any code change | 10.4% |
| Shift of 7 days or less | 7.4% |
| Shift of 8–31 days | 0.8% |
| Shift greater than 31 days | 2.3% |
| Quarter-aligned shifts within the last group | 0.9% |
| Other unexplained shifts | 1.3% |

Report exact counts, denominators and rounding.

Important: distinguish unique fiscal-quarter chains from repeated stock-month observations of the same chain.

Explain whether the 1.3% figure uses the same denominator as the original Stage C gate.

Do not conflate the percentages.

---

## 5. Investigate the Unexplained Group

Focus specifically on the approximately 1.3% unexplained changes.

For each affected chain, examine the metadata needed to distinguish between:

### A. Legitimate 52/53-week calendars

Small fiscal-year-end date shifts, with otherwise consistent accounting-quarter boundaries.

### B. Genuine fiscal-year changes

The company actually changed its fiscal year or fiscal quarter structure.

### C. SEC metadata inconsistencies

The fiscal-year-end code changed, but the period-end dates and reporting sequence remain consistent.

### D. Quarter mapping problems

A fiscal quarter is associated with the wrong reporting period or filing.

### E. Registrant or identity changes

Potential successor/predecessor CIK problems, company reorganizations or incorrect historical mapping.

### F. Transition or amended filings

10-KT, 10-Q amendments or other filing patterns that could create misleading fiscal-calendar metadata.

### G. Unresolved

Cases that cannot be classified reliably from permitted metadata.

Do not force an explanation for every anomaly.

Any unresolved case remains unresolved.

---

## 6. Determine Whether Quarterly Comparisons Remain Valid

For each anomaly category, answer:

1. Are the actual quarter-end dates consistent?
2. Are the quarter durations compatible?
3. Does the original 80–100-day continuity rule detect the problem?
4. Are q0 and q4 truly comparable fiscal quarters?
5. For 13-quarter histories, are all seasonal comparisons valid?
6. Could the anomaly cause a mathematically incorrect surprise calculation?
7. Could it create a point-in-time violation?
8. Can it be safely excluded without changing any historical accounting data?

The critical distinction is:

**A change in the fiscal-year-end metadata code does not automatically mean the underlying financial periods are incomparable.**

Conversely, a chain of quarter ends that looks continuous does not necessarily prove the accounting periods are fully comparable.

Explain both cases carefully.

---

# PART B — Quantify the Impact

## 7. Measure the Actual Data-Quality Risk

For each category report:

- Number of affected histories.
- Percentage of affected histories.
- Unique registrants affected.
- Unique securities affected.
- Number of affected eligible stock-months.
- Years affected.
- Sectors affected.
- Whether the issue is concentrated in particular companies.
- Whether the issue occurs disproportionately for entrants or leavers.
- Whether a PIT risk exists.

Use aggregate results.

Do not compute returns or surprise values.

## 8. Effect of Excluding Unresolved Histories

Calculate the coverage impact of conservatively excluding:

1. Genuine fiscal-year changes that invalidate quarter comparisons.
2. Confirmed quarter-mapping errors.
3. All unresolved anomalies.

Report the effects separately and cumulatively.

Focus on:

- C1 — Earnings Surprise.
- C2 — Revenue Surprise.
- C6 — Combined Earnings and Revenue Surprise.

Report annual coverage for 2013–2021.

Compare it with the existing provisional 70% coverage floor.

Do not change the floor.

Also report any meaningful new coverage imbalance by sector, firm size, company age, entrant status or leaver status.

Do not claim that excluding a small fraction of histories automatically eliminates selection bias.

---

# PART C — Corrected Validation Design

## 9. Propose an Economically and Technically Meaningful Fiscal-Calendar Rule

After investigating the anomalies, propose a prospective fiscal-period validation rule based on:

- Actual accounting period start and end dates, where available.
- Fiscal quarter duration.
- Comparable same-quarter reporting periods.
- Consistent historical quarter ordering.
- Known fiscal-calendar transitions.
- PIT availability.
- Conservative treatment of ambiguity.

Avoid using fiscal-year-end code equality as a substitute for validating the actual accounting periods.

The rule must specify:

- When an observation is valid.
- When it is invalid.
- When it is unknown.
- How unknown cases are handled.
- How genuine fiscal-year transitions are handled.
- How 52/53-week calendars are handled.

Include small illustrative metadata cases and unit-test expectations.

This is a **proposal for a future Stage C exception or amendment**, not permission to apply it to the frozen original result.

## 10. No Retrospective Threshold Optimization

Do not choose a rule simply because it produces coverage above 70%.

Do not adjust the unexplained-anomaly tolerance to make the test pass.

If a conservative period-based rule can eliminate demonstrably invalid comparisons, explain the rationale independently of the resulting coverage.

Separate:

- Objective accounting-period validity.
- Arbitrary numerical thresholds.
- Missing-data and coverage consequences.

The original Stage C failure remains recorded.

Any future acceptance of a revised rule requires an explicit owner decision.

---

# PART D — Decision Report

## 11. Required Final Classification

Conclude the investigation with exactly one:

### A — ANOMALIES SUFFICIENTLY EXPLAINED

The previously unexplained cases have credible metadata explanations or can be excluded through an independently justified, PIT-safe period-validity rule.

Residual uncertainty and coverage loss are reported.

This supports considering a future owner-approved Stage C exception.

It does not itself change Stage C from C to B.

### B — MATERIAL UNRESOLVED PROBLEMS

The investigation identifies genuine fiscal-period inconsistencies or remaining uncertainty substantial enough to compromise the proposed surprise calculations.

Report affected coverage and precise blockers.

### C — INSUFFICIENT EVIDENCE

Available offline metadata cannot distinguish valid fiscal-period changes from problematic ones.

Report what would be needed for resolution, without taking unauthorized actions.

---

## 12. Required Checkpoint

Create:

**LH-CP2 — Fiscal Calendar Anomaly Resolution**

Follow repository naming conventions.

Include:

1. Repository verification.
2. Owner authorization and exact scope.
3. Original LH-CP1 failure preserved.
4. Source and cutoff verification.
5. Reproduction of the anomaly counts.
6. Denominator reconciliation.
7. Anomaly classification methodology.
8. Classification results.
9. Representative metadata-only examples.
10. Fiscal-quarter comparability findings.
11. PIT implications.
12. Candidate C1/C2/C6 coverage effects.
13. Sector/size/age/entrant/leaver effects.
14. Residual unresolved cases.
15. Proposed corrected calendar-validity rule.
16. Unit-test results.
17. Limitations.
18. Final classification A/B/C.
19. Exact owner decision required next.
20. Confirmation no returns, backtests, QuantConnect runs or Holdout data were used.

Preserve all frozen artifacts.

Commit the checkpoint and its reproducible diagnostic code through the normal PR process.

---

# PART E — Mandatory STOP

After completing LH-CP2:

**STOP AND RETURN FOR OWNER REVIEW.**

Do not automatically:

- Reclassify Stage C.
- Accept an exception.
- Begin Stage B.
- Select C1/C2/C6.
- Change monthly versus filing-event review frequency.
- Compute any signal.
- Run a backtest.
- Touch H028.
- Open the Holdout.

The next decision is mine.

If the investigation supports a corrected data-validity rule, present a narrow owner-approval proposal that preserves the frozen Stage C failure.

The broader investment objective remains unchanged:

**A long-only US-equity system that seeks greater terminal wealth than SPY over approximately 30 years, after costs and without leverage.**

H028 remains the Frozen Defensive Research Reference, with formal status REJECTED.

No new production candidate exists.
