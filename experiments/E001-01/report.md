# E001-01 — S001 v1.0 (research)

C01 H001 S001 v1.0 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `3b2e3c32d7051fdb37fe1cdc458f112380d9d516` · **QC backtest:** `5dbf7039455abd329768b7bd1d676f28` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T11:39:36Z · **runtime:** 353s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 1.80% |
| Annualised volatility | 17.65% |
| Sharpe (rf = 0) | 0.19 |
| Sortino | 0.26 |
| Max drawdown | -36.14% |
| Longest drawdown (trading days) | 688 |
| Calmar | 0.05 |
| Worst year | -20.82% |
| Worst month | -12.34% |
| Closed trades | 2035 |
| Win rate | 54.10% |
| Average winner | 1.58% |
| Average loser | -2.34% |
| Expectancy per trade | -0.22% |
| Profit factor | 0.78 |
| Average holding (calendar days) | 5.9 |
| Average exposure | 91.66% |
| Turnover (1-way, per year) | 14.41 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -11.49% | 1.03 | 0.84 |
| E901-03 | -12.35% | 1.00 | 0.89 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.71% |
| 2011 | -20.82% |
| 2012 | 11.38% |
| 2013 | 29.80% |
| 2014 | -1.20% |
| 2015 | -13.74% |
| 2016 | 4.00% |
| 2017 | 4.54% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 78179.29 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0126 |
| cash_never_negative | pass | min cash/equity 0.0126 |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 4085 orders vs QuantConnect Total Orders 4085 |
| fills_match_harness_count | pass | downloaded fill events 4085 vs harness-recorded fills 4085 |
| commission_fixed_per_order | pass | 4085 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `d0ca29298187b1f4540690342eaf8deed6b28dfc9e3be443593e19ee0eaacdca`
- fills_sha256: `fc944b2560a96ad82657a916f0b8eba44ce3b306cdf8543a9a445a83980c589c`
- trades_sha256: `696b48ea2c2d9d514b1957d722e607e2c8f52bac3a81bd77370fbb05427ede40`
