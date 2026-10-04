# E018-03 — S018 v1.0 (infrastructure)

Phase 3 PRIMARY NULL batch 3/5: the entire frozen search on within-date permutation worlds, seeds 201..300 (P3_spec.md section 12)

- **Status:** completed
- **Split:** AUDIT (2010-03-01 → 2017-12-31)
- **Commit:** `a5a39b778e7cb165690939f386d2d9beebfa64b5` · **QC backtest:** `031af5fd85e2fea41651014699f9ae2b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-04T07:01:35Z · **runtime:** 1963s
- **Parameters:** `{'mode': 'search', 'slots': 10, 'hold': 63, 'worlds': [{'name': 'null201', 'seed': 201}, {'name': 'null202', 'seed': 202}, {'name': 'null203', 'seed': 203}, {'name': 'null204', 'seed': 204}, {'name': 'null205', 'seed': 205}, {'name': 'null206', 'seed': 206}, {'name': 'null207', 'seed': 207}, {'name': 'null208', 'seed': 208}, {'name': 'null209', 'seed': 209}, {'name': 'null210', 'seed': 210}, {'name': 'null211', 'seed': 211}, {'name': 'null212', 'seed': 212}, {'name': 'null213', 'seed': 213}, {'name': 'null214', 'seed': 214}, {'name': 'null215', 'seed': 215}, {'name': 'null216', 'seed': 216}, {'name': 'null217', 'seed': 217}, {'name': 'null218', 'seed': 218}, {'name': 'null219', 'seed': 219}, {'name': 'null220', 'seed': 220}, {'name': 'null221', 'seed': 221}, {'name': 'null222', 'seed': 222}, {'name': 'null223', 'seed': 223}, {'name': 'null224', 'seed': 224}, {'name': 'null225', 'seed': 225}, {'name': 'null226', 'seed': 226}, {'name': 'null227', 'seed': 227}, {'name': 'null228', 'seed': 228}, {'name': 'null229', 'seed': 229}, {'name': 'null230', 'seed': 230}, {'name': 'null231', 'seed': 231}, {'name': 'null232', 'seed': 232}, {'name': 'null233', 'seed': 233}, {'name': 'null234', 'seed': 234}, {'name': 'null235', 'seed': 235}, {'name': 'null236', 'seed': 236}, {'name': 'null237', 'seed': 237}, {'name': 'null238', 'seed': 238}, {'name': 'null239', 'seed': 239}, {'name': 'null240', 'seed': 240}, {'name': 'null241', 'seed': 241}, {'name': 'null242', 'seed': 242}, {'name': 'null243', 'seed': 243}, {'name': 'null244', 'seed': 244}, {'name': 'null245', 'seed': 245}, {'name': 'null246', 'seed': 246}, {'name': 'null247', 'seed': 247}, {'name': 'null248', 'seed': 248}, {'name': 'null249', 'seed': 249}, {'name': 'null250', 'seed': 250}, {'name': 'null251', 'seed': 251}, {'name': 'null252', 'seed': 252}, {'name': 'null253', 'seed': 253}, {'name': 'null254', 'seed': 254}, {'name': 'null255', 'seed': 255}, {'name': 'null256', 'seed': 256}, {'name': 'null257', 'seed': 257}, {'name': 'null258', 'seed': 258}, {'name': 'null259', 'seed': 259}, {'name': 'null260', 'seed': 260}, {'name': 'null261', 'seed': 261}, {'name': 'null262', 'seed': 262}, {'name': 'null263', 'seed': 263}, {'name': 'null264', 'seed': 264}, {'name': 'null265', 'seed': 265}, {'name': 'null266', 'seed': 266}, {'name': 'null267', 'seed': 267}, {'name': 'null268', 'seed': 268}, {'name': 'null269', 'seed': 269}, {'name': 'null270', 'seed': 270}, {'name': 'null271', 'seed': 271}, {'name': 'null272', 'seed': 272}, {'name': 'null273', 'seed': 273}, {'name': 'null274', 'seed': 274}, {'name': 'null275', 'seed': 275}, {'name': 'null276', 'seed': 276}, {'name': 'null277', 'seed': 277}, {'name': 'null278', 'seed': 278}, {'name': 'null279', 'seed': 279}, {'name': 'null280', 'seed': 280}, {'name': 'null281', 'seed': 281}, {'name': 'null282', 'seed': 282}, {'name': 'null283', 'seed': 283}, {'name': 'null284', 'seed': 284}, {'name': 'null285', 'seed': 285}, {'name': 'null286', 'seed': 286}, {'name': 'null287', 'seed': 287}, {'name': 'null288', 'seed': 288}, {'name': 'null289', 'seed': 289}, {'name': 'null290', 'seed': 290}, {'name': 'null291', 'seed': 291}, {'name': 'null292', 'seed': 292}, {'name': 'null293', 'seed': 293}, {'name': 'null294', 'seed': 294}, {'name': 'null295', 'seed': 295}, {'name': 'null296', 'seed': 296}, {'name': 'null297', 'seed': 297}, {'name': 'null298', 'seed': 298}, {'name': 'null299', 'seed': 299}, {'name': 'null300', 'seed': 300}]}`
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
