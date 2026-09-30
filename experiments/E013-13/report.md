# E013-13 — S013 v1.0 (sizing)

C03 S2 ($200K, 20 positions) of E013-01. Diagnostic, not a trial. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `ff1e91cbdd8b777be1c46132d397a575d3cb1735` · **QC backtest:** `a6dd5ea19efb69a0173f2fea0de5074c` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T18:18:51Z · **runtime:** 443s
- **Parameters:** `{'q': 0.2, 'stat': 'max', 'seed': 1, 'slots': 20, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.51% |
| Annualised volatility | 13.77% |
| Sharpe (rf = 0) | 0.86 |
| Sortino | 1.22 |
| Max drawdown | -23.12% |
| Longest drawdown (trading days) | 433 |
| Calmar | 0.50 |
| Worst year | -3.20% |
| Worst month | -8.38% |
| Closed trades | 642 |
| Win rate | 59.50% |
| Average winner | 10.71% |
| Average loser | -8.66% |
| Expectancy per trade | 2.86% |
| Profit factor | 1.75 |
| Average holding (calendar days) | 88.0 |
| Average exposure | 83.77% |
| Turnover (1-way, per year) | 3.55 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.83% | 0.88 | 0.92 |
| E901-07 | -2.41% | 0.84 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 16.33% |
| 2011 | -1.48% |
| 2012 | 9.81% |
| 2013 | 31.89% |
| 2014 | 14.41% |
| 2015 | -3.20% |
| 2016 | 13.83% |
| 2017 | 14.08% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 194440.43 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.101680; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1305 orders vs QuantConnect Total Orders 1305 |
| fills_match_harness_count | pass | downloaded fill events 1303 vs harness-recorded fills 1303 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1303 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `106f974e9e4781decd0d6020b16d9c9895df4acf9c40edbf65a6f43ccf79882e`
- fills_sha256: `cc0259b97e88784dfa4b3bb25e56572810237d2285f2efc76cf064f4f255d2b4`
- trades_sha256: `377103dd4641d6aedc13022da4fc44a644fbb37280179ea764594aff8ae00736`
