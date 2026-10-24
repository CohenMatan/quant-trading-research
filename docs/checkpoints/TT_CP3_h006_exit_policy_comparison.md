# TT-CP3: H006 exit-policy comparison — does removing the 60-session time limit add value?

**Date:** 2026-10-24 · **Owner direction:** D304 (`docs/owner/2026-10-24_h006_exit_policy_comparison.md`) · **Record:** D305
**Frozen before any run:** spec `research/tt/h006_exit/H006X_spec.md`, evaluation rule `H006X_eval.py`, S006 code, all pinned in `qresearch.h006x` (commit 6053804).
**Result file:** `research/tt/h006_exit/H006X_result.json`.
**Status:** EXPLORATORY. The 2010–2021 data has been extensively researched, so nothing here is independent validation. H006 stays REJECTED.

## Answer in three lines

1. **Removing the time limit does not add meaningful value.**
   - B ends with 1.06× A's wealth; the pre-declared bar was 1.10×.
   - The monthly B − A difference is statistically indistinguishable from zero (Newey–West t = 0.12).
2. **Neither version beats SPY.**
   - B: $424,456 (12.82% a year). A: $401,344 (12.29%). SPY: $511,757 (14.59%).
3. **Nothing here is robust enough to justify seeking independent evidence. Recommendation: close.** No parameter variations.

## 1. What was run (exactly as frozen)

| Run | Rules | Build | Trades | Runtime |
|---|---|---|---|---|
| E006-04 Control A | H006 v1.0: 55-day-high breakout, volume ≥ 1.5×, close > SMA200, chandelier 3 × ATR20, **60-session time stop**, 10 slots | LEAN 18203 (default) | 809 | 17 min |
| E006-05 Experiment B | Identical, **no time stop** (S006 v1.3) | 18203 | 667 | 16 min |
| E900-08 SPY | B900 buy-and-hold, 98% SPY, dividends reinvested | 18203 | — | 20 s |

- **Common terms:** DEV 2010-01-04 → 2021-12-31; $100,000; $7 per order plus 10 bps per side; D051 execution; next-open fills; vendor ≥ $2B universe.
- **Retries:** none used. One start-up refusal (dirty tree after E900-08, no backtest submitted) is not a run.
- **E900-08 equals E900-07** (build 18131) to every digit, so the SPY data has not drifted.
- **Scope flags, stated before the runs (spec §2):**
  - Flag 1: B's uncapped holding period, read as granted by D304 for this run only.
  - Flag 2: the vendor universe misses ≥ $2B names (RR5), read as approved by D304's request for a universe-sensitivity analysis.

## 2. Results

| | Control A (60-day cap) | Experiment B (no cap) | SPY |
|---|---|---|---|
| Terminal wealth | $401,344 | **$424,456** | **$511,757** |
| CAGR | 12.29% | 12.82% | 14.59% |
| vs SPY, CAGR | −2.30 pts | −1.77 pts | — |
| Volatility / Sharpe | 20.2% / 0.67 | 16.4% / 0.82 | 16.6% / 0.91 |
| Maximum drawdown | −31.6% | −27.4% | −33.1% |
| Upside / downside capture (monthly) | 0.70 / 0.44 | 0.71 / 0.49 | 1 / 1 |
| Beta; alpha a year (Newey–West t) | 0.70; +3.0% (0.61) | 0.69; +3.0% (1.12) | — |
| Information ratio vs SPY | −0.08 | −0.14 | — |
| Holding: mean / median / 90th percentile / max (sessions) | 35 / 33 / 61 / 61 | 43 / 33 / 88 / 276 | — |
| Holds > 126 / > 252 sessions | 0% / 0% | 3.1% / 0.15% | — |
| Orders; one-way turnover a year | 1,628; 6.3× | 1,344; 5.2× | — |
| Costs (commission + slippage) a year | 1.70% of equity | 1.36% | — |
| Top 1 / top 5 stocks' share of net P&L | **47%** (GME) / 72% | 10% / 37% | — |

**Halves:** cumulative log-wealth difference.

| | B − A | B − SPY | B − SPY, CAGR |
|---|---|---|---|
| 2010–2015 | +0.047 | +0.025 | +0.47 pts a year |
| 2016–2021 | +0.008 | **−0.212** | **−4.06 pts a year** |

**Pre-declared answers (spec §5):**
- V1 (W_B / W_A ≥ 1.10): **FAIL**, at 1.058.
- V2 (B ahead of A in both halves): PASS.
- V3 (no single year dominates): PASS, the largest year is 19% of the positive differences.
- So Q1 = **NOT MEANINGFUL**.
- Q2: B beats SPY = **NO**.
- R1–R5: R1, R2 and R3 FAIL; R4 and R5 pass. So **Q3 = NO → close**.

