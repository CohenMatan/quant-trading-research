# P4-CP1 — Weekly Multi-Indicator Trend/Momentum Research Architecture Proposal (STOP)

- **Date:** 2026-10-04.
- **Owner direction:** "Phase 4 — Design a Weekly Multi-Indicator Trend/Momentum Strategy Research Architecture" (2026-10-04; summary `docs/owner/2026-10-04_phase4_weekly_architecture_design.md`).
- **This is design only.** Nothing was implemented in the engine:
  - no Weekly return was computed;
  - no MA / RSI / MACD configuration was tested or compared;
  - no data was accessed for 2018–2021 candidate evaluation or for the Holdout;
  - nothing was purchased; no search run was started.
- **Supporting studies** (`research/phase4/`, all synthetic or combinatorial):

| Study | What it contains |
|---|---|
| `P4_literature_review.md` | External evidence |
| `P4_search_space.py/.json` | The proposed grammar and its exact count |
| `P4_mechanics.py/.json` | Portfolio-size study: synthetic prices through the fidelity-verified book engine |
| `P4_power.py/.json` | Null precision, false-pass rate and power on synthetic worlds calibrated on the committed control-book statistics, run through the frozen Phase 3 selection pipeline |
| `P4_weekly_bars.py` + `tests/test_p4_weekly_bars.py` | The exact Weekly-bar rule and 6 leakage canaries |

## Summary and recommendation

**The architecture can be built safely, cheaply and without leakage:**
- 240 configurations;
- 12 positions;
- a trend-state exit;
- 1,000 fake worlds for the null;
- ≈ 2 hours of node time and $0 extra.

**But on the evidence available before any Weekly backtest, it has very little power to find a realistic edge.**

| Measure | Result |
|---|---|
| Selection edge over a random portfolio needed for even a 50% chance of passing the search gates | ≈ 6–8% a year |
| Same, for the whole pre-Holdout chain (with the one-shot 2018–2021 test) | ≈ 9–12% a year |
| Plausible edge for large-cap technical selection after costs and after publication (literature) | ≈ 0–3% a year |

**Its information families also overlap heavily with ideas that already failed here:** momentum (H002), 52-week high (H003), breakout (H006), residual strength (H008), and Phase 3's trend and momentum primaries.

**What is genuinely new is mechanical:** the state-based exit, longer holds, lower costs and momentum ranking. Those change risk and cost, not the underlying information.

**My recommendation: do not implement Phase 4 as a search for a production candidate.**
- The most likely outcome is again "No Production Candidate Found", at several days of engineering.
- The cloud cost would be $0, so the price is engineering time, not money.
- If the owner still wants the question closed definitively, the design below is ready to freeze (item 38).

---

## 1. Phase 3 is closed

- **H018 / Phase 3 Stage 1 is CLOSED: No Production Candidate Found** (D139). It is not reused and not rescued.
- **Phase 2** (H014, H016, H017): closed and rejected.
- **2018–2021:** unused by Phase 3.
- **Holdout** 2022-01-01 → 2026-08-31: locked.
- **No Weekly strategy has run.** Phase 3's results are used only as the methodological lesson (fake winners), never to choose Weekly parameters.

## 2. Phase 4 economic objective

Unchanged:
- **Goal:** same capital and dates; long-only, no leverage; terminal wealth above SPY total-return buy-and-hold after realistic costs.
- **Accounts:** $100K primary; $200K sensitivity.
- **Reported first for every final candidate:**
  - starting capital;
  - final strategy and SPY values;
  - total returns;
  - CAGRs and excess CAGR;
  - terminal-wealth ratio.
- **Risk statistics** are safeguards.

## 3. Why Weekly is (and is not) materially different from daily Phase 3

| | Phase 3 (H018) | Phase 4 proposal |
|---|---|---|
| Decision frequency | Daily | Weekly (last session of the week) |
| Exit | Fixed 63 sessions | **Trend-state invalidation**, no fixed horizon (holds of weeks to > 1 year) |
| Ranking | Each primary's own strength | **Relative strength** (26-week return, skipping 4 weeks), fixed |
| Slots | 10 | 12 (from mechanics, item 13) |
| Configurations | 1,533 | **240** |
| Costs | ≈ 1.05–1.1% a year | ≈ 0.35–1.25% a year, depending on how long trends persist |

