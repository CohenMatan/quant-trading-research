# E962-09 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 19 slots at $100K, hold 20, seed 3. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `eb2dfb60624011e53705da05ace5ad42f2b4d823` · **QC backtest:** `645d913548739f79c89d8b14ca91ab29` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:20:54Z · **runtime:** 295s
- **Parameters:** `{'slots': 19, 'hold': 20, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 19, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 0.16% |
| Annualised volatility | 9.47% |
| Sharpe (rf = 0) | 0.06 |
| Sortino | 0.09 |
| Max drawdown | -19.65% |
| Longest drawdown (trading days) | 1658 |
| Calmar | 0.01 |
| Worst year | -4.49% |
| Worst month | -10.63% |
| Closed trades | 455 |
| Win rate | 49.89% |
| Average winner | 5.81% |
| Average loser | -6.34% |
| Expectancy per trade | -0.28% |
| Profit factor | 0.91 |
| Average holding (calendar days) | 30.1 |
| Average exposure | 24.67% |
| Turnover (1-way, per year) | 2.89 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -13.18% | 0.35 | 0.53 |
| E901-07 | -13.76% | 0.34 | 0.56 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 3.95% |
| 2011 | -4.49% |
| 2012 | -2.83% |
| 2013 | 6.02% |
| 2014 | 0.00% |
| 2015 | 1.18% |
| 2016 | -2.88% |
| 2017 | 0.80% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 86172.50 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.027940; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.196725525139577e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 915 orders vs QuantConnect Total Orders 915 |
| fills_match_harness_count | pass | downloaded fill events 915 vs harness-recorded fills 915 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 915 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `512f95bbdd036e58e8cfb5aaaa6c9ad7d50236efb904671ca4e861541253fae8`
- fills_sha256: `7bdb7169f809a24fbea46c3393461127332d0964a56e0792473c7c659fbc6987`
- trades_sha256: `8604f4c4fcc21b5f9252e4a83e315df5891feb7a31ad0b8474af6c9ce92303c6`
