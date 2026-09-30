# E962-03 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 10 slots at $100K, hold 20, seed 3. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `e04a9765733d3d6188b7865f1ed10769077520ca` · **QC backtest:** `6f9629624937bbffb474f0671dc933e9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T08:41:35Z · **runtime:** 315s
- **Parameters:** `{'slots': 10, 'hold': 20, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 12.00% |
| Annualised volatility | 15.41% |
| Sharpe (rf = 0) | 0.81 |
| Sortino | 1.17 |
| Max drawdown | -19.06% |
| Longest drawdown (trading days) | 305 |
| Calmar | 0.63 |
| Worst year | 1.00% |
| Worst month | -8.80% |
| Closed trades | 902 |
| Win rate | 56.21% |
| Average winner | 6.19% |
| Average loser | -5.76% |
| Expectancy per trade | 0.96% |
| Profit factor | 1.33 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 83.32% |
| Turnover (1-way, per year) | 10.10 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.34% | 0.91 | 0.84 |
| E901-07 | -1.93% | 0.87 | 0.88 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 25.30% |
| 2011 | 2.28% |
| 2012 | 9.65% |
| 2013 | 36.18% |
| 2014 | 1.20% |
| 2015 | 1.00% |
| 2016 | 8.21% |
| 2017 | 16.74% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96404.96 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.033269; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.174388296080242e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1814 orders vs QuantConnect Total Orders 1814 |
| fills_match_harness_count | pass | downloaded fill events 1814 vs harness-recorded fills 1814 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1814 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `7abd714a8f5ed8a683d5ba856777b5e758558355637129a6c74835d8931fe487`
- fills_sha256: `57c02f3eb5cf5cdb3f861162be64c748b5d14c43f65b49072f8d22b9593ba82f`
- trades_sha256: `d93ac09c962cebdf7ac555dcdcd7920aaa164fe3ca0a370bb656ac376e1d149d`
