# P3-CP4 — Phase 3 Closure: No Production Candidate Found (STOP)

- **Date:** 2026-10-04.
- **Owner decision:** "Phase 3 — Close H018 / Stage 1 and Stop Before Any New Research Direction" (2026-10-04, D139; summary `docs/owner/2026-10-04_close_H018_phase3_stage1.md`).
- **This checkpoint is documentation only:**
  - no backtest, search, diagnostic or data access was run for it;
  - nothing was purchased;
  - no hypothesis or phase was created.

---

## 1. Formal closure of H018 / Stage 1

**H018 (Systematic Multi-Indicator Technical Strategy Search) — Phase 3 Stage 1 — is CLOSED: NO PRODUCTION CANDIDATE FOUND** (owner, 2026-10-04).

- **Preserved exactly as run, with nothing removed** (all failed configurations, zero-trade configurations, null worlds and runs):

| Item | Location |
|---|---|
| Spec | `research/phase3/P3_spec.md` |
| Null calibration | `P3_null_result.json`, `P3_null_worlds.csv` |
| Real search | `P3_search_result.json`, `P3_search_configs.csv.gz` (all 1,533 configurations) |
| Runs | E018-01..07 |
| Engine verification | E984-01..09 |

- **The frozen rules allowed one search round.** It is complete; there is no second round.

## 2. The exact architecture that was tested

| Element | Frozen value |
|---|---|
| Universe | US common stocks, point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, data infrastructure v1 (SEC correction layer) |
| Search window | 2010-03-01 → 2017-12-31 (history-only warm-up from 2009-07-01); four two-year folds |
| Grammar | 1 primary setup (trend, momentum, breakout or pullback) + ≤ 1 confirmation from a **different** information family + ≤ 1 volatility filter; ranking by the primary's own strength |
| Search space | **1,533 configurations** (trend 297, momentum 495, breakout 405, pullback 336), coarse literature grids |
| Portfolio | $100,000; 10 slots; **63-session hold**; next-open fills; $7 per buy and per sell; 10 bps slippage per side; settled cash, 2% buffer, 15% gap reserve, $4,000 minimum; no leverage |
| Score | Gates (cost ≤ 1.5% a year; drawdown ≥ SPY − 10 points; ≥ 3 of 4 positive folds), then the median fold log excess over SPY |
| Selection | **Plateau:** the 25th percentile over the one-step neighbourhood. Connected clusters of ≥ 3; an interior centre; the one-standard-error lexicographic simplicity rule; ≤ 3 clusters → ≤ 2 finalists → 1 candidate |
| Gates | Q1 search-null; Q2 walk-forward 2014–2017; (Q3 LEAN verification and Q4 internal OOS never reached) |
| Removed before the search | Stage 2 (exits and regime overlay) and the 126-session / 20-position architecture |

## 3. Null-world methodology

**Primary null: within-date permutation**, 500 worlds (seeds 1–500).
- Every session, each stock's technical **signal row** was mapped to a randomly chosen eligible **traded stock**.
- **Preserved:** real returns, regimes, volatility, correlation, universe changes, corporate actions, costs, signal frequencies and portfolio mechanics.
- **Broken:** only the link between a stock's own signal and its own future return.
- **The entire optimizer ran in every fake world** (gates, plateau, clusters, the statistic T, simplicity, walk-forward).
- **Secondary diagnostic:** a 63-session block permutation, 100 worlds.

## 4. Null threshold and proof it was frozen first

| Item | Value |
|---|---|
| **τ** | **0.0284** (exactly 0.028423616730466103): the 25th largest of 500 null values (≡ permutation p ≤ 0.05) |
| Frozen in commit | **`3a1c9151c3e11c94534e2546c3c1c68386b8416a`** (D137), before the real run |
| Null result file SHA-256 | `46c92d12858fd7df67776c0798c2e459be4fceabf392cf88ee921438eac5d3a1`, pinned in `qresearch.p3spec` with τ and checked by a test |
| Real run E018-07 | Started from that commit (its recorded `git_commit` is 3a1c915) |
| Search-stage false-pass rate of the null | 8 / 500 = 1.6%, 95% CI 0.69–3.13% |

## 5. Real search score

**T = 0.0127**: the plateau level of the best connected cluster, about 1.3% a year of log excess over SPY.

## 6. Empirical p-value

**p = 0.31.** The real result sits at the **69th percentile** of the 500 no-edge worlds. **Q1 FAIL.**

## 7. Walk-forward result

