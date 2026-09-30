# E013-05 — S013 v1.1 (research)

C03 H013 S013 v1.1 seed 2 (one candidate per variation; seeds are replicates, D082) on IS, paired with null E962-23. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `c2cc811531a1f9d5655743723492fb402d4fb8c6` · **QC backtest:** `582e3ccf7cff2ea45f7d02a1123ff5b7` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T16:04:50Z · **runtime:** 370s
- **Parameters:** `{'q': 0.1, 'stat': 'max', 'seed': 2, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.01% |
| Annualised volatility | 14.44% |
| Sharpe (rf = 0) | 0.80 |
| Sortino | 1.11 |
| Max drawdown | -23.24% |
| Longest drawdown (trading days) | 358 |
| Calmar | 0.47 |
| Worst year | -5.93% |
| Worst month | -9.70% |
| Closed trades | 481 |
| Win rate | 61.75% |
| Average winner | 10.49% |
| Average loser | -10.19% |
| Expectancy per trade | 2.58% |
| Profit factor | 1.60 |
| Average holding (calendar days) | 88.0 |
| Average exposure | 83.69% |
| Turnover (1-way, per year) | 3.55 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.33% | 0.90 | 0.90 |
| E901-07 | -2.92% | 0.86 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 20.73% |
| 2011 | -5.93% |
| 2012 | 15.35% |
| 2013 | 24.97% |
| 2014 | 8.61% |
| 2015 | 8.45% |
| 2016 | 9.99% |
| 2017 | 8.53% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96462.11 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.108493; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 977 orders vs QuantConnect Total Orders 977 |
| fills_match_harness_count | pass | downloaded fill events 977 vs harness-recorded fills 977 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 977 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3ebc8c346bbc9c72052f562fb5d3fda751416c5ad1b6b7165d3d094e59be3f06`
- fills_sha256: `e2208ece8f889bceffa6221828a417ccf41aae477a95f732cfd63b5ee46270b7`
- trades_sha256: `c59cc740845cda37baa4e598f3e8ee84440197327eb741db0cb91103d7986d52`