**Genuinely different:**
- the exit and holding architecture ("let winners run" while the trend persists; the disposition-effect rationale, Frazzini 2006);
- lower turnover and costs;
- momentum ranking;
- a much smaller, literature-anchored space.

**Not different:**
- **the information.** A weekly close is a daily close, so weekly sampling adds no information; it only makes decisions slower.
- Close > MA, MA crosses, K-month returns and 52-week-high proximity were all in Phase 3's grammar, and momentum, 52-week-high, breakout and relative-strength hypotheses failed in Phase 1.

**The rationale is therefore "same information, different wrapper".** A full review is in `P4_literature_review.md`; questions A and J are answered below.

## 4. Exact Weekly-bar construction

Prototype `research/phase4/P4_weekly_bars.py`.

| Element | Rule |
|---|---|
| Week | ISO week (Monday–Sunday) of the exchange-local session date |
| Week end | The **last exchange session of the ISO week**, from the exchange calendar (holidays are published in advance; no price is needed to know it) |
| Holiday-shortened weeks | The same rule: the bar ends at the week's last session (e.g. Thursday before Good Friday). Fewer sessions; no padding |
| Open / High / Low / Close / Volume | First daily open; maximum daily high; minimum daily low; close of the stock's last daily bar of the week; sum of daily volumes |
| A stock without a bar on the last session | Close = its last daily bar within that week; the bar still completes at the week's last session |
| A week without any daily bar | No weekly bar; the series skips the week |
| Adjustment | Built from the point-in-time adjusted daily window (`SCALED_RAW`, rescaled on splits and dividends), as in Phases 2–3 |

## 5. Point-in-time and leakage timing rules

1. A weekly bar is usable **only after the close of the week's last session**. Partial weeks never produce a bar.
2. **Decision:** at that close. **Execution:** market-on-open at the **next exchange session** (normally Monday; Tuesday after a Monday holiday). Never at the decision close.
3. Universe eligibility (market cap, price, ADV) is the frozen daily point-in-time eligibility **at the decision session**.
4. Cross-sectional ranks (relative strength, volatility rank) use only stocks eligible at that session.
5. **Leakage canaries**, all passing (`tests/test_p4_weekly_bars.py`):
   - truncation invariance;
   - tampering with any data after the decision date changes nothing;
   - no partial week;
   - exact fields;
   - holiday-shortened weeks (Good Friday, Thanksgiving);
   - a missing last-day bar and an empty week;
   - the ISO-year boundary.
6. **The engine version would add in-LEAN canaries** (implementation stage): a weekly-close digest compared with an offline rebuild from the same daily windows; and the assertion `fill session > decision session` for every order.

## 6. Proposed Weekly indicator families

**Pool:** 8 families reviewed; 5 admitted, 3 excluded.

| Family | Admitted as | Evidence weight |
|---|---|---|
| Trend (weekly SMA position, SMA cross, time-series momentum sign) | **Primary** (entry + exit state) | Academic for asset classes; modest for stocks |
| Momentum / relative strength (26-week return, skip 4) | **Ranking (fixed)** and a confirmation | Academic (Jegadeesh & Titman; Novy-Marx); weaker in large caps |
| 52-week-high proximity (range position) | Confirmation | Academic (George & Hwang) |
| Trend strength (Wilder ADX) | Confirmation | Practitioner only |
| Momentum oscillators (RSI(14w) high; MACD histogram > 0) | One confirmation group | Practitioner only |
| Volatility (26-week realised-volatility rank) | Risk filter | Academic (low-volatility); H005 failed here |
| Volume / participation | **Excluded** | Sign ambiguous for momentum (Lee & Swaminathan) |
| Breakout as a primary; ATR%; Bollinger width; EMA variants; MACD line | **Excluded** | Duplicates of admitted families |

## 7. Redundancy grouping

**Information groups** (a strategy may use at most one condition per group, and the confirmation must come from a different group than the primary):

| Group | Contents | Role |
|---|---|---|
| **Direction / trend persistence** | Close > SMA(L), SMA(S) > SMA(L), K-week return > 0. Also, by construction: MACD line > 0 (≡ EMA cross) and RSI > 50 | Primary only |
| Relative strength | Cross-sectional rank of the 26-week return | Confirmation / ranking |
| Range position | Close vs 52-week high | Confirmation |
| Trend strength | ADX | Confirmation |
| Oscillator / acceleration | RSI ≥ 50 or 60; MACD histogram > 0 | Confirmation |
| Volatility | Realised-volatility rank | Risk filter |

