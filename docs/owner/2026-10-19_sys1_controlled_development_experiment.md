# Owner decision D252 — SYS-1 Controlled Development Experiment (2026-10-19)

**Context:**
- This follows D251 / OC-CP6 (`docs/checkpoints/OC_CP6_oc2_closure_corrected_sys1_design.md`; protocol `research/longhorizon/sys1/SYS1_protocol_PROPOSED.md`; merged in PR #116, main 924f1fc).
- The message is recorded verbatim below.

---

Owner Approval — SYS-1 Controlled Development Experiment
I have reviewed OC-CP6 and `SYS1_protocol_PROPOSED.md`.
I approve the following choices for SYS-1 only, subject to the clarifications and stop conditions below.
Record this as the next available owner decision after D251, after verifying the repository.
Approved decisions
OD-1 — ETF exception: Option (a)
For SYS-1 only, unleveraged diversified ETFs SPY, SPLV and USMV:

* Do not count against the 15-stock-position limit.
* Are exempt from the 10% single-position weight cap.
* Remain subject to cash sufficiency, no borrowing, commission, slippage and execution rules.

The maximum of 15 stock positions, $5,000 minimum new stock position and 10% initial stock-position cap remain unchanged.
This is not a programme-wide amendment and does not retroactively change earlier experiments.
OD-2 — Capital: Option (a)
Approve $200,000 initial capital for SYS-1 only.
The programme baseline remains $100,000.
Results obtained at $200,000 must not be represented as achievable at $100,000.
OD-3 — Execution: E1, research only
Use the frozen H028 shadow-book convention to maintain development-period comparability.
However, explicitly classify E1 as an idealized research execution model, not validated real-world implementation.
Fractional notional execution, dividend treatment, delisting conventions and absence of gap reserve remain limitations.
Any later real-money implementation would require separate approval and whole-share/cash-reserve feasibility validation.
OD-4 — ETF comparator
SPLV is the designated transparent ETF defensive comparator.
USMV is non-gating and diagnostic only.
Verify both through the canary.
If SPLV cannot pass the historical-data requirements, STOP before the evaluation. Do not silently remove the comparator, substitute USMV, or relax FS-6.
OD-5 — Allocation: Option (a)
Use the predefined 50% account-equity basis for new defensive-stock purchases at each monthly review.
SPY absorbs residual available cash after correctly sequenced stock and ETF trades.
Do not describe the strategy as maintaining exactly 50/50 invested weights throughout the month or after every review.
Report actual defensive-stock, SPY and cash allocations.
OD-6 — Falsification screens: Option (a)
Use FS-1 through FS-6 as frozen development-period falsification screens.
Permitted classifications are:

* NOT EXECUTABLE.
* NOT SUPPORTED.
* NOT FALSIFIED — DEVELOPMENT-CONSISTENT.

No result may be described as QUALIFIED, VALIDATED or proof of persistent alpha.
A failure applies to the specific tested architecture. It does not disprove every defensive allocation.
A pass does not authorize opening the Holdout.
OD-7 — Conditional execution approval
Authorize:

1. One canary, E032-01.
2. One evaluation, E032-02, only if every mandatory canary check passes.

Allow at most two documented infrastructure retries using identical frozen scientific settings.
No additional experiments, allocation variations, signal modifications or optimization runs are authorized.
Mandatory pre-freeze clarifications
Before creating any result, resolve and test the following implementation details.
1. H028 reproduction versus combined-account behavior
Require exact frozen H028 reproduction in standalone canary mode.
For the combined account, disclose and quantify any differences caused by:

* Cross-sleeve capital allocation.
* The $5,000 minimum-position overlay.
* Skipped purchases.
* Cash constraints.
* Dynamic account equity.
* SPY absorption trades.

Do not claim that the combined sleeve reproduces the exact frozen H028 equity curve.
2. Cash-ledger sequencing
Specify deterministically:

* Order of stock sales, ETF sales, stock buys and ETF buys.
* Treatment of commission and slippage before determining available cash.
* What happens when planned purchases exceed available cash.
* Handling of stock positions whose calculated new ticket is below $5,000.
* Treatment of residual cash.
* Prevention of negative cash and borrowing.

No hidden financing or leverage is permitted.
3. Beta-matched controls
Retain the prospective trailing-data BM-X method.
Before the run, define:

* What happens when an estimated beta is negative or above 1.
* How a benchmark remains long-only and unleveraged.
* What happens when 252-session beta inputs are insufficient.
* How realized beta mismatch is reported.

Do not use future returns or the already observed full-period H028 beta to choose benchmark weights.
4. ETF and corporate-action accounting
Ensure stock and ETF dividends are treated consistently and never double-counted between adjusted prices, cash distributions and reinvestment.
Preserve the disclosed historical delisting conventions and their implementation limitations.
5. Interpretation of known history
2015–2021 has been extensively studied.
The expected terminal-wealth comparison is already partially known.
The new test is primarily about:

* Account-level feasibility.
* Incremental value beyond market exposure.
* Transaction costs.
* Stability.
* Comparison against transparent defensive alternatives.

It does not independently validate H028.
Protocol and experiment freeze
After resolving these engineering details:

1. Finalize `SYS1_protocol_PROPOSED.md`.
2. Record all approved exceptions and classifications.
3. Freeze the complete protocol and code/configuration hashes.
4. Commit offline evaluation rules and tests before any result.
5. Run E032-01.
6. If all mandatory canary checks pass, run E032-02.
7. Produce the full checkpoint and STOP.

If a clarification requires a substantive change to the strategy, benchmarks, historical rules or scientific gates, STOP and obtain a new owner decision instead.
Do not choose a favorable interpretation without authorization.
Restrictions
No modifications to H028, its learned score, Top-K or frozen historical results.
No OC-2 restart.
No new stock-selection hypothesis.
No allocation optimization.
No new datasets or purchases.
No data after 2021-12-31.
No Holdout access.
No automatic move to live trading, a D051 production model or Holdout confirmation.
Final Deliverable
Report every canary check and every permitted evaluation arm, including:

* Net terminal wealth relative to SPY.
* Wealth relative to each prospective beta-matched control.
* Performance versus LV15 and SPLV combinations.
* Risk, drawdowns and market capture.
* Turnover, commissions and slippage.
* Skipped trades and actual allocations.
* Dependence on 2018 and 2020.
* Double-slippage robustness.
* All account-rule violations, if any.
* Formal FS-1 through FS-6 verdict.
* What the result can and cannot establish.
* Exact next owner decision required.

STOP after SYS-1.
The Holdout remains sealed, and H028 remains REJECTED regardless of the development-period result.
