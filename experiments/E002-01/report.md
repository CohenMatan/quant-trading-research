# E002-01 — S002 v1.0 (research)

C01 H002 S002 v1.0 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `f809898e40d18fe272a67c2e1d535e345d00d106` · **QC backtest:** `349bb88f9e29858f5f87342efb926de4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T12:10:51Z · **runtime:** 351s
- **Parameters:** `{'lookback': 252, 'skip': 21, 'every_months': 1, 'slots': 15, 'band': 0.25, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.97% |
| Annualised volatility | 28.27% |
| Sharpe (rf = 0) | 0.51 |
| Sortino | 0.70 |
| Max drawdown | -42.31% |
| Longest drawdown (trading days) | 606 |
| Calmar | 0.26 |
| Worst year | -12.40% |
| Worst month | -16.49% |
| Closed trades | 540 |
| Win rate | 54.44% |
| Average winner | 17.52% |
| Average loser | -14.04% |
| Expectancy per trade | 3.15% |
| Profit factor | 1.32 |
| Average holding (calendar days) | 77.2 |
| Average exposure | 95.50% |
| Turnover (1-way, per year) | 4.41 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -2.31% | 1.41 | 0.72 |
| E901-03 | -3.18% | 1.39 | 0.78 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 21.30% |
| 2011 | -12.40% |
| 2012 | 41.93% |
| 2013 | 26.91% |
| 2014 | -1.01% |
| 2015 | 2.97% |
| 2016 | 5.91% |
| 2017 | 11.12% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 87108.95 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0107 |
| cash_never_negative | pass | min cash/equity 0.0107 |
| fills_after_signal_date | pass | 0 violations, 21 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.196725525139577e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1174 orders vs QuantConnect Total Orders 1174 |
| fills_match_harness_count | pass | downloaded fill events 1173 vs harness-recorded fills 1173 |
| commission_fixed_per_order | pass | 1173 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `b84dbe535f1c6982e67f0da34b71e99ac1f739fa538bc975aaa51c1e49a440e1`
- fills_sha256: `4bc3f7e88b7bd2a9a8af7047ab44598bdcd523066899f18584d1c74261b3db98`
- trades_sha256: `e62344b7b6d5cfe8fcfa9f01f4b26bc1c2d4745738ce026e7e12698894a88aeb`
