# E004-03 — S004 v1.2 (research)

C01 H004 S004 v1.2 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `16f31e89d7431c606c483131d310fb3de1606aba` · **QC backtest:** `3a9b45ab30b0d154001ca6caf247bd5b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T13:29:43Z · **runtime:** 334s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.05, 'hold_days': 20, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.99% |
| Annualised volatility | 24.48% |
| Sharpe (rf = 0) | 0.59 |
| Sortino | 0.84 |
| Max drawdown | -44.58% |
| Longest drawdown (trading days) | 900 |
| Calmar | 0.27 |
| Worst year | -18.55% |
| Worst month | -14.66% |
| Closed trades | 1460 |
| Win rate | 52.88% |
| Average winner | 9.60% |
| Average loser | -8.71% |
| Expectancy per trade | 0.97% |
| Profit factor | 1.20 |
| Average holding (calendar days) | 28.9 |
| Average exposure | 94.13% |
| Turnover (1-way, per year) | 11.97 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -1.29% | 1.31 | 0.77 |
| E901-03 | -2.16% | 1.28 | 0.83 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 9.07% |
| 2011 | 0.65% |
| 2012 | 20.63% |
| 2013 | 58.58% |
| 2014 | -18.55% |
| 2015 | -4.55% |
| 2016 | 8.46% |
| 2017 | 39.49% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 82620.63 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0133 |
| cash_never_negative | pass | min cash/equity 0.0133 |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2938 orders vs QuantConnect Total Orders 2938 |
| fills_match_harness_count | pass | downloaded fill events 2935 vs harness-recorded fills 2935 |
| commission_fixed_per_order | pass | 2935 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `cbb373098d5dc3358eb416ee1aff4fe4c464cfd8f6c3231a30adb46cb28a0ec2`
- fills_sha256: `e286f1d2c2a3079d9dcc195028d467dd2d2214ef2a5b8f27e16db64ce5cbb0f6`
- trades_sha256: `f4af1ad6003c2a0f934444541a9ce9e41204bd90db960ec8de24980815bcbd55`
