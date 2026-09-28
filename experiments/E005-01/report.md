# E005-01 — S005 v1.0 (research)

C01 H005 S005 v1.0 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `01f86b8479427457888e1bce672426f50c1f406e` · **QC backtest:** `5829053a70afe2c4c1941628a7771458` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T13:40:29Z · **runtime:** 455s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.73% |
| Annualised volatility | 8.03% |
| Sharpe (rf = 0) | 1.31 |
| Sortino | 1.93 |
| Max drawdown | -7.93% |
| Longest drawdown (trading days) | 134 |
| Calmar | 1.35 |
| Worst year | 4.98% |
| Worst month | -6.10% |
| Closed trades | 574 |
| Win rate | 61.32% |
| Average winner | 5.07% |
| Average loser | -4.00% |
| Expectancy per trade | 1.56% |
| Profit factor | 1.88 |
| Average holding (calendar days) | 69.6 |
| Average exposure | 92.79% |
| Turnover (1-way, per year) | 4.71 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -2.56% | 0.45 | 0.80 |
| E901-03 | -3.43% | 0.39 | 0.77 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.96% |
| 2011 | 13.44% |
| 2012 | 8.77% |
| 2013 | 19.72% |
| 2014 | 10.06% |
| 2015 | 7.48% |
| 2016 | 4.98% |
| 2017 | 8.86% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97928.33 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0198 |
| cash_never_negative | pass | min cash/equity 0.0198 |
| fills_after_signal_date | pass | 0 violations, 79 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3862034721872065e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1162 orders vs QuantConnect Total Orders 1162 |
| fills_match_harness_count | pass | downloaded fill events 1162 vs harness-recorded fills 1162 |
| commission_fixed_per_order | pass | 1162 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `b3b1d0ab41927bc002efe4c8421d3ec717fd7d0debb860298ba429810209a330`
- fills_sha256: `5fb02097767858c80a7afe137f7bd9f219ea23b5ba15bd7a47791518574ef943`
- trades_sha256: `56e9ea3025557124d9811949e79e73451a275dcefae91730912bc8f610c690a0`
