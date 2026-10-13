# P14-CP3b — H029 / H030 Sector-Stratified Null Amendment

**Result: H029/H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE.**
- The new same-sector null was built exactly as the owner approved (D233). It passed its canary 23/23 and produced 5,000 reproducible worlds.
- It still fails the unchanged, pre-registered adequacy rule on one measure: **H029 name turnover**. The real H029 Top-15 changes fewer names from month to month than **any** of the 5,000 sector-null worlds.
- Under the owner's rule (D233 sections 22, 33 and 39):
  - no threshold is pinned (none was even computed);
  - the real run E031-10 is **not** run, and no real H029 / H030 return, wealth, capture or gate exists;
  - **no third null is designed**.
- H029 and H030 are **neither qualified nor rejected**. H028 and Data v3 are unchanged. The Holdout is sealed.

**STOP. Awaiting the owner.**

---

## 1. P14-CP3a — the original null failure (unchanged, permanent)

- **Original null:** single-stratum identity tether (donor from any sector). Runs E031-01 (canary 17/17), E031-02 / 03 (5,000 worlds) and E031-04 (rerun, identical).
- **Adequacy failure:** H029 FF12 sector HHI real **0.1630** vs the null 99.5th percentile **0.1599**. Only 2 of 5,000 worlds reached it.
- **Record:** `docs/checkpoints/P14_CP3a_h029_h030_null_inadequate.md`, `research/phase14/cp3/P14_CP3_null.json`. Neither is changed.

## 2. Owner approval of the amendment

- **Owner decision D233 (2026-10-13):** "Approve Option 1: replace the original single-stratum H029/H030 null with a sector-stratified identity tether using the same FF12 sector."
- **Recorded verbatim** in `docs/owner/2026-10-13_p14cp3b_sector_null_amendment.md` before any sector-null value existed.

## 3. No real performance existed before the amendment

- **No real H029 / H030 portfolio return, wealth, capture, threshold or gate result has ever been computed.** No run in real mode was ever started (E031-05 never ran; E031-10 not run).
- The only real quantities ever observed are the score-only selection-structure values the adequacy rule needs: name turnover and sector HHI of the Top-15 target lists, built from scores without any return.
- The amendment is therefore an **owner-approved pre-performance methodological amendment following a pre-registered adequacy failure**. It was not pre-registered from the start.

## 4. Original null methodology

`qr_p7_pred.Tether(seed)` with one stratum, over the 84 evaluation months:
- each H029-eligible recipient received the complete six-signal vector of a persistent donor from **any** sector, never itself;
- H028, returns, sectors and eligibility stayed with the recipient;
- H030_null = 0.5 × centred(real H028) + 0.5 × centred(permuted H029).

## 5. New same-FF12-sector methodology (Amendment 1)

`research/phase14/H029_H030_amendment1_sector_null.md` (SHA-256 pinned in `qresearch.p14h029`; the original spec is byte-identical):
- **Tether:** `qr_h020_stats.ChartTether(seed)` with strata = each stock's frozen FF12 sector at the review.
- **Donor:** another eligible stock of the **same sector**, persistent while both stay eligible and in that sector.
- **Vector:** the complete six-signal vector moves together.
- **No self-matches:** a self-match is a STOP ("SECTOR-STRATIFIED NULL NOT CONSTRUCTIBLE"); there is never a cross-sector fallback.
- **H030_null:** 50% real H028 + 50% sector-randomized H029; H028 is never randomized.
- **Implementation:** `qr_h029.tether_vectors` / `donors`; host S031 v1.1, which only adds canary checks.

## 6. Scientific rationale

- The first null failed because it destroyed a structural property of the real signal: Business Improvement scores cluster by sector.
- Matching donors within sectors keeps the sector composition of the eligible set in every world.
- The question would then have been whether the real ranking selects better stocks than same-sector reassignments.

## 7. Limitation: sector alpha is conditioned out

- The sector null intentionally does not test whether H029's sector allocation itself is predictive.
- A significant result would have meant within-sector / conditional stock-selection information only.
- This is moot now: no significance test was performed.

## 8–12. Unchanged components

