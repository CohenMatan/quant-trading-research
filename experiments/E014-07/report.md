# E014-07 — S014 v1.0 (benchmark)

P2 control R random uptrend seed 3, exit A (same code, universe, slots, costs and exit as E014-01). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `e838a8d441fa3702f9160953e0c5b8fbf70f2142` · **QC backtest:** `1982f47f260343fd3c8fab9d17bb7355` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T00:53:59Z · **runtime:** 1297s
- **Parameters:** `{'mode': 'rand', 'exit': 'A', 'limit': 63, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 11.83% |
| Annualised volatility | 17.43% |
| Sharpe (rf = 0) | 0.73 |
| Sortino | 1.02 |
| Max drawdown | -32.37% |
| Longest drawdown (trading days) | 479 |
| Calmar | 0.37 |
| Worst year | -10.44% |
| Worst month | -13.59% |
| Closed trades | 350 |
| Win rate | 37.71% |
| Average winner | 23.78% |
| Average loser | -7.83% |
| Expectancy per trade | 4.09% |
| Profit factor | 1.60 |
| Average holding (calendar days) | 144.2 |
| Average exposure | 94.58% |
| Turnover (1-way, per year) | 2.12 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.75% | 0.84 | 0.80 |
| E901-07 | -1.65% | 0.78 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.23% |
| 2011 | 3.02% |
| 2012 | 14.58% |
| 2013 | 40.72% |
| 2014 | 4.79% |
| 2015 | -3.35% |
| 2016 | -0.26% |
| 2017 | 27.40% |
| 2018 | -10.44% |
| 2019 | 26.39% |
| 2020 | 26.04% |
| 2021 | 6.01% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 90784.82 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.024614; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.8302747322856585e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 712 orders vs QuantConnect Total Orders 712 |
| fills_match_harness_count | pass | downloaded fill events 712 vs harness-recorded fills 712 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 712 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `de4f3290caad8dd6411fbc12fcb8c24a5f810de36044eb93f9f95ab6fdf60c9b`
- fills_sha256: `36fa4875ef6a312b571280ee9ad7101a3a5e94cd2257e528b9494ecc3acc7d1a`
- trades_sha256: `95b4b6ac6520073139558c5840b02656122cdf26220f3d9e484c4d31a357fc81`
