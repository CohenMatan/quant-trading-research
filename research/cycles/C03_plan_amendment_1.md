# C03 plan: Amendment 1 (D087/D088), owner-approved 2026-09-30

This replaces the H012 parts of `docs/checkpoints/CP3e_C03_final_plan.md` (which is kept unchanged as history). Everything not mentioned here stays as approved.

## Scope

- **H013 is the only active C03 hypothesis.** Its rules, parameters, three variations (v1.0: top 20% by MAX; v1.1: top 10% by MAX; v1.2: top 20% by MAX5) and three seeds are unchanged.
- **H012 is removed before any strategy backtest.**
  - Status: *not evaluable with sufficient statistical power using the currently available data* (CP3h, D086). It is not a failed hypothesis.
  - Its configurations E012-01..11 are listed in `experiments/WITHDRAWN.json`, and the runner refuses them.

## Committed runs (research budget: 21)

| Class | Runs | IDs |
|---|---|---|
| H013 selection ($100K, 15 positions) | 9 | E013-01..09 (v1.0 seeds 1–3, v1.1 seeds 1–3, v1.2 seeds 1–3) |
| S1 capital sensitivity ($200K, 15 positions, v1.0) | 3 | E013-10..12 |
| S2 construction variant ($200K, 20 positions, v1.0) | 3 | E013-13..15 |
| Paired random nulls at $200K | 6 | E962-25..27 (S1), E962-28..30 (S2) |

The $100K paired nulls are the existing E962-22..24 (identical settings; not re-run).

## Conditional runs (pre-declared; only if the preceding step is passed)

1. **2× slippage screen item.** Run only for a variation whose three seeds **all** pass the base IS screen: 3 runs per variation (one per seed), at most 9 in total. The item requires Sharpe ≥ 0.40 for each seed.
2. **Mechanical choice.** Among variations whose three seeds all pass the full screen, choose the one with the highest mean of its seeds' IS Sharpes. Ties go to the lower version.
3. **Robustness battery for the chosen variation only, per seed:** 6 runs per seed, 18 in total.
   - 4× and 6× slippage.
   - Exclusion fraction q ± 0.05: 15%/25% for v1.0 and v1.2; 5%/15% for v1.1.
     - **D088 clarification:** CP3e's "exclusion 15%/25%" was written for the 20% base. It is fixed here, before any result, as the base ± 5 points.
   - Holding period 45 and 75 sessions.

   **Criteria (unchanged), for every seed:**
   - plateau: all 4 perturbations (two q, two hold) keep Sharpe ≥ 70% of that seed's base Sharpe;
   - Sharpe > 0 at 4× costs (6× is reported only);
   - every third of IS with Sharpe > 0.
4. **Maximum research budget:** 21 + 9 + 18 = **48 of the 82 cap.** It is a maximum, not a target.

Validation is not part of this plan. It requires separate owner approval.

## Statistics

- **Trial counts:** Amendment 1 of the statistical specification (`research/cycles/C03_statistical_spec_amendment_1.md`):
  - official N = 40 at the C03 evaluation;
  - conservative N = 73 after the selection runs, at most 103;
  - N = 43 reported as a sensitivity only.
- **PBO:** a diagnostic only, over H013's 3 variations using the seed-averaged series.

## Limitations stated in advance

- **Three variations** of one idea give little room to measure selection bias. PBO over 3 highly correlated columns is especially weak.
- **The three seeds are correlated** (about 0.86), so they carry the information of about 1.1 independent portfolios. "All three pass" guards against a lucky draw; it is **not** three independent confirmations of significance.
- **The paired null** removes the market and portfolio-structure effects shared by H013 and random selection. Only the effect of the exclusion remains. Its precision is limited by the 8-year IS.

## Stopping rule (unchanged)

If H013 produces no qualifying candidate:

- no further research cycle is started;
- a comprehensive review of the research programme is prepared before any further experiment is proposed.
