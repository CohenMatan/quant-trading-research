# E013-10 — S013 v1.0 (sizing)

C03 S1 ($200K, 15 positions) of E013-01. Diagnostic, not a trial. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `1a0119b134f7df079615e93dcb8c070ee5673d6f` · **QC backtest:** `d292750e91a6d182000a5239dac576e4` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T17:57:51Z · **runtime:** 393s
- **Parameters:** `{'q': 0.2, 'stat': 'max', 'seed': 1, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.12% |
| Annualised volatility | 14.10% |
| Sharpe (rf = 0) | 0.75 |
| Sortino | 1.07 |
| Max drawdown | -23.15% |
| Longest drawdown (trading days) | 436 |
| Calmar | 0.44 |
| Worst year | -4.28% |
| Worst month | -9.11% |
| Closed trades | 482 |
| Win rate | 58.30% |
| Average winner | 10.53% |
| Average loser | -8.73% |
| Expectancy per trade | 2.50% |
| Profit factor | 1.59 |
| Average holding (calendar days) | 87.9 |
| Average exposure | 84.15% |
| Turnover (1-way, per year) | 3.57 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.22% | 0.89 | 0.90 |
| E901-07 | -3.81% | 0.85 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 21.02% |
| 2011 | -4.16% |
| 2012 | 11.49% |
| 2013 | 28.42% |
| 2014 | 9.40% |
| 2015 | -4.28% |
| 2016 | 10.31% |
| 2017 | 12.55% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 194435.32 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.088692; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 980 orders vs QuantConnect Total Orders 980 |
| fills_match_harness_count | pass | downloaded fill events 978 vs harness-recorded fills 978 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 978 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c9b4d348dd9ee9e0ed58f77c765d4bb48515265262ad8f561260339d36d70845`
- fills_sha256: `124aa431c29b7bbed19fc8f223152bbb230cdd23db562c2ce61593e759a8aec1`
- trades_sha256: `f2806dfdb652003aed0b38bef86443e333d8e4020d03209729cab36648c684a2`
