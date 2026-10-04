# E018-04 — S018 v1.0 (infrastructure)

Phase 3 PRIMARY NULL batch 4/5: the entire frozen search on within-date permutation worlds, seeds 301..400 (P3_spec.md section 12)

- **Status:** completed
- **Split:** AUDIT (2010-03-01 → 2017-12-31)
- **Commit:** `6c7dd09338e8dcbf61b55ce5fece42c10ab458d5` · **QC backtest:** `7766da073b9840426a34b0bd404da762` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-04T07:34:32Z · **runtime:** 1960s
- **Parameters:** `{'mode': 'search', 'slots': 10, 'hold': 63, 'worlds': [{'name': 'null301', 'seed': 301}, {'name': 'null302', 'seed': 302}, {'name': 'null303', 'seed': 303}, {'name': 'null304', 'seed': 304}, {'name': 'null305', 'seed': 305}, {'name': 'null306', 'seed': 306}, {'name': 'null307', 'seed': 307}, {'name': 'null308', 'seed': 308}, {'name': 'null309', 'seed': 309}, {'name': 'null310', 'seed': 310}, {'name': 'null311', 'seed': 311}, {'name': 'null312', 'seed': 312}, {'name': 'null313', 'seed': 313}, {'name': 'null314', 'seed': 314}, {'name': 'null315', 'seed': 315}, {'name': 'null316', 'seed': 316}, {'name': 'null317', 'seed': 317}, {'name': 'null318', 'seed': 318}, {'name': 'null319', 'seed': 319}, {'name': 'null320', 'seed': 320}, {'name': 'null321', 'seed': 321}, {'name': 'null322', 'seed': 322}, {'name': 'null323', 'seed': 323}, {'name': 'null324', 'seed': 324}, {'name': 'null325', 'seed': 325}, {'name': 'null326', 'seed': 326}, {'name': 'null327', 'seed': 327}, {'name': 'null328', 'seed': 328}, {'name': 'null329', 'seed': 329}, {'name': 'null330', 'seed': 330}, {'name': 'null331', 'seed': 331}, {'name': 'null332', 'seed': 332}, {'name': 'null333', 'seed': 333}, {'name': 'null334', 'seed': 334}, {'name': 'null335', 'seed': 335}, {'name': 'null336', 'seed': 336}, {'name': 'null337', 'seed': 337}, {'name': 'null338', 'seed': 338}, {'name': 'null339', 'seed': 339}, {'name': 'null340', 'seed': 340}, {'name': 'null341', 'seed': 341}, {'name': 'null342', 'seed': 342}, {'name': 'null343', 'seed': 343}, {'name': 'null344', 'seed': 344}, {'name': 'null345', 'seed': 345}, {'name': 'null346', 'seed': 346}, {'name': 'null347', 'seed': 347}, {'name': 'null348', 'seed': 348}, {'name': 'null349', 'seed': 349}, {'name': 'null350', 'seed': 350}, {'name': 'null351', 'seed': 351}, {'name': 'null352', 'seed': 352}, {'name': 'null353', 'seed': 353}, {'name': 'null354', 'seed': 354}, {'name': 'null355', 'seed': 355}, {'name': 'null356', 'seed': 356}, {'name': 'null357', 'seed': 357}, {'name': 'null358', 'seed': 358}, {'name': 'null359', 'seed': 359}, {'name': 'null360', 'seed': 360}, {'name': 'null361', 'seed': 361}, {'name': 'null362', 'seed': 362}, {'name': 'null363', 'seed': 363}, {'name': 'null364', 'seed': 364}, {'name': 'null365', 'seed': 365}, {'name': 'null366', 'seed': 366}, {'name': 'null367', 'seed': 367}, {'name': 'null368', 'seed': 368}, {'name': 'null369', 'seed': 369}, {'name': 'null370', 'seed': 370}, {'name': 'null371', 'seed': 371}, {'name': 'null372', 'seed': 372}, {'name': 'null373', 'seed': 373}, {'name': 'null374', 'seed': 374}, {'name': 'null375', 'seed': 375}, {'name': 'null376', 'seed': 376}, {'name': 'null377', 'seed': 377}, {'name': 'null378', 'seed': 378}, {'name': 'null379', 'seed': 379}, {'name': 'null380', 'seed': 380}, {'name': 'null381', 'seed': 381}, {'name': 'null382', 'seed': 382}, {'name': 'null383', 'seed': 383}, {'name': 'null384', 'seed': 384}, {'name': 'null385', 'seed': 385}, {'name': 'null386', 'seed': 386}, {'name': 'null387', 'seed': 387}, {'name': 'null388', 'seed': 388}, {'name': 'null389', 'seed': 389}, {'name': 'null390', 'seed': 390}, {'name': 'null391', 'seed': 391}, {'name': 'null392', 'seed': 392}, {'name': 'null393', 'seed': 393}, {'name': 'null394', 'seed': 394}, {'name': 'null395', 'seed': 395}, {'name': 'null396', 'seed': 396}, {'name': 'null397', 'seed': 397}, {'name': 'null398', 'seed': 398}, {'name': 'null399', 'seed': 399}, {'name': 'null400', 'seed': 400}]}`
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
