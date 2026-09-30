# E962-22 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series H: holding period: 15 slots at $100K, hold 60, seed 1. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `f3cd86cd7be3e4018774441b9d53653cb9827656` · **QC backtest:** `a2ce370d83812cc4030dc3a3451e4d10` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:44:48Z · **runtime:** 284s
- **Parameters:** `{'slots': 15, 'hold': 60, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.52% |
| Annualised volatility | 15.58% |
| Sharpe (rf = 0) | 0.72 |
| Sortino | 1.02 |
| Max drawdown | -25.93% |
| Longest drawdown (trading days) | 467 |
| Calmar | 0.41 |
| Worst year | -8.00% |
| Worst month | -11.53% |
| Closed trades | 480 |
| Win rate | 58.33% |
| Average winner | 11.33% |
| Average loser | -9.47% |
| Expectancy per trade | 2.66% |
| Profit factor | 1.61 |
| Average holding (calendar days) | 88.0 |
| Average exposure | 84.94% |
| Turnover (1-way, per year) | 3.59 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.82% | 0.98 | 0.90 |
| E901-07 | -3.41% | 0.94 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 24.55% |
| 2011 | -8.00% |
| 2012 | 8.81% |
| 2013 | 28.39% |
| 2014 | 7.76% |
| 2015 | 0.49% |
| 2016 | 8.35% |
| 2017 | 18.33% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97390.35 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.089782; 0 closes with negative cash |
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

- equity_sha256: `eeb445d246652bbab686c3b03966e8592197aa87561e1de747eca7a59448d040`
- fills_sha256: `19a8ecf7673471adcc80f5a2fd1dcdd29dc0622c13a18a0c387b16cfa562e004`
- trades_sha256: `4c4b83ca29ede16616a0393a3810b3595ee7cf313179e0c709f8de015993ae98`
