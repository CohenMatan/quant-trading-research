# Owner message 2026-10-10: "Phase 7 — H022 / Data v2 Null Calibration. Canary → 5,000 Null Worlds → Pin New c_IC. NO REAL H022 EVALUATION"

Recorded summary (the full message is in the session transcript). Decision id: **D194**.

**Approved: H022 on frozen Data v2, steps 1–3 only.**
1. One H022 / Data-v2 canary.
2. Only if the canary passes: the full 5,000 pre-registered identity-tethered null worlds (seeds 1 → 5,000, one world per seed, preferably 5 × 1,000).
3. Compute the new empirical Data-v2 c_IC, pin it in Git before any real H022 evaluation, and STOP for owner review.

**The real H022 evaluation is NOT authorised.**

**Immutable during this checkpoint:**
- Data Infrastructure v2, FROZEN (manifest `cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb`), including the owner-approved Gate K exception. Gate K stays "FAILED under the original pre-registered 3%-per-year identity-incidence criterion / OWNER-APPROVED EXCEPTION".
- Data v2 itself: reference data, market-cap repair, M2, SEC identity rules and the SAFE / BOUNDED / REJECT classes, restatement guard, universe.
- Score v1 and H1–H7.
- The H022 setup: research window, specification, gates, null methodology, significance level, mechanics and costs.

Any mismatch against the frozen manifest is a STOP.

**H022 is unchanged:**
- 83 decision dates, 2011-01-31 → 2017-11-30.
- Response: next-session open after review t → next review close, as stock total shareholder return minus the equal-weight mean of the same population.
- Primary statistic: monthly Spearman IC, t_IC with Newey-West lag 2.
- Gates G1–G4 as frozen:
  - G1: t_IC > c_IC and mean IC > 0;
  - G2: 80+ ≥ +3.0%/yr;
  - G3: monotonicity ≥ 0.90 and Q5 > Q1;
  - G4: both halves > 0 and no block > 50%, blocks 2011–12 / 2013–14 / 2015–16 / 2017.

**Blindness:**
- Before the new c_IC is pinned, no unpermuted real score → future-return statistic may be computed, printed, exported, logged, cached or inspected. That covers the real mean IC, t_IC, quintiles, 80+ returns, G1–G4, sector-demeaned IC, Fama-MacBeth and 2- or 3-month diagnostics.
- No world reproduces the real assignment.
- The null is the exact frozen identity-tethered within-date permutation (no simpler shuffle; port mechanically, with equivalence tests).

**Canary:** it verifies:
- the manifest, Score v1 and reference hashes;
- the actual LEAN build and the panel digest;
- the 83 dates and the populations;
- response construction, corporate actions and next-session-open timing;
- null plumbing, Newey-West and the full G1–G4 null procedure;
- the output path and compliance.

It must not compute the real H022 result. It establishes the Data-v2 H022 panel digest, and the later real run is blocked if that digest changes.

STOP conditions: manifest, score, reference, review-count or panel mismatch; a PIT, timing, corporate-action or null error; real mapping used; compliance rejection; a default-build change that alters the panel.

**Null runs:**
- Every world reruns the complete procedure. Per-world output: seed, t_IC, mean IC, G1–G4 and all-four.
- Integrity: exactly 5,000 unique seeds, identical panel digest and code across batches, and a deterministic rerun of a pre-specified seed sample. A different result for the same seed is a STOP.
- c_IC = max(empirical 1% one-sided threshold, 2.326), using the same order-statistic convention as Data v1.
- Report the null distribution, the gate frequencies and the full-procedure false promotion.
- The synthetic c_IC (≈ 2.53) is not the threshold.
- The old c_IC 2.390976216956 stays DATA_V1_ONLY / UNUSED_ON_V2. The new threshold is a separate, versioned record.

**Pin before any real run:** write the new c_IC, the null-distribution hash, the seeds, the panel digest, the code hashes and the LEAN build(s); commit; merge; verify the tree is clean.

**Not allowed:** a quick look at the real result, any portfolio, 0 orders broken, 2018–2021, the Holdout, or tuning after seeing null results. If something surprising appears, investigate implementation errors only.

**Checkpoint:** "P7-CP6 — H022 Data v2 Canary and Null Calibration" (53 items). Final status:
- "CALIBRATED — Data v2 c_IC pinned, real H022 still sealed", or
- "BLOCKED — H022 Data v2 calibration not valid".

Then STOP.
