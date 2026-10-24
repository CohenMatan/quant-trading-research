# E006-05 — S006 v1.3 (research)

H006X Experiment B (D304): H006 v1.0 entry, ranking, chandelier K 3.0 and 10 slots WITHOUT the 60-session time stop on QuantConnect's default build, DEV 2010-01-04 .. 2021-12-31. EXPLORATORY; H006 stays REJECTED.

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `ed6f3b7944766fbb610622109016a6faa8fb170d` · **QC backtest:** `98ac04d9e98365cee0e91c382a330561` · **LEAN:** v2.5.0.0.18203 · **run:** 2026-10-24T18:04:34Z · **runtime:** 977s
- **Parameters:** `{'n': 55, 'vol_mult': 1.5, 'use_volume': True, 'k': 3.0, 'slots': 10, 'time_stop': None, 'h006x_spec_sha256': 'ae016962e71686aacc383b4da7336fe166ecc9c14b68eb17bbcba5192d42fb5e', 'h006x_code_sha256': {'main.py': 'da3e810179df7288892a2b8210c85471b3659beed89cac5aaa2be7d5f6efd65e', 'signals.py': '91ada940e221f3aa558e29223ccd92f4cbb83f3c16935e21cf86f96487c46a0f'}}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 12.82% |
| Annualised volatility | 16.45% |
| Sharpe (rf = 0) | 0.82 |
| Sortino | 1.14 |
| Max drawdown | -27.41% |
| Longest drawdown (trading days) | 271 |
| Calmar | 0.47 |
| Worst year | -10.87% |
| Worst month | -11.31% |
| Closed trades | 667 |
| Win rate | 47.08% |
| Average winner | 12.30% |
| Average loser | -6.83% |
| Expectancy per trade | 2.17% |
| Profit factor | 1.44 |
| Average holding (calendar days) | 62.4 |
| Average exposure | 91.93% |
| Turnover (1-way, per year) | 5.18 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-08 | -1.77% | 0.63 | 0.63 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 28.44% |
| 2011 | -10.87% |
| 2012 | 23.37% |
| 2013 | 27.34% |
| 2014 | 7.55% |
| 2015 | 6.44% |
| 2016 | 26.16% |
| 2017 | 21.65% |
| 2018 | -3.02% |
| 2019 | 24.02% |
| 2020 | 12.37% |
| 2021 | -0.60% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96315.08 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.021205; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 26 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0818751887864673e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1346 orders vs QuantConnect Total Orders 1346 |
| fills_match_harness_count | pass | downloaded fill events 1344 vs harness-recorded fills 1344 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1344 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `76dd5f1cbe4ef14664bcbf301ca3e5de76620a3778ff4faa74b84941b923356d`
- fills_sha256: `135b92dbfd480d4260ddf6f1e5aa1667d29e5d9194cd511e1ac20f5bb6745bfb`
- trades_sha256: `b6c8d9b261bdd7d92f6a397f0821a1d5cb21ae4c327b2fed8385f8d94dcfb3c8`
