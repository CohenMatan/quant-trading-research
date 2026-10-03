# E017-03 — S017 v1.0 (benchmark)

P2 H017 random-event control seed 1: identical code path, timing, sizing, holding, costs and daily k_t as E017-01; only the selection differs. Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `ce601ba4d2e419480d057a9af3130d6a52f07efd` · **QC backtest:** `9080db4517268796f1ce37f3da213023` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-03T18:42:42Z · **runtime:** 838s
- **Parameters:** `{'slots': 10, 'hold_sessions': 60, 'quantile': 0.9, 'reaction_lag': 1, 'book': 'random', 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 13.10% |
| Annualised volatility | 19.57% |
| Sharpe (rf = 0) | 0.73 |
| Sortino | 1.04 |
| Max drawdown | -37.01% |
| Longest drawdown (trading days) | 558 |
| Calmar | 0.35 |
| Worst year | -8.52% |
| Worst month | -13.03% |
| Closed trades | 462 |
| Win rate | 61.04% |
| Average winner | 11.16% |
| Average loser | -9.01% |
| Expectancy per trade | 3.30% |
| Profit factor | 1.86 |
| Average holding (calendar days) | 86.8 |
| Average exposure | 89.30% |
| Turnover (1-way, per year) | 3.73 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.78% | 1.03 | 0.87 |
| E901-07 | -0.28% | 0.99 | 0.90 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 22.66% |
| 2011 | -5.34% |
| 2012 | 8.71% |
| 2013 | 33.13% |
| 2014 | 29.17% |
| 2015 | -8.52% |
| 2016 | 10.63% |
| 2017 | 17.31% |
| 2018 | -8.05% |
| 2019 | 17.37% |
| 2020 | 26.19% |
| 2021 | 22.37% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91069.59 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 100000.00 vs initial cash 100000.00; 166 warm-up sessions |
| no_leverage | pass | min cash/equity 0.028934; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.092280125712233e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 934 orders vs QuantConnect Total Orders 934 |
| fills_match_harness_count | pass | downloaded fill events 934 vs harness-recorded fills 934 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 934 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c336911f4e31a0fac2d2abf9339afe818da4e7e6d0067a7870461b544f9f8815`
- fills_sha256: `c4153e82c7803b5e09f33db40c65e4719fa4d7bfbfaf36d99ec5a8f16b6d270a`
- trades_sha256: `06dc2566c1d22f4cf7d99bc68fdc28aa18ea8228ee2cc31fb81578eca28a025f`
