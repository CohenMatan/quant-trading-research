# E018-05 — S018 v1.0 (infrastructure)

Phase 3 PRIMARY NULL batch 5/5: the entire frozen search on within-date permutation worlds, seeds 401..500 (P3_spec.md section 12)

- **Status:** completed
- **Split:** AUDIT (2010-03-01 → 2017-12-31)
- **Commit:** `8d67a3b3d35dc8e283afcd4867bbd78b61a047a5` · **QC backtest:** `061bc0b70ab254ea84b8c5c4d94bbbd9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-04T08:07:37Z · **runtime:** 1960s
- **Parameters:** `{'mode': 'search', 'slots': 10, 'hold': 63, 'worlds': [{'name': 'null401', 'seed': 401}, {'name': 'null402', 'seed': 402}, {'name': 'null403', 'seed': 403}, {'name': 'null404', 'seed': 404}, {'name': 'null405', 'seed': 405}, {'name': 'null406', 'seed': 406}, {'name': 'null407', 'seed': 407}, {'name': 'null408', 'seed': 408}, {'name': 'null409', 'seed': 409}, {'name': 'null410', 'seed': 410}, {'name': 'null411', 'seed': 411}, {'name': 'null412', 'seed': 412}, {'name': 'null413', 'seed': 413}, {'name': 'null414', 'seed': 414}, {'name': 'null415', 'seed': 415}, {'name': 'null416', 'seed': 416}, {'name': 'null417', 'seed': 417}, {'name': 'null418', 'seed': 418}, {'name': 'null419', 'seed': 419}, {'name': 'null420', 'seed': 420}, {'name': 'null421', 'seed': 421}, {'name': 'null422', 'seed': 422}, {'name': 'null423', 'seed': 423}, {'name': 'null424', 'seed': 424}, {'name': 'null425', 'seed': 425}, {'name': 'null426', 'seed': 426}, {'name': 'null427', 'seed': 427}, {'name': 'null428', 'seed': 428}, {'name': 'null429', 'seed': 429}, {'name': 'null430', 'seed': 430}, {'name': 'null431', 'seed': 431}, {'name': 'null432', 'seed': 432}, {'name': 'null433', 'seed': 433}, {'name': 'null434', 'seed': 434}, {'name': 'null435', 'seed': 435}, {'name': 'null436', 'seed': 436}, {'name': 'null437', 'seed': 437}, {'name': 'null438', 'seed': 438}, {'name': 'null439', 'seed': 439}, {'name': 'null440', 'seed': 440}, {'name': 'null441', 'seed': 441}, {'name': 'null442', 'seed': 442}, {'name': 'null443', 'seed': 443}, {'name': 'null444', 'seed': 444}, {'name': 'null445', 'seed': 445}, {'name': 'null446', 'seed': 446}, {'name': 'null447', 'seed': 447}, {'name': 'null448', 'seed': 448}, {'name': 'null449', 'seed': 449}, {'name': 'null450', 'seed': 450}, {'name': 'null451', 'seed': 451}, {'name': 'null452', 'seed': 452}, {'name': 'null453', 'seed': 453}, {'name': 'null454', 'seed': 454}, {'name': 'null455', 'seed': 455}, {'name': 'null456', 'seed': 456}, {'name': 'null457', 'seed': 457}, {'name': 'null458', 'seed': 458}, {'name': 'null459', 'seed': 459}, {'name': 'null460', 'seed': 460}, {'name': 'null461', 'seed': 461}, {'name': 'null462', 'seed': 462}, {'name': 'null463', 'seed': 463}, {'name': 'null464', 'seed': 464}, {'name': 'null465', 'seed': 465}, {'name': 'null466', 'seed': 466}, {'name': 'null467', 'seed': 467}, {'name': 'null468', 'seed': 468}, {'name': 'null469', 'seed': 469}, {'name': 'null470', 'seed': 470}, {'name': 'null471', 'seed': 471}, {'name': 'null472', 'seed': 472}, {'name': 'null473', 'seed': 473}, {'name': 'null474', 'seed': 474}, {'name': 'null475', 'seed': 475}, {'name': 'null476', 'seed': 476}, {'name': 'null477', 'seed': 477}, {'name': 'null478', 'seed': 478}, {'name': 'null479', 'seed': 479}, {'name': 'null480', 'seed': 480}, {'name': 'null481', 'seed': 481}, {'name': 'null482', 'seed': 482}, {'name': 'null483', 'seed': 483}, {'name': 'null484', 'seed': 484}, {'name': 'null485', 'seed': 485}, {'name': 'null486', 'seed': 486}, {'name': 'null487', 'seed': 487}, {'name': 'null488', 'seed': 488}, {'name': 'null489', 'seed': 489}, {'name': 'null490', 'seed': 490}, {'name': 'null491', 'seed': 491}, {'name': 'null492', 'seed': 492}, {'name': 'null493', 'seed': 493}, {'name': 'null494', 'seed': 494}, {'name': 'null495', 'seed': 495}, {'name': 'null496', 'seed': 496}, {'name': 'null497', 'seed': 497}, {'name': 'null498', 'seed': 498}, {'name': 'null499', 'seed': 499}, {'name': 'null500', 'seed': 500}]}`
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
