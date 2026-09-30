# E011-01 — S011 v1.0 (research)

C02 H011 S011 v1.0 (pre-declared selection candidate, D069) on IS 2010-2017: base: 5 annual lags

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `f59d530143c3f93bc7144051b2f5d8a4c3ca03a5` · **QC backtest:** `b76b2f44f4b22818f59983e350b556be` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T01:05:51Z · **runtime:** 812s
- **Parameters:** `{'lags': 5, 'trend_filter': False, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 1.30% |
| Annualised volatility | 20.62% |
| Sharpe (rf = 0) | 0.17 |
| Sortino | 0.23 |
| Max drawdown | -43.28% |
| Longest drawdown (trading days) | 619 |
| Calmar | 0.03 |
| Worst year | -22.21% |
| Worst month | -23.74% |
| Closed trades | 885 |
| Win rate | 51.98% |
| Average winner | 9.35% |
| Average loser | -9.32% |
| Expectancy per trade | 0.38% |
| Profit factor | 1.03 |
| Average holding (calendar days) | 30.6 |
| Average exposure | 80.27% |
| Turnover (1-way, per year) | 9.60 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -12.04% | 1.10 | 0.76 |
| E901-07 | -12.63% | 1.08 | 0.81 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 19.00% |
| 2011 | -3.59% |
| 2012 | -15.57% |
| 2013 | 42.22% |
| 2014 | 8.23% |
| 2015 | -11.17% |
| 2016 | -22.21% |
| 2017 | 7.58% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 86765.12 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.051507; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.069879566903419e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1789 orders vs QuantConnect Total Orders 1789 |
| fills_match_harness_count | pass | downloaded fill events 1780 vs harness-recorded fills 1780 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1780 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `fefea9e4eacb89e4d1480e20d7f824c56884f2d3b17da0633dabe7a2ea1349e0`
- fills_sha256: `34246a9a6b8dfc45eb4a0ff8a8ed06368d758417c49d51add76a7d8f08f5aff7`
- trades_sha256: `60c8eea71c8d616066b01682b92d4d9056f78d41e454a8b53c71e44d200f29ee`