The procedure re-ran each year using only earlier years. Its picks (all breakout variants) returned **−6.8% vs SPY** and −1.8% vs the equal-weight universe over 2014–2017 (summed yearly log excess). **Q2 FAIL.**

## 8. Configurations searched

- **Exactly 1,533**, the pinned list. None was added or removed.
- **31 never traded:** they contain self-contradictory combinations, e.g. a new 63-day high together with RSI(5) ≤ 30. They were kept and failed the fold gate.

## 9. Configurations satisfying the basic filters

**90 of 1,533** passed all three gates.

| Gate | Failures |
|---|---|
| Cost | 0 |
| Drawdown | 449 |
| Fold consistency | 1,432 |

## 10. Robust clusters passing the threshold

**Zero.**
- No eligible configuration had a plateau score above τ.
- Six smaller clusters exist below τ; they are reported in P3-CP3 for transparency only.

## 11. Why no candidate reached S019

- S019 (the full-LEAN finalist strategy) was to be built only for ≤ 2 finalists from clusters that pass **both** the search-null gate (Q1) and the procedure walk-forward (Q2).
- **Both gates failed and no cluster existed at the threshold**, so the promotion path was empty. S019 was never built.

## 12. 2018–2021

**Unused** by Phase 3. No candidate qualified for the one-shot internal OOS. The period remains available, as before, for a single future frozen candidate only, under a new owner decision.

## 13. Holdout

**Locked and untouched:** 2022-01-01 → 2026-08-31. `HOLDOUT_UNLOCK.md` is unchanged; it has never been opened in any phase.

## 14. Data purchase

**None.** Phase 3 used only the existing QuantConnect subscription ($24/month) and free SEC data already in the data infrastructure v1.

## 15. Main methodological lesson: fake winners

**The null experiment shows how dangerous naive optimizer-based technical research is.** In 500 worlds where technical signals carried **no** information about a stock's own future return, the same optimizer:

| Finding | Result |
|---|---|
| Best configuration beat SPY over 2010–2017 | In **every one** of the 500 worlds |
| Best configuration's excess CAGR over SPY | **Median ≈ +6.8% a year** (5–95%: +5.0% to +9.1%; maximum +12.1%) |
| Best terminal-wealth ratio vs SPY | Median 1.57 (maximum 2.20) |
| Apparently robust "winning" clusters | A median of **8 per world** (up to 37) |
| Worlds with at least one such cluster | 98.8% |

**The real search's best raw winners were weaker than most fake worlds' winners:**
- its best configuration ended at 1.40× SPY's wealth, the 5th percentile of the fake worlds;
- it was nevertheless "a 5%-a-year SPY-beater" on paper.

**Permanent conclusion:**

> **Historical outperformance of the single best technical configuration — even one that beats SPY by several percent a year over eight years — is not sufficient evidence of a real edge.** Only a comparison with what the same search finds in no-edge worlds can separate an edge from the search's own selection effect.

## 16. Exact limitations of the conclusion

The result is **conditional on the architecture tested**:
- **Instruments and universe:** long-only US common stocks of ≥ $2B, as stock **selection** (always seeking 10 positions).
- **Horizon:** one holding horizon (63 sessions) and one portfolio shape (10 equal slots, $100K, fixed costs).
- **Space:** a constrained grammar of 1 + ≤ 1 + ≤ 1 conditions on coarse, literature-based grids; ranking by the primary's own strength only.
- **Data period:** one training period (2010-03 → 2017-12), largely a rising market; four two-year folds.
- **Power:**
  - The null threshold sits at about 2.8% a year of plateau excess.
  - The pre-declared power analysis (P3-CP1 §26) showed that only selection edges of roughly 6–8% a year above a random book had a realistic chance of passing.
  - **Smaller real edges cannot be excluded**; they are undetectable with this design and history.
- **The null and the selection procedure are themselves choices:**
  - another null (e.g. the block null, whose threshold was 0.0348) or another plateau rule would give different numbers;
  - both were frozen before any result, and the block null gives the same verdict.

## 17. This does not prove that all technical analysis fails

**This closure is not a general proof that technical analysis is useless.** It establishes only:

> Under the frozen Phase 3 architecture — 1,533 configurations, the constrained multi-indicator grammar, a 63-session holding period, 10 positions, the approved cost model, plateau selection, null calibration and the walk-forward procedure — **no robust technical stock-selection edge was found** in the ≥ $2B US universe over 2010–2017.

**It says nothing about** other horizons, other instruments, market-level timing, other ranking architectures, other cost and account models, or edges smaller than this design can detect.