| Item | Status |
|---|---|
| 8. H029 | Unchanged: F1, F2, F4, F5, F7, F8; at least 5 of 6; equal weights; no ML / Ridge / λ; Top-15, at most 3 per FF12; monthly; next-open; $7 / $7; 10 bps; $100,000. Canary in-host score recomputation identical. |
| 9. H030 | Unchanged: exactly 0.50 / 0.50 (canary blend mismatch 0). |
| 10. Data v3 | Unchanged: frozen manifest; per-review H029 panel digests equal the frozen ones (131 / 131) in E031-06, 07 and 08; PIT audit 0; no v3-view record after the decision day. |
| 11. H028 | Unchanged: λ = 100 coefficients identical (max difference 0.0); H028 $328,294.908 and LV15 $220,156.035 reproduced exactly on LEAN 18179 in every run; result file hash pinned. |
| 12. Gates | N1–N5 and C1–C7 unchanged (never evaluated). |

## 13. Canary E031-06 — PASS 23/23

| Check | Result |
|---|---|
| Sector null constructible | Yes. Smallest FF12 sector in any review: **12** eligible stocks; reviews with a one-stock sector: 0. |
| Donor sector = recipient sector | 128,490 mappings (seeds 1, 2); 0 cross-sector |
| Recipient sector unchanged | 0 changed |
| Recipient eligible sets unchanged | 0 changed |
| Complete six-signal vector moves | 0 mismatches |
| No self-matches | 0 |
| Persistent donor mapping | 120,472 of 120,654 possible kept (99.85%) |
| Recipient returns / holding arrays unchanged | Digests identical before and after the null worlds |
| Recipient H028 unchanged | 0 changes |
| Costs and mechanics unchanged | K 15, cap 3, $100,000, $7, 0.10% (stress 0.20%), λ 100 |
| Data v3, H026 panels, H028 / LV15, H029 score, 50/50 blend, entry timing | All pass |
| Resources | Peak memory 7.84 GB; 50 project files; 0.21 s per world |

## 14. Synthetic A — pure noise within sectors (5 replications × 50 sector-null worlds)

- **S_UP p-values:** 0.82, 0.25, 0.59, 0.39, 0.04.
- **S_INC p-values:** 0.59, 0.49, 0.76, 0.39, 0.45.
- **Result:** none has p ≤ 0.02 → **PASS**. Noise does not beat the sector null.

## 15. Synthetic B — planted within-sector upside predictor

- **S_UP:** 12.10 vs a null maximum of 0.21, p = 1/51 → **PASS**.
- **S_INC:** 3.75, p = 1/51.
- **Conclusion:** the sector null can recognise genuine within-sector selection skill.

## 16. 5,000-world completion

| Run | Seeds | Worlds | Seconds per world | Peak memory | Checks |
|---|---|---|---|---|---|
| E031-07 | 1–2,500 | 2,500 | 0.24 | 7.73 GB | Data v3 / H026 panels equal, H028 reproduced |
| E031-08 | 2,501–5,000 | 2,500 | 0.22 | 7.79 GB | as above |

- All 5,000 rows are finite. The real score-only structure is identical in both runs.
- Default build LEAN 18179.

## 17. Seeds 1–25 reproducibility

E031-09 reproduces E031-07's rows 1–25 **exactly** (every stored field).

## 18–22. Adequacy (the unchanged rule, spec section 9)

| # | Measure | Real | Sector null 0.5% – 99.5% | Null median | Result |
|---|---|---|---|---|---|
| 18 | **H029 name turnover** | **0.3574** | **0.3655** – 0.3831 | 0.3735 | **FAIL**: below all 5,000 worlds (null minimum 0.3622) |
| 19 | H029 sector HHI | 0.1630 | 0.1628 – 0.1630 | 0.1630 | ok |
| 20 | H030 name turnover | 0.3598 | 0.3590 – 0.4297 | 0.3944 | ok (0.68th percentile, just inside) |
| 21 | H030 sector HHI | 0.1674 | 0.1617 – 0.1720 | 0.1669 | ok |

**22. Risk adequacy (rule C):** every null distribution is finite with sd > 0, and the medians lie in [0.5, 1.5] → **pass**.

| Null world | Beta | Up capture | Down capture | Volatility |
|---|---|---|---|---|
| H029 sector null | 1.14 | 1.02 | 1.13 | 21.5% |
| H030 sector null | 0.85 | 0.88 | 0.84 | 17.3% |

## 23. Original vs sector-stratified null (descriptive; not a choice between nulls)

