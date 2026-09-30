# E007-04 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): 2x slippage (20 bps/side): IS screen item Sharpe >= 0.4 at 2x (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `d5c38ec15a66d5bc36a9a35d5e878b4438addce0` · **QC backtest:** `6462dfc0d2a65462977d428022acad6d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T01:59:19Z · **runtime:** 1296s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate', 'slippage_stress_multiple': 2}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 4.90% |
| Annualised volatility | 4.84% |
| Sharpe (rf = 0) | 1.01 |
| Sortino | 1.58 |
| Max drawdown | -5.30% |
| Longest drawdown (trading days) | 478 |
| Calmar | 0.93 |
| Worst year | 0.39% |
| Worst month | -1.80% |
| Closed trades | 223 |
| Win rate | 43.05% |
| Average winner | 7.04% |
| Average loser | -2.37% |
| Expectancy per trade | 1.68% |
| Profit factor | 2.21 |
| Average holding (calendar days) | 27.6 |
| Average exposure | 20.97% |
| Turnover (1-way, per year) | 2.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -8.44% | 0.09 | 0.28 |
| E901-07 | -9.03% | 0.09 | 0.30 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.42% |
| 2011 | 0.55% |
| 2012 | 9.30% |
| 2013 | 3.54% |
| 2014 | 7.86% |
| 2015 | 0.39% |
| 2016 | 2.10% |
| 2017 | 7.43% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 99855.49 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.031121; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 30 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.2039611088936356e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 447 orders vs QuantConnect Total Orders 447 |
| fills_match_harness_count | pass | downloaded fill events 446 vs harness-recorded fills 446 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 446 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `4b4a047a8006be1685e4f303b401afc0993938fcfd25ad1242d1e97b903e3897`
- fills_sha256: `6052a8a412a8112721e936f67e7da468e8ad55af435c3c9ed943268f44e898f9`
- trades_sha256: `9588ad33d7389a9b603e294827327d1adf712fc4d83f33792151ca0ce7c004c0`
