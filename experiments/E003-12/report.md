# E003-12 — S003 v1.2 (research)

C01 H003 S003 v1.2 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E003-03 under D051 with the D054 harness fix (replaces E003-09)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `b1a2f5f947cd7fbe9af6bd87ed56aeddab5be493` · **QC backtest:** `278cf388e0e71785d141c4af9dcdeca8` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T09:00:35Z · **runtime:** 466s
- **Parameters:** `{'rebalance': 'monthly', 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.73% |
| Annualised volatility | 8.02% |
| Sharpe (rf = 0) | 0.73 |
| Sortino | 1.02 |
| Max drawdown | -12.54% |
| Longest drawdown (trading days) | 425 |
| Calmar | 0.46 |
| Worst year | -2.90% |
| Worst month | -3.93% |
| Closed trades | 658 |
| Win rate | 53.50% |
| Average winner | 5.93% |
| Average loser | -4.81% |
| Expectancy per trade | 0.94% |
| Profit factor | 1.42 |
| Average holding (calendar days) | 35.1 |
| Average exposure | 48.69% |
| Turnover (1-way, per year) | 4.98 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -7.61% | 0.41 | 0.73 |
| E901-05 | -8.01% | 0.39 | 0.75 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.22% |
| 2011 | -2.90% |
| 2012 | 3.72% |
| 2013 | 7.64% |
| 2014 | 9.09% |
| 2015 | 4.43% |
| 2016 | 4.02% |
| 2017 | 12.23% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96290.67 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.148945; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 14 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.092280125712233e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1327 orders vs QuantConnect Total Orders 1327 |
| fills_match_harness_count | pass | downloaded fill events 1326 vs harness-recorded fills 1326 |
| commission_fixed_per_order | pass | 1326 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `939b4d21f9dbab58f00039e5a0766d8d2dfb4e185d0bb1dddbaf4cf2f898ff17`
- fills_sha256: `f660105be9392a2d84c6c16a7737dbfa4cdc1ae37f26bfb82f4e4b81b0580f6c`
- trades_sha256: `9d9649194c4581d0fee4f5bb9ea0dcca8ead09a819ffffd0dfe7ef50fdc79ea9`
