# E995-04 — X995 v1.0 (infrastructure)

P7-CP5c NEW-DATASET (re-run of E995-01 / E995-03, which failed at upload: 50-file project limit, then stale files left in the project; table trimmed to periods <= 2017-12) FUNDAMENTAL-TIMING PROBE (owner D184; infrastructure, QuantConnect default build, recorded): X971 v1.1 SEC verification on the X971 sample + pre-registered S2 (480 companies), schema scan of every fundamental object (timing-like members, every period window), per-security changes of every candidate timing field, aggregated market-cap check. Dates, identifiers and vendor/SEC value RATIOS only; no orders, no returns; 2009-06 .. 2017-12.

- **Status:** integrity_failed
- **Split:** AUDIT (2009-06-01 → 2017-12-31)
- **Commit:** `dae181e6d2e4524e37487ef18a234fba800012f4` · **QC backtest:** `7326b64ea8d261b4f1bd8b767a611e22` · **LEAN:** v2.5.0.0.18178 · **run:** 2026-10-10T12:57:23Z · **runtime:** 45s
- **Parameters:** `{}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2009-06-01 → 2009-10-07 (91 trading days) |
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
| E900-07 | n/a | n/a | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2009 | 0.00% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 91 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2009-06-01..2009-10-07 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 91 vs algorithm days 91 |
| equity_matches_qc_tradeable_dates | FAIL | chart rows 91 vs QuantConnect tradeableDates 2163 |
| no_leverage | pass | min cash/equity 1.000000; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=0.0 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 0 orders vs QuantConnect Total Orders 0 |
| fills_match_harness_count | pass | downloaded fill events 0 vs harness-recorded fills 0 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | no fills downloaded; harness recorded 0 fills |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `24b29d32e6e4ea8c7dbb43511dcc64650a098749bec8c2b37feb6e269be3bde3`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
