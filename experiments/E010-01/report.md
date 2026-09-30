# E010-01 — S010 v1.0 (research)

C02 H010 S010 v1.0 (pre-declared selection candidate, D069) on IS 2010-2017: base: gap-and-hold, hold 40

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `77b1a1b46e492d8972778ce100e17ffc38a3f3ac` · **QC backtest:** `055d04290e269b7ecbfe266827fdc081` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T00:17:14Z · **runtime:** 1093s
- **Parameters:** `{'min_gap': 0.02, 'gap_atr': 1.5, 'require_hold': True, 'vol_mult': 2.0, 'hold': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 6.94% |
| Annualised volatility | 12.91% |
| Sharpe (rf = 0) | 0.58 |
| Sortino | 0.81 |
| Max drawdown | -19.11% |
| Longest drawdown (trading days) | 571 |
| Calmar | 0.36 |
| Worst year | -5.47% |
| Worst month | -8.26% |
| Closed trades | 711 |
| Win rate | 40.08% |
| Average winner | 8.91% |
| Average loser | -4.98% |
| Expectancy per trade | 0.59% |
| Profit factor | 1.18 |
| Average holding (calendar days) | 35.4 |
| Average exposure | 83.37% |
| Turnover (1-way, per year) | 8.43 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -6.40% | 0.66 | 0.73 |
| E901-07 | -6.98% | 0.64 | 0.77 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 1.05% |
| 2011 | -5.47% |
| 2012 | 19.78% |
| 2013 | 23.02% |
| 2014 | 14.13% |
| 2015 | -3.70% |
| 2016 | -1.80% |
| 2017 | 12.50% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 90065.32 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.026141; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.480852778507996e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1432 orders vs QuantConnect Total Orders 1432 |
| fills_match_harness_count | pass | downloaded fill events 1431 vs harness-recorded fills 1431 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1431 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `887d821b42554b75807e73a9651125654329166c51a9d61cb5c5998586e6e434`
- fills_sha256: `90d8d71fffa7cda461f36ba23cae67be4b0ce7663e55abb9191ee2123a7df82f`
- trades_sha256: `10239b0f7907a4823a28db0cc9a735d75348127e4e04fe0f950ccdfeb0b5ef07`
