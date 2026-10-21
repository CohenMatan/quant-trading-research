# Owner decision D278 — OS-CP1 Revision 1 decisions (2026-10-21)

**Context:**
- This follows OS-CP1 Revision 1 (D277, §11 of `docs/checkpoints/OS_CP1_offensive_score_candidate_selection_first_experiment_design.md`, PR #129).
- The message is recorded verbatim below, before any work.

---

Owner Decisions — OS-CP1 Revision 1
I have reviewed Revision 1 and agree with the revised three-stage stock-selection approach:
Financial quality filters → Net share reduction ranking → Top 15.
I want to move toward the first legitimate strategy experiment using only our existing resources, without compromising point-in-time integrity or introducing another large research infrastructure project.
1. Approve the Revised Filters
Approve:

* F-OCF: Latest available fiscal-year operating cash flow > 0.
* F-REV: Latest available fiscal-year revenue growth > 0.
* Primary ranking: The original 12-month split-adjusted net share reduction score.

The two financial metrics are eligibility filters, not additional weighted scoring factors.
Do not optimize thresholds or introduce learned weights.
Keep the distinction clear: positive operating cash flow does not prove that repurchases were funded entirely from operations, and positive revenue growth does not establish future stock outperformance.
2. Approve Fiscal-Year Measurements, Subject to Verification
Approve using the latest eligible 10-K / 10-KT rather than reconstructing rolling-quarter TTM values.
Before freezing the specification, verify that the prior-year revenue comparative can actually be extracted from the same filing with adequate coverage. The offline study used consecutive annual filings and therefore has not yet verified this exact implementation.
Use only information available by each historical decision date, with explicit filing-date and accounting-period checks.
Do not silently fall back to a different definition if the proposed comparative is missing.
3. Approve Excluding Financials and REITs
For H032, approve the exclusion of SIC 6000–6799.
Use the latest point-in-time SEC industry classification available at the decision date.
Report the proportion of otherwise eligible companies removed by this restriction and any resulting sector concentration.
This is a scope decision for H032 only, not a permanent change to the overall programme's equity universe.
4. Coverage Gates — Conditional Approval
Approve G-COV1–3 in principle, with the following clarifications:

* The offline study's public-float population is not identical to our actual repaired QuantConnect universe.
* The canary must measure the full joint coverage on the actual eligible non-financial universe.
* Preserve the proposed 70% starting threshold and 65% minimum ongoing coverage.
* Report coverage for vendor-only securities, SEC-restored securities and later-disappearing companies.
* Where the 24-month future-exit comparison cannot be assessed without accessing the sealed Holdout, report it as censored or unevaluable. Do not access the Holdout or silently treat the gate as passed.
* Future exit information must be used only for retrospective audit diagnostics, never for historical security selection.

Keep the subperiod boundary fixed at 2016. Do not change the start threshold or boundary based on strategy performance.
If the first subperiod is too short for a meaningful evaluation, report that before any return analysis and STOP for my decision.
5. Approve the Decomposition Controls
Approve B0, B2 and the extended O5 gate:

* B1: Filtered net-share-reduction Top-15 strategy — primary.
* B0: Original unfiltered net-share-reduction strategy — diagnostic only.
* B2: Five random Top-15 portfolios drawn from the same filtered eligible pool.
* Existing SPY, equal-weight, random, beta-matched and vendor-universe comparisons remain in place.

Use consistent timing, account constraints and costs across comparable portfolios.
Clarify that beating filtered random portfolios supports the incremental ranking hypothesis, but does not independently prove that the filters improve the original strategy.
B0 must never be promoted if B1 fails.
The original vendor-universe shadow comparison must apply the same approved financial filters where the underlying SEC data is available.
6. Approve One Extended SEC Object
I approve preparing and uploading one extended plain-JSON SEC object using only the existing independently sourced public SEC cache.
The extension may contain the minimum operating cash flow, revenue, prior-year comparative and PIT SIC data needed for H032.
No purchase, additional data source, QuantConnect Platform Data export or new identity-repair project is authorized.
Preserve and document the original SEC object and its hashes. Keep the extended version separate and reproducible.
7. Next Execution Stage
Proceed with the minimum implementation necessary for the revised OS-1 design, including offline tests.
Once the data definitions and coverage-gate semantics have been verified, freeze H032 and its evaluation protocol before calculating any strategy returns.
Then run ONLY the aggregate-only C-OS1 canary, with at most one documented infrastructure retry.
The canary must verify:

* Point-in-time accounting and identity.
* Same-filing revenue comparatives.
* Annual OCF and revenue coverage.
* Correct share-count and split adjustments.
* Actual repaired-universe coverage.
* Coverage gaps for restored and later-disappearing securities.
* The mechanical development start date and subperiod lengths.
* Shadow-book feasibility and determinism.

No strategy returns, R1/R2 backtests or Holdout access are authorized.
If the canary fails a frozen gate, or the exact approved data definitions prove unavailable, STOP rather than redesigning the strategy or relaxing thresholds.
Record the owner decisions, commit the work through the normal workflow, publish the canary checkpoint and STOP for my review.
H031 remains parked. RR6 remains INCONCLUSIVE. All future H032 results remain EXPLORATORY unless independently validated.
Our objective is to test whether selecting cash-generating, growing companies with meaningful net share reduction can outperform SPY after realistic costs—not to create another unrestricted factor-search programme.
