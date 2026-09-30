# E007-08 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): plateau: ATR10/ATR100 ratio 0.6 -> 0.48 (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `ad18807db8a6c94ee60c373fb22825765ecc1d04` · **QC backtest:** `2cf59606ef23c94616ec3c89e5d61633` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T04:35:51Z · **runtime:** 1273s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.48, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 0.36% |
| Annualised volatility | 0.89% |
| Sharpe (rf = 0) | 0.41 |
| Sortino | 1.00 |
| Max drawdown | -0.99% |
| Longest drawdown (trading days) | 678 |
| Calmar | 0.37 |
| Worst year | -0.35% |
| Worst month | -0.37% |
| Closed trades | 51 |
| Win rate | 33.33% |
| Average winner | 2.90% |
| Average loser | -0.68% |
| Expectancy per trade | 0.51% |
| Profit factor | 2.11 |
| Average holding (calendar days) | 24.5 |
| Average exposure | 4.28% |
| Turnover (1-way, per year) | 0.63 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -12.98% | 0.00 | 0.06 |
| E901-07 | -13.57% | 0.00 | 0.06 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 0.01% |
| 2011 | 0.17% |
| 2012 | 0.65% |
| 2013 | 0.04% |
| 2014 | -0.08% |
| 2015 | -0.32% |
| 2016 | 2.80% |
| 2017 | -0.35% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 99743.26 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.684042; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 23 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.52789495319531e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 103 orders vs QuantConnect Total Orders 103 |
| fills_match_harness_count | pass | downloaded fill events 102 vs harness-recorded fills 102 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 102 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `0978ef87c712db9f2c468e72465da847c0713b2279da3b27c6895c3a1e20b4df`
- fills_sha256: `e586eca249cefd6240cc5c787968cf57b40e49ff6783446c9145524c147a5283`
- trades_sha256: `9928139c1da398f31d01e5c932f7224adef814746514d9196341bd7a30661de8`
