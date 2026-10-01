# E014-06 — S014 v1.0 (benchmark)

P2 control R random uptrend seed 2, exit A (same code, universe, slots, costs and exit as E014-01). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `de4f7298af89672c07d5d8e07b99043134a53449` · **QC backtest:** `089d40d3adfb3c88a7ef33a791adbd19` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T00:33:31Z · **runtime:** 1217s
- **Parameters:** `{'mode': 'rand', 'exit': 'A', 'limit': 63, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 19.69% |
| Annualised volatility | 19.89% |
| Sharpe (rf = 0) | 1.00 |
| Sortino | 1.43 |
| Max drawdown | -29.93% |
| Longest drawdown (trading days) | 226 |
| Calmar | 0.66 |
| Worst year | -1.72% |
| Worst month | -14.28% |
| Closed trades | 314 |
| Win rate | 40.76% |
| Average winner | 36.53% |
| Average loser | -7.83% |
| Expectancy per trade | 10.26% |
| Profit factor | 3.25 |
| Average holding (calendar days) | 158.4 |
| Average exposure | 94.31% |
| Turnover (1-way, per year) | 1.73 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 5.10% | 0.86 | 0.72 |
| E901-07 | 6.21% | 0.80 | 0.71 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 11.17% |
| 2011 | 11.41% |
| 2012 | 11.45% |
| 2013 | 42.82% |
| 2014 | 8.69% |
| 2015 | 5.41% |
| 2016 | 14.42% |
| 2017 | 16.32% |
| 2018 | -1.72% |
| 2019 | 34.83% |
| 2020 | 75.38% |
| 2021 | 23.46% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91768.01 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.021356; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 10 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.9944438002836664e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 640 orders vs QuantConnect Total Orders 640 |
| fills_match_harness_count | pass | downloaded fill events 640 vs harness-recorded fills 640 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 640 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `e864f686d3639918ceb5168d9884d088db469a916bdefa1311784a1285aeec1f`
- fills_sha256: `2b947f715dedb4b51dc597edd51f886fc1959c311a49ddca08023af5af483a33`
- trades_sha256: `f128d37535ad90536b2b78a5d9e81fd6d2d7f396b8d7a5feec3393435d3638cc`
