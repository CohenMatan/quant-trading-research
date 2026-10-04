# Owner message 2026-10-04: "P4-CP3 Revision — Correct the Signal Definitions and Freeze H019 Before Any Real Validation"

This is a recorded summary; the full message is in the session transcript.

## Decision
- **Conditional GO** toward H019, after these corrections:
  1. Smooth Momentum must use the exact published information-discreteness definition, ID = sign(PRET) × (%neg − %pos). Verify the PRET lookback, the skip month, the counting rule, zero-return days, and whether the paper conditions within momentum groups.
  2. The trend score must not be attributed to Han-Zhou-Zhu unless it is their construction.
     - **Preferred:** implement the real HZZ trend factor fully point-in-time (prior-data coefficients only; no full-sample coefficients; no look-ahead normalisation).
     - If it is impractical, unsafe or materially different: STOP and recommend Option A (exact HZZ) or Option B (an honestly renamed, independently justified simplified score). No silent substitution.
  3. Primary horizon = **next 1 month**. The 3-month return is a diagnostic only and can never rescue a primary failure.
  4. Monthly ranking stays.
  5. α = 1% stays, described as a conservative pre-registered research threshold reflecting prior experimentation, not an exact adjustment.
  6. Exactly three signals; no fourth.
- **Other requirements:**
  - The incremental-value test is mandatory: one frozen method.
  - The permutation family-level framework stays.
  - The null preserves dates, returns, cross-sectional structure, universe and common shocks, and breaks only the signal-to-own-return link.
  - Re-run the synthetic power study for the 1-month primary (MDE 50% / 80%, false-pass rate, effective sample size), with 3-month values for comparison.
  - Reassess the economic floor (3% a year top decile) for the 1-month horizon without loosening it for power.
  - Verify both definitions against the strongest accessible complete sources. Document what is verified and what remains uncertain. Do not freeze a materially uncertain formula.
- **Pre-registered interpretations:**
  - **Failure:** "No technical stock-selection signal large enough to satisfy the project's detection and economic-significance requirements was found" — not "no 1–3% edge exists".
  - **Success:** credible cross-sectional predictive information on the frozen test only; not a strategy, not SPY-beating, not portfolio viability, not 2018–2021 validation.

## Deliverable
**P4-CP3R — Corrected Cross-Sectional Signal Validation Specification** (34 items, ending with READY / NOT READY).

## STOP conditions
- None of the following:
  - computing real signals;
  - computing next-month returns, deciles, IC or t-statistics;
  - running real permutations;
  - building a portfolio (holdings, entries, exits, weekly management, commissions);
  - accessing 2018–2021 (in any form) or the Holdout.
- After P4-CP3R is committed: STOP and wait for explicit approval of the corrected frozen specification.
