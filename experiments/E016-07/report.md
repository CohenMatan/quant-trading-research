# E016-07 — S016 v1.0 (benchmark)

P2 H016 random control seed 5: same universe, 20 slots, schedule, costs and position rules as E016-01; only the ranking differs. Pre-declared in research/phase2/H016_spec.md (frozen, D116).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `c971e2ce6bfe743bcb45c4bc2c1548a6350c10fa` · **QC backtest:** `503a6f2e4f5be2e66092186f88a2ede4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T18:46:45Z · **runtime:** 750s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'random', 'seed': 5}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 18.46% |
| Annualised volatility | 19.15% |
| Sharpe (rf = 0) | 0.98 |
| Sortino | 1.38 |
| Max drawdown | -36.35% |
| Longest drawdown (trading days) | 216 |
| Calmar | 0.51 |
| Worst year | 2.55% |
| Worst month | -13.35% |
| Closed trades | 98 |
| Win rate | 51.02% |
| Average winner | 40.31% |
| Average loser | -21.55% |
| Expectancy per trade | 10.01% |
| Profit factor | 1.66 |
| Average holding (calendar days) | 468.5 |
| Average exposure | 95.96% |
| Turnover (1-way, per year) | 0.25 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 3.58% | 1.04 | 0.90 |
| E901-07 | 5.08% | 0.99 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 14.77% |
| 2011 | 7.54% |
| 2012 | 10.54% |
| 2013 | 26.94% |
| 2014 | 10.04% |
| 2015 | 2.55% |
| 2016 | 13.56% |
| 2017 | 31.51% |
| 2018 | 3.05% |
| 2019 | 44.03% |
| 2020 | 33.97% |
| 2021 | 28.02% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96940.58 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.018602; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 8 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.4962832304260223e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 314 orders vs QuantConnect Total Orders 314 |
| fills_match_harness_count | pass | downloaded fill events 314 vs harness-recorded fills 314 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 314 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `aab171ccfa9601ad1e137ecc82a98626da4b3b18c76ddb1b5eaf8fcb04f97c21`
- fills_sha256: `ff64fadc15f61653783286a5d9cbb8e6f743d2e86395f560a14387d80412f730`
- trades_sha256: `bbbcca2f18306b788cfb94720aea4f07b48aa0c8404e7d985cd5c5e831f8b7b3`
