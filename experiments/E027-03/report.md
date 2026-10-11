# E027-03 — S027 v1.0 (infrastructure)

P10-CP1 (owner D204): H025 canary (S027 canary mode): ledger / review / identity / calendar / cooldown / entry and exit timing checks, SPY total return and corporate actions against fresh histories on NON-event windows, next-open timing on synthetic prices, statistic / gates / null machinery on SYNTHETIC responses only. No real H025 response computed. Infrastructure. Default build (recorded).

- **Status:** completed
- **Split:** AUDIT (2011-01-03 → 2017-12-31)
- **Commit:** `dd42328f38a2ae5c92f63e5b239bac8976ff64ed` · **QC backtest:** `3909c6c03d768e17bd87f553fd5d4a25` · **LEAN:** v2.5.0.0.18178 · **run:** 2026-10-11T16:13:53Z · **runtime:** 535s
- **Parameters:** `{'mode': 'canary', 'spec_sha256': 'f250e50ebc0dcfb0c4b0a176e9ad0e5bb3e5a850fdefef65bf9413724fb04768', 'pred_code_sha256': 'bc6fd8e83e7c105e50bbd05fabb23c61ac5229216af6599320962195d83f8da5', 'h025_code_sha256': '817231ca33cac481cbd7eb770bc064dd830f40a952ff8b6bfb8c2549aa68876b', 'payload_sha256': '92632242eca7706421560002a20b297c79fab87f2c51ba3f7569f8147c0441ee', 'calendar_sha256': '53ed9ff45b7c5146205b9163c6d5322ba90ebc8f1980e838219391cdb7746958', 'in_host_ledger_sha256': '7adbb0b9d010a7435bf62aa1ca85683061d54a9db448c69d4106ba9228be18fe'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': False}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2011-01-03 → 2017-12-29 (1761 trading days) |
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
| E900-07 | -13.19% | 0.00 | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
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
| equity_nonempty | pass | 1761 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2011-01-03..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 1761 vs algorithm days 1761 |
| equity_matches_qc_tradeable_dates | pass | chart rows 1761 vs QuantConnect tradeableDates 1761 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 632 warm-up sessions |
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

- equity_sha256: `fd2976e77f7ef0df9c799d33912f39ede4176238baf836e80d3fb8d9ade279b6`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
