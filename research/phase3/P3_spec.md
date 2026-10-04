# Phase 3 — Frozen Specification of the Systematic Technical Search (H018)

- **Status:** FROZEN on 2026-10-04 at P3-CP2, before any real search configuration was evaluated on market returns.
- **Hash pin:** `qresearch.p3spec.SPEC_SHA256`, checked by `tests/test_p3_spec.py`. The configuration list is pinned separately (`CONFIG_LIST_SHA256`).
- **Owner instructions implemented:** 2026-10-04, "Phase 3 — Approve Architecture Direction, Authorise Implementation/Fidelity Only, and Freeze the Search Before Any Strategy Sweep" (`docs/owner/2026-10-04_phase3_implementation_fidelity_only.md`). Architecture: P3-CP1.
- **Hypothesis:** `research/hypotheses/H018.md`. H018 is the **procedure**: "the frozen search below finds a technical rule whose stock selection beats its own full-search null, keeps working in a procedure walk-forward, and beats SPY once on untouched data."

**Nothing in this document may change after any search or null result is seen.**
- A genuine engine defect found by a canary or a fidelity check is a technical repeat: fix, re-run the whole affected stage, record it. It is never a reason to change a rule.
- Any other change is a new phase and an owner decision.

---

## 1. Objective

- **Goal:** starting with the same capital on the same date, finish with more wealth than SPY total-return buy-and-hold, after realistic costs, without leverage.
- **Accounts:** $100,000 primary; $200,000 sensitivity only (reported, never gated).
- **Risk metrics** are safeguards, not the objective.

## 2. Data, universe and partition

| Item | Frozen value |
|---|---|
| **Engine and data** | QuantConnect Cloud LEAN, build 18131 (pinned per experiment); data infrastructure v1 (`research/phase2/data_freeze_v1.json`), unchanged |
| **Universe** (each close) | Harness eligibility of data v1: US common stock, point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, the SEC correction layer (`universe.sec_corrections: true`). Financials are included (technical search; no fundamentals used) |
| **Signals** | Daily bars as known at the close, `SCALED_RAW` (split- and dividend-adjusted as of that date, rescaled on each later split or dividend) |
| **Fills** | Raw prices |
| **History-only warm-up** | from 2009-07-01 (no decisions, orders or equity before the official start) |
| **SEARCH window** | 2010-03-01 → 2017-12-31 (the official start of every search and null run) |
| **Training folds** | Two-year calendar blocks: 2010–11 (from 2010-03-01), 2012–13, 2014–15, 2016–17 |
| **Procedure walk-forward** | Test years 2014, 2015, 2016, 2017, inside the search window (§11) |
| **Internal OOS** | 2018-01-01 → 2021-12-31, used **exactly once**, for exactly one frozen candidate (§16) |
| **Holdout** | 2022-01-01 → 2026-08-31, **locked** (CLAUDE.md, `HOLDOUT_UNLOCK.md`) |
| **Hard limits in code** | Every Phase 3 engine run (X984, S018) must end on or before 2017-12-31 (`experiment.validate` and the algorithm both refuse). The harness Holdout lock applies to all runs |

**The partition is the project's pre-existing 2010 scheme** (D034), not a performance-based choice.

**How the walk-forward interacts with the search:**
- The walk-forward re-uses the search's own shadow results, restricted to the years before each test year.
- It creates no configuration and tunes nothing.
- 2014–2017 are both training years of the final search **and** test years of the walk-forward. The walk-forward therefore tests the **procedure** ("does a choice made only from earlier years keep working in the next year?"); it is not an independent sample for the final choice.
- **Its result is a pass/fail gate (Q2) and is never used to redesign anything.** If it fails, the phase stops.
- The 2014–2017 results of individual configurations are never inspected to adjust the grammar, the grids, the score or any rule. The search window is evaluated once, by the frozen code, and only the outputs in §20 are read.

## 3. Indicator families and exact definitions

All quantities are computed each close from the last 280 adjusted bars per stock (`qr_p3_features.WINDOW`). **A condition is False whenever its look-back is incomplete.**

