# E007-14 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): plateau: time stop 40 -> 60 (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `9ec1a095552089e17846a205b5f29e4b42f5fa5d` · **QC backtest:** `d6a40d322e14d43cf60790309198234b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T07:53:12Z · **runtime:** 1012s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 60, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.53% |
| Annualised volatility | 4.87% |
| Sharpe (rf = 0) | 1.13 |
| Sortino | 1.78 |
| Max drawdown | -5.15% |
| Longest drawdown (trading days) | 430 |
| Calmar | 1.07 |
| Worst year | -0.29% |
| Worst month | -1.69% |
| Closed trades | 223 |
| Win rate | 46.19% |
| Average winner | 6.89% |
| Average loser | -2.36% |
| Expectancy per trade | 1.91% |
| Profit factor | 2.47 |
| Average holding (calendar days) | 28.5 |
| Average exposure | 21.60% |
| Turnover (1-way, per year) | 2.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -7.81% | 0.10 | 0.28 |
| E901-07 | -8.40% | 0.10 | 0.31 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 9.22% |
| 2011 | -0.29% |
| 2012 | 10.17% |
| 2013 | 6.09% |
| 2014 | 8.18% |
| 2015 | 0.80% |
| 2016 | 3.55% |
| 2017 | 6.91% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 99884.84 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.031383; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 32 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.116719661283175e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 446 orders vs QuantConnect Total Orders 446 |
| fills_match_harness_count | pass | downloaded fill events 446 vs harness-recorded fills 446 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 446 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `d48e653623da00b861cc9d425dafdcf8dd82b3462b5e41452336313d3d2973d7`
- fills_sha256: `c7326b5f0b8fa91685637b0025683c61f4451a655088f092c70c8113a49a6bce`
- trades_sha256: `f1f08e7873882b97e72fa4d1d7367ffaf512730cd8fd3681b7fcdc876fc29ff4`
