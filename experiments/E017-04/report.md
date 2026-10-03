# E017-04 — S017 v1.0 (benchmark)

P2 H017 random-event control seed 2: identical code path, timing, sizing, holding, costs and daily k_t as E017-01; only the selection differs. Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `4a336ec4be47b8e2869ec3e2d383d2a73cab8223` · **QC backtest:** `a9a4a2ed1ec0fee65df70a666381dace` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T18:56:58Z · **runtime:** 1057s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'random', 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 13.62% |
| Annualised volatility | 20.35% |
| Sharpe (rf = 0) | 0.73 |
| Sortino | 1.02 |
| Max drawdown | -42.01% |
| Longest drawdown (trading days) | 415 |
| Calmar | 0.32 |
| Worst year | -15.22% |
| Worst month | -22.17% |
| Closed trades | 464 |
| Win rate | 60.78% |
| Average winner | 11.56% |
| Average loser | -9.06% |
| Expectancy per trade | 3.47% |
| Profit factor | 1.83 |
| Average holding (calendar days) | 86.7 |
| Average exposure | 89.54% |
| Turnover (1-way, per year) | 3.76 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.27% | 1.07 | 0.87 |
| E901-07 | 0.23% | 1.03 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 26.84% |
| 2011 | 0.76% |
| 2012 | 18.37% |
| 2013 | 33.45% |
| 2014 | 19.02% |
| 2015 | -5.99% |
| 2016 | 8.93% |
| 2017 | 16.01% |
| 2018 | -15.22% |
| 2019 | 27.76% |
| 2020 | 13.53% |
| 2021 | 29.05% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 94500.15 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.028473; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.8302747322856585e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 938 orders vs QuantConnect Total Orders 938 |
| fills_match_harness_count | pass | downloaded fill events 938 vs harness-recorded fills 938 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 938 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `d283ca4b0e1a9d104480f1dbdddd192fb9cf7d2518bbed30235bec32ca655bf5`
- fills_sha256: `6c1301ca0330a16efe5bc3bf2e2888b3d2bdbefcf0e47ef10dd021347cebf275`
- trades_sha256: `d152a96600c92651f9f8a4678cf51e5e9707eda1a8e3e4ccecaaebb89341fc7b`