| Quantity | Definition |
|---|---|
| SMA(n) | mean of the last n closes |
| slope(L) | SMA(L) today / SMA(L) 21 sessions ago − 1 |
| ret(K) | close / close K sessions ago − 1 |
| ret(K, skip 21) | close 21 sessions ago / close K sessions ago − 1 |
| xret(K) | ret(K) − SPY's ret(K) (SPY price, same dates) |
| max(N) | maximum close of the last N sessions (including today) |
| RSI(n) | Wilder: smoothed mean gain / mean loss, seeded by the simple mean of the first n changes, recursion started 100 changes back; 100 − 100 / (1 + RS) (100 if no losses; 50 if neither) |
| MACD | EMA(12) − EMA(26) of closes; signal = EMA(9) of MACD; EMAs seeded by a simple mean, started 200 bars back |
| ADX(14) | Wilder's ADX from high, low, close, seeded as RSI, started 100 bars back |
| %b(20, 2) | (close − (SMA20 − 2 sd20)) / (4 sd20), population sd |
| vol63 | sample standard deviation (ddof 1) of the last 63 daily log returns |
| volrank | cross-sectional percentile rank of vol63 among today's eligible stocks, ascending (0 = least volatile, 1 = most) |
| rel. volume | mean volume of the last 20 sessions / mean volume of the last 120 sessions |

**Information families:**

| Family | Role |
|---|---|
| Trend | primary or confirmation |
| Momentum (incl. relative strength) | primary or confirmation |
| Breakout | primary or confirmation |
| Pullback | primary or confirmation |
| Participation | confirmation only |
| Volatility | risk filter only |

## 4. Grammar, grids and the exact count

```
Strategy  := Primary setup (exactly 1)
             AND Confirmation (0 or 1, from a DIFFERENT information family than the primary)
             AND Volatility risk filter (0 or 1)
Ranking   := the primary's own strength (highest first); ties by security id
```

**Primary setups** (10 types, 41 variants):

| Type | Family | Condition | Strength | Grid |
|---|---|---|---|---|
| T1 | trend | close > SMA(L) | close / SMA(L) − 1 | L ∈ {50, 100, 150, 200} |
| T2 | trend | SMA(S) > SMA(L) | SMA(S) / SMA(L) − 1 | (S, L) ∈ {(20, 100), (50, 150), (50, 200)} |
| T3 | trend | slope(L) > 0 | slope(L) | L ∈ {100, 200} |
| M1 | momentum | top q of ret(K, skip 21) among eligible stocks with a value (k = max(1, round(q·n)); rank ≤ k) | ret(K, skip 21) | K ∈ {63, 126, 252} × q ∈ {10%, 20%, 30%} |
| M2 | momentum | ret(K) > 0 | ret(K) | K ∈ {63, 126, 252} |
| M3 | momentum | xret(K) > 0 | xret(K) | K ∈ {63, 126, 252} |
| B1 | breakout | close ≥ (1 − x) · max(N) | close / max(N) − 1 | N ∈ {63, 126, 252} × x ∈ {0, 5%, 10%} |
| R1 | pullback | RSI(n) ≤ θ | −RSI(n) | (n, θ) ∈ {(2, 10), (2, 20), (5, 30), (14, 40)} |
| R2 | pullback | close ≤ SMA(20) · (1 − y) | −(close / SMA20 − 1) | y ∈ {3%, 6%} |
| R3 | pullback | %b(20, 2) ≤ z | −%b | z ∈ {0, 0.2} |

**Confirmations** (12 types, 15 variants):

| Type | Family | Condition | Grid |
|---|---|---|---|
| cT_sma200 | trend | close > SMA200 | — |
| cT_cross | trend | SMA50 > SMA200 | — |
| cT_adx | trend | ADX(14) ≥ a | a ∈ {20, 25} |
| cT_macd0 | trend | MACD > 0 (EMA12 > EMA26) | — |
| cM_r126 | momentum | ret(126) > 0 | — |
| cM_r252s | momentum | ret(252, skip 21) > 0 | — |
| cM_rsi | momentum | RSI(14) ≥ r | r ∈ {50, 60} |
| cM_macdsig | momentum | MACD > signal(9) | — |
| cB_hi252 | breakout | close ≥ 0.9 · max(252) | — |
| cR_rsi5 | pullback | RSI(5) ≤ 30 | — |
| cR_sma20 | pullback | close < SMA20 | — |
| cP_rv | participation | relative volume ≥ v | v ∈ {1.0, 1.25} |

