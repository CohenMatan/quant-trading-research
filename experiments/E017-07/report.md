# E017-07 — S017 v1.0 (benchmark)

P2 H017 random-event control seed 5: identical code path, timing, sizing, holding, costs and daily k_t as E017-01; only the selection differs. Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `1eee56a85cbefd873f03c3078556577c16bb74a2` · **QC backtest:** `618e845a4b7eca3508e2ebf59242baee` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T19:42:17Z · **runtime:** 796s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'random', 'seed': 5}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 13.08% |
| Annualised volatility | 20.21% |
| Sharpe (rf = 0) | 0.71 |
| Sortino | 1.03 |
| Max drawdown | -33.22% |
| Longest drawdown (trading days) | 615 |
| Calmar | 0.39 |
| Worst year | -13.53% |
| Worst month | -9.95% |
| Closed trades | 463 |
| Win rate | 57.67% |
| Average winner | 13.80% |
| Average loser | -10.28% |
| Expectancy per trade | 3.61% |
| Profit factor | 2.05 |
| Average holding (calendar days) | 86.8 |
| Average exposure | 89.12% |
| Turnover (1-way, per year) | 3.69 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.80% | 1.02 | 0.84 |
| E901-07 | -0.30% | 0.99 | 0.88 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 5.43% |
| 2011 | -12.02% |
| 2012 | 2.49% |
| 2013 | 21.40% |
| 2014 | 14.54% |
| 2015 | -4.63% |
| 2016 | 15.02% |
| 2017 | 14.52% |
| 2018 | -13.53% |
| 2019 | 16.08% |
| 2020 | 86.68% |
| 2021 | 37.72% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 82421.65 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.022754; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.8364951163126596e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 936 orders vs QuantConnect Total Orders 936 |
| fills_match_harness_count | pass | downloaded fill events 936 vs harness-recorded fills 936 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 936 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `d76cc2c7cbc192350a41e7d127e02e90727a5dd5323469ac14dccdc34225ceaf`
- fills_sha256: `2e7805ecce802af5af64d8d3182e956c40d6149993b677a9f1aa601b3ca8809e`
- trades_sha256: `3a2b9a0257a87198768dfb625f1bf049ea59da6e30b6826b88ba50b24361c642`
