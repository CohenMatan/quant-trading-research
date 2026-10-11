# H023 — Score v2 Weight Optimization: pre-registration (FROZEN before any H023 run)

**Status:** FROZEN pre-registration (owner D199, 2026-10-11). SHA-256 pinned in `qresearch.p8h023.SPEC_SHA256` together with the code of `src/qresearch/lean/qr_h023.py`, and committed before any H023 QuantConnect run. Nothing in this document may change after any H023 statistic is seen. A genuine defect means STOP, document it and ask the owner.

## 1. Identity and permanent records

- **H023 is a new hypothesis.** It is not a rerun, rescue or correction of H022.
- **H022 / Score v1 stays permanently Rejected / NOT QUALIFIED exactly as tested.** Its record:
  - E024-07 on frozen Data v2;
  - t_IC 0.4771, mean IC 0.00755;
  - 80+ excess −12.57% a year;
  - monotonicity −0.40;
  - G1–G4 all FAIL.

  That record is never overwritten.
- **Question:** can a different weighting of the three existing frozen Score v1 layers give a robust cross-sectional predictive score on 2011–2017 that is strong and stable enough to justify one untouched validation on 2018–2021?
- **2011–2017 is TRAINING / DEVELOPMENT data for H023** (decisions 2011-01-31 → 2017-11-30, 83 months; the last response ends 2017-12-29). It is no longer out-of-sample for any score derived from it. A strong 2011–2017 result is evidence only that the search found a candidate worth testing. It is not evidence that Score v2 works out of sample.
- **Sealed:**
  - 2018-01-01 → 2021-12-31: sealed through the search, null, robustness, selection, diagnostics and plateau work. It is H023's first genuine external validation set.
  - Holdout 2022-01-01 → 2026-08-31: sealed for every purpose.

## 2. Frozen inputs (unchanged)

| Item | Frozen value |
|---|---|
| Data Infrastructure v2 | manifest `cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb` (`qresearch.datafreeze_v2`). Covers: universe, PIT market-cap repair, M2 timing, SEC identity, restatement guard, prices, corporate actions, H1–H7, share-class rules, FF12 sectors, research calendar |
| Score v1 layers | `qr_p7_score.py` / spec as pinned in `qresearch.p7score`: indicators, lookbacks, bands, fundamental and sector definitions, integer points per dimension |
| Population, response, calendar | H022 (`research/phase7/P7_predictive_spec.md`, SHA-256 `2c99f962…`), unchanged. The population is the eligible, fully scored kept-class stocks with no hard disqualifier H1–H7 (`qr_p7_export.eligible_flag`). It does not depend on the weights. The response is the next-session open → next monthly review close total shareholder return, demeaned by the population mean. |
| Statistics and null code | `qr_p7_pred.py` (`bc6fd8e8…`), `qr_xs.py`, `qr_h020_stats.py`, unchanged |
| Prepared H022 panel on Data v2 | `09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0` (`qresearch.p7pred_v2.PANEL_SHA256`). Every H023 run must reproduce it exactly or compute nothing. |
| Host | S025 = a subclass of the pinned H022 host S024 (uploaded byte-identical as `qr_s024`), which subclasses the frozen Data v2 host X998 (`qr_x998`). S025 adds only the per-stock layer subtotals and the H023 grid evaluation. |

## 3. What changes: the layer weights only

Per stock and review, the three frozen layer subtotals are:
- Technical = trend + momentum + risk points (maximum 40);
- Fundamental = profitability + cash conversion + balance sheet + growth (maximum 45);
- Sector = sector context (maximum 15).

The host checks Technical + Fundamental + Sector = the Score v1 total for every population row (0 mismatches required).

The normalised layers are `T = Technical/40`, `F = Fundamental/45` and `S = Sector/15`. The score is:

```
Score_v2 = wT·T + wF·F + wS·S,   wT + wF + wS = 100
```

The score is computed **exactly** as the integer `Z = 360·Score_v2 = 9·wT·Technical + 8·wF·Fundamental + 24·wS·Sector`. Ranks, ties, quintiles and the 80+ group (`Z ≥ 28,800`) therefore carry no rounding. At 40/45/15, Z = 360 × the Score v1 total, which gives the same ranks, quintiles and 80+ group as H022.

Nothing inside a layer changes:
- no new or removed indicator;
- no changed lookback, band or definition;
- no feature-level weight;
- no post-hoc rescaling.

## 4. The grid (92 configurations)

