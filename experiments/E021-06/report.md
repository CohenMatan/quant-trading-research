# E021-06 — S021 v1.0 (research)

H020 REAL EVALUATION, ONCE: the frozen structured chart score on the 2010-2017 weekly decisions (4-week total-shareholder-return responses), judged with the pinned c_ic / c_inc (gates G1-G5); then the descriptives, the NON-GATING SECTOR DIAGNOSTIC and the NON-GATING 13-week diagnostic. No portfolio.

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-31)
- **Commit:** `0995ed98b3035e18833555ea382571d067577280` · **QC backtest:** `539d5e2f6a19eae395dc59636132baa0` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-05T15:59:26Z · **runtime:** 2273s
- **Parameters:** `{'mode': 'real', 'c_ic': 2.328878115, 'c_inc': 2.264744985, 'threshold_commit': '55bf6634150b6cc8b068177e73a5c3b6a5d6c3ac', 'null_result_sha256': '4b26be842ce499696a82e29c8ddf84d386f590597f4f943f185d645d84be4e13', 'spec_sha256': '48e6feccbdb734d6918e28f332fe34154a529122bb6ed9ff3c76a95edca22b06', 'addendum_sha256': 'c653513cb9ec754270c92ac6c7828f5dae45c1bc4882d94f6552d3a883186498', 'chart_panel_sha256': 'aa5d3c51fb1203584adfc3604508fcfb0537af7f630381c51a11e34492cbb7d9'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
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
| E900-07 | -13.34% | 0.00 | n/a |

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
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 128 warm-up sessions |
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

- equity_sha256: `a4356a5a198e161e7a6d926d982cfb2aa5b5164c0ea278dd4d893a60261cac72`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
