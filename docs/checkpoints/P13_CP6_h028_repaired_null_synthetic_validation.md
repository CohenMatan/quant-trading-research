# P13-CP6 — H028 Repaired Null Synthetic Validation

**Owner decision D239** (message verbatim in `docs/owner/2026-10-18_p13cp6_h028_repaired_null_synthetic.md`).

**Scope:** synthetic data, offline code and methodological validation only. No real-data run, no QuantConnect run, no H028 holdings or returns, Holdout untouched.

## Result

**B — METHOD NOT VALIDATED. R1 IS NOT FEASIBLE AT THE CURRENT UNIVERSE SIZE**, and a 4× larger universe does not fix it.

- **The pre-registered matching-feasibility gate failed.** A Top-15 portfolio built like H028 sits in the joint tail of the very exposures the test must control (LOWVOL, growth/value, profitability).
  - No matching method finds comparable stocks for enough positions while keeping the exposure imbalance below the design limit (absolute standardized difference < 0.10).
  - The twins are always systematically less extreme than the stocks they replace.
- **No method could be frozen, so the final synthetic calibration and power study was not run** (owner sections 5, 13, 16 and 24). Running it on a method already known to break the balance requirement would only invite repeated repair.
- **The secondary R3 factor regression** (pre-declared synthetic diagnostic) **is not an alternative**:
  - When growth and profitability are priced but no stock skill exists, it rejects at **14%** instead of the nominal 1%.
  - Its power against a strong planted stock-specific signal is only **29%**.

**H028 remains REJECTED. Nothing here changes it.**

---

## 1. Repository state and sources

