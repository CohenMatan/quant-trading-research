# E018-01 — S018 v1.0 (infrastructure)

Phase 3 PRIMARY NULL batch 1/5: the entire frozen search on within-date permutation worlds, seeds 1..100 (P3_spec.md section 12)

- **Status:** completed
- **Split:** AUDIT (2010-03-01 → 2017-12-31)
- **Commit:** `2d55c02ca874c301005bdd3d7307dad3047abb05` · **QC backtest:** `9cd376f5548833296b44d2941aa62a11` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-04T05:46:25Z · **runtime:** 2318s
- **Parameters:** `{'mode': 'search', 'slots': 10, 'hold': 63, 'worlds': [{'name': 'null1', 'seed': 1}, {'name': 'null2', 'seed': 2}, {'name': 'null3', 'seed': 3}, {'name': 'null4', 'seed': 4}, {'name': 'null5', 'seed': 5}, {'name': 'null6', 'seed': 6}, {'name': 'null7', 'seed': 7}, {'name': 'null8', 'seed': 8}, {'name': 'null9', 'seed': 9}, {'name': 'null10', 'seed': 10}, {'name': 'null11', 'seed': 11}, {'name': 'null12', 'seed': 12}, {'name': 'null13', 'seed': 13}, {'name': 'null14', 'seed': 14}, {'name': 'null15', 'seed': 15}, {'name': 'null16', 'seed': 16}, {'name': 'null17', 'seed': 17}, {'name': 'null18', 'seed': 18}, {'name': 'null19', 'seed': 19}, {'name': 'null20', 'seed': 20}, {'name': 'null21', 'seed': 21}, {'name': 'null22', 'seed': 22}, {'name': 'null23', 'seed': 23}, {'name': 'null24', 'seed': 24}, {'name': 'null25', 'seed': 25}, {'name': 'null26', 'seed': 26}, {'name': 'null27', 'seed': 27}, {'name': 'null28', 'seed': 28}, {'name': 'null29', 'seed': 29}, {'name': 'null30', 'seed': 30}, {'name': 'null31', 'seed': 31}, {'name': 'null32', 'seed': 32}, {'name': 'null33', 'seed': 33}, {'name': 'null34', 'seed': 34}, {'name': 'null35', 'seed': 35}, {'name': 'null36', 'seed': 36}, {'name': 'null37', 'seed': 37}, {'name': 'null38', 'seed': 38}, {'name': 'null39', 'seed': 39}, {'name': 'null40', 'seed': 40}, {'name': 'null41', 'seed': 41}, {'name': 'null42', 'seed': 42}, {'name': 'null43', 'seed': 43}, {'name': 'null44', 'seed': 44}, {'name': 'null45', 'seed': 45}, {'name': 'null46', 'seed': 46}, {'name': 'null47', 'seed': 47}, {'name': 'null48', 'seed': 48}, {'name': 'null49', 'seed': 49}, {'name': 'null50', 'seed': 50}, {'name': 'null51', 'seed': 51}, {'name': 'null52', 'seed': 52}, {'name': 'null53', 'seed': 53}, {'name': 'null54', 'seed': 54}, {'name': 'null55', 'seed': 55}, {'name': 'null56', 'seed': 56}, {'name': 'null57', 'seed': 57}, {'name': 'null58', 'seed': 58}, {'name': 'null59', 'seed': 59}, {'name': 'null60', 'seed': 60}, {'name': 'null61', 'seed': 61}, {'name': 'null62', 'seed': 62}, {'name': 'null63', 'seed': 63}, {'name': 'null64', 'seed': 64}, {'name': 'null65', 'seed': 65}, {'name': 'null66', 'seed': 66}, {'name': 'null67', 'seed': 67}, {'name': 'null68', 'seed': 68}, {'name': 'null69', 'seed': 69}, {'name': 'null70', 'seed': 70}, {'name': 'null71', 'seed': 71}, {'name': 'null72', 'seed': 72}, {'name': 'null73', 'seed': 73}, {'name': 'null74', 'seed': 74}, {'name': 'null75', 'seed': 75}, {'name': 'null76', 'seed': 76}, {'name': 'null77', 'seed': 77}, {'name': 'null78', 'seed': 78}, {'name': 'null79', 'seed': 79}, {'name': 'null80', 'seed': 80}, {'name': 'null81', 'seed': 81}, {'name': 'null82', 'seed': 82}, {'name': 'null83', 'seed': 83}, {'name': 'null84', 'seed': 84}, {'name': 'null85', 'seed': 85}, {'name': 'null86', 'seed': 86}, {'name': 'null87', 'seed': 87}, {'name': 'null88', 'seed': 88}, {'name': 'null89', 'seed': 89}, {'name': 'null90', 'seed': 90}, {'name': 'null91', 'seed': 91}, {'name': 'null92', 'seed': 92}, {'name': 'null93', 'seed': 93}, {'name': 'null94', 'seed': 94}, {'name': 'null95', 'seed': 95}, {'name': 'null96', 'seed': 96}, {'name': 'null97', 'seed': 97}, {'name': 'null98', 'seed': 98}, {'name': 'null99', 'seed': 99}, {'name': 'null100', 'seed': 100}]}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2017-12-29 (1975 trading days) |
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
| E900-07 | -13.75% | 0.00 | n/a |

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
| equity_nonempty | pass | 1975 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 100000.00 |
| equity_complete | pass | chart rows 1975 vs algorithm days 1975 |
| equity_matches_qc_tradeable_dates | pass | chart rows 1975 vs QuantConnect tradeableDates 1975 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 166 warm-up sessions |
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

- equity_sha256: `05ca54549c0c2bfb106014910eb3abcfabf4fb18d8299ae2e577e1ee04f5c512`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