| Statistic | Original null median (0.5–99.5%) | Sector null median (0.5–99.5%) | Real (percentile in original → in sector null) |
|---|---|---|---|
| H029 sector HHI | 0.1523 (0.1444–0.1599) | 0.1630 (0.1628–0.1630) | 0.1630 (99.96 → 51.1) |
| H029 turnover | 0.3582 (0.3422–0.3767) | 0.3735 (0.3655–0.3831) | 0.3574 (41.9 → **0.0**) |
| H030 sector HHI | 0.1631 (0.1565–0.1690) | 0.1669 (0.1617–0.1720) | 0.1674 (96.7 → 60.8) |
| H030 turnover | 0.3928 (0.3558–0.4281) | 0.3944 (0.3590–0.4297) | 0.3598 (1.3 → 0.7) |
| H029 beta / up / down / vol | 1.10 / 0.95 / 1.10 / 21.1% | 1.14 / 1.02 / 1.13 / 21.5% | not computed (no real run) |
| H030 beta / up / down / vol | 0.84 / 0.88 / 0.83 / 17.2% | 0.85 / 0.88 / 0.84 / 17.3% | not computed |

**What the comparison shows (structure only, no return used):**
- **Sector concentration is now fully controlled.** The H029 sector HHI has zero spread in the sector null.
  - Within-sector reassignment leaves each sector's set of scores unchanged, and the Top-15 with at most 3 per sector depends on those sets.
  - So every world, and the real selection, holds the same sector composition each month.
- **That control moved the problem to turnover.**
  - In the sector null, which stocks inside each sector carry the high scores is reshuffled, and the null selections turn over more names (median 0.374 vs 0.358 before).
  - The real H029 selection is more persistent (0.357) than every sector-null world.
- **The exact mechanism is not established.** It could be partner re-matching when stocks change sector or leave the eligible set, or a stock-level persistence of the real scores that the tether does not carry. Investigating it would mean designing another null, which the owner excluded.

## 24. Final null adequacy decision

**H029/H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE.**
- The failing measure is H029 name turnover, with the real value below all 5,000 worlds.
- Result file: `research/phase14/cp3/P14_CP3b_null.json` (SHA-256 7a48b1e5…; rows in `P14_CP3b_null_rows.json`, rows hash in the file).

## 25–26. New c_UP_H029 / c_INCREMENTAL_H030

**Not computed and not pinned.** The analysis script computes thresholds only for an adequate null. `qresearch.p14h029.C_UP_H029` and `C_INCREMENTAL_H030` remain `None`, so the runner refuses any real-mode config.

## 27. The old thresholds were not reused

- 0.2696 / 0.0059 are recorded in `p14h029.INVALID_THRESHOLDS`.
- The analysis script asserts that any new threshold differs from them, and a test asserts that a pinned threshold can never equal them.
- Neither value was used anywhere.

## 28. Thresholds and real result

- No threshold exists, and no real result exists.
- The run-order guarantee (thresholds pinned and merged before any real run) is intact: the config rule rejects a real run while `C_UP_H029` is `None`, and the real run id must be E031-10.

## 29. Exact next step

**STOP. Return to the owner.** Under D233 sections 33 and 39, no third null is designed or run, and no real H029 / H030 evaluation is made.

**Owner options:**
1. **Close H029 / H030 as not evaluable** under the pre-registered null-adequacy standard. Neither qualified nor rejected; the Business Improvement direction is left untested.
2. **Separate owner review of a third null.**
   - It would need a null that preserves both the sector composition and the month-to-month persistence of the real selection.
   - Excluded options (industry, sector + size, market-cap deciles, propensity, residualized) need an explicit owner decision.
   - It would be designed without any real return.
3. **Owner exception:** accept the turnover inadequacy and proceed with the sector null.
   - **Not recommended.** It is the exact failure the rule exists to catch: a null whose portfolios trade more than the real one would understate the real strategy's cost advantage and its persistence.

**Recommendation:** option 1.
- Two pre-registered nulls have failed adequacy on structural grounds, in different ways.
- A third design would be shaped by these structural observations. It would not be informed by performance, but it would add a further fork in the analysis.

## Integrity

| Item | Value |
|---|---|
| New experiments | E031-06 (canary), E031-07 / 08 (null), E031-09 (rerun); all infrastructure, all logged in `experiments/INDEX.csv` |
| Hypotheses / strategies in P14 | 2 (H029, H030) / 1 (S031, now v1.1) |
| Total P14 H029 / H030 experiments | 8 (E031-01..04 original null; E031-06..09 sector null); E031-05 and E031-10 never run |
| Real H029 / H030 runs | **0**. No performance computed. |
| Amendment and code committed before any run | 74316ea, b8a4e76 (the full test suite passed) |
| H028 / Data v3 | Unchanged; reproduced exactly |
| Holdout 2022-01-01 → 2026-08-31 | Sealed: no price, fundamental, SPY return or diagnostic accessed |

**STOP. Awaiting the owner's decision (section 29).**
