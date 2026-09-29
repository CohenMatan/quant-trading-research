# E007-03 — S007 v1.2 (research)

C02 H007 S007 v1.2 (pre-declared selection candidate, D069) on IS 2010-2017: no SMA200 trend condition

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `29aef0b92b884c01c6baa1282ee20f5e4f511c9c` · **QC backtest:** `8db4a27f6e0ecdfc9327aad79742e739` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T22:26:17Z · **runtime:** 925s
- **Parameters:** `{'setup': 'bandwidth', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': False, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.36% |
| Annualised volatility | 11.96% |
| Sharpe (rf = 0) | 0.50 |
| Sortino | 0.69 |
| Max drawdown | -18.96% |
| Longest drawdown (trading days) | 882 |
| Calmar | 0.28 |
| Worst year | -8.90% |
| Worst month | -8.67% |
| Closed trades | 941 |
| Win rate | 42.08% |
| Average winner | 6.16% |
| Average loser | -3.92% |
| Expectancy per trade | 0.32% |
| Profit factor | 1.10 |
| Average holding (calendar days) | 25.1 |
| Average exposure | 78.17% |
| Turnover (1-way, per year) | 11.31 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -7.98% | 0.52 | 0.62 |
| E901-07 | -8.56% | 0.51 | 0.65 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 6.02% |
| 2011 | 0.47% |
| 2012 | 21.45% |
| 2013 | 16.25% |
| 2014 | 6.77% |
| 2015 | -8.90% |
| 2016 | -2.03% |
| 2017 | 5.89% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 90896.19 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.028992; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 14 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.480852778507996e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1893 orders vs QuantConnect Total Orders 1893 |
| fills_match_harness_count | pass | downloaded fill events 1892 vs harness-recorded fills 1892 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1892 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `81b88f789a46861b93f37237b2c1bd6c576c4048d834d9bf7b2d940222dd57fd`
- fills_sha256: `6716d8f378595397e0a6d0a17fecd4579640f1c9ee11edd354199cd6179d0a04`
- trades_sha256: `6166bc050c1a0f0de341cc73016f521142e3e70a20ac73c8138db645351cc5c2`
