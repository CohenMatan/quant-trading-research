# E005-12 — S005 v1.2 (research)

C01 H005 S005 v1.2 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E005-03 under D051 with the D054 harness fix (replaces E005-09)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `6b0ce8f42dd5437240e776709ee42bbcaca17681` · **QC backtest:** `a543007e00e06649e8eb86495ab5955b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T09:49:42Z · **runtime:** 347s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.52% |
| Annualised volatility | 5.80% |
| Sharpe (rf = 0) | 1.44 |
| Sortino | 2.17 |
| Max drawdown | -5.28% |
| Longest drawdown (trading days) | 165 |
| Calmar | 1.61 |
| Worst year | 2.19% |
| Worst month | -3.52% |
| Closed trades | 408 |
| Win rate | 62.99% |
| Average winner | 5.22% |
| Average loser | -3.52% |
| Expectancy per trade | 1.99% |
| Profit factor | 2.33 |
| Average holding (calendar days) | 74.9 |
| Average exposure | 67.67% |
| Turnover (1-way, per year) | 3.22 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -4.82% | 0.31 | 0.77 |
| E901-05 | -5.22% | 0.28 | 0.74 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 11.65% |
| 2011 | 12.38% |
| 2012 | 5.15% |
| 2013 | 16.47% |
| 2014 | 5.34% |
| 2015 | 10.08% |
| 2016 | 2.19% |
| 2017 | 5.48% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98059.30 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.075545; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 71 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3862034721872065e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 828 orders vs QuantConnect Total Orders 828 |
| fills_match_harness_count | pass | downloaded fill events 828 vs harness-recorded fills 828 |
| commission_fixed_per_order | pass | 828 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3ac0ff70622ae0008240051936f452b11338a6fc1470062a373e1761408063c4`
- fills_sha256: `1e748a483c4cf278c48ee92a5377c1c5e44fd86e56719885d977ab83ab6dc480`
- trades_sha256: `e0213b96b289ab5e1abab9acb52b97bab9c67e3dd71610853387e3050c0286d3`
