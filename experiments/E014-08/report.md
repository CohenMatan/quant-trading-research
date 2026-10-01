# E014-08 — S014 v1.1 (benchmark)

P2 control C1 trend-only, exit B (same code, universe, slots, costs and exit as E014-02). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed_with_warnings
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `7a38f1a6327ec91a9fe07f33e60bdcb7262d0a17` · **QC backtest:** `cbdfc04335eb134ec636fd3e411700db` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T01:15:47Z · **runtime:** 1395s
- **Parameters:** `{'mode': 'c1', 'exit': 'B', 'limit': 126, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 7.32% |
| Annualised volatility | 32.72% |
| Sharpe (rf = 0) | 0.38 |
| Sortino | 0.52 |
| Max drawdown | -53.14% |
| Longest drawdown (trading days) | 1344 |
| Calmar | 0.14 |
| Worst year | -32.21% |
| Worst month | -19.22% |
| Closed trades | 487 |
| Win rate | 39.22% |
| Average winner | 34.82% |
| Average loser | -16.59% |
| Expectancy per trade | 3.57% |
| Profit factor | 1.16 |
| Average holding (calendar days) | 104.4 |
| Average exposure | 92.77% |
| Turnover (1-way, per year) | 2.94 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -7.27% | 1.25 | 0.63 |
| E901-07 | -6.16% | 1.26 | 0.69 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 27.87% |
| 2011 | -7.29% |
| 2012 | 34.16% |
| 2013 | 20.54% |
| 2014 | 10.34% |
| 2015 | -5.21% |
| 2016 | -2.39% |
| 2017 | 10.63% |
| 2018 | -32.21% |
| 2019 | 35.48% |
| 2020 | 41.48% |
| 2021 | -17.09% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 88853.97 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.003614; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 34 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0058560358130133e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 989 orders vs QuantConnect Total Orders 989 |
| fills_match_harness_count | pass | downloaded fill events 985 vs harness-recorded fills 985 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | warn | 1 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 1 mirrored |
| commission_fixed_per_order | pass | 986 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2b32e56a4853596e6ca535d14a9f771e8f532e4c0003f3ab82593caed5cd0d03`
- fills_sha256: `88d602f5cdc5735eb8cb5074441a35d6cbec1e88203d82eb20153fa11b046691`
- trades_sha256: `ff8f570b526d228413c8d39c817ea6e2e19cd43bf0b1b10217d82d75e6f11d26`
