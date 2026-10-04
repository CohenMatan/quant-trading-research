# P3-CP3 — Systematic Technical Search Stage-1 Result (STOP)

- **Date:** 2026-10-04.
- **Owner authorisation:** "Phase 3 — Authorise First Real Systematic Search Runs E018-01 to E018-07" (2026-10-04, D136; summary `docs/owner/2026-10-04_authorise_E018_search.md`).
- **Executed exactly as frozen in `research/phase3/P3_spec.md`** (SHA-256 `d7fa1123…`):
  1. 500 null worlds first;
  2. the threshold computed, committed and pinned;
  3. then the single real search over the 1,533 configurations and the frozen Stage-1 procedure.
- **Not done:** no 2018–2021 data, no Holdout, no S019, no purchase, no manual intervention.

## Verdict

**NO ROBUST TECHNICAL EDGE FOUND.**

| Measure | Result |
|---|---|
| **Real search statistic T** (the plateau level of the best connected cluster) | **0.0127** (≈ 1.3% a year of log excess growth over SPY) |
| **Frozen null threshold τ** | **0.0284** |
| Real T vs the 500 no-edge worlds | Lower than 31% of them (69th percentile) |
| **Empirical p-value** | **0.31** |
| **Search-null gate Q1** | **FAIL** |
| Clusters above τ | **None** |
| **Walk-forward Q2** | **FAIL**: the procedure's year-by-year picks lost 6.8% (log) vs SPY and 1.8% vs the equal-weight universe over 2014–2017 |

**In plain words:**
- The real technical rules did not find anything that the same optimizer does not routinely "find" in fake worlds where technical signals carry no information about the stock's own future return.
- By several raw measures, the real search's best winners were **less** impressive than those of a typical fake world.
- Under the frozen rules, Phase 3 Stage 1 ends here:
  - nothing is promoted;
  - **no candidate is eligible for LEAN finalist verification, S019 or the 2018–2021 internal OOS.**

---

## 1. Runs executed

**All seven authorised runs completed on the first attempt,** with every integrity check passing. All ran on S018 v1.0, a byte copy of the fidelity-verified engine, window 2010-03-01 → 2017-12-31, with `--owner-approved D136`.

| Run | Content | QC backtest | Code commit | Runner time | Peak memory |
|---|---|---|---|---|---|
| E018-01 | Null worlds, seeds 1–100 | 9cd376f5… | 2d55c02 | 2,318 s | 4.35 GB |
| E018-02 | Null worlds, seeds 101–200 | 3bddff38… | 0800ce3 | 2,131 s | 4.26 GB |
| E018-03 | Null worlds, seeds 201–300 | 031af5fd… | a5a39b7 | 1,963 s | 4.25 GB |
| E018-04 | Null worlds, seeds 301–400 | 7766da07… | 6c7dd09 | 1,960 s | 4.34 GB |
| E018-05 | Null worlds, seeds 401–500 | 061bc0b7… | 8d67a3b | 1,960 s | 4.17 GB |
| E018-06 | Block-null worlds 1001–1100 (diagnostic) | 9b41514f… | 3d12e58 | 1,873 s | 4.36 GB |
| **E018-07** | **Real world: all 1,533 configurations** | **277bf4f7…** | **3a1c915** (the threshold commit) | 483 s | 4.04 GB |

- The code commits differ only because the queue commits each run's results before starting the next. The engine and spec are identical in all runs.
- **Before any run:** the per-world summary gained reporting-only "apparent winner" fields for your item 15 (D136). Nothing that selects anything changed.

## 2. Technical reruns

**None.** No run failed, stalled or was repeated.

## 3. 2018–2021 status

**Not accessed.**
- Every run ends 2017-12-31 (enforced by `experiment.validate` and by the algorithm itself).
- No candidate exists for the internal OOS, so 2018–2021 remains unused by Phase 3.

## 4. Holdout

