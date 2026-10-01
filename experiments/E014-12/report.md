# E014-12 — S014 v1.1 (benchmark)

P2 control R random uptrend seed 3, exit B (same code, universe, slots, costs and exit as E014-02). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `5691dfe3300627ebda433095b389337a68688227` · **QC backtest:** `fae35fe1c0622c19c198c83bdb5380b4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T02:48:19Z · **runtime:** 1337s
- **Parameters:** `{'mode': 'rand', 'exit': 'B', 'limit': 126, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 15.30% |
| Annualised volatility | 16.96% |
| Sharpe (rf = 0) | 0.92 |
| Sortino | 1.32 |
| Max drawdown | -25.48% |
| Longest drawdown (trading days) | 463 |
| Calmar | 0.60 |
| Worst year | -15.91% |
| Worst month | -11.07% |
| Closed trades | 518 |
| Win rate | 40.73% |
| Average winner | 20.81% |
| Average loser | -7.87% |
| Expectancy per trade | 3.81% |
| Profit factor | 1.70 |
| Average holding (calendar days) | 97.6 |
| Average exposure | 93.59% |
| Turnover (1-way, per year) | 3.30 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 0.71% | 0.80 | 0.79 |
| E901-07 | 1.82% | 0.76 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.14% |
| 2011 | 1.71% |
| 2012 | 19.68% |
| 2013 | 60.41% |
| 2014 | 7.60% |
| 2015 | -3.09% |
| 2016 | 4.51% |
| 2017 | 17.35% |
| 2018 | -15.91% |
| 2019 | 32.68% |
| 2020 | 25.35% |
| 2021 | 33.58% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 90784.82 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.027642; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.092280125712233e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1048 orders vs QuantConnect Total Orders 1048 |
| fills_match_harness_count | pass | downloaded fill events 1048 vs harness-recorded fills 1048 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1048 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `e4a95d3c485bf85ffbc52811b0563d3593ff6ac272bec4f2d6e6190b3c1e490b`
- fills_sha256: `8f420fb43cbe79947f45610ec4cc0fd60e3809d9f38a711d5a46db9ee4300901`
- trades_sha256: `24c21f7a14492309654c3ab1513b1123f8c77169d3a7ed9f1805c34f04a20cba`
