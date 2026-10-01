# Phase 2 development checkpoint (P2-CP1): H014 trend + pullback + recovery

- **Date:** 2026-10-01.
- **Data used:** 2010-01-04 → 2021-12-31 only (development).
- **Untouched:** the 2022–2026 Holdout, everything after 2026-08-31, and any forward data.
- **Status: STOP.** No candidate qualifies; nothing is requested.

## Result in one paragraph

**H014 does not qualify for the Holdout.**

- The frozen selection rule chose **Candidate A** (63-session exit). Candidate B was better than A in 2016–2021 but worse in 2010–2015, so it could not replace A.
- Candidate A is **profitable**: 12.1% a year net of costs. It is **not benchmark-beating**: Sharpe 0.64 against equal-weight 0.80 and SPY 0.91.
- A is **not control-beating**. It beats the trend-only and pullback-without-recovery controls, but not the random-uptrend control.
- A is **not consistent**: it beats equal-weight in only 1 of 6 two-year blocks.
- So it fails G1, G2 and G3. Under the pre-declared procedure, the robustness runs were therefore not made, and G4 fails as "not run".
- The non-chosen Candidate B also fails G1, G2 and G3. B is shown for information only and could not have qualified.

The most informative finding is in the controls. **Picking uptrend stocks at random beat both H014 and the momentum-ranked trend-only book.** So whatever value exists here comes from the trend filter plus diversification, not from the pullback/recovery timing or the momentum ranking.

## What was run (all registered in `experiments/INDEX.csv`)

| Group | Runs | Notes |
|---|---|---|
| Canaries (infrastructure) | E965-01 (bugged, D096), E965-04, E965-02, E965-03 + 1 reproduction | All pass (D097, D098) |
| Diagnostics (infrastructure) | E966-01 (bugged diagnostic), E966-02 | Dividend-factor diagnosis (D097) |
| Candidates (research) | E014-01 (A), E014-02 (B) | 2 Phase 2 selection trials |
| Controls (benchmark kind) | E014-03 … E014-12 | C1, C2, R seeds 1–3, for each exit |
| $200K sensitivity | E014-13 → never started (QC disk error, D099), repeat E014-24; E014-14 → never started (same error), repeat E014-25 | Diagnostic only |
| Conditional robustness | E014-15 … E014-23 | **Not run:** the §9 trigger (G1, G2 and G3 all pass) was not met |

**Totals.**
- Phase 2 has 1 hypothesis (H014), 1 strategy (S014) and 2 selection trials.
- There are 0 robustness configurations.
- The cumulative count across both programmes is 42 selection candidates (conservative count 75).

## 1–5. Performance of every book (2010–2021, $100K, net of $7/order and 10 bps slippage)

| Book | Sharpe | CAGR | Max DD | Calmar |
|---|---|---|---|---|
| **H014 A (chosen)** E014-01 | **0.64** | **12.1%** | −36.9% | 0.33 |
| H014 B E014-02 | 0.72 | 14.8% | −39.2% | 0.38 |
| Equal-weight universe (EW) | 0.80 | 13.5% | −37.7% | 0.36 |
| SPY | 0.91 | 14.6% | −33.1% | 0.44 |
| C1 trend-only, exit A | 0.59 | 14.3% | −44.8% | 0.32 |
| C2 pullback without recovery, exit A | 0.61 | 13.2% | −36.0% | 0.37 |
| R random uptrend, exit A, seeds 1/2/3 | 0.68 / 1.00 / 0.73 | 10.4 / 19.7 / 11.8% | −28.0 / −29.9 / −32.4% | 0.37 / 0.66 / 0.37 |
| C1 trend-only, exit B | 0.38 | 7.3% | −53.1% | 0.14 |
| C2 pullback without recovery, exit B | 0.62 | 14.3% | −39.6% | 0.36 |
| R random uptrend, exit B, seeds 1/2/3 | 0.81 / 0.84 / 0.93 | 12.4 / 14.5 / 15.3% | −28.5 / −30.0 / −25.5% | 0.44 / 0.48 / 0.60 |

**Per-year returns, H014 A vs EW**

| Year | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H014 A | 32.8% | 6.3% | 12.1% | 33.8% | 7.7% | −0.5% | 13.4% | 20.4% | −14.8% | 27.2% | 2.0% | 14.6% |
| EW | 22.1% | −0.2% | 16.8% | 35.4% | 10.6% | −2.2% | 14.5% | 18.7% | −8.4% | 27.3% | 18.5% | 16.4% |

H014 A trailed EW by 16.5 points in 2020. The pullback entries kept it out of much of the post-crash rebound.

## 16. Candidate selection (frozen rule, spec §7)

Metric: D = Sharpe(candidate) − Sharpe(EW) within each half. B replaces A only if B's D is higher in both halves.

| Half | D for A | D for B | B better? |
|---|---|---|---|
| 2010–2015 | −0.03 | −0.07 | No |
| 2016–2021 | −0.27 | −0.08 | Yes |

**Chosen: Candidate A (E014-01).**
- B's better full-period figure plays no role, by rule.
- Both candidates fail anyway (below).

