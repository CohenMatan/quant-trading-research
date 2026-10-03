# E017-05 — S017 v1.0 (benchmark)

P2 H017 random-event control seed 3: identical code path, timing, sizing, holding, costs and daily k_t as E017-01; only the selection differs. Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `9f5d99a62f4dfb4542bd275264c07c8335c1e380` · **QC backtest:** `394617c3d6e3928d0d6563bfee5da529` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T19:14:51Z · **runtime:** 767s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'random', 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 11.14% |
| Annualised volatility | 19.52% |
| Sharpe (rf = 0) | 0.64 |
| Sortino | 0.89 |
| Max drawdown | -45.03% |
| Longest drawdown (trading days) | 704 |
| Calmar | 0.25 |
| Worst year | -18.83% |
| Worst month | -22.41% |
| Closed trades | 461 |
| Win rate | 60.74% |
| Average winner | 11.36% |
| Average loser | -10.18% |
| Expectancy per trade | 2.90% |
| Profit factor | 1.62 |
| Average holding (calendar days) | 87.0 |
| Average exposure | 88.89% |
| Turnover (1-way, per year) | 3.71 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.74% | 1.02 | 0.87 |
| E901-07 | -2.24% | 0.99 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.72% |
| 2011 | -3.67% |
| 2012 | 9.33% |
| 2013 | 32.94% |
| 2014 | 9.58% |
| 2015 | 2.65% |
| 2016 | 17.36% |
| 2017 | 12.41% |
| 2018 | -18.83% |
| 2019 | 21.77% |
| 2020 | 15.36% |
| 2021 | 27.39% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 89438.42 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.029577; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.902608476210358e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 932 orders vs QuantConnect Total Orders 932 |
| fills_match_harness_count | pass | downloaded fill events 932 vs harness-recorded fills 932 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 932 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3179b2481c834f8b968cecefe39ac7d61a3901594405753fd88bb13b81df28ff`
- fills_sha256: `77ea65050125fc9eabcddb55099c9e191674213a6cbf07aad2189786994761d4`
- trades_sha256: `83f621ac425fb951a91e8b1908b8a44bdb2f9fbe45daff8c91730e0d59f8b6bf`