**Risk filter:** an ordinal axis with 3 levels: none → volrank ≤ 0.80 → volrank ≤ 0.50.

**Exact count: 1,533 configurations.**

| Primary family | Primary variants | Confirmation options (none + other-family variants) | Risk levels | Configurations |
|---|---|---|---|---|
| Trend | 9 | 1 + 10 | 3 | 297 |
| Momentum | 15 | 1 + 10 | 3 | 495 |
| Breakout | 9 | 1 + 14 | 3 | 405 |
| Pullback | 8 | 1 + 13 | 3 | 336 |
| **Total** | **41** | | | **1,533** |

**Configuration identity:**
- Canonical key: `<primary type>:<axis indices>|<confirmation type>:<axis indices> or ->|R<risk level index>`.
- Id = "C" + the first 10 hex digits of SHA-256(key).
- The list (canonical order of `qr_p3_grammar.enumerate_configs()`) is pinned by `CONFIG_LIST_SHA256` = SHA-256 of the lines `id|key\n`.
- **No configuration may be added, removed or changed after the search begins.**

**Exclusions (not in the space, by design):**
- More than one primary, more than one confirmation, or more than one risk filter.
- A confirmation from the primary's own family.
- Short-horizon oscillator trading, gap or intraday rules, pattern recognition, news, fundamentals (P3-CP1 §4).
- Exits, stops, targets, market-regime overlays and holding-period variants (Stage 2 is removed, §6).
- The feature-only redundancy merge proposed in P3-CP1 §5 rule 2 is **not applied**. The owner approved the grammar and its exact count; merging families after approval would change the space. Correlation between configurations is handled by the full-search null (§12).

## 5. Simplicity attributes (used only by the one-standard-error rule)

- **n_cond** = 1 + (confirmation present) + (risk filter present) ∈ {1, 2, 3}.
- **n_par** = the number of grid axes of the active components:
  - the primary's axes;
  - plus the confirmation's axes;
  - plus 1 if the risk filter is on.

Distribution of (n_cond, n_par) over the 1,533 configurations:

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

## 6. Portfolio and execution (frozen; never optimised)

