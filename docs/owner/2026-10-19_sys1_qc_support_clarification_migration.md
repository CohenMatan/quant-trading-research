# Owner decision D257 — QuantConnect Support clarification and SYS-1 migration preparation (2026-10-19)

**Context:**
- This follows D255 / D256 (SYS1-CP1, `docs/checkpoints/SYS1_CP1_platform_recovery_feasibility.md`, PR #119).
- The message is recorded verbatim below.

---

SYS-1 — QuantConnect Support Clarification and Migration Preparation

QuantConnect Support has now confirmed the following:

1. Independently sourced SEC EDGAR reference data can be uploaded as plain JSON into QuantConnect Object Store and used within Cloud backtests.
2. QuantConnect security identifiers and historical universe membership should be generated directly inside Cloud backtests using the platform's own symbol and universe-selection functions, rather than reusing previously extracted QuantConnect data.
3. The underlying QuantConnect Platform Data must remain within QuantConnect Cloud.
4. Backtest results should be retrieved using the supported official result-export functionality.

I want to proceed toward recovering SYS-1.

Your next task

Review D252–D256, the frozen SYS-1 protocol, the failed E032-01 upload, and the platform recovery feasibility checkpoint.

Prepare a compliant Object Store migration plan based on QuantConnect Support's instructions.

Specifically:

1. Identify the independently sourced SEC data to store as plain JSON.
2. Determine how to regenerate QuantConnect security identifiers and historical universe membership entirely inside Cloud.
3. Identify every compressed source module, embedded dataset and encoded output that must be replaced.
4. Design the minimal changes required to the data-loading infrastructure.
5. Use only permitted backtest result exports.
6. Determine how to verify that the new infrastructure reproduces frozen H028 exactly, including the original final wealth, trades, commissions and mandatory integrity checks.
7. Identify any issues caused by historical changes in QuantConnect's underlying data or universe-selection behavior.

Preserve the original strategy, allocations, costs, benchmark definitions and research gates.

If exact H028 reproduction is impossible, stop and explain why. Do not silently relax reproduction tolerances, substitute a different historical universe or reinterpret the results as equivalent.

Prepare the proposed replacement infrastructure version, new freeze requirements, migration procedure and canary specification.

Do not yet upload data, run a QuantConnect backtest, launch E032-02, modify legacy Cloud projects or access the Holdout.

Do not purchase additional services.

Record the support clarification and your findings in a checkpoint, commit the documentation and STOP for owner approval.

The objective is to restore SYS-1 with minimal changes while preserving research integrity and complying fully with QuantConnect's current Terms of Service.
