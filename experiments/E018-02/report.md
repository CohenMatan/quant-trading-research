# E018-02 — S018 v1.0 (infrastructure)

Phase 3 PRIMARY NULL batch 2/5: the entire frozen search on within-date permutation worlds, seeds 101..200 (P3_spec.md section 12)

- **Status:** completed
- **Split:** AUDIT (2010-03-01 → 2017-12-31)
- **Commit:** `0800ce38a016e31b7a4e8d2f81a07f608ca075b8` · **QC backtest:** `3bddff389de4bdcd1816f00ce9563e0a` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-04T06:25:50Z · **runtime:** 2131s
- **Parameters:** `{'mode': 'search', 'slots': 10, 'hold': 63, 'worlds': [{'name': 'null101', 'seed': 101}, {'name': 'null102', 'seed': 102}, {'name': 'null103', 'seed': 103}, {'name': 'null104', 'seed': 104}, {'name': 'null105', 'seed': 105}, {'name': 'null106', 'seed': 106}, {'name': 'null107', 'seed': 107}, {'name': 'null108', 'seed': 108}, {'name': 'null109', 'seed': 109}, {'name': 'null110', 'seed': 110}, {'name': 'null111', 'seed': 111}, {'name': 'null112', 'seed': 112}, {'name': 'null113', 'seed': 113}, {'name': 'null114', 'seed': 114}, {'name': 'null115', 'seed': 115}, {'name': 'null116', 'seed': 116}, {'name': 'null117', 'seed': 117}, {'name': 'null118', 'seed': 118}, {'name': 'null119', 'seed': 119}, {'name': 'null120', 'seed': 120}, {'name': 'null121', 'seed': 121}, {'name': 'null122', 'seed': 122}, {'name': 'null123', 'seed': 123}, {'name': 'null124', 'seed': 124}, {'name': 'null125', 'seed': 125}, {'name': 'null126', 'seed': 126}, {'name': 'null127', 'seed': 127}, {'name': 'null128', 'seed': 128}, {'name': 'null129', 'seed': 129}, {'name': 'null130', 'seed': 130}, {'name': 'null131', 'seed': 131}, {'name': 'null132', 'seed': 132}, {'name': 'null133', 'seed': 133}, {'name': 'null134', 'seed': 134}, {'name': 'null135', 'seed': 135}, {'name': 'null136', 'seed': 136}, {'name': 'null137', 'seed': 137}, {'name': 'null138', 'seed': 138}, {'name': 'null139', 'seed': 139}, {'name': 'null140', 'seed': 140}, {'name': 'null141', 'seed': 141}, {'name': 'null142', 'seed': 142}, {'name': 'null143', 'seed': 143}, {'name': 'null144', 'seed': 144}, {'name': 'null145', 'seed': 145}, {'name': 'null146', 'seed': 146}, {'name': 'null147', 'seed': 147}, {'name': 'null148', 'seed': 148}, {'name': 'null149', 'seed': 149}, {'name': 'null150', 'seed': 150}, {'name': 'null151', 'seed': 151}, {'name': 'null152', 'seed': 152}, {'name': 'null153', 'seed': 153}, {'name': 'null154', 'seed': 154}, {'name': 'null155', 'seed': 155}, {'name': 'null156', 'seed': 156}, {'name': 'null157', 'seed': 157}, {'name': 'null158', 'seed': 158}, {'name': 'null159', 'seed': 159}, {'name': 'null160', 'seed': 160}, {'name': 'null161', 'seed': 161}, {'name': 'null162', 'seed': 162}, {'name': 'null163', 'seed': 163}, {'name': 'null164', 'seed': 164}, {'name': 'null165', 'seed': 165}, {'name': 'null166', 'seed': 166}, {'name': 'null167', 'seed': 167}, {'name': 'null168', 'seed': 168}, {'name': 'null169', 'seed': 169}, {'name': 'null170', 'seed': 170}, {'name': 'null171', 'seed': 171}, {'name': 'null172', 'seed': 172}, {'name': 'null173', 'seed': 173}, {'name': 'null174', 'seed': 174}, {'name': 'null175', 'seed': 175}, {'name': 'null176', 'seed': 176}, {'name': 'null177', 'seed': 177}, {'name': 'null178', 'seed': 178}, {'name': 'null179', 'seed': 179}, {'name': 'null180', 'seed': 180}, {'name': 'null181', 'seed': 181}, {'name': 'null182', 'seed': 182}, {'name': 'null183', 'seed': 183}, {'name': 'null184', 'seed': 184}, {'name': 'null185', 'seed': 185}, {'name': 'null186', 'seed': 186}, {'name': 'null187', 'seed': 187}, {'name': 'null188', 'seed': 188}, {'name': 'null189', 'seed': 189}, {'name': 'null190', 'seed': 190}, {'name': 'null191', 'seed': 191}, {'name': 'null192', 'seed': 192}, {'name': 'null193', 'seed': 193}, {'name': 'null194', 'seed': 194}, {'name': 'null195', 'seed': 195}, {'name': 'null196', 'seed': 196}, {'name': 'null197', 'seed': 197}, {'name': 'null198', 'seed': 198}, {'name': 'null199', 'seed': 199}, {'name': 'null200', 'seed': 200}]}`
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
