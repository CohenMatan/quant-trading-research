# E005-02 — S005 v1.1 (research)

C01 H005 S005 v1.1 (pre-declared variation) on IS 2010-2017

- **Status:** integrity_failed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `4c32c9677ac48dfd268298016481c0cb68cf8da3` · **QC backtest:** `a26378ba2346da0921b9283aa6da4716` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T13:48:23Z · **runtime:** 383s
- **Parameters:** `{'vol_days': 252, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.58% |
| Annualised volatility | 9.42% |
| Sharpe (rf = 0) | 1.21 |
| Sortino | 1.77 |
| Max drawdown | -9.43% |
| Longest drawdown (trading days) | 221 |
| Calmar | 1.23 |
| Worst year | 3.08% |
| Worst month | -6.86% |
| Closed trades | 206 |
| Win rate | 62.62% |
| Average winner | 10.83% |
| Average loser | -5.73% |
| Expectancy per trade | 4.64% |
| Profit factor | 2.86 |
| Average holding (calendar days) | 195.6 |
| Average exposure | 93.87% |
| Turnover (1-way, per year) | 1.77 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -1.71% | 0.51 | 0.78 |
| E901-03 | -2.58% | 0.45 | 0.75 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.31% |
| 2011 | 14.41% |
| 2012 | 5.70% |
| 2013 | 17.92% |
| 2014 | 13.32% |
| 2015 | 3.08% |
| 2016 | 11.74% |
| 2017 | 11.73% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97787.36 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | FAIL | min cash/equity -0.0179 |
| cash_never_negative | warn | min cash/equity -0.0179 |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.913330198470113e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 430 orders vs QuantConnect Total Orders 430 |
| fills_match_harness_count | pass | downloaded fill events 429 vs harness-recorded fills 429 |
| commission_fixed_per_order | pass | 429 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c71d2ebb0f8f042012871a2d939350d54bc475c7c34270a70205be15cdd44fa2`
- fills_sha256: `134bc8f9e2716d02c811d09bab24b64487099f05d793827e06f50fd192223984`
- trades_sha256: `bc7293c6ca035bb8ce08afaf256c7112356897540f6cdf31e51c65a09ebd7026`
