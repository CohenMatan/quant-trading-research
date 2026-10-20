# Owner decision D263 — RR2 controlled approval and universe baseline (2026-10-20)

**Context:**
- This follows RR2 (D261 / D262, `docs/checkpoints/RR2_qc_price_first_research_programme_proposal.md`, PR #122).
- The message is recorded verbatim below, before any design or run.

---

Owner Direction — RR2 Controlled Approval and Universe Baseline
I have reviewed RR2 and want to proceed using our existing QuantConnect subscription and data.
Our objective remains finding long-only US equity strategies that outperform SPY in long-term terminal wealth after realistic costs.
1. Programme Structure
I approve RR2's simplified research architecture in principle:

* Reuse the existing plain-text harness.
* One reusable engine instead of separate infrastructure for each hypothesis.
* Small, economically motivated, pre-registered research experiments.
* No post-result parameter optimization or rescue variants.
* Distinguish promising development results from independent validation.
* Keep the existing portfolio and transaction-cost assumptions.

Before the first strategy experiment, present the final candidate-screen and confirmation rules for freezing. Preserve the proposed P1–P6 gates unless a change is justified before seeing any new strategy results.
No strategy experiments are authorized yet.
2. Approve the Universe Baseline
I authorize one aggregate-only QuantConnect infrastructure run, with at most one retry for a documented infrastructure failure.
The run should examine U-A and U-B and determine whether reliable PIT market-cap coverage exists before 2010.
Before running, freeze the universe-audit definitions and pass/fail criteria.
The proposed maximum unrepaired missing-market-cap rate is 3% of eligible stock-months in every year, but this numerical threshold is not sufficient by itself.
The audit must also address survivorship bias explicitly:

* Compare subsequent delisting rates among missing-cap and observed-cap securities using comparable observation windows.
* Account for follow-up censoring; do not inspect the sealed 2022–2026 Holdout to establish later delisting.
* Report both security counts and stock-month counts.
* Report year-by-year coverage and the magnitude and uncertainty of any survivorship imbalance.
* Verify that reconstructed share counts were actually available at each historical decision date.
* Verify split adjustment consistency between share counts and prices.
* Distinguish agreement with vendor market cap from independent PIT validity.

Do not classify the universe as unbiased based solely on a low missing-data percentage or lack of statistical significance.
If the results are ambiguous or fail the pre-registered rules, STOP for owner review.
Do not automatically implement U-C or relax the universe requirements.
3. In-Cloud Evaluation
I approve computing SPY-relative performance metrics inside QuantConnect, with only permitted summary results exported through the supported backtest-results mechanism.
No underlying QuantConnect price histories, reconstructed benchmark series, encoded blocks or Platform Data may be exported.
If a required output is not compliant, STOP rather than bypass the restriction.
4. First Research Categories
My preferred first candidates are:

* K1 — Dividend-event drift.
* K2 — Market-trend exposure control.

Do not register or implement them yet.
Before freezing K1, demonstrate that every event is observable by the decision date, without announcement-date look-ahead or mechanical ex-dividend price distortions.
Before freezing K2, demonstrate that its broad-portfolio construction is feasible under our existing position-count, position-size and account constraints.
There is no obligation to fill all three hypothesis slots. K3 and K4 are not approved at this stage.
5. Confirmation Periods
If the universe audit establishes reliable 1999–2009 coverage, propose a separate amendment to D033 and D035.
Do not automatically amend those decisions.
1999–2009 may be used for prospective confirmation only after assessing earlier research exposure and obtaining separate owner approval.
The 2022-01-01 through 2026-08-31 Holdout remains sealed.
6. Execution Boundary
For now, execute only the approved universe-baseline infrastructure work.
Do not purchase services, access the Holdout, launch strategy backtests, implement the SEC fallback or change frozen historical experiments.
Record the decisions, freeze the audit criteria before the run, document the resulting aggregate findings and STOP for owner review.
Our next decision should be based on whether the current QuantConnect data can support trustworthy stock-universe construction, not on speculative strategy performance.
