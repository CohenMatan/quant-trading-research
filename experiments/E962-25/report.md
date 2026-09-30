# E962-25 — X962 v1.0 (infrastructure)

C03 S1 null ($200K, 15 slots, hold 60, seed 1). Not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `50f4f7475847c409396b41f82f9bb5cbaf88aa8f` · **QC backtest:** `f774d2debbcd8ef77359a165e180ca67` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T18:41:08Z · **runtime:** 419s
- **Parameters:** `{'slots': 15, 'hold': 60, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.86% |
| Annualised volatility | 15.60% |
| Sharpe (rf = 0) | 0.74 |
| Sortino | 1.05 |
| Max drawdown | -25.91% |
| Longest drawdown (trading days) | 465 |
| Calmar | 0.42 |
| Worst year | -7.70% |
| Worst month | -11.55% |
| Closed trades | 480 |
| Win rate | 58.54% |
| Average winner | 11.37% |
| Average loser | -9.44% |
| Expectancy per trade | 2.75% |
| Profit factor | 1.64 |
| Average holding (calendar days) | 88.0 |
| Average exposure | 85.09% |
| Turnover (1-way, per year) | 3.60 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.48% | 0.98 | 0.90 |
| E901-07 | -3.07% | 0.94 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 25.00% |
| 2011 | -7.70% |
| 2012 | 9.20% |
| 2013 | 28.80% |
| 2014 | 8.05% |
| 2015 | 0.81% |
| 2016 | 8.63% |
| 2017 | 18.62% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 194871.12 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.088844; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 6 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 976 orders vs QuantConnect Total Orders 976 |
| fills_match_harness_count | pass | downloaded fill events 975 vs harness-recorded fills 975 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 975 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2d2bfa0e2215f984dca80e36ff45a0a3e365fe6a9b98e5608d3ef4adbc5c5f08`
- fills_sha256: `a1e5911b2c9890fa276729841b5d20f82607426a1c7cd7a4a267492210c65ffb`
- trades_sha256: `6d023b724e7f41640a6f874bc6ae31e6a58a2847b02205b59d22fb7db7729d64`
