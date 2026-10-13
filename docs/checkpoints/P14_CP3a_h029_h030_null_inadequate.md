# P14-CP3a — STOP: H029 / H030 NULL INADEQUATE (before any threshold or real result)

**Result: STOP — H029/H030 NULL INADEQUATE.**
- The pre-registered null-adequacy rule (spec section 9 B) failed on one measure: H029 sector concentration. The real H029 portfolio is more sector-concentrated than the null allows.
- Under the owner's rule (D229 section 30: "If the null is structurally inappropriate: STOP — H029/H030 NULL INADEQUATE. Do not invent another null after seeing the real result"):
  - c_UP_H029 and c_INCREMENTAL_H030 are **not pinned**;
  - the real run E031-05 was **not run**;
  - no real H029 or H030 portfolio, return, wealth, capture or gate has been computed.
- H028 is unchanged. The Holdout is sealed.

## 1. What was done (owner run order steps 1–16)

| Step | Status |
|---|---|
| 1–6 Data v3 | **DATA V3 PASS** and frozen (P14-CP2, D230; PR #97) |
| 7–10 H029 / H030 hypotheses, spec, gates, null, assessment scripts | Frozen before any H029 / H030 value: commit 7bdbcf7 (D231): `research/phase14/H029_H030_spec.md`, `qr_h029`, standalone host S031 |
| 11 Tests | All pass (full suite) |
| 12 Canary E031-01 | **PASS 17/17** (details in section 2) |
| 13 Freeze | Spec, module and host hash-pinned in `qresearch.p14h029` |
| 14 5,000 null worlds | E031-02 (seeds 1–2,500) and E031-03 (2,501–5,000): all finite; Data v3 / H026 panel digests and H028 reproduction verified in each run |
| 15 Rerun seeds 1–25 | E031-04: **identical** to E031-02 rows 1–25 |
| 16 Null adequacy | **FAILED** (section 3) → STOP |
| 17–27 | Not performed |

## 2. Canary E031-01 (PASS 17/17)

- **Data v3:** the per-review H029 input-panel digests equal the frozen Data v3 digests (131 / 131). PIT audit 0; no v3-view record after the decision day.
- **H026 panels:** the feature and response panel digests equal the pinned ones.
- **Frozen H028 reproduced exactly** on QuantConnect's current default build (LEAN 18179):
  - λ = 100 coefficients identical (maximum difference 0.0);
  - H028 terminal wealth **$328,294.908** (identical);
  - LV15 **$220,156.035** (identical).
- **Mechanics:**
  - every signal row has at least 5 of 6 values;
  - the H029 scores of three months were recomputed independently (identical);
  - the H030 blend is exactly 0.5 / 0.5;
  - entries come after the review session;
  - the joint universe is a subset of the H029-eligible set.
- **Null checks** (seeds 1, 2):
  - H028 scores never change;
  - the eligible set never changes;
  - every recipient holds its donor's complete six-signal vector;
  - no self-matches;
  - partner persistence 120,633 / 120,633.
- **Synthetic A (pure noise, 5 replications):** p for S_UP from 0.08 to 0.76; never significant.
- **Synthetic B (planted upside predictor):** S_UP 12.3 vs a null maximum of 0.37; p = 1/51.
- **Runtime and resources:** 0.16–0.21 s per world; peak memory 7.7 GB (above the 6.5 GB preference; not a gate); 50 project files.

## 3. The adequacy failure (pre-registered rule, spec section 9)

**Rule (B):** the real value of the score-only selection structure must lie inside the [0.5%, 99.5%] range of the 5,000 null worlds. The selection structure is the Top-15 target lists, with no returns used. It is checked for name turnover and FF12 sector concentration (Herfindahl index of sector counts), for H029 and for H030.

| Measure | Real | Null 0.5% – 99.5% | Null median | Result |
|---|---|---|---|---|
| H029 name turnover | 0.357 | 0.342 – 0.377 | 0.358 | ok |
| **H029 sector concentration (HHI)** | **0.1630** | 0.1444 – **0.1599** | 0.1523 | **FAIL**: only 2 of 5,000 null worlds reach it (99.96th percentile) |
| H030 name turnover | 0.360 | 0.356 – 0.428 | 0.393 | ok |
| H030 sector concentration | 0.1674 | 0.1565 – 0.1690 | 0.1631 | ok |

**Rule (C) — null risk distributions:** finite, non-degenerate, medians in [0.5, 1.5]. All pass.

| Null world | Beta | Up capture | Down capture | Volatility |
|---|---|---|---|---|
| H029 null | 1.10 | 0.95 | 1.10 | 21.1% |
| H030 null | 0.84 | 0.88 | 0.83 | 17.2% |

**Interpretation (structure only; no return was looked at):**
- The real Business Improvement scores cluster by sector: improving fundamentals tend to move together within industries.
- The single-stratum identity tether hands each stock a donor from any sector, so the null portfolios are more sector-diversified than the real one.
- Under the pre-registered criterion, the null therefore does not reproduce a structural property of the real selection. A null that cannot produce the real portfolio's sector concentration could make sector bets look like stock-selection skill.

**What the stop means:**
- The real H029 / H030 performance is **unknown**. H029 and H030 are **neither qualified nor rejected**.
- The null result is committed (`research/phase14/cp3/P14_CP3_null.json`, `P14_CP3_null_rows.json`) for the record. Its thresholds (c_UP 0.2696, c_INC 0.0059) are **not pinned and must not be used**.

## 4. Options for the owner

1. **Sector-stratified identity tether (recommended):**
   - The same null, but donors are drawn only from the same FF12 sector at each review. This is the stratified mode of the existing tether (`ChartTether` strata).
   - It preserves the sector composition of the H029-eligible set, and so the sector concentration of the selections, by construction.
   - It needs a short pre-registered amendment, then a new canary, 5,000 null worlds, the seeds 1–25 rerun and the same adequacy rule. Only then: thresholds and the ONE real run.
   - No real return has been seen, so choosing this null is not informed by H029 / H030 performance. The amendment would still be owner-approved and disclosed as a response to the adequacy check.
2. **Accept the inadequacy as an owner exception**, and proceed with the single-stratum null. Not recommended: the failure is exactly the kind the rule was written to catch.
3. **Close H029 / H030 without a result.**

**Recommendation:** option 1. It changes nothing in H029, H030, H028, Data v3, the gates or the costs; only the null's donor pool becomes sector-matched.

## 5. Integrity

| Item | Value |
|---|---|
| New hypotheses / strategies / experiments | 2 (H029, H030) / 1 (S031) / 4 (E031-01 canary, E031-02 and 03 null, E031-04 rerun), all infrastructure |
| Pre-registration before any value | 7bdbcf7 |
| Real H029 / H030 runs | **0**. No performance computed. |
| H028 | Unchanged; reproduced exactly |
| Data v3 | Frozen, unchanged |
| Holdout | Sealed |

**STOP. Awaiting the owner's decision (section 4).**