| Layer | Weights |
|---|---|
| wT | 10, 15, …, 80 |
| wF | 10, 15, …, 80 |
| wS | 0, 5, …, 30 |

The weights must sum to 100. Configurations per Sector weight:

| wS | 0 | 5 | 10 | 15 | 20 | 25 | 30 |
|---|---|---|---|---|---|---|---|
| Configurations | 13 | 14 | 15 | 14 | 13 | 12 | 11 |

That is 92 in all, listed in lexicographic (wT, wF, wS) order (`qr_h023.GRID`). The control 40/45/15 is index 42.

- **Adjacency:** one 5-point transfer between two layers, the third unchanged (L1 distance 10). There are 239 adjacent pairs.
- **Boundary:** wT or wF ∈ {10, 80}, or wS ∈ {0, 30}; 34 configurations lie on it.
- **No changes:** no weight is added after results, no 1-point step, and no boundary is extended. If the absolute best configuration, the winning plateau or the candidate touches the boundary, a **boundary flag** is reported. Any expanded search needs a new owner decision.

## 5. Fixed settings

| Setting | Value |
|---|---|
| Entry threshold | 80 (not optimised) |
| Primary horizon | one month (the H022 response) |
| Primary statistic | monthly Spearman IC (Pearson of average ranks), Newey-West t, lag 2 |
| Diagnostics only | 2- and 3-month horizons (overlapping, Newey-West lag 2 and 3, the H022 convention). They can never rescue a failed primary result. |
| Calendar blocks | 2011–12, 2013–14, 2015–16, 2017 |
| Halves | first 41 / last 42 of the 83 months |

## 6. Metrics for every configuration

Computed by `qr_h023.summarise`, with formulas identical to `qr_p7_pred.summarise`. Tests show equality to < 1e-12 for the control and other configurations, in the real and null worlds.

- **Ranking:**
  - monthly IC series;
  - mean IC, Newey-West SE and t_IC (lag 2);
  - positive months.
- **80+ group:**
  - mean monthly demeaned return;
  - annualised (× 12);
  - 80+ stock-months;
  - months with an 80+ stock;
  - mean 80+ count per month.
- **Quintiles** (frozen average-rank quintiles):
  - Q1..Q5 mean demeaned return, monthly and annualised;
  - Q5 − Q1;
  - monotonicity Spearman of (1..5, quintile means).
- **Stability:**
  - IC by decision year;
  - first- and second-half IC;
  - block sums and shares of the summed IC;
  - largest block share (infinite if the summed IC ≤ 0).
- **Structure:**
  - Score_v2 distribution (pooled stock-months: min, p10, p25, median, p75, p90, max, mean);
  - stock-months and mean monthly counts at 75+, 80+, 85+ and 90+;
  - months with ≥ 1 stock at each threshold.

## 7. Search-level null and c_SEARCH

**Null worlds.** Each world uses the frozen H022 identity tether (`qr_p7_pred.Tether(seed)`: one stratum, no self-matches, partners kept while both stay in the population). One tether permutation per date is applied to the **whole grid**. Each receiving stock takes all three layer subtotals of its partner, while responses stay with the receiver. Every configuration's complete statistics are then recomputed, exactly as in the real optimiser.

**Count and runs.** 5,000 worlds, seeds 1..5,000 (the H022 seeds):
- E025-02..06: batches of 1,000;
- E025-07: a pre-specified determinism rerun of seeds 1–25, which must be identical.

If 5,000 worlds proved infeasible, the work STOPs and the cost is reported. The count is never reduced silently. The local cost measured before any run is about 0.1 s per world, the same as an H022 world.

**Per-world record** (`qr_h023.null_record`):
- the maximum t_IC across the 92 configurations, and its index;
- the control column's t_IC and mean IC;
- the maximum t_IC across the grid on each walk-forward training prefix (decision years < 2014, < 2015, < 2016, < 2017);
- the number of configurations meeting the plateau conditions;
- the number of robust plateaus and the largest plateau size;
- `cstar`: the largest t_IC among plateau members that pass D2–D5 with mean IC > 0;
- the number of configurations passing D2–D5 with mean IC > 0, and their largest t_IC.

**Integrity checks (pre-registered):**
1. Every null run reproduces the pinned panel digest and the pinned layer-subtotal digest from the canary.
2. The seeds are exactly 1..5,000, with no duplicates.
3. The rerun is identical.
4. For every seed, the control column's t_IC equals the frozen H022 / Data v2 null world of the same seed (`research/phase7/cp6/P7_CP6_null_worlds.json.gz`) within 1e-9. This is the same tether on the same panel.

