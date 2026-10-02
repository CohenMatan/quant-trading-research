# E016-02 — S016 v1.0 (benchmark)

P2 EW-H016: equal weight of the exact H016 universe, monthly, 25% band (B901 mechanics), $10M paper notional. Primary benchmark of G1/G3/G4. Pre-declared in research/phase2/H016_spec.md (frozen, D116).

- **Status:** completed_with_warnings
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `0aa1d3e606cb4388a022dbc300a3e3350f92b82b` · **QC backtest:** `5d4b31018e4e2344b611516d1758b11d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T15:33:31Z · **runtime:** 1058s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'ew', 'band': 0.25}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 14.42% |
| Annualised volatility | 17.73% |
| Sharpe (rf = 0) | 0.85 |
| Sortino | 1.18 |
| Max drawdown | -35.98% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.40 |
| Worst year | -6.55% |
| Worst month | -16.97% |
| Closed trades | 3025 |
| Win rate | 32.79% |
| Average winner | 42.69% |
| Average loser | -16.32% |
| Expectancy per trade | 3.03% |
| Profit factor | 1.05 |
| Average holding (calendar days) | 439.1 |
| Average exposure | 94.05% |
| Turnover (1-way, per year) | 0.39 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.46% | 1.02 | 0.96 |
| E901-07 | 1.04% | 0.99 | 1.00 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.53% |
| 2011 | 0.66% |
| 2012 | 17.51% |
| 2013 | 36.15% |
| 2014 | 10.48% |
| 2015 | -2.63% |
| 2016 | 13.41% |
| 2017 | 20.12% |
| 2018 | -6.55% |
| 2019 | 27.82% |
| 2020 | 24.48% |
| 2021 | 18.40% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 9298186.31 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 10000000.00 vs initial cash 10000000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.031994; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 352 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 17423 orders vs QuantConnect Total Orders 17423 |
| fills_match_harness_count | pass | downloaded fill events 17416 vs harness-recorded fills 17416 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | warn | 3 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 3 mirrored |
| commission_fixed_per_order | pass | 17419 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `6b021f2932b874ed2159cdcf144aed2a41aaef89395c70d9e2225192c41911b9`
- fills_sha256: `3e36349f946117ea30ac6ce2ce3066f671e1ba1df8f60c47537679a318cca300`
- trades_sha256: `ac6d24b06a95c41a39954ed59fd216244043494534c8749d25f874e03dd68751`
