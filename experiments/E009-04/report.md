# E009-04 — S009 v1.0 (research)

C02 H009 S009 v1.0 (pre-declared selection candidate, D069) on IS 2010-2017: base: 1-day volume shock, hold 20 | TECHNICAL REPEAT of E009-01 (runner lost in a container restart; identical configuration; not an extra trial, D069)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `3e521c1f8a0a7e49d0ecf4ff1b3297d08d5e83cf` · **QC backtest:** `773ee0f5581d065f1396e4f057ee3db6` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T23:40:55Z · **runtime:** 700s
- **Parameters:** `{'vol_mult': 2.5, 'days': 1, 'hold': 20, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.13% |
| Annualised volatility | 14.71% |
| Sharpe (rf = 0) | 0.67 |
| Sortino | 0.94 |
| Max drawdown | -20.38% |
| Longest drawdown (trading days) | 624 |
| Calmar | 0.45 |
| Worst year | -6.59% |
| Worst month | -8.48% |
| Closed trades | 907 |
| Win rate | 56.89% |
| Average winner | 5.23% |
| Average loser | -5.45% |
| Expectancy per trade | 0.63% |
| Profit factor | 1.23 |
| Average holding (calendar days) | 30.1 |
| Average exposure | 89.27% |
| Turnover (1-way, per year) | 10.87 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.21% | 0.78 | 0.76 |
| E901-07 | -4.79% | 0.76 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 20.76% |
| 2011 | -6.59% |
| 2012 | 13.83% |
| 2013 | 25.81% |
| 2014 | 5.26% |
| 2015 | 4.88% |
| 2016 | -1.29% |
| 2017 | 14.13% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 95984.59 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.028504; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 14 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6137604829183815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1825 orders vs QuantConnect Total Orders 1825 |
| fills_match_harness_count | pass | downloaded fill events 1824 vs harness-recorded fills 1824 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1824 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `e3ff22c5760ac4d452b1df3940604a02a26102acbce1357765f12bc76e43f884`
- fills_sha256: `0948db4fffb9ae89bdbbf18da46e9a5bec5dc0e7a5248362bc0340beafdac645`
- trades_sha256: `eb3515f91fcd51e65eb0f2cce165d6b359ecb09060c724097a9963f9035afd67`
