# P3-CP1 — Systematic Multi-Indicator Technical Strategy Search: Architecture Proposal (STOP)

- **Date:** 2026-10-04.
- **Owner direction:** "Phase 3 — Close Phase 2 and Design a Systematic Multi-Indicator Technical Strategy Search" (2026-10-04; summary `docs/owner/2026-10-04_close_phase2_design_phase3.md`).
- **This is design only:**
  - no optimizer, no strategy configuration and no technical-indicator return were built or computed;
  - no backtest was run; the Holdout is untouched; nothing was bought.
- **Supporting studies** (`research/phase3/`):
  - `P3_literature_review.md`;
  - `P3_cost_feasibility.py/.json`: analytic, no returns;
  - `P3_search_space.py/.json`: counts only, nothing generated;
  - `P3_calibration.py/.json`: uses only already-completed **control** books (SPY, EW-H017, the five random-event books). No candidate result, and no H017 candidate result.

## Summary

| Question | Short answer |
|---|---|
| **A** — Up to 7–8 indicators? | Yes as a **pool** of candidate indicators across information families; **no** as 7–8 stacked conditions in one rule. Each strategy has at most 3 conditions (1 setup + 1 confirmation from a different family + 1 risk filter), plus a market-regime overlay tested once in Stage 2 (§6) |
| **B** — How many configurations? | ≈ **1,560** in total (1,533 in Stage 1 + ≤ 24 in Stage 2), with a search-level permutation null. Highly correlated, so the effective number is far smaller |
| **C** — Grammar vs free combinations? | A constrained grammar: 1,533 configurations instead of 2.3 × 10⁹ free combinations of up to 8 conditions |
| **D** — Plateau vs peak? | Neighbourhood lower-quartile score + fold consistency + connected clusters; the cluster centre is chosen, never the peak (§15) |
| **E** — How to split 2010–2021? | **Search 2010-03 → 2017-12** (four two-year folds); **procedure walk-forward 2014–2017**; **internal OOS 2018–2021, used once** for one candidate; Holdout locked. This is the project's pre-existing 2010 scheme (D034: IS 2010–17, VAL 2018–21, WF folds), not a performance-based choice |
| **F** — Walk-forward or fixed split? | Both: a **procedure-level** walk-forward inside 2010–2017 (does a choice made on past data keep working the next year?) **and** one untouched fixed internal OOS |
| **G** — Promotion to QuantConnect verification? | Only plateau clusters above the search-null 95th percentile, ordered by the one-standard-error simplicity rule: at most 3 to Stage 2, at most 2 to full LEAN verification, exactly 1 to internal OOS |
| **H** — How often does the optimizer find a fake winner? | Measured by running the **entire** procedure on permutation-null data (R = 39 replicates). Calibration on our control books: under no edge, the best training configuration beats SPY essentially **100%** of the time (median fake excess ≈ +7% a year). The proposed chain cuts false final passes to ≈ 1% |
| **I** — Evidence to open the Holdout? | All of Q1–Q4 (§26): search-null significance (family-wise p ≤ 0.05), positive procedure walk-forward, LEAN fidelity, and a one-shot internal OOS passing W1, W3, R1, R2, R4, g/SE ≥ 1 and W1 at 2× slippage |

**Honest expectation:**
- Calibration (§17 and §26) shows that only large selection edges have a realistic chance:
  - ≈ 6–8% a year above a random book (≈ 4–6% above SPY in 2010–17) is needed;
  - edges of ≤ 4% a year are essentially undetectable with this history.
- The ≥ $2B equal-weight universe trailed SPY by **4.1% a year in 2018–2021**, a headwind for any stock-selection strategy in the internal OOS.
- The most likely outcome is again **"No Production Candidate Found"**. The architecture makes that a fair and informative result, and makes a lucky configuration very unlikely to reach the Holdout.

---

## 1. Formal closure of Phase 2

- **Phase 2 is CLOSED: No Production Candidate Found** (owner, 2026-10-04).
- **Hypotheses:**

  | Slot | Hypothesis | Outcome |
  |---|---|---|
  | 1 | H014 | Rejected |
  | — | H015 | Not adopted (no slot used) |
  | 2 | H016 | Rejected |
  | 3 | H017 | Rejected (Case A; preserved exactly as tested; never tuned, repaired or re-run) |

- **Holdout:** 2022-01-01 → 2026-08-31 remains locked and has never been opened.
- **Data:** no data purchased.
- **Amendment 3, Event Data v1 and data infrastructure v1** remain frozen as historical records. Phase 3 reuses the data infrastructure v1 universe and Amendment 3's gate definitions where stated; nothing is changed.
- **H017's results are not used** to design Phase 3 (owner instruction 26).

## 2. Phase 3 objective

Unchanged: starting with the same capital on the same date, finish with **more wealth than SPY buy-and-hold total return** after realistic costs, without leverage.

