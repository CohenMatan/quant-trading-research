# E021-01 — S021 v1.0 (infrastructure)

H020 NULL worlds 1-1000 of 5,000 (unstratified identity-tethered within-date permutation of the chart side, no self-matches; the complete procedure per world; H020_spec.md section 18). Publishes per-world null statistics only. Infrastructure (never a strategy trial).

- **Status:** integrity_failed
- **Split:** AUDIT (2010-01-04 → 2017-12-31)
- **Commit:** `c6e716e07aba95ec1e751d08c407c3b753a01dd2` · **QC backtest:** `9d80b52bf177b4a67b36df17bfdab566` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-05T11:55:30Z · **runtime:** 411s
- **Parameters:** `{'mode': 'null', 'seeds': [1, 1000]}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-07-05 (1889 trading days) |
| CAGR | 0.00% |
| Annualised volatility | 0.00% |
| Sharpe (rf = 0) | n/a |
| Sortino | n/a |
| Max drawdown | 0.00% |
| Longest drawdown (trading days) | 0 |
| Calmar | n/a |
| Worst year | 0.00% |
| Worst month | 0.00% |
| Closed trades | 0 |
| Win rate | n/a |
| Average winner | n/a |
| Average loser | n/a |
| Expectancy per trade | n/a |
| Profit factor | n/a |
| Average holding (calendar days) | n/a |
| Average exposure | 0.00% |
| Turnover (1-way, per year) | 0.00 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -12.71% | 0.00 | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 0.00% |
| 2011 | 0.00% |
| 2012 | 0.00% |
| 2013 | 0.00% |
| 2014 | 0.00% |
| 2015 | 0.00% |
| 2016 | 0.00% |
| 2017 | 0.00% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 1889 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-07-05 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | FAIL | chart rows 1889 vs algorithm days None |
| equity_matches_qc_tradeable_dates | FAIL | chart rows 1889 vs QuantConnect tradeableDates 2141 |
| no_leverage | pass | min cash/equity 1.000000; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | FAIL | violations=None max_fill_dev=None |
| harness_no_short | FAIL | negative_qty=None |
| no_invalid_orders | pass | invalid=None |
| summary_present | FAIL | QRSUMMARY log line parsed |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| commission_fixed_per_order | pass | no fills downloaded; harness recorded None fills |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `cb8173d3063b80023d4da444c56c26df76898a20c6b5ad4f4411103d1d9f542e`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