- **Start state:** `main` = `8d03e10` (PR #103); last decision D238; last experiment E031-09; no `HOLDOUT_UNLOCK.md`.
- **Session checks:** QuantConnect credentials present (values never printed); site reachable (HTTP 200).
- **Sources read (read-only):**
  - P13-CP5 and D238;
  - `research/phase13/H028_spec.md`;
  - `research/phase13/cp1/P13_CP1_result.json` and `P13_CP1_null.json` (E030-05);
  - `research/phase13/cp5/P13_CP5_artifacts.json`;
  - P14-CP4 and P14-CP6a.
- **New files:**
  - `src/qresearch/r1synth.py`: synthetic generator.
  - `src/qresearch/r1twin.py`: H028-style portfolio, M1–M4 matching, twin worlds in Mode A and Mode B, Monte Carlo p-value, R3.
  - `research/phase13/cp6/P13_CP6_feasibility.{py,json}`: development fixture.
  - `research/phase13/cp6/P13_CP6_r3_diagnostic.{py,json}`.
  - `tests/test_p13_cp6.py`.
  - All offline; nothing is uploaded to QuantConnect.

## 2. Approved scope (D239)

**Approved:** synthetic code, offline synthetic experiments, tests, documentation, checkpoint and PR.

**Not approved (none of it was done):**
- any real-data H028 run, real holdings export, real statistic or real-return null;
- the Holdout;
- any change to H028 or its gates;
- H031 or an offensive strategy;
- purchases;
- closing Phase 13 or H029 / H030.

## 3. H028 status preserved

**ORIGINAL RESEARCH STATUS: H028 REJECTED** (D220; B4 failed: 2015–2017 vs LV15 −0.006). Its conditional-null p ≈ 0.0004 remains structurally suspect (D238). Nothing was re-run, refitted or reclassified.

## 4. D238 root cause (summary)

- The H028 null gives each recipient stock the ten non-LOWVOL features of a partner ("donor") stock. A pair survives only while both stay in the universe.
- About 17.6% of pairs re-form each month because of universe churn.
- Each re-formation moves a feature path to a different stock, which adds rank changes, turnover and costs to null worlds only (P13-CP5).

## 5. Conditional exposure mismatch

The old null drew the ten features from their overall distribution, not given each stock's LOWVOL. Committed null worlds therefore differ from real H028:

| | Real H028 | Null worlds (median) |
|---|---|---|
| Up-capture | 0.97 | 0.71 |
| LOWVOL share of coefficient weight | 0.155 | 0.31 |

(Sources: `P13_CP1_null.json`, `P13_CP5_artifacts.json`.) Factor differences could therefore be mistaken for skill. The repaired test had to control those exposures explicitly, and that is exactly what proved infeasible.

## 6. R1's exact statistical question

**R1 null hypothesis:** given the frozen strategy's realised positions and trade dates, each held stock's subsequent returns are exchangeable with those of comparable stocks. "Comparable" means the same sector, with similar point-in-time values of the controlled characteristics.

**Two control sets were evaluated:**
- **V1, "beyond LOWVOL":** LOWVOL and size.
- **V2, "beyond LOWVOL + known priced exposures":** LOWVOL, size, book-to-market, profitability, momentum and past beta.

Only V2 can separate Explanation A (exposure) from Explanation B (selection) for H028.

## 7. What R1 cannot prove

Even if R1 were feasible and calibrated:
- It conditions on the selected holdings and trade schedule.
- It cannot validate the full learned-score pipeline (training, λ, fitting, construction).
- It cannot show that the pipeline would find profitable selections on unseen data.
- An R1 success would never be full-pipeline validation.

## 8–9. Matching feasibility study and methods compared

**Setup:**
- Development fixture: seeds 900001–900008, not reused for anything else.
- 475 stocks, 84 evaluation months.
- Measured over every real buy and every continuing holding (each a possible twin draw).
- Rejection rates were never computed in this study.
- File: `research/phase13/cp6/P13_CP6_feasibility.json`, SHA-256 e8cfd751…

**Selection processes (scores computed without future information):**
- **P1:** H028-like composition. LOWVOL carries about 16% of the weight, as it carries 15.5% of the committed H028 coefficients; this is structural calibration only, never tuned to wealth.
- **P1L:** LOWVOL-dominant, LV15-like.
- **P2:** P1 plus a planted predictor.
- **P3:** persistent random selection.

**Imbalance** is the matched-only standardized difference between real and twin characteristics. A negative LOWVOL value means the twins are more volatile than the real stock.

| Method | P1: matched | P1: LOWVOL | P1: BM | P1: PROF | P1L: matched | P1L: LOWVOL |
|---|---|---|---|---|---|---|
| **M1** exact cells, V1 (11 sectors × 5 LV × 3 size = 165 cells, about 2.9 stocks per cell; 23% singleton cells) | 92.5% with ≥ 1 alternative | — | — | — | 92.7% | — |
| **M1** exact cells, V1 + BM terciles (495 cells, about 1 stock per cell; 55% singleton cells) | 67.5% with ≥ 1 alternative | — | — | — | 69.5% | — |
| **M2** hierarchical (V1 cell → sector × LV quintile → sector × LV tercile; ≥ 3 alternatives) | 99.1% (L1 63%, L2 32%, L3 4%) | −0.08 | −1.15 (uncontrolled) | +0.92 (uncontrolled) | 98.9% | −0.23 |
| **M3** V1, within sector, caliper 0.15, k = 10, ≥ 3 | 77.9% | −0.10 | −1.19 (uncontrolled) | +0.96 | 69.7% | −0.24 |
| **M3** V1, within sector, caliper 0.20 | 90.2% | −0.16 | −1.18 | +0.97 | 85.5% | −0.34 |
| **M3** V2, within sector, caliper 0.20 | **21.0%** | −0.19 | −0.24 | +0.18 | 20.1% | −0.42 |
| **M3** V2, within sector, caliper 0.30 | 86.9% | **−0.37** | **−0.48** | +0.37 | 86.2% | −0.66 |
| **M3** V2, sector relaxed to 3 groups, caliper 0.25 | 96.9% (63% of twins cross-sector) | −0.26 | −0.34 | +0.27 | 96.6% | −0.51 |
| **M3** V2, no sector constraint, caliper 0.20 | 97.6% (87% cross-sector) | −0.18 | −0.24 | +0.18 | 97.6% | −0.38 |
| **M4** portfolio-level exposure matching (rejection sampling, tolerance 0.05) | acceptance ≈ 0.0006 (V1), 0 (V2) | — | — | — | 0 | — |

**Control (P3, random persistent selection):** every method balances well. For example, M3 V2 within sector at caliper 0.30 gives 90.5% matched with all imbalances ≤ 0.02. The code works; the problem is the selected portfolio's position in the tail.

**Universe-size sensitivity** (seeds 900001–900003):
- V2 within sector, caliper 0.25: LOWVOL imbalance −0.28 at 475 stocks (60% matched), −0.30 at 950 (83%), −0.31 at 1,900 (94%) for P1; −0.55 / −0.55 / −0.53 for P1L.
- A larger universe raises coverage but **not** balance. A Top-15 drawn from a bigger universe is simply more extreme.

## 10. Frozen matching method

**None.** No method meets the design targets (owner section 17: absolute imbalance < 0.10 on the controlled exposures with credible coverage):

| Option | Why it fails |
|---|---|
| V2 within sector | Coverage ≤ 25% at caliper ≤ 0.2; LOWVOL/BM imbalance 0.37–0.66 once coverage exceeds 85% |
| V2 with sector relaxed | Gives up sector control (63–87% of twins cross-sector) and still leaves LOWVOL / BM imbalance of 0.18–0.51 |
| V1 | Only answers "beyond LOWVOL". Its own LOWVOL imbalance is −0.10 to −0.16 (P1) and −0.24 to −0.34 (P1L), and it leaves growth/profitability imbalance of about 1 standardized unit, which is exactly the alternative explanation for H028 |
| M4 | Practically never finds a matching portfolio |
| M1 / M2 | M1 cells are too sparse once book-to-market is added. M2 answers only V1, and its fallbacks change the question for 36% of positions |

By the owner's rule (section 16): **R1 NOT FEASIBLE AT CURRENT UNIVERSE SIZE.** The size sensitivity shows it is structural for concentrated Top-15 portfolios.

## 11. Matching support and fallback policy

- **Implemented and tested in code:**
  - M3 with a level-1 caliper and an optional level-2 caliper;
  - minimum support;
  - **honest abstention**: an unmatched position is self-matched, so it contributes no evidence either way;
  - duplicate avoidance within a world.
- **Not frozen**, because no method passed (section 10).
- **Relaxing the sector constraint** is reported above as an explicit change of question, never applied silently.

## 12. Entry, exit and delisting rules (implemented in `r1twin.twin_sim`, tested)

| Event | Real-style portfolio | Twin |
|---|---|---|
| Real slot closes (dropped by score, ineligible, or delisted) | Sold at the next open (delisted: cash at the delisting value, no order) | The twin is sold too |
| Twin leaves the eligible set while the real slot continues | — | Sold at the next decision; a replacement is drawn from the real stock's current pool and bought with the proceeds (two real trades in Mode B; free under Mode A's controlled schedule) |
| Twin delisted | — | Cash at the delisting value; refilled at the next decision |
| Unmatched draw | — | Self-match (abstention) |
| Final month | Liquidated after costs | Liquidated after costs |

