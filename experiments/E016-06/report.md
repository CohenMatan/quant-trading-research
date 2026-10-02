# E016-06 — S016 v1.0 (benchmark)

P2 H016 random control seed 4: same universe, 20 slots, schedule, costs and position rules as E016-01; only the ranking differs. Pre-declared in research/phase2/H016_spec.md (frozen, D116).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `36f4b9a0c3f5d49d5fe0cec9798606c4ec6ed0b9` · **QC backtest:** `748e81514c6ff9b17dadcbdf159026ee` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T18:34:43Z · **runtime:** 704s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'random', 'seed': 4}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 13.39% |
| Annualised volatility | 19.24% |
| Sharpe (rf = 0) | 0.75 |
| Sortino | 1.03 |
| Max drawdown | -40.59% |
| Longest drawdown (trading days) | 265 |
| Calmar | 0.33 |
| Worst year | -8.39% |
| Worst month | -21.49% |
| Closed trades | 78 |
| Win rate | 52.56% |
| Average winner | 45.72% |
| Average loser | -17.20% |
| Expectancy per trade | 15.87% |
| Profit factor | 2.79 |
| Average holding (calendar days) | 521.3 |
| Average exposure | 95.97% |
| Turnover (1-way, per year) | 0.24 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.49% | 1.05 | 0.91 |
| E901-07 | 0.00% | 0.99 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.29% |
| 2011 | -0.59% |
| 2012 | 16.95% |
| 2013 | 43.38% |
| 2014 | 19.17% |
| 2015 | 6.72% |
| 2016 | 4.69% |
| 2017 | 19.24% |
| 2018 | -8.39% |
| 2019 | 24.38% |
| 2020 | 15.68% |
| 2021 | 12.94% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 87921.90 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.018427; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 6 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.8364951163126596e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 242 orders vs QuantConnect Total Orders 242 |
| fills_match_harness_count | pass | downloaded fill events 242 vs harness-recorded fills 242 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 242 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3fb401019a02bf5846eff56d314ad056205be7afc4fbfea169102bd97a6c53d9`
- fills_sha256: `0c40588ea2a318cfca4e2acff8e8e44cc8bb99ffadd6b6546ddafd51094ec11a`
- trades_sha256: `e07a106cf0214534ed8b2d41ae822720b904c50b9b2a8cdc0aad3123cde43116`