**"Close > MA, MACD > 0, positive momentum and RSI > 50" are one group, never four confirmations.**

## 8. Exact proposed strategy grammar

`P4_search_space.py`:

```
Strategy := Primary trend state (exactly 1, direction group)  — defines entry AND exit
           AND Confirmation (0 or 1, from a different group)  — entry only
           AND Volatility filter (0 or 1)                     — entry only
Ranking  := 26-week return skipping the latest 4 weeks, highest first; ties by security id (fixed, not searched)
```

**At most 3 conditions / 3 information groups per strategy.**

## 9. Exact proposed entry architecture

At each Weekly decision session (the close of the week's last session):
1. **Exits first** (item 10).
2. **Free slots** = 12 − (held + pending, with exiting positions still counted until they fill).
3. **Candidates:** eligible stocks, not held or pending, that satisfy primary AND confirmation AND risk filter on completed weekly bars.
4. **Ranking and fill:** rank by relative strength and fill the free slots in rank order.
5. **Sizing:** the fidelity-verified harness sizing (D051): target 0.98/N, settled cash, 2% buffer, 15% gap reserve, $4,000 minimum, $7 per order, 10 bps slippage.
6. **No queue:** an unfilled candidate is simply re-evaluated next week.
7. **Execution:** next session's open.
8. **No daily indicators** are added after a Weekly setup fires.

## 10. Exact proposed exit architecture

**Stage A (the only stage proposed for the search):**
- A position is held while its **primary trend state** remains true at each weekly close.
- At the first weekly close where it is false, a sell fills at the next session's open.
- Confirmation and risk filter apply **at entry only**, so winners are not cut when, e.g., RSI cools or volatility rises.
- **Forced exits:** delistings and the stale-data rule (as before).
- **No fixed horizon, no stop-loss, no profit target.**

**Stage B (exit refinement): not proposed.**
- Phase 3's lesson and the power study (item 26) argue against adding degrees of freedom.
- If the owner wants Stage B, it must be pre-declared now: at most 2 alternatives (e.g. exit on a 2-week confirmation), applied only to a promoted cluster, kept only if better by more than one standard error.

## 11. Variable holding periods

| Situation | Rule |
|---|---|
| Positions of different lengths | Each slot is independent: a slot is freed when its exit fills and refilled at the **next** weekly decision (one-week slot lag; measured in item 13) |
| Entry clustering (many signals at once, e.g. after a market low) | Capped by free slots and ranking; there is no catch-up later |
| Signal scarcity (bear markets) | Slots stay empty and the book holds cash. **This implicit market-timing effect** is reported (exposure series) and controlled: the duration-matched random twins of item 27 have **exactly** the same exposure, so it cannot be mistaken for stock-selection skill |
| Re-entry after an exit | Allowed at any later weekly decision if all entry conditions hold again (no cooling-off) |
| Gate: minimum invested share | Average invested share ≥ 50% over the training window. This is a **stock-selection** study; a configuration mostly in cash is a timing rule (owner item 29) |
| Gate: minimum activity | At least 24 entries (2 × N) in training, so that selection evidence exists |

## 12. Proposed ranking rule

**26-week return ending 4 weeks before the decision** (relative strength with the conventional skip of the most recent month; Jegadeesh & Titman; Novy-Marx), highest first; ties by security id.
- It is the economic hypothesis itself: "buy the strongest stocks among those in confirmed uptrends".
- It is **not a search axis**.

## 13. Mechanical portfolio-size study

`P4_mechanics.py`: synthetic prices and synthetic holding durations through the fidelity-verified book engine, with the exact D051 rules; **no returns used**. Results at $100K:

| N | Target position | Mechanics at 13-week holds | Mechanics at 26–52-week holds | Selection tracking error vs EW (train / OOS) |
|---|---|---|---|---|
| 10 | $9,800 | Works; 87% invested | 90–91% invested | 7.4% / 10.3% |
| **12** | **$8,167** | **Works; 88% invested; no skipped buys** | **90–91% invested** | **6.7% / 9.4%** |
| 15 | $6,533 | **Degrades:** 43 buys a year skipped by the $4,000 minimum after gap-reserve scaling; 83% invested | 91% invested | 6.0% / 8.4% |
| 20 | $4,900 | **Breaks:** most buys skipped; 17–23% invested (13–15% at 8-week holds) | 45–82% invested | 5.2% / 7.3% |

**Why 15 and 20 fail at $100K:**
- When the book is fully invested, a freed slot only funds the next buy net of the 2% buffer and the 15% gap reserve.
- The scaled buy then falls below the $4,000 minimum and is skipped.
- At $200K, 15 and 20 work.

**A built-in drag:** even at its best, the book is ≈ 90% invested. That is the cash buffer, gap-reserve scaling and the one-week slot lag, worth roughly 1% a year against SPY in a rising market.

## 14. Proposed primary position count

**N = 12.**
- It is the largest count whose mechanics hold in every turnover scenario at $100K: no skipped buys, positions ≈ $8.2K, costs within the cap except under heavy whipsaw.
- It is more diversified than 10 (tracking error −9%).
- The owner's intuition of 15 is mechanically sound only if trends persist for ≥ 26 weeks on average. That is unknown before data, so 15 is not adopted.
- **$200K sensitivity:** N = 12 as well (the same rule), reported only.

## 15. Expected turnover

Unknown until trend persistence is observed. The design therefore uses scenarios and an implementation-stage check.

| Mean hold | Buys a year (N = 12) | +30% whipsaw entries |
|---|---|---|
| 8 weeks | 69 | 88 |
| 13 weeks | 44 | 60 |
| 26 weeks | 24 | 33 |
| 52 weeks | 12 | 18 |

**Implementation-stage check (proposed):** a **feature-only turnover canary**.
- It measures the distribution of primary-state durations on 2010–2017 **without any returns**.
- It verifies that the space is cost-feasible before the null runs.
- Any configuration exceeding the cost cap fails its gate anyway.

## 16. Expected annual costs

N = 12, $100K, measured in the mechanical simulation:

| Mean hold | Cost a year | With 30% whipsaw | Invested share |
|---|---|---|---|
| 8 weeks | 2.04% (above the cap) | 2.59% | 84% / 81% |
| 13 weeks | 1.24% | 1.74% (above the cap) | 88% / 85% |
| 26 weeks | 0.68% | 0.91% | 90% / 89% |
| 52 weeks | 0.34% | 0.49% | 91% / 91% |

- **Cost gate:** realised cost ≤ 1.5% a year (R4).
- **Structurally too expensive:** primaries whose state flips faster than ≈ 10–13 weeks. Daily evaluation (Phase 3, 63-session holds) cost ≈ 1.1%.

## 17. Proposed parameter grids

Coarse, conventional time scales. Fixed before any data.

| Component | Values | Rationale |
|---|---|---|
| WP1 close > SMA(L) | L ∈ {20, 30, 40} weeks | ≈ 100 / 150 / 200 days; Weinstein's 30-week; Faber's ≈ 43-week |
| WP2 SMA(S) > SMA(L) | (S, L) ∈ {(10, 30), (13, 40), (17, 52)} | Ratio ≈ 1:3, the 50/150 and 50/200-day convention; quarter / half-year / year |
| WP3 K-week return > 0 | K ∈ {26, 52} | 6 / 12-month time-series momentum |
| CRS relative strength top q | q ∈ {20%, 40%} | Quintile / two-quintile |
| CHI close ≥ (1 − x) × 52-week high | x ∈ {5%, 15%} | Near / moderately below the high |
| CADX ADX(14w) ≥ a | a ∈ {20, 25} | Wilder's conventional trend thresholds |
| CRSI RSI(14w) ≥ r | r ∈ {50, 60} | Bull-range convention |
| CMH MACD(12, 26, 9) histogram > 0 | — | Conventional parameters only |
| Risk: 26-week realised-volatility rank | none / ≤ 80% / ≤ 50% | As in Phase 3 |

## 18. Exact configuration count

**240.**
- 8 primary variants × (1 + 9 confirmations) × 3 risk levels.
- By primary type: WP1 90, WP2 90, WP3 60.
- **Comparison:** free AND combinations of the same 19 conditions: 1,159 up to 3 conditions, 169,765 up to 8.
- **Neighbour graph:** every configuration has 2–5 neighbours; 406 edges; the largest connected component has 18 configurations.

## 19. Plateau definition

The Phase 3 rule, unchanged:

| Element | Rule |
|---|---|
| Neighbour | One grid step on one axis (primary axis within the same type; confirmation axis within the same type; the risk axis) |
| Plateau score PS | The 25th percentile of the score over the configuration and its neighbours (every neighbour, eligible or not); boundaries are not padded |
| Survivors | Eligible configurations with PS > τ |
| Clusters | Connected survivor components of **≥ 3** |
| Centre | Interior survivor with the highest PS (else most in-cluster neighbours, then PS, then id) |
| Statistic T | The plateau level of the best connected cluster of ≥ 3 |

**A spectacular isolated configuration cannot pass:** its neighbours pull its PS down, and it is not a cluster.

## 20. Simplicity rule

The Phase 3 one-standard-error lexicographic rule:
- among clusters whose centre PS ≥ PS* − SE* (SE* = 1.2533 × sd(folds) / √folds);
- choose the fewest conditions, then the fewest parameters, then the lowest turnover, then the highest PS, then the id.

## 21. Search score and promotion framework

**Hierarchical gates, no weights.**
1. **Gates:**
   - cost ≤ 1.5% a year;
   - max drawdown ≥ SPY − 10 points;
   - ≥ ceil(0.75 × folds) positive two-year folds vs SPY;
   - invested share ≥ 50%;
   - ≥ 24 entries.
2. **Score:** the median over folds of the annualised log excess over SPY (equivalent to the terminal-wealth ratio).
3. **Selection:** plateau (19), then simplicity (20).
4. **Q1:** search-null gate (24).
5. **Q2:** walk-forward (25).
6. **Q3:** LEAN verification of finalists.
7. **Q4:** one-shot internal OOS (31).
8. **Holdout** (32).

## 22. Null-world construction

**Tethered within-week permutation.** Adapted to state-based exits.
- **At each weekly decision:** a seeded permutation maps each eligible stock's **signal row** to a traded stock.
- **A new position is tethered** to the signal row that triggered it: it **stays open while that signal row's primary state stays true** and closes when it turns false.
- **Preserved exactly:** the real holding-duration distribution, the weekly entry counts, exposure (cash), turnover, costs, every corporate action, universe changes, real returns, regimes and cross-sectional correlation.
- **Broken:** only the link between a stock's technical signal and **its own** future return, during both selection and holding.
- **The entire optimizer runs in every fake world** (gates, plateau, clusters, T, simplicity, walk-forward).
- **Secondary diagnostic:** the same with 13-week blocks (200 worlds).

## 23. Number of null repetitions

**R = 1,000** (Phase 3 used 500). The smaller space makes each world ≈ 6× cheaper.

| Measure | R = 1,000 | R = 500 |
|---|---|---|
| 95% interval of the threshold quantile | 0.937–0.964 | 0.928–0.968 |
| Typical 95% CI for a true 1% false-pass rate | 0.48%–1.83% | — |
| Upper CI bound with zero passes | 0.37% | — |

## 24. Null-threshold procedure

As in Phase 3 (D137), stricter on ordering:
1. Run the 1,000 primary and 200 block null worlds.
2. Compute **τ = the 50th largest of 1,000 null T values** (m = floor(0.05 × 1,001)), together with the stage counts and the false-pass rate with its CI.
3. **Commit, hash-pin (code constant + test) and push**, with a clean tree.
4. **Only then** start the real run, which must be launched from that commit.

**τ is immutable for Phase 4.**

## 25. Training / walk-forward / internal-OOS split

**Two architectures were compared** with the power model (item 26):

| | **A: Phase 3 pattern (recommended if implemented)** | B: expanding walk-forward through 2021 |
|---|---|---|
| Search window | 2010-03 → 2017-12 (4 folds) | 2010-03 → 2021-12 (6 folds) |
| Walk-forward | 2014–2017 (past only, procedure re-run yearly) | 2014–2021 (8 yearly tests, g/SE ≥ 1) |
| Internal OOS | 2018–2021, **one-shot**, one candidate | None (2018–2021 is used by the walk-forward) |
| Full-chain false pass (no edge) | **0–0.1%** (CI upper ≤ 0.56%) | **0.8–1.3%** |
| Edge for 50% power, full pre-Holdout chain | 11.7% / yr (base); > 12% (high correlation) | 8.8% / yr (base); 7.7–10.1% |

- **Recommendation:** A.
  - B is somewhat more powerful because its walk-forward has 8 test years.
  - But B spends 2018–2021 on the procedure (several picks see it), contrary to the one-shot rule (owner item 21).
  - B also leaves the Holdout as the only independent confirmation.
  - **Neither changes the verdict:** both need edges far above plausible ones.
- **Weekly scarcity:** what limits power is calendar time and tracking error, not the number of weekly bars. The standard error of a mean annual excess depends on years, not sampling frequency. 600 weekly bars and 3,000 daily bars carry the same information about a slow edge.

## 26. Weekly statistical-power analysis

`P4_power.py`: 1,000 null worlds and 300 worlds per edge per scenario.
- **Calibration:** on the committed control-book statistics (random books vs EW and SPY). Selection tracking error for 12 slots: 6.7% (training) and 9.4% (OOS); EW − SPY drift and volatility from the controls; mechanical drag of a slot book.
- **Pipeline:** the frozen Phase 3 selection pipeline on the proposed 240-configuration graph.
- **Planted edge:** a true selection edge on one 18-configuration region.
- **Correlation scenarios** across configurations: low / base / high.

**Architecture A:**

| True selection edge a year (vs a random book) | 2% | 4% | 6% | 8% | 10% | 12% |
|---|---|---|---|---|---|---|
| Q1 detects and selects it (base) | 1% | 12% | 41% | 68% | 95% | 97% |
| + walk-forward (Q2) | 1% | 9% | 30% | 58% | 89% | 96% |
| + one-shot internal OOS (full pre-Holdout chain) | 0.3% | 1% | 7% | 17% | 34% | 53% |

**Edge needed, by scenario:**

| Edge needed | Search gates (Q1 + Q2) | Full pre-Holdout chain |
|---|---|---|
| For 50% power | 6.0–8.4% / yr | 11.7% (base, low); > 12% (high correlation) |
| For 80% power | 8.1–11.2% / yr | Not reached within 12% |

- **False pass with no edge:** search stage 2.1–2.9%; full chain 0–0.1%.
- **Interpretation:**
  - Only selection edges of roughly **≥ 6–8% a year** have even an even chance at the search stage.
  - **≈ 12% a year** is needed through the one-shot OOS, which carries the ≥ $2B universe's 2018–2021 headwind against SPY (−4.1% a year in the controls) and higher tracking error.
  - The literature suggests large-cap technical selection edges of ≈ 0–3% a year. **The architecture has effectively no power for plausible edges** (owner item 31).
- **Rough "vs SPY" translation:** an 8% selection edge means beating a random book by 8% a year; a random 12-slot book trailed SPY by ≈ 2% a year in 2010–2017.

## 27. Random control design

| Control | Definition |
|---|---|
| **SPY** | Total-return buy-and-hold (the objective) |
| **Same-universe EW** | The universe effect |
| **Duration-matched random twins** (seeds 1–5) | When the candidate opens k positions at a weekly decision, the twin opens k random eligible stocks at the same session. Each twin position is held for **exactly the same number of weeks** as the candidate position it mirrors. Same slots, costs, cash rules and exposure path; **only the stock identity is random**. W3: beat the median twin |

**Twins are never averaged into a synthetic portfolio** (D104).

## 28. Search-null design

**Separate from the random controls, as the owner asked:**
- **Twins** answer: "does the final rule pick better stocks than random picking with identical timing?"
- **The full search null** (item 22) answers: "could the whole Weekly optimizer find something this impressive from noise?"
- **Both are required.** Only the null decides Q1.

## 29. Candidate-promotion pipeline

```
240 configurations (2010-03 → 2017-12) ─ gates ─▶ eligible
  ▶ plateau survivors (PS > τ) ─▶ clusters (≥ 3) ─▶ Q1: T > τ (1,000-world null)
  ▶ ≤ 3 clusters ranked (simplicity rule)
  ▶ Q2: procedure walk-forward 2014–2017
  ▶ ≤ 2 finalists ─▶ Q3: full LEAN harness reproduction (same tolerance file as Phase 3)
  ▶ exactly 1 candidate ─▶ Q4: one-shot internal OOS 2018–2021 (W1, W3 vs EW and twins, R1, R2, R4,
                                g/SE ≥ 1, W1 at 2× slippage)
  ▶ STOP ─▶ owner ─▶ Holdout (HO-W, HO-R)
```

## 30. Maximum candidates at each stage

| Stage | Maximum |
|---|---|
| Configurations | 240 |
| Ranked clusters | ≤ 3 (rank 3 reported only) |
| LEAN finalists | ≤ 2 |
| Internal-OOS candidate | Exactly 1 |
| Holdout candidate | Exactly 1 |
| Search rounds | **One**; no second round, no added parameters, no Stage B unless pre-declared now |

## 31. Internal-OOS one-shot rule

- 2018–2021 is exposed to **exactly one** frozen candidate, once, after Q1–Q3, and only with explicit owner approval.
- If it fails, Phase 4 validation fails. No "candidate A failed, try B".

## 32. Holdout request criteria

All of the following must be complete before any Holdout request:
- Q1–Q4 passed;
- the candidate frozen and hash-pinned;
- written owner approval in `HOLDOUT_UNLOCK.md`.

**Then:**
- **One run set:** the candidate, EW, five twins and SPY, over 2022-01-01 → 2026-08-31.
- **Gates:**
  - **HO-W:** CAGR > SPY;
  - **HO-R:** R1.
- **After the Holdout:** never modified.

## 33. QuantConnect / LEAN implementation architecture

**Adapt the fidelity-verified Phase 3 engine; do not rewrite it:**

```
daily PIT universe + adjusted daily windows (existing X984/S018 code, batch-independent subscriptions)
   ▶ deterministic Weekly aggregation at each week's last session (the P4_weekly_bars rule; weekly ring buffers)
   ▶ Weekly features (SMA, returns, RSI, ADX, MACD, 52-week high, volatility rank) computed once per week
   ▶ 240 configuration masks + fixed relative-strength ranking
   ▶ Books engine (unchanged sizing / cash / costs) with state exits (the existing exits_due extra-flags hook)
     and a per-slot signal-row tether for the null
   ▶ the frozen pipeline (gates, plateau, T, walk-forward) in LEAN for every world
   ▶ full LEAN harness strategy for ≤ 2 finalists
```

**Fidelity before any search:**
- the existing control-book replay (the books engine is unchanged);
- a new Weekly replay test against a LEAN harness book with state exits;
- the weekly-bar digest canary;
- batch-independence digests;
- turnover and runtime canaries on dummy masks.

## 34. Estimated runtime and cost

| Item | Estimate |
|---|---|
| Per world | 240 books ≈ 1/6 of a Phase 3 world; ≈ 2 s of engine time |
| 1,000 primary null worlds | 4 runs × 250 worlds, ≈ 18 min each |
| 200 block-null worlds | 1 run |
| Real search | 1 run, ≈ 11 min |
| **Total node time** | **≈ 2 hours** |
| Memory | ≈ 4.5 GB (8 GB node) |
| QuantConnect cost | **$0 extra** |
| Engineering before any search | ≈ 2–4 working days: weekly aggregation, state exits, tether, twins, fidelity and canaries, frozen spec |

## 35. Main methodological risks

1. **Power (decisive):** detection needs ≈ 6–12% a year of true selection edge (item 26); plausible edges are ≈ 0–3%.
2. **Same information, different wrapper:** the families overlap with failed Phases 1–3 ideas. A positive result would need to come from the exit architecture alone.
3. **Implicit market timing:** trend-state exits move the book into cash in downtrends. In 2010–2017 (a rising market) that is a drag; in the 2018–2021 OOS it may help or hurt. The twins isolate it, but W1 vs SPY includes it.
4. **Long holds reduce independent bets:** each configuration's excess becomes more persistent (more autocorrelated), which lowers effective sample size and power.
5. **Momentum is weakest in large caps** and decays after publication.
6. **Long-run reversal** after ~12 months may give back gains of very long holds.
7. **Whipsaw costs** in sideways markets for short MA lengths.
8. **Mechanical cash drag:** the book is ≈ 90% invested under D051.
9. **Knowledge contamination:** 2010–2021 has been studied in Phases 1–3. 2018–2021 is procedurally unused by Phase 3, but not knowledge-pristine.
10. **The temptation to rescue after results:** blocked by one round, the frozen spec, and the threshold committed before the real run.

## 36. Comparison with Weekly market / sector rotation (context only)

| | A. Weekly stock selection (this proposal) | B. Weekly market / sector rotation |
|---|---|---|
| Question | Do weekly technical states pick stocks that beat SPY? | Do weekly trend states time exposure or rotate sectors well enough to beat SPY? |
| Evidence | Modest; weakest in large caps | Stronger for drawdown reduction (Faber; Zakamulin), weak for terminal wealth above buy-and-hold in rising markets |
| Independent bets | Many stocks, but correlated | Few series: **even lower power** |
| Fit with scope | Inside the current universe rules | Needs ETFs (outside "US common stocks"): a scope change |

**Only A is proposed for Phase 4.** B would be a separate phase with its own scope decision.

## 37. Recommendation

**Not worth implementing as a search for a production candidate** (question J).
- It can be done cleanly and cheaply. But the pre-data power analysis shows it cannot detect the edges the evidence makes plausible.
- Its information overlaps with families that have already failed here.
- **Expected outcome:** No Production Candidate Found.

**If the owner nevertheless wants Phase 4** (e.g. to test the trend-exit / let-winners-run architecture definitively, at $0 cloud cost and ≈ 2–4 days of engineering), the design above is complete and can be frozen:
- architecture A;
- N = 12;
- 240 configurations;
- 1,000 null worlds;
- duration-matched twins.

## 38. Exact owner decisions required next

1. **Go / no-go:** proceed to implementation (engine + fidelity + canaries only, as in Phase 3), or do not open Phase 4.
2. **If go**, approve or amend:
   - the grammar and grids (items 8, 17; 240 configurations);
   - the trend-state exit with **no Stage B** (or pre-declare at most 2 Stage-B alternatives now);
   - fixed relative-strength ranking;
   - N = 12;
   - the invested-share and activity gates.
3. **Partition:** A (recommended) or B.
4. **Null:** tethered within-week permutation, R = 1,000, τ = the 50th largest; block-null diagnostic (200 worlds).
5. **Feature-only turnover canary** (state durations, no returns) before the null runs.
6. **Acknowledge the power analysis:** the expected outcome is "No Production Candidate Found".

**STOP.**
- No Weekly implementation, returns, configurations, candidates, 2018–2021 evaluation, Holdout access, purchase or search run.
- Waiting for owner approval.

---

## Answers to the owner's questions

| # | Question | Answer |
|---|---|---|
| **A** | Different rationale from daily Phase 3? | **Partly.** The exit and holding architecture (trend-state exit, letting winners run, lower costs, momentum ranking) is genuinely different. The **information** is not: weekly bars are a subset of daily bars, and the families overlap with failed Phase 1–3 ideas |
| **B** | Which 2–3 families per strategy? | **Direction / trend** as primary (it also defines the exit) + **relative strength or 52-week-high proximity** as confirmation + an optional **volatility** filter. Ranking by relative strength. ADX and RSI / MACD are admitted as one weak-evidence confirmation group each, not stacked |
| **C** | Ranges? | Item 17: 20/30/40-week MA; 10/30, 13/40, 17/52 crosses; 26/52-week momentum; top 20/40% RS; 5/15% from the high; ADX 20/25; RSI 50/60; MACD conventional. Conventional time scales, 2–3 values each |
| **D** | Exit by trend invalidation? | **Yes**, primary-state invalidation at a weekly close, with no fixed horizon. That is the hypothesis being tested |
| **E** | Position count at $100K? | **12.** 15 and 20 break the existing cash / minimum-size mechanics at $100K unless trends persist ≥ 26 weeks |
| **F** | How many configurations? | **≈ 240.** Power is limited by calendar time, not by the count. Fewer, coarser configurations lower the null threshold modestly; more would raise it |
| **G** | Null for Weekly? | **Tethered within-week permutation.** Each new position follows its signal row's state, preserving holding durations, exposure and turnover. R = 1,000 |
| **H** | Detectable edge? | ≈ 6–8% / yr over a random book to pass the search gates with 50% probability; ≈ 12% / yr through the one-shot OOS. Not plausible for large-cap technical selection |
| **I** | Keep 2010–2017 / 2018–2021? | **Yes (A).** B (expanding walk-forward through 2021) is a little more powerful but spends the one-shot OOS and raises false passes. The split choice does not change the verdict |
| **J** | Worth building? | **Not as a candidate search.** Only if the owner wants a definitive, low-cost test of the trend-exit architecture, accepting a very likely negative result |
