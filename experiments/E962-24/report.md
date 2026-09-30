# E962-24 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series H: holding period: 15 slots at $100K, hold 60, seed 3. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `ddba74e3040ec7d0727ab768039ed30b8cf6e30d` · **QC backtest:** `da4e7f0feea9aac5a7ae1836287c0b4d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:54:34Z · **runtime:** 347s
- **Parameters:** `{'slots': 15, 'hold': 60, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.42% |
| Annualised volatility | 15.28% |
| Sharpe (rf = 0) | 0.90 |
| Sortino | 1.29 |
| Max drawdown | -21.69% |
| Longest drawdown (trading days) | 261 |
| Calmar | 0.62 |
| Worst year | -0.07% |
| Worst month | -9.46% |
| Closed trades | 481 |
| Win rate | 62.16% |
| Average winner | 11.81% |
| Average loser | -10.29% |
| Expectancy per trade | 3.45% |
| Profit factor | 1.81 |
| Average holding (calendar days) | 88.2 |
| Average exposure | 83.71% |
| Turnover (1-way, per year) | 3.56 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 0.07% | 0.95 | 0.89 |
| E901-07 | -0.51% | 0.91 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 13.25% |
| 2011 | 5.24% |
| 2012 | 9.77% |
| 2013 | 32.52% |
| 2014 | 18.99% |
| 2015 | -0.07% |
| 2016 | 18.25% |
| 2017 | 12.08% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 93158.54 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.048779; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 977 orders vs QuantConnect Total Orders 977 |
| fills_match_harness_count | pass | downloaded fill events 977 vs harness-recorded fills 977 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 977 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ce116ea1da722fa0d46646ab6b8e87a2e1c7acca0d6628c9c3d9a2aed1b40da2`
- fills_sha256: `6b6860316dc16764d6ae435262f0f5dcf159f16b0136275b525a77298867cb87`
- trades_sha256: `879fca71f3d9b5260f18bd27693cc93f52a8aeef44c3d5cda757338ad69011b6`
