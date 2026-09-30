# E962-28 — X962 v1.0 (infrastructure)

C03 S2 null ($200K, 20 slots, hold 60, seed 1). Not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `ecf814d3ad152cb2763964a770950eefba77040b` · **QC backtest:** `39557af7b75c0cc6ac66fae61c8b01f9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T18:57:57Z · **runtime:** 292s
- **Parameters:** `{'slots': 20, 'hold': 60, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.34% |
| Annualised volatility | 15.14% |
| Sharpe (rf = 0) | 0.67 |
| Sortino | 0.94 |
| Max drawdown | -27.24% |
| Longest drawdown (trading days) | 501 |
| Calmar | 0.34 |
| Worst year | -6.76% |
| Worst month | -11.29% |
| Closed trades | 641 |
| Win rate | 57.88% |
| Average winner | 11.14% |
| Average loser | -9.78% |
| Expectancy per trade | 2.33% |
| Profit factor | 1.51 |
| Average holding (calendar days) | 88.0 |
| Average exposure | 84.46% |
| Turnover (1-way, per year) | 3.57 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.00% | 0.96 | 0.91 |
| E901-07 | -4.59% | 0.92 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 21.54% |
| 2011 | -6.76% |
| 2012 | 7.12% |
| 2013 | 30.88% |
| 2014 | 7.56% |
| 2015 | -4.10% |
| 2016 | 6.98% |
| 2017 | 16.34% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 193780.35 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.102216; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1303 orders vs QuantConnect Total Orders 1303 |
| fills_match_harness_count | pass | downloaded fill events 1301 vs harness-recorded fills 1301 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1301 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2918f7309e6c8da8b548c55965fce492ab1341c1d0034db39c954e00e7cff4fe`
- fills_sha256: `0e18057799ce3c96260f0ae67b3382438f75e9f94df1511abd41a0bcdc5265bb`
- trades_sha256: `f9bcaf32da8a27d66dc25906ffd6238c830a09b695834b409143763d5e90d3e9`