## 6. G1: practical superiority (all four must hold)

| Item | Requirement | Candidate A | Pass? |
|---|---|---|---|
| G1.1 | Sharpe ≥ EW + 0.25 and ≥ SPY + 0.10 | **−0.16** vs EW; **−0.26** vs SPY | **No** |
| G1.2 | CAGR ≥ EW − 2 pts | 12.1% vs 13.5% | Yes |
| G1.3 | Calmar ≥ EW | 0.33 vs 0.36 | **No** |
| G1.4 | Drawdown ≤ 5 pts deeper than EW | −36.9% vs −37.7% | Yes |

**G1 fails.** (B: −0.08 vs EW and −0.18 vs SPY. It also fails G1.1.)

## 7. G2: beating the controls (same exit A)

| Control | Sharpe | H014 A (0.64) better? |
|---|---|---|
| C1 trend-only | 0.59 | Yes |
| C2 pullback without recovery | 0.61 | Yes |
| Median random-uptrend seed | 0.73 | **No** |

**G2 fails.** (B, exit-B controls: it beats C1 at 0.38 and C2 at 0.62, but not the median random seed at 0.84.)

## 8. G3: consistency over six two-year blocks

| Block | 2010–11 | 2012–13 | 2014–15 | 2016–17 | 2018–19 | 2020–21 |
|---|---|---|---|---|---|---|
| Sharpe(A) − Sharpe(EW) | +0.29 | −0.44 | −0.09 | −0.29 | −0.30 | −0.32 |

- A beats EW in **1 of 6** blocks; 4 are required.
- Its total excess return over EW is negative, so the "no block above half" test cannot pass either.

**G3 fails.**

## 9. G4: robustness and costs

| Item | Result |
|---|---|
| (a) ≥ 5 of 6 perturbations keep ≥ EW + 0.10 | **Not run.** Pre-declared trigger: only if G1–G3 pass (spec §9). Counts as a fail. |
| (b) 2× slippage keeps ≥ EW + 0.10 | **Not run** (same rule). Counts as a fail. Base Sharpe is already below EW. |
| (c) Realised costs ≤ 1.5% a year | **1.46%** for A. Passes, narrowly. |

**G4 fails.**

## 10–11. Costs, turnover, exposure and cash: how comparable the books are

| Book | Costs a year | Turnover a year | Orders | Invested | Mean cash | Min cash | Slot use | Mean hold (sessions) |
|---|---|---|---|---|---|---|---|---|
| H014 A | 1.46% | 10.6× | 1,646 | 92.2% | 7.8% | 2.1% | 96.6% | 43 |
| H014 B | 0.92% | 6.8× | 1,106 | 93.1% | 6.9% | 2.0% | 97.5% | 64 |
| C1 A | 0.54% | 3.8× | 732 | 94.3% | 5.7% | 1.8% | 98.3% | 98 |
| C2 A | 1.56% | 11.3× | 1,798 | 92.2% | 7.8% | 2.3% | 96.8% | 39 |
| R A (mean of 3) | 0.57% | 4.0× | 689 | 94.4% | 5.6% | ~2.4% | 98.4% | 103 |
| C1 B | 0.89% | 5.9× | 986 | 92.8% | 7.2% | 0.4% | 98.0% | 72 |
| C2 B | 1.09% | 7.9× | 1,330 | 92.9% | 7.1% | 2.1% | 97.5% | 53 |
| R B (mean of 3) | 0.88% | 6.3× | 1,005 | 93.6% | 6.4% | ~2.5% | 98.0% | 70 |

**Reading.**
- All books are almost fully invested (92–95%) and use 97–98% of their 12 slots. Cash rarely falls below the 2% buffer.
- So the differences in results are **not** explained by holding more cash or fewer positions.
- The main structural difference is **turnover**:
  - H014 A trades about 2.7× as much as the trend-only and random books, and holds positions less than half as long.
  - That costs about 0.9 points a year more.
- Under exit A, the trend-only and random books hold much longer because of the horizon roll. Their stocks usually still qualify at day 63, so they are kept.
- The extra costs do not explain the shortfall. Adding back about 0.9 points a year (roughly +0.05 Sharpe) would still leave H014 A below the median random book (0.73).

**H014 A's exits.**
- 442 exits were Close < MA200 and 365 were time exits; there were 14 horizon rolls.
- Mean holding was 43 sessions. 10% of trades lasted 4 sessions or less: whipsaw exits soon after entry.

**Trades.**
- 817 closed trades; 43% won.
- Profit factor 1.30; expectancy +2.5% per trade.
- Profits are very concentrated: the top 5% of trades contributed 177% of total net profit, so the rest lost money in aggregate.

## 12. $200K sensitivity (12 slots; never used for selection)

| Candidate | $100K Sharpe | $200K Sharpe | Costs at $100K → $200K |
|---|---|---|---|
| A | 0.64 | 0.65 | 1.46% → 1.26% |
| B | 0.72 | 0.73 | 0.92% → 0.80% |

A larger account lowers costs a little but does not change any conclusion.