- **Accounts:** $100K primary; $200K sensitivity only.
- **Every final candidate reports:**
  - starting capital;
  - final strategy value and final SPY value;
  - strategy CAGR, SPY CAGR and excess CAGR;
  - terminal-wealth ratio.
- **Risk statistics** are safeguards, not the objective.

## 3. Why Phase 3 is methodologically different

| Phase 2 | Phase 3 |
|---|---|
| One hand-designed hypothesis per slot, from the literature | A pre-declared, finite space of ≈ 1,560 technical configurations searched mechanically |
| Selection risk ≈ 3 trials | Selection risk ≈ thousands of correlated trials: the dominant risk is data mining |
| Evidence = one backtest vs controls | Evidence = the search **beats its own null**, a plateau (not a peak), procedure walk-forward, then one untouched OOS |
| Development 2010–2021 used for one candidate | 2010–2017 for search; 2018–2021 kept untouched for one candidate |

## 4. Proposed technical indicator families

All are computed point-in-time from split- and dividend-adjusted daily bars (as known at the close), for the frozen data-v1 universe:
- US common stock;
- point-in-time market cap ≥ $2B;
- price ≥ $5;
- ADV20 ≥ $5M;
- the SEC correction layer;
- financials included.

| Information family | Indicators (role) | Literature |
|---|---|---|
| **Trend** | Close vs SMA(L); SMA(S) vs SMA(L); SMA slope; MACD line > 0 (≡ EMA12 > EMA26); ADX strength | Brock et al. 1992; Faber 2007; Han, Yang & Zhou 2013 |
| **Momentum** (incl. relative strength) | Cross-sectional K-month return rank (skip 1 month); time-series return > 0; return minus SPY return; RSI(14) high; MACD vs signal | Jegadeesh & Titman 1993; Asness et al. 2013 |
| **Breakout** | Close within x% of the N-day high | George & Hwang 2004 |
| **Pullback / mean reversion** (inside a longer hold) | RSI(n) low; close below SMA(20) by y%; Bollinger %b low | Jegadeesh 1990; practitioner |
| **Volatility** (risk filter) | 63-session realised-volatility cross-sectional rank (ATR% is the same information and is not added) | Ang et al. 2006 |
| **Participation** (confirmation) | Relative volume 20/120 sessions | Lee & Swaminathan 2000 |
| **Market regime** (Stage 2 overlay only) | SPY > SMA(200) for new entries | Faber 2007 |

**Excluded, with reasons:**
- **Short-horizon oscillator trading** (RSI(2) / 5-day holds): costs. A 10-session hold costs ≈ 4.9% a year in slippage alone.
- **Intraday or gap rules:** out of scope.
- **Fine pattern recognition:** degrees of freedom.
- **News or fundamentals:** not technical; Phase 2 covered fundamentals.

## 5. Redundancy and correlation grouping

**Indicators are grouped by the information they encode, not by name:**
- close > SMA, SMA cross, MACD > 0 and ADX are **trend**;
- RSI(14) ≥ 50, MACD vs signal, K-month return and return vs SPY are **momentum**;
- %b and the distance below SMA(20) are the **same** pullback information;
- ATR% duplicates realised volatility.

**Rules:**
1. **One information family per role:** a confirmation must come from a different family than the primary setup. Correlated indicators therefore never count as independent confirmations.
2. **Feature-only redundancy check before freezing** (implementation step 1; uses no returns):
   - compute the average daily cross-sectional Spearman correlation between every pair of condition variants' strength measures on 2010-03 → 2017-12;
   - any cross-family pair with ρ > 0.8 is merged into one family for rule 1.
3. **Effective number of trials:** reported from the eigenvalues of the configurations' return correlation matrix (Nyholt / Li-Ji). The permutation null (§17) accounts for correlation automatically.

## 6. Proposed strategy grammar

```
Strategy := Primary setup (exactly 1, one family: trend | momentum | breakout | pullback)
           AND Confirmation (0 or 1, from a DIFFERENT family: trend | momentum | breakout | pullback | participation)
           AND Risk filter (0 or 1: volatility rank)
Ranking   := the primary setup's own strength measure (fixed; e.g. distance above the SMA, return, closeness to the high,
             depth of the pullback); ties by security id
Portfolio := slot-filling: each close, eligible stocks satisfying the rule, ranked, fill the free slots; next-open
             market orders; no queue; held stocks ignored
Exit      := Stage 1: fixed horizon H = 63 sessions (exit order at sessions held = 62)
             Stage 2 (≤ 3 promoted clusters only): {H = 63, H = 126, primary-condition reversal (weekly check, min 21,
             max 126 sessions), 3 × ATR(14) trailing stop (max 126)} × {no regime overlay, SPY > SMA200 for new entries}
```

**Comparison of the alternatives:**

