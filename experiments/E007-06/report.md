# E007-06 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): cost stress 6x (60 bps/side), reported only (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `3bd5c50c655016ce9f11af4ef0a9a442bafbc48d` · **QC backtest:** `e1e3663a187812a6fd24cd79f3910edd` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T03:03:40Z · **runtime:** 1241s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate', 'slippage_stress_multiple': 6}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 2.78% |
| Annualised volatility | 4.86% |
| Sharpe (rf = 0) | 0.59 |
| Sortino | 0.89 |
| Max drawdown | -8.25% |
| Longest drawdown (trading days) | 814 |
| Calmar | 0.34 |
| Worst year | -1.20% |
| Worst month | -2.52% |
| Closed trades | 223 |
| Win rate | 37.67% |
| Average winner | 7.18% |
| Average loser | -2.88% |
| Expectancy per trade | 0.91% |
| Profit factor | 1.49 |
| Average holding (calendar days) | 27.7 |
| Average exposure | 20.97% |
| Turnover (1-way, per year) | 2.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -10.56% | 0.09 | 0.28 |
| E901-07 | -11.15% | 0.10 | 0.30 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 6.31% |
| 2011 | -0.55% |
| 2012 | 5.93% |
| 2013 | 1.96% |
| 2014 | 5.70% |
| 2015 | -1.20% |
| 2016 | -0.83% |
| 2017 | 5.24% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 99738.09 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.030948; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 30 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.2203863763664486e-16 |
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

- equity_sha256: `3a40e907584f0f7ae1a7b6b6769d2245a61b16232e9a5df5b9f73f214e238152`
- fills_sha256: `fe247768de3f6e439ff200e21b9c105690de1e7d24650d9f2027503bef28b4f3`
- trades_sha256: `cb8ad04c0f3754104611b5c9a8b7ff454cca92a8cc75c705668db082f303b388`