## 3. What actually happened

- **Why removing the cap changes little.** The 3 × ATR chandelier stop exits most trades long before 60 sessions: the median hold is 33 sessions in both runs. The time stop was binding for only about 22% of A's trades. Without it, only 3% of B's trades last more than six months, and one trade lasts more than a year (276 sessions maximum). "Letting winners run" is limited by the trailing stop, not by the time cap.
- **The A − B gap is noise dominated by a single stock.**
  - **Through 2020, B led clearly:** wealth multiple 4.27× vs A 3.15× vs SPY 4.00×; CAGR 14.1% vs 11.0% vs 13.4%.
  - **January 2021 (GME):** A happened to have free slots on 22 January 2021 and caught GameStop's short squeeze, +$140,614 in 4 days. That one trade is **47% of A's entire 12-year net P&L**. B's slots were full of longer holds, so it missed it.
  - **2021 for B:** −0.6% against SPY's +28%.
  - Both the "B ahead through 2020" and "A catches up in 2021" paths come from slot-timing luck. Neither is a robust effect.
  - The through-2020 numbers are an after-the-fact cut and are reported as description only; they change no answer.
- **Data drift is larger than the effect.** A's 2010–2017 sub-path on today's dataset returns 13.66% a year (Sharpe 0.98) against 12.19% (0.88) for the original E006-01 on the old dataset. The trade count is the same (529 entered). That 1.5-point swing from the data vendor change alone is three times the 0.5-point A-vs-B difference.

## 4. Universe-quality sensitivity

- **Paired comparison:** A and B use the same universe, so the vendor universe's missing ≥ $2B names (RR5: 3.5–6.1% a year in 2010–2015, 0.8–2.9% in 2016–2021) largely cancel in A − B.
- **Against SPY:**
  - 2010–2015: B's +0.47-point lead is smaller than RR5's largest confirmed survivorship bias (0.78 points). It is not distinguishable from universe bias.
  - 2016–2021: B is −4.06 points behind SPY, far beyond any plausible bias (RR6 upper bound 1.26 points). The universe limitation cannot turn this into a win.
- **Forced exits (delistings, mostly takeovers):** 26 in B, +$45,173 (14% of net P&L); 18 in A, +$28,650. This is where missing failed companies would matter most. If anything, it flatters both runs.

## 5. Taxes (descriptive)

- Only **3.8%** of B's realised gains came from holds longer than a year (A: 0%).
- B's tax position is therefore essentially all short-term gains, like A's.
- B's turnover is 5.2× a year against SPY's near zero. After taxes the gap to SPY would widen, not narrow.

## 6. Conclusion and recommendation

- Removing H006's 60-session time limit **did not materially improve the strategy**. The trailing stop, not the time cap, governs how long winners run.
- The small terminal-wealth difference is inside the noise of single-stock slot timing (one GME trade) and of data-vendor drift.
- **Neither version beats SPY** in terminal wealth after costs. The modest defensive profile (lower beta, about 0.45–0.5 downside capture) does not compensate.
- **Recommendation: close this question.** Do not vary the stop multiple, slot count, entry or any other parameter: that would be the search the owner ruled out. Do not seek independent evidence for H006 with or without the time cap.

**Constraints kept:**
- one comparison only; the spec and evaluation rule were frozen and pinned before any run;
- no grid and no tuning;
- no 1999–2009 data, no Holdout, no purchase, no new infrastructure;
- H006 stays REJECTED.

**Tests:**
- New files `tests/test_h006x.py` and `tests/test_h006x_pins.py`.
- Two existing items were adjusted. Disclosed here because D296 restricted test changes before WIKI access; that condition no longer applies.
  - **Registry tests.** Three tests pin the historical pre-C02 / pre-C03 trial counts: `tests/test_registry.py` (1) and `tests/test_c03_stats.py` (2). The new research runs E006-04 / 05 must be excluded from those historical counts like every later programme. Their exclusion lists gain `H006X` / `TT`, exactly as H032 was added. **No pinned count changed** (19 / 15 / 1; 37 / 0 / 26 / 1; 40 / 73).
  - **Signal-equivalence canary.** `strategies/X961_signal_equivalence/sig006.py` is re-copied from the new S006 `signals.py`, as `tests/test_signal_equivalence_canary.py` requires. The canary's calls are unchanged in behaviour (time stop 60, no carry; tested).

**Experiments added:** E900-08, E006-04, E006-05 (3 runs; 0 retries).

**STOPPED for owner review.**
