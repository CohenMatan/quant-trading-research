# P3-CP2 — Technical Search Engine Implementation, Null Calibration Design and Fidelity Readiness (STOP)

- **Date:** 2026-10-04.
- **Owner authorisation:** "Phase 3 — Approve Architecture Direction, Authorise Implementation/Fidelity Only, and Freeze the Search Before Any Strategy Sweep" (2026-10-04; summary `docs/owner/2026-10-04_phase3_implementation_fidelity_only.md`).
- **Done:**
  - implemented the Phase 3 engine inside QuantConnect / LEAN;
  - verified it against completed control books with tolerances declared before any run;
  - measured runtime, memory and output on dummy configurations;
  - designed and calibrated the null machinery on synthetic data;
  - froze and hash-pinned the full search specification.
- **Not done:**
  - no real configuration was evaluated on market returns;
  - no technical-indicator performance, ranking or heatmap exists;
  - no null world was run;
  - no 2018–2021 or Holdout data was touched;
  - nothing was bought.

## Verdict

**READY FOR PHASE 3 SEARCH**

- **Engine fidelity:** the shadow-book engine reproduces LEAN's own execution of six completed control books **exactly**: zero daily-return difference, identical terminal values, every buy, sell, quantity, price, commission and forced exit. This holds on the final engine code (E984-09). The tolerances were committed before the first run.
- **Two defects found and fixed by the canaries themselves, outcome-blind:**
  - forced-exit fills were not reported (E984-01 → E984-04);
  - the features depended slightly on which other worlds shared a run (E984-06 → E984-07 / 08).