## 13. DSR diagnostics (never a gate)

This is the probability that the true Sharpe exceeds what the best of N no-skill attempts would show by luck.

| Count | N | Luck hurdle (Sharpe) | DSR for A |
|---|---|---|---|
| Phase 2 candidates | 2 | 0.25 | 0.91 |
| Phase 2 broad (+ robustness configs; none run) | 2 | 0.25 | 0.91 |
| Cumulative with programme 1 | 42 | 1.08 | **0.07 (warning)** |

- The high Phase 2 values only say that A's returns are very probably positive: PSR(0) = 0.99, consistent with "profitable".
- They say nothing about beating EW.
- Across the 42 ideas tried since C01, A's Sharpe of 0.64 is far below the luck hurdle.

## 14. PBO diagnostics (never a gate)

- PBO over the two candidates (CSCV, 16 blocks) is 0.69. The candidate that looks better in one half of the data tends to rank lower in the other, consistent with the selection table above.
- With only two candidates, this number carries little information.
- The perturbation PBO was not computed, because the robustness runs were not triggered.

## 15. Does the pullback/recovery mechanism add value beyond the trend filter?

**Only weakly against the momentum-ranked controls, and not at all against random selection.**

**Paired block-bootstrap of the Sharpe difference** (mean block 63 days, 2,000 draws):

| A minus … | Difference | 95% interval | Share of draws ≤ 0 |
|---|---|---|---|
| EW | −0.16 | −0.54 to +0.15 | 84% |
| SPY | −0.26 | −0.65 to +0.05 | 95% |
| C1 trend-only | +0.05 | −0.30 to +0.41 | 36% |
| C2 pullback without recovery | +0.04 | −0.25 to +0.32 | 40% |
| R seed 1 / 2 / 3 | −0.03 / −0.36 / −0.09 | all intervals include 0 | 58% / 95% / 68% |

**By block, A minus trend-only:** +0.42, +0.13, −0.30, +0.20, −0.10, −0.07.
- It is positive early (2010–2013, 2016–17) and negative since 2018.
- The small advantage over C1 and C2 is not statistically distinguishable from zero.

**What the controls reveal:**
- The trend-only book (top 12-1 momentum) is the **worst** exit-A book and trails EW in 5 of 6 blocks.
- Random choices from the **same** uptrend list do better.
- Within this ≥ $2B universe over 2010–2021, ranking by strongest momentum hurt. The recovery entry partly offsets this (A > C1), but not enough to beat random.

**Stress episodes (total return over each window):**

| Episode | H014 A | EW | Trend-only |
|---|---|---|---|
| 2011 downgrade | −19.6% | −20.7% | −26.0% |
| 2015–16 sell-off | −23.3% | −17.6% | −37.9% |
| 2018 Q4 | −24.6% | −20.6% | −28.7% |
| 2020 crash | −33.5% | −37.3% | −35.1% |
| 2020 recovery (Mar–Aug) | +41.2% | +54.6% | +82.2% |

## 17. Does any candidate qualify to request Holdout access?

**No.**

| Classification | Candidate A (chosen) | Candidate B (not chosen) |
|---|---|---|
| Profitable (CAGR > 0 net) | **Yes** (12.1%) | Yes (14.8%) |
| Benchmark-beating (G1) | **No** | No |
| Control-beating (G2) | **No** | No |
| Development-qualified (G1–G4) | **No** | No (and not eligible) |

**Hypothesis budget:** H014 used 1 of the 3 Phase 2 hypotheses. **The Holdout remains unopened and unconsumed.**

## Operational notes (no effect on results)

- **Canary defects.** Canary v1.0 (E965-01) and diagnostic v1.0 (E966-01) had defects in their own audit code. Both were fixed, documented (D096, D097) and re-run. The S014 code never changed after the freeze.
- **Dividend-factor convention (D097).** Rolling windows match fresh history exactly on 83% of samples. The rest differ by a dividend factor of at most 0.07% on bars older than the dividend. No signal was affected.
- **QuantConnect incidents.**
  - QuantConnect delayed the fill events of E965-04 by over an hour, and a container restart then interrupted its download. It was recovered from the same backtest (D077).
  - QuantConnect's backtest node ran out of disk twice: E014-13 and E014-14 never started. Each was re-run once as a technical repeat (D099).
  - Two holdings were closed by the stale-data rule (D059) after acquisitions without a delisting event (E014-03, E014-08).
- **Quality checks.** 0 timing violations in any run; every fill was at the next open ± slippage.

## Evidence files

- `research/phase2/P2_results.json`: every number above, from `P2_eval.py`, which was committed before the first development run.
- `research/phase2/P2_spec.md`: frozen rules (hash-pinned).
- `research/phase2/P2_canary_check.json` and `P2_canary_min_position.json`: canary verification.
- `DECISIONS.md` D094–D100.

**STOP.** Awaiting the owner's decision. The options are:
- record H014 as rejected and stop Phase 2;
- propose a second, separately registered hypothesis (budget 2 of 3 remaining);
- review the programme.

H014 will not be modified.