No replacement is free in Mode B. No draw uses future information.

## 13. Mode A: controlled comparison

- With ρ = twin equity / real equity before the month's trades, each twin world pays ρ × the real portfolio's sell and buy costs.
- New slots are bought at ρ × the real purchase amount (capped by the world's cash), and final liquidation is ρ-scaled.
- Twin-only replacements cost nothing.
- Verified: a world of self-matches reproduces the real wealth **exactly** (relative error < 1e-10).

## 14. Mode B: investable comparison

- Each twin pays its own $7 per order plus 10 bps slippage.
- Sizing follows the real cash-constrained rule on the twin's own equity; replacements are funded by the replaced slot's proceeds after costs.
- Verified:
  - self-matches reproduce the real wealth exactly;
  - with no churn and no delistings, twin buys and sells equal the real portfolio's exactly, with 0 replacements.

## 15. Point-in-time and look-ahead safeguards

- **Prefix test:** a shorter panel is an exact prefix of a longer one with the same seed (test), so nothing at month t depends on later draws.
- **Momentum and beta** are computed from each stock's own past simulated returns only (12-1 months; 36-month OLS with at least 12 months).
- **Percentiles and z-scores** are taken within the decision date's eligible set.
- **Twins:** pools are built from the decision date's eligible set and characteristics; the real portfolio's decisions are prefix-stable (test).

## 16–17. Synthetic generator design and version

`r1synth.panel` (file SHA-256 f8d0c997…):
- 475 eligible stocks, 11 sectors of unequal size;
- persistent correlated latent characteristics (LV, SIZE, BM, PROF, planted Q, four uninformative features), with LV driving true volatility and correlating with beta;
- market and sector factors;
- characteristic premia, stationary or time-varying;
- about 43 entries a month (calibrated to the real churn of about 44 a month, E029-01), half of them re-entries;
- delistings with a hazard that rises with volatility;
- sector reclassification;
- optional growth or composition drift.

`r1twin` SHA-256 4d50a537….

## 18–19. Scenarios and seed ranges

**Not run.** The pre-registration of scenarios S1–S12 was conditional on a frozen matching method (owner section 13). Reserved ranges:
- final evaluation: none issued;
- feasibility: 900001–900008;
- R3 diagnostic: 910001–913200.

## 20. Frozen statistical acceptance criteria

Not reached, for the same reason. The criteria the final evaluation would have used are recorded for any future version:
- α = 0.01 one-sided, with p = (1 + #{twin wealth ≥ real}) / (R + 1);
- at least 500 panels × 500 twin draws per calibration scenario;
- rejection rate ≤ 0.02 at α = 0.01;
- 0.035–0.065 at α = 0.05;
- a one-sided Kolmogorov–Smirnov p-value-distortion bound;
- power ≥ 0.80 for the strong planted signal;
- absolute standardized imbalance < 0.10 on the controlled exposures.

## 21–27. Calibration, confidence intervals, power, churn, correlated factors, growth mismatch, thin cells

**R1:** not run, because the feasibility gate failed.

**What the evidence shows instead:**
- **Thin cells:** with V1 at caliper 0.15, 22% of P1 positions are unmatched (abstentions).
- **Growth mismatch:** under V1, twins have BM about 1.2 and PROF about 1.0 standardized units away from the real holdings. That is the "growth/profitability exposure looks like skill" problem, documented directly.

## 28–29. Exposure balance and matching coverage

See the table in sections 8–9 and `P13_CP6_feasibility.json` (balance per dimension, all methods, all selection processes, three universe sizes).

## 30–35. Forced exits, costs and artificial turnover

The accounting is implemented and unit-tested:
- exact self-match identity in both modes;
- Mode B trade equality with no churn;
- commissions = $7 × orders;
- wealth = product of monthly returns × capital;
- holdings ≤ 15 and ≤ 3 per sector.

The zero / base / 2× cost comparisons and the churn turnover checks belong to the final evaluation, which was not run.

## 36. Limitations of statistical validity

- **R1** fails before calibration on balance.
- **R3**, from the pre-declared synthetic diagnostic (`research/phase13/cp6/P13_CP6_r3_diagnostic.json`, SHA-256 ebbf2792…; 200 panels per configuration; one-sided rejection rates):

| Synthetic truth | R3a (market + LOWVOL) at 1% / 5% | R3b (+ BM, PROF, momentum) at 1% / 5% |
|---|---|---|
| Nothing priced (P1) | 0% / 1% (conservative: costs) | 0% / 1% |
| LOWVOL priced (P1) | 1.0% / 5.0% | 1.5% / 5.5% |
| LOWVOL + growth + profitability priced, no skill (P1) | **50.5% / 69.5%** | **14.0% / 31.0%** |
| Strong planted skill (P2) | 32% / 56% | 29% / 50% |

**Reading:** a regression on tercile factor portfolios cannot fully absorb characteristic exposures, so factor exposure still looks like alpha. With 84 months, the power against a strong signal is low.

## 37. R3 design (prospective, secondary)

- **Factors:** point-in-time, equal-weight, from the eligible set.
  - LVF = lowest-LOWVOL quintile minus the universe.
  - BMF, PROFF and MOMF = top minus bottom tercile.
- **Regression:** monthly portfolio minus SPY on [SPY, LVF] and on [SPY, LVF, BMF, PROFF, MOMF], with Newey–West standard errors (lag 2).
- **Assumptions:** linear, constant exposures; stationarity; correct factor proxies.
- The synthetic diagnostic shows the third assumption fails materially. R3 is therefore unsuitable as a substitute for R1 and of limited value as a secondary test.

## 38. Synthetic simulation counts

| Study | Panels | Twin draws |
|---|---|---|
| Feasibility | 32 (8 seeds × 4 selection processes) | — |
| Size sensitivity | 18 | — |
| R3 diagnostic | 800 | — |
| Smoke tests | 3, plus unit-test fixtures | 2 × 500 |

No simulation failed.

## 39. Determinism

Same seed → identical panel and identical twin wealth vectors (checked). The feasibility and R3 outputs are reproducible from the committed scripts.

## 40. Runtime and memory

- One 475-stock panel plus 2 × 500 twin worlds: 1.1 s, peak RSS 46 MB, single core.
- Feasibility study: 393 s. R3 diagnostic: 276 s.
- No QuantConnect resources were used. The final evaluation as planned (about 6,500 panels) would have fitted offline in roughly 1 hour on 4 cores.

## 41. Failed tests and unresolved limitations

- **Failed:** the matching-feasibility gate (section 10).
- **Also inadequate:** R3 calibration under priced factors (section 36).
- **Open dependency:** any real R1 would need H028's real holdings, which E030-05 never exported (P13-CP2). This was **recorded, not worked around**.
- **Unexplored alternative, deliberately not built:** bias-corrected (regression-adjusted) matching. It would rely on the same factor-model assumptions R3 just failed, cannot produce an investable Mode B, and would be a new method version needing separate approval.

## 42–44. Confirmations

- **No real H028 run:** no QuantConnect run, no real holdings, prices or returns, no new real statistic.
- **Holdout untouched:** no data from 2022-01-01 → 2026-08-31.
- **H028 unchanged:** status REJECTED; gates, spec and results unchanged; no data manifest touched.

## 45. Overall feasibility recommendation

- **Stop the H028 null repair.** The decisive question, H028's advantage as exposure versus stock selection, cannot be answered by a matched-null test on this universe and portfolio design.
- The available regression alternative is miscalibrated in the very case that matters.
- What remains possible is a **prospective** comparison of a frozen strategy against **transparent exposure benchmarks** on data that did not shape it. Examples of such benchmarks: a beta-matched LV15 + SPY mix fixed in advance; investable low-volatility and quality ETFs.
- Under the governance rules, that is a new hypothesis and needs separate approval.

## 46. Exact next approval required

Choose one:
1. **Accept classification B and close the H028 null-repair line (recommended).** H028 stays REJECTED, and its conditional-null significance stays unreliable with no repair available. Closing Phase 13 is still a separate decision you have not taken.
2. **Approve a narrower R1-V1-only synthetic validation** ("beyond LOWVOL / sector / size") as a new method version. **Not recommended**: it cannot separate growth/profitability exposure from skill, and its own LOWVOL balance is borderline.
3. **Approve a bias-corrected matching design study (R1b).** **Not recommended**, given the R3 evidence.

**Still outstanding and untouched:** H029 / H030 (P14-CP6a).

## Final classification

**B — METHOD NOT VALIDATED**
(matching is inadequate: R1 NOT FEASIBLE AT CURRENT UNIVERSE SIZE; a 4× larger universe does not repair the balance; R3 is miscalibrated under priced factors.)

**H028 FORMAL STATUS REMAINS REJECTED.**

**STOP.**
