# E014-04 — S014 v1.0 (benchmark)

P2 control C2 pullback without recovery, exit A (same code, universe, slots, costs and exit as E014-01). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `9d769ea8352017a33470c83a2929282645773f64` · **QC backtest:** `aeba32e4fa4999e0bb5b6149b0d6150e` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T23:47:36Z · **runtime:** 1397s
- **Parameters:** `{'mode': 'c2', 'exit': 'A', 'limit': 63, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 13.17% |
| Annualised volatility | 26.07% |
| Sharpe (rf = 0) | 0.61 |
| Sortino | 0.85 |
| Max drawdown | -36.01% |
| Longest drawdown (trading days) | 619 |
| Calmar | 0.37 |
| Worst year | -16.54% |
| Worst month | -18.52% |
| Closed trades | 893 |
| Win rate | 39.64% |
| Average winner | 21.67% |
| Average loser | -9.92% |
| Expectancy per trade | 2.60% |
| Profit factor | 1.30 |
| Average holding (calendar days) | 56.5 |
| Average exposure | 92.21% |
| Turnover (1-way, per year) | 5.67 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.42% | 1.11 | 0.71 |
| E901-07 | -0.31% | 1.10 | 0.75 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 26.69% |
| 2011 | 4.68% |
| 2012 | 23.58% |
| 2013 | 39.11% |
| 2014 | 0.93% |
| 2015 | 0.99% |
| 2016 | -8.50% |
| 2017 | 33.18% |
| 2018 | -16.54% |
| 2019 | 51.05% |
| 2020 | 25.17% |
| 2021 | -1.35% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 84251.95 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.023300; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 11 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1798 orders vs QuantConnect Total Orders 1798 |
| fills_match_harness_count | pass | downloaded fill events 1798 vs harness-recorded fills 1798 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1798 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `01c2e60d1eaf9858f73bf20e2e397514ff6b5220cab6d5e4ef48df4142dcad5f`
- fills_sha256: `7a00655b3561311a8275f46e94ea340788c706b3559b32546945a9a218c2d0cf`
- trades_sha256: `87b21051696fa89abfbc970bfc32a91a9d3a86d3c70a87e24a91bd1d9863537a`
