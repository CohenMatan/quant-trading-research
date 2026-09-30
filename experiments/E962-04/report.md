# E962-04 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 15 slots at $100K, hold 20, seed 1. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `8a08407877fe92a84d704814ebddbb2457009e98` · **QC backtest:** `26d84380b53b70c885283878e2197819` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T08:47:09Z · **runtime:** 379s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.37% |
| Annualised volatility | 14.56% |
| Sharpe (rf = 0) | 0.69 |
| Sortino | 0.97 |
| Max drawdown | -18.92% |
| Longest drawdown (trading days) | 391 |
| Calmar | 0.50 |
| Worst year | -4.69% |
| Worst month | -7.90% |
| Closed trades | 1352 |
| Win rate | 54.66% |
| Average winner | 6.07% |
| Average loser | -5.49% |
| Expectancy per trade | 0.83% |
| Profit factor | 1.30 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 83.73% |
| Turnover (1-way, per year) | 10.11 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.97% | 0.89 | 0.88 |
| E901-07 | -4.55% | 0.86 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 14.18% |
| 2011 | 0.40% |
| 2012 | 17.06% |
| 2013 | 18.11% |
| 2014 | 4.45% |
| 2015 | -4.69% |
| 2016 | 8.16% |
| 2017 | 19.84% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97073.62 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.046746; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.209735034398567e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2720 orders vs QuantConnect Total Orders 2720 |
| fills_match_harness_count | pass | downloaded fill events 2719 vs harness-recorded fills 2719 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 2719 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `0db6eae39e60964292a8331b4178b64a801b93d96c85a720800413de2edd98b3`
- fills_sha256: `ca2fb4536e3d5fa4047e1859743cca78283ced4b36fc13708786edd224044199`
- trades_sha256: `12720b883db8d3af799e0f3e299c60fa4455d1d3a9e43e9b035b8d4aeea41b87`
