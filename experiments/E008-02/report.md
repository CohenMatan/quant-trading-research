# E008-02 — S008 v1.1 (research)

C02 H008 S008 v1.1 (pre-declared selection candidate, D069) on IS 2010-2017: 6-1 month residual return

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `d4046c524f82c8452efca2fc91da6bd73705c143` · **QC backtest:** `dc6eb1db84e7ea6068879e5533fd94e9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T22:59:18Z · **runtime:** 865s
- **Parameters:** `{'window': 126, 'skip': 21, 'scaled': True, 'slots': 10, 'keep': 20}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.64% |
| Annualised volatility | 16.62% |
| Sharpe (rf = 0) | 0.69 |
| Sortino | 0.97 |
| Max drawdown | -25.96% |
| Longest drawdown (trading days) | 492 |
| Calmar | 0.41 |
| Worst year | -10.23% |
| Worst month | -10.64% |
| Closed trades | 566 |
| Win rate | 53.89% |
| Average winner | 8.51% |
| Average loser | -7.20% |
| Expectancy per trade | 1.27% |
| Profit factor | 1.33 |
| Average holding (calendar days) | 49.0 |
| Average exposure | 86.17% |
| Turnover (1-way, per year) | 6.40 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.70% | 0.94 | 0.81 |
| E901-07 | -3.29% | 0.89 | 0.83 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.90% |
| 2011 | -10.23% |
| 2012 | 14.50% |
| 2013 | 43.81% |
| 2014 | 2.38% |
| 2015 | 7.20% |
| 2016 | 6.03% |
| 2017 | 15.41% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 92272.05 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.063474; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.8364951163126596e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1142 orders vs QuantConnect Total Orders 1142 |
| fills_match_harness_count | pass | downloaded fill events 1142 vs harness-recorded fills 1142 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1142 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `cc39e29510a7e8a38418afc935fb428d59f53e596a4ff7501c2cff6647be430e`
- fills_sha256: `6cf666707e19b3df186abb3fa3d468a761e59cd701e1648e816193a1205b898a`
- trades_sha256: `3778c0377cc9154ed7754a1d9331fe0e6276ba4482514da5d3d4936333f3df15`
