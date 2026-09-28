# E003-02 — S003 v1.1 (research)

C01 H003 S003 v1.1 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `a204d23a4c3d129afcfae73c9d5942068871e7d0` · **QC backtest:** `ef0d82869f1c5464e52094b447909c83` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T13:11:41Z · **runtime:** 367s
- **Parameters:** `{'rebalance': 'days', 'every_days': 10, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 2.91% |
| Annualised volatility | 13.72% |
| Sharpe (rf = 0) | 0.28 |
| Sortino | 0.38 |
| Max drawdown | -21.08% |
| Longest drawdown (trading days) | 1154 |
| Calmar | 0.14 |
| Worst year | -10.23% |
| Worst month | -6.44% |
| Closed trades | 2575 |
| Win rate | 48.43% |
| Average winner | 3.59% |
| Average loser | -3.28% |
| Expectancy per trade | 0.05% |
| Profit factor | 1.02 |
| Average holding (calendar days) | 16.7 |
| Average exposure | 95.73% |
| Turnover (1-way, per year) | 20.95 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -10.37% | 0.75 | 0.78 |
| E901-03 | -11.24% | 0.70 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 4.68% |
| 2011 | -10.23% |
| 2012 | -0.22% |
| 2013 | 15.19% |
| 2014 | 4.41% |
| 2015 | -3.61% |
| 2016 | 5.09% |
| 2017 | 10.09% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 89002.01 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0093 |
| cash_never_negative | pass | min cash/equity 0.0093 |
| fills_after_signal_date | pass | 0 violations, 25 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 5168 orders vs QuantConnect Total Orders 5168 |
| fills_match_harness_count | pass | downloaded fill events 5166 vs harness-recorded fills 5166 |
| commission_fixed_per_order | pass | 5166 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `49093c09bb432950aa39c78661b5fc3e93b8e64063bca1ba8ddbb7b394710255`
- fills_sha256: `d1f8112027db1c6ad275398ef7873bae85f3d32c88285e192f4390761f2062c6`
- trades_sha256: `a46ade5b79567206db7d25a132fc519de921b4b407025c592a72d97193af7954`