**Untouched.** 2022-01-01 → 2026-08-31 is locked; `HOLDOUT_UNLOCK.md` is unchanged.

## 5. Null-generation method

**Primary null: within-date permutation (spec §12.1).**
- Each session, a seeded permutation maps every eligible stock's **signal row** to a randomly chosen eligible **traded stock**.
- **Preserved:**
  - real returns, regimes, volatility, correlation and common shocks;
  - universe membership, delistings, splits and dividends;
  - each configuration's daily signal counts (hence its timing, turnover, cash and costs);
  - the correlation between configurations;
  - all portfolio mechanics and costs.
- **Broken:** only the link between a stock's own technical signal and its own future return.
- **The whole optimizer ran on every fake world:** gates, score, plateau, clusters, T, simplicity ranking and walk-forward.
- **Secondary (diagnostic only):** a 63-session block permutation.

**Nothing in the null method changed after the runs began.**

## 6. Null worlds completed

- **500 primary** (seeds 1–500), all completed.
- **100 block-null** (seeds 1001–1100), all completed.

## 7. Null pass counts by stage (primary null)

| Stage | Worlds |
|---|---|
| Null worlds | 500 |
| With ≥ 1 eligible configuration | 500 |
| With a connected cluster of ≥ 3 | 494 |
| Pass Q1 (T above τ estimated from the other 499 worlds) | 25 (5.0%, by construction) |
| Pass Q2 walk-forward | 72 (14.4%) |
| **Pass Q1 and Q2 (the full search-stage pipeline)** | **8** |

**Block null (diagnostic):** 100 worlds; Q1 5, Q2 18, both 1.

## 8. Null false-pass estimate

**8 / 500 = 1.6%:** the probability that this search stage would wrongly pass a technical edge that does not exist. Q3 and Q4 would reduce it further, so for the whole chain it is an upper bound.

## 9. Confidence interval

- **Primary:** Clopper–Pearson 95% interval **0.69% – 3.13%**.
- **Q1 alone:** 5.0% (3.3% – 7.3%).

## 10. Frozen null threshold

**τ = 0.028423616730466103**, the 25th largest of the 500 null T values (equivalent to the permutation p ≤ 0.05).

| Null T quantile | Value |
|---|---|
| 5% | −0.018 |
| 25% | −0.003 |
| 50% | 0.006 |
| 75% | 0.015 |
| 95% | 0.028 |
| 99% | 0.043 |
| Max | 0.072 |

- **Block-null threshold** (diagnostic): 0.0348.
- **Files:**
  - `research/phase3/P3_null_result.json`;
  - per-world history `research/phase3/P3_null_worlds.csv` (600 rows).

## 11. Proof that the threshold was frozen before the real search

| Item | Value |
|---|---|
| **Threshold commit** | **`3a1c9151c3e11c94534e2546c3c1c68386b8416a`** (D137), pushed 2026-10-04 ≈ 09:13 UTC; clean tree verified |
| `P3_null_result.json` SHA-256 | `46c92d12858fd7df67776c0798c2e459be4fceabf392cf88ee921438eac5d3a1`, pinned in `qresearch.p3spec.NULL_RESULT_SHA256` together with `TAU`; test `test_null_threshold_frozen_before_real_search` |
| **Real run E018-07** | Started 09:14:10 UTC **from that commit** (its recorded `git_commit` is 3a1c915) |
| Evaluation guard | The real evaluation refuses any null file other than the pinned one |

## 12. Real configurations evaluated

- **Exactly 1,533**, the pinned list (hash `76b3dd38…`). All are present in E018-07; none was removed or added.
- **31 configurations never traded.** Their rules contradict themselves:
  - a new-high breakout (x = 0) combined with a pullback confirmation (RSI(5) ≤ 30 or close < SMA20);
  - a deep pullback (RSI(14) ≤ 40, or close ≥ 3–6% below SMA20) combined with RSI(14) ≥ 50/60.

  They stayed in the evaluation (frozen grammar) and failed the fold gate. This is a property of the pre-registered grammar, recorded, not changed.