| Approach | Size | Verdict |
|---|---|---|
| Full combinatorial (any AND of up to 8 of 58 condition variants) | 2.26 × 10⁹ (× 8 with exits / regime) | Statistically hopeless; the Novy-Marx multi-signal bias |
| Fine-grid sweep of one 7-indicator template | 5.4 × 10¹¹ | Fake precision |
| **Constrained grammar, staged entry → exit** | **1,533 + ≤ 24** | **Recommended** |
| Staged greedy (add indicators one at a time) | Smaller, but path-dependent; hidden degrees of freedom | Rejected: the selection path is itself a search |

**Why staged entry → exit:**
- Stage 1 isolates the information in the **entry selection** under one frozen, cost-feasible exit.
- Stage 2 tests ≤ 8 exit / overlay variants on ≤ 3 clusters, and keeps the base exit unless an alternative is better by more than one standard error.
- Entry × exit × stops × targets are never searched jointly.

## 7. Exact proposed parameter ranges

Coarse, literature-anchored, 2–4 values each, roughly geometric. No fine grids.

| Component | Variants |
|---|---|
| **Primary: trend** | T1 close > SMA(L), L ∈ {50, 100, 150, 200}; T2 SMA(S) > SMA(L), (S, L) ∈ {(20, 100), (50, 150), (50, 200)}; T3 21-session slope of SMA(L) > 0, L ∈ {100, 200} — **9** |
| **Primary: momentum** | M1 cross-sectional rank of return(K, skipping 21), K ∈ {63, 126, 252}, top q ∈ {10, 20, 30}%; M2 return(K) > 0; M3 return(K) − SPY return(K) > 0, K ∈ {63, 126, 252} — **15** |
| **Primary: breakout** | B1 close ≥ (1 − x) × max close(N), N ∈ {63, 126, 252}, x ∈ {0, 5, 10}% — **9** |
| **Primary: pullback** | R1 RSI(n) ≤ θ, (n, θ) ∈ {(2, 10), (2, 20), (5, 30), (14, 40)}; R2 close ≤ SMA(20) × (1 − y), y ∈ {3, 6}%; R3 %b(20, 2) ≤ {0, 0.2} — **8** |
| **Confirmation: trend** | close > SMA200; SMA50 > SMA200; ADX(14) ≥ {20, 25}; MACD(12, 26) > 0 — 5 |
| **Confirmation: momentum** | return(126) > 0; return(252 skipping 21) > 0; RSI(14) ≥ {50, 60}; MACD > signal(9) — 5 |
| **Confirmation: breakout** | close ≥ 0.9 × max close(252) — 1 |
| **Confirmation: pullback** | RSI(5) ≤ 30; close < SMA(20) — 2 |
| **Confirmation: participation** | relative volume 20/120 ≥ {1.0, 1.25} — 2 |
| **Risk filter** | none; 63-session realised-volatility rank ≤ {50, 80}% — 3 |
| **Stage 1 exit / portfolio** | H = 63 sessions, N = 10 slots (§22) |
| **Stage 2** | 4 exits × 2 regime options, ≤ 3 clusters |

## 8. Estimated raw search-space size

| Primary family | Primaries | Confirmation options | Risk options | Configurations |
|---|---|---|---|---|
| Trend | 9 | 11 | 3 | 297 |
| Momentum | 15 | 11 | 3 | 495 |
| Breakout | 9 | 15 | 3 | 405 |
| Pullback | 8 | 14 | 3 | 336 |
| **Stage 1** | | | | **1,533** |
| **Stage 2** | | | | **≤ 24** |
| **Total budget** | | | | **≤ 1,557** |

Free AND-combinations of the same 58 condition variants:
- ≤ 3 conditions: 32,567;
- ≤ 4: 456,837;
- ≤ 6: 4.6 × 10⁷;
- ≤ 8: 2.3 × 10⁹.

## 9. Method for reducing the space

1. **Information families**, with one per role (§5).
2. **At most 3 conditions**, by grammar.
3. **Coarse grids** of 2–4 values.
4. **Cost-derived exclusions:** holding < ≈ 56 sessions is infeasible for 10 slots at $100K under R4 (P3_cost_feasibility: the minimum H is 56 at a 1.5% cost cap).
5. **Fixed, not searched:**
   - ranking key;
   - portfolio mechanics;
   - Stage 1 exit;
   - slot count.
6. **Staging:** exits and the regime overlay are tested only on ≤ 3 promoted clusters.
7. **Fixed budget:** one Stage-1 round, never repeated after seeing results.

## 10. Development / validation / internal-OOS architecture

```
2009-07 ───── 2010-03 ─────────────────────── 2017-12 ─────────── 2021-12 ─────────── 2026-08
 warm-up      │ SEARCH (Stage 1/2, plateau, nulls)  │ INTERNAL OOS      │ HOLDOUT (locked)
 (history)    │ folds: 2010-11 | 2012-13 | 2014-15 | 2016-17 │ used ONCE, 1 candidate │ 1 candidate, owner approval
              │ procedure walk-forward tests: 2014, 2015, 2016, 2017       │
```

