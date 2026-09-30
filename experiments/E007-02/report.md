# E007-02 — S007 v1.1 (research)

C02 H007 S007 v1.1 (pre-declared selection candidate, D069) on IS 2010-2017: contraction as ATR10/ATR100 <= 0.6

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `e90f2f8373734e0c05661e8f367aeb851746f592` · **QC backtest:** `7da236e2350271f0277d576144d7f964` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T22:07:43Z · **runtime:** 1100s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.43% |
| Annualised volatility | 4.84% |
| Sharpe (rf = 0) | 1.12 |
| Sortino | 1.75 |
| Max drawdown | -5.14% |
| Longest drawdown (trading days) | 430 |
| Calmar | 1.06 |
| Worst year | 0.80% |
| Worst month | -1.69% |
| Closed trades | 223 |
| Win rate | 46.19% |
| Average winner | 6.76% |
| Average loser | -2.32% |
| Expectancy per trade | 1.87% |
| Profit factor | 2.46 |
| Average holding (calendar days) | 27.6 |
| Average exposure | 20.95% |
| Turnover (1-way, per year) | 2.72 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -7.91% | 0.09 | 0.28 |
| E901-07 | -8.50% | 0.09 | 0.30 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.95% |
| 2011 | 0.82% |
| 2012 | 10.16% |
| 2013 | 3.91% |
| 2014 | 8.35% |
| 2015 | 0.80% |
| 2016 | 2.84% |
| 2017 | 7.98% |

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
| no_leverage | pass | min cash/equity 0.031402; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 30 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.116719661283175e-16 |
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

- equity_sha256: `d36f7380162c9b5e9fa60dce1b37296819b04fa45b28bc36cf05387037829597`
- fills_sha256: `74bfefb8f4f1943df1d70dcf2a9119880c62a801289852ea0f301adb727ebbad`
- trades_sha256: `bbe45997ef7df0e61ea4b33d18b3b27aa08564ddca0acd08337d20eae5a3c8eb`