## 18. Directions that remain conceptually open (NOT authorised)

**Context only.** Listed, not researched, designed, ranked or recommended. Each would need a separate, owner-approved design step and a new phase:
- market regime / market-timing approaches;
- ETF or index rotation;
- long / flat (exposure on or off) approaches;
- catalyst + technical confirmation;
- alternative cross-sectional ranking architectures;
- different holding horizons;
- fundamentally different account models (capital, position counts, cost structures).

**Explicitly not authorised as rescue attempts of H018:** other MA / RSI / MACD ranges, added indicators, the 126-day or shorter holds, 20 positions, stops or exits, or another search round on the same architecture.

## 19. Programme status (Phases 1–3; prior results unchanged)

### Phase 1: hypothesis-driven cycles C01–C03 (2026-09-27 → 2026-09-30)

| Item | Result |
|---|---|
| Hypotheses | **H001–H013**: price / volume / technical families and low volatility |
| Families tested | RSI oversold reversal, price momentum, 52-week-high proximity, momentum pullback, **low volatility (H005)**, breakout, volatility squeeze, residual relative strength, volume shock, gap and hold, seasonality, lottery-stock avoidance |
| Withdrawn untested | H012 (volatility-managed exposure; not evaluable) |
| Selection candidates | 40, none survived |
| **H005** (low volatility) | Passed the in-sample screen; v1.2 **failed Validation** (E005-28) |
| **H007 v1.1** | Passed the screen; **failed robustness** |
| Cycle outcomes | C01, C02, C03 each closed: **No Production Candidate Found** |
| Review | `docs/checkpoints/CP3j_programme_review_C01_C03.md` |

### Phase 2: hypothesis budget of 3 (2026-09-30 → 2026-10-04)

| Hypothesis | Outcome |
|---|---|
| **H014** (trend + pullback + confirmed recovery) | **Rejected**: profitable, but not benchmark- or control-beating (D101) |
| H015 (diversified low-turnover trend) | Not adopted before implementation; no slot used (D104) |
| **H016** (gross profitability GP/A, point-in-time fundamentals) | **Rejected**: Sharpe 0.69 vs SPY 0.92 (D119) |
| **H017** (earnings-event continuation, SEC 8-K timestamps) | **Rejected** (Case A, D128) |

- **H017 in more detail:** it was economically interesting. CAGR was 17.46% vs SPY 14.88% (wealth 1.30×), it beat the equal-weight universe and all five random-event controls, and it passed the drawdown, Sharpe and cost safeguards. It **failed** the evidence requirement W2 (g/SE 0.71 vs 2.15) and the persistence requirement R3 (74% of its excess came from 2014–15).
- **Phase 2 CLOSED: No Production Candidate Found** (D129).
- Data infrastructure v1, Amendment 3 and Event Data v1 remain frozen records.

### Phase 3: Systematic Multi-Indicator Technical Strategy Search (2026-10-04)

| Hypothesis | Outcome |
|---|---|
| **H018** (the search procedure) | Full optimizer tested; null search calibrated (500 worlds); **no robust technical edge found under the frozen architecture**; **CLOSED: No Production Candidate Found** (D139) |

### Programme totals (from `experiments/INDEX.csv`)

| Item | Count |
|---|---|
| Hypotheses written | **18** (H001–H018); 16 with backtests (H012 withdrawn and H015 not adopted, both before any run) |
| Research strategies run | 17 |
| Registry rows | **456**: 292 original backtests (135 research, the rest infrastructure, verification, benchmark, sizing, stress and demo), plus technical repeats, recoveries and annotations. Every failed, superseded and bugged run is preserved |
| Phase 3 | 1 real search of 1,533 configurations, 600 null worlds, 9 engine-verification runs |

**Locked assets:**
- **Holdout 2022-01-01 → 2026-08-31:** never opened in any phase.
- **2018–2021:** used once in Phase 1 (H005 Validation) and as part of Phase 2 development (2010–2021); unused by Phase 3.
- **No data purchased** in any phase. Running cost: $24/month (QuantConnect).

**Overall status: no production candidate has been found in any phase.**

## 20. STOP

**Phase 3 is closed.** I am waiting for the owner's explicit instruction on the next research direction.

**Not done, and not to be done without that instruction:**
- no strategy search;
- no 2018–2021 or Holdout access;
- no new phase or hypothesis (no H019, no Phase 4);
- no rescue or tuning of the technical search;
- no proposal based on the observed winners;
- no data purchase.
