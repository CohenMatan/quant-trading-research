# E007-10 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): plateau: ATR10/ATR100 ratio 0.6 -> 0.9 (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `23ad4dced455893f28e5508d850f72ddf3497484` · **QC backtest:** `2451852aba4e902fcbb84a57f64d3683` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T05:16:04Z · **runtime:** 1235s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.9, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.08% |
| Annualised volatility | 12.00% |
| Sharpe (rf = 0) | 0.86 |
| Sortino | 1.21 |
| Max drawdown | -20.74% |
| Longest drawdown (trading days) | 616 |
| Calmar | 0.49 |
| Worst year | -8.71% |
| Worst month | -6.71% |
| Closed trades | 897 |
| Win rate | 44.15% |
| Average winner | 6.46% |
| Average loser | -3.72% |
| Expectancy per trade | 0.77% |
| Profit factor | 1.30 |
| Average holding (calendar days) | 26.2 |
| Average exposure | 77.40% |
| Turnover (1-way, per year) | 10.78 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.26% | 0.52 | 0.62 |
| E901-07 | -3.85% | 0.50 | 0.65 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 26.64% |
| 2011 | -4.23% |
| 2012 | 22.76% |
| 2013 | 21.20% |
| 2014 | 10.35% |
| 2015 | -8.71% |
| 2016 | 0.46% |
| 2017 | 17.89% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98091.40 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.028004; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 27 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1805 orders vs QuantConnect Total Orders 1805 |
| fills_match_harness_count | pass | downloaded fill events 1803 vs harness-recorded fills 1803 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1803 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `b4ae5976faf55159a263a85de3f6810839a11b805b84cf29162a4542fbd9936a`
- fills_sha256: `610be2660ac4e133d598430a3b3a469c66736d84206265ab47e3ad338036bfa5`
- trades_sha256: `7992849abd25b577baa1df52de099337d30e3f0cc95fb9aad6e681d739b13c94`
