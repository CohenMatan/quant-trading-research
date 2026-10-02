# E016-05 — S016 v1.0 (benchmark)

P2 H016 random control seed 3: same universe, 20 slots, schedule, costs and position rules as E016-01; only the ranking differs. Pre-declared in research/phase2/H016_spec.md (frozen, D116).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `8b77f6a75b8c7db96a3eebdb12824c7f1b9366df` · **QC backtest:** `be7e4b6710d8a8b648d0c25a81a5b748` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T17:20:22Z · **runtime:** 754s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'random', 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 13.34% |
| Annualised volatility | 22.40% |
| Sharpe (rf = 0) | 0.67 |
| Sortino | 0.93 |
| Max drawdown | -40.38% |
| Longest drawdown (trading days) | 488 |
| Calmar | 0.33 |
| Worst year | -13.30% |
| Worst month | -18.01% |
| Closed trades | 100 |
| Win rate | 47.00% |
| Average winner | 80.72% |
| Average loser | -22.74% |
| Expectancy per trade | 25.89% |
| Profit factor | 2.66 |
| Average holding (calendar days) | 512.1 |
| Average exposure | 94.73% |
| Turnover (1-way, per year) | 0.37 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.54% | 1.19 | 0.88 |
| E901-07 | -0.04% | 1.15 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 30.22% |
| 2011 | -13.30% |
| 2012 | 18.90% |
| 2013 | 31.07% |
| 2014 | -5.23% |
| 2015 | -3.48% |
| 2016 | 12.51% |
| 2017 | 13.99% |
| 2018 | -5.68% |
| 2019 | 34.03% |
| 2020 | 52.32% |
| 2021 | 10.74% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 90968.73 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.015749; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.017355591316655e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 324 orders vs QuantConnect Total Orders 324 |
| fills_match_harness_count | pass | downloaded fill events 323 vs harness-recorded fills 323 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 323 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `31da6b18744d71fbce4df280a57672fc5b72f01fd750862fd89d55203c163211`
- fills_sha256: `e655cd571e2bc10e19de9199c1a556ded00c5b3ee5e353e8f76aab1a03a3895e`
- trades_sha256: `300c4d4f4e9b14151d2260f41fe82120f8974de3b34f0f315f107b17987d4eb9`