| Item | Value |
|---|---|
| Holding period H | **63 sessions** (exit order at the close where sessions held ≥ 62; fill at the next open) |
| Slots N | **10** |
| Capital | **$100,000** ($200,000 sensitivity only) |
| Commission | **$7 per executed buy and per executed sell** |
| Slippage | **10 bps per side** (buys at open × 1.001, sells at open × 0.999) |
| Leverage | **none**; long-only |
| Decisions | once per session at the close; market-on-open at the next session with a bar; never at the decision close |
| Entries | each close, the free slots are filled from the configuration's passing stocks in strength order; held and pending stocks are skipped; nothing is queued; stocks with a delisting warning are skipped and the slot stays free |
| Sizing | the verified harness `plan_orders` (D051): w = min(max(0.98/N, 1.01 × 4000 / pv), 0.10); quantity = int(w × pv / close); positions ≥ $4,000; open positions ≤ min(N, pv × 0.98 // 4000); settled cash only, 2% buffer, 15% gap reserve, proportional scaling when short |
| Top-ups and resizing | none |
| Splits | quantity / factor (whole shares; the fraction is paid in cash) |
| Dividends | cash |
| Delisting | position closed at the last close, $7, no slippage |
| Stale | a holding with no real bar for more than 10 sessions is closed at its last real close, $7 (D059) |

**Removed from Phase 3 entirely:**
- **Stage 2** (four exits × regime overlay, ≤ 24 configurations).
- **The 126-session / 20-position architecture.**

**Why both are removed rather than given a trigger:**
- They would add degrees of freedom after the main search.
- They would need engine code (trailing stops, reversal exits, overlays) that the fidelity tests have not covered.
- They are exactly the "rescue" paths the owner wants closed.
- **No trigger exists that could re-introduce them in Phase 3.** Any later use would be a new phase and an owner decision.

**H is not optimised.** 63 sessions and N = 10 come from the cost-feasibility rule (P3-CP1 §22: projected cost ≈ 1.34% a year at $100K, under the 1.5% cap), never from returns.

## 7. Stage-1 score (hierarchical, gate-based; no weights)

For configuration c, on data through year Y_last (2017 for the full search):

1. **Daily log excess:** d_t = ln(1 + r_c,t) − ln(1 + r_SPY,t), with SPY total return (dividends included).
2. **Fold score:** s_k = 252 × Σ_{t∈fold k} d_t / (sessions in fold k).
3. **Gates** (all required; failing any → not eligible):
   - **G-cost:** realised commissions + slippage ≤ **1.5%** a year of mean equity (R4);
   - **G-dd:** maximum drawdown through Y_last ≥ SPY's maximum drawdown − **10 points** (R1);
   - **G-folds:** positive fold scores in ≥ **ceil(0.75 × folds)** folds (3 of 4 in the full search; 2 of 2 in walk-forward years 2014 and 2015; 2 of 3 in 2016 and 2017).
4. **Score:** s(c) = the **median** of the fold scores.

**The score has no tunable weight.** Risk, cost and consistency are pass/fail; plateau and simplicity are separate rules (§8–10).

## 8. Plateau definition

| Element | Frozen definition |
|---|---|
| **Neighbour** | c′ is a neighbour of c iff they differ by exactly **one step on one axis**: one grid step of one primary axis (same primary type); or one grid step of one confirmation axis (same confirmation type); or one step of the risk axis (none ↔ 0.80 ↔ 0.50). Symmetric. Changing the type of a primary or confirmation, or adding or removing a confirmation, is not a step |
| **Neighbourhood sizes** | every configuration has 2–7 neighbours: 2 (236), 3 (500), 4 (463), 5 (248), 6 (76), 7 (10); 2,795 edges |
| **Minimum neighbours** | 2, structural (no configuration has fewer; none is excluded) |
| **Boundary** | grid ends have fewer neighbours; nothing is padded or extrapolated |
| **Plateau score** | PS(c) = the **25th percentile** (linear interpolation) of s over {c} ∪ N(c), using every neighbour whether eligible or not. An isolated peak scores low |
| **Survivors** | eligible configurations with PS(c) > τ (the null threshold, §12) |
| **Connectivity** | two survivors are connected if they are neighbours; clusters = connected components of the survivor graph |
| **Minimum cluster size** | **3** (smaller components are discarded) |
| **Cluster score** | the PS of the cluster's centre |
| **Centre** | the **interior** survivor (all its neighbours inside the cluster) with the highest PS; if none is interior, the survivor with the most in-cluster neighbours, then the highest PS, then the lowest id. **Never** the single best s(c) by construction |

Reported for every cluster:
- size;
- parameter ranges;
- the members' fold signs;
- s along each axis through the centre.

## 9. Search statistic and Q1

- **Search statistic** T = the largest level t such that the eligible configurations with PS > t contain a connected cluster of at least 3. Equivalently: add eligible configurations in decreasing PS order; T is the PS of the configuration whose addition first creates a connected component of 3. If none exists, T = −∞.
  - This is "the plateau level of the best cluster".
  - **T > τ ⇔ at least one promotable cluster exists at the threshold τ.** The null statistic and the promotion rule are therefore the same object.
  - Implemented in `qr_p3_pipeline.cluster_level`.
- **Q1:** T_real > τ, where τ is the null threshold of §12.
  - Equivalent to the family-wise permutation p = (1 + #{null T ≥ T_real}) / (R + 1) ≤ 0.05.
  - Reported with the p-value.

## 10. One-standard-error simplicity rule (lexicographic)

Among the clusters at τ:
1. Let the best cluster be the one with the highest centre PS, PS*.
2. **SE\*** = 1.2533 × sd(the best centre's fold scores) / √(folds). This is the standard error of a median.
3. **Band:** the clusters whose centre PS ≥ PS* − SE*.
4. **Rank 1** = the cluster in the band with the lexicographically smallest key (n_cond, n_par, turnover a year, −PS, id) of its centre.
5. **Ranks 2 and 3:** the same rule re-applied to the remaining clusters (a new PS* and SE* each time).
6. At most 3 clusters are ranked.

## 11. Procedure walk-forward (Q2)

For each test year Y ∈ {2014, 2015, 2016, 2017}:
1. **Re-run the complete frozen procedure** (§7, §8, §10), using only years 2010 … Y−1. The folds are the two-year blocks available then.
2. **No τ gate is applied**, because τ is calibrated only for the full window. Rank 1 is chosen among all clusters. If no cluster exists, there is no pick that year.
3. **Record** the rank-1 centre's year-Y log excess vs SPY, and vs the same-universe EW index (§12.4). The configuration's book is continuous: its year-Y state depends only on rules fixed before Y.

**Q2 passes iff all three hold:**
- picks in **≥ 3** of the 4 years;
- **and** the summed year-Y log excess vs SPY > 0;
- **and** the summed year-Y log excess vs EW > 0.

**Never redesign after the walk-forward.**

## 12. Null calibration (the primary multiple-testing control)

### 12.1 Primary null: within-date signal permutation

- **What changes:** on each session t of null world r, a seeded permutation π_r,t of the day's eligible stocks maps each **signal row** to a **traded stock** (`qr_p3_engine.null_permutation(seed_r, t)`, NumPy `default_rng([seed_r, t, 7919])`).
- **What stays the same:** every configuration computes its conditions, masks and strength order exactly as in the real search, but buys π_r,t(stock). Everything else is unchanged: the engine, the mechanics, the costs, the eligible universe, prices, corporate actions, delistings and SPY.
- **The entire optimizer is run on every null world:** gates, score, plateau, clusters, T, the one-standard-error ranking and the walk-forward. One summary per world is recorded (`qr_p3_pipeline.world_summary`).

**Randomised vs preserved:**

| Randomised (broken) | Preserved |
|---|---|
| The link between a stock's own technical history and its own future return, i.e. the stock-selection information the search claims to find, including any characteristic premium a configuration loads on (e.g. low volatility, momentum) | Real returns of real eligible stocks: market regimes, volatility clustering, autocorrelation, cross-sectional correlation and common shocks |
| | Universe changes, delistings, splits, dividends, stale exits |
| | Every configuration's daily number of passing stocks, hence its entry timing, turnover, cash level, costs and constraints |
| | The correlation between configurations (all share the same permuted rows each day), hence the effective number of trials |
| | The portfolio rules |

### 12.2 Null methods evaluated (chosen before any result)

| Method | Assessment | Role |
|---|---|---|
| **Within-date permutation** (signal rows → traded stocks, fresh each session) | Breaks exactly the signal → own-future-return link and preserves everything in §12.1. Exact for the daily decision structure; deterministic by seed | **PRIMARY** |
| **Block permutation** (the same mapping kept for 63-session blocks) | Also preserves the persistence of "which stock a signal points to" over a holding period. Fewer independent mappings, so a slightly noisier null | **Secondary diagnostic** (R = 100), never a gate |
| **Circular time shift** of each stock's signal series | Shifted signals fall on dates where the stock is not eligible, delisted or not yet listed. It breaks the alignment of signal frequency with market regimes. It does not respect universe changes | Rejected |
| **Signal-label permutation** (shuffle which configuration owns which result) | Leaves the maximum over configurations unchanged: no null distribution for a max statistic | Rejected (degenerate) |
| **Return-label permutation** (shuffle returns across stocks) | Equivalent in intent to the primary, but needs synthetic return paths that break corporate-action and cash accounting | Rejected (the primary achieves it exactly on real paths) |
| **Bootstrap of configuration returns** (White / Hansen) | Cannot reproduce the plateau and cluster steps of the optimizer. Hansen's SPA is correctly sized only when monthly excess returns are serially independent: on synthetic data with 94 months and 200 correlated zero-edge models, it rejects 5.5% (iid) but 24.5% under AR(1) = 0.3 at a nominal 5% (`research/phase3/P3_spa_size_check.json`). The permutation null needs no such assumption | Not used |

**No cherry-picking:**
- The primary null is fixed here.
- The secondary null is reported, never gated.
- If the two disagree, the primary decides and the disagreement is reported.

### 12.3 Repetitions, threshold and precision

| Item | Frozen value |
|---|---|
| **Primary null worlds** | **R = 500**, seeds 1 … 500 (`seed_r = r`) |
| **Secondary block-null worlds** | 100, seeds 1001 … 1100, block = 63 sessions |
| **Null threshold τ** | the m-th largest of the 500 null statistics T, m = floor(0.05 × 501) = **25** (the 25th largest; empirical quantile ≈ 0.952). Null worlds with no cluster have T = −∞ |
| **Q1** | T_real > τ ⇔ p = (1 + #{null T ≥ T_real}) / 501 ≤ 0.05 |
| **Precision of τ** | distribution-free 95% interval of the 95th percentile from R = 500 draws: order statistics 464–484, i.e. quantile levels 0.928–0.968 (R = 39 cannot bracket it at all; `P3_null_precision.json`) |
| **Search-stage false-pass rate** | Among the 500 null worlds, the number that pass the **full search-stage pipeline**: Q1 with τ estimated from the other 499 worlds (leave-one-out) **and** Q2. Reported as the count, the rate and the Clopper–Pearson 95% interval |
| **Also reported** | the Q1-only pass count (by construction ≈ 5%); the Q2 pass rate under the null; the distribution of T (5/50/95/99%); the number of null worlds without a cluster |
| **Precision at R = 500** | a true rate of 1% gives a typical interval of [0.33%, 2.32%]; a 5% rate gives [3.3%, 7.3%]; zero passes gives an upper bound of 0.74% |

Q3 (LEAN) and Q4 (internal OOS) cannot be run in null worlds: Q3 is a technical check, and Q4 needs data the search must not touch. **The reported false-pass rate is therefore an upper bound for the complete chain.**

### 12.4 Control series used inside the procedure

- **SPY:** total return from QuantConnect prices plus cash dividends, computed in the same run. The frozen E900-07 is the reference for reports.
- **EW index:** each session, the equal-weighted mean total return of the eligible stocks with two consecutive real closes. A daily-rebalanced, cost-free index used only for the walk-forward EW comparison (Q2).

## 13. Secondary diagnostics (reported, never gating; not stacked)

| Diagnostic | Use |
|---|---|
| **Block-permutation null** (§12.2) | T distribution and false-pass rate, side by side with the primary |
| **PBO** (CSCV) | On the 1,533 configurations' monthly log excess over SPY, 2010-03 → 2017-12. 8 blocks of about 12 months; `qresearch.stats.pbo_cscv` (no embargo: diagnostic only, and the 63-session holding overlap is noted in the report) |
| **DSR** | Of the rank-1 centre's training excess, with N = the effective number of configurations (eigenvalue / Li–Ji estimate from the monthly excess correlation matrix); `qresearch.stats` |
| **Effective number of trials** | Same eigenvalue estimate, reported |

**Hansen's SPA is not used:**
- its size depends on serial dependence we cannot verify: 5.5% (iid) vs 24.5% (AR(1) = 0.3) rejections of a true null at a nominal 5% (`research/phase3/P3_spa_size_check.py/.json`);
- it cannot see the plateau and cluster steps;
- the owner asked not to stack methods.

## 14. Promotion budget (exact meanings; no discretion)

| Stage | Number | Meaning |
|---|---|---|
| Stage-1 configurations | 1,533 | All evaluated once, in one real-world run (§19) |
| Null worlds | 500 primary + 100 secondary | Fixed seeds |
| **Q1** | pass / fail | T_real > τ. Fail → STOP: No Production Candidate Found |
| **Ranked clusters** | ≤ 3 | Clusters at τ ranked by §10. Rank 3 is reported only and never promoted |
| **Q2** | pass / fail | The walk-forward (§11). Fail → STOP |
| **LEAN-verified finalists** | ≤ 2 | The centres of ranks 1 and 2 (rank 2 only if it exists) |
| **Internal-OOS candidate** | exactly 1 | Rank 1's centre if it passes Q3. Rank 2's centre **only if** rank 1 fails Q3 for a technical, fidelity or R4 reason in LEAN. If neither passes Q3 → STOP |
| **Holdout candidate** | exactly 1 | The internal-OOS candidate, if Q4 passes, after written owner approval in `HOLDOUT_UNLOCK.md` |

**Hard rules:**
- **No discretionary finalist:** no human choice, no swap of centre within a cluster, no neighbour substitution.
- **One search round.** No second round after results; any redesign is a new phase and an owner decision.

## 15. LEAN verification requirements (Q3)

For each finalist (≤ 2), on 2010-03-01 → 2017-12-31 with $100K:

1. **A full LEAN harness strategy (S019: real LEAN orders, fills, fees and corporate actions).**
   - It implements the frozen configuration with the same feature and grammar modules (`qr_p3_features`, `qr_p3_grammar`) and the harness order planner.
   - It is built after Q2 and **before** Q3 is read.
   - It is configured by the finalist's canonical key only: no choice remains.
   - It is preceded by a byte-copy canary (X-number) on the same window.
2. **A shadow trace run of the same configuration** (S018 search mode, real world, `trace` = the finalist ids): daily equity and cash, and every fill.
3. **Comparison** with `research/phase3/P3_fidelity_check.py` against **the same tolerances** as the engine fidelity test (`research/phase3/P3_fidelity_tolerances.json`, unchanged):
   - buy and sell match ≥ 99%;
   - quantities ≥ 98%;
   - prices ≥ 99% exact;
   - commissions and slippage within 1%;
   - daily-return RMSE ≤ 0.0005, max ≤ 0.005;
   - terminal value within 0.5%;
   - cash within 1% on ≥ 99% of days;
   - equal forced exits.
4. **R4 must hold in LEAN** (cost ≤ 1.5% a year, no leverage, the harness integrity checks pass).

**Q3 failure:**
- It is a technical finding, never a reason to change a rule.
- If the cause is an engine defect, the engine is fixed and the **whole search** (all null and real runs) is repeated outcome-blind.

## 16. Internal OOS (Q4): one shot, 2018-01-01 → 2021-12-31

**Run set** (once; no re-runs except a documented technical failure before any result is read):
- the candidate (S019, $100K, history-only warm-up from 2017-05-01, the search's 8-month offset; indicator windows come from history; the book starts empty with $100K on 2018-01-02);
- the same-universe EW book (the B901 mechanics, as E901-type runs);
- **five matched-random twins:** identical engine, slots, holding, costs, cash and **daily entry counts** of the candidate; stocks drawn by SHA-256(seed | sid | date) among eligible names; seeds 1–5;
- SPY total return (E900-07 window);
- the candidate at **2×, 4× and 6× slippage**;
- the candidate at **$200K**.

**Q4 passes iff all of the following hold** (Amendment 3 definitions on the OOS window):
- **W1:** CAGR(candidate) > CAGR(SPY).
- **W3:** CAGR(candidate) > CAGR(EW) **and** > the median CAGR of the five twins. Fewer than five completed twins → fail.
- **R1:** MaxDD ≥ MaxDD(SPY) − 10 points.
- **R2:** Sharpe ≥ Sharpe(SPY) − 0.15.
- **R4:** cost ≤ 1.5% a year; no leverage.
- **Evidence:** g / SE ≥ **1.0**. This is the frozen W2 statistic: g = 252 × mean daily log excess vs SPY; SE = max(iid, exact stationary-bootstrap SE, q = 1 − 1/126). The 2.15 threshold is not attainable on 4 years.
- **Cost robustness:** W1 still holds at **2× slippage**.

**Reported only:**
- R3 (two-year blocks 2018–19 and 2020–21);
- 4× and 6× slippage;
- $200K;
- rolling 1- and 3-year windows (`wealth.rolling_report`);
- the full 2010–2021 table, flagged as selection-biased.

**If Q4 fails, it fails:** No Production Candidate Found. 2018–2021 is never used again in Phase 3.

## 17. Robustness requirements (all frozen; nothing added later)

| Robustness | Where | Status |
|---|---|---|
| Parameter stability | Plateau: PS = the lower quartile of the neighbourhood; cluster ≥ 3 connected configurations; centre interior | Gate (§8, §9) |
| Time consistency | ≥ 3 of 4 positive folds; score = median fold | Gate (§7) |
| Procedure persistence | The walk-forward | Gate (Q2) |
| Engine fidelity | LEAN reproduction | Gate (Q3) |
| Cost robustness | W1 at 2× slippage on the internal OOS | Gate (Q4); 4×/6× reported |
| Capital | $200K | Reported |
| Axis sensitivity | s along each axis through the centre; the cluster's parameter ranges | Reported |

## 18. Holdout criteria (unchanged, Amendment 3 §4)

1. **Freeze first:** the single candidate (spec, code, parameters, portfolio, costs and evaluation) is hash-pinned before any request.
2. **Owner approval:** written, recorded in `HOLDOUT_UNLOCK.md`.
3. **One run set** on 2022-01-01 → 2026-08-31: the candidate, EW, five twins and SPY.
4. **Gates:**
   - **HO-W:** CAGR > SPY;
   - **HO-R:** R1.
5. **After the Holdout:** never modified; a forward test only after further owner approval.

There is no regime overlay in Phase 3, so the P3-CP1 market-timing exception does not apply.

## 19. Runs, batching and approvals

**Strategy and hypothesis ids:**
- **H018** = the procedure.
- **S018 v1.0** = a byte copy of X984 at its final, fidelity-verified revision (E984-09: all tolerances pass on the final code) for all search, null and trace runs.
- **S019** = the LEAN finalist strategy (§15).

**Runs, after the owner approves the search** (configs carry `owner_approval_required`; the runner refuses without `--owner-approved <decision id>`):

| Run | Content |
|---|---|
| E018-01 … E018-05 | Primary null worlds, seeds 1 … 500, in 5 deterministic batches of 100 consecutive seeds. 100 worlds is the scale verified by the runtime canaries (E984-03, E984-05, E984-07). A world's result does not depend on its batch: each world is an independent, seeded book set on the same features. Verified: the same seeds in different runs give identical books (E984-02 / E984-03 / E984-05), and the real signal masks are identical whatever the batch (digest of every session's 1,533 masks: E984-07, 100 worlds = E984-08, 1 world). Batch independence rests on one engine rule: in search and canary modes every stock stays subscribed from its first eligibility until it is delisted, so each price window is loaded once (history without fill-forward) and then streamed, whatever the books hold |
| E018-06 | Secondary block-null worlds, seeds 1001 … 1100 (63-session blocks) |
| **then: τ is computed and committed** (`research/phase3/P3_null_result.json`) **before the real run is started** | |
| E018-07 | The real world (identity mapping), one run, publishing per-configuration yearly statistics and monthly log excess |
| Evaluation | `research/phase3/P3_eval.py`: T_real, Q1, the clusters, the ranking, Q2, diagnostics. Then **STOP at the search checkpoint** (P3-CP3) |
| After P3-CP3 | Q3 (S019 build + canary + finalist runs + shadow traces). The internal OOS needs a further explicit owner approval (it uses 2018–2021, once) |

**Technical repeats** (outcome-blind only):
- a run that dies, stalls or fails a canary or integrity check is repeated unchanged and recorded;
- an engine defect → fix → repeat the whole affected stage (all null worlds and the real world).

## 20. Outputs and reporting

**Null runs publish one summary per world:**
- T and the best centre PS;
- the number of eligible configurations, survivors and clusters;
- the ranked centres;
- the walk-forward picks and excesses.

**The real run publishes, per configuration:**
- yearly log excess, costs, mean equity, notional and drawdown;
- monthly log excess.

These are derived results only (licence). No QuantConnect price data leaves the platform.

**Every report states:**
- the total number of hypotheses, strategies, configurations and experiments tested;
- the number of null repetitions and the number passing;
- the false-pass rate with its 95% interval.

## 21. Code that implements this specification

| Section | Module / file |
|---|---|
| §3–5 grammar, features | `src/qresearch/lean/qr_p3_grammar.py`, `qr_p3_features.py` |
| §6 engine | `src/qresearch/lean/qr_p3_engine.py` (harness-identical sizing; `tests/test_p3_engine.py`) |
| §7–11 selection | `src/qresearch/lean/qr_p3_pipeline.py` |
| §12 null | `qr_p3_engine.null_permutation`, `strategies/S018_p3_search/main.py`, `research/phase3/P3_null_precision.py` |
| §15 fidelity | `research/phase3/P3_fidelity_check.py`, `P3_fidelity_tolerances.json` |
| Pins | `src/qresearch/p3spec.py` (this file's hash, the configuration-list hash) |