**Why this partition:**
1. **Not chosen on performance:** it is the project's pre-existing 2010 scheme (D034: IS 2010–17, VAL 2018–21, annual walk-forward folds).
2. **Search span:** 7.8 years for the search (four two-year folds) is the minimum to see two different market phases per fold set.
3. **OOS span:** 4 years of untouched internal OOS is the longest that still leaves the search ≥ 7 years.
4. **The Holdout stays a second, independent confirmation.**

**Disclosure:** 2018–2021 is **procedurally** untouched by Phase 3 (no Phase 3 configuration ever sees it before the single candidate is frozen), but not **knowledge**-pristine. Phases 1–2 used it, and some aggregate behaviour of that period is known. The Holdout and a true forward test are the only knowledge-pristine data.

**Rejected alternatives:**
- One long training period plus a short validation: less robust fold structure.
- Combinatorial purged CV as the main design: too little history for many groups. It is kept as the PBO diagnostic only.
- Using 2018–2021 inside the walk-forward: it would leave no untouched OOS before the Holdout.

## 11. Walk-forward methodology (procedure-level)

**Steps**, for each test year Y ∈ {2014, 2015, 2016, 2017}:
1. **Re-run the complete frozen selection procedure:**
   - hard filters;
   - plateau scoring;
   - search-null threshold;
   - the one-standard-error simplicity rule;
   - the base Stage-1 exit.

   It uses **only** monthly results through December of Y−1 (folds = the available two-year blocks; ≥ 2 required).
2. **Record the selected configuration's returns in year Y** from its continuous book. The book's state at the start of Y depends only on rules fixed before Y.
3. **Concatenate** the four OOS years and compare with:
   - SPY;
   - the EW universe;
   - the selected configurations' matched-random twins.

**Output: the walk-forward efficiency.** Does a choice made only on past data keep working in the next unseen year? The procedure, not one configuration, is tested.

**No new configurations are created:** the walk-forward re-uses the Stage-1 shadow results restricted to past months.

## 12. Purging and embargo

**Holding periods overlap fold boundaries (63–126 sessions):**
- **Walk-forward selection** uses only monthly returns through December of Y−1. The test year starts afterwards. No test-period outcome enters selection, so purging is automatic.
- **Fold scores inside the search window** are all training data. They measure consistency, not out-of-sample performance, so no purge is needed.
- **CSCV / PBO diagnostic:** an embargo of 3 months (≥ 63 sessions) at every train/test block boundary. For 126-session Stage-2 variants, 6 months.
- **Feature look-backs** (up to 252 sessions) use only past prices: no label leakage. The history-only warm-up starts 2009-07-01, as for H017.

## 13. Search objective

**Primary score of a configuration:**

> s(c) = **median over the four training folds** of the fold's annualised log excess growth over SPY, after all costs
> = median_k [ 252 × mean_t∈fold k ( ln(1 + r_c,t) − ln(1 + r_SPY,t) ) ]

- Log excess growth is exactly the per-year change in the **terminal-wealth ratio** vs SPY. It matches the objective, which plain Sharpe or CAGR do not.
- The **median over folds** rewards consistency; a single lucky fold cannot carry it.

**Hard safeguard filters** (a configuration failing any is not eligible), on the training window:
- realised costs ≤ 1.5% a year (R4);
- maximum drawdown ≥ SPY's − 10 points (R1);
- at least **3 of 4 folds** with positive excess over SPY.

**No composite with tunable weights.** Risk, cost and consistency enter as pass/fail safeguards; plateau and simplicity are separate selection rules (§14–15).

## 14. Complexity penalty: the one-standard-error rule

