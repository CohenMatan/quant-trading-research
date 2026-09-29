# E003-10 — S003 v1.0 (research)

C01 H003 S003 v1.0 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E003-01 under D051 with the D054 harness fix (replaces E003-07)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `5dbf36aba730b72e0cef8750305c1bff73299066` · **QC backtest:** `00c2c26726f155633f2ca568faa73ecb` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T08:46:57Z · **runtime:** 398s
- **Parameters:** `{'rebalance': 'monthly', 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.64% |
| Annualised volatility | 7.91% |
| Sharpe (rf = 0) | 0.73 |
| Sortino | 1.01 |
| Max drawdown | -12.53% |
| Longest drawdown (trading days) | 469 |
| Calmar | 0.45 |
| Worst year | -2.76% |
| Worst month | -4.01% |
| Closed trades | 659 |
| Win rate | 53.26% |
| Average winner | 5.87% |
| Average loser | -4.84% |
| Expectancy per trade | 0.87% |
| Profit factor | 1.37 |
| Average holding (calendar days) | 35.0 |
| Average exposure | 48.68% |
| Turnover (1-way, per year) | 5.00 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -7.70% | 0.41 | 0.74 |
| E901-05 | -8.10% | 0.39 | 0.76 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.04% |
| 2011 | -2.76% |
| 2012 | 5.72% |
| 2013 | 10.23% |
| 2014 | 6.45% |
| 2015 | 2.16% |
| 2016 | 3.98% |
| 2017 | 11.95% |

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
| orders_download_complete | pass | downloaded 1329 orders vs QuantConnect Total Orders 1329 |
| fills_match_harness_count | pass | downloaded fill events 1328 vs harness-recorded fills 1328 |
| commission_fixed_per_order | pass | 1328 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `741be0b7abb51d52d1008da61a92952fdeb2dcb455c66dfc4cb6bf71aa4ac788`
- fills_sha256: `56cab3648d59fce70793d8f2b3cfba661ab2c653cb22f9c20ce02fa7ede18652`
- trades_sha256: `3a6ce4079a7c6dc0257e1440422f477f27aeec2081c2206c6e9df0e8892b7da9`
