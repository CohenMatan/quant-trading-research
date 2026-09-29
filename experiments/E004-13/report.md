# E004-13 — S004 v1.0 (research)

C01 H004 S004 v1.0 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E004-01 under D051 with the D054 harness fix (replaces E004-09)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `47001e90b3b8d4ccbec29a3b2e6f3182f08749ff` · **QC backtest:** `4bb04b39353aefd75ede7fedd489c4ba` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T09:08:36Z · **runtime:** 385s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.05, 'hold_days': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 4.58% |
| Annualised volatility | 21.63% |
| Sharpe (rf = 0) | 0.32 |
| Sortino | 0.44 |
| Max drawdown | -52.41% |
| Longest drawdown (trading days) | 965 |
| Calmar | 0.09 |
| Worst year | -21.88% |
| Worst month | -15.20% |
| Closed trades | 2581 |
| Win rate | 49.86% |
| Average winner | 6.55% |
| Average loser | -6.05% |
| Expectancy per trade | 0.23% |
| Profit factor | 1.04 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 81.08% |
| Turnover (1-way, per year) | 20.57 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -8.77% | 1.11 | 0.74 |
| E901-05 | -9.17% | 1.11 | 0.79 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 27.83% |
| 2011 | -8.80% |
| 2012 | 22.79% |
| 2013 | 28.93% |
| 2014 | -21.88% |
| 2015 | -20.10% |
| 2016 | 1.83% |
| 2017 | 21.83% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 93016.70 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.029290; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 5183 orders vs QuantConnect Total Orders 5183 |
| fills_match_harness_count | pass | downloaded fill events 5176 vs harness-recorded fills 5176 |
| commission_fixed_per_order | pass | 5176 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ab3ea136593ae21ab68d24e48260672da9c9d3b34a4b79c0db12504c94c90a09`
- fills_sha256: `3388bfec2c599823009d5d41be2aa0220ef3167780580d5c249ccd151417a145`
- trades_sha256: `f851417da31317739a3c87e5e13b9fc7ecfd2d70f6084ebea6fe3dd5d17d3ee6`
