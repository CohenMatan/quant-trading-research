# E001-03 — S001 v1.2 (research)

C01 H001 S001 v1.2 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `e82e5b3b6110c0dae02176c340e9e7a374b8e9d3` · **QC backtest:** `8420da7d5d364eb38d0221c0682a79ad` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T11:52:15Z · **runtime:** 367s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'time', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 3.57% |
| Annualised volatility | 15.51% |
| Sharpe (rf = 0) | 0.30 |
| Sortino | 0.42 |
| Max drawdown | -26.39% |
| Longest drawdown (trading days) | 639 |
| Calmar | 0.14 |
| Worst year | -7.22% |
| Worst month | -9.31% |
| Closed trades | 2295 |
| Win rate | 51.20% |
| Average winner | 3.91% |
| Average loser | -3.85% |
| Expectancy per trade | 0.13% |
| Profit factor | 1.03 |
| Average holding (calendar days) | 14.7 |
| Average exposure | 92.87% |
| Turnover (1-way, per year) | 18.46 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -9.72% | 0.95 | 0.88 |
| E901-03 | -10.58% | 0.89 | 0.90 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 16.20% |
| 2011 | -5.11% |
| 2012 | 2.65% |
| 2013 | 21.17% |
| 2014 | 17.28% |
| 2015 | -6.61% |
| 2016 | -7.22% |
| 2017 | -5.06% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 94721.86 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0117 |
| cash_never_negative | pass | min cash/equity 0.0117 |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 4608 orders vs QuantConnect Total Orders 4608 |
| fills_match_harness_count | pass | downloaded fill events 4605 vs harness-recorded fills 4605 |
| commission_fixed_per_order | pass | 4605 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `8737b8d93b40b312c230f20ae9fa2c0468de17b5be4b2f431b1d12e2140676f5`
- fills_sha256: `6d813906997f38550876adab83340d7ecbc02e296885be0f4a7cef1e95ff27c0`
- trades_sha256: `c0970abd92c218d7551bf98ad8a72e8c799ab2afe29dcb8910211cc543225b0a`