## 13. Search runtime and memory

| Item | Value |
|---|---|
| Null runs | 6 × ≈ 33 min (1,873 – 2,318 s) |
| Real run | 8 min |
| **Total node time** | **≈ 3 h 45 min** |
| Peak memory | 4.04 – 4.36 GB (node 8 GB) |
| Output | ≈ 118 KB per null run; 2.17 MB for the real run (15 chunks), all returned intact |
| Extra cost | **$0** |

## 14. Distribution of real configuration outcomes

Training window 2010-03 → 2017-12, after all costs, vs SPY total return.

| Measure (1,533 configurations) | 5% | 25% | Median | 75% | 95% | Best |
|---|---|---|---|---|---|---|
| Fold-median score s (annualised log excess) | −10.7% | −5.5% | −2.8% | −0.7% | +1.5% | +5.5% |
| Excess CAGR vs SPY | −11.1% | −5.7% | −3.1% | −0.9% | +1.5% | +5.0% |
| Terminal-wealth ratio vs SPY | 0.45 | 0.67 | 0.81 | 0.94 | 1.11 | 1.40 |
| Cost a year (all ≤ 1.5% cap) | 1.00% | 1.05% | 1.08% | 1.12% | 1.18% | max 1.29% |

- **239 of 1,533** configurations ended the window with more wealth than SPY. The null worlds' median is 207 (range 75–601).
- **Gate failures:**

