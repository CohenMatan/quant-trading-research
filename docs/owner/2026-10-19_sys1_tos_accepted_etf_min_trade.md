# Owner decision D253 — QuantConnect terms accepted; $1,000 ETF minimum trade approved (2026-10-19)

**Context:**
- This follows D252 (SYS-1 controlled development experiment) and the E032-01 start refusal: QuantConnect required acceptance of its latest terms of service (`RESEARCH_LOG.md`, 2026-10-19).
- The message is recorded verbatim below.

---

I confirm that I have accepted the latest QuantConnect Terms of Service.
I also explicitly approve the $1,000 minimum ETF trade rule for SYS-1 only, applying consistently to SPY, SPLV, USMV and all benchmark portfolios.
Please:

1. Verify that the QuantConnect API is accessible again.
2. Record this approval as the next owner decision after D252, before any run.
3. Preserve the frozen SYS-1 strategy, parameters and evaluation gates. Do not introduce further changes.
4. Run E032-01 (canary).
5. Proceed to E032-02 (evaluation) only if every mandatory canary check passes.
6. Evaluate all approved portfolios and report the complete FS-1 through FS-6 results.
7. Commit the checkpoint and STOP for my review.

If the canary fails, STOP and report the issue. Do not modify the experiment or bypass any requirement without my approval.
Do not access the Holdout, optimize allocations, modify H028, or run additional experiments.
H028 remains REJECTED — Frozen Defensive Research Reference.
