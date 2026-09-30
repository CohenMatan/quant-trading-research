# E010-02 — S010 v1.1 (research)

C02 H010 S010 v1.1 (pre-declared selection candidate, D069) on IS 2010-2017: hold 60

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `0b3aab44d7ffb0c82e6e0cbebc229c53fbb336e7` · **QC backtest:** `1c3b90b31f8e71e77f8d0e8484cc6bd4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T00:35:47Z · **runtime:** 779s
- **Parameters:** `{'min_gap': 0.02, 'gap_atr': 1.5, 'require_hold': True, 'vol_mult': 2.0, 'hold': 60, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.60% |
| Annualised volatility | 13.39% |
| Sharpe (rf = 0) | 0.68 |
| Sortino | 0.96 |
| Max drawdown | -21.72% |
| Longest drawdown (trading days) | 611 |
| Calmar | 0.40 |
| Worst year | -8.98% |
| Worst month | -6.16% |
| Closed trades | 534 |
| Win rate | 35.21% |
| Average winner | 12.69% |
| Average loser | -5.30% |
| Expectancy per trade | 1.04% |
| Profit factor | 1.25 |
| Average holding (calendar days) | 47.8 |
| Average exposure | 85.43% |
| Turnover (1-way, per year) | 6.32 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.74% | 0.69 | 0.74 |
| E901-07 | -5.32% | 0.66 | 0.77 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.42% |
| 2011 | -8.90% |
| 2012 | 14.79% |
| 2013 | 28.71% |
| 2014 | 17.54% |
| 2015 | -3.82% |
| 2016 | -8.98% |
| 2017 | 24.13% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96677.95 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.026497; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 6 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.2692361674484425e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1078 orders vs QuantConnect Total Orders 1078 |
| fills_match_harness_count | pass | downloaded fill events 1078 vs harness-recorded fills 1078 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1078 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `acaa98458e9383f825cc55992a782970373fafae2006e99f5fcca7987631751d`
- fills_sha256: `12a9b289fddb8dc061a84027b5969003b838f53c97a3f0be2c1e323d2af86e83`
- trades_sha256: `9a3c30d1532c034fed485c84c2298e78ed3f3a4bbe0e18ffd29c68721d612b43`
