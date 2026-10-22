# Owner decision D282 — OS-CP2 / H032 first strategy backtest (2026-10-22)

**Context:** follows OS-CP2 (`docs/checkpoints/OS_CP2_h032_canary_c_os1_E807.md`, D281, PR #130). The message is recorded verbatim below, before any work.

---

Owner Approval — OS-CP2 / H032 First Strategy Backtest
I have reviewed OS-CP2, the frozen H032 specification and the E807-02 canary results.
I accept C-OS1 = PASS under the original frozen gates.
The two narrow margins are acknowledged:

* Split-adjusted share pairs within the sanity bound: 90.05%, against the 90% threshold.
* Minimum joint coverage: 66.8%, against the 65% threshold.

These do not justify changing the frozen thresholds or strategy specification.
Decision: Approve Option A
I authorize the minimum trading-host implementation and the first exploratory backtests of H032.
1. Implementation
Implement the trading host exactly according to the frozen H032 specification and evaluation protocol.
Reuse the existing harness, SEC objects, scoring module, portfolio rules and control books.
Before running, complete offline synthetic tests for trade execution, position sizing, cash constraints, commissions, slippage, delistings, shadow-book accounting and benchmark alignment.
No changes to the frozen signal, filters, Top-15 rules, ranking buffer, start date, evaluation gates or research window are authorized.
2. R1 — Primary Backtest
Authorize R1 with:

* The frozen development window beginning July 31, 2012.
* $100,000 initial capital.
* 10 bps slippage per side.
* $7 per order.
* The existing position, cash, execution and portfolio constraints.
* All frozen benchmark and control-book comparisons.
* Evaluation against the frozen O1–O9 framework.

Before accepting any performance verdict, enforce the frozen shadow-book fidelity pre-gate.
Report the actual maximum monthly-return discrepancy and terminal-wealth discrepancy between LEAN and the shadow replay, not only PASS/FAIL.
If fidelity fails, or there is a material execution, point-in-time or dataset-integrity problem, STOP. Do not reinterpret the run as a valid strategy result or change the implementation to rescue it without owner approval.
3. R2 — Cost Stress
If R1 is technically valid and passes all gates evaluable without R2, authorize R2 using the identical frozen strategy at 20 bps slippage per side.
If R1 already fails a required performance gate, close H032 as NOT PROMISING and do not run R2 unnecessarily.
At most one documented infrastructure retry per authorized run. No performance-motivated reruns or variants.
4. Required Results Report
Provide a clear comparison of H032 against SPY and the frozen controls, including:

* Final portfolio wealth and CAGR after costs.
* Excess CAGR over SPY.
* Performance during SPY-positive months and upside capture.
* Regression alpha, beta and the prespecified statistic.
* Comparison with equal-weight, random, filtered-random and beta-matched control portfolios.
* The original unfiltered OS-1 result, strictly diagnostic.
* Results for both fixed development subperiods.
* Results for the original vendor universe.
* Maximum drawdown, downside capture and volatility.
* Turnover, costs, concentration and the contribution of restored securities.
* Results of every O1–O9 gate.
* Engine version, data checks and execution-fidelity diagnostics.

Clearly distinguish observed performance from claims of predictive ability or independent validation.
5. Execution Boundaries
No additional hypotheses, parameter searches, filter changes, sector restrictions, new SEC repairs or purchases.
Do not reopen H028, activate H031 or access the 2022–2026 Holdout.
RR6 remains INCONCLUSIVE. All H032 results remain EXPLORATORY.
After the authorized runs, produce and commit a concise performance checkpoint and STOP for my review.
If H032 fails, preserve the original result and do not promote B0 or any control book as a replacement strategy.
If all gates pass, report EXPLORATORY PASS and propose the appropriate independent-validation path, without initiating it.
Our goal is now to determine whether the frozen H032 strategy demonstrates a meaningful offensive advantage over SPY after realistic costs.