| Gate | Configurations failing |
|---|---|
| Cost | 0 |
| Drawdown (> SPY − 10 points; SPY's max drawdown was −18.7%) | 449 |
| Fold consistency (< 3 of 4 two-year folds beat SPY) | 1,432 (994 on this gate alone; 438 together with drawdown) |

- **Eligible:** **90**.
- **By primary family:**

| Family | Configurations | Eligible | Beat SPY | Best s | Median s |
|---|---|---|---|---|---|
| Trend | 297 | 8 | 35 | +5.5% | −2.7% |
| Momentum | 495 | 10 | 25 | +5.3% | −3.9% |
| Breakout | 405 | 55 | 145 | +3.8% | −0.7% |
| Pullback | 336 | 17 | 34 | +3.4% | −4.5% |

- **Single best raw configurations:**
  - best fold-median score: SMA50 > SMA200 with close within 10% of the 252-day high (+5.5% a year);
  - best terminal wealth: momentum top-20% of 126-day return with RSI(5) ≤ 30 (ratio 1.40).

  **Neither sits on a plateau. They are exactly the isolated "peaks" the method is designed not to select.**

## 15. Distribution of the best null-world outcomes (the fake-winner effect)

**What the same optimizer "finds" in 500 worlds where technical signals carry no stock-specific information:**

| In each no-edge world | 5% | 25% | Median | 75% | 95% | Max |
|---|---|---|---|---|---|---|
| Best configuration's excess CAGR vs SPY | +5.0% | +5.9% | **+6.8%** | +7.8% | +9.1% | +12.1% |
| Best terminal-wealth ratio vs SPY | 1.40 | 1.48 | **1.57** | 1.68 | 1.82 | 2.20 |
| Best fold-median score s | 5.1% | 5.9% | 6.7% | 7.6% | 8.9% | 11.5% |
| Best cluster-centre plateau score | −0.6% | 1.2% | 1.9% | 2.6% | 4.1% | 7.8% |
| Number of apparent "winning" clusters (eligible, connected, ≥ 3) | 2 | 5 | **8** | 12 | 20 | 37 |
| Eligible configurations | 50 | 78 | 100 | 132 | 191 | 318 |

- **In every one of the 500 fake worlds, the best configuration beat SPY over 2010–2017**, typically by 6.8% a year (wealth 1.57× SPY's).
- **98.8% of fake worlds contained at least one apparently robust cluster.**

Systematic search manufactures convincing historical winners from noise; the full-search null is what separates them from real edges.

## 16. Real result vs the null search

| Statistic | Real | Null percentile of the real value |
|---|---|---|
| **T (gate statistic)** | **0.0127** | **69th** (p = 0.31) |
| Best cluster-centre plateau score | 0.0194 | 54th |
| Best fold-median score | 5.5% | **13th** |
| Best terminal-wealth ratio | 1.40 | **5th** |
| Number of apparent clusters | 6 | 31st |
| Eligible configurations | 90 | 37th |
| Configurations beating SPY | 239 | 65th |
| Walk-forward total excess vs SPY | −6.8% | 66th |

**The real search is indistinguishable from the fake ones, and its best raw winners are weaker than in most fake worlds.**

## 17. Parameter plateaus found

| Threshold | Plateaus |
|---|---|
| **At τ** (the frozen rule) | **None** (0 survivors) |
| Without any threshold (reporting only; never promotable) | 6 connected clusters of eligible configurations, all below τ |

Clusters found without any threshold:

| Cluster | Size | Centre | Centre PS | Excess CAGR | Max drawdown | Fold scores (2010–11, 12–13, 14–15, 16–17) |
|---|---|---|---|---|---|---|
| 1 | 19 | Breakout: close ≥ 0.9 × 63-day high, ADX(14) ≥ 20, vol rank ≤ 50% | 0.0194 | +2.4% / yr | −13.2% | −0.5%, +3.5%, +2.1%, +3.2% |
| 2 | 4 | Breakout: close ≥ 0.9 × 63-day high, SMA50 > SMA200, vol rank ≤ 80% | 0.0118 | +1.7% / yr | −14.5% | +1.3%, +1.6%, +0.8%, +2.4% |
| 3 | 9 | Breakout: close ≥ 0.9 × 252-day high, RSI(14) ≥ 60, vol rank ≤ 50% | 0.0055 | +2.0% / yr | −12.9% | −1.0%, +0.6%, +0.5%, +6.6% |
| 4 | 3 | Breakout: close ≥ 0.95 × 63-day high, ret126 > 0, vol rank ≤ 50% | −0.0040 | +1.2% / yr | −14.4% | −3.1%, +4.0%, +1.7%, +1.2% |
| 5 | 4 | Pullback: RSI(2) ≤ 20, RSI(14) ≥ 60, vol rank ≤ 50% | −0.0058 | +0.1% / yr | −16.4% | +2.0%, −6.3%, +1.8%, +2.9% |
| 6 | 3 | Momentum: top 20% of 63-day return (skip 21), close ≥ 0.9 × 252-day high | −0.0172 | +0.8% / yr | −25.6% | −11.8%, +0.5%, +4.0%, +9.2% |

**For scale:** the null worlds' best cluster centres have a median PS of 0.0185 and a 95th percentile of 0.0405.

## 18. Promoted clusters

**None.** The promotion budget (≤ 3 clusters) was not used.

## 19. Details per promoted cluster

**Not applicable.** No cluster was promoted.

- The six below-threshold clusters are described in item 17 for transparency only: families, representative parameters, size, neighbourhood score, excess vs SPY, costs (all ≈ 1.05% a year) and drawdown.
- Every member's details are in `research/phase3/P3_search_configs.csv.gz`.

## 20. Walk-forward result

The frozen procedure re-run each year using only earlier years (no τ gate, so it always picks something):

| Test year | Pick (rank-1 centre from data through the year before) | Year-Y log excess vs SPY | vs EW |
|---|---|---|---|
| 2014 | Breakout at the 126-day high, MACD > signal | +3.1% | +5.7% |
| 2015 | Same configuration | −10.2% | −6.7% |
| 2016 | Breakout within 10% of the 126-day high, SMA50 > SMA200, vol rank ≤ 80% | +4.9% | +1.4% |
| 2017 | Breakout within 10% of the 63-day high, SMA50 > SMA200 | −4.6% | −2.2% |
| **Total** | 4 picks | **−6.8%** | **−1.8%** |

**Q2 FAILS:** both totals must be positive. A choice made from past data did not keep beating SPY. Fake worlds pass Q2 14.4% of the time; the real total sits at the null's 66th percentile.

## 21. Simplicity-rule decisions

- **At τ:** no cluster existed, so the rule was not applied.
- **Reporting only, without the threshold:**
  - the best centre is cluster 1 (PS 0.0194, SE* 0.0116), so the band is ≥ 0.0078;
  - cluster 2 (PS 0.0118, 3 parameters) is inside the band and simpler than cluster 1 (4 parameters);
  - the rule would therefore have preferred cluster 2.
- The walk-forward applies the same rule each year; its picks are shown in item 20.

## 22. Search-null gate

**FAIL** (T_real 0.0127 ≤ τ 0.0284; p = 0.31).

## 23. Rejected configurations and clusters, and why

| Reason | Count |
|---|---|
| Failed fold consistency (fewer than 3 of 4 two-year folds beat SPY) | 1,432 (including the 31 that never traded) |
| Failed the drawdown safeguard (> 10 points worse than SPY's −18.7%) | 449 |
| Failed cost | 0 |
| **Eligible** | **90** |
| Eligible with a plateau score above τ | **0** |
| Clusters at τ | 0 |
| Below-τ clusters (item 17) | 6, all rejected by the frozen Q1 rule |

- The full history (every configuration's id, key, fold scores, s, PS, gates, cost, turnover, drawdown and cluster) is recorded in `research/phase3/P3_search_configs.csv.gz` (SHA-256 `bb3e13bd…`).
- Every null world is recorded in `P3_null_worlds.csv`.
- The decisions are in `P3_search_result.json` (SHA-256 `2bdd0e70…`).

## 24. Eligible for LEAN finalist verification?

**No.** Q1 failed and Q2 failed; the frozen promotion path has no finalist.

## 25. Should S019 be built?

**No.** S019 is built only for finalists that pass Q1 and Q2 (spec §15).

## 26. A candidate for the 2018–2021 internal OOS?

**No.** No candidate exists. 2018–2021 stays unused by Phase 3.

## 27. Next action requiring owner approval

**Owner decision: close Phase 3 Stage 1 / H018 as "No Production Candidate Found".**

- Under the frozen spec (§14, §19), a Q1 failure stops the phase at the search. **One search round only**: no second round, no new grammar, no other holding periods, no threshold change.
- **Any further technical research would be a new phase, with a new owner decision and a new design.**

**My recommendation:** accept the result.
- The evidence is clear, not borderline: the real search sits in the middle of the null distribution (p = 0.31), and its walk-forward lost to SPY.
- This matches the pre-declared power analysis (P3-CP1 §26): realistic technical edges in this universe are too small to detect.

## 28. Final verdict

**NO ROBUST TECHNICAL EDGE FOUND.**

**Secondary diagnostics** (reported only):
- **PBO** of the configuration set: 0.61 (70 CSCV splits). In 61% of the splits, the configuration that was best in-sample ranked below the out-of-sample median.
- **Effective number of independent configurations:** ≈ 136 of 1,533 (Li–Ji).
- **The block null** gives a higher threshold (0.0348), which the real T also fails.

**Research totals to date:**

| Item | Count |
|---|---|
| Hypotheses written | 18 (H001–H018); 16 with runs |
| Strategies run | 17 |
| `experiments/INDEX.csv` rows | 456 (292 original backtests, 135 of them research) |
| Phase 3 | 1 hypothesis (H018: the search procedure), 1 real search of 1,533 configurations, 600 null worlds, 7 runs |

**STOP.**
- No S019, no 2018–2021, no Holdout, no new search round, no threshold change, no tuning, no purchase.
- The result is preserved exactly as produced.
