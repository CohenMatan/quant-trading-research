# E984-05 — X984 v1.0 (infrastructure)

Phase 3 engine OUTPUT / BATCH CANARY at the frozen batch size: 1 identity + 99 permutation worlds of DUMMY configurations (seeds as E984-03, so identical books are expected), publishing every world's summary and the first world's 1,533 per-configuration lines in the exact search-mode format (output-size test). Timings, memory and output only.

- **Status:** completed
- **Split:** AUDIT (2010-03-01 → 2017-12-31)
- **Commit:** `971c156d68489032953ec871127b7917807496d1` · **QC backtest:** `719be67ff7106635cb01809ffeeebb08` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-04T03:55:53Z · **runtime:** 2171s
- **Parameters:** `{'mode': 'canary', 'slots': 10, 'hold': 63, 'worlds': [{'name': 'identity'}, {'name': 'perm1', 'seed': 901}, {'name': 'perm2', 'seed': 902}, {'name': 'perm3', 'seed': 903}, {'name': 'perm4', 'seed': 904}, {'name': 'perm5', 'seed': 905}, {'name': 'perm6', 'seed': 906}, {'name': 'perm7', 'seed': 907}, {'name': 'perm8', 'seed': 908}, {'name': 'perm9', 'seed': 909}, {'name': 'perm10', 'seed': 910}, {'name': 'perm11', 'seed': 911}, {'name': 'perm12', 'seed': 912}, {'name': 'perm13', 'seed': 913}, {'name': 'perm14', 'seed': 914}, {'name': 'perm15', 'seed': 915}, {'name': 'perm16', 'seed': 916}, {'name': 'perm17', 'seed': 917}, {'name': 'perm18', 'seed': 918}, {'name': 'perm19', 'seed': 919}, {'name': 'perm20', 'seed': 920}, {'name': 'perm21', 'seed': 921}, {'name': 'perm22', 'seed': 922}, {'name': 'perm23', 'seed': 923}, {'name': 'perm24', 'seed': 924}, {'name': 'perm25', 'seed': 925}, {'name': 'perm26', 'seed': 926}, {'name': 'perm27', 'seed': 927}, {'name': 'perm28', 'seed': 928}, {'name': 'perm29', 'seed': 929}, {'name': 'perm30', 'seed': 930}, {'name': 'perm31', 'seed': 931}, {'name': 'perm32', 'seed': 932}, {'name': 'perm33', 'seed': 933}, {'name': 'perm34', 'seed': 934}, {'name': 'perm35', 'seed': 935}, {'name': 'perm36', 'seed': 936}, {'name': 'perm37', 'seed': 937}, {'name': 'perm38', 'seed': 938}, {'name': 'perm39', 'seed': 939}, {'name': 'perm40', 'seed': 940}, {'name': 'perm41', 'seed': 941}, {'name': 'perm42', 'seed': 942}, {'name': 'perm43', 'seed': 943}, {'name': 'perm44', 'seed': 944}, {'name': 'perm45', 'seed': 945}, {'name': 'perm46', 'seed': 946}, {'name': 'perm47', 'seed': 947}, {'name': 'perm48', 'seed': 948}, {'name': 'perm49', 'seed': 949}, {'name': 'perm50', 'seed': 950}, {'name': 'perm51', 'seed': 951}, {'name': 'perm52', 'seed': 952}, {'name': 'perm53', 'seed': 953}, {'name': 'perm54', 'seed': 954}, {'name': 'perm55', 'seed': 955}, {'name': 'perm56', 'seed': 956}, {'name': 'perm57', 'seed': 957}, {'name': 'perm58', 'seed': 958}, {'name': 'perm59', 'seed': 959}, {'name': 'perm60', 'seed': 960}, {'name': 'perm61', 'seed': 961}, {'name': 'perm62', 'seed': 962}, {'name': 'perm63', 'seed': 963}, {'name': 'perm64', 'seed': 964}, {'name': 'perm65', 'seed': 965}, {'name': 'perm66', 'seed': 966}, {'name': 'perm67', 'seed': 967}, {'name': 'perm68', 'seed': 968}, {'name': 'perm69', 'seed': 969}, {'name': 'perm70', 'seed': 970}, {'name': 'perm71', 'seed': 971}, {'name': 'perm72', 'seed': 972}, {'name': 'perm73', 'seed': 973}, {'name': 'perm74', 'seed': 974}, {'name': 'perm75', 'seed': 975}, {'name': 'perm76', 'seed': 976}, {'name': 'perm77', 'seed': 977}, {'name': 'perm78', 'seed': 978}, {'name': 'perm79', 'seed': 979}, {'name': 'perm80', 'seed': 980}, {'name': 'perm81', 'seed': 981}, {'name': 'perm82', 'seed': 982}, {'name': 'perm83', 'seed': 983}, {'name': 'perm84', 'seed': 984}, {'name': 'perm85', 'seed': 985}, {'name': 'perm86', 'seed': 986}, {'name': 'perm87', 'seed': 987}, {'name': 'perm88', 'seed': 988}, {'name': 'perm89', 'seed': 989}, {'name': 'perm90', 'seed': 990}, {'name': 'perm91', 'seed': 991}, {'name': 'perm92', 'seed': 992}, {'name': 'perm93', 'seed': 993}, {'name': 'perm94', 'seed': 994}, {'name': 'perm95', 'seed': 995}, {'name': 'perm96', 'seed': 996}, {'name': 'perm97', 'seed': 997}, {'name': 'perm98', 'seed': 998}, {'name': 'perm99', 'seed': 999}], 'publish_format': True}`
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
