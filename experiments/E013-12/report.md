# E013-12 — S013 v1.0 (sizing)

C03 S1 ($200K, 15 positions) of E013-03. Diagnostic, not a trial. Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082).

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `d025f8a80e1ba2bdcb18ecffa7542980d76d2877` · **QC backtest:** `7a3846748ba5ae69133a5b8069f03067` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T18:12:27Z · **runtime:** 373s
- **Parameters:** `{'q': 0.2, 'stat': 'max', 'seed': 3, 'slots': 15, 'hold': 60}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.92% |
| Annualised volatility | 14.37% |
| Sharpe (rf = 0) | 0.86 |
| Sortino | 1.21 |
| Max drawdown | -22.36% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.53 |
| Worst year | -0.06% |
| Worst month | -9.10% |
| Closed trades | 481 |
| Win rate | 62.99% |
| Average winner | 10.42% |
| Average loser | -9.63% |
| Expectancy per trade | 3.00% |
| Profit factor | 1.81 |
| Average holding (calendar days) | 88.1 |
| Average exposure | 84.21% |
| Turnover (1-way, per year) | 3.58 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.42% | 0.91 | 0.90 |
| E901-07 | -2.01% | 0.87 | 0.93 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.96% |
| 2011 | 2.04% |
| 2012 | 9.49% |
| 2013 | 38.77% |
| 2014 | 14.54% |
| 2015 | -0.06% |
| 2016 | 9.03% |
| 2017 | 16.56% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 183276.91 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.048654; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
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

- equity_sha256: `f53af7a1bd0858ef0cc1727468143ad07430726836e78b2fadb31a526ddad1c0`
- fills_sha256: `179d8a4f32d3cd2edfa1dafa3d016a91b7d4dbc9613f4adcacd686efdb51e188`
- trades_sha256: `c0d35c8fe3359101a2301234a0b15d45b9a766b95b5a37b898eba21016375576`