**The threshold.**

```
c_SEARCH = max(k-th largest of the 5,000 null max_t_IC_across_grid, 2.326),   k = ceil(0.01 × 5,000) = 50
```

This is the frozen one-sided empirical order-statistic convention of H022 (`qr_xs.critical_value`, `qr_h023.critical_value`).

- **Fold thresholds:** for walk-forward fold Y, c_fold(Y) applies the same rule to the null maxima on that fold's training prefix. These are diagnostic only.
- **Pinning:** c_SEARCH, the c_fold values and the null result hash are pinned in `qresearch.p8h023` and merged **before** the real search.
- **Reported:**
  - the full-procedure false-promotion rate, the share of null worlds with `cstar > c_SEARCH`;
  - the share with any configuration passing D1–D5 (no plateau);
  - the null-world percentile and p-value of the real highest t_IC: `(1 + #{null max_t ≥ real max_t}) / (1 + 5,000)`.

## 8. Development filters (fixed; never changed after results)

A configuration is **development-qualified** only if all five hold on 2011–2017:

| Filter | Requirement |
|---|---|
| D1 | t_IC > c_SEARCH and mean IC > 0 |
| D2 | 80+ annualised demeaned return ≥ +3.0% |
| D3 | quintile monotonicity ≥ 0.90 and Q5 > Q1 |
| D4 | first-half IC > 0, second-half IC > 0, and largest calendar block ≤ 50% of the summed IC |
| D5 | 80+ stocks in ≥ 60 of the 83 months, and mean 80+ count ≥ 2 a month |

For walk-forward training prefixes, D5's month count is scaled: months with 80+ / months ≥ 60/83.

## 9. Robust plateau

1. The base set is the configurations with mean IC > 0, 80+ annualised > 0, Q5 > Q1 and both half ICs > 0.
2. Its **connected regions** are the connected components under the adjacency of section 4.
3. In each region, keep the members whose t_IC ≥ 0.80 × the highest t_IC in that region.
4. Every connected component of the kept members with **≥ 4 configurations** is a robust plateau.

A single isolated optimum is never enough.

## 10. Selection rule (frozen; deterministic)

1. A **candidate exists** if and only if at least one configuration is both development-qualified (D1–D5) **and** a member of a robust plateau.
2. **Eligible plateaus** are the robust plateaus with ≥ 1 qualified member. They are ranked by:
   1. most configurations;
   2. highest median t_IC across the plateau;
   3. highest median 80+ annualised;
   4. (determinism only) smallest first grid index.
3. **Within the winning plateau,** the candidate is its **L1 medoid** among its qualified members: the configuration with the smallest total L1 weight distance to **all** members of the plateau. Ties go to:
   1. higher t_IC;
   2. smaller L1 distance to 40/45/15;
   3. (determinism only) lexicographic weights.
4. **Also reported, never used:**
   - the unrestricted ranking of all robust plateaus and the medoid of the top one over all its members, which equals the candidate whenever that medoid is qualified;
   - the **absolute best historical configuration** (highest t_IC).

   The selected configuration may differ from the absolute best. Robustness, not the historical maximum, is the objective.
5. **No manual choice.** Nothing is chosen by CAGR, SPY outperformance, terminal wealth, Sharpe or drawdown. No portfolio is evaluated.

**Outcome:**

| Situation | Result |
|---|---|
| A candidate exists | Named **Score v2 Candidate**, status **DEVELOPMENT CANDIDATE — NOT YET VALIDATED**. Frozen per section 13 before anything else. Checkpoint result: **DEVELOPMENT CANDIDATE — SCORE V2 FROZEN, VALIDATION STILL SEALED**. |
| No candidate | **H023 — NO ROBUST SCORE V2 CANDIDATE**. Nothing is widened: no larger grid, no other horizon, no other threshold, no feature-level weights, no removal of Sector, no new indicators. |

## 11. Weight-surface analysis (descriptive)

For all 92 configurations:
- t_IC, mean IC, 80+ annualised, monotonicity, half ICs, largest block share, plateau membership, D1–D5 pass/fail;
- maps over (wT, wS) with wF = 100 − wT − wS.

The report also covers:
- whether the surface is a **broad plateau** or a **sharp isolated peak**: plateau sizes, the share of the grid within 80% of the best t_IC, and the t_IC of the best configuration's neighbours;
- descriptive layer conclusions only, from the slopes of t_IC against each weight: higher Technical, Fundamental or Sector weight generally helped, hurt or did not matter.

