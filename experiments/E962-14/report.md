# E962-14 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series A: account size: 15 slots at $1000K, hold 20, seed 2. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `8c6e8decad34f865cd30d8f0870521ea0e7887b1` · **QC backtest:** `868938ab8d0d5ede955517ed50d46053` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:57:19Z · **runtime:** 315s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.48% |
| Annualised volatility | 15.05% |
| Sharpe (rf = 0) | 0.68 |
| Sortino | 0.95 |
| Max drawdown | -23.03% |
| Longest drawdown (trading days) | 474 |
| Calmar | 0.41 |
| Worst year | -7.54% |
| Worst month | -6.06% |
| Closed trades | 1351 |
| Win rate | 56.92% |
| Average winner | 6.03% |
| Average loser | -5.92% |
| Expectancy per trade | 0.88% |
| Profit factor | 1.32 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 81.25% |
| Turnover (1-way, per year) | 9.77 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.86% | 0.93 | 0.88 |
| E901-07 | -4.45% | 0.89 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 19.82% |
| 2011 | -4.13% |
| 2012 | 9.75% |
| 2013 | 33.55% |
| 2014 | -1.32% |
| 2015 | -7.54% |
| 2016 | 6.20% |
| 2017 | 26.36% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 971088.69 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.110606; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3717273618679165e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2717 orders vs QuantConnect Total Orders 2717 |
| fills_match_harness_count | pass | downloaded fill events 2717 vs harness-recorded fills 2717 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 2717 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `4b530acadd3cd4d19d024598426d41a16e296093113cefd04fc06f9253182ab6`
- fills_sha256: `2d5db3d8a4fc492541eabb1757a274d436689d2934b9c18dcefef7bff9ad76c9`
- trades_sha256: `0fcf1691e57b1d78ec8fca7f7145c014f79374181c8d89c2ba99dfe6866196e0`
