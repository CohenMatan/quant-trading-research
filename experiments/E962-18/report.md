# E962-18 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series B: breadth beyond the $100K limit: 30 slots at $250K, hold 20, seed 3. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `eb5347705cc562eecd7ec31577f2f9adb99df0d2` · **QC backtest:** `1454f677925412d11cf5b1015933121e` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:23:08Z · **runtime:** 298s
- **Parameters:** `{'slots': 30, 'hold': 20, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 30, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.65% |
| Annualised volatility | 14.40% |
| Sharpe (rf = 0) | 0.58 |
| Sortino | 0.82 |
| Max drawdown | -21.57% |
| Longest drawdown (trading days) | 466 |
| Calmar | 0.35 |
| Worst year | -3.93% |
| Worst month | -9.26% |
| Closed trades | 2706 |
| Win rate | 55.76% |
| Average winner | 5.98% |
| Average loser | -6.10% |
| Expectancy per trade | 0.64% |
| Profit factor | 1.21 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 82.13% |
| Turnover (1-way, per year) | 9.90 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -5.69% | 0.92 | 0.91 |
| E901-07 | -6.28% | 0.88 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 16.41% |
| 2011 | -3.93% |
| 2012 | 4.20% |
| 2013 | 24.07% |
| 2014 | 7.92% |
| 2015 | -1.38% |
| 2016 | 3.06% |
| 2017 | 13.58% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 242501.27 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.082653; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 8 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6427373294361057e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 5442 orders vs QuantConnect Total Orders 5442 |
| fills_match_harness_count | pass | downloaded fill events 5442 vs harness-recorded fills 5442 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 5442 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `bb36832f732ccd63661ac2c093af66740f804912eb3a288f79e392156be8e12b`
- fills_sha256: `3b5d0a8b194f2fe4fe4bf0773d58ea594166e3db1c04e2c3c8809a7a83e990a5`
- trades_sha256: `2d018cc2672dd652f748284a5c05c47e2416abd47824e4fbeb6a767943316bbf`
