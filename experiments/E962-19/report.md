# E962-19 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series H: holding period: 15 slots at $100K, hold 5, seed 1. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `4bf70182d2647bae39a15b13737ba77486b96e2d` · **QC backtest:** `79b3bb4dfdf3d360fc442edafc807d3d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:28:33Z · **runtime:** 292s
- **Parameters:** `{'slots': 15, 'hold': 5, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -1.96% |
| Annualised volatility | 13.76% |
| Sharpe (rf = 0) | -0.07 |
| Sortino | -0.10 |
| Max drawdown | -31.79% |
| Longest drawdown (trading days) | 965 |
| Calmar | -0.06 |
| Worst year | -14.30% |
| Worst month | -10.65% |
| Closed trades | 3925 |
| Win rate | 50.04% |
| Average winner | 3.01% |
| Average loser | -3.17% |
| Expectancy per trade | -0.08% |
| Profit factor | 0.93 |
| Average holding (calendar days) | 8.7 |
| Average exposure | 68.79% |
| Turnover (1-way, per year) | 29.31 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -15.30% | 0.82 | 0.85 |
| E901-07 | -15.89% | 0.78 | 0.87 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 7.91% |
| 2011 | -12.59% |
| 2012 | 5.06% |
| 2013 | 13.69% |
| 2014 | -2.15% |
| 2015 | -12.77% |
| 2016 | -14.30% |
| 2017 | 3.61% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 81750.04 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.031974; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 7852 orders vs QuantConnect Total Orders 7852 |
| fills_match_harness_count | pass | downloaded fill events 7850 vs harness-recorded fills 7850 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 7850 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `e1949b498344ed87c278ad0a46a90cabb742083bfa43e89b85486f53a25700d2`
- fills_sha256: `3dc80298fba2a5c6da165df0a9e105d69923579d4c9a5e02017abc371f03b6fb`
- trades_sha256: `d88f153111166e08dc4e9213b625b611394a01f569ef47dfb9e9100e52557fbf`
