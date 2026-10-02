# E016-03 — S016 v1.0 (benchmark)

P2 H016 random control seed 1: same universe, 20 slots, schedule, costs and position rules as E016-01; only the ranking differs. Pre-declared in research/phase2/H016_spec.md (frozen, D116).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `938a988d7b3244f4bd380d702a679a12ecd54392` · **QC backtest:** `880fd589c9802443adef349b0125f5d8` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T15:51:56Z · **runtime:** 851s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'random', 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 15.38% |
| Annualised volatility | 19.08% |
| Sharpe (rf = 0) | 0.85 |
| Sortino | 1.20 |
| Max drawdown | -33.78% |
| Longest drawdown (trading days) | 305 |
| Calmar | 0.46 |
| Worst year | -6.42% |
| Worst month | -14.09% |
| Closed trades | 100 |
| Win rate | 51.00% |
| Average winner | 61.54% |
| Average loser | -21.15% |
| Expectancy per trade | 21.02% |
| Profit factor | 2.88 |
| Average holding (calendar days) | 545.4 |
| Average exposure | 94.83% |
| Turnover (1-way, per year) | 0.40 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 0.50% | 0.98 | 0.86 |
| E901-07 | 1.99% | 0.95 | 0.89 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.73% |
| 2011 | 3.81% |
| 2012 | 10.70% |
| 2013 | 27.63% |
| 2014 | 7.24% |
| 2015 | -6.42% |
| 2016 | 10.78% |
| 2017 | 10.37% |
| 2018 | 5.42% |
| 2019 | 36.00% |
| 2020 | 42.76% |
| 2021 | 27.49% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 94227.88 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.020325; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 6 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.477601755173623e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 315 orders vs QuantConnect Total Orders 315 |
| fills_match_harness_count | pass | downloaded fill events 315 vs harness-recorded fills 315 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 315 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2df589b87b0d5fdc7dcfd502f8acf79407203f6fe079cb5c038e36f98bf7380c`
- fills_sha256: `aead83c03c8b61650bb80e2f047ba0cbb2966fce4093cd82a05993ec147ef093`
- trades_sha256: `8aff70df9eaeefdf729e05a92ded78ef2db9cbad132fb14c3768598b195aaa55`
