# E900-03 — B900 v1.0 (benchmark)

Benchmark: SPY buy-and-hold, dividends reinvested monthly. Official 2010 scheme (D034): IS+VAL 2010-01-04..2021-12-31.

- **Status:** completed
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `534ae34f05c9b71e53178115e1fe7e770585c68c` · **QC backtest:** `a052fa890efc19b9f1b9025d5bd27f3a` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T10:38:18Z · **runtime:** 19s
- **Parameters:** `{'weight': 0.98}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 14.56% |
| Annualised volatility | 16.59% |
| Sharpe (rf = 0) | 0.90 |
| Sortino | 1.26 |
| Max drawdown | -33.05% |
| Longest drawdown (trading days) | 192 |
| Calmar | 0.44 |
| Worst year | -4.46% |
| Worst month | -12.26% |
| Closed trades | 0 |
| Win rate | n/a |
| Average winner | n/a |
| Average loser | n/a |
| Expectancy per trade | n/a |
| Profit factor | n/a |
| Average holding (calendar days) | n/a |
| Average exposure | 97.86% |
| Turnover (1-way, per year) | 0.03 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.29% |
| Annualised volatility | 14.35% |
| Sharpe (rf = 0) | 0.94 |
| Sortino | 1.33 |
| Max drawdown | -18.30% |
| Longest drawdown (trading days) | 192 |
| Calmar | 0.73 |
| Worst year | 1.28% |
| Worst month | -7.76% |
| Average exposure | 97.83% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 16.98% |
| Annualised volatility | 20.34% |
| Sharpe (rf = 0) | 0.87 |
| Sortino | 1.20 |
| Max drawdown | -33.05% |
| Longest drawdown (trading days) | 139 |
| Calmar | 0.51 |
| Worst year | -5.13% |
| Worst month | -12.26% |
| Average exposure | 97.91% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.80% |
| 2011 | 1.81% |
| 2012 | 15.66% |
| 2013 | 31.38% |
| 2014 | 13.16% |
| 2015 | 1.28% |
| 2016 | 11.71% |
| 2017 | 21.18% |
| 2018 | -4.46% |
| 2019 | 30.49% |
| 2020 | 18.00% |
| 2021 | 28.05% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91114.72 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.0173 |
| cash_never_negative | pass | min cash/equity 0.0173 |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.729208065967196e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| commission_fixed_per_order | pass | 100 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `43400bf9abfc5a3626dd02c6917cbe82f8790c79cad1b0708f44ebba5bc9bb33`
- fills_sha256: `6f347615023b2993d3d1d5e8eca4cc00e20a23f363351d2931edc65eb7a060a4`
- trades_sha256: `82b239f94545be02ee368182826447ed34911f937ebd517c1c6d6e26b0b9afd3`
