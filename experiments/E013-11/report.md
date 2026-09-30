# E013-11 — S013 v1.0 (sizing)

C03 S1 ($200K, 15 positions) of E013-02. Diagnostic, not a trial. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `9d5012f967b65670bd059a08bdaf0cffdeda45e7` · **QC backtest:** `9e06b49836b1bc36ce1731d7b9b264d9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T18:04:36Z · **runtime:** 460s
- **Parameters:** `{'q': 0.2, 'stat': 'max', 'seed': 2, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.21% |
| Annualised volatility | 13.63% |
| Sharpe (rf = 0) | 0.85 |
| Sortino | 1.19 |
| Max drawdown | -19.39% |
| Longest drawdown (trading days) | 273 |
| Calmar | 0.58 |
| Worst year | -1.25% |
| Worst month | -9.23% |
| Closed trades | 482 |
| Win rate | 62.86% |
| Average winner | 9.89% |
| Average loser | -9.85% |
| Expectancy per trade | 2.56% |
| Profit factor | 1.60 |
| Average holding (calendar days) | 87.8 |
| Average exposure | 83.97% |
| Turnover (1-way, per year) | 3.57 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.13% | 0.86 | 0.90 |
| E901-07 | -2.72% | 0.81 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 19.61% |
| 2011 | -1.25% |
| 2012 | 17.91% |
| 2013 | 27.42% |
| 2014 | 9.01% |
| 2015 | 4.01% |
| 2016 | 9.75% |
| 2017 | 5.74% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 194902.57 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.098921; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 6 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 979 orders vs QuantConnect Total Orders 979 |
| fills_match_harness_count | pass | downloaded fill events 979 vs harness-recorded fills 979 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 979 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `807426fe0ed5f968c41829dd0a56fe89679165b527ea803e3a5593d129d13355`
- fills_sha256: `de9de37ec71c20469abb1472052748ed96ed8bdafa8765b6d7c8fabd08edba4a`
- trades_sha256: `af13c8a571a4550120d84cd88d4984fd4dc4f0ff121cdfae9a24ba921f1b1206`
