# E014-03 — S014 v1.0 (benchmark)

P2 control C1 trend-only, exit A (same code, universe, slots, costs and exit as E014-01). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed_with_warnings
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `f49715bfef9a9c90f8bb6d5e01d325c85c181cef` · **QC backtest:** `4445356a2a016096a5b935bc4aa444ae` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T23:26:31Z · **runtime:** 1253s
- **Parameters:** `{'mode': 'c1', 'exit': 'A', 'limit': 63, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 14.31% |
| Annualised volatility | 30.81% |
| Sharpe (rf = 0) | 0.59 |
| Sortino | 0.82 |
| Max drawdown | -44.83% |
| Longest drawdown (trading days) | 494 |
| Calmar | 0.32 |
| Worst year | -24.70% |
| Worst month | -21.28% |
| Closed trades | 360 |
| Win rate | 38.06% |
| Average winner | 45.88% |
| Average loser | -14.65% |
| Expectancy per trade | 8.39% |
| Profit factor | 1.52 |
| Average holding (calendar days) | 141.4 |
| Average exposure | 94.27% |
| Turnover (1-way, per year) | 1.92 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.28% | 1.27 | 0.68 |
| E901-07 | 0.82% | 1.25 | 0.72 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 28.88% |
| 2011 | -7.88% |
| 2012 | 36.62% |
| 2013 | 20.64% |
| 2014 | 17.75% |
| 2015 | 7.53% |
| 2016 | 1.07% |
| 2017 | 35.92% |
| 2018 | -16.81% |
| 2019 | 39.99% |
| 2020 | 66.43% |
| 2021 | -24.70% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 88853.97 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.017535; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 31 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0058560358130133e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 732 orders vs QuantConnect Total Orders 732 |
| fills_match_harness_count | pass | downloaded fill events 731 vs harness-recorded fills 731 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | warn | 1 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 1 mirrored |
| commission_fixed_per_order | pass | 732 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `1dc910a3042c3648c31cc85d7d19e9f91a2cbcaa00cff9ba201dae51c6f3f792`
- fills_sha256: `751b926470ee0a7fd9436457d8f04c09cdff06a8917c403e9130c7f24819aad3`
- trades_sha256: `9d6ea1be9c61917c7bcd5479cbed06b440a3bfa968506836b6d0093b229de82a`
