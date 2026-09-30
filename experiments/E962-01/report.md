# E962-01 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 10 slots at $100K, hold 20, seed 1. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `86501b2dcaee6b8aeaaa8f46ba408b2e39203c7f` · **QC backtest:** `883a5b7bdaaaa473fcfc95cf02377d22` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T08:28:30Z · **runtime:** 452s
- **Parameters:** `{'slots': 10, 'hold': 20, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.98% |
| Annualised volatility | 15.25% |
| Sharpe (rf = 0) | 0.82 |
| Sortino | 1.18 |
| Max drawdown | -18.21% |
| Longest drawdown (trading days) | 249 |
| Calmar | 0.66 |
| Worst year | -1.45% |
| Worst month | -7.40% |
| Closed trades | 901 |
| Win rate | 55.60% |
| Average winner | 6.33% |
| Average loser | -5.54% |
| Expectancy per trade | 1.06% |
| Profit factor | 1.41 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 83.41% |
| Turnover (1-way, per year) | 10.07 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.36% | 0.90 | 0.85 |
| E901-07 | -1.95% | 0.86 | 0.88 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 14.99% |
| 2011 | -0.69% |
| 2012 | 17.68% |
| 2013 | 18.47% |
| 2014 | 14.65% |
| 2015 | -1.45% |
| 2016 | 13.09% |
| 2017 | 21.31% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96809.38 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.049619; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.209735034398567e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1812 orders vs QuantConnect Total Orders 1812 |
| fills_match_harness_count | pass | downloaded fill events 1812 vs harness-recorded fills 1812 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1812 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `b577db9711ab9facb1e133782e7d066243befcad12a34df698fbb90b27b4c68e`
- fills_sha256: `a99225d93a61e3e76bc61a55389993f8f94779ddc2f9f4aab2f577635861cac6`
- trades_sha256: `b82a5b1d00d63ffbcebc4354b343ceab2d0542eb244234e479cdf7742fa22f5a`
