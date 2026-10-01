# E014-11 — S014 v1.1 (benchmark)

P2 control R random uptrend seed 2, exit B (same code, universe, slots, costs and exit as E014-02). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `71bd67cb5b9635fbdd40850a3643ae26060cffed` · **QC backtest:** `9fb43a91f4bf4f309a47d15a5e41871e` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T02:23:15Z · **runtime:** 1493s
- **Parameters:** `{'mode': 'rand', 'exit': 'B', 'limit': 126, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 14.49% |
| Annualised volatility | 18.07% |
| Sharpe (rf = 0) | 0.84 |
| Sortino | 1.18 |
| Max drawdown | -29.95% |
| Longest drawdown (trading days) | 341 |
| Calmar | 0.48 |
| Worst year | -4.40% |
| Worst month | -13.62% |
| Closed trades | 479 |
| Win rate | 42.80% |
| Average winner | 21.27% |
| Average loser | -8.53% |
| Expectancy per trade | 4.22% |
| Profit factor | 1.85 |
| Average holding (calendar days) | 105.1 |
| Average exposure | 93.58% |
| Turnover (1-way, per year) | 2.93 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -0.10% | 0.86 | 0.79 |
| E901-07 | 1.01% | 0.81 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 11.59% |
| 2011 | -4.40% |
| 2012 | 17.93% |
| 2013 | 41.16% |
| 2014 | -3.35% |
| 2015 | -2.55% |
| 2016 | 17.14% |
| 2017 | 8.25% |
| 2018 | 1.04% |
| 2019 | 15.49% |
| 2020 | 70.21% |
| 2021 | 20.17% |

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
| no_leverage | pass | min cash/equity 0.022519; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 8 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.9944438002836664e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 970 orders vs QuantConnect Total Orders 970 |
| fills_match_harness_count | pass | downloaded fill events 970 vs harness-recorded fills 970 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 970 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `b27c0dfeda736a3cc5bf8ac19f097ca71d39c47b64a142d88087b6620ee9cb54`
- fills_sha256: `c1b1a121fcb8c69a31fda22606ad82463f2c5d7fd4ab5454ace2c7a2220adbba`
- trades_sha256: `3b193464a0b10e581eb8ac374c10f009eb45ebe32afd56e1ae78f6ff7e7901c0`