- **Complexity** c(x) = number of conditions (1 primary + confirmation + risk filter; 1–3 in Stage 1). Stage-2 exits other than the base, and the regime overlay, each add 1.
- **Rule:** among plateau clusters above the null threshold (§15, §17), take the best plateau score PS*, and its standard error SE* (stationary bootstrap of the centre's monthly excess series, mean block 6 months, the PS computation repeated).
- **Eligible:** clusters with PS ≥ PS* − SE*.
- **Choose:**
  1. the **lowest complexity**;
  2. then the lowest turnover;
  3. then the highest PS.
- **Stage 2** keeps the base exit and no overlay unless an alternative improves s by more than one SE.
- **Effect:** an 8-condition strategy cannot beat a 3-condition one "by a tiny amount" (and 8 conditions are not allowed anyway). There is no arbitrary weight.

## 15. Plateau and parameter-stability definition

**Neighbourhood N(c):** configurations differing from c in exactly one step:
- one grid step in one ordinal parameter of any component (L, K, q, N, x, θ, y, vol-rank cut, ADX or RSI threshold); **or**
- swapping the confirmation for a sibling variant of the same indicator (e.g. RSI ≥ 50 ↔ RSI ≥ 60); **or**
- adding or removing the risk filter.

**Definitions:**
- **Plateau score:** PS(c) = the **25th percentile** of { s(c′) : c′ ∈ N(c) ∪ {c} }. This requires at least ≈ 75% of the neighbourhood to be at least as good; an isolated peak scores low.
- **Eligibility:** |N(c)| ≥ 3; c passes the safeguards; c is in ≥ 3 of 4 positive folds.
- **Plateau region:**
  - survivors = eligible configurations with PS(c) > τ, where τ is the search-null threshold (§17);
  - **clusters** = connected components of survivors in the neighbourhood graph.
- **Cluster representative = the centre:** the survivor whose entire neighbourhood is inside the cluster (an interior point) with the highest PS; if none is interior, the survivor with the most in-cluster neighbours. **Never the single best s(c).**
- **Reported for each cluster:**
  - size;
  - parameter ranges (e.g. "SMA 100–200, top 20–30%");
  - the fraction of members positive in each fold;
  - sensitivity: s along each parameter axis.

**Example:** "MA 153 works, MA 150 and 160 fail" cannot pass. The grid has no 153; its neighbours would pull its PS down; and its cluster would be a single point.

## 16. Multiple-testing controls (the smallest coherent set)

| Control | Role | Why |
|---|---|---|
| **1. Search-level permutation null** (§17) | **Primary gate (Q1):** family-wise p of the best plateau score, procedure included | It tests exactly what we do (filters + plateau + max over a correlated space). White's and Hansen's tests cannot see the plateau step |
| **2. Hansen's SPA** (stationary bootstrap, studentised, monthly excess vs SPY of the 1,533 configurations) | Secondary report: "does any configuration beat SPY after the search?" | Standard, complementary; it handles poor configurations better than White's test |
| **3. Procedure walk-forward + one-shot internal OOS** | Q2, Q4 | Persistence on unseen data is the decisive test (Sullivan, Timmermann & White) |
| **4. PBO (CSCV) and DSR** | Diagnostics only | Describe overfitting tendency. DSR is already diagnostic under Amendment 3 |

**Not used, and why:**
- White's Reality Check: SPA dominates it.
- StepM / FDR: only one candidate is promoted, so the family-wise null is sufficient.
- Bonferroni: far too conservative for 1,533 correlated trials.

## 17. Search-null experiment ("how often does the optimizer find a fake winner?")

**Null data: daily cross-sectional permutation of signals.**
- On each day t and replicate r, a fixed seeded permutation π_t,r maps the eligible stocks' **signal rows** to **traded stocks**.
- Each configuration computes its conditions and ranking exactly as in the real search, but trades π(stock).
- **Preserved:**
  - each configuration's entry counts, holding, turnover, costs and cash;
  - the market-level timing content (how many stocks pass a filter);
  - the **correlation between configurations**: all of them use the same permuted signals, so neighbours stay similar;
  - the eligible universe.
- **Destroyed:** the link between a stock's own technical history and its own future return, i.e. the stock-selection information the search claims to find.

**Procedure:**
- Run the **entire** selection procedure (safeguards, plateau, clusters) on each of R = **39** null replicates.
- Record the best plateau score.
- **Family-wise p** = (1 + #{null best PS ≥ observed best PS}) / (R + 1).
- **τ** = the 95th percentile of the null best PS (R = 39 gives p ≥ 0.025 resolution).

**Calibration preview** (`P3_calibration.json`; control books only):
- **Measured no-skill behaviour:**
  - a random 10-stock book in this universe trails SPY by ≈ 2.0% a year in 2010–17 (−1.6% vs the universe EW);
  - tracking error vs SPY 8.1% (12.8% in 2018–21);
  - correlation of two random books' excess ≈ 0.50.
- **Gaussian simulation of the proposed procedure** (1,536 configurations, neighbourhoods of 8; three correlation scenarios):

| Under no edge | Result |
|---|---|
| Probability the best raw configuration beats SPY in training | **100%** |
| Median best raw training excess | **+6.0 to +7.3% a year** |
| Probability the best **plateau** beats SPY in training | ≈ 99% |
| Null 95th percentile τ of the best plateau score | **+4.9% to +6.7% a year** |
| Selected configuration's mean 2018–21 excess vs SPY | −5.8% a year (the universe headwind + no skill) |
| Probability the selected configuration passes the internal-OOS chain (W1, W3 proxy, g/SE ≥ 1) | **≈ 1%** |

**Conclusion:** without the null threshold, a "winner" is guaranteed. The real τ is measured on the actual configurations, not the simulation.

## 18. Random portfolio controls

| Control | Definition | Answers |
|---|---|---|
| **SPY** | E900-07 total return, same dates | The objective |
| **Same-universe EW** | Monthly, 25% band, $10M paper (B901 mechanics) | Universe effect |
| **Matched-random twins** | For the final candidate (and each walk-forward pick): identical engine, slots, holding, costs, cash and **daily entry counts**; stocks chosen by SHA-256(seed\|sid\|date) among eligible names. Seeds 1–5 for W3; seed 0 for canaries | Stock selection vs random selection at the same moments |
| **Permutation-null replicates** | §17 | The search itself |

## 19. Search budget (fixed before searching)

| Item | Budget |
|---|---|
| Configurations | ≤ **1,557** (1,533 Stage 1 + ≤ 24 Stage 2) |
| Search rounds | **1** Stage-1 round + **1** Stage-2 round. **No second Stage-1 round**: any redesign after results is a new phase and an owner decision |
| Null replicates | 39 (× 1,533) |
| Plateau clusters promoted to Stage 2 | ≤ **3** |
| Finalists to full LEAN verification (training window) | ≤ **2** |
| Candidates to the internal OOS | **exactly 1** |
| Candidates to the Holdout | **exactly 1**, with written owner approval |
| Technical repeats | Outcome-blind only (an engine bug found by a canary or fidelity check → fix → re-run the **whole** affected stage; recorded) |

## 20. Computational architecture

| Option | Licence / data | Fidelity | Speed | Verdict |
|---|---|---|---|---|
| Thousands of full QuantConnect harness backtests | OK | Exact | ≈ 15 min each: 1,533 → ≈ 16 days of node time (+ nulls: impossible) | Rejected |
| LEAN locally | Needs a local data licence / purchase; raw-data export is forbidden | Exact | Fast | Rejected (no purchase, licence) |
| Vectorised Python locally | Needs local prices: QuantConnect data cannot be exported; free sources (Yahoo, Stooq) are survivorship-biased and lack point-in-time market cap | Universe wrong | Fast | Rejected |
| QuantConnect research notebooks | OK (data stays in the cloud) | Good | Depends on the research node available to our seat (to be checked; no purchase) | Possible fallback |
| **In-cloud "shadow-book" engine inside a LEAN backtest** | **OK**: data never leaves QuantConnect; only derived results (monthly returns, fold scores) are exported | High: same universe, same point-in-time data, same calendar, same SPY | One backtest evaluates thousands of virtual books | **Recommended** |

**Shadow-book engine (to be built only after approval):**
- **Platform:** a non-trading LEAN algorithm using the frozen harness for the universe and the warm-up.
- **Features:** each close, computes every base condition **once**, as numpy arrays over the eligible stocks, from adjusted windows.
- **Configurations:** composed as AND-masks plus the primary strength ranking.
- **Book mechanics:** vectorised arrays of virtual books (slots × entry price × entry session) apply exactly the H017-verified mechanics:
  - next-open fills ± 10 bps;
  - $7 per order;
  - D051 settled cash with the 15% gap reserve and 2% buffer;
  - target 0.98/N;
  - $4,000 minimum;
  - fixed horizon;
  - no top-ups;
  - delisted or untradeable holdings closed at the last real close (the D059 convention).
- **Output:** monthly log returns of the real configurations (≈ 1.5 MB per full set) and fold scores of the null replicates, as summary-statistic chunks. These are derived results only.
- **Runs:** split by primary family and null replicate block, ≈ 6–10 cloud runs of ≈ 0.5–2 h each.

## 21. Fast screening vs LEAN verification

**What the shadow engine reproduces exactly:**
- the universe and eligibility (the same harness code);
- point-in-time adjusted signals;
- decision at the close and fills at the next open with fixed slippage;
- the $7 commission;
- settled-cash funding and sizing;
- the holding clock;
- the delisting / stale-exit convention.

**What it approximates (all verified in LEAN for finalists):**
- dividends are taken through adjusted prices rather than as cash credits (a sub-basis-point difference in cash timing);
- integer-share rounding;
- LEAN's order cancellations on ticker changes and their re-issue;
- exact forced-exit prices on acquisitions.

**Fidelity protocol** (no technical returns are revealed by it):
1. **Before Stage 1:** the shadow engine replicates **existing control books**:
   - the H017 random-event books E017-03 … 07 (same mechanics, seeds known);
   - the canary E982-02.

   **Tolerance:** |ΔCAGR| ≤ 0.3 point a year; monthly-return correlation ≥ 0.99; positions identical on ≥ 95% of days.
2. **After selection:** each finalist (≤ 2) is run as a full harness strategy (S018) on 2010-03 → 2017-12, with a byte-copy canary.

   **Tolerance:** |ΔCAGR| ≤ 0.5 point a year; monthly correlation ≥ 0.97.

   A failure is a **technical** finding: fix the engine and repeat the stage outcome-blind.

## 22. Portfolio-construction methodology (no performance used)

The slot count follows from the **cost model and holding period**, never from returns:
- **Rule:** N = the largest slot count with projected cost ≤ 1.5% a year at $100K and position ≥ $4,000, capped at 20 and floored at 10 for diversification.
- **Stage 1 (H = 63):**
  - cost-feasible N ≤ 12 at 1.5%;
  - with the floor, **N = 10**: projected cost ≈ 1.34% a year at $100K, lower as equity grows.
- **Stage 2 (H = 126):** **N = 20** (projected ≈ 0.95%).
- **Mechanics:** H017's canary-verified slot-filling engine:
  - target 0.98/N, maximum weight 10%, $4,000 minimum;
  - D051 settled cash, 2% buffer, 15% gap reserve;
  - no top-ups, no leverage, long-only;
  - daily decisions, next-open orders.
- **$200K:** sensitivity only.

## 23. Cost handling

- **Base:** $7 per buy and per sell; 10 bps slippage per side, applied **inside** the search. Every score is net of costs, so a high-turnover configuration is penalised automatically.
- **Safeguard:** realised cost ≤ 1.5% a year (R4) in training.
- **Stress:** the final candidate at 2× slippage in the internal OOS (W1 must hold, Q4); 4× and 6× reported.

## 24. Candidate-promotion pipeline

```
1,533 Stage-1 configurations (training 2010-03 → 2017-12, shadow engine) + 39 permutation-null replicates
   │ safeguards: cost ≤ 1.5%, MaxDD ≥ SPY − 10 pts, ≥ 3/4 folds > SPY, |N(c)| ≥ 3
   ▼
plateau survivors: PS(c) > τ (null 95th pct)  → clusters (connected components)            [Q1: family-wise p ≤ 0.05]
   │ one-standard-error rule (lowest complexity, then turnover)
   ▼
≤ 3 clusters → Stage 2 (≤ 8 exit/overlay variants each; base kept unless > 1 SE better)
   ▼
procedure walk-forward 2014–2017 (re-selection each year from past data only)               [Q2]
   ▼
≤ 2 finalists → full LEAN harness (S018) on training + canary; fidelity                     [Q3]
   ▼
exactly 1 final candidate (rank 1; rank 2 only if rank 1 fails a technical/fidelity/R4 check in LEAN)
   │ freeze: rules, parameters, portfolio, costs, evaluation
   ▼
internal OOS 2018–2021, ONE run set: candidate + EW + 5 matched-random twins (+ 2×/4×/6× slippage)   [Q4]
   ▼
STOP → owner decision → Holdout (exactly 1 candidate)
```

## 25. Number of candidates at each stage

| Stage | Number |
|---|---|
| Stage-1 configurations | 1,533 |
| Null replicates | 39 × 1,533 |
| Clusters → Stage 2 | ≤ 3 |
| Stage-2 configurations | ≤ 24 |
| LEAN-verified finalists | ≤ 2 |
| Internal-OOS candidate | 1 |
| Holdout candidate | 1 |

If no cluster passes Q1, the phase stops at the search: **No Production Candidate Found**.

## 26. Final-candidate qualification criteria (all required before any Holdout request)

| # | Criterion | Rule |
|---|---|---|
| **Q1** | Search significance | Best plateau score > τ (permutation-null 95th percentile); family-wise p ≤ 0.05. SPA p-value reported |
| **Q2** | Procedure walk-forward 2014–2017 | Concatenated OOS log excess vs SPY > 0 **and** > the median of the walk-forward picks' matched-random twins |
| **Q3** | LEAN fidelity and integrity | Finalist reproduced within tolerance (§21); the canary passes; R4 holds in LEAN |
| **Q4** | Internal OOS 2018–2021, one shot (frozen Amendment 3 definitions on the OOS window) | **W1:** CAGR > SPY. **W3:** CAGR > EW and > the median of 5 matched-random twins. **R1, R2, R4** pass. **g/SE ≥ 1.0** (W2 statistic, frozen SE method; 2.15 is not attainable on 4 years). **W1 at 2× slippage** |
| Report | Full 2010–2021 | Amendment 3 table, rolling reports; selection-biased, so reported, not gated |

**Power, honestly** (calibration simulation; a true selection edge planted in one neighbourhood):

| True selection edge over a random book | Detected and selected (Q1) | Passes Q1 + the internal-OOS chain |
|---|---|---|
| 0% | 0% | 0% |
| 2% a year | 0–0.4% | ≈ 0% |
| 4% a year | 2–5% | ≈ 0% |
| 6% a year | 10–20% | 1–3% |
| 8% a year | 31–53% | 5–13% |

- **False-pass rate of the whole chain under no edge:** ≈ 1% before Q2 and Q3 (lower with them).
- **The design is strict on purpose:** with ≈ 12 years of history, only a large, persistent edge can be distinguished from search luck.

## 27. Rolling-horizon reporting

- **For the final candidate, EW and the matched-random twins:** rolling 1/3/5/10-year comparisons with SPY over every start date (`wealth.rolling_report`), reporting:
  - share of start dates beating SPY;
  - mean and median excess CAGR;
  - 10th / 90th percentiles;
  - worst and best windows;
  - independent windows.
- **Coverage:**
  - on the internal OOS, only the 1-year and 3-year windows are meaningful;
  - on 2010–2021, every horizon is shown, flagged as selection-biased.
- **Diagnostics only:** windows from a sample shorter than twice the horizon are labelled "not evidence", and luck bands come from the random twins.

## 28. Locked-Holdout procedure

1. **Freeze** the single candidate after Q1–Q4: a hash-pinned spec, code, parameters, portfolio, costs and evaluation.
2. **STOP** and request written owner approval, recorded in `HOLDOUT_UNLOCK.md`.
3. **One run set** on 2022-01-01 → 2026-08-31: the candidate, EW, 5 random twins and SPY.
   - Gates (Amendment 3 §4, unchanged): **HO-W** (CAGR > SPY) and **HO-R** (R1).
   - If the Stage-2 regime overlay is part of the candidate (market timing), CAGR > SPY must also hold in 2023-01-01 → 2026-08-31 alone.
4. **After the Holdout:** no modification ever; a forward test only after further owner approval.

## 29. Estimated runtime and cost

| Item | Estimate |
|---|---|
| Implementation (engine, feature-only redundancy check, fidelity canary on control books, null machinery, tests) | ≈ 3–5 working days |
| QuantConnect node time | Stage 1 + 39 nulls ≈ 8–20 h (6–10 runs); Stage 2 ≈ 1 h; LEAN finalists ≈ 1 h; internal OOS set ≈ 2–3 h |
| QuantConnect cost | **$0 extra** (the existing $24/month node; one backtest at a time) |
| Local compute | Minutes (plateau, null and SPA analysis on exported monthly series) |
| Unknowns to test first | Per-backtest runtime / memory / summary-statistic limits for ≈ 10,000 virtual books. A short engine smoke test on control mechanics only, before Stage 1 |

## 30. Main risks

1. **Low power and a low prior** (§26, literature): technical stock-selection edges in liquid US large caps after costs are small or absent; realistic edges are undetectable here. The likely outcome is "No Production Candidate Found".
2. **Universe headwind:** the ≥ $2B equal-weight universe trailed SPY by 4.1% a year in 2018–2021 (mega-cap leadership). Any stock-picking strategy starts behind in the internal OOS.
3. **Knowledge contamination:** 2010–2021 has been studied in Phases 1–2. 2018–2021 is procedurally fresh for Phase 3 but not knowledge-fresh.
4. **Shadow-engine fidelity:** mitigated by the control-book replication and LEAN finalist verification (§21).
5. **QuantConnect limits** (runtime, memory, output size): mitigated by splitting runs and the smoke test.
6. **The permutation null might be imperfect:**
   - it may break genuine risk-premium links (e.g. low-volatility filters);
   - it keeps market timing.

   Reported alongside SPA and the walk-forward.
7. **Regime overlay = market timing:** it brings the stricter Holdout exception.
8. **Temptation to iterate after results:** forbidden by the budget (one Stage-1 round).
9. **Prior exposure:** H005 (low-volatility) failed validation in Phase 1. Volatility is used only as a risk filter, and is still subject to the same null.
10. **Short Holdout** (4.7 years): low power there too. A forward test may be needed after any Holdout pass.

## 31. Exact owner decisions required before implementation

1. **Approve the architecture:**
   - the grammar (§6);
   - the families and ranges (§4, §7);
   - the budget of ≤ 1,557 configurations, one Stage-1 round, ≤ 3 / ≤ 2 / 1 / 1 promotions (§19, §25).
2. **Approve the data partition:**
   - search 2010-03 → 2017-12 (four two-year folds);
   - procedure walk-forward 2014–2017;
   - internal OOS 2018–2021 used once for one candidate;
   - Holdout locked.
3. **Approve the selection rules:**
   - the objective s(c) (§13);
   - the plateau definition (§15);
   - the one-standard-error simplicity rule (§14);
   - the permutation search-null with R = 39 and Hansen's SPA as secondary (§16–17).
4. **Approve the qualification criteria Q1–Q4 and the Holdout procedure** (§26, §28).
5. **Approve the computational architecture:**
   - the in-cloud shadow-book engine (licence-compliant);
   - fidelity tests on control books before any search;
   - LEAN verification of finalists.
6. **Approve the portfolio rule:** cost-derived N and H (Stage 1: N = 10, H = 63; Stage 2 option H = 126, N = 20).
7. **Acknowledge the power analysis and the likely "No Production Candidate Found" outcome,** and decide whether Phase 3 is worth implementing on that basis.
8. **If approved, authorise implementation only:**
   - engine, tests, feature-only redundancy check, and fidelity canaries on control books;
   - then a frozen Phase 3 spec;
   - and a separate approval before the Stage-1 search runs.

**STOP.**
- No optimizer was implemented, no configuration generated, no technical return computed and no candidate selected.
- The Holdout is locked; no data was purchased; no Phase 3 backtest was run.