- **Capacity:** 100 worlds × 1,533 configurations per run (28–36 min, 4.4 GB, 2.26 MB output, all within QuantConnect's limits).
- **Determinism:** identical seeds give identical books in every run, and the real signals are identical whatever the batch.
- **Spec:** the whole search is frozen and hash-pinned: grammar (1,533), 63 / 10, score, plateau, statistic T, simplicity, walk-forward, the primary null (within-date permutation, R = 500, τ = the 25th largest), promotion ≤ 3 → ≤ 2 → 1 → 1, Q1–Q4 and the Holdout.
- **Run configs:** E018-01..07 are written and refuse to run without the owner's approval.
- **Tests:** 621 pass.

**No real configuration, no null world and no technical return has been computed.**

---

## 1. Phase 2 closed

- **Phase 2 is CLOSED: No Production Candidate Found** (owner, 2026-10-04; D129).
- **Slots:**
  - H014, H016 and H017 were rejected;
  - H015 was not adopted.
- **Records:** Amendment 3, Event Data v1 and data infrastructure v1 remain frozen records.
- **H017's results were not used** for any Phase 3 design choice.

## 2. Holdout locked

- **Holdout:** 2022-01-01 → 2026-08-31, never opened. `HOLDOUT_UNLOCK.md` is unchanged.
- **Every Phase 3 engine run is limited to 2017-12-31 or earlier, enforced three times:**
  - `experiment.validate` refuses X984 / S018 configs ending after 2017-12-31;
  - the algorithm raises if its end is later;
  - the harness Holdout lock still applies.
- **The fidelity replay** only compares decisions and fills up to 2017-12-31.

## 3. No technical search performed

- **No real configuration has been evaluated on real returns.** The six canaries (E984-02, -03, -05, -06, -07, -08) replaced every configuration mask and strength with **seeded random dummies**: the real features were computed for timing only and discarded, keeping only a SHA-256 digest and a count of the real masks. They therefore published nothing but timings, counts of random-book trades, digests and dummy-format output.
- **The fidelity runs** (E984-01, E984-04, E984-09) replayed the entry decisions of already-completed **control** books (random-event controls and the canary), not technical rules.
- **Null worlds:** none run. The null calibration used **synthetic** data only.
- **Config gate:** the search and null configs (E018-01..07) carry `owner_approval_required`; the runner refuses them without `--owner-approved <decision id>`.

## 4. Indicator families

Frozen in `research/phase3/P3_spec.md` §3, with exact formulas:

| Family | Indicators | Roles |
|---|---|---|
| Trend | close vs SMA(L); SMA(S) vs SMA(L); 21-session SMA slope; MACD > 0; ADX(14) | primary or confirmation |
| Momentum (incl. relative strength) | cross-sectional rank of ret(K, skip 21); ret(K); ret(K) − SPY; RSI(14) high; MACD > signal | primary or confirmation |
| Breakout | close within x of the N-session high | primary or confirmation |
| Pullback | RSI(n) low; close below SMA20 by y; Bollinger %b low | primary or confirmation |
| Participation | relative volume 20/120 | confirmation only |
| Volatility | 63-session realised-volatility cross-sectional rank | risk filter only |

**Not in the space:**
- regime overlays, exits / stops / targets, holding variants (Stage 2 removed);
- short-horizon oscillator trading, gap / intraday rules, pattern recognition, news, fundamentals.

**The feature-only redundancy merge (P3-CP1 §5 rule 2) is not applied.** The owner approved the grammar and its count; merging families would have changed the space after approval. Correlation is absorbed by the full-search null.

## 5. Grids

Coarse, 2–4 values per axis (spec §4):

| Component | Grid |
|---|---|
| T1 close > SMA(L) | L ∈ {50, 100, 150, 200} |
| T2 SMA(S) > SMA(L) | (S, L) ∈ {(20, 100), (50, 150), (50, 200)} |
| T3 SMA slope > 0 | L ∈ {100, 200} |
| M1 top q of ret(K, skip 21) | K ∈ {63, 126, 252} × q ∈ {10, 20, 30%} |
| M2 ret(K) > 0 | K ∈ {63, 126, 252} |
| M3 ret(K) − SPY > 0 | K ∈ {63, 126, 252} |
| B1 close ≥ (1 − x) max(N) | N ∈ {63, 126, 252} × x ∈ {0, 5, 10%} |
| R1 RSI(n) ≤ θ | (n, θ) ∈ {(2, 10), (2, 20), (5, 30), (14, 40)} |
| R2 close ≤ SMA20 (1 − y) | y ∈ {3, 6%} |
| R3 %b ≤ z | z ∈ {0, 0.2} |
| Confirmations | close > SMA200; SMA50 > SMA200; ADX ≥ {20, 25}; MACD > 0; ret126 > 0; ret(252, skip 21) > 0; RSI14 ≥ {50, 60}; MACD > signal; close ≥ 0.9 max(252); RSI5 ≤ 30; close < SMA20; rel. volume ≥ {1.0, 1.25} |
| Risk filter | none → vol rank ≤ 0.80 → ≤ 0.50 |

## 6. Grammar

**Rule:** 1 primary setup AND 0/1 confirmation from a **different** information family AND 0/1 volatility filter.
- **Ranking:** the primary's own strength (highest first), ties by security id.
- **Generator:** `qr_p3_grammar.enumerate_configs()`.
- **Ids:** "C" + SHA-256(canonical key)[:10]; all 1,533 are unique.

## 7. Exact count

**1,533 configurations:**

| Primary family | Configurations |
|---|---|
| Trend | 297 |
| Momentum | 495 |
| Breakout | 405 |
| Pullback | 336 |

- **Configuration-list hash:** SHA-256 `76b3dd3866bc1d0152426d68d1d17d88fce2a13c8f1c98189fb5817b6cba7016`, pinned in `qresearch.p3spec.CONFIG_LIST_SHA256` and tested.
- **Stage 2 (≤ 24) is removed.** The total budget is exactly 1,533.

## 8. 63 / 10 architecture

**Frozen:**
- 63-session hold (exit order at 62 sessions held, fill at the next open);
- 10 slots, $100K;
- $7 per buy and per sell, 10 bps per side;
- no leverage, long-only;
- the verified harness sizing (D051 settled cash, 2% buffer, 15% gap reserve, $4,000 minimum, 10% cap);
- no top-ups.

**H is not optimised.** It comes from the cost-feasibility rule (P3-CP1 §22).

## 9. 126 / 20 rule

**Removed from Phase 3 entirely**, together with all of Stage 2 (exits, stops, the regime overlay):
- they add degrees of freedom after the main search;
- they need engine code that the fidelity tests do not cover;
- they are the rescue paths the owner wants closed.

**No trigger exists.** Any later use is a new phase and an owner decision.

## 10. Score

Hierarchical and gate-based, with no weights (spec §7):
1. **Gates:**
   - realised cost ≤ 1.5% a year;
   - max drawdown ≥ SPY − 10 points;
   - positive excess in ≥ ceil(0.75 × folds) two-year folds.
2. **Score** = the median over folds of the annualised log excess growth vs SPY total return, after all costs.

Log excess growth is exactly the yearly change of the terminal-wealth ratio vs SPY, which is the objective.

## 11. Plateau

Spec §8:

| Element | Definition |
|---|---|
| **Neighbour** | One grid step on one axis (primary, confirmation or risk); symmetric |
| **Neighbourhood sizes** | 2–7 neighbours: 2 (236 configurations), 3 (500), 4 (463), 5 (248), 6 (76), 7 (10); 2,795 edges |
| **Minimum neighbours** | 2 (structural) |
| **Boundary** | Grid ends simply have fewer neighbours (no padding) |
| **PS** | The 25th percentile of s over c and its neighbours |
| **Survivors** | Eligible and PS > τ |
| **Clusters** | Connected components of survivors, of size ≥ 3 |
| **Cluster score** | The centre's PS |
| **Centre** | The interior survivor with the highest PS (else the most in-cluster neighbours, then PS, then id); never the single best s |

**Search statistic T** = the plateau level of the best connected cluster of ≥ 3 (§9 of the spec). T > τ exactly when a promotable cluster exists, so the null statistic and the promotion rule are the same object (tested on the real graph).

## 12. Simplicity

Lexicographic one-standard-error rule:
1. Band = the clusters whose centre PS ≥ PS* − SE*, where SE* = 1.2533 × sd(folds) / √folds (the standard error of a median).
2. Choose the smallest (n_conditions, n_parameters, turnover, −PS, id).
3. Ranks 2 and 3 re-apply the rule to the remaining clusters.

Distribution of (n_cond, n_par):

| (n_cond, n_par) | Configurations |
|---|---|
| (1, 1) | 23 |
| (1, 2) | 18 |
| (2, 1) | 146 |
| (2, 2) | 280 |
| (2, 3) | 126 |
| (3, 2) | 292 |
| (3, 3) | 468 |
| (3, 4) | 180 |

## 13. Training / walk-forward / OOS architecture

| Segment | Use |
|---|---|
| 2009-07 → 2010-02 | History-only warm-up |
| **2010-03-01 → 2017-12-31** | The search: four two-year folds |
| **2014–2017** | Procedure walk-forward. Each year re-runs the whole procedure using only earlier years (no τ gate) and records the rank-1 centre's next-year excess vs SPY and EW. Q2 passes with ≥ 3 picks and positive summed excess vs both |
| **2018-01-01 → 2021-12-31** | Internal OOS: once, for exactly one frozen candidate, after a further owner approval |
| **2022-01-01 → 2026-08-31** | Holdout, locked |

**Interaction rule (spec §2):**
- The walk-forward re-uses the search's own results restricted to past years. It tests the **procedure**, is a pass/fail gate, and is never used to redesign anything.
- 2014–2017 results of individual configurations are never inspected to adjust any rule.

## 14. Promotion budget

| Step | Number | Meaning |
|---|---|---|
| Search | 1,533 configurations, one round | — |
| Q1 | pass / fail | T > τ |
| Ranked clusters | ≤ 3 | Rank 3 is reported only |
| Q2 | pass / fail | The walk-forward |
| LEAN finalists | ≤ 2 | The centres of ranks 1 and 2 |
| Internal-OOS candidate | exactly 1 | Rank 1, or rank 2 only if rank 1 fails Q3 for a technical, fidelity or R4 reason |
| Holdout candidate | exactly 1 | Written owner approval |

No human choice exists at any step.

## 15. Null method

**Primary: within-date permutation of signal rows onto traded stocks**, fresh each session and seeded by (seed, session).

- **The entire optimizer runs on every null world:** gates, score, plateau, clusters, T, ranking and walk-forward.
- **Broken:** the link between a stock's own technical history and its own future return.
- **Preserved:**
  - real returns, regimes, volatility clustering, autocorrelation, cross-sectional correlation and common shocks;
  - universe changes, delistings, splits, dividends and stale exits;
  - every configuration's daily signal counts, hence its timing, turnover, cash and costs;
  - the correlation between configurations;
  - portfolio rules.

**Evaluated and rejected** (spec §12.2):
- **Circular shifts:** they put signals on dates where the stock is not eligible, not listed or delisted, and break the alignment with regimes.
- **Signal-label permutation:** degenerate for a max statistic.
- **Return-label shuffles:** they need synthetic paths that break the accounting.
- **Bootstrap tests (White / SPA):** cannot see plateaus; SPA's size depends on serial dependence (item 19).

**Secondary diagnostic:** block permutation (63-session blocks).

## 16. Number of null repetitions

| Null | Worlds | Seeds | Runs |
|---|---|---|---|
| **Primary** | **R = 500** | 1–500 | 5 runs of 100 |
| Secondary (block) | 100 | 1001–1100 | 1 run |

**Precision** (`research/phase3/P3_null_precision.json`, exact binomial):

| R | 95% interval of the 95th percentile (quantile levels) | Typical CI for a true 1% false-pass rate | P(upper CI < 5%) at a true 1% |
|---|---|---|---|
| 39 | **cannot be bracketed** | [0, 9.0%] | 0 |
| 100 | 0.90 – 0.99 | [0.03%, 5.4%] | 37% |
| 200 | 0.915 – 0.98 | [0.12%, 3.6%] | 86% |
| **500** | **0.928 – 0.968** | **[0.33%, 2.3%]** | **> 99.99%** |
| 1000 | 0.937 – 0.964 | [0.48%, 1.8%] | ≈ 100% |

**R = 39 (P3-CP1) was too small and is replaced by 500.**

## 17. False-pass precision / CI

- **Reporting rule (spec §12.3):**
  - the number of null worlds;
  - the number passing the full search-stage pipeline (Q1 with τ from the other 499 worlds, **and** Q2);
  - the rate and its Clopper–Pearson 95% interval;
  - plus the Q1-only and Q2-only rates and the T distribution.
- **Synthetic demonstration** of exactly this machinery: the frozen pipeline, the real 1,533-configuration graph, 500 synthetic no-edge worlds with correlated configuration noise calibrated on control books.

| Measure | Result |
|---|---|
| Q1 passes (leave-one-out) | 25 / 500 = 5.0% (CI 3.3–7.3%), as designed |
| Q2 passes | 27% |
| **Full search-stage passes** | **17 / 500 = 3.4%, 95% CI [2.0%, 5.4%]** |
| Worlds without any cluster | 7 |

- **Q1 and Q2 are positively related in synthetic worlds:** Q2 passes 68% of the time given Q1. A world whose universe happens to beat SPY makes both easier.
- **The real null avoids this:** it keeps the one realised market path in every world. Only stock selection is randomised, so the market-path effect is held fixed.
- **Q3 and Q4 cannot run in null worlds.** The reported rate is therefore an upper bound for the full chain.

## 18. Null threshold

- **τ** = the 25th largest of the 500 null T values: m = floor(0.05 × 501).
- **Q1 holds if and only if** T_real > τ, which is equivalent to the permutation p-value (1 + #{null ≥ T_real}) / 501 ≤ 0.05. This is tested exactly in `tests/test_p3_spec.py` for R = 39 … 1000.
- **Null worlds with no cluster** count as T = −∞.
- **Order of computation:** τ is computed and committed (`P3_null_result.json`) **before** the real run is started.

## 19. Secondary diagnostics

Reported, never gating, not stacked:

| Diagnostic | Definition |
|---|---|
| Block-permutation null (100 worlds) | Side by side with the primary null |
| PBO | CSCV, 8 blocks, on the monthly excess of all 1,533 configurations |
| DSR | Of the rank-1 centre, with N = the Li–Ji effective number of configurations |
| Effective number of trials | Li–Ji estimate, reported |

**Hansen's SPA is dropped.** A size check on synthetic data (94 months, 200 correlated zero-edge models; `research/phase3/P3_spa_size_check.json`) gave:

| Serial dependence | Block | Rejections of a true null at a nominal 5% |
|---|---|---|
| iid | 6 | 5.5% |
| iid | 12 | 6.0% |
| AR(1) = 0.3 | 6 | 24.5% |

- Its validity therefore rests on serial-independence assumptions we cannot verify.
- It cannot see the plateau step.
- Adding it would stack methods.

## 20. Fast-engine design

**A non-trading LEAN algorithm (X984; S018 = its byte copy for the search)** simulates thousands of virtual books inside one backtest. QuantConnect data never leaves the platform; only derived statistics are published.

- **Universe and calendar:** the frozen data-v1 universe and harness calendar.
- **Price windows:** point-in-time adjusted 280-bar windows, loaded once from history and rescaled on splits and dividends.
- **Signals:** every base condition is computed once per close and composed into the 1,533 masks.
- **Book mechanics:** books are numpy arrays (books × slots) with exactly the harness mechanics:
  - next-open fills ± 10 bps, $7;
  - D051 sizing;
  - the fixed horizon;
  - splits (fraction to cash), dividends, delisting closes, stale exits;
  - delisting-warned stocks skipped.
- **Statistics:** per world, the yearly log excess vs SPY total return, costs, equity sums, notional and drawdowns (monthly for the real world).
- **End of run:** the frozen pipeline runs in LEAN for every world.

**Modules:**
- `qr_p3_grammar`, `qr_p3_features`, `qr_p3_engine`, `qr_p3_pipeline`;
- tests `test_p3_features` / `_engine` / `_pipeline` / `_spec` / `_eval`.

**The engine's sizing is tested equal to the harness's own `plan_orders`** on 300 random scenarios.

## 21. Tolerances defined before tests

- **File:** `research/phase3/P3_fidelity_tolerances.json`, committed in 0089caf **before** the first fidelity run (E984-01, commit f39118c).
- **Per-book tolerances:**

| Check | Tolerance |
|---|---|
| Buy match | ≥ 99% |
| Exact quantities | ≥ 98% |
| Sell match | ≥ 99% |
| Trade-count difference | ≤ 1% |
| Fill prices | within 1e-6 on ≥ 99% |
| Commission and slippage totals | within 1% |
| Daily-return RMSE | ≤ 0.0005 |
| Maximum daily difference | ≤ 0.005 |
| Terminal value | within 0.5% |
| Cash | within 1% of equity on ≥ 99% of days |
| Forced exits | equal count |

- **Stop rule:** a failure stops the engine. A genuine engine defect may be fixed and the **same** tolerances re-applied; tolerances never change after results; candidate strategies are never used to calibrate.

## 22. Fidelity results

**What is compared.**
- The engine replays the **entry decisions** of six completed control books through its own sizing, execution, corporate-action and exit code:
  - the canary E982-02;
  - the H017 random-event controls E017-03..07.
- **Window:** 2010-03-01 → 2017-12-29; the replay schedule has 1,871 entries.
- **Comparison:** with LEAN's own fills and equity for the same books (`research/phase3/P3_fidelity_check.py`).
- **Coverage of the mechanics exercised:**
  - 238 cash-scaled buys;
  - 1,389 dividend credits;
  - 14 split adjustments;
  - 16 delisting closes.

**E984-01 (first run): FAILED two checks.**

| Check | Result |
|---|---|
| Forced exits reported | 0 vs LEAN's 16 |
| E017-04 sell match | 0.9868 (< 0.99) |
| Equity and cash paths, every buy, quantity and price | Identical (RMSE 0, terminal difference 0) |

- **Cause: a reporting defect, not an accounting one.** Fills created by corporate actions (delisting closes) were processed before the host's fill-capture marker and so were never published. The engine itself had counted all 16 closes; the identical equity proves they were booked correctly.

**Fix and repeat:**
- **Fix:** the host now publishes fills made during corporate-action processing, dated with LEAN's slice date (LEAN stamps delisting liquidations on that date, e.g. LLTC on Saturday 2017-03-11). Commit 1eb83f2.
- **E984-04:** an outcome-blind technical repeat with the **same tolerances**: **ALL CHECKS PASS for all 6 books.**

| Book | Buys (LEAN = shadow) | Sells (LEAN = shadow) | Commission (LEAN = shadow) | Forced exits | Terminal (LEAN = shadow) | Daily-return RMSE | Max daily diff | Cash diff max |
|---|---|---|---|---|---|---|---|---|
| E982-02 | 311 | 302 | $4,291 | 3 = 3 | $241,389.55 | 0 | 0 | 0 |
| E017-03 | 312 | 302 | $4,298 | 3 = 3 | $257,693.59 | 0 | 0 | 0 |
| E017-04 | 313 | 303 | $4,312 | 4 = 4 | $285,478.73 | 0 | 0 | 0 |
| E017-05 | 311 | 301 | $4,284 | 2 = 2 | $240,383.94 | 0 | 0 | 0 |
| E017-06 | 311 | 301 | $4,284 | 1 = 1 | $242,904.61 | 0 | 0 | 0 |
| E017-07 | 313 | 303 | $4,312 | 3 = 3 | $166,066.94 | 0 | 0 | 0 |

- **Every match share is 1.000:** buy match, quantity, fill price and sell match. Commission and slippage-notional differences are 0, and no day is missing.
- **The shadow engine reproduces LEAN's normal execution exactly** (to the cent) on these books: daily returns, final value, trade counts, entries and exits, cash, commissions, slippage, delistings, splits, dividends and sizing.
- **E984-09 — fidelity on the FINAL engine code** (after the batch-independence fix of item 23; the fidelity path is unchanged): **all checks pass again for all 6 books**, with identical figures. S018 is a byte copy of this code.
- **Result files:**
  - `research/phase3/P3_fidelity_check.json` (E984-09);
  - `P3_fidelity_check_E984-04.json`;
  - `P3_fidelity_check_E984-01.json` (the failed first run, kept).

**Limits of this test** (covered elsewhere):
- It replays decisions, so it does not test signal computation. Signals are covered by the unit tests: indicators vs independent reference loops and the look-ahead truncation test.
- Stale (no-data) exits did not occur in these books; they are covered by `test_p3_engine`.
- Each finalist is re-verified in a full LEAN run (Q3).


## 23. Runtime / memory canary

**All canaries use DUMMY configurations:**
- every configuration's mask and ranking key is replaced each session by seeded random numbers (densities 2–50%);
- the real features and masks are computed (for timing) and discarded, except for a SHA-256 digest of the real masks;
- each run covers the full search window 2010-03-01 → 2017-12-29 (1,975 sessions, up to 1,331 eligible stocks, 2,282 stocks seen).

| Run | Worlds (× 1,533 books) | Algorithm time | Runner time | Peak memory | Published | Purpose |
|---|---|---|---|---|---|---|
| E984-02 | 5 | 696 s | 869 s | 4.11 GB | 0.7 KB | Runtime / memory |
| E984-03 | 100 (153,300 books) | 1,853 s | 1,916 s | 4.32 GB | 4 KB | Scaling |
| E984-05 | 100 + full search-mode output | 1,940 s | 2,171 s | 4.44 GB | **2.26 MB in 16 chunks** | Output format and size |
| E984-06 | 1 | 617 s | 631 s | 4.36 GB | — | Batch independence (**failed**, below) |
| E984-08 | 1 (after the fix) | 484 s | 651 s | 4.10 GB | — | Batch independence |
| E984-07 | 100 + output (after the fix) | 1,644 s | 1,707 s | 4.44 GB | **2.26 MB in 16 chunks** | Batch independence and output |

**Time split** (E984-03, 100 worlds):
- shared per run: features 79 s, masks 29 s, history 96 s, bars 35 s;
- per world: engine 508 s, selection 404 s, corporate actions 256 s, statistics 30 s, in-LEAN pipeline 50 s (0.5 s per world);
- **marginal cost ≈ 12–13 s per world**; fixed cost ≈ 10 min per run (harness universe and history).

**Determinism:**
- **The same seeded worlds give identical books in every run** (100 worlds compared across E984-02 / 03 / 05 / 06 / 08: entries, exits and forced exits identical), including across the two code revisions.
- **Batch independence of the real features:**
  - **E984-06 found a defect.** The digest of the real masks in a 1-world run differed from the 100-world run (575,014,605 vs 575,013,700 true cells, a 1.6 × 10⁻⁶ difference).
  - **Cause:** stocks were unsubscribed when no book held them, then reloaded from history (which fills forward missing days) on re-entry. How often that happened depended on the other worlds' holdings (8,371 vs 5,520 history loads).
  - **Fix** (commit 8d5c07f): in search and canary modes every stock stays subscribed from its first eligibility until delisted, so each window is loaded once (now without fill-forward) and then streamed. E984-08 loaded each of the 2,282 windows exactly once.
  - **Verified after the fix:** E984-07 (100 worlds) and E984-08 (1 world) have the **identical digest** of all real masks over all 1,975 sessions: 574,991,318 true cells each, SHA-256 `418aa1ef…`. E984-07's 100 dummy worlds are also identical to E984-05's.
- **Analysis:** `research/phase3/P3_canary_report.py/.json`.


## 24. QC limits

| Limit | Observed |
|---|---|
| **Output** | Results travel as summary statistics in 150,000-character chunks. E984-05 published 2.26 MB in 16 chunks, all returned intact. This covers the real run's 1,533 per-configuration lines (≈ 1,420 characters each) plus 100 world summaries |
| **Log budget** | The host keeps ≤ 400,000 result lines; E984-05 used 1,635 |
| **Memory** | 4.1–4.4 GB peak, almost all of it the harness universe (the fidelity run alone uses 4.08 GB). Each world adds ≈ 3 MB. The node has 8 GB |
| **Runtime** | 100 worlds ≈ 36 min; no QuantConnect time limit was met. One backtest at a time on our node (the runner enforces it) |
| **Project files** | Every engine file is ≤ 25,000 characters (the host 24,497), well below the 64,000-character limit |
| **Data** | Every run ends ≤ 2017-12-31; QuantConnect data never leaves the platform; no logs used (daily quota) |


## 25. One run vs batching

**Batched: 100 worlds per run.**
- 100 worlds is the scale fully verified (E984-03, E984-05, E984-07): runtime, memory and output.
- 500 worlds in one run would take ≈ 2 h 10 min and 4.5 GB. That probably fits, but has not been tested, and one failure would lose everything.
- **Deterministic batching:**
  - the worlds are fixed by seed (1–100, 101–200, …);
  - a world's books depend only on its seed and the shared features;
  - the features do not depend on the batch (item 23).
- **The real world runs alone** (E018-07), so its result is computed exactly as each null world's is.


## 26. Test suite

**621 tests pass** (`pytest`, 2026-10-04, after all changes). New for Phase 3:

| File | Covers |
|---|---|
| `test_p3_features` | Every indicator vs an independent reference loop; look-ahead truncation; the grammar count, ids, neighbour symmetry and one-step property; signal-table composition |
| `test_p3_engine` | Sizing = harness `plan_orders` (300 random trials); next-open timing and the exact 63-session horizon; ≤ 10 positions and no negative cash; splits, dividends, delisting and stale exits; candidate selection; the null destroys a planted signal while keeping entry counts; finalist trace |
| `test_p3_pipeline` | Folds, score and safeguards; an isolated peak loses to a plateau; the one-standard-error rule; walk-forward truncation |
| `test_p3_spec` | Spec and configuration-list hashes; frozen values; τ ⇔ p-value for R = 39 … 1000; leave-one-out false-pass accounting; T ⇔ cluster-at-τ on the real graph; S018 config gates; the frozen run plan; S018 = byte copy of the verified engine |
| `test_p3_eval` | The published lines round-trip into the pipeline and reproduce T, the walk-forward and the ranking; an incomplete null is refused |

## 27. Spec hash

- **File:** `research/phase3/P3_spec.md`.
- **SHA-256:** `d7fa11235e6bd8d7183f6bc78e1f0b78b847cd41fb94d1898efaae98ceb6ea81`.
- **Pinned in:** `qresearch.p3spec.SPEC_SHA256`.
- **Tests:** `tests/test_p3_spec.py`, which also pins the configuration-list hash and asserts the frozen values.
- **Hypothesis:** `research/hypotheses/H018.md` (the procedure).

## 28. Estimated search runtime

**Node time, from the canaries on the final code** (runner time: E984-07, 100 worlds = 1,707 s; E984-08, 1 world = 651 s; ≈ 11 s per extra world):

| Runs | Content | Estimated time |
|---|---|---|
| E018-01 … E018-05 | 5 × 100 primary null worlds | ≈ 5 × 28.5 min |
| E018-06 | 100 block-null worlds | ≈ 28.5 min |
| E018-07 | Real world + 2.2 MB output | ≈ 12 min |
| **Total** | | **≈ 3.0 hours** of node time, one run at a time (3.4 h by a fit over all six canaries) |

- **Range:** about ±30%, because real masks will be sparser or denser than the 2–50% dummy densities.
- **Local evaluation:** minutes (`P3_eval.py`).
- **Cost:** **$0 extra** (the existing $24/month node).


## 29. Exact runs after approval

**Configs written now, all gated by `owner_approval_required`** (`research/phase3/P3_make_search_configs.py`, validated by `experiment.validate` and tests):

| Run | Content |
|---|---|
| **E018-01 … E018-05** | Primary null, within-date permutation, seeds 1–100, 101–200, …, 401–500 (S018, kind infrastructure) |
| **E018-06** | Secondary block null, seeds 1001–1100, 63-session blocks (diagnostic) |
| — | `P3_eval.py null` → τ, the false-pass count and CI → **committed** (`P3_null_result.json`) |
| **E018-07** | The real world: all 1,533 configurations (S018, kind research, H018). Started only after τ is committed |
| — | `P3_eval.py real` → T_real, p, Q1, clusters, ranking, Q2, diagnostics → **STOP at P3-CP3** |

**Not authorised by this approval, and needing later owner decisions:**
- Q3: building S019, its canary, the finalist LEAN runs and the shadow traces;
- the internal OOS (once);
- the Holdout.

**Each needs its own approval.**

## 30. Verdict

**READY FOR PHASE 3 SEARCH**

**Why READY:**

| Owner requirement | Status |
|---|---|
| Engine built inside LEAN | Done |
| Fidelity within tolerances defined before testing | Passes exactly, on the final code (E984-09) |
| No discrepancy calibrated away | The two defects were reporting and data-plumbing issues, fixed with unchanged tolerances and no candidate strategy involved |
| Runtime, memory, output and limits measured on dummy configurations; deterministic batching | Established (100 worlds per run, verified batch-independent) |
| Null | Chosen before any result (within-date permutation), R = 500, with the false-pass rate and CI defined and demonstrated |
| Spec | Every element the owner listed is frozen and hash-pinned |
| Run plan | Fixed and gated |

**What remains outside this verdict** (by design; each needs its own approval later):
- **S019** (the LEAN finalist strategy) and the finalist traces for Q3. They are built only if Q1 and Q2 pass, configured by the finalist's frozen key alone; trace mode is already in the engine.
- **The internal OOS run set** (once) and **the Holdout**.

**Honest expectation (unchanged from P3-CP1):**
- Realistic technical edges in this universe are probably too small to pass a 500-world full-search null and the walk-forward.
- **"No Production Candidate Found" remains the most likely outcome**, and the design makes that an informative result.

**Owner decision requested:**
- Approve (or not) the first real Phase 3 search runs E018-01..07 (null worlds first; τ committed; then the real world), ending at the P3-CP3 search checkpoint.
- **Not requested now:** Q3 verification, the internal OOS, the Holdout.

**STOP.**
- No real Phase 3 search run until the owner explicitly approves.
- No 2018–2021 data, no Holdout, no purchase.
