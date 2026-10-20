# Owner decision D267 — RR4 review decisions (2026-10-20)

**Context:**
- This follows RR4 (D266, `docs/checkpoints/RR4_rr3_review_universe_risk_screen_k1_k2.md`, PR #124).
- The message is recorded verbatim below, before any work.

---

Owner Decisions — RR4 Review
I have reviewed RR4 and approve the following controlled next steps.
Our priority remains finding promising investment strategies using existing resources, without new purchases or unnecessary infrastructure.
1. UR-1 — Approve Option A
I approve the narrow, free SEC classification assessment described in RR4 §2.5.
Scope:

* Independently sourced SEC JSON only.
* QuantConnect identifiers and universe membership generated inside Cloud.
* One aggregate-only run and at most one documented infrastructure retry.
* No strategy returns or performance analysis.
* No QuantConnect Platform Data exports.
* No SEC-based universe repair under this authorization.
* No Holdout access.

Before running, freeze the measurement definitions and interpretation rules.
The audit must distinguish confirmed missing eligible securities, possible missing securities, matched securities and unresolved cases.
SEC public float is a lower-bound indicator, not an exact substitute for historical market capitalization. Ticker-matching failures must not be interpreted as proof of absence.
If the audit cannot establish that the relevant universe-bias risk is acceptably bounded, classify the outcome as INCONCLUSIVE or FAIL.
Do not automatically proceed to Option B, C or D. STOP for owner review.
If QuantConnect's compliance review rejects the audit, STOP without attempting a workaround.
2. Candidate Screen and Confirmation Rules
Approve the RR4 D1 and D2 screening framework in principle, including P1–P6 and the stricter development evidence test.
However, make two clarifications before freezing:
A. The existing 2022–2026 Holdout may be used for at most ONE programme candidate across the entire research programme, not one candidate per tranche. Any opening requires separate explicit written approval.
B. D1 and D2 are evaluated on heavily exposed development data. Passing either does not establish independently validated statistical significance or investable alpha. Holm adjustment for the new tranche does not erase the earlier programme-wide search history.
Keep the trial-history ledger and all limitations visible.
Also reconcile the cloud-run budget with the planned sensitivity tests so that no additional runs are implicitly authorized.
Prepare the corrected final protocol for freezing before any strategy return is calculated.
3. K1 — Conditional GO
Approve preparation of H031 based on dividend-event drift.
Authorize the event-count and timing canary only AFTER the universe decision has been resolved and its audit accepted.
No H031 strategy backtest is authorized yet.
The specification must pre-register:

* Dividend initiation and regular-increase definitions.
* Ex-date availability and next-session execution.
* Exclusion of special distributions, spin-offs and ambiguous cadence changes.
* Dividend adjustment and total-return handling.
* A fixed 126-session holding period.
* Position limits, queue selection and tie-break rules.
* Appropriate event-matched controls.
* Estimated costs and turnover.
* Research stopping conditions.

No performance-based parameter selection or rescue variations.
The event canary must export only permitted aggregate results, not returns or security-level data.
4. K2 — Drop From the Current Tranche
Accept RR4's recommendation not to register K2 under the current portfolio constraints.
Do not approve ETF exceptions, concentration exceptions or a redesigned 15-stock timing strategy.
Preserve K2 as a possible future separate research direction, not an active hypothesis.
5. Execution and Stopping Conditions
Proceed only with the narrowly approved UR-1 audit and the necessary documentation.
Do not:

* Purchase data or services.
* Open the Holdout.
* Run strategy backtests.
* Implement U-C.
* Reopen H028 or SYS-1.
* Relax the approved portfolio or universe constraints.
* Begin further infrastructure development outside the approved audit.

After the UR-1 results, report whether we have a sufficiently credible universe to start K1 research.
If the universe passes, present the final frozen-ready H031 specification and evaluation protocol for owner approval before executing the strategy.
Commit the documentation and audit evidence through the normal workflow, then STOP for my review.