No further search may be launched from these observations.

## 12. Walk-forward diagnostic (never used to redefine anything)

For Y = 2014, 2015, 2016, 2017:
1. **Train** on decision years < Y (expanding from 2011).
2. **Select** by the frozen rule of sections 8–10 on the training months, with D1 against c_fold(Y).
3. **Observe** decision year Y (2017: 11 months).

If the strict rule gives no candidate in a fold, the fold falls back, with a label, to:
1. the unrestricted plateau medoid;
2. otherwise the highest-t configuration.

**Reported:**
- the fold selections and pairwise L1 distances;
- clustering (all fold selections within L1 ≤ 20 of each other = "cluster");
- next-year mean IC and 80+ annualised per fold;
- the aggregate pseudo-out-of-sample IC: the four observation years' monthly ICs of their own fold selections, with mean, Newey-West t (lag 2) and positive months.

## 13. Candidate freeze (only if a candidate exists; before any 2018–2021 access)

Pinned in `qresearch.p8h023`, then committed and merged:
- the exact weights and formula;
- the Score v1 layer hashes (`qresearch.p7score`) and the Data v2 manifest;
- the training period;
- the grid hash;
- the optimiser-null result hash and c_SEARCH;
- the plateau definition, the selected plateau's members and the selection rule (this spec's SHA-256);
- the real-search result hash.

The **candidate hash** is the SHA-256 of the canonical JSON of all of the above (`qresearch.p8h023.candidate_record`).

## 14. Pre-registered 2018–2021 validation (sealed; requires a separate owner approval)

**Prerequisite.** Frozen Data v2 ends on 2017-12-31 by construction. Before any validation statistic exists, the Data v2 reference layers must be extended to 2018–2021 under the **identical frozen rules**. That data build computes no return and needs its own owner approval. Its validation panel is then frozen and pinned.

| Element | Frozen value |
|---|---|
| Decisions | the monthly reviews 2018-01-31 → 2021-11-30 (47 months; responses end at the 2021-12 review) |
| Score | the frozen Score v2 Candidate |
| Population and response | the H022 / H023 population and one-month demeaned TSR response |
| Primary statistic | monthly Spearman IC, Newey-West lag 2 |
| Diagnostics | 2- and 3-month horizons, which cannot rescue a failure |

**Gates** (all four required):

| Gate | Requirement |
|---|---|
| V1 | Before the real mapping, a fresh identity-tethered null (5,000 worlds, H022 method) on the frozen validation panel gives **c_IC_VALIDATION** = max(50th largest null t_IC, 2.326), pinned. Then real t_IC > c_IC_VALIDATION and mean IC > 0. |
| V2 | 80+ annualised demeaned return ≥ +3.0% |
| V3 | quintile Spearman ≥ 0.90 and Q5 > Q1 |
| V4 | 2018–2019 mean IC > 0, 2020–2021 mean IC > 0, and no single calendar year > 50% of the summed IC |

All four pass → **H023 VALIDATED**. Any failure → **H023 NOT VALIDATED**. No tuning after 2018–2021 is seen, and the Holdout stays locked.

## 15. Not allowed in H023

- Portfolio optimisation: K, entry, exit, regime limits, sector cap, replacement buffer, position size, holding period, costs.
- Wealth, CAGR, SPY, Sharpe or drawdown selection.
- Any change to the threshold 80, the horizon or the features.
- Any access to 2018–2021 or the Holdout.

## 16. Run plan

1. Canary **E025-01** (S025 canary mode, synthetic responses only; no real IC). Checks:
   - layer subtotals sum to the Score v1 total;
   - the control Z = 360 × total;
   - grid evaluation = `qr_p7_pred.run_world` for the control and other configurations, in the real and null assignments, on synthetic responses;
   - tether structure;
   - determinism;
   - runtime;
   - panel digest = pinned;
   - the H022 canary checks (inherited).

   The canary pins the **layer-subtotal digest**.
2. Nulls **E025-02..06** (seeds 1..5,000) and rerun **E025-07** (seeds 1–25).
3. Compute c_SEARCH and the fold thresholds offline (`research/phase8/cp1/P8_CP1_null.py`). Pin them, commit and merge.
4. ONE real development search, **E025-08** (S025 real mode, pinned provenance): the full grid with every metric, the in-host selection and the walk-forward diagnostic. The real IC matrices are exported for offline verification (`research/phase8/cp1/P8_CP1_result.py`, written before the run).
5. Freeze any candidate (section 13), then write P8-CP1, then STOP.
