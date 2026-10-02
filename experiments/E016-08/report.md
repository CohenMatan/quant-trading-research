# E016-08 — S016 v1.0 (sizing)

P2 $200K sensitivity of E016-01. Never decides, never rescues. Pre-declared in research/phase2/H016_spec.md (frozen, D116).

- **Status:** completed
- **Split:** DEV (2010-03-01 → 2021-12-31)
- **Commit:** `8e38b655d8eabcfdaa416d1c5a987018e30ebc10` · **QC backtest:** `70f65861b3d7c7d4a233d6d11524e19c` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-02T18:59:43Z · **runtime:** 789s
- **Parameters:** `{'slots': 20, 'months': [3, 6, 9, 12], 'book': 'gpa'}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20, 'sec_corrections': True}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 4000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-03-01 → 2021-12-31 (2983 trading days) |
| CAGR | 13.28% |
| Annualised volatility | 20.44% |
| Sharpe (rf = 0) | 0.71 |
| Sortino | 1.00 |
| Max drawdown | -40.44% |
| Longest drawdown (trading days) | 543 |
| Calmar | 0.33 |
| Worst year | -2.34% |
| Worst month | -14.38% |
| Closed trades | 201 |
| Win rate | 53.73% |
| Average winner | 45.40% |
| Average loser | -19.97% |
| Expectancy per trade | 15.15% |
| Profit factor | 2.44 |
| Average holding (calendar days) | 346.5 |
| Average exposure | 95.71% |
| Turnover (1-way, per year) | 0.75 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.60% | 1.02 | 0.83 |
| E901-07 | -0.10% | 1.00 | 0.87 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 20.77% |
| 2011 | 16.39% |
| 2012 | 2.72% |
| 2013 | 45.18% |
| 2014 | 2.50% |
| 2015 | 2.10% |
| 2016 | -2.34% |
| 2017 | 20.78% |
| 2018 | 5.01% |
| 2019 | 18.50% |
| 2020 | 35.91% |
| 2021 | 0.00% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2983 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-03-01..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 188270.82 |
| equity_complete | pass | chart rows 2983 vs algorithm days 2983 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2983 vs QuantConnect tradeableDates 2983 |
| warmup_left_account_untouched | pass | first recorded equity 200000.00 vs initial cash 200000.00; 418 warm-up sessions |
| no_leverage | pass | min cash/equity 0.019430; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 9 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.9241314226868925e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 622 orders vs QuantConnect Total Orders 622 |
| fills_match_harness_count | pass | downloaded fill events 622 vs harness-recorded fills 622 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 622 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `1fa5c76952e6296e6bb23e894c2b6bc876b8b28844bff9041571adea6118e2cb`
- fills_sha256: `d3d52fac7e47b1dd864c1738b2afba586c02895fb8d097f7f9d529e1b8021821`
- trades_sha256: `d925604e1ea6c843d1187be7d2df5b177bbf3c368704161b810224a3aaad8210`
