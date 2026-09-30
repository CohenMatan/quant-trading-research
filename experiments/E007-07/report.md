# E007-07 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): plateau: ATR10/ATR100 ratio 0.6 -> 0.3 (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `e1524cc64e244b21a5bee2ab851a600ca36688bc` · **QC backtest:** `01b6a7bac1f0541a55095a1b8226ee7c` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T03:24:33Z · **runtime:** 4264s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.3, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -0.01% |
| Annualised volatility | 0.14% |
| Sharpe (rf = 0) | -0.10 |
| Sortino | -0.14 |
| Max drawdown | -0.34% |
| Longest drawdown (trading days) | 1342 |
| Calmar | -0.04 |
| Worst year | -0.16% |
| Worst month | -0.13% |
| Closed trades | 30 |
| Win rate | 26.67% |
| Average winner | 0.52% |
| Average loser | -0.30% |
| Expectancy per trade | -0.08% |
| Profit factor | 0.62 |
| Average holding (calendar days) | 22.5 |
| Average exposure | 2.30% |
| Turnover (1-way, per year) | 0.37 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -13.35% | 0.00 | 0.10 |
| E901-07 | -13.94% | 0.00 | 0.10 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -0.00% |
| 2011 | -0.11% |
| 2012 | 0.02% |
| 2013 | 0.07% |
| 2014 | 0.02% |
| 2015 | -0.01% |
| 2016 | -0.16% |
| 2017 | 0.06% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 99773.06 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.706958; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 16 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.52789495319531e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 60 orders vs QuantConnect Total Orders 60 |
| fills_match_harness_count | pass | downloaded fill events 60 vs harness-recorded fills 60 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 60 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `31916ea457280387058ad090ff2f993ff4db4163a5a019251d29ebf1df90627b`
- fills_sha256: `5ca1c4a9f179ae9aa8d405834dbdf0bd01a2958786d3f8f05674cde20fc7eff9`
- trades_sha256: `938dd789c19c75889b77e8f5422cd7f4d89c31cc9ab2e2be99c4703ab2b23905`
