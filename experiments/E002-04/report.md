# E002-04 — S002 v1.3 (research)

C01 H002 S002 v1.3 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `fc2df66e23ef85a80fe5f1f7c51fa0c242a4a9e0` · **QC backtest:** `b1a44feb2cdc0c8538046d0a38e70cab` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T12:59:38Z · **runtime:** 354s
- **Parameters:** `{'lookback': 252, 'skip': 21, 'every_months': 2, 'slots': 15, 'band': 0.25, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.41% |
| Annualised volatility | 28.12% |
| Sharpe (rf = 0) | 0.49 |
| Sortino | 0.68 |
| Max drawdown | -44.08% |
| Longest drawdown (trading days) | 606 |
| Calmar | 0.24 |
| Worst year | -7.81% |
| Worst month | -15.91% |
| Closed trades | 377 |
| Win rate | 52.79% |
| Average winner | 20.77% |
| Average loser | -15.65% |
| Expectancy per trade | 3.58% |
| Profit factor | 1.28 |
| Average holding (calendar days) | 107.2 |
| Average exposure | 94.23% |
| Turnover (1-way, per year) | 3.09 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -2.88% | 1.41 | 0.72 |
| E901-03 | -3.74% | 1.39 | 0.78 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.96% |
| 2011 | -7.81% |
| 2012 | 37.01% |
| 2013 | 37.76% |
| 2014 | -7.64% |
| 2015 | 2.45% |
| 2016 | 6.02% |
| 2017 | 8.91% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 80672.95 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0159 |
| cash_never_negative | pass | min cash/equity 0.0159 |
| fills_after_signal_date | pass | 0 violations, 20 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.196725525139577e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 818 orders vs QuantConnect Total Orders 818 |
| fills_match_harness_count | pass | downloaded fill events 818 vs harness-recorded fills 818 |
| commission_fixed_per_order | pass | 818 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `9d9a5e51c252c36ac8304e3feee8e9de70b2735d9216ae32bd96d630fe497f73`
- fills_sha256: `299183de70c08e874339935a1bbf9c403c51c20fd9bad6296ea4692b059e5956`
- trades_sha256: `812e041a7239ffe9cfb851ec6201750f2afb52db4b1755878e5a54d8c5fa4bbb`
