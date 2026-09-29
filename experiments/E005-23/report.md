# E005-23 — S005 v1.2 (research)

C01 robustness of E005-12: plateau slots 12 (base 15) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `6da67d902666e4bd2d3fa39d4e02caeb97aa882b` · **QC backtest:** `5536456501d384a8a8831b47b809ddb9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T11:07:53Z · **runtime:** 420s
- **Parameters:** `{'vol_days': 63, 'slots': 12, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.57% |
| Annualised volatility | 5.46% |
| Sharpe (rf = 0) | 1.36 |
| Sortino | 2.06 |
| Max drawdown | -5.10% |
| Longest drawdown (trading days) | 144 |
| Calmar | 1.49 |
| Worst year | 3.78% |
| Worst month | -3.90% |
| Closed trades | 424 |
| Win rate | 62.03% |
| Average winner | 4.43% |
| Average loser | -3.33% |
| Expectancy per trade | 1.48% |
| Profit factor | 2.24 |
| Average holding (calendar days) | 67.0 |
| Average exposure | 65.42% |
| Turnover (1-way, per year) | 3.43 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.77% | 0.29 | 0.75 |
| E901-05 | -6.17% | 0.26 | 0.72 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 7.39% |
| 2011 | 8.97% |
| 2012 | 3.78% |
| 2013 | 15.04% |
| 2014 | 5.23% |
| 2015 | 11.73% |
| 2016 | 3.91% |
| 2017 | 4.92% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98044.58 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.084211; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 72 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1046 orders vs QuantConnect Total Orders 1046 |
| fills_match_harness_count | pass | downloaded fill events 1046 vs harness-recorded fills 1046 |
| commission_fixed_per_order | pass | 1046 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `52c0a4f6d72296bd3842ff344ef415dc4e73435e989a4e56d091abf38b7a412c`
- fills_sha256: `b44bb003200d390427c69c0b8dcdd53137e90f735220fe582da6d105692946b9`
- trades_sha256: `936cfb8368c01e315327a76506ecd96547ae801ca4dc7ac0ee7db5553a79adf0`
