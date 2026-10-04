# Owner message 2026-10-04: "P4-CP3R2 — Verify Exact Signal Implementation Fidelity Before H019"

This is a recorded summary; the full message is in the session transcript.

## Decision
- Conditional approval to continue toward H019. **H019 runs are not authorised yet.**
- **Approved and frozen** unless a true implementation contradiction appears:
  - S1 plain momentum (reference);
  - S2 = ID = sign(PRET) × (%neg − %pos), with momentum groups first, then ID;
  - S3 = the actual published Han-Zhou-Zhu trend factor;
  - monthly ranking;
  - next-1-month primary outcome; 3-month diagnostic only;
  - 1% threshold;
  - 5,000 null worlds (if the null is correct);
  - the quintile monotonicity rule (conditionally).

## Required
- **Trend factor, missing history:** verify how the published method / trusted replication handles insufficient price history. Cover every horizon, IPOs and young stocks, the minimum history, and regression tolerance of missing MAs. Use the replication code as the authority; state any discrepancy with the paper; do not invent conventions to preserve sample size.
- **Warm-up and window:** determine the warm-up and pre-2010 sufficiency, and the earliest valid month per signal. Fix the common window mechanically. Re-run the power study if the window or implementation changes materially.
- **Chronology and leakage:**
  - an exact trend-factor chronology;
  - strict leakage canaries: future prices, next-month returns, coefficients observable only historically, late entrants, truncation.
- **Null procedure:**
  - null worlds must re-run the full procedure, including re-estimating the fitted trend factor;
  - preserve the S1 → S2 dependency and market structure;
  - no naive global shuffle.
- **Smooth-momentum conventions:** verify PRET, skip month, counting, zero-return days, missing days, group count, ties and minimum history.
- **Quintile rule:** document why the decile rule failed, the exact new rule, and its synthetic false-positive comparison.
- **Trend-factor decomposition:** explanatory only; it may never trim or rescue the factor. No simplified trend-score fallback inside H019 (that would need a spec v2 and approval).
- **Run sequence:** canary → 5,000 null → threshold → commit / hash → clean tree → one real run → checkpoint → STOP. The threshold is immutable.
- **Constraints:** no portfolio; no 2018–2021 (in any form); Holdout locked; no new signals.

## Deliverable
**P4-CP3R2 — H019 Signal Implementation Fidelity and Null-Procedure Readiness** (36 items, verdict READY FOR H019 RUNS / NOT READY).

## STOP
After committing: no real null worlds, no real evaluation, no real ICs or deciles, no 2018–2021, no Holdout, no portfolio, no simplified trend-factor substitute. Wait for explicit approval.
