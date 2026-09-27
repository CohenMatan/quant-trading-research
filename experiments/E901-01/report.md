# E901-01 — B901 v1.0 (benchmark)

Benchmark: equal-weight eligible >= $2B universe, monthly rebalance, 25% tolerance band. Starts 2010-01-04: QC's new Morningstar dataset has no MarketCap before ~2009 (E951-02/03).

- **Status:** completed
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `8773b89b62a627e12efd2198ff2c93590d5000bf` · **QC backtest:** `07db1055161beb4c82988fbd1c274416` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-27T21:14:28Z · **runtime:** 391s
- **Parameters:** `{'band': 0.25, 'shard_count': 1, 'shard_index': 0}`
- **Costs:** `{'slippage_bps': 10, 'commission': 'IB fixed via LEAN InteractiveBrokersFeeModel: $0.005/share, $1 min, 1% max'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 14.26% |
| Annualised volatility | 18.15% |
| Sharpe (rf = 0) | 0.83 |
| Sortino | 1.14 |
| Max drawdown | -38.07% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.37 |
| Worst year | -8.01% |
| Worst month | -18.63% |
| Closed trades | 3479 |
| Win rate | 22.62% |
| Average winner | 33.83% |
| Average loser | -16.03% |
| Expectancy per trade | -4.75% |
| Profit factor | 0.52 |
| Average holding (calendar days) | 355.3 |
| Average exposure | 96.60% |
| Turnover (1-way, per year) | 0.40 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2014-12-31 (1258 trading days) |
| CAGR | 17.38% |
| Annualised volatility | 17.12% |
| Sharpe (rf = 0) | 1.02 |
| Sortino | 1.45 |
| Max drawdown | -22.18% |
| Longest drawdown (trading days) | 201 |
| Calmar | 0.78 |
| Worst year | 0.59% |
| Worst month | -8.56% |
| Average exposure | 95.81% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2015-01-02 → 2021-12-31 (1763 trading days) |
| CAGR | 12.10% |
| Annualised volatility | 18.87% |
| Sharpe (rf = 0) | 0.70 |
| Sortino | 0.96 |
| Max drawdown | -38.07% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.32 |
| Worst year | -8.01% |
| Worst month | -18.63% |
| Average exposure | 97.15% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 23.92% |
| 2011 | 0.59% |
| 2012 | 17.59% |
| 2013 | 36.13% |
| 2014 | 11.50% |
| 2015 | -2.67% |
| 2016 | 14.65% |
| 2017 | 19.92% |
| 2018 | -8.01% |
| 2019 | 27.59% |
| 2020 | 21.62% |
| 2021 | 16.34% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 9674372.85 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| no_leverage | pass | min cash/equity 0.0186 |
| cash_never_negative | pass | min cash/equity 0.0186 |
| fills_after_signal_date | pass | 0 violations, 379 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.5852410018675075e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `4c760f80bd5a999a88decbed4fd7bfbdf35801f2c857c8793748020a2b5e5b98`
- fills_sha256: `de134b3cae72a8610d41dfcbc8ef43e333d921e2cc132d9a5687afb585c74ac3`
- trades_sha256: `aaf30a09d2532a2fba889a6d83f97e89af8b5dea523cde89b6ca6dda15c00dd5`
